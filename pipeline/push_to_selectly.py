"""
pipeline/push_to_selectly.py — Push approved questions from SQLite → Selectly import API.

Usage:
    # Dry run — show counts, no API calls
    python -m pipeline.push_to_selectly --dry-run

    # Push to production (reads SELECTLY_URL + SELECTLY_IMPORT_SECRET from .env)
    python -m pipeline.push_to_selectly

    # Push one subject only
    python -m pipeline.push_to_selectly --subject verbal_reasoning

    # Push to local dev server instead
    python -m pipeline.push_to_selectly --url http://localhost:3000 --secret selectly-import-secret-dev

    # Re-push everything (clear tracking first)
    python -m pipeline.push_to_selectly --reset-tracking
    python -m pipeline.push_to_selectly

Tracking:
    Successfully pushed IDs are saved to run_data/db/pushed_to_selectly.json.
    Re-runs skip already-pushed IDs automatically.
"""

import argparse
import base64
import hashlib
import json
import logging
import os
import re
import sqlite3
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent
DB_PATH = REPO_ROOT / "run_data" / "db" / "qbank.db"
TRACKING_FILE = REPO_ROOT / "run_data" / "db" / "pushed_to_selectly.json"
# Marks a row carried over from the id-only tracking format, whose sent content is
# unknown. Never equal to a real hash, so such rows are re-sent once.
_seen_target: dict = {}
LEGACY_HASH = "unknown-legacy"
# Above this many withdrawals in one run, stop and make the operator confirm. Bulk
# deactivation is the shape of a mistake, not of a review round.
DEACTIVATE_LIMIT = 200

SCHOOL_IDS = ["vic-seal", "nsw-shspt"]

# Which exam(s) a question belongs to. Previously every question was sent to BOTH, which
# is wrong in both directions: vic-seal has no `mathematics` section at all, and NSW
# students were being served VIC verbal_reasoning.
#
# Derived from Selectly's own schools.ts. vic-seal sections: verbal_reasoning,
# quantitative_reasoning, reading_comprehension, writing. nsw-shspt sections:
# reading_comprehension, mathematics, logical_reasoning, writing.
CATEGORY_SCHOOLS: dict[str, list[str]] = {
    "verbal_reasoning": ["vic-seal"],
    "quantitative_reasoning": ["vic-seal"],
    # mathematics is NOT one exam's category -- it routes on the source book, the same
    # way reading does. year9_maths and ma_vic_stats are the VIC "Mathematics and
    # Quantitative Reasoning" component and were being sent to NSW, which is a Year 6-7
    # paper: 642 Year 9 questions aimed at the wrong students, and vic-seal never saw
    # its own maths. See MATHS_BOOK_SCHOOLS and school_ids_for().
    "logical_reasoning": ["nsw-shspt"],
    "writing": ["vic-seal", "nsw-shspt"],
    # reading_comprehension is the only category both exams draw on, so it routes on the
    # source book instead -- see school_ids_for().
    "science_reasoning": [],
}

# Reading books are state-specific except the ACT-sourced ones, whose passages were
# verified usable for both exams (see CLAUDE.md, the 2026-08-10 reuse finding).
READING_BOOK_SCHOOLS: list[tuple[str, list[str]]] = [
    ("rc_nsw_", ["nsw-shspt"]),
    ("rc_vic_", ["vic-seal"]),
    ("act_test", ["vic-seal", "nsw-shspt"]),
]

# Maths books are state-specific and the two-year pitch gap is deliberate (delivery spec
# §4.1), so no maths book serves both exams.
MATHS_BOOK_SCHOOLS: list[tuple[str, list[str]]] = [
    ("year7_nsw_maths", ["nsw-shspt"]),
    ("ma_nsw_selective", ["nsw-shspt"]),
    # Questions authored to replace ones withdrawn at review. Registering the book is
    # not optional: an unregistered maths book routes NOWHERE by design, so a
    # replacement would load, be dealt into its form, and then silently never ship --
    # leaving the form a question short with nothing to show for it.
    ("ma_nsw_replacements", ["nsw-shspt"]),
    ("year9_maths", ["vic-seal"]),
    ("ma_vic_stats", ["vic-seal"]),
]

