# QBANK — CLAUDE CODE MASTER BRIEFING
## Australian Selective School Exam Question Bank Pipeline
---

> **READ THIS ENTIRE FILE BEFORE DOING ANYTHING.**
> This is your complete context for every session.
> Never assume you remember anything from a previous session.
> Never skip straight to coding. Plan first, validate first, code second.

---

## WHAT THIS PROJECT IS

We are building an **Australian selective school exam preparation platform**.

Students in Grades 6–10 use this to prepare for:
- JMSS (John Monash Science School) entry exam
- Victorian selective school exams
- All Australian state competitive selective school exams

The platform serves students a question bank of thousands of MCQ questions.
Students never see the same question twice. Questions are AI-generated from
real exam prep books using a background ETL pipeline that runs on a Linux VM.
This pipeline is NOT user-facing. It runs as a batch job on the VM.

**Solo developer. Claude Code for development. GitHub for version control.**
**Pipeline runs on Linux VM. Review UI accessed from local browser via VM IP.**

---

## INFRASTRUCTURE

```
GitHub (personal account)
    └── repo: qbank
            ├── All pipeline code
            ├── CLAUDE.md + TESTS.md
            ├── db/schema.sql, requirements.txt
            └── NO PDFs, NO generated files, NO API keys, NO data

Linux VM (Ubuntu 22.04+)
    ├── Git clone of qbank repo  ~/qbank/
    ├── Python venv              ~/qbank/.venv/
    ├── /data/pdfs/              ← input PDFs + briefing .md files
    ├── /data/scratch/           ← extracted PNG page images
    ├── /data/output/            ← generated question JSON files
    └── /data/db/                ← SQLite database

Your local machine
    ├── Claude Code              ← all development happens here
    └── Browser → http://<VM_IP>:8000  ← review UI
```

**VM minimum specs:**
- 2 GB RAM (no heavy AI models — just pdf2image + Gemini API)
- 20 GB disk (PDFs + page PNGs accumulate)
- Python 3.11+
- Ubuntu 22.04 or 24.04

**CRITICAL — always use these exact commands on VM:**
- Python: `.venv/bin/python3.11` — NEVER `python` or `python3`
- Git remote: `git@github-personal:qamaradn/qbank.git` — NEVER `git@github.com`
- Git identity: `qamar.adn@gmail.com` — personal, NEVER CSIRO identity
- GEMINI_KEY is set in shell env — there is no `.env` file on the VM

---

## THE 7 SUBJECTS — FIXED. NEVER CHANGE THESE.

| Subject ID | Full Name | Folder Name |
|---|---|---|
| MA | Mathematics | mathematics |
| QR | Quantitative Reasoning | quantitative_reasoning |
| VR | Verbal Reasoning | verbal_reasoning |
| LR | Logical Reasoning | logical_reasoning |
| SR | Science Reasoning | science_reasoning |
| RC | Reading Comprehension | reading_comprehension |
| WR | Writing | writing |

These are the ONLY valid subject values in the entire codebase.
Every database column, folder name, and UI label must use exactly these values.
No exceptions. Do not add an eighth without the owner's explicit instruction.

**MA vs QR — do not merge these.** `mathematics` is curriculum-based maths
(e.g. the Year 7 NSW syllabus: number, algebra, measurement, geometry,
statistics, probability), keyed to a year level. `quantitative_reasoning` is
test-style quantitative questions as they appear in selective exam papers.
They are separate subjects so they can be drilled separately, and because
dedup is subject-scoped, a maths question is never compared against a QR one.

`logical_reasoning` is NOT spare capacity: the Selectly app already maps it to
the NSW selective **Thinking Skills** section (40 questions / 40 minutes). It is
empty only because those questions have not been generated yet.

---

## PDF METADATA BRIEFING FILES — THE MOST IMPORTANT INPUT

Before the pipeline runs on any PDF, a human-written `.md` briefing file MUST
exist. This tells the pipeline which pages to extract and what subject each page
range covers. There is NO automatic subject classification — the briefing is the
sole source of truth.

### Why it matters

- Without it: pipeline refuses to run.
- With it: every page gets the correct subject label before Gemini ever sees it.
  Gemini is told "this is a science reasoning page" and generates accordingly.

### Naming convention — same name as PDF, .md extension

```
/data/pdfs/
    rs_aggarwal_reasoning.pdf
    rs_aggarwal_reasoning.md        ← briefing file
    10_ACT_Practice_Tests.pdf
    10_ACT_Practice_Tests.md
```

### Briefing file format — MINIMAL. Only these fields.

```markdown
# PDF BRIEFING: <book_title>

## Basic Info
- **file:** <pdf_filename>.pdf
- **relevant_pages:** <start>–<end>
- **target_year:** 9–10
- **difficulty:** medium

## Subject Coverage
- **pages 45–54:** quantitative_reasoning
- **pages 55–60:** reading_comprehension
- **pages 61–74:** science_reasoning
- **pages 75–80:** verbal_reasoning
- **pages 81–90:** skip
```

**Valid subject IDs for Subject Coverage:**
`mathematics` | `quantitative_reasoning` | `verbal_reasoning` |
`logical_reasoning` | `science_reasoning` | `reading_comprehension` |
`writing` | `skip`

**`skip` means:** cover pages, answer keys, indexes, ads, worked examples —
anything Gemini should NOT generate questions from.

### Real example — run_data/pdfs/act_test1.md

```markdown
# PDF BRIEFING: ACT Practice Test 1 (Math + Reading + Science)

## Basic Info
- **file:** 10_ACT_Practice_Tests.pdf
- **relevant_pages:** 45–74
- **target_year:** 11–12
- **difficulty:** hard

## Subject Coverage
- **pages 45–54:** quantitative_reasoning
- **pages 55–60:** reading_comprehension
- **pages 61–74:** science_reasoning
```

### Pipeline refuses to run without briefing file

`run_book.py` checks for the briefing file before doing anything. If it is
missing it raises `FileNotFoundError` with a clear message pointing here.

---

## PIPELINE ARCHITECTURE — 4 PHASES

