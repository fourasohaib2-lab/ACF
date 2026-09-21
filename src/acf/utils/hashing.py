"""
Atmospheric Complexity Framework (ACF)

Utils - Hashing

Real, stdlib-only (``hashlib``) content hashing - the ``hashing.py``
module named in
``docs/architecture/acf_awci_architecture_gap_analysis.md`` (row
``utils/{...}.py``). Several modules already compute their own
SHA-256 checksum inline for their own specific purpose
(``acf.release.package_validator``, ``acf.hpc_connector.
file_transfer``, ``acf.hpc_connector.data_management.data_manager``) -
this module is not a refactor of those (out of scope here; each has
its own specific real context), only the first real, generic,
reusable version of the same real stdlib operation for a new caller
that needs it.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


def sha256_of_bytes(data: bytes) -> str:
    """Real SHA-256 hex digest of ``data``."""
    return hashlib.sha256(data).hexdigest()


def sha256_of_text(text: str, encoding: str = "utf-8") -> str:
    """Real SHA-256 hex digest of ``text``, encoded as ``encoding``."""
    return sha256_of_bytes(text.encode(encoding))


def sha256_of_file(path: str | Path, chunk_size: int = 1 << 20) -> str:
    """Real SHA-256 hex digest of the file at ``path``, read in real
    ``chunk_size``-byte chunks so this never loads a real large file
    entirely into memory at once."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()
