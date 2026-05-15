"""
Phase 3 figure detection tests — P3-01 through P3-11.
All tests are fast (no Docling, no API).
Run: pytest tests/test_phase3_figures.py -v
"""
import json
import pytest
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"

import pipeline.phase3_figures as p3


# ── P3-01 ─────────────────────────────────────────────────────────────────────
def test_p3_01_no_figure_nearby_returns_false():
    """[UNIT] question with no nearby figure → has_figure=False, figure_path=None."""
    question = {"type": "text", "text": "Q1", "x": 50, "y": 200, "width": 400, "height": 20}
    elements = [question]  # no figure elements
    result = p3.detect_figure(question, elements, threshold=150)
    assert result["has_figure"] is False
    assert result["figure_path"] is None


# ── P3-02 ─────────────────────────────────────────────────────────────────────
def test_p3_02_figure_within_threshold_returns_true():
    """[UNIT] figure 80px below question → has_figure=True, figure_path set."""
    question = {"type": "text", "text": "Q1", "x": 50, "y": 200, "width": 400, "height": 20}
    figure   = {"type": "figure", "text": "", "x": 50, "y": 280, "width": 300, "height": 200,
                "figure_path": "/tmp/fig1.png"}
    # distance = 280 - 200 = 80 ≤ 150
    result = p3.detect_figure(question, [question, figure], threshold=150)
    assert result["has_figure"] is True
    assert result["figure_path"] == "/tmp/fig1.png"


# ── P3-03 ─────────────────────────────────────────────────────────────────────
def test_p3_03_figure_at_exact_threshold_included():
    """[UNIT] figure at exactly threshold distance → included (distance <= threshold)."""
    question = {"type": "text", "text": "Q1", "x": 50, "y": 200, "width": 400, "height": 20}
    figure   = {"type": "figure", "text": "", "x": 50, "y": 350, "width": 300, "height": 200,
                "figure_path": "/tmp/fig1.png"}
    # distance = 350 - 200 = 150 == threshold
    result = p3.detect_figure(question, [question, figure], threshold=150)
    assert result["has_figure"] is True


# ── P3-04 ─────────────────────────────────────────────────────────────────────
def test_p3_04_figure_at_threshold_plus_1_excluded():
    """[UNIT] figure at threshold+1 → NOT included."""
    question = {"type": "text", "text": "Q1", "x": 50, "y": 200, "width": 400, "height": 20}
    figure   = {"type": "figure", "text": "", "x": 50, "y": 351, "width": 300, "height": 200,
                "figure_path": "/tmp/fig1.png"}
    # distance = 351 - 200 = 151 > threshold=150
    result = p3.detect_figure(question, [question, figure], threshold=150)
    assert result["has_figure"] is False


# ── P3-05 ─────────────────────────────────────────────────────────────────────
def test_p3_05_one_figure_shared_by_three_questions():
    """[EDGE] figure within 150px of 3 questions — all three linked to same figure."""
    figure = {"type": "figure", "text": "", "x": 50, "y": 300, "width": 300, "height": 200,
              "figure_path": "/tmp/shared_fig.png"}
    q14    = {"type": "text", "text": "14. In which month...", "x": 50, "y": 200, "width": 400, "height": 20}
    q15    = {"type": "text", "text": "15. Which city...",     "x": 50, "y": 250, "width": 400, "height": 20}
    q16    = {"type": "text", "text": "16. Approximately...", "x": 50, "y": 380, "width": 400, "height": 20}
    # q14: figure.y - q.y = 300-200=100  ✓ (below, within 150)
    # q15: figure.y - q.y = 300-250=50   ✓ (below, within 150)
    # q16: figure.y - q.y = 300-380=-80  ✗ for below_question
    #       q.y - figure.y = 380-300=80  ✓ but that's above_question

    elements = [figure, q14, q15, q16]

    # q14 and q15 are below_question (figure is below them)
    for q in [q14, q15]:
        result = p3.detect_figure(q, elements, threshold=150, figure_position="below_question")
        assert result["has_figure"] is True, f"Expected has_figure=True for {q['text'][:20]}"
        assert result["figure_path"] == "/tmp/shared_fig.png"

    # q16 is ABOVE the figure — check with above_question hint
    result_q16 = p3.detect_figure(q16, elements, threshold=150, figure_position="above_question")
    assert result_q16["has_figure"] is True, "q16 above figure should be detected with above_question hint"
    assert result_q16["figure_path"] == "/tmp/shared_fig.png"

    # All three linked to same path — figure PNG exists only once conceptually
    assert result_q16["figure_path"] == "/tmp/shared_fig.png"


