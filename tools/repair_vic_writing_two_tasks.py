"""Split the 54 VIC writing prompts into the two shapes the real paper sets, and pair them.

THE CORRECTION THIS APPLIES. The 54 prompts were built to a single band -- ~20 minutes,
160-260 words -- on the assumption that the paper's two tasks are alike and that drill
serves one at a time. Neither is true. The paper sets a **short task of about 150 words
and an extended one of about 250**, and a writing drill has to serve **both, in 40
minutes**, because unlike MCQ the exercise does not survive being halved:

  - Budgeting across two tasks is itself the skill being examined. A candidate who spends
    28 minutes on the piece they are enjoying has failed the paper, and will never find
    that out by practising one piece at a time.
  - The second task is written by a tired writer who has already spent their best ideas.
    That is where marks are lost, and a single-prompt drill never reaches it.
  - MCQ is different and does scale: halve the questions and halve the time and the
    candidate still meets the same seconds per question, so doubling back up predicts the
    real sitting. Writing has no equivalent invariant.

    short     130-170 words, 15 minutes
    extended  220-290 words, 25 minutes      15 + 25 = the paper's 40

WHY LENGTH IS ORTHOGONAL TO GENRE HERE. The paper sets one creative task and one
persuasive/analytical task, and it also sets one short and one extended -- but which
genre carries which length is not published anywhere found. So both genres hold prompts
in both bands, and each dealt form pairs one creative with one persuasive such that one
is short and one is extended. If the pairing turns out to be fixed in the real paper,
that is a re-band of one column and not a rewrite.

RE-CUTTING, WHICH IS THE PART THAT IS NOT ARITHMETIC. Moving a prompt to 150 words breaks
some of its instructions, in exactly the way the legacy VIC prompts were broken at 20
minutes:

  - **Five tasks name the writing time in their own text** ("Twenty minutes is one
    scene"). Two of those five mean twenty minutes *inside the story* -- the bus wait,
    the argument between two students -- and are correct as they stand. Three meant the
    clock and are now wrong.
  - **Eight ask for two deliverables or for a counter-argument.** At 150 words "and also
    offer two practical changes" or "deal with the strongest argument against you" is
    unaffordable, and a candidate who obeys runs out of room while one who does not is
    marked down for it. This is the same defect fixed in the ten legacy prompts, back
    again because the band moved underneath them.

Marking focus follows: a short persuasive prompt that no longer asks for a counter should
not be marked on one, so `counter-argument` is replaced with `economy` -- which is the
real short-form skill.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_vic_writing_two_tasks --dry-run
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_vic_writing_two_tasks --apply
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "run_data" / "db" / "qbank.db"
MANIFEST = REPO_ROOT / "run_data" / "output" / "vic_writing_two_tasks.json"

BANDS = {
    "short":    {"lo": 130, "hi": 170, "minutes": 15},
    "extended": {"lo": 220, "hi": 290, "minutes": 25},
}

# Keyed by topic, which is unique across the 54. Everything not listed is extended.
# Chosen by reading: a prompt goes short when its task is already one moment or one
# judgement, and extended when it needs room to develop.
SHORT_TOPICS = {
    # creative slot -- 14
    "Reconnection", "Risk and Judgement", "Community", "Patience and Perspective",
    "Pressure and Time", "Everyday Mysteries", "Solitude", "Conscience", "Small Towns",
    "Fairness", "Trust", "Growing Up", "Heritage",
    "Climate Change and Human Experience",
    # persuasive slot -- 13
    "Fairness vs consistency", "Winning vs retention", "Safety vs risk",
    "Loyalty vs help", "Livelihood vs amenity", "Measurement and Values", "Priorities",
    "Public Institutions", "Assessment", "Sport and Fairness", "Environment and Society",
    "Health and Society", "Health and Wellbeing",
}

# The creative slot. Everything else counts to the persuasive/analytical slot.
CREATIVE_TYPES = {"narrative", "diary"}

# topic -> replacement task_instruction, where 150 words broke the instruction.
RECUT: dict[str, str] = {
    # --- named the clock, and the clock changed
    "Risk and Judgement":
        "Write a narrative that begins at the moment of looking back. This is the short "
        "task, so it is one scene: the walk out is over, and the story is what happens now.",
    "Community":
        "Write a narrative about the person who made the sign, set on the morning they "
        "made it. This is the short task — choose the moment they decided, not the whole "
        "three weeks.",
    "Everyday Mysteries":
        "One of these items has been left behind twice in the same week. Write a narrative "
        "about the person who keeps losing it. This is the short task — write the second "
        "time, not the first.",
    # --- asked for two things, or for a counter, at 150 words
    "Health and Wellbeing":
        "Write an informative article for a school magazine explaining why teenagers need "
        "more sleep than adults, and offer one practical change a student could make this "
        "week. Use the findings in the stimulus.",
    "Health and Society":
        "Write an informative article for a general audience explaining what is driving "
        "the rise in youth mental health problems in Australia. Draw on the report for "
        "evidence, and choose the one factor you can explain properly in the space.",
    "Climate Change and Human Experience":
        "Write a diary entry from the perspective of a 16-year-old on the day of this "
        "second relocation. Focus on voice and one or two specific details rather than "
        "listing the events of the day.",
    "Environment and Society":
        "Write a persuasive essay arguing for or against the view expressed in the quote. "
        "Support your position with reasoning and one specific example. At this length one "
        "example developed beats three mentioned.",
    "Assessment":
        "Write a persuasive piece arguing for one of these two systems. This is the short "
        "task, so make your single strongest point properly rather than listing several.",
    "Public Institutions":
        "Write a persuasive piece arguing whether libraries should charge overdue fines. "
        "Use what the passage tells you, and choose the one reason you can make stick.",
    "Sport and Fairness":
        "Write a persuasive piece supporting or opposing the equal game time rule. Make "
        "one argument well rather than three quickly.",
    "Loyalty vs help":
        "Write a persuasive piece arguing what you should do, addressed to yourself. Take "
        "one position and hold it — at this length the strongest single case beats a "
        "weighing-up of both.",
}

# Marking focus for short prompts that no longer ask for a counter-argument.
FOCUS_SWAP = {"counter-argument": "economy", "balance": "economy"}


def band_of(topic: str) -> str:
    return "short" if topic in SHORT_TOPICS else "extended"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    if not (args.dry_run or args.apply):
        ap.error("choose --dry-run or --apply")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute(
        "SELECT * FROM writing_prompts WHERE school_type = 'victorian_selective'")]
    now = datetime.now(timezone.utc).isoformat()
    record, recut_n, focus_n = [], 0, 0

    for r in rows:
        band = band_of(r["topic"])
        spec = BANDS[band]
        task = RECUT.get(r["topic"], r["task_instruction"])
        focus = json.loads(r["marking_focus"])
        if band == "short":
            new_focus = [FOCUS_SWAP.get(f, f) for f in focus]
            # never leave a duplicate behind if both counter-argument and balance were listed
            seen, deduped = set(), []
            for f in new_focus:
                if f not in seen:
                    seen.add(f)
                    deduped.append(f)
            new_focus = deduped
        else:
            new_focus = focus

        changed = []
        if r["word_count_min"] != spec["lo"] or r["word_count_max"] != spec["hi"]:
            changed.append(f"words {r['word_count_min']}-{r['word_count_max']} -> "
                           f"{spec['lo']}-{spec['hi']}")
        if r["time_limit_minutes"] != spec["minutes"]:
            changed.append(f"time {r['time_limit_minutes']} -> {spec['minutes']} min")
        if task != r["task_instruction"]:
            changed.append("task re-cut")
            recut_n += 1
        if new_focus != focus:
            changed.append(f"focus {focus} -> {new_focus}")
            focus_n += 1
        if not changed:
            continue

        slot = "creative" if r["prompt_type"] in CREATIVE_TYPES else "persuasive"
        print(f"\n{band.upper():<9} {slot:<10} {r['topic']}")
        for ch in changed:
            print(f"    {ch}")
        if task != r["task_instruction"]:
            print(f"      was: {' '.join(r['task_instruction'].split())[:140]}")
            print(f"      now: {' '.join(task.split())[:140]}")
        record.append({"id": r["id"], "topic": r["topic"], "band": band, "slot": slot,
                       "changes": changed})

        if args.apply:
            conn.execute(
                "UPDATE writing_prompts SET word_count_min = ?, word_count_max = ?, "
                "time_limit_minutes = ?, task_instruction = ?, marking_focus = ?, "
                "edited = 1 WHERE id = ?",
                (spec["lo"], spec["hi"], spec["minutes"], task,
                 json.dumps(new_focus), r["id"]))

    shorts = sum(1 for r in rows if band_of(r["topic"]) == "short")
    print(f"\nshort {shorts} / extended {len(rows) - shorts}"
          f"   |   {recut_n} tasks re-cut, {focus_n} marking-focus lists adjusted")

    if args.apply:
        conn.commit()
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(json.dumps(
            {"generated_from": "tools/repair_vic_writing_two_tasks.py",
             "applied_at": now, "bands": BANDS, "prompts": record}, indent=2))
        print(f"Applied to {len(record)} prompts. Record: {MANIFEST}")
    else:
        print(f"Dry run: {len(record)} prompts would change. Nothing written.")


if __name__ == "__main__":
    main()
