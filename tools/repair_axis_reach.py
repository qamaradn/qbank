#!/usr/bin/env python3
"""Extend a chart's axis until it reaches the last thing measured against it.

"x-axis doesn't fully reach the end of the art bar." The baseline of a column chart
stopped 11 px short of the fifth column, so that column stood on nothing and its
height had no line to be measured from.

Additive under rule 11c: a line grows, nothing moves, and no coordinate that carries
meaning changes. The gridlines that share the axis's span are extended with it, since
a grid that stops where the axis used to stop is the same fault one step in.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_axis_reach
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_axis_reach --apply
"""
import argparse
import json
import pathlib
import re
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import figure_lib as fl                 # noqa: E402
from tools import question_checks as qc            # noqa: E402
from tools.repair_grid_reach import ALL_FIG        # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
RECORD = ROOT / "run_data/output/axis_reach_repairs.json"


def fig_state(svg):
    return {n for n in ALL_FIG + ["angle_arc_misses_its_rays"]
            if getattr(qc, n)(svg)}


def repair(svg, margin=6.0):
    ax = qc._axis_span(svg)
    if not ax:
        return None, "no axis pair"
    (hx0, hx1), (_vy0, vy1) = ax
    bars = []
    for m in re.finditer(r"<rect\b[^>]*>", svg):
        a = dict(fl._ATTR.findall(m.group(0)))
        try:
            x, y = float(a.get("x", 0)), float(a.get("y", 0))
            w, h = float(a.get("width", 0)), float(a.get("height", 0))
        except ValueError:
            continue
        if w > 0 and h > 6 and fl._is_inked(a) and abs((y + h) - vy1) < 1.5:
            bars.append((x, x + w))
    if len(bars) < 3:
        return None, "not a column chart"
    right = max(b[1] for b in bars) + margin
    left = min(b[0] for b in bars) - margin
    new = svg
    touched = 0
    for tag in re.findall(r"<line\b[^>]*>", svg):
        a = dict(fl._ATTR.findall(tag))
        try:
            x1, y1, x2, y2 = (float(a[k]) for k in ("x1", "y1", "x2", "y2"))
        except (KeyError, ValueError):
            continue
        if abs(y1 - y2) > 0.5 or abs(x1 - x2) < 40:
            continue                            # only long horizontal rules
        t = tag
        if max(x1, x2) < right:
            k = "x2" if x2 > x1 else "x1"
            t = re.sub(rf"\b{k}=([\'\"])[-\d.]+\1", f'{k}="{right:g}"', t, count=1)
        if min(x1, x2) > left:
            k = "x1" if x1 < x2 else "x2"
            t = re.sub(rf"\b{k}=([\'\"])[-\d.]+\1", f'{k}="{left:g}"', t, count=1)
        if t != tag:
            new = new.replace(tag, t, 1)
            touched += 1
    if not touched:
        return None, "axis already reaches"
    return new, f"{touched} horizontal rule(s) extended to {left:g}..{right:g}"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    done, refused = [], []
    for r in con.execute("SELECT id, source_book, form_id, figure_svg FROM questions "
                         "WHERE figure_svg IS NOT NULL AND figure_svg != '' "
                         "AND review_status != 'rejected'"):
        svg = r["figure_svg"]
        if not qc.axis_shorter_than_the_data(svg):
            continue
        before = fig_state(svg)
        new, note = repair(svg)
        if not new:
            refused.append({"id": r["id"], "why": note})
            continue
        gained = fig_state(new) - before
        if gained:
            refused.append({"id": r["id"], "newly_firing": sorted(gained)})
            continue
        done.append({"id": r["id"], "form": r["form_id"], "note": note})
        if args.apply:
            con.execute("UPDATE questions SET figure_svg = ?, edited = 1 WHERE id = ?",
                        (new, r["id"]))
    if args.apply:
        con.commit()
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps({"applied": args.apply, "extended": done,
                                  "refused": refused}, indent=1))
    print(f"{len(done)} extended, {len(refused)} refused"
          f"{'' if args.apply else '  (dry run — pass --apply)'}")
    for x in done + refused:
        print("  ", x["id"][:8], x.get("note") or x.get("why") or x.get("newly_firing"))
    print(f"record -> {RECORD}")


if __name__ == "__main__":
    main()
