#!/usr/bin/env python3
"""VIC round 8: the twenty-eight figures that had to be redrawn one at a time.

Round 8's other faults each had a shape a tool could exploit -- an arc derivable from
the figure's own rays, a grid laid out from the wrong corner, LaTeX that decodes. These
twenty-eight do not. Every one is a label printed along the very line it names, and
there is nowhere within reach to nudge it to: the offset ring in
`repair_label_collisions` slides along the same side, and growing the canvas does not
help a "17 cm" lying on a hypotenuse.

They are also the reason none of them could simply be dropped: pulling a question
leaves a hole in a form that is already dealt, and a form short a question re-bases
every score recorded against it.

So each is rebuilt from what the STEM and the stored explanation say, through
`figure_lib` where a generator exists -- `plane`, `pie_chart`, `trapezium` -- and by
hand where none does. Dimensions go OUTSIDE the shape they measure, which is the
convention `right_triangle` was built on and the one the reviewer keeps asking for.
Nothing about a question's numbers, options or key is touched.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_vic_round8_figures
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_vic_round8_figures --apply
"""
import argparse
import json
import math
import pathlib
import re
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import figure_lib as fl                 # noqa: E402
from tools import question_checks as qc            # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
RECORD = ROOT / "run_data/output/vic_round8_figures.json"

FIG_CHECKS = ("doubled_circle_outline", "overlapping_text_labels",
              "plotted_points_inconsistent", "text_overlaps_geometry",
              "axes_unlabelled", "angle_arc_malformed", "axis_scale_nonlinear",
              "coordinate_figure_without_grid", "gridlines_off_the_ticks",
              "unknown_marker_far_from_point", "label_too_faint",
              "undefined_marker_reference", "text_outside_the_canvas",
              "gridlines_stop_short_of_the_axes", "axis_shorter_than_the_data",
              "angle_arc_misses_its_rays", "figure_svg_errors")
Q_CHECKS = ("angle_named_without_arc", "polygon_sides_disagree_with_stem",
            "figure_proportions_disagree", "plotted_geometry_matches_stem")


def _curve(fn, x_lo, x_hi, yr, n=64):
    """A smooth curve, sampled through the figure's own px() and stopped at the edge."""
    def build(px):
        runs, cur = [], []
        for i in range(n + 1):
            x = x_lo + (x_hi - x_lo) * i / n
            y = fn(x)
            if yr[0] <= y <= yr[1]:
                cur.append(px(x, y))
            elif cur:
                runs.append(cur)
                cur = []
        if cur:
            runs.append(cur)
        d = "".join("M" + "L".join(f"{a:.0f} {b:.0f}" for a, b in r)
                    for r in runs if len(r) > 1)
        return (f'<path d="{d}" fill="none" stroke="currentColor" '
                f'stroke-width="2" stroke-opacity=".9"/>')
    return build


def _right_angle_at(corner, a, b, size=0.45):
    """A right-angle square at `corner`, opening toward `a` and `b` (plane units)."""
    def build(px):
        def unit(p):
            dx, dy = p[0] - corner[0], p[1] - corner[1]
            n = max(math.hypot(dx, dy), 1e-9)
            return (corner[0] + dx / n * size, corner[1] + dy / n * size)
        p0, p2 = px(*unit(a)), px(*unit(b))
        c = px(*corner)
        p1 = (p0[0] + p2[0] - c[0], p0[1] + p2[1] - c[1])
        pts = " ".join(f"{x:.0f},{y:.0f}" for x, y in (p0, p1, p2))
        return (f'<polyline points="{pts}" fill="none" stroke="currentColor" '
                f'stroke-width="1.3"/>')
    return build


# --------------------------------------------------------------- coordinate planes
def f_54585091():
    """Triangle PQR reflected in the y-axis; the question asks only for Q'.

    The stored triangle was drawn at (−1.5, 0.5), (−1.5, −1) and (−0.5, −1) -- not one
    of them a lattice point, and none of them the Q(−3, 1) the explanation names. P and
    R are free (nothing asks about them), so they take the shape the old figure drew,
    right-angled at Q with P above and R to the right, on whole units.
    """
    return fl.plane(points={"P": (-3, 3), "Q": (-3, 1), "R": (-1, 1)},
                    polygon=[(-3, 3), (-3, 1), (-1, 1)],
                    xr=(-5, 5), yr=(-3, 5), cell=24)


