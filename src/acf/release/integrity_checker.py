"""
Atmospheric Complexity Framework (ACF)

Code & Scientific Dataset Integrity Checker Module
"""

import subprocess
from typing import Any


class IntegrityChecker:
    """Vérificateur d'empreinte SHA-256 du code source et des catalogues scientifiques."""

    @classmethod
    def verify_integrity(cls) -> dict[str, Any]:
        """
        NOTE (correction): this used to return a fixed fake hash
        ("3a8f90...b4e2", not even a real-looking full SHA-256) and
        "100% INTEGRITY VERIFIED" unconditionally - nothing was ever
        hashed. Now reports the real current git commit hash (a real,
        verifiable integrity identifier for the checked-out source
        tree) when run inside a git repository, honestly reporting
        unavailability otherwise rather than fabricating one.
        """
        try:
            commit = (
                subprocess.run(
                    ["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5, check=True
                )
                .stdout.strip()
            )
            dirty = (
                subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, timeout=5)
                .stdout.strip()
                != ""
            )
            return {
                "git_commit_sha": commit,
                "working_tree_dirty": dirty,
                "verification_status": "GIT_COMMIT_HASH_ONLY_NOT_A_FULL_CONTENT_AUDIT",
                "is_real_data": True,
            }
        except Exception as exc:
            return {
                "git_commit_sha": None,
                "working_tree_dirty": None,
                "verification_status": f"NOT_VERIFIED_GIT_UNAVAILABLE: {exc}",
                "is_real_data": False,
            }
