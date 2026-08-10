#!/usr/bin/env python3
"""Deals the NSW bank into fixed drill forms (selective_exam_delivery_SPEC.md §5.1, §6.2).

WHY NOT RANDOM
    §5.4 ranks a student against everyone who sat the same form. A form assembled at
    random can land four truth-tellers and no spatial work, and it still produces a
    percentile — one that quietly means something different from every other form's.

WHY NOT STRICTLY PROPORTIONAL EITHER
    Thinking Skills has 26 subcategories and a 20-question form. Twenty of them average
    under one question per form. A proportional form is not a thing that exists.

WHAT IT DOES INSTEAD
    Interleaves the strata, then places each question into whichever form is currently
    least like it — fewest of that subcategory, then that answer key, then that
    difficulty, then that build batch. The result spreads every axis at once without
    pretending a 20-slot form can mirror a 26-way taxonomy.

    Reading is dealt in whole passages, because a student must read the passage to answer
    any of it. Forms are packed to a SLOT target rather than a passage count: passages run
    4 to 8 slots, so four passages is anywhere from 16 to 32 questions, and the timer
    (§5.1.1) would range 19 to 38 minutes for what claims to be the same test.

REPRODUCIBILITY
    Deterministic given the seed. Refuses to overwrite an existing assignment without
    --force, because §5.1 requires fixed membership: once students have sat a form,
    re-dealing it orphans every percentile built against the old composition.
"""
import argparse
import collections
import datetime
import hashlib
import json
import os
import pathlib
import random
import re
import sqlite3

VERSION = 1
DB = os.environ.get("DB_PATH", "run_data/db/qbank.db")
MANIFEST = pathlib.Path("run_data/output/forms/nsw_forms_manifest.json")

# component -> (slug, source_book filter, questions per form, seconds per answer slot)
COMPONENTS = {
    "thinking_skills": ("ts", "source_book = 'lr_thinking_skills'", 20, 60),
    "mathematical_reasoning": ("math",
                               "source_book IN ('ma_nsw_selective','year7_nsw_maths')", 20, 69),
    "reading": ("read", "source_book LIKE 'rc_nsw_%'", 24, 71),
}

FAMILY = {
    "5.2 critical thinking": {"who_reasons_correctly", "identify_assumption",
                              "weaken_argument", "strengthen_argument",
                              "necessary_vs_sufficient", "identify_flaw",
                              "identify_conclusion", "correlation_vs_causation",
                              "conditional_chains"},
    "5.3 problem solving": {"numeric_deduction", "ordering_ranking", "syllogism_formal",
                            "logic_grid", "optimisation", "truth_teller",
                            "calendar_scheduling"},
    "5.4 spatial": {"shape_combination", "tessellation", "spatial_3d_views",
                    "orientation_rotation", "segment_display"},
}


def stratum(row):
    """What a question is, for spreading purposes: LR category, else its topic."""
    m = re.match(r"Category: (\w+)", row["spd"] or "")
    return m.group(1) if m else (row["topic"] or "untopiced")


def family_of(s):
    for f, ks in FAMILY.items():
        if s in ks:
            return f
    return "legacy"


def timer_seconds(slots, per_slot):
    """§5.1.1 — slots x the real exam allowance, rounded to the nearest 30 seconds."""
    return int(round(slots * per_slot / 30.0) * 30)


def even_sizes(total, per_form):
    """Split `total` into forms of `per_form` +/- 1, never leaving a stub form."""
    n = max(1, round(total / per_form))
    base, rem = divmod(total, n)
    return [base + 1] * rem + [base] * (n - rem)


def interleave(groups):
    """One from each group in turn, largest first, until all are spent."""
    order = sorted(groups, key=lambda k: -len(groups[k]))
    pools = {k: list(groups[k]) for k in order}
    out = []
    while any(pools.values()):
        for k in order:
            if pools[k]:
                out.append(pools[k].pop(0))
    return out


def deal_mcq(rows, per_form, rng):
    """Place each question into whichever form is currently least like it."""
    groups = collections.defaultdict(list)
    for r in rows:
        groups[stratum(r)].append(r)
    for k in groups:
        rng.shuffle(groups[k])
    sizes = even_sizes(len(rows), per_form)
    forms = [[] for _ in sizes]
    seen = [collections.Counter() for _ in sizes]

    for r in interleave(groups):
        s, key, diff, batch = stratum(r), r["ans"], r["diff"], r["page"]
        fam = family_of(s)
        best, best_cost = None, None
        for i, cap in enumerate(sizes):
            if len(forms[i]) >= cap:
                continue
            c = seen[i]
            # Subcategory spread dominates, then FAMILY. Weighting family explicitly
            # matters: with 26 subcategories the per-subcategory term alone left the
            # spatial family swinging 1 to 5 per form against a mean of 2.9, because
            # spreading five small subcategories evenly does not spread their sum evenly.
            cost = (c[("s", s)] * 100 + c[("f", fam)] * 30 + c[("k", key)] * 10
                    + c[("b", batch)] * 5 + c[("d", diff)] * 1 + len(forms[i]) * 0.01)
            if best_cost is None or cost < best_cost:
                best, best_cost = i, cost
        forms[best].append(r)
        seen[best].update([("s", s), ("f", fam), ("k", key), ("b", batch), ("d", diff)])
    return forms


