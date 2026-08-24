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
import math
import re
from fractions import Fraction

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
            longest = max(lens.values())
            # Strictly longest, not merely tied for it. A key that ties with a distractor
            # hands a guesser nothing, and `max` breaks ties toward A — which is exactly
            # where every builder parks the key before the finaliser shuffles, so ties
            # were being counted as a tell in the one place they cannot be one.
            key_len = lens.get(str(q.get("correct_answer")), -1)
            flags.append(key_len == longest
                         and sum(1 for v in lens.values() if v == longest) == 1)
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
    r"\b(the (first|last) (two|three|four)"
    r"(?! (statements?|sentences?|premises?|stanzas?|lines?|paragraphs?|paras?))|"
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

    # `_words` keeps only alphabetic tokens, so a purely numeric or symbolic option --
    # "4/5", "$24", "38 cm" -- reduces to nothing and can never be "quoted back". Before
    # this guard the check fired on essentially every numeric question in the bank: 579
    # hits per 1000 on VIC and 473 on NSW, which is not a difference between banks, it is
    # the check reporting that arithmetic questions have numbers for options. Where no
    # distractor carries a word, the check does not apply.
    if not any(_words(d) for d in distractors):
        return None

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
    r"|\bhold on\b(?!\s+to\b)|\bscratch that\b|\bon second thought\b"
    r"|\blet'?s re-?(check|read|do|compute)\b"
    r"|\bactually,\s*(i|let me|the answer)\b|\bcorrection:"
    # A bare "Actually 1090/6 = 181.6" carries the same failure and matched none of the
    # above, which is how 13 questions survived the August sweep. Same for the recalculate
    # and re-examine spellings, and for "hmm" -- a model does not say hmm to a student.
    r"|\bactually\b\s*[0-9(]|\blet me (re-?calculate|re-?examine|try)\b"
    r"|\bre-?examine:|\bhmm\b|\bclosest (?:answer|option) is\b",
    re.I | re.M)

# The worst class, and the one the August sweep had no word for: the model could not make
# the question it had just written work, so it rewrote the question INSIDE the explanation
# while the stem and options on disk stayed broken. Every match found so far was
# unanswerable as stored, so this is a rejection signal, not a prose-cleanup signal.
REWRITES_THE_QUESTION = re.compile(
    r"\bre-?setting (?:the )?options\b|\bi'?ll (?:just )?(?:set|redesign|use)\b"
    r"|\bredesign(?:ing)? (?:the )?question\b|\bchange to:|\blet me redesign\b"
    r"|\bso use (?:total|the) \b|\bi need the .{0,40} to sum to\b",
    re.I)

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


def rewrites_the_question(text):
    """Return the offending phrase if the explanation edits the question instead of
    answering it. Treat a hit as "this question has no correct answer", not as a typo."""
    m = REWRITES_THE_QUESTION.search(str(text or ""))
    return m.group(0).strip() if m else None


# ---------------------------------------------------------------- per-question basics
def options_distinct(q):
    """False if any two options are equal ignoring case and surrounding whitespace.

    TASK §7: no two options may be equivalent. This catches the textual half of that;
    it cannot see that `5(b-3)` and `5b-15` are the same value.
    """
    opts = [str(q.get(k, "")).strip().lower() for k in KEYS]
    return len(set(opts)) == 4


def doubled_token_errors(q):
    """Options where a word or possessive is repeated back to back: "the the dog", "Yan's's".

    This is not a typo class — it is the signature of a formatter applied to text that
    already carries what the formatter adds. A builder that writes `fmt=lambda v: f"the
    {v}"` gets a clean key, because the key is the bare computed value, and three broken
    distractors, because those were written out in full. The key therefore stays the only
    well-formed option, which hands the answer to any student who notices.

    It has happened three times in this build (`the the bird`, `Yan's's`, and the
    `1st`/`second` mapping that crashed rather than shipping), always the same way, so it
    is screened here rather than left to whoever reads the batch.
    """
    bad = []
    for k in KEYS:
        text = str(q.get(k, "") or "")
        if re.search(r"'s's\b", text):
            bad.append(f"{k}: doubled possessive in {text!r}")
            continue
        words = text.lower().split()
        for a, b in zip(words, words[1:]):
            if a == b and a.isalpha():
                bad.append(f"{k}: doubled word {a!r} in {text!r}")
                break
    return bad


