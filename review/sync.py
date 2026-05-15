"""
review/sync.py — sync approved questions to Supabase.

Usage:
    python review/sync.py --dry-run   # preview, no changes
    python review/sync.py             # execute sync
"""

import argparse
import logging
import os
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

_DEFAULT_DB      = os.getenv("DB_PATH", "/data/db/qbank.db")
_DEFAULT_FIGURES = os.getenv("FIGURES_DIR", "/data/db/figures")
_BUCKET          = os.getenv("SUPABASE_STORAGE_BUCKET", "figures")
_BATCH_SIZE      = 50  # questions per upsert call


def _get_supabase_client():
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_KEY", "")
    if not url or not key:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_KEY must be set in environment"
        )
    from supabase import create_client
    return create_client(url, key)


def _fetch_approved(db_path: str) -> list[dict]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM questions WHERE review_status = 'approved'"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _upload_figure(sb, figures_dir: str, figure_path: str, bucket: str) -> str | None:
    """Upload figure PNG to Supabase Storage. Returns public URL or None on failure."""
    local = Path(figure_path)
    if not local.exists():
        # Try resolving relative to figures_dir
        local = Path(figures_dir) / local.name
    if not local.exists():
        logger.warning(f"Figure file not found: {figure_path}")
        return None
    dest = local.name
    sb.storage.from_(bucket).upload(dest, local.read_bytes())
    url = sb.storage.from_(bucket).get_public_url(dest)
    return url


def dry_run(db_path: str = _DEFAULT_DB, supabase_client=None) -> dict:
    """Count approved questions that would be synced without making any changes."""
    approved = _fetch_approved(db_path)
    return {"would_sync": len(approved)}


def run(
    db_path: str = _DEFAULT_DB,
    supabase_client=None,
    figures_dir: str = _DEFAULT_FIGURES,
    bucket: str = _BUCKET,
) -> dict:
    """Upsert all approved questions to Supabase and upload any figure PNGs."""
    sb = supabase_client or _get_supabase_client()
    approved = _fetch_approved(db_path)

    stats = {"synced": 0, "failed": 0, "figures_uploaded": 0}

    # Batch upsert questions
    for i in range(0, len(approved), _BATCH_SIZE):
        batch = approved[i : i + _BATCH_SIZE]
        # Convert SQLite integers to Python bools for Supabase
        records = [
            {**q, "has_figure": bool(q["has_figure"]), "edited": bool(q["edited"])}
            for q in batch
        ]
        try:
            sb.table("questions").upsert(records).execute()
            stats["synced"] += len(batch)
        except Exception as e:
            logger.error(f"Failed to upsert batch starting at index {i}: {e}")
            stats["failed"] += len(batch)

    # Upload figures for questions that have them
    figure_questions = [q for q in approved if q.get("has_figure") and q.get("figure_path")]
    for q in figure_questions:
        try:
            _upload_figure(sb, figures_dir, q["figure_path"], bucket)
            stats["figures_uploaded"] += 1
        except Exception as e:
            logger.error(f"Failed to upload figure for question {q['id']}: {e}")

    logger.info(
        f"Sync complete: {stats['synced']} synced, "
        f"{stats['failed']} failed, "
        f"{stats['figures_uploaded']} figures uploaded"
    )
    return stats


def _cli():
    parser = argparse.ArgumentParser(description="Sync approved questions to Supabase")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview sync without making changes")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    if args.dry_run:
        result = dry_run()
        print(f"{result['would_sync']} questions would be synced")
    else:
        result = run()
        print(
            f"Sync complete: {result['synced']} synced, "
            f"{result['failed']} failed, "
            f"{result['figures_uploaded']} figures uploaded"
        )


if __name__ == "__main__":
    _cli()
