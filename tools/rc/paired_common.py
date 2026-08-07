#!/usr/bin/env python3
"""Shared machinery for the NSW Reading paired-extract and multi-extract types (§3.4, §3.5).

TWO OR MORE TEXTS, ONE `passage` COLUMN. There is nowhere else to put them: `questions.
passage` is a single column, Selectly hashes it to form `passageId` (so all the items of a
set group together), and `push_to_selectly.py` prepends the whole string to the stem. A
paired set is therefore ONE passage holding several labelled extracts:

    Text 1
    <first extract>

    Text 2
    <second extract>

Labels are plain text, never markdown — Selectly renders the passage in a `pre-wrap` div
without parsing it, so `**Text 1**` would show the asterisks to the student.

WHY `min_cross_extract` EXISTS. The failure mode for this type is a set where every
question can be answered from one extract: the second text is then decoration, the student
never compares anything, and the item is ordinary single-passage comprehension that took
twice as long to write. Each item therefore declares which extracts it needs, and
`rc_finalise` fails a group that does not reach across enough of them.

Sentences are stored as lists so a stem can quote by index rather than by retyping —
the same discipline as `quote()` for poetry and `GAP` for the structural cloze.
"""
import datetime
import uuid

NOW = datetime.datetime(2026, 8, 6, 10, 0, 0, tzinfo=datetime.timezone.utc) \
    .isoformat().replace("+00:00", "Z")


def render(passage) -> str:
    """Label, blank line, extract text; extracts separated by a blank line."""
    blocks = []
    for label, sentences in passage["extracts"]:
        # Two trailing spaces: markdown's hard break. Without it the review UI collapses
        # the newline and shows "Text 1 The Riverbend Primary Spring Fete will be..." as
        # one run of prose, with the label swallowed into the first sentence. Selectly
        # renders pre-wrap and honours the newline either way, so the spaces are free.
        if not label:                      # single-passage: no heading to render
            blocks.append(" ".join(sentences))
            continue
        blocks.append(f"{label}  \n" + " ".join(sentences))
    return "\n\n".join(blocks)


def quote(passage, refs):
    """Cut the named sentences out of the named extracts. Never retyped.

    refs are (extract_index, sentence_index) pairs. Returns the text to show and the
    verbatim sentences for `quote_lines`, which rc_finalise re-checks against the stored
    passage.
    """
    lines = [passage["extracts"][e][1][s] for e, s in refs]
    # Join adjacent sentences with a space, but mark a jump with an ellipsis. Running two
    # non-adjacent sentences together presents the passage as saying something continuous
    # that it does not, and quietly hides whatever sat between them.
    shown = lines[0]
    for (e, i), (pe, pi), line in zip(refs[1:], refs[:-1], lines[1:]):
        shown += (" " if (e == pe and i == pi + 1) else " ... ") + line
    return shown, lines


def build(passages, book, nn, category, label, now=NOW):
    """passages: [{title, topic, extracts, items}] with
    item = (skill, difficulty, confidence, uses, quote_refs, stem, key, distractors, expl)
    `uses` is the list of extract labels the question genuinely needs.
    """
    out = []
    for p in passages:
        text = render(p)
        for skill, diff, conf, uses, refs, stem_tpl, key, distractors, expl in p["items"]:
            shown, lines = quote(p, refs) if refs else ("", [])
            opts = [key] + [d for d, _ in distractors]
            out.append({
                "id": str(uuid.uuid4()),
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
                "source_page": nn,
                "source_page_description": f"Category: {category} — {label}",
                "passage": text,
                "figure_svg": None,
                "review_status": "pending",
                "created_at": now,
                "passage_title": p["title"],
                "skill": skill,
                "quote_lines": lines,
                "extracts": list(uses),
                "relations": {d: r for d, r in distractors},
            })
    return out
