from acf.model4d.domain4d import Domain4D
from acf.model4d.grid4d import Grid4D


def test_create():

    domain = Domain4D()

    assert domain.grid is None


def test_grid():

    domain = Domain4D()

    grid = Grid4D()

    domain.set_grid(grid)

    assert domain.grid is grid


def test_validate():

    domain = Domain4D()

    assert domain.validate() is False

    domain.name = "Europe"

    domain.set_grid(Grid4D())

    assert domain.validate() is True


def test_copy():

    domain = Domain4D()

    other = domain.copy()

    assert other is not domain


def test_summary():

    domain = Domain4D()

    summary = domain.summary()

    assert "projection" in summary


def test_repr():

    domain = Domain4D()

    assert "Domain4D" in repr(domain)


def test_metadata():

    domain = Domain4D()

    domain.metadata["author"] = "ACF"

    assert domain.metadata["author"] == "ACF"


def test_resolution():

    domain = Domain4D()

    domain.resolution = "2.5 km"

    assert domain.resolution == "2.5 km"
