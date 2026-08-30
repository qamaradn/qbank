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

from tools import figure_lib as fl  # noqa: E402
from tools.repair_canvas_overflow import grow  # noqa: E402
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
    """Where each axis's tick labels sit: (the x-row's y, the y-column's x).

    Deciding by TEXT was wrong. A symmetric plane prints "5" on both axes, so the
    same string is an x-tick and a y-tick, and whichever test ran first won -- which
    let a y-axis "-5" be moved DOWNWARD, along its own axis, turning a linear scale
    into one that advances at 24 px per unit in one place and 40 in another. A tick
    belongs to the axis whose row or column it actually sits in.
    """
    xps = [p for _v, p in qc._axis_ticks(svg)[0]]
    yps = [p for _v, p in qc._axis_ticks(svg)[1]]
    # A CATEGORY LABEL IS A TICK TOO. `_axis_ticks` only reads NUMBERS, so on a chart
    # whose x-axis reads "9am 10am 11am 12pm 1pm" or "Mon Tue Wed Thu" none of them
    # counted, the tool was free to move them anywhere, and its first offset -- down --
    # dropped the leftmost one out of the row its four neighbours are in. Eight NSW
    # charts came back with a category label on a line of its own.
    #
    # What makes something a tick is that it is one of a ROW or a COLUMN of labels at
    # one size. Find those the same way, by their shared coordinate.
    rows, cols = {}, {}
    for m in qc._TEXT.finditer(svg):
        b = qc._text_box(m)
        if not b:
            continue
        cx = (b[0] + b[2]) / 2
        rows.setdefault(round(b[1] / 3), []).append(cx)
        cols.setdefault(round(cx / 3), []).append(b[1])
    for _k, v in rows.items():
        if len(v) >= 3:
            xps += v
    for _k, v in cols.items():
        if len(v) >= 3:
            yps += v
    return (xps, yps)


def _allowed(tag, xps, yps):
    """Which offsets this label may use, decided by WHERE it is.

    An x-axis tick shares its column with one of the x tick positions and may only
    move across the axis, in y; a y-axis tick shares its row and may only move in x.
    """
    mx = re.search(r"\bx=['\"]([-\d.]+)", tag)
    my = re.search(r"\by=['\"]([-\d.]+)", tag)
    if not (mx and my):
        return OFFSETS
    x, y = float(mx.group(1)), float(my.group(1))
    # A TICK MOVES A LITTLE OR NOT AT ALL. Crossing its own axis keeps it level with
    # the mark it names, so the scale is safe -- but only for as far as it takes to
    # clear the line. Given the full ring, the nudger sent an x-axis "0" forty-four
    # pixels down the page, where it sat a whole unit below the origin it names and
    # read as a stray number. A tick that cannot be freed within one label-height of
    # its axis is one a human should look at, not one to fling.
    if any(abs(x - p) <= 3 for p in xps):
        return [(0, dy) for dy in (16, -14, 22, -20)]
    if any(abs(y - p) <= 5 for p in yps):
        return [(dx, 0) for dx in (18, -18, 26, -26)]
    return OFFSETS


def _clearance(svg, tags):
    """Smallest gap between the moved label's box and any ink in the figure.

    THE OFFSET RING IS BLIND. It returns the FIRST offset that stops the boxes
    intersecting, and (0, +16) is first in the list -- so the commonest outcome was a
    label pushed sixteen pixels DOWN onto whatever was underneath it. A "10 cm"
    dimension sitting between its bracket and the shape's top edge moved off the
    bracket and onto the edge; an x-axis "−1" moved off its tick and onto the axis.
    Both cleared the check and both read worse.

    So: among the offsets that clear, take the one that leaves the label in the most
    open space, and refuse to move at all if the best of them is no better than where
    the label already sits.
    """
    boxes = []
    for t in tags:
        m = qc._TEXT.search(t)
        if m:
            b = qc._text_box(m)
            if b:
                boxes.append(b[:4])
    if not boxes:
        return 0.0
    segs = fl.figure_outlines(svg)
    best = 1e9
    for x0, y0, x1, y1 in boxes:
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        hw, hh = (x1 - x0) / 2, (y1 - y0) / 2
        for (a, b), (c, d) in segs:
            for t in range(9):
                px = a + (c - a) * t / 8
                py = b + (d - b) * t / 8
                best = min(best, max(abs(px - cx) - hw, abs(py - cy) - hh))
    return best


