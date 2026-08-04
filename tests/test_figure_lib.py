"""Figure builders — the invariants that make a figure trustworthy without looking at it.

These guard the class of defect the builders were written to remove: a label that
disagrees with the line it names, a cube stack that cannot be counted, a net that does
not fold. Rendering and looking is still required on top of this — see
tools/figure_contact_sheet.py.
"""
import re

import pytest

from tools.figure_lib import (
    check_stack,
    fold,
    iso_stack_fitted,
    net_svg,
    opposite_of,
    ortho,
    svg,
)
from tools.question_checks import figure_svg_errors


# ---------------------------------------------------------------- ortho
L_SHAPE = [(6, 0), (0, 4), (-2, 0), (0, -2), (-4, 0), (0, -2)]


def test_ortho_labels_are_derived_from_the_same_moves_as_the_path():
    """REGRESSION: hand-written figures had labels that were geometrically impossible.

    Every side length in the output must come from the move list, so a label cannot
    disagree with the line it names.
    """
    body, perim, area = ortho(L_SHAPE, "cm", 20)
    labelled = sorted(int(n) for n in re.findall(r">(\d+) cm<", body))
    assert labelled == sorted(abs(dx) + abs(dy) for dx, dy in L_SHAPE)


def test_ortho_computes_perimeter_and_area():
    _, perim, area = ortho(L_SHAPE, "cm", 20)
    assert perim == 20
    assert area == 16  # 6x2 base strip plus the 2x2 block standing on its right


def test_ortho_rejects_a_shape_that_does_not_close():
    with pytest.raises(ValueError, match="does not close"):
        ortho([(6, 0), (0, 4), (-2, 0)], "cm", 20)


def test_ortho_output_satisfies_the_figure_rules():
    body, _, _ = ortho(L_SHAPE, "cm", 20)
    assert figure_svg_errors(svg(body)) == []


def test_ortho_labels_do_not_collide():
    """REGRESSION: a narrow concavity printed three labels over one another.

    Anchor points alone looked clear; the rendered glyphs overlapped. Labels on the same
    horizontal band must not share horizontal extent.
    """
    body, _, _ = ortho([(4, 0), (0, 2), (-1, 0), (0, 3), (-2, 0), (0, -3), (-1, 0), (0, -2)],
                       "m", 26)
    labels = [(float(x), float(y)) for x, y in
              re.findall(r'<text x="(-?[\d.]+)" y="(-?[\d.]+)"', body)]
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            (x1, y1), (x2, y2) = labels[i], labels[j]
            assert abs(y1 - y2) >= 12 or abs(x1 - x2) >= 12, \
                f"labels at {labels[i]} and {labels[j]} overlap"


# ---------------------------------------------------------------- isometric stacks
def test_check_stack_rejects_a_column_that_would_hide_another():
    """A near column taller than a far one on the same screen diagonal paints over it.

    Face culling cannot fix this: the columns are not adjacent, merely overlapping in
    projection, so the far one is silently erased and the cubes become uncountable.
    """
    with pytest.raises(ValueError, match="occlusion"):
        check_stack({(0, 0): 1, (1, 1): 3})


def test_check_stack_accepts_a_visible_layout_and_counts_cubes():
    total, footprint = check_stack({(0, 0): 3, (1, 0): 2, (0, 1): 1})
    assert (total, footprint) == (6, 3)


def test_iso_stack_fits_inside_its_viewbox():
    """REGRESSION: hand-picked offsets clipped the tallest column off the canvas."""
    body = iso_stack_fitted({(0, 0): 4, (1, 0): 2, (0, 1): 3, (1, 1): 1}, vw=340, vh=220)
    m = re.search(r"translate\((-?[\d.]+),(-?[\d.]+)\) scale\(([\d.]+)\)", body)
    assert m, "expected a fitting transform"
    dx, dy, s = (float(g) for g in m.groups())
    xs, ys = [], []
    for pts in re.findall(r'points="([^"]+)"', body):
        for pair in pts.split():
            a, b = pair.split(",")
            xs.append(float(a) * s + dx)
            ys.append(float(b) * s + dy)
    assert 0 <= min(xs) and max(xs) <= 340
    assert 0 <= min(ys) and max(ys) <= 220


def test_iso_stack_draws_only_visible_faces():
    """Drawing buried cubes produced an uncountable tessellation."""
    one = iso_stack_fitted({(0, 0): 1}).count("<polygon")
    assert one == 3                       # top, front, side of a lone cube
    two = iso_stack_fitted({(0, 0): 2}).count("<polygon")
    assert two < one * 2                  # the join between them is not drawn


# ---------------------------------------------------------------- cube nets
CROSS = {"A": (1, 0), "B": (0, 1), "C": (1, 1), "D": (2, 1), "E": (1, 2), "F": (1, 3)}


def test_fold_gives_each_face_a_distinct_outward_normal():
    faces = fold(CROSS)
    assert len(faces) == 6
    assert len(set(faces.values())) == 6


def test_opposite_faces_are_mutual():
    for label in CROSS:
        other = opposite_of(CROSS, label)
        assert opposite_of(CROSS, other) == label
        assert other != label


def test_fold_rejects_a_net_that_does_not_make_a_cube():
    """Six squares in a row fold two faces onto the same normal."""
    strip = {c: (i, 0) for i, c in enumerate("ABCDEF")}
    with pytest.raises(ValueError, match="does not fold to a cube"):
        fold(strip)


def test_fold_rejects_a_disconnected_net():
    with pytest.raises(ValueError, match="not connected"):
        fold({"A": (0, 0), "B": (1, 0), "C": (5, 5), "D": (6, 5), "E": (0, 1), "F": (1, 1)})


def test_net_svg_labels_every_face_and_satisfies_the_figure_rules():
    body = net_svg(CROSS)
    for label in CROSS:
        assert f">{label}<" in body
    assert figure_svg_errors(svg(body)) == []
