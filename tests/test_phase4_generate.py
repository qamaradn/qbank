"""
Phase 4 question generation tests — P4-01 through P4-14.

Fast tests (no API): P4-07 to P4-13
Slow tests (real Gemini API): P4-01 to P4-06, P4-14

Run fast only:  pytest tests/test_phase4_generate.py -v -m "not slow"
Run all:        pytest tests/test_phase4_generate.py -v
"""
import json
import os
import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest

FIXTURES = Path(__file__).parent / "fixtures"

import pipeline.phase4_generate as p4

# ── shared briefing fixture ────────────────────────────────────────────────────
import pipeline.briefing as briefing_module

@pytest.fixture(scope="module")
def briefing_data():
    return briefing_module.load(str(FIXTURES / "sample_briefing.md"))


# ── shared slow fixtures: one real Gemini call per track, shared across tests ──
@pytest.fixture(scope="module")
def generated_text_qs(briefing_data):
    """Real Gemini call — generates 8 QR questions from sample page. Shared."""
    markdown = (FIXTURES / "sample_qr_page.md").read_text(encoding="utf-8")
    return p4.generate_text_questions(markdown, "quantitative_reasoning", briefing_data, n=8)


@pytest.fixture(scope="module")
def generated_figure_qs(briefing_data):
    """Real Gemini call — generates 4 questions from sample_figure.png. Shared."""
    figure_path = str(FIXTURES / "sample_figure.png")
    original_qs = [{"stem": "What shape is shown?"}]
    return p4.generate_figure_questions(
        figure_path, original_qs, "science_reasoning", briefing_data, n=4
    )


@pytest.fixture(scope="module")
def generated_writing_qs(briefing_data):
    """Real Gemini call — generates writing prompts from writing page. Shared."""
    markdown = (FIXTURES / "sample_wr_page.md").read_text(encoding="utf-8")
    return p4.generate_text_questions(markdown, "writing", briefing_data, n=3)


# ── P4-01 ──────────────────────────────────────────────────────────────────────
@pytest.mark.slow
def test_p4_01_text_generation_returns_correct_count(generated_text_qs):
    """[CONTRACT] text generation returns exactly n questions."""
    assert isinstance(generated_text_qs, list)
    assert len(generated_text_qs) == 8


# ── P4-02 ──────────────────────────────────────────────────────────────────────
@pytest.mark.slow
def test_p4_02_correct_answer_is_always_abcd(generated_text_qs):
    """[CONTRACT] correct_answer is always exactly A, B, C, or D."""
    for q in generated_text_qs:
        ca = q["correct_answer"]
        assert ca in ("A", "B", "C", "D"), f"Invalid correct_answer: {ca!r}"
        assert ca == ca.upper()
        assert not ca.startswith("(")


# ── P4-03 ──────────────────────────────────────────────────────────────────────
@pytest.mark.slow
def test_p4_03_confidence_is_float_0_to_1(generated_text_qs):
    """[CONTRACT] confidence is a float between 0.0 and 1.0."""
    for q in generated_text_qs:
        conf = q["confidence"]
        assert isinstance(conf, float), f"confidence is {type(conf)}, not float"
        assert 0.0 <= conf <= 1.0, f"confidence out of range: {conf}"


# ── P4-04 ──────────────────────────────────────────────────────────────────────
@pytest.mark.slow
def test_p4_04_subject_matches_input(generated_text_qs):
    """[CONTRACT] subject matches what was passed in."""
    for q in generated_text_qs:
        assert q["subject"] == "quantitative_reasoning"


# ── P4-05 ──────────────────────────────────────────────────────────────────────
@pytest.mark.slow
def test_p4_05_review_status_is_pending(generated_text_qs):
    """[CONTRACT] review_status is always 'pending' on generation."""
    for q in generated_text_qs:
        assert q["review_status"] == "pending"


