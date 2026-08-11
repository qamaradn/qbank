#!/usr/bin/env python3
"""Rule on the 45 questions repair_key_skew refused to reorder.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.triage_blocked --dry-run
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.triage_blocked --apply

repair_key_skew blocked these because reordering a broken question only moves the
breakage. Its manifest listed them for a human; this records the ruling and applies it.
Every one was read, and where the maths was checkable it was recomputed rather than
taken from the explanation -- which is the whole problem with these rows.

WHY SO MANY ARE REJECTED

Four failure modes, and only the last is recoverable:

  the key is one of a duplicated pair       a student choosing the identical option is
                                            marked wrong; there is no right answer to
                                            restore without rewriting the question

  two options are the same VALUE            5√2 and 10/√2; 1/2 and 3/6; 17 and √289.
                                            Two correct answers, and picking which one
                                            "counts" is a rewrite, not a repair

  the explanation abandons its own working  and either names a different answer than the
                                            stored key, or silently changes the question's
                                            own numbers to make one come out. Precedent is
                                            tools/repair_leaked_working.py, where every
                                            contradiction checked by hand had the working
                                            right and the key wrong

  the explanation merely leaked editing     but the maths is sound and the key survives
                                            recomputation -- these are cleaned and kept

Two were false positives of the blocker and are kept untouched: one whose correct option
IS "Both A and C" (a legitimate item that simply must never be reordered), and one whose
explanation names coordinate-geometry POINTS A and B, not options.

Nothing is deleted. review_status is reversible and the full prior state of every row is
written to run_data/output/blocked_triage.json.
"""
import argparse
import json
import pathlib
import sqlite3
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DB = ROOT / "run_data/db/qbank.db"
MANIFEST = ROOT / "run_data/output/key_skew_manifest.json"
REPORT = ROOT / "run_data/output/blocked_triage.json"

# id prefix -> (ruling, note). Everything in the blocked list not named here is rejected,
# with the reason carried over from the blocker.
KEEP_CLEANED = {
    "689361ad": ("12 marbles, 4 blue, so P(not blue) = 8/12 = 2/3, which is the stored "
                 "key D. Only the explanation was faulty: it admitted replacing an option.",
                 "A bag of 12 holds 4 blue marbles, so 8 are not blue and the probability "
                 "is 8/12, which simplifies to 2/3. The nearby 1/3 is the probability of "
                 "drawing a green marble rather than a non-blue one."),
    "24d7ff02": ("(240-2w)(180-2w) = 21600 reduces to w^2 - 210w + 5400 = 0, giving "
                 "w = 30 or 180; 180 is impossible, so 30 m is right and matches key C.",
                 "Half the paddock is 240 x 180 / 2 = 21600 m squared, so "
                 "(240 - 2w)(180 - 2w) = 21600. This reduces to w squared - 210w + 5400 = 0, "
                 "whose solutions are w = 30 and w = 180. A border of 180 m would be wider "
                 "than the paddock, so w = 30 m. The 25 m option comes from halving only "
                 "one dimension rather than the area."),
    "4fde8984": ("f(-4) > f(4) holds only for 8 - x^3: 72 against -56. The two even "
                 "functions are equal at plus and minus 4 and the constant is flat. Key C "
                 "stands; the explanation enumerated the options by letter.",
                 "Only an odd power distinguishes -4 from 4. For 8 - x cubed, f(-4) = 72 "
                 "while f(4) = -56. Both 8x squared and x to the fourth plus 8 are even "
                 "functions and give the same value at -4 and 4, and the constant function "
                 "8 never changes at all, so none of those three can satisfy the inequality."),
    "64da4e4d": ("In slope-intercept form the gradients are 3, 6, 2.5 and 4, so 4y = 24x - 8 "
                 "has the greatest at 6, matching key B. The explanation listed the options "
                 "by letter.",
                 "Rearranging each into slope-intercept form gives gradients of 3, 6, 2.5 "
                 "and 4. The line written as 4y = 24x - 8 becomes y = 6x - 2, so its "
                 "gradient of 6 is the largest. The line y = 4x - 1 is the closest rival at "
                 "4, and is easy to pick if the others are not rearranged first."),
}

KEEP_UNTOUCHED = {
    "f6bf96e9": "False positive. The correct option IS 'Both A and C', and A and C really "
                "are the same parabola, so the item is sound. It must never be reordered, "
                "because its own option text names option letters.",
    "f488d2ef": "False positive. A and B in the explanation are coordinate-geometry POINTS "
                "from the stem, not option letters, so nothing was wrong with the item.",
}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", default=str(DB))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    blocked = json.loads(pathlib.Path(MANIFEST).read_text())["blocked"]
    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row

    rulings = []
    for b in blocked:
        short = b["id"][:8]
        row = conn.execute("SELECT * FROM questions WHERE id=?", (b["id"],)).fetchone()
        if row is None:
            rulings.append({"id": b["id"], "ruling": "missing_from_db"})
            continue
        before = {"review_status": row["review_status"], "explanation": row["explanation"]}
        if short in KEEP_CLEANED:
            why, expl = KEEP_CLEANED[short]
            rulings.append({"id": b["id"], "short": short, "ruling": "keep_cleaned",
                            "blocker_reason": b["reason"], "why": why,
                            "before": before, "after": {"explanation": expl}})
        elif short in KEEP_UNTOUCHED:
            rulings.append({"id": b["id"], "short": short, "ruling": "keep_untouched",
                            "blocker_reason": b["reason"], "why": KEEP_UNTOUCHED[short],
                            "before": before, "after": {}})
        else:
            rulings.append({"id": b["id"], "short": short, "ruling": "reject",
                            "blocker_reason": b["reason"],
                            "why": f"blocked as {b['reason']}; not recoverable without "
                                   f"rewriting the question",
                            "before": before, "after": {"review_status": "rejected"}})

    counts = {}
    for r in rulings:
        counts[r["ruling"]] = counts.get(r["ruling"], 0) + 1
    print(f"blocked questions: {len(rulings)}")
    for k, v in sorted(counts.items()):
        print(f"  {k:16s} {v}")
    print("\n  rejected by blocker reason:")
    by = {}
    for r in rulings:
        if r["ruling"] == "reject":
            by[r["blocker_reason"]] = by.get(r["blocker_reason"], 0) + 1
    for k, v in sorted(by.items()):
        print(f"    {k:28s} {v}")
    approved = [r for r in rulings
                if r["ruling"] == "reject" and r["before"]["review_status"] == "approved"]
    print(f"\n  of the rejected, currently APPROVED and being served: {len(approved)}")

    if not args.apply:
        print("\n  --dry-run: nothing written. Re-run with --apply to commit.")
        return 0

    with conn:
        for r in rulings:
            a = r.get("after") or {}
            if "review_status" in a:
                conn.execute("UPDATE questions SET review_status=?, reviewed_at=? WHERE id=?",
                             (a["review_status"], datetime.now(timezone.utc).isoformat(), r["id"]))
            if "explanation" in a:
                conn.execute("UPDATE questions SET explanation=? WHERE id=?",
                             (a["explanation"], r["id"]))
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({
        "tool": "triage_blocked",
        "written_at": datetime.now(timezone.utc).isoformat(),
        "counts": counts, "rulings": rulings}, indent=1, ensure_ascii=False))
    print(f"\n  applied. record -> {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
