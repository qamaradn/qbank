#!/usr/bin/env python3
"""Builds qr_vic_replacements_p1.json — 9 questions to refill the holes review left.

WHY THIS EXISTS. Rejecting or withholding a question leaves its drill form a slot short,
and a 29-slot form is not the same test as its 31-slot siblings: the timer differs and any
percentile built across forms is comparing unequal papers. Eight vic-drill-mq forms lost
nine questions between them, so nine are authored back at the same component, difficulty
and question type.

    vic-drill-mq-001   US civics, withheld            -> rate/ratio puzzle
    vic-drill-mq-002   bar chart, no consistent read  -> bar chart, medium
    vic-drill-mq-002   sin of a marked right angle    -> right-triangle ratio, medium
    vic-drill-mq-003   koala climb, no valid option   -> multi-stage sharing, hard
    vic-drill-mq-006   temperature rate, no exact opt -> constant-rate tank, medium
    vic-drill-mq-010   US civics, withheld            -> reverse percentage
    vic-drill-mq-056   US civics, withheld            -> average speed
    vic-drill-mq-066   US civics, withheld            -> remainder puzzle
    vic-drill-mq-072   US civics, withheld            -> area scale factor

EVERY KEY IS COMPUTED TWICE, by different routes, and the build fails if they disagree.
That is the ma_common contract and it is the reason the hand-authored books survive a blind
re-solve. Every distractor names the specific error a candidate makes to land on it, so no
option is filler and the three cannot cohere into a findable odd-one-out.

The two figures are drawn in currentColor with the scale stated on the axis, because the
questions they replace failed precisely there: one had gridlines its explanation read at a
different scale, the other marked a right angle at the vertex the stem then asked about.
"""
import datetime
import json
import math
import pathlib
import sys
import uuid

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/quantitative_reasoning/generated"
BOOK = "qr_vic_replacements"
NN = 1
NOW = datetime.datetime(2026, 8, 13, 9, 0, 0, tzinfo=datetime.timezone.utc).isoformat().replace("+00:00", "Z")

ITEMS = []


def Q(topic, stem, key, verify, wrong, expl, target_form, difficulty="medium",
      confidence=0.93, fig=None, fmt=str):
    """key and verify must be reached by different routes and must agree."""
    if isinstance(key, float) or isinstance(verify, float):
        ok = math.isclose(float(key), float(verify), rel_tol=1e-9, abs_tol=1e-9)
    else:
        ok = key == verify
    if not ok:
        raise AssertionError(f"{topic}: routes disagree — key={key!r} verify={verify!r}")
    if len(wrong) != 3:
        raise ValueError(f"{topic}: need exactly 3 distractors")
    opts = [fmt(key)] + [fmt(v) for v, _ in wrong]
    if len(set(opts)) != 4:
        raise AssertionError(f"{topic}: options collide: {opts}")
    ITEMS.append({
        "id": str(uuid.uuid4()),
        "subject": "quantitative_reasoning",
        "stem": stem,
        "option_a": opts[0], "option_b": opts[1], "option_c": opts[2], "option_d": opts[3],
        "correct_answer": "A",                     # the finaliser deals letters out
        "explanation": expl,
        "topic": topic,
        "difficulty": difficulty,
        "confidence": confidence,
        "source_book": BOOK,
        "source_page": NN,
        "source_page_description": f"Replacement for a withdrawn item in {target_form}",
        "passage": None,
        "figure_svg": fig,
        "review_status": "pending",
        "created_at": NOW,
        "_target_form": target_form,
        "_errors": {fmt(v): cls for v, cls in wrong},
    })


# ---------------------------------------------------------------- mq-001
Q("Rates and Ratios",
  "A tram in Melbourne takes 18 seconds to pass a person standing beside the track, and "
  "45 seconds to pass completely through a 216-metre tunnel. How long is the tram?",
  key=144, verify=8 * 45 - 216,          # route 2: speed x tunnel time, minus the tunnel
  wrong=[(216, "gives the tunnel length instead of the tram length"),
         (360, "gives the total distance covered in the 45 seconds"),
         (72, "subtracts the tram from the tunnel rather than the other way round")],
  expl="Passing the person takes 18 s, so the tram's own length is 18v. Passing through "
       "the tunnel covers the tram plus the tunnel: 18v + 216 = 45v, so 27v = 216 and "
       "v = 8 m/s. The tram is 18 × 8 = 144 metres long.",
  target_form="vic-drill-mq-001", fmt=lambda v: f"{v} metres")

