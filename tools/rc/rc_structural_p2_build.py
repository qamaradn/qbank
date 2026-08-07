#!/usr/bin/env python3
"""Builds rc_nsw_structural_p2.json — 4 passages x 4 gaps = 16 answer slots (§3.6).

Second structural batch. Ground not used by p1 (wombat droppings, a wrong bus, the white
ibis, beach flags): the dingo fence, a borrowed bike, the school run, and the Flying
Doctor. Text types again spread across informational, narrative and persuasive.

Distractors are written at the same length as the keys from the start. In p1 they came out
short — the key is a real sentence from a coherent passage and an invented distractor
tends to be blunter — and 14 of 16 keys were the longest option before that was fixed.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.rc.structural_common import GAP, build  # noqa: E402

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/reading_comprehension/generated"
NN = 2
BOOK = "rc_nsw_structural"
CATEGORY = "structural_cloze"
LABEL = "Structural cloze"

# item = (gap, role, difficulty, confidence, distractors, explanation)
PASSAGES = [
 {
  "title": "The Longest Fence",
  "topic": "History",
  "paragraphs": [
    ["The dingo fence runs for more than five thousand kilometres across the south-east "
     "of the continent.",
     GAP(1, "It was not built all at once, and it was not built to keep dingoes out of "
            "anywhere in particular."),
     "Separate colonies put up separate barriers in the 1880s, first against rabbits, and "
     "only later joined them into one line."],
    ["The fence is about the height of a person, with wire mesh buried below the ground "
     "so that nothing can dig underneath it.",
     GAP(2, "Keeping the whole length of it standing is a full-time job for a very small "
            "number of people."),
     "Boundary riders patrol sections of it in four-wheel drives, mending breaks made by "
     "wombats, camels, floods and fallen trees."],
    ["The fence has done what it was meant to do.",
     GAP(3, "On the sheep side of it there are far fewer dingoes, and a great many more "
            "sheep."),
     "But scientists comparing the two sides have found something nobody expected."],
    ["Without dingoes, kangaroo numbers on the sheep side have risen sharply.",
     GAP(4, "More kangaroos means more grass eaten, and the ground on that side is barer "
            "and dustier than the ground on the other."),
     "A fence built to protect grazing land may be quietly wearing it out."],
  ],
  "items": [
    (1, "topic_sentence", "medium", 0.93,
     [("The fence was designed from the very beginning as a single unbroken barrier.",
       "contradicts"),
      ("Rabbits were brought to Australia in the nineteenth century and spread quickly.",
       "off_topic"),
      ("Boundary riders patrol long sections of the fence in four-wheel drives, mending "
       "the breaks as they find them.", "wrong_order")],
     "The sentence after the gap explains that separate colonies built separate barriers "
     "and joined them only later, so the gap must deny a single planned project. The "
     "fence was designed from the very beginning as a single unbroken barrier says the "
     "opposite of what follows it."),

    (2, "supporting_detail", "medium", 0.92,
     [("The mesh is buried below ground level so that nothing is able to dig under it.",
       "redundant"),
      ("The fence has needed no repairs at all since the colonies joined theirs up.",
       "contradicts"),
      ("Fences of this kind have been built in several countries around the world.",
       "too_general")],
     "The sentence after the gap describes the riders who do that work, so the gap has to "
     "say the work exists. The mesh is buried below ground level so that nothing is able "
     "to dig under it repeats the sentence immediately before the gap."),

    (3, "example", "medium", 0.92,
     [("It has been a complete failure by every measure anyone has ever applied to it.",
       "contradicts"),
      ("The dingo is the largest land predator left on the Australian mainland today.",
       "off_topic"),
      ("The fence has worked exactly as the people who built it intended it to work.",
       "redundant")],
     "'Comparing the two sides' only means something once the reader knows what is "
     "different about them. The fence has worked exactly as the people who built it "
     "intended it to work says again what the sentence before the gap has just said."),

    (4, "conclusion", "hard", 0.90,
     [("The extra kangaroos have had no effect at all on the land that they graze.",
       "contradicts"),
      ("Kangaroo numbers on the sheep side of the fence have gone up a great deal.",
       "redundant"),
      ("One boundary rider can be responsible for more than a hundred kilometres of fence, "
       "driving the length of it week after week.", "wrong_order")],
     "The last sentence says the fence may be wearing the land out, which needs the damage "
     "to have been described. The extra kangaroos have had no effect at all on the land "
     "that they graze would leave that closing claim with nothing behind it."),
  ],
 },
 {
  "title": "The Borrowed Bike",
  "topic": "Narrative",
  "paragraphs": [
    ["Sam had asked to borrow the bike for an hour.",
     GAP(1, "It was now nearly four o'clock, and the hour had been up since two."),
     "He pushed harder up the hill, working out what he was going to say."],
    ["The chain had come off twice on the way back from the creek.",
     GAP(2, "Both times he had pushed it back on with his fingers, and both times it had "
            "come off again within a kilometre."),
     "His hands were black to the wrist and there was a long grease mark down one leg of "
     "his shorts."],
    ["Ravi was sitting on his front step when Sam finally rounded the corner.",
     GAP(3, "He did not look up, and he did not say anything at all."),
     "That was worse than shouting, and both of them knew it."],
    ["Sam leaned the bike against the fence and sat down on the step beside him.",
     GAP(4, "He explained about the chain, and then he said he should have told Ravi an "
            "hour ago."),
     "Ravi looked at the grease on Sam's leg, and then at the bike, and moved along a bit "
     "to make room."],
  ],
  "items": [
    (1, "topic_sentence", "medium", 0.92,
     [("Sam had remembered to ask before he took the bike anywhere at all.", "redundant"),
      ("The bike had belonged to Ravi's older brother before it belonged to him.",
       "off_topic"),
      ("Sam was back at exactly the time that he had promised he would be back.",
       "contradicts")],
     "The next sentence has him working out what to say, which only makes sense if he is "
     "in trouble. Sam was back at exactly the time that he had promised he would be back "
     "would leave him nothing to explain."),

    (2, "supporting_detail", "medium", 0.92,
     [("He had left the bike down at the creek and walked the rest of the way home.",
       "contradicts"),
      ("Bicycle chains need to be cleaned and oiled every few months if they are going to "
       "keep running smoothly on a rough road.", "too_general"),
      ("The chain had come off twice on the way back from the creek that afternoon.",
       "redundant")],
     "Black hands and a grease mark are the evidence of handling the chain repeatedly, so "
     "the gap has to describe that. He had left the bike down at the creek and walked the "
     "rest of the way home cannot be right, because he arrives on it."),

    (3, "example", "medium", 0.92,
     [("He jumped up and shouted at Sam from halfway down the front path.",
       "contradicts"),
      ("Ravi had been waiting out on that step for most of the afternoon.",
       "broken_reference"),
      ("Ravi was sitting out the front of his house when Sam finally arrived.",
       "redundant")],
     "'That was worse than shouting' has to point back at silence, which is what the gap "
     "must supply. Ravi had been waiting out on that step for most of the afternoon "
     "leaves 'that' with nothing to refer to."),

    (4, "conclusion", "hard", 0.90,
     [("Sam pushed harder up the hill, working out what he was going to say.",
       "wrong_order"),
      ("Sam leaned the borrowed bike up against the front fence and sat down.",
       "redundant"),
      ("Bikes of that age often need a whole new chain rather than a repair.",
       "too_general")],
     "Ravi making room is an answer to something, and an apology is the only thing on "
     "offer that he could be answering. Sam pushed harder up the hill, working out what "
     "he was going to say belongs back in the first paragraph, before he arrives."),
  ],
 },
 {
  "title": "Let Them Walk",
  "topic": "Community",
  "paragraphs": [
    ["Fifty years ago, most Australian children walked or rode a bike to school.",
     GAP(1, "Today most of them are driven right up to the school gate by a parent."),
     "The change has been blamed on traffic, on distance and on busy mornings, but the "
     "biggest reason is simpler than any of those."],
    ["Parents drive because other parents drive.",
     GAP(2, "Every car at the gate makes the road outside the school a little more "
            "dangerous, which persuades one more family to drive."),
     "The traffic that frightens people into driving is made almost entirely of people "
     "who were frightened into driving."],
    ["Breaking that circle does not need new laws or new footpaths.",
     GAP(3, "In several suburbs, families have started walking in groups, with one adult "
            "collecting children along an agreed route."),
     "The children walk, the adults take turns, and the number of cars falls."],
    ["There is a lot to be gained here.",
     GAP(4, "A child who walks arrives awake, knows their own neighbourhood, and has had "
            "twenty minutes of the day that belongs to nobody else."),
     "None of that arrives through a car window."],
  ],
  "items": [
    (1, "topic_sentence", "medium", 0.92,
     [("Today almost all of them still walk or ride a bike to school.",
       "contradicts"),
      ("Fifty years ago most Australian children made their own way in to school.",
       "redundant"),
      ("Families in some suburbs have started walking to school in organised groups.",
       "wrong_order")],
     "The sentence after the gap asks why things changed, so the gap has to state the "
     "change. Today almost all of them still walk or ride a bike to school would mean "
     "nothing had changed at all."),

    (2, "supporting_detail", "medium", 0.92,
     [("Parents drive their own children because the other parents are driving theirs.",
       "redundant"),
      ("Cars have become a great deal safer over the course of the last fifty years, for "
       "the people travelling inside them at least.", "too_general"),
      ("The road outside a school is the safest stretch of road in any suburb.",
       "contradicts")],
     "The sentence after the gap describes a circle, and the gap has to be the step that "
     "closes it. Parents drive their own children because the other parents are driving "
     "theirs simply repeats the sentence before the gap."),

    (3, "example", "medium", 0.92,
     [("Councils should build much wider footpaths on every street near a school.",
       "contradicts"),
      ("The number of cars falls, and the road gets safer for everybody on it.",
       "redundant"),
      ("Parents should be encouraged to leave the car at home in the mornings.",
       "broken_reference")],
     "The gap has to give the practical example the next sentence then describes in "
     "action. Councils should build much wider footpaths on every street near a school "
     "argues for the very thing the sentence before the gap says is not needed."),

    (4, "conclusion", "hard", 0.90,
     [("There are real and lasting benefits to be had from making a change of this kind, "
       "for the children and for everybody else on the road.", "redundant"),
      ("Some children live too far away from their school to be able to walk there.",
       "off_topic"),
      ("A twenty-minute walk covers roughly one and a half kilometres of ground.",
       "too_specific")],
     "'None of that' has to point back at a list of things gained, and only one option "
     "supplies one. There are real and lasting benefits to be had from making a change of "
     "this kind says again what the sentence before the gap has just said."),
  ],
 },
 {
  "title": "The Flying Doctor",
  "topic": "History",
  "paragraphs": [
    ["In 1928 a minister named John Flynn started an air service for people living in the "
     "inland.",
     GAP(1, "At the time, a station hand with a broken leg could be a fortnight away from "
            "the nearest hospital."),
     "An aeroplane could cover in three hours what a truck covered in three days."],
    ["Getting the aeroplane there was only half the problem.",
     GAP(2, "Somebody on a remote station had to be able to call for it in the first "
            "place."),
     "Alfred Traeger solved that with a pedal-powered radio, so a homestead with no "
     "electricity could still send a message."],
    ["The service today looks nothing like the one Flynn started.",
     GAP(3, "Its aircraft carry equipment that would not have fitted in the first machine, "
            "let alone worked in it."),
     "A patient can be treated in the air on the way to a city hospital, rather than "
     "simply carried there."],
    ["What has not changed is the reason it exists.",
     GAP(4, "Distance is still the thing that makes inland medicine difficult, and "
            "distance has not shrunk."),
     "It is only the time it takes to cross it that has."],
  ],
  "items": [
    (1, "topic_sentence", "medium", 0.93,
     [("Australia had a very large number of small country hospitals at that time.",
       "contradicts"),
      ("John Flynn later appeared on the Australian twenty-dollar note in recognition of "
       "the work that he had done.", "off_topic"),
      ("Alfred Traeger built a pedal-powered radio so homesteads could send messages.",
       "wrong_order")],
     "The next sentence compares three hours against three days, so the gap has to "
     "establish how far away help was. Australia had a very large number of small country "
     "hospitals at that time would remove the problem the service was built to solve."),

    (2, "supporting_detail", "medium", 0.92,
     [("Aeroplanes of that period could not fly safely at night or in poor weather.",
       "off_topic"),
      ("Getting an aeroplane out to a remote station was the only real difficulty.",
       "contradicts"),
      ("Flying an aeroplane out to the station was half of the problem to solve.",
       "redundant")],
     "The next sentence says Traeger 'solved that', so the gap has to name the other half "
     "of the problem. Getting an aeroplane out to a remote station was the only real "
     "difficulty contradicts the sentence before the gap, which says it was half."),

    (3, "example", "medium", 0.92,
     [("The service today is run in much the same way as it was run in 1928.",
       "contradicts"),
      ("The service now operates from a network of bases spread across every mainland "
       "state, and flies on every day of the year.", "too_specific"),
      ("Today's service is a very different thing from the one that Flynn began.",
       "redundant")],
     "The gap has to show what the difference is before the next sentence gives an "
     "example of it. Today's service is a very different thing from the one that Flynn "
     "began repeats the sentence that opens the paragraph."),

    (4, "conclusion", "hard", 0.90,
     [("The reason the service exists has changed a great deal since 1928.",
       "contradicts"),
      ("Australia is one of the largest countries in the world by land area.",
       "too_general"),
      ("What has not changed at all is the reason that the service was started.",
       "redundant")],
     "The last sentence begins 'It is only the time it takes to cross it', and 'it' has "
     "to be distance. The reason the service exists has changed a great deal since 1928 "
     "reverses the sentence before the gap."),
  ],
 },
]


if __name__ == "__main__":
    GEN.mkdir(parents=True, exist_ok=True)
    qs = build(PASSAGES, BOOK, NN, CATEGORY, LABEL)
    path = GEN / f"{BOOK}_p{NN}.json"
    path.write_text(json.dumps(qs, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(qs)} questions across {len(PASSAGES)} passages -> {path}")
