"""
pipeline/blind_solve.py — harness for an independent re-solve of the question bank.

The point of this file is to make blindness a property of the DATA FLOW rather than a
promise. The solver (a model working in a Claude Code session, on the subscription
rather than the metered API) must never see the stored key, because a solver shown
"the answer is B" will find a way to justify B. So:

    export  ->  stem + options ONLY, with the options SHUFFLED, written to disk
    solve   ->  the solver reads that file and writes a letter per question
    score   ->  this script un-shuffles, compares against the DB, records a verdict

The key never appears in the exported file, so it cannot enter the solver's context.
The shuffle is stored only in the export file's `perm`, and scoring is the first
moment the two are ever brought together.

Shuffling matters for a second reason: the bank being audited was written by a model
with unknown positional habits, and an unshuffled re-solve would let any shared habit
show up as false agreement.

Verdicts accumulate in a durable JSON file, so a run can stop and resume - which it
will, since this is thousands of questions done conversationally.

Usage
-----
    python -m pipeline.blind_solve --export --status approved --limit 25
    #   ... solver reads run_data/blind/pending_batch.json, writes answers ...
    python -m pipeline.blind_solve --score
    python -m pipeline.blind_solve --report
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import random
import sqlite3
from pathlib import Path

DB = os.environ.get("DB_PATH", "run_data/db/qbank.db")
WORK = Path("run_data/blind")
BATCH = WORK / "pending_batch.json"
ANSWERS = WORK / "answers.json"
VERDICTS = WORK / "verdicts.json"
LETTERS = ["A", "B", "C", "D"]


def _load(p, default):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def export(conn, subject, status, limit, seed):
    """Write a batch of unsolved questions, options shuffled, key withheld."""
    WORK.mkdir(parents=True, exist_ok=True)
    done = {v["id"] for v in _load(VERDICTS, [])}
    conn.row_factory = sqlite3.Row
    sql = "SELECT * FROM questions WHERE subject=?"
    params = [subject]
    if status:
        sql += " AND review_status=?"
        params.append(status)
    sql += " ORDER BY id"
    rows = [r for r in conn.execute(sql, params) if r["id"] not in done]

    rng = random.Random(seed)
    out = []
    for r in rows[:limit]:
        order = LETTERS[:]
        rng.shuffle(order)
        # perm maps the SHOWN letter -> the letter it really is in the database
        perm = {shown: real for shown, real in zip(LETTERS, order)}
        item = {"id": r["id"], "topic": r["topic"], "stem": r["stem"], "perm": perm}
        for shown in LETTERS:
            item["option_" + shown.lower()] = r["option_" + perm[shown].lower()]
        out.append(item)

    BATCH.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    # A fresh batch invalidates any stale answer file from the previous one.
    if ANSWERS.exists():
        ANSWERS.unlink()
    remaining = len(rows) - len(out)
    print(f"exported {len(out)} unsolved questions -> {BATCH}")
    print(f"  ({remaining} still unsolved after this batch)")
    print("  the exported file contains NO correct_answer and NO explanation")
    return out


def score(conn):
    """Bring the solver's answers and the stored keys together for the first time."""
    batch = _load(BATCH, [])
    answers = _load(ANSWERS, {})
    if not batch:
        print("no batch to score"); return
    if not answers:
        print(f"no answers found at {ANSWERS}"); return

    conn.row_factory = sqlite3.Row
    verdicts = _load(VERDICTS, [])
    seen = {v["id"] for v in verdicts}
    agree = disagree = skipped = 0

    for item in batch:
        shown = answers.get(item["id"])
        if not shown:
            skipped += 1
            continue
        if item["id"] in seen:
            continue
        shown = shown.strip().upper()[:1]
        if shown not in LETTERS + ["N"]:
            skipped += 1
            continue
        row = conn.execute("SELECT correct_answer, review_status, option_a, option_b, "
                           "option_c, option_d FROM questions WHERE id=?",
                           (item["id"],)).fetchone()
        # "N" = none of the four options is defensible. Without it the solver is forced
        # to pick the least-wrong option, which can land on the stored key and record a
        # FALSE agreement - that is how the broken BANANA/ORANGE cipher first passed.
        if shown == "N":
            real, ok = "N", False
        else:
            # translate the solver's SHOWN letter back into a real database letter
            real = item["perm"][shown]
            ok = (real == row["correct_answer"])
        agree += ok
        disagree += (not ok)
        verdicts.append({
            "id": item["id"], "topic": item["topic"],
            "review_status": row["review_status"],
            "solver_said": real, "stored_key": row["correct_answer"],
            "agree": ok,
            "stem": item["stem"][:180],
            "solver_option": ("(none of the options is correct)" if real == "N"
                              else row["option_" + real.lower()]),
            "keyed_option": row["option_" + row["correct_answer"].lower()],
        })

    VERDICTS.write_text(json.dumps(verdicts, indent=2, ensure_ascii=False),
                        encoding="utf-8")
    print(f"scored {agree + disagree}   agree {agree}   DISAGREE {disagree}"
          + (f"   (no answer given: {skipped})" if skipped else ""))
    print(f"  running total in {VERDICTS}: {len(verdicts)}")


def report():
    v = _load(VERDICTS, [])
    if not v:
        print("no verdicts yet"); return
    dis = [x for x in v if not x["agree"]]
    print(f"BLIND RE-SOLVE — {len(v)} questions scored")
    print(f"  agree with stored key : {len(v) - len(dis)} "
          f"({100*(len(v)-len(dis))/len(v):.1f}%)")
    print(f"  DISAGREE              : {len(dis)} "
          f"({100*len(dis)/len(v):.1f}%)\n")
    by_status = collections.Counter(x["review_status"] for x in dis)
    print("  disagreements by review status:", dict(by_status))
    print("\n  disagreements by topic:")
    for t, k in collections.Counter(x["topic"] for x in dis).most_common(10):
        print(f"    {str(t):<42} {k:>3}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default=DB)
    ap.add_argument("--subject", default="verbal_reasoning")
    ap.add_argument("--status", default=None, help="approved | pending | rejected")
    ap.add_argument("--limit", type=int, default=25)
    ap.add_argument("--seed", type=int, default=None,
                    help="shuffle seed; omit for a fresh shuffle each batch")
    ap.add_argument("--export", action="store_true")
    ap.add_argument("--score", action="store_true")
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()

    conn = sqlite3.connect(a.db)
    if a.export:
        export(conn, a.subject, a.status, a.limit, a.seed)
    if a.score:
        score(conn)
    if a.report:
        report()
    conn.close()


if __name__ == "__main__":
    main()
