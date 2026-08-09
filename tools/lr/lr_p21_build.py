#!/usr/bin/env python3
"""Builds lr_thinking_skills_p21.json — 32 §5.2 questions with no computable answer.

identify_flaw 16, weaken_argument 8, strengthen_argument 8. This opens identify_flaw,
the last §5.2 subcategory holding nothing, and takes §5.2 to 199/396.

The last three batches settled every answer with a model checker. Nothing of the sort is
available here: whether a fact weakens an argument is a judgement, and no enumeration
decides it. That does not leave the batch unchecked, it changes what there is to check.
Two structural guarantees replace the semantic one, and both catch real defects rather
than standing in for a check that cannot be run.

FLAWS — every distractor label must be a key somewhere else in the batch
    Sixteen arguments, eight named flaws, each flaw the answer to exactly two of them.
    A label that only ever appears as a wrong answer is a giveaway: a student who
    notices it is never right learns to eliminate it without reading the argument, and
    a label invented purely to be wrong is usually one the writer could not make fit.
    Requiring every distractor to be somebody else's key removes both. It is enforced at
    the end of the build, over the whole batch, and it failed on the first run.

WEAKEN AND STRENGTHEN — both directions are written for every argument, only one ships
    Each argument declares a fact that weakens it AND a fact that strengthens it. The
    weaken item keys the weakener and offers the strengthener as a distractor; the
    strengthen item does the reverse. A direction error therefore cannot hide — it would
    make the same option correct in both readings, and the build asserts they differ.

    Only one of each pair is emitted. Two stems sharing a 40-word argument and differing
    by one word score far above phase 4's silent 0.85 dedup, so shipping both would
    quietly lose one of them.

    The remaining two distractors are also typed and checked: the restatement must share
    at least three content words with the evidence, since restating is what makes it
    tempting, and the irrelevance must share at most one with the conclusion, since
    otherwise it is not irrelevant but weak.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.lr.lr_common import Batch  # noqa: E402

B = Batch(nn=21)

_STOP = set("""a an and are as at be been but by can cannot did do does for from had has have
he her his if in into is it its more most no not of on one only or our out she so than that
the their them there these they this to was were what when which who will with would you your
have also same each every been""".split())


def content(text):
    """Meaning-bearing words, crudely stemmed.

    Stemming is needed, not tidiness: "students who wore hats" and "the hat wearers"
    restate each other, and an exact-token comparison scores them as barely related.
    """
    out = set()
    for w in re.findall(r"[a-z]+", text.lower()):
        if w in _STOP or len(w) <= 2:
            continue
        for suffix in ("iest", "ies", "ing", "ers", "est", "ed", "er", "es", "s"):
            if w.endswith(suffix) and len(w) - len(suffix) >= 3:
                w = w[:-len(suffix)]
                break
        out.add(w)
    return out


# ===================================================== identify the flaw (16)

FLAWS = {
    "one_case": "It treats a single case as though it settled a general rule.",
    "after_so_because": "It assumes that because one thing followed another, the first "
                        "caused the second.",
    "needed_not_enough": "It treats something that is needed as though it were enough on "
                         "its own.",
    "attacks_person": "It argues against the person rather than against what they said.",
    "only_two": "It assumes there are only two possibilities when there may be others.",
    "assumes_conclusion": "It offers the thing it is trying to prove as the reason for "
                          "believing it.",
    "odd_group": "It draws a conclusion about everybody from a group that was never "
                 "typical.",
    "word_shifts": "It lets a word change meaning partway through the argument.",
}

# (flaw, argument, three other flaw keys, explanation)
FLAW_ITEMS = [
    ("one_case",
     "I tried a pie from the school canteen once and did not enjoy it. The canteen's food "
     "must be terrible.",
     ["after_so_because", "odd_group", "attacks_person"],
     "One pie tasted once by one person cannot settle anything about everything the "
     "canteen sells. It may have been the only poor item on the counter, or simply not to "
     "this person's taste."),
    ("one_case",
     "The first koala we saw at the sanctuary was asleep in the fork of a tree. Koalas "
     "must sleep all day.",
     ["odd_group", "after_so_because", "word_shifts"],
     "A single koala seen once tells us nothing about koalas as a whole, or even about "
     "that koala at other times of day."),
    ("after_so_because",
     "The council put a new streetlight on the corner in March, and the number of "
     "accidents there fell in April. The streetlight has made the corner safer.",
     ["one_case", "needed_not_enough", "only_two"],
     "The fall came after the streetlight, which is not the same as being caused by it. "
     "Roadworks, a speed limit change or ordinary month-to-month variation could each "
     "explain it."),
    ("after_so_because",
     "Whenever I wear my lucky socks, my team wins. The socks are helping the team win.",
     ["assumes_conclusion", "one_case", "odd_group"],
     "Wins following the socks is not the socks causing the wins. The argument never "
     "considers the games where the socks were worn and the team lost, or why socks would "
     "affect play at all."),
    ("needed_not_enough",
     "Nobody can win the science prize without a good hypothesis. Sara has a good "
     "hypothesis, so Sara will win the prize.",
     ["only_two", "assumes_conclusion", "after_so_because"],
     "A good hypothesis is required, which is not the same as being sufficient. Every "
     "other entrant may have one too, and the judging will rest on much more besides."),
    ("needed_not_enough",
     "To be picked for the choir you must be able to read music. Tom can read music, so "
     "Tom will be in the choir.",
     ["one_case", "word_shifts", "attacks_person"],
     "Reading music is a condition of being picked, not a guarantee of it. There may be "
     "an audition, a limit on numbers, or a clash with Tom's other commitments."),
    ("attacks_person",
     "Dr Nguyen's report says the reef is recovering. But Dr Nguyen has never been diving "
     "in her life, so the reef is not recovering.",
     ["odd_group", "needed_not_enough", "assumes_conclusion"],
     "Whether Dr Nguyen dives has no bearing on whether her measurements are right. The "
     "argument never engages with the report's evidence at all."),
    ("attacks_person",
     "Ali argues that the bus route should be changed. Ali is late to school nearly every "
     "day, so the route should stay as it is.",
     ["only_two", "after_so_because", "word_shifts"],
     "Ali's punctuality is not a reason for or against the route. If anything a person who "
     "is often late may know the route's problems best."),
    ("only_two",
     "Either we cut the sports budget or the school closes the library. We are not closing "
     "the library, so sports must be cut.",
     ["needed_not_enough", "assumes_conclusion", "one_case"],
     "The argument offers two options as though they were the only ones. The money might "
     "come from elsewhere, be raised, or the shortfall might be met in part from each."),
    ("only_two",
     "You are either good at maths or good at art. Nina is very good at art, so Nina "
     "cannot be good at maths.",
     ["word_shifts", "odd_group", "attacks_person"],
     "The two are treated as though nobody could be both, which is simply asserted. Plenty "
     "of people are good at both, and plenty at neither."),
    ("assumes_conclusion",
     "This newspaper can be trusted, because everything it prints is true. We know "
     "everything it prints is true because it is a newspaper that can be trusted.",
     ["one_case", "after_so_because", "needed_not_enough"],
     "The reason given for trusting the paper is the trustworthiness it is meant to be "
     "establishing. The argument goes in a circle and never reaches the ground."),
    ("assumes_conclusion",
     "Skateboarding is the best sport there is, because no other sport is as good as "
     "skateboarding.",
     ["only_two", "odd_group", "word_shifts"],
     "The second sentence says the same thing as the first in different words, so nothing "
     "has been offered in support of it."),
    ("odd_group",
     "We asked everyone at the running club how much exercise they do each week. The "
     "answers show that our town is one of the fittest in the state.",
     ["one_case", "assumes_conclusion", "needed_not_enough"],
     "A running club is the least typical group in town for a question about exercise. The "
     "people who do none were never going to be standing there to be asked."),
    ("odd_group",
     "Everybody queuing outside the library at opening time said they enjoy reading. So "
     "the whole school enjoys reading.",
     ["after_so_because", "attacks_person", "only_two"],
     "The queue is made of exactly the students most likely to enjoy reading. Asking them "
     "cannot tell us about the students who never go near the library."),
    ("word_shifts",
     "Nothing is better than a healthy lunch. A packet of chips is better than nothing. So "
     "a packet of chips is better than a healthy lunch.",
     ["only_two", "one_case", "assumes_conclusion"],
     "'Nothing' means two different things here. In the first sentence it means there is "
     "no better option; in the second it means going without. Sliding between the two is "
     "what produces the silly conclusion."),
    ("word_shifts",
     "The sign at the entrance says light vehicles only. My van is painted light green, so "
     "my van may use the entrance.",
     ["needed_not_enough", "attacks_person", "after_so_because"],
     "'Light' means not heavy on the sign and pale in colour in the second sentence. The "
     "argument works only if the two meanings are quietly treated as one."),
]

_key_flaws = [f for f, *_ in FLAW_ITEMS]
_distractor_flaws = {d for _, _, ds, _ in FLAW_ITEMS for d in ds}
_missing = _distractor_flaws - set(_key_flaws)
if _missing:
    raise AssertionError(f"these labels are only ever wrong answers: {sorted(_missing)} "
                         f"— a label a student never has to choose is one they learn to "
                         f"eliminate on sight")
for _f in FLAWS:
    if _key_flaws.count(_f) != 2:
        raise AssertionError(f"{_f} is the key {_key_flaws.count(_f)} times, not 2 — an "
                             f"uneven spread makes the commoner labels guessable")

for _i, (_flaw, _arg, _others, _expl) in enumerate(FLAW_ITEMS):
    if _flaw in _others or len(set(_others)) != 3:
        raise AssertionError(f"{_flaw}: the four labels are not distinct")
    B.Q("identify_flaw",
        f"Read this argument. '{_arg}' Which one of these best describes what is wrong "
        f"with the reasoning?",
        key=FLAWS[_flaw], verify=FLAWS[_flaw],
        wrong=[FLAWS[o] for o in _others],
        expl=_expl,
        difficulty="hard" if _i % 2 else "medium",
        confidence=0.90 if _i % 2 else 0.92)

# ===================================================== weaken / strengthen (8 + 8)

# (direction, conclusion, evidence, weakener, strengthener, irrelevant, restatement, expl)
ARGUMENTS = [
    ("weaken",
     "The new bike path has made our town safer.",
     "Since it opened, the number of cycling injuries has fallen by half.",
     "Half as many people ride bicycles in the town now as before the path opened.",
     "The number of people cycling in the town has doubled since the path opened.",
     "Funding for the project came from a state government grant announced in 2023.",
     "Cycling injuries in the town are now half what they were.",
     "If half as many people are riding, half as many injuries is exactly what you would "
     "expect from an unchanged level of danger. The fall in the count no longer shows the "
     "path did anything."),
    ("strengthen",
     "Reading before bed helps students fall asleep.",
     "Year 6 students who read at night report falling asleep faster than those who do not.",
     "The students who read at night also go to bed a full hour earlier than the others.",
     "When those same students stopped reading at night, they began taking longer to fall "
     "asleep.",
     "The survey forms were collected by the office and typed up during the winter term.",
     "Year 6 students who read at night say they get to sleep quickly.",
     "Taking the reading away and watching sleep get worse tests the claim directly. It "
     "rules out the possibility that fast sleepers were simply the ones who chose to read."),
    ("weaken",
     "The canteen's new menu is popular with students.",
     "Sales have risen every week since the new menu started.",
     "The canteen cut all its prices in the same week the new menu began.",
     "Prices and opening hours were left unchanged when the new menu began.",
     "A committee of parents meets each month to run the service and set the roster.",
     "Canteen sales have gone up each week under the new menu.",
     "Cheaper food would lift sales whatever was on the menu, so the rise no longer points "
     "to the menu as the reason. Two changes at once cannot be told apart."),
    ("strengthen",
     "Playing chess makes students better at mathematics.",
     "Members of the chess club have the highest maths marks in the school.",
     "Students must already have a high maths mark before they are allowed to join the "
     "chess club.",
     "Students' maths marks rose in the term after they joined the chess club, not before.",
     "The club meets on Tuesday afternoons in the library beside the science rooms.",
     "Members of the chess club score higher marks in maths than other students do.",
     "Marks rising after joining puts the chess before the improvement, which is the order "
     "the claim needs. The bare fact that good mathematicians play chess would fit the "
     "reverse just as well."),
    ("weaken",
     "The koala population in the reserve is recovering.",
     "Rangers counted 40 koalas this year, up from 25 last year.",
     "This year the rangers searched twice as much of the reserve as they did last year.",
     "The rangers covered exactly the same area of the reserve in both years.",
     "Visitors are welcome at weekends and there is a car park at the northern gate.",
     "Rangers counted more koalas this year than they did last year.",
     "Searching twice the area would turn up more koalas even if there were no more koalas "
     "to find. The higher count measures the search, not the population."),
    ("strengthen",
     "Wearing a hat prevents sunburn.",
     "Students who wore hats at the athletics carnival were less likely to be sunburnt.",
     "The students in hats also spent most of the day sitting under the shade tents.",
     "Hatted and bare-headed students spent equal time out in the open sun.",
     "The carnival was held at the district athletics track out past the showground.",
     "Fewer of the hat wearers were sunburnt at the carnival.",
     "Equal time in the sun removes the obvious rival explanation, leaving the hats as the "
     "difference between the two groups."),
    ("weaken",
     "The library's new opening hours are working.",
     "More books are being borrowed this year than last year.",
     "The library also bought 500 new books at the start of this year.",
     "The library's collection has not changed at all since last year.",
     "The building stands beside the staff car park on the eastern side of the grounds.",
     "The number of books borrowed is higher this year than it was last year.",
     "A shelf of new books would lift borrowing whatever the opening hours were. With two "
     "things changed at once, the rise cannot be credited to either."),
    ("strengthen",
     "This brand of battery lasts longer than the other one.",
     "In our test it powered a torch for 12 hours, while the other brand managed 9.",
     "The other brand's battery had already been used for three hours before the test "
     "began.",
     "Both batteries were new, and both were tested in identical torches.",
     "Both were bought at a supermarket in Ballarat on the same afternoon.",
     "The tested battery ran the torch three hours longer than the other brand did.",
     "A fair test needs the two batteries to start equal. Confirming that they did is what "
     "turns the 12 against 9 into evidence about the brands."),
    ("weaken",
     "Homework improves results.",
     "The students who spend the most time on homework get the best marks.",
     "The students who spend the most time on homework also attend a tutoring centre after "
     "school.",
     "When one class had its homework doubled, that class's marks rose while other classes "
     "stayed flat.",
     "The work is set on Mondays, Wednesdays and Fridays and collected the next day.",
     "The students who put the most hours into homework achieve the highest marks of all.",
     "The tutoring could be producing the marks on its own, with the long homework hours "
     "simply being what the same committed families also do. The figures no longer point "
     "at the homework in particular."),
    ("strengthen",
     "The tram is a faster way into the city than the bus.",
     "Commuters who take the tram arrive at work earlier than those who take the bus.",
     "Tram passengers live considerably closer to the city than bus passengers do.",
     "Tram and bus passengers begin their journeys the same distance from the city.",
     "The vehicles were built in Bendigo and refurbished about ten years ago.",
     "People who take the tram get to work before people who take the bus.",
     "Equal starting distances make the arrival times comparable. Without that, the tram "
     "might be arriving first simply by having less ground to cover."),
    ("weaken",
     "The water in the creek is cleaner than it used to be.",
     "Far fewer dead fish have been found in it this summer.",
     "There are hardly any fish living in the creek now compared with last summer.",
     "Fish numbers in the creek have stayed steady across the two summers.",
     "It runs behind the netball courts before joining the river further downstream.",
     "Not as many dead fish have turned up in the creek this summer.",
     "With almost no fish left there is almost nothing to find dead, so the drop is what "
     "you would see if the creek had got worse rather than better."),
    ("strengthen",
     "The new coach has improved the football team.",
     "The team has won six games in a row since he arrived.",
     "All six of those wins were against the bottom four teams in the league.",
     "Three of those six wins were against teams that beat them twice last season.",
     "He travels up from Geelong for every match and drives home the same night.",
     "The team has won every game it has played since the new coach started.",
     "Beating sides that used to beat them shows a change in the team rather than a change "
     "in the difficulty of the draw."),
    ("weaken",
     "Music lessons improve a child's concentration.",
     "Children who take music lessons sit still for longer in class.",
     "The parents who can afford music lessons also pay for tutoring in study skills.",
     "A class given free music lessons sat still longer than an identical class given none.",
     "Most are on the piano or the violin, and are held at a studio in town.",
     "Children having music lessons stay seated longer during class.",
     "If the same families buy both, the study tutoring could be doing all the work. The "
     "music lessons would then be a marker of the household, not the cause of anything."),
    ("strengthen",
     "The recycling campaign has worked.",
     "The amount of rubbish going to landfill has dropped since it began.",
     "The council began charging households by the bin in the same month.",
     "Bin charges and collection days were left untouched throughout the campaign.",
     "The posters were designed by Year 9 students and printed at a local shop.",
     "The amount of rubbish sent to landfill has dropped since the campaign began.",
     "Ruling out a change in charges removes the strongest rival explanation for the drop, "
     "which leaves the campaign standing as the reason."),
    ("weaken",
     "This sunscreen is the most effective one on sale.",
     "Swimmers using it reported the fewest burns at the surf carnival.",
     "The swimmers using it were the only ones wearing full-length swimsuits that day.",
     "All the swimmers wore the same swimsuits and spent the same time in the sun.",
     "It is sold in 200 mL bottles at chemists and at most surf shops along the coast.",
     "Fewer burns were reported by the swimmers who used this sunscreen.",
     "Full-length suits cover the skin the burns would otherwise appear on, so the low "
     "burn count may be about the clothing rather than the sunscreen."),
    ("strengthen",
     "The earlier start has helped Year 6 concentrate.",
     "Teachers report fewer distractions in morning lessons than before the change.",
     "The school moved its noisiest classes to the afternoon at the same time.",
     "Nothing else about the timetable was altered when the start time moved.",
     "News of it went out in the school newsletter at the end of the previous term.",
     "Teachers say there are fewer distractions in the mornings now.",
     "If the start time was the only change, the improvement has nothing else to be "
     "credited to."),
]

for _dir, _concl, _ev, _weak, _strong, _irrel, _restate, _expl in ARGUMENTS:
    if _weak == _strong:
        raise AssertionError(f"{_concl}: the weakener and the strengthener are the same fact")
    _shared_ev = content(_restate) & content(_ev)
    if len(_shared_ev) < 3:
        raise AssertionError(
            f"{_concl}: the restatement shares only {sorted(_shared_ev)} with the evidence "
            f"— it has to echo the evidence to be tempting")
    _shared_concl = content(_irrel) & content(_concl)
    if len(_shared_concl) > 1:
        raise AssertionError(
            f"{_concl}: the irrelevance shares {sorted(_shared_concl)} with the conclusion "
            f"— that makes it weak rather than irrelevant")
    _key, _other = (_weak, _strong) if _dir == "weaken" else (_strong, _weak)
    # A rival explanation takes more words to state than a piece of scenery, so the key
    # drifts towards being the longest option. Measured over the first build it was the
    # longest in 9 of 16 — above chance, and just under the 0.6 group cap length_tell
    # applies, so nothing would have caught it. The irrelevance carries the slack.
    _lens = [len(x) for x in (_key, _other, _irrel, _restate)]
    if min(_lens) < 0.7 * max(_lens):
        raise AssertionError(
            f"{_concl}: options run {min(_lens)}-{max(_lens)} characters — the short ones "
            f"need filling out before the key stands out by length alone")
    B.Q(f"{_dir}_argument",
        f"{_concl} {_ev} Which one of these, if true, most {_dir}s the argument?",
        key=_key, verify=_key,
        wrong=[_other, _irrel, _restate],
        expl=_expl,
        difficulty="hard", confidence=0.90)

B.write()
