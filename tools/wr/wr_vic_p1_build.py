#!/usr/bin/env python3
"""Builds wr_vic_acer_p1.json — 11 creative-slot prompts for the VIC paper.

CALIBRATION. The VIC writing test is TWO tasks in 40 minutes, sat in Year 8 (ACER's own
preparation page, confirmed 2026-08-12). That is ~20 minutes a task, so these ask for
160-260 words, not the 350-500 the ten legacy VIC rows were written for. A prompt that
cannot be finished in the time is not a hard prompt, it is a broken one.

WHAT A 20-MINUTE CREATIVE TASK CAN ACTUALLY BE. Twenty minutes buys one scene, not a plot.
Every prompt here is therefore built around a single situation with a decision inside it,
and says so — "one afternoon", "the ten minutes before", "the moment after". Prompts that
invite a saga are the commonest way a good writer loses this section: they spend the time
summarising events instead of writing.

TASK PHRASING IS DELIBERATELY VARIED. wr_finalise rejects a task 0.72 similar to any
other, and eleven prompts that all open "Write a narrative about..." would trip it —
but the real reason is that a stock opening trains a stock response.

Held before this batch: 4 in the creative slot (narrative 3, diary 1). Target 27.
"""
import datetime
import json
import pathlib
import sys
import uuid

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/writing/generated"
BOOK = "wr_vic_acer"
NN = 1
NOW = datetime.datetime(2026, 8, 12, 9, 0, 0, tzinfo=datetime.timezone.utc) \
    .isoformat().replace("+00:00", "Z")

PROMPTS = []


def P(stimulus_type, stimulus, task, topic, focus, lo=160, hi=260, difficulty="medium"):
    PROMPTS.append({
        "id": str(uuid.uuid4()),
        "prompt_type": "narrative",
        "school_type": "victorian_selective",
        "stimulus_type": stimulus_type,
        "stimulus_content": stimulus,
        "stimulus_image_desc": None,
        "task_instruction": task,
        "word_count_min": lo,
        "word_count_max": hi,
        "time_limit_minutes": 20,
        "target_year": "7-8",
        "difficulty": difficulty,
        "topic": topic,
        "marking_focus": json.dumps(focus),
        "source_book": BOOK,
        "review_status": "pending",
        "created_at": NOW,
    })


P("scenario",
  "The bus from Bendigo is twenty minutes late and there is one other person waiting at "
  "the stop: someone you used to know well and have not spoken to in over a year. Neither "
  "of you has moved to the far end of the shelter, which would have been the easy thing "
  "to do. The timetable says the bus is still coming.",
  "Write a narrative set entirely in those twenty minutes at the bus stop. Keep the whole "
  "story inside the wait — do not follow the characters onto the bus. What is not said "
  "should carry as much weight as what is.",
  "Reconnection", ["character", "dialogue", "restraint", "language"]),

P("quote",
  "\"I was the only one who saw it, which meant that for the rest of the afternoon I had "
  "to decide what kind of person I was going to be about it.\"",
  "Use this sentence to open a narrative set in an Australian school, workplace or "
  "street. The reader should never be told outright what was seen — let the character's "
  "afternoon make it clear. End at the point the decision is made, not after it.",
  "Conscience", ["voice", "structure", "implication", "language"], difficulty="hard"),

P("scenario",
  "A hot northerly has been blowing across the Wimmera since dawn. The sheets on the line "
  "are dry inside ten minutes. The radio in the kitchen has been on all day, and at four "
  "o'clock the announcer stops reading the football scores and starts reading district "
  "names instead.",
  "Write a narrative in which the weather is doing more than sitting in the background. "
  "The reader should feel the day tighten. Focus on one household and one hour.",
  "Bushfire and Rural Life", ["atmosphere", "detail", "tension", "language"]),

P("scenario",
  "Every Sunday for six years your grandmother has cooked the same meal for the same "
  "people at the same table in her house in Footscray. This Sunday she has set the table "
  "for one fewer person, and nobody has mentioned it.",
  "Write a narrative about this Sunday lunch. Tell it through what people do rather than "
  "what they explain — who sits where, who talks too much, who goes to the kitchen. The "
  "empty place should never need to be described.",
  "Family and Absence", ["character", "subtext", "detail", "language"], difficulty="hard"),

