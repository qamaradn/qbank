#!/usr/bin/env python3
"""Clear the gate on the fifty forms being released to the reviewer.

Ten drill forms per component were selected for the first reviewer release -- VIC
maths+quant and reading+verbal, and all three NSW components. `gate_forms` refused
them on sixteen questions. Most were cleared by existing tools once three latent
bugs in those tools were fixed (see the commit); what is left is here, one entry
per question, each verified against its own key.

The figures are REBUILT from a single mapping rather than nudged, for the reason
round 5 recorded: every figure patched in place came back, and every figure
regenerated from its stated quantities held.

    57c749c2  y ticks read 0, 5, 15 at 50 px apart. The third is 10.
    c9b7e9f0  y ticks read 40, 80, 110, 120 for marks 40 px, 40 px and 20 px
              apart, and the line ends at 140 km when the stem and the key both
              say the train travels 120 km in 1.5 hours.
    7c472f4d  the grid was drawn on the tick LABELS, which sit 5 px left of their
              own marks, so every value read off the grid was read off by 5 px.
    d6b5e934  "a number line represents the dial of a linear scale" -- drawn with
              0, 5, 10, 15, 17, 20, 30, 40 all one tick apart. It is the one
              question in the set whose whole subject is reading a scale.
    de533ba1  a Bezier curve that is not the parabola, with (0, -3) drawn ABOVE
              the x-axis; the axis itself lands at y = -6.5 by its own labels.
    c06d73c2  the (3x + 15) label sits on the line whose angle it names; the
              nudger cannot place a 66 px box in that sector.

    33b467f9  120 passengers, +15%, then -10% = 124.2 people. Re-cut to +25% then
              -10% = 135, which is exact. Round 5 settled this: rounding is the
              worse fix, the numbers should come out.
    58913efa  96 apartments, 65% remaining = 62.4. Re-cut to 25% sold, 75% left.
    537e27da  models an addition with counters and "zero pairs" -- a classroom
              manipulative, which NSW selective does not test. Re-cut to a
              temperature context; all four options are unchanged and so is the key.
    79ea44bf  "Consider the following: '...'" and then four options. The stem
              never asks anything.

Usage:
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_vic_round7_release --dry-run
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_vic_round7_release --apply
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import question_checks as qc          # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
MANIFEST = ROOT / "run_data/output/round7_release_repairs.json"


# ---------------------------------------------------------------- drawing helpers
def line_chart(xlab, ylab, xticks, yticks, pts, vw=300, vh=236,
               ox=52, oy=180, right=272, top=32):
    """A straight-line graph where ticks, grid, axes and the line share one mapping.

    Both charts repaired here had ticks whose VALUES did not advance with their
    PIXELS, which is unreadable and which no amount of relabelling one tick fixes.
    Deriving every element from (value -> pixel) removes the possibility.
    """
    xmax, ymax = max(xticks), max(yticks)
    sx = (right - ox) / xmax
    sy = (oy - top) / ymax

    def px(x, y):
        return ox + sx * x, oy - sy * y

    grid = "".join(f"M{px(v, 0)[0]:.0f} {top:.0f}V{oy:.0f}" for v in xticks)
    grid += "".join(f"M{ox:.0f} {px(0, v)[1]:.0f}H{right:.0f}" for v in yticks)
    b = [f'<path d="{grid}" stroke="currentColor" stroke-opacity=".16" '
         f'stroke-width="1" fill="none"/>']
    b.append(f'<path d="M{ox:.0f} {top - 8:.0f}V{oy:.0f}H{right + 8:.0f}" '
             f'stroke="currentColor" stroke-width="2" fill="none"/>')
    marks = "".join(f"M{px(v, 0)[0]:.0f} {oy:.0f}v5" for v in xticks)
    marks += "".join(f"M{ox:.0f} {px(0, v)[1]:.0f}h-5" for v in yticks)
    b.append(f'<path d="{marks}" stroke="currentColor" stroke-width="1.4"/>')
    for v in xticks:
        b.append(f'<text x="{px(v, 0)[0]:.0f}" y="{oy + 17:.0f}" font-size="11" '
                 f'fill="currentColor" text-anchor="middle">{v:g}</text>')
    for v in yticks:
        b.append(f'<text x="{ox - 9:.0f}" y="{px(0, v)[1] + 4:.0f}" font-size="11" '
                 f'fill="currentColor" text-anchor="end">{v:g}</text>')
    b.append(f'<text x="{(ox + right) / 2:.0f}" y="{vh - 8:.0f}" font-size="12" '
             f'fill="currentColor" text-anchor="middle">{xlab}</text>')
    b.append(f'<text x="14" y="{(top + oy) / 2:.0f}" font-size="12" '
             f'fill="currentColor" text-anchor="middle" '
             f'transform="rotate(-90 14 {(top + oy) / 2:.0f})">{ylab}</text>')
    (ax, ay), (bx, by) = px(*pts[0]), px(*pts[-1])
    b.append(f'<line x1="{ax:.0f}" y1="{ay:.0f}" x2="{bx:.0f}" y2="{by:.0f}" '
             f'stroke="currentColor" stroke-width="2.5" stroke-opacity=".9"/>')
    for (x, y) in pts:
        cx, cy = px(x, y)
        b.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="4" fill="currentColor"/>')
    return (f'<svg viewBox="0 0 {vw} {vh}" xmlns="http://www.w3.org/2000/svg" '
            f'fill="none">' + "".join(b) + "</svg>")


def number_line(values, marked, vw=320, vh=110, x0=26, x1=286, y=58):
    """A number line to ONE scale, with every labelled value in its true place.

    `values` are the numbers to print; `marked` is {label: value} for the arrows.
    The original put 0, 5, 10, 15, 17, 20, 30 and 40 one tick apart, so the
    reading a student takes off it is not the reading the key assumes.
    """
    lo, hi = 0, max(max(values), max(marked.values()))
    s = (x1 - x0) / (hi - lo)

    def px(v):
        return x0 + s * (v - lo)
    b = [f'<path d="M{x0} {y}H{x1 + 10}" stroke="currentColor" stroke-width="2" '
         f'fill="none"/>',
         f'<polygon points="{x1 + 10},{y} {x1 + 2},{y - 5} {x1 + 2},{y + 5}" '
         f'fill="currentColor"/>',
         f'<text x="{x1 + 16}" y="{y + 4}" font-size="12" fill="currentColor">kg</text>']
    minor = "".join(f"M{px(v):.1f} {y}v-4" for v in range(lo, hi + 1)
                    if v not in values)
    b.append(f'<path d="{minor}" stroke="currentColor" stroke-opacity=".55" '
             f'stroke-width="1" fill="none"/>')
    major = "".join(f"M{px(v):.1f} {y}v-9" for v in values)
    b.append(f'<path d="{major}" stroke="currentColor" stroke-width="1.6" fill="none"/>')
    for v in values:
        b.append(f'<text x="{px(v):.1f}" y="{y - 14}" font-size="11" '
                 f'fill="currentColor" text-anchor="middle">{v:g}</text>')
    for name, v in marked.items():
        p = px(v)
        b.append(f'<polygon points="{p:.1f},{y + 6} {p - 6:.1f},{y + 22} '
                 f'{p + 6:.1f},{y + 22}" fill="currentColor" fill-opacity=".25" '
                 f'stroke="currentColor" stroke-width="1.2"/>')
        b.append(f'<text x="{p:.1f}" y="{y + 38}" font-size="12" fill="currentColor" '
                 f'text-anchor="middle" font-weight="bold">{name}</text>')
    return (f'<svg viewBox="0 0 {vw} {vh}" xmlns="http://www.w3.org/2000/svg" '
            f'fill="none">' + "".join(b) + "</svg>")


def parabola(a, c, xr, yr, pts, vw=300, vh=230, pad=30):
    """y = a x^2 + c, drawn from the coefficients, with its axes through (0, 0)."""
    x0, x1 = xr
    y0, y1 = yr
    sx = (vw - 2 * pad) / (x1 - x0)
    sy = (vh - 2 * pad) / (y1 - y0)

    def px(x, y):
        return pad + (x - x0) * sx, vh - pad - (y - y0) * sy
    axx, axy = px(0, 0)
    b = []
    grid = "".join(f"M{px(v, 0)[0]:.0f} {pad}V{vh - pad}"
                   for v in range(int(x0), int(x1) + 1))
    grid += "".join(f"M{pad} {px(0, v)[1]:.0f}H{vw - pad}"
                    for v in range(int(y0), int(y1) + 1) if v % 2 == 0)
    b.append(f'<path d="{grid}" stroke="currentColor" stroke-opacity=".14" '
             f'stroke-width="1" fill="none"/>')
    b.append(f'<path d="M{pad} {axy:.0f}H{vw - pad}M{axx:.0f} {vh - pad}V{pad}" '
             f'stroke="currentColor" stroke-width="1.6" fill="none"/>')
    ticks = "".join(f"M{px(v, 0)[0]:.0f} {axy - 4:.0f}v8"
                    for v in range(int(x0), int(x1) + 1) if v)
    ticks += "".join(f"M{axx - 4:.0f} {px(0, v)[1]:.0f}h8"
                     for v in range(int(y0), int(y1) + 1) if v and v % 2 == 0)
    b.append(f'<path d="{ticks}" stroke="currentColor" stroke-width="1.4"/>')
    for v in range(int(x0), int(x1) + 1):
        if v:
            b.append(f'<text x="{px(v, 0)[0]:.0f}" y="{axy + 16:.0f}" font-size="10" '
                     f'fill="currentColor" text-anchor="middle">'
                     f'{str(v).replace("-", "−")}</text>')
    for v in range(int(y0), int(y1) + 1):
        if v and v % 2 == 0:
            b.append(f'<text x="{axx - 8:.0f}" y="{px(0, v)[1] + 4:.0f}" '
                     f'font-size="10" fill="currentColor" text-anchor="end">'
                     f'{str(v).replace("-", "−")}</text>')
    pathd, first = "", True
    steps = 90
    for i in range(steps + 1):
        x = x0 + (x1 - x0) * i / steps
        y = a * x * x + c
        if not (y0 <= y <= y1):
            first = True
            continue
        X, Y = px(x, y)
        pathd += ("M" if first else "L") + f"{X:.1f} {Y:.1f}"
        first = False
    b.append(f'<path d="{pathd}" stroke="currentColor" stroke-width="2" fill="none"/>')
    for (x, y), (dx, dy) in pts:
        X, Y = px(x, y)
        b.append(f'<circle cx="{X:.0f}" cy="{Y:.0f}" r="4" fill="currentColor"/>')
        b.append(f'<text x="{X + dx:.0f}" y="{Y + dy:.0f}" font-size="12" '
                 f'fill="currentColor" text-anchor="middle">'
                 f'({x:g}, {str(y).replace("-", "−")})</text>')
    b.append(f'<text x="{vw - pad + 12:.0f}" y="{axy + 4:.0f}" font-size="12" '
             f'fill="currentColor" text-anchor="middle">x</text>')
    b.append(f'<text x="{axx + 12:.0f}" y="{pad - 12:.0f}" font-size="12" '
             f'fill="currentColor" text-anchor="middle">y</text>')
    return (f'<svg viewBox="0 0 {vw} {vh}" xmlns="http://www.w3.org/2000/svg" '
            f'fill="none">' + "".join(b) + "</svg>")


def relabel(svg, old, new):
    """Change one tick's printed value, leaving its position alone."""
    out, n = re.subn(rf"(>)\s*{re.escape(old)}\s*(</text>)", rf"\g<1>{new}\g<2>", svg, 1)
    if n != 1:
        raise SystemExit(f"relabel {old!r} -> {new!r} matched {n} times")
    return out


