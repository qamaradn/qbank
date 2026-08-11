#!/usr/bin/env python3
"""Adds fixed-form delivery columns to writing_prompts.

WHY WRITING NEEDS FORMS AND WHY IT IS NOT THE SAME AS MCQ FORMS.

A drill is a scaled-down sitting of the real paper. For MCQ that scales cleanly: halve
the question count and halve the time, and the candidate still experiences the same
seconds per question, which is the thing that has to become automatic. Doubling it back
up is a fair prediction of the real sitting.

Writing does not scale that way. The VIC paper sets TWO tasks in 40 minutes -- a short
piece of about 150 words and a longer one of about 250. Serving one of them for 20
minutes is not half of that experience, it is a different experience:

  - budgeting across two tasks is itself the skill. A candidate who spends 28 minutes on
    a piece they are enjoying has failed the paper, and will never discover that by
    practising one piece at a time.
  - the second task is written by a tired writer who has already spent their best ideas.
    That is the task most candidates lose marks on, and a single-prompt drill never
    reaches it.
  - the two tasks are different shapes. At 150 words every "and also" is unaffordable;
    at 250 there is room to develop. A candidate needs to feel the difference.

So a writing drill is a PAIR -- one short prompt and one extended prompt, 40 minutes --
and the pair is the unit that gets dealt, scored and locked. That needs the same three
columns `questions` already carries.

    form_id        e.g. vic-drill-wr-004
    form_position  1 = short task, 2 = extended task
    form_kind      'drill' or 'mock'

Idempotent: checks PRAGMA table_info first, so running it twice is harmless.
"""
import os
import sqlite3
import sys

DB = os.environ.get("DB_PATH", "run_data/db/qbank.db")

ADD = [
    ("form_id", "ALTER TABLE writing_prompts ADD COLUMN form_id TEXT"),
    ("form_position", "ALTER TABLE writing_prompts ADD COLUMN form_position INTEGER"),
    ("form_kind", "ALTER TABLE writing_prompts ADD COLUMN form_kind TEXT "
                  "CHECK (form_kind IS NULL OR form_kind IN ('drill','mock'))"),
]


def main(db=DB):
    conn = sqlite3.connect(db)
    have = {r[1] for r in conn.execute("PRAGMA table_info(writing_prompts)")}
    added = []
    for col, ddl in ADD:
        if col in have:
            continue
        conn.execute(ddl)
        added.append(col)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_wp_form "
                 "ON writing_prompts(form_id, form_position)")
    conn.commit()
    n = conn.execute("SELECT COUNT(*) FROM writing_prompts").fetchone()[0]
    print(f"{db}: added {added or 'nothing (already present)'}; {n} rows intact")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else DB)
