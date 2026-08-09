#!/usr/bin/env python3
"""Finalise one NSW mathematics (Mathematical Reasoning) batch.

Validate -> near-dup screen -> balanced-shuffle -> update manifest + progress.

Usage:  env -u PYTHONPATH .venv/bin/python3.11 -m tools.ma_finalise <NN> [--check-only]

Subject-agnostic checks live in tools/question_checks.py. What is specific to maths, and
why it is here:

`ERRORS` — every distractor declares the mistake that produces it. A maths distractor is
not "a nearby number": it is the answer a student actually gets by making one identifiable
error. Three distinct error classes are required per question, which stops the standard
lazy set (key, key x 2, key / 2, key + 10) where a student who cannot do the question can
still see that one option is unlike the others. This mirrors the distractor-relation rule
that repaired the verbal_reasoning bank.

`tractability` — no calculator is allowed anywhere in this component, so an option that
carries more than two decimal places, or a money value that is not a whole number of
cents, means the arithmetic went somewhere a Year 6 candidate cannot follow by hand.

`unit_agreement` — if any option carries a unit, all four must, and they must be the same
unit. A bare number sitting among three "cm" options is answerable without the maths.

The builders compute every option rather than typing it, and each item carries a second
independent route to the same answer (`verify`). That is where correctness is actually
established: this module cannot re-derive the mathematics, it can only check the shape of
what the builder produced.
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
    KEYS,
    answer_shape_monotony,
    explanation_addresses_a_distractor,
    figure_svg_errors,
    length_tell,
    doubled_token_errors,
    options_distinct,
    positional_reference,
)

GEN = ROOT / "run_data/output/mathematics/generated"
PLAN = GEN / "ma_PLAN.json"
MANIFEST = GEN / "ma_MANIFEST.json"
PROGRESS = GEN / "MA_PROGRESS.md"
LOADED = GEN / "ma_LOADED.json"
DB = ROOT / "run_data/db/qbank.db"
BOOK = "ma_nsw_selective"

REQUIRED = ["id", "subject", "stem", *KEYS, "correct_answer", "explanation", "topic",
            "difficulty", "confidence", "source_book", "source_page",
            "source_page_description", "passage", "figure_svg", "review_status",
            "created_at", "category", "archetype", "errors"]

OPTIONAL = {"mixed_units", "no_shuffle"}

ARCHETYPES = {"multi_step", "single_step", "pattern_sequence",
              "data_interpretation", "geometry_measurement"}

# The mistake that produces a distractor. Every one of these has been observed in a real
# Year 6 script; a distractor that fits none of them is usually a random number.
ERRORS = {
    "operation_swap",      # multiplied where the problem divides, added where it subtracts
    "partial_step",        # the intermediate value — stopped one step short of the answer
    "wrong_attribute",     # perimeter for area, radius for diameter, mean for median
    "unit_error",          # no conversion, or converted the wrong way
    "off_by_one",          # fencepost counting, inclusive/exclusive endpoints
    "place_value",         # a factor of ten out
    "inverse",             # the reciprocal, or the complement of a probability
    "misread_data",        # read the wrong bar, row or column
    "ignored_constraint",  # dropped a condition the stem states
    "rounding",            # rounded at the wrong point, or the wrong way
    "double_count",        # counted a shared item twice
    "formula_slip",        # wrong variant of the right formula — triangle without the half
}

UNIT_RE = re.compile(r"^\s*\$?-?[\d\s,./]+\s*([a-zA-Z][a-zA-Z²³ ]*?)\s*$")
NUM_RE = re.compile(r"-?\d+(?:\.\d+)?")


def tractability_errors(q):
    """No calculator: an option a candidate cannot reach by hand is a defect in the item."""
    errs = []
    for k in KEYS:
        v = str(q.get(k, ""))
        for n in NUM_RE.findall(v):
            if "." in n and len(n.split(".")[1]) > 2:
                errs.append(f"option {v!r} has more than two decimal places — "
                            f"this component is sat without a calculator")
            if v.strip().startswith("$") and "." in n and len(n.split(".")[1]) != 2:
                errs.append(f"money option {v!r} is not a whole number of cents")
    return errs


def unit_agreement_errors(q):
    # A "which of these is longest" item mixes units on purpose — converting is the
    # question. Everything else that mixes them is testing reading, not reasoning.
    if q.get("mixed_units"):
        return []
    stop = {"the", "a", "an", "of", "per", "and", "or", "by", "to", "from",
            "plus", "minus", "times", "stage", "position", "number"}
    units = []
    for k in KEYS:
        m = UNIT_RE.match(str(q.get(k, "")))
        u = m.group(1).strip() if m else None
        words = u.split() if u else []
        if not words or len(words) > 2 or any(w.lower() in stop for w in words):
            u = None
        units.append(u)
    # "1 cube" and "6 cubes" are the same unit; only the count differs.
    units = [u if u is None else (u[:-1] if u.endswith("s") and not u.endswith("ss") else u)
             for u in units]
    named = [u for u in units if u]
    if named and len(named) != 4:
        return [f"only {len(named)} of 4 options carry a unit — a bare number among "
                f"united options is answerable without the mathematics"]
    if named and len(set(named)) != 1:
        return [f"options mix units {sorted(set(named))} — convert them to one unit, or "
                f"the question tests reading rather than reasoning"]
    return []


def distractor_error_errors(q, min_distinct=3):
    """Every distractor declares the mistake that yields it, and they must differ."""
    key = q[f"option_{q['correct_answer'].lower()}"]
    errmap = q.get("errors") or {}
    if not isinstance(errmap, dict):
        return ["'errors' must be a dict of distractor text -> error class"]
    errs, seen = [], []
    for k in KEYS:
        opt = q[k]
        if opt == key:
            continue
        if opt not in errmap:
            errs.append(f"distractor {opt!r} declares no error class")
            continue
        cls = errmap[opt]
        if cls not in ERRORS:
            errs.append(f"distractor {opt!r}: unknown error class {cls!r} "
                        f"(use one of {sorted(ERRORS)})")
        else:
            seen.append(cls)
    if len(errs) == 0 and len(set(seen)) < min_distinct:
        errs.append(f"the three distractors share only {len(set(seen))} error class(es) "
                    f"{sorted(set(seen))} — a student who cannot do the question can see "
                    f"which option is unlike the others")
    return errs


def explanation_cites_a_distractor(q):
    """Return an error if no wrong option's VALUE appears in the explanation.

    The shared prose version of this check tokenises on letters, so a numeric option like
    "48 cm" reduces to ["cm"] and any explanation mentioning centimetres satisfies it.
    Maths options are values, so the value is what has to be quoted back: an explanation
    that says only how to get the right answer leaves the student who got 48 with nothing.
    """
    key_letter = q["correct_answer"].lower()
    key = str(q[f"option_{key_letter}"])
    expl = str(q.get("explanation") or "")
    if not expl.strip():
        return "explanation is empty"
    expl_nums = set(NUM_RE.findall(expl))
    for k in KEYS:
        opt = str(q[k])
        if opt == key:
            continue
        nums = NUM_RE.findall(opt)
        if nums:
            if all(n in expl_nums for n in nums):
                return None
        elif explanation_addresses_a_distractor(q) is None:
            return None
    return ("no distractor value is quoted back in the explanation")


def category_of(q):
    return q.get("category")


def validate(qs, nn, plan):
    cats = {c["key"]: c for c in plan["categories"]}
    errs, seen_ids = [], set()
    for i, q in enumerate(qs):
        tag = f"q[{i}] {q.get('category', '?')}"
        missing = [f for f in REQUIRED if f not in q]
        if missing:
            errs.append(f"{tag}: missing field(s) {missing}")
            continue
        if q["subject"] != "mathematics":
            errs.append(f"{tag}: subject must be mathematics")
        if q["correct_answer"] not in ("A", "B", "C", "D"):
            errs.append(f"{tag}: bad correct_answer {q['correct_answer']!r}")
        if q["difficulty"] not in ("medium", "hard"):
            errs.append(f"{tag}: bad difficulty {q['difficulty']!r}")
        if q["review_status"] != "pending":
            errs.append(f"{tag}: review_status must be pending")
        if q["passage"] is not None:
            errs.append(f"{tag}: passage must be null for mathematics")
        if q["source_book"] != BOOK:
            errs.append(f"{tag}: source_book must be {BOOK!r}")
        if q["source_page"] != nn:
            errs.append(f"{tag}: source_page must be {nn}")
        if not (isinstance(q["confidence"], (int, float)) and 0.0 <= q["confidence"] <= 1.0):
            errs.append(f"{tag}: confidence out of range")
        if q["id"] in seen_ids:
            errs.append(f"{tag}: duplicate id")
        seen_ids.add(q["id"])
        if q["category"] not in cats:
            errs.append(f"{tag}: unknown category {q['category']!r}")
        elif q["topic"] != cats[q["category"]]["area"]:
            errs.append(f"{tag}: topic {q['topic']!r} does not match the category's "
                        f"area {cats[q['category']]['area']!r}")
        if q["archetype"] not in ARCHETYPES:
            errs.append(f"{tag}: unknown archetype {q['archetype']!r}")
        if not re.match(r"Category: (\w+) — (.+)$", q["source_page_description"]):
            errs.append(f"{tag}: source_page_description must be "
                        f"'Category: <key> — <title>' (em dash)")
        if not options_distinct(q):
            errs.append(f"{tag}: options not distinct")
        for msg in doubled_token_errors(q):
            errs.append(f"{tag}: {msg}")
        for e in figure_svg_errors(q.get("figure_svg")):
            errs.append(f"{tag}: {e}")
        if not q.get("figure_svg"):
            # Runs for every category, not just the ones flagged needs_figure: an averages
            # item shipped naming a frequency table it never showed, because its category
            # is not a figure category. What matters is whether the STEM points at
            # something the reader cannot see.
            if re.search(r"\bshown\b|\bdiagram\b|\bfigure\b|\bgraph\b|\bchart\b|\babove\b"
                         r"|\bthe table\b|\bthe timetable\b|\btable shows\b",
                         q["stem"], re.I):
                errs.append(f"{tag}: stem refers to a figure but figure_svg is empty")
        phrase = positional_reference(q["explanation"])
        if phrase:
            errs.append(f"{tag}: explanation refers to option positions ({phrase!r}) — "
                        f"options are shuffled at finalise")
        errs += [f"{tag}: {e}" for e in tractability_errors(q)]
        errs += [f"{tag}: {e}" for e in unit_agreement_errors(q)]
        errs += [f"{tag}: {e}" for e in distractor_error_errors(q)]
        if explanation_cites_a_distractor(q):
            errs.append(f"{tag}: the explanation never quotes a wrong option back — give "
                        f"the value a student would get and name the mistake that gets it")
    pool = qs + bank_questions(nn)
    errs += answer_shape_monotony(pool, group_of=category_of)
    errs += length_tell(pool, group_of=category_of)
    return errs


def loaded_set():
    return set(json.loads(LOADED.read_text(encoding="utf-8"))) if LOADED.exists() else set()


def batch_no(f):
    return int(re.search(r"_p(\d+)\.json$", f.name).group(1))


def other_batches(skip_nn):
    done = loaded_set()
    return [f for f in sorted(GEN.glob(f"{BOOK}_p*.json"))
            if batch_no(f) not in done and batch_no(f) != skip_nn]


def bank_questions(skip_nn):
    """Every NSW maths question already written — loaded, or pending in another batch.

    `category` and `errors` have no DB column, so a loaded row cannot be grouped by
    category. Batch files are read in full and DB rows are matched back to them by id,
    which keeps the quality pool from shrinking to the current batch as the build runs.
    """
    by_id = {}
    for f in sorted(GEN.glob(f"{BOOK}_p*.json")):
        if batch_no(f) == skip_nn:
            continue
        for q in json.loads(f.read_text(encoding="utf-8")):
            by_id[q["id"]] = q
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    # Exclude this batch's own loaded rows, or re-checking a batch that is already in the
    # DB reports every one of its stems as a 1.000 duplicate of itself.
    for r in con.execute("SELECT * FROM questions WHERE source_book=? AND source_page!=?",
                         (BOOK, skip_nn)):
        if r["id"] not in by_id:
            by_id[r["id"]] = dict(r)
    return list(by_id.values())


def near_duplicates(qs, nn, threshold=0.82):
    existing = [q["stem"] for q in bank_questions(nn)]
    errs, batch = [], []
    for q in qs:
        low = q["stem"].lower()
        for prev in batch + existing:
            r = SequenceMatcher(None, low, prev.lower()).ratio()
            if r >= threshold:
                errs.append(f"{q['category']}: stem {r:.3f} similar to {prev[:80]!r} — "
                            f"reword or phase 4 will drop it silently")
                break
        batch.append(q["stem"])
    return errs


def running_counts(skip_nn):
    c = collections.Counter()
    for q in bank_questions(skip_nn):
        c[q["correct_answer"]] += 1
    return c


def recompute_manifest(plan, current_nn, current_qs):
    have = collections.Counter()
    have_fig = collections.Counter()
    for q in bank_questions(current_nn) + current_qs:
        cat = q.get("category")
        if cat:
            have[cat] += 1
            if q.get("figure_svg"):
                have_fig[cat] += 1
    return [{"key": c["key"], "area": c["area"], "target": c["target"],
             "needs_figure": c["needs_figure"], "have": have[c["key"]],
             "have_figure": have_fig[c["key"]]} for c in plan["categories"]]


def write_progress(nn, line):
    header, entries = f"# {BOOK} — batch progress\n\n", {}
    if PROGRESS.exists():
        head = []
        for ln in PROGRESS.read_text(encoding="utf-8").split("\n"):
            m = re.match(r"^p(\d+)\s*\|", ln)
            if m:
                entries[int(m.group(1))] = ln
            elif ln.strip() or not entries:
                head.append(ln)
        header = "\n".join(head).rstrip() + "\n\n"
    entries[nn] = line.rstrip("\n")
    PROGRESS.write_text(header + "\n".join(entries[k] for k in sorted(entries)) + "\n",
                        encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("nn", type=int)
    ap.add_argument("--check-only", action="store_true")
    a = ap.parse_args()

    path = GEN / f"{BOOK}_p{a.nn}.json"
    qs = json.loads(path.read_text(encoding="utf-8"))
    plan = json.loads(PLAN.read_text(encoding="utf-8"))

    errs = validate(qs, a.nn, plan) + near_duplicates(qs, a.nn)
    if errs:
        print(f"VALIDATION FAILED ({len(errs)}):")
        for e in errs:
            print("  -", e)
        sys.exit(1)
    if a.check_only:
        print(f"OK (check-only) {path.name}: {len(qs)} questions, "
              f"{len(set(q['category'] for q in qs))} categories")
        return

    rng = random.Random(a.nn * 1009)
    counts = running_counts(a.nn)
    for q in qs:
        if q.pop("no_shuffle", False):
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

    manifest = recompute_manifest(plan, a.nn, qs)
    MANIFEST.write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8")

    cats = collections.Counter(q["category"] for q in qs)
    arch = collections.Counter(q["archetype"] for q in qs)
    nfig = sum(1 for q in qs if q.get("figure_svg"))
    nhard = sum(1 for q in qs if q["difficulty"] == "hard")
    write_progress(a.nn, f"p{a.nn:<3}| {', '.join(f'{k}x{v}' for k, v in cats.items()):<70}"
                         f"| {len(qs):>2} q | {nfig} fig | {nhard} hard | done")
    print(f"OK {path.name}: {len(qs)} q across {len(cats)} categories, {nfig} fig, {nhard} hard")
    print(f"batch keys  { {L: sum(1 for q in qs if q['correct_answer'] == L) for L in 'ABCD'} }")
    print(f"running keys {dict(sorted(counts.items()))}")
    print(f"archetypes  {dict(arch)}")
    built = sum(m["have"] for m in manifest)
    print(f"  categories {sum(1 for m in manifest if m['have'] >= m['target'])}/{len(manifest)}"
          f"  questions {built}/{sum(m['target'] for m in manifest)}")
    over = [m["key"] for m in manifest if m["have"] > m["target"]]
    if over:
        print(f"WARNING over-target: {over}")


if __name__ == "__main__":
    main()
