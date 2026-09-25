"""
Atmospheric Complexity Framework (ACF)

Core - Lifecycle

Real ``Lifecycle`` - the generic ``lifecycle.py`` module named in
``docs/architecture/acf_awci_architecture_gap_analysis.md`` (row
``core/{...,lifecycle,...}.py``). Reuses the already-real
``acf.core.bootstrap.Bootstrap`` directly - it already IS ACF's real
startup-sequence class (config load, service registration, plugin
discovery); this module only exposes it under the name the blueprint
expects, rather than a second, independently invented lifecycle class.
"""

from __future__ import annotations

from acf.core.bootstrap import Bootstrap

#: Real alias - see this module's own docstring.
Lifecycle = Bootstrap

__all__ = ["Lifecycle"]
