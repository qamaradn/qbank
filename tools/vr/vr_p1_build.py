#!/usr/bin/env python3
"""Builds vr_vic_acer_p1.json — 21 vocabulary-in-context questions (TASK §3.1).

Design rules, each one a response to a defect measured in the existing VR bank:

OPTIONS ARE PARALLEL. All four options in a question share grammatical form and sit in
the same length band. The existing bank leans on multi-word glosses for the key beside
one-word distractors, which hands the answer to `length_tell`.

DISTRACTORS ARE WRONG IN THREE DIFFERENT WAYS. Declared per option and enforced by
tools.question_checks.distractor_relation_errors. In ~24 of 26 sampled existing items all
three distractors were mutual synonyms, so the key was the odd one out and the question
tested pattern-spotting rather than vocabulary.

STEMS CARRY CONTEXT. A bare "Which word means X?" frame scores 0.857+ against the same
frame with another word, above phase 4's silent 0.85 dedup threshold. Context also makes
the item a test of reading, which is what TASK §3.1 asks for.

PITCH. Words a capable Year 8 meets in reading — the level of edict, discern, curb,
pique, ovation, curtail. TASK §3 records comfort ratings of 8.5-9.5/10 on the real paper.
"""
import datetime
import json
import pathlib
import sys
import uuid

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/verbal_reasoning/generated"
NN = 1
BOOK = "vr_vic_acer"
CATEGORY = "vocabulary_synonym"
LABEL = "Vocabulary in context / synonyms"
NOW = datetime.datetime(2026, 8, 4, 10, 0, 0, tzinfo=datetime.timezone.utc) \
    .isoformat().replace("+00:00", "Z")

