#!/usr/bin/env python3
"""Finalise one verbal_reasoning (VIC SEHS / ACER) batch.

Validate -> near-duplicate screen -> balanced shuffle -> manifest.

Usage:  env -u PYTHONPATH .venv/bin/python3.11 -m tools.vr_finalise <NN>

Subject-specific orchestrator; the checks that generalise live in
tools/question_checks.py. Modelled on tools/lr_finalise.py.

Three VR-specific rules, each earned:

1. CONTEXTUAL STEMS. A bare "Which word is the BEST synonym for 'X'?" scores 0.857-0.872
   against the same frame with a different word — above phase 4's 0.85 dedup threshold,
   which drops silently. A whole batch of them would vanish at load with no error. Put the
   word in a sentence and the same pair scores 0.66. TASK §3.1 asks for vocabulary *in
   context* anyway, so the rule the dedup forces is also the rule the brief wants.

2. TARGET WORDS ARE UNIQUE ACROSS THE BANK. Stem similarity cannot police vocabulary
   reuse once stems are contextual — two questions on 'curtail' in different sentences
   look nothing alike. The target word is the identity of a vocabulary question.

3. DISTRACTORS MUST BE WRONG IN DIFFERENT WAYS. See distractor_relation_errors. In ~24 of
   26 sampled existing VR items the three distractors were mutual synonyms and the key was
   the odd one out, answerable without knowing the target word.
"""
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
    KEYS,
    answer_shape_monotony,
    distractor_relation_errors,
    length_tell,
    doubled_token_errors,
    option_wording_errors,
    options_distinct,
    positional_reference,
    relation_monotony,
    unknown_words,
)

PLAN = ROOT / "tools/vr/vr_plan.json"
GEN = ROOT / "run_data/output/verbal_reasoning/generated"
MANIFEST = GEN / "vr_MANIFEST.json"
# Written by tools/load_batch.py as a list of FILENAMES. Reading a different path here
# silently made every loaded batch count twice — once from the DB and once from its JSON
# — inflating the manifest to 63 when only 42 questions existed.
LOADED = GEN / "vr_vic_acer_LOADED.json"
DB = ROOT / "run_data/db/qbank.db"
BOOK = "vr_vic_acer"

REQUIRED = ["id", "subject", "stem", *KEYS, "correct_answer", "explanation", "topic",
            "difficulty", "confidence", "source_book", "source_page",
            "source_page_description", "passage", "figure_svg", "review_status",
            "created_at", "target_word", "relations"]

# Categories whose distractors must be wrong in three different ways. word_group is
# excluded on purpose: there the coherent distractor bloc IS the item — TASK §3.3 asks
# for three distractors that form their own group so a student pattern-matching on
# "which three go together" picks wrong.
RELATION_CATEGORIES = {"vocabulary_synonym", "antonym", "shades_of_meaning"}

# Words a capable Year 8 student meets in reading, not in a word list. TASK §3 records
# comfort ratings of 8.5-9.5/10 on the real paper and warns our bank is harder than the
# exam, so exotica is a calibration failure, not a bonus.
# Everyday Australian and British words the American system wordlist does not carry.
# Without this the real-words check rejects perfectly ordinary vocabulary.
AU_EXTRA = {
    "peckish", "chuffed", "dob", "esky", "arvo", "ute", "bushwalk", "bushwalker",
    "doona", "servo", "brekkie", "daggy", "chocka", "sunnies", "togs", "thongs",
    "tradie", "woop", "yakka", "billabong", "saltbush", "mallee", "pardalote",
    "kelpie", "wombat", "bilby", "quokka", "goanna", "brumby", "jarrah", "karri",
}

TOO_HARD = {
    "perspicacious", "obfuscate", "recalcitrant", "perfunctory", "sycophant",
    "intransigent", "obstreperous", "pusillanimous", "grandiloquent", "abstruse",
    "lachrymose", "supercilious", "truculent", "mendacious", "ineffable",
}


def category_of(q):
    m = re.match(r"Category: (\w+)", q.get("source_page_description") or "")
    return m.group(1) if m else None


