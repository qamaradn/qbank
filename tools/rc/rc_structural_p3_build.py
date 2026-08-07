#!/usr/bin/env python3
"""Builds rc_nsw_structural_p3.json — 5 passages x 4 gaps = 20 answer slots (§3.6).

Closes the type: 4 + 4 + 5 passages = 13, 52 gaps, the §3.1 target exactly.

Ground not used by p1 (wombat cubes, wrong bus, white ibis, beach flags) or p2 (dingo
fence, borrowed bike, school run, Flying Doctor): fire-triggered seeds, a lost dog, school
swimming, a recycling plant and the Hills Hoist.

Distractors are written LONG from the start. This type reproduces the same tell every
batch — the key is a real sentence from a coherent passage and an invented distractor
comes out blunter — and p1 and p2 both needed a rescue pass at 14/16 and 13/16.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.rc.structural_common import GAP, build  # noqa: E402

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/reading_comprehension/generated"
NN = 3
BOOK = "rc_nsw_structural"
CATEGORY = "structural_cloze"
LABEL = "Structural cloze"

# item = (gap, role, difficulty, confidence, distractors, explanation)
PASSAGES = [
 {
  "title": "The Seed That Waits",
  "topic": "Science",
  "paragraphs": [
    ["Some Australian plants will not grow until something has tried to destroy them.",
     GAP(1, "Their seeds can sit in the soil for years without doing anything at all."),
     "What wakes them is not rain, and not warmth, but fire."],
    ["A banksia holds its seeds inside a woody cone that stays shut for the whole life of "
     "the plant.",
     GAP(2, "Heat is what opens it, and only heat of the kind a bushfire brings."),
     "Within days of a fire the cones split, and the seeds fall onto ground that is bare, "
     "ash-rich and suddenly free of competition."],
    ["Other species respond to the smoke rather than to the flames.",
     GAP(3, "Chemicals in the smoke soak into the soil with the first rain, and seeds "
            "that have waited a decade begin to swell."),
     "Nurseries now sell smoke-treated water so that gardeners can trigger the same "
     "response at home."],
    ["This makes fire a difficult thing to argue about.",
     GAP(4, "The same fire that destroys a house is the one a banksia has been waiting "
            "for."),
     "Managing land in this country means deciding how much of it, and how often, and "
     "never getting the answer entirely right."],
  ],
  "items": [
    (1, "topic_sentence", "medium", 0.93,
     [("Their seeds germinate within a few days of falling onto the ground.", "contradicts"),
      ("Australia has more species of flowering plant than most other countries.", "off_topic"),
      ("What wakes these seeds is not rain, and not warmth, but fire itself.", "wrong_order")],
     "The next sentence says what finally wakes them, so the gap has to establish the "
     "waiting. Their seeds germinate within a few days of falling onto the ground would "
     "leave nothing to be woken."),

    (2, "supporting_detail", "medium", 0.92,
     [("The cone stays closed for the whole of the plant's life without exception.", "redundant"),
      ("Banksias are named after the botanist who sailed with Captain Cook.", "off_topic"),
      ("The cones open a little more each year as the plant slowly grows older.", "contradicts")],
     "The sentence after the gap describes cones splitting within days of a fire, so the "
     "gap must name heat as the trigger. The cone stays closed for the whole of the "
     "plant's life without exception repeats the sentence before it."),

    (3, "example", "medium", 0.92,
     [("Some species respond to the smoke of a fire rather than to its flames.", "redundant"),
      ("Smoke from a large bushfire can drift for hundreds of kilometres, and on a clear "
       "day it can be seen from another state.", "off_topic"),
      ("Smoke has no effect at all on seeds lying in the soil beneath it.", "contradicts")],
     "The next sentence sells smoke-treated water to gardeners, which only makes sense "
     "once smoke has been shown to do something. Smoke has no effect at all on seeds "
     "lying in the soil beneath it removes the very mechanism the paragraph is about."),

    (4, "contrast", "hard", 0.90,
     [("Fire is always destructive and has no useful role in the Australian bush.", "contradicts"),
      ("Nurseries now sell smoke-treated water so gardeners can do this at home.", "wrong_order"),
      ("House fires and bushfires are put out by the same fire brigades.", "off_topic")],
     "The last sentence is about a decision with no clean answer, which needs both sides "
     "of fire stated first. Fire is always destructive and has no useful role in the "
     "Australian bush denies everything the passage has just demonstrated."),
  ],
 },
 {
  "title": "The Lost Dog",
  "topic": "Narrative",
  "paragraphs": [
    ["The dog turned up at the back gate on Tuesday, thin and polite and completely "
     "certain of its welcome.",
     GAP(1, "It had no collar, and nobody in the street had seen it before."),
     "Mum said we would put a photo up at the shops and see what happened."],
    ["By Thursday it had a place on the verandah and a name we were not supposed to be "
     "using.",
     GAP(2, "Naming a dog you are going to give back is a mistake, and we all knew it."),
     "We used the name anyway, quietly, and only when Mum was inside."],
    ["The woman rang on Saturday morning.",
     GAP(3, "She described a scar on the dog's front leg before we had said anything "
            "about one."),
     "There was no argument to be had after that."],
    ["She cried when she saw it, which none of us had expected.",
     GAP(4, "It turned out she had been driving the same four streets every evening for "
            "nine days."),
     "We had spent four of those days deciding what to call something that already had a "
     "name."],
  ],
  "items": [
    (1, "topic_sentence", "medium", 0.92,
     [("It was wearing a collar with a phone number printed on the tag.", "contradicts"),
      ("The back gate had been left open again by somebody that morning.", "off_topic"),
      ("Mum said we would put a photograph up at the shops on the corner.", "wrong_order")],
     "Putting a photo up at the shops is only worth doing if there is no other way to "
     "find the owner. It was wearing a collar with a phone number printed on the tag "
     "would make the whole search unnecessary."),

    (2, "supporting_detail", "medium", 0.92,
     [("By Thursday the dog had earned a place on the verandah and a name of its own.",
       "redundant"),
      ("Dogs settle into a new household within a few days of arriving in it.", "too_general"),
      ("None of us had thought of a name for the dog by that stage at all.", "contradicts")],
     "'We used the name anyway' answers a warning, so the gap has to be the warning. By "
     "Thursday the dog had earned a place on the verandah and a name of its own repeats "
     "the sentence before the gap."),

    (3, "example", "medium", 0.92,
     [("She asked us whether the dog was thin, and whether it had been polite about its "
       "food.", "broken_reference"),
      ("The woman rang the house on Saturday morning while we were eating.", "redundant"),
      ("She was not able to say anything at all about what the dog looked like.",
       "contradicts")],
     "'There was no argument to be had after that' has to point at proof, and only one "
     "option provides any. She asked us whether the dog was thin, and whether it had been "
     "polite about its food leaves that sentence with nothing to refer back to."),

    (4, "conclusion", "hard", 0.90,
     [("She had only noticed that the dog was missing on the Friday evening.", "contradicts"),
      ("The woman cried when she saw the dog, which surprised all of us.", "redundant"),
      ("Dogs can travel a surprising distance in a single night, especially if something "
       "has frightened them.", "too_general")],
     "The last sentence measures the family's four days against something, and the gap "
     "has to supply the nine. She had only noticed that the dog was missing on the Friday "
     "evening would leave that comparison with nothing on the other side."),
  ],
 },
 {
  "title": "Every Child Should Swim",
  "topic": "Safety",
  "paragraphs": [
    ["Australia is a country with a coastline on every side and a pool in every second "
     "suburb.",
     GAP(1, "It is also a country where a child can finish primary school unable to swim "
            "fifty metres."),
     "Those two facts sit very badly together."],
    ["Swimming lessons are not free, and that is where the gap begins.",
     GAP(2, "A term of lessons costs more than many families can find on top of "
            "everything else a school year asks for."),
     "The children who miss out are not the children who live furthest from the water."],
    ["Some states already run programs that close the gap.",
     GAP(3, "Their schools take whole year groups to a local pool for a fortnight, in "
            "class time, at no cost to the family."),
     "The results are measured in the number of children who can float, tread water and "
     "get themselves to the edge."],
    ["This is not an argument about sport.",
     GAP(4, "Nobody is asking that every child be fast in the water, only that every "
            "child be safe in it."),
     "A country shaped like this one owes its children that much."],
  ],
  "items": [
    (1, "topic_sentence", "medium", 0.93,
     [("It is also a country where every child learns to swim before school ends.",
       "contradicts"),
      ("Australia has produced a great many Olympic swimming champions over the last "
       "hundred years.", "off_topic"),
      ("Swimming lessons cost more than a lot of families are able to find.", "wrong_order")],
     "'Those two facts sit very badly together' needs a second fact that clashes with the "
     "first. It is also a country where every child learns to swim before school ends "
     "would sit perfectly well with it, and the sentence after would make no sense."),

    (2, "supporting_detail", "medium", 0.92,
     [("Swimming lessons are not free, and that is where the whole problem starts.",
       "redundant"),
      ("Learning to swim well takes most children a couple of years of regular lessons, "
       "and rather more than that if they start late.", "too_general"),
      ("Lessons are provided free of charge to every family in the country.", "contradicts")],
     "The gap has to turn 'not free' into a reason families cannot manage it. Swimming "
     "lessons are not free, and that is where the whole problem starts simply says the "
     "sentence before the gap over again."),

    (3, "example", "medium", 0.92,
     [("Some states have already set up programs that go some way to closing it.",
       "redundant"),
      ("Public swimming pools are expensive things for a council to build, and more "
       "expensive still to keep heated and staffed all year.", "off_topic"),
      ("These programs are offered only to children whose families can pay for them.",
       "contradicts")],
     "The next sentence reports what the programs achieve, so the gap has to describe how "
     "they work. These programs are offered only to children whose families can pay for "
     "them would reopen the very gap the paragraph says is being closed."),

    (4, "conclusion", "hard", 0.90,
     [("The point of all this is to produce the next generation of champions.",
       "contradicts"),
      ("This argument has nothing at all to do with competitive sport.", "redundant"),
      ("Swimming is one of the best forms of exercise available to anybody, at any age, "
       "and one of the few that lasts a lifetime.", "too_general")],
     "The gap has to say what IS being asked, so that the last sentence can agree the "
     "country owes it. The point of all this is to produce the next generation of "
     "champions is exactly what the sentence before the gap rules out."),
  ],
 },
 {
  "title": "Sorting the Recycling",
  "topic": "Environment",
  "paragraphs": [
    ["The truck that empties your yellow bin does not take it away to be sorted by hand.",
     GAP(1, "Almost all of the sorting is done by machines that separate materials by "
            "weight, size and magnetism."),
     "A modern plant can process the contents of thousands of bins in a single day."],
    ["The first stage is a set of spinning discs that everything tumbles across.",
     GAP(2, "Flat things such as cardboard ride over the top, while round things such as "
            "bottles and cans drop through the gaps."),
     "By the end of that one machine, paper and containers are already travelling on "
     "separate belts."],
    ["Magnets and moving air do most of the rest.",
     GAP(3, "A large magnet lifts steel cans straight off the belt, and a jet of air "
            "blows the lighter plastics into a separate bay."),
     "Aluminium, which is not magnetic, is pushed aside by a spinning magnetic field that "
     "makes the cans jump."],
    ["The machines are good, but they are not clever.",
     GAP(4, "A plastic bag wrapped around a spinning disc stops the whole line while "
            "somebody climbs in to cut it free."),
     "That is why the rule about loose plastic in the bin is not fussiness, but the "
     "difference between a plant that runs and one that does not."],
  ],
  "items": [
    (1, "topic_sentence", "medium", 0.93,
     [("Every item is checked by hand before it is sent on to be recycled.", "contradicts"),
      ("Yellow-lidded bins were introduced to Australian councils gradually, one area at "
       "a time, over a period of many years.", "off_topic"),
      ("A modern plant can handle the contents of thousands of bins every day.",
       "wrong_order")],
     "The gap has to say what does the sorting, since the sentence before rules out hands. "
     "Every item is checked by hand before it is sent on to be recycled contradicts that "
     "opening sentence outright."),

    (2, "supporting_detail", "medium", 0.92,
     [("The first stage is a set of spinning discs that everything tumbles across.",
       "redundant"),
      ("Cardboard is one of the easiest materials of all to recycle, and one of the few "
       "that can be used again and again without losing much strength.", "too_general"),
      ("Everything that reaches the discs falls through them at the same rate.",
       "contradicts")],
     "The next sentence has paper and containers on separate belts, so the gap has to "
     "explain how the discs split them. Everything that reaches the discs falls through "
     "them at the same rate would mean nothing had been separated at all."),

    (3, "example", "medium", 0.92,
     [("Magnets and moving air do most of the rest of the sorting work.", "redundant"),
      ("Steel is one of the most widely recycled materials in the world, and can be "
       "melted down and used again any number of times.", "too_general"),
      ("Neither magnets nor air is of any use at this point in the process.", "contradicts")],
     "The gap has to show the magnet and the air actually working before aluminium is "
     "dealt with separately. Magnets and moving air do most of the rest of the sorting "
     "work repeats the sentence that opens the paragraph."),

    (4, "conclusion", "hard", 0.90,
     [("The machines in a sorting plant are clever enough to deal with anything.",
       "contradicts"),
      ("The machines are very good at their work, but they are not at all clever.",
       "redundant"),
      ("Plastic bags can be recycled at special collection points inside many "
       "supermarkets, but never in a household bin.", "off_topic")],
     "The last sentence explains why a rule exists, so the gap has to show the damage the "
     "rule prevents. The machines in a sorting plant are clever enough to deal with "
     "anything reverses the sentence immediately before the gap."),
  ],
 },
 {
  "title": "The Hills Hoist",
  "topic": "History",
  "paragraphs": [
    ["In 1945 a man in Adelaide named Lance Hill built his wife a clothes line.",
     GAP(1, "The old one was in the way of a tree she did not want cut down."),
     "What he made instead turned on a central post and could be wound up and down with a "
     "handle."],
    ["Neighbours asked for one, and then their neighbours did.",
     GAP(2, "Within a few years he was making them in a shed and selling them faster than "
            "he could weld."),
     "The design suited the quarter-acre blocks that were going up around every "
     "Australian city at the time."],
    ["The hoist did more than dry clothes.",
     GAP(3, "It became the thing a backyard was arranged around, and the thing children "
            "spun on until somebody shouted at them."),
     "It appears in more Australian paintings, songs and childhood memories than any "
     "other piece of garden hardware."],
    ["Dryers are quicker, and flats do not have backyards.",
     GAP(4, "Even so, the hoist has outlasted almost everything else invented in that "
            "decade."),
     "It costs nothing to run, it works whenever the sun does, and it has never needed to "
     "be plugged in."],
  ],
  "items": [
    (1, "topic_sentence", "medium", 0.92,
     [("The old clothes line had rusted through and could not be repaired at all.",
       "off_topic"),
      ("What he made instead turned on a central post and wound up and down.", "wrong_order"),
      ("Lance Hill had no interest in making a new clothes line at all.", "contradicts")],
     "'What he made instead' needs a reason the old line had to go, and the tree is the "
     "one the passage uses. The old clothes line had rusted through and could not be "
     "repaired at all supplies a different reason the passage never returns to."),

    (2, "supporting_detail", "medium", 0.92,
     [("Neighbours asked him for one, and then their neighbours asked as well.", "redundant"),
      ("Welding was a common enough trade in Australia in the years immediately after the "
       "war ended.", "too_general"),
      ("He built only the one hoist and never made another for anybody else.", "contradicts")],
     "The gap has to turn neighbours asking into a business before the blocks are "
     "mentioned. He built only the one hoist and never made another for anybody else "
     "contradicts a paragraph about demand spreading."),

    (3, "example", "medium", 0.92,
     [("The hoist did a great deal more than simply dry the family washing.", "redundant"),
      ("Clothes dry a good deal faster in a breeze than they do in still air, which is "
       "why a hoist was placed out in the open.", "too_general"),
      ("The hoist was kept at the side of the house and rarely used.", "contradicts")],
     "The next sentence claims a place in paintings and memories, which needs the hoist to "
     "have been part of daily life first. The hoist was kept at the side of the house and "
     "rarely used would make that claim impossible."),

    (4, "conclusion", "medium", 0.92,
     [("Dryers are quicker than a hoist, and flats do not have backyards.", "redundant"),
      ("The hoist disappeared from Australian backyards within a few decades.",
       "contradicts"),
      ("Australia produced a number of well-known inventions in the years after the war, "
       "several of which are still in use.", "too_general")],
     "The sentence before the gap lists what is against the hoist, so the gap has to turn "
     "the argument. The hoist disappeared from Australian backyards within a few decades "
     "cannot be followed by a sentence explaining why it still works."),
  ],
 },
]


if __name__ == "__main__":
    GEN.mkdir(parents=True, exist_ok=True)
    qs = build(PASSAGES, BOOK, NN, CATEGORY, LABEL)
    path = GEN / f"{BOOK}_p{NN}.json"
    path.write_text(json.dumps(qs, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(qs)} questions across {len(PASSAGES)} passages -> {path}")
