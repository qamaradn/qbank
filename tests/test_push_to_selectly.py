

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
    assert loaded == {"a": {"h": m.LEGACY_HASH, "f": None},
                      "b": {"h": m.LEGACY_HASH, "f": None}}
    assert m.LEGACY_HASH != m.payload_hash({"qbankId": "a"})


def test_tracking_round_trips_hashes(tmp_path, monkeypatch):
    import pipeline.push_to_selectly as m
    f = tmp_path / "pushed.json"
    monkeypatch.setattr(m, "TRACKING_FILE", f)
    m.save_tracking({"a": {"h": "h1", "f": "form-1"}, "b": {"h": "h2", "f": None}})
    assert m.load_tracking() == {"a": {"h": "h1", "f": "form-1"},
                                 "b": {"h": "h2", "f": None}}


def test_deactivate_is_a_noop_for_an_empty_list():
    from pipeline.push_to_selectly import deactivate
    assert deactivate("http://x", "s", [], dry_run=False) == 0


def test_deactivate_sends_the_shape_questions_fix_expects(monkeypatch):
    """The two Selectly endpoints do not share a contract: import takes a bearer token
    and a `questions` array; questions-fix takes an x-import-secret header and a `fixes`
    array addressed per row. Getting this wrong fails silently as a 403."""
    import json as _json
    import pipeline.push_to_selectly as m
    seen = {}

    class _Resp:
        def read(self): return _json.dumps({"updated": 2}).encode()
        def __enter__(self): return self
        def __exit__(self, *a): return False

    def fake_urlopen(req, timeout=None):
        seen["url"] = req.full_url
        seen["headers"] = {k.lower(): v for k, v in req.headers.items()}
        seen["body"] = _json.loads(req.data)
        return _Resp()

    monkeypatch.setattr(m.urllib.request, "urlopen", fake_urlopen)
    assert m.deactivate("http://x", "sec", ["q1", "q2"], dry_run=False) == 2
    assert seen["url"].endswith("/api/admin/questions-fix")
    assert seen["headers"].get("x-import-secret") == "sec"
    assert "authorization" not in seen["headers"]
    assert seen["body"] == {"fixes": [{"qbankId": "q1", "active": False},
                                      {"qbankId": "q2", "active": False}]}


def test_every_replacement_book_is_routed():
    """A replacement question that routes nowhere is worse than no replacement: the form
    is dealt as full, the pusher silently drops it, and the paper ships a question short.
    Caught in the first NSW review round, where ma_nsw_replacements was unregistered."""
    from pipeline.push_to_selectly import school_ids_for
    for book in ("ma_nsw_replacements",):
        row = {"subject": "mathematics", "source_book": book}
        assert school_ids_for(row), f"{book} routes to no exam"


def test_a_rejected_question_lifted_from_its_form_is_still_withdrawn(tmp_path, monkeypatch):
    """The row that most needs switching off is the one that stops belonging to a form.

    A question rejected at review is lifted out, so its form_id becomes NULL. Scoping the
    withdrawal pass by CURRENT form made it invisible — it would have kept being served
    to the reviewer indefinitely. Tracking records the form each question was sent as
    part of, so scoping works on where it WAS.
    """
    import json as _json
    import pipeline.push_to_selectly as m
    f = tmp_path / "pushed.json"
    f.write_text(_json.dumps({"pushed": {
        "kept": {"h": "h1", "f": "nsw-drill-math-001"},
        "rejected-and-lifted": {"h": "h2", "f": "nsw-drill-math-001"},
        "other-form": {"h": "h3", "f": "vic-drill-mq-050"},
    }}))
    monkeypatch.setattr(m, "TRACKING_FILE", f)
    tracked = m.load_tracking()
    sendable = {"kept"}
    want = {"nsw-drill-math-001"}
    stale = sorted(q for q, v in tracked.items() if v.get("f") in want and q not in sendable)
    assert stale == ["rejected-and-lifted"], stale


