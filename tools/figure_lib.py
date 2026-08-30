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
            # An empty cell still costs ~40 bytes as <text></text>, and a blank logic-grid
            # is mostly empty cells — enough to push a 5-column grid past the size budget.
            if str(cell).strip():
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


# ------------------------------------------------------------------ figural reasoning
def shapes_row(cellsets, labels=None, size=17, gap=26, vw=340, pad=12, marks=None):
    """Draw several polyomino shapes side by side, bottom-aligned, each with a caption.

    cellsets: one list of (col, row) per shape, row 0 at the bottom.
    marks:    optional {shape_index: {(col, row): "X"}} to letter a particular square.

    Like tile_stages, but for shapes that are alternatives or components rather than
    successive stages of one pattern — and it can mark a named square, which is what a
    rotation question needs to ask about.
    """
    labels = labels or [chr(65 + i) for i in range(len(cellsets))]
    if len(labels) != len(cellsets):
        raise ValueError("one label per shape")
    marks = marks or {}
    widths = [(max(c for c, _ in s) + 1) * size for s in cellsets]
    heights = [(max(r for _, r in s) + 1) * size for s in cellsets]
    total = sum(widths) + gap * (len(cellsets) - 1)
    if total > vw - 8:
        raise ValueError(f"shapes need {total:.0f}px, canvas is {vw}")
    vh = max(heights) + 2 * pad + 22
    ox = (vw - total) / 2
    base = pad + max(heights)

    d, texts = [], []
    for i, (cells, lab, w) in enumerate(zip(cellsets, labels, widths)):
        for c, r in cells:
            x, y = ox + c * size, base - (r + 1) * size
            d.append(f"M{x:.0f} {y:.0f}h{size}v{size}h-{size}z")
            m = marks.get(i, {}).get((c, r))
            if m:
                texts.append(txt(x + size / 2, y + size / 2 + 5, m, 12))
        texts.append(txt(ox + w / 2, base + 17, lab, 11, op=".75"))
        ox += w + gap
    body = (f'<path d="{"".join(d)}" stroke="currentColor" stroke-opacity=".85" '
            f'stroke-width="1.6" fill="currentColor" fill-opacity=".08"/>' + "".join(texts))
    return svg(body, vb=f"0 0 {vw} {vh:.0f}")


def rotate_cells(cells, quarter_turns=1):
    """Rotate a cell set a quarter turn clockwise, `quarter_turns` times, and re-seat it
    at the origin. Answers about rotation are computed from this rather than pictured."""
    cs = list(cells)
    for _ in range(quarter_turns % 4):
        cs = [(r, -c) for c, r in cs]
        mc, mr = min(c for c, _ in cs), min(r for _, r in cs)
        cs = [(c - mc, r - mr) for c, r in cs]
    return sorted(cs)


# Which of the seven segments each digit lights. a=top, b=top-right, c=bottom-right,
# d=bottom, e=bottom-left, f=top-left, g=middle.
SEGMENTS = {
    "0": "abcdef", "1": "bc", "2": "abdeg", "3": "abcdg", "4": "bcfg",
    "5": "acdfg", "6": "acdefg", "7": "abc", "8": "abcdefg", "9": "abcdfg",
}


def seven_segment(digits, dead=(), w=34, h=58, gap=16, vw=340, pad=14, t=6):
    """Draw digits on a seven-segment display, with `dead` segments never lighting.

    dead: segment letters that are broken, e.g. ("a", "f"). A dead segment is drawn faintly
    so the reader can see the display has seven segments and which are unlit — otherwise
    the question is unanswerable, because a missing stroke and an absent stroke look alike.
    """
    n = len(digits)
    total = n * w + (n - 1) * gap
    ox, oy = (vw - total) / 2, pad
    vh = h + 2 * pad
    on, off = [], []
    for i, ch in enumerate(digits):
        x = ox + i * (w + gap)
        lit = set(SEGMENTS[ch]) - set(dead)
        geo = {
            "a": f"M{x + t} {oy}h{w - 2 * t}",
            "b": f"M{x + w} {oy + t}v{h / 2 - 1.5 * t}",
            "c": f"M{x + w} {oy + h / 2 + 0.5 * t}v{h / 2 - 1.5 * t}",
            "d": f"M{x + t} {oy + h}h{w - 2 * t}",
            "e": f"M{x} {oy + h / 2 + 0.5 * t}v{h / 2 - 1.5 * t}",
            "f": f"M{x} {oy + t}v{h / 2 - 1.5 * t}",
            "g": f"M{x + t} {oy + h / 2}h{w - 2 * t}",
        }
        for seg, path in geo.items():
            (on if seg in lit else off).append(path)
    body = (f'<path d="{"".join(off)}" stroke="currentColor" stroke-opacity=".13" '
            f'stroke-width="{t}" stroke-linecap="round"/>'
            f'<path d="{"".join(on)}" stroke="currentColor" stroke-opacity=".9" '
            f'stroke-width="{t}" stroke-linecap="round"/>')
    return svg(body, vb=f"0 0 {vw} {vh:.0f}")


def symbol_grid(rows, size=30, vw=340, pad=10, shade=()):
    """A grid of symbols — the repeating-pattern and tessellation stimulus.

    rows:  list of rows, each a list of one- or two-character symbols ("" for empty).
    shade: {(row, col)} to fill, for "the shaded tile" questions.
    """
    nr, nc = len(rows), max(len(r) for r in rows)
    ox, oy = (vw - nc * size) / 2, pad
    vh = nr * size + 2 * pad
    fills = ""
    if shade:
        d = "".join(f"M{ox + c * size:.0f} {oy + r * size:.0f}h{size}v{size}h-{size}z"
                    for r, c in shade)
        fills = f'<path d="{d}" fill="currentColor" fill-opacity=".16"/>'
    rules = []
    for r in range(nr + 1):
        rules.append(f"M{ox:.0f} {oy + r * size:.0f}h{nc * size}")
    for c in range(nc + 1):
        rules.append(f"M{ox + c * size:.0f} {oy:.0f}v{nr * size}")
    grid = (f'<path d="{"".join(rules)}" stroke="currentColor" stroke-opacity=".55" '
            f'stroke-width="1.3"/>')
    texts = "".join(
        f'<text x="{ox + c * size + size / 2:.0f}" y="{oy + r * size + size / 2 + 6:.0f}" '
        f'font-family="system-ui,sans-serif" font-size="15" fill="currentColor" '
        f'text-anchor="middle">{s}</text>'
        for r, row in enumerate(rows) for c, s in enumerate(row) if s)
    return svg(fills + grid + texts, vb=f"0 0 {vw} {vh:.0f}")


# ------------------------------------------------------------------ four-quadrant plane
def _seg_box_gap(seg, bx0, by0, bx1, by1):
    """Shortest distance from a segment to a box, 0 if it passes through."""
    (x1, y1), (x2, y2) = seg
    best = 1e9
    steps = 40
    for i in range(steps + 1):
        t = i / steps
        px, py = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
        dx = max(bx0 - px, 0, px - bx1)
        dy = max(by0 - py, 0, py - by1)
        best = min(best, (dx * dx + dy * dy) ** 0.5)
    return best


def _faint_ink(svg_text):
    """Just the watermark-opacity elements, so they can be told from real ink."""
    keep = [m.group(0) for m in
            re.finditer(r"<(?:line|path|rect|circle|ellipse|polygon|polyline)\b[^>]*>",
                        svg_text)]
    out = []
    for tag in keep:
        op = re.search(r"stroke-opacity=[\'\"]([\d.]+)", tag)
        if op and float(op.group(1)) <= 0.25:
            out.append(tag)
    return "<svg>" + "".join(out) + "</svg>"


def _label_w(text, size):
    """Rendered width of a label, from the same Arial advance widths the checks use.

    There were three copies of `len(text) * size * 0.55` in this codebase and all
    three called it a quarter narrow. It is not: it is right on average and wrong per
    label -- "W" is 0.944 em and "l" is 0.222 -- which is the wrong shape of error for
    deciding whether a label fits. One table, in `question_checks`, imported here
    lazily because that module reaches back into this one.
    """
    from tools.question_checks import text_width
    return text_width(text, size)


