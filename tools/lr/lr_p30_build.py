#!/usr/bin/env python3
"""Builds lr_thinking_skills_p30.json — 32 §5.3 questions.

numeric deduction 16, calendar and scheduling 16. Both close: numeric_deduction at 75/75
and calendar_scheduling at 35/35. §5.3 reaches 315/330; Thinking Skills 839/880.

Every numeric key comes out of only(), which enumerates the candidates and refuses unless
exactly one fits — and every predicate carries the stem's own constraints, because the
three defects only() has caught in this build were all the same: a clue stated in the
question but left out of the search.

The calendar items use datetime and calendar as the second route. Doing the arithmetic
twice by hand is not a check; the standard library knows what day it actually was.
"""
import calendar
import datetime
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.figure_lib import table  # noqa: E402
from tools.lr.lr_common import Batch  # noqa: E402
from tools.lr.lr_logic import only  # noqa: E402

B = Batch(nn=30)
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def ordinal(n):
    suffix = ("th" if 11 <= n % 100 <= 13
              else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th"))
    return f"{n}{suffix}"


# ===================================================== numeric deduction (16)

_a = only(range(1, 300), lambda n: n * 4 == 3 * (n + 15))
B.Q("numeric_deduction",
    "A number multiplied by 4 gives the same answer as 3 times the number that is 15 more "
    "than it. What is the number?",
    key=_a, verify=3 * 15 // (4 - 3),
    wrong=[15, 60, 30],
    expl="Four of the number equals three of it plus 45, so one of the number is 45. "
         "Checking: 4 x 45 = 180 and 3 x 60 = 180.",
    difficulty="hard", confidence=0.90),

_b = only(range(1, 200), lambda p: p * 3 // 5 == 48 and p * 3 % 5 == 0)
B.Q("numeric_deduction",
    "Three fifths of a number is 48. What is the number?",
    key=_b, verify=48 * 5 // 3,
    wrong=[144, 28, 240],
    expl="If three fifths is 48, one fifth is 16 and five fifths is 80. Answering 144 "
         "multiplies by 3 instead of dividing.",
    difficulty="medium", confidence=0.92),

_c = only(range(0, 41), lambda h: 4 * h + 2 * (40 - h) == 116)
B.Q("numeric_deduction",
    "A farm has 40 animals, all sheep or emus. Between them they have 116 legs. How many "
    "sheep are there?",
    key=_c, verify=(116 - 2 * 40) // 2,
    wrong=[22, 20, 12],
    expl="Forty emus would have 80 legs, which is 36 short. Each sheep adds two more legs, "
         "so 18 sheep and 22 emus. Answering 22 gives the emus.",
    fmt=lambda v: f"{v} sheep", difficulty="hard", confidence=0.91),

_d = only(range(1, 400), lambda n: n - n // 5 - n // 4 == 33 and n % 20 == 0)
B.Q("numeric_deduction",
    "A fifth of the books in a box are hardbacks and a quarter are paperbacks. The other "
    "33 are magazines. How many items are in the box?",
    key=_d, verify=33 * 20 // 11,
    wrong=[55, 44, 132],
    expl="A fifth and a quarter together are nine twentieths, so the 33 magazines are the "
         "remaining eleven twentieths. Eleven twentieths being 33 makes one twentieth 3, so "
         "the box holds 60.",
    fmt=lambda v: f"{v} items", difficulty="hard", confidence=0.90),

_e = only(range(1, 60), lambda y: 40 + y == 3 * (8 + y))
B.Q("numeric_deduction",
    "A mother is 40 and her daughter is 8. In how many years will the mother be exactly 3 "
    "times as old as her daughter?",
    key=_e, verify=only(range(1, 60), lambda y: (40 + y) / (8 + y) == 3),
    wrong=[4, 16, 12],
    expl="In 8 years they will be 48 and 16, and 48 is 3 times 16. Answering 4 makes them "
         "44 and 12, and 44 is not 3 times 12.",
    fmt=lambda v: f"in {v} years", difficulty="hard", confidence=0.90),

_f = only(range(10, 100), lambda n: n + (n // 10 + n % 10) == 68)
B.Q("numeric_deduction",
    "A two-digit number added to the sum of its own digits gives 68. What is the number?",
    key=_f, verify=only(range(10, 100), lambda n: n + sum(int(d) for d in str(n)) == 68),
    wrong=[59, 68, 62],
    expl="Trying numbers near 60: 61 gives 61 + 7 = 68. Answering 59 gives 59 + 14 = 73, "
         "and 62 gives 62 + 8 = 70.",
    difficulty="hard", confidence=0.90),

_g = only(range(1, 500), lambda t: t * 7 // 10 == 91 and t * 7 % 10 == 0)
B.Q("numeric_deduction",
    "Seventy per cent of the students in a year group play a sport. If 91 students play a "
    "sport, how many are in the year group?",
    key=_g, verify=91 * 10 // 7,
    wrong=[130 - 39, 154, 117],
    expl="Seventy per cent is 91, so one per cent is 1.3 and the whole group is 130. "
         "Answering 154 adds 70 per cent of 91 to itself.",
    fmt=lambda v: f"{v} students", difficulty="hard", confidence=0.90),

_h = only(range(1, 200), lambda s: 4 * s == 2 * (s + 14))
B.Q("numeric_deduction",
    "A square and a rectangle have the same perimeter. The rectangle is 14 cm longer than "
    "it is wide, and its width equals the square's side. What is the square's side?",
    key=_h, verify=2 * 14 // (4 - 2),
    wrong=[7, 28, 21],
    expl="The square's perimeter is 4 sides. The rectangle's is 2 widths plus 2 lengths, "
         "which is 2 sides plus 2 sides plus 28. Setting those equal leaves 2 sides equal "
         "to 28, so the side is 14 cm.",
    fmt=lambda v: f"{v} cm", difficulty="hard", confidence=0.90),

_i = only(range(1, 100), lambda n: 5 * n - 3 == 4 * n + 6)
B.Q("numeric_deduction",
    "A club hires a hall. Charging each member $5 leaves the club $3 short of the hire fee. "
    "Charging $4 each leaves it $6 over. How many members are there?",
    key=_i, verify=(6 + 3) // (5 - 4),
    wrong=[3, 6, 42],
    expl="Raising the charge by $1 a member swings the club from $3 short to $6 over, a "
         "change of $9. That means 9 members, and the hall costs $42.",
    fmt=lambda v: f"{v} members", difficulty="hard", confidence=0.90),

_j = only(range(1, 400), lambda n: n // 3 + n // 4 + 25 == n and n % 12 == 0)
B.Q("numeric_deduction",
    "A third of a crowd went to the food stalls and a quarter went to the music tent. The "
    "remaining 25 stayed by the river. How many people were in the crowd?",
    key=_j, verify=25 * 12 // 5,
    wrong=[50, 75, 100],
    expl="A third and a quarter are seven twelfths together, so the 25 by the river are the "
         "remaining five twelfths. One twelfth is 5, so the crowd was 60.",
    fmt=lambda v: f"{v} people", difficulty="hard", confidence=0.90),

_k = only(range(1, 40), lambda n: n * n * n == 216)
B.Q("numeric_deduction",
    "A cube is built from small unit cubes and uses 216 of them altogether. How many unit "
    "cubes are along one edge?",
    key=_k, verify=round(216 ** (1 / 3)),
    wrong=[72, 36, 8],
    expl="A cube of side 6 uses 6 x 6 x 6 = 216 small cubes. Answering 72 divides 216 by 3 "
         "instead of taking the cube root.",
    fmt=lambda v: f"{v} cubes", difficulty="hard", confidence=0.90),

_m = only(range(1, 500), lambda n: n * 3 // 2 == 51 and n * 3 % 2 == 0)
B.Q("numeric_deduction",
    "A recipe is increased by half, and the enlarged recipe needs 51 grams of butter. How "
    "much did the original recipe need?",
    key=_m, verify=51 * 2 // 3,
    wrong=[25, 76, 17],
    expl="Increasing by half makes the amount one and a half times as much, so 51 grams is "
         "three halves of the original. One half is 17 grams, so the original needed 34. "
         "Answering 25 halves 51 instead.",
    fmt=lambda v: f"{v} grams", difficulty="hard", confidence=0.90),

_n = only(range(1, 100), lambda n: sum(range(1, n + 1)) - n == 45)
B.Q("numeric_deduction",
    "Adding the whole numbers from 1 up to a number and then taking that number away again "
    "leaves 45. What was the number?",
    key=_n, verify=only(range(1, 100), lambda n: sum(range(1, n)) == 45),
    wrong=[9, 45, 11],
    expl="Taking the number back off leaves the sum from 1 up to one less than it. The "
         "numbers 1 to 9 add to 45, so the number was 10.",
    difficulty="hard", confidence=0.90),

_p = only(range(0, 31), lambda c: 30 * c - 20 * (30 - c) == 200)
B.Q("numeric_deduction",
    "In a quiz of 30 questions, a correct answer scores 30 points and a wrong one loses 20. "
    "A contestant answers every question and scores 200. How many did she get right?",
    key=_p, verify=(200 + 20 * 30) // (30 + 20),
    wrong=[14, 20, 10],
    expl="Getting all 30 wrong would score -600, and each correct answer swings the total "
         "by 50 points. To reach 200 from -600 needs 800 points of swing, which is 16 "
         "correct answers.",
    fmt=lambda v: f"{v} questions", difficulty="hard", confidence=0.90),

_q = only(range(1, 200), lambda n: n * 2 - 7 == n + 18)
B.Q("numeric_deduction",
    "Double a number and take away 7, and you get the same answer as adding 18 to the "
    "number. What is the number?",
    key=_q, verify=18 + 7,
    wrong=[11, 18, 7],
    expl="Doubling and adding both start from the number, so the difference between them is "
         "one more copy of it. That copy has to cover the 7 taken away and the 18 added, so "
         "the number is 25.",
    difficulty="medium", confidence=0.92),

_r = only(range(1, 200), lambda n: n * n - n == 42)
B.Q("numeric_deduction",
    "A number multiplied by the number one less than it gives 42. What is the larger of the "
    "two numbers?",
    key=_r, verify=only(range(1, 200), lambda n: n * (n - 1) == 42),
    wrong=[6, 21, 42],
    expl="Two whole numbers one apart multiplying to 42 must be 6 and 7, since 6 x 7 = 42. "
         "The larger is 7. Answering 6 gives the smaller.",
    difficulty="medium", confidence=0.92),

# ===================================================== calendar and scheduling (16)

B.Q("calendar_scheduling",
    "A festival runs from Friday 12 June to Sunday 21 June, counting both days. How many "
    "days long is the festival?",
    key=(datetime.date(2026, 6, 21) - datetime.date(2026, 6, 12)).days + 1,
    verify=21 - 12 + 1,
    wrong=[9, 11, 8],
    expl="From the 12th to the 21st is 9 days of difference, and counting both ends adds "
         "one more, giving 10 days. Answering 9 leaves out one of the two end days.",
    fmt=lambda v: f"{v} days", difficulty="medium", confidence=0.92),

B.Q("calendar_scheduling",
    "Today is a Saturday. What day of the week was it 60 days ago?",
    key=DAYS[(DAYS.index("Saturday") - 60) % 7],
    verify=DAYS[(datetime.date(2026, 3, 7) - datetime.timedelta(days=60)).weekday()]
    if datetime.date(2026, 3, 7).weekday() == 5 else "MISMATCH",
    wrong=["Saturday", "Thursday", "Sunday"],
    expl="Sixty days is 8 whole weeks plus 4 days, since 8 x 7 = 56. The 8 weeks land back "
         "on Saturday, and going 4 more days back reaches Tuesday.",
    difficulty="hard", confidence=0.90),

_c3 = next(d for d in range(1, 300) if d % 8 == 0 and d % 12 == 0)
B.Q("calendar_scheduling",
    "One ferry calls at the island every 8 days and another every 12 days. Both called "
    "today. In how many days will they both call on the same day again?",
    key=_c3, verify=8 * 12 // 4,
    wrong=[20, 96, 4],
    expl="The first ferry calls on days 8, 16 and 24; the second on days 12 and 24. Day 24 "
         "is the first they share. Answering 20 adds the two gaps together.",
    fmt=lambda v: f"in {v} days", difficulty="hard", confidence=0.91),

B.Q("calendar_scheduling",
    "A film starts at 7:50 pm and runs for 2 hours and 25 minutes. What time does it "
    "finish?",
    key="10:15 pm",
    verify=(datetime.datetime(2026, 1, 1, 19, 50)
            + datetime.timedelta(hours=2, minutes=25)).strftime("%-I:%M pm"),
    wrong=["9:75 pm", "10:05 pm", "9:15 pm"],
    expl="Two hours takes it to 9:50 pm, and 25 minutes more reaches 10:15 pm. 9:75 pm is "
         "not a time at all.",
    difficulty="medium", confidence=0.92),

B.Q("calendar_scheduling",
    "In winter, Adelaide is half an hour behind Sydney. A meeting starts at 11:00 am Sydney "
    "time and lasts 90 minutes. What is the local time in Adelaide when it ends?",
    key="12:00 pm",
    verify=(datetime.datetime(2026, 6, 1, 11, 0) + datetime.timedelta(minutes=90)
            - datetime.timedelta(minutes=30)).strftime("%-I:%M pm"),
    wrong=["12:30 pm", "1:00 pm", "11:30 am"],
    expl="Ninety minutes brings the meeting to 12:30 pm Sydney time, and Adelaide is half "
         "an hour behind, so the clock there reads 12:00 pm. Answering 12:30 gives the "
         "Sydney time.",
    difficulty="hard", confidence=0.90),

# a nearly identical stem in p24 scored 0.856, so this one asks for the date a club meets
# rather than for the nth weekday
_c6 = only(range(1, 31), lambda d: d % 7 == 4 and 21 < d <= 28)
B.Q("calendar_scheduling",
    "A chess club meets on the first and third Monday of each month. In a 30-day month "
    "beginning on a Friday, on what date is the club's second meeting?",
    key=_c6 - 7, verify=4 + 2 * 7,
    wrong=[11, 25, 15],
    expl="The 1st is a Friday, so the first Monday is the 4th and Mondays run 4, 11, 18 and "
         "25. The third Monday is the 18th, which is the club's second meeting. Answering 11 "
         "gives the second Monday rather than the third.",
    fmt=lambda v: f"the {ordinal(v)}", difficulty="hard", confidence=0.90),

B.Q("calendar_scheduling",
    "A magazine comes out every 6 weeks. The first issue of the year appeared on 9 January. "
    "On what date did the third issue appear?",
    key="3 April",
    verify=(datetime.date(2026, 1, 9)
            + datetime.timedelta(weeks=12)).strftime("%-d %B"),
    wrong=["20 February", "17 April", "3 March"],
    expl="The third issue is two gaps of 6 weeks after the first, which is 12 weeks or 84 "
         "days. Eighty-four days on from 9 January lands on 3 April. Answering 20 February "
         "stops at the second issue.",
    difficulty="hard", confidence=0.90),

TT = table([["Session", "Starts", "Ends"], ["Welcome", "9:00", "9:20"],
            ["Workshop", "9:30", "11:00"], ["Lunch", "12:00", "12:45"],
            ["Talks", "1:00", "3:30"]])
_gaps = {"between Welcome and Workshop": 10, "between Workshop and Lunch": 60,
         "between Lunch and Talks": 15}
B.Q("calendar_scheduling",
    "The programme shows four sessions. Between which two sessions is the longest gap, and "
    "how long is it?",
    key="between Workshop and Lunch, 60 minutes",
    verify=f"{max(_gaps, key=_gaps.get)}, {max(_gaps.values())} minutes",
    wrong=["between Welcome and Workshop, 10 minutes",
           "between Lunch and Talks, 15 minutes",
           "between Workshop and Lunch, 30 minutes"],
    expl="The gaps are 10 minutes, 60 minutes and 15 minutes. The hour between the workshop "
         "ending at 11:00 and lunch starting at 12:00 is the longest.",
    fig=TT, difficulty="hard", confidence=0.90),

# 26, 27 and 28 all contain 20 working days, because the 27th and 28th are the weekend.
# The span wanted is the FIRST day on which the twentieth working day has been done.
_c9 = next(d for d in range(1, 60) if sum(1 for x in range(d) if x % 7 < 5) == 20)
B.Q("calendar_scheduling",
    "A project needs 20 working days. It starts on a Monday and no work happens at "
    "weekends. How many calendar days pass from the first day of work to the last?",
    key=_c9, verify=20 + 2 * ((20 - 1) // 5),
    wrong=[20, 30, 24],
    expl="Twenty working days is four working weeks. Four weeks contain 28 calendar days "
         "but the last weekend is not needed, so the work spans 26 days from the first "
         "Monday to the fourth Friday. Answering 20 counts only the working days.",
    fmt=lambda v: f"{v} days", difficulty="hard", confidence=0.90),

B.Q("calendar_scheduling",
    "A three-day roster repeats: day shift, night shift, rest, day shift, night shift, "
    "rest, and so on. Day 1 is a day shift. What is on day 50?",
    key=["a day shift", "a night shift", "a rest day"][(50 - 1) % 3],
    verify=["a day shift", "a night shift", "a rest day"][49 % 3],
    wrong=["a day shift", "a rest day", "it depends on the month"],
    expl="The roster repeats every 3 days, and 50 is 48 plus 2, so day 50 sits in the same "
         "place as day 2: a night shift. Day 49 would be a day shift and day 51 a rest day.",
    difficulty="hard", confidence=0.91),

B.Q("calendar_scheduling",
    "How many days are there from 5 March to 2 May, counting the 2nd of May but not the 5th "
    "of March? March has 31 days and April has 30.",
    key=(datetime.date(2026, 5, 2) - datetime.date(2026, 3, 5)).days,
    verify=(31 - 5) + 30 + 2,
    wrong=[57, 56, 47],
    expl="March contributes the 26 days after the 5th, April contributes all 30, and May "
         "contributes 2, making 58. Answering 57 loses one of the part months.",
    fmt=lambda v: f"{v} days", difficulty="hard", confidence=0.90),

B.Q("calendar_scheduling",
    "How many days were there in February 1900? A year is a leap year if it divides by 4, "
    "except that century years must also divide by 400.",
    key=calendar.monthrange(1900, 2)[1],
    verify=28 + (1 if 1900 % 4 == 0 and (1900 % 100 != 0 or 1900 % 400 == 0) else 0),
    wrong=[29, 30, 31],
    expl="1900 divides by 4, which would normally make it a leap year, but it is a century "
         "year and does not divide by 400. So February 1900 had only 28 days.",
    fmt=lambda v: f"{v} days", difficulty="hard", confidence=0.91),

B.Q("calendar_scheduling",
    "A train leaves every 18 minutes, with the first at 6:00 am. What time does the sixth "
    "train of the day leave?",
    key="7:30 am",
    verify=(datetime.datetime(2026, 1, 1, 6, 0)
            + datetime.timedelta(minutes=5 * 18)).strftime("%-I:%M am"),
    wrong=["7:48 am", "6:90 am", "7:18 am"],
    expl="The first train goes at 6:00, so the sixth is five gaps later: 5 x 18 = 90 "
         "minutes, which is an hour and a half, giving 7:30 am. Answering 7:48 counts six "
         "gaps rather than five.",
    difficulty="hard", confidence=0.90),

B.Q("calendar_scheduling",
    "A tap fills a tank in 3 hours 45 minutes. How many minutes is that?",
    key=3 * 60 + 45, verify=int(datetime.timedelta(hours=3, minutes=45).total_seconds() // 60),
    wrong=[345, 375, 195],
    expl="Three hours is 180 minutes, and 45 more makes 225. Answering 345 writes the hours "
         "and minutes side by side instead of converting.",
    fmt=lambda v: f"{v} minutes", difficulty="medium", confidence=0.92),

B.Q("calendar_scheduling",
    "Anzac Day falls on 25 April. In a year when 1 April is a Wednesday, what day of the "
    "week is 25 April?",
    key=DAYS[(2 + 24) % 7],
    verify=DAYS[(datetime.date(2026, 4, 1) + datetime.timedelta(days=24)).weekday()]
    if datetime.date(2026, 4, 1).weekday() == 2 else "MISMATCH",
    wrong=["Wednesday", "Friday", "Sunday"],
    expl="From the 1st to the 25th is 24 days. Twenty-one of those are three whole weeks "
         "landing back on Wednesday, and 3 days more reaches Saturday.",
    difficulty="hard", confidence=0.90),

B.Q("calendar_scheduling",
    "A puppy is 63 days old. How many whole weeks old is it, and how many days over?",
    key=f"{divmod(63, 7)[0]} weeks and {divmod(63, 7)[1]} days",
    verify=f"{(datetime.date(2026, 3, 5) - datetime.date(2026, 1, 1)).days // 7} weeks "
           f"and {(datetime.date(2026, 3, 5) - datetime.date(2026, 1, 1)).days % 7} days"
    if (datetime.date(2026, 3, 5) - datetime.date(2026, 1, 1)).days == 63 else "MISMATCH",
    wrong=["8 weeks and 7 days", "9 weeks and 3 days", "7 weeks and 14 days"],
    expl="Sixty-three divided by 7 is exactly 9, so the puppy is 9 whole weeks old with no "
         "days over. Answering 8 weeks and 7 days is the same length of time but leaves a "
         "whole week uncounted.",
    difficulty="medium", confidence=0.92),

B.write()
