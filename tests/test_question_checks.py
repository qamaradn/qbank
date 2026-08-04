"""Batch-level question quality checks.

Each test names the real defect it guards against — all five were found in shipped
batches after per-question validation passed clean. See tools/question_checks.py.
"""
import pytest

from tools.question_checks import (
    answer_shape_monotony,
    by_topic,
    figure_svg_errors,
    length_tell,
    options_distinct,
    positional_reference,
)


def q(correct="A", topic="judgement", **opts):
    base = {"option_a": "aa", "option_b": "bb", "option_c": "cc", "option_d": "dd"}
    base.update(opts)
    return {"topic": topic, "correct_answer": correct, **base}


# ---------------------------------------------------------------- length_tell
def test_length_tell_flags_group_where_key_is_longest():
    """REGRESSION: 32 of 32 LR judgement keys were the longest option."""
    batch = [q(correct="A", option_a="a fully qualified and precise answer") for _ in range(8)]
    errs = length_tell(batch)
    assert len(errs) == 1
    assert "8 of 8" in errs[0]
    assert "judgement" in errs[0]


def test_length_tell_passes_when_key_length_varies():
    batch = [q(correct="A", option_a="a fully qualified and precise answer") for _ in range(3)]
    batch += [q(correct="B", option_a="a fully qualified and precise answer") for _ in range(5)]
    assert length_tell(batch) == []


def test_length_tell_ignores_groups_below_min_size():
    """Four questions cannot establish a pattern; flagging them is noise."""
    batch = [q(correct="A", option_a="a much longer option here") for _ in range(4)]
    assert length_tell(batch) == []


# ---------------------------------------------------------------- answer_shape_monotony
NAMES = ["Priya", "Marcus", "Ingrid", "Tomas", "Leila", "Aroha",
         "Beau", "Omar", "Grace", "Noah", "Ruby", "Levi"]


def test_shape_monotony_flags_repeated_key_shape_despite_distinct_text():
    """REGRESSION: 15 keys of '<student> only' — all textually distinct, all one shape.

    This is the case no near-duplicate screen can catch: the names differ, so every
    stem and key is unique, yet the answer is guessable without reading the question.
    """
    batch = [q(correct="A", option_a=f"{n} only") for n in NAMES]
    errs = answer_shape_monotony(batch)
    assert len(errs) == 1
    assert "12 of 12" in errs[0]


def test_shape_monotony_passes_on_varied_answer_forms():
    forms = ["{n} only", "Both {n} and the others", "Neither {n} nor the others"]
    batch = [q(correct="A", option_a=forms[i % 3].format(n=n)) for i, n in enumerate(NAMES)]
    assert answer_shape_monotony(batch) == []


def test_shape_monotony_ignores_groups_too_small_to_judge():
    """REGRESSION: batch p1 flagged 3-of-4 '<N> only' against a bank-wide rate of 47%.

    "A only" and "B only" reduce to the same shape, so ~50% is correct for that
    archetype. A four-question sample hits 75% about a quarter of the time, so the check
    must see the accumulated bank rather than one batch.
    """
    batch = [q(correct="A", option_a=f"{n} only") for n in NAMES[:4]]
    assert answer_shape_monotony(batch) == []


def test_shape_monotony_ignores_single_word_vocabulary_answers():
    """Every synonym key is one capitalised word — and so is every distractor.

    Blanking names reduces all of them to '<N>', which matched 6 real VR groups. It is
    not a shape a student can exploit, because the options are indistinguishable by form.
    """
    batch = [q(correct="A", topic="Synonyms", option_a=w) for w in
             ["Frugal", "Candid", "Placate", "Discern", "Curtail", "Ovation",
              "Edict", "Pique", "Sparse", "Wary", "Brisk", "Terse"]]
    assert answer_shape_monotony(batch) == []


