#!/usr/bin/env python3
"""Finalise one reading_comprehension batch.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.rc_finalise <type> <NN> [--check-only]

`<type>` is a key of TYPES below — one per NSW Reading question type in the taxonomy
§3.1. Each type is its own `source_book`, so the review UI's source-book filter isolates
it, and each keeps its own MANIFEST and LOADED files.

    cloze       vocabulary cloze — a passage with 8 blanks       (built, 120/120)
    poetry      imagery, figurative language, mood, symbolism    (target 65)

Three things this enforces that the generic checks cannot:

1. THE PASSAGE IS THE SAME FOR EVERY QUESTION IN ITS GROUP. Eight rows carry eight copies
   of one passage; if one drifts, Selectly's passageId (a hash of the text) splits them
   into two groups and the student sees the passage twice.

2. THE PASSAGE AND THE QUESTIONS AGREE. For cloze, every marker in the passage has
   exactly one question and vice versa. For the comprehension types, every line a stem
   quotes must appear in the passage verbatim.

3. QUOTED TEXT IS CUT FROM THE PASSAGE BY THE BUILDER, never retyped, so it cannot
   disagree. It also makes the stems of one group textually distinct, which matters
   because phase 4 drops near-duplicate stems at 0.85 SILENTLY.

NSW is sat in Year 6, so this is pitched below the VIC verbal_reasoning bank (Year 8) —
see the taxonomy §3.4, which calls the difficulty gap deliberate.

WHY A GROUP IS N EXTRACTS, NOT ONE PASSAGE
------------------------------------------
Types 3.4 and 3.5 set two, three or four texts against each other. There is no room in
the schema for a second passage: `questions.passage` is one column, Selectly hashes it to
form `passageId`, and `push_to_selectly.py` prepends the whole thing to the stem. So a
multi-extract group is ONE passage string holding several labelled extracts, and the
group check verifies the labels are present and that enough items actually reach across
more than one of them — otherwise a paired set is single-passage comprehension wearing a
second text as decoration. `extract_labels` and `min_cross_extract` are that check.
Poetry and cloze are the N=1 case of the same model.
"""
import argparse
import collections
import json
import pathlib
import random
import re
import sqlite3
import sys
from difflib import SequenceMatcher

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.question_checks import (  # noqa: E402
    COMPREHENSION_RELATIONS,
    STRUCTURAL_RELATIONS,
    KEYS,
    RELATIONS,
    answer_shape_monotony,
    distractor_relation_errors,
    explanation_addresses_a_distractor,
    length_tell,
    doubled_token_errors,
    option_wording_errors,
    options_distinct,
    positional_reference,
    relation_monotony,
    unknown_words,
)
from tools.vr_finalise import AU_EXTRA  # noqa: E402

GEN = ROOT / "run_data/output/reading_comprehension/generated"
DB = ROOT / "run_data/db/qbank.db"
BLANK_RE = re.compile(r"_{2,} \((\d+)\) _{2,}")
# Two gap markers, one per cloze type. The vocabulary cloze blanks a WORD, so it uses
# `___ (n) ___`, which still looks like a blank; the structural cloze removes a whole
# SENTENCE, so `[ n ]` reads better there. Both survive markdown. The original
# `___(n)___` did not: underscores tight against content open emphasis, so `marked` in the
# review UI swallowed them and showed the reviewer a stray "(n)" with no blank in it,
# while Selectly -- which renders the passage as plain text -- showed it correctly.
# The reviewer's screen was the misleading one. See tools/repair_cloze_marker.py.
STRUCT_BLANK_RE = re.compile(r"\[ (\d+) \]")

