# Phase 1 — Normalise Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement `pipeline/phase1_normalise.py` — a Docling-powered PDF normaliser that converts a book PDF into per-page markdown, images, figure crops, and a structured `docling_output.json`, controlled entirely by the book's briefing file.

**Architecture:** Thin orchestrator around Docling. Validates inputs, reads briefing, calls Docling once per book, then writes output files for each relevant page. All config from `config.py`. Fully resumable.

**Tech Stack:** Python 3.11, Docling 2.x, pypdf (fixture slicing), Pillow (image I/O), pytest with `@pytest.mark.slow`

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `pipeline/phase1_normalise.py` | Implement | Core orchestration + Docling wrapper |
| `tests/test_phase1_normalise.py` | Implement | 9 tests, all marked `@pytest.mark.slow` |
| `tests/fixtures/act_5pages.pdf` | Create | ACT pages 45–49, used by P1-01 through P1-07 |
| `tests/fixtures/sample_act_briefing.md` | Create | Minimal briefing for act_5pages fixture |
| `tests/fixtures/rsaggarwal_3pages.pdf` | Create | RS Aggarwal pages 1–3, used by P1-08 |
| `tests/fixtures/sample_scanned_briefing.md` | Create | Minimal briefing for rsaggarwal slice |
| `requirements.txt` | Modify | Add `pypdf>=4.0.0` |
| `.gitignore` | Modify | Add `!tests/fixtures/*.pdf` exception |

---

### Task 0: Feature branch + install dependencies

**Files:** none (setup only)

- [ ] **Step 1: Create feature branch**

```bash
git checkout -b feature/phase1-normalise
```

- [ ] **Step 2: Install docling and pypdf into the venv**

```bash
.venv/bin/pip install "docling>=2.0.0" "pypdf>=4.0.0"
```

Expected: packages install successfully (docling is large — ~1-2GB, may take several minutes).

- [ ] **Step 3: Update requirements.txt**

Add `pypdf>=4.0.0` to `/scratch/qbank/requirements.txt` after the `docling` line:

```
docling>=2.0.0
pypdf>=4.0.0
```

- [ ] **Step 4: Update .gitignore to allow test fixture PDFs**

In `/scratch/qbank/.gitignore`, find the `*.pdf` line and add an exception below it:

```gitignore
*.pdf
!tests/fixtures/*.pdf
```

- [ ] **Step 5: Commit setup**

```bash
git add requirements.txt .gitignore
git commit -m "chore(phase1): branch setup, add pypdf dep, gitignore fixture PDFs"
```

---

### Task 1: Create PDF fixture files + briefing fixtures

**Files:**
- Create: `tests/fixtures/act_5pages.pdf`
- Create: `tests/fixtures/sample_act_briefing.md`
- Create: `tests/fixtures/rsaggarwal_3pages.pdf`
- Create: `tests/fixtures/sample_scanned_briefing.md`

- [ ] **Step 1: Slice act_5pages.pdf from the ACT PDF**

Run this Python script once (not a test — a one-time fixture generator):

```python
# Run as: .venv/bin/python3 -c "..."
from pypdf import PdfReader, PdfWriter

reader = PdfReader("pdfs/10_ACT_Practice_Tests.pdf")
writer = PdfWriter()
# Pages 45-49 (0-indexed: 44-48)
for i in range(44, 49):
    writer.add_page(reader.pages[i])
with open("tests/fixtures/act_5pages.pdf", "wb") as f:
    writer.write(f)
print("Done — 5 pages written")
```

```bash
.venv/bin/python3 -c "
from pypdf import PdfReader, PdfWriter
reader = PdfReader('pdfs/10_ACT_Practice_Tests.pdf')
writer = PdfWriter()
for i in range(44, 49):
    writer.add_page(reader.pages[i])
with open('tests/fixtures/act_5pages.pdf', 'wb') as f:
    writer.write(f)
print('Done')
"
```

Expected: `Done` printed, file exists at `tests/fixtures/act_5pages.pdf`.

- [ ] **Step 2: Create sample_act_briefing.md**

Create `/scratch/qbank/tests/fixtures/sample_act_briefing.md`:

