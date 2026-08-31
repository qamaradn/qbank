#!/usr/bin/env python3
"""VIC round 9: the forty-nine questions Alaan Q wrote a note against.

Round 8 sent a before/after page of 223 figures. The reviewer worked through the first
223 cards and left a written comment on forty-nine of them -- thirty-one that round 8
had already redrawn and eighteen that nothing had touched yet. Everything else on that
page was looked at and left alone, so nothing else is repaired here.

Most notes are placement: a number sitting on the line it names, an angle number outside
the sector it belongs to, a right-angle square on the wrong side of a vertex, a grid that
stops short of its axis. Those are done exactly as written.

Nine are not placement at all, and each was worked twice by two different routes before
anything changed:

  0096a667  a rectilinear perimeter whose bottom edge was labelled 8 when the shape only
            closes at 7; the perimeter is 38, not the keyed 46
  23bfa545  a trapezoid whose marked angles forced it to be a parallelogram; angle CDE
            is 70, not the keyed 40
  e75376a3  two options that are the same line written differently
  63e9b382  an inscribed circle drawn too small to touch anything
  7c325b26  a stem that named the wrong pair of parallel sides; angle BDC is 40
  f17a9331  a triangle drawn off the lattice, so its area could not be read
  a30aed4e  the answer printed on the graph as a labelled point
  d3c74fcc  a cut-out drawn 6 wide where the working says 4
  b86b2e3c  a point C defined as lying on both diameters -- that is the centre -- and an
            option naming a point D that is not in the figure
  ccac7c88  an explanation using five numbers that are not the five in the chart
  f0ab0510  a graph of a straight line through the origin at 20 km/h, keyed 25
  7edd1fff  an explanation that used adjacent angles where the parallelogram needs
            opposite ones

Every figure is rendered and looked at before it is applied, and every question's full
check state is compared before and after: a question that would gain a finding is
refused rather than written.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_vic_round9_figures
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_vic_round9_figures --apply
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

from tools import figure_lib as fl                 # noqa: E402
from tools import question_checks as qc            # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
RECORD = ROOT / "run_data/output/vic_round9_figures.json"

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


def txt(x, y, s, size=13, anchor="middle", colour="currentColor", extra=""):
    a = f' text-anchor="{anchor}"' if anchor else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Arial,sans-serif" '
            f'font-size="{size}" fill="{colour}"{a}{extra}>{s}</text>')


def line(x1, y1, x2, y2, w=2, dash=None, op=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' stroke-opacity="{op}"' if op else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="currentColor" stroke-width="{w}"{d}{o}/>')


def poly(pts, w=2, fill="none", fop=None, dash=None):
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    f = f'{fill}' if fill == "none" else fill
    o = f' fill-opacity="{fop}"' if fop else ""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<polygon points="{p}" fill="{f}"{o} stroke="currentColor" '
            f'stroke-width="{w}" stroke-linejoin="round"{d}/>')


def polyline(pts, w=1.4, dash=None):
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<polyline points="{p}" fill="none" stroke="currentColor" '
            f'stroke-width="{w}"{d}/>')


def wrap(body, vb):
    return (f"<svg viewBox=\"{vb}\" xmlns='http://www.w3.org/2000/svg' "
            f"fill='none'>{body}</svg>")


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
    return polyline([p0, p1, p2])


def tick_mark(a, b, n=1, gap=5.0, half=6.0):
    """n equal-length hash marks across the midpoint of segment ab, perpendicular to
    it and PIERCING it -- half either side, which is what the convention means."""
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


# ================================================================= surgical edits
def f_4653b226(svg, q):
    """#6 -- the y-axis label '10' sits 18 px right of the column, on the axis itself.
    Every other tick label is right-aligned at x=24; a collision nudge had pushed this
    one out. Put it back in the column."""
    s = sub1(svg, '<text x="42" y="38"', '<text x="24" y="38"', "4653b226-a")
    # ...which then put it on the rotated axis title, because that title is drawn
    # inside the number column. Slide the title left and widen the canvas to hold it.
    s = sub1(s, '<text x="12" y="84" font-family="system-ui,sans-serif" '
                'font-size="12" fill="currentColor" text-anchor="middle" '
                'transform="rotate(-90 12 84)">Number of students</text>',
             '<text x="4" y="84" font-family="system-ui,sans-serif" '
             'font-size="12" fill="currentColor" text-anchor="middle" '
             'transform="rotate(-90 4 84)">Number of students</text>', "4653b226-b")
    s = sub1(s, 'viewBox="-2.49 0 362.49 204"', 'viewBox="-8 0 368 204"',
             "4653b226-c")
    return {"figure_svg": s}


def f_660a2278(svg, q):
    """#79 -- same fault: the '20' tick label was nudged from x=8 to x=26, on top of
    the rotated 'Students' axis label. Back into the column."""
    s = sub1(svg, "<text x='26' y='99'", "<text x='8' y='99'", "660a2278-a")
    # Same second fault as 4653b226: the rotated 'Students' title is drawn in the
    # number column, so a two-digit label at its height lands on it.
    s = sub1(s, "<text x='20' y='116' font-size='11' text-anchor='middle' "
                "fill='#1a1a2a' transform='rotate(-90,20,100)'>Students</text>",
             "<text x='2' y='100' font-size='11' text-anchor='middle' "
             "fill='#1a1a2a' transform='rotate(-90,2,100)'>Students</text>",
             "660a2278-b")
    s = sub1(s, "viewBox='0 0 300 220'", "viewBox='-10 0 310 220'", "660a2278-c")
    # the white backing rect is geometry too: its left edge ran through the title's
    # new position, so it grows with the canvas
    s = sub1(s, "<rect width='300' height='220' fill='white'/>",
             "<rect x='-10' y='0' width='320' height='220' fill='white'/>",
             "660a2278-d")
    return {"figure_svg": s}


def f_b2e0b69d(svg, q):
    """#36 -- two right-angle marks at the same corner. Keep the L-shaped one, which is
    the smaller and the conventional form, and drop the 20x20 box that crowds the alpha."""
    return {"figure_svg": sub1(
        svg,
        "<rect x='40' y='150' width='20' height='20' fill='none' "
        "stroke='currentColor' stroke-width='1.5'/>", "", "b2e0b69d")}


def f_bed54cfb(svg, q):
    """#82 -- the right-angle square floated 6 px above the chord it belongs on. Drop it
    so its lower edge lies along AB."""
    return {"figure_svg": sub1(svg, "<rect x='140' y='148' width='14' height='14'",
                               "<rect x='140' y='154' width='14' height='14'",
                               "bed54cfb")}


def f_1a87560f(svg, q):
    """#24 -- '7 cm' was printed across the left side of the parallelogram. It labels the
    dashed perpendicular height, so it goes beside that line, inside the shape where
    nothing is drawn."""
    return {"figure_svg": sub1(
        svg, "<text x='40' y='100' font-size='14' fill='currentColor' "
             "font-family='Arial'>7 cm</text>",
        "<text x='96' y='99' font-size='14' fill='currentColor' "
        "font-family='Arial'>7 cm</text>", "1a87560f")}


def f_b03c10bc(svg, q):
    """#30 -- the side was labelled '12?', a stray marker. It reads '12 cm'. Right-align
    it so the longer text does not run into the side it names."""
    return {"figure_svg": sub1(
        svg, "<text x='15' y='105' font-size='12' fill='currentColor'>12?</text>",
        "<text x='36' y='105' text-anchor='end' font-size='12' "
        "fill='currentColor'>12 cm</text>", "b03c10bc")}


def f_58e9df0d(svg, q):
    """#35 -- '34 degrees' lay along PR. Widen the arc and move the number out along the
    bisector until the hypotenuse clears the top of its box."""
    s = sub1(svg, "<text x='55' y='158' font-size='13' fill='currentColor'>34°</text>",
             txt(86, 153, "34°", 13), "58e9df0d-a")
    s = sub1(s, '<path d="M50.2 152.3A23.9 23.9 0 0 1 53.9 165.0" fill="none" '
                'stroke="currentColor" stroke-width="1.3"/>',
             arc(30, 165, 30, (220, 45), (220, 165)), "58e9df0d-b")
    return {"figure_svg": s}


def f_0896c838(svg, q):
    """#40 -- '52 degrees' was about to touch AC. Same treatment as 58e9df0d."""
    s = sub1(svg, "<text x='48' y='168' font-size='13' fill='currentColor'>52°</text>",
             txt(84, 159, "52°", 13), "0896c838-a")
    s = sub1(s, '<path d="M43.3 161.2A23.0 23.0 0 0 1 48.0 175.0" fill="none" '
                'stroke="currentColor" stroke-width="1.3"/>',
             arc(25, 175, 32, (210, 35), (210, 175)), "0896c838-b")
    return {"figure_svg": s}


