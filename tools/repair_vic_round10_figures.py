#!/usr/bin/env python3
"""VIC round 10: the forty-six questions Alaan Q wrote a note against above card 113.

Round 9 sent a 223-card before/after page. The reviewer works through it a stretch at a
time and re-downloads the whole file each time, so the 2026-09-01 return holds 95
comments of which 49 are the round-9 notes repeated byte-for-byte. Those 49 are the
cards numbered 2 to 113 and they are already repaired. This file is the OTHER 46 -- the
cards numbered above 113. Nothing else on that page is touched: a card with no comment
was looked at and passed.

Most notes are placement again -- a number sitting on the line it names, a dot beside
the line it should be on, a grid that stops short of the point it should contain. Those
are done exactly as written.

Eleven are not placement, and each was worked twice by two different routes before
anything changed:

  3c6c07ee  a rectangle with a 6-9 corner cut: the perimeter is 45 + 3*sqrt(13) = 55.8,
            which is not among the options, and the explanation's own arithmetic says
            57.8 for the same expression. Re-cut to a 6-8-10 corner, perimeter 56
  33547c58  alpha drawn in the region ABOVE l1, which is exterior; co-interior needs it
            below l1 on the same side as beta
  f253343d  70 degrees marked on an obtuse sector, and "a" printed on the transversal
            marking no angle at all; the two lines were not parallel, so a + b = 180
            did not follow from anything
  93e6e231  W was not the foot of the perpendicular -- YW was drawn slanting -- and the
            right angle at Y was drawn at 78 degrees
  6559d286  a pie chart whose sectors do not match their own legend
  7ed5c9e5  a bar chart whose y-axis ticks are 0, 12, 20 at equal spacing
  c1930d7d  a "pie chart" drawn as a four-pointed star: every sector arc bulges inward
  7d94095a  a stem describing black and white L-shaped sections beside a plain black box
  64404632  the Collingwood bar drawn taller than the Carlton bar while labelled lower
  46c3108f  two congruent triangles where the question wants similar ones, so x could
            be read straight off the other triangle without any working
  3114e7d5  a cuboid net with four loose numbers and no edge named

Every figure is rendered and looked at before it is applied, and every question's full
check state is compared before and after: a question that would gain a finding is
refused rather than written.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_vic_round10_figures
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_vic_round10_figures --apply
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

from tools import question_checks as qc            # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
RECORD = ROOT / "run_data/output/vic_round10_figures.json"

FIG_CHECKS = ("doubled_circle_outline", "overlapping_text_labels",
              "plotted_points_inconsistent", "text_overlaps_geometry",
              "axes_unlabelled", "angle_arc_malformed", "axis_scale_nonlinear",
              "coordinate_figure_without_grid", "gridlines_off_the_ticks",
              "unknown_marker_far_from_point", "label_too_faint",
              "undefined_marker_reference", "text_outside_the_canvas",
              "gridlines_stop_short_of_the_axes", "axis_shorter_than_the_data",
              "angle_arc_misses_its_rays", "figure_svg_errors")
Q_CHECKS = ("angle_named_without_arc", "polygon_sides_disagree_with_stem",
            "figure_proportions_disagree", "plotted_geometry_matches_stem",
            "latex_markup_in_text", "options_distinct", "options_distinct_by_value",
            "leaked_working", "disputes_its_own_key", "rewrites_the_question",
            "no_question_asked", "one_point_on_the_line")


# ------------------------------------------------------------------ small helpers
def sub1(svg, old, new, who):
    """Exactly-once string replacement. Anything else is a bug in this file."""
    n = svg.count(old)
    if n != 1:
        raise AssertionError(f"{who}: expected 1 occurrence of {old!r}, found {n}")
    return svg.replace(old, new)


def subn(svg, old, new, times, who):
    """Replace an exact number of occurrences, all of them."""
    n = svg.count(old)
    if n != times:
        raise AssertionError(f"{who}: expected {times} of {old!r}, found {n}")
    return svg.replace(old, new)


def txt(x, y, s, size=13, anchor="middle", colour="currentColor", extra="",
        family="Arial,sans-serif"):
    a = f' text-anchor="{anchor}"' if anchor else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" '
            f'font-size="{size}" fill="{colour}"{a}{extra}>{s}</text>')


def line(x1, y1, x2, y2, w=2, dash=None, op=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' stroke-opacity="{op}"' if op else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="currentColor" stroke-width="{w}"{d}{o}/>')


def poly(pts, w=2, fill="none", fop=None, dash=None):
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    o = f' fill-opacity="{fop}"' if fop else ""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<polygon points="{p}" fill="{fill}"{o} stroke="currentColor" '
            f'stroke-width="{w}" stroke-linejoin="round"{d}/>')


def polyline(pts, w=1.6, dash=None):
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<polyline points="{p}" fill="none" stroke="currentColor" '
            f'stroke-width="{w}"{d}/>')


def wrap(body, vb):
    return (f'<svg viewBox="{vb}" xmlns="http://www.w3.org/2000/svg" '
            f'fill="none">{body}</svg>')


def arc(cx, cy, r, p_from, p_to, w=1.3):
    """Arc of radius r about (cx,cy), from the ray towards p_from to the ray towards
    p_to, taking the SHORT way round -- which is the angle a reader sees between the
    two rays. Sweep is derived, never guessed."""
    def ang(p):
        return math.degrees(math.atan2(p[1] - cy, p[0] - cx)) % 360.0
    a0, a1 = ang(p_from), ang(p_to)
    d = (a1 - a0) % 360.0
    sweep = 1 if d <= 180.0 else 0
    span = d if d <= 180.0 else 360.0 - d
    x0 = cx + r * math.cos(math.radians(a0))
    y0 = cy + r * math.sin(math.radians(a0))
    x1 = cx + r * math.cos(math.radians(a1))
    y1 = cy + r * math.sin(math.radians(a1))
    large = 1 if span > 180.0 else 0
    return (f'<path d="M{x0:.1f} {y0:.1f}A{r:.1f} {r:.1f} 0 {large} {sweep} '
            f'{x1:.1f} {y1:.1f}" fill="none" stroke="currentColor" '
            f'stroke-width="{w}"/>')


def unit(ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    n = math.hypot(dx, dy) or 1.0
    return dx / n, dy / n


def bisect_pt(v, a, b, r):
    """A point r from vertex v, along the bisector of the angle a-v-b."""
    ux, uy = unit(*v, *a)
    vx, vy = unit(*v, *b)
    bx, by = ux + vx, uy + vy
    n = math.hypot(bx, by) or 1.0
    return v[0] + bx / n * r, v[1] + by / n * r


def right_angle_mark(v, a, b, s=12.0):
    """An open square at v opening towards a and b. Two segments, so it never inks
    over the lines that define it."""
    ux, uy = unit(*v, *a)
    vx, vy = unit(*v, *b)
    p0 = (v[0] + ux * s, v[1] + uy * s)
    p2 = (v[0] + vx * s, v[1] + vy * s)
    p1 = (p0[0] + p2[0] - v[0], p0[1] + p2[1] - v[1])
    return polyline([p0, p1, p2], w=1.5)


def tick_mark(a, b, n=1, gap=5.0, half=6.0):
    """n equal-length hash marks across the midpoint of segment ab, PERPENDICULAR to
    it and piercing it -- half either side, which is what the convention means. A mark
    drawn at any other angle reads as a stray line, which is what the reviewer saw."""
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    ux, uy = unit(*a, *b)
    px, py = uy, -ux
    out = []
    for i in range(n):
        off = (i - (n - 1) / 2) * gap
        cx, cy = mx + ux * off, my + uy * off
        out.append(line(cx - px * half, cy - py * half,
                        cx + px * half, cy + py * half, w=1.6))
    return "".join(out)


def halo(body):
    """The page-coloured stroke layer that keeps a label readable over faint ink.

    It only counts as a halo where the checks look for it -- inside a group carrying
    aria-hidden -- and it only forgives FAINT ink underneath. A solid line through a
    label is still a finding, halo or no halo, so this is never a substitute for
    moving the label."""
    return (f'<g stroke="#fff" stroke-width="3" stroke-linejoin="round" '
            f'fill="none" aria-hidden="true">{body}</g>')


# ============================================================ plain label placement
def f_431d4c9b(svg, q):
    """#144 -- '5 cm' started at x=22 and runs about 28 px, so it printed across side
    CA at x=50. Start it further left."""
    return {"figure_svg": sub1(svg, '<text x="22" y="124"', '<text x="14" y="124"',
                               "431d4c9b")}


def f_ebd339c2(svg, q):
    """#163 -- '4 cm' started at x=135 and reached x=165, which is rectangle B's left
    side. Start it at 126."""
    return {"figure_svg": sub1(svg, '<text x="135" y="95" text-anchor="start"',
                               '<text x="126" y="95" text-anchor="start"', "ebd339c2")}


def f_0e77976c(svg, q):
    """#164 -- '11 cm' sat with its cap-line on the y=175 dimension rule. Drop it
    below the rule."""
    return {"figure_svg": sub1(svg, '<text x="148" y="185" text-anchor="middle"',
                               '<text x="148" y="191" text-anchor="middle"',
                               "0e77976c")}


def f_c5daaa49(svg, q):
    """#154 -- R's '5 cm' was drawn at (140, 48): past R's right side, above S, and
    close enough to S's left side to read as S's label. Put it beside R, level with
    R's middle."""
    return {"figure_svg": sub1(svg, '<text x="140" y="48" font-size="12"',
                               '<text x="134" y="69" font-size="12"', "c5daaa49")}


