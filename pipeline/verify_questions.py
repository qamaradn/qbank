"""
pipeline/verify_questions.py — Batch API question verifier and improver.

Strategy:
  - Sends stem + options ONLY to Sonnet (no answer, no explanation)
  - Sonnet independently derives correct answer, fixes options if needed,
    improves language, writes fresh explanation, returns confidence score
  - Always returns ALL questions improved (not just flagged ones)
  - Uses Batch API for 50% cost discount

Run order:
  VR  18 files  → Sonnet batch  ~$0.18
  SR  131 files → Sonnet batch  ~$1.30
  QR  111 files → test 10 first, then full run

Workflow:
  python -m pipeline.verify_questions --subject vr --submit
  python -m pipeline.verify_questions --subject vr --status
  python -m pipeline.verify_questions --subject vr --apply

QR test mode (10 files first):
  python -m pipeline.verify_questions --subject qr --submit --limit 10
  python -m pipeline.verify_questions --subject qr --apply
  # if happy, run the rest:
  python -m pipeline.verify_questions --subject qr --submit
"""
import argparse
import json
import logging
import os
import re
import sqlite3
import time
from pathlib import Path

import anthropic

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

HAIKU_MODEL  = "claude-haiku-4-5-20251001"
SONNET_MODEL = "claude-sonnet-4-6"

_OUTPUT    = os.environ.get("OUTPUT_DIR", "run_data/output")
_DB        = os.environ.get("DB_PATH",    "run_data/db/qbank.db")
_STATE_DIR = os.environ.get("STATE_DIR",  "run_data")

SUBJECT_ALIASES = {
    "qr": "quantitative_reasoning",
    "vr": "verbal_reasoning",
    "lr": "logical_reasoning",
    "sr": "science_reasoning",
    "rc": "reading_comprehension",
}

SUBJECT_LABELS = {
    "quantitative_reasoning": "Quantitative Reasoning — maths, arithmetic, algebra, number patterns",
    "verbal_reasoning":       "Verbal Reasoning — analogies, word codes, sequences, odd-one-out, hidden words, synonyms, antonyms",
    "logical_reasoning":      "Logical Reasoning — deductive reasoning, patterns, syllogisms, spatial reasoning, abstract thinking",
    "science_reasoning":      "Science Reasoning — passage-based experiment analysis, data interpretation",
    "reading_comprehension":  "Reading Comprehension — passage-based, inference, vocabulary, main idea",
}

SUBJECT_SYSTEM = {
    "quantitative_reasoning": (
        "You are an expert mathematics teacher and exam question writer for Australian selective schools. "
        "You have deep knowledge of arithmetic, algebra, number patterns, ratios, and problem solving at Year 9-10 level. "
        "Always show clear logical reasoning when deriving answers."
    ),
    "verbal_reasoning": (
        "You are an expert verbal reasoning exam question writer for Australian selective schools. "
        "You have deep knowledge of word codes, analogies, sequences, hidden words, odd-one-out, "
        "synonyms, antonyms, and all standard verbal reasoning question types at Year 9-10 level."
    ),
    "logical_reasoning": (
        "You are an expert logical reasoning exam question writer for Australian selective schools. "
        "You have deep knowledge of deductive reasoning, syllogisms, pattern recognition, "
        "spatial reasoning, and abstract thinking at Year 9-10 level. "
        "Always verify that the correct answer follows necessarily from the given premises."
    ),
    "science_reasoning": (
        "You are an expert science teacher and exam question writer for Australian selective schools. "
        "You specialise in passage-based science questions involving experiment design, data interpretation, "
        "and scientific reasoning at Year 9-10 level. "
        "The passage provided IS the source of truth — all answers must be derivable from it."
    ),
    "reading_comprehension": (
        "You are an expert English teacher and exam question writer for Australian selective schools. "
        "You specialise in passage-based comprehension questions covering inference, vocabulary in context, "
        "main idea, author purpose, and text structure at Year 9-10 level. "
        "The passage provided IS the source of truth — all answers must be derivable from it."
    ),
}

