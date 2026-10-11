#!/usr/bin/env python3
"""NSW round 13: the 20 NSW questions in the reviewer's 2026-10-11 Selectly flag export.

The VIC half of the same export is `repair_vic_round13_flags.py`. These 20 sit on
`nsw-drill-math-*` (6) and `nsw-drill-ts-*` (14). All are approved and live, so nothing
here reaches a student until it is pushed.

TWO ARE LEFT AS THEY ARE, on purpose:
  10c4510b  'a simultaneous equation question, not thinking'. Round 5 ruled on exactly
            this (pdfs/figure_correctness_TASK.md §4): numeric deduction is a real
            Thinking Skills subcategory, the official PT1 examples are two-unknown
            problems, and the test is whether the numbers yield to REASONING. This one
            does, and its explanation already reasons rather than solves. 379480ff, the
            same note, is kept too but reworded: its stem used letters s and j, which is
            what made it read as algebra.
  1c476116  'looks like a duplicate from another set'. Checked: the closest stem in the
            whole bank scores 0.61 and asks something else; no other question counts
            tiles touching an edge.

Every question's full check state is compared before and after, and a repair that would
make any check newly fire is refused rather than written.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_nsw_round13_flags
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_nsw_round13_flags --apply
"""
from __future__ import annotations

import argparse
import csv
import json
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.repair_vic_round12_flags import FIELDS, findings      # noqa: E402
from tools.repair_vic_round13_flags import CSV, DB               # noqa: E402

RECORD = ROOT / "run_data/output/nsw_round13_flags.json"


# ================================================================ mathematics
def f_3b823824(q):
    """'Options B and C are both technically correct. Change one of them to be less
    accurate.' C ('the graph shows 30 students, not everybody') is a real weakness too,
    and the explanation even admitted it. C is now a claim that is simply wrong."""
    return {"option_c": "The graph should show percentages instead of numbers",
            "explanation": "Strawberry has no column of its own, but the Other column "
                           "holds a student whose flavour is not named, so that student "
                           "could have chosen strawberry. The graph cannot show that "
                           "nobody did. Using numbers rather than percentages is fine for "
                           "30 students, the order of the columns does not matter, and "
                           "chocolate being most popular says nothing about strawberry."}


def f_d1975740(q):
    """'Replace the text "box" in the equation with a symbol.'"""
    return {"stem": "Which operation belongs in the box to make this true: 24 □ 6 = 4?"}


def f_f76e6990(q):
    """'Option A and D are the same. Revise answer options to state which angle is
    which number.' Each option now names the opposite angle and the angle next to it.
    The explanation also matched the wrong options to their mistakes; it now names them
    by value."""
    return {"option_a": "Opposite: 137°. Next to it: 43°",
            "option_b": "Opposite: 43°. Next to it: 47°",
            "option_c": "Opposite: 137°. Next to it: 137°",
            "option_d": "Opposite: 43°. Next to it: 137°",
            "explanation": "Vertically opposite angles are equal, so the opposite angle "
                           "is 43°. The angle next to it sits on a straight line with it, "
                           "so the two add to 180°: 180 − 43 = 137°. Opposite 137° and "
                           "next to it 43° swaps the two. 47° uses 90 − 43, as if angles "
                           "on a straight line added to 90°. 137° twice makes the "
                           "opposite angle add to 180° instead of being equal."}


def f_b5e5f404(q):
    """'Text "sqrt" is not a square root symbol.'"""
    return {"stem": "Evaluate 3² + √81 − 2³",
            "explanation": "3² = 9, √81 = 9 and 2³ = 8. So 9 + 9 − 8 = 10."}


def f_5594487d(q):
    """'The square symbol is just a 2 not in superscript.' m2 is m² throughout."""
    return {"option_a": "1 542 m²", "option_b": "1 543 m²", "option_c": "160 m²",
            "option_d": "1 540 m²",
            "explanation": "Area is length × width: 47.6 × 32.4 = 1 542.24 m². The "
                           "first decimal digit is 2, so it rounds down to 1 542 m². "
                           "1 543 m² rounds up when it should not. 1 540 m² rounds to the "
                           "nearest ten, not the nearest whole number. 160 is the "
                           "perimeter, 2 × (47.6 + 32.4) = 160 m, not the area."}


