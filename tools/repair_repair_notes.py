#!/usr/bin/env python3
"""Take the repair notes out of the explanations students read.

Round 5 found one of these on `8139103c` -- "the question is keyed to (3,1)" sitting
in the field a Year 8 student reads -- and recorded it as a one-off. It was one of
thirteen. They are the residue of the key repairs of August 2026: the working was
corrected and IS correct, and then a sentence explains what the previous explanation
or the previous key got wrong. That sentence is addressed to whoever was fixing the
bank. It reaches the student instead, and tells them their question used to have a
different answer.

The worst is `0ac8b411`, one of the two figures flagged in review round 6. It opens
"Read from the figure rather than the explanation" and then reasons in SVG PIXEL
COORDINATES -- "the b label sits at (148,168)" -- naming nothing a student can see.

WHY THESE ARE HAND-WRITTEN. Stripping the trailing sentence would clear the check on
most of them, and would leave `0ac8b411` reasoning in pixels and `074b9ee4` with a
parenthesis about a parallelogram that is a note to a repairer too. Every key below
was re-derived from the stem and the options before its explanation was rewritten;
the script refuses to write if any of them no longer matches the stored key.

`explanation_is_a_repair_note` is the check, and it is BLOCKING.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_repair_notes --dry-run
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_repair_notes --apply
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import question_checks as qc          # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
MANIFEST = ROOT / "run_data/output/repair_note_rewrites.json"

# id prefix -> (expected key, new explanation). The key is asserted, not read: if a
# later repair re-keys one of these, the rewrite below stops being true and this
# refuses to run rather than writing a confident wrong explanation.
REWRITES = {
    "6631df7f": ("D",
        "Growth of 15% a year multiplies the population by 1.15 each year, so after "
        "two years it is 5 000 x 1.15 x 1.15 = 5 000 x 1.3225 = 6 612.5, which rounds "
        "to 6 612 kangaroos. 6 500 applies 15% once; 6 750 adds 15% of the ORIGINAL "
        "5 000 twice, which is simple interest rather than compound growth."),
    "2203f240": ("C",
        "Try each operation: plus gives (4 + 8) - 5 = 7; divided by gives (4 / 8) - 5 "
        "= -4.5; minus gives (4 - 8) - 5 = -9; multiplied by gives (4 x 8) - 5 = 27. "
        "The smallest result is -9, so the operation is minus."),
    "cb520797": ("C",
        "The line through (0, 8) and (4, 4) falls 4 units as it runs 4 units across, "
        "so its gradient is -1. The ACUTE angle a line makes with the x-axis is "
        "measured as a positive turn, and tan 45 = 1, so tan phi = 1 and phi = 45 "
        "degrees. Option A pairs tan phi = -1 with phi = 45 degrees, which "
        "contradicts itself, since tan 45 is +1."),
    "0ac8b411": ("C",
        "Angle a is marked above PQ on the right of the transversal, and angle b is "
        "marked below RS on the left of it. Both therefore lie OUTSIDE the pair of "
        "parallel lines and on opposite sides of the transversal, which makes them "
        "alternate exterior angles. Alternate angles across a transversal cutting "
        "parallel lines are equal, so b = a = 65 degrees. 115 degrees would be right "
        "only if b were co-interior with a, which needs both angles between the two "
        "parallel lines."),
    "b49b2c69": ("C",
        "Over the 5 years from the start of 2010, maths enrolments rise from 4 to 16, "
        "which is 2.4 a year, and science rises from 2 to 20, which is 3.6 a year. "
        "They are equal when 4 + 2.4t = 2 + 3.6t, so 1.2t = 2 and t = 5/3 years - "
        "about 8 months into 2011. Science overtakes maths during 2011."),
    "fd4d2c94": ("B",
        "Line l passes through P(0, 4) and Q(2, 0), so its gradient is (0 - 4) / "
        "(2 - 0) = -2. A perpendicular line has the negative reciprocal gradient, "
        "which is +1/2, and passing through the origin its equation is y = x/2. "
        "y = -x/2 uses the wrong sign: the negative reciprocal of -2 is +1/2."),
    "5f486830": ("B",
        "Total distance is (20 x 3) + (30 x 5) + (40 x 7) + (50 x 4) + (60 x 1) = "
        "60 + 150 + 280 + 200 + 60 = 750 km over 3 + 5 + 7 + 4 + 1 = 20 members, so "
        "the mean is 750 / 20 = 37.5 km. The question asks to the nearest kilometre, "
        "and 37.5 rounds up to 38 km."),
    "074b9ee4": ("D",
        "AB is parallel to CD and BC crosses both, so angle ABC and angle BCD are "
        "co-interior angles and add to 180 degrees. Angle BCD = 180 - 115 = 65 "
        "degrees. 115 degrees would make them equal, which is true of corresponding "
        "or alternate angles, not co-interior ones."),
    "a016ffb4": ("B",
        "AB is vertical with length 6 and lies on the line x = 2, so taking AB as the "
        "base, the height of the triangle is the horizontal distance from C to that "
        "line. Area = 1/2 x 6 x |x - 2| = 24 gives |x - 2| = 8, so x = 10 and C is "
        "(10, 0). (8, 0) sits 6 across and gives an area of 18."),
    "ab970adf": ("D",
        "Row 1 has 1 black square, row 2 has 2, row 3 has 3 and row 4 has 4 - the "
        "black squares sit at the odd positions of each row. That is 1 + 2 + 3 + 4 = "
        "10 black squares, each 1 cm², so the black area is 10 cm². 16 cm² counts "
        "every square in the four rows rather than only the black ones."),
    "928d3c31": ("C",
        "The arrangement is a Z-pentomino: two cells at the top left, a vertical "
        "middle column, two at the bottom right. Adding one square above or below the "
        "middle column each gives a 1-4-1 net, and adding one above the top-left cell "
        "or below the bottom-right cell each gives a valid net as well - 4 positions. "
        "Of the other adjacent cells, two would make a 2 x 2 block and two would put "
        "the same face on the cube twice."),
    "7162daf3": ("B",
        "Shape A is two cards side by side along their long sides, so its perimeter "
        "is 2L + 4W = 60, giving L + 2W = 30. Both L = 14, W = 8 and L = 16, W = 7 "
        "satisfy that, so Shape A alone cannot decide it. Adding the third card on "
        "top adds 2W to the perimeter: 74 - 60 = 14 = 2W, so W = 7 and L = 30 - 14 = "
        "16 cm."),
    "8beb02e5": ("B",
        "580 divided by 24 is 24 remainder 4, since 24 x 24 = 576. So 24 boxes are "
        "filled completely and 4 tins are left over, which need a 25th box: 25 boxes, "
        "with 4 tins in the last one."),
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

    for prefix, (want_key, new) in REWRITES.items():
        row = con.execute("SELECT * FROM questions WHERE id LIKE ?||'%'",
                          (prefix,)).fetchone()
        if row is None:
            raise SystemExit(f"{prefix} is not in the database")
        q = dict(row)
        problems = []
        if q["correct_answer"] != want_key:
            problems.append(f"key is {q['correct_answer']}, this rewrite assumes "
                            f"{want_key}")
        if qc.explanation_is_a_repair_note({**q, "explanation": new}):
            problems.append("the replacement still reads as a repair note")
        for name in ("leaked_working", "disputes_its_own_key", "rewrites_the_question"):
            if getattr(qc, name)(new):
                problems.append(f"{name} fires on the replacement")
        failed += bool(problems)
        print(f"{prefix}  key {q['correct_answer']}  "
              f"{'OK' if not problems else 'REFUSED'}")
        for p in problems:
            print(f"      ! {p}")
        record.append(dict(id=q["id"], form_id=q["form_id"], key=q["correct_answer"],
                           old=q["explanation"], new=new, problems=problems))
        if a.apply and not problems:
            con.execute("UPDATE questions SET explanation=? WHERE id=?",
                        (new, q["id"]))

    left = [r for r in con.execute(
        "SELECT id, explanation FROM questions WHERE review_status != 'rejected'")
        if qc.explanation_is_a_repair_note({"explanation": r["explanation"]})]

    if a.apply:
        if failed:
            con.rollback()
            raise SystemExit(f"\n{failed} refused — nothing written")
        con.commit()
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(json.dumps(record, indent=1, ensure_ascii=False))
        left = [r for r in con.execute(
            "SELECT id, explanation FROM questions WHERE review_status != 'rejected'")
            if qc.explanation_is_a_repair_note({"explanation": r["explanation"]})]
        print(f"\nrewrote {len(record)} — manifest {MANIFEST}")
    else:
        print(f"\ndry run — {len(record)} rewrite(s), {failed} refused")
    print(f"repair notes remaining in the bank: {len(left)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
