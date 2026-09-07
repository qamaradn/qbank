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
11. **MEASURE WIDE, REPAIR NARROW.** (Revised 2026-08-30, replacing "a gatable flag is
    a sweep". The old rule cost three sets of correct figures — see below.)

    a. **Fix the question the reviewer flagged, exactly as described.** That is the job.

    b. If the flag is expressible as a check, write it and run it over the whole bank
       **to COUNT ONLY.** Measuring is read-only and cannot break anything. Report the
       number — it is the only thing that distinguishes one bad figure from a broken
       generator, and a generator fault will keep producing them in whatever is
       authored next.

    c. **Repair beyond the flagged question ONLY when the repair is ADDITIVE** — one
       that can only add and cannot destroy a correct state: growing a canvas, adding
       an arc where none exists, adding a missing arrowhead, raising opacity. Those are
       safe to sweep.

    d. **A repair that MOVES or REPLACES anything** — a label, a grid, an arc, a tick,
       a number — runs on the FLAGGED QUESTION ONLY. List the other hits and let the
       owner decide.

    The split is not theoretical. On 2026-08-29/30 the additive sweeps ran over 214
    figures with zero damage (canvas 128, angle arcs 42, faint labels 41, markers 3).
    Every mutative sweep broke correct figures: the label nudger moved a y-tick ALONG
    its own axis and made a linear scale nonlinear (3), the gridline tool drew onto
    tick labels 5 px off their marks (3), and the arc repair stripped the mark off a
    phi and an alpha and put nothing back (4). All were caught and reverted, but only
    because the before/after diff and the rendered look were run every time.

    e. Whatever the scope: diff the whole check state before and after and require
       **"newly firing: none"**, and RENDER AND LOOK before applying. Three of that
       session's defects were found only by looking and by no check at all.

    f. **The human eye is the ground truth for whether a figure is right.** Every
       figure question goes in front of a reviewer before it serves a student, so a
       measurement is a triage signal, never a verdict.
12. **Fix quietly. Do not escalate.** Closing a flag is not a discovery to be reported
    with a proposed action plan. Do not raise a count as a blocker, do not create
    out-of-band work items, do not ask which of several repairs to start. Work is
    sequenced BY FORM and continues in that sequence — a defect found outside the
    current form is fixed, or listed under 11d, and does not reorder anything.
    Reporting a COUNT under 11b is not escalation: it is one line of fact, with no
    plan attached.

### What this looks like in practice

**Additive, so sweep it.** Round 6 flagged one figure for naming an angle with nothing
marking it. Adding an arc cannot destroy a correct figure, so all 42 were marked and
the flag closed in one pass.

**Mutative, so don't.** A reviewer flags one label sitting on a line. Moving labels is
how three correct figures got a nonlinear axis. Move the flagged one, report "31 others
match this pattern", and stop there.

**A re-cut of a question is mutative.** Round 5 flagged `a00cb43b` as needing algebra
rather than reasoning, and two more (`c99bf947`, `c61a9369`) matched. Under the old
rule all three were re-cut unasked. Under this one: re-cut the flagged one, say the
other two match, and let the owner call it.

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

**Last worked on:** 2026-09-06 — NSW FIGURE ROUND 1 IS OPEN AND NOT STARTED.

Alaan Q.'s first NSW return is `review/ui/figure-review-nsw-2026-09-06.json`: **10 flags
on a 254-card page**, all `pending`, none live in Selectly. The brief for working them is
`pdfs/nsw_figure_round1_PROMPT.md`. Two Thinking Skills questions and eight maths; the
marks run from card 8 to card 250, so it reads as a complete pass rather than a partial
one. **No repairs have been started.**

**The authoring gate is vindicated by the numbers.** NSW has 320 figures and 12 fire the
check set (4%); VIC has 512 and 88 fire (17%). The reviewer flagged 10 of 254 here
against 181 of 445 on VIC — a tenfold difference in review load, the same reviewer and
the same kind of content. NSW was authored through `question_checks`; the Gemini books
were not. `tools/figure_gate.py` now runs the whole set at authoring time for exactly
this reason.

Three things that round has to handle, each checked rather than assumed:

- `bf613208` and `d5975559` share ONE figure, byte for byte — the same 1,429-character
  SVG, one asking the area of a U-shaped tile and the other its perimeter. That is why
  the reviewer wrote the identical note twice. Fix the drawing once and write it to BOTH
  rows. They are not duplicate questions (stem similarity 0.31).
- **Seven of the ten fire no check at all.** Only three are visible to
  `text_overlaps_geometry`. A clean gate state is not evidence a figure is right.
- `b2c8c7b6` asks for a deletion, not a repair. Removing a question from a dealt form
  changes its size, and NSW forms are 19-26 items, so a silent removal re-bases every
  score recorded against that form.

**Previously:** 2026-09-04 — ALL 153 VIC DRILL FORMS APPROVED AND PUSHED LIVE.

The figure rounds are closed, so the owner's call was to stop piloting and put the whole
VIC bank in front of the reviewers: approve everything, push everything, let them work
through it form by form at their own pace, and take the fixes from the CSVs as they come.
**Human review inside Selectly is the launch gate — nothing in qbank is.**

| Category | Forms | Questions | Complete |
|---|---:|---:|---:|
| Maths + Quantitative `vic-drill-mq-*` | 87 | 2,691 | 87 of 87 |
| Reading + Verbal `vic-drill-rv-*` | 66 | 2,499 | 66 of 66 |
| Writing `vic-drill-wr-*` | 27 | 54 prompts | not pushed |

**Approved in two steps, both revertible.** First every VIC question carrying a figure --
445 pending rows, 67 already done, 512 in all, every one of them in an `mq` form since VIC
reading and verbal have no figures (`tools/approve_vic_figures.py`). Then the remaining
4,055 across all 153 forms (`tools/approve_forms.py`, whose record now holds 5,380 rows and
appends rather than overwrites, so August's 1,325 stay revertible). Rejected questions are
left alone by design.

**Pushed 4,500 to production: `inserted=4500 skipped=0 errors=0` over 113 batches.** The
other 690 were already live from the August pilot. Restricted with `--forms` to the 153 VIC
forms, which also restricts the deactivation pass, so the 635 approved NSW questions that
would otherwise have gone were left alone.

**Verified by reading production back, not from the push log.** Per category, every one of
the 5,190 VIC approved questions is live and every live row carries a `qbank_id`:
mathematics 641 of 641, quantitative 2,050, reading 1,112, verbal 1,387. **0 unaddressable.**
The larger row counts in the dump (842 mathematics, 1,347 reading) are NSW questions in the
same categories, and the single inactive mathematics row is the rejected "zero pairs"
question the withdrawal pass switched off in August.

**ONE THING IS NOT VERIFIED AND CANNOT BE FROM HERE: the form assignments.** Selectly's
schema has `form_id`, `form_position` and `form_kind`, the import route reads and writes all
three (checked in the code), and the push sent them with no errors -- but no endpoint
returns them. `/api/admin/questions-dump` exposes `qbankId` precisely so a caller can see
what is unaddressable; it should expose `formId` for the same reason, and until it does,
"the forms are dealt in production" rests on the import code rather than on a read-back. It
is a few lines in that route. **Ask for it before relying on the forms.**

**Both August blockers are closed** (checked in the Selectly repo, not the notes): `vic-seal`
in `schools.ts` is now the 2026 three-component config -- maths+quantitative 62q/60min,
reading+verbal 75q/55min as ONE section, writing 2 tasks/40min -- and the import no longer
strips the form fields.

**Nothing holds back a form.** The pusher excludes 158 §6 verbal and 108 beyond-Year-8 QR
questions; none of them is in an `mq` or `rv` form, so all 5,190 were sendable and every
form arrives full.

**VIC WRITING IS NOW LIVE TOO (2026-09-06).** All 54 VIC prompts across the 27
`vic-drill-wr-*` forms: `inserted=54 skipped=0`. Verified by reading production back and
comparing FIELD BY FIELD against qbank -- stem, stimulus, stimulus type, prompt type,
both word counts, the time, the form and the position all match on all 54, every one
active, 27 forms of exactly two at positions 1 and 2. `pipeline/push_writing_to_selectly.py`.

Writing prompts live in their own table, so they have their own sender. It shares the
tracking and payload hashing, and it **refuses to push while Selectly's dump lacks
`stimulus`** -- a prompt whose stimulus is dropped imports with `errors=0` and reads as
broken, and eleven of the 54 are quote prompts whose task says "argue for or against the
view expressed in the quote below". That guard held the push for a day until the Selectly
work shipped, which is what it is for.

**No rubric is sent.** Selectly's import used to require a five-key object qbank does not
have and nothing there read -- `buildGradingPrompt` hardcoded its own dimensions. The
marking dimensions now come from `prompt_type`, which matters: `vic-drill-wr-016` is
persuasive at position 1 and narrative at position 2, so the old fixed rubric was marking
that narrative on "Argument".

**NSW and JMSS writing are NOT pushed and that is deliberate.** NSW's section is already
correct at 1 task / 30 min and its 42 prompts have no forms dealt, because NSW sets one
prompt and a form of one adds nothing -- "writing does not halve" (SPEC). JMSS has no
exam in schools.ts, so the sender holds its 10 back on its own. All 106 are `approved`;
52 are approved-but-unsent by design, which is what `--verify` reports as "not live".

**Previously:** 2026-09-04 — VIC REVIEW ROUND 11. THE SIXTEEN THAT CAME BACK.

The rounds 9-10 page (`compare-vic-mq-rounds9-10.html`, all 95 questions repaired in
those two rounds) came back on 2026-09-03. **Seventy-nine passed with no comment.**
Sixteen carry a note and **all sixteen are repaired.** All were `pending`, none live.
Nine of the sixteen are round-10 work coming back and seven are round-9 work.

Read the return with care: the ingest tool prints "flagged 15, marked fine 1" because
one card is marked `note` rather than `problem` — and that note asks for gridlines and
a bigger font, which is work. The count is 16. The same thing happened in round 10.

**The flags are converging: 181 of 445, then 95 of 223, then 16 of 95.**

Ten of the sixteen were placement or presentation and were done as written — four
charts wanted horizontal gridlines in almost the same words, so they get them the same
way, at the tick heights and nowhere else. **Six were not**, and each was worked twice:

- **A duplicate the checks never saw.** `431d4c9b` asks for the area of a square on the
  hypotenuse of a 5-12 triangle, and so does `ef7b9ff2` in `vic-drill-mq-070`, with the
  same numbers and the same answer of 169. Both pending, so a student sitting two drill
  papers would meet it twice. Re-cut on 8-15-17 (289), which no other question uses;
  the closest stem in the bank is now 0.71 against phase 4's 0.85 threshold. The square
  is drawn on the hypotenuse now — the figure had only ever shown the triangle.
- **A stem, a figure and a key describing three different shapes.** `0e77976c`'s stem
  says the notches are 3-by-2 and 4-by-2, which leaves 63; its explanation works those
  two out and stops before subtracting; the figure is a U with ONE notch in the middle
  of the top edge; and the key is 57, which is 77 − 4×3 − 4×2, exactly what the
  figure's four numbers say. The key and the figure's labels agree with each other, so
  they stand and the stem's two numbers are corrected. Drawn area measures 57 cm².
- **Bars at three different scales.** `ccac7c88` drew 80 students as 80 px, 100 as 125
  and 70 as 63 — 1.0, 1.25 and 0.9 px per student. Nothing showed it until the y-axis
  the reviewer asked for went on. Redrawn at 1.2 throughout.
- **A chord that stopped inside its own circle.** `bed54cfb`'s ends were 86.5 from a
  centre with radius 90. Rather than stretch it, the whole figure is put on one scale:
  the chord now sits where a 16 cm chord in a 10 cm circle actually sits, 6 cm from the
  centre, which is the answer. Every length is now the length its label claims.
- **A right angle marked about a point in mid-air.** `5edd52c3` drew road OB at 52.5°
  while the stem says 55, and put D at a spot 7 px off that road, so the mark hung off
  the line. OB is at exactly 55° now and D is DERIVED as the foot of the perpendicular
  from C — which lands at 114.7 m, the keyed 114.
- **A straight revert.** `7961f672`: "the updated graph looks far worse ... revert back
  to the before graph and simply delete any number that is being overlapped." Round 10
  moved a whole column and row of tick numbers to keep every number at its own tick;
  the reviewer would rather have four numbers missing than seven moved. Restored from
  the round-10 backup with those four deleted. **The lesson is worth keeping: a fix
  that satisfies a check can still read worse than the defect it removed.**

**Two more only showed up on redrawing.** `c76f4d12`'s point E "is a semi-circle" —
it is a whole circle with the letter E painted over its right half, because round 10
moved the letter to clear the y-axis and moved it onto the dot instead. And
`a30aed4e`'s missing x numbers, −2 and 3, are missing because the line y = x + 2
crosses the axis at exactly x = −2 and the line x = 3 runs the full height of the plot
through where its own number belongs; they can only come back if both lines stop short
of the number row, and they now do.

**16 repaired, 0 refused, newly firing none. 275 tests pass.** One finding stands and
is not a regression: `42e248db` keeps a tick number grazed by its own plotted line.

**THREE OF THE SIXTEEN WERE THEN OVERRULED BY THE OWNER (2026-09-04), ALL THE SAME
CALL: a missing tick number is to be written, and every number sits on the same side of
its axis as the rest.** `7961f672` gets back the four the reviewer had deleted -- y 3
and -2 into the x=89 column, x -1 and 4 into the y=158 row -- and `42e248db`'s -5 comes
in from the far side of the axis to the column at x=72. Read back off the stored SVGs,
both figures now carry a complete, evenly spaced set: 30 px per unit on 7961f672 and 24
on 42e248db, with no number off its column or row. Each restored number is drawn twice,
halo behind and glyphs on top, so the rectangle side or the plotted line behind it is
broken where the digits sit. `tools/repair_owner_axis_ticks.py`, backup
`qbank.db.bak-owner2-184900`.

**Redoing 42e248db turned up a defect round 10 left behind.** Round 10 meant to give
that -5 a halo and inserted the second copy next to its neighbour in the COLUMN instead
of inside the aria-hidden group -- the pattern it anchored on only existed in the
visible layer, because the halo layer never carried -4 or -5. So the figure had been
carrying two identical visible copies stacked on each other, and the number had never
had a halo at all. One copy is in the halo layer now and one is glyphs.

**AND THEN THE NUMBERS WERE MOVED CLEAR (2026-09-04, same session).** Restoring them
left four sitting on ink, and the owner asked for them moved "a bit up or down". Up and
down was measured first and is not available: shifting a y column down clears the line
at 6 px, and at 6 px `plotted_geometry_matches_stem` starts calling the figure wrong,
because it reads the axis mapping from the label positions and every plotted point then
reads a fifth of a unit out. **A y number may only move SIDEWAYS and an x number only UP
OR DOWN — the other direction is the one the mapping is read from.**

So on `7961f672` the whole y column went left of the rectangle and the whole x row below
it, and on `c0526d7f` the y column went left of A. Each set stays one straight line of
its own kind, which is what round 10 got wrong by moving only some of them. **Both
figures are now completely clean on every check** — the overlap is gone and nothing was
traded for it. `tools/repair_owner_tick_clearance.py`, backup
`qbank.db.bak-owner3-190616`.

The first attempt put `7961f672`'s x row just under the rectangle, where the row's -2 and
the column's -3 ended up shoulder to shoulder in the corner. `overlapping_text_labels`
passed it, because that check wants a real 6 px overlap and these merely touched. Found
by rendering it and looking.

**Previously overruled the same way (2026-09-04):** on `c0526d7f` the
reviewer asked for the y-axis "1" to be deleted and round 11 deleted it; the owner asked
for it back, "align 1 as all other ticks on y axis". It is back at x = 179, y = 176,
where the column and its own tick put it, and it now carries the page-coloured halo the
other numbers have and it never had — so AB is broken behind the glyphs and the number
reads over the line. `tools/repair_c0526d7f_yaxis_one.py`, backup
`qbank.db.bak-owner-184607`. The whole column measures 30 px per unit end to end.

AB runs from x = −4 to x = 2 at that exact height, covering the column on both sides of
the axis, so there was never a clear spot to use instead.
Record: `run_data/output/vic_round11_figures.json`, script
`tools/repair_vic_round11_figures.py`, backup `run_data/db/qbank.db.bak-round11-180148`.

**Page built and ready to send: `review/ui/compare-vic-mq-round11.html`** — 16 cards,
all 16 carrying Alaan's own note, all 16 redrawn. Verified by parsing the page's own
data back against the live database and the backup.

**WHAT "DONE" MEANS HERE.** Finishing these rounds finishes the DRAWING work for VIC
maths. It approves nothing: 445 of the 512 VIC maths questions carrying a figure are
still `pending`, and moving them to `approved` is a separate human pass over the words
and the keys, not just the pictures. NSW's 254 pending figures have not started.

**Previously:** 2026-09-02 — VIC REVIEW ROUND 10. THE FORTY-SIX ABOVE CARD 113.

Alaan's 2026-09-01 file (`review/ui/figure-review-vic-mq-recheck-2026-09-01.json`) holds
95 comments. Forty-nine are the round-9 notes repeated byte-for-byte, because Alaan
re-downloads the whole page each time; those are the cards numbered 2 to 113 and were
already done. **The work was the 46 comments on cards above 113. All 46 are repaired.**
All were `pending`; none was live in Selectly. Nothing outside the 46 was touched.

Most notes were placement and were done as written. **Twenty-one were not**, and each was
worked twice by two routes before anything changed, with every key confirmed by MEASURING
the figure that shipped — reading the coordinates back out of the stored SVG:

- **Two keys moved.** `3c6c07ee` cuts a 6-by-9 corner off a 12-by-18 rectangle, so the
  perimeter is 45 + 3√13 = 55.8 — not one of the four options, and the explanation wrote
  that same expression and then called it 57.8. Worse, a cut corner always SHORTENS a
  boundary, so 60, 63 and 66 were unreachable on sight and only one option could ever
  have been right. Re-cut to a 6-by-8 corner: hypotenuse 10, perimeter 56.
  `46c3108f` showed two congruent triangles with 15 cm printed on the very side the
  other one called x, so x could be read straight across — the reviewer's own words were
  "too obvious ... scale up the second triangle and make them similar". It is now 8-15-17
  against 16-30-34, drawn at twice the size, and x = 30 either by the scale factor or by
  Pythagoras.
- **Eight figures disagreed with their own numbers.** `c1930d7d` was a pie chart drawn as
  a four-pointed star: every slice swept the long way with the large-arc flag left at 0,
  so each arc bulged inward. `6559d286` had C and D the wrong way round, drawing the
  90° slice as 50°, and two labels sitting in a slice they do not name. `64404632` drew
  Collingwood's bar TALLER than Carlton's while labelling it lower. `7ed5c9e5` placed its
  three y numbers at heights that work out at 17, 9 and 0. `2a58c697` drew the 15-pie bar
  at 12.5. `6e95b3e1` cut the spinner into 156/81/33/90 degrees against probabilities of
  45/15/25/15, put X and Y in the same slice and ran two radii out through the rim.
  `93e6e231` drew W somewhere other than the foot of the perpendicular and the right
  angle at Y at 78°. `3aa33936` drew a 10-by-24 rectangle wider than it is tall.
- **Four questions said something the picture did not.** `f253343d` asked for a + b = 180
  from two lines that were not parallel, so the answer followed from nothing; they are
  parallel now, with chevrons. `b45f50b0` put OB at 45° while the stem needs 125°, so the
  picture said the answer was 45 and the key says 35. `7d94095a` described black and
  white L-shaped sections beside a plain black box — two of its three rect elements
  painted nothing, one of them written with x2/y2 attributes a rect does not have.
  `82f15e67` and its stem both said the corner was cut off the top right; the polygon
  cuts the bottom right.
- **Two were wrong in the words only.** `247238f5`'s explanation listed ten values that
  are in no row of its plot and averaged them to 37.5, which is not an option; the plot
  holds nine values and its median is the keyed 36. `81a45008` offered "96 + 36 = 132
  cm²" as an option — a sum with its working shown, of the right answer plus the base.
- **One was a font that was never a font.** `6e18fcef`'s A, B and C looked "weird"
  because the root `<svg>` carries `fill="none" stroke="currentColor"` and every `<text>`
  inherits it, so all seven labels were drawn as hollow outlines.
- **Four more turned up only on redrawing what the reviewer asked for.** `33547c58`
  marked alpha in the region ABOVE the first line, which is exterior, while the stem
  calls it co-interior with beta — and beta, named in the stem, was marked nowhere at
  all. `26205798` drew the q arc as a semicircle about a point sitting on the base line
  30 px past the vertex, belonging to no angle, and carried two `<line>` elements whose
  x1 reads `'50,180'`, which is not a length. `3114e7d5`'s net could not be folded: the
  top and bottom flaps start 10 px from the face between them. `36544278` drew a height
  of 160 px on a figure whose own 3s and 16 set the scale at 10 px per cm, so the height
  labelled 8 was drawn as 16 — and its one dimension rule ran the whole base, 22, with a
  "3" under each end.

**MY OWN WORK ADDED FIFTEEN MORE DEFECTS, AND THE CHECK DIFF REFUSED EVERY ONE OF THEM
BEFORE IT REACHED THE DATABASE** — fewer than the figures held this time, which is the
first round that has been true. Six were labels I moved onto something else: a "10" onto
a circle, a beta onto its own arc, a "C" 6 px above the viewBox, an "x" onto an
arrowhead, a "12 cm" onto its own dimension rule twice, and an "S" under a tick number.
Four were the scale trap: **a y number may only
move sideways and an x number only up or down**, because the check reads the axis mapping
from the label positions, so a number shifted along its own axis makes the axis read as
nonlinear — that refused three separate attempts on `7961f672`, `c0526d7f` and
`0f936d02`. Four were labels landing on faint gridlines, fixed with halos. One was a
figure rebuilt over the 3.5 KB limit at 4,219 bytes.

**And one was a check reading a table as a chart.** Removing the ghost grid from
`3a39fbb9` — the reviewer's actual request — made `coordinate_figure_without_grid` fire,
because that check exits early only on a drawn rect LARGER than 40 by 40 and every cell
in that table is exactly 40 by 40. An outer frame round the sixteen cells settles it, and
a table wants one anyway.

**Four findings are left standing and are NOT regressions.** Three figures (`42e248db`,
`7cc5d3c3`, `653b3f7f`) keep a tick number grazed by the plotted line, which crosses the
number column at that height — the only free spot is the far side of the axis, and a
second number out of column reads worse than a two-pixel graze. One (`3a39fbb9`) stays
over the byte limit. All four were firing before this round and none is what the reviewer
raised.

**46 repaired, 0 refused, 8 findings cleared, newly firing none. 275 tests pass.**
Record: `run_data/output/vic_round10_figures.json`, script
`tools/repair_vic_round10_figures.py`, backup `run_data/db/qbank.db.bak-round10-133407`.

**Page built and ready to send: `review/ui/compare-vic-mq-round10.html`** — 46 cards, all
46 carrying Alaan's own note, all 46 redrawn. Verified by parsing the page's own data
back: every before-picture matches the backup, every after-picture, stem, option and key
matches the live database, and all 46 are still `pending`.

**Previously:** 2026-08-31 — VIC REVIEW ROUND 9. THE FORTY-NINE ALAAN WROTE A
NOTE AGAINST, AND NOTHING ELSE.

Round 8's page (`compare-vic-mq-recheck.html`, 223 cards) came back with comments on
**49**, numbered 2 to 113. All 49 are repaired. The other 64 inside that range were
looked at and passed.

**ROUND 10 IS QUEUED AND BRIEFED.** Alaan's next file arrived 2026-09-01 as
`review/ui/figure-review-vic-mq-recheck-2026-09-01.json`. It holds 95 comments, but 49
are the round-9 ones repeated byte-for-byte — Alaan re-downloads the whole page each
time — so **the work is the 46 comments on cards numbered above 113**, all `pending`,
none live. Books: `png_shs_pt1_310526` 13, `png_act_test8_240526` 12,
`png_act_test7_240526` 10, `png_act_test5_230526` 4, `png_act_test2_230526` 3,
`year9_maths` 2, `png_act_test4_230526` 2 — the first and the `year9_maths` pair have
not been through a figure round before. Full brief:
`pdfs/vic_figure_round10_PROMPT.md`.

**A card with no comment is a PASS, not a gap.** The round's whole brief: work only on
questions carrying a comment, do not sweep, do not repair anything the reviewer did not
name. Nothing approved was touched; all 49 were `pending`.

Most notes were placement and were done as written. **Twelve were not**, each worked
twice by two routes, and every key confirmed by MEASURING the figure that shipped:

- **Four keys moved.** `0096a667` a bottom edge labelled 8 on a shape that closes at 7
  (perimeter 38, not the keyed 46 — which is 38 with that edge counted twice);
  `23bfa545` marking 70° at A *and* 110° at D forces AB ∥ DC, making it a parallelogram
  rather than the trapezoid the stem describes, so A is 60° and angle CDE is 70°, not
  40°; `7c325b26` the stem named the wrong pair of sides parallel, angle BDC is 40°;
  `f0ab0510` one straight line through the origin at 20 km/h, keyed 25, with an
  explanation reading 70 km at t=3 (not on the line) and signing off "The answer is C"
  while the key said B.
- **Eight where the key was right and something else was wrong.** `d3c74fcc` the
  reviewer read the figure correctly and got 44 — the cut-out was drawn 6 wide where
  the working says 4, so the FIGURE was redrawn and the keyed 56 now matches;
  `63e9b382` an incircle too small to touch anything, derived now at exactly 2 cm from
  all three sides; `f17a9331` a triangle off the lattice; `a30aed4e` the answer printed
  on the graph as a labelled point; `e75376a3` options B and C the same line
  (`4x − 2y = −6` is `y = 2x + 3`), C now `y = 2x − 3` which is parallel;
  `b86b2e3c` a point C defined as lying on both diameters — that is the centre, so
  every angle from it was undefined — beside an option naming a point D the figure does
  not contain; `ccac7c88` an explanation using five numbers that are not the five in
  its chart; `7edd1fff` an explanation using adjacent angles where a parallelogram
  needs opposite ones.

**MORE WAS WRONG IN MY OWN BUILDS THAN IN THE FIGURES, AGAIN — ten against twelve.**
The before/after check diff refused SEVEN before they reached the database: a
hard-coded `#fff`, a circumference stroked twice, two rotated axis titles drawn inside
the tick-number column, equation labels with no halo over the gridlines beneath them,
a pie label long enough to reach back over its own arc, and four gridlines called a
grid. **Three more no check saw and only looking caught:** `fl.plane` moves a tick
number to the other side of the axis wherever a plotted line crosses the tick row,
which reads as a number out of line — the exact fault the reviewer raised on
`4653b226` — so `31585b1f` keeps its own grid, extended, and `e75376a3` keeps its
figure untouched; and twice, two arcs of equal radius at one crossing joined into a
single semicircle and marked nothing.

**All 44 single-question checks were diffed before and after: newly firing none, ten
findings cleared.** 275 tests pass. Record: `run_data/output/vic_round9_figures.json`,
script `tools/repair_vic_round9_figures.py`, backup
`run_data/db/qbank.db.bak-round9-204047`.

**Page built and ready to send: `review/ui/compare-vic-mq-round9.html`** — 49 cards,
all 49 carrying Alaan's own note, 47 redrawn and 2 wording-only (their notes were about
the options, not the picture). Verified by reading the page back: all 49 cards' stem,
options, key and after-picture match the live DB.

**`latex_markup_in_text` WIDENED, with the owner's agreement.** It only fired on a
`$...$` pair containing a backslash command, so it missed `$y = 2x - 3$` and `$AB$`,
which the reviewer found twice. Measured first: 421 questions carry a `$...$` pair and
**404 of them are prices**, which is why the rule was narrow. A price always opens on a
digit, so the rule now also fires when the `$` is followed by a LETTER — 16 hits, none
of them money. **Nine were pending and are repaired** (`tools/repair_latex_markup_round9.py`);
six were already rejected and one (`f27e0d63`) is approved and live in
`vic-drill-mq-008`, so both groups are left alone. Reading those nine turned up **a
fifth wrong key**: `6aafd8b2` asks when $5000 at 4% first passes $6000 —
1.04⁴ gives $5849.29 and 1.04⁵ gives $6083.26, so it is 5 complete years (option D),
keyed A, with an explanation that worked out "5 years" then wrote "Answer is B" while
B is 7 years.

**Previously:** 2026-08-31 — VIC REVIEW ROUND 8. THE REVIEWER FOUND 181 OF 445
FIGURES BAD AND THE CHECK SUITE HAD CLEARED ALL 445.

AlaanQ reviewed the VIC maths figure page and flagged 181 (41%), 94 of them for the
same thing: a number printed on top of a line. `text_overlaps_geometry` caught **none
of the 94**, and both reasons were in the check. It read only `<line>` elements — so a
rectangle's sides, a polygon's, a circle's and every angle arc were invisible, which is
where shape figures do all their drawing — and it skipped horizontal and vertical
segments by design, so a label on the vertical side of a cube was invisible twice. It
reads `figure_lib.figure_outlines` now: every inked edge, arcs and curves flattened,
**transforms applied** (three pie charts draw inside `translate(110,108)`, so read at
face value their sectors sit 110 px from where the browser puts them). 85 of the 94.

**Widths are measured, not counted.** Three comments claimed `len(label) * 0.55` ran "a
quarter narrow". Measured against the 4,317 labels the VIC figures draw, it is within a
few percent ON AVERAGE and wrong by up to a factor of four per label. `_text_box` uses
Arial's advance widths and unescapes entities first.

Four new BLOCKING checks, one per thing the reviewer kept saying:
`gridlines_stop_short_of_the_axes` (the grid is laid out from the first tick, not the
origin), `axis_shorter_than_the_data`, `angle_arc_misses_its_rays` (12 hits bank-wide,
all 12 reviewer-flagged), `latex_markup_in_text` (a student shown `$42 \text{ cm}²$`).

**200 questions changed, every one rendered and looked at.** 28 redrawn one at a time
through `figure_lib` (`repair_vic_round8_figures.py`), 20 bare planes, 11 arcs, 70
haloed, 85 labels moved, 25 LaTeX conversions, 11 grids/axes extended.
`text_overlaps_geometry` is now clear on **every one of the reviewer's 189 marks**;
11 marks remain (4 ambiguous arcs at crossings, 3 partial grids, 4 advisory).

**Six of the 28 were WRONG, not untidy**, and only redrawing showed it: a draining-tank
graph with two lines crossing in an X; a triangle at half-units none of which was the
point its explanation names; a parabola printing "(1, 5)" beside the vertex the question
asks for; a pie with two legends stacked and sectors of 60/30/180/90 against a legend
saying 30/15/40/15; "OC" written across the right-angle symbol defining it; and a
meat-pie sector that was not half the circle when half is the answer.

**MORE WAS WRONG IN THE TOOLING THAN THE FIGURES, AGAIN.** `plane()` failed its own
tightened checks. `repair_label_collisions` pushed a label off the canvas and the guard
passed it, moved an x-axis "0" 44 px down the page in two individually-legal moves, took
"30°" out of the sector it names, and its ring returns the FIRST offset that clears —
which is (0,+16), so its habit was shoving labels onto whatever was underneath. It
refuses a partial fix now. And the halo colour written as `var(--figure-page,#fff)`
resolves in a browser and makes **cairosvg refuse the whole document**, so 20 freshly
redrawn planes were applied and unrenderable by the tool every contact sheet here is
made with. Found as blank tiles in a before/after sheet; no check said a word.

**NSW WAS MEASURED AND IS CLEAN** — 254 figures, 12 findings, 0 blocked. It is
materially better than VIC because NSW went through `question_checks` as an authoring
gate and the Gemini books never did. **The NSW round has not started; leave it.**

**LIVE FORMS ARE OFF-LIMITS.** 14 questions in `vic-drill-mq-002..010` fail the new
checks. The reviewer has passed them; those failures are accepted. Do not repair them.

**Reviewer pages now live one-per-scope in `review/ui/`** — `figures-<scope>.html`,
`compare-<scope>.html`; `/figures` lists the folder. `tools/figure_compare_page.py`
builds a before/after page that takes comments and downloads the SAME JSON
`ingest_figure_review` already reads. `compare-vic-mq-recheck.html` is built and ready
to send: 166 pairs, 132 carrying AlaanQ's own note.

**Previously:** 2026-08-29 — FIFTY DRILL FORMS RELEASED TO THE REVIEWER.

**1,325 questions across 50 forms are live and verified (2026-08-29).** Ten forms per
component: `vic-drill-mq-001..010`, `vic-drill-rv-001..010`, `nsw-drill-math-001..010`,
`nsw-drill-read-001..010`, `nsw-drill-ts-001..010`. Push was `inserted=785 skipped=0
errors=0` over 20 batches (779 new, 6 changed), tracked total 546 → 1,325. Verified by
reading production back per category: **1,325 of 1,325 confirmed live, 0 unaddressable.**
The one extra live mathematics row is a rejected "zero pairs" question already
`active=false` — the withdrawal pass had done its job.

`tools/approve_forms.py` set those 1,325 to `approved`; the other 6,306 form-carrying
questions stay `pending`. **Approval here means "reachable by the reviewer", not
"reviewed"** — that is what the tool is for and it is revertible via `--revert`.

**Both gates read "all clear — safe to push" before the release.** They did not at the
start: 16 blocking failures. Clearing them found more in the TOOLING than in the
questions, recorded in `pdfs/figure_correctness_TASK.md` (RELEASE GATE):

- `repair_label_collisions` **could not move a label vertically at all.** Its x/y pattern
  closed the y alternative on `\1`, the *quote* group of the x alternative, which never
  participates when the y branch is taken — so `y=` never matched and every vertical
  offset was a silent no-op. It also read only the first quoted name from "labels 'A' and
  'B' overlap", so the only candidate ever tried was the one named first, which for an
  axis tick is the one that must NOT move; and it moved one of the halo/glyph pair most
  labels are drawn as, leaving the other behind.
- `repair_add_gridlines` **drew grids onto tick LABELS**, which sit ~5 px off the marks
  they name — creating `gridlines_off_the_ticks`, the exact defect round 5 wrote that
  check to catch. It now uses tick MARKS, refuses a figure whose axis is not to a constant
  scale, and spaces lines at the tick interval rather than one mapping unit.
- `_axis_ticks` bucketed by `round(x/6)`, so a y column right-aligned at x=124 and x=120
  split into two groups of two and a figure with a good y-axis read as having none. The
  origin's "0" was counted into BOTH axes, making a linear axis read as nonlinear. Numbers
  inside drawn CELLS are excluded now — a dice net numbered 1 to 6 was being read as a
  y-axis.
- `angle_named_without_arc` measured from the label's CENTRE, so a 66 px label in a 51°
  sector could never be within any fixed tolerance however correctly placed. Edge now.

**Ten questions repaired in `tools/repair_vic_round7_release.py`**, each re-verified
against its own key: two charts whose y ticks did not advance with their pixels (one drew
its line to 140 km when the stem says 120), a "linear scale" numbered 0,5,10,15,17,20,30,40
all one tick apart, a Bézier curve standing in for a parabola with (0,−3) drawn ABOVE the
x-axis, two questions whose answers were 124.2 people and 62.4 apartments, a question
about counters and "zero pairs", and a stem that never asked anything.

**Previously:** 2026-08-29 — VIC review round 6 closed AND PUSHED.

**SELECTLY ADDRESSABILITY IS LIVE — the entry below that calls it "written and undeployed"
was stale and is corrected here (verified 2026-08-29).** `c52ffa9` is on `origin/main`
(tip 2026-08-24), local main is level with origin, and migration
`0001_add_questions_qbank_id.sql` is applied in production: a read of
`/api/admin/questions-dump?category=quantitative_reasoning` returns 150 live rows, **150
of them carrying a `qbank_id` and 0 unaddressable.** Blocker 1 in "Two things needing
attention" is CLOSED. The clean-reload plan of 2026-08-12 was never needed — the upsert
path repairs rows in place.

**Round 6's ten corrections are live (2026-08-29).** `push_to_selectly` upserted 10
changed rows, 0 new, `inserted=10 skipped=0 errors=0`, tracked total unchanged at 546.
Both flagged questions verified live by reading production back: key, explanation and
figure all match the local row, `active=true`. Tracking now stores a payload HASH per
row, so a repaired question re-sends and an untouched one does not — `--dry-run` reports
0 to push afterwards.

**Reviewer flags for round 6 are recorded but NOT cleared** in
`run_data/output/review_flags/round_vic6.json`. Clearing needs
`push_to_selectly --clear-flags vic6`, which deletes the two flags from the reviewer's
admin board; left for the owner to run once the reviewer has seen the fixes.

**`vic-drill-mq-004` still fails the gate on two questions that were NOT in this push and
are already live:** pos 7 `33b467f9` (120 → +15% → −10% = 124.2 passengers, key 124, the
stem never says to round — `repair_rounding_unstated` deliberately declines, since a
passenger count should not carry a rounding instruction; the round-5 precedent is to
re-cut the numbers exact, e.g. +25% then −10% = 135) and pos 21 `1da2cb04` (two "−1" tick
labels overlapping 9×5 px). Bank-wide those two checks stand at `rounds_without_saying_so`
7 and `overlapping_text_labels` 34.

**ROUND 6 IS CLOSED (2026-08-29).** Two reviewer flags, both on figures round 5 had
already redrawn and cleared: the "?" on `25bbe5a8` sat nearer (−2, 0) than the vertex it
names, and `0ac8b411` printed "65°" and "b" beside a crossing that makes eight angles and
marked none of them. Record in `pdfs/figure_correctness_TASK.md` (ROUND 6).

**The round's finding: "the gate is clean", "the figure agrees with the stem" and "a
reader can use it" are three claims.** Round 5 separated the first two. Both round-6
figures pass every hygiene check AND `plotted_geometry_matches_stem` — the geometry is
right and the picture is unreadable anyway. Four new BLOCKING checks:
`unknown_marker_far_from_point` (1 hit — the flagged one), `angle_named_without_arc`
(42 across 36 forms), `label_too_faint` (41), `polygon_sides_disagree_with_stem` (1).

**86 figures repaired; bank-wide figure findings 238 → 143 with nothing newly firing.**
Arcs are DERIVED, never placed: `figure_lib` reads the figure's own segments, finds the
vertex nearest the label and the sector the label already sits in, and draws between the
two rays bounding it — so an arc cannot land on an angle other than the one named.
`tools/repair_angle_arcs.py` 42 marked / 0 declined / 0 rolled back,
`tools/repair_faint_labels.py` 41, `tools/repair_vic_round6_figures.py` 3 redrawn.

**Three defects nobody had reported, found by reading the figures rather than by the
flags.** 41 figures print what the student needs at `fill-opacity` .18 — one of them asks
for y from three interior angles all drawn as watermarks, so it is unanswerable as
rendered. A "regular octagon" is drawn with TEN sides, and 144° — the answer for a
decagon — is sitting there as option A. And `dad3322d` draws the apex whose angle the
question asks for at y = −23 in a viewBox 190 tall, off the canvas entirely.

**A right-angle square is drawn only where the LABEL says 90.** The first pass took it
from the drawn geometry, and these figures are not to scale: it marked a 110° corner
square, and marked the unknown "?°" corner of the same quadrilateral square when the
answer is 70°. A convention that carries information can also carry a wrong answer.

**Measured and NOT actioned: 45 figures have a text box past the viewBox edge**
(`year9_maths` 17). `_text_box` estimates width from a character count and runs about a
quarter narrow, so at the edge it cannot tell a clipped label from a tight one. Fix the
width model before building that check.

**Previously:** 2026-08-26 — VIC review round 5 closed, both exams.

**ROUND 5 IS CLOSED (2026-08-26).** All twelve reviewer flags repaired: ten VIC
quantitative figures and two NSW Thinking Skills taxonomy calls. Record and reasoning in
`pdfs/figure_correctness_TASK.md`.

**The round's real finding: twelve checks existed and the gate was CLEAN on all ten
flagged figures.** Every one of the twelve measured figure HYGIENE — overlapping labels,
doubled outlines, bounding boxes — and none measured whether the picture shows what the
question describes. "The gate passes" and "the figures are correct" are different claims.
`plotted_geometry_matches_stem` is the first check that asks the second one: it reads the
coordinates out of the STEM, derives the axis mapping from the figure's own ticks, and
verifies the drawn points, lines and axes agree. Where it cannot derive a mapping it
returns **needs a human** rather than None.

Figures are now redrawn by `figure_lib.plane` / `.right_triangle` / `.trapezium`, which
place axes, ticks, gridlines, dots, dimensions and angle arcs from ONE mapping, so the
picture has no way to disagree with the words. Repair scripts re-run the full check set
on their own output and roll back if anything fails — that guard caught three of my own
redraws.

**Three exemptions were each individually correct and each removed the only thing
looking.** `figure_proportions_disagree` exempts triangles (a hypotenuse crosses the
bounding box rather than setting it) and exempts figures with an unknown side. Behind
those: a 7 cm side drawn HALF AGAIN LONGER than its 24 cm one, a triangle 25% out of
shape, a 5 cm height drawn taller than a 7 cm base. Where a check cannot judge, it must
say "needs a human", not return None.

**Two silent measurement faults, both bank-wide:** `_text_box` measured
`text-anchor="end"` as if the label started at x, so both overlap checks were reading the
wrong side of every axis (11 newly caught, 18 correctly cleared); and tick-label
BASELINES sit ~4 px below the ticks they name, biasing every label-derived mapping by
0.13 units — most of a 6 px tolerance, spent before the check began.

**The new checks block 70 questions across 50 forms** (`plotted_geometry_matches_stem`
32, `rounds_without_saying_so` 37, `gridlines_off_the_ticks` 1; worst form holds 3).
Nearly all VIC. These are new findings, not regressions — one of them,
`vic-drill-mq-005 pos 15`, is the flagged `11125ee3` defect in a different question.
**They must be cleared before the next push.**

**STILL OPEN — 24 triangles may be drawn to a default shape.** A crude probe over the 261
polygon figures found 24 whose two longest drawn sides disagree with their two longest
labels by more than 22%, all quantitative_reasoning, many drawn at exactly 1.0 or 1.41
while their labels say 2.0–3.0. Needs triage (the probe will catch arrowheads and
similar-triangle figures) then redraw via `right_triangle`. See TASK §5.

**ONE OPEN QUESTION FOR THE OWNER.** `844bbdfe` ("two sisters' ages add up to 19 and
multiply to 88") was flagged as a quadratic and KEPT. No quadratic is needed and none is
used — the stored explanation reasons over factor pairs, which is what UCLES PT1 numeric
deduction asks for, and the reviewer hedged ("could potentially fit in"). Confirm or
overrule. The other three non-symmetric numeric-deduction items were re-cut, not
rejected, so the `nsw-drill-ts` forms keep their size.

**Previously:** 2026-08-12 (second session)

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