def f_a723bb91(svg, q):
    """#41 -- theta sat outside the triangle with nothing marking it. tan(theta)=5/12
    puts it at the vertex where the side of 12 meets the hypotenuse, so it goes inside
    that vertex with an arc across the two rays."""
    v = (200.0, 160.0)
    p = bisect_pt(v, (40, 160), (40, 40), 42)
    s = sub1(svg, "<text x='185' y='141' font-size='13' fill='currentColor' "
                  "font-family='Arial'>θ</text>",
             txt(p[0], p[1] + 4, "θ", 13), "a723bb91-a")
    s = s.replace("</svg>", arc(v[0], v[1], 26, (40, 160), (40, 40)) + "</svg>")
    return {"figure_svg": s}


def f_d4914353(svg, q):
    """#42(96) -- a right-angle square in the middle of the fan of rays, where no angle
    is 90. Redrawn from the stem's own numbers: PQR = 110, PQS = 2x+20, SQR = 90-2x, and
    QT bisecting SQR. The old QT lay between QP and QS, so it bisected nothing."""
    Q = (130.0, 170.0)

    def ray(deg, ln):
        return (Q[0] + ln * math.cos(math.radians(deg)),
                Q[1] - ln * math.sin(math.radians(deg)))
    R, P, S, T = ray(0, 120), ray(110, 130), ray(50, 130), ray(25, 115)
    body = [line(*Q, *R), line(*Q, *P), line(*Q, *S),
            line(*Q, *T, w=1.5, dash="5,3"),
            txt(P[0] - 6, P[1] - 4, "P", 13, "end"),
            txt(S[0] + 6, S[1] - 4, "S", 13, "start"),
            txt(T[0] + 7, T[1] - 3, "T", 13, "start"),
            txt(R[0] + 6, R[1] + 5, "R", 13, "start"),
            txt(Q[0] - 5, Q[1] + 17, "Q", 13, "end")]
    return {"figure_svg": wrap("".join(body), "0 0 280 200")}


def f_791cf236(svg, q):
    """#59 -- the equal-side hashes sat mostly outside the triangle. A hash mark crosses
    the side it marks, half either way."""
    s = sub1(svg, '<line x1="101" y1="103" x2="109" y2="106" stroke="currentColor" '
                  'stroke-width="1.5"/>',
             tick_mark((140, 25), (76, 185)), "791cf236-a")
    s = sub1(s, '<line x1="179" y1="103" x2="171" y2="106" stroke="currentColor" '
                'stroke-width="1.5"/>',
             tick_mark((140, 25), (204, 185)), "791cf236-b")
    return {"figure_svg": s}


def f_13720600(svg, q):
    """#66 -- same fault, same fix."""
    s = sub1(svg, '<line x1="90" y1="105" x2="98" y2="107" stroke="currentColor" '
                  'stroke-width="1.5"/>',
             tick_mark((140, 25), (55, 185)), "13720600-a")
    s = sub1(s, '<line x1="190" y1="105" x2="182" y2="107" stroke="currentColor" '
                'stroke-width="1.5"/>',
             tick_mark((140, 25), (225, 185)), "13720600-b")
    return {"figure_svg": s}


def f_b0646282(svg, q):
    """#101 -- the equal-side marks were drawn as two-stroke bent arrowheads. They are
    single dashes across the side."""
    s = sub1(svg, "<line x1='80' y1='100' x2='95' y2='93' stroke='#1a1a2a' "
                  "stroke-width='1.5'/><line x1='80' y1='100' x2='88' y2='113' "
                  "stroke='#1a1a2a' stroke-width='1.5'/>",
             tick_mark((140, 30), (40, 190)), "b0646282-a")
    s = sub1(s, "<line x1='200' y1='100' x2='185' y2='93' stroke='#1a1a2a' "
                "stroke-width='1.5'/><line x1='200' y1='100' x2='192' y2='113' "
                "stroke='#1a1a2a' stroke-width='1.5'/>",
             tick_mark((140, 30), (240, 190)), "b0646282-b")
    return {"figure_svg": s}


def f_81afb3a7(svg, q):
    """#113 -- a stray line. `<line x1='72,76' y1='76' x2='208,76'>` has a comma in its
    x, no y2 at all, and is immediately followed by the same line written properly, so
    the browser drew a second line from (72,76) to (208,0). Removing it also showed PQ
    running well past both sides of the triangle and sitting at AP/AB = 0.31 when the
    stem says 3/12; PQ is placed from the mapping now."""
    s = sub1(svg, "<line x1='72,76' y1='76' x2='208,76' stroke='#1a1a2a' "
                  "stroke-width='2'/>", "", "81afb3a7-a")
    A, B, C = (140.0, 20.0), (40.0, 200.0), (240.0, 200.0)
    t = 3.0 / 12.0
    P = (A[0] + t * (B[0] - A[0]), A[1] + t * (B[1] - A[1]))
    Qp = (A[0] + t * (C[0] - A[0]), A[1] + t * (C[1] - A[1]))
    s = sub1(s, "<line x1='72' y1='76' x2='208' y2='76' stroke='#1a1a2a' "
                "stroke-width='2'/>", line(*P, *Qp), "81afb3a7-b")
    s = sub1(s, "<text x='52' y='72' font-size='13' font-family='Arial' "
                "fill='#1a1a2a'>P</text>",
             txt(P[0] - 7, P[1] - 4, "P", 13, "end"), "81afb3a7-c")
    s = sub1(s, "<text x='212' y='72' font-size='13' font-family='Arial' "
                "fill='#1a1a2a'>Q</text>",
             txt(Qp[0] + 7, Qp[1] - 4, "Q", 13, "start"), "81afb3a7-d")
    s = sub1(s, "<text x='82' y='50' font-size='12' font-family='Arial' "
                "fill='#1a1a2a'>3 cm</text>",
             txt(118, 42, "3 cm", 12, "end"), "81afb3a7-e")
    s = sub1(s, "<text x='38' y='140' font-size='12' font-family='Arial' "
                "fill='#1a1a2a'>9 cm</text>",
             txt(66, 134, "9 cm", 12, "end"), "81afb3a7-f")
    return {"figure_svg": s}


def f_ce16a033(svg, q):
    """#104 -- the dashed CD started at A, not C, and stopped at a point that is not on
    AB at all, with a small square hanging where it ended. D is the foot of the
    perpendicular from C, so it is derived: project C onto AB. The stem already says CD
    is perpendicular, so D carries no square."""
    A, C, B = (40.0, 60.0), (40.0, 180.0), (200.0, 180.0)
    ux, uy = unit(*A, *B)
    t = (C[0] - A[0]) * ux + (C[1] - A[1]) * uy
    D = (A[0] + ux * t, A[1] + uy * t)
    s = sub1(svg, '<line x1="40" y1="60" x2="113" y2="155" stroke="currentColor" '
                  'stroke-width="1.8" stroke-dasharray="4,3"/>',
             line(*C, *D, w=1.8, dash="4,3"), "ce16a033-a")
    s = sub1(s, '<rect x="106" y="143" width="12" height="12" fill="none" '
                'stroke="currentColor" stroke-width="1.2" transform="rotate(38,113,155)"/>',
             "", "ce16a033-b")
    s = sub1(s, '<text x="116" y="172" font-size="13" font-family="Arial" '
                'fill="currentColor">D</text>',
             txt(D[0] + 8, D[1] - 5, "D", 13, "start"), "ce16a033-c")
    return {"figure_svg": s}


def f_5edd52c3(svg, q):
    """#108 -- the right-angle square at D was centred ON D, so half of it lay across
    road OB. A right-angle mark has its corner at the vertex and opens into the angle."""
    D, O, C = (102.0, 105.0), (50.0, 180.0), (210.0, 180.0)
    return {"figure_svg": sub1(
        svg, '<rect x="96" y="100" width="12" height="12" fill="none" '
             'stroke="#1a1a2a" stroke-width="1.5" transform="rotate(-55,102,105)"/>',
        right_angle_mark(D, O, C, 12), "5edd52c3")}


def f_dddc910e(svg, q):
    """#19 -- a bar chart with tick numbers up the side and nothing to read them across.
    Gridlines at exactly the three tick marks, drawn from the axis, behind the bars."""
    grid = "".join(f'<path d="M40 {y}H305" stroke="currentColor" stroke-opacity=".18" '
                   f'stroke-width="1"/>' for y in (135, 95, 55))
    return {"figure_svg": sub1(
        svg, "<line x1='40' y1='175' x2='305' y2='175' stroke='currentColor' "
             "stroke-width='2'/>",
        "<line x1='40' y1='175' x2='305' y2='175' stroke='currentColor' "
        "stroke-width='2'/>" + grid, "dddc910e")}


