#!/usr/bin/env python3
"""Builds rc_nsw_multi_p1.json — 4 sets x 4 items = 16 answer slots (§3.5).

Multi-extract synthesis: three short related texts, and questions about which text
supports what. Shares the machinery in tools/rc/paired_common.py — a set is one `passage`
holding labelled extracts — with `min_cross_extract` raised from 2 to 3, because synthesis
IS the skill here: "which text best supports this conclusion" cannot be answered from one
extract, so a set with only two crossing items is a single-passage set carrying two spare
texts.

Each set deliberately mixes an evidence type, a constraint and a voice — research beside a
bus timetable beside a student survey; survey counts beside a disease explainer beside a
landholder. That is what makes synthesis necessary rather than decorative: no single text
settles the question, and the texts do not simply agree.

Figures inside a text are the text's own (a school survey, a clean-up tally) and are never
attributed to a real named body. Two earlier batches had to be corrected for exactly that.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.rc.paired_common import build  # noqa: E402

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/reading_comprehension/generated"
NN = 1
BOOK = "rc_nsw_multi"
CATEGORY = "multi_extract"
LABEL = "Multi-extract synthesis"
ALL = ["Text 1", "Text 2", "Text 3"]

# item = (skill, difficulty, confidence, uses, quote_refs, stem, key, distractors, expl)
PASSAGES = [
 {
  "title": "Later Start",
  "topic": "School",
  "extracts": [
    ("Text 1", [
      "Between the ages of about twelve and eighteen, the body clock shifts later by "
      "roughly two hours.",
      "A teenager who cannot fall asleep before eleven is not being difficult; the timing "
      "is biological.",
      "Schools that have moved their start to half past eight report fewer late arrivals "
      "and better attendance.",
      "The effect on marks is smaller and less consistent than the effect on attendance.",
    ]),
    ("Text 2", [
      "School services in this district share buses with the general morning timetable.",
      "A start later than half past eight would require six additional vehicles.",
      "The company has no objection in principle to a change of fifteen or twenty minutes.",
      "A change of a full hour would need to be funded, and we would need eighteen "
      "months' notice.",
    ]),
    ("Text 3", [
      "Of 214 students surveyed, sixty-eight per cent said they would use extra morning "
      "time to sleep.",
      "Twenty-two per cent said they would use it for homework.",
      "Ninety-one per cent said they had fallen asleep in class at least once this term.",
      "Asked whether they would accept a later finish, fifty-five per cent said no.",
    ]),
  ],
  "items": [
    ("detail", "medium", 0.93, ["Text 1"], [(0, 3)],
     'Text 1 states: "{q}" This tells the reader that a later start —',
     "helps attendance more reliably than it helps results",
     [("improves marks more than it improves attendance", "contradicts"),
      ("has never actually been studied in real schools", "unsupported"),
      ("guarantees better results for every single student", "overreach")],
     "Smaller and less consistent puts the effect on marks below the effect on "
     "attendance. Improves marks more than it improves attendance reverses the "
     "comparison the sentence makes."),

    ("comparison", "medium", 0.92, ALL, [],
     'Which text gives the strongest reason to keep the change small?',
     "Text 2, because a larger change needs six more buses and funding",
     [("Text 1, because the body clock shifts by about two hours", "contradicts"),
      ("Text 3, because most students would use the time to sleep", "wrong_focus"),
      ("Text 3, because more than half of them would refuse a later finish anyway", "half_right")],
     "Only the bus operator names a cost that grows with the size of the change. Text 1, "
     "because the body clock shifts by about two hours is an argument for a larger change, "
     "not a smaller one."),

    ("main_idea", "medium", 0.92, ALL, [],
     'Taken together, what do the three texts establish?',
     "that a later start would help, but its size is limited by cost",
     [("that a later start would make no difference to anybody", "contradicts"),
      ("that the decision belongs to the bus company alone", "overreach"),
      ("that sleep research has already settled the whole question completely", "unsupported")],
     "One text gives the benefit, one gives the constraint, and the third shows students "
     "want it. That a later start would make no difference to anybody is contradicted by "
     "the attendance findings in the first text."),

    ("comparison", "hard", 0.90, ALL, [],
     'Which text shows that the student survey on its own cannot settle the question?',
     "Text 2, because wanting a change does not pay for the buses",
     [("Text 1, because the body clock shifts later in teenagers", "contradicts"),
      ("Text 3, because ninety-one per cent had fallen asleep in class", "wrong_focus"),
      ("Text 1, because the effect on marks is small and inconsistent", "half_right")],
     "A survey measures what students want; the timetable text measures what it would "
     "take. Text 1, because the body clock shifts later in teenagers supports the survey "
     "rather than limiting it."),
  ],
 },
 {
  "title": "The Quiet Creek",
  "topic": "Science",
  "extracts": [
    ("Text 1", [
      "Frog surveys have been run on Boggy Creek every October since 2011.",
      "In the first five years the average count was forty-one calling males across six "
      "sites.",
      "Since 2019 the average has been nine.",
      "Two species recorded in 2011 have not been heard at all since 2018.",
    ]),
    ("Text 2", [
      "Chytrid is a fungus that attacks the skin of frogs, and frogs breathe partly "
      "through their skin.",
      "It spreads in water and on wet equipment, including boots and nets.",
      "Cool, moist highland streams are where outbreaks have been worst.",
      "Some populations recover; many do not.",
    ]),
    ("Text 3", [
      "We put in the second dam in 2017 and the creek below it has run lower ever since.",
      "There were frogs in the reeds every spring when the children were small.",
      "I could not tell you when they stopped.",
      "The reeds are still there.",
    ]),
  ],
  "items": [
    ("detail", "medium", 0.93, ["Text 1"], [(0, 1), (0, 2)],
     'Text 1 records: "{q}" What has happened to the count?',
     "it has fallen to about a fifth of what it was",
     [("it has stayed steady since the surveys began", "contradicts"),
      ("nine different species were counted across the sites", "wrong_focus"),
      ("frogs have vanished from every creek in the region", "overreach")],
     "Forty-one down to nine is a fall of roughly four fifths. Nine different species "
     "were counted across the sites misreads a count of calling males as a count of "
     "species."),

    ("comparison", "medium", 0.92, ["Text 1", "Text 2"], [],
     'Which detail in Text 2 makes the fungus a plausible explanation for Text 1?',
     "that outbreaks have been worst in cool, moist streams",
     [("that the fungus can spread on wet boots, nets and other equipment", "half_right"),
      ("that frogs breathe partly through their skin", "wrong_focus"),
      ("that some affected populations do recover", "contradicts")],
     "A creek is exactly the habitat the fungus does most damage in, which is what makes "
     "it fit this case. That the fungus spreads on wet boots and nets explains how it "
     "travels, not why this creek would suffer."),

    ("main_idea", "medium", 0.92, ALL, [],
     'What do the three texts together suggest about the decline?',
     "that more than one cause is possible and neither is ruled out",
     [("that the fungus is certainly the only cause of it", "overreach"),
      ("that the surveys have already identified the cause", "contradicts"),
      ("that the landholder is the one to blame for everything that happened", "unsupported")],
     "The surveys show the fall, the fungus offers one explanation and the dam offers "
     "another, with nothing choosing between them. That the surveys have already "
     "identified the cause is not something a count of calling males can do."),

    ("comparison", "hard", 0.90, ALL, [],
     'Text 3 never mentions the fungus. Why does it still matter?',
     "because it dates a change in the creek to about the right time",
     [("because it proves the fungus was not involved at all", "overreach"),
      ("because it shows that the reeds have disappeared", "contradicts"),
      ("because it counts the frogs far more carefully than the surveys in Text 1", "unsupported")],
     "A dam in 2017 and lower water ever since sits alongside a collapse recorded from "
     "2018 and 2019. Because it shows that the reeds have disappeared is the opposite of "
     "the last line, which says they are still there."),
  ],
 },
 {
  "title": "What Reaches the Bay",
  "topic": "Environment",
  "extracts": [
    ("Text 1", [
      "Volunteers collected 4,180 items from the foreshore over one weekend in March.",
      "Soft plastic fragments made up just under half of the total.",
      "Bottle caps, straws and cigarette filters together made up another third.",
      "Only six per cent of items could be identified as coming from a boat.",
    ]),
    ("Text 2", [
      "Anything smaller than a credit card falls through the sorting machinery at the "
      "recycling plant.",
      "Small items placed loose in the yellow bin are therefore treated as waste.",
      "Soft plastics cannot be recycled in a kerbside bin anywhere in this state.",
      "Please place soft plastics in the red bin, not the yellow one.",
    ]),
    ("Text 3", [
      "Most of what ends up in the bay does not arrive by boat, or from the beach itself.",
      "It arrives through the stormwater drains, which carry whatever is on the street "
      "when it rains.",
      "A wrapper dropped three kilometres inland can be in the water within an hour of a "
      "storm.",
      "Street cleaning is therefore a marine issue, which is not how councils are usually "
      "organised.",
    ]),
  ],
  "items": [
    ("detail", "medium", 0.93, ["Text 1"], [(0, 3)],
     'The clean-up tally records: "{q}" This tells the reader that —',
     "most of the rubbish did not come from boats",
     [("most of the rubbish was thrown from passing boats", "contradicts"),
      ("six per cent of the rubbish was left on the beach", "wrong_focus"),
      ("no rubbish at all arrived in the bay from a boat", "overreach")],
     "Six per cent from boats leaves ninety-four per cent from somewhere else. No rubbish "
     "at all arrived in the bay from a boat turns a small share into none."),

    ("comparison", "medium", 0.92, ["Text 1", "Text 3"], [],
     'Which text explains how the items counted in Text 1 reached the foreshore?',
     "Text 3, by way of the stormwater drains",
     [("Text 2, by way of the kerbside recycling bin", "wrong_focus"),
      ("Text 3, by being dropped on the beach itself", "contradicts"),
      ("Text 2, because small items fall through the sorting", "half_right")],
     "Only the third text traces a route from the street to the water. Text 3, by being "
     "dropped on the beach itself is ruled out by that text's own first sentence."),

    ("main_idea", "medium", 0.92, ALL, [],
     'Taken together, what do the three texts imply about reducing rubbish in the bay?',
     "that inland streets matter as much as the beach itself",
     [("that beach clean-ups on their own will solve the problem", "contradicts"),
      ("that the recycling plant is the main source of the rubbish", "unsupported"),
      ("that nothing can be done about soft plastics at all", "overreach")],
     "The rubbish is mostly soft plastic, mostly not from boats, and mostly arrives down "
     "the drains. That beach clean-ups on their own will solve the problem is exactly "
     "what the third text rules out."),

    ("comparison", "hard", 0.90, ALL, [],
     'A councillor proposes more bins along the foreshore. Which text most challenges '
     'that as a solution?',
     "Text 3, because most of the rubbish is not dropped there",
     [("Text 1, because soft plastic fragments were half the total", "wrong_focus"),
      ("Text 2, because soft plastics cannot go in a yellow bin", "half_right"),
      ("Text 1, because volunteers already collect the rubbish", "unsupported")],
     "Bins on the foreshore can only catch what is dropped on the foreshore, and the "
     "third text says most of it is not. Text 2, because soft plastics cannot go in a "
     "yellow bin is about which bin, not about where the rubbish comes from."),
  ],
 },
 {
  "title": "Feeding the Birds",
  "topic": "Australian Wildlife",
  "extracts": [
    ("Text 1", [
      "We take in magpies and lorikeets every summer with soft, brittle bones.",
      "Almost all of them come from streets where somebody puts out mince or bread.",
      "Mince has no calcium in it and bread has almost nothing a bird needs.",
      "A bird that fills up on either will not go looking for the food that would keep it "
      "well.",
    ]),
    ("Text 2", [
      "Of 300 households surveyed, thirty-seven per cent said they put food out for birds "
      "at least weekly.",
      "Of those, sixty per cent used bread, mince, or seed mixes sold for pet parrots.",
      "Ninety-four per cent said they did it because they enjoyed watching the birds.",
      "Only four per cent had ever been told that it might cause harm.",
    ]),
    ("Text 3", [
      "Feeding does not usually kill birds outright; it changes which birds are there.",
      "Species that can exploit a reliable handout crowd out species that cannot.",
      "In suburbs with heavy feeding, the number of species falls while the number of "
      "birds rises.",
      "A garden can be full of birds and much poorer than it looks.",
    ]),
  ],
  "items": [
    ("inference", "medium", 0.93, ["Text 1"], [(0, 3)],
     'The wildlife carer writes: "{q}" The harm described here comes from —',
     "what the bird then stops going out to eat",
     [("the mince and the bread being poisonous", "overreach"),
      ("birds refusing to eat mince or bread", "contradicts"),
      ("there being no other food anywhere nearby", "unsupported")],
     "The damage is done by the meal that is skipped, not by the meal that is eaten. The "
     "mince and the bread being poisonous is stronger than a text whose complaint is that "
     "they contain nothing useful."),

    ("comparison", "medium", 0.92, ["Text 1", "Text 2"], [],
     'Which figure in Text 2 best explains why the problem in Text 1 continues?',
     "that only four per cent had ever been told it might do harm",
     [("that thirty-seven per cent feed birds at least weekly", "half_right"),
      ("that ninety-four per cent enjoy watching the birds", "wrong_focus"),
      ("that most households feed birds in order to harm them", "contradicts")],
     "People cannot stop doing something they have never been told is a problem. That "
     "thirty-seven per cent feed birds at least weekly measures how common it is, not why "
     "it goes on."),

    ("main_idea", "medium", 0.92, ALL, [],
     'What do the three texts together suggest about feeding birds in gardens?',
     "that it is meant kindly and does harm people cannot see",
     [("that it is done deliberately to reduce the species count", "contradicts"),
      ("that it should be made illegal in every Australian suburb", "overreach"),
      ("that the birds involved would be better off in the bush", "unsupported")],
     "Ninety-four per cent do it for pleasure, four per cent have been warned, and the "
     "loss is in species rather than in birds. That it is done deliberately to reduce the "
     "species count reverses the intention every text describes."),

    ("comparison", "hard", 0.90, ALL, [],
     'Text 3 says a garden can be full of birds and much poorer than it looks. Which '
     'other text most supports that?',
     "Text 2, because people judge the feeding by how many birds they see",
     [("Text 1, because the birds arrive with soft, brittle bones", "half_right"),
      ("Text 2, because thirty-seven per cent feed birds weekly", "wrong_focus"),
      ("Text 1, because feeding the birds kills them outright in the end", "contradicts")],
     "Ninety-four per cent feed birds for the pleasure of watching them, which is a "
     "judgement made on birds seen rather than on species present. Text 1, because the "
     "birds arrive with soft, brittle bones describes harm that is plainly visible, "
     "which is the opposite of harm a garden hides."),
  ],
 },
]


if __name__ == "__main__":
    GEN.mkdir(parents=True, exist_ok=True)
    qs = build(PASSAGES, BOOK, NN, CATEGORY, LABEL)
    path = GEN / f"{BOOK}_p{NN}.json"
    path.write_text(json.dumps(qs, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(qs)} questions across {len(PASSAGES)} sets -> {path}")
