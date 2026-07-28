from acf.model4d.physics.advanced_climate_coupling import (
    AdvancedClimateCoupling,
    AdvancedClimateState,
)


def create_state():

    return AdvancedClimateState(
        temperature=300,
        humidity=15,
        cloud_cover=30,
        radiation_flux=260,
        convection=3,
        precipitation=8,
        ocean_feedback=20,
        surface_energy=350,
    )


def test_atmosphere_ocean_coupling():

    model = AdvancedClimateCoupling()

    assert (
        model.atmosphere_ocean_coupling(create_state())
        == 18.5
    )


def test_cloud_feedback_coupling():

    model = AdvancedClimateCoupling()

    assert (
        model.cloud_feedback_coupling(create_state())
        == 245
    )


def test_radiation_energy_balance():

    model = AdvancedClimateCoupling()

    assert (
        model.radiation_energy_balance(create_state())
        == 310.0
    )


def test_moisture_climate_coupling():

    model = AdvancedClimateCoupling()

    assert (
        model.moisture_climate_coupling(create_state())
        == 7.5
    )


def test_ocean_heat_transport():

    model = AdvancedClimateCoupling()

    assert (
        model.ocean_heat_transport(create_state())
        == 35.0
    )


def test_climate_stability_index():

    model = AdvancedClimateCoupling()

    assert (
        model.climate_stability_index(create_state())
        == 12.8
    )
