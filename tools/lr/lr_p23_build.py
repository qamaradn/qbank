#!/usr/bin/env python3
"""Builds lr_thinking_skills_p23.json — 32 §5.2 argument questions.

identify_assumption 12, identify_conclusion 10, correlation_vs_causation 10. §5.2 goes
199/396 to 231/396; Thinking Skills reaches 615/880. correlation_vs_causation closes at
26/26 and identify_conclusion at 25/40.

None of these has a computable answer, so the discipline is p21's, extracted into
lr_prose and applied per item: every distractor declares what it is doing and the build
checks that it does it. An "irrelevant" option is checked against the conclusion, a
"restatement" against the text it restates, an "overreach" for an absolute word, and all
four for length.

Two further checks belong to this batch alone.

    An assumption must be UNSTATED. must_not_restate holds the key against the argument
    it belongs to and fails if it is close to being said outright, which is the way an
    assumption question quietly stops testing anything.

    The correlation keys are spread across four ways a link can arise without cause —
    reverse causation, a common cause behind both, how the group was selected, and plain
    coincidence — and the build refuses if any one of them carries more than three of the
    ten. Ten items that all turn out to be "something else caused both" teach the
    student to answer the question type rather than the question.
"""
import collections
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.lr.lr_common import Batch  # noqa: E402
from tools.lr.lr_prose import (  # noqa: E402
    must_assert_cause, must_balance, must_be_unrelated, must_not_restate, must_overreach,
    must_restate,
)

B = Batch(nn=23)

# ===================================================== identify the assumption (12)

