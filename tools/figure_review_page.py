#!/usr/bin/env python3
"""One self-contained HTML page for reviewing figures in a real browser.

WHY THIS REPLACES THE PNG CONTACT SHEET FOR THIS PASS. The sheet is rasterised by
cairosvg, which is NOT the renderer a student or a reviewer uses. Two of the 349
figures cairosvg refused outright would draw perfectly well in a browser (they
reference a marker it cannot resolve), and the reverse is just as possible: a
figure that rasterises cleanly can still be wrong in Chrome. Judging a picture by a
second renderer's opinion of it is a category error, and it is the same one this
project has made before -- believing a proxy instead of looking at the thing.

So: the SVG goes into the page verbatim, inside the same white card and
`color: #0D1117` the review UI uses, and the browser draws it exactly as it will
be drawn in Selectly.

WHAT THE PAGE GIVES YOU that a sheet cannot: the stem, the four options and the
key beside every figure, so "the picture disagrees with the words" is decidable
without looking anything up. Click a card to flag it, type a note if you want, and
press Copy -- you get a list to paste back. Flags survive a reload (localStorage),
so the pass can be done in sittings.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.figure_review_page --scope vic-mq
    # then open  http://<VM_IP>:8000/figures
"""
from __future__ import annotations

import argparse
import collections
import html
import json
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import gate_forms as gf                       # noqa: E402
from tools.sweep_checks import withheld_ids              # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
UI = ROOT / "review/ui"          # every reviewer-facing page lives here

SCOPES = {
    # Every VIC figure lives in maths+quant; reading and verbal carry none.
    "vic-mq": ("(subject = 'quantitative_reasoning' "
               "OR source_book IN ('year9_maths','ma_vic_stats'))"),
    # Thinking Skills carries MORE figures than the two maths books do, and lives
    # under subject='logical_reasoning' rather than a book name -- scoping by book
    # alone left 171 of the 323 out.
    "nsw": ("(subject = 'logical_reasoning' "
            "OR source_book IN ('year7_nsw_maths','ma_nsw_selective'))"),
    "all": "1=1",
}