```markdown
# PDF BRIEFING: ACT 5-Page Test Fixture

## Basic Info
- **file:** act_5pages.pdf
- **publisher:** McGraw-Hill
- **edition:** 2008
- **total_pages:** 5
- **relevant_pages:** 1–5

## Layout
- **column_format:** double_column
- **question_numbering:** 1,2,3
- **options_format:** A.B.C.D.
- **answer_key_pages:** 0–0
- **answer_key_format:** grid
- **has_figures:** yes
- **figure_position:** below_question

## Subject Coverage
- **pages 1–5:** quantitative_reasoning

## Sample Questions
- **has_samples:** no

## Year Level
- **target_year:** 11–12
- **difficulty:** medium to hard
```

Note: `answer_key_pages: 0–0` means no answer key pages (start == end == 0 is the sentinel for "none").

- [ ] **Step 3: Slice rsaggarwal_3pages.pdf**

```bash
.venv/bin/python3 -c "
from pypdf import PdfReader, PdfWriter
reader = PdfReader('pdfs/rsaggarwal.pdf')
writer = PdfWriter()
for i in range(0, 3):
    writer.add_page(reader.pages[i])
with open('tests/fixtures/rsaggarwal_3pages.pdf', 'wb') as f:
    writer.write(f)
print('Done')
"
```

- [ ] **Step 4: Create sample_scanned_briefing.md**

Create `/scratch/qbank/tests/fixtures/sample_scanned_briefing.md`:

```markdown
# PDF BRIEFING: RS Aggarwal 3-Page Test Fixture (Scanned)

## Basic Info
- **file:** rsaggarwal_3pages.pdf
- **publisher:** S. Chand
- **edition:** 2023
- **total_pages:** 3
- **relevant_pages:** 1–3

## Layout
- **column_format:** single_column
- **question_numbering:** 1,2,3
- **options_format:** (A)(B)(C)(D)
- **answer_key_pages:** 0–0
- **answer_key_format:** grid
- **has_figures:** no
- **figure_position:** below_question

## Subject Coverage
- **pages 1–3:** logical_reasoning

## Sample Questions
- **has_samples:** no

## Year Level
- **target_year:** 7–9
- **difficulty:** medium
```

- [ ] **Step 5: Commit fixtures**

```bash
git add tests/fixtures/act_5pages.pdf tests/fixtures/sample_act_briefing.md \
        tests/fixtures/rsaggarwal_3pages.pdf tests/fixtures/sample_scanned_briefing.md
git commit -m "test(phase1): add PDF fixtures and briefing fixtures for 9 tests"
```

---

### Task 2: validate_book_id() + test P1-09 (RED → GREEN)

**Files:**
- Modify: `pipeline/phase1_normalise.py`
- Modify: `tests/test_phase1_normalise.py`

- [ ] **Step 1: Write the failing test (RED)**

Replace the stub contents of `tests/test_phase1_normalise.py` with:

```python
"""
Phase 1 normalise tests — TEST-P1-01 through TEST-P1-09.
All tests are marked @pytest.mark.slow (call real Docling).
Run: .venv/bin/pytest tests/test_phase1_normalise.py -v
Skip slow: .venv/bin/pytest -m "not slow"
"""
import json
import os
import time
import pytest
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"
ACT_PDF = FIXTURES / "act_5pages.pdf"
ACT_BRIEFING = FIXTURES / "sample_act_briefing.md"
SCANNED_PDF = FIXTURES / "rsaggarwal_3pages.pdf"
SCANNED_BRIEFING = FIXTURES / "sample_scanned_briefing.md"

import pipeline.phase1_normalise as phase1


# ── TEST-P1-09 ────────────────────────────────────────────────────────────────
def test_p1_09_invalid_book_id_raises_value_error():
    """[UNIT] book_id with invalid characters raises ValueError."""
    invalid_ids = ["my book! (2025)", "book name", "book-id", "book.name"]
    for bad_id in invalid_ids:
        with pytest.raises(ValueError) as exc_info:
            phase1.validate_book_id(bad_id)
        assert "alphanumeric" in str(exc_info.value).lower() or "underscores" in str(exc_info.value).lower()

    # Valid ids should not raise
    phase1.validate_book_id("my_book")
    phase1.validate_book_id("book2025")
    phase1.validate_book_id("ACT_Practice_Tests")
```

- [ ] **Step 2: Run test — confirm RED**

```bash
.venv/bin/pytest tests/test_phase1_normalise.py::test_p1_09_invalid_book_id_raises_value_error -v
```

Expected: `FAILED` — `AttributeError: module 'pipeline.phase1_normalise' has no attribute 'validate_book_id'`

- [ ] **Step 3: Implement validate_book_id() (minimal)**

Replace stub in `pipeline/phase1_normalise.py` with:

