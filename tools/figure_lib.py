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
import math
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


# ------------------------------------------------------------------ tables
def table(rows, col_w=None, row_h=24, pad=8, size=12.5, vw=340, header=True):
    """Draw a table and size its own viewBox around it.

    rows: list of rows, each a list of cell strings; row 0 is the header when `header`.

    A timetable or two-way table is data the question reasons over, so it has to be a
    figure rather than stem prose: the review UI renders the stem as markdown and the
    Selectly player renders it as pre-wrapped plain text, and a pipe table survives
    neither intact. Columns are measured from the widest cell so nothing collides.
    """
    ncol = max(len(r) for r in rows)
    rows = [list(r) + [""] * (ncol - len(r)) for r in rows]
    if col_w is None:
        col_w = [max(7.0 * max(len(str(r[c])) for r in rows) + 2 * pad, 44)
                 for c in range(ncol)]
    total = sum(col_w)
    if total > vw - 8:                                   # shrink to fit the canvas
        col_w = [w * (vw - 8) / total for w in col_w]
        total = sum(col_w)
    h = row_h * len(rows)
    ox, oy = (vw - total) / 2, 6
    body = []
    if header:
        body.append(f'<rect x="{ox:.0f}" y="{oy:.0f}" width="{total:.0f}" '
                    f'height="{row_h}" fill="currentColor" fill-opacity=".10"/>')
    body.append(f'<rect x="{ox:.0f}" y="{oy:.0f}" width="{total:.0f}" height="{h}" '
                f'stroke="currentColor" stroke-opacity=".85" stroke-width="1.6"/>')
    # Every rule in one <path>: a five-column timetable drawn as separate <line> elements
    # runs past the 3.5 KB budget figure_svg_errors enforces.
    rules = []
    y = oy
    for r in range(1, len(rows)):
        y += row_h
        rules.append(f"M{ox:.0f} {y:.0f}H{ox + total:.0f}")
    x = ox
    for c in range(ncol - 1):
        x += col_w[c]
        rules.append(f"M{x:.0f} {oy:.0f}V{oy + h:.0f}")
    body.append(f'<path d="{"".join(rules)}" stroke="currentColor" stroke-opacity=".45" '
                f'stroke-width="1"/>')
    for r, row in enumerate(rows):
        x = ox
        for c, cell in enumerate(row):
            body.append(txt(x + col_w[c] / 2, oy + r * row_h + row_h / 2 + 4.5,
                            str(cell), size, op=".95" if r == 0 and header else ".85"))
            x += col_w[c]
    return svg("".join(body), vb=f"0 0 {vw} {h + 12}")


# ------------------------------------------------------------------ coordinate grids
def coord_grid(points, xmax=6, ymax=6, cell=26, vw=340, pad=30, dots=True):
    """Plot labelled points on a first-quadrant grid.

    points: {label: (x, y)} in grid units. The dots and the axis numbering both come from
    the same coordinates the question reasons about, so a plotted point cannot sit
    somewhere other than where the stem says it is.
    """
    gw, gh = xmax * cell, ymax * cell
    ox, oy = (vw - gw) / 2 + 8, pad
    vh = gh + 2 * pad + 6

    def px(x, y):
        return ox + x * cell, oy + (ymax - y) * cell

    rules = []
    for i in range(xmax + 1):
        x, _ = px(i, 0)
        rules.append(f"M{x:.0f} {oy:.0f}V{oy + gh:.0f}")
    for j in range(ymax + 1):
        _, y = px(0, j)
        rules.append(f"M{ox:.0f} {y:.0f}H{ox + gw:.0f}")
    body = [f'<path d="{"".join(rules)}" stroke="currentColor" stroke-opacity=".25" '
            f'stroke-width="1"/>']
    x0, y0 = px(0, 0)
    body.append(f'<path d="M{ox:.0f} {y0:.0f}H{ox + gw:.0f}M{x0:.0f} {oy:.0f}V{y0:.0f}" '
                f'stroke="currentColor" stroke-opacity=".85" stroke-width="1.8"/>')
    for i in range(xmax + 1):
        x, _ = px(i, 0)
        body.append(txt(x, y0 + 16, str(i), 11, op=".7"))
    for j in range(1, ymax + 1):
        _, y = px(0, j)
        body.append(txt(x0 - 12, y + 4, str(j), 11, op=".7"))
    for lab, (x, y) in points.items():
        cx, cy = px(x, y)
        if dots:
            body.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="4" fill="currentColor" '
                        f'fill-opacity=".9"/>')
        body.append(txt(cx + 12, cy - 7, lab, 14))
    return svg("".join(body), vb=f"0 0 {vw} {vh:.0f}")


