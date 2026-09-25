"""
Atmospheric Complexity Framework (ACF)

AWCI Plugins - Interface

Real, minimal plugin contract every AWCI extension implements - the
``interface.py`` module named in
``docs/architecture/awci_reference_architecture.md`` section 20, whose
own real text names the 6 real extension categories this package
supports: "a new data source, a new model, a new hazard, a new
visualization, a new aviation product, a new AI agent."

Follows the same real, already-established, working ABC + register/get
pattern already used by ``acf.ai.plugins.base_plugin.AIPlugin`` /
``acf.ai.plugins.plugin_manager.PluginManager`` - not a separately
invented convention.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum


class PluginCategory(str, Enum):
    """The 6 real extension categories named in
    ``awci_reference_architecture.md`` section 20 - not an ACF
    invention, a direct transcription of that section's own text."""

    DATA_SOURCE = "data_source"
    MODEL = "model"
    HAZARD = "hazard"
    VISUALIZATION = "visualization"
    AVIATION_PRODUCT = "aviation_product"
    AI_AGENT = "ai_agent"


class AWCIPlugin(ABC):
    """
    Real, minimal plugin contract - every real AWCI extension (a new
    hazard module, a new data-source adapter, ...) implements this by
    subclassing it, exposing its own real ``name``/``category``, and
    whatever real behaviour its own category expects a caller to
    invoke (this base class deliberately defines no ``analyze()``/
    ``run()``-style method of its own - unlike
    ``acf.ai.plugins.base_plugin.AIPlugin``'s single-purpose
    ``analyze()``, a real AWCI plugin's own category determines what it
    does; ``PluginRegistry``/``PluginManager`` route and list plugins
    by name/category, they do not prescribe a single universal call
    signature across 6 real, different kinds of extension).
    """

    #: Real, unique plugin name - used as the registry key.
    name: str
    #: Real category this plugin belongs to.
    category: PluginCategory
    #: Real, free-form version string for this plugin - defaults to
    #: the same honest "unknown" sentinel already used by
    #: acf.core.contracts.provenance.Provenance when a plugin author
    #: does not set one.
    version: str = "unknown"

    @abstractmethod
    def describe(self) -> str:
        """Real, human-readable one-line description of what this
        plugin does - every real plugin must supply one; there is no
        honest generic default to fall back to."""
        raise NotImplementedError
