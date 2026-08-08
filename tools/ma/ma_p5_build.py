#!/usr/bin/env python3
"""Builds ma_nsw_selective_p5.json — 36 Algebra and patterns questions (§4.1).

pattern rules 20, simple equations 14, substitution 2. After this batch Algebra stands at
72/91, with substitution 9 and unknowns 10 left.

The growing-tile items count `len(cells)` on the very list `tile_stages` draws, so a
pattern cannot show one number of tiles and be marked against another; the closed-form
rule is then the second route. The equations are all solved by inverse operations and
then checked by substituting the answer back into the original equation, which is the
only route that catches a sign slip.

Years 5-6 content, Year 6 sitting, no calculator.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.figure_lib import table, tile_stages  # noqa: E402
from tools.ma.ma_common import Batch, PLAIN, money, unit  # noqa: E402

B = Batch(nn=5)
CM = unit("cm")


# ---------------------------------------------------------------- pattern families
def Lshape(n):
    """Two arms of n tiles sharing a corner: 2n - 1 tiles."""
    return [(i, 0) for i in range(n)] + [(0, j) for j in range(1, n)]


def stair(n):
    """A staircase n wide: 1 + 2 + ... + n tiles."""
    return [(i, j) for i in range(n) for j in range(n - i)]


def square(n):
    return [(i, j) for i in range(n) for j in range(n)]


def cross(n):
    """A plus sign with arms n long: 4n + 1 tiles."""
    return [(n, n)] + [(n + k, n) for k in range(1, n + 1)] + \
           [(n - k, n) for k in range(1, n + 1)] + \
           [(n, n + k) for k in range(1, n + 1)] + [(n, n - k) for k in range(1, n + 1)]


def band(n):
    """Two rows of n tiles: 2n."""
    return [(i, j) for i in range(n) for j in range(2)]


def row(n):
    return [(i, 0) for i in range(n)]


# ===================================================== pattern rules (20)

# --- 1. L pattern, later stage.
B.Q("pattern_rules", "pattern_sequence",
    "The diagram shows the first three stages of a tile pattern. How many tiles are in "
    "stage 6?",
    key=len(Lshape(6)), verify=2 * 6 - 1,
    wrong=[(len(Lshape(5)), "off_by_one"), (2 * 6, "formula_slip"), (6 * 6, "operation_swap")],
    expl="Each stage adds 2 tiles to the one before, and stage 1 has 1, so stage 6 has "
         "2 x 6 - 1 = 11 tiles. 9 is stage 5, one short, and 12 doubles the stage number "
         "without taking off the tile the two arms share at the corner.",
    fig=tile_stages([Lshape(1), Lshape(2), Lshape(3)]), fmt=unit("tiles")),

# --- 2. The rule behind it.
B.Q("pattern_rules", "pattern_sequence",
    "Look again at the tile pattern in the diagram. Which rule gives the number of tiles "
    "in any stage?",
    key="double the stage number, then take away 1",
    verify="double the stage number, then take away 1",
    wrong=[("double the stage number", "partial_step"),
           ("add 2 to the stage number", "operation_swap"),
           ("multiply the stage number by itself", "misread_data")],
    difficulty="hard", confidence=0.91,
    expl="Stage 1 has 1 tile, stage 2 has 3 and stage 3 has 5, and 2 x 3 - 1 = 5 fits. "
         "Double the stage number gives 6 at stage 3, one too many, because the two arms "
         "share the corner tile.",
    fig=tile_stages([Lshape(1), Lshape(2), Lshape(3)]), fmt=PLAIN),

# --- 3. Staircase.
B.Q("pattern_rules", "pattern_sequence",
    "The diagram shows a staircase pattern growing stage by stage. How many tiles does "
    "stage 5 use?",
    key=len(stair(5)), verify=5 * 6 // 2,
    wrong=[(len(stair(4)), "off_by_one"), (5 * 5, "operation_swap"), (5 * 6, "formula_slip")],
    difficulty="hard", confidence=0.91,
    expl="Each stage adds a whole new column, so stage 5 is 1 + 2 + 3 + 4 + 5 = 15 tiles. "
         "10 is stage 4, and 25 squares the stage number when the pattern is a triangle "
         "rather than a square. 30 is 5 x 6, which counts every tile twice.",
    fig=tile_stages([stair(1), stair(2), stair(3)]), fmt=unit("tiles")),

# --- 4. Square numbers as a pattern.
B.Q("pattern_rules", "pattern_sequence",
    "The diagram shows squares of tiles growing one stage at a time. How many tiles are "
    "in stage 7?",
    key=len(square(7)), verify=sum(range(1, 14, 2)),
    wrong=[(len(square(6)), "off_by_one"), (7 * 2, "formula_slip"), (7 * 4, "wrong_attribute")],
    expl="Stage 7 is a 7 by 7 square, so it holds 49 tiles. Counting the extra tiles each "
         "stage adds — 3, 5, 7, 9 and so on — gives 49 too. 36 is stage 6, and 28 counts "
         "the tiles around the edge rather than all of them.",
    fig=tile_stages([square(1), square(2), square(3)]), fmt=unit("tiles")),

# --- 5. Cross pattern.
B.Q("pattern_rules", "pattern_sequence",
    "The diagram shows a cross pattern. How many tiles are in stage 4?",
    key=len(cross(4)), verify=4 * 4 + 1,
    wrong=[(4 * 4, "partial_step"), (len(cross(3)), "off_by_one"), (4 * 5, "operation_swap")],
    difficulty="hard", confidence=0.90,
    expl="Four arms of 4 tiles make 16, and the middle tile they all meet at makes 17. "
         "16 counts the arms but leaves out the centre, and 13 is stage 3.",
    fig=tile_stages([cross(1), cross(2), cross(3)]), fmt=unit("tiles")),

# --- 6. Which stage has a given count.
B.Q("pattern_rules", "multi_step",
    "In the tile pattern shown, each stage has two rows. Which stage is the first to use "
    "more than 20 tiles?",
    key=11, verify=next(n for n in range(1, 40) if len(band(n)) > 20),
    wrong=[(10, "off_by_one"), (20, "misread_data"), (12, "rounding")],
    difficulty="hard", confidence=0.90,
    expl="Stage n uses 2n tiles, so stage 10 uses exactly 20 — which is not more than 20 — "
         "and stage 11 uses 22. 10 stops at the stage that only equals 20, and 20 gives "
         "the number of tiles rather than the stage.",
    fig=tile_stages([band(1), band(2), band(3)]), fmt=PLAIN),

# --- 7. Perimeter of a row of squares.
B.Q("pattern_rules", "multi_step",
    "The diagram shows square tiles 1 cm on each side, joined in a row. What is the "
    "distance around the outside of a row of 8 tiles?",
    key=2 * 8 + 2, verify=8 + 8 + 1 + 1,        # two long sides and the two ends
    wrong=[(4 * 8, "formula_slip"), (8, "partial_step"), (2 * 8, "off_by_one")],
    difficulty="hard", confidence=0.91,
    expl="The row is 8 cm along the top and 8 cm along the bottom, with 1 cm at each end: "
         "18 cm. 32 counts all four sides of every tile as though they were separate, "
         "which double counts the edges where they join.",
    fig=tile_stages([row(1), row(2), row(3)]), fmt=CM),

# --- 8. Reverse: from tiles back to the stage.
B.Q("pattern_rules", "multi_step",
    "In the L-shaped tile pattern shown, one stage uses 19 tiles. Which stage is it?",
    key=(19 + 1) // 2, verify=next(n for n in range(1, 40) if len(Lshape(n)) == 19),
    wrong=[(19 // 2, "rounding"), (19 * 2 - 1, "inverse"), (19, "partial_step")],
    difficulty="hard", confidence=0.90,
    expl="The rule is 2 x stage - 1, so 19 tiles means 2 x stage = 20 and the stage is 10. "
         "9 rounds 19 / 2 down instead of adding the shared corner tile back first, and 37 "
         "runs the rule forwards from 19 rather than backwards to it.",
    fig=tile_stages([Lshape(1), Lshape(2), Lshape(3)]), fmt=PLAIN),

# --- 9. Tables and chairs.
B.Q("pattern_rules", "multi_step",
    "Square tables are pushed end to end in a line. One table seats 4 people, and every "
    "extra table adds 2 more seats. How many people can sit at 10 tables?",
    key=2 * 10 + 2, verify=4 + 2 * 9,           # the first table, then nine more
    wrong=[(4 * 10, "ignored_constraint"), (2 * 10, "partial_step"), (4 + 10, "operation_swap")],
    expl="The first table seats 4 and each of the other 9 adds 2, so 4 + 18 = 22 people. "
         "40 gives every table 4 seats and forgets that pushing them together hides the "
         "ends, and 20 leaves off the two seats at the ends of the line.",
    fmt=unit("people")),

# --- 10. The same pattern, run backwards.
B.Q("pattern_rules", "multi_step",
    "Using the same line of square tables, how many tables are needed to seat 26 people?",
    key=(26 - 2) // 2, verify=next(n for n in range(1, 40) if 2 * n + 2 == 26),
    wrong=[(26 // 2, "off_by_one"), (26 // 4, "operation_swap"), (26 - 2, "partial_step")],
    difficulty="hard", confidence=0.91,
    expl="Seats come to 2 x tables + 2, so 26 seats means 2 x tables = 24 and 12 tables. "
         "Check it: 12 tables seat 2 x 12 + 2 = 26. 13 divides 26 by 2 without first "
         "taking off the two end seats.",
    fmt=unit("tables")),

# --- 11. Posts and panels.
B.Q("pattern_rules", "multi_step",
    "A straight fence is built from panels with a post at each join and one at each end. "
    "A fence of 15 panels needs how many posts?",
    key=15 + 1, verify=len(range(0, 16)),
    wrong=[(15, "off_by_one"), (15 * 2, "operation_swap"), (15 - 1, "misread_data")],
    expl="Every panel needs a post on its left, and then one more closes off the right "
         "end: 15 + 1 = 16 posts. 15 counts one post per panel and leaves the far end "
         "without one.",
    fmt=unit("posts")),

# --- 12. Rule from a table of stages.
STG = table([["Stage", "1", "2", "3", "4"], ["Tiles", "7", "12", "17", "22"]])
B.Q("pattern_rules", "data_interpretation",
    "The table shows how many tiles each stage of a pattern uses. Which rule gives the "
    "number of tiles from the stage number?",
    key="multiply the stage by 5, then add 2", verify="multiply the stage by 5, then add 2",
    wrong=[("multiply the stage by 5", "partial_step"), ("add 5 to the stage", "operation_swap"),
           ("multiply the stage by 7", "misread_data")],
    difficulty="hard", confidence=0.91,
    expl="The tiles go up by 5 each stage, so the rule multiplies by 5 — and stage 1 gives "
         "5, two short of 7, so it adds 2. Check stage 4: 5 x 4 + 2 = 22. Multiply the "
         "stage by 7 fits stage 1 alone.",
    fig=STG, fmt=PLAIN),

# --- 13. Hexagons in a chain.
B.Q("pattern_rules", "multi_step",
    "Regular hexagons are joined in a chain, each sharing one whole side with the next. "
    "One hexagon has 6 sides showing. How many sides show on a chain of 9 hexagons?",
    key=4 * 9 + 2, verify=6 + 4 * 8,
    wrong=[(6 * 9, "ignored_constraint"), (4 * 9, "partial_step"), (6 * 9 - 9, "misread_data")],
    difficulty="hard", confidence=0.90,
    expl="The first hexagon shows 6 sides and every one after it adds 4, because it hides "
         "one side and covers one of its neighbour's: 6 + 8 x 4 = 38. 54 gives every "
         "hexagon all 6 sides as though none were joined, and 36 forgets the two extra "
         "sides on the hexagon at the start.",
    fmt=unit("sides")),

# --- 14. A taxi fare.
B.Q("pattern_rules", "multi_step",
    "A taxi charges a $4 flagfall plus $2 for each kilometre travelled. What is the fare "
    "for a 14 km trip?",
    key=4 + 2 * 14, verify=2 * 14 + 4,
    wrong=[(2 * 14, "partial_step"), ((4 + 2) * 14, "wrong_attribute"), (4 * 14, "operation_swap")],
    expl="The fare is $4 plus 14 lots of $2: $4 + $28 = $32. $28 leaves out the flagfall, "
         "and $84 charges the flagfall for every kilometre rather than once.",
    fmt=money),

# --- 15. Savings growing weekly.
B.Q("pattern_rules", "multi_step",
    "Mia has $12 saved and adds $5 every week. How much will she have saved after 8 more "
    "weeks?",
    key=12 + 5 * 8, verify=5 * 8 + 12,
    wrong=[(5 * 8, "partial_step"), (12 + 5, "off_by_one"), (12 * 5, "operation_swap")],
    expl="Eight weeks add 8 x $5 = $40 to the $12 she already has, giving $52. $40 counts "
         "only the new savings, and $60 multiplies the starting amount by 5 instead of "
         "adding the weekly amount.",
    fmt=money),

# --- 16. Matching a rule to a sequence.
B.Q("pattern_rules", "pattern_sequence",
    "A pattern produces the numbers 5, 9, 13, 17 for stages 1, 2, 3 and 4. Which rule "
    "produces those numbers?",
    key="4 times the stage, plus 1", verify="4 times the stage, plus 1",
    wrong=[("4 times the stage", "partial_step"), ("5 times the stage", "misread_data"),
           ("the stage plus 4", "operation_swap")],
    expl="Stage 1 gives 4 + 1 = 5 and stage 4 gives 16 + 1 = 17, so the rule is 4 times "
         "the stage plus 1. 4 times the stage lands 1 short every time, and 5 times the "
         "stage happens to fit stage 1 and nothing after it.",
    fmt=PLAIN),

# --- 17. Stacking cups.
B.Q("pattern_rules", "multi_step",
    "One plastic cup stands 12 cm tall. Each extra cup stacked inside it adds 2 cm to the "
    "height. How tall is a stack of 9 cups?",
    key=12 + 2 * 8, verify=2 * 9 + 10,          # ten centimetres of base plus 2 cm a cup
    wrong=[(12 + 2 * 9, "off_by_one"), (12 * 9, "operation_swap"), (2 * 9, "partial_step")],
    difficulty="hard", confidence=0.91,
    expl="The first cup is 12 cm and the other 8 add 2 cm each: 12 + 16 = 28 cm. 30 adds "
         "2 cm nine times, once for the first cup as well, when the first cup is already "
         "the 12 cm the stack starts at.",
    fmt=CM),

# --- 18. First stage past a threshold.
B.Q("pattern_rules", "multi_step",
    "A pattern uses 3 tiles at stage 1 and 4 more tiles at every stage after that. Which "
    "is the first stage to use more than 40 tiles?",
    key=next(n for n in range(1, 60) if 4 * n - 1 > 40), verify=11,
    wrong=[(10, "off_by_one"), (4 * 11 - 1, "misread_data"), (12, "rounding")],
    difficulty="hard", confidence=0.90,
    expl="Stage n uses 4n - 1 tiles: stage 10 uses 39, which is not more than 40, and "
         "stage 11 uses 43. 10 stops one stage short, 43 gives the number of tiles that "
         "stage uses rather than the stage number, and 12 goes one further than needed.",
    fmt=PLAIN),

# --- 19. Hire cost, run backwards.
B.Q("pattern_rules", "multi_step",
    "A hall costs $20 to book plus $6 for each hour it is used. A booking came to $62. "
    "For how many hours was the hall used?",
    key=(62 - 20) // 6, verify=next(h for h in range(1, 30) if 20 + 6 * h == 62),
    wrong=[(62 // 6, "rounding"), ((62 + 20) // 6, "inverse"), (62 - 20, "partial_step")],
    difficulty="hard", confidence=0.91,
    expl="Take off the booking fee first: $62 - $20 = $42, and $42 / $6 = 7 hours. Check "
         "it: $20 + 7 x $6 = $62. 10 divides the whole $62 by 6 and never takes the "
         "booking fee off.",
    fmt=unit("hours")),

# --- 20. Two patterns meeting.
B.Q("pattern_rules", "multi_step",
    "Pattern A uses 3 tiles at stage 1 and adds 3 tiles a stage. Pattern B uses 1 tile at "
    "stage 1 and adds 5 tiles a stage. At which stage do the two patterns use the same "
    "number of tiles?",
    key=next(n for n in range(1, 40) if 3 * n == 5 * n - 4), verify=2,
    wrong=[(1, "misread_data"), (4, "operation_swap"), (3, "off_by_one")],
    difficulty="hard", confidence=0.90,
    expl="Pattern A goes 3, 6, 9 and pattern B goes 1, 6, 11, so they meet at stage 2 with "
         "6 tiles each. At stage 1 they are 3 and 1, which do not match, and by stage 3 B "
         "has already overtaken A.",
    fmt=PLAIN),

# ===================================================== simple equations (14)


def EQ(stem, key, wrong, expl, check, fmt=PLAIN, **kw):
    """An equation item. `check` substitutes the answer back into the original equation
    and must return the value the equation states — solving and checking are different
    operations, which is what makes this a second route rather than a repeat."""
    B.Q("simple_equations", "single_step" if kw.pop("single", False) else "multi_step",
        stem, key=key, verify=key if check(key) else "SUBSTITUTION FAILED",
        wrong=wrong, expl=expl, fmt=fmt, **kw)


EQ("What number does x stand for if x + 17 = 45?",
   key=45 - 17, wrong=[(45 + 17, "inverse"), (45 - 7, "misread_data"), (17, "partial_step")],
   expl="Undo the adding: 45 - 17 = 28. Check it: 28 + 17 = 45. 62 adds the 17 again "
        "instead of taking it off, and 38 takes off 7 rather than 17.",
   check=lambda x: x + 17 == 45, single=True)

EQ("In the equation n - 23 = 19, what is the value of n?",
   key=19 + 23, wrong=[(32, "place_value"), (23 - 19, "inverse"), (19, "partial_step")],
   expl="Undo the subtracting by adding it back: 19 + 23 = 42. Check it: 42 - 23 = 19. "
        "4 takes 19 from 23, which is the subtraction done the wrong way round, and 32 "
        "loses the carry when adding 19 and 23.",
   check=lambda n: n - 23 == 19, single=True)

EQ("If 6k = 84, what does k equal?",
   key=84 // 6, wrong=[(84 * 6, "inverse"), (84 - 6, "operation_swap"), (84 // 6 + 1, "off_by_one")],
   expl="Undo the multiplying by dividing: 84 / 6 = 14. Check it: 6 x 14 = 84. 504 "
        "multiplies again rather than undoing, and 78 subtracts the 6.",
   check=lambda k: 6 * k == 84, single=True)

EQ("A number m divided by 5 gives 12. What is m?",
   key=12 * 5, wrong=[(12 - 5, "operation_swap"), (12 + 5, "misread_data"),
                      (12 * 5 + 5, "off_by_one")],
   expl="Undo the dividing by multiplying: 12 x 5 = 60. Check it: 60 / 5 = 12. 7 takes "
        "the 5 away and 17 adds it, when undoing a division calls for multiplying, and 65 "
        "multiplies correctly and then adds a stray 5.",
   check=lambda m: m / 5 == 12, single=True)

EQ("Solve 3x + 4 = 25.",
   key=(25 - 4) // 3, wrong=[(25 // 3, "rounding"), ((25 + 4) // 3, "inverse"),
                             (25 - 4, "partial_step")],
   expl="Take the 4 off first: 25 - 4 = 21, then divide by 3 to get 7. Check it: "
        "3 x 7 + 4 = 25. 21 stops after taking off the 4, and 9 divides before taking it "
        "off, which is the two steps in the wrong order.",
   check=lambda x: 3 * x + 4 == 25, difficulty="hard", confidence=0.91)

EQ("The equation 2y - 7 = 15 is true for exactly one value of y. Which value?",
   key=(15 + 7) // 2, wrong=[((15 - 7) // 2, "inverse"), (15 + 7, "partial_step"),
                             (15 // 2 + 7, "operation_swap")],
   expl="Add the 7 back first: 15 + 7 = 22, then halve it to get 11. Check it: "
        "2 x 11 - 7 = 15. 4 takes the 7 off when the equation has already taken it off, "
        "and 22 stops before the halving.",
   check=lambda y: 2 * y - 7 == 15, difficulty="hard", confidence=0.91)

EQ("Find p, given that 4p + 4 = 32.",
   key=(32 - 4) // 4, wrong=[(32 // 4, "ignored_constraint"), (32 - 4, "partial_step"),
                             ((32 + 4) // 4, "inverse")],
   expl="Take off the 4 first: 32 - 4 = 28, and 28 / 4 = 7. Check it: 4 x 7 + 4 = 32. "
        "8 divides 32 by 4 and ignores the +4 sitting in the equation.",
   check=lambda p: 4 * p + 4 == 32, difficulty="hard", confidence=0.90)

EQ("A box stands for a missing number: 7 + box = 22. What number belongs in the box?",
   key=22 - 7, wrong=[(22 + 7, "inverse"), (22, "partial_step"), (7, "misread_data")],
   expl="Undo the adding: 22 - 7 = 15. Check it: 7 + 15 = 22. 29 adds the 7 a second "
        "time rather than taking it away.",
   check=lambda b: 7 + b == 22, single=True)

EQ("Three identical bags of sand and a 4 kg weight balance against 19 kg. How heavy is "
   "one bag?",
   key=(19 - 4) // 3, wrong=[(19 // 3, "rounding"), (19 - 4, "partial_step"),
                             ((19 + 4) // 3, "inverse")],
   expl="The three bags together weigh 19 - 4 = 15 kg, so one bag is 15 / 3 = 5 kg. Check "
        "it: 3 x 5 + 4 = 19. 15 is what all three weigh, not one, and 6 divides before "
        "taking the 4 kg weight off.",
   check=lambda b: 3 * b + 4 == 19, fmt=unit("kg"), difficulty="hard", confidence=0.91)

EQ("A number is doubled and then 5 is added, giving 23. What was the number?",
   key=(23 - 5) // 2, wrong=[(23 // 2, "rounding"), (23 - 5, "partial_step"),
                             ((23 + 5) // 2, "inverse")],
   expl="Undo the steps backwards: 23 - 5 = 18, then halve it to get 9. Check it: "
        "2 x 9 + 5 = 23. 18 stops after undoing the adding, and 14 adds the 5 instead of "
        "taking it off.",
   check=lambda n: 2 * n + 5 == 23, difficulty="hard", confidence=0.90)

EQ("Work out w in 24 - w = 9.",
   key=24 - 9, wrong=[(24 + 9, "inverse"), (16, "off_by_one"), (9, "partial_step")],
   expl="The number taken away must be 24 - 9 = 15. Check it: 24 - 15 = 9. 33 adds the 9 "
        "to 24 when the equation takes something away from 24, and 16 is one out — check "
        "it and 24 - 16 gives 8, not 9.",
   check=lambda w: 24 - w == 9, single=True)

EQ("If t + t + 3 = 17, which number is t?",
   key=(17 - 3) // 2, wrong=[(17 - 3, "partial_step"), (17 // 2, "rounding"),
                             ((17 + 3) // 2, "inverse")],
   expl="Two lots of t and a 3 make 17, so two lots of t make 17 - 3 = 14 and t is 7. "
        "Check it: 7 + 7 + 3 = 17. 14 is what the two lots come to together, not one of "
        "them.",
   check=lambda t: t + t + 3 == 17, difficulty="hard", confidence=0.91)

EQ("For which value of x is 2x the same as x + 6?",
   key=6, wrong=[(3, "operation_swap"), (12, "misread_data"), (0, "ignored_constraint")],
   expl="Two lots of x are one lot of x plus another, so that extra lot must be the 6, "
        "making x = 6. Check it: 2 x 6 = 12 and 6 + 6 = 12. 3 halves the 6, 12 gives what "
        "both sides come to rather than what x is, and 0 works only if the 6 is left out "
        "of the right-hand side altogether.",
   check=lambda x: 2 * x == x + 6, difficulty="hard", confidence=0.90)

EQ("Which equation says 'a number has 8 taken away from it and the answer is 15'?",
   key="n - 8 = 15", wrong=[("8 - n = 15", "inverse"), ("n + 8 = 15", "operation_swap"),
                            ("n - 15 = 8", "misread_data")],
   expl="The number comes first and the 8 is taken from it, so the equation is n - 8 = 15. "
        "8 - n = 15 takes the number away from 8, which is the subtraction the other way "
        "round, and n + 8 = 15 adds instead of taking away.",
   check=lambda s: s == "n - 8 = 15", single=True)

# ===================================================== substitution (2)

B.Q("substitution", "single_step",
    "If a = 7, what is the value of 4a - 3?",
    key=4 * 7 - 3, verify=7 + 7 + 7 + 7 - 3,     # four lots of a, added rather than multiplied
    wrong=[(4 * (7 - 3), "wrong_attribute"), (4 + 7 - 3, "operation_swap"),
           (4 * 7, "partial_step")],
    expl="4a means 4 lots of a, so 4 x 7 = 28, and 28 - 3 = 25. 16 takes the 3 off before "
         "multiplying, which is the two steps in the wrong order, and 28 stops before the "
         "subtraction.",
    fmt=PLAIN),

B.Q("substitution", "multi_step",
    "If p = 6 and q = 4, what is the value of 2p + 3q?",
    key=2 * 6 + 3 * 4, verify=(6 + 6) + (4 + 4 + 4),
    wrong=[(2 + 6 + 3 + 4, "operation_swap"), (2 * 6, "partial_step"),
           ((2 + 3) * (6 + 4), "wrong_attribute")],
    difficulty="hard", confidence=0.91,
    expl="2p is 2 x 6 = 12 and 3q is 3 x 4 = 12, so the total is 24. 15 adds all four "
         "numbers instead of multiplying the pairs, and 50 adds the multipliers together "
         "and the letters together before multiplying.",
    fmt=PLAIN),

if __name__ == "__main__":
    B.write()