def f_5f8121d8(svg, q):
    """#39 -- the value above each bar was left-aligned at the bar's left edge, the
    y-axis word was 9 px, and the x-axis had no word at all."""
    s = svg
    for x_old, x_new, v in (("55", 65, "6"), ("100", 110, "10"), ("145", 155, "7"),
                            ("190", 200, "12"), ("235", 245, "5")):
        old = (f"<text x='{x_old}' y='{{Y}}' font-size='10' fill='#1a1a2a' "
               f"font-family='Arial'>{v}</text>")
        for yy in ("112", "72", "102", "52", "122"):
            cand = old.replace("{Y}", yy)
            if cand in s:
                s = sub1(s, cand, txt(x_new, int(yy), v, 11, "middle", "#1a1a2a"),
                         f"5f8121d8-{v}")
                break
        else:
            raise AssertionError(f"5f8121d8: no bar value {v}")
    s = sub1(s, "<text x='1' y='130' font-size='9' fill='#1a1a2a' "
                "font-family='Arial'>Goals</text>",
             '<text x="14" y="95" font-family="Arial,sans-serif" font-size="12" '
             'fill="#1a1a2a" text-anchor="middle" transform="rotate(-90 14 95)">'
             'Goals</text>', "5f8121d8-y")
    s = s.replace("</svg>", txt(162, 210, "Player", 12, "middle", "#1a1a2a") + "</svg>")
    return {"figure_svg": s}


def f_ccac7c88(svg, q):
    """#76 -- neither axis said what it held. The rotated 'Students' was anchored so
    that rotating it put the whole word off the left of the canvas, which is why the
    render showed no y-axis label at all.

    Reading the chart also settled the explanation, which used five numbers that are not
    the five drawn: swimming 80 + AFL 100 = 180 of 400, which is the keyed 45 per cent."""
    s = sub1(svg, "<text x='20' y='15' font-size='10' fill='currentColor' "
                  "font-family='sans-serif' transform='rotate(-90,20,100)'>Students</text>",
             '<text x="16" y="112" font-family="Arial,sans-serif" font-size="11" '
             'fill="currentColor" text-anchor="middle" transform="rotate(-90 16 112)">'
             'Number of students</text>', "ccac7c88-y")
    s = s.replace("</svg>", txt(167, 213, "Sport", 11) + "</svg>")
    return {
        "figure_svg": s,
        "explanation": (
            "Reading the bar chart: swimming 80, AFL 100, basketball 70, tennis 50, "
            "soccer 100. Total = 400 students. Swimming + AFL = 80 + 100 = 180. "
            "Percentage = 180 ÷ 400 × 100 = 45%."),
    }


# ================================================================= coordinate planes
def _label_near_point(svg, old_text, new_text, who):
    """Move an fl.plane point label and give it the white halo the others already have,
    so it stays readable where it now sits over a gridline."""
    s = sub1(svg, old_text, new_text, who + "-vis")
    halo = ('<g stroke="#fff" stroke-width="3" stroke-linejoin="round" fill="none" '
            'aria-hidden="true">')
    return sub1(s, halo, halo + new_text, who + "-halo")


def f_960e31fb(svg, q):
    """#47 -- 'P(1, 2)' had been pushed 83 px below the point, outside the grid. Back
    beside P, with a halo."""
    return {"figure_svg": _label_near_point(
        svg, '<text x="53" y="259" font-size="13" text-anchor="middle">P(1, 2)</text>',
        '<text x="84" y="191" font-size="13" text-anchor="start">P(1, 2)</text>',
        "960e31fb")}


def f_2f330d5e(svg, q):
    """#49 -- same fault, same fix."""
    return {"figure_svg": _label_near_point(
        svg, '<text x="55" y="256" font-size="13" text-anchor="middle">A(1, 2)</text>',
        '<text x="84" y="191" font-size="13" text-anchor="start">A(1, 2)</text>',
        "2f330d5e")}


def f_31585b1f(svg, q):
    """#21 -- the grid reached only y = 4, so the point (2, 5) and the top of the dashed
    segment sat off it. The grid is extended to y = 6 at the same two-unit spacing the
    ticks use, and y = 6 gets a tick and a number of its own so no gridline lands
    anywhere a tick does not.

    NOT redrawn through fl.plane: fl.plane moves a tick number to the other side of the
    axis wherever the plotted line runs through the tick row, and every range and cell
    size tried flipped one. A number out of line with the rest is the exact fault the
    reviewer raised on 4653b226, so regenerating would have traded one for another."""
    s = sub1(svg, '<path d="M115 63V167M175 63V167M235 63V167M55 63H235M55 89H235'
                  'M55 141H235M55 167H235"',
             '<path d="M115 37V167M175 37V167M235 37V167M55 37H235M55 63H235'
             'M55 89H235M55 141H235M55 167H235"', "31585b1f-a")
    s = sub1(s, '<line x1="51" y1="63" x2="59" y2="63" stroke="currentColor" '
                'stroke-width="1.2"/>',
             '<line x1="51" y1="37" x2="59" y2="37" stroke="currentColor" '
             'stroke-width="1.2"/><text x="46" y="41" font-size="11" '
             'fill="currentColor" text-anchor="end" font-family="sans-serif">6</text>'
             '<line x1="51" y1="63" x2="59" y2="63" stroke="currentColor" '
             'stroke-width="1.2"/>', "31585b1f-b")
    # the point label would now sit on the gridline that was added under it
    s = sub1(s, '<text x="123" y="44" font-size="11" fill="currentColor" '
                'text-anchor="start" font-family="sans-serif">(2, 5)</text>',
             '<text x="107" y="33" font-size="11" fill="currentColor" '
             'text-anchor="end" font-family="sans-serif">(2, 5)</text>', "31585b1f-c")
    return {"figure_svg": s}


def f_d3b6d5e1(svg, q):
    """#50 -- gridlines stopped short of both axes."""
    return {"figure_svg": fl.plane(
        points={"P(2, 5)": (2, 5), "Q(8, 1)": (8, 1)},
        segments=[((2, 5), (8, 1))], xr=(-1, 9), yr=(-1, 6), cell=26)}


def f_d6e54257(svg, q):
    """#106 -- the grid stopped inside the triangle."""
    def mark(px):
        return right_angle_mark(px(5, 4), px(1, 4), px(5, 1), 11)
    return {"figure_svg": fl.plane(
        polygon=[(1, 4), (5, 4), (5, 1)],
        points={"A": (1, 4), "B": (5, 4), "C": (5, 1)},
        xr=(-1, 7), yr=(-1, 6), cell=28, extra=mark)}


def f_2f68e90c(svg, q):
    """#109 -- no gridlines above y = 4, where the triangle's own top edge sits."""
    return {"figure_svg": fl.plane(
        polygon=[(0, 4), (6, 4), (3, 0)],
        points={"P": (0, 4), "Q": (6, 4), "R": (3, 0)},
        xr=(-1, 7), yr=(-1, 6), cell=28)}


def f_f17a9331(svg, q):
    """#67 -- P, Q and R were drawn between grid lines, so no area could be read off
    them. Placed on the lattice points the explanation names: P(1,1), Q(7,1), R(4,6)."""
    return {"figure_svg": fl.plane(
        polygon=[(1, 1), (7, 1), (4, 6)],
        points={"P": (1, 1), "Q": (7, 1), "R": (4, 6)},
        xr=(-1, 8), yr=(-1, 7), cell=26)}


def f_a30aed4e(svg, q):
    """#73 -- the intersection was drawn as a dot and labelled '(3,5)', which is the
    answer. Both are gone; the two lines stay and the student reads the crossing."""
    return {"figure_svg": fl.plane(
        lines=[((3, 0), (3, 1)), ((0, 2), (1, 3))],
        xr=(-4, 6), yr=(-3, 7), cell=24)}


def f_e75376a3(svg, q):
    """#25 -- options B and C were the same line: 4x - 2y = -6 rearranges to y = 2x + 3,
    so both gave infinitely many solutions. B stays the key, because rearranging is the
    skill; C becomes y = 2x - 3, which is PARALLEL to the graphed line and so gives no
    solutions -- the exact confusion the question is about.

    The figure is left alone. It is not what the reviewer flagged here, and redrawing
    it through fl.plane moved a tick number off its own axis."""
    return {
        "option_c": "y = 2x − 3",
        "explanation": (
            "The graphed line passes through (0, 3) and (1, 5), giving a gradient of 2 "
            "and the equation y = 2x + 3. For infinitely many solutions the second "
            "equation must be the SAME line. Option B: 4x − 2y = −6 → −2y = −4x − 6 → "
            "y = 2x + 3, which is that line. Option C is parallel to it, so that system "
            "has no solutions; A and D both have gradient −2 and cross the line once."),
    }


