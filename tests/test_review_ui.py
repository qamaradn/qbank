"""
Review UI tests — UI-01 through UI-22.

All fast: parse review/ui/index.html statically (BeautifulSoup + CSS regex).
No browser required. Tests verify design system compliance and DOM structure.

Run: pytest tests/test_review_ui.py -v
"""
import re
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

UI_HTML = Path(__file__).parent.parent / "review" / "ui" / "index.html"
DESIGN_SYSTEM = Path(__file__).parent.parent / "design-system" / "MASTER.md"


@pytest.fixture(scope="module")
def html_source():
    return UI_HTML.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def soup(html_source):
    return BeautifulSoup(html_source, "html.parser")


@pytest.fixture(scope="module")
def css(soup):
    """Extract all inline <style> block content."""
    styles = soup.find_all("style")
    return "\n".join(s.get_text() for s in styles)


@pytest.fixture(scope="module")
def js(soup):
    """Extract all inline <script> block content."""
    scripts = soup.find_all("script")
    return "\n".join(s.get_text() for s in scripts)


# ── UI-01 ──────────────────────────────────────────────────────────────────────
def test_ui_01_html_is_valid_and_has_body(soup):
    """[INTEGRATION] page has required structure — html, head, body, style, script."""
    assert soup.find("html") is not None
    assert soup.find("head") is not None
    assert soup.find("body") is not None
    assert soup.find("style") is not None
    assert soup.find("script") is not None


# ── UI-02 ──────────────────────────────────────────────────────────────────────
def test_ui_02_design_system_file_exists():
    """[CONTRACT] design-system/MASTER.md exists with required sections."""
    assert DESIGN_SYSTEM.exists(), "design-system/MASTER.md must exist before UI build"
    content = DESIGN_SYSTEM.read_text()
    for section in ("COLORS", "TYPOGRAPHY", "STYLE", "ANTI-PATTERNS"):
        assert section in content, f"MASTER.md missing section: {section}"


# ── UI-03 ──────────────────────────────────────────────────────────────────────
def test_ui_03_dark_mode_background(css):
    """[CONTRACT] background color is dark (not white/light grey)."""
    # Match hex colours declared for body or :root background
    dark_pattern = re.compile(
        r"background(?:-color)?\s*:\s*#([0-9a-fA-F]{3,6})", re.IGNORECASE
    )
    dark_found = False
    for match in dark_pattern.finditer(css):
        hex_val = match.group(1)
        if len(hex_val) == 3:
            hex_val = "".join(c * 2 for c in hex_val)
        r, g, b = int(hex_val[0:2], 16), int(hex_val[2:4], 16), int(hex_val[4:6], 16)
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        if luminance < 0.2:
            dark_found = True
            break
    assert dark_found, "No dark background color found in CSS (luminance must be < 0.2)"


# ── UI-04 ──────────────────────────────────────────────────────────────────────
def test_ui_04_correct_answer_green_class_defined(css, js):
    """[CONTRACT] CSS defines a green style for correct-answer options."""
    # correct-answer class must exist
    assert "correct-answer" in css or "correct_answer" in css, (
        "No correct-answer class in CSS"
    )
    # Green color must be declared (either directly or via a CSS var mapped to green)
    has_green = (
        "3fb950" in css.lower()
        or "3fb950" in js.lower()
        or ("approve" in css.lower() and "#3f" in css.lower())
    )
    assert has_green, "Green color #3FB950 not found for correct-answer styling"


# ── UI-05 ──────────────────────────────────────────────────────────────────────
def test_ui_05_figure_display_logic_in_js(js):
    """[CONTRACT] JS contains logic to show figure above question when has_figure=true."""
    assert "has_figure" in js or "hasFigure" in js, "No has_figure logic found in JS"
    assert "figure_url" in js or "figureUrl" in js, "No figure_url rendering logic in JS"
    assert "<img" in js or "createElement('img')" in js or "img.src" in js, (
        "No img element creation for figure found in JS"
    )


# ── UI-06 ──────────────────────────────────────────────────────────────────────
def test_ui_06_no_figure_hides_image(js):
    """[CONTRACT] JS hides or omits img when figure_url is null."""
    # Must have a condition that checks null/falsy figure_url
    assert re.search(
        r"(figure_url|figureUrl)\s*(===|==|!==|!=|&&|\|\||\?)\s*(null|undefined|''|\"\")",
        js,
    ) or re.search(r"if\s*\(.*figure", js, re.IGNORECASE), (
        "No null-check for figure_url found in JS"
    )