def validate(qs, nn, plan):
    cats = {c["key"] for c in plan["categories"]}
    errs, seen_ids, seen_targets = [], set(), set()
    for i, q in enumerate(qs):
        tag = f"q[{i}] {q.get('target_word', '?')}"
        for f in REQUIRED:
            if f not in q:
                errs.append(f"{tag}: missing field '{f}'")
        if q.get("subject") != "verbal_reasoning":
            errs.append(f"{tag}: subject must be verbal_reasoning")
        if q.get("correct_answer") not in ("A", "B", "C", "D"):
            errs.append(f"{tag}: bad correct_answer {q.get('correct_answer')!r}")
        if q.get("difficulty") not in ("medium", "hard"):
            errs.append(f"{tag}: bad difficulty {q.get('difficulty')!r}")
        if q.get("review_status") != "pending":
            errs.append(f"{tag}: review_status must be pending")
        if q.get("passage") is not None:
            errs.append(f"{tag}: passage must be null")
        if q.get("figure_svg") is not None:
            errs.append(f"{tag}: verbal_reasoning questions carry no figure")
        if q.get("source_book") != BOOK:
            errs.append(f"{tag}: source_book must be {BOOK}")
        if q.get("source_page") != nn:
            errs.append(f"{tag}: source_page must be {nn}")
        if not (isinstance(q.get("confidence"), (int, float)) and 0.0 <= q["confidence"] <= 1.0):
            errs.append(f"{tag}: confidence out of range")
        if q.get("id") in seen_ids:
            errs.append(f"{tag}: duplicate id")
        seen_ids.add(q.get("id"))
        if not options_distinct(q):
            errs.append(f"{tag}: options not distinct (case/whitespace-insensitive)")
        for msg in doubled_token_errors(q) + option_wording_errors(q):
            errs.append(f"{tag}: {msg}")
        phrase = positional_reference(q.get("explanation"))
        if phrase:
            errs.append(f"{tag}: explanation names an option position ({phrase!r}) — "
                        f"options get shuffled")

        cat = category_of(q)
        # In an antonym question the KEY is the opposite of the target, so a distractor
        # declared 'opposite' would be a second defensible answer. Conversely a synonym
        # of the target is the classic trap there, and is simply wrong in a synonym
        # question, where it would be a second key.
        # Only where the banned relation would BE the answer. A synonym distractor is
        # legitimate in shades_of_meaning — it matches the target's meaning at the wrong
        # intensity, which is exactly the trap that category is built on.
        rel = q.get("relations") or {}
        banned = {"antonym": "opposite", "vocabulary_synonym": "synonym"}.get(cat)
        for word, r in rel.items():
            if banned and r == banned:
                errs.append(f"{tag}: distractor {word!r} is declared {banned!r}, which in "
                            f"a {cat} question would be a second correct answer")
        if not re.match(r"Category: (\w+) — (.+)$", q.get("source_page_description", "")):
            errs.append(f"{tag}: source_page_description must be 'Category: <key> — <title>'")
        elif cat not in cats:
            errs.append(f"{tag}: unknown category {cat!r}")

        errs += [f"{tag}: {e}" for e in target_word_errors(q, cat, seen_targets)]
        if cat in RELATION_CATEGORIES:
            errs += [f"{tag}: {e}" for e in distractor_relation_errors(q)]
        elif cat == "word_group":
            errs += [f"{tag}: {e}" for e in word_group_errors(q)]

        expl = str(q.get("explanation") or "")
        if len(expl.split()) < 8:
            errs.append(f"{tag}: explanation too thin — say why the key is right AND why "
                        f"the strongest distractor is wrong")

    pool = qs + bank_questions(nn)
    errs += answer_shape_monotony(pool, group_of=category_of)
    errs += length_tell(pool, group_of=category_of)
    # Only where varied relations are the design. word_group REQUIRES a uniform 'domain'
    # decoy set (see word_group_errors), so running monotony over it would fail every
    # correctly built batch — the two checks would contradict each other.
    errs += relation_monotony([q for q in pool if category_of(q) in RELATION_CATEGORIES],
                              group_of=category_of)
    return errs


