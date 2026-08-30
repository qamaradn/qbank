#!/usr/bin/env python3
"""Turn LaTeX left in plain-text fields into the characters it was meant to draw.

"Why are the answer options all having like strange symbol things on them?" and, two
questions later, "Again weird $ signs on the answers." A student is offered
`$42 \\text{ cm}²$` and `\\(\\dfrac{12}{13}\\)` and has to read past the markup to the
number. Nothing in this pipeline renders maths -- the review UI prints the stored
string and so does Selectly -- so whatever the generating model typed is what a
student sees.

WHY THIS ONE SWEEPS. It rewrites text, which rule 11d normally holds to the flagged
question. The exception the rule allows is a repair that cannot destroy a correct
state, and a plain-text field holding `\\dfrac{12}{13}` has no correct state to
destroy: the conversion is a transcription with no judgement in it. What it does NOT
do is guess -- anything left carrying a backslash command after conversion is refused
and listed for a human rather than half-translated.

Bank-wide this is 26 questions, all pending. The reviewer found three of them.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_latex_markup
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_latex_markup --apply
"""
import argparse
import json
import pathlib
import re
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import question_checks as qc            # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
RECORD = ROOT / "run_data/output/latex_markup_repairs.json"
FIELDS = ("stem", "option_a", "option_b", "option_c", "option_d", "explanation")

SYMBOLS = {
    r"\times": "×", r"\div": "÷", r"\cdot": "·", r"\neq": "≠",
    r"\leq": "≤", r"\geq": "≥", r"\le": "≤", r"\ge": "≥", r"\circ": "°",
    r"\angle": "∠", r"\pm": "±", r"\approx": "≈", r"\ldots": "…", r"\%": "%",
    r"\left": "", r"\right": "", r"\displaystyle": "", r"\mathrm": "", r"\,": " ",
    # Greek, which the rest of the bank writes as the letter itself
    r"\pi": "π", r"\theta": "θ", r"\alpha": "α", r"\beta": "β", r"\gamma": "γ",
    r"\delta": "δ", r"\phi": "φ", r"\lambda": "λ", r"\mu": "μ", r"\omega": "ω",
    # Function names are words, not commands, and read perfectly well as words
    r"\sin": "sin", r"\cos": "cos", r"\tan": "tan", r"\log": "log",
    r"\ln": "ln", r"\max": "max", r"\min": "min",
}
SUP = {"0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵",
       "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹", "n": "ⁿ"}


def _braced(text, cmd):
    """Yield (whole, arg) for each `\\cmd{...}`, matching braces properly."""
    out = []
    i = 0
    tag = "\\" + cmd + "{"
    while (j := text.find(tag, i)) != -1:
        depth, k = 1, j + len(tag)
        while k < len(text) and depth:
            depth += (text[k] == "{") - (text[k] == "}")
            k += 1
        if depth:
            break
        out.append((text[j:k], text[j + len(tag):k - 1]))
        i = k
    return out


