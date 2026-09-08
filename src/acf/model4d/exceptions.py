"""
Atmospheric Complexity Framework (ACF)

MODEL4D - Exceptions
====================
Custom exceptions for the 4D spatio-temporal modeling subsystem.
"""

from __future__ import annotations

from acf.core.exceptions import ACFError


class Model4DError(ACFError):
    """Base exception for all 4D modeling errors."""


class GridDimensionMismatchError(Model4DError):
    """Raised when dimensions of two 4D grids or fields do not align."""


class CoordinateOutOfBoundsError(Model4DError):
    """Raised when a spatial or temporal query falls outside grid boundaries."""


class InterpolationError(Model4DError):
    """Raised when interpolation cannot be performed on grid data."""


class OperatorError(Model4DError):
    """Raised when a differential or tensor operator fails."""

