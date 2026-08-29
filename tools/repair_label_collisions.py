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
# The y alternative used to close on \1 -- the QUOTE group of the x alternative, which
# never participates when the y branch is taken, so the backreference could not match
# and y= was never found. Every vertical offset in OFFSETS was therefore a silent
# no-op, and this tool has only ever been able to move a label sideways. It is why the
# P(4, 4) label "took three attempts" in round 2, and why three labels here looked
# unfixable. Each alternative must close on its own group.
_XY = re.compile(r"\bx=([\'\"])([-\d.]+)\1|\by=([\'\"])([-\d.]+)\3")

# outward first, then further; sideways before diagonal, since a diagonal offset near a
# diagonal line tends to stay on it
OFFSETS = [(0, dy) for dy in (16, -14, 24, -22, 32, -30, 44, -42)] + \
          [(dx, 0) for dx in (18, -18, 28, -28, 40, -40, 54, -54)] + \
          [(dx, dy) for d in (20, 30, 42, 56) for dx in (d, -d) for dy in (d, -d)]


def _shift(tag, dx, dy):
    def rep(m):
        if m.group(2) is not None:
            return f"x={m.group(1)}{float(m.group(2)) + dx:g}{m.group(1)}"
        return f"y={m.group(3)}{float(m.group(4)) + dy:g}{m.group(3)}"
    return _XY.sub(rep, tag, count=2)


def _tick_axes(svg):
    """(x-axis tick texts, y-axis tick texts) as they are printed.

    An x-axis tick shares a row with the other x ticks and may only move in y; a
    y-axis tick shares a column and may only move in x.
    """
    xs, ys = qc._axis_ticks(svg)
    fmt = lambda v: (f"{v:g}").replace("-", "")
    return ({fmt(v) for v, _p in xs}, {fmt(v) for v, _p in ys})


def _allowed(target, xt, yt):
    """Which offsets this label may use."""
    bare = target.replace("\u2212", "-").lstrip("-")
    if bare in xt:                       # an x-axis tick: across the x-axis only
        return [(0, dy) for dy in (16, -14, 24, -22, 32, -30, 44, -42)]
    if bare in yt:                       # a y-axis tick: across the y-axis only
        return [(dx, 0) for dx in (18, -18, 28, -28, 40, -40, 54, -54)]
    return OFFSETS


def clashes(svg):
    return (qc.text_overlaps_geometry(svg), qc.overlapping_text_labels(svg))


# Round 5's rule, which this tool never had: re-run the checks on your own output and
# roll back anything that comes back worse. Moving a label cannot fix a collision at
# the cost of a scale, a grid or a plotted point.
GUARD = ("axis_scale_nonlinear", "gridlines_off_the_ticks", "axes_unlabelled",
         "plotted_points_inconsistent", "coordinate_figure_without_grid",
         "angle_arc_malformed", "doubled_circle_outline")


def guard_state(svg):
    return {n for n in GUARD if getattr(qc, n)(svg)}


def repair(svg, tries=8):
    """Nudge one label at a time until the figure is clean, or give up honestly."""
    moved = []
    seen = set()
    for _ in range(tries):
        geo, lab = clashes(svg)
        if not geo and not lab:
            return svg, moved
        msg = geo or lab
        # Every quoted name in the message. "labels 'A' and 'B' overlap" names TWO,
        # and a pattern anchored on the word "label" saw only the first -- so the
        # only candidate ever tried was the one it happened to mention first, which
        # for an axis tick is the one that must not move.
        names = re.findall(r"'([^']+)'", msg)
        if not names:
            return svg, moved
        # An AXIS TICK may not move: it names the mark it sits against, and shifting
        # it is how a figure comes to disagree with its own scale. So when two labels
        # collide, move the annotation. Moving the tick was why "-5" and "P" stayed
        # stuck -- every offset tried was applied to the "-5".
        def is_tick(t):
            return bool(re.fullmatch(r"-?−?\d+(?:\.\d+)?", t.replace("−", "-")))
        # A tick may move ACROSS its own axis but never ALONG it. Sliding a number
        # away from the mark it names is a measurement change -- three figures came
        # back reading as nonlinear axes when the fallback did exactly that. Moving
        # it to the other side of the axis line keeps it level with its own mark, so
        # the scale is untouched, and it is what unsticks the commonest collision in
        # the bank: the x-axis "-1" and the y-axis "-1" meeting in the same corner
        # of the origin, where BOTH are ticks and neither could move at all.
        xt, yt = _tick_axes(svg)
        annotations = [t for t in names if not is_tick(t)]
        names = annotations + [t for t in names if is_tick(t)]
        # A label is often drawn TWICE at one spot: a thick white stroke behind, the
        # real glyphs on top, so it stays readable over a gridline. Moving one of the
        # pair leaves the other where it was and the collision survives every offset
        # -- which is why all three of these looked unfixable. Move the whole group.
        groups = []
        for target in names:
            byxy = {}
            for t in _TEXT_TAG.findall(svg):
                body = re.search(r">([^<]*)<", t)
                if not body or body.group(1).strip() != target:
                    continue
                xy = tuple(m.group(2) or m.group(4) for m in _XY.finditer(t))
                byxy.setdefault(xy, []).append(t)
            for tags in byxy.values():
                groups.append((target, tags))
        if not groups:
            return svg, moved

        def shift_group(s, tags, dx, dy):
            for t in tags:
                s = s.replace(t, _shift(t, dx, dy), 1)
            return s

        for target, tags in groups:
            for dx, dy in _allowed(target, xt, yt):
                cand = shift_group(svg, tags, dx, dy)
                g2, l2 = clashes(cand)
                if not g2 and not l2:
                    return cand, moved + [(target, dx, dy)]
        target, tags = groups[0]
        # nothing clears everything; take the best partial and continue
        best = None
        for dx, dy in _allowed(target, xt, yt):
            cand = shift_group(svg, tags, dx, dy)
            g2, l2 = clashes(cand)
            score = (g2 is not None) + (l2 is not None)
            if best is None or score < best[0]:
                best = (score, cand, (target, dx, dy))
        # Accept a move that does not lower the count but UNCOVERS a different
        # collision -- moving P off the "-5" revealed a "-1"/"-1" pair underneath, and
        # refusing an equal score meant neither ever got fixed. `seen` stops it
        # cycling between two states forever.
        if best is None:
            return svg, moved
        after = tuple(x for x in clashes(best[1]) if x)
        if best[0] > (geo is not None) + (lab is not None) or after in seen:
            return svg, moved
        seen.add(after)
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
        regressed = sorted(guard_state(fixed) - guard_state(r["figure_svg"]))
        if regressed:
            print(f"  [{r['form_id']} pos {r['form_position']}] ROLLED BACK — "
                  f"the move would have caused {regressed}")
            continue
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
