#!/usr/bin/env python3
"""Builds lr_thinking_skills_p33.json — 32 questions across four subcategories.

who reasons correctly 12, logic grid 11, optimisation 6, necessary vs sufficient 3. Four
subcategories close here: who_reasons_correctly at 70/70, logic_grid at 45/45,
optimisation at 40/40 and necessary_vs_sufficient at 45/45. Only strengthen and weaken
remain after this.

Every grid with two attributes carries a clue joining them, and solve2 proves the clue
matters by solving the puzzle without it and refusing if it still comes out unique.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.figure_lib import table  # noqa: E402
from tools.lr.lr_common import Batch  # noqa: E402
from tools.lr.lr_logic import (  # noqa: E402
    ALL, IFo, ISo, NO, NOTHING, NOTo, ORo, SOME, Scenario, best, only, solve, solve2,
    syllogism,
)

B = Batch(nn=33)
NIGHT = {"Friday": 0, "Saturday": 1, "Sunday": 2}


def says(name, claim):
    return f"{name}: '{claim}'"


def conditional(cat, stem, a, b, given, options, expl, **kw):
    S = Scenario([a, b], rules=[IFo(a, b)], given=[given])
    resolved = [(t, f(S) if callable(f) else f) for t, f in options]
    key = S.pick(resolved)
    B.Q(cat, stem, key=key, verify=key,
        wrong=[t for t, _ in resolved if t != key], expl=expl, **kw)


# ===================================================== who reasons correctly (12)

_w1 = syllogism(["shed", "tool", "sharp"], [ALL("shed", "tool"), NO("tool", "sharp")],
                [(says("Ana", "Nothing in the shed is sharp"), NO("shed", "sharp")),
                 (says("Bo", "Every tool is in the shed"), ALL("tool", "shed")),
                 (says("Cy", "Some things in the shed are sharp"), SOME("shed", "sharp")),
                 (says("Di", "Every sharp thing is a tool"), ALL("sharp", "tool"))])
B.Q("who_reasons_correctly",
    "Everything in the shed is a tool. No tool is sharp. Which student has reasoned "
    "correctly?",
    key=_w1, verify=says("Ana", "Nothing in the shed is sharp"),
    wrong=[says("Bo", "Every tool is in the shed"),
           says("Cy", "Some things in the shed are sharp"),
           says("Di", "Every sharp thing is a tool")],
    expl="The shed holds only tools and no tool is sharp, so nothing in the shed is sharp. "
         "Bo reverses the first statement: tools live in plenty of other places.",
    difficulty="medium", confidence=0.92),

_S2 = Scenario(["frozen", "burst", "leak"],
               rules=[IFo("frozen", "burst"), IFo("burst", "leak")], given=[ISo("frozen")])
_w2 = _S2.pick([(says("Eve", "There will be a leak"), _S2.here(ISo("leak"))),
                (says("Fin", "There will be no leak"), _S2.here(NOTo("leak"))),
                (says("Gia", "The pipe stays whole"), _S2.here(NOTo("burst"))),
                (says("Hal", "Leaks only ever come from frost"),
                 _S2.always(IFo("leak", "frozen")))])
B.Q("who_reasons_correctly",
    "If the pipe freezes, it bursts. If it bursts, water leaks into the cellar. Last night "
    "the pipe froze. Which student has reasoned correctly?",
    key=_w2, verify=says("Eve", "There will be a leak"),
    wrong=[says("Fin", "There will be no leak"),
           says("Gia", "The pipe stays whole"),
           says("Hal", "Leaks only ever come from frost")],
    expl="Frozen leads to burst and burst leads to a leak, so the chain runs all the way "
         "through. Hal reverses it, and a cellar can leak for a dozen other reasons.",
    difficulty="medium", confidence=0.92),

_S3 = Scenario(["north", "south"], given=[ORo("north", "south"), NOTo("south")])
_w3 = _S3.pick([(says("Ivy", "The bird flew north"), _S3.here(ISo("north"))),
                (says("Jo", "The bird flew south"), _S3.here(ISo("south"))),
                (says("Kit", "The bird did not fly"),
                 _S3.here(lambda i: lambda m: not m[f"north@{i}"] and not m[f"south@{i}"])),
                (says("Lex", "The bird flew both ways"),
                 _S3.here(lambda i: lambda m: m[f"north@{i}"] and m[f"south@{i}"]))])
B.Q("who_reasons_correctly",
    "The tagged bird flew either north or south for the winter. It did not fly south. "
    "Which student has reasoned correctly?",
    key=_w3, verify=says("Ivy", "The bird flew north"),
    wrong=[says("Jo", "The bird flew south"),
           says("Kit", "The bird did not fly"),
           says("Lex", "The bird flew both ways")],
    expl="One of the two directions was taken, and south is ruled out, so it flew north. "
         "Kit's answer contradicts the first statement rather than using it.",
    difficulty="medium", confidence=0.92),

_S4 = Scenario(["borrowed", "card"], rules=[IFo("borrowed", "card")], given=[ISo("borrowed")])
_w4 = _S4.pick([(says("Mia", "Tam holds a library card"), _S4.here(ISo("card"))),
                (says("Nils", "Tam holds no library card"), _S4.here(NOTo("card"))),
                (says("Opal", "Everyone with a card has borrowed a book"),
                 _S4.always(IFo("card", "borrowed"))),
                (says("Pax", "Tam will borrow again next week"),
                 _S4.later(ISo("borrowed")))])
B.Q("who_reasons_correctly",
    "Only people holding a library card may borrow a book. Tam borrowed a book yesterday. "
    "Which student has reasoned correctly?",
    key=_w4, verify=says("Mia", "Tam holds a library card"),
    wrong=[says("Nils", "Tam holds no library card"),
           says("Opal", "Everyone with a card has borrowed a book"),
           says("Pax", "Tam will borrow again next week")],
    expl="'Only card holders may borrow' means anyone who borrows holds a card, so Tam "
         "does. Opal reads it the other way, as though a card meant having used it.",
    difficulty="medium", confidence=0.92),

_S5 = Scenario(["holiday", "collected", "windy"],
               rules=[lambda i: lambda m: m[f"collected@{i}"] != m[f"holiday@{i}"]],
               given=[NOTo("collected")])
_w5 = _S5.pick([(says("Quinn", "Today is a public holiday"), _S5.here(ISo("holiday"))),
                (says("Rae", "Today is not a public holiday"), _S5.here(NOTo("holiday"))),
                (says("Sol", "The bins are never collected"), _S5.always(NOTo("collected"))),
                (says("Tia", "It is windy today"), _S5.here(ISo("windy")))])
B.Q("who_reasons_correctly",
    "The bins are collected every day except public holidays, when they are left. Today "
    "the bins were not collected. Which student has reasoned correctly?",
    key=_w5, verify=says("Quinn", "Today is a public holiday"),
    wrong=[says("Rae", "Today is not a public holiday"),
           says("Sol", "The bins are never collected"),
           says("Tia", "It is windy today")],
    expl="A public holiday is the only day collection stops, so uncollected bins mean it is "
         "a holiday. Tia's claim may be true but nothing in the statement is about wind.",
    difficulty="hard", confidence=0.91),

_w6 = syllogism(["ranger", "trained", "climber"],
                [ALL("ranger", "trained"), SOME("ranger", "climber")],
                [(says("Uma", "Some trained people can climb"), SOME("trained", "climber")),
                 (says("Vik", "All trained people can climb"), ALL("trained", "climber")),
                 (says("Wren", "All climbers are rangers"), ALL("climber", "ranger")),
                 (says("Xan", "No trained person can climb"), NO("trained", "climber"))])
B.Q("who_reasons_correctly",
    "Every ranger in the park has been trained. Some of the rangers can climb. Which "
    "student has reasoned correctly?",
    key=_w6, verify=says("Uma", "Some trained people can climb"),
    wrong=[says("Vik", "All trained people can climb"),
           says("Wren", "All climbers are rangers"),
           says("Xan", "No trained person can climb")],
    expl="A ranger who climbs is a trained person who climbs, so at least one trained "
         "person can. Trained people who are not rangers are not covered.",
    difficulty="hard", confidence=0.91),

_S7 = Scenario(["blocked", "overflow", "flooded"],
               rules=[IFo("blocked", "overflow"), IFo("overflow", "flooded")],
               given=[NOTo("flooded")])
_w7 = _S7.pick([(says("Yas", "The drain is not blocked"), _S7.here(NOTo("blocked"))),
                (says("Zed", "The drain is blocked"), _S7.here(ISo("blocked"))),
                (says("Abe", "The gutter is overflowing"), _S7.here(ISo("overflow"))),
                (says("Bea", "The yard never floods"), _S7.always(NOTo("flooded")))])
B.Q("who_reasons_correctly",
    "If the drain is blocked, the gutter overflows. If the gutter overflows, the yard "
    "floods. This morning the yard is not flooded. Which student has reasoned correctly?",
    key=_w7, verify=says("Yas", "The drain is not blocked"),
    wrong=[says("Zed", "The drain is blocked"),
           says("Abe", "The gutter is overflowing"),
           says("Bea", "The yard never floods")],
    expl="Working back from the end: a dry yard means the gutter is not overflowing, and "
         "that means the drain is not blocked. Abe goes forwards from a fact never given.",
    difficulty="hard", confidence=0.91),

_S8 = Scenario(["green", "gate"], rules=[IFo("green", "gate")], given=[ISo("green")])
_w8 = _S8.pick([(says("Cleo", "The gate is unlocked"), _S8.here(ISo("gate"))),
                (says("Dev", "The gate is locked"), _S8.here(NOTo("gate"))),
                (says("Eli", "The gate is unlocked only when the light is green"),
                 _S8.always(IFo("gate", "green"))),
                (says("Fay", "The light will be green tomorrow"), _S8.later(ISo("green")))])
B.Q("who_reasons_correctly",
    "Whenever the light on the post is green, the gate is unlocked. This morning the light "
    "is green. Which student has reasoned correctly?",
    key=_w8, verify=says("Cleo", "The gate is unlocked"),
    wrong=[says("Dev", "The gate is locked"),
           says("Eli", "The gate is unlocked only when the light is green"),
           says("Fay", "The light will be green tomorrow")],
    expl="A green light guarantees an unlocked gate, and the light is green. Eli makes the "
         "light the only way the gate is ever unlocked, which is a stronger claim.",
    difficulty="medium", confidence=0.92),

_w9 = syllogism(["entry", "photo", "late"],
                [ALL("entry", "photo"), NO("late", "photo")],
                [(says("Gus", "No late piece is an entry"), NO("late", "entry")),
                 (says("Hana", "Every photo is an entry"), ALL("photo", "entry")),
                 (says("Ivo", "Some late pieces are entries"), SOME("late", "entry")),
                 (says("Jem", "Every entry was late"), ALL("entry", "late"))])
B.Q("who_reasons_correctly",
    "Every entry in the competition is a photograph. None of the late pieces is a "
    "photograph. Which student has reasoned correctly?",
    key=_w9, verify=says("Gus", "No late piece is an entry"),
    wrong=[says("Hana", "Every photo is an entry"),
           says("Ivo", "Some late pieces are entries"),
           says("Jem", "Every entry was late")],
    expl="Entries are all photographs and no late piece is one, so no late piece is an "
         "entry. Hana reverses the first statement, which would make every photograph "
         "anywhere an entry.",
    difficulty="medium", confidence=0.92),

_S10 = Scenario(["signal", "siding"], rules=[IFo("signal", "siding")],
                given=[NOTo("siding")])
_w10 = _S10.pick([(says("Kai", "The signal was not against the train"),
                   _S10.here(NOTo("signal"))),
                  (says("Lena", "The signal was against the train"),
                   _S10.here(ISo("signal"))),
                  (says("Mo", "A train in the siding always has the signal against it"),
                   _S10.always(IFo("siding", "signal"))),
                  (says("Nia", "The train will be held tomorrow"),
                   _S10.later(ISo("siding")))])
B.Q("who_reasons_correctly",
    "Whenever the signal is against a goods train, the train is held in the siding. This "
    "morning the goods train was not held in the siding. Which student has reasoned "
    "correctly?",
    key=_w10, verify=says("Kai", "The signal was not against the train"),
    wrong=[says("Lena", "The signal was against the train"),
           says("Mo", "A train in the siding always has the signal against it"),
           says("Nia", "The train will be held tomorrow")],
    expl="A signal against the train guarantees it is held, and it was not held, so the "
         "signal was not against it. Mo reverses the rule — a train can wait in the siding "
         "to let an express past.",
    difficulty="hard", confidence=0.91),

_w11 = syllogism(["signed", "member", "rosa"],
                 [ALL("signed", "member"), NO("rosa", "member")],
                 [(says("Omar", "Rosa did not sign"), NO("rosa", "signed")),
                  (says("Pia", "Rosa signed"), ALL("rosa", "signed")),
                  (says("Quill", "Every member signed"), ALL("member", "signed")),
                  (says("Rae", "No member signed"), NO("member", "signed"))])
B.Q("who_reasons_correctly",
    "Everyone who signed the petition is a member of the club. Rosa is not a member. Which "
    "student has reasoned correctly?",
    key=_w11, verify=says("Omar", "Rosa did not sign"),
    wrong=[says("Pia", "Rosa signed"),
           says("Quill", "Every member signed"),
           says("Rae", "No member signed")],
    expl="Signing means being a member, and Rosa is not one, so Rosa did not sign. Quill "
         "reverses it: plenty of members may not have signed at all.",
    difficulty="medium", confidence=0.92),

_S12 = Scenario(["late", "queue", "missed"],
                rules=[IFo("late", "queue"), IFo("queue", "missed")],
                given=[NOTo("missed")])
_w12 = _S12.pick([(says("Sol", "The delivery was not late"), _S12.here(NOTo("late"))),
                  (says("Tam", "The delivery was late"), _S12.here(ISo("late"))),
                  (says("Uri", "There was a queue at the depot"), _S12.here(ISo("queue"))),
                  (says("Vale", "Deliveries only ever miss the ferry when late"),
                   _S12.always(IFo("missed", "late")))])
B.Q("who_reasons_correctly",
    "If the delivery is late, it queues at the depot. If it queues at the depot, it misses "
    "the ferry. Today's delivery did not miss the ferry. Which student has reasoned "
    "correctly?",
    key=_w12, verify=says("Sol", "The delivery was not late"),
    wrong=[says("Tam", "The delivery was late"),
           says("Uri", "There was a queue at the depot"),
           says("Vale", "Deliveries only ever miss the ferry when late")],
    expl="Catching the ferry means there was no queue, and no queue means the delivery was "
         "not late. Vale reverses the chain: a breakdown would miss the ferry too.",
    difficulty="hard", confidence=0.91),

# ===================================================== logic grid (11)

_G1 = solve2(["Ada", "Bram", "Cleo"], ["poem", "song", "play"], ["Friday", "Saturday",
                                                                 "Sunday"],
             [lambda g: g["Ada"]["a"] == "poem",
              lambda g: g["Bram"]["a"] != "song",
              lambda g: NIGHT[g["Ada"]["b"]] < NIGHT[g["Cleo"]["b"]]],
             cross=[lambda g: next(v["b"] for v in g.values()
                                   if v["a"] == "play") == "Sunday"])
B.Q("logic_grid",
    "Ada, Bram and Cleo each perform a different piece on a different night. The pieces are "
    "a poem, a song and a play; the nights are Friday, Saturday and Sunday. Ada performs "
    "the poem. Bram does not perform the song. The play is on Sunday. Ada performs on an "
    "earlier night than Cleo. On which night does Cleo perform?",
    key=_G1["Cleo"]["b"], verify=({"Friday", "Saturday"} - {_G1["Ada"]["b"]}).pop(),
    wrong=["Friday", "Sunday", "it cannot be worked out"],
    expl="Ada has the poem and Bram does not have the song, so Bram has the play and Cleo "
         "the song. The play is on Sunday, so Bram performs then, leaving Friday and "
         "Saturday. Ada is earlier than Cleo, so Ada is on Friday and Cleo on Saturday.",
    fig=table([["", "poem", "song", "play", "Fri", "Sat", "Sun"],
               ["Ada", "", "", "", "", "", ""], ["Bram", "", "", "", "", "", ""],
               ["Cleo", "", "", "", "", "", ""]]),
    difficulty="hard", confidence=0.90),

_G2 = solve(["Dov", "Elsa", "Fai"], ["chemistry", "biology", "physics"],
            [lambda a: a["Dov"] != "biology",
             lambda a: a["Elsa"] == "physics",
             lambda a: a["Fai"] != "chemistry"])
B.Q("logic_grid",
    "Dov, Elsa and Fai each teach a different subject: chemistry, biology or physics. Elsa "
    "teaches physics. Dov does not teach biology, and Fai does not teach chemistry. Which "
    "subject does Dov teach?",
    key=_G2["Dov"], verify=({"chemistry", "biology"} - {_G2["Fai"]}).pop(),
    wrong=["biology", "physics", "it cannot be worked out"],
    expl="Elsa teaches physics, so chemistry and biology are left. Dov does not teach "
         "biology, so Dov teaches chemistry and Fai biology.",
    difficulty="medium", confidence=0.92),

_G3 = solve2(["Gil", "Hana", "Ivo"], ["blue", "red", "white"], ["8", "10", "12"],
             [lambda g: g["Gil"]["a"] == "red",
              lambda g: g["Gil"]["b"] != "8",
              lambda g: g["Hana"]["a"] != "white"],
             cross=[lambda g: next(v["b"] for v in g.values() if v["a"] == "white") == "12"])
B.Q("logic_grid",
    "Gil, Hana and Ivo each own a different coloured kayak of a different length. The "
    "colours are blue, red and white; the lengths are 8, 10 and 12 feet. Gil's kayak is "
    "red. Hana's is not white. The white kayak is 12 feet long. Gil's is not 8 feet. How "
    "long is Hana's kayak?",
    key=f'{_G3["Hana"]["b"]} feet',
    verify=f'{({"8", "10"} - {_G3["Gil"]["b"]}).pop()} feet',
    wrong=["10 feet", "12 feet", "it cannot be worked out"],
    expl="Gil's is red and Hana's is not white, so Hana's is blue and Ivo's white. The "
         "white one is 12 feet, so Ivo's is 12, leaving 8 and 10 for Gil and Hana. Gil's is "
         "not 8, so Gil's is 10 and Hana's is 8.",
    difficulty="hard", confidence=0.90),

_G4 = solve(["Jai", "Kez", "Lou", "Mia"], ["1st", "2nd", "3rd", "4th"],
            [lambda a: a["Jai"] == "3rd",
             lambda a: a["Kez"] != "1st",
             lambda a: a["Lou"] == "4th",
             lambda a: a["Mia"] != "2nd"])
B.Q("logic_grid",
    "Jai, Kez, Lou and Mia finished a quiz in the first four places. Jai came third and Lou "
    "came fourth. Kez did not come first, and Mia did not come second. Who came first?",
    key="Mia", verify=next(n for n, p in _G4.items() if p == "1st"),
    wrong=["Jai", "Kez", "Lou"],
    expl="Third and fourth are taken, so first and second belong to Kez and Mia. Kez did "
         "not come first, so Kez came second and Mia first — which also fits Mia not being "
         "second.",
    difficulty="medium", confidence=0.92),

_G5 = solve2(["Nia", "Oz", "Pia"], ["cello", "harp", "oboe"], ["Mon", "Wed", "Fri"],
             [lambda g: g["Nia"]["a"] == "harp",
              lambda g: g["Nia"]["b"] != "Fri",
              lambda g: g["Oz"]["a"] != "oboe"],
             cross=[lambda g: next(v["b"] for v in g.values() if v["a"] == "oboe") == "Mon"])
B.Q("logic_grid",
    "Nia, Oz and Pia each play a different instrument and practise on a different day. The "
    "instruments are cello, harp and oboe; the days are Monday, Wednesday and Friday. Nia "
    "plays the harp and does not practise on Friday. Oz does not play the oboe. The oboe "
    "is practised on Monday. On which day does Oz practise?",
    key={"Mon": "Monday", "Wed": "Wednesday", "Fri": "Friday"}[_G5["Oz"]["b"]],
    verify={"Mon": "Monday", "Wed": "Wednesday", "Fri": "Friday"}[
        ({"Mon", "Wed", "Fri"} - {_G5["Nia"]["b"], _G5["Pia"]["b"]}).pop()],
    wrong=["Monday", "Wednesday", "it cannot be worked out"],
    expl="Nia has the harp and Oz does not have the oboe, so Oz has the cello and Pia the "
         "oboe. The oboe is on Monday, so Pia takes Monday. Nia is not on Friday, so Nia "
         "is on Wednesday and Oz on Friday.",
    difficulty="hard", confidence=0.90),

_G6 = solve(["Quinn", "Rio", "Sam"], ["tent", "cabin", "van"],
            [lambda a: a["Quinn"] != "van",
             lambda a: a["Rio"] != "van",
             lambda a: a["Quinn"] != "cabin"])
B.Q("logic_grid",
    "Quinn, Rio and Sam each stay in different accommodation: a tent, a cabin or a van. "
    "Neither Quinn nor Rio stays in the van. Quinn does not stay in the cabin either. Where "
    "does Rio stay?",
    key=_G6["Rio"], verify=({"tent", "cabin"} - {_G6["Quinn"]}).pop(),
    wrong=["the tent", "the van", "it cannot be worked out"],
    expl="Neither Quinn nor Rio takes the van, so Sam does. Quinn does not take the cabin "
         "either, so Quinn has the tent and Rio the cabin.",
    fmt=lambda v: f"the {v}" if not v.startswith(("the", "it")) else v,
    difficulty="hard", confidence=0.91),

_G7 = solve(["Tao", "Uma", "Vik", "Wren"], ["Japan", "Chile", "Kenya", "Norway"],
            [lambda a: a["Tao"] == "Kenya",
             lambda a: a["Uma"] != "Japan",
             lambda a: a["Vik"] == "Norway",
             lambda a: a["Wren"] != "Chile"])
B.Q("logic_grid",
    "Tao, Uma, Vik and Wren each visited a different country: Japan, Chile, Kenya or "
    "Norway. Tao went to Kenya and Vik to Norway. Uma did not go to Japan, and Wren did "
    "not go to Chile. Which country did Uma visit?",
    key=_G7["Uma"], verify=({"Japan", "Chile"} - {_G7["Wren"]}).pop(),
    wrong=["Japan", "Kenya", "Norway"],
    expl="Kenya and Norway are taken, so Japan and Chile are left for Uma and Wren. Uma did "
         "not go to Japan, so Uma went to Chile and Wren to Japan.",
    difficulty="medium", confidence=0.92),

_G8 = solve2(["Xan", "Yara", "Zed"], ["maths", "art", "music"], ["9", "10", "11"],
             [lambda g: g["Xan"]["a"] == "art",
              lambda g: g["Yara"]["b"] != "11",
              lambda g: g["Yara"]["a"] != "music"],
             cross=[lambda g: next(v["b"] for v in g.values() if v["a"] == "music") == "9"])
B.Q("logic_grid",
    "Xan, Yara and Zed each study a different subject and are in different year levels. The "
    "subjects are maths, art and music; the years are 9, 10 and 11. Xan studies art. Yara "
    "does not study music and is not in Year 11. The music student is in Year 9. Which "
    "year is Xan in?",
    key=f'Year {_G8["Xan"]["b"]}',
    verify=f'Year {({"9", "10", "11"} - {_G8["Yara"]["b"], _G8["Zed"]["b"]}).pop()}',
    wrong=["Year 9", "Year 10", "it cannot be worked out"],
    expl="Xan has art and Yara does not have music, so Yara has maths and Zed music. The "
         "music student is in Year 9, so Zed is. Yara is not in Year 11, so Yara is in "
         "Year 10 and Xan in Year 11.",
    difficulty="hard", confidence=0.90),

_G9 = solve(["Ada", "Ben", "Cy"], ["email", "phone", "letter"],
            [lambda a: a["Ada"] != "letter",
             lambda a: a["Ben"] == "phone",
             lambda a: a["Cy"] != "email"])
B.Q("logic_grid",
    "Ada, Ben and Cy each got in touch a different way: by email, by phone or by letter. "
    "Ben phoned. Ada did not write a letter, and Cy did not send an email. How did Cy get "
    "in touch?",
    key=_G9["Cy"], verify=({"email", "letter"} - {_G9["Ada"]}).pop(),
    wrong=["by email", "by phone", "it cannot be worked out"],
    expl="Ben phoned, so the email and the letter are left. Cy did not email, so Cy wrote a "
         "letter and Ada sent the email.",
    fmt=lambda v: {"email": "by email", "phone": "by phone", "letter": "by letter"}.get(v, v),
    difficulty="medium", confidence=0.92),

_G10 = solve2(["Dee", "Eli", "Fen", "Gus"], ["oak", "elm", "fig", "pine"],
              ["north", "south", "east", "west"],
              [lambda g: g["Dee"]["a"] == "oak",
               lambda g: g["Fen"]["b"] == "east",
               lambda g: g["Fen"]["a"] == "pine",
               lambda g: g["Gus"]["b"] != "north",
               lambda g: g["Dee"]["b"] == "west"],
              cross=[lambda g: next(v["b"] for v in g.values() if v["a"] == "fig") == "north"])
B.Q("logic_grid",
    "Dee, Eli, Fen and Gus each planted a different tree in a different corner of the park. "
    "The trees are an oak, an elm, a fig and a pine; the corners are north, south, east and "
    "west. Dee planted the oak in the west corner. Fen planted the pine in the east. The "
    "fig stands in the north corner. Gus did not plant in the north. Which tree did Gus "
    "plant?",
    key=f'the {_G10["Gus"]["a"]}',
    verify=f'the {({"elm", "fig"} - {_G10["Eli"]["a"]}).pop()}',
    wrong=["the oak", "the fig", "the pine"],
    expl="Dee has the oak and Fen the pine, so the elm and the fig go to Eli and Gus. The "
         "fig stands in the north and Gus did not plant there, so Gus has the elm and Eli "
         "the fig in the north corner, leaving the south for Gus.",
    fig=table([["", "oak", "elm", "fig", "pine", "N", "S", "E", "W"],
               ["Dee", "", "", "", "", "", "", "", ""],
               ["Eli", "", "", "", "", "", "", "", ""],
               ["Fen", "", "", "", "", "", "", "", ""],
               ["Gus", "", "", "", "", "", "", "", ""]], vw=470),
    difficulty="hard", confidence=0.90),

_G11 = solve(["Hana", "Ivo", "Jem"], ["gold", "silver", "bronze"],
             [lambda a: a["Hana"] != "gold",
              lambda a: a["Ivo"] != "gold",
              lambda a: a["Hana"] != "bronze"])
B.Q("logic_grid",
    "Hana, Ivo and Jem took gold, silver and bronze in some order. Neither Hana nor Ivo "
    "took gold. Hana did not take bronze either. Which medal did Ivo take?",
    key=_G11["Ivo"], verify=({"silver", "bronze"} - {_G11["Hana"]}).pop(),
    wrong=["gold", "silver", "it cannot be worked out"],
    expl="Neither Hana nor Ivo took gold, so Jem did. Hana did not take bronze either, so "
         "Hana took silver and Ivo bronze.",
    difficulty="hard", confidence=0.91),

# ===================================================== optimisation (6)

_o1 = only(range(1, 40), lambda n: 9 * n >= 200 and 9 * (n - 1) < 200)
B.Q("optimisation",
    "A shelf holds 9 tins. A shop needs to store 200 tins. What is the smallest number of "
    "shelves needed?",
    key=_o1, verify=-(-200 // 9),
    wrong=[22, 200, 24],
    expl="Twenty-two shelves hold 198 tins, leaving 2 over, so a twenty-third is needed. "
         "Answering 22 leaves two tins on the floor.",
    fmt=lambda v: f"{v} shelves", difficulty="medium", confidence=0.92),

_HIRE = {"the day rate": 45, "the hourly rate": 4 * 14, "the weekly rate": 210}
_o2, _ = best(list(_HIRE), lambda k: _HIRE[k])
B.Q("optimisation",
    "A trailer can be hired at $14 an hour, $45 for a whole day, or $210 for a week. "
    "Someone needs it for four hours on one day. Which way of paying costs least?",
    key=_o2, verify=min(_HIRE, key=_HIRE.get),
    wrong=[k for k in _HIRE if k != _o2] + ["they all cost the same"],
    expl="Four hours at $14 an hour is $56, the day rate is $45, and the week costs $210 "
         "however little of it is used. The day rate is cheapest, and it stays cheapest "
         "from about three and a quarter hours onwards.",
    difficulty="hard", confidence=0.90),

_o3 = only(range(1, 40), lambda c: c * 5 == 45 - 5)
B.Q("optimisation",
    "A ribbon 45 cm long is cut into pieces 5 cm long. Each cut takes 4 seconds. How long "
    "does the cutting take altogether?",
    key=_o3 * 4, verify=(45 // 5 - 1) * 4,
    wrong=[36, 45, 40],
    expl="Nine pieces need only eight cuts, since the last piece falls free on the eighth. "
         "Eight cuts at 4 seconds each is 32 seconds. Answering 36 counts nine cuts.",
    fmt=lambda v: f"{v} seconds", difficulty="hard", confidence=0.90),

_BULK = {"six single tickets": 6 * 9, "a book of five plus one single": 40 + 9,
         "two books of five": 2 * 40}
_o4, _ = best(list(_BULK), lambda k: _BULK[k])
B.Q("optimisation",
    "Cinema tickets cost $9 each, or $40 for a book of five. Six tickets are needed. Which "
    "purchase costs least?",
    key=_o4, verify=min(_BULK, key=_BULK.get),
    wrong=[k for k in _BULK if k != _o4] + ["they all cost the same"],
    expl="Six singles come to $54. A book of five plus one single is $49. Two books cost "
         "$80 and give four tickets nobody needs. The book plus a single is cheapest.",
    difficulty="hard", confidence=0.90),

_PLANKS = [(a, b) for a in range(0, 12) for b in range(0, 18)
           if 9 * a + 5 * b == 61]
_o5 = min(a + b for a, b in _PLANKS)
B.Q("optimisation",
    "Timber is sold in lengths of 9 metres and 5 metres. A builder needs exactly 61 metres "
    "with nothing wasted. What is the smallest number of lengths that will do it?",
    key=_o5, verify=next(n for n in range(1, 18) if any(a + b == n for a, b in _PLANKS)),
    wrong=[7, 11, 8],
    expl="Four nines and five fives give 36 + 25 = 61 metres in 9 lengths. Nothing shorter "
         "works: with fewer than 9 lengths the combinations either fall short of 61 or "
         "overshoot it.",
    fmt=lambda v: f"{v} lengths", difficulty="hard", confidence=0.90),

_o6 = only(range(1, 60), lambda n: 6 * n >= 140 and 6 * (n - 1) < 140)
B.Q("optimisation",
    "A cable car carries 6 people each trip. One hundred and forty people are waiting at "
    "the bottom. How many trips are needed to take them all up?",
    key=_o6, verify=-(-140 // 6),
    wrong=[23, 140, 25],
    expl="Twenty-three trips carry 138 people, leaving 2 behind, so a twenty-fourth is "
         "needed. Answering 23 leaves the last pair at the bottom.",
    fmt=lambda v: f"{v} trips", difficulty="medium", confidence=0.92),

# ===================================================== necessary vs sufficient (3)

conditional("necessary_vs_sufficient",
            "Nobody may sit the examination without a candidate number. Kira has a "
            "candidate number. Which one of these must be true?",
            "sat", "number", ISo("number"),
            [("Everyone who sat the examination has a candidate number",
              lambda S: S.always(IFo("sat", "number"))),
             ("Kira sat the examination", lambda S: S.here(ISo("sat"))),
             ("Kira did not sit the examination", lambda S: S.here(NOTo("sat"))),
             ("Everyone with a candidate number sat the examination",
              lambda S: S.always(IFo("number", "sat")))],
            "The rule requires a number of everyone who sits, so all of them have one. It "
            "does not run backwards: Kira may have been ill on the day.",
            difficulty="hard", confidence=0.90)

conditional("necessary_vs_sufficient",
            "A grass fire will not start unless the ground is dry. The ground here has been "
            "sodden for a fortnight. Which one of these must be true?",
            "fire", "dry", NOTo("dry"),
            [("No grass fire has started here", lambda S: S.here(NOTo("fire"))),
             ("A grass fire has started here", lambda S: S.here(ISo("fire"))),
             ("Dry ground always brings a grass fire",
              lambda S: S.always(IFo("dry", "fire"))),
             ("Nothing follows about whether a fire has started", NOTHING)],
            "Dry ground is required before a grass fire can start, and the ground is "
            "sodden, so none has. Dry ground would not have started one on its own either "
            "— something has to light it.",
            difficulty="medium", confidence=0.92)

conditional("necessary_vs_sufficient",
            "Scoring three goals is enough on its own to win the match. Rafi's team scored "
            "one goal. Which one of these must be true?",
            "three", "won", NOTo("three"),
            [("Nothing follows about whether the team won", NOTHING),
             ("The team won the match", lambda S: S.here(ISo("won"))),
             ("The team did not win the match", lambda S: S.here(NOTo("won"))),
             ("Only teams scoring three goals win",
              lambda S: S.always(IFo("won", "three")))],
            "Three goals would have guaranteed a win, but the rule does not say that is the "
            "only way to win. One goal against none still wins a match.",
            difficulty="hard", confidence=0.90)

B.write()
