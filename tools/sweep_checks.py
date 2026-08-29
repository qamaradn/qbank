"""Run the authoring checks over questions ALREADY in the bank.

`question_checks.py` was built as a gate for hand-authored batches: a builder emits a
batch, the finaliser runs the checks, and nothing loads until they pass. That is why NSW
came back 87/87 on a blind re-solve — every question cleared these before it ever entered
the bank. The Gemini and Sonnet books never went through it, because they arrived through
`phase3_generate` / `generate_direct`, which have no such gate.

So the standard is not unreachable retroactively. **15 of the 17 checks read nothing but
stored columns** — stem, options, key, explanation, passage, topic, figure_svg — and run
on a database row exactly as well as on a batch about to be written. This sweeps them.

THE TWO THAT CANNOT BE SWEPT, and why that matters. `distractor_relation_errors` and
`relation_monotony` need `relations`: a map declaring HOW EACH DISTRACTOR IS WRONG, keyed
by distractor text. That is a statement of authorial intent, not a property of the text,
so it is not in the database and cannot be recovered by any amount of parsing. It is also
the check that catches the defect the VIC verbal bank was measured to have — three
distractors that are mutual synonyms, leaving the key findable as the odd one out without
knowing the target word. A blind solver passes that question and is none the wiser.

That gap closes only by a human or a model READING the question and declaring the
relations, which is precisely the per-question pass this sweep is meant to precede: sweep
first so the mechanically-detectable failures are gone, then spend the expensive reading
on what is left.

WHAT A HIT MEANS. Not "reject". Most of these are triage signals — `length_tell` is a
property of a GROUP, not of any one question in it, and `unknown_words` is a typo screen
that fires on real Australian place names. Read the report, then decide.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.sweep_checks --scope vic
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.sweep_checks --scope vic --sample 3
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.sweep_checks --scope vic --manifest
"""

from __future__ import annotations

import argparse
import collections
import json
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools import question_checks as qc  # noqa: E402

DB_PATH = REPO_ROOT / "run_data" / "db" / "qbank.db"
MANIFEST = REPO_ROOT / "run_data" / "output" / "sweep_checks.json"

# Only questions that will actually be served. A withheld question is not worth repairing.
WITHHELD = [
    (REPO_ROOT / "run_data/output/vr_banned_types.json", "banned"),
    (REPO_ROOT / "run_data/output/qr_beyond_year8.json", "excluded"),
]

SCOPES = {
    "vic": "(subject = 'verbal_reasoning' OR subject = 'quantitative_reasoning' "
           "OR source_book IN ('year9_maths','ma_vic_stats') "
           "OR (subject = 'reading_comprehension' AND (source_book LIKE 'act_test%' "
           "OR source_book LIKE 'rc_vic_%')))",
    "nsw": "(subject = 'logical_reasoning' "
           "OR source_book IN ('year7_nsw_maths','ma_nsw_selective') "
           "OR (subject = 'reading_comprehension' AND source_book LIKE 'rc_nsw_%'))",
    "all": "1=1",
}


def withheld_ids() -> set[str]:
    out = set()
    for path, key in WITHHELD:
        if path.exists():
            out |= {r["id"] for r in json.loads(path.read_text()).get(key, [])}
    return out


