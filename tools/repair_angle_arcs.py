#!/usr/bin/env python3
"""Draw the angle mark on every figure that names an angle and does not show one.

VIC review round 6, 2026-08-27:

    "For all of the angle-related questions, make sure there is a small angle arc
     to signal this is the angle being mentioned."

That is a convention for the bank, not a request about one picture, so it is a
sweep: `angle_named_without_arc` over every served figure, not just the flagged
one. The flagged figure (`0ac8b411`, parallel lines cut by a transversal) printed a
bare "65°" and a bare "b" at two of the eight angles those three lines make, and
said "as shown".

HOW THE MARK IS PLACED. Not by hand and not by a rule of thumb. `figure_lib`
collects the figure's own segments, finds the vertices where they meet or cross,
takes the vertex nearest the label, and works out which SECTOR of that vertex the
label is already sitting in. The arc is then drawn between the two rays bounding
that sector. So the arc marks the angle the label names, or the script declines --
it cannot mark a different one.

WHERE IT DECLINES it says so and changes nothing. An octagon's "?°" printed at the
centre of the shape names an interior angle without saying which vertex; a pie
chart's "90°" is a slice size the slice already shows. Those are for a human, and
`--report` lists them.

Every write is verified: the full figure check set runs on the new SVG, and any
figure that comes back worse than it went in is rolled back. That guard caught
three redraws in round 5 and is the reason this can run over 46 figures unattended.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_angle_arcs --report
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_angle_arcs --apply
"""
from __future__ import annotations

import argparse
import math
import json
import pathlib
import re
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import figure_lib as fl          # noqa: E402
from tools import question_checks as qc     # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
MANIFEST = ROOT / "run_data/output/angle_arc_repairs.json"

# Run on the new SVG and compared against the old. A figure may not come back with
# a check firing that was clean before it -- an arc that overlaps a label or bulges
# off its vertex is worse than the bare number it replaced.
FIGURE_CHECKS = ("doubled_circle_outline", "overlapping_text_labels",
                 "plotted_points_inconsistent", "text_overlaps_geometry",
                 "axes_unlabelled", "angle_arc_malformed", "axis_scale_nonlinear",
                 "coordinate_figure_without_grid", "gridlines_off_the_ticks",
                 "unknown_marker_far_from_point")


def figure_state(svg: str) -> set[str]:
    out = set()
    for name in FIGURE_CHECKS:
        try:
            if getattr(qc, name)(svg):
                out.add(name)
        except Exception as exc:                      # a check that dies is news
            out.add(f"{name}:crashed:{exc}")
    for e in qc.figure_svg_errors(svg) or []:
        out.add(f"figure_svg_errors:{e}")
    return out


def stroke_colour(svg: str) -> str:
    """Match the figure's own ink. Half these books hardcode #1a1a2a."""
    hits = re.findall(r'stroke=[\'"]([^\'"]+)[\'"]', svg)
    for h in hits:
        if h not in ("none",):
            return h
    return "currentColor"


def _all_boxes(svg: str):
    return [(b, m.group(0)) for m in qc._TEXT.finditer(svg)
            if (b := qc._text_box(m))]


def _arc_hits(v, a1, a2, r, boxes, pad=2.5, steps=28):
    """Does an arc of radius r between these rays pass through any of these boxes?"""
    span = (a2 - a1) % (2 * 3.141592653589793)
    for i in range(steps + 1):
        ang = a1 + span * i / steps
        x = v[0] + r * math.cos(ang)
        y = v[1] + r * math.sin(ang)
        for b in boxes:
            if (b[0] - pad <= x <= b[2] + pad) and (b[1] - pad <= y <= b[3] + pad):
                return True
    return False


def move_text(svg: str, tag: str, x: float, y: float) -> str:
    """Rewrite one <text>'s x and y, leaving every other attribute alone."""
    moved = re.sub(r'\bx=[\'"][-\d.]+[\'"]', f'x="{x:.1f}"', tag, count=1)
    moved = re.sub(r'\by=[\'"][-\d.]+[\'"]', f'y="{y:.1f}"', moved, count=1)
    return svg.replace(tag, moved, 1)


