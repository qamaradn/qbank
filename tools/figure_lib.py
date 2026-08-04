#!/usr/bin/env python3
"""Builders for inline `figure_svg`, usable by any subject's generator.

Written for the logical_reasoning figure batches; nothing here is LR-specific. The
orthogonal-shape and isometric-stack builders would both have caught defects that
shipped in the Year 7 mathematics figures.

Everything draws in `currentColor` with a viewBox, which is what
`tools.question_checks.figure_svg_errors` requires. Render and LOOK at the output with
`tools/figure_contact_sheet.py` — code cannot tell you a correct figure is unreadable.

Two things here exist because of defects found on the pilot batch:

`ortho` — an orthogonal shape is described ONCE, as a list of moves in real units. The
SVG path and the side labels are both generated from that single description, so a label
can no longer disagree with the line it names. The pilot had two shapes whose labels were
geometrically impossible (an L-bed whose left side could not equal right + step, and a
composite drawn 12.5 cm but labelled 12); both were written by hand and checked after the
fact. This removes the class of error rather than the instances.

`iso_stack_fitted` — draws only visible faces and then measures its own bounding box to
centre itself. Drawing buried cubes produced an uncountable tessellation, and hand-picked
offsets clipped the tallest column off the canvas. `check_stack` additionally rejects a
layout where a near column would paint over a far one, which face-culling cannot fix
because such columns are not adjacent, merely overlapping in projection.
"""
import re

W, H, V = 30, 17, 34


# ------------------------------------------------------------------ primitives
def svg(body, vb="0 0 340 220"):
    return (f'<svg viewBox="{vb}" xmlns="http://www.w3.org/2000/svg" fill="none" '
            f'stroke-linejoin="round" stroke-linecap="round">{body}</svg>')


def txt(x, y, s, size=13, anchor="middle", op=".9"):
    return (f'<text x="{x:.0f}" y="{y:.0f}" font-family="system-ui,sans-serif" '
            f'font-size="{size}" fill="currentColor" fill-opacity="{op}" '
            f'text-anchor="{anchor}">{s}</text>')


def rect(x, y, w, h, op=".85"):
    return (f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" '
            f'stroke="currentColor" stroke-opacity="{op}" stroke-width="1.8" '
            f'fill="currentColor" fill-opacity=".05"/>')


