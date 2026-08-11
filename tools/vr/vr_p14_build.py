#!/usr/bin/env python3
"""Builds vr_vic_acer_p14.json — 30 vocabulary-in-context questions (TASK §3.1).

Fifth batch of the ~341-item top-up in vic_content_taxonomy_TASK.md §5.3. The mix is
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
NN = 14
BOOK = "vr_vic_acer"
CATEGORY = "vocabulary_synonym"
LABEL = "Vocabulary in context / synonyms"
NOW = datetime.datetime(2026, 8, 11, 10, 0, 0, tzinfo=datetime.timezone.utc) \
    .isoformat().replace("+00:00", "Z")

# (target, stem, key, [(distractor, relation) x3], explanation, difficulty, confidence)
ITEMS = [
 ("legible", "His writing was barely legible after the third hour of the exam.", "readable",
  [("illegible", "opposite"), ("smudged", "domain"), ("hurried", "nuance")],
  "Legible means able to be read, which is what three hours of writing eroded; 'hurried' explains why the writing suffered rather than what the word means.", "medium", 0.94),
 ("liable", "Anyone leaving gear on the court is liable for any damage to it.", "responsible",
  [("exempt", "opposite"), ("insured", "domain"), ("charged", "nuance")],
  "To be liable is to bear the responsibility if something goes wrong; 'charged' would mean a fee had already been imposed rather than that responsibility rests with you.", "medium", 0.94),
 ("liberate", "The floodwater finally began to liberate the boat from the sandbar.", "free",
  [("trap", "opposite"), ("salvage", "domain"), ("float", "nuance")],
  "To liberate is to release something that was held fast, which is what rising water does to a stuck boat; 'float' is the result rather than the freeing itself.", "medium", 0.94),
 ("listless", "The heat left the whole class listless by the last period.", "lethargic",
  [("energetic", "opposite"), ("drowsy", "domain"), ("restless", "nuance")],
  "Listless means drained of energy and interest, which is what afternoon heat produces; 'restless' means the opposite kind of unease, fidgety rather than flat.", "medium", 0.93),
 ("loiter", "Signs ask people not to loiter near the loading bay after closing.", "linger",
  [("hurry", "opposite"), ("trespass", "domain"), ("gather", "nuance")],
  "To loiter is to hang about a place with no purpose, which is what the sign discourages; 'gather' would describe a group forming rather than aimless waiting.", "medium", 0.94),
 ("lucid", "For a few minutes after waking he was perfectly lucid, then drifted again.", "clear-headed",
  [("confused", "opposite"), ("upright", "nuance"), ("talkative", "domain")],
  "Lucid means thinking clearly, which is what the sentence sets against drifting; 'talkative' says how much he spoke rather than how clearly he thought.", "medium", 0.94),
 ("magnify", "The screen will magnify the sample forty times without losing detail.", "enlarge",
  [("shrink", "opposite"), ("focus", "domain"), ("clarify", "nuance")],
  "To magnify is to make something appear bigger, which is what a forty-times figure describes; 'clarify' concerns sharpness rather than size.", "medium", 0.95),
 ("malice", "There was no malice in the tackle, but the umpire paid the free anyway.", "ill will",
  [("kindness", "opposite"), ("regret", "domain"), ("carelessness", "nuance")],
  "Malice is a deliberate wish to do harm, which is what the sentence says was absent; 'carelessness' is a different fault, and one the tackle may well have involved.", "medium", 0.94),
 ("mandate", "The new rules mandate a second official at every finals match.", "require",
  [("forbid", "opposite"), ("fund", "domain"), ("recommend", "nuance")],
  "To mandate is to make something compulsory, which a rule does; 'recommend' would leave clubs free to run finals with one official.", "medium", 0.94),
 ("marvel", "Visitors still marvel at how the dome was built without steel.", "wonder",
  [("scoff", "opposite"), ("restore", "nuance"), ("inspect", "domain")],
  "To marvel is to be filled with admiring astonishment, which is what the dome provokes; 'inspect' is a careful looking that carries no wonder at all.", "medium", 0.94),
 ("mediate", "A former player was asked to mediate between the two clubs.", "arbitrate",
  [("inflame", "opposite"), ("meditate", "form"), ("decide", "nuance")],
  "To mediate is to help two sides reach agreement, which is why a neutral figure was chosen; 'decide' would mean imposing an outcome rather than helping them find one.", "medium", 0.94),
 ("menace", "A cracked branch over the footpath was judged a menace and taken down.", "hazard",
  [("safeguard", "opposite"), ("obstacle", "domain"), ("nuisance", "nuance")],
  "A menace is something posing real danger, which justified removing the branch; 'nuisance' would be merely annoying and would not warrant the work.", "medium", 0.93),
 ("merge", "The two smaller clubs will merge before the start of next season.", "combine",
  [("split", "opposite"), ("emerge", "form"), ("relocate", "domain")],
  "To merge is for two things to become one, which is what the clubs will do; 'relocate' would mean moving grounds while staying separate.", "medium", 0.95),
 ("methodical", "His methodical approach to the repair meant nothing had to be done twice.", "systematic",
  [("haphazard", "opposite"), ("medical", "form"), ("slow", "nuance")],
  "Methodical means working in an ordered, step-by-step way, which is why nothing was repeated; 'slow' describes pace and a methodical worker need not be slow.", "medium", 0.94),
 ("migrate", "Short-tailed shearwaters migrate to the Bering Sea and back each year.", "travel seasonally",
  [("settle", "opposite"), ("mitigate", "form"), ("navigate", "domain")],
  "To migrate is to move between regions with the seasons, which the annual round describes; 'navigate' is how they find the way rather than the movement itself.", "medium", 0.94),
 ("minimal", "The damage after the storm was minimal, mostly a few tiles.", "slight",
  [("extensive", "opposite"), ("minimum", "form"), ("costly", "nuance")],
  "Minimal means as small as it could reasonably be, which a few tiles is; 'costly' would say something about price, and the sentence suggests the opposite.", "medium", 0.94),
 ("mock", "It is easy to mock the old scoreboard until you try to read the new one.", "ridicule",
  [("admire", "opposite"), ("mark", "form"), ("replace", "domain")],
  "To mock is to make fun of something, which the sentence says is easy to do; 'replace' is what happened to the scoreboard rather than an attitude to it.", "medium", 0.94),
 ("momentous", "The vote that evening turned out to be a momentous one for the whole district.", "significant",
  [("trivial", "opposite"), ("momentary", "form"), ("lengthy", "nuance")],
  "Momentous means of great and lasting importance, which is why it mattered district-wide; 'momentary' sounds close but means the opposite, lasting only an instant.", "medium", 0.94),
 ("monotonous", "The monotonous hum of the pump made it hard to concentrate.", "unvarying",
  [("varied", "opposite"), ("monotone", "form"), ("loud", "nuance")],
  "Monotonous means tediously unchanging, which is what makes a hum wearing; 'loud' describes volume, and a quiet hum can be just as monotonous.", "medium", 0.94),
 ("morose", "He had been morose all week and nobody could get much out of him.", "sullen",
  [("cheerful", "opposite"), ("verbose", "form"), ("unwell", "nuance")],
  "Morose means gloomy and withdrawn, which fits somebody hard to draw out; 'unwell' offers a cause the sentence never gives.", "medium", 0.93),
 ("murky", "The water below the weir was too murky to see the bottom.", "cloudy",
  [("clear", "opposite"), ("musty", "form"), ("shallow", "domain")],
  "Murky means dark and clouded, which is why the bottom was hidden; 'shallow' concerns depth and would make the bottom easier to see, not harder.", "medium", 0.95),
 ("negligible", "The difference between the two brands turned out to be negligible.", "insignificant",
  [("substantial", "opposite"), ("negligent", "form"), ("measurable", "nuance")],
  "Negligible means so small it can be ignored, which is why the choice did not matter; 'measurable' would mean the difference could be detected and counted.", "medium", 0.94),
 ("notable", "The most notable change was the removal of the fence along the boundary.", "striking",
  [("unremarkable", "opposite"), ("notify", "form"), ("recent", "nuance")],
  "Notable means worth remarking on, which is why it heads the list; 'recent' places the change in time rather than saying it stood out.", "medium", 0.94),
 ("notorious", "That corner is notorious for flooding after even moderate rain.", "infamous",
  [("obscure", "opposite"), ("notable", "form"), ("dangerous", "nuance")],
  "Notorious means widely known for something bad, which fits a corner everyone knows floods; 'dangerous' may be true but says nothing about being well known.", "medium", 0.94),
 ("nourish", "Mulch will nourish the beds through the worst of the summer.", "sustain",
  [("starve", "opposite"), ("flourish", "form"), ("shade", "nuance")],
  "To nourish is to supply what something needs to keep growing, which is what mulch does; 'shade' is another benefit of mulch but concerns light, not feeding.", "medium", 0.94),
 ("obsolete", "The old ticket machines were obsolete years before they were finally removed.", "outdated",
  [("current", "opposite"), ("absolute", "form"), ("broken", "nuance")],
  "Obsolete means superseded and no longer in proper use, which can be true of a machine that still works; 'broken' would be a fault rather than being out of date.", "medium", 0.94),
 ("obstruct", "A parked trailer had begun to obstruct the view from the crossing.", "block",
  [("clear", "opposite"), ("instruct", "form"), ("narrow", "nuance")],
  "To obstruct is to get in the way of something, which the trailer does to sightlines; 'narrow' would reduce the view without cutting it off.", "medium", 0.94),
 ("ominous", "An ominous line of cloud built up over the range through the afternoon.", "threatening",
  [("reassuring", "opposite"), ("obvious", "form"), ("distant", "domain")],
  "Ominous means giving the impression that something bad is coming, which is how a building storm reads; 'distant' places the cloud in space rather than describing its menace.", "medium", 0.95),
 ("opaque", "The glass had gone opaque with years of salt spray.", "not see-through",
  [("transparent", "opposite"), ("opulent", "form"), ("cracked", "nuance")],
  "Opaque means light will not pass through, which is what a salt-etched pane becomes; 'cracked' is different damage and would still let light through.", "medium", 0.94),
 ("outweigh", "For most families the savings outweigh the inconvenience of the earlier start.", "exceed",
  [("undercut", "opposite"), ("outreach", "form"), ("justify", "nuance")],
  "To outweigh is to be greater in importance when the two are set against each other; 'justify' is the conclusion families draw rather than the comparison itself.", "medium", 0.93),
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