# (target, stem, key, [(distractor, relation) x3], explanation, difficulty, confidence)
ITEMS = [
 ("curtail",
  "Faced with a shrinking budget, the Ballarat council voted to curtail its summer events "
  "programme rather than cancel it altogether.",
  "cut back",
  [("put off", "nuance"), ("build up", "opposite"), ("carry out", "form")],
  "To curtail something is to cut it back, which is why the programme shrank instead of "
  "ending; 'put off' would mean delaying it to a later date, but the council shortened it "
  "rather than moved it.",
  "medium", 0.94),

 ("discern",
  "Through the smoke haze drifting across the valley, we could just discern the outline of "
  "the ranger's hut on the far ridge.",
  "make out",
  [("look past", "opposite"), ("give out", "form"), ("map out", "domain")],
  "To discern is to manage to see something indistinct, so 'make out' fits the outline "
  "barely visible in haze; 'look past' would mean failing to notice it at all.",
  "medium", 0.95),

 ("edict",
  "The incoming principal issued an edict that mobile phones were to stay in lockers for "
  "the whole school day, and made clear the decision was not open to discussion.",
  "an official order",
  [("a lengthy debate", "domain"), ("a permanent ban", "overreach"), ("a polite request", "nuance")],
  "An edict is an order issued by someone in authority, which matches a rule imposed with "
  "no exceptions; 'a polite request' misses that an edict compels rather than asks.",
  "medium", 0.93),

 ("curb",
  "Rangers have installed low fencing along the wetland edge to curb the spread of feral "
  "pigs into the breeding grounds.",
  "hold back",
  [("keep track of", "nuance"), ("open up", "opposite"), ("carry through", "form")],
  "To curb something is to restrain it, so 'hold back' matches fencing meant to limit the "
  "pigs' spread; 'keep track of' would describe monitoring them, which fencing does not do.",
  "medium", 0.94),

 ("pique",
  "The museum designed its new dinosaur gallery to pique the curiosity of visitors who "
  "arrive certain they already know the whole story.",
  "stir up",
  [("settle down", "opposite"), ("pick out", "form"), ("set down", "domain")],
  "To pique curiosity is to arouse it, so 'stir up' fits a gallery built to provoke fresh "
  "interest; 'settle down' reverses the sense, since the aim is to unsettle assumptions.",
  "medium", 0.92),

 ("ovation",
  "When the orchestra held the final chord, the audience at Hamer Hall rose in an ovation "
  "that went on for several minutes.",
  "a burst of applause",
  [("a stunned silence", "opposite"), ("a quiet murmur", "nuance"), ("a roar of protest", "domain")],
  "An ovation is sustained applause in praise of a performance, which is why the audience "
  "stood; 'a quiet murmur' is far too subdued for a response that lasted minutes.",
  "medium", 0.95),

 ("lenient",
  "Several parents thought the umpire had been too lenient with players who argued about "
  "decisions during the grand final.",
  "easy on them",
  [("generous to them", "nuance"), ("fair to both", "collocation"), ("hard on them", "opposite")],
  "To be lenient is to punish less than the offence deserves, so 'easy on them' fits the "
  "complaint; 'generous to them' is close but describes giving something, rather than "
  "withholding a punishment that was deserved.",
  "medium", 0.93),

 ("tedious",
  "Sorting several thousand shells by size was tedious work, though the marine biology "
  "students finished it in a single afternoon.",
  "dull and slow",
  [("hard but quick", "nuance"), ("tense and risky", "form"), ("bright and lively", "opposite")],
  "Tedious work is wearisome because it is repetitive, which is why sorting thousands of "
  "shells qualifies; 'hard but quick' misses the point, since the difficulty is monotony "
  "rather than effort.",
  "medium", 0.94),

 ("vigilant",
  "Surf lifesavers stay vigilant even on quiet afternoons, because a rip can open up in a "
  "matter of minutes.",
  "on the lookout",
  [("off their guard", "opposite"), ("full of energy", "domain"), ("out of practice", "nuance")],
  "To be vigilant is to watch carefully for danger, which is exactly why lifesavers scan a "
  "quiet beach; 'full of energy' describes vigour, which a tired lifesaver could lack "
  "while still watching the water closely.",
  "medium", 0.95),

 ("novice",
  "As a novice, Amir was surprised to be paired with the club's most experienced climber "
  "for the whole weekend.",
  "a beginner",
  [("an expert", "opposite"), ("a novelist", "form"), ("a spectator", "domain")],
  "A novice is someone new to an activity, which is what makes the pairing surprising; "
  "'a spectator' would not be climbing at all, so the contrast with an experienced partner "
  "would make no sense.",
  "medium", 0.96),

 ("deter",
  "Bright lighting and visible cameras in the car park are there to deter thieves rather "
  "than to catch them after the fact.",
  "discourage",
  [("determine", "form"), ("warn", "collocation"), ("encourage", "opposite")],
  "To deter is to put someone off acting, which is why the measures work before a theft "
  "rather than after; 'warn' is close but describes telling someone of a risk, not making "
  "them decide against it.",
  "medium", 0.93),

 ("futile",
  "After three hours of bailing, the crew accepted that their efforts were futile and "
  "radioed for assistance.",
  "pointless",
  [("worthwhile", "opposite"), ("exhausting", "nuance"), ("unthinkable", "overreach")],
  "Futile efforts produce no result, which is why the crew stopped and called for help; "
  "'exhausting' describes how the bailing felt, not the fact that it was achieving nothing.",
  "medium", 0.95),

 ("hinder",
  "Heavy rain on the Hume did not stop the convoy, but it did hinder progress for several "
  "hours either side of Wodonga.",
  "hold up",
  [("help along", "opposite"), ("hand over", "form"), ("head off", "domain")],
  "To hinder is to make something slower or harder without preventing it, which matches a "
  "convoy delayed but still moving; 'help along' reverses the meaning entirely.",
  "medium", 0.94),

 ("impartial",
  "An impartial adjudicator was brought in from Adelaide so that neither school could "
  "claim the result had been decided in advance.",
  "unbiased",
  [("uninterested", "nuance"), ("prejudiced", "opposite"), ("impatient", "form")],
  "An impartial judge favours neither side, which is why an outsider was chosen; "
  "'uninterested' means lacking interest, a different idea often confused with it — an "
  "adjudicator must care about the contest while favouring nobody.",
  "hard", 0.92),

 ("lavish",
  "The centenary dinner was a lavish affair, with three courses, live music and flowers on "
  "every table.",
  "extravagant",
  [("sparing", "opposite"), ("tasteful", "collocation"), ("enormous", "nuance")],
  "Lavish means generous to the point of excess, which the three courses and flowers "
  "illustrate; 'tasteful' often appears alongside descriptions of dinners but says the "
  "event was in good taste, not that it was costly.",
  "medium", 0.92),

 ("quell",
  "Teachers moved quickly to quell the excitement in the hall so the announcement could "
  "actually be heard.",
  "put a stop to",
  [("stir up", "opposite"), ("make light of", "nuance"), ("take note of", "domain")],
  "To quell is to suppress something that has broken out, which is what the teachers did "
  "to the noise; 'make light of' would mean treating the excitement as unimportant, but "
  "they acted to stop it.",
  "medium", 0.94),

 ("mundane",
  "Between the dramatic rescues, most of a lifesaver's shift is taken up with mundane "
  "tasks like checking flags and raking the sand.",
  "ordinary",
  [("remarkable", "opposite"), ("undemanding", "nuance"), ("worthless", "overreach")],
  "Mundane tasks are everyday and unexciting, which is the contrast the sentence draws "
  "with dramatic rescues; 'undemanding' says they are easy, but a mundane task can still "
  "be hard work.",
  "medium", 0.93),

 ("abate",
  "The cyclone warning for the Whitsundays was lifted once the winds began to abate late "
  "on Tuesday evening.",
  "die down",
  [("pick up", "opposite"), ("abet", "form"), ("set in", "domain")],
  "To abate is to become less intense, which is why the warning could be lifted; 'pick up' "
  "would mean the winds were strengthening, in which case the warning would have stayed.",
  "medium", 0.95),

 ("thrive",
  "Mangroves thrive in the brackish water where the river meets the sea, even though few "
  "other trees can grow there at all.",
  "flourish",
  [("wither", "opposite"), ("thrash", "form"), ("survive", "nuance")],
  "To thrive is to grow vigorously, which is the contrast with trees that cannot grow "
  "there; 'survive' is the trap, since it means merely staying alive rather than doing well.",
  "hard", 0.91),

 ("terse",
  "The coach's terse reply to the reporter's question suggested he had no wish to discuss "
  "the selection at all.",
  "short and blunt",
  [("long and rambling", "opposite"), ("tense and uneasy", "form"), ("formal and polite", "domain")],
  "A terse reply is brief to the point of curtness, which is what signals the coach's "
  "reluctance; 'tense and uneasy' describes a mood and only resembles the word by sound.",
  "medium", 0.93),

 ("zeal",
  "Volunteers took to the dune restoration with such zeal that the planting was finished a "
  "fortnight ahead of schedule.",
  "great enthusiasm",
  [("total indifference", "opposite"), ("blind fanaticism", "overreach"), ("natural talent", "domain")],
  "Zeal is energetic enthusiasm for a cause, which explains finishing early; 'blind "
  "fanaticism' pushes the idea too far, describing zeal that has lost all judgement.",
  "medium", 0.93),
]


def build():
    out = []
    for target, stem, key, distractors, expl, diff, conf in ITEMS:
        opts = [key] + [d for d, _ in distractors]
        out.append({
            "id": str(uuid.uuid4()),
            "subject": "verbal_reasoning",
            "stem": f"{stem} As it is used here, '{target}' most nearly means:",
            "option_a": opts[0], "option_b": opts[1],
            "option_c": opts[2], "option_d": opts[3],
            "correct_answer": "A",
            "explanation": expl,
            "topic": LABEL,
            "difficulty": diff,
            "confidence": conf,
            "source_book": BOOK,
            "source_page": NN,
            "source_page_description": f"Category: {CATEGORY} — {LABEL}",
            "passage": None,
            "figure_svg": None,
            "review_status": "pending",
            "created_at": NOW,
            "target_word": target,
            "relations": {d: r for d, r in distractors},
        })
    return out


if __name__ == "__main__":
    GEN.mkdir(parents=True, exist_ok=True)
    qs = build()
    path = GEN / f"{BOOK}_p{NN}.json"
    path.write_text(json.dumps(qs, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(qs)} questions -> {path}")
