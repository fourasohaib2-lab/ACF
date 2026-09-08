"""
Atmospheric Complexity Framework (ACF)

Production Updater & Rollback Module
"""

from typing import Any

from acf.core.version import __version__


class ProductionUpdater:
    """Gestionnaire de mises à jour et de retour arrière automatisé (Rollback)."""

    @classmethod
    def check_for_updates(cls) -> dict[str, Any]:
        """
        NOTE (correction): current_version/latest_version were both
        hardcoded to "1.0.0" - the actual installed version
        (acf.core.version.__version__) is "0.1.0", so this reported a
        flatly wrong current version, same bug already fixed next door
        in release/installer.py's ProductionInstaller (see its own
        "current_package_version" NOTE - this sibling was missed at
        the time). latest_version is honestly unknown rather than
        assumed equal to current_version - no real update channel/
        release feed is connected here to check against.
        """
        return {
            "current_version": __version__,
            "latest_version": None,
            "update_available": None,
            "status": "NOT_CHECKED_NO_UPDATE_CHANNEL_CONNECTED",
        }