def f_4f3a0df2():
    return fl.plane(lines=[((1, 1), (3, 5))],
                    points={"P(1, 1)": (1, 1), "Q(3, 5)": (3, 5)},
                    xr=(-2, 5), yr=(-2, 6), cell=26)


def f_c004fdff():
    return fl.plane(polygon=[(1, 5), (1, 1), (7, 1)],
                    points={"A(1, 5)": (1, 5), "B(1, 1)": (1, 1), "C(7, 1)": (7, 1)},
                    xr=(-1, 8), yr=(-1, 7), cell=24,
                    extra=_right_angle_at((1, 1), (7, 1), (1, 5)))


def f_a34c0db1():
    # A and B stay UNLABELLED by coordinate, as the stored figure had them: the
    # question is "what is the midpoint of AB", and reading the two points off the grid
    # is the skill. Printing "A(−1, 1)" would hand half the work over, and it is also
    # a nine-character label on a point one unit from the axis, which has nowhere to sit.
    return fl.plane(segments=[((-1, 1), (3, 5))],
                    points={"A": (-1, 1), "B": (3, 5)},
                    xr=(-3, 5), yr=(-2, 6), cell=26)


def f_a318b00f():
    # Bare A and B, as the stored figure had them -- the question asks for the midpoint
    # and reading the points off the grid is the skill.
    return fl.plane(lines=[((-1, -1), (3, 5))],
                    points={"A": (-1, -1), "B": (3, 5)},
                    xr=(-4, 5), yr=(-3, 6), cell=24)


def f_e6839d84():
    """A parabola whose vertex the student must READ OFF the grid.

    "Why is 1, 5 on the coordinate plane, it gives out the answer." The old figure
    printed "(1, 5)" beside the vertex, which is the answer to the question. The dot
    stays and the label goes: y = 5 − (x − 1)² is the curve the old one drew.
    """
    return fl.plane(points=[(1, 5)],
                    xr=(-3, 5), yr=(-4, 6), cell=24,
                    extra=_curve(lambda x: 5 - (x - 1) ** 2, -3, 5, (-4, 6)))


def f_fa7b38b8():
    return fl.plane(polygon=[(1, 4), (4, 4), (4, 1)],
                    points={"A(1, 4)": (1, 4), "B(4, 4)": (4, 4), "C(4, 1)": (4, 1)},
                    xr=(-5, 6), yr=(-5, 6), cell=22)


def f_092c6056():
    return fl.plane(lines=[((0, 1), (4, 3))], points=[(0, 1), (4, 3)],
                    xr=(-4, 6), yr=(-3, 5), cell=24)


# ----------------------------------------------------------------------- pie charts
# `figure_lib.pie_chart` takes (label, count) pairs and derives the angles from the
# counts, so a sector labelled 25% is 25%. All five of these had labels printed across
# the spokes; `lab_gap` is the distance from the rim to the label ring, and it is set
# per chart to whatever the longest label on that chart needs.
def f_d1d46997():
    """120 meat pies, 80 sausage rolls, 40 sandwiches. The question asks for the MEAT
    PIES ANGLE, so no angle is printed on the chart -- the counts are, because the stem
    gives them anyway."""
    return fl.pie_chart([("Meat Pies (120)", 120), ("Sausage Rolls (80)", 80),
                         ("Sandwiches (40)", 40)], lab_gap=48)


def f_733b125d():
    return fl.pie_chart([("Food 25%", 25), ("Rent 37.5%", 37.5),
                         ("Other 37.5%", 37.5)], lab_gap=40)


def f_d1b8a9e0():
    return fl.pie_chart([("Food 90°", 90), ("Transport 90°", 90),
                         ("Games 90°", 90), ("Savings 90°", 90)], lab_gap=32)


def f_77831293():
    return fl.pie_chart([("Rent 1/4", 1), ("Transport 1/4", 1),
                         ("Food 1/4", 1), ("Savings 1/4", 1)], lab_gap=32)


