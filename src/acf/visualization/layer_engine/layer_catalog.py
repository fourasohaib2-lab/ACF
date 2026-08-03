"""
Atmospheric Complexity Framework (ACF)

Layer Catalog & Category Manager Module
"""

from typing import Any, Dict, List
from acf.visualization.layer_engine.layer_registry import DOMAINS_15, LayerRegistry


class LayerCatalog:
    """Gestionnaire de catalogue multi-domaine et de catégorisation."""

    @classmethod
    def get_domains(cls) -> List[str]:
        return DOMAINS_15

    @classmethod
    def get_catalog_summary(cls) -> Dict[str, Any]:
        return {
            "total_domains": len(DOMAINS_15),
            "total_registered_layers": len(LayerRegistry.list_all_layers()),
            "catalog_status": "500_LAYERS_CATALOGUE_READY",
        }
