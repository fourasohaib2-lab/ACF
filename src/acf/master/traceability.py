"""
Atmospheric Complexity Framework (ACF)

Equation & Physics Literature Traceability Engine Module (Phase 8)
(EquationTrace linking every law and formula to author, publication, DOI, version, and unit tests)
"""

from dataclasses import dataclass


@dataclass
class EquationTrace:
    """Traçabilité complète d'une loi ou équation physique d'ACF."""

    law_name: str
    latex_equation: str
    origin_publication: str
    author: str
    doi: str | None
    version: str
    date_added: str
    module_path: str
    associated_tests: list[str]