def f_929a33c3(svg, q):
    """#55 -- a dot printed at the intersection, a blue line that did not start at its
    own y-intercept and a red line drawn at the wrong gradient. Both lines are placed
    from their equations now, and the dot is gone."""
    def draw(px):
        spec = (((0, 7), (7, 0), "#1f6fb2", "y = −x + 7", 2.6, 6.6),
                ((0.5, -1), (5, 8), "#c0392b", "y = 2x − 2", 6.8, 7.4))
        out, halo, real = [], [], []
        for (x0, y0), (x1, y1), col, lab, lx, ly in spec:
            a, b = px(x0, y0), px(x1, y1)
            out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
                       f'y2="{b[1]:.1f}" stroke="{col}" stroke-width="2.2"/>')
            p = px(lx, ly)
            t = txt(p[0], p[1], lab, 12, "middle", col)
            halo.append(t)
            real.append(t)
        # The equation labels sit inside the grid, so a faint rule runs through them.
        # The answer a real graph gives is a page-coloured stroke behind the glyphs --
        # the same halo layer fl.plane draws its point labels with, and the same
        # aria-hidden group the checks already recognise.
        out.append('<g stroke="#fff" stroke-width="3" stroke-linejoin="round" '
                   'fill="none" aria-hidden="true">' + "".join(halo) + "</g>")
        return "".join(out + real)
    return {"figure_svg": fl.plane(xr=(-1, 8), yr=(-1, 9), cell=26, extra=draw)}


# ================================================================= hand-built figures
def f_0096a667(svg, q):
    """#4 -- the stem already says every corner is a right angle, so six right-angle
    squares and an italic 'all right angles' were both redundant. Removing them left the
    real fault visible: the bottom edge was labelled 8 when 10 across the top and a step
    of 3 leave only 7, and the shape does not close at 8.

    Perimeter, two ways. Edge by edge: 10 + 5 + 3 + 4 + 7 + 9 = 38. Bounding box: a
    rectilinear shape with a single corner notch has the perimeter of the 10 by 9
    rectangle that contains it, 2 x (10 + 9) = 38. The stored key of 46 is 38 with the
    bottom edge counted twice, which is what the stored explanation does."""
    u = 15.0
    x0, y0 = 20.0, 20.0
    p = [(x0, y0), (x0, y0 + 9 * u), (x0 + 7 * u, y0 + 9 * u),
         (x0 + 7 * u, y0 + 5 * u), (x0 + 10 * u, y0 + 5 * u), (x0 + 10 * u, y0)]
    body = [poly(p, fill="currentColor", fop=".18"),
            txt(x0 + 5 * u, y0 - 6, "10", 12),
            txt(x0 + 10 * u + 6, y0 + 2.5 * u, "5", 12, "start"),
            txt(x0 + 8.5 * u, y0 + 5 * u + 13, "3", 12),
            txt(x0 + 7 * u + 6, y0 + 7 * u, "4", 12, "start"),
            txt(x0 + 3.5 * u, y0 + 9 * u + 15, "7", 12),
            txt(x0 - 6, y0 + 4.5 * u, "9", 12, "end")]
    return {
        "figure_svg": wrap("".join(body), "0 0 200 185"),
        "correct_answer": "B",
        "explanation": (
            "Going round the outline: 10 + 5 + 3 + 4 + 7 + 9 = 38 cm. The same answer "
            "falls out of the bounding rectangle: because every corner is a right angle "
            "and only one corner is cut away, the horizontal edges add to 10 each way "
            "and the vertical edges to 9 each way, so the perimeter is 2 × (10 + 9) = "
            "38 cm. 46 comes from counting the bottom edge twice."),
    }


def f_19ba6203(svg, q):
    """#5 -- the number line began at -1, the very endpoint of the solution, leaving a
    bare stretch on the left. It runs from -3 now, so the open circle at -1 has line on
    both sides of it."""
    y, step, x0 = 35.0, 26.0, 30.0
    def X(v):
        return x0 + (v + 3) * step
    body = [line(16, y, 262, y, w=1.5),
            f'<polygon points="262,{y} 254,{y-4} 254,{y+4}" fill="currentColor"/>',
            f'<polygon points="16,{y} 24,{y-4} 24,{y+4}" fill="currentColor"/>']
    for v in range(-3, 6):
        body.append(line(X(v), y - 5, X(v), y + 5, w=1))
        body.append(txt(X(v), y + 19, "−1" if v == -1 else
                        ("−2" if v == -2 else ("−3" if v == -3 else str(v))), 11))
    body.append(f'<line x1="{X(-1)+6:.1f}" y1="{y}" x2="{X(5)-6:.1f}" y2="{y}" '
                f'stroke="currentColor" stroke-width="4" stroke-opacity=".5"/>')
    for v in (-1, 5):
        body.append(f'<circle cx="{X(v):.1f}" cy="{y}" r="5.5" fill="none" '
                    f'stroke="currentColor" stroke-width="2"/>')
    return {"figure_svg": wrap("".join(body), "0 0 280 70")}


def f_805a9fcc(svg, q):
    """#42 -- the right-angle square sat at the triangle's bottom-left vertex, which is
    not a right angle; the triangle's right angle is at its top-left, where it meets the
    rectangle. Redrawn from the stored working: rectangle 9 by 8 (72) and a triangle
    whose legs are the rectangle's 8 cm side and 6 cm along the top (24), total 96.

    Second route: the whole shape is a trapezium with parallel sides 15 and 9 and height
    8, so its area is (15 + 9) / 2 x 8 = 96."""
    u = 16.0
    A, B = (46.0, 30.0), (46.0 + 15 * u, 30.0)          # top-left, top-right
    C, D = (46.0 + 9 * u, 30.0 + 8 * u), (46.0, 30.0 + 8 * u)
    split_top, split_bot = (46.0 + 9 * u, 30.0), C
    body = [poly([A, B, C, D], fill="currentColor", fop=".18"),
            line(*split_top, *split_bot, w=1.5),
            right_angle_mark(split_top, split_bot, B, 13),
            txt((A[0] + D[0]) / 2 + 4.5 * u, D[1] + 18, "9 cm", 13),
            txt(A[0] - 6, (A[1] + D[1]) / 2, "8 cm", 13, "end"),
            txt((split_top[0] + B[0]) / 2, A[1] - 8, "6 cm", 13)]
    return {"figure_svg": wrap("".join(body), "0 0 320 200")}


def f_ef7b9ff2(svg, q):
    """#65 -- 'Square on AC' was a caption standing in for a square that was drawn but
    was not a square (its side was 145 px against a hypotenuse of 170) and ran off the
    top of the canvas. The square is drawn properly now, on the hypotenuse, and the
    caption is gone."""
    u = 12.0
    A, B, C = (45.0, 165.0), (45.0, 165.0 + 5 * u), (45.0 + 12 * u, 165.0 + 5 * u)
    vx, vy = C[0] - A[0], C[1] - A[1]
    nx, ny = -vy, vx                      # perpendicular, away from B
    if (nx * (B[0] - A[0]) + ny * (B[1] - A[1])) > 0:
        nx, ny = -nx, -ny
    sq = [A, C, (C[0] + nx, C[1] + ny), (A[0] + nx, A[1] + ny)]
    body = [poly(sq, w=1.5, dash="5,3"),
            poly([A, B, C]),
            right_angle_mark(B, A, C, 13),
            txt(A[0] - 8, (A[1] + B[1]) / 2, "5", 14, "end"),
            txt((B[0] + C[0]) / 2, C[1] + 18, "12", 14),
            txt(A[0] - 9, A[1] + 4, "A", 13, "end"),
            txt(B[0] - 9, B[1] + 13, "B", 13, "end"),
            txt(C[0] + 6, C[1] + 15, "C", 13, "start")]
    return {"figure_svg": wrap("".join(body), "0 0 275 250")}


def f_63e9b382(svg, q):
    """#57 -- the inscribed circle was drawn far too small to touch anything, so no
    radius could be read from it. It is derived now: the incircle of a right triangle
    sits at (r, r) from the right angle, so with legs 6 and 8 its centre is 2 cm in from
    each leg and it touches all three sides.

    Checked two ways: r = (a + b - c) / 2 = (6 + 8 - 10) / 2 = 2, and r = area / s =
    24 / 12 = 2. The drawn circle's distance to the hypotenuse is 40 px on a 20 px per
    cm scale, which is the same 2 cm."""
    u = 20.0
    A, B, C = (50.0, 180.0), (50.0, 180.0 - 6 * u), (50.0 + 8 * u, 180.0)
    r = 2.0 * u
    cx, cy = A[0] + r, A[1] - r
    body = [poly([A, B, C]),
            right_angle_mark(A, C, B, 14),
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="currentColor" '
            f'stroke-width="1.6" stroke-dasharray="5,3"/>',
            line(cx, cy, cx, A[1], w=1.4),
            txt(cx + 6, cy + (A[1] - cy) / 2 + 4, "r", 13, "start"),
            txt(A[0] - 10, (A[1] + B[1]) / 2, "6", 13, "end"),
            txt((A[0] + C[0]) / 2, A[1] + 18, "8", 13),
            txt(142, 104, "10", 13, "start"),
            txt(A[0] - 8, A[1] + 15, "A", 13, "end"),
            txt(B[0] - 8, B[1] - 4, "B", 13, "end"),
            txt(C[0] + 7, C[1] + 15, "C", 13, "start")]
    return {"figure_svg": wrap("".join(body), "0 0 240 215")}


