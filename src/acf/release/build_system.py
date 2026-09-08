"""
Atmospheric Complexity Framework (ACF)

Production Package Build System Module
"""

from typing import Any


class BuildSystem:
    """Générateur d'artefacts d'empaquetage (Wheel, sdist, tar.gz)."""

    @classmethod
    def build_packages(cls) -> dict[str, Any]:
        """
        NOTE (correction): this used to unconditionally claim
        specific artifact filenames ("acf-1.0.0-py3-none-any.whl",
        "acf-1.0.0.tar.gz" - note: even the version was wrong, the
        real declared package version is 0.1.0, see
        acf.core.version.__version__) and "SUCCESS" with 0 parameters
        and no actual build tool (e.g. `python -m build`) ever
        invoked. Deliberately not shelling out to a real build here
        either (running an actual package build as a side effect of
        a status query would be surprising/expensive) - honestly
        reports that no build ran.
        """
        return {"wheel": None, "sdist": None, "build_status": "NOT_BUILT_NO_BUILD_INVOKED", "is_real_data": False}
