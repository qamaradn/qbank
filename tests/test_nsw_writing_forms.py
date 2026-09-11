"""The NSW writing deal, and the VIC pairing Selectly now depends on.

Two different shapes, one table. NSW is one prompt per form because the paper sets one
task; VIC is two because the paper sets two and budgeting across them is the skill. Both
are pinned here because Selectly's timer and its mock rotation read them:

  * a SINGLE-prompt writing form is timed by its own `time_limit_minutes`, so a null there
    silently hands NSW's ten 25-minute prompts the section's 30
  * a TWO-prompt form ignores the per-prompt limit and takes the section fallback, so an
    NSW form of two would quietly become a 30-minute sitting
  * Selectly rotates VIC writing over FORM GROUPS rather than over prompts, precisely so a
    mock cannot serve two short tasks — that only works while every VIC form holds one
    short and one extended, one narrated and one argued

Built from the real rows rather than invented ones, so both halves code against the same
thing. Skips if the table is empty.
"""
import pathlib
import re
import sqlite3
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from tools.assign_nsw_writing_forms import (          # noqa: E402
    PREFIX, TYPE_ORDER, build_forms, check_contract,
)

DB = pathlib.Path(__file__).resolve().parents[1] / "run_data/db/qbank.db"
NARRATED = {"narrative", "diary"}
SELECTLY_FORM_ID = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def prompts(school_type):
    if not DB.exists():
        return []
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in con.execute(
            "SELECT * FROM writing_prompts WHERE school_type = ? "
            "AND review_status != 'rejected' ORDER BY form_id, form_position",
            (school_type,))]
    except sqlite3.OperationalError:
        return []
    finally:
        con.close()


NSW = prompts("nsw_selective")
VIC = prompts("victorian_selective")
needs_nsw = pytest.mark.skipif(not NSW, reason="no NSW writing prompts loaded")
needs_vic = pytest.mark.skipif(not VIC, reason="no VIC writing prompts loaded")


def by_form(rows):
    out = {}
    for r in rows:
        out.setdefault(r["form_id"], {})[r["form_position"]] = r
    return out


# ------------------------------------------------------------------ NSW: forms of one
@needs_nsw
def test_every_nsw_prompt_carries_a_form():
    """A prompt with no form_id is invisible in drill — listStudentForms builds the
    student's set list from form_id IS NOT NULL."""
    assert [r["id"] for r in NSW if not r["form_id"]] == []


@needs_nsw
def test_one_prompt_per_form_at_position_one():
    forms = by_form(NSW)
    assert len(forms) == len(NSW)
    assert all(list(d) == [1] for d in forms.values())
    assert {r["form_kind"] for r in NSW} == {"drill"}


@needs_nsw
def test_form_ids_are_contiguous_and_selectly_can_parse_them():
    ids = sorted({r["form_id"] for r in NSW})
    assert ids == [f"{PREFIX}-{i:03d}" for i in range(1, len(ids) + 1)]
    for f in ids:
        assert SELECTLY_FORM_ID.match(f) and len(f) <= 50
        # formFamily strips the trailing set number; anything else loses the label
        assert re.sub(r"-\d+$", "", f) == PREFIX


@needs_nsw
def test_time_limit_is_never_null():
    """The one field that fails silently: a single-prompt form is timed by its prompt,
    and null falls back to the section's 30 minutes."""
    assert [r["id"] for r in NSW if r["time_limit_minutes"] is None] == []


@needs_nsw
def test_word_range_is_valid_and_prompt_type_is_known():
    for r in NSW:
        assert r["word_count_min"] <= r["word_count_max"]
        # an unknown type falls through to Selectly's ARGUED rubric, so an advice sheet
        # would be marked on quality of argument
        assert r["prompt_type"] in TYPE_ORDER


@needs_nsw
def test_the_contract_check_passes_on_the_real_pool():
    assert check_contract(NSW) == []


@needs_nsw
def test_the_deal_is_deterministic_and_spreads_the_text_types():
    first, second = build_forms(NSW), build_forms(NSW)
    assert [r["id"] for r in first] == [r["id"] for r in second]
    # the first eight sets are one of each type, so sitting sets 1-3 is three kinds of
    # writing rather than three advice sheets
    assert len({r["prompt_type"] for r in first[:len(TYPE_ORDER)]}) == len(TYPE_ORDER)


@needs_nsw
def test_the_contract_check_catches_a_null_time_limit():
    broken = dict(NSW[0], time_limit_minutes=None)
    assert any("time_limit_minutes" in p for p in check_contract([broken]))


# --------------------------------------------------- VIC: pairs, which Selectly relies on
@needs_vic
def test_every_vic_form_holds_exactly_two_prompts():
    forms = by_form(VIC)
    assert all(sorted(d) == [1, 2] for d in forms.values())


@needs_vic
def test_vic_position_one_is_short_and_position_two_extended():
    """Selectly rotates VIC writing over form groups on the strength of this. Independent
    rotation would serve two short tasks."""
    for form, d in by_form(VIC).items():
        assert d[1]["word_count_max"] <= 200 < d[2]["word_count_min"], form
        assert d[1]["time_limit_minutes"] == 15 and d[2]["time_limit_minutes"] == 25, form


@needs_vic
def test_every_vic_form_pairs_a_narrated_task_with_an_argued_one():
    for form, d in by_form(VIC).items():
        assert (d[1]["prompt_type"] in NARRATED) != (d[2]["prompt_type"] in NARRATED), form
