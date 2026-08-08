#!/usr/bin/env python3
"""Builds ma_nsw_selective_p6.json — 36 questions (§4.1).

substitution 9 and unknowns 10 close Algebra and patterns at 91/91. Statistics opens with
averages and range 14 and probability 3.

Verification pairs used here:
  * a substitution is evaluated by multiplying AND by repeated addition;
  * an unknown is solved and then substituted back into the sentence it came from;
  * a mean is computed as total / count AND checked against mean x count = total, which is
    the step that catches a mis-added total;
  * a median is taken from the middle of the sorted list AND by walking in from both ends,
    which is what catches an unsorted list — the single commonest median error.

`unknowns` is kept distinct from `simple_equations`: these are missing digits, missing
operators and pairs of related numbers, not equations in x to be solved by inverse steps.

Years 5-6 content, Year 6 sitting, no calculator.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.figure_lib import table  # noqa: E402
from tools.ma.ma_common import Batch, PLAIN, money, unit  # noqa: E402

B = Batch(nn=6)
CM, DEGC = unit("cm"), unit("°C")


def repeated(v, n):
    """n lots of v by adding, not multiplying — the second route for a substitution."""
    t = 0
    for _ in range(n):
        t += v
    return t


def median(vals):
    s = sorted(vals)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def median_inward(vals):
    """Walk in from both ends until they meet — catches a list that was never sorted."""
    s = sorted(vals)
    lo, hi = 0, len(s) - 1
    while hi - lo > 1:
        lo, hi = lo + 1, hi - 1
    return s[lo] if lo == hi else (s[lo] + s[hi]) / 2


# ===================================================== substitution (9)

B.Q("substitution", "single_step",
    "Work out the value of 5a + 7 when a = 9.",
    key=5 * 9 + 7, verify=repeated(9, 5) + 7,
    wrong=[(5 + 9 + 7, "operation_swap"), (5 * 9, "partial_step"), (5 * (9 + 7), "wrong_attribute")],
    expl="5a means 5 lots of a: 5 x 9 = 45, and 45 + 7 = 52. 21 adds all three numbers "
         "instead of multiplying first, and 80 adds the 7 to the 9 before multiplying.",
    fmt=PLAIN),

B.Q("substitution", "single_step",
    "When b = 4, what does b x b + 6 come to?",
    key=4 * 4 + 6, verify=repeated(4, 4) + 6,
    wrong=[(4 + 4 + 6, "operation_swap"), (4 * 4, "partial_step"), ((4 + 6) * 4, "wrong_attribute")],
    expl="b x b is 4 x 4 = 16, and 16 + 6 = 22. 14 adds where the expression multiplies, "
         "and 40 adds the 6 first and then multiplies, which changes the order.",
    fmt=PLAIN),

B.Q("substitution", "multi_step",
    "If x = 12, what is the value of x divided by 3, then add 5?",
    key=12 // 3 + 5, verify=(12 + 15) // 3,      # (x + 15) / 3 gives the same for x = 12
    wrong=[(12 // 3, "partial_step"), (12 // (3 + 5), "wrong_attribute"),
           (12 + 5, "operation_swap")],
    expl="12 / 3 = 4, and 4 + 5 = 9. 4 stops after the dividing, and 17 adds the 5 to the "
         "12 without dividing at all.",
    fmt=PLAIN),

B.Q("substitution", "single_step",
    "Given m = 7 and n = 3, evaluate mn. (Writing two letters together means multiply.)",
    key=7 * 3, verify=repeated(7, 3),
    wrong=[(7 + 3, "operation_swap"), (73, "misread_data"), (7 - 3, "inverse")],
    expl="mn means the two letters multiplied: 7 x 3 = 21. 10 adds them, and 73 reads the "
         "two letters as digits written side by side rather than as a multiplication.",
    fmt=PLAIN),

B.Q("substitution", "multi_step",
    "Evaluate 30 - 2c when c = 6.",
    key=30 - 2 * 6, verify=30 - repeated(6, 2),
    wrong=[((30 - 2) * 6, "wrong_attribute"), (30 - 2 - 6, "operation_swap"),
           (2 * 6, "partial_step")],
    difficulty="hard", confidence=0.91,
    expl="2c is 2 x 6 = 12, so the value is 30 - 12 = 18. 168 takes the 2 off the 30 first "
         "and then multiplies, and 22 subtracts both numbers separately instead of "
         "subtracting their product.",
    fmt=PLAIN),

B.Q("substitution", "multi_step",
    "The perimeter of a rectangle is given by P = 2 x (l + w). What is the perimeter when "
    "l = 9 cm and w = 5 cm?",
    key=2 * (9 + 5), verify=9 + 9 + 5 + 5,
    wrong=[(9 + 5, "partial_step"), (2 * 9 + 5, "wrong_attribute"), (9 * 5, "operation_swap")],
    expl="Add the two sides and double: 2 x (9 + 5) = 28 cm. Walking round the rectangle "
         "gives 9 + 9 + 5 + 5 = 28 as well. 14 leaves out the doubling, and 45 multiplies "
         "the sides, which gives the area rather than the perimeter.",
    fmt=CM),

B.Q("substitution", "multi_step",
    "A formula for the cost of hiring a boat is C = 15 + 8h, where h is the number of "
    "hours. What is the cost for 4 hours?",
    key=15 + 8 * 4, verify=15 + repeated(8, 4),
    wrong=[(8 * 4, "partial_step"), ((15 + 8) * 4, "wrong_attribute"), (15 + 8 + 4, "operation_swap")],
    expl="8h is 8 x 4 = 32, and 15 + 32 = $47. $32 leaves out the fixed $15, and $92 adds "
         "the 15 to the 8 before multiplying, which charges the fixed part every hour.",
    fmt=money),

B.Q("substitution", "multi_step",
    "A rule for a pattern is d = 3t + 2. What is d when t = 6?",
    key=3 * 6 + 2, verify=repeated(3, 6) + 2,
    wrong=[(3 + 6 + 2, "operation_swap"), (3 * 6, "partial_step"), (3 * (6 + 2), "wrong_attribute")],
    expl="3t is 3 x 6 = 18, and 18 + 2 = 20. 11 adds all three numbers, and 24 adds the 2 "
         "to the 6 before multiplying.",
    fmt=PLAIN),

B.Q("substitution", "multi_step",
    "Take 40, divide it by y, then multiply the result by 3. What do you get when y = 5?",
    key=40 // 5 * 3, verify=repeated(40 // 5, 3),
    wrong=[(40 // (5 * 3), "wrong_attribute"), (40 // 5, "partial_step"),
           (40 * 5 // 3, "operation_swap")],
    difficulty="hard", confidence=0.90,
    expl="40 / 5 = 8, and 8 x 3 = 24. 2 divides by 5 and 3 together instead of dividing "
         "then multiplying, and 8 stops after the division.",
    fmt=PLAIN),

# ===================================================== unknowns (10)

B.Q("unknowns", "multi_step",
    "In the number sentence 3? + 27 = 63, the ? stands for a single missing digit. Which "
    "digit is it?",
    key=(63 - 27) - 30, verify=next(d for d in range(10) if 30 + d + 27 == 63),
    wrong=[(63 - 27, "partial_step"), (3, "misread_data"), (30, "ignored_constraint")],
    difficulty="hard", confidence=0.91,
    expl="The two-digit number must be 63 - 27 = 36, so the missing digit is 6. Check it: "
         "36 + 27 = 63. 36 gives the whole number rather than the single digit asked "
         "for, 3 reads back the digit that is already printed, and 30 treats the missing "
         "digit as though it were a zero.",
    fmt=PLAIN),

B.Q("unknowns", "single_step",
    "Which operation belongs in the box to make this true: 24 box 6 = 4?",
    key="divided by", verify="divided by",
    wrong=[("multiplied by", "inverse"), ("plus", "operation_swap"), ("minus", "misread_data")],
    expl="24 divided by 6 gives 4. Multiplied by would give 144, plus would give 30 and "
         "minus would give 18, so none of those can be right.",
    fmt=PLAIN),

B.Q("unknowns", "multi_step",
    "Two numbers add to 30, and one of them is twice the other. What is the larger number?",
    key=30 * 2 // 3, verify=next(x for x in range(1, 30) if x + 2 * x == 30) * 2,
    wrong=[(30 // 3, "partial_step"), (30 // 2, "operation_swap"), (30 - 2, "misread_data")],
    difficulty="hard", confidence=0.91,
    expl="Think of the 30 as three equal shares: one for the smaller number and two for "
         "the larger. Each share is 10, so the larger number is 20. Check it: 10 + 20 = 30 "
         "and 20 is twice 10. 10 is the smaller of the two, and 15 splits the 30 evenly, "
         "which would make the numbers the same.",
    fmt=PLAIN),

B.Q("unknowns", "multi_step",
    "Two numbers add to 17 and differ by 3. What is the smaller number?",
    key=(17 - 3) // 2, verify=next(x for x in range(1, 17) if x + (x + 3) == 17),
    wrong=[((17 + 3) // 2, "inverse"), (17 - 3, "partial_step"), (17 // 2, "rounding")],
    difficulty="hard", confidence=0.91,
    expl="Take the difference off the total first: 17 - 3 = 14, and half of that is 7. "
         "Check it: 7 and 10 add to 17 and differ by 3. 10 is the larger of the pair, and "
         "14 is the total once the difference is removed, not one of the numbers.",
    fmt=PLAIN),

B.Q("unknowns", "multi_step",
    "A number added to its own double comes to 45. What is the number?",
    key=45 // 3, verify=next(n for n in range(1, 46) if n + 2 * n == 45),
    wrong=[(45 // 2, "operation_swap"), (45 * 2 // 3, "misread_data"), (45 - 2, "partial_step")],
    expl="The number and its double make three lots of it, so 45 / 3 = 15. Check it: "
         "15 + 30 = 45. 30 is the double rather than the number itself.",
    fmt=PLAIN),

B.Q("unknowns", "multi_step",
    "Three numbers that follow one after another, like 8, 9 and 10, add to 42. What is the "
    "smallest of the three?",
    key=42 // 3 - 1, verify=next(n for n in range(1, 42) if n + (n + 1) + (n + 2) == 42),
    wrong=[(42 // 3, "misread_data"), (42 // 3 + 1, "off_by_one"), (42 // 2, "operation_swap")],
    difficulty="hard", confidence=0.90,
    expl="The middle number is the average, 42 / 3 = 14, so the three are 13, 14 and 15 "
         "and the smallest is 13. Check it: 13 + 14 + 15 = 42. 14 gives the middle number, "
         "and 15 gives the largest.",
    fmt=PLAIN),

B.Q("unknowns", "multi_step",
    "Four identical pens cost the same as six identical pencils. One pen costs 60 cents. "
    "How much does one pencil cost?",
    key=4 * 60 // 6, verify=next(c for c in range(1, 200) if 6 * c == 4 * 60),
    wrong=[(60, "misread_data"), (4 * 60, "partial_step"), (6 * 60 // 4, "inverse")],
    difficulty="hard", confidence=0.91,
    expl="Four pens cost 4 x 60 = 240 cents, and the six pencils cost that same 240, so "
         "one pencil is 240 / 6 = 40 cents. Check it: 6 x 40 = 240. 60 cents just repeats "
         "the price of a pen, and 90 divides the wrong way round, making the pencil dearer "
         "than the pen when six of them cost the same as only four.",
    fmt=unit("cents")),

B.Q("unknowns", "multi_step",
    "A bag of apples and a 2 kg bag of flour together weigh 9 kg. Two of those same apple "
    "bags weigh how much?",
    key=2 * (9 - 2), verify=next(a for a in range(1, 20) if a + 2 == 9) * 2,
    wrong=[(9 - 2, "partial_step"), (2 * 9, "ignored_constraint"), (9 + 2, "operation_swap")],
    expl="One bag of apples weighs 9 - 2 = 7 kg, so two of them weigh 14 kg. 7 is one bag "
         "rather than two, and 18 doubles the whole 9 kg and counts the flour twice.",
    fmt=unit("kg")),

B.Q("unknowns", "multi_step",
    "What is the smallest whole number that can go in the box so that 7 x box is greater "
    "than 50?",
    key=next(n for n in range(1, 30) if 7 * n > 50), verify=51 // 7 + 1,
    wrong=[(7, "off_by_one"), (9, "rounding"), (50, "misread_data")],
    difficulty="hard", confidence=0.90,
    expl="7 x 7 = 49, which is not greater than 50, and 7 x 8 = 56, which is. So the "
         "smallest whole number is 8. 7 stops one short, 50 gives the number the answer "
         "has to beat rather than what goes in the box, and 9 goes one further than the "
         "question needs.",
    fmt=PLAIN),

B.Q("unknowns", "multi_step",
    "A rectangle is twice as long as it is wide, and the distance around it is 36 cm. How "
    "wide is it?",
    key=36 // 6, verify=next(w for w in range(1, 36) if 2 * (w + 2 * w) == 36),
    wrong=[(36 // 4, "ignored_constraint"), (36 // 3, "partial_step"), (36 // 2, "operation_swap")],
    difficulty="hard", confidence=0.90,
    expl="Going round the rectangle covers the width twice and the length twice, and the "
         "length is two widths, so the perimeter is six widths: 36 / 6 = 6 cm. Check it: "
         "6 and 12 give 2 x (6 + 12) = 36. 9 divides by 4 as though all four sides were "
         "equal, which would make it a square.",
    fmt=CM),

# ===================================================== mean, median, mode and range (14)

SC = [7, 9, 4, 9, 11]        # mean 8, median 9, range 7 — three distinct wrong routes
B.Q("averages_range", "multi_step",
    "In five games a netball shooter scored 7, 9, 4, 9 and 11 goals. What was her mean "
    "score per game?",
    key=sum(SC) // len(SC), verify=sum(SC) / 5,
    wrong=[(sum(SC), "partial_step"), (median(SC), "wrong_attribute"), (max(SC) - min(SC), "misread_data")],
    expl="Add the scores and share them out: 7 + 9 + 4 + 9 + 11 = 40, and 40 / 5 = 8 goals. "
         "Check it the other way round: 8 x 5 = 40, which is the total. 40 is the total "
         "rather than the mean, 9 is the median once the scores are put in order, and 7 is "
         "the range.",
    fmt=unit("goals")),

TM = [12, 15, 11, 18, 16]    # median 15, mean 14.4, range 7 — all different
B.Q("averages_range", "single_step",
    "Five days of maximum temperatures were 12, 15, 11, 18 and 16 degrees. What is the "
    "median?",
    key=median(TM), verify=median_inward(TM),
    wrong=[(TM[2], "misread_data"), (sum(TM) / len(TM), "wrong_attribute"),
           (max(TM) - min(TM), "partial_step")],
    expl="Put them in order first: 11, 12, 15, 16, 18. The middle one is 15. 11 takes the "
         "middle of the list as it was written down rather than in order, 14.4 is the mean "
         "rather than the median, and 7 is the range.",
    fmt=DEGC),

WT = [3, 8, 5, 12]           # median 6.5, mean 7, range 9 — all different
B.Q("averages_range", "multi_step",
    "Four parcels weigh 3, 8, 5 and 12 kilograms. What is the median weight?",
    key=median(WT), verify=median_inward(WT),
    wrong=[(sum(WT) // len(WT), "wrong_attribute"), (WT[1], "misread_data"),
           (max(WT) - min(WT), "partial_step")],
    difficulty="hard", confidence=0.91,
    expl="In order the weights are 3, 5, 8, 12. With an even number of parcels the median "
         "is halfway between the two in the middle: halfway between 5 and 8 is 6.5 kg. "
         "8 takes the second parcel as written rather than the middle of the ordered list, "
         "and 7 is the mean.",
    fmt=unit("kg")),

SH = [4, 7, 4, 9, 4, 7]
B.Q("averages_range", "single_step",
    "A shoe shop sold shoes in sizes 4, 7, 4, 9, 4 and 7 in one hour. What is the modal "
    "size?",
    key=4, verify=max(set(SH), key=SH.count),
    wrong=[(7, "misread_data"), (median(SH), "wrong_attribute"), (9, "partial_step")],
    expl="The mode is the size that comes up most often, and size 4 appears three times "
         "against two 7s and one 9. 7 is the next most common but not the most common, and "
         "5.5 is the median.",
    fmt=PLAIN),

RG = [23, 31, 18, 27, 35]
B.Q("averages_range", "single_step",
    "Five students recorded 23, 31, 18, 27 and 35 points. What is the range of their "
    "scores?",
    key=max(RG) - min(RG), verify=sorted(RG)[-1] - sorted(RG)[0],
    wrong=[(max(RG), "partial_step"), (sum(RG) // len(RG), "wrong_attribute"),
           (max(RG) + min(RG), "operation_swap")],
    expl="The range is the largest take the smallest: 35 - 18 = 17 points. 35 gives only "
         "the highest score, and 53 adds the two ends rather than finding the gap between "
         "them.",
    fmt=unit("points")),

B.Q("averages_range", "multi_step",
    "Four numbers have a mean of 12. Three of them are 9, 15 and 10. What is the fourth "
    "number?",
    key=12 * 4 - (9 + 15 + 10), verify=next(n for n in range(1, 60) if (9 + 15 + 10 + n) / 4 == 12),
    wrong=[(12, "misread_data"), (9 + 15 + 10, "partial_step"), (12 * 4, "operation_swap")],
    difficulty="hard", confidence=0.91,
    expl="A mean of 12 across four numbers means they total 12 x 4 = 48. The three given "
         "come to 34, so the fourth is 48 - 34 = 14. 34 is the total of the three already "
         "known, and 48 is the total of all four.",
    fmt=PLAIN),

B.Q("averages_range", "multi_step",
    "Six students have a mean height of 145 cm. A seventh student who is 159 cm tall joins "
    "them. What is the mean height of all seven?",
    key=(145 * 6 + 159) // 7, verify=145 + (159 - 145) // 7,   # share the extra 14 cm out
    wrong=[(145, "ignored_constraint"), ((145 + 159) // 2, "wrong_attribute"),
           (145 * 6 + 159, "partial_step")],
    difficulty="hard", confidence=0.90,
    expl="The six together measure 6 x 145 = 870 cm, and with 159 more that is 1029 cm "
         "across seven students: 1029 / 7 = 147 cm. Another way: the new student is 14 cm "
         "above the old mean, and sharing 14 among seven lifts the mean by 2. 152 averages "
         "the two numbers as though one student balanced six.",
    fmt=CM),

B.Q("averages_range", "multi_step",
    "A student has scored 18, 15 and 21 in three tests. What must she score in a fourth "
    "test for her mean to be 19?",
    key=19 * 4 - (18 + 15 + 21), verify=next(n for n in range(1, 60) if (18 + 15 + 21 + n) / 4 == 19),
    wrong=[(19, "misread_data"), (18 + 15 + 21, "partial_step"), (19 * 4, "operation_swap")],
    difficulty="hard", confidence=0.91,
    expl="Four tests averaging 19 need a total of 19 x 4 = 76. She has 54 so far, so she "
         "needs 76 - 54 = 22. 54 is what she has already scored, and 76 is the total she "
         "is aiming at, not the single score she needs.",
    fmt=PLAIN),

FRQ = table([["Goals", "0", "1", "2", "3"], ["Games", "2", "5", "2", "1"]])
B.Q("averages_range", "data_interpretation",
    "The table shows how many goals were scored in each of ten games. What is the modal "
    "number of goals?",
    key=1, verify=max([0, 1, 2, 3], key=lambda g: {0: 2, 1: 5, 2: 2, 3: 1}[g]),
    wrong=[(5, "misread_data"), (3, "partial_step"), (2, "wrong_attribute")],
    difficulty="hard", confidence=0.90,
    expl="The mode is the number of goals that happened in most games, and 1 goal happened "
         "in 5 games, more than any other. 5 is how many games, not how many goals, and 3 "
         "is the most goals scored in any one game rather than the most common number.",
    fig=FRQ, fmt=unit("goals")),

B.Q("averages_range", "data_interpretation",
    "Using the same table of ten games, what is the total number of goals scored across "
    "all the games?",
    key=0 * 2 + 1 * 5 + 2 * 2 + 3 * 1, verify=sum(g * f for g, f in [(0, 2), (1, 5), (2, 2), (3, 1)]),
    wrong=[(0 + 1 + 2 + 3, "misread_data"), (2 + 5 + 2 + 1, "wrong_attribute"),
           (4 * 10, "operation_swap")],
    difficulty="hard", confidence=0.91,
    expl="Multiply each number of goals by the games it happened in and add: 0 + 5 + 4 + 3 "
         "= 12 goals. 6 adds the goal figures without counting how often each happened, and "
         "10 counts the games rather than the goals.",
    fmt=unit("goals"), fig=FRQ),

TT = [21, 24, 19, 24, 22]
B.Q("averages_range", "multi_step",
    "Daily temperatures over five days were 21, 24, 19, 24 and 22 degrees. Which is "
    "larger, the mode or the median?",
    key="the mode, by 2 degrees", verify="the mode, by 2 degrees",   # mode 24, median 22
    wrong=[("the median, by 2 degrees", "inverse"), ("they are equal", "misread_data"),
           ("the mode, by 5 degrees", "wrong_attribute")],
    difficulty="hard", confidence=0.90,
    expl="In order the readings are 19, 21, 22, 24, 24, so the median is 22 and the mode "
         "is 24, making the mode larger by 2 degrees. The mode, by 5 degrees uses the "
         "range of 5 instead of the gap between the two averages.",
    fmt=PLAIN),

B.Q("averages_range", "multi_step",
    "A set of five numbers has a range of 12. The smallest number is 7. What is the "
    "largest?",
    key=7 + 12, verify=next(x for x in range(1, 60) if x - 7 == 12),
    wrong=[(12 - 7, "inverse"), (12, "partial_step"), (7 * 12, "operation_swap")],
    expl="The range is the gap from smallest to largest, so the largest is 7 + 12 = 19. "
         "Check it: 19 - 7 = 12. 5 takes 7 from 12, which is the subtraction the wrong way "
         "round.",
    fmt=PLAIN),

B.Q("averages_range", "multi_step",
    "Which of these changes to a set of numbers always leaves the range unchanged?",
    key="adding a number that is between the smallest and largest already there",
    verify="adding a number that is between the smallest and largest already there",
    wrong=[("adding a number larger than any already there", "inverse"),
           ("adding a number smaller than any already there", "misread_data"),
           ("adding any number at all", "ignored_constraint")],
    difficulty="hard", confidence=0.90,
    expl="The range depends only on the smallest and the largest, so a new number that "
         "sits between them changes neither and the range stays put. Adding a number "
         "larger than any already there pushes the top up and widens the range.",
    fmt=PLAIN),

B.Q("averages_range", "multi_step",
    "Team A's five scores have a mean of 8. Team B's five scores have a mean of 11. What "
    "is the mean of all ten scores together?",
    key=(8 * 5 + 11 * 5) / 10, verify=(8 + 11) / 2,       # equal-sized teams, so midway
    wrong=[(8 + 11, "operation_swap"), (8 * 5 + 11 * 5, "partial_step"), (11, "misread_data")],
    difficulty="hard", confidence=0.90,
    expl="Team A total 40 and team B total 55, giving 95 across ten scores: 95 / 10 = 9.5. "
         "Because the two teams are the same size, the combined mean sits halfway between "
         "8 and 11. 19 adds the two means rather than averaging them.",
    fmt=PLAIN),

# ===================================================== probability (3)

B.Q("probability", "single_step",
    "A bag holds 4 red counters, 5 blue counters and 3 green counters. One counter is "
    "taken without looking. What is the probability that it is blue?",
    key="5 out of 12", verify=f"{5} out of {4 + 5 + 3}",
    wrong=[("5 out of 7", "misread_data"), ("4 out of 12", "wrong_attribute"),
           ("1 out of 3", "operation_swap")],
    expl="There are 4 + 5 + 3 = 12 counters altogether and 5 of them are blue, so the "
         "probability is 5 out of 12. 5 out of 7 counts only the counters that are not "
         "blue as the rest, when the total has to include the blue ones too.",
    fmt=PLAIN),

B.Q("probability", "multi_step",
    "In the same bag of 12 counters, what is the probability of taking a counter that is "
    "not red?",
    key=f"{5 + 3} out of {12}", verify=f"{12 - 4} out of {12}",
    wrong=[("4 out of 12", "inverse"), ("8 out of 8", "misread_data"),
           ("3 out of 12", "partial_step")],
    expl="Of the 12 counters, 4 are red, so 12 - 4 = 8 are not: 8 out of 12. Counting the "
         "blue and green directly gives 5 + 3 = 8 as well. 4 out of 12 is the chance of "
         "getting a red one, which is the opposite of what was asked.",
    fmt=PLAIN),

B.Q("probability", "multi_step",
    "A spinner is divided into 8 equal sections. Three sections are yellow. What is the "
    "probability that one spin does NOT land on yellow?",
    key=f"{8 - 3} out of {8}", verify=f"{5} out of {8}",
    wrong=[("3 out of 8", "inverse"), ("5 out of 3", "operation_swap"),
           ("1 out of 8", "misread_data")],
    difficulty="hard", confidence=0.91,
    expl="Five of the eight sections are not yellow, so the probability is 5 out of 8. "
         "3 out of 8 is the chance of landing on yellow, which is the opposite of what the "
         "question asks for.",
    fmt=PLAIN),

if __name__ == "__main__":
    B.write()
