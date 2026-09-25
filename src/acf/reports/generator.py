"""
Atmospheric Complexity Framework (ACF)

Reports - Generator

Real, generic text-report rendering helpers - the ``generator.py``
module named in
``docs/architecture/acf_awci_architecture_gap_analysis.md`` (row
``reports/``). Promoted here from ``awci.reports.generator`` (built
earlier this session for the AWCI aviation report) once it became
clear the same real, generic need (arrange already-real, caller-
supplied text sections into one report, honestly disclosing a section
with no real content rather than hiding it) applies beyond that one
caller - nothing here is aviation-specific.
``awci.reports.generator`` now re-exports this module rather than
keeping a duplicate implementation.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReportSection:
    """One real, titled section of a report - ``lines`` are already
    real, formatted strings (built by the caller from its own real
    data); this class and ``render_report()`` below only arrange them,
    never generate or alter their content."""

    title: str
    lines: tuple[str, ...]


def render_report(title: str, sections: tuple[ReportSection, ...]) -> str:
    """
    Real, plain-text rendering of ``title`` plus every real
    ``ReportSection`` in ``sections``, in the given order. A section
    with no real lines (``lines == ()``) still renders its own title
    with an honest "not available" body, never silently dropped.
    """
    output_lines = [title, "=" * len(title), ""]
    for section in sections:
        output_lines.append(section.title)
        output_lines.append("-" * len(section.title))
        if section.lines:
            output_lines.extend(section.lines)
        else:
            output_lines.append("not available")
        output_lines.append("")
    return "\n".join(output_lines).rstrip() + "\n"
