#!/usr/bin/env python3
"""Refuse to ship a set of forms that repeats a defect a reviewer already found.

Run this before every push. It applies the subject-agnostic checks in
`question_checks` to exactly the forms about to go out, and exits non-zero if any
BLOCKING check fires.

Two tiers, because not every check means "do not ship":

  BLOCKING  — defects a reviewer flagged, or that make a question unanswerable or
              wrongly marked. These are cheap to fix and indefensible to ship.
  ADVISORY  — quality signals with real false-positive rates
              (`explanation_addresses_a_distractor` fires on 35% of the bank, mostly
              because maths options are numbers and cannot be quoted back). Reported,
              never blocking. Promoting one of these to BLOCKING without first driving
              its count down would make the gate meaningless, and a gate everyone
              overrides is worse than no gate.

Usage:
    python -m tools.gate_forms --forms nsw-drill-math-003,nsw-drill-math-004
    python -m tools.gate_forms --next-push        # everything approved and unsent
"""
import argparse
import json
import pathlib
import sqlite3
import sys
from collections import Counter, defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import question_checks as qc  # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
TRACKING = ROOT / "run_data/db/pushed_to_selectly.json"

# Every one of these was written from a real defect. The comment names the round.
# SHARED — nothing here depends on which exam the question serves. A table that will
# not render, a time that cannot exist, an answer that needs a calculator: all of these
# are wrong for a Year 6 paper and a Year 8 paper alike.
BLOCKING = [
    ("options_distinct_by_value", "blind-solve: two options with the same value"),
    ("one_point_on_the_line", "blind-solve: more than one option satisfies the stem"),
    ("markdown_table_in_stem", "NSW round 1: table renders as raw pipes"),
    ("invalid_clock_time", "NSW round 1: a time that cannot exist, e.g. 2:65 am"),
    ("teaching_manipulative", "NSW round 1: tests classroom materials, not maths"),
    ("calculator_required", "NSW round 1: key is a decimal only a calculator gives"),
    ("non_integer_count", "NSW round 1: fractional answer to 'how many'"),
    ("leaked_working", "Aug 2026: the model's own reasoning left in the explanation"),
    ("rewrites_the_question", "Aug 2026: explanation edits the stem, so the item is unanswerable"),
    ("negative_count", "VIC round 1: a count that cannot be negative, e.g. −1 wickets"),
    ("no_question_asked", "VIC round 1: the stem never asks anything"),
    ("compounding_needs_calculator", "VIC round 1: compounding or a chain of percentages"),
    ("doubled_circle_outline", "VIC round 1: circumference drawn twice"),
    ("plotted_points_inconsistent", "VIC round 1: points not plotted to one scale"),
    # Promoted from advisory after VIC round 2. It had already caught the graph whose
    # axis title printed through the tick numbers -- the check was right and its tier
    # was wrong, so the gate waved it through and a reviewer had to find it.
    ("overlapping_text_labels", "VIC round 2: two labels printed over each other"),
    ("text_overlaps_geometry", "VIC round 2: a label printed over a plotted line"),
    ("axes_unlabelled", "VIC round 2: a chart with no axis titles"),
    ("angle_arc_malformed", "VIC round 2: angle mark not centred on its vertex"),
    ("axis_scale_nonlinear", "VIC round 4: axis ticks not evenly spaced for their values"),
    ("coordinate_figure_without_grid", "VIC round 4: a plane with no gridlines to read"),
    ("multi_letter_variable", "VIC round 4: T_wc reads as a product of unknowns"),
    ("asks_rationale_not_skill", "VIC round 4: asks why a method is preferred"),
    ("figure_proportions_disagree", "VIC round 4: shape drawn to the wrong proportions"),
]

# EXAM-SPECIFIC — two things genuinely differ, and only two.
#
#   Year level. NSW selective is sat in Year 6; VIC is sat in Year 8. A question that is
#   fair for one may be out of reach for the other, which is why the same reviewer note
#   ("quite difficult for a year 6", "a little difficult for year 8s") arrived from both
#   rounds about different questions.
#
#   Banned types. The VIC brief (§6) forbids word codes, hidden words, anagrams,
#   alphabetical ordering and alphabet-position items. NSW Thinking Skills legitimately
#   contains some of that family, so the same question is off-spec in one exam and in
#   spec in the other.
#
# Everything else is shared. Resist adding to this: a check that differs per exam has to
# earn it, or the two gates drift apart and neither is trusted.
EXAM_BLOCKING = {
    "vic": [("teaching_manipulative",
             "VIC: tests classroom materials rather than reasoning")],
    "nsw": [("teaching_manipulative",
             "NSW round 1: tests classroom materials rather than reasoning")],
}

# Off-spec question types, VIC only. Sourced from the committed manifest rather than a
# regex, because tools/vr_banned_types.py records which rule fired on each row.
BANNED_MANIFEST = ROOT / "run_data/output/vr_banned_types.json"

