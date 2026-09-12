"""
Atmospheric Complexity Framework (ACF)

BUFR Adapter

NOTE (correction — undisclosed empty-shell load, found during the
2026-09-12 ICAO/WMO compliance audit): `load()` used to unconditionally
return a well-formed-looking `Dataset` (real `.variables`/`.dimensions`/
`.metadata` dicts, all silently empty) regardless of what the actual
BUFR file contains - no BUFR-decoding library is used anywhere in this
adapter, and this class is not wired into any real caller today
(`AdapterFactory` itself has no caller outside its own tests, verified
via grep) - but a future caller would have no way to tell "genuinely
empty file" from "we never decoded it". Same underlying gap as
`acf.importers.readers.bufr_reader.BufrReader`'s own already-disclosed
stub (2026-09-06 audit) - this codebase has no real BUFR-decoding
dependency (e.g. eccodes/pybufrkit) yet. `metadata["is_real_data"]` now
honestly discloses this rather than leaving a silent trap.
"""

from pathlib import Path

from acf.data.dataset import Dataset


class BUFRAdapter:
    supported_extensions = [
        ".bufr",
        ".buf",
        ".bfr",
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

    def is_bufr(self):

        return self.suffix in self.supported_extensions

    def supports(self, filepath):

        return Path(filepath).suffix.lower() in self.supported_extensions

    def load(self, filepath):
        """Returns a Dataset shell, NOT a real decode - see module NOTE.
        `metadata["is_real_data"]` is honestly False; `.variables` stays
        empty because no BUFR-decoding dependency is available yet."""
        filepath = Path(filepath)

        dataset = Dataset(
            name=filepath.stem,
            filepath=filepath,
            filetype="BUFR",
        )
        dataset.metadata["is_real_data"] = False
        dataset.metadata["not_implemented_reason"] = (
            "No BUFR-decoding dependency (e.g. eccodes/pybufrkit) available in this "
            "codebase yet - see acf.importers.readers.bufr_reader.BufrReader's own "
            "docstring for the same disclosed gap."
        )
        return dataset
