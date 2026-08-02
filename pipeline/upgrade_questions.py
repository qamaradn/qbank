"""
pipeline/upgrade_questions.py — Use Claude Opus to review and upgrade 90–95% confidence
verbal_reasoning and quantitative_reasoning questions.

Usage:
    python -m pipeline.upgrade_questions --dry-run          # show counts only, no API calls
    python -m pipeline.upgrade_questions                    # run (batches of 20, auto-resume)
    python -m pipeline.upgrade_questions --batch 10         # smaller batches
    python -m pipeline.upgrade_questions --subject verbal_reasoning  # one category only

Progress is saved after every batch — safe to Ctrl-C and resume.
Upgraded questions are written back into the original generated/*.json files in place.
"""

import argparse
import json
import logging
import os
import re
import sys
import time
from pathlib import Path

import anthropic

REPO_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = REPO_ROOT / "run_data" / "output"
TRACKING_FILE = REPO_ROOT / "run_data" / "db" / "upgraded_questions.json"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

CATEGORIES = ["verbal_reasoning", "quantitative_reasoning"]
DEFAULT_BATCH = 20
CONF_LOW = 0.90
CONF_HIGH = 0.95

NEEDS_IMAGE_RE = re.compile(
    r"(refer to the|shown (below|above) in the (diagram|figure|chart|graph|table)|"
    r"the (chart|graph|table) (below|above|shows)|based on the (chart|graph|table))",
    re.IGNORECASE,
)

UPGRADE_PROMPT = """\
You are a senior Australian selective school exam question writer.
Review this {category} question for Year 7–9 selective entry (students aged 11–14).

Check and fix if needed:
1. Stem is clear and unambiguous
2. Correct answer is definitively correct
3. All wrong options are plausible but clearly wrong
4. Explanation fully justifies the correct answer and rules out distractors

Return ONLY valid JSON — no markdown fences, no commentary:
{{
  "stem": "...",
  "option_a": "...",
  "option_b": "...",
  "option_c": "...",
  "option_d": "...",
  "correct_answer": "A",
  "explanation": "...",
  "confidence": 0.97,
  "changes": "brief note on what changed, or 'none' if unchanged"
}}

QUESTION:
Category: {category}
Difficulty: {difficulty}
Topic: {topic}

Stem: {stem}

A) {option_a}
B) {option_b}
C) {option_c}
D) {option_d}

Correct answer: {correct_answer}
Explanation: {explanation}
"""


def load_env() -> None:
    env_path = REPO_ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def load_tracking() -> set:
    if TRACKING_FILE.exists():
        data = json.loads(TRACKING_FILE.read_text())
        return set(data.get("upgraded_keys", []))
    return set()


def save_tracking(keys: set) -> None:
    TRACKING_FILE.parent.mkdir(parents=True, exist_ok=True)
    TRACKING_FILE.write_text(json.dumps({"upgraded_keys": sorted(keys)}, indent=2))


def question_key(source_file: Path, q_num: int) -> str:
    return f"{source_file.name}::{q_num}"


def collect_eligible(categories: list[str]) -> list[dict]:
    """Return all 90–95% conf questions (no image dependency) with source metadata."""
    eligible = []
    for cat in categories:
        gen_dir = OUTPUT_DIR / cat / "generated"
        if not gen_dir.exists():
            logger.warning(f"No generated dir for {cat}")
            continue
        for f in sorted(gen_dir.glob("*.json")):
            try:
                qs = json.loads(f.read_text())
                if not isinstance(qs, list):
                    continue
                for q in qs:
                    conf = q.get("confidence")
                    if conf is None:
                        continue
                    if not (CONF_LOW <= float(conf) < CONF_HIGH):
                        continue
                    stem = q.get("stem", "")
                    if NEEDS_IMAGE_RE.search(stem):
                        continue
                    eligible.append({
                        "source_file": f,
                        "category": cat,
                        "question": q,
                    })
            except Exception as e:
                logger.warning(f"Failed to read {f}: {e}")
    return eligible


