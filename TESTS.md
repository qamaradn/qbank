# QBANK — TEST PLAN
## Read this before writing any code for any phase.
## Every feature needs a failing test BEFORE implementation.
## Red → Green → Refactor. Never skip the red step.

---

## TESTING PHILOSOPHY

This is a data pipeline. The most dangerous failure mode is **silent corruption** —
the pipeline runs without errors but produces wrong output. Bad questions reach
the review UI, get approved, and reach students.

Every test checks **actual output content**, not just that the function ran.
A function returning an empty list without raising an exception is a failure.
Test for that explicitly.

**No fixtures directory.** Tests create all their own data using `tmp_path`.
Do not add a `tests/fixtures/` folder. Keep tests self-contained.

**No mocking the database.** Tests use real SQLite via `tmp_path`. No mocks.
Schema is applied from `db/schema.sql` in test setup.

**Test categories:**
- `UNIT` — one function, no API calls, no real file I/O
- `INTEGRATION` — full phase with real tmp files
- `CONTRACT` — output schema is exactly correct (shape, types, values)
- `EDGE` — known difficult cases from CLAUDE.md
- `REGRESSION` — previously fixed bugs stay fixed

---

## BRIEFING PARSER TESTS
### File: tests/test_briefing.py
### 7 tests — all passing

```
TEST-B-01 [UNIT] valid briefing file loads basic fields
  Given: briefing .md with file, relevant_pages, target_year, difficulty
  When:  briefing.load(path) is called
  Then:  returns dict with all fields, no exception

TEST-B-02 [CONTRACT] subject_coverage is a list of page-range dicts
  Given: briefing with 3 subject ranges
  When:  briefing.load() is called
  Then:  result["subject_coverage"] is list of dicts
         each item has: pages_start, pages_end, subject
         subject is one of 5 valid subjects OR "skip"

TEST-B-03 [UNIT] get_subject_for_page returns correct subject
  Given: briefing with QR on pages 45–54, SR on pages 61–74
  When:  get_subject_for_page(data, 50) called
  Then:  returns "quantitative_reasoning"
  When:  get_subject_for_page(data, 65) called
  Then:  returns "science_reasoning"

TEST-B-04 [UNIT] is_relevant_page returns correct booleans
  Given: briefing with relevant_pages 45–74
  When:  is_relevant_page(data, 50) called
  Then:  returns True
  When:  is_relevant_page(data, 10) called
  Then:  returns False

TEST-B-05 [EDGE] missing briefing file raises FileNotFoundError
  Given: path to a .md file that does not exist
  When:  briefing.load(nonexistent_path) is called
  Then:  raises FileNotFoundError

TEST-B-06 [EDGE] invalid subject in coverage raises ValueError
  Given: briefing with subject_coverage containing "mathematics"
  When:  briefing.load() is called
  Then:  raises ValueError (not a valid subject)

TEST-B-07 [UNIT] skip is valid in subject_coverage
  Given: briefing with one range marked "skip"
  When:  briefing.load() is called
  Then:  no exception raised
         get_subject_for_page returns "skip" for that range
```

---

## PHASE 1 — PDF → PNG NORMALISATION
### File: tests/test_phase1_normalise.py
### Uses pdf2image. Tests are fast (tiny test PDFs or mocked pdf2image).

```
TEST-P1-01 [UNIT] missing briefing file raises FileNotFoundError
  Given: valid PDF path but no matching .md briefing file
  When:  phase1_normalise.run(book_id, pdf_path, briefing_path=...) called
  Then:  raises FileNotFoundError mentioning the briefing path

TEST-P1-02 [INTEGRATION] output PNGs created in correct subject subfolders
  Given: briefing says pages 45–54 are quantitative_reasoning
  When:  phase1 extracts pages
  Then:  PNGs at scratch/{book_id}/images/quantitative_reasoning/{book_id}_*_p<n>.png
         date in filename is today (DDMMYY format)

TEST-P1-03 [CONTRACT] PNG naming convention: {book_id}_{DDMMYY}_p{n}.png
  Given: book_id="test_book", page_number=45, subject="science_reasoning"
  When:  PNG written
  Then:  filename matches pattern test_book_DDMMYY_p45.png (regex match)

TEST-P1-04 [UNIT] pages outside relevant_pages range are skipped
  Given: briefing with relevant_pages 45–74
         PDF has pages 1–100
  When:  phase1 runs
  Then:  only pages 45–74 extracted
         pages 1–44 and 75–100 not extracted

TEST-P1-05 [UNIT] pages with subject "skip" are not extracted
  Given: briefing with pages 81–90 marked as skip
  When:  phase1 runs
  Then:  no PNGs created for pages 81–90

TEST-P1-06 [INTEGRATION] stats dict returned with correct counts
  Given: 10 relevant pages (2 marked skip, 8 subject pages)
  When:  phase1 returns
  Then:  stats["extracted"] == 8
         stats["skipped"] == 2
```

