#!/usr/bin/env python3
"""Redraw twenty coordinate planes that had no grid, no ticks and, in nine cases,
points the line does not pass through.

WHY A REDRAW AND NOT A GRID. The reviewer asked for gridlines on twenty figures --
"please add some grid lines and subdivisions/scale lines" -- and on nine of them said
something else in the same breath: "the line doesn't pass through designated points",
"None of the mentioned points are touched", "the graph makes no sense with the 0, −2
being ABOVE the x-axis". Those are the same fault. A plane with no ticks has no scale
to be wrong against, so nothing could check it and nothing did; the moment you draw
the grid the misplacement becomes visible. Adding a grid to the figure as drawn would
have produced a figure that is visibly wrong instead of invisibly wrong.

So each is rebuilt by `figure_lib.plane`, where the axes, ticks, gridlines, dots and
lines are all placed by one px() and there is no second opinion about where a unit is.
The spec below carries only what the STEM and the stored explanation say; the drawing
follows from that. Every redraw is re-checked against the full figure check set and
rolled back if anything new fires.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_vic_plane_redraws
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_vic_plane_redraws --apply
"""
import argparse
import json
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import figure_lib as fl                 # noqa: E402
from tools import question_checks as qc            # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
RECORD = ROOT / "run_data/output/plane_redraws.json"

FIG_CHECKS = ("doubled_circle_outline", "overlapping_text_labels",
              "plotted_points_inconsistent", "text_overlaps_geometry",
              "axes_unlabelled", "angle_arc_malformed", "axis_scale_nonlinear",
              "coordinate_figure_without_grid", "gridlines_off_the_ticks",
              "unknown_marker_far_from_point", "label_too_faint",
              "undefined_marker_reference", "text_outside_the_canvas",
              "gridlines_stop_short_of_the_axes", "axis_shorter_than_the_data")
Q_CHECKS = ("angle_named_without_arc", "polygon_sides_disagree_with_stem",
            "figure_proportions_disagree", "plotted_geometry_matches_stem")


def _dashed(pa, pb, label=None, at=None):
    """An auxiliary construction line, placed by the figure's own px()."""
    def build(px):
        (x1, y1), (x2, y2) = px(*pa), px(*pb)
        out = (f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" '
               f'stroke="currentColor" stroke-width="1.4" stroke-dasharray="5,4" '
               f'stroke-opacity=".85"/>')
        if label:
            lx, ly = px(*at)
            t = (f'<text x="{lx:.0f}" y="{ly:.0f}" font-size="12" '
                 f'text-anchor="middle">{label}</text>')
            # Same two-layer halo the tick numbers use, and the same reason: the
            # stroke is the PAGE colour, which currentColor cannot be, so it rides in
            # an aria-hidden layer that `figure_svg_errors` knows to judge separately.
            out += (f'<g stroke="#fff" stroke-width="3" '
                    f'stroke-linejoin="round" fill="none" aria-hidden="true">{t}</g>'
                    f'<g fill="currentColor">{t}</g>')
        return out
    return build


def _right_angle(corner, along_a, along_b, size=0.5):
    """A right-angle square at `corner`, opening towards the two given directions."""
    def build(px):
        cx, cy = corner
        ax = (cx + (along_a[0] - cx) * 0, cy)
        p0 = px(cx + (along_a[0] - cx) * size / _norm(along_a, corner),
                cy + (along_a[1] - cy) * size / _norm(along_a, corner))
        p2 = px(cx + (along_b[0] - cx) * size / _norm(along_b, corner),
                cy + (along_b[1] - cy) * size / _norm(along_b, corner))
        p1 = (p0[0] + p2[0] - px(*corner)[0], p0[1] + p2[1] - px(*corner)[1])
        pts = " ".join(f"{a:.0f},{b:.0f}" for a, b in (p0, p1, p2))
        return (f'<polyline points="{pts}" fill="none" stroke="currentColor" '
                f'stroke-width="1.3"/>')
    return build


def _norm(p, c):
    return max(((p[0] - c[0]) ** 2 + (p[1] - c[1]) ** 2) ** 0.5, 1e-9)


def _curve(fn, x_lo, x_hi, yr, n=40):
    """A smooth curve y = fn(x), sampled through the figure's own px() and STOPPED at
    the top and bottom of the plane.

    Drawn to a fixed x range the first cut ran a parabola's arms three units below the
    y-axis's lowest number and out through the bottom of the canvas, where a browser
    simply does not draw them -- a curve that appears to stop in mid-air.
    """
    def build(px):
        runs, cur = [], []
        for i in range(n + 1):
            x = x_lo + (x_hi - x_lo) * i / n
            y = fn(x)
            if yr[0] <= y <= yr[1]:
                cur.append(px(x, y))
            elif cur:
                runs.append(cur)
                cur = []
        if cur:
            runs.append(cur)
        d = "".join("M" + "L".join(f"{a:.0f} {b:.0f}" for a, b in r)
                    for r in runs if len(r) > 1)
        return (f'<path d="{d}" fill="none" stroke="currentColor" '
                f'stroke-width="2" stroke-opacity=".9"/>')
    return build


