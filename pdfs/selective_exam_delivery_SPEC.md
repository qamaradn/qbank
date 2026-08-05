# SPEC — Exam structure, question categories, and how Selectly delivers them

> Shared source of truth for **qbank** (what questions to build) and **Selectly** (how to
> serve them). Written 2026-08-05. Supersedes the delivery assumptions in
> `src/lib/config/schools.ts`, which is wrong for Victoria — see §3.
>
> Companion documents: `pdfs/selective_verbal_reasoning_TASK.md` (content briefs per
> subject), `pdfs/selective_verbal_reasoning_HANDOVER.md` (build state), `CLAUDE.md`
> (pipeline rules).

---

## 1. WHY THIS EXISTS

Selectly currently serves every student a **random** selection of questions. That makes
percentile scoring and progress tracking impossible: no two students sit the same paper,
so no score is comparable to any other, and a student's score this month cannot be
compared with their score last month.

This spec replaces random selection with **fixed forms**. Every student sitting Drill Set
7 sees the same questions in the same order; every student sitting Mock 3 sits the same
paper. That single change is what makes a parent-facing percentile and an improvement
curve possible.

Two delivery modes, doing different jobs:

| | Drill | Mock |
|---|---|---|
| Purpose | learn a category, and give cohort data from week one | measure exam readiness under exam conditions |
| Scope | one category, ~20 questions | full paper, all sections |
| Length | ~20–25 min | ~60 min of MCQ, half-length (see §5.2) |
| Source | the existing approved bank | authored new, monthly |
| Available | all of it, from launch | released on a schedule |
| Feedback | after submit | after submit |

---

## 2. EXAM CALENDAR

Both 2027-entry exams have already been held. **The build target is 2028 entry.**

| | NSW SHSPT | VIC SEHS |
|---|---|---|
| Authority | NSW Dept of Education (UCLES/Cambridge authored) | ACER, for the Victorian Dept of Education |
| Sat in | Year 6, for Year 7 entry | Year 8, for Year 9 entry |
| 2027 entry (held) | **1–2 May 2026** (make-up 22 May) | **Sat 20 June 2026** |
| 2027 results | late August 2026 | 3 August 2026 |
| **2028 entry (target)** | **~first Fri/Sat May 2027** — not yet announced | **~mid-late June 2027** — not yet announced |
| Applications | open ~Oct 2026, close ~Feb 2027 | open ~March 2027, close ~April 2027 |

**The two exams are roughly six weeks apart.** NSW is early May; VIC is late June. A single
release calendar cannot serve both — see §5.3.

Confirm both dates once officially announced. The NSW date has followed the first
Friday/Saturday of May for several years; ACER has held the VIC exam in June each year.

---

## 3. EXAM STRUCTURE AND CATEGORIES

### 3.1 NSW Selective High School Placement Test

Fully computer-based from 2026. Four components, **each weighted 25%**, ~150 minutes.

| # | Component | Questions | Answer slots | Time | Per slot | Categories tested |
|---|---|---:|---:|---:|---:|---|
| 1 | Reading | 17 | **38** | 45 min | **71 s** | inference, vocabulary in context, critical analysis, **vocabulary cloze** (~8 blanks per passage) |
| 2 | Mathematical Reasoning | 35 | 35 | 40 min | **69 s** | problem solving, patterns, word problems — Year 6 curriculum |
| 3 | Thinking Skills | 40 | 40 | 40 min | **60 s** | critical thinking (~45%) and problem solving / logic puzzles (~55%) |
| 4 | Writing | 1 | 1 | 30 min | — | narrative, persuasive, article, diary, email, speech, advice sheet, news report |

**Reading is 17 questions but 38 answer slots** — several questions have multiple parts.
The pacing that matters is therefore 45 min ÷ 38 ≈ **71 seconds per answer**, not 45 ÷ 17.
Timing a reading drill on 17 would give students more than twice the real allowance.

This maps cleanly onto how the cloze questions are already built: 8 linked blanks sharing
one passage is one multi-part question occupying 8 answer slots.

**This matches `schools.ts` exactly.** No Selectly change needed for NSW section structure.

