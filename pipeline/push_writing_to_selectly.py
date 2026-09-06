#!/usr/bin/env python3
"""Push approved writing prompts to Selectly.

`push_to_selectly` reads the `questions` table. Writing prompts live in their own table,
`writing_prompts`, with a different shape -- a stimulus the student reads and a task
telling them what to write about it, plus two word counts and a per-prompt time. So they
get their own sender, sharing this repo's tracking, payload hashing, batching and POST
so a corrected prompt re-sends and an untouched one does not.

THE PAYLOAD CONTRACT is Selectly's, verified by them end-to-end against a real row from
this table rather than described:

    qbankId, questionType='writing', category='writing', difficulty, schoolIds,
    stem            <- task_instruction        (required)
    stimulus        <- stimulus_content        (optional)
    stimulusType    <- stimulus_type           (optional)
    promptType      <- prompt_type             (drives the marking dimensions)
    wordLimit       <- word_count_max          (required)
    wordCountMin    <- word_count_min          (optional)
    timeLimitMinutes<- time_limit_minutes      (optional, guidance only)
    formId, formPosition, formKind

NO RUBRIC. Selectly's import used to require a five-key rubric object that qbank does not
have and that nothing in Selectly read -- `buildGradingPrompt` hardcodes its own
dimensions, so the column was written on import and consumed by nobody. It was dropped
rather than have qbank invent five keys per prompt. The marking dimensions now come from
`promptType`, which is why sending the right prompt_type matters: a narrative marked on
"Argument" is what the old fixed rubric was doing to half of every VIC paper.

REQUIRES the Selectly migration that adds `stimulus`, `stimulus_type`, `word_count_min`
and `time_limit_minutes` to `questions`. Until it is deployed those four are dropped
silently, exactly as the form fields were in August -- so `--verify` reads them back and
says whether they landed.

    env -u PYTHONPATH .venv/bin/python3.11 -m pipeline.push_writing_to_selectly --dry-run
    env -u PYTHONPATH .venv/bin/python3.11 -m pipeline.push_writing_to_selectly
    env -u PYTHONPATH .venv/bin/python3.11 -m pipeline.push_writing_to_selectly --verify
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sqlite3
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from pipeline.push_to_selectly import (            # noqa: E402
    DB_PATH, TRACKING_FILE, check_target, load_env, load_tracking, payload_hash,
    post_batch, save_tracking,
)

logger = logging.getLogger("push_writing")

# Which exam a prompt belongs to. jmss has no exam configured in Selectly's schools.ts,
# so those prompts are held back rather than sent somewhere they cannot be served --
# the same rule science_reasoning follows in the MCQ pusher.
SCHOOL_TYPE_TO_EXAMS: dict[str, list[str]] = {
    "victorian_selective": ["vic-seal"],
    "nsw_selective": ["nsw-shspt"],
    "general": ["vic-seal", "nsw-shspt"],
    "jmss": [],
}

# The four the migration adds. Read back by --verify, because a column Selectly does not
# have yet is dropped silently on import and everything still reports success.
MIGRATION_FIELDS = ("stimulus", "stimulusType", "wordCountMin", "timeLimitMinutes")


def prompt_to_question(row: dict) -> dict:
    q: dict = {
        "qbankId": row["id"],
        "questionType": "writing",
        "category": "writing",
        "difficulty": row["difficulty"],
        "schoolIds": SCHOOL_TYPE_TO_EXAMS.get(row["school_type"], []),
        "stem": row["task_instruction"],
        "wordLimit": row["word_count_max"],
    }
    for key, col in (("stimulus", "stimulus_content"),
                     ("stimulusType", "stimulus_type"),
                     ("promptType", "prompt_type"),
                     ("wordCountMin", "word_count_min"),
                     ("timeLimitMinutes", "time_limit_minutes")):
        if row.get(col) not in (None, ""):
            q[key] = row[col]
    if row.get("form_id"):
        q["formId"] = row["form_id"]
        q["formPosition"] = row["form_position"]
        q["formKind"] = row["form_kind"]
    return q


def fetch_approved_prompts(forms: list[str] | None) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        where, params = ["review_status='approved'"], []
        if forms:
            where.append(f"form_id IN ({','.join('?' * len(forms))})")
            params.extend(forms)
        rows = conn.execute(
            f"SELECT * FROM writing_prompts WHERE {' AND '.join(where)} "
            f"ORDER BY form_id, form_position", params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def pending_count() -> int:
    conn = sqlite3.connect(DB_PATH)
    try:
        return conn.execute("SELECT COUNT(*) FROM writing_prompts "
                            "WHERE review_status='pending'").fetchone()[0]
    finally:
        conn.close()


def verify(url: str, secret: str) -> int:
    """Read the writing prompts back out of Selectly and check what actually landed."""
    req = urllib.request.Request(f"{url.rstrip('/')}/api/admin/questions-dump"
                                 f"?category=writing",
                                 headers={"x-import-secret": secret})
    rows = json.loads(urllib.request.urlopen(req, timeout=180).read())["questions"]
    live = {r["qbankId"]: r for r in rows if r.get("qbankId")}
    mine = {r["id"]: r for r in fetch_approved_prompts(None)}
    logger.info(f"approved in qbank {len(mine)}   live in Selectly {len(live)}")
    missing = [q for q in mine if q not in live]
    logger.info(f"not live: {len(missing)}")
    if not live:
        return 1 if mine else 0
    sample = next(iter(live.values()))
    absent = [f for f in MIGRATION_FIELDS if f not in sample]
    if absent:
        logger.error(
            f"the dump does not return {absent} — either the migration is not deployed "
            f"or the import is dropping them. This is the August form-fields failure "
            f"again: everything reports success and the data is not there.")
        return 1
    for f in MIGRATION_FIELDS:
        n = sum(1 for r in live.values() if r.get(f) not in (None, ""))
        logger.info(f"  {f:<18} present on {n} of {len(live)} live prompts")
    noform = [q for q, r in live.items() if not r.get("formId")]
    logger.info(f"live but carrying no form: {len(noform)}")
    return 0 if not missing and not noform else 1


def migration_is_live(url: str, secret: str) -> bool | None:
    """Does Selectly's dump return the four fields the migration adds?

    True yes, False no, None cannot tell (no rows to look at). A prompt pushed before
    the migration lands loses its stimulus silently -- the import drops unknown keys and
    still reports success -- and a persuasive task with no quote under it is worse live
    than absent. This is the check that stops that happening by accident."""
    for cat in ("writing", "mathematics"):
        try:
            req = urllib.request.Request(
                f"{url.rstrip('/')}/api/admin/questions-dump?category={cat}",
                headers={"x-import-secret": secret})
            rows = json.loads(urllib.request.urlopen(req, timeout=120).read())["questions"]
        except Exception as e:                                   # noqa: BLE001
            logger.warning(f"could not probe the dump: {e}")
            return None
        if rows:
            return all(f in rows[0] for f in MIGRATION_FIELDS)
    return None


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", default="")
    ap.add_argument("--secret", default="")
    ap.add_argument("--forms", default="", help="comma-separated form_ids")
    ap.add_argument("--batch", type=int, default=20)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true",
                    help="push even though the migration looks undeployed")
    ap.add_argument("--verify", action="store_true",
                    help="read the prompts back and check the new fields landed")
    args = ap.parse_args()

    load_env()
    url = args.url or os.environ.get("SELECTLY_URL", "")
    secret = args.secret or os.environ.get("SELECTLY_IMPORT_SECRET", "")
    if not url or not secret:
        logger.error("set SELECTLY_URL and SELECTLY_IMPORT_SECRET")
        sys.exit(1)
    check_target(url)
    logger.info(f"Target: {url}")

    if args.verify:
        sys.exit(verify(url, secret))

    live = migration_is_live(url, secret)
    if live is False and not args.force:
        logger.error(
            "REFUSING TO PUSH. Selectly's dump does not return "
            f"{list(MIGRATION_FIELDS)}, so the migration that adds those columns is not "
            "deployed. Every prompt would land with its task and NO STIMULUS -- a "
            "persuasive question reading 'argue for or against the view in the quote "
            "below' with no quote. The import drops unknown keys silently and still "
            "reports errors=0, which is exactly how the form fields failed in August. "
            "Deploy the migration, or pass --force if you have another way of knowing "
            "it is live.")
        sys.exit(2)
    if live is None:
        logger.warning("could not confirm the migration is deployed — run --verify "
                       "straight after this push and check the stimulus arrived")

    forms = [f.strip() for f in args.forms.split(",") if f.strip()]
    rows = fetch_approved_prompts(forms or None)
    waiting = pending_count()
    if not rows:
        logger.warning(
            f"No APPROVED writing prompts. {waiting} are pending — this sender only "
            f"sends approved rows, so nothing goes until a reviewer approves them or "
            f"tools/approve_forms-style approval is run over the wr forms.")
        return
    if waiting:
        logger.warning(f"{waiting} writing prompts are still pending and will not be sent")

    held = [r for r in rows if not SCHOOL_TYPE_TO_EXAMS.get(r["school_type"])]
    if held:
        logger.warning(f"held back, no exam configured for their school_type: "
                       f"{len(held)} ({held[0]['school_type']})")
    rows = [r for r in rows if SCHOOL_TYPE_TO_EXAMS.get(r["school_type"])]

    payloads = {r["id"]: prompt_to_question(r) for r in rows}
    pushed = load_tracking()
    new = [r for r in rows if r["id"] not in pushed]
    changed = [r for r in rows
               if r["id"] in pushed
               and pushed[r["id"]]["h"] != payload_hash(payloads[r["id"]])]
    to_push = new + changed
    logger.info(f"Approved, sendable: {len(rows)}")
    logger.info(f"Carrying a form assignment: "
                f"{sum(1 for r in rows if r.get('form_id'))} of {len(rows)}")
    logger.info(f"To push: {len(to_push)}  ({len(new)} new, {len(changed)} changed)")
    if not to_push:
        return
    if args.dry_run:
        logger.info("DRY RUN — no API calls made.")
        logger.info("Sample payload:\n"
                    + json.dumps(payloads[to_push[0]["id"]], indent=2)[:900])
        return

    total_in = total_skip = 0
    newly: dict = {}
    for i in range(0, len(to_push), args.batch):
        batch = to_push[i:i + args.batch]
        qs = [payloads[r["id"]] for r in batch]
        logger.info(f"Batch {i // args.batch + 1}/"
                    f"{(len(to_push) + args.batch - 1) // args.batch} ({len(batch)})...")
        ins, skip, errs = post_batch(url, secret, qs)
        total_in += ins
        total_skip += skip
        for e in errs:
            logger.error(f"  {e}")
        if not errs:
            for idx, r in enumerate(batch):
                newly[r["id"]] = {"h": payload_hash(qs[idx])}
    pushed.update(newly)
    save_tracking(pushed, url)
    logger.info(f"inserted={total_in}  skipped={total_skip}")
    logger.info("Now run --verify: the four new fields are dropped silently if the "
                "migration is not deployed.")


if __name__ == "__main__":
    main()
