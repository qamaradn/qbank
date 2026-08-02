# TASK BRIEFING — Year 9 Maths Question Generation

> **For a fresh Claude Code session.** Read this file completely before generating anything.
> Also read `/scratch/qbank/CLAUDE.md` for project-wide rules.
> **Run `/model opus` before starting** — arithmetic correctness is the whole point of this job.
> Companion task, already complete: `year7_nsw_maths_TASK.md` (532 questions, all loaded).

---

## 1. OBJECTIVE

Generate **543 MCQ questions** covering the Australian Year 9 maths curriculum.

- Source curriculum: `/scratch/qbank/pdfs/year9_maths_curriculum.md`
- The raw list has 37 categories and 240 items. **Eight categories and 13 individual items
  are out of scope and are dropped** (§2) — leaving **29 categories, 183 items,
  181 unique subtopics**.
- **3 questions per unique subtopic** = 543 questions
- **71** of those carry an inline SVG figure (list in §6); the other 472 are text-only

Same strategy as the Year 7 run, which finished at 532 questions with `failed = 0`,
`duplicate = 0`, keys balanced 133/133/133/133 and 20.0% hard. Follow that shape.

> **Why 3 per subtopic and not 2:** the platform's premise is that a student never sees the
> same question twice, so depth on topics they will actually sit beats breadth across topics
> they will not. Trading the out-of-scope categories for a third question costs almost nothing
> overall — figures fall from 91 to 71, and figures are by far the most expensive work.

---

## 2. SUBJECT — `mathematics` (this changed since the Year 7 task)

The Year 7 briefing told you *not* to create a `mathematics` subject. **That is now obsolete.**
`mathematics` was added on 2026-07-30 as the seventh subject, and the 532 Year 7 questions
were migrated into it.

```
subject     = "mathematics"
source_book = "year9_maths"
topic       = "Year 9: <Category Name>"     e.g. "Year 9: Trigonometry"
```

| Subject | Meaning |
|---|---|
| `mathematics` | curriculum-based maths, keyed to a year level ← **this task** |
| `quantitative_reasoning` | test-style quantitative questions from exam papers |
| `logical_reasoning` | NSW selective **Thinking Skills** — reserved, do not use |

- **Do NOT** add a `year_level` column. The `Year 9:` topic prefix plus `source_book`
  distinguishes these, exactly as `Year 7:` does. `GET /stats/topics` groups by `topic`,
  so all 29 surviving categories appear as their own rows with no code change.
- **Do NOT** reuse `logical_reasoning`. It looks empty but the Selectly app maps it to the
  NSW Thinking Skills section (40 questions / 40 min).

### ⚠️ SCOPE — DROP THESE. DECIDED 2026-07-30, DO NOT RE-ADD.

The source list is titled "Grade 9" and is IXL-derived, so a chunk of it sits **above** the
Australian Year 9 curriculum — most of it Year 11–12 Methods or Specialist. Adnan decided to
drop that material and spend the effort on a third question per remaining subtopic instead.

**Eight whole categories are out (44 subtopics):**

| Cat | Category | Items | Why out |
|---|---|---:|---|
| I | Inequalities and Linear Programming | 5 | linear programming is not in the 7–10 curriculum |
| J | Matrices | 6 | not in the Australian 7–10 curriculum at all |
| L | Logarithms | 6 | Year 11 Methods |
| M | Exponential and Logarithmic Functions | 6 | Year 11 Methods |
| T | Hyperbolas | 7 | conics — Year 11/12 Specialist |
| X | Logic | 5 | formal logic and truth tables are not in 7–10 maths |
| CC | Angle Measures | 4 | radians, coterminal and reference angles — Year 11 |
| GG | Circles in the Coordinate Plane | 5 | circle equations — Year 11 |

**Thirteen further items are out, inside categories that otherwise stay (13 subtopics):**

| Ref | Item | Why out |
|---|---|---|
| B4, B5 | Continuously compounded interest I and II | needs `e` — Year 11/12 |
| O6 | Synthetic division | Year 11 |
| O8, O9 | Polynomial graphs; domain and range of polynomials | Year 11 |
| S2 | Focus and directrix | Year 12 Specialist |
| DD2–DD6 | Unit circle; special angles; trigonometric functions; inverse trig; trig equations | Year 11 Methods |
| FF4 | Radians and degrees | Year 11 |
| JJ5 | Variance and standard deviation | Year 11/12 |

