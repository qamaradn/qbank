# HANDOVER TO SELECTLY — what changed, and what the app must implement

> Written 2026-08-11 from the qbank side. Audience: whoever works on the Selectly app next.
> Read this before touching question selection, the drill flow, or the import endpoint.
>
> Companion documents, both in `qbank/pdfs/`:
> `selective_exam_delivery_SPEC.md` (the full delivery design — §5 drill, §6 data model)
> and `vic_content_taxonomy_TASK.md` (what VIC content exists and why).
>
> Every claim below is measured against the qbank database on 2026-08-11 unless marked
> otherwise. Where something is an estimate, it says so.

---

## 0. THE ONE THING TO READ IF YOU READ NOTHING ELSE

**Selectly and qbank have silently diverged, and the divergence cannot currently be
repaired.**

5,321 questions have been pushed to Selectly. Since then, in qbank:

| | Count |
|---|---:|
| Pushed rows whose **options were reordered or edited** | **3,133** |
| Pushed rows now **rejected** in qbank but still live in Selectly | **7** |
| Pushed rows moved back to `pending` | 4 |

Those 3,133 are not cosmetic edits. They are answer-key repairs: the option order changed
and `correct_answer` moved with it. **Selectly is currently serving the old order with the
old key letter for 3,133 questions.** Anything scored against them is scored against a
key that qbank no longer agrees with.

The cause is §1 below. Fixing §1 is the prerequisite for every other item in this
document.

**The code for §1 already exists on both sides and is not deployed.** Selectly commit
`c52ffa9` on the unmerged local branch `feature/qbank-id-addressability` adds the column,
the upsert, and `qbankId` addressing in `questions-fix`. Re-read on 2026-08-15, it is
better than this document previously credited: the import upserts on `qbankId`, keeps
`questions.id` stable, and **deliberately excludes `active` from the update set**, so a
re-push cannot resurrect a question you deactivated. So §1 is a **merge, deploy, migrate
and verify** job, not a build job. Until it ships, everything below stays blocked.

**A hazard that will bite on the reload.** qbank's tracking file
(`run_data/db/pushed_to_selectly.json`) records **5,321 questions as already pushed**.
If `questions` is wiped without clearing it, the reload sends almost nothing — the pusher
believes Selectly already holds them. **The wipe must be paired with
`push_to_selectly.py --reset-tracking`.** This is now the only remaining use of that flag:
tracking is otherwise content-hashed and self-correcting (§8.2).

**The review loop is now specified in §8.** Read it before building anything in §6 —
it is what the first ten forms are for, and it adds one small requirement to the CSV
export that nothing else in this document mentions.

---

## 1. `qbank_id` — THE CRITICAL PATH

### What is wrong

**qbank already sends the field.** `pipeline/push_to_selectly.py` has always included
`qbankId` in the payload, with a comment saying Selectly upserts on it. It does not.
`/api/questions/import` **drops the field**, is insert-only, and lets Postgres mint its own
`uuid` for each row. qbank therefore has **no handle on the row it created**.

This is a Selectly-side fix only. No change to the pusher is needed for `qbankId` itself
(the form fields and `schoolIds` in §4.3 are a separate matter). Until the fix ships there is
no key on which to issue an update, a withdrawal, or a correction, and all 5,321 pushed
questions are unaddressable.

Selectly already has the machinery to act on a question — `questions.active` (both the
exam and drill selectors honour it) and `/api/admin/questions-fix` — but both address rows
by **Selectly's** uuid, which qbank never learns.

### The fix

1. **Add `qbank_id` to `questions`**: `uuid`, unique, nullable, indexed.
2. **`/api/questions/import` must stop discarding it and store it.** The field is already
   arriving in every payload; qbank ids are uuid-v4, so they can be used directly. Do **not** make `qbank_id` the primary key — five tables hold
   foreign keys onto `questions.id` (`question_mastery`, `question_responses`,
   `drill_responses`, `question_flags`, `writing_feedback`), so `id` can never be rewritten.
3. **Make import upsert on `qbank_id`**, not insert-only, so a corrected question replaces
   its predecessor instead of duplicating it.