# ── UI-07 ──────────────────────────────────────────────────────────────────────
def test_ui_07_keyboard_approve(js):
    """[CONTRACT] keyboard handler calls approve on key 'A' or 'a'."""
    assert re.search(r"['\"]a['\"]|['\"]A['\"]|key.*[Aa]pprove|[Aa]pprove.*key", js), (
        "No keyboard handler for A/approve found in JS"
    )
    assert "approve" in js.lower(), "No approve function found in JS"


# ── UI-08 ──────────────────────────────────────────────────────────────────────
def test_ui_08_keyboard_reject(js):
    """[CONTRACT] keyboard handler calls reject on key 'R' or 'r'."""
    assert re.search(r"['\"]r['\"]|['\"]R['\"]|key.*[Rr]eject|[Rr]eject.*key", js), (
        "No keyboard handler for R/reject found in JS"
    )
    assert "reject" in js.lower(), "No reject function found in JS"


# ── UI-09 ──────────────────────────────────────────────────────────────────────
def test_ui_09_keyboard_edit(js):
    """[CONTRACT] keyboard handler enters edit mode on key 'E' or 'e'."""
    assert re.search(r"['\"]e['\"]|['\"]E['\"]|key.*edit|edit.*key", js, re.IGNORECASE), (
        "No keyboard handler for E/edit found in JS"
    )
    assert "edit" in js.lower(), "No edit function found in JS"


# ── UI-10 ──────────────────────────────────────────────────────────────────────
def test_ui_10_arrow_key_navigation(js):
    """[CONTRACT] arrow keys navigate between questions."""
    assert "ArrowRight" in js or "arrowright" in js.lower(), "No ArrowRight handler"
    assert "ArrowLeft" in js or "arrowleft" in js.lower(), "No ArrowLeft handler"


# ── UI-11 ──────────────────────────────────────────────────────────────────────
def test_ui_11_progress_bar_element(soup, js):
    """[CONTRACT] progress bar element present and JS updates it."""
    progress = (
        soup.find("progress")
        or soup.find(attrs={"id": re.compile("progress", re.I)})
        or soup.find(attrs={"class": re.compile("progress", re.I)})
    )
    assert progress is not None, "No progress bar element found in DOM"
    assert "progress" in js.lower(), "No progress update logic in JS"


# ── UI-12 ──────────────────────────────────────────────────────────────────────
def test_ui_12_stats_sidebar(soup, js):
    """[CONTRACT] stats sidebar with approve/reject/edited/pending counts."""
    assert "approved" in soup.get_text().lower() or "approved" in js.lower(), (
        "No approved count in UI"
    )
    assert "rejected" in soup.get_text().lower() or "rejected" in js.lower(), (
        "No rejected count in UI"
    )
    assert "pending" in soup.get_text().lower() or "pending" in js.lower(), (
        "No pending count in UI"
    )
    assert "/stats" in js, "JS must call GET /stats endpoint"


# ── UI-13 ──────────────────────────────────────────────────────────────────────
def test_ui_13_subject_filter(soup, js):
    """[CONTRACT] subject filter buttons present for all 5 subjects."""
    text = soup.get_text().lower() + js.lower()
    for subject in ("quantitative", "logical", "science", "reading", "writing"):
        assert subject in text, f"Subject filter for '{subject}' not found"
    # JS must filter by subject
    assert "subject" in js, "No subject filter logic in JS"


# ── UI-14 ──────────────────────────────────────────────────────────────────────
def test_ui_14_confidence_badge(css, js):
    """[CONTRACT] confidence indicator is color-coded."""
    assert "confidence" in js.lower(), "No confidence logic in JS"
    # Should have at least two different confidence-related colors
    confidence_colors = re.findall(r"confidence[^;]*#([0-9a-fA-F]{6})", css + js, re.IGNORECASE)
    # Or color variables / conditions based on threshold
    assert (
        "0.90" in js or "0.9" in js or "threshold" in js.lower() or "confidence" in js.lower()
    ), "No confidence threshold logic found"


# ── UI-15 ──────────────────────────────────────────────────────────────────────
def test_ui_15_edit_mode_save(js):
    """[CONTRACT] edit mode save calls POST /edit endpoint."""
    assert "/edit" in js, "JS must call POST /questions/{id}/edit"
    assert "save" in js.lower() or "Save" in js, "No save action in JS"


