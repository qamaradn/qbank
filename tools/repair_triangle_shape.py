#!/usr/bin/env python3
"""Redraw right triangles whose drawn sides disagree with their labelled lengths.

figure_proportions_disagree exempts triangles, correctly: the longest label on one is
usually a hypotenuse, and a hypotenuse crosses the bounding box rather than setting it.
So nothing in the bank had ever checked a triangle's SHAPE, and round 5 turned up two
flagged ones -- a 7 cm side drawn half again longer than its 24 cm one, and another 25%
out.

TRIAGE FIRST, and it mattered. A crude probe comparing the two longest drawn sides
against the two longest labels flagged 24. Comparing all THREE side ratios, and dropping
three-point polygons too small to be anything but an arrowhead, leaves 4. Two of those
are still false positives, read by hand:

    3869da13  its labels are 7.5, 9 and 15, but 7.5 is the MEDIAN to the hypotenuse, not
              a side. The sides are 9, 12, 15 and the figure draws them correctly.
    805a9fcc  a composite shape: the rectangle owns 8 and 9, the triangle owns 8 and 6.
              No single triangle has those three sides.

Two are real, both 5-12-13 right triangles drawn at neither shape.

Usage:
    python -m tools.repair_triangle_shape --dry-run | --apply
"""
import argparse
import json
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.figure_lib import right_triangle   # noqa: E402
from tools import question_checks as qc       # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
MANIFEST = ROOT / "run_data/output/triangle_shape_repairs.json"

REPAIRS = {
    "920b9b98": dict(
        why="PR 5, QR 12, PQ 13 drawn 140:150:205 — nothing like 5:12:13",
        figure=lambda: right_triangle(
            5, 12, corner="R", up="P", right="Q",
            up_label="5 cm", base_label="12 cm", hyp_label="13 cm",
            midpoint="M", max_px=170),
        check=lambda: abs(5**2 + 12**2 - 13**2) < 1e-9,
    ),
    "aa086624": dict(
        why="QR 5, PR 12, PQ 13 drawn 120:180:216 — the legs are the wrong way round",
        figure=lambda: right_triangle(
            12, 5, corner="R", up="P", right="Q",
            up_label="12 cm", base_label="5 cm", hyp_label="13 cm", max_px=170),
        check=lambda: abs(12**2 + 5**2 - 13**2) < 1e-9,
    ),
}

SVG_CHECKS = ["overlapping_text_labels", "text_overlaps_geometry", "axes_unlabelled",
              "angle_arc_malformed", "doubled_circle_outline",
              "plotted_points_inconsistent"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if not (a.apply or a.dry_run):
        raise SystemExit("pass --apply or --dry-run")
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rec, failed = [], 0
    for prefix, spec in REPAIRS.items():
        row = con.execute("SELECT * FROM questions WHERE id LIKE ?||'%'",
                          (prefix,)).fetchone()
        if not spec["check"]():
            raise SystemExit(f"{prefix}: the side lengths are not a right triangle")
        svg = spec["figure"]()
        bad = [f"{n}: {m}" for n in SVG_CHECKS if (m := getattr(qc, n)(svg))]
        bad += [f"figure_svg_errors: {x}" for x in (qc.figure_svg_errors(svg) or [])]
        q = dict(row, figure_svg=svg)
        if (m := qc.figure_proportions_disagree(q)):
            bad.append(f"figure_proportions_disagree: {m}")
        failed += bool(bad)
        print(f"{prefix}  {spec['why']}\n    {'OK' if not bad else 'STILL FAILING'}")
        for x in bad:
            print(f"      ! {x}")
        rec.append(dict(id=row["id"], why=spec["why"], form_id=row["form_id"],
                        status=row["review_status"], old_svg=row["figure_svg"],
                        new_svg=svg))
        if a.apply and not bad:
            con.execute("UPDATE questions SET figure_svg=? WHERE id=?", (svg, row["id"]))
    if a.apply:
        if failed:
            con.rollback()
            raise SystemExit("failing — nothing written")
        con.commit()
        MANIFEST.write_text(json.dumps(rec, indent=1, ensure_ascii=False))
        print(f"\napplied {len(rec)} — manifest {MANIFEST}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