def test_older_tracking_formats_load_forward(tmp_path, monkeypatch):
    import json as _json
    import pipeline.push_to_selectly as m
    f = tmp_path / "pushed.json"
    monkeypatch.setattr(m, "TRACKING_FILE", f)
    f.write_text(_json.dumps({"pushed_ids": ["a"]}))
    assert m.load_tracking() == {"a": {"h": m.LEGACY_HASH, "f": None}}
    f.write_text(_json.dumps({"pushed": {"b": "hashonly"}}))
    assert m.load_tracking() == {"b": {"h": "hashonly", "f": None}}


def test_tracking_refuses_a_different_database(tmp_path, monkeypatch):
    """Two Selectly databases exist and look alike — the local Supabase carries qbank_id
    and form_id too. Pushing to the wrong one would send the questions there, mark them
    all as sent, and leave production silently missing every repair.
    """
    import json as _json
    import pytest as _pytest
    import pipeline.push_to_selectly as m
    f = tmp_path / "pushed.json"
    f.write_text(_json.dumps({"target": "https://selectly-fawn.vercel.app",
                              "pushed": {"a": {"h": "h1", "f": None}}}))
    monkeypatch.setattr(m, "TRACKING_FILE", f)
    m.load_tracking()
    with _pytest.raises(SystemExit):
        m.check_target("http://127.0.0.1:54321")
    m.check_target("https://selectly-fawn.vercel.app/")     # trailing slash is the same


def test_tracking_without_a_target_does_not_block(tmp_path, monkeypatch):
    """Files written before the target was recorded must keep working."""
    import json as _json
    import pipeline.push_to_selectly as m
    f = tmp_path / "pushed.json"
    f.write_text(_json.dumps({"pushed": {"a": {"h": "h1", "f": None}}}))
    monkeypatch.setattr(m, "TRACKING_FILE", f)
    m.load_tracking()
    m.check_target("http://anywhere")


def test_clear_flags_uses_adjudicated_ids_not_a_region(tmp_path, monkeypatch):
    """CSVs are not region-pure — the first one carried four NSW flags and two VIC ones,
    because both reviewers export from the same admin list. Clearing "all VIC" after an
    NSW round would have deleted two flags nobody had adjudicated."""
    import json as _json
    import pipeline.push_to_selectly as m
    rf = tmp_path / "round_x.json"
    rf.write_text(_json.dumps([
        {"qbank_id": "a", "form_id": "nsw-drill-math-001", "verdict": "repair"},
        {"qbank_id": "b", "form_id": "vic-drill-mq-001", "verdict": "keep"},
    ]))
    seen = {}

    class _Resp:
        def read(self): return _json.dumps({"deleted": 2}).encode()
        def __enter__(self): return self
        def __exit__(self, *a): return False

    def fake(req, timeout=None):
        seen["url"] = req.full_url
        seen["headers"] = {k.lower(): v for k, v in req.headers.items()}
        seen["body"] = _json.loads(req.data)
        return _Resp()

    monkeypatch.setattr(m.urllib.request, "urlopen", fake)
    m.clear_flags("http://x", "sec", rf, dry_run=False)
    assert seen["url"].endswith("/api/admin/flags-clear")
    assert seen["headers"].get("x-import-secret") == "sec"
    # both ids, including the one whose verdict was `keep` — it was still adjudicated
    assert seen["body"] == {"qbankIds": ["a", "b"]}


def test_clear_flags_survives_the_endpoint_not_existing(tmp_path, monkeypatch, caplog):
    """Until Selectly ships the route, a push must still succeed and say what happened."""
    import json as _json
    import urllib.error
    import pipeline.push_to_selectly as m
    rf = tmp_path / "round_x.json"
    rf.write_text(_json.dumps([{"qbank_id": "a"}]))

    def fake(req, timeout=None):
        raise urllib.error.HTTPError(req.full_url, 404, "Not Found", {}, None)

    monkeypatch.setattr(m.urllib.request, "urlopen", fake)
    m.clear_flags("http://x", "sec", rf, dry_run=False)   # must not raise
