# Phase 2 — Classify Subject: Implementation Plan
**Date:** 2026-05-15
**Status:** Approved
**Branch:** feature/phase2-classify

---

## Overview

Build `pipeline/phase2_classify.py` — reads Docling output, classifies each page's subject using Gemini Flash (with briefing override for known ranges), writes `page_map.json`.

API: `google-generativeai` SDK, model `gemini-2.0-flash`, key from `GEMINI_KEY` env var.
Tests needing Gemini: marked `@pytest.mark.slow` + skip if `GEMINI_KEY` not set.

---

## Task 0 — Branch + deps + config
**Files:** `requirements.txt`, `config.py`, `.env.example`
**Time:** ~3 min

1. `git checkout -b feature/phase2-classify`
2. `.venv/bin/pip install google-generativeai`
3. Add `google-generativeai>=0.8.0` to `requirements.txt`
4. Add to `config.py`:
   - `GEMINI_KEY = os.getenv("GEMINI_KEY", "")`
   - `GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")`
5. Add to `.env.example`:
   - `GEMINI_KEY=your_gemini_api_key_here`
   - `GEMINI_MODEL=gemini-2.0-flash`
6. Commit: `chore(phase2): branch setup, google-generativeai dep, config`

---

## Task 1 — Unit tests (no API) RED→GREEN
**Tests:** P2-11, P2-06
**Files:** `tests/test_phase2_classify.py`, `pipeline/phase2_classify.py`
**Time:** ~5 min

These tests must pass with NO Gemini key set.

### P2-11: empty markdown raises ValueError

```python
def test_p2_11_empty_markdown_raises_value_error():
    """[UNIT] classify_page() raises ValueError for empty markdown."""
    import pipeline.phase2_classify as p2
    import pipeline.briefing as b
    data = b.load(str(FIXTURES / "sample_briefing.md"))
    with pytest.raises(ValueError, match="empty"):
        p2.classify_page("", data, page_number=100)
```

### P2-06: briefing override returns subject without API call

```python
def test_p2_06_briefing_override_skips_api():
    """[UNIT] classify_page() returns briefing subject when page in coverage range."""
    import pipeline.phase2_classify as p2
    import pipeline.briefing as b
    data = b.load(str(FIXTURES / "sample_briefing.md"))
    # sample_briefing.md: pages 45–120 = logical_reasoning
    result = p2.classify_page("some content here", data, page_number=80)
    assert result["subject"] == "logical_reasoning"
    assert result["briefing_override"] is True
    assert result["confidence"] == 1.0
    assert "briefing" in result["reasoning"].lower()
```

### Minimal implementation to pass both:

```python
VALID_SUBJECTS = {
    "quantitative_reasoning", "logical_reasoning", "science_reasoning",
    "reading_comprehension", "writing", "answer_key", "skip",
}

def classify_page(markdown: str, briefing_data: dict, page_number: int = None) -> dict:
    if not markdown or not markdown.strip():
        raise ValueError("Cannot classify empty page")
    
    # Briefing override: if page is in a known coverage range, use it directly
    if page_number is not None:
        subject = briefing_module.get_subject_for_page(briefing_data, page_number)
        if subject is not None:  # None means outside all ranges
            return {
                "subject": subject,
                "confidence": 1.0,
                "is_question_page": subject not in ("answer_key", "skip"),
                "reasoning": f"Briefing override: page {page_number} is in coverage range ({subject})",
                "needs_manual_review": False,
                "briefing_override": True,
            }
    
    # Gemini path (not yet implemented)
    raise NotImplementedError("Gemini path not yet implemented")
```

Verify P2-11 and P2-06 RED→GREEN. P2-07 will raise NotImplementedError — expected.

Commit: `test(phase2): P2-11 P2-06 unit tests RED→GREEN, briefing override`

---

## Task 2 — Gemini integration + schema tests P2-02, P2-03
**Tests:** P2-02, P2-03
**Files:** `pipeline/phase2_classify.py`, `tests/test_phase2_classify.py`
**Time:** ~8 min (includes real API call)

### Classification prompt (from CLAUDE.md, adapted for Gemini):

```
You are classifying pages from Australian selective school exam prep books.

BOOK CONTEXT (from briefing file):
{briefing_context}

Classify this page into EXACTLY ONE of:
- quantitative_reasoning
- logical_reasoning
- science_reasoning
- reading_comprehension
- writing
- answer_key (page is an answer grid or answer listing)
- skip (cover, contents, index, ads, instructions)

Return ONLY valid JSON, no markdown, no explanation:
{
  "subject": "<subject>",
  "is_question_page": true,
  "confidence": 0.0-1.0,
  "reasoning": "<one sentence>"
}

PAGE CONTENT:
{page_markdown}
```