**Keep the original refs.** Do not renumber surviving items — `S3` stays `S3` even though `S2`
is gone. The refs are the traceability link back to the curriculum file.

**Two borderline blocks were deliberately KEPT**, being NSW Stage 5.3 / Year 10 and fair game
for a selective or scholarship candidate: the circle-geometry group (FF6 chords, FF7 tangents,
FF8 inscribed angles) and the sine and cosine rules (DD8, DD9). If Adnan later wants those out
too, it drops to roughly 176 subtopics / 528 questions.

---

## 3. KEY PATHS AND FACTS

```
Repo root      /scratch/qbank
Python         .venv/bin/python3.11        ← never bare python/python3
DB             run_data/db/qbank.db
Generated JSON run_data/output/mathematics/generated/      ← note: mathematics, not QR
Review server  uvicorn review.server:app --host 0.0.0.0 --port 8000
Figure QA      python -m tools.figure_contact_sheet        ← committed tool, see §6
```

### ⚠️ Three environment gotchas

**1. `PYTHONPATH` shadows the venv.** `PYTHONPATH=/scratch/python-packages` precedes the
venv in `sys.path` and shadows its working `pydantic` with a broken copy
(`ModuleNotFoundError: pydantic_core._pydantic_core`). Anything importing pydantic —
uvicorn, pytest, anthropic — needs `env -u PYTHONPATH`:

```bash
env -u PYTHONPATH nohup .venv/bin/uvicorn review.server:app --host 0.0.0.0 --port 8000 \
  > /tmp/qbank_review.log 2>&1 &
```

This is an environment issue, not a code bug — don't "fix" `review/server.py`.

**2. `sqlite3` CLI is NOT installed.** Query with Python's `sqlite3` module.

**3. Chromium/Playwright cannot launch** (`libatk-1.0.so.0` missing). There is no
real-browser check available; figure QA goes through cairosvg — see §6.

### Current DB state (baseline, before this task)

| Subject | Total | Note |
|---|---:|---|
| `quantitative_reasoning` | 2,240 | ACT-style, year 9–12 band |
| `science_reasoning` | 1,322 | |
| `verbal_reasoning` | 1,029 | |
| `reading_comprehension` | 719 | |
| **`mathematics`** | **532** | all Year 7 — **this is what dedup compares you against** |
| `logical_reasoning` | 0 | reserved |

Total 5,842. Nothing is approved except 3,625 already pushed to Selectly.

---

## 4. BUILD THE MANIFEST FIRST — AND VERIFY IT COMES TO 181

After the §2 drops, 183 items remain, of which **181 are unique titles**. Two titles appear
twice and both survivors are in kept categories; generate each once:

| Duplicate title | Where |
|---|---|
| `Power rule` | K5 **and** U3 (Exponents / Rational Exponents) |
| `Similar figures` | W9 **and** AA1 (2-D Figures / Similarity) |

Generate under the **first** occurrence and mark the second as covered in the progress file,
so the manifest totals 181.

Run this before anything else. It is the single source of truth for the whole run — if it does
not print `181 unique subtopics / 71 figures`, stop and find out why:

