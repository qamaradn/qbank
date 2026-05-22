"""
run_book.py — pipeline orchestrator.

Usage:
    python -m pipeline.run_book --book_id <id> --pdf <path/to/book.pdf> --briefing <path/to/book.md>
    python -m pipeline.run_book --book_id <id> --pdf <path> --briefing <path> --test-pages 61 62
    python -m pipeline.run_book --book_id <id> --status

Phases:
    1 — PDF → PNG (per subject subfolder)
    2 — Briefing → page_map.json
    3 — PNG + subject → Gemini → 10 MCQs per page
    4 — Dedup + load into DB
"""
import argparse
import logging
import os
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

_SCRATCH = os.environ.get("SCRATCH_DIR", "/data/scratch")
_OUTPUT = os.environ.get("OUTPUT_DIR", "/data/output")
_DB = os.environ.get("DB_PATH", "/data/db/qbank.db")


def get_status(book_id: str, scratch_dir: str, output_dir: str, db_path: str) -> dict:
    from pathlib import Path
    import sqlite3

    images_root = Path(scratch_dir) / book_id / "images"
    page_map = Path(scratch_dir) / book_id / "page_map.json"
    output_root = Path(output_dir)

    png_count = sum(1 for _ in images_root.rglob("*.png")) if images_root.exists() else 0
    json_count = sum(1 for _ in output_root.glob(f"*/generated/{book_id}_p*.json"))

    db_count = 0
    if Path(db_path).exists():
        try:
            conn = sqlite3.connect(db_path)
            db_count = conn.execute(
                "SELECT COUNT(*) FROM questions WHERE source_book=?", (book_id,)
            ).fetchone()[0]
            conn.close()
        except Exception:
            pass

    return {
        "phase1_pngs": png_count,
        "phase2_page_map": page_map.exists(),
        "phase3_json_files": json_count,
        "phase4_db_rows": db_count,
    }


def run(
    book_id: str,
    pdf_path: str,
    briefing_path: str,
    scratch_dir: str = None,
    output_dir: str = None,
    db_path: str = None,
    test_pages: list = None,
) -> dict:
    _scratch = scratch_dir or _SCRATCH
    _output = output_dir or _OUTPUT
    _db = db_path or _DB

    import pipeline.briefing as briefing_module
    briefing_data = briefing_module.load(briefing_path)

    results = {}

    if test_pages:
        logger.info(f"[{book_id}] TEST MODE: pages {test_pages}")
        # In test mode, skip Phase 1 (assume PNGs already exist) and Phase 2
        # Go straight to Phase 3 + 4
    else:
        # Phase 1 — extract PNGs
        logger.info(f"[{book_id}] Phase 1: Extract PNGs")
        import pipeline.phase1_normalise as p1
        results["phase1"] = p1.extract_pages(
            pdf_path=pdf_path,
            book_id=book_id,
            briefing_data=briefing_data,
            scratch_dir=_scratch,
        )

        # Phase 2 — build page map
        logger.info(f"[{book_id}] Phase 2: Build page map")
        import pipeline.phase2_classify as p2
        p2.run(
            book_id=book_id,
            briefing_path=briefing_path,
            scratch_dir=_scratch,
        )

    # Phase 3 — generate questions
    logger.info(f"[{book_id}] Phase 3: Generate questions")
    import pipeline.phase3_generate as p3
    results["phase3"] = p3.run(
        book_id=book_id,
        scratch_dir=_scratch,
        output_dir=_output,
        briefing_data=briefing_data,
        briefing_path=briefing_path,
        test_pages=test_pages,
    )

    # Phase 4 — dedup + load
    logger.info(f"[{book_id}] Phase 4: Load into DB")
    import pipeline.phase4_load as p4
    results["phase4"] = p4.load_book(
        book_id=book_id,
        output_dir=_output,
        db_path=_db,
    )

    logger.info(f"[{book_id}] Pipeline complete: {results}")
    return results


def _cli():
    parser = argparse.ArgumentParser(description="QBank pipeline orchestrator")
    parser.add_argument("--book_id", required=True)
    parser.add_argument("--pdf", dest="pdf_path", default=None)
    parser.add_argument("--briefing", dest="briefing_path", default=None)
    parser.add_argument("--test-pages", nargs="+", type=int, metavar="PAGE")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()

    scratch = os.environ.get("SCRATCH_DIR", _SCRATCH)
    output = os.environ.get("OUTPUT_DIR", _OUTPUT)
    db = os.environ.get("DB_PATH", _DB)

    if args.status:
        s = get_status(args.book_id, scratch, output, db)
        for k, v in s.items():
            print(f"  {k}: {v}")
        return

    # Resolve briefing path: explicit arg, or look alongside PDF, or look in run_data/pdfs
    briefing_path = args.briefing_path
    if not briefing_path and args.pdf_path:
        briefing_path = str(Path(args.pdf_path).with_suffix(".md"))
    if not briefing_path:
        briefing_path = f"run_data/pdfs/{args.book_id}.md"

    pdf_path = args.pdf_path or f"run_data/pdfs/{args.book_id}.pdf"

    if args.test_pages:
        run(
            book_id=args.book_id,
            pdf_path=pdf_path,
            briefing_path=briefing_path,
            scratch_dir=scratch,
            output_dir=output,
            db_path=db,
            test_pages=args.test_pages,
        )
    else:
        if not Path(pdf_path).exists():
            parser.error(f"PDF not found: {pdf_path}")
        run(
            book_id=args.book_id,
            pdf_path=pdf_path,
            briefing_path=briefing_path,
            scratch_dir=scratch,
            output_dir=output,
            db_path=db,
        )


if __name__ == "__main__":
    _cli()
