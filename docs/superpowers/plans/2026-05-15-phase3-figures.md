# Phase 3 — Figure Detection: Implementation Plan
**Date:** 2026-05-15
**Status:** Approved
**Branch:** feature/phase3-figures

---

## Overview

Build `pipeline/phase3_figures.py` — pure coordinate maths, no ML, no API.
Reads `docling_output.json` + `page_map.json`, detects figures near text elements,
writes one JSON per text element to `/data/output/<subject>/text/` or `figures/`.

Unit = one text element → one JSON file.
Proximity = y-distance between element and figure, ≤ FIGURE_PROXIMITY_PX.
All tests are fast (no Docling, no Gemini).

---

## Task 0 — Feature branch
**Time:** ~2 min

```bash
git checkout main && git checkout -b feature/phase3-figures
```

No new dependencies — Phase 3 is pure stdlib.

Commit: `chore(phase3): create feature branch`

---

## Task 1 — detect_figure() unit tests P3-01 through P3-04 RED→GREEN
**Files:** `pipeline/phase3_figures.py`, `tests/test_phase3_figures.py`
**Time:** ~5 min

### Tests:

```python
"""Phase 3 figure detection tests — P3-01 through P3-11."""
import pytest
from pathlib import Path
FIXTURES = Path(__file__).parent / "fixtures"

import pipeline.phase3_figures as p3


# ── P3-01 ─────────────────────────────────────────────────────────────────────
def test_p3_01_no_figure_nearby_returns_false():
    """[UNIT] question with no nearby figure → has_figure=False."""
    question = {"type": "text", "text": "Q1", "x": 50, "y": 200, "width": 400, "height": 20}
    elements = [question]  # no figure elements at all
    result = p3.detect_figure(question, elements, threshold=150)
    assert result["has_figure"] is False
    assert result["figure_path"] is None


# ── P3-02 ─────────────────────────────────────────────────────────────────────
def test_p3_02_figure_within_threshold_returns_true():
    """[UNIT] figure 80px below question → has_figure=True."""
    question = {"type": "text", "text": "Q1", "x": 50, "y": 200, "width": 400, "height": 20}
    figure   = {"type": "figure", "text": "", "x": 50, "y": 280, "width": 300, "height": 200,
                "figure_path": "/tmp/fig1.png"}
    result = p3.detect_figure(question, [question, figure], threshold=150)
    assert result["has_figure"] is True
    assert result["figure_path"] == "/tmp/fig1.png"


# ── P3-03 ─────────────────────────────────────────────────────────────────────
def test_p3_03_figure_at_exact_threshold_is_included():
    """[UNIT] figure at exactly threshold distance → included (<=, not <)."""
    question = {"type": "text", "text": "Q1", "x": 50, "y": 200, "width": 400, "height": 20}
    figure   = {"type": "figure", "text": "", "x": 50, "y": 350, "width": 300, "height": 200,
                "figure_path": "/tmp/fig1.png"}
    # distance = 350 - 200 = 150 = threshold
    result = p3.detect_figure(question, [question, figure], threshold=150)
    assert result["has_figure"] is True


# ── P3-04 ─────────────────────────────────────────────────────────────────────
def test_p3_04_figure_at_threshold_plus_1_is_excluded():
    """[UNIT] figure at threshold+1 → NOT included."""
    question = {"type": "text", "text": "Q1", "x": 50, "y": 200, "width": 400, "height": 20}
    figure   = {"type": "figure", "text": "", "x": 50, "y": 351, "width": 300, "height": 200,
                "figure_path": "/tmp/fig1.png"}
    # distance = 351 - 200 = 151 > threshold=150
    result = p3.detect_figure(question, [question, figure], threshold=150)
    assert result["has_figure"] is False
```

### Minimal implementation:

```python
def detect_figure(
    question_element: dict,
    page_elements: list,
    threshold: int,
    figure_position: str = "below_question",
) -> dict:
    """
    Check whether any figure element on the page is within threshold pixels
    of question_element, in the direction indicated by figure_position.

    Returns dict: {has_figure: bool, figure_path: str|None}
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
        else:  # beside_question or default
            distance = abs(fig_y - q_y)

        if 0 <= distance <= threshold:
            return {"has_figure": True, "figure_path": fig_path}

    return {"has_figure": False, "figure_path": None}
```

Commit: `test(phase3): P3-01 P3-02 P3-03 P3-04 detect_figure RED→GREEN`

---

## Task 2 — Shared figure + figure_position hint: P3-05, P3-06 RED→GREEN
**Files:** `tests/test_phase3_figures.py`
**Time:** ~5 min

### Tests:

```python
# ── P3-05 ─────────────────────────────────────────────────────────────────────
def test_p3_05_one_figure_shared_by_three_questions():
    """[EDGE] figure within 150px of 3 questions — all three linked to same figure."""
    figure = {"type": "figure", "text": "", "x": 50, "y": 300, "width": 300, "height": 200,
              "figure_path": "/tmp/shared_fig.png"}
    q14    = {"type": "text", "text": "14. In which month...", "x": 50, "y": 200, "width": 400, "height": 20}
    q15    = {"type": "text", "text": "15. Which city...",     "x": 50, "y": 250, "width": 400, "height": 20}
    q16    = {"type": "text", "text": "16. Approximately...", "x": 50, "y": 380, "width": 400, "height": 20}
    # q14 distance: 300-200=100  ✓
    # q15 distance: 300-250=50   ✓
    # q16 distance: 380-300=80   ✓  (figure.y=300, q16.y=380 → above_question perspective,
    #                                 but for below_question: 380-300=80 ✓ still within 150)

    elements = [figure, q14, q15, q16]
    for q in [q14, q15, q16]:
        result = p3.detect_figure(q, elements, threshold=150)
        assert result["has_figure"] is True, f"Expected has_figure=True for {q['text']}"
        assert result["figure_path"] == "/tmp/shared_fig.png"


# ── P3-06 ─────────────────────────────────────────────────────────────────────
def test_p3_06_figure_position_above_question():
    """[UNIT] figure_position='above_question' detects figure above, not only below."""
    question = {"type": "text", "text": "Q1", "x": 50, "y": 300, "width": 400, "height": 20}
    figure   = {"type": "figure", "text": "", "x": 50, "y": 200, "width": 300, "height": 80,
                "figure_path": "/tmp/fig_above.png"}
    # figure is 100px ABOVE question
    # below_question check: 200 - 300 = -100 → NOT detected
    result_below = p3.detect_figure(question, [question, figure], threshold=150,
                                    figure_position="below_question")
    assert result_below["has_figure"] is False

    # above_question check: 300 - 200 = 100 ≤ 150 → detected
    result_above = p3.detect_figure(question, [question, figure], threshold=150,
                                    figure_position="above_question")
    assert result_above["has_figure"] is True
```

Note for P3-05: Q16 is at y=380, figure at y=300. For `below_question`, distance = 380-300 = 80 ✓. This works because the figure IS below Q14/Q15 AND Q16 is below the figure — both directions link to the same figure within threshold.

No code changes needed — `detect_figure()` already handles this. Confirm tests are GREEN after writing them.

Commit: `test(phase3): P3-05 P3-06 shared figure + position hint RED→GREEN`

---

## Task 3 — Create fixtures + implement run() + P3-07 through P3-10 RED→GREEN
**Files:** `tests/fixtures/sample_p3_docling.json`, `tests/fixtures/sample_p3_page_map.json`,
           `pipeline/phase3_figures.py`, `tests/test_phase3_figures.py`
**Time:** ~10 min

### Fixture: sample_p3_docling.json

A self-contained docling_output.json with predictable elements:
- Page 10: 5 text elements, 0 figures → 5 JSONs in text/ (P3-07)
- Page 11: 3 text elements near 1 figure → 3 JSONs in figures/ (P3-08)
- Page 381: answer_key page → 0 JSONs (P3-10)

```json
{
  "book_id": "test_book",
  "total_pages": 3,
  "pages": [
    {
      "page_number": 10,
      "markdown_path": "",
      "image_path": null,
      "elements": [
        {"type":"text","text":"1. What is 15% of 200?","x":50,"y":80,"width":400,"height":20},
        {"type":"text","text":"2. A car travels at 60 km/h for 2 hours.","x":50,"y":130,"width":400,"height":20},
        {"type":"text","text":"3. Find the next term: 2, 6, 18, 54...","x":50,"y":180,"width":400,"height":20},
        {"type":"text","text":"4. If x + 7 = 19, what is x?","x":50,"y":230,"width":400,"height":20},
        {"type":"text","text":"5. A rectangle has length 12 cm and width 8 cm.","x":50,"y":280,"width":400,"height":20}
      ]
    },
    {
      "page_number": 11,
      "markdown_path": "",
      "image_path": null,
      "elements": [
        {"type":"figure","text":"","x":50,"y":200,"width":300,"height":200,
         "figure_path":"FIXTURE_FIG_PATH"},
        {"type":"text","text":"6. What does the diagram show?","x":50,"y":80,"width":400,"height":20},
        {"type":"text","text":"7. Which bar is the tallest?","x":50,"y":130,"width":400,"height":20},
        {"type":"text","text":"8. What is the difference between A and B?","x":50,"y":170,"width":400,"height":20}
      ]
    },
    {
      "page_number": 381,
      "markdown_path": "",
      "image_path": null,
      "elements": [
        {"type":"text","text":"Answer Key","x":200,"y":50,"width":200,"height":24},
        {"type":"text","text":"1 C  2 A  3 B  4 D  5 A","x":50,"y":100,"width":500,"height":20}
      ]
    }
  ]
}
```

