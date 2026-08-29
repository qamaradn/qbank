#!/usr/bin/env python3
"""Stop drawing a pie chart's circumference twice.

"The top part of the circumference has double lining", said a reviewer in VIC
round 1. The cause is a full `<circle>` stroked as the chart's outline AND stroked
sector paths whose arcs cover that same circumference. Two strokes a fraction
apart read as a smudged or thickened edge.

The sectors have to keep their arcs -- the arc IS the sector's shape, and the
dividing lines between slices carry the reading. So the full circle gives up its
stroke and keeps its fill. Nothing moves and nothing is removed; one redundant
outline stops being inked.

Only fires where the arcs are genuinely inked and the circle is a SOLID stroke: a
dashed circle behind a solid sector says "and this is the rest of the circle",
and an annulus draws its ring as one unstroked evenodd path whose subpaths sit at
exactly the radii its boundary circles stroke. Four of the first seven hits were
one of those two, and are correct drawing.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_doubled_circles --dry-run
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_doubled_circles --apply
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

from tools import question_checks as qc                  # noqa: E402
from tools.repair_angle_arcs import figure_state         # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
MANIFEST = ROOT / "run_data/output/doubled_circle_repairs.json"


def unstroke_outline(svg: str) -> tuple[str, str | None]:
    """Drop the stroke from the big circle the sector arcs already draw."""
    radii = set()
    for m in re.finditer(r"<path[^>]*>", svg):
        if not re.search(r"stroke=[\'\"](?!none)", m.group(0)):
            continue
        for am in qc._ARC_R.finditer(m.group(0)):
            rx, ry = float(am.group(1)), float(am.group(2))
            if rx == ry:
                radii.add(round(rx, 1))
    if not radii:
        return svg, None
    for m in re.finditer(r"<circle[^>]*>", svg):
        tag = m.group(0)
        rr = re.search(r"\br=[\'\"]([\d.]+)", tag)
        if not rr or round(float(rr.group(1)), 1) not in radii:
            continue
        if not re.search(r"stroke=[\'\"](?!none)", tag) or "stroke-dasharray" in tag:
            continue
        new = re.sub(r"\s*stroke=[\'\"][^\'\"]*[\'\"]", "", tag)
        new = re.sub(r"\s*stroke-width=[\'\"][^\'\"]*[\'\"]", "", new)
        return svg.replace(tag, new, 1), f"r={rr.group(1)}"
    return svg, None


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
    todo = [q for q in rows if qc.doubled_circle_outline(q["figure_svg"])]
    print(f"{len(todo)} figure(s) draw their circumference twice\n")

    record, failed = [], 0
    for q in todo:
        new, which = unstroke_outline(q["figure_svg"])
        regressed = sorted(figure_state(new) - figure_state(q["figure_svg"]))
        ok = which is not None and not regressed and \
            not qc.doubled_circle_outline(new)
        failed += not ok
        note = which or "no matching circle found"
        print(f"  {q['id'][:8]} {q['source_book']:<22} unstroked {note}  "
              f"{'OK' if ok else 'FAILED ' + str(regressed)}")
        record.append({"id": q["id"], "book": q["source_book"],
                       "form": q["form_id"], "unstroked": which})
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
