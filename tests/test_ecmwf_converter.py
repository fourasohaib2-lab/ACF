from acf.standards.ecmwf.converter import ECMWFConverter


def test_converter():

    converter = ECMWFConverter()

    parameter = converter.convert(
        "t2m",
        {
            "name": "2 metre temperature",
            "unit": "K",
            "standard_name": "air_temperature",
            "category": "Temperature",
        },
    )

    assert parameter.code == "t2m"
    assert parameter.unit == "K"
    assert parameter.category == "Temperature"
