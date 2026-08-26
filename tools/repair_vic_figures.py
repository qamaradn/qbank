#!/usr/bin/env python3
"""Redraw the six figures the VIC reviewer called rough, confusing or inaccurate.

Each is rebuilt from the numbers in its own stem rather than adjusted by eye, so the
picture and the question cannot disagree. Three of them are coordinate plots and get a
shared grid helper: equal scale on both axes, visible gridlines, and points placed by
arithmetic. That combination is what the reviewer asked for three separate times —
"add grid lines", "doesn't resemble a line with a slope of 1", "the spacing of each
point isn't equal".
"""
import argparse
import json
import math
import pathlib
import sqlite3

ROOT = pathlib.Path(__file__).resolve().parents[1]
DB = ROOT / "run_data/db/qbank.db"
RECORD = ROOT / "run_data/output/vic_figure_repairs.json"

C = "currentColor"


def grid(xmin, xmax, ymin, ymax, cell=22, pad=46):
    """A coordinate plane with ONE scale on both axes and gridlines that show it."""
    w = (xmax - xmin) * cell + 2 * pad
    h = (ymax - ymin) * cell + 2 * pad

    def px(x, y):
        return pad + (x - xmin) * cell, pad + (ymax - y) * cell

    body = [f'<rect width="{w}" height="{h}" fill="none"/>']
    # One path for the whole grid. Twenty-five <line> elements pushed these figures past
    # the 3.5 KB the payload budget allows, and they travel to Selectly as data URIs.
    d = []
    for x in range(xmin, xmax + 1):
        x0, y0 = px(x, ymax)
        _, y1 = px(x, ymin)
        d.append(f"M{x0:.0f} {y0:.0f}V{y1:.0f}")
    for y in range(ymin, ymax + 1):
        x0, y0 = px(xmin, y)
        x1, _ = px(xmax, y)
        d.append(f"M{x0:.0f} {y0:.0f}H{x1:.0f}")
    body.append(f'<path d="{"".join(d)}" stroke="{C}" stroke-opacity=".18" '
                f'stroke-width="1"/>')
    ax0, ay0 = px(xmin, 0)
    ax1, ay1 = px(xmax, 0)
    body.append(f'<line x1="{ax0:.0f}" y1="{ay0:.0f}" x2="{ax1:.0f}" y2="{ay1:.0f}" '
                f'stroke="{C}" stroke-width="1.8"/>')
    bx0, by0 = px(0, ymin)
    bx1, by1 = px(0, ymax)
    body.append(f'<line x1="{bx0:.0f}" y1="{by0:.0f}" x2="{bx1:.0f}" y2="{by1:.0f}" '
                f'stroke="{C}" stroke-width="1.8"/>')
    for x in range(xmin, xmax + 1, 2):
        if x == 0:
            continue
        tx, _ = px(x, 0)
        # Bottom margin, not on the axis. With negative coordinates the x-axis runs
        # through the middle of the picture, so labels placed against it land in the
        # data — which is how "-2" ended up printed across the parallelogram's diagonal.
        body.append(f'<text x="{tx:.0f}" y="{h - 8:.0f}" font-size="9" fill="{C}" '
                    f'fill-opacity=".7" text-anchor="middle">{x}</text>')
    for y in range(ymin, ymax + 1, 2):
        if y == 0:
            continue
        _, ty = px(0, y)
        # Tick labels go in the left margin, not beside an interior axis. Sitting next
        # to the axis put "-2" on top of the parallelogram's diagonal; out here nothing
        # drawn in the data area can reach them.
        body.append(f'<text x="{pad - 8:.0f}" y="{ty + 3:.0f}" font-size="9" fill="{C}" '
                    f'fill-opacity=".7" text-anchor="end">{y}</text>')
    # The axis letters. Redrawing these figures yesterday I dropped them, and the check
    # written the next day found all three — a coordinate plane says what it is with x
    # and y, and without them it is just a grid.
    axr, _ = px(xmax, 0)
    _, ayt = px(0, ymax)
    body.append(f'<text x="{axr + 10:.0f}" y="{px(0, 0)[1] + 4:.0f}" font-size="12" '
                f'fill="{C}">x</text>')
    body.append(f'<text x="{px(0, 0)[0] + 6:.0f}" y="{ayt - 8:.0f}" font-size="12" '
                f'fill="{C}">y</text>')
    return body, px, w + 14, h + 6


