#!/usr/bin/env python3
"""Shared machinery for the NSW Reading structural/organisation cloze (taxonomy §3.6).

The gap marker is `[ 1 ]`, because here the gap is a whole SENTENCE rather than a word.
The vocabulary cloze uses `___ (n) ___`, which still looks like a blank. Both survive
markdown: the original `___(1)___` did not — underscores tight against content open
emphasis, so `marked` in the review UI ate them and showed a bare "(1)" with no blank in
it, while Selectly, which renders the passage as plain text, showed it correctly. See
tools/repair_cloze_marker.py.

A sentence has been removed from a passage and the student must put it back. The type is
closer to the vocabulary cloze than to comprehension — same gap markers, same one-question-
per-gap group model — but what is removed is a whole sentence, and what makes an option
wrong is cohesion rather than meaning.

THE PASSAGE IS STORED WHOLE AND THE GAPS ARE CUT FROM IT. A paragraph is a list of
sentences; a gap is written in place as `GAP(n, "the sentence that was removed")`. `render`
emits the passage with `[ n ]` where the gap sits, and `key_of` hands back the removed
sentence for the option list. So the correct answer is BY CONSTRUCTION the sentence the
passage is missing — it cannot drift from the text the way a retyped key can, which is the
same discipline `context()` and `quote()` enforce for the other two types.

STEMS CARRY A LOCATOR, AND THAT IS NOT DECORATION. "Which sentence best fills gap (1)?"
is identical for every item in the type, and phase 4 drops near-duplicate stems at 0.85
SILENTLY — a whole batch would collapse to one row. Quoting the words either side of the
gap makes each stem unique and, incidentally, tells the student where to look.
"""
import datetime
import re
import uuid

NOW = datetime.datetime(2026, 8, 6, 10, 0, 0, tzinfo=datetime.timezone.utc) \
    .isoformat().replace("+00:00", "Z")

# The structural roles a removed sentence can play. Declared per gap rather than inferred,
# and checked for spread across a passage: four gaps that all want a topic sentence test
# one thing four times.
ROLES = {"topic_sentence", "supporting_detail", "example", "contrast",
         "transition", "conclusion"}


class GAP:
    """A removed sentence, held in the passage where it belongs."""

    def __init__(self, n, sentence):
        self.n = n
        self.sentence = sentence


def render(paragraphs) -> str:
    """The passage as the student sees it: gaps replaced by numbered markers."""
    out = []
    for para in paragraphs:
        out.append(" ".join(f"[ {s.n} ]" if isinstance(s, GAP) else s for s in para))
    return "\n\n".join(out)


def flat(paragraphs):
    """Every sentence and gap in reading order, so a gap can see its neighbours."""
    return [s for para in paragraphs for s in para]


def key_of(paragraphs, n):
    for s in flat(paragraphs):
        if isinstance(s, GAP) and s.n == n:
            return s.sentence
    raise ValueError(f"no gap {n} in the passage")


def locator(paragraphs, n, words=7):
    """The words either side of gap n, cut from the passage.

    Both sides where they exist; a gap that opens or closes the passage gets the one side
    it has. Generated, so a locator cannot quote something the passage does not say.
    """
    seq = flat(paragraphs)
    i = next(k for k, s in enumerate(seq) if isinstance(s, GAP) and s.n == n)
    before = [s for s in seq[:i] if not isinstance(s, GAP)]
    after = [s for s in seq[i + 1:] if not isinstance(s, GAP)]
    def cut(sentence, tail):
        """Quote a neighbour, marking with an ellipsis ONLY the end actually cut.

        Appending "..." unconditionally produced "Almost none of this is fair...." on
        every neighbour short enough to quote whole — four dots, which reads as a typo.
        """
        w = sentence.split()
        if len(w) <= words:
            return sentence
        return ("..." + " ".join(w[-words:])) if tail else (" ".join(w[:words]) + "...")

    lead = cut(before[-1], tail=True) if before else ""
    trail = cut(after[0], tail=False) if after else ""
    if lead and trail:
        return f'The gap comes after "{lead}" and before "{trail}"'
    if lead:
        return f'The gap comes after "{lead}" and ends the passage'
    return f'The gap opens the passage, before "{trail}"'


def build(passages, book, nn, category="structural_cloze", label="Structural cloze",
          now=NOW):
    """passages: [{title, topic, paragraphs, items}] with
    item = (gap_n, role, difficulty, confidence, distractors, explanation)
    """
    out = []
    for p in passages:
        passage = render(p["paragraphs"])
        for n, role, diff, conf, distractors, expl in p["items"]:
            key = key_of(p["paragraphs"], n)
            if key in passage:
                raise ValueError(f"{p['title']} gap {n}: the removed sentence is still in "
                                 f"the rendered passage")
            opts = [key] + [d for d, _ in distractors]
            out.append({
                "id": str(uuid.uuid4()),
                "subject": "reading_comprehension",
                "stem": f"{locator(p['paragraphs'], n)} "
                        f"Which sentence best fills gap ({n})?",
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
                "passage": passage,
                "figure_svg": None,
                "review_status": "pending",
                "created_at": now,
                "passage_title": p["title"],
                "skill": role,
                "blank": n,
                "quote_lines": [],
                "extracts": [],
                "relations": {d: r for d, r in distractors},
            })
    return out


BLANK_RE = re.compile(r"\[ (\d+) \]")
