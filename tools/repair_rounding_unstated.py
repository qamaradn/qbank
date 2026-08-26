#!/usr/bin/env python3
"""Say so when a question's answer needs rounding.

    "If the answer requires approximation or rounding, always mention it in the
     question for clarity."  -- VIC round 5

That note says ALWAYS, so it is a sweep, not a repair to one question. The instruction
is derived from the KEY's own format rather than applied uniformly, because the right
words differ: money rounds to the cent, a percentage given as 42.3% rounds to one
decimal place, and a count of whole tiles does not round at all.

WHAT IS SKIPPED, and why the blanket version would have been wrong:

  * a key that is a whole number in a stem asking "how many", "minimum number" or
    "whole" -- the answer is a count or a ceiling, exact by construction. One of these
    already tells the student "(Use π ≈ 3.14159)"; the ≈ is pi's, not the answer's.
  * a stem that already ends in an instruction of its own.

Nothing here changes a key, an option or an explanation. It appends one sentence to the
stem, and only where the stem does not already carry one.

Usage:
    python -m tools.repair_rounding_unstated --dry-run
    python -m tools.repair_rounding_unstated --apply
"""
import argparse
import json
import pathlib
import re
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import question_checks as qc      # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
MANIFEST = ROOT / "run_data/output/rounding_unstated_repairs.json"

_EXACT_BY_NATURE = re.compile(
    r"\bhow many\b|\bminimum number\b|\bmaximum number\b|\bwhole\b|\bhow many times\b",
    re.I)
_MONEY = re.compile(r"^\s*\$")
_DEC = re.compile(r"(\d+)\.(\d+)")


def instruction(key: str, stem: str):
    """The sentence to append, or None to leave the question alone."""
    k = (key or "").strip()
    if not k:
        return None
    m = _DEC.search(k)
    if _MONEY.match(k):
        if m and len(m.group(2)) == 2:
            return "Give your answer to the nearest cent."
        return "Give your answer to the nearest dollar."
    if m:
        places = len(m.group(2))
        word = {1: "one decimal place", 2: "two decimal places",
                3: "three decimal places"}.get(places)
        return f"Give your answer to {word}." if word else None
    if _EXACT_BY_NATURE.search(stem):
        return None                      # a count or a ceiling; nothing is being rounded
    if "%" in k:
        return "Give your answer to the nearest per cent."
    unit = re.sub(r"^[\d,.\s]+", "", k).strip()
    if unit and re.fullmatch(r"[A-Za-z°²³/ ]{1,14}", unit):
        return f"Give your answer to the nearest {unit.rstrip('s')}."
    if re.fullmatch(r"[\d,]+", k):
        return "Give your answer to the nearest whole number."
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not (args.apply or args.dry_run):
        raise SystemExit("pass --apply or --dry-run")

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute("SELECT * FROM questions")]
    targets = [r for r in rows if qc.rounds_without_saying_so(r)]

    done, skipped, failed = [], [], []
    for r in targets:
        key = r.get("option_" + (r["correct_answer"] or "a").lower())
        ins = instruction(key, r["stem"] or "")
        if ins is None:
            skipped.append((r, key))
            continue
        stem = (r["stem"] or "").rstrip()
        q = dict(r, stem=f"{stem} {ins}")
        # The check must actually fall silent, and nothing else may start firing.
        if qc.rounds_without_saying_so(q) or qc.no_question_asked(q):
            failed.append((r, ins))
            continue
        done.append((r, key, ins, q["stem"]))
        if args.apply:
            con.execute("UPDATE questions SET stem=? WHERE id=?", (q["stem"], r["id"]))

    print(f"{len(targets)} questions round without saying so")
    print(f"  instruction added : {len(done)}")
    print(f"  left alone        : {len(skipped)}")
    print(f"  refused           : {len(failed)}\n")
    for r, key, ins, _s in done[:14]:
        print(f"  {r['id'][:8]} key={key!r:12} -> {ins}")
    for r, key in skipped:
        print(f"  - {r['id'][:8]} key={key!r:12} left alone (exact by nature)")
    for r, ins in failed:
        print(f"  ! {r['id'][:8]} {ins}")

    if args.apply:
        con.commit()
        MANIFEST.write_text(json.dumps(
            [dict(id=r["id"], key=k, instruction=i, form_id=r["form_id"],
                  status=r["review_status"], old_stem=r["stem"], new_stem=s)
             for r, k, i, s in done], indent=1, ensure_ascii=False))
        print(f"\napplied {len(done)} — manifest {MANIFEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
