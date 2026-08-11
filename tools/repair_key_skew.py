#!/usr/bin/env python3
"""Rebalance the answer key by reordering options — never by rewriting a question.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_key_skew --dry-run
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_key_skew --apply
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_key_skew --revert <manifest>

THE DEFECT

    vic_content_taxonomy_TASK.md §7.1. The Gemini pipeline never shuffled options for key
    balance; the hand-built finalisers always did. So the two hand-built subjects are an
    even 25/25/25/25 and the generated ones are not:

        ACT reading  (718)   A 3.8%  B 37.9%  C 47.6%  D 10.7%   -> answer C, score 48%
        quantitative (2195)  A 37.8% B 31.1%  C 23.6%  D  7.6%   -> never pick D, lose 8%

    No question is wrong. The options are in the wrong order. That makes this a reorder,
    not a rewrite, and it is reversible.

WHY SHUFFLE RATHER THAN SORT ASCENDING

    75% of the quantitative options are purely numeric, and 56% of those are already in
    ascending order — so "sort every numeric item ascending" looks like the tidy fix that
    also imposes a real exam convention. Measured over the 1,550 numeric items with four
    distinct values, it is not:

        now              A 35%  B 33%  C 25%  D  7%    best single-letter cheat 35%
        sort ascending   A 17%  B 37%  C 34%  D 12%    best single-letter cheat 37%
        shuffle          A 25%  B 24%  C 26%  D 25%    best single-letter cheat 26%

    Sorting makes it slightly worse, because distractors are generated to bracket the key:
    1,098 of 1,550 keys (71%) are the 2nd or 3rd smallest of the four values, so sorting
    concentrates them in B and C. Nothing is lost by not sorting — at 56% the ascending
    convention is not currently honoured, so students cannot be relying on it.

    The bracketing itself is a real defect and this tool does NOT fix it: after shuffling,
    a student who sorts the options mentally still finds the key in the middle 71% of the
    time. Fixing that means regenerating distractor VALUES so the key's rank is uniform,
    which is authoring work, not reordering.

WHAT THIS TOOL DOES NOT FIX

    The length tell. In ACT reading the key averages 62.1 characters against 54.9 for
    distractors, so "pick the longest option" scores 48.7% — and reordering cannot touch
    that, since it moves options without changing them. Padding the short distractors is
    an editing pass a person has to do. Shuffling alone takes the reading set from two
    cheap cheats to one.

BLOCKED QUESTIONS

    Reordering a broken question just moves the breakage. Anything whose options are not
    four distinct answers, or whose explanation admits the item is defective, is refused
    and listed in the manifest for a human:

      duplicate_options     two options with the same text — one of them is the key in
                            several cases, so the student is marked wrong for a right answer
      equivalent_admitted   the explanation says two options are the same value or that
                            both are correct ("5√2" against "10/√2"; "Both A and B are factors")
      authoring_intent      the explanation shows the answer being chosen rather than
                            derived ("I'll set answer C to 30 000", "This geometry needs fixing")

EXPLANATIONS THAT NAME AN OPTION LETTER

    71 in scope. They are not hand-edited and they do not block the shuffle: this tool
    knows the permutation it applied, so it rewrites "option C" to whichever letter that
    option moved to, in the same pass. Letter lists ("Options C and D", "Both A and B")
    are remapped together. References to sentence or value positions — "the first four
    scores", "the other two interior angles" — are left alone, because they point at the
    stem, not at the options.

REVERSIBILITY

    Every changed row is written to the manifest with its full previous state (four
    options, key, explanation), so --revert restores the scope exactly. The tool refuses
    to run twice over the same scope without --force, because a second shuffle would
    rebase the first manifest's "before" and make the revert a lie.
"""
import argparse
import collections
import json
import os
import pathlib
import random
import re
import sqlite3
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

VERSION = 1
DB = os.environ.get("DB_PATH", "run_data/db/qbank.db")
MANIFEST = ROOT / "run_data/output/key_skew_manifest.json"
LETTERS = "ABCD"

# The VIC repair scope from vic_content_taxonomy_TASK.md §4.2 and §3.3: the ACT-sourced
# reading set plus the whole quantitative bank. rc_nsw_* is excluded because it is
# already an even 25/25/25/25 — its finaliser shuffled.
SCOPES = {
    "vic": "((subject = 'reading_comprehension' AND source_book LIKE 'act_%') "
           "OR subject = 'quantitative_reasoning')",
    "reading": "(subject = 'reading_comprehension' AND source_book LIKE 'act_%')",
    "quantitative": "(subject = 'quantitative_reasoning')",
    # The four Gemini-built verbal books. vr_vic_acer is excluded: it is hand-built and
    # already even at 25/25/25/25, because its finaliser deals the letters out.
    #
    # These were rated "mild" in vic_content_taxonomy_TASK.md §7.1 and passed over. That
    # rating came from the SUBJECT average, and the books skew in opposite directions --
    # external_vr_300526 is 43% A while direct_ve_290526 is 43% B -- so they cancel out
    # to a harmless-looking 27/29/24/19. Per book, three of the four are exploitable.
    "verbal": "(subject = 'verbal_reasoning' AND source_book != 'vr_vic_acer')",
}


