#!/usr/bin/env python3
"""VIC review round 8: the figures whose fault is their own, one at a time.

Round 8's flags fell into classes that each got a tool -- overlapping labels, arcs
that sweep past their angle, floating grids, bare planes, raw LaTeX. This holds what
was left: figures that are individually wrong and share nothing with anything else.

`dfc0c664` — THE ONLY FIGURE IN THE BANK THAT WILL NOT RASTERISE. It carries two
complete legends stacked on each other: an older one built from "■" glyphs and a
newer one built from colour swatches, drawn at the same four y positions so every row
reads doubled. It also carries a fifth, orphaned legend row saying "Car (30%)" a
second time, written as `<text x='236' ... x='250'>` -- a duplicate attribute, which
is not valid XML, and which cairosvg refuses the whole document over. A half-applied
nudge from some earlier round, never rendered afterwards.

Underneath all that the pie is wrong as well: the four sectors are drawn at 60°, 30°,
180° and 90° while the legend says 30%, 15%, 40% and 15%, which is 108°, 54°, 144°
and 54°. Every slice is the wrong size, and the question asks for a probability read
off the chart. So it is redrawn by `figure_lib.pie_chart`, where the angles come from
the counts and a sector labelled 15% is 15%.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_vic_round8
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.repair_vic_round8 --apply
"""
import argparse
import json
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import figure_lib as fl                 # noqa: E402
from tools import question_checks as qc            # noqa: E402
from tools.repair_grid_reach import ALL_FIG        # noqa: E402

DB = ROOT / "run_data/db/qbank.db"
RECORD = ROOT / "run_data/output/vic_round8_repairs.json"

# 200 Year 9 students: Car 30%, Bus 15%, Walk 40%, Train 15%.
FIGURES = {
    "dfc0c664": lambda: fl.pie_chart([("Car (30%)", 60), ("Bus (15%)", 30),
                                      ("Walk (40%)", 80), ("Train (15%)", 30)]),
}


def state(q, svg):
    row = dict(q)
    row["figure_svg"] = svg
    return ({n for n in ALL_FIG + ["angle_arc_misses_its_rays"]
             if getattr(qc, n)(svg)}
            | {n for n in ("angle_named_without_arc", "figure_proportions_disagree",
                           "polygon_sides_disagree_with_stem",
                           "plotted_geometry_matches_stem") if getattr(qc, n)(row)})


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dump", type=pathlib.Path)
    args = ap.parse_args()
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    done, refused, dump = [], [], []
    for prefix, build in FIGURES.items():
        row = con.execute("SELECT * FROM questions WHERE id LIKE ?",
                          (prefix + "%",)).fetchone()
        if row is None:
            refused.append({"id": prefix, "why": "no such question"})
            continue
        q = dict(row)
        before = state(q, q["figure_svg"])
        new = build()
        gained = state(q, new) - before
        if gained:
            refused.append({"id": q["id"], "newly_firing": sorted(gained)})
            continue
        done.append({"id": q["id"], "form": q["form_id"],
                     "cleared": sorted(before - state(q, new)),
                     "left": sorted(state(q, new))})
        dump.append({"id": prefix + "-BEFORE", "figure_svg": q["figure_svg"],
                     "stem": q["stem"]})
        dump.append({"id": prefix + "-AFTER", "figure_svg": new, "stem": q["stem"]})
        if args.apply:
            con.execute("UPDATE questions SET figure_svg = ?, edited = 1 WHERE id = ?",
                        (new, q["id"]))
    if args.apply:
        con.commit()
    if args.dump:
        args.dump.write_text(json.dumps(dump))
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps({"applied": args.apply, "redrawn": done,
                                  "refused": refused}, indent=1))
    print(f"{len(done)} redrawn, {len(refused)} refused"
          f"{'' if args.apply else '  (dry run — pass --apply)'}")
    for r in refused:
        print("   refused", r["id"][:8], r.get("newly_firing") or r["why"])
    print(f"record -> {RECORD}")


if __name__ == "__main__":
    main()