4. **Do not backfill — wipe and reload instead (decided 2026-08-12).** See §1.1.
   `pipeline/backfill_qbank_ids.py` exists and works, but it is no longer the plan.

### 1.1 The decision: wipe `questions` and reload, do not backfill

**No students are onboarded.** The only two accounts are a reviewer and an admin, and every
question will be re-reviewed from scratch after the reload. There is therefore no student
history to preserve, which removes the only real objection to a wipe.

That makes the clean reload strictly better than a backfill:

- No stem-matching. Nothing is guessed at, nothing is left ambiguous.
- **No orphans.** A backfill leaves unmatched rows with `qbank_id NULL`; re-pushing then
  inserts a *second* copy while the stale original keeps being served. A wipe cannot
  produce that state.
- The 156 live §6 verbal questions are withdrawn by simply not sending them (§5.2).
- 956 `science_reasoning` questions stop being imported at all (§5.4).
- `qbank_id` is set on insert rather than reconstructed.

**Scope it to `questions`, plus `question_flags`.** Not the whole database — accounts,
school config and the two reviewer logins must survive. `question_flags` holds the
reviewer's earlier notes, which have already been actioned in qbank.

**The migration and deploy are still required.** A wipe removes the *backfill* step, not the
*addressability* step. Without `qbank_id` stored on import you are back to unaddressable
rows the first time a question needs correcting.

**Do steps 2 and 3 of §6 before the wipe**, or you reload form-less questions today and
reload again later — which is the confusion the wipe exists to avoid.

### What unblocks the moment this lands

- Pushing the 117 NSW drill form assignments (§2)
- Withdrawing 149 banned-type verbal questions, 147 of which are live (§5)
- Applying 3,133 answer-key and distractor repairs already made in qbank (§4)
- Deactivating 7 questions rejected in qbank but still served

---

## 2. FIXED FORMS REPLACE RANDOM SELECTION

This is the central change to how the app works. Full rationale in delivery spec §5.1.

### Why

Random selection makes percentile and progress tracking meaningless — two students who
"scored 70% on a reading drill" did not sit the same test. Fixed forms make a score
comparable between students and over time.

### Rules the app must enforce

1. **Fixed membership and fixed order.** Every student sees Drill Set 7 identically,
   in `form_position` order.
2. **Timed at exact exam pace** — §3 below. Not a generous approximation.
3. **No feedback during the attempt.** On submit: score first, then answers and
   explanations unlock.
4. **A completed form is locked** until every form in that category has been attempted.
   The enforced gap is deliberate spaced repetition — the student must recall, not re-read.
5. **When a category's forms are exhausted, the counter resets and round 2 begins on the
   same forms with the same membership.** Round 2 is scored separately.

### Selection code that must change

| File | Change |
|---|---|
| `src/lib/exam/select-questions.ts` | Replace random selection with "fetch form N in `form_position` order" |
| `src/lib/drill/select-drill-questions.ts` | Same, **and disable the mastery filter for fixed forms** |

The mastery filter currently excludes questions a student has already mastered. Under fixed
forms that would make students diverge from one another and destroy the comparability the
whole change exists to create.

### State of the deal, qbank side

117 NSW drill forms are assigned over 2,441 questions (`tools/assign_forms.py`, manifest in
`run_data/output/forms/nsw_forms_manifest.json`). All are `form_kind='drill'`; no mock forms
are dealt yet.

**The deal is provisional.** It covers approved *and* pending questions, because gating on
approval would have produced almost nothing — NSW sits near zero approved. Some form members
will therefore be rejected at review. Before launch that is repairable in qbank
(`assign_forms.py --repair` lifts them out and renumbers). **After launch it is not**:
removing a question re-bases every score already recorded against that form, so the fix
moves downstream to `questions.active`, leaving form membership untouched.

---

## 3. TIMING — EXACT EXAM PACE

**Speed is the skill being examined.** Candidates who fail typically run out of time, not
ideas. A drill that allows more time than the exam trains the wrong thing and reports a
score the student cannot reproduce on the day.

**The rule.** A form's timer is *(number of answer slots) x (that component's exam allowance
per slot)*, rounded to the nearest 30 seconds.

