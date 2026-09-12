from pathlib import Path

from acf.data.integration.bufr_adapter import BUFRAdapter


def test_adapter():

    adapter = BUFRAdapter()

    adapter.open(Path("/tmp/obs.bufr"))

    assert adapter.suffix == ".bufr"

    assert adapter.is_bufr()


def test_not_existing():

    adapter = BUFRAdapter()

    adapter.open(Path("/tmp/data.buf"))

    assert adapter.exists is False

    assert adapter.is_bufr()


def test_load_honestly_discloses_it_is_not_a_real_decode():
    """Regression guard (2026-09-12 ICAO/WMO compliance audit): load()
    used to silently return an empty-but-well-formed Dataset with no
    disclosure - a future real caller could mistake this for genuinely
    decoded (but empty) BUFR content."""
    adapter = BUFRAdapter()

    dataset = adapter.load(Path("/tmp/obs.bufr"))

    assert dataset.metadata["is_real_data"] is False
    assert dataset.variables == {}
