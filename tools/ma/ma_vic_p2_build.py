#!/usr/bin/env python3
"""Builds ma_vic_stats_p2.json — 15 summary statistics, closing that category at 22.

    MA_BOOK=ma_vic_stats env -u PYTHONPATH .venv/bin/python3.11 tools/ma/ma_vic_p2_build.py

Two rules this strand keeps breaking, both learned on p1:

  * THREE DIFFERENT ERROR CLASSES. The obvious distractor here is always "another
    summary statistic of the same data", which collapses to wrong_attribute twice over
    and hands the answer to anyone who spots the odd one out.
  * THE STATISTICS MUST SEPARATE. Pick data casually and the mean equals the median, or
    the mode equals the middle value, and two options come out identical. ma_common
    aborts on that, but it is cheaper to choose data that separates in the first place.
"""
import pathlib
import statistics
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.ma.ma_common import Batch, PLAIN, unit  # noqa: E402

B = Batch(nn=2)


def mean_of(xs):
    return sum(xs) / len(xs)


def dev_check(xs, m):
    """Independent route: deviations from a true mean cancel to zero."""
    assert abs(sum(x - m for x in xs)) < 1e-9, xs
    return m


# ============================================== summary statistics (15) -> 22/22

A1 = [2, 8, 5, 12, 8]
B.Q("summary_statistics", "single_step",
    "Five deliveries contained 2, 8, 5, 12 and 8 crates. What is the mean number of "
    "crates per delivery?",
    key=mean_of(A1), verify=dev_check(A1, sum(A1) / 5),
    wrong=[(statistics.median(A1), "wrong_attribute"), (sum(A1), "partial_step"),
           (sum(A1) / 4, "off_by_one")],
    expl="The five deliveries total 35 crates and 35 divided by 5 is 7. 8 is the median, "
         "the middle value once they are sorted, 35 is the total rather than the average, "
         "and 8.75 divides by four deliveries instead of five.",
    fmt=unit("crates")),

A2 = [14, 9, 22, 9, 17, 31]
B.Q("summary_statistics", "single_step",
    "Six volunteers logged 14, 9, 22, 9, 17 and 31 hours. What is the median number of "
    "hours?",
    key=statistics.median(A2), verify=(sorted(A2)[2] + sorted(A2)[3]) / 2,
    wrong=[(round(mean_of(A2), 1), "wrong_attribute"), (statistics.mode(A2), "misread_data"),
           (sorted(A2)[2], "off_by_one")],
    expl="Sorted, the hours run 9, 9, 14, 17, 22, 31, and with six values the median sits "
         "halfway between the third and fourth, so between 14 and 17. 14 takes only the "
         "third value, 9 is the mode, and 17 is the mean.",
    fmt=unit("hours")),

A3 = [6, 6, 6, 11, 15, 20]
B.Q("summary_statistics", "single_step",
    "A stall sold 6, 6, 6, 11, 15 and 20 loaves on six mornings. What is the modal number "
    "of loaves?",
    key=statistics.mode(A3), verify=max(set(A3), key=A3.count),
    wrong=[(round(mean_of(A3), 1), "wrong_attribute"), (max(A3) - min(A3), "partial_step"),
           (statistics.median(A3), "misread_data")],
    expl="6 loaves occurs on three mornings and nothing else repeats, so 6 is the mode. "
         "10.7 is the mean, 14 is the range, and 8.5 is the median, the middle of the sorted "
         "list rather than the most frequent value.",
    fmt=unit("loaves")),

A4 = [42, 51, 38, 60, 47]
B.Q("summary_statistics", "single_step",
    "Five stalls took 42, 51, 38, 60 and 47 dollars in the first hour. What is the range?",
    key=max(A4) - min(A4), verify=sorted(A4)[-1] - sorted(A4)[0],
    wrong=[(round(mean_of(A4), 1), "wrong_attribute"), (max(A4), "partial_step"),
           (min(A4), "misread_data")],
    expl="The largest taking is 60 dollars and the smallest 38, so the range is 22. 47.6 "
         "is the mean and describes the middle rather than the spread, while 60 and 38 are "
         "the two ends of the range rather than the distance between them.",
    fmt=unit("dollars")),

