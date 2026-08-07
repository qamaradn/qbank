#!/usr/bin/env python3
"""Builds rc_nsw_poetry_p3.json — 5 poems x 5 items = 25 answer slots (taxonomy §3.3).

Third and final poetry batch: 4 + 4 + 5 poems = 13 poems, 65 items, which is the §3.1
target exactly. Five poems here rather than four so the type closes without an orphan
batch of one.

Ground not already used by p1 (drought, coast, migration, suburban comedy) or p2 (summer
noise, school carnival, second-hand shop, blackout): a fire warning, an introduced pest, a
working dog, a first day at a new school, an overnight train. Two rhyme, three are free
verse, keeping the whole set at 6 rhyming / 7 free (§3.3 requires it not be all rhyme).
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.rc.poetry_common import build  # noqa: E402

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/reading_comprehension/generated"
NN = 3
BOOK = "rc_nsw_poetry"
CATEGORY = "poetry"
LABEL = "Poetry"

# item = (skill, difficulty, confidence, quote_refs, stem, key, distractors, explanation)
POEMS = [
 {
  "title": "Bushfire Smoke",
  "topic": "Environment",
  "stanzas": [
    ["You smell it first. Before the news,",
     "before the siren or the phone,",
     "a smell like someone burning leaves",
     "in a paddock you have never known."],
    ["The light goes wrong. The sun turns red",
     "at four o'clock, and much too low.",
     "The magpies stop. The dogs come in.",
     "The air says something we don't know."],
    ["Dad checks the app. Mum checks the sky.",
     "They give each other one short look",
     "that means: not yet, but pack the car,",
     "the photographs, the little book."],
    ["By morning it has turned away.",
     "The sky comes back its ordinary blue.",
     "But we have learned the smell by heart",
     "and turn our heads whenever it comes through."],
  ],
  "items": [
    ("inference", "medium", 0.92, [(0, 0), (0, 1)],
     'The poem begins: "{q}" This tells the reader that —',
     "the smoke arrives before any warning does",
     [("the family owns no radio or telephone", "unsupported"),
      ("a neighbour is burning leaves in a garden", "literal"),
      ("the fire has already reached the house", "overreach")],
     "Putting the smell ahead of the news and the siren makes it the first thing anybody "
     "knows. The fire has already reached the house goes far past a stanza in which "
     "nothing has happened yet but a smell."),

    ("imagery", "medium", 0.93, [(1, 0), (1, 1)],
     'The poem says: "{q}" These lines mainly describe —',
     "daylight altered by smoke in the air",
     [("a sun setting earlier than it usually does", "half_right"),
      ("a family sitting outside to watch a sunset", "wrong_focus"),
      ("a sky that has cleared completely by four", "contradicts")],
     "A red sun sitting too low at four o'clock is the sky seen through smoke, not the "
     "ordinary end of a day. A sun setting earlier than it usually does explains the hour "
     "but not the wrongness the line insists on."),

    ("mood", "medium", 0.92, [(1, 2), (1, 3)],
     'The poem says: "{q}" These lines create a feeling of —',
     "an uneasy quiet that nobody can explain",
     [("animals being called indoors by the family", "unsupported"),
      ("birds and dogs excited by the change", "contradicts"),
      ("a message arriving over the radio", "literal")],
     "Birds going silent and dogs coming in are the animals reacting before the people "
     "understand why. Birds and dogs excited by the change reverses a stanza built on "
     "things going still."),

    ("symbolism", "hard", 0.90, [(2, 2), (2, 3)],
     'Stanza 3 ends: "{q}" What does the choice of things show?',
     "they are choosing what could never be replaced",
     [("the parents are packing for an ordinary holiday", "contradicts"),
      ("the book holds the emergency instructions", "unsupported"),
      ("the family has decided to leave for good", "overreach")],
     "Photographs and one small book are worth nothing and cannot be bought again, which "
     "is exactly why they are named. The parents are packing for an ordinary holiday "
     "cannot fit a stanza whose whole meaning is 'not yet'."),

    ("figurative_language", "medium", 0.92, [(3, 2), (3, 3)],
     'The poem ends: "{q}" This suggests that —',
     "the fear outlasts the fire itself",
     [("the family has learned how to fight fires", "wrong_focus"),
      ("the smell has damaged their sense of smell", "literal"),
      ("the family no longer notices the smell", "contradicts")],
     "Learning something by heart means carrying it afterwards, and the turned head is "
     "the habit it leaves behind. The family no longer notices the smell is the opposite "
     "of a poem about noticing it forever."),
  ],
 },
 {
  "title": "Cane Toad",
  "topic": "Australian Wildlife",
  "stanzas": [
    ["They brought him here in 'thirty-five",
     "to eat a beetle off the cane.",
     "He would not eat a single one.",
     "He ate the rest, and stayed, and came again."],
    ["He has no interest in the cane.",
     "He likes a road, a bin, a light,",
     "a dog's bowl left out on the step,",
     "a warm wet gutter after night."],
    ["He is not handsome. He is not quick.",
     "He does not need to be. He waits.",
     "Whatever eats him dies of him.",
     "That is the trick. That's all it takes."],
    ["We were the ones who let him out.",
     "He only did the thing he does.",
     "He is not evil. He is ours.",
     "He is exactly what he was."],
  ],
  "items": [
    ("inference", "medium", 0.92, [(0, 2), (0, 3)],
     'The poem says: "{q}" This tells the reader that the toad —',
     "failed at its job and thrived anyway",
     [("arrived after the beetles had died out", "unsupported"),
      ("ate every beetle in the cane fields", "contradicts"),
      ("has now eaten everything in Australia", "overreach")],
     "He was imported for one task, refused it, and prospered on everything else. Ate "
     "every beetle in the cane fields is the opposite of a line saying he would not eat a "
     "single one."),

    ("imagery", "medium", 0.93, [(1, 1), (1, 2)],
     'The poem lists what he likes: "{q}" This suggests the toad does best —',
     "in places people have made",
     [("deep inside the cane fields themselves", "contradicts"),
      ("indoors, kept as somebody's pet", "unsupported"),
      ("near lights, because he cannot see well", "outside_knowledge")],
     "Roads, bins, bowls and gutters are all human leavings, which is where he prospers. "
     "Deep inside the cane fields themselves runs against a stanza that opens by saying "
     "he has no interest in the cane."),

    ("figurative_language", "medium", 0.92, [(2, 2), (2, 3)],
     'The poem says: "{q}" What does this mean?',
     "his poison alone is enough to protect him",
     [("he fights off anything that attacks him", "contradicts"),
      ("he performs a trick to escape being eaten", "literal"),
      ("he learned this behaviour after arriving", "unsupported")],
     "He does nothing at all; the animal that eats him is the one that dies. He performs "
     "a trick to escape being eaten reads 'the trick' as an action rather than as the "
     "poet's dry word for a fact about his skin."),

    ("mood", "medium", 0.92, [(2, 0), (2, 1)],
     'The poem says: "{q}" The tone of these lines is best described as —',
     "flat and unimpressed, but not hostile",
     [("openly disgusted by how the toad looks", "half_right"),
      ("admiring of the toad's speed and beauty", "contradicts"),
      ("sad that the toad is so often overlooked", "unsupported")],
     "Short, plain sentences state his faults and then dismiss them as beside the point. "
     "Openly disgusted by how the toad looks takes 'not handsome' further than a poem "
     "that goes on to say it does not matter."),

    ("symbolism", "hard", 0.90, [(3, 2), (3, 3)],
     'The poem ends: "{q}" What is the poet saying?',
     "the fault lies with the people, not the animal",
     [("the toad has changed since it arrived here", "contradicts"),
      ("the toad now belongs to a family as a pet", "wrong_sense"),
      ("the toad is the worst animal in the country", "overreach")],
     "'Ours' makes him our doing, and 'exactly what he was' says he never changed — we "
     "did. The toad now belongs to a family as a pet takes 'ours' to mean owned rather "
     "than caused."),
  ],
 },
 {
  "title": "Kelpie",
  "topic": "Working Life",
  "stanzas": [
    ["She is not a pet.",
     "Nobody has ever said good girl",
     "in the voice you use for pets."],
    ["At the gate she is a coiled thing,",
     "low to the ground, eye on the mob,",
     "waiting for the whistle",
     "the way a match waits for the box."],
    ["Two notes and she is gone —",
     "three hundred sheep turned",
     "by one dog and an idea."],
    ["In the ute on the way home",
     "she sleeps like something switched off,",
     "her paws still running."],
    ["Dad says she'll work until she can't.",
     "He says it like a compliment.",
     "I think it is one."],
  ],
  "items": [
    ("mood", "medium", 0.92, [(0, 0), (0, 1), (0, 2)],
     'The poem opens: "{q}" These lines mainly show —',
     "respect rather than affection",
     [("dislike of a dog that is unfriendly", "half_right"),
      ("sadness that nobody is kind to her", "unsupported"),
      ("certainty that she would rather be a pet", "contradicts")],
     "Refusing the pet voice is not coldness; the rest of the poem is full of admiration "
     "for what she can do. Sadness that nobody is kind to her reads a distinction about "
     "her job as neglect."),

    ("figurative_language", "medium", 0.93, [(1, 3)],
     'The poem says she waits "{q}" The comparison suggests she is —',
     "still, but ready to go off at once",
     [("waiting for somebody to light a fire", "literal"),
      ("too tired to move from the gate", "contradicts"),
      ("frightened by the sound of the whistle", "unsupported")],
     "A match does nothing until it is struck and then does everything instantly, which "
     "is the coiled stillness the stanza describes. Waiting for somebody to light a fire "
     "takes the match for an object in the paddock."),

    ("imagery", "medium", 0.93, [(2, 0), (2, 1), (2, 2)],
     'The poem says: "{q}" This mainly conveys —',
     "an enormous job done by something small",
     [("three hundred dogs turning the sheep", "contradicts"),
      ("two whistles being needed for each sheep", "literal"),
      ("three hundred hours of training behind it", "unsupported")],
     "One dog against three hundred sheep, moved by two notes, is the whole contrast. "
     "Two whistles being needed for each sheep misreads 'two notes' as a count per animal "
     "rather than the single command."),

    ("imagery", "medium", 0.92, [(3, 1), (3, 2)],
     'The poem says: "{q}" This suggests the dog is —',
     "deeply asleep and still working in her dreams",
     [("injured, and unable to walk properly", "unsupported"),
      ("pretending to be asleep in the ute", "contradicts"),
      ("beside a machine somebody has turned off", "literal")],
     "Switched off gives the depth of the sleep and the running paws give the dreaming, "
     "so both halves are needed. Pretending to be asleep in the ute would empty the image "
     "of the exhaustion it is built on."),

    ("symbolism", "hard", 0.90, [(4, 0), (4, 1), (4, 2)],
     'The poem ends: "{q}" What does the last line show?',
     "the child has come to share Dad's view of work",
     [("the child disagrees with Dad about the dog", "contradicts"),
      ("the child fears the dog is being overworked", "half_right"),
      ("Dad has decided to retire the dog shortly", "unsupported")],
     "'I think it is one' is quiet agreement arrived at rather than repeated. The child "
     "disagrees with Dad about the dog is the reading the final line exists to rule out."),
  ],
 },
 {
  "title": "First Day",
  "topic": "School",
  "stanzas": [
    ["New school. The corridors all go",
     "somewhere everybody else already knows."],
    ["At lunch I take my sandwich",
     "to the end of a bench",
     "and eat it slowly,",
     "so it lasts the whole of lunch."],
    ["There is a particular loudness",
     "to a place where nobody is talking to you."],
    ["Then a girl sits down. Not next to me —",
     "one seat along, which is the right amount —",
     "and says, That's my brother's old locker.",
     "You'll never get it open."],
    ["She shows me how. It takes",
     "a lift, then a knee.",
     "By Thursday I can do it on my own",
     "and by Friday somebody asks me how."],
  ],
  "items": [
    ("inference", "medium", 0.92, [(0, 0), (0, 1)],
     'The poem opens: "{q}" This suggests that —',
     "everyone but the newcomer knows their way",
     [("the corridors lead nowhere in particular", "contradicts"),
      ("the school has no signs on any of its walls", "unsupported"),
      ("the newcomer has come to the wrong school", "overreach")],
     "The corridors are fine; it is the knowing that the speaker lacks. The corridors "
     "lead nowhere in particular reverses a line whose point is that they lead somewhere "
     "definite to everybody else."),

    ("inference", "medium", 0.92, [(1, 2), (1, 3)],
     'The poem says: "{q}" This mainly shows that the speaker —',
     "is stretching lunch out to fill the time",
     [("has been given a very large sandwich", "literal"),
      ("is enjoying a favourite meal slowly", "half_right"),
      ("is not hungry at all on that day", "contradicts")],
     "Making it last the whole of lunch gives the hands something to do when there is "
     "nobody to talk to. Is enjoying a favourite meal slowly borrows the slowness but "
     "not the reason the poem gives for it."),

    ("figurative_language", "hard", 0.90, [(2, 0), (2, 1)],
     'The poem says: "{q}" What does this mean?',
     "being ignored can feel louder than noise",
     [("the lunch area is extremely noisy then", "literal"),
      ("the speaker has trouble hearing in crowds", "unsupported"),
      ("everybody in the school has stopped talking", "overreach")],
     "The loudness is the speaker's own attention to a silence aimed at them, not a "
     "measurement of sound. The lunch area is extremely noisy then takes a word about a "
     "feeling and makes it a fact about the room."),

    ("mood", "medium", 0.92, [(3, 0), (3, 1)],
     'The poem says: "{q}" This detail mainly shows —',
     "a kindness careful not to crowd anyone",
     [("a girl who does not want to sit near them", "half_right"),
      ("that no other seat was free on the bench", "unsupported"),
      ("that the girl is about to tell them off", "contradicts")],
     "One seat along is close enough to talk and far enough not to trap anybody, which "
     "is why the poem calls it the right amount. A girl who does not want to sit near "
     "them reads the gap as avoidance rather than as tact."),

    ("symbolism", "medium", 0.92, [(4, 2), (4, 3)],
     'The poem ends: "{q}" This ending suggests that the speaker —',
     "has become somebody others come to",
     [("finds that the locker jams again by Friday", "unsupported"),
      ("still cannot get the locker open alone", "contradicts"),
      ("has taught the whole class to open lockers", "overreach")],
     "Four days move the speaker from being shown to being asked, which is the smallest "
     "possible sign of belonging. Still cannot get the locker open alone contradicts the "
     "Thursday line directly."),
  ],
 },
 {
  "title": "Night Train",
  "topic": "Travel",
  "stanzas": [
    ["The train leaves Sydney in the dark",
     "and by midnight there is nothing in the window",
     "but my own face,",
     "and behind my face, the country going past."],
    ["Somewhere past the last of the towns",
     "a level crossing rings and swings away",
     "and is gone before I finish looking at it."],
    ["I sleep in pieces.",
     "Each time I wake the land has changed its mind:",
     "paddock, then scrub,",
     "then a long flat nothing with a single light in it",
     "that somebody is awake inside."],
    ["At six the sky goes grey, then apricot.",
     "The window lets my face go",
     "and gives the country back."],
  ],
  "items": [
    ("imagery", "medium", 0.93, [(0, 2), (0, 3)],
     'The poem says there is nothing in the window "{q}" This describes —',
     "a dark window working as a mirror",
     [("another passenger standing behind the seat", "literal"),
      ("a window that has been painted over", "contradicts"),
      ("the poet asleep against the cold glass", "unsupported")],
     "At night the lit carriage turns the glass into a mirror, with the landscape faint "
     "beyond it. Another passenger standing behind the seat takes 'behind my face' as a "
     "position in the carriage rather than in the reflection."),

    ("inference", "medium", 0.92, [(1, 1), (1, 2)],
     'The poem says: "{q}" This mainly conveys —',
     "how fast the train is travelling",
     [("a crossing being swung open by hand", "literal"),
      ("the poet deciding to look away from it", "wrong_focus"),
      ("the train slowing to a stop at the crossing", "contradicts")],
     "A crossing that is gone before the looking finishes measures the speed against a "
     "glance. The train slowing to a stop at the crossing is the opposite of something "
     "swinging away."),

    ("figurative_language", "medium", 0.92, [(2, 1)],
     'The poem says: "{q}" This suggests that the landscape —',
     "is different at every waking",
     [("keeps making the poet change direction", "wrong_focus"),
      ("has turned the train around in the night", "unsupported"),
      ("stays exactly the same all night long", "contradicts")],
     "Giving the land a mind is a way of saying it will not settle into one kind of "
     "country. Stays exactly the same all night long contradicts the list of paddock, "
     "scrub and flat nothing that follows."),

    ("imagery", "hard", 0.90, [(2, 3), (2, 4)],
     'The poem describes "{q}" What makes this image striking?',
     "one sign of another life in all that emptiness",
     [("the light is mounted on the front of the train", "wrong_focus"),
      ("the poet has come upon an entire town", "overreach"),
      ("there is nothing to see out there at all", "contradicts")],
     "A single light in a long flat nothing puts one waking stranger against an enormous "
     "dark. The poet has come upon an entire town makes a settlement out of the one lit "
     "window the line allows."),

    ("symbolism", "medium", 0.92, [(3, 1), (3, 2)],
     'The poem ends: "{q}" This ending describes —',
     "daylight replacing the reflection with real country",
     [("the poet leaving the train at six o\'clock", "unsupported"),
      ("somebody sliding the train window open", "literal"),
      ("the country disappearing from view", "contradicts")],
     "Once it is light outside, the glass stops reflecting and starts showing, so the "
     "face goes and the land returns. The country disappearing from view reverses what "
     "the last line says is given back."),
  ],
 },
]


if __name__ == "__main__":
    GEN.mkdir(parents=True, exist_ok=True)
    qs = build(POEMS, BOOK, NN, CATEGORY, LABEL)
    path = GEN / f"{BOOK}_p{NN}.json"
    path.write_text(json.dumps(qs, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(qs)} questions across {len(POEMS)} poems -> {path}")
