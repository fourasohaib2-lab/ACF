"""
Tests ACF - Mesoscale Convective Systems
Sprint 8.84
"""

from acf.model4d.physics.mesoscale_convective_systems import (
    MCSState,
    MesoscaleConvectiveSystem,
)


def create_test_system():

    return MesoscaleConvectiveSystem(
        MCSState(
            cape=2000,
            wind_shear=30,
            moisture=80,
            temperature=295,
            precipitation_rate=25,
            organization=90,
        )
    )


def test_energy():

    mcs = create_test_system()

    assert mcs.convective_energy() == 1600


def test_organization():

    mcs = create_test_system()

    assert mcs.organization_index() == 60


def test_precipitation():

    mcs = create_test_system()

    assert mcs.precipitation_intensity() > 0


def test_propagation():

    mcs = create_test_system()

    assert mcs.propagation_speed() > 0


def test_stability():

    mcs = create_test_system()

    assert mcs.stability_index() < 295


def test_simulation():

    mcs = create_test_system()

    result = mcs.simulate()

    assert "convective_energy" in result
    assert "precipitation" in result


def test_state():

    mcs = create_test_system()

    assert isinstance(mcs.state, MCSState)


def test_cape():

    state = MCSState(1000, 10, 50, 280, 5, 50)

    assert state.cape == 1000


def test_example():

    from acf.model4d.physics.mesoscale_convective_systems import create_example_mcs

    assert create_example_mcs() is not None


def test_positive_values():

    mcs = create_test_system()

    assert mcs.precipitation_intensity() >= 0