def target_word_errors(q, cat, seen_targets):
    """The target word must be real, in the stem, in context, pitched right, and new."""
    errs = []
    word = str(q.get("target_word") or "").strip()
    if not word:
        return ["missing target_word"]
    low = word.lower()
    if low in seen_targets:
        errs.append(f"target word {word!r} used twice in this batch")
    seen_targets.add(low)
    if low in TOO_HARD:
        errs.append(f"target word {word!r} is exotica — TASK §3 pitches at the level of "
                    f"edict, discern, curb, pique, ovation, curtail")

    # An option that repeats the target word gives the game away, and one built out of an
    # invented lookalike ("mimec" for 'mimic') can be struck out without knowing anything.
    for k in KEYS:
        opt = str(q.get(k) or "")
        # Whole word only. A 'form' distractor is SUPPOSED to share letters with the
        # target — deter/determine, grim/grimy are the trap working as intended. Only
        # repeating the target as its own word gives the answer away.
        if cat != "word_group" and re.search(rf"\b{re.escape(low)}\b", opt.lower()):
            errs.append(f"option {opt!r} repeats the target word {word!r}")
        bad = unknown_words(opt, extra_ok=AU_EXTRA | {word})
        if bad:
            errs.append(f"option {opt!r} is not made of real words: {bad}")

    stem = str(q.get("stem") or "")
    if cat != "word_group":
        if low not in stem.lower():
            errs.append(f"target word {word!r} does not appear in the stem")
        # A bare "Which word means X?" frame collides with every other such frame above
        # phase 4's silent 0.85 dedup threshold. Context also matches what §3.1 asks for.
        without = re.sub(re.escape(word), "", stem, flags=re.I)
        if len(without.split()) < 12:
            errs.append(f"stem is a bare lookup frame ({len(without.split())} words "
                        f"besides the target) — put {word!r} in a sentence, or phase 4 "
                        f"will silently drop this question as a near-duplicate")
    return errs


def word_group_errors(q):
    """The signature ACER item: three distractors that form their OWN coherent group.

    TASK §3.3 — 'Miserly, Stingy, Parsimonious' joined by Frugal, against Spendthrift /
    Extravagant / Squandering. The trap only works if the distractors cohere, so this is
    the one category where a uniform relation set is required rather than rejected.
    """
    errs = []
    rel = q.get("relations")
    if not isinstance(rel, dict):
        return ["missing 'relations' map"]
    kinds = set(rel.values())
    if kinds != {"domain"}:
        errs.append(f"word_group distractors must all be declared 'domain' (they form "
                    f"the decoy group); got {sorted(kinds)}")
    if not q.get("group_words") or len(q["group_words"]) < 3:
        errs.append("word_group needs 'group_words': the 3+ words shown in the stem")
    for w in q.get("group_words", []):
        if w.lower() not in str(q.get("stem", "")).lower():
            errs.append(f"group word {w!r} is not in the stem")
    return errs


def bank_questions(skip_nn):
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute(
        "SELECT * FROM questions WHERE subject='verbal_reasoning' "
        "AND NOT (source_book=? AND source_page=?)", (BOOK, skip_nn))]
    for f in other_batches(skip_nn):
        rows += json.loads(f.read_text(encoding="utf-8"))
    return rows


def existing_target_words(skip_nn):
    """Target words already spent, from finalised batches and from the loaded bank."""
    words = set()
    con = sqlite3.connect(DB)
    for (desc,) in con.execute(
            "SELECT source_page_description FROM questions WHERE source_book=? "
            "AND source_page != ?", (BOOK, skip_nn)):
        m = re.search(r"\[target: ([^\]]+)\]", desc or "")
        if m:
            words.add(m.group(1).lower())
    for f in other_batches(skip_nn):
        for q in json.loads(f.read_text(encoding="utf-8")):
            if q.get("target_word"):
                words.add(q["target_word"].lower())
    return words


def loaded_set():
    """Batch numbers already inserted into the DB, parsed from the loader's filenames."""
    if not LOADED.exists():
        return set()
    names = json.loads(LOADED.read_text(encoding="utf-8"))
    return {int(m.group(1)) for m in (re.search(r"_p(\d+)\.json$", n) for n in names) if m}


def batch_no(f):
    return int(re.search(r"_p(\d+)\.json$", f.name).group(1))


