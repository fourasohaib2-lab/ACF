from acf.science.lifted_index import LiftedIndex


def test_lifted_index():

    li = LiftedIndex.calculate(
        parcel_temperature=15.0,
        environment_temperature=10.0,
    )

    assert li == -5.0


def test_category():

    assert LiftedIndex.category(-5.0) == "Very Unstable"


def test_stable():

    assert LiftedIndex.category(5.0) == "Stable"
