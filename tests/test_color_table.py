from acf.maps.styles.color_table import ColorTable


def test_creation():
    table = ColorTable()

    assert table.count() == 0


def test_add():
    table = ColorTable()

    table.add("temperature", "coolwarm")

    assert table.exists("temperature")


def test_get():
    table = ColorTable()

    table.add("temperature", "coolwarm")

    assert table.get("temperature") == "coolwarm"


def test_remove():
    table = ColorTable()

    table.add("temperature", "coolwarm")

    table.remove("temperature")

    assert not table.exists("temperature")


def test_variables():
    table = ColorTable()

    table.add("temperature", "coolwarm")
    table.add("pressure", "viridis")

    assert table.variables() == [
        "pressure",
        "temperature",
    ]


def test_count():
    table = ColorTable()

    table.add("a", "x")
    table.add("b", "y")

    assert table.count() == 2


def test_clear():
    table = ColorTable()

    table.add("temperature", "coolwarm")

    table.clear()

    assert table.count() == 0


def test_repr():
    table = ColorTable()

    assert "ColorTable" in repr(table)