def _label_offset(ux, uy, text, size=13, gap=10.0):
    """Push a label out until its NEAREST EDGE clears the point by `gap`.

    "the question mark should be closer to the fourth vertex because right now it
    looks like its sat on -2,0." The offset used to be a fixed 30 px measured to the
    label's CENTRE -- right for the six-character "(3, 0)", whose near edge then
    lands 8 px from its dot, and a whole grid cell too far for a one-character "?",
    which landed squarely on the neighbouring lattice point.

    A label's distance from its point is a property of its EDGE, so that is what is
    held constant. "(3, 0)" barely moves; "?" comes in by half a cell.
    """
    n = max((ux * ux + uy * uy) ** 0.5, 1e-9)
    ux, uy = ux / n, uy / n
    hw, top, bot = _label_w(text, size) / 2, size * 0.8, size * 0.25
    lo, hi = 0.0, 120.0
    for _ in range(40):
        t = (lo + hi) / 2
        cx, cy = ux * t, uy * t
        dx = max(cx - hw, 0.0, -(cx + hw))
        dy = max(cy - top, 0.0, -(cy + bot))
        if (dx * dx + dy * dy) ** 0.5 < gap:
            lo = t
        else:
            hi = t
    return ux * hi, uy * hi


def plane(points=None, lines=None, polygon=None, xr=(-4, 4), yr=(-4, 4), cell=30,
          pad=22, dots=True, label_off=(11, -8), segments=None, extra=None):
    """A four-quadrant coordinate plane where everything derives from one mapping.

    coord_grid covers the first quadrant only, and every figure in VIC round 5 that a
    reviewer flagged needed negative coordinates. Those figures were drawn by hand, and
    each one drifted in its own direction: a point plotted a whole unit low, two lines
    that miss the intercepts they are labelled with, a y-axis drawn outside the square
    it should have cut through, tick labels implying 13 px per unit on one side of a
    figure and 24 on the other.

    Every one of those is impossible here, because the axes, the ticks, the gridlines,
    the dots and the lines are all placed by px() and there is no second opinion about
    where a unit is. That is the point of this function -- not tidiness.

    points:   {"B": (-2, 3)}         dots, labelled
              [(1, 1), (2, 3)]       dots the student must read off the grid
    lines:    [((0, 4), (4, 0))]     drawn THROUGH both points, clipped to the plane
    segments: [((0, 2), (4, 4))]     drawn BETWEEN the two points and stopped there
    polygon:  [(-1, 4), (3, 4), ...] closed outline
    extra:    f(px) -> svg           anything else this figure needs -- a dashed
                                     auxiliary line, an angle arc, a curve. It is
                                     handed the SAME px() everything else is placed
                                     by, so an addition cannot land on its own scale.

    A SEGMENT IS NOT A LINE. `lines` extends through both points to the edge of the
    plane, which is right for "the line through A and B" and wrong for "line segment
    PQ" -- a question asking for the midpoint of PQ drawn as an endless line has no
    PQ in it. They are separate arguments because they are separate objects.
    """
    x0, x1 = xr
    y0, y1 = yr
    gw, gh = (x1 - x0) * cell, (y1 - y0) * cell
    # The y label is drawn at oy - 14 with a 12 px font, so its box reaches
    # oy - 24. A pad of 22 left it two pixels above the canvas and the browser
    # cut the top off it -- found the day `text_outside_the_canvas` learned to
    # look at all four edges, in this function's own output.
    pad = max(pad, 26)
    ox, oy = pad + 16, pad
    vw, vh = gw + 2 * pad + 30, gh + 2 * pad + 20

    def px(x, y):
        return ox + (x - x0) * cell, oy + (y1 - y) * cell

    ax, ay = px(0, 0)

    # Lines are resolved to pixels FIRST, because where they run decides which side of
    # each axis its numbers can safely go. Drawing the labels first is how a line ended
    # up printed through the "-6" that names its own intercept.
    drawn = []
    for (pa, pb) in (segments or []):
        drawn.append((px(*pa), px(*pb)))
    for (pa, pb) in (lines or []):
        (ux, uy), (vx, vy) = pa, pb
        if ux == vx:
            drawn.append((px(ux, y0), px(ux, y1)))
            continue
        m = (vy - uy) / (vx - ux)
        cand = [(x0, uy + m * (x0 - ux)), (x1, uy + m * (x1 - ux))]
        if m != 0:
            cand += [((y0 - uy) / m + ux, y0), ((y1 - uy) / m + ux, y1)]
        inside = sorted(c for c in cand
                        if x0 - 1e-9 <= c[0] <= x1 + 1e-9 and y0 - 1e-9 <= c[1] <= y1 + 1e-9)
        if len(inside) >= 2:
            drawn.append((px(*inside[0]), px(*inside[-1])))

    b = []
    rules = []
    for i in range(x0, x1 + 1):
        x, _ = px(i, 0)
        rules.append(f"M{x:.0f} {oy:.0f}V{oy + gh:.0f}")
    for j in range(y0, y1 + 1):
        _, y = px(0, j)
        rules.append(f"M{ox:.0f} {y:.0f}H{ox + gw:.0f}")
    b.append(f'<path d="{"".join(rules)}" stroke="currentColor" stroke-opacity=".18" '
             f'stroke-width="1" fill="none"/>')

    b.append(f'<path d="M{ox:.0f} {ay:.0f}H{ox + gw + 12:.0f}M{ax:.0f} {oy + gh:.0f}'
             f'V{oy - 12:.0f}" stroke="currentColor" stroke-width="1.6"/>')
    b.append(f'<polygon points="{ox + gw + 12:.0f},{ay - 4:.0f} {ox + gw + 19:.0f},'
             f'{ay:.0f} {ox + gw + 12:.0f},{ay + 4:.0f}" fill="currentColor"/>')
    b.append(f'<polygon points="{ax - 4:.0f},{oy - 12:.0f} {ax:.0f},{oy - 19:.0f} '
             f'{ax + 4:.0f},{oy - 12:.0f}" fill="currentColor"/>')

    # Tick marks ride in one path with the numbers placed off the same coordinate, so a
    # gridline, a mark and a label cannot drift apart -- the defect that made every
    # point on one flagged figure read 0.125 units off. gridlines_off_the_ticks reads
    # short path segments as marks, so folding them in costs the check nothing.
    marks = []
    for i in range(x0, x1 + 1):
        if i:
            x, _ = px(i, 0)
            marks.append(f"M{x:.0f} {ay - 4:.0f}V{ay + 4:.0f}")
    for j in range(y0, y1 + 1):
        if j:
            _, y = px(0, j)
            marks.append(f"M{ax - 4:.0f} {y:.0f}H{ax + 4:.0f}")
    b.append(f'<path d="{"".join(marks)}" stroke="currentColor" stroke-width="1.4"/>')

    # WHAT A TICK NUMBER HAS TO KEEP CLEAR OF is everything the figure draws in real
    # ink, not only the lines passed in `lines`. The polygon's edges are content, and
    # so is whatever `extra` draws -- a parabola, a construction line, an angle arc.
    # Leaving those out put a "−1" on a parabola and a "3" on a triangle's side, both
    # in this function's own output, both caught by the check afterwards.
    content = list(drawn)
    if polygon:
        _pp = [px(*q) for q in polygon]
        content += [(_pp[i], _pp[(i + 1) % len(_pp)]) for i in range(len(_pp))]
    extra_svg = extra(px) if extra else ""
    if extra_svg:
        content += figure_outlines(extra_svg)

    def clear(bx0, by0, bx1, by1):
        return min([_seg_box_gap(s, bx0, by0, bx1, by1) for s in content] or [99])

    # At small cell sizes the x-axis "-1" and the y-axis "-1" sit in the same corner and
    # print over each other: the x label is centred at ax-cell and the y label ends at
    # ax-9, and their boxes intersect for any cell under about 22 px. Labelling alternate
    # ticks is what a real graph does at that scale, and it costs bytes rather than
    # spending them. Tick MARKS stay on every unit, so nothing is unreadable.
    # Decided PER AXIS. Thinning a short axis leaves it with one or two numbers, and
    # _axis_ticks needs three to fit a mapping -- so the figure stops being verifiable,
    # which is a worse fault than the collision this avoids.
    def thin(lo, hi):
        """Every unit, or every second one if consecutive numbers would touch.

        The threshold used to be `cell < 22`, guessed rather than measured. At cell=24
        a "−1" and a "1" still overlap by 4 px, because what decides it is the WIDTH of
        the widest number on the axis and not the cell size -- "−10" is two and a half
        times as wide as "1". Measure the widest label and compare it with the spacing
        it has to live in.
        """
        every = [v for v in range(lo, hi + 1) if v]
        if not every:
            return every
        widest = max(_label_w(str(v).replace("-", "\u2212"), 10) for v in every)
        alt = [v for v in every if v % 2 == 0]
        return alt if (widest + 3 > cell and len(alt) >= 3) else every
    xs, ys = thin(x0, x1), thin(y0, y1)
    # WHICH SIDE OF EACH AXIS THE NUMBERS GO, decided by trying every arrangement and
    # measuring, rather than by scoring the two axes independently. Scoring them apart
    # cannot see the one collision that actually happens: near the origin the x-axis
    # "−1" and the y-axis "1" are a few pixels apart whatever each axis prefers on its
    # own, and a plotted line through the origin sits on top of both. So enumerate --
    # above/below, left/right, near/far -- and keep the first arrangement where no
    # number touches another number and none is struck through by a drawn line.
    def boxes_for(xdy, ydx, yanch):
        out = []
        for i in xs:
            x, _ = px(i, 0)
            w = _label_w(str(i).replace("-", "\u2212"), 10)
            out.append((x - w / 2, ay + xdy - 8, x + w / 2, ay + xdy + 2,
                        str(i).replace("-", "\u2212")))
        for j in ys:
            _, y = px(0, j)
            w = _label_w(str(j).replace("-", "\u2212"), 10)
            x = ax + ydx
            x0b = x - w if yanch == "end" else x
            out.append((x0b, y - 4, x0b + w, y + 6, str(j).replace("-", "\u2212")))
        return out

    def cost(xdy, ydx, yanch):
        bx = boxes_for(xdy, ydx, yanch)
        bad = 0
        for k in range(len(bx)):
            for l in range(k + 1, len(bx)):
                if (min(bx[k][2], bx[l][2]) - max(bx[k][0], bx[l][0]) > 0
                        and min(bx[k][3], bx[l][3]) - max(bx[k][1], bx[l][1]) > 0):
                    bad += 4
        for b0, b1, b2, b3, _t in bx:
            if clear(b0, b1, b2, b3) <= 0:
                bad += 1
        return bad

    best = None
    for xdy in (16, -9, 22, -15):
        for ydx, yanch in ((-9, "end"), (9, "start"), (-15, "end"), (15, "start")):
            c = cost(xdy, ydx, yanch)
            if best is None or c < best[0]:
                best = (c, xdy, ydx, yanch)
            if c == 0:
                break
        if best[0] == 0:
            break
    _c, xdy, ydx, yanch = best
    left = right = 99
    xanch = "middle"

    # Shared attributes ride on a <g>; x, y, font-size and text-anchor stay on each
    # <text> because question_checks._text_box reads all four off the tag to size a
    # label's box. Hoisting text-anchor would make every centred number measure as if
    # it started where it actually centres, and the overlap checks would quietly
    # mis-box the whole figure.
    def tick(x, y, s, anchor):
        """One tick number. It is emitted TWICE, into two <g> layers -- see below."""
        return (f'<text x="{x:.0f}" y="{y:.0f}" font-size="10" '
                f'text-anchor="{anchor}">{s}</text>')

    # AND THEN PER LABEL. The arrangement above is chosen for the axis as a whole,
    # which cannot help the one or two numbers a plotted line happens to run through
    # -- a segment from (−2, 3) to (4, −5) crosses the tick row twice wherever the row
    # sits. A tick may cross its own axis freely: it stays level with the mark it
    # names, so the scale is untouched. So any number still struck through goes to the
    # other side on its own.
    other_x = -9 if xdy > 0 else 16
    other_y = (9, "start") if ydx < 0 else (-9, "end")
    ROOM = 2.5
    lab = []
    tickboxes = []

    def free_of_ticks(b):
        """No placed tick number already occupies this box."""
        return not any(min(b[2], t[2]) - max(b[0], t[0]) > -1
                       and min(b[3], t[3]) - max(b[1], t[1]) > -1 for t in tickboxes)

    dropped_x = dropped_y = 0
    for i in xs:
        x, _ = px(i, 0)
        t = str(i).replace("-", "\u2212")
        w = _label_w(t, 10)
        dy0 = xdy
        # ROOM, not merely absence of contact. `text_overlaps_geometry` measures the
        # rendered box -- baseline plus font size, real advance widths -- and a
        # half-pixel gap by this estimate is a hit by that one. Ask for daylight.
        bn = (x - w / 2, ay + dy0 - 9, x + w / 2, ay + dy0 + 3)
        ba = (x - w / 2, ay + other_x - 9, x + w / 2, ay + other_x + 3)
        here = clear(*bn) if free_of_ticks(bn) else -99
        there = clear(*ba) if free_of_ticks(ba) else -99
        if here < ROOM <= there:
            dy0, here = other_x, there
        # NEITHER SIDE IS CLEAR: the plotted line crosses the tick row here, so this
        # number cannot be printed anywhere near its own mark without being struck
        # through. Print the MARK and drop the NUMBER -- which is what a graph does,
        # and is honest, where moving it away from its mark would not be. Only while
        # four numbers remain, since three is what fitting a scale needs.
        if here < ROOM and len(xs) - dropped_x > 4:
            dropped_x += 1
            continue
        tickboxes.append((x - w / 2, ay + dy0 - 9, x + w / 2, ay + dy0 + 3))
        lab.append(tick(x, ay + dy0, t, xanch))
    for j in ys:
        _, y = px(0, j)
        t = str(j).replace("-", "\u2212")
        w = _label_w(t, 10)
        dx0, an = ydx, yanch
        b_now = (ax + dx0 - (w if an == "end" else 0), y - 5,
                 ax + dx0 + (0 if an == "end" else w), y + 7)
        alt_dx, alt_an = other_y
        b_alt = (ax + alt_dx - (w if alt_an == "end" else 0), y - 5,
                 ax + alt_dx + (0 if alt_an == "end" else w), y + 7)
        here = clear(*b_now) if free_of_ticks(b_now) else -99
        there = clear(*b_alt) if free_of_ticks(b_alt) else -99
        if here < ROOM <= there:
            dx0, an, here = alt_dx, alt_an, there
        if here < ROOM and len(ys) - dropped_y > 4:
            dropped_y += 1
            continue
        tickboxes.append((ax + dx0 - (w if an == "end" else 0), y - 5,
                          ax + dx0 + (0 if an == "end" else w), y + 7))
        lab.append(tick(ax + dx0, y + 4, t, an))
    # The "O" sits in the corner between the two tick columns and is the first thing to
    # collide when they crowd. It names something every reader can already see, so at
    # tight scales it simply goes.
    if cell >= 24:
        _ow = _label_w("O", 10)
        for _ox2, _oanch in ((ax - 9, "end"), (ax + 9, "start")):
            _b = (_ox2 - (_ow if _oanch == "end" else 0), ay + 6,
                  _ox2 + (0 if _oanch == "end" else _ow), ay + 18)
            if clear(*_b) >= ROOM and free_of_ticks(_b):
                tickboxes.append(_b)
                lab.append(tick(_ox2, ay + 15, "O", _oanch))
                break
        # else: no room on either side. The origin is the one label every reader can
        # already find, so it goes rather than being printed through.
    # HALOED, IN TWO LAYERS. A four-quadrant plane puts its tick numbers INSIDE the
    # grid whenever the axis is not at an edge, so a gridline runs through every one of
    # them -- "Why are there thin grid lines behind the numbers?" A page-coloured
    # stroke behind the glyphs is what a real graph does about it, and both text checks
    # read a label drawn twice at one spot as one label rather than as a collision.
    #
    # The stroke colour is the PAGE, which is the one thing `currentColor` cannot be:
    # currentColor IS the ink. Written plainly as #fff, not as a CSS variable: a
    # browser resolves `var(--x,#fff)` and CAIROSVG DOES NOT -- it raises on the whole
    # document, and cairosvg is the renderer every contact sheet in this project is
    # made with. A figure it cannot parse is a figure nobody can look at, which is the
    # one thing this round has shown matters most. `figure_svg_errors` refuses a CSS
    # function in a paint attribute now, so this cannot come back. Hoisting the stroke
    # to the group keeps the halo from doubling the figure's size -- each <text> still
    # carries its own x, y, font-size and text-anchor, because `_text_box` reads all
    # four off the tag and would mis-box every number if they were hoisted too.
    b.append(f'<g font-family="system-ui,sans-serif" stroke="#fff" '
             f'stroke-width="3" stroke-linejoin="round" fill="none" '
             f'aria-hidden="true">{"".join(lab)}</g>')
    b.append(f'<g font-family="system-ui,sans-serif" fill="currentColor" '
             f'fill-opacity=".75">{"".join(lab)}</g>')
    b.append(txt(ox + gw + 20, ay + 14, "x", 12, "middle", ".9"))
    b.append(txt(ax + 13, oy - 14, "y", 12, "middle", ".9"))

    if polygon:
        pts = " ".join(f"{a:.0f},{c:.0f}" for a, c in (px(*q) for q in polygon))
        b.append(f'<polygon points="{pts}" fill="currentColor" fill-opacity=".12" '
                 f'stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>')

    for (a, c), (d, e) in drawn:
        b.append(f'<line x1="{a:.0f}" y1="{c:.0f}" x2="{d:.0f}" y2="{e:.0f}" '
                 f'stroke="currentColor" stroke-width="2" stroke-opacity=".9"/>')

    lx, ly = label_off
    # A vertex label belongs OUTSIDE its shape. Placed by a fixed offset they landed
    # inside the square -- the "?" naming the answer printed over the very edge that
    # leads to it -- which is the same fault the reviewer raised against a triangle:
    # "put the figure's dimension outside the triangle". Push each label away from the
    # polygon's centre instead, by its own WIDTH: see _label_offset.
    cen = None
    if polygon:
        cen = (sum(q[0] for q in polygon) / len(polygon),
               sum(q[1] for q in polygon) / len(polygon))
    pts = points or {}
    # A list plots bare dots the student has to read off the grid -- one flagged
    # question shows three points and names none of them. A dict keyed on "" would
    # collapse them into one, so carry pairs rather than a mapping.
    if extra_svg:
        b.append(extra_svg)
    pairs = list(pts.items()) if isinstance(pts, dict) else [("", q) for q in pts]
    plab = []
    placed = []                     # boxes of the point labels already written
    # EVERYTHING ALREADY DRAWN, read back off the figure rather than listed by hand.
    # The hand-written list was axes + plotted lines + tick marks, which is most of a
    # figure and not all of it: a vertex label went straight over the polygon edge it
    # belongs to, and another over a parabola drawn by `extra`. Ask the drawing.
    _body = "".join(b)
    _faint = {(tuple(u), tuple(v)) for u, v in figure_outlines(_faint_ink(_body))}
    solid = [sg for sg in figure_outlines(_body)
             if (tuple(sg[0]), tuple(sg[1])) not in _faint]
    for name, (x, y) in pairs:
        cx, cy = px(x, y)
        if dots:
            b.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="4.5" fill="currentColor"/>')
        if name.strip():
            if cen is None and drawn:
                # No polygon to push away from, but there are LINES -- and a point
                # named on a line has its label sitting along that line if the
                # offset is a fixed up-and-right. Push perpendicular to the nearest
                # drawn line instead, on whichever side has more room.
                near = min(drawn, key=lambda s: _dist_point_seg((cx, cy), *s))
                (sx1, sy1), (sx2, sy2) = near
                vx, vy = sx2 - sx1, sy2 - sy1
                n = max((vx * vx + vy * vy) ** 0.5, 1e-9)
                nx, ny = -vy / n, vx / n
                if ox + gw / 2 - cx < 0:
                    nx, ny = -nx, -ny
                dx, dy = _label_offset(nx, ny, name)
            elif cen is None:
                dx, dy = lx, ly
            else:
                vx, vy = x - cen[0], y - cen[1]
                n = max((vx * vx + vy * vy) ** 0.5, 1e-9)
                ux, uy = vx / n, -vy / n
                # A vertex sitting ON an axis has the axis's own numbers directly
                # outward of it, so "outward" collides with the tick row: (3, 0) landed
                # on the "3" beneath it. Send those labels along the axis instead.
                if y == 0:
                    ux, uy = (1 if vx >= 0 else -1), -0.4
                elif x == 0:
                    ux, uy = (1 if vx >= 0 else -1), (-0.4 if vy >= 0 else 0.5)
                dx, dy = _label_offset(ux, uy, name)
            # WHEREVER IT LANDS, IT MUST NOT LAND ON A LINE. The rules above choose a
            # DIRECTION well -- outward from the shape, or perpendicular to the line
            # the point sits on -- and then trust it. For a vertex one unit from an
            # axis that is not enough: "A(1,1)" pushed outward from its triangle went
            # straight over the y-axis. Keep the chosen direction if it is clear, and
            # otherwise walk the compass and take the first that is.
            w13 = _label_w(name, 13)

            def free(ddx, ddy):
                bx = (cx + ddx - w13 / 2, cy + ddy - 10,
                      cx + ddx + w13 / 2, cy + ddy + 3)
                if not (ox - 12 <= bx[0] and bx[2] <= ox + gw + 26
                        and oy - 12 <= bx[1] and bx[3] <= oy + gh + 22):
                    return -99
                for tb in tickboxes + placed:
                    if (min(bx[2], tb[2]) - max(bx[0], tb[0]) > -1
                            and min(bx[3], tb[3]) - max(bx[1], tb[1]) > -1):
                        return -99
                return min(_seg_box_gap(sg, *bx) for sg in solid)

            if free(dx, dy) < 3:
                ring = [(1, -0.4), (1, 0.5), (-1, -0.4), (-1, 0.5), (0, -1), (0, 1),
                        (0.7, -0.7), (-0.7, -0.7), (0.7, 0.7), (-0.7, 0.7)]
                best = (free(dx, dy), dx, dy)
                for ux2, uy2 in ring:
                    cdx, cdy = _label_offset(ux2, uy2, name)
                    g = free(cdx, cdy)
                    if g > best[0]:
                        best = (g, cdx, cdy)
                    if g >= 3:
                        break
                _g, dx, dy = best
            # Haloed like the tick numbers: a point label sits inside the grid by
            # definition, so a gridline runs under most of them.
            placed.append((cx + dx - _label_w(name, 13) / 2, cy + dy - 10,
                           cx + dx + _label_w(name, 13) / 2, cy + dy + 3))
            plab.append(f'<text x="{cx + dx:.0f}" y="{cy + dy:.0f}" font-size="13" '
                        f'text-anchor="middle">{name}</text>')
    if plab:
        # Haloed like the tick numbers: a point label sits inside the grid by
        # definition, so a gridline runs under most of them.
        b.append(f'<g font-family="system-ui,sans-serif" stroke="#fff" '
                 f'stroke-width="3" stroke-linejoin="round" fill="none" '
                 f'aria-hidden="true">{"".join(plab)}</g>')
        b.append(f'<g font-family="system-ui,sans-serif" fill="currentColor" '
                 f'fill-opacity=".9">{"".join(plab)}</g>')
    return svg("".join(b), vb=f"0 0 {vw:.0f} {vh:.0f}")


