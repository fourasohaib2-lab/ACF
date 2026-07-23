from acf.importers.hub import ImporterHub


def test_auto_import():

    hub = ImporterHub()

    filename = "src/acf/resources/standards/cf/cf_standard_names.json"

    data = hub.auto_load(filename)

    assert isinstance(data, dict)

    assert len(data) > 0