# (evidence, conclusion, assumption, over-strong, restatement, irrelevance, explanation)
ASSUMPTIONS = [
    ("The new tram stop has been built directly outside the town library.",
     "So more people will visit the library.",
     "Some people stay away from the library because it is awkward to get to.",
     "Everybody who uses the new tram will call in at the library.",
     "A tram stop has been placed right at the front of the town library.",
     "Ticket machines were upgraded across the network in March.",
     "The argument only works if getting there was part of what kept people away. If "
     "everyone who wanted to visit could already do so easily, a closer stop changes "
     "nothing. Deny the assumption and the conclusion falls with it."),
    ("Students who eat breakfast score better in morning tests than students who do not.",
     "So the school should provide breakfast to its students.",
     "Students who skip breakfast at home would eat one provided at school.",
     "Every student who eats breakfast does well in morning tests.",
     "In morning tests, the better scores go to the students who have eaten breakfast.",
     "The hall is used for assemblies on Friday mornings each fortnight.",
     "Providing breakfast helps nobody unless the students who currently go without "
     "actually eat it. If they would skip the school's breakfast too, the plan cannot "
     "produce the improvement it is aiming at."),
    ("The council is putting more bins along the paths through the park.",
     "So the amount of litter dropped in the park will fall.",
     "Some litter is dropped by people who would use a bin if one were close by.",
     "Nobody ever drops litter when there is a bin nearby.",
     "More bins are being installed along the park's paths by the council.",
     "The grounds were laid out in 1954 and cover a little over eight hectares.",
     "If every piece of litter comes from people who would not use a bin whatever the "
     "distance, more bins will make no difference at all. The argument needs at least "
     "some litterers to be the convenient sort."),
    ("This bridge was built to carry 20 tonnes, and the loaded truck weighs 18 tonnes.",
     "So the truck can cross the bridge safely.",
     "The bridge is still in the condition it was in when it was built.",
     "Every bridge can carry rather more than the limit written on it.",
     "The truck's 18 tonnes is under the 20 tonnes the bridge was built to carry.",
     "The approach road was resurfaced during the winter shutdown last year.",
     "A number stamped on a bridge describes it when new. Rust, rot or a cracked "
     "footing could leave it carrying far less than 20 tonnes today, and the argument "
     "never checks."),
    ("Our team has trained twice as often this season as it did last season.",
     "So we will finish higher on the ladder than we did last year.",
     "The other teams have not increased their own training by as much.",
     "Training is the only thing that decides where a team finishes.",
     "This season the team has trained twice as many times as it did last season.",
     "The club's playing colours have been navy and gold since it was founded.",
     "Ladder position is a comparison, not a measurement. Training harder lifts a team "
     "only if the rest of the competition has not done the same, and the argument "
     "quietly assumes it has not."),
    ("The recipe says to bake the cake at 180 degrees, and the oven dial is set there.",
     "So the cake will bake at the temperature the recipe intends.",
     "The oven reaches the temperature that its dial is showing.",
     "Every cake baked at 180 degrees turns out exactly as intended.",
     "The oven dial has been set to the 180 degrees that the recipe asks for.",
     "The cake tin being used measures 20 centimetres across at the base.",
     "Setting a dial and reaching a temperature are two different things. An oven that "
     "runs 20 degrees cool defeats the argument entirely, and nothing here rules that "
     "out."),
    ("Sales of the printed newspaper have fallen ever since it launched its website.",
     "So the website is drawing readers away from the printed paper.",
     "The people who stopped buying the paper have not simply stopped following news.",
     "Nobody at all reads the printed paper and the website together.",
     "Ever since the website launched, sales of the printed newspaper have dropped.",
     "The masthead has been published continuously since the spring of 1887.",
     "Readers who drifted away from news altogether would produce the same fall in "
     "sales without ever visiting the website. The argument needs them to have moved "
     "across rather than simply left."),
    ("In laboratory tests this sunscreen blocked 98 per cent of ultraviolet light.",
     "So swimmers who use it at the beach will not get burnt.",
     "Swimmers put it on as thoroughly as it was applied during the tests.",
     "No sunscreen ever fails to protect the skin it is put on.",
     "Laboratory tests found the sunscreen blocked 98 per cent of ultraviolet light.",
     "The trials were carried out at a testing laboratory on the edge of Adelaide.",
     "A thin, patchy or half-washed-off layer is not the layer that was tested. The "
     "laboratory figure carries over to the beach only if the application does too."),
    ("We asked 200 people at the shopping centre and 70 per cent supported the new road.",
     "So most people in the city support the new road.",
     "Shoppers at that centre think about the road much as the rest of the city does.",
     "Everyone living in the city was asked for a view on the road.",
     "Of the 200 people asked at the shopping centre, 70 per cent were in favour.",
     "Collecting the responses took a little under three hours on the day.",
     "A sample stands for a city only if it resembles it. Shoppers at one centre may be "
     "exactly the people the road would help, and the argument never establishes that "
     "they are typical."),
    ("The school's electricity bill dropped after the solar panels were installed.",
     "So the panels are saving the school money overall.",
     "The drop in the bill is larger than what the panels cost to run and maintain.",
     "Solar panels always pay for themselves within a single year.",
     "After the solar panels were installed, the school's electricity bill dropped.",
     "The installation work was carried out over the summer holiday period.",
     "A smaller bill is not the same as a saving. Cleaning, repairs and loan repayments "
     "all come off the other side, and the argument assumes without saying so that they "
     "come to less than the drop."),
    ("From next term the library will open one hour earlier than it does now.",
     "So more students will use the library before school starts.",
     "Some students already arrive at school early enough to use that extra hour.",
     "All students arrive at school a full hour before the first lesson.",
     "The library's opening time will move an hour earlier from the start of next term.",
     "There are a little over twelve thousand books on the shelves at present.",
     "An hour nobody is at school for is an hour nobody can use. The conclusion needs "
     "students to be on the grounds already, which the argument never establishes."),
    ("Traffic past the school has slowed noticeably since the speed humps were built.",
     "So the road past the school is now safer for children.",
     "Slower traffic makes a road less dangerous for the children crossing it.",
     "A road with speed humps built into it is never dangerous.",
     "Since the speed humps were built, the traffic past the school has slowed down.",
     "The work was paid for out of the council's roads budget for the year.",
     "The argument slides from slower to safer, and those are different claims. It "
     "holds only if speed is what made the road dangerous in the first place, rather "
     "than sightlines or the absence of a crossing."),
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
        expl=_expl, difficulty="hard" if _i % 3 else "medium",
        confidence=0.90 if _i % 3 else 0.92)