def _both(*builders):
    return lambda px: "".join(b(px) for b in builders)


def _angle_at(vertex, to_a, to_b, label, r=30.0):
    """An arc between two rays out of `vertex`, with its name written OUTSIDE it.

    `angle_mark` draws the arc alone -- it takes a label only to decide whether the
    angle may be marked square -- so the name has to be placed here, on the bisector
    and clear of the arc, which is where a textbook puts it.
    """
    import math

    def build(px):
        v = px(*vertex)
        a1 = math.atan2(px(*to_a)[1] - v[1], px(*to_a)[0] - v[0])
        a2 = math.atan2(px(*to_b)[1] - v[1], px(*to_b)[0] - v[0])
        lo, hi = (a1, a2) if (a2 - a1) % (2 * math.pi) < math.pi else (a2, a1)
        arc = fl.angle_mark(v, lo, hi, r, label=label) or ""
        bis = lo + ((hi - lo) % (2 * math.pi)) / 2
        tx = v[0] + (r + 13) * math.cos(bis)
        ty = v[1] + (r + 13) * math.sin(bis) + 4
        return (arc + f'<text x="{tx:.0f}" y="{ty:.0f}" font-size="13" '
                f'text-anchor="middle" fill="currentColor">{label}</text>')
    return build


# Each entry is exactly what the stem and the stored explanation state, and nothing
# more. Where the original figure labelled a point, the redraw labels it too: taking a
# label away would change how hard the question is, which is not this round's business.
SPECS = {
    # "length of the line segment with endpoints A(−2, 3) and B(4, −5)" -> 10
    "e760717a": dict(points={"A(−2,3)": (-2, 3), "B(4,−5)": (4, -5)},
                     segments=[((-2, 3), (4, -5))], xr=(-4, 5), yr=(-6, 4), cell=24),
    # graphed line y = 2x + 3, marked at (0, 3)
    "e75376a3": dict(lines=[((0, 3), (1, 5))], points={"(0,3)": (0, 3)},
                     xr=(-4, 4), yr=(-4, 6), cell=26),
    # graphed line y = −(2/3)x − 2 through (0, −2) and (3, −4)
    "cfcc1cf4": dict(lines=[((0, -2), (3, -4))],
                     points={"(0,−2)": (0, -2), "(3,−4)": (3, -4)},
                     xr=(-4, 5), yr=(-6, 3), cell=24),
    # line through (0, 5) and (−2, 0), slope 5/2
    "1451a26a": dict(lines=[((0, 5), (-2, 0))],
                     points={"(0,5)": (0, 5), "(−2,0)": (-2, 0)},
                     xr=(-5, 4), yr=(-3, 7), cell=24),
    # gradient −1/2 through (−2, 3) and (6, −1)
    "d6dcc058": dict(lines=[((-2, 3), (6, -1))],
                     points={"(−2,3)": (-2, 3), "(6,−1)": (6, -1)},
                     xr=(-4, 8), yr=(-4, 5), cell=22),
    # 2x − 5y = 10: through (5, 0) and (0, −2)
    "00ca8516": dict(lines=[((5, 0), (0, -2))],
                     points={"(5,0)": (5, 0), "(0,−2)": (0, -2)},
                     xr=(-3, 7), yr=(-5, 4), cell=24),
    # line l through A(−3, 0) and B(0, 4)
    "9f80068b": dict(lines=[((-3, 0), (0, 4))],
                     points={"A(−3,0)": (-3, 0), "B(0,4)": (0, 4)},
                     xr=(-5, 4), yr=(-3, 6), cell=24),
    # second line through (0, 2) and (3, 0)
    "1d26d673": dict(lines=[((0, 2), (3, 0))],
                     points={"(0,2)": (0, 2), "(3,0)": (3, 0)},
                     xr=(-3, 5), yr=(-3, 5), cell=26),
    # triangle (0,0) (0,8) (6,0) with the line y = 4 across it
    "2d147b4c": dict(polygon=[(0, 0), (0, 8), (6, 0)],
                     points={"(0,8)": (0, 8), "(6,0)": (6, 0), "(0,0)": (0, 0)},
                     xr=(-2, 8), yr=(-2, 9), cell=22,
                     extra=_dashed((-2, 4), (8, 4), "y = 4", (6.6, 4.6))),
    # 4x − 2y + 8 = 0 -> y = 2x + 4; intercepts (−2, 0) and (0, 4)
    "bf58b875": dict(lines=[((-2, 0), (0, 4))], points=[(-2, 0), (0, 4)],
                     xr=(-5, 4), yr=(-3, 6), cell=24),
    # triangle A(1,1) B(1,7) C(9,1), right angle at A
    "94ac4db7": dict(polygon=[(1, 1), (1, 7), (9, 1)],
                     points={"A(1,1)": (1, 1), "B(1,7)": (1, 7), "C(9,1)": (9, 1)},
                     xr=(-1, 10), yr=(-1, 8), cell=22,
                     extra=_right_angle((1, 1), (9, 1), (1, 7))),
    # x = 3 and y = x + 2 meet at (3, 5)
    "a30aed4e": dict(lines=[((3, -3), (3, 6)), ((0, 2), (1, 3))],
                     points={"(3,5)": (3, 5)}, xr=(-4, 6), yr=(-3, 7), cell=24),
    # segment PQ from P(0,2) to Q(4,4)
    "bf8c473c": dict(points={"P(0,2)": (0, 2), "Q(4,4)": (4, 4)},
                     segments=[((0, 2), (4, 4))], xr=(-1, 6), yr=(-1, 6), cell=28),
    # C and the four candidate images
    "24bfd1e2": dict(points={"C(−2,−4)": (-2, -4), "W(2,−4)": (2, -4),
                             "X(−2,4)": (-2, 4), "Y(4,−2)": (4, -2), "Z(2,4)": (2, 4)},
                     xr=(-5, 5), yr=(-5, 5), cell=22),
    # line through (1, 1) and (3, 5) -> y = 2x − 1
    "283c5e44": dict(lines=[((1, 1), (3, 5))],
                     points={"(1,1)": (1, 1), "(3,5)": (3, 5)},
                     xr=(-3, 5), yr=(-3, 7), cell=24),
    # 3x − 2y = 6 through (0, −3) and (2, 0)
    "0328eb9f": dict(lines=[((0, -3), (2, 0))],
                     points={"(0,−3)": (0, -3), "(2,0)": (2, 0)},
                     xr=(-3, 6), yr=(-5, 4), cell=24),
    # parabola through (−1,0) (3,0) (0,3): y = −(x+1)(x−3)
    "6836b305": dict(points={"(−1,0)": (-1, 0), "(3,0)": (3, 0), "(0,3)": (0, 3)},
                     xr=(-3, 5), yr=(-3, 6), cell=26,
                     extra=_curve(lambda x: -(x + 1) * (x - 3), -2.4, 4.4, (-3, 6))),
    # triangle P(1,1) Q(7,1) R(4,6)
    "a4c1594f": dict(polygon=[(1, 1), (7, 1), (4, 6)],
                     points={"P(1,1)": (1, 1), "Q(7,1)": (7, 1), "R(4,6)": (4, 6)},
                     xr=(-1, 9), yr=(-1, 8), cell=24),
    # segment A(1,1) to B(5,4), theta against the positive x direction
    "9eb394c5": dict(points={"A(1,1)": (1, 1), "B(5,4)": (5, 4)},
                     segments=[((1, 1), (5, 4))], xr=(-1, 7), yr=(-1, 6), cell=26,
                     extra=_both(_dashed((1, 1), (6.2, 1)),
                                 _angle_at((1, 1), (6.2, 1), (5, 4), "θ"))),
    # triangle A(−3,0) B(0,4) C(3,0) with its height marked
    "4f2da048": dict(polygon=[(-3, 0), (0, 4), (3, 0)],
                     points={"A(−3,0)": (-3, 0), "B(0,4)": (0, 4), "C(3,0)": (3, 0)},
                     xr=(-5, 5), yr=(-2, 6), cell=24,
                     extra=_both(_dashed((0, 0), (0, 4)),
                                 _right_angle((0, 0), (3, 0), (0, 4)))),
}


