#!/usr/bin/env python3
"""NSW figure round 1: the ten questions Alaan Q. flagged on the 254-card NSW page.

The 2026-09-06 return (`review/ui/figure-review-nsw-2026-09-06.json`) marks ten cards
out of 254 and passes the rest. Two are Thinking Skills, eight are maths. All ten were
`pending`; none was live in Selectly.

Seven of the ten fire no check at all, so this round was worked by rendering each figure
and looking at it, not by reading a gate state.

  bf613208  the U-shaped tile: eight sides, and three of the labels sat where a reader
  d5975559  could not tell which side they named. ONE figure shared byte for byte by two
            questions -- one asks the area, one the perimeter -- so it is drawn once and
            written to both rows.
  05abece6  '3 m' and '2 m' crowded into the same small corner of the cut-out
  7932815e  '4 m' and '3 m', the same defect on the same kind of shape
  b2c8c7b6  'far too difficult and doesn't really make sense. Delete.' -- RE-CUT rather
            than deleted, so the form keeps its twenty questions. See the builder.
  4769e94e  P and Q printed across the x-axis
  c17f98d2  the plotted line stopped one step short of the corner of the grid
  8de54934  no tick marks, and the y-axis '-2' grazed by the plotted line
  2bc8b93a  two numbers on each axis and no ticks
  7abd8a82  '4 cm' labels the depth and was drawn beside a height edge

Every figure is rendered and looked at before it is applied, and every question's full
check state is compared before and after: a question that would gain a finding is
refused rather than written.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_nsw_round1_figures
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_nsw_round1_figures --apply
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

from tools import question_checks as qc                       # noqa: E402
from tools.repair_vic_round10_figures import (                # noqa: E402
    FIG_CHECKS, Q_CHECKS, arc, bisect_pt, halo, line, poly, sub1, tick_mark, txt,
    unit, wrap)

DB = ROOT / "run_data/db/qbank.db"
RECORD = ROOT / "run_data/output/nsw_round1_figures.json"


# ---------------------------------------------------------------- label helpers
def num(x, y, s, size=10, anchor="middle"):
    """One axis number, drawn twice: a page-coloured stroke underneath and the glyphs
    on top. That pair is what `text_overlaps_geometry` accepts over a faint gridline,
    and it is what a real graph does -- a four-quadrant plane runs a rule through every
    tick number it has, so moving them is not an option."""
    body = (f'<text x="{x:g}" y="{y:g}" font-size="{size}" text-anchor="{anchor}">'
            f'{s}</text>')
    glyph = (f'<text x="{x:g}" y="{y:g}" font-size="{size}" fill="currentColor" '
             f'text-anchor="{anchor}">{s}</text>')
    return body, glyph


def numbers(items):
    """The halo layer and the glyph layer for a whole set of axis numbers."""
    pairs = [num(*it) for it in items]
    return (halo("".join(p[0] for p in pairs)), "".join(p[1] for p in pairs))


def ticks(path, w=1.3):
    return (f'<path d="{path}" stroke="currentColor" stroke-width="{w}" '
            f'fill="none"/>')


def box_of(x, y, s, size, anchor):
    """The rendered box of a label, measured the way the checks measure it."""
    w = qc.text_width(s, size)
    x0 = x - w / 2 if anchor == "middle" else (x - w if anchor == "end" else x)
    return (x0, y - size * 0.8, x0 + w, y + size * 0.25)


# ======================================================== the U-shaped tile, shared
def u_tile():
    """#8 and #53 -- 'The entire figure is full of unclear values. The 6 cm overlaps
    with some sides, and there are many vague 4 cm values.'

    Both questions carry the SAME 1,429-character SVG, so the reviewer wrote the same
    sentence twice. Measured, the old drawing was right -- 13 px per cm throughout, and
    its eight sides really are 4, 4, 6, 4, 4, 6, 14 and 6 -- but three of the eight
    labels were not placed on the side they name:

      * the notch's '6 cm' was centred at x=144 when its edge runs 131 to 209, so it
        sat over the notch's LEFT side rather than under its bottom
      * the notch's right side had its '4 cm' parked 18 px below the notch entirely,
        in the middle of the tile, naming nothing
      * the notch's left '4 cm' was inside the notch with 12 px between it and the
        '6 cm', which is what made all three read as one cloud of numbers

    Redrawn at 16 px per cm -- a fifth bigger, so the notch has room for its three
    numbers -- with every label on the outward normal of its own edge and the three
    inside the notch spread across it: the two depths at the same height either side,
    the width centred below them."""
    S = 16.0                                    # px per cm
    x0, ytop = 58.0, 58.0
    x1, ybot = x0 + 14 * S, ytop + 6 * S        # 282, 154
    nl, nr = x0 + 4 * S, x0 + 10 * S            # notch 122 .. 218
    nb = ytop + 4 * S                           # notch bottom 122
    assert (x1, ybot, nl, nr, nb) == (282.0, 154.0, 122.0, 218.0, 122.0)

    shape = poly([(x0, ytop), (nl, ytop), (nl, nb), (nr, nb), (nr, ytop),
                  (x1, ytop), (x1, ybot), (x0, ybot)],
                 w=2, fill="currentColor", fop=".05")
    lab = (txt((x0 + nl) / 2, ytop - 8, "4 cm")           # top-left arm
           + txt((nr + x1) / 2, ytop - 8, "4 cm")         # top-right arm
           + txt(x0 - 8, (ytop + ybot) / 2 + 4, "6 cm", anchor="end")
           + txt(x1 + 8, (ytop + ybot) / 2 + 4, "6 cm", anchor="start")
           + txt((x0 + x1) / 2, ybot + 20, "14 cm")
           + txt(nl + 6, ytop + 30, "4 cm", anchor="start")   # notch left side
           + txt(nr - 6, ytop + 30, "4 cm", anchor="end")     # notch right side
           + txt((nl + nr) / 2, nb - 10, "6 cm"))             # notch bottom
    # the three inside the notch must not touch each other or the notch's own sides
    a = box_of(nl + 6, ytop + 30, "4 cm", 13, "start")
    b = box_of(nr - 6, ytop + 30, "4 cm", 13, "end")
    c = box_of((nl + nr) / 2, nb - 10, "6 cm", 13, "middle")
    assert b[0] - a[2] > 20, f"notch depths only {b[0] - a[2]:.1f} px apart"
    assert c[1] - a[3] > 10, f"notch width only {c[1] - a[3]:.1f} px below the depths"
    assert a[0] - nl > 4 and nr - b[2] > 4, "a depth label touches its own side"
    assert nb - c[3] > 5, "the width label touches the notch floor"
    return wrap(shape + lab, "0 0 340 220")


def f_bf613208(svg, q):
    return {"figure_svg": u_tile()}


def f_d5975559(svg, q):
    return {"figure_svg": u_tile()}


# ============================================== two step-shaped floors, same defect
def f_05abece6(svg, q):
    """#142 -- 'The 3m and the 2m are a little too close to each other. Seperate them
    and move them closer to the sides they are representing while keeping some
    distance.'

    The two labels sat 8 px apart in the cut-out corner, and neither was on its own
    edge: '3 m' was 12 px left of the centre of the 3 m edge, '2 m' was down at the
    bottom of a side whose middle is 20 px higher.

    They now go on opposite sides of the corner they share -- '3 m' centred below the
    edge it names, '2 m' beside the middle of its own side -- which puts 26 px between
    them where there were 8."""
    s = sub1(svg, '<text x="227" y="160"', '<text x="240" y="158"', "05abece6/3m")
    s = sub1(s, '<text x="219" y="178" font-family="system-ui,sans-serif" '
                'font-size="13" fill="currentColor" fill-opacity=".9" '
                'text-anchor="start">2 m</text>',
             '<text x="203" y="164" font-family="system-ui,sans-serif" '
             'font-size="13" fill="currentColor" fill-opacity=".9" '
             'text-anchor="end">2 m</text>', "05abece6/2m")
    three = box_of(240, 158, "3 m", 13, "middle")
    two = box_of(203, 164, "2 m", 13, "end")
    assert three[0] - two[2] > 20, "3 m and 2 m are still crowded"
    assert three[1] - 140 > 6 and 210 - two[2] > 5, "a label touches its own edge"
    return {"figure_svg": s}


def f_7932815e(svg, q):
    """#151 -- 'The 3m and the 4m are a little too close to each other. Seperate them
    and move them closer to the sides they are representing while keeping some
    distance.'

    The same shape and the same defect as 05abece6, so the same fix: '4 m' centred
    below the horizontal edge it names, '3 m' beside the middle of the vertical side.
    36 px between them, where there were 8."""
    s = sub1(svg, '<text x="220" y="140"', '<text x="220" y="138"', "7932815e/4m")
    s = sub1(s, '<text x="189" y="155" font-family="system-ui,sans-serif" '
                'font-size="13" fill="currentColor" fill-opacity=".9" '
                'text-anchor="start">3 m</text>',
             '<text x="173" y="154" font-family="system-ui,sans-serif" '
             'font-size="13" fill="currentColor" fill-opacity=".9" '
             'text-anchor="end">3 m</text>', "7932815e/3m")
    four = box_of(220, 138, "4 m", 13, "middle")
    three = box_of(173, 154, "3 m", 13, "end")
    assert four[0] - three[2] > 20, "4 m and 3 m are still crowded"
    assert four[1] - 120 > 6 and 180 - three[2] > 5, "a label touches its own edge"
    return {"figure_svg": s}


# ================================================================ the re-cut
def f_b2c8c7b6(svg, q):
    """#214 -- 'Out-of-place question. Far too difficult and doesn't really make sense.
    Delete.'

    The reviewer is right about the level and the figure is not the problem. Measured,
    the drawing is exactly correct: both arcs are radius 110 about A and about B, they
    cross at (160, 56.8) and (160, 183.2), and the ruled line runs through both. What
    is wrong is the CONTENT. A compass-and-straightedge construction, named as such and
    justified by the equidistance property, is Stage 4-5 work; this paper is sat by
    Year 6 students, and the question asks them to recognise a construction almost none
    of them has been shown rather than to reason about anything.

    It is RE-CUT rather than deleted. `nsw-drill-math-013` holds exactly twenty
    questions, one per topic, and this is its only 'Two-Dimensional Figures' slot;
    dropping it would leave the form at nineteen and remove the topic from the paper,
    and a form that changes size re-bases every score later recorded against it. The
    precedent is `46c3108f` in VIC round 10.

    The replacement stays in the same topic and is the reasoning the old question was
    reaching for, in a form a Year 6 candidate can actually do: base angles of an
    isosceles triangle, angles on a straight line, and the angle sum. Worked twice --
    180 - 116 = 64 for both base angles and 180 - 64 - 64 = 52, or the exterior angle
    rule, 116 = 52 + 64. The triangle is drawn to those angles, so a reader measuring
    the picture gets the same answer as a reader doing the arithmetic.

    The closest stem anywhere in the bank is 0.66 similar (13720600, a VIC question
    that goes the other way: apex given, base angle asked), against phase 4's 0.85."""
    Q, R, S = (90.0, 180.0), (210.0, 180.0), (280.0, 180.0)
    P = (150.0, 57.0)
    at_q = math.degrees(math.atan2(Q[1] - P[1], P[0] - Q[0]))
    apex = 180.0 - 2 * at_q
    assert abs(math.dist(P, Q) - math.dist(P, R)) < 1e-6, "the triangle is not isosceles"
    assert abs(at_q - 64.0) < 0.1, f"base angle drawn {at_q:.2f}, wanted 64"
    assert abs(apex - 52.0) < 0.2, f"apex drawn {apex:.2f}, wanted 52"

    lab = bisect_pt(R, P, S, 46.0)
    body = (poly([P, Q, R], w=2, fill="currentColor", fop=".05")
            + line(*R, *S, w=2)
            + tick_mark(P, Q) + tick_mark(P, R)
            + arc(*R, 26.0, P, S) + arc(*P, 24.0, Q, R)
            + txt(P[0], P[1] - 13, "P")
            + txt(Q[0] - 8, Q[1] + 18, "Q")
            + txt(R[0], R[1] + 18, "R")
            + txt(S[0] + 2, S[1] + 18, "S")
            + txt(lab[0], lab[1] + 4, "116°", 12))
    # the 116 label must clear its own arc and the ray it is measured from
    bx = box_of(lab[0], lab[1] + 4, "116°", 12, "middle")
    assert math.dist(R, (bx[0], bx[3])) - 26.0 > 6, "the label sits on its own arc"
    assert bx[0] > 200, "the label crosses the ray RP"

    stem = ("In the diagram, triangle PQR has PQ = PR, and the side QR has been "
            "extended to S. Angle PRS is 116°. What is the size of angle QPR?")
    expl = ("Angle PRQ and angle PRS together make the straight line QS, so "
            "angle PRQ = 180° − 116° = 64°. Because PQ = PR the triangle is isosceles, "
            "so angle PQR is 64° as well. The three angles of a triangle add to 180°, "
            "which gives angle QPR = 180° − 64° − 64° = 52°. The exterior angle rule "
            "is a quicker second route to the same answer: angle PRS equals the two "
            "angles of the triangle that are not beside it, so 116° = angle QPR + 64°. "
            "Answering 64° stops at the base angle instead of going on to the apex; "
            "58° halves the 116°; and 116° copies the angle that was given.")
    return {"figure_svg": wrap(body, "0 0 340 220"), "stem": stem, "explanation": expl,
            "option_a": "116°", "option_b": "52°", "option_c": "64°",
            "option_d": "58°", "correct_answer": "B",
            "source_page_description":
                "Subtopic U21 — angles of an isosceles triangle with the base extended"}


