"""
Briefing file parser — Phase 0.

Parses the human-written .md briefing file that must exist alongside every PDF.
All pipeline phases call briefing.load() to get structured metadata before
touching any page content.
"""
import re
from pathlib import Path
from typing import Optional

VALID_COVERAGE_SUBJECTS = {
    "quantitative_reasoning",
    "logical_reasoning",
    "science_reasoning",
    "reading_comprehension",
    "writing",
    "skip",
}

# Normalise both hyphen (-) and en-dash (–) in page ranges.
_DASH_RE = re.compile(r"[–—\-]")


def _parse_range(text: str) -> tuple[int, int]:
    """Parse 'NNN–MMM' (en-dash or hyphen) into (start, end) ints."""
    parts = _DASH_RE.split(text.strip(), maxsplit=1)
    return int(parts[0].strip()), int(parts[1].strip())


_FIELD_RE = re.compile(r"\s*-\s+\*\*([^*:]+):\*\*\s*(.*)")


def _field_kv(line: str) -> tuple[Optional[str], Optional[str]]:
    """
    Parse '- **key:** value' → (key, value), both stripped.
    Returns (None, None) if line doesn't match.
    Format in briefing files: **key:** value  (colon is inside the bold markers)
    """
    m = _FIELD_RE.match(line)
    if not m:
        return None, None
    return m.group(1).strip().lower(), m.group(2).strip()


def _field(line: str) -> Optional[str]:
    """Extract only the value from a '- **key:** value' line, or None."""
    _, v = _field_kv(line)
    return v


def _parse_subject_coverage(lines: list[str]) -> list[dict]:
    """
    Parse lines like:
      - **pages 45–120:** logical_reasoning
      - **pages 121–200:** quantitative_reasoning  (extra description allowed)
    Returns list of {pages_start, pages_end, subject}.
    """
    coverage = []
    # Matches: - **pages 45–120:** logical_reasoning (colon inside bold markers)
    pattern = re.compile(
        r"\s*-\s+\*\*pages\s+([\d]+[––—\-][\d]+)\s*:\*\*\s*(\S+)",
        re.IGNORECASE,
    )
    for line in lines:
        m = pattern.match(line)
        if m:
            start, end = _parse_range(m.group(1))
            subject_raw = m.group(2).rstrip(".,;").lower()
            if subject_raw not in VALID_COVERAGE_SUBJECTS:
                raise ValueError(
                    f"Invalid subject '{subject_raw}' in Subject Coverage. "
                    f"Must be one of: {sorted(VALID_COVERAGE_SUBJECTS)}"
                )
            coverage.append({
                "pages_start": start,
                "pages_end": end,
                "subject": subject_raw,
            })
    return coverage


def _parse_known_issues(lines: list[str]) -> list[str]:
    """Collect lines that look like bullet points or plain sentences."""
    issues = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("-"):
            text = stripped.lstrip("- ").strip()
            if text:
                issues.append(text)
        elif stripped:
            issues.append(stripped)
    return issues


