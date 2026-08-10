#!/usr/bin/env python3
"""Builds lr_thinking_skills_p25.json — 32 §5.3 questions.

numeric deduction 16, logic grid 16. §5.3 reaches 219/330; Thinking Skills 679/880.

Half the grids here use solve2, which assigns TWO attributes rather than one. The
single-attribute shape runs out: with one mapping there are only so many ways to say
"three people, three things", and eighteen have already been built. Two attributes give
a grid that has to be cross-referenced, which is what the question type looks like in a
real paper — and the search guarantee is unchanged, since solve2 enumerates every pairing
of both permutations and refuses unless exactly one survives.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.figure_lib import table  # noqa: E402
from tools.lr.lr_common import Batch  # noqa: E402
from tools.lr.lr_logic import only, solve, solve2  # noqa: E402

B = Batch(nn=25)

# ===================================================== numeric deduction (16)

_a = only(range(1, 200), lambda n: n * (n + 1) // 2 == 78)
B.Q("numeric_deduction",
    "Adding up all the whole numbers from 1 to some number gives 78. What is that number?",
    key=_a, verify=next(n for n in range(1, 200) if sum(range(1, n + 1)) == 78),
    wrong=[13, 39, 11],
    expl="Adding 1 + 2 + 3 and onwards reaches 78 at 12, since 1 to 12 pairs into six pairs "
         "of 13. Answering 13 goes one too far, giving 91.",
    difficulty="hard", confidence=0.90),

_b = only(range(1, 100), lambda u: 2 * u + 3 * u == 45)
B.Q("numeric_deduction",
    "Two sisters share $45 in the ratio 2 to 3. How much does the one with the larger "
    "share receive?",
    key=f"${3 * _b}", verify=f"${45 * 3 // (2 + 3)}",
    wrong=["$18", "$22.50", "$30"],
    expl="The 45 dollars split into 5 equal parts of $9, so the shares are $18 and $27. "
         "Answering $18 gives the smaller share and $22.50 splits the money evenly.",
    difficulty="hard", confidence=0.90),

_c = only(range(1, 200), lambda p: p * 80 // 100 == 48 and p * 80 % 100 == 0)
B.Q("numeric_deduction",
    "A jacket is reduced by 20 per cent and now costs $48. What was its price before the "
    "reduction?",
    key=f"${_c}", verify=f"${48 * 100 // 80}",
    wrong=["$57.60", "$68", "$96"],
    expl="After a fifth is taken off, $48 is four fifths of the old price, so one fifth is "
         "$12 and the original was $60. Answering $57.60 adds 20 per cent to $48, which is "
         "not the same as undoing a 20 per cent cut.",
    difficulty="hard", confidence=0.90),

_d = only(range(2, 40), lambda n: n * (n - 1) // 2 == 28)
B.Q("numeric_deduction",
    "Everyone at a meeting shook hands once with everyone else. There were 28 handshakes "
    "altogether. How many people were at the meeting?",
    key=_d, verify=next(n for n in range(2, 40) if n * (n - 1) // 2 == 28),
    wrong=[14, 7, 28],
    expl="Each of 8 people shakes 7 hands, giving 56, but that counts every handshake "
         "twice, so there are 28. Answering 14 halves 28 without allowing for the pairing.",
    fmt=lambda v: f"{v} people", difficulty="hard", confidence=0.90),

_e = only(range(0, 21), lambda t: 3 * t + 2 * (20 - t) == 52)
B.Q("numeric_deduction",
    "A shop has 20 bicycles and tricycles altogether, with 52 wheels between them. How many "
    "tricycles are there?",
    key=_e, verify=52 - 2 * 20,
    wrong=[8, 15, 6],
    expl="Twenty bicycles would have 40 wheels, which is 12 short. Each tricycle adds one "
         "wheel, so 12 tricycles and 8 bicycles. Answering 8 gives the bicycles.",
    fmt=lambda v: f"{v} tricycles", difficulty="hard", confidence=0.91),

_f = only(range(1, 300), lambda x: (x * 3 - 8) // 2 == 20 and (x * 3 - 8) % 2 == 0)
B.Q("numeric_deduction",
    "Think of a number, multiply it by 3, take away 8, then halve the result. The answer "
    "is 20. What was the number?",
    key=_f, verify=(20 * 2 + 8) // 3,
    wrong=[24, 12, 32],
    expl="Undo each step backwards: 20 doubled is 40, plus 8 is 48, divided by 3 is 16. "
         "Answering 24 halves before undoing the multiplication.",
    difficulty="hard", confidence=0.90),

_g = only(range(1, 60), lambda m: (m - 2) + m + (m + 2) == 51 and m % 2 == 1)
B.Q("numeric_deduction",
    "A shelf holds three boxes. The middle box holds 2 more pencils than the left one, and "
    "the right box holds 2 more than the middle. All three together hold 51 pencils. How "
    "many are in the left-hand box?",
    key=_g - 2, verify=51 // 3 - 2,
    wrong=[17, 19, 13],
    expl="The extra 2 on one side cancels the missing 2 on the other, so the middle box "
         "holds a third of 51, which is 17. The boxes hold 15, 17 and 19, so the left one "
         "holds 15.",
    fmt=lambda v: f"{v} pencils", difficulty="medium", confidence=0.92),

_h = only(range(1, 200), lambda n: n * 3 // 4 * 2 // 3 == 24 and n % 12 == 0)
B.Q("numeric_deduction",
    "Three quarters of the students in a year group came to the concert. Two thirds of "
    "those who came sang in the choir. If 24 students sang in the choir, how many are in "
    "the year group?",
    key=_h, verify=24 * 3 // 2 * 4 // 3,
    wrong=[36, 32, 18],
    expl="The 24 singers are two thirds of the audience, so 36 came. Those 36 are three "
         "quarters of the year group, so a quarter is 12 and the whole group is 48. "
         "Answering 36 stops at the concert audience without going on to the year group.",
    fmt=lambda v: f"{v} students", difficulty="hard", confidence=0.90),

# 34 and 43 both multiply to 12 and add to 7; the stem's "tens digit is the larger" has
# to be in the search too, or the puzzle has two answers
_i = only(range(10, 100), lambda n: (n // 10) * (n % 10) == 12
          and (n // 10) + (n % 10) == 7 and n // 10 > n % 10)
B.Q("numeric_deduction",
    "A two-digit number has digits that multiply to 12 and add to 7. The tens digit is the "
    "larger. What is the number?",
    key=_i, verify=only(range(10, 100),
                        lambda n: sorted([n // 10, n % 10]) == [3, 4] and n > 40),
    wrong=[34, 26, 62],
    expl="Two digits multiplying to 12 and adding to 7 must be 3 and 4. The tens digit is "
         "the larger, so the number is 43. Answering 34 reverses the digits, and 26 "
         "multiplies to 12 but adds to 8.",
    difficulty="hard", confidence=0.90),

_j = only(range(1, 60), lambda a: a + 24 == 3 * a)
B.Q("numeric_deduction",
    "A father is 24 years older than his son, and this year he is exactly 3 times his "
    "son's age. How old is the son?",
    key=_j, verify=24 // (3 - 1),
    wrong=[8, 24, 36],
    expl="Being 3 times as old means the difference of 24 years is 2 lots of the son's age, "
         "so the son is 12 and the father 36. Answering 36 gives the father's age.",
    fmt=lambda v: f"{v} years old", difficulty="hard", confidence=0.91),

_k = only(range(1, 100), lambda s: s * s == 49)
B.Q("numeric_deduction",
    "A square has an area of 49 square centimetres. What is its perimeter?",
    key=4 * _k, verify=4 * next(s for s in range(1, 100) if s * s == 49),
    wrong=[49, 14, 196],
    expl="A square of area 49 has sides of 7 cm, since 7 x 7 = 49, so the perimeter is 4 x "
         "7 = 28 cm. Answering 14 adds only two sides.",
    fmt=lambda v: f"{v} cm", difficulty="medium", confidence=0.92),

# "the smallest such number" — only() finds every one of them, so the search has to be
# for the first, not for a unique one
_l = next(n for n in range(2, 500) if n % 3 == 1 and n % 4 == 1 and n % 5 == 1)
B.Q("numeric_deduction",
    "A number greater than 1 leaves a remainder of 1 when divided by 3, by 4 and by 5. "
    "What is the smallest such number?",
    key=_l, verify=3 * 4 * 5 + 1,
    wrong=[31, 21, 121],
    expl="A number leaving 1 each time is 1 more than a multiple of 3, 4 and 5 together. "
         "The smallest number divisible by all three is 60, so the answer is 61.",
    difficulty="hard", confidence=0.90),

# integer division lets 99 pass as well as 100, because 99 // 4 rounds down; the seat
# count has to divide by 4 exactly for "a quarter were empty" to mean anything
_m = only(range(1, 400), lambda t: t % 4 == 0 and t - t // 4 - 30 == 45)
B.Q("numeric_deduction",
    "A quarter of the seats in a hall were empty. Of the seats that were filled, 30 held "
    "adults and 45 held children. How many seats are in the hall?",
    key=_m, verify=(30 + 45) * 4 // 3,
    wrong=[75, 94, 120],
    expl="The 75 filled seats are three quarters of the hall, so a quarter is 25 and the "
         "hall has 100 seats. Answering 75 counts only the filled ones.",
    fmt=lambda v: f"{v} seats", difficulty="hard", confidence=0.90),

_n = only(range(1, 60), lambda f: 5 * f + 3 == 6 * f - 2)
B.Q("numeric_deduction",
    "If a teacher gives every student 5 stickers, 3 are left over. If she gives every "
    "student 6, she is 2 short. How many students are there?",
    key=_n, verify=(3 + 2) // (6 - 5),
    wrong=[3, 8, 28],
    expl="Going from 5 each to 6 each needs one more sticker per student, and the supply "
         "swings from 3 spare to 2 short — a change of 5. So there are 5 students, and 28 "
         "stickers. Answering 28 gives the stickers instead.",
    fmt=lambda v: f"{v} students", difficulty="hard", confidence=0.90),

_o = only(range(1, 200), lambda x: x + (x + 7) + (x + 14) == 63)
B.Q("numeric_deduction",
    "Three numbers each 7 more than the one before add up to 63. What is the largest of "
    "them?",
    key=_o + 14, verify=63 // 3 + 7,
    wrong=[14, 21, 35],
    expl="The three numbers average 21, and because the steps are even on each side the "
         "middle one is 21. The three are 14, 21 and 28, so the largest is 28.",
    difficulty="medium", confidence=0.92),

_p = only(range(1, 300), lambda n: n // 2 + n // 3 + 10 == n and n % 6 == 0)
B.Q("numeric_deduction",
    "Half of a bag of marbles is red and a third is blue. The remaining 10 are green. How "
    "many marbles are in the bag?",
    key=_p, verify=10 * 6,
    wrong=[30, 20, 90],
    expl="A half and a third together are five sixths, so the 10 green marbles are the last "
         "sixth. Six sixths make 60. Answering 30 treats the 10 as a third.",
    fmt=lambda v: f"{v} marbles", difficulty="hard", confidence=0.91),

# ===================================================== logic grid (16)

_G1 = solve2(["Ana", "Ben", "Cleo"], ["red", "blue", "green"], ["dog", "cat", "bird"],
             [lambda g: g["Ana"]["a"] == "red",
              lambda g: g["Cleo"]["a"] != "green",
              lambda g: g["Ana"]["b"] != "dog"],
             cross=[lambda g: next(v["a"] for v in g.values() if v["b"] == "cat") == "blue"])
B.Q("logic_grid",
    "Ana, Ben and Cleo each own a different coloured bicycle and a different pet. The "
    "bicycles are red, blue and green; the pets are a dog, a cat and a bird. Ana's bicycle "
    "is red. Cleo's is not green. The one who owns the cat rides the blue bicycle. Ana does "
    "not own the dog. Which pet does Cleo own?",
    key=f'the {_G1["Cleo"]["b"]}',
    # second route: find the cat's owner via the blue bicycle, not via Cleo's row
    verify=f'the {next(v["b"] for v in _G1.values() if v["a"] == "blue")}',
    wrong=["the dog", "the bird", "it cannot be worked out"],
    expl="Ana rides red and Cleo does not ride green, so Cleo rides blue and Ben green. The "
         "cat belongs to whoever rides blue, so Cleo owns the cat. Ana does not own the "
         "dog, so Ana has the bird and Ben the dog.",
    fig=table([["", "red", "blue", "green", "dog", "cat", "bird"],
               ["Ana", "", "", "", "", "", ""], ["Ben", "", "", "", "", "", ""],
               ["Cleo", "", "", "", "", "", ""]]),
    difficulty="hard", confidence=0.91),

_G2 = solve2(["Dan", "Eve", "Fay"], ["Monday", "Tuesday", "Friday"],
             ["swimming", "tennis", "running"],
             [lambda g: g["Dan"]["a"] == "Tuesday",
              lambda g: g["Fay"]["a"] != "Monday",
              lambda g: g["Dan"]["b"] != "running"],
             cross=[lambda g: next(v["a"] for v in g.values()
                                   if v["b"] == "tennis") == "Friday"])
B.Q("logic_grid",
    "Dan, Eve and Fay each train on a different day and at a different sport. The days are "
    "Monday, Tuesday and Friday; the sports are swimming, tennis and running. Dan trains on "
    "Tuesday and Fay does not train on Monday. The one who plays tennis trains on Friday. "
    "Dan does not run. Which sport does Fay do?",
    key=_G2["Fay"]["b"], verify=_G2["Fay"]["b"] if _G2["Fay"]["a"] == "Friday" else "MISMATCH",
    wrong=["swimming", "running", "it cannot be worked out"],
    expl="Dan has Tuesday and Fay is not on Monday, so Fay trains on Friday and Eve on "
         "Monday. Tennis belongs to the Friday trainer, so Fay plays tennis. Dan does not "
         "run, so Dan swims and Eve runs.",
    difficulty="hard", confidence=0.90),

_G4 = solve2(["Kai", "Lia", "Max"], ["7", "8", "9"], ["violin", "piano", "guitar"],
             [lambda g: g["Kai"]["a"] == "9",
              lambda g: g["Max"]["a"] != "8",
              lambda g: g["Kai"]["b"] != "guitar"],
             cross=[lambda g: next(v["a"] for v in g.values() if v["b"] == "piano") == "8"])
B.Q("logic_grid",
    "Kai, Lia and Max are aged 7, 8 and 9, and each plays a different instrument: violin, "
    "piano or guitar. Kai is 9 and Max is not 8. The one who plays the piano is 8. Kai does "
    "not play the guitar. Which instrument does Max play?",
    key=f'the {_G4["Max"]["b"]}',
    verify=f'the {_G4["Max"]["b"]}' if _G4["Max"]["a"] == "7" else "MISMATCH",
    wrong=["the violin", "the piano", "it cannot be worked out"],
    expl="Kai is 9 and Max is not 8, so Max is 7 and Lia is 8. The pianist is 8, so Lia "
         "plays the piano. Kai does not play the guitar, so Kai has the violin and Max the "
         "guitar.",
    difficulty="hard", confidence=0.91),

_G6 = solve2(["Quinn", "Rae", "Sol", "Tia"], ["1st", "2nd", "3rd", "4th"],
             ["red", "blue", "green", "yellow"],
             [lambda g: g["Quinn"]["a"] == "2nd",
              lambda g: g["Sol"]["a"] == "4th",
              lambda g: g["Rae"]["b"] == "blue",
              lambda g: g["Quinn"]["b"] != "yellow"],
             cross=[lambda g: next(v["a"] for v in g.values()
                                   if v["b"] == "green") == "1st"])
B.Q("logic_grid",
    "Quinn, Rae, Sol and Tia finished a race in the first four places, each wearing a "
    "different colour: red, blue, green or yellow. Quinn came second and Sol came fourth. "
    "Rae wore blue. The runner in green came first. Quinn did not wear yellow. Which colour "
    "did Sol wear?",
    key=_G6["Sol"]["b"],
    verify=_G6["Sol"]["b"] if _G6["Tia"]["b"] == "green" else "MISMATCH",
    wrong=["blue", "green", "red"],
    expl="Quinn is second and Sol fourth, so Rae and Tia hold first and third. Green came "
         "first and Rae wore blue, so Tia came first in green and Rae was third. Quinn did "
         "not wear yellow, so Quinn wore red and Sol yellow.",
    fig=table([["", "1st", "2nd", "3rd", "4th", "red", "blue", "green", "yellow"],
               ["Quinn", "", "", "", "", "", "", "", ""],
               ["Rae", "", "", "", "", "", "", "", ""],
               ["Sol", "", "", "", "", "", "", "", ""],
               ["Tia", "", "", "", "", "", "", "", ""]], vw=470),
    difficulty="hard", confidence=0.90),

_G8 = solve2(["Xan", "Yara", "Zed"], ["tea", "juice", "water"], ["toast", "cereal", "eggs"],
             [lambda g: g["Xan"]["a"] == "juice",
              lambda g: g["Zed"]["a"] != "tea",
              lambda g: g["Xan"]["b"] != "cereal"],
             cross=[lambda g: next(v["a"] for v in g.values() if v["b"] == "eggs") == "tea"])
B.Q("logic_grid",
    "Xan, Yara and Zed each had a different drink and a different breakfast. The drinks were "
    "tea, juice and water; the breakfasts were toast, cereal and eggs. Xan drank juice and "
    "Zed did not drink tea. The one who had eggs drank tea. Xan did not have cereal. What "
    "did Zed have for breakfast?",
    key=_G8["Zed"]["b"], verify=_G8["Zed"]["b"] if _G8["Zed"]["a"] == "water" else "MISMATCH",
    wrong=["toast", "eggs", "it cannot be worked out"],
    expl="Xan drank juice and Zed did not drink tea, so Zed drank water and Yara tea. The "
         "eggs went with the tea, so Yara had eggs. Xan did not have cereal, so Xan had "
         "toast and Zed cereal.",
    difficulty="hard", confidence=0.90),

_G10 = solve2(["Eli", "Fen", "Gia"], ["blue", "white", "black"], ["12", "14", "16"],
              [lambda g: g["Eli"]["b"] == "16",
               lambda g: g["Gia"]["b"] != "12",
               lambda g: g["Eli"]["a"] != "blue"],
              cross=[lambda g: next(v["b"] for v in g.values()
                                    if v["a"] == "white") == "12"])
B.Q("logic_grid",
    "Eli, Fen and Gia each have a different coloured phone case and a different number of "
    "apps. The cases are blue, white and black; the app counts are 12, 14 and 16. Eli has 16 "
    "apps and Gia does not have 12. The white case belongs to the one with 12 apps. Eli's "
    "case is not blue. What colour is Gia's case?",
    key=_G10["Gia"]["a"], verify=_G10["Gia"]["a"] if _G10["Fen"]["a"] == "white" else "MISMATCH",
    wrong=["white", "black", "it cannot be worked out"],
    expl="Eli has 16 and Gia does not have 12, so Gia has 14 and Fen 12. The white case goes "
         "with 12 apps, so Fen's case is white. Eli's is not blue, so Eli's is black and "
         "Gia's blue.",
    difficulty="hard", confidence=0.90),

_G12 = solve2(["Kit", "Lena", "Mo", "Nils"], ["maths", "art", "music", "drama"],
              ["Mon", "Tue", "Wed", "Thu"],
              [lambda g: g["Kit"]["a"] == "art",
               lambda g: g["Mo"]["a"] == "drama",
               lambda g: g["Mo"]["b"] == "Wed",
               lambda g: g["Lena"]["b"] == "Thu",
               lambda g: g["Nils"]["b"] != "Tue"],
              cross=[lambda g: next(v["b"] for v in g.values()
                                    if v["a"] == "maths") == "Mon"])
B.Q("logic_grid",
    "Kit, Lena, Mo and Nils each run a different club on a different day. The clubs are "
    "maths, art, music and drama; the days are Monday to Thursday. Kit runs art. Mo runs "
    "drama on Wednesday. Lena's club is on Thursday and Nils's is not on Tuesday. The maths "
    "club meets on Monday. Which club does Lena run?",
    key=_G12["Lena"]["a"],
    verify=_G12["Lena"]["a"] if _G12["Nils"]["b"] == "Mon" else "MISMATCH",
    wrong=["maths", "art", "drama"],
    expl="Mo has Wednesday and Lena Thursday, so Kit and Nils take Monday and Tuesday. "
         "Nils is not on Tuesday, so Nils has Monday and Kit Tuesday. Maths meets on "
         "Monday, so Nils runs maths, and with Kit on art and Mo on drama, Lena runs music.",
    difficulty="hard", confidence=0.90),

_G14 = solve2(["Rio", "Sam", "Tara"], ["north", "south", "east"], ["3", "5", "8"],
              [lambda g: g["Rio"]["a"] == "east",
               lambda g: g["Tara"]["a"] != "north",
               lambda g: g["Rio"]["b"] != "5"],
              cross=[lambda g: next(v["b"] for v in g.values()
                                    if v["a"] == "north") == "3"])
B.Q("logic_grid",
    "Rio, Sam and Tara live in different parts of town — north, south or east — and are "
    "different distances from school: 3 km, 5 km or 8 km. Rio lives in the east and Tara "
    "does not live in the north. Whoever lives in the north is 3 km from school. Rio does "
    "not live 5 km away. How far from school does Tara live?",
    key=f'{_G14["Tara"]["b"]} km',
    verify=f'{_G14["Tara"]["b"]} km' if _G14["Sam"]["b"] == "3" else "MISMATCH",
    wrong=["3 km", "8 km", "it cannot be worked out"],
    expl="Rio is in the east and Tara is not in the north, so Tara is in the south and Sam "
         "in the north. The northern one is 3 km away, so Sam is 3 km. Rio is not 5 km, so "
         "Rio is 8 km and Tara 5 km.",
    difficulty="hard", confidence=0.91),

_G16 = solve2(["Yas", "Zane", "Ada"], ["cat", "dog", "fish"], ["Mia", "Bo", "Rex"],
              [lambda g: g["Yas"]["a"] == "fish",
               lambda g: g["Ada"]["a"] != "cat",
               lambda g: g["Yas"]["b"] != "Bo"],
              cross=[lambda g: next(v["b"] for v in g.values() if v["a"] == "dog") == "Rex"])
B.Q("logic_grid",
    "Yas, Zane and Ada each keep a different pet with a different name. The pets are a cat, "
    "a dog and a fish; the names are Mia, Bo and Rex. Yas keeps the fish and Ada does not "
    "keep the cat. The dog is called Rex. Yas's pet is not called Bo. What is the name of "
    "Zane's pet?",
    key=_G16["Zane"]["b"], verify=_G16["Zane"]["b"] if _G16["Ada"]["b"] == "Rex" else "MISMATCH",
    wrong=["Mia", "Rex", "it cannot be worked out"],
    expl="Yas keeps the fish and Ada does not keep the cat, so Ada keeps the dog and Zane "
         "the cat. The dog is Rex, so Ada's pet is Rex. Yas's is not Bo, so Yas's is Mia "
         "and Zane's is Bo.",
    difficulty="hard", confidence=0.90),

_G3 = solve(["Gus", "Hana", "Ivo", "Jem"], ["apple", "banana", "orange", "pear"],
            [lambda a: a["Gus"] == "pear",
             lambda a: a["Hana"] != "apple",
             lambda a: a["Ivo"] == "banana",
             lambda a: a["Jem"] != "orange"])
B.Q("logic_grid",
    "Gus, Hana, Ivo and Jem each packed a different piece of fruit: an apple, a banana, an "
    "orange or a pear. Gus packed the pear and Ivo the banana. Hana did not pack the "
    "apple, and Jem did not pack the orange. What did Hana pack?",
    key=f'the {_G3["Hana"]}',
    verify=f'the {({"apple", "orange"} - {_G3["Jem"]}).pop()}',
    wrong=["the apple", "the banana", "the pear"],
    expl="The pear and banana are taken, so the apple and orange go to Hana and Jem. Hana "
         "did not pack the apple, so Hana has the orange and Jem the apple.",
    difficulty="medium", confidence=0.92),

_G5 = solve(["Nia", "Omar", "Pip"], ["library", "canteen", "office"],
            [lambda a: a["Nia"] != "canteen",
             lambda a: a["Omar"] == "office",
             lambda a: a["Pip"] != "library"])
B.Q("logic_grid",
    "Nia, Omar and Pip each help in a different place at lunchtime: the library, the "
    "canteen or the office. Omar helps in the office. Nia does not help in the canteen, "
    "and Pip does not help in the library. Where does Pip help?",
    key=_G5["Pip"], verify=({"library", "canteen"} - {_G5["Nia"]}).pop(),
    wrong=["the library", "the office", "it cannot be worked out"],
    expl="Omar takes the office, leaving the library and the canteen. Pip is not in the "
         "library, so Pip is in the canteen and Nia in the library.",
    fmt=lambda v: f"the {v}" if not v.startswith(("the", "it")) else v,
    difficulty="medium", confidence=0.92),

_G7 = solve(["Uma", "Vik", "Wes"], ["cricket", "netball", "soccer"],
            [lambda a: a["Uma"] != "soccer",
             lambda a: a["Vik"] != "soccer",
             lambda a: a["Uma"] != "cricket"])
B.Q("logic_grid",
    "Uma, Vik and Wes each coach a different sport: cricket, netball or soccer. Neither "
    "Uma nor Vik coaches soccer. Uma does not coach cricket either. Which sport does Vik "
    "coach?",
    key=_G7["Vik"], verify=({"cricket", "netball"} - {_G7["Uma"]}).pop(),
    wrong=["netball", "soccer", "it cannot be worked out"],
    expl="Neither Uma nor Vik coaches soccer, so Wes does. Uma does not coach cricket "
         "either, so Uma coaches netball and Vik cricket.",
    difficulty="hard", confidence=0.91),

_G9 = solve(["Abe", "Bea", "Cy", "Dot"], ["Perth", "Cairns", "Hobart", "Adelaide"],
            [lambda a: a["Abe"] == "Cairns",
             lambda a: a["Bea"] != "Perth",
             lambda a: a["Cy"] == "Adelaide",
             lambda a: a["Dot"] != "Hobart"])
B.Q("logic_grid",
    "Abe, Bea, Cy and Dot each moved to a different city: Perth, Cairns, Hobart or "
    "Adelaide. Abe moved to Cairns and Cy to Adelaide. Bea did not move to Perth, and Dot "
    "did not move to Hobart. Which city did Bea move to?",
    key=_G9["Bea"], verify=({"Perth", "Hobart"} - {_G9["Dot"]}).pop(),
    wrong=["Perth", "Cairns", "Adelaide"],
    expl="Cairns and Adelaide are taken, so Perth and Hobart are left for Bea and Dot. Bea "
         "did not move to Perth, so Bea went to Hobart and Dot to Perth.",
    difficulty="medium", confidence=0.92),

_G11 = solve(["Hal", "Ines", "Jo"], ["poem", "story", "report"],
             [lambda a: a["Hal"] != "story",
              lambda a: a["Ines"] == "report",
              lambda a: a["Jo"] != "poem"])
B.Q("logic_grid",
    "Hal, Ines and Jo each wrote a different piece: a poem, a story or a report. Ines "
    "wrote the report. Hal did not write the story, and Jo did not write the poem. What "
    "did Hal write?",
    key=_G11["Hal"], verify=({"poem", "story"} - {_G11["Jo"]}).pop(),
    wrong=["the story", "the report", "it cannot be worked out"],
    expl="Ines wrote the report, so the poem and story are left. Hal did not write the "
         "story, so Hal wrote the poem and Jo the story.",
    fmt=lambda v: f"the {v}" if not v.startswith(("the", "it")) else v,
    difficulty="medium", confidence=0.92),

_G13 = solve(["Opal", "Pax", "Quill"], ["bus", "walk", "cycle"],
             [lambda a: a["Opal"] == "cycle",
              lambda a: a["Pax"] != "bus",
              lambda a: a["Quill"] != "walk"])
B.Q("logic_grid",
    "Opal, Pax and Quill each get to school a different way: by bus, on foot or by "
    "bicycle. Opal cycles. Pax does not take the bus, and Quill does not walk. How does "
    "Pax get to school?",
    key=_G13["Pax"], verify=({"bus", "walk"} - {_G13["Quill"]}).pop(),
    wrong=["by bus", "by bicycle", "it cannot be worked out"],
    expl="Opal cycles, so the bus and walking are left. Pax does not take the bus, so Pax "
         "walks and Quill takes the bus.",
    fmt=lambda v: {"walk": "on foot", "bus": "by bus", "cycle": "by bicycle"}.get(v, v),
    difficulty="medium", confidence=0.92),

_G15 = solve(["Uri", "Vale", "Wynn", "Xia"], ["gold", "silver", "bronze", "no medal"],
             [lambda a: a["Uri"] != "gold",
              lambda a: a["Vale"] == "bronze",
              lambda a: a["Wynn"] == "gold",
              lambda a: a["Xia"] != "silver"])
B.Q("logic_grid",
    "Uri, Vale, Wynn and Xia competed and one took gold, one silver, one bronze and one no "
    "medal. Wynn took gold and Vale bronze. Xia did not take silver. What did Uri take?",
    key=_G15["Uri"], verify=({"silver", "no medal"} - {_G15["Xia"]}).pop(),
    wrong=["gold", "bronze", "no medal"],
    expl="Gold and bronze are taken, so silver and no medal are left for Uri and Xia. Xia "
         "did not take silver, so Uri took silver and Xia went home without a medal.",
    difficulty="medium", confidence=0.92),


B.write()
