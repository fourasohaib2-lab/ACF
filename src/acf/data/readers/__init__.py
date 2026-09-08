"""
Atmospheric Complexity Framework (ACF)

DATA READERS - Init Package
"""

from typing import TYPE_CHECKING

from acf.data.readers.epygram_reader import EPyGrAMReader

if TYPE_CHECKING:
    from acf.importers.base.base_reader import BaseReader
    from acf.importers.readers.bufr_reader import BufrReader
    from acf.importers.readers.cf_detector import CFDetector
    from acf.importers.readers.grib_reader import GRIBReader, GribReader
    from acf.importers.readers.netcdf_reader import NetCDFReader

__all__ = [
    "BaseReader",
    "BufrReader",
    "CFDetector",
    "EPyGrAMReader",
    "GRIBReader",
    "GribReader",
    "NetCDFReader",
]


def __getattr__(name: str):
    if name == "BaseReader":
        from acf.importers.base.base_reader import BaseReader

        return BaseReader
    if name == "BufrReader":
        from acf.importers.readers.bufr_reader import BufrReader

        return BufrReader
    if name == "CFDetector":
        from acf.importers.readers.cf_detector import CFDetector

        return CFDetector
    if name in ("GRIBReader", "GribReader"):
        from acf.importers.readers.grib_reader import GRIBReader, GribReader

        return GRIBReader if name == "GRIBReader" else GribReader
    if name == "NetCDFReader":
        from acf.importers.readers.netcdf_reader import NetCDFReader

        return NetCDFReader
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

