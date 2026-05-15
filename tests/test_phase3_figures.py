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
