#!/usr/bin/env python3
"""Redraw the VIC coordinate figures that disagree with, or cannot be checked
against, their own stems.

`repair_coordinate_figures` declined these with honest reasons -- "needs an angle
arc at the origin", "the distractor points exist only in the old figure", "a
transformation: the figure is the pre-image and the answer is the image". Each
reason is a thing `plane()` alone cannot supply. This supplies them, one entry per
question, with the geometry read out of the stem and nothing invented.

Every stem here names its points explicitly, so nothing is guessed: A(1, 5),
B(1, 1), C(7, 1) is what the figure draws, and the key is re-derived from those
same numbers before the entry is written.

WHY REDRAW RATHER THAN PATCH, again. One of these labels the line through B(1, 1)
and C(7, 1) as the x-axis, arrowhead and all, so a student reads two points that
are one unit up as sitting on y = 0. Nudging cannot fix a figure whose axis is in
the wrong place; only deriving the picture from the numbers can.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_vic_figure_pass --dry-run
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_vic_figure_pass --apply
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import figure_lib as fl                       # noqa: E402
from tools import gate_forms as gf                       # noqa: E402
from tools import question_checks as qc                  # noqa: E402
from tools.repair_label_collisions import repair as denude  # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
MANIFEST = ROOT / "run_data/output/vic_figure_pass_repairs.json"


def ray_with_angle(px, py, label, xr, yr, cell=26, extra=None):
    """A plane with a ray from the origin to (px, py) and the angle it makes marked.

    `plane` clips a line to the plot edge, which is right for "the line through A
    and B" and wrong for "the line drawn FROM the origin TO P" -- the angle at the
    origin is between the positive x-axis and a ray, and a line running out the
    other side into the third quadrant invites the reflex reading. So the ray is
    drawn here rather than handed to `plane`, and the arc comes from the same two
    directions the ray and the axis actually have.
    """
    svg = fl.plane(points={"": (px, py)}, xr=xr, yr=yr, cell=cell)
    x0, x1 = xr
    y0, y1 = yr
    ox, oy = 22 + 16, 22

    def to_px(x, y):
        return ox + (x - x0) * cell, oy + (y1 - y) * cell
    o = to_px(0, 0)
    p = to_px(px, py)
    body = (f'<line x1="{o[0]:.0f}" y1="{o[1]:.0f}" x2="{p[0]:.0f}" y2="{p[1]:.0f}" '
            f'stroke="currentColor" stroke-width="2" stroke-opacity=".9"/>')
    a_axis = 0.0                                   # positive x-axis, screen coords
    a_ray = math.atan2(p[1] - o[1], p[0] - o[0])
    lo, hi = (a_ray, a_axis) if a_ray < 0 else (a_axis, a_ray)
    body += fl.angle_mark(o, lo, hi, 22.0, label=label)
    bis = (lo + hi) / 2
    body += fl.txt(o[0] + 36 * math.cos(bis), o[1] + 36 * math.sin(bis) + 4, label, 13)
    body += (f'<text x="{p[0] + 8:.0f}" y="{p[1] - 8:.0f}" font-family="system-ui,'
             f'sans-serif" font-size="12" fill="currentColor" fill-opacity=".9">'
             f'({px:g}, {py:g})</text>')
    return svg.replace("</svg>", body + (extra or "") + "</svg>")


REPAIRS = {
    "7ef62748": ("phi at the origin; the only polygons were arrowheads",
                 lambda: ray_with_angle(5, 5, "φ", (-1, 6), (-1, 6))),
    "61638577": ("theta at the origin, ray to (3, 3)",
                 lambda: ray_with_angle(3, 3, "θ", (-1, 4), (-1, 4), cell=34)),
    "a66ee7e4": ("alpha at the origin, ray to (6, 8)",
                 lambda: ray_with_angle(6, 8, "α", (-1, 8), (-1, 9), cell=22)),
    "ccb2dfba": ("the angle AB makes with the positive x-axis, B at (8, 6)",
                 lambda: ray_with_angle(8, 6, "∠BAx", (-1, 9), (-1, 7), cell=22)),
    "c004fdff": ("the line through B(1,1) and C(7,1) was drawn AS the x-axis",
                 lambda: fl.plane(points={"A(1, 5)": (1, 5), "B(1, 1)": (1, 1),
                                          "C(7, 1)": (7, 1)},
                                  polygon=[(1, 5), (1, 1), (7, 1)],
                                  xr=(-1, 8), yr=(-1, 6), cell=24)),
    "fa7b38b8": ("the pre-image triangle A(1,4) B(4,4) C(4,1)",
                 lambda: fl.plane(points={"A(1, 4)": (1, 4), "B(4, 4)": (4, 4),
                                          "C(4, 1)": (4, 1)},
                                  polygon=[(1, 4), (4, 4), (4, 1)],
                                  xr=(-5, 5), yr=(-5, 5), cell=22)),
    "6fd2caba": ("Q(5, 10) was plotted off the line it names",
                 lambda: fl.plane(points={"P(1, 2)": (1, 2), "Q(5, 10)": (5, 10)},
                                  lines=[((1, 2), (5, 10))],
                                  xr=(-1, 7), yr=(-1, 11), cell=20)),
    "7cc5d3c3": ("the y-axis was drawn at x = -1.3 by its own labels",
                 lambda: fl.plane(points={"M(−4, −1)": (-4, -1), "N(2, 8)": (2, 8)},
                                  lines=[((-4, -1), (2, 8))],
                                  xr=(-6, 4), yr=(-3, 9), cell=20)),
    "83cefc22": ("the x-axis was drawn at y = 1 by its own labels",
                 lambda: fl.plane(points={"A(1, 2)": (1, 2), "B(7, 10)": (7, 10),
                                          "M(4, 6)": (4, 6)},
                                  lines=[((1, 2), (7, 10))],
                                  xr=(-1, 9), yr=(-1, 11), cell=20)),
    "0f936d02": ("the line's position was not given by any point on it",
                 lambda: fl.plane(points={"(3, −4)": (3, -4)},
                                  lines=[((-5, -4), (5, -4))],
                                  xr=(-5, 5), yr=(-6, 4), cell=22)),
    "6c2145b3": ("two named lines, one defined relative to the other",
                 lambda: fl.plane(points={"(0, 2)": (0, 2), "(3, 8)": (3, 8),
                                          "(0, −1)": (0, -1)},
                                  lines=[((0, 2), (3, 8)), ((0, -1), (3, 5))],
                                  xr=(-2, 7), yr=(-3, 10), cell=20)),
    "960e31fb": ("triangle P(1,2) Q(7,2) R(4,8), points not to one scale",
                 lambda: fl.plane(points={"P(1, 2)": (1, 2), "Q(7, 2)": (7, 2),
                                          "R(4, 8)": (4, 8)},
                                  polygon=[(1, 2), (7, 2), (4, 8)],
                                  xr=(-1, 8), yr=(-1, 9), cell=22)),
    "2f330d5e": ("A(1,2) B(5,2) C(5,8), points not to one scale",
                 lambda: fl.plane(points={"A(1, 2)": (1, 2), "B(5, 2)": (5, 2),
                                          "C(5, 8)": (5, 8)},
                                  polygon=[(1, 2), (5, 2), (5, 8)],
                                  xr=(-1, 7), yr=(-1, 9), cell=22)),
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if not (a.apply or a.dry_run):
        raise SystemExit("pass --apply or --dry-run")

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    record, failed = [], 0
    for prefix, (why, build) in REPAIRS.items():
        row = con.execute("SELECT * FROM questions WHERE id LIKE ?||'%'",
                          (prefix,)).fetchone()
        if row is None:
            raise SystemExit(f"{prefix} is not in the database")
        q = dict(row)
        before = [n for n, _ in gf.BLOCKING if gf.run_check(n, q)]
        # plane() places every point label outward from the shape's centre, which
        # on a tight plot can put two of them together or one across a drawn line.
        # The nudger already knows how to move a label without touching a tick.
        built, _moved = denude(build())
        q["figure_svg"] = built
        after = [n for n, _ in gf.BLOCKING if gf.run_check(n, q)]
        errs = [e for e in (qc.figure_svg_errors(q["figure_svg"]) or [])
                if "bytes" not in e]
        ok = not after and not errs
        failed += not ok
        print(f"  {prefix}  {why[:56]:<56} {before} -> {after or 'clean'}"
              f"  {'OK' if ok else 'FAILING'}")
        record.append({"id": row["id"], "why": why, "before": before, "after": after})
        if a.apply and ok:
            con.execute("UPDATE questions SET figure_svg=?, edited=1 WHERE id=?",
                        (q["figure_svg"], row["id"]))
    if a.apply:
        con.commit()
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(json.dumps(record, indent=1, ensure_ascii=False))
        print(f"\napplied {len(record) - failed} of {len(record)} — {MANIFEST}")
    else:
        print(f"\ndry run — {len(record)} figure(s), {failed} failing")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
