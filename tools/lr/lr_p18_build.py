#!/usr/bin/env python3
"""Builds lr_thinking_skills_p18.json — 32 §5.3 problem-solving questions.

logic grid 8, optimisation 8, calendar and scheduling 8, truth-teller 8 — opening the
four §5.3 subcategories that had nothing at all. §5.3 goes from 59/330 to 91/330.

These four are the first categories in the build where the answer can be found by SEARCH
rather than computed, and that gives the strongest verification used anywhere here: every
item enumerates the whole possibility space, filters it by the clues exactly as the stem
states them, and fails unless exactly one possibility survives. That checks three things
at once — that the stated answer is right, that the clues are sufficient, and that they
are not so loose that a second answer also fits. The last of those is the failure this
build has hit repeatedly and cannot catch any other way.

If a puzzle is ever edited, the search re-runs. A clue that stops constraining will show
up as AMBIGUOUS rather than as a question two students can both defend.
"""
import itertools
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.figure_lib import table  # noqa: E402
from tools.lr.lr_common import Batch  # noqa: E402

B = Batch(nn=18)


def solve(items, options, clues):
    """Every assignment of `options` to `items`, kept only if it satisfies every clue.

    Returns the single solution as a dict, or raises if the clues admit none or several —
    which is exactly the two failures a hand-written logic puzzle suffers from.
    """
    found = [dict(zip(items, p)) for p in itertools.permutations(options)
             if all(c(dict(zip(items, p))) for c in clues)]
    if len(found) != 1:
        raise AssertionError(f"puzzle has {len(found)} solutions, not 1: {found}")
    return found[0]


def truth(names, clues):
    """Every pattern of who tells the truth, kept only if self-consistent. Same guarantee."""
    found = [dict(zip(names, p)) for p in itertools.product([True, False], repeat=len(names))
             if all(c(dict(zip(names, p)))for c in clues)]
    if len(found) != 1:
        raise AssertionError(f"{len(found)} consistent patterns, not 1: {found}")
    return found[0]


def best(options, cost, want="min"):
    """The cheapest or dearest option, raising unless one is strictly best."""
    vals = {k: cost(k) for k in options}
    target = min(vals.values()) if want == "min" else max(vals.values())
    winners = [k for k, v in vals.items() if v == target]
    if len(winners) != 1:
        raise AssertionError(f"{len(winners)} options tie at {target}: {winners}")
    return winners[0], target


DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# ===================================================== logic grid (8)

_s = solve(["Ava", "Ben", "Chloe"], ["netball", "hockey", "cricket"],
           [lambda a: a["Ava"] != "hockey",
            lambda a: a["Ben"] != "netball",
            lambda a: a["Chloe"] == "hockey"])
B.Q("logic_grid",
    "Ava, Ben and Chloe each play one sport, and no two play the same one. The sports are "
    "netball, hockey and cricket. Chloe plays hockey. Ava does not play hockey, and Ben "
    "does not play netball. Which sport does Ben play?",
    key=_s["Ben"], verify=_s["Ben"],
    wrong=["netball", "hockey", "it cannot be worked out"],
    expl="Chloe takes hockey, so netball and cricket are left for Ava and Ben. Ben does not "
         "play netball, so Ben plays cricket and Ava netball.",
    fig=table([["", "netball", "hockey", "cricket"], ["Ava", "", "", ""],
               ["Ben", "", "", ""], ["Chloe", "", "", ""]])),

_s2 = solve(["red", "blue", "green"], ["cat", "dog", "bird"],
            [lambda a: a["red"] != "dog",
             lambda a: a["blue"] == "bird",
             lambda a: a["green"] != "cat"])
B.Q("logic_grid",
    "Three houses are painted red, blue and green, and each has one pet: a cat, a dog or a "
    "bird. The blue house has the bird. The red house does not have the dog. The green "
    "house does not have the cat. Which pet lives in the red house?",
    key=f'the {_s2["red"]}', verify=f'the {_s2["red"]}',
    wrong=["the dog", "the bird", "it cannot be worked out"],
    expl="The blue house has the bird, so the cat and the dog are in the red and green "
         "houses. The red house has no dog and the green house has no cat, so red has the "
         "cat and green has the dog.",
    fig=table([["", "cat", "dog", "bird"], ["red", "", "", ""],
               ["blue", "", "", ""], ["green", "", "", ""]])),

