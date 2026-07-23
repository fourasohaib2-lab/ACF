from acf.maps.projection import Projection


def test_creation():

    p = Projection()

    assert p is not None


def test_default_projection():

    p = Projection()

    assert p.current() == "PlateCarree"


def test_change_projection():

    p = Projection()

    p.set("Mercator")

    assert p.current() == "Mercator"


def test_available():

    p = Projection()

    assert "PlateCarree" in p.available()
    assert "Mercator" in p.available()


def test_exists():

    p = Projection()

    assert p.exists("Robinson")
    assert not p.exists("UnknownProjection")


def test_count():

    p = Projection()

    assert p.count() >= 5


def test_reset():

    p = Projection()

    p.set("Mercator")
    p.reset()

    assert p.current() == "PlateCarree"
