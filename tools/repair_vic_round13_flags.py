#!/usr/bin/env python3
"""VIC round 13: the 35 VIC questions in the reviewer's 2026-10-11 Selectly flag export.

`review/ui/flagged-questions-2026-10-11.csv` holds 55 flags from two reviewers: 35 on
`vic-drill-mq-019` to `-034` and 20 on NSW forms. This script does the 35 VIC ones only;
the NSW ones are a separate round. Every one of the 35 is approved and live, so nothing
here reaches a student until it is pushed.

WHAT THE 35 ARE.
  Wrong key, explanation right       4  d39176ed 5e0f6626 0605319e 87888e6f
  Right answer missing from options  3  167b73cc 3d5a5b9b 7d981502
  Two options both correct           3  6a120a5b 6bad5c4a 80da65db
  Needs a calculator                 5  9d857ccb ee877596 6f7e4a25 630d2093 0d1ba57f
  'root' / '^' / '/' / vinculum      8  a284e88b 669ff03e 5d6922c4 5392c10c 3b1c760d
                                        a682cfea 9ad41d04 d4096e9a
  Figure wrong or untidy             8  09506111 4d8c6127 48fb8741 5366b95c 05650106
                                        66d38eef 0b23f6f2 5f486830
  Method question, not maths         2  d4966c1e dd93aedb
  Confusing / no diagram             2  b7693921 aeca13ea

Every re-cut keeps its answer letter. The four wrong keys move to the option the
explanation (and the reviewer) already pointed at.

Every question's full check state is compared before and after, and a repair that would
make any check newly fire is refused rather than written.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_vic_round13_flags
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_vic_round13_flags --apply
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.repair_vic_round12_flags import FIELDS, findings      # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
CSV = ROOT / "review/ui/flagged-questions-2026-10-11.csv"
RECORD = ROOT / "run_data/output/vic_round13_flags.json"

SVG_OPEN = ('<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            'xmlns="http://www.w3.org/2000/svg">')


def t(x, y, s, size=13, anchor="middle", bold=False):
    b = ' font-weight="bold"' if bold else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Arial,sans-serif" '
            f'font-size="{size}" text-anchor="{anchor}" fill="currentColor"{b}>{s}</text>')


def path(d, w=2, fill="none", op=None, fop=None, dash=None):
    o = f' stroke-opacity="{op}"' if op else ""
    f = f' fill-opacity="{fop}"' if fop else ""
    a = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="{d}" fill="{fill}" stroke="currentColor" '
            f'stroke-width="{w}"{o}{f}{a}/>')


# ====================================================================== figures
def f_09506111(q):
    """'The answer (15/24) is over half the pie chart, but the rent category is clearly
    less than half.'

    The key was never 15/24 -- it is B, 9 out of 24, in qbank AND in production (read
    back from Selectly's dump), and the Rent slice is drawn at exactly 135 degrees, which
    is 9/24. So the picture and the key agree. What was wrong is that the stem says the
    chart is 'divided into 24 equal parts' and the picture never showed them: a student
    had to judge 135 degrees by eye, and 9/24 against 15/24 is easy to misread that way.
    The 24 parts are now drawn as faint radii every 15 degrees, so Rent's 9 can be
    counted."""
    svg = q["figure_svg"]
    cx, cy, r = 170.0, 101.0, 62.0
    d = "".join(f"M{cx:g} {cy:g}L{cx + r * math.sin(math.radians(15 * k)):.1f} "
                f"{cy - r * math.cos(math.radians(15 * k)):.1f}" for k in range(24))
    spokes = path(d, w=0.8, op=".45")
    i = svg.index('<text x="109"')                    # after the last sector, before its label
    return {"figure_svg": svg[:i] + spokes + svg[i:]}


def f_167b73cc(q):
    """'The answer is 180 ... 180 is not an option.' Right: 240 - 60 = 180 and the key
    was 160. Option B (the key letter) becomes 180.

    The figure also printed 10 and 6 on the inner rectangle, which does the 'similar,
    perimeter 32' half of the question for the student, and was not to scale (20 by 12
    drawn 240 by 120). Redrawn at 12 px per cm with the inner sides left unlabelled."""
    o = (55, 30, 240, 144)
    i = (115, 66, 120, 72)
    svg = (SVG_OPEN.format(w=320, h=200)
           + f'<rect x="{o[0]}" y="{o[1]}" width="{o[2]}" height="{o[3]}" '
             f'fill="currentColor" fill-opacity=".18" stroke="currentColor" stroke-width="2"/>'
           + f'<rect x="{i[0]}" y="{i[1]}" width="{i[2]}" height="{i[3]}" '
             f'fill="#fff" stroke="currentColor" stroke-width="2"/>'
           + t(175, 22, "20 cm") + t(47, 106, "12 cm", anchor="end")
           + "</svg>")
    return {"option_b": "180", "figure_svg": svg,
            "explanation": "The outer rectangle is 20 × 12 = 240 cm². The inner one is "
                           "similar, so its sides are in the same ratio 20 : 12 = 5 : 3. "
                           "Its perimeter is 32, so length + width = 16, which splits 5 : 3 "
                           "into 10 and 6. Its area is 10 × 6 = 60 cm², and the border is "
                           "240 − 60 = 180 cm². 160 and 140 come from guessing the inner "
                           "rectangle's sides rather than using the ratio, and 120 is half "
                           "the outer area."}


def f_4d8c6127(q):
    """'15 cm slightly overlaps with the line.' The label sat on its own dimension rule.
    It now sits below the rule. The figure was also not to scale (6 cm drawn 120 px
    against 15 cm at 240), so it is redrawn at 16 px per cm throughout."""
    s = 16
    x0, y0 = 40, 40
    W, H, nw, nh = 15 * s, 6 * s, 5 * s, 2 * s
    nx = x0 + (W - nw) / 2
    shape = (f"M{x0} {y0}H{nx:g}V{y0 + nh}H{nx + nw:g}V{y0}H{x0 + W}V{y0 + H}H{x0}Z")
    yr = y0 + H + 12
    svg = (SVG_OPEN.format(w=320, h=180)
           + path(f"M{nx:g} {y0}H{nx + nw:g}", w=1, dash="4,3")
           + path(shape, fill="currentColor", fop=".18")
           + path(f"M{x0} {yr}H{x0 + W}M{x0} {yr - 5}V{yr + 5}M{x0 + W} {yr - 5}V{yr + 5}",
                  w=1)
           + t(x0 + W / 2, yr + 18, "15 cm")
           + t(x0 - 8, y0 + H / 2 + 4, "6 cm", anchor="end")
           + t(nx + nw / 2, y0 - 8, "5 cm")
           + t(nx + nw + 8, y0 + nh / 2 + 5, "2 cm", anchor="start")
           + "</svg>")
    return {"figure_svg": svg}


def f_48fb8741(q):
    """'Revise rectangle figure to look more to scale (the 12 cm² rectangle is meant to
    be 2x6, but it looks like a square).'

    It was drawn 88 by 87 -- a square. The three areas fix only the RATIOS of the sides
    (left : right = 2 : 3, top : bottom = 6 : 5), so 2 by 6 is one valid choice and 4 by
    3 is another. 4 by 3 is used because a 2-wide cell is too narrow to hold its own
    label. Every cell is now drawn at one scale, 24 px per cm: 12 = 4 x 3, 18 = 6 x 3,
    10 = 4 x 2.5 and the shaded 15 = 6 x 2.5.

    The explanation worked a different question (10, 15 and 6, answer 9) that is not the
    figure's; it is rewritten for 12, 18 and 10. The key, 15, was already right."""
    s = 24
    x0, y0 = 30, 20
    a, b, p, r = 4 * s, 6 * s, 3 * s, 2.5 * s
    svg = (SVG_OPEN.format(w=300, h=170)
           + f'<rect x="{x0 + a}" y="{y0 + p}" width="{b}" height="{r:g}" '
             f'fill="currentColor" fill-opacity=".22"/>'
           + path(f"M{x0} {y0}H{x0 + a + b}V{y0 + p + r:g}H{x0}Z"
                  f"M{x0 + a} {y0}V{y0 + p + r:g}M{x0} {y0 + p}H{x0 + a + b}")
           + t(x0 + a / 2, y0 + p / 2 + 5, "12 cm²", 14)
           + t(x0 + a + b / 2, y0 + p / 2 + 5, "18 cm²", 14)
           + t(x0 + a / 2, y0 + p + r / 2 + 5, "10 cm²", 14)
           + t(x0 + a + b / 2, y0 + p + r / 2 + 5, "?", 15, bold=True)
           + "</svg>")
    return {"figure_svg": svg,
            "explanation": "The two top rectangles have the same height, so their widths "
                           "are in the ratio of their areas, 12 : 18 = 2 : 3. The shaded "
                           "rectangle sits under the right-hand one, so it is 3/2 times as "
                           "wide as the 10 cm² rectangle beside it and has the same height. "
                           "Its area is 10 × 3/2 = 15 cm². Check: 12 × 15 = 18 × 10 = 180, "
                           "as it must be for opposite corners. 12 cm² copies the top-left "
                           "area, and 20 and 18 come from adding or copying rather than "
                           "using the ratio."}