def wrap(body, w, h):
    return (f'<svg viewBox="0 0 {w:.0f} {h:.0f}" xmlns="http://www.w3.org/2000/svg" '
            f'fill="none" stroke-linejoin="round" stroke-linecap="round">'
            + "".join(body) + '</svg>')


def dot(px, x, y, label=None, dx=6, dy=-6):
    a, b = px(x, y)
    out = [f'<circle cx="{a:.0f}" cy="{b:.0f}" r="3.2" fill="{C}"/>']
    if label:
        out.append(f'<text x="{a + dx:.0f}" y="{b + dy:.0f}" font-size="11" fill="{C}">'
                   f'{label}</text>')
    return out


# ---------------------------------------------------------------- the six figures
def spinner():
    """Four sectors sized by their own probabilities, and NO separate circle outline --
    stroking both was what doubled the circumference. Blue .35, Green .20, Red .25,
    Yellow .20: P(Blue)=0.35 true, P(not Green)=0.8 true, P(Red or Yellow)=0.45 so the
    0.55 claim is false, which is what makes the key 'P and R only'."""
    parts = [("Blue", 0.35), ("Red", 0.25), ("Yellow", 0.20), ("Green", 0.20)]
    assert abs(sum(p for _, p in parts) - 1) < 1e-9
    cx, cy, r = 150.0, 118.0, 84.0
    body, ang = [f'<rect width="300" height="236" fill="none"/>'], -90.0
    for name, p in parts:
        sweep = p * 360
        a0, a1 = math.radians(ang), math.radians(ang + sweep)
        x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
        x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        large = 1 if sweep > 180 else 0
        body.append(f'<path d="M{cx:.1f},{cy:.1f} L{x0:.1f},{y0:.1f} '
                    f'A{r},{r} 0 {large},1 {x1:.1f},{y1:.1f} Z" fill="{C}" '
                    f'fill-opacity=".10" stroke="{C}" stroke-width="1.6"/>')
        mid = math.radians(ang + sweep / 2)
        lx, ly = cx + r * 0.62 * math.cos(mid), cy + r * 0.62 * math.sin(mid)
        body.append(f'<text x="{lx:.0f}" y="{ly - 3:.0f}" font-size="11.5" fill="{C}" '
                    f'text-anchor="middle">{name}</text>')
        body.append(f'<text x="{lx:.0f}" y="{ly + 11:.0f}" font-size="11.5" fill="{C}" '
                    f'text-anchor="middle">{p:.2f}</text>')
        ang += sweep
    return wrap(body, 300, 236)


def arcs():
    """Circle drawn ONCE. The arcs are identified by their end points and labels, not by
    a second stroke over the same path -- that was the 'double lining'. PQ 8 cm and
    QR 12 cm make a semicircle of 20, so the circumference is 40."""
    cx, cy, r = 150.0, 128.0, 82.0
    pts = {"P": 180.0, "Q": 180.0 - 180.0 * (8 / 20), "R": 0.0}
    body = [f'<rect width="300" height="230" fill="none"/>',
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{C}" '
            f'stroke-width="1.8"/>']
    coord = {}
    for name, deg in pts.items():
        a = math.radians(deg)
        x, y = cx + r * math.cos(a), cy - r * math.sin(a)
        coord[name] = (x, y)
        body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.4" fill="{C}"/>')
        ox = -14 if name == "P" else (14 if name == "R" else 0)
        oy = 4 if name != "Q" else -10
        body.append(f'<text x="{x + ox:.0f}" y="{y + oy:.0f}" font-size="12.5" '
                    f'fill="{C}" text-anchor="middle">{name}</text>')
    body.append(f'<circle cx="{cx}" cy="{cy}" r="2.6" fill="{C}"/>')
    body.append(f'<text x="{cx + 8:.0f}" y="{cy + 14:.0f}" font-size="12.5" '
                f'fill="{C}">O</text>')
    for label, deg in (("8 cm", (180 + pts["Q"]) / 2), ("12 cm", pts["Q"] / 2)):
        a = math.radians(deg)
        x, y = cx + (r + 20) * math.cos(a), cy - (r + 20) * math.sin(a)
        body.append(f'<text x="{x:.0f}" y="{y:.0f}" font-size="11.5" fill="{C}" '
                    f'text-anchor="middle">{label}</text>')
    return wrap(body, 300, 230)


