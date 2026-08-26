# TASK: figures that are correct, not merely tidy

> Written 2026-08-26 after a VIC review round returned twelve flags, seven of them
> figures whose plotted points and drawn lines are not where the question says they are.
> Several had already been "fixed" in an earlier round. They had not been fixed; the
> checks had been tuned until they stopped complaining.
>
> **CLOSED 2026-08-26.** All twelve are repaired and the check is built. What follows is
> the record, and §5 is the one thing this round found that is still open.

---

## 1. WHAT WENT WRONG

Twelve checks were written across four review rounds. Every one measures **figure
hygiene** — do labels overlap, is the circumference drawn twice, does the shape's
bounding box match its labels. Not one measured **figure correctness**: whether the
picture shows what the question describes. The gate was clean on all ten figures the
reviewer flagged.

A clean gate was then reported as "figures fixed". It is not the same claim, and
conflating them is the substantive error of that session.

---

## 2. THE CHECK — BUILT

**`plotted_geometry_matches_stem`** reads the coordinates out of the STEM, derives the
axis mapping from the figure's own ticks or coordinate labels, and checks that the drawn
points, lines and axes agree. Where no mapping can be derived it returns **needs a
human** rather than None: a coordinate figure nothing can verify is not a figure that
has been verified.

`plotted_points_inconsistent` was the near miss. It needs the SVG to carry `B(-2, 3)`;
in these figures the label is a bare `B` with the coordinates in the stem, so it read
nothing and returned None on all four.

`gridlines_off_the_ticks` is split out, because the figure whose grid sat 5 px left of
its own tick marks named no coordinates at all — nothing driven by the stem could reach
it.

Over the 886 figures in the bank: **46 fire** (23 needs-a-human, 15 axis-off-zero,
8 point-misplaced), plus 3 on the grid. Two false positives were found by hand-reading
and fixed — a dashed height line and a gridline taken for an axis — so the axis is now
identified by the `x`/`y` title beside it. Both checks are BLOCKING in `gate_forms`.

Two measurement faults surfaced while building it, each of which had been quietly
wrong across the whole bank:

- `_text_box` measured `text-anchor="end"` as if the label started at x, putting its box
  a full width to the RIGHT of where it draws. Every y-axis number is end-anchored, so
  both overlap checks were reading the wrong side of every axis. Net: 11 newly caught,
  18 correctly cleared.
- A tick number's y is its BASELINE, ~4 px below the tick it names, so every mapping
  derived from labels read 0.13 units low — most of a 6 px tolerance spent before the
  check began. Tick marks carry no such convention and now set the offset while the
  labels set the scale.

---

## 3. THE TWELVE — ALL CLOSED

Redrawn by `figure_lib.plane` (four-quadrant planes) and `figure_lib.right_triangle` /
`.trapezium` (shapes), which place axes, ticks, gridlines, dots, lines, dimensions and
angle arcs from ONE mapping. Repair scripts refuse to write unless every figure check
passes on the result; that guard caught three redraws before they landed.

| qbank_id | What the reviewer said | Done |
|---|---|---|
| `11125ee3` | point B is at (−2, 2); the question asks for (−2, 3) | redrawn |
| `8139103c` | lines do not pass through C(0,4) D(4,0) or E(0,−2) F(2,2) | redrawn |
| `cdbdd5ae` | the line does not pass through (0, −6) and (4, 0) | redrawn |
| `709e977c` | fix the graphs for the lines to line up with each value | redrawn |
| `25bbe5a8` | the y-axis should be within the square | redrawn |
| `e0621105` | the "5 cm" label overlaps the dotted height line | redrawn |
| `79ab50fc` | add an angle symbol on angle R | redrawn |
| `ce375557` | angle values always within the shape, arc always present | redrawn |
| `24386fc1` | dimensions outside the triangle, uniform in every shape | redrawn |
| `8a048a4d` | say "round to the nearest ..." when the answer is not exact | re-cut exact |
| `a00cb43b` | more maths than thinking | re-cut symmetric |
| `844bbdfe` | more maths than thinking | **kept — see §4** |

Three of those notes say ALWAYS. They are conventions for the bank, not requests about
one picture, and they now live in `figure_lib` rather than in a memory of this round.

Beyond what was asked, reading the figures found:

