"""Return every approved question to pending, because the approvals were never reviews.

WHY. Approval was granted by a confidence threshold — roughly "confidence > 0.9 is good
enough" — and confidence in most of this bank is the GENERATING MODEL'S OWN self-report.
Asking a model whether it got the question right, and then trusting the answer, is not
review. The bank has already proved the point three times:

  - August 2026: 139 questions carried the model's scratchpad in the explanation. Comparing
    the working against the stored key found 36 with no correct option at all and 43 whose
    working supported a different option. Two of those were approved and being served.
  - August 2026: an answer-key skew across ~4,900 questions, most of them approved, where
    answering C to every reading question scored 48%.
  - This session: 10 more quantitative questions with no correct answer and 5 wrong keys,
    one of them approved and live. All had passed the confidence bar.

WHAT THE DATABASE SAYS ABOUT THOSE 5,306 APPROVALS. This is not a matter of recollection:

  - There are **2 distinct `reviewed_at` values** across all 5,306 rows. One of them covers
    **3,571 rows spanning four subjects, identical to the microsecond** — a single bulk
    UPDATE.
  - **1,734 approved rows have `reviewed_at` NULL.** They were approved without any review
    event being recorded at all.
  - The minimum confidence per subject lands exactly on threshold boundaries — 0.90, 0.92,
    0.95, 0.95, 0.95 — which is the signature of a cutoff, not of judgement.
  - Exactly **one** row carries its own individual timestamp (2026-05-29). One row out of
    5,306 looks like somebody looked at something.

`edited = 1` on 2,355 approved rows is NOT evidence of review; that flag was set by the
repair tools in this repo (key skew, length tell, leaked working), by machine.

So the approved state carries no information and is actively misleading: it marks 5,306
questions as checked when the checking never happened, and it is the flag `push_to_selectly`
uses to decide what students see.

WHAT THIS COSTS, STATED PLAINLY. `push_to_selectly.py` sends approved questions only. After
this runs, **nothing is sendable** until real review happens. That is the intended
consequence — an empty drill bank is honest where a bank of 5,306 unverified questions is
not — but it means the Selectly reload has nothing to reload until the review queue moves.

Form assignments are untouched: both `assign_forms.py` and `assign_writing_forms.py` deal
over approved AND pending, so the 117 MCQ forms and 27 writing forms survive intact.

Fully reversible. Every id, its prior `review_status` and its prior `reviewed_at` are
recorded, and `--revert` restores them exactly.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.reset_approvals --dry-run
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.reset_approvals --apply
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.reset_approvals --revert
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "run_data" / "db" / "qbank.db"
MANIFEST = REPO_ROOT / "run_data" / "output" / "approval_reset_manifest.json"


def evidence(conn: sqlite3.Connection) -> None:
    """Print why these approvals cannot be trusted, before changing anything."""
    n = conn.execute("SELECT COUNT(*) FROM questions WHERE review_status='approved'").fetchone()[0]
    distinct = conn.execute("SELECT COUNT(DISTINCT reviewed_at) FROM questions "
                            "WHERE review_status='approved'").fetchone()[0]
    nulls = conn.execute("SELECT COUNT(*) FROM questions WHERE review_status='approved' "
                         "AND reviewed_at IS NULL").fetchone()[0]
    print(f"{n} approved questions, {distinct} distinct reviewed_at value(s), "
          f"{nulls} with none at all")
    print("\nlargest timestamp clusters — a bulk UPDATE looks like one timestamp:")
    for r in conn.execute(
            "SELECT reviewed_at, COUNT(*) n, COUNT(DISTINCT subject) s, "
            "MIN(confidence) mn FROM questions WHERE review_status='approved' "
            "GROUP BY 1 ORDER BY n DESC LIMIT 5"):
        print(f"   {str(r[0])[:26]:<28} {r[1]:>5} rows, {r[2]} subject(s), min conf {r[3]}")
    print("\nminimum confidence per subject — a cutoff leaves a flat floor:")
    for r in conn.execute("SELECT subject, MIN(confidence), COUNT(*) FROM questions "
                          "WHERE review_status='approved' GROUP BY 1 ORDER BY 2"):
        print(f"   {r[0]:<24} {r[1]}   ({r[2]} rows)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--revert", action="store_true")
    args = ap.parse_args()
    if not (args.dry_run or args.apply or args.revert):
        ap.error("choose --dry-run, --apply or --revert")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    if args.revert:
        if not MANIFEST.exists():
            raise SystemExit(f"no manifest at {MANIFEST} — nothing to revert")
        data = json.loads(MANIFEST.read_text())
        rows = data["reset"]
        conn.executemany(
            "UPDATE questions SET review_status = ?, reviewed_at = ? WHERE id = ?",
            [(r["was_status"], r["was_reviewed_at"], r["id"]) for r in rows])
        conn.commit()
        print(f"Reverted {len(rows)} questions to their prior state.")
        return

    evidence(conn)

    rows = [dict(r) for r in conn.execute(
        "SELECT id, subject, source_book, confidence, review_status, reviewed_at "
        "FROM questions WHERE review_status = 'approved'")]

    print(f"\n{'subject':<24}{'to pending':>12}")
    by: dict[str, int] = {}
    for r in rows:
        by[r["subject"]] = by.get(r["subject"], 0) + 1
    for k, v in sorted(by.items(), key=lambda kv: -kv[1]):
        print(f"{k:<24}{v:>12}")
    print(f"{'TOTAL':<24}{len(rows):>12}")

    print("\nAfter this, push_to_selectly has 0 sendable questions until review happens.")
    print("Form assignments are unaffected — forms were dealt over approved AND pending.")

    if args.apply:
        now = datetime.now(timezone.utc).isoformat()
        conn.executemany(
            "UPDATE questions SET review_status = 'pending', reviewed_at = NULL "
            "WHERE id = ?", [(r["id"],) for r in rows])
        conn.commit()
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(json.dumps({
            "generated_from": "tools/reset_approvals.py",
            "applied_at": now,
            "why": "approval was a confidence threshold over model self-reported "
                   "confidence, not human review; 2 distinct reviewed_at values across "
                   "5,306 rows and 1,734 with none",
            "reset": [{"id": r["id"], "subject": r["subject"],
                       "source_book": r["source_book"], "confidence": r["confidence"],
                       "was_status": r["review_status"],
                       "was_reviewed_at": r["reviewed_at"]} for r in rows],
        }, indent=2))
        print(f"\nReset {len(rows)} questions to pending. Revert record: {MANIFEST}")
    else:
        print(f"\nDry run: {len(rows)} would move to pending. Nothing written.")


if __name__ == "__main__":
    main()
