from acf.catalogs.ecmwf.catalog import ECMWFCatalog


def test_ecmwf_catalog():

    catalog = ECMWFCatalog()

    catalog.load(
        "src/acf/resources/standards/ecmwf/parameters.json"
    )

    assert catalog.count() >= 4
    assert catalog.exists("t2m")
    assert catalog.get("t2m").unit == "K"
