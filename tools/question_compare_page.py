#!/usr/bin/env python3
"""One HTML page showing what happened to EVERY question the reviewer flagged --
the wording as well as the picture.

WHY THIS EXISTS. `figure_compare_page` reads
`WHERE figure_svg IS NOT NULL`, which was right while every round was a figure round.
Round 12 is not: the flags now come out of Selectly's own flag queue as a CSV, and of
the first 33, twelve are questions with no figure at all -- a calculator needed, a
number that will not round cleanly, a prose question sitting in a maths paper, markup
leaking into a stem. Those twelve were repaired and then fell off the page, so the
reviewer would have seen twenty-one of thirty-three and no way to tell whether the
rest had been looked at.

It also shows the WORDS BOTH WAYS. A repaired figure is obvious side by side; a
re-cut question is not. 'What is the total time taken for the journey, rounded to two
decimal places?' becoming 'What is the total time taken for the journey?' is the whole
point of that repair, and a page showing only the new wording hides it.

The BEFORE comes out of a database backup, so the page can be rebuilt at any time from
two things that are both kept: the backup taken before the round and the live database.

It marks and downloads the SAME JSON as every other reviewer page, so
`tools.ingest_figure_review` reads it back unchanged.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.question_compare_page \\
        --before run_data/db/qbank.db.bak-round12-203751 \\
        --csv review/ui/flagged-questions-2026-09-11.csv \\
        --scope vic-uiflags-all
"""
from __future__ import annotations

