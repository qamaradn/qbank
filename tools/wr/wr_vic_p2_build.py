#!/usr/bin/env python3
"""Builds wr_vic_acer_p2.json — 12 creative-slot prompts, completing the slot at 27.

Same calibration as p1: two tasks, ~20 minutes each, Year 8, 160-260 words. See
tools/wr/wr_vic_p1_build.py for why a 20-minute prompt is built around one scene.

WHAT THIS BATCH ADDS THAT p1 DID NOT. p1 leans on quiet domestic and small-town
situations, which is where a thoughtful Year 8 writer is strongest but is not the whole
of what ACER can set. This batch widens the range on purpose:

  - three prompts with a data or document stimulus (a timetable, a receipt, a form), so a
    candidate who has only practised "write about a memory" meets something else
  - two written from a stated constraint rather than a situation ("no dialogue", "the
    last line is given"), which is a real ACER habit
  - two set outside the domestic register entirely — work, and a public place

Held before this batch: 15 in the creative slot. Target 27.
"""
import datetime
import json
import pathlib
import sys
import uuid

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/writing/generated"
BOOK = "wr_vic_acer"
NN = 2
NOW = datetime.datetime(2026, 8, 12, 10, 0, 0, tzinfo=datetime.timezone.utc) \
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


P("data",
  "Lost property log — Warrnambool Library, week ending 14 June\n\n"
  "Mon — one grey scarf; a set of keys with a wooden fish keyring\n"
  "Tue — nothing\n"
  "Wed — a library card in the name of R. Alvarez; one child's gumboot, left foot\n"
  "Thu — the same set of keys with the wooden fish keyring\n"
  "Fri — one grey scarf; a paperback with a boarding pass used as a bookmark",
  "One of these items has been left behind twice in the same week. Write a narrative "
  "about the person who keeps losing it. Twenty minutes is one scene — choose the second "
  "time, not the first.",
  "Everyday Mysteries", ["character", "imagination", "structure", "language"]),

P("data",
  "Receipt — Shepparton Hardware, 7.42 am\n\n"
  "  Timber screws, box of 100 ........ $8.95\n"
  "  Sandpaper, medium, 5 sheets ...... $6.40\n"
  "  Wood glue, 250 ml ................ $11.20\n"
  "  Sausage roll ..................... $4.50\n"
  "  TOTAL ........................... $31.05\n\n"
  "Handwritten on the back: \"don't tell her yet\"",
  "Write a narrative that explains this receipt without ever mentioning it. The reader "
  "should reach the end and understand what was being built, and why it was a secret.",
  "Secrets and Making", ["structure", "implication", "character", "language"],
  difficulty="hard"),

P("data",
  "Bus 623 — weekday timetable, final four services\n\n"
  "  Depart Ballarat station    4.55 pm   5.40 pm   6.25 pm   7.10 pm\n"
  "  Arrive Sebastopol shops    5.19 pm   6.04 pm   6.49 pm   7.34 pm\n\n"
  "Note: the 7.10 pm service does not run on public holidays.",
  "Write a narrative about somebody who needs the last bus and is not going to make it. "
  "The timetable may be mentioned once. What matters is the walk, or the phone call, or "
  "the decision to do neither.",
  "Pressure and Time", ["tension", "character", "pacing", "language"]),

P("scenario",
  "A character is packing up a room. Not their own room, and not because anyone has died "
  "— the reason is more ordinary than that, and slightly worse. They have four boxes and "
  "one afternoon, and everything they pick up takes longer than it should.",
  "Write a narrative about this afternoon in which no character speaks aloud. Everything "
  "the reader learns must come from objects, actions and thought. Set it somewhere in "
  "Australia the reader can picture.",
  "Endings", ["restraint", "detail", "character", "language"], difficulty="hard"),

