from acf.model4d.physics.physics_coupler import CouplingState, PhysicsCoupler


def create_state():

    return CouplingState(
        temperature=300, humidity=12, pressure=100000, radiation=500, vertical_velocity=10, cloud_water=2, energy=1000
    )


def test_engine_creation():

    model = PhysicsCoupler()

    assert model.name == ("ACF Model4D Physics Coupling Engine")


def test_moisture_temperature_feedback():

    model = PhysicsCoupler()

    result = model.moisture_temperature_feedback(create_state())

    assert result > 12


def test_radiation_balance():

    model = PhysicsCoupler()

    result = model.radiation_energy_balance(create_state())

    assert result > 0


def test_latent_heat_exchange():

    model = PhysicsCoupler()

    result = model.latent_heat_exchange(create_state())

    assert isinstance(result, float)


def test_convection_feedback():

    model = PhysicsCoupler()

    result = model.convection_feedback(create_state())

    assert result > 0


def test_total_coupled_energy():

    model = PhysicsCoupler()

    result = model.coupled_energy(create_state())

    assert result > 1000