def f_5366b95c(q):
    """'The tan symbol is meant to be inside the triangle with the angular arc.'

    θ sat below the base outside the triangle, with no arc. It is now inside, at C, on
    an arc between the two sides that make the angle. The triangle is redrawn to scale
    (5 by 12 at 18 px per cm; it was drawn 120 by 180), and the '12' on the base is gone:
    the stem gives 13 and 5 and asks for the third side's part, and the figure was
    printing that third side for the student."""
    u = 18
    B = (60.0, 190.0)
    C = (B[0] + 12 * u, B[1])
    A = (B[0], B[1] - 5 * u)
    L = math.hypot(C[0] - A[0], C[1] - A[1])
    ca = ((A[0] - C[0]) / L, (A[1] - C[1]) / L)
    ra = 34
    p1 = (C[0] - ra, C[1])
    p2 = (C[0] + ra * ca[0], C[1] + ra * ca[1])
    half = math.atan2(-ca[1], -ca[0]) / 2                     # half the angle at C
    th = (C[0] - 58 * math.cos(half), C[1] - 58 * math.sin(half) + 5)
    mid = ((A[0] + C[0]) / 2, (A[1] + C[1]) / 2)
    nrm = (-ca[1], ca[0])                                     # points up-right, outward
    if nrm[1] > 0:
        nrm = (-nrm[0], -nrm[1])
    lab13 = (mid[0] + 14 * nrm[0], mid[1] + 14 * nrm[1] + 4)
    svg = (SVG_OPEN.format(w=320, h=215)
           + path(f"M{A[0]:g} {A[1]:g}L{B[0]:g} {B[1]:g}L{C[0]:g} {C[1]:g}Z")
           + path(f"M{B[0]} {B[1] - 14}H{B[0] + 14}V{B[1]}", w=1.5)
           + path(f"M{p1[0]:.1f} {p1[1]:.1f}A{ra} {ra} 0 0 1 {p2[0]:.1f} {p2[1]:.1f}", w=1.5)
           + t(*th, "θ", 14)
           + t(A[0] - 10, A[1] + 4, "A", anchor="end")
           + t(B[0] - 10, B[1] + 6, "B", anchor="end")
           + t(C[0] + 10, C[1] + 6, "C", anchor="start")
           + t(B[0] - 10, (A[1] + B[1]) / 2 + 5, "5", anchor="end")
           + t(*lab13, "13")
           + "</svg>")
    return {"figure_svg": svg}


