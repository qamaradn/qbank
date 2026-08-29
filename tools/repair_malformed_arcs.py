#!/usr/bin/env python3
"""Redraw angle arcs whose ends are not the same distance from their vertex.

`angle_arc_malformed` catches an arc that declares a radius its endpoints do not
sit on -- "declares r=18 but its ends are 17.09 and 24.17 from the vertex". SVG
then has to fit a circle of that radius through two points that are not both on
one, so the centre lands off the vertex and the arc bulges past the edge of the
shape. A reviewer saw it as "that little curve going outside the triangle by a
tiny bit near angle A".

Nudging the endpoints is guesswork. Round 6 built machinery that DERIVES an angle
mark from the figure's own segments -- the vertex, the two rays bounding the
sector the label sits in, one radius for both ends -- so an arc it draws cannot
have this fault by construction. This strips the malformed arcs and lets that
machinery put correct ones back.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_malformed_arcs --dry-run
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_malformed_arcs --apply
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import re
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import figure_lib as fl                                # noqa: E402
from tools import question_checks as qc                          # noqa: E402
from tools.repair_angle_arcs import figure_state                 # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
MANIFEST = ROOT / "run_data/output/malformed_arc_repairs.json"

# A path that is nothing but one elliptical arc: an angle mark, not part of a shape.
_ARC_ONLY = re.compile(
    r"<path[^>]*\bd=[\'\"]\s*M\s*([-\d.]+)[ ,]+([-\d.]+)\s*"
    r"A\s*([-\d.]+)[ ,]+([-\d.]+)[ ,]+[-\d.]+[ ,]+([01])[ ,]+([01])[ ,]+"
    r"([-\d.]+)[ ,]+([-\d.]+)[^\'\"]*[\'\"][^>]*/?>")


def fix_bad_arcs(svg: str) -> tuple[str, int]:
    """Redraw each bad arc AT THE SAME ANGLE, both ends on one radius.

    Not stripped. Stripping is what the first version did, and it took the mark off
    a phi at the origin and an alpha in a right triangle and put nothing back --
    those labels are Greek, which the angle-label reader does not claim, so nothing
    redrew them and the figure came back worse than it went in. The arc names an
    angle; the repair has to keep naming it.

    The vertex is the point the two ends are nearest to equidistant from, which is
    how `angle_arc_malformed` finds it too. Both ends are then recomputed at the
    SMALLER of the two original distances, so the mark stays inside the shape.
    """
    fixed = 0
    segs = fl.figure_segments(svg)
    verts = [p for s in segs for p in s]
    for i in range(len(segs)):
        for j in range(i + 1, len(segs)):
            p = fl._intersect(segs[i], segs[j])
            if p:
                verts.append(p)
    if not verts:
        return svg, 0
    for m in list(_ARC_ONLY.finditer(svg)):
        x1, y1, rx, ry = (float(m.group(k)) for k in (1, 2, 3, 4))
        x2, y2 = float(m.group(7)), float(m.group(8))
        if abs(rx - ry) > 0.01:
            continue
        # The vertex an arc is CENTRED on, not merely nearest to. Nearest picked a
        # point 73 px from a radius-25 arc on the phi-at-origin figure, because the
        # y-axis endpoint happened to be closer than the origin itself. The vertex
        # is the one whose two distances are nearly equal AND near the declared
        # radius, which is what being the centre of an arc means.
        def centredness(p):
            e1, e2 = math.dist(p, (x1, y1)), math.dist(p, (x2, y2))
            return abs(e1 - e2) + abs((e1 + e2) / 2 - rx)
        v = min(verts, key=centredness)
        d1, d2 = math.dist(v, (x1, y1)), math.dist(v, (x2, y2))
        if centredness(v) > 2.5 * max(rx, 1):
            continue                       # nothing here looks like its vertex
        if abs(d1 - d2) <= 0.15 and abs(d1 - rx) <= 0.15:
            continue                       # this one is already sound
        a1 = math.atan2(y1 - v[1], x1 - v[0])
        a2 = math.atan2(y2 - v[1], x2 - v[0])
        if (a2 - a1) % (2 * math.pi) > math.pi:
            a1, a2 = a2, a1                # keep the minor sector, as drawn
        colour = (re.search(r'stroke=[\'"]([^\'"]+)', m.group(0)) or
                  [None, "currentColor"])[1]
        redrawn = fl.angle_mark(v, a1, a2, min(d1, d2), colour=colour)
        if not redrawn:
            continue
        svg = svg.replace(m.group(0), redrawn, 1)
        fixed += 1
    return svg, fixed


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
    todo = [q for q in rows if qc.angle_arc_malformed(q["figure_svg"])]
    print(f"{len(todo)} figure(s) carry an arc that will not sit on its angle\n")

    record, failed = [], 0
    for q in todo:
        new, n = fix_bad_arcs(q["figure_svg"])
        regressed = sorted(figure_state(new) - figure_state(q["figure_svg"]))
        ok = n > 0 and not qc.angle_arc_malformed(new) and not regressed
        failed += not ok
        print(f"  {q['id'][:8]} {q['source_book']:<22} redrew {n} arc(s)"
              f"  {'OK' if ok else 'FAILED ' + str(regressed)}")
        record.append({"id": q["id"], "book": q["source_book"], "form": q["form_id"],
                       "arcs_redrawn": n})
        if a.apply and ok:
            con.execute("UPDATE questions SET figure_svg=?, edited=1 WHERE id=?",
                        (new, q["id"]))

    if a.apply:
        # Each write is verified on its own, so a figure this cannot fix does not
        # hold back the ones it can. The failures are named above and stay flagged.
        con.commit()
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(json.dumps(record, indent=1))
        print(f"\napplied {len(record)} — manifest {MANIFEST}")
    else:
        print(f"\ndry run — {len(record)} figure(s), {failed} failing")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
