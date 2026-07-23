from acf.data.bufr_reader import BufrReader


def test_creation():
    reader = BufrReader()
    assert reader.filename is None
    assert reader.is_open is False


def test_exists_false():
    reader = BufrReader()
    assert reader.exists() is False


def test_variables():
    reader = BufrReader()
    assert reader.variables() == []


def test_coordinates():
    reader = BufrReader()
    assert reader.coordinates() == []


def test_attributes():
    reader = BufrReader()
    assert reader.attributes() == {}


def test_stations():
    reader = BufrReader()
    assert reader.stations() == []


def test_times():
    reader = BufrReader()
    assert reader.times() == []


def test_messages():
    reader = BufrReader()
    assert reader.messages() == 0


def test_close():
    reader = BufrReader()
    reader.close()
    assert reader.is_open is False


def test_repr():
    reader = BufrReader()
    assert "BufrReader" in repr(reader)
