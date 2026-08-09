#!/usr/bin/env python3
"""Builds lr_thinking_skills_p19.json — 32 more §5.3 problem-solving questions.

numeric deduction 11, ordering and ranking 11, formal syllogism 10. §5.3 goes 91/330
to 123/330, and syllogism_formal opens.

Each of the three carries its own search, in the spirit of p18:

  only()     — enumerate every candidate number and keep those the clues allow, failing
               unless exactly one survives. A number puzzle that quietly admits 7 and 27
               is the arithmetic version of an ambiguous logic grid.

  order()    — enumerate every arrangement, same guarantee.

  entails()  — the strongest of the three. A syllogism is not solved by search but by
               MODEL CHECKING: build every possible world in which the premises hold,
               then keep a conclusion only if it holds in all of them. Run over all four
               options it proves two separate things at once — that the key follows, and
               that no distractor does. Nothing else here can check a distractor.

               Categories are required to be non-empty. That is existential import, the
               traditional reading, and it is the one a Year 6 student actually uses:
               "all wattles are shrubs" is heard as saying there are wattles. Without it
               "some shrubs are wattles" would stop following and half these items would
               lose their key.
"""
import itertools
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.lr.lr_common import Batch  # noqa: E402

B = Batch(nn=19)


def only(cands, pred, what="number"):
    """The single candidate satisfying pred, raising if none or several do."""
    hits = [c for c in cands if pred(c)]
    if len(hits) != 1:
        raise AssertionError(f"{len(hits)} {what}s fit the clues, not 1: {hits[:8]}")
    return hits[0]


def order(names, clues):
    """The single arrangement of `names` satisfying every clue; positions are 1-based."""
    found = []
    for p in itertools.permutations(names):
        pos = {n: i + 1 for i, n in enumerate(p)}
        if all(c(pos) for c in clues):
            found.append(pos)
    if len(found) != 1:
        raise AssertionError(f"{len(found)} arrangements fit, not 1: {found[:4]}")
    return found[0]


def entails(cats, premises, conclusion, n=4):
    """Does `conclusion` hold in every world where `premises` hold?

    A world assigns each category a subset of an n-element universe. Every category is
    required to be non-empty (see the module docstring). Raises if the premises describe
    no world at all, which means the stem contradicts itself.
    """
    universe = range(n)
    subsets = [frozenset(s) for r in range(1, n + 1)
               for s in itertools.combinations(universe, r)]
    models = [dict(zip(cats, a)) for a in itertools.product(subsets, repeat=len(cats))
              if all(p(dict(zip(cats, a))) for p in premises)]
    if not models:
        raise AssertionError(f"premises {cats} describe no possible world — stem is self-contradictory")
    return all(conclusion(m) for m in models)


def syllogism(cats, premises, options, n=4):
    """The one option entailed by the premises, raising unless exactly one is.

    Every option is model-checked, so a distractor that also follows is caught here
    rather than by a student who picks it and is marked wrong.
    """
    good = [text for text, concl in options
            if concl is not None and entails(cats, premises, concl, n)]
    nothing = [text for text, concl in options if concl is None]
    if not good and len(nothing) == 1:
        return nothing[0]
    if len(good) != 1:
        raise AssertionError(f"{len(good)} options are entailed, not 1: {good}")
    if nothing:
        raise AssertionError(f'"{nothing[0]}" cannot be an option when {good} follows')
    return good[0]


# set-logic shorthands over a model dict
def ALL(a, b):
    return lambda m: m[a] <= m[b]


def NO(a, b):
    return lambda m: not (m[a] & m[b])


def SOME(a, b):
    return lambda m: bool(m[a] & m[b])


def SOME_NOT(a, b):
    return lambda m: bool(m[a] - m[b])


# ===================================================== numeric deduction (11)

_n1 = only(range(1, 60), lambda x: (30 - x) >= 0 and x - (30 - x) == 6 and x > 30 - x)
B.Q("numeric_deduction",
    "Two whole numbers add up to 30. One is 6 more than the other. What is the larger "
    "number?",
    key=_n1, verify=(30 + 6) // 2,
    wrong=[12, 24, 15],
    expl="Take the 6 off the total: 30 - 6 = 24 is twice the smaller number, so the smaller "
         "is 12 and the larger is 18. Answering 12 gives the smaller of the two, and 15 "
         "halves the total without allowing for the difference.",
    difficulty="medium", confidence=0.92),

