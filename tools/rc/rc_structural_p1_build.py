#!/usr/bin/env python3
"""Builds rc_nsw_structural_p1.json — 4 passages x 4 gaps = 16 answer slots (§3.6).

Structural/organisation cloze: a sentence has been removed and must be put back. The four
passages cover four of the §3.3 text types — informational, narrative, persuasive and
functional — so the type is not built entirely out of expository prose.

What makes a distractor wrong here is COHESION, not truth. Three of the four options in
every item are perfectly plausible sentences; they fail because they repeat a neighbour,
because they leave the next sentence's "it" or "forty minutes" pointing at nothing, or
because the paragraph never picks them up again. That is why the type has its own relation
vocabulary (`STRUCTURAL_RELATIONS`) rather than borrowing the comprehension one.

Gaps per passage: 4, at four different structural roles, so no passage tests the same
thing four times.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.rc.structural_common import GAP, build  # noqa: E402

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/reading_comprehension/generated"
NN = 1
BOOK = "rc_nsw_structural"
CATEGORY = "structural_cloze"
LABEL = "Structural cloze"

# item = (gap, role, difficulty, confidence, distractors, explanation)
PASSAGES = [
 {
  "title": "The Cube-Shaped Mystery",
  "topic": "Science",
  "paragraphs": [
    ["The bare-nosed wombat is the only animal on Earth known to produce cube-shaped "
     "droppings.",
     GAP(1, "For years nobody could explain how a round animal made square waste."),
     "Scientists finally worked it out in 2018, by studying the intestines of wombats "
     "that had died on Tasmanian roads."],
    ["A wombat's intestine is about ten metres long, and food takes up to four days to "
     "travel through it.",
     GAP(2, "Along the last part of that journey, the walls of the intestine are not "
            "equally stretchy."),
     "Two narrow strips stay stiff while the rest expands, and this uneven squeezing "
     "presses the drying waste into flat sides and sharp corners."],
    ["The shape turns out to be useful.",
     GAP(3, "Wombats mark their territory by leaving droppings on top of rocks and logs, "
            "where other wombats will notice them."),
     "A cube stays where it is put; a round pellet rolls away into the grass."],
    ["The discovery was not only a curiosity.",
     GAP(4, "Engineers who make things in factories usually cut or mould material into "
            "shape."),
     "A wombat manages it with nothing but soft tissue and time, and manufacturers are "
     "now studying how."],
  ],
  "items": [
    (1, "topic_sentence", "medium", 0.93,
     [("Scientists had explained the shape many years earlier.", "contradicts"),
      ("Tasmania has some of the finest beaches in Australia.", "off_topic"),
      ("The intestine of a wombat is about ten metres long.", "wrong_order")],
     "The next sentence says the answer was found at last, so the gap has to set up a "
     "question that went unanswered. Scientists had explained the shape many years "
     "earlier would leave nothing for 2018 to solve."),

    (2, "supporting_detail", "medium", 0.92,
     [("The rest of the intestine is the same all the way along.", "contradicts"),
      ("Two narrow strips stay stiff while the rest expands.", "redundant"),
      ("Digestion works differently in every kind of animal, and the wombat is no exception.", "too_general")],
     "The sentence after the gap explains what the uneven stretchiness does, so the gap "
     "must introduce it. Two narrow strips stay stiff while the rest expands is the "
     "sentence that already follows, and repeating it leaves the paragraph saying the "
     "same thing twice."),

    (3, "example", "medium", 0.92,
     [("Wombats can move surprisingly fast for such heavy animals, covering short distances at "
       "the speed of a running person.", "off_topic"),
      ("It is useful to them for several different reasons.", "too_general"),
      ("A cube will not roll away once it has been put down.", "redundant")],
     "The last sentence contrasts a cube that stays put with a pellet that rolls, which "
     "only matters once the reader knows the droppings are placed somewhere deliberately. "
     "A cube will not roll away once it has been put down states the very point the final "
     "sentence is there to make."),

    (4, "contrast", "hard", 0.90,
     [("Wombats are protected by law in every Australian state.", "off_topic"),
      ("Researchers worked the answer out by studying the intestines of wombats that had died.", "redundant"),
      ("Many animals produce droppings of unusual shapes.", "contradicts")],
     "The sentence after the gap begins 'A wombat manages it', and 'it' has to point back "
     "at shaping material, which only this option supplies. Many animals produce droppings "
     "of unusual shapes contradicts the opening claim that the wombat is the only one."),
  ],
 },
 {
  "title": "The Long Way Home",
  "topic": "Narrative",
  "paragraphs": [
    ["Mia realised her mistake three stops too late.",
     GAP(1, "The 412 and the 421 leave from the same bay at the interchange, one minute "
            "apart."),
     "She had climbed onto the wrong one without looking up."],
    ["Outside the window the shops thinned out and the houses grew further apart.",
     GAP(2, "She did not recognise a single street name."),
     "Her phone showed nine percent battery and no messages."],
    ["At the next stop she got off and stood on the footpath, working out what to do.",
     GAP(3, "The driver had told her the bus would loop back through the interchange in "
            "forty minutes."),
     "Forty minutes was a long time, but it was also a plan, and having a plan made her "
     "feel taller."],
    ["She sat on the bench and watched the road.",
     GAP(4, "When the 412 finally came around the corner, she was almost disappointed."),
     "She had managed the whole afternoon by herself, and she wanted a bit longer to "
     "enjoy it."],
  ],
  "items": [
    (1, "topic_sentence", "medium", 0.92,
     [("The interchange had been rebuilt the previous summer.", "off_topic"),
      ("She had climbed onto the wrong one without looking up.", "redundant"),
      ("Mia got off at the very next stop and waited on the footpath for another bus to come.", "wrong_order")],
     "The sentence after the gap says she boarded 'the wrong one', which needs two "
     "similar buses to have been named first. She had climbed onto the wrong one without "
     "looking up is that following sentence itself."),

    (2, "supporting_detail", "medium", 0.92,
     [("She knew this part of the city extremely well.", "contradicts"),
      ("The bus was full of people going home from work.", "off_topic"),
      ("Outside, the shops became fewer and the houses spread out.", "redundant")],
     "The paragraph is building the feeling of being somewhere unfamiliar, and this adds "
     "to it. Outside, the shops became fewer and the houses spread out says again what "
     "the sentence before the gap has just said."),

    (3, "example", "medium", 0.92,
     [("She decided that the best thing to do was to wait.", "broken_reference"),
      ("Buses in this city run to a timetable that changes at weekends and on public holidays, "
       "which a lot of passengers forget.", "too_general"),
      ("She had nine percent of her phone battery left.", "redundant")],
     "The next sentence opens 'Forty minutes was a long time', and nothing else on offer "
     "says where forty minutes came from. She decided that the best thing to do was to "
     "wait leaves that number pointing at nothing at all."),

    (4, "conclusion", "hard", 0.90,
     [("She was extremely relieved to see the bus arrive.", "contradicts"),
      ("The bench was cold and uncomfortable to sit on.", "off_topic"),
      ("She watched the road while she waited on the bench.", "redundant")],
     "The final sentence explains why she wanted longer, so the gap must say she did not "
     "want it to end. She was extremely relieved to see the bus arrive is the opposite "
     "feeling, and the sentence after it would then make no sense."),
  ],
 },
 {
  "title": "In Defence of the Bin Chicken",
  "topic": "Environment",
  "paragraphs": [
    ["The Australian white ibis has one of the worst reputations of any bird in the "
     "country.",
     GAP(1, "People call it the bin chicken, the tip turkey and the picnic pirate."),
     "Almost none of this is fair."],
    ["The ibis did not choose to live in our cities.",
     GAP(2, "Drought and drained wetlands inland destroyed the swamps where the birds "
            "used to breed."),
     "They moved to the coast because we left them nowhere else to go."],
    ["Once here, the ibis did exactly what a clever animal does.",
     GAP(3, "It learned that bins, ovals and food courts hold more food than a drying "
            "swamp ever did."),
     "We built the buffet, and then we complained about the guest."],
    ["There is a better way to think about this bird.",
     GAP(4, "An ibis in a rubbish bin is not a pest but a warning."),
     "It is telling us, loudly and in public, what we have done to the wetlands inland."],
  ],
  "items": [
    (1, "topic_sentence", "medium", 0.92,
     [("The ibis is a large white bird with a long curved beak.", "too_general"),
      ("Almost none of these names is deserved by the bird.", "wrong_order"),
      ("The ibis is one of the best loved birds in Australia.", "contradicts")],
     "The opening sentence claims a bad reputation, so the gap has to show what that "
     "reputation sounds like. Almost none of these names is deserved by the bird belongs "
     "in the slot after the gap, where the passage already answers the nicknames."),

    (2, "supporting_detail", "medium", 0.92,
     [("Ibis will often travel hundreds of kilometres between one feeding ground and the "
       "next one.", "off_topic"),
      ("The birds simply preferred the warmer weather near the sea.", "contradicts"),
      ("The ibis did not choose to come and live in our cities.", "redundant")],
     "'We left them nowhere else to go' needs the loss of the inland swamps to have been "
     "stated. The birds simply preferred the warmer weather near the sea would make the "
     "move a choice, which is what the paragraph is arguing against."),

    (3, "example", "medium", 0.92,
     [("It began building its nests much higher off the ground.", "off_topic"),
      ("Clever animals can be found in cities all over the world, from foxes in the streets "
       "overseas to possums in our own roofs.", "too_general"),
      ("The ibis is not really a clever animal at all.", "contradicts")],
     "'We built the buffet' only makes sense once the food in our bins has been "
     "mentioned. Clever animals can be found in cities all over the world is true but "
     "widens the paragraph instead of giving the example it needs."),

    (4, "contrast", "hard", 0.90,
     [("Councils should install bins that the birds cannot open.", "broken_reference"),
      ("The ibis should be removed from our cities altogether.", "contradicts"),
      ("There is another way of looking at this bird.", "redundant")],
     "The last sentence begins 'It is telling us', so the gap must be where the bird "
     "becomes a message. Councils should install bins that the birds cannot open leaves "
     "'It is telling us' with nothing to refer back to."),
  ],
 },
 {
  "title": "Between the Flags",
  "topic": "Safety",
  "paragraphs": [
    ["The red and yellow flags on an Australian beach are not decoration.",
     GAP(1, "They mark the only stretch of water that lifesavers are actively watching."),
     "Swim outside them and nobody is looking for you."],
    ["Before the flags go up, the patrol reads the beach.",
     GAP(2, "They look for rips: narrow lanes of water flowing back out to sea, often "
            "calmer and darker than the surf around them."),
     "The flags are then planted well clear of any rip that has been found."],
    ["The flags move during the day.",
     GAP(3, "A rip can shift as the tide changes, so a patrol may reposition the flags "
            "several times before the afternoon is over."),
     "This is why the safest place at nine in the morning is not always the safest place "
     "at three."],
    ["None of this works if swimmers ignore it.",
     GAP(4, "Most drownings in Australia happen on beaches with no patrol at all, or well "
            "away from the flags."),
     "The system is simple, and it asks one thing only: get between them."],
  ],
  "items": [
    (1, "topic_sentence", "medium", 0.93,
     [("The flags are red on one half and yellow on the other.", "too_specific"),
      ("Swimming outside the flags means nobody is watching you.", "redundant"),
      ("Lifesavers watch the whole beach from one end to the other.", "contradicts")],
     "The paragraph has to say what the flags are for before it can warn about swimming "
     "outside them. Swimming outside the flags means nobody is watching you is the "
     "sentence that already follows the gap."),

    (2, "supporting_detail", "medium", 0.92,
     [("Surf patrols in Australia began more than a century ago, when the first clubs were "
       "formed on the busy beaches of the east coast.", "off_topic"),
      ("They set up their equipment and check all the radios.", "broken_reference"),
      ("Reading the beach is the first job of the patrol's day.", "redundant")],
     "The sentence after the gap refers to 'any rip that has been found', so rips must "
     "have been introduced. They set up their equipment and check all the radios leaves "
     "that phrase pointing at something never mentioned."),

    (3, "transition", "medium", 0.92,
     [("The flags are planted well clear of any rip that the patrol has found while walking "
       "the length of the beach.", "wrong_order"),
      ("The flags stay in one position for the whole day.", "contradicts"),
      ("The flags are moved at various times during the day.", "redundant")],
     "The gap has to explain why the flags move, so that the next sentence can draw the "
     "conclusion about nine o'clock and three. The flags are moved at various times "
     "during the day repeats the sentence that opens the paragraph."),

    (4, "conclusion", "hard", 0.90,
     [("Lifesaving clubs rely mostly on volunteers, who give up their weekends right through "
       "the summer to run the patrols.", "off_topic"),
      ("Almost all drownings happen in the water between the flags.", "contradicts"),
      ("A rip can pull a strong swimmer past the breakers in under a minute.", "too_specific")],
     "'None of this works if swimmers ignore it' needs evidence that ignoring it is what "
     "actually happens. Almost all drownings happen in the water between the flags would "
     "argue that the system fails the people who use it, which is the reverse of the "
     "passage's case."),
  ],
 },
]


if __name__ == "__main__":
    GEN.mkdir(parents=True, exist_ok=True)
    qs = build(PASSAGES, BOOK, NN, CATEGORY, LABEL)
    path = GEN / f"{BOOK}_p{NN}.json"
    path.write_text(json.dumps(qs, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(qs)} questions across {len(PASSAGES)} passages -> {path}")
