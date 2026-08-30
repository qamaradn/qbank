#!/usr/bin/env python3
"""One explanation that worked out the wrong box.

`e89214af` asks for the total surface area of a rectangular prism. Its figure is
labelled 8 cm, 6 cm and 4 cm; its key is 208 cm², which is what those three give:
2(8×6 + 8×4 + 6×4) = 2 × 104 = 208. Its explanation works out a 4 by 6 by 10 box
instead and arrives at 248 — a number that is not among the four options, so a student
who reads the explanation to check their work is told the question has no answer.

The figure and the key agree. The explanation is the odd one out, so it is the
explanation that changes. Nothing else on the question is touched: not the stem, not
the options, not the key.

Found while redrawing the figure, not by any check: no check compares the arithmetic
in an explanation against the numbers printed on the figure.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_vic_round8_explanation
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_vic_round8_explanation --apply
"""
import argparse
import json
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import question_checks as qc            # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
RECORD = ROOT / "run_data/output/vic_round8_explanation.json"

QID = "e89214af"
NEW = ("The box measures 8 cm by 6 cm by 4 cm. Opposite faces are identical, so the "
       "surface area is 2(8×6 + 8×4 + 6×4) = 2(48 + 32 + 24) = 2 × 104 = 208 cm². "
       "Answering 104 cm² counts each of the three different faces once and forgets "
       "that every face has an opposite one.")

CHECKS = ("leaked_working", "rewrites_the_question", "positional_reference",
          "disputes_its_own_key", "explanation_is_a_repair_note",
          "latex_markup_in_text", "caret_power_notation")


def state(q):
    out = set()
    for n in CHECKS:
        fn = getattr(qc, n)
        got = fn(q.get("explanation") or "") if n in (
            "leaked_working", "rewrites_the_question", "positional_reference",
            "disputes_its_own_key") else fn(q)
        if got:
            out.add(n)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    row = con.execute("SELECT * FROM questions WHERE id LIKE ?", (QID + "%",)).fetchone()
    if row is None:
        print("no such question")
        return
    q = dict(row)
    before = state(q)
    after_q = dict(q)
    after_q["explanation"] = NEW
    gained = state(after_q) - before
    if gained:
        print("refused —", sorted(gained))
        return
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps(
        {"applied": args.apply, "id": q["id"], "form": q["form_id"],
         "was": q["explanation"], "now": NEW}, indent=1, ensure_ascii=False))
    if args.apply:
        con.execute("UPDATE questions SET explanation = ?, edited = 1 WHERE id = ?",
                    (NEW, q["id"]))
        con.commit()
    print(f"was: {q['explanation']}")
    print(f"now: {NEW}")
    print("applied" if args.apply else "(dry run — pass --apply)")
    print(f"record -> {RECORD}")


if __name__ == "__main__":
    main()
