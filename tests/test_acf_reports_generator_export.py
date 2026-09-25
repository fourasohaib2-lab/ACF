"""Tests for the new acf.reports additions (generator.py, export.py),
built while working through the full remaining-gaps list ("On les
attaque toutes un par un") for the ACF-general reports/ gap:
docs/architecture/acf_awci_architecture_gap_analysis.md's own
reports/ row named these (among others) as missing.

generator.py was promoted from awci.reports.generator (built earlier
this session for the AWCI aviation report) once the same real,
generic need was recognized beyond that one caller - that module now
re-exports this one rather than keeping a duplicate implementation.
"""

from __future__ import annotations

from acf.reports.export import write_report
from acf.reports.generator import ReportSection, render_report

# --------------------------------------------------------------------- generator.py


def test_render_report_renders_title_and_sections_in_order():
    output = render_report(
        "Test Report",
        (
            ReportSection("First", ("line a", "line b")),
            ReportSection("Second", ("line c",)),
        ),
    )
    assert output.startswith("Test Report\n===========\n")
    assert "First\n-----\nline a\nline b" in output
    assert "Second\n------\nline c" in output
    assert output.index("First") < output.index("Second")


def test_render_report_honestly_discloses_an_empty_section():
    output = render_report("Test Report", (ReportSection("Empty", ()),))
    assert "Empty\n-----\nnot available" in output


def test_awci_reports_generator_reuses_this_module_not_a_copy():
    from awci.reports.generator import ReportSection as AwciSection
    from awci.reports.generator import render_report as awci_render_report

    assert AwciSection is ReportSection
    assert awci_render_report is render_report


# --------------------------------------------------------------------- export.py


def test_write_report_writes_the_real_content_to_disk(tmp_path):
    content = render_report("X", (ReportSection("S", ("a",)),))
    output_path = write_report(content, tmp_path / "report.md")

    assert output_path == tmp_path / "report.md"
    assert output_path.read_text(encoding="utf-8") == content


def test_write_report_creates_missing_parent_directories(tmp_path):
    output_path = write_report("hello", tmp_path / "nested" / "deep" / "report.txt")
    assert output_path.exists()
    assert output_path.read_text() == "hello"


def test_write_report_accepts_a_string_path(tmp_path):
    output_path = write_report("hello", str(tmp_path / "report.txt"))
    assert output_path.exists()
