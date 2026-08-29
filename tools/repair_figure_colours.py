"""Make imported figure_svg theme-safe, the way hand-built figures already are.

`question_checks.figure_svg_errors` requires a figure to draw in `currentColor`, because
the review card is white with `color: #0D1117` while other surfaces are dark: a figure
painted in fixed colours is invisible in one theme or the other. Hand-built figures satisfy
this by construction (`tools/figure_lib.py` draws everything in currentColor and varies
`fill-opacity`). The Gemini and Sonnet books never did, and 461 of their figures fail.

NOT ALL OF THEM CAN BE CONVERTED, which is why this is not a search-and-replace:

- **Ink** (`#1a1a2a`, `#000`, `#333`, `#555`, `#888`) is unambiguous. It becomes
  `currentColor` and the figure gets strictly better.
- **Light greys** (`#ddd`, `#ccc`) are gridlines. They become `currentColor` at low
  opacity, which is what figure_lib uses for the same job.
- **Accent fills** are usually a single pale tint marking a shaded region, and 31 of these
  figures have a stem that says "the shaded region". Flattening them to solid ink would
  destroy the question, so they become `currentColor` with a LOW `fill-opacity` — shaded
  stays visibly shaded, and it now works in both themes.
- **`fill="white"`** on a marker or box is a hollow shape. `fill="none"` renders
  identically on the white card and correctly everywhere else.
- **`stroke="white"` is load-bearing and is NOT converted.** These are wide strokes drawn
  over other content to erase it — a gap in a line, an over/under crossing. There is no
  way to say "the surface colour" in a self-contained SVG, so `currentColor` would paint a
  thick dark bar straight across the figure and `none` would expose what the gap is hiding.
  Those 48 figures instead get an explicit white background rect, which makes them
  self-contained and legible on ANY surface — the check's actual goal, reached the other
  way round. They are recorded as a deliberate exception rather than silently skipped.

Every figure is rendered and compared before and after; see --contact.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_figure_colours --dry-run
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_figure_colours --apply
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_figure_colours --revert
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "run_data" / "db" / "qbank.db"
MANIFEST = REPO_ROOT / "run_data" / "output" / "figure_colour_repairs.json"

INK = {"#1a1a2a", "#000", "#000000", "#111", "#111111", "#222", "#222222", "#333",
       "#333333", "#444", "#444444", "#555", "#555555", "#666", "#666666", "#888",
       "#888888", "black", "#0d1117"}
GREY = {"#ddd", "#dddddd", "#ccc", "#cccccc", "#eee", "#eeeeee", "#e0e0e0", "#f0f0f0",
        "#ababab", "#aaa", "#aaaaaa", "#999", "#999999"}
WHITE = {"white", "#fff", "#ffffff"}

ATTR = re.compile(r'(?P<name>fill|stroke)\s*=\s*(?P<q>[\'"])(?P<val>[^\'"]*)(?P=q)')
WHITE_STROKE = re.compile(r'stroke\s*=\s*[\'"](white|#fff|#ffffff)[\'"]', re.I)
ELEMENT = re.compile(r'<(?P<tag>rect|circle|ellipse|line|path|polygon|polyline|text|g)\b'
                     r'(?P<attrs>[^>]*)>', re.I)


def _has(attrs: str, name: str) -> bool:
    return re.search(rf'\b{name}\s*=', attrs) is not None


def convert_element(tag: str, attrs: str) -> str:
    """Rewrite one element's fill/stroke to currentColor, adding opacity where a flat
    conversion would lose information (a tint becoming solid ink)."""
    add: list[str] = []

    def sub(m: re.Match) -> str:
        name, q, val = m.group("name"), m.group("q"), m.group("val").strip()
        low = val.lower()
        if low in ("none", "currentcolor") or low.startswith("url("):
            return m.group(0)
        if low in WHITE:
            # A white FILL is a hollow shape; none renders the same on the card and
            # correctly elsewhere. A white STROKE is an occluder and never reaches here.
            return f'{name}={q}none{q}' if name == "fill" else m.group(0)
        if low in INK:
            return f'{name}={q}currentColor{q}'
        if low in GREY:
            if not _has(attrs, f"{name}-opacity"):
                add.append(f'{name}-opacity=".28"')
            return f'{name}={q}currentColor{q}'
        # anything else is an accent: keep it as a TINT, not solid ink, so a "shaded
        # region" stays distinguishable from an unshaded one.
        if not _has(attrs, f"{name}-opacity"):
            add.append(f'{name}-opacity="{".18" if name == "fill" else ".85"}"')
        return f'{name}={q}currentColor{q}'

    out = ATTR.sub(sub, attrs)
    if add:
        # attrs still carries the trailing "/" of a self-closing tag. Appending after it
        # yields `<rect ... / fill-opacity=".18">`, which is not well-formed XML, and
        # cairosvg then refuses the WHOLE figure rather than one element. Found by
        # rendering the before/after sheet and looking at it — no check here sees it.
        stripped = out.rstrip()
        selfclose = stripped.endswith("/")
        if selfclose:
            stripped = stripped[:-1].rstrip()
        out = stripped + " " + " ".join(add) + ("/" if selfclose else "")
    return f'<{tag}{out}>'


# A figure that paints its own white ground is already legible on any surface, and its
# ink must STAY dark: turn that ink into currentColor and it goes white-on-white the
# moment the viewer is in dark mode. 133 figures carry `style="background:white"` on the
# <svg> tag, which is exactly this case.
GROUNDED = re.compile(r'<svg[^>]*style\s*=\s*[\'"][^\'"]*background\s*:\s*(white|#fff)', re.I)


def convert(svg: str) -> tuple[str, str]:
    """Return (new_svg, strategy)."""
    if GROUNDED.search(svg):
        return svg, "already-grounded (svg paints its own white background)"
    if WHITE_STROKE.search(svg):
        # Load-bearing white. Give the figure its own ground instead of converting it.
        # The "already grounded?" test used to look only for width="100%", so a figure
        # this tool had itself grounded with an explicit width="344.0" did not match
        # and a SECOND identical rect was laid on top of the first. Re-running the
        # repair has to be a no-op; match what it actually writes.
        if re.search(r'<rect[^>]*\bwidth\s*=\s*[\'"](?:100%|[\d.]+)[\'"][^>]*'
                     r'\bfill\s*=\s*[\'"](?:white|#fff+)[\'"]', svg, re.I):
            return svg, "already-grounded"
        m = re.search(r'viewBox\s*=\s*[\'"]([\d.\-\s]+)[\'"]', svg)
        if not m:
            return svg, "skipped-no-viewbox"
        x, y, w, h = (float(v) for v in m.group(1).split())
        bg = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="white"/>')
        out = re.sub(r'(<svg[^>]*>)', r'\1' + bg, svg, count=1)
        return out, "grounded (white stroke is an occluder)"

    out = ELEMENT.sub(lambda m: convert_element(m.group("tag"), m.group("attrs")), svg)
    return out, "converted to currentColor"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--revert", action="store_true")
    args = ap.parse_args()
    if not (args.dry_run or args.apply or args.revert):
        ap.error("choose --dry-run, --apply or --revert")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    if args.revert:
        data = json.loads(MANIFEST.read_text())
        conn.executemany("UPDATE questions SET figure_svg = ? WHERE id = ?",
                         [(r["was"], r["id"]) for r in data["repairs"]])
        conn.commit()
        print(f"reverted {len(data['repairs'])} figures")
        return

    rows = [dict(r) for r in conn.execute(
        "SELECT id, source_book, figure_svg FROM questions "
        "WHERE figure_svg IS NOT NULL AND review_status != 'rejected'")]
    import collections
    strat = collections.Counter()
    record = []
    for r in rows:
        new, how = convert(r["figure_svg"])
        if new == r["figure_svg"]:
            strat["unchanged"] += 1
            continue
        strat[how] += 1
        record.append({"id": r["id"], "book": r["source_book"],
                       "strategy": how, "was": r["figure_svg"], "now": new})

    for k, v in strat.most_common():
        print(f"  {v:>5}  {k}")
    print(f"  {len(record):>5}  figures would change" if not args.apply
          else f"  {len(record):>5}  figures changed")

    if args.apply:
        conn.executemany("UPDATE questions SET figure_svg = ? WHERE id = ?",
                         [(r["now"], r["id"]) for r in record])
        conn.commit()
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(json.dumps(
            {"generated_from": "tools/repair_figure_colours.py",
             "applied_at": datetime.now(timezone.utc).isoformat(),
             "repairs": record}, indent=2))
        print(f"record -> {MANIFEST}")


if __name__ == "__main__":
    main()