def _sector_map(svg):
    """{label text: the vertex whose sector it sits in} for every angle-ish label.

    `figure_lib.angle_at_label` returns None -- needs a human -- when a label is not
    inside exactly one sector, so a label that moves from a sector to nowhere shows up
    here as a vertex that disappears.
    """
    out = {}
    for m in qc._TEXT.finditer(svg):
        b = qc._text_box(m)
        if not b or "\u00b0" not in b[4] and "&#176;" not in (m.group(4) or ""):
            continue
        got = fl.angle_at_label(svg, b)
        out[b[4]] = None if not got else (round(got[0][0], 1), round(got[0][1], 1))
    return out


def _normal_offsets(svg, tag, step=4.0, reach=40.0):
    """Offsets that push a label straight off the side it is printed on.

    THE RING IS BLIND and it runs out. It tries fixed offsets outward from the anchor
    in growing rings, which frees a label sitting near a line and cannot free one
    printed ALONG a line -- most of the ring's candidates slide along the same side and
    stay on it. That is the shape of the commonest complaint in the whole review:
    "Number/text overlapping with sides", thirty-six times, on dimension labels lying
    against the edge they measure.

    A dimension label belongs on the OUTWARD normal of its own side, which is the
    convention `figure_lib.right_triangle` is built on. Work out which segment the
    label is on, take that segment's normal, and point it away from the figure's own
    centre of ink -- then walk out along it.
    """
    m = qc._TEXT.search(tag)
    if not m:
        return []
    box = qc._text_box(m)
    if not box:
        return []
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    segs = fl.figure_outlines(svg)
    if not segs:
        return []
    hit = [sg for sg in segs if qc._seg_hits_box(sg[0][0], sg[0][1], sg[1][0],
                                                 sg[1][1], *box[:4])]
    if not hit:
        return []
    pts = [p for sg in segs for p in sg]
    gx = sum(p[0] for p in pts) / len(pts)
    gy = sum(p[1] for p in pts) / len(pts)
    out = []
    for (a, b), (c, d) in hit:
        vx, vy = c - a, d - b
        n = max((vx * vx + vy * vy) ** 0.5, 1e-9)
        nx, ny = -vy / n, vx / n
        if (cx - gx) * nx + (cy - gy) * ny < 0:          # point away from the ink
            nx, ny = -nx, -ny
        k = step
        while k <= reach:
            out.append((round(nx * k), round(ny * k)))
            k += step
    # nearest first, and never a no-op
    seen, ordered = set(), []
    for o in sorted(out, key=lambda t: abs(t[0]) + abs(t[1])):
        if o != (0, 0) and o not in seen:
            seen.add(o)
            ordered.append(o)
    return ordered


def clashes(svg):
    return (qc.text_overlaps_geometry(svg), qc.overlapping_text_labels(svg))


# Round 5's rule, which this tool never had: re-run the checks on your own output and
# roll back anything that comes back worse. Moving a label cannot fix a collision at
# the cost of a scale, a grid or a plotted point.
# Every figure check except the two this tool exists to clear. A nudge of 40 px can
# push a label off the canvas, out of the sector its angle arc marks, or away from the
# point its "?" names -- and until 2026-08-30 none of those three was watched, because
# the guard listed only the checks that existed when it was written.
GUARD = ("axis_scale_nonlinear", "gridlines_off_the_ticks", "axes_unlabelled",
         "plotted_points_inconsistent", "coordinate_figure_without_grid",
         "angle_arc_malformed", "doubled_circle_outline",
         "text_outside_the_canvas", "unknown_marker_far_from_point",
         "angle_named_without_arc", "label_too_faint", "axis_shorter_than_the_data",
         "gridlines_stop_short_of_the_axes", "plotted_geometry_matches_stem",
         "undefined_marker_reference")


