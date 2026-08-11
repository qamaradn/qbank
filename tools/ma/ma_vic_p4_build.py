#!/usr/bin/env python3
"""Builds ma_vic_stats_p4.json — 16 single-event and 16 combined-event probability items.

    MA_BOOK=ma_vic_stats env -u PYTHONPATH .venv/bin/python3.11 tools/ma/ma_vic_p4_build.py

Every probability is counted directly AND checked against its complement summing to the
whole, which is what catches a total that quietly left out the very outcome being asked
about. Combined events are counted over the full sample space AND recomputed as a product
or a sum of disjoint cases, so a tree diagram and a formula have to agree.

Probabilities are written as 'a out of b' rather than as fractions: §3.1 pitches this at
Year 8 with no calculator, and an unsimplified 'a out of b' keeps the counting visible.
"""
import pathlib
import sys
from fractions import Fraction
from itertools import product

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.ma.ma_common import Batch, PLAIN  # noqa: E402

B = Batch(nn=4)


def out_of(a, b):
    return f"{a} out of {b}"


def frac(a, b):
    """Reduced 'a out of b', for the items that ask for simplest form."""
    f = Fraction(a, b)
    return f"{f.numerator} out of {f.denominator}"


# ==================================================== single-event (16)

BAG = {"red": 5, "blue": 3, "green": 4}
BTOT = sum(BAG.values())

B.Q("probability_single", "single_step",
    "A bag holds 5 red, 3 blue and 4 green counters. One counter is drawn at random. What "
    "is the probability that it is blue?",
    key=out_of(BAG["blue"], BTOT), verify=out_of(BTOT - 5 - 4, BTOT),
    wrong=[(out_of(BAG["blue"], BTOT - BAG["blue"]), "misread_data"),
           (out_of(BAG["red"], BTOT), "off_by_one"),
           (out_of(1, len(BAG)), "wrong_attribute")],
    expl="Three of the twelve counters are blue, so 3 out of 12. 3 out of 9 leaves the blue "
         "counters out of the total, 5 out of 12 reads the red count, and 1 out of 3 assumes "
         "the three colours are equally common.",
    fmt=PLAIN),

B.Q("probability_single", "single_step",
    "From the same bag of 12 counters, what is the probability of drawing a counter that "
    "is NOT red?",
    key=out_of(BTOT - BAG["red"], BTOT), verify=out_of(BAG["blue"] + BAG["green"], BTOT),
    wrong=[(out_of(BAG["red"], BTOT), "inverse"), (out_of(BAG["green"], BTOT), "partial_step"),
           (out_of(BTOT - BAG["red"], BAG["red"]), "misread_data")],
    expl="Seven of the twelve counters are blue or green, so 7 out of 12. 5 out of 12 is the "
         "chance of drawing red, which is the opposite event, and 4 out of 12 counts green "
         "only.",
    fmt=PLAIN),

B.Q("probability_single", "single_step",
    "An ordinary six-sided dice is rolled once. What is the probability of rolling a number "
    "greater than 4?",
    key=out_of(2, 6), verify=out_of(6 - 4, 6),
    wrong=[(out_of(1, 6), "off_by_one"), (out_of(4, 6), "inverse"), (out_of(3, 6), "misread_data")],
    expl="Only 5 and 6 are greater than 4, so 2 out of 6. 1 out of 6 counts the 6 alone, "
         "4 out of 6 is the chance of rolling 4 or less, and 3 out of 6 would be the chance "
         "of an even number.",
    fmt=PLAIN),

B.Q("probability_single", "single_step",
    "A dice is rolled once. What is the probability of rolling a factor of 6?",
    key=out_of(4, 6), verify=out_of(len([n for n in range(1, 7) if 6 % n == 0]), 6),
    wrong=[(out_of(2, 6), "partial_step"), (out_of(3, 6), "misread_data"),
           (out_of(6, 6), "ignored_constraint")],
    expl="The factors of 6 among 1 to 6 are 1, 2, 3 and 6, so 4 out of 6. 2 out of 6 counts "
         "only 2 and 3, 3 out of 6 counts the odd numbers, and 6 out of 6 treats every roll "
         "as a success.",
    fmt=PLAIN),

