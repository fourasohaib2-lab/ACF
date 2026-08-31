from acf.model4d.physics.atmospheric_fronts import AtmosphericFrontsPhysics


def test_temperature_gradient():

    value = AtmosphericFrontsPhysics.temperature_gradient(10, 100)

    assert value == 0.1


def test_frontal_strength():

    value = AtmosphericFrontsPhysics.frontal_strength(0.1)

    assert value == 10


def test_thermal_advection():

    value = AtmosphericFrontsPhysics.thermal_advection(10, 0.2)

    assert value == -2


def test_front_speed():

    value = AtmosphericFrontsPhysics.front_speed(100, 1)

    assert value == 100


def test_frontogenesis():

    value = AtmosphericFrontsPhysics.frontogenesis(0.5, 2)

    assert value == 1


def test_frontal_zone_width():

    value = AtmosphericFrontsPhysics.frontal_zone_width(0.1, 10)

    assert value == 100


def test_baroclinic_instability():

    value = AtmosphericFrontsPhysics.baroclinic_instability(0.5, 4)

    assert value == 2


def test_warm_front_intensity():

    value = AtmosphericFrontsPhysics.warm_front_intensity(5, 10)

    assert value == 50


def test_cold_front_intensity():

    value = AtmosphericFrontsPhysics.cold_front_intensity(5, 10)

    assert value == 60


def test_frontal_convergence():

    value = AtmosphericFrontsPhysics.frontal_convergence(20, 5)

    assert value == 4
