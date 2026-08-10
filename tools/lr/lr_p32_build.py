#!/usr/bin/env python3
"""Builds lr_thinking_skills_p32.json — 32 §5.2 argument questions.

identify_assumption 17, identify_conclusion 15. Both close: identify_assumption at 55/55
and identify_conclusion at 40/40. §5.2 reaches 388/396; Thinking Skills 903/880 rows
across the book, with only §5.2's last two subcategories outstanding.

Same lr_prose discipline as p23 and p29. The assumption must be UNSTATED, which is
checked by sequence similarity against every sentence of the argument rather than by
shared vocabulary — an assumption about ferries has to say ferries, and a bag-of-words
test reads that as already said.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.lr.lr_common import Batch  # noqa: E402
from tools.lr.lr_prose import (  # noqa: E402
    must_balance, must_be_unrelated, must_not_restate, must_overreach, must_restate,
)

B = Batch(nn=32)

# (evidence, conclusion, assumption, over-strong, restatement, irrelevance, explanation)
ASSUMPTIONS = [
    ("The council is replacing the town's street bins with larger ones.",
     "So the streets will be tidier by the end of summer.",
     "The bins are being emptied often enough that the larger size will not simply "
     "overflow later.",
     "Every street that has a large bin on it stays completely clean all summer.",
     "Larger bins are replacing the town's street bins on the council's orders.",
     "The contract was awarded at a meeting held in the middle of March.",
     "A bigger bin only helps if it is emptied before it fills. If the collection round "
     "stays the same, the town simply gets larger piles of rubbish."),
    ("The new reading app tests every child's level before it sets any work.",
     "So each child will be given work at the right level.",
     "The test measures a child's reading level accurately enough to set work by.",
     "Every child tested by the app is placed perfectly every time.",
     "Before setting work, the app tests the reading level of every child.",
     "The app was written by a company with an office in Brisbane.",
     "Setting work by a test only works if the test is any good. A child having a bad "
     "morning could be placed a year below where they belong."),
    ("The bakery is opening a second shop on the other side of town.",
     "So the bakery's total sales will rise.",
     "The second shop will not simply take customers away from the first.",
     "Every business that opens a second shop increases what it sells.",
     "A second bakery shop is opening on the other side of town.",
     "The lease on the second site was signed for a term of five years.",
     "Two shops sharing one set of customers sell no more between them than one did. The "
     "argument needs the new shop to reach people the first never did."),
    ("Every classroom in the school now has a data projector.",
     "So teachers can show video to their classes whenever they wish.",
     "The rooms can be darkened enough for a projected image to be seen.",
     "All projectors work perfectly in any lighting whatsoever.",
     "A data projector has now been installed in every classroom in the school.",
     "The installation was carried out over two weeks in the holidays.",
     "A projector in a room full of sunlight shows very little. The conclusion assumes a "
     "condition about the rooms that nothing in the argument mentions."),
    ("The train service has been made half an hour faster between the two cities.",
     "So more people will travel by train rather than driving.",
     "Some drivers were choosing the car because of how long the train took.",
     "Every driver on that route will switch to the train.",
     "Between the two cities, the train service is now half an hour faster.",
     "The new timetable was printed on recycled card in two colours.",
     "A faster train wins nobody over unless the old speed was what put them off. Drivers "
     "who need a car at the far end will keep driving whatever the timetable says."),
    ("The museum has translated all its labels into four languages.",
     "So more overseas visitors will understand the exhibits.",
     "The four languages chosen are ones that a useful number of visitors read.",
     "All overseas visitors read at least one of the four languages.",
     "Every label in the museum has been translated into four languages.",
     "The translation work took eight months and was finished last spring.",
     "Four languages help only if visitors read them. Choosing four that almost nobody "
     "arriving at the door speaks would change nothing at all."),
    ("The club has bought lights so the oval can be used after dark.",
     "So the club will be able to train on winter evenings.",
     "The club is allowed to use the oval after dark under its ground agreement.",
     "Every sporting ground fitted with lights is available at any hour.",
     "Lights have been bought by the club so the oval can be used after dark.",
     "The purchase was funded from a raffle run over the summer.",
     "Lights do not grant permission. A curfew in the ground agreement or a council "
     "noise rule would leave the oval dark whatever is bolted to the posts."),
    ("The survey found that 80 per cent of the students who replied want a later start.",
     "So most students at the school want a later start.",
     "The students who replied are not unusually likely to favour a later start.",
     "Every single student at the school replied to the survey form.",
     "Of the students who replied to the survey, 80 per cent want a later start.",
     "The survey was distributed on paper in the second week of term.",
     "Those who reply to a survey are not always typical. The students who most want a "
     "later start are exactly the ones most likely to fill the form in."),
    ("The shop has begun stocking milk in returnable glass bottles.",
     "So the shop's plastic waste will fall.",
     "Customers will buy the glass bottles rather than continuing with plastic ones.",
     "Every customer switches to glass as soon as it is offered.",
     "Milk in returnable glass bottles is now stocked by the shop.",
     "The bottles are supplied by a dairy in the western district.",
     "Offering an alternative changes nothing unless people take it. If shoppers keep "
     "reaching for the plastic, the waste stays exactly where it was."),
    ("The hospital has opened a second operating theatre.",
     "So the hospital will be able to treat more patients each week.",
     "There are enough surgeons and nurses to staff the second theatre.",
     "Every hospital with two theatres treats twice as many patients.",
     "A second operating theatre has been opened at the hospital.",
     "The building work was finished ahead of the scheduled date.",
     "A theatre with nobody in it treats nobody. The conclusion needs staff the argument "
     "never mentions, and staff are usually the harder thing to find."),
    ("The new tyres grip better on wet roads than the ones they replaced.",
     "So the car will be safer to drive in the rain.",
     "The driver will not simply drive faster because the tyres hold the road better.",
     "Every car with good tyres is completely safe in the rain.",
     "On wet roads, the new tyres grip better than the tyres they replaced.",
     "The tyres were fitted at a workshop out on the highway last Tuesday.",
     "Better grip only helps if the driving stays the same. A driver who takes corners "
     "faster because the car feels surer can end up no safer at all."),
    ("The council has put a fence around the lake to keep dogs out.",
     "So the waterbirds nesting there will be left undisturbed.",
     "Dogs were the main thing disturbing the nesting birds.",
     "Every fenced area is completely free of disturbance.",
     "A fence has been put around the lake by the council to keep dogs out.",
     "The posts were cut from timber milled in the same shire.",
     "Fencing out dogs helps only if dogs were the problem. Foxes, cats or people walking "
     "close to the reeds would go on disturbing the birds through any fence."),
    ("The school has moved its sports day from November to March.",
     "So the day is less likely to be lost to extreme heat.",
     "March is reliably cooler here than November is.",
     "March is never hot in any part of the country at all.",
     "The school's sports day has been moved from November to March.",
     "The decision was recorded in the minutes of the March meeting.",
     "Moving a date only helps if the new date is better. In some parts of the country "
     "March is the hotter month, and the argument never checks which is which."),
    ("The library has doubled the number of computers available to the public.",
     "So people will spend less time waiting for a computer.",
     "The demand for the computers will not rise once more of them are available.",
     "Nobody ever waits for a computer once there are enough of them.",
     "The number of public computers in the library has been doubled.",
     "The old machines were sold to a recycler in the northern suburbs.",
     "Extra machines can draw extra users. If word gets round and twice as many people "
     "come in, the queue is where it started."),
    ("The recipe has been changed to use half as much salt.",
     "So the meals served will be healthier for the students.",
     "Nothing has been added in place of the salt that is worse for them.",
     "Every meal with less salt in it is healthier without exception.",
     "The recipe now uses half as much salt as it used to use.",
     "The kitchen was refitted with new benches over the summer.",
     "Taking one thing out can mean putting another in. If the salt has been replaced with "
     "sugar or extra fat to keep the flavour, the meal may be no better."),
    ("The town has installed a siren that can be heard across the whole valley.",
     "So everyone in the valley will be warned of a flood in time.",
     "People in the valley know what the siren means when they hear it.",
     "Everybody always responds immediately to any siren.",
     "A siren that can be heard across the whole valley has been installed.",
     "The unit was manufactured at a plant in South Australia.",
     "A sound is only a warning to somebody who understands it. Without that, the siren is "
     "just a noise, and people carry on as they were."),
    ("The council has widened the footpath outside the shops.",
     "So it will be easier for people using wheelchairs to get past.",
     "The obstacles that blocked the path are not still standing in the widened part.",
     "Every wide footpath anywhere is completely free of obstructions.",
     "The footpath outside the shops has been widened by the council.",
     "The work was completed in the last week of the financial year.",
     "Width helps only if the extra width is clear. Sandwich boards, bins and outdoor "
     "tables moved into the new space would leave the path as narrow as before."),
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

# ===================================================== identify the conclusion (15)

# (argument, conclusion, premise restated, overreach, reversal, explanation)
CONCLUSIONS = [
    ("The town's only doctor retires next month. No replacement has been found, and the "
     "nearest other surgery is forty minutes away.",
     "People here will soon have a much longer trip to see a doctor.",
     "No replacement has been found for the retiring doctor.",
     "Nobody in the town will ever see a doctor again.",
     "People here will soon have a much shorter trip to see a doctor.",
     "The retirement and the empty position are the reasons. What they are offered to "
     "establish is the journey people will face."),
    ("Rainfall in the catchment is down a third on the ten-year average. The reservoir is "
     "at its lowest level since it was built.",
     "The town is facing a serious shortage of water.",
     "Rainfall in the catchment is a third below the ten-year average.",
     "Every town in the state will run entirely out of water.",
     "The town has more water available than it usually does.",
     "Both statements are measurements. The shortage is what those measurements are being "
     "put together to show."),
    ("Bees pollinate most of the fruit grown in this valley. Bee numbers here have halved "
     "in a decade.",
     "Fruit growing in this valley is at risk.",
     "Bee numbers in the valley have halved over a decade.",
     "No fruit will grow anywhere in the valley again.",
     "Fruit growing in this valley is more secure than it was.",
     "The role of the bees and the fall in their numbers are the two reasons. The risk to "
     "the fruit is the point they support."),
    ("The pool needs two lifeguards on duty to open. Only one lifeguard is qualified at "
     "the moment, and training takes six weeks.",
     "The pool cannot open for at least six weeks.",
     "Only one qualified lifeguard is available at the moment.",
     "The pool will never be able to open its doors again.",
     "The pool can open within the next few days.",
     "The rule and the shortage are the reasons. The closure and its length are what those "
     "reasons establish."),
    ("The festival attracted twelve thousand people last year. The town has four hundred "
     "beds for visitors and no camping ground.",
     "Most festival visitors cannot stay overnight in the town.",
     "The town has four hundred visitor beds and no camping ground.",
     "Nobody at all is able to stay in the town overnight.",
     "The town has room for most festival visitors to stay overnight.",
     "The crowd size and the bed count are the two facts. The gap between them is what the "
     "argument exists to point out."),
    ("Native grasses in the reserve need fire every few years to seed. There has been no "
     "burn in the reserve for twenty years.",
     "The native grasses in the reserve are failing to reproduce.",
     "There has been no burn in the reserve for twenty years.",
     "Every native grass in the country is dying out completely.",
     "The native grasses in the reserve are reproducing well.",
     "What the grasses need and what they have not had are the reasons. The failure to "
     "seed is the conclusion drawn from them."),
    ("Second-hand textbooks cost a third of the price of new ones. The syllabus for this "
     "subject has not changed in five years.",
     "Buying second-hand is the sensible choice for this subject.",
     "Second-hand textbooks cost a third of what new ones cost.",
     "Nobody should ever buy a new textbook for any subject.",
     "Buying new is the sensible choice for this subject.",
     "The price difference and the unchanged syllabus are the reasons. That second-hand is "
     "the sensible buy is what they add up to."),
    ("The bridge carries eight thousand vehicles a day. It was designed for three thousand "
     "and was last strengthened in 1974.",
     "The bridge is carrying far more traffic than it was built for.",
     "The bridge was designed to carry three thousand vehicles a day.",
     "Every bridge in the state is on the point of collapse.",
     "The bridge is carrying less traffic than it was built for.",
     "The traffic count and the design figure are the two facts. The mismatch between them "
     "is the point being made."),
    ("The shop's busiest hour is between five and six in the evening. It closes at five.",
     "The shop is missing its best hour of trade every day.",
     "The shop closes its doors at five in the evening.",
     "Every shop that closes at five will go out of business.",
     "The shop is open for its best hour of trade every day.",
     "Both statements are about times. What they are put together to show is the trade the "
     "closing time gives away."),
    ("Solar panels produce most of their power in the middle of the day. The factory uses "
     "most of its power overnight.",
     "Solar panels alone will not cover the factory's power needs.",
     "The factory uses most of its power during the night.",
     "Solar panels are of no use to any factory at all.",
     "Solar panels alone will cover the factory's power needs.",
     "When the panels produce and when the factory uses are the two facts. The mismatch is "
     "what the argument is driving at."),
    ("Every seat on the flight was sold. Nine passengers did not arrive at the gate.",
     "The plane took off with nine empty seats.",
     "Every seat on the flight had been sold.",
     "No aircraft ever leaves with a full load of passengers.",
     "The plane took off with every seat occupied.",
     "The full sale and the missing passengers are the two facts. The empty seats are what "
     "follows from putting them together."),
    ("The koala colony needs a continuous canopy to move between feeding trees. A new road "
     "cuts the reserve into two halves.",
     "The road has divided the colony into two separated groups.",
     "A new road cuts the reserve into two halves.",
     "Every road built near a reserve wipes out its wildlife.",
     "The road has kept the colony together as one group.",
     "What the koalas need and what the road has done are the reasons. The division of the "
     "colony is the conclusion they support."),
    ("The recipe serves four and calls for six eggs. There are ten eggs in the fridge and "
     "eight people coming.",
     "There are not enough eggs in the fridge for the meal.",
     "The recipe serves four people and calls for six eggs.",
     "Nobody can ever cook this recipe for a group of eight.",
     "There are more than enough eggs in the fridge for the meal.",
     "The recipe, the eggs in the fridge and the number coming are three facts. What they "
     "add up to is the shortage."),
    ("The school's water tanks hold enough for three weeks of ordinary use. The bore has "
     "been out of action for a fortnight with no repair date set.",
     "The school will run short of water within about a week.",
     "The school's water tanks hold about three weeks of ordinary use.",
     "The school will have to close for good, since no water will ever reach it.",
     "The school has water enough for the rest of the term.",
     "The tank capacity and the length of the outage are the reasons. The week that is "
     "left is what they establish between them."),
    ("Reading a book takes concentration that a short video does not. Students report "
     "watching more videos and reading fewer books each year.",
     "Students are getting less practice at sustained concentration.",
     "Students report reading fewer books with each passing year.",
     "No student is capable of concentrating on anything any more.",
     "Students are getting more practice at sustained concentration.",
     "The difference between the two activities and the shift between them are the "
     "reasons. The loss of practice is what they are offered to show."),
]

for _i, (_arg, _key, _premise, _over, _rev, _expl) in enumerate(CONCLUSIONS):
    _label = _key[:44]
    if _key.rstrip(".") in _arg:
        raise AssertionError(f"{_label}: the conclusion is written out in the argument, "
                             f"so the question is a copying exercise")
    must_restate(_premise, _arg, f"{_label} [premise restated]")
    must_overreach(_over, f"{_label} [overreach]")
    must_balance([_key, _premise, _over, _rev], _label)
    B.Q("identify_conclusion",
        f"{_arg} Which one of these is the main conclusion the argument is driving at?",
        key=_key, verify=_key,
        wrong=[_premise, _over, _rev],
        expl=_expl,
        difficulty="hard" if _i % 3 else "medium",
        confidence=0.90 if _i % 3 else 0.92)

B.write()
