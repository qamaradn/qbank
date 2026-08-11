

# --- schoolIds routing, banned-type exclusion, form fields -------------------------
# Added when the clean-reload plan was agreed: every question had been going to BOTH
# exams, which served NSW students VIC verbal reasoning and sent `mathematics` to an
# exam whose config has no mathematics section.

import pytest

from pipeline.push_to_selectly import CATEGORY_SCHOOLS, school_ids_for


def _row(subject, book="b", **kw):
    return {"subject": subject, "source_book": book, **kw}


@pytest.mark.parametrize(
    "subject,expected",
    [
        ("verbal_reasoning", ["vic-seal"]),
        ("quantitative_reasoning", ["vic-seal"]),
        ("mathematics", ["nsw-shspt"]),
        ("logical_reasoning", ["nsw-shspt"]),
    ],
)
def test_category_routes_to_one_exam(subject, expected):
    assert school_ids_for(_row(subject)) == expected


def test_science_reasoning_goes_nowhere():
    """Parked for JMSS. No section in either exam maps to it, so sending it would import
    956 rows that are never served."""
    assert school_ids_for(_row("science_reasoning")) == []


@pytest.mark.parametrize(
    "book,expected",
    [
        ("rc_nsw_cloze", ["nsw-shspt"]),
        ("rc_nsw_single", ["nsw-shspt"]),
        ("rc_vic_narrative", ["vic-seal"]),
        ("rc_vic_poetry", ["vic-seal"]),
        ("act_test7", ["vic-seal", "nsw-shspt"]),
    ],
)
def test_reading_routes_on_source_book(book, expected):
    assert school_ids_for(_row("reading_comprehension", book)) == expected


def test_unknown_reading_book_reaches_both_rather_than_nowhere():
    """A new book should be over-served and noticed, not silently dropped."""
    assert school_ids_for(_row("reading_comprehension", "rc_qld_new")) == [
        "vic-seal",
        "nsw-shspt",
    ]


def test_every_routed_category_is_one_selectly_knows():
    valid = {"vic-seal", "nsw-shspt"}
    for subject, schools in CATEGORY_SCHOOLS.items():
        assert set(schools) <= valid, subject