Thinking Skills archetypes are enumerated in `TASK.md` §4 and are already built —
17 categories, 300 questions. Reading vocabulary cloze is built — 15 passages, 120
questions.

### 3.2 Victorian Selective Entry High Schools

**ACER restructured this exam.** It was five separate 30-minute components; it is now
**three**, with the former Reading/Verbal and Maths/Quantitative components interleaved
into single papers. Total task time 2 h 35 min (about four hours on site with breaks).

| # | Component | Questions | Time | Per question | Format |
|---|---|---:|---:|---:|---|
| 1 | Mathematics and Quantitative Reasoning | **~75 (estimated, §3.2.1)** | 60 min | **~48 s** | MCQ |
| 2 | Reading and Verbal Reasoning | ~75 | 55 min | **44 s** | MCQ |
| 3 | Writing | 1 | 40 min | — | extended response |

**Victoria is the faster exam, and got faster in the restructure.** The old format ran
Reading 30 q / 30 min plus Verbal 30 q / 30 min — 60 questions in 60 minutes, 60 s each.
The combined paper is ~75 questions in 55 minutes: **44 seconds**. Roughly a third less
time per item.

Within that paper the budget is not spread evenly. A verbal item should be answerable in
**~25 seconds** so that passage-based reading items can take longer inside the same 55
minutes. See §5.1.1.

#### 3.2.1 Estimating the Maths + Quantitative question count

ACER publishes the 60-minute duration but not the question count, and no student report of
it could be found. It is estimated here by extrapolating from the old format, which is
fully documented, using the one merge whose outcome we can actually observe.

**The old format**, five components of 30 minutes each:

| Component | Questions | Time | Per question |
|---|---:|---:|---:|
| Reading | ~30 | 30 min | 60 s |
| Verbal Reasoning | ~30 | 30 min | 60 s |
| Mathematics | ~30 | 30 min | 60 s |
| Quantitative Reasoning | ~30 | 30 min | 60 s |

**The measured merge.** Reading + Verbal went from 60 questions in 60 minutes to ~75 in
55: questions **×1.25**, time ×0.917, pace **27% faster per item**.

**Applying that to Maths + Quantitative**, which went from 60 questions in 60 minutes to an
unknown count in a confirmed 60:

| Method | Assumption | Result | Pace |
|---|---|---:|---:|
| **A** | same question multiplier (×1.25) | **75 q** | 48 s |
| B | same per-item pace as R+V (44 s) | 82 q | 44 s |
| C | administrative merge only, no density change | 60 q | 60 s |
| D | midpoint of A and C | 68 q | 53 s |

**Planning figure: 75 questions (Method A), ~48 seconds per question.**

Method A applies the only transformation we have measured, rather than inventing one. B
assumes ACER standardised a single pace across subjects, which is implausible — a maths
item requires working that a verbal item does not, which is presumably why this component
kept all 60 minutes while Reading + Verbal lost five. C cannot be dismissed, since the
retained duration is consistent with a purely administrative merge of two 30-minute
blocks, but it ignores the clear evidence that ACER used the restructure to raise density.

**The cost of being wrong is asymmetric, which is why the estimate is set high rather than
at the midpoint.** If the true count is lower, we have authored surplus questions, and
surplus flows straight into the drill pool (§5.2) — no waste. If the true count is higher
and we built to it, a mock release is short and has to be patched under time pressure.
Over-supply degrades gracefully; under-supply does not.

**Verify against ACER's official `SEHS_Sample_Questions.zip` before the first VIC mock
ships**, and correct this section. Everything downstream that depends on the number is
marked "estimated".

> **Verification required before the first VIC mock is authored.** ACER has not formally
> published the 2027 structure, and secondary sources conflict — several still describe
> the old five-component format. The three-component structure above is corroborated by
> four independent first-hand accounts from students who sat 20 June 2026 (recorded in
> `TASK.md` §2 and §8, rated High confidence), and by ACER's current published timing.
> The **question count for component 1 is unknown** and must be established. Download
> ACER's official `SEHS_Sample_Questions.zip` from the prepare page to confirm both.

### 3.3 What this changes for Selectly

