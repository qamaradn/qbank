#!/usr/bin/env python3
"""Repair the vocabulary-cloze gap marker: ___(1)___  ->  ___ (1) ___

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_cloze_marker [--apply]

WHY
---
`___(1)___` is markdown for bold-italic. The two surfaces that show a passage disagree
about it, and the REVIEWER gets the broken one:

  student  (Selectly, plain text in a `white-space: pre-wrap` div, McqQuestion.tsx)
           "...which makes it ___(1)___ difficult to find."      correct
  reviewer (review UI, marked.parse)
           "...which makes it (1) difficult to find."            the blank has vanished

So the 120 cloze questions sitting in the review queue show a stray "(1)" where the gap
should be, which reads as a formatting bug rather than as a question.

WHY THIS MARKER
---------------
`___ (1) ___` renders identically in both. Markdown only opens emphasis when the
delimiter is followed by non-whitespace, so the space after the underscores makes them
literal — verified against the same `marked` build the review UI loads. It also still
LOOKS like a blank, which `[ 1 ]` does less well for a missing word. The structural cloze
keeps `[ 1 ]`, because there the gap is a whole sentence rather than a word.

SAFETY
------
All 120 rows are `pending` and none have been pushed to Selectly, so no `passageId` is in
use anywhere and changing the passage text has no downstream effect. The DB, the four
batch JSON files and the four builders are all updated together, and the before/after is
recorded in run_data/output/cloze_marker_repair.json.
"""
import argparse
import json
import pathlib
import re
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
GEN = ROOT / "run_data/output/reading_comprehension/generated"
DB = ROOT / "run_data/db/qbank.db"
RECORD = ROOT / "run_data/output/cloze_marker_repair.json"
BOOK = "rc_nsw_cloze"

OLD = re.compile(r"_{2,}\((\d+)\)_{2,}")
NEW = r"___ (\1) ___"


def fix(text):
    return OLD.sub(NEW, text or "")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--apply", action="store_true", help="write the changes")
    args = ap.parse_args()

    con = sqlite3.connect(DB)
    rows = con.execute(
        "SELECT id, passage, review_status FROM questions WHERE source_book=?", (BOOK,)
    ).fetchall()
    if not rows:
        sys.exit(f"no {BOOK} rows found")

    live = [r for r in rows if r[2] != "pending"]
    if live:
        sys.exit(f"{len(live)} rows are not pending — check whether any were pushed "
                 f"before changing passage text")

    changed = [(rid, p, fix(p)) for rid, p, _ in rows if fix(p) != p]
    passages = {old for _, old, _ in changed}
    print(f"{len(changed)} of {len(rows)} rows carry the old marker, "
          f"across {len(passages)} distinct passages")

    files = sorted(GEN.glob(f"{BOOK}_p*.json"))
    file_hits = {}
    for f in files:
        s = f.read_text(encoding="utf-8")
        n = len(OLD.findall(s))
        if n:
            file_hits[f.name] = n
    print("batch files:", file_hits)

    if not args.apply:
        print("\ndry run — pass --apply to write. Sample:")
        _, old, new = changed[0]
        i = OLD.search(old).start()
        print("  before:", repr(old[max(0, i-40):i+20]))
        print("  after: ", repr(new[max(0, i-40):i+24]))
        return

    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps({
        "marker": {"from": "___(n)___", "to": "___ (n) ___"},
        "reason": "markdown read ___(n)___ as bold-italic, so the review UI showed the "
                  "reviewer a bare (n) with no blank in it; Selectly, which renders the "
                  "passage as plain text, showed it correctly",
        "rows": [rid for rid, _, _ in changed],
        "distinct_passages": len(passages),
        "batch_files": file_hits,
    }, indent=1), encoding="utf-8")

    for rid, _, new in changed:
        con.execute("UPDATE questions SET passage=? WHERE id=?", (new, rid))
    con.commit()

    for f in files:
        s = f.read_text(encoding="utf-8")
        f.write_text(OLD.sub(NEW, s), encoding="utf-8")

    left = con.execute(
        "SELECT COUNT(*) FROM questions WHERE source_book=? AND passage LIKE '%___(%'",
        (BOOK,)).fetchone()[0]
    print(f"applied. rows still carrying the old marker: {left}")
    print(f"record written to {RECORD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
