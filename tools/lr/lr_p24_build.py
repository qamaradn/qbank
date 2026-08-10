#!/usr/bin/env python3
"""Builds lr_thinking_skills_p24.json — 32 more §5.3 problem-solving questions.

truth-teller 11, calendar and scheduling 11, ordering and ranking 10. §5.3 reaches
187/330 and Thinking Skills 647/880.

All three categories are decided by search, using the helpers in lr_logic: truth()
enumerates every pattern of who is honest, order() every arrangement, only() every
candidate date or count. Each raises rather than shipping a puzzle with no answer or
with two.

The truth-tellers were tested as a set before any of this file was written, and six of
the eleven first drafts were broken — two with no consistent pattern at all and four
with two. That is the normal rate for hand-written self-referential puzzles, and it is
why they are never written straight into a batch.
"""
import calendar
import datetime
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.figure_lib import table  # noqa: E402
from tools.lr.lr_common import Batch  # noqa: E402
from tools.lr.lr_logic import only, order, truth  # noqa: E402

B = Batch(nn=24)

def ordinal(n):
    """29 -> 29th, 22 -> 22nd. A bare f"{n}th" gets four dates in ten wrong."""
    suffix = ("th" if 11 <= n % 100 <= 13
              else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th"))
    return f"{n}{suffix}"


DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# ===================================================== truth-teller (11)

_t1 = truth(["Ana", "Bo", "Cy", "Dee"],
            [lambda t: t["Ana"] == (not t["Bo"]),
             lambda t: t["Bo"] == (not t["Cy"]),
             lambda t: t["Cy"] == (not t["Dee"]),
             lambda t: t["Dee"] == (not t["Ana"] and not t["Bo"] and not t["Cy"])])
B.Q("truth_teller",
    "Ana says: 'Bo is lying.' Bo says: 'Cy is lying.' Cy says: 'Dee is lying.' Dee says: "
    "'All three of the others are lying.' How many of the four are telling the truth?",
    key=sum(_t1.values()), verify=len([n for n, v in _t1.items() if v]),
    wrong=[1, 3, 0],
    expl="Dee cannot be truthful: that would make Cy a liar, and Cy's statement that Dee "
         "lies would then be true. So Dee is lying, which makes Cy truthful, Bo a liar and "
         "Ana truthful. Ana and Cy tell the truth — two of them.",
    difficulty="hard", confidence=0.90),

_t2 = truth(["Iris", "Jonah"],
            [lambda t: t["Iris"] == ((not t["Iris"]) or (not t["Jonah"])),
             lambda t: t["Jonah"] == (not t["Iris"])])
B.Q("truth_teller",
    "Iris says: 'At least one of us two is lying.' Jonah says: 'Iris is lying.' Who is "
    "telling the truth?",
    key="Iris only", verify="Iris only" if _t2["Iris"] and not _t2["Jonah"] else "MISMATCH",
    wrong=["Jonah only", "both of them", "neither of them"],
    expl="If Iris were lying, then nobody would be lying — but Iris would be, which is a "
         "contradiction. So Iris is truthful, and her statement is satisfied by Jonah being "
         "the liar. Jonah's claim that Iris lies is therefore false, which fits.",
    difficulty="hard", confidence=0.91),

_t3 = truth(["Kara", "Liam", "Milo"],
            [lambda t: t["Kara"] == (sum(t.values()) == 1),
             lambda t: t["Liam"] == (not t["Kara"]),
             lambda t: t["Milo"] == (t["Kara"] == t["Liam"])])
B.Q("truth_teller",
    "Kara says: 'Exactly one of us three is telling the truth.' Liam says: 'Kara is "
    "lying.' Milo says: 'Kara and Liam are either both truthful or both lying.' Who is "
    "telling the truth?",
    key="Kara only",
    verify="Kara only" if [n for n, v in _t3.items() if v] == ["Kara"] else "MISMATCH",
    wrong=["Liam only", "Milo only", "Kara and Milo"],
    expl="Suppose Kara is truthful. Then exactly one of the three is, so Liam and Milo both "
         "lie. Liam lying means Kara is truthful, which fits, and Milo lying means Kara and "
         "Liam differ, which they do. Everything holds with Kara alone telling the truth.",
    difficulty="hard", confidence=0.90),

_t4 = truth(["Nell", "Otis"],
            [lambda t: t["Nell"] == (t["Nell"] and not t["Otis"]),
             lambda t: t["Otis"] == t["Nell"]])
B.Q("truth_teller",
    "Nell says: 'I am the only one of us telling the truth.' Otis says: 'Nell is telling "
    "the truth.' Who is telling the truth?",
    key="neither of them",
    verify="neither of them" if not any(_t4.values()) else "MISMATCH",
    wrong=["Nell only", "Otis only", "both of them"],
    expl="If Nell were truthful, Otis would be lying — but Otis says Nell is truthful, "
         "which would make that statement true. The contradiction rules Nell out, and with "
         "Nell lying, Otis's claim that she is truthful is false as well.",
    difficulty="hard", confidence=0.90),

_t5 = truth(["Pru", "Quill", "Rosa"],
            [lambda t: t["Pru"] == (not t["Quill"]),
             lambda t: t["Quill"] == (not t["Rosa"]),
             lambda t: t["Rosa"] == (t["Pru"] != t["Quill"])])
B.Q("truth_teller",
    "Pru says: 'Quill is lying.' Quill says: 'Rosa is lying.' Rosa says: 'Pru and Quill "
    "are not both the same — one tells the truth and the other does not.' Who is lying?",
    key="Quill only",
    verify="Quill only" if [n for n, v in _t5.items() if not v] == ["Quill"] else "MISMATCH",
    wrong=["Pru only", "Rosa only", "Pru and Rosa"],
    expl="Rosa's statement is true whenever Pru and Quill differ, and Pru's statement says "
         "exactly that they differ. So Pru and Rosa agree with each other, and both hold "
         "with Quill as the liar — which also makes Quill's claim about Rosa false.",
    difficulty="hard", confidence=0.90),

_t6 = truth(["Ava", "Ben"],
            [lambda t: t["Ava"] == ((not t["Ava"]) and (not t["Ben"]))])
B.Q("truth_teller",
    "On an island every person is either a knight, who always tells the truth, or a knave, "
    "who always lies. Ava says: 'Ben and I are both knaves.' What are they?",
    key="Ava is a knave and Ben is a knight",
    verify=("Ava is a knave and Ben is a knight"
            if not _t6["Ava"] and _t6["Ben"] else "MISMATCH"),
    wrong=["Ava is a knight and Ben is a knave", "both are knaves", "both are knights"],
    expl="Ava cannot be a knight, because a knight cannot truthfully call herself a knave. "
         "So Ava is a knave and her statement is false — which means they are not both "
         "knaves, and since Ava is one, Ben must be a knight.",
    difficulty="hard", confidence=0.91),

_t7 = truth(["Sky", "Tam", "Uma"],
            [lambda t: t["Sky"] == (not t["Tam"]),
             lambda t: t["Tam"] == (not t["Uma"]),
             lambda t: t["Uma"] == (not t["Sky"] and not t["Tam"])])
B.Q("truth_teller",
    "Sky says: 'Tam is lying.' Tam says: 'Uma is lying.' Uma says: 'Sky and Tam are both "
    "lying.' Which one of them is telling the truth?",
    key="Tam", verify=next(n for n, v in _t7.items() if v),
    wrong=["Sky", "Uma", "none of them"],
    expl="If Uma were truthful, Tam would be lying, so Uma would be truthful — but Uma also "
         "claims Sky lies, and Sky lying means Tam is truthful, a contradiction. So Uma "
         "lies, Tam is truthful, and Sky's claim about Tam is false.",
    difficulty="hard", confidence=0.90),

_t8 = truth(["older", "Gil", "Hana", "Ivo"],
            [lambda t: t["Gil"] == t["older"],
             lambda t: t["Hana"] == t["Gil"],
             lambda t: t["Ivo"] == (not t["Hana"]),
             lambda t: sum(t[n] for n in ("Gil", "Hana", "Ivo")) == 2])
B.Q("truth_teller",
    "Gil says: 'Hana is older than me.' Hana says: 'Gil is telling the truth.' Ivo says: "
    "'Hana is lying.' Exactly two of the three are telling the truth. Which one is lying?",
    key="Ivo", verify=next(n for n in ("Gil", "Hana", "Ivo") if not _t8[n]),
    wrong=["Gil", "Hana", "it cannot be worked out"],
    expl="Gil and Hana must agree, since Hana simply vouches for Gil, so they are truthful "
         "together or lying together. Two of the three are truthful, so it must be those "
         "two, which leaves Ivo as the liar — and his claim that Hana lies is indeed "
         "false.",
    difficulty="medium", confidence=0.92),

_t9 = truth(["Yas", "Zed", "Ada"],
            [lambda t: sum(t.values()) == 1,
             lambda t: t["Yas"] == t["Zed"],
             lambda t: t["Zed"] == (not t["Ada"]),
             lambda t: t["Ada"] == (not t["Yas"])])
B.Q("truth_teller",
    "Yas says: 'Zed is telling the truth.' Zed says: 'Ada is lying.' Ada says: 'Yas is "
    "lying.' Exactly one of the three is telling the truth. Which one?",
    key="Ada", verify=next(n for n, v in _t9.items() if v),
    wrong=["Yas", "Zed", "it cannot be worked out"],
    expl="Yas and Zed must match, since Yas vouches for Zed, so they are either both "
         "truthful or both liars. Only one person is truthful, so they are both liars — "
         "which leaves Ada as the truthful one, and Ada's claim that Yas lies fits.",
    difficulty="hard", confidence=0.90),

# without the "at least one" clue this puzzle has a second pattern in which all three
# lie, and both answers can be argued for
_t10 = truth(["Bree", "Cass", "Dov"],
             [lambda t: t["Bree"] == (sum(t.values()) == 1),
              lambda t: t["Cass"] == (sum(t.values()) == 2),
              lambda t: t["Dov"] == (sum(t.values()) == 3),
              lambda t: sum(t.values()) >= 1])
B.Q("truth_teller",
    "Bree, Cass and Dov are each asked how many of the three of them are telling the "
    "truth. Bree says 'one of us', Cass says 'two of us' and Dov says 'three of us'. At "
    "least one of them is telling the truth. How many of them are?",
    key=sum(_t10.values()), verify=len([n for n, v in _t10.items() if v]),
    wrong=[2, 3, 0],
    expl="The three answers disagree, so at most one of them can be right, and at least "
         "one is. So exactly one is truthful — which is what Bree said, making Bree the "
         "truthful one and the other two liars.",
    fmt=lambda v: f"{v} of them", difficulty="hard", confidence=0.90),

_t11 = [w for w in ("Dot", "Eli", "Fay")
        if [w != "Dot", w == "Fay", w != "Fay"].count(True) == 1]
B.Q("truth_teller",
    "A phone has gone missing and exactly one of three students took it. Dot says: 'It was "
    "not me.' Eli says: 'Fay took it.' Fay says: 'Eli is lying.' Exactly one of the three "
    "is telling the truth. Who took the phone?",
    key="Dot", verify=(_t11 + ["AMBIGUOUS"])[0],
    wrong=["Eli", "Fay", "it cannot be worked out"],
    expl="If Fay took it, Dot and Eli would both be right — two truths. If Eli took it, Dot "
         "and Fay would both be right. Only Dot taking it leaves a single true statement, "
         "Fay's.",
    difficulty="hard", confidence=0.90),

# ===================================================== calendar and scheduling (11)

B.Q("calendar_scheduling",
    "A year is a leap year if it divides by 4, except that century years must divide by "
    "400. How many days were there in February 2024?",
    key=calendar.monthrange(2024, 2)[1],
    verify=28 + (1 if 2024 % 4 == 0 and (2024 % 100 != 0 or 2024 % 400 == 0) else 0),
    wrong=[28, 30, 31],
    expl="2024 divides exactly by 4 and is not a century year, so it is a leap year and "
         "February had 29 days. In an ordinary year it has 28.",
    fmt=lambda v: f"{v} days", difficulty="medium", confidence=0.92),

B.Q("calendar_scheduling",
    "Today is a Wednesday. What day of the week will it be in 100 days' time?",
    key=DAYS[(DAYS.index("Wednesday") + 100) % 7],
    # second route: step a real date forward 100 days rather than count remainders
    verify=DAYS[(datetime.date(2026, 4, 1) + datetime.timedelta(days=100)).weekday()]
    if datetime.date(2026, 4, 1).weekday() == 2 else "MISMATCH",
    wrong=["Wednesday", "Tuesday", "Saturday"],
    expl="One hundred days is 14 whole weeks plus 2 days, since 14 x 7 = 98. The 14 weeks "
         "land back on Wednesday, and 2 more days reach Friday.",
    difficulty="hard", confidence=0.91),

_c3 = next(w for w in range(1, 200) if w % 3 == 0 and w % 5 == 0)
B.Q("calendar_scheduling",
    "A choir rehearses every 3 weeks and an orchestra every 5 weeks. Both rehearsed this "
    "week. In how many weeks will they next rehearse in the same week?",
    key=_c3, verify=3 * 5,
    wrong=[8, 30, 5],
    expl="The choir is in weeks 3, 6, 9, 12 and 15; the orchestra in weeks 5, 10 and 15. "
         "Week 15 is the first they share. Answering 8 adds the two gaps together instead "
         "of finding a week that suits both.",
    fmt=lambda v: f"in {v} weeks", difficulty="hard", confidence=0.91),

B.Q("calendar_scheduling",
    "A night bus leaves at 11:40 pm and the journey takes 55 minutes. At what time does it "
    "arrive?",
    key="12:35 am",
    verify=(datetime.datetime(2026, 1, 1, 23, 40)
            + datetime.timedelta(minutes=55)).strftime("%-I:%M am"),
    wrong=["11:95 pm", "12:35 pm", "1:35 am"],
    expl="Twenty minutes takes the bus to midnight, and the remaining 35 minutes make it "
         "12:35 am the next day. 11:95 pm is not a time, and 12:35 pm would be the middle "
         "of the following day.",
    difficulty="hard", confidence=0.90),

B.Q("calendar_scheduling",
    "In summer, Sydney is 3 hours ahead of Perth. A flight leaves Perth at 9:15 am Perth "
    "time and takes 4 hours. What is the local time in Sydney when it lands?",
    key="4:15 pm",
    verify=(datetime.datetime(2026, 1, 1, 9, 15)
            + datetime.timedelta(hours=4 + 3)).strftime("%-I:%M pm"),
    wrong=["1:15 pm", "10:15 am", "7:15 pm"],
    expl="Four hours in the air brings it to 1:15 pm Perth time, and Sydney is 3 hours "
         "further on, so the clock there reads 4:15 pm. Answering 1:15 pm gives the Perth "
         "time and forgets the change.",
    difficulty="hard", confidence=0.90),

# the 1st is a Tuesday, so Tuesdays are the dates leaving remainder 1 on division by 7,
# not 3 — the first draft searched for the wrong residue and returned the 31st
_c6 = only(range(1, 32), lambda d: d % 7 == 1 and d > 28)
B.Q("calendar_scheduling",
    "The first day of a 31-day month falls on a Tuesday. What is the date of the fifth "
    "Tuesday in that month?",
    key=_c6, verify=1 + 4 * 7,
    wrong=[22, 30, 28],
    expl="Tuesdays fall on the 1st, 8th, 15th, 22nd and 29th, so the fifth is the 29th. "
         "Answering 22 stops at the fourth Tuesday.",
    fmt=lambda v: f"the {ordinal(v)}", difficulty="medium", confidence=0.92),

B.Q("calendar_scheduling",
    "A play rehearses every 10 days. The first rehearsal is on 4 March. On what date is "
    "the fourth rehearsal?",
    key="3 April",
    verify=(datetime.date(2026, 3, 4)
            + datetime.timedelta(days=3 * 10)).strftime("%-d %B"),
    wrong=["34 March", "24 March", "4 April"],
    expl="The fourth rehearsal is three gaps of 10 days after the first, which is 30 days "
         "later. Thirty days on from 4 March runs past the end of March, which has 31 days, "
         "so it lands on 3 April.",
    difficulty="hard", confidence=0.90),

# the first draft named each train by its departure time AND repeated that time in the
# next column, so the table carried the same information twice. Only visible on the page.
TT = table([["Train", "Leaves", "Arrives"], ["A", "7:05", "7:48"],
            ["B", "7:35", "8:12"], ["C", "8:05", "8:51"], ["D", "8:40", "9:19"]])
_trips = {"A": 43, "B": 37, "C": 46, "D": 39}
B.Q("calendar_scheduling",
    "The timetable shows four morning trains. Which train has the shortest journey, and "
    "how long does it take?",
    key="Train B, taking 37 minutes",
    verify=f"Train {min(_trips, key=_trips.get)}, taking {min(_trips.values())} minutes",
    wrong=["Train A, taking 43 minutes", "Train D, taking 39 minutes",
           "Train C, taking 46 minutes"],
    expl="Subtracting each departure from its arrival gives 43, 37, 46 and 39 minutes. "
         "Train B is quickest at 37 minutes, even though it is not the earliest to leave.",
    fig=TT, difficulty="hard", confidence=0.90),

B.Q("calendar_scheduling",
    "A job takes 14 working days. Work starts on a Monday, and no work is done on "
    "Saturdays or Sundays. On which day of the week does the job finish?",
    key=DAYS[(0 + (14 - 1) + 2 * ((14 - 1) // 5)) % 7],
    verify=DAYS[(lambda: [d for d in range(0, 40)
                          if sum(1 for x in range(d + 1) if x % 7 < 5) == 14][0] % 7)()],
    wrong=["Friday", "Monday", "Wednesday"],
    expl="Fourteen working days is two full working weeks plus four more days. Two weeks "
         "of work end on a Friday, and four more working days run Monday to Thursday, so "
         "the job finishes on a Thursday.",
    difficulty="hard", confidence=0.90),

B.Q("calendar_scheduling",
    "A four-day roster repeats: early, late, night, off, early, late, night, off, and so "
    "on. Day 1 is an early shift. What is the shift on day 30?",
    key=["early", "late", "night", "off"][(30 - 1) % 4],
    verify=["early", "late", "night", "off"][29 % 4],
    wrong=["early", "night", "off"],
    expl="The roster repeats every 4 days, and 30 is 28 plus 2, so day 30 sits in the same "
         "place as day 2: a late shift. Day 29 would be early and day 31 night.",
    fmt=lambda v: ("a day off" if v == "off"
                   else f"{'an' if v[0] in 'aeiou' else 'a'} {v} shift"),
    difficulty="hard", confidence=0.91),

B.Q("calendar_scheduling",
    "How many days are there from 20 August to 15 October, counting the 15th of October "
    "but not the 20th of August? August has 31 days and September has 30.",
    key=(datetime.date(2026, 10, 15) - datetime.date(2026, 8, 20)).days,
    verify=(31 - 20) + 30 + 15,
    wrong=[57, 55, 45],
    expl="August contributes the 11 days after the 20th, September contributes all 30, and "
         "October contributes 15, making 56. Answering 57 counts the 20th of August as "
         "well, and 45 loses one of the part months.",
    fmt=lambda v: f"{v} days", difficulty="hard", confidence=0.90),

# ===================================================== ordering and ranking (10)

_r1 = order(["Ada", "Bilal", "Cleo", "Dana"],
            [lambda p: p["Ada"] == p["Bilal"] + 2,
             lambda p: p["Cleo"] == 1,
             lambda p: p["Dana"] < p["Ada"]])
B.Q("ordering_ranking",
    "Four runners finish a race with no ties. Cleo finishes first. Ada finishes exactly "
    "two places behind Bilal. Dana finishes somewhere ahead of Ada. In which place does "
    "Bilal finish?",
    key={1: "first", 2: "second", 3: "third", 4: "fourth"}[_r1["Bilal"]],
    verify={1: "first", 2: "second", 3: "third", 4: "fourth"}[_r1["Ada"] - 2],
    wrong=["first", "third", "fourth"],
    expl="Cleo takes first. Ada two places behind Bilal leaves only second and fourth, "
         "since third and fifth would run off the end of a four-runner race. So Bilal is "
         "second and Ada fourth, and Dana takes third, which is ahead of Ada as required.",
    difficulty="hard", confidence=0.90),

_r2 = order(["Eve", "Fred", "Gina", "Hugo", "Ivy"],
            [lambda p: p["Eve"] < p["Fred"] < p["Gina"],
             lambda p: p["Hugo"] == 1,
             lambda p: p["Ivy"] == 5])
B.Q("ordering_ranking",
    "Five swimmers are ranked with no ties. Hugo is ranked first and Ivy last. Eve is "
    "ranked above Fred, and Fred above Gina. Who is ranked third?",
    key=next(n for n, v in _r2.items() if v == 3), verify=sorted(_r2, key=_r2.get)[2],
    wrong=["Eve", "Gina", "Ivy"],
    expl="Hugo and Ivy take the outside places, leaving second, third and fourth for Eve, "
         "Fred and Gina in that order. Fred is the middle one, so Fred is third.",
    difficulty="medium", confidence=0.92),

_r3 = order(["Jo", "Kit", "Lex"],
            [lambda p: p["Jo"] != 2, lambda p: p["Kit"] < p["Jo"],
             lambda p: p["Lex"] != 1])
B.Q("ordering_ranking",
    "Three cyclists finish with no ties. Jo does not come second. Kit finishes ahead of "
    "Jo. Lex does not come first. Who finishes last?",
    key=next(n for n, v in _r3.items() if v == 3), verify=max(_r3, key=_r3.get),
    wrong=["Kit", "Lex", "it cannot be worked out"],
    expl="Kit is ahead of Jo, so Jo is not first, and Jo is not second either, so Jo is "
         "last. Lex is not first, which leaves Kit first and Lex second.",
    difficulty="hard", confidence=0.91),

_r4 = order(["Mai", "Nils", "Opal", "Piet"],
            [lambda p: abs(p["Mai"] - p["Nils"]) == 3,
             lambda p: p["Opal"] < p["Piet"],
             lambda p: p["Mai"] < p["Nils"],
             lambda p: p["Opal"] == 2])
B.Q("ordering_ranking",
    "Four books stand in a row. Mai's and Nils's books have exactly two books between "
    "them, with Mai's on the left. Opal's book is second from the left, and Piet's is "
    "somewhere to the right of Opal's. Whose book is on the far right?",
    key=f"{next(n for n, v in _r4.items() if v == 4)}'s",
    verify=f"{max(_r4, key=_r4.get)}'s",
    wrong=["Mai's", "Opal's", "Piet's"],
    expl="Two books between Mai's and Nils's, with Mai's first, puts them at the two ends: "
         "Mai first and Nils fourth. Opal is second, so Piet takes third, which fits Piet "
         "being to the right of Opal.",
    difficulty="hard", confidence=0.90),

_r5 = order(["Quon", "Rita", "Sami", "Tao", "Uri"],
            [lambda p: p["Quon"] < p["Rita"],
             lambda p: p["Sami"] == p["Rita"] + 1,
             lambda p: p["Tao"] == 1,
             lambda p: p["Uri"] == 5,
             lambda p: p["Quon"] == 2])
B.Q("ordering_ranking",
    "Five students queue for the canteen. Tao is at the front and Uri at the back. Quon is "
    "second in the queue. Sami stands directly behind Rita. Who is fourth in the queue?",
    key=next(n for n, v in _r5.items() if v == 4), verify=sorted(_r5, key=_r5.get)[3],
    wrong=["Rita", "Quon", "Uri"],
    expl="Tao, Quon and Uri take first, second and fifth, so Rita and Sami fill third and "
         "fourth. Sami stands directly behind Rita, so Rita is third and Sami fourth.",
    difficulty="hard", confidence=0.90),

_r6 = order(["Vera", "Wade", "Xena"],
            [lambda p: p["Vera"] > p["Wade"], lambda p: p["Xena"] > p["Vera"]])
B.Q("ordering_ranking",
    "Three parcels are weighed and no two weigh the same. Vera's is heavier than Wade's, "
    "and Xena's is heavier than Vera's. Which parcel is the lightest?",
    key="Wade's", verify=f"{min(_r6, key=_r6.get)}'s",
    wrong=["Vera's", "Xena's", "it cannot be worked out"],
    expl="Reading the two clues as a chain gives Xena's heaviest, then Vera's, then "
         "Wade's. Wade's is at the bottom of the chain.",
    difficulty="medium", confidence=0.92),

_r7 = order(["Yara", "Zane", "Abe", "Bea"],
            [lambda p: p["Yara"] < p["Zane"],
             lambda p: p["Abe"] < p["Yara"],
             lambda p: p["Bea"] > p["Zane"]])
B.Q("ordering_ranking",
    "Four towers are ranked by height, tallest first, with no two the same. Yara's tower "
    "is taller than Zane's. Abe's is taller than Yara's. Bea's is shorter than Zane's. "
    "Whose tower is the shortest?",
    key="Bea's", verify=f"{max(_r7, key=_r7.get)}'s",
    wrong=["Abe's", "Yara's", "Zane's"],
    expl="The chain runs Abe's above Yara's, Yara's above Zane's and Zane's above Bea's, "
         "so Bea's tower is at the bottom and Abe's at the top.",
    difficulty="hard", confidence=0.91),

_r8 = order(["Cara", "Dev", "Elle", "Finn", "Gil"],
            [lambda p: p["Cara"] == 3,
             lambda p: p["Dev"] < p["Cara"],
             lambda p: p["Elle"] > p["Cara"],
             lambda p: p["Finn"] == 1,
             lambda p: p["Gil"] == 5])
B.Q("ordering_ranking",
    "Five athletes finish with no ties. Cara comes third, Finn first and Gil last. Dev "
    "finishes ahead of Cara and Elle behind her. In which place does Dev finish?",
    key={1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth"}[_r8["Dev"]],
    verify={1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth"}[
        ({1, 2, 3, 4, 5} - {_r8["Finn"], _r8["Cara"], _r8["Elle"], _r8["Gil"]}).pop()],
    wrong=["first", "third", "fourth"],
    expl="First, third and fifth are taken by Finn, Cara and Gil, leaving second and "
         "fourth. Dev is ahead of Cara so Dev is second, and Elle behind her is fourth.",
    difficulty="hard", confidence=0.90),

_r9 = order(["Hana", "Ira", "Jem"],
            [lambda p: p["Hana"] != 1, lambda p: p["Hana"] != 3,
              lambda p: p["Ira"] > p["Jem"]])
B.Q("ordering_ranking",
    "Three friends are ranked by test mark with no ties. Hana is neither top nor bottom. "
    "Ira scored lower than Jem. Who came top?",
    key=next(n for n, v in _r9.items() if v == 1), verify=min(_r9, key=_r9.get),
    wrong=["Hana", "Ira", "it cannot be worked out"],
    expl="Hana is neither top nor bottom, so Hana is in the middle. Ira scored lower than "
         "Jem, so Jem is top and Ira is bottom.",
    difficulty="medium", confidence=0.92),

_r10 = order(["Kez", "Lena", "Moss", "Nia"],
             [lambda p: p["Kez"] == p["Lena"] - 1,
              lambda p: p["Moss"] == 4,
              lambda p: p["Nia"] < p["Kez"]])
B.Q("ordering_ranking",
    "Four people stand in a line facing forward. Moss is last. Kez stands directly in "
    "front of Lena. Nia is somewhere in front of Kez. Who is at the front?",
    key=next(n for n, v in _r10.items() if v == 1), verify=min(_r10, key=_r10.get),
    wrong=["Kez", "Lena", "Moss"],
    expl="Moss is fourth. Kez and Lena must stand together in that order, and Nia is ahead "
         "of Kez, so the only fit is Nia, Kez, Lena, Moss. Nia is at the front.",
    difficulty="hard", confidence=0.91),

B.write()
