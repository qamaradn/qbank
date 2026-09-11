# Selectly → qbank: deal the NSW writing forms, and retire one file

Reply to `pdfs/selectly_nsw_writing_PROMPT.md`. Every claim below was checked against the
Selectly working tree, not against the handover.

Noted on `formId` — verified closed, not raised again.

---

## 1. The decision you put back to me: deal the forms. You were right the second time.

Deal `nsw-drill-wr-001` … `nsw-drill-wr-042`, one prompt each.

Your original reasoning ("NSW sets one prompt, so a form of one adds nothing") is wrong,
and the code says so plainly. `listStudentForms` builds the student's set list from
`questions.form_id IS NOT NULL` (`src/lib/forms/availability.ts:343-346`). A prompt with
no form is not merely awkward in drill — **it is invisible there**, reachable only through
the mock path. Three more things are keyed on the form rather than the question:

- free-tier allowance and form locking count by `formFamily`
- rounds are `(student, form, round)` rows in `form_attempts`
- "you have sat 12 of 42" is a count of `form_attempts` rows

A form of one is not a redundant wrapper. It is the only way an NSW writing prompt becomes
something a student can choose, and the only way progress through the 42 can be counted.

---

## 2. All five of your findings were real and are now fixed

Shipped and live on `main` — `45465b6`, `33a0383` (plus `012d54f` for the drill runner).

| # | Your finding | Status |
|---|---|---|
| 1 | `selectWritingQuestion` had `.limit(1)`, no ordering, no student history | Fixed |
| 2 | One prompt returned into vic-seal's two-task section | Fixed — this was live on VIC |
| 3 | Three NSW prompt types fell through to the argued rubric | Fixed |
| 4 | `formTimerSeconds` hardcoded `vic-drill-wr` | Fixed |
| 5 | No `nsw-drill-wr` in `COMPONENT_LABELS` | Fixed |

Two corrections to the detail:

**Item 1 — your recommended fix would have been a silent no-op.** You said to follow the
MCQ path, which "already rotates on mastery and least-recently-seen." `question_mastery`
rows are written **only** for `isCorrect === true` (`src/app/api/exam/submit/route.ts:62`).
A writing response has `is_correct` NULL permanently, so **no writing prompt ever acquires
a mastery row**. A mastery-ordered rotation reads all 54 as never-seen and returns an
arbitrary order while appearing to rotate. It now reads `question_responses`, COALESCEing
`answered_at` to the attempt's `started_at` — a prompt served and left blank is still spent.

**Item 2 was bigger than "return two instead of one."** Taking two prompts by independent
rotation would have been wrong. Checked against the live dump, your VIC pairing is
structural, not incidental:

- position 1 is **always** 130–170 words / 15 min
- position 2 is **always** 220–290 words / 25 min
- 25 of 27 forms pair an argued task with a narrated one

Independent rotation would cheerfully serve two short tasks, or two narratives. Selection
now rotates over **form groups**, the way a reading passage and its questions are already
treated as one unit. **Keep dealing VIC that way** — Selectly now depends on it.

**Item 4 was less severe than written.** `nsw-drill-wr` matched no allowance prefix either,
so `formTimerSeconds` returned `null` and the form was *refused as untimeable*, not served
at 40 minutes. A blocked form, not a mistimed one.

Also fixed, neither of which you raised:

- `ExamShell` rendered `section.questions[0]` and posted only that one. Fixing the selector
  alone would have been **worse than the bug**: VIC would have got a second
  `question_responses` row the candidate never saw, and the new rotation would have marked
  that prompt spent — every form's extended task burned unseen. The writing section now
  renders every task with per-task drafts under one clock.
- The exam page's response query had **no `ORDER BY`**. Beyond task order, that meant a
  reload mid-mock could renumber an MCQ section under the candidate.

---

## 3. The contract for the 42 forms

| field | value | why it matters |
|---|---|---|
| `form_id` | `nsw-drill-wr-001` … `-042` | **Exact prefix `nsw-drill-wr`.** `COMPONENT_LABELS` matches on it; `nsw-drill-write-…` would show the student a raw id. Must match `^[a-z0-9]+(-[a-z0-9]+)*$`, ≤50 chars, ending in the set number — `formFamily` strips `-\d+` to get the family. |
| `form_position` | `1` | Single-prompt form. |
| `form_kind` | `drill` | |
| `school_ids` | must include `nsw-shspt` | |
| `time_limit_minutes` | **30 or 25, never null** | A single-prompt writing form is now timed **by its own prompt**. Null falls back to 30, which silently gives your ten 25-minute prompts five minutes too many. |
| `word_limit` / `word_count_min` | both set | Shown as "Write N–M words". `word_count_min` must be ≤ `word_limit` or the import rejects the row. |
| `prompt_type` | one of the eight | Drives the marking rubric — see below. |
| `stimulus` / `stimulus_type` | set where the prompt has one | You said NSW often sets a task with no stimulus; null is fine and renders correctly. |

**Prompt types and how each is marked.** Selectly owns the marking dimensions; your
`marking_focus` is not read.

| `prompt_type` | marked as |
|---|---|
| `persuasive`, `article`, `speech` | Argument · Creativity |
| `narrative`, `diary` | Character & Plot · Imagination & Voice |
| `news_report`, `email`, `advice_sheet` | **Information & Accuracy · Audience & Purpose** |

Separator variance is tolerated (`news-report`, `News Report` all resolve), but **an
unknown type still falls back to the argued set** — so if NSW has a ninth type, tell me
before you push rather than letting it mark an advice sheet on quality of argument.

The `rubric` column is optional and read by nothing. Don't populate it.

---

## 4. Retire `run_data/output/vic_repairs_recovered_20260824.json` — do not restore it

This was on both our lists as "restore into qbank, then push." **Doing that would cause a
regression.** I compared all five ids across qbank's SQLite, the file, and production:
**qbank and production agree exactly on all five. The file is the outlier.**

Clearest case, `4d26d3e0` (vic-drill-mq-002 #15), where all three share a stem so the
options compare directly:

| | option C |
|---|---|
| qbank + prod | `27 wickets` |
| the file | `-1 wickets` |

`-1 wickets` is the broken distractor. `27` is the season total — the sensible wrong
answer. **qbank already holds the repaired version.** The other four differ further still:
qbank and prod share a stem the file does not have at all (`280 runs` vs `275 runs`; a
tennis-court question vs a ball-boy question), and three have a different `correct_answer`
in the file.

The August snapshot was superseded by later qbank work that has already been pushed.
Restoring it would overwrite five current questions with older — in one case broken —
content and push that live. Rename it `.superseded` or delete it. The "permanent
divergence" worry from August is retired: there is none.

---

## 5. After you push

Run `verify_pushed_forms.py` as usual. I will then check, from
`/api/admin/questions-dump?category=writing`:

- 42 NSW prompts, each alone in its own form, positions all `1`
- `time_limit_minutes` present on all 42 and splitting 32/10 across 30 and 25 minutes
- `word_count_min` ≤ `word_limit` on all 42
- every `prompt_type` among the eight, with the three informative ones resolving to
  Information & Accuracy rather than Argument
- the 54 VIC prompts unchanged, still paired short-then-extended

Two questions I could not answer from the Selectly side:

1. What are the NSW word ranges per prompt type? Selectly renders whatever you send; I
   only want to know the intended shape so I can tell a bad push from a deliberate one.
2. Are all 42 single-task, or does any NSW set pair two prompts the way VIC does? The
   code handles both, but the timer treats them differently — a two-prompt NSW form would
   take the 30-minute section fallback rather than the prompt's own limit.
