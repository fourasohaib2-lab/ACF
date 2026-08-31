from acf.model4d.domain4d import Domain4D
from acf.model4d.field4d import Field4D


def test_create():

    field = Field4D()

    assert field.domain is None


def test_set_domain():

    field = Field4D()

    domain = Domain4D()

    field.set_domain(domain)

    assert field.domain is domain


def test_set_values():

    field = Field4D()

    field.set_values([1, 2, 3])

    assert field.values == [1, 2, 3]


def test_validate():

    field = Field4D()

    assert field.validate() is False

    field.name = "temperature"

    field.set_domain(Domain4D())

    field.set_values([1])

    assert field.validate() is True


def test_copy():

    field = Field4D()

    other = field.copy()

    assert other is not field


def test_summary():

    field = Field4D()

    summary = field.summary()

    assert "unit" in summary


def test_repr():

    field = Field4D()

    assert "Field4D" in repr(field)


def test_metadata():

    field = Field4D()

    field.metadata["author"] = "ACF"

    assert field.metadata["author"] == "ACF"
