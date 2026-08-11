"""Decide which quantitative_reasoning questions are beyond a Year 8 VIC candidate.

`vic_content_taxonomy_TASK.md` §3.3 reported **188** ACT-sourced quantitative items as
beyond Year 8, from a keyword scan. Reading them says otherwise: of 231 candidates the
same kind of scan turns up here, **98 are genuinely out of range and 133 are not.** The
scan was flagging the *vocabulary* of a topic rather than the *technique* a student needs.

The four ways it was wrong, each worth knowing before writing another scan:

- **`topic` is the generating model's label and it is frequently just wrong.** A prism
  volume question is filed under "Permutations and Combinations"; a Pythagoras walk is
  filed under "Trigonometry and Bearings". Neither has anything to do with its label.
- **Trigonometry is in scope.** §3.1 puts "basic trigonometry" in Measurement and
  Geometry, so sin/cos/tan on a right triangle stays. Only cot/sec/cosec, identities,
  radians, quadrants and the sine area rule go. That alone reverses most of the 61.
- **Counting is in scope.** "How many ways" questions are staple selective material and
  answerable by the multiplication principle or by listing. Only nCr/factorial *notation*
  goes. That reverses most of the 16.
- **A quadratic in the working is not a quadratic in the question.** Where four options
  are given and one substitutes cleanly (`w(w+6) = 135`), a Year 8 tests options and is
  done. What is excluded is where solving is unavoidable: the quadratic formula, a
  non-integer root, `-b/2a`, completing the square, the discriminant, Vieta.

So the exclusion cannot be computed. `CANDIDATES` casts a deliberately wide net and
`VERDICTS` records a human decision per question, with the technique that decided it.
`--unadjudicated` lists candidates no one has ruled on, so a new book is finishable
rather than silently half-filtered.

**Why exclusion means "do not push".** quantitative_reasoning routes to `vic-seal` only
(`push_to_selectly.SUBJECT_SCHOOL_IDS`), so there is no other exam to demote these to.
Out of the VIC pool is out of the bank. They are not rejected in qbank — they are correct
questions aimed two years high, and a JMSS or senior product could want them later.

A fifth finding, recorded but not acted on here: **four items need a calculator** and are
excluded on that ground rather than content. They ask for `tan 35°` with no value
supplied, in a non-calculator exam. Items that supply the ratio ("Use tan 30° ~= 0.577")
or leave the answer as an expression ("60 tan 47°") are fine and are kept.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.qr_beyond_year8 --report
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.qr_beyond_year8 --unadjudicated
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.qr_beyond_year8 --sample 5
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.qr_beyond_year8 --manifest
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "run_data" / "db" / "qbank.db"
MANIFEST = REPO_ROOT / "run_data" / "output" / "qr_beyond_year8.json"

# Deliberately high-recall. A false positive costs one read; a false negative ships a
# logarithm to a Year 8. Ordered most-specific first -- the first match names the group.
CANDIDATES: list[tuple[str, str]] = [
    ("calculus", r"\bderivative\b|\bintegral\b|\bcalculus\b|f['′″]\(|differentiat"),
    ("stats_adv", r"standard deviation|\bvariance\b|normal(?:ly)? distribut|z-score|empirical rule|confidence interval"),
    ("log", r"\blogarithm|\blog[_₀-₉]|\blog\s*[₂-₉\d(]|\bln\s*\(|\bln\(|\be\^|exponential (?:growth|decay|function|model)"),
    ("trig", r"\btrigonometr|\bsine\b|\bcosine\b|\bsec\s*\(|\bcosec|\bcot\s*\(|\bsin\b|\bcos\b|\btan\b|SOHCAHTOA|angle of (?:elevation|depression)"),
    ("conic", r"\bparabola|\bhyperbola\b|\bellipse\b|equation of the circle|vertex of the"),
    ("quadratic", r"quadratic|discriminant|complet(?:e|ing) the square|x²|x\^2|roots of the equation|factoris\w* .{0,20}\bx\b"),
    ("perm", r"\bpermutation|\bcombinatoric|\bfactorial|\bnCr\b|\bnPr\b|\b\d!|how many (?:different )?(?:ways|arrangements|orders)"),
    ("series", r"geometric series|arithmetic series|sigma notation|\bsummation\b|sum to infinity"),
    ("misc_adv", r"\bmatrix\b|\bmatrices\b|\bvector\b|\bsurd\b|imaginary number|complex number"),
]

FIELDS = ("stem", "option_a", "option_b", "option_c", "option_d", "explanation", "topic")

# Hand-adjudicated 2026-08-12 by reading all 231 candidates. The reason is the technique
# that put the item out of range, not the topic it was filed under.
EXCLUDE: list[tuple[str, str]] = [
    ("0029a406-142e-4d53-9bf8-7e2b97ea136c", "log_laws"),  # If log_a(p) = 4 and log_a(q) = 7, what is log_a(√(p³q))?
    ("056dff9c-e9d8-428a-929c-c2feed273186", "cot"),  # In the figure below, right triangle PQR has a right angle at P. The si
    ("0a1c0aab-0be8-4f66-945e-4a402562a64b", "calculus"),  # Let f(x) = 3x³ − 2x² + 5x − 1. Find the value of the second derivative
    ("11bd93e8-3890-40a4-9196-47af35b0c7ee", "solve_quadratic"),  # What values of k are solutions to k² + 6k = 7?
    ("1702b2e6-6029-4327-8aed-560b63681960", "ln"),  # The koala population in a national park is modelled by P(t) = 500 × e^
    ("19fbbf54-e877-47f4-a5f8-9b2c72aaf541", "function_transformation"),  # The height of a kangaroo's jump is modelled by h(x) = −(x − 2)² + 4, w
    ("1d6de3c1-c19a-4130-913b-8dfffc165521", "conic_equation"),  # What is the equation of the circle in the standard (x, y) coordinate p
    ("1f6c7957-5c6d-4f09-8d59-099ad834bd1b", "log_notation"),  # Which value of n satisfies log_n 81 = 4?
    ("20e5a779-c93a-4e76-8fca-16cf9dd193d1", "factorise_quadratic"),  # Which of the following is a factor of the polynomial x² + 5x − 24?
    ("2480ca69-9052-45da-ab73-ae10b4b120ca", "e_exponential"),  # The population, P, of a small Australian coastal town is modelled by P
    ("2485fc69-5c13-4bcb-a76f-2203d11d9347", "quadratic_formula"),  # A rectangular swimming pool measures 25 metres in length and 12 metres
    ("253c5def-a1c7-4739-80eb-5db9a7e6d7b1", "log_notation"),  # Evaluate log₂(64) − log₃(27).
    ("2912b11d-b8d2-44b8-894b-409373622371", "solve_quadratic"),  # The quadratic function f(x) = x² − 6x + 5 is graphed on the coordinate
    ("2a09ab24-8fc7-4d85-9f8c-0bb9502c6e33", "normal_distribution"),  # The floor areas of houses in a new Victorian development are normally 
    ("2b785823-3ad8-465d-aa46-8c9469d16772", "z_score"),  # The daily percentage change for Aussie Gold Mines shares follows a nor
    ("324719c6-cbe1-40d0-95f4-43e1b1d19e9a", "factorise_quadratic"),  # If x² − 28b² = 3xb, what are the two solutions for x in terms of b?
    ("33a349ee-1c98-46eb-9fd9-917e0dc4d3e7", "e_exponential"),  # Students modelling the kookaburra population in a Perth park use the f
    ("34f607aa-5f88-435f-ad4e-4de204d271cd", "vertex_formula"),  # A cricket ball follows a parabolic path modelled by h(t) = −5t² + 20t 
    ("39526aea-5bd5-42c1-a6d4-384c41669328", "normal_distribution"),  # The average monthly rainfall in Brisbane during the wet season is 350 
    ("3a8be4c1-0f4e-4e1d-9080-446f2a7da14e", "trig_identity_radians"),  # Given that cos θ = −12/13 and π/2 < θ < π, what is the exact value of 
    ("3cae1b1b-0318-4205-b4e8-0a21380fa59e", "vertex_formula"),  # The cost to develop a new app is modelled by C(x) = 0.01x² − 2x + 5000
    ("3d887d84-dadc-4b22-93ee-b883858793bd", "log_laws"),  # If log_b(m) = 3 and log_b(n) = 5, what is log_b(m²n³)?
    ("3e8837bc-d4f1-4efe-971f-67470c51794b", "vertex_formula"),  # The height of a bird's flight path is modelled by y = −0.05x² + 2x, wh
    ("44157f23-bbda-4849-8437-551470caa10b", "quadratic_formula"),  # A rectangular swimming pool is 50 metres long and 25 metres wide. A un
    ("470d746f-e9d2-4e11-890b-e702058d7b86", "conic_equation"),  # A circle has centre (−3, 6) and passes through the point (1, 9). What 
    ("47222035-a044-4ab7-8d75-5b38bbae9563", "cot"),  # In the figure below, triangle ABC is right-angled at C. The angle at B
    ("484a596c-2434-489d-8ef2-c9ce0eb0a839", "conic_equation"),  # A ball is thrown between two posts that are 50 metres apart and at gro
    ("50252329-3be3-4c21-a773-8afa0503ca31", "quadratic_formula"),  # A rectangular swimming pool measures 25 m long and 12 m wide. A unifor
    ("504a0ebc-9a61-4309-96e8-50b41163d746", "sine_area_rule"),  # A surveyor measures two sides of a triangular block of land as 250 m a
    ("5111f2f0-d5bc-4150-8ab5-a258d7f35513", "calculator_required_tan62"),  # Liam stands 45 metres from the base of a tall pylon and measures the a
    ("5bad3ba8-7ee2-4e0f-ad55-25db8a46ce8b", "conic_equation"),  # A circle in the standard (x, y) coordinate plane is tangent to the x-a
    ("5d349c8c-f997-416b-b2f0-027cde22dcd4", "ln"),  # The population of quokkas on Rottnest Island is modelled by P(t) = 150
    ("5e71f485-453e-4863-9063-bf55ce378e80", "log_notation"),  # If \log_3(x) + \log_3(x - 2) = 1, what is the value of x?
    ("5f06fb2f-f308-45f2-a09a-12e4f0031cf0", "complex_numbers"),  # For the complex number z = −√3 + i, what are the modulus |z| and the a
    ("5f2cd252-c141-4927-97ef-16e5bb14f032", "vertex_optimisation"),  # A farmer in Tasmania is fencing a rectangular sheep paddock using 500 
    ("5fc9266a-c26b-4917-bca6-0d76d117c29f", "sinusoidal_model"),  # The daily energy production E (in kWh) of a solar power system is mode
    ("62e8c1bf-a550-4d3f-b3a5-de83fa868ed0", "quadratic_coefficient_signs"),  # The graph below shows a parabola y = ax² + bx + c. Based on the graph,
    ("6365cfe1-89d0-445a-aaaa-5dbf9acc958a", "vieta"),  # For the quadratic equation ax² + bx + c = 0, the two solutions are x =
    ("6cf8eb46-3a49-4261-8235-83a9a6c6f425", "log_notation"),  # If log₅ x = 3, then which of the following is equal to x?
    ("73f86921-c9b1-44d7-a08b-10c4abd3fa6d", "quadratic_formula"),  # A rectangular swimming pool is 25 m long and 12 m wide. It is surround
    ("7630c5e3-cef3-49ce-873b-cebca6adc613", "factorise_quadratic"),  # The polynomial x² + 3x − 18 can be factorised. Which of the following 
    ("7a8d1150-e673-4fc0-bf1a-9b12bc73fb6c", "fractional_index_root"),  # The population of a regional Australian town grew from 15,000 to 18,00
    ("7d2d01d9-e521-4b24-8277-38948490f970", "rational_function"),  # Which of the following best describes the graph, in the standard (x, y
    ("7d39e960-84ff-45c1-84f9-d0743a8e360e", "trig_identity"),  # Simplify the expression `(cos(2θ) + sin²(θ)) / cos(θ)`.
    ("8305d62e-2f4e-4b99-9ec3-834cfbadd1e1", "vertex_formula"),  # A small business owner calculates their profit P (in dollars) from sel
    ("84f36f4b-be4d-485e-9549-a588c37dc3b5", "solve_quadratic"),  # If x² − 6x − 40 = 0, what are the solutions for x?
    ("850f63a8-6d37-4ab1-bf81-0c615da14e94", "log_notation"),  # What is the value of log₃ 243?
    ("857ce16c-0a93-4efc-9682-190cde552d64", "conic_equation"),  # The graph below shows a circle drawn on a coordinate plane. What is th
    ("85fad3c8-29c4-4e1b-9fd6-09497fd097ed", "fit_parabola"),  # The arch of the Sydney Harbour Bridge can be modelled by a parabola. T
    ("8aed24d5-1090-4448-963f-0a8770c5cb7c", "solve_quadratic"),  # A kangaroo's jump follows a parabolic path modelled by h = −0.02x² + 0
    ("952da0e5-82c3-489c-8459-402890618caa", "vertex_form"),  # The graph below shows a parabola. Which of the following could be its 
    ("957feb38-0c2c-4c71-913c-87fff2d0ffe9", "compound_angle_radians"),  # What is sin(π/12), given that π/12 = π/4 − π/6 and that sin(α − β) = (
    ("95cf4e85-434b-45d7-9b75-1196444c95dd", "e_exponential"),  # The population of hopping mice in a controlled study grows according t
    ("965cbf15-5270-4c78-98a2-8f43f863edb8", "normal_distribution"),  # The average May rainfall in Tasmania is 85 mm, and rainfall follows a 
    ("9933cd20-c954-4ed6-8ccf-389394d1a96a", "quadratic_function_algebra"),  # Chloe runs a small bakery in Geelong. The cost in dollars to produce x
    ("9aa2b077-6eec-45c3-9c63-e1ccf253b27a", "vertex_formula"),  # A hot air balloon rises vertically from the ground. Its height h (in m
    ("9b93aa32-fdbc-44c3-94bc-5f19af8ce94a", "calculator_required_sin15"),  # A regular 12-sided polygon (dodecagon) is inscribed in a circle of rad
    ("9dcfb629-6a68-4080-8877-242df221722d", "compound_angle_radians"),  # Using the fact that sin(α + β) = sin α cos β + cos α sin β, and using 
    ("9e6ae4a3-1b93-48ec-86dd-f996d3e71a30", "calculator_required_tan35"),  # A surveyor stands 50 metres from the base of a tall eucalyptus tree. T
    ("9fde0d47-74d9-4985-8b37-abe1ab707c7f", "vertex_formula"),  # The height of a football (in metres) after being kicked can be modelle
    ("a1cc86a3-2100-4555-a655-c8eb70c8a933", "vertex_optimisation"),  # A farmer uses an existing 20-metre shed wall as one side of a rectangu
    ("a572e7d2-4044-4c00-b42d-454b20104ef8", "conic_equation"),  # The graph below shows a circle centred at the origin. What is the equa
    ("a9580a25-cb87-43c6-9088-4efcec38c56f", "factors_fractional_roots"),  # A quadratic equation has solutions x = −2/5 and x = 3/7. Which of the 
    ("ac6322e3-ac8a-4d8d-ad60-345d74926b58", "calculus"),  # Given the function f(x) = 2x³ − 5x² + 3x − 1, find the value of f′(2),
    ("aea78c36-12d5-4089-b358-928d900be9f4", "factors_fractional_roots"),  # For a quadratic equation ax² + bx + c = 0, the two solutions are x = 2
    ("b8efeb58-20c3-43a2-beb2-eb1358730a8d", "standard_deviation"),  # Scientists recorded the number of koalas in 12 forest patches in New S
    ("bdcf3e72-642c-4b63-a51b-c952761f80b6", "radians_arccos"),  # If the value of cos θ = −0.574 (to the nearest thousandth), which of t
    ("bf2e17f7-8f1f-4f78-a3ec-473164d617f7", "solve_quadratic"),  # A rectangular swimming pool has a uniform path of width 2 m built arou
    ("bf9fe305-e5f4-43cf-8f53-4136b03e8e80", "sine_range"),  # A kangaroo's hopping speed (in km/h) at time t hours after sunrise is 
    ("bfe8e513-8853-4912-92d8-5c9cf7f2174e", "discriminant"),  # For which of the following values of c will the equation 3x² + 12x + c
    ("c21e2842-dca7-4e4f-91b2-6b1f1990fc7f", "e_exponential"),  # The population of kangaroos in a national park is modelled by P(t) = 5
    ("c4509a6b-d625-42e3-8289-6b35c68f2d4f", "log_notation"),  # The koala population in a national park near Port Macquarie is current
    ("c4ebb9d0-41c3-4209-ab81-84a793c9fa0c", "fit_parabola"),  # The parabola y = ax² + bx + c passes through the points (0, 0), (2, 8)
    ("c606c683-6348-4e66-89ec-857a7482753b", "solve_quadratic"),  # What are all the solutions for x if 2x² + x − 15 = 0?
    ("c65a6853-7cd6-4633-a6d5-77cf79a68bd1", "normal_distribution"),  # The heights of a species of eucalyptus tree are normally distributed w
    ("c6a5df18-51f2-41a5-b405-f5fcf99649ce", "e_exponential"),  # A stock's value is modelled by S(t) = 50e^(−0.02t), where t is the num
    ("c70ff11c-9d2b-4226-b55b-3ad57186eb4b", "fractional_index_root"),  # A kangaroo population in the Blue Mountains was 1500 in 2020 and grew 
    ("c7fe9ace-bd7c-4bc4-bcfd-b8bbc7cac989", "discriminant"),  # For what nonzero whole number $m$ does the quadratic equation $y^2 + 6
    ("c87fff19-8ad5-4a43-8718-d07ea7b3e058", "discriminant"),  # A quadratic equation ax² + bx + c = 0 has discriminant Δ = b² − 4ac. I
    ("cb045ad2-9f0c-4d28-9a45-36aa4a8edb65", "parabola_transformation"),  # A parabola has equation y = (x − 3)² + 5. The vertex is shifted 4 unit
    ("d40f6de8-be9a-4e85-8d47-bc865bcbce43", "vertex_formula"),  # The arch of the Sydney Harbour Bridge can be modelled by the equation 
    ("dac94052-3326-4e8c-9743-a9c5274873b2", "trig_identity_radians"),  # If sin θ = -4/5 and π < θ < 3π/2, what is the value of tan θ?
    ("dcc9c751-de0d-43c8-9a8a-b98c2edf7e4d", "quadratic_formula"),  # A rectangular swimming pool is 25 metres long and 12 metres wide. A un
    ("de61dce0-9695-4519-a249-6866447932e3", "rational_expression_quadratic"),  # For all $x > 5$, simplify $\dfrac{5x - x^2}{x^2 - 3x - 10}$.
    ("df8d226f-dba2-43f9-94ca-42137e01431e", "factorise_quadratic"),  # The graph below shows the parabola y = x² − 4x + 3. At which x-values 
    ("e08799b3-9234-46f6-9c96-7af037cdd060", "vertex_formula"),  # The daily profit P (in hundreds of AUD) earned by a bakery selling sou
    ("e3e409f1-60bd-4a43-8d50-95fe31ea03b4", "factorise_quadratic"),  # The graph below shows a parabola. What are the x-intercepts of the par
    ("e557cf34-6c4a-4895-ac99-9193a8f9b73b", "quadratic_formula"),  # A rectangular swimming pool is 25 metres long and 10 metres wide. It i
    ("e762ded7-225e-4d87-8a55-4e520b85bdae", "log_notation"),  # If log₃ x = 4, then x equals:
    ("e995c206-c5ba-475d-a2c3-1d13f4a5c73f", "vieta"),  # What is the product of the two solutions of the equation x² − 5x − 24 
    ("ea72f1f3-2fa9-4c3a-b42a-d0c198440c41", "ln"),  # The population of koalas in a conservation park is modelled by P(t) = 
    ("ea949fe5-bfdc-43d0-9eb5-eb06493d2818", "solve_quadratic"),  # A rectangular swimming pool in Melbourne is 4 metres longer than twice
    ("f4432647-e451-443a-94b7-1657e73bb0f6", "vertex_formula"),  # The trajectory of a kangaroo's hop is modelled by y = −0.05x² + 2x, wh
    ("f50c9192-d05a-4a96-b66c-7a9b4e6d6aaf", "apothem_cos36"),  # A regular pentagon is inscribed in a circle of radius 10 cm. Given tha
    ("f6bf96e9-33ca-4842-9cde-bb21bf7244f3", "fit_parabola"),  # The graph below shows a parabola. The parabola passes through the poin
    ("f76e3ef7-05c2-4ed6-b966-c503ae9b0fb4", "integration"),  # A dam releases water at a rate modelled by R(t) = 100e^(−0.05t) litres
    ("fa1f3e00-2115-49ca-9d70-14e5f8797b05", "normal_distribution"),  # A survey found that Australians spend an average of 2.3 hours per day 
    ("fa7c5fe8-4b5a-470a-bf22-06a70314bd9c", "calculator_required_tan25"),  # Uluru stands approximately 348 metres above the surrounding plain. A t
]

# Read and ruled in scope. Held explicitly so `--unadjudicated` can tell "judged usable"
# apart from "never looked at".
KEEP: list[str] = [
    "0896c838-21b9-42cc-a3fa-b70e832e91f3",  # In the figure below, a flagpole stands vertically at point B. From poi
    "0963d169-7f9d-4c5c-a609-bceed071b5d2",  # Mia is arranging 4 different books — a maths book, a science book, a h
    "0afdfcd2-947d-4d70-b584-5e00d035bf39",  # The graph of y = ax² + bx + c is shown below. The parabola opens downw
    "112ac581-83e7-45b6-965d-441459069b50",  # In the xy-coordinate system, (√3, t) is one of the points of intersect
    "12702d52-9a0c-48b8-9025-5fb52e70812c",  # Simplify: (3x³ − x² + 4x − 5) − (x³ + 2x² − x + 3)
    "12e83716-8401-49c6-9de6-2de70288acc4",  # In the figure below, triangle PQR is a right triangle with the right a
    "143dd753-46e3-4532-af65-64130284b381",  # In the right triangle XYZ shown below, angle Z is the right angle. Wha
    "1937f43e-8980-4db3-ab92-5fe26a2724e6",  # The rectangle below has length (3x + 2) cm and width (x − 1) cm. Which
    "1c897023-1392-4975-b318-13c78c390855",  # The graph below shows the path of a ball thrown from ground level. The
    "1df9730a-eb87-473e-8b93-9185f4178eba",  # Liam is packing for a 5-day trip to the Gold Coast. He has 6 shirts, 4
    "24aab8b7-f168-4a3e-86f5-c6633cc61c99",  # Scientists are monitoring a population of rare frogs in Tasmania. The 
    "24d7ff02-6085-4f1e-83a3-03780e5ae581",  # A rectangular paddock in the Northern Territory measures 240 m by 180 
    "25bbe5a8-d960-446c-bed0-1b3c296ee907",  # In the standard (x, y) coordinate plane, a square has three of its ver
    "27033346-61f4-435e-a5a9-da2885ca544b",  # In the figure below, triangle PQR has a right angle at Q. If PQ = 9 an
    "28c63857-bd3c-46c9-a2da-98b60dc61bd4",  # A lighthouse on level ground casts a shadow 80 metres long. The angle 
    "2d4e9298-60fe-48aa-92a5-c90077de0cc3",  # A school tuck shop in Brisbane offers 5 types of pies, 3 types of drin
    "2e5d84e4-c0a4-46cb-9272-f6956801e321",  # The population of a small Victorian town was 5000 in 2010 and grew to 
    "2eff2e7c-85cc-42e5-a608-56f1ca90d69f",  # The temperature in Alice Springs over a 24-hour period is modelled by 
    "30e37aa1-a35e-4c7e-b208-1735860c7254",  # A bushwalker starts at a campsite in the Blue Mountains and walks 6 km
    "34df7276-3086-4fd5-97eb-a17623bc5a48",  # Given that tan(x) = 3/4 and sin(x) is positive, what is the value of c
    "3c4ae28b-bb70-49b9-9354-4a56974a9a90",  # If $x = 15$ and $y = 5$, what is the value of $\dfrac{x^2 - y^2}{x - y
    "3ccdd7b2-027f-4144-bbb4-42bfbdfd2918",  # For all integers x, which of the following is ALWAYS an odd number? I.
    "3da275a9-2dfa-4734-9910-02b70e948248",  # A hive in Queensland contains 2500 bees. The population grows by 8% ea
    "3db63ec7-d54c-4202-8e5d-e907ebdcc02b",  # How many different 3-digit positive integers can be formed using the d
    "3e980a72-6c74-4577-a7e3-9e5fd8e62a66",  # If g(x) = 3x² − 5x + 2, what is g(−2)?
    "45b1640c-b58e-4630-9423-54e37d229cda",  # From a point on flat ground, the angle of elevation to the top of the 
    "47f49b01-beac-4fa6-b8c2-ef57dcfe797a",  # In the right triangle below, angle α is at the top-left vertex and ang
    "49f7d606-d02d-49ed-9894-ef60d5a193c7",  # If g(x) = −2x² + 5, then g(−3) = ?
    "4b9a230d-b06e-4ffa-9d74-fbb506881681",  # What is the smallest possible product of two integers that differ by 9
    "4cd6a220-3d78-483e-bcc1-f6585ade825c",  # A water sample from the Great Barrier Reef has a pH of 8.2. Using the 
    "4de74567-cd63-49ec-b753-4895d91bc161",  # The area of a rectangular paddock is 120 square metres. The length of 
    "4fca89ae-7aaf-4a9d-b7a5-f451a12eff99",  # In the figure below, a rectangular swimming pool at a Melbourne aquati
    "4fde8984-1834-4fad-9153-26d01c41e172",  # For which of the following functions is f(−4) > f(4)?
    "51f9f25b-2bb7-4f86-995e-c0d18b1d378a",  # A scientist is studying a colony of bacteria. The colony starts with 1
    "52777971-dd1f-42cd-9280-58e12e88a6a8",  # A farmer plants rows of wheat. The first row contains 50 grains, the s
    "535dde6b-6c98-4a3d-894a-5871515861c9",  # If cos A = 5/13, which of the following could be tan A?
    "5366b95c-c7b1-43f6-a526-7d745fafb2d6",  # In the right triangle below, the hypotenuse has length 13 cm and one l
    "5675ba67-5bc9-449d-b819-65eec6d505cc",  # In the right triangle PQR shown below, where the right angle is at Q, 
    "58e9df0d-db25-4ac4-ac41-4285e6a9236d",  # In the right triangle shown below, the angle at P is 34°. The side opp
    "59251e29-e4ce-4109-be6b-badcd292497e",  # Lachlan saves $15 in the first week. Each week after that, he saves $2
    "597900d9-28f4-47b2-9074-a63a5f8bcbb4",  # A hive contains 500 bees, and the population increases by 10% each wee
    "5edd52c3-6dd0-4ee4-adb5-5f3fe6f4eceb",  # In the figure below, two straight roads meet at point O. Road OA runs 
    "5fcadce7-89cb-4dd5-8841-37200788c62c",  # At a sports carnival, one male and one female athlete will be selected
    "61638577-d3cc-411b-971c-86a1198f2f69",  # A line is drawn from the origin to the point (3, 3) on a coordinate pl
    "61e8ce79-0062-4c8a-922c-5a9a5b35dd55",  # Given f(x) = 2x + 7 and g(x) = x² − 3, what is the simplified expressi
    "6406d50d-5e2d-4f2d-90d5-6f9da248a167",  # For all values of x, what is (4x + 3)²?
    "67477de9-81ad-4bce-8626-c49a36537967",  # If g(x) = x² − 5, what is g(x + 3)?
    "6836b305-8fe8-4ced-9aca-290f19917eac",  # The graph below shows the parabola y = ax² + bx + c passing through th
    "6a08c8fd-7e3d-4f3a-a6b7-a21896b9cf22",  # Mount Kosciuszko is 2228 metres high. A hiker starts at an elevation o
    "6a9b82a0-b7a1-4394-a85f-c829e1b8a44a",  # If 0° ≤ x ≤ 90° and tan x = 7/24, what is sin x?
    "6cfeab22-daa4-4b9c-a592-935379d767e3",  # What is the product of (2x² − 3)(x² + 5)?
    "6dab87e5-c910-479e-bbbd-82dcc7c79284",  # Simplify: (2x³ + 5x² − 4x + 1) − (x³ − 3x² + 2x − 6)
    "6e2ac9d8-a49a-4677-84e0-933e4a99688d",  # A quadratic function g is defined for selected values of x as shown in
    "6e487e1d-7d9c-4cf6-901d-f7cec1a578f3",  # Simplify the expression: (4x³y²)(3x²y⁴)
    "6f7e4a25-2745-45c3-ad8b-7cab214d2e86",  # Daily water consumption per household in a new development is modelled
    "72cc47b0-3249-4ec1-bf90-035433585418",  # Simplify (x⁵y⁸z) / (x³y²z⁵) to its simplest form.
    "73f19669-2912-4355-b226-ab24e9a1a036",  # Which of the following expressions is equivalent to (x + 3)² − (x − 3)
    "74067ee4-b64b-4e17-af06-e2d36f0f80eb",  # A surveyor stands 50 metres from the base of a tall eucalyptus tree an
    "7583ea9a-9efe-4d82-bc83-617f9ab69eb7",  # A farmer in Western Australia has 100 metres of fencing to enclose a r
    "78220f95-f12b-46b5-8004-e56807253f0a",  # A koala sanctuary currently has 80 koalas. The population is expected 
    "795368bb-ada3-4ec1-af14-b7407804f9a9",  # A telecommunications tower in Brisbane stands vertically on level grou
    "79ab50fc-228e-4813-bb1a-7088f1b3cc5b",  # In the right triangle PQR shown below, the hypotenuse PR is 25 cm long
    "7ef62748-0257-409e-821a-de4e01bbda1e",  # In the figure below, a line passes through the origin and the point (5
    "7f2ebfde-434a-484b-b6b9-ae4284353bc2",  # A scientist observes bacteria in a petri dish where the number of bact
    "7fc1178c-119a-4f59-bd35-f259f7fd2129",  # Expand and simplify (5x − 2)(2x − 9).
    "85666492-a3fe-45c1-a22c-f68c0c7c4fcd",  # Chloe works at a native plant nursery in Queensland. The profit P(x) i
    "85a026f8-03d6-45af-9f8e-6883338204cb",  # If p and q are constants and x² + px + 20 is equivalent to (x + 4)(x +
    "85e1c86b-5ccc-43c7-9849-daf323fc02bc",  # A surveyor stands 30 metres from the base of a tall Karri tree in West
    "8627ebcd-848d-4254-ac66-852c462b54df",  # A scientist measures the concentration of a pollutant in a Tasmanian r
    "87e79301-c05c-47fc-a9b2-be7d12e60b2e",  # Which of the following is an equivalent form of 2x + x(3x − x)?
    "8d5c1ec6-d439-42dd-9638-9dce42833dc3",  # Layla is standing 40 m from the base of a vertical flagpole in Melbour
    "8ec9689d-87b9-4cd9-a664-a9d0ad501243",  # A surveyor starts at point A, travels 5 km due east to point B, then 1
    "8f4640fa-579b-4852-8847-65a1f6e9ad23",  # In the right-angled triangle PQR below, what is sin∠QPR?
    "8f4d848b-a068-41ec-9681-f4d1a377b596",  # In the right-angled triangle below, if \(\tan\theta = \frac{5}{12}\), 
    "8fff667c-9d30-4748-bb7a-0257953ad3c9",  # Simplify: 3x² + 14x + 20 − 7x − 15x²
    "91e5d2e1-53f1-4f88-803f-f28b2c81608a",  # In the right triangle PQR shown below, angle Q = 90°, PQ = 9 cm, and Q
    "929f7dd6-a1cf-409f-af92-ecdf94d7ec1b",  # The graph of a quadratic relation passes through the points (−1, 8), (
    "92b386eb-c6d4-493d-97c8-4e6d29a73465",  # A kangaroo makes a series of hops where each hop is 0.9 times the leng
    "9696106c-b3fd-4a1a-baab-463dd0271ff2",  # A kangaroo hops in a pattern: the first hop is 2 metres, the second is
    "99610203-c69c-4f41-aad1-a39881e3ac56",  # The product of two consecutive even integers is 168. What is the sum o
    "9d2a115d-29d8-4b3f-8fe9-53f074487b68",  # The average weight of koalas at a sanctuary is 9.5 kg, with a standard
    "9eb394c5-4bef-48d1-9a27-2e4aababf2a7",  # The graph below shows line segment AB plotted on a coordinate plane. W
    "a4eddd18-da82-4b33-9a9c-1a660e3a2ba6",  # A school camp needs to assign 6 different students to 6 different acti
    "a66ee7e4-69be-4dc2-91c3-73e10c80d826",  # In the coordinate plane below, a line is drawn from the origin O to po
    "a723bb91-63d7-4b30-9bd7-be0e429ead31",  # The figure below shows a right-angled triangle with sides labelled. If
    "a80d9842-9c58-4886-89f0-a07a030721f6",  # A rectangular swimming pool in Melbourne is 20 m long and 8 m wide. A 
    "a8f77758-9c81-487b-974e-fefd3bd9a29c",  # In the right-angled triangle below, if cos θ = 8/17, what is tan θ?
    "a95d412c-f228-4c92-b790-d397ddfd496a",  # Simplify: $3x^3y^2 \times 4x^2y^3 \times 2xy$
    "aa086624-1253-4405-9d44-4945c297fef7",  # In the diagram below, triangle PQR has a right angle at R. PQ = 13 cm 
    "adb6f6d2-048c-4ddb-b116-42489f49970a",  # A quadratic function h satisfies the following table of values. Which 
    "ade7575f-a635-4ff6-8c18-f0f4d6b31ca5",  # A Melbourne café offers 4 types of bread, 5 types of filling, and 3 ty
    "b11fe692-913a-4355-9390-e107734efdfc",  # What is the smallest possible product of two real numbers whose differ
    "b2e0b69d-b2db-4bf6-a972-de543a5950c5",  # The figure below shows a right-angled triangle with legs of length 9 c
    "b39a1e1e-1a2f-4559-a4e3-556d0a4e78e9",  # A swimming club selects its 3 officials by first choosing a president,
    "b44e5cf4-12e9-4ae4-b25c-52e8e468303a",  # A farmer plants rows of macadamia trees. The first row has 5 trees, th
    "b48b30de-e104-4136-8f10-ffda297be9f9",  # How many different positive four-digit integers can be formed if the f
    "b555402a-30c3-47a7-a496-dfa0c3ae642c",  # Given f(x) = 2x − 3 and g(x) = x² + 4x − 1, which of the following is 
    "b67240f4-6400-4e64-b78c-7e6c57f5f3e3",  # In the right triangle DEF shown below, the right angle is at F. Given 
    "b70ad84b-8462-4e8b-b9f5-9b686bc1d72f",  # In the right triangle PQR shown below, the right angle is at Q. PQ = 5
    "b9c057f7-5f5c-4e50-a442-8581121c2cc0",  # Two real numbers differ by 8. What is the smallest possible value of t
    "ba183ee5-87f9-4407-971f-b8db057e1190",  # If f(x) = 3x² − 5, then f(x + 2) = ?
    "bda18384-6f78-4a24-a6ca-58639b1f7f1f",  # The graph below shows a parabola. Which of the following best represen
    "c004fdff-1240-4e4a-8eea-e9c45a7eaa45",  # In the coordinate plane below, points A, B, and C form a right triangl
    "c12dffba-d82d-4133-b9cb-3937689347c3",  # A butcher has 3 types of meat: beef, pork, and chicken. He wants to ma
    "c8a6d01f-6e3c-4b70-88f5-7c3f8a22ba22",  # Priya has 4 different blouses, 5 different skirts, and 3 different sca
    "cb520797-c4ca-40d4-bb4c-904aae8a0809",  # In the figure below, two straight lines intersect at point P. One line
    "ccb2dfba-41ac-4ae8-93ca-4f3a19b7e03c",  # In the coordinate plane below, point A is at the origin and point B is
    "ce31c27f-27b5-4bfd-97b7-80dfe89ed464",  # The area of a rectangular verandah is 18 square metres. Its length is 
    "ce375557-bbf1-4c63-99cd-ee43134c3d5e",  # In the right triangle shown below, the hypotenuse BC has length 10 cm 
    "d1f26017-b839-41fd-ab31-0f2691fbbbab",  # Simplify the expression: (5x²y³)² ÷ (10xy²)
    "d52da3c9-d800-4cae-9f8b-1b6fad31827d",  # An astronomer observes a star with apparent magnitude −1.5 and a comet
    "db5327d6-8b71-4969-a3e5-b4e4867952f0",  # Given that x² = 16 and y³ = −27, find the sum of all possible values o
    "db86b1f2-356b-464a-96b9-5b595b37a3a9",  # A school camp has 85 boys and 112 girls. One boy and one girl are chos
    "de3067a5-edab-4b50-8b3d-9f5309e96452",  # At 8:00 AM, a bushfire in regional Victoria has spread across 120 hect
    "de533ba1-e564-4fdb-8cb3-26a14f67076e",  # The graph below shows a parabola y = ax² + c passing through the point
    "e035b611-758a-4e5c-b50e-507a076747da",  # If sin B = 5/13 and cos B = 12/13, what is tan B?
    "e5308813-5ab4-4f5b-baa2-20b40644e984",  # If 0° ≤ θ ≤ 90° and sin θ = 5/13, what is the value of cos θ?
    "e6839d84-a869-48fb-b93b-660b70b3822a",  # The coordinate grid below shows a parabola. What are the coordinates o
    "e908ebde-7db3-4876-afea-87ad241c73f9",  # If \(\tan\beta = \frac{a}{b}\) where \(a > 0\), \(b > 0\), and \(0 < \
    "ea9475f2-2686-4fff-835e-24da014b8112",  # A rectangular prism has a length of 12 cm, a width of 8 cm, and a heig
    "ebe7d8cf-8e54-4790-8652-314a2db3b525",  # A school council selects 4 officers from 30 eligible students: a chair
    "ec0ff31c-386b-4ffa-a748-2d984b5254d1",  # In the figure below, a rectangular paddock in Queensland has length (3
    "ed7ed5a9-1186-46b2-a996-e923eebe9f11",  # A boomerang is launched at a speed of 20 m/s at an angle of 60° above 
    "f09575cd-4db2-4c86-a847-16321f9d2228",  # A farmer has 200 metres of fencing to enclose a rectangular paddock. W
    "f27e9ff9-0be7-44a7-8e79-2a8f9c956021",  # A surveyor in Melbourne stands at point X and observes the top of a bu
    "f341c3aa-dc96-470c-83f8-1bca1da9e8f1",  # In the figure below, a ramp rises from point B on level ground to poin
    "f4b12900-db68-432f-a144-9c302d58fa2a",  # A rectangular room in a Melbourne apartment is 6 metres longer than it
    "faea914a-1940-4265-ba38-067a29e1970d",  # A rectangular cricket oval practice net is 5 metres longer than it is 
    "fd01b2b9-b9c9-42b2-a27a-8fc809850cfe",  # In the right triangle below, what is the value of tan θ?
    "fd18f338-b02b-40f8-a989-f18f8e56aa60",  # The length of a side of a square is represented as (2x + 3) centimetre
    "fd6cb2fe-9c69-4794-8d0d-3ccb155b0b04",  # Simplify the expression: 7x² − 3x + 2 − (5x² + 8x − 1)
    "fdd0913c-00e2-421c-8e4d-e52c23ef65ad",  # The diagram below shows triangle PQR with the dimensions as labelled. 
    "ffbcdd06-ab8e-4eaa-9db9-438a7c44392e",  # A function is defined by g(x) = 3x² − 5x + 2. What is the value of g(−
]

EXCLUDE_IDS = {qid: reason for qid, reason in EXCLUDE}
KEEP_IDS = set(KEEP)


def fetch(conn: sqlite3.Connection) -> list[dict]:
    conn.row_factory = sqlite3.Row
    return [
        dict(r)
        for r in conn.execute(
            "SELECT id, stem, option_a, option_b, option_c, option_d, correct_answer, "
            "explanation, topic, source_book, review_status FROM questions "
            "WHERE subject = 'quantitative_reasoning' AND review_status != 'rejected' "
            "ORDER BY id"
        )
    ]


def candidate_group(row: dict) -> str | None:
    blob = " ".join(str(row.get(f) or "") for f in FIELDS)
    for group, pattern in CANDIDATES:
        if re.search(pattern, blob, re.I):
            return group
    return None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", action="store_true", help="Counts by group and verdict")
    ap.add_argument("--unadjudicated", action="store_true", help="Candidates nobody has ruled on")
    ap.add_argument("--sample", type=int, default=0, help="Print N excluded items per reason group")
    ap.add_argument("--manifest", action="store_true", help="Write the excluded id list to JSON")
    args = ap.parse_args()

    conn = sqlite3.connect(DB_PATH)
    rows = fetch(conn)
    cands = [(r, g) for r in rows for g in [candidate_group(r)] if g]

    excluded = [(r, g) for r, g in cands if r["id"] in EXCLUDE_IDS]
    kept = [(r, g) for r, g in cands if r["id"] in KEEP_IDS]
    unruled = [(r, g) for r, g in cands if r["id"] not in EXCLUDE_IDS and r["id"] not in KEEP_IDS]

    if args.report or not any([args.unadjudicated, args.sample, args.manifest]):
        print(f"pool (non-rejected QR)   {len(rows)}")
        print(f"candidates flagged       {len(cands)}")
        print(f"  excluded (beyond Y8)   {len(excluded)}")
        print(f"  kept (in scope)        {len(kept)}")
        print(f"  UNADJUDICATED          {len(unruled)}")
        by_group: dict[str, list[int]] = {}
        for r, g in cands:
            slot = by_group.setdefault(g, [0, 0, 0])
            slot[0 if r["id"] in EXCLUDE_IDS else 1 if r["id"] in KEEP_IDS else 2] += 1
        print(f"\n{'group':<12}{'excl':>6}{'keep':>6}{'?':>6}")
        for g, (e, k, u) in sorted(by_group.items(), key=lambda kv: -sum(kv[1])):
            print(f"{g:<12}{e:>6}{k:>6}{u:>6}")
        reasons: dict[str, int] = {}
        for r, _ in excluded:
            reasons[EXCLUDE_IDS[r["id"]]] = reasons.get(EXCLUDE_IDS[r["id"]], 0) + 1
        print("\nexclusion reasons:")
        for reason, n in sorted(reasons.items(), key=lambda kv: -kv[1]):
            print(f"  {n:>3}  {reason}")
        live = sum(1 for r, _ in excluded if r["review_status"] == "approved")
        print(f"\n{live} of the {len(excluded)} excluded are approved and would otherwise be pushed.")

    if args.unadjudicated:
        print(f"{len(unruled)} candidate(s) with no verdict:")
        for r, g in unruled:
            print(f"  [{g}] {r['id']}  {' '.join(r['stem'].split())[:100]}")

    if args.sample:
        seen: dict[str, int] = {}
        for r, _ in excluded:
            reason = EXCLUDE_IDS[r["id"]]
            seen[reason] = seen.get(reason, 0) + 1
            if seen[reason] > args.sample:
                continue
            print(f"\n[{reason}] {r['topic']} | {r['source_book']} | {r['review_status']}")
            print("  Q:", " ".join(r["stem"].split())[:220])
            print("  E:", " ".join((r["explanation"] or "").split())[:180])

    if args.manifest:
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "generated_from": "tools/qr_beyond_year8.py",
            "method": "keyword candidates, then one human verdict per question",
            "excluded": [
                {
                    "id": r["id"],
                    "reason": EXCLUDE_IDS[r["id"]],
                    "stem": " ".join(r["stem"].split())[:160],
                    "topic": r["topic"],
                    "source_book": r["source_book"],
                    "review_status": r["review_status"],
                }
                for r, _ in excluded
            ],
        }
        MANIFEST.write_text(json.dumps(payload, indent=2))
        print(f"wrote {MANIFEST} ({len(excluded)} excluded)")


if __name__ == "__main__":
    main()