```
/data/pdfs/<book_id>.pdf  +  /data/pdfs/<book_id>.md  (briefing)
    │
    ▼  run_book.py orchestrates all phases
    │
PHASE 1 — PDF → PNG (pdf2image, no AI)
├── Reads briefing: relevant_pages, subject_coverage
├── Extracts each relevant page as a PNG at 150 DPI
├── Skips pages outside relevant_pages range
├── Skips pages whose subject is "skip"
└── Output per page:
    /data/scratch/<book_id>/images/<subject>/<book_id>_<DDMMYY>_p<n>.png
    │
    ▼
PHASE 2 — BRIEFING → PAGE MAP (no AI, no API)
├── Reads briefing subject_coverage ranges
├── Builds page_map.json: [{page_number, subject}] for all relevant pages
├── No Claude, no Gemini — pure briefing lookup
└── Output: /data/scratch/<book_id>/page_map.json
    │
    ▼  *** HUMAN CHECKPOINT — review page_map.json if needed ***
    │
PHASE 3 — GENERATE QUESTIONS (Gemini Vision API)
├── Reads briefing: target_year, difficulty → injected into prompt
├── For each page PNG: sends image + subject label to Gemini
├── PASSAGE SUBJECTS (science_reasoning, reading_comprehension):
│   Gemini invents a new scenario/passage FIRST, then generates
│   10 questions that reference it — questions cite "the passage",
│   "Study 1", "Study 2", etc.
├── STANDALONE SUBJECTS (quantitative_reasoning, verbal_reasoning):
│   Gemini generates 10 standalone MCQs inspired by the page style
├── Resumable: skips pages whose output JSON already exists
├── API_DELAY_SECONDS between calls
└── Output: /data/output/<subject>/generated/<book_id>_p<n>.json
    │
    ▼
PHASE 4 — DEDUP + LOAD INTO DB (no AI)
├── Scans output/*/generated/<book_id>_p*.json
├── For each question: SequenceMatcher dedup against existing stems
│   (threshold 0.85, subject-scoped — no cross-subject dedup)
├── Inserts non-duplicate questions as review_status='pending'
├── Confidence score stored for display only — NOT used for auto-approval
└── ALL questions go to human review regardless of confidence
    │
    ▼
HUMAN REVIEW UI
├── FastAPI server: uvicorn review.server:app --host 0.0.0.0 --port 8000
├── Access: http://<VM_IP>:8000
├── Keyboard: A=Approve  R=Reject  E=Edit  ←→=Navigate
├── Passage shown above question for SR and RC questions
├── Confidence shown as triage signal (high/low) — reviewer decides
└── Approved → SQLite at /data/db/qbank.db
```

---

## QUESTION JSON SCHEMA

```json
{
  "id": "uuid-v4",
  "subject": "science_reasoning",
  "stem": "According to Study 2, at which temperature did the reaction rate peak?",
  "option_a": "20°C",
  "option_b": "30°C",
  "option_c": "40°C",
  "option_d": "50°C",
  "correct_answer": "C",
  "explanation": "Study 2 shows reaction rate peaked at 40°C with a value of 0.82 mol/s.",
  "topic": "Chemical Reactions",
  "difficulty": "medium",
  "confidence": 0.95,
  "source_book": "act_test1",
  "source_page": 63,
  "source_page_description": "A page showing an experiment on enzyme activity at varying temperatures.",
  "passage": "Researchers at CSIRO in Melbourne investigated enzyme activity...\n\nStudy 1: ...\nStudy 2: ...",
  "review_status": "pending",
  "created_at": "2026-05-22T10:30:00Z",
  "reviewed_at": null,
  "edited": false
}
```

**Strict rules:**
- `subject` → exactly one of 5 valid IDs
- `correct_answer` → exactly "A", "B", "C", or "D"
- `difficulty` → exactly "medium" or "hard" — no "easy"
- `confidence` → float 0.0–1.0 (display-only triage signal)
- `review_status` → "pending" | "approved" | "rejected"
- `passage` → populated for science_reasoning and reading_comprehension; null for others
- `source_page_description` → Gemini's one-sentence description of the PDF page it saw

---

## DATABASE SCHEMA

```sql
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
```

---

## PROJECT FOLDER STRUCTURE

```
qbank/                               ← GitHub repo root
├── CLAUDE.md                        ← READ EVERY SESSION
├── TESTS.md                         ← READ BEFORE ANY CODING
├── .gitignore
├── requirements.txt
├── .env.example                     ← committed (no real values)
├── pytest.ini
│
├── pipeline/
│   ├── __init__.py
│   ├── briefing.py                  ← parses PDF .md briefing files
│   ├── phase1_normalise.py          ← PDF → PNG via pdf2image
│   ├── phase2_classify.py           ← briefing → page_map.json
│   ├── phase3_generate.py           ← PNG + subject → Gemini → MCQs
│   ├── phase4_load.py               ← dedup + insert into SQLite
│   └── run_book.py                  ← orchestrates phases 1–4
│
├── review/
│   ├── server.py                    ← FastAPI, binds 0.0.0.0:8000
│   └── ui/
│       └── index.html               ← single-file review UI (dark dashboard)
│
├── db/
│   ├── __init__.py
│   ├── init.py                      ← create_tables() helper
│   └── schema.sql                   ← source of truth (structure only)
│
├── tests/
│   ├── __init__.py
│   ├── test_briefing.py
│   ├── test_phase1_normalise.py     ← (if exists)
│   ├── test_phase2_classify.py
│   ├── test_phase3_generate.py
│   ├── test_phase4_load.py
│   ├── test_review_api.py
│   ├── test_review_ui.py
│   └── test_run_book.py
│
└── run_data/                        ← VM runtime data (gitignored)
    ├── pdfs/                        ← PDFs + briefing .md files
    ├── scratch/                     ← extracted PNGs per book
    ├── output/                      ← generated question JSONs
    └── db/                          ← SQLite database
```

---

## GITIGNORE

```gitignore
# Secrets
.env
*.env

# Python
__pycache__/
*.py[cod]
*.egg-info/
.venv/
venv/
dist/
build/

# All data — never commit
/data/
/run_data/
*.pdf
*.db
*.sqlite3

# Pipeline working files
/scratch/
/output/

# OS / IDE
.DS_Store
Thumbs.db
.vscode/
.idea/
```

---

## ENVIRONMENT VARIABLES

```bash
# .env.example — commit this, placeholder values only
# On VM: GEMINI_KEY is set in shell environment, not in a file

GEMINI_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash

ANTHROPIC_API_KEY=your_anthropic_api_key_here

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
SUPABASE_STORAGE_BUCKET=figures

SCRATCH_DIR=/data/scratch
OUTPUT_DIR=/data/output
DB_PATH=/data/db/qbank.db

QUESTIONS_PER_PAGE=10
API_DELAY_SECONDS=2
DEDUP_THRESHOLD=0.85

REVIEW_HOST=0.0.0.0
REVIEW_PORT=8000
```

---

## GEMINI GENERATION PROMPTS

### Passage subjects (science_reasoning, reading_comprehension)

Gemini receives the page PNG + this instruction:

