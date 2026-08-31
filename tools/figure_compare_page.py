#!/usr/bin/env python3
"""One HTML page showing each repaired figure BEFORE and AFTER, side by side.

A reviewer who has already spent a sitting flagging 181 figures should not have to
re-review them from scratch to see whether the flags were acted on. This puts the
picture they objected to next to the picture that replaced it, with their own note
above the pair, so a glance answers "is this what I asked for?".

The BEFORE comes out of a database backup rather than a scratch file, so the page can
be regenerated at any time from two things that are both kept: the backup taken before
the repair round and the live database.

The page marks like the review page does and downloads the SAME JSON, so
`tools.ingest_figure_review` reads it back with no changes: a figure that is still
wrong after a repair is just another flag, and it belongs in the same work list.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.figure_compare_page \\
        --before run_data/db/qbank.db.bak-vicmq-20260830-202732 \\
        --review run_data/output/figure-review-vic-mq-2026-08-30.json \\
        --scope vic-mq-recheck
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
 .stem{padding:9px 14px;font-size:13.5px;color:#333}
 .opts{padding:0 14px 10px;font-size:13px;color:#444;
       border-bottom:1px solid var(--line)}
 .opts span{display:inline-block;margin-right:14px}
 .opts .k{color:var(--new);font-weight:700}
 .pair{display:grid;grid-template-columns:1fr 1fr;gap:0}
 .cell{padding:14px;text-align:center}
 .cell+.cell{border-left:1px solid var(--line)}
 .tag{font-size:11px;letter-spacing:.06em;text-transform:uppercase;font-weight:700;
      margin-bottom:8px}
 .cell.b .tag{color:var(--old)} .cell.a .tag{color:var(--new)}
 .cell svg{max-width:100%;height:auto}
 @media (max-width:760px){.pair{grid-template-columns:1fr}
   .cell+.cell{border-left:0;border-top:1px solid var(--line)}}
 .item.flagged{border-color:var(--old);box-shadow:0 0 0 2px rgba(192,57,43,.16)}
 .item.done{opacity:.55}
 .acts{padding:10px 14px;border-top:1px solid var(--line);display:flex;gap:8px;
       align-items:center;flex-wrap:wrap;background:#fafbfc}
 button{font:inherit;padding:6px 12px;border:1px solid var(--line);background:#fff;
        border-radius:7px;cursor:pointer}
 button:hover{background:#f1f4f8}
 .say{flex:1;min-width:220px}
 .item.flagged .say{background:#fff8f7}
 dialog{border:1px solid var(--line);border-radius:10px;padding:16px;max-width:640px}
 textarea{width:100%;height:220px;font:12px/1.45 ui-monospace,monospace}
</style>
<header>
  <h1>Figure repairs &mdash; before and after</h1>
  <div class="sub">__N__ figures, with what replaced them. Left is what you saw last
    time; right is what is in the bank now. Mark anything still wrong, type what is
    wrong with it, then press <b>Download my comments</b> and send the file back.
    The question, its four options and the marked answer are under each pair.</div>
  <div class="bar">
    <input id="find" placeholder="filter by form, book or words in the question"
           style="min-width:260px">
    <select id="filter">
      <option value="all">show all</option>
      <option value="todo">not yet marked</option>
      <option value="flagged">still a problem</option>
    </select>
    <input id="who" placeholder="your name" style="width:130px">
    <button id="download"><b>Download my comments</b></button>
    <button id="copy">Copy the list</button>
    <button id="reset">Clear my marks</button>
    <span id="count" class="sub"></span>
  </div>
</header>
<main id="grid"></main>
<dialog id="out"><h3 style="margin:0 0 8px">Still a problem</h3>
  <textarea id="outtext" readonly></textarea>
  <p style="margin:10px 0 0;text-align:right">
    <button onclick="document.getElementById('out').close()">Close</button></p>
</dialog>
<script>
const DATA = __DATA__;
const SCOPE = "__SCOPE__";
const KEY = "qbank-compare:" + SCOPE;
const grid = document.getElementById("grid");

// Marks survive a reload, so the pass can be done in sittings. Same mechanism the
// first review page used, and the file it downloads is the SAME shape, so
// tools/ingest_figure_review.py reads it with no changes.
let CAN_SAVE = true, state = {};
try { state = JSON.parse(localStorage.getItem(KEY) || "{}"); }
catch (e) { CAN_SAVE = false; }
function save(){ try { localStorage.setItem(KEY, JSON.stringify(state)); }
                 catch (e) { CAN_SAVE = false; } }

function card(d){
  const st = state[d.n] || {};
  const el = document.createElement("div");
  el.className = "item" + (st.flag ? " flagged" : "") + (st.ok ? " done" : "");
  el.innerHTML =
    '<div class="hd"><b>' + d.n + '</b> &middot; ' + d.book +
    (d.form ? ' &middot; ' + d.form : '') + ' &middot; ' + d.id + '</div>' +
    (d.note ? '<div class="note">' + d.note + '</div>' : '') +
    '<div class="stem">' + d.stem + '</div>' +
    '<div class="pair"><div class="cell b"><div class="tag">before</div>' +
    d.before + '</div><div class="cell a"><div class="tag">after</div>' +
    d.after + '</div></div>' +
    '<div class="acts">' +
      '<input class="say" placeholder="what is still wrong with the new one?" value="' +
        (st.note || "").replace(/"/g,"&quot;") + '">' +
      '<button data-act="flag">' + (st.flag ? "Un-flag" : "Still a problem") +
      '</button><button data-act="ok">' + (st.ok ? "Un-mark" : "Fixed") +
      '</button></div>';
  el.querySelector('[data-act=flag]').onclick = () => {
    state[d.n] = Object.assign({}, state[d.n], {flag: !st.flag, ok:false});
    save(); draw();
  };
  el.querySelector('[data-act=ok]').onclick = () => {
    state[d.n] = Object.assign({}, state[d.n], {ok: !st.ok, flag:false});
    save(); draw();
  };
  el.querySelector('.say').oninput = e => {
    state[d.n] = Object.assign({}, state[d.n], {note: e.target.value}); save();
  };
  return el;
}

function draw(){
  const q = document.getElementById("find").value.trim().toLowerCase();
  const mode = document.getElementById("filter").value;
  grid.innerHTML = ""; let n = 0;
  for (const d of DATA){
    const st = state[d.n] || {};
    if (mode === "todo" && (st.flag || st.ok)) continue;
    if (mode === "flagged" && !st.flag) continue;
    if (q && !d.hay.includes(q)) continue;
    grid.appendChild(card(d)); n++;
  }
  const f = Object.values(state).filter(s => s.flag).length;
  const k = Object.values(state).filter(s => s.ok).length;
  document.getElementById("count").textContent =
    n + " shown \u2022 " + f + " still a problem \u2022 " + k + " fixed \u2022 " +
    (DATA.length - f - k) + " left";
}
document.getElementById("find").oninput = draw;
document.getElementById("filter").onchange = draw;
document.getElementById("reset").onclick = () => {
  if (confirm("Clear every mark on this page?")) { state = {}; save(); draw(); }
};
try { document.getElementById("who").value = localStorage.getItem(KEY + ":who") || ""; }
catch (e) {}
document.getElementById("who").oninput = e => {
  try { localStorage.setItem(KEY + ":who", e.target.value); } catch (err) {}
};
if (!CAN_SAVE) {
  const w = document.createElement("p");
  w.style.cssText = "margin:0;padding:10px 16px;background:#ffe8e6;color:#8a1c12;" +
    "border-bottom:1px solid var(--line);font-size:13px";
  w.innerHTML = "<b>This browser will not let the page remember your marks.</b> " +
    "Press <b>Download my comments</b> before you close the tab.";
  document.querySelector("header").after(w);
}

document.getElementById("download").onclick = () => {
  // Everything LOOKED AT, not only the flags -- the "fixed" marks are the only
  // record of which repairs have had a human's eyes on them.
  const seen = DATA.filter(d => {
    const s = state[d.n] || {}; return s.flag || s.ok || (s.note || "").trim();
  }).map(d => {
    const s = state[d.n];
    return {n: d.n, id: d.full, book: d.book, form: d.form,
            verdict: s.flag ? "problem" : (s.ok ? "fine" : "note"),
            note: (s.note || "").trim(), stem: d.stem.slice(0, 120)};
  });
  const doc = {kind: "qbank-figure-review", version: 1, scope: SCOPE,
               reviewer: document.getElementById("who").value.trim() || null,
               reviewed_at: new Date().toISOString(),
               total_on_page: DATA.length, reviewed: seen.length, items: seen};
  const blob = new Blob([JSON.stringify(doc, null, 1)], {type: "application/json"});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "figure-review-" + SCOPE + "-" +
               new Date().toISOString().slice(0, 10) + ".json";
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 2000);
};

document.getElementById("copy").onclick = () => {
  const lines = DATA.filter(d => (state[d.n]||{}).flag).map(d => {
    const note = (state[d.n].note || "").trim();
    return d.n + "  " + d.id + "  " + d.book + (d.form ? " " + d.form : "") +
           (note ? "  -- " + note : "");
  });
  document.getElementById("outtext").value =
    lines.length ? lines.join("\\n") : "nothing marked as still a problem";
  document.getElementById("out").showModal();
  document.getElementById("outtext").select();
};
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
    ap.add_argument("--scope", default="vic-mq-recheck",
                    help="names the download, and keeps this page's marks separate "
                         "from any other page open at the same time")
    ap.add_argument("-o", "--out", type=pathlib.Path,
                    help="default: review/ui/compare-<scope>.html")
    a = ap.parse_args()

    # ONE FOLDER, ONE NAME PER PAGE. Both builders used to default to a single
    # `figures.html`, so building the NSW page silently replaced the VIC one and the
    # reviewer's link pointed at whichever was made last. Every page this project
    # produces now lands in review/ui/ under a name carrying its scope.
    out = a.out or (ROOT / "review/ui" / f"compare-{a.scope}.html")

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
            "n": i + 1, "id": r["id"][:8], "full": r["id"],
            "book": r["source_book"] or "",
            "form": r["form_id"] or "", "stem": esc(stem),
            # The four options and the key, as the first review page shows them: "does
            # this picture answer this question" cannot be judged from the stem alone.
            # A figure can agree with every word and still contradict the marked answer.
            "a": esc(r["option_a"]), "b": esc(r["option_b"]),
            "c": esc(r["option_c"]), "d": esc(r["option_d"]),
            "key": (r["correct_answer"] or "").strip().lower(),
            "note": esc(notes.get(r["id"], "")),
            "hay": " ".join([r["source_book"] or "", r["form_id"] or "",
                             stem]).lower(),
            # verbatim, both of them: the browser is the renderer whose opinion counts
            "before": was[r["id"]], "after": r["figure_svg"]})

    page = (PAGE.replace("__N__", str(len(data)))
                .replace("__SCOPE__", a.scope)
                .replace("__DATA__", json.dumps(data, ensure_ascii=False)))
    # A backslash in this file's PAGE template is a PYTHON escape before it is a
    # JavaScript one, so `join("\n")` written once becomes a real newline inside a
    # JS string literal and the whole script stops parsing. It cost the Copy button
    # silently. Cheap to check: no quote may be the last thing on a line inside the
    # script.
    script = page[page.index("<script>"):page.index("</script>")]
    bad = [ln for ln in script.splitlines() if ln.rstrip().endswith(('"', "'"))
           and not ln.rstrip().endswith(('";', "';", '",', "',", '")', "')"))]
    if bad:
        raise SystemExit(f"page script has an unterminated string: {bad[0][-60:]!r}")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    kb = out.stat().st_size / 1024
    print(f"{len(data)} before/after pairs -> {out}  ({kb:.0f} KB)")
    flagged = sum(1 for d in data if d["note"])
    print(f"{flagged} of them carry the reviewer's own note")
    print("\nSend that file. When it comes back:")
    print("   env -u PYTHONPATH .venv/bin/python3.11 -m tools.ingest_figure_review "
          "<the file>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
