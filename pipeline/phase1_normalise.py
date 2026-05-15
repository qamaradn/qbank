"""Phase 1 — Normalise: convert PDF to markdown + images using Docling."""
import re


def validate_book_id(book_id: str) -> None:
    """Raise ValueError if book_id contains characters other than letters, digits, and underscores."""
    if not re.match(r"^[A-Za-z0-9_]+$", book_id):
        raise ValueError(
            f"book_id '{book_id}' is invalid: must contain only letters, digits, and underscores"
        )


def run(book_id: str, pdf_path: str) -> None:
    """Run Phase 1 normalisation for a single book."""
    validate_book_id(book_id)
    # Full implementation to follow in subsequent tasks.