```
You are an expert Australian curriculum exam question writer for selective school entry.

The subject of this page is: <subject_name>.

STEP 1 — INVENT A NEW SCENARIO (science) / WRITE A NEW PASSAGE (reading):
  [Science] Create a brand-new experiment scenario with 2-3 named Studies,
  specific data, Australian context (CSIRO, Australian locations, species).
  [Reading] Write a 250–300 word passage: Australian setting, clear topic,
  vocabulary appropriate for Year <year_level>.

STEP 2 — GENERATE 10 QUESTIONS about your scenario/passage.
  Every question stem must reference the passage
  (e.g. "According to Study 2...", "The author suggests...").

DIFFICULTY: 8 medium, 2 hard.
AUSTRALIAN CONTEXT mandatory throughout.

Return ONLY a valid JSON object:
{
  "passage": "...(full passage/scenario)...",
  "questions": [
    {
      "stem": "...",
      "option_a": "...", "option_b": "...", "option_c": "...", "option_d": "...",
      "correct_answer": "A|B|C|D",
      "explanation": "...",
      "topic": "...",
      "difficulty": "medium|hard",
      "confidence": 0.95,
      "source_page_description": "one sentence describing the PDF page"
    }
  ]
}
```

### Standalone subjects (quantitative_reasoning, verbal_reasoning)

```
You are an expert Australian curriculum exam question writer for selective school entry.

The subject of this page is: <subject_name>.

Generate exactly 10 NEW multiple-choice questions inspired by this page.
Do NOT copy or closely paraphrase any question visible on the page.

DIFFICULTY: 8 medium, 2 hard.
AUSTRALIAN CONTEXT mandatory.

Return ONLY a valid JSON object:
{
  "passage": null,
  "questions": [...]
}
```

---

## KNOWN EDGE CASES — HANDLE EXPLICITLY

1. **Pages marked `skip` in briefing** — Phase 1 never extracts them; Phase 3 never generates from them
2. **Gemini returns array instead of object** — `_call_gemini` handles gracefully: `if isinstance(result, list): return {"passage": None, "questions": result}`
3. **Gemini wraps JSON in markdown fences** — `_strip_fences()` strips ` ```json ` or ` ``` ` wrappers
4. **Near-duplicate questions** — `_is_duplicate()` at Phase 4 with 0.85 threshold, subject-scoped
5. **All qualities go to review** — confidence is display-only; never auto-approve
6. **Multiple books, same subject** — dedup is always subject-scoped, cross-book collisions caught
7. **Pages outside relevant_pages range** — Phase 1 skips them entirely
8. **Resumable pipeline** — Phase 3 skips pages whose output JSON already exists

---

## VM FIRST-TIME SETUP

```bash
# On the Linux VM

# 1. System packages
sudo apt update && sudo apt install -y python3.11 python3.11-venv git curl poppler-utils

# 2. Clone repo
git clone git@github-personal:qamaradn/qbank.git ~/qbank
cd ~/qbank

# 3. Virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# 4. Install dependencies
.venv/bin/python3.11 -m pip install -r requirements.txt

# 5. Create data directories (VM-only, not in repo)
sudo mkdir -p /data/pdfs /data/scratch /data/output /data/db
sudo chown -R $USER:$USER /data

# 6. Set GEMINI_KEY in shell (add to ~/.bashrc)
export GEMINI_KEY=your_key_here

# 7. Initialise database
.venv/bin/python3.11 -c "from db.init import create_tables; create_tables()"

# 8. Verify
.venv/bin/python3.11 -c "from pdf2image import convert_from_path; print('pdf2image OK')"
pytest tests/ -v
```

---

## DAILY WORKFLOW

```bash
# Pull latest code
cd ~/qbank && git pull && source .venv/bin/activate

# Add new book
cp /path/to/book.pdf /data/pdfs/<book_id>.pdf
nano /data/pdfs/<book_id>.md        # write briefing using template above

# Run full pipeline
.venv/bin/python3.11 -m pipeline.run_book --book_id <book_id> \
  --pdf /data/pdfs/<book_id>.pdf --briefing /data/pdfs/<book_id>.md

# Test on specific pages only (skips Phase 1 + 2 if PNGs + page_map exist)
.venv/bin/python3.11 -m pipeline.run_book --book_id <book_id> \
  --pdf /data/pdfs/<book_id>.pdf --briefing /data/pdfs/<book_id>.md \
  --test-pages 61 62

# Check status
.venv/bin/python3.11 -m pipeline.run_book --book_id <book_id> --status

# Start review server
nohup uvicorn review.server:app --host 0.0.0.0 --port 8000 &

# Access review UI from local machine
# Browser → http://<VM_IP>:8000

# Tests
pytest tests/ -v
pytest tests/test_phase3_generate.py -v
```

---

## GIT WORKFLOW

```bash
# Never commit directly to main — one branch per feature

git checkout -b feature/<name>
# ... build, test ...
git add pipeline/phase3_generate.py tests/test_phase3_generate.py
git commit -m "phase3: passage-first generation, all 8 tests passing"
git push git@github-personal:qamaradn/qbank.git feature/<name>

# When complete and all tests green
git checkout main
git merge feature/<name>
git push git@github-personal:qamaradn/qbank.git main
```

---

## DEVELOPMENT RULES

1. Read TESTS.md before writing any code
2. Briefing file must exist — `run_book.py` enforces this, no exceptions
3. Never auto-approve questions — humans only set `approved`
4. `API_DELAY_SECONDS` between every Gemini API call — no tight loops
5. Every phase is resumable — skip already-processed pages
6. Validate every LLM JSON response before writing to disk
7. Commit only when all tests for that phase are green
8. Never commit to main directly — feature branches only
9. Never commit `.env` or any API key — ever
10. Use `.venv/bin/python3.11` on VM, never bare `python` or `python3`

---

## QUICK REFERENCE

```bash
# Pipeline — full run
.venv/bin/python3.11 -m pipeline.run_book \
  --book_id <id> --pdf /data/pdfs/<id>.pdf --briefing /data/pdfs/<id>.md

# Pipeline — test pages only
.venv/bin/python3.11 -m pipeline.run_book \
  --book_id <id> --pdf /data/pdfs/<id>.pdf --briefing /data/pdfs/<id>.md \
  --test-pages 61 62 63

# Status check
.venv/bin/python3.11 -m pipeline.run_book --book_id <id> --status

# Review server
uvicorn review.server:app --host 0.0.0.0 --port 8000

# Tests
pytest tests/ -v
pytest tests/test_phase3_generate.py -v
pytest tests/test_review_api.py -v

# DB — count questions
sqlite3 /data/db/qbank.db "SELECT subject, review_status, COUNT(*) FROM questions GROUP BY 1,2;"
```