def mark_angles(svg: str, stem: str) -> tuple[str, list[str], list[str]]:
    """Return (new_svg, marked_labels, declined_labels)."""
    colour = stroke_colour(svg)
    marks, done, skipped, moves = [], [], [], []
    at_vertex: dict[tuple[int, int], int] = {}
    for box, tag in qc.angle_labels(svg, stem):
        label = box[4].strip()
        found = fl.angle_at_label(svg, box)
        # The label is not in any sector of any vertex, which almost always means it
        # was printed just OUTSIDE the corner it names. Round 5 asked for "angle
        # values always within the shape" and put that in figure_lib; these books
        # predate it. Bring the label in, then mark the angle it now sits in.
        relocate = found is None
        if relocate:
            found = fl.interior_angle_at(svg, box)
        if not found:
            skipped.append(label)
            continue
        v, a1, a2, reach = found
        # Two marks at ONE vertex get different radii. Drawn at the same radius the
        # 68° and its vertically opposite z closed into what reads as a circle round
        # the crossing -- and a doubled circumference is a defect a reviewer has
        # already raised once.
        key = (round(v[0]), round(v[1]))
        nth = at_vertex.get(key, 0)
        # Shrink until the arc misses every OTHER label. Its own label is moved out
        # of the way instead; a vertex letter or a side length cannot be, so the arc
        # gives way to it. Without this, "B" and "C" naming the two crossings ended
        # up struck through by the arcs measured at them.
        others = [b for b, _t in _all_boxes(svg) if b[:4] != box[:4]]
        nominal = fl.arc_radius(reach) + 5.0 * nth
        cap = max(9.0, min(28.0, 0.45 * reach))
        # Both directions. A vertex letter parked INSIDE the sector -- "O" naming the
        # crossing, 13 px out -- blocks every radius below it, and the arc that
        # clears it is a larger one, not a smaller.
        cands = [nominal] + [nominal + s * d for d in (2, 4, 6, 8, 10) for s in (-1, 1)]
        r = next((c for c in cands if 9.0 <= c <= cap
                  and not _arc_hits(v, a1, a2, c, others)), None)
        drawn = fl.angle_mark(v, a1, a2, r, colour=colour, label=label) if r else None
        if not drawn:
            skipped.append(label)
            continue
        marks.append(drawn)
        done.append(label)
        at_vertex[key] = nth + 1
        pos = (fl.label_on_bisector(v, a1, a2, box, r) if relocate
               else fl.label_clear_of_arc(v, a1, a2, box, r))
        if pos:
            moves.append((tag, pos))
    if not marks:
        return svg, done, skipped
    for tag, (cx, cy) in moves:
        svg = move_text(svg, tag, *qc.text_xy_for_centre(tag, cx, cy))
    # Marks go in LAST so they sit over the fill of a shape rather than under it.
    return svg[: svg.rindex("</svg>")] + "".join(marks) + "</svg>", done, skipped


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="write to the database")
    ap.add_argument("--report", action="store_true", help="list without writing")
    ap.add_argument("--ids", help="restrict to these question ids (comma separated)")
    a = ap.parse_args()

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute(
        "SELECT * FROM questions WHERE review_status != 'rejected' "
        "AND figure_svg IS NOT NULL AND figure_svg != ''")]
    if a.ids:
        want = {i.strip() for i in a.ids.split(",") if i.strip()}
        rows = [r for r in rows if any(r["id"].startswith(w) for w in want)]

    todo = [r for r in rows if qc.angle_named_without_arc(r)]
    print(f"{len(todo)} figures name an angle with nothing marking it\n")

    fixed, declined, rolled_back = [], [], []
    for q in todo:
        old = q["figure_svg"]
        new, done, skipped = mark_angles(old, q["stem"] or "")
        if new == old:
            declined.append((q["id"], q["source_book"], skipped, "no mark could be placed"))
            continue
        before, after = figure_state(old), figure_state(new)
        regressed = sorted(after - before)
        if regressed:
            rolled_back.append((q["id"], q["source_book"], regressed))
            continue
        if qc.angle_named_without_arc({**q, "figure_svg": new}):
            declined.append((q["id"], q["source_book"], skipped,
                             "still has an unmarked angle after the pass"))
            continue
        fixed.append((q["id"], q["source_book"], q["form_id"], done, new))

    print(f"  marked          {len(fixed)}")
    print(f"  declined        {len(declined)}   (needs a human)")
    print(f"  rolled back     {len(rolled_back)}   (the mark made a check fire)\n")
    for qid, book, labels, why in declined:
        print(f"  DECLINED {qid[:8]} {book:<22} {why}: {labels}")
    for qid, book, regressed in rolled_back:
        print(f"  ROLLBACK {qid[:8]} {book:<22} {regressed}")

    if a.apply and fixed:
        for qid, _b, _f, _d, new in fixed:
            con.execute("UPDATE questions SET figure_svg = ? WHERE id = ?", (new, qid))
        con.commit()
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(json.dumps(
            {"generated_from": "tools/repair_angle_arcs.py",
             "marked": [{"id": q, "book": b, "form": f, "labels": d}
                        for q, b, f, d, _ in fixed],
             "declined": [{"id": q, "book": b, "labels": s, "why": w}
                          for q, b, s, w in declined],
             "rolled_back": [{"id": q, "book": b, "checks": c}
                             for q, b, c in rolled_back]}, indent=2))
        print(f"\nwrote {len(fixed)} figures and {MANIFEST}")
    elif not a.apply:
        print("\ndry run — pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
