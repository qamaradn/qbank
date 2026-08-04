#!/usr/bin/env python3
"""Repair questions whose explanation leaked the generating model's own working.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_leaked_working --dry-run
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_leaked_working

TASK §7: "Write it clean — never leak working, self-correction, or 'wait, let me
recheck'." 139 questions breached it — 137 quantitative_reasoning and 2
science_reasoning, 12 of them already approved and serving students.

WHAT THE AUDIT FOUND

Leaked working turned out to be a symptom, not the disease. Comparing the working that
appears BEFORE the model's first self-correction against the answer actually stored:

    36  the explanation itself admits no option is correct ("none match", "not listed",
        "the closest is", "perhaps the question has a typo")
    43  the working computes a value matching a DIFFERENT option than the stored key
    42  neither the key nor another option appears verbatim — unverifiable mechanically
    18  the working agrees with the stored key

In every contradiction inspected by hand the working was right and the key was wrong:
0.5 x 80 x 45 = 1800 stored as 3600; 500 km / 5 h = 100 km/h stored as 110 km/h;
135 s x 7 = 15 min 45 s stored as 16 min 15 s. Two of those were approved.

WHAT THIS DOES

  reject   the 36 whose own explanation says no option is correct. They cannot be fixed
           by editing text — there is nothing to fix them to.
  requeue  anything approved that cannot be mechanically verified, back to 'pending'.
           An unverifiable question must stop being served while it waits for a human.
  fix key  the 43 where the working supports a different option, setting the answer to
           the option the working actually computes.
  clean    the explanation in every surviving case, by truncating at the model's first
           self-correction. The text before that hinge is the working that stands.

Nothing is deleted. review_status is reversible and every change is written to
run_data/output/leaked_working_repairs.json.
"""
import argparse
import json
import pathlib
import re
import sqlite3
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.question_checks import leaked_working  # noqa: E402

DB = ROOT / "run_data" / "db" / "qbank.db"
REPORT = ROOT / "run_data" / "output" / "leaked_working_repairs.json"

# The explanation conceding that the question has no correct option.
ADMITS_BROKEN = re.compile(
    r"not (listed|among|one of|an option)|none (match|of the options)|no option|"
    r"doesn'?t work|does not work|both options|same value|replacing option|"
    r"option .* should be|closest is|not exactly|if the .* (was|were) different|"
    r"assume the question|might be (slightly )?off|options might be|question parameters",
    re.I)

# Where the model stops asserting and starts arguing with itself. Everything before the
# FIRST hinge is the working that stands; everything after is scratchpad.
HINGE = re.compile(
    r"(^|[.!?;:—–]\s*)(wait|hold on|actually,|let me re-?\w+|let'?s re-?\w+|"
    r"my (mistake|apologies)|scratch that|on second thought|correction:|why did i)",
    re.I | re.M)

LETTERS = ["a", "b", "c", "d"]

