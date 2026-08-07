#!/usr/bin/env python3
"""Builds rc_nsw_cloze_p2.json — 4 cloze passages x 8 blanks = 32 questions (TASK §5).

Same rules as rc_cloze_p1_build.py. Relation sets are rotated deliberately: p1's first
build put 28 of 32 questions on (domain, nuance, opposite) and was rejected.
"""
import datetime
import json
import pathlib
import re
import sys
import uuid

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.rc.rc_cloze_p1_build import context  # noqa: E402  — cut the stem from the passage

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/reading_comprehension/generated"
NN = 2
BOOK = "rc_nsw_cloze"
CATEGORY = "vocabulary_cloze"
LABEL = "Vocabulary cloze"
NOW = datetime.datetime(2026, 8, 4, 20, 0, 0, tzinfo=datetime.timezone.utc) \
    .isoformat().replace("+00:00", "Z")

BLANK_RE = re.compile(r"_{2,} \((\d+)\) _{2,}")

PASSAGES = [
 {
  "title": "The Flying Doctor",
  "topic": "Australian History",
  "text":
    "In 1928 a minister named John Flynn began an air service for people living in the "
    "outback. Before it existed, a station hand with a broken leg might wait days for "
    "help, and the ___ (1) ___ was often measured in hundreds of kilometres.\n\n"
    "Flynn's idea depended on two inventions. The first was the aeroplane. The second was "
    "a pedal-powered radio, ___ (2) ___ by Alfred Traeger, which let a homestead call for "
    "assistance without mains electricity. Operators pedalled to generate current while "
    "they spoke.\n\n"
    "Early flights were ___ (3) ___. There were no sealed runways, so pilots landed on claypans "
    "and paddocks, sometimes guided in at night by car headlights. Doctors ___ (4) ___ "
    "surgery on kitchen tables, and the aircraft carried only what could be lifted aboard "
    "by hand.\n\n"
    "The service ___ (5) ___ steadily through the following decades. Today the Royal Flying "
    "Doctor Service runs a fleet of pressurised aircraft, and its clinics reach communities "
    "that have no ___ (6) ___ doctor of their own. It also runs a telephone health line, so "
    "that ___ (7) ___ advice can be given before an aircraft is sent.\n\n"
    "Flynn called his plan a mantle of safety spread across the inland. Nearly a century on, "
    "that description still ___ (8) ___ what the service does.",
  "items": [
    (1, "distance", [("cost", "domain"), ("delay", "nuance"), ("help", "collocation")],
     "noun",
     "The sentence measures the problem in kilometres, which is a distance; 'delay' is "
     "measured in days and is already covered by the waiting mentioned just before.",
     "medium", 0.93),
    (2, "designed", [("destroyed", "opposite"), ("purchased", "domain"), ("described", "collocation")],
     "verb",
     "Traeger is credited with creating the pedal radio, which is what designing it means; "
     "'purchased' would make him a buyer rather than the inventor the sentence names.",
     "medium", 0.94),
    (3, "dangerous", [("routine", "opposite"), ("expensive", "domain"), ("frequent", "nuance")],
     "adjective",
     "Landing on claypans by car headlight describes real risk, which the next sentences "
     "illustrate; 'expensive' says nothing about the hazards being listed.",
     "medium", 0.94),
    (4, "performed", [("avoided", "opposite"), ("scheduled", "collocation"), ("attempted", "nuance")],
     "verb",
     "Doctors carried out operations wherever they landed, which performing surgery means; "
     "'attempted' would leave open whether the surgery happened at all.",
     "medium", 0.93),
    (5, "expanded", [("shrank", "opposite"), ("travelled", "domain"), ("improved", "nuance")],
     "verb",
     "A fleet of aircraft and clinics across the inland describes growth over decades; "
     "'improved' says the service got better without saying it got bigger, which is what "
     "the paragraph goes on to describe.",
     "medium", 0.93),
    (6, "resident", [("visiting", "opposite"), ("qualified", "nuance"), ("local", "collocation")],
     "adjective",
     "The point is that these communities have nobody living there permanently, so the "
     "service flies in; 'qualified' would suggest the doctors they had were untrained.",
     "hard", 0.90),
    (7, "immediate", [("delayed", "opposite"), ("written", "domain"), ("medical", "collocation")],
     "adjective",
     "The phone line gives help straight away, before an aircraft is needed; 'medical' sits "
     "naturally beside advice but does not explain why a phone line is useful.",
     "medium", 0.93),
    (8, "captures", [("misses", "opposite"), ("repeats", "domain"), ("exaggerates", "overreach")],
     "verb",
     "The closing sentence says Flynn's phrase is still accurate, so it expresses the "
     "service well; 'exaggerates' would say the phrase overstates what the service does.",
     "hard", 0.90),
  ],
 },
 {
  "title": "Cane Toads",
  "topic": "Environment",
  "text":
    "Cane toads were brought to Queensland in 1935 to control beetles that were damaging "
    "sugar cane. The plan ___ (1) ___ almost immediately. The beetles lived high on the cane "
    "stalks, and the toads could not climb.\n\n"
    "What the toads could do was breed. A single female lays up to thirty thousand eggs at "
    "a time, and the young toads are ___ (2) ___ to the dry conditions of northern Australia. "
    "The front of their range has moved west across the Top End at a rate that ___ (3) ___ "
    "researchers, reaching Western Australia in 2009.\n\n"
    "The damage is ___ (4) ___. Cane toads carry poison glands behind the head, and native "
    "predators that have never encountered them have no ___ (5) ___ against the toxin. "
    "Northern quoll numbers collapsed as the toads arrived, and goannas and freshwater "
    "crocodiles were also ___ (6) ___.\n\n"
    "Some native species are now adapting. Crows have learned to flip the toads over and "
    "eat only the parts that are ___ (7) ___, and quolls in some areas appear to be "
    "developing a reluctance to attack them at all. Whether this happens quickly enough to "
    "___ (8) ___ the worst losses is still unknown.",
  "items": [
    (1, "failed", [("succeeded", "opposite"), ("began", "domain"), ("stalled", "nuance")],
     "verb",
     "The next sentence explains that the toads could not reach the beetles, so the plan "
     "did not work; 'stalled' would suggest it paused rather than never worked at all.",
     "medium", 0.94),
    (2, "suited", [("harmful", "domain"), ("exposed", "opposite"), ("confined", "collocation")],
     "adjective",
     "The toads thrive in the dry north, which is what being suited to conditions means; "
     "'exposed' would mean the conditions endangered them, yet their range is spreading.",
     "medium", 0.93),
    (3, "surprised", [("expected", "opposite"), ("employed", "domain"), ("worried", "collocation")],
     "verb",
     "Crossing the Top End faster than anyone predicted is what surprised the researchers; "
     "'worried' fits the tone but the sentence is about the speed being unexpected.",
     "medium", 0.92),
    (4, "severe", [("minor", "opposite"), ("recent", "domain"), ("total", "overreach")],
     "adjective",
     "Collapsing quoll numbers describe serious harm; 'total' would mean nothing survived, "
     "which the later paragraph about adapting species contradicts.",
     "medium", 0.93),
    (5, "defence", [("interest", "domain"), ("weakness", "opposite"), ("warning", "nuance")],
     "noun",
     "Predators that have never met the toad have no protection from its poison; 'warning' "
     "would mean they were told about it, which is not what a predator lacks.",
     "medium", 0.94),
    (6, "affected", [("unharmed", "opposite"), ("counted", "domain"), ("devastated", "overreach")],
     "verb",
     "Goannas and crocodiles suffered too, which 'affected' states without overstating; "
     "'devastated' claims more than the sentence, which reserves collapse for the quolls.",
     "hard", 0.90),
    (7, "safe", [("poisonous", "opposite"), ("visible", "domain"), ("tender", "collocation")],
     "adjective",
     "The crows avoid the poison glands and eat the rest, so they take the harmless parts; "
     "'tender' goes naturally with eating but does not explain flipping the toad over.",
     "medium", 0.93),
    (8, "prevent", [("cause", "opposite"), ("record", "domain"), ("delay", "nuance")],
     "verb",
     "The question is whether adaptation can stop the worst losses happening; 'delay' would "
     "mean the losses still occur, only later, which is a weaker claim than the sentence "
     "is weighing.",
     "medium", 0.93),
  ],
 },
 {
  "title": "The Snowy Scheme",
  "topic": "Australian History",
  "text":
    "The Snowy Mountains Scheme took twenty-five years to build. Begun in 1949, it "
    "___ (1) ___ the Snowy River inland through a system of tunnels so that water could "
    "generate electricity and then irrigate farmland.\n\n"
    "Most of the work was ___ (2) ___. Sixteen large dams, seven power stations and more "
    "than a hundred and forty kilometres of tunnel were cut through rock, much of it by "
    "hand-held drills. More than a hundred thousand people worked on the scheme, and about "
    "two-thirds of them came from overseas.\n\n"
    "They arrived from more than thirty countries, many from a Europe still ___ (3) ___ from "
    "the war. Camps were built at Cooma and Khancoban, and workers who shared no common "
    "language learned to ___ (4) ___ through gesture and diagram. One hundred and twenty-one "
    "people died during construction, a toll that would be ___ (5) ___ today.\n\n"
    "The scheme is still ___ (6) ___ as an engineering achievement, though its effect on the "
    "river itself was severe. For decades only a ___ (7) ___ of the original flow reached the "
    "lower Snowy. Environmental releases begun in 2002 have since returned some water to "
    "the channel, and the argument over how much the river should receive ___ (8) ___ "
    "unresolved today.",
  "items": [
    (1, "diverted", [("followed", "domain"), ("blocked", "nuance"), ("released", "opposite")],
     "verb",
     "Sending the river inland through tunnels is diverting it; 'blocked' would stop the "
     "water rather than redirect it, and the sentence has it reaching farmland.",
     "medium", 0.93),
    (2, "underground", [("overseas", "domain"), ("exposed", "opposite"), ("temporary", "nuance")],
     "adjective",
     "Tunnels cut through rock are below the surface, which the next sentence details; "
     "'overseas' describes where the workers came from, not where the work was done.",
     "medium", 0.93),
    (3, "recovering", [("benefiting", "opposite"), ("departing", "domain"), ("suffering", "collocation")],
     "verb",
     "Post-war Europe was slowly rebuilding, which is what recovering from a war means; "
     "'suffering' sits naturally beside war but the sentence describes the years after it.",
     "medium", 0.92),
    (4, "communicate", [("compete", "domain"), ("misunderstand", "opposite"), ("argue", "collocation")],
     "verb",
     "Gesture and diagram are ways of getting meaning across without shared words; "
     "'argue' is something people do beside each other but does not explain the diagrams.",
     "medium", 0.94),
    (5, "unacceptable", [("unavoidable", "nuance"), ("celebrated", "opposite"), ("recorded", "domain")],
     "adjective",
     "The sentence contrasts past practice with modern standards, so such a death toll "
     "would not be tolerated now; 'unavoidable' would excuse the deaths rather than "
     "condemn them.",
     "hard", 0.90),
    (6, "admired", [("forgotten", "opposite"), ("operated", "domain"), ("expanded", "collocation")],
     "verb",
     "The clause 'though its effect was severe' sets up praise being qualified, so the "
     "scheme is held in regard; 'operated' is true but makes no contrast with the criticism.",
     "medium", 0.92),
    (7, "fraction", [("majority", "opposite"), ("measurement", "domain"), ("portion", "nuance")],
     "noun",
     "Only a small part of the original flow reached the lower river, which is what a "
     "fraction conveys; 'portion' gives no sense of how little, and the sentence is "
     "describing severe loss.",
     "hard", 0.90),
    (8, "remains", [("becomes", "nuance"), ("settles", "opposite"), ("flows", "collocation")],
     "verb",
     "The argument has not been resolved and is still going, which is what remaining "
     "unresolved means; 'settles' would say the dispute had ended, which the sentence denies.",
     "medium", 0.92),
  ],
 },
 {
  "title": "Wombat Burrows",
  "topic": "Australian Wildlife",
  "text":
    "A wombat burrow is far larger than most people ___ (1) ___. Tunnels can run twenty "
    "metres, branch several times, and hold chambers wide enough for an adult wombat to "
    "turn around in.\n\n"
    "The burrow keeps a ___ (2) ___ temperature all year. Outside, the ground surface may "
    "swing between five and forty degrees across a single day, while a metre down the air "
    "___ (3) ___ close to the annual average. That stability is what allows wombats to sleep "
    "through the heat and forage after dark.\n\n"
    "After the 2019 and 2020 fires, cameras placed at burrow entrances recorded something "
    "___ (4) ___. Rock wallabies, echidnas, lizards and even small birds were photographed "
    "entering wombat burrows in burnt country. The wombats did not appear to ___ (5) ___ "
    "them.\n\n"
    "Researchers were careful about the claim that wombats deliberately ___ (6) ___ other "
    "animals. A burrow is simply the coolest and safest space available, and its owner may "
    "___ (7) ___ visitors rather than invite them. Even so, in a landscape stripped of cover, "
    "a network of deep tunnels is a ___ (8) ___ that many species now depend on.",
  "items": [
    (1, "imagine", [("mention", "domain"), ("know", "collocation"), ("exaggerate", "opposite")],
     "verb",
     "The sentence says the burrows exceed what people picture, which is imagining; 'know' "
     "would be about facts rather than the mental picture the comparison relies on.",
     "medium", 0.92),
    (2, "steady", [("shifting", "opposite"), ("comfortable", "nuance"), ("recorded", "domain")],
     "adjective",
     "The contrast with a forty-degree daily swing outside shows the burrow barely changes; "
     "'comfortable' is true but does not name the constancy the next sentence measures.",
     "medium", 0.93),
    (3, "stays", [("rises", "domain"), ("swings", "opposite"), ("drops", "collocation")],
     "verb",
     "A metre down the temperature holds near the yearly average, which is staying; "
     "'swings' describes the surface conditions the sentence is contrasting it with.",
     "medium", 0.94),
    (4, "unexpected", [("ordinary", "opposite"), ("expensive", "domain"), ("shocking", "overreach")],
     "adjective",
     "Other species sheltering in wombat burrows was a surprise worth reporting; 'shocking' "
     "overstates a finding researchers went on to describe cautiously.",
     "medium", 0.92),
    (5, "evict", [("welcome", "opposite"), ("notice", "nuance"), ("follow", "domain")],
     "verb",
     "The wombats let the visitors stay, so they did not drive them out; 'notice' would "
     "mean they failed to see them, which cameras at the entrance do not show.",
     "hard", 0.90),
    (6, "shelter", [("abandon", "opposite"), ("hunt", "domain"), ("tolerate", "nuance")],
     "verb",
     "The claim being questioned is that wombats protect other animals on purpose; "
     "'tolerate' is what the next sentence offers instead, so it cannot also be the claim "
     "being doubted.",
     "hard", 0.89),
    (7, "endure", [("encourage", "opposite"), ("expect", "nuance"), ("escort", "collocation")],
     "verb",
     "The sentence contrasts putting up with visitors against inviting them, so the wombat "
     "merely puts up with them; 'expect' would mean it anticipates them arriving.",
     "hard", 0.89),
    (8, "refuge", [("hazard", "opposite"), ("burden", "domain"), ("convenience", "nuance")],
     "noun",
     "In burnt country the tunnels are a place of safety many species rely on; "
     "'convenience' is far too mild for something the sentence says they depend on.",
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
