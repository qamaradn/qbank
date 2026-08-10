#!/usr/bin/env python3
"""Adds the fixed-form delivery columns to an existing database.

db/init.py runs schema.sql, and every CREATE is `IF NOT EXISTS`, so a database that
already holds questions never picks up new columns from it. This adds them in place.

Idempotent: checks PRAGMA table_info first, so running it twice is harmless.
"""
import os
import sqlite3
import sys

DB = os.environ.get("DB_PATH", "run_data/db/qbank.db")

ADD = [
    ("form_id", "ALTER TABLE questions ADD COLUMN form_id TEXT"),
    ("form_position", "ALTER TABLE questions ADD COLUMN form_position INTEGER"),
    ("form_kind", "ALTER TABLE questions ADD COLUMN form_kind TEXT "
                  "CHECK (form_kind IS NULL OR form_kind IN ('drill','mock'))"),
]


def main(db=DB):
    conn = sqlite3.connect(db)
    have = {r[1] for r in conn.execute("PRAGMA table_info(questions)")}
    added = []
    for col, ddl in ADD:
        if col in have:
            continue
        conn.execute(ddl)
        added.append(col)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_form ON questions(form_id, form_position)")
    conn.commit()
    n = conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    print(f"{db}: added {added or 'nothing (already present)'}; {n} rows intact")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else DB)
