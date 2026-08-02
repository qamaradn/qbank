# TASK BRIEFING — Year 7 NSW Selective Maths Question Generation

> **For a fresh Claude Code session.** Read this file completely before generating anything.
> Also read `/scratch/qbank/CLAUDE.md` for project-wide rules.
> **Run `/model opus` before starting** — arithmetic correctness is the whole point of this job.

---

## 1. OBJECTIVE

Generate **532 MCQ questions** covering the full Year 7 maths curriculum for the
**NSW Selective High School Placement Test (Year 7 entry)**.

- Source curriculum: `/scratch/qbank/pdfs/year7_maths_curriculum.md`
- 27 categories (A–AA), **273 numbered subtopics, 266 unique**
- **2 questions per unique subtopic** = 532 questions
- **Exactly 50** of those carry an SVG figure (list in §6). Everything else is text-only.

This is a **validation pass at breadth**, not production depth. The goal is full
curriculum coverage with verifiable quality, so the prompt can then be locked in
for a larger Batch API run.

---

## 2. WHY `quantitative_reasoning` — DO NOT CREATE A NEW SUBJECT

The NSW Selective test (Year 7 entry, 2021 format) has four sections:

| NSW section | Questions | qbank subject |
|---|---:|---|
| Reading | 30 | `reading_comprehension` |
| **Mathematical Reasoning** | 35 | **`quantitative_reasoning`** ← this task |
| Thinking Skills | 40 | `logical_reasoning` |
| Writing | 1 task | `writing` |

Year 7 maths maps onto `quantitative_reasoning`. **Zero schema change required.**

- **Do NOT** add a `mathematics` subject. The 6 subjects in `CLAUDE.md` are locked.
- **Do NOT** repurpose `logical_reasoning` — it is the slot for Thinking Skills,
  the single largest MCQ section of the exam (40 of 105). It is currently empty
  (0 rows) but reserved.

### Distinguishing these from the existing bank

The DB already holds **2,240 `quantitative_reasoning` questions** that are
ACT-style at year 9–12 — a different difficulty band. Keep the new rows
identifiable using **two fields that already exist**:

```
source_book = "year7_nsw_maths"
topic       = "Year 7: <Category Name>"     e.g. "Year 7: Number Theory"
```

`GET /stats/topics` groups by `topic`, so the `Year 7:` prefix makes them visible
as a distinct block in the review UI with no code change.

> A dedicated `target_year` column on `questions` would be cleaner long-term, but
> it needs schema + loader + UI changes. **Defer it.** Use the two fields above
> for this pass.

---

## 3. KEY PATHS AND FACTS

```
Repo root      /scratch/qbank
Python         .venv/bin/python3.11        ← never bare python/python3
DB             run_data/db/qbank.db
OUTPUT_DIR     run_data/output
Generated JSON run_data/output/quantitative_reasoning/generated/
Review server  uvicorn review.server:app --host 0.0.0.0 --port 8000
```

### ⚠️ Two environment gotchas (both confirmed during the pilot)

**1. `PYTHONPATH` shadows the venv.** The shell has `PYTHONPATH=/scratch/python-packages`,
which precedes `.venv/lib/python3.11/site-packages` in `sys.path` and shadows the
venv's working `pydantic` with a broken copy (`ModuleNotFoundError:
pydantic_core._pydantic_core`). **The review server will not start** unless you clear it:

```bash
env -u PYTHONPATH nohup .venv/bin/uvicorn review.server:app --host 0.0.0.0 --port 8000 \
  > /tmp/qbank_review.log 2>&1 &
