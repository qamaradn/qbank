#!/usr/bin/env python3
"""Builds ma_vic_stats_p5.json — 12 two-way table / Venn items and 12 on data and bias.

    MA_BOOK=ma_vic_stats env -u PYTHONPATH .venv/bin/python3.11 tools/ma/ma_vic_p5_build.py

Completes the 100-item VIC Statistics and Probability top-up.

Two-way tables carry a figure and every total is recomputed from the cells rather than
typed, so a table cannot disagree with its own margins. The characteristic error here is
double_count -- adding two overlapping groups without removing the overlap -- and it is
the distractor that matters most.

Data and bias items have no single numeric answer, so `verify` restates the key through
the property that makes it right (the sampling frame that excludes the affected group,
the axis that does not start at zero) rather than by a second calculation.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.figure_lib import table  # noqa: E402
from tools.ma.ma_common import Batch, PLAIN, unit  # noqa: E402

B = Batch(nn=5)

# ---- two-way table: sport by year level -------------------------------------
# cells then margins, so the margins cannot be typed wrong
Y8_S, Y8_N, Y9_S, Y9_N = 24, 16, 18, 22
ROW8, ROW9 = Y8_S + Y8_N, Y9_S + Y9_N
COL_S, COL_N = Y8_S + Y9_S, Y8_N + Y9_N
GRAND = ROW8 + ROW9
SPORT_TBL = table([["", "Plays sport", "Does not", "Total"],
                   ["Year 8", str(Y8_S), str(Y8_N), str(ROW8)],
                   ["Year 9", str(Y9_S), str(Y9_N), str(ROW9)],
                   ["Total", str(COL_S), str(COL_N), str(GRAND)]])

B.Q("two_way_venn", "data_interpretation",
    "The two-way table records whether students in two year levels play a sport. How many "
    "Year 9 students do not play a sport?",
    key=Y9_N, verify=ROW9 - Y9_S,
    wrong=[(Y8_N, "misread_data"), (COL_N, "partial_step"), (Y9_S, "inverse")],
    expl="The Year 9 row shows 22 students not playing a sport, which also checks out as "
         "the row total of 40 less the 18 who do. 16 reads the Year 8 row, 38 is the column "
         "total for all students not playing, and 18 is the Year 9 students who do play.",
    fig=SPORT_TBL, fmt=unit("students")),

B.Q("two_way_venn", "data_interpretation",
    "Using the same table, how many students were surveyed altogether?",
    key=GRAND, verify=COL_S + COL_N,
    wrong=[(ROW8, "partial_step"), (COL_S, "misread_data"), (COL_N, "off_by_one")],
    expl="Adding the two row totals gives 40 plus 40, which is 80, and the column totals of "
         "42 and 38 come to the same. 40 is one year level only, 42 is the number who play "
         "a sport, and 38 the number who do not.",
    fig=SPORT_TBL, fmt=unit("students")),

B.Q("two_way_venn", "multi_step",
    "Using the same table, what fraction of the Year 8 students play a sport?",
    key=f"{Y8_S} out of {ROW8}", verify=f"{ROW8 - Y8_N} out of {ROW8}",
    wrong=[(f"{Y8_S} out of {GRAND}", "misread_data"), (f"{COL_S} out of {GRAND}", "wrong_attribute"),
           (f"{Y8_S} out of {COL_S}", "off_by_one")],
    difficulty="hard", confidence=0.92,
    expl="Of the 40 Year 8 students, 24 play a sport, so 24 out of 40. 24 out of 80 uses the "
         "whole survey as the total, 42 out of 80 is the figure for both year levels, and 24 "
         "out of 42 compares Year 8 players with all players.",
    fig=SPORT_TBL, fmt=PLAIN),

B.Q("two_way_venn", "multi_step",
    "Using the same table, a student is chosen at random from the whole survey. What is the "
    "probability that they are in Year 9 AND play a sport?",
    key=f"{Y9_S} out of {GRAND}", verify=f"{COL_S - Y8_S} out of {ROW8 + ROW9}",
    wrong=[(f"{Y9_S} out of {ROW9}", "misread_data"), (f"{ROW9} out of {GRAND}", "partial_step"),
           (f"{COL_S} out of {GRAND}", "ignored_constraint")],
    difficulty="hard", confidence=0.92,
    expl="Eighteen students are both in Year 9 and playing a sport, out of 80 altogether. "
         "18 out of 40 restricts the total to Year 9 when the student is drawn from everyone, "
         "40 out of 80 is the chance of being in Year 9 at all, and 42 out of 80 drops the "
         "year-level condition.",
    fig=SPORT_TBL, fmt=PLAIN),

B.Q("two_way_venn", "multi_step",
    "Using the same table, which year level has the higher proportion of sport players?",
    key="Year 8", verify="Year 8" if Y8_S / ROW8 > Y9_S / ROW9 else "Year 9",
    wrong=[("Year 9", "inverse"), ("they are equal", "misread_data"),
           ("it cannot be worked out from the table", "ignored_constraint")],
    expl="Year 8 has 24 of 40 playing, which is three fifths, against Year 9's 18 of 40, "
         "which is under half, so Year 8 is higher. The two row totals happen to be equal at "
         "40, which is what makes the comparison quick.",
    fig=SPORT_TBL, fmt=PLAIN),

B.Q("two_way_venn", "multi_step",
    "Using the same table, how many more Year 8 than Year 9 students play a sport?",
    key=Y8_S - Y9_S, verify=24 - 18,
    wrong=[(Y8_S + Y9_S, "operation_swap"), (Y8_N - Y9_N, "misread_data"),
           (Y8_S, "partial_step")],
    expl="Year 8 has 24 players and Year 9 has 18, a difference of 6. 42 adds the two "
         "instead of subtracting, minus 6 reads the non-players column, and 24 is the Year 8 "
         "figure on its own.",
    fig=SPORT_TBL, fmt=unit("students")),

# ---- Venn: two overlapping clubs --------------------------------------------
ONLY_D, BOTH, ONLY_C, NEITHER = 14, 9, 11, 6
VTOT = ONLY_D + BOTH + ONLY_C + NEITHER
VENN_TBL = table([["Group", "Students"],
                  ["Debating only", str(ONLY_D)],
                  ["Both clubs", str(BOTH)],
                  ["Chess only", str(ONLY_C)],
                  ["Neither club", str(NEITHER)]])

B.Q("two_way_venn", "data_interpretation",
    "The summary lists how many students in one class belong to the debating and chess "
    "clubs. How many students belong to the debating club in total?",
    key=ONLY_D + BOTH, verify=23,
    wrong=[(ONLY_D, "partial_step"), (ONLY_D + BOTH + ONLY_C, "double_count"),
           (BOTH, "misread_data")],
    expl="Fourteen are in debating only and nine are in both, so 23 belong to debating "
         "altogether. 14 leaves out the students in both clubs, 34 adds the chess-only group "
         "as well, and 9 counts only the overlap.",
    fig=VENN_TBL, fmt=unit("students")),

B.Q("two_way_venn", "multi_step",
    "Using the same summary, how many students are in at least one of the two clubs?",
    key=ONLY_D + BOTH + ONLY_C, verify=VTOT - NEITHER,
    wrong=[(ONLY_D + ONLY_C, "partial_step"), (ONLY_D + BOTH + ONLY_C + BOTH, "double_count"),
           (VTOT, "ignored_constraint")],
    difficulty="hard", confidence=0.92,
    expl="Adding the three club groups gives 14 plus 9 plus 11, which is 34, and that also "
         "equals the class of 40 less the 6 in neither. 25 leaves out the overlap entirely, "
         "43 counts the overlap twice, and 40 is the whole class including those in no club.",
    fig=VENN_TBL, fmt=unit("students")),

B.Q("two_way_venn", "data_interpretation",
    "How many students does that class contain altogether?",
    key=VTOT, verify=ONLY_D + BOTH + ONLY_C + NEITHER,
    wrong=[(ONLY_D + BOTH + ONLY_C, "partial_step"), (ONLY_D + ONLY_C + NEITHER, "misread_data"),
           (VTOT + BOTH, "double_count")],
    expl="All four groups together make 14 plus 9 plus 11 plus 6, which is 40. 34 leaves out "
         "the students in neither club, 31 leaves out the overlap, and 49 counts the overlap "
         "a second time.",
    fig=VENN_TBL, fmt=unit("students")),

B.Q("two_way_venn", "multi_step",
    "Using the same summary, a student is picked at random from the class. What is the "
    "probability that they are in exactly one club?",
    key=f"{ONLY_D + ONLY_C} out of {VTOT}", verify=f"{VTOT - BOTH - NEITHER} out of {VTOT}",
    wrong=[(f"{ONLY_D + BOTH + ONLY_C} out of {VTOT}", "double_count"),
           (f"{BOTH} out of {VTOT}", "inverse"),
           (f"{ONLY_D + ONLY_C} out of {ONLY_D + BOTH + ONLY_C}", "misread_data")],
    difficulty="hard", confidence=0.91,
    expl="Exactly one club means debating only or chess only, so 14 plus 11 is 25 out of 40. "
         "34 out of 40 includes the students in both, 9 out of 40 is the chance of being in "
         "both, and 25 out of 34 leaves the no-club students out of the total.",
    fig=VENN_TBL, fmt=PLAIN),

B.Q("two_way_venn", "multi_step",
    "For that same class, by how many does debating membership exceed chess membership?",
    key=(ONLY_D + BOTH) - (ONLY_C + BOTH), verify=ONLY_D - ONLY_C,
    wrong=[(ONLY_D + BOTH, "partial_step"), (BOTH, "misread_data"),
           ((ONLY_D + BOTH) + (ONLY_C + BOTH), "operation_swap")],
    expl="Debating has 23 members and chess has 20, a difference of 3, which is also just "
         "the gap between the two 'only' groups since the overlap counts in both. 23 is the "
         "debating total alone and 43 adds the two clubs together.",
    fig=VENN_TBL, fmt=unit("students")),

B.Q("two_way_venn", "multi_step",
    "Using the same summary, what fraction of the debating club members are also in chess?",
    key=f"{BOTH} out of {ONLY_D + BOTH}", verify=f"{BOTH} out of {23}",
    wrong=[(f"{BOTH} out of {VTOT}", "misread_data"),
           (f"{BOTH} out of {ONLY_C + BOTH}", "off_by_one"),
           (f"{ONLY_D} out of {ONLY_D + BOTH}", "inverse")],
    difficulty="hard", confidence=0.91,
    expl="Of the 23 debating members, 9 are also in chess, so 9 out of 23. 9 out of 40 uses "
         "the whole class as the total, 9 out of 20 uses the chess membership instead, and "
         "14 out of 23 is the fraction who are in debating only.",
    fig=VENN_TBL, fmt=PLAIN),

# ---- data collection, bias and misleading displays (12) ----------------------

B.Q("data_and_bias", "single_step",
    "A school wants to know how students travel to school. Which method would give the "
    "least biased result?",
    key="surveying every tenth student on the whole roll",
    verify="surveying every tenth student on the whole roll",
    wrong=[("surveying students in the bike shed", "ignored_constraint"),
           ("surveying students who arrive after 8:45", "misread_data"),
           ("surveying the school captains", "wrong_attribute")],
    expl="Taking every tenth name from the full roll gives every student the same chance of "
         "being asked. Surveying the bike shed reaches cyclists only, surveying late arrivals "
         "picks a group whose travel may be the reason they are late, and the captains are "
         "far too small and unrepresentative a group.",
    fmt=PLAIN),

B.Q("data_and_bias", "single_step",
    "A shop asks customers leaving the store whether they are happy with the service. Why "
    "might this sample be biased?",
    key="people who had a bad experience may have left already",
    verify="people who had a bad experience may have left already",
    wrong=[("the sample is too large to analyse", "wrong_attribute"),
           ("customers cannot remember the service", "misread_data"),
           ("the question is about service rather than price", "ignored_constraint")],
    expl="Anyone who walked out in frustration is never asked, so the sample is missing "
         "exactly the opinions that would lower the result. Sample size is not the problem "
         "here, and asking about service rather than price is a choice of topic, not a bias.",
    fmt=PLAIN),

B.Q("data_and_bias", "single_step",
    "A bar chart is drawn with its vertical axis starting at 90 rather than 0. What is the "
    "likely effect on a reader?",
    key="small differences between bars will look large",
    verify="small differences between bars will look large",
    wrong=[("the bars will all appear the same height", "inverse"),
           ("the total of the bars will be wrong", "wrong_attribute"),
           ("the chart will be easier to read accurately", "misread_data")],
    expl="Cutting off the bottom of the scale magnifies whatever variation remains, so a gap "
         "of two units can fill half the display. That the bars will all appear the same height "
         "is the opposite of what happens, and the total of the bars will be wrong is not "
         "true either -- the numbers are right and only the picture misleads.",
    fmt=PLAIN),

B.Q("data_and_bias", "single_step",
    "A survey question reads: 'Do you agree that the unfair new parking fees should be "
    "scrapped?' What is wrong with it?",
    key="it is worded to push the respondent towards one answer",
    verify="it is worded to push the respondent towards one answer",
    wrong=[("it asks about two things at once", "misread_data"),
           ("it is too short to be understood", "wrong_attribute"),
           ("it does not offer a numerical scale", "ignored_constraint")],
    expl="Calling the fees unfair inside the question invites agreement before the "
         "respondent has decided anything. It asks about one thing, its length is not the "
         "problem, and a scale would not fix loaded wording.",
    fmt=PLAIN),

B.Q("data_and_bias", "single_step",
    "A council posts an online poll about a new skate park on its social media page. Which "
    "group is most likely to be under-represented?",
    key="residents who do not use social media",
    verify="residents who do not use social media",
    wrong=[("residents who own a skateboard", "inverse"),
           ("residents living closest to the site", "misread_data"),
           ("residents who read the council newsletter", "wrong_attribute")],
    expl="An online poll can only reach the people who see it, so anyone off that platform is "
         "silently excluded. Skateboarders are if anything over-represented, and proximity to "
         "the site has nothing to do with who sees the post.",
    fmt=PLAIN),

B.Q("data_and_bias", "multi_step",
    "A report says 'sales doubled' when the figures behind it rise from 40 to 48. What is "
    "the actual percentage increase?",
    key=round((48 - 40) / 40 * 100), verify=round(8 / 40 * 100),
    wrong=[(100, "ignored_constraint"), (8, "partial_step"), (round(48 / 40 * 100), "misread_data")],
    difficulty="hard", confidence=0.92,
    expl="The rise of 8 on a starting value of 40 is 20 per cent, nowhere near doubling. "
         "100 per cent is what doubling would mean, 8 is the rise itself rather than a "
         "percentage, and 120 per cent is the new figure as a share of the old.",
    fmt=unit("per cent")),

B.Q("data_and_bias", "single_step",
    "Which sample would best represent the views of all 800 students at a school?",
    key="80 students chosen at random from the full roll",
    verify="80 students chosen at random from the full roll",
    wrong=[("80 students from the two Year 12 classes", "ignored_constraint"),
           ("the first 80 students to reply to an email", "misread_data"),
           ("800 students from a neighbouring school", "wrong_attribute")],
    expl="A random tenth of the roll gives every student an equal chance of selection. Two "
         "Year 12 classes leave out five other year levels, the first 80 students to reply to "
         "an email are the keenest rather than the typical, and 800 students from a "
         "neighbouring school are not this school's students at all.",
    fmt=PLAIN),

B.Q("data_and_bias", "single_step",
    "A pictogram uses one drawing of a tree to stand for 10 trees planted. One row shows "
    "three and a half trees. How many trees does that row represent?",
    key=35, verify=3 * 10 + 5,
    wrong=[(3.5, "partial_step"), (30, "rounding"), (310, "place_value")],
    expl="Three whole symbols are 30 trees and the half symbol adds 5, giving 35. 3.5 is the "
         "number of symbols rather than trees, 30 ignores the half, and 310 misreads the "
         "scale entirely.",
    fmt=unit("trees")),

B.Q("data_and_bias", "single_step",
    "Two classes are compared using pie charts of the same size, but one class has 20 "
    "students and the other 40. What can the pie charts NOT show?",
    key="how many students are in each class",
    verify="how many students are in each class",
    wrong=[("the proportion in each category", "inverse"),
           ("which category is largest in each class", "misread_data"),
           ("whether the categories are the same in both", "wrong_attribute")],
    expl="A pie chart shows shares of its own whole, so two equal-sized circles hide the fact "
         "that one whole is twice the other. The proportion in each category and which category "
         "is largest in each class are exactly what such a display does show.",
    fmt=PLAIN),

B.Q("data_and_bias", "multi_step",
    "A newspaper reports that 90 per cent of readers support a proposal, based on 50 replies "
    "to a printed coupon. Which criticism is strongest?",
    key="only readers who felt strongly would post a coupon",
    verify="only readers who felt strongly would post a coupon",
    wrong=[("90 per cent of 50 is not a whole number", "wrong_attribute"),
           ("the sample should have been exactly 100", "misread_data"),
           ("percentages should not be used for opinions", "ignored_constraint")],
    difficulty="hard", confidence=0.91,
    expl="A coupon that has to be cut out and posted is answered by the motivated, which is "
         "self-selection rather than sampling. 90 per cent of 50 is 45, a whole number, and "
         "there is nothing special about a sample of exactly 100.",
    fmt=PLAIN),

B.Q("data_and_bias", "single_step",
    "Rainfall for January, February and December is plotted as a line, in that order along "
    "the axis. Why is this misleading?",
    key="the months are not in their natural order",
    verify="the months are not in their natural order",
    wrong=[("rainfall should be shown as a bar chart", "wrong_attribute"),
           ("three months is too few to plot", "misread_data"),
           ("the axis should show days rather than months", "ignored_constraint")],
    expl="A line graph invites the reader to see change over time, and putting December after "
         "February implies a trend that the calendar does not support. A bar chart would also "
         "work, but the ordering is what actually deceives.",
    fmt=PLAIN),

B.Q("data_and_bias", "multi_step",
    "A class of 25 records how many pets each student has, and the mean comes to 1.6. A "
    "newspaper reports that 'the average family has 1.6 pets'. What is the main problem?",
    key="one class of students is not a sample of all families",
    verify="one class of students is not a sample of all families",
    wrong=[("a mean cannot be a decimal", "wrong_attribute"),
           ("the median would have been larger", "misread_data"),
           ("25 students is too many to survey", "ignored_constraint")],
    expl="The finding describes 25 students at one school and is reported as though it "
         "described every family, which is a claim the sample cannot support. A mean of 1.6 "
         "is perfectly ordinary for counted data, and 25 is a reasonable class-sized sample.",
    fmt=PLAIN),


if __name__ == "__main__":
    B.write()
