from acf.catalog.default_catalog import create_catalog


def test_catalog_creation():

    catalog = create_catalog()

    assert catalog.exists("t2m")


def test_parameter_metadata():

    catalog = create_catalog()

    p = catalog.get("t2m")

    assert p.standard_name == "air_temperature"
    assert p.units == "K"
