from pathlib import Path

from acf.maps.exporter import Exporter


def test_creation():
    exporter = Exporter()
    assert exporter.count() == 0


def test_export():
    exporter = Exporter()

    filename = exporter.export("map.png")

    assert filename == Path("map.png")
    assert exporter.exists("map.png")


def test_remove():
    exporter = Exporter()

    exporter.export("map.png")
    exporter.remove("map.png")

    assert exporter.count() == 0


def test_clear():
    exporter = Exporter()

    exporter.export("map1.png")
    exporter.export("map2.png")

    exporter.clear()

    assert exporter.count() == 0


def test_exports():
    exporter = Exporter()

    exporter.export("map1.png")
    exporter.export("map2.png")

    assert len(exporter.exports()) == 2