# ------------------------------------------------------------------ orthogonal shapes
def ortho(moves, unit, scale, x0=None, y0=None, vw=340, vh=220, pad=34, show=True):
    """Draw a closed orthogonal polygon and label every side from the same data.

    moves: [(dx, dy)] in real units, walked in order; must sum to (0, 0).
    unit:  string appended to each label, e.g. "m" or "cm".
    scale: pixels per unit.

    Returns (svg_body, perimeter, area).
    """
    if sum(d[0] for d in moves) or sum(d[1] for d in moves):
        raise ValueError(f"shape does not close: {moves}")

    pts = [(0, 0)]
    for dx, dy in moves:
        pts.append((pts[-1][0] + dx, pts[-1][1] + dy))
    pts.pop()

    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    if x0 is None:
        x0 = (vw - (max(xs) - min(xs)) * scale) / 2 - min(xs) * scale
    if y0 is None:
        y0 = (vh - (max(ys) - min(ys)) * scale) / 2 - min(ys) * scale

    def px(p):
        return (x0 + p[0] * scale, y0 + p[1] * scale)

    d = "M" + " L".join(f"{px(p)[0]:.0f} {px(p)[1]:.0f}" for p in pts) + " Z"
    body = (f'<path d="{d}" stroke="currentColor" stroke-opacity=".9" stroke-width="2" '
            f'fill="currentColor" fill-opacity=".05"/>')

    # shoelace area, and centroid used to push each label to the outside
    area = abs(sum(pts[i][0] * pts[(i + 1) % len(pts)][1] -
                   pts[(i + 1) % len(pts)][0] * pts[i][1]
                   for i in range(len(pts)))) / 2
    def inside(p):
        """Ray-cast point-in-polygon, in shape units."""
        x, y = p
        hit = False
        for i in range(len(pts)):
            ax, ay = pts[i]
            bx, by = pts[(i + 1) % len(pts)]
            if (ay > y) != (by > y) and x < (bx - ax) * (y - ay) / (by - ay) + ax:
                hit = not hit
        return hit

    # A centroid test picks the wrong side on a concave shape: on the T-piece it put the
    # two bar-underside labels INSIDE the bar, and on the L-panel two labels collided.
    # Testing whether the offset point actually falls inside the polygon is exact.
    recs = []
    for i, (dx, dy) in enumerate(moves):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        probe = 0.45
        if dy == 0:                                     # horizontal side
            out = -1 if not inside((mx, my - probe)) else 1
            recs.append({"x": px((mx, my))[0], "y": px((mx, my))[1] + (-8 if out < 0 else 20),
                         "t": f"{abs(dx)} {unit}", "a": "middle", "ux": 1, "uy": 0})
        else:                                           # vertical side
            out = -1 if not inside((mx - probe, my)) else 1
            recs.append({"x": px((mx, my))[0] + (-9 if out < 0 else 9),
                         "y": px((mx, my))[1] + 5, "t": f"{abs(dy)} {unit}",
                         "a": "end" if out < 0 else "start", "ux": 0, "uy": 1})

    # Push apart labels that land on top of each other. A narrow concavity sends several
    # outward-pointing labels into the same small gap — the U-piece printed three of them
    # over one another as an unreadable smudge. Each is nudged along its own edge.
    def span(r):
        """Horizontal extent of the rendered text, which is what actually collides.

        Comparing anchor points alone missed the U-piece's notch labels: they are
        anchored 60 px apart but point toward each other, so the glyphs overlapped
        while the anchors looked comfortably clear.
        """
        w = 7.0 * len(r["t"])
        return {"start": (r["x"], r["x"] + w),
                "end": (r["x"] - w, r["x"])}.get(r["a"], (r["x"] - w / 2, r["x"] + w / 2))

    for _ in range(8):
        moved = False
        for i in range(len(recs)):
            for j in range(i + 1, len(recs)):
                p, q = recs[i], recs[j]
                (pa, pb), (qa, qb) = span(p), span(q)
                if min(pb, qb) - max(pa, qa) > -4 and abs(p["y"] - q["y"]) < 15:
                    for r, sgn in ((p, -1), (q, 1)):
                        r["x"] += sgn * 13 * r["ux"]
                        r["y"] += sgn * 13 * r["uy"]
                    moved = True
        if not moved:
            break
    labels = [txt(r["x"], r["y"], r["t"], anchor=r["a"]) for r in recs]
    perim = sum(abs(dx) + abs(dy) for dx, dy in moves)
    return body + ("".join(labels) if show else ""), perim, area


# ------------------------------------------------------------------ isometric stacks
def _p(x, y, z, ox, oy):
    return (ox + (x - y) * W, oy + (x + y) * H - z * V)


def check_stack(heights):
    """Reject a layout where a nearer column would paint over a farther one."""
    bad = [f"col{(x, y)} h{v} would cover col{(x2, y2)} h{v2}"
           for (x, y), v in heights.items() for (x2, y2), v2 in heights.items()
           if (x2 + y2) < (x + y) and v > v2 and (x - y) == (x2 - y2)]
    if bad:
        raise ValueError("stack occlusion: " + "; ".join(bad))
    return sum(heights.values()), len(heights)


