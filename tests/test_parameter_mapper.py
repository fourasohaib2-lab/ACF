from acf.catalog.default_mapping import create_default_mapper


def test_temperature_mapping():

    mapper = create_default_mapper()

    assert mapper.resolve("T2") == "t2m"
    assert mapper.resolve("TMP") == "t2m"
    assert mapper.resolve("2T") == "t2m"
    assert mapper.resolve("air_temperature") == "t2m"


def test_wrf_mapping():

    mapper = create_default_mapper()

    assert mapper.resolve("QVAPOR") == "q"
    assert mapper.resolve("RAINNC") == "tp"
    assert mapper.resolve("RAINC") == "tp"


def test_unknown():

    mapper = create_default_mapper()

    assert mapper.resolve("ABCXYZ") is None