P("quote",
  "\"There is a kind of courage that looks, from the outside, exactly like doing nothing. "
  "It is the courage of the person who stays in the room, or who does not repeat what they "
  "were told, or who lets somebody else finish being wrong in peace. Nobody in Australia "
  "hands out medals for it.\"",
  "Write a narrative in which a character shows this kind of courage. Somebody watching "
  "them should misread it completely. The story can end without that misunderstanding "
  "being corrected.",
  "Courage", ["character", "perspective", "structure", "language"], difficulty="hard"),

P("scenario",
  "The tide at Port Fairy goes out a long way. At low tide you can walk out over the flats "
  "for ten minutes and still be in ankle-deep water. Two cousins have walked out further "
  "than they meant to, and one of them has just looked back at the beach.",
  "Write a narrative that begins at the moment of looking back. Twenty minutes of writing "
  "is one scene, so stay in it: the walk out is over, and the story is what happens now.",
  "Risk and Judgement", ["tension", "pacing", "character", "language"]),

P("text",
  "A community noticeboard outside a hall in Castlemaine carries four things: a flyer for "
  "a lost dog, last updated in March; a notice about the water tank; a hand-written card "
  "offering piano lessons, with the tear-off phone numbers all still attached; and a "
  "faded photograph of a football team with no year written on it.",
  "Choose one item on the noticeboard and write a narrative about the person who put it "
  "there. The noticeboard itself may appear only once. Give the reader the person, not "
  "the explanation.",
  "Small Towns", ["character", "imagination", "detail", "language"]),

P("scenario",
  "You have been given a job you are not quite good enough at yet: minding the front desk "
  "of the council pool in Geelong on a Saturday, alone, for the first time. There is a "
  "laminated card by the phone with three numbers on it and no explanation of when to ring "
  "which. It is quiet. Then it is not quiet.",
  "Write a narrative about the first hour of this job. The character should get something "
  "wrong. Do not rescue them with a lucky accident — let them handle it, well or badly.",
  "Responsibility", ["character", "plausibility", "structure", "language"]),

P("quote",
  "\"We had been driving for so long that the paddocks had stopped changing, and my father "
  "had stopped pretending he knew where we were. Somewhere behind us was Horsham. "
  "Somewhere ahead was the turn-off he was certain he would recognise when he saw it. "
  "Between those two certainties there was a great deal of Victoria.\"",
  "Use this sentence somewhere in a narrative — at the beginning, the middle or the end. "
  "The journey matters less than what happens between the two people in the car.",
  "Journeys", ["voice", "character", "structure", "language"]),

P("scenario",
  "A magpie has been swooping the same stretch of footpath in Preston for three weeks. The "
  "primary school children have started taking the long way around. This morning somebody "
  "has tied a hand-lettered cardboard sign to the pole: BE NICE TO HIM, HE LIVES HERE.",
  "Write a narrative about the person who made the sign, set on the morning they made it. "
  "Twenty minutes is one scene — choose the moment they decided, not the whole three weeks.",
  "Community", ["character", "humour", "detail", "language"]),

P("text",
  "In the second week of the school holidays the shopping centre in Dandenong runs a "
  "\"holiday program\" in the empty shop next to the chemist. It has a table, a box of "
  "textas, forty sheets of butcher's paper, and one adult who is being paid to be there. "
  "Nine children turn up on the first day. On the second day, three do.",
  "Write a narrative set on that second day, from the point of view of either the adult or "
  "one of the three children. Whoever tells it should not fully understand the other.",
  "Belonging", ["perspective", "character", "restraint", "language"], difficulty="hard"),


if __name__ == "__main__":
    GEN.mkdir(parents=True, exist_ok=True)
    path = GEN / f"{BOOK}_p{NN}.json"
    path.write_text(json.dumps(PROMPTS, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    print(f"wrote {len(PROMPTS)} prompts -> {path}")