# Names and everyday Australian words the system dictionary does not carry. The check
# exists to catch invented lookalike words and typos, not to police proper nouns.
RC_EXTRA = AU_EXTRA | {
    "texta", "letterbox", "letterboxes", "powerline", "powerlines", "downpipe",
    "downpipes", "gutter", "gutters", "anemone", "anemones", "rockpool", "spinifex",
    "wattle", "nan", "magpie", "magpies", "mustering", "paddock", "paddocks",
    "bushfire", "esky", "verandah", "jacaranda", "frangipani", "bindi", "wardrobe",
    "mould", "moulded", "reposition", "lifesaver", "lifesavers", "lifesaving", "ibis",
    "interchange", "footpath", "timetable", "wombat", "wombats", "intestine",
    "arborist", "arborists", "replant", "replanted", "replanting", "kilowatt",
    "breakwater", "groyne", "groynes", "hatchling", "hatchlings",
    "skilful", "skilfully", "coupe", "platypus", "petrakis",
    "unprofessionally", "unprofessional", "bushland", "lyrebird", "lyrebirds",
    "whipbird", "whipbirds", "rosella", "rosellas", "kookaburra", "kookaburras",
    "lantana", "vegemite", "muesli", "messaged", "beanbag", "beanbags",
    "saltbush", "bluebush", "nullarbor", "eucalypt", "eucalypts", "quarry",
    "handover", "postcode", "postcodes", "trampoline", "trampolines",
}

PARTS_OF_SPEECH = {"noun", "verb", "adjective", "adverb", "preposition", "conjunction",
                   "pronoun", "determiner"}

# The reading skills a comprehension item can test. Declared per question rather than
# inferred, for the same reason `pos` is declared on a cloze item: it is the thing the
# group check needs and it is not recoverable from the text.
SKILLS = {"imagery", "figurative_language", "mood", "symbolism", "inference",
          "vocabulary_in_context", "main_idea", "author_purpose", "structure",
          "comparison", "detail", "cause_effect",
          # structural cloze: the role the removed sentence plays in its paragraph. It
          # lives in `skill` so the per-passage spread check applies unchanged — four
          # gaps that all want a topic sentence test one thing four times.
          "topic_sentence", "supporting_detail", "example", "contrast",
          "transition", "conclusion"}

TYPES = {
    "cloze": {
        "book": "rc_nsw_cloze",
        "category": "vocabulary_cloze",
        "label": "Vocabulary cloze",
        "kind": "cloze",
        "target_passages": 17,
        "items_per_passage": (8, 8),
        "target_questions": 136,
        "relations": RELATIONS,
    },
    "structural": {
        "book": "rc_nsw_structural",
        "category": "structural_cloze",
        "label": "Structural cloze",
        "kind": "structural",
        "target_passages": 13,
        "items_per_passage": (4, 4),
        "target_questions": 52,
        "relations": STRUCTURAL_RELATIONS,
        "extract_labels": [],
        "min_cross_extract": 0,
        "min_skills_per_group": 3,
    },
    "single": {
        "book": "rc_nsw_single",
        "category": "single_passage",
        "label": "Single-passage comprehension",
        "kind": "set",
        "target_passages": 49,
        "items_per_passage": (4, 8),
        "target_questions": 292,
        "relations": COMPREHENSION_RELATIONS,
        "extract_labels": [],       # one unlabelled text
        "min_cross_extract": 0,
        "min_skills_per_group": 3,
    },
    "paired": {
        "book": "rc_nsw_paired",
        "category": "paired_extract",
        "label": "Paired-extract comparison",
        "kind": "set",
        "target_passages": 13,
        "items_per_passage": (4, 4),
        "target_questions": 52,
        "relations": COMPREHENSION_RELATIONS,
        "extract_labels": ["Text 1", "Text 2"],
        # Half the set must actually reach across both texts. Below that the second
        # extract is decoration and the item is single-passage comprehension that took
        # twice as long to write.
        "min_cross_extract": 2,
        "min_skills_per_group": 3,
    },
    "multi": {
        "book": "rc_nsw_multi",
        "category": "multi_extract",
        "label": "Multi-extract synthesis",
        "kind": "set",
        "target_passages": 13,
        "items_per_passage": (4, 4),
        "target_questions": 52,
        "relations": COMPREHENSION_RELATIONS,
        "extract_labels": ["Text 1", "Text 2", "Text 3"],
        # Higher than the paired type's 2. Synthesis IS the skill here — "which text best
        # supports this conclusion" is unanswerable from one extract — so a set with only
        # two crossing items is a single-passage set with two spare texts.
        "min_cross_extract": 3,
        "min_skills_per_group": 3,
    },
    "poetry": {
        "book": "rc_nsw_poetry",
        "category": "poetry",
        "label": "Poetry",
        "kind": "verse",
        "target_passages": 13,
        "items_per_passage": (5, 8),
        "target_questions": 65,
        "relations": COMPREHENSION_RELATIONS,
        "extract_labels": [],       # one text
        "min_cross_extract": 0,
        "min_skills_per_group": 3,
    },
}

