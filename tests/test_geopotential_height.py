from acf.science.geopotential_height import GeopotentialHeight


def test_geopotential_height():
    z = GeopotentialHeight.calculate(9806.65)

    assert round(z, 2) == 1000.00


def test_zero():
    assert GeopotentialHeight.calculate(0.0) == 0.0