def f_05650106(q):
    """'Point X is shown at the value 1, not the value 5.' It was. The line ran -3 to 2,
    so 5 was not even on it. Redrawn from -4 to 6 with W on -3 and X on 5, every tick
    numbered, and Y (the answer) not marked."""
    sp, x0 = 25, 30
    X = lambda v: x0 + sp * (v + 4)                           # noqa: E731
    ticks = "".join(f"M{X(v)} 48V62" for v in range(-4, 7))
    nums = "".join(t(X(v), 80, ("−" + str(-v)) if v < 0 else str(v), 12)
                   for v in range(-4, 7))
    svg = (SVG_OPEN.format(w=320, h=100)
           + path(f"M15 55H305M297 50L305 55L297 60" + ticks)
           + nums
           + f'<circle cx="{X(-3)}" cy="55" r="5" fill="currentColor"/>'
           + f'<circle cx="{X(5)}" cy="55" r="5" fill="currentColor"/>'
           + t(X(-3), 38, "W") + t(X(5), 38, "X")
           + "</svg>")
    return {"figure_svg": svg}


def f_66d38eef(q):
    """'Create a little more distance between the text/numbers and the sides.'

    Every label is now at least 8 px off the line it names, and B sits above the apex
    instead of inside it. The figure was also not to scale (a 15 cm side drawn shorter
    than the 10 cm one), so it is redrawn at 8 px per cm.

    Reading it turned up a wrong letter in the stem: it called the rectangle's height
    'DE = 15 cm', but DE is the bottom, 10 cm, in the figure and in the explanation. The
    15 cm side is CD, and the stem says so now."""
    s = 8
    xa, ya = 100, 100
    xc = xa + 10 * s
    yd = ya + 15 * s
    yb = ya - 10 * s * math.sqrt(3) / 2
    xb = (xa + xc) / 2
    svg = (SVG_OPEN.format(w=280, h=250)
           + path(f"M{xa} {ya}L{xb:g} {yb:.1f}L{xc} {ya}Z"
                  f"M{xa} {ya}V{yd}H{xc}V{ya}")
           + t(xb, yb - 9, "B")
           + t(xa - 9, ya + 5, "A", anchor="end")
           + t(xc + 9, ya + 5, "C", anchor="start")
           + t(xc + 9, yd + 12, "D", anchor="start")
           + t(xa - 9, yd + 12, "E", anchor="end")
           + t(xb, yd + 20, "10 cm", 12)
           + t(xc + 10, (ya + yd) / 2 + 4, "15 cm", 12, anchor="start")
           + "</svg>")
    return {"figure_svg": svg,
            "stem": "In the figure below, triangle ABC is equilateral and sits on top of "
                    "rectangle ACDE. If AC = 10 cm and the height of the rectangle "
                    "CD = 15 cm, what is the total perimeter of the combined shape BCDEA "
                    "(the outer boundary), in centimetres?"}


def f_5f486830(q):
    """'If possible, translate the list of numbers and make it a proper table.'

    The table was typed into the stem with '|' between the columns. It is now drawn as a
    two-column table, and the stem keeps only the question."""
    rows = [("20", "3"), ("30", "5"), ("40", "7"), ("50", "4"), ("60", "1")]
    x0, y0, w1, w2, h = 30, 10, 120, 150, 26
    n = len(rows) + 1
    grid = (f"M{x0} {y0}H{x0 + w1 + w2}V{y0 + n * h}H{x0}Z"
            f"M{x0 + w1} {y0}V{y0 + n * h}"
            + "".join(f"M{x0} {y0 + k * h}H{x0 + w1 + w2}" for k in range(1, n)))
    body = (f'<rect x="{x0}" y="{y0}" width="{w1 + w2}" height="{h}" '
            f'fill="currentColor" fill-opacity=".1"/>'
            + path(grid, w=1.2)
            + t(x0 + w1 / 2, y0 + 17, "Distance (km)", 12, bold=True)
            + t(x0 + w1 + w2 / 2, y0 + 17, "Number of members", 12, bold=True))
    for k, (a, b) in enumerate(rows, start=1):
        body += t(x0 + w1 / 2, y0 + k * h + 17, a, 12)
        body += t(x0 + w1 + w2 / 2, y0 + k * h + 17, b, 12)
    svg = SVG_OPEN.format(w=330, h=y0 * 2 + n * h) + body + "</svg>"
    return {"figure_svg": svg,
            "stem": "The table below shows the distances (in km) cycled by members of a "
                    "Melbourne cycling club on a Saturday ride. What is the average "
                    "distance cycled per member, to the nearest kilometre?"}


