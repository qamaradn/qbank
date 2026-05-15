"""Phase 1 — Normalise: convert PDF to markdown + images using Docling."""
import json
import logging
import os
import re

import pipeline.briefing as briefing_module

logger = logging.getLogger(__name__)

# Redirect HuggingFace model cache away from /home (which may be full)
# to /scratch which has ample space.  Must be set before any docling import.
_HF_CACHE = os.environ.get("HF_HOME", "/scratch/hf_cache")
os.environ.setdefault("HF_HOME", _HF_CACHE)
os.environ.setdefault("HUGGINGFACE_HUB_CACHE", _HF_CACHE)
os.makedirs(_HF_CACHE, exist_ok=True)


def validate_book_id(book_id: str) -> None:
    """Raise ValueError if book_id contains characters other than letters, digits, and underscores."""
    if not re.match(r"^[A-Za-z0-9_]+$", book_id):
        raise ValueError(
            f"book_id '{book_id}' is invalid: must contain only letters, digits, and underscores"
        )


def run(
    book_id: str,
    pdf_path: str,
    scratch_dir: str = None,
    briefing_path: str = None,
) -> dict:
    """
    Phase 1: normalise a PDF book using Docling.

    Args:
        book_id: identifier for the book (alphanumeric + underscores only)
        pdf_path: path to the PDF file
        scratch_dir: where to write output (defaults to config SCRATCH_DIR)
        briefing_path: path to the .md briefing file
                       (defaults to pdf_path with .pdf → .md extension)

    Returns:
        dict with keys: book_id, total_pages, pages (list of page entries)
    """
    validate_book_id(book_id)

    # Resolve defaults
    if scratch_dir is None:
        from config import SCRATCH_DIR
        scratch_dir = SCRATCH_DIR

    if briefing_path is None:
        briefing_path = pdf_path.replace(".pdf", ".md")

    # Load briefing — raises FileNotFoundError if missing
    briefing_data = _require_briefing(briefing_path)

    # Validate PDF exists
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    # Create output directories
    book_scratch = os.path.join(scratch_dir, book_id)
    pages_dir = os.path.join(book_scratch, "pages")
    images_dir = os.path.join(book_scratch, "images")
    figures_dir = os.path.join(book_scratch, "figures")
    for d in [pages_dir, images_dir, figures_dir]:
        os.makedirs(d, exist_ok=True)

    # Determine relevant page range from briefing
    rel_start = briefing_data["relevant_pages_start"]
    rel_end = briefing_data["relevant_pages_end"]

    # Determine candidate relevant pages from briefing range.
    # We don't know total_pages yet (that requires Docling), so we build
    # a provisional list; Docling will clip if the PDF is shorter.
    candidate_pages = list(range(rel_start, rel_end + 1))

    # Full-book resumability: if every candidate page already has its .md file,
    # skip Docling entirely and rebuild output from existing files.
    if _all_pages_done(pages_dir, candidate_pages):
        logger.info(
            "All %d pages already processed — skipping Docling entirely",
            len(candidate_pages),
        )
        pages_output = _rebuild_from_existing(pages_dir, images_dir, candidate_pages)
        output = {
            "book_id": book_id,
            "total_pages": len(candidate_pages),
            "pages": pages_output,
        }
        json_path = os.path.join(book_scratch, "docling_output.json")
        with open(json_path, "w", encoding="utf-8") as fh:
            json.dump(output, fh, indent=2, ensure_ascii=False)
        logger.info(
            "Phase 1 complete (resumed): %d pages from %s",
            len(pages_output),
            book_scratch,
        )
        return output

    # Normal path: run Docling on the full PDF
    docling_result = _run_docling(pdf_path, briefing_data)

    doc = docling_result.document
    total_pages = doc.num_pages()

    # Clip candidate pages to what the PDF actually contains
    relevant_pages = [p for p in candidate_pages if p <= total_pages]

    pages_output = []
    for page_n in relevant_pages:
        # Per-page resumability: skip pages already done (handles partial runs)
        md_path = os.path.join(pages_dir, f"{page_n}.md")
        if os.path.exists(md_path):
            logger.info("Skipping page %d (already done)", page_n)
            pages_output.append({"page_number": page_n, "markdown_path": md_path})
            continue

        try:
            page_entry = _process_page(
                docling_result,
                page_n,
                pages_dir,
                images_dir,
                figures_dir,
            )
            pages_output.append(page_entry)
            logger.info("Processed page %d", page_n)
        except Exception as exc:
            logger.error("Error processing page %d: %s", page_n, exc)
            continue

    # Write docling_output.json
    output = {
        "book_id": book_id,
        "total_pages": total_pages,
        "pages": pages_output,
    }
    json_path = os.path.join(book_scratch, "docling_output.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(output, fh, indent=2, ensure_ascii=False)

    logger.info(
        "Phase 1 complete: %d pages written to %s",
        len(pages_output),
        book_scratch,
    )
    return output


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _all_pages_done(pages_dir: str, relevant_pages: list) -> bool:
    """Return True if every page in relevant_pages already has a .md file."""
    return bool(relevant_pages) and all(
        os.path.exists(os.path.join(pages_dir, f"{n}.md"))
        for n in relevant_pages
    )


def _rebuild_from_existing(pages_dir: str, images_dir: str, relevant_pages: list) -> list:
    """
    Rebuild a pages_output list from already-written .md (and optional .png) files.

    Used by the full-book resumability path when Docling is skipped entirely.
    elements is empty on resume — Phase 2 only needs markdown_path.
    """
    pages_output = []
    for n in relevant_pages:
        md_path = os.path.join(pages_dir, f"{n}.md")
        img_path = os.path.join(images_dir, f"{n}.png")
        entry = {
            "page_number": n,
            "markdown_path": md_path,
            "image_path": img_path if os.path.exists(img_path) else None,
            "elements": [],  # not re-extracted on resume; Phase 2 uses markdown only
        }
        pages_output.append(entry)
    return pages_output


def _require_briefing(briefing_path: str) -> dict:
    """Load the briefing file; raise FileNotFoundError (with 'briefing' in msg) if absent."""
    if not os.path.exists(briefing_path):
        raise FileNotFoundError(
            f"\n\nBRIEFING FILE MISSING: {briefing_path}\n"
            f"You must create this file before running the pipeline.\n"
            f"Template: see CLAUDE.md → PDF METADATA BRIEFING FILES\n"
        )
    return briefing_module.load(briefing_path)


def _run_docling(pdf_path: str, briefing_data: dict):
    """
    Call Docling once on the full PDF.

    Pipeline options:
    - OCR disabled (born-digital PDF; enabled on VM for real scanned books)
    - Table structure disabled (not needed for Phase 1 output)
    - Page images enabled so full-page PNGs are available for figure cropping
    - Picture images enabled so PictureItem.image.pil_image is populated

    Returns:
        ConversionResult
    """
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.datamodel.base_models import InputFormat

    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = False
    pipeline_options.generate_page_images = True
    pipeline_options.generate_picture_images = True

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    return converter.convert(pdf_path)


def _process_page(
    docling_result,
    page_n: int,
    pages_dir: str,
    images_dir: str,
    figures_dir: str,
) -> dict:
    """
    Process a single page: extract markdown text, collect element bboxes.

    Page images and figure crops are attempted but failures are non-fatal;
    the entry is still written so Phase 2 can classify the page.
    """
    doc = docling_result.document

    # --- Markdown for this page ---
    page_md = _extract_page_markdown(doc, page_n)
    md_path = os.path.join(pages_dir, f"{page_n}.md")
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write(page_md)

    if not page_md.strip():
        logger.warning("Page %d: OCR produced empty markdown", page_n)

    # --- Page image (best-effort) ---
    img_path = os.path.join(images_dir, f"{page_n}.png")
    img_path = _write_page_image(docling_result, page_n, img_path)

    # --- Elements with bounding boxes ---
    elements = _extract_elements(doc, page_n, figures_dir)

    return {
        "page_number": page_n,
        "markdown_path": md_path,
        "image_path": img_path,
        "elements": elements,
    }


def _extract_page_markdown(doc, page_n: int) -> str:
    """
    Collect text from all items whose provenance is on page_n and join them.

    Docling's iterate_items() yields every content item across the whole
    document; we filter by prov.page_no and concatenate the texts.
    """
    lines = []
    for item, _ in doc.iterate_items():
        if not (hasattr(item, "prov") and item.prov):
            continue
        for prov in item.prov:
            if hasattr(prov, "page_no") and prov.page_no == page_n:
                if hasattr(item, "text") and item.text:
                    lines.append(item.text)
                break
    return "\n\n".join(lines)


def _write_page_image(docling_result, page_n: int, img_path: str):
    """
    Write the full-page PNG for page_n.

    doc.pages is a dict keyed by 1-indexed page numbers.
    When generate_page_images=False the .image attribute is None; in that case
    we fall back to a blank placeholder so img_path is always set.

    Returns the img_path on success, or None if writing fails entirely.
    """
    doc = docling_result.document
    try:
        page_item = doc.pages.get(page_n)
        if page_item is not None and page_item.image is not None:
            pil_img = getattr(page_item.image, "pil_image", None)
            if pil_img is not None:
                pil_img.save(img_path, "PNG")
                return img_path

        # Fallback: blank white placeholder
        try:
            from PIL import Image
            img = Image.new("RGB", (800, 1100), color=(255, 255, 255))
            img.save(img_path, "PNG")
            return img_path
        except ImportError:
            return None
    except Exception as exc:
        logger.warning("Page %d: could not write image: %s", page_n, exc)
        return None


def _extract_elements(doc, page_n: int, figures_dir: str) -> list:
    """
    Extract text and figure elements with bounding boxes for page_n.

    BoundingBox coord_origin is BOTTOMLEFT; we expose raw l/t/r/b values
    so downstream phases that work with Docling coordinates remain consistent.
    """
    from docling.datamodel.document import PictureItem

    elements = []
    fig_count = 0

    for item, _ in doc.iterate_items():
        if not (hasattr(item, "prov") and item.prov):
            continue

        for prov in item.prov:
            if not (hasattr(prov, "page_no") and prov.page_no == page_n):
                continue

            bbox = prov.bbox if hasattr(prov, "bbox") else None
            x = float(bbox.l) if bbox else 0.0
            y = float(bbox.t) if bbox else 0.0
            w = float(bbox.r - bbox.l) if bbox else 0.0
            h = float(bbox.b - bbox.t) if bbox else 0.0

            if isinstance(item, PictureItem):
                fig_count += 1
                fig_path = os.path.join(figures_dir, f"{page_n}_fig_{fig_count}.png")
                fig_path = _save_figure(item, fig_path)

                el = {
                    "type": "figure",
                    "text": "",
                    "x": x,
                    "y": y,
                    "width": w,
                    "height": h,
                }
                if fig_path and os.path.exists(fig_path):
                    el["figure_path"] = fig_path
                elements.append(el)
            else:
                text = (item.text if hasattr(item, "text") and item.text else "")
                elements.append({
                    "type": "text",
                    "text": text,
                    "x": x,
                    "y": y,
                    "width": w,
                    "height": h,
                })
            break  # only use first prov entry per item per page

    return elements


def _save_figure(picture_item, fig_path: str):
    """Save a PictureItem's image to disk. Returns fig_path on success, else None."""
    try:
        img_ref = getattr(picture_item, "image", None)
        if img_ref is None:
            return None
        pil_img = getattr(img_ref, "pil_image", None)
        if pil_img is not None:
            pil_img.save(fig_path, "PNG")
            return fig_path
        return None
    except Exception as exc:
        logger.warning("Could not save figure: %s", exc)
        return None
