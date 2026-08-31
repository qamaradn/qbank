#!/usr/bin/env python3
"""Strip the LaTeX a student would have been shown, on the nine PENDING questions the
widened `latex_markup_in_text` now finds.

Round 9's reviewer found stray dollar signs twice on one page -- '$y = 2x - 3$' in an
option and '$AB$' in a stem -- and the check saw neither, because it only fired on a
$...$ pair with a backslash command inside it. That narrowness is deliberate: a stem
about a $180 phone is not maths markup, and 404 questions in this bank price things in
dollars. The rule now also fires when the opening $ is followed by a LETTER, which no
price ever is. It catches sixteen questions: this repairs the nine that are pending.

The six already rejected are left alone, and so is `f27e0d63`, which is approved and
live in vic-drill-mq-008 -- the reviewer has passed it.

READING THE NINE TURNED UP MORE THAN MARKUP IN ONE OF THEM. `6aafd8b2` asks when
$5000 at 4% first exceeds $6000. 5000 x 1.04^4 = 5849.29 and 5000 x 1.04^5 = 6083.26,
so the answer is 5 complete years, which is option D. The key said A (6 years) and the
stored explanation worked out "5 years" and then signed off "Answer is B (5 years).
Selecting B" -- while B is 7 years. Checked the other way, n > log 1.2 / log 1.04 =
4.65, so the first whole year is 5. The key moves to D and the explanation is rewritten.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_latex_markup_round9
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_latex_markup_round9 --apply
"""
from __future__ import annotations

import argparse
import inspect
import json
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import question_checks as qc            # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
RECORD = ROOT / "run_data/output/latex_markup_round9.json"

FIXES = {
    # plain markup strips -- nothing but the delimiters goes
    "8a523b94": {
        "stem": "Given that x³ = 64 and y² = 9, where both x and y are positive "
                "numbers, what is the value of x + y?"},
    "e0f18fc4": {
        # here the dollar sign is doing two jobs at once: the question prices tickets
        # in dollars AND wrapped its algebra in $. One leading $ is kept, as currency,
        # which is what the answer actually is.
        "stem": "A group of Year 12 students are planning a school trip to the Blue "
                "Mountains. The bus hire costs $650. They plan to sell 200 tickets at "
                "$5 each, which is enough to cover the cost and make a profit. If they "
                "sell an additional x tickets at the same price, how does their profit "
                "change?",
        "option_a": "Profit increases by $650 − 5x",
        "option_b": "Profit increases by $5x",
        "option_c": "Profit decreases by $5x",
        "option_d": "Profit increases by $5x − 650"},
    "63efba06": {
        "stem": "If 5x + 3 = 3x + 11, what is the value of x?"},
    "2e5a0b03": {
        "stem": "What is the value of 5(200x − 4000) + 500 when x = 30?"},
    "c7fe9ace": {
        "stem": "For what nonzero whole number m does the quadratic equation "
                "y² + 6my + 9m = 0 have exactly one real solution for y?",
        "explanation": "For exactly one real solution the discriminant must be zero. "
                       "Discriminant = (6m)² − 4(1)(9m) = 36m² − 36m = 36m(m − 1) = 0. "
                       "Since m is nonzero, m − 1 = 0, so m = 1."},
    "f6bf96e9": {
        "stem": "The graph below shows a parabola. The parabola passes through the "
                "points (1, 0), (5, 0) and (3, −4). What is the equation of the "
                "parabola?",
        "option_a": "y = (x − 1)(x − 5)",
        "option_b": "y = −(x − 1)(x − 5)",
        "option_c": "y = (x − 3)² − 4",
        "explanation": "From the roots x = 1 and x = 5: y = a(x − 1)(x − 5). "
                       "Substituting (3, −4): −4 = a(2)(−2) = −4a, so a = 1. That "
                       "gives y = (x − 1)(x − 5) = x² − 6x + 5 = (x − 3)² − 4. A and C "
                       "are the same parabola written two ways, so both are correct "
                       "and the answer is D."},
    "6aafd8b2": {
        "stem": "Mia is in Melbourne and invests $5000 AUD at a compound interest rate "
                "of 4% per annum. After how many complete years will her investment "
                "first exceed $6000 AUD?",
        "correct_answer": "D",
        "explanation": "After n years the investment is 5000 × 1.04ⁿ, and this must "
                       "first pass 6000. After 4 years: 5000 × 1.04⁴ = $5849.29, still "
                       "under $6000. After 5 years: 5000 × 1.04⁵ = $6083.26, over it. "
                       "So the investment first exceeds $6000 after 5 complete years. "
                       "Checking with logarithms: n > log 1.2 ÷ log 1.04 = 4.65, so "
                       "the first whole year is 5."},
    "37e10b1c": {
        "stem": "Which of the following is equivalent to the inequality "
                "5x − 4 > 7x + 8?",
        "option_a": "x < 6", "option_b": "x < −6",
        "option_c": "x > 6", "option_d": "x > −6"},
    "5d9dfbce": {
        "stem": "The variable m is directly proportional to n². When n = 2, m = 28. "
                "What is the positive value of n when m = 63?"},
}

INVERTED = {"options_distinct"}


def _checks():
    row, svg = [], []
    for name, fn in vars(qc).items():
        if name.startswith("_") or not inspect.isfunction(fn):
            continue
        ps = list(inspect.signature(fn).parameters)
        if not ps:
            continue
        (row if ps[0] == "q" else svg if ps[0] == "svg" else []).append(name)
    return row, svg


ROW_CHECKS, SVG_CHECKS = _checks()


def state(q):
    fired = set()
    for n in ROW_CHECKS:
        try:
            hit = getattr(qc, n)(q)
        except Exception:
            fired.add(n + ":ERR")
            continue
        if (not hit) if n in INVERTED else bool(hit):
            fired.add(n)
    for n in SVG_CHECKS:
        try:
            if getattr(qc, n)(q.get("figure_svg") or ""):
                fired.add(n)
        except Exception:
            fired.add(n + ":ERR")
    return fired


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    done, refused = [], []
    for prefix, upd in FIXES.items():
        row = con.execute("SELECT * FROM questions WHERE id LIKE ?",
                          (prefix + "%",)).fetchone()
        if row is None:
            refused.append({"id": prefix, "why": "no such question"})
            continue
        q = dict(row)
        if q["review_status"] != "pending":
            refused.append({"id": q["id"], "why": f"status {q['review_status']}"})
            continue
        before = state(q)
        after_row = dict(q)
        after_row.update(upd)
        after = state(after_row)
        gained = sorted(after - before)
        rec = {"id": q["id"], "form": q["form_id"], "pos": q["form_position"],
               "changed": sorted(upd), "newly_firing": gained,
               "cleared": sorted(before - after)}
        if gained:
            refused.append(rec)
            continue
        done.append(rec)
        if args.apply:
            cols = ", ".join(f"{k} = ?" for k in upd)
            con.execute(f"UPDATE questions SET {cols}, edited = 1 WHERE id = ?",
                        [*upd.values(), q["id"]])
    if args.apply:
        con.commit()
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps({"done": done, "refused": refused}, indent=1))
    print(f"repaired {len(done)}   refused {len(refused)}"
          f"   {'APPLIED' if args.apply else 'dry run'}")
    for r in refused:
        print("  REFUSED", r.get("id"), r.get("newly_firing") or r.get("why"))
    for r in done:
        print(f"  {r['id'][:8]} {r['form'] or '-':<17} changed={','.join(r['changed'])}"
              f"{'  cleared=' + ','.join(r['cleared']) if r['cleared'] else ''}")


if __name__ == "__main__":
    main()
