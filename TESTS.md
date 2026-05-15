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

**Test categories:**
- `UNIT` — one function, no API calls, no real file I/O
- `INTEGRATION` — full phase with real fixture files
- `CONTRACT` — output schema is exactly correct (shape, types, values)
- `EDGE` — known difficult cases from CLAUDE.md
- `REGRESSION` — previously fixed bugs stay fixed

---

## FIXTURES REQUIRED

Create these in `tests/fixtures/` before running any tests.
Use real content from actual books — synthetic fixtures miss real problems.

| File | Description |
|---|---|
| `sample_briefing.md` | Complete briefing file using the template from CLAUDE.md |
| `sample_briefing_minimal.md` | Briefing with only required fields, optional fields absent |
| `sample_briefing_double_col.md` | Briefing declaring double_column layout |
| `sample_qr_page.md` | Docling markdown of a Quantitative Reasoning page |
| `sample_lr_page.md` | Docling markdown of a Logical Reasoning page |
| `sample_sr_page.md` | Docling markdown of a Science Reasoning page |
| `sample_rc_page.md` | Docling markdown of a Reading Comprehension page |
| `sample_wr_page.md` | Docling markdown of a Writing page |
| `sample_theory_page.md` | Explanation/theory page with no questions |
| `sample_answer_key_page.md` | Answer key grid page |
| `sample_mixed_page.md` | Page where one figure is near three questions |
| `sample_figure.png` | Real geometry or science figure image |
| `sample_docling_output.json` | Real Docling JSON output for a 5-page section |
| `sample_garbled_page.md` | Badly OCR'd text simulating low-quality scan |

---

## BRIEFING PARSER TESTS
### File: tests/test_briefing.py
### This is Phase 0 — build and test briefing.py before any pipeline phase.

```
TEST-B-01 [UNIT] valid briefing file parses without error
  Given: sample_briefing.md fixture
  When:  briefing.load(path) is called
  Then:  returns a dict
         no exception raised

TEST-B-02 [CONTRACT] parsed briefing has all required fields
  Given: sample_briefing.md fixture
  When:  briefing.load(path) is called
  Then:  result contains keys:
           file, total_pages, relevant_pages_start, relevant_pages_end,
           column_format, has_figures, figure_position,
           subject_coverage (list of dicts),
           target_year, difficulty,
           sample_pages (list),
           answer_key_pages_start, answer_key_pages_end,
           known_issues (list)

TEST-B-03 [CONTRACT] subject_coverage is a list of page-range dicts
  Given: sample_briefing.md with 4 subject ranges
  When:  briefing.load() is called
  Then:  result["subject_coverage"] is a list of length 4
         each item has: pages_start, pages_end, subject
         subject is one of 5 valid subjects OR "skip"

TEST-B-04 [CONTRACT] column_format is one of valid values
  Given: any valid briefing file
  When:  briefing.load() is called
  Then:  result["column_format"] in ["single_column","double_column","mixed"]

TEST-B-05 [UNIT] get_subject_for_page returns correct subject
  Given: briefing with QR on pages 46–120, LR on pages 121–200
  When:  briefing.get_subject_for_page(briefing_data, page=80) is called
  Then:  returns "quantitative_reasoning"
  When:  briefing.get_subject_for_page(briefing_data, page=150) is called
  Then:  returns "logical_reasoning"

TEST-B-06 [UNIT] get_subject_for_page returns "skip" for skip ranges
  Given: briefing with pages 201–280 marked as skip
  When:  briefing.get_subject_for_page(briefing_data, page=240) is called
  Then:  returns "skip"

TEST-B-07 [UNIT] get_subject_for_page returns None for pages outside all ranges
  Given: briefing covers pages 45–380
  When:  briefing.get_subject_for_page(briefing_data, page=400) is called
  Then:  returns None (not an error, not "skip")

TEST-B-08 [UNIT] is_relevant_page correctly identifies in-range pages
  Given: briefing with relevant_pages 45–380
  When:  briefing.is_relevant_page(briefing_data, page=100) is called
  Then:  returns True
  When:  briefing.is_relevant_page(briefing_data, page=10) is called
  Then:  returns False

TEST-B-09 [UNIT] is_answer_key_page correctly identifies answer key pages
  Given: briefing with answer_key_pages 381–395
  When:  briefing.is_answer_key_page(briefing_data, page=385) is called
  Then:  returns True
  When:  briefing.is_answer_key_page(briefing_data, page=100) is called
  Then:  returns False

TEST-B-10 [UNIT] is_sample_page correctly identifies sample pages
  Given: briefing with sample_pages: [12, 67, 145]
  When:  briefing.is_sample_page(briefing_data, page=67) is called
  Then:  returns True
  When:  briefing.is_sample_page(briefing_data, page=68) is called
  Then:  returns False

TEST-B-11 [EDGE] missing briefing file raises FileNotFoundError
  Given: path to a .md file that does not exist
  When:  briefing.load(nonexistent_path) is called
  Then:  raises FileNotFoundError
         message mentions the missing path
         message mentions the template in CLAUDE.md

TEST-B-12 [EDGE] minimal briefing with only required fields parses correctly
  Given: sample_briefing_minimal.md (only required fields, no optional)
  When:  briefing.load() is called
  Then:  returns dict without error
         optional fields have sensible defaults:
           sample_pages → []
           known_issues → []
           figure_position → "below_question"

TEST-B-13 [EDGE] invalid subject in coverage raises ValueError
  Given: briefing with subject_coverage containing subject="mathematics"
  When:  briefing.load() is called
  Then:  raises ValueError
         message says "mathematics" is not a valid subject
         message lists the 5 valid subject IDs

TEST-B-14 [UNIT] double_column format is parsed correctly
  Given: sample_briefing_double_col.md
  When:  briefing.load() is called
  Then:  result["column_format"] == "double_column"

TEST-B-15 [REGRESSION] page range with dash variations parses correctly
  Given: briefing file with "pages 46–120" (en-dash, not hyphen)
  When:  briefing.load() is called
  Then:  parses correctly, returns pages_start=46, pages_end=120
         does NOT crash on en-dash vs hyphen difference
```

