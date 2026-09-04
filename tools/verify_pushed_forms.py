#!/usr/bin/env python3
"""Check that the form assignments qbank pushed actually landed in Selectly.

qbank sends `formId`, `formPosition` and `formKind` with every question, and Selectly's
import writes all three -- but for a long time nothing read them back, so the claim "the
forms are dealt in production" rested on the import code rather than on a check. That is
exactly the hole `qbank_id` was added to `/api/admin/questions-dump` to close, and in
August the fields WERE being silently stripped by zod without anyone noticing.

This compares, per category, the form assignment qbank holds against the one Selectly
returns, and reports:

  * questions live in Selectly with no form at all
  * questions whose form_id or form_position disagrees with qbank
  * approved qbank questions that are not live at all

It needs `formId` in the dump response. Until that ships (Selectly branch
`feature/dump-form-fields`) it says so and exits rather than reporting a false pass --
an absent field is not the same as an empty one.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.verify_pushed_forms
    env -u PYTHONPATH .venv/bin/python3.11 -m tools.verify_pushed_forms --prefix vic-drill-
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sqlite3
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
DB = ROOT / "run_data/db/qbank.db"
CATEGORIES = ("mathematics", "quantitative_reasoning", "reading_comprehension",
              "verbal_reasoning", "logical_reasoning")


def load_env():
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if line.strip() and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip("\"'"))


def dump(url, secret, category):
    req = urllib.request.Request(f"{url}/api/admin/questions-dump?category={category}",
                                 headers={"x-import-secret": secret})
    return json.loads(urllib.request.urlopen(req, timeout=180).read())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--prefix", default="vic-drill-",
                    help="only check questions whose form_id starts with this")
    args = ap.parse_args()
    load_env()
    url = os.environ.get("SELECTLY_URL", "").rstrip("/")
    secret = os.environ.get("SELECTLY_IMPORT_SECRET", "")
    if not url or not secret:
        raise SystemExit("set SELECTLY_URL and SELECTLY_IMPORT_SECRET")

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    bad_missing, bad_noform, bad_wrong = [], [], []
    checked = 0
    for cat in CATEGORIES:
        mine = {r["id"]: r for r in con.execute(
            "SELECT id, form_id, form_position FROM questions "
            " WHERE subject = ? AND review_status = 'approved' AND form_id LIKE ?",
            (cat, args.prefix + "%"))}
        if not mine:
            continue
        d = dump(url, secret, cat)
        rows = d["questions"]
        if rows and "formId" not in rows[0]:
            raise SystemExit(
                "questions-dump does not return formId yet, so this cannot be checked.\n"
                "Deploy Selectly branch feature/dump-form-fields first — an absent "
                "field is not an empty one, and reporting a pass here would be a lie.")
        theirs = {r["qbankId"]: r for r in rows if r.get("qbankId")}
        for qid, m in mine.items():
            checked += 1
            t = theirs.get(qid)
            if t is None:
                bad_missing.append((cat, qid, m["form_id"]))
            elif not t.get("formId"):
                bad_noform.append((cat, qid, m["form_id"]))
            elif (t["formId"] != m["form_id"]
                  or t.get("formPosition") != m["form_position"]):
                bad_wrong.append((cat, qid, m["form_id"], m["form_position"],
                                  t["formId"], t.get("formPosition")))
        print("%-24s qbank %5d   live with a form %5d"
              % (cat, len(mine), sum(1 for q in mine
                                     if theirs.get(q, {}).get("formId"))))
    print("\nchecked %d approved questions carrying a %s form" % (checked, args.prefix))
    print("  not live in Selectly      : %d" % len(bad_missing))
    print("  live but carrying no form : %d" % len(bad_noform))
    print("  form differs from qbank   : %d" % len(bad_wrong))
    for label, rows in (("NOT LIVE", bad_missing), ("NO FORM", bad_noform),
                        ("MISMATCH", bad_wrong)):
        for r in rows[:5]:
            print("   %-9s %s" % (label, r))
        if len(rows) > 5:
            print("   %-9s ... and %d more" % (label, len(rows) - 5))
    ok = not (bad_missing or bad_noform or bad_wrong)
    print("\n%s" % ("every form assignment landed" if ok else "SOMETHING IS WRONG"))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