| Exam | Category | Allowance / slot | 20-slot form |
|---|---|---:|---:|
| NSW | Reading (incl. cloze) | 71 s | 24 min |
| NSW | Mathematical Reasoning | 69 s | 23 min |
| NSW | Thinking Skills | 60 s | 20 min |
| VIC | Reading + Verbal (combined) | 44 s | 15 min |
| VIC | Verbal alone | 25 s | 8 min 30 s |
| VIC | Maths + Quantitative | ~48 s *(estimated)* | 16 min |

The VIC maths figure is an estimate: ACER does not publish a question count for the merged
paper, and the planning figure of 62 questions is rated Medium confidence.

**Reading forms are dealt in whole passages, not fixed counts.** A passage and its questions
are one unit — a student must read the passage to answer any of it. Because passages carry 4
to 8 questions, a "four passage" set ranges from 16 to 32 slots, and the timer would swing
from 19 to 38 minutes for what claims to be the same test. Forms are therefore packed to a
**slot target**, and the timer follows the slot count automatically.

---

## 4. DATABASE CHANGES

### 4.1 Selectly — `questions`

| Column | Type | Purpose |
|---|---|---|
| `qbank_id` | uuid, unique, nullable, indexed | upstream qbank row id. **Prerequisite for everything** |
| `form_id` | text, nullable | e.g. `nsw-drill-ts-007`, `vic-drill-vr-003`, `nsw-mock-002` |
| `form_position` | integer, nullable | 1-based order within the form |
| `form_kind` | text | `drill` \| `mock` |

A question belongs to exactly one form, so columns suffice — no join table.

`schoolIds` already exists and **must start carrying real per-question values**. It is
currently a hardcoded pair. Note for §5: the drill selector ignores `schoolIds` entirely, so
it cannot be used to withdraw a question from drill.

### 4.1a Selectly — `writing_prompts` needs the same three columns

**A writing drill is a PAIR, not a prompt.** The VIC paper sets two tasks in 40 minutes —
a short one of ~150 words and an extended one of ~250 — and the drill has to serve both.

This is the one component that does not survive being halved. For MCQ, halving the
question count and the clock preserves seconds-per-question, so a 20-question drill
predicts a 40-question paper. Writing has no equivalent invariant:

- **Budgeting across two tasks is the skill.** A candidate who spends 28 of the 40 minutes
  on the piece they are enjoying has failed the paper, and will never discover that by
  practising one piece at a time.
- **The second task is written tired**, by someone who has already spent their best ideas.
  That is where marks are lost, and a single-prompt drill never reaches it.
- The two tasks are different shapes — at 150 words every "and also" is unaffordable, at
  250 there is room to develop. The candidate has to feel the difference.

| Column | Type | Purpose |
|---|---|---|
| `qbank_id` | uuid, unique, nullable, indexed | same rationale as `questions` |
| `form_id` | text, nullable | e.g. `vic-drill-wr-004` |
| `form_position` | integer | **1 = short task, 2 = extended task** |
| `form_kind` | text | `drill` \| `mock` |

**27 VIC writing drill forms are dealt** (`tools/assign_writing_forms.py`, manifest in
`run_data/output/forms/vic_writing_forms_manifest.json`). Every form is one creative plus
one persuasive task, one short plus one extended, totalling exactly 40 minutes. All 54
prompts are `pending`, so none should be served until reviewed.

Two things the app must do differently for a writing form:

1. **Serve both prompts as one timed sitting of 40 minutes**, not two 15/25-minute
   sittings. Whether the candidate is free to move between the two tasks within the 40
   minutes is the app's call, but the clock must be one clock — that is the whole point.
   The per-prompt `time_limit_minutes` (15 and 25) is guidance to show the candidate, not
   a timer to enforce.
2. **Position order is a qbank convention, not a fact about the paper.** ACER does not
   publish which task comes first. Position 1 is the short one here; if that turns out to
   be wrong it is one `UPDATE` in qbank and no app change.

Writing is not scored out of a mark total the way MCQ is, so `form_attempts.score` /
`max_score` do not apply to a writing form. It needs its own result shape, or those
columns need to be nullable.

