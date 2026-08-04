#!/usr/bin/env python3
"""Builds vr_vic_acer_p3.json — 21 vocabulary-in-context questions (TASK §3.1).

Same rules as vr_p1_build.py. Option lengths are matched deliberately here: across p1+p2
the key was the longest option 45% of the time against a 25% chance rate, which is a lean
worth removing before it becomes a tell.
"""
import datetime
import json
import pathlib
import sys
import uuid

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/verbal_reasoning/generated"
NN = 3
BOOK = "vr_vic_acer"
CATEGORY = "vocabulary_synonym"
LABEL = "Vocabulary in context / synonyms"
NOW = datetime.datetime(2026, 8, 4, 12, 0, 0, tzinfo=datetime.timezone.utc) \
    .isoformat().replace("+00:00", "Z")

ITEMS = [
 ("adjacent",
  "The new pavilion stands on the block adjacent to the oval, sharing a boundary fence "
  "with it.",
  "next to",
  [("far from", "opposite"), ("opposite to", "nuance"), ("attached to", "overreach")],
  "Adjacent means lying beside something, which a shared boundary fence describes; "
  "'attached to' goes further and would mean the two were joined as one structure.",
  "medium", 0.93),

 ("cordial",
  "Relations between the two clubs remained cordial even after the disputed final was "
  "referred to the tribunal.",
  "warm and friendly",
  [("cold and distant", "opposite"), ("brief and formal", "nuance"), ("sweet and fruity", "form")],
  "Cordial describes a friendly and pleasant manner, which is notable given the dispute; "
  "'sweet and fruity' is the drink of the same name and has nothing to do with relations.",
  "medium", 0.94),

 ("jovial",
  "Their jovial neighbour could be heard laughing from three houses away on a still "
  "evening.",
  "cheerful",
  [("gloomy", "opposite"), ("juvenile", "form"), ("generous", "domain")],
  "Jovial means good-humoured and merry, which the laughter demonstrates; 'generous' is "
  "another likeable quality but says nothing about someone's cheerfulness.",
  "medium", 0.95),

 ("nimble",
  "The nimble fielder cut off two certain boundaries in the final over of the match.",
  "quick and agile",
  [("slow and clumsy", "opposite"), ("numb and stiff", "form"), ("small and light", "nuance")],
  "Nimble means able to move quickly and lightly, which is what saved the boundaries; "
  "'small and light' often accompanies agility but is a description of build, not movement.",
  "medium", 0.94),

 ("quaint",
  "Tourists stop to photograph the quaint fishermen's cottages along the harbour at Port "
  "Fairy.",
  "old-world",
  [("up-to-date", "opposite"), ("run-down", "nuance"), ("hand-made", "domain")],
  "Quaint means attractively old-fashioned, which is why the cottages draw photographers; "
  "'run-down' is the trap, since quaint implies charm rather than disrepair.",
  "medium", 0.92),

 ("rash",
  "Selling the boat before the season ended proved a rash decision the family came to "
  "regret.",
  "reckless",
  [("cautious", "opposite"), ("itchy", "form"), ("rapid", "nuance")],
  "A rash decision is made too hastily and without thought for the consequences, which "
  "the regret confirms; 'rapid' captures the speed but not the recklessness.",
  "medium", 0.94),

 ("sombre",
  "The mood in the changing room was sombre once news of the injury came through from the "
  "hospital.",
  "gloomy",
  [("cheerful", "opposite"), ("sober", "form"), ("silent", "nuance")],
  "Sombre means dark and serious in mood, which the injury news explains; 'silent' "
  "describes the noise level, and a room can be sombre while people are still talking.",
  "medium", 0.94),

 ("sparse",
  "Vegetation is sparse along the ridge, with a few stunted mallee trees and very little "
  "else.",
  "thinly spread",
  [("densely packed", "opposite"), ("roughly even", "nuance"), ("freshly cut", "domain")],
  "Sparse means thinly scattered, which the few stunted trees illustrate; 'roughly even' "
  "describes how growth is distributed rather than how little of it there is.",
  "medium", 0.94),

 ("elaborate",
  "The memorial has an elaborate frieze running the full length of its northern wall.",
  "highly detailed",
  [("extremely plain", "opposite"), ("poorly finished", "domain"), ("unnecessarily long", "nuance")],
  "Elaborate means worked out with great detail, which is what a full-length carved frieze "
  "suggests; 'unnecessarily long' judges the size rather than the intricacy.",
  "medium", 0.93),

 ("grim",
  "The captain's expression was grim as he read out the injury list before training "
  "started.",
  "stern and harsh",
  [("bright and jolly", "opposite"), ("grimy and dirty", "form"), ("quiet and calm", "nuance")],
  "Grim describes a severe, forbidding look, which bad news would produce; 'quiet and "
  "calm' would suggest composure rather than the severity the word carries.",
  "medium", 0.93),

 ("hasty",
  "A hasty repair to the fence held for barely a week before the cattle pushed through it "
  "again.",
  "done too quickly",
  [("carefully planned", "opposite"), ("hazy and unclear", "form"), ("late in arriving", "domain")],
  "Hasty means done in a hurry and therefore carelessly, which is why the repair failed; "
  "'late in arriving' concerns timing rather than the haste of the work itself.",
  "medium", 0.94),

 ("inept",
  "His inept attempt to reverse the trailer entertained everyone waiting at the boat ramp.",
  "clumsy and unskilled",
  [("capable and assured", "opposite"), ("inert and motionless", "form"), ("rude and impolite", "domain")],
  "Inept means lacking skill, which is what made the attempt entertaining to watch; "
  "'inert and motionless' resembles the word but describes something not moving at all.",
  "medium", 0.94),

 ("keen",
  "She was keen to start the project and had drafted a plan before the first meeting was "
  "even called.",
  "eager",
  [("reluctant", "opposite"), ("kind", "form"), ("calm", "domain")],
  "Keen means enthusiastic about doing something, which drafting a plan early shows; "
  "'reluctant' reverses it, and would not explain the early start.",
  "medium", 0.95),

 ("linger",
  "A few supporters lingered by the gate long after the players had gone home for the "
  "night.",
  "stay on",
  [("rush off", "opposite"), ("lunge at", "form"), ("give up", "domain")],
  "To linger is to remain somewhere longer than expected, which is what the supporters "
  "did; 'rush off' describes the opposite behaviour entirely.",
  "medium", 0.95),

 ("obstacle",
  "The main obstacle to the plan was the cost of moving the power lines underground.",
  "barrier",
  [("shortcut", "opposite"), ("spectacle", "form"), ("reward", "domain")],
  "An obstacle is something standing in the way of progress, which the cost clearly was; "
  "'spectacle' merely rhymes with it and means something worth watching.",
  "medium", 0.95),

 ("relish",
  "He tackled the toughest section of the course with obvious relish, grinning the whole "
  "way up.",
  "open enjoyment",
  [("clear reluctance", "opposite"), ("sharp flavour", "form"), ("quiet patience", "nuance")],
  "Relish here means evident enjoyment, which the grinning conveys; 'sharp flavour' is the "
  "condiment sense of the word and does not fit a person climbing a hill.",
  "medium", 0.93),

 ("uphold",
  "The tribunal chose to uphold the original decision after reviewing the video evidence "
  "twice.",
  "support",
  [("overturn", "opposite"), ("uplift", "form"), ("explain", "domain")],
  "To uphold a decision is to confirm and maintain it, which is what a tribunal does when "
  "it agrees; 'overturn' is precisely the outcome that did not happen.",
  "medium", 0.95),

 ("cease",
  "Drilling must cease within two hundred metres of the nesting colony throughout the "
  "spring.",
  "stop",
  [("start", "opposite"), ("seize", "form"), ("slow", "nuance")],
  "To cease is to come to an end, which a protection rule requires; 'slow' is the trap, "
  "since reducing the drilling would not satisfy a rule that halts it.",
  "medium", 0.94),

 ("earnest",
  "Her earnest appeal to the council persuaded even the members who had opposed the plan "
  "from the start.",
  "sincere",
  [("joking", "opposite"), ("eager", "nuance"), ("earthy", "form")],
  "Earnest means serious and heartfelt, which is what made the appeal persuasive; 'eager' "
  "describes keenness to act rather than depth of sincerity.",
  "hard", 0.91),

 ("affable",
  "The new coach is affable enough away from the field, though he expects total focus at "
  "training.",
  "easy to talk to",
  [("hard to approach", "opposite"), ("quick to anger", "nuance"), ("keen to impress", "domain")],
  "Affable means friendly and easy in company, which the contrast with his training manner "
  "sets up; 'quick to anger' describes the temper an affable person conspicuously lacks.",
  "medium", 0.93),

 ("bland",
  "The report was bland enough to pass without a single comment at the annual meeting.",
  "dull and plain",
  [("rich and tasty", "opposite"), ("brash and loud", "form"), ("kind and gentle", "domain")],
  "Bland means lacking strong character or interest, which is why nobody reacted; 'rich "
  "and tasty' is the food sense and reverses the meaning as well.",
  "hard", 0.91),
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
