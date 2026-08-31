"""
Atmospheric Complexity Framework (ACF)

MODEL4D - Operators Facade
==========================

NOTE (found, NOT changed — RÈGLE D'OR / single source of truth): this
module is dead code. `src/acf/model4d/operators/` is ALSO a package
with its own __init__.py, which Python's import resolution always
finds before this sibling module.py of the same name - so
`import acf.model4d.operators` (or `from acf.model4d.operators import
Operators4D`) can never actually reach this file, and the package's
__init__.py doesn't re-export Operators4D either, so this unified
facade class is permanently unreachable by any import path. The
individual operator classes it wraps (Gradient, Divergence, Laplacian,
Curl, Advection, Diffusion, OperatorsEngine) remain genuinely reachable
and correct via the package directly. Not deleted per project
convention - flagged so nobody mistakes this for live code. Same
situation as data/engine.py's NOTE.
"""

from __future__ import annotations

from typing import Any

from acf.model4d.operators.advection import Advection
from acf.model4d.operators.curl import Curl
from acf.model4d.operators.diffusion import Diffusion
from acf.model4d.operators.divergence import Divergence
from acf.model4d.operators.gradient import Gradient
from acf.model4d.operators.laplacian import Laplacian
from acf.model4d.operators.operators_engine import OperatorsEngine


class Operators4D:
    """
    Unified 4D differential operators interface.
    """

    def __init__(self, engine: OperatorsEngine | None = None) -> None:
        self.engine = engine or OperatorsEngine()

    def gradient(self, *args: Any, **kwargs: Any) -> Any:
        return self.engine.gradient(*args, **kwargs)

    def divergence(self, *args: Any, **kwargs: Any) -> Any:
        return self.engine.divergence(*args, **kwargs)

    def laplacian(self, *args: Any, **kwargs: Any) -> Any:
        return self.engine.laplacian(*args, **kwargs)

    def curl(self, *args: Any, **kwargs: Any) -> Any:
        return self.engine.curl(*args, **kwargs)

    def advection(self, *args: Any, **kwargs: Any) -> Any:
        return self.engine.advection(*args, **kwargs)

    def diffusion(self, *args: Any, **kwargs: Any) -> Any:
        return self.engine.diffusion(*args, **kwargs)


__all__ = [
    "Advection",
    "Curl",
    "Diffusion",
    "Divergence",
    "Gradient",
    "Laplacian",
    "Operators4D",
    "OperatorsEngine",
]