A5 = [4, 7, 7, 10, 12]
B.Q("summary_statistics", "multi_step",
    "Five readings are 4, 7, 7, 10 and 12. If a sixth reading of 14 is added, by how much "
    "does the mean increase?",
    key=round((sum(A5) + 14) / 6 - mean_of(A5), 1),
    verify=round((54 / 6) - (40 / 5), 1),
    wrong=[(14, "ignored_constraint"), (round((sum(A5) + 14) / 6, 1), "partial_step"),
           (round(14 - mean_of(A5), 1), "operation_swap")],
    difficulty="hard", confidence=0.91,
    expl="The first five total 40, so the mean is 8. Adding 14 makes 54 over six readings, "
         "a mean of 9, so the increase is 1. 9 is the new mean rather than the change, and "
         "6 is the gap between the new reading and the old mean.",
    fmt=PLAIN),

A6 = [16, 20, 24, 28]
B.Q("summary_statistics", "multi_step",
    "Four measurements have a mean of 22. Three of them are 16, 20 and 24. What is the "
    "fourth measurement?",
    key=22 * 4 - (16 + 20 + 24), verify=88 - 60,
    wrong=[(22, "ignored_constraint"), (60, "partial_step"), (22 * 3 - 60, "off_by_one")],
    expl="Four measurements averaging 22 total 88, and the three given come to 60, so the "
         "fourth is 28. 60 is the running total, 22 assumes the missing value equals the "
         "mean, and using three measurements instead of four gives 6.",
    fmt=PLAIN),

A7 = [5, 9, 9, 13, 19]
B.Q("summary_statistics", "multi_step",
    "For the values 5, 9, 9, 13 and 19, which statement is correct?",
    key="the mean is greater than the median",
    verify="the mean is greater than the median" if sum(A7) / 5 > statistics.median(A7) else "x",
    wrong=[("the median is greater than the mean", "inverse"),
           ("the mean equals the median", "misread_data"),
           ("the mode is greater than the mean", "wrong_attribute")],
    difficulty="hard", confidence=0.92,
    expl="The five values total 55, giving a mean of 11, and the middle value is 9, so the "
         "mean is the larger. The single high value of 19 drags the mean above the middle "
         "of the data, which is what a long tail on one side always does; the median is "
         "greater than the mean would be true only if the tail ran the other way.",
    fmt=PLAIN),

A8 = [11, 11, 14, 18, 21, 25]
B.Q("summary_statistics", "multi_step",
    "Six readings are 11, 11, 14, 18, 21 and 25. What is the difference between the mean "
    "and the median?",
    key=round(mean_of(A8) - statistics.median(A8), 1),
    verify=round(sum(A8) / 6 - (14 + 18) / 2, 1),
    wrong=[(round(mean_of(A8), 1), "partial_step"), (statistics.median(A8), "wrong_attribute"),
           (max(A8) - min(A8), "operation_swap")],
    difficulty="hard", confidence=0.91,
    expl="The six readings total 100, so the mean is 16.7, and the median lies between 14 "
         "and 18, so 16. The difference is 0.7. 16.7 and 16 are the two statistics "
         "themselves rather than the gap between them, and 14 is the range.",
    fmt=PLAIN),

A9 = [2, 4, 4, 5, 8, 8, 8]
B.Q("summary_statistics", "single_step",
    "A survey recorded 2, 4, 4, 5, 8, 8 and 8 responses across seven questions. Which "
    "statistic is the largest for this data?",
    key="the mode", verify="the mode" if statistics.mode(A9) > max(mean_of(A9), statistics.median(A9)) else "x",
    wrong=[("the median", "wrong_attribute"), ("the mean", "partial_step"),
           ("the range", "misread_data")],
    difficulty="hard", confidence=0.90,
    expl="The mode is 8, the median is the fourth value of seven which is 5, and the mean "
         "is 39 divided by 7, about 5.6. The mode is therefore the largest of the three. "
         "The range is 6, which is not one of the three averages being compared.",
    fmt=PLAIN),