PAGE = """<!doctype html>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Figure review — %(scope)s</title>
<style>
 :root{--ink:#0D1117;--line:#d8dee6;--flag:#c0392b;--ok:#1e7a3c}
 *{box-sizing:border-box}
 body{margin:0;font:14px/1.5 system-ui,sans-serif;background:#eef1f5;color:var(--ink)}
 header{position:sticky;top:0;z-index:9;background:#fff;border-bottom:1px solid var(--line);
   padding:10px 16px;display:flex;gap:14px;align-items:center;flex-wrap:wrap}
 header b{font-size:15px} .sp{flex:1}
 button{font:inherit;padding:6px 12px;border:1px solid var(--line);background:#fff;
   border-radius:6px;cursor:pointer}
 button.primary{background:var(--ink);color:#fff;border-color:var(--ink)}
 #count{font-variant-numeric:tabular-nums}
 select,input[type=search]{font:inherit;padding:5px 8px;border:1px solid var(--line);border-radius:6px}
 main{padding:16px;display:grid;grid-template-columns:repeat(auto-fill,minmax(430px,1fr));gap:16px}
 .card{background:#fff;border:1px solid var(--line);border-radius:10px;overflow:hidden;
   display:flex;flex-direction:column}
 .card.flagged{border-color:var(--flag);box-shadow:0 0 0 2px rgba(192,57,43,.18)}
 .card.done{opacity:.5}
 .hd{display:flex;gap:10px;align-items:center;padding:8px 10px;border-bottom:1px solid var(--line);
   background:#fafbfc}
 .n{background:var(--ink);color:#fff;border-radius:6px;padding:2px 9px;font-weight:700;
   font-variant-numeric:tabular-nums}
 .meta{font-size:11.5px;color:#667}
 .fig{padding:14px;text-align:center;color:var(--ink);background:#fff}
 .fig svg{max-width:100%%;height:auto}
 .stem{padding:10px 12px;border-top:1px solid var(--line);font-size:13px}
 .opts{padding:0 12px 10px;font-size:12.5px;color:#445}
 .opts b{color:var(--ok)}
 .note{width:100%%;border:0;border-top:1px solid var(--line);padding:7px 12px;font:inherit;
   font-size:12.5px;display:none}
 .card.flagged .note{display:block;background:#fff8f7}
 .acts{display:flex;gap:6px;padding:8px 10px;border-top:1px solid var(--line)}
 .acts button{flex:1;font-size:12.5px}
 dialog{border:1px solid var(--line);border-radius:10px;padding:16px;max-width:640px;width:90%%}
 textarea{width:100%%;height:220px;font:12.5px/1.5 ui-monospace,monospace;border:1px solid var(--line);
   border-radius:6px;padding:8px}
</style>
<header>
 <b>Figure review — %(scope)s</b>
 <span id="count"></span>
 <span class="sp"></span>
 <input id="who" placeholder="your name" size="12">
 <select id="filter">
   <option value="all">show all</option>
   <option value="todo">not yet looked at</option>
   <option value="flagged">flagged only</option>
 </select>
 <input type="search" id="find" placeholder="filter by book or text">
 <button id="download" class="primary">Download my comments</button>
 <button id="copy">Copy as text</button>
 <button id="reset">Clear my marks</button>
</header>
<p style="margin:0;padding:10px 16px;background:#fffbe6;border-bottom:1px solid var(--line);
   font-size:13px">
 Mark each figure <b>Flag a problem</b> or <b>Looks fine</b>, and write a note if you can.
 Your marks are saved in this browser as you go, so you can close the file and come back.
 When you are done press <b>Download my comments</b> and send back the small
 <code>.json</code> file it saves — not this page.
 <b>This file contains the answer keys, so please do not forward it.</b>
</p>
<main id="grid"></main>
<dialog id="out"><h3 style="margin:0 0 8px">Paste this back</h3>
 <textarea id="outtext" readonly></textarea>
 <div style="margin-top:10px;text-align:right"><button onclick="out.close()">Close</button></div>
</dialog>
<script>
const DATA = %(data)s;
const KEY = "figrev:%(scope)s";
// Opened from a file:// URL, Safari refuses localStorage outright and Chrome can
// too depending on how it was launched. The page must still work when saving is
// unavailable -- it just cannot survive a reload, and the reviewer has to be told
// that plainly rather than losing an afternoon's marks to a refresh.
let CAN_SAVE = true;
try { localStorage.setItem(KEY + ":probe", "1"); localStorage.removeItem(KEY + ":probe"); }
catch (e) { CAN_SAVE = false; }
let state = {};
if (CAN_SAVE) { try { state = JSON.parse(localStorage.getItem(KEY) || "{}"); } catch (e) {} }
const save = () => { if (CAN_SAVE) { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {} } };
const grid = document.getElementById("grid");

function card(q){
  const st = state[q.n] || {};
  const el = document.createElement("div");
  el.className = "card" + (st.flag ? " flagged" : "") + (st.ok ? " done" : "");
  el.dataset.n = q.n;
  el.dataset.hay = (q.book + " " + q.form + " " + q.stem).toLowerCase();
  el.innerHTML =
    '<div class="hd"><span class="n">' + q.n + '</span>' +
    '<span class="meta">' + q.book + (q.form ? " &middot; " + q.form : "") +
    ' &middot; ' + q.id.slice(0,8) +
    (q.same > 1 ? ' &middot; <b>same figure as ' + (q.same - 1) +
                  ' other question' + (q.same > 2 ? 's' : '') +
                  ', shown together</b>' : '') + '</span></div>' +
    '<div class="fig">' + q.svg + '</div>' +
    '<div class="stem">' + q.stem + '</div>' +
    '<div class="opts">A ' + q.a + ' &nbsp; B ' + q.b + ' &nbsp; C ' + q.c +
    ' &nbsp; D ' + q.d + ' &nbsp; &rarr; <b>key ' + q.key + '</b></div>' +
    '<input class="note" placeholder="what is wrong with it? (optional)" value="' +
      (st.note || "").replace(/"/g,"&quot;") + '">' +
    '<div class="acts"><button data-act="flag">' +
      (st.flag ? "Un-flag" : "Flag a problem") + '</button>' +
      '<button data-act="ok">' + (st.ok ? "Un-mark" : "Looks fine") + '</button></div>';
  el.querySelector('[data-act=flag]').onclick = () => {
    state[q.n] = Object.assign({}, state[q.n], {flag: !st.flag, ok:false}); save(); draw();
  };
  el.querySelector('[data-act=ok]').onclick = () => {
    state[q.n] = Object.assign({}, state[q.n], {ok: !st.ok, flag:false}); save(); draw();
  };
  el.querySelector('.note').oninput = e => {
    state[q.n] = Object.assign({}, state[q.n], {note: e.target.value}); save();
  };
  return el;
}

function draw(){
  const mode = document.getElementById("filter").value;
  const q = document.getElementById("find").value.trim().toLowerCase();
  grid.innerHTML = "";
  let shown = 0;
  for (const it of DATA){
    const st = state[it.n] || {};
    if (mode === "todo" && (st.flag || st.ok)) continue;
    if (mode === "flagged" && !st.flag) continue;
    if (q && !((it.book + " " + it.form + " " + it.stem).toLowerCase().includes(q))) continue;
    grid.appendChild(card(it)); shown++;
  }
  const f = Object.values(state).filter(s => s.flag).length;
  const k = Object.values(state).filter(s => s.ok).length;
  document.getElementById("count").textContent =
    shown + " shown \\u2022 " + f + " flagged \\u2022 " + k + " marked fine \\u2022 " +
    (DATA.length - f - k) + " left";
}
document.getElementById("filter").onchange = draw;
document.getElementById("find").oninput = draw;
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
    "They will be lost if you reload or close the tab, so press " +
    "<b>Download my comments</b> before you finish, and again whenever you take a break.";
  document.querySelector("header").after(w);
}

document.getElementById("download").onclick = () => {
  // Everything LOOKED AT, not only the flags. "I read it and it is fine" is the
  // half of the answer that says which figures still have nobody's eyes on them.
  const seen = DATA.filter(d => {
    const s = state[d.n] || {}; return s.flag || s.ok || (s.note || "").trim();
  }).map(d => {
    const s = state[d.n];
    return {n: d.n, id: d.id, book: d.book, form: d.form,
            verdict: s.flag ? "problem" : (s.ok ? "fine" : "note"),
            note: (s.note || "").trim(),
            stem: d.stem.slice(0, 120)};
  });
  const doc = {kind: "qbank-figure-review", version: 1, scope: "%(scope)s",
               reviewer: document.getElementById("who").value.trim() || null,
               reviewed_at: new Date().toISOString(),
               total_on_page: DATA.length, reviewed: seen.length, items: seen};
  const blob = new Blob([JSON.stringify(doc, null, 1)], {type: "application/json"});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "figure-review-%(scope)s-" +
               new Date().toISOString().slice(0, 10) + ".json";
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 2000);
};

document.getElementById("copy").onclick = () => {
  const lines = DATA.filter(d => (state[d.n]||{}).flag).map(d => {
    const note = (state[d.n].note || "").trim();
    return d.n + "  " + d.id.slice(0,8) + "  " + d.book +
           (d.form ? " " + d.form : "") + (note ? "  -- " + note : "");
  });
  document.getElementById("outtext").value =
    lines.length ? lines.join("\\n") : "nothing flagged yet";
  document.getElementById("out").showModal();
  document.getElementById("outtext").select();
};
draw();
</script>
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scope", choices=sorted(SCOPES), default="vic-mq")
    ap.add_argument("--book")
    ap.add_argument("--status", default="pending",
                    help="review_status to include (default pending; 'any' for all)")
    ap.add_argument("--include-flagged", action="store_true",
                    help="also include figures a BLOCKING check already names")
    ap.add_argument("-o", "--out", type=pathlib.Path,
                    help="default: review/ui/figures-<scope>.html")
    a = ap.parse_args()

    # ONE FOLDER, ONE NAME PER PAGE. This used to default to a single `figures.html`
    # whatever the scope, so building the NSW page silently replaced the VIC one and
    # the link a reviewer had been given pointed at whichever was built last.
    a.out = a.out or (UI / f"figures-{a.scope}.html")

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    sql = ("SELECT * FROM questions WHERE figure_svg IS NOT NULL AND figure_svg != '' "
           f"AND review_status != 'rejected' AND {SCOPES[a.scope]}")
    args: list = []
    if a.status != "any":
        sql += " AND review_status = ?"
        args.append(a.status)
    if a.book:
        sql += " AND source_book = ?"
        args.append(a.book)
    rows = [dict(r) for r in con.execute(sql, args)]

    # A withheld question is one no student will ever see: the 98 beyond Year 8 and
    # the VIC banned types are held back by the pusher, and `assign_forms` never
    # dealt them into a form. Eleven of them are figures, and putting them in front
    # of a reviewer spends their attention on work that cannot matter -- the first
    # card on the page was one, a circle tangent to both axes, which is conics.
    held = withheld_ids()
    withheld_here = [q for q in rows if q["id"] in held]
    rows = [q for q in rows if q["id"] not in held]

    flagged = {q["id"] for q in rows
               if any(gf.run_check(n, q) for n, _ in gf.BLOCKING)}
    if not a.include_flagged:
        rows = [q for q in rows if q["id"] not in flagged]
    # IDENTICAL FIGURES SIT TOGETHER. Ten of the reviewer's 181 notes were "there are
    # many instances of this figure reused", which is true of the PAGE and not of any
    # paper: 140 questions share a figure with another, and not one form holds the same
    # figure twice, so no student ever meets a picture they have already seen. What
    # the reviewer met was 445 figures in a linear list with the copies scattered
    # through it. Grouping them costs nothing and gives back the attention that was
    # being spent looking at the same chart for the seventh time.
    import hashlib
    for q in rows:
        q["_fig"] = hashlib.md5((q["figure_svg"] or "").encode()).hexdigest()
    seen_first = {}
    for q in rows:
        seen_first.setdefault(q["_fig"], (q["source_book"] or "", q["form_id"] or "",
                                          q["form_position"] or 0))
    rows.sort(key=lambda q: (seen_first[q["_fig"]], q["form_id"] or "",
                             q["form_position"] or 0))
    copies = collections.Counter(q["_fig"] for q in rows)

    def esc(v):
        return html.escape(" ".join(str(v or "").split()))

    data = [{"n": i + 1, "id": q["id"], "book": q["source_book"] or "",
             "same": copies[q["_fig"]],
             "form": q["form_id"] or "", "stem": esc(q["stem"]),
             "a": esc(q["option_a"]), "b": esc(q["option_b"]),
             "c": esc(q["option_c"]), "d": esc(q["option_d"]),
             "key": esc(q["correct_answer"]),
             # verbatim: the browser is the renderer whose opinion counts
             "svg": q["figure_svg"]}
            for i, q in enumerate(rows)]

    a.out.parent.mkdir(parents=True, exist_ok=True)
    # The localStorage key and the download filename both carry the scope, so a
    # reviewer can hold a VIC page and an NSW page open at once without one set of
    # marks overwriting the other.
    a.out.write_text(PAGE % {"scope": a.scope,
                             "data": json.dumps(data, ensure_ascii=False)},
                     encoding="utf-8")
    kb = a.out.stat().st_size / 1024
    print(f"{len(rows)} figures -> {a.out}  ({kb:.0f} KB)")
    if withheld_here:
        print(f"{len(withheld_here)} left out — withheld from serving (beyond Year 8 "
              f"or a banned type), so a reviewer's time on them is spent for nothing")
    if not a.include_flagged:
        print(f"{len(flagged)} left out — a BLOCKING check already names their fault")
    print("\nServe it with the review server already running:")
    print("   http://<VM_IP>:8000/figures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
