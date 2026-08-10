#!/usr/bin/env python3
"""Builds lr_thinking_skills_p31.json — 32 questions across four subcategories.

formal syllogism 15, ordering and ranking 14, correlation vs causation 1, necessary vs
sufficient 2. syllogism_formal closes at 45/45, ordering_ranking at 55/55 and
correlation_vs_causation at 26/26. Thinking Skills reaches 871/880.

Every syllogism is model-checked over all four options, so the build proves both that the
key follows and that no distractor does. Every ordering puzzle is enumerated. Nothing
here rests on my reading of it.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.lr.lr_common import Batch  # noqa: E402
from tools.lr.lr_logic import (  # noqa: E402
    ALL, IFo, ISo, NO, NOTHING, NOTo, SOME, SOME_NOT, Scenario, order, syllogism,
)
from tools.lr.lr_prose import must_balance, must_restate  # noqa: E402

B = Batch(nn=31)

# ===================================================== formal syllogism (15)

# (cats, premises, stem, options as (text, conclusion), explanation)
SYLLOGISMS = [
    (["wren", "bird", "nester"], [ALL("wren", "bird"), ALL("bird", "nester")],
     "All wrens are birds. All birds build nests. Which one of these must be true?",
     [("All wrens build nests", ALL("wren", "nester")),
      ("All nest builders are wrens", ALL("nester", "wren")),
      ("No wren builds a nest", NO("wren", "nester")),
      ("Some birds do not build nests", SOME_NOT("bird", "nester"))],
     "Every wren sits inside the birds and every bird inside the nest builders, so every "
     "wren builds a nest. The reverse fails: wasps build nests and are not wrens."),
    (["gum", "tree", "shedder"], [ALL("gum", "tree"), SOME("gum", "shedder")],
     "All gums are trees. Some gums shed their bark. Which one of these must be true?",
     [("Some trees shed their bark", SOME("tree", "shedder")),
      ("All trees shed their bark", ALL("tree", "shedder")),
      ("All bark shedders are gums", ALL("shedder", "gum")),
      ("No tree sheds its bark", NO("tree", "shedder"))],
     "A gum that sheds bark is also a tree, so at least one tree sheds bark. Trees that are "
     "not gums are not covered, so nothing follows about all of them."),
    (["cane", "toad", "native"], [ALL("cane", "toad"), NO("toad", "native")],
     "All cane toads are toads. No toad is native to this island. Which one of these must "
     "be true?",
     [("No cane toad is native to the island", NO("cane", "native")),
      ("All toads are cane toads", ALL("toad", "cane")),
      ("Some cane toads are native", SOME("cane", "native")),
      ("All native animals are toads", ALL("native", "toad"))],
     "Cane toads are all toads, and no toad is native here, so no cane toad is native. "
     "That says nothing about toads in general being cane toads."),
    (["diver", "swimmer", "member"], [ALL("diver", "swimmer"), ALL("diver", "member")],
     "Every diver in the club can swim. Every diver in the club is a member. Which one of "
     "these must be true?",
     [("Some members can swim", SOME("member", "swimmer")),
      ("All members can swim", ALL("member", "swimmer")),
      ("All swimmers are members", ALL("swimmer", "member")),
      ("No member can swim", NO("member", "swimmer"))],
     "The divers are members and they can all swim, so at least some members swim. Members "
     "who do not dive are not covered by either statement."),
    # "All orchids are flowers. Some orchids have no scent." scored 0.828 against p19's
    # boronia item — flowers and scent twice over. Moved to a different subject entirely.
    (["kelpie", "workdog", "barker"],
     [ALL("kelpie", "workdog"), SOME_NOT("kelpie", "barker")],
     "Every kelpie on the property is a working dog. Some of the kelpies never bark. Which "
     "one of these must be true?",
     [("Some working dogs never bark", SOME_NOT("workdog", "barker")),
      ("No working dog barks", NO("workdog", "barker")),
      ("Every working dog is a kelpie", ALL("workdog", "kelpie")),
      ("Everything that barks is a kelpie", ALL("barker", "kelpie"))],
     "A kelpie that never barks is a working dog that never barks, so some working dogs do "
     "not bark. Nothing follows about the working dogs that are not kelpies."),
    (["poet", "writer", "reader"], [ALL("poet", "writer"), ALL("writer", "reader")],
     "All poets are writers. All writers are readers. Which one of these must be true?",
     [("All poets are readers", ALL("poet", "reader")),
      ("All readers are poets", ALL("reader", "poet")),
      ("Some writers are not readers", SOME_NOT("writer", "reader")),
      ("No poet is a reader", NO("poet", "reader"))],
     "The chain runs from poets through writers to readers, so every poet reads. Reading it "
     "backwards would make every reader a poet, which the statements never say."),
    (["magpie", "songbird", "mimic"], [ALL("magpie", "songbird"), SOME("magpie", "mimic")],
     "All magpies are songbirds. Some magpies mimic other sounds. Which one of these must "
     "be true?",
     [("Some songbirds mimic other sounds", SOME("songbird", "mimic")),
      ("All songbirds mimic other sounds", ALL("songbird", "mimic")),
      ("All mimics are magpies", ALL("mimic", "magpie")),
      ("No songbird mimics other sounds", NO("songbird", "mimic"))],
     "A magpie that mimics is a songbird that mimics, so at least one songbird does. "
     "Songbirds that are not magpies are outside what was said."),
    (["ute", "vehicle", "registered"], [ALL("ute", "vehicle"), NO("vehicle", "registered")],
     "Every ute in the yard is a vehicle. No vehicle in the yard is registered. Which one "
     "of these must be true?",
     [("No ute in the yard is registered", NO("ute", "registered")),
      ("All vehicles in the yard are utes", ALL("vehicle", "ute")),
      ("Some utes in the yard are registered", SOME("ute", "registered")),
      ("All registered vehicles are in the yard", ALL("registered", "vehicle"))],
     "Utes in the yard are vehicles in the yard, and none of those is registered, so no ute "
     "there is registered either."),
    (["fern", "plant", "shade"], [ALL("fern", "plant"), ALL("fern", "shade")],
     "All ferns are plants. All ferns grow in shade. Which one of these must be true?",
     [("Some plants grow in shade", SOME("plant", "shade")),
      ("All plants grow in shade", ALL("plant", "shade")),
      ("All shade growers are ferns", ALL("shade", "fern")),
      ("No plant grows in shade", NO("plant", "shade"))],
     "Ferns are plants and they all grow in shade, so at least some plants do. Plants that "
     "are not ferns are not covered."),
    (["clerk", "staff", "trained"], [ALL("clerk", "staff"), ALL("staff", "trained")],
     "All clerks are staff. All staff have been trained. Which one of these must be true?",
     [("All clerks have been trained", ALL("clerk", "trained")),
      ("All trained people are clerks", ALL("trained", "clerk")),
      ("Some staff have not been trained", SOME_NOT("staff", "trained")),
      ("No clerk has been trained", NO("clerk", "trained"))],
     "Clerks are staff and all staff are trained, so all clerks are trained. Plenty of "
     "trained people will not be clerks at all."),
    (["salmon", "fish", "farmed"], [ALL("salmon", "fish"), SOME_NOT("salmon", "farmed")],
     "All salmon are fish. Some salmon are not farmed. Which one of these must be true?",
     [("Some fish are not farmed", SOME_NOT("fish", "farmed")),
      ("No fish is farmed", NO("fish", "farmed")),
      ("All fish are salmon", ALL("fish", "salmon")),
      ("All farmed things are salmon", ALL("farmed", "salmon"))],
     "A wild salmon is a fish that is not farmed, so some fish are not farmed. That leaves "
     "the rest of the fish entirely open."),
    (["dingo", "hunter", "howler"], [SOME("dingo", "howler"), ALL("dingo", "hunter")],
     "Some dingoes howl at night. Every dingo hunts. Which one of these must be true?",
     [("Some hunters howl at night", SOME("hunter", "howler")),
      ("Every hunter howls at night", ALL("hunter", "howler")),
      ("Everything that howls at night is a dingo", ALL("howler", "dingo")),
      ("No hunter howls at night", NO("hunter", "howler"))],
     "A dingo that howls is a hunter that howls, so at least some hunters howl. Hunters "
     "that are not dingoes are outside what was said, so nothing follows about all of "
     "them."),
    (["scout", "camper", "cook"], [NO("scout", "cook"), ALL("camper", "scout")],
     "No scout in the troop can cook. All the campers are scouts in the troop. Which one "
     "of these must be true?",
     [("No camper can cook", NO("camper", "cook")),
      ("All scouts are campers", ALL("scout", "camper")),
      ("Some campers can cook", SOME("camper", "cook")),
      ("All cooks are scouts", ALL("cook", "scout"))],
     "The campers are all scouts, and no scout can cook, so no camper can. Scouts who are "
     "not campers are still scouts, so the reverse does not follow."),
    (["cellist", "player", "reader"], [ALL("cellist", "player"), SOME("cellist", "reader")],
     "All cellists in the orchestra are players. Some cellists read music by sight. Which "
     "one of these must be true?",
     [("Some players read music by sight", SOME("player", "reader")),
      ("All players read music by sight", ALL("player", "reader")),
      ("All sight readers are cellists", ALL("reader", "cellist")),
      ("No player reads music by sight", NO("player", "reader"))],
     "A cellist who sight-reads is a player who sight-reads, so at least one player does. "
     "The other players are not described either way."),
    (["cactus", "plant", "waterer"], [ALL("cactus", "plant"), NO("cactus", "waterer")],
     "All cacti are plants. No cactus needs daily watering. Which one of these must be "
     "true?",
     [("Some plants do not need daily watering", SOME_NOT("plant", "waterer")),
      ("No plant needs daily watering", NO("plant", "waterer")),
      ("All plants are cacti", ALL("plant", "cactus")),
      ("All plants needing daily watering are cacti", ALL("waterer", "cactus"))],
     "A cactus is a plant that does not need daily watering, so some plants do not. Ferns "
     "still might, which is why the stronger claim fails."),
]

for _i, (_cats, _prem, _stem, _opts, _expl) in enumerate(SYLLOGISMS):
    _key = syllogism(_cats, _prem, _opts)
    B.Q("syllogism_formal", _stem,
        key=_key, verify=_key,
        wrong=[t for t, _ in _opts if t != _key],
        expl=_expl,
        difficulty="hard" if _i % 3 else "medium",
        confidence=0.90 if _i % 3 else 0.92)

# ===================================================== ordering and ranking (14)

PLACE = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth"}

_r1 = order(["Anya", "Beau", "Cleo"],
            [lambda p: p["Anya"] > p["Beau"], lambda p: p["Cleo"] > p["Anya"]])
B.Q("ordering_ranking",
    "Three towers are ranked by height, tallest first, with none the same. Anya's tower is "
    "shorter than Beau's. Cleo's is shorter than Anya's. Whose tower is the tallest?",
    key="Beau's", verify=f"{min(_r1, key=_r1.get)}'s",
    wrong=["Anya's", "Cleo's", "it cannot be worked out"],
    expl="The chain runs Beau's above Anya's and Anya's above Cleo's, so Beau's is at the "
         "top and Cleo's at the bottom.",
    difficulty="medium", confidence=0.92),

_r2 = order(["Dex", "Elsa", "Finn", "Gus"],
            [lambda p: p["Dex"] == 1, lambda p: p["Elsa"] == p["Finn"] + 1,
             lambda p: p["Gus"] == 4])
B.Q("ordering_ranking",
    "Four children queue for tickets. Dex is at the front and Gus at the back. Elsa stands "
    "directly behind Finn. Who is second in the queue?",
    key=next(n for n, v in _r2.items() if v == 2), verify=sorted(_r2, key=_r2.get)[1],
    wrong=["Elsa", "Dex", "Gus"],
    expl="Dex and Gus take the ends, so Finn and Elsa fill second and third. Elsa is "
         "directly behind Finn, so Finn is second and Elsa third.",
    difficulty="medium", confidence=0.92),

_r3 = order(["Hana", "Idris", "Jo", "Kit"],
            [lambda p: p["Hana"] < p["Idris"] < p["Jo"], lambda p: p["Kit"] < p["Hana"]])
B.Q("ordering_ranking",
    "Four parcels are weighed, lightest first, with no two the same. Hana's is lighter than "
    "Idris's, which is lighter than Jo's. Kit's is lighter than Hana's. Whose parcel is "
    "heaviest?",
    key="Jo's", verify=f"{max(_r3, key=_r3.get)}'s",
    wrong=["Hana's", "Idris's", "Kit's"],
    expl="Reading the clues as one chain gives Kit's, Hana's, Idris's and Jo's from "
         "lightest to heaviest, so Jo's is the heaviest.",
    difficulty="medium", confidence=0.92),

_r4 = order(["Lila", "Marco", "Nev", "Ola", "Piotr"],
            [lambda p: p["Lila"] == 3, lambda p: p["Marco"] < p["Lila"],
             lambda p: p["Nev"] == 5, lambda p: p["Ola"] == p["Marco"] + 1,
             lambda p: p["Piotr"] > p["Lila"]])
B.Q("ordering_ranking",
    "Five athletes finish a race with no ties. Lila comes third and Nev comes last. Marco "
    "finishes ahead of Lila, and Ola finishes directly behind Marco. Piotr finishes behind "
    "Lila. In which place does Ola finish?",
    key=PLACE[_r4["Ola"]], verify=PLACE[_r4["Marco"] + 1],
    wrong=["first", "third", "fourth"],
    expl="Marco and Ola are next to each other and both ahead of Lila in third, so they "
         "take first and second with Marco first. Piotr and Nev fill fourth and fifth.",
    difficulty="hard", confidence=0.90),

_r5 = order(["Quill", "Rosa", "Sami"],
            [lambda p: p["Quill"] != 1, lambda p: p["Quill"] != 3,
             lambda p: p["Rosa"] < p["Sami"]])
B.Q("ordering_ranking",
    "Three runners finish with no ties. Quill is neither first nor last. Rosa finishes "
    "ahead of Sami. Who finishes last?",
    key=next(n for n, v in _r5.items() if v == 3), verify=max(_r5, key=_r5.get),
    wrong=["Quill", "Rosa", "it cannot be worked out"],
    expl="Quill is neither first nor last, so Quill is second. Rosa is ahead of Sami, so "
         "Rosa is first and Sami last.",
    difficulty="medium", confidence=0.92),

_r6 = order(["Tao", "Uma", "Vik", "Wren"],
            [lambda p: abs(p["Tao"] - p["Uma"]) == 2, lambda p: p["Vik"] == 1,
             lambda p: p["Tao"] < p["Uma"], lambda p: p["Wren"] == 3])
B.Q("ordering_ranking",
    "Four flags stand in a row. Vik's is at the left-hand end and Wren's is third from the "
    "left. Tao's and Uma's have exactly one flag between them, with Tao's the further "
    "left. Whose flag is at the right-hand end?",
    key=f"{next(n for n, v in _r6.items() if v == 4)}'s",
    verify=f"{max(_r6, key=_r6.get)}'s",
    wrong=["Tao's", "Vik's", "Wren's"],
    expl="Vik is first and Wren third, so Tao and Uma take second and fourth — which is "
         "exactly one flag apart, with Tao second and Uma fourth.",
    difficulty="hard", confidence=0.90),

_r7 = order(["Xen", "Yara", "Zed", "Ada"],
            [lambda p: p["Xen"] > p["Yara"], lambda p: p["Zed"] > p["Xen"],
             lambda p: p["Ada"] > p["Zed"]])
B.Q("ordering_ranking",
    "Four students are ranked by mark, highest first, with no ties. Xen scored below Yara. "
    "Zed scored below Xen. Ada scored below Zed. Who came second?",
    key=next(n for n, v in _r7.items() if v == 2), verify=sorted(_r7, key=_r7.get)[1],
    wrong=["Yara", "Zed", "Ada"],
    expl="The chain runs Yara above Xen, Xen above Zed and Zed above Ada, so Yara is first "
         "and Xen second.",
    difficulty="medium", confidence=0.92),

_r8 = order(["Bo", "Cara", "Dan", "Eve", "Fai"],
            [lambda p: p["Bo"] == 2, lambda p: p["Cara"] > p["Dan"],
             lambda p: p["Eve"] == 1, lambda p: p["Fai"] == p["Cara"] + 1,
             lambda p: p["Dan"] == 3])
B.Q("ordering_ranking",
    "Five books sit on a shelf from left to right. Eve's is at the far left and Bo's is "
    "second. Dan's is third. Cara's is to the right of Dan's, and Fai's is directly to the "
    "right of Cara's. Whose book is at the far right?",
    key=f"{next(n for n, v in _r8.items() if v == 5)}'s",
    verify=f"{max(_r8, key=_r8.get)}'s",
    wrong=["Cara's", "Dan's", "Bo's"],
    expl="Eve is at the far left with Bo next and Dan third, so Cara and Fai take the two "
         "remaining spots. Fai is directly right of Cara, so Cara is fourth and Fai fifth.",
    difficulty="hard", confidence=0.90),

# two arrangements fitted the first draft — Gil first with Hugo second, and Ines first
# with Gil second — and the explanation had started hedging rather than deciding
_r9 = order(["Gil", "Hugo", "Ines"],
            [lambda p: p["Gil"] < p["Hugo"], lambda p: p["Ines"] != 2,
             lambda p: p["Gil"] != 1])
B.Q("ordering_ranking",
    "Three cyclists finish with no ties. Gil finishes ahead of Hugo but does not win. Ines "
    "is not second. Who finishes second?",
    key=next(n for n, v in _r9.items() if v == 2), verify=sorted(_r9, key=_r9.get)[1],
    wrong=["Hugo", "Ines", "it cannot be worked out"],
    expl="Gil does not win but finishes ahead of Hugo, so Gil is second and Hugo third. "
         "That leaves first place for Ines, which also fits Ines not being second.",
    difficulty="hard", confidence=0.90),

_r10 = order(["Jai", "Kez", "Lou", "Mia"],
             [lambda p: p["Jai"] == 4, lambda p: p["Kez"] < p["Lou"] < p["Mia"]])
B.Q("ordering_ranking",
    "Four swimmers are ranked by time, fastest first, with no ties. Jai is the slowest. Kez "
    "is faster than Lou, and Lou is faster than Mia. Who is the fastest?",
    key=next(n for n, v in _r10.items() if v == 1), verify=min(_r10, key=_r10.get),
    wrong=["Lou", "Mia", "Jai"],
    expl="Jai is slowest, and the remaining chain runs Kez above Lou and Lou above Mia, so "
         "Kez is the fastest of them.",
    difficulty="medium", confidence=0.92),

_r11 = order(["Nia", "Oz", "Pim", "Rex"],
             [lambda p: p["Nia"] == p["Oz"] - 1, lambda p: p["Pim"] == 1,
              lambda p: p["Rex"] > p["Oz"]])
B.Q("ordering_ranking",
    "Four people board a bus one after another. Pim boards first. Nia boards directly "
    "before Oz. Rex boards after Oz. Who boards third?",
    key=next(n for n, v in _r11.items() if v == 3), verify=sorted(_r11, key=_r11.get)[2],
    wrong=["Nia", "Pim", "Rex"],
    expl="Pim is first, and Rex is after Oz, so Rex is last. Nia and Oz fill second and "
         "third in that order, so Oz boards third.",
    difficulty="hard", confidence=0.90),

_r12 = order(["Sia", "Tomas", "Uli", "Val", "Wen"],
             [lambda p: p["Sia"] == 5, lambda p: p["Tomas"] < p["Uli"],
              lambda p: p["Uli"] < p["Val"], lambda p: p["Wen"] == 1,
              lambda p: p["Val"] == 4])
B.Q("ordering_ranking",
    "Five towns lie along a road from west to east. Wen's town is furthest west and Sia's "
    "furthest east. Val's is fourth from the west. Tomas's town is west of Uli's, and "
    "Uli's is west of Val's. Which town is third from the west?",
    key=f"{next(n for n, v in _r12.items() if v == 3)}'s",
    verify=f"{sorted(_r12, key=_r12.get)[2]}'s",
    wrong=["Tomas's", "Val's", "Wen's"],
    expl="Wen is first, Val fourth and Sia fifth, so Tomas and Uli take second and third. "
         "Tomas is west of Uli, so Tomas is second and Uli third.",
    difficulty="hard", confidence=0.90),

_r13 = order(["Ari", "Bea", "Cy"],
             [lambda p: p["Ari"] != 3, lambda p: p["Bea"] > p["Cy"],
              lambda p: p["Ari"] > p["Cy"]])
B.Q("ordering_ranking",
    "Three trees are ranked by age, oldest first, with none the same. Ari's tree is not the "
    "youngest. Bea's is younger than Cy's, and Ari's is younger than Cy's. Whose tree is "
    "the oldest?",
    key=f"{next(n for n, v in _r13.items() if v == 1)}'s",
    verify=f"{min(_r13, key=_r13.get)}'s",
    wrong=["Ari's", "Bea's", "it cannot be worked out"],
    expl="Cy's tree is older than both the others, so Cy's is oldest. Ari's is not the "
         "youngest, so Ari's is in the middle and Bea's is youngest.",
    difficulty="hard", confidence=0.91),

_r14 = order(["Dee", "Emre", "Fern", "Gwen"],
             [lambda p: p["Dee"] < p["Emre"], lambda p: p["Fern"] == 1,
              lambda p: p["Gwen"] == p["Dee"] + 1, lambda p: p["Emre"] == 4])
B.Q("ordering_ranking",
    "Four horses finish a race with no ties. Fern's horse wins and Emre's comes last. Dee's "
    "finishes ahead of Emre's, and Gwen's finishes directly behind Dee's. In which place "
    "does Gwen's horse finish?",
    key=PLACE[_r14["Gwen"]], verify=PLACE[_r14["Dee"] + 1],
    wrong=["first", "second", "fourth"],
    expl="Fern is first and Emre fourth, so Dee and Gwen take second and third. Gwen is "
         "directly behind Dee, so Dee is second and Gwen third.",
    difficulty="medium", confidence=0.92),

# ===================================================== correlation vs causation (1)

_CORR = ("In a survey of shopping centres, the ones with the most security staff also "
         "record the most shoplifting.")
_RESTATE = "The centres recording the most shoplifting are the ones with the most staff."
must_restate(_RESTATE, _CORR, "shoplifting [restatement]")
_KEY = "Centres with a shoplifting problem hire extra staff to deal with it."
_CAUSAL = "The presence of security staff causes shoppers to steal more often."
_IRREL = "Security staff at most centres work in shifts of eight hours."
must_balance([_KEY, _CAUSAL, _IRREL, _RESTATE], "shoplifting")
B.Q("correlation_vs_causation",
    f"{_CORR} Which one of these best explains the link, without one of the two causing "
    f"the other?",
    key=_KEY, verify=_KEY,
    wrong=[_CAUSAL, _IRREL, _RESTATE],
    expl="The link runs the other way from the one it appears to. The theft comes first "
         "and the hiring follows it, so the staff are a response rather than a cause.",
    difficulty="hard", confidence=0.90),

# ===================================================== necessary vs sufficient (2)

_N1 = Scenario(["swam", "wristband"], rules=[IFo("swam", "wristband")],
               given=[NOTo("wristband")])
_n1 = _N1.pick([("Ravi did not swim", _N1.here(NOTo("swam"))),
                ("Ravi swam", _N1.here(ISo("swam"))),
                ("Everyone with a wristband swam", _N1.always(IFo("wristband", "swam"))),
                ("Nothing follows about whether Ravi swam", NOTHING)])
B.Q("necessary_vs_sufficient",
    "Nobody may swim in the lagoon without a wristband. Ravi had no wristband. Which one "
    "of these must be true?",
    key=_n1, verify="Ravi did not swim",
    wrong=["Ravi swam", "Everyone with a wristband swam",
           "Nothing follows about whether Ravi swam"],
    expl="A wristband is required before anyone swims, and Ravi had none, so Ravi did not "
         "swim. A wristband would not have made him swim either — it only permits it.",
    difficulty="medium", confidence=0.92),

_N2 = Scenario(["fullmarks", "certificate"], rules=[IFo("fullmarks", "certificate")],
               given=[ISo("certificate")])
_n2 = _N2.pick([("Nothing follows about whether Tess got full marks", NOTHING),
                ("Tess got full marks", _N2.here(ISo("fullmarks"))),
                ("Tess did not get full marks", _N2.here(NOTo("fullmarks"))),
                ("Only those with full marks receive a certificate",
                 _N2.always(IFo("certificate", "fullmarks")))])
B.Q("necessary_vs_sufficient",
    "Getting full marks is enough on its own to earn a certificate. Tess received a "
    "certificate. Which one of these must be true?",
    key=_n2, verify="Nothing follows about whether Tess got full marks",
    wrong=["Tess got full marks", "Tess did not get full marks",
           "Only those with full marks receive a certificate"],
    expl="Full marks would earn a certificate, but the rule never says that is the only "
         "way. Tess may have earned hers for effort or for improvement.",
    difficulty="hard", confidence=0.90),

B.write()
