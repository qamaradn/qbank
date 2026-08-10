#!/usr/bin/env python3
"""Builds lr_thinking_skills_p22.json — 32 more §5.3 problem-solving questions.

numeric deduction 12, logic grid 10, optimisation 10. §5.3 goes 123/330 to 155/330;
Thinking Skills reaches 583/880.

First batch to import the search helpers from lr_logic rather than carry its own. p18
and p19 keep their copies deliberately — both are loaded, and rebuilding either would
mint fresh uuids and orphan the database rows.

The three categories here each get the guarantee that suits them. only() enumerates
every candidate number; solve() enumerates every assignment; best() enumerates every
choice and refuses on a tie. All three fail the build rather than shipping a question
with no answer or with two, which is the pair of defects that reading does not catch.

Every item is also checked against p18 and p19 for shape, not just for stem similarity:
those two batches already hold coin, crate, rope and bus-ticket optimisations, so this
one takes different ground.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.figure_lib import table  # noqa: E402
from tools.lr.lr_common import Batch  # noqa: E402
from tools.lr.lr_logic import best, only, solve  # noqa: E402

B = Batch(nn=22)

# ===================================================== numeric deduction (12)

_a1 = only(range(1, 40), lambda n: n % 6 == 4 and n % 5 == 3)
B.Q("numeric_deduction",
    "A teacher has fewer than 40 counters. Sharing them between 6 children leaves 4 over. "
    "Sharing them between 5 children leaves 3 over. How many counters are there?",
    key=_a1, verify=only([n for n in range(1, 40) if n % 5 == 3], lambda n: n % 6 == 4),
    wrong=[22, 34, 18],
    expl="The numbers under 40 leaving 4 after sharing by 6 are 4, 10, 16, 22, 28 and 34. "
         "Sharing each by 5 leaves 4, 0, 1, 2, 3 and 4, so only 28 leaves the 3 that is "
         "wanted. 22 fits the first clue but leaves 2 after sharing by 5.",
    difficulty="hard", confidence=0.91),

_a2 = only(range(1, 19), lambda a: a * (19 - a) == 88 and a > 19 - a)
B.Q("numeric_deduction",
    "Two sisters' ages add up to 19 and multiply to 88. How old is the older sister?",
    key=_a2, verify=max(a for a in range(1, 19) if a * (19 - a) == 88),
    wrong=[8, 9, 12],
    expl="Pairs adding to 19 are 1 and 18, 2 and 17, and so on. Only 8 and 11 multiply to "
         "88, so the older sister is 11 and the younger is 8.",
    fmt=lambda v: f"{v} years old", difficulty="hard", confidence=0.91),

_w3 = only(range(1, 50), lambda w: w * 3 * w == 48)
B.Q("numeric_deduction",
    "A rectangle has an area of 48 square centimetres. Its length is 3 times its width. "
    "What is its perimeter?",
    key=2 * (_w3 + 3 * _w3), verify=only(range(1, 200), lambda p: p == 2 * (4 + 12)),
    wrong=[48, 16, 24],
    expl="If the width is 4 cm the length is 12 cm, and 4 x 12 = 48, so those are the "
         "sides. The perimeter is 4 + 12 + 4 + 12 = 32 cm. Answering 16 gives only the "
         "width plus the length.",
    fmt=lambda v: f"{v} cm", difficulty="hard", confidence=0.90),

_r4 = only(range(0, 461), lambda r: 3 * (r + 20) + 2 * r == 460)
B.Q("numeric_deduction",
    "Three pencils and two rubbers cost $4.60 altogether. A pencil costs 20c more than a "
    "rubber. What does one pencil cost?",
    key=f"${(_r4 + 20) / 100:.2f}", verify=f"${(460 - 3 * 20) / 5 / 100 + 0.20:.2f}",
    wrong=["$0.80", "$0.92", "$1.20"],
    expl="Five items cost $4.60, and the three pencils carry 20c extra each. Taking off "
         "that 60c leaves $4.00 for five rubber-priced items, so a rubber is 80c and a "
         "pencil is $1.00. Answering 80c gives the rubber.",
    difficulty="hard", confidence=0.90),

_d5 = only(range(10, 100),
           lambda n: (n % 10) * 10 + n // 10 - n == 27 and n // 10 + n % 10 == 9)
B.Q("numeric_deduction",
    "A two-digit number has digits that add up to 9. Reversing its digits makes a number "
    "27 larger. What is the original number?",
    key=_d5, verify=only(range(10, 100),
                         lambda n: sorted([n // 10, n % 10]) == [3, 6] and n < 50),
    wrong=[63, 45, 18],
    expl="Reversing changes the number by 9 times the difference between the digits, so a "
         "gain of 27 means the digits differ by 3. Adding to 9 as well makes them 3 and 6, "
         "and the smaller digit leads: 36, which reverses to 63.",
    difficulty="hard", confidence=0.90),

_v6 = only(range(0, 100), lambda x: 8 + 15 + 11 + x == 4 * 12)
B.Q("numeric_deduction",
    "Four numbers have an average of 12. Three of them are 8, 15 and 11. What is the "
    "fourth number?",
    key=_v6, verify=4 * 12 - (8 + 15 + 11),
    wrong=[12, 34, 10],
    expl="An average of 12 across four numbers means they total 48. The three given ones "
         "come to 34, so the fourth is 48 - 34 = 14. Answering 34 stops at the total of "
         "the three.",
    difficulty="medium", confidence=0.92),

_c7 = only(range(1, 200), lambda n: n % 4 == 0 and n - n // 2 - n // 4 == 6)
B.Q("numeric_deduction",
    "Half the students in a class walk to school and a quarter cycle. The remaining 6 come "
    "by bus. How many students are in the class?",
    key=_c7, verify=6 * 4,
    wrong=[12, 18, 30],
    expl="Walking and cycling account for three quarters of the class, so the 6 bus "
         "travellers are the last quarter. Four quarters make 24. Answering 12 treats the "
         "6 as a half.",
    fmt=lambda v: f"{v} students", difficulty="hard", confidence=0.91),

_p8 = only(range(1, 200), lambda x: 3 * x - x == 36)
B.Q("numeric_deduction",
    "A rope is cut into two pieces. One piece is 3 times as long as the other, and it is "
    "36 cm longer. How long was the rope before it was cut?",
    key=_p8 + 3 * _p8, verify=4 * (36 // 2),
    wrong=[36, 48, 54],
    expl="The longer piece is 3 times the shorter, so it is 2 shorter-pieces longer. Those "
         "2 come to 36 cm, making the short piece 18 cm and the long one 54 cm — 72 cm "
         "altogether. Answering 54 gives only the longer piece.",
    fmt=lambda v: f"{v} cm", difficulty="hard", confidence=0.90),

_e9 = only(range(1, 60), lambda m: (m - 2) + m + (m + 2) == 54 and m % 2 == 0)
B.Q("numeric_deduction",
    "Three consecutive even numbers add up to 54. What is the largest of them?",
    key=_e9 + 2, verify=54 // 3 + 2,
    wrong=[18, 16, 27],
    expl="The outer two cancel against the middle one, so the middle number is 54 divided "
         "by 3, which is 18. The three are 16, 18 and 20, so the largest is 20. Answering "
         "18 gives the middle one.",
    difficulty="medium", confidence=0.92),

_k10 = only(range(0, 21), lambda c: 4 * c + 2 * (20 - c) == 68)
B.Q("numeric_deduction",
    "A car park holds 20 vehicles, all cars or motorbikes. Between them they have 68 "
    "wheels. How many cars are there?",
    key=_k10, verify=(68 - 2 * 20) // (4 - 2),
    wrong=[6, 17, 14 - 4],
    expl="Twenty motorbikes would have 40 wheels, which is 28 short. Swapping a motorbike "
         "for a car adds 2 wheels each time, so 14 swaps are needed: 14 cars and 6 "
         "motorbikes. Answering 6 gives the motorbike count.",
    fmt=lambda v: f"{v} cars", difficulty="hard", confidence=0.91),

_m11 = only(range(1, 200), lambda s: s // 2 - 4 == 11 and s % 2 == 0)
B.Q("numeric_deduction",
    "Ali spent half of his money, then spent another $4. He had $11 left. How much did he "
    "start with?",
    key=f"${_m11}", verify=f"${(11 + 4) * 2}",
    wrong=["$26", "$15", "$22"],
    expl="Work backwards. Before the $4 he had $15, and that was half his money, so he "
         "started with $30. Answering $15 stops one step early, and $22 doubles the $11 "
         "without putting the $4 back.",
    difficulty="hard", confidence=0.90),

_g12 = only(range(1, 60), lambda a: a + 2 * a + (a + 4) == 60)
B.Q("numeric_deduction",
    "Ana, Bo and Cy share 60 cards. Bo gets twice as many as Ana. Cy gets 4 more than Ana. "
    "How many cards does Bo get?",
    key=2 * _g12, verify=60 - _g12 - (_g12 + 4),
    wrong=[14, 18, 20],
    expl="Ana's share counted four times, plus the extra 4 for Cy, makes 60. So four Ana "
         "shares come to 56 and Ana gets 14, Bo gets 28 and Cy gets 18. Answering 14 gives "
         "Ana's share.",
    fmt=lambda v: f"{v} cards", difficulty="hard", confidence=0.90),

# ===================================================== logic grid (10)

_L1 = solve(["Amara", "Bailey", "Cruz", "Dee"], ["red", "blue", "green", "yellow"],
            [lambda a: a["Amara"] == "green",
             lambda a: a["Bailey"] != "red",
             lambda a: a["Cruz"] == "yellow",
             lambda a: a["Dee"] != "blue"])
B.Q("logic_grid",
    "Amara, Bailey, Cruz and Dee each chose a different coloured folder: red, blue, green "
    "or yellow. Amara chose green and Cruz chose yellow. Bailey did not choose red, and "
    "Dee did not choose blue. Which colour did Bailey choose?",
    key=_L1["Bailey"], verify=({"red", "blue"} - {_L1["Dee"]}).pop(),
    wrong=["red", "green", "yellow"],
    expl="Green and yellow are taken, so red and blue are left for Bailey and Dee. Bailey "
         "does not take red, so Bailey has blue and Dee has red — which also fits Dee not "
         "taking blue.",
    fig=table([["", "red", "blue", "green", "yellow"], ["Amara", "", "", "", ""],
               ["Bailey", "", "", "", ""], ["Cruz", "", "", "", ""],
               ["Dee", "", "", "", ""]]),
    difficulty="medium", confidence=0.92),

_L2 = solve(["Eddie", "Farah", "Gio"], ["Monday", "Tuesday", "Thursday"],
            [lambda a: a["Farah"] != "Monday",
             lambda a: a["Gio"] == "Tuesday",
             lambda a: a["Eddie"] != "Thursday"])
B.Q("logic_grid",
    "Eddie, Farah and Gio each have a music lesson on a different day: Monday, Tuesday or "
    "Thursday. Gio's lesson is on Tuesday. Farah's is not on Monday, and Eddie's is not on "
    "Thursday. Which day is Farah's lesson?",
    key=_L2["Farah"], verify=({"Monday", "Thursday"} - {_L2["Eddie"]}).pop(),
    wrong=["Monday", "Tuesday", "it cannot be worked out"],
    expl="Gio has Tuesday, leaving Monday and Thursday for Eddie and Farah. Farah is not "
         "on Monday, so Farah has Thursday and Eddie has Monday.",
    difficulty="medium", confidence=0.92),

_L3 = solve(["Hana", "Ines", "Jai", "Kofi"], ["dog", "cat", "rabbit", "fish"],
            [lambda a: a["Hana"] in ("dog", "cat"),
             lambda a: a["Ines"] == "fish",
             lambda a: a["Jai"] != "dog",
             lambda a: a["Kofi"] == "rabbit"])
B.Q("logic_grid",
    "Hana, Ines, Jai and Kofi each keep a different pet: a dog, a cat, a rabbit or a fish. "
    "Ines keeps the fish and Kofi keeps the rabbit. Hana keeps either the dog or the cat. "
    "Jai does not keep the dog. Which pet does Hana keep?",
    key=_L3["Hana"], verify=({"dog", "cat"} - {_L3["Jai"]}).pop(),
    wrong=["the cat", "the rabbit", "the fish"],
    expl="The fish and rabbit are taken, so the dog and cat go to Hana and Jai. Jai does "
         "not keep the dog, so Jai has the cat and Hana has the dog.",
    fmt=lambda v: f"the {v}" if not v.startswith("the") else v,
    fig=table([["", "dog", "cat", "rabbit", "fish"], ["Hana", "", "", "", ""],
               ["Ines", "", "", "", ""], ["Jai", "", "", "", ""],
               ["Kofi", "", "", "", ""]]),
    difficulty="hard", confidence=0.91),

_L4 = solve(["Lily", "Mo", "Nadia"], ["maths", "science", "history"],
            [lambda a: a["Lily"] != "science",
             lambda a: a["Mo"] != "science",
             lambda a: a["Lily"] != "maths"])
B.Q("logic_grid",
    "Lily, Mo and Nadia each chose a different favourite subject: maths, science or "
    "history. Neither Lily nor Mo chose science. Lily did not choose maths either. Which "
    "subject did Mo choose?",
    key=_L4["Mo"], verify=({"maths", "history"} - {_L4["Lily"]}).pop(),
    wrong=["science", "history", "it cannot be worked out"],
    expl="Neither Lily nor Mo took science, so Nadia did. Lily did not take maths either, "
         "so Lily has history and Mo has maths.",
    difficulty="hard", confidence=0.91),

_L5 = solve(["Omar", "Pia", "Quinn", "Rae"], ["1st", "2nd", "3rd", "4th"],
            [lambda a: a["Omar"] == "2nd",
             lambda a: a["Pia"] != "1st",
             lambda a: a["Quinn"] == "4th",
             lambda a: a["Rae"] != "3rd"])
B.Q("logic_grid",
    "Omar, Pia, Quinn and Rae finished a race in the first four places. Omar came second "
    "and Quinn came fourth. Pia did not come first, and Rae did not come third. Who came "
    "first?",
    key="Rae", verify=next(n for n, p in _L5.items() if p == "1st"),
    wrong=["Omar", "Pia", "Quinn"],
    expl="Second and fourth are taken, so first and third belong to Pia and Rae. Pia did "
         "not come first, so Pia came third and Rae came first — which also fits Rae not "
         "coming third.",
    difficulty="medium", confidence=0.92),

_L6 = solve(["Sam", "Tess", "Uri"], ["sandwich", "salad", "soup"],
            [lambda a: a["Sam"] != "soup",
             lambda a: a["Tess"] == "salad",
             lambda a: a["Uri"] != "sandwich"])
B.Q("logic_grid",
    "Sam, Tess and Uri each ordered a different lunch: a sandwich, a salad or a soup. Tess "
    "ordered the salad. Sam did not order the soup, and Uri did not order the sandwich. "
    "What did Uri order?",
    key=_L6["Uri"], verify=({"sandwich", "soup"} - {_L6["Sam"]}).pop(),
    wrong=["the sandwich", "the salad", "it cannot be worked out"],
    expl="Tess took the salad, leaving the sandwich and the soup. Uri did not take the "
         "sandwich, so Uri had the soup and Sam had the sandwich.",
    fmt=lambda v: f"the {v}" if not v.startswith(("the", "it")) else v,
    difficulty="medium", confidence=0.92),

# "went to Perth or Hobart, but not Hobart" says Perth the long way round. The clue is
# load-bearing — without it Xan and Yui are interchangeable and the puzzle has two
# answers — so it is restated rather than dropped.
_L7 = solve(["Vero", "Wes", "Xan", "Yui"], ["Perth", "Hobart", "Darwin", "Cairns"],
            [lambda a: a["Wes"] == "Darwin",
             lambda a: a["Xan"] == "Perth",
             lambda a: a["Yui"] != "Hobart"])
B.Q("logic_grid",
    "Vero, Wes, Xan and Yui each visited a different city: Perth, Hobart, Darwin or "
    "Cairns. Wes went to Darwin and Xan went to Perth. Yui did not go to Hobart. Which "
    "city did Vero visit?",
    key=_L7["Vero"], verify=({"Hobart", "Cairns"} - {_L7["Yui"]}).pop(),
    wrong=["Perth", "Darwin", "Cairns"],
    expl="Xan takes Perth and Wes takes Darwin, leaving Hobart and Cairns for Vero and "
         "Yui. Yui did not go to Hobart, so Yui went to Cairns and Vero went to Hobart.",
    fig=table([["", "Perth", "Hobart", "Darwin", "Cairns"], ["Vero", "", "", "", ""],
               ["Wes", "", "", "", ""], ["Xan", "", "", "", ""],
               ["Yui", "", "", "", ""]]),
    difficulty="hard", confidence=0.90),

_L8 = solve(["Zara", "Ash", "Bea"], ["violin", "cello", "flute"],
            [lambda a: a["Zara"] != "cello",
             lambda a: a["Ash"] == "flute",
             lambda a: a["Bea"] != "violin"])
B.Q("logic_grid",
    "Zara, Ash and Bea each play a different instrument in the trio: the violin, the cello "
    "or the flute. Ash plays the flute. Zara does not play the cello, and Bea does not "
    "play the violin. Which instrument does Zara play?",
    key=_L8["Zara"], verify=({"violin", "cello"} - {_L8["Bea"]}).pop(),
    wrong=["the cello", "the flute", "it cannot be worked out"],
    expl="Ash has the flute, so the violin and cello go to Zara and Bea. Zara does not "
         "play the cello, so Zara has the violin and Bea the cello.",
    fmt=lambda v: f"the {v}" if not v.startswith(("the", "it")) else v,
    difficulty="medium", confidence=0.92),

_L9 = solve(["Cody", "Dara", "Emi", "Fin"], ["swimming", "athletics", "tennis", "rowing"],
            [lambda a: a["Cody"] == "tennis",
             lambda a: a["Dara"] != "swimming",
             lambda a: a["Emi"] == "rowing",
             lambda a: a["Fin"] != "athletics"])
B.Q("logic_grid",
    "Cody, Dara, Emi and Fin each entered a different event: swimming, athletics, tennis "
    "or rowing. Cody entered tennis and Emi entered rowing. Dara did not enter swimming, "
    "and Fin did not enter athletics. Which event did Fin enter?",
    key=_L9["Fin"], verify=({"swimming", "athletics"} - {_L9["Dara"]}).pop(),
    wrong=["athletics", "tennis", "rowing"],
    expl="Tennis and rowing are taken, so swimming and athletics are left for Dara and "
         "Fin. Dara did not enter swimming, so Dara has athletics and Fin has swimming.",
    difficulty="medium", confidence=0.92),

_L10 = solve(["Gus", "Hema", "Ivo"], ["bus", "train", "ferry"],
             [lambda a: a["Gus"] != "ferry",
              lambda a: a["Hema"] != "ferry",
              lambda a: a["Gus"] != "train"])
B.Q("logic_grid",
    "Gus, Hema and Ivo each travel to work a different way: by bus, by train or by ferry. "
    "Neither Gus nor Hema takes the ferry. Gus does not take the train either. How does "
    "Hema travel?",
    key=_L10["Hema"], verify=({"bus", "train"} - {_L10["Gus"]}).pop(),
    wrong=["by bus", "by ferry", "it cannot be worked out"],
    expl="Neither Gus nor Hema takes the ferry, so Ivo does. Gus does not take the train "
         "either, so Gus takes the bus and Hema the train.",
    fmt=lambda v: f"by {v}" if not v.startswith(("by", "it")) else v,
    difficulty="hard", confidence=0.91),

# ===================================================== optimisation (10)

_o1 = -(-100 // 12)
B.Q("optimisation",
    "A lift carries at most 12 people. A group of 100 people needs to go up. What is the "
    "smallest number of trips the lift must make?",
    key=_o1, verify=only(range(1, 30), lambda t: 12 * t >= 100 and 12 * (t - 1) < 100),
    wrong=[8, 12, 100 // 12 + 2],
    expl="Eight trips carry 96 people, which leaves 4 behind, so a ninth trip is needed "
         "with only 4 aboard. Answering 8 forgets those last four.",
    fmt=lambda v: f"{v} trips", difficulty="medium", confidence=0.92),

_REAMS, _LOOSE = 2 * 6.00, 500 * 0.03
_o2, _ = best(["two reams", "loose sheets"],
              lambda k: {"two reams": _REAMS, "loose sheets": _LOOSE}[k])
B.Q("optimisation",
    "A school needs 500 sheets of paper. A ream of 250 sheets costs $6.00, and loose "
    "sheets cost 3c each. Which is the cheaper way to buy 500 sheets, and by how much?",
    key="two reams, by $3", verify=f"{_o2}, by ${abs(_REAMS - _LOOSE):.0f}",
    wrong=["loose sheets, by $3", "two reams, by $9", "loose sheets, by $9"],
    expl="Two reams cost $12.00. Five hundred loose sheets at 3c each cost $15.00. The "
         "reams are cheaper by $3.",
    difficulty="hard", confidence=0.90),

_o3, _ = best(["the flat rate", "the hourly rate"],
              lambda k: {"the flat rate": 15 + 3 * 4, "the hourly rate": 6 * 4}[k])
B.Q("optimisation",
    "A bike can be hired two ways: $15 plus $3 an hour, or $6 an hour with no extra "
    "charge. Someone wants the bike for 4 hours. Which way is cheaper?",
    key=_o3, verify="the hourly rate" if 6 * 4 < 15 + 3 * 4 else "the flat rate",
    wrong=["the flat rate", "they cost the same", "it depends on the day"],
    expl="Four hours on the $15 plan costs $15 + $12 = $27. Four hours at $6 an hour costs "
         "$24. The hourly rate wins at 4 hours, though the flat rate takes over once the "
         "hire runs past 5 hours.",
    difficulty="hard", confidence=0.90),

_o4 = only(range(0, 20), lambda n: 12 * n <= 50 and 12 * (n + 1) > 50)
B.Q("optimisation",
    "Concert tickets cost $12 each. A student has $50 to spend. What is the greatest "
    "number of tickets the student can buy, and how much is left over?",
    key="4 tickets, with $2 left", verify=f"{_o4} tickets, with ${50 - 12 * _o4} left",
    wrong=["4 tickets, with $8 left", "5 tickets, with $2 left",
           "3 tickets, with $14 left"],
    expl="Four tickets cost $48, leaving $2, and a fifth would need $60. Answering $8 left "
         "subtracts from $56 rather than from $50.",
    difficulty="medium", confidence=0.92),

DIST = table([["", "to town", "to lake", "to camp"], ["from gate", "6 km", "4 km", "9 km"],
              ["from town", "-", "3 km", "5 km"], ["from lake", "3 km", "-", "2 km"]])
_routes = {"gate to camp directly": 9, "gate to town to camp": 6 + 5,
           "gate to lake to camp": 4 + 2, "gate to lake to town to camp": 4 + 3 + 5}
_o5, _o5v = best(list(_routes), lambda k: _routes[k])
B.Q("optimisation",
    "The table gives the distances between four points on a walking track. A walker "
    "starting at the gate wants to reach the camp. Which route is shortest?",
    key=_o5, verify=min(_routes, key=_routes.get),
    wrong=[k for k in _routes if k != _o5],
    expl="Straight to the camp is 9 km. Through the town is 6 + 5 = 11 km. Through the "
         "lake is 4 + 2 = 6 km, which is the shortest. Going through both the lake and the "
         "town comes to 12 km.",
    fig=DIST, difficulty="hard", confidence=0.90),

_NEEDED = -(-50 // 4)                                   # 50 m2 at 4 m2 a litre, rounded up
_paint = {"thirteen 1 L tins": (13, 13 * 9),
          "three 4 L tins and one 1 L tin": (13, 3 * 30 + 9),
          "four 4 L tins": (16, 4 * 30),
          "two 4 L tins and five 1 L tins": (13, 2 * 30 + 5 * 9)}
for _name, (_litres, _) in _paint.items():
    if _litres < _NEEDED:
        raise AssertionError(f"{_name} gives {_litres} L but {_NEEDED} L are needed")
_o6, _ = best(list(_paint), lambda k: _paint[k][1])
B.Q("optimisation",
    "One litre of paint covers 4 square metres. A wall of 50 square metres must be "
    "covered. Paint is sold in 4 L tins for $30 and 1 L tins for $9. Which purchase covers "
    "the wall most cheaply?",
    key=_o6, verify=min(_paint, key=lambda k: _paint[k][1]),
    wrong=["thirteen 1 L tins", "four 4 L tins", "two 4 L tins and five 1 L tins"],
    expl="Fifty square metres needs 13 litres. Three 4 L tins give 12 litres for $90, and "
         "one more litre for $9 makes 13 litres and $99. Four 4 L tins give 16 litres but "
         "cost $120, and thirteen single litres cost $117.",
    difficulty="hard", confidence=0.90),

_o7 = only(range(1, 40), lambda p: (p - 1) * 3 == 30)
B.Q("optimisation",
    "A straight fence 30 metres long needs a post every 3 metres, including one at each "
    "end. What is the smallest number of posts needed?",
    key=_o7, verify=30 // 3 + 1,
    wrong=[10, 9, 30],
    expl="Thirty metres divided into 3 metre gaps gives 10 gaps, and a straight fence "
         "needs one more post than it has gaps: 11. Answering 10 counts the gaps rather "
         "than the posts.",
    fmt=lambda v: f"{v} posts", difficulty="hard", confidence=0.91),

def _juice_cost(b):
    return 320 * (b - b // 3)                           # cents; every third bottle is free
_o8 = only(range(1, 40),
           lambda b: _juice_cost(b) <= 1920 and _juice_cost(b + 1) > 1920, "count")
B.Q("optimisation",
    "A shop sells juice at $3.20 a bottle, with a three-for-the-price-of-two offer. What "
    "is the greatest number of bottles that can be taken away for $19.20?",
    key=f"{_o8} bottles", verify=f"{1920 // 320 // 2 * 3} bottles",
    wrong=["6 bottles", "8 bottles", "12 bottles"],
    expl="$19.20 pays for 6 bottles at full price. Under the offer every two paid bottles "
         "bring a third free, so 6 paid gives 3 free: 9 in all. Answering 6 ignores the "
         "offer entirely.",
    difficulty="hard", confidence=0.90),

_packs = [(f, s) for f in range(0, 9) for s in range(0, 9) if 6 * f + 4 * s == 30]
_o9 = min(f + s for f, s in _packs)
B.Q("optimisation",
    "Bread rolls come in packs of 6 and packs of 4. Exactly 30 rolls are needed, with none "
    "left over. What is the smallest number of packs that will do it?",
    key=_o9, verify=next(n for n in range(1, 12) if any(f + s == n for f, s in _packs)),
    wrong=[6, 7, 4],
    expl="Five packs of 6 make exactly 30 using 5 packs. Mixing them takes more: three "
         "sixes and three fours also make 30 but need 6 packs. Nothing does it in fewer "
         "than 5.",
    fmt=lambda v: f"{v} packs", difficulty="hard", confidence=0.90),

_plans = {"Plan A": 20 + 0, "Plan B": 5 + 300 * 0.06, "Plan C": 300 * 0.08}
_o10, _ = best(list(_plans), lambda k: _plans[k])
B.Q("optimisation",
    "Three phone plans are offered. Plan A costs $20 a month for unlimited calls. Plan B "
    "costs $5 a month plus 6c a minute. Plan C has no monthly fee but charges 8c a minute. "
    "For someone who talks for 300 minutes a month, which plan is cheapest?",
    key=_o10, verify=min(_plans, key=_plans.get),
    wrong=[k for k in _plans if k != _o10] + ["they all cost the same"],
    expl="Plan A is $20. Plan B is $5 + $18 = $23. Plan C is $24. Plan A is cheapest at "
         "300 minutes, and it is the only one whose cost does not rise if the talking "
         "does.",
    difficulty="hard", confidence=0.90),

B.write()
