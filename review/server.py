"""
review/server.py — FastAPI review backend.

Start: uvicorn review.server:app --host 0.0.0.0 --port 8000
"""

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator

_DEFAULT_DB = os.getenv("DB_PATH", "/data/db/qbank.db")
_DEFAULT_FIGURES = os.getenv("FIGURES_DIR", "/data/db/figures")

VALID_ANSWERS = {"A", "B", "C", "D"}


# ── Pydantic models ───────────────────────────────────────────────────────────

class EditPayload(BaseModel):
    stem: Optional[str] = None
    option_a: Optional[str] = None
    option_b: Optional[str] = None
    option_c: Optional[str] = None
    option_d: Optional[str] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None

    @field_validator("correct_answer")
    @classmethod
    def validate_correct_answer(cls, v):
        if v is not None and v not in VALID_ANSWERS:
            raise ValueError(f"correct_answer must be A, B, C, or D — got {v!r}")
        return v


# ── DB helpers ────────────────────────────────────────────────────────────────

def _get_conn(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _row_to_dict(row: sqlite3.Row, figures_dir: str) -> dict:
    d = dict(row)
    d["has_figure"] = bool(d.get("has_figure", 0))
    d["edited"] = bool(d.get("edited", 0))
    # Add figure_url — always present, null when no figure
    if d.get("has_figure") and d.get("figure_path"):
        fname = Path(d["figure_path"]).name
        d["figure_url"] = f"/figures/{fname}"
    else:
        d["figure_url"] = None
    return d


# ── App factory ───────────────────────────────────────────────────────────────

def create_app(db_path: str = _DEFAULT_DB, figures_dir: str = _DEFAULT_FIGURES) -> FastAPI:
    app = FastAPI(title="QBank Review API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Health ────────────────────────────────────────────────────────────────
    @app.get("/health")
    def health():
        return {"status": "ok"}

    # ── Next pending question ─────────────────────────────────────────────────
    @app.get("/questions/next")
    def next_question():
        with _get_conn(db_path) as conn:
            row = conn.execute(
                "SELECT * FROM questions WHERE review_status='pending' "
                "ORDER BY confidence DESC LIMIT 1"
            ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="No pending questions")
        return _row_to_dict(row, figures_dir)

    # ── List questions with optional filters ──────────────────────────────────
    @app.get("/questions")
    def list_questions(
        subject: Optional[str] = Query(None),
        status: Optional[str] = Query(None),
    ):
        sql = "SELECT * FROM questions WHERE 1=1"
        params: list = []
        if subject:
            sql += " AND subject=?"
            params.append(subject)
        if status:
            sql += " AND review_status=?"
            params.append(status)
        sql += " ORDER BY created_at DESC"
        with _get_conn(db_path) as conn:
            rows = conn.execute(sql, params).fetchall()
        return [_row_to_dict(r, figures_dir) for r in rows]

    # ── Approve ───────────────────────────────────────────────────────────────
    @app.post("/questions/{qid}/approve")
    def approve(qid: str):
        now = datetime.now(timezone.utc).isoformat()
        with _get_conn(db_path) as conn:
            cur = conn.execute(
                "UPDATE questions SET review_status='approved', reviewed_at=? WHERE id=?",
                (now, qid),
            )
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Question not found")
        return {"id": qid, "review_status": "approved"}

    # ── Reject ────────────────────────────────────────────────────────────────
    @app.post("/questions/{qid}/reject")
    def reject(qid: str):
        now = datetime.now(timezone.utc).isoformat()
        with _get_conn(db_path) as conn:
            cur = conn.execute(
                "UPDATE questions SET review_status='rejected', reviewed_at=? WHERE id=?",
                (now, qid),
            )
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Question not found")
        return {"id": qid, "review_status": "rejected"}

    # ── Edit ──────────────────────────────────────────────────────────────────
    @app.post("/questions/{qid}/edit")
    def edit(qid: str, payload: EditPayload):
        updates: dict = {
            k: v for k, v in payload.model_dump().items() if v is not None
        }
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")

        now = datetime.now(timezone.utc).isoformat()
        updates["review_status"] = "approved"
        updates["reviewed_at"] = now
        updates["edited"] = 1

        set_clause = ", ".join(f"{k}=?" for k in updates)
        values = list(updates.values()) + [qid]

        with _get_conn(db_path) as conn:
            cur = conn.execute(
                f"UPDATE questions SET {set_clause} WHERE id=?", values
            )
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Question not found")
        return {"id": qid, "review_status": "approved", "edited": True}

    # ── Stats ─────────────────────────────────────────────────────────────────
    @app.get("/stats")
    def stats():
        with _get_conn(db_path) as conn:
            row = conn.execute(
                """SELECT
                    SUM(CASE WHEN review_status='approved' THEN 1 ELSE 0 END) AS approved,
                    SUM(CASE WHEN review_status='rejected' THEN 1 ELSE 0 END) AS rejected,
                    SUM(CASE WHEN edited=1 THEN 1 ELSE 0 END)                 AS edited,
                    SUM(CASE WHEN review_status='pending' THEN 1 ELSE 0 END)  AS pending,
                    COUNT(*) AS total
                FROM questions"""
            ).fetchone()
        return {
            "approved": row["approved"] or 0,
            "rejected": row["rejected"] or 0,
            "edited": row["edited"] or 0,
            "pending": row["pending"] or 0,
            "total": row["total"] or 0,
        }

    # ── Figures ───────────────────────────────────────────────────────────────
    @app.get("/figures/{filename}")
    def get_figure(filename: str):
        # Prevent path traversal
        safe_name = Path(filename).name
        path = Path(figures_dir) / safe_name
        if not path.exists():
            raise HTTPException(status_code=404, detail="Figure not found")
        return FileResponse(str(path), media_type="image/png")

    return app


# ── Module-level app for uvicorn ─────────────────────────────────────────────
app = create_app()
