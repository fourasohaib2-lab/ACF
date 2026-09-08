"""
BUFR Reader
"""

from pathlib import Path


class BufrReader:
    """Simple BUFR reader.

    NOTE (correction — undisclosed stub, found during the post-model4d
    audit, 2026-09-06): `open()` only records `self.filename` and sets
    `is_open = True` - it never actually opens or parses any real BUFR
    content (no BUFR-decoding library, e.g. eccodes/pybufrkit, is used
    anywhere in this class). `variables()`, `coordinates()`,
    `attributes()`, `stations()`, `times()` and `messages()` are
    unconditionally empty/zero regardless of what a real opened file
    actually contains - not previously disclosed as such. Not wired
    into ReaderFactory/ReaderRegistry/DataManager for real `.bufr`
    dispatch (verified via grep - no caller in `src/` routes a real
    file to this class), and `tests/test_bufr_reader.py` only ever
    exercises the reader's unopened default state, so this was a real
    but previously-inert gap, not a behavior change for any existing
    caller. Left unimplemented rather than fabricating a fake decode -
    a real fix needs an actual BUFR-decoding dependency this project
    does not have yet.
    """

    def __init__(self, filename=None):
        self.filename = filename
        self.file = None
        self.is_open = False

    def open(self, filename=None):
        if filename is not None:
            self.filename = filename

        if self.filename is None:
            raise ValueError("No BUFR file specified.")

        self.file = Path(self.filename)
        self.is_open = True

    def close(self):
        self.file = None
        self.is_open = False

    def exists(self):
        if self.filename is None:
            return False
        return Path(self.filename).exists()

    def variables(self):
        return []

    def coordinates(self):
        return []

    def attributes(self):
        return {}

    def stations(self):
        return []

    def times(self):
        return []

    def messages(self):
        return 0

    def __repr__(self):
        return f"BufrReader(open={self.is_open})"