def f_3aa33936(svg, q):
    """#146 -- '24' ran from x=215 to x=229 and the circle passes through x=229.9 at
    that height, so the label touched the circumference.

    The label is only where it is because the rectangle is drawn 136 wide by 110 tall
    while its own labels say 10 by 24 -- so it is drawn WIDER than it is tall when it
    should be well over twice as tall as it is wide, and there is nowhere sensible to
    put '24'. Redrawn to its stated proportions at 6 px per cm: 60 by 144, with the
    circle through all four corners at r = 78 (the 10-24-26 diagonal, halved). Both
    labels then sit clear of everything."""
    body = (
        '<rect width="280" height="220" fill="none"/>'
        '<circle cx="140" cy="110" r="78" fill="none" stroke="currentColor" '
        'stroke-width="2"/>'
        '<rect x="110" y="38" width="60" height="144" fill="none" '
        'stroke="currentColor" stroke-width="2"/>'
        + txt(140, 24, "10", 13)
        + txt(176, 114, "24", 13, anchor="start"))
    return {"figure_svg": wrap(body, "0 0 280 220")}


def f_36544278(svg, q):
    """#141 -- the two '3' labels sat with their cap-line on the y=205 dimension rule.

    Redrawn rather than nudged, because the rule they sat on was itself wrong: it ran
    the whole width of the trapezium, 40 to 260, which measures 22 -- and it carried a
    '3' under each END, so it read as though the base were 3. The two 3s measure the
    two horizontal offsets, so they get a short rule each.

    The height is redrawn too. At 10 px per cm (the top 16 is 160 px, the offsets 3 are
    30 px) the height was drawn 160 px while its label says 8, so the figure showed a
    height of 16. It is 80 px now."""
    tri_l = [(40, 180), (70, 100), (70, 180)]
    tri_r = [(230, 100), (260, 180), (230, 180)]
    body = (
        '<rect width="300" height="230" fill="none"/>'
        + poly([(70, 100), (230, 100), (260, 180), (40, 180)])
        + poly(tri_l, fill="currentColor", fop=".18")
        + poly(tri_r, fill="currentColor", fop=".18")
        + '<rect x="70" y="100" width="160" height="80" fill="none" '
          'stroke="currentColor" stroke-width="2"/>'
        + right_angle_mark((70, 180), (70, 100), (230, 180), 14)
        + right_angle_mark((230, 180), (230, 100), (70, 180), 14)
        + txt(150, 92, "16", 13)
        + txt(150, 196, "22", 13)
        # height, with a rule of its own so '8' cannot be read as the sloping side
        + line(24, 100, 24, 180, w=1.2) + line(19, 100, 29, 100, w=1.2)
        + line(19, 180, 29, 180, w=1.2)
        + txt(12, 144, "8", 13)
        # the two offsets, each with its own short rule
        + line(40, 196, 70, 196, w=1.2) + line(40, 191, 40, 201, w=1.2)
        + line(70, 191, 70, 201, w=1.2)
        + line(230, 196, 260, 196, w=1.2) + line(230, 191, 230, 201, w=1.2)
        + line(260, 191, 260, 201, w=1.2)
        + txt(55, 214, "3", 12) + txt(245, 214, "3", 12))
    return {"figure_svg": wrap(body, "0 0 300 230")}


def f_d27c8f45(svg, q):
    """#157 -- the arc at P ran from the dashed altitude round to PQ, so it marked half
    of angle QPR while the label beside it says 40 degrees. Derived across BOTH rays.

    The right-angle square at the foot floated 4 px above QR; dropped onto the line."""
    s = sub1(svg, '<path d="M140.0 60.0A20.0 20.0 0 0 1 129.5 57.0" fill="none" '
                  'stroke="currentColor" stroke-width="1.3"/>',
             arc(140, 40, 24, (60, 170), (220, 170)), "d27c8f45-a")
    s = sub1(s, '<rect x="140" y="150" width="16" height="16"',
             '<rect x="140" y="154" width="16" height="16"', "d27c8f45-b")
    return {"figure_svg": s}


def f_82f15e67(svg, q):
    """#159 -- '3 cm' and '2 cm' were drawn at the TOP-right corner, with two dashed
    segments there, while the corner the polygon actually cuts is the BOTTOM-right one.
    The stem said top-right as well, so the words and the picture agreed with each
    other and neither agreed with the shape.

    The picture is the thing a student measures, so the picture is kept and the stem's
    one word is corrected. Redrawn at one scale, 26 px per cm: 8 by 5 becomes 208 by
    130, and the cut is 3 along the bottom by 2 up the right side -- it was drawn 1.45
    by 2.27 before."""
    body = (
        '<rect width="300" height="220" fill="none"/>'
        + poly([(40, 20), (248, 20), (248, 98), (170, 150), (40, 150)],
               fill="currentColor", fop=".18")
        + line(248, 98, 248, 150, w=1.5, dash="4,3")
        + line(248, 150, 170, 150, w=1.5, dash="4,3")
        + right_angle_mark((248, 150), (248, 98), (170, 150), 13)
        # width
        + line(40, 180, 248, 180, w=1.2) + line(40, 175, 40, 185, w=1.2)
        + line(248, 175, 248, 185, w=1.2)
        + txt(144, 195, "8 cm", 12)
        # height
        + line(30, 20, 30, 150, w=1.2) + line(25, 20, 35, 20, w=1.2)
        + line(25, 150, 35, 150, w=1.2)
        + txt(14, 89, "5 cm", 12)
        # the cut-away triangle's two legs
        + txt(209, 165, "3 cm", 11)
        + txt(254, 128, "2 cm", 11, anchor="start"))
    stem = q["stem"].replace("cut from the top-right corner",
                             "cut from the bottom-right corner")
    assert stem != q["stem"], "82f15e67: stem wording not found"
    return {"figure_svg": wrap(body, "0 0 300 220"), "stem": stem}


# ============================================================== coordinate planes
def f_0f936d02(svg, q):
    """#122 -- a stray '-1' printed in quadrant 4, between the y values -1 and -2.

    It is the x-axis label for -1, which the plane builder moved 30 px right and 46 px
    down, nowhere near the tick it names. Putting it back in the row was tried first and
    is not available: at (126, 101) it lands within a few pixels of the y-axis label
    '1', and it cannot be nudged clear either -- the x label positions are what the
    scale checks read the axis mapping from, so moving one sideways makes the axis
    read as nonlinear. Removed, as the reviewer asked. The x row then runs
    -5 -4 -3 -2 _ 1 2 3 4 5, evenly spaced, which is how a four-quadrant plane usually
    handles the tick next to the origin anyway."""
    return {"figure_svg": sub1(
        svg, '<text x="156" y="147" font-size="10" text-anchor="middle">−1</text>', '',
        "0f936d02")}


def f_42e248db(svg, q):
    """#192 -- the y-axis label '-5' printed across the y-axis itself.

    The plane builder pushed it 18 px right to dodge the plotted line, whose lower end
    stops exactly at (-1, -5), and 18 px right of the number column is the axis. There
    is no room left of the column either, so it goes to the other side of the axis at
    its own tick height -- the placement the reviewer asked for on the same fault in
    653b3f7f -- and gets the halo the moved copy never had."""
    s = sub1(svg, '<text x="90" y="266" font-size="10" text-anchor="end">−5</text>',
             '<text x="94" y="266" font-size="10" text-anchor="start">−5</text>',
             "42e248db-a")
    s = sub1(s, '<text x="72" y="242" font-size="10" text-anchor="end">−4</text>'
                '<text x="72" y="218"',
             '<text x="94" y="266" font-size="10" text-anchor="start">−5</text>'
             '<text x="72" y="242" font-size="10" text-anchor="end">−4</text>'
             '<text x="72" y="218"', "42e248db-b")
    return {"figure_svg": s}


def f_653b3f7f(svg, q):
    """#217 -- the same fault as 42e248db and the reviewer named the destination:
    '-5 ... should be moved to Quadrant 4's edge'. Done, with a halo."""
    s = sub1(svg, '<text x="114" y="266" font-size="10" text-anchor="end">−5</text>',
             '<text x="118" y="266" font-size="10" text-anchor="start">−5</text>',
             "653b3f7f-a")
    s = sub1(s, '<text x="96" y="242" font-size="10" text-anchor="end">−4</text>'
                '<text x="96" y="218"',
             '<text x="118" y="266" font-size="10" text-anchor="start">−5</text>'
             '<text x="96" y="242" font-size="10" text-anchor="end">−4</text>'
             '<text x="96" y="218"', "653b3f7f-b")
    return {"figure_svg": s}


def f_f488d2ef(svg, q):
    """#206 -- the y-axis value '4' sat under the plotted line.

    The line is segment AB, A(0, 4) to B(6, 4), and it was drawn from x = -1 to x = 7
    -- past both named endpoints and straight over the number column. Trimmed to A and
    B, which is what the stem describes; the '4' is then clear without moving."""
    return {"figure_svg": sub1(
        svg, '<line x1="38" y1="52" x2="278" y2="52"',
        '<line x1="68" y1="52" x2="248" y2="52"', "f488d2ef")}