BASE_REQUIRED = ["id", "subject", "stem", *KEYS, "correct_answer", "explanation", "topic",
                 "difficulty", "confidence", "source_book", "source_page",
                 "source_page_description", "passage", "figure_svg", "review_status",
                 "created_at", "relations", "passage_title"]


# --------------------------------------------------------------------- per-question
def validate(qs, nn, T):
    errs, seen_ids = [], set()
    required = BASE_REQUIRED + (["blank", "pos"] if T["kind"] == "cloze"
                                else ["skill", "quote_lines", "extracts"])
    if T["kind"] == "structural":
        required = required + ["blank"]
    for i, q in enumerate(qs):
        tag = (f"q[{i}] {q.get('passage_title', '?')} "
               + (f"blank {q.get('blank', '?')}" if T["kind"] == "cloze"
                  else f"item {q.get('skill', '?')}"))
        for f in required:
            if f not in q:
                errs.append(f"{tag}: missing field '{f}'")
        if q.get("subject") != "reading_comprehension":
            errs.append(f"{tag}: subject must be reading_comprehension")
        if q.get("correct_answer") not in ("A", "B", "C", "D"):
            errs.append(f"{tag}: bad correct_answer {q.get('correct_answer')!r}")
        if q.get("difficulty") not in ("medium", "hard"):
            errs.append(f"{tag}: bad difficulty {q.get('difficulty')!r}")
        if q.get("review_status") != "pending":
            errs.append(f"{tag}: review_status must be pending")
        if q.get("figure_svg") is not None:
            errs.append(f"{tag}: reading questions carry no figure")
        if not (q.get("passage") or "").strip():
            errs.append(f"{tag}: passage must be populated")
        if q.get("source_book") != T["book"]:
            errs.append(f"{tag}: source_book must be {T['book']}")
        if q.get("source_page") != nn:
            errs.append(f"{tag}: source_page must be {nn}")
        if not (isinstance(q.get("confidence"), (int, float)) and 0.0 <= q["confidence"] <= 1.0):
            errs.append(f"{tag}: confidence out of range")
        if q.get("id") in seen_ids:
            errs.append(f"{tag}: duplicate id")
        seen_ids.add(q.get("id"))
        if not options_distinct(q):
            errs.append(f"{tag}: options not distinct")
        for msg in doubled_token_errors(q) + option_wording_errors(q):
            errs.append(f"{tag}: {msg}")
        phrase = positional_reference(q.get("explanation"))
        if phrase:
            errs.append(f"{tag}: explanation names an option position ({phrase!r})")

        errs += [f"{tag}: {e}" for e in
                 distractor_relation_errors(q, vocabulary=T["relations"])]

        if T["kind"] == "cloze":
            errs += cloze_question_errors(q, tag)
        else:
            errs += set_question_errors(q, tag, T)
        if T["kind"] == "structural":
            errs += structural_question_errors(q, tag)

        # Words the passage itself uses are legitimate by definition — character names,
        # place names, Australian spellings. The check exists to catch a distractor
        # INVENTED to look like a real word, and an invented word is precisely the one
        # that will not appear in the passage. Maintaining a hand-written list of every
        # proper noun any future passage might use is a losing game.
        from_passage = {w.lower() for w in
                        re.findall(r"[A-Za-z][A-Za-z'-]*", q.get("passage") or "")}
        for k in KEYS:
            bad = unknown_words(q.get(k), extra_ok=RC_EXTRA | from_passage)
            if bad:
                errs.append(f"{tag}: option {q[k]!r} is not made of real words: {bad}")
        if len(str(q.get("explanation") or "").split()) < 8:
            errs.append(f"{tag}: explanation too thin — say why the key fits AND why the "
                        f"strongest distractor does not")

    errs += passage_group_errors(qs, T)
    pool = qs + bank_questions(nn, T)
    cat = T["category"]
    errs += answer_shape_monotony(pool, group_of=lambda q: cat)
    # floor on the POOL, not the batch: at n=20 the deviation around chance is ~0.10,
    # so a single batch drifts under any sensible floor by luck. The accumulated type
    # is where a systematic over-correction actually shows.
    errs += length_tell(pool, group_of=lambda q: cat, floor=0.12)
    # ALSO judge the batch on its own, and harder. The pooled check above compares a new
    # batch against everything already built, so a lean earlier batch can carry a biased
    # new one under the cap — p2 ran 11 of 20 while the pool sat at a comfortable 13 of
    # 40. A student never meets the pool: a reading drill set is whole passages, so one
    # batch is very close to one set, and 11 of 20 means "pick the longest option" scores
    # 55% against a 25% chance rate. 0.45 allows drift without allowing a systematic tell.
    errs += length_tell(qs, group_of=lambda q: f"batch p{nn}", cap=0.45)
    errs += relation_monotony([q for q in pool if q.get("relations")],
                              group_of=lambda q: cat)
    return errs


