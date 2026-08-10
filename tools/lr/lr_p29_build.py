#!/usr/bin/env python3
"""Builds lr_thinking_skills_p29.json — 32 §5.2 questions.

identify_flaw 24, identify_assumption 8. §5.2 reaches 347/396; Thinking Skills 807/880.

p21's rule again, over a wider taxonomy: eight named flaws, each the answer to exactly
three of the twenty-four, and every distractor label required to be somebody else's key.
Four of the eight are p21's, deliberately — a student should meet the same named flaw
more than once — and four are new: an average read as applying to every case, an unproved
claim treated as disproved, a comparison between things that are not alike, and a
property of the parts assumed of the whole.
"""
import collections
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.lr.lr_common import Batch  # noqa: E402
from tools.lr.lr_prose import (  # noqa: E402
    must_balance, must_be_unrelated, must_not_restate, must_overreach, must_restate,
)

B = Batch(nn=29)

FLAWS = {
    "one_case": "It treats a single case as though it settled a general rule.",
    "after_so_because": "It assumes that because one thing followed another, the first "
                        "caused the second.",
    "needed_not_enough": "It treats something that is needed as though it were enough on "
                         "its own.",
    "only_two": "It assumes there are only two possibilities when there may be others.",
    "average_for_all": "It treats an average as though it held for every single case.",
    # first wording was "treats a claim as false simply because nobody has proved it",
    # which fits the platypus item and NEITHER of the other two — those treat an
    # undisproved claim as true. The label has to cover both directions of the mistake.
    "unproved_so_false": "It treats the absence of proof as though it settled the question.",
    "unlike_comparison": "It compares two things that are not alike enough to compare.",
    "parts_to_whole": "It assumes that what is true of each part is true of the whole.",
}

