from acf.model4d.physics.atmospheric_aerosol_dynamics import (
    AtmosphericAerosolDynamics,
    AerosolState,
)


def create_state():

    return AerosolState(
        dust_loading=5,
        volcanic_aerosol=2,
        pollution_level=4,
        wind_speed=10,
        humidity=50,
        cloud_fraction=0.8,
    )


def test_dust_transport():

    model = AtmosphericAerosolDynamics()

    assert model.dust_transport(create_state()) == 5


def test_volcanic_effect():

    model = AtmosphericAerosolDynamics()

    assert model.volcanic_aerosol_effect(create_state()) == 1.6


def test_pollution():

    model = AtmosphericAerosolDynamics()

    assert model.anthropogenic_pollution(create_state()) == 2


def test_cloud_interaction():

    model = AtmosphericAerosolDynamics()

    assert model.aerosol_cloud_interaction(create_state()) == 7.2


def test_radiative_forcing():

    model = AtmosphericAerosolDynamics()

    assert model.aerosol_radiative_forcing(create_state()) == -0.5


def test_particle_transport():

    model = AtmosphericAerosolDynamics()

    assert model.particle_transport(create_state()) == 0.25