# ---------------------------------------------------------------- mq-002 (bar chart)
BARS = [("Mar", 90), ("Apr", 140), ("May", 180), ("Jun", 120), ("Jul", 70)]
_x0, _y0, _h, _per = 46, 150, 120, 200.0        # 120 px spans 0..200 mm
_bars = "".join(
    f'<rect x="{_x0 + 4 + i*52}" y="{_y0 - v/_per*_h:.1f}" width="34" '
    f'height="{v/_per*_h:.1f}" fill="currentColor" fill-opacity=".18" '
    f'stroke="currentColor" stroke-opacity=".7" stroke-width="1.2"/>'
    for i, (_, v) in enumerate(BARS))
_grid = "".join(f'<path d="M{_x0} {_y0 - g/_per*_h:.1f}H300" stroke="currentColor" '
                f'stroke-opacity=".22" stroke-width="1"/>' for g in (0, 50, 100, 150, 200))
_ylab = "".join(f'<text x="{_x0-6}" y="{_y0 - g/_per*_h + 4:.1f}" font-size="10" '
                f'fill="currentColor" fill-opacity=".8" text-anchor="end">{g}</text>'
                for g in (0, 50, 100, 150, 200))
_xlab = "".join(f'<text x="{_x0 + 21 + i*52}" y="{_y0+15}" font-size="10" '
                f'fill="currentColor" fill-opacity=".8" text-anchor="middle">{m}</text>'
                for i, (m, _) in enumerate(BARS))
FIG_BAR = (f'<svg viewBox="0 0 310 180" xmlns="http://www.w3.org/2000/svg">{_grid}{_bars}'
           f'<path d="M{_x0} 30V{_y0}H300" stroke="currentColor" stroke-opacity=".85" '
           f'stroke-width="1.6" fill="none"/>{_ylab}{_xlab}'
           f'<text x="{_x0}" y="22" font-size="10" fill="currentColor" fill-opacity=".8">'
           f'Rainfall (mm)</text></svg>')

Q("Data interpretation",
  "The graph below shows the rainfall recorded at a Ballarat weather station over five "
  "months. How much more rain fell in the two wettest months combined than in the two "
  "driest months combined?",
  key=160, verify=(180 + 140) - (70 + 90),
  wrong=[(320, "adds the two wettest months and forgets to subtract"),
         (110, "takes the single wettest minus the single driest"),
         (250, "subtracts only the driest month, not both")],
  expl="Reading the bars against the 50 mm gridlines: March 90, April 140, May 180, "
       "June 120, July 70. The two wettest are May and April, 180 + 140 = 320. The two "
       "driest are July and March, 70 + 90 = 160. The difference is 320 − 160 = 160 mm.",
  target_form="vic-drill-mq-002", fig=FIG_BAR, fmt=lambda v: f"{v} mm")

# ---------------------------------------------------------------- mq-002 (trig)
# B is the RIGHT-ANGLE vertex and A is the vertex the stem asks about. Drawing those two
# the wrong way round is exactly the defect that got the question this replaces rejected:
# its square sat on the very angle the stem asked for the cosine of. Caught here by
# rendering the figure and looking at it, not by any check.
#   B(40,60) --- 12 cm --- C(160,60)
#   |  right angle at B
#   9 cm
#   |
#   A(40,150)                    AC is the hypotenuse, 15 cm
FIG_TRI = (
    '<svg viewBox="0 0 250 185" xmlns="http://www.w3.org/2000/svg">'
    '<polygon points="40,60 160,60 40,150" fill="none" stroke="currentColor" '
    'stroke-opacity=".9" stroke-width="2"/>'
    '<path d="M40 78h18v-18" fill="none" stroke="currentColor" stroke-opacity=".8" '
    'stroke-width="1.4"/>'
    '<path d="M40 126A24 24 0 0 0 61 138" fill="none" stroke="currentColor" '
    'stroke-opacity=".85" stroke-width="1.4"/>'
    '<text x="30" y="58" font-size="12" fill="currentColor">B</text>'
    '<text x="166" y="58" font-size="12" fill="currentColor">C</text>'
    '<text x="30" y="160" font-size="12" fill="currentColor">A</text>'
    '<text x="26" y="110" font-size="11" fill="currentColor" fill-opacity=".85" '
    'text-anchor="end">9 cm</text>'
    '<text x="100" y="52" font-size="11" fill="currentColor" fill-opacity=".85" '
    'text-anchor="middle">12 cm</text></svg>')

