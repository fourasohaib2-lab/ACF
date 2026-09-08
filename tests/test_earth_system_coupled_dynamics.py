from acf.model4d.physics.earth_system_coupled_dynamics import EarthSystemCoupledDynamics, EarthSystemState


def test_initialization():

    model = EarthSystemCoupledDynamics()

    assert model.name == "Earth System Coupled Dynamics"


def test_energy_balance():

    model = EarthSystemCoupledDynamics()

    state = EarthSystemState(atmospheric_energy=100, ocean_energy=50, ice_fraction=0.5, greenhouse_forcing=20)

    balance = model.calculate_energy_balance(state)

    assert isinstance(balance, float)


def test_simulation():

    model = EarthSystemCoupledDynamics()

    state = EarthSystemState(atmospheric_energy=100, ocean_energy=50, ice_fraction=0.4, greenhouse_forcing=30)

    new_state = model.simulate(state)

    assert isinstance(new_state, EarthSystemState)


def test_feedback():

    model = EarthSystemCoupledDynamics()

    state = EarthSystemState(atmospheric_energy=100, ocean_energy=50, ice_fraction=0.2, greenhouse_forcing=40)

    index = model.climate_feedback_index(state)

    assert index > 0
