#!/usr/bin/env python3
"""Load one finalised batch JSON into the DB, for any subject.

    env -u PYTHONPATH .venv/bin/python3.11 -m tools.load_batch <batch.json> [--book ID]

Generalised from the LR build's lr_load_one.py. Stages the single file in a temporary
tree so pipeline.phase4_load.load_book sees only this batch, then records the batch in a
<book>_LOADED.json beside it so a re-run cannot double-insert.

Phase 4 drops near-duplicate stems at 0.85 SILENTLY — it logs and moves on. A batch that
half-vanishes therefore looks like success. This refuses to record the batch as loaded if
anything was dropped or failed, so the discrepancy cannot pass unnoticed.
"""
import argparse
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipeline.phase4_load import load_book  # noqa: E402


def refuse_unbalanced(path):
    """Refuse a batch whose answer keys are degenerate.

    Builders emit every row with correct_answer 'A' and rely on the subject finaliser to
    deal the letters out evenly. If the finaliser is skipped -- or fails validation and
    the file is loaded anyway -- the batch arrives with one letter throughout, and
    answering that letter scores 100% on it. This happened to vr_vic_acer_p19: thirty
    rows loaded as all-A because a shell `&&` checked the exit status of `head`, not of
    the finaliser.
    """
    import collections
    import json as _json
    path = Path(path)
    qs = _json.loads(path.read_text(encoding="utf-8"))
    keys = collections.Counter(q.get("correct_answer") for q in qs)
    if len(qs) >= 4 and len(keys) < 2:
        raise SystemExit(
            f"REFUSING {path.name}: all {len(qs)} rows have "
            f"correct_answer {next(iter(keys))!r}. The finaliser has not rebalanced this "
            f"batch -- run it and confirm it prints OK before loading.")
    return keys


def main() -> None:
    ap = argparse.ArgumentParser(description="Load one finalised batch into the DB")
    ap.add_argument("batch", help="path to the finalised batch JSON")
    ap.add_argument("--book", default="", help="source_book id (default: read from the file)")
    ap.add_argument("--db", default=os.environ.get("DB_PATH", "run_data/db/qbank.db"))
    args = ap.parse_args()

    src = Path(args.batch).resolve()
    if not src.exists():
        sys.exit(f"missing {src}")
    qs = json.loads(src.read_text(encoding="utf-8"))
    if not qs:
        sys.exit(f"{src} is empty")
    refuse_unbalanced(src)

    book = args.book or qs[0]["source_book"]
    subject = qs[0]["subject"]
    loaded_file = src.parent / f"{book}_LOADED.json"
    already = json.loads(loaded_file.read_text()) if loaded_file.exists() else []
    if src.name in already:
        sys.exit(f"{src.name} is already recorded in {loaded_file.name}")

    with tempfile.TemporaryDirectory() as tmp:
        staged = Path(tmp) / subject / "generated"
        staged.mkdir(parents=True)
        shutil.copy(src, staged / src.name)
        stats = load_book(book, output_dir=tmp, db_path=args.db)

    print(f"{src.name}: {stats}  (expected {len(qs)} inserted)")
    if stats["failed"] or stats["duplicate"] or stats["inserted"] != len(qs):
        sys.exit(f"NOT recorded as loaded — {stats['failed']} failed, "
                 f"{stats['duplicate']} dropped as duplicates. Investigate before retrying.")

    loaded_file.write_text(json.dumps(sorted(already + [src.name]), indent=1))
    print(f"recorded in {loaded_file.name}")


if __name__ == "__main__":
    main()