Q("Right-angled triangle ratios",
  "In the triangle below the right angle is at B, with AB = 9 cm and BC = 12 cm. What is "
  "the value of cos∠BAC?",
  key=0.6, verify=9 / math.hypot(9, 12),
  wrong=[(0.8, "gives sin∠BAC — the opposite over the hypotenuse"),
         (0.75, "gives tan∠BAC — the opposite over the adjacent"),
         (1 / 0.6, "inverts the ratio, giving hypotenuse over adjacent")],
  expl="The right angle is at B, so AC is the hypotenuse: AC = √(9² + 12²) = √225 = 15 cm. "
       "The angle asked about is at A, where AB is the adjacent side. "
       "cos∠BAC = adjacent ÷ hypotenuse = 9/15 = 3/5. The tempting 4/5 is sin∠BAC: it uses BC, the side opposite A, where the cosine needs the side beside it.",
  target_form="vic-drill-mq-002", fig=FIG_TRI,
  fmt=lambda v: {0.6: "3/5", 0.8: "4/5", 0.75: "3/4"}.get(round(v, 4), "5/3"))

# ---------------------------------------------------------------- mq-003 (hard)
Q("Problem solving",
  "Three friends share one taxi from the airport. The fare is $72 for the full 24 km and "
  "is charged evenly per kilometre. Cara gets out after 8 km and Ben after 16 km; Ana "
  "rides the whole way. They agree to split the cost of each part of the journey equally "
  "between whoever is still in the taxi. How much does Ana pay?",
  key=44, verify=72 - 20 - 8,            # route 2: total fare minus Ben's and Cara's shares
  wrong=[(24, "splits the whole fare equally three ways"),
         (36, "leaves out Ana's share of the first 8 km"),
         (20, "gives Ben's share rather than Ana's")],
  expl="At $72 for 24 km the fare is $3 per km, so each 8 km stage costs $24. "
       "First stage: three passengers, $8 each. Second stage: Ana and Ben, $12 each. "
       "Third stage: Ana alone, $24. Ana pays 8 + 12 + 24 = $44. "
       "(Ben pays 8 + 12 = $20 and Cara $8, and 44 + 20 + 8 = $72.) An even three-way split would be $24 each, but that charges Cara for 16 km she never travels.",
  target_form="vic-drill-mq-003", difficulty="hard", confidence=0.9,
  fmt=lambda v: f"${v}")

# ---------------------------------------------------------------- mq-006
Q("Rates",
  "A rainwater tank is losing water at a constant rate. At 8:00 am it holds 2400 litres, "
  "and at 11:00 am it holds 1950 litres. If the rate does not change, how much water will "
  "the tank hold at 5:00 pm on the same day?",
  key=1050, verify=1950 - 150 * 6,       # route 2: measured forward from 11 am
  wrong=[(1350, "gives the water lost rather than the water left"),
         (750, "counts 11 hours, from 8 am to 7 pm"),
         (1200, "counts 8 hours instead of 9")],
  expl="The tank loses 2400 − 1950 = 450 litres in 3 hours, which is 150 litres per hour. "
       "From 8:00 am to 5:00 pm is 9 hours, so it loses 9 × 150 = 1350 litres, leaving "
       "2400 − 1350 = 1050 litres.",
  target_form="vic-drill-mq-006", fmt=lambda v: f"{v} litres")