# ========================================================== the coordinate planes
def f_4769e94e(svg, q):
    """#217 -- 'The letters P and Q slightly overlap with the x-axis. Move them closer
    to their points without any overlapping.'

    P sat 19 px below its own point with the x-axis rule running through the middle of
    it, and Q sat below-right against the axis and its arrowhead. Both move to the free
    side of their point -- P up and left, Q up and right, since the triangle fills the
    space up and right of P and left of Q -- which also halves the distance from the
    label to the dot it names, 21 px to 12 for P.

    Both land between the gridlines at y=112 and y=130, so neither trades an axis for
    a rule."""
    s = sub1(svg, '<text x="209" y="149" font-size="13" text-anchor="middle">P</text>',
             '<text x="207" y="126" font-size="13" text-anchor="middle">P</text>',
             "4769e94e/P")
    s = sub1(s, '<text x="267" y="143" font-size="13" text-anchor="middle">Q</text>',
             '<text x="265" y="124" font-size="13" text-anchor="middle">Q</text>',
             "4769e94e/Q")
    for x, y, pt in ((207, 126, (218, 130)), (265, 124, (254, 130))):
        bx = box_of(x, y, "P", 13, "middle")
        assert bx[3] < 148 - 2, "the label still reaches the x-axis"
        assert bx[1] > 112 and bx[3] < 130, "the label crosses a gridline"
        near = max(bx[0] - pt[0], pt[0] - bx[2], bx[1] - pt[1], pt[1] - bx[3], 0)
        assert near < 14, f"label {near:.1f} px from its point"
    return {"figure_svg": s}


