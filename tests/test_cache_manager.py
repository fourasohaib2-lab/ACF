from pathlib import Path

from acf.data.cache_manager import CacheManager
from acf.data.dataset import Dataset


def test_cache():

    cache = CacheManager()

    ds = Dataset(
        name="ERA5",
        filepath=Path("/tmp/test.nc"),
        filetype="NetCDF"
    )

    cache.add("era5", ds)

    assert cache.exists("era5")

    assert cache.size() == 1

    loaded = cache.get("era5")

    assert loaded.name == "ERA5"

    cache.remove("era5")

    assert cache.size() == 0
from pathlib import Path

from acf.data.cache_manager import CacheManager
from acf.data.dataset import Dataset


def test_cache():

    cache = CacheManager(max_items=2)

    ds1 = Dataset(
        name="ERA5",
        filepath=Path("/tmp/a.nc"),
        filetype="NetCDF"
    )

    ds2 = Dataset(
        name="GFS",
        filepath=Path("/tmp/b.nc"),
        filetype="NetCDF"
    )

    ds3 = Dataset(
        name="ICON",
        filepath=Path("/tmp/c.nc"),
        filetype="NetCDF"
    )

    cache.add("a", ds1)
    cache.add("b", ds2)

    assert cache.size() == 2

    cache.get("a")

    cache.add("c", ds3)

    assert cache.exists("a")
    assert cache.exists("c")
    assert not cache.exists("b")