def f_aeca13ea(q):
    """'Question states "in the diagram," but does not show a diagram. The answer cannot
    be narrowed down between either 130 or 50 degrees.'

    True on both counts: without a picture there is no way to tell whether A and D sit on
    the same side of the transversal, and that is what decides between co-interior (50)
    and alternate (130). A diagram is drawn: AB parallel to CD (arrow marks on both), the
    transversal through B, E and C, the 130° marked at B and the unknown at C, with A and
    D on the same side so the angles are co-interior."""
    B = (150.0, 60.0)
    d = (math.cos(math.radians(50)), math.sin(math.radians(50)))
    C = (B[0] + (110 / d[1]) * d[0], 170.0)
    E = ((B[0] + C[0]) / 2, (B[1] + C[1]) / 2)
    A = (40.0, 60.0)
    D = (110.0, 170.0)
    tr0 = (B[0] - 30 * d[0], B[1] - 30 * d[1])
    tr1 = (C[0] + 30 * d[0], C[1] + 30 * d[1])
    r = 22
    b1 = (B[0] + r * d[0], B[1] + r * d[1])
    c1 = (C[0] - r * d[0], C[1] - r * d[1])

    def chev(x, y):
        return f"M{x - 5} {y - 5}L{x} {y}L{x - 5} {y + 5}"

    lb = (B[0] + 40 * math.cos(math.radians(115)), B[1] + 40 * math.sin(math.radians(115)))
    lc = (C[0] + 38 * math.cos(math.radians(205)), C[1] + 38 * math.sin(math.radians(205)))
    svg = (SVG_OPEN.format(w=300, h=215)
           + path(f"M{A[0]:g} {A[1]:g}H{B[0] + 60:g}M{D[0]:g} {D[1]:g}H{C[0] + 40:.1f}"
                  f"M{tr0[0]:.1f} {tr0[1]:.1f}L{tr1[0]:.1f} {tr1[1]:.1f}")
           + path(chev(85, 60) + chev(170, 170), w=1.5)
           + path(f"M{b1[0]:.1f} {b1[1]:.1f}A{r} {r} 0 0 1 {B[0] - r:g} {B[1]:g}"
                  f"M{C[0] - r:.1f} {C[1]:g}A{r} {r} 0 0 1 {c1[0]:.1f} {c1[1]:.1f}", w=1.5)
           + "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="currentColor"/>'
                     for x, y in (A, B, C, D, E))
           + t(A[0], A[1] - 10, "A") + t(B[0] + 8, B[1] - 8, "B", anchor="start")
           + t(C[0] - 6, C[1] + 20, "C", anchor="end") + t(D[0], D[1] + 20, "D")
           + t(E[0] + 10, E[1] - 2, "E", anchor="start")
           + t(lb[0], lb[1] + 4, "130°", 12) + t(lc[0] - 2, lc[1] + 4, "?", 13, bold=True)
           + "</svg>")
    return {"figure_svg": svg,
            "stem": "In the diagram below, AB is parallel to CD. The line through B and C "
                    "is a transversal, and E is a point on it between B and C. Angle ABE "
                    "measures 130°. What is the size of angle BCD?",
            "explanation": "A and D are on the same side of the transversal, so angles "
                           "ABE and BCD are co-interior angles between parallel lines and "
                           "add to 180°. Angle BCD = 180° − 130° = 50°. 130° would be "
                           "right only if the angles were alternate, with A and D on "
                           "opposite sides. 40° treats the angles as complementary, and "
                           "230° adds 100° instead of subtracting from 180°."}


def f_9ad41d04(q):
    """'Use the proper fractional notation instead of the slash "/" symbol.'

    Selectly prints the stem as plain text, so a stacked fraction cannot be typed into
    it. The expression is drawn as a figure instead, with real fraction bars, and the stem
    points to it. The four options stay as typed text: an option is a button, and a
    button cannot hold a picture."""
    def frac(cx, top, bot):
        w = 26 + 8 * len(bot)
        return (t(cx, 36, top, 18) + path(f"M{cx - w / 2:g} 45H{cx + w / 2:g}", w=1.6)
                + t(cx, 66, bot, 18))
    svg = (SVG_OPEN.format(w=260, h=80)
           + frac(80, "x", "x − y") + t(130, 51, "−", 20) + frac(180, "y", "y − x")
           + "</svg>")
    return {"figure_svg": svg,
            "stem": "Simplify the expression shown below.",
            "option_a": "(x − y)/(y − x)", "option_b": "(x + y)/(y − x)",
            "option_c": "(x − y)/(x + y)", "option_d": "(x + y)/(x − y)",
            "explanation": "y − x is the same as −(x − y), so the second fraction is "
                           "y/(−(x − y)) = −y/(x − y). Subtracting it means adding "
                           "y/(x − y). Both fractions now have the denominator x − y, so "
                           "the result is (x + y)/(x − y)."}


# ======================================================== key / options / wording
def f_d39176ed(q):
    """'The explanation agrees that 22/130 is the correct option, but the answer says
    25/130. Just make C the right one.' Counted again: 13 numbers end in 5 (25 to 145)
    and 50-59 adds 9 more once 55 is not counted twice, so 22. Key moved to C."""
    return {"correct_answer": "C",
            "explanation": "From 20 to 149 there are 149 − 20 + 1 = 130 integers. Those "
                           "ending in 5 are 25, 35, …, 145: 13 numbers. Those with 5 in the "
                           "tens place are 50 to 59: 10 numbers, but 55 is already counted, "
                           "so 9 are new. No number in the range has 5 in the hundreds "
                           "place. That is 13 + 9 = 22, so the probability is 22/130. "
                           "23/130 counts 55 twice, and 24/130 and 25/130 over-count "
                           "further."}


def f_5e0f6626(q):
    """'The answer is 130, as the explanation says, but the marked correct answer is
    150.' 540 − 2(110) − 2(95) = 130, which is D. Key moved to D."""
    return {"correct_answer": "D"}


def f_0605319e(q):
    """'The answer is clearly option A ... C would share an edge with X.' The reviewer
    is right. X, B, A, C are a straight strip of four, and in a strip, squares two apart
    are opposite: X with A, B with C. Key moved to A and the explanation rewritten."""
    return {"correct_answer": "A",
            "explanation": "X, B, A and C form a straight column of four squares. When a "
                           "strip of four folds into a loop, each square ends up opposite "
                           "the one two places along: X is opposite A, and B is opposite C. "
                           "D and E, the two arms beside A, fold up to face each other. So "
                           "the face opposite X is A. B is next to X in the net, and C "
                           "folds round to meet X along an edge, so neither can be opposite "
                           "it; D is one of the side faces."}


