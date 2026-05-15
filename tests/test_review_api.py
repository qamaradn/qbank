"""
Review API tests — R-01 through R-12.

All fast: use in-memory SQLite + FastAPI TestClient.
Run: pytest tests/test_review_api.py -v
"""
import shutil
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

FIXTURES = Path(__file__).parent / "fixtures"


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
        "writing_prompt": None,
        "year_level": "7-8",
        "difficulty": "easy",
        "topic": "arithmetic",
        "has_figure": 0,
        "figure_path": None,
        "confidence": 0.95,
        "source_book": "test_book",
        "source_page": 1,
        "review_status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "reviewed_at": None,
        "edited": 0,
    }
    defaults.update(overrides)
    conn.execute(
        """INSERT INTO questions VALUES (
            :id,:subject,:stem,:option_a,:option_b,:option_c,:option_d,
            :correct_answer,:explanation,:writing_prompt,:year_level,:difficulty,
            :topic,:has_figure,:figure_path,:confidence,:source_book,:source_page,
            :review_status,:created_at,:reviewed_at,:edited
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
def client(db_path, tmp_path):
    figures_dir = str(tmp_path / "figures")
    Path(figures_dir).mkdir()
    from review.server import create_app
    app = create_app(db_path=db_path, figures_dir=figures_dir)
    return TestClient(app)


@pytest.fixture()
def client_with_data(db_path, tmp_path):
    figures_dir = str(tmp_path / "figures")
    Path(figures_dir).mkdir()
    conn = sqlite3.connect(db_path)
    qid = _insert_question(conn)
    conn.close()
    from review.server import create_app
    app = create_app(db_path=db_path, figures_dir=figures_dir)
    tc = TestClient(app)
    tc._pending_id = qid
    return tc


# ── R-01 ──────────────────────────────────────────────────────────────────────
def test_r01_next_returns_pending_question(client_with_data):
    """GET /questions/next returns 200 with a pending question."""
    resp = client_with_data.get("/questions/next")
    assert resp.status_code == 200
    data = resp.json()
    assert data["review_status"] == "pending"
    assert "stem" in data
    assert "id" in data


# ── R-02 ──────────────────────────────────────────────────────────────────────
def test_r02_next_returns_404_when_empty(client):
    """GET /questions/next returns 404 when no pending questions."""
    resp = client.get("/questions/next")
    assert resp.status_code == 404
    assert "pending" in resp.json()["detail"].lower()


# ── R-03 ──────────────────────────────────────────────────────────────────────
def test_r03_approve_sets_status_and_reviewed_at(client_with_data, db_path):
    """POST /questions/{id}/approve sets review_status='approved' and reviewed_at."""
    qid = client_with_data._pending_id
    resp = client_with_data.post(f"/questions/{qid}/approve")
    assert resp.status_code == 200
    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT review_status, reviewed_at FROM questions WHERE id=?", (qid,)
    ).fetchone()
    conn.close()
    assert row[0] == "approved"
    assert row[1] is not None


# ── R-04 ──────────────────────────────────────────────────────────────────────
def test_r04_reject_sets_status(client_with_data, db_path):
    """POST /questions/{id}/reject sets review_status='rejected'."""
    qid = client_with_data._pending_id
    resp = client_with_data.post(f"/questions/{qid}/reject")
    assert resp.status_code == 200
    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT review_status FROM questions WHERE id=?", (qid,)
    ).fetchone()
    conn.close()
    assert row[0] == "rejected"


# ── R-05 ──────────────────────────────────────────────────────────────────────
def test_r05_edit_updates_fields_and_marks_edited(client_with_data, db_path):
    """POST /questions/{id}/edit updates fields, sets edited=1, review_status='approved'."""
    qid = client_with_data._pending_id
    resp = client_with_data.post(
        f"/questions/{qid}/edit",
        json={"stem": "What is 3 + 3?", "correct_answer": "C"},
    )
    assert resp.status_code == 200
    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT stem, correct_answer, edited, review_status FROM questions WHERE id=?",
        (qid,),
    ).fetchone()
    conn.close()
    assert row[0] == "What is 3 + 3?"
    assert row[1] == "C"
    assert row[2] == 1
    assert row[3] == "approved"


# ── R-06 ──────────────────────────────────────────────────────────────────────
def test_r06_edit_rejects_invalid_correct_answer(client_with_data, db_path):
    """POST /questions/{id}/edit rejects correct_answer='E' with 422."""
    qid = client_with_data._pending_id
    resp = client_with_data.post(
        f"/questions/{qid}/edit",
        json={"correct_answer": "E"},
    )
    assert resp.status_code == 422
    # Question must not be modified
    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT review_status, edited FROM questions WHERE id=?", (qid,)
    ).fetchone()
    conn.close()
    assert row[0] == "pending"
    assert row[1] == 0


# ── R-07 ──────────────────────────────────────────────────────────────────────
def test_r07_stats_returns_accurate_counts(db_path, tmp_path):
    """GET /stats returns correct approved/rejected/edited/pending/total counts."""
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
    app = create_app(db_path=db_path, figures_dir=str(tmp_path / "figures"))
    tc = TestClient(app)

    resp = tc.get("/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["approved"] == 12   # 10 + 2 edited (also approved)
    assert data["rejected"] == 3
    assert data["edited"] == 2
    assert data["pending"] == 50
    assert data["total"] == 65


# ── R-08 ──────────────────────────────────────────────────────────────────────
def test_r08_questions_filter_by_subject(db_path, tmp_path):
    """GET /questions?subject=science_reasoning returns only that subject."""
    conn = sqlite3.connect(db_path)
    for _ in range(3):
        _insert_question(conn, subject="science_reasoning")
    for _ in range(5):
        _insert_question(conn, subject="logical_reasoning")
    conn.close()

    from review.server import create_app
    app = create_app(db_path=db_path, figures_dir=str(tmp_path / "figures"))
    tc = TestClient(app)

    resp = tc.get("/questions?subject=science_reasoning")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    assert all(q["subject"] == "science_reasoning" for q in data)


# ── R-09 ──────────────────────────────────────────────────────────────────────
def test_r09_figure_png_served_correctly(db_path, tmp_path):
    """GET /figures/{filename} returns 200 with Content-Type image/png."""
    figures_dir = tmp_path / "figures"
    figures_dir.mkdir()
    shutil.copy(str(FIXTURES / "sample_figure.png"), str(figures_dir / "sample_figure.png"))

    from review.server import create_app
    app = create_app(db_path=db_path, figures_dir=str(figures_dir))
    tc = TestClient(app)

    resp = tc.get("/figures/sample_figure.png")
    assert resp.status_code == 200
    assert "image" in resp.headers["content-type"]
    assert len(resp.content) > 0


# ── R-10 ──────────────────────────────────────────────────────────────────────
def test_r10_text_only_question_has_figure_url_null(client_with_data):
    """GET /questions/next → text-only question has figure_url=null (key present)."""
    resp = client_with_data.get("/questions/next")
    assert resp.status_code == 200
    data = resp.json()
    assert "figure_url" in data, "figure_url key must be present"
    assert data["figure_url"] is None


# ── R-11 ──────────────────────────────────────────────────────────────────────
def test_r11_questions_filter_by_status(db_path, tmp_path):
    """GET /questions?status=pending returns only pending questions."""
    conn = sqlite3.connect(db_path)
    for _ in range(4):
        _insert_question(conn, review_status="pending")
    for _ in range(6):
        _insert_question(conn, review_status="approved")
    conn.close()

    from review.server import create_app
    app = create_app(db_path=db_path, figures_dir=str(tmp_path / "figures"))
    tc = TestClient(app)

    resp = tc.get("/questions?status=pending")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 4
    assert all(q["review_status"] == "pending" for q in data)


# ── R-12 ──────────────────────────────────────────────────────────────────────
def test_r12_health_endpoint_accessible(client):
    """GET /health returns 200 (verifies server is up and responsive)."""
    resp = client.get("/health")
    assert resp.status_code == 200
