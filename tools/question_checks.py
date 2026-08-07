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
def length_tell(questions, group_of=by_topic, cap=0.6, min_group=5, floor=None):
    """Fail a group where the correct answer's length predicts it either way.

    "Pick the longest option" is the oldest multiple-choice shortcut there is, and a
    precise, fully qualified key sitting beside three short distractors hands it over.
    The LR bank once scored 32 out of 32 on that heuristic across its four judgement
    categories — every question individually sound, the set collectively useless as a
    test of reasoning. Cheap to measure, invisible to every other check here.

    `floor` catches the same exploit running backwards. Over-correcting until the key is
    NEVER the longest is not neutral: striking out the longest option then eliminates a
    distractor almost every time, which lifts a blind guess from one in four to one in
    three. Chance for a four-option item is 0.25, so a healthy group sits near it rather
    than at either extreme.

    Use `floor` only on a pool big enough to mean something. At n=20 the standard
    deviation around chance is about 0.10, so a single batch will wander below any
    sensible floor by luck alone; an accumulated type of 50+ is a fair test.
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
        elif floor is not None and n / len(flags) < floor:
            errs.append(f"[{group}]: the correct answer is the longest option in only {n} "
                        f"of {len(flags)} — over-corrected. Striking the longest option "
                        f"now eliminates a distractor almost every time, which is worth "
                        f"as much to a guesser as the tell it replaced")
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
    "synonym",        # means the SAME as the target — the standard trap in an antonym
                      # question, where the key is the opposite and a synonym is the
                      # answer a student gives when they read the question too fast
    "nuance",         # related meaning, wrong shade or degree
    "form",           # looks or sounds like the target (curtail / cultivate)
    "domain",         # same subject area, unrelated meaning
    "collocation",    # commonly appears beside the target, means something else
    "overreach",      # right direction, too absolute
}

# The vocabulary above describes how one WORD is wrong beside another word, which is the
# right axis for a synonym, antonym or cloze item. It cannot describe how a whole
# proposition about a text is wrong, so a comprehension item declared against it collapses
# to "nuance" for everything and the coherence rule stops biting.
#
# These are the ways a comprehension option is wrong. They are also the ways a student
# gets a comprehension question wrong, which is the point: three distractors drawn from
# three different rows here catch three different misreadings, and no one of them is the
# obvious odd one out.
COMPREHENSION_RELATIONS = {
    "contradicts",        # says the opposite of what the text says
    "unsupported",        # could be true, but the text offers nothing either way
    "overreach",          # the right reading pushed past what the text will carry
    "literal",            # takes a figurative expression at face value — the standard
                          # poetry trap, and the one Year 6 candidates fall for most
    "wrong_sense",        # a real but wrong dictionary sense of a word in the text
    "wrong_focus",        # true of a different part of the text, or in a paired or
                          # multi-extract set, true of a different extract
    "outside_knowledge",  # true of the world, but not something the text establishes
    "half_right",         # a correct observation attached to the wrong reason or effect
}


# A third axis, for the structural/organisation cloze: a sentence has been cut out of a
# passage and must be put back. Here a wrong option is rarely wrong ABOUT anything — it can
# be perfectly true and still be the wrong sentence, because what fails is cohesion. The
# comprehension vocabulary cannot express that: "redundant" and "broken_reference" are not
# claims about the world at all, they are claims about the seam between two sentences.
#
# These double as the reason the item is worth asking. A student who can say why the
# repeat is wrong, and why the true-but-unconnected sentence is wrong, is reading for
# structure — which is the whole point of the type.
STRUCTURAL_RELATIONS = {
    "broken_reference",   # the NEXT sentence's "it"/"them"/"forty minutes" loses what it
                          # points back to — the commonest real failure, and invisible
                          # unless the student reads past the gap
    "redundant",          # says again what a neighbouring sentence already said
    "wrong_order",        # belongs in the passage, but at a different point
    "off_topic",          # true and new, but the paragraph never takes it up
    "too_general",        # the right idea at too high an altitude to set up what follows
    "too_specific",       # a detail where the slot needs a claim
    "wrong_connective",   # "However" where the logic runs on, or the reverse
    "contradicts",        # states the opposite of what the passage establishes
}


def distractor_relation_errors(q, min_distinct=3, vocabulary=RELATIONS):
    """Check a question's declared distractor relations.

    `relations` maps each DISTRACTOR TEXT to one of `vocabulary`. Keyed by text, not by
    option letter, so it survives the answer shuffle. Pass COMPREHENSION_RELATIONS for
    items about a text rather than about a word.
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
        if r not in vocabulary:
            errs.append(f"{word!r}: unknown relation {r!r} (use one of {sorted(vocabulary)})")
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


