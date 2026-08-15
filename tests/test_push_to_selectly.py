

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
        ("logical_reasoning", ["nsw-shspt"]),
    ],
)
def test_category_routes_to_one_exam(subject, expected):
    assert school_ids_for(_row(subject)) == expected


@pytest.mark.parametrize(
    "book,expected",
    [
        ("year7_nsw_maths", ["nsw-shspt"]),
        ("ma_nsw_selective", ["nsw-shspt"]),
        ("year9_maths", ["vic-seal"]),
        ("ma_vic_stats", ["vic-seal"]),
    ],
)
def test_maths_routes_on_source_book(book, expected):
    """`mathematics` is not one exam's category. It was routed wholesale to nsw-shspt,
    which sent 642 Year 9 VIC questions into a paper sat in Year 6 and left vic-seal's
    own maths component empty."""
    assert school_ids_for(_row("mathematics", book)) == expected


def test_unknown_maths_book_goes_nowhere_rather_than_to_the_wrong_exam():
    """Reading over-serves an unknown book so it gets noticed. Maths must not: the two
    banks are two school years apart, so a wrong guess is worse than no guess."""
    assert school_ids_for(_row("mathematics", "ma_qld_new")) == []


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


# --------------------------------------------------------------- push tracking
# The tracking file used to hold ids only, which was right while the import was
# insert-only. Now that it upserts on qbankId, a repaired question must go again --
# the whole review loop depends on it.

def test_payload_hash_changes_when_the_key_is_repaired():
    from pipeline.push_to_selectly import payload_hash
    q = {"qbankId": "x", "correctAnswer": "A", "options": {"A": "1", "B": "2"}}
    before = payload_hash(q)
    q["correctAnswer"] = "B"
    assert payload_hash(q) != before


def test_payload_hash_is_stable_for_identical_content():
    from pipeline.push_to_selectly import payload_hash
    a = {"qbankId": "x", "stem": "s", "options": {"A": "1", "B": "2"}}
    b = {"options": {"B": "2", "A": "1"}, "stem": "s", "qbankId": "x"}
    assert payload_hash(a) == payload_hash(b), "key order must not change the hash"


def test_legacy_id_only_tracking_loads_as_unknown(tmp_path, monkeypatch):
    """A file from the old format has no record of what was sent. Treating those rows as
    'unchanged' would strand every repair made before the upgrade, so they re-send once."""
    import json as _json
    import pipeline.push_to_selectly as m
    f = tmp_path / "pushed.json"
    f.write_text(_json.dumps({"pushed_ids": ["a", "b"]}))
    monkeypatch.setattr(m, "TRACKING_FILE", f)
    loaded = m.load_tracking()
    assert loaded == {"a": m.LEGACY_HASH, "b": m.LEGACY_HASH}
    assert m.LEGACY_HASH != m.payload_hash({"qbankId": "a"})


def test_tracking_round_trips_hashes(tmp_path, monkeypatch):
    import pipeline.push_to_selectly as m
    f = tmp_path / "pushed.json"
    monkeypatch.setattr(m, "TRACKING_FILE", f)
    m.save_tracking({"a": "h1", "b": "h2"})
    assert m.load_tracking() == {"a": "h1", "b": "h2"}


def test_deactivate_is_a_noop_for_an_empty_list():
    from pipeline.push_to_selectly import deactivate
    assert deactivate("http://x", "s", [], dry_run=False) == 0