```python
"""Phase 1 — Normalise PDF using Docling."""
import json
import logging
import os
import re
from pathlib import Path
from typing import Optional

import config
from pipeline import briefing as briefing_module

logger = logging.getLogger(__name__)

_BOOK_ID_RE = re.compile(r'^[a-zA-Z0-9_]+$')


def validate_book_id(book_id: str) -> None:
    """Raise ValueError if book_id contains anything other than alphanumeric + underscore."""
    if not _BOOK_ID_RE.match(book_id):
        raise ValueError(
            f"book_id must contain only alphanumeric characters and underscores. "
            f"Got: '{book_id}'"
        )
```

- [ ] **Step 4: Run test — confirm GREEN**

```bash
.venv/bin/pytest tests/test_phase1_normalise.py::test_p1_09_invalid_book_id_raises_value_error -v
```

Expected: `PASSED`

- [ ] **Step 5: Commit**

```bash
git add pipeline/phase1_normalise.py tests/test_phase1_normalise.py
git commit -m "test(phase1): P1-09 validate_book_id RED→GREEN"
```

---

### Task 3: run() skeleton + tests P1-01 and P1-02 (RED → GREEN)

**Files:**
- Modify: `pipeline/phase1_normalise.py`
- Modify: `tests/test_phase1_normalise.py`

- [ ] **Step 1: Add tests P1-01 and P1-02 to test file**

Append to `tests/test_phase1_normalise.py`:

```python
# ── TEST-P1-01 ────────────────────────────────────────────────────────────────
@pytest.mark.slow
def test_p1_01_valid_pdf_and_briefing_runs_without_error(tmp_path, monkeypatch):
    """[UNIT] valid PDF path with valid briefing returns no error."""
    monkeypatch.setenv("SCRATCH_DIR", str(tmp_path))
    import importlib; importlib.reload(config)
    result = phase1.run("act_test", str(ACT_PDF), str(ACT_BRIEFING))
    assert isinstance(result, dict)
    assert result["book_id"] == "act_test"


# ── TEST-P1-02 ────────────────────────────────────────────────────────────────
def test_p1_02_missing_briefing_raises_file_not_found(tmp_path):
    """[UNIT] missing briefing file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError) as exc_info:
        phase1.run("act_test", str(ACT_PDF), "/tmp/does_not_exist.md")
    assert "does_not_exist.md" in str(exc_info.value)
```

- [ ] **Step 2: Run tests — confirm RED**

```bash
.venv/bin/pytest tests/test_phase1_normalise.py::test_p1_02_missing_briefing_raises_file_not_found -v
```

Expected: `FAILED` — `run() takes 1 positional argument` or `AttributeError`

- [ ] **Step 3: Implement run() skeleton**

Add to `pipeline/phase1_normalise.py` after `validate_book_id()`:

```python
def run(book_id: str, pdf_path: str, briefing_path: Optional[str] = None) -> dict:
    """
    Phase 1: Normalise a PDF book using Docling.
    
    Args:
        book_id: Alphanumeric identifier for the book (e.g. 'act_practice').
        pdf_path: Absolute path to the PDF file.
        briefing_path: Path to the .md briefing file. Defaults to pdf_path with .md extension.
    
    Returns:
        docling_output dict written to SCRATCH_DIR/<book_id>/docling_output.json
    """
    validate_book_id(book_id)

    if briefing_path is None:
        briefing_path = pdf_path.replace('.pdf', '.md')

    # Raises FileNotFoundError with helpful message if missing
    briefing_data = briefing_module.load(briefing_path)

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    # Output directories
    scratch_dir = os.path.join(config.SCRATCH_DIR, book_id)
    pages_dir = os.path.join(scratch_dir, 'pages')
    images_dir = os.path.join(scratch_dir, 'images')
    figures_dir = os.path.join(scratch_dir, 'figures')

    for d in [pages_dir, images_dir, figures_dir]:
        os.makedirs(d, exist_ok=True)

    # Run Docling
    docling_result = _run_docling(pdf_path, briefing_data)

    # Process relevant pages
    relevant_start = briefing_data['relevant_pages_start']
    relevant_end = briefing_data['relevant_pages_end']
    output_pages = []

    for page_no, page_data in _iter_pages(docling_result):
        if not (relevant_start <= page_no <= relevant_end):
            continue

        md_path = os.path.join(pages_dir, f'{page_no}.md')

        if os.path.exists(md_path):
            logger.info(f"skipping already processed page {page_no}")
            output_pages.append(_load_existing_page_entry(page_no, scratch_dir))
            continue

        page_entry = _process_page(page_no, page_data, pages_dir, images_dir, figures_dir)
        output_pages.append(page_entry)
        logger.info(f"processed page {page_no}")

    output = {
        'book_id': book_id,
        'total_pages': briefing_data['total_pages'],
        'pages': output_pages,
    }

    json_path = os.path.join(scratch_dir, 'docling_output.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    return output
```