def move_label(svg, text, nx, ny):
    m = re.search(rf"<text[^>]*>\s*{re.escape(text)}\s*</text>", svg)
    if not m:
        raise SystemExit(f"no label {text!r}")
    tag = m.group(0)
    t = re.sub(r"\bx=(['\"])[-\d.]+\1", lambda z: f"x={z.group(1)}{nx}{z.group(1)}", tag, 1)
    t = re.sub(r"\by=(['\"])[-\d.]+\1", lambda z: f"y={z.group(1)}{ny}{z.group(1)}", t, 1)
    return svg.replace(tag, t, 1)


def fix_grid_to_marks(svg):
    """Redraw the grid path onto the tick MARKS it is supposed to index."""
    marks = qc._tick_marks(svg)
    xs, ys = sorted(marks[0]), sorted(marks[1])
    if len(xs) < 2 or len(ys) < 2:
        raise SystemExit("not enough tick marks to rebuild the grid")
    d = "".join(f"M{x:.0f} {min(ys):.0f}V{max(ys):.0f}" for x in xs)
    d += "".join(f"M{min(xs):.0f} {y:.0f}H{max(xs):.0f}" for y in ys)
    return re.sub(r'<path d="M45 39V184[^"]*"[^>]*/>',
                  f'<path d="{d}" stroke="currentColor" stroke-opacity=".16" '
                  f'stroke-width="1" fill="none"/>', svg, 1)


