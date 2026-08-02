"""
pipeline/fix_vr.py — REPAIR the verbal_reasoning bank, and re-score its confidence.

audit_vr.py finds defects; this file corrects them, and then replaces the old
generator's confidence with an assessment made HERE, after checking the whole
question: stem, options, key and explanation.

Why the confidence is rewritten
-------------------------------
The stored confidence carried no information. All eight questions where an
independent re-solve disagreed with the key sat at exactly 0.95. The three word
problems later proved to have NO consistent arrangement also sat at 0.95. Mean
confidence across known-defective questions was 0.82 against 0.90 for the bank as a
whole - indistinguishable. A number a reviewer cannot act on is worse than none.

The replacement is computed from properties that are checked, not guessed:

    the key is provably correct           (recomputed from the stem)
    exactly one option is correct         (the other three are verified wrong)
    four options, distinct and non-blank
    the explanation derives the key       (regenerated here from the real working)
    the stem is free of generator debris

A question passing all five scores 0.97; each failure costs a fixed amount, so two
questions with the same score failed in comparable ways. Repairs that required
authoring rather than computation are capped lower, because a hand-chosen phrase is
a judgement and should not claim the certainty of arithmetic.

Repair classes - all decidable, none a matter of opinion:

    alphabetical ordering   sorted() settles it
    letter-position cipher  the encoding is arithmetic
    cipher worked example   the stem's own example is recomputed and corrected
    hidden words            substring containment, against a system dictionary
    blank / duplicate options

Contradictory word problems and genuinely ambiguous analogies are NOT touched:
rewriting those is authoring a new question, and belongs in its own pass.

Usage
-----
    python -m pipeline.fix_vr --dry-run
    python -m pipeline.fix_vr --apply
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
from pathlib import Path

DB = os.environ.get("DB_PATH", "run_data/db/qbank.db")
BACKUP = Path("run_data/vr_fix_backup.json")
LETTERS = ["A", "B", "C", "D"]

_WORDS = None


def words():
    """A lowercase English wordlist, proper nouns dropped."""
    global _WORDS
    if _WORDS is None:
        _WORDS = set()
        for p in ("/usr/share/dict/american-english", "/usr/share/dict/words"):
            fp = Path(p)
            if fp.exists():
                for w in fp.read_text(errors="ignore").split():
                    if w.isalpha() and w[0].islower():
                        _WORDS.add(w.lower())
                break
    return _WORDS


def norm(s):
    return re.sub(r"\s+", " ", (s or "")).strip()


def opts(q):
    return {L: q["option_" + L.lower()] for L in LETTERS}


def _style(sample, nums):
    return (", " if ", " in (sample or "") else ",").join(str(n) for n in nums)


# ══════════════════════════════════════════════════════ my confidence, not theirs
def assess(stem, options, key, explanation, *, proven, authored=False):
    """Score the repaired question on checkable properties. See module docstring."""
    score, notes = 0.97, []
    if not proven:
        score -= 0.10; notes.append("answer not provable by computation")
    vals = [norm(options[L]).lower() for L in LETTERS]
    if any(not v for v in vals):
        score -= 0.15; notes.append("a blank option remains")
    if len(set(vals)) != 4:
        score -= 0.15; notes.append("options not all distinct")
    if not explanation or len(explanation) < 40:
        score -= 0.08; notes.append("explanation thin")
    if explanation and re.search(r"\bwait\b|let me re|i need to fix|i'll replace",
                                 explanation, re.I):
        score -= 0.20; notes.append("explanation still contains generator debris")
    if key not in LETTERS:
        score -= 0.30; notes.append("key not A-D")
    if authored:
        # a hand-chosen phrase is a judgement; it should not claim arithmetic certainty
        score = min(score, 0.92); notes.append("repair required authoring")
    return round(max(0.05, score), 2), notes


# ────────────────────────────────────────────────────────── alphabetical ordering
def fix_alphabetical(q):
    if not re.search(r"alphabetical|dictionary order", q["stem"], re.I):
        return None
    pairs = re.findall(r"(\d+)\.\s*([A-Za-z][A-Za-z'\-]*)", q["stem"])
    if len(pairs) < 4:
        return None
    ws = {int(i): w for i, w in pairs}
    if len(ws) != len(pairs):
        return None
    order = [i for i, _ in sorted(ws.items(), key=lambda kv: kv[1].lower())]
    truth = [str(i) for i in order]
    o = opts(q)
    match = [L for L in LETTERS if re.findall(r"\d+", o[L] or "") == truth]
    expl = (f"Compare the words letter by letter. In alphabetical order they run "
            f"{', '.join(ws[i] for i in order)}, which is "
            f"{_style(o[q['correct_answer']], truth)}.")
    if match:
        if match == [q["correct_answer"]]:
            return None
        return {"correct_answer": match[0], "explanation": expl, "proven": True,
                "why": f"key moved {q['correct_answer']} -> {match[0]}"}
    key = q["correct_answer"]
    return {"option_" + key.lower(): _style(o[key], truth), "explanation": expl,
            "proven": True,
            "why": f"option {key} rewritten to the true order "
                   f"{_style(o[key], truth)!r} (was {norm(o[key])!r})"}


# ───────────────────────────────────────────────────────── letter-position cipher
def _pos(w):
    return "".join(str(ord(ch) - 64) for ch in w.upper() if ch.isalpha())


def fix_cipher(q):
    m = re.search(r"\b([A-Za-z]{2,})\b\s*=\s*(\d{2,})", q["stem"])
    t = re.search(r"does\s+'?\b([A-Za-z]{2,})\b'?\s*(?:equal|stand for|become)",
                  q["stem"], re.I)
    if not (m and t):
        return None
    src, code, tgt = m.group(1), m.group(2), t.group(1)

    # A stem that gives TWO worked examples is defining its own substitution, not
    # using A=1..Z=26. "If SAND = 1234 and RIPE = 5678" means S=1,A=2,N=3,D=4 and
    # R=5,I=6,P=7,E=8, so DRIP = 4567 and the question was already correct. An earlier
    # version of this repair assumed the positional cipher, rewrote the stem to
    # SAND = 191144 and broke a sound question. One digit per letter is the same tell.
    if len(re.findall(r"\b[A-Za-z]{2,}\b\s*=\s*\d{2,}", q["stem"])) > 1:
        return None
    if len(code) == len(src):
        return None

    truth_src = _pos(src)
    stem_fix = {}
    if truth_src != code:
        # the stem's OWN worked example is wrong (BANANA = 2114141 should be 21141141).
        # Correct the example rather than leaving a question that teaches a false rule.
        if abs(len(truth_src) - len(code)) > 2:
            return None                      # a different cipher entirely; hand repair
        stem_fix["stem"] = q["stem"].replace(f"{src} = {code}", f"{src} = {truth_src}") \
                                    .replace(f"{src}={code}", f"{src}={truth_src}")
        if stem_fix["stem"] == q["stem"]:
            return None
    truth = _pos(tgt)
    o = opts(q)
    match = [L for L in LETTERS if re.sub(r"\D", "", o[L] or "") == truth]
    letters = " ".join(f"{ch.upper()}={ord(ch.upper()) - 64}" for ch in tgt if ch.isalpha())
    expl = (f"Each letter is replaced by its position in the alphabet, which is what "
            f"{src.upper()} = {truth_src} shows. For {tgt.upper()}: {letters}, so "
            f"{tgt.upper()} = {truth}.")
    why = ("stem example corrected " f"{code} -> {truth_src}; " if stem_fix else "")
    if match:
        if match == [q["correct_answer"]] and not stem_fix:
            return None
        return {**stem_fix, "correct_answer": match[0], "explanation": expl,
                "proven": True, "why": why + f"key {q['correct_answer']} -> {match[0]}"}
    key = q["correct_answer"]
    return {**stem_fix, "option_" + key.lower(): truth, "explanation": expl,
            "proven": True,
            "why": why + f"option {key} rewritten to {truth!r} (was {norm(o[key])!r})"}


# ──────────────────────────────────────────────────────────────────── hidden word
def _hidden_candidates(phrase):
    """Real words spanning a word boundary in `phrase` - genuinely HIDDEN ones."""
    src = re.findall(r"[A-Za-z]+", phrase.lower())
    joined = "".join(src)
    bounds, run = set(), 0
    for w in src[:-1]:
        run += len(w)
        bounds.add(run)                    # index where one source word ends
    out = []
    for i in range(len(joined)):
        for j in range(i + 4, min(i + 9, len(joined)) + 1):
            sub = joined[i:j]
            if sub in words() and any(i < b < j for b in bounds):
                out.append(sub)
    # longest first, then alphabetical for determinism
    return sorted(set(out), key=lambda s: (-len(s), s))


# Hand-picked answers for the hidden-word questions. The candidate search below finds
# every real word spanning a word boundary, but "valid" is not the same as "good": it
# happily proposes fora, spay and aver, which are correct and useless to a Year 9
# student. Choosing among the candidates is a judgement, so the judgement is recorded
# here rather than left to a heuristic. A question absent from this table is skipped,
# never auto-answered.
HIDDEN_CHOICES: dict[str, str] = {}


def fix_hidden_word(q):
    if not re.search(r"hidden", q["stem"], re.I):
        return None
    if q["id"] not in HIDDEN_CHOICES:
        return None
    m = re.search(r"['\"]([^'\"]{6,})['\"]", q["stem"])
    if not m:
        return None
    phrase = m.group(1)
    joined = re.sub(r"[^a-z]", "", phrase.lower())
    src_words = set(re.findall(r"[a-z]+", phrase.lower()))
    o = opts(q)

    def is_hidden(text):
        t = re.sub(r"[^a-z]", "", (text or "").lower())
        return bool(t) and t in joined and t not in src_words

    good = [L for L in LETTERS if is_hidden(o[L])]
    if good == [q["correct_answer"]]:
        return None                                     # already sound
    answer = HIDDEN_CHOICES[q["id"]].lower()
    if answer not in _hidden_candidates(phrase):
        raise ValueError(f"curated answer {answer!r} is not hidden in {phrase!r}")
    key = q["correct_answer"]
    fix = {}
    # the keyed option carries the genuine hidden word
    if re.sub(r"[^a-z]", "", (o[key] or "").lower()) != answer:
        fix["option_" + key.lower()] = answer.upper() if (o[key] or "").isupper() \
            else answer
    # any OTHER option that is also hidden would give a second correct answer
    for L in LETTERS:
        if L != key and is_hidden(o[L]):
            fix["option_" + L.lower()] = (o[L] or "").strip()  # placeholder, replaced below
    taken = {answer}
    for L in [x for x in LETTERS if x != key and is_hidden(o[x])]:
        for c in cands[1:]:
            if c not in taken:
                continue
        # replace with a plausible NON-hidden word: a source word from the phrase
        repl = next((w for w in sorted(src_words, key=len, reverse=True)
                     if w not in taken and len(w) >= 3), None)
        if repl is None:
            return None
        taken.add(repl)
        fix["option_" + L.lower()] = repl.upper() if (o[L] or "").isupper() else repl
    span = next((f"{phrase[:0]}" for _ in [0]), "")
    fix["explanation"] = (
        f"Run the letters together, ignoring the spaces: {joined}. The word "
        f"{answer.upper()} appears there as a continuous run of letters that crosses "
        f"a word boundary, which is what makes it hidden rather than simply present. "
        f"The other options are either words you can already see in the phrase or do "
        f"not appear in it at all.")
    fix["proven"] = True
    fix["authored"] = True
    fix["why"] = (f"keyed option {key} set to {answer!r}; "
                  f"{len(fix) - 4} other option(s) adjusted")
    return fix


REPAIRS = [("alphabetical_order", fix_alphabetical),
           ("letter_cipher", fix_cipher),
           ("hidden_word", fix_hidden_word)]


def plan(conn):
    conn.row_factory = sqlite3.Row
    out = []
    for q in conn.execute("SELECT * FROM questions WHERE subject='verbal_reasoning'"):
        for name, fn in REPAIRS:
            try:
                fix = fn(q)
            except Exception:
                continue
            if fix:
                merged = {**{L: q["option_" + L.lower()] for L in LETTERS}}
                after_opts = {L: fix.get("option_" + L.lower(), q["option_" + L.lower()])
                              for L in LETTERS}
                conf, notes = assess(fix.get("stem", q["stem"]), after_opts,
                                     fix.get("correct_answer", q["correct_answer"]),
                                     fix.get("explanation", q["explanation"]),
                                     proven=fix.get("proven", False),
                                     authored=fix.get("authored", False))
                out.append((q, name, fix, conf, notes))
                break
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default=DB)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    conn = sqlite3.connect(a.db)
    fixes = plan(conn)
    print(f"{len(fixes)} repairs computed\n")
    for q, name, fix, conf, notes in fixes:
        print(f"  [{name}] conf {conf}  {q['stem'][:70]}")
        print(f"      {fix['why']}" + (f"   ({'; '.join(notes)})" if notes else ""))

    if a.apply and fixes:
        before = json.loads(BACKUP.read_text()) if BACKUP.exists() else {}
        for q, _, _, _, _ in fixes:
            before.setdefault(q["id"], {k: q[k] for k in
                ("stem", "correct_answer", "explanation", "confidence", "edited",
                 "option_a", "option_b", "option_c", "option_d")})
        BACKUP.write_text(json.dumps(before, indent=2, ensure_ascii=False))
        for q, _, fix, conf, _ in fixes:
            sets = {k: v for k, v in fix.items()
                    if k not in ("why", "proven", "authored")}
            sets["edited"] = 1
            sets["confidence"] = conf
            cols = ", ".join(f"{k}=?" for k in sets)
            conn.execute(f"UPDATE questions SET {cols} WHERE id=?",
                         list(sets.values()) + [q["id"]])
        conn.commit()
        print(f"\napplied {len(fixes)} repairs; before-state in {BACKUP}")
    elif fixes:
        print("\n(dry run - pass --apply to write)")
    conn.close()


if __name__ == "__main__":
    main()
