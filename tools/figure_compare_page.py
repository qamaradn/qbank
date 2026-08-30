#!/usr/bin/env python3
"""One HTML page showing each repaired figure BEFORE and AFTER, side by side.

A reviewer who has already spent a sitting flagging 181 figures should not have to
re-review them from scratch to see whether the flags were acted on. This puts the
picture they objected to next to the picture that replaced it, with their own note
above the pair, so a glance answers "is this what I asked for?".

The BEFORE comes out of a database backup rather than a scratch file, so the page can
be regenerated at any time from two things that are both kept: the backup taken before
the repair round and the live database.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.figure_compare_page \\
        --before run_data/db/qbank.db.bak-vicmq-20260830-202732 \\
        --review run_data/output/figure-review-vic-mq-2026-08-30.json \\
        -o review/ui/figures-compare.html
"""
from __future__ import annotations

import argparse
import html
import json
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DB = ROOT / "run_data/db/qbank.db"

PAGE = """<!doctype html>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Figure repairs &mdash; before and after</title>
<style>
 :root{--ink:#0D1117;--line:#d8dee6;--old:#c0392b;--new:#1e7a3c}
 *{box-sizing:border-box}
 body{margin:0;font:15px/1.5 system-ui,sans-serif;background:#eef1f5;color:var(--ink)}
 header{position:sticky;top:0;background:#fff;border-bottom:1px solid var(--line);
        padding:12px 18px;z-index:5}
 h1{margin:0;font-size:17px}
 .sub{color:#5a6572;font-size:13px;margin-top:3px}
 .bar{margin-top:8px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
 input,select{font:inherit;padding:5px 8px;border:1px solid var(--line);
              border-radius:6px}
 main{padding:18px;display:flex;flex-direction:column;gap:18px}
 .item{background:#fff;border:1px solid var(--line);border-radius:10px;
       overflow:hidden}
 .hd{padding:9px 14px;border-bottom:1px solid var(--line);background:#fafbfc;
     font-size:13px;color:#5a6572}
 .hd b{color:var(--ink)}
 .note{padding:9px 14px;background:#fff8e8;border-bottom:1px solid var(--line);
       font-size:14px}
 .note::before{content:"you wrote: ";color:#8a6d1c;font-weight:600}
 .stem{padding:9px 14px;font-size:13.5px;color:#333;border-bottom:1px solid var(--line)}
 .pair{display:grid;grid-template-columns:1fr 1fr;gap:0}
 .cell{padding:14px;text-align:center}
 .cell+.cell{border-left:1px solid var(--line)}
 .tag{font-size:11px;letter-spacing:.06em;text-transform:uppercase;font-weight:700;
      margin-bottom:8px}
 .cell.b .tag{color:var(--old)} .cell.a .tag{color:var(--new)}
 .cell svg{max-width:100%;height:auto}
 @media (max-width:760px){.pair{grid-template-columns:1fr}
   .cell+.cell{border-left:0;border-top:1px solid var(--line)}}
</style>
<header>
  <h1>Figure repairs &mdash; before and after</h1>
  <div class="sub">__N__ figures you flagged, with what replaced them. Left is what you
    saw; right is what is in the bank now.</div>
  <div class="bar">
    <input id="find" placeholder="filter by form, book or words in the question"
           style="min-width:280px">
    <span id="count" class="sub"></span>
  </div>
</header>
<main id="grid"></main>
<script>
const DATA = __DATA__;
const grid = document.getElementById("grid");
function draw(){
  const q = document.getElementById("find").value.trim().toLowerCase();
  grid.innerHTML = ""; let n = 0;
  for (const d of DATA){
    if (q && !d.hay.includes(q)) continue;
    const el = document.createElement("div");
    el.className = "item";
    el.innerHTML =
      '<div class="hd"><b>' + d.n + '</b> &middot; ' + d.book +
      (d.form ? ' &middot; ' + d.form : '') + ' &middot; ' + d.id + '</div>' +
      (d.note ? '<div class="note">' + d.note + '</div>' : '') +
      '<div class="stem">' + d.stem + '</div>' +
      '<div class="pair"><div class="cell b"><div class="tag">before</div>' +
      d.before + '</div><div class="cell a"><div class="tag">after</div>' +
      d.after + '</div></div>';
    grid.appendChild(el); n++;
  }
  document.getElementById("count").textContent = n + " shown";
}
document.getElementById("find").oninput = draw;
draw();
</script>
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--before", required=True, type=pathlib.Path,
                    help="database backup taken before the repairs")
    ap.add_argument("--review", type=pathlib.Path,
                    help="the reviewer's JSON, so their note sits above each pair")
    ap.add_argument("--ids", help="comma-separated id prefixes; default every figure "
                                  "that differs between the two databases")
    ap.add_argument("-o", "--out", type=pathlib.Path,
                    default=ROOT / "review/ui/figures-compare.html")
    a = ap.parse_args()

    now = sqlite3.connect(DB)
    now.row_factory = sqlite3.Row
    old = sqlite3.connect(a.before)
    old.row_factory = sqlite3.Row
    was = {r["id"]: r["figure_svg"] for r in
           old.execute("SELECT id, figure_svg FROM questions")}

    notes, order = {}, {}
    if a.review and a.review.exists():
        for it in json.loads(a.review.read_text()).get("items", []):
            notes[it["id"]] = it.get("note") or ""
            order[it["id"]] = it.get("n", 0)

    rows = [dict(r) for r in now.execute(
        "SELECT * FROM questions WHERE figure_svg IS NOT NULL AND figure_svg != ''")]
    if a.ids:
        want = tuple(i.strip() for i in a.ids.split(","))
        rows = [r for r in rows if r["id"].startswith(want)]
    else:
        rows = [r for r in rows
                if r["id"] in was and was[r["id"]] != r["figure_svg"]]
    rows.sort(key=lambda r: (order.get(r["id"], 10 ** 6), r["form_id"] or ""))

    def esc(v):
        return html.escape(" ".join(str(v or "").split()))

    data = []
    for i, r in enumerate(rows):
        stem = " ".join((r["stem"] or "").split())
        data.append({
            "n": i + 1, "id": r["id"][:8], "book": r["source_book"] or "",
            "form": r["form_id"] or "", "stem": esc(stem[:300]),
            "note": esc(notes.get(r["id"], "")),
            "hay": " ".join([r["source_book"] or "", r["form_id"] or "",
                             stem]).lower(),
            # verbatim, both of them: the browser is the renderer whose opinion counts
            "before": was[r["id"]], "after": r["figure_svg"]})

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(
        PAGE.replace("__N__", str(len(data)))
            .replace("__DATA__", json.dumps(data, ensure_ascii=False)),
        encoding="utf-8")
    kb = a.out.stat().st_size / 1024
    print(f"{len(data)} before/after pairs -> {a.out}  ({kb:.0f} KB)")
    flagged = sum(1 for d in data if d["note"])
    print(f"{flagged} of them carry the reviewer's own note")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
