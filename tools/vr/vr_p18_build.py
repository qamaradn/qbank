#!/usr/bin/env python3
"""Builds vr_vic_acer_p18.json — 30 sentence-completion questions (TASK §3.4).

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
NN = 18
BOOK = "vr_vic_acer"
CATEGORY = "sentence_completion"
LABEL = "Sentence completion"
NOW = datetime.datetime(2026, 8, 11, 12, 0, 0, tzinfo=datetime.timezone.utc) \
    .isoformat().replace("+00:00", "Z")

# (key, sentence with ______, [(distractor, relation) x3], explanation, difficulty, conf)
ITEMS = [
 ("dissuade", "Nothing his brother said could ______ him from entering the longer race.",
  [("persuade", "opposite"), ("dissolve", "form"), ("prevent", "overreach")],
  "To dissuade is to talk somebody out of a decision, which is what a brother's words could attempt; 'prevent' would mean physically stopping him, which speech cannot do.", "medium", 0.92),
 ("culminate", "Three weeks of rehearsal will ______ in a single performance on the Friday.",
  [("conclude", "nuance"), ("rehearse", "collocation"), ("begin", "opposite")],
  "'Culminate in' is the phrase for a build-up reaching its high point, which three weeks leading to one night describes; 'conclude' would merely end rather than climax.", "medium", 0.92),
 ("coincide", "The finals ______ with the school holidays again this year.",
  [("clash", "domain"), ("compete", "nuance"), ("differ", "opposite")],
  "Things that happen at the same time coincide; 'collide' sounds similar but means to crash into each other.", "medium", 0.94),
 ("grapple", "Councils across the state are still trying to ______ with the cost of the repairs.",
  [("negotiate", "domain"), ("dismiss", "opposite"), ("calculate", "nuance")],
  "To grapple with a problem is to struggle with it over time, which is what 'still trying' sets up; 'grasp' means to understand rather than to wrestle with.", "medium", 0.92),
 ("hoist", "Two of them were needed to ______ the mainsail in that wind.",
  [("heave", "nuance"), ("trim", "domain"), ("lower", "opposite")],
  "A sail is hoisted, which is the specific word for raising it on a rope; 'heave' describes effort but not the upward raising of a sail.", "medium", 0.93),
 ("convene", "The committee will ______ again in March to review the decision.",
  [("converge", "form"), ("conclude", "opposite"), ("attend", "domain")],
  "A committee convenes when it comes together for a formal meeting, which is what March is for; 'converge' means to come together physically and is not used of meetings.", "medium", 0.92),
 ("mingle", "Guests were slow to ______ until the music started.",
  [("arrive", "domain"), ("gather", "nuance"), ("scatter", "opposite")],
  "To mingle is to move among others and talk, which is what a party needs; 'gather' would mean coming together in one place rather than circulating.", "medium", 0.93),
 ("subside", "The swelling should ______ within a day or two.",
  [("bruise", "collocation"), ("vanish", "overreach"), ("worsen", "opposite")],
  "Swelling subsides as it gradually goes down; 'vanish' claims complete disappearance, which is more than a day or two would give.", "medium", 0.93),
 ("veer", "The track begins to ______ east about a kilometre past the gate.",
  [("climb", "domain"), ("wander", "nuance"), ("straighten", "opposite")],
  "A track veers when it changes direction fairly sharply, which 'east' pins down; 'wander' suggests aimless meandering rather than a definite turn.", "medium", 0.93),
 ("waive", "The club agreed to ______ the joining fee for first-year students.",
  [("invoice", "collocation"), ("reduce", "nuance"), ("impose", "opposite")],
  "To waive a fee is to give up the right to charge it, which is what the club did; 'wave' is the identical-sounding word for a hand movement.", "medium", 0.94),
 ("teem", "By November the shallows ______ with small fish.",
  [("team", "form"), ("fill", "nuance"), ("empty", "opposite")],
  "Water teems when it is crowded with moving life, which is the specific word here; 'team' is the homophone meaning a group of players.", "medium", 0.93),
 ("stall", "The negotiations began to ______ over the question of the ground lease.",
  [("stale", "form"), ("collapse", "overreach"), ("accelerate", "opposite")],
  "Talks stall when they stop making progress but have not ended; 'collapse' would mean they had broken down completely.", "medium", 0.93),
 ("relay", "Volunteers ______ the messages between the two camps twice a day.",
  [("delay", "form"), ("compose", "nuance"), ("withhold", "opposite")],
  "To relay a message is to pass it on from one place to another, which is exactly the volunteers' job; 'compose' would mean writing the messages themselves.", "medium", 0.93),
 ("salvage", "Only a few boxes of records could be ______ from the flooded office.",
  [("savage", "form"), ("restore", "nuance"), ("discard", "opposite")],
  "To salvage is to rescue what survives from a disaster, which is precisely the flooded-office case; 'restore' would mean repairing the records rather than getting them out.", "medium", 0.92),
 ("protrude", "A single nail was left to ______ from the board at head height.",
  [("intrude", "form"), ("emerge", "nuance"), ("recede", "opposite")],
  "Something protrudes when it sticks out from a surface, which is what a nail does; 'intrude' means to enter where one is not wanted.", "medium", 0.93),
 ("straddle", "The new boundary will ______ the creek for about two kilometres.",
  [("strangle", "form"), ("follow", "nuance"), ("avoid", "opposite")],
  "To straddle something is to extend across both sides of it, which is what the boundary does to the creek; 'follow' would run alongside rather than across.", "medium", 0.92),
 ("stray", "Two of the heifers had begun to ______ towards the highway fence.",
  [("spray", "form"), ("graze", "domain"), ("return", "opposite")],
  "Animals stray when they drift away from where they should be, which the highway fence makes worrying; 'graze' is what the heifers do where they are, not a movement away from it.", "medium", 0.92),
 ("tamper", "Signs warn people not to ______ with the water gauges.",
  [("temper", "form"), ("touch", "nuance"), ("maintain", "opposite")],
  "To tamper with equipment is to interfere with it improperly, which is what the warning forbids; 'touch' is too mild to carry the sense of meddling.", "medium", 0.94),
 ("topple", "One more strong gust would have been enough to ______ the whole stack.",
  [("tipple", "form"), ("shift", "nuance"), ("steady", "opposite")],
  "To topple is to fall over completely, which is what a stack does in a gust; 'shift' would mean moving without falling.", "medium", 0.94),
 ("thrust", "He had to ______ his shoulder against the door to get it open.",
  [("brace", "domain"), ("lean", "nuance"), ("withdraw", "opposite")],
  "To thrust is to push suddenly and hard, which forcing a stuck door requires; 'brace' would mean holding the shoulder steady rather than driving it forward.", "medium", 0.93),
 ("wade", "You can ______ across the channel at low tide without much trouble.",
  [("paddle", "domain"), ("swim", "nuance"), ("sink", "opposite")],
  "To wade is to walk through shallow water, which low tide makes possible; 'swim' would mean the water was too deep to stand in.", "medium", 0.94),
 ("wield", "Only two people on the committee actually ______ any influence.",
  [("resist", "domain"), ("seek", "nuance"), ("lack", "opposite")],
  "To wield influence is to hold and use it, which is the standard phrase; 'seek' would mean wanting influence rather than having it.", "medium", 0.93),
 ("dispatch", "The office will ______ the replacement part the same afternoon.",
  [("detach", "form"), ("deliver", "nuance"), ("retain", "opposite")],
  "To dispatch is to send something off, which is what an office does; 'deliver' is what happens at the other end of the journey.", "medium", 0.92),
 ("dwell", "There is no point continuing to ______ on a decision that cannot be changed.",
  [("swell", "form"), ("decide", "domain"), ("forget", "opposite")],
  "To dwell on something is to keep turning it over in your mind, which the sentence advises against; 'decide' is the act that has already happened.", "medium", 0.93),
 ("falter", "Her voice began to ______ halfway through the second verse.",
  [("filter", "form"), ("rise", "opposite"), ("carry", "nuance")],
  "To falter is to become unsteady and lose momentum, which is what a voice does under strain; 'carry' would mean it reached the back of the room.", "medium", 0.93),
 ("glean", "Reporters could ______ very little from the short statement.",
  [("clean", "form"), ("publish", "domain"), ("supply", "opposite")],
  "To glean is to gather small amounts of information with effort, which a short statement allows; 'publish' is what reporters do afterwards.", "medium", 0.92),
 ("jostle", "Passengers began to ______ for position as the doors opened.",
  [("joggle", "form"), ("queue", "opposite"), ("hurry", "nuance")],
  "To jostle is to push against others in a crowd, which is what happens at a door; 'queue' is the orderly behaviour the sentence rules out.", "medium", 0.93),
 ("lurk", "Something was ______ in the shallows just off the ramp.",
  [("lark", "form"), ("swim", "nuance"), ("surface", "opposite")],
  "To lurk is to wait unseen, which suits something noticed only vaguely in shallow water; 'swim' describes movement without the hidden waiting.", "medium", 0.93),
 ("pivot", "The whole argument seems to ______ on one line in the contract.",
  [("privet", "form"), ("depend", "nuance"), ("ignore", "opposite")],
  "An argument pivots on the point everything else turns around, which one decisive line is; 'depend' is close but lacks the sense of turning.", "medium", 0.91),
 ("scour", "They had to ______ the whole shed before the spare was found.",
  [("scout", "form"), ("tidy", "domain"), ("ignore", "opposite")],
  "To scour a place is to search it thoroughly, which finding one spare part required; 'tidy' is a different activity that might happen at the same time.", "medium", 0.93),
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
