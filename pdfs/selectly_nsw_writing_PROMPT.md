# SELECTLY — make NSW writing servable

Paste everything below the line into a fresh Selectly session.

---

NSW writing. The VIC writing work shipped and is live — 54 prompts across 27 forms,
served through `WritingFormShell`, marked per prompt type. **NSW writing has never been
served, and it is not just a matter of pushing the rows.** Five things in this repo are
written for VIC only, and each one was checked in the code rather than assumed.

qbank holds **42 approved NSW prompts**, all sendable today — `push_writing_to_selectly
--dry-run` reports "To push: 42". Nothing on the qbank side is blocking. What is blocking
is that if they were pushed now, every NSW candidate would get the same one prompt, and a
third of them would be marked on the wrong thing.

Please do not fix the qbank side; there is a question for its owner at the end.

## What is wrong, in the order it hurts

### 1. Every student gets the same writing prompt, always

`src/lib/exam/select-questions.ts`, `selectWritingQuestion`:

```ts
const [q] = await db.select().from(questions)
  .where(and(eq(questions.category, 'writing'), eq(questions.active, true),
             sql`${questions.schoolIds} @> ARRAY[${schoolId}]::text[]`))
  .limit(1)
```

No `orderBy`, no student history, no rotation. Push the 42 NSW prompts and 41 of them are
unreachable — every mock, every student, the same task. Postgres is free to return any
row, so it is not even predictably the same one.

The MCQ path immediately above it already does this properly: `selectQuestionsForSection`
reads `question_mastery`, drops what the student has mastered, and orders by least
recently seen. Writing gets none of it.

**Please make writing selection rotate the same way the MCQ path does** — least recently
seen for this student, from that exam's pool, using the history already recorded in
`question_responses`.

### 2. It returns ONE prompt into a section that asks for two

`vic-seal`'s writing section in `src/lib/config/schools.ts` is `question_count: 2`,
40 minutes — that is the 2026 paper and the reason qbank deals VIC writing in pairs. But
both callers ask for one prompt and insert one row:

- `src/lib/exam/start-action.ts:55-64`
- `src/app/api/exam/start/route.ts:102-118`

So **a VIC mock currently serves half its writing section.** NSW is `question_count: 1`
so NSW is not affected by this half, but it is the same function and the same fix:
honour `section.question_count` instead of taking the first row.

This one is a live defect on VIC, not preparation for NSW. It is worth fixing first.

### 3. Three of NSW's eight prompt types are marked on the wrong dimensions

`src/lib/writing/rubrics.ts` maps five types and falls back to ARGUED for anything else:

```ts
const BY_TYPE = { persuasive: ARGUED, article: ARGUED, speech: ARGUED,
                  narrative: NARRATED, diary: NARRATED }
```

That comment is accurate about VIC — those are the five types VIC dealt. **NSW uses
eight**, and the three it adds have no entry:

| type | NSW prompts | marked as today |
|---|---:|---|
| persuasive | 6 | ARGUED ✓ |
| narrative | 6 | NARRATED ✓ |
| speech | 5 | ARGUED ✓ |
| article | 5 | ARGUED ✓ |
| diary | 5 | NARRATED ✓ |
| **news_report** | **5** | ARGUED ✗ |
| **email** | **5** | ARGUED ✗ |
| **advice_sheet** | **5** | ARGUED ✗ |

**15 of 42 prompts — over a third — would be marked on "coherence of position and
quality of argument".** An advice sheet has no position to be coherent about. A news
report that argues a case is a worse news report. This is precisely the fault the VIC
rubric work removed, arriving again from a different direction.

Those three are neither argued nor narrated: they are **informative/functional** writing,
judged on whether the reader ends up correctly informed and whether the register fits the
form. **A third dimension set is needed** — something like accuracy and selection of
information, structure appropriate to the text type, clarity, and register/audience fit.
You own the marking language; the VIC sets are the model to follow.

### 4. Writing form timing is hardcoded to the VIC prefix

