#!/usr/bin/env python3
"""Batch-level quality checks that apply to any subject.

Why this file exists
--------------------
Per-question validation — four options, one key, difficulty in range — passes a batch
that is collectively worthless. The defects below are invisible to any check that looks
at one question at a time, and invisible to a near-duplicate screen, because every
question is individually well-formed and textually distinct from the others. They only
appear when the *keys of a whole group* are compared with each other.

All three were found in the shipped `logical_reasoning` batches after the per-question
checks passed clean:

  - 32 of 32 judgement questions had the longest option as the key
  - 15 of 15 "who reasons correctly" keys were "<second-named student> only"
  - 3 explanations described options by position, which goes false once options shuffle

Grouping
--------
Every check takes a `group_of(question) -> str | None` callable. The shape defects are
per-category — a bank can be balanced overall while one category is entirely predictable
— so the grouping must match however the caller labels question types. The default reads
`topic`, which every subject populates; the LR builders pass their own reader for the
`"Category: <key> — <title>"` convention they store in `source_page_description`.

Returning None from `group_of` excludes that question from the group checks.
"""
import collections
import re

KEYS = ["option_a", "option_b", "option_c", "option_d"]


def by_topic(q):
    """Default grouping: the question's own topic label."""
    return q.get("topic") or None


def _key_text(q):
    """The text of the correct option, or '' if the key is missing/malformed."""
    letter = str(q.get("correct_answer", "")).strip().lower()
    if letter not in ("a", "b", "c", "d"):
        return ""
    return str(q.get("option_" + letter, ""))


def _grouped(questions, group_of):
    out = collections.defaultdict(list)
    for q in questions:
        g = group_of(q)
        if g:
            out[g].append(q)
    return out


# ---------------------------------------------------------------- the longest-option tell
def length_tell(questions, group_of=by_topic, cap=0.6, min_group=5):
    """Fail a group where the correct answer is reliably the longest option.

    "Pick the longest option" is the oldest multiple-choice shortcut there is, and a
    precise, fully qualified key sitting beside three short distractors hands it over.
    The LR bank once scored 32 out of 32 on that heuristic across its four judgement
    categories — every question individually sound, the set collectively useless as a
    test of reasoning. Cheap to measure, invisible to every other check here.
    """
    errs = []
    for group, qs in _grouped(questions, group_of).items():
        if len(qs) < min_group:
            continue
        flags = []
        for q in qs:
            lens = {L: len(str(q.get("option_" + L.lower(), ""))) for L in "ABCD"}
            flags.append(max(lens, key=lens.get) == str(q.get("correct_answer")))
        n = sum(flags)
        if n / len(flags) > cap:
            errs.append(f"[{group}]: the correct answer is the longest option in {n} of "
                        f"{len(flags)} — lengthen the distractors, or 'pick the longest' "
                        f"beats reading the question")
    return errs


# ---------------------------------------------------------------- answer-shape monotony
def _shape_signatures(key):
    """Signatures a pattern-matching student could latch onto in a correct answer.

    Proper nouns are blanked first, because the original defect was 15 keys of the form
    "<second-named student> only" — every one textually distinct thanks to the names,
    every one the same shape. Word 3-grams catch the longer prose keys, where the
    giveaway was a shared mechanism phrase such as "at the same time" rather than a
    shared opening.
    """
    norm = re.sub(r"\b[A-Z][a-z]+\b", "<N>", key).lower()
    words = re.findall(r"[a-z<>']+", norm)
    sigs = set()
    if len(words) <= 5:
        sigs.add(" ".join(words))           # short keys: the whole normalised phrase
    for i in range(len(words) - 2):
        sigs.add(" ".join(words[i:i + 3]))  # longer keys: any shared 3-gram
    # A signature of nothing but blanked names is not a shape a student can exploit.
    # Every synonym key is one capitalised word, which reduces to "<n>" — and so does
    # every distractor, so the match carries no information. Keeping these reported
    # 6 vocabulary groups as monotonous when they are merely single-word answers.
    return {s for s in sigs if s.strip() and set(s.split()) != {"<n>"}}


def _is_value_key(key):
    """True if the key is a computed value rather than a phrase.

    Where the answer is a value — "$5", "72", "Position 4", a run of symbols — every key
    looks alike by construction and that tells a student nothing, so comparing shapes
    there produces only false alarms. A digit is the reliable marker; so is a key with no
    letters at all.
    """
    return bool(re.search(r"\d", key)) or not re.search(r"[A-Za-z]", key)


def _is_prose_group(keys):
    """Only prose answers can carry an exploitable shape.

    Gate on whether the keys are values, NOT on how short they are. An earlier version
    used a word-count threshold of >2, which classified "Leo only" as a value answer and
    so skipped the group — meaning the original 15-of-15 "<student> only" defect this
    check exists to catch would have passed it. Short prose is still prose.
    """
    return bool(keys) and sum(_is_value_key(k) for k in keys) <= len(keys) / 2


def answer_shape_monotony(questions, group_of=by_topic, cap=0.6, min_group=10):
    """Fail a group whose correct answers nearly all share a shape.

    Neither the format checks nor the near-duplicate screen can see this: every question
    is individually well-formed and textually distinct from the others.

    Pass the WHOLE accumulated bank for a subject, not one freshly written batch. Some
    archetypes have a genuinely small shape space — in "who reasons correctly", both
    "A only" and "B only" reduce to "<N> only", so ~50% is the ideal rate, not a defect.
    Judged over a 4-question batch that lands at 75% about a quarter of the time; the
    same category over all 30 questions sits at 47% and passes. min_group is 10 for that
    reason, and callers should still aggregate rather than rely on it.
    """
    errs = []
    for group, qs in _grouped(questions, group_of).items():
        keys = [_key_text(q) for q in qs]
        if len(keys) < min_group or not _is_prose_group(keys):
            continue
        counts = collections.Counter(s for k in keys for s in _shape_signatures(k))
        if not counts:
            continue
        sig, n = counts.most_common(1)[0]
        if n / len(keys) > cap:
            errs.append(f"[{group}]: {n} of {len(keys)} correct answers share the shape "
                        f"{sig!r} — vary the answer, or the item is solvable by pattern "
                        f"rather than by reasoning")
    return errs