def f_dfc0c664():
    """200 students: Car 30%, Bus 15%, Walk 40%, Train 15%.

    The stored figure carried TWO legends stacked on each other and a duplicate `x`
    attribute that made it the only figure in the bank cairosvg would not render at
    all. Its four sectors were drawn at 60°, 30°, 180° and 90° against a legend saying
    30%, 15%, 40% and 15% -- every slice the wrong size, on a question that asks for a
    probability read off the chart."""
    return fl.pie_chart([("Car (30%)", 60), ("Bus (15%)", 30),
                         ("Walk (40%)", 80), ("Train (15%)", 30)], lab_gap=32)


# ------------------------------------------------------------- charts and shapes
def _lab(x, y, t, size=12, anchor="middle"):
    return (f'<text x="{x:.0f}" y="{y:.0f}" font-size="{size}" '
            f'text-anchor="{anchor}" fill="currentColor">{t}</text>')


def _arc(v, p, q, r, label=""):
    """An angle mark at v between the rays to p and q, taking the SMALLER sector.

    `figure_lib.angle_mark` sweeps a1 to a2 clockwise on screen, so handing it the two
    rays in the wrong order marks the 290° reflex angle instead of the 70° one -- which
    is what `angle_arc_malformed` caught on the first cut of the isosceles triangle.
    """
    a1 = math.atan2(p[1] - v[1], p[0] - v[0])
    a2 = math.atan2(q[1] - v[1], q[0] - v[0])
    if (a2 - a1) % (2 * math.pi) > math.pi:
        a1, a2 = a2, a1
    return fl.angle_mark(v, a1, a2, r, label=label) or ""


def _titled(svg_text, x_title, y_title):
    """Put axis titles on a `figure_lib` chart and grow the canvas to hold them.

    `line_graph` labels the ticks but names neither axis, so `axes_unlabelled` rejects
    it -- correctly: "the graph shows the volume of water in litres over time in hours"
    is in the stem, and a chart that does not repeat it makes the reader hold it.
    """
    m = re.search(r'viewBox="([^"]+)"', svg_text)
    x0, y0, w, h = (float(v) for v in m.group(1).split())
    # The titles go in the strip the canvas grows by, not over the tick numbers that
    # are already there -- the first cut put "Time (hours)" through the "2" beneath it.
    extra = (_lab(x0 + w / 2, y0 + h + 17, x_title, 11)
             + f'<text x="{x0 - 12:.0f}" y="{y0 + h / 2:.0f}" font-size="11" '
               f'text-anchor="middle" fill="currentColor" '
               f'transform="rotate(-90 {x0 - 12:.0f} {y0 + h / 2:.0f})">'
               f'{y_title}</text>')
    out = svg_text.replace("</svg>", extra + "</svg>", 1)
    out = out.replace(m.group(0),
                      f'viewBox="{x0 - 26:g} {y0:g} {w + 26:g} {h + 24:g}"', 1)
    return out


def f_2ed01a33():
    """Trapezium, parallel sides 8 and 14, slant sides 5, height unknown.

    `figure_lib.trapezium` draws it to its stated sides and stands the height label
    beside the dashed line rather than on it -- which is the whole complaint ("5
    overlaps with the sides. The right angle is elevated"). The 5 m slant sides are
    not printed: the stem states them, and a trapezium this narrow has no room
    outside its slants for a label that is not touching one.
    """
    return fl.trapezium(8, 14, 4, top_label="8 m", bottom_label="14 m",
                        height_label="h")


def f_c06a29a8():
    """Distance from home over a 5-hour ride: 0, 10, 20, 50, 55, 60 km.

    Those are the values the stored polyline plots, and the explanation names the
    steepest leg as hour 2 to hour 3, 20 km to 50 km. `figure_lib.line_graph` puts the
    axis titles outside the plot, which the hand-drawn one did not.
    """
    return _titled(fl.line_graph(["0", "1", "2", "3", "4", "5"],
                                 [0, 10, 20, 50, 55, 60]),
                   "Time (hours)", "Distance (km)")


def f_0b46725b():
    """Water draining: 200 L at t=0 falling to 0 L at t=4.

    The stored figure drew TWO lines crossing in an X -- one falling and one rising --
    on a question about a tank draining. Only the falling one belongs.
    """
    return _titled(fl.line_graph(["0", "1", "2", "3", "4"], [200, 150, 100, 50, 0]),
                   "Time (hours)", "Volume (L)")