---

## PHASE 1 — DOCLING NORMALISATION TESTS
### File: tests/test_phase1_normalise.py

```
TEST-P1-01 [UNIT] valid PDF path with valid briefing returns no error
  Given: valid PDF + matching .md briefing file
  When:  phase1_normalise.run(book_id, pdf_path) is called
  Then:  function completes without exception

TEST-P1-02 [UNIT] missing briefing file raises FileNotFoundError
  Given: valid PDF but no matching .md briefing file
  When:  phase1_normalise.run(book_id, pdf_path) is called
  Then:  raises FileNotFoundError with clear message about missing briefing

TEST-P1-03 [INTEGRATION] output files are created for each relevant page
  Given: 5-page PDF, briefing says pages 2–4 are relevant
  When:  phase1_normalise.run() completes
  Then:  /data/scratch/<book_id>/pages/ has 3 .md files (pages 2, 3, 4)
         /data/scratch/<book_id>/images/ has 3 .png files
         page 1 and page 5 are NOT processed (outside relevant range)

TEST-P1-04 [CONTRACT] docling_output.json has required structure
  Given: any processed book
  When:  docling_output.json is parsed
  Then:  has keys: pages, total_pages, book_id
         each page has: page_number, elements, markdown_path, image_path
         each element has: type, text, x, y, width, height

TEST-P1-05 [CONTRACT] markdown output is valid UTF-8 and non-empty
  Given: any processed page
  When:  .md file is read
  Then:  valid UTF-8 encoding
         not empty
         contains at least one word

TEST-P1-06 [INTEGRATION] figures extracted when present
  Given: PDF page known to have a diagram
  When:  phase1 completes
  Then:  figures/ folder contains at least one PNG
         figure PNG is valid image (non-zero bytes)
         docling_output.json element of type "figure" has figure_path set

TEST-P1-07 [UNIT] resumable — already-processed pages are skipped
  Given: phase1 already ran for a book
  When:  phase1.run() is called again
  Then:  existing files not overwritten
         log shows "skipping already processed page N"
         runtime significantly shorter than first run

TEST-P1-08 [EDGE] scanned PDF handled without error
  Given: image-based PDF (no selectable text)
  When:  phase1.run() is called
  Then:  completes without error
         OCR applied, markdown files created
         markdown is not empty

TEST-P1-09 [UNIT] book_id with invalid characters raises ValueError
  Given: book_id = "my book! (2025)"
  When:  phase1.run() is called
  Then:  raises ValueError
         message says book_id must be alphanumeric with underscores only
```

---

## PHASE 2 — SUBJECT CLASSIFIER TESTS
### File: tests/test_phase2_classify.py

