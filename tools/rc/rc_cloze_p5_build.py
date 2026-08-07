#!/usr/bin/env python3
"""Builds rc_nsw_cloze_p5.json — 2 cloze passages x 8 blanks = 16 questions, taking the
§5 set from 120 to the taxonomy target of 136 (17 passages).

Same rules as rc_cloze_p1_build.py. Two text types the first fifteen passages under-serve:
one persuasive, one informational-scientific. Each blank was written so that exactly one
option reads — the only test that catches a second defensible answer is substituting the
keys back into the passage and reading it straight through.
"""
import datetime
import json
import pathlib
import re
import sys
import uuid

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.rc.rc_cloze_p1_build import context  # noqa: E402

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/reading_comprehension/generated"
NN = 5
BOOK = "rc_nsw_cloze"
CATEGORY = "vocabulary_cloze"
LABEL = "Vocabulary cloze"
NOW = datetime.datetime(2026, 8, 7, 12, 0, 0, tzinfo=datetime.timezone.utc) \
    .isoformat().replace("+00:00", "Z")

BLANK_RE = re.compile(r"_{2,} \((\d+)\) _{2,}")

PASSAGES = [
 {
  "title": "The Case for Walking",
  "topic": "Opinion",
  "text":
    "Fifty years ago most Australian children walked or rode to school. Today around one "
    "in five does. The change was not a decision anybody made; it ___ (1) ___ slowly, one "
    "cautious family at a time, until the short trip by car became the ordinary thing and "
    "walking became the exception.\n\n"
    "The usual explanation is traffic, and there is something circular about it. Parents "
    "drive because the roads near the school feel dangerous, and the roads near the school "
    "feel dangerous largely because of the ___ (2) ___ of cars arriving at ten to nine. Each "
    "family acts sensibly and the result is a problem none of them wanted.\n\n"
    "What is lost is easy to ___ (3) ___. A walk of fifteen minutes is exercise that "
    "requires no equipment, no fee and no timetable. It is also, for many children, the only "
    "part of the day that is not ___ (4) ___ by an adult standing a few metres away. "
    "Children who walk arrive knowing "
    "which dog barks at the corner and which crossing has the slow light, and that knowledge "
    "is what makes a suburb ___ (5) ___ rather than a place you are driven through.\n\n"
    "None of this means every family can walk. Some live too far out, and some parents "
    "leave for work before the bell. The argument is not that driving is ___ (6) ___; it is "
    "that the balance has tipped a long way without anybody choosing to tip it.\n\n"
    "Schools that have tried to shift it have found the ___ (7) ___ measures work best. A "
    "meeting point three streets away, a parent who walks the last stretch with a group, a "
    "map of quiet routes. None of that ___ (8) ___ the traffic on its own. It does make the "
    "walk look possible again, which is most of what is missing.",
  "items": [
    (1, "happened", [("stopped", "opposite"), ("argued", "domain"), ("exploded", "nuance")],
     "verb",
     "The sentence has just said nobody decided it, so the change came about by itself; "
     "'exploded' would make it sudden, which the words 'slowly, one cautious family at a "
     "time' rule out.",
     "medium", 0.93),
    (2, "number", [("shortage", "opposite"), ("speed", "collocation"), ("noise", "domain")],
     "noun",
     "The danger the paragraph describes comes from many cars arriving at once, which is "
     "why parents drive; 'speed' names a different hazard, and the sentence is explaining "
     "the crowd the parents themselves make.",
     "medium", 0.92),
    (3, "overlook", [("regain", "collocation"), ("exaggerate", "nuance"), ("notice", "opposite")],
     "verb",
     "The paragraph then lists things people do not think about, so the point is that the "
     "loss goes unseen; 'regain' would promise the walk back, which nothing here offers.",
     "medium", 0.92),
    (4, "supervised", [("enjoyed", "domain"), ("interrupted", "nuance"), ("arranged", "collocation")],
     "verb",
     "An adult standing a few metres away is watching rather than organising, and that is "
     "the contrast with the rest of the day; 'arranged' describes planning a day instead.",
     "medium", 0.93),
    (5, "familiar", [("strange", "opposite"), ("attractive", "nuance"), ("crowded", "domain")],
     "adjective",
     "Knowing the dog and the slow crossing is knowing a place well, and the contrast is "
     "with being driven through it; 'attractive' is about liking a suburb, not knowing it.",
     "medium", 0.92),
    (6, "wrong", [("common", "collocation"), ("expensive", "domain"), ("necessary", "nuance")],
     "adjective",
     "The writer has just granted that some families must drive, so the concession is that "
     "driving is not being condemned; 'necessary' would have the writer denying the very "
     "thing the previous sentence allows.",
     "hard", 0.90),
    (7, "smallest", [("largest", "opposite"), ("newest", "nuance"), ("cheapest", "collocation")],
     "adjective",
     "A meeting point, one parent and a map are modest measures, and the sentence promises "
     "the examples that follow; 'cheapest' weighs cost, which none of the three examples is "
     "presented in terms of.",
     "medium", 0.92),
    (8, "fixes", [("worsens", "opposite"), ("explains", "domain"), ("delays", "nuance")],
     "verb",
     "The concession is that these small measures do not solve the traffic, which is why "
     "the last sentence shifts to what they do achieve; 'delays' would mean putting the "
     "traffic off until later, which is not a claim the passage makes.",
     "hard", 0.90),
  ],
 },
 {
  "title": "The Great Artesian Basin",
  "topic": "Science",
  "text":
    "Under about a fifth of Australia lies one of the largest groundwater systems in the "
    "world. The Great Artesian Basin holds water that fell as rain along the western slopes "
    "of the Great Dividing Range, soaked into porous rock, and has been travelling "
    "underground ever since. Some of it entered the ground more than a million years ago, "
    "which makes the basin less a reservoir than a very slow ___ (1) ___.\n\n"
    "The water moves through sandstone layers sandwiched between beds of clay. Because the "
    "sandstone is ___ (2) ___ at its eastern edge and buried deep further west, the water is "
    "under pressure. Drill through the clay and it rises on its own, without a pump. That "
    "is what artesian means, and it is why the first bores in the 1880s were treated as "
    "___ (3) ___: paddocks that had never carried stock could suddenly water a flock.\n\n"
    "The enthusiasm was ___ (4) ___. By 1915 more than fifteen hundred bores were flowing, "
    "many of them left running day and night into open earth drains. Most of the water "
    "___ (5) ___ before it reached an animal. Pressure across the basin fell, and hundreds "
    "of springs that had run for thousands of years stopped.\n\n"
    "Since the 1990s a national program has capped bores and replaced drains with sealed "
    "pipe. The results have been ___ (6) ___: pressure has recovered in many areas and some "
    "springs have returned. The lesson is not that the basin was ___ (7) ___, but that its "
    "size made it look inexhaustible. Water that takes a million years to arrive cannot be "
    "___ (8) ___ as fast as a good season tempts people to draw it.",
  "items": [
    (1, "journey", [("shower", "domain"), ("lake", "collocation"), ("machine", "nuance")],
     "noun",
     "The sentence contrasts a still store of water with water that has been travelling for "
     "a million years; 'lake' is the very idea 'less a reservoir than' has just set aside.",
     "hard", 0.90),
    (2, "exposed", [("hidden", "opposite"), ("cracked", "nuance"), ("wet", "collocation")],
     "adjective",
     "Rain can only soak in where the sandstone reaches the surface, and the clause "
     "contrasts that edge with rock buried deep; 'cracked' describes the rock's condition "
     "rather than whether it is open to the sky.",
     "medium", 0.92),
    (3, "miraculous", [("ordinary", "opposite"), ("expensive", "domain"), ("promising", "nuance")],
     "adjective",
     "Water rising unaided in country that had never carried stock is the wonder the colon "
     "goes on to explain; 'promising' is far too mild for a paddock changed overnight.",
     "medium", 0.92),
    (4, "costly", [("brief", "nuance"), ("shared", "collocation"), ("justified", "opposite")],
     "adjective",
     "The paragraph that follows counts what the rush of bores destroyed, so the "
     "enthusiasm carried a price; 'brief' would say it did not last, but bores went on "
     "being sunk for decades.",
     "medium", 0.93),
    (5, "evaporated", [("froze", "domain"), ("arrived", "opposite"), ("slowed", "nuance")],
     "verb",
     "Open earth drains under an inland sun lose their water to the air, which is why the "
     "drains are mentioned; 'slowed' would still have the water reaching the stock, and "
     "the sentence says it did not.",
     "medium", 0.93),
    (6, "encouraging", [("disappointing", "opposite"), ("expected", "nuance"), ("expensive", "domain")],
     "adjective",
     "Recovered pressure and returning springs are the outcome the colon introduces; "
     "'expected' says nothing about whether the program worked, which is what the sentence "
     "is reporting.",
     "medium", 0.92),
    (7, "small", [("valuable", "domain"), ("ancient", "collocation"), ("damaged", "nuance")],
     "adjective",
     "The clause that follows blames the basin's great size for the illusion, so the point "
     "being denied is that it was ever short of water; 'damaged' is true of what happened "
     "and so cannot be the thing the sentence rules out.",
     "hard", 0.90),
    (8, "replaced", [("measured", "collocation"), ("cleaned", "domain"), ("stored", "nuance")],
     "verb",
     "Water a million years in transit cannot be put back as fast as it is drawn, which is "
     "the whole warning; 'stored' describes keeping water rather than making more arrive.",
     "medium", 0.92),
  ],
 },
]


