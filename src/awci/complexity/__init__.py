"""AWCI complexity scoring engine.

Migrated 2026-09-21 (Phase 2 of the AWCI separate-package migration -
see ``awci``'s own package docstring and
``docs/architecture/acf_awci_architecture_gap_analysis.md``'s "§2c"
section) from ``acf.awci``. This is where AWCI's actual score is
computed - ``AWCICalculator`` (``engine.py``/``calculator.py``),
``WeightsManager`` (``weights.py``), the real value normalizer
(``normalizer.py``), and the shared scientific-status classification
types they both use (``scientific_status.py``). Real, tested code
carried over unchanged; ``acf.awci.<module>`` now re-exports from here
for backward compatibility with every existing caller.
"""
