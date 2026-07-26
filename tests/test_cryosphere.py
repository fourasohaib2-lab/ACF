from acf.model4d.physics.cryosphere import Cryosphere


def test_is_frozen():
    assert Cryosphere.is_frozen(270)
    assert not Cryosphere.is_frozen(280)


def test_melting_rate():
    value = Cryosphere.melting_rate(278)
    assert value > 0


def test_no_melting_below_zero():
    assert Cryosphere.melting_rate(270) == 0


def test_freezing_rate():
    value = Cryosphere.freezing_rate(268)
    assert value > 0


def test_no_freezing_above_zero():
    assert Cryosphere.freezing_rate(280) == 0


def test_albedo_full_ice():
    assert Cryosphere.albedo(1) == 0.85


def test_albedo_water():
    assert Cryosphere.albedo(0) == 0.10


def test_albedo_limit():
    assert 0.10 <= Cryosphere.albedo(0.5) <= 0.85


def test_heat_flux():
    assert Cryosphere.heat_flux(10) == 22


def test_thickness_change():
    assert Cryosphere.thickness_change(2, 5) == 3
