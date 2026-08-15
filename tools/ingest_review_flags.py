#!/usr/bin/env python3
"""Turn Selectly's flagged-questions CSV into an adjudication worklist.

The review loop is deliberately manual in both directions: Selectly never talks to
qbank and qbank never reads Selectly's database. The reviewer flags questions in the
app, the admin exports the CSV, and it arrives here. This reads it.

What it does NOT do is apply anything. A reviewer flag says "this looks wrong", which
is not the same as knowing what is wrong -- across the blind-solve campaign the same
signal resolved variously into a wrong key, a second correct answer, a figure
contradicting its stem, and a reviewer misreading a sound question. Each one needs the
question read. So this prints the full stored question beside the flag and stops.

REQUIRES a `qbank_id` column in the CSV. Selectly's export currently emits its own
`question_id`, which qbank has never seen and cannot resolve; see the handover, §1.
Rows without one are reported and skipped rather than guessed at.
"""
import argparse
import csv
import json
import pathlib
import sqlite3

ROOT = pathlib.Path(__file__).resolve().parents[1]
DB = ROOT / "run_data/db/qbank.db"
OUT = ROOT / "run_data/output/review_flags"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_path", help="flagged-questions-YYYY-MM-DD.csv from Selectly admin")
    ap.add_argument("--round", default="1", help="review round label, used in the filename")
    args = ap.parse_args()

    rows = list(csv.DictReader(open(args.csv_path, encoding="utf-8-sig")))
    if not rows:
        raise SystemExit("CSV is empty")
    if "qbank_id" not in rows[0]:
        raise SystemExit(
            "This CSV has no `qbank_id` column — its columns are: "
            + ", ".join(rows[0]) + "\n"
            "Selectly's export must include qbank_id; its own question_id cannot be "
            "resolved here. See pdfs/selectly_implementation_HANDOVER.md §1.")

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    work, unmatched = [], []

    for r in rows:
        qid = (r.get("qbank_id") or "").strip()
        q = con.execute("SELECT * FROM questions WHERE id=?", (qid,)).fetchone() if qid else None
        if not q:
            unmatched.append(r)
            continue
        q = dict(q)
        work.append({
            "qbank_id": qid,
            "form_id": q["form_id"],
            "form_position": q["form_position"],
            "reviewer": r.get("reviewer_email", ""),
            "note": r.get("note", ""),
            "flagged_at": r.get("flagged_at", ""),
            "subject": q["subject"],
            "topic": q["topic"],
            "review_status": q["review_status"],
            "stem": q["stem"],
            "options": {L.upper(): q["option_" + L] for L in "abcd"},
            "correct_answer": q["correct_answer"],
            "explanation": q["explanation"],
            "has_figure": bool(q["figure_svg"]),
            "has_passage": bool(q["passage"]),
            "verdict": None,     # filled in by hand: repair | rekey | reject | keep
        })

    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"round_{args.round}.json"
    path.write_text(json.dumps(work, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"{len(rows)} flags in the CSV; {len(work)} matched to a qbank question")
    if unmatched:
        print(f"\n{len(unmatched)} could NOT be matched — these need looking at:")
        for r in unmatched[:10]:
            print(f"   qbank_id={r.get('qbank_id','')!r} "
                  f"stem={(r.get('stem_snippet') or '')[:60]!r}")
    by_form = {}
    for w in work:
        by_form[w["form_id"]] = by_form.get(w["form_id"], 0) + 1
    print("\nflags per form:")
    for f, n in sorted(by_form.items()):
        print(f"   {f:<22}{n:>4}")
    print(f"\nworklist -> {path}")
    print("Each entry has a null `verdict`. Read the question, decide "
          "repair / rekey / reject / keep, then act on it.")


if __name__ == "__main__":
    main()
