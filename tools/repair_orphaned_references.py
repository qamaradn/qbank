#!/usr/bin/env python3
"""Repair questions that point back at a question the student will never see.

These were authored as a SET against one chart, table or scenario -- question one
introduces it, questions two to six say "Using the same chart...". That works in the
generated file, where they sit together. It stops working the moment `assign_forms`
deals them, because the dealer places each question independently: the pie chart
question lands in mq-018 and its opener lands in mq-084.

Two severities:

  * no figure of its own -- genuinely unanswerable. "Taking one token from that same
    tin of 12" reached vic-drill-mq-019 while the tin's contents (5 red, 3 blue, 4
    green) went to vic-drill-mq-068. Blind-solve returned no defensible option, which
    is how this was found. The setup is restated in the stem.
  * carries its own figure -- answerable, because the chart travelled with it, but the
    wording still sends the student hunting for a previous question that is not there.
    The opener is repointed at the figure the question actually carries.

Neither class is a wrong answer, so nothing here is rejected.

Not repaired, and checked by hand: "Using the same rule: ACE->CEA, BIT->ITB" states its
rule in its own stem, and a kayak-hire question carries its table inline as text. Those
are self-contained despite matching the phrase.
"""
import argparse
import json
import pathlib
import re
import sqlite3

ROOT = pathlib.Path(__file__).resolve().parents[1]
DB = ROOT / "run_data/db/qbank.db"
RECORD = ROOT / "run_data/output/orphaned_reference_repairs.json"

# Stems with no figure: the setup has to come back into the stem itself.
RESTATE = [
    ("Taking one token from that same tin of 12, how likely is it to be any colour "
     "other than red?",
     "A tin at the front desk contains 5 red, 3 blue and 4 green raffle tokens. A "
     "student takes one without looking. How likely is it to be any colour other "
     "than red?"),
    ("Using the same two machines, a number now goes into B first and then into A. "
     "If 5 goes into B, what comes out of A?",
     "Machine A multiplies by 3 and Machine B adds 7. A number goes into B first, and "
     "whatever comes out of B goes straight into A. If 5 goes into B, what comes out "
     "of A?"),
    # This one had no companion anywhere -- the question that set up the line of tables
    # does not exist in the bank at all, so the pattern is restated from the rule its
    # own explanation uses (2 x tables + 2).
    ("Using the same line of square tables, how many tables are needed to seat 26 "
     "people?",
     "Square tables are pushed together in a straight line to make one long table. One "
     "table on its own seats 4 people, two pushed together seat 6, three seat 8, and so "
     "on. How many tables are needed to seat 26 people?"),
    ("Using the same wheel, the game is played 60 times. About how many times would "
     "you expect it to land on WIN?",
     "A wheel has 12 equal sectors: 2 marked WIN, 3 marked SPIN AGAIN and 7 marked "
     "LOSE. The game is played 60 times. About how many times would you expect the "
     "wheel to land on WIN?"),
    ("In the same bag of 12 counters, what is the probability of taking a counter "
     "that is not red?",
     "A bag holds 4 red counters, 5 blue counters and 3 green counters. One counter "
     "is taken without looking. What is the probability that it is not red?"),
]

# Stems that do carry their figure: repoint the opener at it.
OPENER = re.compile(r"^(Using|In|For) th(?:e|at) same ([a-z][a-z ]*?)(?=[,.]|\s+of\b)", re.I)


def repoint(stem):
    m = OPENER.match(stem)
    if not m:
        return None
    lead, noun = m.group(1), m.group(2)
    rest = stem[m.end():]
    # "Using the same pie chart of 24 students, ..." -> keep the qualifier, then say
    # where to look: "Using the pie chart of 24 students shown below, ..."
    qual = ""
    mq = re.match(r"\s+of\b[^,.]*", rest)
    if mq:
        qual, rest = mq.group(0).rstrip(), rest[mq.end():]
    lead = {"for": "For", "using": "Using", "in": "In"}[lead.lower()]
    article = "the"
    return f"{lead} {article} {noun}{qual} shown below{rest}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    record = []

    for was, now in RESTATE:
        rows = [dict(r) for r in con.execute(
            "SELECT id, stem, form_id, figure_svg FROM questions "
            "WHERE stem=? AND review_status!='rejected'", (was,))]
        for r in rows:
            assert not r["figure_svg"], f"{r['id']} has a figure; restating would duplicate it"
            record.append({"id": r["id"], "form_id": r["form_id"], "kind": "restated",
                           "was": was, "now": now})
            if args.apply:
                con.execute("UPDATE questions SET stem=?, edited=1 WHERE id=?", (now, r["id"]))
            print(f"  RESTATED [{r['form_id']}] {now[:70]}...")

    for r in con.execute("SELECT id, stem, form_id, figure_svg FROM questions "
                         "WHERE review_status!='rejected' AND form_id IS NOT NULL"):
        if any(r["stem"] == w for w, _ in RESTATE):
            continue
        now = repoint(r["stem"])
        if not now or now == r["stem"]:
            continue
        if not r["figure_svg"]:
            print(f"  !! [{r['form_id']}] no figure and not in RESTATE: {r['stem'][:70]}")
            continue
        record.append({"id": r["id"], "form_id": r["form_id"], "kind": "repointed",
                       "was": r["stem"], "now": now})
        if args.apply:
            con.execute("UPDATE questions SET stem=?, edited=1 WHERE id=?", (now, r["id"]))
        print(f"  repointed [{r['form_id']}] {now[:80]}")

    if args.apply and record:
        prior = json.loads(RECORD.read_text()) if RECORD.exists() else []
        seen = {x["id"] for x in prior}
        prior += [x for x in record if x["id"] not in seen]
        RECORD.write_text(json.dumps(prior, indent=2) + "\n")
        con.commit()
        print(f"\napplied {len(record)}; record -> {RECORD}")
    else:
        print(f"\n{len(record)} to repair (dry run)")


if __name__ == "__main__":
    main()