- `8139103c` carried a repair note from an earlier round inside the explanation a
  student reads — "the question is keyed to (3,1)" — which was also false. And it named
  F(2,2), which was the answer.
- `79ab50fc` drew its 7 cm side HALF AGAIN LONGER than its 24 cm one; `24386fc1` was 25%
  out of shape. Both hid behind `figure_proportions_disagree`'s triangle exemption.
- `e0621105` drew a 5 cm height taller than a 7 cm base, hiding behind the same check's
  unknown-side exemption.
- `8a048a4d`'s answer was 3.04, not 3. Rounding was the worse fix: the area becomes
  496 m², the quadratic factors, and the answer is exactly 3.

---

## 4. THE NSW TAXONOMY CALL

`numeric_deduction` is a real Thinking Skills subcategory (target 75) and the official
UCLES PT1 examples for it — q1 marbles, q7 goats and kids, q37 dog legs — are themselves
two-unknown problems. "It has two unknowns" cannot be the test. The test is whether the
numbers yield to REASONING or require algebraic manipulation.

11 of the 75 items set up two lettered unknowns. **Eight are symmetric pairs**
(2r + b = 16 with r + 2b = 17) which add to give r + b and subtract to give r − b — a
student solves them by noticing, inside the 60 seconds a question gets. **Three are not**,
and need elimination with a multiplier. `a00cb43b` is the worst of them and is the only
one of the eleven that was APPROVED, which is why it is the one a reviewer saw.

All three (`a00cb43b`, `c99bf947`, `c61a9369`) were re-cut to symmetric coefficients,
keeping every key and distractor — no rejection, so no hole in the `nsw-drill-ts` forms.

**`844bbdfe` is kept, against the reviewer's opinion.** Its stem reads algebraically —
"add up to 19 and multiply to 88" — but no quadratic is needed and none is used: the
stored explanation already reasons "pairs adding to 19 are 1 and 18, 2 and 17, and so
on. Only 8 and 11 multiply to 88." That is trial over factor pairs, exactly what PT1
numeric deduction asks for. The reviewer hedged on this one ("could potentially fit in").
**Owner should confirm.**

---

## 5. STILL OPEN — TRIANGLES DRAWN TO A DEFAULT SHAPE

Fixing the two flagged triangles exposed a class nobody has counted. A crude probe over
the 261 figures containing a polygon found **24 triangles whose two longest drawn sides
disagree with their two longest labels by more than 22%**, all in
`quantitative_reasoning`. The pattern is unmistakable: many are drawn at a ratio of
exactly 1.0 or 1.41 — isoceles, or 45-45-90 — while their labels say 2.0, 2.4, 2.6, 3.0.
The generator drew a generic right triangle and wrote the stated lengths onto it.

The probe is crude and will contain false positives (three-point arrowheads, similar-
triangle figures whose labels belong to two different triangles), so **the 24 needs
triage before it is a work item**. But two of two flagged triangles were real, and
`figure_proportions_disagree` cannot see any of them, because exempting triangles is
correct — a hypotenuse crosses the bounding box rather than setting it.

The fix for each is `figure_lib.right_triangle`, which derives its pixels from the side
lengths. The work is triage, then redraw.

---

## 6. RULES THIS ROUND ESTABLISHED

**A clean gate is not a correct figure.** Say which one you mean.

**Never exempt a figure silently.** An exemption removes the only thing looking at it.
Every one of this round's non-coordinate defects — two triangles out of shape, a
trapezium taller than it is wide — sat behind an exemption that was individually
correct. Where a check cannot judge, it returns "needs a human", and that verdict is
visible in the gate output.

**Redraw, do not patch.** Every figure patched in place last round came back. Every
figure regenerated from its stated geometry has held. Better: redraw from a helper that
derives the drawing from the stated quantities, so the picture has no way to disagree
with the words.

**Verify an edit against the question's answer.** Removing a stray "3" was defensible
from the axis alone and wrong once the key was considered.

**Render and look, every time.** Code cleared all four shapes; looking at them caught a
trapezium drawing 5 cm longer than 7 cm and a "30°" spilling through the hypotenuse —
the reviewer's own complaint, still present after the check passed.

**Make the repair script refuse to write.** Every repair here re-runs the full check set
on its own output and rolls back if anything fails. It caught three of my own redraws.