---

## PHASE 2 — BRIEFING → PAGE MAP
### File: tests/test_phase2_classify.py
### 3 tests — all passing. No API calls. Pure briefing lookup.

```
TEST-P2-01 [INTEGRATION] run() creates page_map.json
  Given: valid briefing with 3 subject ranges
         scratch/{book_id}/ directory exists
  When:  phase2_classify.run(book_id, briefing_path, scratch_dir) called
  Then:  scratch/{book_id}/page_map.json exists
         file is valid JSON

TEST-P2-02 [CONTRACT] page_map subjects match briefing
  Given: briefing with pages 45–54 quantitative_reasoning,
                            pages 55–60 reading_comprehension,
                            pages 61–74 science_reasoning
  When:  page_map.json parsed
  Then:  pages list has entries for all 30 relevant pages
         page 50 has subject="quantitative_reasoning"
         page 58 has subject="reading_comprehension"
         page 65 has subject="science_reasoning"

TEST-P2-03 [CONTRACT] page_map.json is persisted to disk and reloadable
  Given: phase2 has run
  When:  page_map.json read from disk
  Then:  valid JSON with "pages" key
         each entry has: page_number (int), subject (str)
```

---

## PHASE 3 — QUESTION GENERATION (Gemini Vision)
### File: tests/test_phase3_generate.py
### 8 tests — all passing. Gemini API is mocked.

```
TEST-P3-01 [CONTRACT] _build_question returns correct schema
  Given: valid raw dict from Gemini
  When:  _build_question(raw, subject, book_id, page_n, passage) called
  Then:  returns dict with all required fields:
           id (uuid), subject, stem, option_a-d, correct_answer,
           explanation, topic, difficulty, confidence,
           source_book, source_page, source_page_description,
           passage, review_status="pending", created_at

TEST-P3-02 [EDGE] invalid correct_answer defaults to "A"
  Given: raw dict with correct_answer="E"
  When:  _build_question() called
  Then:  returned question has correct_answer="A"

TEST-P3-03 [EDGE] invalid difficulty defaults to "medium"
  Given: raw dict with difficulty="easy"
  When:  _build_question() called
  Then:  returned question has difficulty="medium"

TEST-P3-04 [EDGE] empty stem returns None
  Given: raw dict with stem=""
  When:  _build_question() called
  Then:  returns None (question discarded)

TEST-P3-05 [UNIT] _strip_fences passes through clean JSON unchanged
  Given: raw text = '[{"a":1}]' (no fences)
  When:  _strip_fences() called
  Then:  returns '[{"a":1}]' unchanged

TEST-P3-06 [UNIT] _strip_fences removes ```json ... ``` wrapper
  Given: raw text = '```json\n[{"a":1}]\n```'
  When:  _strip_fences() called
  Then:  returns '[{"a":1}]'

TEST-P3-07 [UNIT] _strip_fences removes plain ``` ... ``` wrapper
  Given: raw text = '```\n[{"a":1}]\n```'
  When:  _strip_fences() called
  Then:  result contains '[{"a":1}]'

TEST-P3-08 [INTEGRATION] generate_page calls Gemini and writes JSON
  Given: mock Gemini model returning 10 valid question dicts
         real PNG file (PIL-created 100x100 white image)
  When:  generate_page(page_n=5, ..., model=mock_model) called
  Then:  returns list of 10 questions
         output/{subject}/generated/{book_id}_p5.json exists
         JSON contains 10 questions all with review_status="pending"
```

---

## PHASE 4 — DEDUP + LOAD
### File: tests/test_phase4_load.py
### 7 tests — all passing. Uses real SQLite via tmp_path.