def option_wording_errors(q):
    """Malformed ordinals in options: "the 22th".

    Not a typo but formatter output applied without regard to the value it received —
    `f"the {n}th"` is right for 29 and wrong for 22. Same family as doubled_token_errors,
    and invisible to every check that looks at meaning rather than at the rendered string.

    An a/an check was written alongside this and REMOVED. Swept over the whole bank it
    flagged 22 options and only 2 were real: "a and b" and "a as" are algebra variables,
    "an L" is a unit, and "a eucalypt" is correct English because the vowel is sounded
    "yoo". Two hits in twenty is not a check, it is noise that teaches you to skim the
    output, which costs more than the two it would catch.
    """
    bad = []
    for k in KEYS:
        for num, suffix in re.findall(r"(\d+)(st|nd|rd|th)\b", str(q.get(k, "") or "")):
            n = int(num)
            want = ("th" if 11 <= n % 100 <= 13
                    else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th"))
            if suffix != want:
                bad.append(f"{k}: {num}{suffix} should be {num}{want}")
    return bad


# ---------------------------------------------------------------- retrieval disguised as inference
# An "inference" item whose key restates one passage sentence is a retrieval item wearing
# an inference stem. 37% of the ACT reading bank's implies/suggests questions do exactly
# that, and it is the defect vic_reading_TASK.md §3 exists to prevent reintroducing.
#
# The threshold is fitted, not guessed. 40 ACT reading questions were hand-labelled
# retrieval or inference; content-word overlap between the key and the passage averaged
# 0.53 for retrieval against 0.19 for inference, and 0.35 was the decision boundary that
# maximised agreement — 82% accuracy, 95% precision on the retrieval side.
_RESTATE_STOP = frozenset("""
the a an of and or to in is are was were for with on at by that this it its as be been
from which who what not their they them then than there these those has have had will
would could should may might can do does did but if so such other more most some any
""".split())


def _content_words(text):
    return {w for w in re.findall(r"[a-z]+", str(text or "").lower())
            if len(w) > 3 and w not in _RESTATE_STOP}


def key_overlap_with_passage(question):
    """Fraction of the key's content words that also appear in the passage."""
    key = question.get("option_" + str(question.get("correct_answer", "")).lower())
    kw = _content_words(key)
    if not kw:
        return 0.0
    return len(kw & _content_words(question.get("passage"))) / len(kw)


def key_restates_passage(question, threshold=0.35):
    """Return an error if a non-retrieval item's key merely restates the passage.

    Pass `threshold=None` on items deliberately written as access-and-retrieve (§4.1
    wants 20% of them) — there the key SHOULD echo the text, and the honest fix is a
    retrieval stem, not a reworded key.
    """
    if threshold is None:
        return None
    ov = key_overlap_with_passage(question)
    if ov >= threshold:
        return (f"key repeats {100 * ov:.0f}% of its content words from the passage "
                f"(limit {100 * threshold:.0f}%) — this is retrieval, not inference; "
                f"either rewrite the key as a synthesis or label the item retrieval")
    return None

_LOWEST_TERMS = re.compile(
    r"lowest terms|simplest form|simplif|fully reduce|in its simplest", re.I)


def _numeric_value(text):
    """Parse an option that is a plain number or a bare fraction; None otherwise."""
    t = str(text).strip().replace("$", "").replace(",", "").replace("%", "")
    m = re.fullmatch(r"(-?\d+)\s*(?:/|out of)\s*(\d+)", t, re.I)
    if m:
        d = int(m.group(2))
        return None if d == 0 else Fraction(int(m.group(1)), d)
    # Surds, but only where the root comes out whole: "2\u221a25" is 10 and reads as a
    # different answer from "10" while being the same number. A blind-solve disagreement
    # in vic-drill-mq-017 was exactly that pair. Irrational roots are left alone -- they
    # cannot collide with a rational option, and comparing them as floats would invite
    # false positives.
    m = re.fullmatch(r"(-?\d*)\s*(?:\u221a|sqrt)\s*\(?\s*(\d+)\s*\)?", t)
    if m:
        root = math.isqrt(int(m.group(2)))
        if root * root != int(m.group(2)):
            return None
        c = m.group(1)
        return Fraction((-1 if c == "-" else 1) * (int(c.lstrip("-") or 1)) * root)
    return Fraction(t) if re.fullmatch(r"-?\d+(?:\.\d+)?", t) else None


def options_distinct_by_value(q):
    """Two options that read differently but ARE the same number.

    `options_distinct` compares option strings, so it cannot see 4/13 beside 16/52,
    or 5/3 beside 10/6. When the duplicate involves the key the question has two
    correct answers and marks one of them wrong; when it is between distractors a
    solver eliminates both for free, since neither can be the key.

    Stems asking for lowest terms or simplest form are exempt: there the unreduced
    equivalent is the point of the question, and exactly one option satisfies the
    instruction.
    """
    if _LOWEST_TERMS.search(q.get("stem", "") or ""):
        return None
    seen = {}
    for L in "abcd":
        v = _numeric_value(q.get("option_" + L))
        if v is not None:
            seen.setdefault(v, []).append(L.upper())
    dup = [ls for ls in seen.values() if len(ls) > 1]
    if not dup:
        return None
    key = (q.get("correct_answer") or "").upper()
    keyed = any(key in ls for ls in dup)
    pairs = "; ".join("/".join(ls) for ls in dup)
    return (f"options {pairs} have the same VALUE though different text"
            + (" — and one of them is the key, so the question has two correct "
               "answers" if keyed else ""))


_LINE_EQ = re.compile(r"y\s*=\s*(-)?\s*(\d+(?:\.\d+)?)?\s*x\s*([+-]\s*\d+)?")
_POINT = re.compile(r"^\(\s*(-)?(\d+(?:\.\d+)?)\s*,\s*(-)?(\d+(?:\.\d+)?)\s*\)$")


def one_point_on_the_line(q):
    """"Which point lies on y = 2x - 3?" must have exactly one option that does.

    vic-drill-mq-020 offered both (2, 1) and (1, -1), and both satisfy it. That is not
    a duplicate VALUE -- the two options are different points -- so
    options_distinct_by_value cannot see it; only substituting into the line can.
    Blind-solve picked the option that was not keyed and was equally right.
    """
    stem = (q.get("stem") or "").replace("\u2212", "-")
    if "lies on" not in stem or "line" not in stem:
        return None
    m = _LINE_EQ.search(stem)
    if not m:
        return None
    grad = float(m.group(2) or 1) * (-1 if m.group(1) else 1)
    inter = float((m.group(3) or "0").replace(" ", ""))
    on = []
    for L in "abcd":
        p = _POINT.match((q.get("option_" + L) or "").strip().replace("\u2212", "-"))
        if not p:
            continue
        x = float(p.group(2)) * (-1 if p.group(1) else 1)
        y = float(p.group(4)) * (-1 if p.group(3) else 1)
        if abs(grad * x + inter - y) < 1e-9:
            on.append(L.upper())
    if len(on) == 1:
        return None
    if not on:
        return f"no option lies on y = {grad:g}x {inter:+g}"
    return (f"options {'/'.join(on)} ALL lie on y = {grad:g}x {inter:+g}, so the question "
            f"has more than one correct answer")


# ---------------------------------------------------------------------------
# The five checks below were written FROM REVIEWER FLAGS, not from theory. Each
# one names the question that produced it, so that if a check ever looks
# over-zealous there is a real defect to argue against.
# ---------------------------------------------------------------------------

_MD_TABLE = re.compile(r"^\s*\|?[\s:]*-{3,}[\s:|-]*\|", re.M)


def markdown_table_in_stem(q):
    """A markdown table in the stem. Selectly renders the stem as PLAIN TEXT in a
    white-space: pre-wrap div -- there is no markdown pass -- so the pipes and the
    |---|---| separator row are shown to the student literally.

    Flagged twice in the first NSW review round ("Table format is quite messy and
    wrong", "Table is inaccurate, fix to make it more clear"). In both cases the DATA
    was correct; only the rendering was broken, which is the worst kind of defect
    because the question looks wrong while being right. Put tabular data in
    figure_svg, which Selectly renders as an image.
    """
    stem = q.get("stem") or ""
    if not _MD_TABLE.search(stem):
        return None
    return ("stem contains a markdown table; Selectly renders stems as plain text, so "
            "the separator row is shown literally. Use figure_svg for tabular data")


_BAD_MINUTES = re.compile(r"\b\d{1,2}:[6-9]\d\b")
_BAD_HOUR = re.compile(r"\b(?:1[3-9]|[2-9]\d):[0-5]\d\s*(?:am|pm)\b", re.I)


def invalid_clock_time(q):
    """A clock time that cannot exist, such as 2:65 am.

    From the NSW round: a flight-arrival question offered "2:65 am" as the distractor
    for a student who adds 40 and 25 minutes without regrouping. The error it models is
    real and worth testing, but written as a clock time it reads as a typo -- the
    reviewer said it "makes the question seem inaccurate (even though the final answer
    is correct)". Model that error with a valid time instead.
    """
    for field in ("stem", "option_a", "option_b", "option_c", "option_d", "explanation"):
        text = str(q.get(field) or "")
        for pat, why in ((_BAD_MINUTES, "minutes past 59"), (_BAD_HOUR, "hour past 12 with am/pm")):
            m = pat.search(text)
            if m:
                return f"{field} contains {m.group(0)!r} — {why}, which is not a real time"
    return None


_MANIPULATIVE = re.compile(
    r"\bzero pair|counter model|algebra tile|base-?ten block|MAB block|ten-?frame\b", re.I)


def teaching_manipulative(q):
    """Asks about a classroom teaching aid rather than about mathematics.

    "Why would you add zero pairs to a counter model?" tests whether a student has been
    taught integers with a particular manipulative. A selective exam tests reasoning, so
    a student who understands integer subtraction perfectly but met it another way is
    marked wrong for their teacher's choice of materials. The reviewer flagged it as
    "quite difficult for a year 6"; the deeper problem is that it is not a maths
    question at all.
    """
    text = (q.get("stem") or "") + " " + (q.get("explanation") or "")
    m = _MANIPULATIVE.search(text)
    if not m:
        return None
    return (f"refers to the teaching manipulative {m.group(0)!r}; selective exams test "
            f"reasoning, not the materials a particular classroom used")


# Only a RESOLVED radicand counts. "√(8² + 15²)" is working-in-progress, and reading the
# 8 out of it called a question calculator-work when its real radicand, 289, is a perfect
# square giving exactly 17. The lookahead skips any root whose contents are still an
# expression, leaving the evaluated form later in the same line to be judged.
_ROOT_OF = re.compile(
    r"√\s*\(?\s*(\d+(?:\.\d+)?)(?![\d.])\s*\)?(?!\s*[²³^+\-*×])")
_DECIMAL_KEY = re.compile(r"^\s*-?\d+\.\d{2,}\b")


def calculator_required(q):
    """The key is a multi-place decimal that can only be got by evaluating a surd.

    A surd LEFT as a surd is exact and perfectly fair -- √65 is a fine answer. What is
    unfair is being asked for 12.58 when the working is √158.186, which no student
    produces without a calculator. The reviewer's note was exactly that: "this question
    needs a calculator to be solved".
    """
    key_letter = (q.get("correct_answer") or "").lower()
    key = str(q.get("option_" + key_letter) or "") if key_letter else ""
    if "√" in key or not _DECIMAL_KEY.match(key.replace(",", "")):
        return None
    for m in _ROOT_OF.finditer(q.get("explanation") or ""):
        val = float(m.group(1))
        if val != int(val) or math.isqrt(int(val)) ** 2 != int(val):
            return (f"key {key.strip()!r} requires {m.group(0)!r} to be evaluated as a "
                    f"decimal — that needs a calculator")
    return None


_DISCRETE = (r"runs|students|people|children|pupils|cars|buses|books|marbles|counters|"
             r"coins|tickets|seats|chairs|players|teams|goals|questions|pets|bricks|"
             r"boxes|apples|eggs|sheep|cows|birds|trees|houses|rooms|matches|bags|"
             r"packets|classes|wickets|runs|goals|tries|catches|overs|laps|sets|games")
_HOW_MANY = re.compile(rf"\bhow many\s+(?:\w+\s+){{0,2}}?({_DISCRETE})\b", re.I)
_PLAIN_NUM = re.compile(r"^\s*(-?[\d,]+(?:\.\d+)?)\s*$")


def non_integer_count(q):
    """Asks how many of an indivisible thing there are, and answers with a fraction.

    "A cricket team scores 275 runs... they score 75% of that. How many runs?" keyed to
    206.25. The arithmetic is right and the question is still wrong: nobody scores a
    quarter of a run. Its explanation even argues the point -- "the question asks for
    the calculated value (not a rounded whole number of runs)" -- which is a question
    defending itself against its own stem. Change the numbers so the answer divides.
    """
    key_letter = (q.get("correct_answer") or "").lower()
    key = str(q.get("option_" + key_letter) or "") if key_letter else ""
    m = _PLAIN_NUM.match(key.replace(",", ""))
    if not m or float(m.group(1)) == int(float(m.group(1))):
        return None
    u = _HOW_MANY.search(q.get("stem") or "")
    if not u:
        return None
    return (f"asks 'how many {u.group(1)}' but the key is {key.strip()} — "
            f"a count cannot be fractional")


# ---------------------------------------------------------------------------
# From the first VIC review round (2026-08-23). Six of the fourteen flags were
# about FIGURE QUALITY -- a class neither the blind solve nor the NSW round
# surfaced, because both were reading the maths rather than looking at the
# picture. The reviewer's words were "rough", "unprofessional", "confusing".
# ---------------------------------------------------------------------------

def negative_count(q):
    """A negative option for something that cannot be negative.

    "How many wickets did she take in the last match?" offering "−1 wickets". It models
    a real slip -- subtracting the wrong way round -- but no bowler takes minus one
    wicket, so the option is never chosen and the question is a three-option one.
    Sibling of non_integer_count: same principle, other direction.
    """
    key_letter = (q.get("correct_answer") or "").lower()
    for L in "abcd":
        opt = str(q.get("option_" + L) or "")
        m = re.match(r"^\s*[-−]\s*\d", opt)
        if not m:
            continue
        # The counted noun sits on the option ("−1 wickets") at least as often as it
        # sits after "how many" in the stem, which asked "How many did she take".
        unit_on_option = re.search(rf"\b({_DISCRETE})\b", opt, re.I)
        if not unit_on_option and not _HOW_MANY.search(q.get("stem") or ""):
            continue
        if L == key_letter:
            return f"the KEY {opt.strip()!r} is negative, but the stem counts things"
        return (f"option {L.upper()} is {opt.strip()!r}; a count cannot be negative, so "
                f"nobody picks it and the question has three real options")
    return None


# A stem asks its question in one of four ways: it ends in a question mark; it ends in a
# colon, which is the cloze frame reading comprehension uses throughout ("...most nearly
# means:"); it opens with an imperative; or it carries a blank to fill. Missing any of
# these made the first version fire on 1,498 perfectly well-formed questions.
# A colon and an em-dash are the same device: both open a cloze frame the options
# complete ("Here, 'difficult' means —"). NSW reading uses the dash throughout, and
# leaving it out flagged two perfectly ordinary questions.
_ASKS = re.compile(r"\?|[:—–-]\s*$|_{3,}|\b(?:which|what|who|when|where|why|how)\b", re.I)
_IMPERATIVE = re.compile(
    r"\b(evaluate|simplify|find|calculate|work out|solve|round|convert|express|"
    r"arrange|complete|choose|select|identify|state|give|determine|write|compute|"
    r"estimate|order|match|rewrite|factorise|expand)\b", re.I)


def no_question_asked(q):
    """The stem presents information and never asks anything.

    Flagged as "doesn't specify what the question really is". A stem that stops after
    the material leaves the student inferring the task from the options, which is a
    different and much vaguer exercise than the one intended.
    """
    stem = (q.get("stem") or "").strip()
    if not stem or _ASKS.search(stem) or _IMPERATIVE.search(stem):
        return None
    return "stem presents information but never asks a question"


_COMPOUND = re.compile(
    r"compounded\s+(monthly|quarterly|weekly|daily|annually)|"
    r"monthly\s+(?:instalments|repayments)|"
    r"over\s+\d+\s+(?:years|months)\s+with", re.I)
_PCT_CHAIN = re.compile(r"([+−-]?\s*\d+(?:\.\d+)?\s*%[,\s]+){3,}")


def compounding_needs_calculator(q):
    """Arithmetic no student does by hand: repeated compounding, or a chain of per cent
    changes applied one after another.

    Two flags in the VIC round -- an amortised 25-year mortgage compounded monthly, and
    five consecutive daily percentage changes. Both are sound mathematics and neither
    belongs in a paper sat without a calculator. calculator_required catches irrational
    roots; this catches the other route to the same problem.
    """
    stem = q.get("stem") or ""
    if (m := _COMPOUND.search(stem)):
        return (f"stem says {m.group(0)!r} — compounding over many periods cannot be "
                f"done by hand")
    if _PCT_CHAIN.search(stem):
        return ("stem applies four or more percentage changes in sequence, which is "
                "calculator work")
    return None


_CIRCLE = re.compile(r"<circle[^>]*\bcx=[\'\"]([-\d.]+)[\'\"][^>]*\bcy=[\'\"]([-\d.]+)"
                     r"[\'\"][^>]*\br=[\'\"]([-\d.]+)[\'\"][^>]*>")
_ARC_R = re.compile(r"[Aa]\s*([\d.]+)[ ,]+([\d.]+)")


def doubled_circle_outline(svg):
    """A full circle is stroked, and arc paths retrace part of the same circumference.

    Both circle figures in the VIC round did this: "the top part of the circumference
    has double lining", "two lines on the right side of the circumference". The second
    stroke sits a fraction off the first, so the edge looks smudged or doubled. Draw the
    arcs OR the outline, not both.
    """
    if not svg:
        return None
    stroked = [(float(a), float(b), float(r)) for a, b, r in _CIRCLE.findall(svg)
               if "stroke=" in svg and float(r) > 12]
    if not stroked:
        return None
    for m in _ARC_R.finditer(svg):
        rx, ry = float(m.group(1)), float(m.group(2))
        if rx != ry:
            continue
        for _cx, _cy, r in stroked:
            if abs(rx - r) < 0.5:
                return (f"an arc of radius {rx:g} retraces a circle already stroked at "
                        f"the same radius — the circumference is drawn twice")
    return None


_TEXT = re.compile(r"<text[^>]*\bx=[\'\"]([-\d.]+)[\'\"][^>]*\by=[\'\"]([-\d.]+)[\'\"]"
                   r"[^>]*?(?:font-size=[\'\"]([\d.]+)[\'\"])?[^>]*>([^<]*)<")


def _text_box(m, pad=0.0):
    """Bounding box for one <text>, honouring a rotate(±90) transform.

    An axis title is written sideways up the y-axis. Treated as horizontal it appears to
    sprawl across the whole plot, which made both text checks report collisions that are
    not there — "Dial reading (kg)" looked like it lay over the plotted line when it sits
    quietly in the left margin.
    """
    x, y = float(m.group(1)), float(m.group(2))
    size = float(m.group(3) or 12)
    label = (m.group(4) or "").strip()
    if not label:
        return None
    w = len(label) * size * 0.55
    tag = m.group(0)
    rot = re.search(r"rotate\s*\(\s*(-?\d+(?:\.\d+)?)", tag)
    if rot and abs(abs(float(rot.group(1))) - 90) < 1:
        cx = cy = None
        nums = re.findall(r"-?\d+(?:\.\d+)?", rot.string[rot.start():])
        if len(nums) >= 3:
            cx, cy = float(nums[1]), float(nums[2])
        cx = x if cx is None else cx
        cy = y if cy is None else cy
        return (cx - size * 0.8 + pad, cy - w / 2 + pad,
                cx + size * 0.25 - pad, cy + w / 2 - pad, label)
    mid = "text-anchor" in tag and "middle" in tag
    x0 = x - w / 2 if mid else x
    return (x0 + pad, y - size * 0.8 + pad, x0 + w - pad, y + size * 0.25 - pad, label)


def overlapping_text_labels(svg, pad=6.0):
    """Two labels whose boxes overlap, so both read as mush.

    "the number 10cm on the light and 12cm at the bottom are both sort of overlapping
    making it a little unclear and unprofessional." Widths are estimated from the
    character count, which is approximate -- hence the generous padding and a minimum
    overlap before it counts.
    """
    if not svg:
        return None
    boxes = [b for b in (_text_box(m) for m in _TEXT.finditer(svg)) if b]
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            ax0, ay0, ax1, ay1, al = boxes[i]
            bx0, by0, bx1, by1, bl = boxes[j]
            ox = min(ax1, bx1) - max(ax0, bx0)
            oy = min(ay1, by1) - max(ay0, by0)
            if ox > pad and oy > pad:
                return (f"labels {al!r} and {bl!r} overlap by about "
                        f"{ox:.0f}x{oy:.0f} px")
    return None


_LABELLED_POINT = re.compile(
    r">\s*([A-Z])\s*\(\s*([-−]?\d+(?:\.\d+)?)\s*,\s*([-−]?\d+(?:\.\d+)?)\s*\)")
_DOT = re.compile(r"<circle[^>]*\bcx=[\'\"]([-\d.]+)[\'\"][^>]*\bcy=[\'\"]([-\d.]+)"
                  r"[\'\"][^>]*\br=[\'\"]([\d.]+)[\'\"]")


def plotted_points_inconsistent(svg, tol=4.0):
    """Points labelled with coordinates that are not drawn to one scale.

    The parallelogram P(−6,2) Q(2,2) R(4,−4) S(−4,−4) was plotted at four DIFFERENT
    horizontal scales -- 10, 16.67 and 10 pixels per unit between consecutive x values.
    The reviewer saw it immediately: "the spacing of each point isn't equal, the
    difference in 4 and 2 is tiny on the x axis". A figure like this cannot be reasoned
    from, and invites a student to answer by eye and be wrong.

    Fits one linear map to every labelled point and reports the worst residual.
    """
    if not svg:
        return None
    labelled = [(float(x.replace("−", "-")), float(y.replace("−", "-")))
                for _n, x, y in _LABELLED_POINT.findall(svg)]
    dots = [(float(a), float(b)) for a, b, r in _DOT.findall(svg) if float(r) <= 5]
    if len(labelled) < 3 or len(dots) < len(labelled):
        return None
    # pair each labelled point with its nearest dot, left-to-right then top-to-bottom
    used, pairs = set(), []
    for ux, uy in labelled:
        best = None
        for i, (px, py) in enumerate(dots):
            if i in used:
                continue
            if best is None:
                best = i
        if best is None:
            return None
        used.add(best)
        pairs.append(((ux, uy), dots[best]))
    if len({u for u, _ in pairs}) < 3:
        return None
    # least squares for px = ox + sx*ux and py = oy - sy*uy, on each axis independently
    def fit(units, px):
        n = len(units)
        mu, mp = sum(units) / n, sum(px) / n
        den = sum((u - mu) ** 2 for u in units)
        if den == 0:
            return None, None
        s = sum((u - mu) * (p - mp) for u, p in zip(units, px)) / den
        return s, mp - s * mu
    ux = [u[0] for u, _ in pairs]
    uy = [u[1] for u, _ in pairs]
    pxs = [p[0] for _, p in pairs]
    pys = [p[1] for _, p in pairs]
    sx, ox = fit(ux, pxs)
    sy, oy = fit(uy, pys)
    if sx is None or sy is None:
        return None
    worst = 0.0
    for (u, v), (px, py) in pairs:
        worst = max(worst, abs(ox + sx * u - px), abs(oy + sy * v - py))
    if worst > tol:
        return (f"labelled points are not on one scale — worst point is {worst:.0f} px "
                f"from where its own coordinates put it")
    if abs(abs(sx) - abs(sy)) > 0.15 * max(abs(sx), abs(sy)):
        return (f"axes use different scales ({abs(sx):.1f} vs {abs(sy):.1f} px per "
                f"unit), so slopes and right angles are drawn wrong")
    return None


# ---------------------------------------------------------------------------
# VIC review round 2 (2026-08-24). All three flags were figure geometry, on
# figures nobody had complained about before -- a reminder that "the reviewer
# did not mention it" is not evidence a figure is sound.
# ---------------------------------------------------------------------------

_LINE_EL = re.compile(
    r"<line[^>]*\bx1=[\'\"]([-\d.]+)[\'\"][^>]*\by1=[\'\"]([-\d.]+)[\'\"]"
    r"[^>]*\bx2=[\'\"]([-\d.]+)[\'\"][^>]*\by2=[\'\"]([-\d.]+)[\'\"]")


def _seg_hits_box(x1, y1, x2, y2, bx0, by0, bx1, by1):
    """Does a segment pass through an axis-aligned box? Liang-Barsky, short form."""
    dx, dy = x2 - x1, y2 - y1
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, x1 - bx0), (dx, bx1 - x1), (-dy, y1 - by0), (dy, by1 - y1)):
        if p == 0:
            if q < 0:
                return False
            continue
        r = q / p
        if p < 0:
            if r > t1:
                return False
            t0 = max(t0, r)
        else:
            if r < t0:
                return False
            t1 = min(t1, r)
    return t0 <= t1