def test_shape_monotony_still_flags_short_prose_with_a_content_word():
    """'<N> only' survives the filter — 'only' is content, and the distractors differ."""
    batch = [q(correct="A", option_a=f"{n} only") for n in NAMES]
    assert len(answer_shape_monotony(batch)) == 1


def test_shape_monotony_skips_numeric_answer_groups():
    """Value answers all 'look alike' by construction — flagging them is a false alarm."""
    batch = [q(correct="A", option_a=v) for v in ["$5", "72", "14", "$9", "31", "6"]]
    assert answer_shape_monotony(batch) == []


def test_shape_monotony_ignores_question_with_malformed_key():
    """A bad correct_answer must not crash the batch check — format validation reports it."""
    batch = [q(correct="X", option_a="Priya only") for _ in range(5)]
    answer_shape_monotony(batch)  # must not raise


# ---------------------------------------------------------------- grouping
def test_groups_are_independent():
    """A predictable category must be caught even when the batch overall looks balanced."""
    bad = [q(correct="A", topic="who_reasons", option_a="a very long precise key") for _ in range(6)]
    good = [q(correct=c, topic="ordering") for c in "ABCDAB"]
    errs = length_tell(bad + good)
    assert len(errs) == 1
    assert "who_reasons" in errs[0]


def test_by_topic_returns_none_for_untopiced_question():
    """None excludes a question from group checks rather than making an empty-string group."""
    assert by_topic({"topic": ""}) is None
    assert by_topic({}) is None


# ---------------------------------------------------------------- positional_reference
@pytest.mark.parametrize("text", [
    "The first three pairs are anagrams, so the odd one out is the remaining pair.",
    "The other three all describe mammals.",
    "Option C is wrong because the rate is per hour, not per minute.",
    "The former is a cause, the latter an effect.",
])
def test_positional_reference_flags_option_positions(text):
    """REGRESSION: 3 explanations named option positions and went false after shuffling."""
    assert positional_reference(text) is not None


@pytest.mark.parametrize("text", [
    "The first two statements establish that every parrot eats carrots.",
    "The last three premises are consistent with both conclusions.",
    "Chocolate melts at 34 degrees, so the sample was above that temperature.",
])
def test_positional_reference_allows_references_to_the_stem(text):
    """Stem sentences are never reordered, so pointing at them is safe and useful."""
    assert positional_reference(text) is None


def test_positional_reference_handles_missing_explanation():
    assert positional_reference(None) is None
    assert positional_reference("") is None


# ---------------------------------------------------------------- figure_svg_errors
def test_figure_svg_accepts_a_conforming_figure():
    svg = '<svg viewBox="0 0 340 220"><path d="M0 0 L10 10" stroke="currentColor"/></svg>'
    assert figure_svg_errors(svg) == []


def test_figure_svg_requires_viewbox_and_currentcolor():
    errs = figure_svg_errors('<svg><path d="M0 0" stroke="#333"/></svg>')
    assert any("viewBox" in e for e in errs)
    assert any("currentColor" in e for e in errs)


def test_figure_svg_rejects_hardcoded_colours():
    """A figure drawn in black is invisible on the dark surface; white, on the review card."""
    svg = '<svg viewBox="0 0 10 10"><rect fill="white" stroke="currentColor"/></svg>'
    assert any("hard-codes" in e for e in figure_svg_errors(svg))


def test_figure_svg_rejects_oversized_figure():
    svg = '<svg viewBox="0 0 10 10" stroke="currentColor">' + "<rect/>" * 900 + "</svg>"
    assert any("bytes" in e for e in figure_svg_errors(svg))


def test_figure_svg_empty_is_not_an_error():
    """Most questions carry no figure; absence must not be reported as a defect."""
    assert figure_svg_errors(None) == []
    assert figure_svg_errors("") == []


# ---------------------------------------------------------------- options_distinct
def test_options_distinct_detects_case_and_whitespace_duplicates():
    assert options_distinct(q()) is True
    assert options_distinct(q(option_b="AA")) is False
    assert options_distinct(q(option_b="  aa  ")) is False
