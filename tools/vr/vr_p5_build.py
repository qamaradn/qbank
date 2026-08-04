#!/usr/bin/env python3
"""Builds vr_vic_acer_p5.json — 21 vocabulary-in-context questions (TASK §3.1)."""
import datetime
import json
import pathlib
import sys
import uuid

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/verbal_reasoning/generated"
NN = 5
BOOK = "vr_vic_acer"
CATEGORY = "vocabulary_synonym"
LABEL = "Vocabulary in context / synonyms"
NOW = datetime.datetime(2026, 8, 4, 14, 0, 0, tzinfo=datetime.timezone.utc) \
    .isoformat().replace("+00:00", "Z")

ITEMS = [
 ("gauge",
  "It is hard to gauge the depth of the channel from the bank, so the skipper sounded it "
  "first.",
  "judge",
  [("ignore", "opposite"), ("gouge", "form"), ("cross", "domain")],
  "To gauge something is to estimate or measure it, which is why the skipper checked; "
  "'gouge' looks and sounds close but means to cut a groove out of something.",
  "medium", 0.94),

 ("notify",
  "Skippers must notify the harbour master before moving a vessel out of the pens "
  "overnight.",
  "inform",
  [("mislead", "opposite"), ("nullify", "form"), ("consult", "nuance")],
  "To notify is to tell someone officially, which a reporting rule requires; 'consult' "
  "would mean seeking their advice, but the rule only asks that they be told.",
  "medium", 0.94),

 ("dainty",
  "The pardalote is a dainty bird, easily missed among the leaves of a tall eucalypt.",
  "small and delicate",
  [("large and sturdy", "opposite"), ("dingy and drab", "form"), ("rare and protected", "domain")],
  "Dainty means small and finely made, which explains why the bird is easily overlooked; "
  "'rare and protected' concerns its conservation status rather than its appearance.",
  "medium", 0.94),

 ("clarify",
  "The umpire stopped play to clarify the rule for both captains before the free kick was "
  "taken.",
  "make clear",
  [("muddle up", "opposite"), ("classify", "form"), ("read out", "nuance")],
  "To clarify is to remove confusion about something, which is why play stopped; 'read "
  "out' would mean simply reciting the rule, not explaining what it meant.",
  "medium", 0.94),

 ("condone",
  "The club made it plain it would not condone that kind of behaviour from any of its "
  "members.",
  "accept",
  [("condemn", "opposite"), ("condense", "form"), ("encourage", "overreach")],
  "To condone is to let something pass without objecting, which the club refused to do; "
  "'encourage' goes further still, since you can condone behaviour without promoting it.",
  "medium", 0.93),

 ("confide",
  "She would confide in her older sister long before she raised anything with her parents.",
  "trust with a secret",
  [("keep away from", "opposite"), ("confine to home", "form"), ("argue openly with", "domain")],
  "To confide in someone is to share something private with them, which the contrast with "
  "her parents sets up; 'confine to home' resembles the word but means restricting movement.",
  "medium", 0.93),

 ("deft",
  "One deft movement of the paddle turned the canoe before it reached the standing wave.",
  "skilful",
  [("clumsy", "opposite"), ("daft", "form"), ("sudden", "nuance")],
  "Deft means neatly and cleverly done, which saved the canoe; 'sudden' captures the speed "
  "of the movement but not the skill behind it.",
  "medium", 0.94),

 ("devise",
  "The students had to devise a way of getting the egg to the ground unbroken from six "
  "metres.",
  "work out",
  [("copy from", "opposite"), ("divide up", "form"), ("write down", "domain")],
  "To devise is to invent or plan something new, which the task demands; 'write down' "
  "describes recording a solution rather than coming up with one.",
  "medium", 0.94),

 ("dismay",
  "There was general dismay when the fixture was moved to the same weekend as the "
  "carnival.",
  "unhappy surprise",
  [("cheerful relief", "opposite"), ("dismal weather", "form"), ("quiet acceptance", "nuance")],
  "Dismay is the distress felt at unwelcome news, which a clashing fixture would cause; "
  "'quiet acceptance' would mean people took it calmly, which is the opposite reaction.",
  "medium", 0.93),

 ("aloof",
  "The new arrival stayed aloof for the first month, eating lunch away from the others.",
  "distant and reserved",
  [("warm and sociable", "opposite"), ("above the ground", "form"), ("busy and hurried", "domain")],
  "Aloof means keeping apart from other people, which eating alone illustrates; 'above the "
  "ground' is the nautical sense of the word and does not describe a person's manner.",
  "medium", 0.93),

 ("exempt",
  "Junior members are exempt from the working bee, though most of them turn up regardless.",
  "let off",
  [("bound by", "opposite"), ("attempt", "form"), ("banned from", "nuance")],
  "To be exempt is to be freed from a requirement others must meet, which the juniors are; "
  "'banned from' would mean they were not allowed to attend, yet many of them do.",
  "medium", 0.94),

 ("fickle",
  "The breeze was fickle all afternoon, swinging through ninety degrees between races.",
  "changeable",
  [("dependable", "opposite"), ("coastal", "domain"), ("gentle", "nuance")],
  "Fickle means liable to change without warning, which the swinging wind shows; 'gentle' "
  "describes the strength of the breeze, not its inconstancy.",
  "medium", 0.94),

 ("forfeit",
  "The side had to forfeit the match after failing to field the minimum number of players.",
  "give up",
  [("win back", "opposite"), ("protest", "domain"), ("postpone", "nuance")],
  "To forfeit is to lose something as a penalty for failing a condition, which is what "
  "happened; 'postpone' would mean the match was delayed rather than surrendered.",
  "medium", 0.94),

 ("fragile",
  "The shell middens along this stretch are fragile, and a single misplaced step can "
  "damage them.",
  "easily broken",
  [("hard to shift", "opposite"), ("fairly agile", "form"), ("rarely visited", "domain")],
  "Fragile means easily damaged, which is why a single step matters; 'rarely visited' "
  "explains why they survive but says nothing about how delicate they are.",
  "medium", 0.94),

 ("frank",
  "Her frank assessment of the season was not what the committee had expected to hear.",
  "honest and direct",
  [("guarded and vague", "opposite"), ("free of charge", "form"), ("brief and rushed", "nuance")],
  "Frank means saying plainly what you think, which is why it surprised the committee; "
  "'brief and rushed' describes length rather than candour, and a frank account can be long.",
  "medium", 0.93),

 ("gruff",
  "The old shearer had a gruff manner that the new hands found harder to read than it "
  "deserved.",
  "rough and abrupt",
  [("soft and gentle", "opposite"), ("tough and strong", "form"), ("cruel and unkind", "overreach")],
  "Gruff means rough or brusque in speech and manner, which is what the new hands "
  "misjudged; 'cruel and unkind' goes much further, and the sentence implies he was not.",
  "medium", 0.92),

 ("haphazard",
  "The stacking in the shed was haphazard, and nobody could find the spare fittings.",
  "without any order",
  [("carefully arranged", "opposite"), ("hazardous to walk", "form"), ("built up too high", "domain")],
  "Haphazard means done without plan or system, which is why nothing could be found; "
  "'hazardous to walk' picks up the middle of the word but means dangerous instead.",
  "medium", 0.93),

 ("immerse",
  "You need to immerse the bottle completely to get a clean sample from the creek.",
  "put right under",
  [("hold above", "opposite"), ("immense size", "form"), ("rinse briefly", "nuance")],
  "To immerse is to submerge something entirely in liquid, which 'completely' underlines; "
  "'rinse briefly' involves water but not the full covering the method needs.",
  "medium", 0.94),

 ("indulge",
  "Their grandfather would indulge them with a second ice-cream whenever their parents "
  "were out.",
  "give in to",
  [("hold back from", "opposite"), ("include with", "form"), ("bargain with", "domain")],
  "To indulge someone is to allow them something they want, especially more than is wise; "
  "'bargain with' would mean negotiating, but the treat was given freely.",
  "medium", 0.94),

 ("vex",
  "Small delays at the level crossing continued to vex commuters throughout the upgrade.",
  "annoy",
  [("please", "opposite"), ("vet", "form"), ("delay", "collocation")],
  "To vex is to irritate or trouble somebody, which repeated hold-ups do; 'delay' names "
  "the cause of the irritation rather than the feeling itself.",
  "hard", 0.92),

 ("solemn",
  "The dawn service is a solemn occasion, and the crowd stays silent until the last post "
  "ends.",
  "serious and grave",
  [("light and playful", "opposite"), ("quiet and still", "collocation"), ("sad and grieving", "nuance")],
  "Solemn means marked by deep seriousness, which the silence conveys; 'sad and grieving' "
  "is close but an occasion can be solemn without everyone present being in mourning.",
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
