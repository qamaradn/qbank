#!/usr/bin/env python3
"""Shared machinery for the VIC informational inference top-up batches.

WHY THESE BUILDERS DIFFER FROM EVERY OTHER rc/ BUILDER

They do not author a passage. vic_reading_TASK.md §2 caps informational at 372 of 743
while we already hold ~670 informational questions over 144 ACT passages. The passages are
good — 160 words median, right level, Australian context — and what is short is
inference-led QUESTIONS, not text. So these builders read the passage out of the database
and write new questions against it.

THE PASSAGE MUST COME BACK OUT BYTE-IDENTICAL. Selectly derives passageId by hashing the
passage text, so a single drifted character splits the group and the student is shown the
same passage twice in one drill. The text is therefore never retyped here: it is SELECTed,
matched on a prefix for identification only, and passed through untouched. `fetch_passages`
refuses to continue unless each prefix matches exactly one passage.

WHAT MAKES AN ITEM ADMISSIBLE (§3)

The defect being repaired is that 67.5% of the existing ACT reading questions are
retrieval wearing an inference stem — 37% of their implies/suggests items are answered by
a near-verbatim restatement of one passage sentence. Every key here must therefore pass
`question_checks.key_restates_passage`: under 35% content-word overlap with the passage, a
threshold fitted to 40 hand-labelled questions (82% accuracy, 95% precision).

That leaves three honest ways to answer: synthesis across separated statements, the
FUNCTION of a sentence or example, or the stance a word choice commits the author to.
"""
import pathlib
import sqlite3
import sys
import uuid
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

DB = ROOT / "run_data/db/qbank.db"
GEN = ROOT / "run_data/output/reading_comprehension/generated"
BOOK = "rc_vic_inference"

# `structure` and `comparison` ask the student to hold the whole text in view at once
# rather than one sentence, so they are the two skills marked hard.
HARD_SKILLS = {"structure", "comparison"}

# CONFIDENCE IS AUTHORED PER ITEM, NOT SET TO A CONSTANT
#
# The surrounding ACT questions carry Gemini's own confidence, which is near-uniformly
# high and therefore useless as a triage signal — the review UI shows confidence so a
# reviewer can decide where to look first, and a column of 0.95 tells them nothing. These
# items are written and judged by a different model, so the number is a genuine second
# opinion and worth spending.
#
# What it scores is ONE thing: how safe is the key against its strongest rival? Not how
# hard the question is, and not how well written it is.
#
#   0.95-0.98  the key is the only defensible reading; every distractor fails on
#              something the passage states outright
#   0.88-0.94  the key is clearly best; the strongest rival needs a misreading a careful
#              student would not make
#   0.80-0.87  the key is best but the strongest rival is arguable — a reviewer should
#              read this one properly
#   below 0.80 do not ship it; rewrite the rival or drop the item
#
# Items turning on the FUNCTION of a phrase ("this works to...") sit lower by default than
# items turning on a stated relation, because function is a matter of degree and a
# reasonable reader can rank two purposes differently.
MIN_CONFIDENCE = 0.80


def fetch_passages(passages):
    """passages: [(title, source_book, source_page, unique_prefix)] -> {title: text}."""
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    out = {}
    for title, book, page, prefix in passages:
        rows = {r["passage"] for r in conn.execute(
            "SELECT passage FROM questions WHERE source_book=? AND source_page=? "
            "AND review_status!='rejected' AND passage LIKE ?", (book, page, prefix + "%"))}
        if len(rows) != 1:
            raise SystemExit(f"{title}: prefix matched {len(rows)} passages, expected 1 "
                             f"— tighten the prefix in PASSAGES")
        out[title] = rows.pop()
    return out


def build(passages, items, page):
    """Assemble one batch. `items` maps title -> list of
    (skill, stem, [A,B,C,D], key, explanation, {key_letter: relation}, quote_lines,
    confidence)."""
    texts = fetch_passages(passages)
    now = datetime.now(timezone.utc).isoformat()
    qs = []
    for title, book, src_page, _ in passages:
        passage = texts[title]
        for skill, stem, opts, key, expl, rel, quotes, conf in items[title]:
            if not MIN_CONFIDENCE <= conf <= 1.0:
                raise SystemExit(f"{title}/{skill}: confidence {conf} outside "
                                 f"[{MIN_CONFIDENCE}, 1.0] — see the rubric above")
            qs.append({
                "id": str(uuid.uuid5(uuid.NAMESPACE_URL,
                                     f"qbank/{BOOK}/{title}/{skill}/{stem[:40]}")),
                "subject": "reading_comprehension",
                "stem": stem,
                "option_a": opts[0], "option_b": opts[1],
                "option_c": opts[2], "option_d": opts[3],
                "correct_answer": key,
                "explanation": expl,
                "topic": "Informational inference",
                "difficulty": "hard" if skill in HARD_SKILLS else "medium",
                "confidence": conf,
                "source_book": BOOK,
                "source_page": page,
                "source_page_description": f"[reuses {book} p{src_page} passage: {title}]",
                "passage": passage,
                "figure_svg": None,
                "review_status": "pending",
                "created_at": now,
                # authored by letter for readability next to the options list; the checker
                # wants distractor TEXT as the key so the map survives the answer shuffle.
                "relations": {opts["ABCD".index(L)]: r for L, r in rel.items()},
                "passage_title": title,
                "skill": skill,
                "quote_lines": quotes,
                "extracts": [],
            })
    return qs


def write(qs, page):
    """Write the batch, refusing to clobber one that has already been loaded.

    rc_finalise rebalances keys in place and its choice is not reproducible between runs,
    so re-running a builder after its batch is in the database rewrites the file with a
    DIFFERENT key assignment from the rows students are served. That desync is silent —
    the ids still match, only the answers move. Learned the hard way on p1.
    """
    import json
    loaded = GEN / f"{BOOK}_LOADED.json"
    if loaded.exists() and f"{BOOK}_p{page}.json" in loaded.read_text():
        raise SystemExit(
            f"batch p{page} is already recorded in {loaded.name}. Rebuilding it would "
            f"rewrite the file with keys that no longer match the loaded rows. Edit the "
            f"database, or remove the entry deliberately if you intend to re-load.")
    out = GEN / f"{BOOK}_p{page}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(qs, indent=1, ensure_ascii=False))
    print(f"{len(qs)} questions -> {out}")
    return out
