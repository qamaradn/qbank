"""Batch-level question quality checks.

Each test names the real defect it guards against — all five were found in shipped
batches after per-question validation passed clean. See tools/question_checks.py.
"""
import pytest

from tools.question_checks import (
    options_distinct_by_value,
    one_point_on_the_line,
    markdown_table_in_stem,
    invalid_clock_time,
    teaching_manipulative,
    calculator_required,
    non_integer_count,
    negative_count,
    no_question_asked,
    compounding_needs_calculator,
    doubled_circle_outline,
    overlapping_text_labels,
    plotted_points_inconsistent,
    text_overlaps_geometry,
    axes_unlabelled,
    angle_arc_malformed,
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


def test_options_distinct_by_value_catches_two_correct_answers():
    """4/13 and 16/52 are the same probability, so keying one marks the other wrong.

    Found by blind-solve in vic-drill-mq-016: the stored explanation read
    "P = 16/52 = 4/13", naming both options without noticing.
    """
    q = dict(stem="What is the probability?", option_a="4/13", option_b="17/52",
             option_c="16/52", option_d="1/4", correct_answer="A")
    msg = options_distinct_by_value(q)
    assert msg and "A/C" in msg and "two correct answers" in msg


def test_options_distinct_by_value_catches_matching_distractors():
    """No wrong marking, but a solver discards both for free — neither can be the key."""
    q = dict(stem="What is the probability?", option_a="2/5", option_b="2/3",
             option_c="1/3", option_d="6/9", correct_answer="A")
    msg = options_distinct_by_value(q)
    assert msg and "B/D" in msg and "two correct answers" not in msg


def test_options_distinct_by_value_exempts_lowest_terms():
    """6/8 beside 3/4 is the POINT of a lowest-terms question, not a defect —
    exactly one option satisfies the instruction."""
    q = dict(stem="Write 42/56 in its lowest terms.", option_a="6/8", option_b="3/4",
             option_c="3/8", option_d="4/3", correct_answer="B")
    assert options_distinct_by_value(q) is None


def test_options_distinct_by_value_passes_clean_options():
    q = dict(stem="What is the probability?", option_a="1/2", option_b="1/3",
             option_c="1/4", option_d="1/5", correct_answer="A")
    assert options_distinct_by_value(q) is None


def test_one_point_on_the_line_catches_two_valid_points():
    """(2, 1) and (1, -1) both satisfy y = 2x - 3, so keying one marks the other wrong.
    They are different points, so options_distinct_by_value cannot see it."""
    q = dict(stem="The graph shows the line y = 2x − 3. Which point lies on this line?",
             option_a="(2, 1)", option_b="(0, 2)", option_c="(1, −1)",
             option_d="(3, 4)", correct_answer="A")
    msg = one_point_on_the_line(q)
    assert msg and "A/C" in msg and "more than one correct answer" in msg


def test_one_point_on_the_line_passes_a_sound_question():
    q = dict(stem="The graph shows the line y = 2x − 3. Which point lies on this line?",
             option_a="(2, 1)", option_b="(0, 2)", option_c="(1, −2)",
             option_d="(3, 4)", correct_answer="A")
    assert one_point_on_the_line(q) is None


# ---------------------------------------------------------------------------
# Regression tests from the first NSW review round (2026-08-22). Each case is the
# real flagged question, so a future batch cannot reintroduce the same defect
# without a named test going red.
# ---------------------------------------------------------------------------

def test_markdown_table_in_stem_is_caught():
    """Flagged twice: 'Table format is quite messy and wrong'. Selectly renders stems as
    plain text, so the |---|---| separator row reaches the student verbatim."""
    q = dict(stem=(
        "A hall in Warrnambool is hired using the rule c = 12h + 30.\n\n"
        "| Hours (h) | 2  | 4  | ?   |\n"
        "|-----------|----|----|-----|\n"
        "| Cost ($c) | 54 | 78 | 126 |\n\n"
        "How many hours does the $126 hire cover?"))
    assert "markdown table" in (markdown_table_in_stem(q) or "")


def test_prose_with_a_pipe_is_not_a_table():
    assert markdown_table_in_stem(dict(stem="Choose the option A | B that fits.")) is None


def test_invalid_clock_time_is_caught():
    """'2:65 am' models a real error — adding 40 and 25 minutes without regrouping — but
    as a clock time it reads as a typo and undermines a question whose key is correct."""
    q = dict(stem="A flight leaves Perth at 11:40 pm and is in the air for 3 hours 25 minutes.",
             option_a="2:65 am", option_b="3:05 pm", option_c="2:05 am", option_d="3:05 am",
             correct_answer="D", explanation="")
    msg = invalid_clock_time(q)
    assert msg and "2:65" in msg


def test_valid_times_pass():
    q = dict(stem="Leaves at 11:40 pm.", option_a="2:40 am", option_b="3:05 pm",
             option_c="2:05 am", option_d="3:05 am", correct_answer="D", explanation="")
    assert invalid_clock_time(q) is None


def test_teaching_manipulative_is_caught():
    """A selective exam must not test which materials a student's classroom happened to
    use. 'Why would you add zero pairs to a counter model?' does exactly that."""
    q = dict(stem="Why would you add zero pairs to a counter model?", explanation="")
    assert "manipulative" in (teaching_manipulative(q) or "")


def test_calculator_required_is_caught():
    """'this question needs a calculator to be solved' — the key is 12.58, reached only
    by evaluating a root of a non-square."""
    q = dict(stem="How far does he run? Round your answer to two decimal places.",
             option_a="8.23 m", option_b="11.89 m", option_c="12.58 m", option_d="15.95 m",
             correct_answer="C",
             explanation="Using Pythagoras: √(11.885² + 4.115²) = √158.186 ≈ 12.58 m.")
    assert "calculator" in (calculator_required(q) or "")


def test_an_exact_surd_answer_is_not_calculator_work():
    """Leaving the answer as a surd is exact and fair; only evaluating it is not."""
    q = dict(stem="What is the distance?", option_a="√65 km", option_b="8 km",
             option_c="9 km", option_d="65 km", correct_answer="A",
             explanation="Distance = √(1² + 8²) = √65 km.")
    assert calculator_required(q) is None


def test_non_integer_count_is_caught():
    """'how can a cricket team score runs with decimals?' — 206.25 runs."""
    q = dict(stem=("A cricket team scores 275 runs in their first innings. In their "
                   "second innings, they score 75% of their first innings total. How "
                   "many runs did they score in the second innings?"),
             option_a="206", option_b="205", option_c="206.25", option_d="207",
             correct_answer="C", explanation="")
    msg = non_integer_count(q)
    assert msg and "206.25" in msg


def test_a_fractional_measurement_is_fine():
    """Only counts must be whole. 2.5 mm of rain is a measurement, not a count."""
    q = dict(stem="What was the mean daily rainfall over the 30 days?",
             option_a="2.5 mm", option_b="3 mm", option_c="2 mm", option_d="4 mm",
             correct_answer="A", explanation="")
    assert non_integer_count(q) is None


# ---------------------------------------------------------------------------
# Regression tests from the first VIC review round (2026-08-23). Six of the
# fourteen flags were about figure QUALITY — a class neither the blind solve nor
# the NSW round surfaced, because both were reading the maths, not looking.
# ---------------------------------------------------------------------------

def test_negative_count_is_caught():
    """'maybe remove the -1 wickets option; how can a bowler have -1 wickets?'"""
    q = dict(stem="Over 9 matches she averaged 3 wickets. In the first 8 she took 25. "
                  "How many did she take in the last one?",
             option_a="3 wickets", option_b="2 wickets", option_c="-1 wickets",
             option_d="25 wickets", correct_answer="B")
    assert "cannot be negative" in (negative_count(q) or "")


def test_no_question_asked_is_caught():
    """'doesn't specify what the question really is' — the stem stops after the material."""
    q = dict(stem="Consider the following information about the Sydney Opera House. It "
                  "hosts over 1,500 performances annually. Despite its fame, there have "
                  "been ongoing debates about its acoustics and operational costs.")
    assert no_question_asked(q)


def test_a_colon_frame_and_a_mid_stem_imperative_both_count_as_asking():
    """Reading uses a cloze frame and maths puts the imperative mid-sentence. An earlier
    version fired on 1,498 well-formed questions for missing both."""
    assert no_question_asked(dict(stem="the word 'decimated' most closely means:")) is None
    assert no_question_asked(
        dict(stem="Noon is 38C. Using F = (9/5)C + 32, convert this to Fahrenheit.")) is None


def test_compounding_needs_calculator_is_caught():
    """A 25-year mortgage compounded monthly, and five daily percentage changes."""
    assert compounding_needs_calculator(dict(
        stem="a loan at 4.2% per annum, compounded monthly, over 25 years"))
    assert compounding_needs_calculator(dict(
        stem="the value changes by +5%, -2%, +3%, -4%, and +6% respectively"))


def test_doubled_circle_outline_is_caught():
    """'the top part of the circumference has double lining' — an arc retraces a circle
    already stroked at the same radius."""
    svg = ("<svg><circle cx='140' cy='120' r='80' fill='none' stroke='currentColor'/>"
           "<path d='M 60 120 A 80 80 0 0 1 108 50' stroke='currentColor'/></svg>")
    assert "drawn twice" in (doubled_circle_outline(svg) or "")


def test_an_arc_of_a_different_radius_is_not_a_doubled_outline():
    svg = ("<svg><circle cx='140' cy='120' r='80' fill='none' stroke='currentColor'/>"
           "<path d='M 100 120 A 40 40 0 0 1 108 90' stroke='currentColor'/></svg>")
    assert doubled_circle_outline(svg) is None


def test_plotted_points_inconsistent_is_caught():
    """The real parallelogram: P(-6,2) Q(2,2) R(4,-4) S(-4,-4) drawn at three different
    horizontal scales. 'the spacing of each point isn't equal'."""
    svg = ("<svg><circle cx='65' cy='82' r='3'/><circle cx='185' cy='82' r='3'/>"
           "<circle cx='205' cy='162' r='3'/><circle cx='85' cy='162' r='3'/>"
           "<text x='30' y='78'>P(−6,2)</text><text x='188' y='78'>Q(2,2)</text>"
           "<text x='208' y='170'>R(4,−4)</text><text x='48' y='175'>S(−4,−4)</text></svg>")
    assert plotted_points_inconsistent(svg)


def test_points_on_one_scale_pass():
    """Same four points, plotted properly at 15 px per unit about (140, 110)."""
    pts = {"P": (-6, 2), "Q": (2, 2), "R": (4, -4), "S": (-4, -4)}
    body = "".join(
        f"<circle cx='{140 + 15 * x}' cy='{110 - 15 * y}' r='3'/>" for x, y in pts.values())
    body += "".join(f"<text x='10' y='10'>{n}({x},{y})</text>" for n, (x, y) in pts.items())
    assert plotted_points_inconsistent(f"<svg>{body}</svg>") is None


def test_an_em_dash_frame_counts_as_asking():
    """NSW reading opens its cloze with a dash rather than a colon. Both are the same
    device, and missing the dash flagged two ordinary questions on the way to a push."""
    assert no_question_asked(
        dict(stem='The passage says "difficult". Here, "difficult" means —')) is None


def test_an_unresolved_radicand_is_not_read_as_the_answer():
    """√(8² + 15²) resolves to √289 = 17 exactly. Reading the 8 out of the unevaluated
    form called a sound rhombus question calculator-work and blocked a push."""
    q = dict(stem="What is the length of one side, to the nearest hundredth?",
             option_a="23.00 cm", option_b="14.42 cm", option_c="34.00 cm",
             option_d="17.00 cm", correct_answer="D",
             explanation="Side = √(8² + 15²) = √(64 + 225) = √289 = 17.00 cm.")
    assert calculator_required(q) is None


# --------------------------------------------------------------- VIC round 2
# All three flags were figure geometry, on figures nobody had questioned before.

def test_text_overlaps_geometry_is_caught():
    """'fix the graph as the 0,5 is overlapping the line' — the point label was placed
    at the plotted line's own coordinates and printed straight through it."""
    svg = ('<svg><line x1="40" y1="130" x2="220" y2="40" stroke="currentColor"/>'
           '<text x="44" y="128" font-size="11">(0, 5)</text></svg>')
    assert "on top of the line" in (text_overlaps_geometry(svg) or "")


def test_a_rotated_axis_title_is_not_lying_across_the_plot():
    """An axis title written sideways up the y-axis sits in the margin. Read as
    horizontal text it appeared to sprawl over the data and both text checks reported
    collisions that were not there."""
    svg = ('<svg><line x1="40" y1="130" x2="220" y2="40" stroke="currentColor"/>'
           '<text x="2" y="105" font-size="12" transform="rotate(-90,12,105)">'
           'Dial reading (kg)</text></svg>')
    assert text_overlaps_geometry(svg) is None


def test_axes_unlabelled_is_caught():
    """'please label the axis for professionalism' — bars, numbers, and no word saying
    what is being counted."""
    svg = ('<svg><path d="M34 12V144H330" stroke="currentColor"/>'
           '<text x="24" y="148" font-size="10">0</text>'
           '<text x="24" y="126" font-size="10">2</text>'
           '<text x="24" y="104" font-size="10">4</text>'
           '<text x="24" y="82" font-size="10">6</text></svg>')
    assert "no axis titles" in (axes_unlabelled(svg) or "")


def test_a_coordinate_plane_needs_no_axis_titles():
    """x and y are the labels, by convention. Requiring words flagged every graph."""
    svg = ('<svg><path d="M34 12V144H330" stroke="currentColor"/>'
           '<text x="1" y="1" font-size="10">1</text><text x="2" y="2" font-size="10">2</text>'
           '<text x="3" y="3" font-size="10">3</text><text x="4" y="4" font-size="10">4</text>'
           '<text x="9" y="9" font-size="12">x</text>'
           '<text x="8" y="8" font-size="12">y</text></svg>')
    assert axes_unlabelled(svg) is None


def test_a_number_line_needs_no_axis_titles():
    """One rule, no second dimension: the numbers are the quantity."""
    svg = ('<svg><path d="M28 60H332" stroke="currentColor"/>'
           '<text x="40" y="84" font-size="9">-5</text><text x="65" y="84" font-size="9">0</text>'
           '<text x="90" y="84" font-size="9">5</text><text x="115" y="84" font-size="9">10</text>'
           '</svg>')
    assert axes_unlabelled(svg) is None


def test_angle_arc_malformed_is_caught():
    """'that little curve line going outside the triangle by a tiny bit near angle A' —
    endpoints 24.00 and 24.19 from the vertex against a declared radius of 24."""
    svg = ('<svg><polygon points="40,60 160,60 40,150"/>'
           '<path d="M40 126A24 24 0 0 0 61 138"/></svg>')
    assert "not sit on the angle" in (angle_arc_malformed(svg) or "")


def test_an_exact_angle_arc_passes():
    import math
    A, r = (40.0, 150.0), 24.0
    p1 = (40.0, 150.0 - r)
    dx, dy = 120.0, -90.0
    L = math.hypot(dx, dy)
    p2 = (A[0] + dx / L * r, A[1] + dy / L * r)
    svg = (f'<svg><polygon points="40,60 160,60 40,150"/>'
           f'<path d="M{p1[0]:.2f} {p1[1]:.2f}A{r:g} {r:g} 0 0 0 {p2[0]:.2f} {p2[1]:.2f}"/></svg>')
    assert angle_arc_malformed(svg) is None
