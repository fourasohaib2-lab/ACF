"""
Atmospheric Complexity Framework (ACF)

Production Installer Module
"""

from typing import Any

from acf.core.version import __version__


class ProductionInstaller:
    """Installeur automatisé de la release de production ACF v1.0."""

    @classmethod
    def run_installation(cls) -> dict[str, Any]:
        """
        NOTE (correction): this used to unconditionally claim
        "SUCCESSFULLY_INSTALLED" with a hardcoded wrong version
        ("1.0.0" - the real declared version is 0.1.0) and 0
        parameters - no actual installation step (pip install, file
        copy, service registration...) ever ran. Not fabricated.
        """
        return {
            "installation_status": "NOT_INSTALLED_NO_INSTALL_STEP_EXECUTED",
            "installed_version": None,
            "current_package_version": __version__,
            "is_real_data": False,
        }
