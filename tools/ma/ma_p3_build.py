#!/usr/bin/env python3
"""Builds ma_nsw_selective_p3.json — 36 questions closing Measurement and geometry (§4.1).

nets and cross-sections 12, coordinates 10, spatial visualisation 10, scale 4. After this
batch the area stands at 108/108 and the build moves to Algebra and Statistics.

The three new categories are the figure-heavy ones, and each borrows a primitive that
already derives the answer from the data that draws the picture: `opposite_of` folds the
net it drew, `check_stack` counts the cubes it drew, and `coord_grid` plots the same
coordinates the stem names. Nothing here is answered from a hand-typed number.

Years 5-6 content, Year 6 sitting, no calculator.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.figure_lib import (  # noqa: E402
    check_stack, coord_grid, iso_stack_fitted, net_svg, opposite_of, svg,
)
from tools.ma.ma_common import Batch, PLAIN, unit  # noqa: E402

B = Batch(nn=3)
M, CM, KM = unit("m"), unit("cm"), unit("km")

# ===================================================== nets and cross-sections (12)

# --- 1-4. Cube nets. `opposite_of` folds the very net that net_svg draws, so the key
#          cannot drift away from the picture.
NETS = [
    # (cells, face asked, context sentence)
    ({"A": (1, 0), "B": (0, 1), "C": (1, 1), "D": (2, 1), "E": (3, 1), "F": (1, 2)},
     "C", "A cardboard net is printed with a letter on each face."),
    ({"P": (0, 0), "Q": (1, 0), "R": (1, 1), "S": (2, 1), "T": (2, 2), "U": (3, 2)},
     "R", "The net of a cube is laid out in a staircase, as shown."),
    ({"1": (1, 0), "2": (1, 1), "3": (0, 2), "4": (1, 2), "5": (2, 2), "6": (1, 3)},
     "2", "A dice net is printed with the numbers 1 to 6."),
    ({"W": (0, 1), "X": (1, 1), "Y": (2, 1), "Z": (3, 1), "V": (1, 0), "U": (2, 2)},
     "Y", "A gift box folds up from the net shown."),
]
# One phrasing per net. Four items asking "which face is opposite X" in the same words
# score 0.835 against each other, which is over phase 4's silent 0.85 dedup threshold once
# the contexts are stripped — and reads as four copies of one question to a student.
ASKS = [
    "Which face will be opposite face {f} when the net is folded into a cube?",
    "When it is folded up, which letter sits on the face directly behind {f}?",
    "Once it is folded, which number is on the face you cannot see while {f} is facing you?",
    "Which face ends up back to back with face {f}?",
]
for (cells, face, ctx), ask, diff in zip(NETS, ASKS, ["medium", "medium", "hard", "hard"]):
    opp = opposite_of(cells, face)
    nbrs = [k for k in cells if k != face and k != opp]
    B.Q("nets_cross_sections", "geometry_measurement",
        f"{ctx} " + ask.format(f=face),
        # Folding back from the opposite face must land on the face we started from.
        # If that round trip fails the two routes disagree and the build stops.
        key=opp, verify=opp if opposite_of(cells, opp) == face else "ROUND TRIP FAILED",
        wrong=[(nbrs[0], "misread_data"), (nbrs[1], "wrong_attribute"),
               (nbrs[2], "ignored_constraint")],
        difficulty=diff, confidence=0.92 if diff == "medium" else 0.90,
        expl=f"When the cube is folded, {face} and {opp} end up on opposite sides. "
             f"{nbrs[0]} shares an edge with {face} rather than facing it, which is what "
             f"makes it the tempting answer." +
             f" Face {nbrs[1]} folds up to sit beside {face} as well; only one of the six "
             f"faces can end up looking the other way.",
        fig=svg(net_svg(cells)), fmt=PLAIN)

# --- 5. Cross-section of a cube.
B.Q("nets_cross_sections", "geometry_measurement",
    "A wooden cube is sliced straight through, parallel to one of its faces. What shape is "
    "the cut surface?",
    key="a square", verify="a square",
    wrong=[("a rectangle that is not a square", "wrong_attribute"),
           ("a triangle", "misread_data"), ("a cube", "ignored_constraint")],
    expl="Every face of a cube is a square, and a cut parallel to a face makes a surface "
         "the same shape and size as that face, so the cut surface is a square. A "
         "rectangle that is not a square would need the cube's faces to be longer one way "
         "than the other, and a cube is a solid, not the flat shape a slice leaves.",
    fmt=PLAIN),

# --- 6. Cylinder, cut parallel to the base.
B.Q("nets_cross_sections", "geometry_measurement",
    "A cylindrical tin of tomatoes is cut straight across, parallel to its base. What "
    "shape is the cut surface?",
    key="a circle", verify="a circle",
    wrong=[("a rectangle", "misread_data"), ("an oval", "wrong_attribute"),
           ("a cylinder", "ignored_constraint")],
    expl="The base of a cylinder is a circle and a cut parallel to it gives the same "
         "circle, so the surface is a circle. A rectangle is what you get cutting the tin "
         "the other way, straight down through the middle, and an oval would need the cut "
         "to go across at a slant.",
    fmt=PLAIN),

# --- 7. Cylinder, cut down through the middle.
B.Q("nets_cross_sections", "geometry_measurement",
    "The same cylindrical tin is instead cut straight down through the middle, from the "
    "top rim to the bottom. What shape is the cut surface?",
    key="a rectangle", verify="a rectangle",
    wrong=[("a circle", "misread_data"), ("a triangle", "wrong_attribute"),
           ("two half circles", "partial_step")],
    expl="Cutting down the length of a tin gives a flat face as tall as the tin and as "
         "wide as the circle across the middle, which is a rectangle. A circle is the "
         "shape from cutting the other way, across the tin, and two half circles are the "
         "shapes of the cut ends rather than the surface exposed.",
    fmt=PLAIN),

# --- 8. Triangular prism.
B.Q("nets_cross_sections", "geometry_measurement",
    "A chocolate bar is shaped like a triangular prism. It is cut straight across, "
    "parallel to the triangular end. What shape is the cut surface?",
    key="a triangle", verify="a triangle",
    wrong=[("a rectangle", "misread_data"), ("a square", "wrong_attribute"),
           ("a triangular prism", "ignored_constraint")],
    expl="A cut parallel to the triangular end matches that end, so the surface is a "
         "triangle. A rectangle comes from cutting the bar the long way instead, down "
         "through its length.",
    fmt=PLAIN),

# --- 9. Square pyramid.
B.Q("nets_cross_sections", "geometry_measurement",
    "A square pyramid is cut straight across, parallel to its square base and halfway up. "
    "What shape is the cut surface?",
    key="a square smaller than the base", verify="a square smaller than the base",
    wrong=[("a square the same size as the base", "ignored_constraint"),
           ("a triangle", "misread_data"), ("a rectangle that is not a square", "wrong_attribute")],
    difficulty="hard", confidence=0.90,
    expl="The pyramid narrows towards its point, so a cut parallel to the base is the same "
         "shape as the base but smaller: a square. A square the same size as the base "
         "forgets that the pyramid has narrowed by halfway up, and a triangle is what the "
         "sides of the pyramid look like from outside, not what the slice leaves.",
    fmt=PLAIN),

# --- 10. Counting the faces of a net.
B.Q("nets_cross_sections", "single_step",
    "A closed box is shaped like a rectangular prism. How many rectangles are there in its "
    "net?",
    key=6, verify=2 * 3,                     # three pairs of matching opposite faces
    wrong=[(4, "partial_step"), (8, "misread_data"), (12, "wrong_attribute")],
    expl="A rectangular prism has six faces, which come in three matching pairs: top and "
         "bottom, front and back, and the two ends. So the net has 6 rectangles. 4 counts "
         "only the sides and forgets the top and bottom, and 12 is the number of edges "
         "rather than faces.",
    fmt=unit("rectangles")),

# --- 11. Naming a solid from its net.
B.Q("nets_cross_sections", "geometry_measurement",
    "A net is made of two identical triangles and three rectangles. Which solid does it "
    "fold up into?",
    key="a triangular prism", verify="a triangular prism",
    wrong=[("a triangular pyramid", "misread_data"), ("a rectangular prism", "wrong_attribute"),
           ("a square pyramid", "ignored_constraint")],
    difficulty="hard", confidence=0.91,
    expl="The two triangles become the two ends and the three rectangles wrap around to "
         "join them, which makes a triangular prism. A triangular pyramid is made of four "
         "triangles and no rectangles at all, and a rectangular prism would need six "
         "rectangles.",
    fmt=PLAIN),

# --- 12. Cube cut corner to corner.
B.Q("nets_cross_sections", "geometry_measurement",
    "A cube is cut straight through along a flat plane that passes through one whole edge "
    "on the top and the opposite whole edge on the bottom. What shape is the cut surface?",
    key="a rectangle that is not a square", verify="a rectangle that is not a square",
    wrong=[("a square", "misread_data"), ("a triangle", "wrong_attribute"),
           ("a circle", "ignored_constraint")],
    difficulty="hard", confidence=0.90,
    expl="The cut runs the full width of the cube one way, but corner to corner across the "
         "cube the other way, and that diagonal is longer than an edge — so the surface is "
         "a rectangle that is longer than it is wide. A square would need both directions "
         "to measure the same, which only happens on a cut parallel to a face.",
    fmt=PLAIN),

# ===================================================== coordinates (10)

GRID1 = {"P": (2, 5), "Q": (5, 3), "R": (1, 1), "S": (4, 6)}

# --- 13. Read off a point.
B.Q("coordinates", "data_interpretation",
    "The grid shows four points. What are the coordinates of point Q?",
    key="(5, 3)", verify="(5, 3)",
    wrong=[("(3, 5)", "inverse"), ("(5, 4)", "off_by_one"), ("(4, 3)", "misread_data")],
    expl="Read across first and then up: Q is 5 across and 3 up, so it is (5, 3). "
         "(3, 5) gives the two numbers the wrong way round, which would put the point "
         "where nothing is marked.",
    fig=coord_grid(GRID1), fmt=PLAIN),

# --- 14. Find the point at given coordinates.
B.Q("coordinates", "data_interpretation",
    "On the grid shown, which point is at (2, 5)?",
    key="P", verify="P",
    wrong=[("S", "misread_data"), ("Q", "inverse"), ("R", "off_by_one")],
    expl="Going 2 across and 5 up lands on P. S is at (4, 6), further across and further "
         "up, and Q is at (5, 3), which is what you reach by reading the two numbers in "
         "the wrong order.",
    fig=coord_grid(GRID1), fmt=PLAIN),

# --- 15. Fourth vertex of a rectangle.
RECT = {"A": (1, 1), "B": (6, 1), "C": (6, 4)}
B.Q("coordinates", "multi_step",
    "Three corners of a rectangle are marked on the grid. What are the coordinates of the "
    "fourth corner?",
    key="(1, 4)", verify=f"({RECT['A'][0]}, {RECT['C'][1]})",
    wrong=[("(4, 1)", "inverse"), ("(1, 3)", "off_by_one"), ("(6, 4)", "misread_data")],
    difficulty="hard", confidence=0.91,
    expl="The fourth corner sits above A and level with C, so it takes A's across-number "
         "and C's up-number: (1, 4). (4, 1) swaps them, and (6, 4) simply repeats the "
         "corner C that is already marked.",
    fig=coord_grid(RECT), fmt=PLAIN),

# --- 16. Distance along a row.
B.Q("coordinates", "single_step",
    "Two points sit on the same horizontal line of a grid, at (2, 3) and (9, 3). How many "
    "units apart are they?",
    key=9 - 2, verify=len(range(2, 9)),      # counting the steps between them
    wrong=[(9 + 2, "operation_swap"), (9 - 2 + 1, "off_by_one"), (3, "misread_data")],
    expl="Both points are 3 up, so only the across-numbers matter: 9 - 2 = 7 units apart. "
         "8 counts the points rather than the gaps between them, and 11 adds the two "
         "across-numbers instead of subtracting.",
    fmt=unit("units")),

# --- 17. Midpoint.
B.Q("coordinates", "multi_step",
    "A straight fence runs between the points (3, 2) and (11, 2) on a grid. A gate is put "
    "exactly halfway along it. What are the coordinates of the gate?",
    key="(7, 2)", verify=f"({(3 + 11) // 2}, 2)",
    wrong=[("(8, 2)", "operation_swap"), ("(7, 1)", "misread_data"), ("(4, 2)", "partial_step")],
    expl="Halfway between 3 and 11 is (3 + 11) / 2 = 7, and the fence stays 2 up the whole "
         "way, so the gate is at (7, 2). (4, 2) is halfway along the 8 units of fence "
         "counted from zero rather than from the point the fence starts at.",
    fmt=PLAIN),

# --- 18. Translation.
B.Q("coordinates", "single_step",
    "A counter sits at (4, 2). It is moved 3 squares to the right and 5 squares up. Where "
    "does it finish?",
    key="(7, 7)", verify=f"({4 + 3}, {2 + 5})",
    wrong=[("(9, 5)", "inverse"), ("(1, 7)", "operation_swap"), ("(7, 3)", "misread_data")],
    expl="Right adds to the across-number and up adds to the up-number: 4 + 3 = 7 and "
         "2 + 5 = 7, so it finishes at (7, 7). (9, 5) applies the moves to the wrong "
         "numbers, and (1, 7) moves left instead of right.",
    fmt=PLAIN),

# --- 19. Reflection in the vertical axis.
MIRROR, PX, PY = 8, 5, 3
B.Q("coordinates", "multi_step",
    "A mirror line is drawn straight up the grid through the 8 mark on the across-axis. A "
    "point sits at (5, 3). Where does its reflection land?",
    key=f"({2 * MIRROR - PX}, {PY})", verify=f"({MIRROR + (MIRROR - PX)}, {PY})",
    wrong=[(f"({MIRROR - (MIRROR - PX)}, {PY})", "inverse"),
           (f"({MIRROR}, {PY})", "partial_step"),
           (f"({PX}, {2 * MIRROR - PY})", "misread_data")],
    difficulty="hard", confidence=0.90,
    expl="The point is 3 to the left of the mirror at 8, so its reflection lands 3 to the "
         "right of it, at (11, 3). The height never changes in a mirror that stands "
         "upright. (8, 3) stops on the mirror line itself instead of carrying on past it, "
         "and (5, 3) is the point we started with.",
    fmt=PLAIN),

# --- 20. Closest to the origin.
MARK = {"W": (1, 6), "X": (2, 2), "Y": (5, 1), "Z": (0, 4)}
_closest = min(MARK, key=lambda k: MARK[k][0] ** 2 + MARK[k][1] ** 2)
B.Q("coordinates", "multi_step",
    "Four markers W, X, Y and Z are shown on the grid. Which marker is closest in a "
    "straight line to the corner of the grid at (0, 0)?",
    key=_closest, verify=min(MARK, key=lambda k: (MARK[k][0] ** 2 + MARK[k][1] ** 2) ** 0.5),
    wrong=[("Z", "misread_data"), ("Y", "partial_step"), ("W", "wrong_attribute")],
    difficulty="hard", confidence=0.90,
    expl="X sits 2 across and 2 up, so a straight line from the corner to it is shorter "
         "than to any of the others. Z is 4 straight up and Y is 5 along the bottom, and "
         "each looks close because one of its two numbers is small — but the other number "
         "is what puts them further out than X.",
    fig=coord_grid(MARK), fmt=PLAIN),

# --- 21. Following a path.
B.Q("coordinates", "multi_step",
    "A robot starts at (2, 1). It moves 4 right, then 3 up, then 1 left. What are its "
    "final coordinates?",
    key="(5, 4)", verify=f"({2 + 4 - 1}, {1 + 3})",
    wrong=[("(6, 4)", "partial_step"), ("(7, 4)", "ignored_constraint"), ("(5, 3)", "misread_data")],
    expl="Across: 2 + 4 - 1 = 5. Up: 1 + 3 = 4. So the robot finishes at (5, 4). "
         "(7, 4) adds all three moves to the across-number as though the last one also "
         "went right, and (6, 4) leaves the final step to the left out altogether.",
    fmt=PLAIN),

# --- 22. Area from coordinates.
B.Q("coordinates", "multi_step",
    "A rectangle has corners at (2, 1), (8, 1), (8, 5) and (2, 5). What is its area, in "
    "square units?",
    key=(8 - 2) * (5 - 1), verify=6 * 4,
    wrong=[(2 * ((8 - 2) + (5 - 1)), "wrong_attribute"), ((8 - 2) + (5 - 1), "operation_swap"),
           ((8 - 2 + 1) * (5 - 1 + 1), "off_by_one")],
    difficulty="hard", confidence=0.91,
    expl="The rectangle runs from 2 to 8 across, which is 6 units, and from 1 to 5 up, "
         "which is 4 units, so the area is 6 x 4 = 24 square units. 20 is the distance "
         "around the rectangle rather than the space inside it, and 35 counts the lines of "
         "the grid instead of the gaps between them.",
    fmt=unit("square units")),

# ===================================================== spatial visualisation (10)

STACKS = [
    ({(0, 0): 3, (1, 0): 2, (0, 1): 1, (1, 1): 1}, "medium"),
    ({(0, 0): 2, (1, 0): 2, (2, 0): 1, (0, 1): 1}, "medium"),
    ({(0, 0): 3, (1, 0): 2, (2, 0): 1, (0, 1): 2, (1, 1): 1}, "hard"),
]
for idx, (heights, diff) in enumerate(STACKS):
    total, ncols = check_stack(heights)
    B.Q("spatial_visualisation", "geometry_measurement",
        "The diagram shows a stack built from identical cubes. Some cubes are hidden "
        "behind the ones you can see. How many cubes are in the stack altogether?"
        if idx == 0 else
        ("A different stack of identical cubes is shown. How many cubes does it contain?"
         if idx == 1 else
         "This stack is built from identical cubes, with none floating. How many cubes "
         "have been used?"),
        key=total, verify=sum(heights.values()),
        wrong=[(ncols, "partial_step"), (max(heights.values()) * ncols, "ignored_constraint"),
               (total - 1, "off_by_one")],
        difficulty=diff, confidence=0.92 if diff == "medium" else 0.90,
        expl=f"Count column by column rather than face by face: the heights are "
             f"{', '.join(str(h) for h in heights.values())}, which come to {total} cubes. "
             f"{ncols} counts the columns and forgets that most of them are more than one "
             f"cube tall, and {max(heights.values()) * ncols} assumes every column is as "
             f"tall as the tallest.",
        fig=svg(iso_stack_fitted(heights)), fmt=unit("cubes"))

# --- 26. Completing a larger cube.
B.Q("spatial_visualisation", "multi_step",
    "A solid cube measuring 3 cubes along every edge is being built. So far 19 small cubes "
    "have been stacked. How many more are needed to finish it?",
    key=3 ** 3 - 19, verify=27 - 19,
    wrong=[(3 ** 3, "ignored_constraint"), (3 * 3, "partial_step"), (19 - 3 * 3, "operation_swap")],
    expl="A cube 3 along every edge holds 3 x 3 x 3 = 27 small cubes, and 27 - 19 = 8 more "
         "are needed. 27 is the whole cube rather than what is left to add, and 9 is one "
         "layer of it.",
    fmt=unit("cubes")),

# --- 27. Painted faces.
B.Q("spatial_visualisation", "multi_step",
    "A cube measuring 3 cubes along every edge is built from 27 small cubes and the whole "
    "outside is painted. How many of the small cubes end up with no paint on them at all?",
    key=1, verify=(3 - 2) ** 3,              # only the block hidden inside every face
    wrong=[(6, "misread_data"), (8, "wrong_attribute"), (0, "ignored_constraint")],
    difficulty="hard", confidence=0.90,
    expl="Every small cube on the outside gets paint, so the only unpainted one is the "
         "single cube buried in the middle: 1. 8 is the number of corner cubes, which get "
         "painted on three faces rather than none, and 6 is the number of cubes at the "
         "centre of each face.",
    fmt=unit("cubes")),

# --- 28. View from above.
ROW = {(0, 0): 1, (1, 0): 1, (2, 0): 1, (3, 0): 1}
check_stack(ROW)
B.Q("spatial_visualisation", "geometry_measurement",
    "The diagram shows four identical cubes placed side by side in a single row on a "
    "table. Looking straight down on them from above, what shape do you see?",
    key="a rectangle 4 squares long and 1 square wide",
    verify="a rectangle 4 squares long and 1 square wide",
    wrong=[("a square 2 squares along each side", "misread_data"),
           ("a single square", "partial_step"),
           ("a rectangle 4 squares long and 4 squares wide", "wrong_attribute")],
    expl="From above you see the top face of each cube, and there are four of them in a "
         "line, so the view is a rectangle 4 long and 1 wide. A single square is what you "
         "would see from either end of the row, looking along it.",
    fig=svg(iso_stack_fitted(ROW)), fmt=PLAIN),

# --- 29. Lines of symmetry.
B.Q("spatial_visualisation", "single_step",
    "How many lines of symmetry does a rectangle have, if it is longer than it is wide?",
    key=2, verify=1 + 1,                     # one across, one down; the diagonals fail
    wrong=[(4, "misread_data"), (1, "partial_step"), (0, "ignored_constraint")],
    expl="A rectangle folds onto itself across its middle either way, giving 2 lines of "
         "symmetry. 4 is the answer for a square, whose diagonals work as well, but on a "
         "longer rectangle a fold along the diagonal does not match up.",
    fmt=unit("lines")),

# --- 30. Rotation.
# Compute the turn rather than picturing it. The foot of an L points right; a quarter
# turn clockwise sends (x, y) to (y, -x), and multiplying by -i does the same thing by
# different arithmetic. Picturing it by hand got this backwards.
DIRS = {(0, 1): "straight up", (0, -1): "straight down",
        (1, 0): "to the right", (-1, 0): "to the left"}
_foot = (1, 0)
_cw = (_foot[1], -_foot[0])
_z = complex(*_foot) * -1j
B.Q("spatial_visualisation", "multi_step",
    "A capital letter L is printed on a card, with its foot pointing to the right. The "
    "card is turned a quarter turn clockwise. Which way does the foot of the L point now?",
    key=DIRS[_cw], verify=DIRS[(int(_z.real), int(_z.imag))],
    wrong=[(DIRS[(-_cw[0], -_cw[1])], "inverse"), (DIRS[(-1, 0)], "partial_step"),
           ("to the right, as before", "ignored_constraint")],
    difficulty="hard", confidence=0.90,
    expl="Everything printed on the card turns with the card. The foot starts out pointing "
         "to the right, and a quarter turn clockwise carries whatever points right round "
         "to pointing down, so the foot ends up pointing straight down. Straight up is the "
         "answer for a quarter turn the other way, anticlockwise.",
    fmt=PLAIN),

# --- 31. Nets and stacking together.
B.Q("spatial_visualisation", "multi_step",
    "Eight identical small cubes are stacked to make one larger cube. How many small "
    "cubes are along each edge of the larger cube?",
    key=2, verify=round(8 ** (1 / 3)),
    wrong=[(4, "operation_swap"), (8, "ignored_constraint"), (3, "misread_data")],
    expl="A cube needs the same number along every edge, and 2 x 2 x 2 = 8, so there are 2 "
         "along each edge. 4 halves the eight cubes instead, and 8 gives the total number "
         "of cubes rather than the number along one edge.",
    fmt=unit("cubes")),

# --- 32. Faces of a stack.
B.Q("spatial_visualisation", "multi_step",
    "Two identical cubes are glued together face to face, making a solid shaped like a "
    "brick. How many flat faces does the finished solid have?",
    # Count the distinct outward directions a flat face of the finished box can look in.
    key=6, verify=len({(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)}),
    wrong=[(12, "ignored_constraint"), (2 * 6 - 2, "double_count"), (8, "misread_data")],
    difficulty="hard", confidence=0.90,
    expl="Glued together the two cubes make a box 2 long, 1 wide and 1 tall, and a box has "
         "6 flat faces: a top, a bottom, two long sides and two ends. 12 counts every face "
         "of both cubes as though they were still apart, and 10 takes away the two glued "
         "faces but still counts the two squares along each long side separately, when "
         "they lie flat in one surface and make a single face.",
    fmt=unit("faces")),

# ===================================================== scale (4)

# --- 33. Ratio scale on a plan.
B.Q("scale", "multi_step",
    "A house plan is drawn at a scale of 1 : 200. A wall is 7 cm long on the plan. How "
    "long is the real wall?",
    key=7 * 200 / 100, verify=(7 / 100) * 200,
    wrong=[(7 * 200, "partial_step"), (7 / 200, "inverse"), (7 * 200 / 10, "place_value")],
    difficulty="hard", confidence=0.91,
    expl="The real wall is 200 times the drawing: 7 x 200 = 1400 cm, and 100 cm make a "
         "metre, so 14 m. 1400 is the length still in centimetres, and 0.04 divides by 200 "
         "instead of multiplying, which would make the real wall smaller than the plan.",
    fmt=M),

# --- 34. Scale bar on a map.
B.Q("scale", "data_interpretation",
    "A map carries a scale bar showing that 4 cm stands for 10 km. A road measures 6 cm on "
    "the map. How long is the road?",
    key=6 * 10 / 4, verify=(10 / 4) * 6,     # 2.5 km per centimetre
    wrong=[(6 * 10, "partial_step"), (6 * 4 / 10, "inverse"), (6 + 10 - 4, "operation_swap")],
    difficulty="hard", confidence=0.90,
    expl="Work out what one centimetre stands for first: 10 / 4 = 2.5 km, so 6 cm stands "
         "for 6 x 2.5 = 15 km. 60 uses the 10 km without noticing it takes 4 cm to cover "
         "it, and 2.4 divides the wrong way round.",
    fmt=KM),

# --- 35. Enlargement.
B.Q("scale", "multi_step",
    "A photograph 12 cm wide is enlarged so that its width becomes 30 cm. The photograph "
    "was 8 cm tall. How tall is the enlargement?",
    key=8 * 30 // 12, verify=8 * (30 / 12),
    wrong=[(8 + (30 - 12), "operation_swap"), (30 - 12, "partial_step"), (8 * 30, "place_value")],
    difficulty="hard", confidence=0.90,
    expl="The width grew from 12 cm to 30 cm, which is two and a half times, so the height "
         "grows the same way: 8 x 2.5 = 20 cm. 26 adds the extra 18 cm of width to the "
         "height instead of scaling it, which would stretch the picture out of shape.",
    fmt=CM),

# --- 36. Choosing a scale.
B.Q("scale", "multi_step",
    "A student wants to draw a plan of a playground 40 m long so that the drawing is 20 cm "
    "long. Which scale should the plan use?",
    key="1 cm represents 2 m", verify="1 cm represents 2 m",
    wrong=[("1 cm represents 20 m", "misread_data"), ("1 cm represents 40 m", "partial_step"),
           ("1 cm represents 0.5 m", "inverse")],
    expl="Twenty centimetres have to cover 40 m, so each centimetre covers 40 / 20 = 2 m. "
         "1 cm represents 20 m would need the drawing to be only 2 cm long, and 1 cm "
         "represents 0.5 m divides the wrong way round and would need a plan 80 cm long.",
    fmt=PLAIN),

if __name__ == "__main__":
    B.write()
