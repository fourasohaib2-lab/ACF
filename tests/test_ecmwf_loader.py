from acf.standards.ecmwf.loader import ECMWFLoader


def test_loader():

    loader = ECMWFLoader()

    data = loader.load(
        "src/acf/resources/standards/ecmwf/parameters.json"
    )

    assert "t2m" in data
    assert data["t2m"]["unit"] == "K"
    assert data["u10"]["category"] == "Wind"

