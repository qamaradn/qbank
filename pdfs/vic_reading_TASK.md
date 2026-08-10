# TASK BRIEFING — VIC Reading

> Written 2026-08-10. Sits under `vic_content_taxonomy_TASK.md` §4, which sized this
> component. Read that first. This document is the build spec for the 394 items §4 says
> are needed, and it exists because two measurements taken on 2026-08-10 changed what
> that number means.
>
> Every claim carries a confidence rating.

---

## 1. THE TWO MEASUREMENTS THAT SHAPED THIS

**a. The 718 ACT reading questions are retrieval-led.** 40 were read by hand in two
independent random samples: **27 retrieval, 13 inference — 67.5% retrieval** (95% CI
53–82%). A mechanical proxy — content-word overlap between the key and the passage —
separates the two hand-labelled classes cleanly (mean 0.53 against 0.19), agrees with the
hand labels 82% of the time, and errs toward calling things inference. Applied to all
718 it puts the retrieval floor at **59.5%**, consistent across all ten source books
(55–71%). **Confidence: High** — this is a direct reading, not a proxy.

The bank disguises it. 232 stems promise inference ("implies", "suggests", "can be
inferred") and **37% of those are answered by a near-verbatim restatement** of one
passage sentence. Several explanations admit it, saying the passage "explicitly states"
the answer. §4.1 of the taxonomy wants retrieval at 20%. We are at ~67%.

**b. The passages are one text type.** 144 distinct passages, and **~93% are
informational/expository**. Genuine narratives number 6–10; poetry is **zero**; 36 of
144 are about the Great Barrier Reef. **Confidence: High** — heuristic calibrated by
reading both the hits and the misses.

**What follows from (a) and (b) together.** Writing new questions against the existing
passages is the cheap route, and it works — but it can only ever produce *informational*
items, and informational is the one type already oversupplied. So the cheap route covers
**83 of the 394**. The rest needs new passages.

**What is NOT wrong with them.** The passages themselves are good and are kept: 160 words
median (which suits the 44 s/question pace), Australian context, right reading level —
that was checked properly in taxonomy §4.2 after a Flesch-Kincaid score wrongly condemned
them. Nothing here is an argument for discarding the 718.

---

## 2. TARGETS

Text-type split agreed 2026-08-10. ACER publishes none, so this is a judgement:
informational-weighted because ACER's own wording stresses *information* and *ideas
communicated in texts*, with poetry at 10% borrowed from the NSW build, the closest
analogue we hold. **Confidence: Low-Medium.** Revisit if a first-hand account surfaces.

| Text type | Share | Target | Held | Held inference-led | **Author** |
|---|---:|---:|---:|---:|---:|
| Informational / expository | 50% | 372 | ~670 | ~215 | **83** |
| Narrative / literary | 25% | 186 | ~30 | ~25 | **156** |
| Persuasive | 15% | 111 | ~30 | ~25 | **81** |
| Poetry | 10% | 74 | 0 | 0 | **74** |
| | | **743** | | | **394** |

Within every text type the skill mix is taxonomy §4.1: **inference 35%, author's purpose
and tone 25%, integrate and evaluate 20%, access and retrieve 20%.**

Informational needs only 83 new because its 372 slots are filled by 298 inference-led
items (215 held + 83 new) and 74 retrieval items drawn from the 455 already held. The
remaining ~380 informational retrieval questions are **not wasted and not deleted** —
they go to the drill pool, which does not have to mirror the paper. Only mock forms do.

New passages required: roughly **28 narrative, 15 persuasive, 12 poetry — 55 in all**, at
5–6 items each (poetry 5–8).

---

## 3. THE RULE THIS COMPONENT EXISTS TO ENFORCE

**An inference item whose key restates a passage sentence is a retrieval item wearing an
inference stem.** That is the single defect being repaired, it is what 37% of the existing
"implies" questions do, and it is easy to reproduce by accident.

So every authored non-retrieval item must satisfy:

> **The key must not be a restatement of any single sentence in the passage.**
> Mechanically: content-word overlap between the key and the passage **< 0.35**, where
> content words are lowercase alphabetic tokens of 4+ characters minus a stoplist.

That threshold is not invented. It is the decision boundary fitted to the 40 hand-labelled
questions, where it separated retrieval from inference with 82% accuracy and 95% precision
on the retrieval side. `tools/question_checks.key_restates_passage` implements it.

Three ways to satisfy it honestly:

1. **Synthesis** — the answer combines two or more separated statements and appears as
   such in neither. *"conservation efforts are essential but have not yet reversed the
   decline"* from "efforts are underway", "brink of extinction" and "success is crucial".
2. **Function** — what a sentence, example or structural choice is *doing*, not what it
   says. *"The author uses the Dhimurru IPA as an example of…"*
3. **Stance and implicature** — what the writer's word choice commits them to. *"perceived
   emptiness"* signalling that the emptiness is a belief the author does not share.

And the reverse trap: **do not write a retrieval item with an inference stem.** If the
answer is stated, say "According to the passage". The 20% retrieval share is real — ACER
names *access and retrieve* first — so retrieval items are wanted, just labelled honestly.

### Do not reintroduce the length tell

The existing reading key averages 62.1 characters against 54.9 for distractors, so "pick
the longest option" scores **48.7%** — a live defect that reordering could not fix
(`tools/repair_key_skew.py` docstring). `tools/question_checks.length_tell` already
screens it; every batch must pass. **This applies to the repair pass on the old questions
too, which is a separate editing job and is not in this document's 394.**

---

## 4. BUILD METHOD

Same harness as the NSW reading build — `tools/rc_finalise.py` with a per-type entry in
`TYPES`, builders under `tools/rc/`, loaded by `tools/load_batch.py`. What that harness
already guarantees and must keep guaranteeing:

- **One passage string per group, byte-identical across its rows.** Selectly derives
  `passageId` by hashing the passage; a single drifted character splits the group and the
  student is shown the passage twice.
- **Quoted text is cut from the passage by the builder, never retyped.**
- **Stems within a group are textually distinct** — phase 4 drops near-duplicate stems at
  0.85 *silently*, so the finalisers screen lower.
- Distractor-relation design, answer-shape monotony, positional references, real-word
  screening: `tools/question_checks.py`.

### The informational top-up is a different shape from the rest

Its 83 items attach to passages that **already exist in the database**. The builder reads
the passage text out of the DB and emits new rows carrying it **byte-identical**, so the
new questions join the existing group rather than forming a second one. This is the only
RC builder that does not author its own passage, and the byte-identity requirement is
load-bearing: get it wrong and every affected passage is served twice.

New rows take their own `source_book` (`rc_vic_inference`) so review and rollback can
isolate them, while sharing the passage with `act_test*` rows.

### Two-pass QA is mandatory

Run the checks **and read every question** — that is standing instruction on this project
and it has repeatedly caught what code cannot. During the key-skew repair the automated
invariant check passed 2,742 of 2,742 while three corrupted explanations were still live;
reading the diffs found them.

---

## 5. ORDER OF WORK

| # | Batch | Items | New passages | Why here |
|---|---|---:|---:|---|
| 1 | Informational inference top-up | 83 | 0 | Cheapest, no passage authoring, proves the `key_restates_passage` rule against real text |
| 2 | Poetry | 74 | 12 | Nothing held at all, and the NSW `rc_poetry_*` builders and `poetry_common.py` port directly |
| 3 | Narrative / literary | 156 | 28 | Largest block; needs the most new prose |
| 4 | Persuasive | 81 | 15 | Smallest new-passage block |

Pitch every new passage at **Year 8** — the exam is sat in Year 8 for Year 9 entry. The
NSW reading set is Year 6 and deliberately below this (taxonomy §3.4); do not port its
passages, only its builders.

---

## 6. WHAT IS NOT IN THE 394

- **The length-tell repair** on the existing 718 — padding short distractors so the key
  stops being the longest. Editing, not authoring, and a person has to do it.
- **The 45 questions blocked by `repair_key_skew.py`** as defective rather than
  misordered — duplicate options, admitted-equal options, leaked authoring intent. Listed
  in `run_data/output/key_skew_manifest.json`, needs a human ruling.
- **`science_reasoning`** — parked for JMSS, out of scope for VIC entirely.
