"""
Atmospheric Complexity Framework (ACF)

Reports - Export

Real, minimal report-to-file export - the ``export.py`` module named
in ``docs/architecture/acf_awci_architecture_gap_analysis.md`` (row
``reports/``). ``BriefingGenerator.generate_briefing()`` already
accepts an ``export_format`` parameter and labels its output
accordingly, but never actually writes anything to disk (confirmed by
reading that method - it only returns the content string). This
module is the one real, missing piece: writing already-generated real
report text to a real file.
"""

from __future__ import annotations

from pathlib import Path


def write_report(content: str, path: str | Path, encoding: str = "utf-8") -> Path:
    """
    Real file export - writes ``content`` (already-generated real
    report text, e.g. from ``acf.reports.generator.render_report()``
    or ``BriefingGenerator.generate_briefing()``'s own ``"content"``
    field) to ``path``, creating parent directories if needed. Returns
    the real ``Path`` written to.
    """
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding=encoding)
    return output_path
