# HANDOVER — selective VR/LR task, state as at 2026-08-04

> Read this **with** `pdfs/selective_verbal_reasoning_TASK.md`. That file is the spec and
> is still accurate; it simply has no record of what has since been built. This file is
> the state. Read `CLAUDE.md` first for project-wide rules.

---

## 1. WHAT IS DONE

### §4 NSW Thinking Skills → `logical_reasoning` — **COMPLETE, 300/300**

Was 0 rows. Now 300, every category at target, all `review_status='pending'` except one
the reviewer rejected on 2026-08-03.

| category | n | | category | n |
|---|---:|---|---|---:|
| who_reasons_correctly | 30 | | ordering_ranking | 20 |
| identify_assumption | 18 | | syllogism_formal | 20 |
| weaken_argument | 18 | | numeric_deduction | 20 |
| strengthen_argument | 15 | | set_counting_logic | 18 |
| identify_conclusion | 15 | | letter_word_overlap | 18 |
| correlation_vs_causation | 15 | | symbol_sequence_patterns | 18 |
| necessary_vs_sufficient | 12 | | unit_chain_conversion | 17 |
| conditional_chains | 12 | | spatial_3d_views | 17 (figures) |
| | | | measurement_reasoning | 17 (figures) |

- 34 questions carry inline `figure_svg`; 197 medium / 103 hard; key spread 75/75/75/75.
- `confidence` is a genuine per-question value (15 distinct, 0.84–0.98), each with a
  written reason in `lr_confidence.py`. It is NOT the old hardcoded 0.95.
- Source book id: `lr_thinking_skills`. Batches are `source_page` 1–13.

### Content originality

All scenarios are invented. `lr_finalise.py` mechanically rejects any batch containing
fragments from the TASK file's quoted student/official examples (Monaro, Kevin, "taller
adults / larger feet", "reading at bedtime", "space exploration is a waste", the
miserly/stingy/parsimonious set). No PDF in the repo was used as source material.

---

## 2. WHERE THE WORK LIVES

**Resolved 2026-08-04.** The general-purpose tooling is now committed:

| now in git | what it is |
|---|---|
| `tools/question_checks.py` | subject-agnostic batch checks + 25 tests |
| `tools/figure_lib.py` | figure builders + 15 tests |
| `tools/lr_finalise.py` | the LR batch orchestrator, rewired to the two above |

Two defects were found in the checks while extracting them, both now fixed and covered
by regression tests:

- `_is_prose_category` gated on raw word count (>2 words), which classified `"Leo only"`
  as a *value* answer and skipped the group — so the original 15-of-15 `"<student> only"`
  defect the check exists to catch **would have passed it**. It only passed on today's
  data because that defect had already been hand-repaired into 4-word forms. Now gates on
  whether the key is a computed value (contains a digit / has no letters).
- The check was run per batch, where ~4 questions per category is far too small a sample.
  Batch p1 flagged 3-of-4 `"<N> only"` against a bank-wide rate of **47%** — which is the
  *correct* rate for an archetype where "A only" and "B only" share one shape. It now
  runs over the accumulated bank, and `min_group` is 10.

Run over all 6,685 questions the checks are clean on shape-monotony, but flag real
pre-existing defects elsewhere, none yet fixed: **274 explanations naming option
positions** (101 QR, 63 VR, 52 SR, 45 MA, 13 RC), **505 figure-rule violations** (451 QR,
54 MA), **16 QR questions with non-distinct options**, and 23 topic groups where the key
is the longest option more than 60% of the time.

The remaining ~23 files under `run_data/output/logical_reasoning/generated/` are one-off
batch builders and repair scripts, still gitignored: `lr_pNN_build.py`, `lr_confidence.py`,
`lr_revise*.py`, `lr_load_one.py`, `lr_resync_json.py`.

What the two committed modules enforce:

- **`tools/question_checks.py`** — beyond format checks:
  - `answer_shape_monotony` — fails a group whose correct answers share a shape (blanks
    proper nouns, compares 3-grams). Skips value-answer groups and all-placeholder
    signatures. Feed it the whole bank, not one batch.
  - `length_tell` — fails a group where the key is the longest option >60% of the time.
  - `positional_reference` — rejects explanations naming option positions ("the first
    three pairs"), which go false once options shuffle.
  - `figure_svg_errors` — viewBox, `currentColor`, size, no hard-coded colours.
  - `options_distinct` — textual duplicates only; it cannot see that `5(b−3)` and `5b−15`
    are the same value.
  - Grouping is caller-supplied (`group_of`), defaulting to `topic`; LR passes its
    `"Category: <key>"` reader.
- **`tools/lr_finalise.py`** also screens near-duplicate stems at 0.82 (stricter than
  phase 4's 0.85, which drops silently) — that part stays LR-specific because it queries
  the DB by subject.
- **`tools/figure_lib.py`** — figure library:
  - `ortho()` — orthogonal shape from ONE list of moves; path and side labels are both
    generated from it, so a label cannot disagree with the line it names. Ray-cast
    inside/outside test for label placement, plus glyph-extent collision resolution.
  - `fold()` / `opposite_of()` — folds a cube net and computes opposite faces. Refuses
    nets that do not fold to a cube.
  - `iso_stack_fitted()` / `check_stack()` — visible-face culling, auto-fit to viewBox,
    and rejection of layouts where a near column would paint over a far one.

Both generalise to any subject. `figure_lib` would have caught the year7 maths figure
defects.

Run one batch: `env -u PYTHONPATH .venv/bin/python3.11 -m tools.lr_finalise <NN>`.

---

## 3. WHAT REMAINS

### 3a. §3 VIC `verbal_reasoning` — **183 new questions**, and an exclusion problem

The bank is 1029. Measured against the §3 target mix:

| §3 bucket | have | need (600 pool) | **generate** |
|---|---:|---:|---:|
| 3.1 vocabulary / synonyms | 54 | 180 | **126** |
| 3.2 antonyms | 35 | 60 | **25** |
| 3.7 shades of meaning | 8 | 30 | **22** |
| 3.3 word-group classification | 110 | 120 | **10** |
| 3.4 sentence completion | 122 | 90 | 0 (surplus) |
| 3.5 analogies | 154 | 60 | 0 (surplus) |
| 3.6 syllogism | 139 | 60 | 0 (surplus) |

173 of the 183 are vocabulary-family, which matches the brief: every item students
recalled from the 20 June paper was vocabulary, against 8% in our bank.

Other pool sizes: 300 → 43 new · 400 → 83 · 500 → 128 · **600 → 183** · 800 → 313 ·
1000 → 471. (600 ≈ 15 full sittings at ~38 verbal items per paper.)

**Adding alone cannot fix the calibration** — but settle the count first. A stem+topic
classifier over the 1029 finds **166 strict §6 violations**, 164 of them `approved` and
already pushed:

| §6 type | n |
|---|---:|
| dictionary / alphabetical ordering | 61 |
| word codes | 54 |
| hidden words | 32 |
| anagram / making words | 10 |
| alphabet position | 9 |

The **407 / 40%** figure quoted in earlier drafts of this file does not reproduce; it
appears to count a broader "off-spec" set (spatial reasoning, double meanings,
odd-one-out variants, letter/number sequences) that is a judgement call rather than a §6
breach. Note also that TASK §8 rates the §6 list itself **"Medium-low — argument from
absence"**, which is thin evidence for pulling 400 approved questions. Start with the 166.

**The mechanism is `active=false`, not `schoolIds`, and not a new qbank column.** Selectly
already has it: `questions.active` is honoured by both the exam selector
(`src/lib/exam/select-questions.ts`) and the drill selector
(`src/lib/drill/select-drill-questions.ts`). `schoolIds` is the wrong lever twice over —
`verbal_reasoning` is a `vic-seal`-only category so there is no other exam to route these
to, and the drill selector ignores `schoolIds` entirely. On the qbank side mark them
`review_status='rejected'`, which already means "never serve"; no schema change needed.

**Blocked on the identity gap — do this first.** See §3e.

**Calibrate difficulty down.** The brief records comfort ratings of 8.5–9.5/10 and one
difficulty rating of 1.5/10, and warns our bank is harder than the exam. Target
vocabulary at the level of *edict, discern, curb, pique, ovation, curtail* — not
*perspicacious* or *obfuscate*. The 622 on-target existing questions are counted above as
reusable but have NOT been checked for pitch.

### 3b. §5 NSW `reading_comprehension` vocabulary cloze — not started

~8 blanks per passage sharing one `passage`, each stem naming its blank. 15 passages =
120 questions. Distractors must be the right part of speech and wrong only in context.

### 3c. Human review

299 LR questions pending. Nothing reaches students until approved. Start with the
lowest-confidence items — `lr_confidence.py` explains why each is flagged. The op-shop
assumption item (`2d92d087`, 0.85) had an outright wrong key until it was repaired, and
deserves a fresh read rather than a glance.

### 3d. Delivery gap — RESOLVED, was already done

Verified 2026-08-04: `mathematics` **is** in `QBANK_CATEGORIES` in
`src/lib/config/schools.ts` and is mapped to nsw-shspt's "Mathematical Reasoning"
section. `logical_reasoning` is likewise mapped to NSW Thinking Skills. Nothing to do.
`push_to_selectly.py` only ever pushes `approved` rows.

### 3e. Pushed questions are unreachable — THE BLOCKER

`/api/questions/import` is insert-only and lets Postgres mint its own uuid
(`id: uuid().primaryKey().defaultRandom()`), so qbank never learns the id of the row it
created. `run_data/db/pushed_to_selectly.json` records only *that* a qbank id was pushed.
**All 5321 approved questions are therefore live and unaddressable** — they cannot be
deactivated, corrected, or withdrawn.

This blocks the VR exclusion above, and every repair the human review of the 299 pending
LR questions will produce.

Selectly has the endpoint already — `/api/admin/questions-fix` can set `stem`, `options`,
`correctAnswer`, `explanation`, `imageUrl` and `active` — but it addresses rows by
Selectly's uuid.

Fix, in order:
1. Pass the qbank uuid as the row id on import. qbank ids are already uuid-v4, so this is
   a few lines in `validate.ts`, `import/route.ts` and `row_to_question()`. After it, the
   two databases share one key permanently.
2. Backfill the 5321 existing rows by matching stems via `/api/admin/questions-dump`
   (returns id + stem per category). Note `build_stem()` prefixes passage subjects with
   `"PASSAGE:\n...\n\nQUESTION:\n"`, so match on the transformed stem. This is the last
   time a fragile stem-join is ever needed.
3. Then `active=false` becomes a normal operation.

Also worth fixing while in there: `push_to_selectly.py` hard-codes
`SCHOOL_IDS = ["vic-seal", "nsw-shspt"]` on *every* question, so `schoolIds` currently
carries no information — maths is tagged for vic-seal, which has no maths section, and QR
for nsw-shspt, which has no QR section. Harmless today only because the exam selector also
filters on category.

---

## 4. METHOD THAT WORKED — REUSE IT

**Derive the answer in the build script; never assert one you merely believe.** Each
builder computes its answers (permutation search, exact `Fraction` solving,
inclusion-exclusion, set algebra, net folding, shoelace area) and fails if the computed
answer does not match exactly one option. This rejected, before a word was written: two
puzzles with multiple solutions, one unsatisfiable, one with non-integer answers, one
underdetermined, a "shares no letters" item where every option shared one, a "letter in
all three words" item whose words shared four, and a pair called anagrams that were not
the same length.

**Then render figures and LOOK at them** — `python -m tools.figure_contact_sheet --json
<batch>.json`. Code passed a thermometer drawn on the 20 mark against a key of 25 °C,
cube stacks that rendered as an uncountable flat tessellation, a column clipped off the
canvas, and two figures that gave away their own answers.

**Declare the answer's mechanism and refuse repeats.** `lr_p11_build.py` keeps a `USED`
set of every mechanism already in the bank. Without it these categories collapse into one
template — which is exactly what the first six batches did.

### Defects found and closed this session (do not reintroduce)

| defect | was | now |
|---|---|---|
| "2nd student only" in who_reasons | 15/15 | 14 one-only / 8 both / 8 neither |
| one answer mechanism per category | 1 per category | 70+ distinct, registry-enforced |
| key was the longest option | 32/32 | 22% (chance 25%) |
| explanations naming option positions | 3, then 17 | 0 |
| a wrong key | 1 | fixed |

---

## 5. ENVIRONMENT

- `env -u PYTHONPATH .venv/bin/python3.11` — **required**; `PYTHONPATH` shadows the
  venv's pydantic and breaks pytest/uvicorn/anthropic imports.
- No `sqlite3` CLI. Query via Python's `sqlite3` module.
- DB: `run_data/db/qbank.db`. Review UI:
  `DB_PATH=run_data/db/qbank.db uvicorn review.server:app --host 0.0.0.0 --port 8000`
- Rebuild + validate + load one batch:
  ```
  .venv/bin/python3.11 run_data/output/logical_reasoning/generated/lr_pNN_build.py
  .venv/bin/python3.11 run_data/output/logical_reasoning/generated/lr_finalise.py NN
  DB_PATH=run_data/db/qbank.db .venv/bin/python3.11 \
      run_data/output/logical_reasoning/generated/lr_load_one.py NN
  ```
- DB totals 2026-08-04: 6685 questions — MA 1075, QR 2240, SR 1322, VR 1029, RC 719,
  LR 300. 5321 approved, 1340 pending, 24 rejected.
