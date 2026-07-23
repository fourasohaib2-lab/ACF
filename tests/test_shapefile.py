from pathlib import Path

from acf.maps.shapefile import ShapeFileManager


def test_creation():
    manager = ShapeFileManager()

    assert manager.count() == 0


def test_add():
    manager = ShapeFileManager()

    manager.add("Countries", "countries.shp")

    assert manager.exists("Countries")


def test_get():
    manager = ShapeFileManager()

    manager.add("Countries", "countries.shp")

    assert manager.get("Countries") == Path("countries.shp")


def test_remove():
    manager = ShapeFileManager()

    manager.add("Countries", "countries.shp")

    manager.remove("Countries")

    assert not manager.exists("Countries")


def test_clear():
    manager = ShapeFileManager()

    manager.add("Countries", "countries.shp")
    manager.add("Rivers", "rivers.shp")

    manager.clear()

    assert manager.count() == 0


def test_names():
    manager = ShapeFileManager()

    manager.add("Countries", "countries.shp")
    manager.add("Rivers", "rivers.shp")

    names = manager.names()

    assert names == ["Countries", "Rivers"]