# ---------------------------------------------------------------- the repairs
def r_57c749c2(q):
    """Relabel the y tick, then grid the now-linear axis."""
    # 0, 5, 15 printed against marks 50 px apart. The third mark is 10. There is a
    # "15" on the x-axis too, so this is targeted by POSITION -- the y tick sits at
    # x=14, y=84 -- rather than by being the first "15" in the document.
    from tools.repair_add_gridlines import add_grid
    fixed = _fix_y_tick(q["figure_svg"])
    return dict(figure_svg=add_grid(fixed) or fixed)


def _fix_y_tick(svg):
    m = re.search(r'<text x="14" y="84"[^>]*>15</text>', svg)
    if not m:
        raise SystemExit("the y tick labelled 15 is not where it was")
    return svg.replace(m.group(0), m.group(0).replace(">15<", ">10<"), 1)


def r_c9b7e9f0(q):
    return dict(figure_svg=line_chart(
        "Time (hours)", "Distance (km)", [0.5, 1.0, 1.5], [40, 80, 120],
        [(0, 0), (1.5, 120)]))


def r_7c472f4d(q):
    svg = fix_grid_to_marks(q["figure_svg"])
    for old, new in ((100, 105), (155, 160), (210, 215), (265, 270)):
        svg = re.sub(rf"<text x='{old}'", f"<text x='{new}'", svg, 1)
        svg = re.sub(rf'<text x="{old}"', f'<text x="{new}"', svg, 1)
    return dict(figure_svg=svg)