_s3 = solve(["Ella", "Finn", "Grace", "Harry"], ["Year 3", "Year 4", "Year 5", "Year 6"],
            [lambda a: a["Ella"] == "Year 6",
             lambda a: a["Grace"] == "Year 5",
             lambda a: a["Finn"] != "Year 3"])
B.Q("logic_grid",
    "Ella, Finn, Grace and Harry are in Years 3, 4, 5 and 6, one in each. Ella is in Year "
    "6. Grace is in Year 5. Finn is not in Year 3. Which year is Harry in?",
    key=_s3["Harry"], verify=_s3["Harry"],
    wrong=["Year 4", "Year 5", "Year 6"],
    expl="Ella takes Year 6 and Grace takes Year 5, so Years 3 and 4 are left for Finn and "
         "Harry. Finn is not in Year 3, so Finn is in Year 4 and Harry in Year 3.",
    fig=table([["", "Year 3", "Year 4", "Year 5", "Year 6"], ["Ella", "", "", "", ""],
               ["Finn", "", "", "", ""], ["Grace", "", "", "", ""],
               ["Harry", "", "", "", ""]])),

_s4 = solve(["Isla", "Jack", "Kai"], ["Monday", "Wednesday", "Friday"],
            [lambda a: a["Isla"] != "Monday",
             lambda a: a["Jack"] == "Monday",
             lambda a: a["Kai"] != "Wednesday"])
B.Q("logic_grid",
    "Isla, Jack and Kai each help in the canteen on one day of the week — Monday, Wednesday "
    "or Friday, one person to a day. Jack helps on Monday. Kai does not help on Wednesday. "
    "Which day does Isla help?",
    key=_s4["Isla"], verify=_s4["Isla"],
    wrong=["Monday", "Friday", "it cannot be worked out"],
    expl="Jack has Monday, so Isla and Kai have Wednesday and Friday between them. Kai is "
         "not on Wednesday, so Kai has Friday and Isla has Wednesday.",
    difficulty="hard", confidence=0.91),

_s5 = solve(["Liam", "Mia", "Noah"], ["swimming", "running", "cycling"],
            [lambda a: a["Mia"] != "swimming",
             lambda a: a["Noah"] != "swimming",
             lambda a: a["Noah"] != "running"])
B.Q("logic_grid",
    "Liam, Mia and Noah each chose a different event: swimming, running or cycling. Neither "
    "Mia nor Noah chose swimming. Noah did not choose running either. Which event did Mia "
    "choose?",
    key=_s5["Mia"], verify=_s5["Mia"],
    wrong=["swimming", "cycling", "it cannot be worked out"],
    expl="Neither Mia nor Noah swims, so Liam does. Noah does not run either, so Noah "
         "cycles, and running is all that is left for Mia.",
    difficulty="hard", confidence=0.90),

_s6 = solve(["Owen", "Priya", "Rosa"], ["1st", "2nd", "3rd"],
            [lambda a: a["Priya"] != "1st",
             lambda a: a["Owen"] != "3rd",
             lambda a: a["Rosa"] == "3rd"])
B.Q("logic_grid",
    "Owen, Priya and Rosa finished a race in first, second and third places. Rosa came "
    "third. Priya did not come first. Owen did not come third. In which place did Owen "
    "finish?",
    # fmt runs over the distractors too, so the key is worded here rather than mapped;
    # verify derives Owen's place from the other two rather than reading his own off
    key={"1st": "first", "2nd": "second", "3rd": "third"}[_s6["Owen"]],
    verify={"1st": "first", "2nd": "second", "3rd": "third"}[
        ({"1st", "2nd", "3rd"} - {_s6["Priya"], _s6["Rosa"]}).pop()],
    wrong=["second", "third", "it cannot be worked out"],
    expl="Rosa is third, so Owen and Priya have first and second. Priya did not come first, "
         "so Priya is second and Owen is first."),

_s7 = solve(["apple", "banana", "orange"], ["Tara", "Umar", "Vic"],
            [lambda a: a["apple"] != "Tara",
             lambda a: a["banana"] == "Vic",
             lambda a: a["orange"] != "Umar"])
