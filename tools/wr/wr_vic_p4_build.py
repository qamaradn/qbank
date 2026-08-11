#!/usr/bin/env python3
"""Builds wr_vic_acer_p4.json — the last 10 persuasive-slot prompts, completing VIC at 54.

CALIBRATION. ~20 minutes, Year 8, 160-250 words. Design rules in
tools/wr/wr_vic_p1_build.py (one scene) and tools/wr/wr_vic_p3_build.py (one position,
one objection, arguable both ways).

WHAT THIS BATCH DELIBERATELY AVOIDS. p3 is heavy on institutional questions — councils,
schools, museums, libraries — because those give a Year 8 something concrete to argue
about. Run as a whole set, though, that produces a bank where every prompt sounds like a
policy paper, and a candidate who is good at one is good at all of them. This batch
therefore takes the argument somewhere else:

  - three prompts where the reader must be persuaded of a JUDGEMENT rather than a policy
    ("was this fair", "which of these two is the better outcome")
  - two where the candidate must argue against something widely agreed, so agreement
    cannot substitute for argument
  - two written as a letter or a submission with a named audience, because who you are
    persuading changes how, and ACER's "convey ideas in precise language" is audience work

Each prompt is listed below with the counter-argument it was built against, so the
both-ways test can be checked rather than taken on trust. It is recorded HERE and not in
the `topic` field: topic renders in the prompt's meta line in the review UI (index.html
~line 889) and is a category label a delivery app will surface too, so "counter: children
notice the score whether or not it is published" would hand the candidate half the
argument. Caught by reading a rendered prompt, not by the finaliser — no check looks at
what a field means.

    late assignment ....... a rule bent once is not a rule
    swimming squads ....... children join clubs to compete, not to be retained
    read to your children . difficulty is not a reason to stop saying true things
    climbing frame ........ an injury is specific, a benefit is diffuse
    canteen trial ......... the healthiest option lost money
    junior ladders ........ children notice the score whether or not it is published
    friend's confidence ... trust broken once cannot be offered again
    work hard enough ...... disbelieving it changes nothing and costs effort
    bakery at 5 am ........ a business's difficulty is not the neighbours' debt
    streaming ............. both sides claim to protect the struggling student

Held before this batch: 17 in the persuasive slot. Target 27.
"""
import datetime
import json
import pathlib
import sys
import uuid

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/writing/generated"
BOOK = "wr_vic_acer"
NN = 4
NOW = datetime.datetime(2026, 8, 12, 12, 0, 0, tzinfo=datetime.timezone.utc) \
    .isoformat().replace("+00:00", "Z")

PROMPTS = []


def P(stimulus_type, stimulus, task, topic, focus, lo=160, hi=250, difficulty="medium"):
    PROMPTS.append({
        "id": str(uuid.uuid4()),
        "prompt_type": "persuasive",
        "school_type": "victorian_selective",
        "stimulus_type": stimulus_type,
        "stimulus_content": stimulus,
        "stimulus_image_desc": None,
        "task_instruction": task,
        "word_count_min": lo,
        "word_count_max": hi,
        "time_limit_minutes": 20,
        "target_year": "7-8",
        "difficulty": difficulty,
        "topic": topic,
        "marking_focus": json.dumps(focus),
        "source_book": BOOK,
        "review_status": "pending",
        "created_at": NOW,
    })


P("scenario",
  "A student in an Australian school hands in an assignment two days late. It is the best "
  "piece of work in the class. The published rule is 10% off per day, which drops it from "
  "the top mark to the middle of the group. The teacher applies the rule. Another teacher, "
  "hearing about it, says that is exactly backwards.",
  "Write a persuasive piece arguing whether the rule should have been applied here. This "
  "is a judgement, not a policy — argue about this student and this piece of work.",
  "Fairness vs consistency",
  ["position", "reasoning", "counter-argument", "language"], difficulty="hard"),

P("text",
  "Two things happened at a Geelong swimming club in the same season. The under-12 squad "
  "won its division for the first time in nine years and lost four of its eleven swimmers "
  "before the next season began. The under-14 squad finished last and did not lose anyone.",
  "Write a persuasive piece arguing which squad had the better season. You will have to "
  "say what a junior sporting club is actually for, and defend that.",
  "Winning vs retention",
  ["position", "reasoning", "values", "language"], difficulty="hard"),

