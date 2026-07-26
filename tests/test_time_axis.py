from datetime import datetime

from acf.model4d.time_axis import TimeAxis


def test_create():

    axis = TimeAxis()

    assert len(axis) == 0


def test_add():

    axis = TimeAxis()

    axis.add("2026-07-26T00:00:00")

    assert len(axis) == 1


def test_first_last():

    axis = TimeAxis()

    axis.add("2026-07-26T00:00:00")

    axis.add("2026-07-26T06:00:00")

    assert axis.first is not None

    assert axis.last is not None


def test_step():

    axis = TimeAxis()

    axis.add("2026-07-26T00:00:00")

    axis.add("2026-07-26T06:00:00")

    assert axis.step_hours == 6


def test_validate():

    axis = TimeAxis()

    assert axis.validate() is False

    axis.add("2026-07-26T00:00:00")

    assert axis.validate() is True


def test_copy():

    axis = TimeAxis()

    axis.add("2026-07-26T00:00:00")

    other = axis.copy()

    assert len(other) == len(axis)


def test_summary():

    axis = TimeAxis()

    axis.add("2026-07-26T00:00:00")

    summary = axis.summary()

    assert summary["count"] == 1


def test_clear():

    axis = TimeAxis()

    axis.add("2026-07-26T00:00:00")

    axis.clear()

    assert len(axis) == 0


def test_repr():

    axis = TimeAxis()

    assert "TimeAxis" in repr(axis)
