from acf.model4d.physics.arctic_atmosphere_dynamics import ArcticAtmosphereDynamicsPhysics


def test_temperature_gradient():
    assert ArcticAtmosphereDynamicsPhysics.arctic_temperature_gradient(250, 240) == 10


def test_polar_vortex_strength():
    assert ArcticAtmosphereDynamicsPhysics.polar_vortex_strength(20, 5) == 100


def test_sea_ice_feedback():
    assert ArcticAtmosphereDynamicsPhysics.sea_ice_feedback(0.8, 0.5) == 0.30000000000000004


def test_arctic_amplification():
    assert ArcticAtmosphereDynamicsPhysics.arctic_amplification(1, 3) == 3


def test_katabatic_wind_speed():
    assert ArcticAtmosphereDynamicsPhysics.katabatic_wind_speed(10, 2) == 20


def test_boundary_layer():
    assert ArcticAtmosphereDynamicsPhysics.polar_boundary_layer(20, 2) == 10


def test_albedo_feedback():
    assert ArcticAtmosphereDynamicsPhysics.albedo_feedback(1000, 0.3) == 300


def test_jet_stream_shift():
    assert ArcticAtmosphereDynamicsPhysics.jet_stream_shift(5, 2) == 3


def test_cold_air_outbreak():
    assert ArcticAtmosphereDynamicsPhysics.cold_air_outbreak_index(100, 2) == 200


def test_energy_balance():
    assert ArcticAtmosphereDynamicsPhysics.arctic_energy_balance(500, 200) == 300