def per_question(q: dict) -> list[tuple[str, str]]:
    """Checks that judge one question on its own. (check_name, detail)."""
    hits: list[tuple[str, str]] = []
    expl = q.get("explanation") or ""

    if not qc.options_distinct(q):
        hits.append(("options_distinct", "two options are identical"))
    if (m := qc.options_distinct_by_value(q)):
        hits.append(("options_distinct_by_value", m))
    if (m := qc.one_point_on_the_line(q)):
        hits.append(("one_point_on_the_line", m))
    for _name in ("markdown_table_in_stem", "invalid_clock_time", "teaching_manipulative",
                  "calculator_required", "non_integer_count"):
        if (m := getattr(qc, _name)(q)):
            hits.append((_name, m))
    for _name in ("negative_count", "no_question_asked", "compounding_needs_calculator",
                  "rounds_without_saying_so", "multi_letter_variable",
                  "asks_rationale_not_skill", "caret_power_notation",
                  "figure_proportions_disagree", "plotted_geometry_matches_stem",
                  "rounds_without_saying_so", "angle_named_without_arc",
                  "polygon_sides_disagree_with_stem"):
        if (m := getattr(qc, _name)(q)):
            hits.append((_name, m))
    if q.get("figure_svg"):
        for _name in ("doubled_circle_outline", "overlapping_text_labels",
                      "plotted_points_inconsistent", "text_overlaps_geometry",
                      "axes_unlabelled", "angle_arc_malformed",
                      "axis_scale_nonlinear", "coordinate_figure_without_grid",
                      "gridlines_off_the_ticks", "unknown_marker_far_from_point",
                      "label_too_faint"):
            if (m := getattr(qc, _name)(q["figure_svg"])):
                hits.append((_name, m))
    for name, fn in (("doubled_token_errors", qc.doubled_token_errors),
                     ("option_wording_errors", qc.option_wording_errors)):
        for e in fn(q) or []:
            hits.append((name, str(e)))
    for name, fn in (("leaked_working", qc.leaked_working),
                     ("rewrites_the_question", qc.rewrites_the_question),
                     ("positional_reference", qc.positional_reference)):
        got = fn(expl)
        if got:
            hits.append((name, str(got)))
    if qc.disputes_its_own_key(expl):
        hits.append(("disputes_its_own_key", "explanation argues with its own key"))
    got = qc.explanation_addresses_a_distractor(q)
    if got:
        hits.append(("explanation_addresses_a_distractor", str(got)))
    if q.get("passage"):
        got = qc.key_restates_passage(q)
        if got:
            hits.append(("key_restates_passage", str(got)))
    if q.get("figure_svg"):
        for e in qc.figure_svg_errors(q["figure_svg"]) or []:
            hits.append(("figure_svg_errors", str(e)))
    return hits


def group_checks(rows: list[dict]) -> list[tuple[str, str]]:
    """Checks that judge a GROUP. A hit indicts the group, not one question."""
    hits = []
    for name, fn in (("length_tell", qc.length_tell),
                     ("answer_shape_monotony", qc.answer_shape_monotony)):
        try:
            for e in fn(rows) or []:
                hits.append((name, str(e)))
        except Exception as exc:                      # a check that cannot run is news
            hits.append((name, f"could not run: {exc}"))
    return hits


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--scope", choices=sorted(SCOPES), default="vic")
    ap.add_argument("--sample", type=int, default=0, help="print N examples per check")
    ap.add_argument("--manifest", action="store_true")
    ap.add_argument("--include-withheld", action="store_true")
    args = ap.parse_args()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute(
        f"SELECT * FROM questions WHERE review_status != 'rejected' AND {SCOPES[args.scope]}")]
    held = set() if args.include_withheld else withheld_ids()
    rows = [r for r in rows if r["id"] not in held]
    print(f"scope {args.scope}: {len(rows)} served questions\n")

    found: dict[str, list[dict]] = collections.defaultdict(list)
    for q in rows:
        for name, detail in per_question(q):
            found[name].append({"id": q["id"], "book": q["source_book"],
                                "status": q["review_status"], "detail": detail,
                                "stem": " ".join((q["stem"] or "").split())[:110]})

    by_book = collections.defaultdict(list)
    for q in rows:
        by_book[q["source_book"]].append(q)
    for book, qs in sorted(by_book.items()):
        for name, detail in group_checks(qs):
            found[name].append({"id": None, "book": book, "status": "-",
                                "detail": detail, "stem": ""})

    print(f"{'check':<38}{'hits':>7}   {'affected books':>14}")
    total = 0
    for name in sorted(found, key=lambda k: -len(found[k])):
        hits = found[name]
        total += len(hits)
        print(f"  {name:<36}{len(hits):>7}   {len({h['book'] for h in hits}):>14}")
    print(f"  {'TOTAL':<36}{total:>7}")
    ids = {h["id"] for hs in found.values() for h in hs if h["id"]}
    print(f"\n{len(ids)} distinct questions flagged "
          f"({100*len(ids)/len(rows):.1f}% of the served scope)")

    if args.sample:
        for name in sorted(found, key=lambda k: -len(found[k])):
            print(f"\n=== {name} ===")
            for h in found[name][:args.sample]:
                print(f"  [{h['book']}/{h['status']}] {h['detail'][:150]}")
                if h["stem"]:
                    print(f"      {h['stem']}")

    if args.manifest:
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(json.dumps(
            {"generated_from": "tools/sweep_checks.py", "scope": args.scope,
             "served": len(rows), "flagged": sorted(ids),
             "by_check": {k: v for k, v in found.items()}}, indent=2))
        print(f"\nwrote {MANIFEST}")


if __name__ == "__main__":
    main()