### Gemini API call:

```python
import google.generativeai as genai

def _call_gemini(markdown: str, briefing_data: dict) -> dict:
    key = os.environ.get("GEMINI_KEY") or config.GEMINI_KEY
    if not key:
        raise RuntimeError("GEMINI_KEY not set — cannot classify without API key")
    
    genai.configure(api_key=key)
    model = genai.GenerativeModel(config.GEMINI_MODEL)
    
    prompt = _build_prompt(markdown, briefing_data)
    response = model.generate_content(prompt)
    return _parse_response(response.text)

def _parse_response(text: str) -> dict:
    # Strip markdown fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text.strip())
    text = re.sub(r"\s*```$", "", text.strip())
    data = json.loads(text)
    
    subject = data.get("subject", "")
    if subject not in VALID_SUBJECTS:
        raise ValueError(f"Gemini returned invalid subject: {subject!r}")
    
    return {
        "subject": subject,
        "confidence": float(data.get("confidence", 0.0)),
        "is_question_page": bool(data.get("is_question_page", True)),
        "reasoning": str(data.get("reasoning", "")),
        "needs_manual_review": float(data.get("confidence", 0.0)) < 0.5,
        "briefing_override": False,
    }
```

### Tests P2-02 and P2-03:

```python
GEMINI_AVAILABLE = bool(os.environ.get("GEMINI_KEY"))

@pytest.mark.slow
@pytest.mark.skipif(not GEMINI_AVAILABLE, reason="GEMINI_KEY not set")
def test_p2_02_result_has_required_fields_correct_types():
    """[CONTRACT] classify_page() result always has required fields with correct types."""
    import pipeline.phase2_classify as p2
    import pipeline.briefing as b
    data = b.load(str(FIXTURES / "sample_briefing.md"))
    content = (FIXTURES / "sample_qr_page.md").read_text()
    result = p2.classify_page(content, data, page_number=999)  # outside range → API
    assert isinstance(result["subject"], str)
    assert isinstance(result["confidence"], float)
    assert 0.0 <= result["confidence"] <= 1.0
    assert isinstance(result["is_question_page"], bool)
    assert isinstance(result["reasoning"], str) and result["reasoning"]
    assert isinstance(result["needs_manual_review"], bool)
    assert isinstance(result["briefing_override"], bool)

@pytest.mark.slow
@pytest.mark.skipif(not GEMINI_AVAILABLE, reason="GEMINI_KEY not set")
def test_p2_03_subject_always_valid():
    """[CONTRACT] subject is always one of 7 valid return values."""
    import pipeline.phase2_classify as p2
    import pipeline.briefing as b
    valid = {"quantitative_reasoning","logical_reasoning","science_reasoning",
             "reading_comprehension","writing","answer_key","skip"}
    data = b.load(str(FIXTURES / "sample_briefing.md"))
    for fname in ["sample_qr_page.md","sample_lr_page.md","sample_sr_page.md",
                  "sample_rc_page.md","sample_wr_page.md"]:
        content = (FIXTURES / fname).read_text()
        result = p2.classify_page(content, data, page_number=999)
        assert result["subject"] in valid, f"{fname}: invalid subject {result['subject']!r}"
```

Commit: `feat(phase2): Gemini integration + P2-02 P2-03 RED→GREEN`

---

## Task 3 — Accuracy tests P2-01, P2-04, P2-05
**Tests:** P2-01, P2-04, P2-05
**Files:** `tests/test_phase2_classify.py`
**Time:** ~8 min (real API calls × 7 pages)

```python
@pytest.mark.slow
@pytest.mark.skipif(not GEMINI_AVAILABLE, reason="GEMINI_KEY not set")
@pytest.mark.parametrize("fname,expected_subject", [
    ("sample_qr_page.md",  "quantitative_reasoning"),
    ("sample_lr_page.md",  "logical_reasoning"),
    ("sample_sr_page.md",  "science_reasoning"),
    ("sample_rc_page.md",  "reading_comprehension"),
    ("sample_wr_page.md",  "writing"),
])
def test_p2_01_correct_subject_for_each_fixture(fname, expected_subject):
    """[CONTRACT] classifier returns correct subject for each of the 5 subjects."""
    import pipeline.phase2_classify as p2
    import pipeline.briefing as b
    data = b.load(str(FIXTURES / "sample_briefing.md"))
    content = (FIXTURES / fname).read_text()
    result = p2.classify_page(content, data, page_number=999)
    assert result["subject"] == expected_subject, (
        f"{fname}: expected {expected_subject}, got {result['subject']!r}\n"
        f"Reasoning: {result['reasoning']}"
    )