def f_17cc8345(q):
    """'Two possible solutions, -5 and 19. Rephrase to say five whole numbers.'

    −5 is only possible if 7 is the LARGEST number, and the stem says it is the
    smallest -- but the reviewer read it the other way, so a student can too. Reworded
    as asked ('whole numbers') and with 'smallest of the five' spelt out."""
    return {"stem": "Five whole numbers have a range of 12. The smallest of the five is "
                    "7. What is the largest of the five?",
            "explanation": "The range is the largest number take away the smallest. So "
                           "the largest is 7 + 12 = 19. Check: 19 − 7 = 12. 5 takes 7 from "
                           "12, which is the subtraction the wrong way round, and would "
                           "be smaller than 7. 12 is the range itself, and 84 multiplies "
                           "7 by 12."}


# ============================================================ thinking skills
def f_379480ff(q):
    """'A quantitative reasoning question, not a thinking one.' Kept as numeric
    deduction (round 5's ruling, see the module note), but the letters s and j are gone
    from the stem and the explanation now shows the reasoning a Thinking Skills
    candidate uses -- add the two orders, compare the two orders -- instead of 'solving
    the two orders together'."""
    return {"stem": "At a school cafe, three scones and two juices cost $23. Two scones "
                    "and three juices cost $22. How much is one scone?",
            "explanation": "Put the two orders together: 5 scones and 5 juices cost $45, "
                           "so one scone and one juice cost $9. The first order has one "
                           "more scone and one fewer juice than the second and costs $1 "
                           "more, so a scone costs $1 more than a juice. Two prices $1 "
                           "apart that add to $9 are $5 and $4: a scone is $5."}


def f_1e9739d8(q):
    """'Graph overlaps with text (there is no need for the 0).' The 0 sat on the
    ruler's left edge. It is removed, as asked; the 2, 4, 6 ... still number the scale."""
    svg = q["figure_svg"]
    zero = ('<text x="26" y="156" font-family="system-ui,sans-serif" font-size="10" '
            'fill="currentColor" fill-opacity=".65" text-anchor="middle">0</text>')
    assert svg.count(zero) == 1
    return {"figure_svg": svg.replace(zero, "")}


def f_15621bc8(q):
    """'Options C and D should be simplified ... they are 63 days.' 8 weeks 7 days and
    7 weeks 14 days ARE 63 days, so they were not wrong, only unsimplified. Both are now
    genuinely wrong: 8 weeks 3 days is 59 days, and 6 weeks 3 days comes from dividing
    by 10."""
    return {"option_c": "8 weeks and 3 days", "option_d": "6 weeks and 3 days",
            "explanation": "63 ÷ 7 = 9 exactly, so the puppy is 9 whole weeks old with no "
                           "days over. 9 weeks and 3 days reads the 3 off the end of 63. "
                           "8 weeks and 3 days is only 59 days. 6 weeks and 3 days divides "
                           "63 by 10 instead of 7."}


def f_baf4f9c3(q):
    """'Confusing question, one 90 degree turn makes it look exactly the same.' The
    reviewer is right that it does -- and so does every other quarter turn, which is
    the answer. What was confusing is 'in how many of the four quarter turns'. The turns
    are now spelt out one after another."""
    return {"stem": "The grid in the diagram is turned a quarter turn about its centre, "
                    "then another quarter turn, then another, then another, until it is "
                    "back where it started. After how many of those four turns does the "
                    "shaded pattern look exactly the same as it did at the start?",
            "explanation": "The four shaded squares sit one in the middle of each edge. "
                           "A quarter turn moves each one onto the next, so the pattern "
                           "looks the same after the first turn, and so after the second, "
                           "third and fourth too: all 4. A pattern shaded in one corner "
                           "only would match after the fourth turn alone."}


def f_1c2ad907(q):
    """'There is not enough information to solve the question.' Worse than that: there
    is no answer at all. With the rectangle s by s + 14, its perimeter is 4s + 28, which
    can never equal the square's 4s. The explanation got 14 by dropping a term.

    Re-cut to the same idea -- equal perimeters -- with numbers that work: a wire bent
    into a 20 by 8 rectangle and re-bent into a square. Answer 14 cm, still D. B is now
    56, the whole wire, so every distractor is a real mistake."""
    return {"stem": "A piece of wire is bent to make a rectangle 20 cm long and 8 cm "
                    "wide. It is then straightened and bent to make a square, using all "
                    "of the wire. How long is each side of the square?",
            "option_b": "56 cm",
            "explanation": "The wire is as long as the rectangle's perimeter: 20 + 8 + 20 "
                           "+ 8 = 56 cm. A square shares that between 4 equal sides, so "
                           "each is 56 ÷ 4 = 14 cm. 56 cm is the whole wire, 28 cm is only "
                           "one length and one width, and 7 cm divides 28 by 4."}