_n2 = only(range(40, 61), lambda x: x % 7 == 0 and sum(int(d) for d in str(x)) == 6)
B.Q("numeric_deduction",
    "A number is between 40 and 60. It is a multiple of 7, and its two digits add up to 6. "
    "What is the number?",
    key=_n2, verify=next(x for x in range(40, 61)
                         if x % 7 == 0 and (x // 10 + x % 10) == 6),
    wrong=[49, 56, 51],
    expl="The multiples of 7 between 40 and 60 are 42, 49 and 56. Their digits add to 6, 13 "
         "and 11, so only 42 fits. 51 has digits adding to 6 but is not a multiple of 7.",
    difficulty="medium", confidence=0.92),

_n3 = only(range(1, 100), lambda x: 3 * x + 4 == 25)
B.Q("numeric_deduction",
    "Sam thinks of a number, multiplies it by 3 and then adds 4. The answer is 25. What "
    "number did Sam think of?",
    key=_n3, verify=(25 - 4) // 3,
    wrong=[9, 21, 87],
    expl="Undo the steps in reverse order: take off the 4 to get 21, then divide by 3 to get "
         "7. Answering 9 divides first and subtracts afterwards, which undoes the steps in "
         "the wrong order.",
    difficulty="medium", confidence=0.92),

_n4 = only(range(1, 60), lambda d: 3 * d + 10 == 2 * (d + 10))
B.Q("numeric_deduction",
    "A mother is 3 times as old as her daughter. In 10 years she will be twice as old as "
    "her daughter. How old is the daughter now?",
    key=_n4, verify=only(range(1, 60), lambda d: (3 * d + 10) / (d + 10) == 2),
    wrong=[5, 15, 30],
    expl="If the daughter is 10 the mother is 30, and in ten years they are 20 and 40 — "
         "twice as old, which fits. At 5 and 15 they would be 15 and 25 in ten years, and "
         "25 is not twice 15.",
    fmt=lambda v: f"{v} years old", difficulty="hard", confidence=0.90),

_n5 = only(range(0, 21), lambda r: r + (r - 4) == 20)
B.Q("numeric_deduction",
    "A bag holds 20 counters, all red or blue. There are 4 more red counters than blue "
    "ones. How many red counters are in the bag?",
    key=_n5, verify=20 - only(range(0, 21), lambda b: b + b + 4 == 20),
    wrong=[8, 16, 10],
    expl="Setting aside the 4 extra red counters leaves 16 to split evenly, so there are 8 "
         "blue and 8 + 4 = 12 red. Answering 8 gives the blue count instead.",
    difficulty="hard", confidence=0.91),

_n6 = only(range(10, 100),
           lambda x: (x // 10) + (x % 10) == 11 and (x // 10) - (x % 10) == 3)
B.Q("numeric_deduction",
    "A two-digit number has digits that add up to 11. The tens digit is 3 more than the "
    "units digit. What is the number?",
    key=_n6, verify=only(range(10, 100),
                         lambda x: sorted([x // 10, x % 10]) == [4, 7] and x > 50),
    wrong=[47, 74 - 9, 92],
    expl="The digits add to 11 and differ by 3, so they are 7 and 4. The tens digit is the "
         "larger, giving 74. Answering 47 puts the digits the other way round.",
    difficulty="hard", confidence=0.91),

_n7 = only(range(1, 40), lambda m: (m - 1) + m + (m + 1) == 48)
B.Q("numeric_deduction",
    "Three consecutive whole numbers add up to 48. What is the middle number?",
    key=_n7, verify=48 // 3,
    wrong=[15, 17, 24],
    expl="The number below and the number above cancel out against the middle one, so the "
         "total is 3 times the middle number: 48 divided by 3 is 16. The three numbers are "
         "15, 16 and 17, so 15 is the smallest rather than the middle.",
    difficulty="medium", confidence=0.92),

_n8 = only(range(0, 7), lambda f: 50 * f + 20 * (6 - f) == 180)
B.Q("numeric_deduction",
    "A purse holds 6 coins, all 20c or 50c, worth $1.80 altogether. How many 50c coins are "
    "in the purse?",
    key=_n8, verify=(180 - 20 * 6) // (50 - 20),
    wrong=[4, 3, 6],
    expl="Six 20c coins would come to $1.20, which is 60c short. Swapping a 20c for a 50c "
         "adds 30c each time, so two swaps are needed: 2 fifty-cent coins and 4 twenty-cent "
         "coins. Answering 4 gives the 20c count.",
    fmt=lambda v: f"{v} coins", difficulty="hard", confidence=0.90),

_n9 = only(range(0, 701), lambda p: p + (p + 300) == 700)
B.Q("numeric_deduction",
    "A pen and a notebook cost $7 altogether. The notebook costs $3 more than the pen. How "
    "much does the pen cost?",
    key=f"${_n9 / 100:.2f}", verify=f"${(700 - 300) / 2 / 100:.2f}",
    wrong=["$3.50", "$4.00", "$5.00"],
    expl="Taking the extra $3 off the total leaves $4 to split evenly, so the pen is $2 and "
         "the notebook $5. Answering $3.50 halves the $7 without allowing for the "
         "difference.",
    difficulty="hard", confidence=0.91),

_w10 = only(range(1, 13), lambda w: 2 * (w + (w + 3)) == 26)
B.Q("numeric_deduction",
    "A rectangle has a perimeter of 26 cm. Its length is 3 cm more than its width. What is "
    "its area?",
    key=(_w10 + 3) * _w10, verify=only(range(1, 200),
                                       lambda a: a == 5 * 8 and 2 * (5 + 8) == 26),
    wrong=[26, 13, 55],
    expl="Half the perimeter is 13 cm, which is the width plus the length. They differ by 3, "
         "so they are 5 cm and 8 cm, and the area is 5 x 8 = 40 square centimetres. "
         "Answering 13 stops at the half-perimeter.",
    fmt=lambda v: f"{v} cm2", difficulty="hard", confidence=0.90),

_n11 = only(range(1, 21), lambda x: x % 5 == 2 and x % 4 == 3)
B.Q("numeric_deduction",
    "A number between 1 and 20 leaves a remainder of 2 when divided by 5, and a remainder "
    "of 3 when divided by 4. What is the number?",
    key=_n11, verify=only([x for x in range(1, 21) if x % 4 == 3], lambda x: x % 5 == 2),
    wrong=[12, 17, 11],
    expl="The numbers under 20 leaving 2 after dividing by 5 are 2, 7, 12 and 17. Dividing "
         "each by 4 leaves 2, 3, 0 and 1, so only 7 leaves the remainder of 3 that is "
         "wanted.",
    difficulty="hard", confidence=0.91),

# ===================================================== ordering and ranking (11)

_r1 = order(["Amy", "Ben", "Cara"],
            [lambda p: p["Amy"] < p["Ben"], lambda p: p["Ben"] < p["Cara"]])
B.Q("ordering_ranking",
    "Amy is taller than Ben. Ben is taller than Cara. Who is the shortest?",
    key=max(_r1, key=_r1.get),
    verify=next(n for n in _r1 if _r1[n] == 3),
    wrong=["Amy", "Ben", "it cannot be worked out"],
    expl="Putting them in a line from tallest to shortest gives Amy, then Ben, then Cara. "
         "Cara is below Ben, who is already below Amy, so Cara is the shortest.",
    difficulty="medium", confidence=0.92),

_r2 = order(["Dan", "Eve", "Fern", "Gil"],
            [lambda p: p["Dan"] < p["Eve"], lambda p: p["Fern"] < p["Dan"],
             lambda p: p["Gil"] == 4])
B.Q("ordering_ranking",
    "Four runners finished a race. Dan finished ahead of Eve. Fern finished ahead of Dan. "
    "Gil came last. Who won?",
    key=next(n for n in _r2 if _r2[n] == 1),
    verify=min(_r2, key=_r2.get),
    wrong=["Dan", "Eve", "Gil"],
    expl="Fern is ahead of Dan, who is ahead of Eve, and Gil is last. That fixes the order "
         "as Fern, Dan, Eve, Gil, so Fern won.",
    difficulty="medium", confidence=0.92),

_r3 = order(["Hugo", "Ivy", "Jed"],
            [lambda p: p["Ivy"] != 1, lambda p: p["Ivy"] != 3,
             lambda p: p["Hugo"] < p["Jed"]])
B.Q("ordering_ranking",
    "Hugo, Ivy and Jed are queuing. Ivy is neither first nor last. Hugo is somewhere ahead "
    "of Jed. Who is last in the queue?",
    key=next(n for n in _r3 if _r3[n] == 3), verify=max(_r3, key=_r3.get),
    wrong=["Hugo", "Ivy", "it cannot be worked out"],
    expl="Ivy is not first or last, so Ivy is in the middle. Hugo is ahead of Jed, so Hugo "
         "is first and Jed is last.",
    difficulty="medium", confidence=0.92),

_r4 = order(["Kim", "Leo", "Mai", "Ned"],
            [lambda p: p["Kim"] < p["Leo"], lambda p: p["Mai"] < p["Kim"],
             lambda p: p["Ned"] < p["Mai"]])
B.Q("ordering_ranking",
    "Four buildings stand in a row of decreasing height. Kim's building is taller than "
    "Leo's. Mai's is taller than Kim's. Ned's is taller than Mai's. Whose building is the "
    "tallest?",
    key=next(n for n in _r4 if _r4[n] == 1), verify=min(_r4, key=_r4.get),
    wrong=["Kim", "Leo", "Mai"],
    expl="Reading the clues as a chain: Ned is above Mai, Mai above Kim, and Kim above Leo. "
         "Ned is at the top of the chain, so Ned's building is tallest and Leo's is "
         "shortest.",
    fmt=lambda v: f"{v}'s", difficulty="hard", confidence=0.91),

_r5 = order(["Ola", "Pip", "Quinn", "Ravi", "Sia"],
            [lambda p: p["Quinn"] == 3, lambda p: p["Ola"] < p["Pip"],
             lambda p: p["Pip"] < p["Quinn"], lambda p: p["Ravi"] < p["Sia"]])
B.Q("ordering_ranking",
    "Five students sat a test and no two scored the same mark. Quinn came third. Ola scored "
    "higher than Pip, and Pip scored higher than Quinn. Ravi scored higher than Sia. Who "
    "came last?",
    key=next(n for n in _r5 if _r5[n] == 5), verify=max(_r5, key=_r5.get),
    wrong=["Ravi", "Quinn", "Pip"],
    expl="Ola and Pip both beat Quinn, who is third, so they take first and second with Ola "
         "first. Ravi and Sia fill fourth and fifth, and Ravi is above Sia, so Sia came "
         "last.",
    difficulty="hard", confidence=0.90),

_r6 = order(["Tia", "Uma", "Vin"],
            [lambda p: p["Tia"] > p["Uma"], lambda p: p["Vin"] > p["Tia"]])
B.Q("ordering_ranking",
    "Three parcels are weighed. Tia's is heavier than Uma's. Vin's is heavier than Tia's. "
    "Which parcel is in the middle by weight?",
    key=f"{next(n for n in _r6 if _r6[n] == 2)}'s",
    verify=f"{sorted(_r6, key=_r6.get)[1]}'s",
    wrong=["Uma's", "Vin's", "it cannot be worked out"],
    expl="Vin's is the heaviest and Uma's the lightest, which leaves Tia's in the middle.",
    difficulty="medium", confidence=0.92),

_r7 = order(["Will", "Xia", "Yan", "Zed"],
            [lambda p: p["Xia"] == p["Will"] + 1, lambda p: p["Yan"] == 1,
             lambda p: p["Zed"] > p["Xia"]])
B.Q("ordering_ranking",
    "Four books sit on a shelf from left to right. Xia's book is immediately to the right "
    "of Will's. Yan's book is at the far left. Zed's book is somewhere to the right of "
    "Xia's. Whose book is third from the left?",
    key=f"{next(n for n in _r7 if _r7[n] == 3)}'s",
    verify=f"{sorted(_r7, key=_r7.get)[2]}'s",
    wrong=["Will's", "Yan's", "Zed's"],
    expl="Yan is first. Will and Xia must sit side by side in that order, and Zed is to the "
         "right of Xia, so the only fit is Yan, Will, Xia, Zed. Xia's book is third.",
    difficulty="hard", confidence=0.90),

_r8 = order(["Ana", "Bo", "Cy", "Di"],
            [lambda p: p["Bo"] < p["Ana"] < p["Cy"], lambda p: p["Di"] < p["Bo"]])
B.Q("ordering_ranking",
    "Four children line up by age, youngest first. Ana is older than Bo but younger than "
    "Cy. Di is younger than Bo. Who is the second youngest?",
    key=next(n for n in _r8 if _r8[n] == 2), verify=sorted(_r8, key=_r8.get)[1],
    wrong=["Ana", "Cy", "Di"],
    expl="Di is younger than Bo, who is younger than Ana, who is younger than Cy. That gives "
         "Di, Bo, Ana, Cy, so Bo is second youngest and Di is the youngest.",
    difficulty="hard", confidence=0.91),

_r9 = order(["Eli", "Fay", "Gus", "Hal", "Ida"],
            [lambda p: p["Gus"] == 3, lambda p: p["Eli"] == p["Gus"] - 1,
             lambda p: p["Ida"] == 5, lambda p: p["Fay"] < p["Eli"]])
B.Q("ordering_ranking",
    "Five children sit in a row of five seats, numbered 1 to 5 from the left. Gus is in "
    "seat 3. Eli is immediately to the left of Gus. Ida is in seat 5. Fay is somewhere to "
    "the left of Eli. Who is in seat 4?",
    key=next(n for n in _r9 if _r9[n] == 4), verify=sorted(_r9, key=_r9.get)[3],
    wrong=["Fay", "Eli", "Ida"],
    expl="Gus is in seat 3 and Eli in seat 2. Fay must be to the left of Eli, so Fay takes "
         "seat 1, and Ida is in seat 5. That leaves seat 4 for Hal.",
    difficulty="hard", confidence=0.90),

_r10 = order(["Jai", "Kit", "Lena"],
             [lambda p: p["Jai"] != 2, lambda p: p["Kit"] > p["Lena"],
              lambda p: p["Lena"] != 1])
B.Q("ordering_ranking",
    "Three swimmers finished a race in first, second and third. Jai did not come second. "
    "Kit finished behind Lena. Lena did not come first. In which place did Jai finish?",
    key={1: "first", 2: "second", 3: "third"}[_r10["Jai"]],
    verify={1: "first", 2: "second", 3: "third"}[
        ({1, 2, 3} - {_r10["Kit"], _r10["Lena"]}).pop()],
    wrong=["second", "third", "it cannot be worked out"],
    expl="Lena is not first and finishes ahead of Kit, so Lena is second and Kit third. That "
         "leaves first place for Jai, which also fits Jai not coming second.",
    difficulty="hard", confidence=0.91),

_r11 = order(["Mo", "Nia", "Oz", "Pia"],
             [lambda p: abs(p["Mo"] - p["Nia"]) == 1, lambda p: p["Oz"] == 1,
              lambda p: p["Pia"] == 4, lambda p: p["Nia"] < p["Mo"]])
B.Q("ordering_ranking",
    "Four people stand in a line. Oz is at the front and Pia is at the back. Mo and Nia "
    "stand next to each other, with Nia closer to the front. Who is directly behind Oz?",
    key=next(n for n in _r11 if _r11[n] == 2), verify=sorted(_r11, key=_r11.get)[1],
    wrong=["Mo", "Pia", "it cannot be worked out"],
    expl="Oz is first and Pia is fourth, so Mo and Nia fill the two middle places. Nia is "
         "closer to the front, so Nia is second and Mo third. Nia is directly behind Oz.",
    difficulty="hard", confidence=0.90),

# ===================================================== formal syllogism (10)

_y1 = syllogism(["wattle", "shrub", "plant"], [ALL("wattle", "shrub"), ALL("shrub", "plant")],
                [("All wattles are plants", ALL("wattle", "plant")),
                 ("All plants are wattles", ALL("plant", "wattle")),
                 ("No wattles are plants", NO("wattle", "plant")),
                 ("Some shrubs are not plants", SOME_NOT("shrub", "plant"))])
B.Q("syllogism_formal",
    "All wattles are shrubs. All shrubs are plants. Which one of these must be true?",
    key=_y1, verify="All wattles are plants",
    wrong=["All plants are wattles", "No wattles are plants",
           "Some shrubs are not plants"],
    expl="Every wattle sits inside the shrubs, and every shrub sits inside the plants, so "
         "every wattle sits inside the plants. The reverse does not follow: there can be "
         "plenty of plants that are not wattles at all.",
    difficulty="medium", confidence=0.92),

_y2 = syllogism(["echidna", "mammal", "reptile"],
                [NO("reptile", "mammal"), ALL("echidna", "mammal")],
                [("No echidnas are reptiles", NO("echidna", "reptile")),
                 ("All mammals are echidnas", ALL("mammal", "echidna")),
                 ("Some echidnas are reptiles", SOME("echidna", "reptile")),
                 ("All reptiles are mammals", ALL("reptile", "mammal"))])
B.Q("syllogism_formal",
    "No reptiles are mammals. All echidnas are mammals. Which one of these must be true?",
    key=_y2, verify="No echidnas are reptiles",
    wrong=["All mammals are echidnas", "Some echidnas are reptiles",
           "All reptiles are mammals"],
    expl="Echidnas are all inside the mammals, and the mammals do not overlap the reptiles "
         "at all, so no echidna can be a reptile. That says nothing about mammals in "
         "general being echidnas.",
    difficulty="medium", confidence=0.92),

_y3 = syllogism(["student", "chess", "planner"],
                [SOME("student", "chess"), ALL("chess", "planner")],
                [("Some students plan ahead", SOME("student", "planner")),
                 ("All students plan ahead", ALL("student", "planner")),
                 ("All planners play chess", ALL("planner", "chess")),
                 ("No students plan ahead", NO("student", "planner"))])
B.Q("syllogism_formal",
    "Some students play chess. Everyone who plays chess plans ahead. Which one of these "
    "must be true?",
    key=_y3, verify="Some students plan ahead",
    wrong=["All students plan ahead", "All planners play chess",
           "No students plan ahead"],
    expl="At least one student plays chess, and every chess player plans ahead, so at least "
         "one student plans ahead. It does not follow that all students do — the ones who "
         "do not play chess are not covered by the second statement.",
    difficulty="hard", confidence=0.91),

_y4 = syllogism(["quokka", "marsupial", "nocturnal"],
                [ALL("quokka", "marsupial"), SOME("marsupial", "nocturnal")],
                [("Some marsupials are quokkas", SOME("marsupial", "quokka")),
                 ("Some quokkas are nocturnal", SOME("quokka", "nocturnal")),
                 ("No quokkas are nocturnal", NO("quokka", "nocturnal")),
                 ("All marsupials are quokkas", ALL("marsupial", "quokka"))])
B.Q("syllogism_formal",
    "All quokkas are marsupials. Some marsupials are nocturnal. Which one of these must be "
    "true?",
    key=_y4, verify="Some marsupials are quokkas",
    wrong=["Some quokkas are nocturnal", "No quokkas are nocturnal",
           "All marsupials are quokkas"],
    expl="Since quokkas exist and every one of them is a marsupial, at least one marsupial "
         "is a quokka. The nocturnal marsupials might be quokkas or might be other "
         "marsupials entirely, so neither statement about quokkas and night can be relied "
         "on.",
    difficulty="hard", confidence=0.90),

_y5 = syllogism(["frog", "native", "canetoad"],
                [NO("canetoad", "native"), ALL("frog", "native")],
                [("No frogs are cane toads", NO("frog", "canetoad")),
                 ("All native animals are frogs", ALL("native", "frog")),
                 ("Some frogs are cane toads", SOME("frog", "canetoad")),
                 ("All cane toads are frogs", ALL("canetoad", "frog"))])
B.Q("syllogism_formal",
    "No cane toads are native animals. All the frogs in this pond are native animals. Which "
    "one of these must be true?",
    key=_y5, verify="No frogs are cane toads",
    wrong=["All native animals are frogs", "Some frogs are cane toads",
           "All cane toads are frogs"],
    expl="The frogs are all native, and nothing native is a cane toad, so none of the frogs "
         "is a cane toad. Native animals as a whole are a much larger group than these "
         "frogs, so the second option overreaches.",
    difficulty="medium", confidence=0.92),

_y6 = syllogism(["chorister", "singer", "ravi"],
                [ALL("chorister", "singer"), NO("ravi", "singer")],
                [("Ravi is not in the choir", NO("ravi", "chorister")),
                 ("Ravi is in the choir", ALL("ravi", "chorister")),
                 ("Everyone who sings is in the choir", ALL("singer", "chorister")),
                 ("Nobody in the choir sings", NO("chorister", "singer"))])
B.Q("syllogism_formal",
    "Everyone in the school choir can sing. Ravi cannot sing. Which one of these must be "
    "true?",
    key=_y6, verify="Ravi is not in the choir",
    wrong=["Ravi is in the choir", "Everyone who sings is in the choir",
           "Nobody in the choir sings"],
    expl="If Ravi were in the choir he would be able to sing, and he cannot, so he is not in "
         "the choir. Working the rule backwards instead — everyone who sings is in the "
         "choir — is a different claim, and the statement never makes it.",
    difficulty="hard", confidence=0.91),

_y7 = syllogism(["cyclist", "helmet", "rider"],
                [ALL("cyclist", "helmet"), ALL("cyclist", "rider")],
                [("Some riders wear helmets", SOME("rider", "helmet")),
                 ("All riders wear helmets", ALL("rider", "helmet")),
                 ("All helmet wearers are cyclists", ALL("helmet", "cyclist")),
                 ("No riders wear helmets", NO("rider", "helmet"))])
B.Q("syllogism_formal",
    "Every cyclist in the club wears a helmet. Every cyclist in the club is a rider. Which "
    "one of these must be true?",
    key=_y7, verify="Some riders wear helmets",
    wrong=["All riders wear helmets", "All helmet wearers are cyclists",
           "No riders wear helmets"],
    expl="The club cyclists are riders and they all wear helmets, so at least some riders "
         "wear helmets. Riders who are not in the club are not covered by the rule, so "
         "nothing can be said about all of them.",
    difficulty="hard", confidence=0.90),

_y8 = syllogism(["emu", "bird", "flier"],
                [ALL("emu", "bird"), SOME_NOT("bird", "flier")],
                [("Some birds are emus", SOME("bird", "emu")),
                 ("Emus cannot fly", NO("emu", "flier")),
                 ("All emus can fly", ALL("emu", "flier")),
                 ("No birds can fly", NO("bird", "flier"))])
B.Q("syllogism_formal",
    "All emus are birds. Some birds cannot fly. Which one of these must be true?",
    key=_y8, verify="Some birds are emus",
    wrong=["Emus cannot fly", "All emus can fly", "No birds can fly"],
    expl="Emus exist and are all birds, so some birds are emus. The birds that cannot fly "
         "might be emus or might be penguins — the statement does not say, so nothing "
         "follows about emus and flying either way.",
    difficulty="hard", confidence=0.90),

_y9 = syllogism(["triangle", "threesided", "shape"],
                [ALL("triangle", "threesided"), ALL("shape", "threesided")],
                [("Some three-sided figures are triangles", SOME("threesided", "triangle")),
                 ("The shape is a triangle", ALL("shape", "triangle")),
                 ("The shape is not a triangle", NO("shape", "triangle")),
                 ("All three-sided figures are triangles", ALL("threesided", "triangle"))])
B.Q("syllogism_formal",
    "All triangles have three sides. A shape drawn on the board has three sides. Which one "
    "of these must be true?",
    key=_y9, verify="Some three-sided figures are triangles",
    wrong=["The shape is a triangle", "The shape is not a triangle",
           "All three-sided figures are triangles"],
    expl="Triangles exist and all have three sides, so some three-sided figures are "
         "triangles. Reading the rule backwards to conclude that this shape must be a "
         "triangle is the common trap — the rule runs from triangle to three sides, not the "
         "other way.",
    difficulty="hard", confidence=0.90),

_y10 = syllogism(["boronia", "flower", "scented"],
                 [ALL("boronia", "flower"), ALL("boronia", "scented")],
                 [("Some flowers are scented", SOME("flower", "scented")),
                  ("All flowers are scented", ALL("flower", "scented")),
                  ("All scented things are boronias", ALL("scented", "boronia")),
                  ("No flowers are scented", NO("flower", "scented"))])
B.Q("syllogism_formal",
    "All boronias are flowers. All boronias are scented. Which one of these must be true?",
    key=_y10, verify="Some flowers are scented",
    wrong=["All flowers are scented", "All scented things are boronias",
           "No flowers are scented"],
    expl="Boronias are both flowers and scented, so at least some flowers are scented. "
         "Flowers that are not boronias are not covered, so it cannot be said that all "
         "flowers are scented.",
    difficulty="hard", confidence=0.91),

B.write()
