"""
Atmospheric Complexity Framework (ACF)

Version Manager Module
"""

from acf.core.version import __version__


class VersionManager:
    """Gestionnaire de numérotation sémantique des versions (SemVer 2.0.0)."""

    @classmethod
    def get_version(cls) -> str:
        """
        NOTE (correction): used to hardcode "1.0.0" - the actual
        declared version (acf.core.version.__version__, also
        pyproject.toml's version) is "0.1.0". Same wrong-version bug
        already fixed in release/installer.py's ProductionInstaller
        and release/updater.py's ProductionUpdater; this sibling in the
        same package was missed at the time.
        """
        return __version__

    @classmethod
    def parse_version(cls, version_str: str) -> dict[str, int]:
        parts = version_str.split(".")
        return {"major": int(parts[0]), "minor": int(parts[1]), "patch": int(parts[2])}
