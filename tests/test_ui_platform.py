"""
Atmospheric Complexity Framework (ACF)

Global Earth System Operations Platform UI Test Suite (MISSION ACF-UI-001)
"""

from acf.gui.earth_system_operations import EarthSystemOperationsPlatform


def test_earth_system_operations_platform_metadata():
    """Test du gestionnaire d'interface opérationnelle unifiée ACF-UI-001."""
    meta = EarthSystemOperationsPlatform.get_platform_metadata()
    assert meta["platform_name"] == "ACF Earth System Operations Platform v1.0"
    assert len(meta["operational_panels"]) == 8
    assert "header_ribbon" in meta["layout_components"]
    assert meta["integration_status"] == "ALL_45_MISSIONS_INTEGRATED"