---

## WRITING PROMPTS — PLANNED FEATURE (not yet built)

Australian selective schools test writing differently — this needs a separate
`writing_prompts` table and a Claude-powered generator (not Gemini).

### School types and what they test

| School | Prompt types | Stimulus |
|---|---|---|
| JMSS | scientific_report, scientific_analysis | data tables, graphs, experiment descriptions |
| Victorian selective | narrative, persuasive | quote, image, open topic |
| NSW selective (ASAT) | narrative, persuasive, article, diary, email, speech, advice_sheet, news_report | image, quote, scenario, or combination |

### JSON schema (what Claude generates per prompt)

```json
{
  "id": "uuid-v4",
  "prompt_type": "narrative|persuasive|scientific_report|scientific_analysis|article|diary|email|speech|advice_sheet|news_report",
  "school_type": "jmss|victorian_selective|nsw_selective|general",
  "stimulus_type": "text|image|quote|scenario|data",
  "stimulus_content": "Full text of the scenario, quote, or data table (plain text)",
  "stimulus_image_desc": null,
  "task_instruction": "The actual writing task sentence the student reads",
  "word_count_min": 300,
  "word_count_max": 400,
  "time_limit_minutes": 30,
  "target_year": "9-10",
  "difficulty": "medium",
  "topic": "Environment",
  "marking_focus": ["ideas", "structure", "language", "voice"],
  "review_status": "pending",
  "created_at": "2026-05-23T..."
}
```

### DB table to add to db/schema.sql

```sql
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
```

### Steps to implement when ready

1. ~~Add table above to `db/schema.sql`~~ ✅ DONE
2. ~~Update `db/init.py` → `create_tables()` to create it~~ ✅ DONE (init.py reads schema.sql)
3. ~~Run `create_tables()` on VM to add table to live DB~~ ✅ DONE
4. ~~Add writing_prompts endpoints to `review/server.py`~~ ✅ DONE
   - `GET /writing-prompts?status=&school_type=`
   - `POST /writing-prompts/{id}/approve`
   - `POST /writing-prompts/{id}/reject`
   - `GET /stats/writing`
5. ~~Extend review UI to handle writing prompts~~ ✅ DONE
   - "Writing" tab in header — switches sidebar to school_type filter
   - `renderWritingPrompt()` shows: tags + stimulus box (yellow accent) + task box (blue accent) + meta
   - A/R keyboard shortcuts work; E (edit) disabled in writing mode
6. Add `stimulus_image_path` column to `writing_prompts` table — for graph/photo prompts
   - Store image files in `run_data/writing_prompts/figures/`
   - FastAPI mounts that dir as static files at `/wp-figures/`
   - UI renders image above stimulus text when field is populated
   - `stimulus_content` still used for caption alongside image
   - Steps: ALTER TABLE + StaticFiles mount in server.py + 10 lines in renderWritingPrompt()
