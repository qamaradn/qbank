#!/usr/bin/env python3
"""Builds rc_nsw_paired_p3.json — 5 pairs x 4 items = 20 answer slots (§3.4).

Closes the type: 4 + 4 + 5 pairs = 13, 52 items, the §3.1 target exactly.

Pairs not used by p1 (fete, skate park, rainfall, Maria Island) or p2 (milk bar, whale,
homework, snake): a quoll reintroduction, two reviews of one film, a walking track, a
recorder in the house, and a fossil.

Stems for the single-extract items are phrased around the TEXT TYPE rather than as
"Text 1 was written mainly to —". p2 taught that lesson the hard way: three such stems
were byte-identical to a p1 stem already in the DB, and phase 4 drops near-duplicates at
0.85 without saying so, which would have quietly halved the batch.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.rc.paired_common import build  # noqa: E402

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/reading_comprehension/generated"
NN = 3
BOOK = "rc_nsw_paired"
CATEGORY = "paired_extract"
LABEL = "Paired-extract comparison"

# item = (skill, difficulty, confidence, uses, quote_refs, stem, key, distractors, expl)
PASSAGES = [
 {
  "title": "Bringing Back the Quoll",
  "topic": "Environment",
  "extracts": [
    ("Text 1", [
      "Twenty eastern quolls were released into the reserve in April as part of a "
      "five-year trial.",
      "The species has been absent from the mainland for more than sixty years.",
      "Each animal carries a small radio collar, and the collars are checked twice a week.",
      "Fourteen were still being tracked at the end of July.",
      "Two are known to have been taken by foxes outside the fenced area.",
      "The trial will be judged on whether any young are raised in the wild next season.",
    ]),
    ("Text 2", [
      "They asked if they could run the fence across the back of our place and I said "
      "yes, mostly to be polite.",
      "I did not expect much.",
      "We have had programs here before and the animals usually go the way of everything "
      "else.",
      "In June I saw one on the track at night, and it stopped and looked at me for a "
      "good four seconds.",
      "I have lived on this land for fifty-one years and I had never seen one.",
      "I would give them the other paddock too, if they asked.",
    ]),
  ],
  "items": [
    ("detail", "medium", 0.93, ["Text 1"], [(0, 3)],
     'The project update reports: "{q}" What does that figure tell the reader?',
     "six of the released animals were no longer being tracked",
     [("fourteen quolls in total were released into the reserve in April", "contradicts"),
      ("the radio collars had stopped working on every one of the animals", "overreach"),
      ("the trial had already been judged a success by the end of July", "unsupported")],
     "Twenty went out and fourteen were still on the tracker, so six had dropped off it. "
     "Fourteen quolls in total were released into the reserve in April contradicts the "
     "opening sentence, which gives the number as twenty."),

    ("mood", "medium", 0.92, ["Text 2"], [(1, 3), (1, 4)],
     'The landholder writes: "{q}" These two sentences convey —',
     "quiet astonishment at something new after a very long time",
     [("irritation at being stopped on his own back track", "contradicts"),
      ("fear of an animal that he did not recognise at all", "unsupported"),
      ("pride at having been the first person on the place to spot one", "half_right")],
     "Counting the seconds, and then the fifty-one years, is a man marking something he "
     "did not expect to see. Irritation at being stopped on his own back track reverses "
     "the feeling of a writer who ends by offering another paddock."),

    ("comparison", "medium", 0.92, ["Text 1", "Text 2"], [],
     'Both texts measure the trial, but by different things. What is the difference?',
     "Text 1 counts collared animals; Text 2 counts a single encounter",
     [("Text 1 counts encounters while Text 2 counts the collared animals", "contradicts"),
      ("Both texts judge the trial by the number of young raised next season", "half_right"),
      ("Neither text gives any figures at all for how the trial is going", "wrong_focus")],
     "One reports fourteen of twenty on the tracker; the other reports four seconds on a "
     "track at night. Neither text gives any figures at all for how the trial is going is "
     "false of both, when each of them supplies numbers."),

    ("comparison", "hard", 0.90, ["Text 1", "Text 2"], [],
     'Text 1 says the trial will be judged on whether young are raised next season. What '
     'does Text 2 suggest about that measure?',
     "that it leaves out what the trial has already changed for people",
     [("that the measure is far too easy a test to be worth using", "unsupported"),
      ("that the trial ought to be judged on fox numbers in the reserve instead", "wrong_focus"),
      ("that the landholder doubts the trial is worth running at all", "contradicts")],
     "The landholder has been turned from polite tolerance into offering more land, and no "
     "count of young would record that. That the landholder doubts the trial is worth "
     "running at all is the position he starts from and abandons."),
  ],
 },
 {
  "title": "Two Reviews",
  "topic": "The Arts",
  "extracts": [
    ("Text 1", [
      "The Lighthouse Keeper's Daughter runs for one hundred and six minutes and feels "
      "longer.",
      "The photography of the southern coast is genuinely beautiful and does most of the "
      "film's work.",
      "The story, however, asks us to believe that a fourteen-year-old could repair a "
      "diesel generator during a storm, and never explains how she learned to.",
      "Ella Marchetti is very good in the central role and deserves a better script.",
      "Younger audiences may not mind the holes.",
      "Two and a half stars.",
    ]),
    ("Text 2", [
      "I saw The Lighthouse Keeper's Daughter on Saturday and it is the best film I have "
      "seen this year.",
      "The bit where she fixes the generator in the dark had our whole row leaning "
      "forward.",
      "My brother said it was not realistic.",
      "I said neither is anything else he watches.",
      "The lighthouse is a real one and you can visit it, which I intend to do.",
      "Five stars, and I would give more.",
    ]),
  ],
  "items": [
    ("author_purpose", "medium", 0.93, ["Text 1"], [],
     'What is the newspaper reviewer setting out to do?',
     "praise what works and set out clearly what does not",
     [("discourage anybody at all from going to see the film", "overreach"),
      ("explain how the film came to be made on that coast", "wrong_focus"),
      ("criticise the performance given by the lead actor", "contradicts")],
     "The review credits the photography and the lead, then names the hole in the story. "
     "Criticise the performance given by the lead actor is the opposite of a sentence "
     "calling her very good and deserving of a better script."),

    ("inference", "medium", 0.92, ["Text 2"], [(1, 2), (1, 3)],
     'The school reviewer writes: "{q}" This shows that the writer —',
     "knows the objection and does not think it matters",
     [("agrees that the film was not realistic enough", "contradicts"),
      ("argued with the brother for the whole film", "overreach"),
      ("believes the brother had not seen the film", "unsupported")],
     "The reply does not deny the charge; it declines to treat it as important. Agrees "
     "that the film was not realistic enough would make the five stars at the end "
     "impossible to explain."),

    ("comparison", "medium", 0.92, ["Text 1", "Text 2"], [],
     'Both reviews single out the generator scene. How do they treat it?',
     "Text 1 calls it unexplained; Text 2 calls it the best moment",
     [("Both reviews treat it as the weakest part of the whole film", "contradicts"),
      ("Neither review says anything about what happens in the scene", "wrong_focus"),
      ("Both reviews agree that it is the most realistic scene of all", "half_right")],
     "One says the film never explains how she learned; the other says the row leaned "
     "forward. Both reviews treat it as the weakest part of the whole film is true of one "
     "review only."),

    ("comparison", "hard", 0.90, ["Text 1", "Text 2"], [],
     'What does Text 1 predict that Text 2 then demonstrates?',
     "that younger audiences would not mind the gaps in the story",
     [("that the photography would be the best part of the film", "half_right"),
      ("that the lead actor deserved a very much better script", "wrong_focus"),
      ("that no audience anywhere would enjoy the film at all", "contradicts")],
     "'Younger audiences may not mind the holes' is a prediction, and the second review is "
     "a younger audience not minding them. That no audience anywhere would enjoy the film "
     "at all is not something a two-and-a-half-star review says."),
  ],
 },
 {
  "title": "The Overhang Track",
  "topic": "Travel",
  "extracts": [
    ("Text 1", [
      "Grade 4. Eleven kilometres return. Allow five hours.",
      "The track climbs steadily for the first two kilometres over loose rock.",
      "There is no water on the track and no shade at all after the saddle.",
      "The last section crosses open slabs which become dangerous when wet.",
      "Do not begin this walk in the four hours before dark.",
      "Register your intentions at the trailhead.",
    ]),
    ("Text 2", [
      "Two kilometres of loose rock, and then the world opens out.",
      "From the saddle you can see three ranges and no roof of any kind.",
      "I drank a litre before the slabs and wished I had carried two.",
      "The slabs are the part everyone photographs and the part the notes warn you about, "
      "which is not a coincidence.",
      "I signed the book at the bottom and I am glad I did, because I met nobody all day.",
      "Five hours was exactly right.",
    ]),
  ],
  "items": [
    ("detail", "medium", 0.93, ["Text 1"], [],
     'According to the track notes, what must a walker do before setting out?',
     "write their intentions in the register at the trailhead",
     [("carry at least two litres of water for each person", "unsupported"),
      ("check that the open slabs are completely dry first", "overreach"),
      ("begin the walk within four hours of darkness falling", "contradicts")],
     "The last line of the notes gives that instruction directly. Begin the walk within "
     "four hours of darkness falling is the exact thing the notes tell walkers not to do."),

    ("inference", "medium", 0.92, ["Text 2"], [(1, 3)],
     'The walker writes: "{q}" The point being made is that —',
     "the finest part of a walk is often the most dangerous",
     [("the track notes were written by a photographer", "unsupported"),
      ("the slabs are safe as long as you photograph them", "contradicts"),
      ("nobody should ever photograph the slabs at all", "overreach")],
     "'Not a coincidence' links the two facts: what draws people is what the warning is "
     "about. The slabs are safe as long as you photograph them turns a connection into a "
     "cause and gets it backwards."),

    ("comparison", "medium", 0.92, ["Text 1", "Text 2"], [],
     'Both texts mention five hours. How does their use of it differ?',
     "Text 1 sets it as an allowance; Text 2 reports it as what happened",
     [("Text 1 reports it as what happened while Text 2 recommends it", "contradicts"),
      ("Both texts agree that five hours is not nearly long enough", "half_right"),
      ("Neither text says anything about how long the walk took", "wrong_focus")],
     "'Allow five hours' is advice given beforehand; 'was exactly right' is a verdict "
     "given after. Neither text says anything about how long the walk took is false of "
     "the journal, which ends on precisely that."),

    ("comparison", "hard", 0.90, ["Text 1", "Text 2"], [],
     'Which warning in the track notes does the walker confirm from experience?',
     "that there is no water and no shade past the saddle",
     [("that the open slabs become dangerous once they are wet", "unsupported"),
      ("that the first two kilometres are level and easy going", "contradicts"),
      ("that five hours is far too long to allow for the distance", "overreach")],
     "Drinking a litre and wishing for two, under no roof of any kind, is that warning "
     "met in person. That the open slabs become dangerous once they are wet is never "
     "tested, because the journal never says it rained."),
  ],
 },
 {
  "title": "B, A and G",
  "topic": "Family Life",
  "extracts": [
    ("Text 1", [
      "Year 4 has begun learning the descant recorder.",
      "Each child has been given an instrument to keep at home for practice.",
      "Ten minutes a day is far more useful than an hour on a Sunday.",
      "For the first fortnight the notes B, A and G are all that is required.",
      "Some early practice will not sound like music, and that is entirely normal.",
      "Please encourage rather than correct.",
    ]),
    ("Text 2", [
      "There is a recorder in this house now.",
      "It arrived on Tuesday and it has been B, A and G ever since, in that order, "
      "forever.",
      "Mum has the note from the teacher pinned to the fridge and points at it.",
      "On Thursday he got through the whole of Hot Cross Buns without stopping and "
      "everybody clapped, including me.",
      "I want it on the record that I clapped.",
      "It is still B, A and G.",
    ]),
  ],
  "items": [
    ("author_purpose", "medium", 0.93, ["Text 1"], [],
     'The teacher\'s note home is written mainly to —',
     "set out what practice at home should look like",
     [("warn parents that the recorder is a difficult instrument", "half_right"),
      ("explain how a descant recorder is put together", "unsupported"),
      ("ask families to go out and buy an instrument", "contradicts")],
     "It gives the daily length, the three notes, and how to respond, which is all about "
     "practice. Ask families to go out and buy an instrument contradicts a note saying "
     "each child has already been given one."),

    ("mood", "medium", 0.92, ["Text 2"], [(1, 4)],
     'Text 2 says: "{q}" This line conveys —',
     "grudging pride the writer will not quite admit to",
     [("resentment that nobody else in the room clapped", "contradicts"),
      ("genuine anger about the whole business of it", "overreach"),
      ("confusion about what happened on the Thursday", "unsupported")],
     "Insisting it be recorded is a way of admitting it while pretending not to. "
     "Resentment that nobody else in the room clapped contradicts the line before it, "
     "where everybody claps."),

    ("comparison", "medium", 0.92, ["Text 1", "Text 2"], [(0, 5)],
     'The teacher writes: "{q}" What becomes of that sentence in Text 2?',
     "it is pinned to the fridge and used as an instruction",
     [("it is ignored completely by everybody in the house", "contradicts"),
      ("it is quoted back to the teacher in a written reply", "unsupported"),
      ("it is the reason the older child took up the recorder", "wrong_focus")],
     "The note goes on the fridge and gets pointed at, which is a rule being enforced. It "
     "is ignored completely by everybody in the house is the opposite of a household that "
     "displays it."),

    ("comparison", "medium", 0.92, ["Text 1", "Text 2"], [],
     'What does Text 2 supply that Text 1 does not?',
     "what the practice sounds like to everybody else in the house",
     [("the names of the notes B, A and G that come first", "contradicts"),
      ("the reason the school chose the recorder at all", "unsupported"),
      ("the number of minutes that should be practised each and every day", "wrong_focus")],
     "The note says early practice will not sound like music; the sibling is the one "
     "living in it. The names of the notes B, A and G that come first appear in both "
     "texts, so neither of them supplies that alone."),
  ],
 },
 {
  "title": "The Fossil",
  "topic": "Science",
  "extracts": [
    ("Text 1", [
      "Ichthyosaur vertebra, Early Cretaceous, approximately 110 million years old.",
      "Found near Richmond, north-west Queensland, in 2019.",
      "Ichthyosaurs were marine reptiles, not dinosaurs, and breathed air at the surface.",
      "The inland sea that covered this region was shallow, cold and rich in life.",
      "Donated by the finder.",
      "Specimen number F58821.",
    ]),
    ("Text 2", [
      "I was eleven and I was looking for a flat stone to skip, which tells you how much "
      "I knew.",
      "It was heavier than it should have been and it had rings in it like a tree.",
      "Dad said put it back and I said no, and that is the only argument I have ever won.",
      "The museum rang three weeks later and used the word vertebra, which I had to look "
      "up.",
      "They asked whether we wanted to keep it and we said no, because it is not really "
      "ours.",
      "It has a number now, which I think is the best thing that has ever happened to a "
      "rock I picked up.",
    ]),
  ],
  "items": [
    ("detail", "medium", 0.93, ["Text 1"], [(0, 2)],
     'The museum label states: "{q}" This tells the reader that ichthyosaurs —',
     "lived in the sea but had to surface to breathe",
     [("were among the largest dinosaurs of their period", "contradicts"),
      ("could remain underwater indefinitely without surfacing", "overreach"),
      ("were the only reptiles living in the inland sea", "unsupported")],
     "'Not dinosaurs' and 'breathed air at the surface' are both stated outright. Were "
     "among the largest dinosaurs of their period contradicts the label in the same "
     "sentence that describes them."),

    ("mood", "medium", 0.92, ["Text 2"], [(1, 5)],
     'The finder writes: "{q}" This conveys —',
     "delight that something ordinary was made permanent",
     [("regret at having given the fossil away to the museum", "contradicts"),
      ("pride at having identified the specimen without help", "half_right"),
      ("surprise that the museum wanted to keep it at all", "unsupported")],
     "Calling a catalogue number the best thing that could happen to a rock is pleasure, "
     "not loss. Regret at having given the fossil away to the museum contradicts a writer "
     "who says it is not really theirs."),

    ("comparison", "medium", 0.92, ["Text 1", "Text 2"], [(0, 4)],
     'The label says only: "{q}" What does Text 2 add to those four words?',
     "why the family decided not to keep it",
     [("the specimen number the museum later assigned to it", "contradicts"),
      ("the scientific name of the animal it once belonged to", "wrong_focus"),
      ("the reason the museum wanted the fossil in the first place", "unsupported")],
     "The account explains the decision — that it is not really theirs — which the label "
     "records only as a fact. The specimen number the museum later assigned to it is on "
     "the label already."),

    ("comparison", "hard", 0.90, ["Text 1", "Text 2"], [],
     'Text 1 records what the fossil is. What does Text 2 record?',
     "what finding it meant to the person who found it",
     [("how old the fossil was eventually found to be", "contradicts"),
      ("the scientific reason the specimen is important", "wrong_focus"),
      ("a complaint that the finder was never paid for it", "unsupported")],
     "The second text is about a skipping stone, an argument with a father, and a word "
     "that had to be looked up. How old the fossil was eventually found to be is on the "
     "label, not in the account."),
  ],
 },
]


if __name__ == "__main__":
    GEN.mkdir(parents=True, exist_ok=True)
    qs = build(PASSAGES, BOOK, NN, CATEGORY, LABEL)
    path = GEN / f"{BOOK}_p{NN}.json"
    path.write_text(json.dumps(qs, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(qs)} questions across {len(PASSAGES)} pairs -> {path}")