```python
import re, pathlib
from collections import OrderedDict
cats, cur = OrderedDict(), None
for ln in pathlib.Path("pdfs/year9_maths_curriculum.md").read_text().splitlines():
    m = re.match(r"^##\s+([A-Z]{1,2})\.\s+(.+?)\s*$", ln)
    if m: cur = m.group(1); cats[cur] = {"name": m.group(2), "items": []}; continue
    m2 = re.match(r"^\s*-\s+(.+?)\s*$", ln)
    if m2 and cur: cats[cur]["items"].append(m2.group(1))

DROP_CATS  = ["I", "J", "L", "M", "T", "X", "CC", "GG"]
DROP_ITEMS = {"B": [4, 5], "O": [6, 8, 9], "S": [2],
              "DD": [2, 3, 4, 5, 6], "FF": [4], "JJ": [5]}
FIG = {"C":[1],"D":[2,3],"E":[1,2,6,8,10],"F":[1,4,6,8,9],"G":[2,6,7,9,13],"H":[2,7],
       "O":[2],"Q":[1,2,3,10],"R":[1,3],"S":[1,3,6],"W":[2,3,6,7,8,9],"Y":[1,3,4],
       "Z":[1,2,3,4],"AA":[4,5,6],"BB":[1,4],"DD":[7,8,9,10],"EE":[1,2,4,5],
       "FF":[1,2,3,5,6,7,8],"II":[6],"JJ":[2],"KK":[1,2,5,6,7,8]}

rows = []
for c, d in cats.items():
    if c in DROP_CATS: continue
    for i, t in enumerate(d["items"], 1):
        if i in DROP_ITEMS.get(c, []): continue
        rows.append({"ref": f"{c}{i}", "cat": c, "item": i, "title": t,
                     "topic": f"Year 9: {d['name']}",
                     "needs_figure": i in FIG.get(c, []),
                     "have": 0, "have_figure": False})
# the second of each duplicate pair is covered by the first
DUPE_SECONDS = {"U3", "AA1"}
uniq = [r for r in rows if r["ref"] not in DUPE_SECONDS]
print(len(uniq), "unique subtopics /", sum(r["needs_figure"] for r in uniq), "figures")
```

Write the result to `run_data/output/mathematics/generated/year9_MANIFEST.json`, then a
`year9_PLAN.json` assigning subtopics to batches. The Year 7 run survived two context resets
cleanly because these existed — copy that machinery.

### Known list flaws — generate to the items, not the headings

- **W9 `Similar figures` vs AA1** — same title, different categories. See above.
- **H6 is just `Word problems`** with no qualifier; it means simultaneous-equation word
  problems. Likewise **EE6 `Review`** — a grab-bag item. Write it as a genuine mixed question
  spanning its category, not a repeat of item 1.
- **S `Parabolas` loses its focus/directrix item**, so it is now vertex, axis of symmetry,
  equations, vertex/general form and graphing — all Year 10-appropriate.


---

## 5. QUESTION SCHEMA — EXACT

Each generated JSON file is a **flat array** of question objects.

```json
[
  {
    "id": "<uuid4>",
    "subject": "mathematics",
    "stem": "A ute hire firm in Cairns charges c = 48 + 0.25k dollars...",
    "option_a": "300 km",
    "option_b": "492 km",
    "option_c": "684 km",
    "option_d": "18.75 km",
    "correct_answer": "A",
    "explanation": "Subtract the $48 fee: 0.25k = 75, so k = 75 / 0.25 = 300 km. 492 km ignores the fee...",
    "topic": "Year 9: Linear Functions",
    "difficulty": "medium",
    "confidence": 0.94,
    "source_book": "year9_maths",
    "source_page": 1,
    "source_page_description": "Subtopic G7 — Write linear equations from graphs, tables and word problems",
    "passage": null,
    "figure_svg": null,
    "review_status": "pending",
    "created_at": "2026-07-31T10:30:00Z"
  }
]
```

### Hard constraints (Phase 4 rejects violations)

| Field | Rule |
|---|---|
| `subject` | Always `"mathematics"` |
| `correct_answer` | Exactly `"A"`, `"B"`, `"C"` or `"D"` |
| `difficulty` | Exactly `"medium"` or `"hard"` — **there is no `"easy"`** |
| `confidence` | Float 0.0–1.0, display-only, never used for auto-approval |
| `review_status` | Always `"pending"` — humans only set approved/rejected |
| `passage` | Always `null` |
| `topic` | `"Year 9: <Category Name>"` exactly as spelled in the curriculum file |
| `source_page` | Integer — the batch number `NN` from the filename |
| `source_page_description` | `"Subtopic <Cat><Item#> — <title>"` — **em dash, not hyphen** |
| `figure_svg` | `null`, or an SVG string (see §6) |

The em dash in `source_page_description` matters: the finalise script matches
`r"Subtopic ([A-Z]{1,2}\d+) — (.+)$"`. The 30 Year 7 pilot rows used a hyphen and are
inconsistent as a result — don't repeat that.