- [ ] **Step 4: Implement _run_docling() helper**

Add after `run()` in `pipeline/phase1_normalise.py`:

```python
def _run_docling(pdf_path: str, briefing_data: dict):
    """Call Docling on the full PDF. Returns the conversion result."""
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.pipeline_settings import PdfPipelineOptions
    from docling.datamodel.base_models import InputFormat

    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True
    pipeline_options.generate_page_images = True
    pipeline_options.generate_picture_images = True

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    logger.info(f"Running Docling on {pdf_path} ...")
    return converter.convert(source=pdf_path)


def _iter_pages(docling_result):
    """Yield (page_no_1indexed, page_obj) for each page in the Docling result."""
    for page_no, page in docling_result.document.pages.items():
        yield int(page_no), page


def _process_page(page_no: int, page_data, pages_dir: str, images_dir: str, figures_dir: str) -> dict:
    """Write markdown, image, and figure files for one page. Returns page entry dict."""
    # Markdown — export full doc markdown then extract page slice
    # (Docling doesn't natively export per-page markdown in all versions;
    #  we use the full doc export and tag each element by page)
    md_path = os.path.join(pages_dir, f'{page_no}.md')
    img_path = os.path.join(images_dir, f'{page_no}.png')

    # Write page image
    if page_data.image is not None:
        pil_img = page_data.image.pil_image
        pil_img.save(img_path)
    else:
        logger.warning(f"page {page_no}: no image available from Docling")

    elements = []
    return {
        'page_number': page_no,
        'markdown_path': md_path,
        'image_path': img_path,
        'elements': elements,
    }


def _load_existing_page_entry(page_no: int, scratch_dir: str) -> dict:
    """Reconstruct a page entry dict from already-written files (for resumability)."""
    pages_dir = os.path.join(scratch_dir, 'pages')
    images_dir = os.path.join(scratch_dir, 'images')
    return {
        'page_number': page_no,
        'markdown_path': os.path.join(pages_dir, f'{page_no}.md'),
        'image_path': os.path.join(images_dir, f'{page_no}.png'),
        'elements': [],
    }
```

- [ ] **Step 5: Run tests — confirm P1-02 GREEN (P1-01 may be slow)**

```bash
.venv/bin/pytest tests/test_phase1_normalise.py::test_p1_02_missing_briefing_raises_file_not_found -v
```

Expected: `PASSED`

```bash
.venv/bin/pytest tests/test_phase1_normalise.py::test_p1_01_valid_pdf_and_briefing_runs_without_error -v -s
```

Expected: `PASSED` (takes 1–5 minutes, Docling processing)

- [ ] **Step 6: Commit**

```bash
git add pipeline/phase1_normalise.py tests/test_phase1_normalise.py
git commit -m "test(phase1): P1-01 P1-02 RED→GREEN — run() skeleton + Docling integration"
```

---

### Task 4: Page filtering + JSON structure + markdown output — P1-03, P1-04, P1-05 (RED → GREEN)

**Files:**
- Modify: `pipeline/phase1_normalise.py`
- Modify: `tests/test_phase1_normalise.py`

- [ ] **Step 1: Add tests P1-03, P1-04, P1-05**

Append to `tests/test_phase1_normalise.py`:

