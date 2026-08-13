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
    # --- vic-drill-mq-006, 2026-08-13
    ("35db858f-88f0-485c-9d70-777a8af6ef84", "keep", None,
     "FIGURE REDRAWN. The bars carried value labels 58, 63, 65, 67, 72 (mean and median "
     "both 65, difference 0), the explanation read them as 58, 62, 65, 67, 68 (difference "
     "1), and the key said 0.4 -- three different answers. The axis was also non-uniform, "
     "with 45 kg and 60 kg the same 45 px apart as 60 kg and 70 kg. Redrawn on a uniform "
     "55-75 scale with values 58, 62, 65, 67, 71: mean 64.6, median 65, difference 0.4, "
     "which is the key. The explanation now matches the figure."),
    ("bf760031-5f05-4a5f-ad4b-5a5cfb7b9517", "keep", None,
     "FIGURE REPAIRED. The rectangle is 6 by 4 units. The shaded left block spans 0-2 "
     "across the full height, worth 8 units, and the explanation takes the bottom-right "
     "block as 2 wide by 1 tall, worth 2, giving 10 of 24 = 5/12 = the key. The figure "
     "drew that block 2 units tall, making the shaded area 12 of 24 = one half, which is "
     "not among the options. Block height halved so the figure agrees with its own "
     "explanation and key."),
    # --- vic-drill-mq-007, 2026-08-13
    ("91cc3420-7397-4eda-91b4-6a6e90cf7ac6", "reject", None,
     "'Which of the following is NOT true' about 20, 14, 8, 2, ... where ALL FOUR "
     "statements are true. Common difference -6, fifth term -4, seventh term -16, and the "
     "sum of the first five is 20+14+8+2-4 = 40. The stored explanation computes that sum "
     "as 40 itself and then keys the question to the statement that says it is 40. There "
     "is no false statement to find."),
    # --- vic-drill-mq-008, 2026-08-13
    ("f27e0d63-1895-4624-bc80-e46cbf239db4", "keep", None,
     "STEM ALIGNED TO THE FIGURE. The stem said the sides were (2x+3) and (x-1), giving "
     "6x + 4 = 36 and x = 32/6 -- not a whole number and not an option. The FIGURE labels "
     "them (2x+1) and (x+2), giving 6x + 6 = 36 and x = 5, which IS an option. The key "
     "said 8, matching neither. The stored explanation reaches 32/6 and then says 'That "
     "doesn't give a whole number. Rechecking:' -- the model noticed and shipped it "
     "anyway. Stem rewritten to the figure's labels, key moved to 5, explanation redone."),
    # --- vic-drill-mq-009, 2026-08-13
    ("cfeaae43-f1be-4f96-82bc-7bc999a03410", "reject", None,
     "Underdetermined. A pentagon has five interior angles summing to 540; the stem gives "
     "TWO of them (the base angles, 65 each) and asks for a third, which leaves two "
     "unknowns. The stored explanation reads 'the two equal base angles' as two PAIRS, "
     "computes 4 x 65 = 260 and reaches 280 degrees -- not an option -- while the question "
     "is keyed to 150. Measuring the drawn figure gives roughly 244 degrees, a reflex "
     "angle, which is not an option either. Nothing here agrees with anything else."),
    # --- vic-drill-mq-010, 2026-08-13
    ("fd4d2c94-8ad0-42b1-ad8b-604443f8e5f4", "rekey", "B",
     "Line l runs through P(0,4) and Q(2,0), so its gradient is -2 and a perpendicular "
     "line has gradient +1/2, giving y = x/2 through the origin. The stored explanation "
     "derives exactly that -- 'slope of l = -2. A perpendicular line has slope = 1/2' -- "
     "and the question is keyed to y = -x/2, which is parallel-ish nonsense: the negative "
     "reciprocal of -2 is +1/2, not -1/2."),
    # --- vic-drill-rv-007, 2026-08-13
    ("9a6d405a-7f0b-408d-bb5b-c808a90165b3", "keep", None,
     "SOLVER LOSS. Asked how CSIRO's mandate evolved, I read the CONTENT of the examples "
     "(wheat and wool early, Wi-Fi and plastics later) and answered 'agricultural focus to "
     "technological innovation'. The key tracks the passage's own framing instead: it "
     "opens with 'research essential for the development of Australian industries' and "
     "closes on 'solving Australia's greatest challenges', which is specific industry "
     "support broadening into general scientific challenges. The key follows the text; my "
     "answer followed the examples."),
    # --- vic-drill-mq-011, 2026-08-13
    ("2203f240-1147-464e-bfdc-72f3f4b931fc", "rekey", "C",
     "(4 minus 8) - 5 = -9, which is smaller than (4 divided by 8) - 5 = -4.5. The stored "
     "explanation works all four out and states 'The smallest is -9, which is minus' -- "
     "and the question is keyed to 'divided by'."),
    ("9a6e0313-6f6d-4d8e-b195-24d164f1d657", "keep", None,
     "FIGURE REPAIRED. The keyed answer of 1/3 needs Dylan to eat 4 of the 12 pieces, "
     "which only works if ONE row is shaded: Jordan takes 4, leaving 8 unshaded, and "
     "Dylan eats all but one row of them, so 4. The figure shaded TWO full rows, leaving "
     "only one unshaded row, so 'all the unshaded except one row' left Dylan with nothing "
     "at all and no option applied. The stored explanation says Dylan ate 'the middle "
     "row', which is the row the figure had shaded. Middle row unshaded to match."),
    # --- vic-drill-mq-012, 2026-08-13
    ("87714921-cac5-48d0-8bb5-0801be49104f", "reject", None,
     "Three different answers and no agreement anywhere. The STEM puts Y two centimetres "
     "from D and Z two from A, which gives W(2,8), X(8,6), Y(2,0), Z(0,6) and an area of "
     "32. The stored EXPLANATION places Y at (6,0) and Z at (0,2) -- measuring from the "
     "other end of both sides -- which gives 40. The KEY says 52. None of the three is the "
     "same and 32 is not even an option."),
    ("928d3c31-29b5-4b1a-aaf8-d22af8958a3d", "rekey", "C",
     "The figure is a Z-pentomino: two cells top-left, a vertical middle, two "
     "bottom-right. Walking the fold from the middle column, four additions give six "
     "distinct faces -- above and below the middle column (each making a 1-4-1 net), and "
     "above the top-left cell and below the bottom-right cell. The other four adjacent "
     "cells fail: two make a 2x2 block, and two put a repeated face on the cube. So the "
     "answer is 4, not the keyed 2. The stored explanation calls the shape 'L-shaped', "
     "which it is not -- it counted for a different pentomino."),
    ("a016ffb4-44d8-4c44-b335-679526296975", "rekey", "B",
     "AB is vertical of length 6 on x = 2, so an area of 24 needs a horizontal distance of "
     "8 from that line: C is (10,0). The stored explanation derives exactly that -- "
     "'1/2 x 6 x |x - 2| = 24' -- and the question is keyed to (8,0), which gives an area "
     "of 18."),
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
