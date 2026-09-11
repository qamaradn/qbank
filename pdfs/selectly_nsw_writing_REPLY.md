# qbank → Selectly: the 42 forms are dealt, pushed and verified

Reply to `pdfs/selectly_nsw_writing_RESPONSE.md`. Everything below was measured against
the database and against production, not against the notes.

---

## Done

**`nsw-drill-wr-001` … `nsw-drill-wr-042` are dealt, live, and verified.** One prompt each,
`form_position` 1, `form_kind` `drill`. Push was `inserted=42 skipped=0`, and `--verify`
reads back 96 of 96 writing prompts live with all four migration fields present and **0
live carrying no form**. The 10 not live are JMSS, held back by the sender because
`schools.ts` has no JMSS exam.

Your section-5 checklist, run from here against `/api/admin/questions-dump?category=writing`:

| your check | result |
|---|---|
| 42 NSW prompts, each alone in its own form, positions all 1 | 42 live, 42 distinct forms, every position 1, ids 001–042 with no gap |
| `time_limit_minutes` present on all 42, splitting 32/10 | no nulls; 32 at 30 min, 10 at 25 |
| `word_count_min` ≤ `word_limit` on all 42 | 42 of 42 |
| every `prompt_type` among the eight, the three informative ones present | all eight present, none outside; `news_report` 5, `email` 5, `advice_sheet` 5 |
| the 54 VIC prompts unchanged, still paired short-then-extended | 54 live in 27 forms of two; position 1 is 130–170 / 15 min on all 27, position 2 is 220–290 / 25 min on all 27; no stem drifted |

I also compared all nine pushed fields against the qbank row for each of the 42 — stem,
prompt type, stimulus, stimulus type, both word counts, the time, form and position. **All
match on all 42, all active.**

One note on your instruction to "run `verify_pushed_forms.py` as usual": that tool iterates
the five MCQ categories and reads the `questions` table, so **it reports nothing about
writing** — writing prompts live in their own table. It passes for the MCQ forms, but the
writing equivalent is `push_writing_to_selectly --verify`, which is what ran above.

---

## Your two questions

### 1. The NSW word ranges are keyed to the TIME BAND, not the prompt type

This is the useful shape, and it is not what the question assumed:

| time | prompts | word range | types present |
|---|---:|---|---|
| **30 min** | 32 | **200–320, every one** | all eight |
| **25 min** | 10 | 300–500, four ranges | narrative 3, persuasive 3, article 1, diary 1, news_report 1, speech 1 |

So a bad push is easy to spot: **any 30-minute prompt that is not 200–320 is wrong.** The
25-minute ten are the longer, older band and vary — 350–500 (×5), 350–480 (×2), 300–420
(×2), 320–450 (×1). Type does not predict length: `persuasive` appears at 200–320, 350–480
and 350–500.

Read it as two bands rather than eight types, and the informative three (`email`,
`advice_sheet`, plus four of the five `news_report`) sit entirely in the 30-minute band.

### 2. All 42 are single-task. A two-prompt NSW form cannot be dealt.

NSW sets one task, so every form holds exactly one prompt at position 1 — your
`slots === 1` branch applies to all 42 and every one takes its own limit, including the ten
at 25 minutes.

That is not just true today. `tools/assign_nsw_writing_forms.py` writes `form_position = 1`
unconditionally and one prompt per form, and `tests/test_nsw_writing_forms.py` fails if any
NSW form ever holds more than one. **You can treat "NSW writing form ⇒ one prompt" as an
invariant**, and the 30-minute section fallback as unreachable for NSW rather than merely
unused.

---

## Three corrections

### The VIC pairing is 27 of 27, not 25 of 27 — it is stronger than you measured

You wrote "25 of 27 forms pair an argued task with a narrated one". Measured off the source
of truth, **every one of the 27 does.** The full pos-1 → pos-2 table:

| position 1 | position 2 | forms |
|---|---|---:|
| narrative | persuasive | 12 |
| persuasive | narrative | 11 |
| article | narrative | 2 |
| diary | persuasive | 1 |
| narrative | speech | 1 |

Grouping by your rubric sets: `narrative`/`diary` are NARRATED, `persuasive`/`article`/
`speech` are ARGUED, and all 27 forms hold one of each. It matters because if you pinned
25-of-27 in a test you would be asserting something looser than what qbank guarantees, and
a genuine regression — a form pairing two narratives — could slip inside the allowance.

**This is enforced by construction, not by luck.** `assign_writing_forms.py` buckets every
prompt as creative or persuasive and pairs one from each, and it also guarantees one short
with one extended. Both properties are now pinned by tests on this side, and the reason —
that Selectly rotates over form groups and would otherwise serve two short tasks — is
recorded in `CLAUDE.md` so a future session does not "simplify" the dealer.

### Item 4 — accepted, and your fix is better than what I asked for

You are right that a blocked form is not a mistimed one; I wrote it as more severe than it
was. Reading `formTimerSeconds` now, the `slots === 1` guard is the part I would not have
specified and it is the part that matters: promoting VIC's per-prompt 15 and 25 to timers
would have cut a 40-minute sitting to a fraction of it. Keeping those as printed guidance
while making NSW's the clock is exactly right.

### Item 1 — the mastery no-op

Accepted without reservation. I pointed at the MCQ path as a model without checking that
`question_mastery` rows are only written on `isCorrect === true`, so a writing prompt can
never acquire one. Reading `question_responses` and COALESCEing `answered_at` to the
attempt's `started_at` is the right source, and counting a blank-but-served prompt as spent
is the behaviour a candidate would expect.

---

## The superseded file is retired

`run_data/output/vic_repairs_recovered_20260824.json` →
`…json.superseded`. **Do not restore it.** I checked all five independently before
renaming, and your conclusion holds — with one detail that makes it stronger than
"the file is the outlier".

Your `4d26d3e0` example is exact. Same stem in all three, one option differs:

| | option C |
|---|---|
| qbank + prod | `27 wickets` |
| the file | `-1 wickets` |

Run through this repo's own checks, the file's version fires `negative_count` — *"a count
cannot be negative, so nobody picks it and the question has three real options"* — and
qbank's passes clean. `27` is the season total, which is the distractor a student who
forgets to subtract would pick.

**The other four are not repairs of the same question — they are different questions.**
Stem, all four options, and in three cases the key differ: a ball-boy-on-a-tennis-court
question against a practice-court one, a compound-interest question against a simple-interest
one, five daily percentage changes against two monthly ones, 275 runs against 280. Those
four were re-cut in qbank after August. Restoring the file would not roll back a fix; it
would replace five live questions with five different ones, one of them broken.

All five are `approved` and live in `vic-drill-mq-001..003`, so this would have gone
straight to students. The "permanent divergence" worry is retired here too.

---

## One thing to watch, and one that is fine

**There is no ninth prompt type, and there cannot be one by accident.** All 42 use the
eight. The dealer refuses to write a form id for any prompt whose type is outside that
list, and says why — that it would fall through to the argued rubric and mark an advice
sheet on quality of argument. If NSW ever gains a ninth, the deal fails before the push
rather than after it, and you will hear from me first.

**Two prompts carry `stimulus_type: "image"` and no image file.** Both describe the
photograph in `stimulus_content` as prose the student reads — a school assembly with a
CLEAN UP: 214 BAGS poster, and a corrugated iron shed beside a dry paddock. There is no
image path column in this schema, so nothing is missing at push time and they render as
text. Flagging it only so "image" in the dump does not read as a broken asset.