### ⚠️ THREE QUESTIONS PER SUBTOPIC MEANS THREE DIFFERENT SHAPES

This is the hardest requirement in the brief and the one most likely to be quietly violated.

At two per subtopic the Year 7 run still tripped the near-duplicate screen repeatedly — my own
stems collided at 0.83–0.90 purely from sharing a sentence skeleton. **At three per subtopic
the third question is where it breaks.** The natural failure is writing question 1 and then
producing questions 2 and 3 by swapping the digits.

Give each subtopic three genuinely different **question shapes**, for example:

| Shape | Example for "Solve two-step linear equations" |
|---|---|
| bare skill | `Solve 5 - 3x/4 = 14.` |
| applied context | `A plumber in Hobart charges $90 call-out plus $65/h. A bill is $415 — how many hours?` |
| reverse / diagnostic | `A student solved 4x - 7 = 21 and got x = 3.5. Which step did they get wrong?` |

Other reusable third shapes: "which of these equations has no solution", "fill the missing
value in this working", "two students disagree — who is right and why", "estimate before
calculating: which answer is impossible", "given the answer, find the missing coefficient".

Test it, don't trust it — before finalising a batch, check every new stem against every other
stem for that subtopic:

```python
from difflib import SequenceMatcher
# any pair above 0.75 within one subtopic means shape repetition, not just new numbers
```

The 0.82 screen in finalise is the backstop, **not** the target. A pair at 0.78 passes the
screen and is still three variations of one question.

### Difficulty mix

Roughly **80% medium / 20% hard** — about **109 hard** of 543. Year 9 content is harder in
absolute terms, but the label is relative to a Year 9 student, so do not mark everything hard.
Aim for **2 hard per 10-question batch**, 1 per 6-question figure batch; that landed Year 7 on
exactly 20.0%. A natural fit is to make the third, most demanding shape the hard one in
roughly one subtopic out of five.

### Content rules

- **Australian context mandatory** — Australian places, currency ($, GST 10%), metric units,
  Australian names and scenarios. No US spellings or contexts.
- Target a **Year 9 student sitting a competitive selective or scholarship exam**.
- **Distractors must be diagnostic.** Every wrong option corresponds to one specific,
  plausible error, and the explanation must name it. Never use filler options.
  Year 9 has rich, characteristic errors worth using: losing a sign when multiplying out a
  negative bracket, `(a+b)^2 = a^2+b^2`, flipping the inequality when dividing by a negative,
  `log(a+b) = log a + log b`, using degrees where radians are required, taking only the
  positive square root, `sin`/`cos` swapped in SOH-CAH-TOA, forgetting the ± on a discriminant.
- Do **not** write "all of the above", "none of the above", or options that reference their
  own position — they break the answer-key shuffle (below).

### ⚠️ Answer-key balance — enforce mechanically, never by intention

Writing the correct answer first and padding distractors around it parks the key in the
middle. The Year 7 pilot came out **20 of 30 answers = B**. Telling yourself to vary it
does not work; the bias is structural.

The Year 7 run solved this properly: rather than a blind random shuffle, the finalise script
shuffles each question toward **the letter with the lowest running count** (DB rows so far,
plus unloaded batch files). That converges on exactly 25% each instead of merely
approximately. Reuse that approach — see `year7_finalise.py` in
`run_data/output/mathematics/generated/`, which is worth generalising into `year9_finalise.py`
rather than rewriting from scratch.

Check after loading (target ~136 per letter, 543 / 4):

```bash
.venv/bin/python3.11 -c "
import sqlite3; c = sqlite3.connect('run_data/db/qbank.db')
print(dict(c.execute(\"SELECT correct_answer, COUNT(*) FROM questions WHERE source_book='year9_maths' GROUP BY 1\")))
"
```

---

## 6. FIGURES — 91, INLINE SVG

`figure_svg` is already fully wired: the column is in the live DB and `db/schema.sql`,
`phase4_load.py` inserts it, and `review/ui/index.html` renders it inline.
**No schema or code changes needed.**

### SVG requirements

- Self-contained — no external references, no `<image>`, no web fonts
- **Include a `viewBox`**; typical canvas ~340×220
- Keep under ~2 KB. For grids use **one `<path>`** with `M…V…H…` segments, not 100 `<rect>`s
- Label with `<text>`, font-size 9–14; numbers in the figure **must** match stem and explanation

