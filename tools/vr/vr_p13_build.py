#!/usr/bin/env python3
"""Builds vr_vic_acer_p13.json — 30 vocabulary-in-context questions (TASK §3.1).

Fourth batch of the ~341-item top-up in vic_content_taxonomy_TASK.md §5.3. The mix is
vocabulary-poor and §3.1 makes vocabulary the dominant real type at 30%, so 186 of the
341 are this category.

Calibration, from TASK §3: words a capable Year 8 meets in READING, not in a word list.
Students rated this section 8.5-9.5/10 for comfort on the 20 June 2026 paper and one
rated it 1.5/10 for difficulty, so the bank being harder than the exam is a defect, not
a margin. Exotica is refused by vr_finalise.TOO_HARD.

Every distractor declares HOW it is wrong, and the three must differ. In ~24 of 26
sampled questions in the shipped bank the three distractors were mutual synonyms and the
key was the semantic singleton, answerable without knowing the target word at all.
"""
import datetime
import json
import pathlib
import sys
import uuid

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/verbal_reasoning/generated"
NN = 13
BOOK = "vr_vic_acer"
CATEGORY = "vocabulary_synonym"
LABEL = "Vocabulary in context / synonyms"
NOW = datetime.datetime(2026, 8, 11, 10, 0, 0, tzinfo=datetime.timezone.utc) \
    .isoformat().replace("+00:00", "Z")

