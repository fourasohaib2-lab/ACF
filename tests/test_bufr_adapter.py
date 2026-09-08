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