def call_opus(client: anthropic.Anthropic, cat: str, q: dict) -> dict | None:
    prompt = UPGRADE_PROMPT.format(
        category=cat.replace("_", " "),
        difficulty=q.get("difficulty", "medium"),
        topic=q.get("topic", ""),
        stem=q.get("stem", ""),
        option_a=q.get("option_a", ""),
        option_b=q.get("option_b", ""),
        option_c=q.get("option_c", ""),
        option_d=q.get("option_d", ""),
        correct_answer=q.get("correct_answer", ""),
        explanation=q.get("explanation", ""),
    )
    try:
        msg = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        text = msg.content[0].text.strip()
        # Strip markdown fences if Opus wraps anyway
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.warning(f"JSON parse failed: {e}")
        return None
    except anthropic.APIError as e:
        logger.error(f"API error: {e}")
        return None


def merge_upgraded(original: dict, opus_result: dict) -> dict:
    """Return original dict with Opus-corrected fields merged in."""
    updated = dict(original)
    for field in ("stem", "option_a", "option_b", "option_c", "option_d",
                  "correct_answer", "explanation", "confidence"):
        if field in opus_result:
            updated[field] = opus_result[field]
    updated["upgrade_changes"] = opus_result.get("changes", "")
    return updated


def save_upgraded_file(source_file: Path, upgrades: dict[int, dict]) -> None:
    """Overwrite source file in place, merging Opus-upgraded questions back in."""
    originals = json.loads(source_file.read_text())
    if not isinstance(originals, list):
        return

    merged = []
    for q in originals:
        q_num = q.get("question_number")
        if q_num in upgrades:
            merged.append(upgrades[q_num])
        else:
            merged.append(q)

    source_file.write_text(json.dumps(merged, indent=2, ensure_ascii=False))


def run(args: argparse.Namespace) -> None:
    load_env()

    categories = [args.subject] if args.subject else CATEGORIES
    eligible = collect_eligible(categories)

    logger.info(f"Eligible questions (90–95%, no image): {len(eligible)}")
    for cat in categories:
        count = sum(1 for e in eligible if e["category"] == cat)
        logger.info(f"  {cat}: {count}")

    if args.dry_run:
        logger.info("DRY RUN — no API calls.")
        return

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        logger.error("ANTHROPIC_API_KEY not set")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    done_keys = load_tracking()

    todo = [e for e in eligible if question_key(e["source_file"], e["question"].get("question_number")) not in done_keys]
    logger.info(f"Already upgraded: {len(eligible) - len(todo)}  |  To do: {len(todo)}")

    if not todo:
        logger.info("All eligible questions already upgraded.")
        return

    # Group pending upgrades by source file so we can write one file per batch chunk
    batch_size = args.batch
    total = len(todo)
    processed = 0
    failed = 0

    # Accumulate per-file upgrades; flush to disk after each batch
    file_upgrades: dict[Path, dict[int, dict]] = {}

    for i, entry in enumerate(todo):
        src = entry["source_file"]
        cat = entry["category"]
        q = entry["question"]
        q_num = q.get("question_number")
        key = question_key(src, q_num)

        result = call_opus(client, cat, q)
        if result:
            upgraded_q = merge_upgraded(q, result)
            file_upgrades.setdefault(src, {})[q_num] = upgraded_q
            done_keys.add(key)
            processed += 1
            conf_before = q.get("confidence", "?")
            conf_after = result.get("confidence", "?")
            changes = result.get("changes", "")
            logger.info(f"[{i+1}/{total}] {cat} Q{q_num} {conf_before:.2f}→{conf_after:.2f} | {changes[:60]}")
        else:
            failed += 1
            logger.warning(f"[{i+1}/{total}] {cat} Q{q_num} — FAILED, keeping original")

        # Flush after every batch
        if (i + 1) % batch_size == 0 or (i + 1) == total:
            for f_path, upgrades in file_upgrades.items():
                save_upgraded_file(f_path, upgrades)
            file_upgrades.clear()
            save_tracking(done_keys)
            logger.info(f"── Batch saved. Progress: {processed} upgraded, {failed} failed ──")
            if (i + 1) < total:
                time.sleep(1)  # brief pause between batches

    logger.info(f"Done. Upgraded: {processed}  Failed: {failed}")
    logger.info(f"Originals updated in place under {OUTPUT_DIR}/<category>/generated/")


def main() -> None:
    parser = argparse.ArgumentParser(description="Upgrade 90–95% confidence questions using Claude Opus")
    parser.add_argument("--subject", choices=CATEGORIES, help="Process one category only")
    parser.add_argument("--batch", type=int, default=DEFAULT_BATCH, help="Save/checkpoint every N questions (default 20)")
    parser.add_argument("--dry-run", action="store_true", help="Show counts only, no API calls")
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
