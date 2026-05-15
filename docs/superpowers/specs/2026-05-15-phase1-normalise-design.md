# Phase 1 — Normalise: Design Spec
**Date:** 2026-05-15
**Status:** Approved
**Branch:** feature/phase1-normalise

---

## What We Are Building

`pipeline/phase1_normalise.py` — the first phase of the QBank ETL pipeline. It accepts a book ID and PDF path, reads the accompanying briefing file, calls Docling to process the PDF, and writes structured output files (markdown per page, page images, figure crops, and a master JSON) that all downstream phases consume.

---

## Architecture

`phase1_normalise.py` is a thin orchestrator around Docling. It does no ML itself — it configures Docling, calls it once per book, then writes structured output files.

```
run(book_id, pdf_path)
    │
    ├── validate_book_id()        → raises ValueError if invalid chars
    ├── require_briefing()        → raises FileNotFoundError if .md missing
    ├── load briefing             → get relevant_pages, column_format
    │
    ├── call Docling once on full PDF
    │
    ├── for each page in relevant_pages:
    │       ├── skip if already processed (resumable)
    │       ├── _process_page(docling_result, page_n)
    │       │       ├── write pages/<n>.md
    │       │       ├── write images/<n>.png
    │       │       └── write figures/<n>_fig_<k>.png (if figures present)
    │       └── log progress
    │
    └── write docling_output.json
```

**Key decisions:**
- Docling called **once per book** (not once per page) — matches Docling's design
- `double_column` layout from briefing → passed to Docling's column-aware reading order
- All output paths from `config.py` — no hardcoded paths anywhere
- Resumable: if `pages/<n>.md` exists, skip that page entirely

---

## Output Structure

```
SCRATCH_DIR/<book_id>/
    pages/
        <n>.md          ← Docling markdown for page n
    images/
        <n>.png         ← full page image
    figures/
        <n>_fig_<k>.png ← cropped figure image (k = figure index on page)
    docling_output.json
```

### docling_output.json Schema

```json
{
  "book_id": "10_ACT_Practice_Tests",
  "total_pages": 860,
  "pages": [
    {
      "page_number": 45,
      "markdown_path": "<SCRATCH_DIR>/10_ACT_Practice_Tests/pages/45.md",
      "image_path": "<SCRATCH_DIR>/10_ACT_Practice_Tests/images/45.png",
      "elements": [
        {
          "type": "text",
          "text": "1. A train travels...",
          "x": 50, "y": 80, "width": 500, "height": 20
        },
        {
          "type": "figure",
          "text": "",
          "x": 50, "y": 300, "width": 280, "height": 200,
          "figure_path": "<SCRATCH_DIR>/10_ACT_Practice_Tests/figures/45_fig_1.png"
        }
      ]
    }
  ]
}
```

**Rules:**
- Only relevant pages appear in `pages[]` — skipped/cover pages never written
- Every element has `(x, y, width, height)` — required by Phase 3 figure detection
- `figure_path` only present on elements with `type == "figure"`

---

## Error Handling

### Validation (fail fast, before Docling runs)

| Condition | Behaviour |
|---|---|
| `book_id` has spaces, `!`, `(` etc | `ValueError` — alphanumeric + underscores only |
| Briefing `.md` missing | `FileNotFoundError` — with CLAUDE.md template hint |
| PDF file missing | `FileNotFoundError` — clear message |
| Output dirs don't exist | Auto-created with `os.makedirs(exist_ok=True)` |

### During Processing

| Condition | Behaviour |
|---|---|
| Page already processed (`pages/N.md` exists) | Skip, log "skipping page N (already done)" |
| Page outside `relevant_pages` range | Skip, never written to disk |
| No figures on page | `figures/` entry omitted — not an error |
| Docling OCR produces empty markdown | Write empty file, log warning — Phase 2 flags low-confidence |
| Docling crashes on one page | Log error + page number, continue to next page |

---

## Testing Approach

All 9 tests from TESTS.md. Tests call real Docling — marked `@pytest.mark.slow`.

| Test | Type | Fixture |
|---|---|---|
| P1-01: valid PDF + briefing → no error | UNIT | `act_5pages.pdf` + briefing |
| P1-02: missing briefing → FileNotFoundError | UNIT | `act_5pages.pdf`, no .md |
| P1-03: only relevant pages processed | INTEGRATION | `act_5pages.pdf`, briefing says 3 of 5 pages relevant |
| P1-04: docling_output.json correct structure | CONTRACT | `act_5pages.pdf` |
| P1-05: markdown UTF-8 and non-empty | CONTRACT | `act_5pages.pdf` |
| P1-06: figures extracted | INTEGRATION | `act_5pages.pdf` (ACT maths pages have geometry figures) |
| P1-07: resumable, second run skips existing pages | UNIT | Run phase1 twice on `act_5pages.pdf` |
| P1-08: scanned PDF, OCR works | EDGE | `rsaggarwal_3pages.pdf` + `sample_scanned_briefing.md` |
| P1-09: invalid book_id → ValueError | UNIT | No PDF needed |

### PDF Fixtures (created once, committed)
```
tests/fixtures/
    act_5pages.pdf             ← pages 45–49 sliced from ACT PDF (pypdf)
    rsaggarwal_3pages.pdf      ← pages 1–3 sliced from RS Aggarwal PDF
    sample_scanned_briefing.md ← minimal briefing for rsaggarwal slice
```

Run slow tests: `pytest tests/test_phase1_normalise.py -v`
Skip slow tests: `pytest -m "not slow"`

---

## Dependencies to Install

```
docling>=2.0.0     ← PDF processing + OCR (already in requirements.txt)
pypdf>=4.0.0       ← slicing test PDF fixtures
```

---

## Files Changed

| File | Action |
|---|---|
| `pipeline/phase1_normalise.py` | Implement (currently stub) |
| `tests/test_phase1_normalise.py` | Implement (currently stub) |
| `tests/fixtures/act_5pages.pdf` | Create (slice from ACT PDF) |
| `tests/fixtures/rsaggarwal_3pages.pdf` | Create (slice from RS Aggarwal PDF) |
| `tests/fixtures/sample_scanned_briefing.md` | Create |
| `tests/fixtures/sample_act_briefing.md` | Create (minimal briefing for act_5pages fixture) |
| `requirements.txt` | Add `pypdf>=4.0.0` |
| `.gitignore` | Add `!tests/fixtures/*.pdf` exception (currently `*.pdf` blocks test fixtures) |
