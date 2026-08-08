#!/usr/bin/env python3
"""Shared machinery for the NSW Thinking Skills (logical_reasoning) figural builders.

Same discipline as tools/ma/ma_common.py: `Q` takes the key and each distractor as
computed values and every item must supply `verify`, the same answer by a second route.

Figural items are where that matters most. A shape question's answer is a property of the
picture, so if the answer is typed by hand it can drift away from what was drawn and
nothing downstream will notice — the figure looks fine, the maths looks fine, and only a
reader who counts the squares finds the disagreement. Here the answer is computed from the
same cell list `shapes_row` draws, a rotation is computed by `rotate_cells` rather than
pictured mentally, and a seven-segment answer is computed from the SEGMENTS table the
display is drawn from.

`tile_by_copies` builds a target shape by actually placing k copies of a piece, so a
question asking how many copies fit cannot claim a tiling that does not exist.
"""
import datetime
import json
import math
import pathlib
import sys
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.figure_lib import rotate_cells  # noqa: E402

GEN = ROOT / "run_data/output/logical_reasoning/generated"
BOOK = "lr_thinking_skills"
FAMILY = {"5.2": "Critical Reasoning", "5.3": "Logic Puzzles", "5.4": "Figural Reasoning"}


def _plan():
    p = json.loads((GEN / "lr_PLAN.json").read_text(encoding="utf-8"))
    return {c["key"]: c for c in p["categories"]}


PLAN = _plan()


def tile_by_copies(piece, offsets):
    """Place copies of `piece` at each offset and return the union — raising if any two
    copies overlap. The shape is built from the copies, so "how many copies fit" is
    answered by construction rather than by assertion."""
    seen = set()
    for dc, dr in offsets:
        for c, r in piece:
            cell = (c + dc, r + dr)
            if cell in seen:
                raise ValueError(f"copies overlap at {cell}")
            seen.add(cell)
    return sorted(seen)


def bounding(cells):
    cs = [c for c, _ in cells]
    rs = [r for _, r in cells]
    return max(cs) - min(cs) + 1, max(rs) - min(rs) + 1


def perimeter(cells):
    """Edge length of a polyomino: four sides per square, less two per shared edge."""
    s = set(cells)
    return sum(1 for c, r in s for d in ((1, 0), (-1, 0), (0, 1), (0, -1))
               if (c + d[0], r + d[1]) not in s)


def symmetry_order(cells):
    """How many of the four quarter turns leave the shape looking the same."""
    base = sorted(cells)
    return sum(1 for k in range(4) if rotate_cells(base, k) == base)


class Batch:
    def __init__(self, nn, now="2026-08-08T13:00:00Z"):
        self.nn = nn
        self.now = now
        self.items = []

    def Q(self, cat, stem, key, wrong, expl, verify,
          difficulty="medium", confidence=0.92, fig=None, fmt=str, no_shuffle=False):
        if verify is None:
            raise ValueError(f"{cat}: every item needs an independent `verify` route")
        if isinstance(key, float) or isinstance(verify, float):
            ok = math.isclose(float(key), float(verify), rel_tol=1e-9, abs_tol=1e-9)
        else:
            ok = key == verify
        if not ok:
            raise AssertionError(
                f"{cat}: the two routes disagree — key={key!r} but verify={verify!r}. "
                f"One of them is wrong; do not 'fix' this by deleting the check.")
        if len(wrong) != 3:
            raise ValueError(f"{cat}: need exactly 3 distractors, got {len(wrong)}")
        opts = [fmt(key)] + [fmt(v) for v in wrong]
        if len(set(opts)) != 4:
            raise AssertionError(f"{cat}: options collide after formatting: {opts}")

        c = PLAN[cat]
        q = {
            "id": str(uuid.uuid4()),
            "subject": "logical_reasoning",
            "stem": stem,
            "option_a": opts[0], "option_b": opts[1],
            "option_c": opts[2], "option_d": opts[3],
            "correct_answer": "A",
            "explanation": expl,
            "topic": f"{FAMILY[c['section']]} — {c['title']}",
            "difficulty": difficulty,
            "confidence": confidence,
            "source_book": BOOK,
            "source_page": self.nn,
            "source_page_description": f"Category: {cat} — {c['title']}",
            "passage": None,
            "figure_svg": fig,
            "review_status": "pending",
            "created_at": self.now,
        }
        if no_shuffle:
            q["no_shuffle"] = True
        self.items.append(q)
        return q

    def write(self):
        GEN.mkdir(parents=True, exist_ok=True)
        path = GEN / f"{BOOK}_p{self.nn}.json"
        path.write_text(json.dumps(self.items, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
        print(f"wrote {len(self.items)} questions -> {path}")
        return path
