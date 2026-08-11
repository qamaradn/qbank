"""Identify verbal_reasoning questions of the types TASK §6 says never to generate.

§6 ("DO NOT GENERATE THESE") lists Indian-syllabus artefacts that made the bank feel
wrong for an Australian selective paper: alphabet position, letter/number codes, hidden
words, dictionary/alphabetical ordering, blood relations, clock-and-calendar,
input-output, data sufficiency, and anagram unscrambling.

Why this is a tool and not a query. Two different figures for "the §6 count" are in
circulation -- 166 in CLAUDE.md and 149 in the Selectly handover -- because both came
from ad-hoc classifiers that were never committed. Neither can be reproduced or audited.
A question is about to be withdrawn from students on the strength of this number, so it
needs to be re-derivable and its matches need to be readable.

What it deliberately does NOT flag. The handover's broader "off-spec" set -- spatial
reasoning, double meanings, odd-one-out variants -- is a judgement call about taxonomy
fit, not a §6 breach. §8 rates the §6 list itself "Medium-low -- argument from absence".
Conflating the two turns a defensible 150-odd into an indefensible 400. Run with
--questionable to see that second set separately, and decide it separately.

Matching is topic-first and stem-second. `topic` is the generating model's own label and
is the stronger signal; stem patterns catch rows whose topic was vague. Every match
records WHICH rule fired, so a wrong rule can be found and fixed rather than argued about.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.vr_banned_types --report
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.vr_banned_types --sample 4
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.vr_banned_types --manifest
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "run_data" / "db" / "qbank.db"
MANIFEST = REPO_ROOT / "run_data" / "output" / "vr_banned_types.json"

# (category, topic regex, stem regex). Either match flags the row.
# Topic patterns are anchored loosely because the generators produced several spellings
# of the same label ("odd one out", "odd-one-out semantic").
BANNED: list[tuple[str, str, str]] = [
    (
        "alphabetical_ordering",
        r"dictionary|alphabetical|alphabetic order",
        r"\bdictionary order\b|\balphabetical order\b|"
        r"\bcome[s]? (?:first|last) in a dictionary\b|"
        r"\bappear[s]? (?:first|last) in (?:a|the) dictionary\b|"
        r"\barrange(?:d)? .{0,30}alphabetical",
    ),
    (
        "letter_number_codes",
        r"word code|letter code|number code|letter or number sequence",
        r"\bis (?:written|coded|represented) as\b.{0,40}\b(?:what|which)\b|"
        r"\bin a certain code\b|\bcode language\b|\bthe code for\b",
    ),
    (
        "hidden_words",
        r"hidden word",
        r"\bhidden word\b|\bconceal(?:ed|s)? (?:a|the) word\b|"
        r"\bword hidden (?:in|within|across)\b",
    ),
    (
        "anagrams",
        r"anagram|making words|unscramb",
        r"\banagram\b|\bunscramble\b|\brearrang(?:e|ed|ing) the letters\b|"
        r"\bletters of .{0,30} (?:can be )?rearranged\b",
    ),
    (
        "alphabet_position",
        r"alphabet position|letter position",
        r"\b\d+(?:st|nd|rd|th) letter (?:from|of) the\b|"
        r"\bposition in the alphabet\b|\bletter of the alphabet\b",
    ),
    (
        "blood_relations",
        r"blood relation|family relation",
        r"\bhow is .{0,40} related to\b|\bmy (?:father|mother)'s only\b|"
        r"\bpointing (?:to|at) (?:a|the) (?:photograph|picture)\b",
    ),
    (
        "clock_calendar",
        r"clock and calendar|calendar reasoning",
        r"\bangle between the hour and minute\b|\bwhat day of the week (?:was|will)\b",
    ),
    (
        "input_output",
        r"input.?output",
        r"\binput\b.{0,60}\bstep (?:i|1|one)\b",
    ),
    (
        "data_sufficiency",
        r"data sufficiency",
        r"\bwhich statement\(s\) (?:is|are) sufficient\b|\bis the data sufficient\b",
    ),
]

# Not §6 breaches. Off-taxonomy judgement calls, reported separately and never merged
# into the banned count.
QUESTIONABLE = r"spatial|double meaning|odd.?one.?out|word classification|ordering and logic"


def classify(row: dict) -> tuple[str, str] | None:
    """Return (category, which_rule) for the first banned rule that fires, else None."""
    topic = (row.get("topic") or "").lower()
    stem = (row.get("stem") or "").lower()
    for category, topic_pat, stem_pat in BANNED:
        if re.search(topic_pat, topic):
            return category, "topic"
        if stem_pat and re.search(stem_pat, stem):
            return category, "stem"
    return None


def fetch(conn: sqlite3.Connection) -> list[dict]:
    conn.row_factory = sqlite3.Row
    return [
        dict(r)
        for r in conn.execute(
            "SELECT id, stem, topic, source_book, review_status "
            "FROM questions WHERE subject='verbal_reasoning'"
        )
    ]


def collect(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    banned, questionable = [], []
    for r in rows:
        hit = classify(r)
        if hit:
            banned.append({**r, "category": hit[0], "matched_on": hit[1]})
        elif re.search(QUESTIONABLE, (r.get("topic") or "").lower()):
            questionable.append(r)
    return banned, questionable


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", action="store_true", help="Counts by category and status")
    ap.add_argument("--sample", type=int, default=0, help="Print N stems per category")
    ap.add_argument("--questionable", action="store_true", help="Show the off-taxonomy set")
    ap.add_argument("--manifest", action="store_true", help="Write the id list to JSON")
    args = ap.parse_args()
    if not any([args.report, args.sample, args.questionable, args.manifest]):
        args.report = True

    conn = sqlite3.connect(DB_PATH)
    try:
        rows = fetch(conn)
    finally:
        conn.close()
    banned, questionable = collect(rows)

    if args.report or args.manifest:
        print(f"verbal_reasoning rows: {len(rows)}")
        print(f"§6 banned            : {len(banned)}")
        approved = [b for b in banned if b["review_status"] == "approved"]
        print(f"  of which approved  : {len(approved)}  (live to students today)")
        print()
        by_cat: dict[str, list[dict]] = {}
        for b in banned:
            by_cat.setdefault(b["category"], []).append(b)
        print(f"{'category':<24}{'total':>7}{'approved':>10}{'by topic':>10}{'by stem':>9}")
        for cat in sorted(by_cat, key=lambda c: -len(by_cat[c])):
            hits = by_cat[cat]
            print(
                f"{cat:<24}{len(hits):>7}"
                f"{sum(1 for h in hits if h['review_status'] == 'approved'):>10}"
                f"{sum(1 for h in hits if h['matched_on'] == 'topic'):>10}"
                f"{sum(1 for h in hits if h['matched_on'] == 'stem'):>9}"
            )
        print(f"\noff-taxonomy (NOT §6, separate decision): {len(questionable)}")

    if args.sample:
        by_cat = {}
        for b in banned:
            by_cat.setdefault(b["category"], []).append(b)
        for cat in sorted(by_cat, key=lambda c: -len(by_cat[c])):
            print(f"\n=== {cat} ({len(by_cat[cat])}) ===")
            for h in by_cat[cat][: args.sample]:
                print(f"  [{h['matched_on']}/{h['review_status']}] {h['topic']}")
                print(f"    {h['stem'][:150]}")

    if args.questionable:
        print(f"\n=== off-taxonomy, {len(questionable)} rows ===")
        seen: dict[str, int] = {}
        for q in questionable:
            seen[q["topic"] or ""] = seen.get(q["topic"] or "", 0) + 1
        for t, n in sorted(seen.items(), key=lambda kv: -kv[1]):
            print(f"  {n:>4}  {t}")

    if args.manifest:
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(
            json.dumps(
                {
                    "generated_from": "tools/vr_banned_types.py",
                    "banned": banned,
                    "off_taxonomy_ids": [q["id"] for q in questionable],
                },
                indent=2,
            )
        )
        print(f"\nwrote {MANIFEST}")


if __name__ == "__main__":
    main()