### 4.1b `vic-seal` in schools.ts describes an exam that no longer exists

`src/lib/config/schools.ts` still carries the **pre-2026 five-component format**: four
sections totalling 120 minutes — Verbal 30q/30min, Numerical 35q/35min, Reading 30q/30min,
Written Expression 1 task/25min.

ACER restructured for 2026. The paper is **three components, 2h35m**:

| Component | Time | Questions | Per question |
|---|---:|---:|---:|
| Mathematics and Quantitative Reasoning | 60 min | ~62 | ~58 s |
| **Reading and Verbal Reasoning (ONE section)** | 55 min | 75 | 44 s |
| Writing — two tasks | 40 min | 2 | — |

Two consequences the app cannot avoid:

1. **Reading and Verbal are one section, so a VIC drill form mixes them.** The 66
   `vic-drill-rv-*` forms each hold 15–18 reading questions (whole passages, never split)
   and 20–22 verbal, in one 27-minute timed run. A selector that fetches by a single
   `category` cannot serve these — it has to fetch by `form_id`.
2. **`written-expression` as configured (1 task, 25 min) cannot hold a VIC writing form**,
   which is 2 prompts in 40 minutes (§4.1a).

VIC drill forms are dealt at half the real paper at the real paper's pace, the same rule
NSW uses:

| Form prefix | Forms | Questions | Per form | Timer |
|---|---:|---:|---:|---:|
| `vic-drill-mq-*` | 87 | 2,691 | 30–31 | 29–30 min |
| `vic-drill-rv-*` | 66 | 2,499 | 37–38 | 27–28 min |
| `vic-drill-wr-*` | 27 | 54 prompts | 2 | 40 min |

### 4.1c `mathematics` must route on source book, not category

Fixed in `push_to_selectly.py` on 2026-08-12. `mathematics` was mapped wholesale to
`nsw-shspt`, which sent **642 Year 9 VIC questions** (`year9_maths` 542, `ma_vic_stats`
100) into a paper sat in **Year 6**, and left vic-seal's own maths component with nothing.
It now routes per book, exactly as reading does:

    year7_nsw_maths, ma_nsw_selective  -> nsw-shspt
    year9_maths, ma_vic_stats          -> vic-seal

**vic-seal therefore needs a section that accepts these 642.** Either a `mathematics`
section, or fold them into the merged Maths + Quantitative component above — the latter
matches the real paper, where maths and quantitative are one 60-minute section.

An unknown maths book routes to **nowhere** rather than to both exams. Reading
over-serves an unknown book so somebody notices; maths must not, because the two banks
are two school years apart and a wrong guess is worse than no guess.

### 4.2 Selectly — `form_attempts` (new table)

One row per student per form per round.

| Column | Purpose |
|---|---|
| `student_id`, `form_id`, `round` | identity of the attempt |
| `score`, `max_score`, `duration_seconds` | the result |
| `started_at`, `submitted_at`, `status` | lifecycle |

**Percentile is a query over this table, not a stored value.**

### 4.3 qbank — already applied, for reference

`form_id`, `form_position`, `form_kind` exist in `db/schema.sql` on **both** `questions`
(migration `db/migrations/001_form_columns.py`) and `writing_prompts` (migration
`db/migrations/002_writing_form_columns.py`), both applied. Forms are authored and reviewed
in qbank and pushed down, not assembled in the app.

**`push_to_selectly.py` does not push writing prompts at all yet** — it sends `questions`
only. A writing push path is still to be written, and needs `/api/writing-prompts/import`
or equivalent on the Selectly side.

`push_to_selectly.py` **now sends** `qbankId` (it always did), the three form fields, and
real per-question `schoolIds`. **Selectly's import schema must be extended to accept
`formId`, `formPosition` and `formKind`** — zod currently strips them silently, so they
arrive and are discarded.

### 4.4 A constraint that will bite you: `passageId`

Selectly derives `passageId` by **hashing the passage text**. Two rows whose passage differs
by a single character become two separate passages, and the student is shown the same
passage twice in one drill.

This matters now because 84 newly authored VIC reading questions deliberately share their
passage text byte-for-byte with existing ACT questions so they join the same group. **Any
transformation applied to `passage` on import — trimming, unicode normalisation, newline
rewriting — will split those groups.** Pass the passage through unchanged.