def cloze_question_errors(q, tag):
    errs = []
    if q.get("pos") not in PARTS_OF_SPEECH:
        errs.append(f"{tag}: pos must be one of {sorted(PARTS_OF_SPEECH)}, got "
                    f"{q.get('pos')!r} — §5 requires every option to be the same "
                    f"part of speech, so it is declared rather than guessed")
    # A cloze blank accepts any word that fits the sentence, so a distractor meaning
    # the same as the key will usually fit it too — a second correct answer rather
    # than a trap. Found by eye: "Funding for the programs is not ___" with key
    # 'secure' and distractor 'guaranteed', both of which read perfectly.
    for word, r in (q.get("relations") or {}).items():
        if r == "synonym":
            errs.append(f"{tag}: distractor {word!r} is declared 'synonym' — in a "
                        f"cloze a word meaning the same as the key normally fits the "
                        f"blank as well, giving two correct answers")
    return errs


def structural_question_errors(q, tag):
    """Rules specific to putting a removed sentence back.

    The key must be absent from the passage — it was cut out — and every option must be a
    whole sentence. An option that is a fragment while the other three are sentences is
    strikeable on sight, without reading the passage at all, which is the shape-level tell
    `length_tell` catches for length and nothing catches for grammar.
    """
    errs = []
    passage = q.get("passage") or ""
    key = str(q.get("option_" + str(q.get("correct_answer", "")).lower(), ""))
    if key and key in passage:
        errs.append(f"{tag}: the correct sentence is still present in the passage, so the "
                    f"gap was never actually cut")
    for k in KEYS:
        opt = str(q.get(k) or "").strip()
        if not opt:
            continue
        if not opt[0].isupper():
            errs.append(f"{tag}: option {opt[:40]!r} does not start as a sentence does")
        if opt[-1] not in ".!?":
            errs.append(f"{tag}: option {opt[:40]!r} has no sentence-ending punctuation — "
                        f"an option that is not a sentence is strikeable without reading "
                        f"the passage")
    return errs


