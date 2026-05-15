"""
run_book.py — pipeline orchestrator.

Usage:
    python pipeline/run_book.py --book_id <id> --pdf /data/pdfs/<id>.pdf
    python pipeline/run_book.py --book_id <id> --pdf /data/pdfs/<id>.pdf --pages 70 85
    python pipeline/run_book.py --book_id <id> --status
"""

import argparse
import json
import logging
import os
import re
import sys

import pipeline.briefing as briefing_module

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

_BOOK_ID_RE = re.compile(r"^[A-Za-z0-9_]+$")


def validate_book_id(book_id: str) -> None:
    """Raise ValueError if book_id contains characters other than alphanumeric/underscore."""
    if not _BOOK_ID_RE.match(book_id):
        raise ValueError(
            f"book_id must be alphanumeric with underscores only, got: {book_id!r}"
        )


def require_briefing(book_id: str, pdf_path: str) -> dict:
    """Load the briefing .md file for this PDF, or raise with a helpful message."""
    briefing_path = os.path.splitext(pdf_path)[0] + ".md"
    if not os.path.exists(briefing_path):
        raise FileNotFoundError(
            f"\n\nBRIEFING FILE MISSING: {briefing_path}\n"
            f"You must create this file before running the pipeline.\n"
            f"Template: see CLAUDE.md -> PDF METADATA BRIEFING FILES\n"
        )
    return briefing_module.load(briefing_path)


def get_status(book_id: str, scratch_dir: str = None, output_dir: str = None) -> dict:
    """Return a dict describing which phases have produced output for book_id."""
    if scratch_dir is None:
        scratch_dir = os.getenv("SCRATCH_DIR", "/data/scratch")
    if output_dir is None:
        output_dir = os.getenv("OUTPUT_DIR", "/data/output")

    book_scratch = os.path.join(scratch_dir, book_id)

    # Phase 1: pages/ directory has at least one .md file
    pages_dir = os.path.join(book_scratch, "pages")
    if os.path.isdir(pages_dir) and any(
        f.endswith(".md") for f in os.listdir(pages_dir)
    ):
        p1 = "complete"
    else:
        p1 = "not_started"

    # Phase 2: page_map.json exists
    page_map_path = os.path.join(book_scratch, "page_map.json")
    p2 = "complete" if os.path.exists(page_map_path) else "not_started"

    # Phase 3: any output JSON in output_dir/<subject>/text/ or figures/
    p3 = "not_started"
    if os.path.isdir(output_dir):
        for subject in os.listdir(output_dir):
            for track in ("text", "figures"):
                track_dir = os.path.join(output_dir, subject, track)
                if os.path.isdir(track_dir) and any(
                    f.endswith(".json") for f in os.listdir(track_dir)
                ):
                    p3 = "complete"
                    break
            if p3 == "complete":
                break

    # Phase 4: any generated JSON in output_dir/<subject>/generated/
    p4 = "not_started"
    if os.path.isdir(output_dir):
        for subject in os.listdir(output_dir):
            gen_dir = os.path.join(output_dir, subject, "generated")
            if os.path.isdir(gen_dir) and any(
                f.endswith(".json") for f in os.listdir(gen_dir)
            ):
                p4 = "complete"
                break

    return {
        "book_id": book_id,
        "phase1": p1,
        "phase2": p2,
        "phase3": p3,
        "phase4": p4,
    }


# ── thin wrappers so tests can monkeypatch individual phases ──────────────────

def _run_phase1(book_id, pdf_path, scratch_dir=None, briefing_path=None):
    import pipeline.phase1_normalise as p1
    p1.run(book_id, pdf_path, scratch_dir=scratch_dir, briefing_path=briefing_path)


def _run_phase2(book_id, scratch_dir=None, briefing_path=None):
    import pipeline.phase2_classify as p2
    p2.run(book_id, scratch_dir=scratch_dir, briefing_path=briefing_path)


def _run_phase3(book_id, scratch_dir=None, output_dir=None, briefing_path=None):
    import pipeline.phase3_figures as p3
    p3.run(book_id, scratch_dir=scratch_dir, output_dir=output_dir,
           briefing_path=briefing_path)


def _run_phase4(book_id, output_dir=None, scratch_dir=None, briefing_path=None):
    import pipeline.phase4_generate as p4
    p4.run(book_id, output_dir=output_dir, scratch_dir=scratch_dir,
           briefing_path=briefing_path)


def run(
    book_id: str,
    pdf_path: str,
    scratch_dir: str = None,
    output_dir: str = None,
    briefing_path: str = None,
) -> None:
    """Orchestrate all 4 pipeline phases for a single book."""
    validate_book_id(book_id)

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    # Enforce briefing requirement before doing any work
    if briefing_path is None:
        briefing_path = os.path.splitext(pdf_path)[0] + ".md"
    require_briefing(book_id, pdf_path)

    logger.info(f"[{book_id}] Starting pipeline - Phase 1: Normalise")
    _run_phase1(book_id, pdf_path, scratch_dir=scratch_dir, briefing_path=briefing_path)

    logger.info(f"[{book_id}] Phase 2: Classify")
    _run_phase2(book_id, scratch_dir=scratch_dir, briefing_path=briefing_path)

    logger.info(f"[{book_id}] Phase 3: Figure Detection")
    _run_phase3(book_id, scratch_dir=scratch_dir, output_dir=output_dir,
                briefing_path=briefing_path)

    logger.info(f"[{book_id}] Phase 4: Generate Questions")
    _run_phase4(book_id, output_dir=output_dir, scratch_dir=scratch_dir,
                briefing_path=briefing_path)

    logger.info(f"[{book_id}] Pipeline complete.")


def _cli():
    parser = argparse.ArgumentParser(description="QBank pipeline orchestrator")
    parser.add_argument("--book_id", required=True,
                        help="Book identifier (alphanumeric + underscores)")
    parser.add_argument("--pdf", dest="pdf_path",
                        help="Path to PDF file")
    parser.add_argument("--pages", nargs=2, type=int, metavar=("START", "END"),
                        help="Process only pages START-END")
    parser.add_argument("--status", action="store_true",
                        help="Show pipeline status without running")
    args = parser.parse_args()

    scratch_dir = os.getenv("SCRATCH_DIR", "/data/scratch")
    output_dir = os.getenv("OUTPUT_DIR", "/data/output")

    if args.status:
        status = get_status(args.book_id, scratch_dir=scratch_dir, output_dir=output_dir)
        print(json.dumps(status, indent=2))
        return

    if not args.pdf_path:
        pdf_dir = os.getenv("PDF_DIR", "/data/pdfs")
        args.pdf_path = os.path.join(pdf_dir, f"{args.book_id}.pdf")

    run(
        book_id=args.book_id,
        pdf_path=args.pdf_path,
        scratch_dir=scratch_dir,
        output_dir=output_dir,
    )


if __name__ == "__main__":
    _cli()
