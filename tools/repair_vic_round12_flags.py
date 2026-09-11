#!/usr/bin/env python3
"""VIC round 12: the 33 questions the reviewer flagged in the Selectly UI itself.

WHERE THESE CAME FROM. Every earlier round arrived as a JSON file downloaded from a
figure page we built and emailed. This one did not. All 153 VIC forms went live on
2026-09-04, and the reviewer has been working through them inside Selectly, pressing
the flag button. `review/ui/flagged-questions-2026-09-11.csv` is that queue exported:
33 rows across `vic-drill-mq-001` to `-018`, flagged between 2026-08-29 and 09-08.

SO EVERY ONE OF THESE IS LIVE AND APPROVED, which no previous round was. The repairs
here change what a student is being served right now, and they have to be pushed back
to Selectly afterwards or the fix never reaches anyone.

NONE OF THE 33 HAD BEEN REPAIRED. Checked rather than assumed: the stem, options, key,
explanation and SVG of all 33 were hashed against every backup in run_data/db, and not
one has changed since 2026-08-31 -- before the earliest of these flags was acted on and
well before the 09-07 ones were written. The eleven flags on forms 001-010 are the
unpaged-figure problem from 2026-09-07 arriving by a different route: those forms were
approved in August, so `figure_review_page.py --status pending` left their figures off
every page we ever sent.

WHAT THE 33 ARE. Sixteen are figures. Eight are questions that need a calculator or land
on a number that does not round cleanly. Four are prose questions about method sitting in
a maths paper. Three are markup leaking into the stem -- dollar signs, backticks, carets.
One is a duplicate pair inside a single form. One is a table the question describes but
the figure never showed.

Every figure is rendered and looked at before it is applied, and every question's full
check state is compared before and after: a question that would gain a finding is refused
rather than written.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_vic_round12_flags
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_vic_round12_flags --apply
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import pathlib
import re
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import figure_lib as fl                            # noqa: E402
from tools import question_checks as qc                       # noqa: E402
from tools.repair_vic_round10_figures import (                # noqa: E402
    FIG_CHECKS, Q_CHECKS, arc, halo, line, sub1, subn, txt, unit)

DB = ROOT / "run_data/db/qbank.db"
CSV = ROOT / "review/ui/flagged-questions-2026-09-11.csv"
RECORD = ROOT / "run_data/output/vic_round12_flags.json"

WHITE = "#fff"
INK = "currentColor"


def grid_path(xs, ys, x0, x1, y0, y1, op=".16"):
    """One faint rule per tick, drawn from axis to axis as a single path.

    The rules are placed at the SAME pixel values the ticks are, because a grid laid out
    on its own spacing is how `7c472f4d` ended up 2.5 px out from its own numbering --
    which is exactly what the reviewer called 'slightly off'."""
    d = "".join(f"M{x:g} {y0:g}V{y1:g}" for x in xs)
    d += "".join(f"M{x0:g} {y:g}H{x1:g}" for y in ys)
    return (f'<path d="{d}" stroke="currentColor" stroke-opacity="{op}" '
            f'stroke-width="1" fill="none"/>')


def haloed(x, y, s, size=11, anchor="middle", extra=""):
    """A label drawn twice: page-coloured underneath, glyphs on top."""
    a = f' text-anchor="{anchor}"' if anchor else ""
    common = (f'x="{x:.1f}" y="{y:.1f}" font-family="Arial,sans-serif" '
              f'font-size="{size}"{a}{extra}')
    return (f'<g aria-hidden="true"><text {common} fill="none" stroke="{WHITE}" '
            f'stroke-width="3" stroke-linejoin="round">{s}</text></g>'
            f'<text {common} fill="currentColor">{s}</text>')


def numbers(items, size=10, anchor="middle"):
    """A set of labels drawn twice -- halo layer, then glyphs -- with the shared
    attributes hoisted onto the two <g> elements.

    One <g> per label, which is what `haloed` gives you, costs about 90 bytes apiece and
    is what pushed three of this round's figures past the 3.5 KB limit
    `figure_svg_errors` enforces. x, y, font-size and text-anchor stay on each <text>,
    because `question_checks._text_box` reads all four off the tag and would mis-box
    every one of them if they were hoisted too."""
    body = "".join(f'<text x="{x:.0f}" y="{y:.0f}" font-size="{size}" '
                   f'text-anchor="{anchor}">{t}</text>' for x, y, t in items)
    return (f'<g font-family="Arial,sans-serif" stroke="#fff" stroke-width="3" '
            f'stroke-linejoin="round" fill="none" aria-hidden="true">{body}</g>'
            f'<g font-family="Arial,sans-serif" fill="currentColor">{body}</g>')


def strokes(segs, w=1, op=None):
    """Many short rules as ONE path -- ticks, gridlines, a dial's graduations."""
    d = "".join(f"M{a:.0f} {b:.0f}L{c:.0f} {e:.0f}" for (a, b), (c, e) in segs)
    o = f' stroke-opacity="{op}"' if op else ""
    return (f'<path d="{d}" fill="none" stroke="currentColor" '
            f'stroke-width="{w}"{o}/>')


def polyline(pts, w=2, dash=None, close=False, fill="none", op=None):
    d = "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + ("Z" if close else "")
    a = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' stroke-opacity="{op}"' if op else ""
    return (f'<path d="{d}" fill="{fill}" stroke="currentColor" '
            f'stroke-width="{w}"{a}{o}/>')


def right_angle(vx, vy, p1, p2, size=10):
    """A right-angle square at v, drawn INTO the corner between the two rays."""
    ux, uy = unit(vx, vy, *p1)
    wx, wy = unit(vx, vy, *p2)
    a = (vx + ux * size, vy + uy * size)
    b = (vx + ux * size + wx * size, vy + uy * size + wy * size)
    c = (vx + wx * size, vy + wy * size)
    return polyline([a, b, c], w=1.2, op=".75")


# ==================================================== figures repaired in place
def f_7c472f4d(svg, q):
    """#1 -- 'The thin grid lines don't properly align with the Axis numbering.
    Slightly off.'

    They were off, and the axis was the thing that was wrong. The x-axis is at y=185
    and the 60 km tick at y=35, so 15 km is 37.5 px. The four y ticks were drawn at
    145, 110, 70, 35 -- spacings of 35, 40, 35. The scale was NOT linear, and the grid
    was laid on those same wrong heights, so the two agreed with each other and both
    disagreed with the numbers. Ticks and rules now sit at 147.5, 110, 72.5, 35, which
    is 37.5 apart all the way down and puts 0 exactly on the axis.

    The grid also started at x=105 -- the first tick -- leaving the first hour outside
    it, which is `gridlines_stop_short_of_the_axes`. It now runs from the y-axis."""
    ys = [185 - 2.5 * v for v in (15, 30, 45, 60)]           # 2.5 px per km
    xs = [50 + 55 * t for t in (1, 2, 3, 4)]                 # 55 px per hour
    old_grid = ('<path d="M105 35V145M160 35V145M215 35V145M270 35V145M105 35H270'
                'M105 70H270M105 110H270M105 145H270" stroke="currentColor" '
                'stroke-opacity=".16" stroke-width="1" fill="none"/>')
    svg = sub1(svg, old_grid, grid_path(xs, ys, 50, 270, 35, 185), "7c472f4d grid")
    for was, now, lab in ((145, 147.5, "15"), (70, 72.5, "45")):
        svg = sub1(svg, f'<line x1="50" y1="{was}" x2="54" y2="{was}"',
                   f'<line x1="50" y1="{now}" x2="54" y2="{now}"', f"tick {lab}")
        svg = sub1(svg, f'<text x="30" y="{was + 4}" font-family="Arial" font-size="11" '
                   f'fill="currentColor">{lab}</text>',
                   f'<text x="30" y="{now + 4:g}" font-family="Arial" font-size="11" '
                   f'fill="currentColor">{lab}</text>', f"label {lab}")
    return {"figure_svg": svg}


def f_b445f197(svg, q):
    """#2 -- 'Please create a little more distance between the x-axis label and the
    numberings.'

    'Books borrowed' sat at y=166 with the category labels at y=159: seven pixels, and
    the two ran together. It goes to y=174 and the canvas grows to hold it."""
    svg = sub1(svg, '<text x="182" y="166"', '<text x="182" y="174"', "b445f197 label")
    return {"figure_svg": sub1(svg, 'viewBox="-4.49 0 344.49 176"',
                               'viewBox="-4.49 0 344.49 184"', "b445f197 canvas")}


