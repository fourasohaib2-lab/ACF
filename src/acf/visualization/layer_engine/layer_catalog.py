"""
Atmospheric Complexity Framework (ACF)

Layer Catalog & Category Manager Module
"""

from typing import Any

from acf.visualization.layer_engine.layer_registry import DOMAINS_15, LayerRegistry


class LayerCatalog:
    """Gestionnaire de catalogue multi-domaine et de catégorisation."""

    @classmethod
    def get_domains(cls) -> list[str]:
        return DOMAINS_15

    @classmethod
    def get_catalog_summary(cls) -> dict[str, Any]:
        """
        NOTE (correction): total_domains/total_registered_layers are
        genuine real counts (len() of the actual registries), but
        "catalog_status": "500_LAYERS_CATALOGUE_READY" was a fixed
        aspirational claim wildly inconsistent with reality - only 7
        layers are actually registered in LayerRegistry at the time of
        this fix, not 500. Now reports the real count instead of a
        fixed marketing number.
        """
        total_layers = len(LayerRegistry.list_all_layers())
        return {
            "total_domains": len(DOMAINS_15),
            "total_registered_layers": total_layers,
            "catalog_status": f"{total_layers}_LAYERS_REGISTERED",
            "is_real_data": True,
        }
