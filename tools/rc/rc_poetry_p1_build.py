#!/usr/bin/env python3
"""Builds rc_nsw_poetry_p1.json — 4 poems x 5 items = 20 answer slots (taxonomy §3.3).

Poetry is one of the four NSW Reading types that were entirely unbuilt. 20 slots is one
drill set: 71 s x 20 = 24 minutes at exam pace (delivery spec §5.1.1), and a reading
drill is built in whole passages, so a set is four complete poems.

Three decisions worth stating, because they are not obvious from the JSON:

LINE BREAKS ARE LOAD-BEARING. The review UI renders `passage` through `marked.parse`
without `breaks`, so a single newline collapses and the poem arrives as a paragraph. A
poem rendered as prose is a different question — line endings are where the meaning sits.
Stanzas are therefore stored as lists of lines and joined with markdown's hard break, and
`rc_finalise.verse_line_errors` fails the batch if any line loses it.

EVERY STEM QUOTES THE POEM, AND THE QUOTE IS CUT FROM IT. `quote()` slices the stored
lines, so a stem cannot quote something the poem does not say, and the quoted lines go
into `quote_lines` for the finaliser to re-check against the passage. Anchoring each
question to named lines is also the defence against the poetry failure mode: "what is the
mood of this poem?" has several defensible answers, "what does *this line* suggest?" has
one.

DISTRACTORS ARE DECLARED AGAINST COMPREHENSION_RELATIONS, not the word-relation set the
cloze build used. `literal` — reading a figure of speech at face value — is the trap Year
6 candidates actually fall into, and it has no equivalent in a vocabulary item.

Two of the four poems are free verse, per §3.3, which requires the poetry not be all
rhyme. Pitched to Year 6: concrete situations, plain vocabulary, the difficulty in the
inference rather than in the words.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.rc.poetry_common import build  # noqa: E402

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/reading_comprehension/generated"
NN = 1
BOOK = "rc_nsw_poetry"
CATEGORY = "poetry"
LABEL = "Poetry"

# item = (skill, difficulty, confidence, quote_refs, stem, key, distractors, explanation)
# quote_refs are (stanza, line) indices into `stanzas`; "{q}" in the stem is replaced by
# the lines they name, cut from the poem itself. See tools/rc/poetry_common.py.
POEMS = [
 {
  "title": "Tank Stand",
  "topic": "Drought",
  "stanzas": [
    ["The tank stand keeps its empty drum",
     "above the cracking yard,",
     "four rusted legs, one broken rung,",
     "a shadow thin and hard."],
    ["Dad taps the iron every night",
     "and waits to hear it fall.",
     "A full tank answers low and dull.",
     "Ours rings out like a bell."],
    ["The clouds come over, thick as wool,",
     "and take their weather west.",
     "The dogs lie flat beneath the tank",
     "and do not lift their heads."],
    ["But Dad has cleaned the gutters out",
     "and turned the downpipe round,",
     "so when it comes — and it will come —",
     "we will not lose a drop."],
  ],
  "items": [
    ("figurative_language", "medium", 0.94, [(1, 2), (1, 3)],
     'The poem says: "{q}" What does this tell the reader about the family\'s tank?',
     "It is empty, because an empty tank rings.",
     [("It is full to the top after a week of steady rain.", "contradicts"),
      ("Someone has fixed a bell to the side of the tank stand.", "literal"),
      ("The iron has rusted through and will soon need replacing.", "unsupported")],
     "A full tank is said to answer low and dull, and this one does the opposite, so "
     "there is nothing in it. Nobody has fixed a bell to the side of the tank stand — "
     "'like a bell' is a comparison for the hollow ringing sound."),

    ("figurative_language", "medium", 0.93, [(2, 0), (2, 1)],
     'In stanza 3 the poet writes: "{q}" This suggests that —',
     "the clouds cross the farm without dropping rain on it",
     [("sheep are being shorn on the far side of the paddock", "literal"),
      ("a storm has damaged the tank stand during the night", "unsupported"),
      ("the family has decided to move further west to find work", "wrong_focus")],
     "The clouds arrive and carry their weather away westward, which is why the yard is "
     "still cracking. 'Wool' describes how thick they look, so sheep are being shorn on "
     "the far side of the paddock mistakes a comparison for an event."),

    ("mood", "medium", 0.92, [(2, 2), (2, 3)],
     'The lines "{q}" mainly create a feeling of —',
     "worn-out stillness that has gone on a long time",
     [("sudden danger moving towards the farmhouse", "contradicts"),
      ("tiredness at the end of a long day of mustering", "half_right"),
      ("a property that everybody has now abandoned", "overreach")],
     "Dogs flattened in the shade and too listless to raise their heads belong to a long "
     "dry spell rather than to one hard day, and tiredness at the end of a long day of "
     "mustering invents work the poem never mentions."),

    ("symbolism", "hard", 0.90, [(3, 0), (3, 1)],
     'The final stanza says: "{q}" What does this show about Dad?',
     "He is getting ready for rain he has not yet seen.",
     [("He is tidying the place up because the family is leaving.", "contradicts"),
      ("He is repairing damage left behind by the last big storm.", "unsupported"),
      ("He is certain that the rain will fall on that very night.", "overreach")],
     "Clean gutters and a turned downpipe only matter once rain arrives, so preparing "
     "them is an act of expectation, and 'it will come' states that belief outright. He "
     "is certain the rain will fall on that very night claims a precision the poem "
     "refuses: it says the rain will come, not when."),

    ("vocabulary_in_context", "medium", 0.92, [(0, 3)],
     'Stanza 1 describes "{q}" As it is used here, "hard" means the shadow is —',
     "sharply outlined by strong sunlight",
     [("difficult to make out in the glare of the sun", "wrong_sense"),
      ("solid enough for somebody to pick it up", "literal"),
      ("cast across the yard by a heavy rain cloud", "contradicts")],
     "A thin shadow with a hard edge is what fierce sun makes, so the word describes the "
     "outline. Difficult to make out in the glare of the sun takes a different meaning "
     "of 'hard' that the line does not carry."),
  ],
 },
 {
  "title": "Rock Pool",
  "topic": "The Coast",
  "stanzas": [
    ["Low tide, and the sea has left",
     "a room behind:"],
    ["one blue bowl in the rock,",
     "still as held breath,",
     "with a rim of white shells",
     "like a chipped plate."],
    ["A crab moves the way a secret moves,",
     "sideways, under the ledge."],
    ["The anemone shuts itself",
     "when my shadow crosses it —",
     "a small red fist",
     "that will not argue."],
    ["Then the first wave of the turning tide",
     "comes over the lip,",
     "and the room is a sea again,",
     "and the crab is only a crab."],
  ],
  "items": [
    ("figurative_language", "medium", 0.93, [(0, 0), (0, 1)],
     'The poem opens: "{q}" Calling the rock pool a room suggests that it is —',
     "a small closed space, shut off from the ocean",
     [("part of a beach house that the poet is standing inside", "literal"),
      ("proof the tide has gone out further than it ever has", "overreach"),
      ("surrounded by a wall that somebody has built from rock", "unsupported")],
     "A room is enclosed and separate, which is how the pool sits once the tide "
     "withdraws. The poet is standing on the rocks, not inside part of a beach house — "
     "the room is a comparison, not a building."),

    ("imagery", "medium", 0.92, [(1, 0), (1, 1)],
     'The poet describes "{q}" This mainly tells the reader that the water is —',
     "completely motionless, as though it is waiting",
     [("still warm from a whole morning of strong sun", "outside_knowledge"),
      ("rising and falling gently with the swell outside", "contradicts"),
      ("actually breathing, in and out, like an animal", "literal")],
     "Held breath is silent and unmoving, and it is held only for a moment, so the "
     "comparison gives both stillness and expectation. A pool actually breathing, in "
     "and out, like an animal mistakes the comparison for a description."),

    ("figurative_language", "medium", 0.93, [(2, 0), (2, 1)],
     'What does the comparison in "{q}" suggest about the crab?',
     "It moves quietly and out of sight.",
     [("It scuttles loudly enough to be heard from the shore.", "contradicts"),
      ("It goes sideways, which is simply how every crab moves.", "half_right"),
      ("It has been startled by the wave that is coming in.", "unsupported")],
     "Secrets travel quietly and stay hidden, and the crab does the same by slipping "
     "under the ledge. It goes sideways, which is simply how every crab moves is true of "
     "crabs but ignores what the comparison is doing."),

    ("figurative_language", "medium", 0.93, [(3, 2), (3, 3)],
     'The anemone is called "{q}" This presents the anemone as —',
     "closed tight, and refusing without a fight",
     [("furious, and ready to sting the poet's hand", "half_right"),
      ("injured by the shadow that crossed over it", "unsupported"),
      ("a human hand reaching up out of the water", "literal")],
     "A fist is shut and firm, and 'will not argue' takes the fight out of it, leaving a "
     "silent refusal. Furious, and ready to sting the poet's hand keeps the anger a fist "
     "suggests but drops the half of the image that matters."),

    ("mood", "hard", 0.90, [(4, 2), (4, 3)],
     'The poem ends: "{q}" This ending marks a change because —',
     "the returning water makes everything ordinary again",
     [("the tide has destroyed the rock pool for good", "overreach"),
      ("the poet decides the crab was never really there", "contradicts"),
      ("the poem turns from the sea to look at the land", "wrong_focus")],
     "Until this point the pool was a room and the crab was a secret; once the water "
     "returns they are only a sea and only a crab, so the spell rather than the place is "
     "what ends. The tide has destroyed the rock pool for good misreads an ordinary "
     "turning tide as damage."),
  ],
 },
 {
  "title": "The Suitcase",
  "topic": "Migration",
  "stanzas": [
    ["Nan's suitcase lives on top of the wardrobe",
     "where the dust is."],
    ["It came off a ship in 1958",
     "with a label still tied to the handle,",
     "her name spelled wrong,",
     "the ink gone brown as tea."],
    ["Inside: a wedding photograph,",
     "two pressed gum leaves from the first week,",
     "a coin that is not money here,",
     "and a jumper for a winter",
     "that never came."],
    ["When we lift it down she does not open it.",
     "She puts her hand flat on the lid",
     "the way you would calm a horse,",
     "and says, Not today, love.",
     "Not today."],
  ],
  "items": [
    ("inference", "hard", 0.90, [(1, 1), (1, 2)],
     'The poem mentions "{q}" This most likely shows that —',
     "she arrived where her name was unfamiliar",
     [("she travelled under a false name so she would not be noticed", "unsupported"),
      ("the suitcase had belonged to somebody else before the voyage", "contradicts"),
      ("she had never been taught how to spell her own name", "overreach")],
     "A name written down by strangers who had not met it before comes out wrong, which "
     "is what arriving in a new country is like. The suitcase had belonged to somebody "
     "else before the voyage contradicts the first line, which calls it Nan's."),

    ("symbolism", "medium", 0.92, [(2, 3), (2, 4)],
     'The list of contents ends with "{q}" What does this suggest about Nan?',
     "She packed for a country unlike the one she found.",
     [("She knitted the jumper to pass the time on the long voyage.", "unsupported"),
      ("The winter did not arrive at all in Australia that year.", "literal"),
      ("The jumper was lost before she ever had a chance to wear it.", "contradicts")],
     "A jumper packed for a cold season that never arrives is a preparation for the "
     "wrong place, which is what leaving one country for another can be. The jumper was "
     "lost before she ever had a chance to wear it cannot be right, since the poem lists "
     "it among the things still inside."),

    ("symbolism", "medium", 0.92, [(2, 2)],
     'The list includes "{q}" The line shows that the coin —',
     "buys nothing here, but has been kept anyway",
     [("is a forgery that Nan was handed by mistake overseas", "wrong_sense"),
      ("was spent at one of the ports along the voyage out", "contradicts"),
      ("would now be worth a great deal to a coin collector", "unsupported")],
     "Currency from somewhere else has no value in a new country, yet it has been carried "
     "across the world and kept for sixty years. It was spent at one of the ports along "
     "the voyage out cannot be right, because the coin is still in the case."),

    ("figurative_language", "medium", 0.93, [(3, 1), (3, 2)],
     'The poem describes Nan: "{q}" The comparison suggests she is —',
     "quieting something that could easily become upsetting",
     [("worried that the heavy case is about to fall on somebody", "literal"),
      ("teaching the grandchildren the right way to handle animals", "wrong_focus"),
      ("angry that the case was brought down from the wardrobe", "contradicts")],
     "You calm a horse gently, and only because it might otherwise bolt, so the gesture "
     "treats the suitcase as something that could break loose. Angry that the case was "
     "brought down from the wardrobe misses the gentleness the comparison insists on."),

    ("mood", "medium", 0.92, [(3, 3), (3, 4)],
     'The poem ends: "{q}" The repetition creates a feeling of —',
     "gentle refusal, and grief that is still close",
     [("sharp scolding of the children for having disturbed her", "contradicts"),
      ("playful teasing between Nan and her grandchildren", "half_right"),
      ("confusion about what the old suitcase actually holds", "unsupported")],
     "Saying it twice, and softly, makes it final without making it harsh, and 'love' "
     "keeps it kind. Sharp scolding of the children for having disturbed her would need "
     "an anger the word 'love' rules out."),
  ],
 },
 {
  "title": "Magpie Season",
  "topic": "Suburban Life",
  "stanzas": [
    ["From the first of September we take the long way,",
     "my brother and I, in a broad-brimmed hat",
     "with two eyes drawn in texta on the back of it,",
     "because the magpie of Wattle Street knows where we're at."],
    ["He owns the road. He owns the powerlines.",
     "He owns the sky above the letterbox.",
     "We are only tenants, riding through,",
     "and the rent is paid in shrieks and hair and shocks."],
    ["He comes in from behind like a thrown thing,",
     "a black-and-white stone with a plan,",
     "and my brother, who is brave in every other street,",
     "forgets that he is brave, and runs as fast as he can."],
    ["By December the chicks have learned to fly",
     "and the war of Wattle Street is done.",
     "We ride bare-headed down the middle of the road,",
     "and nobody is sure which of us won."],
  ],
  "items": [
    ("inference", "medium", 0.92, [(0, 1), (0, 2)],
     'The poem describes "{q}" This mainly shows that —',
     "they have a careful routine for getting past him",
     [("they are dressing up for a costume parade at school", "unsupported"),
      ("they think of the magpie as a friend of the family", "contradicts"),
      ("the drawings were made to frighten the poet's brother", "wrong_focus")],
     "Taking the long way and preparing the hat before September even starts is a "
     "practised set of precautions. They think of the magpie as a friend of the family "
     "runs against a bird the children are plainly trying to avoid."),

    ("figurative_language", "medium", 0.93, [(1, 0), (1, 1)],
     'Stanza 2 begins: "{q}" The repetition creates the impression that the magpie —',
     "behaves as though the whole street belongs to him",
     [("has built a nest high up on one of the powerlines", "literal"),
      ("is the only bird left anywhere in the neighbourhood", "overreach"),
      ("has lived in Wattle Street far longer than the children", "unsupported")],
     "Repeating 'he owns' over road, powerlines and sky piles up a claim over everything "
     "in sight. Has built a nest high up on one of the powerlines turns a statement about "
     "power into a fact about where the bird lives."),

    ("figurative_language", "medium", 0.93, [(1, 2), (1, 3)],
     'The poem says: "{q}" The idea of paying rent suggests that —',
     "being frightened is the price of using his street",
     [("the children's family rents a house in Wattle Street", "literal"),
      ("the children have decided to avoid the street completely", "contradicts"),
      ("the magpie takes food from the children as they ride past", "unsupported")],
     "Tenants pay to use something somebody else owns, and what these ones hand over is "
     "shrieks and hair and shocks. The children's family rents a house in Wattle Street "
     "reads a comparison about the bird as a fact about the family."),

    ("author_purpose", "hard", 0.90, [(2, 2), (2, 3)],
     'The poem tells us: "{q}" The humour here comes from —',
     "how fast one bird undoes his usual courage",
     [("the poet disliking their brother and enjoying his fear", "unsupported"),
      ("the brother being frightened of every bird he has met", "overreach"),
      ("the magpie chasing the brother the length of the street", "half_right")],
     "The joke is the gap: brave everywhere else, and the bravery gone the instant the "
     "bird appears. The magpie chasing the brother the length of the street describes "
     "what happens without touching what makes it funny."),

    ("symbolism", "medium", 0.92, [(3, 2), (3, 3)],
     'The poem closes: "{q}" This ending suggests that —',
     "the contest ends in a truce neither side can claim",
     [("the magpie has finally been driven out of Wattle Street", "contradicts"),
      ("the children lost every single encounter with the bird", "half_right"),
      ("the poet can no longer remember how the season ended", "literal")],
     "The children ride bare-headed again and the bird simply stops, so the season "
     "closes without a winner. The poet can no longer remember how the season ended "
     "reads 'nobody is sure' as forgetfulness rather than as a draw."),
  ],
 },
]


if __name__ == "__main__":
    GEN.mkdir(parents=True, exist_ok=True)
    qs = build(POEMS, BOOK, NN, CATEGORY, LABEL)
    path = GEN / f"{BOOK}_p{NN}.json"
    path.write_text(json.dumps(qs, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(qs)} questions across {len(POEMS)} poems -> {path}")
