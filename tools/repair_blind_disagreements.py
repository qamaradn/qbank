"""Act on questions where an independent blind re-solve disagreed with the stored key.

This is the repair half of the workflow `pipeline/blind_solve.py` opens. The solver never
sees the key and the options are shuffled, so a disagreement is real evidence that
something is wrong — but it does not say WHAT, and roughly a third of the time the solver
is the one who is wrong. So every entry here is a human decision with the working that
settled it, in the same shape as tools/repair_broken_working.py.

Three verdicts:

  reject   no option is correct as the question stands.
  rekey    the working is right and the stored key is wrong — the pattern established by
           the August leaked-working repair, which found 42 of these.
  keep     the solver was wrong. Recorded so the same question is not re-adjudicated, and
           so a pattern of solver error is visible if one develops.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_blind_disagreements --dry-run
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_blind_disagreements --apply
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "run_data" / "db" / "qbank.db"
MANIFEST = REPO_ROOT / "run_data" / "output" / "blind_disagreement_repairs.json"

# (id, verdict, new_key or None, why)
DECISIONS: list[tuple[str, str, str | None, str]] = [
    ("05647390-eea2-42f0-9ee0-006ad7c78cc8", "reject", None,
     "Koala climbs 3 m and slides 1 m EACH HOUR, so it nets 2 m per hour: 10 m after 5 "
     "hours, and hour 6 takes it to 13 m, past the 12 m top. The answer is 6 hours and no "
     "option offers it. The stored explanation reaches 10 by treating a climb-and-slide "
     "cycle as two hours ('after 8 hours (4 cycles) the koala is at 8 m'), which "
     "contradicts the stem it is explaining."),
    ("074b9ee4-d419-4a38-b53a-a017a685e762", "rekey", "D",
     "AB is parallel to CD and BC is a transversal, so angle ABC and angle BCD are "
     "co-interior and sum to 180: BCD = 65 degrees. The stored EXPLANATION derives 65 and "
     "then the question is keyed to 115. (The symmetry framing is also loose — AB = CD = 5 "
     "on the parallel sides describes a parallelogram, which has no line of symmetry — but "
     "the co-interior answer holds regardless.)"),
    ("0ac8b411-b5cc-403a-9eec-6dc13bc8c88c", "rekey", "C",
     "Read from the figure rather than the explanation. The transversal meets PQ at "
     "(113,70) and RS at (167,150). The 65-degree label sits at (118,64) — above PQ, right "
     "of the transversal. The b label sits at (148,168) — BELOW RS and to its LEFT, so b is "
     "outside the parallel strip and is NOT co-interior with a. b is vertically opposite "
     "the angle corresponding to a, so b = 65 degrees. The explanation assumed co-interior "
     "without checking where b was drawn."),
    ("11f391af-7696-41d2-a8ef-490d4c1df08b", "reject", None,
     "The temperature falls 13 degrees in 45 minutes, so over 120 minutes it falls 34.67 "
     "and lands at -2.67 degrees. The options are 8, -2, -3 and 6. No option is that value, "
     "and the stored explanation picks -2 while stating -2.7, which is nearer to -3. Same "
     "class as the other 'closest option' items rejected on 2026-08-12."),
    # --- vic-drill-mq-002, 2026-08-13
    ("77951e11-a393-4865-aeea-771786330a4a", "reject", None,
     "The figure's gridlines sit at 0/100/200/300 with 40 px between them, so the five "
     "bars are 200, 250, 300, 225 and 175 and the difference is 175. The stored "
     "explanation reads them as 160/200/240/180/140 (a 50 px scale) and computes 140. The "
     "key says 120. Figure, explanation and key give three different answers and none of "
     "them is an option."),
    ("8f4640fa-579b-4852-8847-65a1f6e9ad23", "reject", None,
     "The figure is internally consistent — right angle marked at P, legs PQ = 12 and "
     "PR = 5, hypotenuse QR = 13 — but the stem asks for sin of angle QPR, which IS that "
     "right angle, so the answer would be 1. The keyed 12/13 is the sine of the angle at "
     "R. The stored explanation describes a third arrangement again (right angle at Q, "
     "PQ = 5, QR = 12). A student is shown the figure, so the question they see is "
     "unanswerable."),
    ("b5c3f5f4-9d64-4ccb-a0e6-3384e3c97b1a", "keep", None,
     "FIGURE REPAIRED rather than the question rejected. A(1,2), B(5,6) and the marked "
     "midpoint M(3,4) sit on evenly spaced gridlines that were LABELLED 0, 1, 3, 5 — a "
     "mislabelled axis, so no reading of the figure gave the keyed (3,4). Relabelled to "
     "0, 2, 4, 6, at which point the points, the marked midpoint, the explanation and the "
     "key all agree. The key was right; the axis was wrong."),
    # --- vic-drill-mq-005, 2026-08-13
    ("8139103c-b653-4196-ab7a-db8366af40f1", "rekey", "A",
     "Line CD through (0,4) and (4,0) is y = -x + 4; line EF through (0,-2) and (2,2) is "
     "y = 2x - 2. They meet where -x + 4 = 2x - 2, so x = 2 and y = 2: the point (2,2). "
     "The stored explanation derives x = 2 and then the question is keyed to (3,1)."),
    ("8beb02e5-b611-48c0-8a0c-a6b79b58df4d", "rekey", "B",
     "580 = 24 x 24 + 4, so twenty-four boxes are full and four tins are left over, "
     "needing a twenty-fifth box holding 4 tins. The stored explanation says exactly that "
     "-- '25 boxes total, with 4 tins in the last box' -- and the question is keyed to "
     "'25 boxes, 20 tins in the last box'."),
    # --- vic-drill-rv-001, 2026-08-13
    ("74aabde5-69a9-4f38-91c1-afcb49e09bae", "keep", None,
     "THE SOLVER WAS WRONG, and this is the first time in the campaign. Asked for the "
     "'underlying reason' behind the dingo's duality, I chose the concrete mechanism -- "
     "ecologically beneficial, economically threatening -- where the key chooses the "
     "level above it: a society struggling to balance conservation against economic "
     "interests. Both are supported, but the stem asks for the reason BEHIND the two "
     "sides, not a restatement of them, so the key is the better reading. Recorded so "
     "the question is not re-adjudicated and so a pattern of solver error stays visible."),
    # --- vic-drill-rv-003, 2026-08-13
    ("b704028e-6928-4418-8b1c-bfbfd60628d1", "keep", None,
     "SOLVER LOSS, second of the campaign and the second of this kind. A 'which detail "
     "LEAST supports' question with four genuinely supportive details is soft by "
     "construction. The key says the diet list supports resilience least, and its "
     "reasoning holds: long-distance travel, an eight-week fast and thermal insulation "
     "are each an ACTIVE response to hardship, while the diet is presented as a list of "
     "foods rather than a claim about adaptability. I picked the fast, reading it as a "
     "cost rather than an adaptation. Defensible, but not better than the key."),
]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    if not (args.dry_run or args.apply):
        ap.error("choose --dry-run or --apply")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    now = datetime.now(timezone.utc).isoformat()
    record = []
    already_recorded = {r["id"] for r in
                        (json.loads(MANIFEST.read_text())["repairs"]
                         if MANIFEST.exists() else [])}

    for qid, verdict, new_key, why in DECISIONS:
        row = conn.execute("SELECT * FROM questions WHERE id = ?", (qid,)).fetchone()
        if row is None:
            print(f"MISSING {qid}")
            continue
        if verdict == "reject" and row["review_status"] == "rejected":
            print(f"skip  {qid} — already rejected")
            continue
        if verdict == "rekey" and row["correct_answer"] == new_key:
            print(f"skip  {qid} — already keyed {new_key}")
            continue
        # A "keep" changes nothing, so the state checks above can never suppress it and
        # every re-run appended another copy to the manifest. Skip it once it is recorded.
        if verdict == "keep" and qid in already_recorded:
            print(f"skip  {qid} — keep already recorded")
            continue
        print(f"\n{verdict.upper():<7}{qid}  [{row['source_book']}]")
        print(f"   {' '.join(row['stem'].split())[:110]}")
        print(f"   {why[:200]}")
        record.append({"id": qid, "verdict": verdict, "was_key": row["correct_answer"],
                       "new_key": new_key, "was_status": row["review_status"], "why": why})
        if args.apply:
            if verdict == "reject":
                conn.execute("UPDATE questions SET review_status='rejected', reviewed_at=? "
                             "WHERE id=?", (now, qid))
            elif verdict == "rekey":
                conn.execute("UPDATE questions SET correct_answer=?, explanation=?, "
                             "edited=1 WHERE id=?", (new_key, why, qid))

    if args.apply:
        conn.commit()
        prior = json.loads(MANIFEST.read_text())["repairs"] if MANIFEST.exists() else []
        MANIFEST.write_text(json.dumps(
            {"generated_from": "tools/repair_blind_disagreements.py",
             "applied_at": now, "repairs": prior + record}, indent=2))
        print(f"\napplied {len(record)}; record -> {MANIFEST}")
    else:
        print(f"\ndry run: {len(record)} would be applied")


if __name__ == "__main__":
    main()