# ------------------------------------------------------------------ labelled triangles
def right_triangle(up_len, base_len, corner="C", up="A", right="B", up_label=None,
                   base_label=None, hyp_label=None, angle=None, vw=280, pad=42,
                   max_px=150, midpoint=None, midpoint_label=None):
    """A right triangle drawn to its own side lengths, dimensions outside it.

    Two reviewer rules from VIC round 5 are structural here rather than remembered:

      "For shapes, put the figure's dimension outside the triangle or uniform in every
      shape." Every side label is placed on the outward normal of its own side, so no
      dimension can end up inside the outline and none of them disagree about which
      convention this figure follows.

      "Ensure the angle values are always within the shape and the arc is always present
      without any overlapping." An angle is drawn as an arc at its vertex with the value
      on the bisector INSIDE the triangle, at a radius that keeps it clear of both sides.

    It also fixes the reason those two were flagged at all. figure_proportions_disagree
    exempts triangles -- the longest label is usually a hypotenuse, which spans the
    bounding box diagonally rather than setting it -- so nothing had been checking their
    shape, and one flagged figure drew a 7 cm side HALF AGAIN LONGER than its 24 cm one.
    Here the two legs come from the lengths themselves and cannot disagree with them.
    """
    scale = max_px / max(up_len, base_len)
    uh, bw = up_len * scale, base_len * scale
    # Rounded ONCE, here. Computing the arc from the unrounded corner while the polygon
    # prints the rounded one puts the arc 0.25 px off its own vertex -- two opinions
    # about where a point is, which is the whole defect this round is about.
    cx, cy = float(round(pad)), float(round(pad + uh))   # right-angle corner
    ux, uy = cx, float(round(cy - uh))                   # the vertex above it
    rx, ry = float(round(cx + bw)), cy                   # the vertex to its right
    vw = max(vw, bw + 2 * pad)
    vh = uh + 2 * pad

    b = [f'<polygon points="{cx:.0f},{cy:.0f} {ux:.0f},{uy:.0f} {rx:.0f},{ry:.0f}" '
         f'fill="currentColor" fill-opacity=".07" stroke="currentColor" '
         f'stroke-width="2" stroke-linejoin="round"/>']
    m = 13
    b.append(f'<path d="M{cx:.0f} {cy - m:.0f}H{cx + m:.0f}V{cy:.0f}" fill="none" '
             f'stroke="currentColor" stroke-width="1.5"/>')

    b.append(txt(cx - 13, cy + 15, corner, 14))
    b.append(txt(ux - 13, uy - 4, up, 14))
    b.append(txt(rx + 13, ry + 15, right, 14))

    # Each dimension sits on its side's outward normal: left of the vertical leg, below
    # the base, and out past the hypotenuse on the side away from the right angle.
    if up_label:
        b.append(txt(cx - 20, (cy + uy) / 2 + 4, up_label, 13))
    if base_label:
        b.append(txt((cx + rx) / 2, cy + 22, base_label, 13))
    if hyp_label:
        mx, my = (ux + rx) / 2, (uy + ry) / 2
        nx, ny = (ry - uy), -(rx - ux)           # normal, pointing away from the corner
        n = max((nx * nx + ny * ny) ** 0.5, 1e-9)
        b.append(txt(mx + 26 * nx / n, my + 26 * ny / n + 4, hyp_label, 13))

    # The median to the hypotenuse is its own question type -- "S is the midpoint of PQ
    # and RS = 7.5" -- and it has to be drawn from the same vertices as everything else
    # or it lands off the line it bisects.
    if midpoint:
        mx, my = (ux + rx) / 2, (uy + ry) / 2
        b.append(f'<circle cx="{mx:.0f}" cy="{my:.0f}" r="3.5" fill="currentColor"/>')
        b.append(f'<line x1="{cx:.0f}" y1="{cy:.0f}" x2="{mx:.0f}" y2="{my:.0f}" '
                 f'stroke="currentColor" stroke-width="1.5" stroke-dasharray="5,4"/>')
        b.append(txt(mx + 14, my - 4, midpoint, 14))
        if midpoint_label:
            b.append(txt((cx + mx) / 2 + 4, (cy + my) / 2 + 16, midpoint_label, 13))

    if angle:
        at, text = angle
        vx, vy = {corner: (cx, cy), up: (ux, uy), right: (rx, ry)}[at]
        others = [(a, c) for k, (a, c) in ((corner, (cx, cy)), (up, (ux, uy)),
                                           (right, (rx, ry))) if k != at]
        dirs = []
        for ax, ay in others:
            dx, dy = ax - vx, ay - vy
            n = max((dx * dx + dy * dy) ** 0.5, 1e-9)
            dirs.append((dx / n, dy / n))
        r = 26
        (d1x, d1y), (d2x, d2y) = dirs
        p1 = (vx + r * d1x, vy + r * d1y)
        p2 = (vx + r * d2x, vy + r * d2y)
        sweep = 1 if (d1x * d2y - d1y * d2x) > 0 else 0
        b.append(f'<path d="M{p1[0]:.2f} {p1[1]:.2f} A{r} {r} 0 0 {sweep} '
                 f'{p2[0]:.2f} {p2[1]:.2f}" fill="none" stroke="currentColor" '
                 f'stroke-width="1.6"/>')
        if text:
            bx, by = d1x + d2x, d1y + d2y
            n = max((bx * bx + by * by) ** 0.5, 1e-9)
            # "Ensure the angle values are always within the shape." At a fixed radius a
            # value written into a NARROW angle spills through both sides -- "30°" is
            # 24 px wide and a 30° vertex is only 12 px across at r=44. Step out along
            # the bisector until the wedge is wide enough to hold the text, capped so it
            # cannot walk off the far side of the triangle.
            half = math.acos(max(-1.0, min(1.0, d1x * d2x + d1y * d2y))) / 2
            need = (len(text) * 13 * 0.55) / 2 + 6
            reach = min(
                ((a - vx) ** 2 + (c - vy) ** 2) ** 0.5 for a, c in others)
            rr = max(40.0, min(need / max(math.tan(half), 1e-3), reach * 0.62))
            b.append(txt(vx + rr * bx / n, vy + rr * by / n + 4, text, 13))
    return svg("".join(b), vb=f"0 0 {vw:.0f} {vh:.0f}")