def f_ef761fd8(svg, q):
    """#3 -- 'the 16cm value overlaps with the shape's boundary.'

    '16 cm' started at x=142 and runs about 34 px, so it reached x=176; the upper-right
    edge crosses that height at x=175. It names the VERTICAL diagonal, which is at
    x=130, and the left of that diagonal is empty at this height -- the upper-left edge
    is out at x=85. Ending the label at x=124 puts it beside the diagonal it names with
    both edges clear."""
    return {"figure_svg": sub1(
        svg, '<text x="142" y="58" font-size="11.5" fill="currentColor">16 cm</text>',
        '<text x="124" y="106" font-size="11.5" fill="currentColor" '
        'text-anchor="end">16 cm</text>', "ef761fd8")}


def f_8cebedb1(svg, q):
    """#4 -- 'The coordinate plane is missing the thin grid lines to make it seem more
    professional.'

    A sweep added the grid on 2026-08-29, hours after this was flagged, so the note is
    already most of the way answered. Two things it left behind are done here: the grid
    column for x=2 was drawn at 201 while the tick is at 200, and the '-1' tick number
    sits on the x=-1 column with nothing behind it. The number gets the halo the figure
    never gave it."""
    svg = sub1(svg, "M201 20V200", "M200 20V200", "8cebedb1 column")
    old = ('<text x="107" y="126" font-size="10" fill="#1a1a2a" '
           'font-family="Arial">−1</text>')
    new = ('<g aria-hidden="true"><text x="107" y="126" font-size="10" fill="none" '
           'stroke="#fff" stroke-width="3" stroke-linejoin="round" '
           'font-family="Arial">−1</text></g>' + old)
    return {"figure_svg": sub1(svg, old, new, "8cebedb1 halo")}


def f_17e21920(svg, q):
    """#20 -- 'Add grid lines, number scaling ticks, and the (0, 0) overlaps with the
    y-axis.'

    The triangle itself was already right: the origin is at (50, 190) and both axes run
    at 20 px per unit, so (0,6) and (7,0) are where they claim to be. What it had no
    scale on, so a reader had to take the three printed coordinates on trust.

    Once the grid and the numbers are on, those three printed coordinates are both
    redundant and in the way -- '(0,0)' ran through the y-axis, which is what was
    flagged, and '(7,0)' lands on the number 8. They come off, and the vertices are
    read off the grid, which is what the question is asking a student to do."""
    xs = [50 + 20 * i for i in range(1, 11)]
    ys = [190 - 20 * i for i in range(1, 7)]
    add = grid_path(xs, ys, 50, 250, 50, 190)
    add += strokes([((x, 190), (x, 186)) for x in xs]
                   + [((50, y), (54, y)) for y in ys], w=1)
    add += numbers([(x, 203, str(i)) for i, x in enumerate(xs, 1)], size=10)
    add += numbers([(44, y + 4, str(i)) for i, y in enumerate(ys, 1)], size=10,
                   anchor="end")
    svg = sub1(svg, "<line x1='30' y1='190'", add + "<line x1='30' y1='190'",
               "17e21920 grid")
    svg = sub1(svg, "<text x='265' y='194' font-size='12' font-family='Arial' "
               "fill='#1a1a2a'>x</text>",
               "<text x='258' y='180' font-size='12' font-family='Arial' "
               "fill='#1a1a2a'>x</text>", "17e21920 x label")
    for lab, x, y in (("(0,0)", 32, 204), ("(7,0)", 194, 204), ("(0,6)", 54, 68)):
        svg = sub1(svg, f"<text x='{x}' y='{y}' font-size='12' font-family='Arial' "
                   f"fill='#1a1a2a'>{lab}</text>", "", f"17e21920 {lab}")
    return {"figure_svg": svg}


# ================================================================ figures redrawn
def f_b84412bc(svg, q):
    """#7 -- 'The smaller inner circle should be completely encompassed to the point a
    small part of both circumferences overlap.'

    Measured: the big circle was centred (140,130) with r=80 and the small one (140,82)
    with r=40. Internal tangency needs the centres 80-40=40 apart; they were 48 apart,
    so the small circle poked 8 px out through the top of the big one.

    Redrawn at 8 px per cm from the two radii themselves, so the centres are 48 px apart
    and the circumferences meet at exactly one point. The dashed line was drawn across
    the small circle's whole DIAMETER, 80 px, and labelled 6 -- which is the radius. It
    is a radius now, and drawn to the side rather than upwards so '6 cm' has room to sit
    beside it without touching the circle it measures."""
    S = 8.0
    bcx, bcy, br = 140.0, 122.0, 12 * S          # big circle, radius 12 cm
    scx, scy, sr = 140.0, bcy - (br - 6 * S), 6 * S   # internally tangent at the top
    body = [
        '<rect width="280" height="240" fill="none"/>',
        # The shaded region is one path with two subpaths and fill-rule="evenodd",
        # so the hole IS the small circle rather than a disc painted over it in the
        # page colour -- which `figure_svg_errors` refuses, and rightly: a figure
        # that paints its own white would vanish on a dark surface.
        f'<path d="M{bcx - br:g} {bcy:g}a{br:g} {br:g} 0 1 0 {2 * br:g} 0'
        f'a{br:g} {br:g} 0 1 0 {-2 * br:g} 0ZM{scx - sr:g} {scy:g}'
        f'a{sr:g} {sr:g} 0 1 0 {2 * sr:g} 0a{sr:g} {sr:g} 0 1 0 {-2 * sr:g} 0Z" '
        f'fill-rule="evenodd" fill="currentColor" fill-opacity=".18"/>',
        f'<circle cx="{bcx:g}" cy="{bcy:g}" r="{br:g}" fill="none" '
        f'stroke="currentColor" stroke-width="2"/>',
        f'<circle cx="{scx:g}" cy="{scy:g}" r="{sr:g}" fill="none" '
        f'stroke="currentColor" stroke-width="2"/>',
        f'<line x1="{scx:g}" y1="{scy:g}" x2="{scx + sr:g}" y2="{scy:g}" '
        f'stroke="currentColor" stroke-width="1.5" stroke-dasharray="4,3"/>',
        f'<circle cx="{scx:g}" cy="{scy:g}" r="2.5" fill="currentColor"/>',
        haloed(scx + sr / 2, scy - 8, "6 cm", size=12),
        f'<text x="{bcx:g}" y="{bcy + br - 22:g}" font-size="12" '
        f'font-family="Arial,sans-serif" text-anchor="middle" '
        f'fill="currentColor">Shaded region</text>',
    ]
    return {"figure_svg": '<svg width="280" height="240" viewBox="0 0 280 240" '
            'xmlns="http://www.w3.org/2000/svg">' + "".join(body) + "</svg>"}


