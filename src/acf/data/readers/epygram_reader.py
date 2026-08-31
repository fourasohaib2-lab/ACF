"""
Atmospheric Complexity Framework (ACF)

DATA READERS - EPyGrAM Reader (FA, LFA, LFI, GRIB, NetCDF)

Integrates Météo-France EPyGrAM library into ACF for reading FA, LFA, LFI, GRIB, and NetCDF formats.
Provides unified interfaces for ARPEGE, AROME, and ALADIN NWP operational outputs.

NOTE (correction — one of the most operationally dangerous findings
this session): every data-extraction method below used to genuinely
attempt a real epygram.resources call first, but on ANY failure
(file not actually parseable by epygram, wrong/corrupted format, or
epygram simply not installed) silently fell back to FABRICATED data
presented as if it had been read from the real file - and for
read_field() specifically, that fallback was np.random.uniform(...):
literally random numbers in a plausible temperature range, returned
under the real field's name, changing on every call. A forecaster or
downstream script has no way to tell from the return value alone
whether a field was really read from a file or randomly generated.
This is worse than a fixed fake constant (which at least reproduces
consistently and can eventually be recognized as suspicious) - every
method now returns an honest None/empty/False result with an explicit
NOT_READ_NO_REAL_RESOURCE_OPENED-style status when the real epygram
path doesn't succeed, and never silently substitutes invented data.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Self

try:
    import epygram

    EPYGRAM_AVAILABLE = True
except ImportError:
    epygram = None
    EPYGRAM_AVAILABLE = False

from acf.importers.base.base_reader import BaseReader

# -----------------------------------------------------------------------------
# Exception Hierarchy
# -----------------------------------------------------------------------------


class EPyGrAMReaderError(Exception):
    """Base exception for EPyGrAM reader operations."""


class EPyGrAMNotInstalledError(EPyGrAMReaderError):
    """Exception raised when EPyGrAM library is not installed in the Python environment."""


class EPyGrAMFileNotFoundError(EPyGrAMReaderError, FileNotFoundError):
    """Exception raised when the target meteorological file does not exist."""


# -----------------------------------------------------------------------------
# EPyGrAMReader Class
# -----------------------------------------------------------------------------


class EPyGrAMReader(BaseReader):
    """
    EPyGrAM backend reader for Météo-France FA, LFA, and LFI formats, as well as GRIB and NetCDF.
    """

    name = "EPyGrAM Reader"
    extensions = [
        ".fa",
        ".lfa",
        ".lfi",
        ".fa.gz",
        ".grib",
        ".grib2",
        ".grb",
        ".nc",
        ".netcdf",
    ]

    def __init__(self, filepath: str | Path | None = None) -> None:
        self.filepath: Path | None = Path(filepath) if filepath else None
        self._resource: Any = None
        self._is_open: bool = False
        self._format: str = "UNKNOWN"
        self._open_failure_reason: str | None = None

    def can_read(self, filename: str | Path) -> bool:
        """Check if the given file format can be read by EPyGrAM."""
        path_str = str(filename).lower()
        for ext in self.extensions:
            if path_str.endswith(ext):
                return True
        return False

    def open(
        self,
        filepath: str | Path | None = None,
        must_exist: bool = True,
        strict_epygram: bool = False,
    ) -> EPyGrAMReader:
        """Open a meteorological file using EPyGrAM.

        Raises:
            ValueError: If no filepath is specified.
            EPyGrAMFileNotFoundError: If the target file does not exist (when must_exist=True).
            EPyGrAMNotInstalledError: If strict_epygram=True and epygram is missing.
        """
        target_path = Path(filepath) if filepath else self.filepath
        if not target_path:
            raise ValueError("No filepath specified to open.")

        self.filepath = target_path
        self._open_failure_reason = None

        if must_exist and not target_path.exists():
            raise EPyGrAMFileNotFoundError(f"Meteorological file not found: {target_path}")

        if strict_epygram and not EPYGRAM_AVAILABLE:
            raise EPyGrAMNotInstalledError("EPyGrAM library is not installed in the active Python environment.")

        self._format = self._detect_format_from_ext(target_path)

        if EPYGRAM_AVAILABLE and target_path.exists():
            try:
                # NOTE (correction): this used to call the
                # non-existent epygram.resources.open(...) (AttributeError:
                # module 'epygram.resources' has no attribute 'open') -
                # meaning the "real" epygram path could never once
                # succeed, with or without epygram installed, and this
                # method always silently fell through to the fake
                # fallback below. The real public API, verified against
                # epygram 2.1.0 installed in this environment, is
                # epygram.open(filename, openmode).
                self._resource = epygram.open(str(target_path), "r")
                self._is_open = True
                self._format = getattr(self._resource, "format", self._format)
                return self
            except Exception as e:
                # NOTE (correction): this used to silently swallow the
                # exception and pretend the file had been opened - the
                # real failure reason is now kept so downstream
                # methods can report it instead of fabricating data.
                self._resource = None
                self._open_failure_reason = f"{type(e).__name__}: {e}"
        elif not EPYGRAM_AVAILABLE:
            self._open_failure_reason = "epygram is not installed in this environment"

        self._is_open = True
        return self

    def close(self) -> None:
        """Close the underlying EPyGrAM resource handle cleanly."""
        if self._resource is not None:
            if hasattr(self._resource, "close"):
                try:
                    self._resource.close()
                except Exception:
                    pass
            self._resource = None
        self._is_open = False

    def __enter__(self) -> Self:
        if not self._is_open:
            self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def _require_open(self) -> None:
        if not self._is_open:
            raise RuntimeError("EPyGrAMReader is not open. Call open() first.")

    def list_fields(self) -> list[str]:
        """
        List all fields available in the opened file.

        NOTE (correction): this used to fall back to a fixed list of 6
        plausible-looking AROME field names when no real resource was
        open - no such fields exist in that case. Now returns an empty
        list.
        """
        self._require_open()

        if self._resource and hasattr(self._resource, "listfields"):
            try:
                fields = self._resource.listfields()
                if isinstance(fields, list):
                    return [str(f) for f in fields]
            except Exception:
                pass

        return []

    def read_field(self, field_id: str) -> dict[str, Any]:
        """
        Read a specific field by its name or identifier.

        NOTE (correction — the most dangerous fallback in this file):
        this used to substitute np.random.uniform(250.0, 310.0, (181,
        360)) - literally random data in a plausible temperature
        range, different every call - as the "data" for the requested
        field_id when no real resource was open or the real read
        failed. Now honestly reports that no real read occurred rather
        than returning invented numbers under a real field's name.
        """
        self._require_open()

        if self._resource and hasattr(self._resource, "readfield"):
            try:
                field_obj = self._resource.readfield(field_id)
                data = field_obj.data if hasattr(field_obj, "data") else None
                if data is None:
                    raise ValueError("readfield() returned no data")
                comment = getattr(field_obj, "comment", field_id)
                return {
                    "field_id": field_id,
                    "name": str(comment),
                    "data": data,
                    "shape": data.shape if hasattr(data, "shape") else None,
                    "unit": getattr(field_obj, "units", None),
                    "status": "READ_FROM_EPYGRAM_RESOURCE",
                    "is_real_data": True,
                }
            except Exception:
                pass

        return {
            "field_id": field_id,
            "name": None,
            "data": None,
            "shape": None,
            "unit": None,
            "status": "NOT_READ_NO_REAL_RESOURCE_OPENED",
            "is_real_data": False,
        }

    def read_fields(self, field_ids: list[str]) -> dict[str, dict[str, Any]]:
        """Read multiple fields by their identifiers."""
        results = {}
        for fid in field_ids:
            results[fid] = self.read_field(fid)
        return results

    def metadata(self) -> dict[str, Any]:
        """
        Extract dataset metadata (format, model, validity time, center).

        NOTE (correction): "center": "Météo-France / CNRM" and
        "model": "AROME/ALADIN/ARPEGE" used to be claimed
        unconditionally, regardless of whether any real file
        metadata was ever read - these are now only included when
        genuinely present on the opened resource.
        """
        self._require_open()

        meta: dict[str, Any] = {
            "format": self._format,
            "filepath": str(self.filepath) if self.filepath else "",
            "epygram_available": EPYGRAM_AVAILABLE,
            "is_real_data": self._resource is not None,
        }
        if self._open_failure_reason:
            meta["open_failure_reason"] = self._open_failure_reason

        if self._resource:
            if hasattr(self._resource, "validity"):
                meta["validity"] = str(self._resource.validity)
            if hasattr(self._resource, "header"):
                meta["header"] = str(self._resource.header)

        return meta

    def geometry(self) -> dict[str, Any]:
        """
        Extract spatial grid geometry and domain boundaries.

        NOTE (correction): this used to fall back to a fixed
        Lambert93/France-domain-bounds grid (or a generic regular
        lat-lon grid) regardless of the real file's content when no
        real geometry was available. Now returns an honest empty
        result in that case.
        """
        self._require_open()

        if self._resource and hasattr(self._resource, "geometry"):
            try:
                geom = self._resource.geometry
                dims = getattr(geom, "dimensions", {}) or {}
                grid = getattr(geom, "grid", {}) or {}
                return {
                    "grid_type": getattr(geom, "name", None),
                    "n_lat": dims.get("Y"),
                    "n_lon": dims.get("X"),
                    "resolution_x_meters": grid.get("X"),
                    "resolution_y_meters": grid.get("Y"),
                    "projection": getattr(geom, "projection", None),
                    "is_real_data": True,
                }
            except Exception:
                pass

        return {
            "grid_type": None,
            "n_lat": None,
            "n_lon": None,
            "resolution_x_meters": None,
            "resolution_y_meters": None,
            "projection": None,
            "bounds": None,
            "is_real_data": False,
        }

    def projection(self) -> str | None:
        """Extract spatial projection information."""
        geom = self.geometry()
        return geom.get("projection")

    def time_validity(self) -> dict[str, Any]:
        """
        Extract time validity attributes (basis time, term/lead time, valid time).

        NOTE (correction): this used to unconditionally claim a fixed
        "basis_time: 2026-08-03T00:00:00Z" and "term_hours: 0"
        regardless of whether any real validity was read. Now only
        reports the real validity string when the resource actually
        provided one.
        """
        self._require_open()

        meta = self.metadata()
        validity_str = meta.get("validity")
        return {
            "basis_time": None,
            "term_hours": None,
            "valid_time": validity_str,
            "is_real_data": validity_str is not None,
        }

    def domain(self) -> dict[str, Any]:
        """Extract geographical domain bounding box and dimensions."""
        geom = self.geometry()
        return {
            "bounds": geom.get("bounds"),
            "n_lat": geom.get("n_lat"),
            "n_lon": geom.get("n_lon"),
            "grid_type": geom.get("grid_type"),
            "is_real_data": geom.get("is_real_data", False),
        }

    def vertical_levels(self) -> list[dict[str, Any]]:
        """
        Extract vertical level definitions (hybrid pressure/eta levels).

        NOTE (correction): this used to unconditionally fabricate a
        fixed 90-level hybrid-pressure coordinate table via a formula
        (a_coeff/b_coeff computed from the loop index, not read from
        any file) regardless of the real file's actual vertical
        coordinate - it never even attempted to read a real one. Now
        honestly returns an empty list, since this reader has no real
        vertical-coordinate extraction implemented.
        """
        self._require_open()
        return []

    def read(self, filename: str | Path) -> dict[str, Any]:
        """BaseReader interface method: open file and return structured dataset dictionary."""
        with self.open(filename) as reader:
            fields = reader.list_fields()
            meta = reader.metadata()
            geom = reader.geometry()
            vlevels = reader.vertical_levels()
            return {
                "format": meta["format"],
                "filepath": str(filename),
                "fields": fields,
                "metadata": meta,
                "geometry": geom,
                "vertical_levels_count": len(vlevels),
                "is_real_data": meta.get("is_real_data", False),
            }

    def _detect_format_from_ext(self, path: Path) -> str:
        path_str = str(path).lower()
        if path_str.endswith((".fa", ".fa.gz")):
            return "FA"
        elif path_str.endswith(".lfa"):
            return "LFA"
        elif path_str.endswith(".lfi"):
            return "LFI"
        elif path_str.endswith((".grib", ".grib2", ".grb")):
            return "GRIB"
        elif any(path_str.endswith(ext) for ext in [".nc", ".netcdf"]):
            return "NETCDF"
        return "UNKNOWN"


# -----------------------------------------------------------------------------
# Module-level convenience functions
# -----------------------------------------------------------------------------

_global_reader: EPyGrAMReader | None = None


def open(
    filepath: str | Path,
    must_exist: bool = True,
    strict_epygram: bool = False,
) -> EPyGrAMReader:
    """Module-level convenience function to open a file with EPyGrAMReader."""
    global _global_reader
    _global_reader = EPyGrAMReader()
    return _global_reader.open(filepath, must_exist=must_exist, strict_epygram=strict_epygram)


def close() -> None:
    """Module-level convenience function to close the global EPyGrAMReader."""
    global _global_reader
    if _global_reader:
        _global_reader.close()
        _global_reader = None


def list_fields() -> list[str]:
    """Module-level convenience function to list fields."""
    if not _global_reader:
        raise RuntimeError("No open EPyGrAMReader found. Call open() first.")
    return _global_reader.list_fields()


def read_field(field_id: str) -> dict[str, Any]:
    """Module-level convenience function to read a field."""
    if not _global_reader:
        raise RuntimeError("No open EPyGrAMReader found. Call open() first.")
    return _global_reader.read_field(field_id)


def read_fields(field_ids: list[str]) -> dict[str, dict[str, Any]]:
    """Module-level convenience function to read multiple fields."""
    if not _global_reader:
        raise RuntimeError("No open EPyGrAMReader found. Call open() first.")
    return _global_reader.read_fields(field_ids)


def metadata() -> dict[str, Any]:
    """Module-level convenience function to extract metadata."""
    if not _global_reader:
        raise RuntimeError("No open EPyGrAMReader found. Call open() first.")
    return _global_reader.metadata()


def geometry() -> dict[str, Any]:
    """Module-level convenience function to extract geometry."""
    if not _global_reader:
        raise RuntimeError("No open EPyGrAMReader found. Call open() first.")
    return _global_reader.geometry()


def projection() -> str | None:
    """Module-level convenience function to extract projection."""
    if not _global_reader:
        raise RuntimeError("No open EPyGrAMReader found. Call open() first.")
    return _global_reader.projection()


def time_validity() -> dict[str, Any]:
    """Module-level convenience function to extract time validity."""
    if not _global_reader:
        raise RuntimeError("No open EPyGrAMReader found. Call open() first.")
    return _global_reader.time_validity()


def domain() -> dict[str, Any]:
    """Module-level convenience function to extract domain."""
    if not _global_reader:
        raise RuntimeError("No open EPyGrAMReader found. Call open() first.")
    return _global_reader.domain()


def vertical_levels() -> list[dict[str, Any]]:
    """Module-level convenience function to extract vertical levels."""
    if not _global_reader:
        raise RuntimeError("No open EPyGrAMReader found. Call open() first.")
    return _global_reader.vertical_levels()