def f_23bfa545(svg, q):
    """#2 -- the reviewer read 30 degrees against an obviously obtuse angle at B and 110
    against an obviously acute one at D, and said the answer should be 70.

    They are right, and the old marking could not be drawn at all. With BC parallel to
    AD, marking angle A = 70 AND angle ADC = 110 forces AB parallel to DC as well, which
    makes it a parallelogram, not the trapezoid the stem describes. So angle A is 60 and
    the shape closes as a trapezoid, drawn to those angles.

    Angle CDE two ways. Straight line at D: 180 - 110 = 70. Alternate angles: DE lies
    along AD which is parallel to CB, so angle CDE = angle DCB = 180 - 110 = 70. The
    stray 30 marked nothing and is gone."""
    A, D, E = (60.0, 170.0), (210.0, 170.0), (270.0, 170.0)
    h = 90.0
    B = (A[0] + h / math.tan(math.radians(60)), A[1] - h)
    C = (D[0] + h / math.tan(math.radians(70)), D[1] - h)
    body = [poly([A, B, C, D]), line(*D, *E),
            arc(*A, 26, D, B), arc(*D, 26, A, C), arc(*D, 40, C, E)]
    pa = bisect_pt(A, D, B, 48)
    pd = bisect_pt(D, A, C, 50)
    pe = bisect_pt(D, C, E, 58)
    body += [txt(pa[0], pa[1] + 4, "60°", 12),
             txt(pd[0], pd[1] + 4, "110°", 12),
             txt(pe[0], pe[1] + 4, "?", 13),
             txt(A[0] - 8, A[1] + 16, "A", 13, "end"),
             txt(B[0] - 6, B[1] - 8, "B", 13, "end"),
             txt(C[0] + 6, C[1] - 8, "C", 13, "start"),
             txt(D[0], D[1] + 16, "D", 13),
             txt(E[0], E[1] + 16, "E", 13)]
    return {
        "figure_svg": wrap("".join(body), "0 0 300 210"),
        "correct_answer": "B",
        "explanation": (
            "Angle ADC is marked 110°. E is on AD beyond D, so angle ADC and angle CDE "
            "sit on the straight line AE: angle CDE = 180° − 110° = 70°. The same "
            "answer comes from the parallel sides: DE lies along AD, which is parallel "
            "to CB, so angle CDE and angle DCB are alternate angles, and angle DCB = "
            "180° − 110° = 70°."),
    }


def f_7c325b26(svg, q):
    """#63 -- the reviewer said the answer should be 40, and it is.

    The stem also had the wrong pair of sides parallel: it said AB is parallel to DC,
    which would make ABCD a parallelogram, while the figure shows BC parallel to AD. The
    working needs BC parallel to AD, so the stem is corrected to match the figure.

    Angle BDC two ways. (1) Angle CDE = 120 so angle ADC = 60; BD crosses the parallels
    so angle BDA = angle DBC = 20; angle BDC = 60 - 20 = 40. (2) In triangle BDC, angle
    DBC = 20 and angle BCD = 180 - 60 = 120 (co-interior with angle ADC), so angle BDC =
    180 - 20 - 120 = 40."""
    h = 70.0
    D = (270.0, 150.0)
    B = (D[0] - h / math.tan(math.radians(20)), D[1] - h)
    A = (B[0] - h / math.tan(math.radians(70)), D[1])
    C = (D[0] - h / math.tan(math.radians(60)), D[1] - h)
    E = (D[0] + 45.0, D[1])
    body = [poly([A, B, C, D]), line(*D, *E), line(*B, *D, w=1.5, dash="6,3"),
            arc(*A, 26, D, B), arc(*B, 26, C, D),
            arc(*D, 30, B, C), arc(*D, 44, C, E)]
    pa = bisect_pt(A, D, B, 46)
    pb = bisect_pt(B, C, D, 52)
    pq = bisect_pt(D, B, C, 48)
    pe = bisect_pt(D, C, E, 66)
    body += [txt(pa[0], pa[1] + 4, "70°", 12),
             txt(pb[0], pb[1] + 4, "20°", 12),
             txt(pq[0], pq[1] + 4, "?", 13),
             txt(pe[0], pe[1] + 4, "120°", 12),
             txt(A[0] - 6, A[1] + 16, "A", 13, "end"),
             txt(B[0] - 6, B[1] - 8, "B", 13, "end"),
             txt(C[0] + 6, C[1] - 8, "C", 13, "start"),
             txt(D[0] - 2, D[1] + 17, "D", 13, "end"),
             txt(E[0] + 6, E[1] + 17, "E", 13, "start")]
    return {
        "figure_svg": wrap("".join(body), "0 0 350 200"),
        "stem": ("In the figure below, ABCD is a trapezoid with BC parallel to AD. "
                 "Point E lies on line AD extended beyond D, and angle measures are as "
                 "shown. What is the measure of angle BDC?"),
        "correct_answer": "D",
        "explanation": (
            "Angle CDE = 120°, so angle ADC = 180° − 120° = 60°. BD crosses the "
            "parallel sides BC and AD, so angle BDA = angle DBC = 20° (alternate "
            "angles). Angle BDC = angle ADC − angle BDA = 60° − 20° = 40°. Checking in "
            "triangle BDC: angle BCD = 180° − 60° = 120° (co-interior with angle ADC), "
            "so angle BDC = 180° − 20° − 120° = 40°."),
    }


def f_7edd1fff(svg, q):
    """#64 -- '38 degrees' was printed under the parallelogram, nowhere near angle DAC.
    Redrawn to the stem's own angles, so the shape agrees with its marks: angle DAC = 38
    and angle ACD = 47 make angle ADC = 95, and then angle BAD = 47 + 38 = 85.

    The stored explanation worked out 95 correctly and then subtracted it from 180,
    which is what you do for ADJACENT angles. ABC and ADC are OPPOSITE angles of the
    parallelogram, so they are equal: 95. Second route: angle BAD = 85 and angle ABC is
    co-interior with it along AB, so angle ABC = 180 - 85 = 95."""
    A = (40.0, 165.0)
    ad = 170.0
    D = (A[0] + ad, A[1])
    ac = ad * math.sin(math.radians(95)) / math.sin(math.radians(47))
    C = (A[0] + ac * math.cos(math.radians(38)), A[1] - ac * math.sin(math.radians(38)))
    B = (A[0] + C[0] - D[0], A[1] + C[1] - D[1])
    body = [poly([A, B, C, D]), line(*A, *C, w=1.5, dash="6,3"),
            arc(*A, 26, D, C), arc(*C, 26, A, D)]
    pa = bisect_pt(A, D, C, 55)
    pc = bisect_pt(C, A, D, 46)
    body += [txt(pa[0], pa[1] + 4, "38°", 12),
             txt(pc[0], pc[1] + 4, "47°", 12),
             txt(A[0] - 7, A[1] + 15, "A", 13, "end"),
             txt(B[0] - 7, B[1] - 6, "B", 13, "end"),
             txt(C[0] + 7, C[1] - 6, "C", 13, "start"),
             txt(D[0] + 7, D[1] + 15, "D", 13, "start")]
    return {
        "figure_svg": wrap("".join(body), "0 0 290 200"),
        "explanation": (
            "In triangle ACD: angle ADC = 180° − 38° − 47° = 95°. ABC and ADC are "
            "opposite angles of the parallelogram, so angle ABC = 95°. Checking the "
            "other way: AB is parallel to DC, so angle BAC = angle ACD = 47°, giving "
            "angle BAD = 47° + 38° = 85°; angle ABC is co-interior with angle BAD along "
            "AB, so angle ABC = 180° − 85° = 95°."),
    }


