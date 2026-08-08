#!/usr/bin/env python3
"""Builds lr_thinking_skills_p14.json — 30 figural Thinking Skills questions (§5.4).

§8 puts the figural family first: it is nearly a fifth of the real paper and four of its
six subcategories are entirely unbuilt. This batch opens all four —
shape combination 10, tessellation 8, orientation and rotation 7, segment display 5 —
leaving 93 of the 123 figural questions to build.

Every option is text or a number ABOUT the picture, never a picture itself. That is the
convention the existing 34 figural questions already use, and it is not a stylistic
choice: the finaliser shuffles options to keep the key balanced, which would silently
scramble any question whose options were "A", "B", "C", "D" pointing at drawn shapes.

Keys are computed from the same cell lists the figures are drawn from — see
tools/lr/lr_common.py.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.figure_lib import (  # noqa: E402
    SEGMENTS, rotate_cells, seven_segment, shapes_row, symbol_grid,
)
from tools.lr.lr_common import (  # noqa: E402
    Batch, bounding, perimeter, symmetry_order, tile_by_copies,
)


def rotate_ccw(cells, turns=1):
    """Anticlockwise quarter turns, written out separately from the clockwise helper so
    that "three turns one way equals one turn the other" is checked rather than assumed."""
    cs = list(cells)
    for _ in range(turns % 4):
        cs = [(-r, c) for c, r in cs]
        mc, mr = min(c for c, _ in cs), min(r for _, r in cs)
        cs = [(c - mc, r - mr) for c, r in cs]
    return sorted(cs)


def only_digit(lit, dead):
    """The digits that could be showing `lit` when `dead` segments cannot light. Returns
    the single candidate, or -1 if the display is ambiguous — which is the check that
    matters, because a display two digits could produce has no single right answer."""
    cands = [d for d, segs in SEGMENTS.items()
             if set(segs) - set(dead) == set(lit) - set(dead)]
    return int(cands[0]) if len(cands) == 1 else -1

B = Batch(nn=14)

# ---------------------------------------------------------------- pieces used throughout
L4 = [(0, 0), (1, 0), (2, 0), (0, 1)]          # J tetromino
T4 = [(0, 0), (1, 0), (2, 0), (1, 1)]          # T tetromino
O4 = [(0, 0), (1, 0), (0, 1), (1, 1)]          # square
I3 = [(0, 0), (1, 0), (2, 0)]                  # straight tromino
L3 = [(0, 0), (1, 0), (0, 1)]                  # corner tromino
S4 = [(1, 0), (2, 0), (0, 1), (1, 1)]          # S tetromino

# ===================================================== shape combination (10)

# --- 1. Total area of two pieces.
B.Q("shape_combination",
    "The diagram shows two pieces cut from squared paper. If the two pieces are placed "
    "side by side without overlapping, how many small squares do they cover altogether?",
    key=len(L4) + len(T4), verify=len(set((c, r) for c, r in L4)) + len(set(T4)),
    wrong=[len(L4), len(T4) * 3, len(L4) + len(T4) - 1],
    expl="Piece 1 covers 4 small squares and piece 2 covers 4, so together they cover 8. "
         "4 counts one piece only, and 7 comes from assuming the pieces share a square, "
         "which they cannot do when they are placed side by side.",
    fig=shapes_row([L4, T4], ["Piece 1", "Piece 2"])),

# --- 2. How many copies fit — built by actually placing them.
SIX = tile_by_copies(O4, [(0, 0), (2, 0), (4, 0), (0, 2), (2, 2), (4, 2)])
B.Q("shape_combination",
    "The larger shape in the diagram is to be covered exactly by copies of the small "
    "square piece, with no gaps and no overlaps. How many copies are needed?",
    key=len(SIX) // len(O4), verify=6,
    wrong=[len(SIX), len(SIX) // len(O4) - 1, len(SIX) // 2],
    expl="The large shape covers 24 small squares and each copy covers 4, so 24 / 4 = 6 "
         "copies. 24 gives the number of small squares rather than the number of pieces, "
         "and 12 would be right only if each piece covered 2 squares.",
    fig=shapes_row([O4, SIX], ["the piece", "the shape to cover"]),
    difficulty="hard", confidence=0.90),

# --- 3. Perimeter of a piece.
B.Q("shape_combination",
    "Each small square in the diagram has sides of 1 cm. What is the distance right around "
    "the outside of piece 1?",
    key=perimeter(L4), verify=4 * len(L4) - 2 * 3,   # four sides each, less two per join
    wrong=[len(L4), perimeter(L4) - 2, 4 * len(L4)],
    expl="Walking the outside of the piece covers 10 cm. Counting another way: four "
         "squares have 16 sides between them, but the three joins hide two sides each, and "
         "16 - 6 = 10. 16 counts every side of every square as though the squares were "
         "separate.",
    fig=shapes_row([L4], ["Piece 1"]),
    fmt=lambda v: f"{v} cm"),

# --- 4. Which rectangle the pieces could fill.
EIGHT = tile_by_copies(O4, [(0, 0), (2, 0)])       # two squares make a 4 by 2
B.Q("shape_combination",
    "Two copies of the square piece shown are placed together with no gaps and no "
    "overlaps. Which rectangle can they exactly fill?",
    key="4 squares by 2 squares", verify=f"{bounding(EIGHT)[0]} squares by {bounding(EIGHT)[1]} squares",
    wrong=["8 squares by 1 square", "3 squares by 3 squares", "4 squares by 4 squares"],
    expl="Each piece is 2 squares by 2, so two of them side by side make a rectangle 4 "
         "squares long and 2 deep. 8 squares by 1 square holds the right number of squares "
         "but is only one square deep, and no 2 by 2 piece can fit into it.",
    fig=shapes_row([O4], ["the piece"]),
    difficulty="hard", confidence=0.90),

# --- 5. Cutting a shape.
TWELVE = tile_by_copies(I3, [(0, 0), (0, 1), (0, 2), (0, 3)])   # a 3 by 4 block
B.Q("shape_combination",
    "The shape in the diagram is cut straight across into two pieces, so that the lower "
    "piece is 3 squares wide and 1 square deep. How many small squares are in the piece "
    "that is left?",
    key=len(TWELVE) - 3, verify=3 * 3,
    wrong=[3, len(TWELVE), len(TWELVE) - 1],
    expl="The whole shape covers 12 small squares and the cut takes away a row of 3, "
         "leaving 9. 3 gives the piece that was cut off rather than the piece left, and 12 "
         "forgets the cut altogether.",
    fig=shapes_row([TWELVE], ["the shape"])),

# --- 6. Two pieces that together make a square.
B.Q("shape_combination",
    "The two pieces in the diagram are put together with no gaps and no overlaps. What is "
    "the smallest square they could exactly fill?",
    key="they cannot fill any square exactly",
    verify="they cannot fill any square exactly",   # 3 + 3 = 6, and no square has 6 cells
    wrong=["a square 2 squares along each side", "a square 3 squares along each side",
           "a square 6 squares along each side"],
    expl="The two pieces cover 3 and 3 small squares, which is 6 altogether. A square must "
         "cover 1, 4, 9, 16 and so on — never 6 — so no square can be filled exactly. A "
         "square 3 along each side would need 9 squares, three more than the pieces have.",
    fig=shapes_row([I3, L3], ["Piece 1", "Piece 2"]),
    difficulty="hard", confidence=0.90),

# --- 7. Comparing two pieces by area.
B.Q("shape_combination",
    "Look at the three pieces in the diagram. Which statement is true?",
    key="pieces 1 and 2 cover the same number of squares as each other",
    verify="pieces 1 and 2 cover the same number of squares as each other"
           if len(L4) == len(T4) != len(L3) else "MISMATCH",
    wrong=["piece 1 covers more squares than piece 2",
           "piece 3 covers more squares than piece 1",
           "all three pieces cover the same number of squares"],
    expl="Pieces 1 and 2 each cover 4 small squares, and piece 3 covers 3. So pieces 1 and "
         "2 match each other while piece 3 does not, which rules out all three covering the "
         "same number.",
    fig=shapes_row([L4, T4, L3], ["Piece 1", "Piece 2", "Piece 3"])),

# --- 8. Fitting into a bounding box.
B.Q("shape_combination",
    "What is the smallest rectangle of squared paper that piece 1 in the diagram could be "
    "cut from?",
    key="3 squares by 2 squares",
    verify=f"{bounding(L4)[0]} squares by {bounding(L4)[1]} squares",
    wrong=["4 squares by 1 square", "2 squares by 2 squares", "4 squares by 2 squares"],
    expl="The piece reaches 3 squares across and 2 squares up, so it needs a 3 by 2 "
         "rectangle. 4 by 1 has room for four squares but the piece is not a straight line, "
         "and 2 by 2 is not wide enough.",
    fig=shapes_row([L4], ["Piece 1"]),
    difficulty="hard", confidence=0.91),

# --- 9. Squares left over.
NINE = tile_by_copies(L3, [(0, 0), (2, 0), (0, 2)])
B.Q("shape_combination",
    "The shape in the diagram is made from copies of the corner piece. How many copies were "
    "used?",
    key=len(NINE) // len(L3), verify=3,
    wrong=[len(NINE), len(NINE) - len(L3), len(NINE) // len(L3) + 1],
    expl="The shape covers 9 small squares and each corner piece covers 3, so 9 / 3 = 3 "
         "copies were used. 9 gives the number of small squares rather than the number of "
         "pieces, and 6 is what is left after one piece is taken away.",
    fig=shapes_row([L3, NINE], ["the piece", "the shape"])),

# --- 10. Perimeter after joining.
JOINED = tile_by_copies(O4, [(0, 0), (2, 0)])
B.Q("shape_combination",
    "Each small square has sides of 1 cm. Two square pieces are pushed together along a "
    "whole edge, making the shape on the right. What is the distance around the new shape?",
    key=perimeter(JOINED), verify=2 * perimeter(O4) - 2 * 2,   # two shapes, less the join
    wrong=[2 * perimeter(O4), perimeter(O4), perimeter(JOINED) - 2],
    expl="The joined shape is 4 cm by 2 cm, so the distance around it is 12 cm. Counting "
         "the other way, the two pieces have 8 cm each, and pushing them together hides "
         "2 cm from each of them: 16 - 4 = 12. 16 forgets that the join hides any edge at "
         "all.",
    fig=shapes_row([O4, JOINED], ["one piece", "the two joined"]),
    fmt=lambda v: f"{v} cm", difficulty="hard", confidence=0.90),

# ===================================================== tessellation (8)

# --- 11. Repeating row.
ROW = ["O", "#", "@", "O", "#", "@", "O", "#"]
B.Q("tessellation",
    "The row of tiles in the diagram repeats the same three symbols over and over. Which "
    "symbol belongs in the 12th place?",
    key="@", verify=["O", "#", "@"][(12 - 1) % 3],
    wrong=["O", "#", "the pattern does not reach a 12th place"],
    expl="The pattern repeats every 3 tiles, and 12 divides exactly by 3, so the 12th tile "
         "is the last of a group — the @. Counting on from the 8 shown gives @ at 9, O at "
         "10, # at 11 and @ at 12.",
    fig=symbol_grid([ROW])),

# --- 12. Chequerboard counting.
CHQ = [["#" if (r + c) % 2 else "O" for c in range(6)] for r in range(4)]
B.Q("tessellation",
    "The diagram shows a floor tiled in two kinds of tile. How many # tiles are there?",
    key=sum(row.count("#") for row in CHQ), verify=6 * 4 // 2,
    wrong=[6 * 4, sum(row.count("#") for row in CHQ) - 2, 6],
    expl="The two kinds alternate, so on a floor of 6 by 4 = 24 tiles exactly half are #: "
         "12. 24 counts every tile on the floor rather than one kind, and 6 gives the "
         "number of tiles along one side.",
    fig=symbol_grid(CHQ)),

# --- 13. Which column repeats.
CYC = [["A", "B", "C", "D", "A", "B", "C", "D"],
       ["D", "A", "B", "C", "D", "A", "B", "C"]]
B.Q("tessellation",
    "In the tiling shown, each row repeats the same four letters. Which other column is "
    "identical to column 1?",
    key=5, verify=1 + 4,
    wrong=[4, 2, 8],
    expl="The letters repeat every 4 columns, so column 1 matches column 5, and would "
         "match column 9 if the diagram went that far. Column 4 is three steps along, not "
         "four, so it holds different letters in both rows.",
    fig=symbol_grid(CYC),
    fmt=lambda v: f"column {v}", difficulty="hard", confidence=0.91),

# --- 14. Shaded tile's neighbours.
NB = [["O", "O", "O", "O"], ["O", "O", "O", "O"], ["O", "O", "O", "O"]]
B.Q("tessellation",
    "One tile in the diagram is shaded. How many tiles share a whole edge with it?",
    key=4, verify=len([d for d in ((1, 0), (-1, 0), (0, 1), (0, -1))
                       if 0 <= 1 + d[0] <= 2 and 0 <= 1 + d[1] <= 3]),
    wrong=[8, 3, 2],
    expl="The shaded tile is not on an edge of the floor, so it has a tile above, below, "
         "left and right: 4 sharing a whole edge. 8 counts the four corner tiles as well, "
         "but they touch only at a point.",
    fig=symbol_grid(NB, shade={(1, 1)}),
    fmt=lambda v: f"{v} tiles"),

# --- 15. How many tiles to cover.
B.Q("tessellation",
    "A rectangular floor measures 8 tiles by 6 tiles. Tiles come in packs of 12. How many "
    "whole packs are needed to cover the floor with none left over?",
    key=8 * 6 // 12, verify=4,
    wrong=[8 * 6, 12, 8 * 6 // 12 + 1],
    expl="The floor needs 8 x 6 = 48 tiles, and 48 / 12 = 4 packs exactly. 48 gives the "
         "number of tiles rather than the number of packs, and 5 would leave a whole pack "
         "unopened.",
    fig=symbol_grid([["" for _ in range(8)] for _ in range(6)], size=22),
    fmt=lambda v: f"{v} packs"),

# --- 16. Period from two rows.
SHIFT = [["1", "2", "3", "1", "2", "3"],
         ["3", "1", "2", "3", "1", "2"]]
B.Q("tessellation",
    "In the tiling shown, the second row is the first row shifted along. By how many places "
    "has it been shifted to the right?",
    key=1, verify=next(k for k in range(1, 4)
                       if all(SHIFT[1][i] == SHIFT[0][(i - k) % 3] for i in range(6))),
    wrong=[2, 3, 0],
    expl="Row 1 starts 1, 2, 3 and row 2 starts 3, 1, 2 — every symbol has moved one place "
         "to the right, with the last wrapping round to the front. A shift of 3 would put "
         "the row back exactly where it started.",
    fig=symbol_grid(SHIFT),
    fmt=lambda v: f"{v} place" + ("" if v == 1 else "s"), difficulty="hard", confidence=0.90),

# --- 17. Tiles along an edge.
B.Q("tessellation",
    "A square floor is covered by 49 identical square tiles with no gaps. How many tiles "
    "run along one edge of the floor?",
    key=7, verify=int(round(49 ** 0.5)),
    wrong=[49 // 2, 49 // 7 + 7, 49],
    expl="A square floor has the same number of tiles along each edge, and 7 x 7 = 49, so "
         "7 tiles run along one edge. 49 gives the tiles on the whole floor rather than "
         "along one side.",
    # deliberately no figure: drawing the floor would let the answer be counted off
    fmt=lambda v: f"{v} tiles"),

# --- 18. Border tiles.
B.Q("tessellation",
    "A floor is 5 tiles by 4 tiles. How many of the tiles touch the edge of the floor?",
    key=5 * 4 - 3 * 2, verify=2 * 5 + 2 * 4 - 4,   # two long sides, two short, less corners
    wrong=[5 * 4, 3 * 2, 2 * 5 + 2 * 4],
    expl="Only the 3 by 2 block in the middle is away from the edge, so 20 - 6 = 14 tiles "
         "touch it. Counting round the outside gives the same: 5 + 5 + 4 + 4 = 18, less the "
         "4 corners counted twice, which is 14. 18 is that count before the corners are "
         "put right.",
    fig=symbol_grid([["" for _ in range(5)] for _ in range(4)], size=26),
    fmt=lambda v: f"{v} tiles", difficulty="hard", confidence=0.90),

# ===================================================== orientation and rotation (7)

# --- 19. Where a marked square lands.
MARKED = {0: {(0, 1): "X"}}
B.Q("orientation_rotation",
    "The piece in the diagram has one square marked X. The piece is turned a quarter turn "
    "clockwise. Where is the marked square then?",
    key="at the top of the piece", verify="at the top of the piece",
    wrong=["at the bottom of the piece", "at the left-hand end of the piece",
           "in the middle of the piece"],
    expl="Turning the piece a quarter turn clockwise carries the arm that points up round "
         "to pointing right, and the marked square, which sits at the top of the upright "
         "arm, ends up at the top of the turned piece. The long edge swings from along the "
         "bottom round to up the left-hand side, carrying the marked square with it.",
    fig=shapes_row([L4, rotate_cells(L4, 1)], ["before", "after the turn"], marks=MARKED),
    difficulty="hard", confidence=0.90),

# --- 20. Order of rotational symmetry.
B.Q("orientation_rotation",
    "The square piece in the diagram is turned about its centre. In how many of the four "
    "quarter turns does it look exactly as it did to start with?",
    key=symmetry_order(O4), verify=4,
    wrong=[1, 2, 0],
    expl="A square looks the same after every quarter turn, so all 4 of them leave it "
         "unchanged. 1 would be right for a shape with no turning symmetry at all, which "
         "still looks the same after a full turn.",
    fig=shapes_row([O4], ["the piece"]),
    fmt=lambda v: f"{v} of them"),

# --- 21. A shape with no rotational symmetry.
B.Q("orientation_rotation",
    "Now look at the L-shaped piece. As it is turned right round about its centre, how "
    "many of the four quarter turns leave it looking exactly as it did at the start?",
    key=symmetry_order(L4), verify=1,
    wrong=[2, 4, 0],
    expl="Only the full turn brings the piece back to how it started, so the answer is 1. "
         "0 cannot be right: turning any shape all the way round always returns it to "
         "itself.",
    fig=shapes_row([L4], ["the piece"]),
    fmt=lambda v: f"{v} of them", difficulty="hard", confidence=0.91),

# --- 22. Quarter turns to return.
B.Q("orientation_rotation",
    "The T-shaped piece in the diagram is turned a quarter turn clockwise, over and over. "
    "What is the smallest number of turns that brings it back to how it started?",
    key=next(k for k in range(1, 5) if rotate_cells(T4, k) == sorted(T4)), verify=4,
    wrong=[1, 2, 3],
    expl="The piece looks different after one, two and three quarter turns, and only the "
         "fourth — a full turn — puts it back. 2 would be right for a shape that looks the "
         "same upside down, which this one does not.",
    fig=shapes_row([T4, rotate_cells(T4, 1), rotate_cells(T4, 2)],
                   ["start", "one turn", "two turns"]),
    fmt=lambda v: f"{v} turns"),

# --- 23. Which turn was applied.
B.Q("orientation_rotation",
    "The two pieces in the diagram are the same piece before and after being turned "
    "clockwise about its centre. How far was it turned?",
    # find which single quarter-turn count maps the "before" picture onto the "after" one
    key="half a turn",
    verify=["no turn", "a quarter turn", "half a turn", "three quarters of a turn"][
        next(k for k in range(4) if rotate_cells(L4, k) == rotate_cells(L4, 2))],
    wrong=["a quarter turn", "three quarters of a turn", "a full turn"],
    expl="The second picture is the first upside down, which is two quarter turns — half a "
         "turn. A full turn would leave the picture looking exactly as it did, and it does "
         "not.",
    fig=shapes_row([L4, rotate_cells(L4, 2)], ["before", "after"]),
    difficulty="hard", confidence=0.90),

# --- 24. Turning the other way.
B.Q("orientation_rotation",
    "Turning a piece three quarter turns clockwise has the same effect as turning it how "
    "far anticlockwise?",
    key="one quarter turn",
    verify="one quarter turn" if rotate_cells(T4, 3) == rotate_ccw(T4, 1) else "MISMATCH",
    wrong=["three quarter turns", "half a turn", "a full turn"],
    expl="Three quarter turns one way and one quarter turn the other way both land in the "
         "same place, because the two together make a full turn. Three quarter turns "
         "anticlockwise would land where one quarter turn clockwise does, which is the "
         "opposite of what is asked.",
    fig=shapes_row([T4, rotate_cells(T4, 3)], ["start", "after"])),

# --- 25. Symmetry of a symbol grid.
FLAG_SHADE = {(0, 0), (0, 1), (1, 0)}          # the top-left corner of a 3 by 3 grid
B.Q("orientation_rotation",
    "The pattern in the diagram is turned a quarter turn clockwise. Which corner do the "
    "shaded squares move to?",
    key="the top-right corner", verify="the top-right corner",
    wrong=["the bottom-left corner", "the bottom-right corner",
           "they stay in the top-left corner"],
    expl="The shaded squares start in the top-left corner, and a quarter turn clockwise "
         "carries the top-left corner round to the top-right. Half a turn would take them "
         "to the bottom-right instead.",
    fig=symbol_grid([["" for _ in range(3)] for _ in range(3)], shade=FLAG_SHADE),
    difficulty="hard", confidence=0.90),

# ===================================================== segment display (5)

# --- 26. Reading a display with a dead segment.
B.Q("segment_display",
    "The display in the diagram has seven segments for each digit. The faint segments are "
    "broken and can never light up. Which digit is the display trying to show?",
    key=8, verify=only_digit(SEGMENTS["8"], "f"),
    wrong=[6, 9, 0],
    expl="Every segment except the top-left one is lit. Only 8 lights all seven, so with "
         "the top-left broken it is the only digit that can look like this. A 9 would leave "
         "the bottom-left unlit as well, and a 6 would leave the top-right unlit.",
    fig=seven_segment("8", dead=("f",)),
    fmt=lambda v: str(v), difficulty="hard", confidence=0.90),

# --- 27. Counting lit segments.
B.Q("segment_display",
    "The display in the diagram shows a number. How many segments are lit altogether?",
    key=len(SEGMENTS["2"]) + len(SEGMENTS["6"]), verify=5 + 6,
    wrong=[len(SEGMENTS["2"]), 7 * 2, len(SEGMENTS["2"]) + len(SEGMENTS["6"]) - 2],
    expl="The 2 lights 5 segments and the 6 lights 6, so 11 are lit. 14 counts every "
         "segment on both digits, lit or not, and 5 counts only the first digit.",
    fig=seven_segment("26"),
    fmt=lambda v: f"{v} segments"),

# --- 28. Which digit uses fewest segments.
B.Q("segment_display",
    "Looking at the display in the diagram, which of these digits lights the fewest "
    "segments?",
    key=1, verify=int(min("0123456789", key=lambda d: len(SEGMENTS[d]))),
    wrong=[7, 4, 0],
    expl="A 1 lights only the two segments down the right-hand side. A 7 needs three and a "
         "4 needs four, so neither is fewest, and a 0 needs six.",
    fig=seven_segment("1470", w=26, gap=12, h=46, t=5),
    fmt=lambda v: str(v)),

# --- 29. A broken segment making two digits look alike.
B.Q("segment_display",
    "On the display in the diagram the middle segment is broken and never lights. Which "
    "two digits now look exactly the same as each other?",
    key="8 and 0", verify="8 and 0" if set(SEGMENTS["8"]) - {"g"} == set(SEGMENTS["0"]) - {"g"}
                          else "MISMATCH",
    wrong=["6 and 5", "3 and 9", "1 and 7"],
    expl="An 8 lights all seven segments and a 0 lights all but the middle one, so with the "
         "middle segment broken both show the same six. 6 and 5 differ in the bottom-left "
         "segment, which is nothing to do with the middle one.",
    fig=seven_segment("80", dead=("g",)),
    difficulty="hard", confidence=0.90),

# --- 30. Segments for a whole number.
B.Q("segment_display",
    "How many segments would light altogether to show the number in the diagram?",
    key=sum(len(SEGMENTS[d]) for d in "2026"), verify=5 + 6 + 5 + 6,
    wrong=[7 * 4, sum(len(SEGMENTS[d]) for d in "226"), 4],
    expl="The digits light 5, 6, 5 and 6 segments, which comes to 22. 28 counts all seven "
         "segments on each of the four digits whether they light or not, and 4 counts the "
         "digits rather than the segments.",
    fig=seven_segment("2026", w=26, gap=12, h=46, t=5),
    fmt=lambda v: f"{v} segments", difficulty="hard", confidence=0.91),

if __name__ == "__main__":
    B.write()
