# SELECTLY TASK 2 — accept writing prompts from qbank

qbank has 106 writing prompts ready and no way to send them. Most of what Selectly needs
already exists; the job is smaller than it looks, and it turns on ONE decision.

## What Selectly already has — do not rebuild any of this

Checked in the repo on 2026-09-04, not assumed:

- `questions` carries `questionType: 'writing'`, plus `promptType`, `wordLimit`, `rubric`
  and `imageUrl`, and the three form columns.
- `/api/questions/import` already accepts writing rows. `validateQuestion` picks
  `writingSchema` on `questionType === 'writing'`, and the insert path already maps
  `promptType`, `wordLimit` and `rubric`.
- `WritingSection.tsx` renders a prompt and takes `stem`, `wordLimit`, `timeMinutes`.
- `writing_feedback` table, `lib/writing/grade-writing.ts`, `/api/writing/submit` and
  `/api/writing/regrade` all exist.
- `vic-seal` in `schools.ts` already has the right writing section: **2 tasks, 40 minutes,
  one clock**, `question_type: 'writing'`.
- `form_attempts.score` / `max_score` are already nullable for writing forms.

So the pipes are laid. What is missing is a place to put part of the content, and an
agreement about two field shapes.

## What qbank holds

106 prompts, all `pending`: **54 Victorian in 27 forms** of 2 prompts each, 42 NSW and
10 JMSS (no forms yet). Each row carries:

    prompt_type        narrative | persuasive | article | diary | email | speech |
                       advice_sheet | news_report | scientific_report | scientific_analysis
    school_type        jmss | victorian_selective | nsw_selective | general
    stimulus_type      text | image | quote | scenario | data
    stimulus_content   the quote, scenario or data table the student reads FIRST
    stimulus_image_desc  what an image prompt should show (no file yet)
    task_instruction   the sentence telling the student what to write
    word_count_min     e.g. 120
    word_count_max     e.g. 180
    time_limit_minutes e.g. 15
    target_year, difficulty, topic
    marking_focus      a JSON array, e.g. ["ideas","structure","language","voice"]
    form_id, form_position, form_kind

## The three gaps

### 1. There is nowhere to put the stimulus — THIS IS THE REAL DECISION

A prompt is two distinct things: a **stimulus** the student reads (a quote, a scenario, a
data table) and a **task** telling them what to write about it. qbank stores them
separately and its review UI shows them as two boxes, because a student needs to see
where the source material ends and the instruction begins.

Selectly's `questions` has one `stem`.

**Preferred: add `stimulus` (text, nullable) to `questions`, and render it above the task
in `WritingSection`.** One column, one migration, a few lines of JSX. `stem` then holds
the task instruction alone, which is what `stem` means everywhere else.

The alternative — concatenating stimulus and task into `stem` with a separator — will
work and will look worse, and it cannot be undone later without reparsing free text.
If you take it, say so, because qbank has to build its sender to match.

For `stimulus_type: 'image'` there is no file yet, only a description. `imageUrl` already
exists on `questions`; leave it null for now.

### 2. `rubric` demands five keys that qbank does not have

`writingSchema` requires an object with exactly `structure`, `argument`, `vocabulary`,
`grammar`, `creativity`, all strings. qbank has `marking_focus`, a free array like
`["ideas","structure","language","voice"]`. These do not line up, and a narrative task
should not be marked on `argument`.

**Decide who owns the rubric.** Either:

- **(a) Selectly owns it** — derive the rubric from `promptType` at grading time, and
  relax `rubric` to optional in `writingSchema`. qbank then sends `marking_focus` as a
  hint or not at all. This is the cleaner split: the marking criteria belong with the
  marker.
- **(b) qbank owns it** — qbank maps `marking_focus` onto the five keys and sends full
  rubric text per prompt. Then the five keys need to stop being mandatory for prompt
  types they do not suit.

(a) is recommended. Whichever it is, tell qbank, because it changes what the sender builds.

### 3. One word limit, two word counts

qbank has `word_count_min` and `word_count_max`; Selectly has a single `wordLimit`, and
`WritingSection` uses it as a ceiling that disables the box.

VIC's two tasks are deliberately different sizes — about 150 words in 15 minutes and
about 250 in 25 — and budgeting across them is the skill being examined. A student who
sees only a ceiling loses half the instruction.

**Add `wordMin` (integer, nullable) and show the range as guidance**, e.g. "aim for
120–180 words", rather than only stopping them at the top. Keep `wordLimit` as the hard
ceiling so nothing existing breaks.

## Also worth doing

- **Per-prompt timing.** `time_limit_minutes` is per prompt (15 and 25); the section is
  one 40-minute clock. Two prompts in one sitting is correct and deliberate — do not add
  two clocks. But the per-prompt figure is useful guidance to show the student.
- **Check the form selector serves a writing form.** `selectFormQuestions` sorts by
  `formPosition`; confirm a `vic-drill-wr-*` form comes back with its two prompts in
  order and that the writing UI is reached rather than the MCQ one.

## What qbank will build once you have decided

`push_to_selectly.py` today knows nothing about the `writing_prompts` table — it reads
`questions` only. qbank will add a writing sender that maps each prompt to the import
shape you settle on, tracks it by `qbank_id` like everything else, and pushes the 27 VIC
forms. **It cannot be written until gaps 1 and 2 are decided**, because those decide the
payload.

## How to know it worked

1. `/api/admin/questions-dump?category=writing` returns the prompts with `formId`,
   `formPosition` and — if you took the recommended path — `stimulus`.
2. Open `vic-drill-wr-001` as a student. Two prompts, in order, one 40-minute clock,
   stimulus visibly separate from the task, a word range shown.
3. Submit both and confirm `writing_feedback` rows appear and `/api/writing/regrade`
   works on them.
