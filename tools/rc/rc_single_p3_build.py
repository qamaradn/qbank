#!/usr/bin/env python3
"""Builds rc_nsw_single_p3.json — 6 passages x 6 items = 36 answer slots (§3.1 type 3.1).

Third single-passage batch: a school concert, why some trees shed bark, an argument for
noisy libraries, an excursion note, a first paid job, and the Nullarbor.

Written against the lessons of p1 and p2. Every quotation is introduced with a colon after
a verb of saying, because the doubled-subject stem (`The passage says the spread "A spread
that had failed..."`) got past a full read seven times in one batch and is now a check.
Distractors are written at the keys' length from the start; both earlier batches needed a
rescue pass otherwise.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.rc.paired_common import build  # noqa: E402

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/reading_comprehension/generated"
NN = 3
BOOK = "rc_nsw_single"
CATEGORY = "single_passage"
LABEL = "Single-passage comprehension"
ONE = []

PASSAGES = [
 {
  "title": "The Last Row",
  "topic": "Narrative",
  "extracts": [("", [
    "In the choir I am back row, third from the end, which is where they put the people "
    "who can be trusted not to be heard.",
    "I have known this since Year 4 and I do not mind it as much as you would think.",
    "The back row sees everything.",
    "You can watch Mr Nguyen's left hand, which is the hand that means quieter, and you "
    "can watch the front row not watching it.",
    "At the winter concert the piano came in four bars early.",
    "I saw Mr Nguyen's face do something very small and very fast, and then his left hand "
    "came up and held, and we all stopped where we were.",
    "For about two seconds there was nothing at all.",
    "Then he counted us back in, from the top, and the audience clapped as though it had "
    "been arranged that way.",
    "Afterwards my sister said it was the best bit and asked whether we had practised it.",
    "We had not practised it.",
    "What we had practised, for eleven weeks, was watching his left hand.",
  ])],
  "items": [
    ("inference", "medium", 0.93, ONE, [(0, 0)],
     'The narrator says: "{q}" How does he feel about where he stands?',
     "he accepts it and has found something in it",
     [("he was put there by a teacher who disliked him", "unsupported"),
      ("he is deeply upset about being placed at the back", "contradicts"),
      ("he expects to be moved to the front row very soon", "overreach")],
     "He states the reason plainly and then says he does not mind it, before listing what "
     "the position lets him see. He is deeply upset about being placed at the back is "
     "ruled out by the very next sentence."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 2)],
     'The narrator writes: "{q}" What does he mean?',
     "the back row has the best view of what is happening",
     [("the back row is higher off the ground than the others", "unsupported"),
      ("the back row is watched closely by the whole audience", "contradicts"),
      ("everybody in the choir is watching the conductor closely", "half_right")],
     "The next sentence lists what he can watch from there, including the front row not "
     "watching. Everybody in the choir is watching the conductor closely is exactly what "
     "the passage denies: the front row is not watching at all."),

    ("cause_effect", "medium", 0.92, ONE, [(0, 5)],
     'The narrator describes: "{q}" What stopped the performance falling apart?',
     "the choir was watching the conductor's hand",
     [("the pianist realised the mistake and stopped playing", "unsupported"),
      ("the audience began clapping before the choir could sing", "wrong_focus"),
      ("Mr Nguyen said something out loud to the front row", "contradicts")],
     "The raised left hand is a signal, and the choir had spent eleven weeks learning to "
     "read it. Mr Nguyen said something out loud to the front row is contradicted by a "
     "passage in which he uses only his face and his hand."),

    ("author_purpose", "medium", 0.92, ONE, [],
     'Why does the writer include the sister\'s question about practising?',
     "to set up the point the last two lines make",
     [("to show that the sister does not understand music", "overreach"),
      ("to explain why the concert was held in winter", "wrong_focus"),
      ("to prove that the choir had rehearsed the mistake", "contradicts")],
     "Her question is answered twice: no, and then yes in a way she did not mean. To "
     "prove that the choir had rehearsed the mistake is exactly what the next sentence "
     "denies."),

    ("main_idea", "hard", 0.90, ONE, [(0, 10)],
     'The passage ends: "{q}" What is the point of the whole passage?',
     "preparation is not the same as rehearsing the event",
     [("the back row of a choir sings better than the front", "unsupported"),
      ("a concert can be ruined by a single early entry", "contradicts"),
      ("practising for eleven weeks is longer than necessary", "wrong_focus")],
     "What saved the concert was a habit built over weeks, not a plan for that moment. A "
     "concert can be ruined by a single early entry is the opposite of an evening the "
     "audience thought was arranged."),

    ("detail", "medium", 0.92, ONE, [],
     'According to the passage, what does Mr Nguyen\'s left hand mean?',
     "sing more quietly",
     [("come in earlier than written", "contradicts"),
      ("watch the front row closely", "wrong_focus"),
      ("stop singing altogether now", "half_right")],
     "The narrator names it as the hand that means quieter. Stop singing altogether now "
     "is what the hand achieves once it is held up, but it is not what the passage says "
     "the hand means."),
  ],
 },
 {
  "title": "Why Some Trees Drop Their Bark",
  "topic": "Science",
  "extracts": [("", [
    "Walk through dry forest in summer and the ground is covered in long strips of bark.",
    "Most trees in the world do not do this.",
    "A pine or an oak grows bark outward and keeps it, so the trunk thickens year by year "
    "in rings you can count.",
    "Many eucalypts shed instead.",
    "The tree grows a new layer underneath and lets the old one split, curl and fall.",
    "One reason is that shed bark takes its passengers with it.",
    "Insects, fungus and moss that settle on the outside of a smooth-barked eucalypt find "
    "themselves on the ground within a season.",
    "There is a second reason, and it is harder to like.",
    "A pile of dry bark at the base of a tree is fuel, and eucalypts are built for fire in "
    "a way almost no other tree is.",
    "Buds sit protected under the bark along the whole trunk, ready to sprout after the "
    "flames pass.",
    "A tree that drops fuel around itself and then survives the fire has removed its "
    "competition without moving.",
    "That is not a plan, because trees do not make plans.",
    "It is simply what happens to work, repeated for long enough that the forest is now "
    "full of trees that do it.",
  ])],
  "items": [
    ("detail", "medium", 0.93, ONE, [(0, 2)],
     'The passage states: "{q}" How is a pine different from many eucalypts?',
     "it keeps its bark instead of dropping it",
     [("it grows a new layer of bark underneath each year", "wrong_focus"),
      ("it sheds its bark in long strips every summer", "contradicts"),
      ("it has no bark on the outside of the trunk at all", "overreach")],
     "The passage sets keeping against shedding as the difference. It sheds its bark in "
     "long strips every summer describes the eucalypts, not the pine."),

    ("inference", "medium", 0.92, ONE, [(0, 6)],
     'The passage explains: "{q}" Why is this an advantage to the tree?',
     "it removes pests without the tree doing anything active",
     [("it provides food for the insects that live nearby", "contradicts"),
      ("it makes the trunk smoother for climbing animals", "wrong_focus"),
      ("it allows the tree to grow taller than its neighbours", "unsupported")],
     "Anything that settles on the outside goes down with the bark it settled on. It "
     "provides food for the insects that live nearby reverses a sentence about getting "
     "rid of them."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 5)],
     'The passage says: "{q}" What are the "passengers"?',
     "the insects, fungus and moss riding on the bark",
     [("the seeds the tree drops at the end of summer", "unsupported"),
      ("the birds that nest in the branches of the tree", "wrong_focus"),
      ("people who walk through the forest in summer", "literal")],
     "The next sentence names them, which is what makes the word a comparison rather "
     "than a puzzle. People who walk through the forest in summer takes a word about "
     "hitching a ride and gives it to the reader."),

    ("inference", "hard", 0.90, ONE, [(0, 10)],
     'The passage says: "{q}" What is being described here?',
     "an advantage that comes from surviving what others do not",
     [("a tree that deliberately sets fire to the trees around it", "literal"),
      ("a tree that grows faster than the trees near it", "wrong_focus"),
      ("a forest in which no tree survives a fire at all", "contradicts")],
     "The fire removes the neighbours and the eucalypt regrows from protected buds. A "
     "tree that deliberately sets fire to its rivals reads intention into something the "
     "passage explicitly says is not a plan."),

    ("author_purpose", "medium", 0.92, ONE, [(0, 11)],
     'Why does the writer add: "{q}"?',
     "to stop the reader thinking the tree intends any of it",
     [("to argue that trees are more intelligent than we think", "contradicts"),
      ("to explain how scientists study the growth of forests", "wrong_focus"),
      ("to suggest the whole explanation is probably wrong", "overreach")],
     "The sentence pulls back from the language of strategy the paragraph has been using. "
     "To argue that trees are more intelligent than we think is the opposite of the "
     "correction being made."),

    ("main_idea", "medium", 0.92, ONE, [],
     'What does this passage set out to explain?',
     "why shedding bark turns out to suit these trees",
     [("how to tell a eucalypt from a pine or an oak", "half_right"),
      ("how forest fires are started in dry country", "wrong_focus"),
      ("why bark should be cleared away from trees", "unsupported")],
     "Two reasons are given, and the last lines explain how a habit like that comes "
     "about. How to tell a eucalypt from a pine or an oak is the opening comparison, not "
     "the passage's business."),
  ],
 },
 {
  "title": "Let the Library Be Noisy",
  "topic": "Opinion",
  "extracts": [("", [
    "The rule that a library must be silent is younger than most people assume, and it was "
    "never really about reading.",
    "It came from reading rooms where dozens of adults sat at long shared tables, and one "
    "conversation genuinely spoiled the room for everybody.",
    "A modern school library has beanbags, group tables, a printer and a borrowing desk.",
    "It is not that room, and it has not been that room for forty years.",
    "Silence in a school library does one useful thing: it protects the person who reads "
    "best when nothing is happening.",
    "It also does one harmful thing, which is rarely counted.",
    "It teaches every student who reads by talking — who needs to say a sentence out loud "
    "before it means anything — that the library is not for them.",
    "Those students stop going, and we record that as a preference.",
    "I am not proposing that libraries become loud.",
    "I am proposing that they become zoned, the way a good classroom already is: a quiet "
    "end that is genuinely quiet, and a working end where talking is the point.",
    "Every library I know that has done this reports the same thing, which is that "
    "borrowing went up at both ends.",
  ])],
  "items": [
    ("author_purpose", "medium", 0.93, ONE, [(0, 8)],
     'Why does the writer break off to say: "{q}"?',
     "to prevent the reader mistaking the proposal for its extreme",
     [("to admit that the argument has no real support", "overreach"),
      ("to explain how loud a library normally becomes", "wrong_focus"),
      ("to agree that silence is the best rule for a library after all", "contradicts")],
     "Ruling out the extreme protects the actual proposal, which the next sentence gives. "
     "To agree that silence is the best rule after all reverses the whole piece."),

    ("inference", "medium", 0.92, ONE, [(0, 7)],
     'The writer says: "{q}" What is being criticised here?',
     "treating an effect of the rule as a free choice",
     [("students who decide not to use the library", "wrong_focus"),
      ("librarians who fail to keep proper records", "unsupported"),
      ("schools that have closed their libraries entirely", "overreach")],
     "The complaint is about the recording, not the students: a rule pushed them out and "
     "the record calls it taste. Students who decide not to use the library is the "
     "reading the sentence is written to reject."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 9)],
     'The writer says: "{q}" What does "zoned" mean here?',
     "divided into areas with different rules",
     [("marked out with lines painted on the floor", "literal"),
      ("closed to students during certain periods", "wrong_sense"),
      ("rebuilt as several separate small rooms", "overreach")],
     "The comparison with a classroom and the two ends described make the meaning plain. "
     "Rebuilt as several separate small rooms goes further than a proposal about rules "
     "rather than walls."),

    ("cause_effect", "medium", 0.92, ONE, [(0, 1)],
     'The writer explains: "{q}" Why does this matter to the argument?',
     "the rule was made for a room schools no longer have",
     [("adults are noisier in libraries than students are", "unsupported"),
      ("long shared tables are the best way to study", "contradicts"),
      ("the reading rooms held only a handful of people", "wrong_focus")],
     "If the reason for the rule has gone, the rule needs its own defence. Long shared "
     "tables are the best way to study is not a claim the passage makes anywhere."),

    ("main_idea", "hard", 0.90, ONE, [],
     'Which of these best states the writer\'s argument?',
     "the rule should be replaced by zones, not abolished",
     [("libraries should be as loud as any other classroom", "overreach"),
      ("silence in libraries has never helped any student", "contradicts"),
      ("school libraries should be closed and the money spent elsewhere", "unsupported")],
     "The writer names one useful thing silence does, then proposes zones rather than "
     "removal. Silence in libraries has never helped any student is contradicted by the "
     "sentence granting exactly that."),

    ("detail", "medium", 0.92, ONE, [(0, 10)],
     'What does the writer report about libraries that have already tried this?',
     "borrowing rose at both the quiet and working ends",
     [("borrowing rose only in the quiet end of the room", "contradicts"),
      ("the quiet end had to be closed again within a year", "unsupported"),
      ("borrowing rose so far that the shelves emptied", "overreach")],
     "The last sentence gives the result at both ends. Borrowing rose only in the quiet "
     "end of the room drops the half of the finding that makes the point."),
  ],
 },
 {
  "title": "The Excursion Note",
  "topic": "Functional",
  "extracts": [("", [
    "Year 6 leaves at 8.15 and will not wait, because the bus is booked by the hour.",
    "Bring a hat you are prepared to wear, not a hat you are prepared to carry.",
    "There is no shade at the quarry site and no shop within twenty minutes.",
    "Bring two litres of water per person.",
    "One litre is what students bring and two litres is what they drink, every year, "
    "without exception.",
    "Lunch must be entirely rubbish-free: nothing that leaves a wrapper, because the site "
    "is a working conservation area and we carry out what we carry in.",
    "Wear closed shoes with a back strap.",
    "The path is loose gravel on a slope and thongs will end your day at the bus.",
    "Do not bring a phone as your camera.",
    "Two students per group will be given a school camera, and phones have a way of going "
    "over the edge at exactly the wrong moment.",
    "If it rains before 7am the excursion is postponed and you will get a message; if it "
    "rains after 7am we are going anyway, so bring a jacket.",
  ])],
  "items": [
    ("author_purpose", "medium", 0.93, ONE, [(0, 4)],
     'The note says: "{q}" Why is this sentence included?',
     "to explain why the amount asked for is doubled",
     [("to criticise students for ignoring the note", "overreach"),
      ("to describe how hot the quarry site becomes", "wrong_focus"),
      ("to suggest that one litre is usually more than enough", "contradicts")],
     "The gap between what is brought and what is drunk is the reason for the two-litre "
     "rule. To suggest that one litre is usually enough is the opposite of what the "
     "sentence reports."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 1)],
     'The note says: "{q}" What is the point of the distinction?',
     "the hat has to be one you will actually keep on",
     [("the hat should be small enough to fit in a bag", "contradicts"),
      ("students should bring two hats to the excursion", "unsupported"),
      ("the hat matters less than the water does", "wrong_focus")],
     "Wearing against carrying is the difference between a hat that works and one that "
     "does not. The hat should be small enough to fit in a bag describes a hat being "
     "carried, which is what the note rules out."),

    ("cause_effect", "medium", 0.92, ONE, [(0, 5)],
     'According to the note, why must lunch leave no rubbish?',
     "the site is a conservation area and waste goes out with the group",
     [("the bus company charges extra for any rubbish left behind on board", "unsupported"),
      ("rubbish left there would be cleared by the rangers", "contradicts"),
      ("wrappers blow away and are difficult to chase", "wrong_focus")],
     "The reason is given in the same sentence as the rule. Rubbish left there would be "
     "cleared by the rangers is the opposite of a site where the group carries out what "
     "it carries in."),

    ("inference", "medium", 0.92, ONE, [(0, 7)],
     'The note says: "{q}" What is the writer warning about?',
     "unsuitable shoes will stop a student joining in",
     [("the path is too dangerous for students to walk", "contradicts"),
      ("thongs are more expensive to replace than shoes", "wrong_focus"),
      ("students who wear thongs will be sent home early", "overreach")],
     "Ending your day at the bus means sitting out the excursion, not leaving it. "
     "Students who wear thongs will be sent home early goes further than waiting at the "
     "bus."),

    ("detail", "medium", 0.92, ONE, [(0, 10)],
     'The note explains: "{q}" What happens if it rains at 6.30am?',
     "the excursion is postponed and families are sent a message",
     [("the excursion goes ahead and students bring a jacket", "contradicts"),
      ("students wait at school until the rain has stopped", "unsupported"),
      ("the excursion is cancelled and will not be held again", "overreach")],
     "Half past six is before seven, which is the line the note draws. The excursion goes "
     "ahead and students bring a jacket is the rule for rain that falls after seven."),

    ("main_idea", "hard", 0.90, ONE, [],
     'What makes this note different from a plain list of instructions?',
     "nearly every instruction carries the reason behind it",
     [("it is written for the parents rather than for the students", "unsupported"),
      ("it describes the quarry site in careful detail", "wrong_focus"),
      ("it warns that the excursion may be cancelled", "half_right")],
     "The hat, the water, the rubbish, the shoes and the cameras each come with why. It "
     "warns that the excursion may be cancelled covers one sentence out of eleven."),
  ],
 },
 {
  "title": "The Job",
  "topic": "Narrative",
  "extracts": [("", [
    "The job was Saturday mornings at the fruit shop and it paid eleven dollars an hour, "
    "which at thirteen felt like being handed the keys to something.",
    "What I actually did for the first month was carry boxes from the cool room to the "
    "front and break them down flat.",
    "Nobody explained anything.",
    "I asked Sal, who owned it, whether I was doing it right, and she said if I was doing "
    "it wrong she would have told me, which I later understood was the whole management "
    "system.",
    "In the second month she let me refill the display.",
    "There is a way to stack apples so the pile does not slide, and a way that looks the "
    "same until somebody takes one from the middle.",
    "I learned that the hard way, twice, in front of customers.",
    "By winter I was taking deliveries and checking them off, which meant telling a grown "
    "man in a truck that he was four crates short.",
    "The first time I did that my voice did something embarrassing halfway through the "
    "sentence.",
    "He counted them again and I was right.",
    "I have had four jobs since and none of them taught me as much as being wrong about "
    "apples in public.",
  ])],
  "items": [
    ("inference", "medium", 0.93, ONE, [(0, 3)],
     'The narrator says: "{q}" What does this tell us about how Sal ran the shop?',
     "she said something only when something was wrong",
     [("she gave detailed instructions for every task", "contradicts"),
      ("she rarely spoke to any of her staff at all", "overreach"),
      ("she preferred to do the difficult jobs herself", "unsupported")],
     "Silence was the signal that things were going fine, which is why he had to work it "
     "out. She gave detailed instructions for every task is the opposite of a shop where "
     "nobody explained anything."),

    ("inference", "medium", 0.92, ONE, [(0, 6)],
     'The narrator says: "{q}" What happened?',
     "the apple display collapsed while customers watched",
     [("he was told off by Sal in front of the customers", "unsupported"),
      ("he dropped a box of apples on the way to the front", "wrong_focus"),
      ("he learned the correct method on his very first try", "contradicts")],
     "The sentence before describes a stack that slides when one is taken from the "
     "middle, and 'twice' says he did it twice. He learned the correct method on his very "
     "first try contradicts 'the hard way'."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 0)],
     'The narrator writes: "{q}" What does the comparison suggest about the pay?',
     "it felt like a much bigger step than the amount",
     [("eleven dollars was a very large sum of money", "overreach"),
      ("he was given a set of keys to the fruit shop", "literal"),
      ("the money was more than he had expected to earn", "unsupported")],
     "Keys stand for being trusted, which is what the amount meant to a thirteen-year-old "
     "rather than what it bought. He was given a set of keys to the fruit shop takes the "
     "comparison for an event."),

    ("author_purpose", "medium", 0.92, ONE, [(0, 8)],
     'Why does the narrator mention: "{q}"?',
     "to show how difficult the moment was for him",
     [("to suggest the delivery driver was frightening", "unsupported"),
      ("to explain why the count came out wrong at first", "contradicts"),
      ("to describe how noisy the loading area could be", "wrong_focus")],
     "A voice going wrong mid-sentence is the sign of a thirteen-year-old doing something "
     "well beyond him. To explain why the count came out wrong at first cannot be right, "
     "since the count was correct."),

    ("main_idea", "hard", 0.90, ONE, [(0, 10)],
     'The passage ends: "{q}" What does the narrator value about the job?',
     "being visibly wrong and having to correct it",
     [("the money he was able to earn at thirteen", "wrong_focus"),
      ("the fact that Sal never once criticised him", "half_right"),
      ("learning that he was never suited to the work", "contradicts")],
     "The two things he names are the apples and the truck, both of them public "
     "mistakes and public corrections. The fact that Sal never once criticised him is "
     "true of the shop, but it is not what he says taught him."),

    ("cause_effect", "medium", 0.92, ONE, [(0, 7)],
     'What made checking deliveries difficult for the narrator?',
     "he had to contradict an adult who was a stranger",
     [("the crates were too heavy for him to lift", "unsupported"),
      ("he had been shown entirely the wrong way to count them", "contradicts"),
      ("the truck arrived before the shop had opened", "wrong_focus")],
     "A thirteen-year-old telling a grown man he is four crates short is the difficulty "
     "the passage sets up. The crates were too heavy for him to lift belongs to the "
     "box-carrying month, not the counting."),
  ],
 },
 {
  "title": "The Plain With No Trees",
  "topic": "Geography",
  "extracts": [("", [
    "The Nullarbor is named for what is missing.",
    "The word is not from any Aboriginal language but from Latin: nullus arbor, no tree.",
    "It is about twelve hundred kilometres across and the road over it includes a straight "
    "stretch of a hundred and forty-six kilometres without a single bend.",
    "Twenty-five million years ago it was a shallow sea.",
    "What you drive across is the floor of that sea, lifted up and dried out, which is why "
    "the rock underneath is limestone and why it is full of caves.",
    "Limestone dissolves in slightly acid water, and rain is slightly acid.",
    "Over millions of years the water went down instead of running along, which is the "
    "reason there are almost no rivers on the surface and a great many hollows underneath.",
    "That is also why there are no trees.",
    "A tree needs water it can reach, and on the Nullarbor the water is either gone or a "
    "long way down.",
    "Saltbush and bluebush manage on almost nothing and cover the whole plain.",
    "So the name is accurate, but it describes a consequence rather than a fact about the "
    "soil.",
  ])],
  "items": [
    ("detail", "medium", 0.93, ONE, [(0, 1)],
     'The passage states: "{q}" Where does the name come from?',
     "Latin words meaning no tree",
     [("an Aboriginal word for open country", "contradicts"),
      ("the name of the sea that once covered it", "unsupported"),
      ("a description of the saltbush growing there", "wrong_focus")],
     "The sentence names the language and the two words. An Aboriginal word for open "
     "country is precisely what the passage rules out."),

    ("cause_effect", "hard", 0.90, ONE, [(0, 6)],
     'The passage explains: "{q}" What is the effect of the water going downward?',
     "the surface has few rivers and the rock is full of caves",
     [("the surface floods badly whenever it rains", "contradicts"),
      ("the limestone underneath has been washed away completely", "overreach"),
      ("the plain is covered in shallow salt lakes", "unsupported")],
     "Water travelling down rather than along makes hollows below and leaves nothing on "
     "top. The surface floods badly whenever it rains is the opposite of water that "
     "disappears into the rock."),

    ("inference", "medium", 0.92, ONE, [(0, 8)],
     'The passage says: "{q}" Why does this prevent trees growing?',
     "a tree cannot reach water that has drained away",
     [("trees are unable to grow in any limestone soil", "overreach"),
      ("the ground is too hard for roots to push through", "unsupported"),
      ("saltbush takes all the water before trees can", "wrong_focus")],
     "The passage ties the absence of trees to the depth of the water, not to the rock "
     "itself. Trees are unable to grow in any limestone soil is a much wider claim than "
     "the passage makes."),

    ("vocabulary_in_context", "medium", 0.92, ONE, [(0, 10)],
     'The passage concludes: "{q}" What does "consequence" mean here?',
     "a result of something else that happened",
     [("an unfortunate accident nobody intended", "wrong_sense"),
      ("a problem that has no solution at all", "overreach"),
      ("a fact about the soil of the plain", "contradicts")],
     "The treelessness follows from the water, which follows from the limestone. A fact "
     "about the soil of the plain is the reading the final sentence exists to correct."),

    ("author_purpose", "medium", 0.92, ONE, [(0, 3)],
     'Why does the writer mention: "{q}"?',
     "to explain why the rock beneath is limestone",
     [("to show how long the plain has been treeless", "unsupported"),
      ("to argue that the plain is still under water", "contradicts"),
      ("to describe the animals that lived in the sea", "wrong_focus")],
     "A shallow sea is where limestone forms, and the limestone is what the rest of the "
     "passage rests on. To show how long the plain has been treeless is not what the "
     "sentence establishes."),

    ("main_idea", "medium", 0.92, ONE, [],
     'What does this passage mainly do?',
     "trace a chain from ancient sea to missing trees",
     [("compare the Nullarbor with other Australian deserts", "unsupported"),
      ("describe what it is like to drive across the plain", "wrong_focus"),
      ("explain why the caves beneath the plain are dangerous", "overreach")],
     "Sea to limestone to vanished water to no trees is the passage's whole structure. "
     "Describe what it is like to drive across the plain covers a single clause about the "
     "road."),
  ],
 },
]


if __name__ == "__main__":
    GEN.mkdir(parents=True, exist_ok=True)
    qs = build(PASSAGES, BOOK, NN, CATEGORY, LABEL)
    path = GEN / f"{BOOK}_p{NN}.json"
    path.write_text(json.dumps(qs, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(qs)} questions across {len(PASSAGES)} passages -> {path}")