`schools.ts` models `vic-seal` as **four** sections — verbal 30/30 min, numerical 35/35,
reading 30/30, writing 1/25. That is the old format and is wrong on every count.

Two consequences beyond the timings:

- **VIC component 2 draws from two qbank subjects at once** (`reading_comprehension` and
  `verbal_reasoning`), interleaved in one paper.
- **VIC component 1 likewise draws from two** (`mathematics` and
  `quantitative_reasoning`). Today `vic-seal` uses only `quantitative_reasoning`, so the
  1,073 approved `mathematics` questions are unavailable to Victorian students. Under the
  correct structure they become available.

`SectionConfig` currently allows one `category` per section and must accept several.

---

## 4. CATEGORY → QBANK SUBJECT MAP

| Exam | Component | qbank subject(s) | Approved | Notes |
|---|---|---|---:|---|
| NSW | Reading | `reading_comprehension` | 634 | plus 120 cloze, pending |
| NSW | Mathematical Reasoning | `mathematics` | 1,073 | Year 6 pitch |
| NSW | Thinking Skills | `logical_reasoning` | **0** | 300 pending — see §7 |
| NSW | Writing | `writing` | 0 | 30 prompts pending |
| VIC | Maths + Quantitative | `mathematics` + `quantitative_reasoning` | 2,702 | |
| VIC | Reading + Verbal | `reading_comprehension` + `verbal_reasoning` | 1,655 | |
| VIC | Writing | `writing` | 0 | 30 prompts pending |

### 4.1 Two content rules the schema cannot currently express

**Vocabulary cloze is NSW-only.** The 120 cloze questions sit in `reading_comprehension`
alongside general comprehension. A Victorian student must never be served one — that
format does not appear in their exam. `category` alone cannot distinguish them.

**Reading and verbal are pitched two years apart, deliberately.** NSW is sat in Year 6,
VIC in Year 8. `TASK.md` §2 states the gap is intentional and that a question is not
interchangeable between them. Sharing one reading pool across both exams therefore serves
Year 8 passages to Year 6 students and vice versa.

Both are solved by making school eligibility explicit per question rather than inferred
from category — see §6.1. `push_to_selectly.py` currently hardcodes
`schoolIds = ["vic-seal", "nsw-shspt"]` on every question, so today the field carries no
information at all.

### 4.2 `science_reasoning` is orphaned

1,322 questions (956 approved) map to no component of either exam. They are **drill-only
content** unless a third school type (e.g. JMSS) is added. Recorded here so the decision
is explicit rather than accidental.

---

## 5. HOW THE APP OPERATES

### 5.1 Drill

**Content.** The entire existing approved bank, divided into fixed forms of ~20 questions
within a single category. No new authoring — drill is what we already have.

**Rules.**

1. Fixed membership and fixed order. Every student sees Drill Set 7 identically.
2. **Timed at exact exam pace** — see §5.1.1. Not a generous approximation: the real
   allowance, to the second.
3. No feedback during the attempt. On submit: score, then answers and explanations unlock.
4. The score is recorded and feeds the parent portal and the percentile.
5. **A completed form is locked** — the student cannot reopen it until every form in that
   category has been attempted. The enforced gap is a spaced-repetition mechanism: they
   must recall rather than re-read.
6. When all forms in a category are exhausted, the counter resets and **round 2 begins on
   the same forms, in the same membership**. Round 2 is scored too.

#### 5.1.1 Timing — exact exam pace

**Speed is the skill being examined.** Successful candidates finish; unsuccessful ones run
out of time with questions unattempted. A drill that allows more time than the exam trains
the wrong thing and reports a score the student cannot reproduce on the day. Drill
therefore runs at the **real per-item allowance**, not a padded one.

**The rule.** A drill set's timer is the number of answer slots in the set multiplied by
that component's exam allowance per slot, rounded to the nearest 30 seconds.