def trapezium(top, bottom, height, top_label=None, bottom_label=None,
              height_label=None, vw=300, pad=40, max_px=190):
    """A trapezium drawn to its stated sides, with the height clear of its own label.

    "the 5 Cm overlaps with the dotted line." The height was dashed straight down the
    middle of the figure and its label written on top of it. The dashed line now sits
    off-centre and the label stands beside it, on the side with the room.
    """
    # ONE scale for all three dimensions. A 1.6x fudge on the height made a 5 cm height
    # taller than a 7 cm base, which figure_proportions_disagree cannot see: it exempts
    # any figure carrying an unknown side, and this one is labelled "b". The exemption
    # is right and it is exactly why the drawing has to be right by construction.
    scale = max_px / max(top, bottom)
    tw, bw, h = top * scale, bottom * scale, height * scale
    cx = pad + max(tw, bw) / 2
    ty, by = pad, pad + h
    tl, tr = cx - tw / 2, cx + tw / 2
    bl, br = cx - bw / 2, cx + bw / 2
    vh = h + 2 * pad
    b = [f'<polygon points="{tl:.0f},{ty:.0f} {tr:.0f},{ty:.0f} {br:.0f},{by:.0f} '
         f'{bl:.0f},{by:.0f}" fill="currentColor" fill-opacity=".07" '
         f'stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>']
    hx = cx + max(tw, bw) * 0.22                 # off-centre, so the label has a side
    b.append(f'<line x1="{hx:.0f}" y1="{ty:.0f}" x2="{hx:.0f}" y2="{by:.0f}" '
             f'stroke="currentColor" stroke-width="1.5" stroke-dasharray="5,4"/>')
    b.append(f'<path d="M{hx:.0f} {by - 12:.0f}H{hx + 12:.0f}V{by:.0f}" fill="none" '
             f'stroke="currentColor" stroke-width="1.4"/>')
    if height_label:
        b.append(txt(hx - 20, (ty + by) / 2 + 4, height_label, 13))
    if top_label:
        b.append(txt(cx, ty - 12, top_label, 13))
    if bottom_label:
        b.append(txt(cx, by + 22, bottom_label, 13))
    return svg("".join(b), vb=f"0 0 {max(vw, max(tw, bw) + 2 * pad):.0f} {vh:.0f}")