```
TEST-P2-01 [CONTRACT] classifier returns correct subject for each of 5 subjects
  Given: sample_qr_page.md → expect "quantitative_reasoning"
         sample_lr_page.md → expect "logical_reasoning"
         sample_sr_page.md → expect "science_reasoning"
         sample_rc_page.md → expect "reading_comprehension"
         sample_wr_page.md → expect "writing"
  When:  classify_page(markdown, briefing_data) is called for each
  Then:  result["subject"] matches expected value for each

TEST-P2-02 [CONTRACT] result always has required fields with correct types
  Given: any page markdown
  When:  classify_page() is called
  Then:  result["subject"] is a string
         result["confidence"] is float between 0.0 and 1.0
         result["is_question_page"] is bool (True or False, not truthy string)
         result["reasoning"] is non-empty string

TEST-P2-03 [CONTRACT] subject is always one of 7 valid return values
  Given: any page markdown
  When:  classify_page() is called
  Then:  result["subject"] in [
           "quantitative_reasoning", "logical_reasoning",
           "science_reasoning", "reading_comprehension",
           "writing", "answer_key", "skip"
         ]
         NEVER any other value

TEST-P2-04 [EDGE] answer key page returns "answer_key"
  Given: sample_answer_key_page.md
  When:  classify_page() is called
  Then:  result["subject"] == "answer_key"

TEST-P2-05 [EDGE] theory page sets is_question_page to False
  Given: sample_theory_page.md
  When:  classify_page() is called
  Then:  result["is_question_page"] == False
         result["subject"] is still a valid subject (not null)

TEST-P2-06 [UNIT] briefing prior overrides classifier when confidence high
  Given: briefing says pages 46–120 are "quantitative_reasoning"
         page 80 content looks vaguely like logical reasoning
         BUT briefing coverage confidence >= BRIEFING_OVERRIDE_THRESHOLD (0.85)
  When:  classify_page(markdown, briefing_data, page_number=80) is called
  Then:  result["subject"] == "quantitative_reasoning" (briefing wins)
         no API call made (cost saved)
         result["reasoning"] mentions "briefing override"

TEST-P2-07 [UNIT] briefing prior does NOT override when page outside coverage range
  Given: briefing covers pages 46–380
         page_number=400 (outside range)
  When:  classify_page(markdown, briefing_data, page_number=400) is called
  Then:  API call IS made
         classification from Claude used, not briefing

TEST-P2-08 [INTEGRATION] page_map.json written correctly
  Given: 10-page book processed by phase1
  When:  phase2_classify.run(book_id) completes
  Then:  page_map.json exists, is valid JSON
         has exactly one entry per processed page
         each entry: page_number, subject, confidence, is_question_page

TEST-P2-09 [UNIT] resumable — already-classified pages not re-called
  Given: page_map.json has entries for pages 1–5
  When:  phase2_classify.run() called again
  Then:  pages 1–5 NOT re-classified (no API call)
         new pages classified normally

TEST-P2-10 [EDGE] garbled OCR page flags low confidence
  Given: sample_garbled_page.md
  When:  classify_page() is called
  Then:  result["confidence"] < 0.5
         page flagged in page_map.json as needs_manual_review=True

TEST-P2-11 [UNIT] empty markdown raises ValueError
  Given: markdown = ""
  When:  classify_page("", briefing_data) is called
  Then:  raises ValueError("Cannot classify empty page")
```

---

## PHASE 3 — FIGURE DETECTOR TESTS
### File: tests/test_phase3_figures.py

```
TEST-P3-01 [UNIT] question with no nearby figure returns has_figure=False
  Given: question at y=200, no figures on page
  When:  detect_figure(question, page_elements, threshold=150) called
  Then:  returns has_figure=False, figure_path=None

TEST-P3-02 [UNIT] question with figure within threshold returns has_figure=True
  Given: question at y=200, figure at y=280 (80px below — within 150)
  When:  detect_figure() called
  Then:  returns has_figure=True, figure_path is non-null string

TEST-P3-03 [UNIT] figure at exactly threshold distance is included (inclusive)
  Given: question at y=200, figure at y=350 (exactly 150px)
  When:  detect_figure() called with threshold=150
  Then:  returns has_figure=True

TEST-P3-04 [UNIT] figure at threshold+1 is NOT included
  Given: question at y=200, figure at y=351 (151px)
  When:  detect_figure() called with threshold=150
  Then:  returns has_figure=False

TEST-P3-05 [EDGE] one figure shared by three questions — all linked
  Given: sample_mixed_page fixture
         figure at y=300, Q14 at y=200, Q15 at y=250, Q16 at y=380
         all within 150px of figure
  When:  phase3 processes the page
  Then:  Q14, Q15, Q16 all have has_figure=True
         all three reference the same figure_path
         figure PNG exists only ONCE (not duplicated)

TEST-P3-06 [UNIT] figure_position hint from briefing affects detection direction
  Given: briefing says figure_position="above_question"
         question at y=300, figure at y=200 (100px ABOVE)
  When:  detect_figure() called with briefing hint
  Then:  returns has_figure=True (checks above, not only below)

TEST-P3-07 [INTEGRATION] text-only questions go to text/ folder
  Given: page with 5 questions, none near a figure
  When:  phase3_figures.run(book_id) completes
  Then:  5 JSON files in /data/output/<subject>/text/
         0 files in /data/output/<subject>/figures/

TEST-P3-08 [INTEGRATION] figure-linked questions go to figures/ folder with PNG
  Given: page with 3 questions near a figure
  When:  phase3_figures.run(book_id) completes
  Then:  3 JSON files in /data/output/<subject>/figures/
         3 PNG files with matching names
         each JSON has figure_path pointing to existing PNG

TEST-P3-09 [CONTRACT] output JSON has correct schema
  Given: any processed question
  When:  JSON file read from output folder
  Then:  has_figure is boolean (not null, not string "true")
         figure_path is null when has_figure=False
         figure_path is non-null string when has_figure=True
         review_status == "pending"

TEST-P3-10 [INTEGRATION] answer_key pages skipped
  Given: page_map.json marks page 45 as "answer_key"
  When:  phase3 runs
  Then:  no output files for page 45
         log shows "skipping answer_key page 45"

TEST-P3-11 [UNIT] threshold comes from config, not hardcoded
  Given: config.FIGURE_PROXIMITY_PX = 200
  When:  detect_figure() runs
  Then:  uses 200 as threshold, not 150
         no hardcoded 150 appears in phase3 source code
```

