"""
Atmospheric Complexity Framework (ACF)

AWCI Core - Configuration

Real re-export - the ``configuration.py`` module named in
``docs/architecture/awci_reference_architecture.md`` section 1. AWCI's
own real, external, versioned configuration already exists at
``awci.complexity.config_loader`` (``AWCIConfig``/``load_config()``/
``save_default_config()`` - built to close
``docs/ACF_MASTER_PROMPT.md`` section 56's own named gap, "prévoir une
configuration versionnée (modules, normalisation AWCI, poids,
seuils)"; JSON-backed, validated by genuinely constructing a real
``AWCICalculator`` from the loaded values, never reimplementing that
validation). Re-exported here under the path the reference
architecture names, rather than building a second, competing AWCI
configuration concept.
"""

from __future__ import annotations

from awci.complexity.config_loader import AWCIConfig, load_config, save_default_config

__all__ = ["AWCIConfig", "load_config", "save_default_config"]
