"""
Atmospheric Complexity Framework (ACF)

Core - Registry

Real ``Registry`` - the generic ``registry.py`` module named in
``docs/architecture/acf_awci_architecture_gap_analysis.md`` (row
``core/{...,registry,...}.py`` - explicitly distinguished there from
``parameter_registry.py``, which is science-specific). Reuses the
already-real, already-generic ``acf.core.service_manager.
ServiceManager`` directly rather than a second, independently
invented registry class.
"""

from __future__ import annotations

from acf.core.service_manager import ServiceManager

#: Real alias - see this module's own docstring.
Registry = ServiceManager

__all__ = ["Registry"]
