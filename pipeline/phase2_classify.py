"""
Phase 2 — Build page map from briefing.

Reads the .md briefing file and produces page_map.json listing every
relevant page with its subject. No API call — subject comes entirely
from the human-verified briefing.

Output: scratch/{book_id}/page_map.json
"""
import json
import logging
import os
from pathlib import Path

import pipeline.briefing as briefing_module

logger = logging.getLogger(__name__)


def run(
    book_id: str,
    briefing_path: str,
    scratch_dir: str = None,
) -> dict:
    """
    Build page_map.json for book_id.
    Returns the page map dict.
    """
    _scratch = scratch_dir or os.environ.get("SCRATCH_DIR", "/data/scratch")
    briefing_data = briefing_module.load(briefing_path)

    coverage = briefing_data["subject_coverage"]
    relevant_start = briefing_data["relevant_pages_start"]
    relevant_end = briefing_data["relevant_pages_end"]

    # Build page → subject lookup
    page_subject: dict[int, str] = {}
    for entry in coverage:
        for p in range(entry["pages_start"], entry["pages_end"] + 1):
            page_subject[p] = entry["subject"]

    pages = []
    for page_n in range(relevant_start, relevant_end + 1):
        subject = page_subject.get(page_n, "skip")
        pages.append({
            "page_number": page_n,
            "subject": subject,
        })

    page_map = {
        "book_id": book_id,
        "briefing_file": str(Path(briefing_path).name),
        "pages": pages,
    }

    out_dir = Path(_scratch) / book_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "page_map.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(page_map, f, indent=2)

    question_pages = [p for p in pages if p["subject"] != "skip"]
    logger.info(
        f"Phase 2 complete for {book_id}: {len(question_pages)} question pages, "
        f"{len(pages) - len(question_pages)} skipped"
    )
    return page_map
