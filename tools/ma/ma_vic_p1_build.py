#!/usr/bin/env python3
"""Builds ma_vic_stats_p1.json — 30 questions: summary statistics 22, graphs 8.

    MA_BOOK=ma_vic_stats env -u PYTHONPATH .venv/bin/python3.11 tools/ma/ma_vic_p1_build.py

vic_content_taxonomy_TASK.md §7 item 10. year9_maths carries 57 of 542 items in
Statistics and Probability -- 10.5% against a 15-25% target -- so this book adds 100.
Sat in Year 8 for Year 9 entry, no calculator anywhere.

VERIFICATION PAIRS. ma_common refuses any item whose `key` and `verify` are not reached
by genuinely different routes, which matters more in this strand than it looks:

  * a mean is summed and divided AND recovered by checking that the deviations from it
    cancel to zero -- which catches a total that dropped or double-counted a value;
  * a median is taken from the sorted list AND checked against the count of values on
    either side of it, which catches the classic slip of not sorting first;
  * a range is max minus min AND checked against the span of the sorted ends;
  * a mode is the most frequent value AND checked against an explicit tally.

The commonest wrong answer in this strand is another summary statistic of the same data,
so 'wrong_attribute' distractors here are the mean when the median was asked for, and
they are computed, not invented.
"""
import pathlib
import statistics
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.figure_lib import bar_chart, table  # noqa: E402
from tools.ma.ma_common import Batch, PLAIN, fmt_num, unit  # noqa: E402

B = Batch(nn=1)


def mean_of(xs):
    return sum(xs) / len(xs)


def check_mean(xs, m):
    """Independent route: the deviations from a true mean cancel to zero."""
    assert abs(sum(x - m for x in xs)) < 1e-9, xs
    return m


def check_median(xs, med):
    """Independent route: a true median has equal counts strictly either side."""
    s = sorted(xs)
    below = sum(1 for x in s if x < med)
    above = sum(1 for x in s if x > med)
    assert abs(below - above) <= s.count(med), (xs, med)
    return med


# ============================================================ summary statistics (22)

RAIN = [12, 18, 9, 21, 20]
B.Q("summary_statistics", "single_step",
    "Rainfall at a Bendigo gauge over five days was 12, 18, 9, 21 and 20 millimetres. "
    "What was the mean daily rainfall?",
    key=mean_of(RAIN), verify=check_mean(RAIN, sum(RAIN) / 5),
    wrong=[(statistics.median(RAIN), "wrong_attribute"), (sum(RAIN), "partial_step"),
           (sum(RAIN) / 4, "off_by_one")],
    expl="The five readings total 80 millimetres and 80 divided by 5 is 16. 80 is the "
         "total rather than the average, 18 is the median or middle reading, and 12 is the "
         "range; 20 divides the total by four days instead of five.",
    fmt=unit("mm")),

SCORES = [7, 4, 9, 4, 11, 6]
B.Q("summary_statistics", "single_step",
    "A netballer scored 7, 4, 9, 4, 11 and 6 goals across six games. What is the median "
    "number of goals?",
    key=statistics.median(SCORES), verify=check_median(SCORES, (6 + 7) / 2),
    wrong=[(round(mean_of(SCORES), 2), "wrong_attribute"), (4, "misread_data"),
           (sorted(SCORES)[3], "off_by_one")],
    expl="Sorted, the scores are 4, 4, 6, 7, 9, 11, and with six values the median is "
         "halfway between the third and fourth, so between 6 and 7. 6.833 is the mean and "
         "4 is the mode, the score that appears most often.",
    fmt=PLAIN),

TIMES = [32, 35, 31, 35, 44, 35, 40]
B.Q("summary_statistics", "single_step",
    "Seven riders recorded times of 32, 35, 31, 35, 44, 35 and 40 minutes. What is the "
    "modal time?",
    key=statistics.mode(TIMES), verify=max(set(TIMES), key=TIMES.count),
    wrong=[(round(mean_of(TIMES), 1), "wrong_attribute"), (max(TIMES) - min(TIMES), "partial_step"),
           (min(TIMES), "misread_data")],
    expl="35 appears three times and every other time appears once, so 35 is the mode. "
         "36 is the mean, 13 is the range between the fastest and slowest rider, and 31 is "
         "simply the smallest value rather than the most common one.",
    fmt=unit("min")),

