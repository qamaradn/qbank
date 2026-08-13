"""Withhold questions whose CONTENT belongs to a different subject than their label.

Found on 2026-08-13 while blind-solving vic-drill-mq-001, which contains a question about
sectional tensions before the American Civil War. It is filed under
`quantitative_reasoning` and was dealt into a VIC Maths and Quantitative drill form, where
a candidate expecting arithmetic meets US constitutional history.

A sweep for humanities vocabulary inside maths, quantitative and logical questions found
nine candidates. Four are false positives — `lr_thinking_skills` puzzles that merely use a
novel or a poet as an object to order ("Five books stand in a row: an atlas, a novel, a
diary..."). The other five are real, all from `act_test10`, all asking a candidate to draw
an analogy between an 1850s American political event and an Australian one.

WITHHELD, NOT REJECTED. These are competent questions; they are in the wrong component.
Nothing in the seven subjects fits them: `logical_reasoning` is NSW Thinking Skills and
these need US history a Year 6 candidate has not met, and `reading_comprehension` would
need the passage they refer to. So they are treated exactly as the beyond-Year-8
quantitative items are — held out of the push and lifted out of their forms, while staying
in the bank in case a humanities component ever exists.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.qr_off_subject --report
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.qr_off_subject --manifest
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "run_data" / "db" / "qbank.db"
MANIFEST = REPO_ROOT / "run_data" / "output" / "qr_off_subject.json"

# Hand-verified by reading each one. The reason is what the question actually tests.
OFF_SUBJECT: list[tuple[str, str]] = [
    ("0afbf000-4cb9-4864-b22c-e22cbb3cd688", "US civics — the Kansas-Nebraska Act, asked for an Australian analogy"),
    ("266081a0-fedd-417b-a760-22e7f1364989", "US history — Lincoln on the Founding Fathers and slavery"),
    ("8d01f100-8c8c-4934-9ed4-320fdfb139b3", "US history — sectional tensions before the Civil War"),
    ("1f35755e-2ce8-400a-b036-01532984e363", "US law — the Dred Scott decision"),
    ("3c1109b3-9ce4-42b5-a445-1892e46a4b65", "US political science — ideological drift in 1850s America"),
]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--manifest", action="store_true")
    args = ap.parse_args()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = []
    for qid, why in OFF_SUBJECT:
        r = conn.execute("SELECT * FROM questions WHERE id = ?", (qid,)).fetchone()
        if r is None:
            print(f"MISSING {qid}")
            continue
        rows.append({"id": qid, "reason": why, "subject": r["subject"],
                     "topic": r["topic"], "source_book": r["source_book"],
                     "form_id": r["form_id"], "review_status": r["review_status"],
                     "stem": " ".join(r["stem"].split())[:150]})

    if args.report or not args.manifest:
        print(f"{len(rows)} off-subject question(s) withheld\n")
        for r in rows:
            print(f"  [{r['source_book']} | {r['subject']}] form={r['form_id']}")
            print(f"     {r['reason']}")
            print(f"     {r['stem'][:110]}")

    if args.manifest:
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(json.dumps(
            {"generated_from": "tools/qr_off_subject.py",
             "excluded": rows}, indent=2))
        print(f"wrote {MANIFEST} ({len(rows)} withheld)")


if __name__ == "__main__":
    main()
