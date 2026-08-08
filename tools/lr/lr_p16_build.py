#!/usr/bin/env python3
"""Builds lr_thinking_skills_p16.json — 32 more figural questions (§5.4).

shape combination 8, tessellation 7, orientation and rotation 7, segment display 6,
3D views 4. Figural reaches 128/154 after this batch, leaving 29 in one more batch.

Where a question asks "which one of these", the check now enumerates every candidate and
fails unless exactly one survives. Three items in this build shipped into a check that
could not see a second correct answer, so uniqueness is verified rather than assumed.
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

B = Batch(nn=16)

L4 = [(0, 0), (1, 0), (2, 0), (0, 1)]
T4 = [(0, 0), (1, 0), (2, 0), (1, 1)]
O4 = [(0, 0), (1, 0), (0, 1), (1, 1)]
I4 = [(0, 0), (1, 0), (2, 0), (3, 0)]
I3 = [(0, 0), (1, 0), (2, 0)]
L3 = [(0, 0), (1, 0), (0, 1)]
S4 = [(1, 0), (2, 0), (0, 1), (1, 1)]
Z5 = [(0, 0), (1, 0), (1, 1), (1, 2), (2, 2)]


def only(cands):
    """The single candidate, or a marker that fails the two-route check if there are
    none or several. A "which one of these" question with two answers is unanswerable."""
    return cands[0] if len(cands) == 1 else "NOT UNIQUE"


# ===================================================== shape combination (8)

# --- 1. Odd one out by area.
_areas = [len(L4), len(T4), len(I3), len(O4)]
B.Q("shape_combination",
    "Three of the four pieces in the diagram cover the same number of small squares. Which "
    "one does not?",
    key="Piece 3",
    verify=only([f"Piece {i + 1}" for i, a in enumerate(_areas) if _areas.count(a) == 1]),
    wrong=["Piece 1", "Piece 2", "Piece 4"],
    expl="Pieces 1, 2 and 4 each cover 4 small squares. Piece 3 covers only 3, so it is the "
         "odd one out. Being a different shape is not the same as covering a different "
         "number of squares — pieces 1, 2 and 4 all look different from each other.",
    fig=shapes_row([L4, T4, I3, O4], ["Piece 1", "Piece 2", "Piece 3", "Piece 4"])),

# --- 2. Perimeter of a notched shape.
NOTCH = tile_by_copies(O4, [(0, 0), (2, 0), (0, 2)])
B.Q("shape_combination",
    "The shape in the diagram is drawn on squared paper with 1 cm squares. How far is it "
    "right round the outside of the shape?",
    key=perimeter(NOTCH), verify=4 * len(NOTCH) - 2 * sum(
        1 for c, r in NOTCH for d in ((1, 0), (0, 1)) if (c + d[0], r + d[1]) in set(NOTCH)),
    wrong=[len(NOTCH), perimeter(NOTCH) - 2, 4 * len(NOTCH)],
    expl="Walking right round the outside of the shape covers 16 cm — the same as round the "
         "4 cm by 4 cm square it sits in, because pushing the step out does not change the "
         "edge. Counting another way: 12 squares have 48 sides between them, and the 16 "
         "joins hide two sides each, leaving 48 - 32 = 16. 48 counts every side of every "
         "square as though none of them touched, and 14 misses the pair of edges at the "
         "inside corner.",
    fig=shapes_row([NOTCH], ["the shape"]),
    fmt=lambda v: f"{v} cm", difficulty="hard", confidence=0.90),

# --- 3. Squares left after removing a piece.
BIG = tile_by_copies(O4, [(0, 0), (2, 0), (0, 2), (2, 2)])
B.Q("shape_combination",
    "The square in the diagram is made of small squares. If one corner piece the size of "
    "piece 1 is taken away, how many small squares are left?",
    key=len(BIG) - len(O4), verify=4 * 4 - 2 * 2,
    wrong=[len(BIG), len(O4), len(BIG) - 1],
    expl="The square covers 16 small squares and the corner piece covers 4, so 12 are left. "
         "16 forgets to take the piece away, and 4 gives the piece that was removed.",
    fig=shapes_row([O4, BIG], ["Piece 1", "the square"]),
    fmt=lambda v: f"{v} squares"),

# --- 4. Largest square inside a piece.
B.Q("shape_combination",
    "What is the largest square of whole small squares that fits inside the piece shown, "
    "without sticking out over its edge?",
    key="1 square by 1 square", verify="1 square by 1 square",
    wrong=["2 squares by 2 squares", "3 squares by 3 squares",
           "the whole piece is already a square"],
    expl="The piece is only ever one square thick along its arms, so no 2 by 2 block of "
         "small squares fits anywhere inside it — the largest square that fits is a single "
         "small square. 2 by 2 would need four small squares meeting at a corner, and the "
         "piece has no such corner.",
    fig=shapes_row([L4], ["the piece"]),
    difficulty="hard", confidence=0.90),

# --- 5. Two piece types filling a rectangle.
B.Q("shape_combination",
    "A rectangle covering 18 small squares is to be filled with pieces that each cover 3 "
    "small squares and pieces that each cover 4. If exactly three of the larger pieces are "
    "used, how many of the smaller ones are needed?",
    key=(18 - 3 * 4) // 3, verify=next(n for n in range(1, 9) if 3 * 4 + 3 * n == 18),
    wrong=[3, 18 - 3 * 4, 3 + (18 - 3 * 4) // 3],
    expl="Three larger pieces cover 3 x 4 = 12 small squares, leaving 18 - 12 = 6, and 6 / 3 "
         "= 2 smaller pieces. 6 gives the squares still to be covered rather than the number "
         "of pieces that cover them, and 5 counts every piece used, large and small.",
    fig=shapes_row([I3, I4], ["small piece", "large piece"]),
    difficulty="hard", confidence=0.90),

# --- 6. Comparing three perimeters.
B.Q("shape_combination",
    "Each small square has sides of 1 cm. Which of the three pieces in the diagram has the "
    "longest distance around its outside?",
    key="Piece 3",
    verify=only([f"Piece {i + 1}" for i, per in enumerate([perimeter(O4), perimeter(I4), perimeter(Z5)])
                 if per == max(perimeter(O4), perimeter(I4), perimeter(Z5))]),
    wrong=["Piece 1", "Piece 2", "they are all the same"],
    expl="Piece 1 measures 8 cm around, piece 2 measures 10 cm and piece 3 measures 12 cm, "
         "so piece 3 has the longest edge. Piece 3 also covers the most squares — a bigger "
         "piece usually has more edge, though a compact shape hides more of it than a "
         "straggling one.",
    fig=shapes_row([O4, I4, Z5], ["Piece 1", "Piece 2", "Piece 3"]),
    difficulty="hard", confidence=0.90),

# --- 7. Which piece completes a rectangle.
B.Q("shape_combination",
    "The piece in the diagram is to be made up into a rectangle 3 squares by 2 by adding "
    "one more piece. What shape must the added piece be?",
    key="a straight piece 2 squares long",
    verify=f"a straight piece {3 * 2 - len(L4)} squares long",
    wrong=["a straight piece 3 squares long", "a corner piece of 3 squares",
           "a square piece of 4 squares"],
    expl="A 3 by 2 rectangle holds 6 small squares and the piece uses 4, so the missing part "
         "covers 2 — and the two empty squares sit side by side, making a straight piece 2 "
         "long. A piece of 3 squares would overfill the rectangle.",
    fig=shapes_row([L4], ["the piece"]),
    difficulty="hard", confidence=0.91),

# --- 8. Copies of a corner piece.
CORNERS = tile_by_copies(L3, [(0, 0), (2, 0), (0, 2), (2, 2)])
B.Q("shape_combination",
    "The shape in the diagram was built from copies of the corner piece, with no gaps and "
    "no overlaps. How many copies does it use?",
    key=len(CORNERS) // len(L3), verify=4,
    wrong=[len(CORNERS), len(L3), len(CORNERS) // len(L3) + 2],
    expl="The shape covers 12 small squares and each corner piece covers 3, so 4 copies "
         "were used. 12 gives the small squares rather than the pieces.",
    fig=shapes_row([L3, CORNERS], ["the piece", "the shape"]),
    fmt=lambda v: f"{v} copies"),

# ===================================================== tessellation (7)

# --- 9. Colour at a position in a four-cycle.
CYC4 = ["W", "X", "Y", "Z"] * 2
B.Q("tessellation",
    "The row of tiles shown repeats the same four letters over and over. Which letter would "
    "be at place 23?",
    key="Y", verify=["W", "X", "Y", "Z"][(23 - 1) % 4],
    wrong=["W", "X", "Z"],
    expl="The pattern repeats every 4 tiles, and 23 is 3 more than 20, so place 23 holds "
         "the third letter of a group: Y. Place 24 would be the Z that ends the group.",
    fig=symbol_grid([CYC4], size=30), difficulty="hard", confidence=0.91),

# --- 10. A double-width border.
B.Q("tessellation",
    "A floor is 8 tiles by 8. The tiles in the outer two rings around the edge are to be "
    "replaced. How many tiles is that?",
    key=8 * 8 - 4 * 4, verify=(8 * 8) - ((8 - 4) * (8 - 4)),
    wrong=[8 * 8, 4 * 8 - 4, 4 * 4],
    expl="Taking off two rings from each side leaves a 4 by 4 block in the middle, so "
         "64 - 16 = 48 tiles are replaced. 28 counts one ring only, and 16 gives the block "
         "left untouched in the middle.",
    fig=symbol_grid([["" for _ in range(8)] for _ in range(8)], size=21),
    fmt=lambda v: f"{v} tiles", difficulty="hard", confidence=0.90),

# --- 11. Missing tile in a pattern.
GAP = [["P", "Q", "P", "Q", "P"],
       ["Q", "P", "Q", "", "Q"],
       ["P", "Q", "P", "Q", "P"]]
B.Q("tessellation",
    "One tile is missing from the pattern in the diagram. Which letter belongs in the gap?",
    key="P", verify="P" if GAP[1][2] == "Q" and GAP[0][3] == "Q" else "MISMATCH",
    wrong=["Q", "either letter would fit", "the pattern is broken and cannot be finished"],
    expl="The letters alternate along every row and down every column. The gap has Q on "
         "both sides of it along its row, and Q above and below it down its column, so it "
         "must be a P.",
    fig=symbol_grid(GAP)),

# --- 12. An L-shaped floor.
B.Q("tessellation",
    "A floor is shaped like a large square 6 tiles by 6, with a square 2 tiles by 2 missing "
    "from one corner. How many tiles does the floor use?",
    key=6 * 6 - 2 * 2, verify=6 * 4 + 4 * 2,
    wrong=[6 * 6, 2 * 2, 6 * 6 + 2 * 2],
    expl="The full square would take 36 tiles and the missing corner accounts for 4, so 32 "
         "are used. Splitting the L into two rectangles gives the same: 6 by 4 is 24, and "
         "4 by 2 is 8. 36 forgets the missing corner.",
    # drawn with shapes_row, not symbol_grid: symbol_grid always draws a full rectangle,
    # so an L-shaped floor came out looking like a plain 6 by 6 square
    fig=shapes_row([[(c, r) for r in range(6) for c in range(6)
                     if not (r >= 4 and c >= 4)]], ["the floor"], size=15),
    fmt=lambda v: f"{v} tiles", difficulty="hard", confidence=0.90),

# --- 13. Which row holds the most of a symbol.
ROWS = [["#", "O", "#", "O", "#", "O"],
        ["#", "#", "O", "#", "#", "O"],
        ["O", "O", "#", "O", "O", "#"]]
B.Q("tessellation",
    "In the tiling shown, which row holds the most # tiles?",
    key="row 2",
    verify=only([f"row {i + 1}" for i, r in enumerate(ROWS)
                 if r.count("#") == max(x.count("#") for x in ROWS)]),
    wrong=["row 1", "row 3", "rows 1 and 2 hold the same number"],
    expl="Row 1 holds 3, row 2 holds 4 and row 3 holds 2, so row 2 has the most. Rows 1 and "
         "2 do not match — row 2 has one more.",
    fig=symbol_grid(ROWS)),

# --- 14. Complete patterns inside a grid.
B.Q("tessellation",
    "A pattern is made from a block of tiles 3 wide and 2 deep. How many complete blocks fit "
    "inside a floor 12 tiles wide and 8 deep?",
    key=(12 // 3) * (8 // 2), verify=(12 * 8) // (3 * 2),
    wrong=[12 * 8, (12 // 3) + (8 // 2), 3 * 2],
    expl="Four blocks fit across the floor and four fit down it, so 4 x 4 = 16 blocks. The "
         "areas agree: 96 tiles divided by the 6 tiles in a block is 16. 8 adds the two "
         "counts instead of multiplying them.",
    fig=symbol_grid([["" for _ in range(12)] for _ in range(8)], size=21),
    fmt=lambda v: f"{v} blocks", difficulty="hard", confidence=0.90),

# --- 15. Tiles along a diagonal.
B.Q("tessellation",
    "A square floor is 7 tiles by 7. How many tiles lie on the diagonal running from one "
    "corner to the opposite corner?",
    key=7, verify=len([i for i in range(7)]),
    wrong=[7 * 7, 7 * 2, 7 - 1],
    expl="The diagonal picks up exactly one tile from each row, and there are 7 rows, so 7 "
         "tiles lie on it. 49 gives the whole floor, and 14 would count both diagonals with "
         "the middle tile twice.",
    fig=symbol_grid([["" for _ in range(7)] for _ in range(7)], size=23),
    fmt=lambda v: f"{v} tiles"),

# ===================================================== orientation and rotation (7)

# --- 16. Which piece is a turn of the first.
_cands = [I4, rotate_cells(L4, 1), O4]
B.Q("orientation_rotation",
    "Which of pieces 2, 3 and 4 in the diagram is piece 1 after being turned?",
    key="Piece 3",
    verify=only([f"Piece {i + 2}" for i, c in enumerate(_cands)
                 if any(rotate_cells(L4, k) == sorted(c) for k in range(4))]),
    wrong=["Piece 2", "Piece 4", "none of them is"],
    expl="Turning piece 1 a quarter turn gives piece 3 exactly. Piece 2 is a straight line "
         "of four and piece 4 is a square, and no amount of turning changes one shape into "
         "another.",
    fig=shapes_row([L4] + _cands, ["Piece 1", "Piece 2", "Piece 3", "Piece 4"]),
    difficulty="hard", confidence=0.91),

# --- 17. Marked square after three turns.
B.Q("orientation_rotation",
    "A square on the piece shown is marked X. The whole piece is given three quarter turns "
    "clockwise. Whereabouts on it does the marked square finish?",
    key="at the left-hand end of the piece", verify="at the left-hand end of the piece",
    wrong=["at the right-hand end of the piece", "at the top of the piece",
           "at the bottom of the piece"],
    expl="Three quarter turns clockwise is the same as one quarter turn anticlockwise. That "
         "swings the upright arm, and the square marked on it, round to the left, so X "
         "finishes at the left-hand end.",
    fig=shapes_row([L4, rotate_cells(L4, 3)], ["before", "after"], marks={0: {(0, 1): "X"}}),
    difficulty="hard", confidence=0.90),

# --- 18. Symmetry of a straight piece.
B.Q("orientation_rotation",
    "A straight piece four squares long is turned right round about its centre. In how many "
    "of the four quarter turns does it look exactly as it did?",
    key=symmetry_order(I4), verify=2,
    wrong=[1, 4, 0],
    expl="A straight line looks the same after a half turn — it simply swaps end for end — "
         "and after a full turn, so 2 of the four leave it unchanged. A quarter turn stands "
         "it upright, which is plainly different.",
    fig=shapes_row([I4, rotate_cells(I4, 1)], ["start", "one turn"]),
    fmt=lambda v: f"{v} of them"),

# --- 19. Turning versus flipping.
B.Q("orientation_rotation",
    "The two pieces in the diagram are mirror images of each other. Can one be turned about "
    "its centre to look exactly like the other?",
    # the key was half again as long as any distractor, which a student can see
    key="no, turning cannot do it",
    verify="no, turning cannot do it"
           if not any(rotate_cells(S4, k) == sorted([(2 - c, r) for c, r in S4]) for k in range(4))
           else "MISMATCH",
    wrong=["yes, a quarter turn does it", "yes, a half turn does it",
           "yes, three quarter turns do it"],
    expl="Trying all four quarter turns on the first piece never produces the second: a turn "
         "keeps the order of the corners the same way round, and a mirror reverses it. That "
         "is why some pieces have a left-handed and a right-handed version.",
    fig=shapes_row([S4, [(2 - c, r) for c, r in S4]], ["Piece 1", "Piece 2"]),
    difficulty="hard", confidence=0.90),

# --- 20. Shading after three turns.
B.Q("orientation_rotation",
    "Three quarter turns clockwise are made to the 3 by 3 grid shown. In which corner do the "
    "shaded squares end up?",
    key="the bottom-left corner", verify="the bottom-left corner",
    wrong=["the top-right corner", "the bottom-right corner",
           "they stay in the top-left corner"],
    expl="One quarter turn carries the top-left corner to the top-right, a second to the "
         "bottom-right and a third to the bottom-left. Stopping after one turn gives the "
         "top-right, which is the commonest slip.",
    fig=symbol_grid([["" for _ in range(3)] for _ in range(3)], shade={(0, 0), (0, 1), (1, 0)}),
    difficulty="hard", confidence=0.90),

# --- 21. Turns to make a full turn.
B.Q("orientation_rotation",
    "A pattern has already been turned two quarter turns clockwise. How many more quarter "
    "turns in the same direction bring it back to where it started?",
    key=4 - 2, verify=next(k for k in range(1, 5) if (2 + k) % 4 == 0),
    wrong=[4, 1, 3],
    expl="Four quarter turns make a full turn, and two have been done, so 2 more finish it. "
         "4 would take the pattern a full turn past where it started.",
    fig=shapes_row([T4, rotate_cells(T4, 2)], ["start", "after two turns"]),
    fmt=lambda v: f"{v} more"),

# --- 22. Rotational symmetry of a grid pattern.
def _turned(cells, k):
    """Rotate a set of grid squares a quarter turn clockwise, k times, inside a 3 by 3."""
    out = set(cells)
    for _ in range(k % 4):
        out = {(r, 2 - c) for c, r in out}
    return out


PIN = {(0, 1), (1, 0), (1, 2), (2, 1)}
B.Q("orientation_rotation",
    "The shaded pattern in the diagram is turned about the centre of the grid. In how many "
    "of the four quarter turns does it look exactly the same?",
    # apply the quarter turn k times, rather than once regardless of k
    key=4,
    verify=sum(1 for k in range(4)
               if _turned(PIN, k) == PIN),
    wrong=[1, 2, 0],
    expl="The four shaded squares sit one in the middle of each edge, so turning the grid a "
         "quarter turn moves each of them onto the next, and the pattern looks unchanged "
         "every time: all 4. A pattern shaded in one corner only would look the same after "
         "a full turn alone.",
    fig=symbol_grid([["" for _ in range(3)] for _ in range(3)], shade={(1, 0), (0, 1), (2, 1), (1, 2)}),
    fmt=lambda v: f"{v} of them", difficulty="hard", confidence=0.90),

# ===================================================== 3D views (4)

ST3 = {(0, 0): 2, (1, 0): 2, (0, 1): 2, (1, 1): 2}
ST4 = {(0, 0): 3, (1, 0): 2, (2, 0): 1}
_t3, _c3 = check_stack(ST3)
_t4, _c4 = check_stack(ST4)

B.Q("spatial_3d_views",
    "The diagram shows cubes stacked into a solid block. How many cubes make up the block?",
    key=_t3, verify=2 * 2 * 2,
    wrong=[_c3, _t3 - 2, max(ST3.values())],
    expl="The block is 2 cubes long, 2 wide and 2 tall, so it holds 2 x 2 x 2 = 8 cubes. "
         "4 counts the columns and forgets that each is two cubes tall.",
    fig=svg(iso_stack_fitted(ST3)),
    fmt=lambda v: f"{v} cubes"),

B.Q("spatial_3d_views",
    "Looking at the block in the diagram, how many of its cubes have no cube resting on "
    "top of them?",
    key=_c3, verify=len(ST3),
    wrong=[_t3, 2, 1],
    expl="Only the top cube of each column has nothing above it, and there are 4 columns, "
         "so 4 cubes are clear on top. 8 counts every cube in the block, and 1 would be "
         "right only if the block came to a single point at the top.",
    fig=svg(iso_stack_fitted(ST3)),
    fmt=lambda v: f"{v} cube" + ("" if v == 1 else "s"), difficulty="hard", confidence=0.90),

B.Q("spatial_3d_views",
    "The diagram shows a staircase of cubes. How many cubes does it use?",
    key=_t4, verify=3 + 2 + 1,
    wrong=[_c4, max(ST4.values()) * _c4, _t4 + 1],
    expl="The three columns are 3, 2 and 1 cubes tall, which comes to 6. 9 assumes every "
         "column is as tall as the tallest, and 3 counts the columns.",
    fig=svg(iso_stack_fitted(ST4)),
    fmt=lambda v: f"{v} cubes"),

B.Q("spatial_3d_views",
    "How many more cubes would turn the staircase in the diagram into a solid block 3 cubes "
    "long, 1 wide and 3 tall?",
    key=3 * 1 * 3 - _t4, verify=sum(3 - h for h in ST4.values()),
    wrong=[3 * 1 * 3, _t4, 3 * 1 * 4],
    expl="The finished block would hold 3 x 3 = 9 cubes and the staircase has 6, so 3 more "
         "are needed. Filling each column up to 3 gives the same: 0 + 1 + 2 = 3. 9 gives "
         "the size of the finished block rather than what has to be added, and 12 comes "
         "from building it four cubes tall instead of three.",
    fig=svg(iso_stack_fitted(ST4)),
    fmt=lambda v: f"{v} cubes", difficulty="hard", confidence=0.90),

# ===================================================== segment display (6)

B.Q("segment_display",
    "On a seven-segment display, which digit uses exactly four segments?",
    key=4, verify=int(only([d for d in "0123456789" if len(SEGMENTS[d]) == 4])),
    wrong=[7, 1, 2],
    expl="A 4 lights four segments: the two down the right-hand side, the top-left and the "
         "middle. A 7 uses three, a 1 uses two and a 2 uses five.",
    fig=seven_segment("1247", w=25, gap=12, h=46, t=5),
    fmt=str),

B.Q("segment_display",
    "How many of the ten digits use the middle segment of a seven-segment display?",
    key=sum(1 for d in "0123456789" if "g" in SEGMENTS[d]),
    verify=len([d for d in SEGMENTS if "g" in SEGMENTS[d]]),
    wrong=[10, sum(1 for d in "0123456789" if "g" not in SEGMENTS[d]), 5],
    expl="Every digit uses the middle segment except 0, 1 and 7, so 7 of the ten do. 3 "
         "counts the digits that do not, which is the opposite question, and 10 would mean "
         "no digit could be drawn without it.",
    fig=seven_segment("0123456789", w=20, gap=6, h=36, t=4),
    fmt=lambda v: f"{v} digits", difficulty="hard", confidence=0.90),

B.Q("segment_display",
    "By how many segments do a 6 and an 8 differ on a seven-segment display?",
    key=len(set(SEGMENTS["8"]) ^ set(SEGMENTS["6"])),
    verify=abs(len(SEGMENTS["8"]) - len(SEGMENTS["6"])),
    wrong=[2, 0, 6],
    expl="An 8 lights all seven segments and a 6 lights six of them, missing only the "
         "top-right, so they differ by 1. 0 would mean the two looked identical, which they "
         "do not.",
    fig=seven_segment("68"),
    fmt=lambda v: f"{v} segment" + ("" if v == 1 else "s")),

B.Q("segment_display",
    "Adding up all four digits on the display shown, how many segments are lit?",
    key=sum(len(SEGMENTS[d]) for d in "1348"), verify=2 + 5 + 4 + 7,
    wrong=[7 * 4, 4, sum(len(SEGMENTS[d]) for d in "134")],
    expl="The 1 lights 2, the 3 lights 5, the 4 lights 4 and the 8 lights all 7, giving 18. "
         "28 counts every segment on each digit whether it lights or not.",
    fig=seven_segment("1348", w=26, gap=12, h=46, t=5),
    fmt=lambda v: f"{v} segments"),

B.Q("segment_display",
    "The bottom segment of this display is broken and cannot light. Which of the digits "
    "shown is unaffected by it?",
    key=4, verify=int(only([d for d in "0234" if "d" not in SEGMENTS[d]])),
    wrong=[0, 2, 3],
    expl="A 4 lights the two right-hand segments, the top-left and the middle, and none of "
         "those is the bottom one, so it comes out unchanged. The 0, the 2 and the 3 all "
         "use the bottom segment to close their shape.",
    fig=seven_segment("0234", dead=("d",), w=25, gap=12, h=46, t=5),
    fmt=str, difficulty="hard", confidence=0.90),

B.Q("segment_display",
    "A display shows a two-digit number using 9 segments in total. The first digit is a 1. "
    "What is the second digit?",
    key=8, verify=int(only([d for d in "0123456789"
                            if len(SEGMENTS["1"]) + len(SEGMENTS[d]) == 9])),
    wrong=[7, 4, 9],
    expl="A 1 uses 2 segments, so the second digit must use 9 - 2 = 7 of them, and the 8 is "
         "the only digit that lights all seven. A 9 lights six and a 4 lights four.",
    fig=seven_segment("18"),
    fmt=str, difficulty="hard", confidence=0.90),

if __name__ == "__main__":
    B.write()