| Exam | Category | Exam allowance | 20-slot drill |
|---|---|---:|---:|
| NSW | Reading (incl. cloze) | 71 s / slot | **24 min** |
| NSW | Mathematical Reasoning | 69 s | **23 min** |
| NSW | Thinking Skills | 60 s | **20 min** |
| VIC | Reading + Verbal (combined rate) | 44 s | **15 min** |
| VIC | Verbal alone | 25 s | **8 min 30 s** |
| VIC | Maths + Quantitative | ~48 s *(estimated, §3.2.1)* | **16 min** |

**Timing is also what makes scores comparable at all.** Once drill scores are ranked
between students, an untimed score is meaningless — one student took eight minutes and
another took an hour. Exam pace serves both purposes at once.

**Reading drills are built in whole passages, not in fixed counts.** A passage and its
questions are one unit: a student must read the passage to answer any of them, so a set
that cuts a passage in half gives some students free reading time and charges others for
it. An NSW reading drill is therefore *n* complete passages, and its timer is
71 s × (total answer slots across those passages). With cloze at 8 blanks per passage,
three passages is 24 slots and a 28-minute timer.

**A per-question timer is not required.** The exam gives a whole-section allowance and
lets candidates distribute it — spending 20 seconds on an easy item to buy time for a hard
one is part of the skill. Drill must mirror that: one timer for the set, free movement
within it.

**Mocks run at true section pace by construction** — a half-length section is half the
questions and half the minutes, so the per-item rate is identical to the real exam.

**Why round 2 uses the same questions.** Round 1 → round 2 on identical questions is a
paired measurement: difficulty is identical by construction, so the score delta is close
to pure learning. Reshuffling questions into new forms for round 2 would destroy that — it
would compare two different papers, which is what mocks already do.

**Order within a form is shuffled per round**, seeded by round number. Same 20 questions,
different sequence. This blunts positional memory ("#4 was C") without breaking the
pairing.

**Rounds are not capped at two.** The round is a property of the *attempt*, not the
question, so rounds 3+ cost nothing.

### 5.2 Mock exams

**Content.** Authored new, one form per school per release. **Half length** — full papers
are too long for regular practice.

| | Full | Half (mock) | Half, MCQ only |
|---|---|---|---|
| NSW | Reading 17/45 min · Maths 35/40 · Thinking 40/40 · Writing 1/30 — 155 min | Reading 9/23 · Maths 18/20 · Thinking 20/20 · Writing 1/30 | **47 q, 62 min** (92 min with writing) |
| VIC | Maths+QR ~75/60 min · Reading+Verbal ~75/55 · Writing 1/40 — 155 min | Maths+QR 38/30 · Reading+Verbal 38/28 · Writing 1/40 | **76 q, 58 min** (98 with writing) |

**Writing does not halve.** One prompt is one prompt. Either keep it at full length or
omit it from the short form — **decision required** (§9). Including it roughly doubles the
sitting, from ~60 minutes to ~95.

**Rules.**

1. Fixed membership and fixed order, identical for every student.
2. Timed at true exam pace, per section.
3. No feedback until the whole paper is submitted.
4. A mock is sat **once**. Improvement across mocks comes from the series, not retakes.
5. Mock questions are never in the drill pool while the mock is live.

**Retiring mocks into drill.** Once a mock is superseded, its questions are released into
the drill pool. At the release rates in §5.3 this more than covers drill growth, so drill
never needs its own authoring after launch.

### 5.3 Release calendar

Frequency ramps as the exam approaches. Early on, students are in school and warming up —
they will mostly drill. Closer to the exam, full-paper practice matters more.

| Period | Cadence | Rationale |
|---|---|---|
| Launch → ~3 months out | **monthly** | students are warming up; drill carries the load |
| ~3 months out → exam | **weekly** | intensive full-paper practice |

Applied to a September 2026 launch:

| | NSW (exam ~7 May 2027) | VIC (exam ~19 June 2027) |
|---|---|---|
| Monthly phase | Sep–Feb (6 mocks) | Sep–Mar (7 mocks) |
| Weekly phase | Mar–Apr (~8 mocks) | Apr–Jun (~11 mocks) |
| **Total forms** | **~14** | **~18** |

**Two calendars, six weeks offset.** NSW intensifies while VIC is still monthly.

### 5.4 Scoring and the parent portal