def r_d6b5e934(q):
    return dict(figure_svg=number_line([0, 5, 10, 15, 20, 25, 30, 35, 40],
                                       {"E": 5, "L": 17}))


def r_de533ba1(q):
    # y = 2x^2 - 3, which is what (0, -3) and (2, 5) give and what the key uses.
    return dict(figure_svg=parabola(2, -3, (-3, 3), (-4, 8),
                                    [((0, -3), (34, 14)), ((2, 5), (30, -8))]))


def r_c06d73c2(q):
    # Both labels, because they name the vertically OPPOSITE pair and so belong in
    # the left and right sectors. A 51 degree sector is only tall enough for a 60-66
    # px box some way out from the crossing, which is why nudging in small rings
    # could not place either one.
    svg = move_label(q["figure_svg"], "(3x + 15)°", 34, 112)
    return dict(figure_svg=move_label(svg, "(5x − 9)°", 180, 114))


def r_33b467f9(q):
    return dict(
        stem="A ferry travels between Tasmania and the mainland. On its first trip "
             "it carried 120 passengers. On its second trip it carried 25% more "
             "passengers than the first trip. On its third trip it carried 10% "
             "fewer passengers than the second trip. How many passengers did the "
             "ferry carry on its third trip?",
        option_a="150", option_b="138", option_c="135", option_d="132",
        correct_answer="C",
        explanation="Second trip: 120 × 1.25 = 150 passengers. Third trip: 10% fewer "
                    "than 150 is 150 − 15 = 135 passengers. 150 stops at the second "
                    "trip; 132 takes 25% and 10% of the ORIGINAL 120 instead of "
                    "applying each to the trip before it.")


