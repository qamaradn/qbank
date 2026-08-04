#!/usr/bin/env python3
"""Builds vr_vic_acer_p2.json — 21 vocabulary-in-context questions (TASK §3.1).

Same design rules as vr_p1_build.py: parallel options, contextual Australian stems, and
three distractors each wrong in a declared, different way.
"""
import datetime
import json
import pathlib
import sys
import uuid

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/verbal_reasoning/generated"
NN = 2
BOOK = "vr_vic_acer"
CATEGORY = "vocabulary_synonym"
LABEL = "Vocabulary in context / synonyms"
NOW = datetime.datetime(2026, 8, 4, 11, 0, 0, tzinfo=datetime.timezone.utc) \
    .isoformat().replace("+00:00", "Z")

ITEMS = [
 ("coax",
  "It took twenty minutes to coax the frightened wallaby out of the culvert and back into "
  "the scrub.",
  "gently persuade",
  [("firmly order", "opposite"), ("quietly follow", "domain"), ("carefully lift", "nuance")],
  "To coax is to persuade gradually and gently, which is why it took so long; 'carefully "
  "lift' describes handling the animal physically, but nobody touched it.",
  "medium", 0.94),

 ("dwindle",
  "Water in the tank continued to dwindle through February, and by the end of March the "
  "taps ran dry.",
  "steadily shrink",
  [("sharply spike", "opposite"), ("slowly settle", "nuance"), ("quietly kindle", "form")],
  "To dwindle is to grow less and less over time, matching a tank that emptied across two "
  "months; 'slowly settle' would mean the water was becoming still, not disappearing.",
  "medium", 0.95),

 ("feasible",
  "The engineers reported that a single-span bridge was feasible, though it would cost "
  "rather more than the council had set aside.",
  "able to be done",
  [("certain to succeed", "overreach"), ("easy to explain", "domain"), ("impossible to fund", "opposite")],
  "Feasible means capable of being done, which is consistent with a design that works but "
  "costs more than budgeted; 'certain to succeed' claims far more than the engineers did.",
  "medium", 0.93),

 ("bleak",
  "The paddocks north of Hay looked bleak after two failed seasons, with bare soil "
  "stretching away to the horizon.",
  "cold and cheerless",
  [("warm and inviting", "opposite"), ("black and stormy", "form"), ("wide and level", "domain")],
  "Bleak country is bare and dispiriting to look at, which the failed seasons explain; "
  "'wide and level' describes the shape of the land rather than its desolate feel.",
  "medium", 0.93),

 ("brisk",
  "She set off at a brisk pace along the Yarra path, overtaking other walkers without ever "
  "breaking into a run.",
  "quick and lively",
  [("slow and heavy", "opposite"), ("rough and choppy", "collocation"), ("sharp and rude", "nuance")],
  "A brisk pace is quick and energetic, which is why she passed people while still walking; "
  "'sharp and rude' is a real sense of brisk applied to manner, but not to how someone walks.",
  "medium", 0.92),

 ("elated",
  "The crew were elated when the result came through: their boat had taken the state title "
  "by a single point.",
  "overjoyed",
  [("downcast", "opposite"), ("elevated", "form"), ("relieved", "nuance")],
  "Elated means filled with joy, which fits winning a title by the narrowest margin; "
  "'relieved' is the trap, since it would mean they were glad the ordeal was over rather "
  "than thrilled to have won.",
  "hard", 0.91),

 ("ponder",
  "The selectors took a fortnight to ponder the nominations before they announced the "
  "final squad.",
  "think over",
  [("brush aside", "opposite"), ("pounce on", "form"), ("talk through", "collocation")],
  "To ponder is to consider something at length, which explains a fortnight's delay; "
  "'talk through' often accompanies a decision but describes discussion with others, "
  "whereas pondering is reflection.",
  "medium", 0.92),

 ("scarce",
  "Fresh water became scarce on the third day of the trek, and the group began rationing "
  "what was left in the drums.",
  "hard to come by",
  [("easy to find", "opposite"), ("scared away", "form"), ("poor in quality", "nuance")],
  "Scarce means available only in small amounts, which is why rationing began; 'poor in "
  "quality' would describe the water being bad rather than there being too little of it.",
  "medium", 0.95),

 ("vivid",
  "Her memory of the bushfire was still vivid twenty years later — the colour of the sky, "
  "the smell of the smoke, the sound of the roof.",
  "sharp and clear",
  [("dim and faded", "opposite"), ("brief and fleeting", "domain"), ("livid and angry", "form")],
  "A vivid memory is intensely clear, which the specific details demonstrate; 'brief and "
  "fleeting' describes how long a memory lasts, and this one had lasted twenty years.",
  "medium", 0.94),

 ("yield",
  "The trial plot at Horsham was expected to yield almost twice as much grain per hectare "
  "as the older variety.",
  "produce",
  [("consume", "opposite"), ("wield", "form"), ("require", "domain")],
  "To yield here is to produce a crop, which is what a trial plot is measured on; "
  "'require' would describe what the plot needs as input rather than what it gives back.",
  "medium", 0.94),

 ("barren",
  "Beyond the last fence the country turned barren, and even the hardy saltbush gave out "
  "within a kilometre.",
  "bare and infertile",
  [("rich and fertile", "opposite"), ("barred and locked", "form"), ("flat and treeless", "nuance")],
  "Barren land cannot support growth, which is why even saltbush failed; 'flat and "
  "treeless' describes country that may still be fertile, so it misses the point.",
  "medium", 0.93),

 ("adept",
  "After three seasons she was adept at reading the wind, and rarely misjudged the final "
  "leg of a race.",
  "highly skilled",
  [("poorly trained", "opposite"), ("newly adopted", "form"), ("widely admired", "domain")],
  "Adept means skilled through practice, which three seasons and few misjudgements show; "
  "'widely admired' describes what others think of her, not what she can do.",
  "medium", 0.95),

 ("ample",
  "There was ample room in the shed for both tractors, with space left over for the feed "
  "bins along the back wall.",
  "more than enough",
  [("barely enough", "nuance"), ("far too little", "opposite"), ("simple enough", "form")],
  "Ample means plentiful, which the leftover space confirms; 'barely enough' is the trap, "
  "since it would mean the tractors only just fitted and nothing else could.",
  "medium", 0.95),

 ("compel",
  "The new regulations compel every operator to log their catch before returning to port, "
  "whatever the size of the boat.",
  "force",
  [("permit", "opposite"), ("compile", "form"), ("persuade", "nuance")],
  "To compel is to require by authority, which is what regulations do; 'persuade' is the "
  "trap, since it would leave the operator free to decide, and regulations do not.",
  "medium", 0.94),

 ("console",
  "Her teammates gathered to console her once the disqualification had been confirmed by "
  "the officials.",
  "comfort",
  [("upset", "opposite"), ("consult", "form"), ("congratulate", "domain")],
  "To console someone is to ease their disappointment, which fits a disqualification; "
  "'congratulate' belongs to the same setting of results and officials but would make no "
  "sense after a loss.",
  "medium", 0.95),

 ("daunt",
  "The final climb did not daunt the junior riders, several of whom attacked it from the "
  "bottom.",
  "intimidate",
  [("reassure", "opposite"), ("dawdle", "form"), ("exhaust", "nuance")],
  "To daunt is to make someone lose their nerve, which the riders plainly did not; "
  "'exhaust' is the trap, since a climb can tire riders without frightening them at all.",
  "medium", 0.93),

 ("deplete",
  "Successive dry winters deplete the aquifer far faster than the slow recharge can "
  "replace what is taken.",
  "use up",
  [("top up", "opposite"), ("deplore", "form"), ("spread out", "domain")],
  "To deplete is to reduce a supply by using it, which is what the dry winters do to the "
  "groundwater; 'top up' describes the recharge instead, which is the opposite process.",
  "medium", 0.94),

 ("docile",
  "The rescue horses were docile enough for complete beginners, which is why the riding "
  "school agreed to take them.",
  "easily managed",
  [("hard to handle", "opposite"), ("slow to learn", "nuance"), ("kept indoors", "domain")],
  "Docile means calm and willing to be led, which is what makes a horse suitable for "
  "beginners; 'slow to learn' is a common confusion, but a docile animal may be quick to "
  "learn and simply gentle.",
  "hard", 0.91),

 ("elude",
  "The fox continued to elude the trappers, taking a different route across the ridge "
  "almost every night.",
  "slip past",
  [("run towards", "opposite"), ("allude to", "form"), ("argue with", "domain")],
  "To elude is to avoid capture by being evasive, which the changing routes describe; "
  "'allude to' means to refer to something indirectly and merely resembles the word.",
  "medium", 0.94),

 ("endorse",
  "Three former captains agreed to endorse the club's bid for a new stadium at the public "
  "meeting.",
  "publicly support",
  [("openly oppose", "opposite"), ("quietly allow", "nuance"), ("formally appoint", "domain")],
  "To endorse is to declare public support for something, which is why it happened at a "
  "public meeting; 'quietly allow' would mean merely tolerating the bid rather than "
  "backing it.",
  "medium", 0.93),

 ("erratic",
  "The old generator's output was erratic, surging one minute and fading almost to nothing "
  "the next.",
  "irregular",
  [("steady", "opposite"), ("mistaken", "form"), ("fierce", "domain")],
  "Erratic means irregular and inconsistent, which the surging and fading illustrate; "
  "'mistaken' confuses erratic with erroneous, a similar-looking word that means wrong "
  "rather than uneven.",
  "medium", 0.94),
]


def build():
    out = []
    for target, stem, key, distractors, expl, diff, conf in ITEMS:
        opts = [key] + [d for d, _ in distractors]
        out.append({
            "id": str(uuid.uuid4()),
            "subject": "verbal_reasoning",
            "stem": f"{stem} As it is used here, '{target}' most nearly means:",
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