def f_ec0ff31c():
    """Rectangle (3x + 4) by (x − 2), both dimensions written OUTSIDE it."""
    x0, y0, w, h = 70, 46, 200, 96
    b = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="currentColor" '
         f'fill-opacity=".10" stroke="currentColor" stroke-width="2"/>',
         _lab(x0 + w / 2, y0 - 12, "(3x + 4) m"),
         _lab(x0 - 12, y0 + h / 2 + 4, "(x − 2) m", anchor="end")]
    return fl.svg("".join(b), vb="0 0 300 190")


def f_d3c74fcc():
    """An L-shape: a 10 by 8 rectangle with a 4 by 6 corner cut out.

    Every dimension is on its own leader line OUTSIDE the outline, and the cut-out is
    dashed so it is visibly the piece removed rather than a second shape.
    """
    sx, sy, u = 60, 40, 18                     # 18 px per cm
    W, H, cw, ch = 10 * u, 8 * u, 4 * u, 6 * u
    pts = [(sx, sy), (sx + W, sy), (sx + W, sy + H), (sx + W - cw, sy + H),
           (sx + W - cw, sy + H - ch), (sx, sy + H - ch)]
    poly = " ".join(f"{a},{c}" for a, c in pts)
    b = [f'<polygon points="{poly}" fill="currentColor" fill-opacity=".18" '
         f'stroke="currentColor" stroke-width="2"/>',
         f'<rect x="{sx + W - cw}" y="{sy + H - ch}" width="{cw}" height="{ch}" '
         f'fill="none" stroke="currentColor" stroke-width="1.4" '
         f'stroke-dasharray="5,3" stroke-opacity=".7"/>',
         # dimensions, each on its own leader outside the shape
         f'<line x1="{sx}" y1="{sy - 14}" x2="{sx + W}" y2="{sy - 14}" '
         f'stroke="currentColor" stroke-width="1"/>',
         _lab(sx + W / 2, sy - 20, "10 cm"),
         f'<line x1="{sx + W + 14}" y1="{sy}" x2="{sx + W + 14}" y2="{sy + H}" '
         f'stroke="currentColor" stroke-width="1"/>',
         _lab(sx + W + 22, sy + H / 2 + 4, "8 cm", anchor="start"),
         f'<line x1="{sx + W - cw}" y1="{sy + H + 14}" x2="{sx + W}" '
         f'y2="{sy + H + 14}" stroke="currentColor" stroke-width="1"/>',
         _lab(sx + W - cw / 2, sy + H + 28, "4 cm"),
         f'<line x1="{sx + W - cw - 14}" y1="{sy + H - ch}" x2="{sx + W - cw - 14}" '
         f'y2="{sy + H}" stroke="currentColor" stroke-width="1"/>',
         _lab(sx + W - cw - 20, sy + H - ch / 2 + 4, "6 cm", anchor="end")]
    return fl.svg("".join(b), vb="0 0 320 230")


def f_31a7147e():
    """A 6 cm square with a 2 cm square in each corner, both dimensions outside."""
    sx, sy, u = 80, 34, 26
    S, s2 = 6 * u, 2 * u
    b = [f'<rect x="{sx}" y="{sy}" width="{S}" height="{S}" fill="none" '
         f'stroke="currentColor" stroke-width="2"/>']
    for cx, cy in ((sx, sy), (sx + S - s2, sy), (sx, sy + S - s2),
                   (sx + S - s2, sy + S - s2)):
        b.append(f'<rect x="{cx}" y="{cy}" width="{s2}" height="{s2}" '
                 f'fill="currentColor" fill-opacity=".45" stroke="currentColor" '
                 f'stroke-width="1.4"/>')
    b += [f'<line x1="{sx}" y1="{sy + S + 16}" x2="{sx + S}" y2="{sy + S + 16}" '
          f'stroke="currentColor" stroke-width="1"/>',
          _lab(sx + S / 2, sy + S + 32, "6 cm"),
          f'<line x1="{sx - 16}" y1="{sy}" x2="{sx - 16}" y2="{sy + s2}" '
          f'stroke="currentColor" stroke-width="1"/>',
          _lab(sx - 22, sy + s2 / 2 + 4, "2 cm", anchor="end")]
    return fl.svg("".join(b), vb="0 0 300 230")


