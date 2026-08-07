#!/usr/bin/env python3
"""Builds rc_nsw_cloze_p3.json — 3 cloze passages x 8 blanks = 24 questions, completing
the §5 set at 15 passages / 120 questions.

Same rules as rc_cloze_p1_build.py. Every blank was checked by substituting the keys and
reading the passage: batch 2 had three blanks where a distractor read just as well as the
key, which is the one defect class no mechanical check has caught.
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
NN = 3
BOOK = "rc_nsw_cloze"
CATEGORY = "vocabulary_cloze"
LABEL = "Vocabulary cloze"
NOW = datetime.datetime(2026, 8, 4, 21, 0, 0, tzinfo=datetime.timezone.utc) \
    .isoformat().replace("+00:00", "Z")

BLANK_RE = re.compile(r"_{2,} \((\d+)\) _{2,}")

PASSAGES = [
 {
  "title": "Cool Burning",
  "topic": "Environment",
  "text":
    "For thousands of years Aboriginal people across northern Australia have used fire to "
    "manage country. The practice is often called cool burning, because the fires are lit "
    "early in the dry season when the grass is still ___ (1) ___ and the wind is light.\n\n"
    "A cool fire moves slowly along the ground. It clears leaf litter without reaching the "
    "canopy, so the tall trees are ___ (2) ___ and animals have time to move away. A late-season "
    "fire behaves very differently: it burns hot, spreads fast, and can ___ (3) ___ an area "
    "the size of a small country in a week.\n\n"
    "Rangers now light early-season fires from helicopters as well as on foot, using "
    "knowledge that has been ___ (4) ___ through families for generations. The aim is to break "
    "the landscape into a ___ (5) ___ of burnt and unburnt patches, so that a late fire runs "
    "out of fuel before it can travel far.\n\n"
    "The results have been ___ (6) ___. Savanna burning projects across the Top End now cut "
    "greenhouse emissions by amounts that can be audited, and several earn carbon credits "
    "that fund ranger "
    "wages. For communities, the work also ___ (7) ___ people to country, which many rangers "
    "describe as the part that ___ (8) ___ most.",
  "items": [
    (1, "damp", [("dry", "opposite"), ("tall", "domain"), ("green", "collocation")],
     "adjective",
     "Fires are lit early precisely because moisture keeps them cool and slow; 'green' "
     "describes the colour of the grass rather than the wetness that makes the fire mild.",
     "medium", 0.92),
    (2, "unharmed", [("destroyed", "opposite"), ("visible", "domain"), ("scorched", "nuance")],
     "adjective",
     "A fire that never reaches the canopy leaves the tall trees intact; 'scorched' would "
     "mean they were burnt after all, which contradicts the clause before it.",
     "medium", 0.93),
    (3, "consume", [("protect", "opposite"), ("measure", "domain"), ("threaten", "nuance")],
     "verb",
     "A hot fire burning across an enormous area destroys it, which consuming means; "
     "'threaten' would leave the country unburnt, but the sentence describes what the fire "
     "actually does.",
     "medium", 0.93),
    (4, "passed", [("withheld", "opposite"), ("printed", "domain"), ("shared", "collocation")],
     "verb",
     "Knowledge handed from one generation to the next is passed down through families; "
     "'shared' is close but does not carry the sense of moving between generations that "
     "'through families for generations' requires.",
     "hard", 0.89),
    (5, "mosaic", [("wall", "domain"), ("uniform", "opposite"), ("collection", "nuance")],
     "noun",
     "Alternating burnt and unburnt patches form a patchwork, which is what a mosaic "
     "describes; 'collection' gives no sense of the pattern that stops a fire spreading.",
     "hard", 0.89),
    (6, "measurable", [("imagined", "opposite"), ("expensive", "domain"), ("enormous", "overreach")],
     "adjective",
     "Emissions cut by audited amounts, and carbon credits earned against them, are "
     "results that can be quantified; 'enormous' claims a scale the passage never gives.",
     "medium", 0.91),
    (7, "connects", [("separates", "opposite"), ("transports", "domain"), ("introduces", "nuance")],
     "verb",
     "Ranger work strengthens people's link with country, which connecting means; "
     "'introduces' would suggest the connection was new, but the passage describes a "
     "practice thousands of years old.",
     "medium", 0.92),
    (8, "matters", [("costs", "domain"), ("fails", "opposite"), ("surprises", "nuance")],
     "verb",
     "Rangers single this out as the most important part of the work, which is what "
     "mattering most means; 'costs' would turn a statement about value into one about money.",
     "medium", 0.93),
  ],
 },
 {
  "title": "The Platypus",
  "topic": "Science",
  "text":
    "When the first platypus specimen reached London in 1799, several scientists were "
    "___ (1) ___ that it was a hoax. The animal had a bill like a duck, fur like an otter and "
    "a tail like a beaver, and one curator went so far as to check the bill for stitches.\n\n"
    "The platypus is one of only five mammal species that lay eggs. It also hunts in a way "
    "no other mammal ___ (2) ___. Swimming with its eyes, ears and nostrils shut, it finds "
    "prey using electroreceptors in the bill, which ___ (3) ___ the tiny electrical signals "
    "given off by the muscles of shrimp and insect larvae.\n\n"
    "Males carry a spur on each hind leg connected to a venom gland. The venom is not "
    "___ (4) ___ to humans, but the pain is severe and can last for weeks. Production rises "
    "during the breeding season, which suggests the spur is used in ___ (5) ___ between males "
    "rather than for defence.\n\n"
    "Platypus numbers are hard to ___ (6) ___, because the animal is shy and active mainly at "
    "dawn and dusk. Surveys now use environmental DNA, testing river water for traces the "
    "animal ___ (7) ___ behind. The results suggest the range has contracted, and drought and "
    "river regulation are the most likely ___ (8) ___.",
  "items": [
    (1, "convinced", [("doubtful", "opposite"), ("delighted", "domain"), ("suspicious", "nuance")],
     "adjective",
     "Checking the bill for stitches shows they believed it was a fake, which being "
     "convinced of a hoax means; 'suspicious' is weaker than an act that assumes the fraud "
     "is real.",
     "medium", 0.91),
    (2, "matches", [("attempts", "nuance"), ("teaches", "domain"), ("avoids", "opposite")],
     "verb",
     "No other mammal hunts the same way, so nothing equals it; 'teaches' would describe passing the "
     "method on, which is not what hunting in a unique way means.",
     "hard", 0.89),
    (3, "detect", [("produce", "opposite"), ("count", "domain"), ("amplify", "nuance")],
     "verb",
     "Electroreceptors sense signals coming from the prey, which detecting means; 'produce' "
     "reverses the direction, since the shrimp generate the signals, not the platypus.",
     "medium", 0.93),
    (4, "fatal", [("harmless", "opposite"), ("common", "domain"), ("painful", "collocation")],
     "adjective",
     "The sentence concedes it will not kill you before adding that it hurts a great deal; "
     "'painful' cannot fill the blank because the very next clause says the pain is severe.",
     "medium", 0.92),
    (5, "competition", [("cooperation", "opposite"), ("migration", "domain"), ("conversation", "nuance")],
     "noun",
     "Venom peaking in the breeding season points to males fighting each other; "
     "'cooperation' is the opposite of what a venomous spur between rivals suggests.",
     "medium", 0.92),
    (6, "estimate", [("ignore", "opposite"), ("describe", "domain"), ("guarantee", "overreach")],
     "verb",
     "A shy nocturnal animal makes population figures hard to work out approximately, which "
     "estimating means; 'guarantee' claims a certainty no survey of a shy animal offers.",
     "medium", 0.92),
    (7, "leaves", [("takes", "opposite"), ("hides", "nuance"), ("swims", "collocation")],
     "verb",
     "Environmental DNA works by picking up material shed into the water, which the animal "
     "leaves behind; 'hides' would mean the traces were concealed, yet the surveys find them.",
     "medium", 0.93),
    (8, "causes", [("results", "opposite"), ("regions", "domain"), ("theories", "nuance")],
     "noun",
     "Drought and river regulation are what brought the contraction about; 'results' names "
     "the contraction itself rather than what produced it.",
     "hard", 0.90),
  ],
 },
 {
  "title": "The Ghan",
  "topic": "Australian History",
  "text":
    "The railway line from Adelaide to Darwin took more than a century to ___ (1) ___. The "
    "first section opened in 1878, and the last spike was driven in 2003.\n\n"
    "The original line was built along a route surveyed by John McDouall Stuart, who had "
    "followed a chain of waterholes. That choice proved ___ (2) ___. The waterholes lay in "
    "country that floods, and washaways closed the line so often that passengers sometimes "
    "waited weeks. On one ___ (3) ___ occasion in 1917 a train was stranded for two weeks and "
    "the driver shot wild goats to feed everyone on board.\n\n"
    "The line was ___ (4) ___ in the 1980s onto higher ground to the west, and the old track "
    "was pulled up. The new alignment has proved far more ___ (5) ___, though the crossing of "
    "the Finke River still requires a bridge built for floods that arrive perhaps twice in a "
    "decade.\n\n"
    "The train is named after the Afghan cameleers who ___ (6) ___ goods through the interior "
    "before the railway existed. Their camel strings carried wire for the Overland Telegraph, "
    "supplies to remote stations and water to construction camps. The name is all that "
    "___ (7) ___ of a trade that the railway itself made ___ (8) ___.",
  "items": [
    (1, "complete", [("abandon", "opposite"), ("describe", "domain"), ("approve", "collocation")],
     "verb",
     "A first section in 1878 and a last spike in 2003 describe finishing the line; "
     "'approve' concerns permission rather than the building the dates measure.",
     "medium", 0.93),
    (2, "unwise", [("sensible", "opposite"), ("expensive", "domain"), ("popular", "nuance")],
     "adjective",
     "The following sentences describe floods and washaways caused by that route, so the "
     "choice went badly; 'expensive' names a cost the passage never mentions.",
     "medium", 0.92),
    (3, "notorious", [("ordinary", "opposite"), ("recent", "domain"), ("cheerful", "nuance")],
     "adjective",
     "A stranding remembered for a driver shooting goats is a famously bad episode; "
     "'ordinary' contradicts the point of singling the occasion out.",
     "hard", 0.90),
    (4, "rebuilt", [("removed", "opposite"), ("renamed", "domain"), ("repaired", "nuance")],
     "verb",
     "The line was laid again on a new alignment and the old track lifted, which rebuilding "
     "means; 'repaired' would mean the original route was kept and mended.",
     "medium", 0.92),
    (5, "reliable", [("fragile", "opposite"), ("scenic", "domain"), ("frequent", "collocation")],
     "adjective",
     "Higher ground avoids the washaways that closed the old line, so services can be "
     "counted on; 'frequent' concerns how often trains run, not whether floods stop them.",
     "medium", 0.93),
    (6, "hauled", [("ordered", "domain"), ("abandoned", "opposite"), ("escorted", "nuance")],
     "verb",
     "Camel strings carrying wire, supplies and water were transporting goods; 'escorted' "
     "would mean travelling alongside cargo somebody else moved.",
     "medium", 0.92),
    (7, "survives", [("began", "opposite"), ("travelled", "domain"), ("grew", "nuance")],
     "verb",
     "The name is the last thing left of the cameleers' trade, which is what surviving "
     "means; 'grew' would describe the trade expanding, and the railway ended it.",
     "hard", 0.89),
    (8, "obsolete", [("essential", "opposite"), ("famous", "domain"), ("difficult", "nuance")],
     "adjective",
     "Once the railway could carry the freight, camel trains were no longer needed at all; "
     "'difficult' would mean the trade continued but got harder.",
     "hard", 0.89),
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
                "stem": f'Blank ({blank}): "...{frag}..." '
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
