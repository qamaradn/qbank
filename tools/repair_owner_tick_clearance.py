#!/usr/bin/env python3
"""Lift the axis numbers on 7961f672 and c0526d7f clear of the lines they sit on.

The owner's instruction, 2026-09-04: "15 and 16 question has overlap with line can u
move a bit up or down?" -- cards 15 and 16 on the round-11 page. Those numbers were put
back into their columns on the owner's previous instruction, and they land on ink.

Up and down was tried first and measured, and it is not available. Shifting the whole y
column down clears side AB at 6 px -- and at 6 px `plotted_geometry_matches_stem` starts
reporting the figure as disagreeing with its own stem, because that check reads the axis
mapping from the label positions and every plotted point then reads a fifth of a unit
out. There is no offset that clears the ink and keeps the mapping.

So the numbers move the one way that costs nothing: a y number sideways, an x number up
or down. The mapping is untouched either way, and each set stays one straight line.

  c0526d7f  side AB runs the width of the plot at y = 1, through the number column. The
            y column goes out to the left of A.

  7961f672  the rectangle spans x -1 to 4 by y -2 to 3, so its sides cross the column
            AND the row: y 3 and -2 sit on its top and bottom, x -1 and 4 on its left
            and right. The column goes left of it and the row below it. Round 10 moved
            only some of them and the reviewer rightly called that misaligned; here
            every number of a kind moves together.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_owner_tick_clearance
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_owner_tick_clearance --apply
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import question_checks as qc                       # noqa: E402
from tools.repair_vic_round11_figures import state            # noqa: E402

DB = ROOT / "run_data/db/qbank.db"


def move_column(svg, x, new_x):
    """Move every right-aligned tick number in the column at `x` sideways to new_x.

    Sideways is the ONLY direction a y number may go. The scale checks read the axis
    mapping from the label positions, so moving the column up or down -- even by 6 px,
    measured -- makes every plotted point read a fifth of a unit out and
    `plotted_geometry_matches_stem` starts reporting the figure as disagreeing with its
    own stem. Moving it sideways changes nothing about the mapping.

    The origin marker O is left where it is: it names the origin, not a tick."""
    pat = re.compile(rf'(<text x=")({x})(" y="\d+" font-size="10" text-anchor="end">)'
                     rf'((?!O<)[^<]*)(</text>)')
    moved = []

    def go(m):
        moved.append(m.group(4))
        return f"{m.group(1)}{new_x}{m.group(3)}{m.group(4)}{m.group(5)}"
    out = pat.sub(go, svg)
    assert moved, f"no column found at x={x}"
    return out, moved


def move_row(svg, y, new_y):
    """Move every centred tick number in the row at `y` down to new_y. Up and down is
    the only direction an x number may go, for the mirror-image reason."""
    pat = re.compile(rf'(<text x="\d+" y=")({y})(" font-size="10" '
                     rf'text-anchor="middle">)([^<]*)(</text>)')
    moved = []

    def go(m):
        moved.append(m.group(4))
        return f"{m.group(1)}{new_y}{m.group(3)}{m.group(4)}{m.group(5)}"
    out = pat.sub(go, svg)
    assert moved, f"no row found at y={y}"
    return out, moved


def f_c0526d7f(svg):
    """Side AB runs from x = -4 to x = 2 at y = 1, straight through the number column,
    so the y numbers go out to the left of A where nothing is drawn."""
    s, moved = move_column(svg, 179, 60)
    assert len(moved) == 14, f"c0526d7f: moved {len(moved)} labels, expected 14"
    return s


def f_7961f672(svg):
    """The rectangle spans x -1 to 4 by y -2 to 3, which is nearly the whole plotted
    area, so its four sides cross both the number column and the number row. The column
    goes out to the left of the rectangle and the row down below it -- each stays one
    straight line of its own kind, which is what the last round got wrong by moving
    only some of them.

    The row goes 22 px below the grid rather than just under the rectangle: at the
    nearer spot the row's -2 and the column's -3 ended up shoulder to shoulder in the
    bottom-left corner. Found by rendering it and looking; the label-overlap check
    passed it, because that check wants a real 6 px overlap and these merely touched."""
    s, ymoved = move_column(svg, 89, 62)
    assert len(ymoved) == 14, f"7961f672: moved {len(ymoved)} y labels, expected 14"
    s, xmoved = move_row(s, 158, 254)
    assert len(xmoved) == 14, f"7961f672: moved {len(xmoved)} x labels, expected 14"
    return s


BUILDERS = {"7961f672": f_7961f672, "c0526d7f": f_c0526d7f}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    for prefix, build in BUILDERS.items():
        q = dict(con.execute("SELECT * FROM questions WHERE id LIKE ?",
                             (prefix + "%",)).fetchone())
        assert q["review_status"] == "pending", f"{prefix}: {q['review_status']}"
        before = state(q)
        svg = build(q["figure_svg"])
        after = state({**q, "figure_svg": svg})
        print(f"{prefix}  before {sorted(before) or 'clean'}  ->  "
              f"after {sorted(after) or 'clean'}")
        print(f"   newly firing : {sorted(after - before) or 'none'}")
        print(f"   cleared      : {sorted(before - after) or 'none'}")
        print(f"   scale linear : {qc.axis_scale_nonlinear(svg) is None}")
        print(f"   labels clear : {qc.overlapping_text_labels(svg) is None}")
        print(f"   on the canvas: {qc.text_outside_the_canvas(svg) is None}")
        if args.apply:
            con.execute("UPDATE questions SET figure_svg = ?, edited = 1 WHERE id = ?",
                        (svg, q["id"]))
    if args.apply:
        con.commit()
        print("APPLIED")
    else:
        print("dry run")


if __name__ == "__main__":
    main()
