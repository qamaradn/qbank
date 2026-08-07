#!/usr/bin/env python3
"""Builds rc_nsw_multi_p3.json — 5 sets x 4 items = 20 answer slots (§3.5).

Closes the type, and with it the four NSW Reading types that were entirely unbuilt:
4 + 4 + 5 sets = 13, 52 items.

Sets not used by p1 (school start, frogs, the bay, feeding birds) or p2 (dogs, solar
panels, the beach, the canteen): a rail trail, street lighting, a row of memorial elms,
reading on screens, and hazard reduction burning.

Every set is built so that no single text settles the question and the three do not simply
agree — a proposal against the person whose land it crosses against another town's
figures; an astronomer against a lighting specification against a turtle researcher. Where
the texts merely agreed, "which text best supports this" would have one obvious answer and
the synthesis would be decorative.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.rc.paired_common import build  # noqa: E402

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/reading_comprehension/generated"
NN = 3
BOOK = "rc_nsw_multi"
CATEGORY = "multi_extract"
LABEL = "Multi-extract synthesis"
ALL = ["Text 1", "Text 2", "Text 3"]

# item = (skill, difficulty, confidence, uses, quote_refs, stem, key, distractors, expl)
PASSAGES = [
 {
  "title": "The Rail Trail",
  "topic": "Community",
  "extracts": [
    ("Text 1", [
      "The disused line between Kellerton and Ward's Crossing has carried no train since "
      "1987.",
      "The proposal is to surface twenty-two kilometres of it as a shared walking and "
      "cycling trail.",
      "The corridor is already public land; no acquisition is required.",
      "Construction is costed at 4.1 million dollars, with maintenance estimated at "
      "90,000 dollars a year.",
    ]),
    ("Text 2", [
      "The line runs through the middle of our place for two and a half kilometres.",
      "We have crossed it with stock twice a day since the trains stopped.",
      "Nobody has explained how that works once there are cyclists on it.",
      "I am not against the trail; I am against finding out about the gates after it is "
      "built.",
    ]),
    ("Text 3", [
      "The Willow Creek trail opened in 2016 and is thirty-one kilometres long.",
      "Counters record an average of 240 users a day, rising to 900 on a long weekend.",
      "Two cafes and a bike hire business have opened along the route since then.",
      "The shire reports that maintenance has cost more than the original estimate every "
      "year.",
    ]),
  ],
  "items": [
    ("detail", "medium", 0.93, ["Text 1"], [(0, 2)],
     'Text 1 states: "{q}" This means that —',
     "no land has to be bought for the trail to go ahead",
     [("the council must buy land from the farmers along the route", "contradicts"),
      ("the rail corridor was sold to the public back in 1987", "wrong_focus"),
      ("the trail would cross no private property anywhere at all", "overreach")],
     "Public land already in the council's hands needs no purchase. The trail would cross "
     "no private property anywhere at all goes further than the text supports, and the "
     "second text describes a farm the line runs straight through."),

    ("comparison", "medium", 0.92, ["Text 1", "Text 2"], [],
     'What does Text 2 raise that Text 1 leaves out entirely?',
     "how stock will cross the line once the trail is in use",
     [("the total length of the disused line in kilometres", "contradicts"),
      ("the yearly cost of maintaining the finished trail", "wrong_focus"),
      ("proof that the trail would never actually be used", "unsupported")],
     "The proposal covers surface, land and cost, and says nothing about a crossing used "
     "twice a day. The total length of the disused line in kilometres is given in the "
     "proposal itself."),

    ("main_idea", "medium", 0.92, ALL, [],
     'What conclusion do all three texts support?',
     "the trail would be used, and would cost more than planned",
     [("the trail would be used by almost nobody at all", "contradicts"),
      ("the trail ought to be built somewhere else entirely", "unsupported"),
      ("the trail would solve every problem in both towns", "overreach")],
     "The comparable trail carries 240 users a day and has overrun its maintenance "
     "estimate every year since opening. The trail would be used by almost nobody at all "
     "is the opposite of what the third text records."),

    ("comparison", "hard", 0.90, ALL, [],
     'Which text most complicates the cost figure given in Text 1?',
     "Text 3, because maintenance there has exceeded the estimate every year",
     [("Text 2, because the farmer is asking for gates to be built into the fence line", "half_right"),
      ("Text 3, because two cafes have opened along that route", "wrong_focus"),
      ("Text 1, because no land has to be bought for the corridor", "contradicts")],
     "A comparable trail overrunning its maintenance budget every year is direct evidence "
     "against the 90,000 dollar figure. Text 3, because two cafes have opened along that "
     "route is an argument for the trail, not a problem with its costing."),
  ],
 },
 {
  "title": "Night Lights",
  "topic": "Science",
  "extracts": [
    ("Text 1", [
      "The number of stars visible from a suburban backyard has fallen by about two "
      "thirds in fifty years.",
      "Most of that loss comes from light thrown upward and sideways rather than down.",
      "A shield above a lamp costs almost nothing and removes most of it.",
      "Brightness is not the problem; direction is.",
    ]),
    ("Text 2", [
      "All new street lighting in the shire uses LED lamps at 4000 kelvin.",
      "The LEDs use about sixty per cent less power than the lamps they replaced.",
      "Every lamp is fitted with a flat lens that directs the light downward.",
      "The colour temperature was chosen for the clarity it gives to security cameras.",
    ]),
    ("Text 3", [
      "Hatchling turtles find the sea by moving towards the brightest open horizon.",
      "Blue and white light draws them inland far more strongly than amber light does.",
      "On beaches beside amber-lit streets we lose a small fraction of a nest.",
      "On beaches beside white-lit streets we can lose most of it.",
    ]),
  ],
  "items": [
    ("detail", "medium", 0.93, ["Text 1"], [(0, 3)],
     'Text 1 concludes: "{q}" This means that —',
     "where the light goes matters more than how much of it there is",
     [("using dimmer lamps everywhere would solve the problem", "contradicts"),
      ("the number of street lamps in the shire should be cut back sharply", "unsupported"),
      ("street lighting should not be used anywhere at all", "overreach")],
     "The sentence sets direction above brightness as the thing that counts. Using dimmer "
     "lamps everywhere would solve the problem is exactly the brightness answer the "
     "sentence rejects."),

    ("comparison", "medium", 0.92, ["Text 1", "Text 2"], [],
     'Which part of the council specification already answers Text 1?',
     "the flat lenses that direct the light downward",
     [("the LEDs using sixty per cent less power than before", "wrong_focus"),
      ("the colour temperature of four thousand kelvin", "contradicts"),
      ("the replacement of all of the older lamps", "half_right")],
     "Downward-directed light is precisely the fix the first text asks for. The colour "
     "temperature of four thousand kelvin is the choice that creates the problem in the "
     "third text, not one that answers the first."),

    ("main_idea", "medium", 0.92, ALL, [],
     'Put side by side, what do these three texts show?',
     "the council has solved one problem and created another",
     [("the council has solved both of the problems at once", "contradicts"),
      ("street lighting should be switched off entirely from dusk until dawn", "overreach"),
      ("astronomers and turtle researchers want opposite things", "unsupported")],
     "The lenses fix the sky glow; the white colour is what disorients hatchlings. "
     "Astronomers and turtle researchers want opposite things is not so — both want the "
     "light controlled, in different ways."),

    ("comparison", "hard", 0.90, ALL, [],
     'Which change would satisfy Text 1 and Text 3 at the same time?',
     "keeping the shielded lenses and changing the colour to amber",
     [("keeping the colour and taking the shields off the lamps", "contradicts"),
      ("going back to the older lamps used before the LEDs", "unsupported"),
      ("making the lamps a good deal brighter but pointing them downward", "half_right")],
     "The lenses already satisfy the astronomer; only the colour is left, and amber is "
     "what the turtle researcher asks for. Making the lamps brighter but pointing them "
     "downward keeps the white light that does the damage."),
  ],
 },
 {
  "title": "The Old Oval Trees",
  "topic": "Heritage",
  "extracts": [
    ("Text 1", [
      "The row of twelve elms on the western boundary was planted in 1928.",
      "Four are in good condition, six are in fair condition, and two have significant "
      "decay in the main stem.",
      "The target zone of the two decayed trees includes the players' benches.",
      "Removal of those two is recommended; the other ten require pruning only.",
    ]),
    ("Text 2", [
      "The benches have stood under those trees for as long as anybody can remember.",
      "On a January afternoon they are the only shade anywhere on the ground.",
      "We would rather move the benches than lose the trees.",
      "Nobody at the club has been told that moving them was an option.",
    ]),
    ("Text 3", [
      "The avenue is listed as a memorial planting, one tree for each local man who did "
      "not return from the First World War.",
      "The listing covers the row as a group, not the individual trees.",
      "Works to a listed planting require notification but not approval where public "
      "safety is involved.",
      "Replacement planting is expected wherever a listed tree is removed.",
    ]),
  ],
  "items": [
    ("detail", "medium", 0.93, ["Text 1"], [(0, 1)],
     'The arborist reports: "{q}" This means that —',
     "most of the row is in good or fair condition",
     [("all twelve of the trees are recommended for removal", "contradicts"),
      ("the arborist's report was carried out back in 1928", "wrong_focus"),
      ("the trees are certain to fall within the next year", "overreach")],
     "Ten of the twelve are sound enough to keep, with only two decayed. All twelve of "
     "the trees are recommended for removal contradicts the very next sentence, which "
     "recommends pruning ten of them."),

    ("comparison", "medium", 0.92, ["Text 1", "Text 2"], [],
     'What does Text 2 propose that Text 1 never considers?',
     "moving the benches out from under the trees",
     [("pruning the ten trees that are still sound", "contradicts"),
      ("replacing any of the trees that are removed", "wrong_focus"),
      ("closing the whole ground on hot afternoons", "unsupported")],
     "The report treats the benches as fixed and the trees as the variable; the club "
     "reverses that. Pruning the ten trees that are still sound is the report's own "
     "recommendation, not the club's proposal."),

    ("main_idea", "medium", 0.92, ALL, [],
     'Reading all three, what becomes clear?',
     "the decision involves safety, shade and memory at once",
     [("the decision is purely a matter of the trees' health", "contradicts"),
      ("the cricket club has the final say over the trees", "unsupported"),
      ("the whole avenue will have to be replanted shortly", "overreach")],
     "One text measures decay, one measures shade, and one records what the row stands "
     "for. The decision is purely a matter of the trees' health leaves out both of the "
     "other texts."),

    ("comparison", "hard", 0.90, ALL, [],
     'Which text shows that removing the two trees would not settle the matter?',
     "Text 3, because replacement planting is expected",
     [("Text 1, because ten of the trees still need pruning", "half_right"),
      ("Text 2, because the benches are the only shade there", "wrong_focus"),
      ("Text 3, because approval would first have to be sought", "contradicts")],
     "A memorial of one tree per man cannot simply lose two, so something has to be "
     "planted back. Text 3, because approval would first have to be sought contradicts "
     "the listing, which requires notification and not approval."),
  ],
 },
 {
  "title": "Reading on Screens",
  "topic": "Education",
  "extracts": [
    ("Text 1", [
      "Readers of the same passage on paper and on screen were tested on what they "
      "remembered.",
      "On short, simple passages there was no difference between the two.",
      "On longer passages with an argument to follow, the paper readers scored higher.",
      "Readers on screen consistently judged their own understanding to be better than it "
      "was.",
    ]),
    ("Text 2", [
      "Physical loans from the school library fell by nineteen per cent over three years.",
      "Ebook loans over the same period rose by four hundred per cent, from a very low "
      "base.",
      "Ebook loans are still fewer than one in six of all loans.",
      "The most borrowed items in both formats are the same twelve series.",
    ]),
    ("Text 3", [
      "I read on the tablet because I can carry forty books in my bag instead of one.",
      "I read faster on the tablet and I am fairly sure I remember less.",
      "If it is for a test I print it out, which everyone does and nobody says.",
      "Paper is better and heavier, and that is the whole problem.",
    ]),
  ],
  "items": [
    ("detail", "medium", 0.93, ["Text 1"], [(0, 3)],
     'Text 1 found: "{q}" This tells the reader that screen readers —',
     "overestimated how much they had understood",
     [("understood more than the paper readers did", "contradicts"),
      ("were asked to judge the passage itself", "wrong_focus"),
      ("understood nothing at all of what they read", "overreach")],
     "Judging their understanding better than it was is overestimating it. Understood "
     "more than the paper readers did reverses the finding in the sentence before."),

    ("comparison", "medium", 0.92, ["Text 1", "Text 3"], [],
     'Which of the student\'s statements matches the study finding most closely?',
     "that they read faster on the tablet and remember less",
     [("that they can carry forty books instead of only one", "wrong_focus"),
      ("that they print things out before sitting a test", "half_right"),
      ("that everybody does it and nobody talks about it", "unsupported")],
     "Speed traded against recall is the study's result stated in a student's own words. "
     "That they print things out before sitting a test is a response to the problem, not "
     "a description of it."),

    ("main_idea", "medium", 0.92, ALL, [],
     'What is the point on which the three texts converge?',
     "screens are convenient, and convenience is not understanding",
     [("screens are better than paper in every situation", "contradicts"),
      ("paper books ought to be banned from the school library altogether", "overreach"),
      ("students borrow far fewer books than they used to", "wrong_focus")],
     "Forty books in a bag is convenience; the study and the student both put recall "
     "elsewhere. Screens are better than paper in every situation is denied by every one "
     "of the three texts."),

    ("comparison", "medium", 0.92, ALL, [],
     'Text 2 reports ebook loans rising four hundred per cent. Why is that less '
     'impressive than it sounds?',
     "because it starts from a very low base and is still under a sixth",
     [("because physical loans fell by nineteen per cent as well", "wrong_focus"),
      ("because the same twelve series are top of both of the formats anyway", "half_right"),
      ("because ebook loans have not actually risen at all", "contradicts")],
     "The text says so itself in the same breath, and the next line gives the share. "
     "Because ebook loans have not actually risen at all contradicts the figure the "
     "question is about."),
  ],
 },
 {
  "title": "The Fire Trail",
  "topic": "Environment",
  "extracts": [
    ("Text 1", [
      "Hazard reduction burning removes fuel so that a summer fire burns with less "
      "intensity.",
      "Burns are conducted in autumn and spring, when conditions allow.",
      "The number of days suitable for burning has fallen over the last two decades.",
      "A reduction burn is not a guarantee; it buys firefighters room to work.",
    ]),
    ("Text 2", [
      "Many Australian plants need fire, but they need it at the right interval.",
      "Some species take eight to twelve years to set seed after a fire.",
      "Burning the same ground every four years removes those species one generation at a "
      "time.",
      "A landscape can be well protected and badly damaged by the same program.",
    ]),
    ("Text 3", [
      "We had three burns in seven years on the ridge behind us.",
      "After the last one the smoke sat in the valley for four days and my daughter "
      "missed school.",
      "I would still rather the smoke than the alternative, and I have seen the "
      "alternative.",
      "What I would like is to be told the interval, and why.",
    ]),
  ],
  "items": [
    ("detail", "medium", 0.93, ["Text 1"], [(0, 3)],
     'Text 1 states: "{q}" This means the burns —',
     "make a fire easier to fight rather than impossible",
     [("prevent summer fires from ever starting in the first place", "contradicts"),
      ("are conducted only when the conditions allow it", "wrong_focus"),
      ("mean firefighters need not attend at all", "overreach")],
     "Room to work is help for the people fighting it, not the removal of the fire. "
     "Prevent summer fires from starting at all is precisely what 'not a guarantee' "
     "denies."),

    ("comparison", "medium", 0.92, ["Text 1", "Text 2"], [],
     'What tension do Texts 1 and 2 set up between them?',
     "burning often enough for safety may be too often for some plants",
     [("burning is of no use at all for either safety or for the plants", "contradicts"),
      ("there are now far more suitable days for burning", "wrong_focus"),
      ("the right interval has already been agreed upon", "unsupported")],
     "One text wants fuel kept low, the other needs eight to twelve years between fires. "
     "Burning is of no use for either safety or for plants denies the first sentence of "
     "both texts."),

    ("main_idea", "medium", 0.92, ALL, [],
     'What single picture emerges from the three texts?',
     "a necessary program whose timing is contested and unexplained",
     [("a program that nobody involved in it supports in any way at all", "contradicts"),
      ("a program that ought to be stopped immediately", "overreach"),
      ("a program whose interval has been fully explained", "unsupported")],
     "Everybody accepts the burning; the argument is about how often, and nobody has been "
     "told. A program that nobody involved supports at all is contradicted by a resident "
     "who says he would rather the smoke."),

    ("comparison", "hard", 0.90, ALL, [],
     'The resident asks to be told the interval, and why. Which text shows that the '
     'answer is not simple?',
     "Text 2, because safety and seeding pull the interval opposite ways",
     [("Text 1, because suitable burning days have become fewer", "half_right"),
      ("Text 3, because the smoke sat in the valley for four whole days afterwards", "wrong_focus"),
      ("Text 2, because no interval at all could ever work", "overreach")],
     "Four-yearly burning protects and removes species at the same time, so there is no "
     "single right number. Text 2, because no interval at all could ever work overstates "
     "a text that says plants need fire at the right interval."),
  ],
 },
]


if __name__ == "__main__":
    GEN.mkdir(parents=True, exist_ok=True)
    qs = build(PASSAGES, BOOK, NN, CATEGORY, LABEL)
    path = GEN / f"{BOOK}_p{NN}.json"
    path.write_text(json.dumps(qs, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(qs)} questions across {len(PASSAGES)} sets -> {path}")