def f_422ba017(svg, q):
    """#3 -- a sector labelled 120 degrees was drawn at about 60, the '120' and the
    '6 cm' were both floating away from what they name, and 'Shaded sector' repeated
    what the stem already says. The sector is drawn from the number now, so it is a
    third of the circle."""
    O, r = (150.0, 120.0), 78.0
    a0, a1 = 90.0, -30.0                    # 120 degrees, clockwise from the top
    def P(a):
        return (O[0] + r * math.cos(math.radians(a)),
                O[1] - r * math.sin(math.radians(a)))
    p0, p1 = P(a0), P(a1)
    body = [f'<path d="M{p1[0]:.1f} {p1[1]:.1f}A{r} {r} 0 1 1 {p0[0]:.1f} '
            f'{p0[1]:.1f}" fill="none" stroke="currentColor" stroke-width="1.8"/>',
            f'<path d="M{O[0]} {O[1]}L{p0[0]:.1f} {p0[1]:.1f}'
            f'A{r} {r} 0 0 1 {p1[0]:.1f} {p1[1]:.1f}Z" fill="currentColor" '
            f'fill-opacity=".2" stroke="currentColor" stroke-width="1.8"/>',
            f'<circle cx="{O[0]}" cy="{O[1]}" r="3" fill="currentColor"/>',
            txt(179, 107, "120°", 13),
            txt(144, 84, "6 cm", 13, "end")]
    return {"figure_svg": wrap("".join(body), "0 0 300 220")}


def f_a6e5c362(svg, q):
    """#90 -- the two circles were drawn overlapping like a snowman. The stem says the
    small circle's diameter equals the large circle's radius, so the small circle sits
    on a radius of the large one: it passes through the large circle's centre and
    touches its circumference. Drawn that way, with the shaded region cut out by
    fill-rule."""
    O, R = (150.0, 130.0), 100.0
    r = R / 2
    c = (O[0], O[1] - r)
    body = [f'<path fill-rule="evenodd" fill="currentColor" fill-opacity=".18" '
            f'd="M{O[0]-R} {O[1]}a{R} {R} 0 1 0 {2*R} 0a{R} {R} 0 1 0 {-2*R} 0'
            f'M{c[0]-r} {c[1]}a{r} {r} 0 1 0 {2*r} 0a{r} {r} 0 1 0 {-2*r} 0"/>',
            f'<circle cx="{O[0]}" cy="{O[1]}" r="{R}" fill="none" '
            f'stroke="currentColor" stroke-width="2"/>',
            f'<circle cx="{c[0]}" cy="{c[1]}" r="{r}" fill="none" '
            f'stroke="currentColor" stroke-width="2"/>',
            line(c[0], c[1] - r, c[0], c[1] + r, w=1.5, dash="5,4"),
            f'<circle cx="{O[0]}" cy="{O[1]}" r="3.5" fill="currentColor"/>',
            txt(c[0] + 8, c[1] + 4, "10 cm", 13, "start")]
    return {"figure_svg": wrap("".join(body), "0 0 300 250")}


def f_d3c74fcc(svg, q):
    """#91 -- the reviewer worked the figure out as 44, and the figure as drawn did give
    44: the piece cut out of the 10 by 8 rectangle was 6 wide, not the 4 the working
    names, so 80 - 36 = 44. The keyed 56 needs a cut-out of 4 by 6, and that is what is
    drawn now, with both of its sides labelled inside the notch where they cannot be
    read as anything else.

    Two ways: 10 x 8 - 4 x 6 = 80 - 24 = 56, and as two pieces, a full-width bar 10 by 2
    plus a leg 6 by 6, 20 + 36 = 56."""
    u = 22.0
    x0, y0 = 40.0, 30.0
    W, H, nw, nh = 10 * u, 8 * u, 4 * u, 6 * u
    p = [(x0, y0), (x0 + W, y0), (x0 + W, y0 + H), (x0 + nw, y0 + H),
         (x0 + nw, y0 + H - nh), (x0, y0 + H - nh)]
    body = [poly(p, fill="currentColor", fop=".18"),
            txt(x0 + W / 2, y0 - 8, "10 cm", 13),
            txt(x0 + W + 8, y0 + H / 2, "8 cm", 13, "start"),
            txt(x0 + nw / 2, y0 + H - nh + 16, "4 cm", 13),
            txt(x0 + nw - 8, y0 + H - nh / 2 + 4, "6 cm", 13, "end")]
    return {"figure_svg": wrap("".join(body), "0 0 310 225")}


def f_cb1773e3(svg, q):
    """#98 -- a soft grey shadow ringed the pie, and its three sectors were drawn at
    roughly 120 degrees each while the labels said 90, 75 and the rest. Rebuilt through
    fl.pie_chart, where the sector angles come from the counts, so 90 is a quarter and
    75 is acute. Sleep 6 hours is 90 degrees, Study is 75, and the remaining 195 is
    everything else."""
    return {"figure_svg": fl.pie_chart(
        [("Sleep 90°", 90), ("Study 75°", 75), ("Other", 195)], r=64, lab_gap=30)}


def f_992eaf5f(svg, q):
    """#99 -- C was printed beside E, so the two triangles could not be told apart and
    the question could not be started. Redrawn as the nested pair the stem describes: B
    on AC with AB = 8 and BC = 12 (so AC = 20), E on AD, and BE parallel to CD.

    Everything is at 10 px per unit, so BE really is 6 and CD really is 15: AB/AC =
    8/20 = 2/5 and CD = 6 x 20/8 = 15."""
    A = (40.0, 190.0)
    th = math.radians(45)
    d = (math.cos(th), -math.sin(th))
    B = (A[0] + 80 * d[0], A[1] + 80 * d[1])
    C = (A[0] + 200 * d[0], A[1] + 200 * d[1])
    E = (A[0] + 76.57, A[1])
    D = (A[0] + 191.4, A[1])
    body = [line(*A, *D), line(*A, *C), line(*B, *E), line(*C, *D),
            txt(58, 156, "8", 13), txt(128, 84, "12", 13),
            txt(122, 161, "6", 13), txt(222, 118, "?", 13),
            txt(A[0] - 6, A[1] + 16, "A", 13, "end"),
            txt(E[0], E[1] + 16, "E", 13),
            txt(D[0], D[1] + 16, "D", 13),
            txt(B[0] - 10, B[1] - 5, "B", 13, "end"),
            txt(C[0] - 5, C[1] - 8, "C", 13, "end")]
    return {"figure_svg": wrap("".join(body), "0 0 260 220")}


def f_05ea2fe9(svg, q):
    """#60 -- the reviewer found three things and all three were real. The stem carried
    stray dollar signs around AB, CD, p, q and r. The arcs were incomplete or in the
    wrong place. And r was printed on the line AB with no arc at all, so it read as a
    straight angle -- which is why they said the question should not be solvable.

    Redrawn as the triangle it is, between the two parallel lines, with all three angles
    marked by an arc and lettered. The stem already gives p and q, so the figure carries
    only the letters. r = 180 - 65 - 48 = 67."""
    yA, yC = 45.0, 195.0
    h = yC - yA
    V1 = (60.0, yA)
    d1 = (math.cos(math.radians(65)), math.sin(math.radians(65)))
    V2 = (V1[0] + h / math.tan(math.radians(65)), yC)
    V3 = (V2[0] + h / math.tan(math.radians(67)), yA)
    d2 = unit(*V3, *V2)
    body = [line(40, yA, 250, yA), line(40, yC, 250, yC),
            line(V1[0] - 22 * d1[0], V1[1] - 22 * d1[1],
                 V2[0] + 22 * d1[0], V2[1] + 22 * d1[1]),
            line(V3[0] - 22 * d2[0], V3[1] - 22 * d2[1],
                 V2[0] + 22 * d2[0], V2[1] + 22 * d2[1]),
            arc(*V1, 26, V3, V2), arc(*V2, 26, V1, V3), arc(*V3, 26, V2, V1)]
    for v, a, b, lab in ((V1, V3, V2, "p"), (V2, V1, V3, "q"), (V3, V2, V1, "r")):
        p = bisect_pt(v, a, b, 42)
        body.append(txt(p[0], p[1] + 4.5, lab, 14))
    body += [txt(32, 50, "A", 13, "end"), txt(258, 50, "B", 13, "start"),
             txt(32, 200, "C", 13, "end"), txt(258, 200, "D", 13, "start")]
    return {
        "figure_svg": wrap("".join(body), "0 0 280 235"),
        "stem": ("In the figure below, line AB is parallel to line CD. Two straight "
                 "lines cross both of them and meet, forming a triangle. The angle "
                 "marked p is 65° and the angle marked q is 48°. What is the value of "
                 "the angle marked r?"),
        "explanation": (
            "p, q and r are the three angles of the triangle, and the angles of a "
            "triangle add to 180°. So r = 180° − 65° − 48° = 67°."),
    }


def f_aa8ee79a(svg, q):
    """#62 -- the four options were written as LaTeX, dollar signs and all, so a student
    would be shown '$y = 2x - 3$'. Plain text, with a proper minus sign."""
    return {"option_a": "y = x − 3", "option_b": "y = 3x − 3",
            "option_c": "y = 2x + 3", "option_d": "y = 2x − 3"}


