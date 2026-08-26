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
from tools.question_checks import _axis_ticks, coordinate_figure_without_grid  # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
RECORD = ROOT / "run_data/output/gridline_repairs.json"


def add_grid(svg):
    xs, ys = _axis_ticks(svg)
    if len(xs) < 3 or len(ys) < 3:
        return None
    vb = re.search(r'viewBox=["\']0 0 ([\d.]+) ([\d.]+)["\']', svg)
    if not vb:
        return None
    w, h = float(vb.group(1)), float(vb.group(2))
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