```python
@pytest.fixture(scope="module")
def act_run_output(tmp_path_factory):
    """Run phase1 once on act_5pages.pdf, cache result for multiple tests."""
    import importlib
    scratch = tmp_path_factory.mktemp("scratch")
    os.environ["SCRATCH_DIR"] = str(scratch)
    importlib.reload(config)
    result = phase1.run("act_test", str(ACT_PDF), str(ACT_BRIEFING))
    return result, scratch


# ── TEST-P1-03 ────────────────────────────────────────────────────────────────
@pytest.mark.slow
def test_p1_03_only_relevant_pages_processed(act_run_output):
    """[INTEGRATION] only pages within relevant_pages range are written."""
    result, scratch = act_run_output
    pages_dir = scratch / "act_test" / "pages"
    md_files = list(pages_dir.glob("*.md"))
    # sample_act_briefing.md: relevant_pages 1–5, all 5 pages are relevant
    assert len(md_files) == 5
    page_numbers = {int(f.stem) for f in md_files}
    assert page_numbers == {1, 2, 3, 4, 5}


# ── TEST-P1-04 ────────────────────────────────────────────────────────────────
@pytest.mark.slow
def test_p1_04_docling_output_json_correct_structure(act_run_output):
    """[CONTRACT] docling_output.json has all required keys with correct types."""
    result, scratch = act_run_output
    json_path = scratch / "act_test" / "docling_output.json"
    assert json_path.exists()

    with open(json_path) as f:
        data = json.load(f)

    assert "book_id" in data
    assert "total_pages" in data
    assert "pages" in data
    assert isinstance(data["pages"], list)
    assert len(data["pages"]) > 0

    for page in data["pages"]:
        assert "page_number" in page
        assert "markdown_path" in page
        assert "image_path" in page
        assert "elements" in page
        assert isinstance(page["elements"], list)

        for elem in page["elements"]:
            assert "type" in elem
            assert "text" in elem
            assert "x" in elem
            assert "y" in elem
            assert "width" in elem
            assert "height" in elem
            assert elem["type"] in ("text", "figure", "table")


# ── TEST-P1-05 ────────────────────────────────────────────────────────────────
@pytest.mark.slow
def test_p1_05_markdown_is_utf8_and_non_empty(act_run_output):
    """[CONTRACT] each page .md file is valid UTF-8 and non-empty."""
    result, scratch = act_run_output
    pages_dir = scratch / "act_test" / "pages"
    md_files = list(pages_dir.glob("*.md"))
    assert len(md_files) > 0

    for md_file in md_files:
        content = md_file.read_text(encoding='utf-8')  # raises if not UTF-8
        assert len(content.strip()) > 0, f"{md_file.name} is empty"
        assert len(content.split()) >= 1, f"{md_file.name} has no words"
```

- [ ] **Step 2: Run tests — confirm RED**

```bash
.venv/bin/pytest tests/test_phase1_normalise.py::test_p1_04_docling_output_json_correct_structure -v
```

Expected: `FAILED` — elements list is empty, or missing keys.

- [ ] **Step 3: Implement element extraction and markdown writing in _process_page()**

Replace `_process_page()` in `pipeline/phase1_normalise.py` with:

```python
def _process_page(page_no: int, page_data, pages_dir: str, images_dir: str, figures_dir: str) -> dict:
    """Write markdown, image, and figure files for one page. Returns page entry dict."""
    from docling.datamodel.base_models import DocItemLabel

    md_path = os.path.join(pages_dir, f'{page_no}.md')
    img_path = os.path.join(images_dir, f'{page_no}.png')

    # Page image
    if page_data.image is not None:
        page_data.image.pil_image.save(img_path)
    else:
        logger.warning(f"page {page_no}: no image available")

    return {
        'page_number': page_no,
        'markdown_path': md_path,
        'image_path': img_path,
        'elements': [],  # populated in Task 4 Step 4
    }
```

Also update `run()` to write per-page markdown after Docling processes all pages. Add this block in `run()` after `docling_result = _run_docling(...)`:

```python
    # Export full document markdown then split per page
    _write_per_page_markdown(docling_result, briefing_data, pages_dir,
                              images_dir, figures_dir, output_pages)
```

Add the new function:

```python
def _write_per_page_markdown(docling_result, briefing_data: dict,
                              pages_dir: str, images_dir: str,
                              figures_dir: str, output_pages: list) -> None:
    """
    Extract elements per page from docling_result, write markdown files,
    and populate output_pages[].elements with bounding box data.
    """
    from docling.datamodel.base_models import DocItemLabel

    # Build page_no → list of (type, text, bbox) map
    page_elements: dict[int, list] = {}

    for item, level in docling_result.document.iterate_items():
        if not item.prov:
            continue
        prov = item.prov[0]
        page_no = int(prov.page_no)
        bbox = prov.bbox

        elem_type = "text"
        if item.label in (DocItemLabel.PICTURE,):
            elem_type = "figure"
        elif item.label in (DocItemLabel.TABLE,):
            elem_type = "table"

        elem = {
            "type": elem_type,
            "text": item.text if hasattr(item, 'text') and item.text else "",
            "x": round(float(bbox.l), 2),
            "y": round(float(bbox.t), 2),
            "width": round(float(bbox.r - bbox.l), 2),
            "height": round(float(bbox.b - bbox.t), 2),
        }

        page_elements.setdefault(page_no, []).append(elem)

    # Write per-page markdown + update output_pages elements
    full_md = docling_result.document.export_to_markdown()

    for page_entry in output_pages:
        pn = page_entry['page_number']
        elems = page_elements.get(pn, [])
        page_entry['elements'] = elems

        # Write markdown: use full doc export (Docling doesn't split natively)
        # Tag page content by filtering elements on this page_no
        page_md_lines = [f"## Page {pn}\n"]
        for elem in elems:
            if elem['type'] == 'text' and elem['text']:
                page_md_lines.append(elem['text'])
        page_md = '\n'.join(page_md_lines)

        md_path = page_entry['markdown_path']
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(page_md if page_md.strip() else full_md)
```

