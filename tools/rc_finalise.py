#!/usr/bin/env python3
"""Finalise one reading_comprehension vocabulary-cloze batch (TASK §5).

Usage:  env -u PYTHONPATH .venv/bin/python3.11 -m tools.rc_finalise <NN>

The NSW test is now computer-based and sets a passage with roughly 8 blanks, each filled
from a dropdown. Modelled as 8 linked MCQs sharing one `passage`, exactly as the existing
RC questions already share passages (719 questions across 144 passages).

Three things this enforces that the generic checks cannot:

1. THE PASSAGE IS THE SAME FOR EVERY BLANK IN ITS GROUP. Eight rows carry eight copies of
   one passage; if one drifts, Selectly's passageId (a hash of the text) splits them into
   two groups and the student sees the passage twice.

2. THE BLANKS AND THE QUESTIONS AGREE. Every marker in the passage has exactly one
   question and vice versa, numbered from 1 with no gaps — a passage with a blank nobody
   asks about is unanswerable, and a question pointing at a missing blank is worse.

3. STEMS QUOTE THE PASSAGE VERBATIM. The quoted fragment is generated from the passage by
   the builder rather than retyped, so it cannot disagree. It also makes the eight stems
   textually distinct, which matters because phase 4 drops near-duplicate stems at 0.85
   SILENTLY — eight stems reading "which word fits blank (n)?" would collapse to one.

NSW is sat in Year 6, so this is pitched below the VIC verbal_reasoning bank (Year 8) —
see TASK §2, which calls the difficulty gap deliberate.
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
    options_distinct,
    positional_reference,
    relation_monotony,
    unknown_words,
)
from tools.vr_finalise import AU_EXTRA  # noqa: E402

GEN = ROOT / "run_data/output/reading_comprehension/generated"
MANIFEST = GEN / "rc_cloze_MANIFEST.json"
LOADED = GEN / "rc_cloze_LOADED.json"
DB = ROOT / "run_data/db/qbank.db"
BOOK = "rc_nsw_cloze"
CATEGORY = "vocabulary_cloze"
BLANK_RE = re.compile(r"_{2,}\((\d+)\)_{2,}")
TARGET_PASSAGES = 15
BLANKS_PER_PASSAGE = 8

REQUIRED = ["id", "subject", "stem", *KEYS, "correct_answer", "explanation", "topic",
            "difficulty", "confidence", "source_book", "source_page",
            "source_page_description", "passage", "figure_svg", "review_status",
            "created_at", "blank", "pos", "relations", "passage_title"]

PARTS_OF_SPEECH = {"noun", "verb", "adjective", "adverb", "preposition", "conjunction",
                   "pronoun", "determiner"}


def validate(qs, nn):
    errs, seen_ids = [], set()
    for i, q in enumerate(qs):
        tag = f"q[{i}] {q.get('passage_title', '?')} blank {q.get('blank', '?')}"
        for f in REQUIRED:
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
            errs.append(f"{tag}: cloze questions carry no figure")
        if not (q.get("passage") or "").strip():
            errs.append(f"{tag}: passage must be populated for a cloze question")
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
            errs.append(f"{tag}: options not distinct")
        phrase = positional_reference(q.get("explanation"))
        if phrase:
            errs.append(f"{tag}: explanation names an option position ({phrase!r})")
        if q.get("pos") not in PARTS_OF_SPEECH:
            errs.append(f"{tag}: pos must be one of {sorted(PARTS_OF_SPEECH)}, got "
                        f"{q.get('pos')!r} — §5 requires every option to be the same "
                        f"part of speech, so it is declared rather than guessed")
        errs += [f"{tag}: {e}" for e in distractor_relation_errors(q)]
        # A cloze blank accepts any word that fits the sentence, so a distractor meaning
        # the same as the key will usually fit it too — a second correct answer rather
        # than a trap. Found by eye: "Funding for the programs is not ___" with key
        # 'secure' and distractor 'guaranteed', both of which read perfectly.
        for word, r in (q.get("relations") or {}).items():
            if r == "synonym":
                errs.append(f"{tag}: distractor {word!r} is declared 'synonym' — in a "
                            f"cloze a word meaning the same as the key normally fits the "
                            f"blank as well, giving two correct answers")
        for k in KEYS:
            bad = unknown_words(q.get(k), extra_ok=AU_EXTRA)
            if bad:
                errs.append(f"{tag}: option {q[k]!r} is not made of real words: {bad}")
        if len(str(q.get("explanation") or "").split()) < 8:
            errs.append(f"{tag}: explanation too thin — say why the key fits AND why the "
                        f"strongest distractor does not")

    errs += passage_group_errors(qs)
    pool = qs + bank_questions(nn)
    errs += answer_shape_monotony(pool, group_of=lambda q: CATEGORY)
    errs += length_tell(pool, group_of=lambda q: CATEGORY)
    errs += relation_monotony([q for q in pool if q.get("relations")],
                              group_of=lambda q: CATEGORY)
    return errs


def passage_group_errors(qs):
    """Every passage must carry exactly one question per blank, and one text."""
    errs = []
    groups = collections.defaultdict(list)
    for q in qs:
        groups[q.get("passage_title")].append(q)

    for title, group in groups.items():
        texts = {q.get("passage") for q in group}
        if len(texts) != 1:
            errs.append(f"[{title}]: the {len(group)} questions carry {len(texts)} "
                        f"different passage texts — Selectly groups by a hash of the "
                        f"passage, so they would split into separate passages")
            continue
        passage = texts.pop() or ""
        in_passage = [int(n) for n in BLANK_RE.findall(passage)]
        asked = [q.get("blank") for q in group]

        if sorted(in_passage) != list(range(1, len(in_passage) + 1)):
            errs.append(f"[{title}]: blanks in the passage are numbered {in_passage} — "
                        f"expected 1..{len(in_passage)} with no gaps or repeats")
        if sorted(asked) != sorted(in_passage):
            errs.append(f"[{title}]: passage has blanks {sorted(in_passage)} but the "
                        f"questions ask about {sorted(asked)}")
        if len(in_passage) != BLANKS_PER_PASSAGE:
            errs.append(f"[{title}]: {len(in_passage)} blanks, expected "
                        f"{BLANKS_PER_PASSAGE} (TASK §5)")

        # The stem must quote the passage, not a retyped approximation of it.
        for q in group:
            frag = q.get("stem_fragment")
            if frag and frag not in passage:
                errs.append(f"[{title}] blank {q.get('blank')}: the quoted fragment is "
                            f"not in the passage verbatim")
    return errs


def bank_questions(skip_nn):
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute(
        "SELECT * FROM questions WHERE subject='reading_comprehension' "
        "AND NOT (source_book=? AND source_page=?)", (BOOK, skip_nn))]
    for f in other_batches(skip_nn):
        rows += json.loads(f.read_text(encoding="utf-8"))
    return rows


def loaded_set():
    if not LOADED.exists():
        return set()
    names = json.loads(LOADED.read_text(encoding="utf-8"))
    return {int(m.group(1)) for m in (re.search(r"_p(\d+)\.json$", n) for n in names) if m}


def other_batches(skip_nn):
    done = loaded_set()
    return [f for f in sorted(GEN.glob(f"{BOOK}_p*.json"))
            if int(re.search(r"_p(\d+)\.json$", f.name).group(1)) not in done
            and int(re.search(r"_p(\d+)\.json$", f.name).group(1)) != skip_nn]


def near_duplicates(qs, nn, threshold=0.82):
    con = sqlite3.connect(DB)
    existing = [r[0] for r in con.execute(
        "SELECT stem FROM questions WHERE subject='reading_comprehension' "
        "AND NOT (source_book=? AND source_page=?)", (BOOK, nn)) if r[0]]
    for f in other_batches(nn):
        existing += [x["stem"] for x in json.loads(f.read_text(encoding="utf-8"))]
    errs, batch = [], []
    for q in qs:
        low = q["stem"].lower()
        for prev in batch + existing:
            r = SequenceMatcher(None, low, prev.lower()).ratio()
            if r >= threshold:
                errs.append(f"{q.get('passage_title')} blank {q.get('blank')}: stem "
                            f"{r:.3f} similar to {prev[:70]!r} — phase 4 would drop it")
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


def recompute_manifest(current_nn, current_qs):
    titles = set()
    con = sqlite3.connect(DB)
    for (d,) in con.execute("SELECT source_page_description FROM questions "
                            "WHERE source_book=? AND source_page != ?", (BOOK, current_nn)):
        m = re.search(r"\[passage: ([^\]]+)\]", d or "")
        if m:
            titles.add(m.group(1))
    for f in other_batches(current_nn):
        titles |= {q["passage_title"] for q in json.loads(f.read_text(encoding="utf-8"))}
    titles |= {q["passage_title"] for q in current_qs}
    return {"passages": len(titles), "target_passages": TARGET_PASSAGES,
            "questions": len(titles) * BLANKS_PER_PASSAGE,
            "target_questions": TARGET_PASSAGES * BLANKS_PER_PASSAGE,
            "titles": sorted(titles)}


def main():
    nn = int(sys.argv[1])
    path = GEN / f"{BOOK}_p{nn}.json"
    qs = json.loads(path.read_text(encoding="utf-8"))

    errs = validate(qs, nn) + near_duplicates(qs, nn)
    if errs:
        print(f"VALIDATION FAILED ({len(errs)}):")
        for e in errs:
            print("  -", e)
        sys.exit(1)

    rng = random.Random(nn * 3571)
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
        if "[passage:" not in q["source_page_description"]:
            q["source_page_description"] += f" [passage: {q['passage_title']}]"

    path.write_text(json.dumps(qs, indent=2, ensure_ascii=False), encoding="utf-8")
    manifest = recompute_manifest(nn, qs)
    GEN.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8")

    npass = len({q["passage_title"] for q in qs})
    nhard = sum(1 for q in qs if q["difficulty"] == "hard")
    print(f"OK p{nn}: {len(qs)} q across {npass} passages, {nhard} hard")
    print(f"batch keys  { {a: sum(1 for q in qs if q['correct_answer'] == a) for a in 'ABCD'} }")
    print(f"running keys {dict(sorted(counts.items()))}")
    print(f"  passages {manifest['passages']}/{manifest['target_passages']}  "
          f"questions {manifest['questions']}/{manifest['target_questions']}")


if __name__ == "__main__":
    main()