def f_69918047():
    """Isosceles triangle PQR: apex (x + 20)°, both base angles (2x)°.

    The base angles were printed ON the base. They sit above it now, inside the
    triangle and clear of both the base and the slant, and the equal-side ticks stay.
    """
    ax, ay, bx, by, cx2 = 172, 44, 92, 158, 252
    b = [f'<polygon points="{ax},{ay} {bx},{by} {cx2},{by}" fill="none" '
         f'stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>']
    for (px_, py_, qx, qy) in ((ax, ay, bx, by), (ax, ay, cx2, by)):
        mx, my = (px_ + qx) / 2, (py_ + qy) / 2
        dx, dy = qx - px_, qy - py_
        n = math.hypot(dx, dy)
        b.append(f'<line x1="{mx - dy / n * 5:.1f}" y1="{my + dx / n * 5:.1f}" '
                 f'x2="{mx + dy / n * 5:.1f}" y2="{my - dx / n * 5:.1f}" '
                 f'stroke="currentColor" stroke-width="1.6"/>')
    b += [_arc((ax, ay), (bx, by), (cx2, by), 30, "(x+20)°"),
          _arc((bx, by), (cx2, by), (ax, ay), 26, "(2x)°"),
          _arc((cx2, by), (ax, ay), (bx, by), 26, "(2x)°"),
          _lab(ax, ay - 12, "P"), _lab(bx - 14, by + 6, "Q"),
          _lab(cx2 + 14, by + 6, "R"),
          _lab(ax, ay + 62, "(x+20)°"), _lab(bx + 46, by - 12, "(2x)°"),
          _lab(cx2 - 46, by - 12, "(2x)°")]
    return fl.svg("".join(b), vb="0 0 344 200")


def f_46c3108f():
    """Two congruent right triangles, 8 and 15 with a 17 hypotenuse, side by side.

    Every dimension is outside its own triangle -- the stored one wrote "17 cm" along
    the hypotenuse it names.
    """
    def one(ox, base_label):
        bx, by = ox, 158
        b = [f'<polygon points="{bx},{by} {bx + 105},{by} {bx},{by - 56}" '
             f'fill="none" stroke="currentColor" stroke-width="2" '
             f'stroke-linejoin="round"/>',
             f'<polyline points="{bx + 10},{by} {bx + 10},{by - 10} {bx},{by - 10}" '
             f'fill="none" stroke="currentColor" stroke-width="1.2"/>',
             _lab(bx + 52, by + 20, base_label),
             _lab(bx - 8, by - 24, "8 cm", anchor="end"),
             _lab(bx + 76, by - 44, "17 cm")]
        return "".join(b)
    return fl.svg(one(48, "15 cm") + one(212, "x"), vb="0 0 344 200")


def f_7fec9689():
    """Circle centre O, chord AB = 24, OC perpendicular to AB, radius 13.

    "OC overlaps with right angle symbol." The right-angle square now sits on the far
    side of OC from its label, and every length is written clear of the line it
    measures.
    """
    cx, cy, r = 150, 96, 78
    half = r * 24 / 26.0 / 2 * 2 / 2            # 12/13 of r, halved: AC on screen
    ax_, bx_ = cx - r * 12 / 13, cx + r * 12 / 13
    cy_ = cy + r * 5 / 13
    b = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="currentColor" '
         f'stroke-width="1.8"/>',
         f'<line x1="{ax_:.1f}" y1="{cy_:.1f}" x2="{bx_:.1f}" y2="{cy_:.1f}" '
         f'stroke="currentColor" stroke-width="1.8"/>',
         f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy_:.1f}" '
         f'stroke="currentColor" stroke-width="1.5"/>',
         f'<line x1="{cx}" y1="{cy}" x2="{ax_:.1f}" y2="{cy_:.1f}" '
         f'stroke="currentColor" stroke-width="1.2" stroke-dasharray="4,3"/>',
         f'<polyline points="{cx - 11},{cy_:.1f} {cx - 11},{cy_ - 11:.1f} '
         f'{cx},{cy_ - 11:.1f}" fill="none" stroke="currentColor" '
         f'stroke-width="1.2"/>',
         f'<circle cx="{cx}" cy="{cy}" r="3.5" fill="currentColor"/>',
         _lab(cx + 10, cy - 4, "O", anchor="start"),
         _lab(ax_ - 10, cy_ + 4, "A", anchor="end"),
         _lab(bx_ + 10, cy_ + 4, "B", anchor="start"),
         _lab(cx + 8, cy_ + 16, "C", anchor="start"),
         _lab(cx - 46, cy + 4, "13 cm", anchor="middle"),
         _lab(cx, cy + r + 30, "AB = 24 cm")]
    return fl.svg("".join(b), vb="0 0 300 220")


