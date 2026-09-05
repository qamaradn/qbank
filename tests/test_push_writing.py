"""The writing payload must match the contract Selectly verified on its side.

Built from real rows in writing_prompts rather than invented ones, so both halves are
coding against the same thing. Skips if the table is empty.
"""
import pathlib
import sqlite3
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from pipeline.push_writing_to_selectly import (
    SCHOOL_TYPE_TO_EXAMS, prompt_to_question,
)

DB = pathlib.Path(__file__).resolve().parents[1] / "run_data/db/qbank.db"


def vic_prompts():
    if not DB.exists():
        return []
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in con.execute(
            "SELECT * FROM writing_prompts WHERE form_id LIKE 'vic-drill-wr-%' "
            "ORDER BY form_id, form_position")]
    except sqlite3.OperationalError:
        return []
    finally:
        con.close()


ROWS = vic_prompts()
needs_data = pytest.mark.skipif(not ROWS, reason="no VIC writing prompts loaded")


@needs_data
def test_every_required_field_is_present_on_every_prompt():
    for r in ROWS:
        q = prompt_to_question(r)
        for f in ("qbankId", "questionType", "category", "difficulty", "schoolIds",
                  "stem", "wordLimit"):
            assert q.get(f) not in (None, "", []), f"{f} missing on {r['id'][:8]}"
        assert q["questionType"] == "writing"
        assert q["category"] == "writing"


@needs_data
def test_no_rubric_is_sent():
    """Selectly's import used to require a five-key rubric that nothing read --
    buildGradingPrompt hardcodes its own dimensions. Sending one again would put us
    back to inventing five keys per prompt that no marker consults."""
    assert all("rubric" not in prompt_to_question(r) for r in ROWS)


@needs_data
def test_the_stimulus_is_sent_separately_from_the_task():
    """A prompt is a stimulus the student reads plus a task telling them what to write.
    Concatenating them into stem is what this contract exists to avoid."""
    for r in ROWS:
        q = prompt_to_question(r)
        assert q["stem"] == r["task_instruction"]
        if r["stimulus_content"]:
            assert q["stimulus"] == r["stimulus_content"]
            assert q["stimulus"] not in q["stem"]


@needs_data
def test_prompt_type_is_sent_because_it_drives_the_marking_dimensions():
    """VIC sets one narrative and one persuasive in the same form, so a wrong or absent
    promptType marks half of every paper on dimensions it never asked for."""
    for r in ROWS:
        assert prompt_to_question(r)["promptType"] == r["prompt_type"]
        assert len(r["prompt_type"]) <= 20, "promptType column is varchar(20)"


@needs_data
def test_each_form_is_two_prompts_of_different_sizes_in_one_sitting():
    forms: dict[str, list[dict]] = {}
    for r in ROWS:
        forms.setdefault(r["form_id"], []).append(r)
    for fid, rs in forms.items():
        assert len(rs) == 2, f"{fid} holds {len(rs)} prompts, expected 2"
        rs.sort(key=lambda r: r["form_position"])
        assert [r["form_position"] for r in rs] == [1, 2]
        short, extended = (prompt_to_question(r) for r in rs)
        assert short["wordLimit"] < extended["wordLimit"], fid
        assert (short["timeLimitMinutes"] + extended["timeLimitMinutes"]) == 40, fid


@needs_data
def test_form_fields_ride_along():
    for r in ROWS:
        q = prompt_to_question(r)
        assert q["formId"] == r["form_id"]
        assert q["formPosition"] == r["form_position"]
        assert q["formKind"] == r["form_kind"]


def test_a_school_type_with_no_exam_gets_no_schools():
    """jmss has no exam in Selectly's schools.ts, so those prompts are held back rather
    than sent somewhere they cannot be served."""
    assert SCHOOL_TYPE_TO_EXAMS["jmss"] == []
    assert SCHOOL_TYPE_TO_EXAMS["victorian_selective"] == ["vic-seal"]
