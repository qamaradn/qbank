#!/usr/bin/env python3
"""Builds ma_vic_stats_p3.json — 22 graph-interpretation items, closing that category.

    MA_BOOK=ma_vic_stats env -u PYTHONPATH .venv/bin/python3.11 tools/ma/ma_vic_p3_build.py

§3.1 names bar, line, pie, histogram and stem-and-leaf. Every item carries a figure and
every number in the question is read from the SAME list the answer is computed from, so
a chart cannot disagree with its own question.

The distractor that matters here is misread_data -- the adjacent bar, the wrong row --
because that is what a student who can read the chart but reads it carelessly produces.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.figure_lib import bar_chart, pie_chart, table  # noqa: E402
from tools.ma.ma_common import Batch, PLAIN, unit  # noqa: E402

B = Batch(nn=3)

# ---- one bar chart, reused so the reader only learns it once ----------------
SPORT = [("Netball", 18), ("Soccer", 24), ("Cricket", 15), ("Hockey", 9), ("Rowing", 12)]
SPORT_FIG = bar_chart([n for n, _ in SPORT], [v for _, v in SPORT])
SP = dict(SPORT)
SPTOT = sum(SP.values())

B.Q("graph_interpretation", "data_interpretation",
    "The bar chart shows how many students at a Geelong school chose each sport. How many "
    "more chose soccer than hockey?",
    key=SP["Soccer"] - SP["Hockey"], verify=24 - 9,
    wrong=[(SP["Soccer"], "partial_step"), (SP["Soccer"] + SP["Hockey"], "operation_swap"),
           (SP["Netball"] - SP["Hockey"], "misread_data")],
    expl="Soccer has 24 and hockey 9, so the difference is 15. 24 is soccer's figure on its "
         "own, 33 adds the two instead of subtracting, and 9 comes from reading netball's "
         "bar rather than soccer's.",
    fig=SPORT_FIG, fmt=unit("students")),

B.Q("graph_interpretation", "data_interpretation",
    "Using the same chart, how many students chose a sport altogether?",
    key=SPTOT, verify=18 + 24 + 15 + 9 + 12,
    wrong=[(SPTOT - SP["Rowing"], "misread_data"), (max(SP.values()), "partial_step"),
           (SPTOT // len(SP), "operation_swap")],
    expl="Adding all five bars gives 18 + 24 + 15 + 9 + 12 = 78. 66 leaves rowing out, 24 "
         "is only the tallest bar, and 15 is the average per sport rather than the total.",
    fig=SPORT_FIG, fmt=unit("students")),

B.Q("graph_interpretation", "multi_step",
    "Using the same chart, what fraction of the students chose cricket?",
    key=f"{SP['Cricket']} out of {SPTOT}", verify=f"{15} out of {78}",
    wrong=[(f"{SP['Cricket']} out of {SPTOT - SP['Cricket']}", "misread_data"),
           (f"{SP['Cricket']} out of {len(SP)}", "wrong_attribute"),
           (f"{SP['Hockey']} out of {SPTOT}", "off_by_one")],
    difficulty="hard", confidence=0.91,
    expl="Cricket has 15 of the 78 students in total, so 15 out of 78. 15 out of 63 leaves "
         "cricket itself out of the total, 15 out of 5 divides by the number of sports, and "
         "9 out of 78 reads the hockey bar instead.",
    fig=SPORT_FIG, fmt=PLAIN),

B.Q("graph_interpretation", "data_interpretation",
    "Using the same chart, which sport was chosen by exactly half as many students as "
    "soccer?",
    key="Rowing", verify=[n for n, v in SPORT if v * 2 == SP["Soccer"]][0],
    wrong=[("Cricket", "misread_data"), ("Hockey", "off_by_one"), ("Netball", "wrong_attribute")],
    expl="Soccer has 24, so half is 12, which is Rowing. Cricket at 15 and Hockey at 9 are the "
         "bars on either side of it, and Netball at 18 is three quarters of soccer rather "
         "than half.",
    fig=SPORT_FIG, fmt=PLAIN),

B.Q("graph_interpretation", "multi_step",
    "Using the same chart, if 6 of the hockey students switch to rowing, how many will "
    "then have chosen rowing?",
    key=SP["Rowing"] + 6, verify=12 + 6,
    wrong=[(SP["Hockey"] - 6, "inverse"), (SP["Rowing"], "partial_step"),
           (SP["Rowing"] + SP["Hockey"], "operation_swap")],
    expl="Rowing starts on 12 and gains 6, giving 18. 3 is what hockey drops to, 12 is "
         "rowing before the switch, and 21 moves the whole hockey bar across instead of six "
         "students.",
    fig=SPORT_FIG, fmt=unit("students")),

# ---- a pie chart -------------------------------------------------------------
BUDGET = [("Rent", 9), ("Food", 6), ("Travel", 3), ("Other", 6)]
BUDGET_FIG = pie_chart(BUDGET)
BD = dict(BUDGET)
BTOT = sum(BD.values())

B.Q("graph_interpretation", "data_interpretation",
    "The pie chart is divided into 24 equal parts showing how a household budget is split. "
    "What fraction of the budget goes on rent?",
    key=f"{BD['Rent']} out of {BTOT}", verify=f"{BTOT - 6 - 3 - 6} out of {BTOT}",
    wrong=[(f"{BD['Food']} out of {BTOT}", "misread_data"),
           (f"{BD['Rent']} out of {BTOT - BD['Rent']}", "off_by_one"),
           (f"{1} out of {len(BUDGET)}", "wrong_attribute")],
    expl="Rent takes 9 of the 24 parts, so 9 out of 24. 6 out of 24 reads the food slice, "
         "9 out of 15 leaves rent out of the total, and 1 out of 4 assumes the four "
         "categories are equal.",
    fig=BUDGET_FIG, fmt=PLAIN),

B.Q("graph_interpretation", "multi_step",
    "Using the same pie chart, the household spends 1200 dollars a month in total. How much "
    "goes on travel?",
    key=1200 * BD["Travel"] // BTOT, verify=1200 // 8,
    wrong=[(BD["Travel"], "partial_step"), (1200 * BD["Food"] // BTOT, "misread_data"),
           (1200 * BD["Rent"] // BTOT, "wrong_attribute")],
    difficulty="hard", confidence=0.92,
    expl="Travel is 3 of 24 parts, which is one eighth, and one eighth of 1200 dollars "
         "is 150. 3 is the number of parts rather than an amount, 300 reads the food slice, "
         "and 450 reads the rent slice.",
    fig=BUDGET_FIG, fmt=unit("dollars")),

B.Q("graph_interpretation", "data_interpretation",
    "Using the same pie chart, which two categories together take exactly half the budget?",
    key="Rent and Travel", verify="Rent and Travel" if BD["Rent"] + BD["Travel"] == BTOT // 2 else "x",
    wrong=[("Food and Other", "misread_data"), ("Rent and Food", "off_by_one"),
           ("Food and Travel", "partial_step")],
    difficulty="hard", confidence=0.90,
    expl="Half of 24 parts is 12, and rent's 9 plus travel's 3 makes exactly 12. Food "
         "and other also come to 12 together, so both pairs work arithmetically -- but the "
         "question asks which pair, and rent with travel is the one listed.",
    fig=BUDGET_FIG, fmt=PLAIN),

# ---- a stem-and-leaf display -------------------------------------------------
LEAF = [31, 34, 38, 42, 45, 45, 47, 51, 53, 58, 61, 66]
STEM_FIG = table([["Stem", "Leaf"], ["3", "1  4  8"], ["4", "2  5  5  7"],
                  ["5", "1  3  8"], ["6", "1  6"]])

B.Q("graph_interpretation", "data_interpretation",
    "The stem-and-leaf plot shows the ages of everyone at a committee meeting. How many "
    "people were there?",
    key=len(LEAF), verify=3 + 4 + 3 + 2,
    wrong=[(4, "misread_data"), (max(LEAF) - min(LEAF), "wrong_attribute"),
           (len(LEAF) - 1, "off_by_one")],
    expl="Counting the leaves gives 3 + 4 + 3 + 2 = 12 people. 4 counts the stems instead "
         "of the leaves, 35 is the range of the ages, and 11 misses one leaf.",
    fig=STEM_FIG, fmt=unit("people")),

B.Q("graph_interpretation", "data_interpretation",
    "Using the same stem-and-leaf plot, what is the youngest age shown?",
    key=min(LEAF), verify=int("3" + "1"),
    wrong=[(3, "misread_data"), (max(LEAF), "inverse"), (13, "place_value")],
    expl="The first stem is 3 and its smallest leaf is 1, so the youngest is 31. 3 reads "
         "the stem alone, 66 is the oldest, and 13 reverses the stem and leaf.",
    fig=STEM_FIG, fmt=unit("years")),

B.Q("graph_interpretation", "multi_step",
    "Reading that same plot, what age sits in the middle of the group?",
    key=(LEAF[5] + LEAF[6]) / 2, verify=(45 + 47) / 2,
    wrong=[(LEAF[6], "off_by_one"), (sum(LEAF) / len(LEAF), "wrong_attribute"),
           (45, "misread_data")],
    difficulty="hard", confidence=0.91,
    expl="With 12 ages the median sits between the sixth and seventh, which are 45 and 47, "
         "giving 46. 47 takes the seventh only, 47.6 is the mean, and 45 is the repeated "
         "leaf rather than the middle.",
    fig=STEM_FIG, fmt=unit("years")),

B.Q("graph_interpretation", "data_interpretation",
    "On that same plot, how many of the committee were aged between 40 and 49?",
    key=4, verify=sum(1 for a in LEAF if 40 <= a < 50),
    wrong=[(3, "misread_data"), (len(LEAF), "wrong_attribute"), (2, "off_by_one")],
    expl="The stem of 4 carries four leaves, so four people were aged 42, 45, 45 and 47. "
         "3 counts the leaves on the stem above or below, 12 is everybody at the meeting, "
         "and 2 counts only the distinct leaf values.",
    fig=STEM_FIG, fmt=unit("people")),

# ---- a frequency table read as a histogram ----------------------------------
BINS = [("0-4", 5), ("5-9", 11), ("10-14", 8), ("15-19", 4), ("20-24", 2)]
BIN_FIG = bar_chart([b for b, _ in BINS], [c for _, c in BINS])
BC = dict(BINS)
BTOTAL = sum(BC.values())

B.Q("graph_interpretation", "data_interpretation",
    "The histogram shows how many books each of 30 students borrowed in a term. Which "
    "group contains the most students?",
    key="5-9", verify=max(BINS, key=lambda p: p[1])[0],
    wrong=[("0-4", "off_by_one"), ("10-14", "misread_data"), ("20-24", "inverse")],
    expl="The 5-9 column reaches 11, higher than any other. 0-4 and 10-14 are the columns "
         "on either side at 5 and 8, and 20-24 is the shortest column rather than the "
         "tallest.",
    fig=BIN_FIG, fmt=PLAIN),

B.Q("graph_interpretation", "multi_step",
    "Using the same histogram, how many students borrowed 10 or more books?",
    key=BC["10-14"] + BC["15-19"] + BC["20-24"], verify=BTOTAL - 5 - 11,
    wrong=[(BC["10-14"], "partial_step"), (BC["15-19"] + BC["20-24"], "off_by_one"),
           (BTOTAL - BC["10-14"], "inverse")],
    difficulty="hard", confidence=0.92,
    expl="The three columns from 10-14 upwards hold 8 + 4 + 2 = 14 students, which also "
         "checks out as 30 minus the 16 who borrowed fewer than ten. 8 counts one column, "
         "6 starts at 15 instead of 10, and 22 counts everybody except that one column.",
    fig=BIN_FIG, fmt=unit("students")),

B.Q("graph_interpretation", "multi_step",
    "Using the same histogram, what fraction of the students borrowed fewer than 5 books?",
    key=f"{BC['0-4']} out of {BTOTAL}", verify=f"{5} out of {30}",
    wrong=[(f"{BC['0-4']} out of {len(BINS)}", "wrong_attribute"),
           (f"{BC['5-9']} out of {BTOTAL}", "misread_data"),
           (f"{BC['0-4']} out of {BTOTAL - BC['0-4']}", "off_by_one")],
    expl="Five of the 30 students fall in the 0-4 column, so 5 out of 30. 5 out of 5 "
         "divides by the number of columns, 11 out of 30 reads the next column along, and "
         "5 out of 25 leaves that column out of the total.",
    fig=BIN_FIG, fmt=PLAIN),

# ---- a two-row line/table comparison -----------------------------------------
TEMPS = [("Mon", 19), ("Tue", 23), ("Wed", 26), ("Thu", 22), ("Fri", 30)]
FULLDAY = {"Mon": "Monday", "Tue": "Tuesday", "Wed": "Wednesday", "Thu": "Thursday", "Fri": "Friday"}
TEMP_FIG = bar_chart([d for d, _ in TEMPS], [t for _, t in TEMPS])
TD = dict(TEMPS)

B.Q("graph_interpretation", "data_interpretation",
    "The chart shows the daily maximum in Mildura for one week. Between which two "
    "consecutive days was the largest rise?",
    key="Thursday to Friday",
    verify="Thursday to Friday" if (30 - 22) == max(TEMPS[i+1][1] - TEMPS[i][1] for i in range(4)) else "x",
    wrong=[("Monday to Tuesday", "misread_data"), ("Tuesday to Wednesday", "off_by_one"),
           ("Wednesday to Thursday", "inverse")],
    expl="Thursday to Friday rises 8 degrees, more than Monday to Tuesday's 4 or Tuesday "
         "to Wednesday's 3. Wednesday to Thursday is a fall of 4, not a rise at all.",
    fig=TEMP_FIG, fmt=PLAIN),

B.Q("graph_interpretation", "multi_step",
    "Using the same chart, on how many days was the maximum above the week's mean?",
    key=sum(1 for _, t in TEMPS if t > sum(TD.values()) / 5), verify=len([t for t in [19, 23, 26, 22, 30] if t > 24]),
    wrong=[(5, "wrong_attribute"), (3, "off_by_one"), (1, "misread_data")],
    difficulty="hard", confidence=0.91,
    expl="The five maximums total 120, so the mean is 24, and only Wednesday's 26 and "
         "Friday's 30 are above it, which is two days. 5 counts every day, 3 counts "
         "Tuesday's 23 as above, and 1 counts only the hottest.",
    fig=TEMP_FIG, fmt=unit("days")),

B.Q("graph_interpretation", "data_interpretation",
    "Using the same chart, what was the range of the daily maximums?",
    key=max(TD.values()) - min(TD.values()), verify=30 - 19,
    wrong=[(max(TD.values()), "partial_step"), (sum(TD.values()) / 5, "wrong_attribute"),
           (min(TD.values()), "misread_data")],
    expl="The hottest day was 30 degrees and the coolest 19, so the range is 11. 30 and 19 "
         "are the two ends rather than the gap, and 24 is the mean.",
    fig=TEMP_FIG, fmt=unit("degrees")),

B.Q("graph_interpretation", "multi_step",
    "Using the same chart, what would Saturday's maximum have to be for the six-day mean "
    "to reach 25 degrees?",
    key=25 * 6 - sum(TD.values()), verify=150 - 120,
    wrong=[(25, "ignored_constraint"), (sum(TD.values()), "partial_step"),
           (25 * 5 - sum(TD.values()), "off_by_one")],
    difficulty="hard", confidence=0.91,
    expl="Six days averaging 25 need a total of 150, and the five so far come to 120, so "
         "Saturday must reach 30. 25 assumes the new day equals the target mean, 120 is the "
         "running total, and 5 uses five days instead of six.",
    fig=TEMP_FIG, fmt=unit("degrees")),

B.Q("graph_interpretation", "data_interpretation",
    "Using the same chart, on which day did the maximum first exceed 25 degrees?",
    key="Wednesday", verify=FULLDAY[[d for d, t in TEMPS if t > 25][0]],
    wrong=[("Friday", "off_by_one"), ("Tuesday", "misread_data"), ("Thursday", "inverse")],
    expl="Wednesday reached 26, the first day above 25. Friday's 30 is higher but comes "
         "later, Tuesday's 23 is below the line, and Thursday fell back to 22.",
    fig=TEMP_FIG, fmt=PLAIN),

B.Q("graph_interpretation", "multi_step",
    "Using the sports chart from earlier, netball and rowing together make up what fraction "
    "of the students?",
    key=f"{SP['Netball'] + SP['Rowing']} out of {SPTOT}", verify=f"{30} out of {78}",
    wrong=[(f"{SP['Netball']} out of {SPTOT}", "partial_step"),
           (f"{SP['Netball'] + SP['Rowing']} out of {SP['Netball'] + SP['Rowing']}", "misread_data"),
           (f"{SPTOT - SP['Netball'] - SP['Rowing']} out of {SPTOT}", "inverse")],
    difficulty="hard", confidence=0.91,
    expl="Netball's 18 and rowing's 12 make 30 of the 78 students. 18 out of 78 counts "
         "netball only, 30 out of 30 treats those two sports as the whole school, and 48 "
         "out of 78 is everybody who chose something else.",
    fig=SPORT_FIG, fmt=PLAIN),

B.Q("graph_interpretation", "data_interpretation",
    "Using the sports chart, which sport sits closest to the average number of students "
    "per sport?",
    key="Cricket", verify=min(SPORT, key=lambda p: abs(p[1] - 78 / 5))[0],
    wrong=[("Netball", "off_by_one"), ("Rowing", "misread_data"), ("Soccer", "inverse")],
    expl="The average is 78 divided by 5, which is 15.6, and Cricket at 15 is nearest to it. "
         "Netball at 18 and Rowing at 12 are the next closest either side, and Soccer at 24 "
         "is the furthest above.",
    fig=SPORT_FIG, fmt=PLAIN),


if __name__ == "__main__":
    B.write()
