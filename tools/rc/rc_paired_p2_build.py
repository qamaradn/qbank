#!/usr/bin/env python3
"""Builds rc_nsw_paired_p2.json — 4 pairs x 4 items = 16 answer slots (§3.4).

Second paired batch. Pairs not used by p1 (school fete, skate park, rainfall, Maria
Island): a closing corner shop, a whale in the harbour, an argument about homework, and a
snake in a shed.

Each pair sets two text TYPES against each other as well as two attitudes — a history
society note against the shopkeeper himself, a scientist's briefing against a school
newspaper, a principal's column against a parent's email, a safety advice sheet against
the family story of following it. Two of the four items in every pair reach across both
extracts, enforced by `min_cross_extract`.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.rc.paired_common import build  # noqa: E402

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/reading_comprehension/generated"
NN = 2
BOOK = "rc_nsw_paired"
CATEGORY = "paired_extract"
LABEL = "Paired-extract comparison"

# item = (skill, difficulty, confidence, uses, quote_refs, stem, key, distractors, expl)
PASSAGES = [
 {
  "title": "The Last Milk Bar",
  "topic": "Community",
  "extracts": [
    ("Text 1", [
      "Kostas Milk Bar on Rowan Street closed in March after fifty-eight years.",
      "It opened in 1968, three years after the family arrived from Greece, and was the "
      "first shop in the street to sell ice cream by the scoop.",
      "Generations of children from Rowan Street Primary walked past it every afternoon.",
      "The building will be converted into two apartments.",
      "The society has photographed the interior and collected the original sign, which "
      "will be held in the local collection.",
      "Something has gone from the street that cannot be put back.",
    ]),
    ("Text 2", [
      "People keep telling me they are sad the shop has closed.",
      "I am seventy-four and I have been standing behind that counter since I was sixteen.",
      "For the last ten years we sold about forty dollars of ice cream on a good day, and "
      "I paid the electricity out of my own pocket.",
      "Everyone who is sad about it now was buying their milk at the supermarket.",
      "I am not bitter about that; a shop is a business, and a business needs customers.",
      "But I would rather people said thank you than sorry.",
    ]),
  ],
  "items": [
    ("author_purpose", "medium", 0.93, ["Text 1"], [],
     "What is the main purpose of the history society's note?",
     "record the closure and what the shop meant to the street",
     [("advertise the two apartments that will replace the shop", "contradicts"),
      ("persuade the council to prevent the building being converted", "unsupported"),
      ("explain how ice cream first came to be sold in Australia", "wrong_focus")],
     "It gives dates, describes the shop's place in the street, and notes what has been "
     "kept for the collection. Advertise the two apartments that will replace the shop "
     "mistakes a fact reported in passing for the reason the piece was written."),

    ("inference", "medium", 0.92, ["Text 2"], [(1, 3)],
     'Text 2 says: "{q}" The writer is pointing out that —',
     "the people mourning the shop are the ones who stopped using it",
     [("the supermarket sold milk that was cheaper and fresher than his", "wrong_focus"),
      ("the shop had stopped selling milk altogether some years earlier", "contradicts"),
      ("nobody in the street ever bought anything from him at all", "overreach")],
     "Setting their sadness beside where they actually shopped is the whole point of the "
     "sentence. Nobody in the street ever bought anything from him at all goes further "
     "than a writer who reports forty dollars of ice cream on a good day."),

    ("comparison", "medium", 0.92, ["Text 1", "Text 2"], [],
     'Both texts describe the same closure. How do their feelings about it differ?',
     "Text 1 mourns a loss; Text 2 treats it as an ordinary business coming to an end",
     [("Text 1 welcomes the change while Text 2 regrets it deeply", "contradicts"),
      ("Both texts are equally sorry that the shop has had to close", "half_right"),
      ("Neither text gives any reason at all for the shop closing", "wrong_focus")],
     "One says something has gone that cannot be put back; the other says a business needs "
     "customers. Both texts are equally sorry that the shop has had to close flattens a "
     "difference the second writer states outright."),

    ("comparison", "hard", 0.90, ["Text 1", "Text 2"], [],
     'What would the writer of Text 2 most likely say about the last sentence of Text 1?',
     "that being missed is not the same thing as being used",
     [("that the original sign should have stayed in the shop window", "wrong_focus"),
      ("that the history society should have bought the building itself", "unsupported"),
      ("that he agrees nothing has really been lost from the street", "contradicts")],
     "His closing line asks for thanks rather than sympathy, which is exactly the "
     "distinction. That he agrees nothing has really been lost from the street misreads a "
     "man who spent fifty-eight years behind that counter."),
  ],
 },
 {
  "title": "The Whale in the Harbour",
  "topic": "Science",
  "extracts": [
    ("Text 1", [
      "A juvenile humpback entered the harbour on Monday morning and has remained inside "
      "the heads since.",
      "Humpbacks migrate north along this coast between May and August, and a small "
      "number enter sheltered water each year.",
      "The animal appears to be in good condition and is feeding normally.",
      "Boat traffic has been restricted within three hundred metres of the whale.",
      "Most animals in this situation leave within a few days without any intervention.",
      "We are asking the public to watch from the shore rather than from the water.",
    ]),
    ("Text 2", [
      "There is a whale in the harbour.",
      "It is the biggest thing anyone at this school has ever seen and it is about four "
      "hundred metres from the ferry wharf.",
      "Ms Halloran took our class down at lunchtime and even she was excited, which has "
      "never happened before.",
      "Scientists say it will probably leave on its own, which everyone agrees is "
      "disappointing.",
      "There are boats that are not allowed to go near it and one of them got told off on "
      "Tuesday.",
      "If it is still there on Friday I am going again.",
    ]),
  ],
  "items": [
    ("detail", "medium", 0.93, ["Text 1"], [(0, 4)],
     'Text 1 states: "{q}" This tells the reader that —',
     "the whale is expected to leave without any help",
     [("the whale will have to be towed back out of the harbour", "contradicts"),
      ("whales rarely survive a visit into sheltered water like this", "unsupported"),
      ("the harbour has now been closed to every kind of boat", "overreach")],
     "'Without any intervention' says plainly that nothing needs to be done. The harbour "
     "has now been closed to every kind of boat goes beyond a restriction that applies "
     "within three hundred metres."),

    ("mood", "medium", 0.92, ["Text 2"], [(1, 3)],
     'Text 2 says: "{q}" This creates a tone of —',
     "cheerful disappointment that the excitement will end",
     [("anger at the scientists for driving the whale away again", "contradicts"),
      ("worry that the whale is in real danger of dying there", "unsupported"),
      ("relief that the whale will not be trapped in the harbour", "half_right")],
     "Calling a whale's safe departure 'disappointing' is a joke about wanting it to stay. "
     "Relief that the whale will not be trapped in the harbour is the sensible feeling, "
     "and is precisely the one the sentence refuses."),

    ("comparison", "medium", 0.92, ["Text 1", "Text 2"], [],
     'Both texts mention the restriction on boats. How do they differ?',
     "Text 1 states the rule; Text 2 reports somebody breaking it",
     [("Text 1 opposes the restriction while Text 2 supports it", "contradicts"),
      ("Both texts give exactly the same distance for the restriction", "wrong_focus"),
      ("Both texts treat the restriction as the most important part of the story",
       "overreach")],
     "One gives the three-hundred-metre limit; the other reports a boat being told off. "
     "Both texts give exactly the same distance for the restriction confuses Text 2's "
     "four hundred metres from the wharf with the limit around the animal."),

    ("comparison", "hard", 0.90, ["Text 1", "Text 2"], [],
     'How does the purpose of the two texts differ?',
     "Text 1 sets out to manage how people behave; Text 2 to share an experience",
     [("Text 1 sets out to entertain readers while Text 2 informs them", "contradicts"),
      ("Both texts were written to warn people away from the harbour entirely", "half_right"),
      ("Text 2 was written in order to correct a mistake made in Text 1", "unsupported")],
     "Text 1 restricts, asks and reassures; Text 2 records a lunchtime nobody will forget. "
     "Text 1 sets out to entertain readers while Text 2 informs them has the two the wrong "
     "way round."),
  ],
 },
 {
  "title": "Twenty Minutes and One Task",
  "topic": "School",
  "extracts": [
    ("Text 1", [
      "Several families have written to ask why Year 6 still sets homework.",
      "The answer is not that we believe an hour of worksheets makes anybody cleverer.",
      "It is that high school will expect students to manage work without being watched, "
      "and that habit takes about a year to build.",
      "Our homework is deliberately short: twenty minutes of reading and one task.",
      "If it is taking your child an hour, please tell us, because that is information we "
      "need.",
      "We would rather adjust the task than have families arguing about it at the kitchen "
      "table.",
    ]),
    ("Text 2", [
      "I read your column and I want to say that I am not against homework in principle.",
      "I am against homework that arrives on a Friday and is due on the Monday.",
      "My daughter reads for forty minutes every night without being asked, which I would "
      "have thought was the habit you are describing.",
      "What she does not do is remember a task set three days earlier, and neither would I.",
      "Could the task be set on the day it is meant to be started?",
      "That is the whole of my complaint, and I am sorry it took five paragraphs to reach "
      "it.",
    ]),
  ],
  "items": [
    ("author_purpose", "medium", 0.93, ["Text 1"], [],
     "The principal wrote this column mainly in order to —",
     "explain a policy and invite families to report problems with it",
     [("announce that homework is being abolished in Year 6 this year", "contradicts"),
      ("criticise the families who have written in to complain about it", "unsupported"),
      ("describe what high school teachers will expect of their students", "wrong_focus")],
     "It gives the reason, states the size of the task, and asks to be told when it "
     "overruns. Criticise the families who have written in to complain about it misreads "
     "a column that answers them politely."),

    ("inference", "medium", 0.92, ["Text 2"], [(1, 5)],
     'Text 2 ends: "{q}" This tells the reader that —',
     "the writer knows the complaint is a small and specific one",
     [("the writer has a long list of other complaints to make", "contradicts"),
      ("the writer no longer wants any reply from the school", "unsupported"),
      ("the writer is apologising for having been rude to the school", "wrong_focus")],
     "Apologising for the length is a way of marking how modest the request is. The writer "
     "is apologising for having been rude in the email mistakes an apology about five "
     "paragraphs for one about tone."),

    ("comparison", "medium", 0.92, ["Text 1", "Text 2"], [],
     'What do the two writers actually agree about?',
     "that the point of homework is building a habit of working independently",
     [("that twenty minutes is the right length for a reading task", "half_right"),
      ("that homework ought to be set on a Friday afternoon", "contradicts"),
      ("that reading is always more useful than any task a school sets", "unsupported")],
     "One says the habit takes a year to build; the other says her daughter already has "
     "it. That homework ought to be set on a Friday afternoon is the one thing the second "
     "writer objects to."),

    ("comparison", "hard", 0.90, ["Text 1", "Text 2"], [],
     'Text 1 offers to adjust a task rather than have families arguing. How does Text 2 '
     'take up that offer?',
     "by naming one precise change and asking for it",
     [("by arguing that homework should be stopped altogether in Year 6", "contradicts"),
      ("by asking the school to reduce the twenty minutes of reading", "wrong_focus"),
      ("by demanding an apology from the principal for the column", "overreach")],
     "The email identifies the Friday-to-Monday gap and proposes setting the task on the "
     "day it starts. By asking the school to reduce the twenty minutes of reading is the "
     "opposite of a parent whose daughter reads forty minutes unprompted."),
  ],
 },
 {
  "title": "Snake in the Shed",
  "topic": "Australian Wildlife",
  "extracts": [
    ("Text 1", [
      "If you find a snake inside a building, the first thing to do is nothing.",
      "Move people and pets out of the room and close the door behind you.",
      "Do not attempt to catch, kill or move the animal yourself.",
      "Most bites in this country happen to people who were trying to handle a snake.",
      "Call a licensed relocator, and keep watch on the door from outside so that you can "
      "tell them where it went.",
      "A snake that is left alone will usually stay in one place.",
    ]),
    ("Text 2", [
      "Grandad went into the shed for a rake and came out considerably faster than he "
      "went in.",
      "He shut the door, which the pamphlet says you should do, and then stood in front "
      "of it for two hours like a man guarding a bank.",
      "Mum rang the relocator and the relocator said forty minutes.",
      "The relocator arrived in ninety, by which time Grandad had told the story to three "
      "neighbours and it had grown.",
      "The snake was still exactly where it had been, behind a tin of paint, entirely "
      "uninterested in all of us.",
      "Grandad has not been back into the shed.",
    ]),
  ],
  "items": [
    ("author_purpose", "medium", 0.93, ["Text 1"], [],
     "The advice sheet exists mainly to —",
     "give a short set of instructions and the reason behind them",
     [("explain how snakes find their way into buildings", "wrong_focus"),
      ("persuade readers that snakes are harmless animals", "overreach"),
      ("describe how a licensed relocator does the job", "unsupported")],
     "Every sentence is either an instruction or the reason behind one. Persuade readers "
     "that snakes are harmless animals goes past a text that mentions bites in the very "
     "middle of it."),

    ("mood", "medium", 0.92, ["Text 2"], [(1, 1)],
     'Text 2 says: "{q}" The tone here is best described as —',
     "affectionate teasing of an overreaction",
     [("criticism of Grandad for having done the wrong thing", "contradicts"),
      ("fear that the snake was about to escape the shed", "unsupported"),
      ("admiration for Grandad's very great physical courage", "half_right")],
     "The writer notes that he did the right thing and then compares him to a bank guard, "
     "which is a joke rather than a complaint. Criticism of Grandad for having done the "
     "wrong thing misses the clause that says the pamphlet agrees with him."),

    ("comparison", "medium", 0.92, ["Text 1", "Text 2"], [],
     'Which instruction from Text 1 does Grandad actually follow?',
     "shutting the door and keeping watch on it from outside",
     [("calling the licensed relocator himself straight away", "contradicts"),
      ("moving every person and pet out of the whole yard", "overreach"),
      ("identifying which kind of snake was behind the paint", "unsupported")],
     "He shuts the door and stands in front of it, which is two of the instructions "
     "together. Calling the licensed relocator himself straight away belongs to Mum, who "
     "made the call."),

    ("comparison", "hard", 0.90, ["Text 1", "Text 2"], [],
     'Text 1 ends by saying a snake left alone will usually stay put. What in Text 2 '
     'bears that out?',
     "the snake was still behind the paint tin when help arrived",
     [("the relocator took ninety minutes instead of the promised forty", "wrong_focus"),
      ("Grandad stood in front of the shed door for a full two hours", "half_right"),
      ("the snake had moved into a different shed by the time they looked", "contradicts")],
     "An hour and a half passed and the animal had not moved at all, which is the claim "
     "tested. Grandad stood in front of the shed door for a full two hours describes what "
     "the people did, not what the snake did."),
  ],
 },
]


if __name__ == "__main__":
    GEN.mkdir(parents=True, exist_ok=True)
    qs = build(PASSAGES, BOOK, NN, CATEGORY, LABEL)
    path = GEN / f"{BOOK}_p{NN}.json"
    path.write_text(json.dumps(qs, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(qs)} questions across {len(PASSAGES)} pairs -> {path}")
