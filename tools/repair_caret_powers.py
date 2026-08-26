#!/usr/bin/env python3
"""Convert caret powers to real superscript characters.

Selectly renders a stem as plain text, so "x^2" reaches the student as "x^2". It is
readable, but next to the questions that already use superscripts it reads as two
different papers, and a caret is not how a printed exam writes a power.

Exponents that have no superscript character -- "^(1/2)", "^(4x2)" -- are left alone and
reported. Rewording those is authoring, not formatting.
"""
import argparse
import json
import pathlib
import re
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.question_checks import _CARET, superscript  # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
RECORD = ROOT / "run_data/output/caret_power_repairs.json"
FIELDS = ("stem", "option_a", "option_b", "option_c", "option_d", "explanation")


def convert(text):
    """Return (new_text, n_converted, n_left). Leaves what it cannot render."""
    left = [0]

    def rep(m):
        sup = superscript((m.group(1) or m.group(2)).strip())
        if sup is None:
            left[0] += 1
            return m.group(0)
        return sup

    new, n = _CARET.subn(rep, text)
    return new, n - left[0], left[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--forms-only", action="store_true",
                    help="restrict to questions carrying a form (the servable bank)")
    args = ap.parse_args()
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    q = "SELECT * FROM questions WHERE review_status!='rejected'"
    if args.forms_only:
        q += " AND form_id IS NOT NULL"
    changed = stubborn = 0
    record = []
    for r in (dict(x) for x in con.execute(q)):
        updates, conv, kept = {}, 0, 0
        for f in FIELDS:
            text = str(r[f] or "")
            if "^" not in text:
                continue
            new, n, k = convert(text)
            conv += n
            kept += k
            if new != text:
                updates[f] = new
        if not updates:
            stubborn += 1 if kept else 0
            continue
        changed += 1
        stubborn += 1 if kept else 0
        record.append({"id": r["id"], "form_id": r["form_id"], "converted": conv,
                       "left": kept})
        if args.apply:
            sets = ", ".join(f"{k}=?" for k in updates)
            con.execute(f"UPDATE questions SET {sets}, edited=1 WHERE id=?",
                        [*updates.values(), r["id"]])
    if args.apply:
        RECORD.write_text(json.dumps(record, indent=2) + "\n")
        con.commit()
    print(f"{'converted' if args.apply else 'would convert'} {changed} question(s); "
          f"{sum(x['converted'] for x in record)} powers rewritten")
    if stubborn:
        print(f"{stubborn} still hold a caret that has no superscript form "
              f"(e.g. ^(1/2), ^(4x2)) — those need rewording, not formatting")


if __name__ == "__main__":
    main()