# Only send stem + options + topic/difficulty — Sonnet derives the answer independently
_SEND_FIELDS = {"stem", "option_a", "option_b", "option_c", "option_d", "topic", "difficulty"}

_USER_PROMPT = """\
You are given {n} exam questions. For EACH question you must:

1. SOLVE — work out the correct answer yourself from the stem and options alone.
   Do not assume any option is correct. Derive the answer independently.

2. FIX OPTIONS — if no option matches the correct answer, replace the weakest
   distractor with the correct answer. Ensure exactly one option is correct.

3. IMPROVE LANGUAGE — rewrite the stem and options to be clear, precise, and
   natural for Year 9-10 students. Fix awkward phrasing, ambiguous wording,
   poor grammar, or unnatural English. Keep the same question type and skill.

4. WRITE EXPLANATION — write a fresh 1-2 sentence explanation of why the correct
   answer is right. Do not recycle the original — write from scratch.

5. CONFIDENCE — rate 0.0-1.0 how confident you are the question is correct
   and well-written after your improvements.

Rules:
- correct_answer must be exactly "A", "B", "C", or "D"
- difficulty must be "medium" or "hard"
- Australian context is welcome but never forced
- Keep the same topic/skill type as the original question

Return ALL {n} questions. Valid JSON only, no markdown fences:
{{
  "questions": [
    {{
      "stem": "improved stem",
      "option_a": "...",
      "option_b": "...",
      "option_c": "...",
      "option_d": "...",
      "correct_answer": "B",
      "explanation": "fresh explanation written from scratch",
      "confidence": 0.95,
      "difficulty": "medium"
    }}
  ]
}}

Return exactly {n} items in the same order as the input.{passage_section}

Questions to improve (stem + options only — you derive the answer):
{questions_json}
"""

_PASSAGE_SECTION = """

IMPORTANT — passage is provided below. All question answers must be derivable
from this passage. Do not invent information not present in the passage.

Passage:
{passage}
"""


# ── helpers ───────────────────────────────────────────────────────────────────

