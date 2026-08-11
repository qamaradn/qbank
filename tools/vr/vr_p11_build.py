#!/usr/bin/env python3
"""Builds vr_vic_acer_p11.json — 30 vocabulary-in-context questions (TASK §3.1).

Second batch of the ~341-item top-up in vic_content_taxonomy_TASK.md §5.3. The mix is
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
NN = 11
BOOK = "vr_vic_acer"
CATEGORY = "vocabulary_synonym"
LABEL = "Vocabulary in context / synonyms"
NOW = datetime.datetime(2026, 8, 11, 10, 0, 0, tzinfo=datetime.timezone.utc) \
    .isoformat().replace("+00:00", "Z")

# (target, stem, key, [(distractor, relation) x3], explanation, difficulty, confidence)
ITEMS = [
 ("adamant",
  "She was adamant that the meeting had been moved, even after three people told her otherwise.",
  "insistent",
  [("unsure", "opposite"), ("outspoken", "domain"), ("mistaken", "nuance")],
  "Adamant means refusing to be shifted from a position, which is why the corrections made no difference; 'mistaken' may well be true of her but describes being wrong, not being immovable.",
  "medium", 0.94),

 ("alleviate",
  "A second doctor was flown in to alleviate the pressure on the clinic during the outbreak.",
  "ease",
  [("worsen", "opposite"), ("prescribe", "collocation"), ("diagnose", "domain")],
  "To alleviate is to make something less severe without removing it, which is what an extra doctor does to pressure; 'elevate' sounds close but means to lift or raise.",
  "medium", 0.94),

 ("ambiguous",
  "The sign was so ambiguous that half the drivers turned left and half turned right.",
  "unclear",
  [("obvious", "opposite"), ("misprinted", "domain"), ("faded", "nuance")],
  "Ambiguous means open to more than one reading, which is exactly why drivers split two ways; 'faded' would explain a sign being hard to see rather than hard to interpret.",
  "medium", 0.95),

 ("apprehensive",
  "He was apprehensive about the swim leg, having never raced in open water before.",
  "uneasy",
  [("confident", "opposite"), ("apprehend", "form"), ("unfit", "nuance")],
  "Apprehensive means worried about something ahead, which fits a first open-water race; 'unfit' would be about his condition rather than his state of mind.",
  "medium", 0.94),

 ("arduous",
  "The last stage was an arduous climb over loose rock in full sun.",
  "gruelling",
  [("effortless", "opposite"), ("steep", "nuance"), ("scenic", "domain")],
  "Arduous means demanding sustained hard effort, which loose rock in full sun requires; 'scenic' may be true of the climb but describes the view, not the difficulty.",
  "medium", 0.94),

 ("assert",
  "The younger councillor began to assert her view more firmly as the debate went on.",
  "state",
  [("withhold", "opposite"), ("assess", "form"), ("shout", "overreach")],
  "To assert is to put a view forward confidently, which is what growing firmness looks like; 'shout' pushes the same direction far past what the sentence supports.",
  "medium", 0.93),

 ("astute",
  "It was an astute decision to book the courts before the school holidays began.",
  "shrewd",
  [("foolish", "opposite"), ("acute", "form"), ("expensive", "domain")],
  "Astute describes a decision showing sharp practical judgement, which early booking is; 'acute' sounds nearly the same but means sharp in the sense of severe or intense.",
  "medium", 0.94),

 ("avert",
  "Quick work by the volunteers helped avert a much larger fire in the scrub behind the oval.",
  "prevent",
  [("cause", "opposite"), ("extinguish", "domain"), ("contain", "nuance")],
  "To avert something is to stop it happening at all, which is what the volunteers achieved; 'contain' would mean the larger fire started and was then held in check.",
  "medium", 0.94),

 ("baffle",
  "The last question on the paper baffled almost everyone, including two of the teachers.",
  "puzzle",
  [("clarify", "opposite"), ("mislead", "domain"), ("annoy", "nuance")],
  "To baffle is to leave somebody completely unable to work something out, which fits teachers being caught too; 'annoy' describes irritation rather than confusion.",
  "medium", 0.94),

 ("blatant",
  "It was a blatant push in the back and the umpire paid the free kick immediately.",
  "obvious",
  [("subtle", "opposite"), ("blatantly", "form"), ("illegal", "nuance")],
  "Blatant means done openly and without any attempt to hide it, which is why the umpire saw it at once; 'illegal' is true of the push but not what the word describes.",
  "medium", 0.94),

 ("brittle",
  "Left in the sun for two summers, the hose had gone brittle and split at the first bend.",
  "fragile",
  [("supple", "opposite"), ("kinked", "domain"), ("perished", "nuance")],
  "Brittle means hard but easily snapped, which is why the hose split rather than bent; 'perished' describes rubber decaying generally and is a cause rather than the quality.",
  "medium", 0.93),

 ("coarse",
  "The coarse sand at that end of the beach is hard to walk on in bare feet.",
  "rough",
  [("smooth", "opposite"), ("course", "form"), ("damp", "domain")],
  "Coarse means made of large, rough particles, which is what makes walking uncomfortable; 'course' is the identical-sounding word for a route or a class.",
  "medium", 0.94),

 ("coherent",
  "After a night with no sleep her answer was barely coherent, though every fact in it was right.",
  "logical",
  [("rambling", "opposite"), ("exhausted", "domain"), ("audible", "nuance")],
  "Coherent means holding together so it can be followed, which is separate from being correct; 'audible' would mean her answer could not be heard rather than not be followed.",
  "hard", 0.92),

 ("oblige",
  "Nothing in the rules can oblige a club to release a player mid-season.",
  "require",
  [("permit", "opposite"), ("obliterate", "form"), ("encourage", "nuance")],
  "To oblige somebody is to leave them no choice, which is what the rules cannot do here; 'encourage' would mean the rules push in that direction without requiring it.",
  "medium", 0.94),

 ("comply",
  "Two of the stalls refused to comply with the new packaging rules and were asked to leave.",
  "obey",
  [("defy", "opposite"), ("compile", "form"), ("understand", "nuance")],
  "To comply is to act in line with a rule, which is what the stalls would not do; 'understand' would mean they failed to grasp the rules rather than refused them.",
  "medium", 0.94),

 ("condense",
  "The editor asked him to condense the report to a single page without losing the findings.",
  "shorten",
  [("expand", "opposite"), ("proofread", "domain"), ("rewrite", "nuance")],
  "To condense is to compress something into less space while keeping its substance, which is exactly the brief; 'rewrite' says nothing about the length changing.",
  "medium", 0.94),

 ("conserve",
  "Households were asked to conserve water until the reservoir came back above forty per cent.",
  "save",
  [("squander", "opposite"), ("recycle", "nuance"), ("filter", "domain")],
  "To conserve is to use carefully so that a supply lasts, which is what a low reservoir demands; 'filter' is something done to water but is not about using less.",
  "medium", 0.95),

 ("contend",
  "Growers in the region must contend with both frost in spring and hail in summer.",
  "cope",
  [("avoid", "opposite"), ("contain", "form"), ("complain", "nuance")],
  "To contend with something is to have to deal with it, which is what an unavoidable climate forces; 'avoid' is precisely what the growers cannot do.",
  "medium", 0.93),

 ("credible",
  "Her account was the only credible explanation anybody had offered by the end of the week.",
  "believable",
  [("far-fetched", "opposite"), ("creditable", "form"), ("lengthy", "domain")],
  "Credible means deserving to be believed, which is why the other explanations were set aside; 'creditable' is a different word meaning deserving of praise.",
  "medium", 0.94),

 ("abridge",
  "Rain forced the organisers to abridge the parade after only three floats.",
  "cut short",
  [("extend", "opposite"), ("bridge", "form"), ("cancel", "nuance")],
  "To abridge something is to shorten it, which is why three floats still went through; 'cancel' would mean the parade never started at all.",
  "medium", 0.93),

 ("decipher",
  "It took two of us to decipher the handwriting on the back of the photograph.",
  "interpret",
  [("scribble", "opposite"), ("decimal", "form"), ("photograph", "collocation")],
  "To decipher is to work out something hard to read, which is what bad handwriting requires; 'photograph' appears in the sentence but is the object, not the action.",
  "medium", 0.94),

 ("deflect",
  "He tried to deflect the question by asking one of his own.",
  "turn aside",
  [("invite", "opposite"), ("reflect", "form"), ("answer", "nuance")],
  "To deflect is to send something off course rather than meet it, which a counter-question does; 'answer' is exactly what he avoided doing.",
  "medium", 0.94),

 ("dense",
  "The scrub grew so dense past the creek that the track disappeared altogether.",
  "thick",
  [("sparse", "opposite"), ("tense", "form"), ("prickly", "domain")],
  "Dense means packed closely together, which is why the track vanished; 'prickly' may be true of scrub but describes what it feels like, not how much of it there is.",
  "medium", 0.95),

 ("deprive",
  "The new fence would deprive the neighbours of their afternoon light.",
  "rob",
  [("supply", "opposite"), ("deprave", "form"), ("shade", "collocation")],
  "To deprive somebody of something is to take away what they had, which a tall fence does to light; 'shade' is the result rather than the action.",
  "medium", 0.93),

 ("dire",
  "The situation on the third day was dire enough for the crew to call for help.",
  "desperate",
  [("promising", "opposite"), ("direct", "form"), ("unpleasant", "nuance")],
  "Dire means extremely serious, which is what justifies a distress call; 'unpleasant' is far too mild for a situation of that gravity.",
  "medium", 0.94),

 ("disclose",
  "The company refused to disclose how much of the site had already been cleared.",
  "reveal",
  [("conceal", "opposite"), ("enclose", "form"), ("measure", "domain")],
  "To disclose is to make known something previously kept back, which the company would not do; 'measure' is an activity on a site rather than a way of telling anyone.",
  "medium", 0.94),

 ("discreet",
  "A discreet word to the coach afterwards was better than raising it in front of the team.",
  "tactful",
  [("indiscreet", "opposite"), ("discrete", "form"), ("brief", "nuance")],
  "Discreet means careful not to cause embarrassment, which is why the private word was better; 'discrete' is the identical-sounding word meaning separate.",
  "medium", 0.94),

 ("disperse",
  "The crowd began to disperse as soon as the last band left the stage.",
  "scatter",
  [("gather", "opposite"), ("disburse", "form"), ("applaud", "collocation")],
  "To disperse is to move apart in all directions, which is what a crowd does at the end; 'applaud' is something the crowd also does but not what the word means.",
  "medium", 0.94),

 ("distort",
  "Cheap speakers distort the low notes until the bass line is unrecognisable.",
  "warp",
  [("clarify", "opposite"), ("distraught", "form"), ("amplify", "nuance")],
  "To distort is to warp something out of its proper shape, which is why the bass becomes unrecognisable; 'amplify' would mean making it louder without changing it.",
  "medium", 0.93),

 ("diverse",
  "The market draws a diverse crowd from every suburb along the line.",
  "varied",
  [("uniform", "opposite"), ("divert", "form"), ("enormous", "nuance")],
  "Diverse means made up of many different kinds, which fits people coming from everywhere; 'enormous' would describe the size of the crowd rather than its variety.",
  "medium", 0.95),
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