@pytest.mark.slow
@pytest.mark.skipif(not GEMINI_AVAILABLE, reason="GEMINI_KEY not set")
def test_p2_04_answer_key_page():
    """[EDGE] answer key page returns 'answer_key'."""
    import pipeline.phase2_classify as p2
    import pipeline.briefing as b
    data = b.load(str(FIXTURES / "sample_briefing.md"))
    content = (FIXTURES / "sample_answer_key_page.md").read_text()
    result = p2.classify_page(content, data, page_number=999)
    assert result["subject"] == "answer_key"

@pytest.mark.slow
@pytest.mark.skipif(not GEMINI_AVAILABLE, reason="GEMINI_KEY not set")
def test_p2_05_theory_page_is_question_page_false():
    """[EDGE] theory/explanation page sets is_question_page=False."""
    import pipeline.phase2_classify as p2
    import pipeline.briefing as b
    data = b.load(str(FIXTURES / "sample_briefing.md"))
    content = (FIXTURES / "sample_theory_page.md").read_text()
    result = p2.classify_page(content, data, page_number=999)
    assert result["is_question_page"] is False
    assert result["subject"] in {
        "quantitative_reasoning","logical_reasoning","science_reasoning",
        "reading_comprehension","writing"
    }
```

If any accuracy test fails, inspect the prompt and adjust the prompt wording. Do NOT change the fixture files.

Commit: `test(phase2): accuracy tests P2-01 P2-04 P2-05 RED→GREEN`

---

## Task 4 — Garbled page + outside-range + P2-07, P2-10
**Tests:** P2-07, P2-10
**Files:** `tests/test_phase2_classify.py`
**Time:** ~5 min

```python
@pytest.mark.slow
@pytest.mark.skipif(not GEMINI_AVAILABLE, reason="GEMINI_KEY not set")
def test_p2_07_outside_briefing_range_uses_api():
    """[UNIT] page outside all briefing ranges uses API, not briefing override."""
    import pipeline.phase2_classify as p2
    import pipeline.briefing as b
    data = b.load(str(FIXTURES / "sample_briefing.md"))
    content = (FIXTURES / "sample_qr_page.md").read_text()
    result = p2.classify_page(content, data, page_number=9999)
    assert result["briefing_override"] is False

@pytest.mark.slow
@pytest.mark.skipif(not GEMINI_AVAILABLE, reason="GEMINI_KEY not set")
def test_p2_10_garbled_page_flags_low_confidence():
    """[EDGE] garbled OCR page → confidence < 0.5, needs_manual_review=True."""
    import pipeline.phase2_classify as p2
    import pipeline.briefing as b
    data = b.load(str(FIXTURES / "sample_briefing.md"))
    content = (FIXTURES / "sample_garbled_page.md").read_text()
    result = p2.classify_page(content, data, page_number=999)
    assert result["confidence"] < 0.5, (
        f"Expected low confidence for garbled page, got {result['confidence']}"
    )
    assert result["needs_manual_review"] is True
```

Note: `sample_garbled_page.md` already exists in fixtures. Verify its content is genuinely garbled (random characters, broken OCR text). If not garbled enough to produce low confidence, update the fixture.

Commit: `test(phase2): P2-07 P2-10 RED→GREEN`

---

## Task 5 — run() + page_map.json + P2-08 + P2-09
**Tests:** P2-08, P2-09
**Files:** `pipeline/phase2_classify.py`, `tests/test_phase2_classify.py`
**Time:** ~8 min

### run() implementation:

```python
def run(book_id: str, scratch_dir: str = None) -> dict:
    if scratch_dir is None:
        scratch_dir = config.SCRATCH_DIR
    
    book_scratch = os.path.join(scratch_dir, book_id)
    docling_json = os.path.join(book_scratch, "docling_output.json")
    page_map_path = os.path.join(book_scratch, "page_map.json")
    
    with open(docling_json) as f:
        docling = json.load(f)
    
    briefing_path = _find_briefing(book_id)
    briefing_data = briefing_module.load(briefing_path)
    
    # Load existing page_map (resumability)
    if os.path.exists(page_map_path):
        with open(page_map_path) as f:
            page_map = json.load(f)
    else:
        page_map = {"book_id": book_id, "pages": []}
    
    classified_pages = {p["page_number"] for p in page_map["pages"]}
    
    for page_entry in docling["pages"]:
        page_n = page_entry["page_number"]
        if page_n in classified_pages:
            logger.info(f"Skipping page {page_n} (already classified)")
            continue
        
        md_path = page_entry["markdown_path"]
        if not os.path.exists(md_path):
            logger.warning(f"Page {page_n}: markdown file missing, skipping")
            continue
        
        with open(md_path, encoding="utf-8") as f:
            markdown = f.read()
        
        if not markdown.strip():
            logger.warning(f"Page {page_n}: empty markdown, skipping")
            continue
        
        result = classify_page(markdown, briefing_data, page_number=page_n)
        page_map["pages"].append({"page_number": page_n, **result})
        
        # Write after each page (resumable on crash)
        with open(page_map_path, "w") as f:
            json.dump(page_map, f, indent=2)
        
        logger.info(f"Classified page {page_n}: {result['subject']} (conf={result['confidence']:.2f})")
        time.sleep(config.API_DELAY_SECONDS)
    
    return page_map
