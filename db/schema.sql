-- db/schema.sql — source of truth

CREATE TABLE IF NOT EXISTS questions (
    id                      TEXT PRIMARY KEY,
    subject                 TEXT NOT NULL CHECK (subject IN (
                                'quantitative_reasoning','logical_reasoning',
                                'science_reasoning','reading_comprehension','writing'
                            )),
    stem                    TEXT NOT NULL,
    option_a                TEXT,
    option_b                TEXT,
    option_c                TEXT,
    option_d                TEXT,
    correct_answer          TEXT CHECK (correct_answer IN ('A','B','C','D')),
    explanation             TEXT,
    topic                   TEXT,
    difficulty              TEXT CHECK (difficulty IN ('medium','hard')),
    confidence              REAL NOT NULL DEFAULT 0.0,
    source_book             TEXT,
    source_page             INTEGER,
    source_page_description TEXT,
    passage                 TEXT,
    review_status           TEXT NOT NULL DEFAULT 'pending'
                                CHECK (review_status IN ('pending','approved','rejected')),
    created_at              TEXT NOT NULL,
    reviewed_at             TEXT,
    edited                  INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS books (
    id              TEXT PRIMARY KEY,
    pdf_filename    TEXT NOT NULL,
    briefing_path   TEXT NOT NULL,
    processed_at    TEXT,
    status          TEXT NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending','processing','complete','failed'))
);

CREATE INDEX IF NOT EXISTS idx_subject       ON questions(subject);
CREATE INDEX IF NOT EXISTS idx_review_status ON questions(review_status);
CREATE INDEX IF NOT EXISTS idx_confidence    ON questions(confidence);
CREATE INDEX IF NOT EXISTS idx_source_book   ON questions(source_book);