def _extract_json(text: str) -> str:
    """Strip markdown fences and extract the first complete JSON object."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()
    start = text.find("{")
    if start == -1:
        return text
    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start: i + 1]
    return text[start:]


def _state_path(subject: str) -> Path:
    return Path(_STATE_DIR) / f"verify_{subject}_state.json"


def _load_state(subject: str) -> dict:
    p = _state_path(subject)
    return json.loads(p.read_text()) if p.exists() else {}


def _save_state(subject: str, state: dict):
    _state_path(subject).write_text(json.dumps(state, indent=2))


def _verified_marker(json_path: Path) -> Path:
    return json_path.with_suffix(".verified")


def _pending_files(subject: str, limit: int = None) -> list[Path]:
    gen_dir = Path(_OUTPUT) / subject / "generated"
    files = sorted(f for f in gen_dir.glob("*.json")
                   if not _verified_marker(f).exists())
    return files[:limit] if limit else files


def _load_questions(json_path: Path) -> list:
    data = json.loads(json_path.read_text())
    return data if isinstance(data, list) else data.get("questions", [])


def _build_request(custom_id: str, subject: str, questions: list, model: str) -> dict:
    system = SUBJECT_SYSTEM.get(subject, "You are an expert exam question editor.")

    # Strip everything except stem, options, topic, difficulty
    slim = [{k: v for k, v in q.items() if k in _SEND_FIELDS} for q in questions]

    # For passage-based subjects, include the shared passage once (from first question)
    passage = questions[0].get("passage") if questions else None
    if passage and subject in ("science_reasoning", "reading_comprehension"):
        passage_section = _PASSAGE_SECTION.format(passage=passage)
    else:
        passage_section = ""

    content = _USER_PROMPT.format(
        n=len(slim),
        passage_section=passage_section,
        questions_json=json.dumps(slim, indent=2, ensure_ascii=False),
    )

    return {
        "custom_id": custom_id,
        "params": {
            "model": model,
            "max_tokens": 8096,
            "system": SUBJECT_LABELS.get(subject, subject) + "\n\n" + system,
            "messages": [{"role": "user", "content": content}],
        },
    }


# ── apply improvements ────────────────────────────────────────────────────────

# Fields Sonnet may rewrite
_EDITABLE = {"stem", "option_a", "option_b", "option_c", "option_d",
             "correct_answer", "explanation", "difficulty"}

def _apply_improvements(json_path: Path, improved_questions: list, db_path: str) -> int:
    """
    Write Sonnet's improved questions back to JSON file and DB.
    DB-identity fields (id, subject, source_book, etc.) always preserved from original.
    confidence updated from Sonnet's rating.
    """
    originals = _load_questions(json_path)
    updated   = 0

    conn = sqlite3.connect(db_path)
    for idx, improved_q in enumerate(improved_questions):
        if idx >= len(originals):
            break
        orig = originals[idx]

        # Merge editable fields from Sonnet, preserve DB fields
        for field in _EDITABLE:
            if field in improved_q:
                orig[field] = improved_q[field]

        # Update confidence from Sonnet's rating
        if "confidence" in improved_q:
            orig["confidence"] = improved_q["confidence"]

        # Update DB
        if "id" in orig:
            rows = conn.execute(
                """UPDATE questions SET
                     edited=1,
                     stem=?, option_a=?, option_b=?, option_c=?, option_d=?,
                     correct_answer=?, explanation=?, difficulty=?, confidence=?
                   WHERE id=?""",
                (orig["stem"], orig["option_a"], orig["option_b"],
                 orig["option_c"], orig["option_d"], orig["correct_answer"],
                 orig.get("explanation", ""), orig.get("difficulty", "medium"),
                 orig.get("confidence", 0.0), orig["id"]),
            ).rowcount
        else:
            rows = conn.execute(
                "UPDATE questions SET edited=1, correct_answer=?, explanation=?, confidence=? WHERE stem=?",
                (orig["correct_answer"], orig.get("explanation", ""),
                 orig.get("confidence", 0.0), orig["stem"]),
            ).rowcount

        logger.info(
            f"    q[{idx}] → {orig['correct_answer']} "
            f"conf={orig.get('confidence', '?')} | DB:{rows} | {orig['stem'][:55]}"
        )
        updated += 1

    conn.commit()
    conn.close()

    json_path.write_text(json.dumps(originals, indent=2, ensure_ascii=False))
    return updated


# ── commands ──────────────────────────────────────────────────────────────────

def cmd_submit(subject: str, model: str, limit: int = None):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("ERROR: ANTHROPIC_API_KEY not set.\nexport ANTHROPIC_API_KEY=sk-ant-...")

    files = _pending_files(subject, limit)
    if not files:
        logger.info(f"[{subject}] No pending files — all already verified.")
        return

    logger.info(f"[{subject}] Building batch: {len(files)} files, model={model}")

    requests = []
    file_map = {}

    for f in files:
        questions = _load_questions(f)
        if not questions:
            continue
        custom_id = f"{subject[:2]}_{f.stem}"
        requests.append(_build_request(custom_id, subject, questions, model))
        file_map[custom_id] = str(f)

    if not requests:
        logger.warning(f"[{subject}] All files empty — nothing to submit.")
        return

    client = anthropic.Anthropic(api_key=api_key)
    batch  = client.messages.batches.create(requests=requests)

    state = {
        "subject":      subject,
        "model":        model,
        "batch_id":     batch.id,
        "submitted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "file_count":   len(requests),
        "file_map":     file_map,
    }
    _save_state(subject, state)

    alias = next((k for k, v in SUBJECT_ALIASES.items() if v == subject), subject[:2])
    logger.info(f"[{subject}] Batch submitted!")
    logger.info(f"  batch_id  : {batch.id}")
    logger.info(f"  files     : {len(requests)}")
    logger.info(f"  model     : {model}")
    logger.info(f"  status    : {batch.processing_status}")
    logger.info(f"  Next step : python -m pipeline.verify_questions --subject {alias} --status")


def cmd_status(subject: str):
    state = _load_state(subject)
    if not state:
        logger.warning(f"[{subject}] No active batch — run --submit first.")
        return

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    batch  = client.messages.batches.retrieve(state["batch_id"])
    counts = batch.request_counts

    alias = next((k for k, v in SUBJECT_ALIASES.items() if v == subject), subject[:2])
    logger.info(f"[{subject}] Batch status")
    logger.info(f"  batch_id    : {batch.id}")
    logger.info(f"  status      : {batch.processing_status}")
    logger.info(f"  submitted   : {state.get('submitted_at')}")
    logger.info(f"  succeeded   : {counts.succeeded}")
    logger.info(f"  errored     : {counts.errored}")
    logger.info(f"  in_progress : {counts.processing}")
    if batch.processing_status == "ended":
        logger.info(f"  → Ready! Run: python -m pipeline.verify_questions --subject {alias} --apply")


def cmd_apply(subject: str):
    state = _load_state(subject)
    if not state:
        raise SystemExit(f"[{subject}] No batch state — run --submit first.")

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    batch  = client.messages.batches.retrieve(state["batch_id"])

    if batch.processing_status != "ended":
        raise SystemExit(f"[{subject}] Batch still {batch.processing_status} — check --status.")

    file_map = state["file_map"]
    stats    = {"succeeded": 0, "updated_files": 0, "updated_questions": 0, "errored": 0}

    logger.info(f"[{subject}] Applying batch results ({state['batch_id']})...")

    for result in client.messages.batches.results(state["batch_id"]):
        cid    = result.custom_id
        f_path = Path(file_map.get(cid, ""))

        if result.result.type != "succeeded":
            logger.error(f"  {cid}: {result.result.type} — skipping")
            stats["errored"] += 1
            continue

        stats["succeeded"] += 1
        raw = result.result.message.content[0].text

        try:
            parsed   = json.loads(_extract_json(raw))
            improved = parsed.get("questions", [])
            if not improved:
                raise ValueError("No 'questions' array in response")
        except Exception as e:
            logger.error(f"  {cid}: parse error — {e}")
            stats["errored"] += 1
            continue

        count = _apply_improvements(f_path, improved, _DB)
        logger.info(f"  {cid}: {count} questions improved")
        stats["updated_files"]     += 1
        stats["updated_questions"] += count

        _verified_marker(f_path).touch()

    logger.info(f"[{subject}] Apply complete: {stats}")
    _state_path(subject).unlink(missing_ok=True)
    logger.info(f"[{subject}] State cleared. Done.")


# ── CLI ───────────────────────────────────────────────────────────────────────

def _cli():
    parser = argparse.ArgumentParser(
        description="Verify and improve MCQ questions via Claude Sonnet Batch API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m pipeline.verify_questions --subject vr --submit
  python -m pipeline.verify_questions --subject vr --status
  python -m pipeline.verify_questions --subject vr --apply

  # QR — test 10 files first, review, then run the rest
  python -m pipeline.verify_questions --subject qr --submit --limit 10
  python -m pipeline.verify_questions --subject qr --apply
  python -m pipeline.verify_questions --subject qr --submit
        """,
    )
    parser.add_argument("--subject", required=True, help="vr, sr, qr, rc")
    parser.add_argument("--submit",  action="store_true")
    parser.add_argument("--status",  action="store_true")
    parser.add_argument("--apply",   action="store_true")
    parser.add_argument("--limit",   type=int, default=None,
                        help="Submit only first N files (test mode)")
    parser.add_argument("--model",   default="sonnet", choices=["haiku", "sonnet"],
                        help="Model (default: sonnet)")

    args    = parser.parse_args()
    subject = SUBJECT_ALIASES.get(args.subject, args.subject)
    model   = HAIKU_MODEL if args.model == "haiku" else SONNET_MODEL

    if not (args.submit or args.status or args.apply):
        parser.error("Specify one of: --submit, --status, --apply")

    if args.submit:
        cmd_submit(subject, model, limit=args.limit)
    if args.status:
        cmd_status(subject)
    if args.apply:
        cmd_apply(subject)


if __name__ == "__main__":
    _cli()
