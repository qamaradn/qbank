#!/usr/bin/env python3
"""Give an arrowhead to the figures that ask for one and never define it.

Three figures carry `marker-end="url(#arr)"` on a line and define no `<marker>`
anywhere in the document. A browser resolves the reference to nothing and draws
the line without its head, silently — so an arrow the author put there to mean
"this direction" or "this measurement" is simply absent, and nothing complains.
cairosvg is the only thing that ever noticed, and it noticed by crashing.

No check catches this because every check reads the SVG as text: the reference is
present, well-formed and points at an id, and only resolving it shows there is
nothing on the other end. `undefined_marker_reference` is that check.

The repair adds the marker the reference is asking for, drawn in currentColor at
the size the rest of these figures use for arrowheads. It does not move or remove
anything, so a figure cannot be made wrong by it -- only completed.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_missing_markers --dry-run
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_missing_markers --apply
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

from tools import question_checks as qc          # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
MANIFEST = ROOT / "run_data/output/missing_marker_repairs.json"


def marker_def(mid: str) -> str:
    """A plain filled arrowhead, in currentColor so it follows the theme."""
    return (f'<defs><marker id="{mid}" markerWidth="7" markerHeight="7" refX="6" '
            f'refY="3" orient="auto" markerUnits="strokeWidth">'
            f'<path d="M0,0 L7,3 L0,6 Z" fill="currentColor"/></marker></defs>')


def add_markers(svg: str) -> tuple[str, list[str]]:
    missing = sorted(qc.undefined_marker_reference(svg, ids_only=True) or [])
    if not missing:
        return svg, []
    defs = "".join(marker_def(m) for m in missing)
    i = svg.index(">") + 1
    return svg[:i] + defs + svg[i:], missing


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if not (a.apply or a.dry_run):
        raise SystemExit("pass --apply or --dry-run")

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute(
        "SELECT * FROM questions WHERE review_status != 'rejected' "
        "AND figure_svg IS NOT NULL AND figure_svg != ''")]
    todo = [q for q in rows if qc.undefined_marker_reference(q["figure_svg"])]
    print(f"{len(todo)} figure(s) reference a marker they never define\n")

    record, failed = [], 0
    for q in todo:
        new, added = add_markers(q["figure_svg"])
        still = qc.undefined_marker_reference(new)
        errs = qc.figure_svg_errors(new) or []
        ok = not still and not errs
        failed += not ok
        print(f"  {q['id'][:8]} {q['source_book']:<22} added {added}  "
              f"{'OK' if ok else 'STILL FAILING: ' + str(still or errs)}")
        record.append({"id": q["id"], "book": q["source_book"],
                       "form": q["form_id"], "added": added})
        if a.apply and ok:
            con.execute("UPDATE questions SET figure_svg=?, edited=1 WHERE id=?",
                        (new, q["id"]))

    if a.apply:
        if failed:
            con.rollback()
            raise SystemExit(f"\n{failed} failed — nothing written")
        con.commit()
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(json.dumps(record, indent=1))
        print(f"\napplied {len(record)} — manifest {MANIFEST}")
    else:
        print(f"\ndry run — {len(record)} figure(s), {failed} failing")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
