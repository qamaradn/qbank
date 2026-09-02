# VIC figure recheck, round 10 — prompt for a fresh context window

Paste everything below the line into a new session.

---

VIC figure recheck, round 10. Read CLAUDE.md CURRENT STATUS first for the background.

## THE JOB

Alaan Q has sent their next batch of comments:

    review/ui/figure-review-vic-mq-recheck-2026-09-01.json

Read it with:

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.ingest_figure_review \
        review/ui/figure-review-vic-mq-recheck-2026-09-01.json

**That file holds 95 comments, and 49 of them are old news.** Alaan is working through
one long page and re-downloading the whole thing each time, so every note from the
31 August file is still in it. Those 49 are the cards numbered 2 to 113 and they were
all repaired in round 9. I checked: all 49 notes are byte-for-byte identical to the
31 August file, so nothing new is hiding among them.

**Your work is the 46 comments on cards numbered ABOVE 113. Skip everything at 113 or
below.** Their card numbers are:

    122 123 124 126 127 128 129 130 132 135 136 137 139 141 142 143 144 146 148 150
    154 157 159 162 163 164 165 166 170 172 173 174 179 183 186 192 199 200 204 206
    207 210 211 217 218 222

All 46 are `pending`. None is live in Selectly.

The ingest will warn that four questions changed since the page was built (#60, #63,
#74, #92). Those are round-9 repairs and they are all at n ≤ 113. Ignore that warning.

## THE RULE, AND IT IS THE WHOLE BRIEF

Work ONLY on those 46. Every other card on that page was looked at and left alone,
which means it is fine. Do not re-run checks over the rest of the bank, do not sweep,
do not repair anything the reviewer did not name. If a check fires on an uncommented
question, that is not your problem this round.

## WHAT THE 46 ARE

By source book: `png_shs_pt1_310526` 13, `png_act_test8_240526` 12,
`png_act_test7_240526` 10, `png_act_test5_230526` 4, `png_act_test2_230526` 3,
`year9_maths` 2, `png_act_test4_230526` 2.

`png_shs_pt1_310526` and `year9_maths` have not been through a figure round before.

Most notes are placement again, and Alaan is specific. A flavour of them:

- #122 `0f936d02` — a stray "−1" printed between the real −1 and −2 in quadrant 4
- #123 `b9928154` — an empty gap between the y value 16 and the "Days" label; enlarge
  the graph and the bars to fill it
- #124 `ccb2dfba` — "∠BAx" too far from the angle it names; move it near the origin
  without overlapping any line or value
- #126 `2a58c697` — the "Pies" y-axis label should be bigger, to fill the empty space
  left of the axis
- #127 `3c6c07ee` — "6 cm" slightly overlaps the right side of the rectangle
- #128 `33547c58` — the dots for P and Q should sit ON the transversal, not beside it

**One is marked as a note rather than a problem: #207 `7961f672`.** It reads "−2 and 3
on the y-axis and −1 and 4 on the x-axis are all being overlapped by the square's
sides." That is a real defect, so treat it as work like the rest.

## SOME WILL NOT BE FIGURE PROBLEMS

Round 9 had twelve of forty-nine that were maths or wording, not placement — four of
them a wrong key. Expect a similar rate. Handle those with more care than the rest, and
say what you did rather than fixing them silently. Changing a key or an option is not
the same as moving a label: **work the maths twice, by two different routes, before you
touch one, and confirm the answer by MEASURING the figure you shipped** — read the
coordinates back out of the SVG, do not trust the code that drew it.

## TWO THINGS ARE OFF-LIMITS

1. Questions already live in Selectly (`review_status='approved'`). The reviewer has
   passed them. Checks failing there is accepted. None of the 46 are live, so this
   should not come up — but check your query scope before any `--apply`.
2. NSW. Measured, clean, page built, round not started. Leave it.

## WHAT ROUND 9 LEARNED — READ THIS BEFORE WRITING ANY REPAIR

Ten defects were in my own tooling against twelve in the questions. Seven were caught
by the before/after check diff; three only by rendering and looking.

- **`options_distinct` is INVERTED.** It returns `True` for GOOD. Every other check in
  `question_checks.py` returns `None` for good. Special-case it, or all your questions
  look like they are failing it.
- **`fl.plane` moves a tick number to the other side of its axis** wherever a plotted
  line crosses the tick row. It reads as a stray number out of line — the exact fault
  Alaan flags, and #122 above is that same complaint. Do not regenerate a coordinate
  figure through `fl.plane` when a plotted line crosses an axis near a tick; extend the
  grid the figure already has instead.
- **Two arcs of the same radius at one vertex merge into one semicircle** and mark
  nothing. Adjacent angles need alternating radii, with the number outside its own arc.
- **A halo only counts inside `<g … aria-hidden="true">`**, and
  `text_overlaps_geometry` forgives a haloed label only over FAINT ink. A solid line
  through a label is still a finding.
- **A background `<rect fill='white'/>` is geometry.** Grow it when you grow the
  viewBox, or a label moved near the edge collides with it.
- **A rotated label's box comes from the rotate CENTRE's x**, not the text's own x. To
  slide a rotated axis title sideways, move the rotate centre.
- `tools/repair_vic_round9_figures.py` is the model to copy: one builder per question,
  a `state()` that runs every check, and a refusal to write anything that would gain a
  finding.

## HOW TO WORK

- Plain English in your summaries. Short sentences. Explain any tool or check name the
  first time you use it. Numbers at the end, not the start.
- Back up the database before the first write.
- Render every figure and LOOK at it before applying —
  `tools/figure_contact_sheet.py --db <db> --ids "a,b,c,d"`, four at a time so the
  sheet stays under the image size limit.
- Verify by reading what you actually produced, not by re-running your own intended
  code. That mistake once shipped a page with the answer key missing.
- Diff the check state before and after and require "newly firing: none". Diff ALL the
  single-question checks, not a hand-picked subset.
- Ask before doing anything outside the 46.

## WHEN YOU ARE DONE — BUILD THE PAGE BACK FOR ALAAN

Same page as last time: the original picture on the LEFT, your corrected one on the
RIGHT, the question, its four options and the marked answer underneath, and the same
buttons — "Still a problem", "Fixed", a box for what is still wrong, and Download my
comments. **Only the 46 go on it, not the 49 that are already done.**

    # take this BEFORE you change anything — it is what the left-hand picture comes
    # from, and it has to be the version Alaan reviewed
    cp run_data/db/qbank.db run_data/db/qbank.db.bak-round10-$(date +%H%M%S)

    # ...do the fixes...

    IDS=$(env -u PYTHONPATH .venv/bin/python3.11 -c "
    import json
    d=json.load(open('review/ui/figure-review-vic-mq-recheck-2026-09-01.json'))
    print(','.join(x['id'] for x in d['items'] if x['n'] > 113))")

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.figure_compare_page \
        --before run_data/db/qbank.db.bak-round10-<the timestamp you used> \
        --review review/ui/figure-review-vic-mq-recheck-2026-09-01.json \
        --scope vic-mq-round10 \
        --ids "$IDS"

That writes `review/ui/compare-vic-mq-round10.html`. Every reviewer page lives in
`review/ui/` with its scope in the filename — do not write to a name another page
already uses. Check the counts it prints: 46 cards, 46 carrying a note, and "redrawn"
should be 46 if you fixed them all.

Env: always `env -u PYTHONPATH .venv/bin/python3.11`
DB: `run_data/db/qbank.db`
Round 9's backup: `run_data/db/qbank.db.bak-round9-204047`
Round 9's page, still to send if Alaan has not seen it:
`review/ui/compare-vic-mq-round9.html`