def f_c0526d7f(svg, q):
    """#210 -- the y-axis value '1' sat under side AB.

    AB runs from x = -4 to x = 2 at exactly that height, so it covers the number column
    and every other spot at that height on the left of the axis: no sideways move
    clears it. It goes to the other side of the axis and just above the line, which is
    the only free spot beside its own tick."""
    return {"figure_svg": subn(
        svg, '<text x="179" y="176" font-size="10" text-anchor="end">1</text>',
        '<text x="196" y="166" font-size="10" text-anchor="start">1</text>', 1,
        "c0526d7f")}


def f_48f9e70a(svg, q):
    """#199 -- 'P' printed across the y-axis. Moved out from under it, to just below
    its own vertex, where nothing is drawn (the triangle is entirely above PQ). That
    spot is on the faint gridline through P's own column, so it is haloed, which is
    what the four-quadrant planes in this book do with every tick number."""
    lab = '<text x="90" y="172" font-size="13" text-anchor="middle">P</text>'
    return {"figure_svg": sub1(
        svg, '<text x="66" y="163" font-size="13" text-anchor="middle">P</text>',
        halo(lab) + lab, "48f9e70a")}


def f_c76f4d12(svg, q):
    """#204 -- 'E' reached the y-axis. Moved left, as asked; it cannot go far, because
    side EF runs down-left out of that vertex, but 9 px is enough to clear the axis."""
    lab = '<text x="138" y="103" font-size="13" text-anchor="middle">E</text>'
    return {"figure_svg": sub1(
        svg, '<text x="147" y="103" font-size="13" text-anchor="middle">E</text>',
        halo(lab) + lab, "c76f4d12")}


def f_7cc5d3c3(svg, q):
    """#211 -- 'N(2, 8)' reached back over the y-axis. Moved to the far side of its own
    point, below the line, where the whole label fits inside the canvas."""
    lab = '<text x="206" y="58" font-size="13" text-anchor="start">N(2, 8)</text>'
    s = sub1(svg,
             '<text x="178" y="29" font-size="13" text-anchor="middle">N(2, 8)</text>',
             halo(lab) + lab, "7cc5d3c3-a")
    # the y number -2 carries the same fault the reviewer raised on N: the plane
    # builder pushed it 18 px right of its column to dodge M's label, and 18 px right
    # of the column is the y-axis. It goes to the far side of the axis, as -5 does in
    # 42e248db and 653b3f7f.
    s = subn(s, '<text x="162" y="246" font-size="10" text-anchor="end">−2</text>',
             '<text x="166" y="246" font-size="10" text-anchor="start">−2</text>', 1,
             "7cc5d3c3-b")
    # The y number 4 grazes the plotted line by about 2 px, which is a second finding
    # in this figure and is NOT repaired: the line crosses the number column at that
    # height, so the only place to put it is the far side of the axis, and a second
    # number out of column would read worse than the graze does. Left as found.
    return {"figure_svg": s}


def f_6c2145b3(svg, q):
    """#218 -- '(0, 2)' was printed across the x-axis, five units below the point it
    names. Moved up beside the point, on the free side of both lines."""
    lab = '<text x="70" y="174" font-size="13" text-anchor="end">(0, 2)</text>'
    return {"figure_svg": sub1(
        svg, '<text x="108" y="229" font-size="13" text-anchor="middle">(0, 2)</text>',
        halo(lab) + lab, "6c2145b3")}


def f_965641b2(svg, q):
    """#222 -- 'R' sat on the diagonal, because the diagonal was drawn as a full line
    across the plane instead of the segment PR the question asks about. Trimmed to P
    and R; the label is then past its end.

    The y number column sat INSIDE the rectangle -- it is drawn to the right of the
    axis, and the rectangle spans x = 0 to 4 -- so the 3 was printed along the
    rectangle's top side, which is the same fault the reviewer raised on 7961f672.
    The column moves to the outside of the axis; every number keeps its own height."""
    s = sub1(svg, '<line x1="38" y1="183" x2="234" y2="36"',
             '<line x1="66" y1="162" x2="178" y2="78"', "965641b2-a")
    for yy in ("194", "138", "110", "82", "54", "26"):
        old = f'<text x="80" y="{yy}" font-size="10" text-anchor="start">'
        n = s.count(old)
        assert n in (1, 2), f"965641b2: y label {yy} appears {n} times"
        s = s.replace(old, f'<text x="60" y="{yy}" font-size="10" text-anchor="end">')
    # S's own letter was in the column's new lane; nudged up and left of its vertex
    s = sub1(s, '<text x="53" y="73" font-size="13" text-anchor="middle">S</text>',
             '<text x="48" y="68" font-size="13" text-anchor="middle">S</text>',
             "965641b2-c")
    return {"figure_svg": s}


def f_1238596a(svg, q):
    """#200 -- 'A' and 'B' both sat on the segment.

    Same cause as 965641b2: the stem says 'line segment AB has endpoints A(2, 1) and
    B(8, 9)' and the line was drawn from (0.5, -1) to (8.75, 10), through both labels
    and out the other side. Trimmed to A and B, which clears B; A is dropped below its
    own point, since the segment leaves that vertex going up and right."""
    s = sub1(svg, '<line x1="74" y1="286" x2="272" y2="22"',
             '<line x1="110" y1="238" x2="254" y2="46"', "1238596a-a")
    lab = '<text x="98" y="244" font-size="13" text-anchor="middle">A</text>'
    s = sub1(s, '<text x="121" y="230" font-size="13" text-anchor="middle">A</text>',
             halo(lab) + lab, "1238596a-b")
    return {"figure_svg": s}


def f_7961f672(svg, q):
    """#207 -- four tick numbers overlapped by the square's own sides: the y values 3
    and -2 lie on its top and bottom edges, the x values -1 and 4 on its left and right
    edges.

    Each can only move in one direction. A y number moved up or down, or an x number
    moved sideways, changes the spacing the scale checks read the axis mapping from,
    and the axis then reads as nonlinear -- so a y number may only go sideways and an x
    number only up or down. The square spans x -1 to 4 by y -2 to 3, so:

      * the whole y column goes out to the left of the square. Moving the two that
        clash alone would leave them 27 px adrift of the other five, and the column is
        just as readable outside the shape as inside it.
      * the two x numbers drop below the square's bottom corners, directly under their
        own ticks. The other five stay: they sit inside the shaded area but no edge
        runs through them, and the reviewer passed them.
    """
    ycols = ("236", "206", "176", "116", "86", "56", "26")
    s = svg
    for yy in ycols:
        old = f'<text x="89" y="{yy}" font-size="10"'
        n = s.count(old)
        assert n in (1, 2), f"7961f672: y label {yy} appears {n} times"
        s = s.replace(old, f'<text x="62" y="{yy}" font-size="10"')
    s = subn(s, '<text x="68" y="158" font-size="10" text-anchor="middle">−1</text>',
             '<text x="68" y="216" font-size="10" text-anchor="middle">−1</text>', 1,
             "7961f672-x1")
    s = subn(s, '<text x="218" y="158" font-size="10" text-anchor="middle">4</text>',
             '<text x="218" y="216" font-size="10" text-anchor="middle">4</text>', 1,
             "7961f672-x4")
    assert '<text x="89" y="157"' in s, "7961f672: the origin label O should not move"
    return {"figure_svg": s}


# ================================================================= marks and arcs
def f_a865cd26(svg, q):
    """#132 -- the equal-side mark on QR was drawn at the same slope as the other one,
    down and to the right, which on QR is very nearly ALONG the side. That is why it
    was almost invisible.

    Both marks are derived now: perpendicular to their own side and piercing it, half
    either side of the midpoint, which is what the convention means."""
    s = sub1(svg, '<line x1="88" y1="106" x2="98" y2="118" stroke="#1a1a2a" '
                  'stroke-width="2"/>',
             tick_mark((140, 30), (50, 190)).replace("currentColor", "#1a1a2a"),
             "a865cd26-a")
    s = sub1(s, '<line x1="182" y1="106" x2="192" y2="118" stroke="#1a1a2a" '
                'stroke-width="2"/>',
             tick_mark((140, 30), (230, 190)).replace("currentColor", "#1a1a2a"),
             "a865cd26-b")
    return {"figure_svg": s}


def f_26205798(svg, q):
    """#135 -- the q arc was a semicircle about (260, 180): a point sitting on the base
    line 30 px past the triangle's right vertex, belonging to no angle at all.

    Redrawn about the vertex itself, between the two rays that bound the exterior angle
    -- the base produced to the right, and the side up to the apex -- which is the
    mirror of the p arc on the left. Two malformed line elements go with it: they carry
    `x1='50,180'`, which is not a length, and each duplicates a well-formed line drawn
    immediately after it."""
    s = sub1(svg, '<line x1=\'50,180\' x2=\'10,180\' y1=\'180\' y2=\'180\' '
                  'stroke=\'currentColor\' stroke-width=\'2\'/>', "", "26205798-a")
    s = sub1(s, '<line x1=\'230,180\' x2=\'260,180\' y1=\'180\' y2=\'180\' '
                'stroke=\'currentColor\' stroke-width=\'2\'/>', "", "26205798-b")
    s = sub1(s, '<path d="M251.0 180.0A9.0 9.0 0 0 1 269.0 180.0" fill="none" '
                'stroke="currentColor" stroke-width="1.3"/>',
             arc(230, 180, 12, (265, 180), (140, 30)), "26205798-c")
    return {"figure_svg": s}


