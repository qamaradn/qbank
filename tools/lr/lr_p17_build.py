#!/usr/bin/env python3
"""Builds lr_thinking_skills_p17.json — 29 figural questions closing §5.4 at 154/154.

shape combination 8, tessellation 7, orientation and rotation 5, segment display 5,
3D views 4. This finishes the family §8 named as the first Thinking Skills priority.

Remaining after this batch: §5.3 problem solving 271 and §5.2 critical thinking 262,
neither of which needs figures.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.figure_lib import (  # noqa: E402
    SEGMENTS, check_stack, iso_stack_fitted, rotate_cells, seven_segment, shapes_row,
    svg, symbol_grid,
)
from tools.lr.lr_common import (  # noqa: E402
    Batch, bounding, perimeter, symmetry_order, tile_by_copies,
)

B = Batch(nn=17)

L4 = [(0, 0), (1, 0), (2, 0), (0, 1)]
T4 = [(0, 0), (1, 0), (2, 0), (1, 1)]
O4 = [(0, 0), (1, 0), (0, 1), (1, 1)]
I4 = [(0, 0), (1, 0), (2, 0), (3, 0)]
I3 = [(0, 0), (1, 0), (2, 0)]
L3 = [(0, 0), (1, 0), (0, 1)]
S4 = [(1, 0), (2, 0), (0, 1), (1, 1)]


def only(cands):
    return cands[0] if len(cands) == 1 else "NOT UNIQUE"


def corners(cells):
    """How many corners the outline of a polyomino turns through. Counted from the cells
    rather than by looking: at every grid point, the number of filled squares around it
    decides whether the outline turns there."""
    s = set(cells)
    pts = {(c + dc, r + dr) for c, r in s for dc in (0, 1) for dr in (0, 1)}
    n = 0
    for x, y in pts:
        around = sum((x - 1 + i, y - 1 + j) in s for i in (0, 1) for j in (0, 1))
        if around in (1, 3):
            n += 1
        elif around == 2 and ((x - 1, y - 1) in s) == ((x, y) in s):
            n += 2                      # two squares meeting only at this point
    return n


def congruent(a, b):
    """True if b is a turn of a — no reflection allowed."""
    return any(rotate_cells(a, k) == sorted(b) for k in range(4))


# ===================================================== shape combination (8)

B.Q("shape_combination",
    "Counting every corner the outline turns through, how many corners does the piece in "
    "the diagram have?",
    key=corners(L4), verify=corners(rotate_cells(L4, 1)),   # turning cannot change it
    wrong=[4, 4 * len(L4), corners(L4) + 2],
    expl="Following the outline of the piece, it turns at 6 corners — five of them turning "
         "outward and one where the shape steps in. 4 would be right for a rectangle, which "
         "is the only shape here with no step in it, and 16 counts four corners for every "
         "square as though the squares were separate.",
    fig=shapes_row([L4], ["the piece"]),
    fmt=lambda v: f"{v} corners", difficulty="hard", confidence=0.90),

_shapes = [L4, rotate_cells(L4, 2), T4]
B.Q("shape_combination",
    "Two of the three pieces in the diagram are the same shape, one simply turned round. "
    "Which piece is the odd one out?",
    key="Piece 3",
    verify=only([f"Piece {i + 1}" for i in range(3)
                 if not any(congruent(_shapes[i], _shapes[j]) for j in range(3) if j != i)]),
    wrong=["Piece 1", "Piece 2", "all three are the same shape"],
    expl="Piece 2 is piece 1 turned upside down, so those two match. Piece 3 has its extra "
         "square in the middle of the row rather than at one end, and no amount of turning "
         "moves it there.",
    fig=shapes_row(_shapes, ["Piece 1", "Piece 2", "Piece 3"]),
    difficulty="hard", confidence=0.91),

B.Q("shape_combination",
    "A rectangle 4 squares by 2 is cut into two pieces. One of them is the piece shown, "
    "which covers 3 squares. How many squares does the other piece cover?",
    key=4 * 2 - len(L3), verify=8 - 3,
    wrong=[len(L3), 4 * 2, 4 * 2 - 1],
    expl="The rectangle covers 4 x 2 = 8 small squares and one piece takes 3, so the other "
         "takes 5. 3 gives back the piece already shown, and 8 forgets the rectangle was "
         "cut at all.",
    fig=shapes_row([L3], ["one piece"]),
    fmt=lambda v: f"{v} squares"),

B.Q("shape_combination",
    "A piece covering 4 small squares is enlarged so that every side is twice as long. How "
    "many small squares does the enlarged piece cover?",
    key=4 * 4, verify=4 * 2 * 2,
    wrong=[4 * 2, 4, 4 * 8],
    expl="Doubling every side doubles the piece in both directions, so the area is "
         "multiplied by 2 x 2 = 4, giving 16 small squares. 8 doubles the area once, which "
         "is what most people expect, but a shape twice as long and twice as wide holds "
         "four times as much. 32 would need every side trebled and then some.",
    fig=shapes_row([O4, tile_by_copies(O4, [(0, 0), (2, 0), (0, 2), (2, 2)])],
                   ["before", "after"]),
    fmt=lambda v: f"{v} squares", difficulty="hard", confidence=0.90),

STEP = tile_by_copies(I3, [(0, 0), (0, 1), (0, 2)])
WIDE2 = tile_by_copies([(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)], [(0, 0), (0, 1)])
B.Q("shape_combination",
    "How many small squares run along the longest side of the shape in the diagram?",
    # STEP is a 3 by 3 block, so its two sides are equal and the "longest side"
    # distractor cannot be the other side; use a wider shape instead
    key=bounding(WIDE2)[0], verify=max(c for c, _ in WIDE2) - min(c for c, _ in WIDE2) + 1,
    wrong=[bounding(WIDE2)[1], len(WIDE2), bounding(WIDE2)[0] + bounding(WIDE2)[1]],
    expl="The shape reaches 5 squares across and 2 squares up, so its longest side is 5 "
         "squares. 2 gives the shorter side, and 10 counts every small square in the shape "
         "rather than the squares along one side.",
    fig=shapes_row([WIDE2], ["the shape"]),
    fmt=lambda v: f"{v} squares"),

B.Q("shape_combination",
    "The two pieces in the diagram are pushed together along a whole edge to make one "
    "shape. How many small squares does that shape cover?",
    key=len(I3) + len(L3), verify=6,
    wrong=[len(I3), len(I3) * len(L3), len(I3) + len(L3) - 1],
    expl="One piece covers 3 small squares and so does the other, giving 6 altogether. "
         "Pushing them together hides some edges but never loses a square, which is why 5 "
         "is wrong. 9 multiplies the two counts instead of adding them.",
    fig=shapes_row([I3, L3], ["Piece 1", "Piece 2"]),
    fmt=lambda v: f"{v} squares"),

B.Q("shape_combination",
    "A square piece 2 squares along each side is cut along one line into two pieces that "
    "are exactly the same shape and size. How many squares does each piece cover?",
    key=len(O4) // 2, verify=2 * 2 // 2,
    wrong=[len(O4), 1, len(O4) * 2],
    expl="The square covers 4 small squares and the two matching pieces share them evenly, "
         "so each covers 2. Cutting straight down the middle gives two pieces 1 square wide "
         "and 2 tall. 4 gives the whole square rather than one of its halves.",
    fig=shapes_row([O4], ["the square"]),
    fmt=lambda v: f"{v} square" + ("" if v == 1 else "s")),

WIDE = tile_by_copies(I4, [(0, 0), (0, 1)])
B.Q("shape_combination",
    "How many copies of the corner piece would exactly cover the rectangle in the diagram?",
    key="none — it cannot be covered exactly",
    verify="none — it cannot be covered exactly" if len(WIDE) % len(L3) else "IT DIVIDES",
    wrong=["2 copies", "3 copies", "4 copies"],
    expl="The rectangle covers 8 small squares and each corner piece covers 3. Since 8 does "
         "not divide by 3, no whole number of copies can fill it exactly — 2 copies leave 2 "
         "squares bare and 3 copies would need 9.",
    fig=shapes_row([L3, WIDE], ["the piece", "the rectangle"]),
    difficulty="hard", confidence=0.91),

# ===================================================== tessellation (7)

# 8 by 5, not 6 by 4: at 6 by 4 the path and the pool both come to 24 tiles, so the
# "you gave the pool" distractor was the same number as the answer
B.Q("tessellation",
    "A rectangular pool 8 tiles by 5 has a path one tile wide laid all the way around it. "
    "How many tiles does the path use?",
    key=(8 + 2) * (5 + 2) - 8 * 5, verify=2 * 8 + 2 * 5 + 4,
    wrong=[8 * 5, 2 * 8 + 2 * 5, (8 + 2) * (5 + 2)],
    expl="Pool and path together measure 10 by 7 = 70 tiles, and the pool itself takes 40, "
         "so the path uses 30. Counting the path directly gives the same: two sides of 8, "
         "two of 5, and the 4 corners. 26 leaves the corners out, and 40 gives the pool.",
    fig=symbol_grid([["" for _ in range(10)] for _ in range(7)], size=23,
                    shade={(r, c) for r in range(1, 6) for c in range(1, 9)}),
    fmt=lambda v: f"{v} tiles", difficulty="hard", confidence=0.90),

SIX = ["A", "B", "C", "D", "E", "F"] * 2
B.Q("tessellation",
    "The tiles in the diagram repeat a group of six letters. Which letter falls at "
    "place 40?",
    key="D", verify=["A", "B", "C", "D", "E", "F"][(40 - 1) % 6],
    wrong=["A", "C", "F"],
    expl="Six tiles make a group, and 40 is 36 plus 4, so place 40 holds the fourth letter "
         "of a group: D. Place 36 would be the F that ends the sixth group.",
    fig=symbol_grid([SIX], size=27), difficulty="hard", confidence=0.91),

FRAC = [["#" if c < 2 else "O" for c in range(5)] for _ in range(4)]
B.Q("tessellation",
    "What fraction of the floor shown is tiled with # tiles?",
    key="2 out of 5",
    verify=f"{sum(r.count('#') for r in FRAC) // 4} out of {len(FRAC[0])}",
    wrong=["2 out of 3", "8 out of 5", "1 out of 2"],
    expl="Two of the five tiles in every row are #, so the # tiles make 2 out of every 5 of "
         "the floor — 8 out of 20 altogether, which is the same fraction. 2 out of 3 "
         "compares the # tiles with the O tiles rather than with the whole floor.",
    fig=symbol_grid(FRAC)),

TWOROW = [["R", "S", "R", "S", "R", "S"],
          ["S", "S", "R", "S", "S", "R"]]        # matches at places 2, 3 and 4
B.Q("tessellation",
    "In the two rows shown, at how many places does the same letter appear in both rows?",
    key=sum(1 for a, b in zip(*TWOROW) if a == b),
    verify=len([i for i in range(6) if TWOROW[0][i] == TWOROW[1][i]]),
    wrong=[6, 2, 0],
    expl="Comparing the rows place by place, the letters match at places 2, 3 and 4 — three "
         "places in all. 6 would mean the two rows were identical, which they are not, and "
         "0 would mean they never agreed.",
    fig=symbol_grid(TWOROW),
    fmt=lambda v: f"{v} place" + ("" if v == 1 else "s"), difficulty="hard", confidence=0.90),

# 24 with groups of 5 leaves 4 over, which is also the number of complete groups — so
# the "you gave the group count" distractor was the same number as the answer
B.Q("tessellation",
    "A path is one tile wide and 27 tiles long. It is tiled with a repeating group of 5 "
    "tiles. How many tiles are left over after the last complete group?",
    key=27 % 5, verify=27 - 5 * (27 // 5),
    wrong=[27 // 5, 27, 0],
    expl="27 divided by 5 is 5 complete groups with 2 tiles left over. 5 is the number of "
         "complete groups rather than the leftover, 27 gives the whole path, and 0 would "
         "mean the groups fitted the path exactly.",
    fig=symbol_grid([["1", "2", "3", "4", "5", "1", "2", "3", "4", "5"]], size=27),
    fmt=lambda v: f"{v} tiles"),

B.Q("tessellation",
    "Which of these shapes will NOT tile a flat surface on its own, leaving no gaps?",
    key="a regular pentagon", verify="a regular pentagon",
    wrong=["a square", "an equilateral triangle", "a regular hexagon"],
    expl="Squares, equilateral triangles and regular hexagons all fit around a point with "
         "no gap — four squares, six triangles or three hexagons. Regular pentagons cannot: "
         "three of them leave a gap and four overlap, which is why no floor is tiled with "
         "them.",
    # no figure: a blank square grid says nothing about pentagons, and an irrelevant
    # picture is worse than none — it invites the reader to look for something in it
    difficulty="hard", confidence=0.90),

B.Q("tessellation",
    "A wall 12 tiles wide and 9 tiles high is tiled. Every third row is a different colour, "
    "starting with row 3. How many tiles are the different colour?",
    key=(9 // 3) * 12, verify=len([r for r in range(1, 10) if r % 3 == 0]) * 12,
    wrong=[9 * 12, 12, 9 // 3],
    expl="Rows 3, 6 and 9 are the different colour — three rows of 12 tiles, which is 36. "
         "12 counts a single row, and 3 counts the rows rather than the tiles in them.",
    fig=symbol_grid([["" for _ in range(12)] for _ in range(9)], size=20,
                    shade={(r, c) for r in range(9) if (r + 1) % 3 == 0 for c in range(12)}),
    fmt=lambda v: f"{v} tiles", difficulty="hard", confidence=0.90),

# ===================================================== orientation and rotation (5)

B.Q("orientation_rotation",
    "The T-shaped piece in the diagram is given a quarter turn anticlockwise. Which way "
    "does the stem of the T point afterwards?",
    key="to the left", verify="to the left",
    wrong=["to the right", "straight up", "straight down"],
    expl="The stem points up to begin with, and a quarter turn anticlockwise carries "
         "anything pointing up round to pointing left. Turning the other way, clockwise, "
         "would send it to the right instead.",
    fig=shapes_row([T4, rotate_cells(T4, 3)], ["before", "after"]),
    difficulty="hard", confidence=0.90),

B.Q("orientation_rotation",
    "In how many different positions can the T-shaped piece be placed, if it may be turned "
    "but not flipped over?",
    key=4 // symmetry_order(T4), verify=len({tuple(rotate_cells(T4, k)) for k in range(4)}),
    wrong=[symmetry_order(T4), 2, 8],
    expl="Turning the piece a quarter turn at a time gives four different positions before "
         "it comes back to where it started, and none of them repeats. A square piece would "
         "give only 1, because every quarter turn leaves it looking the same.",
    fig=shapes_row([T4, rotate_cells(T4, 1), rotate_cells(T4, 2), rotate_cells(T4, 3)],
                   ["start", "one", "two", "three"]),
    fmt=lambda v: f"{v} position" + ("" if v == 1 else "s"),
    difficulty="hard", confidence=0.90),

B.Q("orientation_rotation",
    "A pattern looks exactly the same after a half turn but different after a quarter turn. "
    "How many of the four quarter turns leave it unchanged?",
    key=2, verify=len([k for k in range(4) if k % 2 == 0]),
    wrong=[1, 4, 3],
    expl="A half turn and a full turn both leave it unchanged, and the two odd quarter "
         "turns do not, so 2 of the four. 4 would mean every quarter turn worked, which the "
         "question rules out.",
    fig=shapes_row([S4, rotate_cells(S4, 2)], ["start", "after a half turn"]),
    fmt=lambda v: f"{v} of them"),

B.Q("orientation_rotation",
    "A shape is turned a quarter turn clockwise five times in a row. Where does it finish, "
    "compared with a single quarter turn clockwise?",
    key="in exactly the same position", verify="in exactly the same position"
        if 5 % 4 == 1 else "MISMATCH",
    wrong=["a quarter turn further on", "half a turn further on", "back where it started"],
    expl="Four of the five turns make a full turn, which changes nothing, so the fifth turn "
         "is all that shows: the shape finishes exactly where one quarter turn would put "
         "it. Back where it started would need four turns, or eight.",
    fig=shapes_row([L4, rotate_cells(L4, 1)], ["start", "after five turns"]),
    difficulty="hard", confidence=0.90),

DIAG = {(0, 0), (1, 1), (2, 2)}
B.Q("orientation_rotation",
    "The shaded squares in the diagram run down one diagonal of the grid. After a quarter "
    "turn clockwise, where do they lie?",
    key="down the other diagonal", verify="down the other diagonal",
    wrong=["down the same diagonal", "along the middle row", "down the middle column"],
    expl="A quarter turn carries each corner of the grid to the next one round, so the "
         "diagonal from top-left to bottom-right swings onto the diagonal from top-right to "
         "bottom-left. Only a half turn would leave the same diagonal in place.",
    fig=symbol_grid([["" for _ in range(3)] for _ in range(3)], shade=DIAG),
    difficulty="hard", confidence=0.90),

# ===================================================== 3D views (4)

SA = {(0, 0): 2, (1, 0): 2, (2, 0): 2}
SB = {(0, 0): 3, (1, 0): 2}
_ta, _ca = check_stack(SA)
_tb, _cb = check_stack(SB)

B.Q("spatial_3d_views",
    "The diagram shows one stack of identical cubes. A second stack, not shown, is built "
    "from a column of 3 cubes beside a column of 2. Which stack holds more, and by how "
    "many?",
    key=f"the first, by {_ta - _tb}", verify=f"the first, by {sum(SA.values()) - sum(SB.values())}",
    wrong=[f"the second, by {_ta - _tb}", "they hold the same number", "the first, by 3"],
    expl="The stack in the diagram has three columns of 2, which is 6 cubes. The second "
         "has columns of 3 and 2, which is 5. So the one shown holds 1 more. Being taller "
         "does not make a stack bigger — the second is the taller of the two.",
    fig=svg(iso_stack_fitted(SA)), difficulty="hard", confidence=0.90),

B.Q("spatial_3d_views",
    "The diagram shows a block of cubes 3 long, 1 wide and 2 tall. How many of its cubes "
    "are on the bottom layer?",
    key=3 * 1, verify=len(SA),
    wrong=[_ta, 2, 9],
    expl="The bottom layer is 3 cubes long and 1 wide, so it holds 3 cubes. 6 counts the "
         "whole block, both layers together, and 2 gives the height rather than the layer.",
    fig=svg(iso_stack_fitted(SA)),
    fmt=lambda v: f"{v} cubes"),

B.Q("spatial_3d_views",
    "Looking at the same block from directly in front, along its length, how many cube "
    "faces can be seen?",
    key=3 * 2, verify=_ta,
    wrong=[3, 2, 3 * 2 * 2],
    expl="From the front the block shows a wall 3 cubes wide and 2 high, so 6 faces are "
         "visible. 3 counts one row of that wall and 2 counts one column.",
    fig=svg(iso_stack_fitted(SA)),
    fmt=lambda v: f"{v} faces", difficulty="hard", confidence=0.90),

B.Q("spatial_3d_views",
    "How tall is the tallest column in the stack shown, measured in cubes?",
    key=max(SB.values()), verify=sorted(SB.values())[-1],
    wrong=[_tb, min(SB.values()), _tb + 1],
    expl="The taller of the two columns holds 3 cubes. 5 counts every cube in the stack "
         "rather than the height of one column, and 2 gives the shorter column.",
    fig=svg(iso_stack_fitted(SB)),
    fmt=lambda v: f"{v} cubes"),

# ===================================================== segment display (5)

B.Q("segment_display",
    "How many of the ten digits light exactly six segments on a seven-segment display?",
    key=sum(1 for d in "0123456789" if len(SEGMENTS[d]) == 6),
    verify=len([d for d in SEGMENTS if len(SEGMENTS[d]) == 6]),
    wrong=[1, 6, 10],
    expl="The 0, the 6 and the 9 each light six segments, so 3 of the ten do. 1 would be "
         "right if only the 8 counted, but the 8 lights all seven.",
    fig=seven_segment("069", w=28, gap=13, h=48, t=5),
    fmt=lambda v: f"{v} digit" + ("" if v == 1 else "s"),
    difficulty="hard", confidence=0.90),

_two = min(range(10, 100), key=lambda n: sum(len(SEGMENTS[c]) for c in str(n)))
B.Q("segment_display",
    "Which two-digit number lights the fewest segments on a display?",
    key=11, verify=only([n for n in range(10, 100)
                         if sum(len(SEGMENTS[c]) for c in str(n))
                         == min(sum(len(SEGMENTS[c]) for c in str(m)) for m in range(10, 100))]),
    wrong=[10, 17, 71],
    expl="A 1 lights the fewest segments of any digit, just two, so 11 lights 4 in all — "
         "fewer than any other two-digit number. 10 lights 2 and 6, which is 8, and 17 "
         "lights 2 and 3, which is 5.",
    fig=seven_segment("11"),
    fmt=str, difficulty="hard", confidence=0.91),

B.Q("segment_display",
    "Two segments of this display are broken: the top-left and the bottom-left. Which digit "
    "can still be shown correctly?",
    key=7, verify=only([int(d) for d in "0567"
                        if not ({"f", "e"} & set(SEGMENTS[d]))]),
    wrong=[0, 5, 6],
    expl="A 7 uses only the top segment and the two down the right-hand side, so neither "
         "broken segment touches it. The 0 and the 6 both use the bottom-left, and the 5 "
         "uses the top-left.",
    fig=seven_segment("0567", dead=("f", "e"), w=25, gap=12, h=46, t=5),
    fmt=str, difficulty="hard", confidence=0.90),

B.Q("segment_display",
    "The display shows a year. Counting every digit, how many segments are lit?",
    key=sum(len(SEGMENTS[d]) for d in "2027"), verify=5 + 6 + 5 + 3,
    wrong=[7 * 4, sum(len(SEGMENTS[d]) for d in "2026"), 4],
    expl="The digits light 5, 6, 5 and 3 segments, which comes to 19. 28 counts all seven "
         "segments on each of the four digits, and 22 is the total for 2026, where the last "
         "digit lights 6 rather than 3.",
    fig=seven_segment("2027", w=26, gap=12, h=46, t=5),
    fmt=lambda v: f"{v} segments"),

B.Q("segment_display",
    "A 1 and a 7 are shown side by side. How many segments does the 7 light that the 1 does "
    "not?",
    key=len(set(SEGMENTS["7"]) - set(SEGMENTS["1"])), verify=3 - 2,
    wrong=[3, 2, 0],
    expl="A 7 lights three segments and a 1 lights two of those same three, so the 7 adds "
         "just 1 — the segment across the top. 3 counts every segment the 7 uses rather "
         "than the extra ones.",
    fig=seven_segment("17"),
    fmt=lambda v: f"{v} segment" + ("" if v == 1 else "s")),

if __name__ == "__main__":
    B.write()
