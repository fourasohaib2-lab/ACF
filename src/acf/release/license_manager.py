"""
Atmospheric Complexity Framework (ACF)

License Manager Module
"""

from pathlib import Path
from typing import Any

_LICENSE_FILE = Path(__file__).resolve().parents[3] / "LICENSE"


class LicenseManager:
    """Gestionnaire de conformité des licences scientifiques et des dépendances open source."""

    @classmethod
    def verify_licenses(cls) -> dict[str, Any]:
        """
        NOTE (correction): this used to unconditionally claim
        "Apache 2.0 / Open Science License, 100% COMPLIANT" without
        checking anything - and did not actually cross-check any
        dependency's real license (that needs a package-metadata scan,
        e.g. via importlib.metadata, not implemented here). Now
        genuinely checks whether the project's own LICENSE file exists
        and reports its first line, rather than fabricating a
        compliance percentage no real check produced.
        """
        if _LICENSE_FILE.exists():
            first_line = _LICENSE_FILE.read_text(encoding="utf-8", errors="replace").splitlines()[0]
            return {
                "license_file_found": True,
                "license_first_line": first_line,
                "compliance": "LICENSE_FILE_PRESENT_DEPENDENCY_SCAN_NOT_PERFORMED",
                "is_real_data": True,
            }
        return {
            "license_file_found": False,
            "license_first_line": None,
            "compliance": "NOT_VERIFIED_NO_LICENSE_FILE_FOUND",
            "is_real_data": True,
        }
