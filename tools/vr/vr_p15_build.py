#!/usr/bin/env python3
"""Builds vr_vic_acer_p15.json — 35 vocabulary-in-context questions (TASK §3.1).

Sixth batch, completing the vocabulary share of the top-up in vic_content_taxonomy_TASK.md §5.3. The mix is
vocabulary-poor and §3.1 makes vocabulary the dominant real type at 30%, so 186 of the
341 are this category.

Calibration, from TASK §3: words a capable Year 8 meets in READING, not in a word list.
Students rated this section 8.5-9.5/10 for comfort on the 20 June 2026 paper and one
rated it 1.5/10 for difficulty, so the bank being harder than the exam is a defect, not
a margin. Exotica is refused by vr_finalise.TOO_HARD.

Every distractor declares HOW it is wrong, and the three must differ. In ~24 of 26
sampled questions in the shipped bank the three distractors were mutual synonyms and the
key was the semantic singleton, answerable without knowing the target word at all.
"""
import datetime
import json
import pathlib
import sys
import uuid

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/verbal_reasoning/generated"
NN = 15
BOOK = "vr_vic_acer"
CATEGORY = "vocabulary_synonym"
LABEL = "Vocabulary in context / synonyms"
NOW = datetime.datetime(2026, 8, 11, 10, 0, 0, tzinfo=datetime.timezone.utc) \
    .isoformat().replace("+00:00", "Z")