# (flaw, argument, three other flaw keys, explanation)
ITEMS = [
    ("one_case",
     "The one wombat I saw at the sanctuary was eating grass. Wombats must eat nothing but "
     "grass.",
     ["average_for_all", "after_so_because", "parts_to_whole"],
     "A single animal watched once cannot settle what a whole species eats, or even what "
     "that wombat eats at other times of day."),
    ("one_case",
     "The first train I caught on the new line was late. The new line cannot be relied on.",
     ["after_so_because", "unlike_comparison", "unproved_so_false"],
     "One late train says nothing about how the line runs in general. It may have been the "
     "only delay all month, or caused by something that will not happen again."),
    ("one_case",
     "My neighbour's solar panels did not lower her power bill. Solar panels do not save "
     "anyone money.",
     ["only_two", "average_for_all", "parts_to_whole"],
     "One household's bill cannot establish what happens to households generally. Her usage "
     "may have risen, or her roof may face the wrong way."),
    ("after_so_because",
     "The council planted trees along the main road in March, and shop takings rose in "
     "April. The trees have brought customers in.",
     ["one_case", "needed_not_enough", "unlike_comparison"],
     "The rise came after the planting, which is not the same as being caused by it. School "
     "holidays, a new bus stop or ordinary seasonal change could each explain it."),
    ("after_so_because",
     "Ever since the club changed its jersey, it has won every match. The new jersey is "
     "winning them games.",
     ["parts_to_whole", "unproved_so_false", "only_two"],
     "Wins following the jersey are not the jersey causing the wins. A new coach, an easier "
     "draw or a returning player would all fit the same run of results."),
    ("after_so_because",
     "The library started opening on Sundays, and borrowing went up that month. Sunday "
     "opening is what lifted borrowing.",
     ["needed_not_enough", "average_for_all", "one_case"],
     "One thing following another is not one thing causing another. A new delivery of books "
     "or the start of the school holidays would produce the same rise."),
    ("needed_not_enough",
     "You cannot become a pilot without good eyesight. Nadia has excellent eyesight, so "
     "Nadia will become a pilot.",
     ["only_two", "unproved_so_false", "after_so_because"],
     "Good eyesight is required, which is not the same as being sufficient. Training, "
     "examinations and a licence all stand between Nadia and the cockpit."),
    ("needed_not_enough",
     "No one can enter the exhibition without a ticket. Sam has a ticket, so Sam is inside "
     "the exhibition.",
     ["one_case", "unlike_comparison", "parts_to_whole"],
     "A ticket is a condition of entry, not a guarantee that it was used. Sam may be "
     "queueing, may have arrived late, or may not have gone at all."),
    ("needed_not_enough",
     "A cake will not rise without baking powder. This cake has baking powder in it, so it "
     "will rise.",
     ["average_for_all", "only_two", "after_so_because"],
     "Baking powder is one requirement among several. The oven temperature, the mixing and "
     "the freshness of the powder all have to be right as well."),
    ("only_two",
     "Either the school buys new laptops or the students fall behind. The school cannot "
     "afford laptops, so the students will fall behind.",
     ["needed_not_enough", "parts_to_whole", "unproved_so_false"],
     "Two options are offered as though they were the only ones. The school might repair "
     "the old machines, share them between classes, or borrow from the council."),
    ("only_two",
     "You either love the beach or you love the bush. Priya loves the bush, so she cannot "
     "love the beach.",
     ["unlike_comparison", "one_case", "average_for_all"],
     "The two are treated as though nobody could love both, which is simply asserted. Many "
     "people are fond of both, and some of neither."),
    ("only_two",
     "The team will either win the grand final or have a wasted season. They lost the "
     "grand final, so their season was wasted.",
     ["after_so_because", "unproved_so_false", "needed_not_enough"],
     "A season can be worth having without ending in a premiership. Setting up only two "
     "outcomes leaves out development, finals experience and everything in between."),
    ("average_for_all",
     "The average rainfall here is 600 millimetres a year. So this district gets 600 "
     "millimetres every year.",
     ["one_case", "parts_to_whole", "after_so_because"],
     "An average is what the years come to between them, not what any single year "
     "delivers. Dry years and wet years both sit behind that figure."),
    ("average_for_all",
     "Students at this school score above the state average in mathematics. So every "
     "student here is above the state average.",
     ["only_two", "unlike_comparison", "unproved_so_false"],
     "A group can sit above an average while many of its members sit below it. The average "
     "describes the school as a whole, not each student in it."),
    ("average_for_all",
     "The average family in this suburb has 1.8 children. So the family next door has 1.8 "
     "children.",
     ["needed_not_enough", "after_so_because", "one_case"],
     "No family has eight tenths of a child. The figure is what you get by dividing all the "
     "children among all the families, and it need not describe any of them."),
    ("unproved_so_false",
     "Nobody has ever proved that this creek carries platypus. So there are no platypus in "
     "the creek.",
     ["one_case", "unlike_comparison", "only_two"],
     "Not having found something is not the same as its not being there. Platypus are shy "
     "and nocturnal, and nobody may have looked at the right hour."),
    ("unproved_so_false",
     "No one has shown that the new drink causes any harm. So the new drink is completely "
     "safe.",
     ["parts_to_whole", "needed_not_enough", "average_for_all"],
     "An absence of evidence of harm is not evidence of safety. The drink may simply be too "
     "new for anyone to have tested it properly."),
    ("unproved_so_false",
     "There is no proof that this painting is a forgery, so it must be genuine.",
     ["after_so_because", "only_two", "one_case"],
     "Failing to prove a forgery leaves the question open rather than settling it. A clever "
     "forgery is exactly the kind that has not been proved."),
    ("unlike_comparison",
     "The tomatoes in the greenhouse grew twice as tall as those in the open bed. "
     "Greenhouse soil must be twice as rich.",
     ["one_case", "needed_not_enough", "unproved_so_false"],
     "The two beds differ in warmth, shelter and watering as well as in soil. Comparing "
     "them tells you nothing about the soil on its own."),
    ("unlike_comparison",
     "Our under-12 team scored more goals last season than the senior team did. Our under-"
     "12s must be the better side.",
     ["average_for_all", "parts_to_whole", "after_so_because"],
     "The two teams play different opponents in different competitions over a different "
     "number of matches. The goal counts are not measuring the same thing."),
    ("unlike_comparison",
     "A litre of petrol costs more than a litre of milk, so petrol is harder to produce "
     "than milk.",
     ["only_two", "one_case", "unproved_so_false"],
     "Price reflects tax, transport, refining and demand, and those differ completely "
     "between the two. The comparison cannot carry the conclusion."),
    ("parts_to_whole",
     "Every player in the squad is a fine footballer. So the squad must be a fine team.",
     ["after_so_because", "average_for_all", "needed_not_enough"],
     "A team is more than the players in it. Individually excellent players can combine "
     "badly, and a fine team often depends on how they fit together."),
    ("parts_to_whole",
     "Each brick in this wall is light enough to lift with one hand. So the wall can be "
     "lifted with one hand.",
     ["one_case", "only_two", "unlike_comparison"],
     "What holds for a single brick does not carry over to thousands of them together. The "
     "property being described does not survive being added up."),
    ("parts_to_whole",
     "Every ingredient in the dish is delicious on its own. So the dish must be delicious.",
     ["unproved_so_false", "after_so_because", "average_for_all"],
     "Ingredients that are good separately can be poor together. The quality of the dish "
     "depends on the combination, which the argument never considers."),
]

_keys = [f for f, *_ in ITEMS]
_missing = {d for _, _, ds, _ in ITEMS for d in ds} - set(_keys)
if _missing:
    raise AssertionError(f"only ever wrong answers: {sorted(_missing)} — a label a student "
                         f"never has to choose is one they learn to eliminate on sight")
for _f in FLAWS:
    if _keys.count(_f) != 3:
        raise AssertionError(f"{_f} is the key {_keys.count(_f)} times, not 3")

for _i, (_flaw, _arg, _others, _expl) in enumerate(ITEMS):
    if _flaw in _others or len(set(_others)) != 3:
        raise AssertionError(f"{_flaw}: the four labels are not distinct")
    B.Q("identify_flaw",
        f"Read this argument. '{_arg}' Which one of these best describes what is wrong "
        f"with the reasoning?",
        key=FLAWS[_flaw], verify=FLAWS[_flaw],
        wrong=[FLAWS[o] for o in _others],
        expl=_expl,
        difficulty="hard" if _i % 3 else "medium",
        confidence=0.90 if _i % 3 else 0.92)