**Percentile is computed within a form.** Rank a student's score against every other
completed attempt of that same form. Because the paper is identical, the comparison is
sound.

**Round 1 and round 2 attempts use separate percentile pools.** Mixing them would rank a
student on their second pass against students on their first and flatter them.

**Suppress percentile below a minimum cohort.** With fewer than ~30 completed attempts of
a form, show raw score and cohort mean instead. A percentile from six students is noise
and will be read by a parent as fact.

**What the portal shows.** Drill gives *per-category* percentiles — more actionable than a
single mock score, and available from week one:

> Verbal reasoning — 71st percentile · Numerical — 38th · Reading — 55th

Mocks add what drill cannot: performance under timed, full-paper conditions, and a
trend line across the series.

---

## 6. DATA MODEL

### 6.1 Selectly

**`questions`** — add:

| Column | Type | Purpose |
|---|---|---|
| `qbank_id` | uuid, unique, nullable | the upstream qbank row id. **Prerequisite for everything here** — see §7. |
| `form_id` | text, nullable | which form this question belongs to, e.g. `vic-drill-vr-007`, `nsw-mock-003` |
| `form_position` | integer, nullable | 1-based position within the form; fixes the order |
| `form_kind` | text | `drill` \| `mock` |

`schoolIds` already exists and must start carrying real values — see §4.1.

A question belongs to exactly one form, so columns are sufficient; a join table is not
needed. `id` stays the primary key: five tables hold foreign keys onto it
(`question_mastery`, `question_responses`, `drill_responses`, `question_flags`,
`writing_feedback`), so it can never be rewritten.

**`form_attempts`** — new table. One row per student per form per round.

| Column | Purpose |
|---|---|
| `student_id`, `form_id`, `round` | identity of the attempt |
| `score`, `max_score`, `duration_seconds` | the result |
| `started_at`, `submitted_at`, `status` | lifecycle |

Percentile is a query over this table, not a stored value.

**Selection logic must change.** Both selectors are currently random:

- `src/lib/exam/select-questions.ts` — replace random selection with "fetch form N in
  `form_position` order".
- `src/lib/drill/select-drill-questions.ts` — same, **and disable the mastery filter for
  fixed forms**. It currently excludes questions a student has mastered, which would make
  students diverge from each other and break comparability.

**`SectionConfig`** must accept multiple qbank categories per section (§3.3).

### 6.2 qbank

Add to `questions`: `form_id`, `form_position`, `form_kind` — the same values pushed to
Selectly, so forms are authored and reviewed in qbank rather than assembled downstream.

`push_to_selectly.py` must send `qbankId`, the form fields, and **real per-question
`schoolIds`** instead of the hardcoded pair.

---

## 7. CAPACITY, AND THE ONE CRITICAL PATH

Approved questions available for drill at launch:

| Subject | Approved | Drill forms (~20 q) |
|---|---:|---:|
| quantitative_reasoning | 1,629 | 81 |
| mathematics | 1,073 | 53 |
| verbal_reasoning | 1,021 | 51 |
| science_reasoning | 956 | 47 (drill-only, §4.2) |
| reading_comprehension | 634 | 31 |
| **logical_reasoning** | **0** | **0** |

**Mock authoring required for a September launch:**

| | Half-form | Forms | Questions |
|---|---:|---:|---:|
| NSW | 47 | 14 | 658 |
| VIC | 76 *(38 R+V + 38 M+QR, estimated)* | 18 | 1,368 |
| **Total over nine months** | | **32** | **~2,030** |

About **225 questions a month**. Within current output — this session alone produced 303 —
but it is the dominant ongoing cost. Sensitivity to the §3.2.1 estimate is modest: at
Method C (60 questions) the total falls to ~1,880, at Method B (82) it rises to ~2,080.
The estimate does not change whether the plan is feasible.

Halving preserves exam pace exactly, which is the point: 38 questions in 28 minutes is the
same 44 s per item as 75 in 55.

> **`logical_reasoning` is the critical path for NSW.** Thinking Skills is 25% of the NSW
> exam. Its 300 questions are built and validated but all sit `pending`, so NSW has
> neither drill content nor mock content for a quarter of its paper. Reviewing those 300
> yields ~15 drill forms and ~280 of the ~280 mock questions needed. **No other single
> action unblocks as much.**

