#!/usr/bin/env python3
"""Builds vr_vic_acer_p8.json — 22 shades-of-meaning questions (TASK §3.7).

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
NN = 8
BOOK = "vr_vic_acer"
CATEGORY = "shades_of_meaning"
LABEL = "Shades of meaning / connotation"
NOW = datetime.datetime(2026, 8, 4, 17, 0, 0, tzinfo=datetime.timezone.utc) \
    .isoformat().replace("+00:00", "Z")

# (target, stem, key, distractors, explanation, difficulty, confidence)
ITEMS = [
 ("annoyed",
  "After three hours waiting in the rain, the supporters were well past being merely "
  "annoyed. Which word best describes their much stronger feeling?",
  "furious",
  [("irritated", "synonym"), ("delighted", "opposite"), ("anxious", "domain")],
  "Furious sits well above annoyed on the same scale of anger, which three hours in the "
  "rain would justify; 'irritated' is simply another word for annoyed and adds no strength.",
  "medium", 0.93),

 ("warm",
  "The soup had been left on the stove far too long and was no longer merely warm. Which "
  "word describes the greater degree of heat?",
  "scalding",
  [("heated", "synonym"), ("chilled", "opposite"), ("simmering", "nuance")],
  "Scalding is far hotter than warm and sits at the top of the same scale; 'heated' means "
  "much the same as warm and does not register the increase.",
  "medium", 0.94),

 ("surprised",
  "She was not just surprised by the result — she could hardly take it in. Which word "
  "describes the stronger reaction?",
  "astounded",
  [("startled", "synonym"), ("unmoved", "opposite"), ("confused", "nuance")],
  "Astounded describes shock so great it is hard to absorb, which the sentence spells "
  "out; 'startled' is a brief jolt and sits no higher than surprised.",
  "medium", 0.93),

 ("tired",
  "By the last kilometre the walkers were more than tired; several could barely lift their "
  "feet. Which word describes that greater state?",
  "exhausted",
  [("weary", "synonym"), ("refreshed", "opposite"), ("thirsty", "domain")],
  "Exhausted means completely drained of energy, which barely lifting your feet describes; "
  "'weary' is close to tired and does not mark the step up.",
  "medium", 0.94),

 ("cold",
  "The wind off the ice was beyond cold, and exposed skin stung within seconds. Which word "
  "captures that extreme?",
  "bitter",
  [("cool", "synonym"), ("mild", "opposite"), ("gusty", "collocation")],
  "Bitter cold is severe enough to hurt, which stinging skin confirms; 'cool' is milder "
  "than cold, so it moves down the scale rather than up.",
  "medium", 0.94),

 ("like",
  "He did not merely like the sport — he organised his whole week around it. Which word "
  "describes the stronger feeling?",
  "adore",
  [("enjoy", "synonym"), ("resent", "opposite"), ("watch", "collocation")],
  "To adore is to feel devotion well beyond liking, which reorganising a week demonstrates; "
  "'enjoy' sits at about the same level as like and marks no increase.",
  "medium", 0.93),

 ("rain",
  "It was not the light rain that had been forecast; the gutters overflowed within "
  "minutes. Which word describes what actually fell?",
  "downpour",
  [("shower", "synonym"), ("drizzle", "nuance"), ("forecast", "domain")],
  "A downpour is heavy enough to overwhelm gutters, which is what happened; 'shower' is a "
  "brief light fall and matches the forecast that proved wrong.",
  "medium", 0.94),

 ("ask",
  "She did not simply ask for the equipment back — she asked again and again until it "
  "arrived. Which word describes that persistence?",
  "demand",
  [("request", "synonym"), ("offer", "opposite"), ("whisper", "domain")],
  "To demand carries the force and insistence the repetition shows; 'request' is a polite "
  "equivalent of ask and loses that insistence entirely.",
  "medium", 0.92),

 ("big",
  "The fig in the schoolyard is not just big; its canopy covers half the oval. Which word "
  "best conveys that scale?",
  "colossal",
  [("large", "synonym"), ("tiny", "opposite"), ("leafy", "collocation")],
  "Colossal describes something enormous, which a canopy covering half an oval is; "
  "'large' means much the same as big and does not convey the scale.",
  "medium", 0.94),

 ("upset",
  "He was more than upset when the news came through; he could not speak for some minutes. "
  "Which word describes that stronger state?",
  "devastated",
  [("bothered", "synonym"), ("cheered", "opposite"), ("informed", "domain")],
  "Devastated describes being overwhelmed by distress, which being unable to speak "
  "conveys; 'bothered' is milder than upset, not stronger.",
  "medium", 0.94),

 ("hungry",
  "By the time the bus reached Bendigo the children were beyond hungry. Which word "
  "describes that greater need?",
  "famished",
  [("peckish", "synonym"), ("full", "opposite"), ("restless", "nuance")],
  "Famished means extremely hungry, which a long trip without food would produce; "
  "'peckish' means only slightly hungry and sits below the target rather than above it.",
  "medium", 0.94),

 ("stubborn",
  "A person who refuses to change their mind can be called stubborn. Which word describes that same trait but treats it as a strength?",
  "determined",
  [("obstinate", "synonym"), ("agreeable", "opposite"), ("forgetful", "domain")],
  "Determined praises persistence, while stubborn criticises it, though both describe the "
  "same behaviour; 'obstinate' carries the same disapproval as stubborn.",
  "medium", 0.93),

 ("nosy",
  "Someone who asks a great many questions might be dismissed as nosy. Which word puts that same habit in a favourable light?",
  "curious",
  [("prying", "synonym"), ("incurious", "opposite"), ("talkative", "domain")],
  "Curious treats the questioning as healthy interest, while nosy treats it as "
  "intrusion; 'prying' carries the same disapproval that nosy does.",
  "medium", 0.94),

 ("skinny",
  "A very slight build is sometimes described as skinny. Which word conveys the same build as an attractive feature?",
  "slender",
  [("scrawny", "synonym"), ("stout", "opposite"), ("athletic", "nuance")],
  "Slender is complimentary where skinny is not, though both describe the same build; "
  "'scrawny' is, if anything, less flattering than skinny.",
  "medium", 0.93),

 ("cheap",
  "Goods that cost very little are often called cheap. Which word notes the low price without hinting at poor quality?",
  "affordable",
  [("shoddy", "synonym"), ("costly", "opposite"), ("imported", "domain")],
  "Affordable praises the low price, while cheap often hints at poor quality; 'shoddy' "
  "makes that criticism explicit and is not about price at all.",
  "medium", 0.93),

 ("childish",
  "Behaviour typical of a young child may be labelled childish. Which word describes it warmly instead?",
  "childlike",
  [("immature", "synonym"), ("grown-up", "opposite"), ("noisy", "collocation")],
  "Childlike suggests innocence and wonder, while childish is a criticism; 'immature' "
  "carries the same disapproval that childish does.",
  "hard", 0.90),

 ("bossy",
  "A person who tells everyone else what to do is often called bossy. Which word treats that same habit as leadership?",
  "assertive",
  [("domineering", "synonym"), ("timid", "opposite"), ("popular", "domain")],
  "Assertive treats the behaviour as confident leadership, while bossy treats it as "
  "overbearing; 'domineering' is harsher than bossy rather than kinder.",
  "medium", 0.93),

 ("reckless",
  "Someone who takes very large risks may be called reckless. Which word admires that same behaviour?",
  "daring",
  [("foolhardy", "synonym"), ("cautious", "opposite"), ("skilful", "nuance")],
  "Daring admires the courage in taking a risk, while reckless condemns the carelessness; "
  "'foolhardy' is a sharper version of the same criticism.",
  "medium", 0.93),

 ("odd",
  "Something quite unlike anything else is sometimes called odd. Which word treats that difference as a virtue?",
  "distinctive",
  [("peculiar", "synonym"), ("ordinary", "opposite"), ("rare", "nuance")],
  "Distinctive treats the difference as a virtue, while odd hints at something wrong; "
  "'peculiar' leans further towards that same suspicion.",
  "medium", 0.93),

 ("thrifty",
  "A person careful with money is often praised as thrifty. Which word presents that same care as a fault?",
  "miserly",
  [("economical", "synonym"), ("wasteful", "opposite"), ("wealthy", "domain")],
  "Miserly condemns the carefulness as meanness, while thrifty approves of it; "
  "'economical' shares thrifty's approval instead of reversing it.",
  "medium", 0.93),

 ("confident",
  "Someone sure of their own ability is described as confident. Which word turns that same self-belief into a criticism?",
  "arrogant",
  [("assured", "synonym"), ("unsure", "opposite"), ("talented", "nuance")],
  "Arrogant treats the self-belief as excessive, while confident treats it as healthy; "
  "'assured' is a near-equivalent of confident and keeps the approval.",
  "medium", 0.93),

 ("talkative",
  "A person who says a great deal is called talkative. Which word makes that same quality sound like a fault?",
  "long-winded",
  [("chatty", "synonym"), ("silent", "opposite"), ("friendly", "collocation")],
  "Long-winded complains that the talking goes on too long, while talkative is broadly "
  "neutral; 'chatty' is, if anything, warmer than talkative.",
  "hard", 0.90),
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
