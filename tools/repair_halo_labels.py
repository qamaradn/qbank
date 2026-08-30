#!/usr/bin/env python3
"""Put a halo behind a label that a gridline runs through.

"Why are there thin grid lines behind the numbers?" A four-quadrant plane and a bar
chart both print labels inside the plot area, and a grid runs under them by
construction. Moving the label is the wrong answer -- it belongs where it is, against
the mark or the bar it names -- and so is dropping the grid, which is there because a
reviewer asked for it eleven times in the same pass.

What a real graph does is print the label twice: a page-coloured stroke behind, the
glyphs on top. `figure_lib.plane` does it for everything it draws; this does it for
figures already in the bank.

WHY THIS SWEEPS (rule 11c). It is additive in the strict sense the rule means: a layer
is added behind the text, nothing moves, no coordinate changes, and removing the layer
restores the figure byte for byte. It applies ONLY where the ink under the label is
faint -- watermark-opacity grid -- because a halo behind a solid line is a cover-up
rather than a fix, and that case is left to `repair_label_collisions` and to a human.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_halo_labels
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_halo_labels --apply
"""
import argparse
import json
import pathlib
import re
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import figure_lib as fl                 # noqa: E402
from tools import question_checks as qc            # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
RECORD = ROOT / "run_data/output/halo_repairs.json"

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

_TEXT_TAG = re.compile(r"<text\b[^>]*>[^<]*</text>")


def state(q, svg):
    row = dict(q)
    row["figure_svg"] = svg
    return ({n for n in FIG_CHECKS if getattr(qc, n)(svg)}
            | {n for n in Q_CHECKS if getattr(qc, n)(row)})


def halo(svg):
    """(new_svg, labels) or (None, why-not)."""
    faint = {(tuple(a), tuple(b))
             for a, b in fl.figure_outlines(qc._faint_only(svg))}
    if not faint:
        return None, "nothing faint under anything"
    solid = [s for s in fl.figure_outlines(svg)
             if (tuple(s[0]), tuple(s[1])) not in faint]
    already = qc._haloed_labels(svg)
    want = []
    for m in _TEXT_TAG.finditer(svg):
        tm = qc._TEXT.search(m.group(0))
        if not tm:
            continue
        b = qc._text_box(tm)
        if not b or not b[4] or b[4] in already:
            continue
        box = b[:4]
        on_faint = any(qc._seg_hits_box(a, c, d, e, *box)
                       for (a, c), (d, e) in faint)
        # Only where the ONLY thing under the label is faint. A halo over a solid
        # line hides a real collision instead of fixing it.
        on_solid = any(qc._seg_hits_box(a, c, d, e, *box)
                       for (a, c), (d, e) in solid)
        if on_faint and not on_solid:
            want.append((m.group(0), b[4]))
    if not want:
        return None, "no label sits on faint ink alone"
    layer = "".join(t for t, _n in want)
    # The stroke is the PAGE colour, which currentColor cannot be -- currentColor IS
    # the ink. A variable so a dark card can set it, white as the fallback the review
    # card and Selectly both use.
    layer = (f'<g stroke="#fff" stroke-width="3" '
             f'stroke-linejoin="round" fill="none" aria-hidden="true">{layer}</g>')
    # Behind the text it duplicates but in front of the grid: inserting it directly
    # before the first of the labels does both.
    first = want[0][0]
    at = svg.index(first)
    return svg[:at] + layer + svg[at:], [n for _t, n in want]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--scope", default="all")
    ap.add_argument("--dump", type=pathlib.Path)
    args = ap.parse_args()
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute(
        "SELECT * FROM questions WHERE figure_svg IS NOT NULL AND figure_svg != '' "
        "AND review_status != 'rejected'")]
    done, refused, dump = [], [], []
    for q in rows:
        if not qc.text_overlaps_geometry(q["figure_svg"]):
            continue
        before = state(q, q["figure_svg"])
        new, why = halo(q["figure_svg"])
        if not new:
            continue
        after = state(q, new)
        gained = after - before
        if gained:
            refused.append({"id": q["id"], "newly_firing": sorted(gained)})
            continue
        done.append({"id": q["id"], "form": q["form_id"], "labels": why,
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
    RECORD.write_text(json.dumps({"applied": args.apply, "haloed": done,
                                  "refused": refused}, indent=1))
    print(f"{len(done)} haloed, {len(refused)} refused"
          f"{'' if args.apply else '  (dry run — pass --apply)'}")
    print(f"   {sum(1 for d in done if not d['left'])} of them now clean")
    print(f"record -> {RECORD}")


if __name__ == "__main__":
    main()