# ------------------------------------------------- the explanation must discharge a rival
# The defect this exists for: on the vocabulary-cloze build every mechanical check passed
# batches that had TWO defensible answers, and only reading them caught it. An author who
# is made to write down why the strongest rival fails has to look at the rival, and that
# is the moment the second defensible answer becomes visible. A word-count floor does not
# force that — you can write eighty words about the key alone.
#
# So: the explanation must name a distractor, in the distractor's own words. Mechanical,
# and it puts the author in front of the exact comparison that was being skipped.
_RUN_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "of", "to", "in", "on", "at", "by", "for",
    "with", "is", "are", "was", "were", "be", "been", "it", "its", "that", "this",
    "as", "from", "has", "have", "had", "not", "no", "so", "than", "then", "there",
}


def _words(text):
    return re.findall(r"[a-z']+", str(text or "").lower())


def _longest_shared_run(a_words, b_words):
    """Longest run of consecutive words appearing in both sequences."""
    best, best_run = 0, []
    prev = [0] * (len(b_words) + 1)
    for i, wa in enumerate(a_words, 1):
        cur = [0] * (len(b_words) + 1)
        for j, wb in enumerate(b_words, 1):
            if wa == wb:
                cur[j] = prev[j - 1] + 1
                if cur[j] > best:
                    best, best_run = cur[j], a_words[i - cur[j]:i]
        prev = cur
    return best, best_run


def explanation_addresses_a_distractor(q, min_run=3):
    """Return an error if the explanation never quotes any distractor back.

    A short distractor is matched whole; a long one needs `min_run` consecutive words in
    common, at least one of which carries meaning — otherwise 'the poet is' would let a
    key-only explanation through.
    """
    expl = _words(q.get("explanation"))
    if not expl:
        return "explanation is empty, so it cannot say why the strongest rival fails"

    key_letter = str(q.get("correct_answer", "")).strip().lower()
    distractors = [str(q.get(k, "")) for k in KEYS if k != "option_" + key_letter]

    for d in distractors:
        dw = _words(d)
        if not dw:
            continue
        if len(dw) <= 2:
            if _longest_shared_run(expl, dw)[0] == len(dw):
                return None
            continue
        n, run = _longest_shared_run(expl, dw)
        if n >= min_run and any(w not in _RUN_STOPWORDS for w in run):
            return None
    return ("the explanation never quotes a distractor back — say in its own words why "
            "the strongest rival fails, or a second defensible answer goes unnoticed")


# ---------------------------------------------------------------- real words
# A distractor invented to look like the target ("mimec" for 'mimic') is not a distractor
# at all: a student who has never met the target word can still strike it out on sight,
# and a marker reads it as a typo. Caught by eye once; this stops it recurring.
_WORDLIST_PATH = "/usr/share/dict/words"
_AU_TO_US = [("our", "or"), ("ise", "ize"), ("isa", "iza"), ("yse", "yze"),
             ("re", "er"), ("ence", "ense"), ("ogue", "og"), ("ll", "l"),
             # 'apologising' has no "ise" in it to swap, so the -ing and -ation forms
             # need their own entries or every Australian participle is reported
             ("ising", "izing"), ("isation", "ization"), ("ised", "ized")]


