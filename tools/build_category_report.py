#!/usr/bin/env python3
"""Render run_data/output/category_report.json as a self-contained HTML page.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.build_category_report

Follows design-system/MASTER.md (Data-Dense Dashboard, dark) rather than inventing a
palette; a light theme is derived from the same hues so the page works in either.

One deliberate reading choice: the confidence band is applied to each category's MINIMUM,
not its mean. Mean confidence sits at 0.94-0.95 in every subject, so banding it paints the
whole table one colour and says nothing. The minimum is what reveals a category holding a
question nobody should trust.
"""
import html
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DATA = ROOT / "run_data" / "output" / "category_report.json"
OUT = ROOT / "run_data" / "output" / "category_report.html"

LABEL = {
    "mathematics": "Mathematics",
    "quantitative_reasoning": "Quantitative Reasoning",
    "verbal_reasoning": "Verbal Reasoning",
    "logical_reasoning": "Logical Reasoning",
    "science_reasoning": "Science Reasoning",
    "reading_comprehension": "Reading Comprehension",
}
ORDER = ["mathematics", "quantitative_reasoning", "verbal_reasoning",
         "logical_reasoning", "science_reasoning", "reading_comprehension"]


def band(v):
    """Bands from design-system/MASTER.md: >=0.90 high, 0.70-0.89 mid, <0.70 low."""
    return "high" if v >= 0.90 else ("mid" if v >= 0.70 else "low")


def esc(s):
    return html.escape(str(s))