def text_overlaps_geometry(svg, pad=1.5):
    """A label sitting on top of a drawn line.

    "fix the graph as the 0,5 is overlapping the line". The point label was placed at the
    plotted line's own coordinates, so it printed straight through it. Distinct from
    overlapping_text_labels, which only compares text with text.

    Axis titles and tick labels are exempt: they sit alongside the axes by design and a
    strict reading would flag every chart ever drawn.
    """
    if not svg:
        return None
    lines = [tuple(map(float, m.groups())) for m in _LINE_EL.finditer(svg)]
    if not lines:
        return None
    for m in _TEXT.finditer(svg):
        b = _text_box(m, pad)
        if not b or len(b[4]) < 2:
            continue
        box = b[:4]
        if box[2] <= box[0] or box[3] <= box[1]:
            continue
        label = b[4]
        for (a, b, c, d) in lines:
            # an axis is a long horizontal or vertical rule; labels belong beside those
            if abs(a - c) < 1 or abs(b - d) < 1:
                continue
            if _seg_hits_box(a, b, c, d, *box):
                return (f"label {label!r} is drawn on top of the line from "
                        f"({a:g}, {b:g}) to ({c:g}, {d:g})")
    return None


_HAS_WORD = re.compile(r"[A-Za-z]{3,}")


