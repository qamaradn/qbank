#!/usr/bin/env python3
"""Builds rc_nsw_single_p6.json — 6 passages x 6 items = 36 answer slots (§3.1 type 3.1).

Sixth single-passage batch: a lost tooth at the wrong moment, why the Sydney Harbour
Bridge has a hinge it never uses, an argument about school photographs, a first-aid card,
a grandfather's shed, and why ice is slippery.

The three distractors in every item here were chosen against each other rather than
picked from a varied pool — p5 showed that varying the pool alone just moves the
duplication from `contradicts` to `literal`. Each item's three relations were written down
before the options and then filled.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.rc.paired_common import build  # noqa: E402

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/reading_comprehension/generated"
NN = 6
BOOK = "rc_nsw_single"
CATEGORY = "single_passage"
LABEL = "Single-passage comprehension"
ONE = []

PASSAGES = [
 {
  "title": "The Wrong Moment",
  "topic": "Narrative",
  "extracts": [("", [
    "The tooth had been loose for nine days and I had a system, which was to move it with "
    "my tongue at every opportunity and never with my fingers.",
    "The fingers felt like cheating and also like the tooth might come out.",
    "It came out during the class photograph.",
    "Not before it, not after it, but in the four seconds between the photographer saying "
    "everybody and saying ready.",
    "I felt it go and I did the only thing available, which was to close my mouth "
    "completely and hold entirely still.",
    "The photograph shows twenty-eight students smiling and one boy with an expression "
    "that has been described, by my own family, as suspicious.",
    "Afterwards I stood in the corridor with a tooth in my hand and no idea what a person "
    "does next.",
    "Priya, who I did not know well, said do you want me to hold it, and I said yes, "
    "which surprised both of us.",
    "She carried it to the office for me in a folded piece of paper.",
    "We are still friends and the photograph is still on my grandmother's wall.",
    "She thinks I look thoughtful.",
    "I have decided not to explain.",
  ])],
  "items": [
    ("inference", "medium", 0.93, ONE, [(0, 1)],
     'The narrator says: "{q}" Why did he avoid using his fingers?',
     "he wanted the tooth to come out on its own",
     [("he had been told never to touch the tooth", "unsupported"),
      ("his fingers were too large to reach the tooth", "literal"),
      ("he was frightened of the tooth coming out at all", "half_right")],
     "Both reasons he gives point the same way: touching it would be forcing something he "
     "wanted to happen by itself. He was frightened of the tooth coming out at all is "
     "close, but he had a system for encouraging it, not preventing it."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 5)],
     'The passage says: "{q}" Why does the family call the expression "suspicious"?',
     "a closed mouth in a photograph looks like hiding something",
     [("the boy had done something wrong earlier that day", "overreach"),
      ("the photographer had asked him to look serious", "contradicts"),
      ("the family already knew the story behind the photograph", "wrong_focus")],
     "Twenty-eight open mouths and one shut one reads as concealment, which in this case "
     "it literally was. The family knew the story behind the photograph would make the "
     "word a joke rather than a description of the face."),

    ("author_purpose", "medium", 0.92, ONE, [(0, 3)],
     'Why does the writer specify: "{q}"?',
     "to make the timing as bad as it could possibly be",
     [("to explain how school photographs are taken", "wrong_focus"),
      ("to show the photographer was working slowly", "contradicts"),
      ("to show the tooth came out because of the photograph", "half_right")],
     "Narrowing it to four seconds turns bad luck into something almost designed. To show "
     "the photographer was working slowly reverses a passage in which everything happens "
     "very fast."),

    ("inference", "medium", 0.92, ONE, [(0, 7)],
     'The passage says: "{q}" Why were both of them surprised?',
     "neither expected him to accept help from a near stranger",
     [("Priya had not meant to make the offer", "unsupported"),
      ("Priya had made exactly the same offer to other students before", "half_right"),
      ("saying yes was the wrong answer to give", "contradicts")],
     "He did not know her well, which makes both the offer and the acceptance a step "
     "outside the ordinary. Saying yes was the wrong answer to give is denied by a "
     "friendship that has lasted since."),

    ("main_idea", "hard", 0.90, ONE, [],
     'What does this passage turn out to be about?',
     "a small disaster that produced a friendship",
     [("the correct way to remove a loose tooth", "wrong_focus"),
      ("a boy embarrassed by a school photograph", "half_right"),
      ("a photograph that was taken again later", "contradicts")],
     "The tooth and the photograph are the setting; Priya is what the passage keeps and "
     "ends on. A boy embarrassed by a school photograph stops halfway through the story."),

    ("cause_effect", "medium", 0.92, ONE, [(0, 10), (0, 11)],
     'The passage ends: "{q}" Why has the narrator decided not to explain?',
     "he prefers his grandmother's version of the picture",
     [("he cannot remember the day clearly enough", "contradicts"),
      ("his grandmother would take the photograph down", "unsupported"),
      ("nobody has ever asked him about the photograph", "wrong_focus")],
     "Leaving her with thoughtful is a small kindness he is choosing. He cannot remember "
     "the day clearly enough is impossible for a narrator who has just described it "
     "second by second."),
  ],
 },
 {
  "title": "The Hinge That Waits",
  "topic": "Science",
  "extracts": [("", [
    "Steel changes size with temperature.",
    "A bar of it a hundred metres long is roughly a centimetre longer on a hot day than a "
    "cold one, which sounds like nothing until you build a bridge.",
    "The Sydney Harbour Bridge is about five hundred metres across the arch, and between a "
    "cold night and a hot afternoon the steel wants to move by close to twenty "
    "centimetres.",
    "If it could not, it would tear itself apart or crush the stone at either end.",
    "So the bridge is not fixed to the ground the way a building is.",
    "Each end of the arch sits on enormous steel pins, and the whole structure is free to "
    "rotate very slightly around them.",
    "The roadway carries expansion joints for the same reason, which is why the sound "
    "changes as you drive across.",
    "None of this is visible from a distance and almost none of it moves more than a hand's "
    "width.",
    "Engineers call a structure that allows for this a determinate structure, meaning the "
    "forces in it can be worked out exactly.",
    "A bridge that was held rigidly at both ends would be stronger on paper and weaker in "
    "August.",
    "The thing that keeps it up is partly its refusal to hold still.",
  ])],
  "items": [
    ("detail", "medium", 0.93, ONE, [(0, 2)],
     'The passage states: "{q}" How much does the steel want to move?',
     "close to twenty centimetres between cold and hot",
     [("about one centimetre across the whole arch", "wrong_focus"),
      ("about five hundred metres in a single day", "literal"),
      ("nothing at all, because steel does not move", "contradicts")],
     "Twenty centimetres is the figure given for the arch. About one centimetre across "
     "the whole arch takes the figure for a hundred-metre bar and applies it to a bridge "
     "five times longer."),

    ("cause_effect", "medium", 0.92, ONE, [(0, 3)],
     'The passage says: "{q}" What would happen if the bridge could not move?',
     "the steel or the stone would be damaged",
     [("the bridge would simply become much stronger", "contradicts"),
      ("the roadway would become noisier to drive on", "wrong_focus"),
      ("the bridge would sink slowly into the harbour", "unsupported")],
     "Tearing itself apart or crushing the stone are the two outcomes named. The bridge "
     "would simply become much stronger is the belief the last paragraph exists to "
     "correct."),

    ("inference", "medium", 0.92, ONE, [(0, 6)],
     'The passage says: "{q}" Why does the sound change as you drive across?',
     "the tyres are crossing gaps left for expansion",
     [("the bridge is rotating on its steel pins", "wrong_focus"),
      ("the road surface is made of different materials", "unsupported"),
      ("the roadway is a single unbroken piece of steel", "contradicts")],
     "Expansion joints are gaps, and gaps are what you hear. The bridge is rotating on "
     "its steel pins belongs to the arch ends, not to the road you drive on."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 9)],
     'The passage says: "{q}" What does "on paper" mean here?',
     "in theory, before real conditions are counted",
     [("in the drawings the engineers first made", "literal"),
      ("in the opinion of most engineers today", "half_right"),
      ("in every situation the bridge might meet", "contradicts")],
     "The phrase marks a calculation that leaves out the heat, which August then supplies. "
     "In the drawings the engineers first made reads a figure of speech as a place."),

    ("author_purpose", "hard", 0.90, ONE, [(0, 10)],
     'The passage ends: "{q}" Why does the writer put it this way?',
     "to turn a piece of engineering into a small paradox",
     [("to suggest the bridge is in danger of falling", "overreach"),
      ("to explain how the steel pins were installed", "wrong_focus"),
      ("to argue that rigid bridges are always better", "contradicts")],
     "Refusal to hold still as the thing that keeps it up is a deliberate reversal of what "
     "a reader expects strength to mean. To argue that rigid bridges are always better is "
     "what the sentence before it denies."),

    ("main_idea", "medium", 0.92, ONE, [],
     'What idea does this passage build towards?',
     "a structure survives by being allowed to move",
     [("steel is a poor material for building bridges", "contradicts"),
      ("the arch is the strongest part of the bridge", "unsupported"),
      ("expansion joints are the noisiest part of a road", "wrong_focus")],
     "Every paragraph adds another way the bridge is left free rather than held. Steel is "
     "a poor material for building bridges is nowhere in a passage that explains how steel "
     "is accommodated."),
  ],
 },
 {
  "title": "The Photograph Nobody Chose",
  "topic": "Opinion",
  "extracts": [("", [
    "Every year a school photographer takes one image of each student and that image "
    "follows them for twelve months.",
    "It goes on the class list, in the yearbook, sometimes on a wall.",
    "The student has no say in which frame is used, and in most cases never sees the "
    "others.",
    "For most children this does not matter at all.",
    "For some it matters a great deal, and those are exactly the children least likely to "
    "say so.",
    "A photograph taken on a bad morning, or on the day a haircut went wrong, or two "
    "seconds after somebody said something in the queue, becomes the official version of "
    "a person for a year.",
    "The fix costs nothing.",
    "Photographers already take several frames; they simply keep the one that looks "
    "technically best.",
    "Showing a student three and letting them point at one would add perhaps four seconds "
    "per child.",
    "I have heard the objection that this would make children vain, which I think has the "
    "argument exactly backwards.",
    "Choosing is not vanity.",
    "Being handed an image of yourself that you had no part in, and being told it is now "
    "you, is the thing that teaches a child their face is somebody else's business.",
  ])],
  "items": [
    ("main_idea", "medium", 0.93, ONE, [],
     'What exactly is being proposed here?',
     "that students pick their own photograph from a few",
     [("that school photographs be stopped altogether", "contradicts"),
      ("that photographers take a great many more frames", "half_right"),
      ("that students be allowed to bring their own photograph", "unsupported")],
     "Three frames and a pointed finger is the whole proposal. That photographers take a "
     "great many more frames misses the point, since the passage says they already take "
     "several."),

    ("inference", "medium", 0.92, ONE, [(0, 4)],
     'The writer says: "{q}" Why are those children least likely to speak up?',
     "the ones most affected are least willing to draw attention",
     [("they are never told that the photograph is being taken", "contradicts"),
      ("they do not know that other frames exist", "half_right"),
      ("they have been asked not to complain about it", "unsupported")],
     "Minding a great deal about how you appear is exactly what stops you raising it. "
     "They do not know that other frames exist is true of most students and does not "
     "explain why these ones stay quiet."),

    ("author_purpose", "medium", 0.92, ONE, [(0, 6), (0, 7)],
     'Why does the writer point out: "{q}"?',
     "to remove cost as a reason for refusing",
     [("to criticise photographers for wasting frames", "wrong_focus"),
      ("to show that schools already refuse the change", "contradicts"),
      ("to show the school is already spending too much", "unsupported")],
     "If the extra frames exist already, the objection cannot be expense. To criticise "
     "photographers for wasting frames turns a fact offered in their defence into a "
     "complaint."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 9)],
     'The writer says: "{q}" What does the phrase mean?',
     "the objection describes the opposite of what happens",
     [("the objection was made in the wrong order", "literal"),
      ("the objection has not been written down properly", "wrong_sense"),
      ("the objection is one the writer also holds", "contradicts")],
     "Backwards names a reversal of cause and effect, which the last two sentences then "
     "explain. The objection is one the writer also holds is the opposite of an objection "
     "being answered."),

    ("cause_effect", "hard", 0.90, ONE, [(0, 11)],
     'The passage ends: "{q}" According to the writer, what does the current system teach?',
     "that a child's appearance is decided by other people",
     [("that photographs should be taken more carefully", "wrong_focus"),
      ("that children should care less about appearance", "contradicts"),
      ("that schools do not value their students at all", "overreach")],
     "Being handed the image and told it is you is the lesson the sentence names. That "
     "children should care less about appearance is the vanity argument the writer has "
     "just rejected."),

    ("detail", "medium", 0.92, ONE, [(0, 8)],
     'How much extra time does the writer estimate the change would take?',
     "about four seconds for each child",
     [("about four minutes for each child", "contradicts"),
      ("no extra time at all, since frames exist", "half_right"),
      ("a full extra morning for the whole school", "overreach")],
     "Four seconds per child is the figure given. No extra time at all, since frames exist "
     "confuses the cost of taking the frames with the cost of showing them."),
  ],
 },
 {
  "title": "The Card in the First Aid Kit",
  "topic": "Functional",
  "extracts": [("", [
    "This card covers what to do before help arrives, not instead of it.",
    "Bleeding: press hard on the wound with anything clean and keep pressing.",
    "Do not lift the cloth to check, because checking restarts the bleeding you have just "
    "stopped.",
    "Add another cloth on top if the first soaks through.",
    "Burns: cool running water for twenty minutes, and twenty means twenty, not until it "
    "stops hurting.",
    "No ice, no butter, no creams.",
    "Cover loosely with cling film if you have it, because it does not stick to the burn.",
    "Suspected broken bone: do not straighten it and do not move the person unless they "
    "are in danger where they are.",
    "Support the limb in the position you found it.",
    "Snakebite: keep the person completely still and bandage firmly from the bite towards "
    "the body, then splint the limb.",
    "Do not wash the bite, because the venom on the skin helps identify the snake.",
    "In every one of these, the most useful thing you can do first is send somebody "
    "specific to call, by name.",
    "A room told to call an ambulance will often not produce anybody who has.",
  ])],
  "items": [
    ("cause_effect", "medium", 0.93, ONE, [(0, 2)],
     'The card says: "{q}" Why should the cloth not be lifted?',
     "lifting it undoes the clotting already formed",
     [("the open wound will be exposed to the risk of infection", "unsupported"),
      ("the cloth will not be clean any longer", "wrong_focus"),
      ("the bleeding has already stopped by then", "contradicts")],
     "The reason is given in the same sentence: checking restarts what pressing has "
     "achieved. The bleeding has already stopped by then would make the instruction "
     "pointless."),

    ("author_purpose", "medium", 0.92, ONE, [(0, 4)],
     'The card says: "{q}" Why does it repeat the number?',
     "because people stop as soon as the pain eases",
     [("because twenty minutes is difficult to measure", "unsupported"),
      ("because cold water works better than warm", "wrong_focus"),
      ("because twenty minutes is longer than needed", "contradicts")],
     "Naming the wrong stopping point is what the repetition guards against. Because "
     "twenty minutes is longer than needed is the opposite of an instruction insisting on "
     "the full time."),

    ("inference", "medium", 0.92, ONE, [(0, 10)],
     'The card says: "{q}" What does this tell you about treating snakebite?',
     "identifying the snake matters to the treatment",
     [("washing any wound at all is always a serious mistake", "overreach"),
      ("the venom on the skin is still dangerous", "unsupported"),
      ("the bite should be left completely uncovered", "contradicts")],
     "Keeping the venom for identification implies the identification changes what "
     "happens next. Washing a wound is always a mistake generalises a rule given for one "
     "situation."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 7)],
     'The card says: "{q}" What does this condition mean?',
     "move them only if staying put is worse",
     [("move them once help has arrived", "wrong_focus"),
      ("move them if they ask to be moved", "unsupported"),
      ("never move them under any circumstances", "contradicts")],
     "The exception is danger where they are, which is a comparison between two risks. "
     "Never move them under any circumstances drops the exception the sentence exists to "
     "make."),

    ("main_idea", "hard", 0.90, ONE, [(0, 11), (0, 12)],
     'The card ends: "{q}" Why is this placed last rather than first?',
     "it applies to every situation above it",
     [("it is the least important of the instructions", "contradicts"),
      ("it is only needed if the other steps fail", "unsupported"),
      ("it describes what to do after help arrives", "wrong_focus")],
     "Saying 'in every one of these' gathers all four situations together, which only "
     "works once they have been given. It is the least important of the instructions is "
     "the opposite of 'the most useful thing you can do first'."),

    ("detail", "medium", 0.92, ONE, [(0, 6)],
     'According to the card, why is cling film suggested for a burn?',
     "it does not stick to the burnt skin",
     [("it keeps the burn cool for longer", "unsupported"),
      ("it holds the cold water against the burn", "half_right"),
      ("it presses down firmly onto the burnt skin", "contradicts")],
     "Not sticking is the reason the card gives. It presses down firmly on the wound "
     "contradicts an instruction to cover loosely."),
  ],
 },
 {
  "title": "Grandad's Shed",
  "topic": "Narrative",
  "extracts": [("", [
    "The shed had a system and the system was not written down anywhere.",
    "Screws lived in baby food jars with the lids screwed to the shelf above, so you "
    "turned the jar and it came away in your hand.",
    "He had done that in 1974 and never explained it to anybody, and every visitor worked "
    "it out within about a minute and then felt clever for a week.",
    "Nothing in there was new.",
    "The bench was a door.",
    "The vice had come off a ship.",
    "There was a drill he had rewired twice with parts from two other drills, and it made "
    "a noise that meant he was home.",
    "After he died we spent a weekend in there deciding what to keep, which is a job "
    "nobody should do in one weekend.",
    "My uncle wanted the tools and my mother wanted the jars, and neither of them said "
    "why, and both of them were right.",
    "I took the drill, which does not work, and which I have not repaired, and which sits "
    "on a shelf in a flat where I am not allowed to drill anything.",
    "I understand exactly how little sense that makes.",
    "It is still the most useful thing in the room.",
  ])],
  "items": [
    ("inference", "medium", 0.93, ONE, [(0, 2)],
     'The passage says: "{q}" Why did visitors feel clever?',
     "they had worked out something never explained to them",
     [("Grandad had told each of them the trick beforehand", "contradicts"),
      ("the jars were difficult to open otherwise", "wrong_focus"),
      ("nobody else had ever solved the puzzle", "overreach")],
     "Solving something unexplained feels like an achievement even when it is easy. "
     "Grandad had told them the trick beforehand is ruled out by a man who never explained "
     "it to anybody."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 6)],
     'The passage says: "{q}" What does this mean?',
     "the sound told the family he was there",
     [("the drill could only be used at home", "literal"),
      ("the drill was too loud for a workshop", "wrong_focus"),
      ("the drill had been bought for the house", "unsupported")],
     "A noise that means he is home is a sound standing for a person. The drill could "
     "only be used at home reads a sentence about association as one about permission."),

    ("author_purpose", "medium", 0.92, ONE, [(0, 3), (0, 4), (0, 5)],
     'Why does the writer list: "{q}"?',
     "to show everything had been given a second life",
     [("to show the shed was badly equipped", "contradicts"),
      ("to explain how a workbench is built", "wrong_focus"),
      ("to prove that Grandad could not afford new tools", "overreach")],
     "A door as a bench and a ship's vice are objects saved rather than bought. To show "
     "the shed was badly equipped misreads resourcefulness as poverty of equipment."),

    ("inference", "hard", 0.90, ONE, [(0, 8)],
     'The passage says: "{q}" Why were both of them right?',
     "each wanted the part of him that mattered to them",
     [("the tools and the jars were worth exactly the same", "wrong_focus"),
      ("neither of them had any reason at all", "contradicts"),
      ("they had agreed on the division beforehand", "unsupported")],
     "Not saying why, and both being right, means the reasons were personal rather than "
     "arguable. Neither of them had any reason at all is the opposite of a sentence "
     "saying both were right."),

    ("main_idea", "medium", 0.92, ONE, [(0, 11)],
     'The passage ends: "{q}" What does the narrator mean?',
     "its value has nothing to do with what it does",
     [("the drill will be repaired again at some point", "unsupported"),
      ("the drill is the only tool he now owns", "wrong_focus"),
      ("the drill still works better than it looks", "contradicts")],
     "A broken drill in a flat where drilling is banned is useful only as a reminder. The "
     "drill still works better than it looks contradicts the sentence that says it does "
     "not work."),

    ("cause_effect", "medium", 0.92, ONE, [(0, 7)],
     'Why does the narrator say the weekend was too short?',
     "deciding what to keep needs longer than that",
     [("the shed was too full to sort in two days", "half_right"),
      ("the family argued for most of the weekend", "contradicts"),
      ("they were not allowed into the shed for long", "unsupported")],
     "The complaint is about the kind of job it is, not about the volume of objects. The "
     "shed was too full to sort in two days makes it a problem of quantity, which the "
     "sentence does not."),
  ],
 },
 {
  "title": "Why Ice Is Slippery",
  "topic": "Science",
  "extracts": [("", [
    "For most of two centuries the accepted explanation was pressure.",
    "The weight of a skater, concentrated on a thin blade, was said to melt the ice "
    "beneath it, and the skater slid on a film of water.",
    "It is a satisfying story and it is wrong.",
    "The pressure a skater applies lowers the melting point by a fraction of a degree, "
    "nowhere near enough to matter at minus ten.",
    "Worse, the explanation predicts that ice would not be slippery for somebody standing "
    "still in flat shoes, and it is.",
    "The current answer has two parts.",
    "The first is that the surface of ice is not solid in the way the inside is: the top "
    "layer of molecules has nothing above it to bond to, so it stays loose and mobile even "
    "well below freezing.",
    "Ice is wet before anybody touches it.",
    "The second is friction.",
    "Anything sliding across ice heats the surface slightly, which thickens that loose "
    "layer, which makes it more slippery, which lets it slide faster.",
    "It is worth noticing how long the wrong answer lasted.",
    "It survived because it sounded mechanical, it involved a number, and nobody checked "
    "whether the number was large enough.",
  ])],
  "items": [
    ("detail", "medium", 0.93, ONE, [(0, 1)],
     'The passage describes the old explanation: "{q}" What did it claim caused the '
     'slipperiness?',
     "the skater's weight melting the ice below the blade",
     [("the skater's speed warming up the blade itself", "wrong_focus"),
      ("a layer of water already present on the ice", "contradicts"),
      ("the blade being sharpened to a fine edge", "unsupported")],
     "Pressure melting a film of water under the blade is the whole of the old story. A "
     "layer of water already present on the ice is the modern answer, not the old one."),

    ("inference", "medium", 0.92, ONE, [(0, 4)],
     'The passage says: "{q}" Why is this a problem for the old explanation?',
     "slipperiness happens without any concentrated pressure",
     [("skaters are a good deal heavier than people in flat shoes", "wrong_focus"),
      ("flat shoes are not designed for walking on ice", "unsupported"),
      ("standing still on ice is perfectly safe", "contradicts")],
     "If the effect appears where the cause is absent, the cause is not doing the work. "
     "Standing still on ice is perfectly safe is the opposite of the sentence's final "
     "two words."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 7)],
     'The passage says: "{q}" What does this sentence mean?',
     "the surface behaves like liquid before contact",
     [("ice always has rain or snow lying on it", "unsupported"),
      ("ice is melting whenever it is touched", "contradicts"),
      ("water freezes onto the ice out of the air above it", "wrong_focus")],
     "The loose top layer described in the previous sentence is what makes it wet before "
     "anybody arrives. Ice always has rain or snow lying on it puts the water on the ice "
     "rather than in it."),

    ("cause_effect", "hard", 0.90, ONE, [(0, 9)],
     'The passage says: "{q}" What kind of process is being described?',
     "one that reinforces itself as it goes",
     [("one that stops as soon as it begins", "contradicts"),
      ("one that requires a very heavy weight on top", "wrong_focus"),
      ("one that only works below minus ten", "unsupported")],
     "Heat thickens the layer, the layer speeds the slide, the slide makes more heat. One "
     "that stops as soon as it begins is the reverse of the chain the sentence sets out."),

    ("author_purpose", "medium", 0.92, ONE, [(0, 11)],
     'The passage ends: "{q}" Why does the writer explain how the error survived?',
     "to show why a wrong answer can be convincing",
     [("to blame the scientists who first proposed it", "overreach"),
      ("to argue that the old explanation was never believed", "contradicts"),
      ("to explain how skating blades are designed", "wrong_focus")],
     "Sounding mechanical and carrying a number are the features that let it pass "
     "unchecked. To blame the scientists who first proposed it turns an observation about "
     "reasoning into an accusation."),

    ("main_idea", "medium", 0.92, ONE, [],
     'What is this passage doing?',
     "replacing an old explanation and asking why it lasted",
     [("describing how to skate safely on thin ice", "wrong_focus"),
      ("proving that pressure has no effect at all on ice", "overreach"),
      ("explaining how ice forms on a cold night", "unsupported")],
     "Two thirds gives the better answer and the last third asks about the error itself. "
     "Proving that pressure has no effect on ice overstates a passage that says the effect "
     "is real but far too small."),
  ],
 },
]


if __name__ == "__main__":
    GEN.mkdir(parents=True, exist_ok=True)
    qs = build(PASSAGES, BOOK, NN, CATEGORY, LABEL)
    path = GEN / f"{BOOK}_p{NN}.json"
    path.write_text(json.dumps(qs, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(qs)} questions across {len(PASSAGES)} passages -> {path}")
