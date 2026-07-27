from acf.model4d.physics.atmospheric_energy_budget_dynamics import (
    AtmosphericEnergyBudgetDynamics,
    EnergyBudgetState,
)



def create_state():

    return EnergyBudgetState(
        solar_input=100,
        infrared_loss=50,
        latent_heat=10,
        sensible_heat=5,
        surface_flux=20,
        cloud_effect=4,
        temperature=20,
    )



def test_solar_energy_gain():

    model = AtmosphericEnergyBudgetDynamics()

    assert model.solar_energy_gain(create_state()) == 5.0



def test_infrared_cooling():

    model = AtmosphericEnergyBudgetDynamics()

    assert model.infrared_cooling(create_state()) == 2.5



def test_latent_heat_transport():

    model = AtmosphericEnergyBudgetDynamics()

    assert model.latent_heat_transport(create_state()) == 2.0



def test_sensible_heat_transport():

    model = AtmosphericEnergyBudgetDynamics()

    assert model.sensible_heat_transport(create_state()) == 1.0



def test_surface_energy_flux():

    model = AtmosphericEnergyBudgetDynamics()

    assert model.surface_energy_flux(create_state()) == 2.0



def test_cloud_energy_feedback():

    model = AtmosphericEnergyBudgetDynamics()

    assert model.cloud_energy_feedback(create_state()) == 2.0



def test_atmospheric_energy_balance():

    model = AtmosphericEnergyBudgetDynamics()

    assert model.atmospheric_energy_balance(create_state()) == 9.5



def test_equilibrium_temperature():

    model = AtmosphericEnergyBudgetDynamics()

    assert model.equilibrium_temperature(create_state()) == 20.95



def test_climate_feedback_index():

    model = AtmosphericEnergyBudgetDynamics()

    assert model.climate_feedback_index(create_state()) == -2.6
