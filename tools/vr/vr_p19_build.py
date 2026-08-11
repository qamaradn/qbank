#!/usr/bin/env python3
"""Builds vr_vic_acer_p19.json — 30 sentence-completion questions (TASK §3.4).

A category the bank held nothing of. §3.4 puts it at 15% of the VIC paper and describes
it as testing "context and collocation": which word the sentence will actually accept,
not which word means roughly the right thing.

That is the design constraint. Every distractor must be a word that COULD go in the gap
grammatically -- same part of speech, same rough sense-area -- so the item is decided by
what the rest of the sentence demands. A distractor that does not fit the slot at all is
eliminated without reading the sentence, which is the failure this category is most prone
to.

target_word carries the KEY here, so vr_finalise bans a distractor declared 'synonym':
a synonym of the target would fill the blank equally well and be a second answer.
"""
import datetime
import json
import pathlib
import sys
import uuid

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/verbal_reasoning/generated"
NN = 19
BOOK = "vr_vic_acer"
CATEGORY = "sentence_completion"
LABEL = "Sentence completion"
NOW = datetime.datetime(2026, 8, 11, 12, 0, 0, tzinfo=datetime.timezone.utc) \
    .isoformat().replace("+00:00", "Z")

# (key, sentence with ______, [(distractor, relation) x3], explanation, difficulty, conf)
ITEMS = [
 ("adjourn", "The chair moved to ______ the meeting until the following Tuesday.",
  [("adjoin", "form"), ("cancel", "opposite"), ("minute", "collocation")],
  "A meeting is adjourned when it is broken off to resume later, which 'until Tuesday' requires; 'cancel' would end it with no resumption.", "medium", 0.93),
 ("appease", "A written apology did little to ______ the neighbours.",
  [("applaud", "form"), ("enrage", "opposite"), ("notify", "domain")],
  "To appease is to calm somebody's anger, which is what an apology attempts; 'notify' would only tell them something.", "medium", 0.93),
 ("ascertain", "Inspectors could not ______ how long the crack had been there.",
  [("ascend", "form"), ("conceal", "opposite"), ("repair", "nuance")],
  "To ascertain is to find out for certain, which is what an inspection tries to do; 'repair' is the action that might follow.", "medium", 0.93),
 ("brandish", "He would ______ the old racquet whenever the story came up.",
  [("banish", "form"), ("conceal", "opposite"), ("polish", "domain")],
  "To brandish is to wave something about for effect, which suits a story-telling flourish; 'conceal' is the opposite behaviour.", "medium", 0.92),
 ("chide", "She would ______ them gently for leaving the gate open.",
  [("chime", "form"), ("praise", "opposite"), ("fine", "overreach")],
  "To chide is to scold mildly, which 'gently' confirms; 'fine' would impose a penalty rather than express disapproval.", "medium", 0.93),
 ("denounce", "Several members stood up to ______ the proposal in the strongest terms.",
  [("announce", "form"), ("endorse", "opposite"), ("amend", "nuance")],
  "To denounce is to condemn publicly, which 'in the strongest terms' calls for; 'announce' merely makes something known.", "medium", 0.94),
 ("disband", "The committee voted to ______ at the end of the season.",
  [("disbar", "form"), ("form", "opposite"), ("reconvene", "nuance")],
  "A group disbands when it breaks up for good, which an end-of-season vote suggests; 'reconvene' would mean meeting again.", "medium", 0.93),
 ("elapse", "Four hours will ______ before the next bus reaches the turn-off.",
  [("collapse", "form"), ("remain", "nuance"), ("hasten", "opposite")],
  "Time elapses as it passes, which is the specific word for a stretch going by; 'remain' would describe time still left rather than time passing.", "medium", 0.92),
 ("envisage", "Nobody could ______ the site being ready before December.",
  [("envelop", "form"), ("recall", "opposite"), ("inspect", "nuance")],
  "To envisage is to picture something happening in the future, which a completion date is; 'recall' looks backwards instead.", "medium", 0.93),
 ("exhale", "Divers are told to ______ steadily on the way up.",
  [("exhume", "form"), ("inhale", "opposite"), ("ascend", "collocation")],
  "To exhale is to breathe out, which is the instruction for a controlled ascent; 'ascend' is what the diver is already doing.", "medium", 0.94),
 ("garner", "The petition managed to ______ nine hundred signatures in a fortnight.",
  [("garnish", "form"), ("shed", "opposite"), ("verify", "nuance")],
  "To garner is to gather in a quantity of something, which a signature count is; 'verify' would mean checking the signatures rather than collecting them.", "medium", 0.92),
 ("impart", "The older hands would ______ what they knew over a season or two.",
  [("impale", "form"), ("withhold", "opposite"), ("record", "nuance")],
  "To impart knowledge is to pass it on to others, which is what mentoring does; 'withhold' is the opposite behaviour.", "medium", 0.93),
 ("inflict", "A single hailstorm can ______ more damage than a whole dry summer.",
  [("inflect", "form"), ("repair", "opposite"), ("survive", "nuance")],
  "To inflict damage is to cause it, which is what a storm does; 'repair' would undo it instead.", "medium", 0.94),
 ("juggle", "Most of the volunteers ______ the roster around shift work.",
  [("joggle", "form"), ("abandon", "opposite"), ("publish", "collocation")],
  "To juggle commitments is to keep several going at once, which fitting a roster around shifts requires; 'publish' is what the club does with the roster.", "medium", 0.93),
 ("navigate", "It takes local knowledge to ______ the channel at low tide.",
  [("measure", "nuance"), ("navigable", "form"), ("dredge", "domain")],
  "To navigate is to find a safe course through, which local knowledge serves; 'measure' would mean charting the depth rather than steering a course through.", "medium", 0.91),
 ("offset", "Rainwater tanks will ______ some of the increase in the water bill.",
  [("outset", "form"), ("double", "opposite"), ("estimate", "nuance")],
  "To offset a cost is to cancel part of it out, which tanks do to a bill; 'estimate' is only working out what the bill will be.", "medium", 0.93),
 ("overhaul", "The engine will need a full ______ before the next season.",
  [("overhang", "form"), ("neglect", "opposite"), ("overheat", "domain")],
  "An overhaul is a thorough strip-down and rebuild, which 'full' signals; 'overheat' is not something an engine is given.", "medium", 0.93),
 ("penetrate", "Very little light can ______ the canopy at that height.",
  [("penalise", "form"), ("reflect", "nuance"), ("block", "opposite")],
  "To penetrate is to pass through something dense, which light struggles to do here; 'reflect' would bounce it back instead.", "medium", 0.93),
 ("procure", "The club had to ______ a second set of goalposts before the finals.",
  [("procrastinate", "form"), ("discard", "opposite"), ("endure", "domain")],
  "To procure is to obtain something with some effort, which sourcing posts before finals is; 'endure' is not something done to equipment at all.", "medium", 0.93),
 ("ration", "Crews had to ______ the drinking water for the last two days.",
  [("rational", "form"), ("squander", "opposite"), ("purify", "nuance")],
  "To ration is to limit each person's share of a scarce supply, which two days short of water demands; 'purify' is a different treatment of the same water.", "medium", 0.94),
 ("reclaim", "The council plans to ______ the strip of land behind the depot.",
  [("recline", "form"), ("surrender", "opposite"), ("survey", "nuance")],
  "To reclaim land is to take it back into use, which is the council's plan; 'survey' would only measure it.", "medium", 0.93),
 ("relinquish", "She was reluctant to ______ the role after eight seasons.",
  [("replenish", "form"), ("retain", "opposite"), ("share", "nuance")],
  "To relinquish is to give something up entirely, which is what leaving a role means; 'share' would keep part of it.", "medium", 0.93),
 ("resemble", "From the ridge the two peaks ______ each other almost exactly.",
  [("reassemble", "form"), ("differ", "opposite"), ("overlook", "domain")],
  "To resemble is to look like, which is what 'almost exactly' measures; 'differ' states the reverse.", "medium", 0.94),
 ("retrieve", "The dog was trained to ______ from thick cover.",
  [("relieve", "form"), ("abandon", "opposite"), ("point", "domain")],
  "To retrieve is to fetch something back, which is the specific working task; 'point' is a different gundog behaviour altogether.", "medium", 0.93),
 ("sever", "The storm was strong enough to ______ the cable at the pole.",
  [("severe", "form"), ("splice", "opposite"), ("sway", "domain")],
  "To sever is to cut right through, which is what breaking a cable means; 'splice' is joining two ends together.", "medium", 0.94),
 ("simmer", "Let the sauce ______ for another twenty minutes.",
  [("shimmer", "form"), ("freeze", "opposite"), ("season", "domain")],
  "To simmer is to cook just below boiling, which twenty more minutes suits; 'season' is adding flavour rather than applying heat.", "medium", 0.94),
 ("smother", "Wet hessian was used to ______ the last of the flames.",
  [("smoulder", "form"), ("fan", "opposite"), ("scorch", "domain")],
  "To smother a fire is to cut off its air, which wet hessian does; 'fan' would feed the flames instead.", "medium", 0.94),
 ("submerge", "Spring tides ______ the lower track twice a month.",
  [("submit", "form"), ("expose", "opposite"), ("erode", "domain")],
  "To submerge is to cover completely with water, which a spring tide does to a low track; 'erode' would wear it away over time.", "medium", 0.94),
 ("taper", "The path begins to ______ once it passes the last hut.",
  [("tamper", "form"), ("widen", "opposite"), ("climb", "domain")],
  "To taper is to become gradually narrower, which is what happens past the hut; 'climb' describes a change in height, not width.", "medium", 0.93),
 ("unearth", "Roadworks managed to ______ a bottle dump from the 1890s.",
  [("unearned", "form"), ("bury", "opposite"), ("catalogue", "domain")],
  "To unearth is to dig something up, which roadworks do by accident; 'catalogue' is what a museum then does with the find.", "medium", 0.93),
]


def build():
    out = []
    for key, sentence, distractors, expl, diff, conf in ITEMS:
        assert "______" in sentence, key
        opts = [key] + [d for d, _ in distractors]
        out.append({
            "id": str(uuid.uuid4()),
            "subject": "verbal_reasoning",
            "stem": f"{sentence} Which word best completes the sentence?",
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
            "target_word": key,
            "relations": {d: r for d, r in distractors},
        })
    return out


if __name__ == "__main__":
    GEN.mkdir(parents=True, exist_ok=True)
    qs = build()
    path = GEN / f"{BOOK}_p{NN}.json"
    path.write_text(json.dumps(qs, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(qs)} questions -> {path}")
