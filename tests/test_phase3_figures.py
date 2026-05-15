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
