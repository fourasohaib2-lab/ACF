from acf.importers.cf.importer import CFImporter


def test_cf_importer():

    importer = CFImporter()

    filename = "src/acf/resources/standards/cf/cf_standard_names.json"

    assert importer.validate(filename)

    data = importer.load(filename)

    assert isinstance(data, dict)

    assert len(data) > 0
