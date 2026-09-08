from acf.model4d.grid4d import Grid4D
from acf.model4d.time_axis import TimeAxis
from acf.model4d.vertical_axis import VerticalAxis


def test_create():

    grid = Grid4D()

    assert grid.time is None


def test_time_axis():

    grid = Grid4D()

    axis = TimeAxis()

    grid.set_time_axis(axis)

    assert grid.time is axis


def test_vertical_axis():

    grid = Grid4D()

    axis = VerticalAxis()

    grid.set_vertical_axis(axis)

    assert grid.vertical is axis


def test_latitudes():

    grid = Grid4D()

    grid.set_latitudes([0, 1, 2])

    assert len(grid.latitudes) == 3


def test_longitudes():

    grid = Grid4D()

    grid.set_longitudes([10, 20])

    assert len(grid.longitudes) == 2


def test_validate():

    grid = Grid4D()

    assert grid.validate() is False

    grid.set_time_axis(TimeAxis())

    grid.set_vertical_axis(VerticalAxis())

    grid.set_latitudes([1])

    grid.set_longitudes([1])

    assert grid.validate() is True


def test_copy():

    grid = Grid4D()

    other = grid.copy()

    assert other is not grid


def test_summary():

    grid = Grid4D()

    summary = grid.summary()

    assert "projection" in summary


def test_repr():

    grid = Grid4D()

    assert "Grid4D" in repr(grid)
