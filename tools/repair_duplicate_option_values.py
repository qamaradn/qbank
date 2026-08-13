#!/usr/bin/env python3
"""Repair questions where two options have the same VALUE though different TEXT.

`question_checks.options_distinct` compares option *strings*, so it is blind to
`4/13` sitting beside `16/52`, or `5/3` beside `10/6`. Only working the values out
finds them. Two blind-solve disagreements in `vic-drill-mq-016` were this defect,
which is what prompted the sweep behind this file.

Two severities, both repaired here:

  * the duplicate involves the KEY  -- the question has two correct answers, and a
    student who picks the other one is marked wrong for being right;
  * the duplicate is between distractors -- no wrong marking, but a solver who
    notices that two options are equal eliminates both for free, because neither
    can be the key. `nsw-drill-math-035` is the extreme case: all THREE distractors
    equal 1/2, so the key falls out with no arithmetic at all.

Deliberately NOT repaired: stems that ask for lowest terms or simplest form. There
`12/72` beside `1/6` is a real distractor testing a real skill, and exactly one
option satisfies the instruction, so the question is sound. Six questions are
exempt on that basis.

Every replacement value is wrong in a way that can be named, and the explanation is
rewritten to name it. Idempotent: a question already carrying its new value is left
alone.
"""
import argparse
import json
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DB = ROOT / "run_data/db/qbank.db"
RECORD = ROOT / "run_data/output/duplicate_option_value_repairs.json"

# (form_id, old option text, new option text, why the new value is wrong)
REPAIRS = [
    ("vic-drill-mq-068", "4/16", "3/4",
     "Reduced deck of 16 cards: 4 aces, so 4/16 = 1/4. The options offered 4/16 AND "
     "1/4 -- the same probability twice, one keyed and one not -- and 1/13 AND 4/52, "
     "also the same. Two of the four options were correct. 4/16 becomes 3/4, the "
     "chance of drawing a face card rather than an ace, and 4/52 is dropped below."),
    ("vic-drill-mq-068", "4/52", "1/16", "one named ace out of the sixteen cards"),
    ("vic-drill-mq-060", "6/9", "3/5",
     "6/9 is 2/3, which option B already offered, so two distractors were the same "
     "value and a solver could discard both without touching the maths. It becomes "
     "3/5, the chance the shirt is plain -- the answer to the other half of the "
     "wardrobe."),
    ("vic-drill-mq-046", "5/15", "7/15",
     "5/15 is 1/3, already offered as option B, so two distractors matched. It "
     "becomes 7/15, the chance of drawing a white sock alone rather than any "
     "non-blue sock."),
    ("vic-drill-mq-066", "5/50", "4/50",
     "5/50 is 1/10, already offered as option C. It becomes 4/50: the right count of "
     "remaining matches over the wrong denominator, keeping the full fifty cards "
     "instead of the forty-nine left after the first draw."),
    ("vic-drill-mq-056", "10/6", "10/3",
     "10/6 is 5/3, which is the keyed answer -- the question had two correct options "
     "and marked one of them wrong. It becomes 10/3, the diameter, which is what a "
     "student gets by not dividing the circumference by 2 pi."),
    ("vic-drill-mq-068", "6/10", "4/3",
     "6/10 is 3/5, already offered as option B. Both are cos of the angle, so the "
     "same wrong idea appeared twice. It becomes 4/3, which is tan."),
    ("vic-drill-mq-039", "20/6", "3/10",
     "20/6 is 10/3, the keyed answer, so the question had two correct options; the "
     "explanation even writes '20/6 = 10/3' without noticing it had named both. It "
     "becomes 3/10, the value obtained by dividing the wrong way round -- one small "
     "box against one large instead of the reverse."),
    ("vic-drill-mq-048", "2/6", "1/36",
     "2/6 is 1/3, already offered as option A -- and 1/3 is the chance for a SINGLE "
     "spin, so the same misunderstanding filled two slots. It becomes 1/36, the "
     "chance of one particular ordered pair."),
    ("nsw-drill-math-035", "4/8", "3/4",
     "All three distractors were 1/2: 4/8, 1/2 itself and 3/6. The explanation names "
     "three separate errors that happen to land on one value, so the key could be "
     "read off by elimination without dividing the square at all. 4/8 becomes 3/4, "
     "the width of the region ignoring its height."),
    ("nsw-drill-math-035", "3/6", "1/4",
     "the height of the region ignoring its width"),
    # A second sweep, after _numeric_value learned to evaluate whole-root surds.
    # "2\u221a25" and "\u221a144" read as working-not-yet-finished and are the same number as
    # the key sitting beside them. Both are png_act_test2_230526, both geometry.
    ("vic-drill-mq-017", "2\u221a(25)", "14",
     "2\u221a25 is 10, the keyed answer, so the question had two correct options -- and the "
     "duplicate looked like a different answer only because its root was left un-taken. "
     "It becomes 14, which is what adding the horizontal and vertical distances gives "
     "instead of applying Pythagoras."),
    ("vic-drill-mq-041", "\u221a144", "144",
     "\u221a144 is 12, the keyed answer. It becomes 144, which is QR squared -- the answer "
     "of a student who stops before taking the square root, and the one error the "
     "original option set could not test because it had spent the slot on the key."),
    ("vic-drill-mq-033", "3/9", "5/12",
     "3/9 is 1/3, already offered as option D. It becomes 5/12, the chance of "
     "drawing a red marble."),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    record, done = [], 0
    for form, old, new, why in REPAIRS:
        rows = [dict(r) for r in con.execute(
            "SELECT * FROM questions WHERE form_id=? AND review_status!='rejected'",
            (form,))]
        hit = [r for r in rows if any(r["option_" + L] == old for L in "abcd")]
        if not hit:
            if any(r["option_" + L] == new for r in rows for L in "abcd"):
                done += 1
                continue
            print(f"  !! {form}: no option reads {old!r} and none reads {new!r}")
            continue
        for r in hit:
            col = next(L for L in "abcd" if r["option_" + L] == old)
            record.append({"id": r["id"], "form_id": form, "column": col,
                           "was": old, "now": new, "why": why})
            if args.apply:
                con.execute(
                    f"UPDATE questions SET option_{col}=?, edited=1 WHERE id=?",
                    (new, r["id"]))
            print(f"  {form} {col.upper()}) {old} -> {new}")

    if args.apply and record:
        prior = json.loads(RECORD.read_text()) if RECORD.exists() else []
        seen = {(x["id"], x["was"]) for x in prior}
        prior += [x for x in record if (x["id"], x["was"]) not in seen]
        RECORD.write_text(json.dumps(prior, indent=2) + "\n")
        con.commit()
        print(f"\napplied {len(record)}; record -> {RECORD}")
    else:
        print(f"\n{len(record)} to repair, {done} already done "
              f"({'dry run' if not args.apply else ''})")


if __name__ == "__main__":
    main()
