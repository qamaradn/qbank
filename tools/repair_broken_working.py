"""Act on quantitative questions whose explanation shows the model failing, not solving.

The 2026-08-04 sweep (`repair_leaked_working.py`) caught 139 questions carrying the
generating model's scratchpad and established the rule that mattered: **where the working
and the key disagree, the working is right and the key is wrong.** Its patterns then went
into `question_checks.LEAKED_WORKING`.

Thirteen questions slipped through, found on 2026-08-12 while reading the quantitative
bank for the beyond-Year-8 filter. They slipped through because the pattern required
`actually,` to be followed by "I"/"let me"/"the answer", so a bare "Actually 1090/6 =
181.6" did not match, and because it had no word for the worst class of all:

**The model rewriting the question inside the explanation.** Five of these say, in the
stored explanation, things like *"Re-setting options so correct is A"*, *"I'll just set a
problem where w=2 works cleanly"*, *"Change to: 2x80 degrees"*, *"Redesign question with
clean answer"*. That is not a model correcting its arithmetic — it is a model that could
not make the question it had just written work, and edited the question in its head while
the stem and options on disk stayed broken. Every one of those five is unanswerable as
stored. This is a strictly stronger signal than self-correction and now has its own check.

What reading all thirteen decided:

- **8 rejected** — no option is correct as the question stands. Four are the rewrite class
  above; the others are a mean of 1.67 offered against "increased by 2", an average speed
  of 66.25 km/h with no 66 option, a "which CANNOT" where all four options can, and a
  hexagon whose stated angles force the remaining two to be 180 degrees.
- **2 re-keyed** — the working was right and the key was wrong, exactly as in August.
  750/20 = 37.5 rounds to 38 (was keyed 37); 1+2+3+4 = 10 cm squared (was keyed 16).
- **3 explanations cleaned** — key correct, prose corrupt. One of these is approved and
  live. Its figure was rendered and read before trusting it: horizontals 7+3 = 10 and
  verticals 4+3 = 7, so the perimeter of 34 m is right.

Widening the pattern then found seven more, of which four needed action and three were
false positives worth keeping in mind: two compound-interest items whose stems ask which
value is *closest*, so settling for the nearest option is the question rather than a
failure, and a verbal item explaining that "retain" means "to hold on to what you already
have" — where "hold on" is ordinary English, not a model stalling. The `hold on` rule now
excludes "hold on to".

Nothing here is inferred from a pattern match. Every verdict is a per-question decision
with the arithmetic that settled it, and `--dry-run` prints all of them before writing.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_broken_working --dry-run
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_broken_working --apply
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "run_data" / "db" / "qbank.db"
MANIFEST = REPO_ROOT / "run_data" / "output" / "broken_working_repairs.json"

# (id, why) -- no option is correct as the question stands.
REJECT: list[tuple[str, str]] = [
    ("72fa1a19-03b1-4809-ba89-08f251fe825a",
     "285 km in 3h20 is 85.5 km/h; at 90.5 km/h the trip takes 188.95 min, a saving of "
     "11.05 min. The options are 20, 10, 25 and 15, and the stem does not say "
     "'approximately'. No option is correct as asked."),
    ("277f95ec-7ba8-4ed1-8818-c3b81da6a28a",
     "Mean moves 180 -> 181.67, a change of +1.67. Options offer 'increased by 2' with no "
     "'approximately' in the stem. No option is correct as asked."),
    ("341528d8-84a0-435f-9646-d022836471e3",
     "'150% loading' is defined in the stem as 250% of base ($277.50) but $166.50, the "
     "standard Australian award reading of the same phrase, is also an option. The item "
     "tests which reading of an ambiguous term the writer meant, not arithmetic."),
    ("ab9affe3-1f54-45ad-a50d-f7bb736b21f0",
     "'Which CANNOT be one of those integers' -- but 9x23=207, 11x19=209, 14x15=210 and "
     "17x12=204 are all between 200 and 215. All four options can. No correct answer."),
    ("4ce30f0e-8d2c-418b-bc28-ae288a2ea004",
     "GCF(p^3q^2, p^2q^4) = p^2q^2 = 108, which has no positive integer solution because "
     "108 is not a perfect square. The explanation flails for a paragraph and then names "
     "option D while the key is A."),
    ("f75f45ca-5033-485c-9fc2-ae3e4533c45c",
     "55/165 = 1/3, and BOTH option A (5/15) and option C (11/33) equal 1/3. The key is B "
     "(1/5), which is wrong, and the question has two correct options besides."),
    ("a4ab458e-82cf-4856-ac84-de450a632acc",
     "265 km / 4 h = 66.25 km/h, which to the nearest km/h is 66. The options are 63, 70, "
     "65 and 67. No option is correct; the explanation settles for 'closest'."),
    ("6ac6acc3-9ae5-4855-b5d1-ba2bbc8ee265",
     "A hexagon sums to 720. The stem's 2x75 + 2x105 = 360 forces the remaining two angles "
     "to 180 each, which are straight lines, not angles. The stem is impossible; the "
     "explanation reaches the keyed 150 only by inventing different given angles."),
    ("4fca89ae-7aaf-4a9d-b7a5-f451a12eff99",
     "Border 52 m^2 on a 10x6 pool gives w^2+8w-13 = 0, w = 1.44 -- irrational, and the key "
     "is 1. The explanation ends 'I'll just set a problem where w=2 works cleanly', which "
     "was never done to the stored stem."),
    ("1f94455c-b94c-4914-94d3-1b3ba3fe77d1",
     "(25+2w)(10+2w) = 504 gives w = 3.08. The key is 3, and w=3 gives 31x16 = 496, not "
     "504. The explanation tries five replacement pools and ends 'Redesign question with "
     "clean answer', which was never done to the stored stem."),
]

# (id, new_key, why) -- the working was right and the key was wrong.
REKEY: list[tuple[str, str, str]] = [
    ("6631df7f-35b2-449a-867a-d00a62618085", "D",
     "5000 x 1.15^2 = 6612.5, and option D is 6612. The explanation talks itself into "
     "believing no option matches while D sits in front of it. Was keyed B (6750), which "
     "is neither the compound nor the simple-interest answer."),
    ("b49b2c69-d8a8-4bee-8ccf-e1cb8e4ef338", "C",
     "Over the 5 years from the start of 2010, maths rises 2.4/year from 4 and science "
     "3.6/year from 2. They meet when 4 + 2.4t = 2 + 3.6t, so t = 5/3 years, about "
     "September 2011 = option C. The explanation reaches 2011 and the key says 2012."),
    ("7162daf3-8eb8-49c5-92bb-e59958b29daf", "B",
     "Shape A gives L + 2W = 30, which BOTH option A (14+16) and option B (16+14) satisfy "
     "-- so Shape A cannot decide it. Shape B adds 2W to the perimeter: 74 - 60 = 14 = 2W "
     "gives W = 7 and L = 16, option B. Option A would need 2W = 16 and a perimeter of 76. "
     "The explanation reaches B and the key says A."),
    ("5f486830-d3ec-4581-989f-6a5916f8d80e", "B",
     "(20x3 + 30x5 + 40x7 + 50x4 + 60x1) / 20 = 750/20 = 37.5, and the stem asks to the "
     "nearest kilometre, so 38 km = option B. Was keyed A (37)."),
    ("ab970adf-441a-4ad2-87ad-a92a1f77aa73", "D",
     "Rows 1-4 hold 1, 2, 3 and 4 black squares of 1 cm^2 each, so 10 cm^2 = option D. "
     "Was keyed C (16)."),
]

# (id, replacement explanation) -- key correct, prose corrupt.
CLEAN: list[tuple[str, str]] = [
    ("84f36f4b-be4d-485e-9549-a588c37dc3b5",
     "Factorise: x² − 6x − 40 = (x − 10)(x + 4), since −10 × 4 = −40 and −10 + 4 = −6. "
     "Setting each factor to zero gives x = 10 or x = −4."),
    ("723e52c3-ae85-46ad-a288-2167c4b670cb",
     "For a rectilinear figure, add every labelled edge once: 10 (bottom) + 7 (right) + 7 "
     "(top) + 3 (step across) + 3 (step down) + 4 (left) = 34 m. The labels are consistent "
     "with a 10 by 7 outline, since the horizontals 7 + 3 total the bottom's 10 and the "
     "verticals 4 + 3 total the right side's 7."),
]

REKEY_MAP = {qid: (key, why) for qid, key, why in REKEY}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="Print every change, write nothing")
    ap.add_argument("--apply", action="store_true", help="Write the changes and the manifest")
    args = ap.parse_args()
    if not (args.dry_run or args.apply):
        ap.error("choose --dry-run or --apply")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    now = datetime.now(timezone.utc).isoformat()
    record: list[dict] = []

    for qid, why in REJECT:
        row = conn.execute("SELECT * FROM questions WHERE id = ?", (qid,)).fetchone()
        if row is None:
            print(f"MISSING {qid}")
            continue
        if row["review_status"] == "rejected":
            print(f"\nREJECT {qid} -- already rejected, skipping")
            continue
        print(f"\nREJECT {qid} [{row['review_status']}]\n  {' '.join(row['stem'].split())[:120]}\n  why: {why}")
        record.append({"id": qid, "action": "reject", "was": row["review_status"], "why": why})
        if args.apply:
            conn.execute(
                "UPDATE questions SET review_status = 'rejected', reviewed_at = ? WHERE id = ?",
                (now, qid),
            )

    for qid, new_key, why in REKEY:
        row = conn.execute("SELECT * FROM questions WHERE id = ?", (qid,)).fetchone()
        if row is None:
            print(f"MISSING {qid}")
            continue
        if row["correct_answer"] == new_key:
            print(f"\nREKEY  {qid} -- already keyed {new_key}, skipping")
            continue
        print(f"\nREKEY  {qid} [{row['review_status']}] {row['correct_answer']} -> {new_key}"
              f"\n  {' '.join(row['stem'].split())[:120]}\n  why: {why}")
        record.append({"id": qid, "action": "rekey", "was": row["correct_answer"],
                       "now": new_key, "why": why})
        if args.apply:
            conn.execute(
                "UPDATE questions SET correct_answer = ?, explanation = ?, edited = 1 WHERE id = ?",
                (new_key, why, qid),
            )

    for qid, text in CLEAN:
        row = conn.execute("SELECT * FROM questions WHERE id = ?", (qid,)).fetchone()
        if row is None:
            print(f"MISSING {qid}")
            continue
        if (row["explanation"] or "") == text:
            print(f"\nCLEAN  {qid} -- already clean, skipping")
            continue
        print(f"\nCLEAN  {qid} [{row['review_status']}]\n  was: {' '.join((row['explanation'] or '').split())[:150]}"
              f"\n  now: {text[:150]}")
        record.append({"id": qid, "action": "clean_explanation",
                       "was": row["explanation"], "now": text})
        if args.apply:
            conn.execute(
                "UPDATE questions SET explanation = ?, edited = 1 WHERE id = ?", (text, qid)
            )

    if args.apply:
        conn.commit()
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        prior = []
        if MANIFEST.exists():
            prior = json.loads(MANIFEST.read_text()).get("repairs", [])
        MANIFEST.write_text(json.dumps(
            {"generated_from": "tools/repair_broken_working.py", "applied_at": now,
             "repairs": prior + record}, indent=2))
        print(f"\nApplied {len(record)} repairs. Record: {MANIFEST}")
    else:
        print(f"\nDry run: {len(record)} repairs would be applied. Nothing written.")


if __name__ == "__main__":
    main()
