"""Deal VIC writing prompts into drill forms, one PAIR per form.

A writing drill is not one prompt. The VIC paper sets two tasks in 40 minutes -- a short
piece of about 150 words and an extended one of about 250 -- and a drill has to serve
both, because writing is the one component that does not survive being halved:

  - **Budgeting across two tasks is the skill.** A candidate who spends 28 minutes on the
    piece they are enjoying has failed the paper, and practising one piece at a time never
    teaches them that.
  - **The second task is written tired**, by someone who has already spent their best
    ideas. That is where marks go, and a single-prompt drill never reaches it.
  - MCQ is different and does scale. Halve the questions and halve the clock and the
    candidate still meets the same seconds per question, so doubling back up predicts the
    real sitting. Writing has no such invariant, which is why `assign_forms.py` deals MCQ
    forms of 20-25 questions and this deals writing forms of exactly 2.

EVERY FORM IS ONE CREATIVE PLUS ONE PERSUASIVE, AND ONE SHORT PLUS ONE EXTENDED. The
paper sets one of each genre and one of each length; which genre carries which length is
not published anywhere found, so both combinations are dealt. `form_position` 1 is the
short task and 2 the extended one -- a convention, since the real order is unpublished,
and one `UPDATE` to flip if it turns out to matter.

Pairing is deterministic given the pool, so a re-run reproduces the same forms rather than
reshuffling a student's Set 7 underneath them.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.assign_writing_forms --report
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.assign_writing_forms --deal
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.assign_writing_forms --deal --force
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "run_data" / "db" / "qbank.db"
MANIFEST = REPO_ROOT / "run_data" / "output" / "forms" / "vic_writing_forms_manifest.json"

CREATIVE_TYPES = {"narrative", "diary"}
SHORT_MAX_WORDS = 200          # the short band tops out at 170, the extended starts at 220


def slot_of(row: dict) -> str:
    return "creative" if row["prompt_type"] in CREATIVE_TYPES else "persuasive"


def band_of(row: dict) -> str:
    return "short" if row["word_count_max"] <= SHORT_MAX_WORDS else "extended"


def fetch(conn: sqlite3.Connection) -> list[dict]:
    conn.row_factory = sqlite3.Row
    return [dict(r) for r in conn.execute(
        "SELECT * FROM writing_prompts WHERE school_type = 'victorian_selective' "
        "AND review_status != 'rejected' ORDER BY topic")]


def build_forms(rows: list[dict]) -> tuple[list[list[dict]], list[str]]:
    """Pair creative with persuasive so each form holds one short and one extended."""
    buckets: dict[tuple[str, str], list[dict]] = {}
    for r in rows:
        buckets.setdefault((slot_of(r), band_of(r)), []).append(r)

    cs = buckets.get(("creative", "short"), [])
    ce = buckets.get(("creative", "extended"), [])
    ps = buckets.get(("persuasive", "short"), [])
    pe = buckets.get(("persuasive", "extended"), [])

    notes = [f"pool: creative {len(cs)} short / {len(ce)} extended, "
             f"persuasive {len(ps)} short / {len(pe)} extended"]

    forms: list[list[dict]] = []
    # creative-short pairs with persuasive-extended, and vice versa. Position 1 = short.
    for short, extended in zip(cs, pe):
        forms.append([short, extended])
    for short, extended in zip(ps, ce):
        forms.append([short, extended])

    leftover = (len(cs) - min(len(cs), len(pe))) + (len(ps) - min(len(ps), len(ce)))
    if leftover:
        notes.append(f"{leftover} prompt(s) left unpaired — the bands are not balanced. "
                     f"A form needs one short and one extended from opposite slots.")
    return forms, notes


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", action="store_true", help="Show the pool and the deal")
    ap.add_argument("--deal", action="store_true", help="Write form_id/position/kind")
    ap.add_argument("--force", action="store_true",
                    help="re-deal prompts that already carry a form_id")
    args = ap.parse_args()

    conn = sqlite3.connect(DB_PATH)
    rows = fetch(conn)
    forms, notes = build_forms(rows)

    for n in notes:
        print(n)

    already = [r for r in rows if r["form_id"]]
    if already and args.deal and not args.force:
        print(f"\nREFUSING: {len(already)} prompt(s) already carry a form_id. Re-dealing "
              f"changes what a student who has sat that form was given. Pass --force if "
              f"that is what you mean.")
        raise SystemExit(1)

    manifest = []
    for n, form in enumerate(forms, 1):
        fid = f"vic-drill-wr-{n:03d}"
        minutes = sum(p["time_limit_minutes"] for p in form)
        manifest.append({
            "form_id": fid,
            "minutes": minutes,
            "prompts": [{"position": i, "id": p["id"], "topic": p["topic"],
                         "slot": slot_of(p), "band": band_of(p),
                         "words": f"{p['word_count_min']}-{p['word_count_max']}",
                         "minutes": p["time_limit_minutes"],
                         "review_status": p["review_status"]}
                        for i, p in enumerate(form, 1)],
        })

    if args.report or not args.deal:
        print(f"\n{len(forms)} writing drill forms\n")
        for f in manifest[:6]:
            print(f"  {f['form_id']}  {f['minutes']} min")
            for p in f["prompts"]:
                print(f"      {p['position']}. {p['band']:<8} {p['slot']:<10} "
                      f"{p['words']:<8} {p['minutes']:>2}min  {p['topic']}")
        if len(manifest) > 6:
            print(f"  ... and {len(manifest) - 6} more")
        bad = [f for f in manifest if f["minutes"] != 40]
        print(f"\nforms not totalling the paper's 40 minutes: {len(bad)}")
        pend = sum(1 for f in manifest for p in f["prompts"]
                   if p["review_status"] != "approved")
        print(f"prompts in a form that are not yet approved: {pend} of {len(forms) * 2}")

    if args.deal:
        updates = []
        for f in manifest:
            for p in f["prompts"]:
                updates.append((f["form_id"], p["position"], "drill", p["id"]))
        conn.executemany("UPDATE writing_prompts SET form_id = ?, form_position = ?, "
                         "form_kind = ? WHERE id = ?", updates)
        conn.commit()
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(json.dumps(
            {"generated_from": "tools/assign_writing_forms.py",
             "forms": manifest}, indent=2))
        print(f"\nDealt {len(forms)} forms over {len(updates)} prompts. "
              f"Manifest: {MANIFEST}")


if __name__ == "__main__":
    main()
