from acf.science.total_totals import TotalTotals


def test_total_totals():

    tt = TotalTotals.calculate(
        t850=20.0,
        td850=15.0,
        t500=-10.0,
    )

    assert tt == 55.0


def test_category_extreme():

    assert (
        TotalTotals.category(60.0)
        == "Extreme"
    )


def test_category_low():

    assert (
        TotalTotals.category(35.0)
        == "Low"
    )
