#!/usr/bin/env python3
"""Builds lr_thinking_skills_p35.json — the last 2 questions.

necessary vs sufficient 2, closing that subcategory at 45/45 and with it every named
subcategory in §5.2, §5.3 and §5.4. p33 was allocated three of these when five were
outstanding; the shortfall only showed up in the per-category tally after p34 loaded.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.lr.lr_common import Batch  # noqa: E402
from tools.lr.lr_logic import IFo, ISo, NOTHING, NOTo, Scenario  # noqa: E402

B = Batch(nn=35)


def conditional(stem, a, b, given, options, expl, **kw):
    S = Scenario([a, b], rules=[IFo(a, b)], given=[given])
    resolved = [(t, f(S) if callable(f) else f) for t, f in options]
    key = S.pick(resolved)
    B.Q("necessary_vs_sufficient", stem, key=key, verify=key,
        wrong=[t for t, _ in resolved if t != key], expl=expl, **kw)


conditional(
    "A boat cannot leave the marina unless the tide is above two metres. This morning the "
    "tide never rose above one and a half metres. Which one of these must be true?",
    "left", "tide", NOTo("tide"),
    [("No boat left the marina this morning", lambda S: S.here(NOTo("left"))),
     ("A boat left the marina this morning", lambda S: S.here(ISo("left"))),
     ("A tide above two metres always sends boats out",
      lambda S: S.always(IFo("tide", "left"))),
     ("Nothing follows about whether a boat left", NOTHING)],
    "A tide above two metres is required before any boat can leave, and it never got "
    "there, so none did. A high tide would not have made anyone leave either — it only "
    "makes leaving possible.",
    difficulty="medium", confidence=0.92)

conditional(
    "Reaching the semi-final is enough on its own to earn a trophy. Devi's team did not "
    "reach the semi-final. Which one of these must be true?",
    "semi", "trophy", NOTo("semi"),
    [("Nothing follows about whether the team earned a trophy", NOTHING),
     ("The team earned a trophy", lambda S: S.here(ISo("trophy"))),
     ("The team earned no trophy", lambda S: S.here(NOTo("trophy"))),
     ("Only teams reaching the semi-final earn a trophy",
      lambda S: S.always(IFo("trophy", "semi")))],
    "Reaching the semi-final would have earned a trophy, but the rule never says that is "
    "the only route to one. The team may have taken a trophy for fair play or for most "
    "improved.",
    difficulty="hard", confidence=0.90)

B.write()