```

This is an environment issue, not a code bug — don't "fix" `review/server.py`.

**2. `sqlite3` CLI is NOT installed.** Query the DB with Python:

```bash
.venv/bin/python3.11 -c "
import sqlite3
c = sqlite3.connect('run_data/db/qbank.db')
for r in c.execute(\"SELECT topic, review_status, COUNT(*) FROM questions WHERE source_book='year7_nsw_maths' GROUP BY 1,2\"): print(r)
"
```

### Current DB state (baseline, before this task)

| Subject | Approved | Pending | Rejected | Total |
|---|---:|---:|---:|---:|
| `quantitative_reasoning` | 1,637 | 596 | 7 | 2,240 |
| `science_reasoning` | 956 | 361 | 5 | 1,322 |
| `verbal_reasoning` | 398 | 623 | 8 | 1,029 |
| `reading_comprehension` | 634 | 84 | 1 | 719 |
| `logical_reasoning` | — | — | — | 0 |

Total 5,310.

---

## 4. DEDUPLICATE THE CURRICULUM FIRST

`year7_maths_curriculum.md` has **273 numbered items but only 266 unique titles**.
Generate against the 266. The 7 redundant lines:

| Duplicate title | Where |
|---|---|
| `Add and subtract decimals: word problems` | E, items 1, 2, 3 (**3×**) |
| `Divide decimals` | D item 4 **and** E item 11 (cross-category) |
| `Price lists` | M items 1 and 4 |
| `Translations: find the coordinates` | V items 3 and 4 |
| `Reflections: find the coordinates` | V items 5 and 6 |
| `Area and perimeter: word problems` | X items 7 and 8 |

Verify the count before starting:

```bash
cd /scratch/qbank/pdfs
grep -E '^[0-9]+\.' year7_maths_curriculum.md | sed 's/^[0-9]*\. //' | sort -u | wc -l   # → 266
```

**Known data issue:** heading **T** is labelled *One-Variable Inequalities* but
every item under it is a two-variable-equation / rate-of-change topic. Generate
to the **items**, not the heading. There is no inequality content in the file.

---

## 5. QUESTION SCHEMA — EXACT

Each generated JSON file is a **flat array** of question objects.

```json
[
  {
    "id": "<uuid4>",
    "subject": "quantitative_reasoning",
    "stem": "Two ferries leave Circular Quay at 9:00 am...",
    "option_a": "9:72 am",
    "option_b": "10:12 am",
    "option_c": "10:00 am",
    "option_d": "11:12 am",
    "correct_answer": "B",
    "explanation": "LCM(18, 24) = 2^3 x 3^2 = 72 min = 1 h 12 min after 9:00 am.",
    "topic": "Year 7: Number Theory",
    "difficulty": "medium",
    "confidence": 0.95,
    "source_book": "year7_nsw_maths",
    "source_page": 1,
    "source_page_description": "Subtopic A7 — HCF and LCM: word problems",
    "passage": null,
    "figure_svg": null,
    "review_status": "pending",
    "created_at": "2026-07-29T10:30:00Z"
  }
]
```

### Hard constraints (Phase 4 rejects violations)

| Field | Rule |
|---|---|
| `subject` | Always `"quantitative_reasoning"` |
| `correct_answer` | Exactly `"A"`, `"B"`, `"C"` or `"D"` — anything else is dropped |
| `difficulty` | Exactly `"medium"` or `"hard"` — **there is no `"easy"`** |
| `confidence` | Float 0.0–1.0, display-only, never used for auto-approval |
| `review_status` | Always `"pending"` — humans only set approved/rejected |
| `passage` | Always `null` for this subject |
| `topic` | `"Year 7: <Category Name>"` exactly as spelled in the curriculum file |
| `source_page` | Integer — use the batch number `NN` from the filename |
| `source_page_description` | `"Subtopic <Letter><Item#> — <subtopic title>"` for traceability |
| `figure_svg` | `null`, or an SVG string (see §6) |

### Difficulty mix

Roughly **80% `medium` / 20% `hard`** across the whole run — about 1 hard question
per 5 subtopics. Don't force a hard question into every subtopic.

### Content rules

- **Australian context mandatory** — Australian places, currency ($, GST at 10%),
  metric units, Australian names, local scenarios (ferries, servos, footy, surf
  clubs, drought, the Murray, CSIRO, Bunnings). No US spellings or contexts.
- Target a **Year 7 student sitting a competitive selective exam** — harder than
  classroom work, but Year 7 curriculum content only. No algebra beyond
  two-step equations, no trigonometry, no negative exponents beyond the listed items.
- **Distractors must be diagnostic** — each wrong option should correspond to a
  specific, plausible student error (wrong operation order, forgetting to convert
  units, subtracting instead of dividing, double-rounding). Never use filler options.
### ⚠️ Answer-key balance — enforce this mechanically, not by intention

**The pilot batch failed this badly: 20 of 30 answers were B.** Writing the correct
answer first and then padding distractors around it naturally parks the key in the
middle. Instructing yourself to "vary the key" does not work — the bias is structural.

**After writing each batch file, run this shuffle pass over it:**

```bash
.venv/bin/python3.11 - <<'PY'
import json, random, sys, pathlib
p = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "PATH_TO_BATCH.json")
qs = json.loads(p.read_text(encoding="utf-8"))
keys = ["option_a", "option_b", "option_c", "option_d"]
for q in qs:
    opts = [q[k] for k in keys]
    correct = opts[keys.index(f"option_{q['correct_answer'].lower()}")]
    random.shuffle(opts)
    for k, v in zip(keys, opts):
        q[k] = v
    q["correct_answer"] = "ABCD"[opts.index(correct)]
