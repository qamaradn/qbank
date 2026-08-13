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
    # Fixed-form delivery. Selectly's import schema does not accept these yet (zod strips
    # unknown keys silently, so sending them early is harmless); once it does, a reload
    # carries form membership instead of needing a second pass over every row.
    if row.get("form_id"):
        q["formId"] = row["form_id"]
        q["formPosition"] = row["form_position"]
        q["formKind"] = row["form_kind"]
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

    to_push = [r for r in all_rows if r["id"] not in already_pushed]

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