```
TEST-P4-01 [UNIT] _is_duplicate returns True for exact match
  Given: existing_stems = ["What is 2+2?"]
         new_stem = "What is 2+2?"
  When:  _is_duplicate(new_stem, existing_stems, 0.85) called
  Then:  returns True

TEST-P4-02 [UNIT] _is_duplicate returns False for clearly different stems
  Given: existing_stems = ["What is 2+2?"]
         new_stem = "Solve for x when 3x = 9."
  When:  _is_duplicate() called
  Then:  returns False

TEST-P4-03 [UNIT] _is_duplicate returns False for dissimilar near-matches
  Given: existing_stems = ["What is 15% of 240?"]
         new_stem = "Name the largest river in Australia."
  When:  _is_duplicate() called
  Then:  returns False

TEST-P4-04 [INTEGRATION] load_book inserts non-duplicate questions
  Given: 5 distinct questions in generated JSON
         empty DB
  When:  load_book(book_id, output_dir, db_path) called
  Then:  stats["inserted"] == 5
         stats["duplicate"] == 0
         SELECT COUNT(*) FROM questions == 5

TEST-P4-05 [INTEGRATION] load_book skips exact duplicate stems
  Given: question with stem "What is the square root of 144?" already in DB
         new JSON has same stem
  When:  load_book() called
  Then:  stats["inserted"] == 0
         stats["duplicate"] == 1
         DB still has exactly 1 row

TEST-P4-06 [CONTRACT] all loaded questions have review_status="pending"
  Given: 3 questions inserted by load_book
  When:  SELECT review_status FROM questions
  Then:  all rows == "pending"
         no auto-approved questions

TEST-P4-07 [EDGE] load_book with no matching JSON files returns zero stats
  Given: output dir is empty (no generated JSON for this book_id)
  When:  load_book("nonexistent_book", ...) called
  Then:  stats["inserted"] == 0
         no error raised
```

---

## REVIEW API TESTS
### File: tests/test_review_api.py
### 14 tests — all passing. Uses FastAPI TestClient + tmp SQLite.

```
TEST-R-01 [INTEGRATION] GET /questions/next returns pending question
  Given: SQLite has a pending question with source_page_description
  When:  GET /questions/next called
  Then:  200 with review_status="pending"
         response includes "source_page_description" field

TEST-R-02 [INTEGRATION] GET /questions/next returns 404 when empty
  Given: no pending questions in SQLite
  When:  GET /questions/next called
  Then:  404

TEST-R-03 [INTEGRATION] POST approve sets review_status and reviewed_at
  Given: pending question with known id
  When:  POST /questions/{id}/approve called
  Then:  200
         SQLite: review_status="approved", reviewed_at is non-null

TEST-R-04 [INTEGRATION] POST reject sets review_status
  Given: pending question
  When:  POST /questions/{id}/reject called
  Then:  200
         SQLite: review_status="rejected"

TEST-R-05 [INTEGRATION] POST edit updates fields, sets edited=1, approves
  Given: pending question
         payload: {"stem": "new stem", "correct_answer": "C"}
  When:  POST /questions/{id}/edit called
  Then:  200
         stem updated, correct_answer="C", edited=1, review_status="approved"

TEST-R-06 [CONTRACT] edit rejects invalid correct_answer
  Given: payload with correct_answer="E"
  When:  POST /questions/{id}/edit called
  Then:  422 — question NOT modified

TEST-R-07 [INTEGRATION] GET /stats returns accurate counts
  Given: 10 approved (12 total including 2 edited), 3 rejected, 50 pending
  When:  GET /stats called
  Then:  {approved:12, rejected:3, edited:2, pending:50, total:65}

TEST-R-08 [INTEGRATION] GET /questions filters by subject
  Given: 3 science_reasoning, 5 verbal_reasoning questions
  When:  GET /questions?subject=science_reasoning called
  Then:  returns exactly 3, all science_reasoning

TEST-R-09 [INTEGRATION] GET /questions filters by status
  Given: 4 pending, 6 approved
  When:  GET /questions?status=pending called
  Then:  returns exactly 4

TEST-R-10 [INTEGRATION] GET /health returns 200
  When:  GET /health called
  Then:  200

TEST-R-11 [INTEGRATION] DELETE /questions/{id} removes the row
  Given: pending question with known id
  When:  DELETE /questions/{id} called
  Then:  200
         row no longer in SQLite

TEST-R-12 [INTEGRATION] POST /questions/bulk-approve approves by confidence
  Given: 5 questions with confidence=0.95, 3 with confidence=0.75
  When:  POST /questions/bulk-approve?min_confidence=0.90 called
  Then:  {"approved": 5} returned
         only the high-confidence questions approved

TEST-R-13 [INTEGRATION] GET /stats/topics returns per-subject topic breakdown
  Given: 3 approved "percentages" questions, 2 pending "percentages" questions
  When:  GET /stats/topics called
  Then:  data["quantitative_reasoning"]["percentages"]["approved"] == 3
         data["quantitative_reasoning"]["percentages"]["pending"] == 2

TEST-R-14 [CONTRACT] /questions/next response includes source_page_description
  Given: question inserted with source_page_description="A basic arithmetic page."
  When:  GET /questions/next called
  Then:  response["source_page_description"] == "A basic arithmetic page."
```

