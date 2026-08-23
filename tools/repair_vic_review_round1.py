#!/usr/bin/env python3
"""Repairs from the first VIC review round (2026-08-23), fourteen flags.

Grouped by what the flag actually was. Numbers are changed rather than rounded away:
where a question needed a calculator, the quantities are re-chosen so the arithmetic
comes out exactly, which keeps the skill being tested and removes the tool.
"""
import argparse
import json
import pathlib
import sqlite3

ROOT = pathlib.Path(__file__).resolve().parents[1]
DB = ROOT / "run_data/db/qbank.db"
RECORD = ROOT / "run_data/output/vic_review_round1_repairs.json"

# id -> {field: new value}, plus a `why` recording the reviewer's words and the verdict.
REPAIRS = {
    # "this question needs a calculator to be solved" — half a 23.77 m court is 11.885 m,
    # and the diagonal is the root of a non-square. A practice court measured in whole
    # metres gives a 5-12-13 triangle, so the same Pythagoras is exact.
    "ce671dbe-8658-4eab-b2e2-5de2fda6709d": {
        "why": "calculator required; renumbered to a 5-12-13 triangle",
        "stem": ("A practice tennis court at a Melbourne centre is 24 metres long and "
                 "10 metres wide. A ball boy stands at the centre of the net. If he "
                 "sprints from there to the far corner of his side of the court, how "
                 "far does he run?"),
        "option_a": "13 m", "option_b": "12 m", "option_c": "17 m", "option_d": "5 m",
        "correct_answer": "A",
        "explanation": ("His side of the court is 24 ÷ 2 = 12 m long, and the corner is "
                        "half the width across, 10 ÷ 2 = 5 m. By Pythagoras the run is "
                        "√(12² + 5²) = √(144 + 25) = √169 = 13 m exactly. Answering 17 m "
                        "adds the two distances instead of combining them by Pythagoras; "
                        "12 m and 5 m each give one side on its own."),
    },
    # "again, the number of runs is still a decimal." 75% of 275 is 206.25. 280 divides.
    "eba092f4-95cc-4722-af0a-201a9a3f6aeb": {
        "why": "fractional runs; first innings changed from 275 to 280 so 75% is whole",
        "stem": ("A cricket team scores 280 runs in their first innings. In their second "
                 "innings, they score 75% of their first innings total. How many runs "
                 "did they score in the second innings?"),
        "option_a": "210", "option_b": "70", "option_c": "224", "option_d": "490",
        "correct_answer": "A",
        "explanation": ("75% of 280 is three quarters of it: 280 ÷ 4 = 70, and 70 × 3 = "
                        "210 runs. Answering 70 gives the quarter they fell short by "
                        "rather than the runs they scored. 224 takes 80% instead of 75%. "
                        "490 adds both innings together."),
    },
    # "calculator might be needed" — five percentage changes in a row. Two changes, both
    # a tenth, test the same idea (a rise then an equal fall does NOT return you to the
    # start) and can be done in the head.
    "ed89b006-87ac-4fd8-8831-872ec1970069": {
        "why": "five successive percentage changes; reduced to two clean ones",
        "stem": ("A stockbroker invests $20 000 in a fund. In the first month the value "
                 "rises by 10%, and in the second month it falls by 10%. What is the "
                 "value of the investment at the end of the two months?"),
        "option_a": "$19 800", "option_b": "$20 000", "option_c": "$22 000",
        "option_d": "$18 000", "correct_answer": "A",
        "explanation": ("A 10% rise takes $20 000 to $22 000. The 10% fall is then taken "
                        "off the NEW value, not the old one: 10% of $22 000 is $2 200, "
                        "leaving $19 800. Answering $20 000 assumes the rise and the "
                        "fall cancel, which they never do — the fall is a tenth of a "
                        "larger number. $22 000 stops after the first month, and "
                        "$18 000 takes 10% of the original off twice."),
    },
    # "doesn't specify what the question really is." The stem presented the material and
    # stopped, leaving the student to infer the task from the options.
    "507e20cc-c336-494b-b022-10d537c11aac": {
        "why": "stem never asked anything; the question is now stated",
        "stem": ("Consider the following information about the Sydney Opera House: It is "
                 "one of Australia's most recognisable landmarks, located on the "
                 "foreshore of Sydney Harbour. It hosts over 1,500 performances "
                 "annually, including opera, ballet, and theatre. The building's iconic "
                 "sail-like design was conceived by Danish architect Jørn Utzon. Despite "
                 "its fame, there have been ongoing debates about its acoustics and "
                 "operational costs.\n\nWhich of these is supported by the information "
                 "above?"),
    },
    # "calculator is required." An amortised 25-year mortgage compounded monthly cannot
    # be renumbered into something doable by hand -- the formula itself is the problem.
    # The slot is rewritten to a different Financial Mathematics question that tests the
    # same ideas a Year 8 paper actually wants: a percentage deposit, the balance
    # borrowed, and simple interest on it.
    "48301748-d392-4806-a8f6-488e5d6a0ebb": {
        "why": "amortisation needs a calculator; rewritten as deposit + simple interest",
        "stem": ("Olivia buys a house in Wollongong for $850 000. She pays a deposit of "
                 "20% and borrows the rest. Simple interest of 5% per year is charged on "
                 "the amount she borrows. How much interest does she pay in the first "
                 "year?"),
        "option_a": "$34 000", "option_b": "$42 500", "option_c": "$68 000",
        "option_d": "$170 000", "correct_answer": "A",
        "explanation": ("The deposit is 20% of $850 000 = $170 000, so she borrows "
                        "$850 000 − $170 000 = $680 000. One year of simple interest at "
                        "5% is 680 000 ÷ 20 = $34 000. Answering $42 500 charges the "
                        "interest on the full purchase price instead of on the loan. "
                        "$68 000 uses 10% rather than 5%. $170 000 gives the deposit."),
        "topic": "Financial Mathematics",
    },
    # "honestly a little difficult for year 8's like i have no clue what any of these
    # words mean except elegy." Beyond the vocabulary, the options overlapped: both
    # "expressions of grief or mourning" and "associated with funerals" fit all four
    # words, so the question had two defensible answers. Same frame, words a Year 8
    # reader knows, and one precise classification.
    "747fb2e3-046d-410b-a24b-6dbdd29a0669": {
        "why": "vocabulary beyond Year 8, and two options both fitted; frame kept",
        "stem": ("Which group of words shares the most precise common classification?\n"
                 "WALK   TROT   CANTER   GALLOP"),
        "option_a": "They are all gaits of a horse",
        "option_b": "They are all ways of moving quickly",
        "option_c": "They are all commands given to an animal",
        "option_d": "They are all words for a kind of race",
        "correct_answer": "A",
        "explanation": ("The four words name the paces a horse moves at, in order from "
                        "slowest to fastest, so 'gaits of a horse' is the classification "
                        "that fits all four and nothing else. 'Ways of moving quickly' "
                        "fails on walk, which is the slowest of them. They are not "
                        "commands, and none of them is a race."),
    },
    # "not really a verbal reasoning question - more of a sciency one." Correct, and it is
    # also an ORDERING item, which the VIC brief bans outright. Answering it needs
    # geology, not reasoning. Rewritten as a vocabulary-in-context item, the largest
    # legitimate VIC verbal category.
    "17f57fcf-79f8-4784-9d2b-b428dacde662": {
        "why": "general knowledge, not verbal reasoning, and an ordering type VIC bans",
        "stem": ("The committee's approval was tacit: nobody said a word against the "
                 "plan, and nobody said a word for it either. As it is used here, "
                 "'tacit' most nearly means:"),
        "option_a": "unspoken", "option_b": "unanimous", "option_c": "reluctant",
        "option_d": "temporary", "correct_answer": "A",
        "explanation": ("Tacit approval is approval understood without being stated, "
                        "which is exactly what the sentence describes: nobody spoke "
                        "either way. 'Unanimous' would mean everyone agreed, which the "
                        "silence does not establish; 'reluctant' adds an unwillingness "
                        "the sentence never mentions; 'temporary' says nothing about how "
                        "the approval was given."),
        "topic": "Vocabulary in context / synonyms",
        "source_page_description": "Category: vocabulary_in_context [target: tacit]",
    },
    # "maybe remove the -1 wickets option; how can a bowler have -1 wickets?"
    "4d26d3e0-96c4-4975-a4af-202c15c9efe1": {
        "why": "impossible negative count; replaced with a reachable wrong answer",
        "option_c": "27 wickets",
        "explanation": ("Averaging 3 wickets across 9 matches means 3 × 9 = 27 wickets "
                        "for the season. She already had 25 after eight matches, so the "
                        "last match brought 27 − 25 = 2. Answering 27 gives the season "
                        "total rather than the last match, 25 repeats the first eight "
                        "matches, and 3 quotes the average itself."),
    },
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    record = []
    for qid, fix in REPAIRS.items():
        row = con.execute("SELECT * FROM questions WHERE id=?", (qid,)).fetchone()
        if not row:
            print(f"  !! {qid} not found")
            continue
        fields = {k: v for k, v in fix.items() if k != "why"}
        before = {k: row[k] for k in fields}
        record.append({"id": qid, "why": fix["why"], "before": before, "after": fields})
        if args.apply:
            sets = ", ".join(f"{k}=?" for k in fields)
            con.execute(f"UPDATE questions SET {sets}, edited=1 WHERE id=?",
                        [*fields.values(), qid])
        print(f"  [{row['form_id']} pos {row['form_position']}] {fix['why']}")
    if args.apply:
        prior = json.loads(RECORD.read_text()) if RECORD.exists() else []
        seen = {x["id"] for x in prior}
        RECORD.write_text(json.dumps(
            prior + [x for x in record if x["id"] not in seen], indent=2,
            ensure_ascii=False) + "\n")
        con.commit()
        print(f"\napplied {len(record)}; record -> {RECORD}")
    else:
        print(f"\n{len(record)} to repair (dry run)")


if __name__ == "__main__":
    main()