def load(path: str) -> dict:
    """
    Parse a PDF briefing .md file and return a structured dict.

    Raises FileNotFoundError if path does not exist.
    Raises ValueError if an invalid subject name appears in Subject Coverage.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(
            f"\n\nBRIEFING FILE MISSING: {path}\n"
            f"You must create this file before running the pipeline.\n"
            f"Template: see CLAUDE.md → PDF METADATA BRIEFING FILES\n"
        )

    text = p.read_text(encoding="utf-8")
    lines = text.splitlines()

    # Split into sections by ## heading
    sections: dict[str, list[str]] = {}
    current_section: Optional[str] = None
    for line in lines:
        if line.startswith("## "):
            current_section = line[3:].strip().lower()
            sections[current_section] = []
        elif current_section is not None:
            sections[current_section].append(line)

    basic = sections.get("basic info", [])
    layout = sections.get("layout", [])
    coverage_lines = sections.get("subject coverage", [])
    samples_lines = sections.get("sample questions", [])
    issues_lines = sections.get("known issues", [])
    year_lines = sections.get("year level", [])

    # ── Basic Info ────────────────────────────────────────────────────────────
    file_val = ""
    total_pages = 0
    relevant_start = 1
    relevant_end = 0

    for line in basic:
        key, v = _field_kv(line)
        if key is None:
            continue

        if key == "file":
            file_val = v
        elif key == "total_pages":
            try:
                total_pages = int(v)
            except ValueError:
                pass
        elif key == "relevant_pages":
            try:
                relevant_start, relevant_end = _parse_range(v)
            except (ValueError, IndexError):
                pass

    # ── Layout ────────────────────────────────────────────────────────────────
    column_format = "single_column"
    has_figures = False
    figure_position = "below_question"
    answer_key_start = 0
    answer_key_end = 0

    for line in layout:
        key, v = _field_kv(line)
        if key is None:
            continue

        if key == "column_format":
            column_format = v.split("|")[0].strip()
        elif key == "has_figures":
            has_figures = v.lower().startswith("y")
        elif key == "figure_position":
            figure_position = v.split("|")[0].strip()
        elif key == "answer_key_pages":
            try:
                answer_key_start, answer_key_end = _parse_range(v)
            except (ValueError, IndexError):
                pass

    # ── Subject Coverage ──────────────────────────────────────────────────────
    subject_coverage = _parse_subject_coverage(coverage_lines)

    # ── Sample Questions ──────────────────────────────────────────────────────
    sample_pages: list[int] = []
    for line in samples_lines:
        key, v = _field_kv(line)
        if key is None:
            continue
        if key == "sample_pages":
            for tok in re.split(r"[\s,;]+", v):
                tok = tok.strip()
                if tok.isdigit():
                    sample_pages.append(int(tok))

    # ── Year Level ────────────────────────────────────────────────────────────
    target_year = ""
    difficulty = ""
    for line in year_lines:
        key, v = _field_kv(line)
        if key is None:
            continue
        if key == "target_year":
            target_year = v
        elif key == "difficulty":
            difficulty = v

    # ── Known Issues ──────────────────────────────────────────────────────────
    known_issues = _parse_known_issues(issues_lines)

    return {
        "file": file_val,
        "total_pages": total_pages,
        "relevant_pages_start": relevant_start,
        "relevant_pages_end": relevant_end,
        "column_format": column_format,
        "has_figures": has_figures,
        "figure_position": figure_position,
        "answer_key_pages_start": answer_key_start,
        "answer_key_pages_end": answer_key_end,
        "subject_coverage": subject_coverage,
        "sample_pages": sample_pages,
        "target_year": target_year,
        "difficulty": difficulty,
        "known_issues": known_issues,
    }


def get_subject_for_page(data: dict, page: int) -> Optional[str]:
    """
    Return the subject string for a given page number from briefing coverage.
    Returns 'skip' if the page falls in a skip range.
    Returns None if the page is outside all declared ranges.
    """
    for entry in data["subject_coverage"]:
        if entry["pages_start"] <= page <= entry["pages_end"]:
            return entry["subject"]
    return None


def is_relevant_page(data: dict, page: int) -> bool:
    """True if page falls within relevant_pages_start..relevant_pages_end."""
    return data["relevant_pages_start"] <= page <= data["relevant_pages_end"]


def is_answer_key_page(data: dict, page: int) -> bool:
    """True if page falls within declared answer_key_pages range."""
    start = data.get("answer_key_pages_start", 0)
    end = data.get("answer_key_pages_end", 0)
    if start == 0 and end == 0:
        return False
    return start <= page <= end


def is_sample_page(data: dict, page: int) -> bool:
    """True if page is listed in sample_pages."""
    return page in data.get("sample_pages", [])
