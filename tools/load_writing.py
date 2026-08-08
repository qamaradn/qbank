#!/usr/bin/env python3
"""Load one finalised writing-prompt batch into writing_prompts.

Usage:  env -u PYTHONPATH .venv/bin/python3.11 -m tools.load_writing <path-to-batch.json>

The MCQ path goes through phase 4, which dedups against existing stems and drops
near-duplicates SILENTLY. Writing prompts do not go through phase 4 at all, so the dedup
screen lives in wr_finalise and this loader simply refuses to run if any id is already
present — a re-run must be deliberate, not a second copy of everything.
"""
import argparse
import json
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DB = ROOT / "run_data/db/qbank.db"
LOADED = ROOT / "run_data/output/writing/generated/wr_LOADED.json"

COLUMNS = ["id", "prompt_type", "school_type", "stimulus_type", "stimulus_content",
           "stimulus_image_desc", "task_instruction", "word_count_min", "word_count_max",
           "time_limit_minutes", "target_year", "difficulty", "topic", "marking_focus",
           "source_book", "review_status", "created_at"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("batch")
    ap.add_argument("--db", default=str(DB))
    a = ap.parse_args()

    path = pathlib.Path(a.batch)
    prompts = json.loads(path.read_text(encoding="utf-8"))
    con = sqlite3.connect(a.db)

    have = {r[0] for r in con.execute("SELECT id FROM writing_prompts")}
    clash = [p["id"] for p in prompts if p["id"] in have]
    if clash:
        print(f"REFUSING: {len(clash)} id(s) already in writing_prompts — "
              f"this batch looks already loaded")
        sys.exit(1)

    con.executemany(
        f"INSERT INTO writing_prompts ({', '.join(COLUMNS)}) "
        f"VALUES ({', '.join('?' * len(COLUMNS))})",
        [[p[c] for c in COLUMNS] for p in prompts])
    con.commit()

    after = con.execute("SELECT COUNT(*) FROM writing_prompts WHERE school_type='nsw_selective'"
                        ).fetchone()[0]
    print(f"{path.name}: inserted {len(prompts)} prompts")
    print(f"NSW writing prompts now: {after}")

    done = json.loads(LOADED.read_text(encoding="utf-8")) if LOADED.exists() else []
    if path.name not in done:
        done.append(path.name)
        LOADED.write_text(json.dumps(done, indent=1) + "\n", encoding="utf-8")
        print(f"recorded in {LOADED.name}")


if __name__ == "__main__":
    main()
