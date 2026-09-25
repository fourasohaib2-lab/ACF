"""
Atmospheric Complexity Framework (ACF)

AWCI API - Shared Serialization Helper

Real re-export of ``acf.utils.serialization.to_json_safe()``. This
module originally held its own real implementation (built for this
API before the generic need was recognized and promoted to
``acf.utils`` - see that module's own docstring); it now reuses that
one, not a second, duplicate implementation.
"""

from __future__ import annotations

from acf.utils.serialization import to_json_safe

__all__ = ["to_json_safe"]
