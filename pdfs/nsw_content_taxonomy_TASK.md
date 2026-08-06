# NSW SELECTIVE — CONTENT TAXONOMY AND BUILD TARGETS

> Generation brief for the NSW Selective High School Placement Test. Every category and
> subcategory to be covered, with a build target for each.
>
> Read with `pdfs/selective_exam_delivery_SPEC.md` (delivery, forms, calendar) and
> `CLAUDE.md` (pipeline rules). Researched 2026-08-05, primarily from the **official
> UCLES practice papers** published by the NSW Department of Education; provenance and
> confidence for every claim is in §7.

---

## 1. THE EXAM

Sat in Year 6 for Year 7 entry. Fully computer-based from 2026. Four components, **each
weighted 25%**, ~150 minutes total.

| Component | Questions | Answer slots | Time | Per slot | qbank subject |
|---|---:|---:|---:|---:|---|
| Reading | 17 | **38** | 45 min | 71 s | `reading_comprehension` |
| Mathematical Reasoning | 35 | 35 | 40 min | 69 s | `mathematics` |
| Thinking Skills | 40 | 40 | 40 min | 60 s | `logical_reasoning` |
| Writing | 1 | 1 | 30 min | — | `writing_prompts` |

Content is drawn from **Years 5–6**, presented in unfamiliar contexts. No specialist
knowledge is required in any component — everything needed is in the question.

---

## 2. BUILD TARGETS

Targets are set above the minimum so that mock forms can be **assembled by selection**
rather than by using everything available. Mock need is inflated 1.5× for that reason;
drill uses whatever is left over, so is taken at face value.

| Component | Mock (14 forms) | ×1.5 | Drill (1 round) | **Target** |
|---|---:|---:|---:|---:|
| Reading | 126 | 189 | 460 | **649** |
| Mathematical Reasoning | 252 | 378 | 460 | **838** |
| Thinking Skills | 280 | 420 | 460 | **880** |
| **Total MCQ** | 658 | 987 | 1,380 | **2,367** |
| Writing | 14 | 21 | — | **21 prompts** |

Round 2 of drill reuses round 1, so no additional questions are needed for it.

---

## 3. READING — 649 questions

45 minutes, 17 questions across **38 answer slots**. Several questions are multi-part: one
passage carries a block of linked items. Build to slots, not to questions.

### 3.1 Question types

| # | Type | Target | What it is |
|---|---|---:|---|
| 3.1 | Single-passage comprehension | **292** | One text, a block of linked questions |
| 3.2 | Vocabulary cloze | **136** | A passage with ~8 blanks filled from a dropdown |
| 3.3 | Poetry | **65** | Imagery, figurative language, mood, symbolism |
| 3.4 | Paired-extract comparison | **52** | Two texts compared for tone, attitude, perspective |
| 3.5 | Multi-extract synthesis | **52** | 3–4 related texts; which best supports a conclusion |
| 3.6 | Structural / organisation cloze | **52** | A removed sentence or paragraph must be replaced |

**We currently have types 3.1 and 3.2 only.** Types 3.3–3.6 are unbuilt — see §6.

### 3.2 Subcategories within single-passage comprehension (292)

| Subcategory | Target | Notes |
|---|---:|---|
| Inference and implied meaning | 70 | The dominant type. What is suggested, not stated |
| Vocabulary in context | 55 | What this word means *here*, not in general |
| Author's attitude, tone and purpose | 55 | Serious, ironic, critical; what is the writer doing |
| Main idea and summary | 45 | Whole-text gist; best title; central claim |
| Detail retrieval | 35 | Directly stated fact — the easiest type, keep the share low |
| Cause and effect | 32 | Why did this happen; what followed from it |

### 3.3 Text types — spread across all of the above

| Text type | Share | Notes |
|---|---:|---|
| Narrative / literary fiction | 25% | Character, plot, theme; extracts, not whole stories |
| Informational / expository | 25% | Science, history, explanatory writing |
| Persuasive / argumentative | 20% | Opinion pieces, speeches, editorials |
| Poetry | 15% | Must include some free verse, not only rhyming |
| Functional / everyday | 15% | Instructions, schedules, notices, infographics |

### 3.4 Calibration

**Pitch to Year 6.** A capable eleven-year-old should meet this vocabulary in reading, not
in a word list. This is the single biggest risk in the existing bank — see §6.