def f_43ff3bdd():
    """Circle centre O with the inscribed angle BAC standing on the same arc as the
    50° angle BOC. A is put well round the circle from B and C so its label has room,
    and both angles carry an arc derived from the rays that bound them."""
    cx, cy, r = 160, 112, 84
    def at(deg):
        a = math.radians(deg)
        return (cx + r * math.cos(a), cy - r * math.sin(a))
    B, C, A = at(115), at(65), at(255)
    b = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="currentColor" '
         f'stroke-width="1.8"/>']
    for p_ in (B, C):
        b.append(f'<line x1="{cx}" y1="{cy}" x2="{p_[0]:.1f}" y2="{p_[1]:.1f}" '
                 f'stroke="currentColor" stroke-width="1.5"/>')
        b.append(f'<line x1="{A[0]:.1f}" y1="{A[1]:.1f}" x2="{p_[0]:.1f}" '
                 f'y2="{p_[1]:.1f}" stroke="currentColor" stroke-width="1.5"/>')
    b += [_arc((cx, cy), B, C, 30, "50°"),
          f'<circle cx="{cx}" cy="{cy}" r="3.2" fill="currentColor"/>',
          _lab(cx - 12, cy + 5, "O", anchor="end"),
          _lab(B[0] - 6, B[1] - 8, "B", anchor="end"),
          _lab(C[0] + 6, C[1] - 8, "C", anchor="start"),
          _lab(A[0], A[1] + 18, "A"),
          _lab(cx, cy - 40, "50°")]
    return fl.svg("".join(b), vb="0 0 320 240")


def f_5e46281e():
    """Two roads crossing at B, with the four angles numbered clear of both lines."""
    b = ['<line x1="40" y1="156" x2="248" y2="44" stroke="currentColor" '
         'stroke-width="2"/>',
         '<line x1="40" y1="44" x2="248" y2="156" stroke="currentColor" '
         'stroke-width="2"/>',
         '<circle cx="144" cy="100" r="3.4" fill="currentColor"/>',
         _lab(144, 88, "B"),
         _lab(196, 104, "∠1", anchor="start"),
         _lab(144, 142, "∠2"),
         _lab(92, 104, "∠3", anchor="end"),
         _lab(144, 64, "∠4")]
    return fl.svg("".join(b), vb="0 0 288 190")


def f_e89214af():
    """A 4 by 8 by 6 box, each edge measured on a leader line outside the drawing."""
    x0, y0, w, h, d = 62, 92, 132, 78, 40
    b = [f'<polygon points="{x0},{y0} {x0 + w},{y0} {x0 + w},{y0 + h} {x0},{y0 + h}" '
         f'fill="currentColor" fill-opacity=".14" stroke="currentColor" '
         f'stroke-width="1.8"/>',
         f'<polygon points="{x0},{y0} {x0 + d},{y0 - d} {x0 + w + d},{y0 - d} '
         f'{x0 + w},{y0}" fill="currentColor" fill-opacity=".08" '
         f'stroke="currentColor" stroke-width="1.8"/>',
         f'<polygon points="{x0 + w},{y0} {x0 + w + d},{y0 - d} '
         f'{x0 + w + d},{y0 + h - d} {x0 + w},{y0 + h}" fill="currentColor" '
         f'fill-opacity=".20" stroke="currentColor" stroke-width="1.8"/>',
         f'<path d="M{x0},{y0 + h}l{d},{-d}h{w}M{x0 + d},{y0 + h - d}v{-h}" '
         f'fill="none" stroke="currentColor" stroke-width="1.2" '
         f'stroke-dasharray="4,3" stroke-opacity=".7"/>',
         f'<line x1="{x0}" y1="{y0 + h + 16}" x2="{x0 + w}" y2="{y0 + h + 16}" '
         f'stroke="currentColor" stroke-width="1"/>',
         _lab(x0 + w / 2, y0 + h + 32, "8 cm"),
         f'<line x1="{x0 - 16}" y1="{y0}" x2="{x0 - 16}" y2="{y0 + h}" '
         f'stroke="currentColor" stroke-width="1"/>',
         _lab(x0 - 22, y0 + h / 2 + 4, "6 cm", anchor="end"),
         f'<line x1="{x0 + w + d + 12}" y1="{y0 - d}" x2="{x0 + w + d + 12}" '
         f'y2="{y0}" stroke="currentColor" stroke-width="1"/>',
         _lab(x0 + w + d + 20, y0 - d / 2 + 4, "4 cm", anchor="start")]
    return fl.svg("".join(b), vb="0 0 320 210")