def other_batches(skip_nn):
    done = loaded_set()
    return [f for f in sorted(GEN.glob(f"{BOOK}_p*.json"))
            if batch_no(f) not in done and batch_no(f) != skip_nn]


def near_duplicates(qs, nn, threshold=0.82):
    """Stem similarity against the rest of the bank, plus target-word reuse."""
    errs = []
    spent = existing_target_words(nn)
    for q in qs:
        w = str(q.get("target_word") or "").lower()
        if w and w in spent:
            errs.append(f"target word {q['target_word']!r} is already used by another "
                        f"vr_vic_acer question")

    con = sqlite3.connect(DB)
    existing = [r[0] for r in con.execute(
        "SELECT stem FROM questions WHERE subject='verbal_reasoning' "
        "AND NOT (source_book=? AND source_page=?)", (BOOK, nn)) if r[0]]
    for f in other_batches(nn):
        existing += [x["stem"] for x in json.loads(f.read_text(encoding="utf-8"))]

    batch = []
    for q in qs:
        low = q["stem"].lower()
        for prev in batch + existing:
            r = SequenceMatcher(None, low, prev.lower()).ratio()
            if r >= threshold:
                errs.append(f"{q.get('target_word')}: stem {r:.3f} similar to "
                            f"{prev[:80]!r} — reword or phase 4 will drop it")
                break
        batch.append(q["stem"])
    return errs


def running_counts(skip_nn):
    c = collections.Counter()
    con = sqlite3.connect(DB)
    for a, n in con.execute("SELECT correct_answer, COUNT(*) FROM questions "
                            "WHERE source_book=? GROUP BY 1", (BOOK,)):
        c[a] += n
    for f in other_batches(skip_nn):
        for q in json.loads(f.read_text(encoding="utf-8")):
            c[q["correct_answer"]] += 1
    return c


def recompute_manifest(plan, current_nn, current_qs):
    have = {c["key"]: 0 for c in plan["categories"]}
    rows = []
    con = sqlite3.connect(DB)
    rows += [r[0] for r in con.execute(
        "SELECT source_page_description FROM questions WHERE source_book=? "
        "AND source_page != ?", (BOOK, current_nn))]
    for f in other_batches(current_nn):
        rows += [q["source_page_description"] for q in json.loads(f.read_text(encoding="utf-8"))]
    rows += [q["source_page_description"] for q in current_qs]
    for desc in rows:
        m = re.match(r"Category: (\w+)", desc or "")
        if m and m.group(1) in have:
            have[m.group(1)] += 1
    return [{"key": c["key"], "label": c["label"], "target": c["target"],
             "have": have[c["key"]]} for c in plan["categories"]]


def main():
    nn = int(sys.argv[1])
    path = GEN / f"{BOOK}_p{nn}.json"
    qs = json.loads(path.read_text(encoding="utf-8"))
    plan = json.loads(PLAN.read_text(encoding="utf-8"))

    errs = validate(qs, nn, plan) + near_duplicates(qs, nn)
    if errs:
        print(f"VALIDATION FAILED ({len(errs)}):")
        for e in errs:
            print("  -", e)
        sys.exit(1)

    rng = random.Random(nn * 7919)
    counts = running_counts(nn)
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
        # Carry the target word into a field that survives the load, so a later batch can
        # tell which vocabulary is already spent. source_page_description is the only free
        # text column the schema keeps.
        if q.get("target_word") and "[target:" not in q["source_page_description"]:
            q["source_page_description"] += f" [target: {q['target_word']}]"

    path.write_text(json.dumps(qs, indent=2, ensure_ascii=False), encoding="utf-8")
    manifest = recompute_manifest(plan, nn, qs)
    MANIFEST.write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8")

    cats = collections.Counter(category_of(q) for q in qs)
    nhard = sum(1 for q in qs if q["difficulty"] == "hard")
    print(f"OK p{nn}: {len(qs)} q, {nhard} hard | {dict(cats)}")
    print(f"batch keys  { {a: sum(1 for q in qs if q['correct_answer'] == a) for a in 'ABCD'} }")
    print(f"running keys {dict(sorted(counts.items()))}")
    for m in manifest:
        print(f"  {m['key']:22} {m['have']:>3} / {m['target']}")


if __name__ == "__main__":
    main()
