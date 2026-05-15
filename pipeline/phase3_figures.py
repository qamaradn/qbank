"""
Phase 3 — Figure Detection and Sort
Reads docling_output.json + page_map.json, detects figures near text elements,
writes one JSON per text element to output/<subject>/text/ or figures/.
Pure coordinate maths — no ML, no API.
"""
import os
import json
import shutil
import logging

logger = logging.getLogger(__name__)


def detect_figure(
    question_element: dict,
    page_elements: list,
    threshold: int,
    figure_position: str = "below_question",
) -> dict:
    """
    Check whether any figure element is within threshold pixels of question_element.

    Args:
        question_element: the text element to check (dict with x, y, width, height)
        page_elements:    all elements on the page (text + figure)
        threshold:        max pixel distance to count as linked (from config)
        figure_position:  direction hint from briefing:
                          "below_question" | "above_question" | "beside_question"

    Returns:
        {"has_figure": bool, "figure_path": str | None}
    """
    q_y = question_element["y"]

    for el in page_elements:
        if el.get("type") != "figure":
            continue
        fig_path = el.get("figure_path")
        if not fig_path:
            continue

        fig_y = el["y"]

        if figure_position == "below_question":
            distance = fig_y - q_y
        elif figure_position == "above_question":
            distance = q_y - fig_y
        else:  # "beside_question" or unknown → check either direction
            distance = abs(fig_y - q_y)

        if 0 <= distance <= threshold:
            return {"has_figure": True, "figure_path": fig_path}

    return {"has_figure": False, "figure_path": None}


def run(
    book_id: str,
    scratch_dir: str = None,
    output_dir: str = None,
    briefing_path: str = None,
    page_map_path: str = None,
    docling_json_path: str = None,
) -> dict:
    """
    Phase 3: detect figures near text elements, sort into text/ or figures/.

    Returns dict: {"text": int, "figures": int, "skipped": int}
    """
    # Resolve paths
    _scratch = scratch_dir or os.environ.get("SCRATCH_DIR", "/data/scratch")
    _output  = output_dir  or os.environ.get("OUTPUT_DIR",  "/data/output")
    book_scratch = os.path.join(_scratch, book_id)

    _docling_path  = docling_json_path or os.path.join(book_scratch, "docling_output.json")
    _page_map_path = page_map_path     or os.path.join(book_scratch, "page_map.json")

    if not os.path.exists(_docling_path):
        raise FileNotFoundError(f"docling_output.json not found: {_docling_path}")
    if not os.path.exists(_page_map_path):
        raise FileNotFoundError(f"page_map.json not found: {_page_map_path}")

    with open(_docling_path, encoding="utf-8") as f:
        docling = json.load(f)
    with open(_page_map_path, encoding="utf-8") as f:
        page_map = json.load(f)

    # Briefing hint for figure_position
    figure_position = "below_question"
    if briefing_path and os.path.exists(briefing_path):
        import pipeline.briefing as briefing_module
        bd = briefing_module.load(briefing_path)
        figure_position = bd.get("figure_position", "below_question")

    # Threshold from env/config
    threshold = int(os.environ.get("FIGURE_PROXIMITY_PX", "150"))
    try:
        import config as _config
        threshold = getattr(_config, "FIGURE_PROXIMITY_PX", threshold)
    except Exception:
        pass

    # Index page_map by page number
    page_subjects = {p["page_number"]: p for p in page_map["pages"]}

    stats = {"text": 0, "figures": 0, "skipped": 0}

    for page_entry in docling["pages"]:
        page_n    = page_entry["page_number"]
        page_info = page_subjects.get(page_n)

        if page_info is None:
            logger.debug(f"Page {page_n}: not in page_map — skipping")
            stats["skipped"] += 1
            continue

        subject = page_info["subject"]
        if subject in ("answer_key", "skip"):
            logger.info(f"Page {page_n}: skipping {subject} page")
            stats["skipped"] += 1
            continue

        elements      = page_entry.get("elements", [])
        text_elements = [e for e in elements if e.get("type") == "text"]

        for idx, el in enumerate(text_elements):
            fig_result = detect_figure(el, elements, threshold, figure_position)
            source_id  = f"{book_id}_p{page_n}_e{idx}"

            record = {
                "source_id":   source_id,
                "book_id":     book_id,
                "page_number": page_n,
                "subject":     subject,
                "content":     el.get("text", ""),
                "has_figure":  fig_result["has_figure"],
                "figure_path": None,
                "element_bbox": {
                    "x": el["x"], "y": el["y"],
                    "width": el["width"], "height": el["height"],
                },
                "review_status": "pending",
            }

            if fig_result["has_figure"]:
                out_dir = os.path.join(_output, subject, "figures")
                os.makedirs(out_dir, exist_ok=True)
                json_path = os.path.join(out_dir, f"{source_id}.json")

                # Copy figure PNG to output dir
                src_fig = fig_result["figure_path"]
                if src_fig and os.path.exists(src_fig):
                    ext = os.path.splitext(src_fig)[1] or ".png"
                    dst_fig = os.path.join(out_dir, f"{source_id}_fig{ext}")
                    shutil.copy2(src_fig, dst_fig)
                    record["figure_path"] = dst_fig

                stats["figures"] += 1
            else:
                out_dir = os.path.join(_output, subject, "text")
                os.makedirs(out_dir, exist_ok=True)
                json_path = os.path.join(out_dir, f"{source_id}.json")
                stats["text"] += 1

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(record, f, indent=2, ensure_ascii=False)

    logger.info(
        f"Phase 3 done for {book_id}: "
        f"{stats['text']} text, {stats['figures']} figure, {stats['skipped']} skipped"
    )
    return stats