---

## PHASE 4 — QUESTION GENERATOR TESTS
### File: tests/test_phase4_generate.py

```
TEST-P4-01 [CONTRACT] text generation returns correct number of questions
  Given: sample_qr_page.md, n=8
  When:  generate_text_questions(markdown, subject, briefing_data, n=8) called
  Then:  returns Python list of exactly 8 items

TEST-P4-02 [CONTRACT] correct_answer is always exactly A, B, C, or D
  Given: any generated question
  When:  correct_answer read
  Then:  value in ["A","B","C","D"]
         NEVER lowercase, never "(A)", never "1"

TEST-P4-03 [CONTRACT] confidence is float 0.0–1.0
  Given: any generated question
  When:  confidence read
  Then:  isinstance(confidence, float) == True
         0.0 <= confidence <= 1.0

TEST-P4-04 [CONTRACT] subject matches what was passed in
  Given: generate called with subject="science_reasoning"
  When:  any generated question read
  Then:  question["subject"] == "science_reasoning"

TEST-P4-05 [CONTRACT] review_status is always "pending" on generation
  Given: any freshly generated question
  When:  review_status read
  Then:  value == "pending"
         NEVER "approved" straight out of generation

TEST-P4-06 [CONTRACT] figure generation returns questions referencing the figure
  Given: sample_figure.png + original questions
  When:  generate_figure_questions(figure_path, original_qs, n=4) called
  Then:  returns list of 4 items
         each stem contains "diagram" or "graph" or "table" or "figure"

TEST-P4-07 [UNIT] year_level from briefing injected into generation prompt
  Given: briefing with target_year="7-9"
  When:  generate_text_questions() called
  Then:  prompt sent to API includes "Year Level: 7-9"
         not hardcoded year level in code

TEST-P4-08 [UNIT] difficulty from briefing injected into generation prompt
  Given: briefing with difficulty="medium to hard"
  When:  generate_text_questions() called
  Then:  prompt sent to API includes difficulty level

TEST-P4-09 [EDGE] malformed LLM response with JSON fences handled
  Given: LLM returns ```json [...] ``` with markdown fences
  When:  parse_llm_response(response) called
  Then:  fences stripped, valid questions returned
         no exception raised

TEST-P4-10 [EDGE] LLM returns fewer questions than requested
  Given: LLM returns 5 when 8 were requested
  When:  generate_text_questions() processes response
  Then:  logs warning "expected 8, got 5"
         returns the 5 valid questions
         does NOT crash or auto-retry

TEST-P4-11 [EDGE] LLM returns invalid JSON — handled gracefully
  Given: LLM returns plain text response
  When:  generate_text_questions() processes it
  Then:  logs error with book_id and page number
         returns empty list []
         does NOT crash pipeline
         page flagged as generation_failed=True in output

TEST-P4-12 [UNIT] API delay is respected between calls
  Given: config.API_DELAY_SECONDS = 2
         3 pages to generate
  When:  phase4 processes all 3 pages
  Then:  time.sleep called with value from config (not hardcoded 2)
         total time >= 2 * 2 seconds between 3 calls

TEST-P4-13 [INTEGRATION] resumable — already-generated pages skipped
  Given: generated JSON exists for page 23
  When:  phase4_generate.run() called
  Then:  page 23 not regenerated
         log shows "skipping already generated page 23"

TEST-P4-14 [CONTRACT] writing subject questions use writing_prompt field
  Given: generate called with subject="writing"
  When:  generated questions read
  Then:  option_a, option_b, option_c, option_d are null or absent
         correct_answer is null or absent
         writing_prompt field is present and non-empty
```

---

## REVIEW API TESTS
### File: tests/test_review_api.py

