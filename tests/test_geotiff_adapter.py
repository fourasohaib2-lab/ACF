from pathlib import Path

from acf.data.integration.geotiff_adapter import GeoTIFFAdapter


def test_geotiff_adapter():

    adapter = GeoTIFFAdapter()

    ds = adapter.load(Path("/tmp/world.tif"))

    assert ds.name == "world"
    assert ds.filetype == "GeoTIFF"


def test_geotiff_support():

    adapter = GeoTIFFAdapter()

    assert adapter.supports(Path("map.tif"))
    assert adapter.supports(Path("map.tiff"))
    assert not adapter.supports(Path("map.nc"))