def isosceles():
    """AB = AC = 10, BC = 12, so AM = 8. Drawn to scale, with every label placed on the
    outside of the shape it names so none can collide with another."""
    s = 14.0
    bx, cx_ = 150 - 6 * s, 150 + 6 * s
    ay = 40.0
    by = ay + 8 * s
    body = [f'<rect width="300" height="{by + 46:.0f}" fill="none"/>',
            f'<path d="M150,{ay} L{bx},{by} L{cx_},{by} Z" fill="{C}" '
            f'fill-opacity=".05" stroke="{C}" stroke-width="2"/>',
            f'<line x1="150" y1="{ay}" x2="150" y2="{by}" stroke="{C}" '
            f'stroke-width="1.4" stroke-dasharray="5,4"/>',
            f'<path d="M150,{by - 12} h12 v12" fill="none" stroke="{C}" '
            f'stroke-opacity=".7" stroke-width="1.2"/>',
            f'<text x="150" y="{ay - 10:.0f}" font-size="13" fill="{C}" '
            f'text-anchor="middle">A</text>',
            f'<text x="{bx - 12:.0f}" y="{by + 6:.0f}" font-size="13" fill="{C}" '
            f'text-anchor="middle">B</text>',
            f'<text x="{cx_ + 12:.0f}" y="{by + 6:.0f}" font-size="13" fill="{C}" '
            f'text-anchor="middle">C</text>',
            f'<text x="150" y="{by + 20:.0f}" font-size="13" fill="{C}" '
            f'text-anchor="middle">M</text>',
            # side labels sit outside the triangle, clear of the vertex letters
            f'<text x="{(150 + bx) / 2 - 20:.0f}" y="{(ay + by) / 2:.0f}" font-size="12" '
            f'fill="{C}" text-anchor="middle">10 cm</text>',
            f'<text x="{(150 + cx_) / 2 + 20:.0f}" y="{(ay + by) / 2:.0f}" font-size="12" '
            f'fill="{C}" text-anchor="middle">10 cm</text>',
            f'<text x="150" y="{by + 38:.0f}" font-size="12" fill="{C}" '
            f'text-anchor="middle">12 cm</text>']
    return wrap(body, 300, by + 46)


def two_points():
    """P(-3, 7) and Q(4, 2) on a real grid, so the vertical gap of 5 can be counted."""
    body, px, w, h = grid(-5, 6, -1, 8)
    body += dot(px, -3, 7, "P(−3, 7)", dx=6, dy=-8)
    body += dot(px, 4, 2, "Q(4, 2)", dx=6, dy=16)
    a, b = px(4, 2)
    _, c = px(4, 7)
    body.append(f'<line x1="{a:.0f}" y1="{b:.0f}" x2="{a:.0f}" y2="{c:.0f}" stroke="{C}" '
                f'stroke-width="1.6" stroke-dasharray="5,4"/>')
    return wrap(body, w, h)


def two_lines():
    """One line of slope 1 and one of slope −1 on equal axes, so 45° looks like 45°."""
    body, px, w, h = grid(-1, 6, -1, 9)
    # Stop the lines short of the margin. Drawn to the grid corner, the y = x line ended
    # exactly where the "-1" tick label sits and printed through it.
    for (x0, y0), (x1, y1) in (((-0.6, -0.6), (5.6, 5.6)), ((0, 8), (5.6, 2.4))):
        a, b = px(x0, y0)
        c, d = px(x1, y1)
        body.append(f'<line x1="{a:.0f}" y1="{b:.0f}" x2="{c:.0f}" y2="{d:.0f}" '
                    f'stroke="{C}" stroke-width="2"/>')
    body += dot(px, 4, 4, "P(4, 4)", dx=24, dy=4)
    body += dot(px, 0, 8, "(0, 8)", dx=7, dy=-5)
    return wrap(body, w, h)