```
TEST-R-01 [INTEGRATION] GET /questions/next returns pending question
  Given: SQLite has pending questions
  When:  GET /questions/next called
  Then:  200 response with valid question JSON
         review_status == "pending"

TEST-R-02 [INTEGRATION] GET /questions/next returns 404 when queue empty
  Given: no pending questions in SQLite
  When:  GET /questions/next called
  Then:  404 with message "No pending questions"

TEST-R-03 [INTEGRATION] POST approve sets review_status and reviewed_at
  Given: pending question with known id
  When:  POST /questions/{id}/approve called
  Then:  200 response
         SQLite: review_status="approved", reviewed_at is set timestamp

TEST-R-04 [INTEGRATION] POST reject sets review_status
  Given: pending question with known id
  When:  POST /questions/{id}/reject called
  Then:  200 response
         SQLite: review_status="rejected"

TEST-R-05 [INTEGRATION] POST edit updates fields and marks edited
  Given: pending question with known id
         payload: {stem: "new stem", correct_answer: "C"}
  When:  POST /questions/{id}/edit called
  Then:  200 response
         SQLite: stem="new stem", correct_answer="C"
         edited=1, review_status="approved"

TEST-R-06 [CONTRACT] edit rejects invalid correct_answer
  Given: payload with correct_answer="E"
  When:  POST /questions/{id}/edit called
  Then:  422 response
         question in SQLite NOT modified

TEST-R-07 [INTEGRATION] GET /stats returns accurate counts
  Given: 10 approved, 3 rejected, 2 edited, 50 pending in SQLite
  When:  GET /stats called
  Then:  {approved:10, rejected:3, edited:2, pending:50, total:65}

TEST-R-08 [INTEGRATION] GET /questions filters by subject
  Given: questions across all 5 subjects
  When:  GET /questions?subject=science_reasoning called
  Then:  only science_reasoning questions returned

TEST-R-09 [INTEGRATION] figure PNG served correctly
  Given: question with has_figure=True, figure saved in figures dir
  When:  GET /figures/{filename} called
  Then:  200 with Content-Type: image/png
         body is valid PNG

TEST-R-10 [CONTRACT] text-only question has figure_url=null (not absent)
  Given: question with has_figure=False
  When:  GET /questions/next returns it
  Then:  response JSON has "figure_url": null
         key is present, value is null (not missing key)

TEST-R-11 [INTEGRATION] GET /questions?status=pending returns only pending
  Given: mix of pending/approved/rejected questions
  When:  GET /questions?status=pending called
  Then:  only pending questions returned

TEST-R-12 [INTEGRATION] review server accessible on 0.0.0.0 (not just localhost)
  Given: server started with --host 0.0.0.0
  When:  request made to http://127.0.0.1:8000/health
  Then:  200 response (verifies binding to all interfaces)
```

---

## SYNC TESTS
### File: tests/test_sync.py

```
TEST-S-01 [UNIT] dry-run shows correct count without modifying anything
  Given: 25 approved questions in SQLite not yet in Supabase
  When:  sync.py --dry-run called
  Then:  output shows "25 questions would be synced"
         Supabase NOT modified
         SQLite NOT modified

TEST-S-02 [INTEGRATION] only approved questions are synced
  Given: 20 approved, 5 rejected, 100 pending in SQLite
  When:  sync.py runs
  Then:  Supabase receives exactly 20 questions
         rejected and pending NOT synced

TEST-S-03 [INTEGRATION] sync is idempotent
  Given: 20 questions synced to Supabase
  When:  sync.py runs again
  Then:  Supabase still has exactly 20 (no duplicates)
         no errors raised

TEST-S-04 [INTEGRATION] figures uploaded to Supabase Storage
  Given: approved question with has_figure=True and local figure_path
  When:  sync.py runs
  Then:  figure exists in Supabase Storage bucket
         question in Supabase has figure_url as Storage URL

TEST-S-05 [UNIT] one network error does not stop entire sync
  Given: 20 questions to sync, Supabase times out on question 5
  When:  sync.py runs
  Then:  questions 1–4 and 6–20 synced successfully
         question 5 logged as failed
         exits with partial success message, not unhandled exception
```

---

## SCHEMA TESTS
### File: tests/test_schema.py

```
TEST-DB-01 [UNIT] subject CHECK rejects invalid values
  Given: INSERT with subject="mathematics"
  Then:  raises sqlite3.IntegrityError, row NOT inserted

TEST-DB-02 [UNIT] correct_answer CHECK rejects invalid values
  Given: INSERT with correct_answer="E"
  Then:  raises sqlite3.IntegrityError

TEST-DB-03 [UNIT] review_status CHECK rejects invalid values
  Given: INSERT with review_status="maybe"
  Then:  raises sqlite3.IntegrityError

TEST-DB-04 [UNIT] all 5 valid subjects insert successfully
  Given: one valid question per subject
  When:  all 5 inserted
  Then:  all 5 rows exist, no errors

TEST-DB-05 [UNIT] id NOT NULL constraint enforced
  Given: question with id=None
  Then:  raises sqlite3.IntegrityError

TEST-DB-06 [INTEGRATION] schema.sql creates correct structure
  Given: schema.sql applied to fresh SQLite file
  When:  table structure inspected
  Then:  all columns present with correct types
         all CHECK constraints present
         all indexes present
         books table also created correctly
```