def f_b7056f8c(svg, q):
    """#142 -- a stray arrow beside P and a stray stub beside S: half of a dimension
    rule for the base that was never finished. Removed, as asked, and the arrowhead
    definition with them, since nothing else uses it."""
    s = sub1(svg, '<line x1="70" y1="238" x2="100" y2="238" stroke="currentColor" '
                  'stroke-width="1" marker-end="url(#arr)"/>', "", "b7056f8c-a")
    s = sub1(s, '<line x1="190" y1="238" x2="160" y2="238" stroke="currentColor" '
                'stroke-width="1"/>', "", "b7056f8c-b")
    s = sub1(s, '<defs><marker id="arr" markerWidth="7" markerHeight="7" refX="6" '
                'refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L7,3 '
                'L0,6 Z" fill="currentColor"/></marker></defs>', "", "b7056f8c-c")
    assert "url(#arr)" not in s, "b7056f8c: something still uses the arrowhead"
    return {"figure_svg": s}


def f_f2ce366f(svg, q):
    """#148 -- the grid stopped exactly where the two lines stop, so Car P's line ended
    in the corner of the grid with nothing beyond it. The rules run past the data now:
    the uprights reach 13 px above the top rule and the rules 13 px past the last
    upright. The two series labels move out of the way of the longer rules."""
    s = sub1(svg, '<path d="M95 58V190M145 58V190M195 58V190M245 58V190M45 58H245'
                  'M45 91H245M45 124H245M45 157H245"',
             '<path d="M95 45V190M145 45V190M195 45V190M245 45V190M45 58H258'
             'M45 91H258M45 124H258M45 157H258"', "f2ce366f-a")
    s = sub1(s, '<text x="248" y="55" font-size="11" fill="#2255cc">Car P</text>',
             '<text x="262" y="55" font-size="11" fill="#2255cc">Car P</text>',
             "f2ce366f-b")
    s = sub1(s, '<text x="248" y="68" font-size="11" fill="#cc2222">Car Q</text>',
             '<text x="262" y="68" font-size="11" fill="#cc2222">Car Q</text>',
             "f2ce366f-c")
    return {"figure_svg": s}


def f_81a45008(svg, q):
    """#166 -- a '6' floating in the middle of the square, naming nothing, and a second
    '6' inside the right-hand triangle, where every other triangle carries the slant
    height 5. The middle one goes; the other moves inside the square against its right
    side, where it names that side.

    Option C read '96 + 36 = 132 cm2' -- a sum with its own working shown, and the sum
    is of the right answer plus the base area. Written as the number it is."""
    s = sub1(svg, '<text x="130" y="124" text-anchor="middle" font-size="12" '
                  'fill="currentColor">6</text>', "", "81a45008-a")
    s = sub1(s, '<text x="174" y="124" font-size="11" fill="currentColor">6</text>',
             '<text x="154" y="124" text-anchor="end" font-size="11" '
             'fill="currentColor">6</text>', "81a45008-b")
    assert q["option_c"] == "96 + 36 = 132 cm²", f"81a45008: option C is {q['option_c']!r}"
    return {"figure_svg": s, "option_c": "132 cm²"}


def f_6e18fcef(svg, q):
    """#183 -- 'the letters A, B and C all look weird'. They are ordinary letters; the
    root <svg> carries fill="none" stroke="currentColor", which every <text> inherits,
    so all of them are drawn as hollow outlines rather than solid glyphs. At 12 px bold
    that reads as a strange double-struck font. Each text element paints itself now."""
    n = svg.count("<text ")
    assert n == 7, f"6e18fcef: {n} text elements, expected 7"
    s = svg.replace("<text ", '<text fill="currentColor" stroke="none" ')
    return {"figure_svg": s}


