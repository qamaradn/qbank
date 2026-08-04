"""Backfill matching — the part that could silently point a Selectly row at the wrong question.

A mis-pair here is worse than no pair: deactivating or correcting by qbank_id would then
hit an unrelated question that students are being served. Every ambiguous case must be
reported and left alone rather than guessed at.
"""
from pipeline.backfill_qbank_ids import match


def local(qid, stem, a="aa", b="bb", c="cc", d="dd", passage=None):
    return {"id": qid, "stem": stem, "passage": passage,
            "option_a": a, "option_b": b, "option_c": c, "option_d": d}


def remote(sid, stem, opts=None, qbank_id=None):
    return {"id": sid, "stem": stem, "qbankId": qbank_id,
            "options": opts or {"A": "aa", "B": "bb", "C": "cc", "D": "dd"}}


def test_matches_on_stem_and_returns_both_ids():
    pairs, unmatched, ambiguous = match([local("q1", "What is 2+2?")],
                                        [remote("s1", "What is 2+2?")])
    assert pairs == [("s1", "q1", "What is 2+2?")]
    assert (unmatched, ambiguous) == ([], [])


def test_skips_rows_that_already_carry_a_handle():
    """Re-running the backfill must be a no-op, not a rewrite."""
    pairs, unmatched, ambiguous = match([local("q1", "What is 2+2?")],
                                        [remote("s1", "What is 2+2?", qbank_id="q1")])
    assert (pairs, unmatched, ambiguous) == ([], [], [])


def test_reports_a_remote_row_with_no_local_counterpart():
    """A question in Selectly that qbank no longer has approved — report, never guess."""
    pairs, unmatched, ambiguous = match([local("q1", "What is 2+2?")],
                                        [remote("s9", "Something else entirely")])
    assert pairs == []
    assert [r["id"] for r in unmatched] == ["s9"]


def test_duplicate_stems_are_separated_by_their_options():
    """13 approved VR questions share 6 stems — 'Which word does NOT belong?' and similar."""
    stem = "Which word does NOT belong with the others?"
    loc = [local("q1", stem, a="Emu", b="Wren", c="Crow", d="Dingo"),
           local("q2", stem, a="Oak", b="Elm", c="Ash", d="Salmon")]
    rem = [remote("s2", stem, {"A": "Oak", "B": "Elm", "C": "Ash", "D": "Salmon"}),
           remote("s1", stem, {"A": "Emu", "B": "Wren", "C": "Crow", "D": "Dingo"})]
    pairs, unmatched, ambiguous = match(loc, rem)
    assert sorted((s, q) for s, q, _ in pairs) == [("s1", "q1"), ("s2", "q2")]
    assert (unmatched, ambiguous) == ([], [])


def test_duplicate_stems_with_identical_options_are_reported_not_guessed():
    """Two genuinely indistinguishable rows: leaving both unaddressable beats a coin flip."""
    stem = "Which word does NOT belong with the others?"
    loc = [local("q1", stem), local("q2", stem)]
    pairs, unmatched, ambiguous = match(loc, [remote("s1", stem)])
    assert pairs == []
    assert [r["id"] for r in ambiguous] == ["s1"]


def test_a_local_question_is_never_claimed_twice():
    """qbank_id is unique — assigning one id to two rows would fail the write anyway."""
    stem = "What is 2+2?"
    pairs, unmatched, ambiguous = match([local("q1", stem)],
                                        [remote("s1", stem), remote("s2", stem)])
    assert len(pairs) == 1
    assert len(unmatched) == 1
    assert pairs[0][1] == "q1"


def test_passage_subjects_match_on_the_transformed_stem():
    """push_to_selectly prefixes passage questions with 'PASSAGE:...QUESTION:...'.

    Matching the raw stem would leave every SR and RC question unmatched.
    """
    loc = [local("q1", "According to Study 2, what happened?", passage="Researchers...")]
    transformed = "PASSAGE:\nResearchers...\n\nQUESTION:\nAccording to Study 2, what happened?"
    pairs, unmatched, ambiguous = match(loc, [remote("s1", transformed)])
    assert pairs == [("s1", "q1", transformed)]
    assert unmatched == []
