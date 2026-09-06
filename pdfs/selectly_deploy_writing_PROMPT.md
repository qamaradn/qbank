# SELECTLY TASK 3 — ship the writing work that is sitting on the laptop

Almost no code. The writing feature is built and correct; it has never left the machine.

## The diagnosis

    main         4943033  feat: accept VIC writing prompts — stimulus, word range, ...
    origin/main  81080ca  feat: name the set in the flagged-questions CSV

**Local `main` is one commit ahead of `origin/main`.** Task 2 was committed and never
pushed, so Vercel has never built it and
`supabase/migrations/0007_writing_prompt_fields.sql` — which ships inside that same
commit — has never run.

Confirmed from the outside: `/api/admin/questions-dump` returns the form fields, so
Task 1 is live, and returns none of `stimulus`, `stimulusType`, `wordCountMin`,
`timeLimitMinutes`. There are 0 writing rows in production.

Nothing is broken. It just has not shipped.

## Do this, in this order

**1. Run the migration against production first.** It is already written:

    supabase/migrations/0007_writing_prompt_fields.sql

    ALTER TABLE questions ADD COLUMN IF NOT EXISTS stimulus text;
    ALTER TABLE questions ADD COLUMN IF NOT EXISTS stimulus_type varchar(20);
    ALTER TABLE questions ADD COLUMN IF NOT EXISTS word_count_min integer;
    ALTER TABLE questions ADD COLUMN IF NOT EXISTS time_limit_minutes integer;
    ALTER TABLE writing_feedback ADD COLUMN IF NOT EXISTS dimension_labels jsonb;

Additive and idempotent, so it is safe to run before the deploy — and it has to be, or
the newly deployed code queries columns that do not exist yet for the minute in between.

**2. Push.** `git push origin main` sends `4943033`; Vercel builds it.

**3. Merge `feature/dump-writing-fields` and push that too.**

Commit `4914208`, branched off `main`, written on the qbank side and ready. It adds
`promptType`, `stimulus`, `stimulusType`, `wordLimit`, `wordCountMin` and
`timeLimitMinutes` to the `questions-dump` select. Type-checks clean, no behaviour change
for existing callers.

**Why it matters, and it is not a nicety.** Task 2 does not touch the dump. Without this,
qbank can push the prompts but cannot prove the stimulus arrived — and a prompt whose
stimulus was dropped imports with `errors=0` and reads as broken to the first candidate:
eleven of the 54 VIC prompts are quote prompts whose task says *"argue for or against the
view expressed in the quote below."* That is the third time this argument has applied to
this endpoint, after `qbankId` and `formId`.

**4. Tell qbank.** One command sends the 54 VIC prompts across 27 forms.

## What qbank has waiting

- all 106 writing prompts approved; 54 VIC dealt into 27 forms of two
- `pipeline/push_writing_to_selectly.py`, built against the contract you verified, with
  7 tests over real `writing_prompts` rows
- a preflight that **refuses to push** while the dump lacks those four fields, so this
  cannot be shipped half-done by accident. `--force` exists if you deploy some other way.
- `--verify`, which reads the prompts back and reports per prompt what actually landed

## How to know it worked

1. `/api/admin/questions-dump?category=writing` returns 54 rows, each with a non-empty
   `stimulus`, a `formId` and a `formPosition` of 1 or 2.
2. Open `vic-drill-wr-016` as a student: position 1 is persuasive at 130–170 words in
   15 minutes, position 2 is narrative at 220–290 in 25, one 40-minute clock, the
   stimulus visibly separate from the task.
3. Submit both and check `writing_feedback` carries `dimension_labels` — the narrative
   marked on Character & Plot, not on Argument.

## Not in scope

NSW writing. Its section is already correct at 1 task / 30 min, its 42 prompts have no
forms dealt on purpose, and qbank will not send them. Nothing to do.