---

## END-TO-END SMOKE TEST
### Run manually after all phases built. Requires real 5-page test PDF.

```
TEST-E2E-01 [INTEGRATION] full pipeline on 5 pages produces reviewable questions

SETUP:
  Create test PDF with 5 pages:
    page 1: Quantitative Reasoning, no figure
    page 2: Quantitative Reasoning, with figure
    page 3: Science Reasoning, with figure
    page 4: Reading Comprehension, no figure
    page 5: Answer key

  Create matching briefing .md file at /data/pdfs/e2e_test.md

EXECUTE:
  python pipeline/run_book.py --book_id e2e_test

ASSERT PHASE 1:
  ✓ /data/scratch/e2e_test/pages/ has 4 .md files (page 5 skipped = answer key)
  ✓ /data/scratch/e2e_test/images/ has 4 .png files
  ✓ docling_output.json is valid JSON with all required fields

ASSERT PHASE 2:
  ✓ page_map.json has entries for pages 1–4
  ✓ pages 1–2 classified as "quantitative_reasoning"
  ✓ page 3 classified as "science_reasoning"
  ✓ page 4 classified as "reading_comprehension"
  ✓ page 5 classified as "answer_key"

ASSERT PHASE 3:
  ✓ quantitative_reasoning/text/ has questions from page 1
  ✓ quantitative_reasoning/figures/ has questions + PNG from page 2
  ✓ science_reasoning/figures/ has questions + PNG from page 3
  ✓ reading_comprehension/text/ has questions from page 4
  ✓ No output files generated for page 5 (answer key)

ASSERT PHASE 4:
  ✓ All question JSON files valid against schema
  ✓ All have review_status="pending"
  ✓ All have confidence 0.0–1.0
  ✓ Figure questions contain "diagram" or "figure" in stem
  ✓ Year level and difficulty match briefing values

ASSERT REVIEW API:
  ✓ GET /questions/next returns 200
  ✓ Approve first question → review_status="approved" in SQLite
  ✓ Reject second → review_status="rejected"
  ✓ GET /stats returns correct counts

ASSERT SYNC:
  ✓ sync.py --dry-run shows 1 question would sync
  ✓ sync.py syncs the approved question
  ✓ Question in Supabase with correct data and no duplicates
```

---

## SUPERPOWERS METHODOLOGY VALIDATION
### Not automated tests — human checkpoints enforced before each phase starts.
### Claude Code must confirm these before writing any production code.

```
CHECK-SP-01 [HUMAN] brainstorming skill activated before any phase
  Before writing code for any phase:
  Verify Claude Code asked clarifying questions about requirements
  Verify a spec was produced and shown in readable chunks
  Verify you approved the spec before any code was written
  If Claude Code jumped straight to code → STOP, restart session,
  say "Use brainstorming skill first"

CHECK-SP-02 [HUMAN] implementation plan produced before coding starts
  After spec approval:
  Verify Claude Code produced a written implementation plan
  Plan must have individual tasks with: exact file path, what to build,
  verification step for each task
  Tasks must be 2–5 minutes each (not "build the whole phase")
  If no plan produced → say "Use writing-plans skill before coding"

CHECK-SP-03 [HUMAN] TDD enforced — failing test written before any code
  For every task in the plan:
  Verify Claude Code wrote a FAILING test first
  Verify it actually ran the test and showed it failing (red)
  THEN it wrote the minimal code to make it pass (green)
  THEN it refactored
  If code was written before test → say "Delete that code.
  Write the failing test first per test-driven-development skill"

CHECK-SP-04 [HUMAN] subagent review between tasks
  Between each task:
  Verify Claude Code reviewed the previous subagent's output
  Review must check: spec compliance first, then code quality
  Critical issues must be fixed before next task starts
  If skipped → say "Use requesting-code-review skill before continuing"

CHECK-SP-05 [HUMAN] git worktree used for each phase
  When starting a new phase:
  Verify Claude Code created a new git branch for the work
  Branch name matches naming convention in CLAUDE.md
  Work happens on branch, not directly on main
  If on main → say "Use using-git-worktrees skill to create branch first"

CHECK-SP-06 [HUMAN] finishing-a-development-branch used when phase complete
  When all tasks in a phase are done:
  Verify all tests pass before merge is proposed
  Verify Claude Code presented merge/PR options, not auto-merged
  Verify worktree cleaned up after merge
```

---

## REVIEW UI FRONTEND TESTS
### File: tests/test_review_ui.py
### These test the single HTML file at review/ui/index.html
### Uses Playwright or Selenium for browser automation.
### Also includes design system compliance checks.

