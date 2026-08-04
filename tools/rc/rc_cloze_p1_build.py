#!/usr/bin/env python3
"""Builds rc_nsw_cloze_p1.json — 4 cloze passages x 8 blanks = 32 questions (TASK §5).

Each passage becomes 8 linked MCQs sharing one `passage` field, the same way the existing
719 RC questions already share 144 passages.

The quoted fragment in every stem is CUT FROM THE PASSAGE by `context()` rather than
retyped, so a stem cannot quote something the passage does not say. It also makes the
eight stems textually distinct, which matters: phase 4 drops near-duplicate stems at 0.85
silently, and eight stems reading "which word fits blank (n)?" would collapse to one.

Pitched for Year 6 — NSW is sat a full two years before the VIC paper, and TASK §2 calls
that difficulty gap deliberate.
"""
import datetime
import json
import pathlib
import re
import sys
import uuid

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/reading_comprehension/generated"
NN = 1
BOOK = "rc_nsw_cloze"
CATEGORY = "vocabulary_cloze"
LABEL = "Vocabulary cloze"
NOW = datetime.datetime(2026, 8, 4, 19, 0, 0, tzinfo=datetime.timezone.utc) \
    .isoformat().replace("+00:00", "Z")

BLANK_RE = re.compile(r"_{2,}\((\d+)\)_{2,}")