# These read the whole question, not just the SVG: they compare the figure with what
# the stem says. Moving a TICK label changes the mapping the figure is read through,
# so they belong in the guard, but they have to be handed the row.
_GUARD_NEEDS_Q = ("plotted_geometry_matches_stem",)


def guard_state(svg, q=None):
    out = {n for n in GUARD if n not in _GUARD_NEEDS_Q and getattr(qc, n)(svg)}
    if q is not None:
        row = dict(q)
        row["figure_svg"] = svg
        out |= {n for n in _GUARD_NEEDS_Q if getattr(qc, n)(row)}
    return out


def repair(svg, tries=8, may_grow=True):
    """Nudge one label at a time until the figure is clean, or give up honestly."""
    moved = []
    seen = set()
    # A label gets ONE move. The loop is here to work through DIFFERENT labels, and
    # letting it come back to the same one compounds offsets it was never allowed to
    # make in one step -- an x-axis "0" went down 16 on the first pass and right 18 on
    # the second, ending a whole unit from the origin it names by two moves each of
    # which was individually within the tick budget.
    already = set()
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
        xps, yps = _tick_axes(svg)
        aligned = set()
        for _m in qc._TEXT.finditer(svg):
            _b = qc._text_box(_m)
            if not _b:
                continue
            _cx = (_b[0] + _b[2]) / 2
            if (any(abs(_cx - p) <= 3 for p in xps)
                    or any(abs(_b[1] - p) <= 5 for p in yps)):
                aligned.add(_b[4])

        def is_tick(t):
            return (bool(re.fullmatch(r"-?−?\d+(?:\.\d+)?", t.replace("−", "-")))
                    or t in aligned)
        # A tick may move ACROSS its own axis but never ALONG it. Sliding a number
        # away from the mark it names is a measurement change -- three figures came
        # back reading as nonlinear axes when the fallback did exactly that. Moving
        # it to the other side of the axis line keeps it level with its own mark, so
        # the scale is untouched, and it is what unsticks the commonest collision in
        # the bank: the x-axis "-1" and the y-axis "-1" meeting in the same corner
        # of the origin, where BOTH are ticks and neither could move at all.
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

        # An offset that pushes the label off the canvas is not a candidate at all.
        # Leaving it to the guard meant the whole figure was rolled back and the
        # collision left standing, when the next offset in the ring would have done.
        clipped0 = qc.text_outside_the_canvas(svg)
        # AN ANGLE LABEL MAY NOT LEAVE ITS SECTOR. "30°" sat inside the corner it
        # names, touching one side; nudged 16 px down it cleared the side and landed
        # OUTSIDE the triangle, naming nothing. `angle_named_without_arc` passed it,
        # because the arc was still within tolerance of the label -- the arc had not
        # moved. Only a rendered look caught it, which is the third time a label move
        # has been caught that way and nowhere else.
        before_sectors = _sector_map(svg)

        def ok(cand):
            if not clipped0 and qc.text_outside_the_canvas(cand):
                return False
            after = _sector_map(cand)
            for label, v in before_sectors.items():
                if label in after and after[label] != v:
                    return False
            return True

        groups = [g for g in groups if g[0] not in already]
        if not groups:
            return svg, moved
        for target, tags in groups:
            here = _clearance(svg, tags)
            options = []
            allowed = _allowed(tags[0], xps, yps)
            # A tick keeps its short, axis-crossing budget; anything else may also
            # take the outward normal of the side it is lying on.
            if not is_tick(target):
                allowed = _normal_offsets(svg, tags[0]) + allowed
            for dx, dy in allowed:
                cand = shift_group(svg, tags, dx, dy)
                if not ok(cand):
                    continue
                g2, l2 = clashes(cand)
                if g2 or l2:
                    continue
                shifted = [_shift(t, dx, dy) for t in tags]
                options.append((_clearance(cand, shifted), -abs(dx) - abs(dy),
                                cand, (target, dx, dy)))
            # NEAREST FIRST, not roomiest. Maximising clearance sent a point label
            # 56 px diagonally into the empty corner of its own plot, which clears
            # everything and names nothing. What a label needs is to stop touching --
            # a few pixels of daylight -- as close to where the author put it as that
            # allows.
            for gap, near, cand, mv in sorted(options, key=lambda o: -o[1]):
                if gap >= max(here, 3.0):
                    return cand, moved + [mv]
        target, tags = groups[0]
        # nothing clears everything; take the best partial and continue
        best = None
        fallback = _allowed(tags[0], xps, yps)
        if not is_tick(target):
            fallback = _normal_offsets(svg, tags[0]) + fallback
        for dx, dy in fallback:
            cand = shift_group(svg, tags, dx, dy)
            if not ok(cand):
                continue
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
        already.add(best[2][0])
    return svg, moved