# Verbal questions of types TASK §6 says never to generate. Withdrawing these from the
# 5,321 already pushed is impossible without qbank_id; on a clean reload it costs nothing
# but not sending them. Regenerate with tools/vr_banned_types.py --manifest.
BANNED_MANIFEST = REPO_ROOT / "run_data" / "output" / "vr_banned_types.json"

# Quantitative questions pitched beyond Year 8. quantitative_reasoning routes to vic-seal
# only, so there is no other exam to demote them to -- out of the VIC pool is out of the
# bank. They are correct questions aimed two years high, not rejects, so they stay
# 'approved' in qbank against a later senior or JMSS product. Regenerate with
# tools/qr_beyond_year8.py --manifest.
BEYOND_Y8_MANIFEST = REPO_ROOT / "run_data" / "output" / "qr_beyond_year8.json"

# Questions whose CONTENT belongs to another subject than their label -- US civics filed
# under quantitative_reasoning. Correct questions with no component to sit in.
OFF_SUBJECT_MANIFEST = REPO_ROOT / "run_data" / "output" / "qr_off_subject.json"


def banned_ids() -> set[str]:
    """Ids excluded from every push. Absent manifest means nothing is excluded, which is
    reported loudly rather than assumed safe."""
    if not BANNED_MANIFEST.exists():
        return set()
    data = json.loads(BANNED_MANIFEST.read_text())
    return {b["id"] for b in data.get("banned", [])}


def beyond_year8_ids() -> set[str]:
    """Quantitative ids ruled beyond Year 8 by hand, plus those whose content belongs to
    another subject entirely. Same absent-manifest contract as banned_ids()."""
    out: set[str] = set()
    for path in (BEYOND_Y8_MANIFEST, OFF_SUBJECT_MANIFEST):
        if path.exists():
            out |= {b["id"] for b in json.loads(path.read_text()).get("excluded", [])}
    return out


BOOK_ROUTED = {
    "reading_comprehension": (READING_BOOK_SCHOOLS, ["vic-seal", "nsw-shspt"]),
    "mathematics": (MATHS_BOOK_SCHOOLS, []),
}


def school_ids_for(row: dict) -> list[str]:
    """Which exams a question belongs to. Two subjects route on their source book rather
    than their category, because both exams test them at different year levels."""
    subject = row["subject"]
    if subject in BOOK_ROUTED:
        table, default = BOOK_ROUTED[subject]
        book = row.get("source_book") or ""
        for prefix, schools in table:
            if book.startswith(prefix):
                return schools
        return default
    return CATEGORY_SCHOOLS.get(subject, [])

VALID_SUBJECTS = [
    "mathematics",
    "quantitative_reasoning",
    "verbal_reasoning",
    "logical_reasoning",
    "science_reasoning",
    "reading_comprehension",
    "writing",
]