P("quote",
  "\"And that, I decided, was the last time I would ever be the youngest person in the "
  "room.\"\n\nSome decisions are made all at once, at a particular hour, in a particular "
  "place, and the person making them knows it at the time. Most are not like that. This "
  "one was made in a hall in Ballarat, on a Tuesday, at about half past seven.",
  "End a narrative with this sentence. Everything before it should earn it. The reader "
  "should not need the sentence explained once they arrive at it.",
  "Growing Up", ["structure", "voice", "character", "language"], difficulty="hard"),

P("scenario",
  "Casual work at the Mildura fruit packing shed starts at six in the morning. On the "
  "first day nobody explains anything, because everybody assumes somebody else already "
  "has. By the first break your character has been doing one part of the job wrong for "
  "two hours, and the person on the next bench has just noticed.",
  "Write a narrative set between that moment and the end of the break. The story is in "
  "how the two of them handle it, not in whether the mistake gets fixed.",
  "Work and Dignity", ["character", "dialogue", "plausibility", "language"]),

P("scenario",
  "The queue at the Queen Victoria Market has not moved in four minutes. At the front of "
  "it, a transaction has gone wrong in some way the people further back cannot see. Your "
  "character is seventh in the queue and in a hurry.",
  "Write a narrative from inside this queue. The character must never reach the front. "
  "Let the reader learn more about the person waiting than about whatever is happening "
  "ahead of them.",
  "Patience and Perspective", ["perspective", "humour", "character", "language"]),

P("text",
  "Notice pinned inside the door of a Gippsland dairy:\n\n"
  "\"To whoever has been leaving the gate open — I am not angry. I am fifty-eight years "
  "old and I have walked that paddock at eleven o'clock at night four times this month. "
  "If you need to come through, come and say so and I will give you a key.\"",
  "Write a narrative about the person the notice is addressed to, set on the night they "
  "read it. Whether they come and say so is up to you, but the reader should understand "
  "why they were coming through.",
  "Trust", ["character", "motivation", "structure", "language"]),

P("scenario",
  "Two students have been put together on a project neither of them chose. One has done "
  "all the work. It is the afternoon before it is due, and the one who has not done the "
  "work has just arrived with something genuinely good.",
  "Write a narrative about the next twenty minutes between them. Neither character should "
  "be simply in the right. Australian school setting.",
  "Fairness", ["character", "dialogue", "balance", "language"], difficulty="hard"),

P("quote",
  "\"My grandmother spoke three languages and my mother speaks two and I speak one, and "
  "the joke in our family is that my children will communicate entirely by pointing. "
  "Nobody laughs at it any more. Somewhere between Melbourne and here, something was put "
  "down and not picked back up.\"",
  "Write a narrative in which a character notices something being lost between "
  "generations. It does not have to be language. Keep it to one occasion.",
  "Heritage", ["voice", "character", "theme", "language"], difficulty="hard"),

P("scenario",
  "Somebody has been feeding a stray cat behind the shops at Torquay for a year. This "
  "week a sign went up on the fence: the block has been sold and the demolition starts "
  "on the 20th. The cat does not read signs.",
  "Write a narrative about the days before the 20th. The cat is not the point of the "
  "story and should not narrate it.",
  "Care and Change", ["character", "restraint", "structure", "language"]),

P("text",
  "Three entries from a school's incident book, all in the same term:\n\n"
  "  9 May — Y8 student found in the library at lunch, third time this week. No issue.\n"
  "  23 May — Same student, library again. Spoke with them. No issue.\n"
  "  6 June — Same student. Suggested the yard. Student declined. No issue.",
  "Write a narrative from the point of view of the student in these entries, set at one "
  "lunchtime in an Australian secondary school. The teacher who wrote \"no issue\" three "
  "times may or may not be right.",
  "Solitude", ["perspective", "voice", "character", "language"]),


if __name__ == "__main__":
    GEN.mkdir(parents=True, exist_ok=True)
    path = GEN / f"{BOOK}_p{NN}.json"
    path.write_text(json.dumps(PROMPTS, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    print(f"wrote {len(PROMPTS)} prompts -> {path}")
