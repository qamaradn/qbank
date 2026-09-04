#!/usr/bin/env python3
"""Put the y-axis '1' back on c0526d7f, in the column with the other numbers.

The owner's instruction, 2026-09-04: "align 1 as all other ticks on y axis, write 1 as
it missed out." That overrules the reviewer's note on the same figure in the 2026-09-03
return, which asked for it to be deleted, and round 11 deleted it.

Why it kept moving. Triangle ABC has A(-4, 1) and B(2, 1), so side AB is drawn at
y = 172 running from x = 68 to x = 248 -- straight through the number column at x = 179
and across almost the whole plot. There is nowhere at that height on either side of the
axis that AB does not cover, and the number cannot be nudged up or down instead: the
scale checks read the axis mapping from the label positions, so a y number moved along
its own axis makes the axis read as nonlinear (moving it 10 px in round 10 did exactly
that). Round 10 put it on the far side of the axis; the reviewer called that out of
place; round 11 deleted it; the owner wants it back in line.

So it goes back at x = 179, y = 176, which is where the column and the tick put it, and
it gets the page-coloured halo the other numbers have and it never had. The halo breaks
AB where the glyphs sit, which is how a chart normally prints a number over a rule.

`text_overlaps_geometry` fires again on this question as a result, because AB is solid
ink and that check forgives a haloed label only over faint ink. That is a known and
accepted cost of the instruction, not an accident: the alternative is no number at all.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_c0526d7f_yaxis_one
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_c0526d7f_yaxis_one --apply
"""
from __future__ import annotations

import argparse
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import question_checks as qc                       # noqa: E402
from tools.repair_vic_round10_figures import halo, sub1       # noqa: E402
from tools.repair_vic_round11_figures import state            # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
LABEL = '<text x="179" y="176" font-size="10" text-anchor="end">1</text>'
ANCHOR = '<text x="179" y="236" font-size="10" text-anchor="end">−1</text>'


def build(svg):
    assert LABEL not in svg, "the y-axis 1 is already there"
    # the halo copy goes in the aria-hidden layer the other numbers use, and the glyph
    # in the visible layer, both immediately before the -1 that follows it in each
    n = svg.count(ANCHOR)
    assert n == 2, f"expected the -1 twice (halo and glyph), found {n}"
    return svg.replace(ANCHOR, LABEL + ANCHOR)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    q = dict(con.execute("SELECT * FROM questions WHERE id LIKE 'c0526d7f%'").fetchone())
    assert q["review_status"] == "pending", q["review_status"]
    before = state(q)
    svg = build(q["figure_svg"])
    after = state({**q, "figure_svg": svg})
    print(f"before: {sorted(before) or 'clean'}")
    print(f"after : {sorted(after) or 'clean'}")
    print(f"newly firing: {sorted(after - before) or 'none'}")
    print(f"the y-axis 1 is drawn twice (halo + glyph): {svg.count(LABEL) == 2}")
    print(f"axis still to a constant scale: {qc.axis_scale_nonlinear(svg) is None}")
    if args.apply:
        con.execute("UPDATE questions SET figure_svg = ?, edited = 1 WHERE id = ?",
                    (svg, q["id"]))
        con.commit()
        print("APPLIED")
    else:
        print("dry run")


if __name__ == "__main__":
    main()
