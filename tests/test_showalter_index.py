from acf.science.showalter_index import ShowalterIndex


def test_showalter():

    si = ShowalterIndex.calculate(
        parcel_temperature_500=14.0,
        environment_temperature_500=10.0,
    )

    assert si == -4.0


def test_category():

    assert ShowalterIndex.category(-4.0) == "Very Unstable"


def test_stable():

    assert ShowalterIndex.category(5.0) == "Stable"