---

## REVIEW UI TESTS
### File: tests/test_review_ui.py
### 22 tests — all passing. Static analysis of review/ui/index.html.
### No Playwright required — tests parse and inspect the HTML/JS/CSS source.

```
TEST-UI-01  HTML is valid and has a body element
TEST-UI-02  design-system/MASTER.md file exists
TEST-UI-03  dark mode background set as default (not a toggle)
TEST-UI-04  CSS class for correct-answer green highlighting is defined
TEST-UI-05  figure display logic exists in JS (show img when passage/figure present)
TEST-UI-06  logic to hide image when figure is null exists in JS
TEST-UI-07  keyboard shortcut A triggers approve
TEST-UI-08  keyboard shortcut R triggers reject
TEST-UI-09  keyboard shortcut E enters edit mode
TEST-UI-10  arrow key navigation logic in JS
TEST-UI-11  progress bar element exists
TEST-UI-12  stats sidebar element exists
TEST-UI-13  subject filter logic in JS
TEST-UI-14  confidence badge styling defined in CSS
TEST-UI-15  edit mode save calls /edit endpoint
TEST-UI-16  edit mode cancel restores original values
TEST-UI-17  CSS focus ring styles defined
TEST-UI-18  dark theme text contrast values in CSS
TEST-UI-19  no emoji characters used as UI icons
TEST-UI-20  keyboard-only workflow is completable (A/R/E all wired up)
TEST-UI-21  no AI purple/pink gradient backgrounds in CSS
TEST-UI-22  monospace font class applied to data elements (confidence, page, source)
```

---

## RUN_BOOK ORCHESTRATOR TESTS
### File: tests/test_run_book.py (if needed)
### These may be added to cover orchestration logic: --status flag, --test-pages,
### briefing check enforced before phases start, etc.

```
TEST-RB-01 [UNIT] run() raises if briefing file missing
TEST-RB-02 [UNIT] --test-pages skips Phase 1 and Phase 2 when PNGs exist
TEST-RB-03 [INTEGRATION] --status returns counts from DB + scratch + output
TEST-RB-04 [CONTRACT] get_status() returns dict with expected keys
```

---

## TEST EXECUTION ORDER

```bash
# Run everything
pytest tests/ -v

# Run individual files
pytest tests/test_briefing.py -v
pytest tests/test_phase2_classify.py -v
pytest tests/test_phase3_generate.py -v
pytest tests/test_phase4_load.py -v
pytest tests/test_review_api.py -v
pytest tests/test_review_ui.py -v

# Quick count check
pytest tests/ --collect-only 2>&1 | tail -3
# Should show: 61 tests collected
```

**Current test count: 61 (all green)**

| File | Tests |
|---|---|
| test_briefing.py | 7 |
| test_phase2_classify.py | 3 |
| test_phase3_generate.py | 8 |
| test_phase4_load.py | 7 |
| test_review_api.py | 14 |
| test_review_ui.py | 22 |
| **Total** | **61** |

---

## DEFINITION OF DONE FOR EACH PHASE

A phase is NOT done until ALL of the following:

**Tests:**
- [ ] All automated tests for that phase are GREEN
- [ ] `pytest tests/ -v` passes with no failures anywhere
- [ ] No test was written AFTER the implementation — red must come first

**Code quality:**
- [ ] No hardcoded magic numbers — use `os.environ.get(...)` or constants
- [ ] Every LLM JSON response validated before writing to disk
- [ ] Phase is resumable — skips already-processed output

**Manual verification:**
- [ ] Phase run on at least one real page/file on VM
- [ ] Output files manually inspected (open them, read them)
- [ ] Edge cases from CLAUDE.md verified

**Git:**
- [ ] Committed on feature branch with message: `feat(phase-N): description, N tests passing`
- [ ] Merged to main, never committed directly to main