# ------------------------------------------------------------------------- dials
def _dial(cx, cy, r, ticks, pointer=None, start=-90, span=340, size=10):
    """A round scale: rim, tick marks, numbers OUTSIDE the rim, and a pointer.

    All three dial figures in this round printed their numbers ON the rim or on the
    tick they name. A dial's numbers belong outside its rim -- that is the only place
    on a dial where nothing else is drawn.
    """
    b = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="currentColor" '
         f'stroke-width="2"/>',
         f'<circle cx="{cx}" cy="{cy}" r="3.2" fill="currentColor"/>']
    n = len(ticks) - 1
    # All the tick marks in ONE path. Twenty <line> elements pushed a two-dial figure
    # past the 3.5 KB the size rule allows, and the rule's own advice is exactly this.
    marks = []
    for i, t in enumerate(ticks):
        a = math.radians(start + span * i / n)
        ca, sa = math.cos(a), math.sin(a)
        marks.append(f"M{cx + (r - 7) * ca:.0f} {cy + (r - 7) * sa:.0f}"
                     f"L{cx + r * ca:.0f} {cy + r * sa:.0f}")
        if t is None:
            continue
        lx, ly = cx + (r + 14) * ca, cy + (r + 14) * sa
        b.append(_lab(lx, ly + 4, t, size))
    b.append(f'<path d="{"".join(marks)}" fill="none" stroke="currentColor" '
             f'stroke-width="1.4"/>')
    if pointer is not None:
        a = math.radians(start + span * pointer)
        b.append(f'<line x1="{cx}" y1="{cy}" x2="{cx + (r - 16) * math.cos(a):.1f}" '
                 f'y2="{cy + (r - 16) * math.sin(a):.1f}" stroke="currentColor" '
                 f'stroke-width="2.4"/>')
    return "".join(b)


def f_7f3d6cef():
    """Two identical dials: A reads 22 kg with no zero error, B reads 26 kg.

    Numbers outside the rim, pointer inside, and the caption under each dial rather
    than across it.
    """
    ticks = ["0", "10", "20", "30", "40", "50", "60", "70", "80", "90"]
    b = [_dial(88, 96, 56, ticks, pointer=22 / 90),
         _dial(250, 96, 56, ticks, pointer=26 / 90),
         _lab(88, 186, "Scale A: 22 kg", 12), _lab(88, 202, "(no zero error)", 11),
         _lab(250, 186, "Scale B: 26 kg", 12), _lab(250, 202, "(faulty)", 11)]
    return fl.svg("".join(b), vb="0 0 340 216")


def f_6a63e0a1():
    """A kitchen scale reading 680 g, numbered 0 to 1000 in hundreds."""
    # 320° rather than the default 340: at 340 the "0" and the "1000" close up on each
    # other at twelve o'clock, and the unit sat on top of the "500" at the bottom.
    ticks = [str(v) for v in range(0, 1001, 100)]
    b = [_dial(150, 106, 70, ticks, pointer=680 / 1000, span=320, size=10),
         _lab(150, 226, "grams", 12)]
    return fl.svg("".join(b), vb="0 0 300 240")


