"""Deal NSW writing prompts into drill forms, ONE PROMPT PER FORM.

WHY A FORM OF ONE IS NOT A REDUNDANT WRAPPER. This was recorded the other way round for a
month -- "NSW sets one prompt, so a form of one adds nothing" -- and reading Selectly's own
code settled it: a prompt with no `form_id` is INVISIBLE in drill, not merely awkward.
`listStudentForms` builds the student's set list from `questions.form_id IS NOT NULL`
(`src/lib/forms/availability.ts`), so an unformed prompt is reachable only inside a mock.
Three more things hang off the form rather than the question:

  * the free-tier allowance and form locking count by `formFamily`
  * a round is a `(student, form, round)` row in `form_attempts`
  * "you have sat 12 of 42" is a count of those rows

So the form is what makes a prompt something a student can CHOOSE, and the only way
progress through the 42 can be counted.

CONTRAST WITH VIC, which `assign_writing_forms.py` deals in PAIRS. That is not a stylistic
difference: the VIC paper sets two tasks in 40 minutes and budgeting across them is the
skill, so a VIC form holds a short task at position 1 and an extended one at position 2.
Selectly now depends on that pairing -- its writing selection rotates over form GROUPS
precisely so a mock cannot serve two short tasks -- so the two dealers must stay different.

NSW sets ONE task in 30 minutes, and the prompt carries its own clock: 32 of the 42 run 30
minutes at 200-320 words and 10 run 25 minutes at 300-500. A single-prompt form is timed by
`time_limit_minutes` on the prompt itself, so that column may never be null -- a null falls
back to the section's 30 and silently hands the ten 25-minute prompts five extra minutes.
That is checked here before anything is written, not assumed.

THE ORDER IS ROUND-ROBIN BY TEXT TYPE, not by whatever the table returns. A student who
sits sets 1, 2 and 3 should meet three different kinds of writing, and the eight NSW types
are the point of the component. Deterministic given the pool, so a re-run reproduces the
same forms rather than reshuffling someone's Set 7 underneath them.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.assign_nsw_writing_forms --report
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.assign_nsw_writing_forms --deal
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "run_data" / "db" / "qbank.db"
MANIFEST = REPO_ROOT / "run_data" / "output" / "forms" / "nsw_writing_forms_manifest.json"

PREFIX = "nsw-drill-wr"

# Fixed, so the deal is reproducible. Ordered longest-established first; the only thing
# that matters is that it never changes.
TYPE_ORDER = ("narrative", "persuasive", "article", "diary",
              "email", "speech", "advice_sheet", "news_report")

# Selectly's own form-id rule: lowercase, hyphenated, ending in the set number, and
# `formFamily` strips the trailing `-\d+` to get `nsw-drill-wr`. A name it cannot parse
# shows the student a raw id instead of "NSW Writing — Set 3".
FORM_ID_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def fetch(conn: sqlite3.Connection) -> list[dict]:
    conn.row_factory = sqlite3.Row
    return [dict(r) for r in conn.execute(
        "SELECT * FROM writing_prompts WHERE school_type = 'nsw_selective' "
        "AND review_status != 'rejected' ORDER BY id")]


def check_contract(rows: list[dict]) -> list[str]:
    """Everything Selectly needs, verified before a form id is written rather than after
    the push. Each of these renders wrong rather than failing loudly downstream."""
    problems = []
    for r in rows:
        who = r["id"][:8]
        if r["time_limit_minutes"] is None:
            problems.append(f"{who}: time_limit_minutes is null — the form would be "
                            f"timed at the section's 30 minutes whatever the prompt says")
        if r["word_count_min"] is None or r["word_count_max"] is None:
            problems.append(f"{who}: word count missing — the task renders without its "
                            f"'Write N-M words'")
        elif r["word_count_min"] > r["word_count_max"]:
            problems.append(f"{who}: word_count_min {r['word_count_min']} exceeds "
                            f"word_count_max {r['word_count_max']} — the import rejects it")
        if r["prompt_type"] not in TYPE_ORDER:
            problems.append(f"{who}: prompt_type {r['prompt_type']!r} is not one of the "
                            f"eight — Selectly falls back to the ARGUED rubric, so it "
                            f"would be marked on quality of argument")
        if not (r["task_instruction"] or "").strip():
            problems.append(f"{who}: no task_instruction — that is the stem")
    return problems


def build_forms(rows: list[dict]) -> list[dict]:
    """One prompt per form, round-robin across the text types."""
    by_type: dict[str, list[dict]] = {t: [] for t in TYPE_ORDER}
    for r in rows:
        by_type[r["prompt_type"]].append(r)
    for t in by_type:
        by_type[t].sort(key=lambda r: r["id"])

    dealt: list[dict] = []
    depth = 0
    while len(dealt) < len(rows):
        for t in TYPE_ORDER:
            if depth < len(by_type[t]):
                dealt.append(by_type[t][depth])
        depth += 1
    return dealt


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", action="store_true", help="Show the pool and the deal")
    ap.add_argument("--deal", action="store_true", help="Write form_id/position/kind")
    ap.add_argument("--force", action="store_true",
                    help="re-deal prompts that already carry a form_id")
    args = ap.parse_args()

    conn = sqlite3.connect(DB_PATH)
    rows = fetch(conn)

    problems = check_contract(rows)
    if problems:
        print(f"REFUSING TO DEAL — {len(problems)} prompt(s) fail the contract:")
        for p in problems:
            print("  " + p)
        raise SystemExit(1)

    already = [r for r in rows if r["form_id"]]
    if already and not args.force:
        print(f"{len(already)} prompt(s) already carry a form_id; pass --force to re-deal")
        raise SystemExit(1)

    dealt = build_forms(rows)
    forms = []
    for i, r in enumerate(dealt, start=1):
        form_id = f"{PREFIX}-{i:03d}"
        assert FORM_ID_PATTERN.match(form_id) and len(form_id) <= 50, form_id
        assert form_id.rsplit("-", 1)[0] == PREFIX, form_id
        forms.append({"form_id": form_id, "id": r["id"], "prompt_type": r["prompt_type"],
                      "minutes": r["time_limit_minutes"],
                      "words": [r["word_count_min"], r["word_count_max"]],
                      "topic": r["topic"]})

    if args.report or not args.deal:
        print(f"{len(rows)} NSW prompts -> {len(forms)} forms of one\n")
        for f in forms:
            print(f"  {f['form_id']}  {f['prompt_type']:<13} {f['minutes']} min  "
                  f"{f['words'][0]}-{f['words'][1]} words   {f['topic']}")
        mins = {}
        for f in forms:
            mins[f["minutes"]] = mins.get(f["minutes"], 0) + 1
        print(f"\n  time split: {dict(sorted(mins.items()))}")

    if args.deal:
        for f in forms:
            conn.execute("UPDATE writing_prompts SET form_id = ?, form_position = 1, "
                         "form_kind = 'drill' WHERE id = ?", (f["form_id"], f["id"]))
        conn.commit()
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(json.dumps(
            {"prefix": PREFIX, "forms": len(forms), "per_form": 1, "deal": forms},
            indent=1))
        print(f"\ndealt {len(forms)} forms -> {MANIFEST}")
    conn.close()


if __name__ == "__main__":
    main()
