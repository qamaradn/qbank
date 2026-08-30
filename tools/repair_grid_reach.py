#!/usr/bin/env python3
"""Extend a floating grid until it meets the axes it is drawn against.

Twelve separate reviewer notes in one pass, all the same sentence: "Why do the grid
lines stop before touching the axes?", "The grid lines don't reach the axes",
"Grid lines don't reach the axes end". No check saw any of them, because every figure
check in the suite measured labels and none measured the grid.

The cause is arithmetic, not drawing. The grid is laid out from the FIRST TICK rather
than from the ORIGIN, so it begins one whole interval in on both axes and hangs in the
middle of the plot with a gutter down two sides. A reader tracing a gridline back to
the axis to read a value finds it stops before it gets there.

WHY THIS IS SAFE TO SWEEP (rule 11c). Lengthening a line is additive: the grid gains
the segment between its old end and the axis and loses nothing, no coordinate that
carries meaning moves, and no label is touched. It is the same shape of repair as
growing a canvas, which ran over 128 figures with nothing broken. It still re-runs the
full check set on its own output and rolls the figure back if anything new fires.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_grid_reach
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_grid_reach --apply
"""
import argparse
import json
import pathlib
import re
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import question_checks as qc          # noqa: E402
from tools import figure_lib as fl               # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
RECORD = ROOT / "run_data/output/grid_reach_repairs.json"

# Every figure check there is. A repair that clears one and lights another is not a
# repair, and the only way to know is to run the whole set before and after.
ALL_FIG = [n for n in dir(qc) if not n.startswith("_") and n in {
    "doubled_circle_outline", "overlapping_text_labels", "plotted_points_inconsistent",
    "text_overlaps_geometry", "axes_unlabelled", "angle_arc_malformed",
    "axis_scale_nonlinear", "coordinate_figure_without_grid", "gridlines_off_the_ticks",
    "unknown_marker_far_from_point", "label_too_faint", "undefined_marker_reference",
    "text_outside_the_canvas", "gridlines_stop_short_of_the_axes",
    "axis_shorter_than_the_data"}]


def fig_state(svg):
    return {n for n in ALL_FIG if getattr(qc, n)(svg)}


# The WHOLE tag, not just up to the d attribute: stroke-opacity is usually written
# after d, and matching only as far as d meant `_is_faint` never saw it and every
# grid path in the bank read as solid.
_PATH = re.compile(r"<path\b[^>]*?\bd=([\'\"])([^\'\"]+)\1[^>]*>")
_LINE = re.compile(r"<line\b[^>]*>")


def _is_faint(tag):
    m = re.search(r"stroke-opacity=[\'\"]([\d.]+)", tag)
    if m and float(m.group(1)) <= 0.35:
        return True
    c = re.search(r"stroke=[\'\"]([^\'\"]+)", tag)
    return bool(c and re.fullmatch(r"#(?:[cdef]{3}|(?:[c-f][0-9a-f]){3})",
                                   c.group(1).strip().lower()))


def _stretch_d(d, yaxis_x, xaxis_y):
    """Rewrite a grid path so every run reaches its axis.

    The paths these figures use are the simple kind a generator emits --
    `M80 70V160M110 70V160M80 70H200` -- so each run is one M followed by one V or H.
    Anything richer is left alone rather than guessed at.
    """
    out, changed = [], False
    for m in re.finditer(r"M\s*(-?[\d.]+)[ ,]+(-?[\d.]+)\s*([VH])\s*(-?[\d.]+)", d):
        x, y, cmd, v = float(m.group(1)), float(m.group(2)), m.group(3), float(m.group(4))
        if cmd == "V":                     # a vertical gridline: reach DOWN to the x-axis
            lo, hi = min(y, v), max(y, v)
            if xaxis_y > hi:
                hi, changed = xaxis_y, True
            out.append(f"M{x:g} {lo:g}V{hi:g}")
        else:                              # a horizontal gridline: reach LEFT to the y-axis
            lo, hi = min(x, v), max(x, v)
            if yaxis_x < lo:
                lo, changed = yaxis_x, True
            out.append(f"M{lo:g} {y:g}H{hi:g}")
    if not changed:
        return None
    # every run has to have been recognised, or the rewrite would DROP the rest
    if len(re.findall(r"[MLHVACQZmlhvacqz]", d)) != 2 * len(out):
        return None
    return "".join(out)