def axes_unlabelled(svg):
    """A chart with numbers up the side and along the bottom, and no word saying what
    they are. "please label the axis for professionalism".

    Only fires on figures that clearly ARE charts -- several numeric labels and a long
    axis rule -- so diagrams of shapes are untouched.
    """
    if not svg:
        return None
    texts = [(m.group(4) or "").strip() for m in _TEXT.finditer(svg)]
    numeric = [t for t in texts if re.fullmatch(r"-?\d+(?:\.\d+)?", t)]
    if len(numeric) < 4:
        return None
    if not re.search(r"<(?:line|path)[^>]*d?=?[^>]*>", svg):
        return None
    if any(_HAS_WORD.search(t) for t in texts):
        return None
    # A coordinate plane is labelled by convention: the axes are x and y, and nothing
    # more is needed or wanted. Only charts that MEASURE something -- litres, students,
    # kilograms -- need words saying what the numbers count.
    singles = {t for t in texts if len(t) == 1}
    if {"x", "y"} <= singles:
        return None
    # A number line has one rule and no second dimension. Its numbers ARE the quantity,
    # so there is nothing to name. Only figures with both a horizontal and a vertical
    # rule are charts in the sense this check means.
    rules = [tuple(map(float, m.groups())) for m in _LINE_EL.finditer(svg)]
    horiz = any(abs(b - d) < 1 and abs(a - c) > 40 for a, b, c, d in rules)
    vert = any(abs(a - c) < 1 and abs(b - d) > 40 for a, b, c, d in rules)
    # An axis pair is often one path, e.g. "M34 12V144H330". Measure how far it actually
    # travels: a tick mark is also "V" and must not count. Judging by string length
    # instead made every tick on a number line look like an axis.
    for d in re.findall(r"<path[^>]*\bd=[\'\"]([^\'\"]+)", svg):
        m0 = re.match(r"\s*M\s*(-?[\d.]+)[ ,]+(-?[\d.]+)", d)
        if not m0:
            continue
        x0, y0 = float(m0.group(1)), float(m0.group(2))
        for cmd, val in re.findall(r"([VH])\s*(-?[\d.]+)", d):
            if cmd == "V" and abs(float(val) - y0) > 40:
                vert = True
            if cmd == "H" and abs(float(val) - x0) > 40:
                horiz = True
    if not (horiz and vert):
        return None
    return ("the figure is a chart with numeric scales but no axis titles — a reader "
            "cannot tell what is being counted or measured")


