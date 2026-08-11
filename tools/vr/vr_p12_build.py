#!/usr/bin/env python3
"""Builds vr_vic_acer_p12.json — 30 vocabulary-in-context questions (TASK §3.1).

Third batch of the ~341-item top-up in vic_content_taxonomy_TASK.md §5.3. The mix is
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
NN = 12
BOOK = "vr_vic_acer"
CATEGORY = "vocabulary_synonym"
LABEL = "Vocabulary in context / synonyms"
NOW = datetime.datetime(2026, 8, 11, 10, 0, 0, tzinfo=datetime.timezone.utc) \
    .isoformat().replace("+00:00", "Z")

# (target, stem, key, [(distractor, relation) x3], explanation, difficulty, confidence)
ITEMS = [
 ("dominate", "One tall gum came to dominate the corner of the yard, shading everything under it.", "overshadow",
  [("recede", "opposite"), ("donate", "form"), ("flourish", "nuance")],
  "To dominate a space is to be the controlling presence in it, which a tree shading everything does; 'flourish' would mean growing well without saying anything about the effect on the rest.", "medium", 0.94),
 ("drastic", "Losing the main sponsor called for drastic cuts rather than the usual trimming.", "severe",
  [("mild", "opposite"), ("costly", "domain"), ("permanent", "nuance")],
  "Drastic means extreme and far-reaching, which is what 'rather than the usual trimming' sets it against; 'permanent' says how long the cuts last, not how deep they go.", "medium", 0.94),
 ("dread", "She began to dread the Thursday practice weeks before the season even started.", "fear",
  [("relish", "opposite"), ("thread", "form"), ("attend", "collocation")],
  "To dread something is to feel fear about it in advance, which is why the feeling came weeks early; 'attend' is what she does at practice, not how she feels about it.", "medium", 0.94),
 ("dreary", "Three weeks of dreary weather kept the courts empty for most of the holidays.", "gloomy",
  [("cheerful", "opposite"), ("windy", "nuance"), ("freezing", "domain")],
  "Dreary means dull and spirit-lowering, which explains empty courts; 'freezing' names a temperature and would be a different complaint about the weather.", "medium", 0.94),
 ("durable", "The bench is made of a durable hardwood that will outlast anything else in the park.", "long-lasting",
  [("flimsy", "opposite"), ("imported", "collocation"), ("polished", "domain")],
  "Durable means able to withstand wear over time, which is what outlasting everything else shows; 'polished' describes the finish rather than the strength.", "medium", 0.95),
 ("eccentric", "Her eccentric habit of gardening at midnight became something the street looked forward to.", "unconventional",
  [("ordinary", "opposite"), ("electric", "form"), ("secretive", "nuance")],
  "Eccentric means charmingly out of the ordinary, which is why neighbours enjoyed it; 'secretive' would mean she hid it, and the street plainly knew.", "medium", 0.94),
 ("efficient", "The new roster is far more efficient, covering the same shifts with two fewer staff.", "economical",
  [("wasteful", "opposite"), ("cheaper", "domain"), ("popular", "nuance")],
  "Efficient means achieving the same result with less input, which is exactly what two fewer staff means; 'popular' says how people feel about the roster, not how it performs.", "medium", 0.94),
 ("eligible", "Only students who have played four games are eligible for the end-of-season award.", "qualified",
  [("barred", "opposite"), ("keen", "domain"), ("nominated", "nuance")],
  "Eligible means meeting the conditions to be considered, which four games establishes; 'nominated' would mean somebody had already put them forward.", "medium", 0.94),
 ("embark", "The pair will embark on the coastal walk as soon as the track reopens.", "begin",
  [("conclude", "opposite"), ("embargo", "form"), ("survey", "domain")],
  "To embark on something is to set out on it, which is what waiting for the track to reopen implies; 'survey' is an activity on a track but not a way of starting one.", "medium", 0.94),
 ("eminent", "An eminent marine biologist was flown in to give the opening address.", "distinguished",
  [("obscure", "opposite"), ("retired", "domain"), ("elderly", "nuance")],
  "Eminent means well known and highly regarded in a field, which is why she was flown in; 'imminent' sounds nearly identical but means about to happen.", "medium", 0.94),
 ("endure", "The old shearing shed has endured a century of weather with almost no repair.", "withstand",
  [("collapse", "opposite"), ("ensure", "form"), ("shelter", "collocation")],
  "To endure something is to come through it still standing, which a century with no repair describes; 'shelter' is what a shed does for others, not what it does to weather.", "medium", 0.94),
 ("enhance", "A second coat of oil will enhance the grain without changing the colour.", "improve",
  [("spoil", "opposite"), ("darken", "domain"), ("conceal", "nuance")],
  "To enhance is to make an existing quality better, which fits bringing out grain that is already there; 'conceal' would mean hiding the grain instead.", "medium", 0.95),
 ("entice", "A free first lesson was offered to entice new members through the door.", "tempt",
  [("repel", "opposite"), ("entire", "form"), ("register", "collocation")],
  "To entice is to draw somebody in with something attractive, which a free lesson does; 'register' is what a new member then does, not the drawing in.", "medium", 0.94),
 ("erode", "Winter swells continue to erode the dune in front of the surf club.", "wear away",
  [("rebuild", "opposite"), ("secure", "domain"), ("flood", "nuance")],
  "To erode is to remove material gradually, which repeated swells do to a dune; 'flood' would be a single covering with water rather than a slow loss of sand.", "medium", 0.94),
 ("escalate", "What began as a disagreement over parking began to escalate through the whole street.", "intensify",
  [("subside", "opposite"), ("escape", "form"), ("spread", "nuance")],
  "To escalate is to grow more serious, which is what a parking row becoming a street matter means; 'spread' captures the reach but not the increase in heat.", "medium", 0.93),
 ("exceed", "Entries this year exceed the number the club can actually accommodate.", "surpass",
  [("trail", "opposite"), ("excel", "form"), ("match", "nuance")],
  "To exceed is to go beyond a limit, which is why the club cannot fit everyone; 'match' would mean the entries exactly filled the places available.", "medium", 0.94),
 ("exclude", "The revised rule would exclude anybody who had not trained before September.", "bar",
  [("admit", "opposite"), ("exclaim", "form"), ("penalise", "nuance")],
  "To exclude somebody is to keep them out altogether, which the rule does; 'penalise' would mean they could still take part but under some disadvantage.", "medium", 0.94),
 ("exert", "It takes very little force to open, so do not exert yourself on the handle.", "apply",
  [("conserve", "opposite"), ("exalt", "form"), ("repair", "domain")],
  "To exert force is to put it forth, which is what the warning tells you not to do; 'repair' is something else you might do to a handle entirely.", "medium", 0.93),
 ("exotic", "The nursery stocks a few exotic species that will not survive a Ballarat winter.", "foreign",
  [("native", "opposite"), ("delicate", "domain"), ("expensive", "nuance")],
  "Exotic means introduced from elsewhere, which is why the local winter is a problem; 'expensive' may be true of rare plants but is not what the word means.", "medium", 0.94),
 ("expel", "The committee has the power to expel a member who breaches the code twice.", "eject",
  [("enrol", "opposite"), ("expend", "form"), ("suspend", "nuance")],
  "To expel is to remove somebody permanently, which is the strongest sanction available; 'suspend' would put the membership on hold rather than end it.", "medium", 0.94),
 ("exploit", "Small operators cannot exploit the same discounts the big chains negotiate.", "make use of",
  [("waste", "opposite"), ("explode", "form"), ("obtain", "nuance")],
  "To exploit an advantage is to turn it to your benefit, which small operators cannot do here; 'obtain' would mean getting the discount rather than using it well.", "medium", 0.93),
 ("fabricate", "There was no need to fabricate an excuse; the delay was on the noticeboard.", "invent",
  [("verify", "opposite"), ("fabric", "form"), ("rehearse", "nuance")],
  "To fabricate is to make something up that is not true, which the noticeboard made unnecessary; 'rehearse' would mean practising a real excuse rather than inventing one.", "medium", 0.94),
 ("fatigue", "By the fourth day the fatigue in the group was showing in every decision.", "exhaustion",
  [("vigour", "opposite"), ("impatience", "nuance"), ("hunger", "domain")],
  "Fatigue is deep tiredness built up over time, which four days would produce; 'hunger' is another hardship of a long walk but a different one.", "medium", 0.94),
 ("ferocious", "A ferocious southerly came through about four and took the marquee with it.", "violent",
  [("gentle", "opposite"), ("precious", "form"), ("sudden", "nuance")],
  "Ferocious describes great destructive force, which taking a marquee demonstrates; 'sudden' would describe how quickly it arrived rather than how strong it was.", "medium", 0.94),
 ("fertile", "The river flats are fertile enough to crop twice in a good year.", "productive",
  [("barren", "opposite"), ("futile", "form"), ("flooded", "domain")],
  "Fertile land is land that grows things well, which cropping twice shows; 'flooded' is something that happens to river flats but not what makes them productive.", "medium", 0.95),
 ("flaw", "One flaw in the design meant the gate would not close on a hot day.", "defect",
  [("merit", "opposite"), ("flow", "form"), ("failure", "overreach")],
  "A flaw is a single fault in something otherwise sound, which one stuck gate is; 'failure' overstates it, since the design worked in every other respect.", "medium", 0.94),
 ("flee", "Wallabies flee into the scrub at the first sound of a vehicle on the track.", "escape",
  [("approach", "opposite"), ("flea", "form"), ("hide", "nuance")],
  "To flee is to run away from danger, which is what moving into the scrub is; 'hide' would mean staying put out of sight rather than running.", "medium", 0.94),
 ("forge", "The two clubs began to forge an arrangement that suited both grounds.", "build",
  [("dissolve", "opposite"), ("forget", "form"), ("sign", "collocation")],
  "To forge an arrangement is to work it into existence with effort, which negotiation is; 'sign' is what happens once the arrangement already exists.", "medium", 0.93),
 ("foster", "The program is designed to foster confidence rather than to find talent.", "encourage",
  [("stifle", "opposite"), ("fluster", "form"), ("test", "nuance")],
  "To foster something is to help it grow, which is set here against merely finding what is already there; 'test' is closer to the finding the program avoids.", "medium", 0.94),
 ("frugal", "A frugal household, they had never once replaced a thing that could be mended.", "thrifty",
  [("extravagant", "opposite"), ("fragile", "form"), ("poor", "nuance")],
  "Frugal describes a deliberate care with money, which mending rather than replacing shows; 'poor' would mean they could not afford to replace things, which the sentence does not say.", "medium", 0.94),
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