- [ ] **Step 4: Run tests — confirm P1-03, P1-04, P1-05 GREEN**

```bash
.venv/bin/pytest tests/test_phase1_normalise.py::test_p1_03_only_relevant_pages_processed \
                 tests/test_phase1_normalise.py::test_p1_04_docling_output_json_correct_structure \
                 tests/test_phase1_normalise.py::test_p1_05_markdown_is_utf8_and_non_empty -v
```

Expected: all 3 `PASSED`

- [ ] **Step 5: Commit**

```bash
git add pipeline/phase1_normalise.py tests/test_phase1_normalise.py
git commit -m "test(phase1): P1-03 P1-04 P1-05 RED→GREEN — elements, markdown, JSON structure"
```

---

### Task 5: Figure extraction — P1-06 (RED → GREEN)

**Files:**
- Modify: `pipeline/phase1_normalise.py`
- Modify: `tests/test_phase1_normalise.py`

- [ ] **Step 1: Add test P1-06**

Append to `tests/test_phase1_normalise.py`:

```python
# ── TEST-P1-06 ────────────────────────────────────────────────────────────────
@pytest.mark.slow
def test_p1_06_figures_extracted(act_run_output):
    """[INTEGRATION] figure PNGs extracted when present, linked in JSON."""
    result, scratch = act_run_output
    figures_dir = scratch / "act_test" / "figures"

    # ACT maths pages 45-49 contain geometry figures
    assert figures_dir.exists()
    figure_files = list(figures_dir.glob("*.png"))
    assert len(figure_files) > 0, "Expected at least one figure from ACT maths pages"

    # Check JSON links figures correctly
    json_path = scratch / "act_test" / "docling_output.json"
    with open(json_path) as f:
        data = json.load(f)

    figure_elements = [
        elem
        for page in data["pages"]
        for elem in page["elements"]
        if elem["type"] == "figure"
    ]
    assert len(figure_elements) > 0

    for fig_elem in figure_elements:
        assert "figure_path" in fig_elem
        assert os.path.exists(fig_elem["figure_path"]), \
            f"Figure file missing: {fig_elem['figure_path']}"
```

- [ ] **Step 2: Run test — confirm RED**

```bash
.venv/bin/pytest tests/test_phase1_normalise.py::test_p1_06_figures_extracted -v
```

Expected: `FAILED` — figure_elements list empty or `figure_path` key missing.

- [ ] **Step 3: Implement figure image extraction**

Update `_write_per_page_markdown()` in `pipeline/phase1_normalise.py`. Replace the element building block with:

```python
    for item, level in docling_result.document.iterate_items():
        if not item.prov:
            continue
        prov = item.prov[0]
        page_no = int(prov.page_no)
        bbox = prov.bbox

        elem_type = "text"
        figure_path = None

        if item.label in (DocItemLabel.PICTURE,):
            elem_type = "figure"
            # Extract and save figure image
            fig_index = len([
                e for e in page_elements.get(page_no, [])
                if e['type'] == 'figure'
            ]) + 1
            fig_filename = f"{page_no}_fig_{fig_index}.png"
            fig_path = os.path.join(figures_dir, fig_filename)

            if hasattr(item, 'image') and item.image is not None:
                try:
                    item.image.pil_image.save(fig_path)
                    figure_path = fig_path
                except Exception as e:
                    logger.warning(f"Could not save figure {fig_filename}: {e}")

        elif item.label in (DocItemLabel.TABLE,):
            elem_type = "table"

        elem = {
            "type": elem_type,
            "text": item.text if hasattr(item, 'text') and item.text else "",
            "x": round(float(bbox.l), 2),
            "y": round(float(bbox.t), 2),
            "width": round(float(bbox.r - bbox.l), 2),
            "height": round(float(bbox.b - bbox.t), 2),
        }
        if figure_path:
            elem["figure_path"] = figure_path

        page_elements.setdefault(page_no, []).append(elem)
```