def set_question_errors(q, tag, T):
    """Rules for a comprehension item — poetry, paired, multi-extract, structural."""
    errs = []
    if q.get("skill") not in SKILLS:
        errs.append(f"{tag}: skill must be one of {sorted(SKILLS)}, got {q.get('skill')!r}")

    # The defect this exists for: the cloze checks passed batches with two defensible
    # answers, and only reading them caught it. Making the author write down why the
    # strongest rival fails puts them in front of that comparison.
    problem = explanation_addresses_a_distractor(q)
    if problem:
        errs.append(f"{tag}: {problem}")

    passage = q.get("passage") or ""
    for line in q.get("quote_lines") or []:
        if line not in passage:
            errs.append(f"{tag}: the stem quotes {line[:50]!r}, which is not in the "
                        f"passage verbatim")

    # A quotation needs something to hang off. Written by hand, the lead-in keeps
    # acquiring the quote's own subject — "The passage says the spread \"A spread that had
    # failed...\"" — which reads as a stutter and, in the worst cases, as a broken
    # sentence. Six of those survived a full read of one batch, so the eye is not reliable
    # here. The word immediately before the opening quote must be a verb of saying, or the
    # quote must be introduced by a colon or comma.
    # A quotation needs something to hang off. Written by hand, the lead-in keeps
    # acquiring the quote's own subject — `The passage says the spread "A spread that had
    # failed..."` — which reads as a stutter or, at worst, as a broken sentence. Seven of
    # those survived a full read of one batch, so the eye is not reliable here.
    #
    # Two conditions together, because either alone gives false alarms. The word before
    # the quote must not be a legitimate introducer (a verb of saying, or a preposition
    # that takes the quote as its object — `The gap comes after "..."` is fine), AND the
    # quote must begin a fresh sentence. A quote that continues the lead-in's own clause
    # starts lower case and is grammatical whatever precedes it.
    INTRODUCES = {"says", "said", "say", "writes", "wrote", "states", "notes", "reports",
                  "explains", "begins", "ends", "opens", "closes", "continues",
                  "concludes", "asks", "adds", "admits", "records", "observes", "argues",
                  "describes", "includes", "lists", "quotes", "reads",
                  "after", "before", "as", "with", "than", "like", "about", "called",
                  "in", "of", "on", "at", "from", "between", "following"}
    opening = re.match(r'([^"]*)"(.)[^"]*"\s*(.?)', str(q.get("stem") or ""))
    if opening:
        lead, first, after = opening.group(1).rstrip(), opening.group(2), opening.group(3)
        words = re.findall(r"[A-Za-z']+", lead)
        # `The lines "..." mainly create a feeling of —` is an appositive and perfectly
        # grammatical. The tell is what comes AFTER the closing quote: a lower-case word
        # means the sentence carries on through the quotation.
        continues = after.islower()
        if (lead and not lead.endswith((":", ",", "—", "-")) and words and not continues
                and words[-1].lower() not in INTRODUCES and first.isupper()):
            errs.append(f"{tag}: the quotation is introduced by {lead[-32:]!r}, which "
                        f"leaves the stem ungrammatical — use a colon, a comma, or a "
                        f"verb of saying immediately before the quote")

    # Anything a stem puts in quotation marks must be in the passage, whether the builder
    # generated it or an author typed it. The generated ones cannot drift; a retyped
    # fragment can, and a stem quoting words the passage does not contain is unanswerable.
    for quoted in re.findall(r'"([^"]{4,})"', str(q.get("stem") or "")):
        # " ... " marks a deliberate jump between sentences; " / " is the ordinary way to
        # quote verse, where each line is separately checked against `quote_lines`.
        for piece in re.split(r" \.\.\. | / ", quoted):
            piece = piece.strip(" .,;:—-?!")
            if piece and piece not in passage:
                errs.append(f"{tag}: the stem quotes {piece[:55]!r} but the passage does "
                            f"not contain those words")

    labels = T.get("extract_labels") or []
    used = q.get("extracts") or []
    if labels:
        unknown = [e for e in used if e not in labels]
        if unknown:
            errs.append(f"{tag}: declares extract(s) {unknown} that this type does not "
                        f"define (known: {labels})")
        if not used:
            errs.append(f"{tag}: must declare which extract(s) it needs")
    elif used:
        errs.append(f"{tag}: this type has a single text, so 'extracts' must be empty")
    return errs


