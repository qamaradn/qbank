#!/usr/bin/env python3
"""Shared machinery for the NSW mathematics builders.

The point of this module is that **no answer is ever typed**. `Q` takes the key and each
distractor as computed Python values, and every item must also supply `verify` — the same
answer reached by a second, genuinely different route. A rectangle's area computed as
l * w is checked against the shoelace area of the drawn polygon; a volume computed in
cubic metres is checked against the same volume computed in cubic centimetres. If the two
disagree the build aborts, so an item cannot reach the review queue with a wrong key.

That matters more here than in any other subject. A reading question with a bad key is
arguable; a maths question with a bad key is simply wrong, and the reviewer has to redo
the arithmetic to notice. On the Year 7 figure batch, hand-checked-after-the-fact labels
shipped two shapes that were geometrically impossible.

`angle_rays` draws rays from a point and labels the sectors between them from the same
list of angles used to compute the answer, so a diagram cannot disagree with its question.
"""
import datetime
import json
import math
import pathlib
import sys
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.figure_lib import svg, txt  # noqa: E402

GEN = ROOT / "run_data/output/mathematics/generated"
BOOK = "ma_nsw_selective"
AREA_OF = {}          # category key -> §4.1 area, filled from the plan


def _load_plan():
    plan = json.loads((GEN / "ma_PLAN.json").read_text(encoding="utf-8"))
    AREA_OF.update({c["key"]: c["area"] for c in plan["categories"]})
    return {c["key"]: c["title"] for c in plan["categories"]}


TITLE_OF = _load_plan()


def fmt_num(v):
    """Render a computed value the way a Year 6 paper would print it."""
    if isinstance(v, float):
        if abs(v - round(v)) < 1e-9:
            return str(int(round(v)))
        s = f"{v:.2f}".rstrip("0").rstrip(".")
        return s
    return str(v)


def money(v):
    v = round(float(v) + 1e-9, 2)
    return f"${int(v)}" if abs(v - int(v)) < 1e-9 else f"${v:.2f}"


def deg(v):
    """Degrees close up against the number: "62°", never "62 °"."""
    return f"{fmt_num(v)}°"


def unit(u):
    return lambda v: f"{fmt_num(v)} {u}"


PLAIN = fmt_num