_N = r"[-+]?[\d.]+"
_ARC = re.compile(
    rf"<path[^>]*\bd=[\'\"]\s*M\s*({_N})[ ,]+({_N})\s*"
    rf"A\s*({_N})[ ,]+({_N})[ ,]+{_N}[ ,]+([01])[ ,]+([01])[ ,]+({_N})[ ,]+({_N})")


def _arc_centre(x1, y1, x2, y2, r, f_large, f_sweep):
    """Where SVG will actually put the centre of this arc (spec F.6.5, rx = ry, no
    rotation). The flags choose between two candidate centres, and only one of them is
    the vertex — which is why an arc can have perfect endpoints and still bulge the
    wrong way."""
    dx2, dy2 = (x1 - x2) / 2, (y1 - y2) / 2
    den = r * r * (dy2 * dy2 + dx2 * dx2)
    if den <= 0:
        return None
    k2 = (r ** 4 - r * r * dy2 * dy2 - r * r * dx2 * dx2) / den
    k = math.sqrt(k2) if k2 > 0 else 0.0
    if f_large == f_sweep:
        k = -k
    return (k * dy2 + (x1 + x2) / 2, -k * dx2 + (y1 + y2) / 2)
_POLY = re.compile(r"<polygon[^>]*\bpoints=[\'\"]([^\'\"]+)[\'\"]")