# ===================================================== identify the conclusion (10)

# (argument, conclusion, premise restated, overreach, reversal, explanation)
CONCLUSIONS = [
    ("Bushfire seasons in Victoria are starting earlier than they used to. Fire services "
     "now have less time between seasons to service equipment and train volunteers.",
     "Victoria is less prepared for each fire season than it once was.",
     "Fire services have less time between seasons than they used to have.",
     "No fire service in Victoria will be able to cope with the next season.",
     "Victoria is better prepared for each fire season than it once was.",
     "The two statements are both reasons. What they are offered in support of is the "
     "state of the preparation, which is the claim the argument is driving at."),
    ("The town's only bakery closes at three in the afternoon. Most people in the town "
     "finish work at five.",
     "The bakery misses the trade of people heading home from work.",
     "Most of the town's workers finish their working day at five o'clock.",
     "Every bakery that closes early will eventually go out of business.",
     "The bakery's closing time suits the town's working hours well.",
     "Both statements are facts about times. The point they are put together to make is "
     "about the customers those times leave out."),
    ("Recycling bins have been placed in every classroom in the school. The amount of "
     "paper in the general rubbish has not changed since they arrived.",
     "The classroom bins are not catching the paper they were meant to catch.",
     "A recycling bin has been placed in every one of the school's classrooms.",
     "Recycling schemes never work properly in schools of any kind.",
     "The bins have cut the amount of paper going into the general rubbish.",
     "The unchanged rubbish is evidence, not the point. What it is evidence for is that "
     "the bins are not doing the job they were installed to do."),
    ("The ferry timetable has not changed in ten years. The town's population has "
     "doubled over the same period.",
     "Each ferry sailing now carries far more people than it was planned for.",
     "The town's population is twice what it was ten years ago.",
     "Every sailing of the ferry is now completely unsafe to travel on.",
     "The ferry now runs many more sailings than it did ten years ago.",
     "A fixed timetable and a doubled population are the two reasons. The crowding on "
     "each sailing is what they are offered to establish."),
    ("Museums that charge no entry fee report far higher visitor numbers than those that "
     "do. Those same museums report much lower income from ticket sales.",
     "Free entry brings museums crowds but not takings.",
     "Museums with no entry fee report far higher visitor numbers.",
     "No museum anywhere should ever charge a fee for entry.",
     "Free entry brings museums both crowds and takings.",
     "Each statement reports a measurement. The conclusion is the trade-off the two "
     "measurements together point to."),
    ("Native gardens need far less watering than lawns do. Water restrictions are "
     "becoming more common across the state each summer.",
     "Native gardens are becoming the more practical choice for gardeners here.",
     "Native gardens need considerably less watering than lawns need.",
     "Lawns will disappear from the state entirely within a few years.",
     "Lawns are becoming the more practical choice for gardeners here.",
     "Lower water use and tighter restrictions are the reasons. That native gardens are "
     "becoming the sensible option is what those reasons support."),
    ("The bus route was changed to serve the new estate. Passengers from the old route "
     "now face a longer journey, and complaints to the council have risen sharply.",
     "The change has bought one group convenience at another group's expense.",
     "Passengers on the old route now face a longer journey than before.",
     "Bus routes should never be changed once they have been established.",
     "The change has made the journey shorter for everybody who uses the route.",
     "The longer journeys and the complaints are what happened. The trade between the "
     "two groups is the point being made about it."),
    ("Sea temperatures off this coast have risen by a degree in twenty years. The fish "
     "the local industry depends on will breed only in cooler water.",
     "The local fishery faces a difficulty that will not resolve itself.",
     "The fish the industry depends on breed only in cooler water.",
     "Every fishery in the country will be closed down before long.",
     "The local fishery's difficulty will resolve itself given time.",
     "The temperature and the breeding habits are two facts. Put together they are "
     "offered to show that the problem is a lasting one."),
    ("The school oval floods after heavy rain and takes three days to dry out. Sport is "
     "cancelled whenever the oval cannot be used, and rain has fallen in eight of the "
     "last ten weeks.",
     "Sport has been called off far more often than usual this term.",
     "The oval takes three days to dry out once it has flooded.",
     "Sport will never be played on that oval again at any point.",
     "Sport has run more regularly than usual over this term.",
     "Three separate facts about the oval, the rule and the weather are given. What "
     "they add up to is the number of cancellations."),
    ("The reading app was designed for phones with large screens. Most of the students "
     "who use it have older phones with small ones.",
     "The app is hardest to use for the very students it was built to help.",
     "Most students using the app have older phones with small screens.",
     "Nobody at all is able to use the reading app on any phone.",
     "The app suits the students who use it particularly well.",
     "The design and the phones the students own are the two facts. The mismatch "
     "between them is the point the argument exists to make."),
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
        expl=_expl, difficulty="hard" if _i % 3 else "medium",
        confidence=0.90 if _i % 3 else 0.92)