def iso_stack(heights, ox=0, oy=0):
    cubes = {(x, y, z) for (x, y), h in heights.items() for z in range(h)}
    out = []
    for x, y, z in sorted(cubes, key=lambda c: (c[0] + c[1], c[2])):
        faces = []
        if (x, y, z + 1) not in cubes:
            faces.append(([_p(x, y, z + 1, ox, oy), _p(x + 1, y, z + 1, ox, oy),
                           _p(x + 1, y + 1, z + 1, ox, oy), _p(x, y + 1, z + 1, ox, oy)],
                          ".26"))
        if (x, y + 1, z) not in cubes:
            faces.append(([_p(x, y + 1, z + 1, ox, oy), _p(x + 1, y + 1, z + 1, ox, oy),
                           _p(x + 1, y + 1, z, ox, oy), _p(x, y + 1, z, ox, oy)], ".06"))
        if (x + 1, y, z) not in cubes:
            faces.append(([_p(x + 1, y, z + 1, ox, oy), _p(x + 1, y + 1, z + 1, ox, oy),
                           _p(x + 1, y + 1, z, ox, oy), _p(x + 1, y, z, ox, oy)], ".15"))
        for pts, op in faces:
            dd = " ".join(f"{a:.0f},{b:.0f}" for a, b in pts)
            out.append(f'<polygon points="{dd}" fill="currentColor" fill-opacity="{op}" '
                       f'stroke="currentColor" stroke-opacity=".9" stroke-width="1.6"/>')
    return "".join(out)


def iso_stack_fitted(heights, vw=340, vh=220, pad=16):
    check_stack(heights)
    body = iso_stack(heights)
    xs, ys = [], []
    for p in re.findall(r'points="([^"]+)"', body):
        for pair in p.split():
            a, b = pair.split(",")
            xs.append(float(a))
            ys.append(float(b))
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    s = min(1.0, (vw - 2 * pad) / w, (vh - 2 * pad) / h)
    dx = (vw - w * s) / 2 - min(xs) * s
    dy = (vh - h * s) / 2 - min(ys) * s
    return f'<g transform="translate({dx:.1f},{dy:.1f}) scale({s:.3f})">{body}</g>'


# ------------------------------------------------------------------ cube nets
def fold(cells):
    """cells: {label: (col, row)} -> {label: outward normal} after folding."""
    def cross(a, b):
        return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
                a[0] * b[1] - a[1] * b[0])

    def neg(a):
        return (-a[0], -a[1], -a[2])

    pos = {v: k for k, v in cells.items()}
    root = next(iter(cells.values()))
    state = {root: ((0, 0, 1), (0, 1, 0))}
    stack = [root]
    while stack:
        c = stack.pop()
        n, u = state[c]
        r = cross(u, n)
        for d, (nn, nu) in {(1, 0): (r, u), (-1, 0): (neg(r), u),
                            (0, 1): (neg(u), n), (0, -1): (u, neg(n))}.items():
            nb = (c[0] + d[0], c[1] + d[1])
            if nb in pos and nb not in state:
                state[nb] = (nn, nu)
                stack.append(nb)
    if len(state) != len(cells):
        raise ValueError("net is not connected")
    faces = {pos[c]: state[c][0] for c in state}
    if len(set(faces.values())) != 6:
        raise ValueError("net does not fold to a cube — two faces collide")
    return faces


def opposite_of(cells, label):
    f = fold(cells)
    tgt = tuple(-v for v in f[label])
    return next(k for k, v in f.items() if v == tgt)


def net_svg(cells, size=46, ox=None, oy=None, vw=340, vh=220):
    fold(cells)                                   # refuse to draw an invalid net
    cs = list(cells.values())
    w = (max(c[0] for c in cs) + 1) * size
    h = (max(c[1] for c in cs) + 1) * size
    ox = (vw - w) / 2 if ox is None else ox
    oy = (vh - h) / 2 if oy is None else oy
    body = "".join(rect(ox + c * size, oy + r * size, size, size)
                   for c, r in cells.values())
    body += "".join(txt(ox + c * size + size / 2, oy + r * size + size / 2 + 6, k, 16)
                    for k, (c, r) in cells.items())
    return body