def f_61dae39f(svg, q):
    """#43 -- five angle numbers scattered across the figure with one arc between them,
    none of them sitting in the region it names.

    Marking them properly showed the question could not stand as it was: whichever
    angle 4 is, the option calls it 'the corresponding angle', and corresponding angles
    ARE equal to x, so that option would have been a second right answer. Each number is
    now placed in a definite region, chosen so that exactly one of them equals x:

      x  interior at the upper crossing, right of the transversal
      2  interior at the upper crossing, left of it  -- supplementary to x
      3  interior at the lower crossing, left of it  -- alternate to x, so EQUAL
      4  interior at the lower crossing, right of it -- co-interior, supplementary
      5  below q, left of the transversal            -- supplementary

    The bracketed reasons in the options stay as they are: three of them are the
    tempting name for the wrong angle, which is the point of the question."""
    yp, yq = 60.0, 150.0
    t0, t1 = (80.0, 20.0), (190.0, 190.0)
    def on(y):
        return t0[0] + (y - t0[1]) * (t1[0] - t0[0]) / (t1[1] - t0[1])
    V1, V2 = (on(yp), yp), (on(yq), yq)
    L, R = 20.0, 260.0
    body = [line(L, yp, R, yp), line(L, yq, R, yq), line(*t0, *t1),
            txt(12, yp + 4, "p", 13, "end"), txt(12, yq + 4, "q", 13, "end")]
    # Two arcs at one crossing must differ in radius, or being adjacent they join into
    # a single semicircle and mark nothing. The adjacent pairs are x with 2, 3 with 4
    # and 3 with 5, so the small radius alternates.
    spec = [(V1, (R, yp), t1, 17, 30, "x"),
            (V1, (L, yp), t1, 29, 42, "2"),
            (V2, (L, yq), t0, 17, 30, "3"),
            (V2, (R, yq), t0, 29, 43, "4"),
            (V2, (L, yq), t1, 29, 42, "5")]
    for v, a, b, ar, lr, lab in spec:
        body.append(arc(*v, ar, a, b))
        p = bisect_pt(v, a, b, lr)
        body.append(txt(p[0], p[1] + 4, lab, 12))
    return {
        "figure_svg": wrap("".join(body), "0 0 280 200"),
        "stem": ("In the figure below, line p is parallel to line q, and a transversal "
                 "crosses both lines. Angle x is the angle at the upper crossing "
                 "between the transversal and line p, below p and to the right. Four "
                 "other angles are labelled 2, 3, 4 and 5. Which angle must be "
                 "congruent to angle x?"),
        "explanation": (
            "Angle x and angle 3 are alternate interior angles: they are on opposite "
            "sides of the transversal, one at each crossing, both between the parallel "
            "lines. Alternate interior angles are equal, so angle 3 = x. Angle 2 is "
            "next to x on the straight line p, angle 4 is co-interior with x, and "
            "angle 5 is equal to angle 4 — each of those three is 180° − x."),
    }


def f_a418c657(svg, q):
    """#92 -- B and C were dots placed 3 px and 17 px away from the crossings they name,
    with C's letter sitting halfway up the transversal instead of on line RS. Both are
    on their crossings now, derived from where the lines actually meet.

    The stem also named the angles as ABR and QBC. R is not on any ray from B, so angle
    ABR is not an angle in this figure; and the arcs are drawn at B and at C. The stem
    now names the transversal A-B-C-D and marks angle ABQ and angle RCD, which is what
    the two arcs enclose. Those two are equal (ABQ corresponds to the angle at C above
    RS on the right, and RCD is vertically opposite that), so 3x + 12 = 5x − 8 and
    x = 10; checking, both angles are then 42°."""
    yP, yR = 70.0, 140.0
    A, D = (80.0, 20.0), (200.0, 190.0)
    def on(y):
        return A[0] + (y - A[1]) * (D[0] - A[0]) / (D[1] - A[1])
    B, C = (on(yP), yP), (on(yR), yR)
    body = [line(20, yP, 260, yP), line(20, yR, 260, yR), line(*A, *D),
            f'<circle cx="{B[0]:.1f}" cy="{B[1]:.1f}" r="3" fill="currentColor"/>',
            f'<circle cx="{C[0]:.1f}" cy="{C[1]:.1f}" r="3" fill="currentColor"/>',
            arc(*B, 20, A, (260, yP)), arc(*C, 20, (20, yR), D),
            txt(4, yP + 4, "P", 12, "start"), txt(262, yP + 4, "Q", 12, "start"),
            txt(4, yR + 4, "R", 12, "start"), txt(262, yR + 4, "S", 12, "start"),
            txt(74, 16, "A", 12, "end"), txt(206, 194, "D", 12, "start"),
            txt(B[0] - 11, B[1] + 15, "B", 12, "end"),
            txt(C[0] + 11, C[1] - 7, "C", 12, "start")]
    p1 = bisect_pt(B, A, (260, yP), 40)
    p2 = bisect_pt(C, (20, yR), D, 42)
    body += [txt(p1[0], p1[1] + 4, "(3x + 12)°", 11),
             txt(p2[0], p2[1] + 4, "(5x − 8)°", 11)]
    return {
        "figure_svg": wrap("".join(body), "0 0 280 200"),
        "stem": ("In the figure below, lines PQ and RS are parallel. A transversal "
                 "cuts them, passing through A, then B on PQ, then C on RS, then D. "
                 "If ∠ABQ = (3x + 12)° and ∠RCD = (5x − 8)°, what is the value of x?"),
        "explanation": (
            "∠ABQ and ∠RCD are equal. ∠ABQ corresponds to the angle at C above RS on "
            "the right (corresponding angles on parallel lines), and ∠RCD is vertically "
            "opposite that angle. So 3x + 12 = 5x − 8, giving 2x = 20 and x = 10. "
            "Checking: both angles are then 42°."),
    }


def f_6579606d(svg, q):
    """#56 -- two arcs that each covered part of a region rather than spanning one, both
    expressions sitting off to the side of them, and the letter O printed inside the
    lower-left region as if it named that angle.

    Redrawn from the numbers: x = 32 makes both marked angles 3(32) + 12 = 108 and
    2(32) + 44 = 108, so the lines cross at 108 and 72 degrees and are drawn at exactly
    that. The two marked regions are the vertically opposite pair, each with a full arc
    from ray to ray and its expression outside the arc on the bisector. O sits beside
    the crossing point in the one region that carries no arc."""
    O = (140.0, 105.0)
    ln = 115.0
    def P(deg):
        return (O[0] + ln * math.cos(math.radians(deg)),
                O[1] - ln * math.sin(math.radians(deg)))
    A, Ao, B, Bo = P(36), P(216), P(144), P(324)
    body = [line(*Ao, *A), line(*B, *Bo),
            arc(*O, 30, A, B), arc(*O, 30, Ao, Bo),
            f'<circle cx="{O[0]}" cy="{O[1]}" r="3" fill="currentColor"/>',
            txt(O[0], O[1] - 46 + 4, "(3x + 12)°", 12),
            txt(O[0], O[1] + 46 + 4, "(2x + 44)°", 12),
            txt(O[0] - 12, O[1] + 5, "O", 13, "end")]
    return {"figure_svg": wrap("".join(body), "0 0 280 200")}


def f_b86b2e3c(svg, q):
    """#74 -- the reviewer said the question is unreadable, and it was, for the reason
    they gave and for one more.

    The stem defined C as lying on segment AE and also on segment BF. AE and BF are both
    diameters, so their only common point is the centre: C was P. Every angle named from
    C was therefore undefined, which is why 35 degrees could be marked at a place that
    is plainly obtuse. And option A named a point D that appears nowhere in the figure,
    while the stored explanation ended by declaring statement A untrue when the key is C.

    Rebuilt on the same picture without C: two diameters AE and BF meeting at P at 110
    degrees. PA = PB (radii), so triangle APB is isosceles with apex 110 and base angles
    (180 - 110) / 2 = 35. Second route: angle BPE = 70, and angle BAE is the inscribed
    angle on the same arc BE, so it is half of it, 35. Either way angle BAP is 35, not
    55, so C is the statement that is not true. The other three hold: PB and PF are both
    radii, PB and PE are both radii, and A, B, E, F have diagonals that are equal and
    bisect each other, so ABEF is a rectangle and AB is parallel to EF.

    Option A is changed from the phantom 'AB is congruent to BD' to 'PB is congruent to
    PF', which is true, so the key letter and the keyed text are both unchanged."""
    P, R = (150.0, 120.0), 95.0
    def pt(deg):
        return (P[0] + R * math.cos(math.radians(deg)),
                P[1] - R * math.sin(math.radians(deg)))
    A, E, B, F = pt(90), pt(270), pt(200), pt(20)
    body = [f'<circle cx="{P[0]}" cy="{P[1]}" r="{R}" fill="none" '
            f'stroke="currentColor" stroke-width="2"/>',
            line(*A, *E, w=1.6), line(*B, *F, w=1.6),
            f'<circle cx="{P[0]}" cy="{P[1]}" r="3.5" fill="currentColor"/>',
            arc(*P, 32, A, B),
            txt(104, 92, "110°", 13),
            txt(A[0], A[1] - 9, "A", 13),
            txt(E[0], E[1] + 19, "E", 13),
            txt(P[0] - 10, P[1] - 7, "P", 13, "end"),
            txt(B[0] - 16, B[1] + 9, "B", 13, "end"),
            txt(F[0] + 16, F[1] - 5, "F", 13, "start")]
    return {
        "figure_svg": wrap("".join(body), "0 0 300 250"),
        "stem": ("In the figure below, P is the centre of the circle. AE and BF are "
                 "diameters of the circle, and ∠APB = 110°. Which of the following "
                 "statements is NOT true?"),
        "option_a": "PB ≅ PF",
        "explanation": (
            "PA and PB are both radii, so triangle APB is isosceles. Its apex angle "
            "∠APB is 110°, so each base angle is (180° − 110°) ÷ 2 = 35°. That makes "
            "∠BAP 35°, not 55°, so statement C is the one that is not true. Checking "
            "∠BAP another way: ∠BPE = 180° − 110° = 70° is the angle at the centre on "
            "arc BE, and ∠BAE is the angle at the circumference on the same arc, so it "
            "is half of it, 35°. The other three statements hold: PB and PF are radii, "
            "PB and PE are radii, and ABEF has diagonals AE and BF that are equal and "
            "bisect each other, so it is a rectangle and AB is parallel to EF."),
    }


