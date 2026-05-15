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
            ├── schema.sql, config.py, requirements.txt
            └── NO PDFs, NO generated files, NO API keys, NO data

Linux VM (Ubuntu 22.04+)
    ├── Git clone of qbank repo  ~/qbank/
    ├── Python venv              ~/qbank/.venv/
    ├── /data/pdfs/              ← input PDFs + briefing .md files
    ├── /data/scratch/           ← Docling working files (large)
    ├── /data/output/            ← generated question JSON files
    └── /data/db/                ← SQLite database + figure images

Your local machine
    ├── Claude Code              ← all development happens here
    └── Browser → http://<VM_IP>:8000  ← review UI
```

**VM minimum specs:**
- 4 GB RAM (Docling layout AI needs headroom)
- 50 GB disk (PDFs + page images + figures accumulate)
- Python 3.11+
- Ubuntu 22.04 or 24.04

---

## THE 5 SUBJECTS — FIXED. NEVER CHANGE THESE.

| Subject ID | Full Name | Folder Name |
|---|---|---|
| QR | Quantitative Reasoning | quantitative_reasoning |
| LR | Logical Reasoning | logical_reasoning |
| SR | Science Reasoning | science_reasoning |
| RC | Reading Comprehension | reading_comprehension |
| WR | Writing | writing |

These are the ONLY valid subject values in the entire codebase.
Every classifier output, database column, folder name, and UI label
must use exactly these values. No exceptions. No additions.

---

## PDF METADATA BRIEFING FILES — THE MOST IMPORTANT INPUT

Before the pipeline runs on any PDF, a human-written `.md` briefing
file MUST exist alongside it. This is the single biggest accuracy
improvement in the entire system.

### Why it matters

Without it: classifier guesses subject and structure from raw content alone.
With it: classifier knows page ranges, layout, figure positions, and year
level BEFORE reading anything. Misclassification drops dramatically.

### Naming convention — same name as PDF, .md extension

```
/data/pdfs/
    rs_aggarwal_reasoning.pdf
    rs_aggarwal_reasoning.md        ← briefing file
    excel_science_grade7.pdf
    excel_science_grade7.md
    selective_school_practice.pdf
    selective_school_practice.md
```

### Briefing file template — copy this for every new PDF

```markdown
# PDF BRIEFING: <book_title>

## Basic Info
- **file:** rs_aggarwal_reasoning.pdf
- **publisher:** S. Chand
- **edition:** 2023
- **total_pages:** 412
- **relevant_pages:** 45–380

## Layout
- **column_format:** single_column | double_column | mixed
- **question_numbering:** 1,2,3 | Q1,Q2 | (i),(ii)
- **options_format:** (A)(B)(C)(D) | A.B.C.D. | a)b)c)d)
- **answer_key_pages:** 381–395
- **answer_key_format:** grid | inline | end_of_chapter
- **has_figures:** yes | no
- **figure_position:** below_question | above_question | beside_question

## Subject Coverage
- **pages 1–45:** logical_reasoning
- **pages 46–120:** quantitative_reasoning
- **pages 121–200:** quantitative_reasoning
- **pages 201–280:** skip (not relevant to target exams)
- **pages 281–380:** logical_reasoning

## Sample Questions
- **has_samples:** yes
- **sample_pages:** 12, 67, 145

## Known Issues
- pages 78–82: poor scan quality, expect low OCR confidence
- pages 201–280: not relevant, mark entire range as skip
- double column layout begins page 121
- answer options sometimes wrap to next line pages 300–340

## Year Level
- **target_year:** 7–9
- **difficulty:** medium to hard

## Notes
Any other info useful for the pipeline. Free text.
```

### How each phase uses the briefing file

```
briefing.py        → parses the .md file into a structured dict
                     all phases call briefing.load(book_id)

phase1_normalise   → reads column_format → configures Docling reading order
                     reads relevant_pages → skips cover/index/appendix