# ------------------------------------------------------------------ angle marks
# "For all of the angle-related questions, make sure there is a small angle arc to
# signal this is the angle being mentioned." (VIC review round 6, 2026-08-27.)
#
# Eight angles meet at the two vertices of a transversal crossing two parallel lines.
# A figure that prints a bare "65°" beside one of them and a bare "b" beside another
# has named neither. The stem says "as shown"; nothing is shown.
#
# These derive the mark from the figure's OWN segments -- which lines meet at which
# vertex, and which sector the label is sitting in -- so an arc cannot be drawn on an
# angle other than the one the label already names. That is the same principle as
# `plane` and `right_triangle`: one source for the picture and the words.

_SEG_LINE = re.compile(r"<line[^>]*\bx1=[\'\"]([-\d.]+)[\'\"][^>]*\by1=[\'\"]([-\d.]+)"
                       r"[\'\"][^>]*\bx2=[\'\"]([-\d.]+)[\'\"][^>]*\by2=[\'\"]([-\d.]+)")
_SEG_POLY = re.compile(r"<(polygon|polyline)[^>]*\bpoints=[\'\"]([^\'\"]+)[\'\"]")
_SEG_PATH = re.compile(r"<path[^>]*\bd=[\'\"]([^\'\"]+)[\'\"]")


