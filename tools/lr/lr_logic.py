#!/usr/bin/env python3
"""Model checking for the reasoning questions in §5.2 and §5.3.

A "which must be true" question has one failure mode that careful writing does not
prevent: a distractor that also follows. It cannot be found by reading, because reading
is the faculty being tested — the writer who missed it while composing the option will
miss it again while checking. It has to be decided mechanically.

Both checkers here do the same thing at different grain. Build every world in which the
premises hold; keep a conclusion only if it holds in all of them; run that over all four
options and refuse unless exactly one survives. That verifies the key and clears the
three distractors in one pass.

  set_entails / syllogism  — categories as subsets of a small universe, for All/Some/No.
  Scenario                 — named facts as booleans, for if-then reasoning.

Categories in the set checker are required non-empty. That is existential import, the
traditional reading, and the one a Year 6 student uses: "all boronias are flowers" is
heard as saying there are boronias. Without it "some flowers are scented" stops
following.

WHY Scenario RUNS TWO OCCASIONS
------------------------------
The obvious encoding gives each fact one boolean and calls it done. It silently breaks
every question whose distractor is a general rule.

Take: "If the ferry is cancelled the tour is called off; if the tour is called off
refunds are given; the ferry was cancelled." With one boolean each, the premises pin
down exactly one world — cancelled, called off, refunds — and in that single world the
converse "refunds are given ONLY when the ferry is cancelled" is true as well. The
checker would report it as entailed and refuse to build, or worse would have passed it
as a second correct answer had the shape been slightly different.

The distractor is not really about this occasion. It is a claim about every occasion,
and one occasion cannot tell them apart. So a Scenario carries the facts over two
occasions and applies the rules to both, while the given facts apply only to the first.
A general rule is then `always(...)`, which fails as soon as the second occasion can
break it — which is exactly what makes it a wrong answer. `later(...)` reaches the
second occasion directly, for options of the form "tomorrow the shop will be open".

Two occasions is enough for every distractor shape used here. Nothing in the design
stops a caller asking for more.
"""
import itertools

#: Marks the option that says nothing follows. Correct exactly when no other option is
#: entailed — checked, not asserted, so it works as a distractor too.
NOTHING = object()


# ---------------------------------------------------------------- set logic

def set_entails(cats, premises, conclusion, n=4):
    """Does `conclusion` hold in every world where `premises` hold?"""
    subsets = [frozenset(s) for r in range(1, n + 1)
               for s in itertools.combinations(range(n), r)]
    models = [dict(zip(cats, a)) for a in itertools.product(subsets, repeat=len(cats))
              if all(p(dict(zip(cats, a))) for p in premises)]
    if not models:
        raise AssertionError(f"premises over {cats} describe no possible world "
                             f"— the stem contradicts itself")
    return all(conclusion(m) for m in models)


def _decide(good, nothing, what):
    if len(nothing) > 1:
        raise AssertionError(f"more than one 'nothing follows' option: {nothing}")
    if not good:
        if nothing:
            return nothing[0]
        raise AssertionError(f"no option follows from the {what}, and none says so")
    if len(good) != 1:
        raise AssertionError(f"{len(good)} options follow from the {what}, not 1: {good}")
    return good[0]


def syllogism(cats, premises, options, n=4):
    """The one option entailed by the premises, raising unless exactly one is."""
    good = [t for t, c in options
            if c is not None and c is not NOTHING and set_entails(cats, premises, c, n)]
    return _decide(good, [t for t, c in options if c is NOTHING], "premises")


def ALL(a, b):
    return lambda m: m[a] <= m[b]


def NO(a, b):
    return lambda m: not (m[a] & m[b])


def SOME(a, b):
    return lambda m: bool(m[a] & m[b])


def SOME_NOT(a, b):
    return lambda m: bool(m[a] - m[b])


# ---------------------------------------------------------------- if-then reasoning

# Rule builders take an occasion index and return a predicate over one world.
def IFo(a, b):
    return lambda i: lambda m: (not m[f"{a}@{i}"]) or m[f"{b}@{i}"]


def ISo(a):
    return lambda i: lambda m: m[f"{a}@{i}"]


def NOTo(a):
    return lambda i: lambda m: not m[f"{a}@{i}"]


def ORo(*names):
    return lambda i: lambda m: any(m[f"{n}@{i}"] for n in names)


def BOTHo(*names):
    return lambda i: lambda m: all(m[f"{n}@{i}"] for n in names)


def NEITHERo(*names):
    return lambda i: lambda m: not any(m[f"{n}@{i}"] for n in names)


def EXACTLY_ONEo(a, b):
    """True when a and b differ — "open every day except Sunday" and the like."""
    return lambda i: lambda m: m[f"{a}@{i}"] != m[f"{b}@{i}"]


class Scenario:
    """Facts over several occasions, with rules that hold on all of them.

    `rules` apply to every occasion; `given` applies only to the first, which is the
    occasion the question is about. See the module docstring for why one occasion is
    not enough.
    """

    def __init__(self, facts, rules=(), given=(), occasions=2):
        self.k = occasions
        self.names = [f"{f}@{i}" for i in range(occasions) for f in facts]
        premises = [r(i) for r in rules for i in range(occasions)] + [g(0) for g in given]
        self.models = [dict(zip(self.names, a))
                       for a in itertools.product([True, False], repeat=len(self.names))
                       if all(p(dict(zip(self.names, a))) for p in premises)]
        if not self.models:
            raise AssertionError(f"premises over {facts} are contradictory — no case fits")

    def here(self, rule):
        """The claim, about the occasion the question asks about."""
        return rule(0)

    def later(self, rule):
        """The claim, about a different occasion the question said nothing about."""
        return rule(1)

    def always(self, rule):
        """The claim as a general rule, holding on every occasion."""
        return lambda m: all(rule(i)(m) for i in range(self.k))

    def entails(self, conclusion):
        return all(conclusion(m) for m in self.models)

    def pick(self, options):
        """The one option that follows, raising unless exactly one does.

        The message names the offenders: when two options both follow the fix is nearly
        always to weaken one of them, not to change the key.
        """
        good = [t for t, c in options
                if c is not None and c is not NOTHING and self.entails(c)]
        return _decide(good, [t for t, c in options if c is NOTHING], "rules")
