from acf.model4d.physics.atmospheric_cloud_microphysics_dynamics import (
    AtmosphericCloudMicrophysicsDynamics,
    CloudMicrophysicsState,
)


def create_state():

    return CloudMicrophysicsState(
        humidity=80,
        temperature=-10,
        condensation_rate=5,
        aerosol_concentration=20,
        cloud_water=6,
        ice_content=4,
    )


def test_cloud_formation():

    model = AtmosphericCloudMicrophysicsDynamics()

    assert model.cloud_formation(create_state()) == 4.0


def test_condensation():

    model = AtmosphericCloudMicrophysicsDynamics()

    assert model.condensation_process(create_state()) == 40.0


def test_nucleation():

    model = AtmosphericCloudMicrophysicsDynamics()

    assert model.droplet_nucleation(create_state()) == 16.0


def test_ice_growth():

    model = AtmosphericCloudMicrophysicsDynamics()

    assert model.ice_crystal_growth(create_state()) == 0.4


def test_precipitation():

    model = AtmosphericCloudMicrophysicsDynamics()

    assert model.precipitation_generation(create_state()) == 10


def test_aerosol_interaction():

    model = AtmosphericCloudMicrophysicsDynamics()

    assert model.aerosol_cloud_interaction(create_state()) == 1.2


def test_cloud_radiative_effect():

    model = AtmosphericCloudMicrophysicsDynamics()

    assert model.cloud_radiative_effect(create_state()) == -1.0
