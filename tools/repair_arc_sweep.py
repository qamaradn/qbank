#!/usr/bin/env python3
"""Redraw angle arcs that sweep past the angle they mark.

Five reviewer notes in one pass, all the same sentence in different words: "the angle
arc of 47 is slipping outside the triangle, fix it", "the angle 34 slips out the
triangle", "The angle 52 degrees line slips out the triangle", "Angle arc doesn't
complete the P angle", "Finish the angle arc."

The cause is that the arc was PLACED rather than derived: a radius chosen and a sweep
guessed, so it leaves the base correctly and finishes several degrees past the
hypotenuse, hanging outside the shape. Round 6 established the answer for arcs that
were MISSING -- read the figure's own segments, find the rays at the vertex, draw
between the two that bound the sector the label sits in, so an arc cannot land on an
angle other than the one named. This applies the same derivation to arcs that are
present and wrong.

The radius is taken from the shorter of the two rays, not from the old arc, because
an arc wider than the side it is drawn against is the other half of the same
complaint.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_arc_sweep
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_arc_sweep --apply
"""
import argparse
import json
import math
import pathlib
import re
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import figure_lib as fl                 # noqa: E402
from tools import question_checks as qc            # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
RECORD = ROOT / "run_data/output/arc_sweep_repairs.json"

FIG_CHECKS = ("doubled_circle_outline", "overlapping_text_labels",
              "plotted_points_inconsistent", "text_overlaps_geometry",
              "axes_unlabelled", "angle_arc_malformed", "axis_scale_nonlinear",
              "coordinate_figure_without_grid", "gridlines_off_the_ticks",
              "unknown_marker_far_from_point", "label_too_faint",
              "undefined_marker_reference", "text_outside_the_canvas",
              "gridlines_stop_short_of_the_axes", "axis_shorter_than_the_data",
              "angle_arc_misses_its_rays", "figure_svg_errors")
Q_CHECKS = ("angle_named_without_arc", "polygon_sides_disagree_with_stem",
            "figure_proportions_disagree", "plotted_geometry_matches_stem")

_ARC_TAG = re.compile(r"<path[^>]*\bd=[\'\"]\s*M[^\'\"]*[Aa][^\'\"]*[\'\"][^>]*>")


def state(q, svg):
    row = dict(q)
    row["figure_svg"] = svg
    out = set()
    for n in FIG_CHECKS:
        got = getattr(qc, n)(svg)
        if got:
            out.add(n)
    for n in Q_CHECKS:
        if getattr(qc, n)(row):
            out.add(n)
    return out


def _label_near(svg, vertex, reach=70.0):
    """The angle's name, if one is printed near this vertex.

    `angle_mark` needs it: a square is drawn only where the label says 90, because the
    convention carries information and a square on a 70° corner hands out a wrong
    answer.
    """
    best, bestd = "", 1e9
    for m in qc._TEXT.finditer(svg):
        b = qc._text_box(m)
        if not b:
            continue
        cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        d = math.dist((cx, cy), vertex)
        if d < bestd and d < reach and re.search(r"[\d°a-zA-Zθαβφ]", b[4]):
            best, bestd = b[4], d
    return best


