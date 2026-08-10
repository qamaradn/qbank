#!/usr/bin/env python3
"""Finalise one logical_reasoning (NSW Thinking Skills) batch.

Validate -> originality screen -> near-dup screen -> balanced-shuffle -> update
manifest + progress.

Usage:  env -u PYTHONPATH .venv/bin/python3.11 -m tools.lr_finalise <NN>

This orchestrator is subject-specific: it knows the LR plan, manifest, batch naming and
`source_book`. The checks that are NOT subject-specific live in tools/question_checks.py
and are shared with every other subject — see that module for why each exists.

Set "no_shuffle": true on a question whose options are deliberately ordered
(ascending values, positional references in explanation). Stripped before rewrite.
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
sys.path.insert(0, str(ROOT))       # allow running as a plain script, not only via -m

from tools.question_checks import (  # noqa: E402
    KEYS,
    answer_shape_monotony,
    figure_svg_errors,
    length_tell,
    doubled_token_errors,
    option_wording_errors,
    options_distinct,
    positional_reference,
)

GEN = ROOT / "run_data/output/logical_reasoning/generated"
PLAN = GEN / "lr_PLAN.json"
MANIFEST = GEN / "lr_MANIFEST.json"
PROGRESS = GEN / "LR_PROGRESS.md"
# tools/load_batch.py records loaded batches as <book>_LOADED.json; the first thirteen
# batches were recorded by an earlier script as lr_LOADED.json. Reading only the old name
# meant every already-loaded batch was counted TWICE — once from its batch file and once
# from its DB rows — which inflated the manifest and the running key balance.
LOADED = GEN / "lr_thinking_skills_LOADED.json"
LOADED_LEGACY = GEN / "lr_LOADED.json"
DB = ROOT / "run_data/db/qbank.db"
REQUIRED = ["id", "subject", "stem", *KEYS, "correct_answer", "explanation", "topic",
            "difficulty", "confidence", "source_book", "source_page",
            "source_page_description", "passage", "figure_svg", "review_status", "created_at"]

# Scenario fragments lifted near-verbatim from the TASK briefing's quoted student /
# official-paper examples. These are provenance-flagged in the briefing as coming
# from a specific outside source, so batches must not reuse them even paraphrased -
# every LR question here must be an independently invented scenario.
BANNED_FRAGMENTS = [
    "monaro", "kevin", "taller adults", "larger feet",
    "reading at bedtime", "less sleep", "space exploration is a waste",
    "miserly", "parsimonious", "stingy",
]


def category_of(q):
    """LR labels its category in source_page_description as 'Category: <key> — <title>'."""
    m = re.match(r"Category: (\w+)", q.get("source_page_description") or "")
    return m.group(1) if m else None


def validate(qs, nn, plan):
    cats = {c["key"] for c in plan["categories"]}
    errs, seen_ids = [], set()
    for i, q in enumerate(qs):
        tag = f"q[{i}] {q.get('source_page_description', '?')}"
        for f in REQUIRED:
            if f not in q:
                errs.append(f"{tag}: missing field '{f}'")
        if q.get("subject") != "logical_reasoning":
            errs.append(f"{tag}: subject must be logical_reasoning")
        if q.get("correct_answer") not in ("A", "B", "C", "D"):
            errs.append(f"{tag}: bad correct_answer {q.get('correct_answer')!r}")
        if q.get("difficulty") not in ("medium", "hard"):
            errs.append(f"{tag}: bad difficulty {q.get('difficulty')!r}")
        if q.get("review_status") != "pending":
            errs.append(f"{tag}: review_status must be pending")
        if q.get("passage") is not None:
            errs.append(f"{tag}: passage must be null")
        if q.get("source_book") != "lr_thinking_skills":
            errs.append(f"{tag}: bad source_book")
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
        if not re.match(r"Category: (\w+) — (.+)$", q.get("source_page_description", "")):
            errs.append(f"{tag}: source_page_description must be 'Category: <key> — <title>' (em dash)")
        elif category_of(q) not in cats:
            errs.append(f"{tag}: unknown category {category_of(q)!r}")
        blob = " ".join(str(q.get(k, "")) for k in ["stem", "explanation", *KEYS]).lower()
        for frag in BANNED_FRAGMENTS:
            if frag in blob:
                errs.append(f"{tag}: contains banned source fragment {frag!r} — invent a new scenario")
        for e in figure_svg_errors(q.get("figure_svg")):
            errs.append(f"{tag}: {e}")
        # Explanations must not describe options by position: finalise shuffles them, so
        # "the first three pairs are anagrams" silently becomes false at load time. Three
        # questions shipped with exactly this defect before the check existed.
        phrase = positional_reference(q.get("explanation"))
        if phrase:
            errs.append(f"{tag}: explanation refers to option positions ({phrase!r}) — "
                        f"options get shuffled, so name the options instead or set no_shuffle")
    # Judged over the whole accumulated bank, not this batch alone. A batch contributes
    # ~4 questions per category, which is far too few for a share to mean anything —
    # p1's who_reasons_correctly ran 3-of-4 "<N> only" against a bank-wide 47%, which is
    # the correct rate for an archetype whose "A only" and "B only" share one shape.
    pool = qs + bank_questions(nn)
    errs += answer_shape_monotony(pool, group_of=category_of)
    errs += length_tell(pool, group_of=category_of)
    return errs


def bank_questions(skip_nn):
    """Every other LR question already written — loaded in the DB or pending in a batch."""
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute(
        "SELECT * FROM questions WHERE subject='logical_reasoning' "
        "AND NOT (source_book='lr_thinking_skills' AND source_page=?)", (skip_nn,))]
    for f in other_batches(skip_nn):
        rows += json.loads(f.read_text(encoding="utf-8"))
    return rows


def near_duplicates(qs, nn, threshold=0.82):
    con = sqlite3.connect(DB)
    existing = [r[0] for r in con.execute(
        "SELECT stem FROM questions WHERE subject='logical_reasoning' "
        "AND NOT (source_book='lr_thinking_skills' AND source_page=?)", (nn,)) if r[0]]
    for f in other_batches(nn):
        existing += [q["stem"] for q in json.loads(f.read_text(encoding="utf-8"))]
    errs, batch = [], []
    for q in qs:
        stem, low = q["stem"], q["stem"].lower()
        for prev in batch + existing:
            r = SequenceMatcher(None, low, prev.lower()).ratio()
            if r >= threshold:
                errs.append(f"{q['source_page_description']}: stem {r:.3f} similar to "
                            f"{prev[:90]!r} — reword or Phase 4 will drop it")
                break
        batch.append(stem)
    return errs


def loaded_set():
    done = set()
    for f in (LOADED, LOADED_LEGACY):
        if f.exists():
            done |= {int(re.search(r"(\d+)", str(x)).group(1)) if not isinstance(x, int) else x
                     for x in json.loads(f.read_text(encoding="utf-8"))}
    return done


def batch_no(f):
    return int(re.search(r"_p(\d+)\.json$", f.name).group(1))


def other_batches(skip_nn):
    done = loaded_set()
    return [f for f in sorted(GEN.glob("lr_thinking_skills_p*.json"))
            if batch_no(f) not in done and batch_no(f) != skip_nn]


def running_counts(skip_nn):
    c = collections.Counter()
    con = sqlite3.connect(DB)
    for a, n in con.execute("SELECT correct_answer, COUNT(*) FROM questions "
                            "WHERE source_book='lr_thinking_skills' GROUP BY 1"):
        c[a] += n
    for f in other_batches(skip_nn):
        for q in json.loads(f.read_text(encoding="utf-8")):
            c[q["correct_answer"]] += 1
    return c


def lock_loaded(qs, nn):
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = {r["stem"]: r for r in con.execute(
        "SELECT stem, option_a, option_b, option_c, option_d, correct_answer FROM questions "
        "WHERE source_book='lr_thinking_skills' AND source_page=?", (nn,))}
    locked = 0
    for q in qs:
        r = rows.get(q["stem"])
        if r:
            for k in KEYS:
                q[k] = r[k]
            q["correct_answer"] = r["correct_answer"]
            q["_locked"] = True
            locked += 1
    return locked


def recompute_manifest(plan, current_nn, current_qs):
    have = {c["key"]: 0 for c in plan["categories"]}
    have_figure = {c["key"]: 0 for c in plan["categories"]}
    rows = []
    con = sqlite3.connect(DB)
    rows += list(con.execute("SELECT source_page_description, figure_svg FROM questions "
                             "WHERE source_book='lr_thinking_skills' AND source_page != ?",
                             (current_nn,)))
    for f in other_batches(current_nn):
        rows += [(q["source_page_description"], q.get("figure_svg"))
                 for q in json.loads(f.read_text(encoding="utf-8"))]
    rows += [(q["source_page_description"], q.get("figure_svg")) for q in current_qs]
    for desc, fig in rows:
        m = re.match(r"Category: (\w+)", desc or "")
        if m and m.group(1) in have:
            have[m.group(1)] += 1
            if fig:
                have_figure[m.group(1)] += 1
    return [{"key": c["key"], "section": c["section"], "target": c["target"],
             "needs_figure": c["needs_figure"], "have": have[c["key"]],
             "have_figure": have_figure[c["key"]]} for c in plan["categories"]]


def write_progress(nn, line):
    header, entries = "# lr_thinking_skills — batch progress\n\n", {}
    if PROGRESS.exists():
        text = PROGRESS.read_text(encoding="utf-8")
        head_lines = []
        for ln in text.split("\n"):
            m = re.match(r"^p(\d+)\s*\|", ln)
            if m:
                entries[int(m.group(1))] = ln
            elif ln.strip() or not entries:
                head_lines.append(ln)
        header = "\n".join(head_lines).rstrip() + "\n\n"
    entries[nn] = line.rstrip("\n")
    PROGRESS.write_text(header + "\n".join(entries[k] for k in sorted(entries)) + "\n",
                        encoding="utf-8")


def main():
    nn = int(sys.argv[1])
    path = GEN / f"lr_thinking_skills_p{nn}.json"
    qs = json.loads(path.read_text(encoding="utf-8"))
    plan = json.loads(PLAN.read_text(encoding="utf-8"))

    errs = validate(qs, nn, plan)
    errs += near_duplicates(qs, nn)
    if errs:
        print(f"VALIDATION FAILED ({len(errs)}):")
        for e in errs:
            print("  -", e)
        sys.exit(1)

    rng = random.Random(nn * 1009)
    nlocked = lock_loaded(qs, nn)
    counts = running_counts(nn)
    for q in qs:
        if q.pop("_locked", False) or q.pop("no_shuffle", False):
            counts[q["correct_answer"]] += 1
            continue
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

    path.write_text(json.dumps(qs, indent=2, ensure_ascii=False), encoding="utf-8")

    manifest = recompute_manifest(plan, nn, qs)
    MANIFEST.write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8")

    cats_hit = collections.Counter(category_of(q) for q in qs)
    nfig = sum(1 for q in qs if q.get("figure_svg"))
    nhard = sum(1 for q in qs if q["difficulty"] == "hard")
    catstr = ", ".join(f"{k}x{v}" for k, v in cats_hit.items())
    lockmsg = f", {nlocked} locked" if nlocked else ""
    write_progress(nn, f"p{nn:<3}| {catstr:<60}| {len(qs):>2} q | {nfig} fig | {nhard} hard{lockmsg} | done")

    remaining = sum(m["target"] - m["have"] for m in manifest)
    print(f"OK p{nn}: {len(qs)} q, {nfig} fig, {nhard} hard{lockmsg} | batch keys "
          f"{ {a: sum(1 for q in qs if q['correct_answer'] == a) for a in 'ABCD'} }")
    print(f"running keys: {dict(sorted(counts.items()))}")
    print(f"remaining across all categories: {remaining}")
    over = [m["key"] for m in manifest if m["have"] > m["target"]]
    if over:
        print(f"WARNING over-target categories: {over}")


if __name__ == "__main__":
    main()
