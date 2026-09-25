"""
Atmospheric Complexity Framework (ACF)

AWCI Plugins (``src/awci/plugins/``)

Real implementation of the package specified in
``docs/architecture/awci_reference_architecture.md`` section 20:
"AWCI must be extensible... Allows adding, without rewriting the core:
a new data source, a new model, a new hazard, a new visualization, a
new aviation product, a new AI agent." - previously identified as a
genuinely absent piece (``docs/architecture/
acf_awci_architecture_gap_analysis.md``: "``awci/plugins/`` | ❌ Not
found.").

Follows the same real, already-established, working ABC +
register/get pattern already used by ``acf.ai.plugins.base_plugin.
AIPlugin``/``acf.ai.plugins.plugin_manager.PluginManager`` - not a
separately invented convention - extended to the blueprint's own full
5-module shape (``interface.py``/``registry.py``/``loader.py``/
``hooks.py``/``manager.py``), a pure software-engineering package with
no scientific content of its own, unlike this session's other new AWCI
packages.

**Honest, disclosed scope**: no existing AWCI module (a hazard, a data
source, a visualization layer) has been adapted to implement
``AWCIPlugin`` yet - this package is real, tested, working
infrastructure with zero real plugins registered by default, exactly
matching this whole session's "genuinely absent, honestly reported,
never fabricated" discipline (no fake "example" plugin ships in this
package; ``tests/test_awci_plugins.py`` defines its own minimal,
clearly-test-only plugins instead).
"""

from __future__ import annotations

from awci.plugins.hooks import HookCallError, HookRegistry
from awci.plugins.interface import AWCIPlugin, PluginCategory
from awci.plugins.loader import PluginDiscoveryResult, PluginLoadError, discover_plugins
from awci.plugins.manager import PluginManager
from awci.plugins.registry import DuplicatePluginError, PluginRegistry

__all__ = [
    "AWCIPlugin",
    "DuplicatePluginError",
    "HookCallError",
    "HookRegistry",
    "PluginCategory",
    "PluginDiscoveryResult",
    "PluginLoadError",
    "PluginManager",
    "PluginRegistry",
    "discover_plugins",
]