def repair(svg):
    """(new_svg, note) or (None, why-not)."""
    got = qc._grid_and_axes(svg)
    if not got:
        return None, "no faint grid beside solid axes"
    _faint, xaxis_y, yaxis_x = got
    new = svg
    touched = 0
    for m in list(_PATH.finditer(svg)):
        whole = m.group(0)
        if not _is_faint(whole):
            continue
        d2 = _stretch_d(m.group(2), yaxis_x, xaxis_y)
        if d2:
            q = m.group(1)
            new = new.replace(whole, whole.replace(f"d={q}{m.group(2)}{q}",
                                                   f"d={q}{d2}{q}", 1), 1)
            touched += 1
    for tag in _LINE.findall(svg):
        if not _is_faint(tag):
            continue
        a = dict(fl._ATTR.findall(tag))
        try:
            x1, y1, x2, y2 = (float(a[k]) for k in ("x1", "y1", "x2", "y2"))
        except (KeyError, ValueError):
            continue
        t = tag
        if abs(x1 - x2) < 1 and max(y1, y2) < xaxis_y - 1:      # vertical, short of x-axis
            k = "y1" if y1 > y2 else "y2"
            t = re.sub(rf"\b{k}=([\'\"])[-\d.]+\1", f'{k}="{xaxis_y:g}"', t, count=1)
        if abs(y1 - y2) < 1 and min(x1, x2) > yaxis_x + 1:      # horizontal, short of y-axis
            k = "x1" if x1 < x2 else "x2"
            t = re.sub(rf"\b{k}=([\'\"])[-\d.]+\1", f'{k}="{yaxis_x:g}"', t, count=1)
        if t != tag:
            new = new.replace(tag, t, 1)
            touched += 1
    if not touched:
        return None, "grid already reaches, or is drawn in a form this cannot rewrite"
    return new, f"{touched} grid element(s) extended to the axes"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--ids", help="comma-separated id prefixes; default every hit")
    args = ap.parse_args()

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute(
        "SELECT id, source_book, form_id, figure_svg FROM questions "
        "WHERE figure_svg IS NOT NULL AND figure_svg != '' "
        "AND review_status != 'rejected'")]
    if args.ids:
        want = tuple(s.strip() for s in args.ids.split(","))
        rows = [r for r in rows if r["id"].startswith(want)]

    done, declined, rolled = [], [], []
    for r in rows:
        svg = r["figure_svg"]
        if not qc.gridlines_stop_short_of_the_axes(svg):
            continue
        before = fig_state(svg)
        new, note = repair(svg)
        if not new:
            declined.append({"id": r["id"], "why": note})
            continue
        after = fig_state(new)
        gained = after - before
        if gained:
            rolled.append({"id": r["id"], "newly_firing": sorted(gained)})
            continue
        done.append({"id": r["id"], "book": r["source_book"], "form": r["form_id"],
                     "note": note, "cleared": sorted(before - after)})
        if args.apply:
            con.execute("UPDATE questions SET figure_svg = ? WHERE id = ?",
                        (new, r["id"]))
    if args.apply:
        con.commit()
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps(
        {"applied": args.apply, "repaired": done, "declined": declined,
         "rolled_back": rolled}, indent=1))
    print(f"{len(done)} repaired, {len(declined)} declined, {len(rolled)} rolled back"
          f"{'' if args.apply else '  (dry run — pass --apply)'}")
    for d in declined + rolled:
        print("   declined", d["id"][:8], d.get("why") or d.get("newly_firing"))
    print(f"record -> {RECORD}")


if __name__ == "__main__":
    main()