7. Write `writing/insert_prompts.py` — loads a JSON array file → bulk inserts into writing_prompts
8. Write `writing/generate_prompts.py` — uses Claude API (Anthropic), not Gemini
   - Takes `school_type`, `prompt_type`, `count` as args
   - Returns list of JSON objects matching schema above
   - Australian context mandatory throughout
   - JMSS: include real-ish data tables in stimulus_content (enzymes, ecosystems, physics)
   - NSW: vary stimulus_type across a batch (don't do all scenarios)
   - For image prompts: set stimulus_type='image', populate stimulus_image_desc, leave stimulus_image_path null (human adds image file manually)

### Notes
- This is NOT MCQ — students write 300–400 words. No correct_answer field.
- marking_focus stored as JSON array string (SQLite has no array type)
- 30 prompts already in DB: 10 JMSS, 10 NSW, 10 Victorian — all pending review
- Images live in run_data/ (gitignored) — migrate to Supabase URLs later
- Claude (Anthropic API) preferred over Gemini for writing prompt generation
  — better narrative creativity and Australian curriculum alignment

---

## PROGRESS CHECKLIST (update each session)

- [x] GitHub repo created and cloned to VM
- [x] VM setup complete (venv, /data dirs, GEMINI_KEY in shell)
- [x] Project folder structure created
- [x] .gitignore committed
- [x] requirements.txt committed
- [x] .env.example committed
- [x] db/schema.sql committed and DB initialised on VM
- [x] briefing.py parser written and tested (7 tests)
- [x] phase1_normalise.py written and tested (pdf2image PNG extraction)
- [x] phase2_classify.py written and tested (briefing → page_map, 3 tests)
- [x] phase3_generate.py written and tested (Gemini Vision, passage-first, 8 tests)
- [x] phase4_load.py written and tested (dedup + DB load, 6 tests)
- [x] run_book.py orchestrator written and tested (phases 1–4)
- [x] review/server.py written and tested (approve/reject/edit/stats, 14 tests)
- [x] review/ui/index.html built (dark dashboard, keyboard A/R/E/←→, passage display)
- [x] All tests passing (61 tests)
- [x] ACT Science page 61 processed end-to-end — passage-based questions confirmed working
- [x] act_test1 + act_test2 fully generated (RC+SR, QR skipped for flash-lite)
- [x] act_test3, act_test4, act_test5 running in background (RC+SR only)
- [x] mathematics subject added (7 subjects) — year7_nsw_maths 532 Qs, 50 SVG figures
- [x] logical_reasoning built 0 -> 300/300 (2026-08-04), 34 SVG figures, per-question confidence
- [x] Move LR tooling out of gitignored run_data/ into tools/ and commit (2026-08-04)
- [ ] Human review of 299 pending logical_reasoning questions
- [x] VIC verbal_reasoning: 183 new questions built and loaded (2026-08-04), all pending
- [x] VIC verbal_reasoning top-up COMPLETE — 341 items authored 2026-08-11
      (vr_vic_acer p10-p20): vocabulary 186, antonyms 60, sentence completion 60,
      shades of meaning 35. Book now 522, keys 25.1/24.9/25.1/24.9, all pending.
      sentence_completion is a new category in vr_plan.json and vr_finalise
- [x] VIC verbal_reasoning key skew REPAIRED 2026-08-11 — repair_key_skew --scope verbal,
      980 of 1021 reordered across the four Gemini books. §7.1 rated verbal "mild" from the
      SUBJECT average, which hid it: the books skew in opposite directions
      (external_vr_300526 43% A against direct_ve_290526 43% B) and cancelled out. Every
      book now within a point of 25/25/25/25. Manifest: key_skew_verbal_manifest.json
- [ ] VIC verbal_reasoning: exclude the off-target §6 questions (blocked — see item 1)
- [x] NSW reading_comprehension vocabulary cloze — 120 questions, 15 passages (2026-08-04)
- [x] Selectly: `mathematics` in schools.ts union — already done, mapped to nsw-shspt
      "Mathematical Reasoning" (verified 2026-08-04)
- [ ] Selectly: make pushed questions addressable (send qbank uuid as the row id) — see
      CURRENT STATUS item 1; blocks the VR exclusion and every future correction
- [x] NSW Thinking Skills built 300 -> 956/880, every named subcategory at target (2026-08-10)
- [x] NSW Reading 649/649, Mathematical Reasoning 839/838, Writing 42 prompts
- [x] Fixed-form delivery: form_id/form_position/form_kind in schema.sql,
      db/migrations/001_form_columns.py applied, tools/assign_forms.py deals 117 NSW
      drill forms (2026-08-10)
- [x] VIC reading reuse verified by reading 40 questions (2026-08-10) — retrieval-led,
      67.5%; the 718 are kept but the authoring gap grows from ~24 to ~300-360
- [x] Answer-key skew repaired across 2,913 VIC-scope questions (2026-08-10) —
      tools/repair_key_skew.py, 2,734 reordered, 45 blocked as defective
- [ ] VIC reading: the ~233 ACT questions counted as inference-led rest on a hand-read
      of 40 (67.5% retrieval, 95% CI 53-82%). ACCEPTED AS-IS 2026-08-11 — top up after
      launch if the mix proves wrong. The 395 authored items are not affected: they are
      inference by construction and every key passed key_restates_passage
- [x] Reading length tell REPAIRED (2026-08-11) — tools/repair_length_tell.py, 153
      hand-written distractor extensions; "pick the longest" 48.7% -> 29.3%
- [x] Triaged the 45 questions repair_key_skew blocked (2026-08-11) —
      tools/triage_blocked.py: 39 rejected (7 were live), 4 verified and cleaned,
      2 were false positives. Record in run_data/output/blocked_triage.json
- [x] `pdfs/vic_reading_TASK.md` written (2026-08-10) — text-type split agreed
      (informational 50 / narrative 25 / persuasive 15 / poetry 10), 394 items to author
- [x] VIC reading informational top-up COMPLETE — 84/84 inference items on 28 existing
      ACT passages (rc_vic_inference p1-p5, 2026-08-10), keys 21/21/21/21, confidence
      authored per item 0.85-0.95 rather than a flat constant
- [x] VIC reading poetry COMPLETE — 74/74 over 12 new poems (rc_vic_poetry p1-p3,
      2026-08-10), keys 19/18/19/18, confidence 0.87-0.93
- [x] VIC reading narrative COMPLETE — 156/156 over 26 authored passages
      (rc_vic_narrative p1-p5, 2026-08-10), keys 39/39/39/39
- [x] VIC READING COMPLETE — 395 items authored across all four text types
      (2026-08-10): informational top-up 84 on existing ACT passages, poetry 74 over
      12 new poems, narrative 156 over 26, persuasive 81 over 14. All pending review;
      every prose key under the 0.35 restatement limit; confidence authored per item
      0.85-0.95 rather than a flat constant. 80 new passages written.
- [x] VIC maths Statistics & Probability COMPLETE — 100/100 (ma_vic_stats p1-p5,
      2026-08-11). Six categories all at target, keys 25/25/25/25, 34 figures, all
      pending. Strand share across the VIC maths pool rises 10.5% -> 24.5% against a
      15-25% target. MA_BOOK env var switches ma_common and ma_finalise to a non-NSW book
- [x] QR beyond-Year-8 filter RESOLVED 2026-08-12 — 98, not the 188 §3.3 estimated. All
      231 keyword candidates read; 133 are in scope. tools/qr_beyond_year8.py holds one
      human verdict per question and push_to_selectly honours the manifest (4,194 -> 4,120
      sendable). Trig and counting are in scope per §3.1; only unavoidable quadratic
      solving, logs, calculus, conics and normal distribution go
- [x] 17 quantitative questions with corrupt explanations repaired 2026-08-12 —
      tools/repair_broken_working.py: 10 rejected (no correct answer), 5 re-keyed, 2
      explanations cleaned. Found by READING, not by a sweep; the August pattern missed
      them. question_checks gained `rewrites_the_question` — the model editing the
      question inside the explanation, which always means the stored item is unanswerable
- [x] VIC writing COMPLETE 2026-08-12 — 54/54 in 27 paired drill forms. Two-task format
      confirmed from ACER's own page (§6 was "Confidence: Low"). The two tasks are
      DIFFERENT SIZES (owner, first-hand): short ~150 words / 15 min and extended ~250 /
      25 min, and a writing drill serves the PAIR because writing is the one component
      that does not survive halving — budgeting across two tasks is the skill. 11 tasks
      re-cut when the band moved. writing_prompts gained form columns (migration 002);
      tools/assign_writing_forms.py deals 27 forms of exactly 40 minutes.
      WR_BOOK=wr_vic_acer selects the VIC profile and enforces the two bands
- [ ] QR pages rerun with GEMINI_MODEL=gemini-2.5-flash (full model, no thinking)
- [ ] writing_prompts table + generator implemented (see WRITING PROMPTS section above)
- [ ] First batch synced to Supabase

---

## CURRENT STATUS

**Last worked on:** 2026-08-12 (second session)

**VIC AUTHORING IS COMPLETE.** Reading 395, verbal 341, maths Statistics 100, writing 44
— 880 items across four components, every one `pending`. `vic_content_taxonomy_TASK.md`
§7 has nothing left in its authoring column. What remains for VIC is human review and the
Selectly reload, neither of which is authoring.

**DB totals:** 9,315 questions — QR 2,240, RC 1,763, VR 1,552, MA 1,482, SR 1,322,
LR 956. 5,306 approved, 3,896 pending, 113 rejected. Writing prompts 106 — NSW 42,
VIC 54, JMSS 10.

**The review queue is the gate, not authoring.** 3,896 pending. Drill serves only the
approved bank (SPEC §5.1), so none of the 880 VIC items or the 954 Thinking Skills items
reaches a student until someone clicks through them.

**CLEAN RELOAD DECIDED 2026-08-12.** No students are onboarded — only a reviewer
(fouijnu@) and admin (qamar.adn@) account, and every question is being re-reviewed after
the reload — so Selectly's `questions` and `question_flags` tables will be wiped and
reloaded rather than backfilled. `pipeline/backfill_qbank_ids.py` is no longer the plan.
This resolves the 3,133 divergent rows, the 7 rejected-but-live rows, the 158 §6 verbal
types and the form assignments in one step. The migration and deploy are still required —
the wipe removes the backfill, not the addressability. Plan: `pdfs/selectly_implementation_HANDOVER.md` §1.1 and §6.

`push_to_selectly.py` is ready: `schoolIds` now routes per question from Selectly's
schools.ts (it was hardcoded to both exams — vic-seal has no mathematics section), §6
banned types are excluded, form fields ride along. Of 5,306 approved, **4,194 are
sendable**: 156 §6 verbal and 956 science_reasoning (no exam section maps to it) are held
back. Only 531 carry a form, so deal the rest before reloading.

**Selectly blockers remaining — ALL FOUR ARE SELECTLY-SIDE AND NEED THE OWNER.** Nothing
on the qbank side blocks them. They change production, so they were not done unasked:
merge `feature/qbank-id-addressability` (commit `c52ffa9`, local only, working tree clean),
apply `supabase/migrations/0001_add_questions_qbank_id.sql`, add
`formId`/`formPosition`/`formKind` to the `questions` table AND the import zod schema
(they are being sent now and silently stripped), then wipe and reload per §1.1.

**VIC LAUNCH FORMS 1-20 ARE BLIND-VERIFIED (2026-08-13).** 1,305 questions solved with
the key withheld and the options shuffled, across `vic-drill-mq-001..020` and
`vic-drill-rv-001..020`. Every one of the 40 forms is at full size and none holds a
rejected or withheld question — a question pulled is a question authored back the same
day, at the same archetype and level.

| Forms | Solved | Defects | Rate |
|---|---:|---:|---:|
| `vic-drill-mq-001..020` | 619 | 32 | 5.2% |
| `vic-drill-rv-001..020` | 686 | 3 | 0.4% |
| NSW sample (hand-authored) | 87 | 0 | 0.0% |

The `rv` half has now run 561 questions clean since its single repair, and the maths half
holds steady near 5%. Twenty forms is enough to call the gap structural rather than
sampling noise.

**Forms 16-20 turned up a defect class the earlier forms never surfaced: options that read
differently and ARE the same answer.** `options_distinct_by_value` in `question_checks`
parses each option as a number, a bare fraction, a whole-root surd or an "N out of M"
probability and compares VALUES; `options_distinct` had only ever compared text, so it
could not see `4/13` beside `16/52`, `2√25` beside `10`, or `1 out of 4` beside `6 out of
24`. Swept over the served bank it found 29, of which 6 are exempt because they ask for
lowest terms — there the unreduced equivalent is the skill being tested. Of the 23 real
ones, 7 had two correct answers and one (`nsw-drill-math-035`) had all THREE distractors
equal to 1/2, so the key fell out by elimination with no arithmetic at all. Root cause is
closed: `ma_common.Q` compares option values now, not just their text.

`one_point_on_the_line` covers the same fault where the options are not equal but are
equally correct — "which point lies on y = 2x − 3?" offering both (2, 1) and (1, −1).

**A second class: questions orphaned from the thing they refer to.** Reading and maths
items were authored as SETS against one chart or scenario, question one introducing it and
the rest opening "Using the same chart...". `assign_forms` deals each question
independently, so the opener and its followers land in different papers. Six had no figure
of their own and were unanswerable — a tin of tokens, a bag of counters, a spinner wheel,
two number machines, a line of square tables whose opener does not exist anywhere in the
bank. `tools/repair_orphaned_references.py` restates those and repoints 45 more that do
carry their figure. **Anything authored as a set from now on must be self-contained per
question, because the dealer will separate it.**

Reading and Verbal came back nine times cleaner than Maths and Quantitative on the same
source books, and the gap held across ten forms. It is what the questions ask, not who
wrote them: a wrong key in a reading question is visible on the page, while a wrong key in
a maths question hides behind arithmetic that reads fluently and behind a figure nobody
rendered. **Almost every mq defect was a figure disagreeing with its own explanation and
key** — bars read on the wrong scale, a shaded block drawn twice its stated height, a stem
labelling a rectangle differently from the figure beside it, a right angle marked on the
very vertex the stem asked about. None is detectable without reading the SVG coordinates.

The five rv defects across 307 questions were of a different kind entirely: one
second-correct-answer in a hand-authored sentence completion, and four soft judgement
questions where the key was the better reading rather than the only one. Expect the
ACT-sourced inference items to keep producing those; they are recorded as `keep` so they
are not re-adjudicated.

**A DEFECT CLASS NO CHECK CAN SEE: DUPLICATE OPTION *VALUES*.** A tan question offered
6/4, 2/3, 3/2 and 4/6 — but 4/6 IS 2/3 and 6/4 IS 3/2, so it had two correct answers and
two identical wrong ones. `options_distinct` compares option TEXT and passes it cleanly.
Any question whose options are fractions or unsimplified ratios could carry the same
fault, and a sweep that evaluates option values would be cheap.

**REJECTION LEAVES A HOLE, SO REPLACE RATHER THAN SHRINK.** 17 questions were authored
back into the forms that lost one (`tools/qr/qr_replacements_build.py`), keeping all 87
mq forms at the dealer's original 81x31 + 6x30. Every replacement key is computed twice by
different routes and the build fails if they disagree; that check caught two of my own
errors. Note the replacements are NOT blind-verified — I wrote them, so solving them is
circular. They have the double-route check, the full sweep and a rendered look, which is
the bar NSW cleared, but genuine independence needs a different reader.

**A MIS-BRIEFED PAGE, NOT SCATTERED ERRORS.** `act_test10` page 816 is a reading passage
on the Lincoln-Douglas debates that the briefing declared quantitative_reasoning, so all
10 questions generated from it are US civics analogies filed under the wrong subject. The
briefing is corrected and all 10 withheld. Worth checking other briefings for the same
off-by-one at a section boundary.

**FORMS ARE COMPLETE FOR BOTH EXAMS (2026-08-12).** Every servable question carries one.

| Form prefix | Forms | Items | Per form | Timer |
|---|---:|---:|---:|---:|
| `nsw-drill-re/ma/ts-*` | 117 | 2,441 | 19-26 | 20-31 min |
| `vic-drill-mq-*` | 87 | 2,691 | 30-31 | 29-30 min |
| `vic-drill-rv-*` | 66 | 2,499 | 37-38 | 27-28 min |
| `vic-drill-wr-*` | 27 | 54 prompts | 2 | 40 min |

VIC forms are half the real paper at the real paper's pace, as NSW's are. **VIC Reading
and Verbal are ONE section in the 2026 paper, so `vic-drill-rv-*` forms MIX them** —
15-18 reading (whole passages, never split) plus 20-22 verbal. A category-based selector
cannot serve those; Selectly must fetch by `form_id`.

**Within-passage key clumping — ACCEPTED AS-IS 2026-08-12 (owner).** In `vic-drill-rv-*`
forms the worst answer letter averages 29.7% per form against a 33.6% random baseline, so
the deal is working — but reading questions enter a form as a WHOLE PASSAGE, placed by
slot count and source book with no key or topic term, and within a single passage the
worst letter averages 44% across all 190 passages. The bank-wide key repair balanced
letters across the subject, not inside each passage's 5-8 questions. Worst single form is
39.5%. Fix if it ever matters: rebalance keys within each passage group (a repair on the
questions, touching 190 passages), or add a key term to passage placement. Not urgent.

**GROWING THE BANK LATER — read this before adding questions.** `assign_forms.py` refuses
to re-deal a question that already carries a `form_id`, and `--force` overrides it. That
override is **pre-launch only**: once a student has sat a form, changing its membership
re-bases every score recorded against it. After launch, new questions go into NEW forms
(continue the numbering) rather than being dealt into existing ones, and a bad question is
retired with Selectly's `questions.active`, leaving form membership untouched.

**Routing bug fixed 2026-08-12:** `mathematics` was mapped wholesale to `nsw-shspt`,
sending 642 Year 9 VIC questions (`year9_maths`, `ma_vic_stats`) into a Year 6 paper and
leaving vic-seal's maths empty. It now routes per source book like reading does; an
unknown maths book goes nowhere rather than to the wrong exam.

**Selectly's `vic-seal` config is still the pre-2026 format** — 4 sections, 120 min,
written expression 1 task/25 min. The real paper is 3 components, 155 min, writing 2
tasks/40 min. Forms are dealt against the real paper, so schools.ts needs rewriting
before any VIC form can be served. Detail: HANDOVER §4.1b and §4.1c.
**Read before generating anything:**
- `pdfs/selectly_implementation_HANDOVER.md` — what the Selectly APP must implement:
  qbank_id, fixed forms, exact-pace timing, the DB columns, and the fact that 3,133
  pushed rows have been repaired in qbank and cannot be updated downstream.
- `pdfs/selective_exam_delivery_SPEC.md` — fixed drill and mock forms, exact-exam-pace
  timing, the release calendar, and the data model (§6).
- `pdfs/nsw_content_taxonomy_TASK.md` — every NSW category and subcategory with a target.

**NSW is content-complete across all four components.**

| Component | Built | Target | Drill forms |
|---|---:|---:|---:|
| Reading | 649 | 649 | 27 |
| Mathematical Reasoning | 839 | 838 | 42 |
| Thinking Skills | 956 | 880 | 48 |
| Writing | 42 prompts | 21 | mock-only, no drill allocation |

**DB totals:** 8480 questions — QR 2240, MA 1382, RC 1368, SR 1322, VR 1212, LR 956.
5313 approved, 3103 pending, 64 rejected.

**Next task: human review.** 3103 pending, of which 954 Thinking Skills and 649 NSW
Reading have never been seen. That queue, not authoring, is what gates launch — drill
serves the approved bank (SPEC §5.1) and NSW currently has ~0 approved outside maths.

**Forms are dealt.** `tools/assign_forms.py` assigned 117 NSW drill forms over 2441
questions; manifest in `run_data/output/forms/nsw_forms_manifest.json`. The deal covers
approved AND pending, because gating on approval would have produced nothing. It is
therefore provisional: `--report` shows which forms hold a rejected question and
`--repair` lifts them out and renumbers. **`--repair` is pre-launch only** — once
students have sat a form, removing a question re-bases every score recorded against it,
and the fix moves downstream to Selectly's `questions.active`.

**Mock plan (decided 2026-08-10).** Nothing is reserved for mocks; the whole bank goes to
drill. Mocks are authored fresh, born `form_kind='mock'`, and retire into drill when
superseded. 19 forms are needed for a September launch with weekly mocks over the last
three months — about 25 questions a week, best front-loaded into Sep–Jan so the intensive
phase needs no authoring.

**VIC is planned, not built.** `pdfs/vic_content_taxonomy_TASK.md` (2026-08-10) is the
Victorian equivalent of the NSW taxonomy — researched from ACER's own site, since coaching
providers mostly still describe the pre-2026 five-component format. Two corrections to the
delivery spec fall out of it: **Writing is TWO tasks, not one** (so 54 prompts are needed,
not 27, against 10 held), and **Maths + Quantitative is ~62 questions, not 75**.

Two assessments were reversed by reading the content rather than its metadata:

- **719 ACT-sourced reading questions ARE usable for VIC** — the passages are. Rejected
  first on a briefing's `target_year: 11-12`, then on a Flesch-Kincaid median of grade 16.
  FK is inflated by long-but-ordinary words; three passages read in full sit at Year 9-11.
  **But the QUESTIONS are retrieval-led, which was checked separately on 2026-08-10** by
  hand-reading 40 in two independent random samples: **67.5% retrieval, 32.5% inference**
  (95% CI 53-82%; a key-to-passage lexical-overlap proxy that under-calls retrieval by
  construction puts the floor at 59.5%, consistent across all ten books at 55-71%). 232
  stems promise inference and 37% of those are answered by a near-verbatim restatement.
  §4.1 wants retrieval at 20%. So the reuse holds for drill and for the passages, but
  **VIC reading authoring goes from ~24 to ~300-360 inference-led items** — and the
  cheaper route is writing new questions against the 718 existing passages rather than
  authoring passages. Robust to §4.1 being wrong: even at a 40% retrieval target the
  shortfall is ~213.
- **90.7% of the ACT quantitative bank is usable at Year 8.** Only 188 of 2,020 are beyond
  it — quadratics, trigonometry, logs, permutations. The component is oversupplied (2,556
  against a target of 1,297) rather than 573 short.

VIC authoring now stands at **~815 items**: verbal top-up ~340, reading ~300-360
inference-led (revised up from ~24 on 2026-08-10 — see the reading finding above),
maths Statistics top-up ~100, writing 44.

**Answer-key skew — REPAIRED in VIC scope 2026-08-10.** `tools/repair_key_skew.py`
reordered 2,734 of 2,913 questions (718 ACT reading + 2,195 quantitative). Reading went
from C 47.6% to worst-letter 25.8%, quantitative from A 37.8% to 25.6%; every source book
is within a point of 25/25/25/25. Full before/after state per row is in
`run_data/output/key_skew_manifest.json`, so `--revert` restores it exactly.

Three things that repair established, none of which were in the plan:

- **Sorting numeric options ascending is the wrong fix.** It looks tidier and imposes a
  real exam convention, but measured over the 1,550 numeric items it makes the cheat
  slightly *worse* (37% vs 35%), because distractors bracket the key — 71% of keys are
  the 2nd or 3rd smallest of four. Shuffling gets it to 26%. The bracketing itself is
  unfixed and needs distractor *values* regenerated, which is authoring.
- **The length tell survives.** In ACT reading the key averages 62.1 characters against
  54.9, so "pick the longest option" still scores **48.7%** — reordering moves options
  without changing them. This is now the single biggest exploitable defect in the bank.
- **45 questions are defective, not merely misordered**, and were refused: 16 with
  duplicate option text (several duplicate the key, so a right answer is marked wrong),
  17 whose explanation shows the answer being chosen rather than derived, 8 admitting two
  options are equal, 2 with a stale inline `A) B) C)` enumeration, 1 missing an option,
  1 where A-D are geometry point labels. They are listed in the manifest and need a human.

**The original bank-wide defect:** `reading_comprehension` runs
37% C, `quantitative_reasoning` 38% A with D at 8%. A student who never picks D loses
almost nothing. Within VIC scope that is **2,913 questions** — 718 ACT reading and 2,195
quantitative. `logical_reasoning`, `mathematics` and the `rc_nsw_*` set are clean at
25/25/25/25, because their finalisers shuffle for key balance and the Gemini pipeline
never did. No question is wrong — they are in the wrong order — so it is a shuffle, not a
rewrite. Repairing it is worth more per hour than any authoring in the VIC plan.

**Blockers:** two, both below. Neither stops new questions being generated; both stop
questions already pushed from being corrected or withdrawn — and blocker 1 now also
blocks pushing the form assignments.

**Explanation quality — repaired 2026-08-04.** 139 questions carried the generating
model's own working in the `explanation` field ("Oh, wait.", "Why did I select B?"),
which TASK §7 forbids. It was a symptom: comparing the working before the model's first
self-correction against the stored answer showed 36 questions with no correct option at
all and 43 whose working supported a different option than the key. In every case checked
by hand the working was right and the key was wrong, including two that were approved and
serving students. `tools/repair_leaked_working.py` rejected 38, corrected 42 answers,
requeued 4 approved rows to pending, and cleaned 59 explanations; the full record is in
`run_data/output/leaked_working_repairs.json`. `tools/question_checks.leaked_working`
now screens for it. The root cause is the open checklist item below — those QR pages were
generated on a thinking model whose scratchpad reached the output.

**Build harness for authored questions** (`tools/`, all committed and tested):
`question_checks.py` holds the subject-agnostic checks — distractor-relation design,
answer-shape monotony, the longest-option tell, positional explanations, figure rules,
real-word screening. `vr_finalise.py` / `lr_finalise.py` are the per-subject
orchestrators; `load_batch.py` loads one batch and refuses to record it as loaded if
phase 4 dropped anything (phase 4 drops near-duplicates silently). Builders live in
`tools/vr/` — committed, because the curated word data is the actual work.

**Recently completed:** VIC `verbal_reasoning` §3 top-up, **183/183** (2026-08-04) —
126 vocabulary-in-context, 25 antonyms, 22 shades of meaning, 10 word-group. All pending.
Built by hand in `tools/vr/vr_p1..p9_build.py`, not by Gemini.

  The design responds to a measured defect in the existing bank: in ~24 of 26 sampled
  synonym/antonym questions the three distractors were mutual synonyms and the key was
  the semantic singleton (ABUNDANT → Plentiful against Scarce/Limited/Meagre), so the
  item was answerable without knowing the target word. Every new question therefore
  declares how each distractor is wrong and is rejected if the three cohere.

  Two other measurements shaped it. Bare "Which word means X?" frames score 0.857–0.872
  against each other, above phase 4's silent 0.85 dedup threshold — so stems are
  contextual, which §3.1 wants anyway. And once stems are contextual, stem similarity
  can no longer police vocabulary reuse, so the target word is the question's identity
  and is carried into `source_page_description` as `[target: word]`.

**Previously:** `logical_reasoning` built from 0 → **300/300** (2026-08-03/04),
all 17 categories at target, 34 with inline SVG figures, per-question confidence
0.84–0.98. Spec: `pdfs/selective_verbal_reasoning_TASK.md` §4. State and method:
`pdfs/selective_verbal_reasoning_HANDOVER.md`.

**Two things needing attention:**

1. **Nothing already pushed to Selectly can be reached again — BUT THE FIX IS WRITTEN
   AND UNDEPLOYED (verified 2026-08-12).** Selectly commit `c52ffa9` on the unmerged local
   branch `feature/qbank-id-addressability` adds `questions.qbank_id`, makes
   `/api/questions/import` upsert on it, and lets `/api/admin/questions-fix` address rows
   by it; qbank has `pipeline/backfill_qbank_ids.py` (with `--dry-run`). The remaining work
   is merge, apply the migration, deploy, backfill, and deactivate whatever stays null.
   `push_to_selectly.py` has always sent `qbankId` — the sending side was never the
   problem. Until this ships it blocks the VR exclusion below, and every future correction. `/api/questions/import` is insert-only
   and lets Postgres mint its own uuid, so qbank has no handle on the row it created —
   all 5321 approved questions are out there unaddressable. Selectly *does* have the
   machinery: `questions.active` (both the exam and drill selectors honour it) and an
   `/api/admin/questions-fix` endpoint that can set it — but that endpoint addresses rows
   by *Selectly's* uuid. Fix: pass the qbank uuid as the row id on import (qbank ids are
   already uuid-v4), then backfill the existing 5321 by stem-matching via
   `/api/admin/questions-dump`. Do this before generating anything new.

2. **VR calibration is not just a shortfall.** Questions of types the brief says never to
   generate — dictionary/alphabetical ordering, word codes, hidden words, anagrams,
   alphabet position — are approved and being served. **Counts need settling before
   acting:** a stem+topic classifier finds 166 strict §6 violations (164 approved); the
   handover's figure of 407 counts a broader "off-spec" set (spatial, double meanings,
   odd-one-out variants) that is a judgement call, not a §6 breach. Note §8 rates the §6
   list "Medium-low — argument from absence", which is thin evidence for pulling 400
   approved questions. The lever is `active=false`, NOT `schoolIds`: `verbal_reasoning`
   is a vic-seal-only category so there is no other exam to route them to, and the drill
   selector ignores `schoolIds` entirely. Blocked on item 1.
