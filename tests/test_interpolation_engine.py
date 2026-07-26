from acf.model4d.interpolation.interpolation_engine import (
    InterpolationEngine,
)


def test_create():

    engine = InterpolationEngine()

    assert engine.algorithm == "nearest"


def test_nearest():

    engine = InterpolationEngine()

    data = [1, 2, 3]

    assert engine.nearest(data) == data


def test_linear():

    engine = InterpolationEngine()

    data = [4, 5]

    assert engine.linear(data) == data


def test_bilinear():

    engine = InterpolationEngine()

    data = [[1, 2], [3, 4]]

    assert engine.bilinear(data) == data


def test_interpolate_nearest():

    engine = InterpolationEngine()

    assert engine.interpolate([1], "nearest") == [1]


def test_interpolate_linear():

    engine = InterpolationEngine()

    assert engine.interpolate([1], "linear") == [1]


def test_methods():

    engine = InterpolationEngine()

    assert "nearest" in engine.available_methods()


def test_summary():

    engine = InterpolationEngine()

    summary = engine.summary()

    assert "methods" in summary


def test_repr():

    engine = InterpolationEngine()

    assert "InterpolationEngine" in repr(engine)

