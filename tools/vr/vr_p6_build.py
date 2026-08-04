#!/usr/bin/env python3
"""Builds vr_vic_acer_p6.json — 21 vocabulary-in-context questions, completing §3.1 (126).

Relation sets are spread deliberately from the start; p5's first build was rejected for
running one template across 11 of 21 questions.
"""
import datetime
import json
import pathlib
import sys
import uuid

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/verbal_reasoning/generated"
NN = 6
BOOK = "vr_vic_acer"
CATEGORY = "vocabulary_synonym"
LABEL = "Vocabulary in context / synonyms"
NOW = datetime.datetime(2026, 8, 4, 15, 0, 0, tzinfo=datetime.timezone.utc) \
    .isoformat().replace("+00:00", "Z")

ITEMS = [
 ("inflate",
  "Reports of the crowd size were inflated, as anyone who saw the empty bays could tell.",
  "exaggerate",
  [("play down", "opposite"), ("count up", "domain"), ("correct", "nuance")],
  "To inflate a figure is to make it seem larger than it is, which the empty seats "
  "contradict; 'count up' describes tallying the crowd rather than overstating it.",
  "medium", 0.93),

 ("innate",
  "A dingo's wariness of people appears to be innate rather than something it learns from "
  "the pack.",
  "inborn",
  [("learned", "opposite"), ("innocent", "form"), ("unusual", "domain")],
  "Innate means present from birth, which the contrast with learning makes explicit; "
  "'unusual' says how common the trait is, not where it came from.",
  "medium", 0.94),

 ("intent",
  "She was so intent on the fishing line that she did not hear the boat come alongside.",
  "concentrating hard",
  [("barely interested", "opposite"), ("clearly intended", "form"), ("quietly waiting", "nuance")],
  "Intent here means fixed in attention on something, which explains not hearing the boat; "
  "'quietly waiting' describes what she was doing but not the intensity of her focus.",
  "hard", 0.91),

 ("jeopardy",
  "The whole expedition was in jeopardy once the second radio failed on the plateau.",
  "serious risk",
  [("total safety", "opposite"), ("legal custody", "form"), ("open dispute", "domain")],
  "Jeopardy means danger of loss or failure, which losing the last radio creates; 'legal "
  "custody' belongs to the courtroom sense of the word and does not fit an expedition.",
  "medium", 0.93),

 ("jumble",
  "The bottom of the pack was a jumble of wet socks, tent pegs and half a map.",
  "untidy mixture",
  [("neat arrangement", "opposite"), ("humble beginning", "form"), ("useless collection", "nuance")],
  "A jumble is things mixed together without order, which the contents describe; 'useless "
  "collection' judges their worth, and tent pegs and a map are plainly useful.",
  "medium", 0.94),

 ("languid",
  "The heat made everyone languid, and even the dogs gave up on the ball by mid-afternoon.",
  "slow and listless",
  [("brisk and eager", "opposite"), ("liquid and runny", "form"), ("calm and peaceful", "nuance")],
  "Languid means lacking energy or spirit, which heat produces; 'calm and peaceful' sounds "
  "similar in tone but describes contentment rather than the droop of exhaustion.",
  "medium", 0.93),

 ("loathe",
  "He came to loathe the drive after doing it twice a day for eleven years.",
  "hate",
  [("adore", "opposite"), ("loaf", "form"), ("dread", "nuance")],
  "To loathe is to feel intense dislike, which eleven years of the same drive could "
  "produce; 'dread' is fear of what is coming rather than hatred of the thing itself.",
  "medium", 0.94),

 ("lofty",
  "The hall has a lofty ceiling that swallows every announcement made without a "
  "microphone.",
  "very high",
  [("very low", "opposite"), ("very old", "domain"), ("rather grand", "nuance")],
  "Lofty means towering in height, which is why sound is lost up there; 'rather grand' "
  "describes how impressive the hall looks, not the distance to its ceiling.",
  "medium", 0.94),

 ("lure",
  "Cheap fares were used to lure travellers onto the new route through Mildura.",
  "tempt",
  [("repel", "opposite"), ("lurk", "form"), ("carry", "domain")],
  "To lure is to attract by offering something appealing, which cheap fares do; 'carry' "
  "describes transporting the travellers once they have already been persuaded.",
  "medium", 0.94),

 ("opt",
  "Most families opt for the earlier session, which leaves the late one half empty.",
  "choose",
  [("refuse", "opposite"), ("adopt", "form"), ("arrive", "domain")],
  "To opt for something is to select it from the alternatives, which the fuller session "
  "shows; 'refuse' would mean turning it down, leaving the numbers the other way around.",
  "medium", 0.95),

 ("outset",
  "The budget was tight from the outset, and nothing that happened later improved it.",
  "very beginning",
  [("very end", "opposite"), ("outer edge", "form"), ("worst moment", "nuance")],
  "The outset is the start of something, which 'nothing later improved it' confirms; "
  "'worst moment' would single out one bad point rather than name the beginning.",
  "medium", 0.94),

 ("pester",
  "The magpies will pester anyone eating chips near the rotunda until the bag is gone.",
  "keep bothering",
  [("politely avoid", "opposite"), ("firmly attack", "overreach"), ("closely watch", "nuance")],
  "To pester is to trouble someone repeatedly with small annoyances, which is what the "
  "birds do; 'firmly attack' overstates it, since pestering stops short of swooping.",
  "medium", 0.93),

 ("precise",
  "The measurements need to be precise, because a millimetre out at this end is a "
  "centimetre out at the other.",
  "exact",
  [("rough", "opposite"), ("prized", "form"), ("quick", "domain")],
  "Precise means exactly stated or measured, which the tolerance explains; 'rough' is the "
  "degree of accuracy the job specifically cannot afford.",
  "medium", 0.95),

 ("quiver",
  "You could see the rope quiver each time the current pushed against the pontoon.",
  "tremble",
  [("hold still", "opposite"), ("shiver", "nuance"), ("stretch", "domain")],
  "To quiver is to shake with a slight rapid motion, which the current would cause; "
  "'shiver' is nearly the same movement but is used of a cold or frightened body.",
  "hard", 0.90),

 ("rally",
  "The side managed to rally in the last quarter and finished within a goal of the lead.",
  "recover strongly",
  [("collapse badly", "opposite"), ("really try", "form"), ("gather together", "nuance")],
  "To rally is to recover after doing badly, which closing the gap late describes; "
  "'gather together' is another sense of the word but does not fit a scoreline.",
  "medium", 0.93),

 ("reckon",
  "The old hands reckon the river will drop again before the end of the week.",
  "believe",
  [("doubt", "opposite"), ("beckon", "form"), ("measure", "nuance")],
  "To reckon here is to hold an opinion about what will happen, which a prediction is; "
  "'measure' is the arithmetic sense of the word and does not fit a forecast.",
  "medium", 0.93),

 ("refine",
  "Two more seasons were spent refining the design before it was offered to buyers.",
  "improve gradually",
  [("abandon quickly", "opposite"), ("redefine fully", "form"), ("rebuild entirely", "overreach")],
  "To refine is to make small improvements to something that already works, which two "
  "seasons of adjustment suggests; 'rebuild entirely' would mean starting again.",
  "medium", 0.93),

 ("remote",
  "The station is remote enough that mail arrives by air once a fortnight.",
  "far away",
  [("close by", "opposite"), ("run by radio", "form"), ("badly served", "nuance")],
  "Remote means distant from other places, which fortnightly air mail illustrates; 'badly "
  "served' is a consequence of the distance rather than the meaning of the word.",
  "medium", 0.94),

 ("render",
  "The flood rendered the lower road impassable for most of the following month.",
  "make",
  [("keep", "opposite"), ("surrender", "form"), ("repair", "domain")],
  "To render something a certain way is to cause it to become so, which the flood did to "
  "the road; 'repair' describes fixing it afterwards, the opposite of the effect.",
  "medium", 0.93),

 ("resent",
  "Some of the older members resent the change to the training times, though few say so "
  "openly.",
  "feel bitter about",
  [("feel pleased by", "opposite"), ("send again to", "form"), ("openly object to", "nuance")],
  "To resent something is to feel quiet indignation at it, which 'few say so openly' fits "
  "exactly; 'openly object to' describes speaking up, which the sentence says they avoid.",
  "hard", 0.91),

 ("resolve",
  "It took three meetings to resolve the dispute over the boundary fence.",
  "settle",
  [("prolong", "opposite"), ("dissolve", "form"), ("discuss", "nuance")],
  "To resolve a dispute is to bring it to an end, which is what the third meeting achieved; "
  "'discuss' is what the earlier meetings did without ever reaching that point.",
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
