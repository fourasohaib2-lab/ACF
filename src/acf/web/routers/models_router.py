"""
`/api/v1/models` - real HTTP surface over the Model Adapter Protocol
(`acf.models.base_model.BaseWeatherModel`, built in an earlier phase).

Every response field below is genuinely computed by the adapter itself
(`capabilities()` is real introspection, not a static claim - see
`base_model.py`'s own docstring) - this router adds no new model
knowledge of its own.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, HTTPException

from acf.models.aladin import ALADINIngestionAdapter
from acf.models.arome import AROMEIngestionAdapter
from acf.models.arpege import ARPEGEIngestionAdapter
from acf.models.base_model import BaseWeatherModel
from acf.models.icon import ICONIngestionAdapter
from acf.models.implementations.era5 import ERA5Model
from acf.models.openifs import OpenIFSIngestionAdapter
from acf.models.wrf import WRFIngestionAdapter

#: Every real adapter this project has - not a subset. Constructed
#: fresh per request (adapters are cheap, stateless unless given a
#: filepath) rather than shared mutable instances.
_ADAPTER_CLASSES: dict[str, type[BaseWeatherModel]] = {
    "AROME": AROMEIngestionAdapter,
    "ALADIN": ALADINIngestionAdapter,
    "ARPEGE": ARPEGEIngestionAdapter,
    "ERA5": ERA5Model,
    "WRF": WRFIngestionAdapter,
    "ICON": ICONIngestionAdapter,
    "OpenIFS": OpenIFSIngestionAdapter,
}

router = APIRouter(prefix="/models", tags=["models"])


def _get_adapter(name: str) -> BaseWeatherModel:
    cls = _ADAPTER_CLASSES.get(name)
    if cls is None:
        raise HTTPException(404, f"Unknown model {name!r} - known: {sorted(_ADAPTER_CLASSES)}")
    return cls()


@router.get("")
async def list_models() -> list[dict[str, Any]]:
    """Every real registered adapter's real `capabilities()` report."""
    return [cls().capabilities() for cls in _ADAPTER_CLASSES.values()]


@router.get("/{name}")
async def get_model(name: str) -> dict[str, Any]:
    """One adapter's real capabilities, variables, projection and vertical level convention."""
    adapter = _get_adapter(name)
    return {
        **adapter.capabilities(),
        "variables": adapter.variables(),
        "levels": adapter.levels(),
    }


@router.post("/{name}/detect")
async def detect_model(name: str, filename: str = Body(..., embed=True)) -> dict[str, Any]:
    """Run the adapter's real `detect()` against a filename - the same real logic ModelDetector uses, not a second implementation."""
    adapter = _get_adapter(name)
    return {"model": name, "filename": filename, "detected": adapter.detect(filename)}