# (target, stem, key, [(distractor, relation) x3], explanation, difficulty, confidence)
# Relation combinations are rotated deliberately through the batch. Left to instinct the
# natural shape of a vocabulary item is opposite / lookalike / near-miss, and three
# batches running showed that is exactly the shape relation_monotony exists to refuse.
ITEMS = [
 ("pacify", "A second umpire was brought over to pacify the crowd behind the goals.", "calm",
  [("provoke", "opposite"), ("segregate", "domain"), ("disperse", "nuance")],
  "To pacify is to quieten anger, which is why a second official was sent; 'disperse' would mean breaking the crowd up rather than settling it.", "medium", 0.94),
 ("parched", "The ground was parched enough that the first rain simply ran off it.", "bone-dry",
  [("saturated", "opposite"), ("cracked", "domain"), ("thirsty", "nuance")],
  "Parched means dried right out, which is why water could not soak in; 'thirsty' properly describes a person rather than the ground itself.", "medium", 0.94),
 ("passive", "He took a passive role in the meeting, letting others put the case.", "inactive",
  [("assertive", "opposite"), ("outvoted", "domain"), ("silent", "nuance")],
  "Passive means not taking initiative, which fits letting others speak; 'silent' would mean he said nothing at all, which is stronger than the sentence claims.", "medium", 0.94),
 ("peculiar", "There was a peculiar smell in the shed that nobody could account for.", "odd",
  [("ordinary", "opposite"), ("pungent", "nuance"), ("chemical", "collocation")],
  "Peculiar means strange in a way that is hard to place, which is why nobody could explain it; 'pungent' describes strength of smell rather than strangeness.", "medium", 0.94),
 ("perceive", "Only the older birds seem to perceive the difference between the two calls.", "detect",
  [("overlook", "opposite"), ("receive", "form"), ("mimic", "domain")],
  "To perceive is to become aware of something, which is what telling two calls apart requires; 'mimic' is what a bird might then do with the call.", "medium", 0.94),
 ("perish", "Seedlings will perish in a single afternoon at that temperature.", "die",
  [("thrive", "opposite"), ("scorch", "domain"), ("wilt", "overreach")],
  "To perish is to die outright, which an afternoon of extreme heat can cause; 'wilt' names a lesser stage the plants would pass through first.", "medium", 0.93),
 ("perpetual", "The perpetual noise from the highway is the one thing tenants complain about.", "constant",
  [("occasional", "opposite"), ("tolerable", "domain"), ("deafening", "nuance")],
  "Perpetual means never stopping, which is why it wears on people; 'deafening' describes volume, and a moderate noise can still be perpetual.", "medium", 0.94),
 ("petty", "The dispute came down to a petty disagreement about parking spaces.", "trivial",
  [("weighty", "opposite"), ("personal", "nuance"), ("bitter", "domain")],
  "Petty means small enough not to be worth the fuss, which is the point being made; 'bitter' describes how the row was conducted rather than how small it was.", "medium", 0.94),
 ("placid", "The bay is placid in the morning and choppy by two.", "still",
  [("turbulent", "opposite"), ("sheltered", "nuance"), ("shallow", "domain")],
  "Placid means calm and undisturbed, which the sentence sets against choppy; 'shallow' concerns depth and has nothing to do with the surface.", "medium", 0.95),
 ("plentiful", "Rain in October made feed plentiful right through the summer.", "abundant",
  [("scarce", "opposite"), ("adequate", "nuance"), ("nutritious", "collocation")],
  "Plentiful means available in large quantity, which good rain produces; 'nutritious' describes the quality of the feed rather than how much there is.", "medium", 0.94),
 ("poised", "She looked poised at the start line even though it was her first final.", "composed",
  [("flustered", "opposite"), ("poisoned", "form"), ("fast", "domain")],
  "Poised means calm and self-possessed, which is notable in a first final; 'fast' concerns her running rather than her bearing.", "medium", 0.94),
 ("portray", "The mural tries to portray the valley as it looked before the dam.", "depict",
  [("distort", "opposite"), ("commission", "collocation"), ("restore", "nuance")],
  "To portray is to represent something in a picture, which is what a mural does; 'restore' would mean bringing the valley itself back.", "medium", 0.94),
 ("precede", "A short warm-up will precede the main race.", "come before",
  [("follow", "opposite"), ("proceed", "form"), ("replace", "nuance")],
  "To precede is to come earlier in sequence, which the warm-up does; 'proceed' is the near-identical word meaning to go forward.", "medium", 0.94),
 ("prevail", "Common sense finally began to prevail after an hour of argument.", "win out",
  [("yield", "opposite"), ("prevent", "form"), ("emerge", "nuance")],
  "To prevail is to come out on top after resistance, which an hour of argument establishes; 'emerge' would mean simply appearing rather than winning.", "medium", 0.93),
 ("profound", "Her answer showed a profound understanding of why the method works.", "deep",
  [("shallow", "opposite"), ("profuse", "form"), ("correct", "nuance")],
  "Profound means going well below the surface, which is more than being right; 'correct' would describe an answer that arrived at the truth without necessarily understanding it.", "medium", 0.94),
 ("prolong", "Watering at night will prolong the life of the lawn through February.", "extend",
  [("curtail", "opposite"), ("propose", "form"), ("improve", "nuance")],
  "To prolong is to make something last longer, which is what night watering achieves; 'improve' would concern quality rather than duration.", "medium", 0.94),
 ("prominent", "The clock tower is the most prominent building on the skyline.", "conspicuous",
  [("hidden", "opposite"), ("permanent", "form"), ("historic", "domain")],
  "Prominent means standing out and easily seen, which is what dominating a skyline means; 'historic' may be true of the tower but concerns its age.", "medium", 0.94),
 ("propel", "A light breeze was enough to propel the dinghy across the flat water.", "drive forward",
  [("anchor", "opposite"), ("repel", "form"), ("steer", "nuance")],
  "To propel is to push something along, which is what wind does to a sail; 'steer' concerns direction rather than the force that moves it.", "medium", 0.94),
 ("provoke", "The decision was always going to provoke a reaction from the members.", "prompt",
  [("soothe", "opposite"), ("revoke", "form"), ("deserve", "nuance")],
  "To provoke a reaction is to bring one about, which the decision was bound to do; 'deserve' would be a judgement about the decision rather than its effect.", "medium", 0.94),
 ("quench", "Nothing seems to quench a thirst like cold water after a long walk.", "satisfy",
  [("worsen", "opposite"), ("quash", "form"), ("dilute", "domain")],
  "To quench a thirst is to end it, which is what the sentence claims water does best; 'dilute' is something you do to a drink, not to thirst.", "medium", 0.94),
 ("radiant", "She came off the court radiant despite having lost in three sets.", "beaming",
  [("downcast", "opposite"), ("reliant", "form"), ("exhausted", "domain")],
  "Radiant here means visibly glowing with pleasure, which is what makes losing surprising; 'exhausted' is likely true after three sets but is a different observation.", "medium", 0.94),
 ("rebuke", "A quiet rebuke from the coach was all it took to end the argument.", "reprimand",
  [("praise", "opposite"), ("rebut", "form"), ("threat", "nuance")],
  "A rebuke is an expression of disapproval, which is what settled the players; 'threat' would promise a consequence rather than express disapproval.", "medium", 0.94),
 ("refrain", "Members are asked to refrain from parking on the verge during matches.", "abstain",
  [("persist", "opposite"), ("refresh", "form"), ("apologise", "domain")],
  "To refrain is to hold back from doing something, which is what the request asks; 'apologise' would come after doing it rather than instead of it.", "medium", 0.94),
 ("reinforce", "Steel bracing was added to reinforce the roof before the second storey went on.", "strengthen",
  [("weaken", "opposite"), ("enforce", "form"), ("replace", "nuance")],
  "To reinforce is to add strength to something already there, which bracing does; 'replace' would mean removing the roof structure entirely.", "medium", 0.95),
 ("relent", "The council refused for two years before it finally began to relent.", "give way",
  [("insist", "opposite"), ("resent", "form"), ("agree", "nuance")],
  "To relent is to soften after holding out, which two years of refusal sets up; 'agree' misses the resistance that came first.", "medium", 0.93),
 ("remedy", "A second coat of sealant should remedy the damp along the south wall.", "fix",
  [("worsen", "opposite"), ("remind", "form"), ("mask", "nuance")],
  "To remedy is to put right the underlying problem, which sealing the wall does; 'mask' would hide the damp while leaving it there.", "medium", 0.94),
 ("replenish", "Rangers replenish the water at the halfway hut once a fortnight.", "restock",
  [("exhaust", "opposite"), ("relinquish", "form"), ("purify", "domain")],
  "To replenish is to fill something back up, which a fortnightly visit does; 'purify' is a different treatment of the same water.", "medium", 0.94),
 ("reside", "Fewer than sixty people reside in the town outside the shearing season.", "live",
  [("depart", "opposite"), ("preside", "form"), ("gather", "nuance")],
  "To reside somewhere is to have your home there, which the seasonal contrast makes clear; 'gather' would describe people coming together temporarily.", "medium", 0.94),
 ("restrain", "It took two of them to restrain the gate in the wind.", "hold back",
  [("release", "opposite"), ("retrain", "form"), ("repair", "domain")],
  "To restrain is to hold something in check against a force, which a gate in wind requires; 'repair' is what you might do to it afterwards.", "medium", 0.94),
 ("retain", "The club will retain both coaches for another season.", "keep",
  [("dismiss", "opposite"), ("obtain", "form"), ("promote", "nuance")],
  "To retain is to hold on to what you already have, which reappointing coaches is; 'obtain' would mean acquiring somebody new.", "medium", 0.95),
 ("revive", "A hot drink and ten minutes out of the wind revived the whole party.", "restore",
  [("exhaust", "opposite"), ("relive", "form"), ("warm", "nuance")],
  "To revive is to bring back strength or spirits, which a break and a hot drink do; 'warm' is the mechanism rather than the effect on the group.", "medium", 0.94),
 ("rigid", "The rules on entry times are rigid and no exceptions are made.", "inflexible",
  [("lenient", "opposite"), ("ridged", "form"), ("detailed", "nuance")],
  "Rigid means not bending in any circumstance, which 'no exceptions' spells out; 'detailed' would say the rules were long rather than unyielding.", "medium", 0.94),
 ("robust", "The frame is robust enough to take a full load on rough tracks.", "sturdy",
  [("flimsy", "opposite"), ("rustic", "form"), ("heavy", "nuance")],
  "Robust means strongly built and able to take punishment, which rough tracks demand; 'heavy' describes weight, and a heavy frame can still be weak.", "medium", 0.95),
 ("rugged", "The rugged coastline south of the cape has almost no safe landing.", "rough",
  [("gentle", "opposite"), ("ragged", "form"), ("remote", "domain")],
  "Rugged means rocky and broken, which is why landing is unsafe; 'remote' concerns distance from anywhere rather than the shape of the shore.", "medium", 0.94),
 ("sanction", "The league refused to sanction a replay after the scoring error.", "authorise",
  [("forbid", "opposite"), ("sanctity", "form"), ("schedule", "domain")],
  "To sanction here means to give official approval, which the league withheld; 'schedule' would be arranging the replay once it had been approved.", "hard", 0.91),
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