# ── P3-06 ─────────────────────────────────────────────────────────────────────
def test_p3_06_figure_position_above_question():
    """[UNIT] figure_position='above_question' detects figure ABOVE, not below."""
    question = {"type": "text", "text": "Q1", "x": 50, "y": 300, "width": 400, "height": 20}
    figure   = {"type": "figure", "text": "", "x": 50, "y": 200, "width": 300, "height": 80,
                "figure_path": "/tmp/fig_above.png"}
    # figure is 100px ABOVE question (figure.y=200 < question.y=300)

    # below_question: distance = 200 - 300 = -100 → NOT detected
    result_below = p3.detect_figure(question, [question, figure], threshold=150,
                                    figure_position="below_question")
    assert result_below["has_figure"] is False, "below_question should NOT detect figure above"

    # above_question: distance = 300 - 200 = 100 ≤ 150 → detected
    result_above = p3.detect_figure(question, [question, figure], threshold=150,
                                    figure_position="above_question")
    assert result_above["has_figure"] is True, "above_question SHOULD detect figure above"
    assert result_above["figure_path"] == "/tmp/fig_above.png"


# ── Integration test fixture ───────────────────────────────────────────────────

@pytest.fixture
def p3_fixture_paths(tmp_path):
    """Load fixture JSON files, replace SAMPLE_FIGURE_PLACEHOLDER with real PNG path."""
    import json as _json
    raw = _json.loads((FIXTURES / "sample_p3_docling.json").read_text())
    fig_src = str(FIXTURES / "sample_figure.png")
    for page in raw["pages"]:
        for el in page["elements"]:
            if el.get("type") == "figure":
                el["figure_path"] = fig_src
    docling_path = tmp_path / "docling_output.json"
    docling_path.write_text(_json.dumps(raw))
    page_map_path = FIXTURES / "sample_p3_page_map.json"
    return docling_path, page_map_path


# ── P3-07 ─────────────────────────────────────────────────────────────────────
def test_p3_07_text_only_pages_go_to_text_folder(p3_fixture_paths, tmp_path):
    """[INTEGRATION] page with 5 text elements and no figures → 5 JSONs in text/, 0 in figures/."""
    docling_path, page_map_path = p3_fixture_paths
    output_dir = tmp_path / "output"

    p3.run(
        book_id="test_book",
        scratch_dir=str(tmp_path),
        output_dir=str(output_dir),
        docling_json_path=str(docling_path),
        page_map_path=str(page_map_path),
    )

    text_dir    = output_dir / "quantitative_reasoning" / "text"
    text_files  = list(text_dir.glob("*.json")) if text_dir.exists() else []
    fig_dir     = output_dir / "quantitative_reasoning" / "figures"

    # Page 10 has 5 text elements, page 11 has 3 text elements near figure
    # text_dir gets only the page-10 elements (no figure) = 5 files
    page10_files = [f for f in text_files if "_p10_" in f.name]
    assert len(page10_files) == 5, f"Expected 5 text JSONs for page 10, got {len(page10_files)}"


