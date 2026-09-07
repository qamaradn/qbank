# NSW figure review, round 1 — prompt for a fresh context window

Paste everything below the line into a new session.

---

NSW figure review, round 1. Read CLAUDE.md CURRENT STATUS first for the background, and
the memories `reference-figure-authoring-failure-modes` and
`reference-figure-check-traps` before writing any repair.

## THE JOB

Alaan Q.'s first NSW return is at:

    review/ui/figure-review-nsw-2026-09-06.json

Read it with:

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.ingest_figure_review \
        review/ui/figure-review-nsw-2026-09-06.json

**Ten flags on a 254-card page.** All ten are `pending`; none is live in Selectly. Work
only on those ten — every other card was looked at and left alone.

| # | id | form | what they said |
|---|---|---|---|
| 8 | `bf613208` | nsw-drill-ts-013 | figure full of unclear values, 6 cm overlaps sides, vague 4 cm values |
| 53 | `d5975559` | nsw-drill-ts-026 | *the same note* — it is the same picture |
| 142 | `05abece6` | nsw-drill-math-014 | 3 m and 2 m too close together; move each nearer the side it names |
| 151 | `7932815e` | nsw-drill-math-018 | 3 m and 4 m too close together; same fix |
| 214 | `b2c8c7b6` | nsw-drill-math-013 | "far too difficult and doesn't really make sense. Delete." |
| 217 | `4769e94e` | nsw-drill-math-016 | P and Q overlap the x-axis; move them nearer their points |
| 218 | `c17f98d2` | nsw-drill-math-017 | extend the line so it reaches (5, 20) |
| 239 | `8de54934` | nsw-drill-math-032 | add axis ticks; more clearance between −2 and the line |
| 244 | `2bc8b93a` | nsw-drill-math-035 | more values on the axes, plus tick marks |
| 250 | `7abd8a82` | nsw-drill-math-038 | the 4 cm labels depth but is drawn on a height edge |

Two `logical_reasoning` (Thinking Skills), eight `mathematics`.

## FOUR THINGS TO KNOW BEFORE STARTING

**1. #8 and #53 share one figure, byte for byte.** Same 1,429-character SVG on two
different questions — one asks for the area of the U-shaped tile, the other for its
perimeter. That is why the reviewer wrote the same sentence twice. Fix the drawing once
and write it to BOTH rows, or the second one comes straight back.

**2. Seven of the ten are invisible to every check.** Only #217, #239 and #244 fire
anything (`text_overlaps_geometry`, a tick number on an axis). The other seven are clean
by machine and wrong to a human — the same lesson VIC round 8 taught. Do not use a clean
check state as evidence a figure is right; render it and look.

**3. NSW is genuinely cleaner than VIC and that is not luck.** 320 NSW figures, 12 firing
the gate (4%); 512 VIC figures, 88 firing (17%). The reviewer flagged 10 of 254 (4%)
against VIC's 181 of 445 (41%). NSW was authored through `question_checks`; the Gemini
books were not. Expect a small round, and do not go looking for VIC-sized trouble.

**4. #214 asks for a deletion, which is a decision, not a repair.** Read the question,
work out whether it is genuinely out of scope for a Year 6-7 paper, and either re-cut it
the way `46c3108f` was re-cut in VIC round 10, or reject it and say so. Do not delete a
question from a dealt form without saying what it does to the form's size — the NSW forms
are 19-26 items and losing one silently re-bases every score recorded against it.

## THE RULE

Work ONLY on those ten. Do not sweep, do not repair anything the reviewer did not name,
do not touch VIC, and do not touch anything `approved` — 66 NSW figures are already live
from the August pilot and none of the ten is among them, but check the scope before any
`--apply`.

## HOW TO WORK

- Back up the database before the first write:
  `cp run_data/db/qbank.db run_data/db/qbank.db.bak-nsw1-$(date +%H%M%S)`
- Copy `tools/repair_vic_round11_figures.py` as the model: one builder per question, a
  `state()` that runs every check, and a refusal to write anything that would gain a
  finding.
- Render and LOOK before applying — `tools/figure_contact_sheet.py --db <db> --ids "…"`,
  four at a time so the sheet stays under the image limit.
- Diff the whole check state before and after and require **"newly firing: none"**.
- Verify by reading back what you actually wrote, not by re-running your own builder.
  Measure the shipped SVG: the coordinates, not the code that drew them.
- Plain English in the summary. Short sentences, ordinary words, numbers at the end.

## WHEN DONE — BUILD THE PAGE BACK

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.figure_compare_page \
        --before run_data/db/qbank.db.bak-nsw1-<your timestamp> \
        --review review/ui/figure-review-nsw-2026-09-06.json \
        --scope nsw-round1 \
        --ids "<the ten ids, comma separated>"

That writes `review/ui/compare-nsw-round1.html`. Check the counts: 10 cards, 10 carrying
a note, 10 redrawn. Then verify the page by parsing its own data back against the live
database and the backup — every before-picture from the backup, every after-picture,
stem, option and key from the live row.

Env: always `env -u PYTHONPATH .venv/bin/python3.11`
DB: `run_data/db/qbank.db`