# ── P4-06 ──────────────────────────────────────────────────────────────────────
@pytest.mark.slow
def test_p4_06_figure_generation_references_figure(generated_figure_qs):
    """[CONTRACT] figure generation returns questions referencing the figure."""
    assert isinstance(generated_figure_qs, list)
    assert len(generated_figure_qs) == 4
    figure_words = {"diagram", "graph", "table", "figure", "image", "chart", "shows", "shown"}
    for q in generated_figure_qs:
        stem_lower = q["stem"].lower()
        assert any(w in stem_lower for w in figure_words), (
            f"Stem does not reference figure: {q['stem']!r}"
        )


# ── P4-07 ──────────────────────────────────────────────────────────────────────
def test_p4_07_year_level_injected_into_prompt(briefing_data):
    """[UNIT] year_level from briefing injected into generation prompt."""
    markdown = (FIXTURES / "sample_qr_page.md").read_text()
    prompt = p4._build_text_prompt(markdown, "quantitative_reasoning", briefing_data, n=8)
    # sample_briefing.md has target_year: "7-9" (or "7–9")
    assert "7" in prompt and "9" in prompt, "Year level digits not found in prompt"
    assert "Year Level" in prompt or "year level" in prompt.lower()


# ── P4-08 ──────────────────────────────────────────────────────────────────────
def test_p4_08_difficulty_injected_into_prompt(briefing_data):
    """[UNIT] difficulty from briefing injected into generation prompt."""
    markdown = (FIXTURES / "sample_qr_page.md").read_text()
    prompt = p4._build_text_prompt(markdown, "quantitative_reasoning", briefing_data, n=8)
    # sample_briefing.md has difficulty: "medium to hard"
    assert "medium" in prompt.lower() or "hard" in prompt.lower(), (
        "Difficulty not found in prompt"
    )


# ── P4-09 ──────────────────────────────────────────────────────────────────────
def test_p4_09_json_fences_stripped():
    """[EDGE] malformed LLM response with JSON fences handled cleanly."""
    raw = (
        "```json\n"
        '[{"stem":"Q1","option_a":"A","option_b":"B","option_c":"C",'
        '"option_d":"D","correct_answer":"A","explanation":"E","topic":"T",'
        '"difficulty":"medium","confidence":0.9}]\n'
        "```"
    )
    result = p4.parse_llm_response(raw, expected_n=1, subject="quantitative_reasoning")
    assert len(result) == 1
    assert result[0]["correct_answer"] == "A"


# ── P4-10 ──────────────────────────────────────────────────────────────────────
def test_p4_10_fewer_questions_than_requested(caplog):
    """[EDGE] LLM returns fewer questions than requested — logs warning, returns what we got."""
    five_qs = json.dumps([
        {
            "stem": f"Q{i}", "option_a": "A", "option_b": "B",
            "option_c": "C", "option_d": "D",
            "correct_answer": "A", "explanation": "E",
            "topic": "T", "difficulty": "medium", "confidence": 0.8,
        }
        for i in range(5)
    ])
    import logging
    with caplog.at_level(logging.WARNING, logger="pipeline.phase4_generate"):
        result = p4.parse_llm_response(five_qs, expected_n=8, subject="quantitative_reasoning")
    assert len(result) == 5
    assert "expected 8, got 5" in caplog.text


# ── P4-11 ──────────────────────────────────────────────────────────────────────
def test_p4_11_invalid_json_returns_empty_list(caplog):
    """[EDGE] LLM returns plain text — handled gracefully, returns empty list."""
    import logging
    with caplog.at_level(logging.ERROR, logger="pipeline.phase4_generate"):
        result = p4.parse_llm_response(
            "Sorry, I cannot generate questions for this content.",
            expected_n=8,
            subject="quantitative_reasoning",
            book_id="test_book",
            page=23,
        )
    assert result == []
    assert "Invalid JSON" in caplog.text or "invalid" in caplog.text.lower()


