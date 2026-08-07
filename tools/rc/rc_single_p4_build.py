#!/usr/bin/env python3
"""Builds rc_nsw_single_p4.json — 6 passages x 6 items = 36 answer slots (§3.1 type 3.1).

Fourth single-passage batch: a hospital waiting room, how the Hills Hoist's rival lost, an
argument about school reports, a recipe card, a dog that would not swim, and why some
beaches squeak.

Eighteen passages already exist in this type, so the risk from here is repetition rather
than error — of subject, of stem frame, and of the shape of the key. Every main-idea and
author-purpose stem in this batch is phrased differently from the eighteen before it, and
the near-duplicate screen at 0.82 is what actually enforces that.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.rc.paired_common import build  # noqa: E402

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/reading_comprehension/generated"
NN = 4
BOOK = "rc_nsw_single"
CATEGORY = "single_passage"
LABEL = "Single-passage comprehension"
ONE = []

PASSAGES = [
 {
  "title": "Waiting Room",
  "topic": "Narrative",
  "extracts": [("", [
    "My brother put his arm through a window at four in the afternoon and by five we were "
    "in a room with a television bolted to the ceiling.",
    "It was showing a cooking programme with the sound off.",
    "Mum filled in a form on a clipboard and got to a question she read twice and then "
    "asked me to check she had understood.",
    "She had understood.",
    "She just did not want to be the only person who had read it.",
    "A man opposite us had been there since before we arrived and had a bandage that was "
    "clearly doing its job, and every time somebody was called he looked up and then did "
    "not stand.",
    "By seven he had stopped looking up.",
    "I asked Mum why he had been there so long when we had not, and she said because he is "
    "not bleeding as fast, which I thought about for the rest of the night.",
    "It was not unfair.",
    "It was the opposite of unfair, and it still felt terrible to be the reason he was "
    "waiting.",
    "My brother had eleven stitches and told everybody at school it was fourteen.",
  ])],
  "items": [
    ("inference", "medium", 0.93, ONE, [(0, 3), (0, 4)],
     'The narrator says: "{q}" Why did Mum ask her son to check the form?',
     "she wanted somebody else to share the decision",
     [("she was unable to read the question herself", "contradicts"),
      ("she thought her son knew more about hospitals", "unsupported"),
      ("she had filled in the whole form incorrectly", "overreach")],
     "The narrator says outright that she had understood, so the asking was about company "
     "rather than comprehension. She was unable to read the question herself is exactly "
     "what the sentence rules out."),

    ("inference", "medium", 0.92, ONE, [(0, 6)],
     'The narrator notes: "{q}" What does this suggest about the man?',
     "he had given up expecting to be called",
     [("he had fallen asleep in the waiting room", "unsupported"),
      ("he had already been treated and was leaving", "contradicts"),
      ("he had already been waiting when they arrived", "half_right")],
     "Looking up each time and then not standing, and finally not looking up, is hope "
     "wearing out. He had already been treated and was leaving cannot fit a man still "
     "sitting there at seven."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 9)],
     'The narrator writes: "{q}" What does he mean by "the opposite of unfair"?',
     "the system was working exactly as it should",
     [("the system was even more unfair than it looked", "contradicts"),
      ("the wait was longer than anybody had expected", "wrong_focus"),
      ("nobody in the room understood the rules at all", "unsupported")],
     "Being seen in order of urgency is fairness itself, which is what makes the feeling "
     "so uncomfortable. The system was even more unfair than it looked is the reading the "
     "phrase is written to prevent."),

    ("author_purpose", "medium", 0.92, ONE, [],
     'Why does the writer end with the detail about the stitches?',
     "to close a serious evening on an ordinary note",
     [("to show that the brother had been badly hurt", "half_right"),
      ("to prove that the hospital had made a mistake", "unsupported"),
      ("to explain why the family waited for so long", "contradicts")],
     "A boy exaggerating to his friends returns the story to normal life after a hard "
     "hour. To explain why the family waited for so long contradicts a passage in which "
     "they waited less than others."),

    ("main_idea", "hard", 0.90, ONE, [],
     'Which of these captures the whole passage?',
     "learning that something fair can still feel wrong",
     [("the treatment of a cut arm in a hospital", "wrong_focus"),
      ("a family who were treated unfairly that night", "contradicts"),
      ("how long people are made to wait for care", "half_right")],
     "The narrator says he thought about it for the rest of the night, and what he "
     "thought about was that discomfort. A family who were treated unfairly that night "
     "reverses the passage's own conclusion."),

    ("detail", "medium", 0.92, ONE, [(0, 7)],
     'According to Mum, why had the man waited longer than they had?',
     "his injury was less urgent than the brother's",
     [("he had arrived at the hospital much later", "contradicts"),
      ("he had not filled in the clipboard form", "unsupported"),
      ("his bandage was clearly doing its job already", "half_right")],
     "Not bleeding as fast is a statement about urgency, which is how the order is set. "
     "He had arrived at the hospital much later is the opposite of a man who was there "
     "before they came."),
  ],
 },
 {
  "title": "The Rival Nobody Remembers",
  "topic": "History",
  "extracts": [("", [
    "Lance Hill was not the only person building a rotary clothes line in Adelaide after "
    "the war.",
    "Gilbert Toyne had patented one twenty years earlier, in 1926, and his was in several "
    "ways the better machine.",
    "It was all metal, it could be wound up and down, and it had a mechanism that kept the "
    "arms level under an uneven load.",
    "Toyne sold them steadily through the 1930s.",
    "What he did not do was arrive at the right moment.",
    "Hill's hoist came out in 1945, into a country about to build hundreds of thousands of "
    "houses on quarter-acre blocks, all of which needed somewhere to hang washing.",
    "Toyne's patents had also begun to expire, which meant anybody could copy the good "
    "parts without paying him.",
    "By the 1950s the word for the object was Hills, and a word is very hard to take back.",
    "Toyne is remembered now mostly by people who collect clothes lines, which is a "
    "smaller group than you would hope.",
    "The lesson is not that the better design wins.",
    "It is that being early is a different thing from being first.",
  ])],
  "items": [
    ("detail", "medium", 0.93, ONE, [(0, 2)],
     'The passage states: "{q}" What made Toyne\'s design good?',
     "it stayed level even when loaded unevenly",
     [("it was made of timber rather than metal", "contradicts"),
      ("it was much cheaper than the Hills hoist", "unsupported"),
      ("it was the only rotary clothes line ever made", "overreach")],
     "The levelling mechanism is the feature the sentence singles out. It was made of "
     "timber rather than metal contradicts the same sentence, which says all metal."),

    ("inference", "medium", 0.92, ONE, [(0, 5)],
     'The passage explains: "{q}" Why did the timing help Hill?',
     "a whole country was about to need what he sold",
     [("Hill had been building hoists for twenty years", "contradicts"),
      ("the houses were built with hoists already fitted", "unsupported"),
      ("the houses were built because of the hoist", "half_right")],
     "Hundreds of thousands of new backyards is demand arriving at the same moment as the "
     "product. The houses were built because of the hoist reverses the order: the houses "
     "came first and created the need."),

    ("cause_effect", "medium", 0.92, ONE, [(0, 6)],
     'What effect did the expiry of Toyne\'s patents have?',
     "his best ideas could be used without payment",
     [("his hoists stopped working after that date", "literal"),
      ("he was able to sell far more of them", "contradicts"),
      ("he was given money by the government", "unsupported")],
     "An expired patent removes the protection, not the product. His hoists stopped "
     "working after that date confuses a legal date with a mechanical one."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 7)],
     'The passage says: "{q}" What does this mean?',
     "once people call it Hills, the name sticks",
     [("the Hills company owned the word by law", "unsupported"),
      ("people stopped using the word altogether", "contradicts"),
      ("the word was difficult to say out loud", "wrong_sense")],
     "The point is about habit rather than about ownership: a name in common use is not "
     "easily replaced. The Hills company owned the word by law adds a legal claim the "
     "passage never makes."),

    ("author_purpose", "hard", 0.90, ONE, [(0, 10)],
     'The passage ends: "{q}" What distinction is the writer drawing?',
     "arriving first is not the same as arriving at the right time",
     [("being early always guarantees a better product in the end", "contradicts"),
      ("a design can only succeed if it is patented", "overreach"),
      ("patents are more important than good design", "wrong_focus")],
     "Toyne was first by twenty years and it did not help him. A design can only succeed if "
     "it is patented is more than the passage claims — Toyne held the patent and still "
     "lost."),

    ("main_idea", "medium", 0.92, ONE, [],
     'This passage was written mainly to explain —',
     "why the better machine is not the one remembered",
     [("how a rotary clothes line is actually put together", "wrong_focus"),
      ("that Lance Hill copied Toyne's invention", "overreach"),
      ("how patents are granted and then expire", "half_right")],
     "The passage compares two designs and explains the outcome by timing rather than "
     "quality. That Lance Hill copied Toyne's invention goes beyond a passage that says "
     "anybody could copy the expired parts."),
  ],
 },
 {
  "title": "What a Report Cannot Say",
  "topic": "Opinion",
  "extracts": [("", [
    "Twice a year a school sends home a document that everybody treats as a summary of a "
    "child, and it is not that.",
    "A report is a summary of what a school is able to measure, which is a much smaller "
    "thing.",
    "It can measure whether a student can find the main idea of a paragraph.",
    "It cannot measure whether that student is the person the class turns to when "
    "somebody new arrives.",
    "One of those is on the report and the other is not, and a parent reading it at the "
    "kitchen table has no way of knowing which matters more in ten years.",
    "I am not arguing that reports should be abolished.",
    "A parent needs to know if a child cannot read, and needs to know early, and nothing "
    "else in the school system carries that news reliably.",
    "What I am arguing is that the document should say what it is.",
    "Three lines at the top would do it: this report covers these subjects, measured in "
    "these ways, over this period.",
    "It does not cover kindness, persistence, curiosity or courage, because we do not know "
    "how to measure those without ruining them.",
    "A report that admitted its own edges would be a better report, and a great deal "
    "easier to read at a kitchen table.",
  ])],
  "items": [
    ("main_idea", "medium", 0.93, ONE, [],
     'What change does the writer want made?',
     "a report that states what it does not cover",
     [("an end to school reports of every kind", "contradicts"),
      ("more subjects added to the current report", "wrong_focus"),
      ("a report written by the student rather than the school", "unsupported")],
     "The three lines proposed are a statement of scope, not a change to what is measured. "
     "A report written by the student rather than the school is nowhere in the piece."),

    ("author_purpose", "medium", 0.92, ONE, [(0, 6)],
     'Why does the writer point out what a report does carry?',
     "to show the document is worth keeping",
     [("to argue that reading is the only subject that matters", "overreach"),
      ("to explain how schools decide on a student's grade", "wrong_focus"),
      ("to admit that the whole argument is mistaken", "contradicts")],
     "Granting the report a real job protects the narrower proposal that follows. To "
     "admit that the whole argument is mistaken misreads a concession, since the very "
     "next sentence restates the claim."),

    ("inference", "medium", 0.92, ONE, [(0, 3)],
     'The writer says a report cannot measure: "{q}" Why choose this example?',
     "it names something valuable that no grade records",
     [("it is the easiest quality for a school to assess", "contradicts"),
      ("it describes a problem the school ought to fix", "wrong_focus"),
      ("it shows that new students are usually ignored", "unsupported")],
     "The example is chosen precisely because it matters and cannot appear. It is the "
     "easiest quality for a school to assess is the opposite of a quality the writer says "
     "cannot be measured."),

    ("vocabulary_in_context", "hard", 0.90, ONE, [(0, 10)],
     'The writer says: "{q}" What does "admitted its own edges" mean?',
     "said plainly where its usefulness stops",
     [("apologised for the grades it contained", "wrong_focus"),
      ("was printed with a border around it", "literal"),
      ("was shorter than the current report", "unsupported")],
     "Edges are the limits of what the document covers, which the proposed three lines "
     "would state. Was printed with a border around it takes a word about scope and makes "
     "it a fact about the paper."),

    ("cause_effect", "medium", 0.92, ONE, [(0, 4)],
     'According to the writer, what is the effect on a parent reading the report?',
     "they cannot tell what has been left out",
     [("they learn more about the child than the school knows", "contradicts"),
      ("they usually disagree with the grades given", "unsupported"),
      ("they read the report somewhere other than at home", "wrong_focus")],
     "The parent sees one column and has no way of knowing which of the two matters more. "
     "They read the report somewhere other than at home moves the problem to the setting, "
     "which is not what the sentence is about."),

    ("detail", "medium", 0.92, ONE, [(0, 8)],
     'What exactly does the writer propose adding?',
     "three lines naming the subjects, methods and period",
     [("a full page explaining how grades are worked out", "overreach"),
      ("a separate report on kindness and persistence", "contradicts"),
      ("a shorter report with fewer subjects on it", "unsupported")],
     "The proposal is stated in one sentence and is deliberately small. A separate report "
     "on kindness and persistence is ruled out by the sentence about ruining them."),
  ],
 },
 {
  "title": "Nan's Anzac Biscuits",
  "topic": "Functional",
  "extracts": [("", [
    "Makes about twenty-four. Oven at 160, not 180, and if that seems low it is because "
    "everybody burns these.",
    "One cup rolled oats, one cup plain flour, one cup brown sugar, three-quarters of a "
    "cup of desiccated coconut.",
    "Mix the dry ingredients in the biggest bowl you have, because you will be folding "
    "later and a small bowl makes that miserable.",
    "125 grams butter and two tablespoons of golden syrup, melted together over low heat.",
    "Take it off the heat before it bubbles.",
    "Dissolve one teaspoon of bicarbonate of soda in two tablespoons of boiling water and "
    "stir it into the butter, which will foam up.",
    "That foam is the whole point: it is what makes the biscuit light instead of hard.",
    "Pour the wet into the dry and fold until there is no loose flour.",
    "Roll into balls slightly smaller than a golf ball and flatten them a little, because "
    "they spread more than you expect.",
    "Fifteen minutes for chewy, eighteen for crunchy, and there is no correct answer, "
    "though people will tell you there is.",
    "Leave them on the tray for five minutes before moving them or they will fall apart.",
  ])],
  "items": [
    ("author_purpose", "medium", 0.93, ONE, [(0, 0)],
     'The recipe opens: "{q}" Why does it explain the oven temperature?',
     "to stop the reader raising it out of habit",
     [("to warn that the biscuits take a long time", "unsupported"),
      ("to explain why the recipe makes twenty-four", "wrong_focus"),
      ("to show that the oven is probably broken", "overreach")],
     "Naming the common error is what stops it being repeated. To explain why the recipe "
     "makes twenty-four attaches the reason to the wrong part of the sentence."),

    ("cause_effect", "medium", 0.92, ONE, [(0, 6)],
     'The recipe says of the foam: "{q}" What would happen without it?',
     "the biscuits would come out hard",
     [("the biscuits would not hold together", "wrong_focus"),
      ("the biscuits would burn in the oven", "unsupported"),
      ("the biscuits would be lighter than they should be", "contradicts")],
     "Light instead of hard names the alternative directly. The biscuits would not hold "
     "together is what happens if they are moved too early, further down the recipe."),

    ("inference", "medium", 0.92, ONE, [(0, 2)],
     'The recipe says to use the biggest bowl you have. Why?',
     "folding in a small bowl is difficult",
     [("the mixture doubles in size as it cooks", "unsupported"),
      ("a large bowl is easier to wash afterwards", "wrong_focus"),
      ("the bowl needs room for the mixture to rise", "contradicts")],
     "The reason is given in the same sentence as the instruction. The mixture doubles in "
     "size as it cooks describes the tray, not the bowl."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 7)],
     'The recipe says: "{q}" What does "fold" mean here?',
     "mix gently until it just comes together",
     [("bend the mixture over on itself in half", "literal"),
      ("beat the mixture as hard as possible", "contradicts"),
      ("leave the mixture to rest before baking", "wrong_focus")],
     "Folding is the gentle mixing the large bowl was recommended for. Beat the mixture "
     "as hard as possible is the opposite of what the word means in a kitchen."),

    ("detail", "medium", 0.92, ONE, [(0, 9)],
     'According to the recipe, what is the difference between fifteen and eighteen '
     'minutes?',
     "chewy biscuits rather than crunchy ones",
     [("burnt biscuits rather than cooked ones", "unsupported"),
      ("twenty-four biscuits rather than twelve", "wrong_focus"),
      ("biscuits left on the tray rather than moved", "half_right")],
     "The sentence gives both times and both results. Burnt biscuits rather than cooked "
     "ones belongs to the oven temperature at the top, not to the three minutes."),

    ("main_idea", "hard", 0.90, ONE, [],
     'How does this recipe differ from one that simply lists steps?',
     "it explains what goes wrong and why",
     [("it gives the ingredients in metric measurements", "wrong_focus"),
      ("it insists there is one correct baking time", "contradicts"),
      ("it assumes the reader has never baked before", "unsupported")],
     "Burning, miserable folding, spreading, falling apart — each warning comes with its "
     "cause. It insists there is one correct baking time is the opposite of a recipe that "
     "says there is no correct answer."),
  ],
 },
 {
  "title": "The Dog Who Would Not Swim",
  "topic": "Narrative",
  "extracts": [("", [
    "Every dog swims, people told us, and for four years ours did not.",
    "She would go in to her knees at the river and stand there like somebody waiting for a "
    "bus, and if you went deeper she would bark at you until you came back.",
    "Dad said she was being sensible.",
    "My cousin said she was broken.",
    "I thought about it more than either of them, because she was mine.",
    "Then in her fifth summer my youngest cousin, who was three, walked off the bank in "
    "the way three-year-olds do, without any noise at all.",
    "The dog was in before any of us had stood up.",
    "She did not do anything clever.",
    "She swam a circle around him, badly, and made a noise none of us had heard before, "
    "and Dad was there in about four seconds.",
    "Afterwards she came out and shook herself and would not go back in.",
    "She has never swum again.",
    "I do not think she was ever afraid of the water.",
    "I think she had simply never been given a reason she agreed with.",
  ])],
  "items": [
    ("inference", "medium", 0.93, ONE, [(0, 1)],
     'The narrator describes: "{q}" What does the dog\'s behaviour show?',
     "she wanted everybody to stay where she could reach them",
     [("she was frightened of the noise the river was making", "unsupported"),
      ("she had entered the water many times before", "contradicts"),
      ("she was guarding the bank against strangers", "half_right")],
     "Standing at the edge and barking people back is herding, not fear of the water "
     "itself. She was guarding the bank against strangers gets the direction wrong: she "
     "is keeping her own people in, not keeping others out."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 3)],
     'The passage says: "{q}" What does the cousin mean by that word?',
     "there is something wrong with her",
     [("she had been injured in the water once", "unsupported"),
      ("she is unable to walk on land properly", "wrong_sense"),
      ("she has been taken apart into pieces", "literal")],
     "Used of an animal, the word claims a fault rather than damage. She has been taken "
     "apart into pieces reads a figure of speech as a description."),

    ("inference", "hard", 0.90, ONE, [(0, 7), (0, 8)],
     'The narrator says: "{q}" Why does he point out that she did nothing clever?',
     "the point is that she went in at all",
     [("she made the situation worse by going in", "contradicts"),
      ("another dog would have done it far better", "unsupported"),
      ("the circling was the cleverest part of it", "half_right")],
     "Swimming badly is still swimming, after four years of refusing. She made the "
     "situation worse by going in is contradicted by Dad arriving in four seconds."),

    ("cause_effect", "medium", 0.92, ONE, [],
     'What made the dog enter the water?',
     "a small child had gone off the bank",
     [("the family had called her in repeatedly", "contradicts"),
      ("the water was warmer that summer", "unsupported"),
      ("she had finally learned how to swim", "wrong_focus")],
     "The three-year-old walking off the bank is the only thing that changed. The family "
     "had called her in repeatedly is what they had done for four years without success."),

    ("main_idea", "medium", 0.92, ONE, [(0, 12)],
     'The passage ends: "{q}" What conclusion does the narrator reach?',
     "she was not afraid, she was unconvinced",
     [("she had been afraid of the water all along", "contradicts"),
      ("she was a better swimmer than anybody knew", "overreach"),
      ("she should have been trained to swim earlier", "wrong_focus")],
     "A reason she agreed with is the missing thing, not courage. She had been afraid of "
     "the water all along is what the sentence before it explicitly denies."),

    ("author_purpose", "medium", 0.92, ONE, [],
     'Why does the writer give both Dad\'s view and the cousin\'s?',
     "to show the question had no agreed answer",
     [("to prove that Dad was right about the dog", "unsupported"),
      ("to explain why the dog belonged to the narrator", "wrong_focus"),
      ("to show the family argued about everything", "overreach")],
     "Two flat contradictory verdicts set up the narrator's own, which arrives at the "
     "end. To show the family argued about everything is far more than two opinions about "
     "one dog."),
  ],
 },
 {
  "title": "The Beach That Squeaks",
  "topic": "Science",
  "extracts": [("", [
    "Walk on some beaches and the sand squeaks under your feet.",
    "Walk on most beaches and it does not.",
    "The difference is not the beach; it is the grains.",
    "Squeaking sand is almost pure quartz, the grains are close to the same size, and they "
    "are rounded rather than jagged.",
    "When a foot presses down, a whole layer of grains slides over the layer beneath at "
    "once, and that sudden shared movement makes the sound.",
    "Anything that stops the grains moving together kills it.",
    "Salt does, which is why some beaches squeak after rain and not before.",
    "So does a small amount of clay, or fine shell, or pollution.",
    "This makes squeaking sand a rough test of how clean a beach is, though nobody would "
    "call it a precise one.",
    "It also makes it fragile.",
    "A beach that has squeaked for centuries can stop after one wet season that washes "
    "silt down a creek, and it does not always start again.",
  ])],
  "items": [
    ("detail", "medium", 0.93, ONE, [(0, 3)],
     'The passage states: "{q}" What are the three features of squeaking sand?',
     "pure quartz, even in size, and rounded",
     [("pure quartz, varied in size, and jagged", "contradicts"),
      ("pure quartz, even in size, and very fine", "half_right"),
      ("pure quartz, even in size, and always wet", "unsupported")],
     "The sentence lists all three together. Pure quartz, varied in size, and jagged "
     "reverses two of the three."),

    ("inference", "hard", 0.90, ONE, [(0, 4)],
     'The passage explains: "{q}" What causes the sound?',
     "many grains moving as one at the same moment",
     [("grains rubbing against each other slowly", "wrong_focus"),
      ("air escaping from between the wet grains", "unsupported"),
      ("the weight of a person pressing the sand flat", "half_right")],
     "The sound comes from a whole layer sliding at once, not from friction over time. "
     "The weight of a person pressing the sand flat is what starts it, but the passage "
     "puts the sound in the shared movement."),

    ("cause_effect", "medium", 0.92, ONE, [(0, 6)],
     'The passage says: "{q}" Why does rain make a difference?',
     "it washes away the salt that was stopping the sliding",
     [("it makes the grains heavier and much easier to press", "unsupported"),
      ("it rounds off the jagged edges of the grains", "wrong_focus"),
      ("it adds salt to the sand from the sea spray", "contradicts")],
     "Salt is named as something that kills the squeak, so removing it restores the "
     "sound. It adds salt to the sand from the sea spray has the effect the wrong way "
     "round."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 5)],
     'The passage says: "{q}" What does "kills" mean here?',
     "stops the squeaking completely",
     [("destroys the grains of sand themselves", "literal"),
      ("harms the animals that live in the sand", "wrong_focus"),
      ("makes the beach dangerous to walk on", "unsupported")],
     "The word applies to the sound, which is the subject of the paragraph. Destroys the "
     "grains of sand themselves takes a word used of an effect and applies it to the "
     "material."),

    ("author_purpose", "medium", 0.92, ONE, [(0, 8)],
     'Why does the writer add the qualification: "{q}"?',
     "to stop the reader treating it as a real measurement",
     [("to argue that the beaches are not really clean at all", "unsupported"),
      ("to explain how scientists measure pollution", "wrong_focus"),
      ("to prove that the test does not work at all", "overreach")],
     "Calling it rough and then denying precision keeps the claim modest. To prove that "
     "the test does not work at all goes further than a writer who still calls it a "
     "test."),

    ("main_idea", "hard", 0.90, ONE, [(0, 10)],
     'The passage ends: "{q}" What does the ending add?',
     "the squeak is easily lost and hard to recover",
     [("silt is the only thing that can stop the squeak", "contradicts"),
      ("all squeaking beaches will fall silent eventually", "overreach"),
      ("silt in a creek improves the squeak over time", "wrong_focus")],
     "Centuries undone by one wet season, and not always restored, is fragility. Silt in a "
     "creek improves the squeak over time reverses the one cause the sentence names."),
  ],
 },
]


if __name__ == "__main__":
    GEN.mkdir(parents=True, exist_ok=True)
    qs = build(PASSAGES, BOOK, NN, CATEGORY, LABEL)
    path = GEN / f"{BOOK}_p{NN}.json"
    path.write_text(json.dumps(qs, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(qs)} questions across {len(PASSAGES)} passages -> {path}")
