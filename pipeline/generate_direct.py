"""
pipeline/generate_direct.py — Generate MCQ questions directly from a prompt using Claude Batch API.

Generates questions in batches of 10. For 100 questions, submits 10 requests in
one Batch API call (50% cost discount vs standard API).

Workflow:
  python -m pipeline.generate_direct --subject vr --count 100 --submit
  python -m pipeline.generate_direct --subject vr --status
  python -m pipeline.generate_direct --subject vr --apply          # saves JSON only
  python -m pipeline.generate_direct --subject vr --apply --load   # saves + loads into DB

Default prompt files (pipeline/prompts/):
  vr → vr_generate.txt

Cost estimate (Sonnet, Batch API 50% discount):
  100 questions (10 requests) → ~$0.18
  500 questions (50 requests) → ~$0.90
"""
import argparse
import json
import logging
import os
import re
import time
import uuid
from pathlib import Path

import base64

import anthropic

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

SONNET_MODEL       = "claude-sonnet-4-6"
QUESTIONS_PER_BATCH = 10

_OUTPUT    = os.environ.get("OUTPUT_DIR", "run_data/output")
_DB        = os.environ.get("DB_PATH",    "run_data/db/qbank.db")
_STATE_DIR = os.environ.get("STATE_DIR",  "run_data")
_SCRATCH   = os.environ.get("SCRATCH_DIR", "run_data/scratch")

SUBJECT_ALIASES = {
    "vr": "verbal_reasoning",
    "ma": "mathematics",
    "qr": "quantitative_reasoning",
    "lr": "logical_reasoning",
    "sr": "science_reasoning",
    "rc": "reading_comprehension",
}

_PROMPTS_DIR = Path(__file__).parent / "prompts"

DEFAULT_PROMPT_FILES = {
    "verbal_reasoning":    str(_PROMPTS_DIR / "vr_generate.txt"),
    "quantitative_reasoning": str(_PROMPTS_DIR / "qr_generate_png.txt"),
}

PNG_STATE_SUFFIX = "_png_state.json"


# ── helpers ───────────────────────────────────────────────────────────────────

