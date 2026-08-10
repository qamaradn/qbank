"""Tests for tools/repair_key_skew.py.

The invariant that matters: reordering must move options without changing the question.
The key's TEXT must be the same before and after — only its letter may differ.
"""
import random

import pytest

from tools.repair_key_skew import (
    LETTERS, blocker, build_change, distribution, plan_group, remap_explanation,
)


def q(**kw):
    base = dict(id="i1", subject="quantitative_reasoning", source_book="b",
                stem="s", option_a="one", option_b="two", option_c="three",
                option_d="four", correct_answer="A", explanation="because one.")
    base.update(kw)
    return base


# ---------------------------------------------------------------- remap
MAP = {"A": "C", "B": "A", "C": "D", "D": "B"}


@pytest.mark.parametrize("text,expected", [
    ("Option D is plausible.", "Option B is plausible."),
    ("Options C and D result from adding.", "Options D and B result from adding."),
    ("Options A, B and D are even.", "Options C, A and B are even."),
    ("option a is wrong; see option (C).", "option c is wrong; see option (D)."),
])
def test_remap_rewrites_option_references(text, expected):
    assert remap_explanation(text, MAP)[0] == expected


@pytest.mark.parametrize("text", [
    "The sum of the first four scores is 326.",       # points at the stem, not the options
    "Area = 1/2 x a x b x sin(C) gives 45 881.",      # C is an angle
    "The other two interior angles sum to 180.",
    "The answer is 5 because the total is 20.",
    "A drop of 15 degrees from 42 gives 27.",         # bare 'A' as an article
    "Both A and B are factors.",                      # no option word: blocker()'s job
])
def test_remap_leaves_non_option_letters_alone(text):
    assert remap_explanation(text, MAP)[0] == text


def test_remap_is_single_pass_not_chained():
    # A->B and B->C must not turn an A into a C by applying both rules in turn.
    out, _ = remap_explanation("Option A and option B.", {"A": "B", "B": "C", "C": "D", "D": "A"})
    assert out == "Option B and option C."


# ---------------------------------------------------------------- blockers
def test_blocker_catches_duplicate_options():
    assert blocker(q(option_d="one")) == "duplicate_options"


def test_blocker_catches_admitted_equivalence():
    assert blocker(q(explanation="options B and C are equivalent; 5 root 2 is simplest.")) \
        == "equivalent_admitted"
    assert blocker(q(explanation="Both A and B are factors.")) == "equivalent_admitted"


def test_blocker_catches_authoring_intent():
    assert blocker(q(explanation="I'll set answer C to 30 000.")) == "authoring_intent"
    assert blocker(q(explanation="This geometry needs fixing.")) == "authoring_intent"


def test_blocker_passes_a_clean_question():
    assert blocker(q()) is None


# ---------------------------------------------------------------- the reorder
def test_key_text_survives_the_reorder():
    rng = random.Random(0)
    src = q(correct_answer="B")
    ch = build_change(src, "D", rng)
    assert ch["new_key"] == "D"
    assert ch["after"]["option_d"] == src["option_b"], "key text must follow the key letter"


def test_reorder_is_a_permutation_nothing_invented_or_lost():
    rng = random.Random(0)
    for target in LETTERS:
        src = q(correct_answer="A")
        ch = build_change(src, target, rng)
        if ch is None:
            continue
        before = {src["option_" + L.lower()] for L in LETTERS}
        after = {ch["after"]["option_" + L.lower()] for L in LETTERS}
        assert before == after


def test_mapping_is_a_bijection():
    rng = random.Random(1)
    ch = build_change(q(correct_answer="C"), "A", rng)
    assert sorted(ch["mapping"]) == list(LETTERS)
    assert sorted(ch["mapping"].values()) == list(LETTERS)


def test_plan_group_is_uniform_within_one():
    rng = random.Random(7)
    group = [q(id=f"i{i}") for i in range(400)]
    counts = {}
    for letter in plan_group(group, rng).values():
        counts[letter] = counts.get(letter, 0) + 1
    assert max(counts.values()) - min(counts.values()) <= 1


def test_distribution_sums_to_one():
    rows = [q(correct_answer=L) for L in "AABBCD"]
    d = distribution(rows)
    assert abs(sum(d.values()) - 1.0) < 1e-9


def test_geometry_point_labels_are_never_remapped():
    """A..D are point labels in coordinate geometry. Remapping them corrupts the maths,
    so such a question is blocked rather than reordered."""
    expl = "AB is horizontal since both A and B have y = 4. For a right angle at B..."
    assert blocker(q(explanation=expl)) == "ambiguous_letter_reference"
    assert remap_explanation(expl, MAP)[0] == expl


def test_option_sense_both_is_still_blocked_as_equivalence():
    assert blocker(q(explanation="Both A and B are equivalent.")) == "equivalent_admitted"


def test_bare_inline_enumeration_is_blocked():
    """"A) m=3, B) y=6x-2, ... belongs to option B" enumerates the options in their
    current order; reordering makes the enumeration contradict the conclusion."""
    assert blocker(q(explanation="Convert each: A) m=3, B) m=6, C) m=2.5, D) m=4. "
                                 "The greatest is 6, which belongs to option B.")) \
        == "inline_option_enumeration"


def test_labelled_enumeration_is_not_blocked():
    """"Option A: ..." carries the option word, so it remaps and needs no block."""
    assert blocker(q(explanation="Option A: 4n+2 is even. Option C: 2n+4 is even. "
                                 "Option D: 8n+6 is even.")) is None


def test_equal_valued_option_is_blocked():
    assert blocker(q(explanation="Note that option D also equals 17, but option A "
                                 "gives the simplified value.")) == "equivalent_admitted"