### Colour — the figure card is WHITE

The review UI is a dark dashboard, but `.figure-container` renders figures on a white card
with `color: #0D1117`. Use `stroke="currentColor"` / `fill="currentColor"` throughout so the
ink resolves to near-black. Never hard-code a colour, never assume a dark background.

**Keep `opacity` above ~0.5 on anything load-bearing.** Use ~0.35 only for background
gridlines, ~0.55 for bars and shaded regions, ~0.22 for supporting bands.

### Generate the geometry, don't type it

Emit coordinates from the real geometry in code — "offset 83 with height 100 gives sides of
130" — not from four guessed points. This is what lets the verification step actually check
the drawing. A hand-typed "rhombus" in the Year 7 run had sides of 155 and 125 while its stem
told students all four sides were equal; only computing the side lengths exposed it.

### Two-pass QA is MANDATORY — see the standing rule

**Pass 1, by code:** side lengths, interior angles, parallel-side pairs, shoelace areas, real
rotation matrices. Assert uniqueness wherever the question depends on it (exactly one option
on the line, mode not tied).

**Pass 2, by eye:**

```bash
# before loading — the cheap moment to catch problems
env -u PYTHONPATH .venv/bin/python3.11 -m tools.figure_contact_sheet \
    --json run_data/output/mathematics/generated/year9_maths_p42.json
# after loading
env -u PYTHONPATH .venv/bin/python3.11 -m tools.figure_contact_sheet --subject mathematics --page 42
```

Then **`Read` the PNG and look at it.** It renders at the card's real colours, so contrast
problems show up. Code alone missed nine defects across seven Year 7 figures: labels clipped
past the viewBox edge, Venn labels overlapping circles, a balance scale whose weights sat on
the beam with empty pans dangling below, hanger lines through the blocks, a kite drawn
near-equilateral so it read as a rhombus. **Re-check after fixing** — two of those needed a
second round because the fix introduced a new collision.

### The 71 figure subtopics

Give each of these **one** figure question; its other two questions are text-only. Every other
subtopic is text-only for all three. Refs are the original curriculum numbers — the §2 drops
removed 20 figure subtopics from the pre-drop list of 91.

> **Why 71 and not 72:** `Similar figures` is the duplicate title at W9 and AA1, and both were
> graphical candidates. Since the title is generated once — under the first occurrence, W9 —
> AA1 leaves the manifest and its figure slot goes with it. Do not "restore" AA1 to this table.

| Cat | Category | Items | Count |
|---|---|---|---:|
| C | Coordinate Plane | 1 | 1 |
| D | Solve Equations | 2, 3 | 2 |
| E | Single-Variable Inequalities | 1, 2, 6, 8, 10 | 5 |
| F | Relations and Functions | 1, 4, 6, 8, 9 | 5 |
| G | Linear Functions | 2, 6, 7, 9, 13 | 5 |
| H | Simultaneous Equations | 2, 7 | 2 |
| O | Polynomials | 2 | 1 |
| Q | Quadratic Equations | 1, 2, 3, 10 | 4 |
| R | Functions: Linear, Quadratic, Exponential | 1, 3 | 2 |
| S | Parabolas | 1, 3, 6 | 3 |
| W | Two-Dimensional Figures | 2, 3, 6, 7, 8, 9 | 6 |
| Y | Introduction to Congruent Figures | 1, 3, 4 | 3 |
| Z | Congruent Triangles | 1, 2, 3, 4 | 4 |
| AA | Similarity | 4, 5, 6 | 3 |
| BB | Right Triangles | 1, 4 | 2 |
| DD | Trigonometry | 7, 8, 9, 10 | 4 |
| EE | Surface Area and Volume | 1, 2, 4, 5 | 4 |
| FF | Circles | 1, 2, 3, 5, 6, 7, 8 | 7 |
| II | Probability | 6 | 1 |
| JJ | Statistics | 2 | 1 |
| KK | Data and Graphs | 1, 2, 5, 6, 7, 8 | 6 |
| | | **TOTAL** | **71** |

