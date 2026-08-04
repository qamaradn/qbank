"""
pipeline/backfill_qbank_ids.py — teach Selectly which qbank row each question came from.

Why this exists
---------------
`/api/questions/import` used to be insert-only and let Postgres mint the row id, so qbank
never learned the id of the row it created. Every question pushed before `qbank_id`
existed is therefore live and unaddressable: it cannot be deactivated, corrected, or
withdrawn. This script closes that gap once, by matching on stem text.

It cannot be done by rewriting Selectly's `id` to ours — five tables carry foreign keys
onto `questions.id` (question_mastery, question_responses, drill_responses,
question_flags, writing_feedback), and moving it would orphan real student progress.
Hence a separate `qbank_id` column, populated here.

Matching
--------
Stems are near-unique: 5314 distinct stems across 5321 approved questions. The handful
that collide are disambiguated by their options; anything still ambiguous is reported and
left alone rather than guessed at. A qbank id is never assigned to two rows — `qbank_id`
is unique, so a wrong guess would fail the write anyway, but silence would be worse.

This is a one-time repair. New pushes carry `qbankId` from the start.

Usage:
    # Report what would change — no writes. Do this first.
    python -m pipeline.backfill_qbank_ids --dry-run

    # Apply
    python -m pipeline.backfill_qbank_ids
"""

import argparse
import json
import logging
import os
import sqlite3
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path

from pipeline.push_to_selectly import (
    DB_PATH,
    VALID_SUBJECTS,
    build_stem,
    load_env,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent
REPORT_PATH = REPO_ROOT / "run_data" / "db" / "backfill_qbank_ids_report.json"


def _request(url: str, secret: str, method: str, payload: dict | None = None) -> dict:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "x-import-secret": secret},
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} on {method} {url}: {e.read().decode()}") from e


def dump_category(url: str, secret: str, category: str) -> list[dict]:
    endpoint = f"{url.rstrip('/')}/api/admin/questions-dump?category={category}"
    body = _request(endpoint, secret, "GET")
    return body.get("questions", [])


def local_questions() -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT * FROM questions WHERE review_status='approved'"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def _options_of(row: dict) -> dict:
    return {
        "A": row.get("option_a") or "",
        "B": row.get("option_b") or "",
        "C": row.get("option_c") or "",
        "D": row.get("option_d") or "",
    }


def match(local: list[dict], remote: list[dict]) -> tuple[list[tuple], list[dict], list[dict]]:
    """Pair remote Selectly rows to local qbank rows on stem, then options.

    Returns (pairs, unmatched_remote, ambiguous_remote).
    """
    by_stem: dict[str, list[dict]] = defaultdict(list)
    for row in local:
        by_stem[build_stem(row)].append(row)

    pairs: list[tuple] = []
    unmatched: list[dict] = []
    ambiguous: list[dict] = []
    claimed: set[str] = set()

    for r in remote:
        if r.get("qbankId"):
            continue                              # already carries a handle
        candidates = [c for c in by_stem.get(r["stem"], []) if c["id"] not in claimed]
        if not candidates:
            unmatched.append(r)
            continue
        if len(candidates) > 1:
            # Same stem, different questions — tell them apart by their options.
            remote_opts = r.get("options") or {}
            narrowed = [c for c in candidates if _options_of(c) == remote_opts]
            if len(narrowed) != 1:
                ambiguous.append(r)
                continue
            candidates = narrowed
        pairs.append((r["id"], candidates[0]["id"], r["stem"]))
        claimed.add(candidates[0]["id"])

    return pairs, unmatched, ambiguous


def apply_fixes(url: str, secret: str, pairs: list[tuple], batch: int) -> tuple[int, list[str]]:
    endpoint = f"{url.rstrip('/')}/api/admin/questions-fix"
    updated, errors = 0, []
    for i in range(0, len(pairs), batch):
        chunk = pairs[i : i + batch]
        body = _request(
            endpoint,
            secret,
            "POST",
            {"fixes": [{"id": sid, "setQbankId": qid} for sid, qid, _ in chunk]},
        )
        updated += body.get("updated", 0)
        errors.extend(body.get("errors", []))
        logger.info(
            f"  batch {i // batch + 1}: updated={body.get('updated', 0)} "
            f"errors={len(body.get('errors', []))}"
        )
    return updated, errors


def run(args: argparse.Namespace) -> None:
    load_env()
    url = args.url or os.environ.get("SELECTLY_URL", "")
    secret = args.secret or os.environ.get("SELECTLY_IMPORT_SECRET", "")
    if not url:
        logger.error("No URL — set SELECTLY_URL in .env or pass --url")
        sys.exit(1)
    if not secret:
        logger.error("No secret — set SELECTLY_IMPORT_SECRET in .env or pass --secret")
        sys.exit(1)

    local = local_questions()
    logger.info(f"Local approved questions: {len(local)}")
    logger.info(f"Target: {url}")

    all_pairs: list[tuple] = []
    summary: dict[str, dict] = {}
    for category in VALID_SUBJECTS:
        remote = dump_category(url, secret, category)
        if not remote:
            continue
        local_cat = [r for r in local if r["subject"] == category]
        pairs, unmatched, ambiguous = match(local_cat, remote)
        all_pairs.extend(pairs)
        summary[category] = {
            "remote": len(remote),
            "local": len(local_cat),
            "matched": len(pairs),
            "unmatched": len(unmatched),
            "ambiguous": len(ambiguous),
            "unmatched_stems": [r["stem"][:120] for r in unmatched[:10]],
            "ambiguous_stems": [r["stem"][:120] for r in ambiguous[:10]],
        }
        logger.info(
            f"{category:24} remote={len(remote):>5} local={len(local_cat):>5} "
            f"matched={len(pairs):>5} unmatched={len(unmatched):>4} "
            f"ambiguous={len(ambiguous):>3}"
        )

    total_unmatched = sum(s["unmatched"] for s in summary.values())
    total_ambiguous = sum(s["ambiguous"] for s in summary.values())
    logger.info("─" * 60)
    logger.info(
        f"to backfill: {len(all_pairs)}  |  unmatched: {total_unmatched}  |  "
        f"ambiguous: {total_ambiguous}"
    )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    logger.info(f"Per-category report written to {REPORT_PATH}")

    if args.dry_run:
        logger.info("DRY RUN — no writes made.")
        for sid, qid, stem in all_pairs[:5]:
            logger.info(f"  would set qbank_id={qid} on {sid}  ({stem[:70]!r})")
        return

    updated, errors = apply_fixes(url, secret, all_pairs, args.batch)
    logger.info("─" * 60)
    logger.info(f"updated={updated}  errors={len(errors)}")
    for e in errors[:10]:
        logger.warning(f"  ! {e}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Backfill Selectly's questions.qbank_id by matching stems"
    )
    parser.add_argument("--url", default="", help="Selectly app URL (overrides .env)")
    parser.add_argument("--secret", default="", help="IMPORT_SECRET (overrides .env)")
    parser.add_argument("--batch", type=int, default=200, help="Fixes per POST (default 200)")
    parser.add_argument("--dry-run", action="store_true", help="Report without writing")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