---

## 5. CONTENT CHANGES SELECTLY SHOULD EXPECT

### 5.1 New source books arriving (all `review_status='pending'`)

| `source_book` | Count | What it is |
|---|---:|---|
| `vr_vic_acer` | 523 | VIC verbal — vocabulary, antonyms, sentence completion, shades of meaning, word groups |
| `rc_vic_narrative` | 156 | VIC reading — authored narrative passages |
| `ma_vic_stats` | 100 | VIC maths — statistics and probability, 34 with inline SVG figures |
| `rc_vic_inference` | 84 | VIC reading — new questions on **existing ACT passages** (see §4.4) |
| `rc_vic_persuasive` | 81 | VIC reading — authored persuasive passages |
| `rc_vic_poetry` | 74 | VIC reading — 12 authored poems |

**None of these should be imported yet** — they are unreviewed. They are listed so the
category mapping and any `source_book` filters are ready.

Poetry passages use **markdown hard line breaks** (two trailing spaces). Selectly renders
the passage as plain text in a `white-space: pre-wrap` div, which is correct; do not run it
through a markdown emphasis pass, or the trailing spaces and any `*` will surface.

### 5.2 Banned-type verbal questions — resolved by the reload

**158 verbal questions**, of which **156 are approved and served today**, are of types the
VIC brief says never to generate: dictionary/alphabetical ordering (61), letter and number
codes (50), hidden words (32), anagrams (11), alphabet position (4). Representative stems:
*"If MAP = 13116, what does POT equal?"*, *"Find the hidden word in 'She listened with
attention.'"*, *"Arrange the following words in dictionary (alphabetical) order"*.

Earlier drafts of this document said 149 and CLAUDE.md said 166. Both came from ad-hoc
classifiers that were never committed. The figure is now derived by
`tools/vr_banned_types.py`, which is committed, tested, and records which rule fired on
each row. **158 is the number.**

`push_to_selectly.py` no longer sends them, so the reload withdraws them at no cost. No
`active=false` pass is needed.

### 5.4 Two categories that will not be imported

- **`science_reasoning`, 956 approved.** No section in either exam maps to it — it is parked
  for JMSS. Importing it would add 956 rows that are never served.
- **A note on `mathematics`, 1,073 approved.** All of it routes to nsw-shspt, whose entry
  point is **Year 7**. 542 of those rows come from `year9_maths`. Worth a look before
  launch: Year 9 material in a Year 7 paper is a difficulty mismatch, not a bug in the
  routing. Flagged, not acted on.

### 5.3 Bank totals as at 2026-08-11

9,315 questions: 5,306 approved, 3,906 pending, 103 rejected.

**The pending queue is what gates launch, not authoring.** Drill serves the approved bank.
Around 954 NSW Thinking Skills, 649 NSW Reading and ~1,018 newly authored VIC questions have
never been looked at by a human.

---

## 6. SUGGESTED ORDER OF WORK

**Revised 2026-08-15 to a ten-form pilot.** The original plan opened the whole approved
bank to the reviewer at once. It now runs 273 questions through the entire loop first —
wipe, reload, review, flag, export, fix in qbank, re-push — because if the CSV is missing
a column or the upsert misbehaves, that is an afternoon lost rather than a fortnight of
review done against a broken pipe. The remaining forms open once a round has completed
end to end.

1. **`qbank_id`** — merge `feature/qbank-id-addressability`, apply
   `supabase/migrations/0001_add_questions_qbank_id.sql`, deploy. The backfill step is
   dropped: §1.1 wipes instead, so there is nothing to match. Nothing else can proceed
   first.
2. **Add `form_id`, `form_position`, `form_kind`** to the `questions` table **and to the
   import zod schema** — they are being sent already and silently dropped.
3. **`form_attempts` table and the two selector changes** — fixed forms and exact-pace
   timing.
