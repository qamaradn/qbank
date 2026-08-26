#!/usr/bin/env python3
"""Redraw the shape figures VIC round 5 flagged, and fix the one that needed no figure.

    e0621105  "the 5 Cm overlaps with the dotted line."
    79ab50fc  "add an angle symbol on angle R to make it obvious which one is being
               discussed."
    ce375557  "Ensure the angle values are always within the shape and the arc is always
               present without any overlapping."
    24386fc1  "For shapes, put the figure's dimension outside the triangle or uniform in
               every shape."
    8a048a4d  "If the answer requires approximation or rounding, always mention it in the
               question for clarity."

Three of those five notes say ALWAYS. They are conventions for the bank, not requests
about one picture, and figure_lib.right_triangle and .trapezium now hold them: every
dimension is placed on its own side's outward normal, and an angle is an arc at its
vertex with the value on the bisector inside the shape.

Reading the figures turned up more than the reviewer asked about, and it is the same
fault in both cases. figure_proportions_disagree deliberately exempts triangles, because
the longest label on one is usually a hypotenuse and a hypotenuse crosses the bounding
box rather than setting it. That exemption is sound and it meant nothing had looked at
the shape of a triangle in this bank:

    79ab50fc  QR is 7 cm and PQ is 24 cm. QR was drawn 180 px and PQ 140 px, so the
              short side was drawn HALF AGAIN LONGER than the long one.
    24386fc1  AC is 8 and CB is 15, a ratio of 0.53. They were drawn 120 and 180, a
              ratio of 0.67 -- 25% out.

Both are redrawn from their side lengths, which is the only reason they cannot recur:
right_triangle takes the lengths and derives the pixels, so the picture has no way to
disagree with the words.

8a048a4d carries no figure. Its answer was not exact -- 2w^2 + 35w - 125 = 0 gives
w = 3.04 -- and the reviewer is right that a question must say when it wants rounding.
Rounding is the worse of the two fixes here: the combined area becomes 496 m^2, the
quadratic factors as (w - 3)(2w + 41) = 0, and the answer is exactly 3. No option other
than 3 satisfies it, and the working no longer ends in an approximation the stem never
mentioned.

Usage:
    python -m tools.repair_vic_round5_shapes --dry-run
    python -m tools.repair_vic_round5_shapes --apply
"""
import argparse
import json
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.figure_lib import right_triangle, trapezium   # noqa: E402
from tools import question_checks as qc                  # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
MANIFEST = ROOT / "run_data/output/vic_round5_shape_repairs.json"

REPAIRS = {
    "e0621105": dict(
        why="the 5 cm label was written on top of the dashed height line",
        figure=lambda: trapezium(11, 7, 5, top_label="b", bottom_label="7 cm",
                                 height_label="5 cm"),
    ),
    "79ab50fc": dict(
        why="no arc marked angle R, and QR (7 cm) was drawn longer than PQ (24 cm)",
        figure=lambda: right_triangle(24, 7, corner="Q", up="P", right="R",
                                      hyp_label="25 cm", angle=("R", None)),
    ),
    "ce375557": dict(
        why="angle B carried no arc and its value sat outside the triangle",
        figure=lambda: right_triangle(8.6603, 5, corner="A", up="B", right="C",
                                      hyp_label="10 cm", angle=("B", "30°")),
    ),
    "24386fc1": dict(
        why="15 cm was labelled inside the triangle and ? outside; drawn 25% out of shape",
        figure=lambda: right_triangle(8, 15, corner="C", up="A", right="B",
                                      up_label="?", base_label="15 cm",
                                      hyp_label="17 cm"),
    ),
    "8a048a4d": dict(
        why="the answer was 3.04 and the stem never asked for rounding",
        stem=("A rectangular swimming pool measures 25 metres long and 10 metres wide. "
              "A uniform concrete path is to be built around the outside of the pool. "
              "If the combined area of the pool and the path is 496 square metres, what "
              "is the width of the path?"),
        explanation=("If the path is w metres wide, the outer rectangle measures "
                     "(25 + 2w) by (10 + 2w). So (25 + 2w)(10 + 2w) = 496, which gives "
                     "4w² + 70w + 250 = 496, or 2w² + 35w − 123 = 0. This factorises as "
                     "(w − 3)(2w + 41) = 0, so w = 3. Checking: 31 × 16 = 496 ✓"),
    ),
}

SVG_CHECKS = ["overlapping_text_labels", "text_overlaps_geometry", "axes_unlabelled",
              "angle_arc_malformed", "doubled_circle_outline", "gridlines_off_the_ticks",
              "plotted_points_inconsistent"]
Q_CHECKS = ["plotted_geometry_matches_stem", "figure_proportions_disagree",
            "rounds_without_saying_so", "calculator_required", "options_distinct_by_value"]


def verify(q):
    out = []
    if q.get("figure_svg"):
        for n in SVG_CHECKS:
            if (m := getattr(qc, n)(q["figure_svg"])):
                out.append(f"{n}: {m}")
        out += [f"figure_svg_errors: {x}" for x in (qc.figure_svg_errors(q["figure_svg"]) or [])]
    for n in Q_CHECKS:
        if (m := getattr(qc, n)(q)):
            out.append(f"{n}: {m}")
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
        if "figure" in spec:
            q["figure_svg"] = spec["figure"]()
        for field in ("stem", "explanation"):
            if field in spec:
                q[field] = spec[field]
        after = verify(q)
        failed += bool(after)
        print(f"{prefix}  {spec['why']}")
        print(f"    before {len(before)} / after {len(after)}"
              f"  {'OK' if not after else 'STILL FAILING'}")
        for a in after:
            print(f"      ! {a}")
        record.append(dict(id=row["id"], why=spec["why"], before=before, after=after,
                           key=row["correct_answer"], form_id=row["form_id"],
                           old_svg=row["figure_svg"], new_svg=q["figure_svg"],
                           old_stem=row["stem"], new_stem=q["stem"],
                           old_explanation=row["explanation"],
                           new_explanation=q["explanation"]))
        if args.apply and not after:
            con.execute("UPDATE questions SET figure_svg=?, stem=?, explanation=? "
                        "WHERE id=?", (q["figure_svg"], q["stem"], q["explanation"],
                                       row["id"]))
    if args.apply:
        if failed:
            con.rollback()
            raise SystemExit(f"\n{failed} still failing — nothing written")
        con.commit()
        MANIFEST.write_text(json.dumps(record, indent=1, ensure_ascii=False))
        print(f"\napplied {len(record)} — manifest {MANIFEST}")
    else:
        print(f"\ndry run — {len(record)} item(s), {failed} still failing")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
