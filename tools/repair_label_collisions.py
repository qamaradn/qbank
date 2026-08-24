#!/usr/bin/env python3
"""Move labels that collide with a line or with another label.

Four of the nine failures on the second VIC batch were a label printed over something.
Nudging by hand is fiddly and gets re-flagged when the first guess is still too close --
the P(4, 4) label took three attempts, because it sat at the intersection of two lines
and every diagonal offset landed on one of them.

So: try candidate offsets outward from the anchor, in growing rings, and keep the first
that clears every line and every other label. The figure is re-checked afterwards, so a
nudge that fixes one collision and causes another cannot be applied.
"""
import argparse
import json
import pathlib
import re
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import question_checks as qc  # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
RECORD = ROOT / "run_data/output/label_collision_repairs.json"

_TEXT_TAG = re.compile(r"<text\b[^>]*>[^<]*</text>")
_XY = re.compile(r"\bx=([\'\"])([-\d.]+)\1|\by=([\'\"])([-\d.]+)\1")

# outward first, then further; sideways before diagonal, since a diagonal offset near a
# diagonal line tends to stay on it
OFFSETS = [(0, dy) for dy in (16, -14, 24, -22, 32, -30)] + \
          [(dx, 0) for dx in (18, -18, 28, -28, 40, -40)] + \
          [(dx, dy) for d in (20, 30, 42) for dx in (d, -d) for dy in (d, -d)]


def _shift(tag, dx, dy):
    def rep(m):
        if m.group(2) is not None:
            return f"x={m.group(1)}{float(m.group(2)) + dx:g}{m.group(1)}"
        return f"y={m.group(3)}{float(m.group(4)) + dy:g}{m.group(3)}"
    return _XY.sub(rep, tag, count=2)


def clashes(svg):
    return (qc.text_overlaps_geometry(svg), qc.overlapping_text_labels(svg))


def repair(svg, tries=6):
    """Nudge one label at a time until the figure is clean, or give up honestly."""
    moved = []
    for _ in range(tries):
        geo, lab = clashes(svg)
        if not geo and not lab:
            return svg, moved
        msg = geo or lab
        m = re.search(r"labels? '([^']+)'", msg)
        if not m:
            return svg, moved
        target = m.group(1)
        tag = next((t for t in _TEXT_TAG.findall(svg)
                    if (re.search(r">([^<]*)<", t) or [""]) and
                    re.search(r">([^<]*)<", t).group(1).strip() == target), None)
        if tag is None:
            return svg, moved
        for dx, dy in OFFSETS:
            cand = svg.replace(tag, _shift(tag, dx, dy), 1)
            g2, l2 = clashes(cand)
            if not g2 and not l2:
                return cand, moved + [(target, dx, dy)]
        # nothing clears everything; take the best partial and continue
        best = None
        for dx, dy in OFFSETS:
            cand = svg.replace(tag, _shift(tag, dx, dy), 1)
            g2, l2 = clashes(cand)
            score = (g2 is not None) + (l2 is not None)
            if best is None or score < best[0]:
                best = (score, cand, (target, dx, dy))
        if best is None or best[0] >= (geo is not None) + (lab is not None):
            return svg, moved
        svg = best[1]
        moved.append(best[2])
    return svg, moved


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--forms", required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    forms = [f.strip() for f in args.forms.split(",") if f.strip()]
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute(
        f"SELECT * FROM questions WHERE form_id IN ({','.join('?' * len(forms))}) "
        f"AND review_status!='rejected' AND figure_svg IS NOT NULL", forms)]
    record = []
    for r in rows:
        if not any(clashes(r["figure_svg"])):
            continue
        fixed, moved = repair(r["figure_svg"])
        left = [m for m in clashes(fixed) if m]
        tag = "clean" if not left else f"STILL: {left[0][:58]}"
        print(f"  [{r['form_id']} pos {r['form_position']}] "
              + ", ".join(f"{l!r} by ({dx:+g},{dy:+g})" for l, dx, dy in moved)
              + f"  -> {tag}")
        if moved and args.apply:
            con.execute("UPDATE questions SET figure_svg=?, edited=1 WHERE id=?",
                        (fixed, r["id"]))
            record.append({"id": r["id"], "form_id": r["form_id"],
                           "moved": [[l, dx, dy] for l, dx, dy in moved]})
    if args.apply and record:
        prior = json.loads(RECORD.read_text()) if RECORD.exists() else []
        RECORD.write_text(json.dumps(prior + record, indent=2) + "\n")
        con.commit()
        print(f"\nmoved labels in {len(record)} figure(s)")
    else:
        print(f"\n{len(record)} figure(s) would change (dry run)")


if __name__ == "__main__":
    main()