# (target, stem, key, [(distractor, relation) x3], explanation, difficulty, confidence)
# Relation sets are deliberately varied across the batch: three distractors that fail the
# same way cohere, and relation_monotony rejects a batch that reaches for one combination.
ITEMS = [
 ("glimpse", "Through the gap in the trees we caught a glimpse of the lake before the road turned.", "brief look",
  [("long stare", "opposite"), ("shoreline", "domain"), ("photograph", "collocation")],
  "A glimpse is a short, partial sighting, which is what a gap in trees allows; 'long stare' is the sustained looking the turning road made impossible.", "medium", 0.94),
 ("grave", "The vet's expression was grave enough that nobody asked a question.", "serious",
  [("cheerful", "opposite"), ("grieve", "form"), ("puzzled", "nuance")],
  "Grave here means solemn and weighty, which is why the room went quiet; 'puzzled' would suggest the vet was uncertain rather than bearing bad news.", "medium", 0.94),
 ("halt", "Works on the bridge will halt all traffic between six and nine on Sunday.", "stop",
  [("hasten", "opposite"), ("congest", "domain"), ("divert", "nuance")],
  "To halt traffic is to bring it to a stand, which a closure does; 'divert' would send the same traffic another way rather than stopping it.", "medium", 0.95),
 ("hardy", "Only a few hardy shrubs survive on that side of the ridge.", "tough",
  [("delicate", "opposite"), ("hasty", "form"), ("native", "domain")],
  "Hardy means able to survive difficult conditions, which surviving on an exposed ridge shows; 'native' says where a plant is from rather than how well it copes.", "medium", 0.94),
 ("hoard", "Ants hoard seed through summer and live off it when the ground dries out.", "stockpile",
  [("squander", "opposite"), ("bury", "domain"), ("harvest", "nuance")],
  "To hoard is to store up a supply for later, which is why the ants get through the dry; 'harvest' is the gathering rather than the keeping.", "medium", 0.94),
 ("hollow", "The trunk turned out to be hollow, which is why the whole tree came down so easily.", "empty inside",
  [("solid", "opposite"), ("brittle", "domain"), ("rotten", "nuance")],
  "Hollow describes a space where material should be, which explains a tree with nothing to hold it; 'rotten' names decay, which may cause hollowness but is not the same thing.", "medium", 0.94),
 ("hover", "A kestrel will hover almost motionless above the paddock before dropping.", "hang in place",
  [("plunge", "opposite"), ("perch", "domain"), ("circle", "nuance")],
  "To hover is to stay in one spot in the air, which 'almost motionless' spells out; 'circle' would mean moving steadily around rather than holding still.", "medium", 0.94),
 ("idle", "Two of the three machines sat idle for the whole of the wet season.", "unused",
  [("busy", "opposite"), ("stored", "domain"), ("broken", "nuance")],
  "Idle means not in use, which says nothing about whether the machines worked; 'broken' adds a reason the sentence does not give.", "medium", 0.94),
 ("ignite", "One spark from the grinder was enough to ignite the dry grass along the fence.", "set alight",
  [("extinguish", "opposite"), ("smoulder", "domain"), ("scorch", "nuance")],
  "To ignite is to start something burning, which one spark in dry grass does; 'scorch' would mean surface burning without the fire taking hold.", "medium", 0.95),
 ("illuminate", "A single skylight is enough to illuminate the whole workshop by mid-morning.", "light up",
  [("darken", "opposite"), ("heat", "nuance"), ("ventilate", "domain")],
  "To illuminate is to fill a space with light, which is what a skylight does; 'ventilate' is another thing an opening in a roof might do but concerns air.", "medium", 0.94),
 ("imitate", "The lyrebird can imitate a chainsaw well enough to fool anyone standing nearby.", "copy",
  [("originate", "opposite"), ("startle", "domain"), ("mock", "nuance")],
  "To imitate is to reproduce something faithfully, which fooling a listener requires; 'mock' would add ridicule, which a bird's call plainly does not carry.", "medium", 0.94),
 ("immense", "The immense scale of the wheat run only becomes clear from the air.", "vast",
  [("tiny", "opposite"), ("intense", "form"), ("fertile", "domain")],
  "Immense means very great in size, which is why the scale needs height to take in; 'fertile' describes the quality of the land, not how much of it there is.", "medium", 0.95),
 ("impair", "Even a light haze can impair visibility enough to close the strip.", "weaken",
  [("sharpen", "opposite"), ("impale", "form"), ("obscure", "nuance")],
  "To impair something is to reduce how well it works, which is what haze does to visibility; 'obscure' would mean hiding a particular thing rather than degrading sight generally.", "medium", 0.93),
 ("implement", "The school will implement the new timetable from the start of next term.", "put into effect",
  [("abandon", "opposite"), ("impediment", "form"), ("draft", "nuance")],
  "To implement is to put a plan into actual operation, which starting next term describes; 'draft' is the earlier stage of writing it rather than running it.", "medium", 0.94),
 ("imply", "Her silence seemed to imply that she had already made up her mind.", "suggest",
  [("declare", "opposite"), ("employ", "form"), ("confirm", "overreach")],
  "To imply is to indicate something without stating it, which silence can do; 'confirm' claims far more certainty than an unspoken hint provides.", "medium", 0.94),
 ("incur", "Late entries incur a small fee that goes to the ground fund.", "attract",
  [("avoid", "opposite"), ("occur", "form"), ("waive", "nuance")],
  "To incur a charge is to bring it upon yourself, which late entry does; 'waive' means the opposite action of letting the fee go.", "medium", 0.93),
 ("indicate", "A rising reading on the gauge would indicate a leak somewhere in the line.", "signal",
  [("disprove", "opposite"), ("indict", "form"), ("repair", "domain")],
  "To indicate is to be a sign of something, which is what an instrument reading does; 'repair' is what you would then do about the leak.", "medium", 0.94),
 ("inhabit", "Only three species of frog inhabit the swamp at that altitude.", "occupy",
  [("desert", "opposite"), ("inherit", "form"), ("visit", "nuance")],
  "To inhabit a place is to live in it, which is a permanent arrangement; 'visit' would mean the frogs came and went rather than lived there.", "medium", 0.94),
 ("inhibit", "Cold nights inhibit growth even when the days are warm enough.", "restrain",
  [("promote", "opposite"), ("inhabit", "form"), ("halt", "overreach")],
  "To inhibit is to hold something back without stopping it, which is why growth still happens; 'halt' would mean growth ceased altogether.", "medium", 0.93),
 ("initiate", "A parent can initiate the process by lodging a single form at the office.", "start",
  [("conclude", "opposite"), ("imitate", "form"), ("complete", "nuance")],
  "To initiate is to set something in motion, which lodging the first form does; 'complete' is the far end of the same process.", "medium", 0.94),
 ("inquire", "Several members rang to inquire about the change to the fixture.", "ask",
  [("answer", "opposite"), ("acquire", "form"), ("complain", "nuance")],
  "To inquire is to seek information, which is what a phone call about a change is; 'complain' would add a grievance the sentence does not report.", "medium", 0.94),
 ("inspect", "An engineer will inspect the footings before any concrete is poured.", "examine",
  [("overlook", "opposite"), ("suspect", "form"), ("approve", "nuance")],
  "To inspect is to look over something carefully, which is what precedes approval; 'approve' is the decision that may follow the looking.", "medium", 0.94),
 ("intense", "The intense heat off the tin roof made the shed unusable by ten.", "extreme",
  [("mild", "opposite"), ("intent", "form"), ("humid", "domain")],
  "Intense means very great in degree, which is why the shed could not be used; 'humid' describes moisture in the air, a different property altogether.", "medium", 0.94),
 ("intercept", "A defender managed to intercept the pass just short of the goal square.", "cut off",
  [("deliver", "opposite"), ("interrupt", "form"), ("deflect", "nuance")],
  "To intercept is to take possession of something in transit, which is what stopping a pass means; 'deflect' would send the ball off course without gaining it.", "medium", 0.94),
 ("intervene", "A teacher had to intervene before the argument reached the car park.", "step in",
  [("withdraw", "opposite"), ("interview", "form"), ("mediate", "nuance")],
  "To intervene is to come between people to stop something, which is why the argument went no further; 'mediate' implies a longer process of settling a dispute.", "medium", 0.94),
 ("invert", "Invert the tin over the rack and the cake should come out whole.", "turn upside down",
  [("upright", "opposite"), ("invent", "form"), ("grease", "collocation")],
  "To invert something is to turn it over, which is how a cake leaves a tin; 'grease' is another thing done to a tin but happens before baking.", "medium", 0.94),
 ("isolate", "Vets will isolate any animal showing symptoms until the tests come back.", "separate",
  [("combine", "opposite"), ("insulate", "form"), ("treat", "nuance")],
  "To isolate is to keep something apart from the rest, which is what waiting on tests requires; 'treat' is a different action taken once results are known.", "medium", 0.95),
 ("jolt", "A jolt as the carriage crossed the points woke half the passengers.", "jerk",
  [("glide", "opposite"), ("bolt", "form"), ("noise", "domain")],
  "A jolt is a sudden rough movement, which is what crossing points produces; 'noise' is another thing that might wake people but is not a movement.", "medium", 0.94),
 ("justify", "The committee could not justify the cost of resurfacing both courts at once.", "defend",
  [("condemn", "opposite"), ("rectify", "form"), ("afford", "nuance")],
  "To justify a cost is to show good reason for it, which the committee could not do; 'afford' concerns whether the money exists rather than whether spending it is defensible.", "medium", 0.94),
 ("kindle", "A short talk from an old member was enough to kindle interest in the club again.", "arouse",
  [("smother", "opposite"), ("kindly", "form"), ("sustain", "nuance")],
  "To kindle is to get something going from almost nothing, which is what reviving interest is; 'sustain' would mean keeping alive an interest that already burned.", "medium", 0.93),
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
