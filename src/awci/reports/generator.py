"""
Atmospheric Complexity Framework (ACF)

Reports - Generator

Real, generic text-report rendering helpers - the ``generator.py``
module named in
``docs/architecture/awci_reference_architecture.md`` section 17
("Reports... Every report must preserve: data sources, model, time,
location, calculation, factors, hazards, confidence, uncertainty,
provenance."). Reusable by any real report type this package builds
(``aviation_report.py`` today) - pure text formatting, never a
computation of its own.
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
    with an honest "not available" body, never silently dropped -
    matching this codebase's established "a missing real value is
    disclosed, not hidden" convention (see e.g.
    ``AWCIResult.trace_chain()``).
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