# ===================================================== correlation vs causation (10)

# (type, correlation, non-causal explanation, causal claim, restatement, irrelevance, expl)
LINKS = [
    ("common_cause",
     "Across Victorian towns, the more ice creams sold in a week, the more people are "
     "treated for sunburn that week.",
     "Hot sunny weather drives up ice cream sales and sends people outdoors for longer.",
     "Something in ice cream makes skin more likely to burn in the sun.",
     "Weeks with high ice cream sales are the weeks with many sunburn cases.",
     "Ice cream is now sold in a far wider range of flavours than it once was.",
     "The weather sits behind both figures and moves them together without either "
     "touching the other. Neither the ice cream nor the sunburn is doing anything to "
     "its partner."),
    ("reverse_cause",
     "Schools with more teacher aides report more students with learning difficulties.",
     "Schools take on extra aides because they already have students who need them.",
     "Having extra aides in the room causes learning difficulties in students.",
     "The schools reporting the most students with difficulties have the most aides.",
     "Teacher aides are employed on a different award from classroom teachers.",
     "The link runs the other way from the one it appears to. The need comes first and "
     "the staffing follows it, so the aides are a response rather than a cause."),
    # the shoe-size-and-reading version of this is a textbook example rather than an
    # invented one, and lr_finalise bans it by name
    ("common_cause",
     "In coastal towns, the months with the highest umbrella sales are also the months "
     "with the most reported falls on footpaths.",
     "Wet weather both sends people out to buy umbrellas and leaves the footpaths slippery.",
     "Carrying an umbrella about makes a person more likely to slip and fall over.",
     "Months with the highest umbrella sales record the most falls on footpaths.",
     "Umbrellas are stocked by hardware shops as well as by department stores.",
     "The rain sits behind both counts and lifts them together. In a dry month both "
     "would fall away, without either having acted on the other at all."),
    ("selection",
     "People who go to the gym regularly report fewer colds than people who do not.",
     "Anyone already coming down with something stays home instead of going.",
     "Exercise at a gym prevents people from catching colds.",
     "Regular gym-goers report catching fewer colds than other people do.",
     "Most gyms open at half past five in the morning on weekdays.",
     "The group being counted was assembled by the very thing being measured. Illness "
     "keeps people out of the gym, so the healthy end up in the counted group."),
    ("reverse_cause",
     "Suburbs with more police officers on duty record more crimes each year.",
     "Officers are posted in larger numbers to the suburbs that already have high crime.",
     "The presence of police officers in a suburb causes crime to happen there.",
     "The suburbs recording the most crime are the ones with the most officers.",
     "Police vehicles are replaced on a rolling five-year cycle across the state.",
     "The staffing decision is made after the crime figures are known, so the crime is "
     "the reason for the police rather than the result of them."),
    ("common_cause",
     "Children from homes with more books on the shelves do better at school.",
     "Families who value education both buy books and sit down to help with homework.",
     "Owning a large number of books directly improves a child's school results.",
     "Children in homes with more books achieve better results at school.",
     "Bookshelves are among the most common items bought at second-hand markets.",
     "The books and the results are two signs of the same thing. What the family does "
     "about learning produces both, and moving books into a house would not carry the "
     "rest across."),
    ("coincidence",
     "Over the last decade the number of pirate films released each year rose, and so "
     "did the average price of butter.",
     "Two unrelated things can both rise across the same decade by chance.",
     "The release of pirate films pushes up the price of butter.",
     "Both pirate film releases and butter prices climbed over the last ten years.",
     "Butter is graded by fat content before it is packed for sale.",
     "Anything that drifts upward over ten years will match anything else that does. "
     "There is no mechanism linking the two, and none is needed to explain the shape."),
    ("selection",
     "Patients treated at the state's largest hospital have lower survival rates than "
     "patients at small country hospitals.",
     "The most seriously ill patients are sent on to the largest hospital for treatment.",
     "Being treated at a large hospital lowers a patient's chance of survival.",
     "Survival rates at the largest hospital are below those at small country hospitals.",
     "The largest hospital was extended with a new wing about six years ago.",
     "The two hospitals are not treating the same patients. The referral system loads "
     "the hardest cases onto one of them, which drags its figures down."),
    ("coincidence",
     "Over twenty years the number of mobile phone towers in the state has risen, and "
     "so has the average age of the population.",
     "The population would have aged over those years whatever the towers had done.",
     "Living near mobile phone towers causes people to live longer.",
     "Mobile phone towers and the average age have both risen over twenty years.",
     "Phone towers are usually leased to more than one carrier at a time.",
     "The ageing has its own causes — longer lives and smaller families — and they were "
     "running before the first tower went up. Putting the two counts side by side adds "
     "nothing to either."),
    ("reverse_cause",
     "Restaurants that roster more staff on a Saturday night take more money that night.",
     "Managers put on extra staff for the nights they already expect to be busy.",
     "Putting extra staff on a shift causes customers to spend more money.",
     "The restaurants taking the most money are the ones with the most staff rostered.",
     "Most restaurants in the area take their last booking at about nine o'clock.",
     "The roster is written days before the customers arrive, using what the manager "
     "expects. The expected trade explains the staffing, not the other way round."),
]

_types = collections.Counter(t for t, *_ in LINKS)
if len(_types) < 4 or max(_types.values()) > 3:
    raise AssertionError(
        f"the ten keys fall as {dict(_types)} — spread them across all four ways a link "
        f"can arise, or students learn to answer the question type instead of the question")

for _i, (_type, _corr, _key, _causal, _restate, _irrel, _expl) in enumerate(LINKS):
    _label = _corr[:44]
    must_restate(_restate, _corr, f"{_label} [restatement]")
    must_assert_cause(_causal, f"{_label} [causal claim]")
    must_balance([_key, _causal, _restate, _irrel], _label)
    B.Q("correlation_vs_causation",
        f"{_corr} Which one of these best explains the link, without one of the two "
        f"causing the other?",
        key=_key, verify=_key,
        wrong=[_causal, _restate, _irrel],
        expl=_expl, difficulty="hard" if _i % 3 else "medium",
        confidence=0.90 if _i % 3 else 0.92)

B.write()
