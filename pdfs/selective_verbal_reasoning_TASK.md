# TASK BRIEFING — Verbal Reasoning topics for VIC + NSW Selective

> **For a fresh Claude Code session.** Read this file completely before generating anything.
> Also read `/scratch/qbank/CLAUDE.md` for project-wide rules.
> **Run `/model opus` before starting.**

Researched 2026-08-02 from official ACER/NSW sources plus ~1,600 posts on the ATAR Notes
"Victoria sehs test 2026" thread, including first-hand accounts from students who sat the
**20 June 2026** VIC exam. Provenance and confidence for every claim is in §8.

---

## 1. WHY THIS FILE EXISTS

The 1,029-question VR bank was generated 25–30 May 2026 from `pipeline/prompts/vr_generate.txt`.

> Ignore `pdfs/verbal_reasoning.md` — it is a generic Indian competitive-exam aptitude syllabus
> (Blood Relation Test, Input-Output, Data Sufficiency, Clock and Calendar) added on 1 August 2026,
> **two months after** the bank was generated. It is not the source of anything and is not a target.

Two separate problems, both fixed by this file.

**(a) The generator drifted from its own spec.** `vr_generate.txt` asks for 60% Tier 1
(analogies, synonyms, antonyms, odd-one-out), 30% Tier 2, 20% Tier 3. Actual bank:

| | asked for | actual |
|---|---:|---:|
| Tier 1 | 60% | **33%** |
| Tier 2 | 30% | 28% |
| Tier 3 | 20% | 19% |
| off-spec entirely | 0% | **20%** |

Tier 1 came in at roughly half its quota, and a fifth of the bank is types the prompt never
asked for — dictionary/alphabetical ordering, hidden words, double meanings, spatial reasoning.
Within Tier 1 the collapse is lopsided: synonyms landed at 4% and antonyms at 2%, because the
model favoured odd-one-out and analogies (14% each).

**(b) Even on-spec, the target was wrong for VIC.** The real ACER paper is vocabulary-led —
every item students recalled was vocabulary — against **6% synonym+antonym** in our bank.
Meanwhile ~17% is alphabet/code/hidden-word/dictionary puzzles that no student reported seeing.

So: tighten the mix *and* move it toward the two exams we actually target. Nothing is deleted;
this file defines what to generate **in addition**.

---

## 2. THE TWO TARGETS ARE NOT THE SAME EXAM

Different authors, different skills. Do not write one set of questions for both.

| | **VIC SEHS** | **NSW SHSPT** |
|---|---|---|
| Author | ACER | **UCLES / Cambridge** |
| Entry | Year 9 (sat in Year 8) | Year 7 (sat in Year 6) |
| Where VR lives | **Reading + Verbal Reasoning**, one combined 55-min paper, 75 questions | Split: vocabulary sits in **Reading**; logic sits in **Thinking Skills** |
| Flavour | Vocabulary, word relationships, light syllogism | Critical thinking, argument analysis, logic puzzles |
| qbank subject | `verbal_reasoning` | Reading → `reading_comprehension`; Thinking Skills → `logical_reasoning` |

### Subject mapping — DECIDED, do not change

- VIC verbal → **`verbal_reasoning`**
- NSW Thinking Skills → **`logical_reasoning`** (currently 0 rows, reserved for exactly this)

Both slots already exist and are already wired to the right exam section in Selectly, so this
needs **no schema change**. Do not invent a new subject and do not merge the two.

**The difficulty gap between them is deliberate.** NSW is sat in Year 6, VIC in Year 8. Write
`logical_reasoning` for an 11–12-year-old and `verbal_reasoning` for a 13–14-year-old. They are
two calibrations, not one pool — a question is not interchangeable between them.

**VIC changed in 2023** (ACER replaced Edutest) and **restructured again for 2027 entry**:
five separate components collapsed into three. Reading and Verbal are now **interleaved in
one booklet**, not two blocks:

> "They combined the two subjects and **scattered them evenly across the paper**. Personally,
> I breezed through the verbal questions first before working my way through the Reading
> passages." — student, 2026-06-23