def f_87888e6f(q):
    """'If r = 2, the answer is 22. 25 simply does not fit.' The total is 5r + 12, so
    17, 22, 27, ...; of the four options only 22 is on that list. Key moved to C."""
    return {"correct_answer": "C",
            "explanation": "Let the number of rabbits be r. Then there are r + 3 parrots "
                           "and 3(r + 3) dogs, so the total is r + (r + 3) + 3(r + 3) = "
                           "5r + 12. With 2 rabbits that is 2 + 5 + 15 = 22. Any total must "
                           "be 12 more than a multiple of 5, so it ends in 2 or 7: 19, 25 "
                           "and 28 cannot be totals."}


def f_3d5a5b9b(q):
    """'5 matches were drawn ... 25% of 20 is 5.' The explanation found 25%, then
    invented a '10%' the stem never says and keyed 2. Option A (the key letter) becomes
    5 and the explanation is rewritten."""
    return {"option_a": "5",
            "explanation": "Australia and England won 40% + 35% = 75% of the matches "
                           "between them, so 25% were draws. 25% of 20 is 20 ÷ 4 = 5 "
                           "matches. Check: Australia won 8 and England 7, and 8 + 7 + 5 = "
                           "20."}


def f_7d981502(q):
    """'By simply adding a single white block to the right, it is symmetrical.' Right:
    W B W W B W reads the same both ways. The row already ends in the palindrome
    B W W B, so only the first W needs mirroring. Option B (the key letter) becomes 1.
    5 stays as a distractor -- it is the full reversed copy the old explanation built."""
    return {"option_a": "3", "option_b": "1", "option_c": "5", "option_d": "4",
            "explanation": "The last four tiles, B W W B, already read the same both ways. "
                           "Only the first tile, W, has no partner, so one white tile on "
                           "the right gives W B W W B W, which is symmetrical. Adding the "
                           "whole row reversed (5 tiles) also works but is not the "
                           "smallest, and mirroring about the last tile takes 4."}


def f_6a120a5b(q):
    """'Option B and C are the same thing.' They named the same two shapes in the other
    order, which a careful reader is entitled to call the same answer. C is replaced with
    a real distractor: two radii and an arc do not make a triangle (that needs a chord)."""
    return {"option_c": "A triangle and a segment",
            "explanation": "Two radii and the arc between them cut out a sector - the "
                           "pizza-slice shape, with the centre as its point. A chord "
                           "slices off a segment, the region between the straight chord "
                           "and the curve. A triangle would need a chord in place of the "
                           "arc. A quadrant is one particular sector, the one with a 90 "
                           "degree angle, so it is not the general name. An arc is part of "
                           "the circle's edge and a tangent is a line touching the outside, "
                           "so neither encloses a region."}


def f_6bad5c4a(q):
    """'Both option C and D are correct (4+3+5 units = 12 units).' D was '4 + 3 + 5
    units', which is 12. The options are now four different lengths with D, the key
    letter, reading '12 units'."""
    return {"option_a": "17 units", "option_b": "20 units", "option_c": "14 units",
            "option_d": "12 units",
            "explanation": "PQ is horizontal, 5 − 1 = 4 units. QR is vertical, 4 − 1 = 3 "
                           "units. PR is the hypotenuse of a right-angled triangle with "
                           "legs 4 and 3, so PR = √(16 + 9) = 5 units. The perimeter is "
                           "4 + 3 + 5 = 12 units. 14 adds 4 + 3 for the slanted side, 17 "
                           "adds the 5 twice, and 20 is 4 × 5."}


def f_80da65db(q):
    """'Option C and D are correct (as both -5 and 4 is the answer).' D was '4 and -5',
    which is also true. D is now 20, the number a student gets by multiplying the two
    constants instead of setting each factor to zero."""
    return {"option_d": "20",
            "explanation": "A product is zero only when one of its factors is zero. "
                           "k + 5 = 0 gives k = −5, and k − 4 = 0 gives k = 4. Of the "
                           "options only −5 is one of these: (−5 + 5)(−5 − 4) = 0 × (−9) "
                           "= 0. 5 and −4 have the signs the wrong way round, and 20 "
                           "multiplies the constants 5 and 4."}


def f_b7693921(q):
    """'If x is 3 and y is -3 they are h(0) but they multiply to 9? Delete or clarify.'

    The reviewer read h(3) as 3. Clarified rather than deleted (the form keeps its size):
    the stem now says h is a rule, tells the student to put x = 0 and y = 0 in, and the
    explanation says outright why h(3) × h(−3) is not 3 × (−3)."""
    return {"stem": "A rule h turns any number into another number, and for every pair "
                    "of numbers x and y it obeys h(x + y) = h(x) × h(y). By putting x = 0 "
                    "and y = 0 into this rule, find which of the following must be true "
                    "of h(0).",
            "explanation": "With x = 0 and y = 0 the rule says h(0) = h(0) × h(0). A "
                           "number equal to its own square is 0 or 1, so h(0) = 0 or 1. "
                           "Note that h(3) means the number the rule gives for 3, not 3 "
                           "itself, so h(0) = h(3) × h(−3) is true but tells us nothing "
                           "new. Other values fail: if h(0) were 2, the rule would need "
                           "2 = 2 × 2."}