4. **Wipe `questions` and `question_flags`** (§1.1).
5. **Reload the pilot.** `push_to_selectly.py --reset-tracking`, then push with
   `--forms` naming the ten (§8.1). The reset is mandatory — see §0. This single step
   replaces the old steps 2, 3, 5 and 6: the repairs, the rejected-but-live rows, the 158
   banned verbal types and the form assignments all resolve because the bank is rebuilt
   from qbank's current state rather than patched toward it.
6. **Add `qbank_id` to the flagged-questions CSV export** (§8.3). Small, and the review
   loop cannot close without it.
7. Open the remaining forms once one review round has run end to end. VIC content import
   follows the same path.

---

## 7. OPEN QUESTIONS FOR THE SELECTLY SIDE

These are decisions qbank cannot make alone.

- **Does a locked form unlock per category or per exam?** §5.1 rule 5 says a form relocks
  until every form *in that category* is attempted. Confirm that is the intended granularity.
- **What happens to an in-progress form when a question in it is deactivated?** Recommended:
  the attempt keeps its original composition and scores out of the original maximum;
  deactivation applies to attempts started afterwards. Otherwise scores shift mid-attempt.
- **Round 2 scoring** — is a second-round score shown alongside the first, or does it
  replace it in the parent portal?
- **Mock forms do not exist yet.** The plan is that mocks are authored fresh, born
  `form_kind='mock'`, and retire into drill when superseded. 19 mock forms are needed for a
  September launch with weekly mocks over the final three months. No mock form has been
  dealt in qbank; nothing in Selectly needs to handle `form_kind='mock'` until they are.

---

## 8. THE REVIEW LOOP (added 2026-08-15)

**Decision: qbank and Selectly never talk to each other automatically.** qbank does not
read Selectly's database; Selectly does not call qbank. The only channels are the push
(qbank → Selectly, over HTTPS) and a CSV a human carries the other way. This is
deliberate — the owner's call — and everything below is built to that constraint.

### 8.1 The pilot: ten forms, 273 questions

| Exam | Forms | Questions |
|---|---|---:|
| VIC | `vic-drill-mq-001..003`, `vic-drill-rv-001..002` | 169 |
| NSW | `nsw-drill-read-001`, `nsw-drill-math-001..002`, `nsw-drill-ts-001..002` | 104 |

Split within each exam is proportional to each component's share of its forms, so the
reviewer sees every question type the app will serve. All ten are approved in qbank
(`tools/approve_forms.py`, revertible) and carry `form_id`/`form_position`/`form_kind`.

**Approval here does not mean reviewed.** It is what makes a question reachable by the
pusher — `fetch_approved` sends `review_status='approved'` and nothing else. Every one of
the 273 is unread by a human; the reviewer IS the check. Worth knowing which side of that
is which: the VIC forms have been blind-solved question by question, the NSW ones have
not (about 3% sampled), so expect the NSW half to surface more.

### 8.2 The loop

1. Reviewer (`fouijnu@`) works the forms in Selectly and flags what looks wrong.
2. Admin (`qamar.adn@`) exports the flagged-questions CSV.
3. The CSV comes to qbank. `tools/ingest_review_flags.py` matches each flag to its stored
   question and writes a worklist. It applies **nothing** — a flag says "this looks
   wrong", which is not the same as knowing what is wrong. Across the blind-solve campaign
   that same signal resolved into a wrong key, a second correct answer, a figure
   contradicting its stem, and a perfectly sound question misread. Each is adjudicated:
   **repair / rekey / reject-and-replace / keep**.
4. Fixes land **in qbank**, never in Selectly. A question rejected at review is replaced
   by a newly authored one at the same archetype and position, so the form keeps its size.
5. `push_to_selectly.py --forms ...` re-sends **only what changed**, upserting in place,
   and switches off anything now rejected via `questions-fix`.

**Why fixes never go into Selectly directly.** §0 of this document is a description of
what happens when the two are corrected independently. Editing a flagged question in the
app would rebuild that divergence one question at a time, and the next reload would
silently revert it. Selectly is never edited; it is rebuilt from qbank's current state,
incrementally.

The one legitimate exception is `active`, which is a *serving* decision rather than a
content correction. It is owned by `questions-fix` and excluded from the import's update
set precisely so that a re-push cannot undo it.

### 8.3 What Selectly must add for this to work