# ── P4-12 ──────────────────────────────────────────────────────────────────────
def test_p4_12_api_delay_from_config(tmp_path, monkeypatch, briefing_data):
    """[UNIT] time.sleep called with config API_DELAY_SECONDS, not hardcoded."""
    book_scratch = tmp_path / "scratch" / "test_book"
    book_scratch.mkdir(parents=True)
    pages_dir = book_scratch / "pages"
    pages_dir.mkdir()

    for i in [1, 2, 3]:
        (pages_dir / f"page_{i}.md").write_text("Sample page content", encoding="utf-8")

    page_map = {
        "book_id": "test_book",
        "pages": [
            {
                "page_number": i, "subject": "quantitative_reasoning",
                "is_question_page": True, "confidence": 0.9,
                "briefing_override": False, "needs_manual_review": False,
                "reasoning": "test",
            }
            for i in [1, 2, 3]
        ],
    }
    (book_scratch / "page_map.json").write_text(json.dumps(page_map), encoding="utf-8")

    one_q = json.dumps([{
        "stem": "Q", "option_a": "A", "option_b": "B",
        "option_c": "C", "option_d": "D",
        "correct_answer": "A", "explanation": "E",
        "topic": "T", "difficulty": "medium", "confidence": 0.9,
    }])
    fake_response = MagicMock()
    fake_response.text = one_q
    fake_model = MagicMock()
    fake_model.generate_content.return_value = fake_response

    monkeypatch.setenv("API_DELAY_SECONDS", "3")
    sleep_calls = []
    monkeypatch.setattr(time, "sleep", lambda s: sleep_calls.append(s))
    monkeypatch.setattr(p4, "_get_gemini_model", lambda *a, **kw: fake_model)

    p4.run(
        "test_book",
        output_dir=str(tmp_path / "output"),
        scratch_dir=str(tmp_path / "scratch"),
        briefing_path=str(FIXTURES / "sample_briefing.md"),
    )

    assert sleep_calls, "time.sleep was never called"
    assert all(s == 3 for s in sleep_calls), (
        f"sleep called with {sleep_calls!r}, expected all 3 (from config API_DELAY_SECONDS)"
    )


# ── P4-13 ──────────────────────────────────────────────────────────────────────
def test_p4_13_resumable_skips_already_generated(tmp_path, monkeypatch, caplog):
    """[INTEGRATION] already-generated page skipped by run()."""
    book_scratch = tmp_path / "scratch" / "test_book"
    book_scratch.mkdir(parents=True)
    (book_scratch / "pages").mkdir()
    (book_scratch / "pages" / "page_23.md").write_text("Some QR content", encoding="utf-8")

    page_map = {
        "book_id": "test_book",
        "pages": [
            {
                "page_number": 23, "subject": "quantitative_reasoning",
                "is_question_page": True, "confidence": 0.9,
                "briefing_override": False, "needs_manual_review": False,
                "reasoning": "test",
            }
        ],
    }
    (book_scratch / "page_map.json").write_text(json.dumps(page_map), encoding="utf-8")

    # Pre-create the "already generated" output file
    output_subdir = tmp_path / "output" / "quantitative_reasoning" / "generated"
    output_subdir.mkdir(parents=True)
    (output_subdir / "test_book_p23.json").write_text(
        json.dumps([{"id": "existing"}]), encoding="utf-8"
    )

    fake_model = MagicMock()
    monkeypatch.setattr(p4, "_get_gemini_model", lambda *a, **kw: fake_model)
    monkeypatch.setattr(time, "sleep", lambda s: None)

    import logging
    with caplog.at_level(logging.INFO, logger="pipeline.phase4_generate"):
        p4.run(
            "test_book",
            output_dir=str(tmp_path / "output"),
            scratch_dir=str(tmp_path / "scratch"),
            briefing_path=str(FIXTURES / "sample_briefing.md"),
        )

    fake_model.generate_content.assert_not_called()
    assert "skipping already generated page 23" in caplog.text


# ── P4-14 ──────────────────────────────────────────────────────────────────────
@pytest.mark.slow
def test_p4_14_writing_subject_uses_writing_prompt(generated_writing_qs):
    """[CONTRACT] writing subject questions use writing_prompt, no MCQ fields."""
    assert isinstance(generated_writing_qs, list)
    assert len(generated_writing_qs) > 0
    for q in generated_writing_qs:
        assert q.get("writing_prompt"), "writing_prompt missing or empty"
        assert q.get("option_a") is None
        assert q.get("option_b") is None
        assert q.get("option_c") is None
        assert q.get("option_d") is None
        assert q.get("correct_answer") is None
