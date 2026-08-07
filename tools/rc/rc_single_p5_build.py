#!/usr/bin/env python3
"""Builds rc_nsw_single_p5.json — 6 passages x 6 items = 36 answer slots (§3.1 type 3.1).

Fifth single-passage batch: a sleepover, two ships meeting off the south coast in 1802,
an argument for letting verges grow, the rules of a shared path, a piano tuner, and what
you actually hear in a shell.

Written deliberately against my own habit. Across p1 to p4 the coherence check fired on
about a third of every batch, always the same way: `contradicts` and `unsupported` for two
of the three distractors, because those are the easiest wrong answers to invent. In this
batch `wrong_focus`, `half_right`, `literal`, `wrong_sense` and `overreach` are reached for
first, and the easy two are used once each per item at most.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.rc.paired_common import build  # noqa: E402

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/reading_comprehension/generated"
NN = 5
BOOK = "rc_nsw_single"
CATEGORY = "single_passage"
LABEL = "Single-passage comprehension"
ONE = []

PASSAGES = [
 {
  "title": "The Sleepover",
  "topic": "Narrative",
  "extracts": [("", [
    "At nine o'clock I was fine.",
    "At ten I was fine in the way you are fine when you are checking whether you are fine.",
    "By half past ten the room had gone strange, the way a room does when everybody else "
    "in it is asleep and you are not.",
    "Theo's house smelled of a washing powder we do not use, which I had not noticed at "
    "all until that moment and then could not stop noticing.",
    "I lay there working out how many hours until morning, which is the worst possible "
    "sum to do.",
    "At eleven I got up and stood in the hallway, not going anywhere, just standing.",
    "Theo's mum came out of the kitchen with a cup of tea and did not look surprised.",
    "She said would you like me to ring your dad, and I said no, and she said that is "
    "fine, and neither of us moved.",
    "Then she said, the thing about the first time is that there is only one of them.",
    "I said all right.",
    "She went back into the kitchen and I went back into the room and I do not remember "
    "anything after that until Theo woke me up.",
    "I have stayed at his house eleven times since.",
    "I have never once thought about the washing powder again.",
  ])],
  "items": [
    ("inference", "medium", 0.93, ONE, [(0, 1)],
     'The narrator says: "{q}" What is he describing?',
     "the moment before he admits he is not fine",
     [("a boy who was genuinely enjoying himself", "half_right"),
      ("a boy who had already decided to go home", "overreach"),
      ("a boy checking the time on a clock", "literal")],
     "Checking whether you are fine is what people do once they have started to doubt it. "
     "A boy checking the time on a clock reads a sentence about self-examination as a "
     "sentence about a clock."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 3)],
     'The narrator writes: "{q}" Why does the smell matter?',
     "it stands for everything being unfamiliar",
     [("the washing powder had a very strong perfume", "wrong_focus"),
      ("he was allergic to that brand of washing powder", "unsupported"),
      ("Theo's family had just done a load of washing", "literal")],
     "A smell he had not noticed becomes impossible to ignore once he is unsettled, which "
     "is what homesickness does. Theo's family had just done a load of washing takes a "
     "detail about him and makes it a fact about the house."),

    ("author_purpose", "medium", 0.92, ONE, [(0, 7)],
     'The passage says: "{q}" Why does the writer include the detail that neither of them '
     'moved?',
     "to show she was letting him decide",
     [("to show that she had not heard his answer", "contradicts"),
      ("to suggest she was too tired to go back", "unsupported"),
      ("to prove she disagreed with his decision", "overreach")],
     "Standing still after the offer leaves the door open without pushing him through it. "
     "To prove she disagreed with his decision makes an argument out of a silence."),

    ("inference", "hard", 0.90, ONE, [(0, 8)],
     'The passage says: "{q}" What is Theo\'s mum telling him?',
     "the difficulty will not be repeated",
     [("first nights are always the most enjoyable", "contradicts"),
      ("he should go home and try again another time", "wrong_focus"),
      ("everybody feels exactly the same way he does", "overreach")],
     "Only one of them means the hard part is behind him once it is over. He should go "
     "home and try again another time is the opposite of what she is doing, which is "
     "helping him stay."),

    ("main_idea", "medium", 0.92, ONE, [],
     'Which sentence best sums up the story?',
     "a hard first night that never had to happen twice",
     [("a boy who was made to stay when he wanted to leave", "wrong_focus"),
      ("a friendship that was damaged by one bad evening", "contradicts"),
      ("a mother who solved a problem by ringing a parent", "half_right")],
     "Eleven visits since is the measure of what that night settled. A friendship that "
     "was damaged by one bad evening is the opposite of the ending."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 5)],
     'The narrator says: "{q}" What does "the worst possible sum" mean here?',
     "a calculation that only makes the waiting harder",
     [("a piece of homework he had been set that night", "literal"),
      ("an addition he was not able to finish", "wrong_focus"),
      ("the largest number he was able to think of", "wrong_sense")],
     "Counting the hours still to go is exactly what keeps him awake, so the sum works "
     "against him. A piece of homework he had been set reads sum as a school exercise."),
  ],
 },
 {
  "title": "Two Ships at Encounter Bay",
  "topic": "History",
  "extracts": [("", [
    "In April 1802 two ships met by accident off the south coast of what is now South "
    "Australia.",
    "One was British, commanded by Matthew Flinders; the other was French, commanded by "
    "Nicolas Baudin.",
    "Britain and France were at war.",
    "Both captains were charting the same unmapped coastline, from opposite ends, and "
    "neither had known the other was there.",
    "What happened next is the part worth knowing.",
    "They lowered boats, went aboard one another's ships, and spent two days comparing "
    "charts.",
    "Flinders told Baudin what he had found in the east; Baudin told Flinders what he had "
    "found in the west.",
    "Neither man had any orders permitting this.",
    "Both had scientific passports, issued by the other country, on the understanding that "
    "exploration was not war, and both chose to treat that understanding as real.",
    "Flinders named the place Encounter Bay, which is what it is still called.",
    "The friendliness did not survive the politics.",
    "Flinders was later held prisoner on Mauritius for six years by a French governor who "
    "did not take the same view.",
    "Two men agreeing that a coastline mattered more than a war is not how these stories "
    "usually go, and it is worth noticing when it happens.",
  ])],
  "items": [
    ("detail", "medium", 0.93, ONE, [(0, 3)],
     'The passage states: "{q}" What made the meeting an accident?',
     "each was charting the coast without knowing of the other",
     [("both ships had been blown off course by a storm", "unsupported"),
      ("the two captains had arranged to meet in secret", "contradicts"),
      ("they were charting two different coastlines entirely", "wrong_focus")],
     "Working from opposite ends of the same unmapped coast, neither aware of the other, "
     "is how they collided. They were charting two different coastlines entirely "
     "contradicts a sentence that puts them on the same one."),

    ("inference", "medium", 0.92, ONE, [(0, 7), (0, 8)],
     'The passage says: "{q}" Why was the exchange of charts unusual?',
     "the two countries were at war and nobody had ordered it",
     [("neither captain had finished mapping his section", "wrong_focus"),
      ("the charts were valuable and could have been sold", "unsupported"),
      ("scientific passports made the meeting compulsory", "overreach")],
     "No orders permitted it, and their countries were fighting, so both were choosing. "
     "Scientific passports made the meeting compulsory turns a permission into a "
     "requirement."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 8)],
     'The passage says: "{q}" What does this mean?',
     "they acted as though the agreement bound them",
     [("they wrote the understanding down in a document", "literal"),
      ("they checked that the passports were genuine", "wrong_focus"),
      ("they believed the war had already ended", "unsupported")],
     "Treating an understanding as real means behaving as if it holds, which is what "
     "sharing the charts did. They wrote the understanding down in a document turns a "
     "choice about conduct into paperwork."),

    ("cause_effect", "medium", 0.92, ONE, [(0, 11)],
     'The passage notes: "{q}" What does this show?',
     "the goodwill between the captains was not shared by others",
     [("Flinders had broken the terms of his passport", "unsupported"),
      ("Baudin had also been imprisoned for the meeting", "half_right"),
      ("the meeting at Encounter Bay never really took place at all", "contradicts")],
     "A different French official took a different view entirely, which is the sentence "
     "before it. Baudin had also been imprisoned for the meeting is not something the "
     "passage says of him at any point."),

    ("author_purpose", "hard", 0.90, ONE, [(0, 12)],
     'The passage ends: "{q}" Why does the writer finish this way?',
     "to mark the meeting as an exception worth remembering",
     [("to argue that wars are usually settled by explorers", "overreach"),
      ("to explain how the bay came to be given its name", "wrong_focus"),
      ("to suggest the two captains were disobeying badly", "half_right")],
     "Naming it as not how these stories usually go is what makes it worth telling. To "
     "suggest the two captains were disobeying badly takes the fact that they had no "
     "orders and turns admiration into a complaint."),

    ("main_idea", "medium", 0.92, ONE, [],
     'The passage is best described as —',
     "an account of two enemies choosing to cooperate",
     [("a description of how a coastline was mapped", "wrong_focus"),
      ("an argument that the two captains were wrong", "contradicts"),
      ("a comparison of British and French ships", "unsupported")],
     "The charts and the imprisonment both serve a story about the two days in between. "
     "An argument that the two captains were wrong reverses a passage that ends by "
     "calling the meeting worth noticing."),
  ],
 },
 {
  "title": "Let the Grass Grow",
  "topic": "Opinion",
  "extracts": [("", [
    "Councils mow the strip of grass between the footpath and the road about eighteen "
    "times a year.",
    "Nobody sits on it.",
    "Nobody plays on it.",
    "It exists because at some point somebody decided that short grass was what tidy "
    "looked like, and no one has revisited the decision since.",
    "Mowing that strip four times a year instead of eighteen would save money, which is "
    "the least interesting reason to do it.",
    "The interesting reason is that grass left to flower feeds insects, and insects feed "
    "everything else.",
    "A verge mown fortnightly is, biologically speaking, a car park with a green surface.",
    "The objection is that long grass looks neglected, and that objection is real.",
    "It is also solvable, and several councils have solved it, by mowing a neat strip "
    "along each edge and leaving the middle.",
    "The eye reads the mown edge as care and stops worrying about the rest.",
    "This is not a proposal to let a suburb go wild.",
    "It is a proposal to stop spending money making a place less alive, and to admit that "
    "tidy is a habit rather than a value.",
  ])],
  "items": [
    ("main_idea", "medium", 0.93, ONE, [],
     'What is the writer\'s central claim?',
     "frequent mowing costs money and does harm for no gain",
     [("all mowing of public land should be stopped", "overreach"),
      ("councils should spend more on their verges", "contradicts"),
      ("long grass is more attractive to look at than short grass", "wrong_focus")],
     "The claim is about the frequency and what it costs in both money and life. All "
     "mowing of public land should be stopped is what the second-last sentence "
     "explicitly denies."),

    ("author_purpose", "medium", 0.92, ONE, [(0, 7)],
     'The writer says: "{q}" Why concede this?',
     "to answer the objection rather than ignore it",
     [("to agree that the proposal will not work", "contradicts"),
      ("to explain how councils choose their contractors", "wrong_focus"),
      ("to show that appearance is the only thing that matters", "overreach")],
     "Granting the objection is what earns the solution offered in the next sentence. To "
     "agree that the proposal will not work is the opposite of a paragraph that goes on "
     "to solve it."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 6)],
     'The writer says: "{q}" What is the point of the comparison?',
     "it is green but supports almost no life",
     [("it is used for parking cars along the road", "literal"),
      ("it is the only green space left in the suburb", "overreach"),
      ("it is the same size as an average car park", "wrong_focus")],
     "A car park with a green surface is a place that looks alive and is not. It is used "
     "for parking cars along the road takes a comparison for a description of what "
     "happens there."),

    ("inference", "medium", 0.92, ONE, [(0, 9)],
     'The writer says: "{q}" Why does the mown edge work?',
     "a sign of care changes how the whole strip is read",
     [("the mown edge is the only part anybody walks on", "unsupported"),
      ("the edge is mown far more often than the middle", "half_right"),
      ("the middle is left long because nobody can reach it", "contradicts")],
     "The eye takes the edge as evidence of intention and stops inspecting the rest. The "
     "edge is mown far more often than the middle is true of the method but is not why "
     "it satisfies people."),

    ("cause_effect", "hard", 0.90, ONE, [(0, 5)],
     'The writer says: "{q}" What chain of effects is being described?',
     "flowers feed insects, and insects feed other animals",
     [("insects damage the grass and stop it flowering", "contradicts"),
      ("mowing removes insects that would eat the flowers", "wrong_focus"),
      ("flowering grass is the only food insects will take", "overreach")],
     "Two steps are given in one sentence, with everything else at the end of the chain. "
     "Flowering grass is the only food insects will take goes far beyond a sentence about "
     "one source of food."),

    ("detail", "medium", 0.92, ONE, [(0, 0), (0, 4)],
     'The passage says: "{q}" What reduction is the writer proposing?',
     "from about eighteen mowings a year down to four",
     [("from eighteen mowings a year down to none at all", "overreach"),
      ("from twelve mowings a year down to about four", "contradicts"),
      ("a reduction the council has already agreed to", "unsupported")],
     "Both figures are given, one at the start and one in the proposal. From eighteen "
     "mowings a year down to none at all goes further than a writer who names four."),
  ],
 },
 {
  "title": "Sharing the Path",
  "topic": "Functional",
  "extracts": [("", [
    "This is a shared path, which means bicycles and pedestrians use the same surface and "
    "neither has the right of way by default.",
    "Keep left unless you are overtaking, the same as a road.",
    "Riders: ring your bell or call out well before you reach somebody, not as you pass "
    "them.",
    "A bell rung two metres behind a walker is a fright, not a warning.",
    "Walkers: if you hear a bell, keep going in a straight line rather than jumping aside.",
    "A rider has already planned a way around you, and the plan does not survive you "
    "moving.",
    "Dogs must be on a lead no longer than two metres.",
    "A long lead across a shared path is invisible to somebody travelling at twenty "
    "kilometres an hour.",
    "Headphones are not banned, but if you cannot hear a bell then you cannot use the "
    "warning the bell is for.",
    "Riders should pass at a speed that would let them stop if somebody stepped out, which "
    "on a busy Sunday is slower than most people think.",
    "None of this is enforced.",
    "All of it works only because most people do it.",
  ])],
  "items": [
    ("cause_effect", "medium", 0.93, ONE, [(0, 5)],
     'The rules say: "{q}" Why should a walker not jump aside?',
     "the rider has chosen a gap that the movement closes",
     [("jumping aside is against the rules of the path", "wrong_focus"),
      ("the walker may fall over on the loose surface", "unsupported"),
      ("the rider has already stopped by that point", "contradicts")],
     "Moving unpredictably ruins a plan already made around where you were. Jumping aside "
     "is against the rules of the path turns a reason into a prohibition, which is not "
     "how the sentence works."),

    ("inference", "medium", 0.92, ONE, [(0, 3)],
     'The rules say: "{q}" What is the point being made?',
     "a warning given too late is not a warning",
     [("bells are too quiet to be heard at a distance", "contradicts"),
      ("riders should not use a bell at all on the path", "overreach"),
      ("walkers are frightened by any sudden noise", "wrong_focus")],
     "Timing is what turns the same sound from useful into alarming. Riders should not "
     "use a bell at all on the path is the opposite of the instruction it explains."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 7)],
     'The rules say: "{q}" What does "invisible" mean here?',
     "not seen in time to be avoided",
     [("impossible to see under any conditions", "overreach"),
      ("made of a material that cannot be seen", "literal"),
      ("too thin to hold a dog of any size", "wrong_focus")],
     "At twenty kilometres an hour a thin lead is not noticed until it is too late, which "
     "is a fact about speed rather than about the lead. Impossible to see under any "
     "conditions removes the speed the sentence depends on."),

    ("author_purpose", "medium", 0.92, ONE, [(0, 8)],
     'The rules say: "{q}" Why are headphones mentioned but not banned?',
     "the writer explains the cost rather than forbidding it",
     [("headphones cannot be banned on a public path", "unsupported"),
      ("the writer thinks headphones are perfectly safe on a path", "contradicts"),
      ("headphones are only a problem for riders", "wrong_focus")],
     "The sentence hands the reader the consequence and leaves the decision alone. The "
     "writer thinks headphones are perfectly safe contradicts a sentence built around "
     "what you lose."),

    ("main_idea", "hard", 0.90, ONE, [(0, 10), (0, 11)],
     'The rules end: "{q}" Taken as a whole, these rules aim to —',
     "explain why each courtesy matters, since nothing is enforced",
     [("list the penalties that apply to path users", "contradicts"),
      ("describe how the path was designed and built", "wrong_focus"),
      ("warn readers that the path is dangerous to use at all", "overreach")],
     "With no enforcement, the only thing that makes a rule work is the reader "
     "understanding it. List the penalties that apply to path users is ruled out by the "
     "line saying none of this is enforced."),

    ("detail", "medium", 0.92, ONE, [(0, 0)],
     'According to the rules, who has right of way on a shared path?',
     "neither riders nor walkers, by default",
     [("riders, because they are travelling faster", "contradicts"),
      ("walkers, since a path is built for walking on", "overreach"),
      ("whoever is keeping to the left of the path", "half_right")],
     "The first sentence says neither has it by default. Whoever is keeping to the left "
     "of the path takes a separate rule and makes it the answer to this one."),
  ],
 },
 {
  "title": "The Piano Tuner",
  "topic": "Narrative",
  "extracts": [("", [
    "The piano tuner came once a year and took four hours over an instrument nobody in the "
    "school could really play.",
    "He was old enough that somebody always carried his case in for him, which he allowed "
    "without comment.",
    "For the first hour he did nothing that sounded like music.",
    "He struck one note and then another and listened to the space between them, and if "
    "you stood near the door you could hear him breathing.",
    "Ms Cardoso said we were not to disturb him and then sat in the back of the hall for "
    "twenty minutes herself, marking nothing.",
    "I asked him once why it took so long when the piano sounded fine to me.",
    "He said it sounds fine to you because you have only heard it out of tune.",
    "I did not understand that for a year.",
    "The following spring he came again, and this time I sat in the hall on purpose, and "
    "at the end he played eight bars of something I have never identified.",
    "It was the same piano.",
    "It was not the same piano at all.",
  ])],
  "items": [
    ("inference", "medium", 0.93, ONE, [(0, 4)],
     'The passage says: "{q}" What does this suggest about Ms Cardoso?',
     "she wanted to listen without saying so",
     [("she was checking that he did the work properly", "wrong_focus"),
      ("she had a large amount of marking to finish", "contradicts"),
      ("she disliked being in the hall during lessons", "unsupported")],
     "Marking nothing for twenty minutes is sitting there for another reason. She had a "
     "large amount of marking to finish is exactly what 'marking nothing' rules out."),

    ("inference", "hard", 0.90, ONE, [(0, 6)],
     'The passage says: "{q}" What does the tuner mean?',
     "the narrator has no version of the piano to compare it with",
     [("the narrator does not listen carefully enough", "half_right"),
      ("the piano has always sounded exactly the same to everybody", "contradicts"),
      ("the narrator cannot hear high notes properly", "wrong_focus")],
     "You cannot notice what is missing if you have never heard it present. The narrator "
     "does not listen carefully enough puts the fault in his attention rather than in his "
     "experience."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 3)],
     'The passage says: "{q}" What does listening to "the space between them" mean?',
     "attending to how the two notes sound together",
     [("measuring the distance between the two keys", "literal"),
      ("waiting for the sound of the first to stop", "wrong_focus"),
      ("choosing which of the two notes is louder", "half_right")],
     "Tuning is done by the relationship between notes, not by either note alone. "
     "Measuring the distance between the two keys reads a phrase about sound as one about "
     "the keyboard."),

    ("author_purpose", "medium", 0.92, ONE, [(0, 1)],
     'Why does the writer mention: "{q}"?',
     "to show his age without making a point of it",
     [("to suggest he was no longer able to work", "contradicts"),
      ("to suggest the school could not afford a younger tuner", "unsupported"),
      ("to show that the case was extremely heavy", "wrong_focus")],
     "Somebody always carrying the case, and his allowing it, says his age quietly. To "
     "show that the case was extremely heavy attaches the detail to the object rather "
     "than to the man."),

    ("main_idea", "hard", 0.90, ONE, [(0, 9), (0, 10)],
     'The passage ends: "{q}" What does the narrator come to understand?',
     "he had not been able to hear the difference before",
     [("the school had replaced the piano over summer", "literal"),
      ("the tuner had damaged the piano while working", "contradicts"),
      ("the piano sounds different in spring than winter", "unsupported")],
     "Two flatly contradictory sentences are the only way to say that the object is "
     "unchanged and his hearing is not. The school had replaced the piano over summer "
     "takes a figure of speech for a fact."),

    ("cause_effect", "medium", 0.92, ONE, [(0, 8)],
     'Why did the narrator sit in the hall the following spring?',
     "he wanted to hear what he had missed the year before",
     [("Ms Cardoso had told the class to attend", "contradicts"),
      ("he had been asked to carry the tuner's case", "unsupported"),
      ("he wanted to identify the piece of music being played", "wrong_focus")],
     "'On purpose' marks a decision made because of the previous year. Ms Cardoso had "
     "told the class to attend contradicts a teacher who told them not to disturb him."),
  ],
 },
 {
  "title": "What You Hear in a Shell",
  "topic": "Science",
  "extracts": [("", [
    "Hold a large shell to your ear and you hear the sea.",
    "You do not hear the sea.",
    "What you hear is the noise already around you, folded back at you by the shape of "
    "the shell.",
    "A room is never silent.",
    "There is traffic, air moving, your own blood, the hum of a fridge two rooms away, and "
    "your brain edits almost all of it out because none of it is news.",
    "A curved hard surface near your ear stops that editing working.",
    "Certain frequencies bounce around inside the shell and come back louder than they "
    "went in, and the mixture that results is broad and shifting and unlike any single "
    "sound.",
    "That is why it resembles surf, which is also broad and shifting.",
    "The test is easy and slightly disappointing.",
    "Take the shell into a very quiet room and the sea gets quieter.",
    "Take it somewhere genuinely loud and the sea gets louder.",
    "An empty cup does the same thing, though nobody writes poems about cups.",
  ])],
  "items": [
    ("detail", "medium", 0.93, ONE, [(0, 2)],
     'The passage states: "{q}" What are you actually hearing?',
     "the sounds already in the room around you",
     [("the sound of the sea recorded in the shell", "contradicts"),
      ("the movement of air inside the shell itself", "half_right"),
      ("the sound of your own blood and nothing else", "overreach")],
     "The noise is already present; the shell only sends it back. The sound of your own "
     "blood and nothing else takes one item from a list of several."),

    ("inference", "medium", 0.92, ONE, [(0, 4)],
     'The passage says: "{q}" Why does this matter to the explanation?',
     "the sound was always there but unnoticed",
     [("the brain is unable to hear quiet sounds", "wrong_focus"),
      ("the brain invents sounds that are not there", "contradicts"),
      ("the fridge hum is louder than the traffic outside", "unsupported")],
     "If the noise is edited out rather than absent, something that defeats the editing "
     "will reveal it. The brain invents sounds that are not there is the opposite of a "
     "passage about sounds being removed."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 5)],
     'The passage says: "{q}" What does "editing" refer to?',
     "the way the brain ignores unchanging noise",
     [("cutting parts out of a piece of writing", "wrong_sense"),
      ("the shell changing the shape of the sound", "wrong_focus"),
      ("a person choosing what to listen to", "half_right")],
     "The word is used for what the brain does automatically with familiar noise. A "
     "person choosing what to listen to makes deliberate something the passage describes "
     "as happening without you."),

    ("cause_effect", "medium", 0.92, ONE, [(0, 9), (0, 10)],
     'The passage says: "{q}" What do these two tests show?',
     "the sound comes from the room, not the shell",
     [("the shell works better in a quiet room", "contradicts"),
      ("the shell changes shape in different rooms", "literal"),
      ("loud rooms damage the surface of the shell", "unsupported")],
     "The sea follows the room's noise up and down, which is what you would expect if the "
     "room supplies it. The shell works better in a quiet room is the reverse of the "
     "first test's result."),

    ("author_purpose", "medium", 0.92, ONE, [(0, 11)],
     'The passage ends: "{q}" Why finish with the cup?',
     "to show the effect has nothing to do with shells",
     [("to argue that cups should appear in more poems", "literal"),
      ("to explain how cups are made from hard material", "wrong_focus"),
      ("to prove that shells are better than cups for this", "contradicts")],
     "If any hard curved object does it, the shell is not the cause. To prove that shells "
     "are better than cups for this is the opposite of a sentence saying they do the same "
     "thing."),

    ("main_idea", "hard", 0.90, ONE, [],
     'Which belief does this passage set out to overturn?',
     "a familiar belief about what a shell contains",
     [("the idea that a room can ever be silent", "half_right"),
      ("the idea that a shell holds no sound at all", "contradicts"),
      ("a mistake about how shells are formed", "wrong_focus")],
     "The first two sentences state the belief and deny it, and the rest explains why. A "
     "mistake about how shells are formed is a subject the passage never touches."),
  ],
 },
]


if __name__ == "__main__":
    GEN.mkdir(parents=True, exist_ok=True)
    qs = build(PASSAGES, BOOK, NN, CATEGORY, LABEL)
    path = GEN / f"{BOOK}_p{NN}.json"
    path.write_text(json.dumps(qs, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(qs)} questions across {len(PASSAGES)} passages -> {path}")
