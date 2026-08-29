#!/usr/bin/env python3
"""Clear the last figure faults on the NSW side, before the reviewer sees them.

NSW came into this pass in far better shape than VIC -- 17 faults across 323
figures against VIC's 67 across 525 -- because most of it was hand-authored
THROUGH the check harness rather than repaired afterwards. `lr_thinking_skills`
was built 0 to 300 with `lr_finalise` running the checks before anything loaded,
and `year7_nsw_maths` was drawn by `figure_lib`. That difference is the argument
for authoring through the gate.

What is left divides three ways:

  NINE charts and grids with no axis titles. Four are coordinate grids, where the
  convention is simply x and y; five are one temperature graph reused by five
  questions, which needs "Time" and "Temperature (°C)". Adding a title moves
  nothing and changes no answer.

  THREE that model arithmetic with CLASSROOM MANIPULATIVES -- algebra tiles and
  positive/negative counters. NSW selective tests reasoning, not the materials a
  particular classroom happens to own, which is why `teaching_manipulative` is
  blocking. Each is restated as the mathematics it was teaching, with every
  option and every key unchanged, and the figure goes: the figure WAS the
  manipulative.

  ONE rotation whose figure could not be checked against its stem, redrawn from
  the vertex the stem names.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_nsw_figure_pass --dry-run
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_nsw_figure_pass --apply
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

from tools import figure_lib as fl                       # noqa: E402
from tools import gate_forms as gf                       # noqa: E402
from tools import question_checks as qc                  # noqa: E402
from tools.repair_canvas_overflow import grow             # noqa: E402
from tools.repair_label_collisions import repair as denude  # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
MANIFEST = ROOT / "run_data/output/nsw_figure_pass_repairs.json"


def add_axis_titles(svg: str, xlab: str, ylab: str) -> str:
    """Name both axes without moving anything already drawn.

    The canvas grows to hold the titles rather than the plot shrinking to fit
    them, so every coordinate in the figure keeps the meaning it had.
    """
    m = re.search(r'viewBox\s*=\s*[\'"]([^\'"]+)[\'"]', svg)
    x0, y0, w, h = (float(v) for v in m.group(1).split())
    body = svg[svg.index(">") + 1:svg.rindex("</svg>")]
    # The viewBox is EXTENDED into new margin rather than the content being wrapped
    # in a translate. Both put the title in clear space, but `_text_box` does not
    # follow a group transform -- it reads a shifted label at its pre-shift x -- so
    # a wrapped figure reported a collision between the y title and a tick that in
    # the browser are 18 px apart. Extending the box moves nothing, so what the
    # check reads is what the browser draws.
    left, below = 26.0, 40.0
    nx, ny = x0 - left, y0
    nw, nh = w + left, h + below
    body += fl.txt(x0 + w / 2, y0 + h + below - 10, xlab, 12)
    midy = y0 + h / 2
    body += (f'<text x="{nx + 13:.0f}" y="{midy:.0f}" font-family="system-ui,'
             f'sans-serif" font-size="12" fill="currentColor" text-anchor="middle" '
             f'transform="rotate(-90 {nx + 13:.0f} {midy:.0f})">{ylab}</text>')
    return fl.svg(body, vb=f"{nx:g} {ny:g} {nw:g} {nh:g}")


def titled(xlab, ylab):
    return lambda q: dict(figure_svg=add_axis_titles(q["figure_svg"], xlab, ylab))


REPAIRS = {
    # -- coordinate grids: the axes are x and y, which is the whole convention --
    "f5cba1c5": ("a coordinate grid with unnamed axes", titled("x", "y")),
    "51aef66f": ("a coordinate grid with unnamed axes", titled("x", "y")),
    "ab4550b1": ("a coordinate grid with unnamed axes", titled("x", "y")),
    "e936bda5": ("a coordinate grid with unnamed axes", titled("x", "y")),
    # -- one temperature graph, five questions --
    "b9503c9e": ("a temperature graph with unnamed axes",
                 titled("Time", "Temperature (°C)")),
    "d5c1f038": ("a temperature graph with unnamed axes",
                 titled("Time", "Temperature (°C)")),
    "4141e359": ("a temperature graph with unnamed axes",
                 titled("Time", "Temperature (°C)")),
    "8727c019": ("a temperature graph with unnamed axes",
                 titled("Time", "Temperature (°C)")),
    "44129c65": ("a temperature graph with unnamed axes",
                 titled("Time", "Temperature (°C)")),
    # -- classroom manipulatives, restated as the mathematics --
    "f44ea56d": ("models an addition with positive and negative counters",
                 lambda q: dict(
                     figure_svg=None,
                     stem="At 6 am the temperature in Orange was 6 °C. By midnight "
                          "it had fallen 8 °C. Which calculation gives the midnight "
                          "temperature, and what is it?",
                     explanation="A fall of 8 degrees is added as a negative number, "
                                 "so the midnight temperature is 6 + (−8) = −2 °C. "
                                 "8 + (−6) starts from the wrong temperature; "
                                 "6 + (−8) = 2 subtracts the wrong way round; "
                                 "6 + 8 treats the fall as a rise.")),
    "e699033b": ("two equal groups of algebra tiles",
                 lambda q: dict(
                     figure_svg=None,
                     stem="Two identical bags each hold x marbles and 3 loose "
                          "marbles. Which pair of expressions BOTH give the total "
                          "number of marbles?",
                     explanation="Each bag holds x + 3, and there are two of them, "
                                 "so the total is 2(x + 3). Expanding gives "
                                 "2x + 6. 2x + 3 doubles only the bags and forgets "
                                 "to double the loose marbles, and 2(x + 6) doubles "
                                 "the 3 twice.")),
    "ab8cb6f5": ("an equation set out in algebra tiles",
                 lambda q: dict(
                     figure_svg=None,
                     stem="Two identical boxes and 3 single books weigh the same as "
                          "11 single books. What is the equation, and how many "
                          "books does one box hold?",
                     explanation="Two boxes and 3 books balance 11 books, so "
                                 "2x + 3 = 11. Take 3 from both sides: 2x = 8. "
                                 "Halve both sides: x = 4. 3x + 2 = 11 counts three "
                                 "boxes; x = 7 stops at 2x = 8 without halving; "
                                 "x = 8 halves nothing at all.")),
    # -- the rotation, redrawn from the vertex the stem names --
    "4769e94e": ("the pre-image triangle with P(4, 1) named",
                 # Bare letters, not coordinate labels: P and Q sit ON the x-axis,
                 # so "P(4, 1)" lies across the axis line and its tick numbers. The
                 # stem already names P(4, 1) in words.
                 lambda q: dict(figure_svg=fl.plane(
                     points={"P": (4, 1), "Q": (6, 1), "R": (4, 5)},
                     polygon=[(4, 1), (6, 1), (4, 5)],
                     xr=(-6, 7), yr=(-6, 7), cell=18))),
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if not (a.apply or a.dry_run):
        raise SystemExit("pass --apply or --dry-run")

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    record, failed = [], 0
    for prefix, (why, build) in REPAIRS.items():
        row = con.execute("SELECT * FROM questions WHERE id LIKE ?||'%'",
                          (prefix,)).fetchone()
        if row is None:
            raise SystemExit(f"{prefix} is not in the database")
        q = dict(row)
        before = [n for n, _ in gf.BLOCKING if gf.run_check(n, q)]
        fields = build(q)
        if fields.get("figure_svg"):
            fields["figure_svg"], _m = denude(fields["figure_svg"])
            grown, _added = grow(fields["figure_svg"])
            fields["figure_svg"] = grown
        q.update(fields)
        after = [n for n, _ in gf.BLOCKING if gf.run_check(n, q)]
        errs = [e for e in (qc.figure_svg_errors(q["figure_svg"] or "") or [])
                if "bytes" not in e]
        ok = not after and not errs
        failed += not ok
        print(f"  {prefix}  {why[:48]:<48} {before} -> {after or 'clean'}"
              f"  {'OK' if ok else 'FAILING ' + str(errs)}")
        record.append({"id": row["id"], "why": why, "before": before, "after": after,
                       "fields": sorted(fields)})
        if a.apply and ok:
            cols = ", ".join(f"{k}=?" for k in fields)
            con.execute(f"UPDATE questions SET {cols}, edited=1 WHERE id=?",
                        (*fields.values(), row["id"]))
    if a.apply:
        con.commit()
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(json.dumps(record, indent=1, ensure_ascii=False))
        print(f"\napplied {len(record) - failed} of {len(record)} — {MANIFEST}")
    else:
        print(f"\ndry run — {len(record)} question(s), {failed} failing")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
