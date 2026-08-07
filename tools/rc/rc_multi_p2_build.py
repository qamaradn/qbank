#!/usr/bin/env python3
"""Builds rc_nsw_multi_p2.json — 4 sets x 4 items = 16 answer slots (§3.5).

Second synthesis batch. Sets not used by p1 (school start times, frog surveys, rubbish in
the bay, feeding birds): dogs on a nesting beach, solar panels on a school roof, a beach
that is narrowing, and a canteen that cannot follow its own guideline.

The synthesis stems are deliberately phrased four different ways. "Taken together, what do
the three texts establish?" is the natural sentence for every one of these items, and four
copies of it would score above phase 4's silent 0.85 near-duplicate threshold — which is
exactly how paired p2 nearly lost three questions.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.rc.paired_common import build  # noqa: E402

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/reading_comprehension/generated"
NN = 2
BOOK = "rc_nsw_multi"
CATEGORY = "multi_extract"
LABEL = "Multi-extract synthesis"
ALL = ["Text 1", "Text 2", "Text 3"]

# item = (skill, difficulty, confidence, uses, quote_refs, stem, key, distractors, expl)
PASSAGES = [
 {
  "title": "Dogs on the Beach",
  "topic": "Environment",
  "extracts": [
    ("Text 1", [
      "Dogs are permitted off-lead on the northern beach between April and August.",
      "From September to March the northern beach is closed to dogs entirely.",
      "The southern beach is open to dogs on-lead all year round.",
      "Fines apply, and rangers patrol the northern beach on weekends during the closure.",
    ]),
    ("Text 2", [
      "Hooded plovers nest directly on the open sand, above the high tide line, from "
      "September onwards.",
      "The eggs are the colour of the sand and are almost impossible to see.",
      "A nest does not have to be stepped on to fail: a bird kept off its eggs for twenty "
      "minutes in the sun will lose them.",
      "A dog does not have to catch anything to do damage.",
    ]),
    ("Text 3", [
      "Of 180 dog owners surveyed, seventy-one per cent said they use the northern beach "
      "at least weekly in summer.",
      "Of those, forty per cent believed the closure applied only to the school holidays.",
      "Eighty-eight per cent said they would use the southern beach if it had shade and "
      "drinking water.",
      "Only nine per cent had ever spoken to a ranger.",
    ]),
  ],
  "items": [
    ("detail", "medium", 0.93, ["Text 1"], [(0, 1)],
     'Text 1 states: "{q}" This means that dogs —',
     "are banned there through the warmer half of the year",
     [("may use the northern beach off-lead all year round", "contradicts"),
      ("are barred from the southern beach over the same months", "wrong_focus"),
      ("have never once been taken onto that beach in summer", "overreach")],
     "September to March covers spring and summer, and the ban is total. May use the "
     "northern beach off-lead all year round describes the northern beach outside those "
     "months only."),

    ("comparison", "medium", 0.92, ["Text 1", "Text 2"], [],
     'Which fact in Text 2 explains why the closure begins in September?',
     "hooded plovers start nesting on the open sand then",
     [("the eggs are exactly the same colour as the sand", "half_right"),
      ("a dog does not have to catch anything to do harm", "wrong_focus"),
      ("the birds make their nests below the high tide line", "contradicts")],
     "The closure and the nesting season begin in the same month, which is the whole "
     "reason for the date. The eggs are exactly the same colour as the sand explains why "
     "nests are missed, not why September."),

    ("main_idea", "medium", 0.92, ALL, [],
     'What is the main problem that the three texts point to between them?',
     "many owners do not know when the closure actually applies",
     [("the rules themselves are not nearly strict enough", "unsupported"),
      ("the plovers have started nesting on the southern beach", "contradicts"),
      ("dog owners are disturbing the nests on purpose", "overreach")],
     "Forty per cent of frequent users think the ban is a school-holiday rule, and nine "
     "per cent have ever met a ranger. The rules themselves are not nearly strict enough "
     "is not something any of the three texts claims."),

    ("comparison", "hard", 0.90, ALL, [],
     'Which text points to a change that would move dogs without more fines?',
     "Text 3, because most owners would use the southern beach if it had shade and water",
     [("Text 1, because rangers already patrol there on weekends", "wrong_focus"),
      ("Text 2, because a nest can fail without ever once being stepped on by anything", "half_right"),
      ("Text 3, because only nine per cent have spoken to a ranger", "unsupported")],
     "Eighty-eight per cent naming two missing facilities is an offer of a solution that "
     "needs no enforcement. Text 1, because rangers already patrol there on weekends is "
     "more enforcement, which is what the question rules out."),
  ],
 },
 {
  "title": "The Solar Panels",
  "topic": "Technology",
  "extracts": [
    ("Text 1", [
      "The school used 214,000 kilowatt hours of electricity last year.",
      "Sixty-two per cent of that was used between nine and three on weekdays.",
      "The single largest use was air conditioning between September and March.",
      "The annual bill was the second largest item in the school's operating budget.",
    ]),
    ("Text 2", [
      "A rooftop system generates most of its power in the middle of the day.",
      "Power that is generated and used on site is worth about four times as much as "
      "power sold back to the grid.",
      "The roof space available here would support a system covering roughly forty per "
      "cent of daytime use.",
      "Panels have no moving parts and generally need cleaning rather than repair.",
    ]),
    ("Text 3", [
      "A screen in the foyer showing live generation would be used in Year 5 and Year 6 "
      "maths every week.",
      "Students could compare a cloudy day with a clear one and work out the difference "
      "themselves.",
      "The panels would make the electricity bill visible, which it is not at present to "
      "anybody under eighteen.",
      "I would want the screen whether or not the system paid for itself.",
    ]),
  ],
  "items": [
    ("detail", "medium", 0.93, ["Text 1"], [(0, 1)],
     'Text 1 reports: "{q}" This tells the reader that —',
     "most of the school's power goes during the school day",
     [("most of the school's power is used overnight instead", "contradicts"),
      ("the school used 62,000 kilowatt hours over the year", "wrong_focus"),
      ("the school uses no electricity at all on a weekend", "overreach")],
     "Nine until three on weekdays is the school day, and it takes nearly two thirds of "
     "the total. The school used 62,000 kilowatt hours over the year reads a percentage "
     "as though it were the amount."),

    ("comparison", "medium", 0.92, ["Text 1", "Text 2"], [],
     'Why does the timing reported in Text 1 matter to the argument in Text 2?',
     "because power used on site is worth far more than power sold back",
     [("because the panels need cleaning rather than any repair", "wrong_focus"),
      ("because the roof could support a very much larger system", "contradicts"),
      ("because the electricity bill is a large item in the school's yearly budget", "half_right")],
     "The school uses its power exactly when a roof generates it, so almost none would "
     "have to be sold back. Because the roof could support a very much larger system "
     "contradicts a text that puts the ceiling at forty per cent of daytime use."),

    ("main_idea", "medium", 0.92, ALL, [],
     'What case do the three texts make when read as a group?',
     "a system sized to daytime use, with a display for teaching",
     [("a system large enough to sell most of its power to the grid", "contradicts"),
      ("no system at all, because the roof space is far too small", "unsupported"),
      ("a display screen in the foyer instead of any panels at all", "overreach")],
     "The usage pattern, the four-to-one value of on-site power and the teaching case all "
     "point the same way. A system large enough to sell most of its power to the grid "
     "throws away the advantage the second text identifies."),

    ("comparison", "hard", 0.90, ALL, [],
     'Which text makes a case that does not depend on money at all?',
     "Text 3, because the writer wants the screen either way",
     [("Text 1, because the bill is a large part of the budget", "contradicts"),
      ("Text 2, because the panels have no moving parts to break", "wrong_focus"),
      ("Text 3, because the system would pay for itself very quickly", "unsupported")],
     "The last sentence of the third text says so outright: the screen is wanted whether "
     "or not it pays. Text 3, because the system would pay for itself very quickly is a "
     "money argument, and no text makes it."),
  ],
 },
 {
  "title": "The Shrinking Beach",
  "topic": "Science",
  "extracts": [
    ("Text 1", [
      "The beach at Cutler Point has been measured from the same six markers since 1998.",
      "Between 1998 and 2012 the average width at high tide was fifty-one metres.",
      "Between 2013 and 2024 the average was thirty-four metres.",
      "Two of the six markers now stand in water at every high tide.",
    ]),
    ("Text 2", [
      "Sand does not disappear; it moves, and along this coast it moves north.",
      "A beach narrows when the sand leaving it is not replaced by sand arriving from the "
      "south.",
      "Groynes, harbour walls and river training works all interrupt that supply.",
      "The breakwater built south of Cutler Point in 2011 traps sand that once passed it.",
    ]),
    ("Text 3", [
      "The club has run the same nippers course on this beach since 1974.",
      "In the 1990s the course was set out in three lanes across the dry sand.",
      "Since 2015 it has been run in two lanes, and in 2023 the club moved it to the "
      "point.",
      "Nobody voted on any of that; the beach decided it.",
    ]),
  ],
  "items": [
    ("detail", "medium", 0.93, ["Text 1"], [(0, 1), (0, 2)],
     'Text 1 records: "{q}" What has happened to the beach?',
     "it is about a third narrower than it used to be",
     [("it has grown steadily wider since about 2013", "contradicts"),
      ("thirty-four separate markers were used in the survey", "wrong_focus"),
      ("it will have disappeared entirely within a decade", "overreach")],
     "Fifty-one metres down to thirty-four is a loss of roughly a third. Thirty-four "
     "separate markers were used in the survey reads a width in metres as a count of "
     "markers."),

    ("comparison", "medium", 0.92, ["Text 1", "Text 2"], [],
     'Which fact in Text 2 best explains the change measured in Text 1?',
     "the breakwater built south of the point in 2011",
     [("that sand generally moves north along this coast", "half_right"),
      ("that sand does not disappear but only ever moves", "wrong_focus"),
      ("that no sand at all now arrives at this beach", "contradicts")],
     "The breakwater goes in in 2011 and the measured drop begins in 2013, which is the "
     "only dated link on offer. That sand generally moves north along this coast is the "
     "background the explanation rests on, not the cause."),

    ("main_idea", "medium", 0.92, ALL, [],
     'Between them, the three texts provide —',
     "a measured loss, a likely cause, and the effect on people",
     [("a loss that nobody has managed to measure properly", "contradicts"),
      ("a cause that has now been proved beyond any doubt", "overreach"),
      ("an effect on the wildlife of the point rather than on the people there", "wrong_focus")],
     "The markers measure it, the breakwater explains it, and the nippers course records "
     "what it cost. A cause that has now been proved beyond any doubt is more than a "
     "matching pair of dates can establish."),

    ("comparison", "hard", 0.90, ALL, [],
     'Text 3 contains no measurements. What does it contribute?',
     "evidence of the change from the people who use the beach",
     [("the exact width of the beach during the 1990s", "contradicts"),
      ("the reason the breakwater was built back in 2011", "unsupported"),
      ("proof that the surf club itself caused the sand to move away", "overreach")],
     "Three lanes becoming two, and then no lanes at all, is the loss measured in what "
     "the beach can still be used for. The exact width of the beach during the 1990s is "
     "in the first text, and the third gives no figures at all."),
  ],
 },
 {
  "title": "The Canteen",
  "topic": "Health",
  "extracts": [
    ("Text 1", [
      "School canteens are asked to sort items into three groups: everyday, select "
      "carefully, and occasional.",
      "Everyday items should make up at least half of the menu.",
      "Occasional items may be sold no more than twice a term.",
      "The guideline is advisory; it is not enforced by any inspection.",
    ]),
    ("Text 2", [
      "Sausage rolls accounted for thirty-one per cent of all items sold last term.",
      "Sandwiches and salads together accounted for nineteen per cent.",
      "The three highest-selling items were all in the occasional group.",
      "Takings finished four hundred dollars above the canteen's break-even point.",
    ]),
    ("Text 3", [
      "We are three volunteers and one paid supervisor for four hundred students.",
      "Sandwiches have to be made in the morning and thrown out if they do not sell.",
      "Sausage rolls come frozen, cook in twenty minutes, and never go to waste.",
      "I know exactly what the guideline says, and I would need two more people to follow "
      "it.",
    ]),
  ],
  "items": [
    ("detail", "medium", 0.93, ["Text 1"], [(0, 3)],
     'Text 1 states: "{q}" This means that —',
     "nobody checks whether a canteen follows it",
     [("the guideline is a legal requirement for every canteen", "contradicts"),
      ("the guideline applies only to the occasional group", "wrong_focus"),
      ("no canteen anywhere in the state follows the guideline", "overreach")],
     "Advisory and uninspected together mean there is no check. The guideline is a legal "
     "requirement for every canteen is the opposite of advisory."),

    ("comparison", "medium", 0.92, ["Text 1", "Text 2"], [],
     'What do the sales figures in Text 2 show about the guideline in Text 1?',
     "the menu is selling in the reverse of the recommended proportions",
     [("the canteen sells no items from the occasional group at all", "contradicts"),
      ("sandwiches outsell every other item on the whole menu", "wrong_focus"),
      ("the guideline has since been withdrawn by the state altogether", "unsupported")],
     "Everyday items are meant to be at least half; here the top three sellers are all "
     "occasional. The canteen sells no items from the occasional group at all is denied "
     "by the sausage roll figure in the first line."),

    ("main_idea", "medium", 0.92, ALL, [],
     'What does the combination of these three texts explain?',
     "why a canteen can know the guideline and still not meet it",
     [("why the guideline ought to be abolished altogether", "overreach"),
      ("why the canteen deliberately ignores nutrition advice", "contradicts"),
      ("why sausage rolls cost a canteen less to buy in than sandwiches do", "wrong_focus")],
     "The rule exists, the sales break it, and the staffing explains why. Why the canteen "
     "deliberately ignores nutrition advice is ruled out by a volunteer who says she "
     "knows exactly what the guideline says."),

    ("comparison", "hard", 0.90, ALL, [],
     'Which text identifies the thing that would have to change first?',
     "Text 3, because the menu is limited by how many people work there",
     [("Text 1, because the guideline is only ever advisory and never inspected", "half_right"),
      ("Text 2, because the canteen finished above break-even", "wrong_focus"),
      ("Text 3, because the volunteers do not know the guideline", "contradicts")],
     "Two more pairs of hands is the condition the volunteer names for following the "
     "rule. Text 3, because the volunteers do not know the guideline contradicts the very "
     "sentence it claims to rest on."),
  ],
 },
]


if __name__ == "__main__":
    GEN.mkdir(parents=True, exist_ok=True)
    qs = build(PASSAGES, BOOK, NN, CATEGORY, LABEL)
    path = GEN / f"{BOOK}_p{NN}.json"
    path.write_text(json.dumps(qs, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(qs)} questions across {len(PASSAGES)} sets -> {path}")
