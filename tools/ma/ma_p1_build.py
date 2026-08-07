#!/usr/bin/env python3
"""Builds ma_nsw_selective_p1.json — 36 Measurement and geometry questions (§4.1).

First batch of the NSW Mathematical Reasoning build (307 questions). Measurement and
geometry is the largest area gap: 102 held against a 210 target.

Split: perimeter/area/volume 12, angle properties 8, units and conversions 8,
time and timetables 8.

Years 5-6 content, Year 6 sitting, no calculator anywhere. Every key is computed and
cross-checked against a second route — see tools/ma/ma_common.py for why.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.figure_lib import ortho, svg, table  # noqa: E402
from tools.ma.ma_common import (  # noqa: E402
    Batch, PLAIN, angle_rays, deg, money, triangle_fig, unit,
)

B = Batch(nn=1)
M, M2, CM, KM, L, KG, T = unit("m"), unit("m²"), unit("cm"), unit("km"), unit("L"), unit("kg"), unit("t")

# ===================================================== perimeter, area and volume (12)

# --- 1. L-shaped courtyard, perimeter. The figure and the answer come from one list of
#        moves, so a label cannot disagree with the side it names.
moves = [(9, 0), (0, 4), (-4, 0), (0, 3), (-5, 0), (0, -7)]
body, per, area = ortho(moves, "m", 20)
B.Q("perimeter_area_volume", "geometry_measurement",
    "The diagram shows a paved courtyard at a school in Ballarat. What is the perimeter "
    "of the courtyard?",
    key=per, verify=2 * (9 + 7),          # an L-shape's perimeter is its bounding rectangle's
    wrong=[(area, "wrong_attribute"), (9 + 4 + 5 + 7, "partial_step"), (9 + 7, "formula_slip")],
    expl="Add all six sides: 9 + 4 + 4 + 3 + 5 + 7 = 32 m. A quicker check is that pushing "
         "the step out gives a 9 m by 7 m rectangle with the same perimeter, and "
         "2 x (9 + 7) = 32. 51 is the area of the courtyard, not the distance around it, "
         "and 16 is 9 + 7 without doubling.",
    fig=svg(body), fmt=M),

# --- 2. T-shaped bed, area.
moves = [(8, 0), (0, 3), (-2, 0), (0, 4), (-4, 0), (0, -4), (-2, 0), (0, -3)]
body, per2, area2 = ortho(moves, "m", 20)
B.Q("perimeter_area_volume", "geometry_measurement",
    "The diagram shows a vegetable bed at a community garden in Geelong. What is its area?",
    key=area2, verify=8 * 3 + 4 * 4,      # cut it into the bar and the stem
    wrong=[(8 * 7, "ignored_constraint"), (per2, "wrong_attribute"), (8 * 3, "partial_step")],
    expl="Cut the shape into two rectangles: the bar is 8 m by 3 m = 24 m² and the stem "
         "is 4 m by 4 m = 16 m², so the bed is 40 m². 56 is the whole 8 m by 7 m rectangle "
         "the shape sits inside, which counts ground that is not part of the bed, and 24 "
         "is the bar on its own.",
    fig=svg(body), fmt=M2),

# --- 3. Pool volume in kilolitres.
lp, wp, dp = 8, 4, 1.5
B.Q("perimeter_area_volume", "multi_step",
    "A rectangular swimming pool at a Newcastle school is 8 m long, 4 m wide and 1.5 m "
    "deep. One cubic metre of water is one kilolitre. How much water does the pool hold "
    "when it is full?",
    key=lp * wp * dp, verify=(800 * 400 * 150) / 1_000_000,   # in cm³, then to m³
    wrong=[(lp + wp + dp, "operation_swap"), (lp * wp, "wrong_attribute"),
           (lp * wp * dp * 1000, "place_value")],
    expl="Volume is length x width x depth: 8 x 4 x 1.5 = 48 m³, which is 48 kL. 13.5 adds "
         "the three measurements instead of multiplying them, and 32 is the area of the "
         "water surface rather than the volume beneath it.",
    fmt=unit("kL")),

# --- 4. Two triangular sails.
bs, hs = 6, 5
B.Q("perimeter_area_volume", "multi_step",
    "A sailing club orders two identical triangular sails. Each sail has a base of 6 m and "
    "a perpendicular height of 5 m. What area of sailcloth is needed altogether?",
    key=2 * (bs * hs / 2), verify=bs * hs,        # two halves make one whole rectangle
    wrong=[(bs * hs / 2, "partial_step"), (2 * bs * hs, "formula_slip"),
           ((bs + hs) * 2, "operation_swap")],
    expl="One sail is half of 6 x 5, which is 15 m², so two sails need 30 m². Neatly, two "
         "of these triangles make exactly one 6 m by 5 m rectangle. 15 is one sail only, "
         "and 60 forgets to halve the rectangle for each triangle.",
    fmt=M2),

# --- 5. Path around a garden.
lg, wg, pw = 12, 8, 1
B.Q("perimeter_area_volume", "multi_step",
    "A rectangular garden bed in Toowoomba measures 12 m by 8 m. A concrete path 1 m wide "
    "is laid all the way around the outside of it. What is the area of the path?",
    key=(lg + 2 * pw) * (wg + 2 * pw) - lg * wg,
    verify=2 * (lg * pw) + 2 * (wg * pw) + 4 * (pw * pw),   # two long strips, two short, four corners
    wrong=[(2 * lg * pw + 2 * wg * pw, "partial_step"), (lg * wg, "wrong_attribute"),
           ((lg + 2 * pw) * (wg + 2 * pw), "ignored_constraint")],
    difficulty="hard", confidence=0.91,
    expl="The garden and path together are 14 m by 10 m = 140 m², and the garden itself is "
         "12 x 8 = 96 m², so the path is 140 - 96 = 44 m². Counting the strips instead "
         "gives 24 + 16 + 4 corner squares = 44 m² as well. 40 is the four strips with the "
         "corner squares left out, and 140 is the whole rectangle including the garden.",
    fmt=M2),

# --- 6. Work back from an area to a perimeter.
ar, sa = 72, 9
B.Q("perimeter_area_volume", "multi_step",
    "A rectangular chicken run has an area of 72 m². One side measures 9 m. What is the "
    "perimeter of the run?",
    key=2 * (sa + ar // sa), verify=2 * sa + 2 * (ar // sa),
    wrong=[(sa + ar // sa, "formula_slip"), (ar // sa, "partial_step"), (sa * sa, "operation_swap")],
    expl="The other side is 72 / 9 = 8 m, so the perimeter is 2 x (9 + 8) = 34 m. 17 is "
         "9 + 8 without doubling, and 8 is the missing side itself rather than the distance "
         "around the run.",
    fmt=M),

# --- 7. Sandpit, in barrow loads.
ls, ws, ds, barrow = 3, 2, 0.3, 60
litres = ls * ws * ds * 1000
B.Q("perimeter_area_volume", "multi_step",
    "A sandpit measures 3 m by 2 m and is to be filled with sand to a depth of 0.3 m. A "
    "wheelbarrow holds 60 litres, and one cubic metre of sand is 1000 litres. How many "
    "barrow loads are needed?",
    key=litres / barrow, verify=(300 * 200 * 30) / 1000 / barrow,   # cm³ -> L -> loads
    wrong=[(litres, "partial_step"), (litres / 6, "place_value"),
           (litres / barrow + 1, "off_by_one")],
    difficulty="hard", confidence=0.91,
    expl="The sand needed is 3 x 2 x 0.3 = 1.8 m³, which is 1800 litres, and 1800 / 60 = 30 "
         "loads. 1800 is the volume in litres rather than the number of loads, and 300 "
         "divides by 6 instead of 60.",
    fmt=unit("loads")),

# --- 8. Turf cost.
lt, wt, rate = 15, 8, 12.5
B.Q("perimeter_area_volume", "multi_step",
    "A rectangular lawn measures 15 m by 8 m. Turf costs $12.50 per square metre. What is "
    "the cost of turfing the whole lawn?",
    key=lt * wt * rate, verify=lt * (wt * rate),        # 8 x 12.5 = 100, then x 15
    wrong=[(2 * (lt + wt), "wrong_attribute"), (lt * wt * rate / 10, "place_value"),
           (lt * wt, "partial_step")],
    expl="The lawn is 15 x 8 = 120 m², and 120 x $12.50 = $1500. It is easier without a "
         "calculator to do 8 x $12.50 = $100 first, then 15 x $100. $120 is the area in "
         "square metres read as a price, and $46 is the perimeter of the lawn.",
    fmt=money),

# --- 9. Packing boxes into a carton.
CB = (60, 40, 30)
BX = (20, 20, 15)
B.Q("perimeter_area_volume", "multi_step",
    "A carton measures 60 cm by 40 cm by 30 cm. Boxes measuring 20 cm by 20 cm by 15 cm "
    "are packed into it with no gaps. How many boxes fit in the carton?",
    key=(CB[0] // BX[0]) * (CB[1] // BX[1]) * (CB[2] // BX[2]),
    verify=(CB[0] * CB[1] * CB[2]) // (BX[0] * BX[1] * BX[2]),   # volume ratio agrees
    wrong=[((CB[0] // BX[0]) * (CB[1] // BX[1]), "partial_step"),
           (CB[0] // BX[0] + CB[1] // BX[1] + CB[2] // BX[2], "operation_swap"),
           ((CB[0] * CB[1] * CB[2]) // (BX[0] * BX[1] * BX[2]) * 10, "place_value")],
    difficulty="hard", confidence=0.91,
    expl="Along the carton 60 / 20 = 3 boxes fit, across it 40 / 20 = 2, and up it "
         "30 / 15 = 2, so 3 x 2 x 2 = 12 boxes. The volumes agree: 72 000 cm³ / 6000 cm³ "
         "= 12. 6 counts only one layer, and 7 adds 3 + 2 + 2 instead of multiplying.",
    fmt=unit("boxes")),

# --- 10. Composite area with a side the reader must deduce.
moves = [(10, 0), (0, 5), (-3, 0), (0, 2), (-7, 0), (0, -7)]
body, per3, area3 = ortho(moves, "m", 20)
B.Q("perimeter_area_volume", "geometry_measurement",
    "The diagram shows the floor of a shearing shed. What is its area?",
    key=area3, verify=10 * 5 + 7 * 2,
    wrong=[(10 * 7, "ignored_constraint"), (per3, "wrong_attribute"), (10 * 5, "partial_step")],
    expl="Split the floor along the step: the upper part is 10 m by 5 m = 50 m² and the "
         "lower part is 7 m by 2 m = 14 m², giving 64 m². 70 is the full 10 m by 7 m "
         "rectangle, which includes the corner the shed does not cover, and 34 is the "
         "perimeter.",
    fig=svg(body), fmt=M2),

# --- 11. Water in a partly filled tank.
lt2, wt2, ht2, dep = 2, 1.5, 1, 0.4
B.Q("perimeter_area_volume", "multi_step",
    "A rectangular rainwater tank has a base measuring 2 m by 1.5 m and is 1 m tall. The "
    "water in it is 0.4 m deep. One cubic metre is 1000 litres. How much water is in the "
    "tank?",
    key=lt2 * wt2 * dep * 1000, verify=(200 * 150 * 40) / 1000,   # cm³ -> litres
    wrong=[(lt2 * wt2 * dep, "place_value"), (lt2 * wt2 * ht2 * 1000, "ignored_constraint"),
           ((lt2 + wt2 + dep) * 1000, "operation_swap")],
    expl="The water forms a box 2 m by 1.5 m by 0.4 m = 1.2 m³, which is 1200 litres. "
         "3000 uses the full 1 m height and ignores that the water is only 0.4 m deep, and "
         "1.2 is the volume in cubic metres rather than in litres.",
    fmt=L),

# --- 12. Compare two paddocks.
pa, pb = 40 * 25, 32 * 32
B.Q("perimeter_area_volume", "multi_step",
    "Paddock A is a rectangle measuring 40 m by 25 m. Paddock B is a square with sides of "
    "32 m. Which paddock covers more ground, and by how much?",
    key=f"Paddock B, by {pb - pa} m²", verify=f"Paddock B, by {32 * 32 - 40 * 25} m²",
    wrong=[(f"Paddock A, by {pb - pa} m²", "misread_data"),
           (f"Paddock A, by {2 * (40 + 25) - 4 * 32} m²", "wrong_attribute"),
           ("They cover the same area", "ignored_constraint")],
    difficulty="hard", confidence=0.90,
    expl="Paddock A is 40 x 25 = 1000 m² and Paddock B is 32 x 32 = 1024 m², so B is larger "
         "by 24 m². Paddock A, by 2 m² compares the fences instead of the ground: A's "
         "perimeter is 130 m and B's is 128 m, which is a different question.",
    fmt=PLAIN),

# ===================================================== angle properties (8)

# --- 13. Angles on a straight line.
given = 118
B.Q("angle_properties", "geometry_measurement",
    "In the diagram, a ray meets a straight line. What is the size of angle x?",
    key=180 - given, verify=180 - 118,
    wrong=[(360 - given, "wrong_attribute"), (given, "partial_step"), (180 - 108, "misread_data")],
    expl="Angles on a straight line add to 180°, so x = 180 - 118 = 62°. 242 treats the "
         "two angles as a full turn and subtracts from 360 instead, and 72 comes from "
         "reading the given angle as 108 rather than 118.",
    fig=angle_rays([given, 180 - given], [f"{given}°", "x"]), fmt=deg),

# --- 14. Angles at a point.
a1, a2 = 95, 130
B.Q("angle_properties", "geometry_measurement",
    "Three angles meet at a point, as shown. What is the size of angle y?",
    key=360 - a1 - a2, verify=360 - (a1 + a2),
    wrong=[(a1 + a2, "partial_step"), (abs(180 - a1 - a2), "formula_slip"),
           (360 - a1 - 100, "misread_data")],
    expl="Angles at a point add to 360°, so y = 360 - 95 - 130 = 135°. 225 is just the two "
         "given angles added together, and 45 uses a straight line's 180° when the three "
         "angles go all the way round.",
    fig=angle_rays([a1, a2, 360 - a1 - a2], [f"{a1}°", f"{a2}°", "y"], full=True),
    fmt=deg),

# --- 15. Triangle angle sum.
t1, t2 = 47, 68
B.Q("angle_properties", "geometry_measurement",
    "Two angles of a triangle measure 47° and 68°, as shown. What is the third angle?",
    key=180 - t1 - t2, verify=180 - (t1 + t2),
    wrong=[(t1 + t2, "partial_step"), (360 - t1 - t2, "formula_slip"), (90 - (180 - t1 - t2), "wrong_attribute")],
    expl="The three angles of a triangle add to 180°, so the third is 180 - 47 - 68 = 65°. "
         "115 is the two given angles added but not subtracted, and 245 uses 360° as the "
         "total, which belongs to a quadrilateral rather than a triangle.",
    fig=triangle_fig(t1, t2, [f"{t1}°", f"{t2}°", "?"]), fmt=deg),

# --- 16. Isosceles triangle.
apex = 34
B.Q("angle_properties", "geometry_measurement",
    "An isosceles triangle has an apex angle of 34°. The two base angles are equal. What "
    "is the size of each base angle?",
    key=(180 - apex) // 2, verify=90 - apex // 2,     # (180 - a)/2 == 90 - a/2
    wrong=[(180 - apex, "partial_step"), (apex, "misread_data"), (180 - apex // 2, "formula_slip")],
    difficulty="hard", confidence=0.91,
    expl="The two base angles share what is left after the apex: 180 - 34 = 146°, and half "
         "of that is 73°. 146 forgets to share it between the two equal angles, and 163 "
         "halves the apex angle first and subtracts that, doing the two steps the wrong "
         "way round.",
    fmt=deg),

# --- 17. Vertically opposite and straight line.
cross = 63
B.Q("angle_properties", "geometry_measurement",
    "Two straight lines cross. One of the four angles formed measures 63°. What is the "
    "size of an angle next to it?",
    key=180 - cross, verify=180 - 63,
    wrong=[(cross, "wrong_attribute"), (360 - cross, "operation_swap"), (90 - cross, "formula_slip")],
    expl="An angle next to the 63° angle sits with it on a straight line, so it is "
         "180 - 63 = 117°. 63 is the angle vertically opposite the one given, which is "
         "equal rather than next to it, and 27 treats the pair as making a right angle.",
    fmt=deg),

# --- 18. Quadrilateral angle sum.
q1, q2, q3 = 85, 100, 92
B.Q("angle_properties", "geometry_measurement",
    "Three angles of a quadrilateral measure 85°, 100° and 92°. What is the fourth angle?",
    key=360 - q1 - q2 - q3, verify=360 - (q1 + q2 + q3),
    wrong=[(q1 + q2 + q3, "partial_step"), (abs(180 - q1 - q2 - q3), "formula_slip"),
           (360 - q1 - 90 - q3, "misread_data")],
    expl="The four angles of a quadrilateral add to 360°, so the fourth is "
         "360 - 85 - 100 - 92 = 83°. 277 is the three given angles added together, and 97 "
         "uses 180° as the total, which is the angle sum of a triangle.",
    fmt=deg),

# --- 19. Compass turn.
B.Q("angle_properties", "multi_step",
    "A bushwalker near Mount Kosciuszko is facing north. She turns 135° clockwise, then "
    "turns a further 90° clockwise. Which direction is she facing now?",
    key="south-west", verify="south-west",
    wrong=[("south-east", "partial_step"), ("north-west", "inverse"), ("west", "operation_swap")],
    expl="The two turns come to 135 + 90 = 225° clockwise from north, and 225° clockwise "
         "points south-west. South-east is where she is facing after the first turn only, "
         "and north-west is 225° turned the wrong way, anticlockwise.",
    fmt=PLAIN),

# --- 20. Reflex angle.
ref = 145
B.Q("angle_properties", "geometry_measurement",
    "Two rays from a point make an angle of 145°. What is the size of the reflex angle "
    "between the same two rays?",
    key=360 - ref, verify=180 + (180 - ref),
    wrong=[(ref, "partial_step"), (180 - ref, "formula_slip"), (360 + ref, "operation_swap")],
    expl="The two angles at the point make a full turn, so the reflex angle is "
         "360 - 145 = 215°. 35 subtracts from 180 as though the rays lay on a straight "
         "line, and 145 repeats the angle given rather than the reflex one.",
    fmt=deg),

# ===================================================== units and conversions (8)

# --- 21. Kilometres to metres, three laps.
course = 2.4
B.Q("units_conversion", "multi_step",
    "A cross-country course at a school in Armidale is 2.4 km long. A student runs the "
    "course three times. How far does she run in total, in metres?",
    key=course * 3 * 1000, verify=2400 * 3,
    wrong=[(course * 3 * 100, "place_value"), (course * 3, "partial_step"),
           ((course + 3) * 1000, "operation_swap")],
    expl="One lap is 2.4 km = 2400 m, and three laps are 3 x 2400 = 7200 m. 7.2 is the "
         "distance in kilometres rather than in metres, and 5400 adds 2.4 and 3 instead of "
         "multiplying them.",
    fmt=M),

# --- 22. Millilitres to litres.
serve, serves = 250, 6
B.Q("units_conversion", "single_step",
    "A recipe uses 250 mL of milk for each serve. How many litres of milk are needed for "
    "6 serves?",
    key=serve * serves / 1000, verify=(serve / 1000) * serves,
    wrong=[(serve * serves / 100, "place_value"), (serve * serves, "partial_step"),
           (serve * 5 / 1000, "misread_data")],
    expl="Six serves need 6 x 250 = 1500 mL, and 1000 mL make a litre, so that is 1.5 L. "
         "1500 is the amount in millilitres with the litre label attached, and 1.25 uses "
         "five serves instead of six.",
    fmt=L),

# --- 23. Grams to kilograms.
bagg, bags = 750, 8
B.Q("units_conversion", "single_step",
    "A shop sells flour in 750 g bags. What is the total mass, in kilograms, of 8 bags?",
    key=bagg * bags / 1000, verify=(bagg / 1000) * bags,
    wrong=[(bagg * bags, "partial_step"), (bagg * bags / 10000, "place_value"),
           (bagg * 7 / 1000, "misread_data")],
    expl="Eight bags weigh 8 x 750 = 6000 g, and 1000 g make a kilogram, so the total is "
         "6 kg. 6000 is the mass in grams, and 5.25 weighs only seven bags.",
    fmt=KG),

# --- 24. Millimetres to centimetres.
mm = 85
B.Q("units_conversion", "single_step",
    "On a house plan, a wall is drawn 85 mm long. What is that length in centimetres?",
    key=mm / 10, verify=mm * 0.1,
    wrong=[(mm * 10, "operation_swap"), (mm / 100, "place_value"), (mm, "partial_step")],
    expl="Ten millimetres make a centimetre, so 85 mm = 85 / 10 = 8.5 cm. 850 multiplies "
         "by ten instead of dividing, which would make the wall longer rather than "
         "shorter, and 0.85 divides by 100 as though converting to metres.",
    fmt=CM),

# --- 25. Kilograms to tonnes.
load, loads = 1250, 3
B.Q("units_conversion", "multi_step",
    "A truck makes 3 trips carrying 1250 kg of gravel each time. What is the total mass "
    "carried, in tonnes?",
    key=load * loads / 1000, verify=(load / 1000) * loads,
    wrong=[(load * loads, "partial_step"), (load * loads / 100, "place_value"),
           (load * 2 / 1000, "misread_data")],
    expl="Three trips carry 3 x 1250 = 3750 kg, and 1000 kg make a tonne, so that is "
         "3.75 t. 3750 is the mass in kilograms, and 2.5 counts only two trips.",
    fmt=T),

# --- 26. Compare lengths given in different units.
B.Q("units_conversion", "single_step",
    "Which of these lengths is the longest?",
    key="0.75 m", verify="0.75 m",              # 75 cm, against 72, 70 and 68
    wrong=[("720 mm", "place_value"), ("0.7 m", "rounding"), ("68 cm", "misread_data")],
    mixed_units=True,
    expl="Put them all in centimetres: 0.75 m = 75 cm, 720 mm = 72 cm, 0.7 m = 70 cm and "
         "68 cm. So 0.75 m is the longest. 720 mm is the largest bare number on the page "
         "and is what anyone comparing digits without converting will pick, and 0.7 m is "
         "chosen by reading 0.75 as though the 5 did not matter.",
    fmt=PLAIN),

# --- 27. Litres to millilitres, with a part jug left over.
tank, jug = 25, 400
B.Q("units_conversion", "multi_step",
    "A water tank holds 25 L. It is filled using a jug that holds 400 mL. How many jugfuls "
    "are needed to fill the tank?",
    key=-(-(tank * 1000) // jug), verify=63,          # 62.5 rounded up: the last jug is partial
    wrong=[((tank * 1000) // jug, "off_by_one"), (tank * 1000 / 4, "place_value"),
           (tank * 1000 / jug, "partial_step")],
    difficulty="hard", confidence=0.90,
    expl="The tank holds 25 x 1000 = 25 000 mL and 25 000 / 400 = 62.5, so 62 jugfuls leave "
         "the tank not quite full and a 63rd is needed. 62 drops the half jug that still "
         "has to be poured, and 62.5 is not a possible number of jugfuls.",
    fmt=unit("jugfuls")),

# --- 28. Perimeter in metres from sides given in centimetres.
s1, s2 = 250, 175
B.Q("units_conversion", "multi_step",
    "A rectangular rabbit pen measures 250 cm by 175 cm. What is its perimeter, in metres?",
    key=2 * (s1 + s2) / 100, verify=2 * (s1 / 100) + 2 * (s2 / 100),
    wrong=[(2 * (s1 + s2), "partial_step"), ((s1 + s2) / 100, "formula_slip"),
           (2 * (s1 + s2) / 10, "place_value")],
    difficulty="hard", confidence=0.91,
    expl="The perimeter is 2 x (250 + 175) = 850 cm, and 100 cm make a metre, so it is "
         "8.5 m. 850 is the perimeter left in centimetres, and 4.25 adds the two sides and "
         "converts but never doubles for the opposite pair.",
    fmt=M),

# ===================================================== time and timetables (8)

TT = table([["Service", "Bendigo", "Castlemaine", "Kyneton", "Melbourne"],
            ["A", "6:42 am", "7:05 am", "7:21 am", "8:31 am"],
            ["B", "7:18 am", "7:41 am", "7:57 am", "9:07 am"],
            ["C", "8:05 am", "8:31 am", "8:49 am", "10:02 am"]])

# --- 29. Journey length from the timetable.
B.Q("time_timetables", "data_interpretation",
    "The timetable shows three morning train services. How long does service C take to "
    "travel from Bendigo to Melbourne?",
    key="1 h 57 min", verify="1 h 57 min",     # 8:05 -> 10:02 is 55 min to 9:00 plus 62
    wrong=[("1 h 97 min", "operation_swap"), ("2 h 3 min", "off_by_one"),
           ("2 h 57 min", "misread_data")],
    expl="From 8:05 am to 10:02 am is 1 hour to 9:05, then 57 more minutes to 10:02, so "
         "1 h 57 min. 1 h 97 min comes from subtracting the clock times as if they were "
         "decimals, 10.02 - 8.05, and no answer in minutes should ever be 97.",
    fig=TT, fmt=PLAIN),

# --- 30. Part of a journey.
B.Q("time_timetables", "data_interpretation",
    "Using the timetable, a passenger boards service C at Castlemaine and travels to "
    "Melbourne. How long is that trip?",
    key="1 h 31 min", verify="1 h 31 min",     # 8:31 -> 10:02
    wrong=[("1 h 71 min", "operation_swap"), ("1 h 57 min", "misread_data"),
           ("2 h 31 min", "off_by_one")],
    expl="Service C leaves Castlemaine at 8:31 am and reaches Melbourne at 10:02 am, which "
         "is 1 h 31 min. 1 h 57 min is the whole trip from Bendigo, which is not where "
         "this passenger got on.",
    fig=TT, fmt=PLAIN),

# --- 31. Gap between services.
B.Q("time_timetables", "data_interpretation",
    "Using the timetable, how long after service A leaves Bendigo does service B leave "
    "Bendigo?",
    key="36 minutes", verify="36 minutes",     # 6:42 -> 7:18
    wrong=[("76 minutes", "operation_swap"), ("24 minutes", "misread_data"),
           ("96 minutes", "off_by_one")],
    expl="Service A leaves at 6:42 am and service B at 7:18 am: 18 minutes to 7:00 and 18 "
         "more to 7:18 gives 36 minutes. 76 minutes subtracts 7.18 - 6.42 as decimals, "
         "which the clock does not work like, and 96 minutes counts a whole extra hour "
         "between 6:42 and 7:18.",
    fig=TT, fmt=PLAIN),

# --- 32. 24-hour clock.
B.Q("time_timetables", "single_step",
    "A ferry leaves Circular Quay at 14:35 and the crossing takes 55 minutes. At what time "
    "does it arrive, on a 24-hour clock?",
    key="15:30", verify="15:30",               # 14:35 + 25 = 15:00, + 30 = 15:30
    wrong=[("15:90", "operation_swap"), ("13:40", "inverse"), ("16:30", "off_by_one")],
    expl="From 14:35, 25 minutes reaches 15:00 and the remaining 30 minutes reaches 15:30. "
         "15:90 adds 35 and 55 to make 90 minutes without turning 60 of them into an hour, "
         "and 13:40 subtracts the crossing time instead of adding it.",
    fmt=PLAIN),

# --- 33. Work backwards from an arrival time.
B.Q("time_timetables", "multi_step",
    "A student must arrive at a swimming carnival by 8:40 am. The bus trip takes 25 "
    "minutes and it takes her 15 minutes to walk to the bus stop. What is the latest time "
    "she can leave home?",
    key="8:00 am", verify="8:00 am",           # 25 + 15 = 40 minutes before 8:40
    wrong=[("8:15 am", "partial_step"), ("7:40 am", "operation_swap"),
           ("9:20 am", "inverse")],
    expl="The journey takes 25 + 15 = 40 minutes altogether, and 40 minutes before 8:40 am "
         "is 8:00 am. 8:15 am allows for the bus but forgets the 15 minute walk, and "
         "9:20 am adds the 40 minutes to the arrival time instead of subtracting them.",
    fmt=PLAIN),

# --- 34. Elapsed time across midnight.
B.Q("time_timetables", "multi_step",
    "A flight leaves Perth at 11:40 pm and is in the air for 3 hours and 25 minutes. At "
    "what time does it land?",
    key="3:05 am", verify="3:05 am",           # 20 min to midnight, then 3 h 5 min
    wrong=[("2:65 am", "operation_swap"), ("3:05 pm", "misread_data"),
           ("2:05 am", "off_by_one")],
    difficulty="hard", confidence=0.90,
    expl="It is 20 minutes to midnight, leaving 3 h 5 min of the flight, so the plane lands "
         "at 3:05 am. 2:65 am adds 40 and 25 minutes without regrouping 60 of them into an "
         "hour, and 3:05 pm loses track of the flight crossing midnight into the morning.",
    fmt=PLAIN),

# --- 35. Australian time zones.
B.Q("time_timetables", "single_step",
    "Perth is 2 hours behind Sydney. When it is 2:30 pm in Sydney, what time is it in "
    "Perth?",
    key="12:30 pm", verify="12:30 pm",
    wrong=[("4:30 pm", "inverse"), ("2:30 pm", "ignored_constraint"),
           ("12:30 am", "misread_data")],
    expl="Perth is behind, so take two hours off: 2:30 pm becomes 12:30 pm. 4:30 pm adds "
         "the two hours instead, which is what you would do going the other way, and "
         "12:30 am is the middle of the night rather than the middle of the day.",
    fmt=PLAIN),

# --- 36. Total duration with breaks.
e1, e2, e3, brk = 45, 80, 50, 10       # 50, not 55: at 55 the "forgot the breaks"
tot = e1 + e2 + e3 + 2 * brk           # distractor lands on a round 3 hours, which no
hm = lambda m: f"{m // 60} h {m % 60} min"   # paper writes and no other option matches
B.Q("time_timetables", "multi_step",
    "At an athletics carnival, three events last 45 minutes, 1 hour 20 minutes and 50 "
    "minutes. There is a 10 minute break between one event and the next. How long does "
    "the carnival run from the start of the first event to the end of the last?",
    key=hm(tot), verify="3 h 15 min",
    wrong=[(hm(tot - 2 * brk), "partial_step"), (hm(tot + brk), "off_by_one"),
           (hm(tot + 60), "operation_swap")],
    difficulty="hard", confidence=0.90,
    expl="The events take 45 + 80 + 50 = 175 minutes, and there are two breaks between "
         "three events, adding 20 minutes, so 195 minutes = 3 h 15 min. 2 h 55 min leaves "
         "the breaks out altogether, and 3 h 25 min counts three breaks when only two fall "
         "between the events.",
    fmt=PLAIN),

if __name__ == "__main__":
    B.write()