def main():
    d = json.loads(DATA.read_text())
    total = sum(d[s]["total"] for s in ORDER)
    cats = sum(d[s]["categories"] for s in ORDER)
    appr = sum(d[s]["approved"] for s in ORDER)
    pend = sum(d[s]["pending"] for s in ORDER)
    rej = sum(d[s]["rejected"] for s in ORDER)
    weak = sum(1 for s in ORDER for c in d[s]["cats"] if c["conf_min"] < 0.80)

    cards, tables, nav = [], [], []
    for s in ORDER:
        v = d[s]
        low = sum(1 for c in v["cats"] if c["conf_min"] < 0.80)
        per = v["total"] / v["categories"]
        nav.append(f'<a class="nav-link" href="#{s}">{esc(LABEL[s])}</a>')
        cards.append(f"""
        <a class="card" href="#{s}">
          <span class="card-name">{esc(LABEL[s])}</span>
          <span class="card-total">{v['total']:,}</span>
          <span class="card-sub">{v['categories']} categories &middot; {per:.1f} per category</span>
          <span class="bar" role="img" aria-label="{v['approved']} approved, {v['pending']} pending, {v['rejected']} rejected">
            <span class="seg seg-a" style="flex:{max(v['approved'],0.001)}"></span
            ><span class="seg seg-p" style="flex:{max(v['pending'],0.001)}"></span
            ><span class="seg seg-r" style="flex:{max(v['rejected'],0.001)}"></span>
          </span>
          <span class="card-meta">
            <span><b>{v['approved']:,}</b> appr</span>
            <span><b>{v['pending']:,}</b> pend</span>
            <span><b>{v['rejected']:,}</b> rej</span>
          </span>
          <span class="card-conf">conf {v['conf_mean']:.2f} <span class="rng">({v['conf_min']:.2f}&ndash;{v['conf_max']:.2f})</span>{
            f'<span class="flag">{low} weak</span>' if low else ''}</span>
        </a>""")

        rows = []
        for c in v["cats"]:
            b = band(c["conf_min"])
            rows.append(
                f'<tr data-topic="{esc(c["topic"].lower())}" data-weak="{1 if c["conf_min"] < 0.80 else 0}">'
                f'<td class="t-topic"><span class="dot dot-{b}"></span>{esc(c["topic"])}</td>'
                f'<td class="num">{c["n"]:,}</td>'
                f'<td class="num sub">{c["approved"]:,}</td>'
                f'<td class="num sub">{c["pending"]:,}</td>'
                f'<td class="num sub">{c["rejected"]:,}</td>'
                f'<td class="num">{c["conf_mean"]:.2f}</td>'
                f'<td class="num conf-{b}">{c["conf_min"]:.2f}</td>'
                f'<td class="num sub">{c["conf_max"]:.2f}</td></tr>')

        books = " &middot; ".join(f"{esc(k)} <b>{n:,}</b>" for k, n in list(v["books"].items())[:6])
        tables.append(f"""
      <section class="subject" id="{s}">
        <header class="sub-head">
          <h2>{esc(LABEL[s])}</h2>
          <p class="sub-stat"><b>{v['total']:,}</b> questions across <b>{v['categories']}</b> categories
             &middot; mean confidence <b>{v['conf_mean']:.2f}</b>
             &middot; {low} categor{'y' if low == 1 else 'ies'} hold a question below 0.80</p>
          <p class="books">{books}</p>
        </header>
        <div class="table-wrap">
          <table>
            <thead><tr>
              <th scope="col">Category</th><th scope="col" class="num">Questions</th>
              <th scope="col" class="num">Appr</th><th scope="col" class="num">Pend</th>
              <th scope="col" class="num">Rej</th>
              <th scope="col" class="num">Conf mean</th><th scope="col" class="num">min</th>
              <th scope="col" class="num">max</th>
            </tr></thead>
            <tbody>{''.join(rows)}</tbody>
          </table>
        </div>
      </section>""")

    page = f"""<title>QBank — Categories by Subject</title>
<style>
  :root {{
    --bg:#0D1117; --surface:#161B22; --raised:#1C2230; --border:#30363D;
    --text:#E6EDF3; --muted:#8B949E;
    --approve:#3FB950; --mid:#E3B341; --reject:#F85149; --action:#58A6FF;
    --mono:'SF Mono','Fira Code','Cascadia Code',ui-monospace,monospace;
    --sans:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
  }}
  @media (prefers-color-scheme: light) {{
    :root {{
      --bg:#F6F8FA; --surface:#FFFFFF; --raised:#EFF2F6; --border:#D3D9E0;
      --text:#1B2129; --muted:#5C6672;
      --approve:#1A7F37; --mid:#9A6700; --reject:#CF222E; --action:#0969DA;
    }}
  }}
  :root[data-theme="light"] {{
    --bg:#F6F8FA; --surface:#FFFFFF; --raised:#EFF2F6; --border:#D3D9E0;
    --text:#1B2129; --muted:#5C6672;
    --approve:#1A7F37; --mid:#9A6700; --reject:#CF222E; --action:#0969DA;
  }}
  :root[data-theme="dark"] {{
    --bg:#0D1117; --surface:#161B22; --raised:#1C2230; --border:#30363D;
    --text:#E6EDF3; --muted:#8B949E;
    --approve:#3FB950; --mid:#E3B341; --reject:#F85149; --action:#58A6FF;
  }}

  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--text); font-family:var(--sans);
         font-size:15px; line-height:1.55; }}
  .wrap {{ max-width:1180px; margin:0 auto; padding:32px 24px 96px; }}

  .masthead {{ display:flex; flex-direction:column; gap:6px;
               border-bottom:1px solid var(--border); padding-bottom:20px; }}
  .eyebrow {{ font-size:11px; font-weight:600; text-transform:uppercase;
              letter-spacing:.1em; color:var(--muted); }}
  h1 {{ margin:0; font-size:27px; font-weight:650; letter-spacing:-.01em; text-wrap:balance; }}
  .totals {{ font-family:var(--mono); font-size:13px; color:var(--muted);
             font-variant-numeric:tabular-nums; }}
  .totals b {{ color:var(--text); }}

  .note {{ margin-top:22px; background:var(--surface); border:1px solid var(--border);
           border-left:2px solid var(--mid); border-radius:5px; padding:14px 18px;
           font-size:13.5px; color:var(--muted); max-width:76ch; }}
  .note b {{ color:var(--text); font-weight:600; }}

  .cards {{ display:grid; gap:12px; margin-top:22px;
            grid-template-columns:repeat(auto-fit,minmax(258px,1fr)); }}
  .card {{ display:flex; flex-direction:column; gap:5px; text-decoration:none; color:inherit;
           background:var(--surface); border:1px solid var(--border); border-radius:6px;
           padding:15px 16px; transition:border-color .12s; }}
  .card:hover, .card:focus-visible {{ border-color:var(--action); }}
  .card:focus-visible {{ outline:2px solid var(--action); outline-offset:2px; }}
  .card-name {{ font-size:11px; font-weight:600; text-transform:uppercase;
                letter-spacing:.08em; color:var(--muted); }}
  .card-total {{ font-family:var(--mono); font-size:25px; font-weight:600; line-height:1.1;
                 font-variant-numeric:tabular-nums; }}
  .card-sub {{ font-size:12.5px; color:var(--muted); }}
  .bar {{ display:flex; height:4px; border-radius:2px; overflow:hidden; margin:5px 0 2px;
          background:var(--raised); }}
  .seg-a {{ background:var(--approve); }} .seg-p {{ background:var(--action); }}
  .seg-r {{ background:var(--reject); }}
  .card-meta {{ display:flex; gap:12px; font-family:var(--mono); font-size:11.5px;
                color:var(--muted); font-variant-numeric:tabular-nums; }}
  .card-meta b {{ color:var(--text); font-weight:600; }}
  .card-conf {{ font-family:var(--mono); font-size:11.5px; color:var(--muted);
                display:flex; align-items:center; gap:8px; font-variant-numeric:tabular-nums; }}
  .rng {{ opacity:.75; }}
  .flag {{ color:var(--mid); border:1px solid currentColor; border-radius:3px;
           padding:0 5px; font-size:10.5px; }}

  .toolbar {{ position:sticky; top:0; z-index:5; display:flex; flex-wrap:wrap; gap:10px;
              align-items:center; margin:30px 0 4px; padding:12px 0;
              background:var(--bg); border-bottom:1px solid var(--border); }}
  #q {{ flex:1 1 240px; min-width:200px; background:var(--surface); color:var(--text);
        border:1px solid var(--border); border-radius:5px; padding:7px 11px;
        font-family:var(--sans); font-size:13.5px; }}
  #q:focus-visible {{ outline:2px solid var(--action); outline-offset:1px; }}
  .toggle {{ display:flex; align-items:center; gap:7px; font-size:13px; color:var(--muted);
             cursor:pointer; user-select:none; }}
  .nav {{ display:flex; flex-wrap:wrap; gap:4px; }}
  .nav-link {{ font-size:12px; color:var(--muted); text-decoration:none;
               border:1px solid var(--border); border-radius:4px; padding:4px 9px; }}
  .nav-link:hover {{ color:var(--text); border-color:var(--action); }}
  .nav-link:focus-visible {{ outline:2px solid var(--action); outline-offset:2px; }}

  .subject {{ margin-top:38px; scroll-margin-top:72px; }}
  .sub-head h2 {{ margin:0; font-size:19px; font-weight:640; letter-spacing:-.005em; }}
  .sub-stat {{ margin:3px 0 0; font-size:13px; color:var(--muted); }}
  .sub-stat b {{ color:var(--text); font-variant-numeric:tabular-nums; }}
  .books {{ margin:5px 0 0; font-family:var(--mono); font-size:11.5px; color:var(--muted);
            font-variant-numeric:tabular-nums; }}
  .books b {{ color:var(--text); }}

  .table-wrap {{ overflow-x:auto; margin-top:12px; border:1px solid var(--border);
                 border-radius:6px; background:var(--surface); }}
  table {{ border-collapse:collapse; width:100%; font-size:13.5px; }}
  thead th {{ position:sticky; top:56px; background:var(--raised); text-align:left;
              font-size:10.5px; font-weight:600; text-transform:uppercase;
              letter-spacing:.07em; color:var(--muted); padding:8px 12px;
              border-bottom:1px solid var(--border); white-space:nowrap; }}
  td {{ padding:7px 12px; border-bottom:1px solid var(--border); }}
  tbody tr:last-child td {{ border-bottom:none; }}
  tbody tr:hover {{ background:var(--raised); }}
  .num {{ text-align:right; font-family:var(--mono); font-variant-numeric:tabular-nums;
          white-space:nowrap; }}
  .sub {{ color:var(--muted); }}
  .t-topic {{ min-width:250px; }}
  .dot {{ display:inline-block; width:6px; height:6px; border-radius:50%;
          margin-right:9px; vertical-align:middle; }}
  .dot-high {{ background:var(--approve); }} .dot-mid {{ background:var(--mid); }}
  .dot-low {{ background:var(--reject); }}
  .conf-high {{ color:var(--approve); }} .conf-mid {{ color:var(--mid); }}
  .conf-low {{ color:var(--reject); }}
  .empty {{ padding:16px; color:var(--muted); font-size:13px; }}
  @media (prefers-reduced-motion: reduce) {{ * {{ transition:none !important; }} }}
</style>

<div class="wrap">
  <header class="masthead">
    <span class="eyebrow">QBank &middot; bank composition</span>
    <h1>Categories by subject</h1>
    <p class="totals"><b>{total:,}</b> questions &middot; <b>{cats:,}</b> categories &middot;
       <b>{appr:,}</b> approved &middot; <b>{pend:,}</b> pending &middot; <b>{rej:,}</b> rejected</p>
  </header>

  <p class="note"><b>Reading the confidence columns.</b> Confidence is a display-only
  triage signal &mdash; it never gates approval. Mean confidence sits at 0.94&ndash;0.95 in
  every subject, so the mean separates almost nothing. The <b>minimum</b> is the useful
  column: it is banded here, and it is what shows a category holding a question nobody
  should trust. <b>{weak}</b> categories contain a question below 0.80.</p>

  <div class="cards">{''.join(cards)}</div>

  <div class="toolbar">
    <input id="q" type="search" placeholder="Filter categories&hellip;" aria-label="Filter categories">
    <label class="toggle"><input type="checkbox" id="weak"> Only categories with a question &lt; 0.80</label>
    <nav class="nav" aria-label="Jump to subject">{''.join(nav)}</nav>
  </div>
  {''.join(tables)}
</div>

<script>
  const q = document.getElementById('q'), weak = document.getElementById('weak');
  function apply() {{
    const term = q.value.trim().toLowerCase(), onlyWeak = weak.checked;
    document.querySelectorAll('section.subject').forEach(sec => {{
      let shown = 0;
      sec.querySelectorAll('tbody tr').forEach(tr => {{
        const hit = (!term || tr.dataset.topic.includes(term))
                 && (!onlyWeak || tr.dataset.weak === '1');
        tr.hidden = !hit;
        if (hit) shown++;
      }});
      sec.hidden = shown === 0;
    }});
  }}
  q.addEventListener('input', apply);
  weak.addEventListener('change', apply);
</script>
"""
    OUT.write_text(page, encoding="utf-8")
    print(f"wrote {OUT}  ({OUT.stat().st_size/1024:.0f} KB)")
    print(f"  {total:,} questions | {cats:,} categories | {weak} categories with a question <0.80")


if __name__ == "__main__":
    main()
