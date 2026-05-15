# PDF BRIEFING: McGraw-Hill's 10 ACT Practice Tests (Second Edition)

## Basic Info
- **file:** 10_ACT_Practice_Tests.pdf
- **publisher:** McGraw-Hill Companies, Inc.
- **author:** Steven W. Dulan and Advantage Education
- **edition:** Second Edition, 2008
- **total_pages:** 860
- **relevant_pages:** 25–860
- **skip_pages:** 1–24 (cover, about author, title page, copyright, TOC, intro, ACT overview section)

## Layout
- **column_format:** double_column
- **column_description:** Left column contains passage text (English/Reading) or working space label (Maths/Science). Right column contains numbered questions with options. Both columns clearly delineated with consistent margins throughout all 10 tests.
- **question_numbering:** 1, 2, 3... (plain bold integers, no prefix)
- **options_format_english_reading_science:** F, G, H, J (4 options, not A B C D)
- **options_format_mathematics:** A, B, C, D, E (odd questions) and F, G, H, J, K (even questions) — 5 options
- **answer_key_format:** four-column grid — English / Mathematics / Reading / Science side by side on 2 pages per test
- **has_figures:** yes
- **figure_types:** geometry diagrams, coordinate graphs (mathematics); data tables, process diagrams, bar graphs, line graphs (science reasoning)
- **figure_position:** below the question that references it (maths); embedded in passage at top of page with questions below (science)
- **figure_frequency:** ~30-40% of maths questions have a figure; ~80-100% of science passages have a table or diagram

## ACT Test Structure — Fixed Order Per Test
Each of the 10 practice tests has EXACTLY this structure:
1. English Test — 75 questions, grammar and rhetoric, passage-based, double column
2. Mathematics Test — 60 questions, pure maths MCQ, figures common
3. Reading Test — 40 questions, passage-based comprehension, double column
4. Science Reasoning Test — 40 questions, data/experiment interpretation, figures essential
5. Writing Test Prompt — essay only, NOT MCQ, skip entirely

## Subject Mapping to Pipeline Subjects
- English Test → skip (NOT in Australian selective exam subject list — skip all phases)
- Mathematics Test → quantitative_reasoning (algebra, geometry, trig, pre-calc)
- Reading Test → reading_comprehension (inference, main idea, author purpose)
- Science Reasoning Test → science_reasoning (data interpretation, NOT recall)
- Writing Test Prompt → skip (essay only, no MCQ — skip all phases)
- Answer Key pages → answer_key (skip all phases)
- Scoring Guide pages → answer_key (skip all phases)
- Answers and Explanations pages → answer_key (skip all phases — prose only)

## Page Ranges Per Practice Test

### PRACTICE TEST 1
- **English Test:** pages 25–44 (SKIP — not in subject list)
- **Mathematics Test:** pages 45–54
- **Reading Test:** pages 55–64
- **Science Reasoning Test:** pages 65–74
- **Writing Prompt:** pages 20–23 (skip)
- **Answer Key:** pages 75–76
- **Scoring Guide:** pages 77–78 (skip)
- **Answers and Explanations:** pages 79–104 (skip)

### PRACTICE TEST 2
- **English Test:** pages 110–129 (SKIP)
- **Mathematics Test:** pages 130–139
- **Reading Test:** pages 140–149
- **Science Reasoning Test:** pages 150–156
- **Answer Key:** pages 157–158
- **Scoring + Explanations:** pages 159–188 (skip)

### PRACTICE TEST 3
- **English Test:** pages 195–214 (SKIP)
- **Mathematics Test:** pages 215–229
- **Reading Test:** pages 230–239
- **Science Reasoning Test:** pages 240–241
- **Answer Key:** pages 242–243
- **Explanations:** pages 245–274 (skip)

### PRACTICE TEST 4
- **English Test:** pages 285–304 (SKIP)
- **Mathematics Test:** pages 305–319
- **Reading Test:** pages 310–319
- **Science Reasoning Test:** pages 315–321
- **Writing Prompt:** page 320 (skip)
- **Answer Key:** pages 322–323
- **Explanations:** pages 325–358 (skip)

### PRACTICE TEST 5
- **English Test:** pages 360–379 (SKIP)
- **Mathematics Test:** pages 380–394
- **Reading Test:** pages 390–399
- **Science Reasoning Test:** pages 395–404
- **Writing Prompt:** pages 405–406 (skip)
- **Answer Key:** pages 407–408
- **Explanations:** pages 413–438 (skip)

### PRACTICE TEST 6
- **English Test:** pages 440–454 (SKIP)
- **Mathematics Test:** pages 455–464
- **Reading Test:** pages 465–474
- **Science Reasoning Test:** pages 475–489
- **Answer Key:** pages 490–491
- **Explanations:** pages 495–528 (skip)

### PRACTICE TEST 7
- **English Test:** pages 530–544 (SKIP)
- **Mathematics Test:** pages 545–554
- **Reading Test:** pages 555–564
- **Science Reasoning Test:** pages 565–574
- **Answer Key:** pages 575–576
- **Explanations:** pages 580–614 (skip)

### PRACTICE TEST 8
- **English Test:** pages 615–629 (SKIP)
- **Mathematics Test:** pages 630–644
- **Reading Test:** pages 645–649
- **Science Reasoning Test:** pages 650–664
- **Answer Key:** pages 665–666
- **Explanations:** pages 670–703 (skip)

