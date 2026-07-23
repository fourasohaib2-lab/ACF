from acf.core.default_parameters import create_registry


def test_registry():

    registry = create_registry()

    assert registry.exists("t2m")


def test_parameter():

    registry = create_registry()

    t = registry.get("t2m")

    assert t.units == "°C"

    assert t.renderer == "Raster"


def test_categories():

    registry = create_registry()

    assert "Surface" in registry.categories()