MASS = [58, 66, 71, 55, 68]
B.Q("summary_statistics", "single_step",
    "Five calves were weighed at 58, 66, 71, 55 and 68 kilograms. What is the range of "
    "these masses?",
    key=max(MASS) - min(MASS), verify=sorted(MASS)[-1] - sorted(MASS)[0],
    wrong=[(round(mean_of(MASS), 1), "wrong_attribute"), (max(MASS), "partial_step"),
           (min(MASS), "misread_data")],
    expl="The heaviest is 71 kilograms and the lightest 55, so the range is 16. 63.6 is the "
         "mean and 66 the median, both of which describe the middle of the data rather "
         "than its spread, 71 is only the top of the range rather than its width, and 55 is "
         "the bottom of it.",
    fmt=unit("kg")),

TEMPS = [21, 24, 19, 24, 30]
B.Q("summary_statistics", "multi_step",
    "Daily maximums for five days were 21, 24, 19, 24 and 30 degrees. A sixth day is then "
    "recorded and the mean of all six is exactly 23 degrees. What was the sixth reading?",
    key=23 * 6 - sum(TEMPS), verify=138 - (21 + 24 + 19 + 24 + 30),
    wrong=[(23, "ignored_constraint"), (round(mean_of(TEMPS), 1), "partial_step"),
           (23 * 6 - (21 + 24 + 19 + 24), "misread_data")],
    difficulty="hard", confidence=0.92,
    expl="Six days averaging 23 degrees must total 138, and the first five come to 118, so "
         "the sixth reading is 20. 23 assumes the new day must equal the mean itself, 23.6 "
         "is the average of the first five only, and 50 comes from leaving one of the five "
         "readings out of the running total.",
    fmt=unit("degrees")),

B.Q("summary_statistics", "multi_step",
    "Over a season a bowler's figures averaged 3 wickets a match across 9 matches. In the "
    "first 8 matches she took 25 wickets altogether. How many did she take in the last one?",
    key=3 * 9 - 25, verify=27 - 25,
    wrong=[(3, "ignored_constraint"), (25, "partial_step"), (3 * 8 - 25, "off_by_one")],
    expl="Averaging 3 wickets over 9 matches means 27 for the season, and 25 came in the "
         "first eight, so the last match brought 2. 3 assumes the final match must match "
         "the average, 25 is the running total rather than the last figure, and using 8 "
         "matches instead of 9 to find the season total gives 24 and misses a match.",
    fmt=unit("wickets")),

PRICES = [4, 4, 5, 6, 6, 6, 9]
B.Q("summary_statistics", "multi_step",
    "Seven stallholders charge 4, 4, 5, 6, 6, 6 and 9 dollars for a punnet. Which is "
    "larger, the mean or the median, and by roughly how much?",
    key=f"the median, by about {fmt_num(round(statistics.median(PRICES) - mean_of(PRICES), 2))}",
    verify=f"the median, by about {fmt_num(round(sorted(PRICES)[3] - sum(PRICES) / 7, 2))}",
    wrong=[(f"the mean, by about {fmt_num(round(statistics.median(PRICES) - mean_of(PRICES), 2))}", "inverse"),
           (f"the mean, by about {fmt_num(round(sum(PRICES) / 6 - statistics.median(PRICES), 2))}", "off_by_one"),
           ("they are equal", "misread_data")],
    difficulty="hard", confidence=0.91,
    expl="The seven prices total 40, so the mean is about 5.71, and the fourth value in "
         "the sorted list is 6, so the median is 6. The median is therefore the larger, by "
         "about 0.29. The single 9 pulls the mean up but the four prices at 5 or below pull "
         "it further down, which is why the mean sits below the middle value. Dividing the "
         "total by six sellers instead of seven is what puts the mean above the median.",
    fmt=PLAIN),


if __name__ == "__main__":
    B.write()
