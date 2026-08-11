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
the upsert, and `qbankId` addressing in `questions-fix`; qbank has
`pipeline/backfill_qbank_ids.py`. So §1 is a **merge, deploy, migrate and verify** job,
not a build job. Until it ships, everything below stays blocked.

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

### 4.2 Selectly — `form_attempts` (new table)

One row per student per form per round.

| Column | Purpose |
|---|---|
| `student_id`, `form_id`, `round` | identity of the attempt |
| `score`, `max_score`, `duration_seconds` | the result |
| `started_at`, `submitted_at`, `status` | lifecycle |

**Percentile is a query over this table, not a stored value.**

### 4.3 qbank — already applied, for reference

`form_id`, `form_position`, `form_kind` exist in `db/schema.sql` (migration
`db/migrations/001_form_columns.py`, applied). Forms are authored and reviewed in qbank and
pushed down, not assembled in the app.

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

1. **`qbank_id`** — merge `feature/qbank-id-addressability`, apply
   `supabase/migrations/0001_add_questions_qbank_id.sql`, deploy, then run
   `pipeline/backfill_qbank_ids.py --dry-run` and inspect the unmatched count before
   writing. Deactivate whatever stays null. Nothing else here can proceed first.
2. **Add `form_id`, `form_position`, `form_kind`** to the `questions` table **and to the
   import zod schema** — they are being sent already and silently dropped.
3. **`form_attempts` table and the two selector changes** — fixed forms and exact-pace
   timing.
4. **Wipe `questions` and `question_flags`** (§1.1).
5. **Reload.** `push_to_selectly.py --reset-tracking`, then push. This single step replaces
   the old steps 2, 3, 5 and 6: the 3,133 repairs, the 7 rejected-but-live rows, the 158
   banned verbal types and the form assignments all resolve because the bank is rebuilt
   from qbank's current state rather than patched toward it.
6. VIC content import, once reviewed.

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