# ── Hand-verified overrides ──────────────────────────────────────────────────────────
# Every explanation that argued with itself about WHICH option was right had the wrong
# answer stored. These five were worked through by hand; the mechanical matcher is not
# trusted with them, and two had no correct option at all so the options were repaired.
HAND_FIXES = {
    # 10 000 x 999 = 9 990 000. The working's own arithmetic slipped to 9 999 000, so the
    # matcher cannot be used here — the conclusion it would match is itself wrong.
    "9ee6234f-81c0-406a-899b-2cdf8771d8a1": {
        "correct_answer": "D",
        "explanation":
            "The smallest five-digit whole number is 10 000 and the largest three-digit "
            "whole number is 999, so the product is 10 000 x 999 = 10 000 000 - 10 000 = "
            "9 990 000. Answering 9 999 900 comes from multiplying by 9999 instead of 999.",
    },
    # P(3 red) = C(15,3)/C(25,3) = 455/2300 = 91/460, which was not among the four
    # options (150/741, 325/741, 13/35, 27/35).
    "a79ccd0e-6b7b-4fe6-8335-3fa06a96bdfd": {
        "option_a": "91/460", "option_b": "27/125", "option_c": "13/35", "option_d": "3/5",
        "correct_answer": "A",
        "explanation":
            "There are C(15,3) = 455 ways to choose 3 red marbles from 15, and C(25,3) = "
            "2300 ways to choose any 3 of the 25, so the probability is 455/2300 = 91/460. "
            "Answering 27/125 treats the draws as independent, which would only hold if "
            "each marble were put back before the next was drawn.",
    },
    # 112.5 m2 of fence / 4.32 m2 per sheet = 26.04, so 27 sheets. The stored options
    # were 5, 6, 7 and 8 — none of them reachable.
    "41a3287d-ce6c-48c4-8edd-3108a3e7c6bc": {
        "option_a": "26", "option_b": "27", "option_c": "28", "option_d": "38",
        "correct_answer": "B",
        "explanation":
            "The fence covers 2.5 m x 45 m = 112.5 square metres and each sheet covers "
            "1.2 m x 3.6 m = 4.32 square metres, so 112.5 / 4.32 = 26.04 sheets are "
            "needed. A part sheet still has to be bought whole, so the answer is 27. "
            "Answering 26 comes from rounding down instead of up.",
    },
}


def working_before_hinge(text):
    m = HINGE.search(text or "")
    return (text[:m.start()] if m else text or "").strip()


def _norm(s):
    return re.sub(r"[^0-9a-z./]", "", str(s).lower())


def conclusion(working):
    """The last sentence of the working — where it states what it arrived at.

    Matching anywhere in the working is unsafe: one item discussed option A only to say
    it "is the SAME line", i.e. to rule it out, and a whole-text match read that mention
    as support. Only the concluding sentence is evidence of an answer.
    """
    parts = [p for p in re.split(r"(?<=[.!?])\s+|\n", working.strip()) if p.strip()]
    return parts[-1] if parts else ""


def option_supported(q, working):
    """Which option the working's conclusion arrives at, if exactly one does.

    Substring matching is unsound on numbers: an option of "3000" matches a working that
    computed "30000 / 100 = 300", because "30000" contains "3000". A first version of
    this did exactly that and would have set a land-area question to 3000 plots instead
    of 300. Numbers are therefore compared as whole tokens, and a phrase option must
    appear as a whole phrase.
    """
    tail = conclusion(working).strip().rstrip(".…").strip()
    if not tail:
        return None
    # Unit exponents are not values. "Area = ... = 1800 m^2" ends in the 2 of "m^2", so
    # the final number read as 2 and the triangle-area fix was silently dropped.
    tail = re.sub(r"\^\s*\d+|[²³]", "", tail)

    # A conclusion that hedges is not a conclusion. These survive the hinge split because
    # they do not match it, but "Alternatively, in the triangle...", "Hmm, 37.5 rounds
    # to 38" and "actually adjacent angles are supplementary" are all the model still
    # thinking, and the value they land on should not be promoted to the answer.
    if re.search(r"\b(actually|alternatively|hmm|perhaps|assume|closest to|"
                 r"approximately|roughly|might be|seems? to be)\b", tail, re.I):
        return None

    # Only the FINAL value counts. Accepting any number in the conclusion produced four
    # wrong answers out of 38: "p = 10/4 = 2.5" matched an option of "2"; "45 + 3√13 ≈
    # 57.8" matched "60" from inside the expression; "1 - 7/12 = 5/12" matched "12".
    nums = re.findall(r"-?\d[\d,]*(?:\.\d+)?(?:/\d+)?", tail)
    last = nums[-1].replace(",", "") if nums else None
    flat = re.sub(r"[^0-9a-z./]", "", tail.lower())

    hits = []
    for L in LETTERS:
        opt = str(q.get("option_" + L) or "").strip()
        if not opt:
            continue
        oflat = re.sub(r"[^0-9a-z./]", "", opt.lower())
        onums = [n.replace(",", "") for n in
                 re.findall(r"-?\d[\d,]*(?:\.\d+)?(?:/\d+)?", opt)]
        # A bare numeric option is only accepted when it IS the final value. Matching the
        # end of the flattened text let the option "12" match a working concluding
        # "1 - 7/12 = 5/12", because the text ends in the fraction's denominator.
        # Phrase options ("15 minutes 45 seconds") still need the tail match, since their
        # value is not a single number.
        is_phrase = bool(re.search(r"[a-z]", oflat)) and len(oflat) >= 4
        ends_with = is_phrase and flat.endswith(oflat)
        is_last = len(onums) == 1 and last is not None and onums[0] == last
        if ends_with or is_last:
            hits.append(L)
    return hits[0].upper() if len(hits) == 1 else None