A10 = [30, 45, 45, 60, 70]
B.Q("summary_statistics", "multi_step",
    "Five journeys took 30, 45, 45, 60 and 70 minutes. If the 70-minute journey is removed, "
    "what happens to the mean?",
    key=f"it falls by {round(mean_of(A10) - mean_of(A10[:4]), 1)}",
    verify=f"it falls by {round(250 / 5 - 180 / 4, 1)}",
    wrong=[(f"it rises by {round(mean_of(A10) - mean_of(A10[:4]), 1)}", "inverse"),
           (f"it falls by {round(70 - mean_of(A10), 1)}", "operation_swap"),
           ("it does not change", "ignored_constraint")],
    difficulty="hard", confidence=0.91,
    expl="All five total 250 for a mean of 50; the remaining four total 180 for a mean of "
         "45, so the mean falls by 5. It rises by 5 gets the direction backwards, since "
         "removing the largest value must pull the mean down, and 20 is the gap between "
         "that value and the original mean rather than the shift.",
    fmt=PLAIN),

A11 = [1, 3, 3, 4, 9]
B.Q("summary_statistics", "single_step",
    "For the values 1, 3, 3, 4 and 9, what is the mean?",
    key=mean_of(A11), verify=dev_check(A11, sum(A11) / 5),
    wrong=[(statistics.median(A11), "wrong_attribute"), (sum(A11), "partial_step"),
           (max(A11) - min(A11), "misread_data")],
    expl="The values total 20 and 20 divided by 5 is 4. 3 is both the median and the mode, "
         "20 is the total before dividing, and 8 is the range.",
    fmt=PLAIN),

A12 = [88, 92, 79, 95, 84, 96]
B.Q("summary_statistics", "multi_step",
    "Six test marks were 88, 92, 79, 95, 84 and 96. A seventh mark is added and the mean "
    "of all seven is exactly 88. What was the seventh mark?",
    key=88 * 7 - sum(A12), verify=616 - (88 + 92 + 79 + 95 + 84 + 96),
    wrong=[(88, "ignored_constraint"), (round(mean_of(A12), 1), "partial_step"),
           (sum(A12), "misread_data")],
    difficulty="hard", confidence=0.92,
    expl="Seven marks averaging 88 total 616, and the first six come to 534, so the seventh "
         "is 82. 88 assumes the last mark must equal the target average, 89 is the average "
         "of the first six only, and 534 is their running total.",
    fmt=PLAIN),

A13 = [2, 2, 3, 7, 11]
B.Q("summary_statistics", "single_step",
    "Which value would you change to raise the median of 2, 2, 3, 7 and 11 without "
    "changing the mode?",
    key="the 3", verify="the 3",
    wrong=[("one of the 2s", "ignored_constraint"), ("the 11", "wrong_attribute"),
           ("the 7", "misread_data")],
    difficulty="hard", confidence=0.89,
    expl="The median is the middle value, 3, so raising it lifts the median directly. "
         "Changing a 2 would break the mode, raising the 11 leaves the middle value where "
         "it is, and the 7 sits above the median so moving it up changes nothing.",
    fmt=PLAIN),

A14 = [15, 15, 15, 15]
B.Q("summary_statistics", "single_step",
    "Four identical readings of 15 are recorded. What is the range of this data?",
    key=max(A14) - min(A14), verify=15 - 15,
    wrong=[(15, "wrong_attribute"), (len(A14), "misread_data"), (sum(A14), "partial_step")],
    expl="Every reading is the same, so the largest and smallest are both 15 and the range "
         "is 0. 15 is the value itself, which is also the mean, median and mode here, 4 is "
         "the number of readings, and 60 is their total.",
    fmt=PLAIN),

A15 = [23, 19, 31, 27]
B.Q("summary_statistics", "multi_step",
    "Four readings are 23, 19, 31 and 27. What must a fifth reading be for the mean of all "
    "five to equal the median of the original four?",
    key=25 * 5 - sum(A15), verify=125 - 100,
    wrong=[(125, "partial_step"), (sum(A15), "misread_data"), (statistics.median(A15) * 4 - sum(A15), "off_by_one")],
    difficulty="hard", confidence=0.90,
    expl="Sorted, the four readings are 19, 23, 27, 31, so their median is 25. Five readings "
         "averaging 25 must total 125, and the four given come to 100, so the fifth is 25. "
         "125 is the required total rather than the missing reading, 100 is what the four "
         "already give, and 0 comes from using four readings instead of five.",
    fmt=PLAIN),


if __name__ == "__main__":
    B.write()