```
TEST-UI-01 [INTEGRATION] page loads without JS errors
  Given: FastAPI server running on port 8000
         review/ui/index.html opened in browser
  When:  page fully loads
  Then:  no console errors
         no uncaught exceptions
         all DOM elements present

TEST-UI-02 [CONTRACT] design system file exists before UI build starts
  Given: project root
  When:  check for design-system/MASTER.md
  Then:  file exists
         file contains sections: COLORS, TYPOGRAPHY, STYLE, ANTI-PATTERNS
         if missing → run uipro persist command before building UI

TEST-UI-03 [CONTRACT] dark mode is applied as default
  Given: review UI loaded
  When:  background colour of body inspected
  Then:  background is dark (luminance < 0.2)
         not white, not light grey
         dark mode is NOT a toggle — it is the only mode

TEST-UI-04 [CONTRACT] correct answer is highlighted green
  Given: a question loaded in the UI
         question has correct_answer="B"
  When:  options rendered
  Then:  option B has green background/border styling
         options A, C, D do NOT have green styling
         colour difference is visible (not subtle)

TEST-UI-05 [CONTRACT] figure shown above question when has_figure=True
  Given: a figure-linked question loaded
         figure_url is set and PNG exists
  When:  question rendered
  Then:  img element exists above the question stem
         img src points to the figure URL
         img loads successfully (no broken image icon)

TEST-UI-06 [CONTRACT] figure_url=null renders no image element
  Given: a text-only question (has_figure=False, figure_url=null)
  When:  question rendered
  Then:  no img element present in question area
         no broken image icon
         no empty image placeholder visible

TEST-UI-07 [CONTRACT] keyboard shortcut A triggers approve
  Given: a pending question displayed
  When:  user presses keyboard key "A"
  Then:  POST /questions/{id}/approve called within 300ms
         UI advances to next question immediately
         no mouse click required

TEST-UI-08 [CONTRACT] keyboard shortcut R triggers reject
  Given: a pending question displayed
  When:  user presses keyboard key "R"
  Then:  POST /questions/{id}/reject called within 300ms
         UI advances to next question immediately

TEST-UI-09 [CONTRACT] keyboard shortcut E enters edit mode
  Given: a pending question displayed
  When:  user presses keyboard key "E"
  Then:  question stem becomes editable (contenteditable or textarea)
         options become editable
         correct answer selector appears
         action bar changes to show Save/Cancel instead of A/R/E

TEST-UI-10 [CONTRACT] arrow keys navigate between questions
  Given: multiple questions in queue
         currently on question 3
  When:  user presses right arrow key →
  Then:  advances to question 4
  When:  user presses left arrow key ←
  Then:  returns to question 3

TEST-UI-11 [CONTRACT] progress bar updates after each decision
  Given: 100 pending questions, 0 reviewed
  When:  user approves 10 questions
  Then:  progress bar fill width increases to ~10%
         counter shows "10 of 100 reviewed"
         updates without page reload

TEST-UI-12 [CONTRACT] stats sidebar shows live counts
  Given: 10 approved, 3 rejected, 2 edited
  When:  stats panel inspected
  Then:  approved count shows 10
         rejected count shows 3
         edited count shows 2
         updates immediately after each decision (no refresh needed)

TEST-UI-13 [CONTRACT] subject filter sidebar works correctly
  Given: questions across all 5 subjects
  When:  user clicks "Science Reasoning" in sidebar filter
  Then:  only science_reasoning questions appear in queue
         filter button shows active state
         question counter updates to reflect filtered count

TEST-UI-14 [CONTRACT] high confidence questions visually distinguished
  Given: question with confidence=0.96 (above 0.90 threshold)
         question with confidence=0.72 (below threshold)
  When:  both questions displayed in queue list
  Then:  high confidence question shows green confidence indicator
         low confidence question shows amber or red indicator
         indicators are colour-coded dots or badges, clearly visible

TEST-UI-15 [CONTRACT] edit mode save calls correct API endpoint
  Given: question in edit mode
         reviewer changed stem text and correct_answer to "C"
  When:  reviewer presses Enter or clicks Save
  Then:  POST /questions/{id}/edit called with updated stem and correct_answer
         UI exits edit mode and advances to next question
         no separate approve call needed (edit implies approval)

TEST-UI-16 [CONTRACT] edit mode cancel restores original values
  Given: question in edit mode
         reviewer changed stem text
  When:  reviewer presses Escape or clicks Cancel
  Then:  original stem text restored
         question returns to normal review mode
         no API call made

TEST-UI-17 [ACCESSIBILITY] all interactive elements have visible focus states
  Given: review UI loaded
  When:  user tabs through all interactive elements
  Then:  every focusable element shows a visible focus ring
         focus ring is not the default browser outline removed by CSS
         WCAG AA: focus indicator must be clearly visible

TEST-UI-18 [ACCESSIBILITY] text contrast meets WCAG AA minimum
  Given: review UI in dark mode
  When:  text colour vs background colour measured
  Then:  body text contrast ratio >= 4.5:1
         secondary/muted text contrast ratio >= 3:1
         correct answer highlighted text contrast >= 4.5:1

TEST-UI-19 [ACCESSIBILITY] no emoji used as icons
  Given: review UI fully rendered
  When:  all icon elements inspected
  Then:  no emoji characters used as icons (✓ ✗ ← → etc.)
         icons are SVG elements or icon font characters
         per UI UX Pro Max anti-pattern rules

TEST-UI-20 [ACCESSIBILITY] keyboard-only user can complete full review workflow
  Given: review UI loaded
         user uses ONLY keyboard (no mouse)
  When:  user approves 5 questions, rejects 2, edits and saves 1
  Then:  all 8 actions completable without touching mouse
         no action requires mouse click to proceed

TEST-UI-21 [DESIGN] no AI purple/pink gradients present
  Given: review UI fully rendered
  When:  background and element colours inspected
  Then:  no purple (#8B5CF6, #A78BFA range) gradient backgrounds
         no pink gradient backgrounds
         per UI UX Pro Max anti-pattern rules for internal tools

TEST-UI-22 [DESIGN] monospace font used for data/code elements
  Given: review UI rendered
  When:  question ID, confidence score, page number, source book inspected
  Then:  these data elements use monospace font family
         readable at small sizes (min 11px)
         per design system MASTER.md typography rules
```