# ── P3-08 ─────────────────────────────────────────────────────────────────────
def test_p3_08_figure_linked_questions_go_to_figures_folder(p3_fixture_paths, tmp_path):
    """[INTEGRATION] 3 text elements near 1 figure → 3 JSONs + 3 PNGs in figures/."""
    docling_path, page_map_path = p3_fixture_paths
    output_dir = tmp_path / "output"

    p3.run(
        book_id="test_book",
        scratch_dir=str(tmp_path),
        output_dir=str(output_dir),
        docling_json_path=str(docling_path),
        page_map_path=str(page_map_path),
    )

    fig_dir   = output_dir / "quantitative_reasoning" / "figures"
    json_files = list(fig_dir.glob("*.json")) if fig_dir.exists() else []
    png_files  = list(fig_dir.glob("*.png"))  if fig_dir.exists() else []
    assert len(json_files) == 3, f"Expected 3 figure JSONs, got {len(json_files)}"
    assert len(png_files)  == 3, f"Expected 3 figure PNGs, got {len(png_files)}"


# ── P3-09 ─────────────────────────────────────────────────────────────────────
def test_p3_09_output_json_correct_schema(p3_fixture_paths, tmp_path):
    """[CONTRACT] every output JSON has correct schema."""
    docling_path, page_map_path = p3_fixture_paths
    output_dir = tmp_path / "output"
    p3.run(book_id="test_book", scratch_dir=str(tmp_path), output_dir=str(output_dir),
           docling_json_path=str(docling_path), page_map_path=str(page_map_path))

    all_json = list((output_dir / "quantitative_reasoning").rglob("*.json"))
    assert len(all_json) > 0, "No output JSON files found"

    for jf in all_json:
        data = json.loads(jf.read_text())
        assert isinstance(data["has_figure"], bool), f"{jf.name}: has_figure must be bool"
        if data["has_figure"]:
            assert data["figure_path"] is not None, f"{jf.name}: figure_path must be set"
            assert isinstance(data["figure_path"], str)
        else:
            assert data["figure_path"] is None, f"{jf.name}: figure_path must be None"
        assert data["review_status"] == "pending", f"{jf.name}: review_status must be 'pending'"


# ── P3-10 ─────────────────────────────────────────────────────────────────────
def test_p3_10_answer_key_pages_produce_no_output(p3_fixture_paths, tmp_path):
    """[INTEGRATION] answer_key page 381 → no output files, skipped count >= 1."""
    docling_path, page_map_path = p3_fixture_paths
    output_dir = tmp_path / "output"
    stats = p3.run(book_id="test_book", scratch_dir=str(tmp_path), output_dir=str(output_dir),
                   docling_json_path=str(docling_path), page_map_path=str(page_map_path))

    ak_dir = output_dir / "answer_key"
    assert not ak_dir.exists(), "answer_key subject should produce no output directory"
    assert stats["skipped"] >= 1, "Expected at least 1 skipped page (answer_key)"


# ── P3-11 ─────────────────────────────────────────────────────────────────────
def test_p3_11_threshold_from_argument_not_hardcoded():
    """[UNIT] detect_figure uses the threshold argument — different thresholds produce different results."""
    question = {"type": "text", "text": "Q1", "x": 50, "y": 200, "width": 400, "height": 20}
    figure   = {"type": "figure", "text": "", "x": 50, "y": 400, "width": 300, "height": 200,
                "figure_path": "/tmp/fig.png"}
    # distance = 400 - 200 = 200

    # threshold=150: NOT linked (200 > 150)
    r150 = p3.detect_figure(question, [question, figure], threshold=150)
    assert r150["has_figure"] is False, "threshold=150 should NOT link (distance=200)"

    # threshold=200: linked (distance == threshold, inclusive)
    r200 = p3.detect_figure(question, [question, figure], threshold=200)
    assert r200["has_figure"] is True, "threshold=200 SHOULD link (distance=200, inclusive)"

    # threshold=199: NOT linked (200 > 199)
    r199 = p3.detect_figure(question, [question, figure], threshold=199)
    assert r199["has_figure"] is False, "threshold=199 should NOT link (distance=200 > 199)"