def f_117dde83(svg, q):
    """#13 -- 'the numbers overlap with the sides and one of the numbers is cut off.'

    Both are true, and redrawing found something worse than either. DEF was drawn on
    (30,180) (100,60) (170,180): its three sides measure 139, 139 and 140 px. It is an
    equilateral triangle carrying the labels 4, 6 and 8. PQR was the same shape again.
    So the figure said nothing the question says, and no check looks at a triangle's
    shape once it has an unknown side.

    Both are rebuilt from the side lengths themselves at ONE scale, 11 px per cm, so
    the second really is two and a half times the first and a reader can see it. Every
    dimension sits on the outward normal of the side it names, which is what kept the
    old '4 cm' and '6 cm' off their own edges."""
    def tri(a, b, c, ox, oy, s):
        """Triangle with |AB|=c... placed from side lengths: D at origin, F at (dl,0),
        E found by intersecting the two circles."""
        de, ef, df = a, b, c
        x = (df * df + de * de - ef * ef) / (2.0 * df)
        y = math.sqrt(max(de * de - x * x, 0.0))
        return [(ox, oy), (ox + x * s, oy - y * s), (ox + df * s, oy)]

    S = 11.0
    d, e, f = tri(4, 6, 8, 26, 160, S)          # DE=4, EF=6, DF=8
    p, qq, r = tri(10, 15, 20, 158, 160, S)     # x2.5
    body = ['<rect width="400" height="210" fill="none"/>']
    body.append(polyline([d, e, f], w=2, close=True))
    body.append(polyline([p, qq, r], w=1.8, close=True, dash="5,3"))

    def side_label(a, b, third, text, size=11, off=17):
        """Placed on the side's own outward normal -- away from the third vertex."""
        mx, my = (a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0
        ux, uy = unit(*a, *b)
        nx, ny = -uy, ux
        if (third[0] - mx) * nx + (third[1] - my) * ny > 0:
            nx, ny = -nx, -ny
        return haloed(mx + nx * off, my + ny * off + 4, text, size=size)

    body.append(side_label(d, e, f, "4 cm"))
    body.append(side_label(e, f, d, "6 cm"))
    body.append(side_label(d, f, e, "8 cm"))
    body.append(side_label(qq, r, p, "20 cm"))
    for pt, lab, dx, dy in ((d, "D", -12, 6), (e, "E", 0, -8), (f, "F", 6, 14),
                            (p, "P", -12, 6), (qq, "Q", 0, -8), (r, "R", 10, 6)):
        body.append(f'<text x="{pt[0] + dx:.1f}" y="{pt[1] + dy:.1f}" '
                    f'font-family="Arial,sans-serif" font-size="13" '
                    f'text-anchor="middle" fill="currentColor">{lab}</text>')
    return {"figure_svg": '<svg width="400" height="210" viewBox="0 0 400 210" '
            'xmlns="http://www.w3.org/2000/svg">' + "".join(body) + "</svg>"}


def f_14b90a3c(svg, q):
    """#19 -- 'The circle isn't the right size; it is too small, and the hypotenuse is
    longer than it's diamater. There is also many overlapping numbers with the circle's
    circumference.'

    All three, and the first two have one cause. The legs were drawn 120 px and 120 px
    while the question calls them 12 cm and 9 cm, so the hypotenuse came out at 170 px
    -- and the circle, drawn at r=75 for a 150 px diameter, could not reach the two
    corners it is supposed to pass through.

    Redrawn at 12 px per cm: legs 144 and 108, hypotenuse exactly 180, circle centred on
    its midpoint at r=90. The circle now passes through B and C because it is built from
    them.

    Note all THREE vertices sit on the circle -- the right angle at A stands on the
    diameter BC, so Thales puts A there too. That is why the old labels could not be got
    out of the way: outside a leg is still inside the circle until you are three
    centimetres clear of it. '12 cm' is written UP its own side instead, which is the
    only way it fits in that gap, and the checks read a rotate(-90) label correctly."""
    S = 12.0
    A = (100.0, 205.0)                        # right angle
    B = (A[0], A[1] - 12 * S)                 # 12 cm up
    C = (A[0] + 9 * S, A[1])                  # 9 cm across
    mx, my = (B[0] + C[0]) / 2.0, (B[1] + C[1]) / 2.0
    body = ['<rect width="320" height="265" fill="none"/>',
            f'<circle cx="{mx:g}" cy="{my:g}" r="{7.5 * S:g}" fill="none" '
            f'stroke="currentColor" stroke-width="1.5" stroke-dasharray="5,4"/>',
            polyline([A, B, C], w=2, close=True),
            right_angle(*A, B, C, size=14)]
    ux, uy = unit(*B, *C)
    body.append(haloed(mx - uy * 16, my + ux * 16 + 4, "15 cm", size=12))
    body.append(haloed(A[0] - 12, (A[1] + B[1]) / 2, "12 cm", size=12,
                       extra=f' transform="rotate(-90,{A[0] - 12:g},'
                             f'{(A[1] + B[1]) / 2:g})"'))
    # Below the circle's lowest point, not beside the base: the base IS a chord, so
    # the arc swings under it and a label 20 px down sits on the dashes.
    body.append(haloed((A[0] + C[0]) / 2, my + 7.5 * S + 18, "9 cm", size=12))
    for pt, lab, dx, dy in ((A, "A", -11, 15), (B, "B", -11, -8), (C, "C", 13, 15)):
        body.append(haloed(pt[0] + dx, pt[1] + dy, lab, size=12))
        body.append(f'<circle cx="{pt[0]:g}" cy="{pt[1]:g}" r="2.6" '
                    f'fill="currentColor"/>')
    return {"figure_svg": '<svg width="320" height="265" viewBox="0 0 320 265" '
            'xmlns="http://www.w3.org/2000/svg">' + "".join(body) + "</svg>"}


TICK_RE = re.compile(
    r'<g font-family="system-ui,sans-serif" stroke="#fff"[^>]*aria-hidden="true">'
    r'(.*?)</g><g font-family="system-ui,sans-serif" fill="currentColor"'
    r' fill-opacity="\.75">.*?</g>', re.S)
ONE_TICK = re.compile(r'<text x="(-?[\d.]+)" y="(-?[\d.]+)" font-size="10" '
                      r'text-anchor="(\w+)">([^<]*)</text>')


def straighten_ticks(svg):
    """Put every tick number back in its own row or column, on top of the ink.

    `plane` draws the numbers BEFORE the plotted lines, so a line crosses them. Its
    answer is to move the struck-through number to the other side of the axis, or drop
    it if neither side is clear. The owner ruled on exactly that in round 11: a missing
    tick number is to be written, and every number sits on the same side of its axis as
    the rest. Three figures in this round hit it -- the segment AB in `a016ffb4` runs up
    through the x row at 2, and line l in `fd4d2c94` grazes the y column at 5.

    So the two tick layers are lifted out and re-emitted at the END of the document,
    where the halo can do its job: page-coloured stroke first, glyphs on top, and the
    line behind is broken where the digits sit. Every number is moved back to the
    majority row or column, and any the layout dropped is written back at the pixel its
    own neighbours put it -- the mapping is fitted from the numbers that survived, so a
    restored one cannot land off the scale.

    A NUMBER IS ONLY EVER MOVED ACROSS ITS AXIS, never along it. A y number shifted up
    or down, or an x number left or right, changes the mapping every check reads out of
    the label positions, which is how round 10 turned a linear axis into a nonlinear
    one three times."""
    m = TICK_RE.search(svg)
    if not m:
        raise AssertionError("straighten_ticks: plane tick layers not found")
    got = [(float(a), float(b), c, d) for a, b, c, d in ONE_TICK.findall(m.group(1))]
    nums = [(x, y, an, t) for x, y, an, t in got if t != "O"]
    rows = [(x, y, an, t) for x, y, an, t in nums if an == "middle"]
    cols = [(x, y, an, t) for x, y, an, t in nums if an != "middle"]

    def majority(vals):
        return collections.Counter(vals).most_common(1)[0][0]

    def fit(pairs):
        """value -> pixel, from at least two placed numbers."""
        (v0, p0), (v1, p1) = pairs[0], pairs[-1]
        step = (p1 - p0) / (v1 - v0)
        return lambda v: p0 + (v - v0) * step

    out = []
    for group, is_row in ((rows, True), (cols, False)):
        if not group:
            continue
        fixed = majority([g[1] if is_row else g[0] for g in group])
        anch = majority([g[2] for g in group])
        vals = sorted((int(t.replace("\u2212", "-")),
                       (x if is_row else y)) for x, y, an, t in group)
        at = fit(vals)
        lo, hi = vals[0][0], vals[-1][0]
        for v in range(lo, hi + 1):
            if v == 0:
                continue
            pos = at(v)
            t = str(v).replace("-", "\u2212")
            x, y = (pos, fixed) if is_row else (fixed, pos)
            out.append(f'<text x="{x:.0f}" y="{y:.0f}" font-size="10" '
                       f'text-anchor="{anch}">{t}</text>')
    for x, y, an, t in got:
        if t == "O":
            out.append(f'<text x="{x:.0f}" y="{y:.0f}" font-size="10" '
                       f'text-anchor="{an}">O</text>')
    layers = (f'<g font-family="system-ui,sans-serif" stroke="#fff" stroke-width="3" '
              f'stroke-linejoin="round" fill="none" aria-hidden="true">'
              f'{"".join(out)}</g>'
              f'<g font-family="system-ui,sans-serif" fill="currentColor" '
              f'fill-opacity=".75">{"".join(out)}</g>')
    svg = svg[:m.start()] + svg[m.end():]
    return svg.replace("</svg>", layers + "</svg>")


def dot(x, y, label=None, dx=0.0, dy=0.0, size=13):
    """A plotted point and, optionally, its name placed by hand.

    `plane` labels its own points, and where that label lands on the tick row it moves
    the NUMBER instead -- which is how round 11 ended up with one x number below the
    axis and the rest above, and the owner's ruling there was that every number stays in
    line. Placing the point's name myself keeps the number row untouched."""
    out = (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="currentColor"/>')
    if label:
        out += haloed(x + dx, y + dy, label, size=size)
    return out


def f_bda18384(svg, q):
    """#5 -- 'The graph is extremely rough. The grid lines are uneven and the 0 is
    overlapping with the x axis. Also ensure the parabola doesn't randomly stop.'

    Every word of that is right and the figure was worse than it looks. Measured: the
    x-axis ran at 40 px per unit and the y NUMBERS at 20, so the two axes were on
    different scales; '0' was printed at y=124 against an axis at y=120, which is the
    overlap; there were horizontal rules at only two of the five heights; the curve ran
    from x=0 to x=4 and stopped dead at both ends; and it passed through (0, 3.7) when
    y = (x-2)^2 - 3 is 1 there. Two more paths sat in the file with stroke-width="0",
    drawing nothing at all.

    Rebuilt through `figure_lib.plane`, so the axes, the numbers, the grid and the curve
    all come off ONE mapping and cannot disagree. The curve is sampled from the function
    and clipped by the plane rather than stopping where a hand-written path ran out.

    THE DASHED AXIS OF SYMMETRY IS GONE, which is more than was asked. The question is
    'which of the following best represents the axis of symmetry' and the figure was
    drawing it -- a vertical dashed line at x=2 with 2 on the axis beneath it. It was
    also struck straight through that 2. The vertex keeps its dot and its name, and the
    grid the reviewer asked for is what a student now reads (2, -3) off."""
    def curve(px):
        pts = []
        x = -1.0
        while x <= 5.0001:
            y = (x - 2.0) ** 2 - 3.0
            if -4.0 <= y <= 4.0:
                pts.append(px(x, y))
            x += 0.1
        d = "M" + "L".join(f"{a:.0f} {b:.0f}" for a, b in pts)
        vx, vy = px(2, -3)
        return (f'<path d="{d}" fill="none" stroke="currentColor" '
                f'stroke-width="2.2"/>' + dot(vx, vy, "vertex", 0, 22, size=11))

    return {"figure_svg": straighten_ticks(
        fl.plane(xr=(-1, 5), yr=(-4, 4), cell=26, extra=curve))}


def f_fd4d2c94(svg, q):
    """#10 of the 09-07 batch -- 'The graph is overall rough. Add axis value scaling
    ticks and grid lines. There is also text overlapping at the "20px" point. The dotted
    line is also not perpendicular as it doesn't form 90 degree angles.'

    The dotted line was not perpendicular and could not be, because the two axes were
    drawn at different scales: P(0,4) sat 80 px up the y-axis at 20 px per unit while
    Q(2,0) sat 80 px along the x-axis at 40. At two different scales a right angle does
    not look like one, and no amount of moving that line would have fixed it.

    Rebuilt through `figure_lib.plane` at one scale both ways, with the ticks and grid
    the note asks for. The 'Each unit = 20px' caption -- the text that was overlapping
    -- goes: a numbered grid says it better, and the number in it was wrong for x.

    THE DOTTED LINE ITSELF IS GONE, which is more than was asked. It was the answer,
    drawn: with both axes finally at one scale a student can read its gradient straight
    off the picture and never do the negative-reciprocal step the question tests. The
    stem asks for 'the line perpendicular to l that passes through the origin' and never
    refers to anything dashed, so nothing in the question needs it."""
    def bits(px):
        # P's name goes to the RIGHT of the axis: at the left it lands in the y
        # number column, which is where 5 sits.
        out = dot(*px(0, 4), "P", 15, -7) + dot(*px(2, 0), "Q", 14, -8)
        lx, ly = px(-1.2, 4.6)
        return out + haloed(lx, ly, "\u2113", size=14,
                            extra=' font-style="italic"')

    return {"figure_svg": straighten_ticks(
        fl.plane(lines=[((0, 4), (2, 0))], xr=(-3, 5), yr=(-3, 5), cell=26, extra=bits))}


def f_a016ffb4(svg, q):
    """#15 of the 09-07 batch -- 'There is slight overlapping with x and y labels, as
    well as no scaling number ticks. Also add more values on the axes to fill up the
    graph.'

    'Fill up the graph' is the important half. The answer is C(10, 0) and the x-axis
    stopped at 8, so the correct answer was off the paper -- a student who wanted to
    check it by looking could not.

    The axes also disagreed with the points drawn on them. The y numbers were spaced 15
    px per unit and put 0 at y=140, while the x-axis line -- which IS y=0 -- was drawn
    at y=110. So B, drawn at y=110 and labelled (2, 0), read as (2, 2) against the
    figure's own numbering.

    Rebuilt through `figure_lib.plane` out to x=12 and y=8, one scale throughout. B's
    name is placed below the axis by hand: left to `plane` it lands in the number row,
    and `plane` answers that by moving the number rather than the name."""
    def bits(px):
        return (dot(*px(2, 6), "A", -13, -4) + dot(*px(2, 0), "B", -14, -8))

    # First quadrant only. Everything in this question is positive, and carrying a -1
    # on each axis put the x row's -1 and the y column's 1 shoulder to shoulder in the
    # corner -- 2 px of overlap, which is what `overlapping_text_labels` is for.
    return {"figure_svg": straighten_ticks(
        fl.plane(segments=[((2, 6), (2, 0))], xr=(0, 12), yr=(0, 8), cell=21,
                 extra=bits))}


def f_df76a602(svg, q):
    """#15 of the 08-29 batch -- 'The graph is highly confusing, the numbers seem messed
    up, there are random mini squares (are they squares or right angle symbols). Polish
    it up entirely.'

    They are right-angle symbols, and the numbers really were messed up. Measured, the
    old net could not be folded: the three rectangles were 100 px wide and 40, 50 and 60
    px tall, so their fold edges came out at 4, 5 and 6 units against a triangle whose
    sides are 3, 4 and 5 -- and each carried a '10' across its middle, which is the
    prism's LENGTH and the one dimension those rectangles did not show. The two
    triangles had legs of 30 and 40 px on a figure otherwise scaled at 10 px per unit,
    so they were drawn at a different scale from the rectangles beside them.

    Redrawn at 9 px per cm throughout as the net a textbook draws: the three rectangles
    stacked, each 10 cm long and 3, 4 and 5 cm deep -- the triangle's three sides
    unrolled -- with the two triangular faces folded off the ends of the middle one,
    whose 4 cm edge is the side they attach along. Only ONE triangle is dimensioned:
    printing the same three numbers on both is what made the old figure unreadable, and
    the rectangles' depths ARE those sides."""
    S = 9.0
    x0, y0 = 120.0, 46.0
    L = 10 * S
    d3, d4, d5 = 3 * S, 4 * S, 5 * S
    body = ['<rect width="300" height="205" fill="none"/>']
    y = y0
    for d in (d3, d4, d5):
        body.append(f'<rect x="{x0:g}" y="{y:g}" width="{L:g}" height="{d:g}" '
                    f'fill="currentColor" fill-opacity=".05" stroke="currentColor" '
                    f'stroke-width="2"/>')
        y += d
    ty = y0 + d3                               # the middle rectangle's top edge
    by = ty + d4                               # and its bottom
    left = [(x0, ty), (x0, by), (x0 - d3, ty)]
    right = [(x0 + L, ty), (x0 + L, by), (x0 + L + d3, ty)]
    for tri in (left, right):
        body.append(polyline(tri, w=2, close=True))
        body.append(right_angle(*tri[0], tri[1], tri[2], size=9))
    body.append(haloed(x0 - 4, ty - 9, "3 cm", size=11, anchor="end"))
    body.append(haloed(x0 + 8, (ty + by) / 2 + 4, "4 cm", size=11, anchor="start"))
    # On the hypotenuse's own outward normal, away from the right angle -- the same
    # rule every other side label in this round is placed by.
    mx, my = (x0 - d3 + x0) / 2, (ty + by) / 2
    body.append(haloed(mx - 14.4, my + 14.8, "5 cm", size=11))
    body.append(haloed(x0 + L / 2, y0 - 10, "10 cm", size=11))
    return {"figure_svg": '<svg width="300" height="205" viewBox="0 0 300 205" '
            'xmlns="http://www.w3.org/2000/svg">' + "".join(body) + "</svg>"}


def f_ac3bb34c(svg, q):
    """#15 of the 09-07 batch -- 'The graph is inaccurate. First, center all of the
    numberings in their respect region. The spinner is actually divided into 6 sections,
    leaving on empty. Revise the question and make all of the sections the correct size
    and amount.'

    Counted off the file, the reviewer is exactly right: two full diameters and two
    extra radii cut the circle into SIX sectors of 36, 54, 54, 36, 90 and 90 degrees,
    with five of them numbered and one blank. The question says five equal sections and
    every one of its three statements is worked out of fifths.

    Redrawn as five sectors of 72 degrees from one loop, each number on its own sector's
    bisector at the same radius, so none of them can be nearer a neighbour's region than
    its own."""
    cx, cy, r = 130.0, 115.0, 92.0
    body = ['<rect width="260" height="230" fill="none"/>',
            f'<circle cx="{cx:g}" cy="{cy:g}" r="{r:g}" fill="none" '
            f'stroke="currentColor" stroke-width="2.5"/>']
    for i in range(5):
        a = math.radians(-90 + i * 72)
        body.append(f'<line x1="{cx:g}" y1="{cy:g}" '
                    f'x2="{cx + r * math.cos(a):.1f}" y2="{cy + r * math.sin(a):.1f}" '
                    f'stroke="currentColor" stroke-width="2"/>')
        mid = math.radians(-90 + i * 72 + 36)
        body.append(f'<text x="{cx + 0.62 * r * math.cos(mid):.1f}" '
                    f'y="{cy + 0.62 * r * math.sin(mid) + 8:.1f}" font-size="22" '
                    f'font-family="Arial,sans-serif" font-weight="bold" '
                    f'text-anchor="middle" fill="currentColor">{i + 1}</text>')
    body.append(f'<circle cx="{cx:g}" cy="{cy:g}" r="5" fill="currentColor"/>')
    return {"figure_svg": '<svg width="260" height="230" viewBox="0 0 260 230" '
            'xmlns="http://www.w3.org/2000/svg">' + "".join(body) + "</svg>"}


def f_d8bc7137(svg, q):
    """#9 of the 08-29 batch -- 'a large proportion of the numbers are overlapped and
    don't make sense. why is there a random 7 after the 100kg value? and most numbers
    still touch the circumference.'

    The 7 is the resting mark the question turns on, and nothing on the dial said so --
    it was a bare numeral sitting between 100 and 0 at no tick of its own. Worse, the
    old scale ran 0 to 100 over about 330 degrees with a gap, so 'halfway around the
    dial (180 degrees)' was not 50 kg on the thing drawn, and the answer only works if
    a whole turn is 100 kg. Every number was inside the rim and touching it.

    Redrawn as one full turn = 100 kg, 3.6 degrees per kilogram: 0 at the top, a major
    tick and a number every 10 kg all the way round, minor ticks every 2, and every
    number OUTSIDE the circle at a fixed radius so none of them can touch it. The
    resting mark at 7 kg gets a tick of its own, its own number and the pointer, so the
    7 the reviewer could not place now names something. A caption states the whole turn,
    because that is the fact the arithmetic rests on."""
    cx, cy, r = 140.0, 132.0, 88.0

    def at(kg, rad):
        a = math.radians(-90 + kg * 3.6)
        return cx + rad * math.cos(a), cy + rad * math.sin(a)

    body = ['<rect width="280" height="285" fill="none"/>',
            f'<circle cx="{cx:g}" cy="{cy:g}" r="{r:g}" fill="currentColor" '
            f'stroke="currentColor" stroke-width="2.5" fill-opacity=".08"/>']
    body.append(strokes([(at(kg, r), at(kg, r - 5)) for kg in range(0, 100, 2)
                         if kg % 10], w=1, op=".6"))
    body.append(strokes([(at(kg, r), at(kg, r - 10)) for kg in range(0, 100, 10)],
                        w=1.8))
    body.append(strokes([(at(7, r), at(7, r - 14))], w=2.2))
    labs = [(x, y + 4, str(kg)) for kg in range(0, 100, 10)
            for x, y in [at(kg, r + 15)]]
    labs += [(x, y + 4, "7") for x, y in [at(7, r + 15)]]
    body.append(numbers(labs, size=11))
    px_, py_ = at(7, r - 22)
    body.append(f'<line x1="{cx:g}" y1="{cy:g}" x2="{px_:.1f}" y2="{py_:.1f}" '
                f'stroke="currentColor" stroke-width="3" stroke-linecap="round"/>')
    body.append(f'<circle cx="{cx:g}" cy="{cy:g}" r="5" fill="currentColor"/>')
    body.append(f'<text x="{cx:g}" y="{cy + r + 48:g}" font-size="11" '
                f'font-family="Arial,sans-serif" text-anchor="middle" '
                f'fill="currentColor">Scale in kg. One full turn = 100 kg.</text>')
    body.append(f'<text x="{cx:g}" y="{cy + r + 34:g}" font-size="11" '
                f'font-family="Arial,sans-serif" text-anchor="middle" '
                f'fill="currentColor">Pointer at rest with nothing on the scale</text>')
    return {"figure_svg": '<svg width="280" height="285" viewBox="0 0 280 285" '
            'xmlns="http://www.w3.org/2000/svg">' + "".join(body) + "</svg>"}


def f_b51e43e6(svg, q):
    """#19 of the 09-07 batch -- 'Same question as question 22 in set 17, ID:
    e30e0186... Also, the 13 cm label should be on dotted line AO, not the chord.'

    Both are right. `9ea1dc86` sits at position 21 of the SAME form and asks for the
    chord AB given OM = 5 and OA = 13; this one asks for the chord AB given an inner
    radius of 5 and an outer radius of 13. Different words, one 5-12-13 triangle, and
    the same answer of 24 twice in one paper.

    Phase 4 could not have caught it -- it compares STEMS, and these two share almost no
    wording. Swept over every form, this is the only pair in the bank where one paper
    holds two questions with the same key and the same numbers in the stem; the other 23
    the sweep turned up share a key like 4 or 2 by coincidence and are worked entirely
    differently.

    RE-CUT ON 8-15-17, which is what round 11 did with `431d4c9b` for the same reason.
    The inner radius is 8 cm, the outer 17 cm, and AB is 30. This question keeps the
    concentric-circles figure, which is the better of the two drawings, and `9ea1dc86`
    keeps the 5-12-13 chord, which is the better-built figure of the two.

    Redrawn at 7 px per cm from the two radii, so the tangent point, the chord's ends
    and the right angle are all derived: A and B are where a 30 cm chord 8 cm from the
    centre of a 17 cm circle actually falls. '17 cm' is now beside OA, on the free side
    away from the inner circle, and nothing is printed on the chord."""
    S = 7.0
    cx, cy = 150.0, 140.0
    R, rr = 17 * S, 8 * S
    half = 15 * S
    ay_ = cy - rr
    A, B, T = (cx - half, ay_), (cx + half, ay_), (cx, ay_)
    body = ['<rect width="300" height="285" fill="none"/>',
            f'<circle cx="{cx:g}" cy="{cy:g}" r="{R:g}" fill="none" '
            f'stroke="currentColor" stroke-width="2"/>',
            f'<circle cx="{cx:g}" cy="{cy:g}" r="{rr:g}" fill="none" '
            f'stroke="currentColor" stroke-width="2"/>',
            polyline([A, B], w=2),
            polyline([(cx, cy), T], w=1.5, dash="5,3"),
            polyline([(cx, cy), A], w=1.5, dash="5,3"),
            right_angle(*T, B, (cx, cy), size=11)]
    for pt in (A, B, T, (cx, cy)):
        body.append(f'<circle cx="{pt[0]:g}" cy="{pt[1]:g}" r="3" '
                    f'fill="currentColor"/>')
    body.append(haloed(A[0] - 11, A[1] - 6, "A", size=13))
    body.append(haloed(B[0] + 11, B[1] - 6, "B", size=13))
    body.append(haloed(T[0], T[1] - 10, "T", size=13))
    body.append(haloed(cx + 11, cy + 5, "O", size=13, anchor="start"))
    body.append(haloed(cx + 9, cy - rr / 2 + 4, "8 cm", size=12, anchor="start"))
    body.append(haloed(70, 116, "17 cm", size=12))
    return {"figure_svg": '<svg width="300" height="285" viewBox="0 0 300 285" '
            'xmlns="http://www.w3.org/2000/svg">' + "".join(body) + "</svg>",
            "stem": "In the figure below, two concentric circles have centre O. The "
                    "radius of the inner circle is 8 cm and the radius of the outer "
                    "circle is 17 cm. Chord AB of the outer circle is tangent to the "
                    "inner circle at point T. What is the length of chord AB?",
            "option_a": "30 cm", "option_b": "34 cm", "option_c": "25 cm",
            "option_d": "15 cm", "correct_answer": "A",
            "explanation": "AB is tangent to the inner circle at T, so OT is "
                           "perpendicular to AB and OT = 8 cm. OA is a radius of the "
                           "outer circle, so OA = 17 cm. In right-angled triangle OTA, "
                           "AT = √(17² − 8²) = √(289 − 64) "
                           "= √225 = 15 cm. A perpendicular from the centre "
                           "bisects a chord, so T is the midpoint of AB and "
                           "AB = 2 × 15 = 30 cm. 34 cm is the outer diameter, "
                           "25 cm adds the two radii, and 15 cm stops at half the "
                           "chord."}


def f_b65a30d0(svg, q):
    """#26 of the 09-07 batch -- 'A table of values should be provided.'

    The stem says 'A table of the value V of a car after t years shows...' and there was
    no table -- just two of its readings quoted in the sentence. The reviewer is asking
    for the thing the question claims to be showing them.

    The table is built around the two readings the question already turns on, so the
    working is unchanged: $15 800 at t=4 and $13 100 at t=5, with $14 000 between them.
    The other four years fall by about the same amount each year, so nothing in the
    table offers a shorter route to the answer than interpolating between those two."""
    rows = [["t (years)", "1", "2", "3", "4", "5", "6"],
            ["Value V ($)", "24 200", "21 300", "18 600", "15 800", "13 100",
             "10 400"]]
    return {"figure_svg": fl.table(rows, col_w=[76] + [44] * 6, size=10.5,
                                  vw=344),
            "stem": "The table below shows the value V of a car after t years. "
                    "Approximately when is the car worth $14 000?"}


# ========================================== questions that needed a calculator
def f_9bc40fa7(svg, q):
    """#30 of the 08-29 batch -- 'Calculator needed to find Root 1200, but still
    possible without by estimating based of answer options.'

    The park's non-parallel sides were 40 m against a 20 m overhang, so the height was
    root 1200 -- 34.64 m, which no student sits a paper working out, and the stem said
    'approximate' to cover it.

    RE-CUT on 15-20-25, so the same reasoning gives a whole number. The overhang is
    still 20 m; the sides are 25 m; the height is exactly 15 m and the area exactly
    1500 square metres, so 'approximate' comes out of the stem as well."""
    return {"stem": "A community park in Perth is designed in the shape of an isosceles "
                    "trapezium. The two parallel sides measure 120 m and 80 m, and the "
                    "two non-parallel sides are each 25 m long. What is the area of the "
                    "park?",
            "option_a": "1200 m²", "option_b": "1500 m²", "option_c": "1800 m²",
            "option_d": "2000 m²", "correct_answer": "B",
            "explanation": "The horizontal overhang at each end is (120 − 80) ÷ 2 = 20 "
                           "m, so the height is √(25² − 20²) = √(625 − 400) = √225 "
                           "= 15 m. Area = ½ × (120 + 80) × 15 = 1500 m². 1200 m² and "
                           "1800 m² treat the park as a rectangle on one parallel side "
                           "or the other, and 2000 m² uses the 20 m overhang as the "
                           "height instead of the 15 m the triangle gives."}


def f_aedf6ec1(svg, q):
    """#23 of the 08-29 batch -- 'The question is possible without calculator but try to
    spread out the values beccause someone trying to approximate teh answer would
    struggle and have to slightly guess, so try leave only one answer in the 11s.'

    700 divided by 110 is 6.36 recurring, which is where the untidy answer came from,
    and two of the four options sat in the 11s so a rough estimate could not separate
    them.

    RE-CUT so both legs divide exactly: 450 km at 90 km/h is 5 hours and 660 km at 110
    km/h is 6 hours. The answer is 11 hours on the nose and the rounding instruction
    goes with it. The other three are 6, 10 hours 5 minutes and 12 hours 20 minutes --
    one in the 11s, as asked, and each of them the answer to a wrong route rather than
    a near miss."""
    return {"stem": "A car travels from Perth towards Broome. The first 450 km are "
                    "driven at an average speed of 90 km/h, and the next 660 km are "
                    "driven at an average speed of 110 km/h. What is the total time "
                    "taken for the journey?",
            "option_a": "12 hours 20 minutes", "option_b": "10 hours 5 minutes",
            "option_c": "11 hours", "option_d": "6 hours", "correct_answer": "C",
            "explanation": "The first leg takes 450 ÷ 90 = 5 hours and the second "
                           "660 ÷ 110 = 6 hours, so the journey takes 5 + 6 = 11 "
                           "hours. 12 hours 20 minutes is the whole 1110 km driven at "
                           "the slower speed and 10 hours 5 minutes is roughly what it "
                           "would take at the faster one; 6 hours is the second leg on "
                           "its own."}


def f_2629c534(svg, q):
    """#6 of the 09-07 batch -- 'The average elevation isn't a clean number. The
    question doesn't specify to round, so the question is inaccurate. Revise the
    statement to state that the student should round the number, or introduce more
    accurate options.'

    330 metres over 3.5 hours is 94.3 m/h and the nearest option was 90, so the question
    had no right answer. The stored explanation knew it: it worked out 94.3, then said
    'since none match exactly', then 'Replacing the weakest distractor (100) with the
    exact value is better' -- the generating model arguing with itself, in the field a
    student reads.

    RE-CUT on 3 hours, so 330 ÷ 3 = 110 exactly. Nothing rounds and the explanation says
    one thing."""
    return {"stem": "A group of friends hiking in the Blue Mountains starts at an "
                    "elevation of 450 metres and reaches a peak at 780 metres above sea "
                    "level. The hike takes 3 hours. What is their average rate of "
                    "vertical ascent in metres per hour?",
            "option_a": "260 metres per hour", "option_b": "110 metres per hour",
            "option_c": "150 metres per hour", "option_d": "330 metres per hour",
            "correct_answer": "B",
            "explanation": "The vertical gain is 780 − 450 = 330 metres and the hike "
                           "takes 3 hours, so the average rate of ascent is "
                           "330 ÷ 3 = 110 metres per hour. 260 divides the height of "
                           "the peak by the time and forgets that the walk started 450 "
                           "m up; 150 divides the starting elevation by the time; and "
                           "330 is the whole climb, which is a distance and not a rate."}


def f_b5a26f4c(svg, q):
    """#29 of the 09-07 batch -- 'A calculator is required.'

    It was: 5000 x 1.15 cubed is 7604.375, which is three multiplications by 1.15 and a
    rounding instruction.

    RE-CUT at 10% a year, where each step is adding a tenth: 5000, 5500, 6050, 6655.
    Nothing rounds. The distractors are the answers to stopping early and to using
    simple interest, which are the two mistakes this question is for."""
    return {"stem": "A kangaroo population in the Australian outback is currently 5000. "
                    "If the population grows by 10% each year, what will the population "
                    "be after 3 years?",
            "option_a": "6500", "option_b": "6050", "option_c": "6655",
            "option_d": "5500", "correct_answer": "C",
            "explanation": "Growing by 10% means multiplying by 1.1 each year. After "
                           "one year 5000 × 1.1 = 5500, after two 5500 × 1.1 = 6050, "
                           "and after three 6050 × 1.1 = 6655. 6500 adds 10% of the "
                           "ORIGINAL 5000 three times, which is simple growth rather "
                           "than compound; 6050 and 5500 stop after two years and after "
                           "one."}


def f_071205f1(svg, q):
    """#19 of the 09-07 batch -- 'Calculator needed to evaluate complex compound
    interest formula compounded monthly.'

    It needed one, and more than that: the loan-repayment formula
    PMT = P·r(1+r)^n / ((1+r)^n − 1) with n = 36 is not in any selective entry syllabus.

    RE-CUT to simple interest on the same loan, which is what Financial Mathematics
    asks at this level: 8000 x 6.5% is 520 a year, and 520 x 3 is 1560. The distractors
    are one year, two years, and the total repayment mistaken for the interest."""
    return {"stem": "Chloe takes out a personal loan of $8,000 at a simple interest "
                    "rate of 6.5% per year. She repays the loan in full at the end of 3 "
                    "years. How much interest does she pay altogether?",
            "option_a": "$520", "option_b": "$1,560", "option_c": "$1,040",
            "option_d": "$9,560", "correct_answer": "B",
            "explanation": "One year's interest is 6.5% of $8,000 = 0.065 × 8000 = "
                           "$520. Over 3 years that is 520 × 3 = $1,560. $520 is one "
                           "year and $1,040 is two; $9,560 is the total Chloe hands "
                           "back, which is the loan plus the interest rather than the "
                           "interest."}


def f_14b63a7a(svg, q):
    """#13 of the 09-07 batch -- 'Calculator is likely needed for this question.'

    Two easy multiplications rather than one hard one is the fix, and the question was
    asking for the hard one: 'which value is CLOSEST to' against four options inside $50
    of each other made the exact figure necessary, and the explanation ended 'The
    closest answer is $5,618', which is the generating model's own reasoning in the
    field a student reads -- `leaked_working` fires on it.

    The numbers stay, because 5000 to 5300 to 5618 is two steps of adding 6%, and both
    are done in the explanation now. What changes is that the question asks for the
    amount rather than the nearest option, and the two near-miss distractors are
    replaced by the answers to simple interest and to stopping after one year."""
    return {"stem": "Lachlan deposits $5,000 into an account offering 6% annual "
                    "interest, compounded annually. Using A = P(1 + r)ⁿ, what is the "
                    "total amount in the account after 2 years?",
            "option_a": "$5,618", "option_b": "$5,600", "option_c": "$5,300",
            "option_d": "$5,636", "correct_answer": "A",
            "explanation": "After one year: 6% of 5000 is 300, so A = $5,300. After the "
                           "second year: 6% of 5300 is 318, so A = 5300 + 318 = $5,618. "
                           "$5,600 adds 6% of the original 5000 twice, which is simple "
                           "interest; $5,300 stops after one year; and $5,636 uses the "
                           "second year's $318 for both years."}


def f_96b2c83f(svg, q):
    """#8 of the 09-08 batch -- 'Calculator needed'.

    1.05 to the eighth power is not something a student works out by hand.

    RE-CUT at 20% a week over 2 weeks, which is 150 to 180 to 216. The distractors are
    one week, adding a flat 20% of the starting weight twice, and reading the index as
    a multiplier."""
    return {"stem": "A koala joey named Gumdrop was born at a wildlife sanctuary near "
                    "Port Macquarie. Its weight is modelled by W(t) = 150 × (1.2)ᵗ, "
                    "where W is the weight in grams and t is the number of weeks since "
                    "birth. What is Gumdrop's estimated weight after 2 weeks?",
            "option_a": "216 grams", "option_b": "180 grams", "option_c": "210 grams",
            "option_d": "360 grams", "correct_answer": "A",
            "explanation": "W(2) = 150 × 1.2² = 150 × 1.44 = 216 grams, or in two "
                           "steps: 150 × 1.2 = 180 after one week, then "
                           "180 × 1.2 = 216 after the second. 180 grams stops after one "
                           "week; 210 grams adds 20% of the STARTING 150 g twice; and "
                           "360 grams reads the index as 'multiply by 1.2, then by 2'."}


# ================================== questions that were about method, not maths
def f_f6f40548(svg, q):
    """#10 of the 08-29 batch -- 'This isn't really a quantative of maths question, it
    doesn't fit in this area.'

    'Why does a stem-and-leaf plot show more than a histogram of the same data?' is a
    question about what a display is FOR. Nothing is counted, read or worked out, and
    the four options are four sentences about statistics. In a Maths and Quantitative
    paper a student has 58 seconds a question and expects to be doing arithmetic.

    RE-CUT to the same topic done rather than described: here is a stem-and-leaf plot,
    read the median off it. The skill the old question gestured at -- that the plot
    keeps every individual value -- is exactly what makes this answerable, so the
    content is not lost, it is used."""
    rows = [("1", "2  5  8"), ("2", "0  3  3  6  9"), ("3", "1  4  7"),
            ("4", "0  2  5  8")]
    body = ['<rect width="300" height="170" fill="none"/>',
            '<line x1="92" y1="28" x2="92" y2="132" stroke="currentColor" '
            'stroke-width="1.6"/>',
            '<line x1="46" y1="28" x2="240" y2="28" stroke="currentColor" '
            'stroke-width="1.6"/>',
            '<text x="84" y="22" font-family="Arial,sans-serif" font-size="12" '
            'text-anchor="end" fill="currentColor">Stem</text>',
            '<text x="100" y="22" font-family="Arial,sans-serif" font-size="12" '
            'fill="currentColor">Leaf</text>']
    for i, (stem_, leaf) in enumerate(rows):
        y = 50 + i * 22
        body.append(f'<text x="84" y="{y}" font-family="Arial,sans-serif" '
                    f'font-size="13" text-anchor="end" fill="currentColor">'
                    f'{stem_}</text>')
        body.append(f'<text x="102" y="{y}" font-family="Arial,sans-serif" '
                    f'font-size="13" fill="currentColor" '
                    f'xml:space="preserve">{leaf}</text>')
    body.append('<text x="46" y="154" font-family="Arial,sans-serif" font-size="11" '
                'fill="currentColor">Key: 1 | 2 means 12 points</text>')
    return {"figure_svg": '<svg width="300" height="170" viewBox="0 0 300 170" '
            'xmlns="http://www.w3.org/2000/svg">' + "".join(body) + "</svg>",
            "stem": "The stem-and-leaf plot below shows the number of points a netball "
                    "team scored in each of its 15 games this season. What is the "
                    "median number of points scored?",
            "option_a": "23", "option_b": "26", "option_c": "29", "option_d": "31",
            "correct_answer": "C",
            "explanation": "There are 15 scores, so the median is the 8th one in order. "
                           "Counting along the leaves: 12, 15, 18, 20, 23, 23, 26, 29 "
                           "-- the 8th is 29. 23 is the mode, the only score that "
                           "appears twice; 26 and 31 are the scores on either side of "
                           "the middle one, which is what you get by counting to the "
                           "7th or the 9th."}


def f_0a33236b(svg, q):
    """#17 of the 08-29 batch -- 'not exactly a math/quantative reasoning question.'

    Same fault as `f6f40548` in the form before it: 'What does its final entry always
    equal, and what is that column useful for?' is a paragraph about cumulative
    frequency with four paragraphs as options.

    RE-CUT to a cumulative frequency table with the median read out of it, which is what
    the column is for and what the old question could only assert."""
    rows = [["Goals scored", "0", "1", "2", "3", "4", "5"],
            ["Frequency", "3", "6", "9", "11", "7", "4"],
            ["Cumulative frequency", "3", "9", "18", "29", "36", "40"]]
    return {"figure_svg": fl.table(rows, col_w=[120] + [34] * 6, size=10,
                                  vw=332),
            "stem": "The table below shows the number of goals scored in each of 40 "
                    "netball games. What is the median number of goals?",
            "option_a": "3 goals", "option_b": "2 goals", "option_c": "11 goals",
            "option_d": "2.5 goals", "correct_answer": "A",
            "explanation": "With 40 games the median sits between the 20th and the 21st "
                           "game in order. The cumulative frequency reaches 18 after "
                           "the 2-goal row and 29 after the 3-goal row, so both the "
                           "20th and the 21st game are in the 3-goal row and the median "
                           "is 3 goals. 2 goals stops at the row where the running "
                           "total reaches 18, two games short; 11 is the largest "
                           "frequency rather than the score it belongs to; and 2.5 "
                           "averages the scores 2 and 3 as though the two middle games "
                           "fell in different rows."}


def f_b9033a2a(svg, q):
    """#22 of the 09-07 batch -- 'Weird question that will not come in the exam. It is
    more of a thinking question rather than quantative or mathematics.'

    The third of these in the same book. 'Why does experimental probability often differ
    from theoretical probability?' is answered by reading four sentences and picking the
    sensible one.

    RE-CUT to the same idea with numbers in it: the expected count against the observed
    one, and the gap between them. That IS the difference the old question described."""
    return {"stem": "A fair six-sided die is rolled 300 times. It lands on a six 62 "
                    "times. How many more sixes is that than the number expected from "
                    "the theoretical probability?",
            "option_a": "50", "option_b": "62", "option_c": "112", "option_d": "12",
            "correct_answer": "D",
            "explanation": "The theoretical probability of a six is 1/6, so in 300 "
                           "rolls the expected number of sixes is 300 × 1/6 = 50. The "
                           "die actually gave 62, which is 62 − 50 = 12 more than "
                           "expected. 50 is the expected count on its own and 62 the "
                           "observed count on its own; 112 adds the two instead of "
                           "subtracting."}


def f_089855ba(svg, q):
    """#3 of the 09-07 batch -- 'Introduces pre-calculus too early. Too difficult and
    wouldn't come in the real exam.'

    The question asked for the domain and range of d = 12t in set-inequality notation,
    with all four options written as 'Domain 0 <= t <= 3 and range ...'. The reviewer's
    call is the level, not the content, and it is the right call for a paper Year 8s
    sit.

    RE-CUT to the same relation used the way a selective paper uses one -- substitute
    and solve for t. It stays in Relations and Functions and it stays about d = 12t;
    what goes is the notation. The distractors are the two classic slips: reading 0.25
    of an hour as 25 minutes, and reading the remainder of 27 divided by 12 as quarters
    of an hour."""
    return {"stem": "A cyclist rides at a steady 12 km/h, so the distance d km she is "
                    "from home after t hours is given by d = 12t. How long does it take "
                    "her to ride 27 km?",
            "option_a": "2 hours 25 minutes", "option_b": "2 hours 45 minutes",
            "option_c": "3 hours 15 minutes", "option_d": "2 hours 15 minutes",
            "correct_answer": "D",
            "explanation": "Put d = 27 into d = 12t: 27 = 12t, so t = 27 ÷ 12 = 2.25 "
                           "hours. A quarter of an hour is 15 minutes, so that is 2 "
                           "hours 15 minutes. 2 hours 25 minutes reads the 0.25 as 25 "
                           "minutes; 2 hours 45 minutes reads 27 ÷ 12 as 2 remainder 3 "
                           "and calls the 3 three quarter-hours; 3 hours 15 minutes "
                           "subtracts 12 from 27 instead of dividing."}


# ================================================= markup leaking into the stem
def f_3a64f175(svg, q):
    """#7 of the 09-07 batch -- 'The question has some weird ' ' symbols around all of
    the equations and the variables. Get rid of the apostrophes.'

    They are backticks: the generating model wrote the stem in Markdown and the code
    spans came through to the page as literal characters. Five questions in the bank
    carry them and three are live; only this one is flagged, so only this one is
    changed."""
    return {"stem": "Chloe bakes lamingtons for a local fete. The amount of sugar s (in "
                    "cups) needed is related to the amount of flour f (in cups) by the "
                    "equation s = 0.75f + 0.25. Which of the following correctly "
                    "expresses the amount of flour f in terms of sugar s?",
            "option_a": "f = 0.75s − 0.25", "option_b": "f = s ÷ 0.75 − 0.25",
            "option_c": "f = (s − 0.25) ÷ 0.75", "option_d": "f = (s + 0.25) ÷ 0.75"}


def f_0ba593f2(svg, q):
    """#13 of the 09-07 batch -- 'Revise the question to get rid of the hats(^) and make
    it proper exponent form in superscript.'

    Reading it to do that turned up something worse. Option B was
    '4th-root(a² · b² · c³) -- 12th root of a⁸ b⁶ c⁹', which SAYS the answer: the text
    after the dash is option C word for word. The question had two correct answers and
    one of them announced itself.

    The whole expression is rewritten with radicals instead of fractional indices, which
    removes every caret at once and is how a paper would print it. Option B is replaced
    with a real distractor. Bank-wide, 32 questions carry a caret exponent and 22 are
    live; only this one is flagged, so only this one is changed."""
    return {"stem": "For positive real numbers a, b and c, which of the following is "
                    "equivalent to ³√(a²) · √b · ⁴√(c³)?",
            "option_a": "⁶√(a⁴b³c²)", "option_b": "¹²√(a⁴b⁶c³)",
            "option_c": "¹²√(a⁸b⁶c⁹)", "option_d": "¹²√(a⁶b⁴c⁹)",
            "correct_answer": "C",
            "explanation": "³√(a²) is a to the power 2/3, √b is b to the power 1/2 and "
                           "⁴√(c³) is c to the power 3/4. Written over a common "
                           "denominator of 12 those are 8/12, 6/12 and 9/12, so the "
                           "product is the twelfth root of a⁸ · b⁶ · c⁹. ⁶√(a⁴b³c²) "
                           "gets a and b right but leaves c as a cube root; the other "
                           "two put the three numerators on the wrong letters."}


def f_47205a3c(svg, q):
    """#23 of the 08-29 batch -- 'Honestly this question feels slighlty familiar check
    if this is or if there are any duplicates.'

    Checked, and it is not a duplicate: the nearest question in the whole bank scores
    0.86 against it and is an NSW one about netball with a different answer, and the
    nearest VIC one is 0.82, in a different form, about a chart, answer 78.

    What IS familiar is the opening. Twenty-four questions in the bank begin 'Using the
    table/chart/histogram/summary shown below' -- the reviewer has been meeting the same
    sentence all week. No single form holds two of them, so no student ever meets it
    twice in one paper, and the other 23 are left alone.

    This one is reworded, which it needed anyway: the old stem never said what the table
    was OF, so a reader had to work that out from the picture before they could start."""
    return {"stem": "The two-way table below shows whether the Year 8 and Year 9 "
                    "students surveyed play a sport. How many students were surveyed "
                    "altogether?"}


def f_f27e0d63(svg, q):
    """#15 of the 08-29 batch -- 'there are weird $ symbols and the x +2 is overlapping
    with teh side.'

    Both. The stem reads 'length $(2x + 1)$ cm and width $(x + 2)$ cm' -- LaTeX maths
    delimiters printed as dollar signs in a question about a rectangle's dimensions,
    where a reader's first guess is money. This is the question round 9 measured, found
    and deliberately LEFT ALONE because it was already live and approved; the reviewer
    has now flagged it, so it is in scope.

    The label was over the side because the rectangle was 210 by 100 for a shape that is
    11 by 7 -- a ratio of 2.1 against 1.57 -- so it ran out to x=250 and the width label
    centred at 268 reached back to 237. Redrawn at 14 px per unit, so the picture is the
    shape the algebra describes and both labels sit clear outside it."""
    U = 14.0
    x0, y0 = 46.0, 34.0
    w, h = 11 * U, 7 * U
    body = ['<rect width="300" height="170" fill="none"/>',
            f'<rect x="{x0:g}" y="{y0:g}" width="{w:g}" height="{h:g}" '
            f'fill="currentColor" fill-opacity=".05" stroke="currentColor" '
            f'stroke-width="2"/>']
    for cx_, cy_ in ((x0, y0), (x0 + w, y0), (x0, y0 + h), (x0 + w, y0 + h)):
        sx = 11 if cx_ == x0 else -11
        sy = 11 if cy_ == y0 else -11
        body.append(polyline([(cx_ + sx, cy_), (cx_ + sx, cy_ + sy),
                              (cx_, cy_ + sy)], w=1.2, op=".75"))
    body.append(haloed(x0 + w / 2, y0 - 11, "(2x + 1) cm", size=13))
    body.append(haloed(x0 + w + 11, y0 + h / 2 + 4, "(x + 2) cm", size=13,
                       anchor="start"))
    return {"figure_svg": '<svg width="300" height="170" viewBox="0 0 300 170" '
            'xmlns="http://www.w3.org/2000/svg">' + "".join(body) + "</svg>",
            "stem": "In the figure below, a rectangle has length (2x + 1) cm and width "
                    "(x + 2) cm. If the perimeter is 36 cm, what is the value of x?"}


def f_04d46d74(svg, q):
    """#24 of the 09-07 batch -- 'The difference is 0.6 repeating. Revise the question
    to state round or give a more accurate answer options.'

    Exactly right. The six readings 11, 11, 14, 18, 21 and 25 total 100, so the mean is
    16.666..., the median is 16, and the difference is two thirds -- offered as '0.7',
    which is not the answer to the question asked.

    RE-CUT by moving the last reading from 25 to 27. The total becomes 102, the mean is
    exactly 17, the median is still 16 and the difference is exactly 1. The two
    distractors that matter are unchanged in kind: the mean and the median themselves,
    which is the mistake this question is for."""
    return {"stem": "Six readings are 11, 11, 14, 18, 21 and 27. What is the difference "
                    "between the mean and the median?",
            "option_a": "16", "option_b": "1", "option_c": "17", "option_d": "16.5",
            "correct_answer": "B",
            "explanation": "The six readings total 102, so the mean is 102 ÷ 6 = 17. In "
                           "order the two middle readings are 14 and 18, so the median "
                           "is (14 + 18) ÷ 2 = 16. The difference is 17 − 16 = 1. 17 "
                           "and 16 are the two statistics themselves rather than the "
                           "gap between them, and 16.5 is halfway between them."}


# =================================================================== the driver
REPAIRS = {
    "7c472f4d": f_7c472f4d, "b445f197": f_b445f197, "ef761fd8": f_ef761fd8,
    "8cebedb1": f_8cebedb1, "bda18384": f_bda18384, "f6f40548": f_f6f40548,
    "b84412bc": f_b84412bc, "df76a602": f_df76a602, "47205a3c": f_47205a3c,
    "9bc40fa7": f_9bc40fa7, "f27e0d63": f_f27e0d63, "0a33236b": f_0a33236b,
    "117dde83": f_117dde83, "aedf6ec1": f_aedf6ec1, "d8bc7137": f_d8bc7137,
    "2629c534": f_2629c534, "fd4d2c94": f_fd4d2c94, "ac3bb34c": f_ac3bb34c,
    "14b90a3c": f_14b90a3c, "17e21920": f_17e21920, "b65a30d0": f_b65a30d0,
    "b5a26f4c": f_b5a26f4c, "089855ba": f_089855ba, "3a64f175": f_3a64f175,
    "a016ffb4": f_a016ffb4, "b9033a2a": f_b9033a2a, "071205f1": f_071205f1,
    "04d46d74": f_04d46d74, "0ba593f2": f_0ba593f2, "14b63a7a": f_14b63a7a,
    "9ea1dc86": None, "b51e43e6": f_b51e43e6, "96b2c83f": f_96b2c83f,
}

FIELDS = ("stem", "option_a", "option_b", "option_c", "option_d", "correct_answer",
          "explanation", "figure_svg")


def findings(row):
    """Every check that fires on one question, figure checks included."""
    out = set()
    svg = row.get("figure_svg")
    if svg:
        for n in FIG_CHECKS:
            try:
                if getattr(qc, n)(svg):
                    out.add(n)
            except Exception as exc:                             # noqa: BLE001
                out.add(f"{n}:raised {exc.__class__.__name__}")
    for n in Q_CHECKS:
        try:
            r = getattr(qc, n)(row)
        except Exception as exc:                                 # noqa: BLE001
            out.add(f"{n}:raised {exc.__class__.__name__}")
            continue
        # These three answer True for GOOD. Everything else answers True for a problem.
        if n in ("options_distinct", "options_distinct_by_value",
                 "plotted_geometry_matches_stem"):
            if r is False:
                out.add(n)
        elif r:
            out.add(n)
    return out


def read_csv():
    import csv
    with CSV.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--only", help="comma-separated short ids, for working on one")
    args = ap.parse_args()

    flags = read_csv()
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    record, refused, changed = [], [], 0
    for f in flags:
        qid = f["qbank_id"]
        short = qid[:8]
        if args.only and short not in args.only.split(","):
            continue
        fn = REPAIRS.get(short, "missing")
        if fn == "missing":
            refused.append((short, "no repair written"))
            continue
        row = dict(con.execute("SELECT * FROM questions WHERE id=?", (qid,)).fetchone())
        if fn is None:                       # deliberately left as it is
            record.append({"id": qid, "form": f["form_id"], "pos": f["form_position"],
                           "note": f["note"], "action": "left as it is",
                           "fields": []})
            continue
        before = findings(row)
        new = fn(row.get("figure_svg"), row)
        after_row = dict(row)
        after_row.update(new)
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