import argparse
import csv as _csv
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
<title>Question repairs &mdash; before and after</title>
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
 .badge{float:right;font-size:11px;letter-spacing:.05em;text-transform:uppercase;
        font-weight:700;padding:2px 8px;border-radius:20px}
 .badge.recut{background:#f3e8fd;color:#6b2ab5}
 .badge.redrawn{background:#e6f4ea;color:var(--new)}
 .badge.reworded{background:#e8eefc;color:#2a4b9b}
 .badge.same{background:#fdece9;color:var(--old)}
 .why{padding:9px 14px;background:#f6f7f9;border-bottom:1px solid var(--line);
      font-size:13px;color:#5a6572}
 .note{padding:9px 14px;background:#fff8e8;border-bottom:1px solid var(--line);
       font-size:14px}
 .note::before{content:"you wrote: ";color:#8a6d1c;font-weight:600}
 .pair{display:grid;grid-template-columns:1fr 1fr;gap:0;
       border-bottom:1px solid var(--line)}
 .pair:last-of-type{border-bottom:0}
 .cell{padding:14px;min-width:0}
 .cell+.cell{border-left:1px solid var(--line)}
 .cell.b{background:#fffafa}
 .tag{font-size:11px;letter-spacing:.06em;text-transform:uppercase;font-weight:700;
      margin-bottom:8px}
 .cell.b .tag{color:var(--old)} .cell.a .tag{color:var(--new)}
 .cell.one .tag{color:#5a6572}
 .pic{text-align:center}
 .cell svg{max-width:100%;height:auto}
 .stem{font-size:13.5px;color:#222;margin-bottom:8px}
 .opts{font-size:13px;color:#444;margin-bottom:8px}
 .opts div{padding:1px 0}
 .opts .k{color:var(--new);font-weight:700}
 .expl{font-size:12.5px;color:#5a6572;border-top:1px dashed var(--line);
       padding-top:7px}
 @media (max-width:860px){.pair{grid-template-columns:1fr}
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
  <h1>Question repairs &mdash; before and after</h1>
  <div class="sub">__SUMMARY__<br>Left is what you flagged; right is what is in the
    bank now. Some of these changed in words only and have no picture &mdash; read the
    question and the four options on both sides. Mark anything still wrong, type what
    is wrong with it, then press <b>Download my comments</b> and send the file back.
    </div>
  <div class="bar">
    <input id="find" placeholder="filter by form, book or words in the question"
           style="min-width:260px">
    <select id="filter">
      <option value="all">show all</option>
      <option value="todo">not yet marked</option>
      <option value="flagged">still a problem</option>
      <option value="pic">picture changed</option>
      <option value="words">words changed</option>
      <option value="same">not changed</option>
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
const KEY = "qbank-qcompare:" + SCOPE;
const grid = document.getElementById("grid");

let CAN_SAVE = true, state = {};
try { state = JSON.parse(localStorage.getItem(KEY) || "{}"); }
catch (e) { CAN_SAVE = false; }
function save(){ try { localStorage.setItem(KEY, JSON.stringify(state)); }
                 catch (e) { CAN_SAVE = false; } }

function words(side, tag){
  let h = '<div class="tag">' + tag + '</div><div class="stem">' + side.stem +
          '</div><div class="opts">';
  for (const L of ['a','b','c','d'])
    h += '<div' + (L === side.key ? ' class="k"' : '') + '>' + L.toUpperCase() +
         ')&nbsp; ' + side[L] + (L === side.key ? '  \\u2190 answer' : '') + '</div>';
  return h + '</div><div class="expl">' + side.expl + '</div>';
}

function card(d){
  const st = state[d.n] || {};
  const el = document.createElement("div");
  el.className = "item" + (st.flag ? " flagged" : "") + (st.ok ? " done" : "");
  const BADGE = {recut: "re-cut", redrawn: "redrawn", reworded: "wording fixed",
                 same: "not changed"};
  // The WORDS. Shown both ways only when they changed -- putting identical text in
  // two columns reads as "look, it is different now" when it is not.
  const wordBlock = d.wordsChanged
    ? '<div class="pair"><div class="cell b">' + words(d.before, "you flagged this") +
      '</div><div class="cell a">' + words(d.after, "in the bank now") + '</div></div>'
    : '<div class="pair"><div class="cell one">' +
      words(d.after, "the question, unchanged") + '</div></div>';
  // The PICTURE, on the same rule.
  let picBlock = '';
  if (d.picChanged)
    picBlock = '<div class="pair"><div class="cell b pic"><div class="tag">' +
      (d.beforeSvg ? 'picture before' : 'there was no picture') + '</div>' +
      (d.beforeSvg || '') + '</div><div class="cell a pic">' +
      '<div class="tag">picture now</div>' + d.afterSvg + '</div></div>';
  else if (d.afterSvg)
    picBlock = '<div class="pair"><div class="cell one pic">' +
      '<div class="tag">the picture, unchanged</div>' + d.afterSvg + '</div></div>';
  el.innerHTML =
    '<div class="hd"><b>' + d.n + '</b> &middot; ' + d.book +
    (d.form ? ' &middot; ' + d.form + ' q' + d.pos : '') + ' &middot; ' + d.id +
    '<span class="badge ' + d.status + '">' + BADGE[d.status] + '</span></div>' +
    (d.note ? '<div class="note">' + d.note + '</div>' : '') +
    (d.why ? '<div class="why">' + d.why + '</div>' : '') +
    wordBlock + picBlock +
    '<div class="acts">' +
      '<input class="say" placeholder="what is still wrong with it?" value="' +
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
    if (mode === "pic" && !d.picChanged) continue;
    if (mode === "words" && !d.wordsChanged) continue;
    if (mode === "same" && d.status !== "same") continue;
    if (q && !d.hay.includes(q)) continue;
    grid.appendChild(card(d)); n++;
  }
  const f = Object.values(state).filter(s => s.flag).length;
  const k = Object.values(state).filter(s => s.ok).length;
  document.getElementById("count").textContent =
    n + " shown \\u2022 " + f + " still a problem \\u2022 " + k + " fixed \\u2022 " +
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
  const seen = DATA.filter(d => {
    const s = state[d.n] || {}; return s.flag || s.ok || (s.note || "").trim();
  }).map(d => {
    const s = state[d.n];
    return {n: d.n, id: d.full, book: d.book, form: d.form,
            verdict: s.flag ? "problem" : (s.ok ? "fine" : "note"),
            note: (s.note || "").trim(), stem: d.after.stem.slice(0, 120)};
  });
  const doc = {kind: "qbank-figure-review", version: 1, scope: SCOPE,
               reviewer: document.getElementById("who").value.trim() || null,
               reviewed_at: new Date().toISOString(),
               total_on_page: DATA.length, reviewed: seen.length, items: seen};
  const blob = new Blob([JSON.stringify(doc, null, 1)], {type: "application/json"});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "question-review-" + SCOPE + "-" +
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

WORD_FIELDS = ("stem", "option_a", "option_b", "option_c", "option_d",
               "correct_answer", "explanation")


def esc(v):
    return html.escape(" ".join(str(v or "").split()))


def side(r):
    return {"stem": esc(r["stem"]), "a": esc(r["option_a"]), "b": esc(r["option_b"]),
            "c": esc(r["option_c"]), "d": esc(r["option_d"]),
            "key": (r["correct_answer"] or "").strip().lower(),
            "expl": esc(r["explanation"])}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--before", type=pathlib.Path, required=True,
                    help="database backup taken before the repairs")
    ap.add_argument("--csv", type=pathlib.Path,
                    help="Selectly's flag-queue export, so their note sits on the card")
    ap.add_argument("--review", type=pathlib.Path,
                    help="a reviewer JSON instead, same purpose")
    ap.add_argument("--why", type=pathlib.Path,
                    help="JSON map of question id (or its first 8 characters) to a "
                         "sentence for that card, where the automatic one would "
                         "mislead -- a flag resolved by changing a DIFFERENT question "
                         "reads as 'not changed' otherwise")
    ap.add_argument("--scope", required=True,
                    help="names the download and keeps this page's marks separate")
    ap.add_argument("-o", "--out", type=pathlib.Path,
                    help="default: review/ui/compare-<scope>.html")
    a = ap.parse_args()
    out = a.out or (ROOT / "review/ui" / f"compare-{a.scope}.html")

    notes, order, pos = {}, {}, {}
    if a.csv:
        with a.csv.open(newline="", encoding="utf-8") as fh:
            for i, row in enumerate(_csv.DictReader(fh), 1):
                notes[row["qbank_id"]] = row.get("note") or ""
                order[row["qbank_id"]] = i
                pos[row["qbank_id"]] = row.get("form_position") or ""
    if a.review and a.review.exists():
        for it in json.loads(a.review.read_text()).get("items", []):
            notes.setdefault(it["id"], it.get("note") or "")
            order.setdefault(it["id"], it.get("n", 0))
    if not notes:
        ap.error("give --csv or --review: a page with no notes on it is not a review")

    said = {}
    if a.why and a.why.exists():
        said = json.loads(a.why.read_text())

    now = sqlite3.connect(DB)
    now.row_factory = sqlite3.Row
    old = sqlite3.connect(f"file:{a.before}?mode=ro", uri=True)
    old.row_factory = sqlite3.Row

    data, missing = [], []
    for qid in sorted(notes, key=lambda i: order.get(i, 10 ** 6)):
        r = now.execute("SELECT * FROM questions WHERE id=?", (qid,)).fetchone()
        o = old.execute("SELECT * FROM questions WHERE id=?", (qid,)).fetchone()
        if r is None or o is None:
            missing.append(qid)
            continue
        wc = any((o[f] or "") != (r[f] or "") for f in WORD_FIELDS)
        pc = (o["figure_svg"] or "") != (r["figure_svg"] or "")
        status = ("recut" if wc and pc else
                  "reworded" if wc else "redrawn" if pc else "same")
        why = said.get(qid) or said.get(qid[:8]) or ""
        if why:
            pass
        elif status == "same":
            why = ("Not changed. Nothing here has been altered since you flagged it "
                   "— say whether it still needs to be.")
        elif status == "reworded":
            why = ("The question or its options were corrected. There is no picture "
                   "on this one, or the picture was already right.")
        elif pc and not (o["figure_svg"] or ""):
            why = "This question had no picture before. One has been drawn for it."
        data.append({
            "n": order.get(qid, len(data) + 1), "id": qid[:8], "full": qid,
            "book": r["source_book"] or "", "form": r["form_id"] or "",
            "pos": pos.get(qid, r["form_position"] or ""),
            "status": status, "wordsChanged": wc, "picChanged": pc,
            "why": esc(why), "note": esc(notes.get(qid, "")),
            "before": side(o), "after": side(r),
            "beforeSvg": o["figure_svg"] or "", "afterSvg": r["figure_svg"] or "",
            "hay": " ".join([r["source_book"] or "", r["form_id"] or "",
                             r["stem"] or ""]).lower()})

    import collections
    tally = collections.Counter(d["status"] for d in data)
    marked = sum(1 for d in data if d["note"])
    pics = sum(1 for d in data if d["picChanged"])
    wordy = sum(1 for d in data if d["wordsChanged"])
    summary = (f"<b>{len(data)}</b> questions you flagged: "
               f"<b>{tally.get('recut', 0)}</b> re-cut, "
               f"<b>{tally.get('redrawn', 0)}</b> redrawn, "
               f"<b>{tally.get('reworded', 0)}</b> with the wording fixed, "
               f"<b>{tally.get('same', 0)}</b> not changed. "
               f"{pics} have a new picture and {wordy} changed in words. "
               f"<b>{marked}</b> carry a note you wrote.")
    page = (PAGE.replace("__SUMMARY__", summary)
                .replace("__SCOPE__", a.scope)
                .replace("__DATA__", json.dumps(data, ensure_ascii=False)))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print(f"{len(data)} questions -> {out}  ({len(page) // 1024} KB)")
    for k, label in (("recut", "re-cut (words and picture)"),
                     ("redrawn", "redrawn, wording as it was"),
                     ("reworded", "wording fixed, no picture change"),
                     ("same", "NOT CHANGED")):
        if tally.get(k):
            print(f"  {tally[k]:5d}  {label}")
    print(f"  {marked:5d}  carry the reviewer's own note")
    if missing:
        print(f"  {len(missing):5d}  flagged ids not found in both databases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
