#!/usr/bin/env python3
"""Builds vr_vic_acer_p17.json — 25 antonym questions (TASK §3.2).

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
NN = 17
BOOK = "vr_vic_acer"
CATEGORY = "antonym"
LABEL = "Antonyms / opposites"
NOW = datetime.datetime(2026, 8, 4, 16, 0, 0, tzinfo=datetime.timezone.utc) \
    .isoformat().replace("+00:00", "Z")

ITEMS = [
 ("compress", "The software will compress the file before sending it.", "expand",
  [("squeeze", "synonym"), ("comprise", "form"), ("encrypt", "domain")],
  "To compress is to squash into less space, so expanding reverses it; 'squeeze' means the same as the target.", "medium", 0.94),
 ("confess", "He would not confess to having moved the marker.", "deny",
  [("admit", "synonym"), ("regret", "domain"), ("apologise", "nuance")],
  "To confess is to own up, so denying is the opposite; 'admit' means the same as confess.", "medium", 0.95),
 ("consent", "Both parents must consent before a student can travel.", "refuse",
  [("agree", "synonym"), ("content", "form"), ("witness", "domain")],
  "To consent is to give permission, so refusing is the reverse; 'agree' means the same as the target.", "medium", 0.94),
 ("converge", "The two tracks converge just past the old bridge.", "diverge",
  [("meet", "synonym"), ("split", "domain"), ("cross", "nuance")],
  "To converge is to come together, so diverging is the opposite; 'meet' says the same as converge.", "medium", 0.94),
 ("courteous", "The staff were courteous even at the end of a long day.", "rude",
  [("polite", "synonym"), ("efficient", "domain"), ("tired", "nuance")],
  "Courteous means well mannered, so rude is its opposite; 'polite' repeats the target.", "medium", 0.95),
 ("deny", "The club will not deny access to former members.", "grant",
  [("refuse", "synonym"), ("delay", "domain"), ("restrict", "nuance")],
  "To deny is to withhold something, so granting it is the reverse; 'refuse' means the same as deny.", "medium", 0.94),
 ("detach", "You can detach the cover for washing.", "attach",
  [("remove", "synonym"), ("detect", "form"), ("fold", "domain")],
  "To detach is to separate one part from another, so attaching is the opposite; 'remove' means much the same as detach.", "medium", 0.95),
 ("dilute", "Dilute the concentrate before putting it on the beds.", "concentrate",
  [("water down", "synonym"), ("thicken", "domain"), ("apply", "collocation")],
  "To dilute is to make weaker by adding liquid, so concentrating reverses it; 'water down' says the same as the target.", "medium", 0.94),
 ("dismantle", "Volunteers will dismantle the marquee on Sunday morning.", "assemble",
  [("take apart", "synonym"), ("dismay", "form"), ("store", "collocation")],
  "To dismantle is to take something to pieces, so assembling is the opposite; 'take apart' means the same thing.", "medium", 0.95),
 ("domestic", "The airline runs domestic services only.", "international",
  [("internal", "synonym"), ("cancelled", "domain"), ("frequent", "nuance")],
  "Domestic here means within one country, so international is the opposite; 'internal' points the same way.", "medium", 0.94),
 ("elevate", "Blocks were used to elevate the tank above the tap line.", "lower",
  [("raise", "synonym"), ("alleviate", "form"), ("secure", "domain")],
  "To elevate is to lift something higher, so lowering is the reverse; 'raise' means exactly the same.", "medium", 0.95),
 ("evaporate", "The shallow pools evaporate within a week of the rain.", "condense",
  [("dry out", "synonym"), ("freeze", "domain"), ("drain", "nuance")],
  "To evaporate is to turn from liquid to vapour, so condensing is the opposite; 'dry out' describes the same process.", "medium", 0.94),
 ("fasten", "Fasten the strap before the ramp is lowered.", "loosen",
  [("secure", "synonym"), ("hasten", "form"), ("check", "collocation")],
  "To fasten is to make firm, so loosening is the reverse; 'secure' means the same as fasten.", "medium", 0.95),
 ("forbid", "House rules forbid ball games on the front lawn.", "permit",
  [("prohibit", "synonym"), ("enforce", "domain"), ("discourage", "nuance")],
  "To forbid is to rule something out entirely, so permitting is the opposite; 'prohibit' means the same as forbid.", "medium", 0.95),
 ("fragment", "The dry clay will fragment as soon as it is lifted.", "cohere",
  [("shatter", "synonym"), ("fragrant", "form"), ("crumble", "nuance")],
  "To fragment is to break into pieces, so holding together is the reverse; 'shatter' means much the same as fragment.", "hard", 0.91),
 ("harden", "The resin will harden overnight in this weather.", "soften",
  [("set", "synonym"), ("shrink", "domain"), ("cure", "nuance")],
  "To harden is to become firm, so softening is the opposite; 'set' means the same as harden in this context.", "medium", 0.94),
 ("horizontal", "The shelf must be horizontal or the jars will slide.", "vertical",
  [("level", "synonym"), ("adjustable", "domain"), ("sturdy", "nuance")],
  "Horizontal means flat and parallel to the ground, so vertical is its opposite; 'level' means the same as horizontal.", "medium", 0.95),
 ("inferior", "The second batch of timber was inferior to the first.", "superior",
  [("poorer", "synonym"), ("interior", "form"), ("cheaper", "nuance")],
  "Inferior means lower in quality, so superior is the opposite; 'poorer' says the same as inferior.", "medium", 0.94),
 ("innocent", "The dog was innocent this time, whatever the neighbours said.", "guilty",
  [("blameless", "synonym"), ("innocuous", "form"), ("obedient", "nuance")],
  "Innocent means not responsible for the wrong, so guilty is the reverse; 'blameless' means the same as innocent.", "medium", 0.95),
 ("integrate", "The plan is to integrate the two rosters from July.", "separate",
  [("merge", "synonym"), ("interrogate", "form"), ("publish", "collocation")],
  "To integrate is to bring parts into one whole, so separating is the opposite; 'merge' means the same as integrate.", "medium", 0.94),
 ("lengthen", "The shadows lengthen quickly at that time of year.", "shorten",
  [("extend", "synonym"), ("lessen", "form"), ("darken", "nuance")],
  "To lengthen is to become longer, so shortening is the reverse; 'extend' means the same as lengthen.", "medium", 0.95),
 ("literal", "She took the instruction in its most literal sense.", "figurative",
  [("exact", "synonym"), ("literary", "form"), ("careful", "nuance")],
  "Literal means taking words at face value, so figurative is its opposite; 'exact' points the same way as literal.", "hard", 0.92),
 ("loosen", "Loosen the nut before lifting the wheel clear.", "tighten",
  [("slacken", "synonym"), ("lessen", "form"), ("grease", "domain")],
  "To loosen is to make less tight, so tightening is the reverse; 'slacken' means the same as loosen.", "medium", 0.95),
 ("mature", "The trees along the drive are mature now.", "immature",
  [("grown", "synonym"), ("manure", "form"), ("shady", "domain")],
  "Mature means fully developed, so immature is its opposite; 'grown' means much the same as mature.", "medium", 0.94),
 ("mobile", "The clinic is mobile and visits four towns a week.", "stationary",
  [("movable", "synonym"), ("noble", "form"), ("modern", "nuance")],
  "Mobile means able to be moved about, so stationary is the reverse; 'movable' means the same as mobile.", "medium", 0.95),
 ("nocturnal", "Most of the small marsupials there are nocturnal.", "active by day",
  [("active at night", "synonym"), ("natural", "form"), ("secretive", "nuance")],
  "Nocturnal means active at night, so being active by day is its opposite; 'active at night' simply restates the target.", "medium", 0.94),
 ("optimistic", "He remained optimistic about the second half.", "pessimistic",
  [("hopeful", "synonym"), ("optimal", "form"), ("relaxed", "nuance")],
  "Optimistic means expecting a good outcome, so pessimistic is the opposite; 'hopeful' means the same as optimistic.", "medium", 0.95),
 ("partial", "The report gave only a partial account of the evening.", "complete",
  [("incomplete", "synonym"), ("partly", "form"), ("brief", "nuance")],
  "Partial here means covering only part, so complete is the opposite; 'incomplete' says the same as partial.", "medium", 0.94),
 ("prohibit", "The by-law will prohibit fires between November and March.", "allow",
  [("ban", "synonym"), ("inhibit", "form"), ("regulate", "nuance")],
  "To prohibit is to forbid outright, so allowing is the reverse; 'ban' means the same as prohibit.", "medium", 0.95),
 ("prosper", "The stall began to prosper once the market moved indoors.", "flounder",
  [("thrive", "synonym"), ("proper", "form"), ("expand", "nuance")],
  "To prosper is to do well, so floundering is the opposite; 'thrive' means the same as prosper.", "medium", 0.94),
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