### PRACTICE TEST 9
- **English Test:** pages 705–719 (SKIP)
- **Mathematics Test:** pages 715–729
- **Reading Test:** pages 730–739
- **Science Reasoning Test:** pages 740–754
- **Answer Key:** pages 755–756
- **Explanations:** pages 760–788 (skip)

### PRACTICE TEST 10
- **English Test:** pages 790–804 (SKIP)
- **Mathematics Test:** pages 800–814
- **Reading Test:** pages 815–824
- **Science Reasoning Test:** pages 825–834
- **Answer Key:** pages 835–836
- **Explanations:** pages 840–860 (skip)

## Sample Questions
- **has_samples:** no — all pages are full exam questions, no worked examples or tutorials

## Question Counts (total across all 10 tests)
- English: 75 × 10 = 750 questions — SKIPPED (not in subject list)
- Mathematics: 60 × 10 = 600 questions → quantitative_reasoning
- Reading: 40 × 10 = 400 questions → reading_comprehension
- Science Reasoning: 40 × 10 = 400 questions → science_reasoning
- **Total MCQ to process: 1,400 questions across the book**
- **Total skipped: 750 English + essay pages**

## Known Issues

**1. Double-column layout throughout — most critical issue**
Docling reading order must correctly separate left column (passage text) from right column (questions). These must NOT be merged into flowing text. The passage is context for the questions — they are spatially distinct.

**2. Non-standard options format (F G H J, not A B C D)**
English, Reading, and Science use F, G, H, J instead of A, B, C, D.
Mathematics uses A, B, C, D, E (odd) and F, G, H, J, K (even) — 5 options not 4.
Pipeline must normalise: F→A, G→B, H→C, J→D when storing in SQLite.
For generation: always generate standard 4-option A, B, C, D questions.
Drop the 5th maths option (E or K) during normalisation.

**3. Science questions are inseparable from their figures**
Every science passage has at least one table or diagram. Questions directly reference "Table 1", "Figure 1", "Study 2" etc. These are always figure-linked — do not classify as text-only. The figure IS the question context.

**4. English passages span multiple pages**
A single English passage covers 2-4 PDF pages. Left column has passage text, right column has questions with numbered underlines in the passage. Docling must preserve this relationship. Phase 3 figure detection does not apply to English — treat as passage-linked not figure-linked.

**5. Answers and Explanations sections are very long prose**
Pages 79-104 (Test 1), 159-188 (Test 2) etc are prose explanations ("The best answer is F because..."). Classifier must return answer_key for these — they look like question content but are not MCQ.

**6. "DO YOUR FIGURING HERE" on maths pages**
The right side of maths pages shows "DO YOUR FIGURING HERE" as a column header. Docling will extract this as text. The pipeline must ignore this string — it is not a question or answer.

**7. Maths geometry figures are vector-drawn**
Docling will detect these as figure elements. They are essential for those questions. Correctly tagged as figure-linked in Phase 3.

**8. Writing test lined pages**
Some tests include 2-4 lined pages for the essay. Return skip for these.

**9. Bubble answer sheets**
Bubble-fill answer sheets appear before some tests. Return skip.

**10. Page header text**
Every page has "PRACTICE TEST N ENGLISH/MATHEMATICS/READING/SCIENCE TEST" as a header plus a bold page number. Docling will extract these — they are navigation, not content.

**11. Imperial units in maths**
Some maths questions use feet, miles, inches, pounds, Fahrenheit. Generated questions must convert to metric for Australian context.

**12. US cultural context**
Names, dollar amounts ($), and cultural references are US-specific. Generation prompt must instruct rewriting to Australian context.

## Year Level and Difficulty
- **target_year:** 11–12 (Australian Year 11-12, pre-university equivalent)
- **difficulty:** medium to hard
- **australian_equivalent:** Comparable to selective high school entry exam top-difficulty questions; harder than most Year 9-10 selective school prep material

## Relevance to Australian Selective Exam Pipeline

| ACT Section | Pipeline Priority | Reason |
|---|---|---|
| Mathematics | HIGH | Algebra, geometry, ratios, word problems transfer directly |
| Science Reasoning | HIGH | Data interpretation, tables, graphs match Australian style |
| Reading | MEDIUM | Passage comprehension transfers well |
| English | SKIP | Grammar/rhetoric not in our 5 subject list |
| Writing | SKIP | Essay only, no MCQ, not in our 5 subject list |

## Generation Notes
- **Born-digital PDF** — Docling text extraction works cleanly, no OCR needed
- **Consistent structure** — Once Phase 2 is calibrated on Test 1, page ranges for Tests 2-10 follow same pattern with offset. Consider bulk-processing after Test 1 validates correctly.
- **Do not store raw questions** — Copyright McGraw-Hill 2008. Use only as style reference for generation.
- **Rewrite all generated questions** with: Australian dollars, metric units, Australian names and places, Australian scientific/environmental contexts where natural.
- **Science passages**: Do not attempt to generate questions without the associated figure/table. Always figure-linked.
- **Reading passages**: Generate comprehension questions about new passage content, not about the ACT passages themselves. Use ACT questions as style templates only.
