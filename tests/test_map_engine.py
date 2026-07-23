from acf.maps.engine import MapEngine


def test_map_engine_creation():
    engine = MapEngine()

    assert engine is not None


def test_default_projection():
    engine = MapEngine()

    assert engine.get_projection() == "PlateCarree"


def test_add_layer():
    engine = MapEngine()

    engine.add_layer("Temperature")

    assert engine.layer_count() == 1


def test_clear_layers():
    engine = MapEngine()

    engine.add_layer("Temperature")
    engine.add_layer("Pressure")

    engine.clear_layers()

    assert engine.layer_count() == 0
