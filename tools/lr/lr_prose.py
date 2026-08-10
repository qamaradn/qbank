#!/usr/bin/env python3
"""Structural checks for argument questions, where no enumeration decides the answer.

lr_logic can settle "which must be true" outright. Nothing settles "which is the
assumption" or "which best explains the link" — those are judgement, and a checker that
claimed otherwise would be lying about what it knows.

What can still be checked is the SHAPE of the four options. Every argument question here
declares what each distractor is doing — restating a premise, overreaching, wandering off
the topic — and the build verifies that each one actually does it. That catches the
defects that are about construction rather than about meaning, and those are the ones a
writer misses when re-reading their own work:

  - an "irrelevant" option that is really about the conclusion, so it is not irrelevant
    but weak, and a reasonable student can defend it
  - a "restatement" that restates nothing, so nothing makes it tempting and the item is
    really a three-option question
  - an "overreach" phrased so mildly it is simply another candidate answer
  - a key that stands out by length, which is answerable without reading the stem

p21 carries its own copy of `content`, written before this module existed. It is left
alone: that batch is loaded, and rebuilding it would mint fresh uuids and orphan rows.
"""
import difflib
import re

_STOP = set("""a an and are as at be been but by can cannot did do does for from had has have
he her him his if in into is it its more most no not of on one only or our out she so than
that the their them there these they this to was were what when where which who will with
would you your also same each every been about after before over under""".split())

#: Words that mark a claim as sweeping. An "overreach" distractor without one of these is
#: not overreaching — it is just another reasonable answer.
ABSOLUTES = {"all", "always", "any", "anybody", "anyone", "cannot", "entirely", "every",
             "everybody", "everyone", "everything", "never", "no", "nobody", "none",
             "nothing", "only", "solely", "totally", "whenever", "wholly"}


def content(text):
    """Meaning-bearing words, crudely stemmed.

    The stemming is load-bearing, not tidiness: "students who wore hats" and "the hat
    wearers" restate each other, and comparing exact tokens scores them as unrelated.
    """
    out = set()
    for w in re.findall(r"[a-z]+", text.lower()):
        if w in _STOP or len(w) <= 2:
            continue
        for suffix in ("iest", "ies", "ing", "ers", "est", "ed", "er", "es", "s"):
            if w.endswith(suffix) and len(w) - len(suffix) >= 3:
                w = w[:-len(suffix)]
                break
        out.add(w)
    return out


def overlap(a, b):
    return content(a) & content(b)


def must_restate(candidate, source, label, n=3):
    shared = overlap(candidate, source)
    if len(shared) < n:
        raise AssertionError(
            f"{label}: shares only {sorted(shared)} with what it is meant to restate — "
            f"restating is what makes it tempting, so it has to echo the wording")


def must_not_restate(candidate, source, label, cap=0.6):
    """Fail if the candidate is a near-paraphrase of any sentence in `source`.

    This one deliberately does NOT use content overlap. An assumption about breakfast in
    an argument about breakfast has to reuse the words breakfast, school and students —
    sharing vocabulary is what being on topic means, and a bag-of-words test reads every
    sound assumption as already stated. What makes an assumption stated is that a
    sentence already SAYS it, in that order, which is sequence similarity.
    """
    for sentence in re.split(r"(?<=[.!?])\s+", source):
        if len(sentence.split()) < 4:
            continue
        ratio = difflib.SequenceMatcher(None, candidate.lower(), sentence.lower()).ratio()
        if ratio > cap:
            raise AssertionError(
                f"{label}: {ratio:.2f} similar to {sentence!r} — an assumption has to be "
                f"UNSTATED, and this one is close to being said outright")


def must_be_unrelated(candidate, source, label, n=1):
    shared = overlap(candidate, source)
    if len(shared) > n:
        raise AssertionError(
            f"{label}: shares {sorted(shared)} with the conclusion — that makes it a weak "
            f"answer a student can argue for, not an irrelevant one")


#: Verbs that assert one thing acting on another. A "this causes that" distractor
#: without one is not making the causal claim it is supposed to be making.
CAUSAL = {"cause", "caused", "causes", "drive", "drives", "help", "helps", "improve",
          "improves", "lead", "leads", "lower", "lowers", "make", "makes", "prevent",
          "prevents", "push", "pushes", "raise", "raises", "reduce", "reduces",
          "stop", "stops", "worsen", "worsens"}


def must_assert_cause(candidate, label):
    """Fail unless the candidate actually claims one thing acts on the other.

    This stands in for the irrelevance check in correlation questions, where that check
    cannot work: every option there names both correlated things, so "ice cream" is
    shared by construction and the overlap test reads a perfectly good distractor as
    being about the conclusion.
    """
    if not set(re.findall(r"[a-z]+", candidate.lower())) & CAUSAL:
        raise AssertionError(
            f"{label}: {candidate!r} names no causal verb, so it does not make the causal "
            f"claim the question is asking the student to reject")


def must_overreach(candidate, label):
    if not (content(candidate) | set(candidate.lower().split())) & ABSOLUTES:
        raise AssertionError(
            f"{label}: {candidate!r} carries no absolute word, so it does not overreach — "
            f"as written it is simply a second reasonable answer")


def must_balance(options, label, ratio=0.7):
    """Keep the four options within `ratio` of each other in length.

    A key that is reliably the longest option is answerable without reading the stem.
    It happens on its own in argument questions, because a rival explanation takes more
    words to state than a piece of scenery does.
    """
    lens = [len(o) for o in options]
    if min(lens) < ratio * max(lens):
        raise AssertionError(
            f"{label}: options run {min(lens)}-{max(lens)} characters — fill out the short "
            f"ones before the key stands out by length alone")
