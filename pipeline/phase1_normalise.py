"""
Phase 1 — PDF to PNG extraction.

For each relevant page declared in the briefing:
  - Extracts the page as a PNG using pdf2image (pdftoppm)
  - Saves to: scratch/{book_id}/images/{subject}/{book_id}_{DDMMYY}_p{n}.png
  - Skips pages already extracted (resumable)

Requires: poppler-utils (pdftoppm) installed on the system.
"""
import logging
import os
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

_DEFAULT_DPI = int(os.environ.get("PNG_DPI", "150"))


def _short_date() -> str:
    return datetime.now().strftime("%d%m%y")


def extract_pages(
    pdf_path: str,
    book_id: str,
    briefing_data: dict,
    scratch_dir: str,
    dpi: int = _DEFAULT_DPI,
) -> dict:
    """
    Extract relevant pages from PDF into subject-organised PNG folders.

    Returns: {"extracted": int, "skipped": int, "failed": int}
    """
    try:
        from pdf2image import convert_from_path
    except ImportError:
        raise RuntimeError("pdf2image not installed. Run: pip install pdf2image")

    date_str = _short_date()
    images_root = Path(scratch_dir) / book_id / "images"
    images_root.mkdir(parents=True, exist_ok=True)

    relevant_start = briefing_data["relevant_pages_start"]
    relevant_end = briefing_data["relevant_pages_end"]
    coverage = briefing_data["subject_coverage"]

    # Build page → subject lookup
    page_subject: dict[int, str] = {}
    for entry in coverage:
        for p in range(entry["pages_start"], entry["pages_end"] + 1):
            page_subject[p] = entry["subject"]

    stats = {"extracted": 0, "skipped": 0, "failed": 0}

    for page_n in range(relevant_start, relevant_end + 1):
        subject = page_subject.get(page_n)
        if subject is None or subject == "skip":
            stats["skipped"] += 1
            continue

        subject_dir = images_root / subject
        subject_dir.mkdir(parents=True, exist_ok=True)
        out_path = subject_dir / f"{book_id}_{date_str}_p{page_n}.png"

        if out_path.exists():
            logger.info(f"Page {page_n}: already extracted — skipping")
            stats["skipped"] += 1
            continue

        try:
            images = convert_from_path(
                pdf_path,
                dpi=dpi,
                first_page=page_n,
                last_page=page_n,
            )
            if not images:
                logger.warning(f"Page {page_n}: no image returned")
                stats["failed"] += 1
                continue
            images[0].save(str(out_path), "PNG")
            logger.info(f"Page {page_n} ({subject}): saved {out_path.name}")
            stats["extracted"] += 1
        except Exception as e:
            logger.error(f"Page {page_n}: extraction failed: {e}")
            stats["failed"] += 1

    logger.info(f"Phase 1 complete for {book_id}: {stats}")
    return stats


def get_page_image_path(
    book_id: str,
    page_n: int,
    subject: str,
    scratch_dir: str,
) -> str | None:
    """
    Find the PNG for a given page. Returns path string or None if not found.
    Matches any date suffix since date is embedded at extraction time.
    """
    subject_dir = Path(scratch_dir) / book_id / "images" / subject
    if not subject_dir.exists():
        return None
    pattern = f"{book_id}_*_p{page_n}.png"
    matches = list(subject_dir.glob(pattern))
    return str(matches[0]) if matches else None
