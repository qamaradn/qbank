"""Initialise the SQLite database from schema.sql."""
import os
import sqlite3
from pathlib import Path

import config


def create_tables(db_path: str = config.DB_PATH) -> None:
    schema_path = Path(__file__).parent / "schema.sql"
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.executescript(schema_path.read_text())
    print(f"Database initialised: {db_path}")


if __name__ == "__main__":
    create_tables()