def figure_segments(svg_text):
    """Every straight segment the figure draws, as ((x1,y1),(x2,y2)).

    Gridline and tick paths are included and then filtered by the caller through the
    vertex-distance limit -- excluding them here would drop the axes of a coordinate
    figure, which are exactly the rays some angles are measured from.
    """
    segs = []
    for m in _SEG_LINE.finditer(svg_text):
        a, b, c, d = (float(g) for g in m.groups())
        segs.append(((a, b), (c, d)))
    for kind, raw in _SEG_POLY.findall(svg_text):
        try:
            nums = [float(n) for n in raw.replace(",", " ").replace("−", "-").split()]
        except ValueError:
            continue
        pts = list(zip(nums[0::2], nums[1::2]))
        if len(pts) < 2:
            continue
        if kind == "polygon":
            pts = pts + [pts[0]]
        segs += [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    for d in _SEG_PATH.findall(svg_text):
        if "A" in d.upper():
            continue                       # an arc is a mark, not a ray
        cur = start = None
        # Z closes the path. Dropping it cost the third side of every triangle drawn
        # as "M.. L.. L.. Z", which left its first vertex with a single ray -- so the
        # corner the question asked about had no angle to measure and went unmarked.
        for mm in re.finditer(r"([MLHVZmlhvz])\s*([-\d., ]*)", d):
            cmd, args = mm.group(1), [float(n) for n in
                                      re.findall(r"-?\d+(?:\.\d+)?", mm.group(2))]
            if cmd in "Zz":
                if cur and start and math.dist(cur, start) > 2:
                    segs.append((cur, start))
                cur = start
            elif cmd in "Mm" and len(args) >= 2:
                cur = start = (args[0], args[1])
            elif cmd in "Ll" and len(args) >= 2 and cur:
                segs.append((cur, (args[0], args[1])))
                cur = (args[0], args[1])
            elif cmd in "Hh" and args and cur:
                segs.append((cur, (args[0], cur[1])))
                cur = (args[0], cur[1])
            elif cmd in "Vv" and args and cur:
                segs.append((cur, (cur[0], args[0])))
                cur = (cur[0], args[0])
    return [s for s in segs if math.dist(*s) > 2]


_OUT_RECT = re.compile(r"<rect\b[^>]*>")
_OUT_CIRCLE = re.compile(r"<circle\b[^>]*>")
_OUT_ELLIPSE = re.compile(r"<ellipse\b[^>]*>")
_ATTR = re.compile(r"\b([\w-]+)\s*=\s*['\"]([^'\"]*)['\"]")


def _attrs(tag):
    return dict(_ATTR.findall(tag))


def _num(d, k, default=0.0):
    try:
        return float(d.get(k, default))
    except (TypeError, ValueError):
        return default


def _arc_points(x1, y1, rx, ry, phi, large, sweep, x2, y2, n=24):
    """Flatten an SVG elliptical arc to a polyline. Endpoint -> centre parameterisation,
    straight out of the SVG 1.1 implementation notes (F.6.5)."""
    if rx == 0 or ry == 0:
        return [(x1, y1), (x2, y2)]
    rx, ry = abs(rx), abs(ry)
    cosp, sinp = math.cos(phi), math.sin(phi)
    dx2, dy2 = (x1 - x2) / 2.0, (y1 - y2) / 2.0
    x1p = cosp * dx2 + sinp * dy2
    y1p = -sinp * dx2 + cosp * dy2
    lam = (x1p * x1p) / (rx * rx) + (y1p * y1p) / (ry * ry)
    if lam > 1:
        rx *= math.sqrt(lam)
        ry *= math.sqrt(lam)
    num = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
    den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
    if den == 0:
        return [(x1, y1), (x2, y2)]
    co = math.sqrt(max(0.0, num / den))
    if large == sweep:
        co = -co
    cxp = co * rx * y1p / ry
    cyp = -co * ry * x1p / rx
    cx = cosp * cxp - sinp * cyp + (x1 + x2) / 2.0
    cy = sinp * cxp + cosp * cyp + (y1 + y2) / 2.0

    def ang(ux, uy, vx, vy):
        dot = ux * vx + uy * vy
        n1 = math.hypot(ux, uy) * math.hypot(vx, vy)
        if n1 == 0:
            return 0.0
        a = math.acos(max(-1.0, min(1.0, dot / n1)))
        return -a if ux * vy - uy * vx < 0 else a

    th1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dth = ang((x1p - cxp) / rx, (y1p - cyp) / ry,
              (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not sweep and dth > 0:
        dth -= 2 * math.pi
    elif sweep and dth < 0:
        dth += 2 * math.pi
    pts = []
    for i in range(n + 1):
        t = th1 + dth * i / n
        pts.append((cx + rx * math.cos(t) * cosp - ry * math.sin(t) * sinp,
                    cy + rx * math.cos(t) * sinp + ry * math.sin(t) * cosp))
    return pts


def _bezier_points(p0, ctrl, n=16):
    """Flatten a quadratic (1 control) or cubic (2 controls) Bezier to a polyline."""
    pts = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        if len(ctrl) == 2:
            c, e = ctrl
            pts.append((u * u * p0[0] + 2 * u * t * c[0] + t * t * e[0],
                        u * u * p0[1] + 2 * u * t * c[1] + t * t * e[1]))
        else:
            c1, c2, e = ctrl
            pts.append((u ** 3 * p0[0] + 3 * u * u * t * c1[0]
                        + 3 * u * t * t * c2[0] + t ** 3 * e[0],
                        u ** 3 * p0[1] + 3 * u * u * t * c1[1]
                        + 3 * u * t * t * c2[1] + t ** 3 * e[1]))
    return pts


def _path_polyline(d):
    """Every point a path travels through, arcs and curves flattened. Absolute and
    relative commands both, because generated figures use whichever the author typed."""
    segs = []
    toks = re.findall(r"([MmLlHhVvZzAaCcQqSsTt])([^MmLlHhVvZzAaCcQqSsTt]*)", d)
    cur = start = None
    for cmd, raw in toks:
        args = [float(v) for v in re.findall(r"-?\d*\.?\d+(?:[eE][-+]?\d+)?", raw)]
        up = cmd.upper()
        rel = cmd.islower()
        if up == "Z":
            if cur and start and math.dist(cur, start) > 1e-9:
                segs.append((cur, start))
            cur = start
            continue
        i = 0
        while True:
            if up == "M":
                if i + 2 > len(args):
                    break
                pt = (args[i] + (cur[0] if rel and cur else 0),
                      args[i + 1] + (cur[1] if rel and cur else 0))
                if i == 0:
                    cur = start = pt
                else:
                    segs.append((cur, pt))
                    cur = pt
                i += 2
            elif up == "L":
                if i + 2 > len(args) or cur is None:
                    break
                pt = (args[i] + (cur[0] if rel else 0), args[i + 1] + (cur[1] if rel else 0))
                segs.append((cur, pt))
                cur = pt
                i += 2
            elif up in "HV":
                if i + 1 > len(args) or cur is None:
                    break
                v = args[i]
                pt = ((v + (cur[0] if rel else 0), cur[1]) if up == "H"
                      else (cur[0], v + (cur[1] if rel else 0)))
                segs.append((cur, pt))
                cur = pt
                i += 1
            elif up == "A":
                if i + 7 > len(args) or cur is None:
                    break
                rx, ry, rot, la, sw, ex, ey = args[i:i + 7]
                end = (ex + (cur[0] if rel else 0), ey + (cur[1] if rel else 0))
                pts = _arc_points(cur[0], cur[1], rx, ry, math.radians(rot),
                                  int(la), int(sw), end[0], end[1])
                segs += [(pts[k], pts[k + 1]) for k in range(len(pts) - 1)]
                cur = end
                i += 7
            elif up in "CQ":
                k = 6 if up == "C" else 4
                if i + k > len(args) or cur is None:
                    break
                raw_pts = [(args[i + j] + (cur[0] if rel else 0),
                            args[i + j + 1] + (cur[1] if rel else 0))
                           for j in range(0, k, 2)]
                pts = _bezier_points(cur, raw_pts)
                segs += [(pts[q], pts[q + 1]) for q in range(len(pts) - 1)]
                cur = raw_pts[-1]
                i += k
            else:                                  # S/T -- rare; treat as a line to end
                if len(args) < 2 or cur is None:
                    break
                pt = (args[-2] + (cur[0] if rel else 0), args[-1] + (cur[1] if rel else 0))
                segs.append((cur, pt))
                cur = pt
                break
            if i >= len(args):
                break
    return segs


_GEOM_TAG = re.compile(r"<(/?)(\w+)((?:[^>\"']|\"[^\"]*\"|'[^']*')*?)(/?)>")


def _xform(spec):
    """A transform attribute as a callable point -> point. translate and rotate only,
    which is every transform these figures use on anything but a <text>."""
    ops = []
    for name, raw in re.findall(r"(translate|rotate|scale)\s*\(([^)]*)\)", spec or ""):
        n = [float(v) for v in re.findall(r"-?\d*\.?\d+", raw)]
        if name == "translate" and n:
            tx, ty = n[0], (n[1] if len(n) > 1 else 0.0)
            ops.append(lambda p, tx=tx, ty=ty: (p[0] + tx, p[1] + ty))
        elif name == "rotate" and n:
            a = math.radians(n[0])
            cx, cy = (n[1], n[2]) if len(n) > 2 else (0.0, 0.0)
            ca, sa = math.cos(a), math.sin(a)
            ops.append(lambda p, ca=ca, sa=sa, cx=cx, cy=cy: (
                cx + (p[0] - cx) * ca - (p[1] - cy) * sa,
                cy + (p[0] - cx) * sa + (p[1] - cy) * ca))
        elif name == "scale" and n:
            sx, sy = n[0], (n[1] if len(n) > 1 else n[0])
            ops.append(lambda p, sx=sx, sy=sy: (p[0] * sx, p[1] * sy))
    if not ops:
        return None

    def apply(pt):
        for op in ops:
            pt = op(pt)
        return pt
    return apply


def _is_inked(a):
    """Does this element put anything on the page?

    Nearly every figure in the bank opens with
    `<rect width="300" height="220" fill="none"/>` -- a sizing frame with no fill and
    no stroke, which draws NOTHING. Counting its four sides as geometry put an
    invisible rectangle around the whole canvas and flagged every label that came
    near the edge, including an axis title sitting exactly where an axis title goes.
    """
    fill = (a.get("fill") or "").strip().lower()
    stroke = (a.get("stroke") or "").strip().lower()
    style = (a.get("style") or "").lower()
    if "fill:" in style and "fill:none" in style.replace(" ", ""):
        fill = "none"
    if "stroke:" in style and "stroke:none" not in style.replace(" ", ""):
        stroke = stroke or "set"
    if stroke and stroke != "none":
        return True
    if fill and fill != "none":
        return True
    # No fill attribute at all means the SVG default, which is black -- inked.
    return not fill


def figure_outlines(svg_text, curve_n=32):
    """EVERY inked boundary the figure draws, flattened to straight segments.

    `figure_segments` answers a different question -- which RAYS meet at a vertex, so
    an angle can be measured -- and deliberately drops arcs and never looked at
    <rect>, <circle> or <ellipse>, none of which contributes a ray. Reusing it to ask
    "is this label sitting on top of something drawn?" is what left
    `text_overlaps_geometry` blind to 94 defects a reviewer found in one sitting:
    a rectangle's own sides are not <line> elements, and neither is a circle, and
    neither is the angle arc that half the geometry figures print a number beside.

    So this returns the drawn EDGES of everything: line, polygon, polyline, rect,
    circle, ellipse, and path with its arcs and Beziers flattened. A shape whose
    fill is its only ink still bounds itself, so an unstroked polygon counts too.

    TRANSFORMS ARE APPLIED. Three of the VIC figures draw a pie chart inside
    `<g transform="translate(110,108)">`, and reading their sector paths at face
    value put every arc 110 px left and 108 px up of where the browser draws it --
    which is not a near miss, it is a different picture. A check that reads
    coordinates has to read them the way the renderer does.
    """
    segs = []
    stack = [None]

    def place(pts, tf):
        if tf:
            pts = [tf(p) for p in pts]
        return pts

    def emit(pts, tf, close=False):
        pts = place(list(pts), tf)
        if close and len(pts) > 2:
            pts = pts + [pts[0]]
        segs.extend((pts[i], pts[i + 1]) for i in range(len(pts) - 1))

    def compose(outer, own):
        if outer is None:
            return own
        if own is None:
            return outer
        return lambda p: outer(own(p))

    for m in _GEOM_TAG.finditer(svg_text):
        closing, name, attrs, selfclose = m.group(1), m.group(2), m.group(3), m.group(4)
        if closing:
            if name in ("g", "svg") and len(stack) > 1:
                stack.pop()
            continue
        own = _xform(_attrs(attrs + ">").get("transform"))
        cur = compose(stack[-1], own)
        if name == "g" and not selfclose:
            stack.append(cur)
            continue
        if name not in ("line", "rect", "circle", "ellipse",
                        "polygon", "polyline", "path"):
            continue
        a = _attrs(attrs + ">")
        if not _is_inked(a):
            continue
        if name == "line":
            emit([(_num(a, "x1"), _num(a, "y1")), (_num(a, "x2"), _num(a, "y2"))], cur)
        elif name == "rect":
            x, y = _num(a, "x"), _num(a, "y")
            w, h = _num(a, "width"), _num(a, "height")
            if w > 0 and h > 0:
                emit([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], cur, close=True)
        elif name in ("circle", "ellipse"):
            cx, cy = _num(a, "cx"), _num(a, "cy")
            rx = _num(a, "r") or _num(a, "rx")
            ry = _num(a, "r") or _num(a, "ry")
            # A plotted point is a filled dot a few pixels across, not an outline. It
            # has its own checks (`unknown_marker_far_from_point`), and treating every
            # dot as geometry would flag the label that names it -- the one label that
            # BELONGS beside it.
            if rx >= 6 and ry >= 6:
                emit([(cx + rx * math.cos(2 * math.pi * i / curve_n),
                       cy + ry * math.sin(2 * math.pi * i / curve_n))
                      for i in range(curve_n)], cur, close=True)
        elif name in ("polygon", "polyline"):
            try:
                nums = [float(v) for v in
                        (a.get("points", "").replace(",", " ")
                         .replace("\u2212", "-").split())]
            except ValueError:
                continue
            pts = list(zip(nums[0::2], nums[1::2]))
            if len(pts) >= 2:
                emit(pts, cur, close=(name == "polygon"))
        elif name == "path":
            for s1, s2 in _path_polyline(a.get("d", "")):
                emit([s1, s2], cur)
    return [s for s in segs if math.dist(*s) > 1e-9]


def _intersect(s1, s2):
    (x1, y1), (x2, y2) = s1
    (x3, y3), (x4, y4) = s2
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(den) < 1e-9:
        return None
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
    u = ((x1 - x3) * (y1 - y2) - (y1 - y3) * (x1 - x2)) / den
    if -0.02 <= t <= 1.02 and -0.02 <= u <= 1.02:
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    return None


def _rays_at(segs, v, eps=2.0):
    """Directions running out of v along the segments that touch it.

    A segment PASSING THROUGH v contributes two rays, which is the whole reason a
    transversal makes four angles at each crossing rather than one.
    """
    out = []
    for (a, b) in segs:
        for end, other in ((a, b), (b, a)):
            if math.dist(end, v) <= eps and math.dist(other, v) > eps:
                out.append((math.atan2(other[1] - v[1], other[0] - v[0]),
                            math.dist(other, v)))
        # interior point
        d = _dist_point_seg(v, a, b)
        if d <= eps and math.dist(a, v) > eps and math.dist(b, v) > eps:
            for other in (a, b):
                out.append((math.atan2(other[1] - v[1], other[0] - v[0]),
                            math.dist(other, v)))
    uniq = []
    for ang, ln in sorted(out):
        if not any(abs((ang - a2 + math.pi) % (2 * math.pi) - math.pi) < 0.05
                   for a2, _ in uniq):
            uniq.append((ang, ln))
    return uniq


def _dist_point_seg(p, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    n = dx * dx + dy * dy
    if n < 1e-9:
        return math.dist(p, a)
    t = max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / n))
    return math.dist(p, (ax + t * dx, ay + t * dy))


def angle_at_label(svg_text, box, reach=72.0):
    """Which angle a label names: (vertex, ray_a, ray_b, radius_room) or None.

    `box` is a `question_checks._text_box`. Returns None -- NEEDS A HUMAN, never a
    silent pass -- when the label is not inside exactly one sector of one vertex.
    An octagon's "?°" printed at its centre is the case that matters: it names an
    interior angle without saying which, and no amount of geometry decides that.
    """
    segs = figure_segments(svg_text)
    if not segs:
        return None
    lx, ly = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    verts = []
    for (a, b) in segs:
        verts += [a, b]
    for i in range(len(segs)):
        for j in range(i + 1, len(segs)):
            p = _intersect(segs[i], segs[j])
            if p:
                verts.append(p)
    cand = [v for v in verts if math.dist((lx, ly), v) <= reach]
    if not cand:
        return None
    for v in sorted(cand, key=lambda p: math.dist((lx, ly), p)):
        rays = _rays_at(segs, v)
        if len(rays) < 2:
            continue
        want = math.atan2(ly - v[1], lx - v[0])
        angs = sorted(a for a, _ in rays)
        for i, a1 in enumerate(angs):
            a2 = angs[(i + 1) % len(angs)]
            span = (a2 - a1) % (2 * math.pi)
            if span < 0.05 or span > math.pi + 0.05:
                continue
            if (want - a1) % (2 * math.pi) < span:
                # Reach is the shorter of the two rays BOUNDING this sector, not the
                # shortest ray at the vertex. A dimension tick or a right-angle
                # square ending near the vertex is not one of the angle's arms, and
                # letting it set the radius drew a 9 px arc on a full-page triangle.
                arms = [l for a, l in rays if abs((a - a1 + math.pi) % (2 * math.pi)
                                                  - math.pi) < 0.02
                        or abs((a - a2 + math.pi) % (2 * math.pi) - math.pi) < 0.02]
                return (v, a1, a2, min(arms) if arms else min(l for _, l in rays))
    return None


def interior_angle_at(svg_text, box, reach=90.0):
    """The angle a label MEANT, when the label was drawn outside the shape.

    Round 5 recorded the convention -- "angle values always within the shape, arc
    always present" -- into `figure_lib`, but the Gemini-era books never went
    through it, and a quarter of the figures that name an angle print the number
    just OUTSIDE the corner it belongs to. `angle_at_label` correctly declines
    those: no sector of that vertex contains the label, so nothing says which angle
    is meant.

    Here the shape decides instead. At the vertex nearest the label, the interior
    sector is the one whose bisector points back toward the middle of the figure --
    which is the angle a reader reads the number as naming anyway. Returns
    (vertex, ray_a, ray_b, reach) like `angle_at_label`.
    """
    segs = figure_segments(svg_text)
    if not segs:
        return None
    lx, ly = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    verts = [p for s in segs for p in s]
    for i in range(len(segs)):
        for j in range(i + 1, len(segs)):
            p = _intersect(segs[i], segs[j])
            if p:
                verts.append(p)
    if not verts:
        return None
    shapes = []
    for _kind, raw in _SEG_POLY.findall(svg_text):
        try:
            nums = [float(n) for n in raw.replace(",", " ").replace("−", "-").split()]
        except ValueError:
            continue
        pts = list(zip(nums[0::2], nums[1::2]))
        if len(pts) >= 3:
            shapes.append(pts)

    def middle(v):
        """Inward is toward the middle of the SHAPE this vertex belongs to.

        Two triangles sharing a side put the figure's overall centroid outside
        both of them, so p and s -- the apexes -- had no sector facing it and
        went unmarked. A vertex belongs to its own polygon.
        """
        for pts in shapes:
            if any(math.dist(v, p) < 2 for p in pts):
                return (sum(p[0] for p in pts) / len(pts),
                        sum(p[1] for p in pts) / len(pts))
        return (sum(p[0] for p in verts) / len(verts),
                sum(p[1] for p in verts) / len(verts))

    for v in sorted(verts, key=lambda p: math.dist((lx, ly), p)):
        if math.dist((lx, ly), v) > reach:
            break
        rays = _rays_at(segs, v)
        if len(rays) < 2:
            continue
        mid = middle(v)
        inward = math.atan2(mid[1] - v[1], mid[0] - v[0])
        angs = sorted(a for a, _ in rays)
        for i, a1 in enumerate(angs):
            a2 = angs[(i + 1) % len(angs)]
            span = (a2 - a1) % (2 * math.pi)
            if span < 0.05 or span > math.pi + 0.05:
                continue
            if (inward - a1) % (2 * math.pi) < span:
                arms = [l for a, l in rays
                        if abs((a - a1 + math.pi) % (2 * math.pi) - math.pi) < 0.02
                        or abs((a - a2 + math.pi) % (2 * math.pi) - math.pi) < 0.02]
                return (v, a1, a2, min(arms) if arms else min(l for _, l in rays))
    return None


def label_on_bisector(v, a1, a2, box, r, clear=9.0, pad=3.0):
    """Put a label on the sector's bisector, just beyond the arc.

    Used when the label has to MOVE rather than merely make room -- it was outside
    the shape and is being brought in.
    """
    box = (box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad)
    span = (a2 - a1) % (2 * math.pi)
    bis = a1 + span / 2
    hw, hh = (box[2] - box[0]) / 2, (box[3] - box[1]) / 2
    lo, hi = 0.0, 240.0
    for _ in range(44):
        t = (lo + hi) / 2
        cx, cy = v[0] + t * math.cos(bis), v[1] + t * math.sin(bis)
        if box_gap((cx - hw, cy - hh, cx + hw, cy + hh), *v) < r + clear:
            lo = t
        else:
            hi = t
    return (v[0] + hi * math.cos(bis), v[1] + hi * math.sin(bis))


def box_gap(box, x, y):
    """Distance from a point to a text box, 0 inside it."""
    bx0, by0, bx1, by1 = box[:4]
    dx = max(bx0 - x, 0.0, x - bx1)
    dy = max(by0 - y, 0.0, y - by1)
    return math.hypot(dx, dy)


def arc_radius(reach):
    """One radius rule, so the label placement and the arc cannot disagree."""
    return max(9.0, min(20.0, 0.30 * reach))


def label_clear_of_arc(v, a1, a2, box, r, clear=9.0, pad=3.0):
    """Where the label has to move to so the arc does not strike through it.

    First cut sized the ARC to miss the label, with a floor under the radius --
    which meant that for a label sitting 12 px from its vertex the floor won and
    the arc was drawn straight through the text. Three of the thirty-two came back
    with "50°" and "a°" struck out. The label is the thing that moves: an angle
    label belongs OUTSIDE its arc, on the bisector, which is where a textbook puts
    it anyway.
    """
    # The box used to be estimated from a character count -- right on average and
    # wrong per label -- so "52 deg" cleared the arc on paper and the rendered
    # glyphs still crossed it. `_text_box` measures with Arial's real advance
    # widths now, but keep the pad: an arc grazing a glyph still reads as struck
    # through, so decide with room to spare and place with room to spare.
    box = (box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad)
    if box_gap(box, *v) >= r + clear:
        return None
    span = (a2 - a1) % (2 * math.pi)
    bis = a1 + span / 2
    hw, hh = (box[2] - box[0]) / 2, (box[3] - box[1]) / 2
    lo, hi = 0.0, 200.0
    for _ in range(40):
        t = (lo + hi) / 2
        cx, cy = v[0] + t * math.cos(bis), v[1] + t * math.sin(bis)
        shifted = (cx - hw, cy - hh, cx + hw, cy + hh)
        if box_gap(shifted, *v) < r + clear:
            lo = t
        else:
            hi = t
    t = hi
    return (v[0] + t * math.cos(bis), v[1] + t * math.sin(bis))


def angle_mark(v, a1, a2, r, colour="currentColor", square_tol=0.035, label=""):
    """The SVG for one angle mark: a square if it is a right angle, else an arc.

    A right angle is drawn as a square by every textbook the students use, so an arc
    there would read as "not 90°" -- the convention carries information. Which is
    exactly why the DRAWN angle cannot decide it. A quadrilateral captioned 85, 95,
    110 and ? was drawn with two corners within two degrees of square, and marking
    those got a right-angle symbol printed on the 110 degree corner -- the figure
    asserting something the question denies. A square is drawn only where the label
    says 90, or where there is no number to contradict it.
    """
    span = (a2 - a1) % (2 * math.pi)
    if r < 8.0:
        return None
    # A square where the label says 90, or where there is no label to contradict it.
    # NOT merely "no digits": the unknown corner of that quadrilateral is labelled
    # "?°", is drawn square, and is 70 degrees -- a square there hands the student a
    # wrong answer off the picture.
    says_90 = re.fullmatch(r"\s*90\s*°?\s*", label or "") is not None
    if abs(span - math.pi / 2) < square_tol and (says_90 or not (label or "").strip()):
        s = min(r, 13.0)
        p1 = (v[0] + s * math.cos(a1), v[1] + s * math.sin(a1))
        p2 = (v[0] + s * math.cos(a2), v[1] + s * math.sin(a2))
        cx = p1[0] + p2[0] - v[0]
        cy = p1[1] + p2[1] - v[1]
        return (f'<path d="M{p1[0]:.1f} {p1[1]:.1f}L{cx:.1f} {cy:.1f}'
                f'L{p2[0]:.1f} {p2[1]:.1f}" fill="none" stroke="{colour}" '
                f'stroke-width="1.3"/>')
    x1, y1 = v[0] + r * math.cos(a1), v[1] + r * math.sin(a1)
    x2, y2 = v[0] + r * math.cos(a2), v[1] + r * math.sin(a2)
    # Endpoints are placed from ONE radius and the sweep flag is chosen from the
    # sector's own direction, which is what `angle_arc_malformed` measures: an arc
    # whose ends are a fifth of a pixel apart in radius bulges through the edge.
    return (f'<path d="M{x1:.1f} {y1:.1f}A{r:.1f} {r:.1f} 0 0 1 {x2:.1f} {y2:.1f}" '
            f'fill="none" stroke="{colour}" stroke-width="1.3"/>')