Australian context mandatory. Passages 200–350 words for single-passage sets; poetry
shorter. Each passage carries 4–8 linked questions, matching the real paper's structure of
multi-part questions over 38 slots.

---

## 4. MATHEMATICAL REASONING — 838 questions

35 questions in 40 minutes, **no calculator**. Drawn from Years 5–6 content but set in
unfamiliar contexts: the component tests mathematical *thinking*, not computation.
Fractions, percentages and ratios are the most heavily tested areas.

### 4.1 Content areas

| Area | Target | Subcategories |
|---|---:|---|
| **Number and arithmetic** | **335** | whole-number operations; fractions (all four operations); decimals; **percentages**; **ratio and proportion**; factors, multiples and primes; order of operations; place value; estimation and approximation; negative numbers |
| **Measurement and geometry** | **210** | perimeter, area, volume; angle properties; 2D and 3D shape properties; units and conversions; time and timetables; scale; coordinates; spatial visualisation; nets and cross-sections |
| **Algebra and patterns** | **168** | number sequences (arithmetic and geometric); pattern rules and extension; simple equations; substitution; unknowns; function machines and input–output rules |
| **Statistics and probability** | **125** | reading bar, line, column and pie charts; tables and two-way tables; mean, median, mode, range; probability as fraction and proportion; drawing conclusions from data |

### 4.2 Question archetypes — apply across all four areas

| Archetype | Share | Notes |
|---|---:|---|
| Multi-step word problems | 35% | Two or three linked operations; the dominant form |
| Single-step application | 20% | One operation in an unfamiliar setting |
| Pattern and sequence | 15% | Identify the rule, then extend or reverse it |
| Data interpretation | 15% | Extract from a chart or table, then reason |
| Geometry and measurement | 15% | Apply a property or formula |

### 4.3 Calibration

**Years 5–6 content, Year 6 sitting.** `year7_nsw_maths` sits one year ahead — a defensible
stretch. **`year9_maths` does not belong to NSW**: its topics include quadratic equations,
linear functions and single-variable inequalities, which are three years beyond a Year 6
candidate. That book belongs to Victoria (Year 8 sitting, Year 9 entry).

No calculator anywhere. Numbers must stay tractable by hand — this is a reasoning test, not
an arithmetic endurance test.

---

## 5. THINKING SKILLS — 880 questions

40 questions in 40 minutes. No syllabus content: it tests reasoning under time pressure.

### 5.1 What the official paper actually contains

Every question in the official UCLES Practice Test 1 was classified from its published
explained answer. This is the most authoritative breakdown available:

| Family | Count | Share | Target |
|---|---:|---:|---:|
| Critical thinking / argument analysis | 18 | 45% | **396** |
| Problem solving / numeric and logical | 15 | 38% | **330** |
| **Figural / spatial / diagram** | **7** | **18%** | **154** |

The figural share is easy to miss and is nearly a fifth of the paper: questions 4, 10, 16,
22, 28, 34 and 40 of Practice Test 1 are all diagram-based.

### 5.2 Critical thinking / argument analysis — 396

| Subcategory | Target | Official PT1 examples |
|---|---:|---|
| Who reasons correctly | 70 | q5, q11, q18, q23, q27 — two named students, pick who is right |
| Identify the assumption | 55 | q15 (every city name must be unique), q38 |
| Weaken the argument | 50 | q8 (wind-farm storage), q35 |
| Strengthen the argument | 50 | q2 (creative skills for engineers), q14, q32 |
| Necessary vs sufficient | 45 | q3 (opportunity *and* motive), q30 |
| Identify the conclusion / main claim | 40 | q20, q26 (a better explanation is offered) |
| Identify the flaw in reasoning | 40 | q9 (double-counting a prize winner) |
| Correlation vs causation | 26 | leaping from linked to caused |
| Conditional chains | 20 | q21, q24 — if A then B; B requires C |

### 5.3 Problem solving / numeric and logical — 330

| Subcategory | Target | Official PT1 examples |
|---|---:|---|
| Numeric deduction | 75 | q1 (marbles), q7 (goats and kids), q37 (dog legs) |
| Ordering and ranking | 55 | q6 (ages), q29 (race), q39 (swimmers vs runners) |
| Logic grid puzzles | 45 | q12 (houses, sports, vehicles) |
| Formal syllogism and set logic | 45 | q33 (game popularity), q24 |
| Optimisation / best value | 40 | q19 (bus passes), q31 (shop prices), q13 |
| Calendar, timetable and scheduling | 35 | q25 (performances across a month) |
| Truth-teller and constraint puzzles | 35 | q36 (statements on doors) |