The `FIXTURE_FIG_PATH` must point to the existing `tests/fixtures/sample_figure.png` — substitute at fixture creation time or in the test setup.

### Fixture: sample_p3_page_map.json

```json
{
  "book_id": "test_book",
  "pages": [
    {"page_number": 10, "subject": "quantitative_reasoning",
     "confidence": 1.0, "is_question_page": true,
     "reasoning": "fixture", "needs_manual_review": false, "briefing_override": true},
    {"page_number": 11, "subject": "quantitative_reasoning",
     "confidence": 1.0, "is_question_page": true,
     "reasoning": "fixture", "needs_manual_review": false, "briefing_override": true},
    {"page_number": 381, "subject": "answer_key",
     "confidence": 1.0, "is_question_page": false,
     "reasoning": "fixture", "needs_manual_review": false, "briefing_override": true}
  ]
}
```

### run() implementation:

```python
import os, json, shutil, uuid, logging
import config as _config

logger = logging.getLogger(__name__)

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
    Returns summary dict.
    """
    if scratch_dir is None:
        scratch_dir = _config.SCRATCH_DIR
    if output_dir is None:
        output_dir = _config.OUTPUT_DIR

    book_scratch = os.path.join(scratch_dir, book_id)

    if docling_json_path is None:
        docling_json_path = os.path.join(book_scratch, "docling_output.json")
    if page_map_path is None:
        page_map_path = os.path.join(book_scratch, "page_map.json")

    with open(docling_json_path, encoding="utf-8") as f:
        docling = json.load(f)
    with open(page_map_path, encoding="utf-8") as f:
        page_map = json.load(f)

    # Load briefing (optional — only for figure_position hint)
    figure_position = "below_question"
    if briefing_path and os.path.exists(briefing_path):
        import pipeline.briefing as briefing_module
        briefing_data = briefing_module.load(briefing_path)
        figure_position = briefing_data.get("figure_position", "below_question")

    # Index page_map by page number
    page_subjects = {p["page_number"]: p for p in page_map["pages"]}

    threshold = int(os.environ.get("FIGURE_PROXIMITY_PX",
                                    getattr(_config, "FIGURE_PROXIMITY_PX", 150)))

    stats = {"text": 0, "figures": 0, "skipped": 0}

    for page_entry in docling["pages"]:
        page_n = page_entry["page_number"]
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

        elements = page_entry.get("elements", [])
        text_elements = [e for e in elements if e.get("type") == "text"]

        for idx, el in enumerate(text_elements):
            fig_result = detect_figure(el, elements, threshold, figure_position)
            source_id = f"{book_id}_p{page_n}_e{idx}"

            record = {
                "source_id": source_id,
                "book_id": book_id,
                "page_number": page_n,
                "subject": subject,
                "content": el.get("text", ""),
                "has_figure": fig_result["has_figure"],
                "figure_path": fig_result["figure_path"],
                "element_bbox": {
                    "x": el["x"], "y": el["y"],
                    "width": el["width"], "height": el["height"],
                },
                "review_status": "pending",
            }

            if fig_result["has_figure"]:
                out_dir = os.path.join(output_dir, subject, "figures")
                os.makedirs(out_dir, exist_ok=True)
                json_path = os.path.join(out_dir, f"{source_id}.json")

                # Copy figure PNG to output
                src_fig = fig_result["figure_path"]
                if src_fig and os.path.exists(src_fig):
                    ext = os.path.splitext(src_fig)[1]
                    dst_fig = os.path.join(out_dir, f"{source_id}_fig{ext}")
                    shutil.copy2(src_fig, dst_fig)
                    record["figure_path"] = dst_fig

                stats["figures"] += 1
            else:
                out_dir = os.path.join(output_dir, subject, "text")
                os.makedirs(os.path.join(output_dir, subject, "text"), exist_ok=True)
                json_path = os.path.join(out_dir, f"{source_id}.json")
                stats["text"] += 1

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(record, f, indent=2, ensure_ascii=False)

    logger.info(f"Phase 3 done: {stats['text']} text, {stats['figures']} figure, {stats['skipped']} skipped")
    return stats
```

### Integration tests P3-07 through P3-10:

