#!/usr/bin/env python3
"""Builds vr_vic_acer_p16.json — 25 antonym questions (TASK §3.2).

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
NN = 16
BOOK = "vr_vic_acer"
CATEGORY = "antonym"
LABEL = "Antonyms / opposites"
NOW = datetime.datetime(2026, 8, 4, 16, 0, 0, tzinfo=datetime.timezone.utc) \
    .isoformat().replace("+00:00", "Z")

ITEMS = [
 ("ascend", "The path begins to ascend sharply after the second creek crossing.", "descend",
  [("climb", "synonym"), ("assent", "form"), ("wind", "domain")],
  "To ascend is to go up, so descending is its opposite; 'climb' means the same as the target and would be a second correct answer if the question asked for a synonym.", "medium", 0.95),
 ("spacious", "The new shed is spacious enough for both trailers.", "cramped",
  [("roomy", "synonym"), ("specious", "form"), ("dusty", "domain")],
  "Spacious means having plenty of room, so cramped is its opposite; 'roomy' repeats the target rather than reversing it.", "medium", 0.94),
 ("accelerate", "The train began to accelerate out of the station.", "decelerate",
  [("hasten", "synonym"), ("celebrate", "form"), ("depart", "collocation")],
  "To accelerate is to speed up, so slowing down is the reverse; 'hasten' pushes in the same direction as the target.", "medium", 0.94),
 ("ally", "Each of the two clubs had long been an ally of the other.", "rival",
  [("partner", "synonym"), ("alley", "form"), ("sponsor", "domain")],
  "An ally is somebody on your side, so a rival is the opposite; 'partner' names the same relationship in different words.", "medium", 0.94),
 ("amateur", "The competition is open to amateur players only.", "professional",
  [("novice", "synonym"), ("amiable", "form"), ("registered", "domain")],
  "An amateur plays without payment, so a professional is the opposite; 'novice' overlaps heavily with amateur rather than reversing it.", "medium", 0.94),
 ("imitation", "The trophy turned out to be imitation silver.", "genuine",
  [("fake", "synonym"), ("imitative", "form"), ("engraved", "nuance")],
  "Imitation means made to resemble the real thing, so genuine is its opposite; 'fake' means the same as the target.", "medium", 0.94),
 ("brief", "The captain gave a brief account of the match.", "lengthy",
  [("concise", "synonym"), ("brisk", "form"), ("honest", "nuance")],
  "Brief means short, so lengthy reverses it; 'concise' means short as well and would be a second key.", "medium", 0.94),
 ("cautious", "He was cautious on the descent, testing each hold.", "reckless",
  [("careful", "synonym"), ("hesitant", "domain"), ("slow", "nuance")],
  "Cautious means taking care to avoid risk, so reckless is the opposite; 'careful' repeats the target rather than reversing it.", "medium", 0.95),
 ("condemn", "The board moved to condemn the decision at once.", "commend",
  [("criticise", "synonym"), ("condense", "form"), ("review", "domain")],
  "To condemn is to declare something wholly wrong, so commending it is the reverse; 'criticise' points the same way as the target.", "medium", 0.94),
 ("crude", "It was a crude repair that held for the rest of the trip.", "refined",
  [("rough", "synonym"), ("hasty", "domain"), ("temporary", "nuance")],
  "Crude means rough and unpolished, so refined is its opposite; 'rough' simply restates the target.", "medium", 0.94),
 ("deliberate", "The pause before her answer was deliberate.", "accidental",
  [("intentional", "synonym"), ("delicate", "form"), ("lengthy", "nuance")],
  "Deliberate means done on purpose, so accidental reverses it; 'intentional' means the same as the target.", "medium", 0.95),
 ("demolish", "Crews will demolish the old stand over the winter.", "erect",
  [("flatten", "synonym"), ("diminish", "form"), ("inspect", "nuance")],
  "To demolish is to pull down, so erecting is the opposite; 'flatten' is another way of saying the same thing.", "medium", 0.94),
 ("descend", "Cloud began to descend over the ridge by mid-morning.", "rise",
  [("drop", "synonym"), ("decent", "form"), ("thicken", "nuance")],
  "To descend is to come down, so rising is the reverse; 'drop' repeats the target's direction.", "medium", 0.94),
 ("diminish", "Interest in the competition began to diminish after round four.", "grow",
  [("dwindle", "synonym"), ("demolish", "form"), ("shift", "nuance")],
  "To diminish is to become less, so growing is the opposite; 'dwindle' means the same and would be a second key.", "medium", 0.94),
 ("discourage", "Wet weather did nothing to discourage the crowd.", "encourage",
  [("deter", "synonym"), ("discover", "form"), ("delay", "nuance")],
  "To discourage is to put somebody off, so encouraging is the reverse; 'deter' means the same thing.", "medium", 0.95),
 ("exaggerate", "He tends to exaggerate the size of the catch.", "understate",
  [("overstate", "synonym"), ("aggravate", "form"), ("recount", "nuance")],
  "To exaggerate is to make something sound bigger than it was, so understating reverses it; 'overstate' says the same as the target.", "medium", 0.94),
 ("swell", "The timber will swell if the door is left out in the rain.", "shrink",
  [("expand", "synonym"), ("soften", "domain"), ("split", "nuance")],
  "To swell is to grow larger, so shrinking is the reverse; 'expand' matches the target instead of reversing it.", "medium", 0.94),
 ("lush", "The paddock was lush after a fortnight of rain.", "withered",
  [("green", "synonym"), ("plush", "form"), ("fenced", "nuance")],
  "Lush means thick with healthy growth, so withered is the opposite; 'green' points the same way as the target.", "medium", 0.94),
 ("flexible", "The new roster is flexible enough to suit shift workers.", "rigid",
  [("adaptable", "synonym"), ("flammable", "form"), ("popular", "nuance")],
  "Flexible means able to bend to circumstances, so rigid is the reverse; 'adaptable' restates the target.", "medium", 0.95),
 ("bountiful", "The harvest that year was bountiful.", "meagre",
  [("ample", "synonym"), ("beautiful", "form"), ("early", "domain")],
  "Bountiful means yielding a great deal, so meagre is the opposite; 'ample' agrees with the target rather than reversing it.", "medium", 0.93),
 ("meek", "He was meek about the whole business, even when pressed.", "assertive",
  [("timid", "synonym"), ("obliging", "domain"), ("truthful", "nuance")],
  "Meek means unwilling to push oneself forward, so assertive is its opposite; 'timid' means much the same as meek.", "medium", 0.94),
 ("douse", "They had to douse the coals before leaving the site.", "kindle",
  [("extinguish", "synonym"), ("scatter", "domain"), ("bury", "nuance")],
  "To douse a fire is to put it out, so kindling one is the reverse; 'extinguish' means the same as douse.", "medium", 0.94),
 ("include", "The fee will include entry to both days.", "exclude",
  [("cover", "synonym"), ("conclude", "form"), ("refund", "domain")],
  "To include is to take something in, so excluding is the reverse; 'cover' says the same as include in this context.", "medium", 0.94),
 ("majority", "A majority of members voted for the change.", "minority",
  [("bulk", "synonym"), ("mayoralty", "form"), ("quorum", "nuance")],
  "A majority is the greater part, so a minority is its opposite; 'bulk' names the greater part as well.", "medium", 0.94),
 ("dutiful", "She was dutiful about the roster all season.", "negligent",
  [("conscientious", "synonym"), ("punctual", "domain"), ("cheerful", "nuance")],
  "Dutiful means reliably doing what is required, so negligent is the opposite; 'conscientious' agrees with the target.", "medium", 0.94),
 ("enduring", "The arrangement proved an enduring one.", "fleeting",
  [("lasting", "synonym"), ("informal", "domain"), ("formal", "nuance")],
  "Enduring means continuing over a long period, so fleeting is its opposite; 'lasting' repeats the target.", "medium", 0.94),
 ("applaud", "The crowd stayed on to applaud both teams.", "jeer",
  [("cheer", "synonym"), ("applied", "form"), ("depart", "domain")],
  "To applaud is to show approval, so jeering is the opposite; 'cheer' means much the same as applaud.", "medium", 0.94),
 ("blunt", "The blade had gone blunt after a season of use.", "keen",
  [("dull", "synonym"), ("chipped", "domain"), ("rusty", "nuance")],
  "Blunt means lacking a sharp edge, so keen is its opposite in this sense; 'dull' means the same as blunt.", "medium", 0.93),
 ("transparent", "The lid is transparent so the contents can be seen.", "opaque",
  [("clear", "synonym"), ("apparent", "form"), ("brittle", "domain")],
  "Transparent means light passes through, so opaque is the reverse; 'clear' means transparent as well.", "medium", 0.95),
 ("voluntary", "Attendance at the twilight session is voluntary.", "compulsory",
  [("optional", "synonym"), ("solitary", "form"), ("free", "domain")],
  "Voluntary means done by choice, so compulsory is its opposite; 'optional' means the same as voluntary.", "medium", 0.95),
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
