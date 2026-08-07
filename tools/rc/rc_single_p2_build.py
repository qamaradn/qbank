#!/usr/bin/env python3
"""Builds rc_nsw_single_p2.json — 6 passages x 6 items = 36 answer slots (§3.1 type 3.1).

Second single-passage batch. Ground not used by p1 (a cricket ball, the ute, boredom, the
class chickens, a relief teacher, the platypus): a lunchbox trade, how Vegemite nearly
failed, an argument about the word "weed", a bike safety check, a breakdown on a highway,
and the lyrebird.

Same §3.2 proportions as p1: inference 9, vocabulary in context 7, author's purpose 7,
main idea 5, detail 4, cause and effect 4. Main-idea stems are phrased differently in
every passage, because "What is the passage mainly about?" repeated across a batch scores
above phase 4's silent 0.85 near-duplicate threshold — p1 hit that three times.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.rc.paired_common import build  # noqa: E402

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/reading_comprehension/generated"
NN = 2
BOOK = "rc_nsw_single"
CATEGORY = "single_passage"
LABEL = "Single-passage comprehension"
ONE = []

PASSAGES = [
 {
  "title": "The Swap",
  "topic": "Narrative",
  "extracts": [("", [
    "Ilya had the good sandwich and I had the good drink, and we had been trading them "
    "since Year 3 without either of us ever saying so out loud.",
    "It was not a rule.",
    "It was more like weather.",
    "Then in Year 6 his family changed what they put in his lunchbox, and the sandwich "
    "stopped being the good sandwich.",
    "He kept offering it anyway.",
    "For two weeks I took it and ate about half and put the rest in my bag, where it "
    "stayed until the bag smelled and Mum found out.",
    "The obvious thing was to say something.",
    "The problem with the obvious thing was that four years of not saying anything had "
    "made it enormous.",
    "In the end I said it badly, on the oval, in front of Ravi.",
    "Ilya went quiet and then said he had known for about a week and had been waiting for "
    "me to work it out.",
    "He said the new sandwich was worse for him too.",
    "We ate our own lunches for three days, which felt strange, and then he offered me "
    "half an orange and I gave him half a biscuit, and that was that.",
    "What I remember is not the sandwich.",
    "It is how long I let something small become something I could not say.",
  ])],
  "items": [
    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 2)],
     'The narrator says: "{q}" What does this comparison mean?',
     "it happened without anybody deciding it",
     [("it changed depending on the season", "wrong_sense"),
      ("it only happened outdoors at lunchtime", "literal"),
      ("it was discussed by both boys in advance", "contradicts")],
     "Weather is the thing nobody arranges and everybody accepts, which is the point of "
     "the comparison. It was discussed by both boys in advance is ruled out by the "
     "opening, which says neither ever said so out loud."),

    ("inference", "medium", 0.92, ONE, [(0, 5)],
     'The narrator says: "{q}" Why did he keep taking a sandwich he did not want?',
     "saying no had become harder than eating it",
     [("he was worried the sandwich would go to waste", "wrong_focus"),
      ("he had grown to like the new sandwich after all", "contradicts"),
      ("his mother had told him to accept whatever he was offered", "unsupported")],
     "Hiding it in a bag for two weeks is the behaviour of somebody avoiding a "
     "conversation. He had grown to like the new sandwich after all cannot fit a boy who "
     "eats half and hides the rest."),

    ("inference", "hard", 0.90, ONE, [(0, 7)],
     'The narrator says: "{q}" What does he mean?',
     "the longer a small thing goes unsaid, the harder it gets to say",
     [("four years is a long time to know somebody", "wrong_focus"),
      ("the sandwich itself had become very large", "literal"),
      ("he had forgotten how to speak to Ilya about anything at all", "overreach")],
     "The size belongs to the silence, not to the problem, which is what the last line "
     "then states outright. The sandwich itself had become very large reads a sentence "
     "about difficulty as a sentence about food."),

    ("author_purpose", "medium", 0.92, ONE, [],
     'Why does the writer tell us that Ilya had known for about a week?',
     "to show the silence was costing them both",
     [("to prove that Ilya was the more honest of the two", "overreach"),
      ("to explain why the new sandwich had been changed", "wrong_focus"),
      ("to show that Ilya had been angry the whole time", "contradicts")],
     "Both of them were waiting, which makes the problem shared rather than one boy's "
     "fault. To show that Ilya had been angry the whole time is contradicted by a friend "
     "who simply waited and then agreed."),

    ("main_idea", "medium", 0.92, ONE, [],
     'Which of these best describes what the passage is about?',
     "how an easy thing to say becomes hard by being left",
     [("a friendship that ends over a disagreement", "contradicts"),
      ("the difficulty of finding a lunch you enjoy", "wrong_focus"),
      ("two boys who fall out over a small misunderstanding", "half_right")],
     "The narrator says so himself in the final sentence. A friendship that ends over a "
     "disagreement is the opposite of an ending in which they resume trading."),

    ("cause_effect", "medium", 0.92, ONE, [(0, 5)],
     'What finally forces the narrator to raise the subject?',
     "his mother discovers the sandwiches in his bag",
     [("Ilya asks him directly whether he still wants it", "contradicts"),
      ("Ravi tells the narrator that he should say something", "unsupported"),
      ("Ravi notices the smell and says something to Ilya", "wrong_focus")],
     "The bag smells, his mother finds out, and the conversation follows. Ilya asks him "
     "directly whether he still wants it is ruled out by a friend who was waiting for the "
     "narrator to work it out."),
  ],
 },
 {
  "title": "How Vegemite Nearly Failed",
  "topic": "History",
  "extracts": [("", [
    "When Vegemite went on sale in 1923 it did not sell.",
    "It had been made to replace a British spread that the war had cut off, and Australians "
    "who wanted that spread simply waited for it to come back.",
    "The company tried a new name, chosen by competition, and it made no difference.",
    "They tried giving it away with other products, and people took the free jar and left "
    "the spread in the cupboard.",
    "What finally worked was not advertising in the usual sense.",
    "In the 1930s the company persuaded doctors to mention it, because it is unusually "
    "high in B vitamins, and doctors at that time were listened to about food in a way "
    "they are not now.",
    "Then the army took it.",
    "Australian soldiers in the Second World War were issued with it, ate it for years, "
    "and came home used to the taste.",
    "A spread that had failed for fifteen years became ordinary in about five.",
    "The lesson is not that the product improved, because it did not change at all.",
    "What changed was who had eaten it, and for how long.",
  ])],
  "items": [
    ("detail", "medium", 0.93, ONE, [(0, 3)],
     'The passage says: "{q}" What happened when the company gave the spread away?',
     "people accepted the jar but did not use it",
     [("people refused to take the free jars at all", "contradicts"),
      ("the free jars were handed out only to soldiers", "wrong_focus"),
      ("free jars were the only way it was ever sold", "overreach")],
     "Taking the free jar and leaving it in the cupboard is acceptance without use. People "
     "refused to take the free jars at all is the opposite: they took them and simply did "
     "not eat the contents."),

    ("inference", "medium", 0.92, ONE, [(0, 1)],
     'The passage explains: "{q}" Why did this make the spread hard to sell?',
     "it was a substitute for something people still expected back",
     [("Australians disliked every kind of spread sold at that time", "overreach"),
      ("the British spread had never been sold here", "contradicts"),
      ("the war had made all groceries too expensive", "unsupported")],
     "A replacement has to compete with the original, and the original was coming back. "
     "The British spread had never been sold here is the opposite of a passage in which "
     "people were waiting for it to return."),

    ("inference", "hard", 0.90, ONE, [(0, 5)],
     'The passage notes: "{q}" Why does the writer add the last part of that sentence?',
     "to explain why a doctor's word carried more weight then",
     [("to argue that doctors today are a good deal less trusted", "unsupported"),
      ("to show that the spread was sold as a medicine", "overreach"),
      ("to prove that the vitamins were not really there", "contradicts")],
     "The aside tells the reader the tactic worked because of when it was tried, not "
     "because of what was claimed. To show that the spread was sold as a medicine goes "
     "past a passage that says only that doctors mentioned it."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 8)],
     'The passage says: "{q}" Here, "ordinary" means —',
     "found in most houses without anybody thinking about it",
     [("of poor quality compared with other spreads", "wrong_sense"),
      ("liked by absolutely everybody in the whole country", "overreach"),
      ("sold in only a small number of shops", "contradicts")],
     "The word marks the change from unwanted to unremarkable, which is the whole point "
     "of the sentence. Sold in only a small number of shops is the opposite of becoming "
     "ordinary."),

    ("author_purpose", "hard", 0.90, ONE, [(0, 9)],
     'The passage states: "{q}" Why does the writer point this out?',
     "to show that taste is learned rather than fixed",
     [("to criticise the company for never improving it", "wrong_focus"),
      ("to explain why the spread was cheap to make", "unsupported"),
      ("to argue that the spread was never really popular", "contradicts")],
     "If the spread did not change, then something about the eaters did, which is the "
     "conclusion the last line draws. To argue that the spread was never really popular "
     "contradicts a passage about it becoming ordinary."),

    ("main_idea", "medium", 0.92, ONE, [],
     'What is this passage mainly explaining?',
     "why a product can fail and then succeed unchanged",
     [("how the Australian army chose its rations", "wrong_focus"),
      ("why B vitamins are added to food spreads at all", "unsupported"),
      ("how a company invents a name for a product", "half_right")],
     "Fifteen years of failure and five years of success, with no change to the product, "
     "is the passage's whole shape. How a company invents a name for a product covers one "
     "sentence that the passage says made no difference."),
  ],
 },
 {
  "title": "Stop Calling It a Weed",
  "topic": "Opinion",
  "extracts": [("", [
    "A weed is not a kind of plant.",
    "There is no botanical family of weeds, no shared leaf, no test you could run in a "
    "laboratory.",
    "A weed is a plant somebody does not want, and that is the entire definition.",
    "The same grass is a weed in a wheat crop and a crop in a hay paddock.",
    "Lantana was sold in Australian nurseries as a garden shrub for fifty years before it "
    "became the thing councils spend millions removing.",
    "It did not change.",
    "We did.",
    "I am not arguing that the word should be banned, because farmers and bush regenerators "
    "need a short word for a real problem.",
    "I am arguing that it hides the question worth asking, which is: unwanted by whom, and "
    "for what?",
    "A plant that chokes a creek and a plant that merely annoys a gardener are both called "
    "weeds, and only one of them matters.",
    "Until we separate those two, we will keep spending money on the wrong one.",
  ])],
  "items": [
    ("main_idea", "medium", 0.93, ONE, [],
     'What is the writer arguing?',
     "the word hides a distinction that matters",
     [("the word should be removed from the language", "contradicts"),
      ("every plant in a garden counts as a weed", "overreach"),
      ("the word is used far too rarely by councils", "wrong_focus")],
     "The argument is about what the word conceals, not about the word itself. The word "
     "should be removed from the language is what the writer explicitly declines to "
     "argue."),

    ("author_purpose", "medium", 0.92, ONE, [(0, 4)],
     'Why does the writer bring up lantana?',
     "to show the same plant can change category without changing",
     [("to argue that nurseries should be shut down", "overreach"),
      ("to explain how lantana spreads through bushland", "wrong_focus"),
      ("to prove that lantana is entirely harmless to native plants", "contradicts")],
     "Sold as a shrub, then removed at great cost, and the plant itself the same "
     "throughout. To prove that lantana is harmless to native plants runs against "
     "councils spending millions on it."),

    ("inference", "hard", 0.90, ONE, [(0, 5), (0, 6)],
     'The passage says: "{q}" What is the writer claiming with these two short sentences?',
     "the change was in people's judgement, not in the plant",
     [("the plant itself became more dangerous over fifty years", "contradicts"),
      ("Australians stopped growing gardens altogether", "unsupported"),
      ("nurseries changed which plants they were selling", "wrong_focus")],
     "Two words each, set against each other, put the whole change on the human side. The "
     "plant became more dangerous over fifty years is exactly what 'it did not change' "
     "denies."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 8)],
     'The writer asks: "{q}" What is the point of the question?',
     "a plant is only a weed relative to somebody's purpose",
     [("weeds ought to be identified only by trained scientists", "wrong_focus"),
      ("nobody is able to answer the question at all", "overreach"),
      ("the writer does not know what a weed is", "contradicts")],
     "Naming the person and the purpose is what turns a label back into a judgement. The "
     "writer does not know what a weed is is contradicted by a passage that opens with a "
     "definition."),

    ("author_purpose", "hard", 0.90, ONE, [(0, 7)],
     'Why does the writer include: "{q}"?',
     "to keep the reader from dismissing the argument as impractical",
     [("to agree that the word is already used correctly by everybody", "contradicts"),
      ("to describe the work that bush regenerators do", "wrong_focus"),
      ("to admit that the argument does not really work", "overreach")],
     "Granting that the word has a job protects the narrower point that follows it. To "
     "admit that the argument does not really work misreads a concession as a surrender — "
     "the next sentence restates the claim."),

    ("cause_effect", "medium", 0.92, ONE, [(0, 10)],
     'According to the writer, what follows from lumping the two kinds of weed together?',
     "effort goes to the plant that matters less",
     [("councils stop removing any plants at all", "overreach"),
      ("gardeners are blamed for the whole problem", "unsupported"),
      ("the creeks are cleared before the gardens are", "contradicts")],
     "The last line names the consequence directly as money spent on the wrong one. The "
     "creeks are cleared before the gardens are would mean the problem had already been "
     "solved."),
  ],
 },
 {
  "title": "Before You Ride",
  "topic": "Functional",
  "extracts": [("", [
    "Do this check before the first ride of the week, not before every ride.",
    "A check you do too often is a check you stop doing.",
    "Squeeze both brake levers.",
    "Each should stop firmly with a gap of at least two fingers between the lever and the "
    "handlebar.",
    "If a lever pulls all the way back, the bike is not rideable, and no amount of care "
    "on the road will make up for it.",
    "Press each tyre hard with your thumb.",
    "A tyre you can push in more than about half a centimetre is too soft, and a soft "
    "tyre is the most common cause of a pinched tube.",
    "Lift the front wheel five centimetres and let it drop.",
    "Anything that rattles is loose, and something loose is easier to fix now than to "
    "notice later at speed.",
    "Spin each wheel and watch the gap at the brake pad.",
    "If the gap opens and closes as the wheel turns, the wheel is buckled and needs a "
    "workshop, not a spanner in the shed.",
    "Last, check that the helmet clip closes and that you can fit no more than two fingers "
    "under the strap.",
    "A helmet that moves when you shake your head is doing about half its job.",
  ])],
  "items": [
    ("author_purpose", "medium", 0.93, ONE, [(0, 1)],
     'The instructions begin by saying: "{q}" Why start here?',
     "to explain why the check is weekly rather than daily",
     [("to warn that the check takes a very long time", "unsupported"),
      ("to suggest the check is not really necessary", "contradicts"),
      ("to describe how often a bike ought to be fully serviced", "wrong_focus")],
     "The sentence defends the frequency by naming what goes wrong if it is too high. To "
     "suggest the check is not really necessary is the opposite of a list that follows it."),

    ("detail", "medium", 0.92, ONE, [(0, 3)],
     'The instructions say: "{q}" What shows that a brake is working?',
     "a gap of two fingers or more remains at the lever",
     [("the lever touches the handlebar when squeezed", "contradicts"),
      ("the lever moves further than two fingers' width", "half_right"),
      ("the lever springs back quickly when released", "unsupported")],
     "Two fingers of clearance is the measure the instructions give. The lever moves "
     "further than two fingers' width describes the same gap closing, which is the "
     "failure the next sentence names."),

    ("inference", "medium", 0.92, ONE, [(0, 8)],
     'The instructions say: "{q}" What is the reason for the drop test?',
     "to find loose parts while the bike is standing still",
     [("to check that the front wheel is properly inflated", "wrong_focus"),
      ("to make sure the bike can survive a heavy landing", "overreach"),
      ("to confirm the wheel is not buckled out of shape", "half_right")],
     "A rattle heard in the shed is a fault found before it becomes one on the road. To "
     "make sure the bike can survive a heavy landing turns a listening test into a "
     "strength test."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 10)],
     'The instructions say: "{q}" What does this mean?',
     "the repair is beyond what can be done at home",
     [("a spanner is the wrong size for the job", "literal"),
      ("the wheel should be thrown away immediately", "overreach"),
      ("the shed is not a safe place to work in", "wrong_focus")],
     "Naming the workshop against the shed marks the line between the two kinds of "
     "repair. A spanner is the wrong size for the job reads a general point about "
     "difficulty as a point about one tool."),

    ("cause_effect", "medium", 0.92, ONE, [(0, 6)],
     'According to the instructions, what does a soft tyre most often cause?',
     "a tube pinched between the rim and the road",
     [("a wheel that goes out of shape over time", "wrong_focus"),
      ("brakes that fail to grip in wet weather", "unsupported"),
      ("a brake lever that pulls back to the handlebar", "contradicts")],
     "The consequence is stated in the same sentence as the test. A wheel that goes out "
     "of shape over time belongs to the buckling check further down the list."),

    ("main_idea", "medium", 0.92, ONE, [],
     'What do these instructions try to do beyond listing checks?',
     "give a reason for each check so it is remembered",
     [("explain how to repair every fault they describe", "contradicts"),
      ("persuade readers that cycling is a dangerous activity", "overreach"),
      ("compare a bicycle with other kinds of vehicle", "unsupported")],
     "Almost every step is followed by what it prevents. Explain how to repair every "
     "fault they describe is ruled out by a buckled wheel being sent to a workshop."),
  ],
 },
 {
  "title": "Waiting for the Tow Truck",
  "topic": "Narrative",
  "extracts": [("", [
    "The car stopped forty kilometres short of anywhere, which Dad said was the most "
    "efficient possible place for it to stop.",
    "There was no shade.",
    "There was a fence, and behind the fence a paddock with nothing in it but a water "
    "trough and a very long view.",
    "The tow truck was ninety minutes away and then it was two hours away, because "
    "somebody nearer had needed it more.",
    "Mum got out the emergency box, which we had never opened, and it turned out to "
    "contain a first aid kit, a torch with no batteries, four muesli bars from a year we "
    "could all remember, and a deck of cards.",
    "We played five hundred on the bonnet.",
    "Dad, who does not lose at cards and has never once let anybody forget it, lost three "
    "hands in a row and blamed the wind.",
    "My sister, who is nine and was in the worst mood of her life at the start of it, "
    "laughed so hard at the third loss that she had to sit down on the gravel.",
    "The tow truck came at ten past five.",
    "The driver said sorry about the wait and Mum said, honestly, no trouble, and meant it "
    "in a way I could hear.",
    "We have had two proper holidays since then and nobody has mentioned either of them.",
  ])],
  "items": [
    ("inference", "medium", 0.93, ONE, [(0, 0)],
     'The passage opens: "{q}" What is Dad doing here?',
     "making a joke about how badly placed the breakdown is",
     [("praising the car for stopping in a genuinely safe spot", "literal"),
      ("explaining how the engine came to fail", "wrong_focus"),
      ("blaming the family for the route they took", "unsupported")],
     "Calling the worst possible place the most efficient one is dry humour, not "
     "approval. Praising the car for stopping in a safe spot takes the sentence at face "
     "value."),

    ("inference", "medium", 0.92, ONE, [(0, 4)],
     'The passage describes the emergency box. What does its contents suggest?',
     "the family had never needed it before",
     [("the box was checked before every long trip", "wrong_focus"),
      ("somebody had taken things out of the box", "unsupported"),
      ("the box had been emptied on an earlier trip", "contradicts")],
     "Dead batteries and muesli bars old enough to date are the signs of a box packed "
     "once and forgotten. The box was checked before every long trip cannot be right for "
     "a box the family says it had never opened."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 9)],
     'The narrator writes: "{q}" What does "meant it" tell us?',
     "she was not simply being polite",
     [("she spoke more loudly than she needed to", "wrong_focus"),
      ("she was annoyed and hiding it well", "contradicts"),
      ("she had said the same thing several times", "unsupported")],
     "The narrator hears sincerity where he expected a courtesy, which is the point of "
     "the phrase. She was annoyed and hiding it well is the reading 'meant it' exists to "
     "rule out."),

    ("author_purpose", "medium", 0.92, ONE, [(0, 6)],
     'The passage says: "{q}" Why does the writer include this detail?',
     "to show the afternoon turning the usual order upside down",
     [("to explain why the family stopped playing cards", "contradicts"),
      ("to show that Dad was a poor loser about the game", "half_right"),
      ("to describe the weather conditions out at the roadside", "wrong_focus")],
     "The man who never loses losing three times is the day being unlike other days. To "
     "prove that Dad was a poor card player really contradicts a sentence that says he "
     "does not lose."),

    ("main_idea", "hard", 0.90, ONE, [(0, 10)],
     'The passage ends: "{q}" What does this ending suggest?',
     "the breakdown was better remembered than the holidays",
     [("the family stopped going on holidays after that", "contradicts"),
      ("nobody in the family enjoys talking about trips", "overreach"),
      ("the two later holidays went badly wrong in the same way", "unsupported")],
     "Two holidays nobody mentions, set against an afternoon told in detail, makes the "
     "comparison for the reader. The family stopped going on holidays after that is "
     "contradicted by the two that followed."),

    ("cause_effect", "medium", 0.92, ONE, [(0, 3)],
     'Why did the wait get longer rather than shorter?',
     "another breakdown was judged more urgent",
     [("the truck could not find the right road", "unsupported"),
      ("the driver had trouble with the truck itself", "wrong_focus"),
      ("the car started working again by itself", "contradicts")],
     "The passage gives the reason in the same sentence as the delay. The car started "
     "working again by itself is ruled out by a tow truck arriving at ten past five."),
  ],
 },
 {
  "title": "The Bird That Copies Everything",
  "topic": "Science",
  "extracts": [("", [
    "A superb lyrebird can reproduce almost any sound it hears often enough.",
    "The famous recordings are of chainsaws and camera shutters, and those recordings have "
    "given people the wrong idea about what the bird is doing.",
    "A lyrebird is not imitating a chainsaw because it finds chainsaws interesting.",
    "Male lyrebirds sing to attract females, and a male with a longer and more varied song "
    "is a male who has survived long enough to learn one.",
    "The song is a record of time spent alive.",
    "Most of what a wild lyrebird copies is other birds: whipbirds, rosellas, kookaburras, "
    "sometimes twenty species in a single performance.",
    "The chainsaws turn up mainly in birds that live near people, and mostly in birds that "
    "have been kept in captivity.",
    "One famous chainsaw recording is now thought to come from a bird raised in a zoo.",
    "None of this makes the ability less remarkable.",
    "It only means the bird is doing something more interesting than a party trick.",
    "It is carrying, in its throat, a list of everything that has been near it.",
  ])],
  "items": [
    ("inference", "medium", 0.93, ONE, [(0, 3), (0, 4)],
     'The passage explains: "{q}" Why does a longer song attract a female?',
     "it shows the male has lived long enough to learn it",
     [("it proves the male can sing more loudly", "wrong_focus"),
      ("it means the male has travelled a long way", "unsupported"),
      ("it shows the male is younger than all of the others", "contradicts")],
     "Length stands for time survived, which is what the next sentence calls a record. It "
     "shows the male is younger than the others reverses the whole logic."),

    ("author_purpose", "medium", 0.92, ONE, [(0, 1)],
     'Why does the writer mention the famous recordings so early?',
     "to correct an impression the reader probably already has",
     [("to prove that the famous recordings were faked by somebody", "overreach"),
      ("to explain how the recordings were made", "wrong_focus"),
      ("to argue that chainsaws harm the birds", "unsupported")],
     "The passage names the well-known idea in order to spend the rest of itself "
     "adjusting it. To prove that the recordings were faked goes beyond a text that says "
     "one bird was zoo-raised."),

    ("detail", "medium", 0.92, ONE, [(0, 5)],
     'According to the passage, what does a wild lyrebird mostly copy?',
     "the calls of other bird species",
     [("machinery it hears near houses", "contradicts"),
      ("only calls it has heard within the last week", "unsupported"),
      ("every sound it has ever heard even once", "overreach")],
     "Whipbirds, rosellas and kookaburras, sometimes twenty species at once. Machinery it "
     "hears near houses is what the passage assigns to birds living near people, not to "
     "wild ones generally."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 9)],
     'The writer says: "{q}" What is meant by "party trick"?',
     "an amusing skill with no purpose behind it",
     [("a game played by children at a birthday", "literal"),
      ("a sound that only occurs indoors", "wrong_sense"),
      ("a skill the bird has been taught by people", "wrong_focus")],
     "The phrase names the shallow reading the passage is arguing against. A skill the "
     "bird has been taught by people is a different claim, and one the passage never "
     "makes about wild birds."),

    ("cause_effect", "medium", 0.92, ONE, [(0, 6)],
     'Why do chainsaw sounds appear mainly in some lyrebirds and not others?',
     "those birds have lived where such sounds are common",
     [("those birds have far better hearing than all the rest", "unsupported"),
      ("chainsaws are louder than any bird call is", "wrong_focus"),
      ("wild lyrebirds are unable to copy machines", "overreach")],
     "A bird copies what it hears often, so proximity explains the difference. Wild "
     "lyrebirds are unable to copy machines is stronger than a passage that only says "
     "they rarely do."),

    ("main_idea", "hard", 0.90, ONE, [(0, 10)],
     'The passage ends: "{q}" What does the writer want the reader to take from this?',
     "the song is a record of the bird's whole life",
     [("the bird should be kept away from machinery", "unsupported"),
      ("the bird can carry objects inside its throat", "literal"),
      ("the bird copies sounds without any purpose", "contradicts")],
     "A list of everything that has been near it is a life measured in sound. The bird "
     "copies sounds without any purpose is exactly the idea the passage set out to "
     "correct."),
  ],
 },
]


if __name__ == "__main__":
    GEN.mkdir(parents=True, exist_ok=True)
    qs = build(PASSAGES, BOOK, NN, CATEGORY, LABEL)
    path = GEN / f"{BOOK}_p{NN}.json"
    path.write_text(json.dumps(qs, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(qs)} questions across {len(PASSAGES)} passages -> {path}")
