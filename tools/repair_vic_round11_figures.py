#!/usr/bin/env python3
"""VIC round 11: the sixteen questions Alaan Q flagged on the rounds 9-10 page.

The 2026-09-03 return covers all 95 questions repaired in rounds 9 and 10. Seventy-nine
came back with no comment, which is a pass. Sixteen carry a note and are repaired here.
Nine of the sixteen are figures round 10 changed, so more than half of this round is my
own work coming back.

Most of the notes are one of two things: a chart with no y-axis scale or no gridlines,
and a number sitting somewhere it should not. Those are done as written. Six are not:

  0e77976c  the stem, the figure and the key described three different shapes
  431d4c9b  a near-duplicate of ef7b9ff2, same numbers and same answer; re-cut
  bed54cfb  a chord whose ends stopped short of the circle it is drawn in
  5edd52c3  a right-angle mark hanging off the line, because the point it marks was
            not on that line
  ccac7c88  bars drawn at three different scales, which only showed up once the y-axis
            the reviewer asked for was put on
  7961f672  a straight revert: round 10's fix reads worse than what it replaced, and
            the reviewer says so

Every figure is rendered and looked at before it is applied, and every question's full
check state is compared before and after: a question that would gain a finding is
refused rather than written.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_vic_round11_figures
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_vic_round11_figures --apply
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
    FIG_CHECKS, Q_CHECKS, arc, halo, line, poly, polyline, right_angle_mark,
    sub1, subn, txt, unit, wrap)

DB = ROOT / "run_data/db/qbank.db"
BEFORE = ROOT / "run_data/db/qbank.db.bak-round10-133407"
RECORD = ROOT / "run_data/output/vic_round11_figures.json"


def gridlines(x0, x1, ys, op=".16"):
    """One faint rule per y, drawn as a single path.

    Four of the sixteen notes ask for these in the same words -- 'draw some horizontal
    grid lines ... for professionalism and readability' -- so they are drawn the same
    way in all four: at the tick heights, never between them, and spanning the plot
    from the axis to the far end."""
    d = "".join(f"M{x0:g} {y:g}H{x1:g}" for y in ys)
    return (f'<path d="{d}" stroke="currentColor" stroke-opacity="{op}" '
            f'stroke-width="1" fill="none"/>')


# ============================================================ the four bar charts
def f_5f8121d8(svg, q):
    """#13 -- 'there is no need for a 0 in the y-axis labels. Instead add some y-axis
    numbering and horizontal grid lines to improve the bar chart and make the 0
    sensible.'

    The axis carried a single '0' sitting 35 px left of the axis line and nothing else,
    so it named no scale at all. The bars are drawn at 10 px per goal, correctly, so a
    tick every 4 goals fits them exactly: 0, 4, 8, 12, with a rule at each and the
    numbers in one column. The 0 now means something."""
    base, per = 175.0, 10.0
    ys = [base - v * per for v in (4, 8, 12)]
    add = gridlines(45, 285, ys)
    for v in (0, 4, 8, 12):
        y = base - v * per
        add += line(41, y, 45, y, w=1).replace("currentColor", "#1a1a2a")
        add += (f'<text x="36" y="{y + 4:g}" font-family="Arial" font-size="10" '
                f'fill="#1a1a2a" text-anchor="end">{v}</text>')
    s = sub1(svg, "<text x='5' y='178' font-size='10' fill='#1a1a2a' "
                  "font-family='Arial'>0</text>", "", "5f8121d8-a")
    # the axis ran 45 px above the top of the scale with nothing on it
    s = sub1(s, "<line x1='40' y1='10' x2='40' y2='175'",
             "<line x1='40' y1='45' x2='40' y2='175'", "5f8121d8-b")
    # the grid goes in behind everything, straight after the opening tag
    i = s.index(">") + 1
    s = s[:i] + add + s[i:]
    # and the numbers on top of the bars get a halo, since a rule now runs behind them
    for lab, x, y in (("6", 65.0, 112.0), ("10", 110.0, 72.0), ("7", 155.0, 102.0),
                      ("12", 200.0, 52.0), ("5", 245.0, 122.0)):
        t = (f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="11" '
             f'fill="#1a1a2a" text-anchor="middle">{lab}</text>')
        s = sub1(s, t, halo(t) + t, f"5f8121d8-{lab}")
    return {"figure_svg": s}


def f_660a2278(svg, q):
    """#35 -- 'draw some horizontal grid lines aligning with the y-axis value ticks'.

    This chart already had its numbers and its ticks, at 4 px per student, and they
    agree with the bars. Only the rules were missing."""
    base, per = 175.0, 4.0
    add = gridlines(45, 285, [base - v * per for v in (10, 20, 30, 40)])
    i = svg.index("<line")
    return {"figure_svg": svg[:i] + add + svg[i:]}


def f_ccac7c88(svg, q):
    """#34 -- 'draw some horizontal grid lines and y-axis values aligning with the grid
    lines'.

    Putting a scale on this chart is what showed the bars were not on one. Measured
    against a baseline of 180: 80 students is drawn 80 px, 100 is drawn 125, 70 is
    drawn 63 and 50 is drawn 50 -- 1.0, 1.25, 0.9 and 1.0 px per student. Against a
    real axis, two of the five bars would read wrong.

    Redrawn at 1.2 px per student throughout, with a tick and a rule every 20. The
    readings are unchanged: 80, 100, 70, 50, 100, so swimming and AFL are 180 of 400,
    which is 45%."""
    vals = [("Swim", 80), ("AFL", 100), ("Bball", 70), ("Tennis", 50), ("Soccer", 100)]
    base, per = 180.0, 1.2
    body = ['<rect width="300" height="220" fill="none"/>',
            gridlines(45, 290, [base - v * per for v in (20, 40, 60, 80, 100)]),
            line(45, 50, 45, 180, w=1.5), line(45, 180, 290, 180, w=1.5)]
    for v in (0, 20, 40, 60, 80, 100):
        y = base - v * per
        body.append(line(41, y, 45, y, w=1))
        body.append(txt(37, y + 4, str(v), 9, anchor="end", family="sans-serif"))
    for i, (name, v) in enumerate(vals):
        x = 55 + i * 45
        body.append(f'<rect x="{x}" y="{base - v * per:g}" width="30" '
                    f'height="{v * per:g}" fill="currentColor" fill-opacity=".18"/>')
        body.append(txt(x + 15, 197, name, 9, family="sans-serif"))
        lab = txt(x + 15, base - v * per - 4, str(v), 9, family="sans-serif")
        body.append(halo(lab) + lab)
    body.append('<text x="16" y="112" font-family="Arial,sans-serif" font-size="11" '
                'fill="currentColor" text-anchor="middle" '
                'transform="rotate(-90 16 112)">Number of students</text>')
    body.append(txt(167, 213, "Sport", 11))
    return {"figure_svg": wrap("".join(body), "0 0 300 220")}


def f_64404632(svg, q):
    """#80 -- 'add some horizontal grid lines upon the y-axis values. Increase the font
    size and center the axes labels.'

    The tick marks were 3 px off the scale the bars use -- the 25 tick sat where 22.9
    is -- so a rule drawn on them would have been wrong. Redrawn with ticks, rules and
    numbers all on the bars' own scale of 1.4 px per pie.

    Every label goes from 9 px to 11, which the four club names do not fit at the old
    spacing: 'Collingwood' at 11 px is wider than the 55 px between bar centres and ran
    into its neighbours on both sides. The bars are dealt on a 60 px pitch now, so the
    names fit at the larger size -- 64 px apart, measured by rendering the sheet and
    looking, not by the width model. Readings unchanged: 85, 70, 65, 70."""
    clubs = [("Richmond", 85, "#e8a040"), ("Carlton", 70, "#4a90d9"),
             ("Collingwood", 65, "#d94a4a"), ("Essendon", 70, "#4ad94a")]
    base, per = 175.0, 1.4
    ink = "#1a1a2a"
    body = ['<rect width="304" height="225" fill="white"/>',
            gridlines(45, 292, [base - v * per for v in (25, 50, 75, 100)]),
            f'<line x1="45" y1="30" x2="45" y2="175" stroke="{ink}" stroke-width="2"/>',
            f'<line x1="45" y1="175" x2="292" y2="175" stroke="{ink}" stroke-width="2"/>']
    for v in (0, 25, 50, 75, 100):
        y = base - v * per
        if v:
            body.append(f'<line x1="41" y1="{y:g}" x2="45" y2="{y:g}" stroke="{ink}" '
                        f'stroke-width="1"/>')
        body.append(f'<text x="37" y="{y + 4:g}" font-family="Arial" font-size="11" '
                    f'fill="{ink}" text-anchor="end">{v}</text>')
    for i, (name, v, col) in enumerate(clubs):
        x, h = 51 + i * 64, v * per
        body.append(f'<rect x="{x}" y="{base - h:g}" width="46" height="{h:g}" '
                    f'fill="{col}" stroke="{ink}" stroke-width="1"/>')
        body.append(f'<text x="{x + 23}" y="192" font-family="Arial" font-size="11" '
                    f'fill="{ink}" text-anchor="middle">{name}</text>')
        lab = (f'<text x="{x + 23}" y="{base - h - 5:g}" font-family="Arial" '
               f'font-size="11" fill="{ink}" text-anchor="middle">{v}</text>')
        body.append(halo(lab) + lab)
    body.append(f'<text x="12" y="102" font-family="Arial" font-size="11" fill="{ink}" '
                f'text-anchor="middle" transform="rotate(-90 12 102)">Pies sold</text>')
    body.append(f'<text x="168" y="214" font-family="Arial" font-size="11" '
                f'fill="{ink}" text-anchor="middle">Football Club</text>')
    return {"figure_svg": ('<svg viewBox="0 0 304 225" '
                           'xmlns="http://www.w3.org/2000/svg" '
                           'style="background:white">' + "".join(body) + '</svg>')}


# =========================================================== numbers put back or taken
def f_a30aed4e(svg, q):
    """#32 -- 'there is no need for a number 0 at the origin ... Also, values -2 and 3
    on the x-axis are missing. Replace them.'

    The 0 goes. The other two are missing because something was drawn through them: the
    line y = x + 2 crosses the x-axis at exactly x = -2, and the line x = 3 runs the
    whole height of the plot through where its own number belongs. So the numbers can
    only come back if the two lines stop short of the number row, and they now do --
    y = x + 2 is drawn from its x-intercept upward, and x = 3 from just below the axis
    upward. Both still show the intersection the question asks about.

    That also lets the -3 come back down into line: it had been lifted 25 px above the
    row to dodge the same line."""
    s = subn(svg, '<text x="129" y="209" font-size="10" text-anchor="end">O</text>',
             "", 2, "a30aed4e-a")
    s = sub1(s, '<line x1="42" y1="242" x2="258" y2="26"',
             '<line x1="90" y1="194" x2="258" y2="26"', "a30aed4e-b")
    s = sub1(s, '<line x1="210" y1="266" x2="210" y2="26"',
             '<line x1="210" y1="198" x2="210" y2="26"', "a30aed4e-c")
    for old, new in (
            ('<text x="66" y="185" font-size="10" text-anchor="middle">−3</text>',
             '<text x="66" y="210" font-size="10" text-anchor="middle">−3</text>'),
            ('<text x="114" y="210" font-size="10" text-anchor="middle">−1</text>',
             '<text x="90" y="210" font-size="10" text-anchor="middle">−2</text>'
             '<text x="114" y="210" font-size="10" text-anchor="middle">−1</text>'),
            ('<text x="186" y="210" font-size="10" text-anchor="middle">2</text>',
             '<text x="186" y="210" font-size="10" text-anchor="middle">2</text>'
             '<text x="210" y="210" font-size="10" text-anchor="middle">3</text>')):
        n = s.count(old)
        assert n in (1, 2), f"a30aed4e: {old[:40]} appears {n} times"
        s = s.replace(old, new)
    return {"figure_svg": s}


def f_42e248db(svg, q):
    """#85 -- 'the -5 still feels out of place. Move it a little higher and to the
    right so it looks more symmetrical and aligned with the other values.'

    It cannot go back into the left-hand column: the plotted line ends at (-1, -5),
    which is exactly where that number sits. Moved 6 px right and 8 px up, as asked."""
    return {"figure_svg": subn(
        svg, '<text x="94" y="266" font-size="10" text-anchor="start">−5</text>',
        '<text x="100" y="258" font-size="10" text-anchor="start">−5</text>', 2,
        "42e248db")}


def f_c0526d7f(svg, q):
    """#91 -- 'just delete the 1 on the y-axis that is found inside the triangle ...
    students can still infer the value line AB is sitting on.'

    Round 10 moved it to the far side of the axis because side AB runs the width of the
    figure at that height and covers every other spot. Deleting it is the better answer
    and the reviewer's call. The remaining numbers are still evenly spaced, so the axis
    still reads."""
    return {"figure_svg": subn(
        svg, '<text x="196" y="166" font-size="10" text-anchor="start">1</text>', "", 1,
        "c0526d7f")}


def f_7961f672(svg, q):
    """#90 -- 'the updated graph looks far worse. The numbers are all misaligned and
    some are duplicating itself. Revert back to the "before" graph and simply delete
    any number that is being overlapped as a student can easily infer what value is
    being touched.'

    Done exactly. Round 10 moved the whole y column outside the square and dropped two
    x numbers below it, to keep every number at its own tick; the reviewer would rather
    have four numbers missing than seven moved. The pre-round-10 figure is restored
    from the backup and the four numbers the square's sides ran through -- y 3 and -2,
    x -1 and 4 -- are removed.

    The axis still reads: what is left is evenly spaced, 30 px per unit on both."""
    old = sqlite3.connect(BEFORE)
    row = old.execute("SELECT figure_svg FROM questions WHERE id = ?",
                      (q["id"],)).fetchone()
    assert row, "7961f672: not in the round-10 backup"
    s = row[0]
    for lab in ('<text x="89" y="56" font-size="10" text-anchor="end">3</text>',
                '<text x="89" y="206" font-size="10" text-anchor="end">−2</text>',
                '<text x="68" y="158" font-size="10" text-anchor="middle">−1</text>',
                '<text x="218" y="158" font-size="10" text-anchor="middle">4</text>'):
        s = subn(s, lab, "", 1, "7961f672-" + lab[-12:])
    return {"figure_svg": s}


def f_c76f4d12(svg, q):
    """#88 -- 'the circular point E is a semi-circle, not a normal circle like the other
    points. Revise by making the points smaller dots and moving the letters to be
    further from the x and y axes.'

    E is a whole circle. It looks like half of one because round 10 moved the letter E
    to x = 138 to get it off the y-axis, and at 13 px the glyph starts at 133.6 -- on
    top of the right half of the dot, which is centred at 133. The letter is painting
    out half the marker.

    E goes below its own point, clear of the dot, the axis and side EF. D and F move
    further from the axes as asked, and all three dots go from 4.5 px to 3."""
    s = svg
    for cx, cy in ((95, 41), (133, 98), (76, 117)):
        s = sub1(s, f'<circle cx="{cx}" cy="{cy}" r="4.5" fill="currentColor"/>',
                 f'<circle cx="{cx}" cy="{cy}" r="3" fill="currentColor"/>',
                 f"c76f4d12-dot{cx}")
    old_e = '<text x="138" y="103" font-size="13" text-anchor="middle">E</text>'
    lab = '<text x="133" y="116" font-size="13" text-anchor="middle">E</text>'
    s = sub1(s, halo(old_e) + old_e, halo(lab) + lab, "c76f4d12-E")
    s = sub1(s, '<text x="64" y="132" font-size="13" text-anchor="middle">F</text>',
             '<text x="64" y="130" font-size="13" text-anchor="end">F</text>',
             "c76f4d12-F")
    return {"figure_svg": s}


# ================================================================ geometry and layout
def f_0896c838(svg, q):
    """#14 -- 'the 52 degree value has moved slightly too far away from Angle A.'

    Round 9 pushed it out to 61 px from the vertex to clear the hypotenuse. The sector
    is 37 degrees wide, so the clearance grows with the radius and there is a limit to
    how close it can come; 44 px is as near as it goes with the whole label inside."""
    return {"figure_svg": sub1(
        svg, '<text x="84.0" y="159.0" font-family="Arial,sans-serif" font-size="13" '
             'fill="currentColor" text-anchor="middle">52°</text>',
        txt(68, 164, "52°", 13), "0896c838")}


def f_bed54cfb(svg, q):
    """#36 -- 'the chord AB doesn't actually reach the circumference.'

    It did not: the circle has radius 90 about (140, 120) and the chord ran from
    (68, 168) to (212, 168), whose ends are 86.5 from the centre -- 3.5 px inside the
    rim.

    Rather than stretch the chord where it was, the whole figure is put on one scale.
    At 9 px per cm the radius 10 cm is the 90 px already drawn, and a chord of 16 cm is
    144 px, which sits at exactly 54 px from the centre -- 6 cm, the answer. So the
    chord moves down to y = 174, where its ends land on the circle exactly, and every
    length in the picture is now the length its label claims."""
    C, r = (140.0, 120.0), 90.0
    A, B = (68.0, 174.0), (212.0, 174.0)
    F = (140.0, 174.0)
    assert abs(math.dist(C, A) - r) < 1e-9 and abs(math.dist(C, B) - r) < 1e-9
    body = ('<rect width="280" height="240" fill="none"/>'
            + f'<circle cx="140" cy="120" r="90" fill="currentColor" '
              f'stroke="currentColor" stroke-width="2" fill-opacity=".18"/>'
            + line(*A, *B)
            + line(*C, *F, w=1.8, dash="5,4")
            + line(*C, *A, w=1.5, dash="4,3")
            + right_angle_mark(F, C, B, 14)
            + '<circle cx="140" cy="120" r="4" fill="currentColor"/>'
            + txt(126, 114, "O", 13, anchor="end")
            + txt(56, 186, "A", 13, anchor="end")
            + txt(224, 186, "B", 13, anchor="start")
            + txt(132, 150, "d", 11, anchor="end")
            + txt(94, 134, "10 cm", 11)
            + txt(140, 196, "16 cm", 11))
    return {"figure_svg": wrap(body, "0 0 280 240")}


def f_5edd52c3(svg, q):
    """#47 -- 'the right angle symbol is slightly passing through line OB.'

    It hangs off the line because D is not on the line. Road OB is drawn at 52.5
    degrees while the stem says 55, and D was placed by hand at (102, 105), which is
    7 px above the road. The mark was then drawn about a point in mid-air.

    Redrawn from the stem's own numbers at 0.8 px per metre: OB at exactly 55 degrees,
    C at 200 m along OA, and D derived as the foot of the perpendicular from C onto OB
    -- which lands at 91.8 px from O, that is 114.7 m, the keyed answer of 114 m. The
    right-angle mark is then built from the two rays at D and cannot leave the line."""
    O, A = (50.0, 180.0), (270.0, 180.0)
    ux, uy = math.cos(math.radians(55)), -math.sin(math.radians(55))
    B = (O[0] + 200 * ux, O[1] + 200 * uy)
    C = (210.0, 180.0)
    t = (C[0] - O[0]) * ux + (C[1] - O[1]) * uy
    D = (O[0] + t * ux, O[1] + t * uy)
    assert abs((C[0] - D[0]) * ux + (C[1] - D[1]) * uy) < 1e-9, "CD not perpendicular"
    body = (line(*O, *A) + line(*O, *B)
            + line(*C, *D, w=1.8, dash="6,3")
            + right_angle_mark(D, O, C, 12)
            + arc(O[0], O[1], 20, A, B)
            + txt(36, 194, "O", 13, anchor="start")
            + txt(214, 196, "C", 13, anchor="start")
            + txt(94, 96, "D", 13, anchor="end")
            + txt(B[0] + 6, B[1] - 4, "B", 13, anchor="start")
            + txt(272, 194, "A", 13, anchor="start")
            + txt(130, 197, "200 m", 12)
            + txt(80, 168, "55°", 12)
            + txt(70, 134, "OD=?", 12, anchor="end"))
    return {"figure_svg": wrap(body, "0 -0.6 300 220.6")}


def f_c5daaa49(svg, q):
    """#70 -- 'create a little more distance between the rectangles as the 5 cm label
    between rectangles is vague.'

    R's width label sat in the 35 px gap between the two rectangles, close enough to S
    to read as S's. S moves 40 px right and the canvas grows to hold it, so there are
    43 px of empty space between R's label and S."""
    s = svg
    for old, new in (("<rect x=\"165\" y=\"55\"", "<rect x=\"205\" y=\"55\""),
                     ("<text x=\"220\" y=\"85\"", "<text x=\"260\" y=\"85\""),
                     ("<text x=\"282\" y=\"85\"", "<text x=\"322\" y=\"85\""),
                     ("<line x1=\"165\" y1=\"120\" x2=\"275\" y2=\"120\"",
                      "<line x1=\"205\" y1=\"120\" x2=\"315\" y2=\"120\""),
                     ("points=\"165,120 171,117 171,123\"",
                      "points=\"205,120 211,117 211,123\""),
                     ("points=\"275,120 269,117 269,123\"",
                      "points=\"315,120 309,117 309,123\""),
                     ("<text x=\"220\" y=\"135\"", "<text x=\"260\" y=\"135\""),
                     ("<text x=\"150\" y=\"20\"", "<text x=\"175\" y=\"20\""),
                     ('viewBox="0 0 315.36 210"', 'viewBox="0 0 356 210"'),
                     ('width="315"', 'width="356"')):
        s = sub1(s, old, new, "c5daaa49-" + old[:22])
    return {"figure_svg": s}


