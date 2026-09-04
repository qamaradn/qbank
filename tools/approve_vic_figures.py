#!/usr/bin/env python3
"""Approve every VIC question that carries a figure.

The owner's instruction, 2026-09-04, once the figure review rounds closed: "mark all
figure question in VIC as approved in the qbank".

What approval means here is what it has always meant in this project, and it is worth
restating because the word is misleading: `review_status='approved'` is the pusher's
filter -- `push_to_selectly` sends approved rows and nothing else -- so approving is what
makes a question REACHABLE BY A REVIEWER in Selectly. It is not a claim that a human has
read the question. The figure rounds checked the pictures; the words and the keys are
still unreviewed.

Scope: every question whose `form_id` starts `vic-drill-` and whose `figure_svg` is not
empty. VIC reading and verbal carry no figures, so in practice this is the maths and
quantitative forms.

Revertible: the prior status of every row is recorded, and --revert restores it exactly.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.approve_vic_figures
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.approve_vic_figures --apply
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.approve_vic_figures --revert --apply
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sqlite3

ROOT = pathlib.Path(__file__).resolve().parents[1]
DB = ROOT / "run_data/db/qbank.db"
RECORD = ROOT / "run_data/output/vic_figure_approvals.json"

SELECT = """
    SELECT id, form_id, review_status, source_book FROM questions
     WHERE form_id LIKE 'vic-drill-%'
       AND figure_svg IS NOT NULL AND figure_svg != ''
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--revert", action="store_true")
    args = ap.parse_args()
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row

    if args.revert:
        if not RECORD.exists():
            raise SystemExit(f"no record at {RECORD}")
        rec = json.loads(RECORD.read_text())
        if args.apply:
            for x in rec:
                con.execute("UPDATE questions SET review_status=? WHERE id=?",
                            (x["was"], x["id"]))
            con.commit()
        print(f"{'reverted' if args.apply else 'would revert'} {len(rec)} questions")
        return

    rows = [dict(r) for r in con.execute(SELECT)]
    before = collections.Counter(r["review_status"] for r in rows)
    todo = [r for r in rows if r["review_status"] != "approved"]
    rejected = [r for r in rows if r["review_status"] == "rejected"]
    print(f"VIC questions carrying a figure: {len(rows)}")
    print(f"  already approved : {before.get('approved', 0)}")
    print(f"  pending          : {before.get('pending', 0)}")
    print(f"  rejected         : {before.get('rejected', 0)}"
          f"{'  <- these are NOT approved' if rejected else ''}")
    todo = [r for r in todo if r["review_status"] == "pending"]
    print(f"  to approve       : {len(todo)}")
    by_form = collections.Counter(r["form_id"] for r in todo)
    print(f"  spread over {len(by_form)} forms")
    if args.apply:
        RECORD.parent.mkdir(parents=True, exist_ok=True)
        RECORD.write_text(json.dumps(
            [{"id": r["id"], "was": r["review_status"]} for r in todo], indent=1))
        for r in todo:
            con.execute("UPDATE questions SET review_status='approved', "
                        "reviewed_at=datetime('now') WHERE id=?", (r["id"],))
        con.commit()
        print("APPLIED")
    else:
        print("dry run")


if __name__ == "__main__":
    main()
