#!/usr/bin/env python3
"""Finalise one NSW writing-prompt batch.

Usage:  env -u PYTHONPATH .venv/bin/python3.11 -m tools.wr_finalise <NN> [--check-only]

Writing prompts are not MCQs, so almost none of the question_checks apply: there are no
options, no key, no distractors. What can go wrong here is different and mostly a matter
of calibration and of the task being answerable:

`calibration` — NSW Writing is one prompt in 30 minutes, sat in Year 6 (taxonomy §1).
Every prompt is checked against that, because the ten NSW prompts already in the table
carry target_year 9-10, a 25 minute limit and word counts up to 500. A Year 6 candidate
cannot write 500 words in 25 minutes, and a prompt written for Year 10 asks for reading
and reference a Year 6 writer has not met.

`names_its_form` — an email prompt that never says "email" leaves the candidate guessing
at the text type, which is precisely what the eight NSW forms are testing. The task
instruction must name its own form.

`has_a_stimulus` — the schema allows a null stimulus, but a bare instruction gives the
candidate nothing to react to and every script comes back the same shape.

`unknown_words` is reused from question_checks purely as a typo screen: these prompts are
read by a Year 6 candidate under time pressure and a misspelling costs them seconds.
"""
import argparse
import collections
import json
import pathlib
import re
import sqlite3
import sys
from difflib import SequenceMatcher

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.question_checks import unknown_words  # noqa: E402

GEN = ROOT / "run_data/output/writing/generated"
DB = ROOT / "run_data/db/qbank.db"
BOOK = "wr_nsw_selective"

PROMPT_TYPES = {"narrative", "persuasive", "article", "diary",
                "email", "speech", "advice_sheet", "news_report"}
STIMULUS_TYPES = {"text", "image", "quote", "scenario", "data"}

# §1: sat in Year 6, one prompt, 30 minutes.
TARGET_YEAR = "5-6"
TIME_LIMIT = 30
MAX_WORDS = 350          # the most a Year 6 writer produces in 30 minutes, planning included
MIN_WORDS = 150

REQUIRED = ["id", "prompt_type", "school_type", "stimulus_type", "stimulus_content",
            "stimulus_image_desc", "task_instruction", "word_count_min", "word_count_max",
            "time_limit_minutes", "target_year", "difficulty", "topic", "marking_focus",
            "source_book", "review_status", "created_at"]

# A prompt set entirely in nowhere reads as translated-from-elsewhere; the brief asks for
# Australian context throughout. One marker anywhere in the stimulus or task is enough.
AU_MARKERS = re.compile(
    r"\b(australia|australian|nsw|new south wales|sydney|melbourne|brisbane|perth|"
    r"adelaide|hobart|darwin|canberra|newcastle|wollongong|bendigo|ballarat|geelong|"
    r"toowoomba|armidale|dubbo|tamworth|bathurst|katoomba|parramatta|blue mountains|"
    r"murray|murrumbidgee|hunter|riverina|outback|bushfires?|bushland|magpies?|"
    r"kookaburras?|platypus|wombats?|possums?|cockatoos?|ibis|galahs?|banksias?|"
    r"wattle|eucalypts?|gum trees?|koalas?|humpbacks?|"
    r"aboriginal|torres strait|first nations|alice springs|snowy mountains|wagga|"
    r"surf life saving|nippers|anzac|naidoc|clean up australia|landcare|wires|rspca|"
    r"ses|state emergency service|shire council|swimming carnival|year 7|"
    r"local council|shire|milo|footy|netball|cricket)\b", re.I)

WR_EXTRA = {"advice", "sheet", "wetland", "wetlands", "boardwalk", "revegetation",
            "canteen", "fundraiser", "fundraising", "assembly", "newsletter",
            "microplastic", "microplastics", "reusable", "screen", "screens",
            "smartphone", "smartphones", "principal", "committee", "council",
            "councillor", "reserve", "ranger", "rangers", "swooping", "swoop",
            "platypus", "wombat", "kookaburra", "eucalypt", "banksia", "milo",
            "nippers", "landcare", "naidoc", "anzac", "katoomba", "armidale",
            "wollongong", "parramatta", "murrumbidgee", "toowoomba", "bendigo",
            "email", "emails", "emailing", "timetable", "timetables",
            # real words the system wordlist simply does not carry
            "sustainability", "wellbeing", "bushland", "gazebo", "seedlings",
            "boardwalk", "footbridge", "statistician", "bilby",
            # invented Australian place names used in these prompts, listed so they are
            # a deliberate choice rather than something that slipped past a typo screen
            "bilby creek", "wattle",
            "interschool", "replanted", "fledge", "fledged", "dubbo", "rspca",
            "riverina", "kindergarten", "humpback", "koala", "koalas", "hectares",
            "bushfire", "bushfires", "skate", "skatepark"}


def blob(p):
    return " ".join(str(p.get(k) or "") for k in
                    ("stimulus_content", "stimulus_image_desc", "task_instruction", "topic"))


