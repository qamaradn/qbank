#!/usr/bin/env python3
"""Builds ma_nsw_selective_p2.json — 36 more Measurement and geometry questions (§4.1).

Closes the four subcategories p1 opened and starts `scale`:
perimeter/area/volume 10 (22 done), angle properties 8 (16 done), units and conversions 6
(14 done), time and timetables 6 (14 done), scale 6.

After this batch Measurement and geometry stands at 72/108, with nets and cross-sections,
coordinates and spatial visualisation still to build — all three figure categories.

Years 5-6 content, Year 6 sitting, no calculator. Keys computed and cross-checked; see
tools/ma/ma_common.py.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.figure_lib import ortho, svg, table  # noqa: E402
from tools.ma.ma_common import (  # noqa: E402
    Batch, PLAIN, angle_rays, deg, shoelace, triangle_fig, unit,
)

B = Batch(nn=2)
M, M2, CM, KM, L, KG = unit("m"), unit("m²"), unit("cm"), unit("km"), unit("L"), unit("kg")

# ===================================================== perimeter, area and volume (10)

# --- 1. Staircase shape, perimeter.
mv = [(12, 0), (0, 3), (-4, 0), (0, 3), (-3, 0), (0, 2), (-5, 0), (0, -8)]
body, per, area = ortho(mv, "m", 20)
B.Q("perimeter_area_volume", "geometry_measurement",
    "The diagram shows a terraced seating area at a sports ground. What is the distance "
    "right around its edge?",
    key=per, verify=2 * (12 + 8),        # the steps push out into the bounding rectangle
    wrong=[(area, "wrong_attribute"), (12 + 4 + 3 + 5, "partial_step"), (12 + 8, "formula_slip")],
    expl="Walk all eight sides: 12 + 3 + 4 + 3 + 3 + 2 + 5 + 8 = 40 m. Sliding the steps "
         "outwards gives a 12 m by 8 m rectangle with exactly the same edge, and "
         "2 x (12 + 8) = 40. 70 is the area of the seating, not the distance around it, "
         "and 20 is 12 + 8 with the doubling left out.",
    fig=svg(body), fmt=M),

# --- 2. L-shaped shade sail, area.
mv = [(7, 0), (0, 6), (-3, 0), (0, -2), (-4, 0), (0, -4)]
body, per2, area2 = ortho(mv, "m", 26)
B.Q("perimeter_area_volume", "geometry_measurement",
    "A shade sail is to be cut to the shape in the diagram. How much sailcloth does it use?",
    key=area2, verify=7 * 4 + 3 * 2,       # the narrow part spans x=4..7, so it is 3 wide
    wrong=[(7 * 6, "ignored_constraint"), (per2, "wrong_attribute"), (7 * 4, "partial_step")],
    expl="Cut it into two rectangles: 7 m by 4 m = 28 m² and 3 m by 2 m = 6 m², giving "
         "34 m². 42 is the whole 7 m by 6 m rectangle the sail is cut from, which counts "
         "the corner that was cut away, and 26 is the length of the edge right around it.",
    fig=svg(body), fmt=M2),

# --- 3. Compost bay volume.
lc, wc, hc = 2, 1, 1.5
B.Q("perimeter_area_volume", "multi_step",
    "A compost bay at a community garden is 2 m long, 1 m wide and 1.5 m high. What "
    "volume of compost does it hold when filled to the top?",
    key=lc * wc * hc, verify=(200 * 100 * 150) / 1_000_000,
    wrong=[(lc + wc + hc, "operation_swap"), (lc * wc, "wrong_attribute"),
           (lc * wc * hc * 1000, "place_value")],
    expl="Multiply the three measurements: 2 x 1 x 1.5 = 3 m³. 4.5 adds them instead, and "
         "2 is the area of the floor of the bay rather than the space above it.",
    fmt=unit("m³")),

# --- 4. Right-triangular garden.
bt, ht = 9, 4
B.Q("perimeter_area_volume", "geometry_measurement",
    "A right-angled triangular garden has its two shorter sides measuring 9 m and 4 m. "
    "What is its area?",
    key=bt * ht / 2, verify=shoelace([(0, 0), (bt, 0), (0, ht)]),   # vertices, not a formula
    wrong=[(bt * ht, "formula_slip"), (bt + ht, "operation_swap"), (bt, "partial_step")],
    expl="A right-angled triangle is half of the rectangle on its two shorter sides: "
         "9 x 4 = 36, and half of that is 18 m². 36 is that whole rectangle, forgetting to "
         "halve it, and 13 adds 9 and 4 rather than multiplying them.",
    fmt=M2),

# --- 5. Find a missing side from the area.
af, lf = 3600, 90
B.Q("perimeter_area_volume", "single_step",
    "A rectangular sports field covers 3600 m² and is 90 m long. How wide is it?",
    key=af // lf, verify=af / lf,
    wrong=[(af - lf, "operation_swap"), (af // lf // 2, "formula_slip"),
           (af // lf * 10, "place_value")],
    expl="Width is area divided by length: 3600 / 90 = 40 m. Check it: 90 x 40 = 3600. "
         "3510 subtracts 90 from 3600 instead of dividing, and 20 halves the width for no "
         "reason the question gives.",
    fmt=M),

# --- 6. Paint coverage over two walls.
wl, wh, cover = 4, 2.5, 8
B.Q("perimeter_area_volume", "multi_step",
    "Two walls each measure 4 m long and 2.5 m high. One litre of paint covers 8 m². How "
    "much paint is needed to give both walls one coat?",
    key=2 * wl * wh / cover, verify=((wl + wl) * wh) / cover,   # the two walls end to end
    wrong=[(wl * wh, "partial_step"), (2 * wl * wh * cover, "operation_swap"),
           (cover / (2 * wl * wh), "inverse")],
    difficulty="hard", confidence=0.91,
    expl="Each wall is 4 x 2.5 = 10 m², so the two come to 20 m², and 20 / 8 = 2.5 L. "
         "10 is the area of one wall in square metres rather than an amount of paint, and "
         "160 multiplies by the coverage instead of dividing by it.",
    fmt=L),

# --- 7. Fish tank capacity.
lk, wk, hk = 80, 35, 40
B.Q("perimeter_area_volume", "multi_step",
    "A fish tank measures 80 cm by 35 cm by 40 cm. One litre is 1000 cm³. How much water "
    "does the tank hold when full?",
    key=lk * wk * hk / 1000, verify=0.8 * 0.35 * 0.4 * 1000,   # in metres, then to litres
    wrong=[(lk * wk * hk, "partial_step"), (lk + wk + hk, "operation_swap"),
           (lk * wk, "wrong_attribute")],
    difficulty="hard", confidence=0.91,
    expl="The tank holds 80 x 35 x 40 = 112 000 cm³, and 1000 cm³ make a litre, so it "
         "holds 112 L. 112000 is the volume in cubic centimetres with a litre label on it, "
         "and 2800 is the area of the base of the tank.",
    fmt=L),

# --- 8. Wall with a window in it.
ww, wht, gw, gh = 6, 3, 2, 1.5
B.Q("perimeter_area_volume", "multi_step",
    "A wall is 6 m long and 3 m high. A window measuring 2 m by 1.5 m is set into it. What "
    "area of the wall is left to be painted?",
    key=ww * wht - gw * gh,
    verify=2 * 3 + 2 * 3 + (gw * wht - gw * gh),   # left strip, right strip, above and below
    wrong=[(ww * wht, "ignored_constraint"), (gw * gh, "partial_step"),
           (ww * wht + gw * gh, "operation_swap")],
    expl="The whole wall is 6 x 3 = 18 m² and the window takes 2 x 1.5 = 3 m² of it, so "
         "15 m² is left. Counting round the window gives the same: 6 + 6 either side, plus "
         "3 above and below it. 18 forgets the window is there at all, and 21 adds the "
         "window instead of taking it away.",
    fmt=M2),

# --- 9. Doubling a side.
sq = 4
B.Q("perimeter_area_volume", "multi_step",
    "A square vegetable patch has sides of 4 m. A gardener doubles the length of every "
    "side. How many times bigger is the new area?",
    key=f"{(2 * sq) ** 2 // sq ** 2} times", verify="4 times",   # 64 m² against 16 m²
    wrong=[("2 times", "formula_slip"), ("8 times", "operation_swap"),
           ("3 times", "misread_data")],
    difficulty="hard", confidence=0.90,
    expl="The old patch is 4 x 4 = 16 m² and the new one is 8 x 8 = 64 m², and 64 / 16 = 4, "
         "so it is 4 times bigger. 2 times is what most people expect, because the sides "
         "doubled — but both the length and the width doubled, so the area doubles twice.",
    fmt=PLAIN),

# --- 10. Pavers over a courtyard.
cl, cw, pav = 4, 3, 0.5
B.Q("perimeter_area_volume", "multi_step",
    "A courtyard measures 4 m by 3 m. It is to be covered with square pavers measuring "
    "50 cm by 50 cm. How many pavers are needed?",
    key=int((cl / pav) * (cw / pav)),                    # 8 along by 6 across
    verify=int((cl * cw) / (pav * pav)),                 # total area over paver area
    wrong=[(cl * cw, "partial_step"), (int(cl * cw / pav), "formula_slip"),
           (int(cl / pav + cw / pav), "operation_swap")],
    difficulty="hard", confidence=0.91,
    expl="Two pavers fit in every metre, so 8 fit along the courtyard and 6 across it: "
         "8 x 6 = 48 pavers. The areas agree, 12 m² / 0.25 m² = 48. 12 is the area of the "
         "courtyard in square metres, and 24 treats each paver as covering half a square "
         "metre when it covers a quarter.",
    fmt=unit("pavers")),

# ===================================================== angle properties (8)

# --- 11. Three angles on a straight line.
g1, g2 = 42, 65
B.Q("angle_properties", "geometry_measurement",
    "Three angles sit together on a straight line, as shown. What is the size of angle p?",
    key=180 - g1 - g2, verify=180 - (g1 + g2),
    wrong=[(g1 + g2, "partial_step"), (360 - (180 - g1 - g2), "wrong_attribute"),
           (360 - g1 - g2, "operation_swap")],
    expl="Angles on a straight line add to 180°, so p = 180 - 42 - 65 = 73°. 107 is the "
         "two given angles added together and left there, and 253 subtracts them from 360 "
         "as though they went all the way round the point.",
    fig=angle_rays([g1, g2, 180 - g1 - g2], [f"{g1}°", f"{g2}°", "p"]), fmt=deg),

# --- 12. Complementary angles.
comp = 27
B.Q("angle_properties", "single_step",
    "A right angle is divided into two parts by a single line. One part measures 27°. What "
    "is the size of the other part?",
    key=90 - comp, verify=90 - 27,
    wrong=[(180 - comp, "formula_slip"), (360 - comp, "operation_swap"), (comp, "partial_step")],
    expl="A right angle is 90°, so the other part is 90 - 27 = 63°. 153 subtracts from 180, "
         "which is the angle on a straight line rather than in a corner, and 27 simply "
         "repeats the part that was given.",
    fmt=deg),

# --- 13. Right-angled triangle.
ac = 38
B.Q("angle_properties", "geometry_measurement",
    "In a right-angled triangle, one of the two smaller angles measures 38°. What is the "
    "size of the third angle?",
    key=180 - 90 - ac, verify=90 - ac,      # the two smaller angles share the other 90°
    wrong=[(180 - ac, "formula_slip"), (90 + ac, "operation_swap"), (ac, "misread_data")],
    expl="The right angle uses 90° of the triangle's 180°, so the other two share what is "
         "left: 90 - 38 = 52°. 142 subtracts 38 from 180 and forgets the right angle "
         "entirely, and 128 adds 38 to the right angle instead of taking it off.",
    fmt=deg),

# --- 14. Four angles at a point.
f1, f2, f3 = 85, 74, 110
B.Q("angle_properties", "geometry_measurement",
    "The diagram shows four angles meeting at a point. How big is angle q?",
    key=360 - f1 - f2 - f3, verify=360 - (f1 + f2 + f3),
    wrong=[(f1 + f2 + f3, "partial_step"), (360 - f1 - f2 - 100, "misread_data"),
           (180 - (360 - f1 - f2 - f3), "wrong_attribute")],
    difficulty="hard", confidence=0.91,
    expl="Angles at a point add to 360°, so q = 360 - 85 - 74 - 110 = 91°. 269 is the three "
         "given angles added together, and 101 comes from reading the largest angle as 100 "
         "rather than 110.",
    fig=angle_rays([f1, f2, f3, 360 - f1 - f2 - f3],
                   [f"{f1}°", f"{f2}°", f"{f3}°", "q"], full=True), fmt=deg),

# --- 15. Half an equilateral triangle.
B.Q("angle_properties", "multi_step",
    "An equilateral triangle is folded exactly in half along a line of symmetry, making "
    "two smaller triangles. What is the smallest angle in one of those smaller triangles?",
    key=60 // 2, verify=180 - 90 - 60,      # the fold makes a right angle at the base
    wrong=[(60, "partial_step"), (90, "wrong_attribute"), (45, "misread_data")],
    difficulty="hard", confidence=0.90,
    expl="Every angle of an equilateral triangle is 60°, and the fold cuts one of them in "
         "half, giving 30°. The other two angles of the small triangle are 60° and the 90° "
         "the fold makes, and 180 - 90 - 60 = 30 as well. 45 would be right for a folded "
         "square, not a folded equilateral triangle.",
    fmt=deg),

# --- 16. Minute hand.
mins = 25
B.Q("angle_properties", "multi_step",
    "The minute hand of a clock starts at 12 and moves for 25 minutes. Through how many "
    "degrees does it turn?",
    key=360 * mins // 60, verify=6 * mins,     # the hand moves 6° every minute
    wrong=[(mins, "partial_step"), (90, "misread_data"), (360 * mins // 30, "operation_swap")],
    difficulty="hard", confidence=0.90,
    expl="A full turn of 360° takes 60 minutes, so the hand moves 6° each minute and "
         "25 x 6 = 150°. 90 is a quarter turn, which would be 15 minutes rather than 25, "
         "and 25 gives the minutes back instead of the angle.",
    fmt=deg),

# --- 17. Two turns, one each way.
B.Q("angle_properties", "multi_step",
    "A yacht is sailing north. It turns 90° to the right, then turns 45° to the left. In "
    "which direction is it sailing now?",
    key="north-east", verify="north-east",
    wrong=[("east", "partial_step"), ("north-west", "inverse"), ("south-east", "operation_swap")],
    expl="Turning 90° right from north points east, and turning 45° back to the left "
         "leaves it halfway between north and east, which is north-east. East is where it "
         "points after the first turn only, and south-east adds the two turns together "
         "instead of taking one off the other.",
    fmt=PLAIN),

# --- 18. One angle twice the other.
B.Q("angle_properties", "multi_step",
    "Two angles sit together on a straight line. One of them is exactly twice the size of "
    "the other. What is the size of the larger angle?",
    key=180 * 2 // 3, verify=180 - 60,        # the smaller is 60, so the larger is the rest
    wrong=[(180 // 3, "partial_step"), (180 // 2, "formula_slip"), (360 * 2 // 3, "operation_swap")],
    difficulty="hard", confidence=0.90,
    expl="Think of the line as three equal shares: one for the smaller angle and two for "
         "the larger. Each share is 180 / 3 = 60°, so the larger angle is 120°. 60 is the "
         "smaller of the two, and 90 splits the line evenly, which would make the angles "
         "the same rather than one twice the other.",
    fmt=deg),

# ===================================================== units and conversions (6)

# --- 19. Long jump totals.
j1, j2, j3 = 285, 310, 295
B.Q("units_conversion", "multi_step",
    "In three long jumps a student records 285 cm, 310 cm and 295 cm. What is the total "
    "distance jumped, in metres?",
    key=(j1 + j2 + j3) / 100, verify=j1 / 100 + j2 / 100 + j3 / 100,
    wrong=[(j1 + j2 + j3, "partial_step"), ((j1 + j2 + j3) / 10, "place_value"),
           ((j1 + j2) / 100, "misread_data")],
    expl="The three jumps come to 285 + 310 + 295 = 890 cm, and 100 cm make a metre, so "
         "8.9 m. 890 is the total left in centimetres, and 5.95 adds the 285 cm and "
         "310 cm jumps and stops there.",
    fmt=M),

# --- 20. Bottle into cups.
bot, cup = 1.25, 250
B.Q("units_conversion", "multi_step",
    "A 1.25 L bottle of juice is poured into cups holding 250 mL each. How many cups does "
    "it fill?",
    key=int(bot * 1000 / cup), verify=1250 // 250,
    wrong=[(int(bot * 1000 / cup) - 1, "off_by_one"), (int(bot * 1000 / cup) * 10, "place_value"),
           (int(bot * 1000 / cup) + 1, "rounding")],
    expl="The bottle holds 1.25 x 1000 = 1250 mL, and 1250 / 250 = 5 cups exactly. 4 leaves "
         "one cup's worth still in the bottle, and 6 rounds up when the division came out "
         "exact and there is nothing left over to pour.",
    fmt=unit("cups")),

# --- 21. Flour into portions.
flr, port = 1.5, 250
B.Q("units_conversion", "multi_step",
    "A baker has 1.5 kg of flour and measures it into portions of 250 g. How many portions "
    "does she get?",
    key=int(flr * 1000 / port), verify=1500 // 250,
    wrong=[(int(flr * 1000 / port) * 10, "place_value"), (int(flr * 1000 / port) - 1, "off_by_one"),
           (int(flr * port), "operation_swap")],
    expl="1.5 kg is 1500 g, and 1500 / 250 = 6 portions. 60 slips a place when converting "
         "the kilograms, and 375 multiplies 1.5 by 250 instead of dividing.",
    fmt=unit("portions")),

# --- 22. Laps of a track.
lap, nlaps = 0.8, 5
B.Q("units_conversion", "multi_step",
    "A running track is 0.8 km around. A runner completes 5 laps. How far has she run, in "
    "metres?",
    key=lap * nlaps * 1000, verify=800 * nlaps,
    wrong=[(lap * nlaps * 100, "place_value"), (lap * nlaps, "partial_step"),
           ((lap + nlaps) * 1000, "operation_swap")],
    expl="One lap is 0.8 km = 800 m, so 5 laps are 5 x 800 = 4000 m. 4 is the distance in "
         "kilometres rather than metres, and 5800 adds 0.8 and 5 before converting instead "
         "of multiplying them.",
    fmt=M),

# --- 23. Fence panels.
pan, npan = 1800, 12
B.Q("units_conversion", "multi_step",
    "Fence panels are each 1800 mm wide. Twelve panels are joined in a straight line. How "
    "long is the fence, in metres?",
    key=pan * npan / 1000, verify=1.8 * npan,
    wrong=[(pan * npan, "partial_step"), (pan * npan / 100, "place_value"),
           ((pan / 1000) + npan, "operation_swap")],
    expl="Each panel is 1800 mm = 1.8 m, so twelve of them make 12 x 1.8 = 21.6 m. 21600 is "
         "the length still in millimetres, and 13.8 adds 1.8 and 12 rather than "
         "multiplying.",
    fmt=M),

# --- 24. Cans into litres.
can, ncan = 375, 6
B.Q("units_conversion", "single_step",
    "A pack holds 6 cans of 375 mL each. How many litres of drink is that altogether?",
    key=can * ncan / 1000, verify=0.375 * ncan,
    wrong=[(can * ncan, "partial_step"), (can * ncan / 100, "place_value"),
           (can * 4 / 1000, "misread_data")],
    expl="Six cans hold 6 x 375 = 2250 mL, which is 2.25 L. 2250 is the amount in "
         "millilitres with a litre label on it, and 1.5 counts only four of the six cans.",
    fmt=L),

# ===================================================== time and timetables (6)

BUS = table([["Route", "School", "Library", "Pool", "Station"],
             ["1", "3:25 pm", "3:38 pm", "3:47 pm", "4:04 pm"],
             ["2", "3:55 pm", "4:08 pm", "4:17 pm", "4:34 pm"],
             ["3", "4:40 pm", "4:55 pm", "5:06 pm", "5:26 pm"]])

# --- 25. Whole journey.
B.Q("time_timetables", "data_interpretation",
    "The timetable shows three afternoon bus routes. How long does route 1 take to get "
    "from the School to the Station?",
    key="39 minutes", verify="39 minutes",       # 3:25 -> 4:00 is 35, then 4 more
    wrong=[("79 minutes", "operation_swap"), ("29 minutes", "misread_data"),
           ("99 minutes", "off_by_one")],
    expl="Route 1 leaves the School at 3:25 pm and reaches the Station at 4:04 pm: 35 "
         "minutes to 4:00 and 4 more, which is 39 minutes. 79 minutes comes from taking "
         "4.04 - 3.25 as if the clock counted in hundredths.",
    fig=BUS, fmt=PLAIN),

# --- 26. Gap at an intermediate stop.
B.Q("time_timetables", "data_interpretation",
    "Using the timetable, how long is the wait at the Library between the route 2 bus and "
    "the route 3 bus?",
    key="47 minutes", verify="47 minutes",       # 4:08 -> 4:55
    wrong=[("87 minutes", "operation_swap"), ("37 minutes", "misread_data"),
           ("107 minutes", "off_by_one")],
    expl="Route 2 calls at the Library at 4:08 pm and route 3 at 4:55 pm, which is 47 "
         "minutes apart. 87 minutes subtracts the times as decimals, 4.55 - 4.08, which "
         "the clock does not work like, and 107 minutes counts a whole extra hour into "
         "the wait.",
    fig=BUS, fmt=PLAIN),

# --- 27. Catching the next bus.
B.Q("time_timetables", "data_interpretation",
    "A student leaves the Library at 4:15 pm and wants to travel to the Station by bus. "
    "Which is the first bus she can catch, and when will she arrive?",
    key="Route 3, arriving 5:26 pm", verify="Route 3, arriving 5:26 pm",
    wrong=[("Route 2, arriving 4:34 pm", "ignored_constraint"),
           ("Route 3, arriving 5:06 pm", "misread_data"),
           ("Route 3, arriving 4:55 pm", "partial_step")],
    difficulty="hard", confidence=0.91,
    expl="The route 2 bus has already left the Library at 4:08 pm, so the first she can "
         "catch is route 3 at 4:55 pm, reaching the Station at 5:26 pm. Route 3, arriving "
         "5:06 pm reads across to the Pool column instead of the Station, and Route 3, "
         "arriving 4:55 pm gives the time the bus leaves the Library rather than the time "
         "it gets to the Station.",
    fig=BUS, fmt=PLAIN),

# --- 28. Comparing two journeys.
B.Q("time_timetables", "data_interpretation",
    "Using the timetable, how much longer does the route 3 journey from the School to the "
    "Station take than the route 1 journey?",
    key="7 minutes", verify="7 minutes",         # 46 minutes against 39
    wrong=[("46 minutes", "partial_step"), ("82 minutes", "misread_data"),
           ("47 minutes", "operation_swap")],
    difficulty="hard", confidence=0.90,
    expl="Route 1 takes 39 minutes and route 3 runs 4:40 pm to 5:26 pm, which is 46 "
         "minutes, so route 3 takes 7 minutes longer. 46 minutes is route 3's journey on "
         "its own rather than the difference, and 82 minutes compares the two arrival "
         "times, 5:26 pm against 4:04 pm, when the buses did not set out together.",
    fig=BUS, fmt=PLAIN),

# --- 29. 24-hour clock with a long journey.
B.Q("time_timetables", "multi_step",
    "A train departs at 16:48 and the journey takes 1 hour and 37 minutes. At what time "
    "does it arrive, on a 24-hour clock?",
    key="18:25", verify="18:25",                 # 16:48 + 1 h = 17:48, + 12 = 18:00, + 25
    wrong=[("17:85", "operation_swap"), ("15:11", "inverse"), ("19:25", "off_by_one")],
    expl="An hour on from 16:48 is 17:48, then 12 minutes reaches 18:00 and the remaining "
         "25 minutes reaches 18:25. 17:85 adds 48 and 37 to make 85 minutes without "
         "turning 60 of them into an hour, and 15:11 subtracts the journey instead of "
         "adding it.",
    fmt=PLAIN),

# --- 30. Working backwards through two legs.
B.Q("time_timetables", "multi_step",
    "A swimmer needs to be at the pool by 4:20 pm. The bus trip takes 22 minutes and it "
    "takes 8 minutes to walk to the bus stop. What is the latest time she can set off?",
    key="3:50 pm", verify="3:50 pm",             # 22 + 8 = 30 minutes before 4:20
    wrong=[("3:58 pm", "partial_step"), ("4:50 pm", "inverse"), ("3:30 pm", "misread_data")],
    expl="The walk and the bus take 8 + 22 = 30 minutes together, and 30 minutes before "
         "4:20 pm is 3:50 pm. 3:58 pm allows for the bus but not the walk to the stop, and "
         "4:50 pm adds the half hour to the deadline instead of taking it off.",
    fmt=PLAIN),

# ===================================================== scale (6)

# --- 31. Map distance to real distance.
sc, mapcm = 5, 7
B.Q("scale", "single_step",
    "On a map, 1 cm represents 5 km. Two towns are 7 cm apart on the map. How far apart "
    "are they in real life?",
    key=sc * mapcm, verify=sum([sc] * mapcm),
    wrong=[(sc + mapcm, "operation_swap"), (mapcm / sc, "inverse"), (sc * mapcm * 10, "place_value")],
    expl="Each centimetre stands for 5 km, so 7 cm stands for 7 x 5 = 35 km. 12 adds 7 and "
         "5 instead of multiplying them, and 1.4 divides the wrong way round, which would "
         "make the real distance shorter than the map.",
    fmt=KM),

# --- 32. Real length to plan length.
plsc, room = 2, 4.5
B.Q("scale", "single_step",
    "A plan is drawn so that 1 cm represents 2 m. A room is 4.5 m long. How long is the "
    "room on the plan?",
    key=room / plsc, verify=4.5 / 2,
    wrong=[(room * plsc, "operation_swap"), (room * plsc / 10, "place_value"),
           (room, "partial_step")],
    expl="Every 2 m of the room takes 1 cm on the plan, so 4.5 / 2 = 2.25 cm. 9 multiplies "
         "by the scale instead of dividing, which would make the drawing bigger than the "
         "room, and 4.5 leaves the length unchanged.",
    fmt=CM),

# --- 33. Model scale as a ratio.
mod, ratio = 9, 50
B.Q("scale", "multi_step",
    "A model car is built to a scale of 1 : 50. The model is 9 cm long. How long is the "
    "real car?",
    key=mod * ratio / 100, verify=(mod / 100) * ratio,
    wrong=[(mod * ratio, "partial_step"), (mod / ratio, "inverse"), (mod * ratio / 10, "place_value")],
    difficulty="hard", confidence=0.91,
    expl="The real car is 50 times the model: 9 x 50 = 450 cm, and 100 cm make a metre, so "
         "4.5 m. 450 is the length still in centimetres, and 0.18 divides by 50 rather than "
         "multiplying, which would make the real car smaller than the model.",
    fmt=M),

# --- 34. Map centimetres to kilometres.
msc, tr = 250, 6
B.Q("scale", "multi_step",
    "On a walking map, 1 cm represents 250 m. A track measures 6 cm on the map. How long "
    "is the track in kilometres?",
    key=msc * tr / 1000, verify=(msc / 1000) * tr,
    wrong=[(msc * tr, "partial_step"), (msc * tr / 100, "place_value"),
           (msc + tr, "operation_swap")],
    difficulty="hard", confidence=0.91,
    expl="Six centimetres stand for 6 x 250 = 1500 m, and 1000 m make a kilometre, so the "
         "track is 1.5 km. 1500 is the length in metres rather than kilometres, and 256 "
         "adds 250 and 6 instead of multiplying them.",
    fmt=KM),

# --- 35. Both dimensions of a hall.
hsc, ha, hb = 3, 8, 5
B.Q("scale", "multi_step",
    "A hall is drawn on a plan at a scale of 1 cm to 3 m. On the plan it measures 8 cm by "
    "5 cm. What are the real measurements of the hall?",
    key=f"{hsc * ha} m by {hsc * hb} m", verify="24 m by 15 m",
    wrong=[(f"{hsc + ha} m by {hsc + hb} m", "operation_swap"),
           (f"{ha} m by {hb} m", "partial_step"),
           (f"{hsc * ha * 10} m by {hsc * hb * 10} m", "place_value")],
    expl="Multiply both plan measurements by 3: 8 x 3 = 24 m and 5 x 3 = 15 m. 11 m by 8 m "
         "adds the scale to each measurement instead of multiplying, and 8 m by 5 m reads "
         "the plan measurements straight off without using the scale at all.",
    fmt=PLAIN),

# --- 36. Real to plan, in reverse.
fsc, fence = 4, 18
B.Q("scale", "multi_step",
    "A fence is 18 m long. It is to be drawn on a plan where 1 cm represents 4 m. How long "
    "should the fence be on the plan?",
    key=fence / fsc, verify=18 / 4,
    wrong=[(fence * fsc, "operation_swap"), (fence / fsc / 10, "place_value"),
           (fence, "partial_step")],
    expl="Each 4 m of fence takes 1 cm, so 18 / 4 = 4.5 cm. 72 multiplies by the scale "
         "rather than dividing, which would draw a fence longer than the paper, and 18 "
         "copies the real length onto the plan unchanged.",
    fmt=CM),

if __name__ == "__main__":
    B.write()
