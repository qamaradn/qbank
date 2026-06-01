"""
Review API tests — R-01 through R-17.

All fast: use in-memory SQLite + FastAPI TestClient.
Run: pytest tests/test_review_api.py -v
"""
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


# ── test database helpers ──────────────────────────────────────────────────────

def _init_db(path: str) -> sqlite3.Connection:
    schema = (Path(__file__).parent.parent / "db" / "schema.sql").read_text()
    conn = sqlite3.connect(path)
    conn.executescript(schema)
    conn.commit()
    return conn


def _insert_question(conn: sqlite3.Connection, **overrides) -> str:
    qid = str(uuid.uuid4())
    defaults = {
        "id": qid,
        "subject": "quantitative_reasoning",
        "stem": "What is 2 + 2?",
        "option_a": "3", "option_b": "4", "option_c": "5", "option_d": "6",
        "correct_answer": "B",
        "explanation": "Basic addition.",
        "topic": "arithmetic",
        "difficulty": "medium",
        "confidence": 0.95,
        "source_book": "test_book",
        "source_page": 1,
        "source_page_description": "A basic arithmetic page.",
        "review_status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "reviewed_at": None,
        "edited": 0,
    }
    defaults.update(overrides)
    conn.execute(
        """INSERT INTO questions (
            id, subject, stem, option_a, option_b, option_c, option_d,
            correct_answer, explanation, topic, difficulty, confidence,
            source_book, source_page, source_page_description,
            review_status, created_at, reviewed_at, edited
        ) VALUES (
            :id, :subject, :stem, :option_a, :option_b, :option_c, :option_d,
            :correct_answer, :explanation, :topic, :difficulty, :confidence,
            :source_book, :source_page, :source_page_description,
            :review_status, :created_at, :reviewed_at, :edited
        )""",
        defaults,
    )
    conn.commit()
    return defaults["id"]


@pytest.fixture()
def db_path(tmp_path):
    path = str(tmp_path / "test.db")
    conn = _init_db(path)
    conn.close()
    return path


@pytest.fixture()
def client(db_path):
    from review.server import create_app
    app = create_app(db_path=db_path)
    return TestClient(app)


@pytest.fixture()
def client_with_data(db_path):
    conn = sqlite3.connect(db_path)
    qid = _insert_question(conn)
    conn.close()
    from review.server import create_app
    app = create_app(db_path=db_path)
    tc = TestClient(app)
    tc._pending_id = qid
    return tc


# ── R-01 ──────────────────────────────────────────────────────────────────────
def test_r01_next_returns_pending_question(client_with_data):
    resp = client_with_data.get("/questions/next")
    assert resp.status_code == 200
    data = resp.json()
    assert data["review_status"] == "pending"
    assert "stem" in data
    assert "id" in data
    assert "source_page_description" in data


# ── R-02 ──────────────────────────────────────────────────────────────────────
def test_r02_next_returns_404_when_empty(client):
    resp = client.get("/questions/next")
    assert resp.status_code == 404


# ── R-03 ──────────────────────────────────────────────────────────────────────
def test_r03_approve_sets_status(client_with_data, db_path):
    qid = client_with_data._pending_id
    resp = client_with_data.post(f"/questions/{qid}/approve")
    assert resp.status_code == 200
    conn = sqlite3.connect(db_path)
    row = conn.execute("SELECT review_status, reviewed_at FROM questions WHERE id=?", (qid,)).fetchone()
    conn.close()
    assert row[0] == "approved"
    assert row[1] is not None


# ── R-04 ──────────────────────────────────────────────────────────────────────
def test_r04_reject_sets_status(client_with_data, db_path):
    qid = client_with_data._pending_id
    resp = client_with_data.post(f"/questions/{qid}/reject")
    assert resp.status_code == 200
    conn = sqlite3.connect(db_path)
    row = conn.execute("SELECT review_status FROM questions WHERE id=?", (qid,)).fetchone()
    conn.close()
    assert row[0] == "rejected"


# ── R-05 ──────────────────────────────────────────────────────────────────────
def test_r05_edit_updates_fields(client_with_data, db_path):
    qid = client_with_data._pending_id
    resp = client_with_data.post(
        f"/questions/{qid}/edit",
        json={"stem": "What is 3 + 3?", "correct_answer": "C"},
    )
    assert resp.status_code == 200
    conn = sqlite3.connect(db_path)
    row = conn.execute("SELECT stem, correct_answer, edited, review_status FROM questions WHERE id=?", (qid,)).fetchone()
    conn.close()
    assert row[0] == "What is 3 + 3?"
    assert row[1] == "C"
    assert row[2] == 1
    assert row[3] == "approved"