# --------------------------------------------------------------------- per-group
def passage_group_errors(qs, T):
    """A group is one passage text and the questions that depend on it."""
    errs = []
    groups = collections.defaultdict(list)
    for q in qs:
        groups[q.get("passage_title")].append(q)

    lo, hi = T["items_per_passage"]
    for title, group in groups.items():
        texts = {q.get("passage") for q in group}
        if len(texts) != 1:
            errs.append(f"[{title}]: the {len(group)} questions carry {len(texts)} "
                        f"different passage texts — Selectly groups by a hash of the "
                        f"passage, so they would split into separate passages")
            continue
        passage = texts.pop() or ""

        if T["kind"] == "cloze":
            errs += passage_markup_errors(title, passage)
            errs += cloze_group_errors(title, group, passage, hi)
            continue
        if T["kind"] == "structural":
            errs += cloze_group_errors(title, group, passage, hi, STRUCT_BLANK_RE)

        if not lo <= len(group) <= hi:
            errs.append(f"[{title}]: {len(group)} questions, expected {lo}–{hi} "
                        f"(taxonomy §3.4: each passage carries 4–8 linked questions)")

        skills = {q.get("skill") for q in group}
        need = T.get("min_skills_per_group", 3)
        if len(skills) < need:
            errs.append(f"[{title}]: the {len(group)} questions test only {len(skills)} "
                        f"distinct skill(s) {sorted(s for s in skills if s)} — a passage "
                        f"asked {len(group)} times about one skill is one question")

        errs += passage_markup_errors(title, passage)
        if T["kind"] == "verse":
            errs += verse_line_errors(title, passage)

        for label in T.get("extract_labels") or []:
            if label not in passage:
                errs.append(f"[{title}]: the passage does not contain the extract "
                            f"heading {label!r}")
            elif f"{label}  \n" not in passage:
                errs.append(f"[{title}]: the heading {label!r} has no markdown hard break "
                            f"after it, so the review UI runs it into the first sentence "
                            f"of the extract and the label disappears")
        need_cross = T.get("min_cross_extract", 0)
        if need_cross:
            cross = sum(1 for q in group if len(q.get("extracts") or []) > 1)
            if cross < need_cross:
                errs.append(f"[{title}]: only {cross} of {len(group)} questions reach "
                            f"across more than one extract, need {need_cross} — "
                            f"otherwise this is single-passage comprehension with a "
                            f"second text attached for decoration")
    return errs


def cloze_group_errors(title, group, passage, blanks_per_passage, marker=BLANK_RE):
    errs = []
    in_passage = [int(n) for n in marker.findall(passage)]
    asked = [q.get("blank") for q in group]

    if sorted(in_passage) != list(range(1, len(in_passage) + 1)):
        errs.append(f"[{title}]: blanks in the passage are numbered {in_passage} — "
                    f"expected 1..{len(in_passage)} with no gaps or repeats")
    if sorted(asked) != sorted(in_passage):
        errs.append(f"[{title}]: passage has blanks {sorted(in_passage)} but the "
                    f"questions ask about {sorted(asked)}")
    if len(in_passage) != blanks_per_passage:
        errs.append(f"[{title}]: {len(in_passage)} blanks, expected "
                    f"{blanks_per_passage} (TASK §5)")

    # The stem must quote the passage, not a retyped approximation of it.
    for q in group:
        frag = q.get("stem_fragment")
        if frag and frag not in passage:
            errs.append(f"[{title}] blank {q.get('blank')}: the quoted fragment is "
                        f"not in the passage verbatim")
    return errs


# Only markup that would actually PARSE. An underscore run counts as an emphasis
# delimiter in markdown solely when it sits at a word boundary and is followed by
# non-space — which is why `___(1)___` was eaten and `___ (1) ___` is left alone. A
# blunter `__` pattern would fail every cloze passage for a marker that renders fine.
# Markup that would actually PARSE, which means an emphasis PAIR: an opening delimiter
# with content tight against it and a matching closer with content tight against that.
# A one-sided test is not enough — `___ (2) ___.` has a run followed by a full stop and
# `marked` leaves it completely alone, so flagging it would fail every cloze passage for
# a marker that renders correctly. Checked against the same marked build the review UI
# loads: `___(1)___` parses, `___ (1) ___` does not.
MARKUP_RE = re.compile(r"(\*\*|___|__)(?=[^\s*_])[^\n]*?(?<=[^\s*_])\1"
                       r"|^#{1,6} |^\s*\|.*\|\s*$", re.M)