That is 39% of the 181 subtopics, against 19% for Year 7 — Year 9 is genuinely more graphical
(coordinate graphs, parabolas, circle theorems, congruence, similarity, box and scatter plots).

### Everything else is text-only — including most geometry

State the dimensions in the stem. *"A quadrilateral has angles 95°, 118° and 63°. Find the
fourth."* needs no figure. Same for area/volume with given dimensions, Pythagoras with given
sides, coordinate transformations with given coordinates, and statistics from a given list.

**Truth tables (X4), frequency tables, stem-and-leaf plots (KK3, KK4) and matrices are
Markdown pipe tables, not SVG.** The review UI renders pipe tables in stems as real tables
(added 2026-07-30), so use that rather than drawing them.

---

## 7. OUTPUT FILE NAMING — MUST MATCH THE LOADER GLOB

`phase4_load.load_book()` globs `*/generated/{book_id}_p*.json`. Non-matching names are
silently ignored.

```
run_data/output/mathematics/generated/year9_maths_p<NN>.json
```

- `NN` sequential from `1`; set each question's `source_page` to its batch `NN`
- **10 questions per turn for text**, **6 per turn for figures**
- 472 text-only ÷ 10 = **48 batches**, then 71 figures ÷ 6 = **12 batches** → **60 files**

Maintain `run_data/output/mathematics/generated/year9_PROGRESS.md`, one line per batch, so
the run is resumable after a context reset:

```
p1  | A1-A4, B1  | 10 q | 0 fig | 2 hard | done
```

The manifest and plan are built in §4. `have` counts up to **3** per subtopic now, not 2 —
make sure the finalise script's completion check uses 3, or it will report the run finished a
third early.

---

## 8. WORKING RULES — THESE DECIDE 2 DAYS VS 5

Context accumulation, not per-question cost, exhausts the window. Every question left in
the transcript is re-sent on every later turn.

1. **Write each batch to its JSON file immediately.** Never carry questions forward in
   conversation.
2. **`/compact` every ~6 turns.**
3. **10 per turn text, 6 per turn figures.** Larger batches degrade — stems start repeating
   structure and arithmetic gets sloppy.
4. **All text-only subtopics first (Day 1), figures last (Day 2).** If the window runs out
   you lose the expensive tail, not the whole run.
5. **Verify every calculation independently before writing it** — not by re-reading your own
   arithmetic. Use `fractions.Fraction(str(x))` for money and decimals (never floats), and
   `sympy` for algebra, expansion, factorising and solving. Check every keyed answer **and**
   every distractor's stated derivation: if an explanation claims an option comes from adding
   instead of multiplying, assert that arithmetic produces exactly that option.
6. **Figures: render and look** (§6). Non-negotiable.

### Day plan

| Day | Work | Questions | Files |
|---|---|---:|---|
| 1 | All text-only questions, A–KK (3 per subtopic, minus the figure slots) | 472 | p1–p48 |
| 2 | The 71 figure questions | 71 | p49–p60 |

---

## 9. LOAD INTO THE DB

Per batch, mirroring the Year 7 flow:

```bash
.venv/bin/python3.11 run_data/output/mathematics/generated/year9_finalise.py NN
DB_PATH=run_data/db/qbank.db .venv/bin/python3.11 \
  run_data/output/mathematics/generated/year9_load_one.py NN
```

`finalise.py` validates the schema, screens near-duplicates (both against the DB and within
the subtopic — see §5), balances the answer key and updates the manifest and progress file. Loading returns
`{"inserted": N, "duplicate": N, "failed": N}`.

### ⚠️ Dedup: what it actually compares, and what to worry about

Phase 4 runs `SequenceMatcher` at **0.85, scoped by `subject`**. Since Year 7 and Year 9 are
both `mathematics`, your stems are compared against **the 532 Year 7 rows** — not against
`quantitative_reasoning`.

**Cross-year collision is a measured non-problem.** Seven subtopic titles are identical
across the two years (B8/M8, D2/S2, D3/S3, K2/J5, W1/U7, FF1/U19, II2/AA3) and sixteen more
are near-identical, but realistic Year 9 stems score only **0.33–0.60** against their Year 7
counterparts. Year 9 content diverges naturally. Do not waste effort defending against this.

