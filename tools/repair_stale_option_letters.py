"""Fix explanations that name an option letter the answer-key repair moved.

`repair_key_skew.py` reordered the options of 2,734 questions in August to break a
"always answer C" cheat that scored 48%. It updated `correct_answer` and it recorded the
exact permutation per question — but it did not rewrite the EXPLANATIONS, which go on
saying "Option A is correct" about an option that is now B.

Measured over the served VIC scope: 99 explanations name a specific letter and **53 of
them contradict the stored key**. That is student-visible. The app marks B correct and
the explanation underneath says the answer is A.

IT LOOKED MECHANICALLY REPAIRABLE AND IT IS NOT. The manifest holds `mapping` — old
letter to new letter — for every question the shuffle touched, so translating the letters
inside the explanation ought to restore what the sentence meant. Measured over the 87
questions that were shuffled AND name exactly one letter:

    applying the mapping forward   fixes 24, leaves 63 still contradicting
    applying it inverted           fixes 20, leaves 67
    doing nothing                  38 already agree, 49 do not

No direction restores consistency, which means the letters were **already unreliable
before the shuffle** — the same generation defect that put the model's own working into
139 explanations and produced 42 wrong keys. The shuffle exposed the problem; it did not
create it.

So this tool does NOT rewrite. Guessing a letter would put a confident wrong sentence in
front of a student, which is worse than the stale one. It classifies and hands the
contradictions to the reading pass:

  agrees        the letter matches the key. Left alone — with fixed forms the option order
                is stable, so a correct letter reference is harmless.
  contradicts   the explanation asserts a different answer than the key. Cannot be settled
                without reading the question, so it is listed for that pass.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_stale_option_letters --dry-run
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_stale_option_letters --apply
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "run_data" / "db" / "qbank.db"
MANIFEST = REPO_ROOT / "run_data" / "output" / "stale_option_letters.json"
SKEW = [REPO_ROOT / "run_data" / "output" / "key_skew_manifest.json",
        REPO_ROOT / "run_data" / "output" / "key_skew_verbal_manifest.json"]

OPTION_REF = re.compile(r'\b([Oo]ption\s+)([A-D])\b')


def mappings() -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for path in SKEW:
        if not path.exists():
            continue
        for ch in json.loads(path.read_text()).get("changes", []):
            if ch.get("mapping"):
                out[ch["id"]] = ch["mapping"]
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    if not (args.dry_run or args.apply):
        ap.error("choose --dry-run or --apply")

    maps = mappings()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute(
        "SELECT id, source_book, correct_answer, explanation FROM questions "
        "WHERE review_status != 'rejected' AND explanation IS NOT NULL")]

    contradicts, agrees = [], 0
    for r in rows:
        expl = r["explanation"]
        letters = {m.group(2) for m in OPTION_REF.finditer(expl)}
        if not letters:
            continue
        if r["correct_answer"] in letters:
            agrees += 1
        else:
            contradicts.append({"id": r["id"], "book": r["source_book"],
                                "key": r["correct_answer"], "letters": sorted(letters),
                                "was_shuffled": r["id"] in maps,
                                "explanation": " ".join(expl.split())[:200]})

    shuffled = sum(1 for x in contradicts if x["was_shuffled"])
    print(f"explanations naming an option letter: {agrees + len(contradicts)}")
    print(f"  letter agrees with the key   : {agrees}")
    print(f"  letter CONTRADICTS the key   : {len(contradicts)}  "
          f"({shuffled} were shuffled, {len(contradicts) - shuffled} never were)")
    print("\n  Not repaired here — see the module docstring. Listed for the reading pass.")
    for u in contradicts[:6]:
        print(f"    [{u['book']}] says {u['letters']}, key {u['key']}  {u['explanation'][:80]}")

    if args.apply:
        MANIFEST.write_text(json.dumps(
            {"generated_from": "tools/repair_stale_option_letters.py",
             "applied_at": datetime.now(timezone.utc).isoformat(),
             "note": "classification only; no explanation was rewritten",
             "needs_reading": contradicts}, indent=2))
        print(f"\nwrote the read list ({len(contradicts)}) -> {MANIFEST}")


if __name__ == "__main__":
    main()
