from acf.models.ensemble import EnsembleForecast


def test_ensemble():

    ens = EnsembleForecast("GEFS")

    ens.add_member(10)

    ens.add_member(20)

    ens.add_member(30)

    assert ens.count() == 3

    assert ens.mean() == 20

    assert ens.minimum() == 10

    assert ens.maximum() == 30