P("quote",
  "\"Read to your children. It is the single most valuable thing a parent can do.\"\n\n"
  "The advice is repeated in every Australian parenting pamphlet and it is almost "
  "certainly good advice. It is also given, unchanged, to a parent working two jobs and to "
  "a parent working none, as though the obstacle were ignorance.",
  "Write a persuasive piece arguing against this advice as it is usually given. You are "
  "not arguing that reading is bad — you are arguing about the advice.",
  "Advice vs circumstance",
  ["position", "precision", "counter-argument", "language"], difficulty="hard"),

P("scenario",
  "Your local council is considering removing the climbing frame from a park in "
  "Warrnambool after two broken arms in three years. The replacement equipment is lower, "
  "softer and rated for the same age group. Attendance at a park with similar equipment "
  "fell by a third after the same change.",
  "Write a persuasive letter to the council arguing for or against the removal. Write it "
  "to a councillor who has to vote on Tuesday, not to a general reader.",
  "Safety vs risk",
  ["position", "audience awareness", "reasoning", "language"]),

P("data",
  "School canteen trial, Bendigo — term 3\n\n"
  "  Before: hot food 68% of sales, fruit and salad 9%\n"
  "  After removing hot food two days a week:\n"
  "    fruit and salad ......... 14%\n"
  "    total canteen sales ..... down 41%\n"
  "    students bringing lunch . up sharply\n\n"
  "The canteen runs at a small profit that funds the breakfast club.",
  "Write a persuasive piece arguing whether the trial should continue next term. The "
  "breakfast club is not a detail you can leave out.",
  "Health policy vs unintended cost",
  ["position", "use of evidence", "reasoning", "language"], difficulty="hard"),

P("text",
  "An Australian sporting body has proposed that all junior competitions publish no "
  "ladders and no individual statistics until Under-15s. Several countries do this. "
  "Coaches are divided, parents more so, and the players have not been asked.",
  "Write a persuasive submission to the sporting body supporting or opposing the proposal. "
  "Somewhere in it, say what the players themselves would probably want and why that "
  "should or should not settle it.",
  "Development vs competition",
  ["position", "audience awareness", "reasoning", "language"]),

P("scenario",
  "A friend at your Australian secondary school tells you something in confidence that "
  "worries you. It is not an emergency, "
  "nobody is in danger, and they have asked you plainly not to repeat it. You think an "
  "adult would be able to help. You also think your friend would never trust you again.",
  "Write a persuasive piece arguing what you should do, addressed to yourself. Argue it "
  "properly — the case for staying silent is not a weak one and should not be treated as "
  "if it were.",
  "Loyalty vs help",
  ["position", "honesty", "counter-argument", "language"], difficulty="hard"),

P("quote",
  "\"If you work hard enough in this country, you will get where you want to go.\"\n\n"
  "It is said sincerely, usually by people for whom it turned out to be true. It is also "
  "the most common thing said to Australian students in Year 8, at exactly the age when "
  "they start being able to check it against what they can see.",
  "Write a persuasive piece agreeing or disagreeing with the quote. Whichever you choose, "
  "you must account for the people the other side would point to.",
  "Effort vs circumstance",
  ["position", "reasoning", "counter-argument", "language"], difficulty="hard"),

P("text",
  "A Victorian town's only bakery has been bought by the family who have run it for "
  "eleven years. They have applied to open at 5 am instead of 6, which needs council "
  "approval because of noise. Four of the nine houses backing onto the lane have objected. "
  "The bakery says the extra hour is the difference between staying open and not.",
  "Write a persuasive letter to the council on behalf of either the bakery or the "
  "neighbours. Write to be read by someone who has already heard the other side.",
  "Livelihood vs amenity",
  ["position", "audience awareness", "reasoning", "language"]),

P("scenario",
  "A school in Melbourne is choosing between two ways of forming its Year 8 classes: "
  "grouping students by ability in every subject, or keeping mixed classes throughout. "
  "The teachers are almost evenly split, and both groups say they are arguing for the "
  "students who would otherwise be left behind.",
  "Write a persuasive piece arguing for one of the two. Both sides claim the same goal, so "
  "your case has to explain why your side reaches it and the other does not.",
  "Streaming vs mixed ability",
  ["position", "reasoning", "counter-argument", "language"], difficulty="hard"),


if __name__ == "__main__":
    GEN.mkdir(parents=True, exist_ok=True)
    path = GEN / f"{BOOK}_p{NN}.json"
    path.write_text(json.dumps(PROMPTS, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    print(f"wrote {len(PROMPTS)} prompts -> {path}")