# ------------------------------------------------------------------ growing patterns
def tile_stages(cellsets, labels=None, size=17, gap=24, vw=340, pad=12):
    """Draw successive stages of a growing tile pattern, side by side and bottom-aligned.

    cellsets: one list of (col, row) per stage, row 0 at the bottom.

    The count a question asks for comes from `len(cells)` on the very list drawn here, so
    a pattern cannot show one number of tiles and be marked against another. Cells are
    emitted as a single <path> — a five-stage pattern drawn as separate <rect> elements
    runs past the 3.5 KB budget figure_svg_errors enforces.
    """
    labels = labels or [f"Stage {i + 1}" for i in range(len(cellsets))]
    if len(labels) != len(cellsets):
        raise ValueError("one label per stage")
    widths = [(max(c for c, _ in s) + 1) * size for s in cellsets]
    heights = [(max(r for _, r in s) + 1) * size for s in cellsets]
    total = sum(widths) + gap * (len(cellsets) - 1)
    vh = max(heights) + 2 * pad + 22
    ox = (vw - total) / 2
    base = pad + max(heights)

    d, texts = [], []
    for cells, lab, w in zip(cellsets, labels, widths):
        for c, r in cells:
            x, y = ox + c * size, base - (r + 1) * size
            d.append(f"M{x:.0f} {y:.0f}h{size}v{size}h-{size}z")
        texts.append(txt(ox + w / 2, base + 17, lab, 11, op=".75"))
        ox += w + gap
    body = (f'<path d="{"".join(d)}" stroke="currentColor" stroke-opacity=".85" '
            f'stroke-width="1.6" fill="currentColor" fill-opacity=".08"/>' + "".join(texts))
    return svg(body, vb=f"0 0 {vw} {vh:.0f}")


# ------------------------------------------------------------------ charts
def _axes(ox, oy, w, h, ymax, ystep, ylabel_every=1):
    """Axis lines, horizontal gridlines and y-axis numbers, as one path plus texts."""
    rules, texts = [], []
    n = int(round(ymax / ystep))
    for i in range(n + 1):
        y = oy + h - (i * ystep / ymax) * h
        rules.append(f"M{ox:.0f} {y:.0f}H{ox + w:.0f}")
        if i % ylabel_every == 0:
            texts.append(txt(ox - 10, y + 4, f"{i * ystep:g}", 10, anchor="end", op=".7"))
    grid = (f'<path d="{"".join(rules)}" stroke="currentColor" stroke-opacity=".18" '
            f'stroke-width="1"/>')
    axis = (f'<path d="M{ox:.0f} {oy:.0f}V{oy + h:.0f}H{ox + w:.0f}" stroke="currentColor" '
            f'stroke-opacity=".8" stroke-width="1.6"/>')
    return grid + axis + "".join(texts)