# ---------------------------------------------------------------- positional references
# "the first two statements" is fine — it points at sentences in the stem, which are
# never reordered. Only references to the OPTIONS are unsafe, since those get shuffled
# at load time and the explanation silently goes false.
POSITIONAL = re.compile(
    r"\b(the (first|last) (two|three|four)(?! (statements?|sentences?|premises?))|"
    r"the other three|the former|the latter|option [A-D]\b)", re.I)


def positional_reference(text):
    """Return the offending phrase if an explanation names option positions, else None."""
    m = POSITIONAL.search(str(text or ""))
    return m.group(0) if m else None


# ---------------------------------------------------------------- inline figure rules
HARDCODED_COLOURS = ("#fff", "#000", "white", "black", "rgb(")


def figure_svg_errors(svg, max_bytes=3500):
    """Rules an inline `figure_svg` must satisfy to render in both review and Selectly.

    The review card is white with `color: #0D1117` while other surfaces are dark, so a
    figure that does not draw in `currentColor` is invisible in one theme or the other.
    A missing viewBox renders at the default 300x150 and clips.
    """
    errs = []
    svg = (svg or "").strip()
    if not svg:
        return errs
    if "viewBox" not in svg:
        errs.append("figure_svg has no viewBox")
    if "currentColor" not in svg:
        errs.append("figure_svg must draw in currentColor")
    if len(svg) > max_bytes:
        errs.append(f"figure_svg is {len(svg)} bytes — keep under ~{max_bytes / 1000:.1f} KB "
                    f"(use one <path> for repeated rules, not many elements)")
    for bad in HARDCODED_COLOURS:
        if bad in svg.lower():
            errs.append(f"figure_svg hard-codes {bad!r}; use currentColor")
    return errs


# ---------------------------------------------------------------- distractor design
# How a distractor is wrong. A vocabulary item is only a test of vocabulary if the three
# distractors are wrong in DIFFERENT ways; if they are wrong in the same way they form a
# coherent group and the key becomes the odd one out, answerable without knowing the
# target word at all.
#
# This is not hypothetical. In ~24 of 26 sampled synonym/antonym questions in the shipped
# VR bank, all three distractors were mutual synonyms and the key was the singleton:
# ABUNDANT -> Plentiful against Scarce/Limited/Meagre; ROBUST -> Strong against
# Fragile/Weak/Delicate. Every one is solvable by pattern alone.
RELATIONS = {
    "opposite",       # antonym of the target
    "nuance",         # related meaning, wrong shade or degree
    "form",           # looks or sounds like the target (curtail / cultivate)
    "domain",         # same subject area, unrelated meaning
    "collocation",    # commonly appears beside the target, means something else
    "overreach",      # right direction, too absolute
}


def distractor_relation_errors(q, min_distinct=3):
    """Check a question's declared distractor relations.

    `relations` maps each DISTRACTOR TEXT to one of RELATIONS. Keyed by text, not by
    option letter, so it survives the answer shuffle.
    """
    errs = []
    rel = q.get("relations")
    if not isinstance(rel, dict):
        return ["missing 'relations' map for the three distractors"]

    key_letter = str(q.get("correct_answer", "")).strip().lower()
    distractors = [str(q.get(k, "")) for k in KEYS if k != "option_" + key_letter]

    for d in distractors:
        if d not in rel:
            errs.append(f"distractor {d!r} has no declared relation")
    for word, r in rel.items():
        if r not in RELATIONS:
            errs.append(f"{word!r}: unknown relation {r!r} (use one of {sorted(RELATIONS)})")
    if str(q.get("option_" + key_letter, "")) in rel:
        errs.append("the correct answer must not appear in 'relations'")

    kinds = [rel[d] for d in distractors if d in rel]
    if len(kinds) == 3 and len(set(kinds)) < min_distinct:
        errs.append(f"distractors are wrong in only {len(set(kinds))} different way(s) "
                    f"({', '.join(kinds)}) — they cohere, so the key is findable as the "
                    f"odd one out without knowing the target word")
    return errs


def relation_monotony(questions, group_of=by_topic, cap=0.5, min_group=10):
    """Fail a group that reaches for the same three relations every time.

    Individually every question can satisfy distractor_relation_errors while the batch as
    a whole runs one template — the same collapse the LR mechanism registry was built to
    stop.
    """
    errs = []
    for group, qs in _grouped(questions, group_of).items():
        combos = [tuple(sorted(set((q.get("relations") or {}).values()))) for q in qs]
        combos = [c for c in combos if c]
        if len(combos) < min_group:
            continue
        combo, n = collections.Counter(combos).most_common(1)[0]
        if n / len(combos) > cap:
            errs.append(f"[{group}]: {n} of {len(combos)} questions use the same relation "
                        f"set {list(combo)} — vary how the distractors are wrong")
    return errs


# ---------------------------------------------------------------- per-question basics
def options_distinct(q):
    """False if any two options are equal ignoring case and surrounding whitespace.

    TASK §7: no two options may be equivalent. This catches the textual half of that;
    it cannot see that `5(b-3)` and `5b-15` are the same value.
    """
    opts = [str(q.get(k, "")).strip().lower() for k in KEYS]
    return len(set(opts)) == 4
