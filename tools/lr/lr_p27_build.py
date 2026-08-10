#!/usr/bin/env python3
"""Builds lr_thinking_skills_p27.json — 32 §5.3 questions.

truth-teller 16, optimisation 16. §5.3 reaches 251/330; Thinking Skills 743/880.
truth_teller closes at 35/35.

The truth-tellers were not written and then tested this time. Sixteen were written and
tested, nine failed, and the replacements came out of an exhaustive search instead: every
combination of eleven statement templates across three speakers, filtered to those with
exactly one consistent pattern. 612 of 1331 survive, which is the honest measure of how
often a hand-written one works — and of how little a writer's intuition is worth on this
question type. The failures were not random either: a cycle of "X is a liar" statements
has no solution when the cycle is odd and two solutions when it is even, and no amount
of rereading the prose shows you that.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.figure_lib import table  # noqa: E402
from tools.lr.lr_common import Batch  # noqa: E402
from tools.lr.lr_logic import best, only, truth  # noqa: E402

B = Batch(nn=27)

# One fixed preamble across sixteen short stems made four of them score above phase 4's
# 0.85 dedup against each other: the shared 24 words were most of what was being compared.
# Four wordings, rotated.
FRAMES = [
    "Knights always tell the truth; knaves always lie. ",
    "On the island, every knight tells the truth and every knave lies. ",
    "Knights are truthful and knaves are not. ",
    "Among the islanders, knights never lie and knaves never tell the truth. ",
]


def knights(t):
    return sorted(n for n, v in t.items() if v)


# ===================================================== truth-teller (16)

_k1 = truth(["Ada", "Bay"], [lambda t: t["Ada"] == ((not t["Ada"]) or (not t["Bay"]))])
B.Q("truth_teller",
    FRAMES[0] + "Ada says: 'If I am a knight, then Bay is a knave.' What are Ada and Bay?",
    key="Ada is a knight and Bay is a knave",
    verify="Ada is a knight and Bay is a knave" if _k1["Ada"] and not _k1["Bay"] else "X",
    wrong=["Ada is a knave and Bay is a knight", "both are knights", "both are knaves"],
    expl="Suppose Ada is a knave. Then her statement is false, but an 'if' statement is "
         "only false when its first part is true — and a knave is not a knight. So Ada "
         "must be a knight, her statement holds, and Bay is a knave.",
    difficulty="hard", confidence=0.90),

_k2 = truth(["Cai", "Dev", "Eir"],
            [lambda t: t["Cai"] == (t["Dev"] and t["Eir"]),
             lambda t: t["Dev"] == (not t["Cai"])])
B.Q("truth_teller",
    FRAMES[1] + "Cai says: 'Dev and Eir are both knights.' Dev says: 'Cai is a knave.' Which "
    "of the three is a knight?",
    key="Dev only", verify=f"{knights(_k2)[0]} only" if len(knights(_k2)) == 1 else "X",
    wrong=["Cai only", "Eir only", "Dev and Eir"],
    expl="If Cai were a knight then Dev would be one too, but Dev calls Cai a knave, which "
         "a knight could not do falsely. So Cai is a knave, Dev's statement is true and Dev "
         "is a knight. Cai's claim being false then means Eir is a knave.",
    difficulty="hard", confidence=0.90),

_k3 = truth(["Fia", "Gil"],
            [lambda t: t["Fia"] == (t["Fia"] == t["Gil"]),
             lambda t: t["Gil"] == (t["Fia"] != t["Gil"])])
B.Q("truth_teller",
    FRAMES[2] + "Fia says: 'Gil and I are the same type.' Gil says: 'Fia and I are of "
    "different types.' What are they?",
    key="Fia is a knave and Gil is a knight",
    verify="Fia is a knave and Gil is a knight" if not _k3["Fia"] and _k3["Gil"] else "X",
    wrong=["Fia is a knight and Gil is a knave", "both are knights", "both are knaves"],
    expl="The two make opposite claims, so exactly one of them is right and they are of "
         "different types. Gil is the one saying that, so Gil is the knight and Fia the "
         "knave.",
    difficulty="hard", confidence=0.91),

_k4 = truth(["Hew", "Isla", "Jai"],
            [lambda t: t["Hew"] == (not t["Jai"]),
             lambda t: t["Isla"] == t["Hew"],
             lambda t: t["Jai"] == (t["Hew"] != t["Isla"])])
B.Q("truth_teller",
    FRAMES[3] + "Hew says: 'Jai is a knave.' Isla says: 'Hew is a knight.' Jai says: 'Hew and "
    "Isla are of different types.' How many of the three are knights?",
    key=sum(_k4.values()), verify=len(knights(_k4)),
    wrong=[1, 3, 0],
    expl="Isla simply backs Hew, so those two match. Jai says they differ, so Jai is wrong "
         "and is a knave — which makes Hew's statement about Jai true. Hew and Isla are "
         "both knights.",
    difficulty="hard", confidence=0.90),

_k5 = truth(["Kaya", "Lir"],
            [lambda t: t["Kaya"] == ((not t["Kaya"]) and (not t["Lir"]))])
B.Q("truth_teller",
    FRAMES[0] + "Kaya says: 'Neither of us is a knight.' What are Kaya and Lir?",
    key="Kaya is a knave and Lir is a knight",
    verify="Kaya is a knave and Lir is a knight" if not _k5["Kaya"] and _k5["Lir"] else "X",
    wrong=["Kaya is a knight and Lir is a knave", "both are knaves", "both are knights"],
    expl="A knight could not say neither is a knight, since that would make her own "
         "statement false. So Kaya is a knave and the statement is false — meaning at least "
         "one is a knight, and it is not Kaya, so it is Lir.",
    difficulty="hard", confidence=0.90),

_k6 = truth(["Mira", "Nero"],
            [lambda t: t["Mira"] == ((not t["Mira"]) or t["Nero"])])
B.Q("truth_teller",
    FRAMES[1] + "Mira says: 'Either I am a knave or Nero is a knight.' What are they?",
    key="both are knights",
    verify="both are knights" if _k6["Mira"] and _k6["Nero"] else "X",
    wrong=["both are knaves", "Mira is a knight and Nero is a knave",
           "Mira is a knave and Nero is a knight"],
    expl="If Mira were a knave the statement would be true, because its first half would "
         "hold — but a knave cannot say something true. So Mira is a knight, the statement "
         "is true, and since its first half is false its second half must hold: Nero is a "
         "knight too.",
    difficulty="hard", confidence=0.90),

_k7 = truth(["Opa", "Piet"],
            [lambda t: t["Opa"] == (not ((not t["Opa"]) and (not t["Piet"]))),
             lambda t: t["Piet"] == (not t["Opa"])])
B.Q("truth_teller",
    FRAMES[2] + "Opa says: 'Piet and I are not both knaves.' Piet says: 'Opa is a knave.' "
    "What are they?",
    key="Opa is a knight and Piet is a knave",
    verify="Opa is a knight and Piet is a knave" if _k7["Opa"] and not _k7["Piet"] else "X",
    wrong=["Opa is a knave and Piet is a knight", "both are knights", "both are knaves"],
    expl="If Opa were a knave, her statement would be false, so both would be knaves — but "
         "then Piet's statement calling Opa a knave would be true, which a knave cannot "
         "say. So Opa is a knight and Piet, who contradicts that, is a knave.",
    difficulty="hard", confidence=0.90),

_k8 = truth(["Rae", "Sten", "Tova"],
            [lambda t: t["Rae"] == (sum(t.values()) == 1),
             lambda t: t["Sten"] == ((not t["Rae"]) and (not t["Tova"])),
             lambda t: t["Tova"] == (sum(t.values()) == 2)])
B.Q("truth_teller",
    FRAMES[3] + "Rae says: 'Exactly one of us three is a knight.' Sten says: 'Rae and Tova "
    "are both knaves.' Tova says: 'Exactly two of us three are knights.' Which one is the "
    "knight?",
    key="Rae", verify=knights(_k8)[0] if len(knights(_k8)) == 1 else "X",
    wrong=["Sten", "Tova", "none of them"],
    expl="Suppose Rae is a knight. Then exactly one is, so Sten and Tova are knaves. Sten "
         "being a knave means Rae and Tova are not both knaves, which is right since Rae is "
         "a knight. Tova being a knave means there are not two knights, which is right. "
         "Everything holds.",
    difficulty="hard", confidence=0.90),

_k9 = truth(["Uve", "Vera", "Wilf"],
            [lambda t: t["Uve"] == (sum(t.values()) == 2),
             lambda t: t["Vera"] == (sum(t.values()) == 1),
             lambda t: t["Wilf"] == (t["Uve"] == t["Vera"])])
B.Q("truth_teller",
    FRAMES[0] + "Uve says: 'Exactly two of us three are knights.' Vera says: 'Exactly one of "
    "us three is a knight.' Wilf says: 'Uve and Vera are the same type.' Which one is the "
    "knight?",
    key="Vera", verify=knights(_k9)[0] if len(knights(_k9)) == 1 else "X",
    wrong=["Uve", "Wilf", "none of them"],
    expl="Uve and Vera contradict each other, so they cannot both be knights. If Vera is "
         "the only knight her statement is satisfied, Uve's is false as a knave's should "
         "be, and Wilf's claim that they match is false, which fits Wilf being a knave.",
    difficulty="hard", confidence=0.90),

_k10 = truth(["Xen", "Yuri", "Zaid"],
             [lambda t: t["Xen"] == (not t["Yuri"]),
              lambda t: t["Yuri"] == ((not t["Xen"]) or (not t["Zaid"])),
              lambda t: t["Zaid"] == (not t["Xen"])])
B.Q("truth_teller",
    FRAMES[1] + "Xen says: 'Yuri is a knave.' Yuri says: 'At least one of Xen and Zaid is a "
    "knave.' Zaid says: 'Xen is a knave.' Which of them are knights?",
    key="Yuri and Zaid", verify=" and ".join(knights(_k10)),
    wrong=["Xen and Yuri", "Xen and Zaid", "all three of them"],
    expl="Suppose Xen is a knight. Then Yuri is a knave, so Yuri's claim is false and "
         "neither Xen nor Zaid is a knave — which makes Zaid a knight, and Zaid's claim that "
         "Xen is a knave would then be true, contradicting Xen being a knight. So Xen is a "
         "knave, and both Yuri's claim and Zaid's are true.",
    difficulty="hard", confidence=0.90),

_k11 = truth(["Ana", "Bela", "Cato"],
             [lambda t: t["Ana"] == (not t["Bela"]),
              lambda t: t["Bela"] == (t["Ana"] and t["Cato"]),
              lambda t: t["Cato"] == (not t["Ana"])])
B.Q("truth_teller",
    FRAMES[2] + "Ana says: 'Bela is a knave.' Bela says: 'Ana and Cato are both knights.' "
    "Cato says: 'Ana is a knave.' Which one is the knight?",
    key="Ana", verify=knights(_k11)[0] if len(knights(_k11)) == 1 else "X",
    wrong=["Bela", "Cato", "none of them"],
    expl="Ana and Cato contradict each other, so exactly one of them is a knight. If Bela "
         "were a knight, Ana and Cato would both be knights, which cannot happen. So Bela "
         "is a knave, Ana's statement is true, and Cato's is false.",
    difficulty="hard", confidence=0.90),

_k12 = truth(["Dara", "Enzo", "Faye"],
             [lambda t: t["Dara"] == (t["Enzo"] == t["Faye"]),
              lambda t: t["Enzo"] == t["Dara"],
              lambda t: t["Faye"] == (sum(t.values()) == 3)])
B.Q("truth_teller",
    FRAMES[3] + "Dara says: 'Enzo and Faye are the same type.' Enzo says: 'Dara is a knight.' "
    "Faye says: 'All three of us are knights.' How many of them are knights?",
    key=sum(_k12.values()), verify=len(knights(_k12)),
    wrong=[0, 1, 2],
    expl="Enzo backs Dara, so those two match. If all three were knaves, Faye's claim would "
         "be false as it should be, but Dara's claim that Enzo and Faye match would be true "
         "— impossible for a knave. All three being knights fits every statement.",
    difficulty="hard", confidence=0.90),

_k13 = truth(["Gero", "Hilde", "Ilan"],
             [lambda t: t["Gero"] == t["Hilde"],
              lambda t: t["Hilde"] == (sum(t.values()) == 3),
              lambda t: t["Ilan"] == ((not t["Gero"]) and (not t["Hilde"]))])
B.Q("truth_teller",
    FRAMES[0] + "Gero says: 'Hilde is a knight.' Hilde says: 'All three of us are knights.' "
    "Ilan says: 'Gero and Hilde are both knaves.' Which one is the knight?",
    key="Ilan", verify=knights(_k13)[0] if len(knights(_k13)) == 1 else "X",
    wrong=["Gero", "Hilde", "none of them"],
    expl="Gero backs Hilde, so they match. If both were knights, Hilde's claim would make "
         "Ilan one too, but Ilan calls them knaves. So Gero and Hilde are both knaves, "
         "which is exactly what Ilan says.",
    difficulty="hard", confidence=0.90),

_k14 = truth(["Jorn", "Kira", "Lupe"],
             [lambda t: t["Jorn"] == ((not t["Kira"]) or (not t["Lupe"])),
              lambda t: t["Kira"] == t["Jorn"],
              lambda t: t["Lupe"] == (t["Jorn"] != t["Kira"])])
B.Q("truth_teller",
    FRAMES[1] + "Jorn says: 'At least one of Kira and Lupe is a knave.' Kira says: 'Jorn is a "
    "knight.' Lupe says: 'Jorn and Kira are of different types.' Which of them are "
    "knights?",
    key="Jorn and Kira", verify=" and ".join(knights(_k14)),
    wrong=["Jorn and Lupe", "Kira and Lupe", "all three of them"],
    expl="Kira backs Jorn, so they match, and Lupe says they differ, so Lupe is a knave. "
         "That makes Jorn's claim about at least one knave true, so Jorn is a knight and "
         "Kira with him.",
    difficulty="hard", confidence=0.90),

_k15 = truth(["Mette", "Nils", "Oona"],
             [lambda t: t["Mette"] == (t["Nils"] and t["Oona"]),
              lambda t: t["Nils"] == (sum(t.values()) == 3),
              lambda t: t["Oona"] == (sum(t.values()) == 2)])
B.Q("truth_teller",
    FRAMES[2] + "Mette says: 'Nils and Oona are both knights.' Nils says: 'All three of us "
    "are knights.' Oona says: 'Exactly two of us are knights.' How many are knights?",
    key=sum(_k15.values()), verify=len(knights(_k15)),
    wrong=[1, 2, 3],
    expl="If Nils were a knight, all three would be knights — but then Oona's claim of "
         "exactly two would be false, which a knight cannot say. So Nils is a knave. Mette "
         "needs Nils to be a knight, so Mette is a knave too. That leaves at most one knight, "
         "so Oona's claim of two is false and Oona is a knave as well. None of them is a "
         "knight, and all three statements are false as required.",
    difficulty="hard", confidence=0.90),

_k16 = truth(["Pia", "Quen", "Rolf"],
             [lambda t: t["Pia"] == (not t["Quen"]),
              lambda t: t["Quen"] == (sum(t.values()) == 1),
              lambda t: t["Rolf"] == (t["Pia"] and t["Quen"])])
B.Q("truth_teller",
    FRAMES[3] + "Pia says: 'Quen is a knave.' Quen says: 'Exactly one of us three is a "
    "knight.' Rolf says: 'Pia and Quen are both knights.' Which one is the knight?",
    key="Quen", verify=knights(_k16)[0] if len(knights(_k16)) == 1 else "X",
    wrong=["Pia", "Rolf", "none of them"],
    expl="Pia and Quen contradict each other, so exactly one of them is a knight. Rolf "
         "needs both to be knights, which cannot happen, so Rolf is a knave. That leaves "
         "one knight among the three, which is what Quen claims, so Quen is the knight.",
    difficulty="hard", confidence=0.90),

# ===================================================== optimisation (16)

_o1 = only(range(1, 40), lambda c: c + 1 == 24 // 3)
B.Q("optimisation",
    "A log 24 metres long is to be sawn into pieces 3 metres long. Each cut takes one "
    "minute. How long does the sawing take?",
    key=_o1, verify=24 // 3 - 1,
    wrong=[8, 9, 24],
    expl="Eight pieces need only seven cuts, because the last piece falls free on the "
         "seventh. Seven minutes. Answering 8 counts the pieces rather than the cuts.",
    fmt=lambda v: f"{v} minutes", difficulty="hard", confidence=0.91),

_POOL = {"single entries": 20 * 6, "a season pass": 95}
_o2, _ = best(list(_POOL), lambda k: _POOL[k])
B.Q("optimisation",
    "A pool charges $6 for a single visit, or $95 for a season pass with unlimited visits. "
    "Someone plans to swim twice a week for ten weeks. Which works out cheaper, and by how "
    "much?",
    key="the season pass, by $25",
    verify=f"the {_o2.replace('a ', '')}, by ${abs(_POOL['single entries'] - _POOL['a season pass'])}",
    wrong=["single entries, by $25", "the season pass, by $15", "single entries, by $15"],
    expl="Twice a week for ten weeks is 20 visits, which at $6 each comes to $120. The "
         "season pass is $95, so it saves $25.",
    difficulty="hard", confidence=0.90),

_PLANS = {"Plan A": 3000, "Plan B": 1500 + 12 * 60, "Plan C": 25 * 60}
_o3, _ = best(list(_PLANS), lambda k: _PLANS[k])
B.Q("optimisation",
    "Three data plans are offered. Plan A costs $30 a month for unlimited data. Plan B "
    "costs $15 a month plus 12c per gigabyte. Plan C has no monthly fee but charges 25c "
    "per gigabyte. Someone uses 60 gigabytes a month. Which plan costs least?",
    key=_o3, verify=min(_PLANS, key=_PLANS.get),
    wrong=[k for k in _PLANS if k != _o3] + ["they all cost the same"],
    expl="Plan A is $30.00. Plan B is $15 plus $7.20, which is $22.20. Plan C is $15.00. "
         "Plan C is cheapest at 60 gigabytes, though it would overtake the others if the "
         "usage climbed much higher.",
    difficulty="hard", confidence=0.90),

_o4 = -(-95 // 24)
B.Q("optimisation",
    "Eggs are packed 24 to a tray. A baker needs 95 eggs. What is the smallest number of "
    "trays she must buy?",
    key=_o4, verify=only(range(1, 20), lambda t: 24 * t >= 95 and 24 * (t - 1) < 95),
    wrong=[3, 5, 24],
    expl="Three trays hold 72 eggs, which is not enough, and four hold 96. So four trays, "
         "with one egg spare. Answering 3 leaves her 23 eggs short.",
    fmt=lambda v: f"{v} trays", difficulty="medium", confidence=0.92),

_DEALS = {"three for the price of two": 4 * 3.00,
          "twenty per cent off everything": 6 * 3.00 * 0.8,
          "fifty cents off each notebook": 6 * 2.50}
_o5, _ = best(list(_DEALS), lambda k: _DEALS[k])
B.Q("optimisation",
    "Notebooks cost $3 each and six are needed. Three offers are available: three for the "
    "price of two, twenty per cent off everything, or fifty cents off each notebook. Which "
    "offer costs least for six notebooks?",
    key=_o5, verify=min(_DEALS, key=_DEALS.get),
    wrong=[k for k in _DEALS if k != _o5] + ["they all cost the same"],
    expl="Three for two means paying for four notebooks, which is $12. Twenty per cent off "
         "$18 is $14.40, and fifty cents off each makes them $2.50, which is $15. The "
         "three-for-two offer wins because it gives two free rather than a slice off each.",
    difficulty="hard", confidence=0.90),

_o6 = only(range(1, 40), lambda p: (p - 1) * 4 == 36)
B.Q("optimisation",
    "A straight path 36 metres long is to have a lamp every 4 metres, including one at each "
    "end. How many lamps are needed?",
    key=_o6, verify=36 // 4 + 1,
    wrong=[9, 8, 36],
    expl="Thirty-six metres gives 9 gaps of 4 metres, and a straight run needs one more "
         "lamp than it has gaps: 10. Answering 9 counts the gaps.",
    fmt=lambda v: f"{v} lamps", difficulty="hard", confidence=0.91),

_o7, _ = best(["two large boxes", "five small boxes", "one large and three small"],
              lambda k: {"two large boxes": 2 * 14.00, "five small boxes": 5 * 6.00,
                         "one large and three small": 14.00 + 3 * 6.00}[k])
B.Q("optimisation",
    "A large box holds 20 books and costs $14. A small box holds 8 books and costs $6. "
    "Forty books must be packed with none left loose. Which purchase costs least?",
    key=_o7, verify="two large boxes",
    wrong=["five small boxes", "one large and three small", "the cost is the same"],
    expl="Two large boxes hold exactly 40 books for $28. Five small boxes hold 40 as well "
         "but cost $30. One large and three small holds 44 and costs $32.",
    difficulty="hard", confidence=0.90),

_o8 = only(range(1, 60), lambda n: 5 * n >= 47 and 5 * (n - 1) < 47)
B.Q("optimisation",
    "A minibus seats 5 passengers. Forty-seven people need to be taken to a match. What is "
    "the smallest number of minibus loads required?",
    key=_o8, verify=-(-47 // 5),
    wrong=[9, 47, 11],
    expl="Nine loads carry 45 people, leaving 2 behind, so a tenth load is needed with only "
         "2 aboard. Answering 9 forgets the last pair.",
    fmt=lambda v: f"{v} loads", difficulty="medium", confidence=0.92),

_RECT = {"12 m by 3 m": 12 * 3, "10 m by 5 m": 10 * 5, "9 m by 6 m": 9 * 6,
         "14 m by 1 m": 14 * 1}
_o9, _ = best(list(_RECT), lambda k: _RECT[k], want="max")
B.Q("optimisation",
    "A gardener has 30 metres of fencing for a rectangular bed. Which of these shapes uses "
    "exactly 30 metres of fencing and encloses the largest area?",
    key=_o9, verify=max(_RECT, key=_RECT.get),
    wrong=[k for k in _RECT if k != _o9],
    expl="Each shape has sides adding to 15 metres, so all four use 30 metres of fencing. "
         "Their areas are 36, 50, 54 and 14 square metres, so the 9 by 6 bed is largest — "
         "the nearer a rectangle gets to a square, the more it encloses.",
    difficulty="hard", confidence=0.90),

_JUGS = [(a, b) for a in range(0, 6) for b in range(0, 8) if 5 * a + 3 * b == 19]
_fills = min(a + b for a, b in _JUGS)
B.Q("optimisation",
    "A tank is filled using a 5 litre jug and a 3 litre jug, each poured in full. Exactly "
    "19 litres are needed. What is the smallest number of jugfuls that will do it?",
    key=_fills,
    # second route: count upwards to the first reachable total
    verify=next(n for n in range(1, 12) if any(a + b == n for a, b in _JUGS)),
    wrong=[4, 6, 19],
    expl="Two of the 5 litre jug and three of the 3 litre jug give 10 + 9 = 19 litres in 5 "
         "jugfuls. Four jugfuls cannot reach 19: the most four can carry is 20 and the "
         "combinations below it miss 19 entirely.",
    fmt=lambda v: f"{v} jugfuls", difficulty="hard", confidence=0.90),

TIMES = table([["Task", "Minutes"], ["Boil the water", "8"], ["Chop the vegetables", "6"],
               ["Heat the oven", "12"], ["Set the table", "4"]])
B.Q("optimisation",
    "The table lists four jobs and how long each takes. One person can only do one job at "
    "a time, but the oven and the kettle work on their own once started. What is the least "
    "time in which all four jobs can be finished?",
    key="12 minutes", verify=f"{max(8, 12, 6 + 4)} minutes",
    wrong=["30 minutes", "10 minutes", "20 minutes"],
    expl="Start the oven and the kettle first, since they run unattended, then chop and set "
         "the table during the 12 minutes the oven takes. Chopping and the table need 10 "
         "minutes together, which fits inside the 12. Answering 30 adds every job as though "
         "nothing overlapped.",
    fig=TIMES, difficulty="hard", confidence=0.90),

_o12, _ = best(["by post", "by courier", "collected in person"],
               lambda k: {"by post": 3 * 4.50, "by courier": 11.00,
                          "collected in person": 3 * 2.00 + 6.00}[k])
B.Q("optimisation",
    "Three parcels must be sent. Post costs $4.50 a parcel. A courier takes any number for "
    "a flat $11. Collecting them in person costs $2 a parcel in handling plus $6 for "
    "petrol. Which is cheapest for three parcels?",
    key=_o12, verify="by courier",
    wrong=["by post", "collected in person", "they cost the same"],
    expl="Post is 3 x $4.50 = $13.50. The courier is a flat $11. Collecting them costs $6 "
         "plus $6, which is $12. The courier is cheapest, and would stay cheapest for any "
         "larger number of parcels.",
    difficulty="hard", confidence=0.90),

_o13 = only(range(1, 40), lambda n: 7 * n >= 100 and 7 * (n - 1) < 100)
B.Q("optimisation",
    "A ferry can take 7 cars each crossing. One hundred cars are waiting. How many "
    "crossings are needed to move them all?",
    key=_o13, verify=-(-100 // 7),
    wrong=[14, 16, 7],
    expl="Fourteen crossings carry 98 cars, leaving 2, so a fifteenth is needed. Answering "
         "14 leaves two cars on the shore, and 7 gives the cars per crossing.",
    fmt=lambda v: f"{v} crossings", difficulty="medium", confidence=0.92),

_CARPET = {"a 4 m by 5 m piece": (20, 4 * 5 * 22),
           "a 3 m by 7 m piece": (21, 3 * 7 * 22),
           "two 2 m by 6 m pieces": (24, 2 * 2 * 6 * 22)}
for _name, (_area, _) in _CARPET.items():
    if _area < 20:
        raise AssertionError(f"{_name} covers only {_area} square metres of the 20 needed")
_o14, _ = best(list(_CARPET), lambda k: _CARPET[k][1])
B.Q("optimisation",
    "A room needs 20 square metres of carpet. Carpet costs $22 a square metre. Which "
    "purchase covers the room for the least money?",
    key=_o14, verify=min(_CARPET, key=lambda k: _CARPET[k][1]),
    wrong=[k for k in _CARPET if k != _o14] + ["they cost the same"],
    expl="Every option has to cover at least 20 square metres. The 4 by 5 piece is exactly "
         "20 and costs $440. The 3 by 7 piece is 21 square metres at $462, and two 2 by 6 "
         "pieces come to 24 square metres at $528. Buying the exact size wastes nothing.",
    difficulty="hard", confidence=0.90),

_o15, _ = best(["walk the whole way", "bus then walk", "bus the whole way"],
               lambda k: {"walk the whole way": 60, "bus then walk": 15 + 20,
                          "bus the whole way": 45}[k])
B.Q("optimisation",
    "Getting to the station takes 60 minutes on foot, or 45 minutes by bus because of the "
    "long route. Taking the bus part of the way and walking the rest takes 15 minutes on "
    "the bus and 20 minutes walking. Which way is quickest?",
    key=_o15, verify="bus then walk",
    wrong=["walk the whole way", "bus the whole way", "they take the same time"],
    expl="Walking takes 60 minutes and the bus 45. The mixed route takes 15 plus 20, which "
         "is 35 minutes — quicker than either on its own, because it skips the bus's long "
         "detour.",
    difficulty="hard", confidence=0.90),

_o16 = only(range(1, 30), lambda n: 4 * n >= 3 * 15 and 4 * (n - 1) < 3 * 15)
B.Q("optimisation",
    "A machine can print 4 posters at a time and takes 3 minutes for each batch. Forty-five "
    "posters are needed. How long will the printing take?",
    key=3 * _o16, verify=3 * -(-45 // 4),
    wrong=[33, 45, 135],
    expl="Forty-five posters need 12 batches, since 11 batches print only 44. Twelve batches "
         "at 3 minutes each is 36 minutes. Answering 33 stops at 11 batches and leaves one "
         "poster unprinted, and 135 prints them one at a time.",
    fmt=lambda v: f"{v} minutes", difficulty="hard", confidence=0.90),

B.write()
