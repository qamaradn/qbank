#!/usr/bin/env python3
"""Approve writing prompts so the pusher can send them.

The owner's call, 2026-09-05: "writing prompts don't need much review. Approve all."

Approval here means what it means everywhere else in this project -- it is the pusher's
filter, so approving is what makes a prompt REACHABLE by a reviewer in Selectly. It is
not a claim that a human has read it. `push_writing_to_selectly` sends approved rows and
nothing else, so with all 106 pending nothing could ever go.

Revertible: the prior status of every row is recorded and --revert restores it exactly.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.approve_writing_prompts
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.approve_writing_prompts --apply
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.approve_writing_prompts --revert --apply
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sqlite3

ROOT = pathlib.Path(__file__).resolve().parents[1]
DB = ROOT / "run_data/db/qbank.db"
RECORD = ROOT / "run_data/output/writing_prompt_approvals.json"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--revert", action="store_true")
    ap.add_argument("--school-type", help="only this school_type")
    args = ap.parse_args()
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row

    if args.revert:
        if not RECORD.exists():
            raise SystemExit(f"no record at {RECORD}")
        rec = json.loads(RECORD.read_text())
        if args.apply:
            for x in rec:
                con.execute("UPDATE writing_prompts SET review_status=? WHERE id=?",
                            (x["was"], x["id"]))
            con.commit()
        print(f"{'reverted' if args.apply else 'would revert'} {len(rec)} prompts")
        return

    where, params = ["review_status = 'pending'"], []
    if args.school_type:
        where.append("school_type = ?")
        params.append(args.school_type)
    rows = [dict(r) for r in con.execute(
        f"SELECT * FROM writing_prompts WHERE {' AND '.join(where)}", params)]
    by = collections.Counter(
        (r["school_type"], "in a form" if r["form_id"] else "no form") for r in rows)
    print(f"pending writing prompts to approve: {len(rows)}")
    for (st, f), n in sorted(by.items()):
        print(f"   {st:<22} {f:<10} {n}")
    if args.apply:
        RECORD.parent.mkdir(parents=True, exist_ok=True)
        RECORD.write_text(json.dumps(
            [{"id": r["id"], "was": r["review_status"]} for r in rows], indent=1))
        for r in rows:
            con.execute("UPDATE writing_prompts SET review_status='approved', "
                        "reviewed_at=datetime('now') WHERE id=?", (r["id"],))
        con.commit()
        print("APPLIED")
    else:
        print("dry run")


if __name__ == "__main__":
    main()
