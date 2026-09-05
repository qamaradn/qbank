#!/usr/bin/env python3
"""Refuse to author a figure that would draw a reviewer's comment.

WHY THIS EXISTS. Four review rounds over 445 VIC maths figures produced 304 distinct
reviewer comments. Counted:

    45%  a number or letter sitting on a line
    15%  a missing scale, gridlines, or axis numbers
     4%  a label too far from the thing it names
     3%  the figure disagreeing with its own numbers
     2%  a shape drawn wrong, not closing, or inverted

Every one of those has a check in `question_checks.py`. The checks were written DURING
the repair rounds and then only ever run during repair rounds -- the authoring path
(`ma_finalise`) ran exactly one of the seventeen, `figure_svg_errors`, which looks at
bytes and colours and never at where anything is drawn. So the same defects kept being
authored, shipped, reviewed, and repaired one at a time.

This runs the whole set at authoring time, on the batch being written, before it is
loaded. A figure that fails here is a figure a reviewer would have sent back.

    from tools.figure_gate import figure_findings
    for msg in figure_findings(question_dict):
        errs.append(f"{tag}: {msg}")

Two of the checks answer "needs a human" rather than yes or no, and those are reported
as advisories: they are returned by `figure_findings(q, advisory=True)` and are NOT
errors, because a builder cannot resolve them and a gate that cannot be satisfied gets
switched off.
"""
from __future__ import annotations

import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from tools import question_checks as qc                       # noqa: E402

# Checks that take the SVG alone. Every one of these was written because a reviewer
# reported the thing it looks for.
SVG_CHECKS = (
    "text_overlaps_geometry",           # 45% of all comments
    "overlapping_text_labels",
    "coordinate_figure_without_grid",   # part of the 15%
    "axes_unlabelled",
    "axis_scale_nonlinear",
    "gridlines_off_the_ticks",
    "gridlines_stop_short_of_the_axes",
    "axis_shorter_than_the_data",
    "plotted_points_inconsistent",
    "angle_arc_malformed",
    "angle_arc_misses_its_rays",
    "unknown_marker_far_from_point",
    "undefined_marker_reference",
    "label_too_faint",
    "text_outside_the_canvas",
    "doubled_circle_outline",
    "figure_svg_errors",
)

# Checks that need the whole question, because they compare the drawing to the words.
QUESTION_CHECKS = (
    "angle_named_without_arc",
    "polygon_sides_disagree_with_stem",
    "plotted_geometry_matches_stem",
    "figure_proportions_disagree",
)

# These return a "needs a human" verdict rather than a defect. Reported, never blocking.
ADVISORY = {"figure_proportions_disagree"}


def figure_findings(q: dict, advisory: bool = False) -> list[str]:
    """Every figure defect in this question. Empty means it would pass a review round.

    `advisory=True` returns only the judgement calls a builder cannot fix; the default
    returns only the ones it can and should."""
    svg = (q or {}).get("figure_svg") or ""
    if not svg.strip():
        return []
    out = []
    for name in SVG_CHECKS:
        if name in ADVISORY:
            continue
        hit = getattr(qc, name)(svg)
        if hit:
            out += [str(h) for h in hit] if isinstance(hit, list) else [str(hit)]
    for name in QUESTION_CHECKS:
        if (name in ADVISORY) != advisory:
            continue
        hit = getattr(qc, name)(q)
        if hit:
            out += [str(h) for h in hit] if isinstance(hit, list) else [str(hit)]
    if advisory:
        return out
    return [m for m in out if "needs a human" not in m.lower()]


def main() -> None:
    """Run the gate over a batch file or a whole source book, to calibrate it."""
    import argparse
    import collections
    import json
    import re
    import sqlite3

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--batch", type=pathlib.Path, help="a batch JSON to check")
    ap.add_argument("--book", help="check every figure already loaded from this book")
    ap.add_argument("--form-prefix", help="check every figure in forms with this prefix")
    args = ap.parse_args()

    if args.batch:
        rows = json.loads(args.batch.read_text())
        rows = rows if isinstance(rows, list) else rows.get("questions", [])
    else:
        db = pathlib.Path(__file__).resolve().parents[1] / "run_data/db/qbank.db"
        con = sqlite3.connect(db)
        con.row_factory = sqlite3.Row
        where, params = "figure_svg IS NOT NULL AND figure_svg != ''", []
        if args.book:
            where += " AND source_book = ?"
            params.append(args.book)
        if args.form_prefix:
            where += " AND form_id LIKE ?"
            params.append(args.form_prefix + "%")
        rows = [dict(r) for r in con.execute(
            f"SELECT * FROM questions WHERE {where}", params)]

    counts, bad = collections.Counter(), 0
    for q in rows:
        found = figure_findings(q)
        if found:
            bad += 1
            for m in found:
                counts[re.split(r"[ ']", m.strip())[0].strip(":")] += 1
    print(f"figures checked : {len(rows)}")
    print(f"with a finding  : {bad}"
          + (f"  ({100 * bad / len(rows):.0f}%)" if rows else ""))
    for k, v in counts.most_common(12):
        print(f"   {k:<28} {v}")


if __name__ == "__main__":
    main()
