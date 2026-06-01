"""
Briefing file parser.

Parses the human-written .md briefing file that must exist alongside every PDF.
Required format:

    ## Basic Info
    - **file:** 10_ACT_Practice_Tests.pdf
    - **relevant_pages:** 45–74
    - **target_year:** 11–12
    - **difficulty:** hard

    ## Subject Coverage
    - **pages 45–54:** quantitative_reasoning
    - **pages 55–60:** reading_comprehension
    - **pages 61–74:** science_reasoning
"""
import re
from pathlib import Path
from typing import Optional

VALID_SUBJECTS = {
    "quantitative_reasoning",
    "verbal_reasoning",
    "logical_reasoning",
    "science_reasoning",
    "reading_comprehension",
    "writing",
    "skip",
}

_DASH_RE = re.compile(r"[–—\-]")
_FIELD_RE = re.compile(r"\s*-\s+\*\*([^*:]+):\*\*\s*(.*)")


def _parse_range(text: str) -> tuple[int, int]:
    parts = _DASH_RE.split(text.strip(), maxsplit=1)
    return int(parts[0].strip()), int(parts[1].strip())


def _field_kv(line: str) -> tuple[Optional[str], Optional[str]]:
    m = _FIELD_RE.match(line)
    if not m:
        return None, None
    return m.group(1).strip().lower(), m.group(2).strip()


def _parse_subject_coverage(lines: list[str]) -> list[dict]:
    coverage = []
    pattern = re.compile(
        r"\s*-\s+\*\*pages\s+([\d]+[–—\-][\d]+)\s*:\*\*\s*(\S+)",
        re.IGNORECASE,
    )
    for line in lines:
        m = pattern.match(line)
        if m:
            start, end = _parse_range(m.group(1))
            subject = m.group(2).rstrip(".,;").lower()
            if subject not in VALID_SUBJECTS:
                raise ValueError(
                    f"Invalid subject '{subject}'. Must be one of: {sorted(VALID_SUBJECTS)}"
                )
            coverage.append({"pages_start": start, "pages_end": end, "subject": subject})
    return coverage


def load(path: str) -> dict:
    """
    Parse a briefing .md file. Returns structured dict.
    Raises FileNotFoundError if missing, ValueError if subject is invalid.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(
            f"\n\nBRIEFING FILE MISSING: {path}\n"
            f"Create a .md briefing file alongside your PDF before running the pipeline.\n"
        )

    lines = p.read_text(encoding="utf-8").splitlines()

    sections: dict[str, list[str]] = {}
    current: Optional[str] = None
    for line in lines:
        if line.startswith("## "):
            current = line[3:].strip().lower()
            sections[current] = []
        elif current is not None:
            sections[current].append(line)

    basic = sections.get("basic info", [])
    coverage_lines = sections.get("subject coverage", [])

    file_val = ""
    relevant_start = 1
    relevant_end = 9999
    target_year = ""
    difficulty = ""

    for line in basic:
        key, v = _field_kv(line)
        if key is None:
            continue
        if key == "file":
            file_val = v
        elif key == "relevant_pages":
            try:
                relevant_start, relevant_end = _parse_range(v)
            except (ValueError, IndexError):
                pass
        elif key == "target_year":
            target_year = v
        elif key == "difficulty":
            difficulty = v

    subject_coverage = _parse_subject_coverage(coverage_lines)

    return {
        "file": file_val,
        "relevant_pages_start": relevant_start,
        "relevant_pages_end": relevant_end,
        "target_year": target_year,
        "difficulty": difficulty,
        "subject_coverage": subject_coverage,
    }


def get_subject_for_page(data: dict, page: int) -> Optional[str]:
    """Return subject for a page number, or None if outside all declared ranges."""
    for entry in data["subject_coverage"]:
        if entry["pages_start"] <= page <= entry["pages_end"]:
            return entry["subject"]
    return None


def is_relevant_page(data: dict, page: int) -> bool:
    """True if page falls within relevant_pages range."""
    return data["relevant_pages_start"] <= page <= data["relevant_pages_end"]
