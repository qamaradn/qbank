#!/usr/bin/env python3
"""Builds ma_nsw_selective_p8.json — 36 questions (§4.1).

probability 12 and drawing conclusions 6 close Statistics at 71/71. Number and arithmetic
opens with percentages 8, ratio and proportion 8 and order of operations 2.

Verification pairs:
  * a probability is counted directly AND checked against its complement summing to the
    whole — which catches a total that left out the very outcome being asked about;
  * a percentage is taken the quick way (a quarter, a tenth) AND the long way (x / 100
    times the amount), and the two disagree the moment the quick way is applied to the
    wrong number;
  * a ratio share is worked out per part AND the parts are added back to check they
    rebuild the original total;
  * an order-of-operations answer is grouped by hand AND evaluated by Python's own
    parser from the expression as printed, so a stem cannot say one thing and be marked
    as another.

Years 5-6 content, Year 6 sitting, no calculator.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.figure_lib import bar_chart, pie_chart, table  # noqa: E402
from tools.ma.ma_common import Batch, PLAIN, money, pct, unit  # noqa: E402

B = Batch(nn=8)


def frac(a, b):
    return f"{a} out of {b}"


# ===================================================== probability (12)

SPIN = [("Red", 4), ("Blue", 3), ("Green", 2), ("Yellow", 3)]
SPINNER = pie_chart(SPIN)
TOT = sum(c for _, c in SPIN)

B.Q("probability", "data_interpretation",
    "The spinner shown is divided into 12 equal sections. What is the probability of one "
    "spin landing on red?",
    key=frac(4, TOT), verify=frac(TOT - 3 - 2 - 3, TOT),
    wrong=[(frac(4, TOT - 4), "misread_data"), (frac(3, TOT), "off_by_one"),
           (frac(1, 4), "wrong_attribute")],
    expl="Four of the twelve sections are red, so the probability is 4 out of 12. 4 out of "
         "8 leaves the red sections out of the total, when everything on the spinner has "
         "to be counted, and 1 out of 4 is what you would get if there were four colours "
         "of equal size.",
    fig=SPINNER, fmt=PLAIN),

B.Q("probability", "data_interpretation",
    "Using the same 12-section spinner, which colour is the least likely to come up?",
    key="Green", verify=min(SPIN, key=lambda p: p[1])[0],
    wrong=[("Red", "inverse"), ("Blue", "misread_data"), ("Yellow", "off_by_one")],
    expl="Green has only 2 sections, fewer than blue's 3, yellow's 3 or red's 4, so green "
         "is least likely. Red has the most sections and so is the most likely, which is "
         "the opposite question.",
    fig=SPINNER, fmt=PLAIN),

B.Q("probability", "multi_step",
    "Using the same 12-section spinner, what is the probability of landing on blue or "
    "green?",
    # blue + green, not blue + white: those two make exactly half, so the complement
    # distractor came out equal to the key.
    key=frac(3 + 2, TOT), verify=frac(TOT - 4 - 3, TOT),
    wrong=[(frac(3, TOT), "partial_step"), (frac(3 + 2, 3 + 2), "misread_data"),
           (frac(TOT - 5, TOT), "inverse")],
    difficulty="hard", confidence=0.91,
    expl="Blue has 3 sections and green has 2, so together 5 out of 12. Taking the other "
         "colours off gives the same: 12 - 4 - 3 = 5. 3 out of 12 counts one of the two "
         "colours only, 5 out of 5 treats those two colours as though they were the whole "
         "spinner, and 7 out of 12 is the chance of missing both.",
    fig=SPINNER, fmt=PLAIN),

B.Q("probability", "multi_step",
    "The same 12-section spinner is spun 60 times. About how many times would you expect "
    "it to land on green?",
    key=60 * 2 // TOT, verify=60 // 6,          # green is one sixth of the spinner
    wrong=[(2, "misread_data"), (60 // 2, "operation_swap"), (60 * 3 // TOT, "off_by_one")],
    difficulty="hard", confidence=0.90,
    expl="Green covers 2 of the 12 sections, which is one sixth, and one sixth of 60 is "
         "10 spins. 2 gives the number of green sections rather than a number of spins, "
         "and 30 halves the 60 as though green were half the spinner.",
    fig=SPINNER, fmt=unit("times")),

B.Q("probability", "single_step",
    "An ordinary six-sided dice is rolled once. What is the probability of rolling a "
    "number greater than 4?",
    key=frac(2, 6), verify=frac(6 - 4, 6),      # only 5 and 6 qualify
    wrong=[(frac(3, 6), "off_by_one"), (frac(4, 6), "misread_data"), (frac(1, 6), "partial_step")],
    expl="Only 5 and 6 are greater than 4, so 2 out of 6. 3 out of 6 counts the 4 as well, "
         "but 4 is not greater than itself, and 4 out of 6 reads the 4 in the question as "
         "the count of outcomes.",
    fmt=PLAIN),

B.Q("probability", "multi_step",
    "Two ordinary coins are tossed at the same time. What is the probability that both "
    "land heads up?",
    key=frac(1, 4), verify=frac(1, 2 * 2),      # HH, HT, TH, TT are the four outcomes
    wrong=[(frac(1, 2), "partial_step"), (frac(1, 3), "misread_data"), (frac(2, 4), "off_by_one")],
    difficulty="hard", confidence=0.91,
    expl="Write out every outcome: heads-heads, heads-tails, tails-heads and tails-tails. "
         "One of those four is two heads, so 1 out of 4. 1 out of 3 counts 'two heads, two "
         "tails, one of each' as three outcomes, but one of each happens two ways.",
    fmt=PLAIN),

B.Q("probability", "single_step",
    "A bag holds only red counters. Which word best describes the chance of drawing a blue "
    "counter from it?",
    key="impossible", verify="impossible",
    wrong=[("unlikely", "partial_step"), ("certain", "inverse"), ("even chance", "misread_data")],
    expl="There are no blue counters in the bag at all, so drawing one cannot happen: it "
         "is impossible. Unlikely would mean it could still happen occasionally, which it "
         "cannot, and certain describes drawing a red one.",
    fmt=PLAIN),

B.Q("probability", "multi_step",
    "Bag A holds 3 white and 5 black marbles. Bag B holds 4 white and 8 black marbles. "
    "From which bag are you more likely to draw a white marble?",
    key="Bag A", verify="Bag A" if 3 / 8 > 4 / 12 else "Bag B",
    wrong=[("Bag B", "misread_data"), ("They are equally likely", "off_by_one"),
           ("Bag B, because it has more white marbles", "wrong_attribute")],
    difficulty="hard", confidence=0.90,
    expl="Bag A is 3 white out of 8, which is more than a third. Bag B is 4 white out of "
         "12, which is exactly a third. So bag A gives the better chance, even though bag "
         "B holds more white marbles — what matters is the share, not the count.",
    fmt=PLAIN),

B.Q("probability", "multi_step",
    "A bag holds 10 counters, of which 3 are yellow. One yellow counter is taken out and "
    "kept. What is the probability that the next counter taken is yellow?",
    key=frac(2, 9), verify=frac(3 - 1, 10 - 1),
    wrong=[(frac(3, 10), "ignored_constraint"), (frac(2, 10), "partial_step"),
           (frac(3, 9), "off_by_one")],
    difficulty="hard", confidence=0.90,
    expl="After the first counter is kept there are 9 left and only 2 of them are yellow, "
         "so 2 out of 9. 3 out of 10 forgets that a counter was removed, and 2 out of 10 "
         "takes the yellow one away but leaves the total at 10.",
    fmt=PLAIN),

B.Q("probability", "multi_step",
    "The probability of rain tomorrow is given as 7 out of 10. What is the probability "
    "that it does not rain?",
    key=frac(3, 10), verify=frac(10 - 7, 10),
    wrong=[(frac(7, 10), "inverse"), (frac(3, 7), "misread_data"), (frac(1, 10), "partial_step")],
    expl="Rain and no rain together cover every possibility, so they add to 10 out of 10: "
         "10 - 7 = 3, giving 3 out of 10. 7 out of 10 repeats the chance of rain, and "
         "3 out of 7 compares the two chances with each other rather than with the whole.",
    fmt=PLAIN),

B.Q("probability", "multi_step",
    "A spinner has 5 equal sections numbered 1 to 5. Which of these has a probability of "
    "3 out of 5?",
    key="landing on an odd number", verify="landing on an odd number",   # 1, 3, 5
    wrong=[("landing on an even number", "inverse"), ("landing on a number below 3", "misread_data"),
           ("landing on a number above 3", "off_by_one")],
    difficulty="hard", confidence=0.90,
    expl="The odd numbers are 1, 3 and 5, which is 3 of the 5 sections. The even numbers "
         "are only 2 and 4, giving 2 out of 5; below 3 is 1 and 2, also 2 out of 5; and "
         "above 3 is 4 and 5, again 2 out of 5. Only the odd numbers make three sections.",
    fmt=PLAIN),

B.Q("probability", "single_step",
    "In which of these situations are all the outcomes equally likely?",
    key="rolling one ordinary six-sided dice",
    verify="rolling one ordinary six-sided dice",
    wrong=[("drawing a counter from a bag of 3 red and 7 blue", "misread_data"),
           ("spinning a spinner with one large and two small sections", "wrong_attribute"),
           ("guessing tomorrow's weather from sunny, cloudy or wet", "ignored_constraint")],
    expl="Every face of an ordinary dice has the same chance, so its six outcomes are "
         "equally likely. A bag of 3 red and 7 blue favours blue, and a spinner with "
         "sections of different sizes favours the large one.",
    fmt=PLAIN),

# ===================================================== drawing conclusions (6)

CLUB = table([["", "Yes", "No", "Total"],
              ["Year 5", "22", "18", "40"],
              ["Year 6", "31", "9", "40"],
              ["Total", "53", "27", "80"]])

B.Q("drawing_conclusions", "data_interpretation",
    "The table shows how many students in each year said they would join a chess club. "
    "Which statement does the table support?",
    key="More Year 6 students than Year 5 students said yes",
    verify="More Year 6 students than Year 5 students said yes",
    wrong=[("Year 6 students are better at chess", "misread_data"),
           ("Most students in the school want a chess club", "ignored_constraint"),
           ("Nine Year 6 students dislike chess", "wrong_attribute")],
    difficulty="hard", confidence=0.91,
    expl="31 against 22 is a straight comparison the table makes. Being better at chess is "
         "not something a yes-or-no question measures, and nine Year 6 students said no, "
         "which is not the same as disliking chess — they might simply be busy.",
    fig=CLUB, fmt=PLAIN),

B.Q("drawing_conclusions", "data_interpretation",
    "Using the same chess club table, what would you need before claiming that most "
    "students in the whole school want a chess club?",
    key="answers from the other year groups as well",
    verify="answers from the other year groups as well",
    wrong=[("a larger table", "misread_data"), ("the ages of the students", "wrong_attribute"),
           ("nothing — 53 out of 80 is already most", "ignored_constraint")],
    difficulty="hard", confidence=0.90,
    expl="The table covers Years 5 and 6 only, so it says nothing about the years it did "
         "not ask. 53 out of 80 is indeed most of the students surveyed, but those 80 are "
         "not the whole school.",
    fig=CLUB, fmt=PLAIN),

B.Q("drawing_conclusions", "data_interpretation",
    "A survey asks: 'Do you agree that our school needs a longer lunch break?' Why might "
    "the results be unreliable?",
    key="The wording invites students to agree",
    verify="The wording invites students to agree",
    wrong=[("Not enough students were asked", "misread_data"),
           ("Lunch breaks cannot be measured", "wrong_attribute"),
           ("The question is about school rather than home", "ignored_constraint")],
    expl="Asking whether someone agrees that something is needed pushes them towards yes "
         "before they have thought about it. How many students were asked is a separate "
         "issue and the question does not say, so it cannot be the fault being pointed at "
         "here.",
    fmt=PLAIN),

ICE = bar_chart(["Vanilla", "Choc", "Mango", "Other"], [9, 14, 6, 1])
B.Q("drawing_conclusions", "data_interpretation",
    "The graph shows the favourite ice cream flavour of 30 students. A shop owner says "
    "'nobody likes strawberry'. What is wrong with that?",
    key="Strawberry may be hidden inside the Other column",
    verify="Strawberry may be hidden inside the Other column",
    wrong=[("The graph shows 30 students, not everybody", "partial_step"),
           ("Chocolate is the most popular flavour", "misread_data"),
           ("The columns are not in order of size", "wrong_attribute")],
    difficulty="hard", confidence=0.91,
    expl="Strawberry has no column of its own, but the Other column holds a student whose "
         "flavour is not named, so the graph cannot show that nobody chose it. That the "
         "graph covers only 30 students is true and is a second weakness, but it does not "
         "explain why strawberry in particular cannot be ruled out.",
    fig=ICE, fmt=PLAIN),

B.Q("drawing_conclusions", "data_interpretation",
    "Using the same ice cream graph, which of these can be worked out from it?",
    key="how many more students chose chocolate than mango",
    verify="how many more students chose chocolate than mango",
    wrong=[("how many students dislike vanilla", "misread_data"),
           ("which flavour the shop should stock most of next summer", "ignored_constraint"),
           ("how many students chose two flavours", "wrong_attribute")],
    expl="Chocolate's 14 and mango's 6 are both on the graph, so the difference of 8 comes "
         "straight off it. How many students dislike vanilla was never asked — students "
         "named a favourite, and not choosing something is not the same as disliking it.",
    fig=ICE, fmt=PLAIN),

B.Q("drawing_conclusions", "data_interpretation",
    "A student notices that in the weeks when more ice creams were sold, more people also "
    "went swimming. She concludes that eating ice cream makes people swim. What is the "
    "flaw?",
    key="Hot weather could be raising both on its own",
    verify="Hot weather could be raising both on its own",
    wrong=[("Ice cream sales were not measured accurately", "misread_data"),
           ("Swimming should have been measured in hours", "wrong_attribute"),
           ("Two things rising together can never be connected", "ignored_constraint")],
    difficulty="hard", confidence=0.90,
    expl="Both go up in hot weather, so the heat can explain the pattern without ice cream "
         "causing anything. Two things rising together can never be connected goes too far "
         "the other way: they may well be connected, but this evidence cannot show which "
         "way round, or whether something else drives both.",
    fmt=PLAIN),

# ===================================================== percentages (8)

B.Q("percentages", "single_step",
    "What is 25% of 80?",
    key=80 // 4, verify=80 * 25 // 100,
    wrong=[(25, "misread_data"), (80 // 2, "wrong_attribute"), (80 * 25, "operation_swap")],
    expl="25% is a quarter, and a quarter of 80 is 20. The long way agrees: 80 x 25 / 100 "
         "= 20. 40 takes half rather than a quarter, and 25 gives back the percentage "
         "instead of applying it.",
    fmt=PLAIN),

B.Q("percentages", "multi_step",
    "What is 30% of 240?",
    key=240 * 30 // 100, verify=(240 // 10) * 3,     # a tenth, then three of them
    wrong=[(240 // 10, "partial_step"), (30, "misread_data"), (240 // 3, "wrong_attribute")],
    expl="A tenth of 240 is 24, so 30% is three of those: 72. 24 stops at 10%, and 80 "
         "takes a third rather than 30 hundredths — close, but not the same thing.",
    fmt=PLAIN),

B.Q("percentages", "multi_step",
    "A jacket priced at $45 is reduced by 20% in a sale. What is the sale price?",
    key=45 - 45 * 20 // 100, verify=45 * 80 // 100,  # pay 80% instead of taking 20% off
    wrong=[(45 * 20 // 100, "partial_step"), (45 + 45 * 20 // 100, "inverse"),
           (45 - 20, "misread_data")],
    difficulty="hard", confidence=0.91,
    expl="20% of $45 is $9, so the sale price is $45 - $9 = $36. Paying 80% straight out "
         "gives the same: 45 x 80 / 100 = 36. $9 is the discount rather than the price, "
         "and $25 takes $20 off instead of 20 per cent.",
    fmt=money),

B.Q("percentages", "multi_step",
    "A school of 300 students grows by 15%. How many students does it have now?",
    key=300 + 300 * 15 // 100, verify=300 * 115 // 100,
    wrong=[(300 * 15 // 100, "partial_step"), (300 - 300 * 15 // 100, "inverse"),
           (315, "misread_data")],
    difficulty="hard", confidence=0.91,
    expl="15% of 300 is 45, so the school now has 300 + 45 = 345 students. Working at 115% "
         "in one step gives the same. 45 is the growth rather than the new size, and 315 "
         "adds 15 students instead of 15 per cent.",
    fmt=unit("students")),

B.Q("percentages", "multi_step",
    "In a class of 25 students, 15 walk to school. What percentage walk?",
    key=15 * 100 // 25, verify=int(15 / 25 * 100),
    wrong=[(15, "misread_data"), (25 - 15, "inverse"), (15 * 100 // (25 - 15), "wrong_attribute")],
    difficulty="hard", confidence=0.90,
    expl="15 out of 25 is the same as 60 out of 100, so 60%. A quick check: a quarter of "
         "the class is about 6 students and 15 is well over half, which 60% is. 15 gives "
         "the number of students rather than a percentage, and 10 counts the ones who do "
         "not walk.",
    fmt=pct),

B.Q("percentages", "multi_step",
    "30% of a number is 18. What is the number?",
    key=18 * 100 // 30, verify=next(n for n in range(1, 200) if n * 30 // 100 == 18),
    wrong=[(18 * 30 / 100, "inverse"), (18 + 30, "operation_swap"), (18 * 3, "off_by_one")],
    difficulty="hard", confidence=0.90,
    expl="If 30% is 18 then 10% is 6, and 100% is ten lots of that: 60. Check it: 30% of "
         "60 is 18. 54 multiplies 18 by 3 as though 30% were a third, and 5.4 takes 30% of "
         "18 rather than working back to the whole.",
    fmt=PLAIN),

B.Q("percentages", "multi_step",
    "Which is the largest share: 1/4, 20% or 3 out of 10?",
    key="3 out of 10", verify="3 out of 10",     # 30% against 25% and 20%
    wrong=[("1/4", "misread_data"), ("20%", "inverse"), ("they are all equal", "ignored_constraint")],
    difficulty="hard", confidence=0.91,
    expl="Put them all in hundredths: 1/4 is 25%, 20% is 20%, and 3 out of 10 is 30%. So "
         "3 out of 10 is the largest. 1/4 looks small written as a fraction but is bigger "
         "than 20%, and 20% is the smallest of the three.",
    fmt=PLAIN),

B.Q("percentages", "multi_step",
    "A test is marked out of 40 and a student scores 34. What percentage did she score?",
    key=34 * 100 // 40, verify=int(34 / 40 * 100),
    wrong=[(34, "misread_data"), (40 - 34, "inverse"), (34 * 100 // 34, "wrong_attribute")],
    difficulty="hard", confidence=0.90,
    expl="Each mark out of 40 is worth 2.5%, so 34 marks are 34 x 2.5 = 85%. Another way: "
         "34 / 40 = 0.85. 34 gives the mark rather than the percentage, and 6 counts the "
         "marks she lost.",
    fmt=pct),

# ===================================================== ratio and proportion (8)

B.Q("ratio_proportion", "single_step",
    "Write the ratio 12 : 18 in its simplest form.",
    key="2 : 3", verify=f"{12 // 6} : {18 // 6}",
    wrong=[("4 : 6", "partial_step"), ("3 : 2", "inverse"), ("6 : 9", "off_by_one")],
    expl="Both numbers divide by 6: 12 / 6 = 2 and 18 / 6 = 3, giving 2 : 3. 4 : 6 divides "
         "by 3 only and can be simplified further, and 3 : 2 turns the ratio round.",
    fmt=PLAIN),

B.Q("ratio_proportion", "multi_step",
    "$40 is shared between two students in the ratio 3 : 5. How much does the student with "
    "the larger share receive?",
    key=40 * 5 // 8, verify=40 - 40 * 3 // 8,   # the rest, once the smaller share is taken
    wrong=[(40 * 3 // 8, "inverse"), (40 // 2, "misread_data"), (5, "partial_step")],
    difficulty="hard", confidence=0.91,
    expl="The $40 splits into 3 + 5 = 8 parts, so each part is $5 and the larger share is "
         "5 parts: $25. Check it: $15 and $25 add back to $40. $15 gives the smaller share "
         "and $20 splits the money evenly, which the ratio does not.",
    fmt=money),

B.Q("ratio_proportion", "multi_step",
    "A recipe uses 2 cups of flour for every 3 people. How many cups are needed for 12 "
    "people?",
    key=2 * (12 // 3), verify=12 // 3 * 2,
    wrong=[(12 // 3, "partial_step"), (2 * 12, "ignored_constraint"), (12 // 2 * 3, "inverse")],
    expl="12 people is four lots of 3, so the flour is four lots of 2 cups: 8 cups. 4 gives "
         "how many lots there are rather than how many cups, 24 uses 2 cups per person "
         "instead of per three people, and 18 turns the recipe round to 3 cups for every "
         "2 people.",
    fmt=unit("cups")),

B.Q("ratio_proportion", "multi_step",
    "Five identical pens cost $7.50. What does one pen cost?",
    key=7.50 / 5, verify=750 // 5 / 100,        # in cents, then back to dollars
    wrong=[(7.50 * 5, "inverse"), (7.50 - 5, "operation_swap"), (7.50 / 5 / 10, "place_value")],
    expl="Divide by 5: $7.50 / 5 = $1.50 a pen. Check it: 5 x $1.50 = $7.50. $37.50 "
         "multiplies instead of dividing, which would be the cost of 25 pens.",
    fmt=money),

B.Q("ratio_proportion", "multi_step",
    "A 500 g box of cereal costs $4 and a 1.5 kg box costs $10.50. Which is better value, "
    "and by how much per kilogram?",
    key="the 1.5 kg box, by $1 per kilogram", verify="the 1.5 kg box, by $1 per kilogram",
    wrong=[("the 500 g box, by $1 per kilogram", "inverse"),
           ("the 1.5 kg box, by $6.50 per kilogram", "misread_data"),
           ("they cost the same per kilogram", "off_by_one")],
    difficulty="hard", confidence=0.90,
    expl="The 500 g box works out at $8 a kilogram, since half a kilogram costs $4. The "
         "1.5 kg box is $10.50 / 1.5 = $7 a kilogram. So the big box is better by $1 a "
         "kilogram. $6.50 is simply the difference between the two prices, which compares "
         "boxes of different sizes.",
    fmt=PLAIN),

B.Q("ratio_proportion", "multi_step",
    "Paint is mixed with white and blue in the ratio 4 : 1. How much white is needed to "
    "make 20 litres of the mixture?",
    key=20 * 4 // 5, verify=20 - 20 * 1 // 5,
    wrong=[(20 * 1 // 5, "inverse"), (20 // 4, "misread_data"), (20, "ignored_constraint")],
    difficulty="hard", confidence=0.91,
    expl="The mixture is 4 + 1 = 5 parts and 20 litres makes each part 4 litres, so the "
         "white is 4 parts: 16 litres. Check it: 16 white and 4 blue make 20. 4 gives the "
         "blue rather than the white, and 20 gives the whole mixture rather than the white "
         "part of it.",
    fmt=unit("L")),

B.Q("ratio_proportion", "multi_step",
    "In a choir the ratio of boys to girls is 2 : 3. What fraction of the choir are boys?",
    key=frac(2, 5), verify=frac(2, 2 + 3),
    wrong=[(frac(2, 3), "misread_data"), (frac(3, 5), "inverse"), (frac(1, 2), "off_by_one")],
    difficulty="hard", confidence=0.91,
    expl="Two parts boys and three parts girls make five parts in all, so boys are 2 out "
         "of 5 of the choir. 2 out of 3 uses the ratio itself as a fraction, which "
         "compares boys with girls rather than with everybody.",
    fmt=PLAIN),

B.Q("ratio_proportion", "multi_step",
    "The ratio 4 : 6 is equal to the ratio 10 : ?. What number belongs in place of the "
    "question mark?",
    key=6 * 10 // 4, verify=next(n for n in range(1, 60) if 4 * n == 6 * 10),
    wrong=[(10 + 2, "operation_swap"), (6, "partial_step"), (10 * 6, "ignored_constraint")],
    difficulty="hard", confidence=0.90,
    expl="4 : 6 simplifies to 2 : 3, so the second number is always one and a half times "
         "the first: 10 x 1.5 = 15. Check it: 4 x 15 = 60 and 6 x 10 = 60, which is what "
         "equal ratios do. 12 adds 2 as though the gap stayed the same rather than the "
         "scale.",
    fmt=PLAIN),

# ===================================================== order of operations (2)

# `expect` is the answer worked out by hand from the printed expression; `key` is what
# Python's own parser makes of that same printed text. If my grouping and the notation
# disagree, the build stops — writing eval() on both sides would only have agreed with
# itself.
for stem_expr, expect, wrongs, expl, diff in [
    ("5 + 3 x 4", 17,
     [("(5 + 3) x 4", "operation_swap"), ("5 + 3 + 4", "misread_data"), ("5 x 3 + 4", "wrong_attribute")],
     "Multiplication comes before addition, so 3 x 4 = 12 first, then 5 + 12 = 17. 32 "
     "works left to right, adding 5 and 3 before multiplying, and 19 multiplies the wrong "
     "pair.", "medium"),
    ("(12 - 4) / 2 + 6", 10,
     [("12 - 4 / 2 + 6", "misread_data"), ("(12 - 4) / (2 + 6)", "operation_swap"),
      ("12 - (4 / 2 + 6)", "wrong_attribute")],
     "Brackets first: 12 - 4 = 8. Then divide before adding: 8 / 2 = 4, and 4 + 6 = 10. 16 "
     "ignores the brackets and divides only the 4, and 1 divides by the whole of 2 + 6 as "
     "though there were brackets there too.", "hard"),
]:
    B.Q("order_of_operations", "single_step" if diff == "medium" else "multi_step",
        f"What is the value of {stem_expr}?",
        # Grouped by hand above, and evaluated here by Python's own parser from the
        # expression exactly as the stem prints it.
        key=eval(stem_expr.replace("x", "*")), verify=expect,
        wrong=[(eval(w.replace("x", "*")), cls) for w, cls in wrongs],
        difficulty=diff, confidence=0.92 if diff == "medium" else 0.90,
        expl=expl, fmt=PLAIN)

if __name__ == "__main__":
    B.write()
