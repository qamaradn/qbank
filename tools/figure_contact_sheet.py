#!/usr/bin/env python3
"""Render question figures into one labelled contact sheet PNG, so they can be LOOKED at.

Why this exists
---------------
Code can verify that a figure is mathematically right; it cannot tell you the figure is
unreadable. On the Year 7 maths book, assertions over the geometry caught a "rhombus" whose
sides were 155 and 125 while the stem told students all four sides were equal — but only
looking at the rendered images caught nine presentation defects that no assertion would
ever flag: labels clipped past the viewBox edge, Venn labels overlapping the circles,
a balance scale whose weights sat on the beam with empty pans dangling below, hanger lines
drawn through the blocks, and a kite with near-equal sides that read as a rhombus.

So: verify the maths with code, then render and look. Neither check substitutes for the other.

Colour matters
--------------
The review UI puts each figure in a WHITE card with `color: #0D1117`, and the figures are
drawn with `currentColor`. Rendering on a default (transparent/black) background would hide
exactly the contrast and opacity problems you are looking for, so the card's real colours are
injected here before rasterising.

Usage
-----
    # straight from the DB — one batch, a whole book, or a whole subject
    .venv/bin/python3.11 -m tools.figure_contact_sheet --subject mathematics --page 52
    .venv/bin/python3.11 -m tools.figure_contact_sheet --book year7_nsw_maths
    .venv/bin/python3.11 -m tools.figure_contact_sheet --subject mathematics --limit 12

    # from generated JSON, BEFORE loading into the DB (the useful moment to catch problems)
    .venv/bin/python3.11 -m tools.figure_contact_sheet \
        --json run_data/output/mathematics/generated/year7_nsw_maths_p52.json

Then open the PNG and check every figure against its stem.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import pathlib
import re
import sqlite3
import sys

import cairosvg
from PIL import Image, ImageDraw

# The review card: white background, near-black text. Figures use currentColor.
CARD_BG = "white"
CARD_FG = "#0D1117"

SCALE = 1.6      # upscale so 9-11px SVG labels stay legible in the sheet
COLS = 2
PAD, HEAD = 12, 26

DEFAULT_DB = os.environ.get("DB_PATH", "run_data/db/qbank.db")


def render_svg(svg: str) -> Image.Image:
    """Rasterise one figure the way a reviewer will actually see it."""
    svg = re.sub(r"<svg\b", f'<svg style="color:{CARD_FG}"', svg, count=1)
    png = cairosvg.svg2png(bytestring=svg.encode(), background_color=CARD_BG, scale=SCALE)
    return Image.open(io.BytesIO(png)).convert("RGB")


def tile(label: str, img: Image.Image) -> Image.Image:
    canvas = Image.new("RGB", (img.width + 2 * PAD, img.height + HEAD + PAD), CARD_BG)
    canvas.paste(img, (PAD, HEAD))
    dr = ImageDraw.Draw(canvas)
    dr.text((PAD, 7), label, fill="black")
    dr.rectangle([0, 0, canvas.width - 1, canvas.height - 1], outline="#999")
    return canvas


def build_sheet(items: list[tuple[str, str]], out: pathlib.Path) -> pathlib.Path:
    """items = [(label, svg), ...]"""
    tiles = [tile(lab, render_svg(svg)) for lab, svg in items]
    w = max(t.width for t in tiles)
    h = max(t.height for t in tiles)
    rows = (len(tiles) + COLS - 1) // COLS
    sheet = Image.new("RGB", (COLS * w, rows * h), CARD_BG)
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % COLS) * w, (i // COLS) * h))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    return out


def _label(desc: str | None, fallback: str) -> str:
    """Prefer the subtopic ref (e.g. "U12") — short and unique on the sheet."""
    if desc:
        m = re.search(r"Subtopic (\S+)", desc)
        if m:
            return m.group(1)
        return desc[:28]
    return fallback


def from_json(path: pathlib.Path) -> list[tuple[str, str]]:
    qs = json.loads(path.read_text(encoding="utf-8"))
    return [(_label(q.get("source_page_description"), q.get("id", "?")[:8]), q["figure_svg"])
            for q in qs if q.get("figure_svg")]


def from_db(db: str, subject: str | None, book: str | None,
            page: int | None, limit: int | None) -> list[tuple[str, str]]:
    where, args = ["figure_svg IS NOT NULL", "review_status != 'rejected'"], []
    for col, val in (("subject", subject), ("source_book", book), ("source_page", page)):
        if val is not None:
            where.append(f"{col} = ?")
            args.append(val)
    sql = ("SELECT source_page, source_page_description, id, figure_svg FROM questions "
           f"WHERE {' AND '.join(where)}")
    if limit:
        sql += f" LIMIT {int(limit)}"
    con = sqlite3.connect(db)
    rows = [(pg, _label(d, i[:8]), svg) for pg, d, i, svg in con.execute(sql, args)]
    # Natural order, so U4 precedes U12 rather than sorting lexically after it.
    def key(row):
        m = re.match(r"([A-Za-z]+)(\d+)", row[1])
        return (row[0] or 0, m.group(1), int(m.group(2))) if m else (row[0] or 0, row[1], 0)
    return [(lab, svg) for _, lab, svg in sorted(rows, key=key)]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=pathlib.Path, help="render figures from a generated JSON file")
    p.add_argument("--db", default=DEFAULT_DB, help=f"SQLite path (default {DEFAULT_DB})")
    p.add_argument("--subject")
    p.add_argument("--book", help="source_book")
    p.add_argument("--page", type=int, help="source_page (one batch)")
    p.add_argument("--limit", type=int)
    p.add_argument("-o", "--out", type=pathlib.Path, help="output PNG path")
    a = p.parse_args()

    if a.json:
        items = from_json(a.json)
        default_out = a.json.with_suffix(".sheet.png")
    else:
        if not any((a.subject, a.book, a.page)):
            p.error("give --json, or at least one of --subject / --book / --page")
        items = from_db(a.db, a.subject, a.book, a.page, a.limit)
        stem = "_".join(str(x) for x in (a.subject, a.book, a.page) if x)
        default_out = pathlib.Path(f"run_data/figure_sheets/{stem}.png")

    if not items:
        print("no figures matched", file=sys.stderr)
        return 1

    out = build_sheet(items, a.out or default_out)
    print(f"{out}  —  {len(items)} figures")
    for lab, svg in items:
        print(f"   {len(svg):5}b  {lab}")
    print("\nNow OPEN it and check every figure against its stem.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
