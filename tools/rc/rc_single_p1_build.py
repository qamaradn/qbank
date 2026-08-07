#!/usr/bin/env python3
"""Builds rc_nsw_single_p1.json — 6 passages x 6 items = 36 answer slots (§3.1 type 3.1).

Single-passage comprehension: one text, a block of linked questions. This is the largest
type in the NSW Reading paper and the bank held NONE of it that a Year 6 candidate could
read — the 634 existing questions of this shape were made from American ACT practice
books written for sixteen- to eighteen-year-olds, and §6.1 rules them out of NSW supply on
that ground. So the format was covered and the supply was zero.

The six subcategories in §3.2 are targets over the whole 292, not over one batch. This
batch carries them in proportion: inference 9, vocabulary in context 7, author's purpose
7, main idea 5, detail 4, cause and effect 4. Detail retrieval is deliberately the
smallest share — it is the easiest type and §3.2 says to keep it low.

Text types follow §3.3 with poetry removed, since poetry is its own type: two narrative,
two informational, one persuasive, one functional.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.rc.paired_common import build  # noqa: E402

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/reading_comprehension/generated"
NN = 1
BOOK = "rc_nsw_single"
CATEGORY = "single_passage"
LABEL = "Single-passage comprehension"
ONE = []            # a single unlabelled text: no extract to declare

# item = (skill, difficulty, confidence, uses, quote_refs, stem, key, distractors, expl)
PASSAGES = [
 {
  "title": "The Cricket Ball",
  "topic": "Narrative",
  "extracts": [("", [
    "The ball went over the fence at about four o'clock, which was later than we usually "
    "played.",
    "It went over in the way that tells you straight away how much trouble you are in: "
    "high, and with a sound behind it.",
    "Mrs Petrakis had lived next door for eleven years and had never once returned a ball.",
    "That was the story, anyway.",
    "None of us had actually asked her.",
    "Dev said we should leave it and buy a new one, and Sam said a new one cost eleven "
    "dollars, and then everybody looked at me, because it was my ball and my hit.",
    "I went round to the front door, which nobody had ever done.",
    "She took a long time to answer and she did not look at all surprised to see me.",
    "The green one or the red one, she said.",
    "There was a box behind the door with eleven or twelve balls in it, some of them "
    "cracked with age.",
    "She had been keeping them, not taking them.",
    "Nobody had ever come.",
    "I took the red one and said thank you, and she said, tell the others they can knock.",
    "We knocked twice more that summer.",
    "The second time she came out and watched from the step, and Dev bowled worse than I "
    "have ever seen him bowl.",
  ])],
  "items": [
    ("inference", "medium", 0.93, ONE, [(0, 2), (0, 4)],
     'The passage says: "{q}" Together these two sentences show that —',
     "what everyone believed about her had never been tested",
     [("Mrs Petrakis had refused the children many times", "contradicts"),
      ("the children had lost only one ball in the whole eleven years", "unsupported"),
      ("Mrs Petrakis disliked children in general", "overreach")],
     "A reputation of eleven years' standing sits beside an admission that nobody ever "
     "checked it. Mrs Petrakis had refused the children many times cannot be right, "
     "because refusing requires being asked."),

    ("inference", "medium", 0.92, ONE, [(0, 10), (0, 11)],
     'The narrator realises: "{q}" This tells the reader that Mrs Petrakis —',
     "had been waiting for somebody to come and ask",
     [("had forgotten the balls were behind her door", "contradicts"),
      ("meant to sell the balls back to the children", "unsupported"),
      ("had collected balls from all over the suburb", "overreach")],
     "Keeping them by the door, sorted enough to offer a choice of colour, is not "
     "forgetting. Had forgotten the balls were behind her door is ruled out by a woman "
     "who answers by asking which one he wants."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 3)],
     'The narrator writes: "{q}" As it is used here, "story" means —',
     "what people said, rather than what was known",
     [("a tale invented purely to entertain children", "wrong_sense"),
      ("a report printed in a local newspaper", "wrong_focus"),
      ("the true account of what actually happened", "contradicts")],
     "The word marks the claim as neighbourhood talk, which the next sentence then "
     "undercuts. The true account of what actually happened is the opposite of a word "
     "used to hold the claim at arm's length."),

    ("author_purpose", "medium", 0.92, ONE, [],
     'Why does the writer follow the claim about Mrs Petrakis with "None of us had '
     'actually asked her"?',
     "to show the reputation rested on nothing",
     [("to explain how the ball came to go over the fence", "wrong_focus"),
      ("to prove that Mrs Petrakis was an unfriendly neighbour", "contradicts"),
      ("to show that the children were frightened of all adults", "overreach")],
     "Placing the admission immediately after the accusation empties it out before the "
     "story has even begun. To prove that Mrs Petrakis was an unfriendly neighbour is the "
     "reading the sentence exists to prevent."),

    ("main_idea", "hard", 0.90, ONE, [],
     'What is the passage mainly about?',
     "an assumption that falls apart once somebody checks it",
     [("the cost of replacing a lost cricket ball", "wrong_focus"),
      ("a neighbour who keeps everything she finds", "contradicts"),
      ("how a group of friends slowly learned to play cricket properly", "unsupported")],
     "The ball is the occasion; what changes is what the children believed about the "
     "woman next door. A neighbour who keeps everything she finds is what the passage "
     "sets up and then disproves."),

    ("cause_effect", "medium", 0.92, ONE, [],
     'What causes the children to knock on her door again later that summer?',
     "she tells them that they may",
     [("they lose several more balls over the fence", "unsupported"),
      ("Dev wants to apologise for bowling so badly", "contradicts"),
      ("the whole box of balls has been offered to them", "wrong_focus")],
     "'Tell the others they can knock' is an invitation, and the knocking follows it. Dev "
     "wants to apologise for bowling so badly reverses the order — the bad bowling happens "
     "on the second visit, not before it."),
  ],
 },
 {
  "title": "How the Ute Got Its Name",
  "topic": "History",
  "extracts": [("", [
    "In 1932 a farmer's wife in Victoria wrote to the Ford motor company with a request.",
    "She wanted a vehicle her family could drive to church on Sunday and take pigs to "
    "market on Monday.",
    "At the time those were two different vehicles, and her family could afford one.",
    "The letter reached a young designer named Lew Bandt.",
    "What he drew was a car at the front and a tray at the back, made in one piece rather "
    "than bolted together.",
    "That single body was the clever part.",
    "A truck with a car's cabin fixed on top will twist and crack on a rough road, "
    "because the two halves pull against each other.",
    "Bandt's design carried the load through the whole frame instead.",
    "Ford released it in 1934 and called it the coupe utility.",
    "Australians called it the ute almost at once, and have called it that ever since.",
    "The design was copied around the world, though most countries kept their trucks and "
    "their cars separate for another twenty years.",
    "Bandt stayed with Ford for the rest of his working life.",
  ])],
  "items": [
    ("detail", "medium", 0.93, ONE, [(0, 1)],
     'The passage states: "{q}" What did she want?',
     "one vehicle that could do two very different jobs",
     [("two vehicles, one for each day of the weekend", "contradicts"),
      ("a vehicle that could carry pigs to market and nothing else", "wrong_focus"),
      ("a vehicle that no other family in Victoria owned", "unsupported")],
     "Church on Sunday and pigs on Monday is one vehicle covering both. Two vehicles, one "
     "for each day of the weekend is exactly the situation she was writing to escape."),

    ("inference", "medium", 0.92, ONE, [(0, 2)],
     'The passage notes: "{q}" This suggests that —',
     "money was the reason the request was unusual",
     [("the family did not know how to drive either vehicle", "unsupported"),
      ("both vehicles were easy for the family to obtain", "contradicts"),
      ("no farming family in Victoria owned a vehicle", "overreach")],
     "Two vehicles existed; what did not exist was a family able to buy both. Both "
     "vehicles were easy for the family to obtain removes the whole reason for writing "
     "the letter."),

    ("inference", "hard", 0.90, ONE, [(0, 6), (0, 7)],
     'The passage explains: "{q}" Bandt\'s design worked better because —',
     "the whole body shared the strain instead of two parts fighting",
     [("the tray at the back was made much lighter", "unsupported"),
      ("the cabin was bolted a great deal more firmly onto the frame", "contradicts"),
      ("the vehicle was never driven on rough roads", "wrong_focus")],
     "One piece has no join to work loose, so the stress runs through the frame. The "
     "cabin was bolted a great deal more firmly onto the frame is the design the passage "
     "says fails."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 5)],
     'The passage says: "{q}" Here, "clever" describes —',
     "an idea that solved the problem simply",
     [("a person who is quick at school work", "wrong_sense"),
      ("a design that was difficult to understand", "contradicts"),
      ("an idea so good that no improvement was ever possible", "overreach")],
     "The word praises the thinking behind the single body, which is the thing that made "
     "it work. A design that was difficult to understand is the opposite of an idea the "
     "passage then explains in one sentence."),

    ("author_purpose", "medium", 0.92, ONE, [],
     'Why does the writer mention that other countries kept trucks and cars separate for '
     'another twenty years?',
     "to show how far ahead the Australian design was",
     [("to explain why the ute was never sold overseas", "contradicts"),
      ("to argue that no other country could have invented it", "overreach"),
      ("to describe how roads were built in other countries", "wrong_focus")],
     "A twenty-year gap between the invention and its copies measures the lead. To "
     "explain why the ute was never sold overseas contradicts the same sentence, which "
     "says the design was copied around the world."),

    ("main_idea", "medium", 0.92, ONE, [],
     'Which of these best sums up the passage?',
     "how one letter led to a new kind of vehicle",
     [("how the Ford company was started in Australia", "unsupported"),
      ("why farmers in Victoria kept pigs in the 1930s", "wrong_focus"),
      ("the career of a designer named Lew Bandt", "half_right")],
     "The request, the design and the name it was given are the three steps the passage "
     "follows. The career of a designer named Lew Bandt covers one sentence at the end, "
     "not the passage."),
  ],
 },
 {
  "title": "In Praise of Being Bored",
  "topic": "Opinion",
  "extracts": [("", [
    "There is one complaint adults have stopped answering properly, and it is the "
    "complaint that there is nothing to do.",
    "Twenty years ago a bored child was handed a problem and left with it.",
    "Now a bored child is handed a screen, and the boredom stops within four seconds.",
    "That sounds like kindness, and I think it is a mistake.",
    "Boredom is uncomfortable, and being uncomfortable is what makes anybody invent "
    "anything.",
    "Every cubby house, every rule for a game that never existed before, every drawing "
    "nobody asked for, began with somebody having nothing to do about it.",
    "A screen removes the discomfort without removing the emptiness, which is the worst "
    "of both.",
    "I am not arguing that screens are bad.",
    "I am arguing that four seconds is not long enough to find out what you would have "
    "done instead.",
    "The next time a child says there is nothing to do, the useful answer is the old one.",
    "Say: I know.",
    "Then say nothing else, and watch what happens in the twenty minutes after that.",
  ])],
  "items": [
    ("author_purpose", "hard", 0.90, ONE, [(0, 7)],
     'The writer says: "{q}" Why include this sentence?',
     "to stop the reader dismissing the argument as anti-screen",
     [("to admit that the whole argument has failed", "contradicts"),
      ("to explain how screens are actually made", "wrong_focus"),
      ("to prove that screens are actually good for children after all", "overreach")],
     "Ruling out the easy objection keeps the reader with the narrower claim that "
     "follows. To admit that the whole argument has failed is contradicted by the next "
     "sentence, which restates the argument more precisely."),

    ("author_purpose", "medium", 0.92, ONE, [(0, 5)],
     'Why does the writer list cubby houses, invented games and unasked-for drawings?',
     "to give evidence that boredom produces things",
     [("to show that children today make none of them", "unsupported"),
      ("to suggest that adults should build them instead", "wrong_focus"),
      ("to prove that drawing is better than screen time", "overreach")],
     "Three ordinary examples make the abstract claim about discomfort concrete. To show "
     "that children today make none of them is not something the sentence says, and the "
     "writer's complaint is about the four seconds, not about children."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 6)],
     'The writer says: "{q}" What does "emptiness" refer to here?',
     "having nothing you actually want to do",
     [("a screen with nothing displayed on it", "literal"),
      ("a room in a house with no furniture", "wrong_sense"),
      ("a feeling of sadness about the future", "wrong_focus")],
     "The emptiness is the state boredom announces, which the screen covers over without "
     "filling. A screen with nothing displayed on it takes a word about the child and "
     "applies it to the device."),

    ("inference", "hard", 0.90, ONE, [(0, 10), (0, 11)],
     'The passage ends: "{q}" What is the writer suggesting an adult should do?',
     "acknowledge the boredom and then leave it alone",
     [("explain to the child why boredom is useful", "contradicts"),
      ("agree with the child and then suggest one activity", "half_right"),
      ("time exactly how long the boredom lasts", "wrong_focus")],
     "Two words and then silence is the whole instruction: agree, and do not rescue. "
     "Explain to the child why boredom is useful is still talking, which is what 'say "
     "nothing else' rules out."),

    ("main_idea", "medium", 0.92, ONE, [],
     'What is the writer\'s main argument?',
     "boredom is worth sitting through because of what follows it",
     [("children should be given screens far less often", "half_right"),
      ("adults today are a great deal less patient than they used to be", "wrong_focus"),
      ("boredom is a pleasant feeling once you get used to it", "contradicts")],
     "The value is placed in what boredom produces, not in boredom itself. Boredom is a "
     "pleasant feeling once you get used to it contradicts a writer who calls it "
     "uncomfortable and keeps it uncomfortable."),

    ("cause_effect", "medium", 0.92, ONE, [],
     'According to the writer, what is the effect of handing a bored child a screen?',
     "the discomfort ends before anything can come of it",
     [("the child becomes bored again within four seconds", "contradicts"),
      ("the child stops inventing games for the rest of childhood", "overreach"),
      ("the child learns to use the screen more skilfully", "unsupported")],
     "Four seconds is offered as too short a time for the useful part to begin. The child "
     "becomes bored again within four seconds reverses the sentence, in which four "
     "seconds is how quickly the boredom stops."),
  ],
 },
 {
  "title": "Looking After the Class Chickens",
  "topic": "Functional",
  "extracts": [("", [
    "Two students are rostered each week, and the roster is on the inside of the coop "
    "door.",
    "Morning jobs are done before the bell, not at recess.",
    "Refill the water first, because it is the job most often forgotten and the one that "
    "matters most in summer.",
    "Tip the old water out onto the garden rather than down the drain.",
    "Scatter one scoop of pellets, not two: extra food is left uneaten and brings rats.",
    "Kitchen scraps go in the green bucket, but never onion, avocado or anything salty.",
    "Collect the eggs every morning, even if you think somebody else already has.",
    "An egg left in the nest for two days will usually be broken by the third.",
    "Write the number of eggs on the chart, including a zero.",
    "A zero is information; a blank square is a puzzle for whoever comes next.",
    "If a chicken is sitting apart from the others and has not moved by lunchtime, tell a "
    "teacher.",
    "Do not try to pick her up.",
    "On Friday, rake the run and put the old straw on the compost, not in the bin.",
  ])],
  "items": [
    ("detail", "medium", 0.93, ONE, [(0, 4)],
     'The instructions say: "{q}" Why is one scoop specified rather than two?',
     "uneaten food attracts rats",
     [("two scoops would cost the school twice as much", "unsupported"),
      ("the chickens will not eat pellets at all", "contradicts"),
      ("the pellets are stored in a scoop-sized container", "wrong_focus")],
     "The reason is given in the same sentence as the rule. Two scoops would cost the "
     "school twice as much may be true of any food, but it is not the reason the "
     "instructions give."),

    ("inference", "medium", 0.92, ONE, [(0, 6), (0, 7)],
     'The instructions say: "{q}" Why does it matter that eggs are collected daily even '
     'if you think somebody has already been?',
     "an uncollected egg will not survive being left",
     [("the chickens will stop laying if eggs are left", "unsupported"),
      ("two students might collect the same egg twice", "contradicts"),
      ("the chickens will never lay in that nest again", "overreach")],
     "The following sentence gives the consequence directly: two days in the nest and it "
     "breaks. Two students might collect the same egg twice is not possible, and would "
     "not be a problem if it were."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 9)],
     'The instructions say: "{q}" What does the writer mean by calling a zero '
     '"information"?',
     "it tells the next person something definite",
     [("it means the chart has been filled in wrongly", "contradicts"),
      ("it is a number rather than a letter", "literal"),
      ("it shows the chickens are unwell that week", "unsupported")],
     "A recorded zero settles the question; a blank leaves the next student guessing. It "
     "is a number rather than a letter reads the word as a fact about zero itself rather "
     "than about what writing it down achieves."),

    ("author_purpose", "medium", 0.92, ONE, [(0, 11)],
     'The instructions say: "{q}" This rule is included mainly to —',
     "keep students from handling a possibly sick bird",
     [("stop students from playing with the chickens at recess", "wrong_focus"),
      ("save time during the morning jobs", "unsupported"),
      ("make sure the teacher does the job instead", "half_right")],
     "It follows immediately from the sign of a chicken that may be unwell, and pairs "
     "with telling a teacher. Stop students from playing with the chickens would make it "
     "a general rule, but it applies only in that one situation."),

    ("main_idea", "medium", 0.92, ONE, [],
     'What do these instructions mainly try to do?',
     "give each job a reason as well as a rule",
     [("list the jobs in the order they take the longest", "unsupported"),
      ("explain how to build and repair a chicken coop", "wrong_focus"),
      ("warn students that chickens are difficult to keep", "contradicts")],
     "Almost every instruction is followed by why it matters — rats, breakage, the next "
     "student. Warn students that chickens are difficult to keep is not the tone of a "
     "list that assumes two students can manage it before the bell."),

    ("cause_effect", "medium", 0.92, ONE, [(0, 3)],
     'The instructions say: "{q}" What is the likely reason for this?',
     "the water is useful to the garden rather than wasted",
     [("the drain would be blocked by the old water", "unsupported"),
      ("the garden needs to be watered every single morning without fail", "overreach"),
      ("the coop has no drain anywhere near it at all", "contradicts")],
     "Sending it to the garden puts it to a second use instead of losing it. The coop has "
     "no drain anywhere near it at all cannot be right, because the instruction only "
     "makes sense if there is a drain to avoid."),
  ],
 },
 {
  "title": "The Substitute",
  "topic": "Narrative",
  "extracts": [("", [
    "Mr Aziz was away for six weeks and we had four different teachers in that time.",
    "The first three did the same thing.",
    "They stood at the front, said their name, and told us what they would not be putting "
    "up with.",
    "By the second lesson we knew exactly how far each one could be pushed, which was not "
    "very far, and we pushed it.",
    "The fourth was a woman called Ms Delaney who wrote nothing on the board at all.",
    "She sat on a desk in the middle of the room, which teachers do not do, and asked what "
    "we had been reading.",
    "Nobody answered, because it was not the kind of question we were expecting.",
    "She waited.",
    "The waiting went on long enough to become uncomfortable and then long enough to "
    "become interesting.",
    "In the end Priya said the name of a book, quietly, as though it might be the wrong "
    "answer.",
    "Ms Delaney said she had not read it and asked whether she should.",
    "That was the whole trick, and I did not understand it for another two years.",
    "She had not tried to control the room.",
    "She had made the room curious about her.",
  ])],
  "items": [
    ("inference", "medium", 0.93, ONE, [(0, 2), (0, 3)],
     'The narrator says of the first three teachers: "{q}" What went wrong for them?',
     "they set limits before they had any authority",
     [("they had not been told which class they were teaching", "unsupported"),
      ("they were too friendly with the students at first", "contradicts"),
      ("they spent far too long writing on the board", "wrong_focus")],
     "Announcing what will not be put up with invites the class to find the edge of it, "
     "which is what happens by lesson two. They were too friendly with the students at "
     "first is the opposite of teachers who open with a list of prohibitions."),

    ("inference", "hard", 0.90, ONE, [(0, 8)],
     'The narrator says: "{q}" What does this suggest about the silence?',
     "it stopped being awkward and started being a question",
     [("the class had decided not to speak to her at all", "contradicts"),
      ("Ms Delaney had forgotten what she meant to ask", "unsupported"),
      ("no student in the room would ever have spoken", "overreach")],
     "The sentence marks a turn: the same silence changes meaning as it goes on. The "
     "class had decided not to speak to her at all is ruled out by Priya answering."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 11)],
     'The narrator writes: "{q}" Here, "trick" means —',
     "the thing she did that actually worked",
     [("a joke played on the class for amusement", "wrong_sense"),
      ("the only teaching method that ever works", "overreach"),
      ("a dishonest way of getting her own way", "wrong_focus")],
     "The word names her method, which the last two sentences then explain. A dishonest "
     "way of getting her own way does not fit a narrator who admires it for two years "
     "afterwards."),

    ("author_purpose", "medium", 0.92, ONE, [(0, 5)],
     'Why does the narrator mention that Ms Delaney sat on a desk, "which teachers do not '
     'do"?',
     "to mark her as different before she has said much",
     [("to criticise her for behaving unprofessionally", "contradicts"),
      ("to explain that there were no chairs in the room", "unsupported"),
      ("to describe the layout of the classroom furniture", "wrong_focus")],
     "The aside tells the reader a rule is being broken, which is the first sign that "
     "this teacher will not follow the pattern. To criticise her for behaving "
     "unprofessionally runs against a passage that ends in admiration."),

    ("main_idea", "hard", 0.90, ONE, [],
     'The passage as a whole is mainly about —',
     "two opposite ways of winning a room, and which one lasts",
     [("a class that behaved badly for six weeks in a row without stopping", "contradicts"),
      ("a student who was too shy to answer a question", "wrong_focus"),
      ("the reason Mr Aziz was away from school so long", "unsupported")],
     "Three teachers try control and fail; one tries curiosity and succeeds, and the "
     "narrator says so outright at the end. A class that behaved badly for six weeks in a "
     "row without stopping ignores the fourth teacher, who is the point of the passage."),

    ("detail", "medium", 0.92, ONE, [],
     'What does Ms Delaney do after Priya names a book?',
     "she admits she has not read it and asks about it",
     [("she writes the title of the book on the board", "contradicts"),
      ("she says she has read it and enjoyed it", "half_right"),
      ("she asks the rest of the class the same question", "unsupported")],
     "Her reply turns the exchange around, which is what makes the room curious about "
     "her. She writes the title of the book on the board is ruled out by a teacher who "
     "wrote nothing on the board at all."),
  ],
 },
 {
  "title": "The Animal Nobody Believed In",
  "topic": "Science",
  "extracts": [("", [
    "In 1799 a parcel arrived in London containing the skin of an animal from New South "
    "Wales.",
    "It had the beak of a duck, the tail of a beaver and the feet of an otter.",
    "The scientist who opened it, George Shaw, took a pair of scissors to the beak to look "
    "for stitches.",
    "He was not being foolish.",
    "Sailors returning from the east had been selling fake creatures for years, sewn "
    "together from parts of real ones.",
    "Shaw found no stitches, wrote up the animal, and was not entirely believed for "
    "another twenty years.",
    "The platypus went on to be difficult in almost every way an animal can be.",
    "It is a mammal, but it lays eggs, which no textbook allowed for.",
    "The male carries venom in a spur on his back foot, which almost no mammal does.",
    "It hunts with its eyes and ears shut, finding prey by detecting the faint electricity "
    "of a moving muscle.",
    "Every one of those facts arrived years apart, and each one was doubted when it came.",
    "The scissor marks are still visible on the original skin in London.",
    "They are a useful reminder that the first response to something genuinely new is "
    "usually to check whether somebody is lying.",
  ])],
  "items": [
    ("inference", "medium", 0.93, ONE, [(0, 3), (0, 4)],
     'The passage says: "{q}" Why does the writer defend George Shaw?',
     "fake animals were a real problem at the time",
     [("Shaw was the most respected scientist in London", "unsupported"),
      ("the platypus skin turned out to be a fake after all", "contradicts"),
      ("cutting the beak was the only way to study it", "overreach")],
     "The sentence about sailors selling sewn-together creatures supplies the reason his "
     "suspicion was reasonable. The platypus skin turned out to be a fake after all is "
     "the opposite of what he found."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 6)],
     'The passage says: "{q}" Here, "difficult" means —',
     "hard for science to fit into its categories",
     [("badly behaved when handled by people", "wrong_sense"),
      ("unpleasant to look at or to touch", "wrong_focus"),
      ("impossible for science to classify at all", "overreach")],
     "What follows is a list of rules the animal breaks, not of trouble it causes. Badly "
     "behaved when handled by people takes the everyday sense of the word and misses what "
     "the next sentences are about."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 7)],
     'The passage says: "{q}" The phrase "no textbook allowed for" means —',
     "the science of the day had no room for it",
     [("no textbook of the period had yet been written", "contradicts"),
      ("textbooks were not permitted to discuss mammals", "unsupported"),
      ("every textbook of the time had to be thrown away", "overreach")],
     "A mammal that lays eggs contradicted the definition of a mammal as it then stood. "
     "No textbook of the period had yet been written cannot be right in a passage about "
     "what the textbooks said."),

    ("author_purpose", "hard", 0.90, ONE, [(0, 11), (0, 12)],
     'The passage ends: "{q}" Why does the writer finish here?',
     "to turn one detail into a point about how discovery works",
     [("to suggest that the original skin should be repaired", "unsupported"),
      ("to prove that George Shaw was wrong to use scissors", "contradicts"),
      ("to describe how museums look after their oldest specimens", "wrong_focus")],
     "The scissor marks become evidence of a habit of mind rather than of one man's "
     "mistake. To prove that George Shaw was wrong to use scissors reverses a passage "
     "that has already defended him."),

    ("cause_effect", "medium", 0.92, ONE, [(0, 10)],
     'The passage says: "{q}" What effect did the timing have?',
     "each new fact met the same doubt as the one before",
     [("the facts were all confirmed at the same time", "contradicts"),
      ("scientists lost interest in the platypus entirely", "unsupported"),
      ("the animal itself changed between the discoveries", "wrong_focus")],
     "Arriving years apart meant no single discovery ever settled the animal's "
     "strangeness. The facts were all confirmed at the same time is what the sentence "
     "denies."),

    ("cause_effect", "medium", 0.92, ONE, [(0, 8)],
     'The passage notes: "{q}" Why is this mentioned?',
     "it is one more way the animal breaks a rule",
     [("it explains why the first skin was sent to London", "unsupported"),
      ("it warns readers not to handle a live platypus", "wrong_focus"),
      ("it proves that the platypus is not really a mammal", "contradicts")],
     "It sits in a list of properties that no mammal was supposed to have. It proves that "
     "the platypus is not really a mammal is the opposite of the passage's point, which "
     "is that the category had to stretch."),
  ],
 },
]


if __name__ == "__main__":
    GEN.mkdir(parents=True, exist_ok=True)
    qs = build(PASSAGES, BOOK, NN, CATEGORY, LABEL)
    path = GEN / f"{BOOK}_p{NN}.json"
    path.write_text(json.dumps(qs, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(qs)} questions across {len(PASSAGES)} passages -> {path}")