def sector(cx, cy, r, a0, a1, fop=".18"):
    """One pie slice, from screen angle a0 to a1 measured clockwise from 3 o'clock.

    The large-arc flag is DERIVED from the span. Both pie charts in this round were
    drawn with it hard-coded to 0 while the slice was wider than a semicircle, and a
    renderer given that combination draws the short way round instead -- which is how
    c1930d7d ended up as a four-pointed star with every arc bulging inwards."""
    def pt(a):
        return (cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
    x0, y0 = pt(a0)
    x1, y1 = pt(a1)
    large = 1 if (a1 - a0) % 360.0 > 180.0 else 0
    return (f'<path d="M{cx:.1f},{cy:.1f} L{x0:.1f},{y0:.1f} '
            f'A{r:.1f},{r:.1f} 0 {large} 1 {x1:.1f},{y1:.1f} Z" fill="currentColor" '
            f'fill-opacity="{fop}" stroke="currentColor" stroke-width="1.5"/>')


def _pie(cx, cy, r, slices, title, vb, label_r, size=10, title_y=210):
    """slices: [(a0, a1, [line, ...]), ...] with labels centred on the bisector."""
    body = []
    for a0, a1, lines in slices:
        body.append(sector(cx, cy, r, a0, a1))
    for a0, a1, lines in slices:
        mid = (a0 + (a1 - a0) % 360.0 / 2.0) % 360.0
        lx = cx + label_r * math.cos(math.radians(mid))
        ly = cy + label_r * math.sin(math.radians(mid))
        top = ly - (len(lines) - 1) * 6.0
        for i, s in enumerate(lines):
            body.append(txt(lx, top + i * 12.0, s, size))
    body.append(txt(140, title_y, title, 11, extra=' font-weight="bold"'))
    return wrap("".join(body), vb)


def f_6559d286(svg, q):
    """#136 -- 'angle C is meant to be in Angle A's location'.

    Measured: the four slices are drawn 120, 100, 50 and 90 degrees while their legend
    reads 120, 100, 90 and 50 -- so C and D are the wrong way round, and C is drawn as
    the SMALLEST slice when it is the one the question asks about. The labels are
    scattered too: 'A: 120' sits inside D's slice and 'C: 90' inside B's, so two of the
    four name a slice they are not in.

    Redrawn with each slice at its own angle and each label on its own slice's
    bisector, outside the circle where nothing can run through it."""
    return {"figure_svg": _pie(
        130, 106, 68,
        [(0, 120, ["A: 120°"]), (120, 220, ["B: 100°"]),
         (220, 310, ["C: 90°"]), (310, 360, ["D: 50°"])],
        "Streaming services (n=360)", "0 -6 280 226", 94)}


def f_c1930d7d(svg, q):
    """#150 -- 'the pie chart is inverted. It is not even in a circular shape.'

    Every slice was written to sweep clockwise while its own end point was one
    anticlockwise turn away, with the large-arc flag left at 0, so each arc was drawn
    the short way and bulged INWARDS: four concave slices meeting at the centre, which
    renders as a four-pointed star. Redrawn round the proper way at Walk 90, Bus 108,
    Train 72, Car 90 -- the four angles the legend states, which come to 360."""
    return {"figure_svg": _pie(
        130, 100, 70,
        [(0, 90, ["Walk", "90°"]), (90, 198, ["Bus", "108°"]),
         (198, 270, ["Train", "72°"]), (270, 360, ["Car", "90°"])],
        "Travel to school (n=300)", "0 0 280 220", 99, size=11)}


def f_b45f50b0(svg, q):
    """#174 -- 'the angle arc is slipping outside the line'.

    Same fault as the pie charts: the arc runs from OA round to OB the long way, 300
    degrees, with the large-arc flag left at 0, so it was drawn the short way and came
    out on the wrong side of both rays.

    Redrawing it showed the figure disagrees with the question as well. The stem puts
    OB at 125 degrees from OA -- 35 degrees PAST the vertical, which is the whole
    point -- and OB was drawn at 45 degrees, short of it. So the picture said the
    answer was 45 while the key says 35. OB is drawn at 125 degrees now, on the far
    side of the vertical, and the arc is derived between the two rays.

    The stem's 'using the protractor scale shown' goes with it: there is no protractor
    in the figure and never was. The angle is marked on the figure instead."""
    O, A, B = (150.0, 170.0), (280.0, 170.0), (64.0, 47.0)
    body = ('<rect width="300" height="200" fill="none"/>'
            + line(*O, *A)
            + line(*O, *B)
            + line(150, 175, 150, 32, w=1, dash="3,3")
            + '<polygon points="146,40 150,30 154,40" fill="currentColor"/>'
            + arc(O[0], O[1], 55, A, B, w=1.5)
            + txt(286, 174, "A", 12, anchor="start")
            + txt(56, 40, "B", 12, anchor="end")
            + txt(142, 188, "O", 12, anchor="end")
            + txt(183, 110, "125°", 11)
            + txt(150, 22, "vert", 10))
    stem = ("The figure below shows two rays meeting at point O. Ray OA is horizontal, "
            "and the angle AOB, measured from OA, is 125°. What is the acute angle "
            "between OB and the vertical?")
    return {"figure_svg": wrap(body, "0 0 300 200"), "stem": stem}


def f_6e95b3e1(svg, q):
    """#179 -- 'X overlaps with one of the sides and some of the lines pass out of the
    circle'. Both true: two of the four radii were drawn 86 and 87 px long inside a
    circle of radius 80, so they poked out through the rim, and X sat on the horizontal
    radius.

    Redrawing it showed worse. The four radii cut the disc into 156, 81, 33 and 90
    degrees, which is nothing like the probabilities the stem states, and two of the
    labels -- X and Y -- were inside the SAME slice, leaving the 33-degree one unnamed.
    Redrawn at the stem's own probabilities: W 0.45, X 0.15, Y 0.25, Z 0.15, so
    162, 54, 90 and 54 degrees, each letter on its own slice's bisector."""
    cx, cy, r = 140.0, 115.0, 78.0
    bounds = [(-90.0, 72.0, "W"), (72.0, 126.0, "X"),
              (126.0, 216.0, "Y"), (216.0, 270.0, "Z")]
    body = ['<rect width="280" height="220" fill="none"/>',
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="currentColor" '
            f'stroke-width="2"/>']
    for a0, _a1, _n in bounds:
        body.append(line(cx, cy, cx + r * math.cos(math.radians(a0)),
                         cy + r * math.sin(math.radians(a0))))
    for a0, a1, name in bounds:
        mid = a0 + (a1 - a0) / 2.0
        body.append(txt(cx + 50 * math.cos(math.radians(mid)),
                        cy + 50 * math.sin(math.radians(mid)) + 5, name, 14,
                        extra=' font-weight="bold"'))
    body.append(txt(140, 18, "Spinner", 12))
    return {"figure_svg": wrap("".join(body), "0 0 280 220")}


# =============================================================== charts and shapes
def f_b9928154(svg, q):
    """#123 -- 'there is an empty gap between y point 16 and the label Days'.

    The bars were plotted at 6 px per day against an axis 170 px tall, so the top of
    the scale sat 74 px below the top of the axis and nothing used that space. Redrawn
    at 9 px per day with wider bars: the 16 tick is now 10 px under the top of the
    axis and the tallest bar, April's 14, reaches most of the way up it. The readings
    are unchanged -- 8, 6, 10, 14, 12, 10, mean 10."""
    days = [("Jan", 8), ("Feb", 6), ("Mar", 10), ("Apr", 14), ("May", 12), ("Jun", 10)]
    base, per = 180.0, 9.0
    body = ['<rect width="300" height="220" fill="none"/>',
            line(45, 26, 45, 180, w=2), line(45, 180, 290, 180, w=2)]
    for v in (0, 4, 8, 12, 16):
        y = base - v * per
        body.append(line(43, y, 47, y, w=1))
        body.append(txt(38, y + 4, str(v), 9, anchor="end"))
    for i, (name, v) in enumerate(days):
        x = 55 + i * 40
        body.append(f'<rect x="{x}" y="{base - v * per:.0f}" width="34" '
                    f'height="{v * per:.0f}" fill="currentColor" stroke="currentColor" '
                    f'stroke-width="1" fill-opacity=".18"/>')
        body.append(txt(x + 17, 195, name, 10))
    body.append(txt(14, 22, "Days", 11, anchor="start"))
    body.append(txt(167, 213, "Month", 11))
    return {"figure_svg": wrap("".join(body), "-1.96 0 301.96 220")}


def f_2a58c697(svg, q):
    """#126 -- 'the Pies text should be enlargened to fill the emptiness to the left of
    the y-axis'. The strip is empty because the y-axis carries no scale at all: a bare
    rule with the values printed on top of the bars instead.

    It has one now -- 0, 10, 20, 30 -- with 'Pies' turned up the axis as a title, which
    is what fills that shape of space. Drawing the scale exposed the Q1 bar: it is 50 px
    tall where the other four are at 4 px per pie, so against a scale it reads 12.5
    while its own label says 15. It is 60 px now. The mean is unchanged at 22."""
    vals = [("Q1", 15), ("Q2", 25), ("Q3", 20), ("Q4", 30), ("Q5", 20)]
    base, per = 185.0, 4.0
    body = [line(45, 10, 45, 185, w=1.5), line(45, 185, 290, 185, w=1.5)]
    for v in (0, 10, 20, 30):
        y = base - v * per
        body.append(line(41, y, 45, y, w=1))
        body.append(txt(37, y + 4, str(v), 10, anchor="end"))
    for i, (name, v) in enumerate(vals):
        x = 55 + i * 50
        body.append(f'<rect x="{x}" y="{base - v * per:.0f}" width="34" '
                    f'height="{v * per:.0f}" fill="currentColor" stroke="currentColor" '
                    f'stroke-width="1" fill-opacity=".18"/>')
        body.append(txt(x + 12, 200, name, 11, anchor="start"))
        body.append(txt(x + 12, base - v * per - 4, str(v), 10, anchor="start"))
    body.append('<text x="8" y="100" font-family="Arial,sans-serif" font-size="13" '
                'fill="currentColor" text-anchor="middle" '
                'transform="rotate(-90 8 100)">Pies</text>')
    body.append(txt(140, 215, "Quarter", 11, anchor="start"))
    return {"figure_svg": wrap("".join(body), "-16 0 316 221")}


def f_ccb2dfba(svg, q):
    """#124 -- the angle name sat 40 px below the x-axis, outside the figure entirely.
    Moved onto the bisector of the angle it names, far enough out along it that the
    sector is wide enough to hold the text clear of both rays, with a halo so the grid
    behind it does not run through the letters."""
    lab = txt(131, 156, "∠BAx", 12, family="system-ui,sans-serif",
              extra=' fill-opacity=".9"')
    return {"figure_svg": sub1(
        svg, '<text x="94" y="213" font-family="system-ui,sans-serif" font-size="13" '
             'fill="currentColor" fill-opacity=".9" text-anchor="middle">∠BAx</text>',
        halo(lab) + lab, "ccb2dfba")}


def f_33547c58(svg, q):
    """#128 -- 'the black dots representing P and Q should be touching the transversal'.

    They were 11 px and 5 px off it. The transversal crosses l1 at (115.3, 70) and l2
    at (164.7, 140); the dots are there now.

    Redrawing them showed the alpha arc has the same fault the reviewer raised on
    f253343d: it is drawn from the transversal round to the RIGHT-hand ray of l1 over
    the top, marking the 125-degree angle ABOVE l1 -- which is an exterior angle, while
    the stem calls alpha co-interior with beta. Co-interior means both between the two
    lines and both on the same side of the transversal, so alpha is the acute angle
    below l1 on the right. Marked there, and beta -- named but never marked at all --
    gets the matching arc above l2 on the same side."""
    P, Q = (115.3, 70.0), (164.7, 140.0)
    s = sub1(svg, "<circle cx='104' cy='70' r='3' fill='currentColor'/>",
             f"<circle cx='{P[0]}' cy='{P[1]}' r='3' fill='currentColor'/>",
             "33547c58-a")
    s = sub1(s, "<circle cx='160' cy='140' r='3' fill='currentColor'/>",
             f"<circle cx='{Q[0]}' cy='{Q[1]}' r='3' fill='currentColor'/>",
             "33547c58-b")
    s = sub1(s, '<path d="M104.7 55.0A18.4 18.4 0 0 1 133.7 70.0" fill="none" '
                'stroke="currentColor" stroke-width="1.3"/>',
             arc(P[0], P[1], 26, (280, 70), (200, 190))
             + arc(Q[0], Q[1], 30, (280, 140), (80, 20)), "33547c58-c")
    s = sub1(s, "<text x=\"117.8\" y=\"36.6\" font-size='12' "
                "fill='currentColor'>α=47°</text>",
             txt(161, 94, "α=47°", 12, colour="currentColor"), "33547c58-d")
    s = sub1(s, "<text x='168' y='135' font-size='12' fill='currentColor'>β</text>",
             txt(204, 117, "β", 12, colour="currentColor"), "33547c58-e")
    return {"figure_svg": s}


def f_3c6c07ee(svg, q):
    """#127 -- '6 cm' overlapped the right side of the rectangle. Working out where it
    should go instead showed the question does not have an answer.

    A 12 by 18 rectangle with a right-angled corner cut off loses the two legs from its
    boundary and gains the hypotenuse: 2(12 + 18) - 6 - 9 + sqrt(6^2 + 9^2)
    = 45 + 3*sqrt(13) = 55.8 cm. The options are 57, 60, 63 and 66, and the explanation
    writes that same expression and then calls it 57.8. Checked a second way by walking
    the five sides of the resulting polygon -- 18 + 6 + sqrt(117) + 9 + 12 -- which is
    the same 55.82.

    Three of the four options were also unreachable on sight: cutting a corner always
    SHORTENS the boundary, because a hypotenuse is shorter than the two legs, so any
    answer of 60 or more is wrong without any arithmetic.

    Re-cut to a 6 by 8 corner, which gives a whole-number hypotenuse of 10 and a
    perimeter of 60 - 6 - 8 + 10 = 56, and the distractors are now the three mistakes
    a student actually makes: leaving the perimeter unchanged, dropping the legs
    without adding the hypotenuse, and adding the hypotenuse without dropping them.
    The figure is redrawn to scale at 11 px per cm with the removed corner dashed."""
    assert q["explanation"].endswith("≈ 57.8"), "3c6c07ee: explanation changed"
    body = ('<rect width="300" height="200" fill="none"/>'
            + poly([(46, 34), (156, 34), (244, 100), (244, 166), (46, 166)])
            + line(156, 34, 244, 34, w=1.5, dash="4,3")
            + line(244, 34, 244, 100, w=1.5, dash="4,3")
            + right_angle_mark((244, 34), (156, 34), (244, 100), 12)
            + line(46, 184, 244, 184, w=1.2) + line(46, 179, 46, 189, w=1.2)
            + line(244, 179, 244, 189, w=1.2)
            + txt(145, 198, "18 cm", 12)
            + line(32, 34, 32, 166, w=1.2) + line(27, 34, 37, 34, w=1.2)
            + line(27, 166, 37, 166, w=1.2)
            + txt(9, 104, "12 cm", 12)
            + txt(200, 26, "8 cm", 11)
            + txt(252, 71, "6 cm", 11, anchor="start"))
    stem = ("A rectangle with sides 12 cm and 18 cm has a right triangle cut from one "
            "corner. The two legs of the removed triangle are 6 cm and 8 cm. What is "
            "the perimeter of the resulting polygon?")
    expl = ("The rectangle's perimeter is 2(12 + 18) = 60 cm. Cutting the corner takes "
            "the two legs, 6 cm and 8 cm, off the boundary and puts the hypotenuse "
            "there instead. The hypotenuse is √(6² + 8²) = √100 = 10 cm. So the new "
            "perimeter is 60 − 6 − 8 + 10 = 56 cm.")
    return {"figure_svg": wrap(body, "-14 0 314 210"), "stem": stem,
            "explanation": expl, "option_a": "46 cm", "option_b": "60 cm",
            "option_c": "56 cm", "option_d": "70 cm", "correct_answer": "C"}


def f_f253343d(svg, q):
    """#129 -- 'the figure makes no sense as a whole ... the 70 degree angle
    mathematically can not be an obtuse angle as it is represented ... a doesn't even
    represent an angle location.'

    All true, and there was a third fault underneath them. The stem asks for a + b and
    keys 180, which only follows if the two crossing lines are PARALLEL -- and they
    were drawn converging, one leaning left and one leaning right, so a + b was not
    determined by anything in the figure. The 70 was marked on the obtuse sector, and
    'a' was printed on the transversal itself, 65 px from the nearest crossing.

    Redrawn: two parallel lines at 70 degrees to the transversal, with chevrons to say
    so. 70 marks the acute angle below the transversal at the left crossing; a is
    vertically opposite it, above the transversal on the right; b is the co-interior
    angle at the other crossing, above the transversal on the left. Each is derived
    between its own two rays, and a + b = 70 + 110 = 180."""
    T = 110.0                                     # the transversal
    c1, c2 = 110.0, 200.0                         # the two crossings
    dx = 85.0 / math.tan(math.radians(70.0))      # 70 degrees, over 85 px of rise
    up1, dn1 = (c1 + dx, T - 85), (c1 - 75 / 2.747, T + 75)
    up2, dn2 = (c2 + dx, T - 85), (c2 - 75 / 2.747, T + 75)

    def chevron(cx, cy):
        ux, uy = unit(cx, cy, cx + dx, cy - 85)
        px, py = uy, -ux
        return polyline([(cx - ux * 7 + px * 5, cy - uy * 7 + py * 5), (cx, cy),
                         (cx - ux * 7 - px * 5, cy - uy * 7 - py * 5)], w=1.5)
    body = ('<rect width="300" height="200" fill="none"/>'
            + line(20, T, 280, T)
            + line(*dn1, *up1) + line(*dn2, *up2)
            + chevron(c1 + dx * 0.7, T - 59.5) + chevron(c2 + dx * 0.7, T - 59.5)
            + arc(c1, T, 22, (20, T), dn1)          # 70, below-left at crossing 1
            + arc(c1, T, 30, (280, T), up1)         # a, above-right at crossing 1
            + arc(c2, T, 26, (20, T), up2)          # b, above-left at crossing 2
            + txt(77, 137, "70°", 13)
            + txt(143, 91, "a°", 13)
            + txt(176, 80, "b°", 13)
            + txt(148, 20, "ℓ₁", 12) + txt(238, 20, "ℓ₂", 12)
            + txt(288, 106, "t", 12))
    stem = ("In the figure below, the two lines ℓ₁ and ℓ₂ are parallel and are cut by "
            "the transversal t. What is the sum of angles a° and b°?")
    expl = ("At the left crossing, a° is vertically opposite the marked 70°, so "
            "a = 70. Because ℓ₁ and ℓ₂ are parallel, a° and b° are co-interior "
            "(allied) angles — they lie between the parallel lines on the same side of "
            "the transversal — so they are supplementary: b = 180 − 70 = 110. "
            "Therefore a + b = 70 + 110 = 180.")
    return {"figure_svg": wrap(body, "0 0 300 200"), "stem": stem, "explanation": expl}


def f_93e6e231(svg, q):
    """#130 -- 'two redundant squares above point W, as well as a useless perpendicular
    symbol'. Removing them left a figure that still did not describe the question, so
    it is redrawn from the stem's own numbers.

    W is defined as the foot of the perpendicular from Y to XZ, and YW was drawn
    slanting: W sat 35 px to the right of the point below Y. The right angle at Y was
    drawn at 78 degrees and marked nowhere; the two squares were both near W, one
    overlapping the other, and neither sat on a line.

    At 11 px per cm: XZ = 20 so 220 px, XY = 12 so YZ = 16, and W divides XZ at
    XY^2 / XZ = 7.2 cm with YW = 9.6 cm. Every one of those lengths is now what it is
    drawn as. 'XZ=20' moves out from under W and becomes '20 cm' beside the side it
    measures, with W's own letter directly under its point."""
    X, Z = (45.0, 180.0), (265.0, 180.0)
    W = (124.2, 180.0)
    Y = (124.2, 74.4)
    body = ('<rect width="300" height="220" fill="none"/>'
            + line(*X, *Z) + line(*X, *Y) + line(*Y, *Z)
            + line(*Y, *W, w=1.5, dash="5,3")
            + right_angle_mark(Y, X, Z, 14)
            + right_angle_mark(W, Y, Z, 12)
            + txt(36, 196, "X", 13) + txt(124, 66, "Y", 13) + txt(274, 196, "Z", 13)
            + txt(124, 196, "W", 13)
            + txt(66, 120, "12 cm", 12)
            + txt(180, 199, "20 cm", 12))
    return {"figure_svg": wrap(body, "0 0 300 220")}


def f_247238f5(svg, q):
    """#137 -- 'add more spacing between the top title, categories, and data sections.
    Also add horizontal lining/separation grids.' Redrawn with a rule under the header,
    a faint rule between each pair of rows, and the leaves spaced on a fixed pitch so
    they line up in columns.

    Reading the plot while laying it out caught the explanation. The plot holds nine
    values -- 22, 28, 34, 36, 36, 41, 45, 49, 53 -- and the median is the fifth, 36,
    which is the keyed answer. The stored explanation lists TEN different values that
    are in no row of the plot, and averages the middle two to 37.5, which is not one of
    the options. The figure and the key were right and only the working was wrong."""
    rows = [("2", ["2", "8"]), ("3", ["4", "6", "6"]),
            ("4", ["1", "5", "9"]), ("5", ["3"])]
    body = ['<rect width="280" height="210" fill="none"/>',
            txt(140, 22, "Rock Sample Masses (grams)", 13,
                extra=' font-weight="bold"'),
            txt(100, 52, "Stem", 11, anchor="end"),
            txt(122, 52, "Leaf", 11, anchor="start"),
            line(40, 60, 240, 60, w=1.2),
            line(110, 38, 110, 186, w=2)]
    for i, (stem_v, leaves) in enumerate(rows):
        y = 86 + i * 30
        body.append(txt(100, y, stem_v, 13, anchor="end"))
        for j, leaf in enumerate(leaves):
            body.append(txt(124 + j * 24, y, leaf, 13, anchor="start"))
        if i < len(rows) - 1:
            body.append(line(40, y + 10, 240, y + 10, w=1, op=".3"))
    expl = ("Reading the plot, the masses in order are 22, 28, 34, 36, 36, 41, 45, 49 "
            "and 53 grams. There are nine values, so the median is the fifth one: "
            "36 grams.")
    return {"figure_svg": wrap("".join(body), "0 0 280 210"), "explanation": expl}


def f_7ed5c9e5(svg, q):
    """#139 -- 'add a label on the y-axis ... ensure that the y-axis numbers are
    accurate (the number 20 is slightly under the bar that represents 20 medals)'.

    The reviewer read it exactly right. The bars are drawn at 5 px per medal, correctly,
    but the three y numbers were placed by hand at heights that work out at 17, 9 and 0
    -- so '20' sat 15 px below the top of the 20-medal bar. Redrawn with a tick every
    5 medals at the height the bars actually use, an axis that runs past the tallest
    bar, and 'Medals' up the axis. The readings are unchanged: 20, 18, 14, 12, 16."""
    states = [("NSW", 20), ("VIC", 18), ("QLD", 14), ("SA", 12), ("WA", 16)]
    base, per = 185.0, 5.0
    body = ['<rect width="300" height="220" fill="none"/>',
            line(40, 62, 40, 185, w=2), line(40, 185, 290, 185, w=2)]
    for v in (0, 5, 10, 15, 20):
        y = base - v * per
        body.append(line(36, y, 40, y, w=1))
        body.append(txt(32, y + 4, str(v), 10, anchor="end"))
    for i, (name, v) in enumerate(states):
        x = 55 + i * 48
        body.append(f'<rect x="{x}" y="{base - v * per:.0f}" width="32" '
                    f'height="{v * per:.0f}" fill="currentColor" stroke="currentColor" '
                    f'stroke-width="1" fill-opacity=".18"/>')
        body.append(txt(x + 16, 200, name, 11))
        body.append(txt(x + 16, base - v * per - 5, str(v), 11))
    body.append('<text x="10" y="124" font-family="Arial,sans-serif" font-size="11" '
                'fill="currentColor" text-anchor="middle" '
                'transform="rotate(-90 10 124)">Medals</text>')
    body.append(txt(165, 215, "State", 12))
    return {"figure_svg": wrap("".join(body), "0 0 300 221")}


def f_e89214af(svg, q):
    """#143 -- 'does 4 or 6 represent the height?'

    Because both were drawn as VERTICAL rules: 6 cm beside the front left edge and 4 cm
    beside a vertical rule at the right, so the figure showed two heights and no depth.
    The 4 cm rule now runs along the receding direction, parallel to the top-left edge
    that actually is the depth, so the three numbers lie on three different
    dimensions."""
    s = sub1(svg, '<line x1="246" y1="52" x2="246" y2="92" stroke="currentColor" '
                  'stroke-width="1"/>'
                  '<text x="254" y="76" font-size="12" text-anchor="start" '
                  'fill="currentColor">4 cm</text>',
             line(50.7, 80.7, 90.7, 40.7, w=1)
             + txt(58, 48, "4 cm", 12, anchor="end"), "e89214af")
    return {"figure_svg": s}


def f_7d94095a(svg, q):
    """#165 -- 'the question mentions a large rectangle divided into black and white
    L-shaped sections, but the rectangle shown is just a black box.'

    It was: a solid 150 by 120 rectangle, with a second rect element for the white part
    that carried fill='none' so it painted nothing, and a third that was written as a
    <rect> with x2/y2 attributes, which a rect does not have, so it drew nothing
    either.

    Redrawn at 40 px per cm as the L the stem describes -- 5 by 4 with a 3 by 2 corner
    taken out at the bottom right -- with the four lengths on the four edges they
    measure. The stem's own wording is corrected too: only the black region is
    L-shaped, and the white one is the rectangle the next sentence calls it."""
    body = ('<rect width="280" height="205" fill="none"/>'
            + poly([(50, 20), (250, 20), (250, 100), (130, 100), (130, 180), (50, 180)],
                   fill="currentColor")
            + '<rect x="50" y="20" width="200" height="160" fill="none" '
              'stroke="currentColor" stroke-width="2"/>'
            + txt(150, 196, "5 cm", 12)
            + txt(38, 104, "4 cm", 12, anchor="end")
            + txt(190, 172, "3 cm", 11)
            + txt(244, 144, "2 cm", 11, anchor="end"))
    stem = ("The figure below shows a large rectangle made up of a black L-shaped "
            "region and a white rectangular region. The total shape is 5 cm wide and "
            "4 cm tall. The white region is a rectangle 3 cm wide and 2 cm tall "
            "positioned in the bottom-right corner. What fraction of the total area "
            "is black?")
    return {"figure_svg": wrap(body, "0 0 280 205"), "stem": stem}


def f_64404632(svg, q):
    """#173 -- 'the Collingwood text is out of line and is overlapping with the x-axis
    label Football Club'. It had been dropped onto a second line to make room; at
    font 9 all four names fit on one line, so it goes back up with the others.

    Redrawing the bars found the reason the reviewer's eye went to this chart. The
    axis runs 1.4 px per pie, and the four bars were drawn 90, 70, 80 and 70 px tall
    against labels of 85, 70, 65 and 70 -- so COLLINGWOOD'S BAR WAS TALLER THAN
    CARLTON'S while its number was lower. They are 119, 98, 91 and 98 px now, which is
    what those four numbers are. The difference the question asks for is unchanged:
    155 against 135, so 20."""
    clubs = [("Richmond", 85, "#e8a040"), ("Carlton", 70, "#4a90d9"),
             ("Collingwood", 65, "#d94a4a"), ("Essendon", 70, "#4ad94a")]
    s = svg
    for i, (name, v, col) in enumerate(clubs):
        x = 55 + i * 55
        h = round(v * 1.4)
        old_y = {0: 85, 1: 105, 2: 95, 3: 105}[i]
        old_h = {0: 90, 1: 70, 2: 80, 3: 70}[i]
        s = sub1(s, f"<rect x='{x}' y='{old_y}' width='40' height='{old_h}' "
                    f"fill='{col}' stroke='#1a1a2a' stroke-width='1'/>",
                 f"<rect x='{x}' y='{175 - h}' width='40' height='{h}' "
                 f"fill='{col}' stroke='#1a1a2a' stroke-width='1'/>", f"64404632-b{i}")
        old_lab = {0: 80, 1: 100, 2: 90, 3: 100}[i]
        s = sub1(s, f"<text x='{x + 20}' y='{old_lab}' font-size='9' "
                    f"text-anchor='middle' font-family='Arial' "
                    f"fill='#1a1a2a'>{v}</text>",
                 f"<text x='{x + 20}' y='{175 - h - 5}' font-size='9' "
                 f"text-anchor='middle' font-family='Arial' "
                 f"fill='#1a1a2a'>{v}</text>", f"64404632-v{i}")
    s = sub1(s, "<text x='185' y='208' font-size='9'", "<text x='185' y='192' "
             "font-size='9'", "64404632-c")
    # and the axis stalk that ran 28 px above the 100 tick with nothing on it
    s = sub1(s, "<line x1='45' y1='10' x2='45' y2='175'",
             "<line x1='45' y1='30' x2='45' y2='175'", "64404632-d")
    return {"figure_svg": s}


def f_3a39fbb9(svg, q):
    """#172 -- 'there are thin grid lines present behind the actual grid in the same
    shape. Get rid of it because it overlaps with basically every number.'

    A faint grid drawn on a 40 px pitch starting at (45, 38), offset from the table's
    own cell borders, so every rule ran a few pixels off a number. The table draws its
    own borders, so the faint one is removed outright -- and an outer frame goes round
    the sixteen cells in its place, which a table wants anyway."""
    s = sub1(svg, '<path d="M45 38V198M85 38V198M125 38V198M165 38V198M205 38V198'
                  'M45 38H205M45 78H205M45 118H205M45 158H205M45 198H205" '
                  'stroke="currentColor" stroke-opacity=".16" stroke-width="1" '
                  'fill="none"/>',
             "<rect x='65' y='45' width='160' height='160' fill='none' "
             "stroke='currentColor' stroke-width='2'/>", "3a39fbb9")
    return {"figure_svg": s}


def f_26c0bfa3(svg, q):
    """#162 -- 'expand the grid and scaling lines to encompass point P. Enlargen the
    grid.' The grid covered x -2 to 2 and y -1 to 2 while P is at (2, 3), so the point
    sat outside it -- and the answer, P'(-3, 2), is outside it as well.

    P was plotted correctly, at 30 px per unit from the origin; only the grid and the
    numbers were short. Rebuilt by hand at the same 30 px per unit over x -4 to 4 and
    y -3 to 4, so both P and its image fall inside, with a tick and a number at every
    line. Not regenerated through figure_lib.plane: that moves a tick number to the far
    side of its axis wherever something crosses the tick row, which is the fault the
    reviewer raised on 0f936d02 in this same batch.

    Repeated rules go in one <path> each and the labels share one <g> for their font,
    because the figure has to stay under the 3.5 KB the check allows."""
    ox, oy, u = 140, 140, 30
    gx = [ox + v * u for v in range(-4, 5)]
    gy = [oy - v * u for v in range(-3, 5)]
    grid = ("".join(f"M{x} {gy[-1]}V{gy[0]}" for x in gx)
            + "".join(f"M{gx[0]} {y}H{gx[-1]}" for y in gy))
    ticks = ("".join(f"M{ox + v * u} {oy - 3}v6" for v in (-4, -3, -2, -1, 1, 2, 3, 4))
             + "".join(f"M{ox - 3} {oy - v * u}h6" for v in (4, 3, 2, 1, -1, -2, -3)))

    def t(x, y, txt_, anchor="middle", size=11, extra=""):
        return (f'<text x="{x}" y="{y}" font-size="{size}" '
                f'text-anchor="{anchor}"{extra}>{txt_}</text>')
    labs = "".join(
        t(ox + v * u, oy + 17, str(v).replace("-", "−")) for v in (-4, -3, -2, -1, 1, 2, 3, 4))
    labs += "".join(
        t(ox - 8, oy - v * u + 4, str(v).replace("-", "−"), "end")
        for v in (4, 3, 2, 1, -1, -2, -3))
    p_lab = t(ox + 2 * u + 9, oy - 3 * u - 6, "P (2, 3)", "start", 13,
              ' font-weight="bold"')
    body = (f'<path d="{grid}" stroke="currentColor" stroke-opacity=".16" '
            f'stroke-width="1"/>'
            f'<path d="M14 {oy}H272M{ox} 236V14" stroke="currentColor" '
            f'stroke-width="1.5"/>'
            f'<polygon points="272,{oy - 4} 280,{oy} 272,{oy + 4}" '
            f'fill="currentColor"/>'
            f'<polygon points="{ox - 4},14 {ox},6 {ox + 4},14" fill="currentColor"/>'
            f'<path d="{ticks}" stroke="currentColor" stroke-width="1"/>'
            f'<circle cx="{ox + 2 * u}" cy="{oy - 3 * u}" r="5" fill="currentColor"/>'
            f'<g font-family="Arial,sans-serif" fill="currentColor">'
            f'{halo(labs + p_lab)}{labs}{p_lab}'
            f'{t(288, oy + 4, "x", "middle", 13)}'
            f'{t(ox + 11, 16, "y", "start", 13)}</g>')
    return {"figure_svg": wrap(body, "0 0 300 260")}


def f_3114e7d5(svg, q):
    """#170 -- 'the locations of the numbers are unclear ... the 4 and 6 at the bottom
    are in random places.'

    They were. Two numbers sat below the net naming nothing, one text element was
    empty, a '5' was printed 5 px inside the edge of the face beside it, and the six
    faces did not even join up: the top and bottom flaps were drawn from x = 90 while
    the face between them runs from x = 80, so the net could not be folded.

    Redrawn to scale at 9 px per cm as the standard cross for a 6 by 5 by 4 cuboid --
    a band of four faces 6, 5, 6, 5 wide and 4 tall, with the 5-deep top and bottom
    faces above and below the first of them -- and one dimension rule per edge, so
    each of the three numbers names one edge and no number is loose."""
    s = 9.0
    L, W, H = 6.0, 5.0, 4.0
    x0, ytop, ymid, ybot = 40.0, 43.0, 88.0, 124.0
    faces = [(x0, ymid, L), (x0 + L * s, ymid, W),
             (x0 + (L + W) * s, ymid, L), (x0 + (2 * L + W) * s, ymid, W)]
    body = ['<rect width="300" height="200" fill="none"/>']
    for fx, fy, fw in faces:
        body.append(f'<rect x="{fx:.0f}" y="{fy:.0f}" width="{fw * s:.0f}" '
                    f'height="{H * s:.0f}" fill="none" stroke="currentColor" '
                    f'stroke-width="2"/>')
    for fy in (ytop, ybot):
        body.append(f'<rect x="{x0:.0f}" y="{fy:.0f}" width="{L * s:.0f}" '
                    f'height="{W * s:.0f}" fill="none" stroke="currentColor" '
                    f'stroke-width="2"/>')
    body += [line(x0, 30, x0 + L * s, 30, w=1.2), line(x0, 25, x0, 35, w=1.2),
             line(x0 + L * s, 25, x0 + L * s, 35, w=1.2),
             txt(x0 + L * s / 2, 21, "6 cm", 12),
             line(32, ytop, 32, ymid, w=1.2), line(27, ytop, 37, ytop, w=1.2),
             line(27, ymid, 37, ymid, w=1.2),
             txt(24, (ytop + ymid) / 2 + 4, "5 cm", 12, anchor="end"),
             line(32, ymid, 32, ybot, w=1.2), line(27, ybot, 37, ybot, w=1.2),
             txt(24, (ymid + ybot) / 2 + 4, "4 cm", 12, anchor="end")]
    return {"figure_svg": wrap("".join(body), "-4 0 304 200")}


def f_46c3108f(svg, q):
    """#186 -- 'this question should be deleted. it is too obvious. Try scaling up the
    second triangle and make them similar so the student has to do some sort of working
    out.'

    The reviewer is right about why it is too obvious: both triangles were drawn the
    same size with the same two numbers, and the FIRST one had 15 cm printed on the
    very side the second one calls x. A student reads the answer straight across
    without doing anything.

    Re-cut as the reviewer suggests. The second triangle is now the first one doubled
    -- 16, 30, 34 against 8, 15, 17 -- and drawn twice the size, so x has to be found,
    either from the scale factor 34 / 17 = 2 or by Pythagoras on the larger triangle.
    Both routes were worked: 15 x 2 = 30, and sqrt(34^2 - 16^2) = sqrt(900) = 30.

    The distractors are the three things that actually go wrong: reading the matching
    side off the small triangle without scaling (15), turning the scale factor upside
    down (7.5), and adding the difference of the hypotenuses instead of multiplying
    (32). The congruence wording goes with the change -- these triangles are similar,
    not congruent."""
    def tri(rx, ry, w, h):
        return (poly([(rx, ry), (rx + w, ry), (rx, ry - h)])
                + right_angle_mark((rx, ry), (rx + w, ry), (rx, ry - h), 11))
    body = ('<rect width="344" height="185" fill="none"/>'
            + tri(36, 150, 67.5, 36)
            + txt(70, 168, "15 cm", 12)
            + txt(30, 136, "8 cm", 12, anchor="end")
            + txt(88, 112, "17 cm", 12, anchor="start")
            + tri(180, 150, 135, 72)
            + txt(247, 168, "x", 12)
            + txt(174, 118, "16 cm", 12, anchor="end")
            + txt(272, 101, "34 cm", 12, anchor="start"))
    stem = "The two right-angled triangles shown are similar. What is the value of x?"
    expl = ("The triangles are similar, so their matching sides are in the same ratio. "
            "The hypotenuses are 17 cm and 34 cm, so the scale factor is 34 ÷ 17 = 2. "
            "The side marked x matches the 15 cm side of the smaller triangle, so "
            "x = 15 × 2 = 30 cm. Pythagoras on the larger triangle gives the same "
            "answer: √(34² − 16²) = √(1156 − 256) = √900 = 30. Reading 15 cm straight "
            "off the smaller triangle forgets the scaling; 7.5 cm turns the scale "
            "factor upside down; 32 cm adds the difference of the hypotenuses, "
            "15 + 17, instead of doubling.")
    return {"figure_svg": wrap(body, "0 0 344 185"), "stem": stem, "explanation": expl,
            "option_a": "15 cm", "option_b": "7.5 cm", "option_c": "30 cm",
            "option_d": "32 cm", "correct_answer": "C"}


# ======================================================================= driver
BUILDERS = {
    "0f936d02": f_0f936d02, "1238596a": f_1238596a, "247238f5": f_247238f5,
    "26205798": f_26205798, "26c0bfa3": f_26c0bfa3, "2a58c697": f_2a58c697,
    "3114e7d5": f_3114e7d5, "33547c58": f_33547c58, "36544278": f_36544278,
    "3a39fbb9": f_3a39fbb9, "3aa33936": f_3aa33936, "3c6c07ee": f_3c6c07ee,
    "42e248db": f_42e248db, "431d4c9b": f_431d4c9b, "46c3108f": f_46c3108f,
    "48f9e70a": f_48f9e70a, "6559d286": f_6559d286, "64404632": f_64404632,
    "653b3f7f": f_653b3f7f, "6c2145b3": f_6c2145b3, "6e18fcef": f_6e18fcef,
    "6e95b3e1": f_6e95b3e1, "7961f672": f_7961f672, "7cc5d3c3": f_7cc5d3c3,
    "7d94095a": f_7d94095a, "7ed5c9e5": f_7ed5c9e5, "81a45008": f_81a45008,
    "82f15e67": f_82f15e67, "93e6e231": f_93e6e231, "965641b2": f_965641b2,
    "a865cd26": f_a865cd26, "b45f50b0": f_b45f50b0, "b7056f8c": f_b7056f8c,
    "b9928154": f_b9928154, "c0526d7f": f_c0526d7f, "c1930d7d": f_c1930d7d,
    "c5daaa49": f_c5daaa49, "c76f4d12": f_c76f4d12, "ccb2dfba": f_ccb2dfba,
    "d27c8f45": f_d27c8f45, "e89214af": f_e89214af, "ebd339c2": f_ebd339c2,
    "f253343d": f_f253343d, "f2ce366f": f_f2ce366f, "f488d2ef": f_f488d2ef,
    "0e77976c": f_0e77976c,
}


def state(row):
    """The set of checks currently firing on this question.

    `options_distinct` is the one check in the suite that returns True for GOOD; every
    other returns None for good and a message for a finding. Reading it the same way as
    the rest makes every question look like it is failing it."""
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
                    default=ROOT / "review/ui/figure-review-vic-mq-recheck-"
                                   "2026-09-01.json")
    args = ap.parse_args()

    # the round is exactly the cards numbered above 113 in the reviewer's file
    want = {}
    for it in json.loads(args.review.read_text())["items"]:
        if it["n"] > 113:
            want[it["id"][:8]] = it["n"]
    missing = sorted(set(want) - set(BUILDERS))
    extra = sorted(set(BUILDERS) - set(want))
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
        after_row = {**q, **upd}
        after = state(after_row)
        gained = sorted(after - before)
        rec = {"n": want[prefix], "id": q["id"], "form": q["form_id"],
               "pos": q["form_position"], "changed": sorted(upd),
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
        print(f"  #{r['n']:<4}{r['id'][:8]} {r['form']} pos{r['pos']:>3}  "
              f"changed={','.join(r['changed'])}"
              f"{'  cleared=' + ','.join(gone) if gone else ''}"
              f"{'  still=' + ','.join(left) if left else ''}")
    cleared = sum(len(set(r["before"]) - set(r["after"])) for r in done)
    gained = sum(len(r["newly_firing"]) for r in done)
    print(f"findings cleared: {cleared}   newly firing: {gained or 'none'}")


if __name__ == "__main__":
    main()
