"""
ECMWF Parameter Catalog

NOTE (found, NOT changed — post-model4d audit, 2026-09-11): the
ECMWF_PARAMETERS dict below is a real, empty placeholder - not
fabricated data, but also not populated - and disconnected from the
package's own real ECMWF parameter loading path
(acf.standards.ecmwf.manager.ECMWFManager/acf.standards.hub.
StandardsHub.load_ecmwf(), which genuinely reads resources/standards/
ecmwf/parameters.json via acf.importers.ecmwf.importer.ECMWFImporter -
see that module's own docstring). Zero callers beyond this module's
own dedicated test (tests/test_ecmwf_catalog.py, which only asserts
ECMWF_PARAMETERS is a dict - not a content check) - verified by grep.
Left empty rather than duplicating the real loader's data here without
a real spec calling for a static, pre-populated catalog alongside the
existing file-backed loader.
"""

from typing import Any

ECMWF_PARAMETERS: dict[str, Any] = {}
