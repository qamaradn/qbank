#!/usr/bin/env python3
"""Builds lr_thinking_skills_p26.json — 32 §5.2 questions.

who reasons correctly 16, necessary vs sufficient 16. §5.2 reaches 263/396; Thinking
Skills 711/880.

Both categories are model-checked by lr_logic, so every option is tested against every
world in which the premises hold and the build refuses unless exactly one survives. The
necessary/sufficient items are built through a single helper rather than written out one
at a time: they are all the same two rules with the fact placed differently, and writing
that shape sixteen times by hand invites a slip in the one place a slip is invisible —
which side of the arrow the given fact sits on.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.lr.lr_common import Batch  # noqa: E402
from tools.lr.lr_logic import (  # noqa: E402
    ALL, IFo, ISo, NO, NOTHING, NOTo, ORo, SOME, Scenario, syllogism,
)

B = Batch(nn=26)


def says(name, claim):
    return f"{name}: '{claim}'"


def conditional(cat, stem, a, b, given, options, expl, **kw):
    """One if-then rule, one given fact, four options resolved against the model.

    `a -> b` is the rule. Options are (text, callable taking the Scenario), so an option
    is written as the claim it makes rather than as an answer someone decided on.
    """
    S = Scenario([a, b], rules=[IFo(a, b)], given=[given])
    resolved = [(t, f(S) if callable(f) else f) for t, f in options]
    key = S.pick(resolved)
    B.Q(cat, stem, key=key, verify=key,
        wrong=[t for t, _ in resolved if t != key], expl=expl, **kw)


# ===================================================== who reasons correctly (16)

_w1 = syllogism(["bed", "native", "rose"], [ALL("bed", "native"), NO("rose", "native")],
                [(says("Ana", "The rose is not in that bed"), NO("rose", "bed")),
                 (says("Bo", "The rose is in that bed"), ALL("rose", "bed")),
                 (says("Cy", "Every native plant is in that bed"), ALL("native", "bed")),
                 (says("Di", "No native plant is in that bed"), NO("native", "bed"))])
B.Q("who_reasons_correctly",
    "Every plant in the front bed is a native. The rose is not a native. Which student has "
    "reasoned correctly?",
    key=_w1, verify=says("Ana", "The rose is not in that bed"),
    wrong=[says("Bo", "The rose is in that bed"),
           says("Cy", "Every native plant is in that bed"),
           says("Di", "No native plant is in that bed")],
    expl="Anything in that bed is a native, and the rose is not one, so the rose is not "
         "there. Cy reads the rule backwards: natives grow in gardens all over town.",
    difficulty="medium", confidence=0.92),

_S2 = Scenario(["unbuckled", "alarm", "engine"],
               rules=[IFo("unbuckled", "alarm"), IFo("alarm", "engine")],
               given=[ISo("unbuckled")])
_w2 = _S2.pick([(says("Eve", "The engine warning comes on"), _S2.here(ISo("engine"))),
                (says("Fin", "The engine warning stays off"), _S2.here(NOTo("engine"))),
                (says("Gia", "The seatbelt alarm stays quiet"), _S2.here(NOTo("alarm"))),
                (says("Hal", "The warning only ever comes on for a seatbelt"),
                 _S2.always(IFo("engine", "unbuckled")))])
B.Q("who_reasons_correctly",
    "If a seatbelt is unbuckled, the alarm sounds. If the alarm sounds, the engine warning "
    "comes on. A seatbelt is unbuckled. Which student has reasoned correctly?",
    key=_w2, verify=says("Eve", "The engine warning comes on"),
    wrong=[says("Fin", "The engine warning stays off"),
           says("Gia", "The seatbelt alarm stays quiet"),
           says("Hal", "The warning only ever comes on for a seatbelt")],
    expl="The two rules chain together, so an unbuckled belt leads to the alarm and the "
         "alarm to the warning. Hal reverses the chain — the warning could come on for a "
         "dozen other faults.",
    difficulty="medium", confidence=0.92),

_S3 = Scenario(["air", "sea"], given=[ORo("air", "sea"), NOTo("air")])
_w3 = _S3.pick([(says("Ivy", "The parcel went by sea"), _S3.here(ISo("sea"))),
                (says("Jo", "The parcel went by air"), _S3.here(ISo("air"))),
                (says("Kit", "The parcel went neither way"),
                 _S3.here(lambda i: lambda m: not m[f"air@{i}"] and not m[f"sea@{i}"])),
                (says("Lex", "The parcel went both ways"),
                 _S3.here(lambda i: lambda m: m[f"air@{i}"] and m[f"sea@{i}"]))])
B.Q("who_reasons_correctly",
    "The parcel went either by air or by sea. It did not go by air. Which student has "
    "reasoned correctly?",
    key=_w3, verify=says("Ivy", "The parcel went by sea"),
    wrong=[says("Jo", "The parcel went by air"),
           says("Kit", "The parcel went neither way"),
           says("Lex", "The parcel went both ways")],
    expl="One of the two routes was used, and air is ruled out, so it went by sea. Kit's "
         "answer contradicts the first statement rather than using it.",
    difficulty="medium", confidence=0.92),

_S4 = Scenario(["entered", "pass"], rules=[IFo("entered", "pass")], given=[ISo("entered")])
_w4 = _S4.pick([(says("Mia", "Kim holds a laboratory pass"), _S4.here(ISo("pass"))),
                (says("Nils", "Kim holds no laboratory pass"), _S4.here(NOTo("pass"))),
                (says("Opal", "Everyone with a pass has been into the laboratory"),
                 _S4.always(IFo("pass", "entered"))),
                (says("Pax", "Kim will go in again tomorrow"), _S4.later(ISo("entered")))])
B.Q("who_reasons_correctly",
    "Only students holding a laboratory pass may go into the laboratory. Kim went in this "
    "morning. Which student has reasoned correctly?",
    key=_w4, verify=says("Mia", "Kim holds a laboratory pass"),
    wrong=[says("Nils", "Kim holds no laboratory pass"),
           says("Opal", "Everyone with a pass has been into the laboratory"),
           says("Pax", "Kim will go in again tomorrow")],
    expl="'Only pass holders may go in' means anyone who went in holds a pass, so Kim does. "
         "Opal turns it round, as though holding a pass meant having used it.",
    difficulty="medium", confidence=0.92),

_S5 = Scenario(["friday", "locked", "raining"],
               rules=[lambda i: lambda m: m[f"locked@{i}"] != m[f"friday@{i}"]],
               given=[NOTo("locked")])
_w5 = _S5.pick([(says("Quinn", "Tonight is Friday"), _S5.here(ISo("friday"))),
                (says("Rae", "Tonight is not Friday"), _S5.here(NOTo("friday"))),
                (says("Sol", "The gate is never locked"), _S5.always(NOTo("locked"))),
                (says("Tia", "It is raining tonight"), _S5.here(ISo("raining")))])
B.Q("who_reasons_correctly",
    "The gate is locked every night except Friday, when it is left open. Tonight the gate "
    "is not locked. Which student has reasoned correctly?",
    key=_w5, verify=says("Quinn", "Tonight is Friday"),
    wrong=[says("Rae", "Tonight is not Friday"),
           says("Sol", "The gate is never locked"),
           says("Tia", "It is raining tonight")],
    expl="Friday is the only night the gate stays open, so an open gate means it is Friday. "
         "Tia's claim may be true but nothing in the statement is about the weather.",
    difficulty="hard", confidence=0.91),

_w6 = syllogism(["tankfish", "goldfish", "shark"],
                [ALL("tankfish", "goldfish"), NO("goldfish", "shark")],
                [(says("Uma", "No fish in the tank is a shark"), NO("tankfish", "shark")),
                 (says("Vik", "Every goldfish is in the tank"), ALL("goldfish", "tankfish")),
                 (says("Wren", "Some fish in the tank are sharks"), SOME("tankfish", "shark")),
                 (says("Xan", "Every shark is a goldfish"), ALL("shark", "goldfish"))])
B.Q("who_reasons_correctly",
    "Every fish in the tank is a goldfish. No goldfish is a shark. Which student has "
    "reasoned correctly?",
    key=_w6, verify=says("Uma", "No fish in the tank is a shark"),
    wrong=[says("Vik", "Every goldfish is in the tank"),
           says("Wren", "Some fish in the tank are sharks"),
           says("Xan", "Every shark is a goldfish")],
    expl="The tank holds only goldfish, and no goldfish is a shark, so the tank holds no "
         "shark. Vik reverses the first statement: goldfish live in plenty of other tanks.",
    difficulty="medium", confidence=0.92),

_S7 = Scenario(["drip", "meter", "bill"],
               rules=[IFo("drip", "meter"), IFo("meter", "bill")], given=[NOTo("bill")])
_w7 = _S7.pick([(says("Yas", "The tap is not dripping"), _S7.here(NOTo("drip"))),
                (says("Zed", "The tap is dripping"), _S7.here(ISo("drip"))),
                (says("Abe", "The meter is turning"), _S7.here(ISo("meter"))),
                (says("Bea", "The bill never rises"), _S7.always(NOTo("bill")))])
B.Q("who_reasons_correctly",
    "If the tap drips, the meter turns. If the meter turns, the bill rises. This quarter "
    "the bill did not rise. Which student has reasoned correctly?",
    key=_w7, verify=says("Yas", "The tap is not dripping"),
    wrong=[says("Zed", "The tap is dripping"),
           says("Abe", "The meter is turning"),
           says("Bea", "The bill never rises")],
    expl="Working back from the end: a steady bill means the meter is not turning, and a "
         "still meter means the tap is not dripping. Abe goes forwards from a fact that was "
         "never given.",
    difficulty="hard", confidence=0.91),

_S8 = Scenario(["flag", "open"], rules=[IFo("flag", "open")], given=[ISo("flag")])
_w8 = _S8.pick([(says("Cleo", "The pool is open"), _S8.here(ISo("open"))),
                (says("Dev", "The pool is closed"), _S8.here(NOTo("open"))),
                (says("Eli", "The pool opens only when the flag is up"),
                 _S8.always(IFo("open", "flag"))),
                (says("Fay", "The flag will be up tomorrow"), _S8.later(ISo("flag")))])
B.Q("who_reasons_correctly",
    "Whenever the flag is up, the pool is open. This morning the flag is up. Which student "
    "has reasoned correctly?",
    key=_w8, verify=says("Cleo", "The pool is open"),
    wrong=[says("Dev", "The pool is closed"),
           says("Eli", "The pool opens only when the flag is up"),
           says("Fay", "The flag will be up tomorrow")],
    expl="A raised flag guarantees an open pool, and the flag is up. Eli makes the flag the "
         "only way the pool ever opens, which is a stronger claim than the rule makes.",
    difficulty="medium", confidence=0.92),

_w9 = syllogism(["tool", "rusty", "replaced"],
                [SOME("tool", "rusty"), ALL("rusty", "replaced")],
                [(says("Gus", "Some tools will be replaced"), SOME("tool", "replaced")),
                 (says("Hana", "All tools will be replaced"), ALL("tool", "replaced")),
                 (says("Ivo", "Everything replaced is a tool"), ALL("replaced", "tool")),
                 (says("Jem", "No tool will be replaced"), NO("tool", "replaced"))])
B.Q("who_reasons_correctly",
    "Some of the tools in the shed are rusty. Every rusty tool is being replaced. Which "
    "student has reasoned correctly?",
    key=_w9, verify=says("Gus", "Some tools will be replaced"),
    wrong=[says("Hana", "All tools will be replaced"),
           says("Ivo", "Everything replaced is a tool"),
           says("Jem", "No tool will be replaced")],
    expl="At least one tool is rusty and every rusty one goes, so at least one tool goes. "
         "The tools that are not rusty are not covered, so nothing follows about all of "
         "them.",
    difficulty="hard", confidence=0.91),

_w10 = syllogism(["reptile", "warm", "quokka"],
                 [NO("reptile", "warm"), ALL("quokka", "warm")],
                 [(says("Kai", "No quokka is a reptile"), NO("quokka", "reptile")),
                  (says("Lena", "Every warm-blooded animal is a quokka"),
                   ALL("warm", "quokka")),
                  (says("Mo", "Some quokkas are reptiles"), SOME("quokka", "reptile")),
                  (says("Nia", "Every reptile is warm-blooded"), ALL("reptile", "warm"))])
B.Q("who_reasons_correctly",
    "No reptile is warm-blooded. All quokkas are warm-blooded. Which student has reasoned "
    "correctly?",
    key=_w10, verify=says("Kai", "No quokka is a reptile"),
    wrong=[says("Lena", "Every warm-blooded animal is a quokka"),
           says("Mo", "Some quokkas are reptiles"),
           says("Nia", "Every reptile is warm-blooded")],
    expl="Quokkas are all warm-blooded and nothing warm-blooded is a reptile, so no quokka "
         "is one. Lena reverses the second statement, which would make every possum a "
         "quokka.",
    difficulty="medium", confidence=0.92),

_S11 = Scenario(["sounded", "door"], rules=[IFo("sounded", "door")], given=[ISo("sounded")])
_w11 = _S11.pick([(says("Omar", "A door was opened"), _S11.here(ISo("door"))),
                  (says("Pia", "No door was opened"), _S11.here(NOTo("door"))),
                  (says("Quill", "Opening a door always sets the alarm off"),
                   _S11.always(IFo("door", "sounded"))),
                  (says("Rae", "The alarm will sound again tonight"),
                   _S11.later(ISo("sounded")))])
B.Q("who_reasons_correctly",
    "The alarm sounds only if a door has been opened. Last night the alarm sounded. Which "
    "student has reasoned correctly?",
    key=_w11, verify=says("Omar", "A door was opened"),
    wrong=[says("Pia", "No door was opened"),
           says("Quill", "Opening a door always sets the alarm off"),
           says("Rae", "The alarm will sound again tonight")],
    expl="'Only if' means the alarm cannot sound without a door being opened, so one was. "
         "Quill turns it round into a guarantee the rule never gives — a door might be "
         "opened with the alarm switched off.",
    difficulty="hard", confidence=0.91),

_S12 = Scenario(["hall", "study", "car"],
                given=[ORo("hall", "study", "car"), NOTo("hall"), NOTo("study")])
_w12 = _S12.pick([(says("Sol", "The book is in the car"), _S12.here(ISo("car"))),
                  (says("Tam", "The book is in the hall"), _S12.here(ISo("hall"))),
                  (says("Uri", "The book is in the study"), _S12.here(ISo("study"))),
                  (says("Vale", "The book has been lost"),
                   _S12.here(lambda i: lambda m: not any(
                       m[f"{n}@{i}"] for n in ("hall", "study", "car"))))])
B.Q("who_reasons_correctly",
    "The book is in the hall, the study or the car. It is not in the hall and not in the "
    "study. Which student has reasoned correctly?",
    key=_w12, verify=says("Sol", "The book is in the car"),
    wrong=[says("Tam", "The book is in the hall"),
           says("Uri", "The book is in the study"),
           says("Vale", "The book has been lost")],
    expl="Three places were offered and two are ruled out, so the third is left. Vale's "
         "answer denies the first statement rather than working from it.",
    difficulty="medium", confidence=0.92),

_w13 = syllogism(["listed", "invited", "sam"],
                 [ALL("listed", "invited"), NO("sam", "invited")],
                 [(says("Wynn", "Sam was not on the list"), NO("sam", "listed")),
                  (says("Xia", "Sam was on the list"), ALL("sam", "listed")),
                  (says("Yara", "Everyone invited was on the list"), ALL("invited", "listed")),
                  (says("Zane", "Nobody on the list was invited"), NO("listed", "invited"))])
B.Q("who_reasons_correctly",
    "Everyone on the list was invited. Sam was not invited. Which student has reasoned "
    "correctly?",
    key=_w13, verify=says("Wynn", "Sam was not on the list"),
    wrong=[says("Xia", "Sam was on the list"),
           says("Yara", "Everyone invited was on the list"),
           says("Zane", "Nobody on the list was invited")],
    expl="Being on the list guarantees an invitation, and Sam has none, so Sam was not on "
         "it. Yara reverses that: other people may have been invited without the list.",
    difficulty="medium", confidence=0.92),

_S14 = Scenario(["rose", "flooded", "closed"],
                rules=[IFo("rose", "flooded"), IFo("flooded", "closed")],
                given=[ISo("rose")])
_w14 = _S14.pick([(says("Ada", "The school closes"), _S14.here(ISo("closed"))),
                  (says("Bram", "The school stays open"), _S14.here(NOTo("closed"))),
                  (says("Cleo", "The road stayed dry"), _S14.here(NOTo("flooded"))),
                  (says("Dov", "The school closes only when the river rises"),
                   _S14.always(IFo("closed", "rose")))])
B.Q("who_reasons_correctly",
    "If the river rises, the road floods. If the road floods, the school closes. Last night "
    "the river rose. Which student has reasoned correctly?",
    key=_w14, verify=says("Ada", "The school closes"),
    wrong=[says("Bram", "The school stays open"),
           says("Cleo", "The road stayed dry"),
           says("Dov", "The school closes only when the river rises")],
    expl="The rules chain: a rising river floods the road, and a flooded road closes the "
         "school. Dov reverses the chain, and the school could close for a public holiday.",
    difficulty="medium", confidence=0.92),

_w15 = syllogism(["scout", "camper", "swimmer"],
                 [ALL("scout", "camper"), SOME("scout", "swimmer")],
                 [(says("Emi", "Some campers can swim"), SOME("camper", "swimmer")),
                  (says("Fen", "All campers can swim"), ALL("camper", "swimmer")),
                  (says("Gil", "All swimmers are scouts"), ALL("swimmer", "scout")),
                  (says("Hume", "No camper can swim"), NO("camper", "swimmer"))])
B.Q("who_reasons_correctly",
    "Every scout in the troop is a camper. Some of the scouts can swim. Which student has "
    "reasoned correctly?",
    key=_w15, verify=says("Emi", "Some campers can swim"),
    wrong=[says("Fen", "All campers can swim"),
           says("Gil", "All swimmers are scouts"),
           says("Hume", "No camper can swim")],
    expl="A scout who swims is also a camper, so at least one camper swims. Campers who are "
         "not scouts are not covered, so nothing follows about all of them.",
    difficulty="hard", confidence=0.90),

_S16 = Scenario(["sunday", "running", "serviced"],
                rules=[lambda i: lambda m: m[f"running@{i}"] != m[f"sunday@{i}"]],
                given=[NOTo("running")])
_w16 = _S16.pick([(says("Ines", "Today is Sunday"), _S16.here(ISo("sunday"))),
                  (says("Jonah", "Today is not Sunday"), _S16.here(NOTo("sunday"))),
                  (says("Kaya", "The machine never runs"), _S16.always(NOTo("running"))),
                  (says("Loki", "The machine is being serviced"), _S16.here(ISo("serviced")))])
B.Q("who_reasons_correctly",
    "The machine runs every day except Sunday, when it is switched off. Today the machine "
    "is not running. Which student has reasoned correctly?",
    key=_w16, verify=says("Ines", "Today is Sunday"),
    wrong=[says("Jonah", "Today is not Sunday"),
           says("Kaya", "The machine never runs"),
           says("Loki", "The machine is being serviced")],
    expl="Sunday is the only day the machine is off, so a machine that is off means it is "
         "Sunday. Loki offers an explanation the statement never mentions.",
    difficulty="hard", confidence=0.91),

# ===================================================== necessary vs sufficient (16)

conditional("necessary_vs_sufficient",
            "Nobody may board the flight without a passport. Ana has a passport. Which one "
            "of these must be true?",
            "board", "passport", ISo("passport"),
            [("Everyone who boards the flight holds a passport",
              lambda S: S.always(IFo("board", "passport"))),
             ("Ana boarded the flight", lambda S: S.here(ISo("board"))),
             ("Ana did not board the flight", lambda S: S.here(NOTo("board"))),
             ("Everyone holding a passport boards the flight",
              lambda S: S.always(IFo("passport", "board")))],
            "The rule works one way: boarding requires a passport, so every passenger has "
            "one. It does not work backwards. Ana meets the requirement but may have no "
            "ticket, or may have missed the flight entirely.",
            difficulty="hard", confidence=0.90)

conditional("necessary_vs_sufficient",
            "Scoring 50 is enough on its own to pass the course. Ben scored 40. Which one "
            "of these must be true?",
            "fifty", "pass", NOTo("fifty"),
            [("Nothing follows about whether Ben passed", NOTHING),
             ("Ben passed the course", lambda S: S.here(ISo("pass"))),
             ("Ben did not pass the course", lambda S: S.here(NOTo("pass"))),
             ("Only those scoring 50 pass the course",
              lambda S: S.always(IFo("pass", "fifty")))],
            "Fifty is enough, but the rule never says it is the only way through. Ben may "
            "have passed on coursework or on a second attempt.",
            difficulty="hard", confidence=0.90)

conditional("necessary_vs_sufficient",
            "Swimmers are not allowed in the pool without a swimming cap. Cy is wearing a "
            "cap. Which one of these must be true?",
            "inpool", "cap", ISo("cap"),
            [("Everyone in the pool is wearing a cap",
              lambda S: S.always(IFo("inpool", "cap"))),
             ("Cy is in the pool", lambda S: S.here(ISo("inpool"))),
             ("Cy is not in the pool", lambda S: S.here(NOTo("inpool"))),
             ("Everyone wearing a cap is in the pool",
              lambda S: S.always(IFo("cap", "inpool")))],
            "The rule requires a cap of everyone in the pool, so all of them are wearing "
            "one. A cap is a condition of getting in, not a ticket in — Cy may be sitting at "
            "the side.",
            difficulty="medium", confidence=0.92)

conditional("necessary_vs_sufficient",
            "You cannot vote unless you are over 18. Dot is 15. Which one of these must be "
            "true?",
            "vote", "over18", NOTo("over18"),
            [("Dot did not vote", lambda S: S.here(NOTo("vote"))),
             ("Dot voted", lambda S: S.here(ISo("vote"))),
             ("Everyone over 18 votes", lambda S: S.always(IFo("over18", "vote"))),
             ("Nothing follows about whether Dot voted", NOTHING)],
            "Being over 18 is required, and Dot is not, so Dot did not vote. The rule does "
            "not run the other way: plenty of adults never vote.",
            difficulty="medium", confidence=0.92)

conditional("necessary_vs_sufficient",
            "A power cut is enough on its own to stop the lift. There was no power cut "
            "today. Which one of these must be true?",
            "cut", "stopped", NOTo("cut"),
            [("Nothing follows about whether the lift stopped", NOTHING),
             ("The lift stopped", lambda S: S.here(ISo("stopped"))),
             ("The lift did not stop", lambda S: S.here(NOTo("stopped"))),
             ("Only a power cut stops the lift",
              lambda S: S.always(IFo("stopped", "cut")))],
            "A power cut would stop the lift, but so might a fault or a service call. With "
            "no cut, nothing at all is settled about the lift.",
            difficulty="hard", confidence=0.90)

conditional("necessary_vs_sufficient",
            "No plant flowers without light. This plant was kept in the dark all season. "
            "Which one of these must be true?",
            "flowered", "light", NOTo("light"),
            [("The plant did not flower", lambda S: S.here(NOTo("flowered"))),
             ("The plant flowered", lambda S: S.here(ISo("flowered"))),
             ("Light alone makes a plant flower",
              lambda S: S.always(IFo("light", "flowered"))),
             ("Nothing follows about whether it flowered", NOTHING)],
            "Light is required for flowering and this plant had none, so it did not flower. "
            "Light on its own would not have been enough either — warmth and water are "
            "needed as well.",
            difficulty="medium", confidence=0.92)

conditional("necessary_vs_sufficient",
            "Only club members may book the hall. The hall was booked on Saturday. Which "
            "one of these must be true?",
            "booked", "member", ISo("booked"),
            [("A member made the booking", lambda S: S.here(ISo("member"))),
             ("No member made the booking", lambda S: S.here(NOTo("member"))),
             ("Every member has booked the hall",
              lambda S: S.always(IFo("member", "booked"))),
             ("Nothing follows about who booked it", NOTHING)],
            "Only members can book, so whoever booked is a member. That says nothing about "
            "members in general — most will never have booked it.",
            difficulty="medium", confidence=0.92)

conditional("necessary_vs_sufficient",
            "Holding a ticket is enough on its own to enter the draw. Eve entered the draw. "
            "Which one of these must be true?",
            "ticket", "entered", ISo("entered"),
            [("Nothing follows about whether Eve holds a ticket", NOTHING),
             ("Eve holds a ticket", lambda S: S.here(ISo("ticket"))),
             ("Eve holds no ticket", lambda S: S.here(NOTo("ticket"))),
             ("Only ticket holders enter the draw",
              lambda S: S.always(IFo("entered", "ticket")))],
            "A ticket gets you in, but the rule does not say it is the only way. Eve may "
            "have been entered as a volunteer or as a prize winner.",
            difficulty="hard", confidence=0.90)

conditional("necessary_vs_sufficient",
            "A form is not accepted unless it is signed. This form was accepted. Which one "
            "of these must be true?",
            "accepted", "signed", ISo("accepted"),
            [("The form was signed", lambda S: S.here(ISo("signed"))),
             ("The form was not signed", lambda S: S.here(NOTo("signed"))),
             ("Every signed form is accepted",
              lambda S: S.always(IFo("signed", "accepted"))),
             ("Nothing follows about the signature", NOTHING)],
            "A signature is required for acceptance, so an accepted form carries one. Plenty "
            "of signed forms will still be rejected for other reasons.",
            difficulty="medium", confidence=0.92)

conditional("necessary_vs_sufficient",
            "Studying every night is enough on its own to pass the test. Fay studied every "
            "night. Which one of these must be true?",
            "studied", "passed", ISo("studied"),
            [("Fay passed the test", lambda S: S.here(ISo("passed"))),
             ("Fay did not pass the test", lambda S: S.here(NOTo("passed"))),
             ("Only those who study every night pass",
              lambda S: S.always(IFo("passed", "studied"))),
             ("Nothing follows about whether Fay passed", NOTHING)],
            "Studying every night guarantees a pass, and Fay did, so Fay passed. It does not "
            "follow that everyone who passed studied that way.",
            difficulty="medium", confidence=0.92)

conditional("necessary_vs_sufficient",
            "The summit cannot be seen unless the sky is clear. This morning the summit was "
            "visible. Which one of these must be true?",
            "visible", "clear", ISo("visible"),
            [("The sky was clear", lambda S: S.here(ISo("clear"))),
             ("The sky was not clear", lambda S: S.here(NOTo("clear"))),
             ("A clear sky always brings the summit into view",
              lambda S: S.always(IFo("clear", "visible"))),
             ("Nothing follows about the sky", NOTHING)],
            "A clear sky is required for the summit to show, so it was clear. The reverse "
            "fails: haze or distance can hide a summit on a cloudless day.",
            difficulty="hard", confidence=0.91)

conditional("necessary_vs_sufficient",
            "Riders must be at least 140 cm tall to go on the ride. Gus is 150 cm. Which "
            "one of these must be true?",
            "rode", "tall", ISo("tall"),
            [("Everyone on the ride is at least 140 cm tall",
              lambda S: S.always(IFo("rode", "tall"))),
             ("Gus went on the ride", lambda S: S.here(ISo("rode"))),
             ("Gus did not go on the ride", lambda S: S.here(NOTo("rode"))),
             ("Everyone at least 140 cm tall goes on the ride",
              lambda S: S.always(IFo("tall", "rode")))],
            "The height bar applies to everyone who rides, so all of them clear it. Height "
            "is a requirement, not an admission — Gus clears it but may have run out of "
            "tickets or simply not wanted to.",
            difficulty="hard", confidence=0.90)

conditional("necessary_vs_sufficient",
            # 0.828 against p20's store-room-key item; recast as a vehicle with an "
            # immobiliser so the surface no longer matches
            "A truck will not start unless the immobiliser is switched off. The delivery "
            "truck started first time this morning. Which one of these must be true?",
            "started", "off", ISo("started"),
            [("The immobiliser had been switched off", lambda S: S.here(ISo("off"))),
             ("The immobiliser was still on", lambda S: S.here(NOTo("off"))),
             ("Switching the immobiliser off starts the truck",
              lambda S: S.always(IFo("off", "started"))),
             ("Nothing follows about the immobiliser", NOTHING)],
            "The immobiliser has to be off before the truck will start, so it was off. "
            "Switching it off would not start the truck on its own — a flat battery would "
            "still leave it silent.",
            difficulty="medium", confidence=0.92)

conditional("necessary_vs_sufficient",
            "Winning both heats is enough on its own to reach the final. Hana did not win "
            "both heats. Which one of these must be true?",
            "bothheats", "final", NOTo("bothheats"),
            [("Nothing follows about whether Hana reached the final", NOTHING),
             ("Hana reached the final", lambda S: S.here(ISo("final"))),
             ("Hana did not reach the final", lambda S: S.here(NOTo("final"))),
             ("Only those winning both heats reach the final",
              lambda S: S.always(IFo("final", "bothheats")))],
            "Two wins would have taken her through, but the rule does not say that is the "
            "only route. A fast losing time might carry her in as well.",
            difficulty="hard", confidence=0.90)

conditional("necessary_vs_sufficient",
            "Nobody is admitted to the restaurant without a booking. Ivo had no booking. "
            "Which one of these must be true?",
            "admitted", "booking", NOTo("booking"),
            [("Ivo was not admitted", lambda S: S.here(NOTo("admitted"))),
             ("Ivo was admitted", lambda S: S.here(ISo("admitted"))),
             ("Every booking gets somebody a table",
              lambda S: S.always(IFo("booking", "admitted"))),
             ("Nothing follows about whether Ivo got in", NOTHING)],
            "A booking is required and Ivo had none, so Ivo did not get in. A booking would "
            "not have guaranteed a table either — the restaurant might have been shut.",
            difficulty="medium", confidence=0.92)

conditional("necessary_vs_sufficient",
            "Students cannot go on the trip unless the fee has been paid. Jai has paid the "
            "fee. Which one of these must be true?",
            "went", "paid", ISo("paid"),
            [("Nothing follows about whether Jai went", NOTHING),
             ("Jai went on the trip", lambda S: S.here(ISo("went"))),
             ("Jai did not go on the trip", lambda S: S.here(NOTo("went"))),
             ("Paying the fee puts a student on the trip",
              lambda S: S.always(IFo("paid", "went")))],
            "Paying is required before going, which is not the same as paying sending you. "
            "Jai may have fallen ill, or the trip may have been cancelled.",
            difficulty="hard", confidence=0.90)

B.write()
