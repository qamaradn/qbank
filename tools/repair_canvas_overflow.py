#!/usr/bin/env python3
"""Grow a figure's canvas so its labels are not cut off by the edge.

Question 6 of the VIC review page is the hexagon/octagon diagonals item, and both
its captions -- "Hexagon (9 diagonals)" and "Octagon (? diagonals)" -- run 8 px
past the bottom of the viewBox. A browser simply does not draw what is outside,
so the reader gets two headless captions and no way to know which polygon is
which.

WHY THIS WAS NOT DONE IN ROUND 6, and why that was a mistake. Round 6 measured 45
figures with a text box past the edge and declined to act, because `_text_box`
estimates WIDTH from a character count and runs about a quarter narrow -- at the
left or right edge it cannot tell a clipped label from a tight one. True, and it
was applied to both directions when it only holds for one. A box's VERTICAL
extent is the baseline plus the font size: no character count, no estimate, no
error. The two directions needed separating and did not get it.

So the CHECK measures top and bottom only, where it is exact. The REPAIR grows in
all four directions, generously, because adding canvas can only cost a margin.

The fix adds room rather than moving anything, so a figure cannot be made wrong
by it: the viewBox grows to contain what was already being drawn, and every
coordinate in it keeps its meaning.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_canvas_overflow --dry-run
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_canvas_overflow --apply
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
MANIFEST = ROOT / "run_data/output/canvas_overflow_repairs.json"


def grow(svg: str, pad: float = 3.0, widen: float = 1.3
         ) -> tuple[str, tuple[float, float] | None]:
    """Extend the viewBox until every label fits, plus a little.

    Sideways as well as up and down, and this is where the width estimate stops
    mattering. DETECTING a horizontal clip needs an accurate width -- too narrow an
    estimate and you miss one, too wide and you chase figures that are merely tight.
    But GROWING the canvas only ever adds empty space, so being generous costs a
    margin and never costs a label. The estimate runs about a quarter narrow, so it
    is inflated by a third here and the box is grown to whatever that says.
    "20 m" was being drawn as "2".
    """
    m = re.search(r'viewBox\s*=\s*[\'"]([^\'"]+)[\'"]', svg)
    if not m:
        return svg, None
    try:
        x0, y0, w, h = (float(v) for v in m.group(1).split())
    except ValueError:
        return svg, None
    top, bot, left, right = y0, y0 + h, x0, x0 + w
    for tm in qc._TEXT.finditer(svg):
        b = qc._text_box(tm)
        if not b:
            continue
        top = min(top, b[1] - pad)
        bot = max(bot, b[3] + pad)
        cx, half = (b[0] + b[2]) / 2, (b[2] - b[0]) / 2 * widen
        left = min(left, cx - half - pad)
        right = max(right, cx + half + pad)
    if all(abs(a - b) < 0.5 for a, b in
           ((top, y0), (bot, y0 + h), (left, x0), (right, x0 + w))):
        return svg, None
    new_h, new_w = bot - top, right - left
    out = svg.replace(m.group(0),
                      f'viewBox="{left:g} {top:g} {new_w:g} {new_h:g}"', 1)
    wm = re.search(r'<svg[^>]*\bwidth\s*=\s*[\'"]([\d.]+)[\'"]', out)
    if wm:
        out = re.sub(r'(<svg[^>]*\bwidth\s*=\s*[\'"])[\d.]+',
                     lambda z: f"{z.group(1)}{float(wm.group(1)) * new_w / w:.0f}",
                     out, 1)
    # A width/height pair on the tag fixes the aspect ratio, so it has to grow with
    # the box or the figure is squashed instead of clipped.
    hm = re.search(r'<svg[^>]*\bheight\s*=\s*[\'"]([\d.]+)[\'"]', out)
    if hm:
        scale = new_h / h if h else 1
        out = re.sub(r'(<svg[^>]*\bheight\s*=\s*[\'"])[\d.]+',
                     lambda z: f"{z.group(1)}{float(hm.group(1)) * scale:.0f}", out, 1)
    return out, (round(left - x0, 1), round(right - (x0 + w), 1),
                 round(y0 - top, 1), round(bot - (y0 + h), 1))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--tol", type=float, default=0.5,
                    help="ignore overflows smaller than this (default 0.5 px)")
    a = ap.parse_args()
    if not (a.apply or a.dry_run):
        raise SystemExit("pass --apply or --dry-run")

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute(
        "SELECT * FROM questions WHERE review_status != 'rejected' "
        "AND figure_svg IS NOT NULL AND figure_svg != ''")]
    todo = [q for q in rows if grow(q["figure_svg"])[1] is not None]
    print(f"{len(todo)} figure(s) draw a label past the top or bottom edge\n")

    record, failed = [], 0
    for q in todo:
        new, added = grow(q["figure_svg"])
        regressed = sorted(figure_state(new) - figure_state(q["figure_svg"]))
        ok = added is not None and not regressed and \
            not qc.text_outside_the_canvas(new, tol=a.tol)
        failed += not ok
        print(f"  {q['id'][:8]} {q['source_book']:<22} grew by {added}"
              f"  {'OK' if ok else 'FAILED ' + str(regressed)}")
        record.append({"id": q["id"], "book": q["source_book"],
                       "form": q["form_id"], "grew": added})
        if a.apply and ok:
            con.execute("UPDATE questions SET figure_svg=?, edited=1 WHERE id=?",
                        (new, q["id"]))

    if a.apply:
        con.commit()
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(json.dumps(record, indent=1))
        print(f"\napplied {len(record) - failed} of {len(record)} — {MANIFEST}")
    else:
        print(f"\ndry run — {len(record)} figure(s), {failed} failing")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
