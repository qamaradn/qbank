#!/usr/bin/env python3
"""Builds rc_nsw_cloze_p4.json — 4 cloze passages x 8 blanks = 32 questions, completing
the §5 set at 15 passages / 120 questions.

Same rules as rc_cloze_p1_build.py. Each blank was written so that exactly one option
reads: batches 2 and 3 between them had six blanks where a distractor read as well as the
key, which no mechanical check catches — the only test is substituting the keys and
reading the passage.
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
NN = 4
BOOK = "rc_nsw_cloze"
CATEGORY = "vocabulary_cloze"
LABEL = "Vocabulary cloze"
NOW = datetime.datetime(2026, 8, 4, 22, 0, 0, tzinfo=datetime.timezone.utc) \
    .isoformat().replace("+00:00", "Z")

BLANK_RE = re.compile(r"_{2,} \((\d+)\) _{2,}")

PASSAGES = [
 {
  "title": "Reading a Rip",
  "topic": "Science",
  "text":
    "A rip is a narrow current of water flowing away from the beach. It forms when waves "
    "push water up the sand and that water has to ___ (1) ___ somewhere. Rather than draining "
    "evenly along the whole beach, it gathers into a channel and runs out through the "
    "breakers.\n\n"
    "Rips are easier to spot once you know what to look for. The water in a rip is often "
    "___ (2) ___ than the water beside it, because the channel is deeper and the sand has "
    "been scoured away. Waves also break less in a rip, so a gap in the line of white water "
    "is a useful ___ (3) ___.\n\n"
    "Swimmers caught in a rip usually make the same ___ (4) ___: they try to swim straight "
    "back to the beach against the flow. A rip can run faster than an Olympic swimmer, so "
    "this ___ (5) ___ them long before they make progress.\n\n"
    "Lifesavers give two pieces of advice. If you can stand, wade rather than swim. If you "
    "cannot, stay ___ (6) ___, float, and raise one arm so somebody on shore can see you. "
    "Most rips ___ (7) ___ within a few hundred metres, and many will carry you back towards "
    "the sand on their own. Above all, swim between the flags, where the water has been "
    "___ (8) ___ by people who read it every day.",
  "items": [
    (1, "return", [("evaporate", "domain"), ("arrive", "opposite"), ("gather", "collocation")],
     "verb",
     "Water pushed up the beach has to travel back out to sea, which returning means; "
     "'gather' is what it does next, in the following clause, not where it has to go.",
     "medium", 0.92),
    (2, "darker", [("shallower", "opposite"), ("warmer", "collocation"), ("rougher", "nuance")],
     "adjective",
     "A deeper scoured channel makes the water look different in colour, and the sentence "
     "gives depth as the reason; 'rougher' contradicts the next sentence, which says waves "
     "break less in a rip.",
     "medium", 0.92),
    (3, "sign", [("cause", "opposite"), ("barrier", "domain"), ("guess", "nuance")],
     "noun",
     "A gap in the white water tells you a rip is there, which makes it something to read; "
     "'cause' reverses it, since the rip produces the gap rather than the gap producing "
     "the rip.",
     "medium", 0.93),
    (4, "mistake", [("choice", "nuance"), ("discovery", "domain"), ("success", "opposite")],
     "noun",
     "Swimming against a current faster than they are goes badly, which the next sentence "
     "spells out; 'choice' is neutral and misses that the passage is naming an error.",
     "medium", 0.93),
    (5, "exhausts", [("assists", "opposite"), ("reaches", "collocation"), ("worries", "nuance")],
     "verb",
     "Swimming hard against a faster current uses up your strength, which is why the advice "
     "that follows is to float; 'worries' describes a feeling rather than what the water "
     "does to a swimmer's body.",
     "medium", 0.92),
    (6, "calm", [("panicked", "opposite"), ("silent", "nuance"), ("upright", "collocation")],
     "adjective",
     "Floating and signalling both require keeping your head, which staying calm means; "
     "'silent' would work against raising the alarm the same sentence recommends.",
     "medium", 0.93),
    (7, "weaken", [("strengthen", "opposite"), ("appear", "domain"), ("vanish", "overreach")],
     "verb",
     "The advice depends on the current easing off a short way out; 'vanish' claims the rip "
     "disappears entirely, which is more than a few hundred metres of weakening.",
     "hard", 0.90),
    (8, "assessed", [("ignored", "opposite"), ("cleaned", "collocation"), ("enjoyed", "nuance")],
     "verb",
     "The flags mark water that lifesavers have judged and chosen, which assessing means; "
     "'cleaned' describes tidying the beach rather than reading the conditions.",
     "medium", 0.92),
  ],
 },
 {
  "title": "Rooftop Solar",
  "topic": "Science",
  "text":
    "Australia has more rooftop solar per person than any other country. Roughly one house "
    "in three now ___ (1) ___ its own electricity, a share that would have seemed impossible "
    "twenty years ago.\n\n"
    "The reasons are partly physical. Australia receives more sunlight per square metre "
    "than almost anywhere else, and most people live in detached houses with ___ (2) ___ roof "
    "space. The reasons are also economic: panel prices have ___ (3) ___ by roughly ninety "
    "per cent since 2010.\n\n"
    "The scale of it has created an unusual ___ (4) ___. On mild sunny days in spring, so "
    "much solar power flows into the grid that demand from coal and gas plants falls close to "
    "zero around midday. The grid was designed for electricity moving in one direction, "
    "from a few big stations outward, and it must now ___ (5) ___ millions of small sources "
    "sending power the other way.\n\n"
    "Batteries are one ___ (6) ___. Storing the midday surplus and releasing it in the "
    "evening flattens the curve, and household battery installations have risen sharply. "
    "Another approach is to ___ (7) ___ demand into the middle of the day, by running hot "
    "water systems and charging cars while the sun is high. Neither alone is ___ (8) ___, but "
    "together they make the surplus useful rather than awkward.",
  "items": [
    (1, "generates", [("consumes", "opposite"), ("purchases", "collocation"), ("requires", "nuance")],
     "verb",
     "A house with solar panels produces power for itself, which generating means; "
     "'purchases' describes buying it from someone else, which is what solar avoids.",
     "medium", 0.93),
    (2, "ample", [("limited", "opposite"), ("expensive", "domain"), ("sloping", "collocation")],
     "adjective",
     "Detached houses give plenty of room for panels, which is why the housing type is "
     "mentioned; 'sloping' describes the shape of a roof, not how much of it there is.",
     "medium", 0.92),
    (3, "collapsed", [("risen", "opposite"), ("varied", "nuance"), ("stabilised", "collocation")],
     "verb",
     "A ninety per cent drop is a steep fall, which collapsing conveys; 'varied' would "
     "describe movement in both directions and lose the size of the fall.",
     "medium", 0.93),
    (4, "problem", [("solution", "opposite"), ("industry", "collocation"), ("delay", "nuance")],
     "noun",
     "What follows describes a grid struggling with power flowing the wrong way, which is "
     "a difficulty; 'solution' reverses the sense the rest of the paragraph builds.",
     "medium", 0.93),
    (5, "accommodate", [("reject", "opposite"), ("purchase", "collocation"), ("count", "nuance")],
     "verb",
     "The grid has to cope with millions of small feed-in sources it was not built for; "
     "'count' would mean merely tallying them, which does not address the design problem.",
     "hard", 0.90),
    (6, "answer", [("obstacle", "opposite"), ("expense", "collocation"), ("experiment", "nuance")],
     "noun",
     "Batteries are offered as a way of fixing the midday surplus, and a second approach "
     "follows; 'experiment' would suggest it is untested, but installations are already "
     "rising sharply.",
     "medium", 0.92),
    (7, "shift", [("reduce", "nuance"), ("record", "collocation"), ("freeze", "opposite")],
     "verb",
     "Running appliances at midday moves demand to a different time rather than lowering "
     "it; 'reduce' would mean using less power overall, which is not what the examples do.",
     "hard", 0.90),
    (8, "sufficient", [("useless", "opposite"), ("popular", "collocation"), ("affordable", "nuance")],
     "adjective",
     "The sentence says the two approaches work where neither would be enough alone; "
     "'affordable' introduces cost, which this sentence is not weighing.",
     "medium", 0.92),
  ],
 },
 {
  "title": "Mawson's Huts",
  "topic": "Australian History",
  "text":
    "At Cape Denison in Antarctica stand four timber buildings put up by Douglas Mawson's "
    "expedition in 1912. The site is one of the ___ (1) ___ places on Earth. Winds pour off "
    "the ice plateau and reach the coast at an average of more than sixty kilometres an "
    "hour, gusting to well over three hundred.\n\n"
    "The expedition had not ___ (2) ___ this. Mawson chose the site from a ship in calm "
    "weather, and the wind began within days of the huts going up. Men learned to walk "
    "leaning forward at an angle that looked ___ (3) ___ in photographs, and to fit their "
    "boots with crampons simply to cross open ground.\n\n"
    "The huts ___ (4) ___, which is remarkable given the conditions. Ice filled the interior "
    "over the following century, and that ice both damaged the timber and ___ (5) ___ it, "
    "sealing the buildings against the worst of the weather.\n\n"
    "Conservation teams now visit for a few weeks each summer. Their work is ___ (6) ___ by "
    "the same wind that has preserved the site, and by a rule that nothing may be "
    "___ (7) ___ from Antarctica. Materials must be carried in and all waste carried out. The "
    "aim is not to make the huts look new but to ___ (8) ___ them roughly as the expedition "
    "left them.",
  "items": [
    (1, "windiest", [("calmest", "opposite"), ("coldest", "collocation"), ("emptiest", "nuance")],
     "adjective",
     "The next sentence gives wind speeds and nothing else, so the claim is about wind; "
     "'coldest' is plausible for Antarctica but is not what the figures measure.",
     "medium", 0.93),
    (2, "expected", [("survived", "collocation"), ("welcomed", "nuance"), ("caused", "opposite")],
     "verb",
     "Mawson picked the site in calm weather and the wind surprised them, so they had not "
     "foreseen it; 'welcomed' would mean they knew and were pleased, which the surprise "
     "rules out.",
     "medium", 0.92),
    (3, "impossible", [("ordinary", "opposite"), ("expensive", "domain"), ("uncomfortable", "nuance")],
     "adjective",
     "Leaning far enough forward to stay upright in such wind looks like something that "
     "could not be done; 'uncomfortable' is true but far too mild for a photograph worth "
     "remarking on.",
     "medium", 0.92),
    (4, "survive", [("collapsed", "opposite"), ("expanded", "domain"), ("weakened", "nuance")],
     "verb",
     "The paragraph goes on to explain how the ice sealed them, so the buildings are still "
     "standing; 'weakened' is true of the timber but does not explain why it is remarkable.",
     "medium", 0.92),
    (5, "protected", [("exposed", "opposite"), ("filled", "collocation"), ("melted", "domain")],
     "verb",
     "The ice is described as doing two opposite things, and the second is sealing the huts "
     "against the weather; 'filled' repeats what the sentence has already said the ice did.",
     "hard", 0.90),
    (6, "limited", [("assisted", "opposite"), ("funded", "collocation"), ("delayed", "nuance")],
     "verb",
     "Wind and a strict rule both restrict what the teams can do, which limiting means; "
     "'delayed' would mean the work happens later, but the constraints shape the work "
     "itself.",
     "medium", 0.92),
    (7, "removed", [("returned", "opposite"), ("photographed", "collocation"), ("purchased", "nuance")],
     "verb",
     "The next sentence explains that all waste must be carried out, so nothing may be "
     "taken away; 'photographed' is plainly permitted, since the passage mentions "
     "photographs.",
     "medium", 0.93),
    (8, "stabilise", [("rebuild", "nuance"), ("abandon", "opposite"), ("decorate", "domain")],
     "verb",
     "The aim is to hold the huts in their present state rather than restore them, which "
     "the contrast with 'look new' establishes; 'rebuild' is exactly what the sentence "
     "rules out.",
     "hard", 0.89),
  ],
 },
 {
  "title": "Seagrass Meadows",
  "topic": "Environment",
  "text":
    "Seagrass is not seaweed. It is a flowering plant with roots, and it grows in shallow "
    "water where enough light ___ (1) ___ the seabed. Australia holds some of the largest "
    "meadows in the world, and one plant in Shark Bay covers nearly two hundred square "
    "kilometres, making it among the largest ___ (2) ___ organisms known.\n\n"
    "The meadows do several jobs at once. Their roots ___ (3) ___ the sediment, which keeps "
    "the water clear. Their leaves shelter juvenile fish, so a healthy meadow ___ (4) ___ the "
    "fisheries offshore. They also store carbon in the mud beneath them at a rate that "
    "___ (5) ___ most forests.\n\n"
    "Seagrass is ___ (6) ___ to two things in particular. The first is anything that clouds "
    "the water, since the plants need light. The second is physical damage: boat propellers "
    "and moorings cut scars that can take decades to ___ (7) ___.\n\n"
    "Replanting is slow and expensive, so most effort now goes into protecting meadows that "
    "are still ___ (8) ___. Moorings that float above the seabed rather than dragging across "
    "it have been installed at several popular anchorages, and the scars beneath them have "
    "begun to close.",
  "items": [
    (1, "reaches", [("leaves", "opposite"), ("warms", "collocation"), ("crosses", "nuance")],
     "verb",
     "The plants grow where light gets down to the bottom, which reaching the seabed means; "
     "'warms' describes an effect of sunlight but not whether it arrives at all.",
     "medium", 0.93),
    (2, "living", [("extinct", "opposite"), ("marine", "collocation"), ("ancient", "nuance")],
     "adjective",
     "The claim compares the plant with other organisms that are alive today; 'ancient' "
     "concerns its age rather than the fact that it is still growing.",
     "medium", 0.92),
    (3, "bind", [("loosen", "opposite"), ("filter", "nuance"), ("cover", "collocation")],
     "verb",
     "Roots holding the sediment in place are what stop it clouding the water; 'filter' "
     "would clean water already carrying sediment rather than stop it lifting.",
     "hard", 0.90),
    (4, "supports", [("threatens", "opposite"), ("resembles", "domain"), ("replaces", "nuance")],
     "verb",
     "Sheltering young fish helps the fisheries further out, which supporting them means; "
     "'replaces' would put the meadow in competition with the fishery instead of feeding it.",
     "medium", 0.93),
    (5, "exceeds", [("matches", "nuance"), ("resembles", "domain"), ("trails", "opposite")],
     "verb",
     "The sentence is making a claim about seagrass outperforming forests; 'matches' would "
     "make the two equal, which is a weaker statement than the comparison intends.",
     "medium", 0.92),
    (6, "vulnerable", [("resistant", "opposite"), ("attached", "domain"), ("visible", "nuance")],
     "adjective",
     "Two threats follow immediately, so the plants are easily harmed by them; 'resistant' "
     "reverses the sense of the list that comes next.",
     "medium", 0.93),
    (7, "heal", [("appear", "opposite"), ("measure", "collocation"), ("spread", "nuance")],
     "verb",
     "Scars closing over decades describe recovery, which the last sentence confirms; "
     "'spread' would mean the damage grows rather than repairs.",
     "medium", 0.93),
    (8, "intact", [("damaged", "opposite"), ("mapped", "collocation"), ("accessible", "nuance")],
     "adjective",
     "Effort goes to meadows that have not yet been harmed, since replanting is expensive; "
     "'mapped' concerns whether they have been surveyed, not whether they are undamaged.",
     "medium", 0.93),
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
