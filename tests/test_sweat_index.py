from acf.science.sweat_index import SWEATIndex


def test_sweat():

    value = SWEATIndex.calculate(
        td850=18,
        tt=52,
        wind850=25,
        wind500=50,
        dir850=170,
        dir500=240,
    )

    assert value > 0


def test_category():

    assert SWEATIndex.category(100) == "Low"

    assert SWEATIndex.category(250) == "Moderate"

    assert SWEATIndex.category(350) == "High"

    assert SWEATIndex.category(500) == "Extreme"

