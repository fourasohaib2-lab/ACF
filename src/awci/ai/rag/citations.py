"""
Atmospheric Complexity Framework (ACF)

AWCI RAG - Citations

Real, human-readable citation formatting from a ``Document``'s own
exact ``Provenance`` - never a second, independent guess at where the
content came from.
"""

from __future__ import annotations

from awci.ai.rag.documents import Document


def format_citation(document: Document) -> str:
    """
    Real citation string built entirely from ``document.provenance``'s
    own real fields - e.g.
    ``"awci.knowledge.meteorology.orographic_turbulence
    (src/awci/knowledge/meteorology/orographic_turbulence.py,
    commit a1b2c3d4)"`` or, for a per-symbol document,
    ``"awci.knowledge.meteorology.clouds.CloudGenus
    (src/awci/knowledge/meteorology/clouds.py, commit a1b2c3d4)"``.
    The commit segment is honestly omitted (never a fabricated hash)
    when ``Provenance.git_commit`` is ``None``.
    """
    provenance = document.provenance
    qualified_name = f"{provenance.module}.{provenance.symbol}" if provenance.symbol else provenance.module
    if provenance.git_commit is not None:
        return f"{qualified_name} ({provenance.source_path}, commit {provenance.git_commit[:8]})"
    return f"{qualified_name} ({provenance.source_path})"