def _load_wordlist(path=_WORDLIST_PATH):
    try:
        with open(path, encoding="latin-1") as fh:
            return {w.strip().lower() for w in fh if w.strip()}
    except OSError:
        return set()


_WORDS = None


def _known(word, vocab):
    """The list is American English; we write Australian, so try the usual swaps."""
    w = word.lower().strip("'")
    # A possessive is the same word: "Ravi's" is known if "Ravi" is. Without this, every
    # possessive of a name a passage legitimately uses is reported as invented.
    if w.endswith("'s"):
        w = w[:-2]
    if not w or w in vocab or w.rstrip("s") in vocab:
        return True
    for au, us in _AU_TO_US:
        if au in w and (w.replace(au, us) in vocab or w.replace(au, us).rstrip("s") in vocab):
            return True
    return False


def unknown_words(text, extra_ok=()):
    """Words in `text` that are not in the system dictionary.

    Hyphenated compounds are checked part by part, so 'up-to-date' and 'hand-made' pass.
    Returns [] when no wordlist is installed rather than failing every batch.
    """
    global _WORDS
    if _WORDS is None:
        _WORDS = _load_wordlist()
    if not _WORDS:
        return []
    ok = _WORDS | {w.lower() for w in extra_ok}
    bad = []
    for token in re.findall(r"[A-Za-z][A-Za-z'-]*", str(text or "")):
        parts = [p for p in token.split("-") if p]
        if not all(_known(p, ok) for p in parts):
            bad.append(token)
    return bad


# ---------------------------------------------------------------- leaked working
# The generating model's scratchpad ending up in the explanation field. TASK §7: "Write it
# clean — never leak working, self-correction, or 'wait, let me recheck'." Found in 139
# shipped questions (137 QR, 2 SR), 12 of them already approved and serving students:
#
#   "= 526.8 km. Oh, wait. The service station is 3/5 of the way..."
#   "Area = 0.5 * 80 * 45 = 1800. Wait. ... Why did I select B? Let me recheck the options."
#
# The second form matters more than the first: where the model argues with itself about
# which option is right, the stored correct_answer cannot be trusted either, so these need
# the answer re-derived rather than the prose tidied.
LEAKED_WORKING = re.compile(
    # "Oh, wait." needs the optional comma — without it the sweep missed exactly the
    # phrasing that made this defect obvious in the first place.
    r"(^|[.!?;:—–]\s*|\bo[hf],?\s+)wait\b"
    r"|let me (re-?check|re-?read|reconsider|recompute|re-?do|verify that|think)"
    r"|\bwhy did i\b|\bi initially\b|\bmy (mistake|apologies)\b"
    r"|\bhold on\b|\bscratch that\b|\bon second thought\b"
    r"|\blet'?s re-?(check|read|do|compute)\b"
    r"|\bactually,\s*(i|let me|the answer)\b|\bcorrection:",
    re.I | re.M)

# Phrases where the model is arguing with itself about WHICH OPTION is correct. An
# explanation carrying one of these casts doubt on the stored key, not just the prose.
DISPUTED_KEY = re.compile(
    r"\bwhy did i\b|\bre-?check the options\b|\bthe option is\b"
    r"|\bi (chose|selected|picked)\b|\bshould be option\b", re.I)


def leaked_working(text):
    """Return the offending phrase if an explanation shows the model's own working."""
    m = LEAKED_WORKING.search(str(text or ""))
    return m.group(0).strip() if m else None


def disputes_its_own_key(text):
    """True if the explanation argues with itself about which option is right."""
    return bool(DISPUTED_KEY.search(str(text or "")))


# ---------------------------------------------------------------- per-question basics
def options_distinct(q):
    """False if any two options are equal ignoring case and surrounding whitespace.

    TASK §7: no two options may be equivalent. This catches the textual half of that;
    it cannot see that `5(b-3)` and `5b-15` are the same value.
    """
    opts = [str(q.get(k, "")).strip().lower() for k in KEYS]
    return len(set(opts)) == 4