p.write_text(json.dumps(qs, indent=2, ensure_ascii=False), encoding="utf-8")
print({a: sum(1 for q in qs if q["correct_answer"] == a) for a in "ABCD"})
PY
```

Two cautions: it must run **before** `load_book`, and it will break any question
whose options are deliberately ordered (ascending values, "all of the above",
options referenced by position in the explanation). Avoid writing such questions —
or exclude them from the shuffle by hand.

Target roughly 25% per letter across the whole run. Check after loading:

```bash
.venv/bin/python3.11 -c "
import sqlite3; c = sqlite3.connect('run_data/db/qbank.db')
print(dict(c.execute(\"SELECT correct_answer, COUNT(*) FROM questions WHERE source_book='year7_nsw_maths' GROUP BY 1\")))
"
```

---

## 6. FIGURES — EXACTLY 50, INLINE SVG

`figure_svg` is **already fully wired**: the column exists in the live DB and in
`db/schema.sql:24`, `pipeline/phase4_load.py:40` inserts it, and
`review/ui/index.html:846` renders it inline (it auto-adds a `viewBox` if missing).
**No schema or code changes are needed.**

### SVG requirements

- Self-contained, no external references, no `<image>`, no web fonts
- **Include a `viewBox`** (the UI patches it if absent, but do it properly)
- Keep under ~2 KB; typical canvas 300×220
- Label with `<text>` elements; font-size 12–14
- Numbers in the figure **must** match the stem and the explanation exactly

### Colour — the figure card is WHITE, not dark

The review UI is a dark dashboard, but `.figure-container` deliberately renders
figures on a **white card** (`background: #ffffff`) so they read like exam paper.

Use `stroke="currentColor"` / `fill="currentColor"` throughout. The container sets
`color: #0D1117`, so `currentColor` resolves to near-black ink on the white card.
Never hard-code a light colour, and never assume a dark background.

> **Fixed during the pilot:** `.figure-container` set a white background but no
> `color`, so `currentColor` inherited the dark theme's `--text: #E6EDF3` and every
> figure rendered near-white on white — technically present, visually invisible.
> One line added at `review/ui/index.html:239`. If figures ever look washed out
> again, check that rule first before editing any SVG.

**Keep `opacity` above ~0.5 on anything load-bearing.** Faint gridlines that look
fine at 0.3 in a rendering tool become unreadable on the white card. Reserve low
opacity for background grid only, never for bars, points, or labels.

**Verify by rendering with the real colours**, substituting exactly what the UI does:

```python
svg = figure_svg.replace("currentColor", "#0D1117")
cairosvg.svg2png(bytestring=svg.encode(), write_to="check.png",
                 output_width=520, background_color="#ffffff")
```

(`cairosvg` is installed in the venv. Then `Read` the PNG and look at it.)

### The 50 figure subtopics

Give each of these **one** figure question; its second question is text-only.
Every other subtopic is text-only for both questions.

| Cat | Items | Count |
|---|---|---:|
| B | 2 | 1 |
| C | 2, 3 | 2 |
| F | 2 | 1 |
| G | 3 | 1 |
| H | 1, 4, 8, 14 | 4 |
| I | 1 | 1 |
| K | 5 | 1 |
| L | 1, 2, 3, 6 | 4 |
| N | 3 | 1 |
| P | 1, 2, 3 | 3 |
| R | 13 | 1 |
| S | 2, 3 | 2 |
| T | 5, 6, 7 | 3 |
| U | 1, 4, 8, 12, 13, 15, 19, 21 | 8 |
| V | 2, 8 | 2 |
| W | 1, 2, 3 | 3 |
| X | 6, 9 | 2 |
| Y | 2, 3, 6, 7, 10, 11, 12, 13 | 8 |
| Z | 1 | 1 |
| AA | 2 | 1 |
| | **TOTAL** | **50** |

### Everything else is text-only — including most geometry

Most "geometry" topics need no drawing; state the dimensions in the stem.
*"A quadrilateral has angles 95°, 118° and 63°. Find the fourth angle."* needs no
figure. Same for area/perimeter/volume with given dimensions, coordinate
transformations with given coordinates, and mean/median/mode with a given data list.

**Stem-and-leaf plots and frequency tables are Markdown/monospace text, not SVG.**

---

## 7. OUTPUT FILE NAMING — MUST MATCH THE LOADER GLOB

`phase4_load.load_book()` globs `*/generated/{book_id}_p*.json`. Filenames that
don't match are silently ignored.

```
run_data/output/quantitative_reasoning/generated/year7_nsw_maths_p<NN>.json
```

- `NN` is a sequential batch number starting at `1`
- **One file per turn**, ~10 questions (5 subtopics × 2)
- 266 subtopics ÷ 5 ≈ **54 files**, `p1` … `p54`
- Set each question's `source_page` to that batch's `NN`

Maintain `run_data/output/quantitative_reasoning/generated/year7_PROGRESS.md`,
appending one line per completed batch so the run is resumable after a context reset:

```
p1  | A1-A5   | 10 q | 0 fig | done
p2  | A6-A8, B1-B2 | 10 q | 1 fig | done
```

---

## 8. WORKING RULES — THESE DECIDE 2 DAYS VS 5

Context accumulation, not per-question cost, is what exhausts a Pro window. Every
question left in the transcript is re-sent on every subsequent turn.

1. **Write each batch to its JSON file immediately.** Never carry generated
   questions forward in conversation.
2. **`/compact` every ~6 turns.**
3. **10 questions per turn for text**, **6 per turn for figure batches.** Larger
   batches degrade — stems start repeating structure and arithmetic gets sloppy.
4. **Do all text-only subtopics first (Day 1), figures last (Day 2).** If the
   window runs out, you lose the expensive tail, not the whole run, and it resumes cleanly.
5. **Verify every calculation before writing it.** Work the arithmetic
   explicitly, then confirm the keyed option matches. This is the failure mode
   that made Gemini flash-lite unusable for QR — do not repeat it.
6. **For figure questions, render and look.** Write the SVG to a temp file,
   convert to PNG, and `Read` the image back to confirm it matches the stem before
   committing. A figure labelled 8 cm against a stem that says 6 cm is the error a
   human reviewer is least likely to catch.

### Day plan

| Day | Work | Questions | Files |
|---|---|---:|---|
| 1 | All text-only subtopics, A–AA | 482 | p1–p49 approx |
| 2 | The 50 figure questions + bulk contact-sheet QA | 50 | p50–p54 approx |

---

## 9. LOAD INTO THE DB

After each day (or after the first pilot batch), load with Phase 4:

```bash
cd /scratch/qbank
.venv/bin/python3.11 -c "
from pipeline.phase4_load import load_book
print(load_book('year7_nsw_maths'))
"
```

Returns `{"inserted": N, "duplicate": N, "failed": N}`.

### Watch the dedup counter

Phase 4 runs `SequenceMatcher` at **threshold 0.85, subject-scoped**. These
questions are compared against all **2,240 existing `quantitative_reasoning`
rows**, which are ACT-style year 9–12.

- A handful of duplicates is normal and healthy.
- **If `duplicate` exceeds ~5% of a batch, stop and inspect.** It likely means
  stems are too formulaic (same sentence skeleton with swapped numbers), which is
  a quality problem worth fixing before generating 500 more.
- `failed > 0` means a schema violation — almost always a bad `correct_answer`
  or a missing `stem`. Check the loader's log output.

---

## 10. REVIEW IN THE UI — QUALITY CHECK

```bash
cd /scratch/qbank
nohup .venv/bin/uvicorn review.server:app --host 0.0.0.0 --port 8000 &
```

Then browse to `http://<VM_IP>:8000`.

### Finding the new questions

`GET /questions` supports `subject` and `status` filters only, and orders by
`created_at DESC` — so **freshly loaded questions appear first**:

```
http://<VM_IP>:8000/questions?subject=quantitative_reasoning&status=pending
```

`GET /stats/topics` groups by topic, so every `Year 7: <Category>` entry shows as
its own row with pending/approved/rejected counts — the fastest way to confirm
coverage across all 27 categories.

> ⚠️ The keyboard review flow (`/questions/next`) orders by `confidence DESC`, so
> it will interleave these with the 596 pre-existing pending QR questions. For an
> isolated review pass, use the `/questions` list endpoint above.

### DO A PILOT BATCH FIRST

**Before generating all 532**, produce **one batch of ~10 questions spanning three
different category types** — one arithmetic (e.g. A or E), one algebra (R or S),
one figure-based (U or Y). Load it, view it in the review UI, and get explicit
sign-off on quality and formatting. Only then continue.

Keyboard shortcuts in the UI: `A` approve · `R` reject · `E` edit · `←` `→` navigate.

---

## 11. DEFINITION OF DONE

- [ ] 266 unique subtopics covered, 2 questions each = 532 questions
- [ ] Exactly 50 questions have non-null `figure_svg`; all 50 rendered and visually verified
- [ ] All arithmetic independently verified; keyed option matches the explanation
- [ ] Every row: `subject='quantitative_reasoning'`, `source_book='year7_nsw_maths'`,
      `topic` prefixed `Year 7: `, `review_status='pending'`
- [ ] `difficulty` is only `medium`/`hard`; mix is roughly 80/20
- [ ] Australian context throughout
- [ ] All batches loaded via `load_book('year7_nsw_maths')`; `failed = 0`
- [ ] `duplicate` under 5% of total
- [ ] `year7_PROGRESS.md` complete, all 54 batches marked done
- [ ] Spot-checked in the review UI across all 27 categories via `/stats/topics`

---

## 12. WHAT THIS TASK IS NOT

- Not a Gemini pipeline run. There is **no PDF and no briefing file** — questions
  are generated directly from the curriculum topic list. Phases 1–3 do not apply;
  only Phase 4 (load) is used.
- Not production volume. 532 questions validates the approach. The full run
  (10 per subtopic ≈ 2,660 questions) goes through the Claude Batch generator once
  quality is signed off.
- Not auto-approved. Every question lands as `pending` and goes to human review,
  regardless of `confidence`.