def repair_and_fit(svg, tries=8):
    """Move the labels, then GROW THE CANVAS to whatever that needed.

    Twenty-eight of the reviewer's "Number/text overlapping with sides" could not be
    freed at all, and for a good share of them the reason was not that there was
    nowhere to put the label -- it was that the only place to put it was outside a
    canvas drawn tight around the shape. A dimension belongs outside the figure it
    measures; if the figure's box does not have room for that, the box is what is
    wrong.

    Growing a viewBox is additive under rule 11c -- it only ever adds empty space --
    so the two together stay a safe pair even though the move on its own is not.
    """
    fixed, moved = repair(svg, tries=tries, may_grow=True)
    if not moved:
        return svg, moved
    if qc.text_outside_the_canvas(fixed):
        grown, _box = grow(fixed)
        if not qc.text_outside_the_canvas(grown):
            return grown, moved
    return fixed, moved


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--forms")
    ap.add_argument("--ids", help="comma-separated question ids or id prefixes")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    if not (args.forms or args.ids):
        ap.error("give --forms or --ids")
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    if args.forms:
        forms = [f.strip() for f in args.forms.split(",") if f.strip()]
        rows = [dict(r) for r in con.execute(
            f"SELECT * FROM questions WHERE form_id IN ({','.join('?' * len(forms))}) "
            f"AND review_status!='rejected' AND figure_svg IS NOT NULL", forms)]
    else:
        want = tuple(i.strip() for i in args.ids.split(",") if i.strip())
        rows = [dict(r) for r in con.execute(
            "SELECT * FROM questions WHERE review_status!='rejected' "
            "AND figure_svg IS NOT NULL AND figure_svg != ''")
            if r["id"].startswith(want)]
    record = []
    for r in rows:
        if not any(clashes(r["figure_svg"])):
            continue
        fixed, moved = repair_and_fit(r["figure_svg"])
        regressed = sorted(guard_state(fixed, r) - guard_state(r["figure_svg"], r))
        if regressed:
            print(f"  [{r['form_id']} pos {r['form_position']}] ROLLED BACK — "
                  f"the move would have caused {regressed}")
            continue
        left = [m for m in clashes(fixed) if m]
        # A PARTIAL FIX IS NOT A FIX. The best-effort fallback accepts a move that
        # keeps the collision count the same while uncovering a different one, which
        # is right while the loop is still working and wrong as a final answer:
        # "120°" came off a radius and landed inside "Shaded sector", scoring equal
        # and reading worse. If the figure is not clean at the end, leave it exactly
        # as the author drew it and let the reviewer see the original.
        if left:
            print(f"  [{r['form_id']} pos {r['form_position']}] left alone — "
                  f"no offset clears it: {left[0][:60]}")
            continue
        tag = "clean" 
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