75 questions in 55 minutes = **44 seconds per question**. Keep items short. A VIC verbal item
should be answerable in ~25 seconds so the passage questions get the remaining time.

---

## 3. VIC — `verbal_reasoning` TOPICS (generate most heavily)

Target mix for new VIC-oriented questions:

| # | Topic | Share | Notes |
|---|---|---:|---|
| 3.1 | Vocabulary in context / synonyms | **30%** | The dominant real type |
| 3.2 | Antonyms / opposites | 10% | |
| 3.3 | Word-group classification | **20%** | The signature ACER item — see below |
| 3.4 | Sentence completion (single + double blank) | 15% | Context and collocation |
| 3.5 | Word relationships / analogies | 10% | Keep relationships crisp |
| 3.6 | Simple syllogism / conditional logic | 10% | Short, 2–3 premises |
| 3.7 | Shades of meaning / connotation | 5% | Rank intensity, positive vs negative |

### 3.3 Word-group classification — the signature item

Given a group of related words, pick the option that belongs with them. A student who sat the
real test described the mechanic:

> "for verbal, the correct answer is usually the one that doesn't 'fit in' w the other options
> (a pattern i see on all mocks and even the irl test)"

Their worked example:

> Miserly, Stingy, Parsimonious — which word joins them?
> A) **Frugal** B) Spendthrift C) Extravagant D) Squandering

The trap is deliberate: three distractors form their own coherent group (wasteful), so a
student pattern-matching on "which three go together" picks wrong. **Build distractors that
cohere with each other**, not random words.

### Vocabulary level — calibrate to these

Words actually recalled from the 20 June 2026 paper:

> **edict, discern, curb, pique, ovation** (→ commendation), **curtail** (→ restrict)

Mid-difficulty, everyday-academic. A capable Year 8 student meets these in reading, not in a
word list. **Do not** use exotica (perspicacious, obfuscate). Students found this section the
easiest on the day — comfort ratings 8.5–9.5/10, one rated difficulty **1.5/10**. Pitch
accordingly: our bank is currently harder than the exam.

---

## 4. NSW — `logical_reasoning` (Thinking Skills) TOPICS

**This subject is currently empty (0 rows) and is the single largest MCQ section of the NSW
exam — 40 of 105 questions.** It is the biggest gap in the bank.

Archetypes below are taken from the **official NSW/UCLES Practice Test 3 explained answers**,
so these are real, not inferred.

### 4A. Critical thinking / argument analysis (~45%)

| Topic | What it asks |
|---|---|
| **"Who reasons correctly?"** | Two named students each draw a conclusion; pick who is right (A only / B only / both / neither). **The most common single archetype — ~7 of 31 questions.** |
| Identify the assumption | What must be taken for granted for the argument to work |
| Weaken the argument | Which fact most undermines the conclusion |
| Strengthen the argument | Which fact most supports it |
| Identify the conclusion | Distinguish conclusion from supporting reasons |
| Correlation vs causation | Spot the leap from "linked" to "caused" |
| Necessary vs sufficient | e.g. must be ≥140 cm to qualify, but height alone doesn't guarantee selection |
| Conditional chains | If A then B; B requires C; what follows |

Worked shapes from the official paper:
- *Taller adults tend to have larger feet* → Monaro assumes it's always true, so his reasoning fails; Kevin's holds.
- *Reading at bedtime is linked to less sleep* → John assumes reading causes it; poor sleepers may simply read more.
- *Space exploration is a waste of money* → weakened if space work benefits people on Earth.

### 4B. Problem solving / logic puzzles (~55%)

| Topic | What it asks |
|---|---|
| Ordering / ranking | Order stations, houses, preferences from partial constraints |
| Syllogism (formal) | All parrots that eat apples eat carrots; no carrot-eater eats peas… |
| Numeric deduction | Deduce zone point-values from several players' totals |
| Set & counting logic | Overlaps between squares/circles/triangles; minimum counts |
| Letter/word overlap | Order CAN, AGE, COT, PAD by shared letters; letter-card puzzles |
| Symbol-sequence patterns | Predict the next symbol from a repeating string |
| Unit-chain conversion | 1 enit = 4 duits, 1 duit = 2 cotts … invented units |
| Spatial / 3D views | What the shape looks like viewed from above; orientation of a key |
| Measurement reasoning | Tiling a width with whole tiles plus a fraction |

