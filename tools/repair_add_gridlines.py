#!/usr/bin/env python3
"""Draw gridlines on a coordinate plane that has tick numbers but no grid.

Asked for three times in one review round: "try adding the lines across the values",
"add the lines on each number". Without a grid the reader estimates where a point sits,
and estimating is not the skill under test.

This does not redraw anything. It reads the tick labels already present, works out where
each gridline belongs from their pixel positions, and inserts one path behind everything
else. Nothing that was drawn moves, so a figure cannot be made wrong by adding a grid —
only easier to read.
"""
import argparse
import json
import pathlib
import re
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.question_checks import (_axis_ticks, _figure_axis_map,  # noqa: E402
                                   _tick_marks,
                                   axis_scale_nonlinear,
                                   coordinate_figure_without_grid)

DB = ROOT / "run_data/db/qbank.db"
RECORD = ROOT / "run_data/output/gridline_repairs.json"


def add_grid(svg):
    # A grid is derived from the axis mapping, so an axis that is not to a constant
    # scale yields a grid that is wrong everywhere -- worse than the missing grid it
    # replaces, because it looks authoritative. Fix the axis first.
    if axis_scale_nonlinear(svg):
        return None
    xs, ys = _axis_ticks(svg)
    if len(xs) < 3 or len(ys) < 3:
        return None
    vb = re.search(r'viewBox=["\']0 0 ([\d.]+) ([\d.]+)["\']', svg)
    if not vb:
        return None
    w, h = float(vb.group(1)), float(vb.group(2))
    # Place the grid from the figure's own MAPPING, not from where the tick numbers
    # print. A label's x is its anchor and its y is a baseline sitting ~4 px below the
    # mark it names, so a grid drawn straight onto label positions lands a few pixels
    # off every tick -- which is precisely the defect round 5 wrote
    # `gridlines_off_the_ticks` to catch, and this tool was creating it. The mapping
    # from `_figure_axis_map` already corrects the label offset against the tick marks.
    # Tick MARKS first, where the figure draws them. They are what
    # `gridlines_off_the_ticks` measures the grid against, and on one chart the
    # label-derived mapping put every vertical line 7-9 px left of the mark it was
    # supposed to index -- the tool re-creating the very defect it is run to avoid.
    marks = _tick_marks(svg)
    if len(marks[0]) >= 3 and len(marks[1]) >= 3:
        xps, yps = sorted(set(marks[0])), sorted(set(marks[1]))
        d = "".join(f"M{x:.0f} {min(yps):.0f}V{max(yps):.0f}" for x in xps)
        d += "".join(f"M{min(xps):.0f} {y:.0f}H{max(xps):.0f}" for y in yps)
        grid = (f'<path d="{d}" stroke="currentColor" stroke-opacity=".16" '
                f'stroke-width="1" fill="none"/>')
        i = svg.index(">") + 1
        return svg[:i] + grid + svg[i:]
    amap = _figure_axis_map(svg)
    if amap:
        sx, ox, sy, oy, _src = amap

        def line_positions(scale, origin, ticks):
            """One gridline per LABELLED tick, plus the axis itself.

            Stepping by one unit of the mapping drew a line every kilogram on an
            axis labelled every five, which is a mesh rather than a grid. And
            starting at the first tick left a bare band between the axis and it.
            The values the figure prints are the values a reader looks up.
            """
            vals = sorted({v for v, _p in ticks})
            step = min((b - a for a, b in zip(vals, vals[1:]) if b > a),
                       default=None)
            if not step:
                return []
            lo, hi = min(vals), max(vals)
            v, out = lo, []
            while v <= hi + step / 2:
                out.append(origin + scale * v)
                v += step
            if all(abs(origin - p) > 1 for p in out):
                out.append(origin)             # the axis line closes the grid
            return sorted(out)
        xps, yps = line_positions(sx, ox, xs), line_positions(sy, oy, ys)
        if len(xps) >= 3 and len(yps) >= 3:
            top, bot = min(yps), max(yps)
            left, right = min(xps), max(xps)
            d = "".join(f"M{x:.0f} {top:.0f}V{bot:.0f}" for x in xps)
            d += "".join(f"M{left:.0f} {y:.0f}H{right:.0f}" for y in yps)
            grid = (f'<path d="{d}" stroke="currentColor" stroke-opacity=".16" '
                    f'stroke-width="1" fill="none"/>')
            i = svg.index(">") + 1
            return svg[:i] + grid + svg[i:]
    xps = sorted({p for _v, p in xs})
    yps = sorted({p for _v, p in ys})
    # extend the tick spacing across the whole plot so the grid is complete
    def span(ps):
        if len(ps) < 2:
            return ps
        step = min(b - a for a, b in zip(ps, ps[1:]) if b - a > 1)
        out, p = list(ps), min(ps) - step
        while p > 4:
            out.append(p)
            p -= step
        p = max(ps) + step
        while p < (w if ps is xps else h) - 4:
            out.append(p)
            p += step
        return sorted(out)
    xps, yps = span(xps), span(yps)
    top, bot = min(yps), max(yps)
    left, right = min(xps), max(xps)
    d = "".join(f"M{x:.0f} {top:.0f}V{bot:.0f}" for x in xps)
    d += "".join(f"M{left:.0f} {y:.0f}H{right:.0f}" for y in yps)
    grid = (f'<path d="{d}" stroke="currentColor" stroke-opacity=".16" '
            f'stroke-width="1" fill="none"/>')
    # behind everything: immediately after the opening <svg ...>
    i = svg.index(">") + 1
    return svg[:i] + grid + svg[i:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--forms", required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    forms = [f.strip() for f in args.forms.split(",") if f.strip()]
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute(
        f"SELECT * FROM questions WHERE form_id IN ({','.join('?' * len(forms))}) "
        f"AND review_status!='rejected' AND figure_svg IS NOT NULL", forms)]
    record = []
    for r in rows:
        if not coordinate_figure_without_grid(r["figure_svg"]):
            continue
        new = add_grid(r["figure_svg"])
        if not new:
            print(f"  !! [{r['form_id']} pos {r['form_position']}] could not read its ticks")
            continue
        if coordinate_figure_without_grid(new):
            print(f"  !! [{r['form_id']} pos {r['form_position']}] grid added but still "
                  f"reads as gridless")
            continue
        print(f"  [{r['form_id']} pos {r['form_position']}] grid added "
              f"(+{len(new) - len(r['figure_svg'])} bytes)")
        record.append({"id": r["id"], "form_id": r["form_id"]})
        if args.apply:
            con.execute("UPDATE questions SET figure_svg=?, edited=1 WHERE id=?",
                        (new, r["id"]))
    if args.apply and record:
        RECORD.write_text(json.dumps(record, indent=2) + "\n")
        con.commit()
        print(f"\ngridded {len(record)} figure(s)")
    else:
        print(f"\n{len(record)} would change (dry run)")


if __name__ == "__main__":
    main()