def f_91bc9f80(q):
    """'Really subjective, because the audience lacks context on whether Pia's
    statement could possibly be true.' Fair: Pia's conclusion COULD be true, and
    'reasons correctly' left a student guessing how strict to be. The question now asks
    whose conclusion MUST be true from the counts, and Quinn's is replaced by one that
    only restates them. The options are reordered so the key stays A."""
    return {"stem": "A shop counted its customers on one Monday in January and one "
                    "Monday in July, and more came in on the July Monday. Pia says: 'So "
                    "the shop is getting busier over time.' Quinn says: 'So more "
                    "customers came on that July Monday than on that January Monday.' "
                    "Whose conclusion must be true from the two counts?",
            "option_a": "Quinn only", "option_b": "Neither Pia nor Quinn",
            "option_c": "Both Pia and Quinn", "option_d": "Pia only",
            "explanation": "Quinn only says what the counts show, so it must be true. "
                           "Pia's could be true, but two single days months apart cannot "
                           "show a trend: the seasons, the weather or a holiday could "
                           "explain the difference. So only Quinn's must be true."}


def f_e9ec3a53(q):
    """'Option B, 9:75 is unrealistic as minutes never exceed 60.' B is now a real
    time a student could reach by a real slip: 10:25 pm, from treating 7:50 as 8:00."""
    return {"option_b": "10:25 pm",
            "explanation": "Two hours after 7:50 pm is 9:50 pm, and 25 minutes more is "
                           "10:15 pm. 10:25 pm rounds the start up to 8:00, 10:05 pm adds "
                           "only 15 minutes, and 9:15 pm adds 1 hour 25 minutes."}


def f_4a47b474(q):
    """'Very repetitive ... I have seen multiple questions exactly like this but with
    just different names.' Measured: 17 knight-and-knave questions sit in the NSW drill
    forms, never two in one form, and `nsw-drill-ts-006` opens with the very same
    'X says: Y and Z are both knights'. This one is re-cut to a different kind of
    truth-teller puzzle -- one liar among three, about who took a biscuit -- so it stays
    in its subcategory. The other 16 are left alone (rule 11d). Key stays A."""
    return {"stem": "Exactly one of Ava, Ben and Cal took the last biscuit, and exactly "
                    "one of the three is lying. Ava says: 'Ben took it.' Ben says: 'I did "
                    "not take it.' Cal says: 'Ava took it.' Who took the last biscuit?",
            "option_a": "Ava", "option_b": "Ben", "option_c": "Cal",
            "option_d": "It cannot be worked out",
            "explanation": "Ava and Ben cannot both be telling the truth, so the one liar "
                           "is Ava or Ben, and Cal is telling the truth. So Ava took it. "
                           "Check: then Ava is lying, Ben is truthful, and Cal is "
                           "truthful, which is exactly one liar."}


def f_5e296a75(q):
    """'Option B is technically correct in a sense.' B was 'it cannot be worked out',
    which is not wrong about the TEAM -- it cannot be. B is now 'either team -- both
    could say it', a clear mistake, and the key stays A."""
    return {"option_b": "either team — both could say it"}


def f_8a7ef690(q):
    """'Explanation makes no sense, five quarter turns would be a quarter turn further
    than the original.' The reviewer is right about the turn and was misled by the
    question: it compared the end with ONE quarter turn, not with the start, and the
    figure then drew the finished shape, so the picture answered a different question.

    Now it asks where the shape finishes compared with where it STARTED, the figure
    shows only the starting shape, and the key stays A: a quarter turn clockwise."""
    svg = ('<svg viewBox="0 0 340 97" xmlns="http://www.w3.org/2000/svg" fill="none" '
           'stroke-linejoin="round" stroke-linecap="round"><path d="M144 46h17v17h-17z'
           'M162 46h17v17h-17zM178 46h17v17h-17zM144 29h17v17h-17z" '
           'stroke="currentColor" stroke-opacity=".85" stroke-width="1.6" '
           'fill="currentColor" fill-opacity=".08"/><text x="170" y="84" '
           'font-family="system-ui,sans-serif" font-size="11" fill="currentColor" '
           'fill-opacity=".75" text-anchor="middle">start</text></svg>')
    return {"figure_svg": svg,
            "stem": "The shape in the diagram is turned a quarter turn clockwise five "
                    "times in a row. Compared with where it started, where does it "
                    "finish?",
            "option_a": "a quarter turn clockwise from the start",
            "option_b": "back where it started",
            "option_c": "half a turn from the start",
            "option_d": "a quarter turn anticlockwise from the start",
            "explanation": "Four quarter turns make a full turn, which brings the shape "
                           "back to the start. The fifth turn is one more quarter turn "
                           "clockwise. Back where it started would need four or eight "
                           "turns, half a turn would need two or six, and a quarter turn "
                           "anticlockwise would need three or seven."}


