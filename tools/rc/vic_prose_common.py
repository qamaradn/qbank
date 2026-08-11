#!/usr/bin/env python3
"""Shared machinery for the VIC authored-prose reading batches — narrative and persuasive.

vic_reading_TASK.md §2 needs 156 narrative and 81 persuasive items, and the bank holds
essentially none of either: of 144 ACT passages ~93% are informational, 6-10 are narrative
and none are persuasive. So unlike the informational top-up, these builders author their
own passages.

WHAT THIS MODULE GUARANTEES

`render`  joins paragraphs with a blank line. Prose needs no hard line breaks -- that is a
          verse problem -- but the passage must be one string, identical across every row
          of its group, because Selectly derives passageId by hashing it.

`quote`   cuts quoted text OUT of the passage rather than letting an author retype it, and
          fails loudly if the fragment is not there. A stem that misquotes its own passage
          is unanswerable, and retyping is how that happens.

`build`   emits every row with `correct_answer` "A"; rc_finalise reassigns the letters to
          keep the running A/B/C/D counts level across the book.

CONFIDENCE IS AUTHORED PER ITEM, on the rubric in vic_inference_common.py: it scores how
safe the key is against its strongest rival, nothing else. A flat constant would tell the
reviewer nothing, which is the state the Gemini-generated bank is already in.

THE RESTATEMENT RULE APPLIES HERE. These are prose passages of roughly ACT length, so
`question_checks.key_restates_passage` transfers directly -- unlike verse, where it was
deliberately switched off. Keep character names out of keys where a pronoun will do: a
name is a content word, and two of them in a short key can trip the threshold without the
item being retrieval at all.
"""
import pathlib
import sys
import uuid
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

GEN = ROOT / "run_data/output/reading_comprehension/generated"

HARD_SKILLS = {"structure", "comparison", "symbolism"}


def render(passage):
    return "\n\n".join(passage["paragraphs"])


def quote(text, fragments):
    """Verify each fragment appears verbatim, and join them for display."""
    for f in fragments:
        if f not in text:
            raise SystemExit(f"quoted fragment not in passage: {f[:70]!r}")
    shown = " ... ".join(f.rstrip(" ,.") for f in fragments)
    return shown, list(fragments)


def build(passages, book, page, category, label):
    now = datetime.now(timezone.utc).isoformat()
    out = []
    for p in passages:
        text = render(p)
        for skill, diff, conf, frags, stem_tpl, key, distractors, expl in p["items"]:
            shown, lines = quote(text, frags)
            opts = [key] + [d for d, _ in distractors]
            out.append({
                "id": str(uuid.uuid5(uuid.NAMESPACE_URL,
                                     f"qbank/{book}/{p['title']}/{skill}/{stem_tpl[:40]}")),
                "subject": "reading_comprehension",
                "stem": stem_tpl.format(q=shown),
                "option_a": opts[0], "option_b": opts[1],
                "option_c": opts[2], "option_d": opts[3],
                "correct_answer": "A",
                "explanation": expl,
                "topic": p["topic"],
                "difficulty": diff,
                "confidence": conf,
                "source_book": book,
                "source_page": page,
                "source_page_description": f"Category: {category} — {label}",
                "passage": text,
                "figure_svg": None,
                "review_status": "pending",
                "created_at": now,
                "passage_title": p["title"],
                "skill": skill,
                "quote_lines": lines,
                "extracts": [],
                "relations": {d: r for d, r in distractors},
            })
    return out


def write(qs, book, page):
    import json
    loaded = GEN / f"{book}_LOADED.json"
    if loaded.exists() and f"{book}_p{page}.json" in loaded.read_text():
        raise SystemExit(
            f"batch p{page} is already recorded in {loaded.name}. Rebuilding it would "
            f"rewrite the file with keys that no longer match the loaded rows.")
    out = GEN / f"{book}_p{page}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(qs, indent=1, ensure_ascii=False))
    print(f"{len(qs)} questions over {len({q['passage_title'] for q in qs})} passages -> {out}")
    return out