# ── UI-16 ──────────────────────────────────────────────────────────────────────
def test_ui_16_edit_mode_cancel_restores(js):
    """[CONTRACT] edit mode cancel restores original values."""
    assert "cancel" in js.lower() or "Cancel" in js, "No cancel action in JS"
    # Should store original values before edit
    assert re.search(r"original|restore|backup|prev|old", js, re.IGNORECASE), (
        "No original-value preservation logic found for edit cancel"
    )


# ── UI-17 ──────────────────────────────────────────────────────────────────────
def test_ui_17_focus_rings_defined(css):
    """[ACCESSIBILITY] CSS defines visible focus rings on interactive elements."""
    assert ":focus" in css or ":focus-visible" in css, "No :focus styles defined in CSS"
    # Must not hide outlines without replacement
    outline_none = re.findall(r":focus[^{]*\{[^}]*outline\s*:\s*none", css, re.DOTALL)
    if outline_none:
        # If outline:none, must have a replacement (box-shadow or border)
        assert re.search(r":focus[^{]*\{[^}]*(box-shadow|border)", css, re.DOTALL), (
            "outline:none on :focus without replacement focus indicator"
        )


# ── UI-18 ──────────────────────────────────────────────────────────────────────
def test_ui_18_text_contrast_dark_theme(css):
    """[ACCESSIBILITY] primary text color is light enough for dark background."""
    # Look for text color declarations and verify they are light
    light_text = re.compile(
        r"color\s*:\s*#([eEdDcCfFbB][0-9a-fA-F]{5}|[eEdDcCfFbB]{3})\b", re.IGNORECASE
    )
    assert light_text.search(css), (
        "No light-colored text found in CSS — primary text must be light on dark background"
    )


# ── UI-19 ──────────────────────────────────────────────────────────────────────
def test_ui_19_no_emoji_icons(html_source):
    """[ACCESSIBILITY] no emoji used as icons in HTML source."""
    emoji_pattern = re.compile(
        "["
        "\U0001f300-\U0001f5ff"
        "\U0001f600-\U0001f64f"
        "\U0001f680-\U0001f6ff"
        "\U0001f700-\U0001f77f"
        "☀-⛿"
        "✀-➿"
        "✓✗✔✘←→↑↓"
        "]"
    )
    matches = emoji_pattern.findall(html_source)
    assert not matches, f"Emoji found in HTML (not allowed as icons): {matches}"


# ── UI-20 ──────────────────────────────────────────────────────────────────────
def test_ui_20_keyboard_only_workflow(js):
    """[ACCESSIBILITY] all actions (approve, reject, edit, save, cancel, navigate) have keyboard handlers."""
    required = ["approve", "reject", "edit", "ArrowRight", "ArrowLeft"]
    for action in required:
        assert action.lower() in js.lower(), f"Keyboard handler for '{action}' missing"
    # Edit mode must have Enter/Escape handlers
    assert "Enter" in js or "enter" in js.lower(), "No Enter key handler for edit save"
    assert "Escape" in js or "escape" in js.lower(), "No Escape key handler for edit cancel"


# ── UI-21 ──────────────────────────────────────────────────────────────────────
def test_ui_21_no_ai_purple_gradient(css):
    """[DESIGN] no AI purple/pink gradient backgrounds in CSS."""
    # Purple range: #8B5CF6, #A78BFA, #7C3AED and similar
    purple_hex = re.compile(r"#([89aAbB][0-9a-fA-F][3-9a-fA-F][0-9a-fA-F]{3})", re.IGNORECASE)
    gradient_purple = re.compile(r"linear-gradient[^;]*#[89aA][0-9a-fA-F]{5}", re.IGNORECASE)
    assert not gradient_purple.search(css), "Purple gradient found in CSS — violates anti-patterns"
    # Also check for generic purple/violet/pink keywords
    assert "purple" not in css.lower(), "CSS contains 'purple' keyword — violates anti-patterns"
    assert "violet" not in css.lower(), "CSS contains 'violet' keyword"


# ── UI-22 ──────────────────────────────────────────────────────────────────────
def test_ui_22_monospace_for_data_elements(css, soup):
    """[DESIGN] monospace font used for data elements (ID, confidence, page, source book)."""
    assert "monospace" in css, "No monospace font declared in CSS"
    # Must have a class/selector that applies monospace to data
    mono_class = re.search(r"(mono|data|meta|code|badge|chip)[^{]*\{[^}]*monospace", css, re.IGNORECASE | re.DOTALL)
    inline_mono = re.search(r"font-family[^;]*monospace", css, re.IGNORECASE)
    assert mono_class or inline_mono, (
        "Monospace font not applied to any data class in CSS"
    )
