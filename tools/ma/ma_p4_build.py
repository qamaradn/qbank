#!/usr/bin/env python3
"""Builds ma_nsw_selective_p4.json — 36 Algebra and patterns questions (§4.1).

number sequences 20 and function machines 16, which closes both subcategories. Pattern
rules, simple equations, substitution and unknowns follow in p5-p6.

Two routes to every answer, as everywhere in this build, but the pairing here is
particularly cheap and particularly worth having:

  * a sequence term is stepped out one term at a time AND reached by its closed form
    (a + (n-1)d, or a x r^(n-1)) — the two disagree the moment an off-by-one creeps into
    which term is being asked for, which is the single most common way a sequence
    question goes wrong.
  * a function machine's answer is fed back through the inverse machine, and must return
    the input the stem gave. A rule that does not invert cleanly is a rule I got wrong.

Years 5-6 content, Year 6 sitting, no calculator.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.figure_lib import table  # noqa: E402
from tools.ma.ma_common import Batch, PLAIN, unit  # noqa: E402

B = Batch(nn=4)


# ---------------------------------------------------------------- sequence helpers
def step(a, d, n):
    """The nth term (1-indexed) reached one step at a time."""
    x = a
    for _ in range(n - 1):
        x += d
    return x


def closed(a, d, n):
    """The same term from the closed form — the independent route."""
    return a + (n - 1) * d


def gstep(a, r, n):
    x = a
    for _ in range(n - 1):
        x *= r
    return x


def gclosed(a, r, n):
    return a * r ** (n - 1)


def seq(a, d, count, g=False):
    return [gstep(a, d, i + 1) if g else step(a, d, i + 1) for i in range(count)]


def shown(vals):
    return ", ".join(PLAIN(v) for v in vals)


# ===================================================== number sequences (20)

# --- 1. Arithmetic, adding.
a, d = 5, 7
B.Q("number_sequences", "pattern_sequence",
    f"A hall is set out so that each row has 7 more seats than the row in front. The rows "
    f"so far hold {shown(seq(a, d, 4))} seats. How many seats are in the next row?",
    key=step(a, d, 5), verify=closed(a, d, 5),
    wrong=[(step(a, d, 4) + d - 1, "off_by_one"), (step(a, d, 4), "partial_step"),
           (step(a, d, 4) * 2, "operation_swap")],
    expl="Each row adds 7, so after 26 comes 26 + 7 = 33 seats. 26 gives back the row "
         "already listed rather than the next one, and 52 doubles it instead of adding "
         "the 7 the pattern uses.",
    fmt=unit("seats")),

# --- 2. Arithmetic, subtracting.
a, d = 84, -6
B.Q("number_sequences", "pattern_sequence",
    f"A tank is emptying steadily. Its depth is measured each hour and the readings so far "
    f"are {shown(seq(a, d, 4))} centimetres. What will the next reading be?",
    key=step(a, d, 5), verify=closed(a, d, 5),
    wrong=[(step(a, d, 4) + 6, "inverse"), (step(a, d, 4), "partial_step"),
           (step(a, d, 5) - 6, "off_by_one")],
    expl="The depth drops 6 cm each hour, so after 66 comes 66 - 6 = 60 cm. 72 adds the 6 "
         "instead of taking it off, which would have the tank filling, and 54 takes off "
         "one 6 too many.",
    fmt=unit("cm")),

# --- 3. Doubling.
a, r = 3, 2
B.Q("number_sequences", "pattern_sequence",
    f"A rumour spreads so that the number of people who have heard it doubles each day: "
    f"{shown(seq(a, r, 4, g=True))}. How many will have heard it on the next day?",
    key=gstep(a, r, 5), verify=gclosed(a, r, 5),
    wrong=[(gstep(a, r, 4) + r, "operation_swap"), (gstep(a, r, 4), "partial_step"),
           (gstep(a, r, 6), "off_by_one")],
    expl="Doubling 24 gives 24 x 2 = 48 people. 26 adds 2 rather than doubling, which is "
         "the difference between a pattern that grows steadily and one that grows faster "
         "and faster, and 96 doubles one day too many.",
    fmt=unit("people")),

# --- 4. Tripling.
a, r = 2, 3
B.Q("number_sequences", "pattern_sequence",
    f"A pattern of counters grows by tripling: {shown(seq(a, r, 4, g=True))}. How many "
    f"counters are in the next stage?",
    key=gstep(a, r, 5), verify=gclosed(a, r, 5),
    wrong=[(gstep(a, r, 4) + 3, "operation_swap"), (gstep(a, r, 4) * 2, "misread_data"),
           (gstep(a, r, 4), "partial_step")],
    expl="Each stage is three times the one before, so after 54 comes 54 x 3 = 162 "
         "counters. 108 doubles instead of tripling, and 57 adds 3 rather than "
         "multiplying by it.",
    fmt=unit("counters")),

# --- 5. Halving.
a, r = 320, 0.5
B.Q("number_sequences", "pattern_sequence",
    f"A ball is dropped and the height of each bounce is half the one before: "
    f"{shown(seq(a, r, 4, g=True))} centimetres. How high is the next bounce?",
    key=gstep(a, r, 5), verify=gclosed(a, r, 5),
    wrong=[(gstep(a, r, 4) - 40, "operation_swap"), (gstep(a, r, 4), "partial_step"),
           (gstep(a, r, 6), "off_by_one")],
    expl="Half of 40 is 20 cm. 0 would need the bounce to stop altogether, and 10 halves "
         "one bounce too many.",
    fmt=unit("cm")),

# --- 6. Missing middle term.
a, d = 11, 7
B.Q("number_sequences", "pattern_sequence",
    f"In this sequence one number has been rubbed out: 11, ___, 25, 32. What number "
    f"belongs in the gap?",
    key=step(a, d, 2), verify=(11 + 25) // 2,        # it sits midway between its neighbours
    wrong=[(step(a, d, 2) - 1, "off_by_one"), (11 + 25, "operation_swap"),
           (step(a, d, 3), "misread_data")],
    expl="The steps from 25 to 32 are 7, so the gap holds 11 + 7 = 18. It also has to sit "
         "midway between 11 and 25, and (11 + 25) / 2 = 18 as well. 36 adds the two "
         "neighbours instead of finding the middle of them.",
    fmt=PLAIN),

# --- 7. Square numbers.
B.Q("number_sequences", "pattern_sequence",
    "A pattern is made from square arrays of dots: 1, 4, 9, 16, 25. How many dots are in "
    "the next square?",
    key=6 * 6, verify=sum(range(1, 12, 2)),          # a square is the sum of the odd numbers
    wrong=[(25 + 6, "operation_swap"), (25 * 2, "misread_data"), (49, "off_by_one")],
    expl="Each term is a square number, and the next is 6 x 6 = 36 dots. Another way to "
         "see it: the gaps go 3, 5, 7, 9, so the next gap is 11 and 25 + 11 = 36. 31 adds "
         "6 rather than squaring it, and 49 jumps to 7 x 7, one square too far.",
    fmt=unit("dots")),

# --- 8. Triangular numbers.
B.Q("number_sequences", "pattern_sequence",
    "Cans are stacked in a triangle, and the totals for the first five triangles are "
    "1, 3, 6, 10, 15. How many cans are in the sixth triangle?",
    key=6 * 7 // 2, verify=sum(range(1, 7)),
    wrong=[(15 + 5, "off_by_one"), (15 * 2, "operation_swap"), (15 + 7, "misread_data")],
    difficulty="hard", confidence=0.91,
    expl="The gaps grow by one each time — 2, 3, 4, 5 — so the next gap is 6 and "
         "15 + 6 = 21 cans. Adding 1 + 2 + 3 + 4 + 5 + 6 gives 21 too. 20 uses a gap of 5, "
         "repeating the gap before instead of growing it, and 22 grows the gap by 2 when "
         "it grows by 1.",
    fmt=unit("cans")),

# --- 9. Add the two before.
B.Q("number_sequences", "pattern_sequence",
    "In this sequence each number is the sum of the two before it: 2, 3, 5, 8, 13. What "
    "is the next number?",
    key=8 + 13, verify=13 + 8,
    wrong=[(13 * 2, "misread_data"), (13 + 5, "off_by_one"), (13 + 3, "operation_swap")],
    expl="Adding the two most recent numbers gives 8 + 13 = 21. 26 doubles the last number "
         "instead, which only matches by accident earlier in the sequence, and 18 reaches "
         "back past 8 to the wrong pair.",
    fmt=PLAIN),

# --- 10. Two rules alternating.
B.Q("number_sequences", "pattern_sequence",
    "This sequence adds 5, then takes away 2, then adds 5, and so on: 10, 15, 13, 18, 16. "
    "What is the next number?",
    key=16 + 5, verify=10 + 3 * 5 - 2 * 2,           # from the start: three +5s, two -2s
    wrong=[(16 - 2, "misread_data"), (16 + 3, "operation_swap"), (16 + 5 + 5, "off_by_one")],
    difficulty="hard", confidence=0.90,
    expl="The last step was a take away 2, so the next step adds 5: 16 + 5 = 21. 14 "
         "repeats the take away when it is the adding turn, 19 does both steps at once when "
         "only one comes next, and 26 adds 5 twice over.",
    fmt=PLAIN),

# --- 11. Decimal steps.
a, d = 2.5, 0.5
B.Q("number_sequences", "pattern_sequence",
    f"A tap fills a bucket and the level is read every minute: {shown(seq(a, d, 4))} "
    f"litres. What is the next reading?",
    key=step(a, d, 5), verify=closed(a, d, 5),
    wrong=[(step(a, d, 4) + 1, "misread_data"), (step(a, d, 4), "partial_step"),
           (step(a, d, 4) + 0.05, "place_value")],
    expl="The level goes up half a litre each minute, so after 4 comes 4.5 L. 5 adds a "
         "whole litre instead of half of one, and 4.05 slips a place and adds five "
         "hundredths.",
    fmt=unit("L")),

# --- 12. Mixed numbers.
B.Q("number_sequences", "pattern_sequence",
    "A recipe is scaled up in equal steps: 1/2 cup, 1 cup, 1 1/2 cups, 2 cups. How much "
    "does the next step use?",
    key="2 1/2 cups", verify="2 1/2 cups",
    wrong=[("3 cups", "operation_swap"), ("2 1/4 cups", "misread_data"),
           ("4 cups", "wrong_attribute")],
    expl="Each step adds half a cup, so after 2 cups comes 2 1/2 cups. 3 cups adds a whole "
         "cup, and 4 cups doubles the last amount rather than continuing the steady steps.",
    fmt=PLAIN),

# --- 13. Naming the rule.
B.Q("number_sequences", "pattern_sequence",
    "Look at this sequence: 4, 7, 10, 13, 16. Which rule describes how to get any term "
    "from its position in the sequence?",
    key="multiply the position by 3, then add 1",
    verify="multiply the position by 3, then add 1",
    wrong=[("multiply the position by 3", "partial_step"),
           ("add 3 to the position", "operation_swap"),
           ("multiply the position by 4", "misread_data")],
    difficulty="hard", confidence=0.90,
    expl="Position 1 gives 3 x 1 + 1 = 4, position 2 gives 3 x 2 + 1 = 7, and so on to "
         "position 5 giving 16. Multiply the position by 3 gets the steps right but every "
         "term lands 1 short, and multiply the position by 4 works for position 1 alone.",
    fmt=PLAIN),

# --- 14. Which position holds a value.
a, d = 6, 5
B.Q("number_sequences", "multi_step",
    f"A sequence starts at 6 and goes up by 5 each time: {shown(seq(a, d, 4))}. In which "
    f"position does the number 51 appear?",
    key=(51 - a) // d + 1, verify=next(i for i in range(1, 30) if step(a, d, i) == 51),
    wrong=[((51 - a) // d, "off_by_one"), ((51 + a) // d, "operation_swap"),
           (51 - a, "partial_step")],
    difficulty="hard", confidence=0.91,
    expl="From 6 you need 51 - 6 = 45 more, and 45 / 5 = 9 steps, which lands on the 10th "
         "term because the first term took no steps at all. 9 counts the steps rather than "
         "the positions, and 45 is the distance travelled, not a position.",
    fmt=PLAIN),

# --- 15. A term far along.
a, d = 3, 4
B.Q("number_sequences", "multi_step",
    f"A pattern of matchsticks starts with 3 and uses 4 more for each new shape: "
    f"{shown(seq(a, d, 4))}. How many matchsticks does the 20th shape use?",
    key=step(a, d, 20), verify=closed(a, d, 20),
    wrong=[(a + 20 * d, "off_by_one"), (20 * d, "partial_step"), (a * 20, "operation_swap")],
    difficulty="hard", confidence=0.91,
    expl="Getting to the 20th shape takes 19 steps of 4, so it uses 3 + 19 x 4 = 79 "
         "matchsticks. 83 takes 20 steps, one more than there are gaps between the first "
         "shape and the twentieth, and 80 forgets the 3 the pattern starts with.",
    fmt=unit("matchsticks")),

# --- 16. Total of the terms.
B.Q("number_sequences", "multi_step",
    "The first five even numbers are 2, 4, 6, 8 and 10. What is their total?",
    key=sum([2, 4, 6, 8, 10]), verify=5 * (2 + 10) // 2,   # pair the ends: five lots of 6
    wrong=[(10, "partial_step"), (5 * 10, "operation_swap"), (2 + 4 + 6 + 8, "misread_data")],
    expl="Adding them gives 2 + 4 + 6 + 8 + 10 = 30. Pairing the outside numbers is "
         "quicker: 2 and 10 make 12, 4 and 8 make 12, and 6 is half of 12, which is five "
         "lots of 6. 50 multiplies the largest by how many there are, which would need "
         "every number to be 10, and 20 stops after 2 + 4 + 6 + 8 and never reaches "
         "the 10.",
    fmt=PLAIN),

# --- 17. A rule with two operations, applied over and over.
B.Q("number_sequences", "pattern_sequence",
    "A sequence starts at 3, and each number after that is double the one before plus 1: "
    "3, 7, 15, 31. What is the next number?",
    key=31 * 2 + 1, verify=(31 + 1) * 2 - 1,         # the same rule rearranged
    wrong=[(31 * 2, "partial_step"), (31 + 16, "misread_data"), (31 * 2 + 2, "off_by_one")],
    difficulty="hard", confidence=0.90,
    expl="Double 31 to get 62, then add 1: 63. 62 stops after the doubling and leaves the "
         "add out, and 64 adds 2 instead of the 1 the rule names.",
    fmt=PLAIN),

# --- 18. Counting terms in a range.
a, d = 7, 8
B.Q("number_sequences", "multi_step",
    "Counting on in eights from 7, the numbers reached are 7, 15, 23 and so on up to 55. "
    "How many numbers are in that list altogether?",
    key=(55 - a) // d + 1, verify=len([x for x in range(7, 56) if (x - 7) % 8 == 0]),
    wrong=[((55 - a) // d, "off_by_one"), (55 - a, "partial_step"), (8, "misread_data")],
    difficulty="hard", confidence=0.91,
    expl="From 7 to 55 is 48, and 48 / 8 = 6 steps, but the starting number counts too, so "
         "there are 7 numbers. 6 counts the steps and forgets that 7 itself is on the list, "
         "and 48 is the distance from one end to the other rather than a count.",
    fmt=unit("numbers")),

# --- 19. The odd one out.
B.Q("number_sequences", "pattern_sequence",
    "Four of these five numbers are square numbers: 4, 9, 16, 24, 25. Which one is not?",
    key=24, verify=next(x for x in [4, 9, 16, 24, 25] if int(x ** 0.5) ** 2 != x),
    wrong=[(16, "misread_data"), (25, "wrong_attribute"), (4, "partial_step")],
    expl="A square number is something times itself: 4 = 2 x 2, 9 = 3 x 3, 16 = 4 x 4 and "
         "25 = 5 x 5. Nothing multiplied by itself gives 24, which sits between 16 and 25. "
         "25 is a square even though it is the largest number here.",
    fmt=PLAIN),

# --- 20. Working backwards to the start.
a, d = 4, 9
B.Q("number_sequences", "multi_step",
    "A sequence goes up by 9 each time. Its fourth term is 31. What is its first term?",
    key=31 - 3 * d, verify=closed(a, d, 1),
    wrong=[(31 - 4 * d, "off_by_one"), (31 - d, "partial_step"), (31 + 3 * d, "inverse")],
    difficulty="hard", confidence=0.90,
    expl="Going back from the fourth term to the first means undoing 3 steps, not 4: "
         "31 - 27 = 4. Check it forwards: 4, 13, 22, 31. -5 takes away four steps, one too "
         "many, and 58 goes forwards instead of back.",
    fmt=PLAIN),

# ===================================================== function machines (16)


def machine(x, ops):
    """Run the machine forwards."""
    for op, v in ops:
        x = {"+": x + v, "-": x - v, "*": x * v, "/": x / v}[op]
    return x


def unmachine(y, ops):
    """Run it backwards. Feeding the answer back through must return the input."""
    for op, v in reversed(ops):
        y = {"+": y - v, "-": y + v, "*": y / v, "/": y * v}[op]
    return y


def MQ(cat, stem, inp, ops, wrong, expl, fmt=PLAIN, **kw):
    """A machine item, verified by the round trip rather than by a second typed number."""
    out = machine(inp, ops)
    back = unmachine(out, ops)
    B.Q(cat, "pattern_sequence", stem,
        key=out, verify=out if abs(back - inp) < 1e-9 else "ROUND TRIP FAILED",
        wrong=wrong, expl=expl, fmt=fmt, **kw)


# --- 21. One step, multiply.
MQ("function_machines",
   "A number machine multiplies whatever goes in by 5. If 8 goes in, what comes out?",
   8, [("*", 5)],
   wrong=[(8 + 5, "operation_swap"), (8 * 5 - 5, "off_by_one"), (8 * 50, "place_value")],
   expl="The machine multiplies, so 8 x 5 = 40 comes out. 13 adds the 5 instead of "
        "multiplying by it, and 400 slips a place.")

# --- 22. One step, add.
MQ("function_machines",
   "A different machine adds 12 to every number that goes in. What comes out when 29 goes "
   "in?",
   29, [("+", 12)],
   wrong=[(29 * 12, "operation_swap"), (29 - 12, "inverse"), (29 + 21, "misread_data")],
   expl="Adding gives 29 + 12 = 41. 348 multiplies instead, and 17 takes the 12 away, "
        "which is what the machine would do running backwards.")

# --- 23. Two steps.
MQ("function_machines",
   "A machine multiplies by 3 and then adds 4. What comes out when 6 goes in?",
   6, [("*", 3), ("+", 4)],
   wrong=[((6 + 4) * 3, "wrong_attribute"), (6 * 3, "partial_step"), (6 * 3 + 3, "misread_data")],
   expl="Multiply first, then add: 6 x 3 = 18, and 18 + 4 = 22. 30 does the two steps in "
        "the wrong order, adding 4 before multiplying, and 18 stops after the first step.")

# --- 24. Two steps with a subtraction.
MQ("function_machines",
   "A machine doubles a number and then takes away 7. What comes out when 9 goes in?",
   9, [("*", 2), ("-", 7)],
   wrong=[(9 * 2 + 7, "inverse"), ((9 - 7) * 2, "wrong_attribute"), (9 * 2, "partial_step")],
   expl="Double 9 to get 18, then take away 7: 11. 25 adds the 7 rather than taking it "
        "off, and 4 takes it off before doubling, which is the two steps in the wrong "
        "order.")

# --- 25. Running one step backwards.
B.Q("function_machines", "pattern_sequence",
    "A machine adds 15 to every number. Something came out as 42. What went in?",
    key=42 - 15, verify=machine(42 - 15, [("+", 15)]) - 15,
    wrong=[(42 + 15, "inverse"), (42 - 15 - 1, "off_by_one"), (42 // 15, "operation_swap")],
    expl="Running the machine backwards means undoing the adding: 42 - 15 = 27. Check it "
         "forwards: 27 + 15 = 42. 57 adds 15 again, which is running the machine the way "
         "it already went.",
    fmt=PLAIN),

# --- 26. Running a multiply backwards.
B.Q("function_machines", "pattern_sequence",
    "Another machine multiplies every number by 6. A 54 appeared at the output end. "
    "Which number must have been fed in?",
    key=54 // 6, verify=next(x for x in range(1, 60) if x * 6 == 54),
    wrong=[(54 * 6, "inverse"), (54 - 6, "operation_swap"), (54 // 6 + 1, "off_by_one")],
    expl="Undoing a multiply means dividing: 54 / 6 = 9. Check it forwards: 9 x 6 = 54. "
         "324 multiplies again instead of undoing, and 48 takes 6 away rather than "
         "dividing by it.",
    fmt=PLAIN),

# --- 27. Two steps backwards.
B.Q("function_machines", "multi_step",
    "A machine multiplies by 4 and then adds 5. Something came out as 41. What went in?",
    key=(41 - 5) // 4, verify=unmachine(41, [("*", 4), ("+", 5)]),
    wrong=[(41 // 4 - 5, "wrong_attribute"), ((41 + 5) // 4, "inverse"),
           (41 - 5, "partial_step")],
    difficulty="hard", confidence=0.91,
    expl="Undo the steps in the opposite order: take off the 5 first, 41 - 5 = 36, then "
         "divide by 4 to get 9. Check it forwards: 9 x 4 + 5 = 41. 36 stops after undoing "
         "the adding, and 11 undoes the multiplying first, which is the wrong order.",
    fmt=PLAIN),

# --- 28. Find the rule from a table.
TBL1 = table([["In", "1", "2", "3", "4"], ["Out", "5", "9", "13", "17"]])
B.Q("function_machines", "data_interpretation",
    "The table shows what a number machine does. Which rule is the machine using?",
    key="multiply by 4, then add 1", verify="multiply by 4, then add 1",
    wrong=[("add 4", "partial_step"), ("multiply by 5", "misread_data"),
           ("multiply by 4", "wrong_attribute")],
    difficulty="hard", confidence=0.91,
    expl="The outputs go up by 4 each time the input goes up by 1, so the machine "
         "multiplies by 4 — and 1 x 4 is 4, one short of 5, so it also adds 1. Check the "
         "last pair: 4 x 4 + 1 = 17. Add 4 and multiply by 5 both happen to give 5 for the "
         "first input, which is exactly why the table lists four pairs and not one: "
         "neither survives the second, where 2 has to give 9.",
    fig=TBL1, fmt=PLAIN),

# --- 29. A dividing rule.
TBL2 = table([["In", "2", "4", "6", "8"], ["Out", "1", "2", "3", "4"]])
B.Q("function_machines", "data_interpretation",
    "The table shows a second machine. What does this machine do to each number?",
    key="divides it by 2", verify="divides it by 2",
    wrong=[("takes 1 away from it", "misread_data"), ("multiplies it by 2", "inverse"),
           ("divides it by 4", "wrong_attribute")],
    expl="Every output is half its input: 2 becomes 1, 8 becomes 4. Takes 1 away from it "
         "matches the first pair but fails at once — 8 would give 7, not 4 — and "
         "multiplies it by 2 runs the machine the wrong way.",
    fig=TBL2, fmt=PLAIN),

# --- 30. Two machines in a row.
MQ("function_machines",
   "Machine A multiplies by 3. Machine B adds 7. A number goes into A, and whatever comes "
   "out goes straight into B. If 5 goes into A, what comes out of B?",
   5, [("*", 3), ("+", 7)],
   wrong=[((5 + 7) * 3, "wrong_attribute"), (5 * 3, "partial_step"), (5 + 7, "misread_data")],
   expl="A turns 5 into 5 x 3 = 15, and B turns that into 15 + 7 = 22. 36 puts the number "
        "through B first and then A, which is the machines in the wrong order, and 15 "
        "stops after machine A.")

# --- 31. The same machines, the other way round.
MQ("function_machines",
   "Using the same two machines, a number now goes into B first and then into A. If 5 goes "
   "into B, what comes out of A?",
   5, [("+", 7), ("*", 3)],
   wrong=[(5 * 3 + 7, "wrong_attribute"), (5 + 7, "partial_step"), (5 * 3, "misread_data")],
   difficulty="hard", confidence=0.91,
   expl="B turns 5 into 12, and A turns that into 12 x 3 = 36. 22 is the answer for the "
        "machines in the other order, which is why the order matters, and 12 stops after "
        "machine B.")

# --- 32. Missing output in a table.
TBL3 = table([["In", "3", "5", "7", "9"], ["Out", "11", "17", "?", "29"]])
B.Q("function_machines", "data_interpretation",
    "The table shows a machine with one output missing. What number belongs where the "
    "question mark is?",
    key=7 * 3 + 2, verify=(17 + 29) // 2,            # midway between the two either side
    wrong=[(7 * 3, "partial_step"), (17 + 3, "misread_data"), (7 + 11, "operation_swap")],
    difficulty="hard", confidence=0.90,
    expl="The machine multiplies by 3 and adds 2: 3 x 3 + 2 = 11 and 5 x 3 + 2 = 17. So "
         "7 gives 7 x 3 + 2 = 23. It also has to sit midway between 17 and 29. 21 stops "
         "after multiplying, and 20 adds 3 to the output before it rather than using the "
         "rule.",
    fig=TBL3, fmt=PLAIN),

# --- 33. Missing input in a table.
TBL4 = table([["In", "2", "?", "8", "11"], ["Out", "9", "21", "33", "45"]])
B.Q("function_machines", "data_interpretation",
    "This machine multiplies by 4 and adds 1. One input is missing from the table. What "
    "number belongs where the question mark is?",
    key=(21 - 1) // 4, verify=unmachine(21, [("*", 4), ("+", 1)]),
    wrong=[(21 - 1, "partial_step"), (21 * 4, "operation_swap"), ((21 + 3) // 4, "off_by_one")],
    difficulty="hard", confidence=0.91,
    expl="Undo the rule in the opposite order: take off the 1 to get 21 - 1 = 20, then "
         "divide by 4 to get 5. Check it forwards: 5 x 4 + 1 = 21. 20 stops after undoing "
         "the adding, and 84 multiplies by 4 when undoing calls for dividing.",
    fig=TBL4, fmt=PLAIN),

# --- 34. A number the machine leaves alone.
B.Q("function_machines", "multi_step",
    "A machine doubles a number and then takes away 6. For which number does the machine "
    "give back exactly the number that went in?",
    key=6, verify=next(x for x in range(1, 40) if x * 2 - 6 == x),
    wrong=[(3, "partial_step"), (12, "operation_swap"), (0, "misread_data")],
    difficulty="hard", confidence=0.90,
    expl="Try 6: doubling gives 12 and taking away 6 leaves 6, the number that went in. "
         "3 gives 0, and 12 gives 18, so neither comes back unchanged.",
    fmt=PLAIN),

# --- 35. Two machines agreeing.
B.Q("function_machines", "multi_step",
    "Machine C adds 10 to a number. Machine D multiplies it by 3. For which number do both "
    "machines give the same answer?",
    key=5, verify=next(x for x in range(1, 40) if x + 10 == x * 3),
    wrong=[(10, "misread_data"), (15, "operation_swap"), (3, "partial_step")],
    difficulty="hard", confidence=0.90,
    expl="Try 5: adding 10 gives 15, and multiplying by 3 gives 15 as well. 10 gives 20 "
         "from C and 30 from D, which do not match, and 15 gives 25 and 45.",
    fmt=PLAIN),

# --- 36. The machine used twice.
MQ("function_machines",
   "A machine doubles a number and adds 3. A number is put through the machine, and then "
   "the answer is put through the same machine again. If 4 goes in first, what comes out "
   "at the end?",
   4, [("*", 2), ("+", 3), ("*", 2), ("+", 3)],
   wrong=[(4 * 2 + 3, "partial_step"), ((4 * 2 + 3) * 2, "misread_data"),
          ((4 + 3) * 2 * 2, "wrong_attribute")],
   difficulty="hard", confidence=0.90,
   expl="First pass: 4 x 2 + 3 = 11. Second pass: 11 x 2 + 3 = 25. 11 stops after one pass "
        "through the machine, and 22 does the doubling of the second pass but leaves off "
        "the adding. 28 adds the 3 before doubling, both times.")

if __name__ == "__main__":
    B.write()
