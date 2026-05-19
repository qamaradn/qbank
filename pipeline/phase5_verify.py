"""
Phase 5 — Question Verification and DB Loading

3-tier system for deciding which questions need human review:

  Tier 1 (confidence >= AUTO_APPROVE)   → auto-approve, insert as 'approved'
  Tier 2 (confidence >= VERIFY_THRESH)  → Claude solves independently:
      • Claude answer matches AND verified=True → 'approved'
      • Mismatch or Claude uncertain       → 'pending'
  Tier 3 (confidence < VERIFY_THRESH)   → insert as 'pending' (human review)

Exceptions to tier 2 (always tier 1/3 only):
  • Figure questions (Claude can't see the image)
  • Writing questions (no correct_answer to verify)

Resumable: questions already in DB (by id) are skipped.
"""

import json
import logging
import os
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

AUTO_APPROVE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.90"))
VERIFY_THRESHOLD = float(os.getenv("VERIFY_THRESHOLD", "0.70"))

_VERIFY_PROMPT = """\
You are checking whether this exam question and answer are correct.

QUESTION: {stem}
A) {option_a}
B) {option_b}
C) {option_c}
D) {option_d}

Claimed correct answer: {correct_answer}) {correct_option}
Explanation given: {explanation}

Tasks:
1. Solve the question independently.
2. Check whether the claimed answer and explanation are correct.
3. Check whether the wrong options are clearly wrong.

Return ONLY valid JSON, no markdown:
{{"verified": true|false, "answer": "A"|"B"|"C"|"D", "reasoning": "one sentence"}}

"verified" is true only if your answer matches the claimed answer AND the explanation is correct.
"""


def _get_claude_client():
    import anthropic  # noqa: PLC0415
    return anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def verify_question(q: dict, *, _claude_client=None) -> dict:
    """
    Ask Claude to independently solve a question and verify correctness.

    Returns {"verified": bool, "claude_answer": str, "reasoning": str}
    """
    client = _claude_client or _get_claude_client()
    model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")

    option_map = {
        "A": q.get("option_a", ""),
        "B": q.get("option_b", ""),
        "C": q.get("option_c", ""),
        "D": q.get("option_d", ""),
    }
    correct = str(q.get("correct_answer", ""))
    prompt = _VERIFY_PROMPT.format(
        stem=q.get("stem", ""),
        option_a=q.get("option_a", ""),
        option_b=q.get("option_b", ""),
        option_c=q.get("option_c", ""),
        option_d=q.get("option_d", ""),
        correct_answer=correct,
        correct_option=option_map.get(correct, ""),
        explanation=q.get("explanation", ""),
    )

    msg = client.messages.create(
        model=model,
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}],
    )
    text = msg.content[0].text.strip()

    # Strip markdown fences if present
    import re  # noqa: PLC0415
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text).strip()

    try:
        parsed = json.loads(text)
        return {
            "verified": bool(parsed.get("verified", False)),
            "claude_answer": str(parsed.get("answer", "")),
            "reasoning": str(parsed.get("reasoning", "")),
        }
    except json.JSONDecodeError:
        logger.warning(f"Could not parse Claude verify response: {text[:100]}")
        return {"verified": False, "claude_answer": "", "reasoning": "parse error"}


def _stem_fingerprint(stem: str) -> str:
    """Normalised 12-word prefix for near-duplicate detection."""
    import re as _re  # noqa: PLC0415
    words = _re.sub(r"[^a-z0-9 ]", "", stem.lower()).split()
    return " ".join(words[:12])


def is_near_duplicate(conn: sqlite3.Connection, q: dict) -> bool:
    """
    Return True if a question with a very similar stem already exists in the DB
    for the same subject. Uses a 12-word normalised prefix comparison.
    """
    fp = _stem_fingerprint(q.get("stem") or "")
    if not fp:
        return False
    subject = q.get("subject", "")
    rows = conn.execute(
        "SELECT stem FROM questions WHERE subject=?", (subject,)
    ).fetchall()
    for row in rows:
        if _stem_fingerprint(row[0] or "") == fp:
            return True
    return False


def _is_in_db(conn: sqlite3.Connection, qid: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM questions WHERE id=?", (qid,)
    ).fetchone() is not None


