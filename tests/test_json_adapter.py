from pathlib import Path

from acf.data.integration.json_adapter import JSONAdapter


def test_json_adapter():

    adapter = JSONAdapter()

    ds = adapter.load(Path("/tmp/config.json"))

    assert ds.name == "config"
    assert ds.filetype == "JSON"


def test_json_support():

    adapter = JSONAdapter()

    assert adapter.supports(Path("file.json"))
    assert not adapter.supports(Path("file.nc"))