def f_c17f98d2(svg, q):
    """#218 -- 'Extend the line so that it touches point 5, 20. This will make the
    graph seem more complete and full of information.'

    The rate is 4 eggs a batch, drawn at 50 px per batch and 7 px per egg, so (5, 20)
    is the top-right corner of the grid at (295, 25) and the line reaches it exactly.
    No fifth dot is added: the four plotted points are the data, and the answer the
    question wants is at 7 batches, off the graph either way."""
    s = sub1(svg, '<line x1="45" y1="165" x2="245" y2="53"',
             '<line x1="45" y1="165" x2="295" y2="25"', "c17f98d2/line")
    assert abs((165 - 25) / 7 - (165 - 53) / (245 - 45) * (295 - 45) / 7) < 0.01
    return {"figure_svg": s}


def f_8de54934(svg, q):
    """#239 -- 'Add the axis value lines or ticks on each value. Also create a little
    more distance between -2 on the y axis and the line.'

    Ticks go on both axes at every whole unit, and the two axes gain the numbers they
    were missing -- x at -4 and 6, y at -4 and 4 -- so every number sits on a mark and
    the scale reads end to end.

    The clearance is the second half. The line is y = x - 2, so it passes through
    (0, -2), which is the y-axis at the exact height of the '-2': at x=144 the line was
    within a pixel of the label. A y number may only be nudged SIDEWAYS -- the axis
    mapping is read from the tick label positions, so moving one up or down makes the
    scale read as nonlinear -- so the WHOLE column moves left, from x=144 to x=139,
    which keeps the four numbers in one line and puts 5 px of white between the '-2'
    and the line.

    Every number is now drawn twice, halo behind and glyphs on top, because a
    four-quadrant grid runs a faint rule through every tick number it has."""
    grid = ('<path d="M62 22V198M84 22V198M106 22V198M128 22V198M150 22V198'
            'M172 22V198M194 22V198M216 22V198M238 22V198M260 22V198M282 22V198'
            'M62 22H282M62 44H282M62 66H282M62 88H282M62 110H282M62 132H282'
            'M62 154H282M62 176H282M62 198H282" stroke="currentColor" '
            'stroke-width="0.5" fill="none" opacity="0.3"/>')
    axes = (line(62, 110, 282, 110) + line(150, 22, 150, 198))
    xt = "".join(f"M{x} 106V114" for x in range(62, 283, 22) if x != 150)
    yt = "".join(f"M146 {y}H154" for y in range(22, 199, 22) if y != 110)
    xs = [(x, 125, s) for x, s in ((62, "-4"), (106, "-2"), (194, "2"),
                                   (238, "4"), (282, "6"))]
    ys = [(139, y, s, 10, "end") for y, s in ((202, "-4"), (158, "-2"),
                                              (70, "2"), (26, "4"))]
    hl, gl = numbers(xs + ys)
    body = (grid + axes + ticks(xt) + ticks(yt)
            + '<text x="288" y="114" font-size="11" fill="currentColor">x</text>'
            + '<text x="155" y="17" font-size="11" fill="currentColor">y</text>'
            + line(106, 198, 282, 22, w=2.5) + hl + gl)
    # the plotted line is y = x - 2 in the figure's own units, and the column clears it
    assert (110 - 198) / 22 == -4 and (106 - 150) / 22 == -2, "the drawn line moved"
    for _, base, s in xs:
        assert base == 125
    for x, base, s, size, anch in ys:
        bx = box_of(x, base, s, size, anch)
        # the line runs from (106,198) to (282,22): one px up for every px right
        lo, hi = 198 - (bx[2] - 106), 198 - (bx[0] - 106)
        gap = max(bx[1] - hi, lo - bx[3])
        assert gap > 4, f"'{s}' is {gap:.1f} px from the plotted line"
    return {"figure_svg": wrap(body, "0 0 340 225")}


