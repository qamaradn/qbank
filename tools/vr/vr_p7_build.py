#!/usr/bin/env python3
"""Builds vr_vic_acer_p7.json — 25 antonym questions (TASK §3.2).

The key is the OPPOSITE of the target, so the relation vocabulary shifts: no distractor
may be declared 'opposite' (it would be a second correct answer), and the standard trap
is a 'synonym' of the target — the answer a student gives when they read the question
too quickly and match on meaning rather than reversing it.
"""
import datetime
import json
import pathlib
import sys
import uuid

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/verbal_reasoning/generated"
NN = 7
BOOK = "vr_vic_acer"
CATEGORY = "antonym"
LABEL = "Antonyms / opposites"
NOW = datetime.datetime(2026, 8, 4, 16, 0, 0, tzinfo=datetime.timezone.utc) \
    .isoformat().replace("+00:00", "Z")

ITEMS = [
 ("scatter", "The wind began to scatter the leaves across the court.", "gather",
  [("disperse", "synonym"), ("shatter", "form"), ("sweep", "collocation")],
  "To scatter is to throw things apart, so its opposite is to bring them together; "
  "'disperse' means the same as scatter, which is what the question asks you to reverse.",
  "medium", 0.94),

 ("ascent", "The ascent from the valley floor took most of the morning.", "descent",
  [("climb", "synonym"), ("assent", "form"), ("summit", "domain")],
  "An ascent is a journey upward, so its opposite is a journey down; 'assent' sounds "
  "identical but means agreement.",
  "medium", 0.94),

 ("praise", "The review was full of praise for the school's junior orchestra.", "criticism",
  [("acclaim", "synonym"), ("prize", "form"), ("attention", "nuance")],
  "Praise is the expression of approval, so its opposite is the expression of "
  "disapproval; 'acclaim' is another word for praise itself.",
  "medium", 0.95),

 ("shallow", "The channel is shallow enough to wade at low tide.", "deep",
  [("low", "synonym"), ("hollow", "form"), ("narrow", "nuance")],
  "Shallow describes little depth, so its opposite concerns great depth; 'narrow' "
  "describes width instead, which is a different dimension entirely.",
  "medium", 0.94),

 ("permanent", "The repair was meant to be permanent, not another patch.", "temporary",
  [("lasting", "synonym"), ("prominent", "form"), ("expensive", "domain")],
  "Permanent means lasting indefinitely, so its opposite lasts only a short while; "
  "'lasting' restates permanent rather than reversing it.",
  "medium", 0.95),

 ("expand", "Warm air will expand the metal panels by several millimetres.", "contract",
  [("enlarge", "synonym"), ("expend", "form"), ("warm", "collocation")],
  "To expand is to grow larger, so the opposite is to shrink; 'expend' looks close but "
  "means to use something up.",
  "medium", 0.94),

 ("guilty", "The panel found him guilty of the lesser charge only.", "innocent",
  [("blameworthy", "synonym"), ("gilded", "form"), ("charged", "collocation")],
  "Guilty means responsible for wrongdoing, so its opposite is free of blame; 'charged' "
  "goes with court proceedings but says only that an accusation was made.",
  "medium", 0.94),

 ("generous", "The club was generous with its equipment during the drought.", "stingy",
  [("giving", "synonym"), ("genuine", "form"), ("wealthy", "nuance")],
  "Generous means freely giving, so its opposite is unwilling to give; 'wealthy' "
  "describes having much rather than parting with it, and the two often come apart.",
  "medium", 0.94),

 ("arrive", "The team will arrive the night before the heats.", "depart",
  [("reach", "synonym"), ("arise", "form"), ("compete", "domain")],
  "To arrive is to reach a place, so its opposite is to leave one; 'reach' is another "
  "way of saying arrive.",
  "medium", 0.95),

 ("ancient", "The ancient river gums along the bank predate the town.", "modern",
  [("aged", "synonym"), ("anxious", "form"), ("towering", "collocation")],
  "Ancient means belonging to the distant past, so its opposite belongs to the present; "
  "'towering' describes the height of the trees rather than their age.",
  "medium", 0.95),

 ("victory", "The victory over Geelong ended a run of eight losses.", "defeat",
  [("triumph", "synonym"), ("victim", "form"), ("contest", "collocation")],
  "A victory is a win, so its opposite is a loss; 'triumph' is simply another word for "
  "a victory.",
  "medium", 0.95),

 ("increase", "A steady increase in visitor numbers followed the new track.", "decrease",
  [("rise", "synonym"), ("incense", "form"), ("change", "nuance")],
  "An increase is a growth in amount, so its opposite is a reduction; 'change' covers "
  "movement in either direction and so does not reverse it.",
  "medium", 0.94),

 ("accept", "The committee voted to accept the revised plan.", "reject",
  [("receive", "synonym"), ("except", "form"), ("consider", "nuance")],
  "To accept is to agree to take something, so its opposite is to turn it down; "
  "'consider' means only to think about it, stopping short of either decision.",
  "medium", 0.94),

 ("frequent", "Frequent stops made the trip twice as long as it needed to be.", "rare",
  [("regular", "synonym"), ("fragrant", "form"), ("brief", "nuance")],
  "Frequent means happening often, so its opposite happens seldom; 'brief' describes how "
  "long each stop lasted, not how often they happened.",
  "medium", 0.93),

 ("harsh", "The harsh light off the salt flat made everyone squint.", "gentle",
  [("severe", "synonym"), ("hoarse", "form"), ("bright", "collocation")],
  "Harsh means unpleasantly severe, so its opposite is mild; 'bright' goes naturally with "
  "light but describes intensity rather than unpleasantness.",
  "medium", 0.93),

 ("obedient", "The kelpie was obedient even with three mobs in the yard.", "defiant",
  [("dutiful", "synonym"), ("eager", "nuance"), ("clever", "domain")],
  "Obedient means willing to follow instructions, so its opposite refuses them; 'clever' "
  "describes intelligence, and a clever dog may be thoroughly disobedient.",
  "medium", 0.94),

 ("humid", "The humid air on the coast made the climb feel harder.", "dry",
  [("muggy", "synonym"), ("humble", "form"), ("hot", "collocation")],
  "Humid means full of moisture, so its opposite lacks it; 'hot' often appears alongside "
  "humid but describes temperature, and dry air can be just as hot.",
  "medium", 0.94),

 ("conceal", "A tarpaulin was used to conceal the gear in the tray.", "reveal",
  [("hide", "synonym"), ("congeal", "form"), ("secure", "domain")],
  "To conceal is to keep something out of sight, so its opposite brings it into view; "
  "'secure' concerns keeping the gear safe rather than hidden.",
  "medium", 0.95),

 ("brave", "It was a brave decision to bat first on that surface.", "cowardly",
  [("bold", "synonym"), ("brash", "form"), ("unwise", "nuance")],
  "Brave means showing courage, so its opposite shows fear; 'unwise' judges whether the "
  "decision was sensible, which is a separate question from whether it was courageous.",
  "medium", 0.93),

 ("abundant", "Feed was abundant after the autumn rain.", "scarce",
  [("plentiful", "synonym"), ("abandoned", "form"), ("nutritious", "domain")],
  "Abundant means present in great quantity, so its opposite is in short supply; "
  "'plentiful' means the same as abundant.",
  "medium", 0.94),

 ("depart", "Buses depart from the northern end of the terminal.", "arrive",
  [("leave", "synonym"), ("deport", "form"), ("queue", "collocation")],
  "To depart is to go away from a place, so its opposite is to come to one; 'leave' is "
  "another word for depart.",
  "medium", 0.95),

 ("polite", "A polite note was left under the windscreen wiper.", "rude",
  [("courteous", "synonym"), ("politic", "form"), ("brief", "domain")],
  "Polite means showing good manners, so its opposite is ill-mannered; 'brief' describes "
  "the length of the note rather than its manner.",
  "medium", 0.94),

 ("gradual", "The gradual slope makes the last kilometre deceptive.", "sudden",
  [("steady", "synonym"), ("graceful", "form"), ("gentle", "nuance")],
  "Gradual means happening by small degrees over time, so its opposite is abrupt; "
  "'gentle' describes how steep the slope is, not how quickly it changes.",
  "hard", 0.91),

 ("artificial", "An artificial reef was sunk off the point in 2019.", "natural",
  [("man-made", "synonym"), ("artistic", "form"), ("submerged", "collocation")],
  "Artificial means made by people, so its opposite occurs of itself; 'submerged' "
  "describes where the reef sits rather than how it came to exist.",
  "medium", 0.94),

 ("reluctant", "She was reluctant to nominate for the committee again.", "willing",
  [("unwilling", "synonym"), ("redundant", "form"), ("quiet", "domain")],
  "Reluctant means hesitant to do something, so its opposite is ready to do it; "
  "'unwilling' restates reluctant instead of reversing it.",
  "medium", 0.95),
]


def build():
    out = []
    for target, stem, key, distractors, expl, diff, conf in ITEMS:
        opts = [key] + [d for d, _ in distractors]
        out.append({
            "id": str(uuid.uuid4()),
            "subject": "verbal_reasoning",
            "stem": f"{stem} Which word is most nearly OPPOSITE in meaning to '{target}'?",
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