def state(q, svg):
    row = dict(q)
    row["figure_svg"] = svg
    return ({n for n in FIG_CHECKS if getattr(qc, n)(svg)}
            | {n for n in Q_CHECKS if getattr(qc, n)(row)})


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dump", type=pathlib.Path, help="write before/after JSON to look at")
    args = ap.parse_args()

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    done, failed, dump = [], [], []
    for prefix, spec in SPECS.items():
        row = con.execute("SELECT * FROM questions WHERE id LIKE ?",
                          (prefix + "%",)).fetchone()
        if row is None:
            failed.append({"id": prefix, "why": "no such question"})
            continue
        q = dict(row)
        before = state(q, q["figure_svg"])
        new = fl.plane(**spec)
        after = state(q, new)
        gained = after - before
        if gained:
            failed.append({"id": q["id"], "newly_firing": sorted(gained)})
            continue
        done.append({"id": q["id"], "form": q["form_id"],
                     "cleared": sorted(before - after), "left": sorted(after)})
        dump.append({"id": prefix + "-BEFORE", "figure_svg": q["figure_svg"],
                     "stem": q["stem"]})
        dump.append({"id": prefix + "-AFTER", "figure_svg": new, "stem": q["stem"]})
        if args.apply:
            con.execute("UPDATE questions SET figure_svg = ?, edited = 1 WHERE id = ?",
                        (new, q["id"]))
    if args.apply:
        con.commit()
    if args.dump:
        args.dump.write_text(json.dumps(dump))
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps({"applied": args.apply, "redrawn": done,
                                  "refused": failed}, indent=1))
    print(f"{len(done)} redrawn, {len(failed)} refused"
          f"{'' if args.apply else '  (dry run — pass --apply)'}")
    for f in failed:
        print("   refused", f["id"][:8], f.get("newly_firing") or f["why"])
    for d in done:
        if d["left"]:
            print("   still flagged", d["id"][:8], d["left"])
    print(f"record -> {RECORD}")


if __name__ == "__main__":
    main()