def load_env() -> None:
    """Load .env file from repo root if it exists."""
    env_path = REPO_ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def payload_hash(q: dict) -> str:
    """Fingerprint of what was actually sent for a question.

    The old tracking file recorded ids only, which was correct while the import was
    insert-only: a question was either there or not. Now that the import upserts on
    qbankId, "already pushed" is the wrong question to ask -- a question whose key or
    options were repaired must go again, and under id-only tracking it never would.
    Hashing the payload makes the pusher re-send exactly what changed and nothing else.
    """
    return hashlib.sha256(
        json.dumps(q, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()[:16]


def load_tracking() -> dict:
    """Return {qbank_id: {"h": payload_hash, "f": form_id_at_push_time}}.

    The form is recorded because a question REJECTED at review is lifted out of its form
    and its form_id becomes NULL. Scoping the withdrawal pass by current form therefore
    made such a question invisible to it — so the one row that most needs switching off
    is the one row that never would be. It has to be scoped by where the question was
    when it was sent.

    Two older formats load forward: a bare id list, and {id: hash}. Both carry no form,
    so they withdraw only on an unscoped run. Their hashes are unknown or unformed, which
    re-sends once and then settles; re-sending is idempotent under upsert, whereas
    assuming "unchanged" would strand real repairs.
    """
    if not TRACKING_FILE.exists():
        return {}
    data = json.loads(TRACKING_FILE.read_text())
    _seen_target["url"] = data.get("target")
    if "pushed" in data:
        out = {}
        for qid, v in data["pushed"].items():
            out[qid] = v if isinstance(v, dict) else {"h": v, "f": None}
        return out
    return {qid: {"h": LEGACY_HASH, "f": None} for qid in data.get("pushed_ids", [])}


def save_tracking(pushed: dict, target: str | None = None) -> None:
    TRACKING_FILE.parent.mkdir(parents=True, exist_ok=True)
    TRACKING_FILE.write_text(json.dumps(
        {"target": target or _seen_target.get("url"),
         "pushed": dict(sorted(pushed.items()))}, indent=2))


def check_target(url: str) -> None:
    """Refuse to reuse one database's tracking against another.

    Tracking says WHAT was sent but, until now, not WHERE. There are two Selectly
    databases on this machine's horizon -- a local Supabase and the production
    deployment -- and they look alike: the local one also carries qbank_id and form_id.
    Pushing to the wrong one would send the questions there, mark them all as sent, and
    leave production silently missing every repair, with no error anywhere. A whole
    afternoon was spent on exactly this confusion in the other direction.
    """
    was = _seen_target.get("url")
    if was and url and was.rstrip("/") != url.rstrip("/"):
        logger.error(
            f"REFUSING to push. This tracking file describes {was}, but the target is "
            f"{url}. Tracking is per-database: reusing it across two would mark "
            f"questions as sent to a database that never received them. Point "
            f"SELECTLY_URL at the right one, or --reset-tracking to start this database "
            f"from scratch.")
        sys.exit(1)


def build_stem(row: dict) -> str:
    """For passage-based subjects, prepend the passage so it displays with the question."""
    passage = (row.get("passage") or "").strip()
    stem = (row.get("stem") or "").strip()
    if passage:
        return f"PASSAGE:\n{passage}\n\nQUESTION:\n{stem}"
    return stem


def passage_id(row: dict) -> str | None:
    """Stable 16-char ID derived from passage text; None if no passage."""
    passage = (row.get("passage") or "").strip()
    if not passage:
        return None
    return hashlib.sha256(passage.encode()).hexdigest()[:16]


FIGURE_STROKE = "#1a1a2a"


def figure_data_uri(row: dict) -> str | None:
    """
    Convert the row's inline figure_svg into a data: URI for Selectly's imageUrl.

    Selectly renders figures via <img src=...>, which sandboxes the SVG (no script
    execution) but also means the SVG cannot inherit page styles. Two fixes needed:
      - currentColor has no page to inherit from, so bind it to an explicit stroke
      - width/height are usually absent, so derive them from viewBox or the image
        renders at the default 300x150 and clips
    """
    svg = (row.get("figure_svg") or "").strip()
    if not svg:
        return None

    svg = svg.replace("currentColor", FIGURE_STROKE)

    if not re.search(r"<svg[^>]*\swidth=", svg):
        m = re.search(r'viewBox="\s*[\d.+-]+\s+[\d.+-]+\s+([\d.]+)\s+([\d.]+)', svg)
        if m:
            width, height = m.group(1), m.group(2)
            svg = svg.replace("<svg", f'<svg width="{width}" height="{height}"', 1)

    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def row_to_question(row: dict) -> dict:
    q: dict = {
        # Carries our row id across so the question stays addressable after import.
        # Without it Selectly mints its own uuid that we never learn, and the question
        # can never be deactivated, corrected, or withdrawn. Selectly upserts on this,
        # so re-pushing a corrected question updates in place instead of duplicating.
        "qbankId": row["id"],
        "questionType": "mcq",
        "category": row["subject"],
        "difficulty": row["difficulty"],
        "schoolIds": school_ids_for(row),
        "stem": build_stem(row),
        "options": {
            "A": row.get("option_a") or "",
            "B": row.get("option_b") or "",
            "C": row.get("option_c") or "",
            "D": row.get("option_d") or "",
        },
        "correctAnswer": row["correct_answer"],
        "explanation": row.get("explanation") or "",
        "imageUrl": figure_data_uri(row),
    }
    pid = passage_id(row)
    if pid is not None:
        q["passageId"] = pid
    # Fixed-form delivery. Selectly's import accepts and stores all three as of
    # 2026-09-04, and /api/admin/questions-dump returns them, so the deal can be checked
    # rather than assumed -- tools/verify_pushed_forms.py does it. Verified after the
    # 4,500-question VIC push: 5,190 of 5,190 live, every form and position matching.
    if row.get("form_id"):
        q["formId"] = row["form_id"]
        q["formPosition"] = row["form_position"]
        q["formKind"] = row["form_kind"]
    return q


def fetch_withdrawn(conn_path=None) -> list[dict]:
    """Questions that are NOT sendable but may already be live in Selectly.

    A question the reviewer rejects stops being returned by fetch_approved, and under
    push-only semantics that means it simply stays live: the pusher has no way to say
    "this one, stop serving it". These rows are what the deactivation pass acts on.
    """
    conn = sqlite3.connect(conn_path or DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in conn.execute(
            "SELECT id, stem, subject, review_status, form_id FROM questions "
            "WHERE review_status != 'approved'")]
    finally:
        conn.close()


def fetch_approved(subject: str | None, forms: list[str] | None = None) -> list[dict]:
    if not DB_PATH.exists():
        logger.error(f"Database not found: {DB_PATH}")
        sys.exit(1)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        where = ["review_status='approved'"]
        params: list = []
        if subject:
            where.append("subject=?")
            params.append(subject)
        if forms:
            where.append(f"form_id IN ({','.join('?' * len(forms))})")
            params.extend(forms)
        rows = conn.execute(
            f"SELECT * FROM questions WHERE {' AND '.join(where)} "
            f"ORDER BY subject, created_at", params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def post_batch(url: str, secret: str, questions: list[dict]) -> tuple[int, int, list[str]]:
    payload = json.dumps({"questions": questions}).encode("utf-8")
    req = urllib.request.Request(
        f"{url.rstrip('/')}/api/questions/import",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {secret}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return body.get("inserted", 0), body.get("skipped", 0), body.get("errors", [])
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read().decode()}") from e


def deactivate(url: str, secret: str, ids: list[str], dry_run: bool) -> int:
    """Ask Selectly to stop serving questions that are no longer sendable.

    Addresses rows by qbankId, which only works once Selectly commit c52ffa9 is
    deployed. Before that this endpoint cannot find the row and the call is a no-op --
    which is why it reports what it could not deactivate rather than failing quietly.
    """
    if not ids:
        return 0
    if dry_run:
        logger.info(f"[dry-run] would deactivate {len(ids)} question(s)")
        return 0
    # Shape and auth verified against Selectly's route: a `fixes` array of entries each
    # addressed by exactly one of id/qbankId, and an `x-import-secret` header -- NOT the
    # bearer token /api/questions/import uses. The two endpoints differ.
    payload = json.dumps(
        {"fixes": [{"qbankId": qid, "active": False} for qid in ids]}).encode("utf-8")
    req = urllib.request.Request(
        f"{url.rstrip('/')}/api/admin/questions-fix", data=payload,
        headers={"Content-Type": "application/json",
                 "x-import-secret": secret}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        n = body.get("updated", 0)
        if n < len(ids):
            logger.warning(f"deactivated {n} of {len(ids)} — the rest were not found by "
                           f"qbankId. Is Selectly commit c52ffa9 deployed?")
        return n
    except urllib.error.HTTPError as e:
        logger.error(f"deactivation failed: HTTP {e.code}: {e.read().decode()[:200]}")
        return 0


def clear_flags(url: str, secret: str, round_file,
                dry_run: bool) -> None:
    """Clear the reviewer flags this round adjudicated, so the next CSV is only new work.

    Cleared by ADJUDICATED ID, not by region. Two reasons, both learned the hard way:

      * the CSVs are not region-pure. The first one carried four NSW flags and two VIC
        ones together, because both reviewers export from the same admin list. Clearing
        "all VIC flags" after an NSW round would have deleted two flags nobody had
        looked at yet.
      * a flag raised WHILE a round is being worked would be swept away by a blanket
        clear, silently, and the reviewer would never know their report was lost.

    Every flag in the round file is cleared whatever the verdict, including the ones
    judged `keep` — the reviewer asked, the question was read, and the answer was "this
    one is sound". Leaving those flagged would have them re-reported every round.
    """
    if not round_file.exists():
        logger.error(f"no round file at {round_file} — nothing to clear")
        return
    ids = sorted({x["qbank_id"] for x in json.loads(round_file.read_text())
                  if x.get("qbank_id")})
    if not ids:
        logger.info("round file holds no qbank ids; nothing to clear")
        return
    if dry_run:
        logger.info(f"[dry-run] would clear {len(ids)} adjudicated flag(s)")
        return
    payload = json.dumps({"qbankIds": ids}).encode("utf-8")
    req = urllib.request.Request(
        f"{url.rstrip('/')}/api/admin/flags-clear", data=payload,
        headers={"Content-Type": "application/json", "x-import-secret": secret},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        logger.info(f"cleared {body.get('deleted', 0)} flag(s) of {len(ids)} adjudicated")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            logger.warning(
                "flags were NOT cleared: /api/admin/flags-clear does not exist yet. It "
                "is specified in the handover, §9. The push itself succeeded; the "
                "reviewer will see the corrected questions but their old flags will "
                "still be listed.")
        else:
            logger.error(f"clearing flags failed: HTTP {e.code}: {e.read().decode()[:200]}")


def run(args: argparse.Namespace) -> None:
    load_env()

    if args.reset_tracking:
        if TRACKING_FILE.exists():
            TRACKING_FILE.unlink()
            logger.info("Tracking cleared — all approved questions will be pushed on next run.")
        else:
            logger.info("No tracking file found.")
        return

    already_pushed = load_tracking()
    # Before anything else: this must be the database the tracking file describes.
    # Every early return below would otherwise skip the check, and "nothing to push"
    # aimed at the wrong database is precisely the silence this guards against.
    url = args.url or os.environ.get("SELECTLY_URL", "")
    secret = args.secret or os.environ.get("SELECTLY_IMPORT_SECRET", "")
    if url:
        check_target(url)
        logger.info(f"Target: {url}")

    forms = [f.strip() for f in (args.forms or "").split(",") if f.strip()]
    all_rows = fetch_approved(args.subject, forms or None)
    if forms:
        logger.info(f"Restricted to {len(forms)} form(s): {', '.join(forms)}")

    excluded = banned_ids()
    if not excluded:
        logger.warning(
            "No §6 banned-type manifest found — nothing will be excluded. "
            "Run: python -m tools.vr_banned_types --manifest"
        )
    banned_here = [r for r in all_rows if r["id"] in excluded]
    all_rows = [r for r in all_rows if r["id"] not in excluded]

    beyond = beyond_year8_ids()
    if not beyond:
        logger.warning(
            "No beyond-Year-8 manifest found — quantitative items pitched at Year 11-12 "
            "will be sent. Run: python -m tools.qr_beyond_year8 --manifest"
        )
    beyond_here = [r for r in all_rows if r["id"] in beyond]
    all_rows = [r for r in all_rows if r["id"] not in beyond]

    # A question with no exam to belong to would import and then never be served. Better
    # to say so than to ship it silently.
    homeless = [r for r in all_rows if not school_ids_for(r)]
    all_rows = [r for r in all_rows if school_ids_for(r)]

    # Send anything never sent, and anything whose sent content has since changed. The
    # second half is the point: a repaired key or a redrawn figure has to reach Selectly,
    # and under the old id-only tracking it never did.
    payloads = {r["id"]: row_to_question(r) for r in all_rows}
    fresh = [r for r in all_rows if r["id"] not in already_pushed]
    changed = [r for r in all_rows
               if r["id"] in already_pushed
               and already_pushed[r["id"]]["h"] != payload_hash(payloads[r["id"]])]
    to_push = fresh + changed

    # Anything previously sent that is no longer sendable must be switched off, or a
    # question rejected at review keeps being served.
    sendable_ids = {r["id"] for r in all_rows}
    if forms:
        # Scope withdrawal by the form the question was SENT as part of, not the form it
        # sits in now. A question rejected at review is lifted out of its form and its
        # form_id becomes NULL, so scoping on the current value skipped exactly the rows
        # that needed switching off. Without any scoping, a pilot run would instead treat
        # every question outside the pilot as "no longer sendable" and switch off the bank.
        want = set(forms)
        stale = sorted(qid for qid, v in already_pushed.items()
                       if v.get("f") in want and qid not in sendable_ids)
    else:
        stale = sorted(qid for qid in already_pushed if qid not in sendable_ids)

    # Summary
    by_subject: dict[str, int] = {}
    for r in to_push:
        by_subject[r["subject"]] = by_subject.get(r["subject"], 0) + 1

    logger.info(f"Approved, sendable: {len(all_rows)}")
    if banned_here:
        logger.info(f"Excluded (§6 banned types): {len(banned_here)}")
    if beyond_here:
        logger.info(f"Excluded (beyond Year 8, quantitative): {len(beyond_here)}")
    if homeless:
        by_subj: dict[str, int] = {}
        for r in homeless:
            by_subj[r["subject"]] = by_subj.get(r["subject"], 0) + 1
        logger.info(
            f"Excluded (no exam section maps to them): {len(homeless)} — "
            + ", ".join(f"{k} {v}" for k, v in sorted(by_subj.items()))
        )
    with_forms = sum(1 for r in to_push if r.get("form_id"))
    logger.info(f"Carrying a form assignment: {with_forms} of {len(to_push)}")
    logger.info(f"Already pushed : {len(already_pushed)}")
    logger.info(f"To push        : {len(to_push)}  ({len(fresh)} new, "
                f"{len(changed)} changed since last push)")
    if stale:
        logger.info(f"To deactivate  : {len(stale)} — pushed before, no longer sendable")
    for subj, count in sorted(by_subject.items()):
        logger.info(f"  {subj}: {count}")

    # A withdrawal is work even when there is nothing to send. Only stop when neither
    # half has anything to do.
    if not to_push and not stale:
        logger.info("Nothing to push and nothing to withdraw.")
        # Still clear the flags. A round can adjudicate several questions and change
        # none of them -- every verdict `keep` -- and those flags are just as resolved
        # as the repaired ones. Nothing to push means Selectly already holds current
        # content, so clearing is safe here by definition.
        if args.clear_flags:
            clear_flags(url, secret,
                        REPO_ROOT / "run_data/output/review_flags"
                        / f"round_{args.clear_flags}.json", args.dry_run)
        return
    if not to_push:
        logger.info("Nothing new to push — proceeding to the withdrawal pass only.")

    # Deactivating in bulk is almost never what anyone means. It happens when approvals
    # are reset, or when --forms is forgotten: every question outside the intended scope
    # looks "no longer sendable". Make it deliberate.
    if stale and len(stale) > DEACTIVATE_LIMIT and not args.force_deactivate:
        logger.error(
            f"REFUSING to deactivate {len(stale)} questions (limit {DEACTIVATE_LIMIT}). "
            f"This usually means --forms was omitted, or approvals were reset and the "
            f"tracking file still describes an older push. Re-run with --forms to scope "
            f"it, or --force-deactivate if switching off {len(stale)} is genuinely "
            f"intended.")
        sys.exit(1)

    if args.dry_run:
        logger.info("DRY RUN — no API calls made.")
        logger.info("Sample converted question:")
        sample = row_to_question(to_push[0])
        preview = json.dumps(sample, indent=2)
        logger.info(preview[:600] + ("..." if len(preview) > 600 else ""))
        return

    if not url:
        logger.error("No URL — set SELECTLY_URL in .env or pass --url")
        sys.exit(1)
    if not secret:
        logger.error("No secret — set SELECTLY_IMPORT_SECRET in .env or pass --secret")
        sys.exit(1)

    batch_size = args.batch
    batches = [to_push[i : i + batch_size] for i in range(0, len(to_push), batch_size)]
    logger.info(f"Pushing in {len(batches)} batches of up to {batch_size}")

    total_inserted = total_skipped = 0
    total_errors: list[str] = []
    newly_pushed: dict[str, str] = {}

    for i, batch in enumerate(batches, 1):
        questions = [row_to_question(r) for r in batch]
        logger.info(f"Batch {i}/{len(batches)} ({len(questions)} questions)...")
        try:
            inserted, skipped, errors = post_batch(url, secret, questions)
            total_inserted += inserted
            total_skipped += skipped
            total_errors.extend(errors)
            # Only track what the API actually accepted. Errors are reported as
            # "Question {index}: ..." against this batch — marking a rejected row
            # as pushed would silently drop it from every future run.
            rejected_idx = set()
            for e in errors:
                m = re.match(r"Question (\d+):", e)
                if m:
                    rejected_idx.add(int(m.group(1)))
            for idx, r in enumerate(batch):
                if idx not in rejected_idx:
                    newly_pushed[r["id"]] = {"h": payload_hash(questions[idx]),
                                             "f": r.get("form_id")}
            logger.info(f"  inserted={inserted} skipped={skipped} errors={len(errors)}")
            if errors:
                for e in errors[:5]:
                    logger.warning(f"  ! {e}")
        except RuntimeError as e:
            logger.error(f"  Batch {i} failed: {e}")
            logger.error("Stopping. Already-pushed questions are tracked — re-run to continue.")
            break

        if i < len(batches):
            time.sleep(0.3)

    tracked = {**already_pushed, **newly_pushed}

    # Deactivate last: a question withdrawn from service should stop being served even
    # if the push above partly failed, and dropping it from tracking would make the next
    # run forget it ever existed.
    if stale and not args.no_deactivate:
        n = deactivate(url, secret, stale, args.dry_run)
        for qid in stale:
            if n:
                tracked.pop(qid, None)

    save_tracking(tracked, url)

    # Last, and only if the push itself did not fail: a flag must not be cleared while
    # the question it describes is still wrong in Selectly.
    if args.clear_flags and not total_errors:
        clear_flags(url, secret,
                    REPO_ROOT / "run_data/output/review_flags"
                    / f"round_{args.clear_flags}.json", args.dry_run)
    elif args.clear_flags:
        logger.warning("flags not cleared — the push reported errors")

    logger.info("─" * 50)
    logger.info(f"inserted={total_inserted}  skipped={total_skipped}  errors={len(total_errors)}")
    logger.info(f"Cumulative tracked: {len(tracked)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Push approved qbank questions to Selectly")
    parser.add_argument("--url", default="", help="Selectly app URL (overrides .env)")
    parser.add_argument("--secret", default="", help="IMPORT_SECRET (overrides .env)")
    parser.add_argument("--subject", choices=VALID_SUBJECTS, help="Push one subject only")
    # 40, not 100. Figures travel as data URIs, so a hundred questions can be several
    # megabytes and take longer than the caller's patience -- a 273-question push was
    # killed at two minutes mid-run, after the rows had landed but before tracking was
    # written, leaving qbank believing it had sent nothing.
    parser.add_argument("--batch", type=int, default=40, help="Questions per POST (default 40)")
    parser.add_argument("--dry-run", action="store_true", help="Show plan without sending")
    parser.add_argument("--reset-tracking", action="store_true", help="Clear push tracking and exit")
    parser.add_argument("--forms", default="",
                        help="Comma-separated form_ids to push, e.g. the pilot set. "
                             "Restricts BOTH the push and the deactivation pass.")
    parser.add_argument("--force-deactivate", action="store_true",
                        help=f"Allow deactivating more than {DEACTIVATE_LIMIT} questions "
                             f"at once. Almost always a mistake; read the error first.")
    parser.add_argument("--clear-flags", metavar="ROUND", default="",
                        help="after a successful push, clear the reviewer flags this "
                             "round adjudicated, e.g. --clear-flags vic1 for "
                             "run_data/output/review_flags/round_vic1.json")
    parser.add_argument("--no-deactivate", action="store_true",
                        help="Skip switching off questions that are no longer sendable")
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