**Pushed questions are currently unreachable.** `/api/questions/import` is insert-only and
lets Postgres mint its own uuid, so qbank has no handle on the rows it created — all 5,313
approved questions are live and unaddressable. Assigning forms in qbank achieves nothing
until this is fixed. A branch implementing `qbank_id` exists but is unmerged and
undeployed.

---

## 8. ORDER OF WORK

1. **Merge and deploy `qbank_id`**, and backfill the existing rows. Everything else
   depends on it.
2. **Confirm the VIC structure** against ACER's official sample, especially the question
   count for Maths + Quantitative Reasoning.
3. **Review the 300 `logical_reasoning` questions** — unblocks NSW.
4. **Fix `schools.ts`** for the three-component VIC format and multi-category sections.
5. **Add the form columns** to both schemas; assign the existing approved bank to drill
   forms.
6. **Replace random selection** with form-ordered selection in both selectors.
7. **Build `form_attempts`, scoring and the parent portal.**
8. **Begin the monthly mock series**, on two calendars.

Steps 2 and 3 can run in parallel with 1.

---

## 9. DECISIONS STILL OPEN

| # | Decision | Note |
|---|---|---|
| 1 | Writing in half-length mocks — keep at full length, or omit? | It cannot be halved |
| 2 | VIC Maths + Quantitative Reasoning question count | **No longer blocking** — estimated at 75 (§3.2.1) and built to. Verify against ACER's sample pack and correct before the first VIC mock ships |
| 3 | Reading pools — separate per state, or shared? | §4.1; separate is recommended, and RC is the tightest category |
| 4 | `science_reasoning` — drill-only, or add JMSS as a third school? | 956 approved questions |
| 5 | Minimum cohort before a percentile is shown | ~30 suggested |
| 6 | **VIC Reading vs Verbal time split** inside the combined 55-minute paper | Needed to time VIC reading drills. Verbal is targeted at ~25 s; the reading residual cannot be derived until the item split is known. Same ACER sample resolves it as #2 |
| 7 | Can a late-registering student sit already-released mocks? | Affects percentile comparability |

Decision 6 in an earlier draft — the drill time multiplier — is **resolved**: drill runs at
exact exam pace, per §5.1.1.

---

## 10. SOURCES

- [NSW selective high school placement timeline, Year 7 entry 2027](https://education.nsw.gov.au/content/dam/main-education/public-schools/selective-high-schools-and-opportunity-classes/media/Selective_high_school_placement_timeline_v7.pdf)
- [NSW selective high school practice tests](https://education.nsw.gov.au/schooling/parents-and-carers/choosing-a-school-setting/selective-high-schools/placement-test/selective-high-school-practice-tests.html)
- [NSW selective test format — four components](https://braintreecoaching.com.au/nsw-selective-test-format-guide)
- [NSW selective test dates 2027 & 2028](https://www.selectiveguru.com.au/blog/nsw-selective-test-dates-2026-2027-2028-complete-guide)
- [ACER — Victorian Selective Entry High Schools](https://selectiveentry.acer.org/vic)
- [ACER — results and selection](https://selectiveentry.acer.org/vic/results-and-selection)
- [ACER's updated selective entry exam format](https://melbournetutorials.com.au/acers-updated-selective-entry-exam-format-why-has-the-test-structure-changed/)
- [SEHS exam format — components, timing, structure](https://braintreecoaching.com.au/victoria-sehs-exam-format) — note this page still describes the superseded five-component format
- [ACER — Victorian selective entry exam day](https://selectiveentry.acer.org/vic/exam-day) — confirms the 60-minute Maths + Quantitative Reasoning duration
- [Free NSW selective practice tests](https://www.selectiveguru.com.au/blog/free-nsw-selective-practice-tests) — source of the 38-answer-slot figure for NSW Reading
- First-hand student accounts of the 20 June 2026 VIC sitting, recorded in
  `pdfs/selective_verbal_reasoning_TASK.md` §2 and §8