phase2_classify    → reads subject_coverage page ranges as strong prior
                     if briefing says pages 46–120 are QR AND
                     classifier confidence >= BRIEFING_OVERRIDE_THRESHOLD
                     → use briefing label, skip API call (saves cost)
                     if confidence < threshold → use Claude, flag for review
                     reads sample_pages → marks as skip, no generation

phase3_figures     → reads figure_position → tunes proximity direction
                     (above_question → check y ABOVE, not below)

phase4_generate    → reads target_year and difficulty → injects into prompt
                     reads has_samples → skips sample/worked-example pages
                     reads answer_key_pages → skips those pages entirely

run_book.py        → REFUSES TO RUN if briefing file does not exist
```

### Pipeline refuses to run without briefing file — enforced in code

```python
def require_briefing(book_id: str, pdf_path: str) -> dict:
    briefing_path = pdf_path.replace('.pdf', '.md')
    if not os.path.exists(briefing_path):
        raise FileNotFoundError(
            f"\n\nBRIEFING FILE MISSING: {briefing_path}\n"
            f"You must create this file before running the pipeline.\n"
            f"Template: see CLAUDE.md → PDF METADATA BRIEFING FILES\n"
        )
    return briefing.load(briefing_path)
```

---

## PIPELINE ARCHITECTURE — 6 PHASES

```
/data/pdfs/<book_id>.pdf  +  /data/pdfs/<book_id>.md  (briefing)
    │
    ▼  run_book.py orchestrates all phases
    │
PHASE 1 — NORMALISE (Docling — runs locally on VM)
├── Reads briefing: column_format, relevant_pages
├── Converts PDF → markdown + page images + figure crops
├── Handles born-digital and scanned PDFs identically
├── Skips pages outside relevant_pages range
├── Records (x, y, width, height) for every element
└── Output:
    /data/scratch/<book_id>/pages/<page_n>.md
    /data/scratch/<book_id>/images/<page_n>.png
    /data/scratch/<book_id>/figures/<page_n>_fig_<n>.png
    /data/scratch/<book_id>/docling_output.json
    │
    ▼
PHASE 2 — CLASSIFY SUBJECT (Claude API — one call per page)
├── Reads briefing: subject_coverage ranges as strong prior
├── If briefing range matches AND confidence >= 0.85 → use briefing
├── Else → Claude API call with page markdown
├── Handles: answer_key, skip, theory-only, low-confidence flags
└── Output: /data/scratch/<book_id>/page_map.json
    │
    ▼  *** HUMAN CHECKPOINT — review page_map.json here ***
    │
PHASE 3 — FIGURE DETECTION + SORT (coordinate maths — no AI)
├── Reads briefing: figure_position hint
├── Uses Docling (x, y) positions — proximity threshold from config
├── One figure shared by multiple questions → linked to ALL of them
├── Sorts into text/ or figures/ per subject
└── Output:
    /data/output/<subject>/text/<q_id>.json
    /data/output/<subject>/figures/<q_id>.json
    /data/output/<subject>/figures/<q_id>_fig.png
    │
    ▼
PHASE 4 — GENERATE QUESTIONS (Claude API)
├── Reads briefing: target_year, difficulty → injected into prompt
├── TEXT TRACK: markdown → 8–10 new questions per page
├── FIGURE TRACK: figure PNG + originals → 3–5 new questions per figure
├── All questions: confidence score, review_status="pending"
├── API_DELAY_SECONDS between calls
├── Resumable: skips already-generated pages
└── Output: /data/output/<subject>/generated/<q_id>.json
    │
    ▼
PHASE 5 — HUMAN REVIEW UI
├── FastAPI server on VM: uvicorn review.server:app --host 0.0.0.0 --port 8000
├── Access from local machine: http://<VM_IP>:8000
├── Keyboard: A=Approve  R=Reject  E=Edit  ←→=Navigate
├── Figure shown above question when has_figure=True
├── Correct answer pre-highlighted green
├── High confidence (>=0.90) → fast-track queue
├── Low confidence (<0.90) → flagged queue
└── Approved → SQLite at /data/db/qbank.db
    │
    ▼