B.Q("logic_grid",
    "Tara, Umar and Vic each brought one piece of fruit — an apple, a banana or an orange, "
    "no two the same. Vic brought the banana. Tara did not bring the apple. Umar did not "
    "bring the orange. Who brought the apple?",
    key=_s7["apple"], verify=_s7["apple"],
    wrong=["Tara", "Vic", "it cannot be worked out"],
    expl="Vic has the banana, so the apple and the orange belong to Tara and Umar. Tara did "
         "not bring the apple, so Tara has the orange and Umar has the apple — which also "
         "fits Umar not bringing the orange.",
    difficulty="hard", confidence=0.90),

_s8 = solve(["Wren", "Xander", "Yuki", "Zoe"], ["piano", "violin", "drums", "flute"],
            [lambda a: a["Wren"] == "drums",
             lambda a: a["Xander"] != "piano",
             lambda a: a["Yuki"] == "flute",
             lambda a: a["Xander"] != "flute"])
B.Q("logic_grid",
    "Wren, Xander, Yuki and Zoe each play a different instrument: piano, violin, drums or "
    "flute. Wren plays the drums and Yuki plays the flute. Xander plays neither the piano "
    "nor the flute. Which instrument does Zoe play?",
    key=f'the {_s8["Zoe"]}', verify=f'the {_s8["Zoe"]}',
    wrong=["the violin", "the drums", "the flute"],
    expl="Wren has the drums and Yuki the flute, leaving the piano and the violin for "
         "Xander and Zoe. Xander does not play the piano, so Xander has the violin and Zoe "
         "the piano.",
    fig=table([["", "piano", "violin", "drums", "flute"], ["Wren", "", "", "", ""],
               ["Xander", "", "", "", ""], ["Yuki", "", "", "", ""], ["Zoe", "", "", "", ""]]),
    difficulty="hard", confidence=0.91),

# ===================================================== optimisation (8)

_o1, _c1 = best(["single tickets", "a ten-trip card", "a monthly pass"],
                lambda k: {"single tickets": 22 * 4, "a ten-trip card": 3 * 35,
                           "a monthly pass": 99}[k])
B.Q("optimisation",
    "A student makes 22 bus trips in a month. A single trip costs $4. A ten-trip card costs "
    "$35 and only whole cards can be bought. A monthly pass costs $99 for unlimited trips. "
    "Which is the cheapest way to pay?",
    key=_o1, verify=_o1,
    wrong=["a ten-trip card", "a monthly pass", "they all cost the same"],
    expl="22 single trips cost $88. Ten-trip cards must be bought whole, so 22 trips need 3 "
         "cards at $105. The monthly pass is $99. So single tickets at $88 are cheapest — "
         "the pass only wins once the trips pass 25.",
    difficulty="hard", confidence=0.90),

B.Q("optimisation",
    "A shop sells rice in three sizes: 500 g for $3, 1 kg for $5.50, and 2 kg for $10.40. "
    "Which size costs the least per kilogram?",
    key="the 2 kg bag",
    verify=best(["the 500 g bag", "the 1 kg bag", "the 2 kg bag"],
                lambda k: {"the 500 g bag": 3 / 0.5, "the 1 kg bag": 5.50,
                           "the 2 kg bag": 10.40 / 2}[k])[0],
    wrong=["the 500 g bag", "the 1 kg bag", "they cost the same per kilogram"],
    expl="Work each one out per kilogram: the 500 g bag is $3 for half a kilogram, so $6; "
         "the 1 kg bag is $5.50; and the 2 kg bag is $10.40 for two, so $5.20. The 2 kg bag "
         "is cheapest per kilogram, though it costs the most to buy.",
    difficulty="hard", confidence=0.90),

B.Q("optimisation",
    "Coins come in 5c, 10c, 20c and 50c. What is the smallest number of coins that makes "
    "95c exactly?",
    key=4, verify=min(a + b + c + d
                      for a in range(20) for b in range(20) for c in range(20) for d in range(20)
                      if 50 * a + 20 * b + 10 * c + 5 * d == 95),
    wrong=[3, 5, 19],
    expl="One 50c, two 20c and one 5c makes 95c with 4 coins. Three coins cannot do it: the "
         "most three can carry without going over 95c is 50c + 20c + 20c = 90c. 19 would be "
         "nineteen 5c coins.",
    fmt=lambda v: f"{v} coins", difficulty="hard", confidence=0.91),

