from acf.importers.hub import ImporterHub


def test_load_cf():

    hub = ImporterHub()

    filename = "src/acf/resources/standards/cf/cf_standard_names.json"

    data = hub.load("cf", filename)

    assert isinstance(data, dict)

    assert len(data) > 0
