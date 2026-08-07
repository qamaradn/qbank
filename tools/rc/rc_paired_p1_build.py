#!/usr/bin/env python3
"""Builds rc_nsw_paired_p1.json — 4 pairs x 4 items = 16 answer slots (§3.4).

Paired-extract comparison: two texts on one subject, differing in tone, attitude or
perspective. Each pair is one `passage` holding two labelled extracts — see
tools/rc/paired_common.py for why there is nowhere else to put the second text.

Two of the four items in every pair reach across BOTH extracts. That is enforced by
`min_cross_extract` in rc_finalise, because the way this type fails is quiet: a set where
every question can be answered from one text is single-passage comprehension with a spare
text attached, and it looks perfectly fine until you check which extract each item needs.

The pairs deliberately contrast text TYPES as well as attitudes — a newsletter against a
diary, two letters that disagree, a personal account against a news report, a travel guide
against a postcard home — so the comparison is about how the writing works, not only about
what each writer thinks.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.rc.paired_common import build  # noqa: E402

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/reading_comprehension/generated"
NN = 1
BOOK = "rc_nsw_paired"
CATEGORY = "paired_extract"
LABEL = "Paired-extract comparison"

# item = (skill, difficulty, confidence, uses, quote_refs, stem, key, distractors, expl)
PASSAGES = [
 {
  "title": "The School Fete",
  "topic": "School",
  "extracts": [
    ("Text 1", [
      "The Riverbend Primary Spring Fete will be held on Saturday 14 October, from nine "
      "until two.",
      "This year's fete will be our biggest yet.",
      "There will be a cake stall, a plant stall, a second-hand book table and, for the "
      "first time, a coffee van.",
      "Every class has been asked to donate items for the hamper raffle.",
      "Parents who can spare an hour on the day should add their name to the roster in "
      "the front office.",
      "Money raised will go towards shade sails for the junior playground.",
      "We look forward to seeing the whole community there.",
    ]),
    ("Text 2", [
      "Fete tomorrow.",
      "I have been on the roster for the lucky dip since March, which was not my idea.",
      "Mum says two hours will go quickly.",
      "Mum has never done two hours of lucky dip.",
      "The good part is that Dad is bringing the dog, and the dog is not allowed at "
      "school on any other day of the year.",
      "There is also a coffee van, which everyone is discussing as though a coffee van "
      "has never existed before.",
      "I would rather be at the fete than at school, which is the most I am prepared to "
      "say about it.",
    ]),
  ],
  "items": [
    ("author_purpose", "medium", 0.93, ["Text 1"], [],
     'Text 1 was written mainly in order to —',
     "tell families what is happening and ask for their help",
     [("persuade families that this fete is better than last year's", "half_right"),
      ("report on how much money the fete managed to raise", "contradicts"),
      ("complain that too few parents have offered to help", "unsupported")],
     "It gives the date, lists the stalls, and asks for donations and roster names, which "
     "is information plus a request. Report on how much money the fete managed to raise "
     "cannot be right, because the fete has not happened yet."),

    ("mood", "medium", 0.92, ["Text 2"], [(1, 2), (1, 3)],
     'Text 2 says: "{q}" These two sentences together create a tone of —',
     "dry amusement at his mother's confidence",
     [("open anger at being made to help", "overreach"),
      ("sadness that his mother will not be there", "contradicts"),
      ("confusion about how long the shift will be", "unsupported")],
     "Setting his mother's cheerful claim beside the fact that she has never done the job "
     "is a joke made without raising a voice. Open anger at being made to help is far "
     "stronger than a writer who ends by saying he would rather be there than at school."),

    ("comparison", "medium", 0.92, ["Text 1", "Text 2"], [],
     'Both texts mention the coffee van. How do they differ in the way they mention it?',
     "Text 1 offers it as an attraction; Text 2 mocks the fuss being made about it",
     [("Both texts treat the coffee van as the main reason anybody would attend at all", "overreach"),
      ("Text 1 objects to it while Text 2 is looking forward to it", "contradicts"),
      ("Neither text says anything about what the van will sell", "wrong_focus")],
     "Text 1 lists it among the attractions and marks it as new; Text 2 reports everyone "
     "discussing it as though such a thing had never existed. Neither text says anything "
     "about what the van will sell is true but is not a difference in how they mention it."),

    ("comparison", "hard", 0.90, ["Text 1", "Text 2"], [],
     'Which statement best describes how the two writers\' attitudes to the fete differ?',
     "Text 1 is enthusiastic on the school's behalf; Text 2 will go, but refuses to be "
     "enthusiastic",
     [("Text 1 is enthusiastic and Text 2 does not want to go at all", "contradicts"),
      ("Both writers are looking forward to exactly the same parts of the day, for very much "
       "the same reasons", "half_right"),
      ("Text 2 dislikes every kind of school event without exception", "overreach")],
     "Text 1 speaks for the school and calls the fete its biggest yet; Text 2 grants only "
     "that it beats a school day. Text 1 is enthusiastic and Text 2 does not want to go "
     "at all overstates the second writer, who names a good part and turns up anyway."),
  ],
 },
 {
  "title": "The Skate Park",
  "topic": "Community",
  "extracts": [
    ("Text 1", [
      "I have lived opposite the reserve for thirty-one years.",
      "The proposal to build a skate park there worries me for reasons that have nothing "
      "to do with young people.",
      "The reserve is the only flat open grass between the highway and the river.",
      "Once it is concrete it will not be grass again in my lifetime.",
      "I would support a skate park on the old depot site, which is already sealed and "
      "sits well away from houses.",
      "The council has not explained why that option was set aside.",
    ]),
    ("Text 2", [
      "I am thirteen and I have been skating for four years, mostly in the car park "
      "behind the shops.",
      "We are moved on from there about once a fortnight, which is fair enough, because "
      "it is a car park.",
      "The point is that there is nowhere else.",
      "A skate park is not a favour to us; it is somewhere to put us.",
      "The reserve is the only site anyone has actually proposed, and we have been "
      "waiting three years for a second one.",
      "If the depot is better, I would take the depot tomorrow.",
    ]),
  ],
  "items": [
    ("inference", "medium", 0.92, ["Text 1"], [(0, 1)],
     'The writer of Text 1 says: "{q}" This opening tells the reader that —',
     "the objection is about the site, not about skaters",
     [("the writer has no objection to the plan at all", "contradicts"),
      ("the writer has been asked to speak for the neighbours", "unsupported"),
      ("the writer objects to every change ever proposed for the reserve", "overreach")],
     "Naming what the worry is not about, before saying what it is, rules out the "
     "objection a reader would expect. The writer has no objection to the plan at all "
     "cannot be right, since the whole letter opposes the site."),

    ("author_purpose", "medium", 0.92, ["Text 2"], [(1, 3)],
     'Text 2 says: "{q}" The writer makes this point mainly to —',
     "argue that the park meets a need rather than granting a treat",
     [("apologise for skating in the car park behind the shops", "wrong_focus"),
      ("claim that skaters deserve more consideration than any other group in the town", "overreach"),
      ("suggest that the car park should be kept as it is", "contradicts")],
     "Calling it 'somewhere to put us' rather than a favour reframes the park as a "
     "practical solution. Apologise for skating in the car park behind the shops "
     "misreads a concession about being moved on as the letter's purpose."),

    ("comparison", "medium", 0.92, ["Text 1", "Text 2"], [],
     'Both letters mention the old depot site. What do they agree about?',
     "that the depot would be an acceptable place for the park",
     [("that the depot has already been ruled out by the council", "half_right"),
      ("that the depot is too far from the shops to be of use", "unsupported"),
      ("that the reserve is a better location than the depot", "contradicts")],
     "One writer proposes the depot and the other says he would take it tomorrow, which "
     "is agreement. That the depot has already been ruled out by the council is close — "
     "Text 1 says the council has not explained setting it aside — but that is not what "
     "the two letters agree about."),

    ("comparison", "hard", 0.90, ["Text 1", "Text 2"], [],
     'What is the real disagreement between the two letters?',
     "how long to keep waiting for a better site",
     [("whether young people should be allowed to skate at all", "contradicts"),
      ("whether the reserve is currently used as open grassland", "unsupported"),
      ("whether the council has explained its decision properly", "wrong_focus")],
     "Both would prefer the depot; one will hold out for it, the other has waited three "
     "years and will take what is on the table. Whether young people should be allowed to "
     "skate at all is the argument neither writer is having."),
  ],
 },
 {
  "title": "When the Rain Came",
  "topic": "Environment",
  "extracts": [
    ("Text 1", [
      "It rained on the Thursday night and nobody in this house slept.",
      "You cannot sleep through a sound you have been waiting three years to hear.",
      "By morning the gully was running and the dam had water in it that you could not "
      "see the bottom of.",
      "We also lost the northern fence and about forty tonnes of topsoil off the ridge, "
      "which had nothing left holding it down.",
      "I am not going to pretend that is a small thing.",
      "But I would take that rain again tomorrow, and so would every farmer between here "
      "and Bourke.",
    ]),
    ("Text 2", [
      "Heavy rain across the state's central west on Thursday night brought falls of "
      "between sixty and ninety millimetres.",
      "The weather bureau described the event as the most significant rainfall in the "
      "district since 2023.",
      "Several roads were closed on Friday morning and a number of properties reported "
      "damage to fencing and to unsealed tracks.",
      "Soil loss is expected to be considerable on slopes left bare by the long dry.",
      "Storage levels in the district's dams rose for the first time in eleven months.",
      "Further falls are forecast for the weekend.",
    ]),
  ],
  "items": [
    ("mood", "medium", 0.92, ["Text 1"], [(0, 0), (0, 1)],
     'Text 1 begins: "{q}" These lines convey —',
     "relief so large that it kept the household awake",
     [("fear that the rain would flood the property", "unsupported"),
      ("irritation at being kept awake by the noise", "contradicts"),
      ("relief so complete that the losses no longer matter", "overreach")],
     "Nobody sleeping is offered as the natural response to a sound waited three years "
     "for, not as a complaint. Irritation at being kept awake by the noise reverses the "
     "feeling the second sentence gives the sleeplessness."),

    ("detail", "medium", 0.92, ["Text 2"], [(1, 3)],
     'Text 2 states: "{q}" This sentence is best described as —',
     "a measured prediction based on the condition of the land",
     [("an eyewitness account of damage the reporter has already been out to see",
       "wrong_focus"),
      ("a warning that the district should be evacuated", "overreach"),
      ("a claim that no soil has been lost anywhere", "contradicts")],
     "'Is expected to be' forecasts rather than reports, and the reason given is the bare "
     "slopes. An eyewitness account of damage the reporter has already been out to see "
     "would need the report to have seen it, which the wording carefully avoids."),

    ("comparison", "medium", 0.92, ["Text 1", "Text 2"], [],
     'Both texts describe soil loss. How does the way they describe it differ?',
     "Text 1 gives a figure and admits the cost; Text 2 forecasts it in general terms",
     [("Text 1 ignores the soil loss while Text 2 measures it", "contradicts"),
      ("Both texts give the same figure for the amount lost", "unsupported"),
      ("Both texts treat the soil loss as the most important consequence of the whole event", "half_right")],
     "The farmer names forty tonnes off one ridge and calls it no small thing; the report "
     "says loss is expected to be considerable. Text 1 ignores the soil loss while Text 2 "
     "measures it has the two the wrong way round."),

    ("comparison", "hard", 0.90, ["Text 1", "Text 2"], [],
     'A reader who had only Text 2 would miss —',
     "what the rain meant to the people who had waited for it",
     [("everything of any importance about that Thursday night", "overreach"),
      ("the damage done to fencing on any one particular property", "half_right"),
      ("any information at all about the state of the dams", "contradicts")],
     "The report has the millimetres, the roads and the dam levels, but nothing about "
     "lying awake or taking the same rain again tomorrow. Any information at all about "
     "the state of the dams is wrong, since the report gives exactly that."),
  ],
 },
 {
  "title": "Three Days on the Island",
  "topic": "Travel",
  "extracts": [
    ("Text 1", [
      "Maria Island rewards the walker who takes their time.",
      "The ferry from Triabunna lands at Darlington, where convict-era buildings stand "
      "against a backdrop of painted cliffs.",
      "Wombats graze on the old cricket ground at dusk, entirely unbothered by visitors.",
      "There are no shops and no vehicles, so everything you need must be carried in.",
      "Accommodation is in the restored penitentiary, and bookings are essential.",
      "For those willing to carry their own water, the walk to Bishop and Clerk is the "
      "finest half-day on the island.",
    ]),
    ("Text 2", [
      "Dear Nan, we have been on the island for two days and I have carried my own water "
      "for both of them.",
      "Dad says this builds character.",
      "There are no shops, which he had somehow not mentioned before we got on the ferry.",
      "The wombats are the best thing I have ever seen and there are dozens of them on "
      "the old cricket ground every evening.",
      "We are staying in an actual convict building, which is colder inside than it is "
      "outside.",
      "Tomorrow we are climbing something called Bishop and Clerk, and I have been told "
      "it is worth it.",
    ]),
  ],
  "items": [
    ("author_purpose", "medium", 0.93, ["Text 1"], [],
     'Text 1 is written mainly for readers who —',
     "are deciding whether to visit and what to bring",
     [("have already spent several days on the island", "contradicts"),
      ("are studying the convict history of Tasmania", "wrong_focus"),
      ("want to know how the island should be managed", "unsupported")],
     "It names the ferry, warns about shops and water, and says bookings are essential, "
     "all of which are planning matters. Have already spent several days on the island "
     "would have no use for advice about what to carry in."),

    ("inference", "medium", 0.92, ["Text 2"], [(1, 1), (1, 2)],
     'Text 2 says: "{q}" What does this suggest about the writer\'s father?',
     "he did not prepare the family for what the island lacks",
     [("he had visited the island several times before", "contradicts"),
      ("he was the one carrying the water for the whole family", "wrong_focus"),
      ("he never plans any detail of a family holiday at all", "overreach")],
     "'Somehow not mentioned' is the child's dry way of saying he found out too late. He "
     "never plans any detail of a family holiday at all goes a great deal further than one "
     "omission about shops."),

    ("comparison", "medium", 0.92, ["Text 1", "Text 2"], [],
     'Both texts mention carrying water. What is the difference between them?',
     "Text 1 presents it as a condition to plan for; Text 2 as a hardship endured",
     [("Text 1 warns against it while Text 2 recommends it", "contradicts"),
      ("Both texts treat it as the worst part of the visit", "overreach"),
      ("Neither text explains why water has to be carried onto the island in the first place", "wrong_focus")],
     "Text 1 says 'for those willing to carry their own water', which is a condition; "
     "Text 2 counts the days of doing it. Both texts treat it as the worst part of the "
     "visit overstates a guide that mentions it in passing."),

    ("comparison", "hard", 0.90, ["Text 1", "Text 2"], [],
     'Which detail appears in both texts but carries a different weight in each?',
     "the wombats, listed by one writer and made the highlight by the other",
     [("the ferry, which both writers describe at length", "unsupported"),
      ("the penitentiary, which both writers mention but which neither of them describes", "half_right"),
      ("Bishop and Clerk, which only one of the texts names", "contradicts")],
     "The guide gives the wombats one line among the attractions; the child calls them "
     "the best thing they have ever seen. Bishop and Clerk, which only one of the texts "
     "names is wrong, because both texts name it."),
  ],
 },
]


if __name__ == "__main__":
    GEN.mkdir(parents=True, exist_ok=True)
    qs = build(PASSAGES, BOOK, NN, CATEGORY, LABEL)
    path = GEN / f"{BOOK}_p{NN}.json"
    path.write_text(json.dumps(qs, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(qs)} questions across {len(PASSAGES)} pairs -> {path}")
