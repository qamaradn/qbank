#!/usr/bin/env python3
"""Numbered contact sheets for a by-eye pass over the VIC figures, plus an index.

A reviewer flipping through twenty figures cannot read "7c472f4d" off the page and
say it out loud, so the sheets this builds number every tile 1, 2, 3 ... across the
whole run. You call out the numbers of the ones that look wrong; the index maps each
number back to the question id, book, form and stem.

WHAT TO LOOK FOR, and why the two kinds matter differently:

  READABILITY -- a label over a line, a number too pale to read, something clipped
  off the edge, two labels printed on top of each other. Fast to spot, and the fix
  is mechanical.

  CORRECTNESS -- the picture is tidy and says something the question does not: a
  shape drawn to the wrong proportions, a point plotted a unit out, an "octagon"
  with ten sides. These are the ones the checks keep missing, and the ones worth
  slowing down for. Where the words matter, the index gives the stem.

Numbers alone are enough -- "14, 22, 31" is a complete report and the figure gets
read properly from there. A word or two ("label on the line", "shape wrong") is
better, because it says whether the fault is readability or correctness, and that
decides whether it can become a check.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.figure_review_sheets --scope vic-mq
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.figure_review_sheets \
        --scope vic-mq --book year9_maths
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import gate_forms as gf                       # noqa: E402
from tools.figure_contact_sheet import build_sheet       # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
OUT = ROOT / "run_data/figure_sheets/review"

SCOPES = {
    # Every VIC figure lives in maths+quant; reading and verbal carry none.
    "vic-mq": ("(subject = 'quantitative_reasoning' "
               "OR source_book IN ('year9_maths','ma_vic_stats'))"),
    "nsw-ma": ("(source_book IN ('year7_nsw_maths','ma_nsw_selective'))"),
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scope", choices=sorted(SCOPES), default="vic-mq")
    ap.add_argument("--book", help="one source_book only")
    ap.add_argument("--per-sheet", type=int, default=12)
    ap.add_argument("--status", default="pending",
                    help="review_status to include (default pending; 'any' for all)")
    ap.add_argument("--include-flagged", action="store_true",
                    help="also include figures a BLOCKING check already catches "
                         "(by default those are left to the repair tools, so a human "
                         "is not spent on a fault already diagnosed)")
    a = ap.parse_args()

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    sql = ("SELECT * FROM questions WHERE figure_svg IS NOT NULL AND figure_svg != '' "
           f"AND review_status != 'rejected' AND {SCOPES[a.scope]}")
    args: list = []
    if a.status != "any":
        sql += " AND review_status = ?"
        args.append(a.status)
    if a.book:
        sql += " AND source_book = ?"
        args.append(a.book)
    rows = [dict(r) for r in con.execute(sql, args)]

    flagged = {q["id"] for q in rows
               if any(gf.run_check(n, q) for n, _ in gf.BLOCKING)}
    if not a.include_flagged:
        rows = [q for q in rows if q["id"] not in flagged]
    # Grouped by book then form, so consecutive numbers look alike and the eye is not
    # re-calibrating between every tile.
    rows.sort(key=lambda q: (q["source_book"] or "", q["form_id"] or "",
                             q["form_position"] or 0))

    if not rows:
        print("nothing to sheet")
        return 1
    OUT.mkdir(parents=True, exist_ok=True)
    index, n = [], 1
    sheets = 0
    failures: list = []
    for i in range(0, len(rows), a.per_sheet):
        batch = rows[i:i + a.per_sheet]
        name = f"{a.scope}_{sheets + 1:02d}.png"
        build_sheet([(q["source_book"][:18], q["figure_svg"]) for q in batch],
                    OUT / name, start=n, failures=failures)
        for j, q in enumerate(batch):
            index.append({"n": n + j, "sheet": name, "id": q["id"],
                          "book": q["source_book"], "form": q["form_id"],
                          "pos": q["form_position"],
                          "stem": " ".join((q["stem"] or "").split())[:150]})
        n += len(batch)
        sheets += 1

    (OUT / f"{a.scope}_index.json").write_text(json.dumps(index, indent=1,
                                                          ensure_ascii=False))
    lines = [f"{x['n']:>4}  {x['sheet']:<16} {x['id'][:8]}  {x['book']:<22} "
             f"{str(x['form']):<18} {x['stem'][:90]}" for x in index]
    (OUT / f"{a.scope}_index.txt").write_text("\n".join(lines) + "\n")

    print(f"{len(rows)} figures over {sheets} sheet(s), numbered 1-{n - 1}")
    if failures:
        print(f"\n{len(failures)} figure(s) would NOT render at all:")
        for num, lab, err in failures:
            row = next(x for x in index if x["n"] == num)
            print(f"   #{num} {row['id'][:8]} {row['book']:<22} {err}")
    if not a.include_flagged:
        print(f"{len(flagged)} left out — a BLOCKING check already names their fault")
    print(f"\nsheets : {OUT}/{a.scope}_01.png ...")
    print(f"index  : {OUT}/{a.scope}_index.txt")
    print("\nCall out the numbers that look wrong. A word on WHY helps but is optional.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