def f_ebd339c2(svg, q):
    """#74 -- 'move the 15 cm and 8 cm arrows a little closer to the side on each
    rectangle that they are meant to be representing. Push both of them upwards.'

    Both width rules sat on the same line, y = 150, which is 30 px below rectangle A
    and 20 px below rectangle B, so neither read as belonging to the side above it.
    Each rule now sits 14 px under its own rectangle."""
    s = svg
    for x0, x1, old_y, new_y in ((20, 110, 150, 134), (165, 265, 150, 144)):
        s = sub1(s, f'<line x1="{x0}" y1="{old_y}" x2="{x1}" y2="{old_y}"',
                 f'<line x1="{x0}" y1="{new_y}" x2="{x1}" y2="{new_y}"',
                 f"ebd339c2-r{x0}")
        s = sub1(s, f'<polygon points="{x0},{old_y} {x0 + 6},{old_y - 3} '
                    f'{x0 + 6},{old_y + 3}"',
                 f'<polygon points="{x0},{new_y} {x0 + 6},{new_y - 3} '
                 f'{x0 + 6},{new_y + 3}"', f"ebd339c2-a{x0}")
        s = sub1(s, f'<polygon points="{x1},{old_y} {x1 - 6},{old_y - 3} '
                    f'{x1 - 6},{old_y + 3}"',
                 f'<polygon points="{x1},{new_y} {x1 - 6},{new_y - 3} '
                 f'{x1 - 6},{new_y + 3}"', f"ebd339c2-b{x1}")
    s = sub1(s, '<text x="65" y="165" text-anchor="middle" font-size="13"',
             '<text x="65" y="149" text-anchor="middle" font-size="13"',
             "ebd339c2-l15")
    s = sub1(s, '<text x="215" y="165" text-anchor="middle" font-size="13"',
             '<text x="215" y="159" text-anchor="middle" font-size="13"',
             "ebd339c2-l8")
    return {"figure_svg": s}