# ---------------------------------------------------------------- blockers
EQUIVALENT_ADMITTED = re.compile(
    r"\b(?:options?|choices?)\s*\(?[A-D]\)?\s*(?:and|,|&)\s*\(?[A-D]\)?\s*(?:are|is)\s+"
    r"(?:equivalent|the same|identical)"
    r"|\b(?:both|either)\s+\(?[A-D]\)?\s+and\s+\(?[A-D]\)?\s+(?:are|is)\s+"
    r"(?:factors|correct|valid|true|equivalent|the same|identical|acceptable)"
    r"|\bequals?\s+[^.]{0,30}\bbut is not in simplest form"
    r"|\b(?:also equals|is equal to)\b[^.]{0,40}\b(?:but|however|though)\b",
    re.I)

# A bare "A) ... B) ... C) ..." run inside an explanation enumerates the options in their
# CURRENT order. Reordering silently invalidates it, and the labels cannot be remapped
# safely because a bare "A)" is indistinguishable from a list marker or a point label.
# Labels written as "Option A:" are fine — those carry the option word and get remapped.
_ENUM_LABEL = re.compile(r"(?<![A-Za-z0-9])([A-D])\s*[):.]\s")
_OPTION_WORD_BEFORE = re.compile(r"(?:option|choice|answer)s?\s*\(?$", re.I)


def _bare_enumeration(expl):
    bare = {m.group(1) for m in _ENUM_LABEL.finditer(expl)
            if not _OPTION_WORD_BEFORE.search(expl[max(0, m.start() - 10):m.start()])}
    return len(bare) >= 3

AUTHORING_INTENT = re.compile(
    r"\b(?:i'?ll|i will|let'?s|we'?ll|let me)\s+"
    r"(?:set|use|pick|choose|make|say|assume|adjust|go with|just present)\b"
    r"|\bfor simplicity[, ]+(?:answer|option|let)"
    r"|\bthis (?:question|geometry) (?:has issues|needs fixing)"
    r"|\bhas been replaced with\b"
    r"|\bclosest to option\b"
    r"|\bnot exact\b"
    r"|\bshould be\s+\d",
    re.I)


def _norm(t):
    return re.sub(r"\s+", " ", str(t or "").strip().lower()).rstrip(".")


def blocker(q):
    """Return a reason string if this question must not be reordered, else None."""
    opts = [q["option_" + L.lower()] for L in LETTERS]
    if any(o is None or not str(o).strip() for o in opts):
        return "missing_option"
    if q["correct_answer"] not in LETTERS:
        return "bad_key"
    if len({_norm(o) for o in opts}) < 4:
        return "duplicate_options"
    expl = str(q["explanation"] or "")
    if EQUIVALENT_ADMITTED.search(expl):
        return "equivalent_admitted"
    if AUTHORING_INTENT.search(expl):
        return "authoring_intent"
    if _bare_enumeration(expl):
        return "inline_option_enumeration"
    if _BOTH_LIST.search(expl):
        # "both A and B" without an option word is genuinely ambiguous: in coordinate
        # geometry A..D are point labels, and remapping them corrupts the maths --
        # "AB is horizontal since both A and B have y = 4" became "both B and C have
        # y = 4", which is simply false. The option-sense forms ("both A and B are
        # equivalent") are already caught above, so anything reaching here cannot be
        # resolved mechanically and is left for a human.
        return "ambiguous_letter_reference"
    return None


# ---------------------------------------------------------------- explanation remap
# An option word followed by a letter, or a letter list joined by and/or/comma/slash.
# The letter must be a standalone token. Without the \b guards, [A-D] under re.I also
# matches the leading letter of "choice", "and", "because" — which made a letter list
# swallow the next word and skip the reference inside it.
_L = r"\(?\b[A-Da-d]\b\)?"
_OPTION_LIST = re.compile(
    r"\b(options?|choices?|answers?)(\s*" + _L +
    r"(?:\s*(?:,|and|&|/|or)\s*" + _L + r")*)",
    re.I)
_BOTH_LIST = re.compile(
    r"\b(both|either|neither)(\s+" + _L + r"\s+(?:and|or)\s+" + _L + r")", re.I)
_BARE_LETTER = re.compile(r"\b([A-Da-d])\b")