def f_d4966c1e(q):
    """'Not really a question that would come in the exam.' It described the two forms
    instead of using them. Re-cut to using one: read the vertex off vertex form and
    substitute x = 0 for the y-intercept. Key stays A."""
    return {"stem": "The parabola y = 2(x − 3)² + 5 is written in vertex form. What "
                    "are its vertex and its y-intercept?",
            "option_a": "Vertex (3, 5), y-intercept 23",
            "option_b": "Vertex (−3, 5), y-intercept 23",
            "option_c": "Vertex (3, 5), y-intercept 5",
            "option_d": "Vertex (3, −5), y-intercept 13",
            "explanation": "In y = a(x − h)² + k the vertex is (h, k), so here it is "
                           "(3, 5). The y-intercept is where x = 0: y = 2(0 − 3)² + 5 = "
                           "2 × 9 + 5 = 23. (−3, 5) takes the sign inside the bracket at "
                           "face value. 5 is the vertex's height, not the y-intercept. "
                           "(3, −5) and 13 flip the sign of k: 2 × 9 − 5 = 13."}


def f_dd93aedb(q):
    """'Not really a quantitative reasoning question.' It asked WHY a prediction was
    unreliable, with four sentences as options, and opened 'Using the same rule' with no
    rule before it. Re-cut to using the rule, stated in full. Key stays C."""
    return {"stem": "A kiosk models its daily ice-cream sales with the rule s = 12t + 40, "
                    "where t is the temperature in degrees Celsius and s is the number of "
                    "ice-creams sold. How many sales does the rule predict on a 25 degree "
                    "day?",
            "option_a": "300", "option_b": "1300", "option_c": "340", "option_d": "65",
            "explanation": "Substitute t = 25: s = 12 × 25 + 40 = 300 + 40 = 340. 300 "
                           "forgets the + 40, 1300 adds 12 and 40 before multiplying by "
                           "25, and 65 adds 25 and 40 and ignores the 12."}


def f_0d1ba57f(q):
    """'Strange to round pi to 3.14159 instead of 3.14 or 22/7.' Changed to 22/7, which
    keeps the answer at 629 and keeps the round-up step: 88/7 ÷ 0.02 = 4400/7 = 628 r 4.
    With 3.14 the answer would be exactly 628 and the 'minimum whole tiles' step would
    vanish."""
    return {"stem": "A mosaic artist is creating a circular mural with a diameter of 4 "
                    "metres. Each hexagonal tile has an area of 0.02 m². What is the "
                    "minimum number of whole tiles required to cover the mural? "
                    "(Use π ≈ 22/7)",
            "explanation": "The radius is 2 m, so the area is 22/7 × 2² = 88/7 m². "
                           "Dividing by 0.02 is the same as multiplying by 50, giving "
                           "4400/7 = 628 remainder 4, so just over 628 tiles. A part tile "
                           "still has to be a whole tile, so 629 are needed."}


def f_9d857ccb(q):
    """'Working out requires a calculator.' 1.03⁴ does. Re-cut to 10% compounded
    half-yearly for ONE year: 1.05² = 1.1025 is two lines by hand. Same error, same
    options in the same order, key stays C."""
    return {"stem": "A $10 000 term deposit pays 10% per annum compounded half-yearly. "
                    "Dev works out the balance after 1 year as 10 000 × 1.10² = $12 100. "
                    "Which statement identifies his error and gives the correct balance?",
            "option_a": "$11 000 — half-yearly compounding is identical to annual, so it "
                         "should be 10 000 × 1.10.",
            "option_b": "$10 500 — the rate should be halved but there is only 1 period, "
                        "giving 10 000 × 1.05.",
            "option_c": "$11 025 — each half-year earns 5%, not 10%, so it should be "
                        "10 000 × 1.05².",
            "option_d": "$12 100 — Dev's calculation is correct.",
            "explanation": "Half-yearly compounding splits the annual rate across two "
                           "periods: 10% ÷ 2 = 5% per half-year, and 1 year has 2 of them. "
                           "So the balance is 10 000 × 1.05 × 1.05 = 10 500 × 1.05 = "
                           "$11 025. Dev used two periods but left the rate at 10%, which "
                           "is a full 21% in one year. Treating it as annual gives $11 000 "
                           "and ignores the interest on the interest, and halving the rate "
                           "but using one period gives $10 500, which covers only half a "
                           "year."}


def f_ee877596(q):
    """'Difficult to solve without a calculator.' 0.95³ is. Re-cut to 10% a year from
    2000: 2000, 1800, 1620, 1458 -- three subtractions. Key stays C."""
    return {"stem": "The population of kangaroos in a national park is decreasing by 10% "
                    "each year. If the current population is 2000, what will the "
                    "population be in 3 years?",
            "option_a": "1400", "option_b": "1620", "option_c": "1458", "option_d": "1800",
            "explanation": "Each year the population keeps 90%. After 1 year: 2000 − 200 "
                           "= 1800. After 2: 1800 − 180 = 1620. After 3: 1620 − 162 = 1458. "
                           "1400 takes 30% off the original in one go, and 1620 and 1800 "
                           "stop after two years and one year."}


def f_6f7e4a25(q):
    """'Calculator needed to raise 0.95^5.' Re-cut to 0.9 over 2 years: 500 × 0.81 = 405
    litres a household, × 200 = 81 000. Key stays B."""
    return {"stem": "Daily water consumption per household in a new development is "
                    "modelled by W(t) = 500 × (0.9)ᵗ litres, where t is the number of "
                    "years since the development was established. If there are 200 "
                    "identical households, what is the total daily water consumption for "
                    "all households after 2 years?",
            "option_a": "90,000 litres", "option_b": "81,000 litres",
            "option_c": "100,000 litres", "option_d": "72,900 litres",
            "explanation": "W(2) = 500 × 0.9 × 0.9 = 500 × 0.81 = 405 litres per "
                           "household. For 200 households: 405 × 200 = 81,000 litres. "
                           "90,000 is after 1 year, 72,900 after 3 years, and 100,000 "
                           "ignores the decrease."}


