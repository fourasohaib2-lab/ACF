from acf.catalog.default_catalog import create_catalog


def test_atmosphere():

    catalog = create_catalog()

    assert catalog.exists("t")
    assert catalog.exists("u")
    assert catalog.exists("v")
    assert catalog.exists("w")
    assert catalog.exists("gh")
    assert catalog.exists("vo")
    assert catalog.exists("clwc")
    assert catalog.exists("ciwc")
    assert catalog.exists("graupel")

    assert len(catalog.all()) >= 30
