from acf.standards.hub import StandardsHub


def test_standards_hub():

    hub = StandardsHub()

    assert hub.exists_cf("air_temperature")

    parameters = hub.load_ecmwf("src/acf/resources/standards/ecmwf/parameters.json")

    assert len(parameters) >= 4
    assert parameters[0].code == "t2m"