```python
@pytest.fixture
def p3_fixture_paths(tmp_path):
    """Set up sample fixture JSON files pointing to tmp_path for output."""
    import json, shutil
    # Read fixture docling JSON and fix the figure_path to real sample_figure.png
    raw = json.loads((FIXTURES / "sample_p3_docling.json").read_text())
    fig_src = str(FIXTURES / "sample_figure.png")
    for page in raw["pages"]:
        for el in page["elements"]:
            if el.get("type") == "figure":
                el["figure_path"] = fig_src
    docling_path = tmp_path / "docling_output.json"
    docling_path.write_text(json.dumps(raw))
    page_map_path = FIXTURES / "sample_p3_page_map.json"
    return docling_path, page_map_path


def test_p3_07_text_only_pages_go_to_text_folder(p3_fixture_paths, tmp_path):
    """[INTEGRATION] text-only page with 5 questions → 5 JSONs in text/, 0 in figures/."""
    docling_path, page_map_path = p3_fixture_paths
    output_dir = tmp_path / "output"

    p3.run(
        book_id="test_book",
        scratch_dir=str(tmp_path),
        output_dir=str(output_dir),
        docling_json_path=str(docling_path),
        page_map_path=str(page_map_path),
    )

    text_files = list((output_dir / "quantitative_reasoning" / "text").glob("*.json"))
    assert len(text_files) == 5, f"Expected 5 text JSONs, got {len(text_files)}"


def test_p3_08_figure_linked_questions_go_to_figures_folder(p3_fixture_paths, tmp_path):
    """[INTEGRATION] 3 text elements near 1 figure → 3 JSONs in figures/ + 3 PNGs."""
    docling_path, page_map_path = p3_fixture_paths
    output_dir = tmp_path / "output"

    p3.run(
        book_id="test_book",
        scratch_dir=str(tmp_path),
        output_dir=str(output_dir),
        docling_json_path=str(docling_path),
        page_map_path=str(page_map_path),
    )

    fig_dir = output_dir / "quantitative_reasoning" / "figures"
    json_files = list(fig_dir.glob("*.json"))
    png_files  = list(fig_dir.glob("*.png"))
    assert len(json_files) == 3, f"Expected 3 figure JSONs, got {len(json_files)}"
    assert len(png_files)  == 3, f"Expected 3 figure PNGs, got {len(png_files)}"


def test_p3_09_output_json_correct_schema(p3_fixture_paths, tmp_path):
    """[CONTRACT] output JSON has correct schema."""
    docling_path, page_map_path = p3_fixture_paths
    output_dir = tmp_path / "output"
    p3.run(book_id="test_book", scratch_dir=str(tmp_path), output_dir=str(output_dir),
           docling_json_path=str(docling_path), page_map_path=str(page_map_path))

    for json_file in (output_dir / "quantitative_reasoning").rglob("*.json"):
        data = json.loads(json_file.read_text())
        assert isinstance(data["has_figure"], bool), "has_figure must be bool"
        if data["has_figure"]:
            assert data["figure_path"] is not None
        else:
            assert data["figure_path"] is None
        assert data["review_status"] == "pending"


def test_p3_10_answer_key_pages_skipped(p3_fixture_paths, tmp_path):
    """[INTEGRATION] answer_key pages (page 381) produce no output files."""
    docling_path, page_map_path = p3_fixture_paths
    output_dir = tmp_path / "output"
    stats = p3.run(book_id="test_book", scratch_dir=str(tmp_path),
                   output_dir=str(output_dir),
                   docling_json_path=str(docling_path),
                   page_map_path=str(page_map_path))

    # No output in answer_key folder
    ak_dir = output_dir / "answer_key"
    assert not ak_dir.exists(), "answer_key should have no output directory"
    # Skipped count should include page 381
    assert stats["skipped"] >= 1
```

Commit: `feat(phase3): run() + fixtures + P3-07 P3-08 P3-09 P3-10 RED→GREEN`

---

## Task 4 — P3-11 threshold from config + P3-05 via run() + full suite + push + merge
**Time:** ~5 min

### Test P3-11:

```python
def test_p3_11_threshold_comes_from_config_not_hardcoded():
    """[UNIT] detect_figure uses the threshold argument; no hardcoded 150 in logic."""
    question = {"type": "text", "text": "Q1", "x": 50, "y": 200, "width": 400, "height": 20}
    figure   = {"type": "figure", "text": "", "x": 50, "y": 400, "width": 300, "height": 200,
                "figure_path": "/tmp/fig.png"}
    # distance = 400-200 = 200

    # With threshold=150: NOT linked
    r150 = p3.detect_figure(question, [question, figure], threshold=150)
    assert r150["has_figure"] is False

    # With threshold=200: linked (distance == threshold, inclusive)
    r200 = p3.detect_figure(question, [question, figure], threshold=200)
    assert r200["has_figure"] is True
```

Then: full suite, push, merge.

---

## Files Changed

| File | Action |
|---|---|
| `pipeline/phase3_figures.py` | Implement |
| `tests/test_phase3_figures.py` | Implement |
| `tests/fixtures/sample_p3_docling.json` | Create |
| `tests/fixtures/sample_p3_page_map.json` | Create |