```

run() needs `_find_briefing(book_id)` — looks for briefing in `PDF_DIR/<book_id>.md`.

### Tests:

```python
@pytest.mark.slow
@pytest.mark.skipif(not GEMINI_AVAILABLE, reason="GEMINI_KEY not set")
def test_p2_08_page_map_json_written_correctly(tmp_path):
    """[INTEGRATION] run() writes page_map.json with correct structure."""
    # Use the act_5pages fixture (phase1 output already tested)
    # We need a phase1 output to work from — run phase1 first
    import pipeline.phase1_normalise as p1
    import pipeline.phase2_classify as p2
    
    p1.run(
        book_id="act_5pages",
        pdf_path=str(FIXTURES / "act_5pages.pdf"),
        scratch_dir=str(tmp_path),
        briefing_path=str(FIXTURES / "sample_act_briefing.md"),
    )
    
    result = p2.run(
        book_id="act_5pages",
        scratch_dir=str(tmp_path),
        briefing_path=str(FIXTURES / "sample_act_briefing.md"),
    )
    
    page_map_path = tmp_path / "act_5pages" / "page_map.json"
    assert page_map_path.exists()
    
    assert result["book_id"] == "act_5pages"
    assert len(result["pages"]) > 0
    for page in result["pages"]:
        assert "page_number" in page
        assert "subject" in page
        assert "confidence" in page
        assert "is_question_page" in page
        assert isinstance(page["is_question_page"], bool)

@pytest.mark.slow
def test_p2_09_resumable_skips_classified_pages(tmp_path):
    """[UNIT] run() skips pages already in page_map.json."""
    import json
    import pipeline.phase2_classify as p2
    import pipeline.phase1_normalise as p1
    
    # Run phase1 to produce docling_output.json
    p1.run(
        book_id="act_5pages",
        pdf_path=str(FIXTURES / "act_5pages.pdf"),
        scratch_dir=str(tmp_path),
        briefing_path=str(FIXTURES / "sample_act_briefing.md"),
    )
    
    # Pre-populate page_map.json with a fake classification for page 1
    pre_classified = {
        "book_id": "act_5pages",
        "pages": [
            {"page_number": 1, "subject": "quantitative_reasoning",
             "confidence": 1.0, "is_question_page": True,
             "reasoning": "pre-classified", "needs_manual_review": False,
             "briefing_override": True}
        ]
    }
    page_map_path = tmp_path / "act_5pages" / "page_map.json"
    page_map_path.write_text(json.dumps(pre_classified))
    
    # run() should not re-classify page 1
    # Since all 5 pages have briefing override (sample_act_briefing covers 1-5),
    # this is a unit test that doesn't actually call Gemini
    result = p2.run(
        book_id="act_5pages",
        scratch_dir=str(tmp_path),
        briefing_path=str(FIXTURES / "sample_act_briefing.md"),
    )
    
    # Page 1 should still have "pre-classified" reasoning (not overwritten)
    page1 = next(p for p in result["pages"] if p["page_number"] == 1)
    assert page1["reasoning"] == "pre-classified", "Page 1 was re-classified (should be skipped)"
```

Note: `run()` needs a `briefing_path` parameter for tests (same pattern as phase1).

Commit: `feat(phase2): run() + page_map.json + P2-08 P2-09 RED→GREEN`

---

## Task 6 — Full suite + push + merge
**Time:** ~5 min

1. Run full suite: `pytest tests/test_briefing.py tests/test_phase1_normalise.py tests/test_phase2_classify.py -v`
2. Verify: 11 phase2 tests + prior tests all GREEN (or SKIP for API tests when key absent)
3. `git push -u origin feature/phase2-classify`
4. `git checkout main && git merge feature/phase2-classify --no-ff -m "feat(phase2): subject classifier complete — 11 tests GREEN"`
5. `git push origin main`

---

## Files Changed

| File | Action |
|---|---|
| `pipeline/phase2_classify.py` | Implement |
| `tests/test_phase2_classify.py` | Implement |
| `requirements.txt` | Add `google-generativeai>=0.8.0` |
| `config.py` | Add `GEMINI_KEY`, `GEMINI_MODEL` |
| `.env.example` | Add `GEMINI_KEY`, `GEMINI_MODEL` |