def main():
    ap = argparse.ArgumentParser(description="Repair leaked-working explanations")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--db", default=str(DB))
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute("SELECT * FROM questions")]
    hits = [r for r in rows if leaked_working(r["explanation"])]

    changes = []
    for r in hits:
        expl = r["explanation"] or ""
        working = working_before_hinge(expl)
        supported = option_supported(r, working)
        upd, note = {}, ""

        if r["id"] in HAND_FIXES:
            upd = dict(HAND_FIXES[r["id"]])
            upd["edited"] = 1
            note = "hand-verified: answer re-derived from the stem"
        elif ADMITS_BROKEN.search(expl):
            upd = {"review_status": "rejected", "reviewed_at": _now()}
            note = "explanation states no option is correct"
        elif leaked_working(working) or len(working.split()) < 8:
            # Truncation leaves nothing usable, so there is no working that stands.
            upd = {"review_status": "rejected", "reviewed_at": _now()}
            note = "no usable working survives the self-correction"
        else:
            upd["explanation"] = working
            if supported and supported != r["correct_answer"]:
                upd["correct_answer"] = supported
                note = (f"key {r['correct_answer']} -> {supported}; the working computes "
                        f"{r['option_' + supported.lower()]!r}")
            elif supported == r["correct_answer"]:
                note = "working agrees with the stored key; explanation cleaned"
            else:
                note = "key not mechanically verifiable; explanation cleaned"
                if r["review_status"] == "approved":
                    # Serving a question we cannot verify is the thing to stop first.
                    upd["review_status"] = "pending"
                    note += "; approved -> pending pending human check"
            upd["edited"] = 1

        changes.append({
            "id": r["id"], "subject": r["subject"], "source_book": r["source_book"],
            "was_status": r["review_status"],
            "now_status": upd.get("review_status", r["review_status"]),
            "was_answer": r["correct_answer"],
            "now_answer": upd.get("correct_answer", r["correct_answer"]),
            "note": note,
            "was_explanation": expl,
            "now_explanation": upd.get("explanation", expl),
        })
        if not args.dry_run and upd:
            sets = ", ".join(f"{k}=?" for k in upd)
            conn.execute(f"UPDATE questions SET {sets} WHERE id=?", [*upd.values(), r["id"]])

    if not args.dry_run:
        conn.commit()

    rejected = [c for c in changes if c["now_status"] == "rejected"]
    keyfix = [c for c in changes if c["was_answer"] != c["now_answer"]]
    requeued = [c for c in changes if c["was_status"] == "approved"
                and c["now_status"] == "pending"]
    print(f"leaked-working questions      : {len(hits)}")
    print(f"  rejected (unfixable)        : {len(rejected)}")
    print(f"  answer corrected            : {len(keyfix)}")
    print(f"  approved -> pending         : {len(requeued)}")
    print(f"  explanation cleaned only    : "
          f"{len(changes) - len(rejected) - len(keyfix)}")
    print(f"  approved rows touched       : "
          f"{sum(1 for c in changes if c['was_status'] == 'approved')}")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(
        {"generated": _now(), "total": len(hits), "changes": changes},
        indent=1, ensure_ascii=False))
    print(f"full record -> {REPORT}")
    if args.dry_run:
        print("DRY RUN — nothing written.")


def _now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


if __name__ == "__main__":
    main()