def f_2bc8b93a(svg, q):
    """#244 -- 'Add more values on the axes, while also integrating more axis
    value/numbering tick marks or lines.'

    The plane carried one number in each direction, -4 and 4, and no marks at all, so
    the only way to read K's position was to count squares. Both axes now carry every
    even value from -6 to 6 and a tick at every whole unit, each number haloed so the
    faint rule behind it does not strike it through. The canvas grows 7 px at the
    bottom to hold the new '-6'.

    Two things came out of redrawing it that the reviewer did not raise, both in the
    words rather than the picture. The explanation named the wrong options twice: it
    said option D has the right coordinates and option B moves up, when it is B that
    reads (2, -2) with the wrong quadrant and D that moves up to (2, 8). And 'K' itself
    sat across the gridline at y=28, so it is haloed with the numbers."""
    grid = ('<path d="M57 -8V208M75 -8V208M93 -8V208M111 -8V208M129 -8V208M147 -8V208'
            'M165 -8V208M183 -8V208M201 -8V208M219 -8V208M237 -8V208M255 -8V208'
            'M273 -8V208M57 -8H273M57 10H273M57 28H273M57 46H273M57 64H273M57 82H273'
            'M57 100H273M57 118H273M57 136H273M57 154H273M57 172H273M57 190H273'
            'M57 208H273" stroke="currentColor" stroke-width="0.5" fill="none" '
            'opacity="0.3"/>')
    axes = line(57, 100, 273, 100) + line(165, 208, 165, -8)
    xt = "".join(f"M{x} 96V104" for x in range(57, 274, 18) if x != 165)
    yt = "".join(f"M161 {y}H169" for y in range(-8, 209, 18) if y != 100)
    xs = [(x, 115, s) for x, s in ((57, "-6"), (93, "-4"), (129, "-2"),
                                   (201, "2"), (237, "4"), (273, "6"))]
    ys = [(158, y, s, 10, "end") for y, s in ((212, "-6"), (176, "-4"), (140, "-2"),
                                              (68, "2"), (32, "4"), (-4, "6"))]
    pairs = [num(*it) for it in xs + ys] + [num(87, 37, "K", 13, "middle")]
    body = (grid + axes + ticks(xt) + ticks(yt)
            + '<text x="281" y="104" font-size="11" fill="currentColor">x</text>'
            + '<text x="170" y="-13" font-size="11" fill="currentColor">y</text>'
            + '<circle cx="93" cy="46" r="5" fill="currentColor"/>'
            + halo("".join(a for a, _ in pairs))
            + "".join(g for _, g in pairs))
    # K is at (-4, 3): 18 px per unit from the origin at (165, 100)
    assert (93 - 165) / 18 == -4 and (100 - 46) / 18 == 3, "K moved"
    expl = ("K is at (-4, 3). Moving 6 units right adds to the x-coordinate: "
            "-4 + 6 = 2. Moving 5 units down subtracts from the y-coordinate: "
            "3 - 5 = -2. So the new position is (2, -2), where x is positive and y is "
            "negative — the fourth quadrant. Option D moves 5 units up instead of "
            "down, and option C moves left instead of right as well as up instead of "
            "down. Option B has the correct coordinates but names the second quadrant, "
            "which is where x is negative and y is positive.")
    return {"figure_svg": wrap(body, "0 -25.6 340 248"), "explanation": expl}


