from pathlib import Path

from acf.data.integration.xml_adapter import XMLAdapter


def test_xml_adapter():

    adapter = XMLAdapter()

    ds = adapter.load(Path("/tmp/sample.xml"))

    assert ds.name == "sample"
    assert ds.filetype == "XML"


def test_xml_support():

    adapter = XMLAdapter()

    assert adapter.supports(Path("file.xml"))
    assert not adapter.supports(Path("file.nc"))