def passage_markup_errors(title, passage):
    """A passage may not carry markdown, because only one of the two readers parses it.

    The review UI runs the passage through `marked.parse`, so markup looks right there.
    Selectly does not: `McqQuestion.tsx` splits the passage back out of the stem and puts
    it in a `white-space: pre-wrap` div as plain text, so a student is shown the
    asterisks of `**Tank Stand**` exactly as written. Checking the reviewer's screen
    would never reveal it — the two surfaces disagree, and the student's is the one that
    matters. Line breaks are safe in both: pre-wrap honours the newline, and the two
    trailing spaces are invisible.
    """
    m = MARKUP_RE.search(passage or "")
    if not m:
        return []
    return [f"[{title}]: the passage contains markdown ({m.group(0).strip()!r}) — the "
            f"review UI parses it but Selectly shows it to the student verbatim"]


def verse_line_errors(title, passage):
    """A poem whose line breaks are lost is a paragraph, and a different question.

    The review UI renders the passage with `marked.parse` and does not set `breaks`, so a
    single newline collapses to a space and the poem arrives as prose. Two trailing
    spaces is markdown's hard line break; it is also invisible wherever the passage is
    handled as plain text, which is what `push_to_selectly.py` does with it.
    """
    errs = []
    lines = passage.split("\n")
    for i, line in enumerate(lines[:-1]):
        nxt = lines[i + 1]
        if line.strip() and nxt.strip() and not line.endswith("  "):
            errs.append(f"[{title}]: verse line {line.strip()[:40]!r} has no markdown "
                        f"hard break (two trailing spaces), so it will render joined to "
                        f"the next line as prose")
    return errs


# --------------------------------------------------------------------- bank and batches
def bank_questions(skip_nn, T):
    """Everything the batch-quality checks should be judged against.

    DB rows plus EVERY batch file for this book, loaded or not, deduplicated by id with
    the file winning. The files are not redundant with the DB: `relations` has no column,
    so once a batch is loaded its declared distractor design survives only in its file.
    Judging relation variety against unloaded batches alone would shrink the pool to the
    batch in hand as the build progresses — the check would tighten from 'is this bank
    varied' to 'is this batch varied' without anyone deciding that it should.
    """
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute(
        "SELECT * FROM questions WHERE subject='reading_comprehension' "
        "AND NOT (source_book=? AND source_page=?)", (T["book"], skip_nn))]
    from_files = []
    for f in sorted(GEN.glob(f"{T['book']}_p*.json")):
        if int(re.search(r"_p(\d+)\.json$", f.name).group(1)) != skip_nn:
            from_files += json.loads(f.read_text(encoding="utf-8"))
    seen = {q.get("id") for q in from_files}
    return from_files + [r for r in rows if r.get("id") not in seen]


def loaded_set(T):
    path = GEN / f"{T['book']}_LOADED.json"
    if not path.exists():
        return set()
    names = json.loads(path.read_text(encoding="utf-8"))
    return {int(m.group(1)) for m in (re.search(r"_p(\d+)\.json$", n) for n in names) if m}


def other_batches(skip_nn, T):
    done = loaded_set(T)
    out = []
    for f in sorted(GEN.glob(f"{T['book']}_p*.json")):
        n = int(re.search(r"_p(\d+)\.json$", f.name).group(1))
        if n not in done and n != skip_nn:
            out.append(f)
    return out


def near_duplicates(qs, nn, T, threshold=0.82):
    con = sqlite3.connect(DB)
    existing = [r[0] for r in con.execute(
        "SELECT stem FROM questions WHERE subject='reading_comprehension' "
        "AND NOT (source_book=? AND source_page=?)", (T["book"], nn)) if r[0]]
    for f in other_batches(nn, T):
        existing += [x["stem"] for x in json.loads(f.read_text(encoding="utf-8"))]
    errs, batch = [], []
    for q in qs:
        low = q["stem"].lower()
        for prev in batch + existing:
            r = SequenceMatcher(None, low, prev.lower()).ratio()
            if r >= threshold:
                errs.append(f"{q.get('passage_title')}: stem "
                            f"{r:.3f} similar to {prev[:70]!r} — phase 4 would drop it")
                break
        batch.append(q["stem"])
    return errs


