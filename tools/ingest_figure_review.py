#!/usr/bin/env python3
"""Read a reviewer's figure-review file back in and turn it into a work list.

The page built by `tools.figure_review_page` is self-contained: no server, no
network, no fonts. A reviewer opens it by double-clicking, marks each figure,
presses Download my comments and emails back a small JSON. This reads that file.

WHAT IT CHECKS, because a file that arrives by email has been round-tripped
through someone else's machine:

  * every id is a real question, and still says what the reviewer was looking at.
    A figure repaired between sending the page and getting it back has moved on,
    and their note may no longer describe it -- that is reported, not silently
    applied.
  * the flags are separated from the "looks fine" marks. Both matter. The fines
    are the only record of which figures have had a human's eyes on them at all,
    and without them the next pass cannot tell "reviewed and sound" from "nobody
    has looked".
  * anything on the page they did not reach is counted, so the size of what is
    left is a number rather than a guess.

It writes `run_data/output/figure_review/<reviewer>_<date>.json` as the durable
record, and prints the flagged ones ordered by book so they can be worked through.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.ingest_figure_review \
        ~/Downloads/figure-review-vic-mq-2026-08-30.json
"""
from __future__ import annotations

import argparse
import itertools
import hashlib
import json
import pathlib
import re
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DB = ROOT / "run_data/db/qbank.db"
OUT = ROOT / "run_data/output/figure_review"


def stem_of(q):
    return " ".join((q["stem"] or "").split())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", type=pathlib.Path)
    ap.add_argument("--quiet", action="store_true", help="record only, print a summary")
    a = ap.parse_args()

    try:
        doc = json.loads(a.file.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"could not read {a.file}: {exc}")
    if doc.get("kind") != "qbank-figure-review":
        raise SystemExit(f"{a.file} is not a figure-review file "
                         f"(kind={doc.get('kind')!r})")

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    items = doc.get("items") or []
    flagged, fine, unknown, moved = [], [], [], []

    for it in items:
        row = con.execute("SELECT * FROM questions WHERE id=?", (it["id"],)).fetchone()
        if row is None:
            unknown.append(it)
            continue
        q = dict(row)
        # The stem the reviewer saw, truncated the same way the page truncates it.
        if it.get("stem") and not stem_of(q).startswith(it["stem"][:80]):
            moved.append((it, stem_of(q)[:100]))
        rec = {**it, "current_status": q["review_status"],
               "current_form": q["form_id"], "source_book": q["source_book"]}
        (flagged if it.get("verdict") == "problem" else fine).append(rec)

    reviewer = re.sub(r"[^a-z0-9]+", "-",
                      (doc.get("reviewer") or "anon").lower()).strip("-")
    date = (doc.get("reviewed_at") or "")[:10] or "undated"
    OUT.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(a.file.read_bytes()).hexdigest()[:12]
    out = OUT / f"{reviewer}_{date}_{digest}.json"
    out.write_text(json.dumps(
        {"source_file": a.file.name, "sha256_12": digest,
         "reviewer": doc.get("reviewer"), "reviewed_at": doc.get("reviewed_at"),
         "scope": doc.get("scope"), "total_on_page": doc.get("total_on_page"),
         "flagged": flagged, "fine": fine,
         "unknown_ids": unknown, "stem_changed_since": [m[0] for m in moved]},
        indent=1, ensure_ascii=False), encoding="utf-8")

    total = doc.get("total_on_page") or 0
    print(f"from {doc.get('reviewer') or 'an unnamed reviewer'}, "
          f"{doc.get('reviewed_at', '')[:10]}, scope {doc.get('scope')}")
    print(f"  page held        {total}")
    print(f"  they looked at   {len(items)}")
    print(f"  flagged          {len(flagged)}")
    print(f"  marked fine      {len(fine)}")
    print(f"  not reached      {max(total - len(items), 0)}")
    if unknown:
        print(f"  !! {len(unknown)} id(s) are not in the bank at all")
    if moved:
        print(f"  !! {len(moved)} question(s) CHANGED since the page was built — "
              f"the note may not describe what is there now:")
        for it, now in moved[:6]:
            print(f"       #{it['n']} {it['id'][:8]}  now: {now}")

    if flagged and not a.quiet:
        print("\nflagged, by book:\n")
        for book, group in itertools.groupby(
                sorted(flagged, key=lambda x: (x["source_book"] or "", x["n"])),
                key=lambda x: x["source_book"] or ""):
            g = list(group)
            print(f"  {book}  ({len(g)})")
            for it in g:
                note = it.get("note") or "(no note)"
                print(f"     #{it['n']:<4} {it['id'][:8]}  {str(it['current_form']):<18} {note}")
    print(f"\nrecorded -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
