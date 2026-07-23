from acf.standards.ecmwf.catalog import ECMWF_PARAMETERS


def test_catalog():

    assert isinstance(ECMWF_PARAMETERS, dict)