### 5.4 Figural / spatial / diagram — 154

**This is the least-covered family and the one most likely to be under-built.** All require
a rendered figure (`figure_svg`).

| Subcategory | Target | Official PT1 examples |
|---|---:|---|
| Shape combination and dissection | 35 | q10 (45° corners forming a square), q40 |
| Tile, tessellation and repeating patterns | 30 | q16 (four copies of one tile) |
| 3D views and projections | 30 | q22 (what the shape looks like from above) |
| Pattern orientation and rotation | 25 | q28 (identify the pattern's starting corner) |
| Segment, grid and display logic | 20 | q4 (seven-segment display with faulty segments) |
| Chart and diagram reasoning | 14 | q34 (which pie section is one quarter) |

Secondary sources also describe **pattern matrices, figure series and figural analogies**
in ACER style. None appear in official Practice Test 1, so they are recorded as *possible*
rather than confirmed — see §7. Build the six subcategories above first.

### 5.5 What we already hold — and where it sits

All 300 built questions are `pending`. Mapping the existing 17 categories onto this
taxonomy:

| Family | Have | Target | Gap | Existing categories |
|---|---:|---:|---:|---|
| Critical thinking / argument | 135 | 396 | **261** | who_reasons 30, identify_assumption 18, weaken 18, strengthen 15, identify_conclusion 15, correlation_vs_causation 15, necessary_vs_sufficient 12, conditional_chains 12 |
| Problem solving / numeric-logic | 131 | 330 | **199** | ordering_ranking 20, syllogism_formal 20, numeric_deduction 20, set_counting_logic 18, letter_word_overlap 18, symbol_sequence_patterns 18, unit_chain_conversion 17 |
| Figural / spatial | 34 | 154 | **120** | spatial_3d_views 17, measurement_reasoning 17 |

Existing figural coverage is only `spatial_3d_views` (cube stacks and views) and
`measurement_reasoning` (rulers, thermometers). **Shape combination, tessellation, pattern
orientation and display logic are entirely unbuilt** — four of the six figural
subcategories. `tools/figure_lib.py` already provides the drawing primitives.

`symbol_sequence_patterns` (18) is counted under problem solving because those items are
symbol strings rather than rendered diagrams. If they are reworked as figures it moves to
the figural family and the gap there falls to ~102.

---

## 6. WHAT WE HAVE VERSUS WHAT WE NEED

| Component | Approved | Pending | Usable for NSW | Target | Gap |
|---|---:|---:|---:|---:|---:|
| Reading | 634 | 204 | **see below** | 649 | ~529+ |
| Mathematical Reasoning | 1,073 | 0 | **531** | 838 | **307** |
| Thinking Skills | 0 | 298 | 298 *(after review)* | 880 | **582** |
| Writing | 0 | 10 | 10 *(after review)* | 21 | **11** |

### 6.1 The Reading pool needs a decision before it can be counted

All 634 approved reading questions were generated from `act_test1–10`, whose briefings
specify `target_year: 11–12, difficulty: hard` — American college-entrance level, for
students five to six years older than a NSW candidate.

Sampling three of them found the **question types correct** (author's portrayal,
implication, sensory detail are all genuine NSW Reading skills) but the **passage
vocabulary too high** in two of three: *"infrastructure and logistics"*, *"injecting
significant revenue into the local economies"*. The third, a descriptive market scene,
would suit Year 6 well.

So they are neither wholesale usable nor wholesale waste. **Sample-review ~30 against Year
6 pitch and decide.** Until then the Reading gap is between ~529 and ~649, and Reading is
25% of the exam.

The only correctly pitched Reading content is the **120 vocabulary cloze** questions, built
for this taxonomy's §3.2 and currently pending.

### 6.2 Writing — 10 prompts, two types missing

Held: narrative 3, persuasive 3, article 1, diary 1, news report 1, speech 1.
**Missing entirely: `email` and `advice_sheet`.** Target 21 prompts across all eight types,
so roughly 2–3 per type.

---

## 7. PROVENANCE AND CONFIDENCE

| Claim | Confidence | Source |
|---|---|---|
| Four components, 25% each, ~150 min | **High** | NSW Dept of Education |
| Reading 17 questions / 38 answer slots / 45 min | **High** | Multiple sources agree on 38 slots |
| Maths 35 q / 40 min, Thinking 40 q / 40 min, Writing 1 / 30 min | **High** | NSW Dept of Education |
| Content drawn from Years 5–6 | **High** | Multiple independent guides |
| Thinking Skills family split (45 / 38 / 18) | **High** | Classified directly from official UCLES explained answers, PT1, all 40 questions |
| Six Reading question types incl. structural cloze and multi-extract | Medium | Coaching-provider guides; not seen in an official paper |
| Reading text-type shares | Medium-low | Inferred from guides; no official breakdown published |
| Maths topic shares (40/25/20/15) | Medium-low | Inferred; "fractions, percentages, ratios most tested" is stated, exact shares are not |
| Thinking Skills subcategory targets | Medium | Extrapolated from PT1 frequencies over a 40-question sample |
| ACER-style pattern matrices / figure series in Thinking Skills | **Low** | Claimed by one secondary source; absent from official PT1 |

**Practice Tests 2 and 3 are also published** and should be classified the same way as PT1
to firm up §5. A 120-question sample across three papers would move the subcategory targets
from Medium to High.

Sources:
- [NSW Dept of Education — selective high school practice tests](https://education.nsw.gov.au/schooling/parents-and-carers/choosing-a-school-setting/selective-high-schools/placement-test/selective-high-school-practice-tests.html)
- [Official UCLES Thinking Skills PT1 — explained answers](https://education.nsw.gov.au/content/dam/main-education/schooling/parents-and-carers/choosing-a-school-setting/selective-high-schools-and-opportunity-classes-parents/documents/shs-practice-tests-2026-entry/PT1_SHS_thinking_skills_answers_explained.pdf) — classified question by question for §5
- [Official UCLES Thinking Skills PT1 — question paper](https://education.nsw.gov.au/content/dam/main-education/schooling/parents-and-carers/choosing-a-school-setting/selective-high-schools-and-opportunity-classes-parents/documents/shs-practice-tests-2026-entry/PT1_SHS_thinking_skills_questions.pdf)
- [Official UCLES Thinking Skills PT3](https://education.nsw.gov.au/content/dam/main-education/schooling/parents-and-carers/choosing-a-school-setting/selective-high-schools-and-opportunity-classes-parents/documents/shs-practice-tests-2026-entry/shs-practice-test-3/Practice_Test_3_-_SHS_Thinking_Skills.pdf)
- [Selective reading test — question types and structure](https://www.selectiveexams.com.au/guides/selective-school-reading-test-guide) — source of the six Reading types
- [NSW selective mathematical reasoning guide](https://insights.educourse.com.au/nsw-selective-mathematical-reasoning/) — source of the maths topic list
- [NSW selective thinking skills — format and question types](https://www.smartexams.com.au/blogs/nsw-selective-thinking-skills-test-explained-question-types-timing-strategy--how-to-prepare)
- [NSW selective test format — four components](https://braintreecoaching.com.au/nsw-selective-test-format-guide)
- [NSW selective test components explained](https://braintreecoaching.com.au/blog/nsw-selective-school-test-components-complete-guide-2026)

---

## 8. BUILD ORDER

1. **Review the 298 Thinking Skills questions.** 25% of the exam, currently zero approved.
2. **Sample-review 30 ACT reading questions** against Year 6 pitch (§6.1). This is a
   decision, not a build, and it sets the size of the largest gap.
3. **Review the 120 vocabulary cloze** — correctly pitched, already built.
4. **Build Thinking Skills figural** — 120 questions across four unbuilt subcategories.
   `tools/figure_lib.py` provides the primitives.
5. **Build Reading types 3.3–3.6** — poetry, paired extracts, multi-extract synthesis and
   structural cloze are all entirely unbuilt: 221 questions.
6. **Top up Mathematical Reasoning** — 307 at Years 5–6 pitch, weighted to fractions,
   percentages and ratios.
7. **Writing** — 11 more prompts, including the two missing types.
8. **Classify Practice Tests 2 and 3** to firm up the §5 targets.
