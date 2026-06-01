"""Phase 3 — question generation tests (mocked Gemini)."""
import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from pipeline.phase3_generate import generate_page, run_from_png_dir, _build_question, _strip_fences


SAMPLE_RAW = {
    "stem": "A train travels 240 km in 3 hours. What is its average speed?",
    "option_a": "60 km/h",
    "option_b": "80 km/h",
    "option_c": "90 km/h",
    "option_d": "120 km/h",
    "correct_answer": "B",
    "explanation": "Speed = distance / time = 240 / 3 = 80 km/h.",
    "topic": "Measurement and Geometry",
    "difficulty": "medium",
    "confidence": 0.95,
    "source_page_description": "A page showing speed and distance problems.",
}


def test_build_question_valid():
    q = _build_question(SAMPLE_RAW, "quantitative_reasoning", "testbook", 10, None)
    assert q is not None
    assert q["subject"] == "quantitative_reasoning"
    assert q["correct_answer"] == "B"
    assert q["difficulty"] == "medium"
    assert q["confidence"] == 0.95
    assert q["source_book"] == "testbook"
    assert q["source_page"] == 10
    assert q["source_page_description"] == "A page showing speed and distance problems."
    assert q["passage"] is None
    assert q["review_status"] == "pending"
    assert "id" in q


def test_build_question_invalid_correct_answer():
    raw = dict(SAMPLE_RAW, correct_answer="E")
    q = _build_question(raw, "quantitative_reasoning", "testbook", 10, None)
    assert q["correct_answer"] == "A"  # defaults to A


def test_build_question_invalid_difficulty():
    raw = dict(SAMPLE_RAW, difficulty="easy")
    q = _build_question(raw, "quantitative_reasoning", "testbook", 10, None)
    assert q["difficulty"] == "medium"  # defaults to medium


def test_build_question_empty_stem():
    raw = dict(SAMPLE_RAW, stem="")
    q = _build_question(raw, "quantitative_reasoning", "testbook", 10, None)
    assert q is None


def test_strip_fences_clean():
    assert _strip_fences('[{"a":1}]') == '[{"a":1}]'


def test_strip_fences_with_json_fence():
    raw = '```json\n[{"a":1}]\n```'
    assert _strip_fences(raw) == '[{"a":1}]'


def test_strip_fences_with_plain_fence():
    raw = '```\n[{"a":1}]\n```'
    result = _strip_fences(raw)
    assert '[{"a":1}]' in result


def test_generate_page_calls_gemini_and_writes_json(tmp_path):
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = json.dumps([SAMPLE_RAW] * 10)
    mock_model.generate_content.return_value = mock_response

    # Create a fake PNG
    from PIL import Image
    img_path = tmp_path / "test.png"
    Image.new("RGB", (100, 100), color="white").save(str(img_path))

    output_dir = str(tmp_path / "output")
    briefing_data = {"target_year": "9-10", "difficulty": "medium"}

    questions = generate_page(
        page_n=5,
        image_path=str(img_path),
        subject="quantitative_reasoning",
        book_id="testbook",
        output_dir=output_dir,
        briefing_data=briefing_data,
        model=mock_model,
    )

    assert len(questions) == 10
    out_file = Path(output_dir) / "quantitative_reasoning" / "generated" / "testbook_p5.json"
    assert out_file.exists()
    saved = json.loads(out_file.read_text())
    assert len(saved) == 10
    assert saved[0]["review_status"] == "pending"


def test_run_from_png_dir_generates_per_png(tmp_path):
    """PNG-dir mode: one output JSON per PNG, 10 questions each."""
    from PIL import Image

    png_dir = tmp_path / "samples"
    png_dir.mkdir()
    for i in range(3):
        Image.new("RGB", (100, 100), color="white").save(str(png_dir / f"sample_{i}.png"))

    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = json.dumps({"passage": None, "questions": [SAMPLE_RAW] * 10})
    mock_model.generate_content.return_value = mock_response

    output_dir = str(tmp_path / "output")

    with patch("pipeline.phase3_generate._get_gemini_model", return_value=mock_model):
        stats = run_from_png_dir(
            book_id="vr_test",
            png_dir=str(png_dir),
            subject="verbal_reasoning",
            output_dir=output_dir,
            target_year="9-10",
            difficulty="medium",
        )

    assert stats["generated"] == 30
    assert stats["skipped"] == 0
    assert stats["failed"] == 0

    out_dir = Path(output_dir) / "verbal_reasoning" / "generated"
    assert (out_dir / "vr_test_p001.json").exists()
    assert (out_dir / "vr_test_p002.json").exists()
    assert (out_dir / "vr_test_p003.json").exists()


def test_run_from_png_dir_resumable(tmp_path):
    """PNG-dir mode: skips PNGs whose output JSON already exists."""
    from PIL import Image

    png_dir = tmp_path / "samples"
    png_dir.mkdir()
    for i in range(2):
        Image.new("RGB", (100, 100), color="white").save(str(png_dir / f"sample_{i}.png"))

    # Pre-create first output file
    out_dir = tmp_path / "output" / "verbal_reasoning" / "generated"
    out_dir.mkdir(parents=True)
    (out_dir / "vr_resume_p001.json").write_text("[]")

    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = json.dumps({"passage": None, "questions": [SAMPLE_RAW] * 10})
    mock_model.generate_content.return_value = mock_response

    with patch("pipeline.phase3_generate._get_gemini_model", return_value=mock_model):
        stats = run_from_png_dir(
            book_id="vr_resume",
            png_dir=str(png_dir),
            subject="verbal_reasoning",
            output_dir=str(tmp_path / "output"),
        )

    assert stats["skipped"] == 1
    assert stats["generated"] == 10  # only second PNG processed


def test_run_from_png_dir_no_pngs_raises(tmp_path):
    """PNG-dir mode: raises FileNotFoundError if dir has no PNGs."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    with pytest.raises(FileNotFoundError, match="No PNG files"):
        run_from_png_dir(
            book_id="vr_test",
            png_dir=str(empty_dir),
            subject="verbal_reasoning",
            output_dir=str(tmp_path / "output"),
        )