def f_f0ab0510(svg, q):
    """#88 -- the reviewer asked for the empty band above the 80 km point to be closed
    up, and rebuilding the axes to do that made the arithmetic fault plain.

    The graph is one straight line through the origin passing through (1, 20), (2, 40)
    and (4, 80): 20 km every hour. Between t = 1 and t = 3 the cyclist goes from 20 km
    to 60 km, so the average speed is 40 / 2 = 20 km/h. The stored explanation read 70
    km at t = 3, which is not on the line, and then signed off 'The answer is C' while
    the key said B. Two routes agree on 20 km/h: the gradient of the line is 80 / 4 =
    20, and (60 - 20) / (3 - 1) = 20. That is option D."""
    ox, oy = 55.0, 175.0
    sx, sy = 50.0, 1.75
    def X(t):
        return ox + t * sx
    def Y(km):
        return oy - km * sy
    body = []
    for km in (20, 40, 60, 80):
        body.append(f'<path d="M{ox} {Y(km):.1f}H265" stroke="currentColor" '
                    f'stroke-opacity=".18" stroke-width="1"/>')
    for t in (1, 2, 3, 4):
        body.append(f'<path d="M{X(t):.1f} 30V{oy}" stroke="currentColor" '
                    f'stroke-opacity=".18" stroke-width="1"/>')
    body.append(f'<path d="M{ox} 25V{oy}H275" stroke="currentColor" '
                f'stroke-width="1.8" fill="none"/>')
    for km in (20, 40, 60, 80):
        body.append(line(ox - 4, Y(km), ox, Y(km), w=1.2))
        body.append(txt(ox - 8, Y(km) + 4, str(km), 11, "end"))
    for t in (1, 2, 3, 4):
        body.append(line(X(t), oy, X(t), oy + 4, w=1.2))
        body.append(txt(X(t), oy + 17, str(t), 11))
    body.append(line(ox, oy, X(4), Y(80), w=2.2))
    for t in (1, 2, 3, 4):
        body.append(f'<circle cx="{X(t):.1f}" cy="{Y(20*t):.1f}" r="4" '
                    f'fill="currentColor"/>')
    body.append('<text x="20" y="100" font-family="Arial,sans-serif" font-size="12" '
                'fill="currentColor" text-anchor="middle" '
                'transform="rotate(-90 20 100)">Distance (km)</text>')
    body.append(txt(165, 208, "Time (hours)", 12))
    return {
        "figure_svg": wrap("".join(body), "0 0 290 225"),
        "correct_answer": "D",
        "explanation": (
            "The graph is a straight line through the origin: 20 km after 1 hour, 40 km "
            "after 2, 80 km after 4. At t = 1 the distance is 20 km and at t = 3 it is "
            "60 km, so the average speed = (60 − 20) ÷ (3 − 1) = 40 ÷ 2 = 20 km/h. The "
            "gradient of the whole line says the same thing: 80 ÷ 4 = 20 km/h."),
    }


BUILDERS = {
    "0096a667": f_0096a667, "05ea2fe9": f_05ea2fe9, "0896c838": f_0896c838,
    "13720600": f_13720600, "19ba6203": f_19ba6203, "1a87560f": f_1a87560f,
    "23bfa545": f_23bfa545, "2f330d5e": f_2f330d5e, "2f68e90c": f_2f68e90c,
    "31585b1f": f_31585b1f, "422ba017": f_422ba017, "4653b226": f_4653b226,
    "58e9df0d": f_58e9df0d, "5edd52c3": f_5edd52c3, "5f8121d8": f_5f8121d8,
    "61dae39f": f_61dae39f, "63e9b382": f_63e9b382, "6579606d": f_6579606d,
    "660a2278": f_660a2278, "791cf236": f_791cf236, "7c325b26": f_7c325b26,
    "7edd1fff": f_7edd1fff, "805a9fcc": f_805a9fcc, "81afb3a7": f_81afb3a7,
    "929a33c3": f_929a33c3, "960e31fb": f_960e31fb, "992eaf5f": f_992eaf5f,
    "9a": None,
    "a30aed4e": f_a30aed4e, "a418c657": f_a418c657, "a6e5c362": f_a6e5c362,
    "a723bb91": f_a723bb91, "aa8ee79a": f_aa8ee79a, "b0646282": f_b0646282,
    "b03c10bc": f_b03c10bc, "b2e0b69d": f_b2e0b69d, "b86b2e3c": f_b86b2e3c,
    "bed54cfb": f_bed54cfb, "cb1773e3": f_cb1773e3, "ccac7c88": f_ccac7c88,
    "ce16a033": f_ce16a033, "d3b6d5e1": f_d3b6d5e1, "d3c74fcc": f_d3c74fcc,
    "d4914353": f_d4914353, "d6e54257": f_d6e54257, "dddc910e": f_dddc910e,
    "e75376a3": f_e75376a3, "ef7b9ff2": f_ef7b9ff2, "f0ab0510": f_f0ab0510,
    "f17a9331": f_f17a9331,
}
BUILDERS.pop("9a")


def state(row, svg):
    """The set of checks currently firing on this question.

    `options_distinct` is the one check in the suite that returns True for GOOD; every
    other returns None for good and a message for a finding. Reading it the same way as
    the rest made all forty-nine look like they were failing it."""
    r = dict(row)
    r["figure_svg"] = svg
    fired = {n for n in FIG_CHECKS if getattr(qc, n)(svg)}
    for n in Q_CHECKS:
        hit = getattr(qc, n)(r)
        if (not hit) if n == "options_distinct" else bool(hit):
            fired.add(n)
    return fired


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
        if q["review_status"] != "pending":
            refused.append({"id": q["id"], "why": f"status {q['review_status']}"})
            continue
        before = state(q, q["figure_svg"])
        upd = build(q["figure_svg"], q)
        after_row = dict(q)
        after_row.update(upd)
        after = state(after_row, after_row["figure_svg"])
        gained = sorted(after - before)
        rec = {"id": q["id"], "form": q["form_id"], "pos": q["form_position"],
               "changed": sorted(upd), "before": sorted(before), "after": sorted(after),
               "newly_firing": gained}
        if gained:
            refused.append(rec)
            continue
        done.append(rec)
        dump.append({"id": q["id"], **upd})
        if args.apply:
            cols = ", ".join(f"{k} = ?" for k in upd)
            con.execute(f"UPDATE questions SET {cols}, edited = 1 WHERE id = ?",
                        [*upd.values(), q["id"]])
    if args.apply:
        con.commit()
    if args.dump:
        args.dump.write_text(json.dumps(dump, indent=1))
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps({"done": done, "refused": refused}, indent=1))
    print(f"repaired {len(done)}   refused {len(refused)}"
          f"   {'APPLIED' if args.apply else 'dry run'}")
    for r in refused:
        print("  REFUSED", r.get("id"), r.get("newly_firing") or r.get("why"))
    cleared = sum(len(set(r["before"]) - set(r["after"])) for r in done)
    print(f"findings cleared: {cleared}")
    for r in done:
        gone = sorted(set(r["before"]) - set(r["after"]))
        left = sorted(set(r["after"]))
        print(f"  {r['id'][:8]} {r['form']} pos{r['pos']:>3}  "
              f"changed={','.join(r['changed'])}"
              f"{'  cleared=' + ','.join(gone) if gone else ''}"
              f"{'  still=' + ','.join(left) if left else ''}")


if __name__ == "__main__":
    main()
