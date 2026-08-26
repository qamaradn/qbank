# TASK: figures that are correct, not merely tidy

> Written 2026-08-26 after a VIC review round returned twelve flags, seven of them
> figures whose plotted points and drawn lines are not where the question says they are.
> Several had already been "fixed" in an earlier round. They had not been fixed; the
> checks had been tuned until they stopped complaining.

---

## 1. WHAT WENT WRONG

Twelve checks were written across four review rounds. Every one measures **figure
hygiene** — do labels overlap, is the circumference drawn twice, does the shape's
bounding box match its labels. Not one measures **figure correctness**: whether the
picture shows what the question describes.

A clean gate was then reported as "figures fixed". It is not the same claim, and
conflating them is the substantive error of that session.

Three specific failures, all the same shape:

**Exemptions removed the only thing looking.** The trapezium was exempted from
`figure_proportions_disagree` because its widest side is the unknown `b`. That reasoning
is correct and the consequence was that nothing examined it again — the reviewer's next
report was "the 5 cm overlaps with the dotted line", a real defect present throughout.
Same for the right triangle exempted because its longest label is a hypotenuse.

**Deferred work was reported as absent work.** "Fix the lines so they pass through the
designated points" appeared in the round-4 CSV and was deferred, twice, while the gate
was reported clear.

**A figure was edited by inference and never checked against its own answer.**
`11125ee3` had two y-tick labels at the same pixel, "2" and "3". The other ticks make
40 px per unit, so that pixel is 2 and the "3" was removed as a stray. The question asks
which point is at (−2, **3**) and is keyed to B — whose dot sits at y ≈ 2. Removing the
label made the axis self-consistent and left the question wrong. Nothing verified the
edit against the key.

---

## 2. THE CHECK TO BUILD

**`plotted_geometry_matches_stem`** — one check, covering the whole class.

1. **Derive the axis mapping** from the tick labels: `_axis_ticks` already returns
   (value, pixel) pairs per axis. Least-squares a linear map for each axis. If the fit
   is poor, the axis is broken — report that and stop.
2. **Read the coordinates out of the stem**: `(−3, 5)`, `points C(0, 4) and D(4, 0)`,
   `three of its vertices at (−1, 4), (3, 4), (3, 0)`. A regex over the stem, not the
   SVG — this is the half that `plotted_points_inconsistent` cannot see, and why it
   caught none of these.
3. **Check each named point has a dot within ~4 px** of where the mapping puts it.
4. **Check each named line passes through both its stated points**, same tolerance.
5. Report the worst offender with both positions in figure units, so the message says
   "B is plotted at (−2, 2) but the stem places it at (−2, 3)".

This is mechanical and it is the whole class. Seven of the twelve flags would have been
caught before the reviewer saw them.

**Do not add more hygiene checks.** There are twelve and they are calibrated. The gap is
correctness.

---

## 3. THE FIGURES TO FIX

All live in production. Fix by **redrawing from the stated geometry**, not by nudging
the existing SVG — the two figures redrawn that way this session (the KLMN parallelogram
and the 30:16 rhombus) are correct, and every patched one came back.

| qbank_id | What the reviewer says |
|---|---|
| `11125ee3` | point B is at (−2, 2); the question asks for (−2, 3) |
| `8139103c` | the two lines do not pass through C(0,4) D(4,0) or E(0,−2) F(2,2) |
| `cdbdd5ae` | the line does not pass through (0, −6) and (4, 0) |
| `709e977c` | the three plotted points do not line up with the axis values |
| `25bbe5a8` | the y-axis is outside the square; it belongs between x = −1 and x = 3 |
| `e0621105` | the "5 cm" label overlaps the dotted height line |
| `79ab50fc` | angle R needs an arc so it is obvious which angle is meant |
| `ce375557` | the angle value must sit inside the shape and its arc must not overlap |
| `24386fc1` | put dimensions outside the triangle, and be consistent across figures |
| `8a048a4d` | say "round to the nearest ..." when the answer is not exact |

Two more are content, not figures, and belong to whoever owns the Thinking Skills
taxonomy: `a00cb43b` and `844bbdfe` are simultaneous-equation and quadratic problems
sitting in `logical_reasoning`, which the reviewer reads as mathematics rather than
thinking.

---

## 4. RULES THIS ROUND ESTABLISHED

**A clean gate is not a correct figure.** Say which one you mean.

**Never exempt a figure silently.** An exemption removes the only thing looking at it.
Where a check cannot judge — an unknown dimension, a hypotenuse, a composite shape —
it should return "needs a human", and that verdict should be visible in the gate output,
not absent from it.

**Redraw, do not patch.** Every figure patched in place this session came back in the
next round. Every figure regenerated from its stated geometry has held.

**Verify an edit against the question's answer.** Removing the stray "3" was defensible
from the axis alone and wrong once the key was considered. Any figure edit must be
re-checked against what the question asks and what it is keyed to.

**Render and look, every time.** This caught three defects in this session that no check
saw, and would have caught B's position immediately.
