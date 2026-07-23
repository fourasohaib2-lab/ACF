from acf.standards.cf_standard_names import CF_STANDARD_NAMES


def test_cf():

    assert "air_temperature" in CF_STANDARD_NAMES

    assert CF_STANDARD_NAMES["air_temperature"]["unit"] == "K"

    assert CF_STANDARD_NAMES["eastward_wind"]["category"] == "Wind"