- [ ] **Step 4: Run test — confirm GREEN**

```bash
.venv/bin/pytest tests/test_phase1_normalise.py::test_p1_06_figures_extracted -v
```

Expected: `PASSED`

- [ ] **Step 5: Commit**

```bash
git add pipeline/phase1_normalise.py tests/test_phase1_normalise.py
git commit -m "test(phase1): P1-06 RED→GREEN — figure PNG extraction"
```

---

### Task 6: Resumability — P1-07 (RED → GREEN)

**Files:**
- Modify: `tests/test_phase1_normalise.py`

- [ ] **Step 1: Add test P1-07**

Append to `tests/test_phase1_normalise.py`:

```python
# ── TEST-P1-07 ────────────────────────────────────────────────────────────────
@pytest.mark.slow
def test_p1_07_resumable_skips_existing_pages(tmp_path, monkeypatch, caplog):
    """[UNIT] second run skips already-processed pages and is faster."""
    import importlib, logging
    monkeypatch.setenv("SCRATCH_DIR", str(tmp_path))
    importlib.reload(config)

    # First run
    t0 = time.time()
    phase1.run("act_resume", str(ACT_PDF), str(ACT_BRIEFING))
    first_run_time = time.time() - t0

    # Second run — should skip all pages
    with caplog.at_level(logging.INFO, logger="pipeline.phase1_normalise"):
        t1 = time.time()
        phase1.run("act_resume", str(ACT_PDF), str(ACT_BRIEFING))
        second_run_time = time.time() - t1

    # Second run must log "skipping" for each page
    skip_logs = [r for r in caplog.records if "skipping already processed" in r.message]
    assert len(skip_logs) == 5, f"Expected 5 skip logs, got {len(skip_logs)}"

    # Second run must be significantly faster (no Docling re-processing)
    assert second_run_time < first_run_time * 0.5, \
        f"Second run ({second_run_time:.1f}s) not faster than half of first ({first_run_time:.1f}s)"
```

- [ ] **Step 2: Run test — confirm RED**

```bash
.venv/bin/pytest tests/test_phase1_normalise.py::test_p1_07_resumable_skips_existing_pages -v
```

Expected: `FAILED` — skip logs count wrong, or second run not faster.

- [ ] **Step 3: Fix resumability — skip Docling call entirely on second run**

Update `run()` in `pipeline/phase1_normalise.py`. Add a check before calling Docling:

```python
    # Check if all relevant pages already processed — skip Docling entirely
    relevant_pages = list(range(
        briefing_data['relevant_pages_start'],
        briefing_data['relevant_pages_end'] + 1
    ))
    all_done = all(
        os.path.exists(os.path.join(pages_dir, f'{pn}.md'))
        for pn in relevant_pages
    )

    if all_done:
        logger.info("All pages already processed — loading from existing files")
        output_pages = [_load_existing_page_entry(pn, scratch_dir) for pn in relevant_pages]
        for pn in relevant_pages:
            logger.info(f"skipping already processed page {pn}")
    else:
        # Run Docling
        docling_result = _run_docling(pdf_path, briefing_data)
        output_pages = []

        for page_no, page_data in _iter_pages(docling_result):
            if not (briefing_data['relevant_pages_start'] <= page_no <= briefing_data['relevant_pages_end']):
                continue

            md_path = os.path.join(pages_dir, f'{page_no}.md')
            if os.path.exists(md_path):
                logger.info(f"skipping already processed page {page_no}")
                output_pages.append(_load_existing_page_entry(page_no, scratch_dir))
                continue

            page_entry = _process_page(page_no, page_data, pages_dir, images_dir, figures_dir)
            output_pages.append(page_entry)
            logger.info(f"processed page {page_no}")

        _write_per_page_markdown(docling_result, briefing_data,
                                  pages_dir, images_dir, figures_dir, output_pages)
```

- [ ] **Step 4: Run test — confirm GREEN**

```bash
.venv/bin/pytest tests/test_phase1_normalise.py::test_p1_07_resumable_skips_existing_pages -v
```

Expected: `PASSED`

- [ ] **Step 5: Commit**