def _extract_json_array(text: str) -> list:
    """Extract a JSON array from text, stripping markdown fences."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text.strip())
    text = text.strip()

    try:
        result = json.loads(text)
        if isinstance(result, list):
            return result
        if isinstance(result, dict) and "questions" in result:
            return result["questions"]
        return result
    except json.JSONDecodeError:
        pass

    start = text.find("[")
    if start == -1:
        raise ValueError("No JSON array found in response")
    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return json.loads(text[start: i + 1])
    raise ValueError("Malformed JSON array in response")


def _state_path(subject: str) -> Path:
    return Path(_STATE_DIR) / f"generate_{subject}_state.json"


def _load_state(subject: str) -> dict:
    p = _state_path(subject)
    return json.loads(p.read_text()) if p.exists() else {}


def _save_state(subject: str, state: dict):
    _state_path(subject).write_text(json.dumps(state, indent=2))


def _output_path(subject: str, alias: str, page_index: int, datestamp: str) -> Path:
    # Named with _p prefix so phase4_load.load_book() can find them via glob
    return Path(_OUTPUT) / subject / "generated" / f"direct_{alias}_{datestamp}_p{page_index:02d}.json"


def _build_request(custom_id: str, prompt_text: str, batch_index: int, total_batches: int) -> dict:
    user_msg = (
        f"Generate batch {batch_index} of {total_batches}. "
        "Ensure this batch uses different vocabulary, analogy types, and question styles "
        "from all other batches — variety is essential. "
        "Return exactly 10 questions as a JSON array."
    )
    return {
        "custom_id": custom_id,
        "params": {
            "model": SONNET_MODEL,
            "max_tokens": 4096,
            "system": prompt_text,
            "messages": [{"role": "user", "content": user_msg}],
        },
    }


def _enrich_questions(questions: list, subject: str, source_book: str) -> list:
    """Add required DB fields to questions returned by Claude."""
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    enriched = []
    for q in questions:
        enriched.append({
            "id":                      str(uuid.uuid4()),
            "subject":                 subject,
            "stem":                    q.get("stem", ""),
            "option_a":                q.get("option_a", ""),
            "option_b":                q.get("option_b", ""),
            "option_c":                q.get("option_c", ""),
            "option_d":                q.get("option_d", ""),
            "correct_answer":          q.get("correct_answer", "A").upper() if q.get("correct_answer") else "A",
            "explanation":             q.get("explanation", ""),
            "topic":                   q.get("topic", q.get("category", "")),
            "difficulty":              q.get("difficulty", "medium") if q.get("difficulty") in ("medium", "hard") else "medium",
            "confidence":              float(q.get("confidence", 0.85)),
            "source_book":             source_book,
            "source_page":             None,
            "source_page_description": q.get("category", None),
            "passage":                 None,
            "figure_svg":              q.get("figure_svg") if q.get("has_figure") else None,
            "review_status":           "pending",
            "created_at":              now,
        })
    return enriched


# ── commands ──────────────────────────────────────────────────────────────────

def cmd_submit(subject: str, prompt_file: str, count: int):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("ERROR: ANTHROPIC_API_KEY not set.\nexport ANTHROPIC_API_KEY=sk-ant-...")

    prompt_path = Path(prompt_file)
    if not prompt_path.exists():
        raise SystemExit(f"ERROR: Prompt file not found: {prompt_file}")

    prompt_text = prompt_path.read_text(encoding="utf-8")
    n_batches   = (count + QUESTIONS_PER_BATCH - 1) // QUESTIONS_PER_BATCH
    datestamp   = time.strftime("%d%m%y")
    alias       = next((k for k, v in SUBJECT_ALIASES.items() if v == subject), subject[:2])
    source_book = f"direct_{alias}_{datestamp}"

    logger.info(f"[{subject}] Submitting {n_batches} requests × {QUESTIONS_PER_BATCH} = ~{n_batches * QUESTIONS_PER_BATCH} questions")
    logger.info(f"[{subject}] Model: {SONNET_MODEL} | Batch API (50% discount)")

    requests  = []
    batch_map = {}

    for i in range(1, n_batches + 1):
        custom_id = f"gen_{alias}_{datestamp}_p{i:02d}"
        requests.append(_build_request(custom_id, prompt_text, i, n_batches))
        batch_map[custom_id] = str(_output_path(subject, alias, i, datestamp))

    client = anthropic.Anthropic(api_key=api_key)
    batch  = client.messages.batches.create(requests=requests)

    state = {
        "subject":      subject,
        "model":        SONNET_MODEL,
        "batch_id":     batch.id,
        "submitted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "n_batches":    n_batches,
        "count":        count,
        "source_book":  source_book,
        "datestamp":    datestamp,
        "batch_map":    batch_map,
    }
    _save_state(subject, state)

    alias = next((k for k, v in SUBJECT_ALIASES.items() if v == subject), subject[:2])
    logger.info(f"[{subject}] Batch submitted!")
    logger.info(f"  batch_id  : {batch.id}")
    logger.info(f"  requests  : {len(requests)}")
    logger.info(f"  source_book: {source_book}")
    logger.info(f"  Next step : python -m pipeline.generate_direct --subject {alias} --status")


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
        logger.info(f"  → Ready! Run: python -m pipeline.generate_direct --subject {alias} --apply")


def cmd_apply(subject: str, load_db: bool = False):
    state = _load_state(subject)
    if not state:
        raise SystemExit(f"[{subject}] No batch state — run --submit first.")

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    batch  = client.messages.batches.retrieve(state["batch_id"])

    if batch.processing_status != "ended":
        raise SystemExit(f"[{subject}] Batch still {batch.processing_status} — check --status first.")

    batch_map   = state["batch_map"]
    source_book = state["source_book"]
    stats = {"succeeded": 0, "failed": 0, "total_questions": 0}

    logger.info(f"[{subject}] Applying batch results ({state['batch_id']})...")

    for result in client.messages.batches.results(state["batch_id"]):
        cid    = result.custom_id
        f_path = Path(batch_map.get(cid, ""))

        if result.result.type != "succeeded":
            logger.error(f"  {cid}: {result.result.type} — skipping")
            stats["failed"] += 1
            continue

        raw = result.result.message.content[0].text

        try:
            questions = _extract_json_array(raw)
            if not questions:
                raise ValueError("Empty array returned")
        except Exception as e:
            logger.error(f"  {cid}: parse error — {e}")
            stats["failed"] += 1
            continue

        enriched = _enrich_questions(questions, subject, source_book)
        f_path.parent.mkdir(parents=True, exist_ok=True)
        f_path.write_text(json.dumps(enriched, indent=2, ensure_ascii=False))

        stats["succeeded"] += 1
        stats["total_questions"] += len(enriched)
        logger.info(f"  {cid}: {len(enriched)} questions → {f_path.name}")

    logger.info(f"[{subject}] Apply complete: {stats}")

    if load_db and stats["succeeded"] > 0:
        logger.info(f"[{subject}] Loading into DB (phase4)...")
        from pipeline.phase4_load import load_book
        db_stats = load_book(source_book, output_dir=_OUTPUT, db_path=_DB)
        logger.info(f"[{subject}] DB load: {db_stats}")

    _state_path(subject).unlink(missing_ok=True)
    logger.info(f"[{subject}] State cleared. Done.")


def cmd_ingest(subject: str, input_file: str):
    """
    Ingest a JSON file from an external LLM into the DB via dedup + phase4.

    The file must be a JSON array using the Claude output format:
      [{stem, option_a-d, correct_answer, explanation, topic, difficulty, confidence, ...}, ...]

    Drop files into run_data/output/<subject>/external/ then run:
      python -m pipeline.generate_direct --subject vr --ingest myfile.json
      python -m pipeline.generate_direct --subject vr --ingest-all   (all files in external/)
    """
    # Resolve relative paths against subject's external folder
    src = Path(input_file)
    if not src.is_absolute() and not src.exists():
        src = Path(_OUTPUT) / subject / "external" / src.name
    if not src.exists():
        raise SystemExit(f"ERROR: File not found: {input_file}")

    try:
        raw = json.loads(src.read_text(encoding="utf-8"))
        if isinstance(raw, list):
            questions = raw
        elif isinstance(raw, dict):
            questions = raw.get("questions", [])
        else:
            questions = []
        if not questions:
            raise ValueError("No questions found")
    except Exception as e:
        raise SystemExit(f"ERROR: Could not parse {input_file}: {e}")

    datestamp   = time.strftime("%d%m%y")
    alias       = next((k for k, v in SUBJECT_ALIASES.items() if v == subject), subject[:2])
    source_book = f"external_{alias}_{datestamp}"
    enriched    = _enrich_questions(questions, subject, source_book)

    # Save enriched file with _p naming so phase4 glob ({source_book}_p*.json) finds it
    out_dir = Path(_OUTPUT) / subject / "generated"
    out_dir.mkdir(parents=True, exist_ok=True)
    existing = list(out_dir.glob(f"external_{alias}_{datestamp}_p*.json"))
    page_num = len(existing) + 1
    out_file = out_dir / f"external_{alias}_{datestamp}_p{page_num:02d}.json"
    out_file.write_text(json.dumps(enriched, indent=2, ensure_ascii=False))
    logger.info(f"[{subject}] {len(enriched)} questions enriched → {out_file.name}")

    # Run dedup + DB load
    from pipeline.phase4_load import load_book
    db_stats = load_book(source_book, output_dir=_OUTPUT, db_path=_DB)
    logger.info(f"[{subject}] DB load: {db_stats}")


def _png_state_path(subject: str) -> Path:
    return Path(_STATE_DIR) / f"generate_{subject}{PNG_STATE_SUFFIX}"


def cmd_submit_png(subject: str, prompt_file: str, book_id: str = None, limit: int = None):
    """Submit a batch of PNG pages to Claude Vision — one request per page, 10 questions each."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("ERROR: ANTHROPIC_API_KEY not set.")

    prompt_path = Path(prompt_file)
    if not prompt_path.exists():
        raise SystemExit(f"ERROR: Prompt file not found: {prompt_file}")
    prompt_text = prompt_path.read_text(encoding="utf-8")

    # Find PNG files for this subject
    scratch_root = Path(_SCRATCH)
    pattern = f"*/images/{subject}/*.png"
    all_pngs = sorted(scratch_root.glob(pattern))

    if book_id:
        all_pngs = [p for p in all_pngs if book_id in p.parts]

    if not all_pngs:
        raise SystemExit(f"No PNGs found in {scratch_root}/{pattern}")

    # Skip already-processed pages (output JSON exists)
    alias      = next((k for k, v in SUBJECT_ALIASES.items() if v == subject), subject[:2])
    out_dir    = Path(_OUTPUT) / subject / "generated"
    to_process = []
    for png in all_pngs:
        # page marker: book_id + page number extracted from filename
        out_file = out_dir / f"png_{png.stem}.json"
        if out_file.exists():
            logger.info(f"  skip (done): {png.name}")
        else:
            to_process.append(png)

    if limit:
        to_process = to_process[:limit]

    if not to_process:
        logger.info(f"[{subject}] All pages already processed.")
        return

    logger.info(f"[{subject}] Submitting {len(to_process)} PNG pages via vision batch")
    logger.info(f"[{subject}] Model: {SONNET_MODEL} | Batch API (50% discount)")
    logger.info(f"[{subject}] Estimated cost: ~${len(to_process) * 0.044:.2f}")

    requests  = []
    batch_map = {}  # custom_id → output path

    for png in to_process:
        img_data   = base64.standard_b64encode(png.read_bytes()).decode("utf-8")
        custom_id  = f"png_{png.stem}"
        out_file   = str(out_dir / f"png_{png.stem}.json")
        batch_map[custom_id] = out_file

        requests.append({
            "custom_id": custom_id,
            "params": {
                "model": SONNET_MODEL,
                "max_tokens": 8192,
                "system": prompt_text,
                "messages": [{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": img_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": "Generate exactly 10 questions based on this page. Return a JSON array only.",
                        },
                    ],
                }],
            },
        })

    client = anthropic.Anthropic(api_key=api_key)
    batch  = client.messages.batches.create(requests=requests)

    state = {
        "subject":      subject,
        "model":        SONNET_MODEL,
        "batch_id":     batch.id,
        "submitted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "n_pages":      len(requests),
        "batch_map":    batch_map,
        "mode":         "png",
    }
    _png_state_path(subject).write_text(json.dumps(state, indent=2))

    logger.info(f"[{subject}] PNG batch submitted!")
    logger.info(f"  batch_id : {batch.id}")
    logger.info(f"  pages    : {len(requests)}")
    logger.info(f"  Next step: python -m pipeline.generate_direct --subject {alias} --status-png")