# ===================================================== identify the assumption (8)

ASSUMPTIONS = [
    ("The new ferry will cut the crossing time from forty minutes to twenty.",
     "So commuters will get to work half an hour earlier.",
     "The saving on the crossing is not lost waiting for a later connecting service.",
     "Every commuter on the route will arrive exactly half an hour earlier.",
     "The new ferry will make the crossing in twenty minutes instead of forty.",
     "The vessel was built at a yard on the Tasmanian north coast.",
     "A faster crossing only reaches the office sooner if the rest of the journey holds "
     "still. If the earlier arrival means a longer wait for the bus, the saving "
     "disappears before anyone gets to work."),
    ("The canteen is replacing its fried snacks with fruit.",
     "So students at the school will eat more fruit.",
     "Students who bought the fried snacks will buy the fruit rather than bring their own "
     "food.",
     "Every student who used to buy snacks will now buy fruit instead.",
     "Fried snacks are being taken off the canteen menu and replaced with fruit.",
     "The counter was refitted during the last week of the summer holidays.",
     "Removing one option does not make anyone take another. If those students simply "
     "bring chips from home, the canteen will sell fruit to nobody new."),
    ("This bridge is rated to carry vehicles up to eight tonnes.",
     "So the loaded truck at eight tonnes can cross it safely.",
     "The rating leaves a margin for the way weight shifts as a vehicle moves.",
     "Every bridge is built to carry far more than the weight written on it.",
     "The bridge carries a rating for vehicles of up to eight tonnes.",
     "The approach was resurfaced over three days in the middle of winter.",
     "A rating describes a still, evenly spread load. A moving truck presses harder on the "
     "deck as it crosses, so a load right on the limit may not be safe at all."),
    ("Sales of the magazine have fallen every year since it went online.",
     "So the website is taking readers away from the printed edition.",
     "The people who stopped buying the magazine have not simply lost interest in the "
     "subject.",
     "Nobody at all reads the printed magazine and the website together.",
     "The magazine's sales have fallen each year since the website launched.",
     "The title has been printed on the same presses since the early 1990s.",
     "Readers who drifted away from the subject entirely would produce the same fall "
     "without ever opening the website. The argument needs them to have moved across."),
    ("The new lighting in the workshop is twice as bright as the old lighting.",
     "So workers will be able to see their work more clearly.",
     "The extra brightness does not produce glare that makes fine detail harder to see.",
     "Brighter light always makes any kind of work easier to see.",
     "The workshop's new lighting is twice as bright as the lighting it replaced.",
     "The fittings were ordered through a supplier in the western suburbs.",
     "More light is not always clearer light. Glare off a metal bench can hide detail that "
     "dimmer, softer lighting would have shown."),
    ("Every student in the class has been given a tablet computer.",
     "So every student can now do the online homework at home.",
     "The students all have somewhere at home where the tablet can connect to the "
     "internet.",
     "All students have exactly the same internet connection at home.",
     "A tablet computer has been given to every student in the class.",
     "The devices were delivered in three boxes at the start of the term.",
     "A tablet with nothing to connect to cannot open the homework. The argument assumes "
     "an internet connection it never mentions."),
    ("The council has widened the road from two lanes to four.",
     "So the morning traffic jam will clear more quickly.",
     "The wider road does not simply attract more drivers onto it than before.",
     "Every road that is widened carries its traffic more quickly.",
     "The road has been widened by the council from two lanes to four.",
     "The work was signed off at a meeting held late last November.",
     "Extra lanes can draw drivers who used to take another route or another hour. If the "
     "traffic grows to fill them, the jam is where it was."),
    ("The medicine cleared the infection in every patient in the trial.",
     "So the medicine will clear the infection in patients generally.",
     "The patients in the trial were not chosen in a way that made them easier to treat.",
     "Every patient who takes the medicine will be cured completely.",
     "In the trial, the medicine cleared the infection in every patient.",
     "The trial was written up in a journal published twice a year.",
     "A trial only speaks for patients generally if its patients resemble them. A group of "
     "young, otherwise healthy volunteers would recover from much on their own."),
]

for _i, (_ev, _concl, _assume, _strong, _restate, _irrel, _expl) in enumerate(ASSUMPTIONS):
    _label = _concl[:44]
    must_not_restate(_assume, _ev + " " + _concl, f"{_label} [assumption]")
    must_overreach(_strong, f"{_label} [over-strong]")
    must_restate(_restate, _ev, f"{_label} [restatement]")
    must_be_unrelated(_irrel, _concl, f"{_label} [irrelevance]")
    must_balance([_assume, _strong, _restate, _irrel], _label)
    B.Q("identify_assumption",
        f"{_ev} {_concl} Which one of these is an assumption the argument depends on?",
        key=_assume, verify=_assume,
        wrong=[_strong, _restate, _irrel],
        expl=_expl,
        difficulty="hard" if _i % 3 else "medium",
        confidence=0.90 if _i % 3 else 0.92)

B.write()