def f_b12f061c(q):
    """'There is no point to have a diagram for this question.' The figure was an
    empty logic grid, which says nothing the stem does not. Removed."""
    return {"figure_svg": None}


def f_3a74da7c(q):
    """'It doesn't explicitly state that the book is in the car. It is possible that
    the book is lost.' The first sentence was meant as a given, but it reads like a
    guess. It now says the book is DEFINITELY in one of the three places."""
    return {"stem": "We know for certain that the book is in one of three places: the "
                    "hall, the study or the car. It is not in the hall and it is not in "
                    "the study. Which student has reasoned correctly?",
            "explanation": "The book is certainly in one of the three places, and two of "
                           "them are ruled out, so it is in the car. Vale's answer "
                           "contradicts the first fact rather than working from it."}


REPAIRS = {
    "3b823824": f_3b823824, "d1975740": f_d1975740, "f76e6990": f_f76e6990,
    "b5e5f404": f_b5e5f404, "5594487d": f_5594487d, "17cc8345": f_17cc8345,
    "379480ff": f_379480ff, "1e9739d8": f_1e9739d8, "15621bc8": f_15621bc8,
    "10c4510b": None, "baf4f9c3": f_baf4f9c3, "1c2ad907": f_1c2ad907,
    "91bc9f80": f_91bc9f80, "1c476116": None, "e9ec3a53": f_e9ec3a53,
    "4a47b474": f_4a47b474, "5e296a75": f_5e296a75, "8a7ef690": f_8a7ef690,
    "b12f061c": f_b12f061c, "3a74da7c": f_3a74da7c,
}


def read_csv():
    with CSV.open(newline="", encoding="utf-8") as fh:
        return [r for r in csv.DictReader(fh) if r["form_id"].startswith("nsw-")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--only", help="comma-separated short ids, for working on one")
    args = ap.parse_args()

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    record, refused, changed = [], [], 0
    for f in read_csv():
        qid = f["qbank_id"]
        short = qid[:8]
        if args.only and short not in args.only.split(","):
            continue
        if short not in REPAIRS:
            refused.append((short, "no repair written"))
            continue
        fn = REPAIRS[short]
        if fn is None:
            record.append({"id": qid, "form": f["form_id"], "pos": f["form_position"],
                           "note": f["note"], "action": "left as it is", "fields": []})
            continue
        row = dict(con.execute("SELECT * FROM questions WHERE id=?", (qid,)).fetchone())
        before = findings(row)
        after_row = dict(row)
        after_row.update(fn(row))
        after = findings(after_row)
        gained = after - before
        if gained:
            refused.append((short, f"would newly fire {sorted(gained)}"))
            continue
        touched = [k for k in FIELDS if after_row.get(k) != row.get(k)]
        if not touched:
            refused.append((short, "repair changed nothing"))
            continue
        changed += 1
        record.append({"id": qid, "form": f["form_id"], "pos": f["form_position"],
                       "note": f["note"], "action": "repaired", "fields": touched,
                       "why": (fn.__doc__ or "").strip(),
                       "cleared": sorted(before - after),
                       "before": {k: row.get(k) for k in touched},
                       "after": {k: after_row.get(k) for k in touched}})
        if args.apply:
            sets = ", ".join(f"{k}=?" for k in touched)
            con.execute(f"UPDATE questions SET {sets} WHERE id=?",
                        [after_row[k] for k in touched] + [qid])

    if args.apply:
        con.commit()
        RECORD.parent.mkdir(parents=True, exist_ok=True)
        RECORD.write_text(json.dumps(record, indent=1, ensure_ascii=False))
    con.close()
    left = sum(1 for r in record if r["action"] == "left as it is")
    print(f"{changed} repaired, {left} left as they are, {len(refused)} refused"
          f"{' (DRY RUN)' if not args.apply else ''}")
    for short, why in refused:
        print(f"  REFUSED {short}: {why}")
    cleared = sorted({c for r in record for c in r.get("cleared", [])})
    print(f"findings cleared: {cleared or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
