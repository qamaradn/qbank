-- db/schema.sql — source of truth, mirrors Supabase exactly
-- Apply with: python -c "from db.init import create_tables; create_tables()"

CREATE TABLE IF NOT EXISTS questions (
    id              TEXT PRIMARY KEY,
    subject         TEXT NOT NULL CHECK (subject IN (
                        'quantitative_reasoning','logical_reasoning',
                        'science_reasoning','reading_comprehension','writing'
                    )),
    stem            TEXT NOT NULL,
    option_a        TEXT,
    option_b        TEXT,
    option_c        TEXT,
    option_d        TEXT,
    correct_answer  TEXT CHECK (correct_answer IN ('A','B','C','D')),
    explanation     TEXT,
    writing_prompt  TEXT,
    year_level      TEXT,
    difficulty      TEXT CHECK (difficulty IN ('easy','medium','hard')),
    topic           TEXT,
    has_figure      INTEGER NOT NULL DEFAULT 0,
    figure_path     TEXT,
    confidence      REAL NOT NULL DEFAULT 0.0,
    source_book     TEXT,
    source_page     INTEGER,
    review_status   TEXT NOT NULL DEFAULT 'pending'
                        CHECK (review_status IN ('pending','approved','rejected')),
    created_at      TEXT NOT NULL,
    reviewed_at     TEXT,
    edited          INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS books (
    id              TEXT PRIMARY KEY,
    pdf_filename    TEXT NOT NULL,
    briefing_path   TEXT NOT NULL,
    total_pages     INTEGER,
    relevant_pages  TEXT,
    layout          TEXT CHECK (layout IN ('single_column','double_column','mixed')),
    processed_at    TEXT,
    status          TEXT NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending','processing','complete','failed'))
);

CREATE INDEX IF NOT EXISTS idx_subject       ON questions(subject);
CREATE INDEX IF NOT EXISTS idx_review_status ON questions(review_status);
CREATE INDEX IF NOT EXISTS idx_confidence    ON questions(confidence);
CREATE INDEX IF NOT EXISTS idx_source_book   ON questions(source_book);
