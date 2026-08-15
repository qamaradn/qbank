#!/usr/bin/env python3
"""Approve (or un-approve) every question in named drill forms.

Approval is the pusher's filter -- `fetch_approved` sends `review_status='approved'`
and nothing else -- so approving a form is what makes it reachable by Selectly. This
exists because the pilot needs exactly ten forms live and nothing else, and clicking
through 300 rows in the review UI to achieve that would be absurd.

This is NOT a substitute for review. It marks questions as ready to be SERVED TO A
REVIEWER in Selectly, which is the pilot's whole point: the reviewer is the check, and
the flags they raise come back as CSV. Everything approved here is still unreviewed by
a human.

Revertible: every change is recorded, and --revert restores the prior status exactly.
"""
import argparse
import json
import pathlib
import sqlite3

ROOT = pathlib.Path(__file__).resolve().parents[1]
DB = ROOT / "run_data/db/qbank.db"
RECORD = ROOT / "run_data/output/form_approvals.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("forms", nargs="*", help="form_ids, e.g. vic-drill-mq-001")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--revert", action="store_true", help="restore statuses from the record")
    ap.add_argument("--status", default="approved", choices=["approved", "pending"])
    args = ap.parse_args()

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row

    if args.revert:
        if not RECORD.exists():
            raise SystemExit(f"no record at {RECORD}")
        rec = json.loads(RECORD.read_text())
        for x in rec:
            if args.apply:
                con.execute("UPDATE questions SET review_status=? WHERE id=?",
                            (x["was"], x["id"]))
        print(f"{'reverted' if args.apply else 'would revert'} {len(rec)} questions")
        if args.apply:
            con.commit()
            RECORD.unlink()
        return

    if not args.forms:
        raise SystemExit("name at least one form, or pass --revert")

    record, skipped = [], 0
    for f in args.forms:
        rows = [dict(r) for r in con.execute(
            "SELECT id, review_status FROM questions WHERE form_id=?", (f,))]
        if not rows:
            raise SystemExit(f"no questions carry form_id={f!r} — check the name")
        # A rejected question is rejected for a reason; approving it in bulk would put a
        # known-bad item in front of the reviewer and waste the round.
        live = [r for r in rows if r["review_status"] != "rejected"]
        skipped += len(rows) - len(live)
        for r in live:
            if r["review_status"] == args.status:
                continue
            record.append({"id": r["id"], "form_id": f, "was": r["review_status"],
                           "now": args.status})
        print(f"  {f:<22} {len(live):>3} questions"
              + (f"  ({len(rows) - len(live)} rejected, left alone)" if len(rows) != len(live) else ""))

    if args.apply:
        for x in record:
            con.execute("UPDATE questions SET review_status=? WHERE id=?",
                        (x["now"], x["id"]))
        con.commit()
        prior = json.loads(RECORD.read_text()) if RECORD.exists() else []
        seen = {x["id"] for x in prior}
        RECORD.write_text(json.dumps(
            prior + [x for x in record if x["id"] not in seen], indent=2) + "\n")
        print(f"\nset {len(record)} questions to {args.status}; record -> {RECORD}")
    else:
        print(f"\n{len(record)} questions would become {args.status} "
              f"({skipped} rejected left alone) — dry run, pass --apply")


if __name__ == "__main__":
    main()
