-- db/schema.sql — source of truth

CREATE TABLE IF NOT EXISTS questions (
    id                      TEXT PRIMARY KEY,
    subject                 TEXT NOT NULL CHECK (subject IN (
                                'mathematics','quantitative_reasoning','verbal_reasoning',
                                'logical_reasoning','science_reasoning',
                                'reading_comprehension','writing'
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
    figure_svg              TEXT,
    review_status           TEXT NOT NULL DEFAULT 'pending'
                                CHECK (review_status IN ('pending','approved','rejected')),
    created_at              TEXT NOT NULL,
    reviewed_at             TEXT,
    edited                  INTEGER NOT NULL DEFAULT 0,
    -- Fixed-form delivery (selective_exam_delivery_SPEC.md §6.2). A question belongs to
    -- exactly one form at a time, so columns are enough and a join table is not needed.
    -- form_id carries the exam, so VIC needs no schema change: nsw-drill-ts-007,
    -- nsw-drill-read-012, nsw-mock-003, vic-drill-vr-004.
    form_id                 TEXT,
    form_position           INTEGER,
    form_kind               TEXT CHECK (form_kind IS NULL OR form_kind IN ('drill','mock'))
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
CREATE INDEX IF NOT EXISTS idx_form          ON questions(form_id, form_position);

CREATE TABLE IF NOT EXISTS writing_prompts (
    id                  TEXT PRIMARY KEY,
    prompt_type         TEXT NOT NULL CHECK (prompt_type IN (
                            'narrative','persuasive','scientific_report',
                            'scientific_analysis','article','diary',
                            'email','speech','advice_sheet','news_report'
                        )),
    school_type         TEXT NOT NULL CHECK (school_type IN (
                            'jmss','victorian_selective','nsw_selective','general'
                        )),
    stimulus_type       TEXT NOT NULL CHECK (stimulus_type IN (
                            'text','image','quote','scenario','data'
                        )),
    stimulus_content    TEXT,
    stimulus_image_desc TEXT,
    task_instruction    TEXT NOT NULL,
    word_count_min      INTEGER DEFAULT 300,
    word_count_max      INTEGER DEFAULT 400,
    time_limit_minutes  INTEGER DEFAULT 30,
    target_year         TEXT NOT NULL,
    difficulty          TEXT NOT NULL CHECK (difficulty IN ('medium','hard')),
    topic               TEXT,
    marking_focus       TEXT,
    source_book         TEXT,
    review_status       TEXT NOT NULL DEFAULT 'pending'
                            CHECK (review_status IN ('pending','approved','rejected')),
    created_at          TEXT NOT NULL,
    reviewed_at         TEXT,
    edited              INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_wp_school_type   ON writing_prompts(school_type);
CREATE INDEX IF NOT EXISTS idx_wp_prompt_type   ON writing_prompts(prompt_type);
CREATE INDEX IF NOT EXISTS idx_wp_review_status ON writing_prompts(review_status);