class Batch:
    def __init__(self, nn, now="2026-08-07T13:00:00Z"):
        self.nn = nn
        self.now = now
        self.items = []

    def Q(self, cat, archetype, stem, key, wrong, expl, verify,
          difficulty="medium", confidence=0.93, fig=None, fmt=PLAIN, mixed_units=False):
        """Add one question. `key`/`wrong` values are computed, never typed.

        wrong: [(value, error_class)] — three of them, in the fixed order B, C, D before
        the finaliser shuffles. `verify` must equal `key` and must be reached another way.
        """
        if verify is None:
            raise ValueError(f"{cat}: every item needs an independent `verify` route")
        if isinstance(key, float) or isinstance(verify, float):
            ok = math.isclose(float(key), float(verify), rel_tol=1e-9, abs_tol=1e-9)
        else:
            ok = key == verify
        if not ok:
            raise AssertionError(
                f"{cat}: the two routes disagree — key={key!r} but verify={verify!r}. "
                f"One of them is wrong; do not 'fix' this by deleting the check.")
        if len(wrong) != 3:
            raise ValueError(f"{cat}: need exactly 3 distractors, got {len(wrong)}")

        opts = [fmt(key)] + [fmt(v) for v, _ in wrong]
        if len(set(opts)) != 4:
            raise AssertionError(f"{cat}: options collide after formatting: {opts}")
        errors = {fmt(v): cls for v, cls in wrong}

        q = {
            "id": str(uuid.uuid4()),
            "subject": "mathematics",
            "stem": stem,
            "option_a": opts[0], "option_b": opts[1],
            "option_c": opts[2], "option_d": opts[3],
            "correct_answer": "A",
            "explanation": expl,
            "topic": AREA_OF[cat],
            "difficulty": difficulty,
            "confidence": confidence,
            "source_book": BOOK,
            "source_page": self.nn,
            "source_page_description": f"Category: {cat} — {TITLE_OF[cat]}",
            "passage": None,
            "figure_svg": fig,
            "review_status": "pending",
            "created_at": self.now,
            "category": cat,
            "archetype": archetype,
            "errors": errors,
        }
        if mixed_units:
            q["mixed_units"] = True
        self.items.append(q)
        return q

    def write(self):
        GEN.mkdir(parents=True, exist_ok=True)
        path = GEN / f"{BOOK}_p{self.nn}.json"
        path.write_text(json.dumps(self.items, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
        print(f"wrote {len(self.items)} questions -> {path}")
        return path


# ------------------------------------------------------------------ angle figures
def angle_rays(spans, labels, r=76, cx=170, cy=None, start=180, full=False, vw=340):
    """Draw rays from one point; label each sector from the same spans used in the maths.

    spans:  sector sizes in degrees, walked anticlockwise from `start`.
    labels: one label per sector, e.g. "118°" or "x".
    full:   True for angles at a point (spans must total 360), else a straight line (180).
    """
    total = 360 if full else 180
    if sum(spans) != total:
        raise ValueError(f"spans total {sum(spans)}, not {total}")
    if len(labels) != len(spans):
        raise ValueError("one label per sector")
    # A full turn has rays going downward too, so the centre belongs in the middle of the
    # canvas. Hanging it near the bottom (right for a straight line, which only uses the
    # upper half) clipped the third sector's label straight off the viewBox.
    vh = 220 if full else 150
    if cy is None:
        cy = vh / 2 if full else vh - 34

    def pt(deg, rad):
        a = math.radians(deg)
        return cx + rad * math.cos(a), cy - rad * math.sin(a)

    body = []
    if not full:                                   # the straight line itself
        x1, y1 = pt(180, r + 22)
        x2, y2 = pt(0, r + 22)
        body.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" '
                    f'stroke="currentColor" stroke-opacity=".55" stroke-width="1.4"/>')
    ang = start
    bounds = [ang]
    for s in spans:
        ang -= s
        bounds.append(ang)
    for b in bounds if full else bounds[1:-1]:
        x, y = pt(b, r)
        body.append(f'<line x1="{cx}" y1="{cy:.0f}" x2="{x:.0f}" y2="{y:.0f}" '
                    f'stroke="currentColor" stroke-opacity=".9" stroke-width="2"/>')
    ang = start
    for s, lab in zip(spans, labels):
        mid = ang - s / 2
        lx, ly = pt(mid, r * 0.52)
        body.append(txt(lx, ly + 4, lab, 14))
        ang -= s
    body.append(f'<circle cx="{cx}" cy="{cy:.0f}" r="3" fill="currentColor" '
                f'fill-opacity=".9"/>')
    return svg("".join(body), vb=f"0 0 {vw} {vh}")


def triangle_fig(left, right, labels, base=250, vw=340, vh=190):
    """Draw a triangle whose shape is computed from its own angles.

    left/right are the two base angles in degrees; the apex follows from them. Drawing a
    fixed schematic triangle instead put a visibly wide apex on a question whose answer
    was 65°, which invites a student to answer by eye and be wrong — and would have
    rewarded eyeballing on some other item purely by luck.
    """
    a, b = math.radians(left), math.radians(right)
    d = base * math.tan(b) / (math.tan(a) + math.tan(b))
    h = d * math.tan(a)
    x0 = (vw - base) / 2
    y0 = vh - 26
    pts = [(x0, y0), (x0 + base, y0), (x0 + d, y0 - h)]
    path = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"
    body = [f'<path d="{path}" stroke="currentColor" stroke-opacity=".9" stroke-width="2" '
            f'fill="currentColor" fill-opacity=".05"/>']
    # Each label sits inside the triangle, along the bisector from its own vertex.
    cx, cy = sum(p[0] for p in pts) / 3, sum(p[1] for p in pts) / 3
    for (px, py), lab in zip(pts, labels):
        f = 0.30
        body.append(txt(px + (cx - px) * f, py + (cy - py) * f + 4, lab, 14))
    return svg("".join(body), vb=f"0 0 {vw} {vh}")


def shoelace(pts):
    """Polygon area from its vertices — an independent route to any area computed
    by decomposing a shape into rectangles or halving a bounding box."""
    n = len(pts)
    return abs(sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1]
                   for i in range(n))) / 2
