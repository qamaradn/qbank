#!/usr/bin/env python3
"""Builds rc_nsw_poetry_p2.json — 4 poems x 5 items = 20 answer slots (taxonomy §3.3).

Second poetry batch. Shared machinery lives in tools/rc/poetry_common.py; this file is
data. Deliberately no overlap with p1's ground: p1 ran drought / coast / migration /
suburban comedy, so p2 takes summer noise, a school carnival, a second-hand shop and a
blackout, and swaps which of them rhyme.

Every stem is anchored to named lines rather than to the poem as a whole. "What is the
mood of this poem?" has several defensible answers and no way to settle between them;
"what do THESE lines suggest?" has one.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.rc.poetry_common import build  # noqa: E402

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/reading_comprehension/generated"
NN = 2
BOOK = "rc_nsw_poetry"
CATEGORY = "poetry"
LABEL = "Poetry"

# item = (skill, difficulty, confidence, quote_refs, stem, key, distractors, explanation)
POEMS = [
 {
  "title": "Cicadas",
  "topic": "Summer",
  "stanzas": [
    ["For three weeks in January",
     "the trees are louder than the traffic."],
    ["It is not a sound you listen to.",
     "It is a sound you stand inside,",
     "the way you stand inside weather."],
    ["Underground they waited seven years",
     "in the dark, drinking from a root,",
     "saying nothing."],
    ["Now every one of them is shouting",
     "the same word at once,",
     "and the word is here."],
    ["By February the ground is littered",
     "with the shells they climbed out of,",
     "split down the back,",
     "still gripping the bark",
     "long after the cicada has gone."],
  ],
  "items": [
    ("figurative_language", "medium", 0.93, [(1, 0), (1, 1)],
     'The poem says: "{q}" This mainly suggests that the noise —',
     "surrounds the listener from every direction",
     [("is coming from inside the walls of the house", "literal"),
      ("is faint enough to be ignored easily", "contradicts"),
      ("comes from the traffic rather than the trees", "wrong_focus")],
     "A sound you stand inside has no single source to face, which is why the poem "
     "compares it to weather. It is faint enough to be ignored easily runs against trees "
     "described as louder than traffic."),

    ("structure", "medium", 0.92, [(2, 0), (2, 1), (2, 2)],
     'Stanza 3 tells us: "{q}" Why does the poet include this before the noise begins?',
     "The long silence makes the sudden racket more striking.",
     [("The cicadas were asleep for the whole seven years.", "half_right"),
      ("The cicadas would rather stay underground for good.", "contradicts"),
      ("Roots are the only food a cicada is able to digest.", "outside_knowledge")],
     "Seven years of saying nothing set against three weeks of shouting is a contrast, "
     "and the silence is what gives the noise its force. The cicadas were asleep for the "
     "whole seven years misses the drinking, which is not something a sleeper does."),

    ("figurative_language", "medium", 0.93, [(3, 0), (3, 1), (3, 2)],
     'The poem continues: "{q}" This suggests that the cicadas are —',
     "announcing that they have finally arrived",
     [("copying a human word they have learned", "literal"),
      ("calling out a warning to one another", "unsupported"),
      ("each making a different sound at once", "contradicts")],
     "After seven hidden years the whole point of the noise is that they are present at "
     "last, which is what 'here' says. Each making a different sound at once contradicts "
     "'the same word at once'."),

    ("symbolism", "hard", 0.90, [(4, 3), (4, 4)],
     'The poem ends: "{q}" What does this image suggest?',
     "A thing can keep its shape after the life leaves.",
     [("The empty shells are too heavy to fall from the tree.", "literal"),
      ("The cicadas climb back into their shells each night.", "contradicts"),
      ("The shells prove the cicadas died before they could fly.", "overreach")],
     "A shell still gripping the bark keeps the exact posture of an insect that is no "
     "longer in it. The shells prove the cicadas died before they could fly reads an "
     "empty case as a death, when splitting out of one is how a cicada leaves."),

    ("inference", "medium", 0.92, [(0, 1)],
     'The poem opens by saying "{q}" This tells the reader that the cicadas —',
     "drown out the ordinary noise of the city",
     [("have driven all the traffic off the roads", "unsupported"),
      ("live beside an unusually quiet stretch of road", "contradicts"),
      ("are being drowned out by wind in the branches", "wrong_focus")],
     "Measuring the trees against the traffic makes the point that the insects beat the "
     "loudest thing around. Live beside an unusually quiet stretch of road would make the "
     "comparison mean nothing."),
  ],
 },
 {
  "title": "The Swimming Carnival",
  "topic": "School",
  "stanzas": [
    ["They call my race at ten past nine.",
     "I have been ready since the bus,",
     "since breakfast, since the night before,",
     "since Mum said, Don't make such a fuss."],
    ["The water has a smell like coins.",
     "The blocks are hot beneath my feet.",
     "The whistle goes. The noise falls off.",
     "I only hear my heart repeat."],
    ["I am not fast. I know I'm not.",
     "Lane one is where they put the slow.",
     "But halfway down I find a rhythm",
     "nobody watching seems to know."],
    ["I come in fifth. My father claps",
     "as though I finished first of all,",
     "and something in me does not mind",
     "the number on the wall."],
  ],
  "items": [
    ("imagery", "medium", 0.93, [(1, 0)],
     'The poem says "{q}" The comparison tells the reader that the water —',
     "has a sharp, metallic smell",
     [("has coins lying on the bottom of it", "literal"),
      ("smells sweet and pleasant to the swimmer", "contradicts"),
      ("cost the school a great deal of money", "unsupported")],
     "Coins have a hard metal smell, which is how chlorine strikes you at the edge of a "
     "pool. Has coins lying on the bottom of it turns a comparison about smell into an "
     "object in the water."),

    ("mood", "medium", 0.92, [(0, 1), (0, 2)],
     'The poem says: "{q}" This repetition creates a feeling of —',
     "nerves that have been building for a long time",
     [("excitement at getting a day away from lessons", "half_right"),
      ("boredom with a carnival that will not begin", "contradicts"),
      ("careful planning of what to eat before racing", "wrong_focus")],
     "Being ready since the night before is not readiness so much as worry that will not "
     "settle. Excitement at getting a day away from lessons would not keep somebody awake "
     "the evening before."),

    ("figurative_language", "medium", 0.93, [(1, 2), (1, 3)],
     'The poem says: "{q}" This suggests that, once the race starts —',
     "everything outside it stops registering",
     [("the crowd has been asked to stop cheering", "literal"),
      ("the swimmer struggles to hear underwater", "half_right"),
      ("the swimmer is too frightened to dive in", "contradicts")],
     "The noise does not stop; it stops mattering, which is why only a heartbeat is left. "
     "The crowd has been asked to stop cheering makes an event out of what is happening "
     "inside the swimmer's head."),

    ("inference", "medium", 0.92, [(2, 0), (2, 1)],
     'The poem admits: "{q}" This mainly shows that the swimmer —',
     "sees their own ability clearly",
     [("resents the teachers for the lane they were given", "unsupported"),
      ("believes lane one is the best lane in the pool", "contradicts"),
      ("has never taken part in a swimming race before", "wrong_focus")],
     "Saying it twice, plainly, is an honest account rather than a protest. Resents the "
     "teachers for the lane they were given adds an anger the flat, matter-of-fact tone "
     "does not carry."),

    ("symbolism", "hard", 0.90, [(3, 2), (3, 3)],
     'The poem ends: "{q}" This ending suggests that the swimmer —',
     "has found something a placing cannot measure",
     [("did not notice which place they came in", "contradicts"),
      ("has decided to train much harder next year", "unsupported"),
      ("now believes that winning does not matter to anyone", "overreach")],
     "The rhythm found halfway down the pool is the thing worth having, and it is not "
     "what the wall records. Did not notice which place they came in cannot be right, "
     "because the poem states the fifth place outright."),
  ],
 },
 {
  "title": "Tip Shop",
  "topic": "Community",
  "stanzas": [
    ["Everything here has been owned."],
    ["A cricket bat with a name burnt into the handle.",
     "Nine teacups, no saucers.",
     "A globe with one country spelled the old way.",
     "Sixty keys in a biscuit tin,",
     "and not one door left to fit them."],
    ["Nothing is broken enough to be thrown out",
     "and nothing is good enough to be kept,",
     "so it waits here in the middle,",
     "under a roof of corrugated iron",
     "that rings when it rains."],
    ["Dad bought a chair here in 1998.",
     "We still eat dinner in it.",
     "He says the trick is knowing",
     "the difference between old",
     "and finished."],
  ],
  "items": [
    ("inference", "medium", 0.92, [(0, 0)],
     'The poem opens with a single line: "{q}" This tells the reader that —',
     "every object here has had an owner already",
     [("everything in the shop has already been paid for", "wrong_sense"),
      ("the whole shop belongs to one particular person", "wrong_focus"),
      ("nothing in the shop has ever actually been used", "contradicts")],
     "Standing alone, the line makes ownership the thing all this junk has in common: "
     "each piece came from a household. Everything in the shop has already been paid for "
     "takes 'owned' to mean settled up rather than belonged to."),

    ("imagery", "medium", 0.93, [(1, 3), (1, 4)],
     'The poem lists "{q}" This detail suggests that the objects —',
     "have outlasted whatever gave them a purpose",
     [("have all been bent out of shape over the years", "contradicts"),
      ("belong to doors being sold in a different shop", "unsupported"),
      ("will soon be matched with the doors they open", "overreach")],
     "A key with no lock left is complete and useless at the same time, which is the "
     "state of everything in the shop. Have all been bent out of shape over the years "
     "invents damage where the point is that nothing is damaged."),

    ("figurative_language", "medium", 0.93, [(2, 0), (2, 1), (2, 2)],
     'The poem says: "{q}" This suggests that the things in the shop are —',
     "caught between being useful and being rubbish",
     [("sorted by the owner into broken and unbroken piles", "contradicts"),
      ("waiting for the shop to open for the day", "literal"),
      ("priced too high for anybody to want them", "unsupported")],
     "Too good to throw out and not good enough to keep leaves nowhere to go, which is "
     "what 'the middle' names. Sorted by the owner into broken and unbroken piles is the "
     "opposite of a line saying the distinction cannot be made."),

    # Retargeted: this item and the one above it both quoted "so it waits here in the
    # middle" and both turned on what "the middle" means — one passage asked the same
    # question twice. A different line, a different word.
    ("vocabulary_in_context", "medium", 0.92, [(2, 3), (2, 4)],
     'The poem describes "{q}" As it is used here, "rings" suggests the roof —',
     "makes a bright metal sound in the rain",
     [("is shaped in a circle above the shop", "wrong_sense"),
      ("is about to give way under the weight", "overreach"),
      ("keeps every drop of rain out of the shop", "wrong_focus")],
     "Rain falling on corrugated iron makes it sound like struck metal, which is what the "
     "word names here. Is shaped in a circle above the shop takes the other meaning of "
     "'rings' and gives the roof a shape instead of a sound."),

    ("symbolism", "hard", 0.90, [(3, 2), (3, 3), (3, 4)],
     'The poem ends: "{q}" What does Dad mean?',
     "Something old is not necessarily finished.",
     [("Old furniture is always better made than new furniture.", "overreach"),
      ("The chair he bought will need replacing very soon.", "contradicts"),
      ("He would rather buy antiques than second-hand goods.", "wrong_focus")],
     "A chair still in use after nearly thirty years proves the distinction he is making: "
     "age is not the same as the end of usefulness. The chair he bought will need "
     "replacing very soon runs against a family still eating dinner in it."),
  ],
 },
 {
  "title": "Blackout",
  "topic": "Family Life",
  "stanzas": [
    ["The storm came over at half past eight.",
     "The telly stopped. The fridge went still.",
     "The whole street lost its light at once,",
     "and everything went quiet, until —"],
    ["Mum found the candles in the drawer,",
     "the ones that only come out when",
     "a storm has knocked the power over,",
     "and lit them one by one, and then —"],
    ["we talked. That's all. For two whole hours",
     "not one of us went near a screen.",
     "My brother told his worst joke twice",
     "and it was funnier than it had been."],
    ["The fridge shuddered back awake,",
     "the lights came on, the screens returned,",
     "and we went back to separate rooms",
     "as if there'd been nothing to be learned."],
  ],
  "items": [
    ("mood", "medium", 0.92, [(0, 1), (0, 2)],
     'The poem opens: "{q}" These lines mainly create a feeling of —',
     "an ordinary evening suddenly turning strange",
     [("terror that the storm will hurt the family", "overreach"),
      ("relief that the power cut was expected", "contradicts"),
      ("annoyance at missing a favourite programme", "unsupported")],
     "Naming the small machines that stop, one after another, makes the familiar room "
     "unfamiliar. Terror that the storm will hurt the family is far stronger than a poem "
     "that reports the evening this calmly."),

    ("inference", "medium", 0.92, [(1, 1), (1, 2)],
     'The poem describes the candles as "{q}" This suggests that —',
     "blackouts here are common enough to expect",
     [("the candles were bought especially for this storm", "contradicts"),
      ("the family buys new candles after every storm", "unsupported"),
      ("the candles are kept hidden because they are valuable", "wrong_focus")],
     "Candles that live in a drawer for exactly this purpose are a household habit, not a "
     "one-off. The candles were bought especially for this storm cannot fit a drawer they "
     "were already waiting in."),

    ("mood", "medium", 0.92, [(2, 2), (2, 3)],
     'The poem says: "{q}" This mainly suggests that —',
     "the dark made ordinary company better than usual",
     [("the brother finally learned to tell a joke well", "half_right"),
      ("the family were too polite to say it was bad", "unsupported"),
      ("it was the funniest thing anybody had ever said", "overreach")],
     "The joke did not improve — the poem calls it his worst, and says he told it twice — "
     "so what changed is the room. The brother finally learned to tell a joke well gives "
     "the credit to him instead of to the evening."),

    ("symbolism", "hard", 0.90, [(3, 2), (3, 3)],
     'The poem ends: "{q}" This ending suggests that the family —',
     "let go of something the blackout had given them",
     [("learned absolutely nothing during the whole evening", "half_right"),
      ("still had storm damage left to deal with", "unsupported"),
      ("were sent to their rooms as a punishment", "contradicts")],
     "'As if' is doing the work: it says they acted as though there were no lesson, which "
     "implies there was one. Learned absolutely nothing during the whole evening drops "
     "that 'as if' and takes the pretence for the truth."),

    ("vocabulary_in_context", "medium", 0.92, [(3, 0)],
     'The poem says "{q}" As it is used here, "shuddered" suggests the fridge —',
     "restarted with a rough, shaking jolt",
     [("was broken by the storm and would not start", "contradicts"),
      ("was frightened by the noise of the storm", "literal"),
      ("was damaged and will shake from now on", "overreach")],
     "A fridge coming back on kicks and rattles before it settles, which is the movement "
     "the word carries. Was frightened by the noise of the storm takes a word used of "
     "people and gives the feeling to the machine."),
  ],
 },
]


if __name__ == "__main__":
    GEN.mkdir(parents=True, exist_ok=True)
    qs = build(POEMS, BOOK, NN, CATEGORY, LABEL)
    path = GEN / f"{BOOK}_p{NN}.json"
    path.write_text(json.dumps(qs, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(qs)} questions across {len(POEMS)} poems -> {path}")
