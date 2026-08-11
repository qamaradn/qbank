#!/usr/bin/env python3
"""Finalise one writing-prompt batch, NSW or VIC.

Usage:  env -u PYTHONPATH .venv/bin/python3.11 -m tools.wr_finalise <NN> [--check-only]
        WR_BOOK=wr_vic_acer env -u PYTHONPATH .venv/bin/python3.11 -m tools.wr_finalise <NN>

WR_BOOK selects the calibration profile, the way MA_BOOK does for maths. The two exams are
nothing like each other and a prompt written for one is wrong for the other:

    NSW   one task,  30 minutes, sat in Year 6, eight named text types
    VIC   TWO tasks, 40 minutes total (~20 each), sat in Year 8, creative + persuasive

The VIC shape was confirmed against ACER's own preparation page on 2026-08-12: "The
writing test consists of two tasks", 40 minutes, inside a 2h35m paper. Three secondary
sources agree the two are completed (roughly 20 minutes each) rather than chosen between;
one prep site describes choosing one of two, which is the minority reading and is recorded
in vic_content_taxonomy_TASK.md §6 rather than followed. Twenty minutes is why VIC prompts
cap at 280 words while the ten already in the table ask for up to 500 in a 30-minute task
they will never be given.

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
import os
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

STIMULUS_TYPES = {"text", "image", "quote", "scenario", "data"}

PROFILES = {
    "wr_nsw_selective": {
        "school_type": "nsw_selective",
        "prompt_types": {"narrative", "persuasive", "article", "diary",
                         "email", "speech", "advice_sheet", "news_report"},
        "target_year": "5-6",
        "exam": "NSW: one prompt, 30 minutes, sat in Year 6",
        "bands": {"only": (150, 350, 30)},
        "target": 21,
    },
    "wr_vic_acer": {
        "school_type": "victorian_selective",
        # The VIC paper sets one creative task and one persuasive/analytical task. Keeping
        # the two slots to `narrative` and `persuasive` makes a matched pair unambiguous
        # when forms are dealt; the ten legacy VIC rows also use article/speech/diary,
        # which sit inside those two slots rather than beside them.
        "prompt_types": {"narrative", "persuasive"},
        "target_year": "7-8",
        # The paper's two tasks are NOT the same size: a short piece of about 150 words
        # and an extended one of about 250, 40 minutes across both. A prompt must sit in
        # one band or the other -- a range would let them drift back to a uniform middle,
        # which is what the first 44 did and what a drill cannot practise. Each band is
        # (min_words, max_words, minutes).
        "bands": {"short": (130, 170, 15), "extended": (220, 290, 25)},
        "exam": "VIC: two tasks in 40 minutes — a short one and an extended one, Year 8",
        # 18 mock forms x 2 tasks = 36, inflated 1.5x so forms can be assembled by
        # selection rather than by exhausting the pool (taxonomy §6).
        "target": 54,
    },
}

BOOK = os.environ.get("WR_BOOK", "wr_nsw_selective")
if BOOK not in PROFILES:
    raise SystemExit(f"WR_BOOK={BOOK!r} is not one of {sorted(PROFILES)}")
_P = PROFILES[BOOK]
SCHOOL_TYPE = _P["school_type"]
PROMPT_TYPES = _P["prompt_types"]
TARGET_YEAR = _P["target_year"]
BANDS = _P["bands"]
EXAM = _P["exam"]
TARGET = _P["target"]

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
    # Victorian places, added when WR_BOOK gained a VIC profile — the list above is NSW
    # by history, and a VIC prompt set in Footscray was failing the Australian-context
    # check for being too Australian in the wrong state.
    r"victoria|victorian|wimmera|gippsland|mornington|dandenong|footscray|preston|"
    r"castlemaine|port fairy|warrnambool|shepparton|mildura|yarra|grampians|otway|"
    r"phillip island|st kilda|brunswick|werribee|sunbury|echuca|torquay|lorne|"
    r"healesville|macedon|bellarine|bacchus marsh|colac|horsham|traralgon|"
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
            # VIC place names and Australian usages the system wordlist lacks
            "wimmera", "footscray", "castlemaine", "dandenong", "gippsland",
            "warrnambool", "shepparton", "mildura", "grampians", "otway",
            "bellarine", "traralgon", "healesville", "werribee", "echuca", "horsham",
            "geelong", "ballarat", "bendigo", "melbourne", "laminated",
            "sebastopol", "gumboot", "gumboots", "keyring", "dairy",
            "tue", "thu", "mon", "wed", "fri", "torquay", "lorne",
            "shortlisted", "netball", "bequest", "app", "turnout",
            "textas", "reconnection", "northerly", "swooping", "butcher's",
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
            errs.append(f"{tag}: prompt_type must be one of {sorted(PROMPT_TYPES)}")
        if p["school_type"] != SCHOOL_TYPE:
            errs.append(f"{tag}: school_type must be {SCHOOL_TYPE}")
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
            errs.append(f"{tag}: target_year is {p['target_year']!r}; {EXAM}, "
                        f"so it must be {TARGET_YEAR!r}")
        # A prompt must land exactly on one of the exam's task shapes. Anything between
        # them is a task the paper never sets and a drill cannot rehearse.
        shape = (p["word_count_min"], p["word_count_max"], p["time_limit_minutes"])
        if shape not in set(BANDS.values()):
            wanted = "; ".join(f"{name} {lo}-{hi} words in {mins} min"
                               for name, (lo, hi, mins) in BANDS.items())
            errs.append(f"{tag}: {shape[0]}-{shape[1]} words in {shape[2]} min matches no "
                        f"band. {EXAM}, so a prompt must be one of: {wanted}")

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
    """Two prompts that ask nearly the same thing waste one of a small number of slots.

    The batch's own rows are excluded from the comparison. Without that, re-running
    --check-only on a batch that has already been loaded reports every prompt as a 1.000
    match against itself, which buries any real finding underneath it.
    """
    mine = {p["id"] for p in ps}
    prior = [(p["prompt_type"], p["task_instruction"]) for p in existing()
             if p["id"] not in mine]
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
                               if p["school_type"] == SCHOOL_TYPE)
    add = collections.Counter(p["prompt_type"] for p in ps)
    print(f"OK {path.name}: {len(ps)} prompts")
    print(f"  stimulus types {dict(collections.Counter(p['stimulus_type'] for p in ps))}")
    total = 0
    for t in sorted(set(PROMPT_TYPES) | set(have) | set(add)):
        n = have[t] + add[t]
        total += n
        legacy = "" if t in PROMPT_TYPES else "  <- legacy form, counts to its slot"
        print(f"    {t:14} {have[t]:2} + {add[t]:2} = {n:2}"
              f"{'  <- none' if n == 0 else legacy}")
    print(f"  {SCHOOL_TYPE} prompts after loading: {total}/{TARGET}")


if __name__ == "__main__":
    main()
