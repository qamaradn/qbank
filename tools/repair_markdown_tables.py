#!/usr/bin/env python3
"""Move markdown tables out of question stems and into figures.

Selectly renders a stem as plain text in a `white-space: pre-wrap` div. There is no
markdown pass, by design -- §5.1 of the handover warns against adding one, because the
poetry passages rely on literal whitespace. So a pipe table reaches the student as pipes
and a row of dashes.

The first NSW review round flagged two of these: "Table format is quite messy and
wrong" and "Table is inaccurate, fix to make it more clear please." In both cases the
DATA was correct. That is the damaging part -- the question is right and looks wrong, so
the reviewer distrusts a sound item and the student loses time deciphering it.

`figure_lib.table` already draws exactly this, sizing columns to the widest cell. The
table becomes a figure; the prose around it stays in the stem.
"""
import argparse
import json
import pathlib
import re
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.figure_lib import table as draw_table          # noqa: E402
from tools.question_checks import markdown_table_in_stem  # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
RECORD = ROOT / "run_data/output/markdown_table_repairs.json"

_SEP = re.compile(r"^\s*\|?[\s:]*-{3,}[\s:|-]*\|")
_ROW = re.compile(r"^\s*\|.*\|\s*$")


def split_table(stem):
    """Return (prose, rows) or (stem, None). Rows are lists of cell strings."""
    lines = stem.split("\n")
    start = end = None
    for i, ln in enumerate(lines):
        if _SEP.match(ln):
            # the header sits directly above the separator
            start = i - 1
            end = i
            for j in range(i + 1, len(lines)):
                if _ROW.match(lines[j]):
                    end = j
                else:
                    break
            break
    if start is None or start < 0:
        return stem, None
    rows = []
    for ln in lines[start:end + 1]:
        if _SEP.match(ln):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        rows.append(cells)
    prose = "\n".join(lines[:start] + lines[end + 1:])
    prose = re.sub(r"\n{3,}", "\n\n", prose).strip()
    return prose, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--forms-like", default="",
                    help="restrict to form_ids matching this SQL LIKE pattern")
    args = ap.parse_args()

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    q = "SELECT * FROM questions WHERE review_status!='rejected'"
    params = []
    if args.forms_like:
        q += " AND form_id LIKE ?"
        params.append(args.forms_like)

    record, skipped = [], []
    for r in (dict(x) for x in con.execute(q, params)):
        if not markdown_table_in_stem(r):
            continue
        if r["figure_svg"]:
            skipped.append((r, "already has a figure — needs a human"))
            continue
        prose, rows = split_table(r["stem"])
        if not rows or len(rows) < 2:
            skipped.append((r, "could not parse the table"))
            continue
        svg = draw_table(rows)
        # The prose must still make sense once the table is a picture below it.
        if not prose.strip():
            skipped.append((r, "stem is nothing but the table"))
            continue
        record.append({"id": r["id"], "form_id": r["form_id"], "rows": rows,
                       "was": r["stem"], "now": prose})
        if args.apply:
            con.execute("UPDATE questions SET stem=?, figure_svg=?, edited=1 WHERE id=?",
                        (prose, svg, r["id"]))
        print(f"  [{r['form_id'] or '(no form)'}] {len(rows)}x{len(rows[0])} table -> figure"
              f"   {' '.join(prose.split())[:60]}")

    for r, why in skipped:
        print(f"  !! [{r['form_id']}] {why}: {' '.join(r['stem'].split())[:60]}")

    if args.apply and record:
        prior = json.loads(RECORD.read_text()) if RECORD.exists() else []
        seen = {x["id"] for x in prior}
        prior += [x for x in record if x["id"] not in seen]
        RECORD.write_text(json.dumps(prior, indent=2, ensure_ascii=False) + "\n")
        con.commit()
        print(f"\nconverted {len(record)}; record -> {RECORD}")
    else:
        print(f"\n{len(record)} to convert, {len(skipped)} skipped (dry run)")


if __name__ == "__main__":
    main()