def deal_reading(rows, slot_target, rng):
    """Whole passages, packed to a slot target rather than a passage count."""
    by_passage = collections.defaultdict(list)
    for r in rows:
        by_passage[(r["book"], r["passage"])].append(r)
    groups = collections.defaultdict(list)
    for (book, _), qs in by_passage.items():
        groups[book].append(qs)
    for k in groups:
        rng.shuffle(groups[k])

    passages = interleave(groups)
    total = sum(len(p) for p in passages)
    n = max(1, round(total / slot_target))
    forms, seen = [[] for _ in range(n)], [collections.Counter() for _ in range(n)]
    slots = [0] * n

    # Longest-first onto the emptiest form. Filling each form to the target before moving
    # on looks tidier and is wrong: the big passages go first, the small ones are left
    # with nowhere to sit, and the last forms come out as stubs. The first draft of this
    # produced forms of 6 to 27 slots — timers of 7 to 32 minutes for what is meant to be
    # the same test.
    for qs in sorted(passages, key=lambda p: -len(p)):
        book = qs[0]["book"]
        room = [i for i in range(n) if slots[i] + len(qs) <= slot_target + 3]
        pool = room or list(range(n))
        best = min(pool, key=lambda i: (slots[i], seen[i][book], i))
        forms[best].extend(qs)
        slots[best] += len(qs)
        seen[best][book] += 1
    return forms


def order_within(form, reading):
    """Fix the order §5.1 rule 1 requires.

    Reading keeps each passage's questions together — a student reads the passage once.
    Elsewhere consecutive questions are pushed apart by subcategory, so a form does not
    present three logic grids in a row.
    """
    if reading:
        out, groups = [], collections.OrderedDict()
        for r in form:
            groups.setdefault((r["book"], r["passage"]), []).append(r)
        for qs in groups.values():
            out.extend(qs)
        return out
    groups = collections.defaultdict(list)
    for r in form:
        groups[stratum(r)].append(r)
    return interleave(groups)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=DB)
    ap.add_argument("--seed", type=int, default=20260810)
    ap.add_argument("--status", default="approved,pending",
                    help="review_status values to include (default: approved,pending)")
    ap.add_argument("--component", action="append",
                    help="restrict to one component; repeatable")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true",
                    help="re-deal questions that already carry a form_id")
    a = ap.parse_args()

    statuses = [s.strip() for s in a.status.split(",")]
    conn = sqlite3.connect(a.db)
    conn.row_factory = sqlite3.Row
    wanted = a.component or list(COMPONENTS)
    manifest = {"version": VERSION, "seed": a.seed, "statuses": statuses,
                "generated_at": datetime.datetime.now(datetime.timezone.utc)
                .isoformat(timespec="seconds"), "components": {}}
    writes = []

    for comp in wanted:
        slug, where, per_form, per_slot = COMPONENTS[comp]
        q = (f"SELECT id, source_book AS book, source_page AS page, topic, "
             f"source_page_description AS spd, correct_answer AS ans, "
             f"difficulty AS diff, passage, form_id FROM questions "
             f"WHERE {where} AND review_status IN "
             f"({','.join('?' * len(statuses))}) ORDER BY id")
        rows = conn.execute(q, statuses).fetchall()
        already = [r for r in rows if r["form_id"]]
        if already and not a.force:
            raise SystemExit(
                f"{comp}: {len(already)} questions already carry a form_id. Re-dealing "
                f"breaks §5.1's fixed membership and orphans any percentile built on it. "
                f"Pass --force only if no student has sat these forms.")
        if not rows:
            print(f"{comp}: no questions match — skipped")
            continue

        rng = random.Random(a.seed + int(hashlib.sha1(comp.encode()).hexdigest()[:6], 16))
        forms = (deal_reading(rows, per_form, rng) if comp == "reading"
                 else deal_mcq(rows, per_form, rng))
        forms = [f for f in forms if f]

        entries = []
        for n, form in enumerate(forms, 1):
            form = order_within(form, comp == "reading")
            fid = f"nsw-drill-{slug}-{n:03d}"
            for pos, r in enumerate(form, 1):
                writes.append((fid, pos, "drill", r["id"]))
            strata = collections.Counter(stratum(r) for r in form)
            entries.append({
                "form_id": fid, "slots": len(form),
                "timer_seconds": timer_seconds(len(form), per_slot),
                "keys": dict(sorted(collections.Counter(r["ans"] for r in form).items())),
                "difficulty": dict(collections.Counter(r["diff"] for r in form)),
                "families": dict(sorted(collections.Counter(
                    family_of(s) for s in strata.elements()).items())),
                "strata": dict(sorted(strata.items())),
                "question_ids": [r["id"] for r in form],
            })
        manifest["components"][comp] = {
            "slug": slug, "questions": len(rows), "forms": len(entries),
            "seconds_per_slot": per_slot, "sets": entries}
        print(f"{comp:24} {len(rows):>5} questions -> {len(entries):>3} forms "
              f"({min(e['slots'] for e in entries)}-{max(e['slots'] for e in entries)} slots, "
              f"{min(e['timer_seconds'] for e in entries)//60}-"
              f"{max(e['timer_seconds'] for e in entries)//60} min)")

    if a.dry_run:
        print("\n--dry-run: nothing written")
        return
    conn.executemany("UPDATE questions SET form_id=?, form_position=?, form_kind=? "
                     "WHERE id=?", writes)
    conn.commit()
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=1))
    print(f"\nassigned {len(writes)} questions; manifest -> {MANIFEST}")


if __name__ == "__main__":
    main()