def _insert(conn: sqlite3.Connection, q: dict, status: str) -> None:
    conn.execute(
        """INSERT OR IGNORE INTO questions (
            id, subject, stem, option_a, option_b, option_c, option_d,
            correct_answer, explanation, writing_prompt,
            year_level, difficulty, topic,
            has_figure, figure_path,
            confidence, source_book, source_page,
            review_status, created_at, reviewed_at, edited
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            q.get("id"), q.get("subject"), q.get("stem"),
            q.get("option_a"), q.get("option_b"), q.get("option_c"), q.get("option_d"),
            q.get("correct_answer"), q.get("explanation"), q.get("writing_prompt"),
            q.get("year_level"), q.get("difficulty"), q.get("topic"),
            1 if q.get("has_figure") else 0,
            q.get("figure_path"),
            float(q.get("confidence", 0.0)),
            q.get("source_book"), q.get("source_page"),
            status,
            q.get("created_at", datetime.now(timezone.utc).isoformat()),
            None, 0,
        ),
    )
    conn.commit()


def process_question(
    q: dict,
    db_path: str,
    *,
    auto_approve_threshold: float = None,
    verify_threshold: float = None,
    _claude_client=None,
) -> dict:
    """
    Classify one question into a tier and insert into SQLite.

    Returns {"tier": "auto_approved"|"claude_approved"|"pending"|"skipped"}
    """
    _auto = auto_approve_threshold if auto_approve_threshold is not None else AUTO_APPROVE_THRESHOLD
    _verify = verify_threshold if verify_threshold is not None else VERIFY_THRESHOLD

    conn = sqlite3.connect(db_path)
    try:
        if _is_in_db(conn, q.get("id", "")):
            return {"tier": "skipped"}

        if is_near_duplicate(conn, q):
            logger.info(f"Near-duplicate detected — skipping: {q.get('id','?')}")
            return {"tier": "duplicate"}

        conf = float(q.get("confidence", 0.0))
        subject = q.get("subject", "")
        has_figure = bool(q.get("has_figure"))
        has_correct_answer = bool(q.get("correct_answer"))

        # Tier 1: auto-approve
        if conf >= _auto:
            _insert(conn, q, "approved")
            logger.info(f"Auto-approved: {q.get('id','?')} conf={conf:.2f}")
            return {"tier": "auto_approved"}

        # Tier 2: Claude verify — only for MCQ text questions
        if conf >= _verify and has_correct_answer and not has_figure and subject != "writing":
            result = verify_question(q, _claude_client=_claude_client)
            if result["verified"] and result["claude_answer"] == q["correct_answer"]:
                _insert(conn, q, "approved")
                logger.info(
                    f"Claude-approved: {q.get('id','?')} "
                    f"claude_answer={result['claude_answer']}"
                )
                return {"tier": "claude_approved"}
            else:
                logger.info(
                    f"Claude disagrees: {q.get('id','?')} "
                    f"claimed={q.get('correct_answer')} claude={result.get('claude_answer')} "
                    f"verified={result.get('verified')}"
                )

        # Tier 3 (or tier 2 fallback): pending for human
        _insert(conn, q, "pending")
        logger.info(f"Pending (human review): {q.get('id','?')} conf={conf:.2f}")
        return {"tier": "pending"}

    finally:
        conn.close()


def run(
    book_id: str,
    output_dir: str = None,
    db_path: str = None,
    *,
    auto_approve_threshold: float = None,
    verify_threshold: float = None,
    api_delay: int = None,
) -> dict:
    """
    Phase 5: verify and load all generated questions for book_id into SQLite.

    Scans output/{subject}/generated/{book_id}_*.json for every subject.
    Resumable: skips questions already present in DB by id.

    Returns {
        "auto_approved": int,
        "claude_approved": int,
        "pending": int,
        "skipped": int,
        "failed": int,
    }
    """
    _output = output_dir or os.getenv("OUTPUT_DIR", "/data/output")
    _db = db_path or os.getenv("DB_PATH", "/data/db/qbank.db")
    _auto = auto_approve_threshold if auto_approve_threshold is not None else AUTO_APPROVE_THRESHOLD
    _verify = verify_threshold if verify_threshold is not None else VERIFY_THRESHOLD
    _delay = api_delay if api_delay is not None else int(os.getenv("API_DELAY_SECONDS", "2"))

    client = _get_claude_client()
    stats = {"auto_approved": 0, "claude_approved": 0, "pending": 0, "skipped": 0, "duplicate": 0, "failed": 0}

    for subject_dir in sorted(Path(_output).iterdir()):
        if not subject_dir.is_dir():
            continue

        # Collect JSON files from both generated/ (text track) and figures/ (figure track)
        json_files: list[Path] = []
        gen_dir = subject_dir / "generated"
        if gen_dir.is_dir():
            json_files.extend(sorted(gen_dir.glob(f"{book_id}_*.json")))
        fig_dir = subject_dir / "figures"
        if fig_dir.is_dir():
            json_files.extend(sorted(fig_dir.glob(f"{book_id}_*_generated.json")))

        for json_file in json_files:
            try:
                data = json.loads(json_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as e:
                logger.error(f"Cannot read {json_file}: {e}")
                stats["failed"] += 1
                continue

            if not isinstance(data, list):
                logger.warning(f"Unexpected format in {json_file} — skipping")
                stats["failed"] += 1
                continue

            for q in data:
                if not isinstance(q, dict) or not q.get("id"):
                    stats["failed"] += 1
                    continue

                result = process_question(
                    q, _db,
                    auto_approve_threshold=_auto,
                    verify_threshold=_verify,
                    _claude_client=client,
                )
                tier = result["tier"]
                if tier == "auto_approved":
                    stats["auto_approved"] += 1
                elif tier == "claude_approved":
                    stats["claude_approved"] += 1
                    time.sleep(_delay)
                elif tier == "skipped":
                    stats["skipped"] += 1
                elif tier == "duplicate":
                    stats["duplicate"] += 1
                else:
                    stats["pending"] += 1

    logger.info(f"Phase 5 complete for {book_id}: {stats}")
    return stats
