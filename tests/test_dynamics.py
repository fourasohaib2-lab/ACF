from acf.model4d.physics.dynamics import Dynamics


def test_acceleration():
    assert Dynamics.acceleration(10, 2) == 5


def test_momentum():
    assert Dynamics.momentum(5, 4) == 20


def test_kinetic_energy():
    assert Dynamics.kinetic_energy(2, 3) == 9


def test_pressure_force():
    assert Dynamics.pressure_force(100, 2) == -50


def test_buoyancy():
    assert Dynamics.buoyancy(1) == 9.81


def test_category_weak():
    assert Dynamics.category(1e-7) == "Weak"


def test_category_moderate():
    assert Dynamics.category(1e-5) == "Moderate"


def test_category_strong():
    assert Dynamics.category(1e-3) == "Strong"


def test_zero_density():
    try:
        Dynamics.pressure_force(10, 0)
        assert False
    except ValueError:
        assert True


def test_zero_mass():
    try:
        Dynamics.acceleration(10, 0)
        assert False
    except ValueError:
        assert True
