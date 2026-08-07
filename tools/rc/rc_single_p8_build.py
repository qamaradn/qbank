#!/usr/bin/env python3
"""Builds rc_nsw_single_p8.json — 5 passages x 8 items = 40 answer slots (§3.1 type 3.1).

Final single-passage batch. 7 x 36 + 40 = 292, which closes the type and, with the
vocabulary cloze top-up, closes NSW Reading at 649.

Eight items per passage rather than six, which is the top of the 4–8 range §3.4 allows and
means five passages instead of seven. Subcategory mix for forty: inference 10, vocabulary
in context 8, author's purpose 8, main idea 6, detail 4, cause and effect 4.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.rc.paired_common import build  # noqa: E402

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/reading_comprehension/generated"
NN = 8
BOOK = "rc_nsw_single"
CATEGORY = "single_passage"
LABEL = "Single-passage comprehension"
ONE = []

PASSAGES = [
 {
  "title": "The Change",
  "topic": "Narrative",
  "extracts": [("", [
    "In a relay the baton is not passed so much as caught up with.",
    "The outgoing runner starts before the incoming one arrives, facing away, and puts a "
    "hand back into a space where the baton is going to be.",
    "You never see it.",
    "You have twenty metres of marked track to get it done in and if you leave the box "
    "without it the whole team is out.",
    "Our team practised the change more than we practised running, which felt wrong until "
    "the day it did not.",
    "At the zone carnival I was second leg and Wren was third.",
    "I came in half a metre wide because somebody had cut across me on the bend, and Wren "
    "had already gone.",
    "She could not see me and I could not reach her hand.",
    "What she did was keep running and move her hand, once, about fifteen centimetres to "
    "the left, which is not something anybody teaches you.",
    "The baton went in.",
    "We came third, which nobody remembers.",
    "I remember a hand moving fifteen centimetres in the one direction that could still "
    "work.",
  ])],
  "items": [
    ("inference", "medium", 0.93, ONE, [(0, 1), (0, 2)],
     'The passage says: "{q}" Why can the outgoing runner not see the baton?',
     "she is already running and facing forward",
     [("the baton is too small to be seen clearly", "wrong_focus"),
      ("she is required to close her eyes in the box", "unsupported"),
      ("the incoming runner hides it until the last moment", "overreach")],
     "Facing away and reaching back is the whole description. The baton is too small to "
     "be seen clearly makes it a problem of size rather than of direction."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 0)],
     'The passage opens: "{q}" What does "caught up with" mean here?',
     "the baton reaches a hand that is already moving",
     [("the runners must catch each other on the track", "literal"),
      ("the team has to make up ground on the others", "wrong_focus"),
      ("the baton is thrown forward to be collected", "contradicts")],
     "The phrase describes a handover between two people already in motion. The baton is "
     "thrown forward to be collected is ruled out by a hand put back into a space."),

    ("detail", "medium", 0.92, ONE, [(0, 3)],
     'According to the passage, what happens if the change is not completed in the box?',
     "the whole team is disqualified",
     [("the outgoing runner must start again", "unsupported"),
      ("the team loses twenty metres of ground", "wrong_focus"),
      ("only the second runner is disqualified", "half_right")],
     "The whole team is out is stated directly. Only the second runner is disqualified "
     "narrows a penalty the passage says falls on everybody."),

    ("author_purpose", "medium", 0.92, ONE, [(0, 4)],
     'Why does the writer mention: "{q}"?',
     "to prepare the reader for why the change worked",
     [("to suggest the team could not run particularly fast", "overreach"),
      ("to explain why the team came third overall", "wrong_focus"),
      ("to show the coach had the wrong priorities", "contradicts")],
     "Practising the change more than the running is what made an unteachable adjustment "
     "possible. To show the coach had the wrong priorities is reversed by 'until the day "
     "it did not'."),

    ("inference", "hard", 0.91, ONE, [(0, 8)],
     'The passage says: "{q}" Why does the writer add that nobody teaches it?',
     "the adjustment came from practice rather than instruction",
     [("the coach had never run in a relay himself", "unsupported"),
      ("Wren had been taught that exact move by somebody else beforehand", "contradicts"),
      ("nobody had ever made that mistake before", "overreach")],
     "Hours of changes build a feel that no instruction covers. Wren had been taught the "
     "move by somebody else is exactly what the clause denies."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 5)],
     'The passage says: "{q}" What does "second leg" mean here?',
     "the second stage of the race, run by one member of the team",
     [("one of the runner's two legs", "literal"),
      ("the second-fastest runner in the whole team", "overreach"),
      ("the runner's second attempt at the race", "wrong_sense")],
     "A relay is run in stages and each runner takes one, which is the sense of leg here. "
     "One of the runner's two legs takes the word in its everyday meaning."),

    ("main_idea", "hard", 0.90, ONE, [(0, 10), (0, 11)],
     'The passage ends: "{q}" What is the writer saying matters?',
     "a small skilled adjustment nobody else noticed",
     [("the disappointment of finishing third", "contradicts"),
      ("the unfairness of being cut off on the bend", "wrong_focus"),
      ("the importance of practising the change often", "half_right")],
     "The placing is dismissed in the same breath as the hand is remembered. The "
     "disappointment of finishing third is the reading 'which nobody remembers' rules "
     "out."),

    ("author_purpose", "medium", 0.92, ONE, [(0, 2)],
     'Why is "{q}" set as a sentence of its own?',
     "to stress how blind the handover is",
     [("to show the writer was not watching", "wrong_focus"),
      ("to suggest the baton had gone missing", "contradicts"),
      ("to explain how a relay is scored", "unsupported")],
     "Three words alone carry the strangeness of reaching for something you cannot look "
     "at. To suggest the baton had gone missing turns a fact about vision into an event."),
  ],
 },
 {
  "title": "Four Numbers",
  "topic": "History",
  "extracts": [("", [
    "Australia had no postcodes until 1967.",
    "Before that a letter carried a suburb and a state, and every one of them was read by "
    "a person who had to know that Richmond exists in both Victoria and Tasmania.",
    "Mail was sorted by hand, at night, by people who had memorised their district.",
    "It worked, in the sense that letters arrived, and it did not scale.",
    "The post office introduced four digits and asked the country to learn them, which is "
    "a strange thing to ask.",
    "The campaign used a cartoon character called Mr Zip, and it worked well enough that "
    "within two years most mail carried a code.",
    "The digits are not random.",
    "The first says which state, the second the region within it, and the last two narrow "
    "it to a delivery area.",
    "That structure is why a machine can begin sorting a letter after reading one digit "
    "and finish after four.",
    "The interesting part is what was lost.",
    "A sorter who knew a district could correct a wrong suburb, recognise a family name, "
    "or work out that a letter addressed to a hospital ward belonged in the next street.",
    "A machine reading four digits cannot do any of that, and does not need to, because it "
    "is right far more often than the person was.",
    "Most improvements are like this: they are not free, and the thing they cost is "
    "usually judgement.",
  ])],
  "items": [
    ("detail", "medium", 0.93, ONE, [(0, 7)],
     'The passage states: "{q}" What does the second digit indicate?',
     "the region within a state",
     [("the state the letter is going to", "contradicts"),
      ("the individual street of delivery", "wrong_focus"),
      ("the year the postcode was issued", "unsupported")],
     "State, region, then delivery area is the order given. The state the letter is going "
     "to is what the first digit does."),

    ("inference", "medium", 0.92, ONE, [(0, 3)],
     'The passage says: "{q}" What does this mean?',
     "it worked but could not handle growth",
     [("it delivered letters to the wrong addresses", "contradicts"),
      ("it was too expensive for the post office", "unsupported"),
      ("it needed more sorters than were available", "half_right")],
     "Letters arrived, and the method could not be enlarged, which is the distinction the "
     "sentence draws. It delivered letters to the wrong addresses is denied by 'letters "
     "arrived'."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 2)],
     'The passage says: "{q}" What does "their district" mean here?',
     "the streets and suburbs one sorter's own share of the mail covered",
     [("the building the sorters worked in at night", "wrong_sense"),
      ("the state that each letter was addressed to", "overreach"),
      ("the hours of the night the sorters worked", "wrong_focus")],
     "A district here is the patch of the map a sorter had learnt by heart. The building "
     "the sorters worked in reads district as a place they were, not a place they knew."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 5)],
     'The passage says: "{q}" What does "worked well enough" suggest?',
     "the campaign succeeded without being a complete success",
     [("the campaign was extremely popular with everybody", "overreach"),
      ("the campaign barely functioned at all", "wrong_sense"),
      ("the cartoon character was unusually well drawn", "wrong_focus")],
     "Enough measures the campaign against what it needed to do, not against perfection. "
     "Extremely popular with everybody claims more than the phrase allows."),

    ("inference", "hard", 0.90, ONE, [(0, 10)],
     'The passage describes what a human sorter could do: "{q}" What did that ability '
     'depend on?',
     "knowing the district as a place rather than as data",
     [("having more time to sort each letter", "wrong_focus"),
      ("being able to read handwriting better", "half_right"),
      ("the number of letters being far smaller in those years", "unsupported")],
     "Recognising a family name or placing a ward requires knowledge no code contains. "
     "Being able to read handwriting better is a different skill and not the one the "
     "examples show."),

    ("author_purpose", "medium", 0.92, ONE, [(0, 11)],
     'Why does the writer add: "{q}"?',
     "to keep the loss from sounding like an argument against the change",
     [("to suggest the machines should be switched off", "contradicts"),
      ("to explain how the postcodes came to be printed on every letter", "wrong_focus"),
      ("to prove the human sorters were often careless", "overreach")],
     "Conceding that the machine is more accurate stops the paragraph becoming nostalgia. "
     "To suggest the machines should be switched off is the opposite of what the clause "
     "concedes."),

    ("main_idea", "medium", 0.92, ONE, [(0, 12)],
     'The passage ends: "{q}" What is the writer\'s general point?',
     "an improvement can be real and still cost something",
     [("machines should not replace people at work", "contradicts"),
      ("postcodes were introduced far too late to be of any help", "half_right"),
      ("judgement is more valuable than accuracy is", "overreach")],
     "Not free, and what it costs is judgement, is the claim stated outright. Judgement is "
     "more valuable than accuracy is goes further than a writer who grants the machine is "
     "right more often."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 9)],
     'The passage says: "{q}" What does "what was lost" refer to?',
     "an ability the human sorters had that a machine does not",
     [("letters that never arrived at the right address", "literal"),
      ("the jobs the post office no longer needed to fill", "wrong_focus"),
      ("the money the post office spent on the campaign", "unsupported")],
     "The sentences after it describe judgement the sorters could exercise, and that is "
     "the loss. Letters that never arrived takes lost in its ordinary postal sense."),
  ],
 },
 {
  "title": "The Case for the Long Lunch",
  "topic": "Opinion",
  "extracts": [("", [
    "Most Australian primary schools give students about forty-five minutes of break "
    "across a day, in two pieces.",
    "Some schools have cut it further, on the reasoning that more class time produces more "
    "learning, which sounds obvious and is not supported by anything.",
    "The schools that have gone the other way and lengthened lunch report the same "
    "cluster of results: fewer playground incidents, fewer students sent out of class "
    "after lunch, and no fall in academic results.",
    "The explanation offered is not that play is magic.",
    "It is that a fifteen-minute break is long enough to start a game and not long enough "
    "to finish one, and a game that ends badly comes back into the classroom with the "
    "students.",
    "Lengthen the break and the game reaches its own end.",
    "There is an objection worth taking seriously, which is that longer breaks mean less "
    "supervised time, and that the students who struggle socially will struggle for "
    "longer.",
    "That is true, and it is an argument for more thought about what happens in a break, "
    "not for making the break shorter.",
    "Shortening it does not remove the difficulty.",
    "It just moves the difficulty into a room where somebody is trying to teach.",
  ])],
  "items": [
    ("inference", "medium", 0.93, ONE, [(0, 4)],
     'The writer says: "{q}" What is the problem with a fifteen-minute break?',
     "a game is interrupted rather than concluded",
     [("students do not have time to eat their lunch", "unsupported"),
      ("teachers cannot supervise a short break properly", "wrong_focus"),
      ("students refuse to come back into the classroom", "overreach")],
     "Started and not finished is the exact complaint, and the consequence follows in the "
     "same sentence. Students do not have time to eat their lunch is a different problem "
     "the passage never raises."),

    ("author_purpose", "medium", 0.92, ONE, [(0, 3)],
     'Why does the writer say: "{q}"?',
     "to rule out a vaguer explanation before giving a precise one",
     [("to argue that play has no value for children", "contradicts"),
      ("to suggest the schools reporting this have simply been lucky", "half_right"),
      ("to describe what children do during a break", "wrong_focus")],
     "Rejecting the sentimental version makes room for the mechanical one that follows. To "
     "argue that play has no value for children is not a claim a piece arguing for longer "
     "play would make."),

    ("detail", "medium", 0.92, ONE, [(0, 2)],
     'What results do the schools with longer breaks report?',
     "fewer incidents, fewer removals, and no academic drop",
     [("better academic results and fewer incidents", "half_right"),
      ("fewer incidents but a fall in academic results", "contradicts"),
      ("fewer incidents and noticeably shorter lessons after lunch", "literal")],
     "Three findings are listed and the third is explicitly no change rather than "
     "improvement. Better academic results and fewer incidents claims a gain the passage "
     "does not report."),

    ("inference", "medium", 0.92, ONE, [(0, 1)],
     'The writer says: "{q}" What is being criticised?',
     "an assumption nobody has tested",
     [("a policy that no school actually follows", "contradicts"),
      ("a claim that has been proved false in schools", "half_right"),
      ("teachers who want longer breaks for themselves", "unsupported")],
     "Sounds obvious and is not supported is the charge: unexamined rather than "
     "disproved. A claim that has been proved false in schools is stronger than 'not "
     "supported by anything'."),

    ("author_purpose", "medium", 0.92, ONE, [(0, 6)],
     'Why does the writer raise the objection about supervision?',
     "to answer the strongest case against the proposal",
     [("to show the proposal cannot work in practice", "contradicts"),
      ("to explain how playgrounds are supervised", "wrong_focus"),
      ("to suggest struggling students should stay inside", "unsupported")],
     "Calling it worth taking seriously and then answering it is what strengthens the "
     "argument. To show the proposal cannot work in practice is the opposite of the reply "
     "given in the next sentence."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 9)],
     'The writer ends: "{q}" What does "moves the difficulty" mean?',
     "the same problem appears somewhere less suitable",
     [("the difficulty becomes easier to solve", "contradicts"),
      ("students are physically moved between rooms", "literal"),
      ("the difficulty is shared out among more people", "half_right")],
     "The trouble is relocated into a lesson rather than reduced. Students are physically "
     "moved between rooms reads a figure of speech as a description of what happens."),

    ("main_idea", "hard", 0.90, ONE, [],
     'What is the shape of the writer\'s argument?',
     "a short break creates the problem it is meant to avoid",
     [("longer breaks improve academic results directly", "contradicts"),
      ("supervision matters a good deal more than the length of a break", "half_right"),
      ("schools should abolish scheduled breaks altogether", "overreach")],
     "Cutting the break to protect lessons is what sends the trouble into the lesson. "
     "Longer breaks improve academic results directly is precisely the claim the passage "
     "declines to make."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 5)],
     'The writer says: "{q}" What does "reaches its own end" mean?',
     "the game finishes the way the players were heading anyway",
     [("the game is stopped by a teacher on duty", "contradicts"),
      ("the game turns out to have had no point to it", "wrong_sense"),
      ("the game spreads to the end of the playground", "literal")],
     "Its own end means the finish the game was moving towards, not one imposed on it. "
     "Stopped by a teacher is exactly the ending the phrase rules out."),
  ],
 },
 {
  "title": "Before the Storm",
  "topic": "Functional",
  "extracts": [("", [
    "A severe weather warning gives you hours, not days, so this list is ordered by what "
    "goes wrong first.",
    "Outside, before anything else: anything that can be picked up by wind will be.",
    "Trampolines, bins, outdoor chairs, the empty pot nobody has moved since March.",
    "A trampoline in a strong wind does not roll, it flies, and it does not stop at your "
    "fence.",
    "Clear the gutters if you can do it safely, and do not go on the roof if it has "
    "already started.",
    "Most storm damage inside a house is water that came in through a blocked gutter, not "
    "water that came through the roof.",
    "Park the car away from trees, and remember that a tree that has stood for forty years "
    "has stood in dry soil.",
    "Wet soil holds a tree far less well.",
    "Inside: charge everything now, fill a few bottles, and find the torch before you need "
    "it rather than in the dark.",
    "A phone at nine per cent is not a torch.",
    "If the power goes out, leave one light switched on so that you know when it comes "
    "back.",
    "Do not open the fridge to check whether the food is still cold, because opening it is "
    "what makes it warm.",
  ])],
  "items": [
    ("author_purpose", "medium", 0.93, ONE, [(0, 0)],
     'The list opens: "{q}" Why explain the ordering?',
     "so the reader does the most urgent things first",
     [("to warn that the storm will last for several days yet", "contradicts"),
      ("to explain how weather warnings are issued", "wrong_focus"),
      ("to suggest the list is too long to finish", "overreach")],
     "Hours rather than days is the reason the order matters. To warn that the storm will "
     "last several days reverses the sentence's own comparison."),

    ("inference", "medium", 0.92, ONE, [(0, 3)],
     'The list says: "{q}" What is the warning here?',
     "a trampoline can travel a long way and cause damage",
     [("trampolines are easily damaged by strong wind", "wrong_focus"),
      ("trampolines should never be owned anywhere near storm areas", "overreach"),
      ("a fence will usually stop a trampoline moving", "contradicts")],
     "Flying rather than rolling, and not stopping at the fence, is about where it ends "
     "up. Trampolines are easily damaged by strong wind worries about the wrong object."),

    ("cause_effect", "medium", 0.92, ONE, [(0, 5)],
     'According to the list, what causes most storm damage inside a house?',
     "water entering through a blocked gutter",
     [("water coming straight through the roof", "contradicts"),
      ("wind forcing rain under the front door", "unsupported"),
      ("trees falling onto the roof of the house", "wrong_focus")],
     "The sentence contrasts the two explicitly and names the gutter. Water coming "
     "straight through the roof is the alternative it rules out."),

    ("inference", "hard", 0.90, ONE, [(0, 6), (0, 7)],
     'The list says: "{q}" Why does the age of a tree not guarantee safety?',
     "it has never been tested in soil this wet",
     [("old trees are weaker than young trees", "unsupported"),
      ("forty years is not a long time for a tree", "wrong_focus"),
      ("trees are always more dangerous in wind", "overreach")],
     "Standing for forty years in dry soil says nothing about wet soil, which is the "
     "point. Old trees are weaker than young trees is a claim the passage never makes."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 9)],
     'The list says: "{q}" What is meant by this?',
     "a nearly flat phone cannot be relied on for light",
     [("phones do not produce light at all", "contradicts"),
      ("torches are cheaper to buy than phones", "wrong_focus"),
      ("a phone should never be relied on during a storm", "overreach")],
     "Nine per cent will not last, which is why a torch is listed separately. Phones do "
     "not produce light at all is contradicted by the comparison being made."),

    ("author_purpose", "medium", 0.92, ONE, [(0, 10)],
     'Why does the list suggest leaving one light switched on?',
     "so the return of power is obvious",
     [("so the house is not completely dark", "half_right"),
      ("so the electricity company can be billed", "unsupported"),
      ("so the house stays warm through the night", "contradicts")],
     "Knowing when it comes back is the reason given. So the house is not completely dark "
     "is a benefit, but the light will be off while the power is out."),

    ("detail", "medium", 0.92, ONE, [(0, 11)],
     'What reason does the list give for not opening the fridge?',
     "opening it is what warms the contents",
     [("the door may be blown open by the wind", "unsupported"),
      ("the light inside will drain the power", "wrong_focus"),
      ("the food will already have gone bad", "contradicts")],
     "The act of checking is what causes the harm being checked for. The food will "
     "already have gone bad is the opposite of an instruction meant to keep it cold."),

    ("main_idea", "hard", 0.90, ONE, [],
     'What makes this list more than a set of instructions?',
     "each instruction is paired with what it prevents",
     [("it is written for people who live near trees", "wrong_focus"),
      ("it assumes the reader has never seen a storm", "unsupported"),
      ("it warns that a severe storm cannot be prepared for", "contradicts")],
     "Flying trampolines, blocked gutters, wet soil, a flat phone: every rule carries its "
     "reason. It warns that a severe storm cannot be prepared for is the opposite of a "
     "list of preparations."),
  ],
 },
 {
  "title": "Why Sound Carries at Night",
  "topic": "Science",
  "extracts": [("", [
    "Stand near a highway on a summer afternoon and it is loud.",
    "Stand in the same place at two in the morning and you can hear a truck you cannot "
    "see, several kilometres away.",
    "The usual explanation is that the world is quieter at night, which is true and is "
    "not the main reason.",
    "Sound bends.",
    "It travels faster in warm air than in cold, and when one part of a wave is moving "
    "faster than another, the wave turns.",
    "During the day the ground is hot and the air above it is cooler, so the bottom of a "
    "sound wave outruns the top and the whole wave bends upward, away from you, and is "
    "lost to the sky.",
    "At night the ground cools quickly and the air a hundred metres up can be warmer than "
    "the air at your feet.",
    "Now the top of the wave is the fast part, so the wave bends downward and comes back "
    "to the ground.",
    "It can do this repeatedly, skipping along, which is why the truck is audible and "
    "invisible.",
    "The effect is strongest on clear, still nights, because wind mixes the layers and "
    "cloud keeps the ground warm.",
    "None of this has anything to do with how much noise there is.",
    "It is about the shape of the air.",
  ])],
  "items": [
    ("detail", "medium", 0.93, ONE, [(0, 4)],
     'The passage states: "{q}" What makes a sound wave turn?',
     "one part of it moving faster than another",
     [("the wave striking an obstacle in its path", "unsupported"),
      ("the wave becoming quieter as it travels", "wrong_focus"),
      ("cold air being heavier than warm air", "outside_knowledge")],
     "A difference in speed across the wave is the mechanism given. The wave striking an "
     "obstacle in its path is a different way of changing direction and not this one."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 5)],
     'The passage explains: "{q}" What does "outruns" mean here?',
     "moves ahead of, because it is travelling faster",
     [("escapes from the top of the wave altogether", "overreach"),
      ("runs out of energy sooner than the top does", "wrong_sense"),
      ("reaches the listener before the truck is seen", "wrong_focus")],
     "The bottom is in warmer air, so it goes faster and gets ahead. Saying it escapes "
     "from the top of the wave would leave the wave in two pieces, which bending is not."),

    ("inference", "medium", 0.92, ONE, [(0, 6), (0, 7)],
     'The passage says: "{q}" What has changed at night?',
     "the warm and cool layers have swapped places",
     [("the air has stopped moving altogether", "wrong_focus"),
      ("the sound has become considerably louder", "contradicts"),
      ("the ground has cooled more slowly than the air", "half_right")],
     "Warm above and cool below is the reverse of the daytime arrangement, and that "
     "reverses the bending. The ground has become warmer than the air is the daytime "
     "condition."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 8)],
     'The passage says: "{q}" What does "skipping" describe?',
     "bending down, reflecting, and bending down again",
     [("missing out large sections of the ground", "wrong_sense"),
      ("jumping right over the ground without ever touching it", "contradicts"),
      ("becoming fainter with each bend downward", "unsupported")],
     "Repeatedly returning to the ground and rising again is the motion the word names. "
     "Missing out large sections of the ground takes a different sense of the word "
     "entirely."),

    ("inference", "hard", 0.90, ONE, [(0, 9)],
     'The passage says: "{q}" Why does cloud weaken the effect?',
     "it stops the ground cooling, so the layers do not invert",
     [("it reflects the sound back into the sky", "unsupported"),
      ("it makes the night much noisier than usual", "wrong_focus"),
      ("it cools the upper air a great deal more than the ground", "contradicts")],
     "The effect depends on the ground getting cold, and cloud prevents that. It cools "
     "the upper air more than the ground would strengthen the inversion, not weaken it."),

    ("author_purpose", "medium", 0.92, ONE, [(0, 2)],
     'Why does the writer grant that the world is quieter at night?',
     "to concede the familiar answer before replacing it",
     [("to agree that quietness alone is the whole explanation", "contradicts"),
      ("to explain why people sleep better at night", "wrong_focus"),
      ("to show that the usual answer is entirely wrong", "overreach")],
     "True but not the main reason is a concession, not a rejection. To show that the "
     "usual answer is entirely wrong overstates a sentence that begins by calling it "
     "true."),

    ("author_purpose", "hard", 0.90, ONE, [(0, 10), (0, 11)],
     'The passage ends: "{q}" Why finish on these two sentences?',
     "to move the explanation from loudness to structure",
     [("to suggest the earlier explanation had been invented", "overreach"),
      ("to admit the writer cannot explain the effect", "contradicts"),
      ("to describe the shape of a sound wave itself", "wrong_focus")],
     "The shape of the air is the answer, and the last line puts it against the "
     "quantity of noise. To admit the writer cannot explain the effect reverses a passage "
     "that has just explained it."),

    ("main_idea", "medium", 0.92, ONE, [],
     'What question does this passage set out to answer?',
     "why distant sound is audible at night and not by day",
     [("why highways are noisier than country roads", "wrong_focus"),
      ("how sound waves are produced by a moving truck", "unsupported"),
      ("why the air is colder at night than during the daytime", "half_right")],
     "The whole passage is built on the difference between the two times of day. Why the "
     "air is colder at night than in the day is the fact the explanation uses, not the "
     "thing being explained."),
  ],
 },
]


if __name__ == "__main__":
    GEN.mkdir(parents=True, exist_ok=True)
    qs = build(PASSAGES, BOOK, NN, CATEGORY, LABEL)
    path = GEN / f"{BOOK}_p{NN}.json"
    path.write_text(json.dumps(qs, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(qs)} questions across {len(PASSAGES)} passages -> {path}")