def remap_explanation(expl, mapping):
    """Rewrite option-letter references through `mapping` (old letter -> new letter).

    Single pass, so an A->B B->C mapping cannot rewrite the same letter twice. Only
    letters that follow an option word are touched; "the first four scores" and the
    C in "sin(C)" are left alone because neither is preceded by one.
    """
    if not expl:
        return expl, 0
    n = [0]

    def fix_letters(text):
        def one(m):
            raw = m.group(1)
            new = mapping.get(raw.upper(), raw.upper())
            if new != raw.upper():
                n[0] += 1
            return new.lower() if raw.islower() else new
        return _BARE_LETTER.sub(one, text)

    def repl(m):
        return m.group(1) + fix_letters(m.group(2))

    # _BOTH_LIST is deliberately NOT remapped here — see blocker().
    out = _OPTION_LIST.sub(repl, str(expl))
    return out, n[0]


def explanation_names_option(expl):
    return bool(_OPTION_LIST.search(str(expl or "")))


# ---------------------------------------------------------------- the deal
def plan_group(questions, rng):
    """Assign each question a target key letter so the group comes out uniform (+/-1).

    Round-robin over a shuffled order rather than an independent random draw per
    question: with n=718 an independent draw lands within a few points of uniform, but
    round-robin is exactly uniform and just as unpredictable to a student.
    """
    order = list(questions)
    rng.shuffle(order)
    targets = [LETTERS[i % 4] for i in range(len(order))]
    rng.shuffle(targets)
    return dict(zip((q["id"] for q in order), targets))


def build_change(q, target, rng):
    """Return the row update moving q's key to `target`, or None if it is already there
    and no reordering would occur."""
    old_key = q["correct_answer"]
    opts = {L: q["option_" + L.lower()] for L in LETTERS}
    others = [L for L in LETTERS if L != old_key]
    rng.shuffle(others)
    slots = [L for L in LETTERS if L != target]
    # mapping: old letter -> new letter
    mapping = {old_key: target}
    for old, new in zip(others, slots):
        mapping[old] = new
    new_opts = {mapping[L]: opts[L] for L in LETTERS}
    new_expl, n_remap = remap_explanation(q["explanation"], mapping)
    if mapping == {L: L for L in LETTERS}:
        return None
    return {
        "id": q["id"],
        "subject": q["subject"],
        "source_book": q["source_book"],
        "mapping": mapping,
        "old_key": old_key,
        "new_key": target,
        "explanation_remapped": n_remap,
        "before": {
            "correct_answer": old_key,
            "explanation": q["explanation"],
            **{"option_" + L.lower(): opts[L] for L in LETTERS},
        },
        "after": {
            "correct_answer": target,
            "explanation": new_expl,
            **{"option_" + L.lower(): new_opts[L] for L in LETTERS},
        },
    }


# ---------------------------------------------------------------- reporting
def distribution(rows):
    c = collections.Counter(r["correct_answer"] for r in rows)
    n = max(1, len(rows))
    return {L: c[L] / n for L in LETTERS}


def fmt_dist(d, n):
    body = "  ".join(f"{L} {100 * d[L]:5.1f}%" for L in LETTERS)
    return f"{body}   worst {100 * max(d.values()):5.1f}%   n={n}"


def report_by_book(rows, title):
    """Group by subject AND book. The ACT books carry both reading and quantitative
    questions, and their skews run in opposite directions (reading C 48%, quantitative
    A 38%), so a book-only report averages them out and shows neither."""
    print(f"\n  {title}")
    by = collections.defaultdict(list)
    for r in rows:
        by[(r["subject"], r["source_book"])].append(r)
    for subject in sorted({s for s, _ in by}):
        sub_rows = [r for r in rows if r["subject"] == subject]
        print(f"    {subject}")
        for s_, book in sorted(k for k in by if k[0] == subject):
            g = by[(s_, book)]
            print(f"      {book:22s} {fmt_dist(distribution(g), len(g))}")
        print(f"      {'-- subject total':22s} {fmt_dist(distribution(sub_rows), len(sub_rows))}")
    print(f"    {'ALL':24s} {fmt_dist(distribution(rows), len(rows))}")


