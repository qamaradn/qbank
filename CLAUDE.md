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
- [ ] VIC verbal_reasoning: 183 new (173 vocabulary-family) + exclude the 407 off-target
- [ ] NSW reading_comprehension vocabulary cloze (~120 questions, 15 passages x 8 blanks)
- [x] Selectly: `mathematics` in schools.ts union — already done, mapped to nsw-shspt
      "Mathematical Reasoning" (verified 2026-08-04)
- [ ] Selectly: make pushed questions addressable (send qbank uuid as the row id) — see
      CURRENT STATUS item 1; blocks the VR exclusion and every future correction
- [ ] QR pages rerun with GEMINI_MODEL=gemini-2.5-flash (full model, no thinking)
- [ ] writing_prompts table + generator implemented (see WRITING PROMPTS section above)
- [ ] First batch synced to Supabase

---

## CURRENT STATUS

**Last worked on:** 2026-08-04
**Next task:** VIC verbal_reasoning top-up (183 questions) — but first decide how §6
off-target VR is excluded from VIC practice sets. See
`pdfs/selective_verbal_reasoning_HANDOVER.md`.

**Blockers:** none technical. One decision needed: VR pool tagging (below).

**DB totals:** 6685 questions — MA 1075, QR 2240, SR 1322, VR 1029, RC 719, LR 300.
5321 approved, 1340 pending, 24 rejected.

**Recently completed:** `logical_reasoning` built from 0 → **300/300** (2026-08-03/04),
all 17 categories at target, 34 with inline SVG figures, per-question confidence
0.84–0.98. Spec: `pdfs/selective_verbal_reasoning_TASK.md` §4. State and method:
`pdfs/selective_verbal_reasoning_HANDOVER.md`.

**Two things needing attention:**

1. **Nothing already pushed to Selectly can be reached again.** This blocks the VR
   exclusion below, and every future correction. `/api/questions/import` is insert-only
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