**The real risk is formulaic phrasing, and it is year-agnostic:**

| Pair | Ratio |
|---|---:|
| `Solve the equation 4x + 9 = 41` vs `Solve the equation 7x - 14 = 35` | 0.825 |
| `Which expression is equivalent to …?` twice, different contents | 0.825 |
| `area of the L-shaped figure shown` vs `T-shaped` | **0.978** |
| The same pair, each with an Australian context clause | **0.430** |

So: **never ship a bare `Solve the equation …` stem.** One context clause drops the ratio by
about 0.4 on its own. Screen at **0.82 and fail the batch** rather than letting Phase 4
silently drop at 0.85 — that is what `year7_finalise.py` does, and it caught several
collisions per day during the Year 7 run.

If `duplicate` exceeds ~5% of a batch, stop and inspect. `failed > 0` is a schema violation,
almost always a bad `correct_answer` or a hyphen where the em dash belongs.

---

## 10. REVIEW IN THE UI

```bash
env -u PYTHONPATH nohup .venv/bin/uvicorn review.server:app --host 0.0.0.0 --port 8000 \
  > /tmp/qbank_review.log 2>&1 &
```

Then browse to `http://<VM_IP>:8000` and click **Mathematics** in the Subject sidebar.

```
http://<VM_IP>:8000/questions?subject=mathematics&status=pending
```

`GET /stats/topics` groups by topic, so every `Year 9: <Category>` entry appears as its own
row — the fastest way to confirm coverage across all 29 surviving categories. Note it excludes rows
with an empty `topic`, so its totals can read slightly low.

### DO A PILOT BATCH FIRST

**Before generating all 543**, produce **one batch of ~10 questions spanning three different
category types** — one algebraic (D or Q), one graphical with a figure (G or S), one
geometry/trig (DD or FF). Load it, view it in the review UI, and get explicit sign-off on
quality and formatting. Only then continue.

Keyboard: `A` approve · `R` reject · `E` edit · `←` `→` navigate.

---

## 11. DEFINITION OF DONE

- [ ] 181 unique subtopics covered (after the §2 drops), 3 questions each = 543 questions
- [ ] Exactly 71 have non-null `figure_svg`; all 71 rendered via
      `tools/figure_contact_sheet.py` and visually checked against their stems
- [ ] All arithmetic independently verified; every keyed option and every distractor's
      stated derivation confirmed by code
- [ ] Every row: `subject='mathematics'`, `source_book='year9_maths'`, `topic` prefixed
      `Year 9: `, `review_status='pending'`
- [ ] `source_page_description` uses the **em dash** and matches the manifest title exactly
- [ ] `difficulty` only `medium`/`hard`; mix roughly 80/20
- [ ] Answer keys within a few of 136 each (543 / 4)
- [ ] No pair of stems within one subtopic above 0.75 — three shapes, not three number sets
- [ ] None of the 8 dropped categories or 13 dropped items appears anywhere in the output
- [ ] Australian context throughout
- [ ] `failed = 0`; `duplicate` under 5%
- [ ] Worst internal stem similarity below 0.85 across the whole `mathematics` subject
- [ ] `year9_PROGRESS.md` complete, all 60 batches marked done
- [ ] Spot-checked in the review UI across all 29 surviving categories via `/stats/topics`

---

## 12. WHAT THIS TASK IS NOT

- Not a Gemini pipeline run. There is **no PDF and no briefing file** — questions come
  straight from the curriculum topic list. Phases 1–3 do not apply; only Phase 4 (load).
- Not a model-verified pass. The Year 7 book was hand-authored and checked by code plus eyes;
  `verify_questions.py` was never run on it (0 `.verified` markers against 109 for other
  books). Do the same here unless told otherwise.
- Not production volume. 543 questions validates breadth and gives three variants per
  subtopic. A deeper run (10 per subtopic ≈ 1,810) goes through the Claude Batch generator
  once quality is signed off.
- Not auto-approved. Everything lands `pending` for human review regardless of `confidence`.
- Not reaching students yet. Selectly does not know the `mathematics` category — its
  TypeScript union and a section config must be updated first. Tracked in the Selectly repo's
  own notes; nothing in this task depends on it.
