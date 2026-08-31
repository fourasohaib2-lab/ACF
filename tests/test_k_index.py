from acf.science.k_index import KIndex


def test_k_index():

    ki = KIndex.calculate(
        t850=20.0,
        t700=8.0,
        t500=-10.0,
        td850=15.0,
        td700=4.0,
    )

    assert ki == 41.0


def test_category_extreme():

    assert KIndex.category(42.0) == "Extreme"


def test_category_low():

    assert KIndex.category(20.0) == "Low"