def cmd_status_png(subject: str):
    state_path = _png_state_path(subject)
    if not state_path.exists():
        logger.warning(f"[{subject}] No active PNG batch — run --submit-png first.")
        return

    state  = json.loads(state_path.read_text())
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    batch  = client.messages.batches.retrieve(state["batch_id"])
    counts = batch.request_counts

    alias = next((k for k, v in SUBJECT_ALIASES.items() if v == subject), subject[:2])
    logger.info(f"[{subject}] PNG batch status")
    logger.info(f"  batch_id    : {batch.id}")
    logger.info(f"  status      : {batch.processing_status}")
    logger.info(f"  submitted   : {state.get('submitted_at')}")
    logger.info(f"  succeeded   : {counts.succeeded}")
    logger.info(f"  errored     : {counts.errored}")
    logger.info(f"  in_progress : {counts.processing}")
    if batch.processing_status == "ended":
        logger.info(f"  → Ready! Run: python -m pipeline.generate_direct --subject {alias} --apply-png")


def cmd_apply_png(subject: str, load_db: bool = False):
    state_path = _png_state_path(subject)
    if not state_path.exists():
        raise SystemExit(f"[{subject}] No PNG batch state — run --submit-png first.")

    state  = json.loads(state_path.read_text())
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    batch  = client.messages.batches.retrieve(state["batch_id"])

    if batch.processing_status != "ended":
        raise SystemExit(f"[{subject}] Batch still {batch.processing_status} — check --status-png first.")

    batch_map   = state["batch_map"]
    stats       = {"succeeded": 0, "failed": 0, "total_questions": 0}
    saved_book_ids: set = set()

    logger.info(f"[{subject}] Applying PNG batch results ({state['batch_id']})...")

    for result in client.messages.batches.results(state["batch_id"]):
        cid    = result.custom_id
        f_path = Path(batch_map.get(cid, ""))

        if result.result.type != "succeeded":
            logger.error(f"  {cid}: {result.result.type} — skipping")
            stats["failed"] += 1
            continue

        raw = result.result.message.content[0].text

        try:
            questions = _extract_json_array(raw)
            if not questions:
                raise ValueError("Empty array")
        except Exception as e:
            logger.error(f"  {cid}: parse error — {e}")
            stats["failed"] += 1
            continue

        # Derive source_book from filename: strip _p<num> suffix
        # e.g. "png_act_test2_230526_p122" → "png_act_test2_230526"
        source_book = re.sub(r"_p\d+$", "", f_path.stem)
        saved_book_ids.add(source_book)

        enriched = _enrich_questions(questions, subject, source_book)
        f_path.parent.mkdir(parents=True, exist_ok=True)
        f_path.write_text(json.dumps(enriched, indent=2, ensure_ascii=False))

        stats["succeeded"] += 1
        stats["total_questions"] += len(enriched)
        logger.info(f"  {cid}: {len(enriched)} questions → {f_path.name}")

    logger.info(f"[{subject}] Apply complete: {stats}")

    if load_db and stats["succeeded"] > 0:
        logger.info(f"[{subject}] Loading into DB (phase4)...")
        from pipeline.phase4_load import load_book
        total_db: dict = {"inserted": 0, "duplicate": 0, "failed": 0}
        for bid in sorted(saved_book_ids):
            db_stats = load_book(bid, output_dir=_OUTPUT, db_path=_DB)
            logger.info(f"[{subject}] DB load ({bid}): {db_stats}")
            for k in total_db:
                total_db[k] += db_stats.get(k, 0)
        logger.info(f"[{subject}] DB total: {total_db}")

    state_path.unlink(missing_ok=True)
    logger.info(f"[{subject}] PNG state cleared. Done.")


