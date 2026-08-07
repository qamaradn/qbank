"""Batch-level question quality checks.

Each test names the real defect it guards against — all five were found in shipped
batches after per-question validation passed clean. See tools/question_checks.py.
"""
import pytest

from tools.question_checks import (
    COMPREHENSION_RELATIONS,
    STRUCTURAL_RELATIONS,
    answer_shape_monotony,
    by_topic,
    distractor_relation_errors,
    disputes_its_own_key,
    explanation_addresses_a_distractor,
    figure_svg_errors,
    leaked_working,
    length_tell,
    options_distinct,
    positional_reference,
    relation_monotony,
    unknown_words,
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


# ---------------------------------------------------------------- distractor relations
def vq(key="Restrict", d1="Postpone", d2="Extend", d3="Cultivate",
       r=("nuance", "opposite", "form"), topic="Synonyms"):
    q = {"topic": topic, "correct_answer": "A", "option_a": key,
         "option_b": d1, "option_c": d2, "option_d": d3,
         "relations": {d1: r[0], d2: r[1], d3: r[2]}}
    return q


def test_relations_accepts_three_differently_wrong_distractors():
    assert distractor_relation_errors(vq()) == []


def test_relations_rejects_a_coherent_distractor_bloc():
    """REGRESSION: ABUNDANT -> Plentiful against Scarce/Limited/Meagre.

    All three distractors were mutual synonyms, so the key was the odd one out and the
    item tested pattern-spotting rather than vocabulary.
    """
    errs = distractor_relation_errors(
        vq(key="Plentiful", d1="Scarce", d2="Limited", d3="Meagre",
           r=("opposite", "opposite", "opposite")))
    assert any("cohere" in e for e in errs)


def test_relations_rejects_two_of_three_sharing_a_relation():
    errs = distractor_relation_errors(vq(r=("opposite", "opposite", "form")))
    assert any("2 different way" in e for e in errs)


def test_relations_requires_every_distractor_to_declare_one():
    q = vq()
    del q["relations"]["Extend"]
    assert any("no declared relation" in e for e in distractor_relation_errors(q))


def test_relations_rejects_an_unknown_relation_name():
    assert any("unknown relation" in e
               for e in distractor_relation_errors(vq(r=("nuance", "opposite", "vibes"))))


def test_relations_rejects_declaring_the_correct_answer():
    """Declaring the key would quietly satisfy the distinct-relations count."""
    q = vq()
    q["relations"]["Restrict"] = "nuance"
    assert any("must not appear" in e for e in distractor_relation_errors(q))


def test_relations_reports_a_missing_map():
    assert distractor_relation_errors({"correct_answer": "A", "option_a": "x"}) == [
        "missing 'relations' map for the three distractors"]


def test_relations_accepts_the_comprehension_vocabulary():
    """A comprehension option is wrong about a proposition, not about a word."""
    q = vq(key="Rain clouds pass without dropping rain",
           d1="Sheep are being shorn nearby", d2="A storm has damaged the tank",
           d3="The family has moved west",
           r=("literal", "unsupported", "wrong_focus"))
    assert distractor_relation_errors(q, vocabulary=COMPREHENSION_RELATIONS) == []


def test_relations_keeps_the_two_vocabularies_apart():
    """'literal' is not a way one word is wrong beside another, and vice versa."""
    q = vq(r=("literal", "unsupported", "wrong_focus"))
    assert any("unknown relation" in e for e in distractor_relation_errors(q))
    q2 = vq(r=("collocation", "unsupported", "wrong_focus"))
    assert any("unknown relation 'collocation'" in e for e in
               distractor_relation_errors(q2, vocabulary=COMPREHENSION_RELATIONS))


def test_relations_still_demands_incoherence_under_comprehension_vocabulary():
    q = vq(r=("unsupported", "unsupported", "unsupported"))
    assert any("cohere" in e for e in
               distractor_relation_errors(q, vocabulary=COMPREHENSION_RELATIONS))


def test_relation_monotony_flags_one_template_across_a_batch():
    """Each question can be individually sound while the batch runs a single template."""
    batch = [vq() for _ in range(12)]
    errs = relation_monotony(batch)
    assert len(errs) == 1
    assert "12 of 12" in errs[0]


def test_relation_monotony_passes_on_a_varied_batch():
    combos = [("nuance", "opposite", "form"), ("domain", "overreach", "nuance"),
              ("form", "collocation", "opposite"), ("overreach", "domain", "collocation")]
    batch = [vq(r=combos[i % 4]) for i in range(12)]
    assert relation_monotony(batch) == []


# ---------------------------------------------------------------- unknown_words
def test_unknown_words_catches_an_invented_lookalike():
    """REGRESSION: 'mimec' shipped as a form-distractor for 'mimic'.

    A student who has never met the target can still strike out a non-word on sight,
    and a marker reads it as a typo.
    """
    assert unknown_words("mimec") == ["mimec"]


@pytest.mark.parametrize("word", ["flavour", "recognise", "metres", "defence", "colour"])
def test_unknown_words_accepts_australian_spelling(word):
    """The system wordlist is American English; the bank is written in Australian."""
    assert unknown_words(word) == []


@pytest.mark.parametrize("word", ["up-to-date", "hand-made", "old-world", "run-down"])
def test_unknown_words_accepts_hyphenated_compounds(word):
    assert unknown_words(word) == []


def test_unknown_words_accepts_the_target_word_via_extra_ok():
    assert unknown_words("saltbush", extra_ok=["saltbush"]) == []


# ---------------------------------------------------------------- leaked_working
@pytest.mark.parametrize("text", [
    "Fuel used = 57.375 litres. Oh, wait. The service station is 3/5 of the way.",
    "Area = 0.5 * 80 * 45 = 1800. Wait. Why did I select B?",
    "The total is 615 km. Let me recheck the options.",
    "So n = 8. Let's recheck: 3^7 = 2187.",
    "The answer is 12. My mistake — the ratio is 3:2.",
])
def test_leaked_working_catches_the_models_scratchpad(text):
    """REGRESSION: 139 shipped questions carried the generating model's own working.

    TASK §7 forbids it, and 12 of them were approved and serving students.
    """
    assert leaked_working(text) is not None


@pytest.mark.parametrize("text", [
    "Passengers were asked to wait, which is direct evidence the flight was delayed.",
    "The waiting time doubled after the timetable changed.",
    "Actually is an adverb meaning in fact.",
    "She had to wait three hours for the connecting service.",
])
def test_leaked_working_ignores_ordinary_prose(text):
    """'wait' is an ordinary verb; only self-correction contexts count."""
    assert leaked_working(text) is None


def test_disputes_its_own_key_flags_an_untrustworthy_answer():
    """Every explanation that argued about which option was right had the wrong key.

    Two of them were approved: 0.5 x 80 x 45 = 1800 stored as 3600, and a 30 000 m2
    block divided into 100 m2 plots stored as 250 rather than 300.
    """
    assert disputes_its_own_key("My answer is 300, which is option B. Why did I select A?")
    assert disputes_its_own_key("Let me recheck the options. The option is 1800.")


def test_disputes_its_own_key_is_quiet_on_a_clean_explanation():
    assert not disputes_its_own_key(
        "The block covers 30 000 square metres and each plot 100, giving 300 plots.")


# ------------------------------------------- explanation_addresses_a_distractor
def cq(explanation, key="Rain clouds pass the farm without dropping any rain"):
    return {"correct_answer": "A", "option_a": key,
            "option_b": "Sheep are being shorn in the far paddock",
            "option_c": "A storm has damaged the tank stand",
            "option_d": "The family has moved further west",
            "explanation": explanation}


def test_explanation_must_quote_a_distractor_back():
    """REGRESSION: the cloze checks passed batches with two defensible answers.

    Every mechanical check was green; only reading the questions caught it. An author
    made to write down why the strongest rival fails has to look at the rival.
    """
    assert explanation_addresses_a_distractor(cq(
        "The clouds carry their rain past the property, so nothing falls on the farm. "
        "It is a long, careful explanation about the key and about nothing else at all."
    )) is not None


def test_explanation_naming_a_distractor_passes():
    assert explanation_addresses_a_distractor(cq(
        "The clouds carry their rain past the property; 'wool' is a comparison for their "
        "thickness, so a storm has damaged the tank stand invents an event the poem "
        "never mentions.")) is None


def test_explanation_matching_only_stopwords_does_not_count():
    """A run of pure function words is coincidence, not a rival being discharged."""
    q = {"correct_answer": "A", "option_a": "The rain falls on the farm",
         "option_b": "It is not the rain that matters",
         "option_c": "A storm damages the stand",
         "option_d": "The family leaves",
         "explanation": "The clouds pass over, and it is not going to fall here at all."}
    assert explanation_addresses_a_distractor(q) is not None


def test_explanation_matches_a_short_distractor_whole():
    q = {"correct_answer": "A", "option_a": "absorbed", "option_b": "amused",
         "option_c": "frightened", "option_d": "bored",
         "explanation": "The speaker leans in rather than laughing; amused misses how "
                        "still the watching is."}
    assert explanation_addresses_a_distractor(q) is None


def test_explanation_empty_is_reported():
    assert "empty" in explanation_addresses_a_distractor(cq(""))


# ---------------------------------------------------------------- STRUCTURAL_RELATIONS
def test_structural_relations_describe_the_seam_not_the_world():
    """A structural-cloze distractor can be perfectly true and still be the wrong sentence.

    What fails is cohesion, so the vocabulary has to name the seam between two sentences
    rather than a claim about the passage's subject.
    """
    q = vq(key="The 412 and the 421 leave from the same bay, one minute apart.",
           d1="The interchange had been rebuilt the previous summer.",
           d2="She had climbed onto the wrong one without looking up.",
           d3="Mia got off at the next stop and waited.",
           r=("off_topic", "redundant", "wrong_order"))
    assert distractor_relation_errors(q, vocabulary=STRUCTURAL_RELATIONS) == []


def test_structural_vocabulary_rejects_comprehension_relations():
    """'literal' is a misreading of a figure; it says nothing about where a sentence goes."""
    q = vq(r=("literal", "redundant", "off_topic"))
    assert any("unknown relation 'literal'" in e for e in
               distractor_relation_errors(q, vocabulary=STRUCTURAL_RELATIONS))


def test_structural_still_demands_three_different_failures():
    q = vq(r=("redundant", "redundant", "redundant"))
    assert any("cohere" in e for e in
               distractor_relation_errors(q, vocabulary=STRUCTURAL_RELATIONS))


def test_unknown_words_accepts_a_possessive_of_a_known_word():
    """"Ravi's" is the same word as "Ravi" — without this every possessive is reported."""
    assert unknown_words("Ravi's bike", extra_ok={"ravi"}) == []
    assert unknown_words("the dog's bowl") == []


def test_unknown_words_still_catches_a_possessive_of_an_invented_word():
    assert unknown_words("the mimec's handle") == ["mimec's"]


def test_length_tell_floor_catches_the_over_correction():
    """A key that is NEVER the longest is worth as much to a guesser as one that always is."""
    batch = [q(correct="A", option_b="a much longer distractor than the key is") for _ in range(20)]
    errs = length_tell(batch, floor=0.12)
    assert len(errs) == 1 and "over-corrected" in errs[0]


def test_length_tell_floor_is_off_by_default():
    batch = [q(correct="A", option_b="a much longer distractor than the key is") for _ in range(20)]
    assert length_tell(batch) == []


def test_length_tell_floor_passes_a_group_sitting_near_chance():
    batch = [q(correct="A", option_a="a much longer key than the distractors are")
             for _ in range(5)]
    batch += [q(correct="A", option_b="a much longer distractor than the key") for _ in range(15)]
    assert length_tell(batch, floor=0.12) == []
