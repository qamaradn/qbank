#!/usr/bin/env python3
"""Builds vr_vic_acer_p9.json — 10 word-group classification questions (TASK §3.3).

The signature ACER item, and the one category where a coherent distractor bloc is the
design rather than the defect. A student who pattern-matches on "which three go together"
picks a distractor, because the three distractors form their own tidy group and the key
is the word that joins the group named in the stem.

That is why word_group is exempt from distractor_relation_errors and instead requires
every distractor to be declared 'domain' — see tools/vr_finalise.word_group_errors.

The briefing's own example (miserly / stingy / parsimonious -> frugal) is deliberately not
reused: it is quoted from a student's account of the real paper, so it is source material
rather than something to copy.
"""
import datetime
import json
import pathlib
import sys
import uuid

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/verbal_reasoning/generated"
NN = 9
BOOK = "vr_vic_acer"
CATEGORY = "word_group"
LABEL = "Word-group classification"
NOW = datetime.datetime(2026, 8, 4, 18, 0, 0, tzinfo=datetime.timezone.utc) \
    .isoformat().replace("+00:00", "Z")

# (theme, stem, group_words, key, decoys, explanation, difficulty, confidence)
ITEMS = [
 ("precipitation",
  "The words drizzle, sleet and hail have something in common. Which word below belongs "
  "with them?",
  ["drizzle", "sleet", "hail"], "downpour", ["gale", "breeze", "gust"],
  "All three are forms of precipitation, and a downpour is another; the other options are "
  "all kinds of wind, which is why they look like a set of their own.",
  "medium", 0.94),

 ("strings",
  "Violin, cello and viola form a group. Which of these joins that group?",
  ["violin", "cello", "viola"], "double bass", ["trumpet", "trombone", "tuba"],
  "All three are bowed string instruments, and the double bass is the fourth; the "
  "remaining options are brass instruments and form a tidy group without the answer.",
  "medium", 0.95),

 ("flightless",
  "Consider these three birds: emu, cassowary and kiwi. Which word fits with them?",
  ["emu", "cassowary", "kiwi"], "ostrich", ["eagle", "falcon", "hawk"],
  "All three are flightless birds, as the ostrich is; the other options are all birds of "
  "prey that fly, so they group together and exclude the answer.",
  "medium", 0.95),

 ("metals",
  "Copper, silver and zinc share a property. Which word shares it too?",
  ["copper", "silver", "zinc"], "nickel", ["ruby", "sapphire", "opal"],
  "All three are metals, and nickel is another; the other options are gemstones, which "
  "form their own group and tempt anyone matching on the majority.",
  "medium", 0.94),

 ("poems",
  "Sonnet, haiku and limerick are all of one kind. Which word is of that kind as well?",
  ["sonnet", "haiku", "limerick"], "ode", ["novel", "essay", "memoir"],
  "All three are verse forms, and an ode is another; the other options are prose forms "
  "and sit together as a group of their own.",
  "medium", 0.94),

 ("polygons",
  "What do triangle, pentagon and octagon have in common? Which word below has it too?",
  ["triangle", "pentagon", "octagon"], "hexagon", ["cube", "sphere", "cylinder"],
  "All three are flat shapes with straight sides, as a hexagon is; the other options are "
  "three-dimensional solids and form an obvious group without the answer.",
  "medium", 0.95),

 ("paddling",
  "Rowing, sailing and kayaking belong together. Which word joins them?",
  ["rowing", "sailing", "kayaking"], "canoeing", ["sprinting", "hurdling", "vaulting"],
  "All three are sports done on the water in a craft, as canoeing is; the other options "
  "are athletics events and group neatly together on land.",
  "medium", 0.94),

 ("herbs",
  "Basil, thyme and oregano are members of one group. Which word is also a member?",
  ["basil", "thyme", "oregano"], "rosemary", ["cinnamon", "nutmeg", "clove"],
  "All three are leafy herbs, and rosemary is another; the other options are spices taken "
  "from bark, seed and flower bud, so they form their own group.",
  "hard", 0.91),

 ("planets",
  "Mercury, Venus and Mars are alike in one way. Which word is alike in the same way?",
  ["mercury", "venus", "mars"], "earth", ["titan", "europa", "callisto"],
  "All three are rocky planets orbiting the Sun, as Earth is; the other options are moons "
  "of other planets, which makes them look like the real set.",
  "hard", 0.91),

 ("grammar",
  "Adjective, adverb and pronoun form a set. Which word completes that set?",
  ["adjective", "adverb", "pronoun"], "preposition", ["comma", "colon", "dash"],
  "All three are parts of speech, and a preposition is another; the other options are "
  "punctuation marks and group together without belonging to the set in the question.",
  "medium", 0.93),
]


def build():
    out = []
    for theme, stem, group_words, key, decoys, expl, diff, conf in ITEMS:
        opts = [key] + decoys
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
            "target_word": theme,
            "group_words": group_words,
            # All decoys are declared 'domain': they belong to one coherent category of
            # their own. That uniformity is required here, not rejected.
            "relations": {d: "domain" for d in decoys},
        })
    return out


if __name__ == "__main__":
    GEN.mkdir(parents=True, exist_ok=True)
    qs = build()
    path = GEN / f"{BOOK}_p{NN}.json"
    path.write_text(json.dumps(qs, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(qs)} questions -> {path}")
