"""Recalibrate the ten victorian_selective writing prompts to the exam that exists.

They were written for a 30-minute, single-task, 350-500 word paper aimed at Year 9-10.
The VIC paper is none of those things. Confirmed against ACER's own preparation page on
2026-08-12: **"The writing test consists of two tasks"**, 40 minutes, inside a 2h35m
paper sat in Year 8 for Year 9 entry. Two tasks in 40 minutes is about 20 minutes each.

`vic_content_taxonomy_TASK.md` §6 rated the two-task format "Confidence: Low" and asked
for a first-hand check before authoring against it. The check is done and it holds. One
prep site (educourse) describes the paper as offering two prompts and letting the
candidate choose one, which would mean ~35 minutes and 400-550 words; it is the minority
reading against ACER's own wording plus three other secondary sources, and it is recorded
in §6 rather than followed. If it turns out to be right, only these numbers change -- the
prompt count of 54 is the same either way, because the paper prints two prompts regardless.

So: 30 -> 20 minutes, Year 9-10 -> Year 7-8, and word bands cut to what a Year 8 writer
actually produces in 20 minutes once planning and a read-back come out.

**Three of the ten needed more than new numbers.** Their task instructions ask for three
separate deliverables -- "explain why adolescents need more sleep, summarise the key
findings, and offer two practical recommendations" is three pieces of writing, not one,
and it was already ambitious at 30 minutes. At 20 it is a trap: the candidate who obeys
the instruction runs out of time and the one who ignores part of it is marked down for
it. Those three are re-cut to two deliverables. The other seven are well made and are
left alone apart from the calibration fields.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_vic_writing_calibration --dry-run
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_vic_writing_calibration --apply
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "run_data" / "db" / "qbank.db"
MANIFEST = REPO_ROOT / "run_data" / "output" / "vic_writing_calibration.json"

TIME_LIMIT = 20
TARGET_YEAR = "7-8"

# 20 minutes at Year 8. Narrative runs a little longer because a story needs a shape;
# a diary entry or a short article can land its point in fewer words.
WORD_BANDS = {
    "narrative": (160, 260),
    "persuasive": (160, 250),
    "speech": (150, 240),
    "article": (150, 240),
    "diary": (150, 240),
}

# Task instructions asking for three deliverables in a 20-minute task. Keyed by topic
# because these ten rows carry no source_book to key on.
RECUT: dict[str, str] = {
    "Health and Wellbeing":
        "Write an informative article for a school magazine explaining why teenagers need "
        "more sleep than adults, and offer two practical changes a student could make this "
        "week. Use the findings in the stimulus to support what you say.",
    "Health and Society":
        "Write an informative article for a general audience explaining what is driving "
        "the rise in youth mental health problems in Australia, and argue for one "
        "specific change schools or governments should make in response. Draw on the "
        "report for evidence.",
    "Environment and Society":
        "Write a persuasive essay arguing for or against the view expressed in the quote. "
        "Support your position with reasoning and one specific example, and deal with the "
        "strongest argument against you.",
}


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
    record = []

    for r in rows:
        lo, hi = WORD_BANDS[r["prompt_type"]]
        recut = RECUT.get(r["topic"])
        changes = {
            "time_limit_minutes": (r["time_limit_minutes"], TIME_LIMIT),
            "target_year": (r["target_year"], TARGET_YEAR),
            "word_count_min": (r["word_count_min"], lo),
            "word_count_max": (r["word_count_max"], hi),
        }
        changed = {k: v for k, v in changes.items() if v[0] != v[1]}
        if recut and recut != r["task_instruction"]:
            changed["task_instruction"] = (r["task_instruction"], recut)
        if not changed:
            print(f"OK      {r['prompt_type']:<11} {r['topic']} — already calibrated")
            continue

        print(f"\nUPDATE  {r['prompt_type']:<11} {r['topic']}")
        for field, (was, now_val) in changed.items():
            if field == "task_instruction":
                print(f"    task re-cut from three deliverables to two:")
                print(f"      was: {' '.join(str(was).split())[:150]}")
                print(f"      now: {' '.join(str(now_val).split())[:150]}")
            else:
                print(f"    {field}: {was} -> {now_val}")
        record.append({"id": r["id"], "topic": r["topic"], "prompt_type": r["prompt_type"],
                       "changes": {k: {"was": v[0], "now": v[1]} for k, v in changed.items()}})

        if args.apply:
            conn.execute(
                "UPDATE writing_prompts SET time_limit_minutes = ?, target_year = ?, "
                "word_count_min = ?, word_count_max = ?, task_instruction = ?, edited = 1 "
                "WHERE id = ?",
                (TIME_LIMIT, TARGET_YEAR, lo, hi, recut or r["task_instruction"], r["id"]),
            )

    if args.apply:
        conn.commit()
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(json.dumps(
            {"generated_from": "tools/repair_vic_writing_calibration.py",
             "applied_at": now, "prompts": record}, indent=2))
        print(f"\nRecalibrated {len(record)} prompts. Record: {MANIFEST}")
    else:
        print(f"\nDry run: {len(record)} prompts would change. Nothing written.")


if __name__ == "__main__":
    main()
