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
import hashlib
import json
import logging
import os
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

SCHOOL_IDS = ["vic-seal", "nsw-shspt"]

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


def load_tracking() -> set:
    if TRACKING_FILE.exists():
        data = json.loads(TRACKING_FILE.read_text())
        return set(data.get("pushed_ids", []))
    return set()


def save_tracking(pushed_ids: set) -> None:
    TRACKING_FILE.parent.mkdir(parents=True, exist_ok=True)
    TRACKING_FILE.write_text(json.dumps({"pushed_ids": sorted(pushed_ids)}, indent=2))


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


def row_to_question(row: dict) -> dict:
    q: dict = {
        "questionType": "mcq",
        "category": row["subject"],
        "difficulty": row["difficulty"],
        "schoolIds": SCHOOL_IDS,
        "stem": build_stem(row),
        "options": {
            "A": row.get("option_a") or "",
            "B": row.get("option_b") or "",
            "C": row.get("option_c") or "",
            "D": row.get("option_d") or "",
        },
        "correctAnswer": row["correct_answer"],
        "explanation": row.get("explanation") or "",
        "imageUrl": None,
    }
    pid = passage_id(row)
    if pid is not None:
        q["passageId"] = pid
    return q


def fetch_approved(subject: str | None) -> list[dict]:
    if not DB_PATH.exists():
        logger.error(f"Database not found: {DB_PATH}")
        sys.exit(1)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        if subject:
            rows = conn.execute(
                "SELECT * FROM questions WHERE review_status='approved' AND subject=? ORDER BY created_at",
                (subject,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM questions WHERE review_status='approved' ORDER BY subject, created_at"
            ).fetchall()
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
    all_rows = fetch_approved(args.subject)
    to_push = [r for r in all_rows if r["id"] not in already_pushed]

    # Summary
    by_subject: dict[str, int] = {}
    for r in to_push:
        by_subject[r["subject"]] = by_subject.get(r["subject"], 0) + 1

    logger.info(f"Approved in DB : {len(all_rows)}")
    logger.info(f"Already pushed : {len(already_pushed)}")
    logger.info(f"To push        : {len(to_push)}")
    for subj, count in sorted(by_subject.items()):
        logger.info(f"  {subj}: {count}")

    if not to_push:
        logger.info("Nothing new to push.")
        return

    if args.dry_run:
        logger.info("DRY RUN — no API calls made.")
        logger.info("Sample converted question:")
        sample = row_to_question(to_push[0])
        preview = json.dumps(sample, indent=2)
        logger.info(preview[:600] + ("..." if len(preview) > 600 else ""))
        return

    url = args.url or os.environ.get("SELECTLY_URL", "")
    secret = args.secret or os.environ.get("SELECTLY_IMPORT_SECRET", "")

    if not url:
        logger.error("No URL — set SELECTLY_URL in .env or pass --url")
        sys.exit(1)
    if not secret:
        logger.error("No secret — set SELECTLY_IMPORT_SECRET in .env or pass --secret")
        sys.exit(1)

    logger.info(f"Target: {url}")

    batch_size = args.batch
    batches = [to_push[i : i + batch_size] for i in range(0, len(to_push), batch_size)]
    logger.info(f"Pushing in {len(batches)} batches of up to {batch_size}")

    total_inserted = total_skipped = 0
    total_errors: list[str] = []
    newly_pushed: set[str] = set()

    for i, batch in enumerate(batches, 1):
        questions = [row_to_question(r) for r in batch]
        logger.info(f"Batch {i}/{len(batches)} ({len(questions)} questions)...")
        try:
            inserted, skipped, errors = post_batch(url, secret, questions)
            total_inserted += inserted
            total_skipped += skipped
            total_errors.extend(errors)
            for r in batch:
                newly_pushed.add(r["id"])
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

    save_tracking(already_pushed | newly_pushed)

    logger.info("─" * 50)
    logger.info(f"inserted={total_inserted}  skipped={total_skipped}  errors={len(total_errors)}")
    logger.info(f"Cumulative pushed: {len(already_pushed | newly_pushed)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Push approved qbank questions to Selectly")
    parser.add_argument("--url", default="", help="Selectly app URL (overrides .env)")
    parser.add_argument("--secret", default="", help="IMPORT_SECRET (overrides .env)")
    parser.add_argument("--subject", choices=VALID_SUBJECTS, help="Push one subject only")
    parser.add_argument("--batch", type=int, default=100, help="Questions per POST (default 100)")
    parser.add_argument("--dry-run", action="store_true", help="Show plan without sending")
    parser.add_argument("--reset-tracking", action="store_true", help="Clear push tracking and exit")
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