`src/lib/forms/timing.ts`:

```ts
export const WRITING_FORM_SECONDS = 40 * 60
const WRITING_FORM_PREFIX = 'vic-drill-wr'

export function formTimerSeconds(formId, slots) {
  if (formId.startsWith(WRITING_FORM_PREFIX)) return WRITING_FORM_SECONDS
  ...
}
```

An `nsw-drill-wr-*` form would fall through to `formSlotAllowance`, find no prefix, and
return `null` — "this form cannot be served", which is at least the safe failure the
comment promises, but it is a failure.

NSW writing is **one task in 30 minutes**, and the prompts carry their own
`time_limit_minutes`: 32 of the 42 are 30 minutes, 10 are 25. The word ranges differ with
them — 200-320 for the 30-minute prompts, 300-500 for the 25-minute ones. So the NSW
timer is **per prompt**, not a fixed constant like VIC's single 40-minute clock across a
pair. Take it from the prompt's own `time_limit_minutes`, falling back to the section
config's 30.

### 5. An NSW writing form would display as a raw id

`src/lib/forms/labels.ts` `COMPONENT_LABELS` lists `vic-drill-wr` → "VIC Writing" and has
no NSW writing entry, so `nsw-drill-wr-003` would render as `nsw-drill-wr-003` to the
student. One line, but it is the difference between a set the student can name and a
string.

## What is already right — do not re-do it

- **`nsw-shspt`'s writing section is correct.** 1 task, 30 minutes, `question_type:
  'writing'`, `categories: ['writing']`. Verified in `schools.ts`. Nothing to change.
- **`/api/drill/writing-submit` already handles NSW.** Line 134 derives the school from
  the form prefix and returns `nsw-shspt` for anything not `vic-`.
- **`questions-dump` returns everything qbank needs to verify with** — `qbankId`,
  `formId`, `formPosition`, `formKind`, and the writing fields. Confirmed today by
  reading production back: 2,441 NSW and 5,190 VIC questions all live with the form
  qbank holds, 0 disagreeing.
- **`WritingFormShell` and `DrillFormPage` are exam-agnostic.** `DrillFormPage` branches
  on `options == null` rather than the form id, exactly so a writing prompt is served
  correctly however it was dealt. That was the right call and it is why NSW needs no new
  shell.

## The question for qbank's owner — please raise it, do not act on it

qbank has not dealt forms for the 42 NSW prompts. The reasoning recorded there is *"NSW
sets one prompt, and a form of one adds nothing."*

**Reading this repo, that looks wrong.** Drill is entirely form-driven —
`selectQuestionsForForm(formId)`, and `familyAttemptCounts` lists what a student can sit
by querying `questions.form_id`. A prompt with no `form_id` is not reachable from drill at
all; only the mock path finds it, and that path is defect 1 above. So a form of one is not
a redundant wrapper — **it is the only way an NSW writing prompt becomes something a
student can choose to practise**, and it is what makes "you have sat 12 of 42" possible
at all.

If the owner agrees, qbank deals `nsw-drill-wr-001..042`, one prompt each, and this app
needs items 4 and 5 for them to serve. If not, NSW writing exists only inside a mock and
items 4 and 5 can be skipped — but item 1 becomes more urgent, not less, because the mock
path would then be the only path.

## Suggested order

1. **Item 2** — the VIC mock is serving one writing task where the paper sets two. Live
   defect, affects students today.
2. **Item 1** — writing selection rotates per student. Nothing NSW can ship without it.
3. **Item 3** — the informative rubric set. 15 NSW prompts are wrong without it.
4. **Items 4 and 5** — only if the owner says NSW writing gets forms.
5. **Tell qbank.** One command sends the 42 prompts:
   `python -m pipeline.push_writing_to_selectly`, and `--verify` reads them back field by
   field.

Repo: `/scratch/selectly`. Latest commit `012d54f` "feat: serve VIC writing forms through
their own runner".