def f_630d2093(q):
    """'Needs calculator to do 1.5^5.' (1.015⁵.) Re-cut to a suburb of 20,000 growing
    10% a year for 2 years: 20,000, 22,000, 24,200. Key stays A."""
    return {"stem": "The population of a fast-growing outer suburb of Perth is 20,000. "
                    "If it grows by 10% each year, what will the population be in 2 "
                    "years?",
            "option_a": "24,200", "option_b": "24,000", "option_c": "22,000",
            "option_d": "26,620",
            "explanation": "After 1 year: 20,000 + 2,000 = 22,000. After 2 years: 22,000 "
                           "+ 2,200 = 24,200. 24,000 adds 10% of the ORIGINAL twice, "
                           "missing the growth on the growth. 22,000 is after 1 year and "
                           "26,620 after 3."}


def f_0b23f6f2(q):
    """'Q is shown on the y-axis, so its x-value (m) should be 0.' Right: the figure
    puts Q on the y-axis and R at the origin, while the stem asked for Q's x-coordinate
    and keyed −6. The figure is kept and the stem now asks about P, which IS 6 to the
    left of Q. Key stays D (−6)."""
    return {"stem": "In the figure below, PQRS is a rectangle. R is at the origin O and Q "
                    "is on the y-axis. The coordinates of P are (m, 6). If PQ = 6, what "
                    "is the value of m?",
            "explanation": "Q is on the y-axis at height 6, so Q is (0, 6). P is on the "
                           "same horizontal line, 6 units to the LEFT of Q, so P is "
                           "(0 − 6, 6) = (−6, 6) and m = −6. 0 is Q's x-coordinate, 6 "
                           "goes the wrong way, and −3 halves the distance."}


# ---------------------------------------------------- notation ('root', '^', vinculum)
def f_a284e88b(q):
    """'Replace text "root" in answer options with the square root symbol.' Done in
    the options and the explanation. The explanation also described the distractors by
    position and got every position wrong; it now names them by value."""
    return {"option_a": "6 cm and 6√2 cm", "option_b": "6√3 cm and 12√3 cm",
            "option_d": "6 cm and 6√3 cm",
            "explanation": "The side opposite the 30° angle is 12 × sin 30° = 12 × ½ = "
                           "6 cm - in any 30-60-90 triangle that side is exactly half the "
                           "hypotenuse. The other side is 12 × cos 30° = 12 × √3/2 = 6√3 cm. "
                           "Check: 36 + 108 = 144 = 12². 6√2 belongs to a 45-45-90 "
                           "triangle. 12√3 cm is longer than the 12 cm hypotenuse, which "
                           "is impossible. 4 cm and 8 cm split 12 in the ratio 1 : 2 "
                           "without using the trigonometric ratios at all."}


def f_669ff03e(q):
    """'Use sqrt symbols instead of the text "root".' Done, and the explanation's
    distractor notes named the wrong options; they are now matched to the values."""
    return {"stem": "Rationalise the denominator of 5/(3 − √2).",
            "option_a": "(15 + 5√2)/11", "option_b": "(15 + 5√2)/9",
            "option_c": "(15 − 5√2)/7", "option_d": "(15 + 5√2)/7",
            "explanation": "Multiply top and bottom by the conjugate 3 + √2. The "
                           "numerator becomes 5(3 + √2) = 15 + 5√2 and the denominator "
                           "becomes 3² − (√2)² = 9 − 2 = 7, so the answer is "
                           "(15 + 5√2)/7. Dividing by 11 adds the 9 and the 2 instead of "
                           "subtracting. Dividing by 9 forgets the −2 altogether. "
                           "(15 − 5√2)/7 has the right denominator but the wrong sign on "
                           "top."}


def f_5d6922c4(q):
    """'Replace text root with the real sqrt symbol.'"""
    return {"option_a": "√100", "option_b": "√36", "option_c": "√40", "option_d": "√49",
            "explanation": "A square root is rational only when the number under it is a "
                           "perfect square. 36, 49 and 100 are the squares of 6, 7 and 10, "
                           "so those roots are whole numbers. 40 sits between 36 and 49, so "
                           "√40 lies between 6 and 7 and cannot be written as an exact "
                           "fraction - its decimal never ends or repeats. It simplifies to "
                           "2√10, but √10 is still irrational."}


def f_5392c10c(q):
    """'Replace text root with sqrt symbol.'"""
    return {"option_b": "5√3 cm", "option_c": "5√2 cm", "option_d": "10√2 cm",
            "explanation": "A diagonal cuts the square into two 45-45-90 triangles, in "
                           "which the hypotenuse is √2 times a side. So side × √2 = 10, "
                           "giving side = 10/√2 = 5√2 cm, about 7.07 cm. 10√2 multiplies "
                           "by √2 instead of dividing, making the side longer than the "
                           "diagonal. 5 cm simply halves the diagonal. 5√3 uses the "
                           "30-60-90 ratio instead."}


def f_3b1c760d(q):
    """'Use the sqrt symbol instead of the root text.'"""
    return {"stem": "Simplify 3√12 − √27.",
            "option_a": "6√3", "option_b": "9√3", "option_c": "3√3", "option_d": "9",
            "explanation": "Simplify each surd first: √12 = 2√3, so 3√12 = 6√3, and "
                           "√27 = 3√3. They are now like terms: 6√3 − 3√3 = 3√3. 9 comes "
                           "from subtracting under one root, √(108 − 27) = √81, which "
                           "surds do not allow. 9√3 adds the terms instead of subtracting, "
                           "and 6√3 drops the second term."}


