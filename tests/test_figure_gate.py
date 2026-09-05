"""The authoring gate must refuse the defects the VIC review rounds kept finding.

Four rounds over 445 figures produced 304 reviewer comments. 45% of them were a number
or letter sitting on a line, and the finaliser that authored those figures never ran the
check that catches it. These tests pin the gate to the defects that actually happened.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from tools.figure_gate import figure_findings


def q(svg, **kw):
    base = {"stem": "In the figure below, what is the value of x?",
            "option_a": "1", "option_b": "2", "option_c": "3", "option_d": "4",
            "correct_answer": "A", "explanation": "x = 1.", "figure_svg": svg}
    base.update(kw)
    return base


def test_a_question_with_no_figure_is_not_gated():
    assert figure_findings(q("")) == []
    assert figure_findings(q(None)) == []


def test_a_label_printed_across_a_line_is_refused():
    """The single most common defect: 45% of every comment across four rounds."""
    svg = ('<svg viewBox="0 0 200 120" xmlns="http://www.w3.org/2000/svg">'
           '<line x1="20" y1="60" x2="180" y2="60" stroke="currentColor" '
           'stroke-width="2"/>'
           '<text x="100" y="63" font-family="Arial" font-size="13" '
           'fill="currentColor" text-anchor="middle">12 cm</text></svg>')
    found = figure_findings(q(svg))
    assert found, "a label drawn straight across a line must be refused"
    assert any("drawn on top of" in m for m in found)


def test_the_same_label_moved_clear_of_the_line_passes():
    """The gate has to be satisfiable, or it gets switched off."""
    svg = ('<svg viewBox="0 0 200 120" xmlns="http://www.w3.org/2000/svg">'
           '<line x1="20" y1="60" x2="180" y2="60" stroke="currentColor" '
           'stroke-width="2"/>'
           '<text x="100" y="48" font-family="Arial" font-size="13" '
           'fill="currentColor" text-anchor="middle">12 cm</text></svg>')
    assert figure_findings(q(svg)) == []


def test_two_labels_on_top_of_each_other_are_refused():
    svg = ('<svg viewBox="0 0 200 120" xmlns="http://www.w3.org/2000/svg">'
           '<text x="100" y="60" font-family="Arial" font-size="13" '
           'fill="currentColor" text-anchor="middle">12 cm</text>'
           '<text x="102" y="61" font-family="Arial" font-size="13" '
           'fill="currentColor" text-anchor="middle">14 cm</text></svg>')
    assert any("overlap" in m for m in figure_findings(q(svg)))


def test_a_figure_that_hard_codes_its_ink_is_refused():
    """Black ink is invisible on a dark surface; every figure draws in currentColor."""
    svg = ('<svg viewBox="0 0 200 120" xmlns="http://www.w3.org/2000/svg">'
           '<line x1="20" y1="60" x2="180" y2="60" stroke="#000" '
           'stroke-width="2"/></svg>')
    assert figure_findings(q(svg))


def test_advisories_are_reported_separately_and_do_not_block():
    """A check that answers 'needs a human' cannot be a gate: a builder cannot satisfy
    it, and a gate that cannot be satisfied gets switched off."""
    svg = ('<svg viewBox="0 0 200 120" xmlns="http://www.w3.org/2000/svg">'
           '<line x1="20" y1="60" x2="180" y2="60" stroke="currentColor" '
           'stroke-width="2"/></svg>')
    assert all("needs a human" not in m.lower() for m in figure_findings(q(svg)))
