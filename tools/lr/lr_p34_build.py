#!/usr/bin/env python3
"""Builds lr_thinking_skills_p34.json — the last 19 §5.3 and §5.2 questions.

strengthen 11, weaken 8. Both close, which takes every named subcategory in §5.2, §5.3
and §5.4 to its target and the Thinking Skills book to 880/880.

Same paired construction as p21 and p28: each argument declares a weakener and a
strengthener, only one direction ships, and the other direction becomes the item's best
distractor. The typed checks in lr_prose apply to the remaining two options.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.lr.lr_common import Batch  # noqa: E402
from tools.lr.lr_prose import must_balance, must_be_unrelated, must_restate  # noqa: E402

B = Batch(nn=34)

# (direction, conclusion, evidence, weakener, strengthener, irrelevance, restatement, expl)
ARGUMENTS = [
    ("strengthen",
     "The new ramp has made the town hall easier to get into.",
     "More people using wheelchairs have attended events since it was built.",
     "The hall began running a free minibus service in the same month.",
     "No transport or booking arrangements were changed while the ramp was built.",
     "The handrails were powder-coated in a workshop two suburbs away.",
     "Attendance by people using wheelchairs has risen since the ramp was built.",
     "If nothing else changed, the ramp is what the higher attendance has to be credited "
     "to. A minibus arriving at the same time would explain it just as well."),
    ("weaken",
     "The reef survey shows the coral is recovering.",
     "Divers recorded more live coral this year than last year.",
     "This year's survey was carried out at a sheltered site the earlier one skipped.",
     "Both surveys covered exactly the same stretch of reef in the same order.",
     "The survey boat is moored at a jetty on the eastern side of the bay.",
     "More live coral was recorded by divers this year than last year.",
     "A sheltered site holds healthier coral whatever is happening elsewhere. The higher "
     "figure measures where they looked rather than how the reef is faring."),
    ("strengthen",
     "The new school timetable has cut the time lost between lessons.",
     "Teachers report classes starting sooner than they did last year.",
     "Two of the most distant classrooms were taken out of use over the summer.",
     "Every classroom in use last year is still in use on the same rooms and floors.",
     "The timetable was drawn up by a committee that met on Thursday afternoons.",
     "Teachers say their classes start sooner than they did last year.",
     "Closing distant rooms would shorten the walk between lessons on its own. Ruling that "
     "out leaves the timetable as the reason classes start sooner."),
    ("weaken",
     "The nesting boxes have helped the possum population.",
     "More possums have been counted in the reserve since the boxes went up.",
     "Land clearing next door has pushed possums into the reserve from outside.",
     "No land was cleared or built on anywhere near the reserve over the period.",
     "The boxes were built from marine ply donated by a hardware chain.",
     "Possum counts in the reserve have risen since the nesting boxes went up.",
     "Possums moving in from a cleared block would raise the count without a single extra "
     "animal being born. The reserve gains what the neighbouring land loses."),
    ("strengthen",
     "The change to the bin lids has cut contamination in the recycling.",
     "The proportion of wrong items in the recycling has fallen since the lids changed.",
     "A council education campaign about recycling ran over the same three months.",
     "No campaign, leaflet or notice about recycling was run over the period.",
     "The lids are moulded at a plant on the outskirts of Wodonga.",
     "The proportion of wrong items in the recycling has dropped since the lids changed.",
     "A campaign would cut contamination on its own. Ruling one out leaves the lids as the "
     "only thing that changed."),
    ("weaken",
     "The tutoring programme has raised reading levels in Year 3.",
     "Year 3 reading levels are higher at the end of the year than at the start.",
     "Reading levels rise over a year in every Year 3 class, with or without tutoring.",
     "A matched Year 3 class without the tutoring showed no rise over the same year.",
     "The sessions were held in a demountable classroom behind the library.",
     "Reading levels in Year 3 are higher at the end of the year than at the start.",
     "Children get better at reading as they get older. If the rise happens anyway, the "
     "figures show a year passing rather than a programme working."),
    ("strengthen",
     "The new goalkeeper has tightened the team's defence.",
     "The team has conceded fewer goals since she joined.",
     "The two best strikers in the league were injured over the same period.",
     "The league's leading strikers all played every match over the period.",
     "The club's home ground was resurfaced during the winter break.",
     "The team has conceded fewer goals since the new goalkeeper joined.",
     "Facing the same strikers means facing the same test, so fewer goals points at the "
     "keeper. Absent strikers would have thinned the tally on their own."),
    ("weaken",
     "The longer lunch break has improved behaviour in afternoon classes.",
     "Fewer behaviour incidents are recorded in the afternoon than before the change.",
     "The school stopped recording minor incidents in the same term.",
     "The way incidents are recorded has not changed at any point.",
     "The break was extended after a vote at a staff meeting in February.",
     "Fewer behaviour incidents are being recorded in the afternoon than before.",
     "Stopping the recording of minor incidents cuts the count without changing a single "
     "child's behaviour. The figures measure the paperwork."),
    ("strengthen",
     "The seed bank's storage method keeps native seeds viable for longer.",
     "Seeds stored by the new method germinated at a higher rate after five years.",
     "The seeds put into the new store were collected in an unusually good season.",
     "Seeds from the same collection were split between the old and new stores.",
     "The store was built with a grant announced at the end of the financial year.",
     "Seeds stored by the new method germinated at a higher rate after five years.",
     "Splitting one collection between the two stores means the seeds started identical, "
     "so the difference after five years is down to the storage."),
    ("weaken",
     "The pedestrian mall has been good for the shops in it.",
     "Takings in the mall's shops are higher than before it was closed to cars.",
     "Three of the mall's shops closed down and their customers went to the rest.",
     "The same shops are trading in the mall as before it was closed to cars.",
     "The paving stones were quarried in the state's central highlands.",
     "Shops in the mall are taking more than before it was closed to cars.",
     "Fewer shops sharing the same customers each take more without a single extra "
     "shopper arriving. The average rises as the street empties."),
    ("strengthen",
     "The night-time speed limit has reduced crashes on the mountain road.",
     "Fewer crashes have been recorded on that road at night since the limit came in.",
     "The road was closed for eleven weeks of repairs during the same period.",
     "The road stayed open every night throughout the period being compared.",
     "The new signs were installed by a crew working out of the regional depot.",
     "Fewer crashes at night have been recorded on that road since the limit came in.",
     "A road that stays open carries the same traffic, so fewer crashes points at the "
     "limit. Eleven weeks of closure would cut the count by itself."),
    ("weaken",
     "The new watering roster has kept the sports field in better condition.",
     "The field has been playable on more days this season than last season.",
     "Rainfall this season has been well above the season before it.",
     "Rainfall this season has been almost the same as the season before it.",
     "The sprinklers were installed by a contractor over the summer break.",
     "The field has been playable on more days this season than it was last season.",
     "A wetter season keeps a field green whatever the roster says. The extra playable "
     "days may be the weather rather than the watering."),
    ("strengthen",
     "The audiobook version has helped struggling readers finish the novel.",
     "More struggling readers finished the book in the class that had the audiobook.",
     "The class with the audiobook was given an extra fortnight to finish.",
     "Both classes were given exactly the same number of weeks to finish the book.",
     "The recording was made in a studio in the inner north of the city.",
     "More struggling readers finished the novel in the class that had the audiobook.",
     "Equal time means the two classes faced the same task, so the difference points at "
     "the audiobook. An extra fortnight would explain it on its own."),
    ("weaken",
     "The fitness app makes people walk further.",
     "People using the app record more steps than people who do not.",
     "Only people already walking a lot bother to install a step-counting app.",
     "The app was given to a randomly chosen half of a large group of volunteers.",
     "The app was written by a small team working out of a shared office.",
     "People who use the app record more steps than people who do not use it.",
     "If keen walkers are the ones who install it, the app's users were walking further "
     "before they downloaded anything. The comparison shows who chose it."),
    ("strengthen",
     "The rewritten instructions have made the machine easier to set up.",
     "New staff are taking less time to set the machine up than they used to.",
     "The machine itself was replaced with a simpler model in the same month.",
     "The machine is the same one that was in use before the instructions changed.",
     "The instructions were printed on waterproof card at a local copy shop.",
     "New staff take less time to set the machine up than they used to take.",
     "Keeping the same machine means the instructions are the only thing that changed, so "
     "the improvement has nothing else to be credited to."),
    ("weaken",
     "The new filter has improved the air quality in the workshop.",
     "Dust readings in the workshop are lower than they were last year.",
     "The dustiest work was moved out to a separate shed at the same time.",
     "Exactly the same work is being done in the workshop as before.",
     "The filter unit was delivered on a truck from the northern depot.",
     "Dust readings taken in the workshop are lower than they were last year.",
     "Moving the dusty work out would cut the readings whatever the filter did. Two "
     "changes at once cannot be told apart."),
    ("strengthen",
     "The mentoring scheme has improved attendance among Year 9 students.",
     "Attendance among the Year 9 students in the scheme has risen this year.",
     "Only students with good attendance records were offered a place in the scheme.",
     "Places in the scheme were offered to every Year 9 student in the year level.",
     "The scheme is run from a room off the main corridor on Wednesdays.",
     "Attendance among Year 9 students in the scheme has risen over this year.",
     "Offering it to everyone removes the question of who was let in, so the comparison is "
     "no longer between the reliable students and the rest."),
    ("strengthen",
     "The garden beds are producing more since the soil was improved.",
     "The beds have yielded more vegetables this season than last season.",
     "The gardeners planted a far larger area this season than they did last.",
     "The gardeners planted exactly the same area in both seasons.",
     "The compost was delivered in bulk by a supplier from the outer east.",
     "The beds have yielded more vegetables this season than they did last season.",
     "Planting the same area means the beds faced the same task, so a bigger yield points "
     "at the soil. A larger planting would raise the total on its own."),
    ("strengthen",
     "The new signage has helped visitors find their way around the hospital.",
     "Fewer visitors are asking staff for directions than before the signs went up.",
     "Two extra help desks were opened in the foyer in the same month.",
     "No help desks or information points were added or moved over the period.",
     "The signs were manufactured at a factory in the state's south-west.",
     "Fewer visitors are asking staff for directions than before the signs went up.",
     "Extra help desks would cut the questions put to other staff without the signs doing "
     "anything. Ruling them out leaves the signage as the reason."),
]

for _i, (_dir, _concl, _ev, _weak, _strong, _irrel, _restate, _expl) in enumerate(ARGUMENTS):
    _label = _concl[:44]
    if _weak == _strong:
        raise AssertionError(f"{_label}: the weakener and the strengthener are the same fact")
    must_restate(_restate, _ev, f"{_label} [restatement]")
    must_be_unrelated(_irrel, _concl, f"{_label} [irrelevance]")
    _key, _other = (_weak, _strong) if _dir == "weaken" else (_strong, _weak)
    must_balance([_key, _other, _irrel, _restate], _label)
    B.Q(f"{_dir}_argument",
        f"{_concl} {_ev} Which one of these, if true, most {_dir}s the argument?",
        key=_key, verify=_key,
        wrong=[_other, _irrel, _restate],
        expl=_expl,
        difficulty="hard" if _i % 3 else "medium",
        confidence=0.90 if _i % 3 else 0.92)

B.write()
