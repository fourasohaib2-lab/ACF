import pytest

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
    """
    CORRECTED: used to return gravity*temperature_difference (missing
    the division by a reference temperature that the function's own
    documented formula "B = g * dT / T" requires) - dimensionally
    wrong. Default reference_temperature=288.15 K.
    """
    assert Dynamics.buoyancy(1) == pytest.approx(9.81 / 288.15)
    assert Dynamics.buoyancy(1, reference_temperature=300.0) == pytest.approx(9.81 / 300.0)
    with pytest.raises(ValueError):
        Dynamics.buoyancy(1, reference_temperature=0)


def test_category_weak():
    assert Dynamics.category(1e-7) == "Weak"


def test_category_moderate():
    assert Dynamics.category(1e-5) == "Moderate"


def test_category_strong():
    assert Dynamics.category(1e-3) == "Strong"


def test_zero_density():
    with pytest.raises(ValueError):
        Dynamics.pressure_force(10, 0)


def test_zero_mass():
    with pytest.raises(ValueError):
        Dynamics.acceleration(10, 0)
