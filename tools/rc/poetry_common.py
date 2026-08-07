#!/usr/bin/env python3
"""Shared machinery for the NSW Reading poetry batches (taxonomy §3.3).

Each batch file is data — the poems and their items — and calls `build()`. The three
functions here are the parts that must not drift between batches, because each of them is
load-bearing for how the question renders or for whether it can be trusted:

`render`  assembles the passage. Lines within a stanza are joined with markdown's hard
          break (two trailing spaces), because the review UI parses the passage with
          `marked` and would otherwise fold a stanza into one paragraph. No markdown
          emphasis anywhere: Selectly puts the same text in a `white-space: pre-wrap` div
          as PLAIN TEXT (McqQuestion.tsx), so a student would be shown the asterisks.
          Newlines and trailing spaces are the only formatting that survives both.

`quote`   cuts the quoted lines out of the poem instead of letting an author retype them,
          so a stem cannot quote something the poem does not say. The lines go into
          `quote_lines` for `rc_finalise` to re-check against the stored passage.

`build`   emits rows with `correct_answer` always "A"; `rc_finalise` reassigns the letters
          to keep the running A/B/C/D counts level across the whole book.
"""
import datetime
import uuid

NOW = datetime.datetime(2026, 8, 6, 10, 0, 0, tzinfo=datetime.timezone.utc) \
    .isoformat().replace("+00:00", "Z")

# item = (skill, difficulty, confidence, quote_refs, stem, key, distractors, explanation)
# quote_refs are (stanza, line) indices; "{q}" in the stem is replaced by those lines.


def render(poem) -> str:
    """Title, blank line, then stanzas with hard line breaks between lines."""
    body = "\n\n".join("  \n".join(lines) for lines in poem["stanzas"])
    return f"{poem['title']}\n\n{body}"


def quote(poem, refs):
    """Cut the named lines out of the poem. Never retyped, so it cannot disagree.

    The trailing comma of a mid-sentence line is dropped from what the stem SHOWS, since
    `"a coin that is not money here," The line shows...` reads as a mistake. `quote_lines`
    keeps the lines exactly as the poem has them, so the finaliser still checks the quote
    against the passage verbatim.
    """
    lines = [poem["stanzas"][s][ln] for s, ln in refs]
    shown = list(lines)
    shown[-1] = shown[-1].rstrip(",")
    return " / ".join(shown), lines


def build(poems, book, nn, category="poetry", label="Poetry", now=NOW):
    out = []
    for poem in poems:
        passage = render(poem)
        for skill, diff, conf, refs, stem_tpl, key, distractors, expl in poem["items"]:
            shown, lines = quote(poem, refs)
            opts = [key] + [d for d, _ in distractors]
            out.append({
                "id": str(uuid.uuid4()),
                "subject": "reading_comprehension",
                "stem": stem_tpl.format(q=shown),
                "option_a": opts[0], "option_b": opts[1],
                "option_c": opts[2], "option_d": opts[3],
                "correct_answer": "A",
                "explanation": expl,
                "topic": poem["topic"],
                "difficulty": diff,
                "confidence": conf,
                "source_book": book,
                "source_page": nn,
                "source_page_description": f"Category: {category} — {label}",
                "passage": passage,
                "figure_svg": None,
                "review_status": "pending",
                "created_at": now,
                "passage_title": poem["title"],
                "skill": skill,
                "quote_lines": lines,
                "extracts": [],
                "relations": {d: r for d, r in distractors},
            })
    return out
