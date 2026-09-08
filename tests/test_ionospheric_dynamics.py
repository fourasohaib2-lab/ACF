from acf.model4d.physics.ionospheric_dynamics import IonosphericDynamicsPhysics


def test_ionization_rate():
    assert IonosphericDynamicsPhysics.ionization_rate(100, 20) == 5


def test_electron_density():
    assert IonosphericDynamicsPhysics.electron_density(50, 10) == 40


def test_recombination_rate():
    assert IonosphericDynamicsPhysics.recombination_rate(100, 0.1) == 10


def test_plasma_frequency():
    assert IonosphericDynamicsPhysics.plasma_frequency(100) == 10


def test_solar_ionization_effect():
    assert IonosphericDynamicsPhysics.solar_ionization_effect(1000, 0.2) == 200


def test_ionospheric_temperature():
    assert IonosphericDynamicsPhysics.ionospheric_temperature(200, 50) == 250


def test_electron_temperature_change():
    assert IonosphericDynamicsPhysics.electron_temperature_change(1000, 100) == 1100


def test_total_electron_content():
    assert IonosphericDynamicsPhysics.total_electron_content(10, 5) == 50


def test_ionosphere_stability():
    assert IonosphericDynamicsPhysics.ionosphere_stability(0.5) == "normal"


def test_geomagnetic_disturbance_effect():
    assert IonosphericDynamicsPhysics.geomagnetic_disturbance_effect(5) == 50