def main():
    ap = argparse.ArgumentParser(description="Rebalance the answer key by reordering options")
    ap.add_argument("--scope", choices=sorted(SCOPES), default="vic")
    ap.add_argument("--db", default=DB)
    ap.add_argument("--seed", type=int, default=20260810)
    ap.add_argument("--manifest", default=str(MANIFEST))
    ap.add_argument("--dry-run", action="store_true", help="report only; the default")
    ap.add_argument("--apply", action="store_true", help="write the changes")
    ap.add_argument("--force", action="store_true", help="re-run over an already-repaired scope")
    ap.add_argument("--revert", metavar="MANIFEST", help="restore every row in a manifest")
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row

    if args.revert:
        return revert(conn, pathlib.Path(args.revert), args.apply)

    where = SCOPES[args.scope]
    rows = [dict(r) for r in conn.execute(
        f"SELECT * FROM questions WHERE {where} AND review_status != 'rejected'")]
    print(f"scope {args.scope!r}: {len(rows)} questions (rejected excluded)")
    report_by_book(rows, "BEFORE")

    blocked, eligible = [], []
    for q in rows:
        b = blocker(q)
        (blocked if b else eligible).append((q, b) if b else q)

    print(f"\n  blocked from reordering: {len(blocked)}")
    for reason, n in collections.Counter(b for _, b in blocked).most_common():
        print(f"    {reason:22s} {n}")
    named = sum(1 for q in eligible if explanation_names_option(q["explanation"]))
    print(f"  eligible: {len(eligible)}   of which explanation names an option letter: {named}")

    rng = random.Random(args.seed)
    by_book = collections.defaultdict(list)
    for q in eligible:
        by_book[(q["subject"], q["source_book"])].append(q)

    changes = []
    for key in sorted(by_book):
        group = by_book[key]
        targets = plan_group(group, rng)
        for q in group:
            ch = build_change(q, targets[q["id"]], rng)
            if ch:
                changes.append(ch)

    after = [dict(r) for r in rows]
    idx = {c["id"]: c for c in changes}
    for r in after:
        if r["id"] in idx:
            r["correct_answer"] = idx[r["id"]]["new_key"]
    report_by_book(after, "AFTER (projected)")

    remapped = sum(1 for c in changes if c["explanation_remapped"])
    print(f"\n  reordered: {len(changes)}   explanations rewritten: {remapped} "
          f"({sum(c['explanation_remapped'] for c in changes)} letter references)")

    manifest = {
        "version": VERSION,
        "tool": "repair_key_skew",
        "written_at": datetime.now(timezone.utc).isoformat(),
        "scope": args.scope,
        "seed": args.seed,
        "db": args.db,
        "counts": {
            "in_scope": len(rows), "eligible": len(eligible),
            "reordered": len(changes), "blocked": len(blocked),
            "explanations_rewritten": remapped,
        },
        "before": {"all": distribution(rows)},
        "after": {"all": distribution(after)},
        "blocked": [{"id": q["id"], "subject": q["subject"],
                     "source_book": q["source_book"], "reason": b,
                     "stem": q["stem"], "explanation": q["explanation"],
                     "options": {L: q["option_" + L.lower()] for L in LETTERS},
                     "correct_answer": q["correct_answer"]}
                    for q, b in blocked],
        "changes": changes,
    }

    if not args.apply:
        print("\n  --dry-run: nothing written. Re-run with --apply to commit.")
        path = pathlib.Path(args.manifest).with_suffix(".dryrun.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(manifest, indent=1, ensure_ascii=False))
        print(f"  plan written to {path}")
        return 0

    live = pathlib.Path(args.manifest)
    if live.exists() and not args.force:
        print(f"\n  REFUSING: {live} already exists. A second shuffle would rebase its "
              f"'before' state and make --revert restore the wrong thing.\n"
              f"  --revert it first, or pass --force if you know the scope is disjoint.")
        return 1

    with conn:
        for c in changes:
            a = c["after"]
            conn.execute(
                "UPDATE questions SET option_a=?, option_b=?, option_c=?, option_d=?, "
                "correct_answer=?, explanation=? WHERE id=?",
                (a["option_a"], a["option_b"], a["option_c"], a["option_d"],
                 a["correct_answer"], a["explanation"], c["id"]))
    live.parent.mkdir(parents=True, exist_ok=True)
    live.write_text(json.dumps(manifest, indent=1, ensure_ascii=False))
    print(f"\n  applied {len(changes)} reorderings. manifest -> {live}")

    check = [dict(r) for r in conn.execute(
        f"SELECT * FROM questions WHERE {where} AND review_status != 'rejected'")]
    report_by_book(check, "AFTER (verified from the database)")
    return 0


def revert(conn, path, apply):
    m = json.loads(path.read_text())
    changes = m["changes"]
    print(f"reverting {len(changes)} rows from {path}")
    if not apply:
        print("  --dry-run: nothing written. Add --apply to commit.")
        return 0
    with conn:
        for c in changes:
            b = c["before"]
            conn.execute(
                "UPDATE questions SET option_a=?, option_b=?, option_c=?, option_d=?, "
                "correct_answer=?, explanation=? WHERE id=?",
                (b["option_a"], b["option_b"], b["option_c"], b["option_d"],
                 b["correct_answer"], b["explanation"], c["id"]))
    path.rename(path.with_suffix(".reverted.json"))
    print(f"  reverted. manifest renamed to {path.with_suffix('.reverted.json')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