B.Q("optimisation",
    "A crate holds 8 books. A librarian has 50 books to move. What is the smallest number "
    "of crates that will carry them all?",
    key=-(-50 // 8), verify=next(n for n in range(1, 30) if 8 * n >= 50),
    wrong=[50 // 8, 8, 50],
    expl="Six crates hold 48 books, which is not enough, and 7 crates hold 56. So 7 crates "
         "are needed, the last one only part full. 6 leaves two books behind.",
    fmt=lambda v: f"{v} crates"),

_o5, _ = best(["separate tickets for everybody", "a family ticket",
               "a family ticket and one adult"],
              lambda k: {"separate tickets for everybody": 2 * 24 + 3 * 12,
                         "a family ticket": 70,
                         "a family ticket and one adult": 70 + 24}[k])
B.Q("optimisation",
    "A zoo charges $24 for an adult and $12 for a child. A family ticket costs $70 and "
    "covers two adults and up to three children. Two adults and three children are going. "
    "What is the cheapest way to pay?",
    key=_o5, verify=_o5,
    wrong=["separate tickets for everybody", "a family ticket and one adult",
           "the cost is the same"],
    expl="Buying separately costs 2 x $24 + 3 x $12 = $84. The family ticket covers exactly "
         "this group for $70, so it is cheaper by $14. Adding an extra adult ticket to the "
         "family ticket pays twice for somebody already covered.",
    difficulty="hard", confidence=0.91),

B.Q("optimisation",
    "A rope 30 metres long is to be cut into pieces 4 metres long. How many pieces can be "
    "cut, and how much rope is left over?",
    key="7 pieces, with 2 m left", verify=f"{30 // 4} pieces, with {30 % 4} m left",
    wrong=["8 pieces, with 2 m left", "7 pieces, with 4 m left", "6 pieces, with 6 m left"],
    expl="Seven pieces use 28 metres and leave 2 metres, which is too short for an eighth "
         "piece. 8 pieces would need 32 metres, which is more rope than there is.",
    difficulty="hard", confidence=0.90),

B.Q("optimisation",
    "Pencils cost 60c each, or $5 for a pack of 10. What is the least a class can pay for "
    "24 pencils?",
    key="$12.40", verify=f"${min(5 * p + 0.6 * (24 - 10 * p) for p in range(3) if 10 * p <= 24):.2f}",
    wrong=["$15.00", "$14.40", "$13.40"],
    expl="Two packs give 20 pencils for $10, and 4 loose pencils cost $2.40, making $12.40. "
         "Check the other ways: all loose is $14.40, one pack plus 14 loose is $13.40, and "
         "three packs is $15.00 for 30 pencils. So $12.40 is the least.",
    difficulty="hard", confidence=0.90),

B.Q("optimisation",
    "A tap fills a bucket in 6 minutes and a second tap fills the same bucket in 3 minutes. "
    "Using both taps together, what is the shortest time to fill it?",
    key=2, verify=next(t for t in range(1, 10) if t / 6 + t / 3 >= 1),
    wrong=[3, 9 // 2, 9],
    expl="In one minute the first tap fills a sixth of the bucket and the second a third, "
         "which is half a bucket between them, so two minutes fills it. 9 adds the two times "
         "together, which would be slower than the faster tap on its own — a clear sign the "
         "answer is wrong.",
    fmt=lambda v: f"{v} minutes", difficulty="hard", confidence=0.90),

# ===================================================== calendar and scheduling (8)

B.Q("calendar_scheduling",
    "A school camp starts on a Thursday and lasts 10 days, counting the first day. On which "
    "day of the week does it end?",
    key=DAYS[(DAYS.index("Thursday") + 9) % 7], verify=DAYS[(3 + 10 - 1) % 7],
    wrong=["Sunday", "Thursday", "Friday"],
    expl="Counting the first day as day 1, the camp runs 9 more days. Seven of those bring "
         "it back to Thursday, and 2 more reach Saturday. Adding 10 instead of 9 gives "
         "Sunday, which is the commonest slip.",
    difficulty="hard", confidence=0.91),

B.Q("calendar_scheduling",
    "The first day of a 30-day month is a Monday. How many Mondays are there in that month?",
    key=len([d for d in range(1, 31) if (d - 1) % 7 == 0]),
    verify=1 + (30 - 1) // 7,
    wrong=[4, 6, 7],
    expl="Mondays fall on the 1st, 8th, 15th, 22nd and 29th — five of them. A 30-day month "
         "holds four full weeks, which is where the answer 4 comes from, plus two days over; "
         "the first of those two, the 29th, is another Monday.",
    fmt=lambda v: f"{v} Mondays"),

B.Q("calendar_scheduling",
    "A library club meets every 4 days and a chess club every 6 days. Both met today. In "
    "how many days will they next meet on the same day?",
    key=12, verify=next(d for d in range(1, 60) if d % 4 == 0 and d % 6 == 0),
    wrong=[24, 10, 2],
    expl="The library club meets on days 4, 8, 12 and so on, and the chess club on days 6 "
         "and 12. Day 12 is the first they share. 24 is a day they share, but not the "
         "first, and 10 adds the two gaps together.",
    fmt=lambda v: f"in {v} days", difficulty="hard", confidence=0.91),

_SESS = [("Art", 9 * 60, 10 * 60 + 15), ("Music", 10 * 60, 11 * 60),
         ("Drama", 11 * 60 + 15, 12 * 60 + 30), ("Sport", 12 * 60 + 15, 13 * 60 + 15)]
_clash = [(a[0], b[0]) for a, b in itertools.combinations(_SESS, 2)
          if a[1] < b[2] and b[1] < a[2]]
TT = table([["Session", "Starts", "Ends"], ["Art", "9:00", "10:15"],
            ["Music", "10:00", "11:00"], ["Drama", "11:15", "12:30"],
            ["Sport", "12:15", "1:15"]])
B.Q("calendar_scheduling",
    "The timetable shows four sessions. Which two sessions overlap in time, so that a "
    "student cannot attend both in full?",
    key="Art and Music, and Drama and Sport",
    verify=", and ".join(f"{a} and {b}" for a, b in _clash),
    wrong=["Art and Music only", "Drama and Sport only",
           "Music and Drama, and Drama and Sport"],
    expl="Music starts at 10:00 while Art runs until 10:15, so those two overlap by 15 "
         "minutes. Sport starts at 12:15 while Drama runs until 12:30, another 15-minute "
         "overlap. Music ends at 11:00 and Drama begins at 11:15, so those two do not clash.",
    fig=TT, difficulty="hard", confidence=0.90),

B.Q("calendar_scheduling",
    "Three students take turns to feed the class fish, in the order Ana, Bo, Cam, Ana, Bo, "
    "Cam and so on. Ana feeds them on day 1. Who feeds them on day 20?",
    # second route: actually deal out twenty turns rather than reasoning modulo 3
    key=["Ana", "Bo", "Cam"][(20 - 1) % 3],
    verify=list(itertools.islice(itertools.cycle(["Ana", "Bo", "Cam"]), 20))[-1],
    wrong=["Ana", "Cam", "it depends on the weekend"],
    expl="The turn repeats every 3 days, and 20 is 18 plus 2, so day 20 holds the second "
         "turn of a round: Bo. Day 19 would be Ana and day 21 Cam.",
    difficulty="hard", confidence=0.91),

B.Q("calendar_scheduling",
    "A project is due on Friday 20 June. A student wants to finish it 9 days early. On "
    "which date should it be finished?",
    # second route: step back one day at a time rather than subtracting
    key=20 - 9, verify=[d for d in range(20, 0, -1)][9],
    wrong=[20 - 7, 20 + 9, 9],
    expl="Nine days before the 20th is the 11th, since 20 - 9 = 11. Taking off 7 gives the "
         "13th, which is a week early rather than nine days, and adding 9 goes past the due "
         "date altogether.",
    fmt=lambda v: f"{v} June"),

B.Q("calendar_scheduling",
    "A bus leaves the depot every 25 minutes, starting at 7:00 am. What time does the "
    "fourth bus of the day leave?",
    key="8:15 am", verify=f"{7 + (3 * 25) // 60}:{(3 * 25) % 60:02d} am",
    wrong=["8:40 am", "7:75 am", "7:25 am"],
    expl="The first bus goes at 7:00, so the fourth is three gaps later: 3 x 25 = 75 "
         "minutes, which is 1 hour 15 minutes, giving 8:15 am. 8:40 counts four gaps rather "
         "than three, and 7:75 is not a time at all.",
    difficulty="hard", confidence=0.91),

B.Q("calendar_scheduling",
    "A term runs for 10 weeks. Assembly is held every second week, in weeks 2, 4, 6 and so "
    "on. How many assemblies are held in the term?",
    key=len([w for w in range(1, 11) if w % 2 == 0]), verify=10 // 2,
    wrong=[10, 4, 6],
    expl="Assemblies fall in weeks 2, 4, 6, 8 and 10 — five of them. 10 counts every week of "
         "term rather than the assembly weeks.",
    fmt=lambda v: f"{v} assemblies"),

# ===================================================== truth-teller (8)

_t1 = truth(["Ana", "Ben"],
            [lambda t: t["Ana"] == (not t["Ben"]),                    # Ana: "Ben is lying"
             lambda t: t["Ben"] == (not t["Ana"] and not t["Ben"])])  # Ben: "we both lie"
B.Q("truth_teller",
    "Ana says: 'Ben is lying.' Ben says: 'Both of us are lying.' Who is telling the truth?",
    key=[n for n, v in _t1.items() if v][0] if any(_t1.values()) else "nobody",
    verify="Ana",
    wrong=["Ben", "both of them", "neither of them"],
    expl="Ben cannot be truthful: if he were, his own claim that he is lying would make him "
         "a liar. So Ben is lying, which means his claim that both lie is false — at least "
         "one of them tells the truth, and it cannot be Ben, so it is Ana. That fits Ana's "
         "own statement, which says Ben is lying.",
    difficulty="hard", confidence=0.90),

_t2 = truth(["Cara", "Dev", "Eli"],
            [lambda t: sum(t.values()) == 1,
             lambda t: t["Cara"] == (not t["Dev"]),
             lambda t: t["Dev"] == (not t["Eli"]),
             lambda t: t["Eli"] == (not t["Cara"] and not t["Dev"])])
B.Q("truth_teller",
    "Cara says: 'Dev is lying.' Dev says: 'Eli is lying.' Eli says: 'Both Cara and Dev are "
    "lying.' Exactly one of the three is telling the truth. Who is it?",
    key=[n for n, v in _t2.items() if v][0], verify="Dev",
    wrong=["Cara", "Eli", "it cannot be worked out"],
    expl="If Cara were truthful then Dev would be lying, so Eli would be truthful too — two "
         "truth-tellers, which is not allowed. If Eli were truthful then Cara and Dev both "
         "lie, but Cara lying means Dev is truthful, another contradiction. Dev alone works: "
         "Dev truthful makes Eli a liar, and Cara a liar as well.",
    difficulty="hard", confidence=0.90),

# two boxes cannot do it: whichever box holds the prize, exactly one label comes out
# true, so the puzzle has two answers. Three boxes break the symmetry.
_box = ([b for b in ("box 1", "box 2", "box 3")
         if [b == "box 2", b != "box 2", b != "box 1"].count(True) == 1] + ["AMBIGUOUS"])[0]
B.Q("truth_teller",
    "Three boxes each carry a label. Box 1 says: 'The prize is in box 2.' Box 2 says: 'The "
    "prize is not in this box.' Box 3 says: 'The prize is not in box 1.' Exactly one label "
    "is true. Where is the prize?",
    key="in box 1", verify=f"in {_box}",
    wrong=["in box 2", "in box 3", "it cannot be worked out"],
    expl="If the prize were in box 2, box 1 and box 3 would both be right — two true "
         "labels. If it were in box 3, box 2 and box 3 would both be right. Only the prize "
         "in box 1 leaves a single true label, box 2's.",
    difficulty="hard", confidence=0.90),

_t4 = truth(["Fay", "Gus"],
            [lambda t: t["Fay"] == (t["Fay"] and t["Gus"]),   # Fay: "we are both truthful"
             lambda t: t["Gus"] == (not t["Fay"])])            # Gus: "Fay is lying"
B.Q("truth_teller",
    "Fay says: 'Both of us are telling the truth.' Gus says: 'Fay is lying.' Who is telling "
    "the truth?",
    key="Gus only", verify="Gus only" if _t4 == {"Fay": False, "Gus": True} else "MISMATCH",
    wrong=["Fay only", "both of them", "neither of them"],
    expl="If Fay were truthful, Gus would be truthful too — but Gus says Fay is lying, which "
         "would make Fay a liar. So Fay is lying, and Gus's statement that Fay is lying is "
         "true. Gus alone tells the truth.",
    difficulty="hard", confidence=0.91),

B.Q("truth_teller",
    "Three children are asked who broke a window. Hana says: 'It was not me.' Ivan says: "
    "'It was Hana.' Jo says: 'It was not Ivan.' Exactly one of them is telling the truth, "
    "and exactly one broke the window. Who broke it?",
    # "exactly one is LYING" would leave both Hana and Jo fitting; only "exactly one is
    # telling the truth" pins it down, and the search is what showed that
    key="Ivan",
    verify=([who for who in ("Hana", "Ivan", "Jo")
             if [who != "Hana", who == "Hana", who != "Ivan"].count(True) == 1] + ["AMBIGUOUS"])[0],
    wrong=["Hana", "Jo", "it cannot be worked out"],
    expl="If Hana broke it, Ivan and Jo are both right — two truths. If Jo broke it, Hana "
         "and Jo are both right — two again. If Ivan broke it, Hana is right but Ivan and "
         "Jo are both wrong, which is the one truth the question calls for.",
    difficulty="hard", confidence=0.90),

_t6 = truth(["Kit", "Lou", "Max"],
            [lambda t: sum(t.values()) == 2,
             lambda t: t["Kit"] == t["Lou"],
             lambda t: t["Lou"] == (not t["Max"]),
             lambda t: t["Max"] == (sum(t.values()) == 1)])
B.Q("truth_teller",
    "Kit says: 'Lou is telling the truth.' Lou says: 'Max is lying.' Max says: 'Only one of "
    "us is telling the truth.' Exactly two of the three are telling the truth. Which one of "
    "them is lying?",
    key="Max",
    verify=([n for n, v in _t6.items() if not v] + ["AMBIGUOUS"])[0],
    wrong=["Kit", "Lou", "it cannot be worked out"],
    expl="Two of the three are truthful, so Max's claim that only one is truthful is false, "
         "making Max the liar. That leaves Kit and Lou as the two truth-tellers, and both "
         "their statements hold: Kit says Lou is truthful, which is right, and Lou says Max "
         "is lying, which is also right.",
    difficulty="hard", confidence=0.90),

B.Q("truth_teller",
    "In a game, everybody in the red team always tells the truth and everybody in the blue "
    "team always lies. A player says: 'I am in the blue team.' Which team is the player in?",
    key="neither — nobody could say that",
    verify="neither — nobody could say that",
    wrong=["the red team", "the blue team", "it cannot be worked out"],
    expl="A red player always tells the truth, so a red player could not claim to be blue. A "
         "blue player always lies, so a blue player could not truthfully admit to being "
         "blue either — the claim would be true, which a liar cannot say. No player of "
         "either team could say it.",
    difficulty="hard", confidence=0.90),

_t8 = truth(["Nina", "Omar"],
            # Nina SAYS they match, which is not the same as them matching
            [lambda t: t["Nina"] == (t["Nina"] == t["Omar"]),
             lambda t: t["Omar"] == (not t["Nina"])])   # Omar: "Nina is lying"
B.Q("truth_teller",
    "Nina says: 'Omar and I are either both telling the truth or both lying.' Omar says: "
    "'Nina is lying.' Who is telling the truth?",
    key="Omar only", verify="Omar only" if _t8 == {"Nina": False, "Omar": True} else "MISMATCH",
    wrong=["Nina only", "both of them", "neither of them"],
    expl="If Nina were truthful, she and Omar would match, so Omar would be truthful too — "
         "but Omar says Nina is lying, which contradicts it. So Nina is lying, and her claim "
         "that they match is false, meaning they differ: Omar is truthful, which is exactly "
         "what his own statement says.",
    difficulty="hard", confidence=0.91),

if __name__ == "__main__":
    B.write()