# ---------------------------------------------------------------- mq-010
Q("Percentages",
  "After a 15% discount, a jacket in a Geelong shop costs $102. What was its price before "
  "the discount?",
  key=120, verify=102 / 0.85,
  wrong=[(117.30, "adds 15% to the sale price instead of reversing the discount"),
         (86.70, "takes a further 15% off the sale price"),
         (136, "reverses a 25% discount rather than a 15% one")],
  expl="A 15% discount leaves 85% of the original price, so 0.85 × original = $102 and the "
       "original is 102 ÷ 0.85 = $120. Checking: 15% of 120 is 18, and 120 − 18 = 102. Adding 15% to $102 gives $117.30, which is not the same thing — the discount was 15% of the larger number.",
  target_form="vic-drill-mq-010", fmt=lambda v: f"${v:.2f}" if v % 1 else f"${int(v)}")

# ---------------------------------------------------------------- mq-056
Q("Average speed",
  "A cyclist rides 30 km from Torquay to Lorne at an average of 20 km/h, then returns "
  "along the same 30 km road at an average of 30 km/h. What is her average speed for the "
  "whole ride?",
  key=24, verify=60 / (30 / 20 + 30 / 30),
  wrong=[(25, "averages the two speeds instead of using total distance over total time"),
         (50, "adds the two speeds together"),
         (12, "divides by the total time but uses only one leg's distance")],
  expl="Out: 30 ÷ 20 = 1.5 hours. Back: 30 ÷ 30 = 1 hour. She covers 60 km in 2.5 hours, "
       "so her average speed is 60 ÷ 2.5 = 24 km/h. It is below the midpoint of 20 and 30 "
       "because she spends longer at the slower speed.",
  target_form="vic-drill-mq-056", fmt=lambda v: f"{v} km/h")

# ---------------------------------------------------------------- mq-066
Q("Number patterns",
  "A whole number leaves a remainder of 3 when it is divided by 5, and a remainder of 2 "
  "when it is divided by 4. What is the smallest such number greater than 20?",
  key=38, verify=next(n for n in range(21, 200) if n % 5 == 3 and n % 4 == 2),
  wrong=[(23, "satisfies the division by 5 but not the division by 4"),
         (22, "satisfies the division by 4 but not the division by 5"),
         (58, "is the next number after the smallest one")],
  expl="Numbers leaving remainder 3 on division by 5 are 23, 28, 33, 38, … and numbers "
       "leaving remainder 2 on division by 4 are 22, 26, 30, 34, 38, … The first value "
       "above 20 in both lists is 38: 38 = 7 × 5 + 3 and 38 = 9 × 4 + 2. 23 meets the first condition only: dividing it by 4 leaves 3, not 2.",
  target_form="vic-drill-mq-066", difficulty="hard", confidence=0.91)

# ---------------------------------------------------------------- mq-072
Q("Area and scale",
  "A rectangular photograph measuring 15 cm by 10 cm is enlarged so that its area is four "
  "times as large. How long is the longer side of the enlargement?",
  key=30, verify=15 * math.sqrt(4),
  wrong=[(60, "multiplies the side by the area factor instead of its square root"),
         (40, "applies the area factor to the shorter side"),
         (20, "doubles the shorter side rather than the longer one")],
  expl="Area scales by the square of the length factor, so an area four times as large "
       "needs every length doubled, not quadrupled. The longer side becomes 15 × 2 = 30 cm. "
       "Checking: the enlargement is 30 by 20, an area of 600 cm², and 4 × 150 = 600.",
  target_form="vic-drill-mq-072", fmt=lambda v: f"{v} cm")


# ---------------------------------------------------------------- wave 3: forms 6-10
# Two more holes. mq-007 lost a "which statement is NOT true" item where all four
# statements were true; mq-009 lost an underdetermined pentagon-angle question. Both
# replacements deliberately avoid the format that broke the originals: a plain numeric
# ask, so the double-route check can actually verify it, rather than a "which of these is
# false" frame where the key is a sentence and nothing can be recomputed.
Q("Number patterns",
  "The first four terms of a sequence are 7, 11, 15 and 19, and the pattern continues in "
  "the same way. What is the tenth term?",
  key=43, verify=7 + 9 * 4,
  wrong=[(47, "counts ten gaps after the first term instead of nine"),
         (40, "adds the nine steps of 4 to 4 rather than to 7"),
         (79, "multiplies the tenth position by 4 and adds 39")],
  expl="Each term is 4 more than the one before, so the tenth term is nine steps past the "
       "first: 7 + 9 x 4 = 43. Counting ten steps instead of nine gives 47, which is the "
       "eleventh term.",
  target_form="vic-drill-mq-007", confidence=0.93)