def f_a682cfea(q):
    """'The ^ is being used instead of the standard exponent notation.'

    Selectly prints plain text, so a fractional index cannot be set as a superscript.
    The question is written with roots instead -- a to the power 2/3 is the cube root of
    a² -- which is how round 12 handled the same note on 0ba593f2. Same skill, same
    four exponents (1/2, 17/12, 8/9, 6/7), key stays C."""
    return {"stem": "The cube root of a² is raised to the power three-quarters. Which of "
                    "the following is the result?",
            "option_a": "¹²√(a¹⁷)", "option_b": "⁹√(a⁸)", "option_c": "√a",
            "option_d": "⁷√(a⁶)",
            "explanation": "The cube root of a² is a to the power 2/3. Raising a power to "
                           "a power multiplies the indices: 2/3 × 3/4 = 6/12 = 1/2, and a "
                           "to the power 1/2 is √a. ¹²√(a¹⁷) is a to the power 17/12, "
                           "which ADDS the two fractions. ⁹√(a⁸) is 8/9, which divides "
                           "one by the other. ⁷√(a⁶) is 6/7, which multiplies the tops but "
                           "adds the bottoms."}


def f_d4096e9a(q):
    """'The repeating decimal symbol is not meant to reach the 0; the vinculum is dotted,
    not a flat straight line.'

    The stem stacked a combining bar on the point and on 2, 7 AND 3 -- so it also named
    the wrong block, 273, while the decimal it spelled out is 0.2727... Rewritten in the
    Australian dot notation, a dot over the first and last repeating digit: 0.2̇7̇."""
    return {"stem": "What is the 143rd digit after the decimal point in the recurring "
                    "decimal 0.2̇7̇ (that is, 0.272727…)?",
            "explanation": "The repeating block is 27, two digits long, so every odd-"
                           "numbered place holds 2 and every even-numbered place holds 7. "
                           "143 is odd (143 = 2 × 71 + 1), so the 143rd digit is 2."}


REPAIRS = {
    "09506111": f_09506111, "6a120a5b": f_6a120a5b, "b7693921": f_b7693921,
    "d4966c1e": f_d4966c1e, "167b73cc": f_167b73cc, "4d8c6127": f_4d8c6127,
    "d39176ed": f_d39176ed, "48fb8741": f_48fb8741, "a284e88b": f_a284e88b,
    "3d5a5b9b": f_3d5a5b9b, "9d857ccb": f_9d857ccb, "a682cfea": f_a682cfea,
    "d4096e9a": f_d4096e9a, "5e0f6626": f_5e0f6626, "0605319e": f_0605319e,
    "87888e6f": f_87888e6f, "0d1ba57f": f_0d1ba57f, "5366b95c": f_5366b95c,
    "5f486830": f_5f486830, "669ff03e": f_669ff03e, "ee877596": f_ee877596,
    "6f7e4a25": f_6f7e4a25, "9ad41d04": f_9ad41d04, "6bad5c4a": f_6bad5c4a,
    "05650106": f_05650106, "7d981502": f_7d981502, "aeca13ea": f_aeca13ea,
    "80da65db": f_80da65db, "630d2093": f_630d2093, "0b23f6f2": f_0b23f6f2,
    "dd93aedb": f_dd93aedb, "66d38eef": f_66d38eef, "5d6922c4": f_5d6922c4,
    "5392c10c": f_5392c10c, "3b1c760d": f_3b1c760d,
}


def read_csv():
    with CSV.open(newline="", encoding="utf-8") as fh:
        return [r for r in csv.DictReader(fh) if r["form_id"].startswith("vic-")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--only", help="comma-separated short ids, for working on one")
    args = ap.parse_args()

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    record, refused, changed = [], [], 0
    for f in read_csv():
        qid = f["qbank_id"]
        short = qid[:8]
        if args.only and short not in args.only.split(","):
            continue
        fn = REPAIRS.get(short)
        if fn is None:
            refused.append((short, "no repair written"))
            continue
        row = dict(con.execute("SELECT * FROM questions WHERE id=?", (qid,)).fetchone())
        before = findings(row)
        after_row = dict(row)
        after_row.update(fn(row))
        after = findings(after_row)
        gained = after - before
        if gained:
            refused.append((short, f"would newly fire {sorted(gained)}"))
            continue
        touched = [k for k in FIELDS if after_row.get(k) != row.get(k)]
        if not touched:
            refused.append((short, "repair changed nothing"))
            continue
        changed += 1
        record.append({"id": qid, "form": f["form_id"], "pos": f["form_position"],
                       "note": f["note"], "action": "repaired", "fields": touched,
                       "why": (fn.__doc__ or "").strip(),
                       "cleared": sorted(before - after),
                       "before": {k: row.get(k) for k in touched},
                       "after": {k: after_row.get(k) for k in touched}})
        if args.apply:
            sets = ", ".join(f"{k}=?" for k in touched)
            con.execute(f"UPDATE questions SET {sets} WHERE id=?",
                        [after_row[k] for k in touched] + [qid])

    if args.apply:
        con.commit()
        RECORD.parent.mkdir(parents=True, exist_ok=True)
        RECORD.write_text(json.dumps(record, indent=1, ensure_ascii=False))
    con.close()
    print(f"{changed} repaired, {len(refused)} refused"
          f"{' (DRY RUN)' if not args.apply else ''}")
    for short, why in refused:
        print(f"  REFUSED {short}: {why}")
    cleared = sorted({c for r in record for c in r.get("cleared", [])})
    print(f"findings cleared: {cleared or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
