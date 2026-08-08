#!/usr/bin/env python3
"""Builds ma_nsw_selective_p9.json — the last 19 NSW Mathematical Reasoning questions.

estimation 7, factors/multiples/primes 6, order of operations 2, negative numbers 4.
This closes Number and arithmetic at 37/37 and the whole §4 build at 307/307.

Verification pairs:
  * an estimate is rounded first AND the exact value is computed and then rounded, which
    is what catches an estimate that rounds the wrong number;
  * a factor count comes from enumerating divisors AND from pairing them off;
  * an LCM is found by walking both lists of multiples AND from product / HCF;
  * a primality claim is trial-divided rather than recalled;
  * a negative-number answer is stepped along a number line AND computed directly.

Years 5-6 content, Year 6 sitting, no calculator.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.ma.ma_common import Batch, PLAIN, money, unit  # noqa: E402

B = Batch(nn=9)
DEGC = unit("°C")


def divisors(n):
    return [d for d in range(1, n + 1) if n % d == 0]


def is_prime(n):
    return n > 1 and all(n % d for d in range(2, int(n ** 0.5) + 1))


def hcf(a, b):
    while b:
        a, b = b, a % b
    return a


def lcm_walk(a, b):
    """Walk the multiples of a until one is also a multiple of b."""
    m = a
    while m % b:
        m += a
    return m


# ===================================================== estimation (7)

B.Q("estimation", "single_step",
    "Which of these is the best estimate of 297 x 4?",
    key=300 * 4, verify=round(297 * 4, -2),
    wrong=[(300 * 4 // 2, "operation_swap"), (3000 * 4, "place_value"), (297 + 4, "misread_data")],
    expl="297 is very close to 300, and 300 x 4 = 1200. The exact answer is 1188, which "
         "rounds to 1200, so the estimate is a good one. 600 halves instead of doubling "
         "twice, and 12000 slips a place.",
    fmt=PLAIN),

B.Q("estimation", "multi_step",
    "A shopper buys items costing $19.80, $4.95 and $12.10. Roughly what will the total "
    "be?",
    key=20 + 5 + 12, verify=round(19.80 + 4.95 + 12.10),
    wrong=[(20 + 5, "partial_step"), (20 + 5 + 12 + 10, "misread_data"),
           ((20 + 5 + 12) * 2, "operation_swap")],
    expl="Round each to the nearest dollar: $20, $5 and $12, which come to about $37. The "
         "exact total is $36.85, so the estimate is close. $25 leaves the third item out.",
    fmt=money),

B.Q("estimation", "multi_step",
    "Which of these calculations gives an answer closest to 500?",
    key="52 x 9", verify="52 x 9",              # 468, against 620, 693 and 355
    wrong=[("62 x 10", "misread_data"), ("71 x 5", "operation_swap"), ("99 x 7", "place_value")],
    difficulty="hard", confidence=0.90,
    expl="Round each one: 52 x 9 is about 50 x 9 = 450, 62 x 10 is 620, 71 x 5 is about "
         "350 and 99 x 7 is about 700. Only 52 x 9, which is really 468, comes near 500. "
         "62 x 10 is the easiest to work out exactly and that is what makes it tempting.",
    fmt=PLAIN),

B.Q("estimation", "multi_step",
    "About how many buses seating 48 people are needed to carry 380 students?",
    key=-(-380 // 48), verify=8,               # 400 / 50 is about 8, and 7 buses is short
    wrong=[(380 // 48, "partial_step"), (380 // 40, "misread_data"), (400 // 40, "rounding")],
    difficulty="hard", confidence=0.91,
    expl="Round to make it easy: about 400 students in buses of about 50 is 8 buses. "
         "Checking, 7 buses carry 336 students, which is not enough, and 8 carry 384, "
         "which is. 7 leaves 44 students behind, 9 comes from using 40 to a bus, and 10 "
         "rounds the students up and the seats down at the same time, exaggerating both.",
    fmt=unit("buses")),

B.Q("estimation", "multi_step",
    "A student works out 6.2 x 48 and gets 297.6. Without doing the multiplication, which "
    "check shows the answer is sensible?",
    key="6 x 50 is 300, and 297.6 is close to that",
    verify="6 x 50 is 300, and 297.6 is close to that",
    wrong=[("6 x 48 is 288, so the answer should be 288", "misread_data"),
           ("the answer has one decimal place, like 6.2", "wrong_attribute"),
           ("48 is even, so the answer should be even", "ignored_constraint")],
    difficulty="hard", confidence=0.90,
    expl="Rounding both numbers to something easy gives 6 x 50 = 300, and 297.6 sits just "
         "under it, so the answer is the right size. 6 x 48 is 288, so the answer should "
         "be 288 is not a check at all — it changes 6.2 to 6 and then insists on the new "
         "answer.",
    fmt=PLAIN),

B.Q("estimation", "multi_step",
    "A rectangular hall measures 19.2 m by 9.8 m. Roughly what is its floor area?",
    # round then multiply, against multiply then round: 188.16 to the nearest hundred
    key=20 * 10, verify=round(19.2 * 9.8, -2),
    wrong=[(2 * (20 + 10), "wrong_attribute"), (20 * 10 * 10, "place_value"),
           (20 + 10, "operation_swap")],
    difficulty="hard", confidence=0.90,
    expl="Round to 20 m by 10 m, which gives about 200 m². The exact area is 188.16 m², so "
         "the estimate is close. 60 is roughly the distance around the hall rather than "
         "the floor inside it, and 30 adds the two sides instead of multiplying them.",
    fmt=unit("m²")),

B.Q("estimation", "single_step",
    "Which of these is the most sensible estimate for the length of an ordinary classroom?",
    key="8 metres", verify="8 metres",
    wrong=[("8 centimetres", "place_value"), ("80 metres", "misread_data"),
           ("8 kilometres", "wrong_attribute")],
    mixed_units=True,           # picking the right unit IS the question here
    expl="A classroom is a few paces across, and a pace is about a metre, so 8 metres is "
         "about right. 8 centimetres is the length of a finger, and 8 kilometres would "
         "take well over an hour to walk.",
    fmt=PLAIN),

# ===================================================== factors, multiples and primes (6)

B.Q("factors_multiples_primes", "single_step",
    "Which of these numbers is prime?",
    key=23, verify=next(n for n in (21, 23, 27, 33) if is_prime(n)),
    wrong=[(21, "misread_data"), (27, "off_by_one"), (33, "wrong_attribute")],
    expl="23 has no factors except 1 and itself, so it is prime. 21 is 3 x 7, 27 is 3 x 9 "
         "and 33 is 3 x 11, so each of those has factors in between.",
    fmt=PLAIN),

B.Q("factors_multiples_primes", "multi_step",
    "What is the largest number that divides exactly into both 24 and 36?",
    key=hcf(24, 36), verify=max(d for d in divisors(24) if 36 % d == 0),
    wrong=[(6, "partial_step"), (24, "misread_data"), (24 * 36 // hcf(24, 36), "inverse")],
    difficulty="hard", confidence=0.91,
    expl="The factors 24 and 36 share are 1, 2, 3, 4, 6 and 12, and the largest is 12. "
         "Check it: 24 / 12 = 2 and 36 / 12 = 3. 6 divides into both but is not the "
         "largest that does, and 72 is the smallest number they both divide into, which is "
         "the opposite question.",
    fmt=PLAIN),

B.Q("factors_multiples_primes", "multi_step",
    "One bus leaves a stop every 6 minutes and another every 8 minutes. They have just "
    "left together. In how many minutes will they next leave together?",
    key=lcm_walk(6, 8), verify=6 * 8 // hcf(6, 8),
    wrong=[(6 * 8, "operation_swap"), (hcf(6, 8), "inverse"), (6 + 8, "misread_data")],
    difficulty="hard", confidence=0.91,
    expl="Count on in sixes — 6, 12, 18, 24 — and in eights — 8, 16, 24 — and 24 is the "
         "first they share. 48 multiplies the two times together, which does give a shared "
         "moment but not the first one, and 14 simply adds them.",
    fmt=unit("minutes")),

B.Q("factors_multiples_primes", "multi_step",
    "How many different factors does 36 have?",
    key=len(divisors(36)), verify=len([d for d in range(1, 37) if 36 % d == 0]),
    wrong=[(len(divisors(36)) - 1, "off_by_one"), (6, "misread_data"), (36 // 2, "operation_swap")],
    difficulty="hard", confidence=0.90,
    expl="Pair them off: 1 and 36, 2 and 18, 3 and 12, 4 and 9, and 6 with itself. That "
         "makes 9 different factors. 8 forgets that 6 x 6 = 36 contributes only one "
         "factor, and 6 counts the pairs rather than the factors.",
    fmt=unit("factors")),

B.Q("factors_multiples_primes", "single_step",
    "Which of these numbers is a multiple of both 3 and 4?",
    key=24, verify=next(n for n in (24, 18, 20, 27) if n % 3 == 0 and n % 4 == 0),
    wrong=[(18, "partial_step"), (20, "misread_data"), (27, "off_by_one")],
    expl="24 divides by 3 to give 8 and by 4 to give 6, so it is a multiple of both. 18 is "
         "a multiple of 3 but not of 4, and 20 is a multiple of 4 but not of 3.",
    fmt=PLAIN),

B.Q("factors_multiples_primes", "single_step",
    "Which of these is NOT a factor of 60?",
    key=8, verify=next(n for n in (8, 5, 12, 15) if 60 % n),
    wrong=[(5, "misread_data"), (12, "off_by_one"), (15, "wrong_attribute")],
    expl="60 / 8 = 7.5, which is not a whole number, so 8 is not a factor. 5, 12 and 15 all "
         "divide 60 exactly, giving 12, 5 and 4.",
    fmt=PLAIN),

# ===================================================== order of operations (2)

for stem_expr, expect, wrongs, expl, diff in [
    ("36 / (3 + 6) x 2", 8,
     [("36 / 3 + 6 x 2", "misread_data"), ("36 / ((3 + 6) x 2)", "operation_swap"),
      ("(36 / 3 + 6) x 2", "wrong_attribute")],
     "Brackets first: 3 + 6 = 9. Then work left to right through the divide and the "
     "multiply: 36 / 9 = 4, and 4 x 2 = 8. 24 ignores the brackets altogether, and 2 "
     "divides by the 2 as well as by the 9, as though the brackets stretched further than "
     "they do.", "hard"),
    ("8 x 3 - 12 / 4", 21,
     [("(8 x 3 - 12) / 4", "misread_data"), ("8 x (3 - 12 / 4)", "wrong_attribute"),
      ("8 x 3 + 12 / 4", "operation_swap")],
     "Multiplying and dividing come before subtracting: 8 x 3 = 24 and 12 / 4 = 3, so "
     "24 - 3 = 21. 3 works straight through from left to right, and 0 subtracts inside a "
     "bracket that is not there.", "hard"),
]:
    B.Q("order_of_operations", "multi_step",
        f"What is the value of {stem_expr}?",
        # `expect` is worked out by hand; `key` is what Python's parser makes of the same
        # printed text. Writing eval() on both sides would only agree with itself.
        key=eval(stem_expr.replace("x", "*")), verify=expect,
        wrong=[(eval(w.replace("x", "*")), cls) for w, cls in wrongs],
        difficulty=diff, confidence=0.90, expl=expl, fmt=PLAIN)

# ===================================================== negative numbers (4)

B.Q("negative_numbers", "multi_step",
    "At 6 pm the temperature on a mountain is 3°C. Overnight it falls by 8 degrees. What "
    "is the temperature then?",
    key=3 - 8, verify=-(8 - 3),                 # count down past zero, then keep going
    wrong=[(8 - 3, "inverse"), (3 + 8, "operation_swap"), (0, "ignored_constraint")],
    expl="Counting down from 3, three degrees reach zero and there are five more to go, so "
         "the temperature is -5°C. 5 gives the size of the drop past zero but leaves off "
         "the minus sign, and 11 adds the fall instead of subtracting it.",
    fmt=DEGC),

B.Q("negative_numbers", "single_step",
    "Which of these lists is in order from coldest to warmest?",
    key="-7°C, -3°C, 0°C, 2°C", verify="-7°C, -3°C, 0°C, 2°C",
    wrong=[("-3°C, -7°C, 0°C, 2°C", "misread_data"), ("0°C, 2°C, -3°C, -7°C", "ignored_constraint"),
           ("2°C, 0°C, -3°C, -7°C", "inverse")],
    difficulty="hard", confidence=0.91,
    expl="Below zero, the bigger the number after the minus sign the colder it is, so -7 "
         "is colder than -3. Reading -3°C, -7°C, 0°C, 2°C treats -3 as smaller than -7 "
         "because 3 is smaller than 7, and the last list runs warmest to coldest.",
    fmt=PLAIN),

B.Q("negative_numbers", "multi_step",
    "How many degrees warmer is 7°C than -4°C?",
    key=7 - (-4), verify=4 + 7,                 # up to zero, then up again
    wrong=[(7 - 4, "misread_data"), (-4 - 7, "inverse"), (4 * 7, "operation_swap")],
    difficulty="hard", confidence=0.91,
    expl="Go up 4 degrees to reach zero, then 7 more to reach 7: 11 degrees in all. 3 "
         "subtracts as though the -4 were a 4, which loses the part of the journey below "
         "zero.",
    fmt=DEGC),

B.Q("negative_numbers", "multi_step",
    "A lift starts 3 floors below ground, goes up 7 floors, then down 2. Where does it "
    "finish?",
    key=-3 + 7 - 2, verify=2,                   # -3, then 4, then 2
    wrong=[(-3 + 7 + 2, "operation_swap"), (3 + 7 - 2, "misread_data"), (-3 - 7 + 2, "inverse")],
    expl="Start at -3, go up 7 to reach floor 4, then down 2 to floor 2. 8 goes up on the "
         "last move instead of down, and -8 treats the first move as going further down.",
    fmt=lambda v: f"{abs(v)} floors above ground" if v >= 0
                  else f"{abs(v)} floors below ground"),

if __name__ == "__main__":
    B.write()
