"""
Atmospheric Complexity Framework (ACF)

GRIB Adapter

NOTE (correction — undisclosed empty-shell load, found during the
2026-09-12 ICAO/WMO compliance audit): same gap as this package's own
`bufr_adapter.py` (see that module's NOTE for the full finding) -
`load()` used to unconditionally return a well-formed-looking `Dataset`
regardless of the actual GRIB file content, with no disclosure. Unlike
BUFR, this codebase DOES have real GRIB decoding elsewhere
(`acf.data.grib_reader`/`acf.data.readers.grib_reader`/`acf.importers.
readers.grib_reader`, all via eccodes/cfgrib) - this specific adapter
(part of the orphaned `AdapterFactory` family, no caller outside its
own tests, verified via grep) just never called any of them.
`metadata["is_real_data"]` now honestly discloses this.
"""

from pathlib import Path

from acf.data.dataset import Dataset


class GRIBAdapter:
    supported_extensions = [
        ".grib",
        ".grb",
        ".grib2",
        ".grb2",
    ]

    def __init__(self):

        self.filename = None

    def open(self, filename):

        self.filename = Path(filename)

        return self.filename

    @property
    def exists(self):

        return self.filename is not None and self.filename.exists()

    @property
    def suffix(self):

        if self.filename is None:
            return ""

        return self.filename.suffix.lower()

    def is_grib(self):

        return self.suffix in self.supported_extensions

    def supports(self, filepath):

        return Path(filepath).suffix.lower() in self.supported_extensions

    def load(self, filepath):
        """Returns a Dataset shell, NOT a real decode - see module NOTE.
        A real caller should use acf.data.grib_reader instead (eccodes/
        cfgrib-backed); `metadata["is_real_data"]` is honestly False
        here since this adapter itself never calls it."""
        filepath = Path(filepath)

        dataset = Dataset(
            name=filepath.stem,
            filepath=filepath,
            filetype="GRIB",
        )
        dataset.metadata["is_real_data"] = False
        dataset.metadata["not_implemented_reason"] = (
            "This adapter never invokes this codebase's real GRIB decoding "
            "(acf.data.grib_reader, eccodes/cfgrib-backed) - use that reader directly "
            "for real GRIB content."
        )
        return dataset