# Each passage: title, topic, text with ___(n)___ markers, and one item per blank.
# item = (blank, key, [(distractor, relation) x3], pos, explanation, difficulty, confidence)
PASSAGES = [
 {
  "title": "The Night Parrot",
  "topic": "Australian Wildlife",
  "text":
    "For almost a century the night parrot was believed to be extinct. The small green "
    "bird lives in the spinifex country of inland Australia, and it is active only after "
    "dark, which makes it ___(1)___ difficult to find. Between 1912 and 1979 there was "
    "not a single confirmed sighting, and many scientists ___(2)___ that the species had "
    "died out altogether.\n\n"
    "Then, in 2013, a naturalist named John Young ___(3)___ a photograph of a living "
    "night parrot in western Queensland. The image was blurred and the bird was partly "
    "hidden by grass, but it was ___(4)___ proof that the species had survived. "
    "Researchers immediately began searching the surrounding country for further signs.\n\n"
    "Finding the birds has proved ___(5)___ work. Night parrots call for only a few "
    "minutes at dusk, so teams leave sound recorders running for weeks and later listen "
    "through hundreds of hours of tape. The recordings are ___(6)___ against known calls "
    "before any sighting is accepted.\n\n"
    "The exact locations of the nests are kept ___(7)___. Conservationists worry that "
    "collectors would pay a great deal for eggs, and that too many visitors would disturb "
    "the fragile spinifex. For a bird that spent a hundred years hidden, a little more "
    "___(8)___ may be exactly what it needs.",
  "items": [
    (1, "extremely",
     [("rarely", "opposite"), ("briefly", "domain"), ("possibly", "nuance")],
     "adverb",
     "The sentence explains why the bird is hard to find, so a word strengthening "
     "'difficult' fits; 'rarely' would say the difficulty is uncommon, which contradicts "
     "a century without sightings.",
     "medium", 0.94),
    (2, "concluded",
     [("wondered", "nuance"), ("denied", "opposite"), ("announced", "collocation")],
     "verb",
     "The scientists reached a settled view after sixty-seven years without a sighting, "
     "which is what concluding means; 'wondered' suggests they were still unsure, but the "
     "sentence says they thought the bird had died out.",
     "medium", 0.93),
    (3, "captured",
     [("described", "collocation"), ("erased", "opposite"), ("imagined", "nuance")],
     "verb",
     "You capture a photograph when you succeed in taking one, which is what happened in "
     "2013; 'described' would mean he only spoke about the bird, yet an image existed.",
     "medium", 0.94),
    (4, "undeniable",
     [("disputed", "opposite"), ("photographic", "collocation"), ("partial", "nuance")],
     "adjective",
     "The sentence concedes the photo was blurred but insists it still settled the "
     "question, so a word meaning 'impossible to argue with' fits; 'partial' would "
     "weaken the proof the sentence is asserting.",
     "hard", 0.91),
    (5, "painstaking",
     [("effortless", "opposite"), ("dangerous", "domain"), ("hurried", "nuance")],
     "adjective",
     "Weeks of recordings and hundreds of hours of listening describe slow, careful "
     "labour; 'hurried' is the opposite of what listening through hundreds of hours of "
     "tape involves.",
     "medium", 0.93),
    (6, "checked",
     [("replaced", "domain"), ("ignored", "opposite"), ("recorded", "collocation")],
     "verb",
     "Comparing a new call with known calls before accepting it is checking; 'recorded' "
     "sits naturally beside tape and calls but names the earlier step, not the comparison.",
     "medium", 0.93),
    (7, "secret",
     [("public", "opposite"), ("quiet", "collocation"), ("temporary", "nuance")],
     "adjective",
     "The next sentence explains the fear of collectors and disturbance, which is a "
     "reason to withhold locations; 'public' would produce exactly the harm described.",
     "medium", 0.94),
    (8, "privacy",
     [("publicity", "opposite"), ("rainfall", "domain"), ("patience", "nuance")],
     "noun",
     "The paragraph argues for keeping the bird's whereabouts hidden, so more of the same "
     "concealment is what it needs; 'patience' is a quality of the researchers rather "
     "than something the parrot is given.",
     "hard", 0.90),
  ],
 },
 {
  "title": "The Overland Telegraph",
  "topic": "Australian History",
  "text":
    "Before 1872, a message sent from Adelaide to London took about three months, because "
    "it travelled by ship. The Overland Telegraph Line changed that ___(1)___, cutting the "
    "journey of a message to a matter of hours.\n\n"
    "The plan was ___(2)___: three thousand kilometres of wire strung between Adelaide and "
    "Darwin, across desert country that few Europeans had crossed. Charles Todd, the man "
    "in charge, divided the route into three sections so that crews could work on all of "
    "them at once. Even so, the northern teams were ___(3)___ by a wet season that turned "
    "the ground to mud and left drays bogged for weeks.\n\n"
    "Timber for the poles was ___(4)___ in much of the centre, so ironwood and even steel "
    "poles had to be carted enormous distances. Workers ___(5)___ on flour, tea and dried "
    "meat, and water was often found only by digging.\n\n"
    "The line was completed in August 1872. Its ___(6)___ on the colonies was immediate: "
    "wool prices from London could be read in Adelaide the same day, and newspapers began "
    "printing overseas news while it was still ___(7)___. Repeater stations built along "
    "the route later became the first permanent settlements in the interior, and several "
    "of them ___(8)___ into the towns that stand there today.",
  "items": [
    (1, "dramatically",
     [("slightly", "opposite"), ("recently", "domain"), ("gradually", "nuance")],
     "adverb",
     "Three months reduced to a few hours is an enormous change, which 'dramatically' "
     "conveys; 'gradually' would misdescribe a change that arrived with a single line.",
     "medium", 0.94),
    (2, "ambitious",
     [("modest", "opposite"), ("costly", "collocation"), ("reasonable", "nuance")],
     "adjective",
     "Three thousand kilometres of wire across barely explored desert is a bold "
     "undertaking; 'modest' contradicts the scale the sentence goes on to describe.",
     "medium", 0.94),
    (3, "delayed",
     [("assisted", "opposite"), ("employed", "domain"), ("warned", "nuance")],
     "verb",
     "Bogged drays and weeks lost describe work being held up; 'warned' would mean they "
     "were told about the wet season, which is not what the mud did to them.",
     "medium", 0.94),
    (4, "scarce",
     [("plentiful", "opposite"), ("valuable", "nuance"), ("seasoned", "collocation")],
     "adjective",
     "The sentence explains that poles had to be carted enormous distances, which only "
     "makes sense if local timber was hard to find; 'valuable' would not explain the "
     "carting.",
     "medium", 0.93),
    (5, "survived",
     [("feasted", "opposite"), ("insisted", "domain"), ("relied", "collocation")],
     "verb",
     "A diet of flour, tea and dried meat is bare subsistence, which 'survived on' "
     "captures; 'relied' is the trap, since you rely on something but the idiom here "
     "needs the sense of barely getting by.",
     "hard", 0.90),
    (6, "effect",
     [("cause", "opposite"), ("expense", "domain"), ("intention", "nuance")],
     "noun",
     "What follows describes results the line produced once finished, which is its "
     "effect; 'intention' would describe what was hoped for beforehand.",
     "medium", 0.93),
    (7, "current",
     [("outdated", "opposite"), ("expensive", "domain"), ("accurate", "nuance")],
     "adjective",
     "The point is that news reached print while it was still new, which 'current' means; "
     "'accurate' concerns whether the news was true, not how fresh it was.",
     "medium", 0.93),
    (8, "grew",
     [("shrank", "opposite"), ("moved", "domain"), ("appeared", "nuance")],
     "verb",
     "Stations becoming the towns that stand there today describes growth over time; "
     "'appeared' would suggest the towns arrived suddenly rather than developing from "
     "the stations.",
     "medium", 0.94),
  ],
 },
 {
  "title": "Sea Country Rangers",
  "topic": "Environment",
  "text":
    "Along the north coast of Australia, Indigenous ranger groups manage stretches of "
    "coastline known as sea country. Their work ___(1)___ traditional knowledge with "
    "satellite tracking, drones and water sampling.\n\n"
    "One of their main tasks is removing ghost nets. These are fishing nets that have been "
    "lost or thrown overboard, and they continue to catch turtles and dugongs for years "
    "___(2)___. A single net can travel thousands of kilometres on the current before it "
    "washes ashore. Rangers ___(3)___ the beaches after big tides, cut the nets free of "
    "the sand and record what has been trapped in them.\n\n"
    "The data they gather is ___(4)___ to scientists. Because rangers walk the same "
    "beaches season after season, they notice changes that a visiting researcher would "
    "___(5)___ entirely — a nesting beach that has narrowed, or a species arriving earlier "
    "than it used to.\n\n"
    "Funding for the programs is not ___(6)___, and groups often work on short grants that "
    "must be renewed. Rangers argue that this makes long-term planning almost impossible, "
    "because the ___(7)___ of the work depends on being present every year rather than in "
    "bursts. Where the programs have been ___(8)___ for a decade or more, turtle nesting "
    "numbers have begun to recover.",
  "items": [
    (1, "combines",
     [("separates", "opposite"), ("replaces", "nuance"), ("requires", "domain")],
     "verb",
     "The sentence lists traditional knowledge alongside modern tools, so both are in "
     "use together; 'replaces' would mean the technology had pushed the knowledge out.",
     "medium", 0.94),
    (2, "afterwards",
     [("beforehand", "opposite"), ("nearby", "domain"), ("occasionally", "nuance")],
     "adverb",
     "The nets keep catching animals long after being lost, which the following sentence "
     "about thousands of kilometres supports; 'occasionally' understates a problem "
     "serious enough to organise ranger patrols around.",
     "medium", 0.93),
    (3, "patrol",
     [("abandon", "opposite"), ("survey", "collocation"), ("visit", "nuance")],
     "verb",
     "Walking the beaches regularly to find and cut free nets is patrolling; 'visit' is "
     "too casual for work described as systematic and repeated after every big tide.",
     "medium", 0.93),
    (4, "valuable",
     [("worthless", "opposite"), ("confidential", "domain"), ("interesting", "nuance")],
     "adjective",
     "The next sentence explains that rangers notice changes researchers would miss, "
     "which is why the data matters; 'interesting' is far weaker than the argument being "
     "made.",
     "medium", 0.93),
    (5, "miss",
     [("notice", "opposite"), ("record", "collocation"), ("doubt", "nuance")],
     "verb",
     "The contrast is between rangers who are always present and a researcher who visits "
     "briefly, so the visitor fails to see the change; 'notice' reverses the contrast the "
     "sentence is building.",
     "medium", 0.94),
    (6, "secure",
     [("welcome", "collocation"), ("generous", "nuance"), ("wasted", "domain")],
     "adjective",
     "Short grants needing renewal describe funding that cannot be counted on; "
     "'generous' concerns how much money there is rather than whether it continues.",
     "hard", 0.90),
    (7, "value",
     [("cost", "collocation"), ("speed", "nuance"), ("danger", "opposite")],
     "noun",
     "The argument is that the work is worth more when it is continuous, which is its "
     "value; 'cost' would turn a point about effectiveness into one about money.",
     "hard", 0.90),
    (8, "sustained",
     [("cancelled", "opposite"), ("funded", "collocation"), ("expanded", "nuance")],
     "verb",
     "Programs running for a decade or more have been kept going, which is what sustained "
     "means; 'expanded' would describe them growing, but the sentence stresses duration.",
     "medium", 0.93),
  ],
 },
 {
  "title": "The Bogong Moth",
  "topic": "Science",
  "text":
    "Every spring, billions of bogong moths leave the plains of southern Queensland and "
    "fly south to the Australian Alps. The journey can be a thousand kilometres, and the "
    "moths ___(1)___ it only once. They spend the summer packed into cool granite caves, "
    "then return north to breed and die.\n\n"
    "How they navigate was a ___(2)___ for many years. Experiments have since shown that "
    "the moths use the Earth's magnetic field together with the pattern of stars, and that "
    "they can ___(3)___ course when one of the two is disturbed.\n\n"
    "In the caves the moths are a ___(4)___ food source. Mountain pygmy possums wake from "
    "hibernation timed to the moths' arrival, and a poor season leaves the possums with "
    "___(5)___ to eat at exactly the wrong moment.\n\n"
    "Numbers ___(6)___ sharply during the drought years after 2017, and in some caves the "
    "moths almost vanished. Researchers are still working out whether the decline was "
    "___(7)___ or the start of something longer. What is clear is that a species most "
    "people never think about ___(8)___ an entire alpine food web.",
  "items": [
    (1, "complete",
     [("abandon", "opposite"), ("describe", "domain"), ("attempt", "nuance")],
     "verb",
     "The moths make the trip a single time in their lives, so the verb must describe "
     "finishing it; 'attempt' would leave open whether they arrive, yet the next sentence "
     "has them in the caves.",
     "medium", 0.93),
    (2, "mystery",
     [("certainty", "opposite"), ("tradition", "domain"), ("difficulty", "nuance")],
     "noun",
     "The sentence sets up an explanation that came later, so the navigation was unknown "
     "at first; 'difficulty' would mean the moths found it hard rather than that "
     "scientists were puzzled.",
     "medium", 0.94),
    (3, "correct",
     [("lose", "opposite"), ("hold", "collocation"), ("repeat", "nuance")],
     "verb",
     "Being able to adjust when one cue is disturbed means fixing the heading; 'lose "
     "course' would make the experiment evidence of failure rather than skill.",
     "medium", 0.93),
    (4, "critical",
     [("trivial", "opposite"), ("seasonal", "nuance"), ("frozen", "domain")],
     "adjective",
     "The possums time their hibernation to the moths, so the food source is essential; "
     "'seasonal' is true but far too mild for a relationship the next sentence shows to "
     "be life or death.",
     "medium", 0.93),
    (5, "little",
     [("plenty", "opposite"), ("something", "nuance"), ("nothing", "overreach")],
     "pronoun",
     "A poor moth season leaves the possums short of food just as they wake; 'nothing' "
     "goes further than a poor season implies, since some moths still arrive.",
     "hard", 0.90),
    (6, "fell",
     [("rose", "opposite"), ("varied", "nuance"), ("counted", "collocation")],
     "verb",
     "The clause about moths almost vanishing shows the direction of the change; 'varied' "
     "would describe movement either way and lose the collapse being reported.",
     "medium", 0.94),
    (7, "temporary",
     [("permanent", "opposite"), ("seasonal", "collocation"), ("unusual", "nuance")],
     "adjective",
     "The sentence contrasts a short-lived dip with 'something longer', so the first "
     "option must be the brief one; 'unusual' says the decline was rare rather than "
     "short.",
     "medium", 0.93),
    (8, "supports",
     [("threatens", "opposite"), ("resembles", "domain"), ("visits", "nuance")],
     "verb",
     "The passage has shown possums depending on the moths, so the moths hold the web up; "
     "'threatens' reverses a relationship the paragraph has just described as sustaining.",
     "medium", 0.94),
  ],
 },
]


def context(passage: str, n: int, words: int = 7) -> str:
    """Cut the words either side of blank n straight out of the passage.

    Generated, never retyped: a stem cannot then quote something the passage does not
    say, and the eight stems of one passage come out textually distinct.
    """
    m = re.search(rf"_{{2,}}\({n}\)_{{2,}}", passage)
    if not m:
        raise ValueError(f"blank {n} not found in passage")
    before = passage[:m.start()].replace("\n", " ").split()[-words:]
    after = passage[m.end():].replace("\n", " ").split()[:words]
    return f"{' '.join(before)} ______ {' '.join(after)}"


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