def parallelogram():
    """P(-6,2) Q(2,2) R(4,-4) S(-4,-4) at ONE scale. The old figure used three different
    horizontal scales, which is what the reviewer saw."""
    body, px, w, h = grid(-8, 6, -6, 4, cell=18)
    pts = {"P": (-6, 2), "Q": (2, 2), "R": (4, -4), "S": (-4, -4)}
    path = " L".join(f"{px(*pts[n])[0]:.0f} {px(*pts[n])[1]:.0f}" for n in "PQRS")
    body.append(f'<path d="M{path} Z" fill="{C}" fill-opacity=".05" stroke="{C}" '
                f'stroke-width="2"/>')
    a, b = px(*pts["P"])
    c, d = px(*pts["R"])
    body.append(f'<line x1="{a:.0f}" y1="{b:.0f}" x2="{c:.0f}" y2="{d:.0f}" stroke="{C}" '
                f'stroke-width="1.5" stroke-dasharray="5,4"/>')
    for n, (x, y) in pts.items():
        body += dot(px, x, y, f"{n}({x}, {y})",
                    dx=-46 if x < 0 else 8, dy=-8 if y > 0 else 16)
    return wrap(body, w, h)


def parallelogram_klmn():
    """K(-3,5) L(5,5) M(7,-1) N(-1,-1), on one scale. The dashed diagonal is KM, the
    side of triangle KLM the question asks about — KL is 8 across, M is 6 below it, so
    the area is 24."""
    body, px, w, h = grid(-5, 9, -3, 7, cell=18)
    pts = {"K": (-3, 5), "L": (5, 5), "M": (7, -1), "N": (-1, -1)}
    path = " L".join(f"{px(*pts[n])[0]:.0f} {px(*pts[n])[1]:.0f}" for n in "KLMN")
    body.append(f'<path d="M{path} Z" fill="{C}" fill-opacity=".05" stroke="{C}" '
                f'stroke-width="2"/>')
    a, b = px(*pts["K"])
    c2, d = px(*pts["M"])
    body.append(f'<line x1="{a:.0f}" y1="{b:.0f}" x2="{c2:.0f}" y2="{d:.0f}" stroke="{C}" '
                f'stroke-width="1.5" stroke-dasharray="5,4"/>')
    for n, (x, y) in pts.items():
        room_left = (x - (-8)) >= 3
        body += dot(px, x, y, f"{n}({x}, {y})",
                    dx=-44 if (room_left and x < 1) else 8, dy=-9 if y > 0 else 18)
    return wrap(body, w, h)


FIGURES = {
    "8373edd1-8636-4546-b5ea-5bcd6d30c63e": ("spinner: circumference drawn twice", spinner),
    "fba184a9-37f3-42f9-a9d6-1749dc0caa5e": ("circle: arcs retraced the outline", arcs),
    "4db981b4-e3cb-4527-8e98-f9454a7411e9": ("triangle: labels overlapped", isosceles),
    "97b2b32c-b686-4840-944f-3ab371dc698e": ("coordinates: no gridlines", two_points),
    "cb520797-c4ca-40d4-bb4c-904aae8a0809": ("lines: slope 1 not drawn at 45°", two_lines),
    "f4d44f5e-eba6-4ddf-95e5-060e6395cdc1": ("parallelogram: three different x scales",
                                             parallelogram),
    "__KLMN__": ("parallelogram KLMN: points 12 px off their own scale",
                 parallelogram_klmn),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    from tools.question_checks import (doubled_circle_outline, overlapping_text_labels,
                                       plotted_points_inconsistent)
    record = []
    for qid, (why, fn) in FIGURES.items():
        svg = fn()
        # the new figure must pass the checks that condemned the old one
        for check in (doubled_circle_outline, overlapping_text_labels,
                      plotted_points_inconsistent):
            msg = check(svg)
            assert not msg, f"{why}: redraw still fails {check.__name__}: {msg}"
        row = con.execute("SELECT form_id, form_position FROM questions WHERE id=?",
                          (qid,)).fetchone()
        record.append({"id": qid, "why": why, "bytes": len(svg)})
        if args.apply:
            con.execute("UPDATE questions SET figure_svg=?, edited=1 WHERE id=?", (svg, qid))
        print(f"  [{row['form_id']} pos {row['form_position']}] {why}  ({len(svg)} bytes)")
    if args.apply:
        RECORD.write_text(json.dumps(record, indent=2) + "\n")
        con.commit()
        print(f"\nredrew {len(record)}; record -> {RECORD}")
    else:
        print(f"\n{len(record)} to redraw (dry run)")


if __name__ == "__main__":
    main()
