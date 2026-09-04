#!/usr/bin/env python3
"""Put the missing axis numbers back on 7961f672 and 42e248db, in their own columns.

The owner's instruction, 2026-09-04, following the same call on c0526d7f: the missing
ticks are to be written, and to sit on the same side of the axis as every other tick.
That overrules the reviewer on both figures.

  7961f672  Rectangle WXYZ spans x -1 to 4 by y -2 to 3, which is nearly the whole
            plotted area, so four tick numbers -- y 3 and -2, x -1 and 4 -- fall on its
            own sides. Round 10 moved the whole y column outside the square and dropped
            the two x numbers below it; the reviewer said that read worse and asked for
            the clashing numbers to be deleted instead; round 11 deleted them. They go
            back where the column and the row put them.

  42e248db  The y number -5 was pushed to the far side of the axis by the plane builder,
            because the plotted line ends at exactly (-1, -5). The reviewer asked twice
            for it to look "aligned with the other values"; it is in the column now.

Each restored number gets the page-coloured halo layer the others already have, so the
line or the rectangle side behind it is broken where the glyphs sit and the number reads
over it -- which is how a chart normally prints a number on a rule.

`text_overlaps_geometry` fires on both questions as a result, because those sides and
that line are solid ink and the check forgives a haloed label only over faint ink. That
is the accepted cost of the instruction. There is nowhere clear to put these numbers
instead: a y number may only move sideways and an x number only up or down, since the
scale checks read the axis mapping from the label positions -- and sideways is where the
rectangle is, and up-and-down is where the line is.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_owner_axis_ticks
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_owner_axis_ticks --apply
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


def ytick(x, y, v):
    return f'<text x="{x}" y="{y}" font-size="10" text-anchor="end">{v}</text>'


def xtick(x, y, v):
    return f'<text x="{x}" y="{y}" font-size="10" text-anchor="middle">{v}</text>'


def f_7961f672(svg):
    """Four numbers back: y 3 and -2 into the x=89 column, x -1 and 4 into the y=158
    row. Each is inserted immediately before a neighbour that is already drawn twice --
    once in the halo layer, once as glyphs -- so the new number is drawn twice too."""
    s = svg
    for new, anchor in ((ytick(89, 56, "3"), ytick(89, 86, "2")),
                        (ytick(89, 206, "−2"), ytick(89, 236, "−3")),
                        (xtick(68, 158, "−1"), xtick(128, 158, "1")),
                        (xtick(218, 158, "4"), xtick(248, 158, "5"))):
        assert new not in s, f"7961f672: {new} is already there"
        n = s.count(anchor)
        assert n == 2, f"7961f672: anchor {anchor} appears {n} times, expected 2"
        s = s.replace(anchor, new + anchor)
    return s


def f_42e248db(svg):
    """The y number -5 moves from the far side of the axis into the column, at its own
    tick height.

    Moving it exposed a defect round 10 left behind. Round 10 tried to give this number
    the halo the others have and inserted the second copy next to its neighbour in the
    COLUMN rather than inside the aria-hidden group -- the pattern it anchored on only
    existed in the visible layer, because the halo layer never carried -4 or -5. So the
    figure has been carrying two identical visible copies stacked on each other ever
    since, and the number has never actually had a halo. One copy goes into the halo
    group, where it does its job; the other stays as the glyphs."""
    old = '<text x="100" y="258" font-size="10" text-anchor="start">−5</text>'
    new = ytick(72, 266, "−5")
    n = svg.count(old)
    assert n == 2, f"42e248db: found {n} copies of the -5, expected 2"
    # one set of glyphs in the column...
    i = svg.index(old)
    s = svg[:i] + new + svg[i + len(old):]
    j = s.index(old)
    s = s[:j] + s[j + len(old):]
    assert s.count(new) == 1 and old not in s, "42e248db: could not reduce to one copy"
    # ...and a real halo copy inside the aria-hidden layer
    g = re.search(r'(<g[^>]*aria-hidden="true"[^>]*>.*?)</g>', s, re.S)
    assert g, "42e248db: no halo layer"
    s = s[:g.end(1)] + new + s[g.end(1):]
    assert s.count(new) == 2, "42e248db: halo copy not added"
    return s


BUILDERS = {"7961f672": f_7961f672, "42e248db": f_42e248db}


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
        print(f"   newly firing: {sorted(after - before) or 'none'}")
        print(f"   axis still to a constant scale: "
              f"{qc.axis_scale_nonlinear(svg) is None}")
        print(f"   labels no longer overlapping each other: "
              f"{qc.overlapping_text_labels(svg) is None}")
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
