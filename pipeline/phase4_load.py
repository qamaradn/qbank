"""
Phase 4 — Dedup and Load into DB.

For each generated questions JSON:
  1. Load existing stems for that subject from DB
  2. Skip questions whose stem is too similar to an existing one (SequenceMatcher >= 0.85)
  3. Insert remaining questions into DB with review_status='pending'

All questions go to review — confidence is displayed as a triage signal only.
"""
import json
import logging
import os
import sqlite3
from difflib import SequenceMatcher
from pathlib import Path

logger = logging.getLogger(__name__)

_DEDUP_THRESHOLD = float(os.environ.get("DEDUP_THRESHOLD", "0.85"))
_DEFAULT_DB = os.environ.get("DB_PATH", "/data/db/qbank.db")


def _is_duplicate(new_stem: str, existing_stems: list[str], threshold: float) -> bool:
    new_lower = new_stem.lower()
    for stem in existing_stems:
        ratio = SequenceMatcher(None, new_lower, stem.lower()).ratio()
        if ratio >= threshold:
            return True
    return False


def _get_existing_stems(conn: sqlite3.Connection, subject: str) -> list[str]:
    rows = conn.execute(
        "SELECT stem FROM questions WHERE subject=?", (subject,)
    ).fetchall()
    return [r[0] for r in rows if r[0]]


def _insert_question(conn: sqlite3.Connection, q: dict) -> None:
    conn.execute(
        """INSERT INTO questions (
            id, subject, stem, option_a, option_b, option_c, option_d,
            correct_answer, explanation, topic, difficulty, confidence,
            source_book, source_page, source_page_description, passage,
            figure_svg, review_status, created_at
        ) VALUES (
            :id, :subject, :stem, :option_a, :option_b, :option_c, :option_d,
            :correct_answer, :explanation, :topic, :difficulty, :confidence,
            :source_book, :source_page, :source_page_description, :passage,
            :figure_svg, :review_status, :created_at
        )""",
        q,
    )


def load_book(
    book_id: str,
    output_dir: str = None,
    db_path: str = None,
) -> dict:
    """
    Load all generated questions for book_id into the DB.

    Returns: {"inserted": int, "duplicate": int, "failed": int}
    """
    _output = output_dir or os.environ.get("OUTPUT_DIR", "/data/output")
    _db = db_path or _DEFAULT_DB

    conn = sqlite3.connect(_db)
    stats = {"inserted": 0, "duplicate": 0, "failed": 0}

    # Collect all generated JSON files for this book across all subjects
    output_root = Path(_output)
    json_files = sorted(output_root.glob(f"*/generated/{book_id}_p*.json"))

    if not json_files:
        logger.warning(f"No generated JSON files found for {book_id} in {_output}")
        conn.close()
        return stats

    # Cache existing stems per subject to avoid repeated DB queries
    stems_cache: dict[str, list[str]] = {}

    for json_path in json_files:
        subject = json_path.parts[-3]  # output/{subject}/generated/...

        if subject not in stems_cache:
            stems_cache[subject] = _get_existing_stems(conn, subject)

        try:
            questions = json.loads(json_path.read_text(encoding="utf-8"))
        except Exception as e:
            logger.error(f"Failed to read {json_path}: {e}")
            stats["failed"] += 1
            continue

        for q in questions:
            q.setdefault("figure_svg", None)
            stem = q.get("stem", "")
            if not stem:
                stats["failed"] += 1
                continue
            if q.get("correct_answer") not in ("A", "B", "C", "D"):
                logger.warning(f"Skipped (invalid correct_answer={q.get('correct_answer')!r}): {stem[:60]}")
                stats["failed"] += 1
                continue

            if _is_duplicate(stem, stems_cache[subject], _DEDUP_THRESHOLD):
                logger.info(f"Duplicate skipped: {stem[:60]}...")
                stats["duplicate"] += 1
                continue

            try:
                _insert_question(conn, q)
                stems_cache[subject].append(stem)
                stats["inserted"] += 1
                logger.info(f"Inserted: [{subject}] {stem[:60]}...")
            except Exception as e:
                logger.error(f"Insert failed for question {q.get('id')}: {e}")
                stats["failed"] += 1

    conn.commit()
    conn.close()
    logger.info(f"Phase 4 complete for {book_id}: {stats}")
    return stats
