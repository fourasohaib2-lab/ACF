from acf.data.grib_reader import GribReader


def test_creation():

    reader = GribReader()

    assert reader.dataset is None


def test_variables():

    reader = GribReader()

    assert reader.variables() == []


def test_dimensions():

    reader = GribReader()

    assert reader.dimensions() == {}


def test_close():

    reader = GribReader()

    reader.close()

    assert reader.dataset is None


def test_repr():

    reader = GribReader()

    assert "GribReader" in repr(reader)
