from acf.model4d.physics.hurricane_dynamics import HurricaneDynamicsPhysics


def test_pressure_drop():
    value = HurricaneDynamicsPhysics.pressure_drop(1010, 950)
    assert value == 60


def test_wind_speed():
    value = HurricaneDynamicsPhysics.wind_speed_from_pressure(2500)
    assert round(value, 3) == 63.246


def test_hurricane_category():
    value = HurricaneDynamicsPhysics.hurricane_category(140)
    assert value == 5


def test_hurricane_category_full_saffir_simpson_scale():
    """
    CORRECTED: sub-64kt winds used to be classified as a genuine
    Category 1 hurricane, and the 113-136 kt Category 4 range was
    merged into ">= 113 -> Category 5" entirely.
    """
    assert HurricaneDynamicsPhysics.hurricane_category(20) == 0  # tropical depression, not a hurricane
    assert HurricaneDynamicsPhysics.hurricane_category(63) == 0  # just below Cat 1
    assert HurricaneDynamicsPhysics.hurricane_category(64) == 1
    assert HurricaneDynamicsPhysics.hurricane_category(82) == 1
    assert HurricaneDynamicsPhysics.hurricane_category(83) == 2
    assert HurricaneDynamicsPhysics.hurricane_category(95) == 2
    assert HurricaneDynamicsPhysics.hurricane_category(96) == 3
    assert HurricaneDynamicsPhysics.hurricane_category(112) == 3
    assert HurricaneDynamicsPhysics.hurricane_category(113) == 4
    assert HurricaneDynamicsPhysics.hurricane_category(136) == 4
    assert HurricaneDynamicsPhysics.hurricane_category(137) == 5


def test_eyewall_strength():
    value = HurricaneDynamicsPhysics.eyewall_strength(50, 2)
    assert value == 100


def test_storm_surge():
    value = HurricaneDynamicsPhysics.storm_surge_height(30, 1.5)
    assert value == 45


def test_coriolis_effect():
    value = HurricaneDynamicsPhysics.coriolis_force(10, 5)
    assert value == 50


def test_hurricane_energy():
    value = HurricaneDynamicsPhysics.hurricane_energy(200, 300)
    assert value == 60000


def test_rainfall_rate():
    value = HurricaneDynamicsPhysics.rainfall_rate(200, 10)
    assert value == 20


def test_track_speed():
    value = HurricaneDynamicsPhysics.track_speed(600, 10)
    assert value == 60


def test_intensification_rate():
    value = HurricaneDynamicsPhysics.intensification_rate(980, 950)
    assert value == 30
