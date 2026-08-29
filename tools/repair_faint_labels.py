#!/usr/bin/env python3
"""Bring figure labels printed as watermarks back up to readable ink.

Found on the way to marking the angles for VIC review round 6. `e5a59579` asks for
y from a triangle whose three interior angles are "(3y−10)°", "(2y−5)°" and
"(y−15)°" -- and draws all three at `fill-opacity=".18"`, pale grey on the review
card's white. The question is unanswerable as rendered, and no check was looking.

One generator, one value, 28 figures across eight books: angle sizes, coordinates,
side lengths, the names on a bar chart. `figure_lib` draws tick numbers at .75 and
everything else at .9, so text under .4 is never a deliberate choice.

`label_too_faint` is the check; this raises every offender to .9 and re-runs the
figure check set, rolling back anything that comes back worse.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_faint_labels --report
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_faint_labels --apply
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import question_checks as qc                       # noqa: E402
from tools.repair_angle_arcs import figure_state              # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
MANIFEST = ROOT / "run_data/output/faint_label_repairs.json"

INK = "0.9"


def brighten(svg: str, floor: float = 0.4) -> tuple[str, list[str]]:
    raised: list[str] = []

    def ink(tag: str) -> str:
        return re.sub(r'fill-opacity=[\'"][\d.]+[\'"]', f'fill-opacity="{INK}"',
                      tag, count=1)

    def fix_text(m: re.Match) -> str:
        tag, op = m.group(0), float(m.group(1))
        label = (m.group(2) or "").strip()
        if op >= floor or not label:
            return tag
        raised.append(label)
        return ink(tag)

    def fix_dot(m: re.Match) -> str:
        tag = m.group(0)
        rr = re.search(r"\br=[\'\"]([\d.]+)", tag)
        fo = re.search(r"fill-opacity=[\'\"]([\d.]+)", tag)
        if not (rr and fo) or float(rr.group(1)) > 7 or float(fo.group(1)) >= floor:
            return tag
        if 'fill="none"' in tag or "fill='none'" in tag:
            return tag
        raised.append(f"dot r={rr.group(1)}")
        return ink(tag)

    return qc._ANY_CIRCLE.sub(fix_dot, qc._FAINT_TEXT.sub(fix_text, svg)), raised


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute(
        "SELECT * FROM questions WHERE review_status != 'rejected' "
        "AND figure_svg IS NOT NULL AND figure_svg != ''")]
    todo = [r for r in rows if qc.label_too_faint(r["figure_svg"])]
    print(f"{len(todo)} figures print a label as a watermark\n")

    fixed, rolled_back = [], []
    for q in todo:
        old = q["figure_svg"]
        new, raised = brighten(old)
        if new == old:
            continue
        regressed = sorted(figure_state(new) - figure_state(old))
        if regressed:
            rolled_back.append((q["id"], q["source_book"], regressed))
            continue
        fixed.append((q["id"], q["source_book"], q["form_id"], raised, new))
        print(f"  {q['id'][:8]} {q['source_book']:<22} {raised}")

    print(f"\n  raised       {len(fixed)}")
    print(f"  rolled back  {len(rolled_back)}")
    for qid, book, regressed in rolled_back:
        print(f"  ROLLBACK {qid[:8]} {book:<22} {regressed}")

    if a.apply and fixed:
        for qid, _b, _f, _r, new in fixed:
            con.execute("UPDATE questions SET figure_svg = ? WHERE id = ?", (new, qid))
        con.commit()
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(json.dumps(
            {"generated_from": "tools/repair_faint_labels.py",
             "raised": [{"id": q, "book": b, "form": f, "labels": r}
                        for q, b, f, r, _ in fixed],
             "rolled_back": [{"id": q, "book": b, "checks": c}
                             for q, b, c in rolled_back]}, indent=2))
        print(f"\nwrote {len(fixed)} figures and {MANIFEST}")
    elif not a.apply:
        print("\ndry run — pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