def f_0a0dbc30():
    """A six-section spinner. The numbers sit on each sector's own bisector, well
    inside the wedge, so none of them lies along a spoke."""
    cx, cy, r = 140, 112, 84
    b = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="currentColor" '
         f'stroke-width="2.4"/>']
    for i in range(6):
        a = math.radians(-90 + 60 * i)
        b.append(f'<line x1="{cx}" y1="{cy}" x2="{cx + r * math.cos(a):.1f}" '
                 f'y2="{cy + r * math.sin(a):.1f}" stroke="currentColor" '
                 f'stroke-width="1.8"/>')
    for i in range(6):
        a = math.radians(-90 + 60 * i + 30)
        b.append(_lab(cx + r * 0.62 * math.cos(a), cy + r * 0.62 * math.sin(a) + 5,
                      str(i + 1), 15))
    b.append(f'<circle cx="{cx}" cy="{cy}" r="3.4" fill="currentColor"/>')
    return fl.svg("".join(b), vb="0 0 280 220")


BUILDERS = {
    "54585091": f_54585091, "4f3a0df2": f_4f3a0df2, "c004fdff": f_c004fdff,
    "a34c0db1": f_a34c0db1, "a318b00f": f_a318b00f, "e6839d84": f_e6839d84,
    "fa7b38b8": f_fa7b38b8, "092c6056": f_092c6056,
    "d1d46997": f_d1d46997, "733b125d": f_733b125d, "d1b8a9e0": f_d1b8a9e0,
    "77831293": f_77831293, "dfc0c664": f_dfc0c664,
    "2ed01a33": f_2ed01a33, "c06a29a8": f_c06a29a8, "0b46725b": f_0b46725b,
    "ec0ff31c": f_ec0ff31c, "d3c74fcc": f_d3c74fcc, "31a7147e": f_31a7147e,
    "69918047": f_69918047, "46c3108f": f_46c3108f, "7fec9689": f_7fec9689,
    "43ff3bdd": f_43ff3bdd, "5e46281e": f_5e46281e, "e89214af": f_e89214af,
    "7f3d6cef": f_7f3d6cef, "6a63e0a1": f_6a63e0a1, "0a0dbc30": f_0a0dbc30,
}


def state(q, svg):
    row = dict(q)
    row["figure_svg"] = svg
    return ({n for n in FIG_CHECKS if getattr(qc, n)(svg)}
            | {n for n in Q_CHECKS if getattr(qc, n)(row)})


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dump", type=pathlib.Path)
    args = ap.parse_args()
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    done, refused, dump = [], [], []
    for prefix, build in BUILDERS.items():
        row = con.execute("SELECT * FROM questions WHERE id LIKE ?",
                          (prefix + "%",)).fetchone()
        if row is None:
            refused.append({"id": prefix, "why": "no such question"})
            continue
        q = dict(row)
        before = state(q, q["figure_svg"])
        new = build()
        after = state(q, new)
        gained = after - before
        if gained:
            refused.append({"id": q["id"], "newly_firing": sorted(gained)})
            continue
        done.append({"id": q["id"], "form": q["form_id"],
                     "cleared": sorted(before - after), "left": sorted(after)})
        dump.append({"id": prefix + "-BEFORE", "figure_svg": q["figure_svg"],
                     "stem": q["stem"]})
        dump.append({"id": prefix + "-AFTER", "figure_svg": new, "stem": q["stem"]})
        if args.apply:
            con.execute("UPDATE questions SET figure_svg = ?, edited = 1 WHERE id = ?",
                        (new, q["id"]))
    if args.apply:
        con.commit()
    if args.dump:
        args.dump.write_text(json.dumps(dump))
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps({"applied": args.apply, "redrawn": done,
                                  "refused": refused}, indent=1))
    print(f"{len(done)} redrawn, {len(refused)} refused"
          f"{'' if args.apply else '  (dry run — pass --apply)'}")
    for r in refused:
        print("   refused", r["id"][:8], r.get("newly_firing") or r["why"])
    for d in done:
        if d["left"]:
            print("   still flagged", d["id"][:8], d["left"])
    print(f"record -> {RECORD}")


if __name__ == "__main__":
    main()
