#!/usr/bin/env python3
"""The round 6 figures that no sweep could repair on its own.

Two reviewer flags arrived on 2026-08-27, both on figures round 5 had already been
through:

    25bbe5a8  "the question mark should be closer to the fourth vertex because
               right now it looks like its sat on -2,0"
    0ac8b411  "For all of the angle-related questions, make sure there is a small
               angle arc to signal this is the angle being mentioned."

Both reduce to a check and a sweep -- `unknown_marker_far_from_point` and
`angle_named_without_arc`, repaired in bulk by `repair_angle_arcs`. What is left
here is the residue: figures the sweeps correctly refused to touch, plus the two
further defects reading them turned up.

    25bbe5a8   REDRAWN. The "?" placement bug is fixed in `figure_lib.plane` -- the
               offset is measured from the label's EDGE, so a one-character label
               no longer lands a whole grid cell out. This regenerates the figure
               from the same call round 5 used.

    5c237d04   "A regular octagon is shown" -- drawn with TEN sides. The key, 135°,
               is right for the octagon in the words; a student who counts the
               sides in front of them reads 144°, which is sitting there as option
               A. Redrawn as a real regular octagon.
               `polygon_sides_disagree_with_stem` is the check.

    dad3322d   The triangle's apex is at y = -23 in a viewBox 190 tall: the corner
               whose angle the question asks for is off the canvas. Redrawn to the
               same three angles, scaled to fit, and the "?" put at the apex.

`722d6bab` needed no entry: it declined only because two triangles sharing a side
put the figure's overall centroid outside both of them, so the apexes had no sector
facing it. `interior_angle_at` now uses the polygon each vertex belongs to.

Usage:
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_vic_round6_figures --dry-run
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_vic_round6_figures --apply
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import question_checks as qc          # noqa: E402
from tools.figure_lib import plane, svg, txt     # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
MANIFEST = ROOT / "run_data/output/round6_figure_repairs.json"


def regular_polygon(n, cx=130, cy=110, r=84, vw=260, vh=220):
    """A genuinely regular n-gon, flat side down, so counting it gives n."""
    pts = []
    for i in range(n):
        a = -math.pi / 2 + math.pi / n + 2 * math.pi * i / n
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    body = (f'<polygon points="{poly}" fill="currentColor" fill-opacity=".05" '
            f'stroke="currentColor" stroke-width="2"/>')
    # The "?" goes AT a vertex, not at the centre. "One interior angle" has to name
    # one; printed in the middle of the shape it named none, which is why the arc
    # sweep declined it.
    v = pts[0]
    inx, iny = (cx - v[0]), (cy - v[1])
    d = math.hypot(inx, iny)
    body += txt(v[0] + 34 * inx / d, v[1] + 34 * iny / d + 4, "?°", 13)
    return svg(body, vb=f"0 0 {vw} {vh}")


def triangle_from_base_angles(a_deg, b_deg, base=180, x0=60, y0=170,
                              vw=340, vh=190, labels=("47°", "68°", "?")):
    """A triangle drawn to its own two base angles, scaled to fit the canvas.

    The original declared 47° and 68° and then placed the apex at y = -23 in a box
    190 tall, so the third angle -- the one the question asks for -- was off the
    page entirely.
    """
    ta, tb = math.tan(math.radians(a_deg)), math.tan(math.radians(b_deg))
    h = base / (1 / ta + 1 / tb)
    room = y0 - 26
    if h > room:                              # scale the whole triangle, not just h
        base *= room / h
        h = room
    ax, ay = x0, y0
    bx, by = x0 + base, y0
    px, py = x0 + h / ta, y0 - h
    body = (f'<path d="M{ax:.1f} {ay:.1f} L{bx:.1f} {by:.1f} L{px:.1f} {py:.1f} Z" '
            f'stroke="currentColor" stroke-opacity=".9" stroke-width="2" '
            f'fill="currentColor" fill-opacity=".05"/>')
    # Each label on its own corner's bisector, inside the triangle. The arcs are
    # added afterwards by repair_angle_arcs, from these positions.
    for (vx, vy), (ox, oy), text in (
            ((ax, ay), (34, -13), labels[0]),
            ((bx, by), (-34, -13), labels[1]),
            ((px, py), (0, 34), labels[2])):
        body += txt(vx + ox, vy + oy, text, 14)
    return svg(body, vb=f"0 0 {vw} {vh}")


REPAIRS = {
    "25bbe5a8": dict(
        why='the "?" sat a full grid cell from the vertex it names, on (-2, 0)',
        figure=lambda: plane(
            points={"(−1, 4)": (-1, 4), "(3, 4)": (3, 4), "(3, 0)": (3, 0),
                    "?": (-1, 0)},
            polygon=[(-1, 4), (3, 4), (3, 0), (-1, 0)],
            xr=(-2, 4), yr=(-1, 5), label_off=(0, -10)),
    ),
    "5c237d04": dict(
        why="a question about a regular octagon drawn with ten sides",
        figure=lambda: regular_polygon(8),
    ),
    "dad3322d": dict(
        why="the apex whose angle is asked for was drawn off the canvas at y = -23",
        figure=lambda: triangle_from_base_angles(47, 68),
    ),
}

SVG_CHECKS = ["gridlines_off_the_ticks", "overlapping_text_labels", "axes_unlabelled",
              "axis_scale_nonlinear", "coordinate_figure_without_grid",
              "text_overlaps_geometry", "plotted_points_inconsistent",
              "angle_arc_malformed", "doubled_circle_outline", "label_too_faint",
              "unknown_marker_far_from_point"]
Q_CHECKS = ["plotted_geometry_matches_stem", "figure_proportions_disagree",
            "one_point_on_the_line", "options_distinct_by_value",
            "polygon_sides_disagree_with_stem"]


def verify(q):
    out = []
    for n in SVG_CHECKS:
        if (m := getattr(qc, n)(q["figure_svg"])):
            out.append(f"{n}: {m}")
    for n in Q_CHECKS:
        if (m := getattr(qc, n)(q)):
            out.append(f"{n}: {m}")
    if (m := qc.figure_svg_errors(q["figure_svg"])):
        out += [f"figure_svg_errors: {x}" for x in m]
    return out


def outside_viewbox(s):
    """Anything drawn past the edge of the canvas is invisible, not merely ugly."""
    import re
    vb = re.search(r'viewBox="([^"]+)"', s)
    if not vb:
        return []
    x0, y0, w, h = (float(n) for n in vb.group(1).split())
    bad = []
    for m in re.finditer(r'\bd="([^"]+)"|\bpoints="([^"]+)"', s):
        raw = (m.group(1) or m.group(2)).replace(",", " ")
        nums = [float(n) for n in __import__("re").findall(r"-?\d+(?:\.\d+)?", raw)]
        for x, y in zip(nums[0::2], nums[1::2]):
            if not (x0 - 1 <= x <= x0 + w + 1 and y0 - 1 <= y <= y0 + h + 1):
                bad.append(f"({x:g}, {y:g}) is outside the viewBox")
    return bad


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not (args.apply or args.dry_run):
        raise SystemExit("pass --apply or --dry-run")

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    record, failed = [], 0

    for prefix, spec in REPAIRS.items():
        row = con.execute("SELECT * FROM questions WHERE id LIKE ?||'%'",
                          (prefix,)).fetchone()
        if row is None:
            raise SystemExit(f"{prefix} is not in the database")
        q = dict(row)
        before = verify(q) + outside_viewbox(q["figure_svg"])
        q["figure_svg"] = spec["figure"]()
        after = verify(q) + outside_viewbox(q["figure_svg"])
        ok = not after
        failed += not ok
        print(f"{prefix}  {spec['why']}")
        print(f"    before: {len(before)} finding(s); after: {len(after)}"
              f"  {'OK' if ok else 'STILL FAILING'}")
        for a in after:
            print(f"      ! {a}")
        record.append(dict(id=row["id"], why=spec["why"], before=before, after=after,
                           form_id=row["form_id"], key=row["correct_answer"],
                           old_svg=row["figure_svg"], new_svg=q["figure_svg"]))
        if args.apply and ok:
            con.execute("UPDATE questions SET figure_svg=? WHERE id=?",
                        (q["figure_svg"], row["id"]))

    if args.apply:
        if failed:
            con.rollback()
            raise SystemExit(f"\n{failed} figure(s) still failing — nothing written")
        con.commit()
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(json.dumps(record, indent=1, ensure_ascii=False))
        print(f"\napplied {len(record)} — manifest {MANIFEST}")
    else:
        print(f"\ndry run — {len(record)} figure(s), {failed} still failing")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