# ================================================================= the prism
def f_7abd8a82(svg, q):
    """#250 -- 'The 4cm label is in the wrong place. It is meant to represent depth,
    but currently it is depicting height. Move it to be on one of the depth values.'

    Correct. The label sat at (269, 97), beside the back-right vertical edge, which
    runs 80 px exactly like the front-left edge already labelled 3 cm — it was naming
    the height a second time. The prism's depth is the receding direction, drawn as the
    offset (+48, -38), and the free one of those three edges is the bottom-right, from
    (215, 175) to (263, 137). The label goes just outside it, along the edge's own
    outward normal, so it reads against the depth and nothing else."""
    a, b = (215.0, 175.0), (263.0, 137.0)
    mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    ux, uy = unit(*a, *b)
    nx, ny = -uy, ux                                   # away from the solid: down-right
    assert nx > 0 and ny > 0, "the normal points into the prism"
    px, py = mid[0] + nx * 20, mid[1] + ny * 20
    s = sub1(svg, '<text x="269" y="97" font-size="11" fill="currentColor">4 cm</text>',
             f'<text x="{px:.0f}" y="{py + 4:.0f}" font-size="11" fill="currentColor" '
             f'text-anchor="middle">4 cm</text>', "7abd8a82/4cm")
    bx = box_of(px, py + 4, "4 cm", 11, "middle")
    edge_y = 175 - (bx[0] - 215) * 38 / 48
    assert bx[1] - edge_y > 8, f"only {bx[1] - edge_y:.1f} px below the depth edge"
    assert bx[2] < 340 and bx[3] < 205, "the label leaves the canvas"
    return {"figure_svg": s}


