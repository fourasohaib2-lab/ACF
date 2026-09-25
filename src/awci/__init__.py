"""AWCI - Aviation Weather Complexity Index.

Separate aviation product/project built on top of the ACF scientific
core, per the user-adopted reference architecture (2026-09-21) - see
``docs/architecture/awci_reference_architecture.md`` for the full
24-layer target and
``docs/architecture/acf_awci_architecture_gap_analysis.md`` for what
has actually moved here versus what still lives under ``acf.awci``/
``acf.aviation`` pending its own migration step.

This package is being built up incrementally, one real subsystem at a
time, rather than as a single large cutover - each migrated subsystem
keeps a backward-compatible re-export at its old ``acf.awci``/
``acf.aviation`` location so existing imports never break.
"""
