#!/usr/bin/env python3
"""Round 14: the four comments on the round 13 compare pages.

The reviewer went through both pages. 51 of the 55 cards carry no comment, which is a
pass. The four below are approved and live, so nothing here reaches a student until it
is pushed.

Two of the four are round 13's own repairs coming back. d4096e9a's dots and 9ad41d04's
picture were both written in round 13, in answer to earlier notes.

Every question's full check state is compared before and after, and a repair that would
make any check newly fire is refused rather than written.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_round14_flags
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_round14_flags --apply
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.repair_vic_round12_flags import FIELDS, findings      # noqa: E402
from tools.repair_vic_round13_flags import DB                    # noqa: E402

RECORD = ROOT / "run_data/output/round14_flags.json"
REVIEWS = [ROOT / "review/ui/question-review-nsw-uiflags-2026-10-11-2026-10-31.json",
           ROOT / "review/ui/question-review-vic-uiflags-2026-10-11-2026-10-25.json"]


def f_d1975740(q):
    """'Replace the text for each answer with the corresponding symbol.'"""
    return {"option_a": "×", "option_b": "+", "option_c": "−", "option_d": "÷",
            "explanation": "24 ÷ 6 = 4. The others do not work: 24 × 6 = 144, "
                           "24 + 6 = 30 and 24 − 6 = 18."}


def f_1e9739d8(q):
    """'The text of each number (and the centimetres text) are too far from the line
    they represent.' The numbers stay at their own tick's x, so the scale is unchanged,
    and only come up the page. They used to sit 17 px under a short tick. The long ticks
    at 0, 5 and 10 would hit the raised row, so they are shortened, and the ruler's lower
    edge comes up with the numbers. 'centimetres' moves up under the ruler and is centred
    on it; it was 8 px left of centre."""
    svg = q["figure_svg"]
    long_ticks = ('<path d="M26 120 L26 142"', '<path d="M131 120 L131 142"',
                  '<path d="M236 120 L236 142"')
    for tick in long_ticks:
        assert svg.count(tick) == 1
        svg = svg.replace(tick, tick.replace(" 142", " 137"))
    assert svg.count('y="156"') == 6
    svg = svg.replace('y="156"', 'y="148"')
    assert svg.count('height="40"') == 1
    svg = svg.replace('height="40"', 'height="34"')
    assert svg.count('<text x="170" y="190"') == 1
    svg = svg.replace('<text x="170" y="190"', '<text x="162.5" y="168"')
    return {"figure_svg": svg}


def f_d4096e9a(q):
    """'The repeating decimal symbol is unclear and merged with the number 7.' Selectly
    prints a stem as plain text, so a mark stacked over a digit lands wherever the font
    puts it. The question does not need the mark: the dots after the digits and the
    words say which block repeats."""
    return {"stem": "What is the 143rd digit after the decimal point in the recurring "
                    "decimal 0.272727… (the digits 27 repeat forever)?"}


def f_9ad41d04(q):
    """'Revert back to original form because there is no need to create an image.' The
    expression goes back into the stem and the picture is removed. The options and the
    explanation keep round 13's wording: the original explanation's middle step
    (-y/(-(x-y))) was wrong, and the options match this stem's minus signs."""
    return {"stem": "Simplify the expression: x/(x − y) − y/(y − x)", "figure_svg": None}


REPAIRS = {"d1975740": f_d1975740, "1e9739d8": f_1e9739d8,
           "d4096e9a": f_d4096e9a, "9ad41d04": f_9ad41d04}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    record, refused = [], []
    for path in REVIEWS:
        for item in json.loads(path.read_text())["items"]:
            qid, short = item["id"], item["id"][:8]
            row = dict(con.execute("SELECT * FROM questions WHERE id=?", (qid,)).fetchone())
            before = findings(row)
            after_row = {**row, **REPAIRS[short](row)}
            after = findings(after_row)
            print(f"{short} before={sorted(before)} after={sorted(after)}")
            if after - before:
                refused.append((short, f"would newly fire {sorted(after - before)}"))
                continue
            touched = [k for k in FIELDS if after_row.get(k) != row.get(k)]
            record.append({"id": qid, "form": item["form"], "note": item["note"],
                           "fields": touched, "why": REPAIRS[short].__doc__.strip(),
                           "cleared": sorted(before - after),
                           "before": {k: row.get(k) for k in touched},
                           "after": {k: after_row.get(k) for k in touched}})
            if args.apply:
                sets = ", ".join(f"{k}=?" for k in touched)
                con.execute(f"UPDATE questions SET {sets} WHERE id=?",
                            [after_row[k] for k in touched] + [qid])
    if args.apply:
        con.commit()
        RECORD.write_text(json.dumps(record, indent=1, ensure_ascii=False))
    con.close()
    print(f"{len(record)} repaired, {len(refused)} refused"
          f"{' (DRY RUN)' if not args.apply else ''}")
    for short, why in refused:
        print(f"  REFUSED {short}: {why}")
    return 1 if refused else 0


if __name__ == "__main__":
    raise SystemExit(main())
