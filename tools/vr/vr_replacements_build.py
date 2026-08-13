#!/usr/bin/env python3
"""Replacement verbal questions for holes left in dealt drill forms.

Same contract as tools/qr/qr_replacements_build.py: each item names the form it is
replacing a question in, and REPL_FORMS selects which wave to write so a reload cannot
re-offer questions already in the bank.

Distractor design follows tools/vr/vr_p*_build.py: every distractor declares HOW it is
wrong, and the three must not cohere into a set that leaves the key as the semantic
singleton -- the measured defect that shaped the whole VIC verbal top-up.
"""
import datetime
import json
import os
import pathlib
import sys
import uuid

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

GEN = pathlib.Path(__file__).resolve().parents[2] / "run_data/output/verbal_reasoning/generated"
BOOK = "vr_vic_replacements"
NOW = datetime.datetime(2026, 8, 13, 11, 0, 0, tzinfo=datetime.timezone.utc) \
    .isoformat().replace("+00:00", "Z")

# ---------------------------------------------------------------- wave 1: rv-030
# Replaces a "word-pattern letter removal" item that could not be answered. Its two
# worked examples used different rules -- BLEND -> LEND drops the first letter, but
# CRANE -> RACE drops the N and reorders what is left -- and the word it asked about,
# SPINE, yields a real word under either reading: PINE by dropping S, SINE by dropping
# P, and BOTH were on the option list. Its explanation was the model arguing with
# itself and never settling ("...actually the rule is remove the first two letters...").
#
# The replacement is shades-of-meaning, which the brief wants and this form did not
# test, rather than another word-pattern item: word codes and letter puzzles are the
# off-spec family in the first place.
ITEMS = [
    ("hurried",
     "The note had not merely been written in a hurry; it was so rushed that whole "
     "words were missing. Which word describes that greater degree of haste?",
     "frantic",
     [("brisk", "nuance — quick and businesslike, which is not the same as rushed"),
      ("unhurried", "opposite — the absence of haste altogether"),
      ("illegible", "consequence — describes the result of the haste, not the haste")],
     "Frantic describes haste so great it becomes disordered, which is what missing "
     "words show; 'brisk' is merely quick and controlled, a lesser degree rather than "
     "a greater one, and 'illegible' names what the rushing produced rather than how "
     "rushed it was.",
     "medium", 0.92, "vic-drill-rv-030"),
]


def build(items):
    out = []
    for target, stem, key, distractors, expl, diff, conf, form in items:
        rels = [r for _, r in distractors]
        assert len(set(rels)) == len(rels), f"{target}: two distractors wrong the same way"
        opts = [key] + [d for d, _ in distractors]
        assert len(set(opts)) == 4, f"{target}: options collide"
        out.append({
            "id": str(uuid.uuid4()),
            "subject": "verbal_reasoning",
            "stem": stem,
            "option_a": opts[0], "option_b": opts[1],
            "option_c": opts[2], "option_d": opts[3],
            "correct_answer": "A",
            "explanation": expl,
            "topic": "Shades of meaning / connotation",
            "difficulty": diff,
            "confidence": conf,
            "source_book": BOOK,
            "source_page": 1,
            "source_page_description":
                f"Category: shades_of_meaning — Shades of meaning / connotation "
                f"[target: {target}]",
            "passage": None,
            "figure_svg": None,
            "review_status": "pending",
            "created_at": NOW,
            "_target_form": form,
            "_relations": {d: r for d, r in distractors},
        })
    return out


if __name__ == "__main__":
    GEN.mkdir(parents=True, exist_ok=True)
    want = {f.strip() for f in os.environ.get("REPL_FORMS", "").split(",") if f.strip()}
    items = [i for i in ITEMS if not want or i[-1] in want]
    if want and not items:
        raise SystemExit(f"REPL_FORMS matched nothing: {sorted(want)}")
    nn = int(os.environ.get("REPL_PAGE", 1))
    qs = build(items)
    path = GEN / f"{BOOK}_p{nn}.json"
    path.write_text(json.dumps(qs, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(qs)} questions -> {path}")
    for q in qs:
        print(f"   {q['_target_form']}  {q['topic']}")
