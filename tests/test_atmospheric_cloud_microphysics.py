from acf.model4d.physics.atmospheric_cloud_microphysics import (
    AtmosphericCloudMicrophysics,
    CloudMicrophysicsState,
)


def create_state():

    return CloudMicrophysicsState(
        liquid_water_content=5,
        ice_content=2,
        temperature=-10,
        droplet_radius=0.5,
        ice_nuclei=4,
        updraft_velocity=3,
    )


def test_droplet_growth():

    model = AtmosphericCloudMicrophysics()

    assert model.droplet_growth(create_state()) == 2.5


def test_ice_crystal_formation():

    model = AtmosphericCloudMicrophysics()

    assert model.ice_crystal_formation(create_state()) == 4.0


def test_bergeron_process():

    model = AtmosphericCloudMicrophysics()

    assert model.bergeron_process(create_state()) == 10


def test_collision_coalescence():

    model = AtmosphericCloudMicrophysics()

    assert model.collision_coalescence(create_state()) == 1.5


def test_precipitation_efficiency():

    model = AtmosphericCloudMicrophysics()

    assert model.precipitation_efficiency(create_state()) == 0.7


def test_phase_transition():

    model = AtmosphericCloudMicrophysics()

    assert model.phase_transition(create_state()) == 12