PHASE 6 — SYNC TO SUPABASE (manual trigger only)
├── python review/sync.py --dry-run   ← preview, no changes
├── python review/sync.py             ← execute sync
├── Upserts approved questions to Supabase
├── Uploads figures to Supabase Storage
└── Run only when a batch is ready to go live
```

---

## QUESTION JSON SCHEMA

```json
{
  "id": "uuid-v4",
  "subject": "quantitative_reasoning",
  "stem": "A shopkeeper bought a bicycle for $640 and sold it at 12.5% profit. What was the selling price?",
  "option_a": "$700",
  "option_b": "$720",
  "option_c": "$740",
  "option_d": "$760",
  "correct_answer": "B",
  "explanation": "12.5% of $640 = $80. Selling price = $640 + $80 = $720.",
  "writing_prompt": null,
  "year_level": "7-8",
  "difficulty": "medium",
  "topic": "percentages",
  "has_figure": false,
  "figure_path": null,
  "confidence": 0.95,
  "source_book": "rs_aggarwal_reasoning",
  "source_page": 23,
  "review_status": "pending",
  "created_at": "2025-05-15T10:30:00Z",
  "reviewed_at": null,
  "edited": false
}
```

**Strict rules — enforced everywhere:**
- `subject` → exactly one of 5 valid IDs
- `correct_answer` → exactly "A", "B", "C", or "D"
- `confidence` → float 0.0–1.0
- `review_status` → "pending" | "approved" | "rejected"
- `has_figure` → boolean, never null
- `figure_path` → null when has_figure=false
- `edited` → boolean, true if reviewer changed any field
- Writing questions → option_a/b/c/d and correct_answer are null,
  writing_prompt is populated instead

---

## DATABASE SCHEMA

```sql
-- db/schema.sql — source of truth, mirrors Supabase exactly

