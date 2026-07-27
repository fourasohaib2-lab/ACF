from acf.model4d.physics.atmospheric_thermodynamics_dynamics import (
    AtmosphericThermodynamicsDynamics,
    ThermodynamicState,
)



def create_state():

    return ThermodynamicState(
        temperature=300,
        pressure=1000,
        humidity=50,
        air_density=1.2,
        vertical_velocity=10,
        lapse_rate=6.5,
        heat_capacity=1005,
        altitude=1000,
    )



def test_potential_temperature():

    model = AtmosphericThermodynamicsDynamics()

    assert model.potential_temperature(create_state()) == 300.0



def test_internal_energy():

    model = AtmosphericThermodynamicsDynamics()

    assert model.internal_energy(create_state()) == 301.5



def test_atmospheric_enthalpy():

    model = AtmosphericThermodynamicsDynamics()

    assert model.atmospheric_enthalpy(create_state()) == 387.61



def test_lapse_rate_effect():

    model = AtmosphericThermodynamicsDynamics()

    assert model.lapse_rate_effect(create_state()) == 6.5



def test_atmospheric_stability():

    model = AtmosphericThermodynamicsDynamics()

    assert model.atmospheric_stability(create_state()) == 3.3



def test_convection_intensity():

    model = AtmosphericThermodynamicsDynamics()

    assert model.convection_intensity(create_state()) == 5.0



def test_heat_exchange():

    model = AtmosphericThermodynamicsDynamics()

    assert model.heat_exchange(create_state()) == 36.0



def test_thermodynamic_equilibrium():

    model = AtmosphericThermodynamicsDynamics()

    assert model.thermodynamic_equilibrium(create_state()) == 981.11
