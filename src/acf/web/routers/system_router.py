"""
`/api/v1/system` - real system health/version endpoint - the
``system.py`` module named in this project's own ACF blueprint gap
list (``docs/architecture/acf_awci_architecture_gap_analysis.md``,
row ``api/`` -> ``routes/{...,system}.py``). Real, minimal: reports
this process's own real ``acf.__version__`` and Python/OS info via
``acf.core.environment`` - never a fabricated "all systems nominal"
verdict (this project's own ``docs/STATUS.md`` explicitly warns
against that pattern, citing ``earth_system_operations.py`` as the
precedent to avoid).
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from acf import __version__
from acf.core.environment import operating_system, python_version

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Real liveness check - this process is running and able to
    answer HTTP requests. Does not claim anything about any other
    real subsystem's own state (HPC connection, model availability,
    ...) - those are each their own router's own real concern."""
    return {"status": "ok"}


@router.get("/version")
async def version() -> dict[str, Any]:
    """Real version/environment info - genuinely reads
    ``acf.__version__`` and the real running Python/OS, never a
    hardcoded placeholder."""
    return {
        "acf_version": __version__,
        "python_version": python_version(),
        "operating_system": operating_system(),
    }