CREATE TABLE questions (
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

CREATE TABLE books (
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

CREATE INDEX idx_subject       ON questions(subject);
CREATE INDEX idx_review_status ON questions(review_status);
CREATE INDEX idx_confidence    ON questions(confidence);
CREATE INDEX idx_source_book   ON questions(source_book);
```

---

## PROJECT FOLDER STRUCTURE

```
qbank/                               ← GitHub repo root
├── CLAUDE.md                        ← READ EVERY SESSION
├── TESTS.md                         ← READ BEFORE ANY CODING
├── README.md
├── .gitignore
├── config.py                        ← all config, reads .env
├── requirements.txt
├── .env.example                     ← committed (no real values)
├── .env                             ← gitignored (real values, VM only)
│
├── pipeline/
│   ├── __init__.py
│   ├── briefing.py                  ← parses PDF .md briefing files
│   ├── phase1_normalise.py
│   ├── phase2_classify.py
│   ├── phase3_figures.py
│   ├── phase4_generate.py
│   └── run_book.py
│
├── review/
│   ├── server.py                    ← FastAPI, binds 0.0.0.0:8000
│   ├── sync.py
│   └── ui/
│       └── index.html               ← single-file review UI
│
├── db/
│   └── schema.sql                   ← committed (structure only, no data)
│
└── tests/
    ├── __init__.py
    ├── test_briefing.py             ← briefing parser tests
    ├── test_phase1_normalise.py
    ├── test_phase2_classify.py
    ├── test_phase3_figures.py
    ├── test_phase4_generate.py
    ├── test_review_api.py
    ├── test_sync.py
    └── fixtures/
        ├── sample_briefing.md
        ├── sample_qr_page.md
        ├── sample_lr_page.md
        ├── sample_sr_page.md
        ├── sample_rc_page.md
        ├── sample_wr_page.md
        ├── sample_theory_page.md
        ├── sample_answer_key_page.md
        ├── sample_mixed_page.md     ← figure shared by 3 questions
        ├── sample_figure.png
        ├── sample_docling_output.json
        └── sample_garbled_page.md
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
*.pdf
*.db
*.sqlite3

# Pipeline working files
/scratch/
/output/

# Figure images (except test fixture)
*.png
*.jpg
*.jpeg
!tests/fixtures/sample_figure.png

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

ANTHROPIC_API_KEY=your_anthropic_api_key_here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
SUPABASE_STORAGE_BUCKET=figures

DATA_DIR=/data
PDF_DIR=/data/pdfs
SCRATCH_DIR=/data/scratch
OUTPUT_DIR=/data/output
DB_PATH=/data/db/qbank.db
FIGURES_DIR=/data/db/figures

FIGURE_PROXIMITY_PX=150
CONFIDENCE_THRESHOLD=0.90
BRIEFING_OVERRIDE_THRESHOLD=0.85
QUESTIONS_PER_PAGE=8
FIGURE_QUESTIONS_PER_FIGURE=4
API_DELAY_SECONDS=2
CLAUDE_MODEL=claude-sonnet-4-6

REVIEW_HOST=0.0.0.0
REVIEW_PORT=8000
```

---

## SUBJECT CLASSIFICATION PROMPT

```
You are classifying pages from Australian selective school exam prep books.

BOOK CONTEXT (from briefing file):
{briefing_subject_coverage}
Layout: {briefing_column_format}

Classify this page into EXACTLY ONE of:
- quantitative_reasoning: maths, arithmetic, algebra, percentages, ratios,
  number patterns, sequences, word problems requiring calculation
- logical_reasoning: patterns, series, analogies, coding-decoding, puzzles,
  spatial reasoning, seating arrangements, deductive reasoning
- science_reasoning: biology, chemistry, physics, earth science,
  data interpretation, experiments, scientific method
- reading_comprehension: passages with questions, vocabulary, inference,
  main idea, author purpose, tone analysis
- writing: creative prompts, essay structure, grammar, punctuation,
  persuasive writing tasks

Special returns (not subjects):
- answer_key   → page is an answer grid or answer listing
- skip         → cover, contents, index, ads, instructions, not relevant range

Return ONLY valid JSON, no markdown, no explanation:
{
  "subject": "<subject_id or answer_key or skip>",
  "is_question_page": true,
  "confidence": 0.0-1.0,
  "reasoning": "<one sentence>"
}

PAGE CONTENT:
{page_markdown}
```

---

## GENERATION PROMPTS

### Text track
```
You are generating Australian selective school exam practice questions.
SUBJECT: {subject_name}
YEAR LEVEL: {year_level}
DIFFICULTY: {difficulty}

Study this page carefully — the style, difficulty, and question structure.
Generate exactly {n} NEW questions.

Rules:
- Answerable from knowledge alone, no figure needed
- Different numbers/names/contexts from originals
- Same difficulty as the examples shown
- Exactly 4 options (A B C D), exactly one correct
- Australian context ($AUD, km, Australian names where natural)
- One-sentence explanation for correct answer
- Do not copy or closely paraphrase any original question

Return ONLY a valid JSON array, no markdown, no preamble:
[{"stem":"...","option_a":"...","option_b":"...","option_c":"...",
"option_d":"...","correct_answer":"A|B|C|D","explanation":"...",
"topic":"...","difficulty":"easy|medium|hard","confidence":0.0}]

SOURCE PAGE:
{page_markdown}
```

### Figure track
```
You are generating Australian selective school exam questions from a figure.
SUBJECT: {subject_name}
YEAR LEVEL: {year_level}

The attached image is a figure from an exam prep book.
Generate exactly {n} NEW questions using this SAME figure.

Rules:
- Every question answerable purely from the figure
- Do not require knowledge not visible in the figure
- Do not repeat what original questions already asked
- Exactly 4 options (A B C D), exactly one correct
- Each stem must reference the figure ("the diagram", "the graph", "the table")
- One-sentence explanation for correct answer

ORIGINAL QUESTIONS THAT USED THIS FIGURE:
{original_questions}

Return ONLY a valid JSON array, no markdown, no preamble:
[{"stem":"...","option_a":"...","option_b":"...","option_c":"...",
"option_d":"...","correct_answer":"A|B|C|D","explanation":"...",
"topic":"...","difficulty":"easy|medium|hard","confidence":0.0}]
```

---

## KNOWN EDGE CASES — HANDLE EXPLICITLY

1. **One figure shared by multiple questions** — link to ALL nearby questions
2. **Answer key pages** — skip all phases, never generate from these
3. **Theory-only pages** — is_question_page=False, skip Phase 4
4. **Low-quality scan** — confidence < 0.5, flag for manual review, skip generation
5. **Writing subject** — no MCQ fields, writing_prompt field instead
6. **Double-column layout** — declared in briefing, passed to Docling
7. **Sample/worked example pages** — declared in briefing, skipped by Phase 4
8. **Pages outside relevant_pages range** — skipped by Phase 1
9. **Chapter boundary pages** — subject changes, Phase 2 reviews carefully
10. **Options wrapping to next line** — Docling may split option text, Phase 3 merges

---

## VM FIRST-TIME SETUP

```bash
# On the Linux VM

# 1. System packages
sudo apt update && sudo apt install -y python3.11 python3.11-venv git curl

# 2. Clone repo
git clone https://github.com/<your-username>/qbank.git ~/qbank
cd ~/qbank

# 3. Virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create data directories (VM-only, not in repo)
sudo mkdir -p /data/pdfs /data/scratch /data/output /data/db/figures
sudo chown -R $USER:$USER /data

# 6. Environment
cp .env.example .env
nano .env    # add real API keys

# 7. Initialise database
python -c "from db.init import create_tables; create_tables()"

# 8. Verify
python -c "import docling; print('Docling OK')"
python -c "import anthropic; print('Anthropic OK')"
pytest tests/test_schema.py -v
```

---

## DAILY WORKFLOW

```bash
# Pull latest code
cd ~/qbank && git pull && source .venv/bin/activate

# Add new book
cp /path/to/book.pdf /data/pdfs/<book_id>.pdf
nano /data/pdfs/<book_id>.md        # write briefing using template

# Run full pipeline
python pipeline/run_book.py --book_id <book_id>

# Run specific pages for testing
python pipeline/run_book.py --book_id <book_id> --pages 70 85

# Check progress
python pipeline/run_book.py --book_id <book_id> --status

# Start review server (background)
nohup uvicorn review.server:app --host 0.0.0.0 --port 8000 &

# Access review UI from local machine
# Browser → http://<VM_IP>:8000

# Sync when batch is ready
python review/sync.py --dry-run
python review/sync.py

# Push code changes
git add -A && git commit -m "description" && git push
```

---

## GIT BRANCH WORKFLOW

```bash
# Never commit directly to main
# One branch per feature/phase

git checkout -b feature/phase1-normalise
# ... build, test ...
git add pipeline/phase1_normalise.py tests/test_phase1_normalise.py
git commit -m "phase1: Docling normalisation, all 9 tests passing"
git push origin feature/phase1-normalise

# When complete and all tests green
git checkout main && git merge feature/phase1-normalise && git push
```

**Branch naming:**
`feature/briefing-parser` → `feature/phase1-normalise` →
`feature/phase2-classify` → `feature/phase3-figures` →
`feature/phase4-generate` → `feature/review-ui` → `feature/sync`

---

## SUPERPOWERS + UI UX PRO MAX — SETUP AND USAGE

These two tools are installed into Claude Code before writing any project code.
They are NOT optional. They change how Claude Code thinks and builds.

---

### 1. SUPERPOWERS (obra/superpowers) — 176k stars

**What it does:**
Superpowers is a complete software development methodology for your coding
agents. As soon as it sees you're building something, it doesn't jump into
writing code. Instead it steps back, asks what you're really trying to do,
refines a spec, writes a detailed implementation plan, then executes via
subagent-driven development — dispatching fresh subagents per task with
two-stage review (spec compliance, then code quality).

**The 7 skills it activates automatically:**
1. `brainstorming` — refines ideas before any code is written
2. `using-git-worktrees` — isolated workspace on new branch
3. `writing-plans` — bite-sized tasks (2–5 min each) with exact file paths
4. `subagent-driven-development` — fresh subagent per task, two-stage review
5. `test-driven-development` — RED→GREEN→REFACTOR, deletes code written before tests
6. `requesting-code-review` — reviews between tasks, critical issues block progress
7. `finishing-a-development-branch` — verifies tests, merge/PR options, cleanup

**Installation in Claude Code (do this once, on your local machine):**

```bash
# Option 1 — Official Claude Marketplace (recommended)
/plugin install superpowers@claude-plugins-official

# Option 2 — Superpowers own marketplace
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

**How it changes your workflow for this project:**

Without Superpowers: you say "build phase1_normalise.py" → Claude Code writes code immediately.

With Superpowers: you say "build phase1_normalise.py" →
- Claude Code asks clarifying questions about what it should do
- Writes a spec → you review and approve
- Writes an implementation plan broken into 2–5 min tasks
- Dispatches subagents to execute each task
- Reviews each subagent's output before continuing
- Only writes tests FIRST (red), then code (green), then refactors
- Can run autonomously for hours without deviating from the plan

**What to say at the start of each Claude Code session:**

```
Read CLAUDE.md and TESTS.md fully.
Then use the brainstorming skill to plan the next unchecked item
in the PROGRESS CHECKLIST before writing any code.
```

---

### 2. UI UX PRO MAX (nextlevelbuilder/ui-ux-pro-max-skill) — 78k stars

**What it does:**
An AI skill that provides design intelligence for building professional UI/UX
across multiple platforms. It automatically generates a complete design system
using a reasoning engine that runs 5 parallel searches across 161 industry
categories, 67 UI styles, 161 colour palettes, 57 font pairings, and 25 chart
types — then outputs a complete design system with recommended pattern, style,
colours, typography, key effects, anti-patterns to avoid, and a pre-delivery
checklist.

**Installation — two options:**

```bash
# Option 1 — Claude Marketplace (inside Claude Code)
/plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill
/plugin install ui-ux-pro-max@ui-ux-pro-max-skill

# Option 2 — CLI (run on your local machine, then it's available to Claude Code)
npm install -g uipro-cli
cd ~/qbank                      # your project root
uipro init --ai claude          # installs into .claude/skills/
```

**What it generates for YOUR review UI specifically:**

When you ask Claude Code to build `review/ui/index.html`, UI UX Pro Max will:

1. Detect the product type: "internal data annotation tool / admin dashboard"
2. Select the right style from 67 options — for an internal tool it will pick
   something like "Data-Dense Dashboard" or "Minimalism" — dark mode, monospace
   data fonts, high information density
3. Generate a design system with exact colours, typography, spacing
4. Apply anti-patterns: no AI purple gradients, no decorative noise, no emojis
   as icons, WCAG AA contrast minimum
5. Output code that looks like a professional tool, not a generic AI app

**How to trigger it for the review UI:**

```
Build the review UI at review/ui/index.html.
It is an internal data annotation tool for reviewing exam questions.
Users: solo reviewer on desktop.
Key interactions: keyboard-first (A/R/E keys), figure image display,
approve/reject/edit flow, progress stats sidebar.
Stack: single HTML file, vanilla JS, no framework, connects to FastAPI on port 8000.
```

UI UX Pro Max activates automatically when you mention UI/UX work — no slash
command needed in Claude Code.

**Persisting the design system across sessions:**

```bash
# Generate and save design system for the review UI
python3 .claude/skills/ui-ux-pro-max/scripts/search.py \
  "internal data annotation tool dark dashboard" \
  --design-system --persist -p "QBank Review UI"
```

This creates `design-system/MASTER.md` in your project — Claude Code reads this
at the start of any UI session so colours, fonts, and spacing stay consistent.

---

### HOW BOTH TOOLS WORK TOGETHER IN PRACTICE

```
You open Claude Code
    ↓
Say: "Read CLAUDE.md and TESTS.md. Use brainstorming skill.
      Next task: build briefing.py parser."
    ↓
SUPERPOWERS activates:
    - Asks clarifying questions about briefing.py requirements
    - Writes spec → you approve
    - Breaks into tasks: parse_basic_fields, parse_subject_coverage,
      get_subject_for_page, is_relevant_page, error handling
    - Dispatches subagent for task 1
    - Subagent writes FAILING TEST first (red)
    - Subagent writes minimal code to pass test (green)
    - Superpowers reviews: spec compliance, then code quality
    - Moves to task 2, repeat
    ↓
When you reach: "Build review/ui/index.html"
    ↓
UI UX PRO MAX activates:
    - Runs design system generator for "internal annotation tool"
    - Selects: dark mode, monospace data, minimal chrome, high density
    - Generates colour palette, typography, spacing system
    - Produces checklist: keyboard nav, WCAG AA, hover states, focus states
    ↓
SUPERPOWERS takes the design system output and:
    - Writes spec for the HTML file
    - Breaks into tasks: layout skeleton, question display, action bar,
      sidebar stats, figure display, keyboard handlers, API integration
    - Builds each piece with TDD
    - Reviews output between each task
    ↓
Result: production-grade review UI built systematically,
        not in one chaotic dump
```

---

### QUICK INSTALL CHECKLIST (do before first Claude Code session)

```bash
# On your local machine where Claude Code runs

# 1. Install Superpowers
# In Claude Code terminal:
/plugin install superpowers@claude-plugins-official

# 2. Install UI UX Pro Max CLI
npm install -g uipro-cli

# 3. In your project folder (after cloning the repo)
cd ~/qbank
uipro init --ai claude

# 4. Verify both installed
ls .claude/skills/          # should show ui-ux-pro-max folder
# Superpowers shows automatically when you start a Claude Code session

# 5. Generate and persist design system for review UI
python3 .claude/skills/ui-ux-pro-max/scripts/search.py \
  "internal data annotation tool dark dashboard keyboard-driven" \
  --design-system --persist -p "QBank Review UI"
```

---

## DEVELOPMENT RULES

1. Read TESTS.md before writing any code
2. Briefing file must exist — run_book.py enforces this, no exceptions
3. Never modify a phase without testing on 5 real pages first
4. Always review page_map.json after Phase 2 before running Phase 3
5. Never auto-approve questions — humans only set approved
6. API_DELAY_SECONDS between every Claude API call — no tight loops
7. Every phase is resumable — skip already-processed pages
8. All config in config.py — no magic numbers anywhere
9. Validate every LLM JSON response before writing to disk
10. Commit only when all tests for that phase are green
11. Never commit to main directly — feature branches only
12. Never commit .env or any API key — ever

---

## QUICK REFERENCE

```bash
# Pipeline
python pipeline/run_book.py --book_id <id>
python pipeline/run_book.py --book_id <id> --pages 70 85
python pipeline/run_book.py --book_id <id> --status
python pipeline/phase2_classify.py --book_id <id>   # run single phase

# Review
uvicorn review.server:app --host 0.0.0.0 --port 8000
python review/sync.py --dry-run
python review/sync.py

# Tests
pytest tests/ -v
pytest tests/test_briefing.py -v
pytest tests/test_phase2_classify.py -v

# Git
git checkout -b feature/<name>
git add -A && git commit -m "<msg>" && git push
```

---

## PROGRESS CHECKLIST (update each session)

- [ ] GitHub repo created and cloned to VM
- [ ] VM setup complete (venv, /data dirs, .env configured)
- [ ] Project folder structure created
- [ ] .gitignore committed
- [ ] requirements.txt committed
- [ ] config.py committed
- [ ] .env.example committed
- [ ] schema.sql committed and DB initialised on VM
- [ ] briefing.py parser written and tested
- [ ] phase1_normalise.py written and tested
- [ ] phase2_classify.py written and tested
- [ ] phase3_figures.py written and tested
- [ ] phase4_generate.py written and tested
- [ ] run_book.py orchestrator written and tested
- [ ] review/server.py written and tested
- [ ] review/ui/index.html built
- [ ] review/sync.py written and tested
- [ ] All tests passing
- [ ] First book processed end-to-end on VM
- [ ] First batch synced to Supabase

---

## CURRENT STATUS

**Last worked on:** Not started
**Next task:** Create GitHub repo → VM setup → project structure → briefing.py parser
**Blockers:** None
**Notes:** —
