#!/usr/bin/env python3
"""Redraw the coordinate figures VIC review round 5 flagged, from their stated geometry.

Round 5 returned twelve flags. Five were coordinate planes whose points, lines or axes
are not where the stem puts them:

    11125ee3  "Point B is not correcly marked at the right coordinate (its at -2,2)"
    8139103c  "Fix the lines so they pass through the designated points."
    cdbdd5ae  "Again fix the line so it passes through the designated intercepts."
    709e977c  "Fix the graphs for the lines to line up with each value."
    25bbe5a8  "The y-axis should be within the square between the -1 and 3 points."

Every one is REDRAWN by figure_lib.plane rather than nudged. Round 4 patched figures in
place and all of them came back; the two redrawn from their geometry held. plane() puts
the axes, ticks, gridlines, dots and lines through a single mapping, so the class of
defect these five share cannot be expressed in its output.

Two things beyond the figures, both found while checking the keys rather than by any
sweep -- which is the round's other lesson:

  8139103c's explanation ends "The stored explanation derives x = 2 and then the
  question is keyed to (3,1)." That is a repair note from an earlier round written into
  the field a student reads, and it is also wrong: the key is (2,2) and correct.

  8139103c named F(2,2), which is the answer. A student who never draws anything can
  read the key off the stem. F moves to (1,0), which is the same line y = 2x - 2, so
  the key and the working are untouched.

Usage:
    python -m tools.repair_vic_round5_figures --dry-run
    python -m tools.repair_vic_round5_figures --apply
"""
import argparse
import json
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.figure_lib import plane            # noqa: E402
from tools import question_checks as qc       # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
MANIFEST = ROOT / "run_data/output/vic_round5_figure_repairs.json"

# Each entry rebuilds the figure from the coordinates the STEM states. Nothing here
# reads the old SVG -- that is what "redraw, do not patch" means in practice.
REPAIRS = {
    "11125ee3": dict(
        why="point B plotted at (-2, 2); the stem and the key put it at (-2, 3)",
        figure=lambda: plane(
            points={"A": (1, -1), "B": (-2, 3), "C": (2, 1), "D": (-1, -2)},
            xr=(-3, 3), yr=(-3, 4)),
    ),
    "8139103c": dict(
        why="neither line passed through the points it is labelled with",
        stem=("In the figure below, two straight lines intersect. One line passes "
              "through points C(0, 4) and D(4, 0). Another line passes through points "
              "E(0, −2) and F(1, 0). At what point do the two lines intersect?"),
        explanation=("Line CD through (0, 4) and (4, 0) has gradient −1, so it is "
                     "y = −x + 4. Line EF through (0, −2) and (1, 0) has gradient 2, "
                     "so it is y = 2x − 2. They meet where −x + 4 = 2x − 2, giving "
                     "3x = 6, x = 2 and y = 2. The lines intersect at (2, 2)."),
        figure=lambda: plane(
            points={"C": (0, 4), "D": (4, 0), "E": (0, -2), "F": (1, 0)},
            lines=[((0, 4), (4, 0)), ((0, -2), (1, 0))],
            xr=(-1, 5), yr=(-3, 5)),
    ),
    "cdbdd5ae": dict(
        why="the line missed both intercepts, and the (0, −6) label sat on the origin",
        figure=lambda: plane(
            points={"": (0, -6), " ": (4, 0)},
            lines=[((0, -6), (4, 0))],
            xr=(-2, 5), yr=(-6, 3), cell=25),
    ),
    "709e977c": dict(
        why="the grid was drawn 5 px left of its own ticks, so every point read 0.125 low",
        figure=lambda: plane(points=[(1, 1), (2, 3), (3, 5)], xr=(-1, 5), yr=(-1, 6)),
    ),
    "25bbe5a8": dict(
        why="the y-axis was drawn left of the square it should cut through",
        figure=lambda: plane(
            points={"(−1, 4)": (-1, 4), "(3, 4)": (3, 4), "(3, 0)": (3, 0),
                    "?": (-1, 0)},
            polygon=[(-1, 4), (3, 4), (3, 0), (-1, 0)],
            xr=(-2, 4), yr=(-1, 5), label_off=(0, -10)),
    ),
}

# Every figure check in the gate, run against the NEW svg. A redraw that trades this
# round's defect for one of the previous four rounds' is not a repair.
SVG_CHECKS = ["gridlines_off_the_ticks", "overlapping_text_labels", "axes_unlabelled",
              "axis_scale_nonlinear", "coordinate_figure_without_grid",
              "text_overlaps_geometry", "plotted_points_inconsistent",
              "angle_arc_malformed", "doubled_circle_outline"]
Q_CHECKS = ["plotted_geometry_matches_stem", "figure_proportions_disagree",
            "one_point_on_the_line", "options_distinct_by_value"]


def verify(q):
    out = []
    for n in SVG_CHECKS:
        if (m := getattr(qc, n)(q["figure_svg"])):
            out.append(f"{n}: {m}")
    for n in Q_CHECKS:
        if (m := getattr(qc, n)(q)):
            out.append(f"{n}: {m}")
    if (m := qc.figure_svg_errors(q["figure_svg"])):
        out += [f"figure_svg_errors: {x}" for x in m]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not (args.apply or args.dry_run):
        raise SystemExit("pass --apply or --dry-run")

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    record, failed = [], 0

    for prefix, spec in REPAIRS.items():
        row = con.execute("SELECT * FROM questions WHERE id LIKE ?||'%'",
                          (prefix,)).fetchone()
        if row is None:
            raise SystemExit(f"{prefix} is not in the database")
        q = dict(row)
        before = verify(q)
        q["figure_svg"] = spec["figure"]()
        for field in ("stem", "explanation"):
            if field in spec:
                q[field] = spec[field]
        after = verify(q)
        ok = not after
        failed += not ok
        print(f"{prefix}  {spec['why']}")
        print(f"    before: {len(before)} finding(s); after: {len(after)}"
              f"  {'OK' if ok else 'STILL FAILING'}")
        for a in after:
            print(f"      ! {a}")
        record.append(dict(id=row["id"], why=spec["why"], before=before, after=after,
                           form_id=row["form_id"], key=row["correct_answer"],
                           old_svg=row["figure_svg"], new_svg=q["figure_svg"],
                           old_stem=row["stem"], new_stem=q["stem"],
                           old_explanation=row["explanation"],
                           new_explanation=q["explanation"]))
        if args.apply and ok:
            con.execute("UPDATE questions SET figure_svg=?, stem=?, explanation=? "
                        "WHERE id=?", (q["figure_svg"], q["stem"], q["explanation"],
                                       row["id"]))

    if args.apply:
        if failed:
            con.rollback()
            raise SystemExit(f"\n{failed} figure(s) still failing — nothing written")
        con.commit()
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(json.dumps(record, indent=1, ensure_ascii=False))
        print(f"\napplied {len(record)} — manifest {MANIFEST}")
    else:
        print(f"\ndry run — {len(record)} figure(s), {failed} still failing")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
