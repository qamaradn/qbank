#!/usr/bin/env python3
"""Builds vr_vic_acer_p10.json — 30 vocabulary-in-context questions (TASK §3.1).

First batch of the ~341-item top-up in vic_content_taxonomy_TASK.md §5.3. The mix is
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
NN = 10
BOOK = "vr_vic_acer"
CATEGORY = "vocabulary_synonym"
LABEL = "Vocabulary in context / synonyms"
NOW = datetime.datetime(2026, 8, 11, 10, 0, 0, tzinfo=datetime.timezone.utc) \
    .isoformat().replace("+00:00", "Z")

# (target, stem, key, [(distractor, relation) x3], explanation, difficulty, confidence)
ITEMS = [
 ("abrupt",
  "The coach's abrupt change of tactics at half-time left half the side unsure where they "
  "were meant to stand.",
  "sudden",
  [("gradual", "opposite"), ("abrasive", "form"), ("tactical", "domain")],
  "An abrupt change is one that arrives without warning, which is why the players had no "
  "time to adjust; 'abrasive' sounds similar and describes a manner rather than a speed.",
  "medium", 0.94),

 ("bolster",
  "A second sponsor was found late in the season to bolster the club's dwindling funds.",
  "strengthen",
  [("replace", "nuance"), ("drain", "opposite"), ("audit", "domain")],
  "To bolster something is to prop it up and make it stronger, so the funds were added to "
  "rather than swapped out; 'replace' would mean the old money was removed.",
  "medium", 0.95),

 ("candid",
  "In a candid interview after the loss, the captain admitted the team had stopped "
  "listening to each other.",
  "frank",
  [("guarded", "opposite"), ("candied", "form"), ("televised", "domain")],
  "A candid interview is an unusually honest one, which fits an admission of failure; "
  "'guarded' describes the careful, revealing-nothing answer she did not give.",
  "medium", 0.95),

 ("commend",
  "The principal took a moment at assembly to commend the students who had stayed behind "
  "to clean up after the fair.",
  "praise",
  [("reward", "nuance"), ("reprimand", "opposite"), ("comment", "form")],
  "To commend someone is to praise them publicly, which is what an assembly mention is; "
  "'reward' implies they were given something, and nothing was handed over.",
  "medium", 0.94),

 ("concise",
  "Marks were lost for rambling, so the teacher asked for answers that were concise and "
  "still complete.",
  "brief",
  [("precise", "form"), ("rambling", "opposite"), ("handwritten", "domain")],
  "Concise means saying it in few words, which is the opposite of the rambling that cost "
  "marks; 'precise' sounds almost the same but means accurate rather than short.",
  "medium", 0.94),

 ("conspicuous",
  "In a room full of dark uniforms his yellow jacket was conspicuous from the doorway.",
  "noticeable",
  [("hidden", "opposite"), ("conscious", "form"), ("waterproof", "domain")],
  "Something conspicuous stands out and is easily seen, which is why the jacket was "
  "spotted at once; 'hidden' describes the effect the dark uniforms had instead.",
  "medium", 0.95),

 ("crucial",
  "Getting the soil temperature right is crucial when planting seedlings this late in the "
  "season.",
  "vital",
  [("helpful", "nuance"), ("optional", "opposite"), ("crucible", "form")],
  "Crucial means the thing everything else depends on, which is stronger than merely "
  "useful; 'helpful' would suggest the planting could succeed without it.",
  "medium", 0.94),

 ("dawdle",
  "We would have caught the earlier ferry if the two of you had not dawdled at the kiosk.",
  "linger",
  [("hurry", "opposite"), ("doodle", "form"), ("queue", "collocation")],
  "To dawdle is to move more slowly than you should, which is why the ferry was missed; "
  "'queue' is something you do at a kiosk but says nothing about being slow.",
  "medium", 0.93),

 ("deficient",
  "Soil tests showed the paddock was deficient in nitrogen, which explained the pale "
  "growth along the fence line.",
  "lacking",
  [("rich", "opposite"), ("defiant", "form"), ("irrigated", "domain")],
  "To be deficient in something is to have too little of it, which is why the growth was "
  "pale; 'rich' describes soil with plenty and would not explain the problem.",
  "medium", 0.94),

 ("deteriorate",
  "The track begins to deteriorate past the second gate, so most drivers turn back there.",
  "worsen",
  [("improve", "opposite"), ("determine", "form"), ("narrow", "nuance")],
  "To deteriorate is to get steadily worse, which is why drivers stop; 'narrow' describes "
  "a track that is merely thinner and might still be in good condition.",
  "medium", 0.94),

 ("diligent",
  "Her diligent note-taking through the whole term meant she barely needed to revise.",
  "industrious",
  [("careless", "opposite"), ("diligence", "form"), ("legible", "nuance")],
  "Diligent means steadily and carefully industrious, which is what made revision "
  "unnecessary; 'legible' describes neat handwriting rather than sustained effort.",
  "medium", 0.94),

 ("dubious",
  "He was dubious about the shortcut, having been led down it once before.",
  "doubtful",
  [("certain", "opposite"), ("durable", "form"), ("lost", "collocation")],
  "Dubious means unconvinced, which fits somebody burnt by the same shortcut before; "
  "'lost' is what might happen next but is not what the word describes.",
  "medium", 0.94),

 ("elicit",
  "No amount of gentle questioning could elicit an explanation from either of them.",
  "draw out",
  [("suppress", "opposite"), ("illicit", "form"), ("interrogate", "nuance")],
  "To elicit is to succeed in getting a response out of somebody, which is exactly what "
  "failed here; 'interrogate' describes the questioning itself rather than its result.",
  "hard", 0.92),

 ("evade",
  "The minister managed to evade the question three times before the interview ended.",
  "avoid",
  [("confront", "opposite"), ("invade", "form"), ("broadcast", "domain")],
  "To evade a question is to get around answering it, which is what repeating the dodge "
  "three times shows; 'confront' would mean tackling it head on.",
  "medium", 0.95),

 ("feeble",
  "The torch gave off a feeble light that barely reached the end of the tent.",
  "weak",
  [("dazzling", "opposite"), ("flexible", "form"), ("battery", "collocation")],
  "Feeble means lacking strength, which is why the beam fell short; 'battery' is a word "
  "that often turns up beside torches but describes a part, not the light's quality.",
  "medium", 0.95),

 ("fluctuate",
  "Prices at the market fluctuate through the season, so the same box costs quite "
  "different amounts in March and August.",
  "vary",
  [("steady", "opposite"), ("fluster", "form"), ("collapse", "nuance")],
  "To fluctuate is to keep moving up and down, which is why the price differs by month; "
  "'collapse' would mean a single sharp fall rather than repeated change.",
  "medium", 0.94),

 ("formidable",
  "By the final term the debating team had become a formidable side that no school "
  "wanted to draw.",
  "daunting",
  [("harmless", "opposite"), ("formal", "form"), ("articulate", "domain")],
  "Formidable means impressive enough to worry an opponent, which is why nobody wanted "
  "the draw; 'articulate' is a fair description of debaters but not what the word means.",
  "medium", 0.94),

 ("frail",
  "The frail wooden jetty had been closed since the storm and nobody expected it to be "
  "repaired.",
  "fragile",
  [("sturdy", "opposite"), ("frayed", "form"), ("coastal", "domain")],
  "Frail means weak and easily broken, which is why the jetty was shut; 'frayed' sounds "
  "similar but describes rope or fabric coming apart at the edges.",
  "medium", 0.94),

 ("grasp",
  "It took most of the lesson before the class began to grasp why the two answers were "
  "the same.",
  "understand",
  [("misjudge", "opposite"), ("gasp", "form"), ("memorise", "nuance")],
  "To grasp an idea is to take hold of it mentally, which is what took the lesson; "
  "'memorise' would mean learning the answer without seeing why it worked.",
  "medium", 0.94),

 ("hesitant",
  "She was hesitant to put her hand up, even though she was fairly sure of the answer.",
  "reluctant",
  [("eager", "opposite"), ("hesitate", "form"), ("mistaken", "nuance")],
  "Hesitant describes holding back rather than being wrong, which is why the passage "
  "says she was fairly sure; 'mistaken' would mean her answer was incorrect.",
  "medium", 0.94),

 ("impede",
  "Fallen branches across the trail impede walkers for about a kilometre after the bend.",
  "obstruct",
  [("assist", "opposite"), ("impale", "form"), ("exhaust", "nuance")],
  "To impede is to get in the way and slow progress, which is what branches on a trail "
  "do; 'exhaust' describes how the walker feels rather than what the branches do.",
  "medium", 0.94),

 ("inevitable",
  "Once the third player was injured, the loss felt inevitable to everyone in the stands.",
  "unavoidable",
  [("preventable", "opposite"), ("inevitably", "form"), ("humiliating", "nuance")],
  "Inevitable means certain to happen whatever anyone does, which is why the crowd gave "
  "up hope; 'humiliating' describes how bad the loss felt, not that it was certain.",
  "medium", 0.95),

 ("intricate",
  "The intricate pattern on the shield had taken the artist most of a year to complete.",
  "elaborate",
  [("plain", "opposite"), ("intricacy", "form"), ("painted", "domain")],
  "Intricate means made of many fine, connected parts, which is why it took a year; "
  "'painted' may well be true of the shield but says nothing about complexity.",
  "medium", 0.94),

 ("lament",
  "Older members of the club still lament the sale of the original ground.",
  "mourn",
  [("celebrate", "opposite"), ("lamentable", "form"), ("dispute", "nuance")],
  "To lament something is to express sorrow at its loss, which fits a ground sold long "
  "ago; 'dispute' would mean they were still arguing that the sale was wrong.",
  "medium", 0.94),

 ("meagre",
  "A meagre crowd of about forty turned out for the twilight match.",
  "scanty",
  [("vast", "opposite"), ("eager", "form"), ("chilly", "domain")],
  "Meagre means far less than expected or needed, which is what forty people at a match "
  "is; 'chilly' is plausible at twilight but describes the weather, not the number.",
  "medium", 0.94),

 ("obscure",
  "Low cloud began to obscure the summit just as the group reached the last ridge.",
  "hide",
  [("reveal", "opposite"), ("obscene", "form"), ("chill", "domain")],
  "To obscure something is to block it from view, which is what low cloud does to a "
  "summit; 'reveal' is the opposite and would mean the view had opened up.",
  "medium", 0.95),

 ("persist",
  "If the rattle persists after the service, bring the car back and we will look again.",
  "continue",
  [("cease", "opposite"), ("insist", "form"), ("worsen", "nuance")],
  "To persist is to keep going, which is the condition for bringing the car back; "
  "'worsen' would mean the rattle had to get louder, which the mechanic did not say.",
  "medium", 0.94),

 ("plausible",
  "His explanation for the missing key was plausible, but nobody could check it.",
  "believable",
  [("absurd", "opposite"), ("applaud", "form"), ("proven", "nuance")],
  "Plausible means it sounds like it could be true, which is why it still needed "
  "checking; 'proven' would mean it had already been shown to be correct.",
  "medium", 0.95),

 ("prudent",
  "It seemed prudent to fill the water tanks before the long weekend rather than after.",
  "sensible",
  [("reckless", "opposite"), ("prude", "form"), ("plumbed", "domain")],
  "Prudent describes a decision that shows good forward thinking, which filling tanks "
  "early is; 'reckless' names the careless choice the family avoided.",
  "medium", 0.95),

 ("scrutinise",
  "The umpires scrutinise the footage frame by frame before overturning a decision.",
  "examine",
  [("glance at", "opposite"), ("scrounge", "form"), ("overturn", "collocation")],
  "To scrutinise is to look at something very closely, which frame-by-frame review is; "
  "'overturn' appears in the same sentence but is the outcome, not the looking.",
  "medium", 0.94),
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
