"""Tests for the §6 banned-type verbal classifier.

The point of these is that 158 approved questions are withdrawn from students on this
classifier's say-so, so both directions matter: it must catch the artefacts, and it must
not sweep in legitimate vocabulary work.
"""

import pytest

from tools.vr_banned_types import BANNED, QUESTIONABLE, classify, collect

import re


def q(stem="", topic="", status="approved", qid="x"):
    return {"id": qid, "stem": stem, "topic": topic, "review_status": status,
            "source_book": "b"}


@pytest.mark.parametrize(
    "topic,stem,expected",
    [
        ("Word Codes", "If MAP = 13116, what does POT equal?", "letter_number_codes"),
        ("Hidden Words", "Find the hidden word in 'She listened'.", "hidden_words"),
        ("dictionary alphabetical order", "Arrange in dictionary order:", "alphabetical_ordering"),
        ("Making Words", "Choose one letter from each word", "anagrams"),
        ("word formation from letter positions", "using the 1st, 2nd, 4th letters",
         "alphabet_position"),
    ],
)
def test_catches_the_artefacts(topic, stem, expected):
    hit = classify(q(stem=stem, topic=topic))
    assert hit is not None and hit[0] == expected


@pytest.mark.parametrize(
    "topic,stem",
    [
        ("vocabulary in context / synonyms",
         "The council's decision was met with vociferous protest. Vociferous means:"),
        ("antonyms / opposites", "Which word is most nearly opposite to ABUNDANT?"),
        ("sentence completion", "The drought ______ the harvest for a third year."),
        ("shades of meaning / connotation", "Which word suggests the mildest disapproval?"),
        ("analogies", "PAINTER is to BRUSH as SURGEON is to ______"),
    ],
)
def test_leaves_legitimate_vocabulary_alone(topic, stem):
    assert classify(q(stem=stem, topic=topic)) is None


def test_a_stem_can_fire_when_the_topic_is_vague():
    hit = classify(q(topic="word puzzle", stem="In a certain code language, CAT is 3120."))
    assert hit is not None and hit[1] == "stem"


def test_topic_beats_stem_so_the_reason_is_reportable():
    hit = classify(q(topic="Hidden Words", stem="Find the hidden word in 'She listened'."))
    assert hit == ("hidden_words", "topic")


def test_off_taxonomy_is_kept_out_of_the_banned_count():
    """§6 is an argument from absence; off-taxonomy is a judgement call. Merging them
    turns a defensible 158 into an indefensible 344."""
    rows = [q(topic="odd-one-out semantic grouping"), q(topic="spatial reasoning"),
            q(topic="Word Codes", stem="If MAP = 13116")]
    banned, questionable = collect(rows)
    assert len(banned) == 1
    assert len(questionable) == 2


def test_every_category_has_a_usable_topic_pattern():
    for category, topic_pat, _ in BANNED:
        assert topic_pat, f"{category} has no topic pattern"
        re.compile(topic_pat)


def test_questionable_pattern_compiles_and_excludes_vocabulary():
    assert not re.search(QUESTIONABLE, "vocabulary in context / synonyms")
    assert re.search(QUESTIONABLE, "odd-one-out semantic grouping")