def validate(ps, nn):
    errs, seen = [], set()
    for i, p in enumerate(ps):
        tag = f"p[{i}] {p.get('prompt_type', '?')}"
        missing = [f for f in REQUIRED if f not in p]
        if missing:
            errs.append(f"{tag}: missing field(s) {missing}")
            continue
        if p["prompt_type"] not in PROMPT_TYPES:
            errs.append(f"{tag}: prompt_type must be one of the eight NSW forms")
        if p["school_type"] != "nsw_selective":
            errs.append(f"{tag}: school_type must be nsw_selective")
        if p["stimulus_type"] not in STIMULUS_TYPES:
            errs.append(f"{tag}: bad stimulus_type {p['stimulus_type']!r}")
        if p["difficulty"] not in ("medium", "hard"):
            errs.append(f"{tag}: bad difficulty {p['difficulty']!r}")
        if p["review_status"] != "pending":
            errs.append(f"{tag}: review_status must be pending")
        if p["source_book"] != BOOK:
            errs.append(f"{tag}: source_book must be {BOOK!r}")
        if p["id"] in seen:
            errs.append(f"{tag}: duplicate id")
        seen.add(p["id"])

        # calibration against §1
        if p["target_year"] != TARGET_YEAR:
            errs.append(f"{tag}: target_year is {p['target_year']!r}; NSW is sat in Year 6, "
                        f"so it must be {TARGET_YEAR!r}")
        if p["time_limit_minutes"] != TIME_LIMIT:
            errs.append(f"{tag}: time_limit_minutes is {p['time_limit_minutes']}; §1 gives "
                        f"the NSW writing task {TIME_LIMIT} minutes")
        lo, hi = p["word_count_min"], p["word_count_max"]
        if not (MIN_WORDS <= lo < hi <= MAX_WORDS):
            errs.append(f"{tag}: word range {lo}-{hi} is outside {MIN_WORDS}-{MAX_WORDS}, "
                        f"which is what a Year 6 writer produces in {TIME_LIMIT} minutes")

        # the task has to name its own form
        form = p["prompt_type"].replace("_", " ")
        if form.split()[0] not in p["task_instruction"].lower():
            errs.append(f"{tag}: the task instruction never says {form!r} — the candidate "
                        f"has to be told which of the eight forms to write")

        # and it has to give them something to react to
        if p["stimulus_type"] == "image":
            if not (p["stimulus_image_desc"] or "").strip():
                errs.append(f"{tag}: an image prompt needs stimulus_image_desc")
        elif len((p["stimulus_content"] or "").split()) < 25:
            errs.append(f"{tag}: stimulus is under 25 words — too thin to react to")

        try:
            mf = json.loads(p["marking_focus"])
            if not isinstance(mf, list) or not 3 <= len(mf) <= 5:
                errs.append(f"{tag}: marking_focus must be a list of 3 to 5 criteria")
        except (TypeError, ValueError):
            errs.append(f"{tag}: marking_focus must be a JSON array string")

        if not AU_MARKERS.search(blob(p)):
            errs.append(f"{tag}: no Australian marker anywhere in the stimulus or task")

        unk = unknown_words(blob(p), extra_ok=WR_EXTRA)
        if unk:
            errs.append(f"{tag}: unrecognised word(s) {sorted(unk)[:6]} — check for typos")
    return errs


def existing():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return [dict(r) for r in con.execute("SELECT * FROM writing_prompts")]


def near_duplicates(ps, threshold=0.72):
    """Two prompts that ask nearly the same thing waste one of only 21 slots."""
    prior = [(p["prompt_type"], p["task_instruction"]) for p in existing()]
    errs, batch = [], []
    for p in ps:
        low = p["task_instruction"].lower()
        for ptype, prev in batch + prior:
            r = SequenceMatcher(None, low, (prev or "").lower()).ratio()
            if r >= threshold:
                errs.append(f"{p['prompt_type']}: task {r:.3f} similar to an existing "
                            f"{ptype} prompt — {prev[:80]!r}")
                break
        batch.append((p["prompt_type"], p["task_instruction"]))
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("nn", type=int)
    ap.add_argument("--check-only", action="store_true")
    a = ap.parse_args()

    path = GEN / f"{BOOK}_p{a.nn}.json"
    ps = json.loads(path.read_text(encoding="utf-8"))

    errs = validate(ps, a.nn) + near_duplicates(ps)
    if errs:
        print(f"VALIDATION FAILED ({len(errs)}):")
        for e in errs:
            print("  -", e)
        sys.exit(1)

    have = collections.Counter(p["prompt_type"] for p in existing()
                               if p["school_type"] == "nsw_selective")
    add = collections.Counter(p["prompt_type"] for p in ps)
    print(f"OK {path.name}: {len(ps)} prompts")
    print(f"  stimulus types {dict(collections.Counter(p['stimulus_type'] for p in ps))}")
    total = 0
    for t in sorted(PROMPT_TYPES):
        n = have[t] + add[t]
        total += n
        print(f"    {t:14} {have[t]:2} + {add[t]:2} = {n:2}{'  <- none' if n == 0 else ''}")
    print(f"  NSW writing prompts after loading: {total}/21")


if __name__ == "__main__":
    main()
