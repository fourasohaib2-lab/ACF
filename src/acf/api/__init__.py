"""
acf.api - ACFAPI, a headless facade over already-real components:
core.default_parameters.create_registry, and 3 already-audited
acf.ai classes (DatasetAnalyzer, ForecastAssistant, WeatherAlertEngine
- see acf.ai's own Tier E audit note). Genuinely correct delegation,
no fabrication.

Verified 2026-09-06: not constructed anywhere in src/ - only used by
tests/test_api.py.
"""