def cmd_ingest_all(subject: str):
    """Ingest all JSON files from run_data/output/<subject>/external/ in one go."""
    external_dir = Path(_OUTPUT) / subject / "external"
    if not external_dir.exists():
        raise SystemExit(f"ERROR: External folder not found: {external_dir}\nCreate it and drop files there.")

    files = sorted(external_dir.glob("*.json"))
    if not files:
        raise SystemExit(f"No JSON files found in {external_dir}")

    logger.info(f"[{subject}] Ingesting {len(files)} file(s) from {external_dir}")
    for f in files:
        cmd_ingest(subject, str(f))


# ── CLI ───────────────────────────────────────────────────────────────────────

def _cli():
    parser = argparse.ArgumentParser(
        description="Generate MCQ questions from a prompt via Claude Batch API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # VR — 100 question test run
  python -m pipeline.generate_direct --subject vr --count 100 --submit
  python -m pipeline.generate_direct --subject vr --status
  python -m pipeline.generate_direct --subject vr --apply
  python -m pipeline.generate_direct --subject vr --apply --load

  # Ingest external LLM output (single file or all at once)
  python -m pipeline.generate_direct --subject vr --ingest myfile.json
  python -m pipeline.generate_direct --subject vr --ingest-all

  # PNG → Vision → questions with SVG figures
  python -m pipeline.generate_direct --subject qr --submit-png --book-id act_test2
  python -m pipeline.generate_direct --subject qr --status-png
  python -m pipeline.generate_direct --subject qr --apply-png --load
        """,
    )
    parser.add_argument("--subject",     required=True, help="vr, qr, sr, rc")
    parser.add_argument("--submit",      action="store_true")
    parser.add_argument("--status",      action="store_true")
    parser.add_argument("--apply",       action="store_true")
    parser.add_argument("--ingest",      default=None, metavar="FILE",
                        help="Ingest a single external LLM JSON file (looks in run_data/output/<subject>/external/ if not found)")
    parser.add_argument("--ingest-all",  action="store_true",
                        help="Ingest all JSON files from run_data/output/<subject>/external/")
    parser.add_argument("--count",       type=int, default=100,
                        help="Total questions to generate, must be multiple of 10 (default: 100)")
    parser.add_argument("--prompt-file", default=None,
                        help="Path to prompt text file (default: pipeline/prompts/<subject>.txt)")
    parser.add_argument("--load",        action="store_true",
                        help="After --apply/--apply-png: also load questions into DB via phase4")
    parser.add_argument("--submit-png",  action="store_true",
                        help="Submit PNG pages to Claude Vision batch (QR figure questions)")
    parser.add_argument("--status-png",  action="store_true",
                        help="Check status of active PNG vision batch")
    parser.add_argument("--apply-png",   action="store_true",
                        help="Apply PNG batch results — save JSON files")
    parser.add_argument("--book-id",     default=None,
                        help="Limit PNG submission to a specific book (e.g. act_test2)")

    args    = parser.parse_args()
    subject = SUBJECT_ALIASES.get(args.subject, args.subject)

    if not (args.submit or args.status or args.apply or args.ingest or args.ingest_all
            or args.submit_png or args.status_png or args.apply_png):
        parser.error("Specify at least one of: --submit, --status, --apply, --ingest, --ingest-all, --submit-png, --status-png, --apply-png")

    prompt_file = args.prompt_file or DEFAULT_PROMPT_FILES.get(subject)
    if args.submit and not prompt_file:
        parser.error(f"No default prompt file for '{subject}' — use --prompt-file")

    if args.submit:
        cmd_submit(subject, prompt_file, args.count)
    if args.status:
        cmd_status(subject)
    if args.apply:
        cmd_apply(subject, load_db=args.load)
    if args.ingest:
        cmd_ingest(subject, args.ingest)
    if args.ingest_all:
        cmd_ingest_all(subject)
    if args.submit_png:
        pf = args.prompt_file or DEFAULT_PROMPT_FILES.get(subject)
        if not pf:
            parser.error(f"No default PNG prompt for '{subject}' — use --prompt-file")
        cmd_submit_png(subject, pf, book_id=args.book_id)
    if args.status_png:
        cmd_status_png(subject)
    if args.apply_png:
        cmd_apply_png(subject, load_db=args.load)


if __name__ == "__main__":
    _cli()