def redraw(svg):
    """(new_svg, notes) or (None, why-not)."""
    segs = fl.figure_outlines(svg)
    if not segs:
        return None, "nothing drawn"
    notes, skipped = [], []
    out = svg
    for tag in _ARC_TAG.findall(svg):
        m = qc._ARC_PATH.search(tag)
        if not m:
            continue
        x1, y1, rx, ry, large, sweep, x2, y2 = (float(g) for g in m.groups())
        if rx <= 0 or abs(rx - ry) > 0.6 or rx > 90:
            continue
        v = qc._arc_centre(x1, y1, x2, y2, rx, int(large), int(sweep))
        if v is None:
            continue
        rays = fl._rays_at(segs, v, eps=3.0)
        if len(rays) < 2:
            continue
        a1 = math.atan2(y1 - v[1], x1 - v[0])
        a2 = math.atan2(y2 - v[1], x2 - v[0])
        mid = a1 + ((a2 - a1) % (2 * math.pi)) / 2
        # The sector the old arc sits in, bounded by the rays either side of its own
        # midpoint. Taking the nearest ray to each END would follow the arc's mistake.
        angs = sorted(a for a, _l in rays)
        lo = hi = None
        for i, a in enumerate(angs):
            nxt = angs[(i + 1) % len(angs)]
            span = (nxt - a) % (2 * math.pi)
            if (mid - a) % (2 * math.pi) <= span + 1e-9:
                lo, hi = a, nxt
                break
        if lo is None:
            continue
        was = (a2 - a1) % (2 * math.pi)
        now = (hi - lo) % (2 * math.pi)
        if abs(now - was) < math.radians(2):
            continue                                  # already correct
        # ONLY WHERE THE OLD ARC WAS ROUGHLY RIGHT AND OVERSHOT. At a crossing there
        # are four sectors, and taking the one the old arc's MIDPOINT falls in follows
        # the old arc's own mistake when it spans across a ray: two vertical angles
        # labelled 35° each came back derived as 120°, and a 50° exterior angle as
        # 107°. Where the derived sector is nothing like the drawn one, which of the
        # four is meant is a judgement, not a measurement -- refuse it and list it.
        if not 0.5 <= now / was <= 1.6:
            skipped.append({"vertex": [round(v[0], 1), round(v[1], 1)],
                            "was_deg": round(math.degrees(was), 1),
                            "derived_deg": round(math.degrees(now), 1),
                            "why": "derived sector is nothing like the drawn one — "
                                   "which of the sectors at this vertex is meant "
                                   "needs a human"})
            continue
        length = min(l for a, l in rays if abs(a - lo) < 1e-9 or abs(a - hi) < 1e-9)
        r = max(12.0, min(rx, 0.42 * length))
        mark = fl.angle_mark(v, lo, hi, r, label=_label_near(svg, v))
        if not mark:
            continue
        out = out.replace(tag, mark, 1)
        notes.append({"vertex": [round(v[0], 1), round(v[1], 1)],
                      "was_deg": round(math.degrees((a2 - a1) % (2 * math.pi)), 1),
                      "now_deg": round(math.degrees((hi - lo) % (2 * math.pi)), 1),
                      "radius": round(r, 1)})
    if not notes:
        return None, (skipped or "no arc could be re-derived from the figure's own "
                                 "segments")
    return out, {"redrawn": notes, "left_for_a_human": skipped}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dump", type=pathlib.Path)
    args = ap.parse_args()
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute(
        "SELECT * FROM questions WHERE figure_svg IS NOT NULL AND figure_svg != '' "
        "AND review_status != 'rejected'")]
    done, refused, dump = [], [], []
    for q in rows:
        if not qc.angle_arc_misses_its_rays(q["figure_svg"]):
            continue
        before = state(q, q["figure_svg"])
        new, notes = redraw(q["figure_svg"])
        if not new:
            refused.append({"id": q["id"], "why": notes})
            continue
        after = state(q, new)
        gained = after - before
        if gained:
            refused.append({"id": q["id"], "newly_firing": sorted(gained)})
            continue
        done.append({"id": q["id"], "form": q["form_id"], **notes,
                     "cleared": sorted(before - after), "left": sorted(after)})
        dump.append({"id": q["id"][:8] + "-BEFORE", "figure_svg": q["figure_svg"],
                     "stem": q["stem"]})
        dump.append({"id": q["id"][:8] + "-AFTER", "figure_svg": new, "stem": q["stem"]})
        if args.apply:
            con.execute("UPDATE questions SET figure_svg = ?, edited = 1 WHERE id = ?",
                        (new, q["id"]))
    if args.apply:
        con.commit()
    if args.dump:
        args.dump.write_text(json.dumps(dump))
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps({"applied": args.apply, "redrawn": done,
                                  "refused": refused}, indent=1))
    print(f"{len(done)} redrawn, {len(refused)} refused"
          f"{'' if args.apply else '  (dry run — pass --apply)'}")
    for r in refused:
        print("   refused", r["id"][:8], r.get("newly_firing") or r["why"])
    for d in done:
        if d["left"]:
            print("   still flagged", d["id"][:8], d["left"])
    print(f"record -> {RECORD}")


if __name__ == "__main__":
    main()