# ── R-06 ──────────────────────────────────────────────────────────────────────
def test_r06_edit_rejects_invalid_answer(client_with_data):
    qid = client_with_data._pending_id
    resp = client_with_data.post(f"/questions/{qid}/edit", json={"correct_answer": "E"})
    assert resp.status_code == 422


# ── R-07 ──────────────────────────────────────────────────────────────────────
def test_r07_stats_accurate(db_path):
    conn = sqlite3.connect(db_path)
    for _ in range(10):
        _insert_question(conn, review_status="approved")
    for _ in range(3):
        _insert_question(conn, review_status="rejected")
    for _ in range(2):
        _insert_question(conn, review_status="approved", edited=1)
    for _ in range(50):
        _insert_question(conn, review_status="pending")
    conn.close()

    from review.server import create_app
    tc = TestClient(create_app(db_path=db_path))
    data = tc.get("/stats").json()
    assert data["approved"] == 12
    assert data["rejected"] == 3
    assert data["edited"] == 2
    assert data["pending"] == 50
    assert data["total"] == 65


# ── R-08 ──────────────────────────────────────────────────────────────────────
def test_r08_filter_by_subject(db_path):
    conn = sqlite3.connect(db_path)
    for _ in range(3):
        _insert_question(conn, subject="science_reasoning")
    for _ in range(5):
        _insert_question(conn, subject="verbal_reasoning")
    conn.close()

    from review.server import create_app
    tc = TestClient(create_app(db_path=db_path))
    data = tc.get("/questions?subject=science_reasoning").json()
    assert len(data) == 3
    assert all(q["subject"] == "science_reasoning" for q in data)


# ── R-09 ──────────────────────────────────────────────────────────────────────
def test_r09_filter_by_status(db_path):
    conn = sqlite3.connect(db_path)
    for _ in range(4):
        _insert_question(conn, review_status="pending")
    for _ in range(6):
        _insert_question(conn, review_status="approved")
    conn.close()

    from review.server import create_app
    tc = TestClient(create_app(db_path=db_path))
    data = tc.get("/questions?status=pending").json()
    assert len(data) == 4


# ── R-10 ──────────────────────────────────────────────────────────────────────
def test_r10_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200


# ── R-11 ──────────────────────────────────────────────────────────────────────
def test_r11_delete_question(client_with_data, db_path):
    qid = client_with_data._pending_id
    resp = client_with_data.delete(f"/questions/{qid}")
    assert resp.status_code == 200
    conn = sqlite3.connect(db_path)
    row = conn.execute("SELECT id FROM questions WHERE id=?", (qid,)).fetchone()
    conn.close()
    assert row is None


# ── R-12 ──────────────────────────────────────────────────────────────────────
def test_r12_bulk_approve(db_path):
    conn = sqlite3.connect(db_path)
    for _ in range(5):
        _insert_question(conn, review_status="pending", confidence=0.95)
    for _ in range(3):
        _insert_question(conn, review_status="pending", confidence=0.75)
    conn.close()

    from review.server import create_app
    tc = TestClient(create_app(db_path=db_path))
    data = tc.post("/questions/bulk-approve?min_confidence=0.90").json()
    assert data["approved"] == 5


# ── R-13 ──────────────────────────────────────────────────────────────────────
def test_r13_topic_stats(db_path):
    conn = sqlite3.connect(db_path)
    for _ in range(3):
        _insert_question(conn, topic="percentages", review_status="approved")
    for _ in range(2):
        _insert_question(conn, topic="percentages", review_status="pending")
    conn.close()

    from review.server import create_app
    tc = TestClient(create_app(db_path=db_path))
    data = tc.get("/stats/topics").json()
    assert data["quantitative_reasoning"]["percentages"]["approved"] == 3
    assert data["quantitative_reasoning"]["percentages"]["pending"] == 2


# ── R-14 ──────────────────────────────────────────────────────────────────────
def test_r14_source_page_description_returned(client_with_data):
    resp = client_with_data.get("/questions/next")
    assert resp.status_code == 200
    data = resp.json()
    assert data["source_page_description"] == "A basic arithmetic page."
