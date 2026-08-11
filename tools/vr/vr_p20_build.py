#!/usr/bin/env python3
"""Builds vr_vic_acer_p20.json — 22 shades-of-meaning questions (TASK §3.7).

Two formats, roughly half each:

INTENSITY — the stem gives a word and the context demands a stronger or weaker one. The
trap is a 'synonym' distractor: right family, right direction, wrong strength.

CONNOTATION — two words describe the same behaviour but judge it differently. The trap is
again a synonym, this time carrying the opposite judgement to the one asked for.

These are the one category where a synonym distractor is correct design rather than a
second key, because the question asks about degree or attitude, not about meaning alone.
"""
import datetime
import json
import pathlib
import sys
import uuid

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/verbal_reasoning/generated"
NN = 20
BOOK = "vr_vic_acer"
CATEGORY = "shades_of_meaning"
LABEL = "Shades of meaning / connotation"
NOW = datetime.datetime(2026, 8, 4, 17, 0, 0, tzinfo=datetime.timezone.utc) \
    .isoformat().replace("+00:00", "Z")

# (target, stem, key, distractors, explanation, difficulty, confidence)
ITEMS = [
 ("pleased", "Winning the regional title left the side well past merely pleased. Which word describes their much stronger feeling?", "elated",
  [("content", "synonym"), ("dismayed", "opposite"), ("relieved", "nuance")],
  "Elated sits far above pleased on the same scale of happiness, which a title would justify; 'content' is a quieter form of pleased and adds no strength.", "medium", 0.93),
 ("sleepy", "By the third hour of the drive the children were well past sleepy. Which word describes the greater degree?", "comatose",
  [("drowsy", "synonym"), ("alert", "opposite"), ("restless", "collocation")],
  "Comatose is used loosely for sleep so deep nothing wakes you, well beyond sleepy; 'drowsy' means much the same as sleepy.", "medium", 0.91),
 ("chilly", "By four in the morning the tent was well past chilly. Which word puts it more strongly?", "freezing",
  [("cool", "synonym"), ("sweltering", "opposite"), ("damp", "collocation")],
  "Freezing is the extreme of the same scale that starts at chilly; 'cool' sits below chilly rather than above it.", "medium", 0.94),
 ("startled", "Nobody was merely startled when the result came through. Which word describes the much stronger reaction?", "astonished",
  [("puzzled", "nuance"), ("unmoved", "opposite"), ("amused", "collocation")],
  "Astonished is surprise taken to its extreme, which the sentence calls for; 'puzzled' is a different reaction rather than a stronger one.", "medium", 0.93),
 ("empty", "By the time they reached the hut their stomachs were far past empty. Which word carries the right force?", "ravenous",
  [("peckish", "nuance"), ("satisfied", "opposite"), ("thirsty", "collocation")],
  "Ravenous is hunger at its strongest, which a long walk would bring on; 'peckish' sits at the very bottom of the same scale.", "medium", 0.92),
 ("wet", "The jackets were well past wet by the time the rain eased. Which word names the stronger version?", "drenched",
  [("damp", "nuance"), ("parched", "opposite"), ("muddy", "domain")],
  "Drenched means thoroughly soaked, the strong end of the same scale; 'damp' is a lesser degree than wet, not a greater one.", "medium", 0.94),
 ("dislike", "She did not merely dislike the arrangement. Which word describes the much stronger feeling?", "detest",
  [("resent", "nuance"), ("admire", "opposite"), ("question", "collocation")],
  "To detest is to dislike intensely, which the sentence signals; 'resent' is a different feeling, bitterness at unfairness rather than sheer strength of dislike.", "medium", 0.92),
 ("request", "The letter did not merely request the money. Which word describes the much stronger act?", "demand",
  [("enquire", "nuance"), ("offer", "opposite"), ("post", "collocation")],
  "To demand is to ask with force behind it, which is a step up from a request; 'enquire' is gentler still, not stronger.", "medium", 0.93),
 ("laugh", "The whole room did more than laugh at the reply. Which word describes the much stronger reaction?", "roar",
  [("chuckle", "nuance"), ("groan", "opposite"), ("applaud", "collocation")],
  "To roar with laughter is laughter at full volume, which 'more than laugh' calls for; 'chuckle' is quieter than a laugh.", "medium", 0.93),
 ("look", "He did not merely look at the map before setting out. Which word describes the much closer attention?", "study",
  [("glance", "nuance"), ("ignore", "opposite"), ("fold", "collocation")],
  "To study something is to look at it long and carefully, which is more than a look; 'glance' is a briefer look, not a longer one.", "medium", 0.93),
 ("walk", "They did not walk the last stretch so much as move at speed. Which word describes the faster action?", "stride",
  [("amble", "nuance"), ("halt", "opposite"), ("navigate", "collocation")],
  "To stride is to walk with long, quick steps, which is faster than walking; 'amble' is a slower, more relaxed walk.", "medium", 0.92),
 ("shower", "It did not merely shower on the Saturday. Which word describes the much heavier fall?", "pour",
  [("drizzle", "nuance"), ("clear", "opposite"), ("flood", "overreach")],
  "To pour is rain at its heaviest, well beyond a shower; 'drizzle' is lighter than a shower rather than heavier.", "medium", 0.93),
 ("clean", "The bench was not merely clean when he had finished. Which of these is the stronger word?", "spotless",
  [("tidy", "nuance"), ("filthy", "opposite"), ("varnished", "collocation")],
  "Spotless means completely without mark, the top of the same scale; 'tidy' describes order rather than a greater degree of cleanliness.", "medium", 0.93),
 ("old", "The map they were using was not merely old. Which word describes the much greater age?", "ancient",
  [("dated", "nuance"), ("modern", "opposite"), ("folded", "collocation")],
  "Ancient is age taken to its extreme, well beyond old; 'dated' means merely out of fashion.", "medium", 0.94),
 ("bright", "The light off the salt pan was not merely bright. Which word describes the greater degree?", "dazzling",
  [("lit", "nuance"), ("dim", "opposite"), ("white", "collocation")],
  "Dazzling is brightness strong enough to hurt the eyes, which a salt pan produces; 'lit' merely means not dark.", "medium", 0.93),
 ("small", "The room they were given was not merely small. Which word puts it more strongly?", "cramped",
  [("compact", "nuance"), ("spacious", "opposite"), ("bare", "domain")],
  "Cramped means small enough to be uncomfortable, which is a step beyond small; 'compact' is a favourable word for small and softens rather than strengthens it.", "medium", 0.93),
 ("interested", "The committee was not merely interested in the offer. Which word describes the much stronger response?", "enthusiastic",
  [("curious", "nuance"), ("indifferent", "opposite"), ("cautious", "collocation")],
  "Enthusiastic is interest at its warmest, which the sentence asks for; 'curious' is a milder form of interest.", "medium", 0.93),
 ("angry", "The letter that followed was not merely angry. Which word describes the much stronger tone?", "scathing",
  [("cross", "nuance"), ("gracious", "opposite"), ("formal", "collocation")],
  "Scathing describes anger expressed with cutting force, well beyond angry; 'cross' is a milder word for annoyed.", "medium", 0.92),
 ("difficult", "The final section was not merely difficult. Which word carries the right force?", "gruelling",
  [("tricky", "nuance"), ("effortless", "opposite"), ("steep", "collocation")],
  "Gruelling means punishingly hard over a sustained period, beyond merely difficult; 'tricky' is a lighter word for awkward.", "medium", 0.93),
 ("busy", "The market on the Saturday was not merely busy. Which word names the stronger version?", "heaving",
  [("active", "nuance"), ("deserted", "opposite"), ("covered", "collocation")],
  "Heaving describes a place packed to overflowing, well past busy; 'active' is a weaker word than busy.", "medium", 0.92),
 ("quiet", "The house at that hour was not merely quiet. Which of these is the stronger word?", "silent",
  [("hushed", "nuance"), ("noisy", "opposite"), ("empty", "domain")],
  "Silent means no sound at all, the extreme of the scale; 'hushed' is quiet with sound still present.", "medium", 0.93),
 ("worried", "By the third hour the family were not merely worried. Which word describes the much stronger state?", "frantic",
  [("uneasy", "nuance"), ("calm", "opposite"), ("weary", "collocation")],
  "Frantic is worry that has become uncontrolled, which three hours would build to; 'uneasy' is a milder state than worried.", "medium", 0.94),
 ("dirty", "The overalls that came back were not merely dirty. Which word describes the greater degree?", "filthy",
  [("marked", "nuance"), ("spotless", "opposite"), ("torn", "domain")],
  "Filthy is dirt at its worst, above dirty on the same scale; 'marked' means carrying a few stains and is weaker.", "medium", 0.94),
 ("windy", "The conditions on the point were not merely windy. Which word puts it more strongly?", "gale-force",
  [("breezy", "nuance"), ("still", "opposite"), ("cloudy", "domain")],
  "Gale-force names wind at its strongest, well beyond windy; 'breezy' is lighter than windy rather than heavier.", "medium", 0.93),
 ("proud", "Her parents were not merely proud when the results came out. Which word describes the much stronger feeling?", "overjoyed",
  [("satisfied", "nuance"), ("ashamed", "opposite"), ("surprised", "domain")],
  "Overjoyed is delight at its fullest, which results day can produce; 'satisfied' is a quieter feeling than proud.", "medium", 0.93),
 ("crowded", "The last carriage was not merely crowded. Which word carries the right force?", "packed",
  [("occupied", "nuance"), ("empty", "opposite"), ("delayed", "domain")],
  "Packed means filled to capacity, beyond crowded; 'occupied' means only that people are in it.", "medium", 0.93),
 ("scared", "The dog was not merely scared of the thunder. Which word describes the much stronger state?", "terrified",
  [("wary", "nuance"), ("fearless", "opposite"), ("noisy", "domain")],
  "Terrified is fear at its strongest, which a storm can produce in a dog; 'wary' is caution rather than fear.", "medium", 0.94),
 ("expensive", "The quote that came back was not merely expensive. Which word names the stronger version?", "exorbitant",
  [("costly", "synonym"), ("cheap", "opposite"), ("itemised", "domain")],
  "Exorbitant means priced far beyond what is reasonable, above expensive; 'costly' is simply another word for expensive.", "hard", 0.91),
 ("damp", "The walls in the back room were not merely damp. Which of these is the stronger word?", "sodden",
  [("moist", "nuance"), ("parched", "opposite"), ("stained", "domain")],
  "Sodden means soaked right through, the far end of the same scale; 'moist' is a lesser degree than damp, not a greater one.", "medium", 0.92),
 ("strange", "The noise from the roof cavity was not merely strange. Which word describes the greater degree?", "eerie",
  [("unusual", "nuance"), ("familiar", "opposite"), ("faint", "domain")],
  "Eerie is strangeness that unsettles, a step beyond strange; 'unusual' is milder than strange.", "medium", 0.92),
 ("sad", "The mood in the rooms afterwards was not merely sad. Which word puts it more strongly?", "desolate",
  [("subdued", "nuance"), ("joyful", "opposite"), ("silent", "domain")],
  "Desolate is sadness at its bleakest, which a heavy defeat can leave; 'subdued' is a quieter, milder state.", "medium", 0.92),
 ("plucky", "What she did that afternoon was not merely plucky. Which word carries the right force?", "heroic",
  [("bold", "nuance"), ("cowardly", "opposite"), ("sudden", "domain")],
  "Heroic is courage of an exceptional order, well above plucky; 'bold' describes confidence rather than a greater courage.", "medium", 0.92),
 ("funny", "The second half of the act was not merely funny. Which word names the stronger version?", "hilarious",
  [("amusing", "nuance"), ("dull", "opposite"), ("rehearsed", "domain")],
  "Hilarious is funniness at its strongest; 'amusing' is milder than funny rather than stronger.", "medium", 0.94),
 ("important", "The decision taken that night was not merely important. Which of these is the stronger word?", "momentous",
  [("relevant", "nuance"), ("trivial", "opposite"), ("unanimous", "domain")],
  "Momentous means important enough to shape what follows, above important; 'relevant' means only that it bears on the matter.", "medium", 0.92),
 ("hot", "The cabin by mid-afternoon was not merely hot. Which word describes the greater degree?", "stifling",
  [("mild", "nuance"), ("frigid", "opposite"), ("dusty", "domain")],
  "Stifling describes heat so close it is hard to breathe, well past hot; 'mild' sits below hot on the scale.", "medium", 0.93),
]


def build():
    out = []
    for target, stem, key, distractors, expl, diff, conf in ITEMS:
        opts = [key] + [d for d, _ in distractors]
        out.append({
            "id": str(uuid.uuid4()),
            "subject": "verbal_reasoning",
            "stem": stem,
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