**`qbank_id` in the flagged-questions CSV.** `/api/admin/flagged-questions/export`
currently emits `question_id` — Selectly's own uuid, which qbank has never seen and cannot
resolve. Join to `questions.qbank_id` and add the column. `tools/ingest_review_flags.py`
refuses a CSV without it rather than guessing, so the loop is blocked on this. It is a few
lines and it is the hinge of the whole workflow.

**`formId`, `formPosition`, `formKind` in the import.** Confirmed by reading the code on
2026-08-15: these appear **nowhere** in the Selectly repo — not in `validateQuestion`, not
in the import's values object, not in the schema. qbank has been sending them all along and
zod strips them silently. Without this the reload produces form-less questions and the
forms have to be dealt a second time. §6 step 2, still outstanding.

### 8.4 The obsolete flags now in the admin

The `question_flags` rows currently visible on the admin page — and their CSV export — are
from an earlier review round and **have already been actioned in qbank**. They refer to
questions by Selectly uuids that will not survive the reload, and to content that has since
been repaired. §1.1 wipes `question_flags` alongside `questions` for this reason. Do not
try to carry them forward or reconcile them; they are spent.

### 8.5 qbank-side changes already made (2026-08-15)

- `push_to_selectly.py` tracks a **hash of the payload sent** per question, not merely
  that it was sent. Under the old id-only tracking a repaired question was skipped
  *because* it had been pushed before, which would have made the loop above impossible.
  Old-format files load with a sentinel so the first run re-sends once, then settles.
- `--forms` scopes a run to named forms — for the pilot, and for every later round.
- A withdrawal pass switches off questions that are no longer sendable, addressed by
  `qbankId`, scoped by `--forms`.
- A guard refuses more than 200 withdrawals in one run. Bulk deactivation is the shape of
  a mistake — a forgotten `--forms`, or a stale tracking file after approvals were reset.
- `tools/approve_forms.py` and `tools/ingest_review_flags.py`, described above.

---

## 9. CLEARING RESOLVED FLAGS (added 2026-08-24)

### 9.1 The one endpoint still missing

**`POST /api/admin/flags-clear`**, authenticated with `x-import-secret` like
`questions-fix` and `questions-dump`.

```jsonc
// request
{ "qbankIds": ["ce671dbe-…", "eba092f4-…"] }
// response
{ "deleted": 14 }
```

Delete rows from `question_flags` whose `questionId` maps to a `questions` row with one
of those `qbank_id` values. Nothing else — no cascade, no touching `questions`.

qbank already calls it: `push_to_selectly.py --clear-flags <round>`, which runs after a
successful push and reads the ids from that round's worklist. Until the route exists the
push still succeeds and logs that flags were not cleared, so shipping this is not urgent
— but every round leaves its resolved flags in the admin list, and the next CSV repeats
them.

### 9.2 Why by id and not by exam

The obvious design — "clear all the VIC flags after a VIC push" — is wrong, and the
first two rounds show why.

**The CSVs are not region-pure.** The NSW round's export carried four NSW flags *and two
VIC ones*, because both reviewers export from the same admin list. Clearing "all VIC"
after that round would have deleted two flags nobody had adjudicated, and they would
have vanished without anyone knowing they existed.

**A flag can arrive mid-round.** Repairs take hours; a reviewer working in that window
raises a flag against a question nobody has looked at. A blanket clear removes it
silently, and the reviewer has no way to tell their report was lost.

Clearing exactly the ids that were adjudicated has neither problem, and needs no
knowledge of exams or forms on either side.

### 9.3 `keep` verdicts are cleared too

A flag whose verdict was `keep` — the question was read and found sound — is as resolved
as a repaired one, and its question is not re-pushed because nothing changed. Those ids
are in the round file and are cleared with the rest. Leaving them would have the same
question re-reported every round, and reviewers would stop trusting the list.

For the same reason `--clear-flags` runs even when the push has nothing to send: a round
can adjudicate a dozen questions and change none of them.

### 9.4 What it must not do

Clearing runs **after** a successful push and is skipped if the push reported errors. A
flag must never be cleared while the question it describes is still wrong in Selectly —
that turns a reported defect into an unreported one.