def f_431d4c9b(svg, q):
    """#66 -- 'this is a duplicate question. Rewrite by changing the values.'

    It is. `ef7b9ff2`, in vic-drill-mq-070, asks the same thing with the same numbers:
    a right-angled triangle with legs 5 cm and 12 cm, a square on the hypotenuse, and
    the same answer of 169. Both are pending, so either could be served; a student
    sitting two drill papers would meet the question twice.

    Re-cut on 8-15-17, which no other question in the pool uses (0b7299a2 has 9-12-15).
    Worked twice: 8² + 15² = 64 + 225 = 289, and 17² = 289. The distractors are the
    three things that go wrong -- squaring only the longer leg, subtracting the squares
    instead of adding, and adding the legs before squaring.

    The figure gains the square the question has always talked about, drawn on the
    hypotenuse; before, it showed only the triangle with the hypotenuse marked '?'."""
    A, B, C = (40.0, 150.0), (130.0, 150.0), (40.0, 102.0)
    ux, uy = unit(*C, *B)
    nx, ny = uy, -ux                                  # outward from the triangle
    L = math.dist(C, B)
    P, Q = (B[0] + nx * L, B[1] + ny * L), (C[0] + nx * L, C[1] + ny * L)
    assert abs(L - 102.0) < 1e-6, f"hypotenuse drawn {L:.2f} px, expected 102"
    body = ('<rect width="260" height="200" fill="none"/>'
            + poly([C, B, P, Q], w=1.8)
            + poly([A, B, C])
            + right_angle_mark(A, B, C, 12)
            + txt(32, 130, "8 cm", 12, anchor="end")
            + txt(85, 170, "15 cm", 12)
            + txt((C[0] + B[0] + P[0] + Q[0]) / 4,
                  (C[1] + B[1] + P[1] + Q[1]) / 4 + 6, "?", 18))
    stem = ("The right-angled triangle below has a shorter leg of 8 cm and a longer leg "
            "of 15 cm. A square is drawn on its hypotenuse, as shown. What is the area "
            "of that square, in square centimetres?")
    expl = ("The square's side is the hypotenuse, so its area is the hypotenuse "
            "squared. By Pythagoras, hypotenuse² = 8² + 15² = 64 + 225 = 289, so the "
            "square has an area of 289 cm² — and the hypotenuse itself is 17 cm, since "
            "17² = 289. Answering 225 squares only the longer leg; 161 subtracts the "
            "squares instead of adding them; 529 adds the two legs first and squares "
            "the total.")
    return {"figure_svg": wrap(body, "0 0 260 200"), "stem": stem, "explanation": expl,
            "option_a": "529", "option_b": "289", "option_c": "161",
            "option_d": "225", "correct_answer": "B"}