def bar_chart(labels, values, ystep=None, vw=340, h=132, pad_l=34, pad_r=10, pad_t=12):
    """A column graph. Bars are drawn from the same values the question reasons about.

    ystep defaults to something that gives 4-6 gridlines for the data given.
    """
    if len(labels) != len(values):
        raise ValueError("one label per bar")
    top = max(values)
    if ystep is None:
        ystep = next(s for s in (1, 2, 5, 10, 20, 25, 50, 100, 200, 500)
                     if top / s <= 6)
    ymax = ystep * int(-(-top // ystep))
    w = vw - pad_l - pad_r
    ox, oy = pad_l, pad_t
    body = [_axes(ox, oy, w, h, ymax, ystep)]
    slot = w / len(values)
    bw = slot * 0.56
    d = []
    for i, v in enumerate(values):
        bh = (v / ymax) * h
        x = ox + slot * i + (slot - bw) / 2
        d.append(f"M{x:.1f} {oy + h - bh:.1f}h{bw:.1f}v{bh:.1f}h-{bw:.1f}z")
    body.append(f'<path d="{"".join(d)}" stroke="currentColor" stroke-opacity=".85" '
                f'stroke-width="1.5" fill="currentColor" fill-opacity=".22"/>')
    for i, lab in enumerate(labels):
        body.append(txt(ox + slot * i + slot / 2, oy + h + 15, lab, 10.5, op=".8"))
    return svg("".join(body), vb=f"0 0 {vw} {h + pad_t + 24}")


def line_graph(labels, series, ystep=None, vw=340, h=130, pad_l=34, pad_r=12, pad_t=12):
    """A line graph. `series` is one list of values, or {name: values} for two lines."""
    if not isinstance(series, dict):
        series = {"": series}
    top = max(max(v) for v in series.values())
    if ystep is None:
        ystep = next(s for s in (1, 2, 5, 10, 20, 25, 50, 100) if top / s <= 6)
    ymax = ystep * int(-(-top // ystep))
    w = vw - pad_l - pad_r
    ox, oy = pad_l, pad_t
    body = [_axes(ox, oy, w, h, ymax, ystep)]
    step = w / (len(labels) - 1)
    for si, (name, vals) in enumerate(series.items()):
        pts = [(ox + step * i, oy + h - (v / ymax) * h) for i, v in enumerate(vals)]
        dash = ' stroke-dasharray="5 3"' if si else ""
        body.append(f'<path d="M' + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) +
                    f'" stroke="currentColor" stroke-opacity=".9" stroke-width="2"{dash}/>')
        body.append("".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="currentColor" '
                            f'fill-opacity=".9"/>' for x, y in pts))
        if name:
            # Legend inside the top-left of the plot, each name preceded by a sample of
            # its own line style. Names alone at the right-hand end sat on top of the
            # data and left no way to tell which line was the dashed one.
            ly = oy + 11 + si * 14
            body.append(f'<path d="M{ox + 6:.0f} {ly:.0f}h16" stroke="currentColor" '
                        f'stroke-opacity=".9" stroke-width="2"{dash}/>')
            body.append(txt(ox + 27, ly + 4, name, 10.5, anchor="start", op=".85"))
    for i, lab in enumerate(labels):
        body.append(txt(ox + step * i, oy + h + 15, lab, 10.5, op=".8"))
    return svg("".join(body), vb=f"0 0 {vw} {h + pad_t + 24}")


def pie_chart(parts, r=62, vw=340, vh=None, lab_gap=24):
    """A pie chart from (label, count) pairs. Sector angles come from the counts, so a
    sector labelled a quarter is a quarter.

    The canvas is sized from the label ring rather than fixed: at vh=170 a sector whose
    midpoint fell near six o'clock put its label below the viewBox and it was clipped
    away entirely. Only rendering showed it — the SVG was valid and under budget.
    """
    total = sum(c for _, c in parts)
    if vh is None:
        vh = 2 * (r + lab_gap) + 30
    cx, cy = vw / 2, vh / 2
    body, ang = [], -90.0
    for lab, c in parts:
        sweep = 360 * c / total
        a0, a1 = math.radians(ang), math.radians(ang + sweep)
        x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
        x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        large = 1 if sweep > 180 else 0
        body.append(f'<path d="M{cx:.1f} {cy:.1f}L{x0:.1f} {y0:.1f}'
                    f'A{r} {r} 0 {large} 1 {x1:.1f} {y1:.1f}Z" stroke="currentColor" '
                    f'stroke-opacity=".85" stroke-width="1.6" fill="currentColor" '
                    f'fill-opacity="{0.06 + 0.05 * len(body):.2f}"/>')
        am = math.radians(ang + sweep / 2)
        body.append(txt(cx + (r + lab_gap) * math.cos(am),
                        cy + (r + lab_gap) * math.sin(am) + 4, lab, 11.5))
        ang += sweep
    return svg("".join(body), vb=f"0 0 {vw} {vh}")