Keep these **text-based**. Anything needing a rendered diagram must set `has_figure: true`
with valid SVG — see the figure rules in `qr_generate_png.txt`.

---

## 5. NSW — `reading_comprehension` addition: VOCABULARY CLOZE

New for 2026, now that the NSW test is fully computer-based: a passage with roughly **8 blanks**,
each filled from a dropdown. Tests vocabulary, grammar, collocation and contextual fit.

Model it as 8 linked MCQs sharing one `passage`, each stem naming its blank. Distractors should
be the right part of speech and plausible in isolation — wrong only in context.

---

## 6. DO NOT GENERATE THESE

No student reported any of these in either exam, and they are the Indian-syllabus artefacts
that made our bank feel wrong:

- Alphabet position tests ("which letter is 8th from the left…")
- Letter/number codes of the `MAP = 13116` kind
- Hidden words inside sentences
- Dictionary/alphabetical ordering
- Blood relations, clock-and-calendar, input-output, data sufficiency
- Anagram unscrambling

**Caveat, stated honestly:** absence of reports is weaker evidence than presence. Nobody
mentioning word codes doesn't strictly prove there were none. But 6% vocabulary against a
paper whose every recalled item was vocabulary is a large enough gap to act on.

Note the overlap: NSW Thinking Skills *does* include code-breaking and odd-one-out style logic.
If you want to keep that flavour, write it into `logical_reasoning` for NSW — **not** into
`verbal_reasoning` for VIC.

---

## 7. WRITING RULES (both states)

- Exactly 4 options, A–D, exactly one defensible answer.
- **No two options may be equivalent** — not `5(b−3)` and `5b−15`, not `12` and `√144`, not
  two synonyms of the same word in a synonym question. This has been a recurring defect.
- Vary the answer position; do not cluster on B/C.
- Australian spelling and context (recognise, colour, metres, AUD).
- Explanation: 1–2 sentences saying why the key is right **and** why the strongest distractor
  is wrong. Write it clean — never leak working, self-correction, or "wait, let me recheck".
- VIC items must be answerable in ~25 seconds. NSW Thinking Skills allows ~60 seconds.
- No calculator anywhere.

---

## 8. PROVENANCE & CONFIDENCE

| Claim | Confidence | Source |
|---|---|---|
| VIC = 3 components; Reading+Verbal 55 min | **High** | ACER official + 4 independent student accounts |
| VIC Reading+Verbal = 75 questions, interleaved | **High** | 4 corroborating first-hand accounts |
| VIC vocabulary list (edict, curb, discern, pique, ovation, curtail) | Medium | Student recall, single thread, hours after exam |
| Word-group classification is a signature item | Medium | One student who has sat the real test |
| VIC section is the easiest on the day | **High** | Consistent across many accounts |
| NSW Thinking Skills archetypes in §4 | **High** | Official NSW/UCLES explained-answers paper |
| NSW Reading vocabulary cloze (~8 blanks) | Medium | Secondary sources; verify against official |
| "Do not generate" list in §6 | Medium-low | Argument from absence — see caveat |

Sources: <https://selectiveentry.acer.org/vic/prepare> · <https://selectiveentry.acer.org/vic/exam-day> ·
<https://education.nsw.gov.au> (SHS practice tests, 2026 entry) ·
<https://discussion.atarnotes.com/d/9800-victoria-sehs-test-2026>

**Re-verify before a large run.** ACER varies forms between sittings, and the next VIC sitting
(2028 entry) is mid-2027. Download ACER's official `SEHS_Sample_Questions.zip` from the prepare
page — it is the only authoritative sample, though ACER warns it is "not necessarily reflective
of the difficulty of the exam".