```bash
git add pipeline/phase1_normalise.py tests/test_phase1_normalise.py
git commit -m "test(phase1): P1-07 RED→GREEN — resumability skips Docling on re-run"
```

---

### Task 7: OCR on scanned PDF — P1-08 (RED → GREEN)

**Files:**
- Modify: `tests/test_phase1_normalise.py`

- [ ] **Step 1: Add test P1-08**

Append to `tests/test_phase1_normalise.py`:

```python
# ── TEST-P1-08 ────────────────────────────────────────────────────────────────
@pytest.mark.slow
def test_p1_08_scanned_pdf_ocr_works(tmp_path, monkeypatch):
    """[EDGE] scanned (image-based) PDF: Docling applies OCR, markdown non-empty."""
    import importlib
    monkeypatch.setenv("SCRATCH_DIR", str(tmp_path))
    importlib.reload(config)

    result = phase1.run("rsaggarwal_test", str(SCANNED_PDF), str(SCANNED_BRIEFING))

    assert isinstance(result, dict)
    pages_dir = tmp_path / "rsaggarwal_test" / "pages"
    md_files = list(pages_dir.glob("*.md"))
    assert len(md_files) == 3, f"Expected 3 pages, got {len(md_files)}"

    for md_file in md_files:
        content = md_file.read_text(encoding='utf-8')
        assert len(content.strip()) > 0, f"OCR produced empty markdown for {md_file.name}"
```

- [ ] **Step 2: Run test — confirm RED**

```bash
.venv/bin/pytest tests/test_phase1_normalise.py::test_p1_08_scanned_pdf_ocr_works -v
```

Expected: `FAILED` — or possibly passes already if Docling handles OCR automatically. Note the result.

- [ ] **Step 3: Verify and fix if needed**

If P1-08 is already `PASSED` (Docling handles OCR transparently with `do_ocr=True`), no code change needed. If `FAILED` because markdown is empty, check that `pipeline_options.do_ocr = True` is set in `_run_docling()` — it is, per Task 3. If still failing, add:

```python
pipeline_options.force_full_page_ocr = True  # force OCR even on born-digital
```

Note: only add `force_full_page_ocr` if the test fails; it slows down born-digital processing.

- [ ] **Step 4: Run full suite — confirm all 9 GREEN**

```bash
.venv/bin/pytest tests/test_phase1_normalise.py -v
```

Expected: all 9 tests `PASSED`. Total time ~5–15 minutes (Docling is slow).

- [ ] **Step 5: Commit**

```bash
git add pipeline/phase1_normalise.py tests/test_phase1_normalise.py
git commit -m "test(phase1): P1-08 RED→GREEN — OCR on scanned PDF, all 9 tests passing"
```

---

### Task 8: Full suite verification + push + merge to main

**Files:** none (git operations only)

- [ ] **Step 1: Run complete test suite (briefing + phase1)**

```bash
.venv/bin/pytest tests/test_briefing.py tests/test_phase1_normalise.py -v
```

Expected: 15 + 9 = 24 tests, all `PASSED`.

- [ ] **Step 2: Push feature branch**

```bash
git push -u origin feature/phase1-normalise
```

- [ ] **Step 3: Merge to main (all tests green)**

```bash
git checkout main
git merge feature/phase1-normalise
git push origin main
```

- [ ] **Step 4: Delete feature branch**

```bash
git push origin --delete feature/phase1-normalise
git branch -d feature/phase1-normalise
```

- [ ] **Step 5: Update CLAUDE.md progress checklist**

In `CLAUDE.md`, mark phase1 done:

```markdown
- [x] phase1_normalise.py written and tested
```

```bash
git add CLAUDE.md
git commit -m "chore: mark phase1 complete in progress checklist"
git push origin main
```

---

## Self-Review Notes

- ✅ All 9 TESTS.md tests covered (P1-01 through P1-09)
- ✅ TDD enforced — every task writes RED test before implementation
- ✅ No hardcoded paths — all from `config.py`
- ✅ `briefing_path` optional param allows tests to pass explicit briefing path
- ✅ Resumability skips Docling entirely when all pages done (not just per-page check)
- ✅ Figure extraction saves PNG + adds `figure_path` to element dict
- ✅ `.gitignore` exception for test fixture PDFs in Task 0
- ⚠️  Docling API (`item.image.pil_image`, `page_data.image.pil_image`) may need adjustment during Task 3 depending on exact Docling 2.x installed version — tests will reveal this
