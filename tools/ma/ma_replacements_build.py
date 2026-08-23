#!/usr/bin/env python3
"""Replacement mathematics questions for holes left in dealt drill forms.

Same contract as tools/qr/qr_replacements_build.py and tools/vr/vr_replacements_build.py:
each item names the form it fills, every key is computed twice by genuinely different
routes, and REPL_FORMS selects which wave to write so a reload cannot re-offer questions
already in the bank.
"""
import datetime
import json
import os
import pathlib
import sys
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

GEN = ROOT / "run_data/output/mathematics/generated"
BOOK = "ma_nsw_replacements"
NOW = datetime.datetime(2026, 8, 23, 9, 0, 0, tzinfo=datetime.timezone.utc) \
    .isoformat().replace("+00:00", "Z")

ITEMS = []


def Q(topic, stem, key, verify, wrong, expl, target_form, difficulty="medium",
      confidence=0.93, fmt=str):
    if key != verify:
        raise AssertionError(f"{topic}: routes disagree — key={key!r} verify={verify!r}")
    if len(wrong) != 3:
        raise ValueError(f"{topic}: need exactly 3 distractors")
    opts = [fmt(key)] + [fmt(v) for v, _ in wrong]
    if len(set(opts)) != 4:
        raise AssertionError(f"{topic}: options collide: {opts}")
    ITEMS.append({
        "id": str(uuid.uuid4()), "subject": "mathematics", "stem": stem,
        "option_a": opts[0], "option_b": opts[1], "option_c": opts[2], "option_d": opts[3],
        "correct_answer": "A", "explanation": expl, "topic": topic,
        "difficulty": difficulty, "confidence": confidence, "source_book": BOOK,
        "source_page": 1,
        "source_page_description": f"Replacement for a withdrawn item in {target_form}",
        "passage": None, "figure_svg": None, "review_status": "pending",
        "created_at": NOW, "_target_form": target_form,
        "_errors": {fmt(v): cls for v, cls in wrong},
    })


# ---------------------------------------------------------------- wave 1: math-001
# Replaces "Why would you add zero pairs to a counter model?", flagged in the first NSW
# review round as "quite difficult for a year 6". The deeper fault is that it is not a
# maths question: it tests whether a student was taught integers with a particular
# classroom manipulative, so a student who understands integer arithmetic perfectly but
# met it another way is marked wrong for their teacher's choice of materials.
#
# The replacement tests the same skill -- signed addition and subtraction in sequence --
# with nothing but numbers and a situation.
_start, _rise, _fall = -4, 11, 9
Q("Year 7: Operations with Integers",
  "The temperature at Cooma was −4°C at 6 am. By midday it had risen 11 degrees, "
  "and by midnight it had fallen 9 degrees from its midday reading. What was the "
  "temperature at midnight?",
  key=_start + _rise - _fall,
  verify=(_start - _fall) + _rise,      # route 2: take the fall off first, then the rise
  wrong=[(_start - _rise + _fall, "treats the rise as a fall and the fall as a rise"),
         (_start + _rise + _fall, "adds the 9 degrees instead of subtracting them"),
         (-_start + _rise - _fall, "starts from +4 instead of −4")],
  expl="Start at −4 and add the 11 degree rise to reach 7°C at midday, then take off "
       "the 9 degree fall: 7 − 9 = −2°C. Doing it in the other order gives the same "
       "answer: −4 − 9 = −13, then −13 + 11 = −2. Answering −6°C swaps the two "
       "movements, taking the 11 off and adding the 9. 16°C adds the fall instead of "
       "subtracting it. 6°C starts from +4 rather than −4.",
  target_form="nsw-drill-math-001",
  # A minus sign, not a hyphen — the stem uses U+2212 and an option that disagrees with
  # its own stem looks like two different questions.
  fmt=lambda v: f"{v}°C".replace("-", "\u2212"))


if __name__ == "__main__":
    GEN.mkdir(parents=True, exist_ok=True)
    want = {f.strip() for f in os.environ.get("REPL_FORMS", "").split(",") if f.strip()}
    items = [i for i in ITEMS if not want or i["_target_form"] in want]
    if want and not items:
        raise SystemExit(f"REPL_FORMS matched nothing: {sorted(want)}")
    nn = int(os.environ.get("REPL_PAGE", 1))
    path = GEN / f"{BOOK}_p{nn}.json"
    path.write_text(json.dumps(items, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(items)} replacement questions -> {path}")
    for it in items:
        print(f"   {it['_target_form']}  {it['topic']}")
        print(f"      {' '.join(it['stem'].split())[:100]}")
        print(f"      " + "  ".join(f"{L.upper()}) {it['option_'+L]}" for L in "abcd"))
