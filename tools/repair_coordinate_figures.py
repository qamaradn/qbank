#!/usr/bin/env python3
"""Redraw every coordinate figure that disagrees with its own stem.

Round 5 flagged four of these and `plotted_geometry_matches_stem` found the rest. Per
CLAUDE.md rules 11-12: a gatable flag is a sweep, the sweep covers questions no reviewer
has reached, and fixing them is the job rather than a finding to report.

The figure is derived from the coordinates IN THE STEM and drawn by figure_lib.plane, so
the picture cannot disagree with the words. Nothing reads the old SVG: patched figures
came back every round, regenerated ones held.

WHAT IS DELIBERATELY NOT TOUCHED. A stem does not always contain the whole figure, and
regenerating from a partial reading would destroy information rather than repair it:

  * rotations, reflections and translations -- the figure shows the pre-image and the
    ANSWER is the image; drawing every coordinate in the stem would draw the answer.
  * "which point has coordinates (x, y)" -- the distractor points exist only in the old
    figure, so their positions cannot be recovered from the stem.
  * parabolas, and questions asking for a trig ratio of an angle at the origin, which
    need a curve or an angle arc that plane() does not draw.

Those are listed as SKIPPED with a reason, and stay for hand work.

Usage:
    python -m tools.repair_coordinate_figures --dry-run
    python -m tools.repair_coordinate_figures --apply
"""
import argparse
import json
import pathlib
import re
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.figure_lib import plane           # noqa: E402
from tools import question_checks as qc      # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
MANIFEST = ROOT / "run_data/output/coordinate_figure_repairs.json"

_PT = re.compile(r"(?:\b([A-Z])\s*)?\(\s*([-−]?\d+(?:\.\d+)?)\s*,\s*([-−]?\d+(?:\.\d+)?)\s*\)")
_SHAPE = re.compile(r"\b(triangle|rectangle|square|parallelogram|quadrilateral|trapez)",
                    re.I)
_LINEY = re.compile(r"\bline\b|\bsegment\b|\bpasses through\b|\bstraight path\b", re.I)

# Anything here means the stem is not the whole figure. Skipped, not guessed at.
_HANDS_OFF = [
    (re.compile(r"\brotat|\breflect|\btranslat|\bimage\b", re.I),
     "a transformation: the figure is the pre-image and the answer is the image"),
    (re.compile(r"\bwhich point\b", re.I),
     "the distractor points exist only in the old figure"),
    (re.compile(r"parabola|y\s*=\s*a?x²|x\^2", re.I),
     "a curve, which plane() does not draw"),
    (re.compile(r"\btan\b|\bsin\b|\bcos\b|angle\s+θ|\bθ\b", re.I),
     "needs an angle arc at the origin"),
    (re.compile(r"parallel to the [xy]-axis|\bline ℓ\b", re.I),
     "the line's position is not given by any stated point"),
    # Two named lines, where one is often defined only in relation to the other
    # ("Line Q is parallel to Line P and passes through (0, -1)"). The planner draws a
    # line only from a pair of points, so it silently drew THREE LOOSE DOTS for a
    # question about two lines -- a redraw strictly worse than the figure it replaced.
    # Caught by rendering, not by any check.
    (re.compile(r"\b(?:two lines|two linear relationships)\b|"
                r"\bline\s+[A-Z]\b.*\bline\s+[A-Z]\b", re.I | re.S),
     "two named lines: one is defined relative to the other"),
]


def num(t):
    return float(str(t).replace("−", "-"))


