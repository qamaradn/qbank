#!/usr/bin/env python3
"""Builds rc_nsw_single_p7.json — 6 passages x 6 items = 36 answer slots (§3.1 type 3.1).

Seventh single-passage batch: a swimming lesson that goes wrong in a useful way, how a
weather forecast is actually made, an argument about handwriting, a lost property notice,
a neighbour's fig tree, and why mirrors reverse left and right but not up and down.

Six batches in, the coherence check has fired at least nine times on every one of them,
including the batch written specifically to beat it. It is treated here as part of the
build rather than as a review step: the fixes are expected, not a sign the batch was
written badly.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.rc.paired_common import build  # noqa: E402

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/reading_comprehension/generated"
NN = 7
BOOK = "rc_nsw_single"
CATEGORY = "single_passage"
LABEL = "Single-passage comprehension"
ONE = []

PASSAGES = [
 {
  "title": "Deep End",
  "topic": "Narrative",
  "extracts": [("", [
    "Mr Halvorsen's method was that you did not go into the deep end until you asked to.",
    "Other teachers moved you across when you were ready, which meant when they said you "
    "were.",
    "He waited, and some of us waited a very long time.",
    "I was in the shallow end for two terms watching people I had started with swim laps.",
    "Nobody said anything about it, which was somehow worse and also the only thing that "
    "made it survivable.",
    "In the second week of third term I put my hand up during roll and said I would like "
    "to try the deep end.",
    "He said good, and then he said, and if you want to come back to this end afterwards "
    "you can, and nobody will say anything about that either.",
    "I did not need to come back.",
    "What I needed was to know I could.",
    "Years later I asked him whether he had been waiting for me the whole time.",
    "He said he had been waiting for everybody the whole time, and that most of them got "
    "there faster and none of them got there better.",
    "I have thought about that sentence more than almost anything else anybody said to me "
    "at school.",
  ])],
  "items": [
    ("inference", "medium", 0.93, ONE, [(0, 1)],
     'The narrator says of other teachers: "{q}" What is he pointing out?',
     "readiness was decided by the teacher, not the student",
     [("other teachers were stricter about swimming", "wrong_focus"),
      ("other teachers moved students across too early", "overreach"),
      ("students were never allowed into the deep end", "contradicts")],
     "The correction in the second half of the sentence puts the decision with the "
     "teacher. Other teachers moved students across too early adds a judgement the "
     "sentence does not make."),

    ("inference", "medium", 0.92, ONE, [(0, 4)],
     'The narrator says: "{q}" Why was the silence both worse and necessary?',
     "not being discussed left the choice with him",
     [("nobody had noticed that he was still there", "contradicts"),
      ("the other students had been told to say nothing", "unsupported"),
      ("he wanted somebody to make him move across", "half_right")],
     "Silence meant no pressure and also no help, which is exactly what made the "
     "eventual step his own. Nobody had noticed that he was still there is denied by a "
     "teacher who says he was waiting for everybody."),

    ("author_purpose", "medium", 0.92, ONE, [(0, 6)],
     'Why does the writer record the second half of what Mr Halvorsen said?',
     "the offer to come back is what made going possible",
     [("to show the teacher expected him to fail", "overreach"),
      ("to explain the rules of the swimming lesson", "wrong_focus"),
      ("to show the teacher had changed his method", "contradicts")],
     "Removing the cost of failing is what makes an attempt safe to make. To show the "
     "teacher expected him to fail turns a safety net into a prediction."),

    ("vocabulary_in_context", "hard", 0.90, ONE, [(0, 7), (0, 8)],
     'The narrator writes: "{q}" What is the difference he is drawing?',
     "between doing something and being free to do it",
     [("between swimming well and swimming badly", "wrong_focus"),
      ("between the deep end and the shallow end", "literal"),
      ("between needing help and refusing it", "half_right")],
     "He never used the option, and having it was the whole point. Between the deep end "
     "and the shallow end reads a sentence about permission as one about the pool."),

    ("cause_effect", "medium", 0.92, ONE, [(0, 10)],
     'Mr Halvorsen says: "{q}" What is he claiming about the students who took longer?',
     "arriving late did not mean arriving worse",
     [("the slower students swam more strongly in the end", "overreach"),
      ("the speed of learning is the only thing that matters", "contradicts"),
      ("he had spent more time on the slower students", "unsupported")],
     "Faster and better are separated deliberately in the same sentence. The slower "
     "students swam more strongly in the end claims an advantage he does not."),

    ("main_idea", "medium", 0.92, ONE, [],
     'What does this passage say about how people learn?',
     "the timing of a step matters less than owning it",
     [("students should be moved on as soon as they are ready", "half_right"),
      ("swimming is best taught in the shallow end first", "wrong_focus"),
      ("teachers should never decide anything for students", "overreach")],
     "Two terms of waiting cost nothing because the step, when it came, was his. Students "
     "should be moved on when they are ready is the method the passage sets itself "
     "against, since somebody else judges the readiness."),
  ],
 },
 {
  "title": "How a Forecast Is Made",
  "topic": "Science",
  "extracts": [("", [
    "A weather forecast is not a prediction in the way most people imagine.",
    "Nobody looks at a sky and decides.",
    "The atmosphere is divided into a grid of boxes, each perhaps ten kilometres across "
    "and a few hundred metres deep, and a computer is given the temperature, pressure, "
    "humidity and wind in every box.",
    "Then it applies the equations of fluid motion, over and over, in very small steps of "
    "time.",
    "The result is not one forecast but many.",
    "Because the starting measurements are never exact, the model is run repeatedly with "
    "tiny deliberate changes to the starting numbers.",
    "If fifty runs all produce rain, the forecast says rain.",
    "If thirty produce rain and twenty do not, the forecast says sixty per cent chance of "
    "rain, and that number is doing real work.",
    "It does not mean it will rain on sixty per cent of your suburb.",
    "It means that in sixty of a hundred plausible versions of tomorrow, it rained where "
    "you are.",
    "This is why forecasts are good for three days and poor for ten.",
    "Small differences at the start stay small for a while and then, quite suddenly, do "
    "not.",
  ])],
  "items": [
    ("detail", "medium", 0.93, ONE, [(0, 2)],
     'The passage states: "{q}" What is the first step in making a forecast?',
     "dividing the atmosphere into a grid of boxes",
     [("looking at satellite images of the sky", "unsupported"),
      ("running the equations of fluid motion", "wrong_focus"),
      ("collecting reports from weather stations around the country", "half_right")],
     "The grid comes first, and the measurements are then supplied for each box. Running "
     "the equations of fluid motion is what happens after the grid has been filled."),

    ("inference", "medium", 0.92, ONE, [(0, 5)],
     'The passage explains: "{q}" Why are the starting numbers changed on purpose?',
     "to see how much the outcome depends on small errors",
     [("to make the computer run the model faster", "unsupported"),
      ("because the original measurements were wrong", "half_right"),
      ("to produce a forecast that people are willing to believe", "wrong_focus")],
     "Deliberate small changes test how fragile the result is. Because the original "
     "measurements were wrong misses the point: they are never exact, which is different "
     "from being mistaken."),

    ("vocabulary_in_context", "hard", 0.90, ONE, [(0, 9)],
     'The passage says a sixty per cent chance means: "{q}" What is being counted?',
     "the share of model runs in which rain fell",
     [("the share of the suburb that will get wet", "contradicts"),
      ("the share of the day during which it rains", "wrong_focus"),
      ("the number of forecasters who agreed on rain", "outside_knowledge")],
     "Plausible versions of tomorrow are the model runs described earlier. The share of "
     "the suburb that will get wet is the misreading the sentence before it rules out."),

    ("cause_effect", "medium", 0.92, ONE, [(0, 11)],
     'The passage says: "{q}" Why are ten-day forecasts poor?',
     "small starting errors grow suddenly after a few days",
     [("nobody bothers to run the model that far ahead", "unsupported"),
      ("the grid boxes become larger further into the future", "outside_knowledge"),
      ("the equations stop working after about three days", "wrong_focus")],
     "Errors stay small and then abruptly do not, which is what limits the useful range. "
     "The equations stop working after about three days puts the fault in the physics "
     "rather than in the starting numbers."),

    ("author_purpose", "medium", 0.92, ONE, [(0, 1)],
     'The passage says: "{q}" Why include so short a sentence?',
     "to dismiss the picture most readers have",
     [("to criticise the forecasters for not looking outside", "overreach"),
      ("to explain why forecasts are sometimes wrong", "wrong_focus"),
      ("to show that skies are difficult to read", "half_right")],
     "Four words remove the image of a person judging the weather by eye. To criticise "
     "forecasters for not looking outside turns a correction into a complaint."),

    ("main_idea", "medium", 0.92, ONE, [],
     'Taken together, what do these paragraphs explain?',
     "that a forecast is a count of possible outcomes",
     [("that forecasts are usually quite wrong beyond three days", "half_right"),
      ("how weather measurements are taken each morning", "wrong_focus"),
      ("why rain is harder to predict than temperature", "unsupported")],
     "Grid, repeated runs and the meaning of a percentage all serve that one idea. That "
     "forecasts are usually wrong beyond three days is the last paragraph rather than the "
     "passage."),
  ],
 },
 {
  "title": "In Defence of Handwriting",
  "topic": "Opinion",
  "extracts": [("", [
    "The argument for teaching handwriting is usually made badly.",
    "People say it is beautiful, or traditional, or that a signature matters, and none of "
    "those will survive contact with a thirteen-year-old.",
    "The good argument is duller and harder to dismiss.",
    "Writing by hand is slower than typing, and because it is slower you cannot take down "
    "everything, so you have to decide what matters while you are listening.",
    "That deciding is the learning.",
    "A student typing a lesson can capture almost all of it and process almost none of "
    "it.",
    "This has been tested more than once, and the students who typed remembered facts as "
    "well as anybody and understood the ideas noticeably less.",
    "I am not arguing that children should stop using computers.",
    "Most of what they will write as adults will be typed, and typing badly is a real "
    "disadvantage.",
    "I am arguing that the case for handwriting has nothing to do with handwriting.",
    "It is a case for being forced to choose, which is a thing our tools are increasingly "
    "designed to spare us.",
  ])],
  "items": [
    ("author_purpose", "medium", 0.93, ONE, [(0, 1)],
     'The writer says: "{q}" Why open by attacking the usual arguments?',
     "to clear away reasons the reader can easily reject",
     [("to show that handwriting should not be taught at all", "contradicts"),
      ("to explain how signatures are used in law", "wrong_focus"),
      ("to prove that thirteen-year-olds are difficult", "overreach")],
     "Removing the weak arguments first is what makes room for the one the writer trusts. "
     "To show that handwriting should not be taught is the opposite of the piece."),

    ("inference", "medium", 0.92, ONE, [(0, 3), (0, 4)],
     'The writer says: "{q}" Where does the learning happen?',
     "in choosing what is worth writing down",
     [("in the act of forming each of the letters neatly", "wrong_focus"),
      ("in writing down as much as possible", "contradicts"),
      ("in reading the notes again afterwards", "unsupported")],
     "The deciding forced by slowness is named as the learning itself. In writing down as "
     "much as possible is what typing allows and what the writer says fails."),

    ("detail", "medium", 0.92, ONE, [(0, 6)],
     'According to the passage, what did the tests find about students who typed?',
     "they recalled facts well but understood ideas less",
     [("they recalled facts badly and understood ideas well", "contradicts"),
      ("they performed worse than the others in every way", "overreach"),
      ("they wrote a great deal more than the others did", "half_right")],
     "Facts as well as anybody, ideas noticeably less, is the split reported. They "
     "performed worse than the others in every way flattens a result that was mixed."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 9)],
     'The writer says: "{q}" What does this apparent contradiction mean?',
     "the value lies in the slowness, not in the letters",
     [("handwriting is not really worth teaching", "contradicts"),
      ("the writer has changed his mind mid-argument", "wrong_focus"),
      ("handwriting and typing are equally valuable", "half_right")],
     "The case is about what slowness forces, which any slow method would supply. "
     "Handwriting is not really worth teaching is the opposite of an argument for "
     "teaching it."),

    ("cause_effect", "hard", 0.90, ONE, [(0, 5)],
     'The writer says: "{q}" What is the connection being drawn?',
     "capturing everything prevents processing anything",
     [("typing is faster than handwriting for most people", "wrong_focus"),
      ("students who type do not pay attention in class", "overreach"),
      ("capturing a lesson helps a student to understand it", "contradicts")],
     "The two halves are set against each other deliberately: the more you catch, the "
     "less you sort. Capturing a lesson helps a student to understand it reverses the "
     "sentence."),

    ("main_idea", "medium", 0.92, ONE, [(0, 10)],
     'The passage ends: "{q}" What is the writer finally arguing for?',
     "keeping something that forces a choice",
     [("removing computers from classrooms entirely", "contradicts"),
      ("designing better tools for taking notes", "unsupported"),
      ("teaching students to type more quickly", "wrong_focus")],
     "Being forced to choose is named as the thing worth protecting. Removing computers "
     "from classrooms entirely is what the writer explicitly says he is not arguing."),
  ],
 },
 {
  "title": "Lost Property",
  "topic": "Functional",
  "extracts": [("", [
    "Lost property is emptied at the end of each term, not each year.",
    "Anything unclaimed goes to a charity shop, including things that are obviously "
    "expensive, because we cannot store them and we will not judge which items deserve to "
    "be kept.",
    "Label everything, including the things that seem too obvious to label.",
    "Last term we held nine identical black jumpers, size 12, and returned two.",
    "The other seven went to the shop, and at least three of them had owners who came "
    "looking.",
    "Drink bottles are the exception and are thrown out weekly for hygiene reasons.",
    "Do not come looking for a drink bottle after a weekend.",
    "Glasses, retainers, hearing aids and medical items are not put in the tub.",
    "They go to the front office immediately and are logged, because these are the items "
    "families most need back and most cannot replace quickly.",
    "If you have lost something, come at lunchtime rather than before school.",
    "Before school there is one person on the desk and forty parents at it, and you will "
    "not get to look properly.",
    "The tub is in the corridor outside the hall and you may search it yourself.",
  ])],
  "items": [
    ("cause_effect", "medium", 0.93, ONE, [(0, 3), (0, 4)],
     'The notice says: "{q}" What does this example show?',
     "an unlabelled item cannot be returned even when claimed",
     [("students lose more jumpers than anything else", "wrong_focus"),
      ("the school does not try to return lost items", "contradicts"),
      ("nine students bought the same jumper by accident", "outside_knowledge")],
     "Three owners came looking and still went away empty, because nothing identified "
     "which jumper was whose. The school does not try to return lost items is contradicted "
     "by the two that were returned."),

    ("detail", "medium", 0.92, ONE, [(0, 7), (0, 8)],
     'The notice says: "{q}" Why are these items treated differently?',
     "families need them back and cannot replace them quickly",
     [("they are considered far more valuable than the other items", "half_right"),
      ("they are too small to be seen in the tub", "unsupported"),
      ("they are not allowed to be brought to school", "contradicts")],
     "Need and replaceability are the two reasons given. They are more valuable than the "
     "other items is close but is not what the notice says, which is about how hard they "
     "are to do without."),

    ("inference", "medium", 0.92, ONE, [(0, 10)],
     'The notice says: "{q}" Why is lunchtime better than before school?',
     "there is time and space to search properly",
     [("the tub is moved into the hall at lunchtime", "unsupported"),
      ("more staff are on the desk during lunchtime", "half_right"),
      ("students are not allowed in the corridor early", "contradicts")],
     "One person and forty parents is a queue, not a search. More staff are on the desk "
     "during lunchtime is not stated and is not the reason the notice gives."),

    ("author_purpose", "medium", 0.92, ONE, [(0, 1)],
     'Why does the notice explain what happens to expensive items?',
     "to make clear that no exceptions will be made",
     [("to warn families that the school simply steals items", "overreach"),
      ("to explain how the charity shop is chosen", "wrong_focus"),
      ("to suggest expensive items are always claimed", "contradicts")],
     "Saying it will not judge which items deserve keeping closes off the obvious "
     "request. To warn families that the school steals items reads a policy as an "
     "accusation."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 5)],
     'The notice says: "{q}" What makes drink bottles "the exception"?',
     "they are thrown out weekly rather than at term's end",
     [("they are the only items that get labelled", "unsupported"),
      ("they are kept longer than everything else", "contradicts"),
      ("they are sent to the charity shop first", "wrong_focus")],
     "Everything else waits until the end of term; bottles do not. They are kept longer "
     "than everything else is the reverse of a weekly clear-out."),

    ("main_idea", "hard", 0.90, ONE, [],
     'What does this notice do besides state the rules?',
     "it gives the reason behind each rule",
     [("it apologises for losing students' property", "contradicts"),
      ("it lists everything currently in the tub", "unsupported"),
      ("it warns that lost items are rarely found", "half_right")],
     "Storage, hygiene, replaceability and queueing are each named as the reason for a "
     "rule. It warns that lost items are rarely found is true of the jumper example but "
     "is not what the notice sets out to do."),
  ],
 },
 {
  "title": "The Fig Tree",
  "topic": "Narrative",
  "extracts": [("", [
    "The fig tree was on their side of the fence and about two thirds of it was over ours.",
    "For eleven years this was fine.",
    "Mrs Adeyemi picked what she could reach from a ladder and we picked what hung over, "
    "and once a summer she brought a jar of something over and we brought a jar of "
    "something back, and neither of us ever discussed the arrangement.",
    "Then they sold, and the new people put up a notice on the tree.",
    "The notice said the fruit was theirs.",
    "It was typed.",
    "My father, who has never once won an argument on paper, wrote back that legally the "
    "overhanging fruit was ours, which is true, and put it in their letterbox.",
    "For a fortnight nobody picked anything and the figs fell and split on the concrete "
    "and the birds got the lot.",
    "Then their daughter, who is about eight, came to the fence and asked whether we knew "
    "how to make the jam, because they had found a jar in the shed with a label in "
    "handwriting.",
    "My mother went over that afternoon with the recipe.",
    "Nobody has mentioned the notice since, and nobody has taken it down either.",
    "It is still on the tree, going soft in the weather.",
  ])],
  "items": [
    ("inference", "medium", 0.93, ONE, [(0, 2)],
     'The passage says: "{q}" Why did the arrangement work?',
     "neither side needed to state the rules",
     [("the fruit was divided exactly in half", "wrong_focus"),
      ("Mrs Adeyemi owned the whole of the tree", "half_right"),
      ("both of the families had agreed the terms in writing", "contradicts")],
     "Never discussing it is what the passage names as the reason it held. Both families "
     "had agreed the terms in writing is the opposite of an arrangement nobody "
     "articulated."),

    ("author_purpose", "medium", 0.92, ONE, [(0, 5)],
     'The passage adds: "{q}" Why include those two words?',
     "to mark how impersonal the notice was",
     [("to show the new people were well organised", "wrong_focus"),
      ("to explain that nobody could read handwriting", "unsupported"),
      ("to suggest the notice was written by a lawyer", "overreach")],
     "A typed notice on a tree between neighbours is the point, and the short sentence "
     "makes sure it lands. To show the new people were well organised takes the detail as "
     "praise."),

    ("cause_effect", "medium", 0.92, ONE, [(0, 7)],
     'The passage says: "{q}" What was the result of the dispute?',
     "nobody got the fruit at all",
     [("the two families divided the fruit evenly", "contradicts"),
      ("the concrete below the tree was stained", "wrong_focus"),
      ("the tree stopped producing fruit that year", "unsupported")],
     "Figs on the concrete and birds taking the lot is the cost of both sides being "
     "right. The tree stopped producing fruit that year confuses fruit going to waste "
     "with fruit not appearing."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 6)],
     'The passage says: "{q}" What does this tell us about the father?',
     "being right on paper is not the same as winning",
     [("he had never written a letter before", "overreach"),
      ("he was correct about the law in this case", "half_right"),
      ("he refused to put anything in writing", "contradicts")],
     "The aside is a joke at his own expense that the fortnight of fallen figs then "
     "proves. He was correct about the law in this case is true and is precisely what did "
     "not help."),

    ("inference", "hard", 0.90, ONE, [(0, 8), (0, 9)],
     'The passage says: "{q}" Why does the daughter\'s question change things?',
     "it asks for something the argument could not settle",
     [("it proves that the fruit belonged to both of the families", "wrong_focus"),
      ("it shows the new family had given up the claim", "overreach"),
      ("it means the notice had been taken down already", "contradicts")],
     "A recipe is not a right, so it cannot be won or lost, and that is what lets "
     "somebody move. It shows the new family had given up the claim goes further than a "
     "child asking about jam."),

    ("main_idea", "medium", 0.92, ONE, [(0, 10), (0, 11)],
     'The passage ends: "{q}" What does the ending suggest?',
     "the quarrel was settled without being resolved",
     [("the families are still arguing over the tree even now", "contradicts"),
      ("the notice will be taken down very soon", "unsupported"),
      ("the new family were in the wrong all along", "half_right")],
     "Nobody mentions it and nobody removes it, which is what people do when the "
     "substance has gone out of a dispute. The families are still arguing about the tree "
     "is denied by a mother taking a recipe across."),
  ],
 },
 {
  "title": "Why Mirrors Do Not Reverse You",
  "topic": "Science",
  "extracts": [("", [
    "Hold up your right hand and the person in the mirror holds up their left.",
    "Everybody notices this, and almost everybody explains it wrongly.",
    "The question people ask is why a mirror swaps left and right but not up and down.",
    "The answer is that it does neither.",
    "A mirror reverses front and back.",
    "The version of you in the glass is not turned around; it is turned inside out along "
    "the one axis pointing at the surface.",
    "Your nose, which is closest to the mirror, is closest in the reflection too.",
    "The back of your head, furthest away, is furthest away.",
    "The reason it feels like left and right is that when you imagine walking around to "
    "stand where the reflection is, you rotate yourself about a vertical axis, because "
    "that is the only way people turn.",
    "That rotation swaps your left and right, and the mirror did not.",
    "Try it with writing.",
    "Hold a page up to a mirror and the letters are reversed left to right, but hold the "
    "page above your head with the writing facing up and they reverse top to bottom "
    "instead.",
    "The mirror behaved identically both times.",
    "You did not.",
  ])],
  "items": [
    ("detail", "medium", 0.93, ONE, [(0, 4)],
     'The passage states: "{q}" What does a mirror actually reverse?',
     "the direction pointing towards the glass",
     [("left and right, but never the top and the bottom", "contradicts"),
      ("nothing at all about the reflected image", "overreach"),
      ("the brightness of the reflected image", "wrong_focus")],
     "Front and back is the axis named, and it is the one pointing at the surface. Left "
     "and right, but never up and down is exactly the belief the passage is correcting."),

    ("inference", "hard", 0.90, ONE, [(0, 8), (0, 9)],
     'The passage explains: "{q}" Where does the sense of left-right swapping come from?',
     "from imagining yourself turned around to face the other way",
     [("from the mirror rotating the image sideways", "contradicts"),
      ("from the difficulty of ever seeing your own back", "wrong_focus"),
      ("from people being right-handed more often", "outside_knowledge")],
     "The swap is performed by the reader's imagined rotation, not by the glass. From the "
     "mirror rotating the image sideways is the explanation the passage is denying."),

    ("inference", "medium", 0.92, ONE, [(0, 11)],
     'The passage suggests a test: "{q}" What does the difference between the two show?',
     "the reversal follows how the page is held",
     [("mirrors work differently when held above you", "contradicts"),
      ("writing is harder to read in a mirror", "wrong_focus"),
      ("the page becomes reversed by being lifted", "literal")],
     "Same mirror, different orientation, different apparent reversal. Mirrors work "
     "differently when held above you is what the next sentence explicitly denies."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 5)],
     'The passage says: "{q}" What does "turned inside out" mean here?',
     "reversed along the one axis facing the glass",
     [("turned right around to face in the other direction", "contradicts"),
      ("physically pulled apart and reassembled", "literal"),
      ("shown from a completely different angle", "wrong_focus")],
     "One axis is flipped and the other two are left alone. Turned around to face the "
     "other direction is the rotation the passage says you supply yourself."),

    ("author_purpose", "medium", 0.92, ONE, [(0, 12), (0, 13)],
     'The passage ends: "{q}" Why finish with these two short sentences?',
     "to place the change in the observer, not the mirror",
     [("to suggest that the reader performed the test badly", "wrong_focus"),
      ("to admit that the explanation is incomplete", "contradicts"),
      ("to show that mirrors are unreliable objects", "overreach")],
     "Four words move the whole puzzle from the glass to the person holding the page. To "
     "admit that the explanation is incomplete reverses an ending that closes the "
     "argument."),

    ("main_idea", "medium", 0.92, ONE, [],
     'Which mistake is this passage written to fix?',
     "the way people describe what a mirror does",
     [("a mistake about how light bounces off glass", "wrong_focus"),
      ("the belief that mirrors show nothing real", "overreach"),
      ("an error in the way mirrors are manufactured", "unsupported")],
     "The physics is not in dispute; the description of it is. A mistake about how light "
     "bounces off glass is a subject the passage never raises."),
  ],
 },
]


if __name__ == "__main__":
    GEN.mkdir(parents=True, exist_ok=True)
    qs = build(PASSAGES, BOOK, NN, CATEGORY, LABEL)
    path = GEN / f"{BOOK}_p{NN}.json"
    path.write_text(json.dumps(qs, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(qs)} questions across {len(PASSAGES)} passages -> {path}")