def angle_arc_malformed(svg, tol=0.15):
    """An angle mark whose two ends are not the same distance from their vertex.

    "try fixing that little curve line that is going outside the triangle by a tiny bit
    near angle A." The arc declared radius 24 while its endpoints sat 24.00 and 24.19
    from the vertex. SVG must then fit a circle of radius 24 through two points that do
    not both lie on one, so the centre lands off the vertex and the arc bulges past the
    edge. A fifth of a pixel of sloppiness is visible, and a reviewer found it.
    """
    if not svg:
        return None
    verts = []
    for m in _POLY.finditer(svg):
        raw = m.group(1).replace(",", " ").replace("\u2212", "-")
        try:
            nums = [float(n) for n in raw.split()]
        except ValueError:
            continue          # a points list we cannot read is not one to judge
        verts += list(zip(nums[0::2], nums[1::2]))
    if not verts:
        return None
    for m in _ARC.finditer(svg):
        x1, y1, rx, ry, f_large, f_sweep, x2, y2 = (
            float(g) if i not in (4, 5) else int(g) for i, g in enumerate(m.groups()))
        if abs(rx - ry) > 0.01:
            continue
        v = min(verts, key=lambda p: max(math.dist(p, (x1, y1)), math.dist(p, (x2, y2))))
        d1, d2 = math.dist(v, (x1, y1)), math.dist(v, (x2, y2))
        if max(d1, d2) > 4 * rx:
            continue                       # not an angle mark at this vertex
        if abs(d1 - d2) > tol or abs(d1 - rx) > tol or abs(d2 - rx) > tol:
            return (f"angle arc at ({v[0]:g}, {v[1]:g}) declares r={rx:g} but its ends "
                    f"are {d1:.2f} and {d2:.2f} from the vertex — it will not sit on "
                    f"the angle")
        # Endpoints alone are not enough. The sweep flag chooses which of two centres
        # SVG uses, and the wrong one swings the arc away from the vertex entirely --
        # "flip angle A's arc to be facing the other way". Perfect endpoints, wrong side.
        c = _arc_centre(x1, y1, x2, y2, rx, f_large, f_sweep)
        if c and math.dist(c, v) > max(tol, 0.5):
            return (f"angle arc at ({v[0]:g}, {v[1]:g}) is centred {math.dist(c, v):.1f} "
                    f"px away at ({c[0]:.1f}, {c[1]:.1f}) — the sweep flag has it "
                    f"curving the wrong way round")
    return None