# Reported, never blocking. These have real false-positive rates -- 
# explanation_addresses_a_distractor fires on a third of the bank because maths options
# are numbers and cannot be quoted back in prose, and overlapping_text_labels estimates
# glyph widths from character counts. A gate that people routinely override is worse
# than no gate, so these stay advisory until their counts come down.
ADVISORY = ["length_tell", "positional_reference", "key_restates_passage",
            "explanation_addresses_a_distractor", "figure_svg_errors",
]


# The checks do not share a calling convention -- some take the question dict, some a
# single field, one takes the whole batch. Dispatch explicitly rather than guessing:
# a wrong guess here makes a check silently never fire, which is worse than a crash.
_TEXT_FIELD = {
    "text_overlaps_geometry": "figure_svg",
    "axes_unlabelled": "figure_svg",
    "angle_arc_malformed": "figure_svg",
    "axis_scale_nonlinear": "figure_svg",
    "coordinate_figure_without_grid": "figure_svg",
    "doubled_circle_outline": "figure_svg",
    "overlapping_text_labels": "figure_svg",
    "plotted_points_inconsistent": "figure_svg",
    "positional_reference": "stem",
    "leaked_working": "explanation",
    "rewrites_the_question": "explanation",
    "figure_svg_errors": "figure_svg",
}
_BATCH = {"length_tell", "answer_shape_monotony"}


def run_check(name, q):
    if name in _BATCH:
        return None                      # handled over the whole set, not per question
    fn = getattr(qc, name)
    if name in _TEXT_FIELD:
        val = q.get(_TEXT_FIELD[name])
        if not val:
            return None
        out = fn(val)
    else:
        out = fn(q)
    if out is None or out is False:
        return None
    if out is True:
        return f"{name} failed"
    if isinstance(out, (list, tuple)):
        return "; ".join(str(x) for x in out) if out else None
    return str(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--forms", default="", help="comma-separated form_ids")
    ap.add_argument("--next-push", action="store_true",
                    help="gate everything approved that has not been sent yet")
    ap.add_argument("--exam", choices=["nsw", "vic"], default=None,
                    help="apply the exam-specific checks as well as the shared ones")
    ap.add_argument("--show", type=int, default=12, help="max examples per check")
    args = ap.parse_args()

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row

    if args.next_push:
        sent = set(json.loads(TRACKING.read_text()).get("pushed", {})) if TRACKING.exists() else set()
        rows = [dict(r) for r in con.execute(
            "SELECT * FROM questions WHERE review_status='approved'")]
        rows = [r for r in rows if r["id"] not in sent]
        scope = f"{len(rows)} approved and not yet sent"
    else:
        forms = [f.strip() for f in args.forms.split(",") if f.strip()]
        if not forms:
            raise SystemExit("pass --forms or --next-push")
        rows = [dict(r) for r in con.execute(
            f"SELECT * FROM questions WHERE review_status!='rejected' AND form_id IN "
            f"({','.join('?' * len(forms))})", forms)]
        scope = f"{len(rows)} questions in {len(forms)} form(s)"

    if not rows:
        print(f"nothing to gate ({scope})")
        return 0

    checks = list(BLOCKING) + EXAM_BLOCKING.get(args.exam or "", [])
    if args.exam is None:
        # Infer from the forms rather than silently skipping the exam-specific tier.
        exams = {f.split("-")[0] for f in {r["form_id"] or "" for r in rows} if f}
        if len(exams) == 1:
            inferred = exams.pop()
            checks = list(BLOCKING) + EXAM_BLOCKING.get(inferred, [])
            print(f"(exam inferred from the forms: {inferred})")

    blocking_hits = defaultdict(list)
    advisory_counts = Counter()
    for r in rows:
        for name, _why in checks:
            if (m := run_check(name, r)):
                blocking_hits[name].append((r, m))
        for name in ADVISORY:
            if run_check(name, r):
                advisory_counts[name] += 1

    print(f"GATE — {scope}\n")
    total = sum(len(v) for v in blocking_hits.values())
    if advisory_counts:
        print("advisory (not blocking):")
        for n, c in advisory_counts.most_common():
            print(f"   {n:<38}{c:>5}")
        print()

    if not total:
        print("BLOCKING CHECKS: all clear — safe to push")
        return 0

    print(f"BLOCKING CHECKS: {total} failure(s) across "
          f"{len(blocking_hits)} check(s)\n")
    why = dict(checks)
    for name, hits in sorted(blocking_hits.items(), key=lambda x: -len(x[1])):
        print(f"  {name} — {len(hits)}   ({why[name]})")
        for r, m in hits[:args.show]:
            print(f"     [{r['form_id']} pos {r['form_position']}] {m}")
            print(f"        {' '.join((r['stem'] or '').split())[:90]}")
        if len(hits) > args.show:
            print(f"     ... and {len(hits) - args.show} more")
        print()
    print("DO NOT PUSH until these are fixed or explicitly accepted.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