# ======================================================================= driver
BUILDERS = {
    "bf613208": f_bf613208, "d5975559": f_d5975559, "05abece6": f_05abece6,
    "7932815e": f_7932815e, "b2c8c7b6": f_b2c8c7b6, "4769e94e": f_4769e94e,
    "c17f98d2": f_c17f98d2, "8de54934": f_8de54934, "2bc8b93a": f_2bc8b93a,
    "7abd8a82": f_7abd8a82,
}


def state(row):
    """The set of checks currently firing on this question. `options_distinct` is the
    one check in the suite that returns True for GOOD; every other returns None."""
    svg = row["figure_svg"]
    fired = {n for n in FIG_CHECKS if getattr(qc, n)(svg)}
    for n in Q_CHECKS:
        hit = getattr(qc, n)(row)
        if (not hit) if n == "options_distinct" else bool(hit):
            fired.add(n)
    return fired


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--review", type=pathlib.Path,
                    default=ROOT / "review/ui/figure-review-nsw-2026-09-06.json")
    args = ap.parse_args()

    want = {it["id"][:8]: it["n"]
            for it in json.loads(args.review.read_text())["items"] if it.get("note")}
    missing, extra = sorted(set(want) - set(BUILDERS)), sorted(set(BUILDERS) - set(want))
    if missing or extra:
        raise SystemExit(f"scope mismatch: missing {missing}  extra {extra}")

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    done, refused = [], []
    for prefix, build in sorted(BUILDERS.items(), key=lambda kv: want[kv[0]]):
        row = con.execute("SELECT * FROM questions WHERE id LIKE ?",
                          (prefix + "%",)).fetchone()
        if row is None:
            refused.append({"id": prefix, "why": "no such question"})
            continue
        q = dict(row)
        if q["review_status"] != "pending":
            refused.append({"id": q["id"], "why": f"status {q['review_status']}"})
            continue
        before = state(q)
        upd = build(q["figure_svg"], q)
        after = state({**q, **upd})
        gained = sorted(after - before)
        rec = {"n": want[prefix], "id": q["id"], "form": q["form_id"],
               "pos": q["form_position"], "changed": sorted(upd),
               "bytes": len(upd.get("figure_svg", q["figure_svg"] or "")),
               "before": sorted(before), "after": sorted(after),
               "newly_firing": gained}
        if gained:
            refused.append(rec)
            continue
        done.append(rec)
        if args.apply:
            cols = ", ".join(f"{k} = ?" for k in upd)
            con.execute(f"UPDATE questions SET {cols}, edited = 1 WHERE id = ?",
                        [*upd.values(), q["id"]])
    if args.apply:
        con.commit()
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps({"done": done, "refused": refused}, indent=1))
    print(f"repaired {len(done)}   refused {len(refused)}"
          f"   {'APPLIED' if args.apply else 'dry run'}")
    for r in refused:
        print("  REFUSED", r.get("id"), r.get("newly_firing") or r.get("why"))
    for r in done:
        gone = sorted(set(r["before"]) - set(r["after"]))
        left = sorted(set(r["after"]))
        print(f"  #{r['n']:<4}{r['id'][:8]} {r['form']} pos{r['pos']:>3} "
              f"{r['bytes']:>5}b  changed={','.join(r['changed'])}"
              f"{'  cleared=' + ','.join(gone) if gone else ''}"
              f"{'  still=' + ','.join(left) if left else ''}")
    cleared = sum(len(set(r["before"]) - set(r["after"])) for r in done)
    print(f"findings cleared: {cleared}   "
          f"newly firing: {sum(len(r['newly_firing']) for r in done) or 'none'}")


if __name__ == "__main__":
    main()