---

## TEST EXECUTION ORDER

```bash
# ── BEFORE FIRST CLAUDE CODE SESSION ──────────────────────────
# Verify tools installed
ls .claude/skills/                        # ui-ux-pro-max should be here
# In Claude Code: /plugin install superpowers@claude-plugins-official

# Generate and persist design system (required before UI build)
python3 .claude/skills/ui-ux-pro-max/scripts/search.py \
  "internal data annotation tool dark dashboard keyboard-driven" \
  --design-system --persist -p "QBank Review UI"
ls design-system/MASTER.md               # must exist before TEST-UI-02 passes

# ── SUPERPOWERS CHECKS (human, before each phase) ─────────────
# CHECK-SP-01 through CHECK-SP-06
# Do these manually at the start of each Claude Code session.
# Cannot be automated — they verify Claude Code's behaviour.

# ── AUTOMATED TESTS (run in this order) ───────────────────────
pytest tests/test_schema.py -v           # 1. DB foundation
pytest tests/test_briefing.py -v         # 2. Briefing parser (Phase 0)
pytest tests/test_phase1_normalise.py -v # 3. Normalisation
pytest tests/test_phase2_classify.py -v  # 4. Classification
pytest tests/test_phase3_figures.py -v   # 5. Figure detection
pytest tests/test_phase4_generate.py -v  # 6. Generation
pytest tests/test_review_api.py -v       # 7. FastAPI backend
pytest tests/test_sync.py -v            # 8. Supabase sync

# ── FRONTEND UI TESTS (after review UI is built) ──────────────
# Requires: FastAPI running + Playwright installed
pip install playwright --break-system-packages
playwright install chromium
pytest tests/test_review_ui.py -v        # 9. UI frontend + design system

# ── FULL SUITE ────────────────────────────────────────────────
pytest tests/ -v                         # 10. Everything at once

# ── END-TO-END (manual, requires real 5-page PDF) ─────────────
python tests/run_e2e.py                  # 11. Full pipeline smoke test
```

---

## DEFINITION OF DONE FOR EACH PHASE

A phase is NOT done until ALL of the following:

**Superpowers methodology (CHECK-SP-01 to 06):**
- [ ] brainstorming skill was used — spec produced and approved before coding
- [ ] writing-plans skill produced a task list before any code written
- [ ] TDD enforced — every task had failing test before code
- [ ] Code review between tasks (requesting-code-review skill)
- [ ] Work done on feature branch (using-git-worktrees skill)
- [ ] finishing-a-development-branch skill used for merge

**Code quality:**
- [ ] All automated tests for that phase are GREEN
- [ ] Phase run on a real 10-page section of a real book
- [ ] Output files manually inspected (open them, read them)
- [ ] Edge cases from CLAUDE.md verified manually

**For the review UI specifically (additional checks):**
- [ ] design-system/MASTER.md exists before UI build starts (TEST-UI-02)
- [ ] All TEST-UI-01 through TEST-UI-22 pass
- [ ] Tested keyboard-only — full workflow completable without mouse
- [ ] Tested in Chrome and Firefox

**Git:**
- [ ] Committed with message: `feat(phase-N): all tests passing`
- [ ] Merged to main via PR, not direct commit

**Do not start the next phase until the current one is truly done.**