Q("Angles in polygons",
  "A regular hexagon and a regular octagon are placed flat on a table so that one side of "
  "each lies against the other with no gap. What is the size of the angle left over at "
  "that point, between the outer edges of the two shapes?",
  key=105, verify=360 - (6 - 2) * 180 // 6 - (8 - 2) * 180 // 8,
  wrong=[(120, "gives the hexagon's interior angle rather than what is left over"),
         (135, "gives the octagon's interior angle"),
         (255, "adds the two interior angles instead of subtracting them from 360")],
  expl="A regular hexagon has interior angles of (6-2) x 180 / 6 = 120 degrees, and a "
       "regular octagon (8-2) x 180 / 8 = 135 degrees. The angles around the meeting point "
       "must total 360, so the gap is 360 - 120 - 135 = 105 degrees. Answering 120 stops "
       "at the hexagon's own angle instead of the space beside it.",
  target_form="vic-drill-mq-009", difficulty="hard", confidence=0.91,
  fmt=lambda v: f"{v} degrees")


# ---------------------------------------------------------------- wave 4: mq-012
# mq-012 lost a square-inside-a-square area question whose stem, explanation and key gave
# three different answers. The replacement keeps the same territory -- a composite area
# inside a square -- but states every measurement once, in the stem, so there is nothing
# for a figure or an explanation to contradict.
Q("Area of composite shapes",
  "A square lawn measures 12 m on each side. A path 1 m wide is laid inside the lawn, "
  "running all the way around its edge, so the grass that remains is a smaller square in "
  "the middle. What is the area of the path?",
  key=44, verify=12 * 12 - 10 * 10,
  wrong=[(48, "multiplies the 12 m side by the 1 m width four times, double-counting the corners"),
         (100, "gives the area of the remaining grass instead of the path"),
         (23, "takes the path off one pair of sides only")],
  expl="The path is 1 m wide on every side, so it takes 1 m off each end of both "
       "dimensions: the grass left in the middle is 10 m by 10 m. The path is therefore "
       "144 - 100 = 44 square metres. Answering 48 counts four strips of 12 x 1 and "
       "double-counts the four corner squares.",
  target_form="vic-drill-mq-012", fmt=lambda v: f"{v} m²")


