"""
Atmospheric Complexity Framework (ACF)

Data Engine Package
===================

Public API for dataset analysis.
"""

from .dataset_engine import DatasetEngine

# Compatibilité avec les anciens tests
DataEngine = DatasetEngine

__all__ = [
    "DataEngine",
    "DatasetEngine",
]