def plan(q):
    """(kwargs for plane, note) or (None, reason it was skipped)."""
    stem = q.get("stem") or ""
    for pat, why in _HANDS_OFF:
        if pat.search(stem):
            return None, why
    pts = [(n, num(x), num(y)) for n, x, y in _PT.finditer(stem)] if False else \
          [(m.group(1), num(m.group(2)), num(m.group(3))) for m in _PT.finditer(stem)]
    if len(pts) < 2:
        return None, "fewer than two coordinates in the stem"
    if len(pts) > 6:
        return None, "more coordinates than a single figure plausibly holds"
    xs = [p[1] for p in pts]
    ys = [p[2] for p in pts]
    lo_x, hi_x = min(xs), max(xs)
    lo_y, hi_y = min(ys), max(ys)
    # Always show the origin: an axis off the drawn area is what half these figures got
    # wrong in the first place.
    xr = (int(min(lo_x, 0)) - 1, int(max(hi_x, 0)) + 1)
    yr = (int(min(lo_y, 0)) - 1, int(max(hi_y, 0)) + 1)
    span = max(xr[1] - xr[0], yr[1] - yr[0])
    if span > 16:
        return None, f"the coordinates span {span} units, too wide to draw legibly"
    cell = max(20, min(30, int(268 / span)))
    named = {n: (x, y) for n, x, y in pts if n}
    kw = dict(xr=xr, yr=yr, cell=cell)
    if _SHAPE.search(stem) and len(pts) >= 3:
        kw["polygon"] = [(x, y) for _n, x, y in pts]
        kw["points"] = named or [(x, y) for _n, x, y in pts]
        kw["label_off"] = (0, -10)
        note = "polygon"
    elif _LINEY.search(stem) and len(pts) == 2:
        kw["lines"] = [((pts[0][1], pts[0][2]), (pts[1][1], pts[1][2]))]
        kw["points"] = named or [(x, y) for _n, x, y in pts]
        note = "line through two points"
    else:
        kw["points"] = named or [(x, y) for _n, x, y in pts]
        note = "plotted points"
    return kw, note


SVG_CHECKS = ["overlapping_text_labels", "text_overlaps_geometry", "axes_unlabelled",
              "angle_arc_malformed", "doubled_circle_outline", "gridlines_off_the_ticks",
              "plotted_points_inconsistent", "axis_scale_nonlinear",
              "coordinate_figure_without_grid"]


def verify(q):
    out = []
    for n in SVG_CHECKS:
        if (m := getattr(qc, n)(q["figure_svg"])):
            out.append(f"{n}: {m}")
    if (m := qc.plotted_geometry_matches_stem(q)):
        out.append(f"plotted_geometry_matches_stem: {m}")
    out += [f"figure_svg_errors: {x}" for x in (qc.figure_svg_errors(q["figure_svg"]) or [])]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not (args.apply or args.dry_run):
        raise SystemExit("pass --apply or --dry-run")

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute(
        "SELECT * FROM questions WHERE figure_svg IS NOT NULL AND figure_svg!=''")]
    targets = [r for r in rows if qc.plotted_geometry_matches_stem(r)]

    fixed, skipped, failed = [], [], []
    for r in targets:
        kw, note = plan(r)
        if kw is None:
            skipped.append((r, note))
            continue
        q = dict(r, figure_svg=plane(**kw))
        bad = verify(q)
        if bad:
            failed.append((r, note, bad))
            continue
        fixed.append((r, note, q["figure_svg"]))
        if args.apply:
            con.execute("UPDATE questions SET figure_svg=? WHERE id=?",
                        (q["figure_svg"], r["id"]))

    print(f"{len(targets)} figures disagree with their stem")
    print(f"  redrawn and verified : {len(fixed)}")
    print(f"  could not verify     : {len(failed)}")
    print(f"  deliberately skipped : {len(skipped)}")
    for r, note, bad in failed:
        print(f"    ! {r['id'][:8]} ({note}) {bad[0][:96]}")
    for r, note in skipped:
        print(f"    - {r['id'][:8]} {note}")

    if args.apply:
        con.commit()
        MANIFEST.write_text(json.dumps(
            [dict(id=r["id"], note=n, form_id=r["form_id"], status=r["review_status"],
                  old_svg=r["figure_svg"], new_svg=s) for r, n, s in fixed],
            indent=1, ensure_ascii=False))
        print(f"\napplied {len(fixed)} — manifest {MANIFEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