def running_counts(skip_nn, T):
    c = collections.Counter()
    con = sqlite3.connect(DB)
    for a, n in con.execute("SELECT correct_answer, COUNT(*) FROM questions "
                            "WHERE source_book=? GROUP BY 1", (T["book"],)):
        c[a] += n
    for f in other_batches(skip_nn, T):
        for q in json.loads(f.read_text(encoding="utf-8")):
            c[q["correct_answer"]] += 1
    return c


def recompute_manifest(current_nn, current_qs, T):
    titles = set()
    con = sqlite3.connect(DB)
    for (d,) in con.execute("SELECT source_page_description FROM questions "
                            "WHERE source_book=? AND source_page != ?",
                            (T["book"], current_nn)):
        m = re.search(r"\[passage: ([^\]]+)\]", d or "")
        if m:
            titles.add(m.group(1))
    n_loaded = con.execute("SELECT COUNT(*) FROM questions WHERE source_book=? "
                           "AND source_page != ?", (T["book"], current_nn)).fetchone()[0]
    n = n_loaded + len(current_qs)
    for f in other_batches(current_nn, T):
        batch = json.loads(f.read_text(encoding="utf-8"))
        titles |= {q["passage_title"] for q in batch}
        n += len(batch)
    titles |= {q["passage_title"] for q in current_qs}
    return {"passages": len(titles), "target_passages": T["target_passages"],
            "questions": n, "target_questions": T["target_questions"],
            "titles": sorted(titles)}


# --------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("type", choices=sorted(TYPES), help="NSW Reading question type")
    ap.add_argument("nn", type=int, help="batch number")
    ap.add_argument("--check-only", action="store_true",
                    help="validate without rebalancing keys or rewriting the file")
    args = ap.parse_args()

    T = TYPES[args.type]
    nn = args.nn
    path = GEN / f"{T['book']}_p{nn}.json"
    qs = json.loads(path.read_text(encoding="utf-8"))

    errs = validate(qs, nn, T) + near_duplicates(qs, nn, T)
    if errs:
        print(f"VALIDATION FAILED ({len(errs)}):")
        for e in errs:
            print("  -", e)
        sys.exit(1)

    if args.check_only:
        print(f"OK (check-only) {T['book']}_p{nn}: {len(qs)} questions, "
              f"{len({q['passage_title'] for q in qs})} passages")
        return

    rng = random.Random(nn * 3571)
    counts = running_counts(nn, T)
    for q in qs:
        opts = [q[k] for k in KEYS]
        correct = opts[ord(q["correct_answer"]) - 65]
        others = [o for i, o in enumerate(opts) if i != ord(q["correct_answer"]) - 65]
        rng.shuffle(others)
        tgt = min("ABCD", key=lambda L: (counts[L], rng.random()))
        new = others[:]
        new.insert(ord(tgt) - 65, correct)
        assert sorted(map(str, new)) == sorted(map(str, opts))
        assert new[ord(tgt) - 65] == correct
        for k, v in zip(KEYS, new):
            q[k] = v
        q["correct_answer"] = tgt
        counts[tgt] += 1
        if "[passage:" not in q["source_page_description"]:
            q["source_page_description"] += f" [passage: {q['passage_title']}]"

    path.write_text(json.dumps(qs, indent=2, ensure_ascii=False), encoding="utf-8")
    manifest = recompute_manifest(nn, qs, T)
    GEN.mkdir(parents=True, exist_ok=True)
    (GEN / f"{T['book']}_MANIFEST.json").write_text(
        json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8")

    npass = len({q["passage_title"] for q in qs})
    nhard = sum(1 for q in qs if q["difficulty"] == "hard")
    print(f"OK {T['book']}_p{nn}: {len(qs)} q across {npass} passages, {nhard} hard")
    print(f"batch keys  { {a: sum(1 for q in qs if q['correct_answer'] == a) for a in 'ABCD'} }")
    print(f"running keys {dict(sorted(counts.items()))}")
    print(f"  passages {manifest['passages']}/{manifest['target_passages']}  "
          f"questions {manifest['questions']}/{manifest['target_questions']}")


if __name__ == "__main__":
    main()
