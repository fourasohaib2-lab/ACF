from acf.science.virtual_temperature import VirtualTemperature


def test_virtual_temperature():
    tv = VirtualTemperature.calculate(
        temperature=300.0,
        specific_humidity=0.010,
    )

    assert round(tv, 2) == 301.83


def test_dry_air():
    tv = VirtualTemperature.calculate(
        temperature=300.0,
        specific_humidity=0.0,
    )

    assert tv == 300.0