def convert(text):
    if not text:
        return text
    t = text
    # Symbols first, so a fraction over pi sees "π" -- one token, no brackets -- rather
    # than "\pi" and prints π/4 instead of (π)/4.
    for k, v in SYMBOLS.items():
        t = re.sub(re.escape(k) + r"(?![a-zA-Z])", v, t)
    # \frac{a}{b} -> a/b, bracketing either half when it is more than one token so
    # "x/x−y" cannot be read as (x/x)−y.
    for _ in range(4):
        changed = False
        for cmd in ("dfrac", "frac", "tfrac"):
            for whole, num in _braced(t, cmd):
                rest = t[t.index(whole) + len(whole):]
                m = re.match(r"\s*\{", rest)
                if not m:
                    continue
                depth, k = 1, m.end()
                while k < len(rest) and depth:
                    depth += (rest[k] == "{") - (rest[k] == "}")
                    k += 1
                den = rest[m.end():k - 1]

                def wrap(x):
                    x = x.strip()
                    # A single token needs no brackets; anything with an operator in
                    # it does, so "x/x−y" cannot be read as (x/x)−y. Greek letters and
                    # a root are single tokens: "(π)/4" is uglier than "π/4" and no
                    # clearer.
                    return (x if re.fullmatch(r"[\w.°²³⁴⁵⁶⁷⁸⁹⁰πθαβγδφλμω√]+", x)
                            else f"({x})")
                whole_frac = whole + rest[:k]
                built = f"{wrap(num)}/{wrap(den)}"
                # \frac{1}{2}p is (1/2)p. Written as "1/2p" it reads as 1/(2p), which
                # is a different number -- the one place this conversion could change
                # an answer, so it is the one place it brackets defensively.
                tail = t[t.index(whole_frac) + len(whole_frac):]
                if re.match(r"[A-Za-z(]", tail.strip()[:1] or " "):
                    built = f"({built})"
                t = t.replace(whole_frac, built, 1)
                changed = True
        if not changed:
            break
    for whole, arg in _braced(t, "sqrt"):
        a = arg.strip()
        bare = re.fullmatch(r"[\w.°²³⁴⁵⁶⁷⁸⁹⁰]+", a)
        t = t.replace(whole, f"√{a}" if bare else f"√({a})", 1)
    for cmd in ("text", "mathrm", "textrm", "overline", "mathbf"):
        for whole, arg in _braced(t, cmd):
            t = t.replace(whole, arg, 1)
    # ^2 and ^{2} -> superscript, which is what the rest of the bank already uses
    # Multi-character exponents too: x^{12} is 81x¹², not 81x^{12}. Only where every
    # character has a superscript form, so x^{n+1} stays legible as x^(n+1).
    def _sup(txt):
        if txt and all(c in SUP for c in txt):
            return "".join(SUP[c] for c in txt)
        return None
    t = re.sub(r"\^\{([^{}]+)\}",
               lambda m: _sup(m.group(1)) or "^(" + m.group(1) + ")", t)
    t = re.sub(r"\^(\w)", lambda m: SUP.get(m.group(1), "^" + m.group(1)), t)
    # A subscript names a base or an index -- log_3, T_1 -- and reads as itself.
    t = re.sub(r"_\{([^{}]+)\}", r"_\1", t)
    t = t.replace("\\(", "").replace("\\)", "").replace("\\[", "").replace("\\]", "")
    # $...$ delimiters go once nothing inside them needs rendering
    t = re.sub(r"\$([^$\n]*)\$", r"\1", t)
    t = re.sub(r"[ \t]{2,}", " ", t)
    return t.strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute(
        "SELECT * FROM questions WHERE review_status != 'rejected'")]
    done, refused = [], []
    for r in rows:
        if not qc.latex_markup_in_text(r):
            continue
        new = {f: convert(r[f]) for f in FIELDS if r[f]}
        after = dict(r)
        after.update(new)
        # Nothing half-translated: a backslash command surviving conversion means a
        # construct this does not know, and a guess there is worse than a report.
        left = [f for f, v in new.items() if re.search(r"\\[a-zA-Z]+|[{}]|\$", v)]
        if left or qc.latex_markup_in_text(after):
            refused.append({"id": r["id"], "fields": left,
                            "sample": {f: new[f] for f in left}})
            continue
        changed = {f: [r[f], v] for f, v in new.items() if v != r[f]}
        if not changed:
            continue
        done.append({"id": r["id"], "book": r["source_book"], "form": r["form_id"],
                     "changed": changed})
        if args.apply:
            con.execute(
                "UPDATE questions SET " + ", ".join(f"{f} = ?" for f in new)
                + ", edited = 1 WHERE id = ?",
                [*new.values(), r["id"]])
    if args.apply:
        con.commit()
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps({"applied": args.apply, "converted": done,
                                  "refused": refused}, indent=1, ensure_ascii=False))
    print(f"{len(done)} converted, {len(refused)} refused"
          f"{'' if args.apply else '  (dry run — pass --apply)'}")
    for r in refused:
        print("   refused", r["id"][:8], r["fields"], r["sample"])
    print(f"record -> {RECORD}")


if __name__ == "__main__":
    main()
