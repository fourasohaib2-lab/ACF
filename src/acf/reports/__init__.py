"""
Atmospheric Complexity Framework (ACF)

acf.reports - real content: ``briefings/briefing_generator.py``
(``BriefingGenerator`` - real operational meteorological briefing
text generation, already carries its own fix disclosure for a
previously fabricated model-consensus claim).

Added 2026-09-21 to close this project's own blueprint `reports/{...}`
gap (`docs/architecture/acf_awci_architecture_gap_analysis.md`):
``generator.py`` (``ReportSection``/``render_report()`` - promoted
from ``awci.reports.generator``, built first for the AWCI aviation
report, once the same real, generic need was recognized beyond that
one caller - not aviation-specific) and ``export.py``
(``write_report()`` - real file export; ``BriefingGenerator`` accepts
an ``export_format`` parameter but never itself writes to disk).

``scientific_report.py``/``model_report.py``/``diagnostic_report.py``
are deliberately not built - each would only be a thin, specific
convention for calling ``render_report()`` with a particular title;
a caller can already build any of those by supplying its own real
``ReportSection`` tuple, so a dedicated wrapper file per report "kind"
would add no real behavior, only naming. ``templates/`` is
deliberately not built - this project has no templating-engine
dependency (e.g. Jinja2) declared anywhere, and adding one is a real,
separate dependency decision this item was not asked to make (matching
this session's own earlier precedent of not adding a new dependency
without asking first).
"""