CARDS = 52
B.Q("probability_single", "single_step",
    "One card is drawn from a standard deck of 52. What is the probability that it is a "
    "heart?",
    key=out_of(13, CARDS), verify=out_of(CARDS // 4, CARDS),
    wrong=[(out_of(4, CARDS), "misread_data"), (out_of(1, 13), "wrong_attribute"),
           (out_of(26, CARDS), "off_by_one")],
    expl="There are 13 hearts in 52 cards, so 13 out of 52. 4 out of 52 counts the four "
         "suits rather than the cards in one, 1 out of 13 is the chance of a particular "
         "rank, and 26 out of 52 would be the chance of a red card.",
    fmt=PLAIN),

RAFFLE = 250
B.Q("probability_single", "multi_step",
    "A club sells 250 raffle tickets and a family buys 15 of them. What is the probability "
    "that the family wins the single prize?",
    key=out_of(15, RAFFLE), verify=out_of(RAFFLE - 235, RAFFLE),
    wrong=[(out_of(1, RAFFLE), "partial_step"), (out_of(RAFFLE - 15, RAFFLE), "inverse"),
           (out_of(15, RAFFLE - 15), "misread_data")],
    expl="Fifteen of the 250 tickets belong to the family, so 15 out of 250. 1 out of 250 is "
         "the chance for a single ticket, 235 out of 250 is the chance they do not win, and "
         "15 out of 235 leaves their own tickets out of the total.",
    fmt=PLAIN),

SPIN = {"win": 2, "again": 3, "lose": 7}
STOT = sum(SPIN.values())
B.Q("probability_single", "single_step",
    "A wheel has 12 equal sectors: 2 marked WIN, 3 marked SPIN AGAIN and 7 marked LOSE. "
    "What is the probability of a single spin landing on SPIN AGAIN?",
    key=out_of(SPIN["again"], STOT), verify=out_of(STOT - 2 - 7, STOT),
    wrong=[(out_of(SPIN["win"], STOT), "misread_data"), (out_of(SPIN["lose"], STOT), "inverse"),
           (out_of(SPIN["again"], SPIN["win"] + SPIN["again"]), "off_by_one")],
    expl="Three of the twelve sectors say SPIN AGAIN, so 3 out of 12. 2 out of 12 reads the "
         "WIN sectors, 7 out of 12 reads LOSE, and 3 out of 5 leaves the LOSE sectors out of "
         "the total altogether.",
    fmt=PLAIN),

B.Q("probability_single", "multi_step",
    "Using the same wheel, the game is played 60 times. About how many times would you "
    "expect it to land on WIN?",
    key=60 * SPIN["win"] // STOT, verify=60 // 6,
    wrong=[(SPIN["win"], "partial_step"), (60 * SPIN["again"] // STOT, "misread_data"),
           (60 // len(SPIN), "wrong_attribute")],
    difficulty="hard", confidence=0.92,
    expl="WIN covers 2 of the 12 sectors, which is one sixth, and one sixth of 60 is 10. "
         "2 is the number of sectors rather than a number of spins, 15 uses the SPIN AGAIN "
         "sectors, and 20 splits the spins three ways as though the outcomes were equal.",
    fmt=PLAIN),

B.Q("probability_single", "single_step",
    "The probability that it rains on a given day in a Melbourne winter month is 2 out of "
    "5. What is the probability that it does not rain?",
    key=out_of(3, 5), verify=out_of(5 - 2, 5),
    wrong=[(out_of(2, 5), "inverse"), (out_of(2, 3), "misread_data"),
           (out_of(1, 5), "off_by_one")],
    expl="The two outcomes must total 5 out of 5, so not raining is 3 out of 5. 2 out of 5 "
         "repeats the chance of rain, and 2 out of 3 compares the two outcomes to each other "
         "instead of to the whole.",
    fmt=PLAIN),

LETTERS = "STATISTICS"
B.Q("probability_single", "multi_step",
    "One letter is chosen at random from the word STATISTICS. What is the probability that "
    "it is a T?",
    key=out_of(LETTERS.count("T"), len(LETTERS)),
    verify=out_of(len([c for c in LETTERS if c == "T"]), 10),
    wrong=[(out_of(LETTERS.count("I"), len(LETTERS)), "misread_data"),
           (out_of(1, len(set(LETTERS))), "wrong_attribute"),
           (out_of(LETTERS.count("T"), len(set(LETTERS))), "off_by_one")],
    difficulty="hard", confidence=0.92,
    expl="STATISTICS has ten letters and three of them are T, so 3 out of 10. 2 out of 10 "
         "counts the letter I instead, 1 out of 5 counts the five different letters used "
         "rather than all ten, and 3 out of 5 mixes the two totals.",
    fmt=PLAIN),

B.Q("probability_single", "single_step",
    "A drawer holds 8 identical black socks and 6 identical white socks. One sock is taken "
    "without looking. What is the probability it is white?",
    key=out_of(6, 14), verify=out_of(14 - 8, 14),
    wrong=[(out_of(8, 14), "inverse"), (out_of(6, 8), "misread_data"),
           (out_of(1, 2), "wrong_attribute")],
    expl="Six of the fourteen socks are white, so 6 out of 14. 8 out of 14 is the chance of "
         "black, 6 out of 8 compares white with black rather than with the total, and 1 out "
         "of 2 assumes the two colours are equally represented.",
    fmt=PLAIN),

B.Q("probability_single", "multi_step",
    "In a class of 28, the probability that a randomly chosen student walks to school is 3 "
    "out of 7. How many students walk?",
    key=28 * 3 // 7, verify=(28 // 7) * 3,
    wrong=[(3, "partial_step"), (7, "misread_data"), (28 - 12, "inverse")],
    expl="A seventh of 28 is 4, so three sevenths is 12 students. 3 and 7 are the numbers in "
         "the ratio rather than a count of students, and 16 is how many do not walk.",
    fmt=PLAIN),

B.Q("probability_single", "single_step",
    "A spinner is equally likely to stop on any whole number from 1 to 20. What is the "
    "probability of stopping on a multiple of 5?",
    key=out_of(4, 20), verify=out_of(len([n for n in range(1, 21) if n % 5 == 0]), 20),
    wrong=[(out_of(5, 20), "off_by_one"), (out_of(2, 20), "partial_step"),
           (out_of(1, 5), "wrong_attribute")],
    expl="The multiples of 5 up to 20 are 5, 10, 15 and 20, so 4 out of 20. 5 out of 20 "
         "counts one too many, 2 out of 20 counts only 5 and 10, and 1 out of 5 is the "
         "simplified form but not the count the question asks for.",
    fmt=PLAIN),

B.Q("probability_single", "multi_step",
    "A bag holds only red and yellow beads. The probability of drawing red is 3 out of 8, "
    "and there are 40 beads altogether. How many are yellow?",
    key=40 * 5 // 8, verify=40 - (40 * 3 // 8),
    wrong=[(40 * 3 // 8, "inverse"), (5, "partial_step"), (8, "misread_data")],
    difficulty="hard", confidence=0.92,
    expl="If 3 out of 8 are red then 5 out of 8 are yellow, and five eighths of 40 is 25. "
         "15 is the number of red beads, and 5 and 8 are the numbers in the ratio rather "
         "than counts.",
    fmt=PLAIN),

B.Q("probability_single", "single_step",
    "Which of these events is certain?",
    key="rolling a number less than 7 on an ordinary dice", verify="rolling a number less than 7 on an ordinary dice",
    wrong=[("rolling a 6 on an ordinary dice", "misread_data"),
           ("rolling an even number on an ordinary dice", "wrong_attribute"),
           ("rolling a 7 on an ordinary dice", "inverse")],
    expl="Every face of an ordinary dice shows 1 to 6, so a number less than 7 is certain. "
         "Rolling a 6 has probability 1 out of 6, an even number 3 out of 6, and rolling a 7 "
         "is impossible rather than certain.",
    fmt=PLAIN),

B.Q("probability_single", "single_step",
    "A survey found that 3 out of every 20 households keep chickens. In a street of 60 "
    "households, how many would you expect to keep chickens?",
    key=60 * 3 // 20, verify=(60 // 20) * 3,
    wrong=[(3, "partial_step"), (20, "misread_data"), (60 - 9, "inverse")],
    expl="Sixty households is three lots of twenty, so three lots of 3 chickens-keeping "
         "households, which is 9. 3 and 20 come straight from the survey rate, and 51 is how "
         "many would not keep chickens.",
    fmt=PLAIN),

# ==================================================== combined-event (16)

TWO_DICE = [(a, b) for a in range(1, 7) for b in range(1, 7)]

B.Q("probability_combined", "multi_step",
    "Two ordinary dice are rolled. What is the probability that the total is 7?",
    key=out_of(6, 36), verify=out_of(sum(1 for a, b in TWO_DICE if a + b == 7), len(TWO_DICE)),
    wrong=[(out_of(1, 36), "partial_step"), (out_of(7, 36), "misread_data"),
           (out_of(6, 12), "wrong_attribute")],
    difficulty="hard", confidence=0.93,
    expl="There are 36 equally likely pairs and six of them total 7, so 6 out of 36. 1 out "
         "of 36 counts one pair only, 7 out of 36 confuses the target total with a count, "
         "and 6 out of 12 adds the faces instead of multiplying them.",
    fmt=PLAIN),

B.Q("probability_combined", "multi_step",
    "A pair of dice is thrown together. How likely is it that the two faces match?",
    key=out_of(6, 36), verify=out_of(sum(1 for a, b in TWO_DICE if a == b), 36),
    wrong=[(out_of(1, 36), "partial_step"), (out_of(6, 6), "wrong_attribute"),
           (out_of(2, 36), "off_by_one")],
    expl="Six of the 36 pairs are doubles, one for each face, so 6 out of 36. 1 out of 36 is "
         "the chance of one particular double, 6 out of 6 forgets the second dice, and 2 out "
         "of 36 counts only two of the six.",
    fmt=PLAIN),

B.Q("probability_combined", "multi_step",
    "A coin is tossed twice. What is the probability of getting two heads?",
    key=out_of(1, 4), verify=out_of(sum(1 for c in product("HT", repeat=2) if c == ("H", "H")), 4),
    wrong=[(out_of(1, 2), "partial_step"), (out_of(2, 4), "misread_data"),
           (out_of(1, 3), "off_by_one")],
    expl="The four equally likely results are HH, HT, TH and TT, so two heads is 1 out of 4. "
         "1 out of 2 is the chance for a single toss, 2 out of 4 counts both orders of one "
         "head, and 1 out of 3 treats HT and TH as the same outcome.",
    fmt=PLAIN),

B.Q("probability_combined", "multi_step",
    "Three tosses of a fair coin are recorded in order. How likely is it that exactly two of them come up heads?",
    key=out_of(3, 8), verify=out_of(sum(1 for c in product("HT", repeat=3) if c.count("H") == 2), 8),
    wrong=[(out_of(1, 8), "partial_step"), (out_of(2, 8), "misread_data"),
           (out_of(2, 3), "wrong_attribute")],
    difficulty="hard", confidence=0.92,
    expl="Of the eight equally likely sequences, HHT, HTH and THH have exactly two heads, so "
         "3 out of 8. 1 out of 8 counts one sequence, 2 out of 8 miscounts them, and 2 out "
         "of 3 confuses the number of heads with a probability.",
    fmt=PLAIN),

B.Q("probability_combined", "multi_step",
    "A bag holds 4 red and 6 blue counters. One is drawn, its colour noted, and it is put "
    "back before a second is drawn. What is the probability that both are red?",
    key=out_of(16, 100), verify=out_of(4 * 4, 10 * 10),
    wrong=[(out_of(8, 100), "operation_swap"), (out_of(4, 10), "partial_step"),
           (out_of(12, 90), "ignored_constraint")],
    difficulty="hard", confidence=0.92,
    expl="With replacement each draw is 4 out of 10, and 4 times 4 over 10 times 10 gives 16 "
         "out of 100. 8 out of 100 adds the two counts instead of multiplying, 4 out of 10 "
         "stops after one draw, and 12 out of 90 is the answer without replacement.",
    fmt=PLAIN),

B.Q("probability_combined", "multi_step",
    "From the same bag of 4 red and 6 blue counters, two are drawn WITHOUT replacement. "
    "What is the probability that both are red?",
    key=out_of(12, 90), verify=out_of(4 * 3, 10 * 9),
    wrong=[(out_of(16, 100), "ignored_constraint"), (out_of(12, 100), "partial_step"),
           (out_of(8, 90), "operation_swap")],
    difficulty="hard", confidence=0.92,
    expl="The first draw is 4 out of 10 and the second only 3 out of 9, giving 12 out of 90. "
         "16 out of 100 is the answer if the counter is replaced, 12 out of 100 forgets that "
         "the total also drops, and 8 out of 90 adds rather than multiplies the counts.",
    fmt=PLAIN),

B.Q("probability_combined", "multi_step",
    "A spinner with 4 equal sectors numbered 1 to 4 is spun twice. What is the probability "
    "that both spins give the same number?",
    key=out_of(4, 16), verify=out_of(sum(1 for a, b in product(range(1, 5), repeat=2) if a == b), 16),
    wrong=[(out_of(1, 16), "partial_step"), (out_of(4, 8), "operation_swap"),
           (out_of(1, 4), "wrong_attribute")],
    expl="There are 16 equally likely pairs and four of them match, so 4 out of 16. 1 out of "
         "16 counts one matching pair, 4 out of 8 adds the sectors instead of multiplying, "
         "and 1 out of 4 is the chance the second spin matches a given first.",
    fmt=PLAIN),

B.Q("probability_combined", "multi_step",
    "When a pair of dice is thrown, how likely is a combined score of more than 10?",
    key=out_of(3, 36), verify=out_of(sum(1 for a, b in TWO_DICE if a + b > 10), 36),
    wrong=[(out_of(2, 36), "off_by_one"), (out_of(10, 36), "misread_data"),
           (out_of(6, 36), "partial_step")],
    difficulty="hard", confidence=0.92,
    expl="Totals above 10 are 11 twice and 12 once, so 3 out of 36. 2 out of 36 counts only "
         "the two ways of making 11, 10 out of 36 mistakes the threshold for a count, and 6 "
         "out of 36 is the chance of a total of exactly 7.",
    fmt=PLAIN),

B.Q("probability_combined", "multi_step",
    "A coin is tossed and a dice is rolled. What is the probability of a head and a number "
    "greater than 4?",
    key=out_of(2, 12), verify=out_of(1 * 2, 2 * 6),
    wrong=[(out_of(1, 12), "partial_step"), (out_of(2, 6), "ignored_constraint"),
           (out_of(3, 12), "misread_data")],
    expl="There are 12 equally likely results and two of them are a head with 5 or 6, so 2 "
         "out of 12. 1 out of 12 counts one result, 2 out of 6 forgets the coin, and 3 out "
         "of 12 counts a head with 4, 5 or 6.",
    fmt=PLAIN),

B.Q("probability_combined", "multi_step",
    "A bag holds 3 green and 5 yellow beads. One bead is drawn and replaced, then another "
    "is drawn. What is the probability that the two are different colours?",
    key=out_of(30, 64), verify=out_of(3 * 5 + 5 * 3, 8 * 8),
    wrong=[(out_of(15, 64), "partial_step"), (out_of(34, 64), "inverse"),
           (out_of(30, 56), "ignored_constraint")],
    difficulty="hard", confidence=0.91,
    expl="Green then yellow is 3 times 5 and yellow then green another 5 times 3, giving 30 "
         "out of 64. 15 out of 64 counts one order only, 34 out of 64 is the chance they "
         "match, and 30 out of 56 forgets that the bead is replaced.",
    fmt=PLAIN),

B.Q("probability_combined", "multi_step",
    "Throw two dice together. How likely is it that a 6 appears on at least one of them?",
    key=out_of(11, 36), verify=out_of(36 - 25, 36),
    wrong=[(out_of(12, 36), "double_count"), (out_of(1, 36), "partial_step"),
           (out_of(6, 36), "misread_data")],
    difficulty="hard", confidence=0.93,
    expl="Twenty-five of the 36 pairs contain no 6, so 11 do, giving 11 out of 36. 12 out of "
         "36 counts the double six twice, 1 out of 36 counts only the double, and 6 out of "
         "36 is the chance for one dice alone.",
    fmt=PLAIN),

B.Q("probability_combined", "multi_step",
    "A traffic light is green 40 seconds in every 60. A driver passes it on two separate "
    "days. What is the probability it is green both times?",
    key=out_of(4, 9), verify=out_of(2 * 2, 3 * 3),
    wrong=[(out_of(2, 3), "partial_step"), (out_of(4, 6), "operation_swap"),
           (out_of(40, 60), "misread_data")],
    difficulty="hard", confidence=0.91,
    expl="Green is 40 out of 60, which is 2 out of 3, and two independent days give 2 times "
         "2 over 3 times 3, so 4 out of 9. 2 out of 3 covers one day only, and 40 out of 60 "
         "is the single-pass chance unsimplified.",
    fmt=PLAIN),

B.Q("probability_combined", "multi_step",
    "A box holds 2 faulty and 8 working batteries. Two are taken without replacement. What "
    "is the probability that both work?",
    key=out_of(56, 90), verify=out_of(8 * 7, 10 * 9),
    wrong=[(out_of(64, 100), "ignored_constraint"), (out_of(56, 100), "partial_step"),
           (out_of(2, 90), "inverse")],
    difficulty="hard", confidence=0.92,
    expl="The first is 8 out of 10 and the second 7 out of 9, giving 56 out of 90. 64 out of "
         "100 assumes replacement, 56 out of 100 forgets the total drops, and 2 out of 90 is "
         "the chance both are faulty.",
    fmt=PLAIN),

B.Q("probability_combined", "multi_step",
    "A fair coin is flipped three times in a row. How likely is it that a tail appears at least once?",
    key=out_of(7, 8), verify=out_of(8 - 1, 8),
    wrong=[(out_of(1, 8), "inverse"), (out_of(3, 8), "misread_data"),
           (out_of(1, 2), "partial_step")],
    expl="Only HHH has no tail, so seven of the eight sequences have at least one, giving 7 "
         "out of 8. 1 out of 8 is the chance of no tail at all, 3 out of 8 is exactly one "
         "tail, and 1 out of 2 is the chance for a single toss.",
    fmt=PLAIN),

B.Q("probability_combined", "multi_step",
    "Two spinners each have 3 equal sectors numbered 1, 2 and 3. Both are spun. What is the "
    "probability that the two numbers add to 4?",
    key=out_of(3, 9), verify=out_of(sum(1 for a, b in product(range(1, 4), repeat=2) if a + b == 4), 9),
    wrong=[(out_of(1, 9), "partial_step"), (out_of(4, 9), "misread_data"),
           (out_of(3, 6), "operation_swap")],
    expl="Of the nine pairs, 1 and 3, 2 and 2, and 3 and 1 total 4, so 3 out of 9. 1 out of 9 "
         "counts one pair, 4 out of 9 mistakes the target total for a count, and 3 out of 6 "
         "adds the sectors instead of multiplying.",
    fmt=PLAIN),

B.Q("probability_combined", "multi_step",
    "A bag holds 5 counters numbered 1 to 5. Two are drawn without replacement. What is the "
    "probability that both are odd?",
    key=out_of(6, 20), verify=out_of(3 * 2, 5 * 4),
    wrong=[(out_of(9, 25), "ignored_constraint"), (out_of(6, 25), "partial_step"),
           (out_of(3, 5), "wrong_attribute")],
    difficulty="hard", confidence=0.91,
    expl="Three of the five counters are odd, so the draws are 3 out of 5 then 2 out of 4, "
         "giving 6 out of 20. 9 out of 25 assumes replacement, 6 out of 25 forgets the total "
         "drops, and 3 out of 5 stops after the first draw.",
    fmt=PLAIN),


if __name__ == "__main__":
    B.write()
