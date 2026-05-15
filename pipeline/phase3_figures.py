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
    """Placeholder — implemented in Task 3."""
    raise NotImplementedError("run() not yet implemented")
