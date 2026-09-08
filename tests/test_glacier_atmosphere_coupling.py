from acf.model4d.physics.glacier_atmosphere_coupling import GlacierAtmosphereCouplingPhysics


def test_glacier_melt_energy():
    value = GlacierAtmosphereCouplingPhysics.glacier_melt_energy(334000, 334000)
    assert value == 1


def test_albedo_feedback():
    value = GlacierAtmosphereCouplingPhysics.albedo_feedback(1000, 0.8)
    assert value == 200


def test_temperature_change():
    value = GlacierAtmosphereCouplingPhysics.glacier_temperature_change(100, 20)
    assert value == 5


def test_sublimation_rate():
    value = GlacierAtmosphereCouplingPhysics.sublimation_rate(100, 10)
    assert value == 10


def test_meltwater_generation():
    value = GlacierAtmosphereCouplingPhysics.meltwater_generation(500, 0.2)
    assert value == 100


def test_energy_balance():
    value = GlacierAtmosphereCouplingPhysics.glacier_energy_balance(500, 200)
    assert value == 300


def test_glacier_retreat():
    value = GlacierAtmosphereCouplingPhysics.glacier_retreat(100, 10)
    assert value == 10


def test_atmospheric_effect():
    value = GlacierAtmosphereCouplingPhysics.atmospheric_warming_effect(50, 2)
    assert value == 100


def test_surface_temperature():
    value = GlacierAtmosphereCouplingPhysics.ice_surface_temperature(200, 50)
    assert value == 4


def test_mass_balance():
    value = GlacierAtmosphereCouplingPhysics.glacier_mass_balance(300, 100)
    assert value == 200
