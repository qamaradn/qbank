#!/usr/bin/env python3
"""Builds vr_vic_acer_p4.json — 21 vocabulary-in-context questions (TASK §3.1)."""
import datetime
import json
import pathlib
import sys
import uuid

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/verbal_reasoning/generated"
NN = 4
BOOK = "vr_vic_acer"
CATEGORY = "vocabulary_synonym"
LABEL = "Vocabulary in context / synonyms"
NOW = datetime.datetime(2026, 8, 4, 13, 0, 0, tzinfo=datetime.timezone.utc) \
    .isoformat().replace("+00:00", "Z")

ITEMS = [
 ("hamper",
  "Low cloud over the ranges continued to hamper the search through most of Thursday.",
  "get in the way of",
  [("speed along", "opposite"), ("hand back to", "form"), ("call off", "overreach")],
  "To hamper is to make something harder without stopping it, which fits a search that "
  "carried on all day; 'call off' would mean the search ended, which it did not.",
  "medium", 0.94),

 ("heed",
  "Few walkers heed the sign about afternoon storms until they are caught out on the "
  "exposed saddle.",
  "pay attention to",
  [("take no notice of", "opposite"), ("hurry past", "domain"), ("agree fully with", "nuance")],
  "To heed is to take notice and act accordingly, which most walkers fail to do here; "
  "'agree fully with' is close but you can heed a warning without agreeing about the risk.",
  "medium", 0.93),

 ("hostile",
  "The reception at the public forum was hostile, with speakers interrupted before they "
  "finished.",
  "openly unfriendly",
  [("warmly welcoming", "opposite"), ("largely indifferent", "nuance"), ("strictly formal", "domain")],
  "Hostile means actively antagonistic, which the interruptions show; 'largely "
  "indifferent' would mean the crowd did not care, but they cared enough to heckle.",
  "medium", 0.94),

 ("humble",
  "Despite winning three premierships, the coach remained humble about his own part in "
  "them.",
  "unassuming",
  [("boastful", "opposite"), ("humid", "form"), ("private", "nuance")],
  "Humble means not thinking too highly of oneself, which downplaying his role shows; "
  "'private' would mean he kept to himself, which is a different quality entirely.",
  "medium", 0.94),

 ("impose",
  "The council voted to impose a curfew on the skate park after a run of late-night "
  "complaints.",
  "put in place",
  [("lift entirely", "opposite"), ("suppose wrongly", "form"), ("look into", "domain")],
  "To impose a rule is to establish it by authority, which is what a council vote does; "
  "'look into' describes investigating the complaints rather than acting on them.",
  "medium", 0.94),

 ("incite",
  "The article was accused of trying to incite anger rather than explain the decision.",
  "stir up",
  [("calm down", "opposite"), ("insight", "form"), ("record", "domain")],
  "To incite is to provoke a reaction into being, which the accusation describes; "
  "'insight' sounds almost identical but means a deep understanding of something.",
  "medium", 0.93),

 ("intact",
  "The nest was still intact after the storm, though the branch beneath it had split.",
  "undamaged",
  [("destroyed", "opposite"), ("in contact", "form"), ("abandoned", "domain")],
  "Intact means whole and unbroken, which is the contrast drawn with the split branch; "
  "'abandoned' concerns whether birds still used it, not whether it survived.",
  "medium", 0.95),

 ("meddle",
  "She warned the committee not to meddle in matters the club's members had already "
  "settled.",
  "interfere",
  [("assist", "opposite"), ("medal", "form"), ("comment", "nuance")],
  "To meddle is to involve yourself where you are not wanted, which the warning implies; "
  "'comment' is milder and would not carry the sense of unwelcome interference.",
  "medium", 0.94),

 ("mimic",
  "The lyrebird can mimic a chainsaw so precisely that walkers look around for the "
  "operator.",
  "imitate",
  [("invent", "opposite"), ("startle", "domain"), ("exaggerate", "nuance")],
  "To mimic is to copy a sound or manner closely, which is exactly what the lyrebird does; "
  "'exaggerate' would mean overstating the sound rather than reproducing it faithfully.",
  "medium", 0.94),

 ("modest",
  "The turnout was modest, but the organisers were satisfied given the weather that "
  "weekend.",
  "fairly small",
  [("very large", "opposite"), ("badly run", "domain"), ("barely any", "overreach")],
  "Modest here means small in size but not disappointing, which the satisfaction confirms; "
  "'barely any' overstates it, and would not leave the organisers pleased.",
  "medium", 0.93),

 ("muster",
  "The team could barely muster eleven players for the last round of the season.",
  "gather together",
  [("send away", "opposite"), ("master fully", "form"), ("pay properly", "domain")],
  "To muster is to assemble a number of people or things, which fitting out a side "
  "requires; 'master fully' resembles the word but means to become skilled at something.",
  "medium", 0.94),

 ("nurture",
  "The program was set up to nurture young umpires rather than throw them straight into "
  "senior games.",
  "carefully develop",
  [("quickly discard", "opposite"), ("closely watch", "nuance"), ("formally register", "domain")],
  "To nurture is to support something as it grows, which the contrast with being thrown in "
  "makes clear; 'closely watch' describes observing them rather than helping them improve.",
  "medium", 0.94),

 ("omit",
  "The editor chose to omit two paragraphs that named the school before the piece ran.",
  "leave out",
  [("put in", "opposite"), ("emit", "form"), ("rewrite", "nuance")],
  "To omit is to leave something out, which is what happened to the paragraphs; 'rewrite' "
  "would mean they were changed and kept rather than removed.",
  "medium", 0.95),

 ("ornate",
  "The old bank has an ornate ceiling that most customers never look up to notice.",
  "richly decorated",
  [("perfectly plain", "opposite"), ("recently painted", "domain"), ("unusually high", "nuance")],
  "Ornate means elaborately decorated, which is why the ceiling is worth noticing; "
  "'recently painted' describes its condition rather than its decoration.",
  "medium", 0.93),

 ("peril",
  "The crew understood the peril of crossing the bar at low tide in an easterly.",
  "serious danger",
  [("complete safety", "opposite"), ("small nuisance", "nuance"), ("legal penalty", "domain")],
  "Peril means grave risk of harm, which crossing a bar in bad conditions carries; 'small "
  "nuisance' understates it to the point of reversing the warning.",
  "medium", 0.94),

 ("pledge",
  "Each club had to pledge a share of the costs before the association would approve the "
  "fixture.",
  "formally promise",
  [("flatly refuse", "opposite"), ("privately hope", "nuance"), ("openly discuss", "domain")],
  "To pledge is to commit yourself by a formal promise, which approval depended on; "
  "'privately hope' carries no commitment at all and would not satisfy the association.",
  "medium", 0.94),

 ("plummet",
  "Attendances began to plummet once the team dropped out of finals contention.",
  "fall sharply",
  [("climb steadily", "opposite"), ("plump up", "form"), ("level off", "nuance")],
  "To plummet is to drop suddenly and steeply, which losing finals hopes would cause; "
  "'level off' would mean the numbers steadied rather than collapsed.",
  "medium", 0.95),

 ("potent",
  "The new antivenom proved more potent than the version it replaced, and less of it was "
  "needed.",
  "powerful",
  [("harmless", "opposite"), ("patent", "form"), ("portable", "domain")],
  "Potent means strong in effect, which is why a smaller dose worked; 'patent' resembles "
  "the word but refers to a registered invention.",
  "medium", 0.94),

 ("prompt",
  "A prompt response from the volunteer brigade kept the fire to a single shed.",
  "immediate",
  [("delayed", "opposite"), ("promised", "form"), ("thorough", "nuance")],
  "Prompt means done without delay, which is what limited the damage; 'thorough' describes "
  "how completely something is done rather than how quickly.",
  "medium", 0.95),

 ("recede",
  "The floodwater began to recede on Sunday, leaving a line of silt across the road.",
  "draw back",
  [("push forward", "opposite"), ("proceed on", "form"), ("dry out", "domain")],
  "To recede is to move back from a former position, which the silt line records; 'dry "
  "out' describes what happens afterwards rather than the water's retreat itself.",
  "medium", 0.95),

 ("refute",
  "She used the survey data to refute the claim that nobody in the town wanted the bypass.",
  "disprove",
  [("confirm", "opposite"), ("refuse", "form"), ("restate", "domain")],
  "To refute is to show a claim is false, which evidence allows; 'refuse' looks similar "
  "but means declining to do something, not proving it wrong.",
  "hard", 0.92),
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