def r_58913efa(q):
    return dict(
        stem="A new apartment building in Melbourne has 12 floors, each with 8 "
             "apartments. If 25% of all the apartments have been sold, how many "
             "apartments are still available for purchase?",
        option_a="72", option_b="24", option_c="96", option_d="84",
        correct_answer="A",
        explanation="The building has 12 × 8 = 96 apartments in total. If 25% have "
                    "been sold then 75% remain: 0.75 × 96 = 72 apartments still "
                    "available. 24 is the number SOLD and 96 is the whole building.")


def r_537e27da(q):
    return dict(
        stem="At noon the temperature in Canberra was 9 °C. By evening it had "
             "fallen by 5 °C. Which calculation gives the evening temperature, and "
             "what is it?",
        explanation="A fall of 5 degrees is added as a negative number, so the "
                    "evening temperature is 9 + (−5) = 4 °C. 9 + 5 treats the fall "
                    "as a rise; 9 − (−5) subtracts the negative, which is the same "
                    "as adding 5; (−9) + 5 starts from the wrong temperature.")


def r_79ea44bf(q):
    return dict(stem=q["stem"].rstrip() +
                " Which of the following can most reasonably be inferred?")


REPAIRS = {
    "57c749c2": ("y ticks 0, 5, 15 against marks 50 px apart", r_57c749c2),
    "c9b7e9f0": ("y ticks not to one scale and the line ends at 140, not 120",
                 r_c9b7e9f0),
    "7c472f4d": ("the grid was drawn on the labels, 5 px off its own marks",
                 r_7c472f4d),
    "d6b5e934": ("a linear scale drawn with 0,5,10,15,17,20,30,40 one tick apart",
                 r_d6b5e934),
    "de533ba1": ("not a parabola, and (0, −3) drawn above the x-axis", r_de533ba1),
    "c06d73c2": ("the angle label sits on the line whose angle it names", r_c06d73c2),
    "33b467f9": ("120 → +15% → −10% = 124.2 people", r_33b467f9),
    "58913efa": ("96 apartments, 65% remaining = 62.4", r_58913efa),
    "537e27da": ("models an addition with counters and zero pairs", r_537e27da),
    "79ea44bf": ("the stem never asks anything", r_79ea44bf),
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if not (a.apply or a.dry_run):
        raise SystemExit("pass --apply or --dry-run")

    import tools.gate_forms as gf
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    record, failed = [], 0

    for prefix, (why, fn) in REPAIRS.items():
        row = con.execute("SELECT * FROM questions WHERE id LIKE ?||'%'",
                          (prefix,)).fetchone()
        if row is None:
            raise SystemExit(f"{prefix} is not in the database")
        q = dict(row)
        before = [n for n, _ in gf.BLOCKING if gf.run_check(n, q)]
        new = fn(q)
        q.update(new)
        after = [n for n, _ in gf.BLOCKING if gf.run_check(n, q)]
        ok = not after
        failed += not ok
        print(f"{prefix}  {why}")
        print(f"    before: {before or 'clean'}   after: {after or 'clean'}"
              f"  {'OK' if ok else 'STILL FAILING'}")
        record.append(dict(id=row["id"], form_id=row["form_id"], why=why,
                           before=before, after=after,
                           fields=sorted(new), key=q["correct_answer"]))
        if a.apply and ok:
            cols = ", ".join(f"{k}=?" for k in new)
            con.execute(f"UPDATE questions SET {cols}, edited=1 WHERE id=?",
                        (*new.values(), row["id"]))

    if a.apply:
        if failed:
            con.rollback()
            raise SystemExit(f"\n{failed} still failing — nothing written")
        con.commit()
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(json.dumps(record, indent=1, ensure_ascii=False))
        print(f"\napplied {len(record)} — manifest {MANIFEST}")
    else:
        print(f"\ndry run — {len(record)} question(s), {failed} still failing")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
