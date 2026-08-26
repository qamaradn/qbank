#!/usr/bin/env python3
"""Re-cut the Thinking Skills numeric-deduction items that need algebra, not reasoning.

    a00cb43b  "In my opinion, this question is more for maths rather than thinking."
    844bbdfe  "Again, more of a mathematical reasoning question (quadratic equation
               application) instead of thinking. Could potentially fit in but in my
               opinion shouldn't be here."

`numeric_deduction` is a real Thinking Skills subcategory with a target of 75, and the
official UCLES PT1 examples for it -- q1 marbles, q7 goats and kids, q37 dog legs -- are
themselves two-unknown problems. So "it has two unknowns" cannot be the test. The test is
whether the numbers YIELD TO REASONING or require algebraic manipulation, and by that
test the subcategory splits cleanly:

  11 of the 75 items set up two lettered unknowns. EIGHT are symmetric pairs --
  2r + b = 16 with r + 2b = 17 -- which add to give r + b and subtract to give r - b, so
  a student solves them by noticing, in well under the 60 seconds a question gets.

  THREE are not symmetric and need elimination with a multiplier. a00cb43b is the worst
  of them (6e + 2f = 46, 2e + 5f = 37, needing x3 on the second) and is the ONLY ONE OF
  THE ELEVEN THAT IS APPROVED -- which is why it is the one a reviewer saw. c99bf947 and
  c61a9369 carry the same defect and are still pending.

All three are re-cut to symmetric coefficients, keeping every key and every distractor.
That answers the reviewer without rejecting anything, which matters: these sit in
nsw-drill-ts forms, and CLAUDE.md is explicit that a rejection leaves a hole.

844bbdfe IS KEPT, and this is a disagreement with the reviewer worth recording. Its
stem reads algebraically -- "add up to 19 and multiply to 88" -- but no quadratic is
needed and none is used: the stored explanation already reasons "pairs adding to 19 are
1 and 18, 2 and 17, and so on. Only 8 and 11 multiply to 88." That is trial over factor
pairs, which is exactly what PT1's numeric deduction asks for. The reviewer hedged on
this one ("could potentially fit in") and the explanation they would not have seen while
solving is the evidence. Left in place, flagged here for the owner.

Usage:
    python -m tools.repair_nsw_round5_numeric --dry-run
    python -m tools.repair_nsw_round5_numeric --apply
"""
import argparse
import json
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import question_checks as qc      # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
MANIFEST = ROOT / "run_data/output/nsw_round5_numeric_repairs.json"

# Each re-cut keeps the two unit prices, so the key and all three distractors stand.
# The new coefficients are symmetric, so adding the two orders gives the sum of the
# prices and subtracting gives their difference -- no elimination, no multiplier.
REPAIRS = {
    "a00cb43b": dict(
        why="6e + 2f = 46 with 2e + 5f = 37 needs elimination; bracket $6, hinge $5 kept",
        stem=("A hardware shop sells brackets for e dollars and hinges for f dollars. "
              "Three brackets and two hinges cost $28. Two brackets and three hinges "
              "cost $27. What does one bracket cost?"),
        explanation=("The two orders together contain five brackets and five hinges for "
                     "$55, so a bracket and a hinge cost $11. The first order has one "
                     "more bracket than the second and costs $1 more, so a bracket is $1 "
                     "more than a hinge. That gives a bracket at $6 and a hinge at $5."),
        check=lambda: (3 * 6 + 2 * 5 == 28 and 2 * 6 + 3 * 5 == 27),
    ),
    "c99bf947": dict(
        why="2c + 5d = 39 with 4c + 1d = 33 needs elimination; fern $7, palm $5 kept",
        stem=("A nursery sells ferns for c dollars and palms for d dollars. Three ferns "
              "and two palms cost $31. Two ferns and three palms cost $29. What does one "
              "palm cost?"),
        explanation=("The two orders together contain five ferns and five palms for $60, "
                     "so a fern and a palm cost $12. The first order has one more fern "
                     "than the second and costs $2 more, so a fern is $2 more than a "
                     "palm. That gives a fern at $7 and a palm at $5."),
        check=lambda: (3 * 7 + 2 * 5 == 31 and 2 * 7 + 3 * 5 == 29),
    ),
    "c61a9369": dict(
        why="4n + m = 17 with n + 3m = 18 needs substitution; notebook $3, pen $5 kept",
        stem=("A stationery shop sells notebooks for n dollars and pens for m dollars. "
              "Three notebooks and two pens cost $19. Two notebooks and three pens cost "
              "$21. How much does one pen cost?"),
        explanation=("The two orders together contain five notebooks and five pens for "
                     "$40, so a notebook and a pen cost $8. The second order has one more "
                     "pen than the first and costs $2 more, so a pen is $2 more than a "
                     "notebook. That gives a notebook at $3 and a pen at $5."),
        check=lambda: (3 * 3 + 2 * 5 == 19 and 2 * 3 + 3 * 5 == 21),
    ),
}

CHECKS = ["leaked_working", "rewrites_the_question", "disputes_its_own_key",
          "no_question_asked", "options_distinct_by_value", "calculator_required",
          "rounds_without_saying_so", "non_integer_count", "negative_count",
          "invalid_clock_time", "markdown_table_in_stem", "caret_power_notation"]


def verify(q):
    out = []
    for n in CHECKS:
        fn = getattr(qc, n)
        m = fn(q["explanation"] or "") if n in ("leaked_working", "rewrites_the_question",
                                                "disputes_its_own_key") else fn(q)
        if m:
            out.append(f"{n}: {m}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not (args.apply or args.dry_run):
        raise SystemExit("pass --apply or --dry-run")

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    record, failed = [], 0
    for prefix, spec in REPAIRS.items():
        row = con.execute("SELECT * FROM questions WHERE id LIKE ?||'%'",
                          (prefix,)).fetchone()
        if row is None:
            raise SystemExit(f"{prefix} is not in the database")
        # The arithmetic is asserted here rather than trusted. Two of the round's own
        # repairs were caught this way before they landed.
        if not spec["check"]():
            raise SystemExit(f"{prefix}: the new totals do not match the kept prices")
        q = dict(row, stem=spec["stem"], explanation=spec["explanation"])
        after = verify(q)
        failed += bool(after)
        print(f"{prefix}  {spec['why']}")
        print(f"    key {row['correct_answer']} unchanged; "
              f"{'OK' if not after else 'STILL FAILING'}")
        for a in after:
            print(f"      ! {a}")
        record.append(dict(id=row["id"], why=spec["why"], form_id=row["form_id"],
                           key=row["correct_answer"], status=row["review_status"],
                           old_stem=row["stem"], new_stem=q["stem"],
                           old_explanation=row["explanation"],
                           new_explanation=q["explanation"], after=after))
        if args.apply and not after:
            con.execute("UPDATE questions SET stem=?, explanation=? WHERE id=?",
                        (q["stem"], q["explanation"], row["id"]))

    print("\n844bbdfe KEPT — its explanation already reasons over factor pairs "
          "(\"only 8 and 11 multiply to 88\"), which is PT1 numeric deduction, not a "
          "quadratic. Recorded as a disagreement with the reviewer.")
    if args.apply:
        if failed:
            con.rollback()
            raise SystemExit(f"\n{failed} still failing — nothing written")
        con.commit()
        MANIFEST.write_text(json.dumps(record, indent=1, ensure_ascii=False))
        print(f"applied {len(record)} — manifest {MANIFEST}")
    else:
        print(f"dry run — {len(record)} item(s), {failed} failing")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
