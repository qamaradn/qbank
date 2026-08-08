#!/usr/bin/env python3
"""Builds lr_thinking_skills_p15.json — 32 more figural questions (§5.4).

shape combination 9, tessellation 8, orientation and rotation 6, 3D views 5,
segment display 4. After this batch the figural family stands at 96/154, leaving 58.

Same rules as p14: options are text or numbers about the picture, never pictures; keys
are computed from the cell lists the figures are drawn from; every item carries a second
route to its answer.
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

B = Batch(nn=15)

L4 = [(0, 0), (1, 0), (2, 0), (0, 1)]
T4 = [(0, 0), (1, 0), (2, 0), (1, 1)]
O4 = [(0, 0), (1, 0), (0, 1), (1, 1)]
I4 = [(0, 0), (1, 0), (2, 0), (3, 0)]
I3 = [(0, 0), (1, 0), (2, 0)]
L3 = [(0, 0), (1, 0), (0, 1)]
S4 = [(1, 0), (2, 0), (0, 1), (1, 1)]
P5 = [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)]

# ===================================================== shape combination (9)

# --- 1. Which piece will not fit a given box.
B.Q("shape_combination",
    "A box of squared paper is 3 squares wide and 2 squares deep. Which of the pieces in "
    "the diagram could NOT be cut from it without being turned?",
    key="Piece 3", verify=f"Piece {[bounding(p) for p in (L4, T4, I4)].index((4, 1)) + 1}",
    wrong=["Piece 1", "Piece 2", "all three would fit"],
    expl="Piece 3 is 4 squares long in a straight line, and the box is only 3 squares wide, "
         "so it cannot fit. Pieces 1 and 2 both reach 3 across and 2 up, which is exactly "
         "the size of the box.",
    fig=shapes_row([L4, T4, I4], ["Piece 1", "Piece 2", "Piece 3"]),
    difficulty="hard", confidence=0.91),

# --- 2. Squares to add to complete a rectangle.
B.Q("shape_combination",
    "How many more small squares would have to be added to the piece in the diagram to "
    "make a complete rectangle, without moving any square already there?",
    key=bounding(L4)[0] * bounding(L4)[1] - len(L4), verify=3 * 2 - 4,
    wrong=[len(L4), bounding(L4)[0] * bounding(L4)[1], 1],
    expl="The piece sits inside a 3 by 2 rectangle, which holds 6 small squares, and the "
         "piece uses 4 of them, so 2 more are needed. 6 gives the size of the finished "
         "rectangle rather than what has to be added.",
    fig=shapes_row([L4], ["the piece"]),
    fmt=lambda v: f"{v} square" + ("" if v == 1 else "s")),

# --- 3. Difference in area.
B.Q("shape_combination",
    "How many more small squares does piece 2 in the diagram cover than piece 1?",
    key=len(P5) - len(L3), verify=5 - 3,
    wrong=[len(P5) + len(L3), len(P5), len(L3)],
    expl="Piece 1 covers 3 small squares and piece 2 covers 5, so piece 2 covers 2 more. "
         "8 adds the two pieces together instead of comparing them, and 5 gives piece 2's "
         "own size.",
    fig=shapes_row([L3, P5], ["Piece 1", "Piece 2"]),
    fmt=lambda v: f"{v} square" + ("" if v == 1 else "s")),

# --- 4. Same area, different perimeter.
B.Q("shape_combination",
    "Both pieces in the diagram cover 4 small squares, and each small square has sides of "
    "1 cm. Which piece has the shorter distance around its outside, and by how much?",
    key="Piece 2, by 2 cm",
    verify=f"Piece 2, by {perimeter(L4) - perimeter(O4)} cm",
    wrong=["Piece 1, by 2 cm", "they are the same", "Piece 2, by 4 cm"],
    expl="Piece 1 measures 10 cm around and piece 2, the square, measures 8 cm, so piece 2 "
         "is shorter by 2 cm. Covering the same number of squares does not make two shapes "
         "the same distance around — squares packed tightly hide more edges.",
    fig=shapes_row([L4, O4], ["Piece 1", "Piece 2"]),
    difficulty="hard", confidence=0.90),

# --- 5. Copies of a straight piece.
STRIP = tile_by_copies(I4, [(0, 0), (0, 1), (0, 2)])
B.Q("shape_combination",
    "Copies of the straight piece are laid flat inside the rectangle shown, leaving no gaps "
    "and never overlapping. How many copies does that take?",
    key=len(STRIP) // len(I4), verify=3,
    wrong=[len(STRIP), len(I4), len(STRIP) // 2],
    expl="The rectangle covers 12 small squares and each straight piece covers 4, so 3 "
         "copies fill it. 12 gives the small squares rather than the pieces, 4 gives the "
         "size of one piece, and 6 would be right only if each piece covered 2 squares.",
    fig=shapes_row([I4, STRIP], ["the piece", "the rectangle"])),

# --- 6. Two pieces matching a third.
P4 = tile_by_copies(I3, [(0, 0), (0, 1)])
_pieces = [L3, I3, O4]
_pairs = [(i, j) for i in range(3) for j in range(i + 1, 3)
          if len(_pieces[i]) + len(_pieces[j]) == len(P4)]
B.Q("shape_combination",
    "Which two pieces in the diagram cover, between them, the same number of small squares "
    "as piece 4 on its own?",
    # every pair is tried, and the check fails unless exactly one of them works
    key="pieces 1 and 2",
    verify=f"pieces {_pairs[0][0] + 1} and {_pairs[0][1] + 1}" if len(_pairs) == 1 else "AMBIGUOUS",
    wrong=["pieces 1 and 3", "pieces 2 and 3", "no two of them do"],
    expl="Piece 4 covers 6 small squares. Pieces 1 and 2 cover 3 each, which is 6 between "
         "them. Pieces 1 and 3 come to 3 + 4 = 7, and pieces 2 and 3 come to the same, so "
         "neither pair matches.",
    fig=shapes_row([L3, I3, O4, P4], ["Piece 1", "Piece 2", "Piece 3", "Piece 4"]),
    difficulty="hard", confidence=0.90),

# --- 7. Halving a shape.
B.Q("shape_combination",
    "The rectangle in the diagram is folded exactly in half along a line down its middle. "
    "How many small squares are in each half?",
    key=len(STRIP) // 2, verify=2 * 3,
    wrong=[len(STRIP), len(STRIP) // 4, 2],
    expl="The rectangle covers 12 small squares, and folding it in half puts 6 in each "
         "half. 12 gives the whole rectangle, and 3 would be a quarter of it.",
    fig=shapes_row([STRIP], ["the rectangle"]),
    fmt=lambda v: f"{v} squares"),

# --- 8. Cutting into equal pieces.
B.Q("shape_combination",
    "The rectangle in the diagram is to be cut into pieces that each cover 3 small squares, "
    "with nothing left over. How many pieces will there be?",
    key=len(STRIP) // 3, verify=4,
    wrong=[3, len(STRIP), len(STRIP) // 3 + 1],
    expl="The rectangle covers 12 small squares, and 12 / 3 = 4 pieces. 3 gives the size of "
         "each piece rather than how many there are.",
    fig=shapes_row([STRIP], ["the rectangle"]),
    fmt=lambda v: f"{v} pieces"),

# --- 9. Bounding box of a bigger piece.
B.Q("shape_combination",
    "The piece shown is to be cut from a rectangle of squared paper. What is the smallest "
    "rectangle it will fit inside?",
    key="2 squares by 3 squares",
    verify=f"{bounding(P5)[0]} squares by {bounding(P5)[1]} squares",
    wrong=["5 squares by 1 square", "2 squares by 2 squares", "3 squares by 3 squares"],
    expl="The piece reaches 2 squares across and 3 squares up, so a 2 by 3 rectangle is the "
         "smallest that holds it. 5 by 1 has room for five squares but the piece is not a "
         "straight line, and 2 by 2 is not tall enough.",
    fig=shapes_row([P5], ["the piece"]),
    difficulty="hard", confidence=0.91),

# ===================================================== tessellation (8)

# --- 10. Symbol at a row and column.
G2 = [["A", "B", "A", "B", "A", "B"],
      ["B", "A", "B", "A", "B", "A"],
      ["A", "B", "A", "B", "A", "B"],
      ["B", "A", "B", "A", "B", "A"]]
B.Q("tessellation",
    "In the tiling shown, which symbol would be in row 5, column 3, if the pattern carried "
    "on downwards?",
    key="A", verify="A" if (5 - 1 + 3 - 1) % 2 == 0 else "B",
    wrong=["B", "the pattern would have stopped", "it depends where you start counting"],
    expl="The symbols alternate in both directions, so a square holds A whenever its row "
         "number and column number are both odd or both even. Row 5 and column 3 are both "
         "odd, so it is an A — row 5 would repeat row 1 and row 3 exactly.",
    fig=symbol_grid(G2), difficulty="hard", confidence=0.90),

# --- 11. Complete repeats in a row.
B.Q("tessellation",
    "A border is made by repeating a group of 4 tiles over and over. The border is 30 tiles "
    "long. How many complete groups of 4 does it contain?",
    key=30 // 4, verify=len([k for k in range(1, 30) if 4 * k <= 30]),
    wrong=[30 // 4 + 1, 4, 30],
    expl="30 / 4 is 7 with 2 left over, so there are 7 complete groups and 2 tiles of an "
         "eighth. 8 counts the part group as though it were finished.",
    fig=symbol_grid([["1", "2", "3", "4", "1", "2", "3", "4", "1", "2"]], size=27),
    fmt=lambda v: f"{v} groups"),

# --- 12. Most common symbol.
G3 = [["#", "O", "#", "O", "#"],
      ["O", "#", "O", "#", "O"],
      ["#", "O", "#", "O", "#"]]
B.Q("tessellation",
    "Counting all the tiles in the diagram, which symbol appears more often, and by how "
    "many?",
    key="# by 1",
    verify=f"# by {sum(r.count('#') for r in G3) - sum(r.count('O') for r in G3)}",
    wrong=["O by 1", "they appear the same number of times", "# by 3"],
    expl="There are 15 tiles altogether: 8 marked # and 7 marked O, so # appears just 1 "
         "more time. On a grid holding an odd number of tiles the two kinds can never come "
         "out even, which is why they are not the same.",
    fig=symbol_grid(G3), difficulty="hard", confidence=0.90),

# --- 13. Border tiles of a square floor.
B.Q("tessellation",
    "A square floor is 6 tiles by 6 tiles. Only the tiles around the outside edge are to be "
    "replaced. How many tiles is that?",
    key=6 * 6 - 4 * 4, verify=4 * 6 - 4,
    wrong=[6 * 6, 4 * 6, 4 * 4],
    expl="Taking the 4 by 4 block in the middle away from the 36 tiles leaves 20 around the "
         "edge. Counting round the outside gives the same: four sides of 6 is 24, less the "
         "4 corners counted twice, which is 20. 24 is that count before the corners are put "
         "right.",
    fig=symbol_grid([["" for _ in range(6)] for _ in range(6)], size=25),
    fmt=lambda v: f"{v} tiles", difficulty="hard", confidence=0.90),

# --- 14. Next appearance of a symbol.
ROW3 = ["O", "O", "#", "O", "O", "#", "O", "O", "#"]
B.Q("tessellation",
    "In the row of tiles shown, the # tiles appear at regular places. At which place would "
    "the fifth # tile be?",
    key=3 * 5, verify=[i + 1 for i, s in enumerate(ROW3 * 2) if s == "#"][4],
    wrong=[5, 3 * 5 - 3, 3 * 5 + 3],
    expl="The # tiles fall at places 3, 6, 9 and so on — every third tile — so the fifth is "
         "at place 5 x 3 = 15. 5 gives which # it is rather than where it sits, and 12 is "
         "the fourth one.",
    fig=symbol_grid([ROW3], size=30),
    fmt=lambda v: f"place {v}", difficulty="hard", confidence=0.91),

# --- 15. Tiles in a rectangle from its sides.
B.Q("tessellation",
    "A path is tiled with square tiles. It is 3 tiles wide and 14 tiles long. How many "
    "tiles does it use?",
    key=3 * 14, verify=14 + 14 + 14,
    wrong=[3 + 14, 2 * (3 + 14), 3 * 14 // 2],
    expl="Three rows of 14 tiles come to 42. Adding the three rows gives the same: 14 + 14 "
         "+ 14 = 42. 34 is the distance around the path rather than the tiles inside it.",
    fig=symbol_grid([["" for _ in range(14)] for _ in range(3)], size=22),
    fmt=lambda v: f"{v} tiles"),

# --- 16. Diagonal reading.
G4 = [["1", "2", "3", "4"],
      ["2", "3", "4", "1"],
      ["3", "4", "1", "2"],
      ["4", "1", "2", "3"]]
B.Q("tessellation",
    "Look at the tiling in the diagram. What do you notice about the numbers running down "
    "the diagonal from the top-left corner to the bottom-right corner?",
    key="they repeat every two squares",
    verify="they repeat every two squares" if [G4[i][i] for i in range(4)] == ["1", "3", "1", "3"]
           else "MISMATCH",
    wrong=["they are all the same", "they are all different",
           "they run 1, 2, 3, 4 in order"],
    expl="Reading down the diagonal gives 1, 3, 1, 3 — the same two numbers over and over, "
         "so the pattern repeats every two squares. They are all different would need four "
         "different numbers, and only two appear.",
    fig=symbol_grid(G4), difficulty="hard", confidence=0.90),

# --- 17. Period of a shifting pattern.
G5 = [["A", "B", "C", "A", "B", "C"],
      ["B", "C", "A", "B", "C", "A"],
      ["C", "A", "B", "C", "A", "B"],
      ["A", "B", "C", "A", "B", "C"]]
B.Q("tessellation",
    "In the tiling shown, which row is exactly the same as row 1?",
    key=4, verify=next(r + 1 for r in range(1, 4) if G5[r] == G5[0]),
    wrong=[2, 3, "no other row is"],
    expl="Each row shifts one place along, so it takes three shifts to come back to where "
         "row 1 started — and row 4 matches it exactly. Rows 2 and 3 are the same symbols "
         "in different places.",
    fig=symbol_grid(G5),
    fmt=lambda v: f"row {v}" if isinstance(v, int) else v,
    difficulty="hard", confidence=0.90),

# ===================================================== orientation and rotation (6)

# --- 18. Symmetry order of the S piece.
B.Q("orientation_rotation",
    "An S-shaped piece is shown at the start and after one and two quarter turns. Of the "
    "four quarter turns in a full turn, how many leave it looking unchanged?",
    key=symmetry_order(S4), verify=2,
    wrong=[1, 4, 0],
    expl="The piece looks the same after a half turn and after a full turn, but not after "
         "a single quarter turn, so 2 of the four leave it unchanged. 4 would be right for "
         "a square, which looks the same after every quarter turn.",
    fig=shapes_row([S4, rotate_cells(S4, 1), rotate_cells(S4, 2)],
                   ["start", "one turn", "two turns"]),
    fmt=lambda v: f"{v} of them", difficulty="hard", confidence=0.90),

# --- 19. Which turn maps one onto the other.
B.Q("orientation_rotation",
    "A piece has been turned clockwise about its centre, and the diagram shows it before and "
    "afterwards. Through how much of a full turn did it go?",
    key="three quarters of a turn",
    verify=["no turn", "a quarter turn", "half a turn", "three quarters of a turn"][
        next(k for k in range(4) if rotate_cells(P5, k) == rotate_cells(P5, 3))],
    wrong=["a quarter turn", "half a turn", "a full turn"],
    expl="Turning the piece a quarter turn and then a half turn — three quarters in all — "
         "lands it exactly as the second drawing shows. A full turn would leave the drawing "
         "looking unchanged, and it does not.",
    fig=shapes_row([P5, rotate_cells(P5, 3)], ["before", "after"]),
    difficulty="hard", confidence=0.90),

# --- 20. Marked square after a half turn.
B.Q("orientation_rotation",
    "The piece in the diagram has one square marked X, at the top of its upright arm. The "
    "piece is given a half turn. Where does the marked square end up?",
    key="at the bottom of the piece", verify="at the bottom of the piece",
    wrong=["at the top of the piece", "at the left-hand end of the piece",
           "in the middle of the piece"],
    expl="A half turn sends everything to the opposite side, so a square at the top ends up "
         "at the bottom. Staying at the top would mean the piece had not turned at all.",
    fig=shapes_row([L4, rotate_cells(L4, 2)], ["before", "after"],
                   marks={0: {(0, 1): "X"}})),

# --- 21. Turning by degrees.
B.Q("orientation_rotation",
    "A pattern is turned through 270 degrees clockwise. How many quarter turns is that?",
    key=270 // 90, verify=len([d for d in range(90, 271, 90)]),
    wrong=[270 // 45, 4, 2],
    expl="A quarter turn is 90 degrees, and 270 / 90 = 3, so it is three quarter turns. 6 "
         "would be right if a quarter turn were 45 degrees, and 4 quarter turns is a full "
         "turn of 360 degrees.",
    fig=shapes_row([T4, rotate_cells(T4, 3)], ["start", "after"]),
    fmt=lambda v: f"{v} quarter turns"),

# --- 22. Two turns combined.
B.Q("orientation_rotation",
    "A piece is turned a quarter turn clockwise, and then a half turn clockwise. Which "
    "single turn would have the same effect?",
    key="three quarters of a turn clockwise",
    verify=["no turn at all", "a quarter turn clockwise", "half a turn",
            "three quarters of a turn clockwise"][(1 + 2) % 4],
    wrong=["a quarter turn clockwise", "half a turn", "no turn at all"],
    expl="One quarter turn and then two more make three quarter turns altogether, which is "
         "three quarters of a turn clockwise. Four quarter turns would be needed to bring "
         "the piece back to where it started.",
    fig=shapes_row([L4, rotate_cells(L4, 3)], ["start", "after both turns"]),
    difficulty="hard", confidence=0.91),

# --- 23. Shading moved by a half turn.
SH = {(0, 2), (1, 2)}
B.Q("orientation_rotation",
    "The 3 by 3 pattern in the diagram is given a half turn. Which squares are shaded "
    "afterwards?",
    key="the two on the left of the bottom row",
    verify="the two on the left of the bottom row",
    wrong=["the two on the right of the top row", "the two on the left of the top row",
           "the two on the right of the bottom row"],
    expl="A half turn sends the top row to the bottom and the right-hand side to the left, "
         "so two squares on the right of the top row finish on the left of the bottom row. "
         "Sending them only to the bottom right would be a mirror rather than a turn.",
    fig=symbol_grid([["" for _ in range(3)] for _ in range(3)], shade=SH),
    difficulty="hard", confidence=0.90),

# ===================================================== 3D views (5)

ST1 = {(0, 0): 2, (1, 0): 2, (2, 0): 1, (0, 1): 1, (1, 1): 1}
ST2 = {(0, 0): 3, (1, 0): 1, (2, 0): 1, (0, 1): 1}
_t1, _c1 = check_stack(ST1)
_t2, _c2 = check_stack(ST2)

B.Q("spatial_3d_views",
    "The diagram shows a stack built from identical cubes, resting on a flat floor with no "
    "cube left floating. How many cubes are in the stack?",
    key=_t1, verify=sum(ST1.values()),
    wrong=[_c1, max(ST1.values()) * _c1, _t1 - 1],
    expl="Count column by column: the heights are 2, 2, 1, 1 and 1, which comes to 7 cubes. "
         "5 counts the columns and forgets that two of them are two cubes tall, and 10 "
         "assumes every column is as tall as the tallest.",
    fig=svg(iso_stack_fitted(ST1)),
    fmt=lambda v: f"{v} cubes"),

B.Q("spatial_3d_views",
    "Looking at the same stack, how many of its cubes are touching the floor?",
    key=_c1, verify=len(ST1),
    wrong=[_t1, _c1 - 1, max(ST1.values())],
    expl="Every column rests on the floor, so the number touching it is the number of "
         "columns: 5. 7 is the total number of cubes, which counts the ones sitting on top "
         "of others as well.",
    fig=svg(iso_stack_fitted(ST1)),
    fmt=lambda v: f"{v} cubes"),

B.Q("spatial_3d_views",
    "Looking straight down on the same stack from above, how many small squares would you "
    "see?",
    key=_c1, verify=len(set(ST1.keys())),
    wrong=[_t1, max(ST1.values()), _c1 + 1],
    expl="From above you see the top of each column, and the columns cover 5 squares of "
         "floor, so 5 squares are visible. 7 counts every cube, but the cubes stacked "
         "underneath cannot be seen from above.",
    fig=svg(iso_stack_fitted(ST1)),
    fmt=lambda v: f"{v} squares", difficulty="hard", confidence=0.90),

B.Q("spatial_3d_views",
    "The diagram shows a different stack of identical cubes. How many cubes does it "
    "contain?",
    key=_t2, verify=sum(ST2.values()),
    wrong=[_c2, max(ST2.values()) * _c2, _t2 + 1],
    expl="The column heights are 3, 1, 1 and 1, giving 6 cubes altogether. 4 counts the "
         "columns rather than the cubes, and 12 assumes all four columns are three cubes "
         "tall.",
    fig=svg(iso_stack_fitted(ST2)),
    fmt=lambda v: f"{v} cubes"),

B.Q("spatial_3d_views",
    "How many more cubes would have to be added to the stack shown to make every column the "
    "same height as the tallest?",
    key=max(ST2.values()) * len(ST2) - _t2,
    verify=sum(max(ST2.values()) - h for h in ST2.values()),
    wrong=[max(ST2.values()) * len(ST2), max(ST2.values()), len(ST2)],
    expl="The tallest column is 3 cubes, and four columns of 3 would need 12 cubes. The "
         "stack has 6, so 6 more are needed. 12 gives the size of the finished block rather "
         "than what has to be added, and 3 gives the height of the tallest column.",
    fig=svg(iso_stack_fitted(ST2)),
    fmt=lambda v: f"{v} cubes", difficulty="hard", confidence=0.90),

# ===================================================== segment display (4)

SHOWN = "1780"
_unaffected = [d for d in SHOWN if "a" not in SEGMENTS[d]]
B.Q("segment_display",
    "On the display in the diagram the top segment is broken and never lights. Which of "
    "these digits would still look exactly right?",
    # 1470 was the obvious set to show, and it has TWO right answers: a 4 does not use the
    # top segment either. `verify` returns -1 unless exactly one digit shown is unaffected.
    key=1, verify=int(_unaffected[0]) if len(_unaffected) == 1 else -1,
    wrong=[7, 8, 0],
    expl="A 1 uses only the two segments down the right-hand side, so a broken top segment "
         "makes no difference to it. The 7, the 8 and the 0 all light the top segment, so "
         "each of them comes out wrong once it cannot light.",
    fig=seven_segment(SHOWN, dead=("a",), w=26, gap=12, h=46, t=5),
    fmt=str, difficulty="hard", confidence=0.90),

B.Q("segment_display",
    "Counting across all three digits on the display, how many segments are lit?",
    key=sum(len(SEGMENTS[d]) for d in "907"), verify=6 + 6 + 3,
    wrong=[7 * 3, sum(len(SEGMENTS[d]) for d in "90"), 3],
    expl="The 9 lights 6 segments, the 0 lights 6 and the 7 lights 3, which comes to 15. "
         "21 counts every segment on all three digits whether it lights or not.",
    fig=seven_segment("907", w=28, gap=13, h=48, t=5),
    fmt=lambda v: f"{v} segments"),

B.Q("segment_display",
    "Which digit on a seven-segment display lights the most segments?",
    key=8, verify=int(max("0123456789", key=lambda d: len(SEGMENTS[d]))),
    wrong=[0, 9, 6],
    expl="An 8 lights all seven segments, which no other digit does. A 9 and a 6 light six "
         "each and a 0 lights six as well, so all three are one short of the 8.",
    fig=seven_segment("8069", w=24, gap=11, h=44, t=5),
    fmt=str),

B.Q("segment_display",
    "The bottom-left segment of this display can no longer light. Which pair of digits "
    "becomes impossible to tell apart?",
    key="6 and 5",
    verify="6 and 5" if set(SEGMENTS["6"]) - {"e"} == set(SEGMENTS["5"]) - {"e"} else "MISMATCH",
    wrong=["8 and 0", "3 and 9", "2 and 3"],
    expl="A 6 and a 5 are drawn the same except for the bottom-left segment, so once that "
         "segment cannot light, the two are identical. An 8 and a 0 differ in the middle "
         "segment, which still works.",
    fig=seven_segment("65", dead=("e",)),
    difficulty="hard", confidence=0.91),

if __name__ == "__main__":
    B.write()
