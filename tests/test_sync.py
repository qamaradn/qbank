"""
Sync tests — S-01 through S-05.

All fast: use real SQLite + mocked Supabase client.
Supabase credentials are not available in test environment;
mocking is required and appropriate here.

Run: pytest tests/test_sync.py -v
"""
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


# ── DB helpers ────────────────────────────────────────────────────────────────

def _init_db(path: str) -> sqlite3.Connection:
    schema = (Path(__file__).parent.parent / "db" / "schema.sql").read_text()
    conn = sqlite3.connect(path)
    conn.executescript(schema)
    conn.commit()
    return conn


def _insert(conn, review_status="approved", has_figure=0, figure_path=None, **kw):
    qid = str(uuid.uuid4())
    defaults = dict(
        id=qid, subject="quantitative_reasoning",
        stem="Q?", option_a="A", option_b="B", option_c="C", option_d="D",
        correct_answer="A", explanation="E", writing_prompt=None,
        year_level="7-8", difficulty="easy", topic="t",
        has_figure=has_figure, figure_path=figure_path,
        confidence=0.9, source_book="book1", source_page=1,
        review_status=review_status,
        created_at=datetime.now(timezone.utc).isoformat(),
        reviewed_at=None, edited=0,
    )
    defaults.update(kw)
    conn.execute(
        """INSERT INTO questions VALUES (
            :id,:subject,:stem,:option_a,:option_b,:option_c,:option_d,
            :correct_answer,:explanation,:writing_prompt,:year_level,:difficulty,
            :topic,:has_figure,:figure_path,:confidence,:source_book,:source_page,
            :review_status,:created_at,:reviewed_at,:edited
        )""", defaults,
    )
    conn.commit()
    return qid


@pytest.fixture()
def db_path(tmp_path):
    path = str(tmp_path / "test.db")
    conn = _init_db(path)
    conn.close()
    return path


def _make_supabase_mock():
    """Return a mock Supabase client whose table/storage calls succeed by default."""
    sb = MagicMock()
    # table().upsert().execute() chain
    execute_result = MagicMock()
    execute_result.data = []
    sb.table.return_value.upsert.return_value.execute.return_value = execute_result
    # storage.from_().upload()
    sb.storage.from_.return_value.upload.return_value = MagicMock()
    return sb


# ── S-01 ──────────────────────────────────────────────────────────────────────
def test_s01_dry_run_shows_count_without_modifying(db_path, tmp_path):
    """dry_run() returns count of approved questions, makes no Supabase calls."""
    conn = sqlite3.connect(db_path)
    for _ in range(25):
        _insert(conn, review_status="approved")
    for _ in range(10):
        _insert(conn, review_status="pending")
    conn.close()

    sb = _make_supabase_mock()
    import review.sync as sync
    result = sync.dry_run(db_path=db_path, supabase_client=sb)

    assert result["would_sync"] == 25
    # No actual Supabase calls
    sb.table.assert_not_called()
    sb.storage.from_.assert_not_called()


# ── S-02 ──────────────────────────────────────────────────────────────────────
def test_s02_only_approved_questions_synced(db_path):
    """sync() sends only approved questions to Supabase, not pending/rejected."""
    conn = sqlite3.connect(db_path)
    for _ in range(20):
        _insert(conn, review_status="approved")
    for _ in range(5):
        _insert(conn, review_status="rejected")
    for _ in range(100):
        _insert(conn, review_status="pending")
    conn.close()

    sb = _make_supabase_mock()
    import review.sync as sync
    result = sync.run(db_path=db_path, supabase_client=sb, figures_dir="/tmp")

    # upsert must have been called exactly once with 20 records (or in batches summing to 20)
    total_upserted = sum(
        len(c.args[0]) if c.args else 0
        for c in sb.table.return_value.upsert.call_args_list
    )
    assert total_upserted == 20
    assert result["synced"] == 20
    assert result["failed"] == 0


# ── S-03 ──────────────────────────────────────────────────────────────────────
def test_s03_sync_is_idempotent(db_path):
    """Running sync() twice upserts same records — no duplicates, no errors."""
    conn = sqlite3.connect(db_path)
    for _ in range(5):
        _insert(conn, review_status="approved")
    conn.close()

    sb = _make_supabase_mock()
    import review.sync as sync
    r1 = sync.run(db_path=db_path, supabase_client=sb, figures_dir="/tmp")
    r2 = sync.run(db_path=db_path, supabase_client=sb, figures_dir="/tmp")

    assert r1["synced"] == 5
    assert r2["synced"] == 5  # upsert is idempotent — same 5 questions again
    assert r1["failed"] == 0
    assert r2["failed"] == 0


# ── S-04 ──────────────────────────────────────────────────────────────────────
def test_s04_figures_uploaded_to_storage(db_path, tmp_path):
    """Approved questions with has_figure=True get their PNG uploaded to Storage."""
    figures_dir = tmp_path / "figures"
    figures_dir.mkdir()
    fig_path = str(figures_dir / "q1_fig.png")
    Path(fig_path).write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 16)

    conn = sqlite3.connect(db_path)
    _insert(conn, review_status="approved", has_figure=1, figure_path=fig_path)
    _insert(conn, review_status="approved", has_figure=0, figure_path=None)
    conn.close()

    sb = _make_supabase_mock()
    import review.sync as sync
    result = sync.run(db_path=db_path, supabase_client=sb, figures_dir=str(figures_dir))

    # Storage upload called exactly once (for the one figure question)
    assert sb.storage.from_.return_value.upload.call_count == 1
    assert result["figures_uploaded"] == 1


# ── S-05 ──────────────────────────────────────────────────────────────────────
def test_s05_network_error_does_not_stop_sync(db_path, caplog):
    """One Supabase error on a question doesn't crash the whole sync."""
    conn = sqlite3.connect(db_path)
    ids = [_insert(conn, review_status="approved") for _ in range(20)]
    conn.close()

    call_count = 0

    def failing_upsert(records):
        nonlocal call_count
        call_count += 1
        mock = MagicMock()
        if call_count == 1:
            # Fail on first batch/record
            mock.execute.side_effect = Exception("Network timeout")
        else:
            result = MagicMock()
            result.data = records
            mock.execute.return_value = result
        return mock

    sb = _make_supabase_mock()
    sb.table.return_value.upsert.side_effect = failing_upsert

    import logging, review.sync as sync
    with caplog.at_level(logging.ERROR, logger="review.sync"):
        result = sync.run(db_path=db_path, supabase_client=sb, figures_dir="/tmp")

    # Some synced, some failed — total adds up, no unhandled exception
    assert result["synced"] + result["failed"] > 0
    assert result["failed"] >= 1
    assert "failed" in caplog.text.lower() or "error" in caplog.text.lower()
