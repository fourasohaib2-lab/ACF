from acf.model4d.vertical_axis import VerticalAxis


def test_create():

    axis = VerticalAxis()

    assert len(axis) == 0


def test_add():

    axis = VerticalAxis()

    axis.add(1000)

    axis.add(925)

    assert len(axis) == 2


def test_first_last():

    axis = VerticalAxis()

    axis.add(1000)

    axis.add(850)

    assert axis.first == 1000

    assert axis.last == 850


def test_validate():

    axis = VerticalAxis()

    assert axis.validate() is False

    axis.add(1000)

    assert axis.validate() is True


def test_copy():

    axis = VerticalAxis()

    axis.add(1000)

    other = axis.copy()

    assert len(other) == len(axis)


def test_summary():

    axis = VerticalAxis()

    axis.add(1000)

    summary = axis.summary()

    assert summary["count"] == 1


def test_clear():

    axis = VerticalAxis()

    axis.add(1000)

    axis.clear()

    assert len(axis) == 0


def test_repr():

    axis = VerticalAxis()

    assert "VerticalAxis" in repr(axis)
