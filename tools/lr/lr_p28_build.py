#!/usr/bin/env python3
"""Builds lr_thinking_skills_p28.json — 32 §5.2 argument questions.

weaken 16, strengthen 16. §5.2 reaches 315/396; Thinking Skills 775/880.

p21's construction, at scale. Every argument declares BOTH a fact that weakens it and a
fact that strengthens it, and only one of the pair is emitted — the weaken item keys the
weakener and offers the strengthener as its best distractor, the strengthen item does the
reverse. A direction error cannot survive that, because it would make the same option
correct read either way.

Only one of each pair ships because two stems sharing a forty-word argument and differing
by one word score far above phase 4's silent 0.85 dedup. The other two distractors are
typed and checked by lr_prose: the restatement must echo the evidence, the irrelevance
must not touch the conclusion, and all four must stay within 70% of each other in length
so the key does not announce itself.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.lr.lr_common import Batch  # noqa: E402
from tools.lr.lr_prose import must_balance, must_be_unrelated, must_restate  # noqa: E402

B = Batch(nn=28)

# (direction, conclusion, evidence, weakener, strengthener, irrelevance, restatement, expl)
ARGUMENTS = [
    ("weaken",
     "The new streetlights have made the park safer at night.",
     "Reported thefts in the park have halved since they were installed.",
     "Far fewer people now walk through the park after dark than before.",
     "The number of people walking through the park at night has stayed steady.",
     "The lights were installed by a contractor based in the next council area.",
     "Thefts reported in the park are now half what they were.",
     "Half as many people about means half as many chances to be robbed, so the drop in "
     "thefts would happen at an unchanged level of risk. The figure no longer shows the "
     "lights did anything."),
    ("strengthen",
     "The reading programme has improved comprehension in Year 4.",
     "Year 4 comprehension scores rose in the term the programme ran.",
     "A new comprehension test was introduced in the same term, with easier passages.",
     "The same comprehension test was used before and after the programme ran.",
     "The funding was announced in a media release from the education minister.",
     "Comprehension scores in Year 4 went up during the term of the programme.",
     "If the test did not change, the higher scores measure the students rather than the "
     "paper. That removes the most obvious rival explanation for the rise."),
    ("weaken",
     "Cycling to work makes people healthier.",
     "People who cycle to work take fewer sick days than those who drive.",
     "Anyone unwell enough to worry about it drives rather than riding in.",
     "Drivers who switched to cycling began taking fewer sick days than before.",
     "The council resurfaced two of the main cycle routes over the summer.",
     "Workers who cycle in take fewer days off sick than workers who drive.",
     "The group being counted is assembled by the very thing being measured. If illness "
     "moves people out of the cycling group, the cyclists will look healthy whatever "
     "cycling does."),
    ("strengthen",
     "The rock lobster population off this coast is recovering.",
     "Divers counted 30 per cent more lobsters this season than last.",
     "Divers searched a much larger stretch of reef this season than last season.",
     "Divers covered exactly the same stretch of reef in both seasons.",
     "The survey was carried out by volunteers from the local diving club.",
     "This season's lobster count was 30 per cent higher than last season's.",
     "Counting the same reef both times makes the two numbers comparable. Without that, a "
     "bigger count might only mean a bigger search."),
    ("weaken",
     "The tutoring centre raises students' marks.",
     "Students who attend the centre score higher than those who do not.",
     "Only students already scoring well are accepted onto the centre's programme.",
     "Students' marks rose in the term after they started at the centre, not before.",
     "The centre operates from a shopfront near the railway station.",
     "Students attending the centre score higher marks than students who do not.",
     "If good marks are the price of entry, the centre's students would score well without "
     "it. The comparison then shows who was admitted rather than what the tutoring did."),
    ("strengthen",
     "The wetland restoration has brought the frogs back.",
     "Frog calls recorded at the site have tripled since the work was done.",
     "Recording equipment was upgraded to a far more sensitive model that same year.",
     "The same recording equipment was used before and after the restoration work.",
     "The restoration was carried out over two winters by a Landcare group.",
     "Recorded frog calls at the site are now three times what they were.",
     "Unchanged equipment means the two recordings measure the same thing. A more "
     "sensitive microphone would have found more calls whatever the frogs did."),
    ("weaken",
     "The morning bell change has improved punctuality.",
     "Fewer students have been marked late since the bell moved to 9:00.",
     "The rule was changed at the same time so that lateness is now recorded from 9:15.",
     "The recording rule was left exactly as it was when the bell time moved.",
     "The new bell tone was chosen by a vote among the Year 6 students.",
     "The number of students marked late has dropped since the bell moved.",
     "Moving the line at which lateness is recorded would cut the count on its own. The "
     "figures measure the rule rather than the students."),
    ("strengthen",
     "The rooftop garden has cooled the building.",
     "Top-floor temperatures are lower this summer than last summer.",
     "This summer has been considerably cooler across the whole city than last summer.",
     "City-wide summer temperatures were the same in both years.",
     "The garden was planted with succulents chosen for their low water needs.",
     "Temperatures on the top floor are lower this summer than they were last summer.",
     "Ruling out a cooler summer leaves the garden as the difference between the two "
     "years. Without it, the whole city's weather could explain the drop."),
    ("weaken",
     "The library's reading challenge has made students read more.",
     "Students in the challenge report reading twice as many books as other students.",
     "Students in the challenge count picture books that other students would not count.",
     "Both groups were asked to count books the same way, using the same list.",
     "Entry forms are handed out during the first week of the winter term.",
     "Students in the challenge say they read twice as many books as other students.",
     "If the two groups are counting different things, the doubled figure is a difference "
     "in bookkeeping rather than in reading. The comparison stops meaning anything."),
    ("strengthen",
     "The speed camera has slowed traffic on the highway.",
     "Average speeds past the camera have fallen by 8 km/h since it was switched on.",
     "Roadworks narrowed the highway to one lane in the month the camera started.",
     "No roadworks or lane changes took place while the camera was being introduced.",
     "The camera was paid for out of the state road safety budget for the year.",
     "Traffic past the camera now averages 8 km/h slower than before it was switched on.",
     "Roadworks would have slowed traffic on their own. Ruling them out leaves the camera "
     "as the reason the average fell."),
    ("weaken",
     "The new fertiliser increases wheat yields.",
     "Fields treated with it yielded a fifth more wheat than untreated fields.",
     "The treated fields lie on the river flats and the untreated ones on stony ground.",
     "Treated and untreated fields were chosen at random across the same paddock.",
     "The fertiliser is sold in 25 kilogram bags through rural supply stores.",
     "Fields given the fertiliser yielded a fifth more wheat than fields without it.",
     "Better soil would raise the yield whatever was spread on it. The comparison is "
     "between two kinds of ground rather than between two treatments."),
    ("strengthen",
     "The hand-washing campaign has cut illness in the school.",
     "Absences due to illness are down a third since the campaign began.",
     "The school also installed air filters in every classroom that same term.",
     "No other health measure was introduced while the campaign was running.",
     "The campaign posters were printed by a company in the next suburb.",
     "Illness absences have fallen by a third since the campaign started.",
     "If nothing else changed, the campaign is what the drop has to be credited to. Two "
     "measures at once could not be told apart."),
    ("weaken",
     "The later closing time has increased the shop's takings.",
     "Weekly takings are up since the shop began closing at eight instead of six.",
     "A rival shop two doors down shut for good in the same week as the change.",
     "No other shop in the street opened, closed or changed hours that month.",
     "The shop has been run by the same family since it opened in 1994.",
     "The shop's weekly takings have risen since it started closing at eight.",
     "Customers with nowhere else to go would lift takings whatever the hours were. Two "
     "changes at once cannot be separated."),
    ("strengthen",
     "The pedestrian crossing has made the road safer for children.",
     "No child has been hurt on that stretch of road since the crossing was built.",
     "The school moved to a new site in the same month, so far fewer children cross there.",
     "The same number of children cross the road each day as before the crossing was built.",
     "The crossing was painted during the September school holidays.",
     "There have been no injuries to children on that stretch since the crossing was built.",
     "The same number crossing means the same exposure to risk, so a fall in injuries "
     "points at the crossing. Fewer children would explain it without any safety gain."),
    ("weaken",
     "The training course improves how quickly staff answer calls.",
     "Staff who took the course answer calls faster than staff who did not.",
     "Staff were sent on the course in order of how fast they already were.",
     "Staff were sent on the course by drawing names at random from the whole team.",
     "The course is delivered over two afternoons in a room above the depot.",
     "Staff who have taken the course answer calls faster than staff who have not.",
     "If the quick ones went first, the course's graduates were fast before they arrived. "
     "The comparison shows the selection, not the training."),
    ("strengthen",
     "The mulch has reduced water use in the garden beds.",
     "Watering has dropped by a third since the beds were mulched.",
     "The mulching was done at the start of an unusually wet autumn.",
     "Rainfall over the period was the same as in the year before the mulching.",
     "The mulch was delivered in bulk by a supplier from the northern suburbs.",
     "Water used on the beds has fallen by a third since they were mulched.",
     "Equal rainfall means the beds needed the same watering as before, so the drop is "
     "down to the mulch. A wet spell would have cut the watering by itself."),
    ("weaken",
     "The new bus timetable has reduced crowding.",
     "Fewer passengers are counted on the busiest services than before the change.",
     "Two thousand commuters switched to the new rail line the month the timetable began.",
     "Passenger numbers across the whole network were unchanged over the period.",
     "The timetables were printed and distributed by the transport authority.",
     "The busiest services now carry fewer passengers than before the timetable changed.",
     "Passengers leaving the buses altogether would thin the busiest services without the "
     "timetable doing anything. The count measures the rail line."),
    ("strengthen",
     "The revision guide helps students in the final exam.",
     "Students who used the guide scored higher in the final exam.",
     "The guide was bought mainly by students who were already doing well.",
     "The guide was given free to every student in the year, so all of them had one.",
     "The guide runs to 80 pages and was written by two former teachers.",
     "Students who used the revision guide achieved higher scores in the final exam.",
     "Giving it to everybody removes the question of who chose to buy it, so the "
     "comparison is no longer between keen students and the rest."),
    ("weaken",
     "The compost bins have cut the school's rubbish.",
     "The general rubbish collected each week is down by a quarter since they arrived.",
     "The cleaners began taking paper waste out to a separate skip in the same week.",
     "No other change was made to how the school's waste is collected or sorted.",
     "The bins were built by Year 8 students in their design and technology class.",
     "General rubbish collected each week has fallen by a quarter since the bins arrived.",
     "Paper going to a different skip would cut the general rubbish whatever the compost "
     "bins did. Two changes at once cannot be told apart."),
    ("strengthen",
     "The shade sails have reduced sunburn at the pool.",
     "Reported sunburn among swimmers is down since the sails went up.",
     "The pool has been open far fewer hours this season than it was last season.",
     "The pool has kept exactly the same opening hours as it did last season.",
     "The sails were made from a fabric woven at a mill in regional Victoria.",
     "Sunburn reported by swimmers has dropped since the shade sails were put up.",
     "Unchanged hours mean the same exposure to the sun, so a fall in sunburn points at "
     "the sails. Fewer hours open would explain it without them."),
    ("weaken",
     "The reminder texts have improved attendance at appointments.",
     "The proportion of patients who miss appointments has fallen since texting began.",
     "The clinic also began charging a fee for missed appointments that same month.",
     "No fee or penalty for missing an appointment was introduced at any point.",
     "The texts are sent by a system the clinic leases from a company interstate.",
     "The proportion of patients missing their appointments has dropped since texting began.",
     "A fee would bring patients in whatever the texts said. With both changes landing "
     "together, the improvement cannot be credited to either."),
    ("strengthen",
     "The oval's new drainage has cut the number of cancelled matches.",
     "Fewer matches have been called off this season than last season.",
     "Rainfall this season has been well below the season before.",
     "Rainfall this season has been almost identical to the season before.",
     "The drainage work was completed during the winter shutdown last year.",
     "Fewer matches have been cancelled this season than were cancelled last season.",
     "Similar rainfall means the oval faced the same test both years, so the drop points "
     "at the drainage. A dry season would explain it on its own."),
    ("weaken",
     "The new packaging has increased sales of the juice.",
     "Sales are up by 15 per cent since the packaging was redesigned.",
     "The juice was moved to the shelf beside the checkout in the same week.",
     "The juice has stayed on exactly the same shelf throughout the period.",
     "The packaging was designed by a studio that specialises in food labels.",
     "Sales of the juice have risen by 15 per cent since the packaging was redesigned.",
     "A place beside the checkout lifts sales of almost anything. With the shelf and the "
     "packaging changing together, the rise cannot be credited to either."),
    ("strengthen",
     "The mentoring scheme keeps new teachers in the profession.",
     "Teachers in the scheme are more likely to still be teaching after three years.",
     "Only teachers who had already committed to a second year could join the scheme.",
     "Every new teacher was placed in the scheme automatically on being appointed.",
     "The scheme is coordinated from the department's regional office.",
     "Teachers who joined the scheme are more likely to be teaching three years later.",
     "Placing everyone in it removes the question of who opted in, so the comparison is no "
     "longer between the committed and the rest."),
    ("weaken",
     "The exercise programme has improved the residents' balance.",
     "Residents in the programme have had fewer falls than those not in it.",
     "Residents already unsteady on their feet were not permitted to take part.",
     "Places in the programme were allocated by drawing lots among all residents.",
     "Sessions are held three mornings a week in the room beside the kitchen.",
     "Residents taking part in the programme have had fewer falls than the others.",
     "If the unsteady were kept out, the participants were steadier before they started. "
     "The comparison shows who was allowed in rather than what the exercise did."),
    ("strengthen",
     "The filter has improved the water quality in the tank.",
     "Cloudiness readings from the tank are lower since the filter was fitted.",
     "The tank was scrubbed out and refilled on the day the filter went in.",
     "The tank was not cleaned or refilled at any point around the fitting.",
     "The filter was bought from a rural supplies store in the same shire.",
     "Cloudiness readings from the tank have fallen since the filter was fitted.",
     "A scrub-out would clear the water on its own. Ruling it out leaves the filter as the "
     "reason the readings fell."),
    ("weaken",
     "The homework club raises the marks of the students who attend.",
     "Students at the club have higher marks than students who do not attend.",
     "Parents who send children to the club also pay for weekend coaching.",
     "The club's students were matched to non-attenders of the same starting mark.",
     "The club meets in the school library from half past three on Tuesdays.",
     "Students who attend the homework club have higher marks than students who do not.",
     "If the same families buy both, the weekend coaching could be doing the work. The "
     "club would then mark out the household rather than cause anything."),
    ("strengthen",
     "The soft-fall surface has reduced playground injuries.",
     "Fewer injuries have been recorded in the playground since it was laid.",
     "The playground was closed for six weeks of the term while other work was done.",
     "The playground was open for exactly the same number of days as the year before.",
     "The surface was laid by a contractor over the September holidays.",
     "Recorded playground injuries have fallen since the soft-fall surface was laid.",
     "The same number of open days means the same exposure, so fewer injuries points at "
     "the surface. A long closure would explain the drop by itself."),
    ("weaken",
     "The new watering system has improved the crop.",
     "Yields from the treated rows are higher than from the untreated rows.",
     "The treated rows are the ones at the sheltered end of the paddock.",
     "Treated and untreated rows were spread evenly across the whole paddock.",
     "The system was installed by a contractor over three days in early spring.",
     "The rows on the new watering system yielded more than the untreated rows.",
     "Shelter would lift the yield whatever the watering did. The comparison is between "
     "two parts of the paddock rather than between two systems."),
    ("strengthen",
     "The recycling signage has reduced contamination in the bins.",
     "Contamination rates in the bins have fallen since the new signs went up.",
     "The bins themselves were replaced with a different shape at the same time.",
     "The bins are the same ones that were in place before the signs went up.",
     "The signs were designed by a graphics student on work experience.",
     "Contamination in the bins has dropped since the new signs were put up.",
     "Keeping the same bins means the signs are the only thing that changed, so the "
     "improvement has nothing else to be credited to."),
    ("weaken",
     "The trial of four-day weeks has made staff more productive.",
     "Output per person is higher since the four-day week began.",
     "Six of the slowest workers left the company in the month the trial started.",
     "No staff joined or left the company during the whole of the trial period.",
     "The change was announced at a meeting held in the middle of February.",
     "Output per person has risen since the four-day week began.",
     "Losing the slowest workers lifts the average without anyone working better. The "
     "figure measures who is left rather than how they work."),
    ("strengthen",
     "The early literacy programme helps children who start behind.",
     "Children in the programme caught up to the class average within a year.",
     "Children who start behind often catch up in that year without any help at all.",
     "A matched group who started equally far behind did not catch up that year.",
     "The programme is delivered in half-hour sessions by a visiting specialist.",
     "Children in the programme reached the class average within a year of starting.",
     "A comparison group who started level and did not catch up shows the gain was not "
     "going to happen anyway. Without it, ordinary development would explain it."),
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