if __name__ == "__main__":
    GEN.mkdir(parents=True, exist_ok=True)
    path = GEN / f"{BOOK}_p{NN}.json"
    path.write_text(json.dumps(ITEMS, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(ITEMS)} replacement questions -> {path}")
    for it in ITEMS:
        print(f"   {it['_target_form']}  {it['topic']:<30} {it['difficulty']}")

# ---------------------------------------------------------------- wave 2: act_test10 p816
# Five more holes, all from the same mis-briefed reading page. Same double-route contract,
# which caught two of my own errors while writing this block: a weighted mean I had keyed
# at 29 when it is 29.67, and a percentage that produced 202.5 trees.
Q("Ratios and Proportions",
  "A native seed mix is blended in the ratio 5 parts wallaby grass to 3 parts kangaroo "
  "grass to 2 parts everlasting daisy, by mass. A Landcare group has 12 kg of kangaroo "
  "grass and plenty of the other two. What is the greatest mass of mix they can blend?",
  key=40, verify=12 / 3 * 10,
  wrong=[(24, "multiplies the kangaroo grass by the number of parts rather than scaling the mix"),
         (120, "treats the 12 kg as one part instead of three"),
         (20, "scales to the wallaby grass share rather than the whole mix")],
  expl="Kangaroo grass is 3 of the 10 parts, so 12 kg is three parts and one part is 4 kg. "
       "The whole mix is 10 parts: 10 x 4 = 40 kg. Checking, the mix is 20 kg + 12 kg + "
       "8 kg = 40 kg. Answering 120 kg treats the 12 kg as a single part.",
  target_form="vic-drill-mq-003", fmt=lambda v: f"{v:g} kg")

Q("Time and the calendar",
  "A ferry leaves Sorrento every 40 minutes, with the first sailing of the day at 6:20 am. "
  "At what time does the twelfth sailing leave?",
  key=6 * 60 + 20 + 40 * 11, verify=13 * 60 + 40,
  wrong=[(14 * 60 + 20, "counts twelve gaps after the first sailing instead of eleven"),
         (13 * 60, "counts ten gaps"),
         (12 * 60 + 20, "uses nine gaps")],
  expl="The first sailing is at 6:20, so the twelfth is ELEVEN gaps later, not twelve: "
       "11 x 40 = 440 minutes, or 7 hours 20 minutes. 6:20 am + 7 h 20 min = 1:40 pm. "
       "Using twelve gaps gives 2:20 pm, which is the thirteenth sailing.",
  target_form="vic-drill-mq-045",
  fmt=lambda m: f"{(m // 60 - 12) if m // 60 > 12 else m // 60}:{m % 60:02d} "
                f"{'pm' if m >= 720 else 'am'}")

Q("Percentages",
  "A council reports that 18% of its 4 400 street trees are eucalypts, and that a quarter "
  "of those eucalypts are more than fifty years old. How many eucalypts are more than "
  "fifty years old?",
  key=198, verify=4400 * 18 // 100 // 4,
  wrong=[(792, "gives every eucalypt rather than the older quarter"),
         (1100, "takes a quarter of all the street trees"),
         (99, "takes a quarter of the quarter")],
  expl="18% of 4 400 is 792 eucalypts, and a quarter of 792 is 198. Answering 792 stops "
       "one step early, at the number of eucalypts rather than the number of old ones.",
  target_form="vic-drill-mq-055", fmt=lambda v: f"{v:g} trees")

Q("Measurement and geometry",
  "A rainwater tank is a cylinder 1.4 metres across and 2 metres tall. Taking pi as 3.14, "
  "about how many litres does it hold when full? (1 cubic metre is 1 000 litres.)",
  key=3077, verify=round(3.14 * (1.4 / 2) ** 2 * 2 * 1000),
  wrong=[(12309, "uses the 1.4 m width as the radius instead of the diameter"),
         (8792, "computes the curved surface area, 2(pi)rh, instead of the volume"),
         (1026, "divides by three, as though the tank were a cone")],
  expl="The radius is half the width: 0.7 m. Volume = 3.14 x 0.7 x 0.7 x 2 = 3.077 cubic "
       "metres, so about 3 077 litres. Using 1.4 as the radius multiplies the answer by "
       "four, giving roughly 12 309 litres.",
  target_form="vic-drill-mq-074", fmt=lambda v: f"about {v:,} litres".replace(",", " "))

Q("Averages",
  "A swimming club met 8 times in each of the first three terms and 12 times in the "
  "fourth. Its average attendance was 24, 30 and 27 members in those first three terms, "
  "and 36 in the fourth. What was the mean attendance across every meeting of the year?",
  key=30, verify=(24 * 8 + 30 * 8 + 27 * 8 + 36 * 12) / (8 * 3 + 12),
  wrong=[(29.25, "averages the four term figures without weighting them by meetings"),
         (27, "uses only the first three terms"),
         (36, "gives the fourth term's average on its own")],
  expl="Weight each term by how often the club met. First three terms: (24 + 30 + 27) x 8 "
       "= 648 over 24 meetings. Fourth term: 36 x 12 = 432 over 12. Altogether 1 080 "
       "members across 36 meetings, so the mean is 30. Averaging 24, 30, 27 and 36 "
       "directly gives 29.25 and ignores that the fourth term had half again as many "
       "meetings.",
  target_form="vic-drill-mq-079", difficulty="hard", confidence=0.9,
  fmt=lambda v: f"{v:g} members")


if __name__ == "__main__":
    GEN.mkdir(parents=True, exist_ok=True)
    path = GEN / f"{BOOK}_p{NN}.json"
    path.write_text(json.dumps(ITEMS, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(ITEMS)} replacement questions -> {path}")
    for it in ITEMS:
        print(f"   {it['_target_form']}  {it['topic']:<30} {it['difficulty']}")
