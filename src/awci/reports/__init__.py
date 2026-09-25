"""
Atmospheric Complexity Framework (ACF)

Reports (``src/awci/reports/``)

Real implementation start of the package named in
``docs/architecture/awci_reference_architecture.md`` section 17:
"Every report must preserve: data sources, model, time, location,
calculation, factors, hazards, confidence, uncertainty, provenance."
Previously the specific, named gap in
``docs/architecture/acf_awci_architecture_gap_analysis.md`` ("no
standalone ``reports/aviation_report.py`` generator" - GUI panels like
``awci_execution_report_dialog.py`` existed, but no standalone
generator).

Built 2026-09-21: ``generator.py`` (real, generic text-rendering
helpers) and ``aviation_report.py`` (``build_aviation_report()``/
``format_aviation_report()`` - a real, composed report over 3
already-real systems: ``awci.airport.weather``, ``awci.decision``,
``awci.provenance`` - see that module's own docstring for the full
composition).

``flight_report.py``/``airport_report.py``/``hazard_report.py``/
``complexity_report.py``/``model_report.py``/``verification_report.py``/
``templates/`` (the blueprint's remaining named files) are deliberately
not built - ``aviation_report.py`` already covers the same real
composed content (weather + hazards + model/provenance) a
flight/airport-specific report would otherwise duplicate; a dedicated
``templates/`` directory would need a real templating engine decision
out of scope for this pass.
"""

from __future__ import annotations
