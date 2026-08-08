#!/usr/bin/env python3
"""Builds ma_nsw_selective_p7.json — 36 Statistics questions (§4.1).

reading charts 18, two-way tables 14, drawing conclusions 4. Statistics reaches 53/71
after this batch, leaving probability 12 and drawing conclusions 6.

Every chart is drawn from the same list of values the question reasons about — a bar
cannot be one height and be marked at another, and a pie sector labelled a quarter is a
quarter because its angle came from the count. The second route is usually a different
way of combining those values: a total by adding across, checked by adding down.

`drawing_conclusions` is deliberately not more arithmetic. Those four ask what a chart
does and does not license you to say, which is where the §4.2 data-interpretation
archetype actually bites.

Years 5-6 content, Year 6 sitting, no calculator.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.figure_lib import bar_chart, line_graph, pie_chart, table  # noqa: E402
from tools.ma.ma_common import Batch, PLAIN, unit  # noqa: E402

B = Batch(nn=7)

# ===================================================== reading charts (18)

# --- Bar chart 1: library borrowings.
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]
BORROW = [12, 18, 9, 21, 15]
BC1 = bar_chart(DAYS, BORROW)

B.Q("reading_charts", "data_interpretation",
    "The column graph shows how many books were borrowed from a school library each day. "
    "On which day were the fewest books borrowed?",
    key=DAYS[BORROW.index(min(BORROW))], verify=min(zip(BORROW, DAYS))[1],
    wrong=[(DAYS[BORROW.index(max(BORROW))], "inverse"), ("Mon", "misread_data"),
           ("Fri", "partial_step")],
    expl="The shortest column is Wednesday's, at 9 books. Thu has the tallest column at "
         "21, which answers the opposite question, and Mon is simply the first day on the "
         "graph rather than the lowest one.",
    fig=BC1, fmt=PLAIN),

B.Q("reading_charts", "data_interpretation",
    "Using the same column graph, how many more books were borrowed on Thursday than on "
    "Wednesday?",
    key=max(BORROW) - min(BORROW), verify=BORROW[3] - BORROW[2],
    wrong=[(max(BORROW) + min(BORROW), "operation_swap"), (max(BORROW), "partial_step"),
           (BORROW[3] - BORROW[1], "misread_data")],
    expl="Thursday shows 21 and Wednesday shows 9, so the difference is 21 - 9 = 12 books. "
         "30 adds the two columns instead of comparing them, and 21 gives Thursday's "
         "figure on its own.",
    fig=BC1, fmt=unit("books")),

B.Q("reading_charts", "data_interpretation",
    "Using the same column graph, how many books were borrowed across the whole week?",
    key=sum(BORROW), verify=sum(BORROW[:3]) + sum(BORROW[3:]),
    wrong=[(sum(BORROW) - min(BORROW), "partial_step"), (max(BORROW) * 5, "ignored_constraint"),
           (sum(BORROW) // 5, "wrong_attribute")],
    difficulty="hard", confidence=0.91,
    expl="Add the five columns: 12 + 18 + 9 + 21 + 15 = 75 books. Grouping them helps "
         "without a calculator: 12 + 18 = 30, 9 + 21 = 30, and 15 more makes 75. 105 "
         "treats every day as Thursday's 21, and 15 is the mean rather than the total.",
    fig=BC1, fmt=unit("books")),

B.Q("reading_charts", "data_interpretation",
    "Using the same column graph, which two days together match Thursday's borrowings "
    "exactly?",
    key="Wednesday and Monday", verify="Wednesday and Monday",   # 9 + 12 = 21
    wrong=[("Monday and Friday", "misread_data"), ("Tuesday and Wednesday", "operation_swap"),
           ("Monday and Tuesday", "partial_step")],
    difficulty="hard", confidence=0.90,
    expl="Thursday shows 21 books. Wednesday's 9 and Monday's 12 add to exactly 21. Monday "
         "and Friday come to 27 and Tuesday and Wednesday come to 27 as well, so neither "
         "pair matches.",
    fig=BC1, fmt=PLAIN),

B.Q("reading_charts", "data_interpretation",
    "Using the same column graph, the mean number of books borrowed per day is 15. On how "
    "many days were more than the mean borrowed?",
    key=sum(1 for v in BORROW if v > 15), verify=len([v for v in BORROW if v > 15]),
    wrong=[(sum(1 for v in BORROW if v >= 15), "off_by_one"),
           (len(BORROW), "ignored_constraint"), (15, "misread_data")],
    difficulty="hard", confidence=0.90,
    expl="Tuesday's 18 and Thursday's 21 are above 15, so 2 days. 3 counts Friday as well, "
         "but Friday is exactly 15 and not more than it; 5 counts every day on the graph; "
         "and 15 gives the mean rather than a number of days.",
    fig=BC1, fmt=unit("days")),

# --- Bar chart 2: rainfall.
MONTHS = ["Jan", "Feb", "Mar", "Apr"]
RAIN = [40, 25, 60, 15]
BC2 = bar_chart(MONTHS, RAIN)

B.Q("reading_charts", "data_interpretation",
    "The column graph shows monthly rainfall in millimetres at a weather station. How much "
    "rain fell in March?",
    key=RAIN[2], verify=max(RAIN),
    wrong=[(RAIN[0], "misread_data"), (RAIN[1], "off_by_one"), (sum(RAIN), "wrong_attribute")],
    expl="March's column reaches 60 mm, the tallest on the graph. 40 reads January's column "
         "and 25 reads February's, both of which sit to the left of March.",
    fig=BC2, fmt=unit("mm")),

B.Q("reading_charts", "data_interpretation",
    "Using the same rainfall graph, March's rainfall is how many times April's?",
    key=RAIN[2] // RAIN[3], verify=next(k for k in range(1, 10) if RAIN[3] * k == RAIN[2]),
    wrong=[(RAIN[2] - RAIN[3], "operation_swap"), (RAIN[2] + RAIN[3], "misread_data"),
           (RAIN[3], "partial_step")],
    difficulty="hard", confidence=0.91,
    expl="March is 60 mm and April is 15 mm, and 60 / 15 = 4, so March had 4 times April's "
         "rain. Check it: 15 x 4 = 60. 45 subtracts the two instead of comparing them by "
         "division, which answers 'how much more' rather than 'how many times'.",
    fig=BC2, fmt=unit("times")),

B.Q("reading_charts", "data_interpretation",
    "Using the same rainfall graph, what fraction of the four months' total rain fell in "
    "January?",
    key=f"{RAIN[0]} out of {sum(RAIN)}", verify=f"{40} out of {40 + 25 + 60 + 15}",
    wrong=[(f"{RAIN[0]} out of {sum(RAIN) - RAIN[0]}", "misread_data"),
           (f"{RAIN[1]} out of {sum(RAIN)}", "off_by_one"),
           (f"{RAIN[0]} out of 4", "wrong_attribute")],
    difficulty="hard", confidence=0.90,
    expl="The four months total 40 + 25 + 60 + 15 = 140 mm, and January had 40 of that: "
         "40 out of 140. 40 out of 100 leaves January's own rain out of the total, and "
         "40 out of 4 divides by the number of months rather than the millimetres.",
    fig=BC2, fmt=PLAIN),

# --- Line graph 1: temperature through a morning.
TIMES = ["9am", "10am", "11am", "12pm", "1pm"]
TEMPS = [14, 17, 21, 24, 22]
LG1 = line_graph(TIMES, TEMPS)

B.Q("reading_charts", "data_interpretation",
    "The line graph shows the temperature through one morning. What was the temperature at "
    "11 am?",
    key=TEMPS[2], verify=sorted(TEMPS)[2],
    wrong=[(TEMPS[1], "off_by_one"), (TEMPS[3], "misread_data"), (max(TEMPS) - min(TEMPS), "wrong_attribute")],
    expl="Follow 11 am up to the line and across: 21 degrees. 17 reads the point one hour "
         "earlier and 24 reads the point one hour later.",
    fig=LG1, fmt=unit("°C")),

B.Q("reading_charts", "data_interpretation",
    "Using the same temperature graph, between which two times did the temperature rise "
    "the most?",
    key="10 am and 11 am", verify="10 am and 11 am",     # a rise of 4, the largest
    wrong=[("9 am and 10 am", "misread_data"), ("11 am and 12 pm", "off_by_one"),
           ("12 pm and 1 pm", "inverse")],
    difficulty="hard", confidence=0.90,
    expl="The rises are 3, 4, 3 and then a fall of 2, so the steepest climb is between "
         "10 am and 11 am. Between 12 pm and 1 pm the line goes down rather than up.",
    fig=LG1, fmt=PLAIN),

B.Q("reading_charts", "data_interpretation",
    "Using the same temperature graph, how much warmer was it at 1 pm than at 9 am?",
    key=TEMPS[-1] - TEMPS[0], verify=22 - 14,
    wrong=[(max(TEMPS) - TEMPS[0], "misread_data"), (TEMPS[-1] + TEMPS[0], "operation_swap"),
           (TEMPS[-1], "partial_step")],
    expl="It was 14 degrees at 9 am and 22 at 1 pm, a rise of 8 degrees. 10 measures up to "
         "the highest point on the graph, at noon, rather than to 1 pm.",
    fig=LG1, fmt=unit("°C")),

B.Q("reading_charts", "data_interpretation",
    "Using the same temperature graph, at how many of the times shown was the temperature "
    "above 20 degrees?",
    key=sum(1 for t in TEMPS if t > 20), verify=len([t for t in TEMPS if t > 20]),
    wrong=[(sum(1 for t in TEMPS if t < 20), "inverse"), (max(TEMPS), "misread_data"),
           (sum(1 for t in TEMPS if t > 20) + 1, "off_by_one")],
    expl="21, 24 and 22 are all above 20, which is 3 of the five times. 2 counts the times "
         "that are below 20 instead, and 24 gives the highest temperature rather than a "
         "count.",
    fig=LG1, fmt=unit("times")),

# --- Line graph 2: two readers.
LDAYS = ["Mon", "Tue", "Wed", "Thu"]
ELLA, SAM = [3, 6, 9, 12], [9, 8, 7, 6]
LG2 = line_graph(LDAYS, {"Ella": ELLA, "Sam": SAM})

B.Q("reading_charts", "data_interpretation",
    "The graph shows how many pages Ella and Sam each read per day. On which day had they "
    "read the same number of pages?",
    key="on none of the days shown", verify="on none of the days shown",
    wrong=[("on Tuesday", "misread_data"), ("on Wednesday", "off_by_one"),
           ("on Monday", "inverse")],
    difficulty="hard", confidence=0.90,
    expl="On Tuesday Ella read 6 and Sam read 8; on Wednesday Ella read 9 and Sam read 7. "
         "The lines swap over between those two days without either day showing an equal "
         "pair. Tuesday is where Sam is still ahead, and Wednesday is where Ella already "
         "is.",
    fig=LG2, fmt=PLAIN),

B.Q("reading_charts", "data_interpretation",
    "Using the same reading graph, how many pages did Ella read on Thursday?",
    key=ELLA[-1], verify=ELLA[0] + 3 * 3,
    wrong=[(SAM[-1], "misread_data"), (ELLA[-2], "off_by_one"), (ELLA[-1] + SAM[-1], "operation_swap")],
    expl="Ella's line is the solid one and it reaches 12 on Thursday. 6 reads Sam's dashed "
         "line at the same point, and 9 reads Ella's line one day earlier.",
    fig=LG2, fmt=unit("pages")),

B.Q("reading_charts", "data_interpretation",
    "Using the same reading graph, whose reading is increasing, and by how much each day?",
    key="Ella, by 3 pages a day", verify="Ella, by 3 pages a day",
    wrong=[("Sam, by 1 page a day", "inverse"), ("Ella, by 4 pages a day", "off_by_one"),
           ("Both, by 3 pages a day", "misread_data")],
    difficulty="hard", confidence=0.91,
    expl="Ella goes 3, 6, 9, 12 — up 3 each day — while Sam goes 9, 8, 7, 6, which is down "
         "by 1 each day rather than up. Ella, by 4 pages a day misreads the steady step in "
         "her line.",
    fig=LG2, fmt=PLAIN),

# --- Pie chart: how students travel to school.
TRAVEL = [("Walk", 6), ("Bus", 3), ("Car", 2), ("Ride", 1)]
PIE = pie_chart(TRAVEL)

B.Q("reading_charts", "data_interpretation",
    "The pie chart shows how a class of 24 students travels to school. Which method is "
    "used by exactly half the class?",
    key="Walk", verify=next(l for l, c in TRAVEL if c * 2 == sum(c for _, c in TRAVEL)),
    wrong=[("Bus", "misread_data"), ("Car", "partial_step"), ("Ride", "inverse")],
    expl="The Walk sector fills half the circle, so half the class walks. The Bus sector "
         "is a quarter of the circle and the Car sector smaller again, so neither can be "
         "half.",
    fig=PIE, fmt=PLAIN),

B.Q("reading_charts", "data_interpretation",
    "Using the same pie chart of 24 students, how many students catch the bus?",
    key=24 * 3 // 12, verify=24 // 4,           # the Bus sector is a quarter of the circle
    wrong=[(3, "misread_data"), (24 // 2, "wrong_attribute"), (24 // 3, "operation_swap")],
    difficulty="hard", confidence=0.91,
    expl="The Bus sector is a quarter of the circle, and a quarter of 24 is 6 students. "
         "12 is half the class, which is the walkers, and 8 divides by 3 rather than "
         "taking a quarter.",
    fig=PIE, fmt=unit("students")),

B.Q("reading_charts", "data_interpretation",
    "Using the same pie chart, which two methods together account for a quarter of the "
    "class?",
    key="Car and Ride", verify="Car and Ride",   # 2 + 1 of 12 parts is a quarter
    wrong=[("Bus and Ride", "misread_data"), ("Walk and Ride", "inverse"),
           ("Bus and Car", "off_by_one")],
    difficulty="hard", confidence=0.90,
    expl="Car takes two parts and Ride one, and together those three parts of twelve make "
         "a quarter of the circle. Bus alone is already a quarter, so Bus and Ride comes "
         "to more than a quarter.",
    fig=PIE, fmt=PLAIN),

# ===================================================== two-way tables (14)

SPORT = table([["", "Netball", "Soccer", "Cricket", "Total"],
               ["Year 5", "12", "18", "10", "40"],
               ["Year 6", "15", "9", "16", "40"],
               ["Total", "27", "27", "26", "80"]])

B.Q("tables_two_way", "data_interpretation",
    "The two-way table shows the sport chosen by every student in Years 5 and 6. How many "
    "Year 6 students chose cricket?",
    key=16, verify=40 - 15 - 9,                  # the rest of the Year 6 row
    wrong=[(10, "misread_data"), (26, "wrong_attribute"), (15, "off_by_one")],
    expl="Follow the Year 6 row across to the Cricket column: 16 students. 10 is the "
         "Year 5 figure for cricket, one row up, and 26 is the cricket total for both "
         "years together.",
    fig=SPORT, fmt=unit("students")),

B.Q("tables_two_way", "data_interpretation",
    "Using the same table, how many students chose netball altogether?",
    key=27, verify=12 + 15,
    wrong=[(12, "partial_step"), (15, "misread_data"), (40, "wrong_attribute")],
    expl="Add down the Netball column: 12 + 15 = 27 students, which is what the Total row "
         "shows. 12 counts Year 5 only, and 40 is the number of students in a year group "
         "rather than in a sport.",
    fig=SPORT, fmt=unit("students")),

B.Q("tables_two_way", "data_interpretation",
    "Using the same table, how many students are there in Years 5 and 6 altogether?",
    key=80, verify=27 + 27 + 26,                 # adding the sport totals must agree
    wrong=[(40, "partial_step"), (27, "misread_data"), (80 - 26, "off_by_one")],
    expl="The grand total is 80. It can be checked two ways: down the year totals, "
         "40 + 40, and across the sport totals, 27 + 27 + 26, both of which give 80. "
         "40 counts one year group only.",
    fig=SPORT, fmt=unit("students")),

B.Q("tables_two_way", "data_interpretation",
    "Using the same table, which sport was chosen by more Year 5 students than Year 6 "
    "students?",
    key="Soccer", verify="Soccer",               # 18 against 9
    wrong=[("Netball", "inverse"), ("Cricket", "misread_data"), ("None of them", "ignored_constraint")],
    difficulty="hard", confidence=0.91,
    expl="Soccer runs 18 in Year 5 against 9 in Year 6, the only sport where the Year 5 "
         "figure is the larger. Netball and cricket both go the other way, 12 against 15 "
         "and 10 against 16.",
    fig=SPORT, fmt=PLAIN),

B.Q("tables_two_way", "data_interpretation",
    "Using the same table, how many more Year 5 students chose soccer than Year 6 students "
    "did?",
    key=18 - 9, verify=27 - 9 - 9,
    wrong=[(18 + 9, "operation_swap"), (18, "partial_step"), (12 - 10, "misread_data")],
    expl="Year 5 shows 18 and Year 6 shows 9, so the difference is 9 students. 27 adds the "
         "two rather than comparing them, which is also why it matches the column total, "
         "and 2 compares the wrong pair of cells — Year 5's netball against Year 5's "
         "cricket.",
    fig=SPORT, fmt=unit("students")),

B.Q("tables_two_way", "data_interpretation",
    "Using the same table, what fraction of Year 5 students chose netball?",
    key="12 out of 40", verify=f"{12} out of {12 + 18 + 10}",
    wrong=[("12 out of 27", "misread_data"), ("12 out of 80", "wrong_attribute"),
           ("27 out of 40", "off_by_one")],
    difficulty="hard", confidence=0.91,
    expl="There are 40 students in Year 5 and 12 of them chose netball: 12 out of 40. "
         "12 out of 27 uses the netball total for both years as the whole, and 12 out of "
         "80 uses the whole school when the question asks about Year 5.",
    fig=SPORT, fmt=PLAIN),

B.Q("tables_two_way", "data_interpretation",
    "Using the same table, which sport is the most popular across both year groups "
    "together?",
    key="Netball and soccer, equal at 27", verify="Netball and soccer, equal at 27",
    wrong=[("Netball, with 27", "partial_step"), ("Cricket, with 26", "misread_data"),
           ("Soccer, with 27", "off_by_one")],
    difficulty="hard", confidence=0.90,
    expl="The totals are netball 27, soccer 27 and cricket 26, so netball and soccer tie "
         "at the top. Netball, with 27 reads the first of the two equal columns and stops "
         "there, and Soccer, with 27 does the same from the other side — neither is the "
         "most popular on its own.",
    fig=SPORT, fmt=PLAIN),

# --- Second two-way table, with a cell to be worked out.
PETS = table([["", "Dog", "Cat", "No pet", "Total"],
              ["Boys", "14", "6", "?", "30"],
              ["Girls", "11", "12", "7", "30"],
              ["Total", "25", "18", "17", "60"]])

B.Q("tables_two_way", "multi_step",
    "The two-way table has one figure missing. How many boys have no pet?",
    key=30 - 14 - 6, verify=17 - 7,              # down the No pet column instead of across
    wrong=[(17, "wrong_attribute"), (30 - 14, "partial_step"), (7, "misread_data")],
    difficulty="hard", confidence=0.91,
    expl="The Boys row must come to 30, and 14 + 6 = 20, so the missing figure is 10. "
         "Checking down the No pet column gives the same: 17 - 7 = 10. 17 is the column "
         "total for both rows, and 7 is the girls' figure.",
    fig=PETS, fmt=unit("boys")),

B.Q("tables_two_way", "data_interpretation",
    "Using the pet table, how many children own a cat?",
    key=18, verify=6 + 12,
    wrong=[(12, "misread_data"), (6, "partial_step"), (25, "wrong_attribute")],
    expl="Add down the Cat column: 6 boys and 12 girls make 18 children. 12 counts the "
         "girls only, and 25 is the dog total rather than the cat total.",
    fig=PETS, fmt=unit("children")),

B.Q("tables_two_way", "multi_step",
    "Using the pet table, how many of the 60 children have a pet of some kind at home?",
    key=25 + 18, verify=60 - 17,                 # everyone, less those with no pet
    wrong=[(60, "ignored_constraint"), (25, "partial_step"), (17, "inverse")],
    difficulty="hard", confidence=0.91,
    expl="Dogs and cats together come to 25 + 18 = 43 children. Taking the no-pet column "
         "off the grand total gives the same: 60 - 17 = 43. 60 counts every child "
         "including those with no pet, and 17 counts exactly the children who have none.",
    fig=PETS, fmt=unit("children")),

B.Q("tables_two_way", "data_interpretation",
    "Using the pet table, are boys or girls more likely to own a dog?",
    key="Boys, 14 against 11", verify="Boys, 14 against 11",
    wrong=[("Girls, 11 against 14", "inverse"), ("They are equally likely", "misread_data"),
           ("Boys, 25 against 11", "wrong_attribute")],
    expl="There are 30 boys and 30 girls, so the counts can be compared directly: 14 boys "
         "own a dog against 11 girls. Boys, 25 against 11 uses the dog column total, which "
         "already includes the girls.",
    fig=PETS, fmt=PLAIN),

B.Q("tables_two_way", "multi_step",
    "Using the pet table, what fraction of the children who own a dog are girls?",
    key="11 out of 25", verify=f"{11} out of {14 + 11}",
    wrong=[("11 out of 30", "misread_data"), ("11 out of 60", "wrong_attribute"),
           ("14 out of 25", "inverse")],
    difficulty="hard", confidence=0.90,
    expl="25 children own a dog and 11 of them are girls: 11 out of 25. 11 out of 30 uses "
         "the number of girls as the whole, when the question asks about dog owners, and "
         "14 out of 25 gives the boys' share instead.",
    fig=PETS, fmt=PLAIN),

B.Q("tables_two_way", "multi_step",
    "In the pet table, suppose two more girls with cats joined the class. What would the "
    "cat column total become?",
    key=18 + 2, verify=6 + (12 + 2),
    wrong=[(18, "ignored_constraint"), (12 + 2, "partial_step"), (60 + 2, "wrong_attribute")],
    expl="The cat total is 18, and two more cat owners make 20. Checking the column: 6 boys "
         "and now 14 girls also gives 20. 14 counts the girls with cats only, and 18 "
         "forgets to add the newcomers at all.",
    fig=PETS, fmt=unit("children")),

B.Q("tables_two_way", "data_interpretation",
    "Which of these can be read straight from the pet table without any working?",
    key="the number of girls who own a cat", verify="the number of girls who own a cat",
    wrong=[("the number of children who own a pet", "partial_step"),
           ("the number of boys with no pet", "misread_data"),
           ("the number of children who own two pets", "ignored_constraint")],
    difficulty="hard", confidence=0.90,
    expl="The girls-and-cat cell shows 12 directly. The number of children who own a pet "
         "has to be worked out from two columns, the boys with no pet is the missing cell, "
         "and the table never records anyone owning two pets at all.",
    fig=PETS, fmt=PLAIN),

# ===================================================== drawing conclusions (4)

B.Q("drawing_conclusions", "data_interpretation",
    "The column graph shows library borrowings for one week. Which statement does the "
    "graph support?",
    key="More books went out on Thursday than on any other day that week",
    verify="More books went out on Thursday than on any other day that week",
    wrong=[("Thursday is always the busiest day at the library", "ignored_constraint"),
           ("Students prefer borrowing later in the week", "misread_data"),
           ("Fewer students came to the library on Wednesday", "wrong_attribute")],
    difficulty="hard", confidence=0.90,
    expl="The graph covers one week, so it can support a claim about that week and nothing "
         "wider. Thursday is always the busiest day claims every week from a single one, "
         "and fewer students came on Wednesday confuses books borrowed with people through "
         "the door — one student may borrow several books.",
    fig=BC1, fmt=PLAIN),

B.Q("drawing_conclusions", "data_interpretation",
    "The rainfall graph covers January to April at one weather station. Which conclusion "
    "goes beyond what the graph can show?",
    key="This station is drier than most of Australia",
    verify="This station is drier than most of Australia",
    wrong=[("March was the wettest of the four months", "misread_data"),
           ("More rain fell in January than in February", "partial_step"),
           ("Less than 20 mm fell in April", "wrong_attribute")],
    difficulty="hard", confidence=0.91,
    expl="Comparing this station with the rest of the country needs rainfall figures from "
         "elsewhere, and the graph shows only this one place. Every statement about the "
         "columns themselves can be checked against them: March at 60 mm is the tallest, "
         "January at 40 beats February at 25, and April's 15 mm is under 20.",
    fig=BC2, fmt=PLAIN),

B.Q("drawing_conclusions", "data_interpretation",
    "The temperature graph runs from 9 am to 1 pm. A student says the graph shows the "
    "temperature fell all afternoon. What is wrong with that?",
    key="The graph stops at 1 pm, so it says nothing about the rest of the afternoon",
    verify="The graph stops at 1 pm, so it says nothing about the rest of the afternoon",
    wrong=[("The temperature rose between 9 am and noon", "partial_step"),
           ("The graph shows degrees rather than hours", "misread_data"),
           ("One reading is not enough to show a fall", "wrong_attribute")],
    difficulty="hard", confidence=0.90,
    expl="The only fall on the graph is the single step from noon to 1 pm, and after 1 pm "
         "the graph simply ends — what happens later is not recorded either way. The "
         "temperature rose between 9 am and noon is true but does not explain why the "
         "claim about the afternoon cannot be made.",
    fig=LG1, fmt=PLAIN),

B.Q("drawing_conclusions", "data_interpretation",
    "The travel pie chart covers one class of 24 students. Which statement is safest to "
    "make from it?",
    key="Half of this class walks to school", verify="Half of this class walks to school",
    wrong=[("Half of the students at the school walk", "ignored_constraint"),
           ("Walking is the fastest way to get to this school", "misread_data"),
           ("Most Australian students walk to school", "inverse")],
    expl="The chart records this one class, so a claim about this class is exactly what it "
         "supports. Half of the students at the school stretches 24 students to the whole "
         "school, and nothing in the chart is about speed at all.",
    fig=PIE, fmt=PLAIN),

if __name__ == "__main__":
    B.write()