def f_0e77976c(svg, q):
    """#75 -- 'there is no need for the arrows and line segment. The figure is also a
    little unclear as the question states two smaller rectangles are cut from the top
    corner, but the figure shows two rectangles being added. Revise the question.'

    The stem, the figure and the key described three different shapes.

      * the STEM says the notches are 3 by 2 and 4 by 2, which leaves 77 - 6 - 8 = 63
      * the EXPLANATION works those same two out and then stops before subtracting
      * the FIGURE is drawn as a U -- one notch in the middle of the top edge, not two
        at the corners -- and carries four numbers, 4, 4, 3 and 2
      * the KEY is 57, which is 77 - 4x3 - 4x2: two corner notches, one 4 by 3 and one
        4 by 2, exactly what the figure's four numbers say

    So the figure's labels and the key agree with each other, and the stem and its
    explanation agree with each other. Going with the key means changing two numbers in
    one sentence; going the other way means changing the key, the four labels and the
    shape. The key stands and the stem is corrected.

    Drawn as the shape the stem now describes, at 16 px per cm, with the two notches
    cut from the top corners and each of their four lengths on the edge it measures.
    The arrowed rule and the stray vertical stub go, as asked; the two overall lengths
    are named without a rule."""
    body = ('<rect width="300" height="220" fill="none"/>'
            + poly([(60, 180), (236, 180), (236, 100), (172, 100), (172, 68),
                    (124, 68), (124, 116), (60, 116)],
                   fill="currentColor", fop=".18")
            + txt(148, 198, "11 cm", 13)
            + txt(246, 128, "7 cm", 13, anchor="start")
            + txt(92, 112, "4 cm", 12) + txt(118, 90, "3 cm", 12, anchor="end")
            + txt(204, 96, "4 cm", 12)
            + txt(180, 80, "2 cm", 12, anchor="start"))
    stem = ("In the figure below, a large rectangle has dimensions 11 cm × 7 cm. A "
            "rectangular notch 4 cm wide and 3 cm tall is cut from the top-left "
            "corner, and another notch 4 cm wide and 2 cm tall is cut from the "
            "top-right corner. What is the area of the remaining shaded shape?")
    expl = ("The large rectangle has area 11 × 7 = 77 cm². The notch cut from the "
            "top-left corner has area 4 × 3 = 12 cm², and the notch cut from the "
            "top-right corner has area 4 × 2 = 8 cm². What is left is "
            "77 − 12 − 8 = 57 cm².")
    return {"figure_svg": wrap(body, "0 0 300 220"), "stem": stem, "explanation": expl}


# ======================================================================= driver
BUILDERS = {
    "0896c838": f_0896c838, "0e77976c": f_0e77976c, "42e248db": f_42e248db,
    "431d4c9b": f_431d4c9b, "5edd52c3": f_5edd52c3, "5f8121d8": f_5f8121d8,
    "64404632": f_64404632, "660a2278": f_660a2278, "7961f672": f_7961f672,
    "a30aed4e": f_a30aed4e, "bed54cfb": f_bed54cfb, "c0526d7f": f_c0526d7f,
    "c5daaa49": f_c5daaa49, "c76f4d12": f_c76f4d12, "ccac7c88": f_ccac7c88,
    "ebd339c2": f_ebd339c2,
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
                    default=ROOT / "review/ui/figure-review-vic-mq-rounds9-10-"
                                   "2026-09-03.json")
    args = ap.parse_args()

    # the round is exactly the cards the reviewer wrote a note against
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
    print(f"findings cleared: {cleared}   "
          f"newly firing: {sum(len(r['newly_firing']) for r in done) or 'none'}")


if __name__ == "__main__":
    main()