def build():
    out = []
    for p in PASSAGES:
        found = sorted(int(x) for x in BLANK_RE.findall(p["text"]))
        asked = sorted(i[0] for i in p["items"])
        assert found == asked, f"{p['title']}: passage blanks {found} != items {asked}"
        for blank, key, distractors, pos, expl, diff, conf in p["items"]:
            frag = context(p["text"], blank)
            opts = [key] + [d for d, _ in distractors]
            out.append({
                "id": str(uuid.uuid4()),
                "subject": "reading_comprehension",
                "stem": f'The passage reads: "{frag}" '
                        f"Which word best fills blank ({blank})?",
                "option_a": opts[0], "option_b": opts[1],
                "option_c": opts[2], "option_d": opts[3],
                "correct_answer": "A",
                "explanation": expl,
                "topic": p["topic"],
                "difficulty": diff,
                "confidence": conf,
                "source_book": BOOK,
                "source_page": NN,
                "source_page_description": f"Category: {CATEGORY} — {LABEL}",
                "passage": p["text"],
                "figure_svg": None,
                "review_status": "pending",
                "created_at": NOW,
                "blank": blank,
                "pos": pos,
                "passage_title": p["title"],
                "stem_fragment": None,
                "relations": {d: r for d, r in distractors},
            })
    return out


if __name__ == "__main__":
    GEN.mkdir(parents=True, exist_ok=True)
    qs = build()
    path = GEN / f"{BOOK}_p{NN}.json"
    path.write_text(json.dumps(qs, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(qs)} questions across {len(PASSAGES)} passages -> {path}")
