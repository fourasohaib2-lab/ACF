from pathlib import Path

from acf.data.integration.csv_adapter import CSVAdapter


def test_csv_adapter():

    adapter = CSVAdapter()

    ds = adapter.load(Path("/tmp/test.csv"))

    assert ds.name == "test"

    assert ds.filetype == "CSV"


def test_csv_support():

    adapter = CSVAdapter()

    assert adapter.supports(Path("file.csv"))

    assert not adapter.supports(Path("file.nc"))
from pathlib import Path

from acf.data.integration.csv_adapter import CSVAdapter


def test_csv_adapter():

    adapter = CSVAdapter()

    ds = adapter.load(Path("/tmp/observations.csv"))

    assert ds.name == "observations"
    assert ds.filetype == "CSV"


def test_csv_support():

    adapter = CSVAdapter()

    assert adapter.supports(Path("file.csv"))
    assert not adapter.supports(Path("file.nc"))
