from acf.maps.layers.vector_layer import VectorLayer


def test_creation():
    layer = VectorLayer("Roads")

    assert layer.name == "Roads"
    assert layer.count() == 0


def test_add_feature():
    layer = VectorLayer()

    feature = {"type": "Point"}

    layer.add_feature(feature)

    assert layer.count() == 1


def test_remove_feature():
    layer = VectorLayer()

    feature = {"type": "Point"}

    layer.add_feature(feature)
    layer.remove_feature(feature)

    assert layer.count() == 0


def test_get_features():
    layer = VectorLayer()

    feature = {"type": "LineString"}

    layer.add_feature(feature)

    assert feature in layer.get_features()


def test_clear():
    layer = VectorLayer()

    layer.add_feature({"id": 1})
    layer.add_feature({"id": 2})

    layer.clear()

    assert layer.count() == 0


def test_repr():
    layer = VectorLayer()

    assert "VectorLayer" in repr(layer)
