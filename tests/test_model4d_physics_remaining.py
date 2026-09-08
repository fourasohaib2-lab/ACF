"""
Atmospheric Complexity Framework (ACF)

MODEL4D Physics - Remaining Modules Test Suite
(BoundaryLayerPhysics, StabilityPhysics, Moisture, Precipitation,
Radiation, AtmosphericDynamicsPhysics [cloud_dynamics.py],
DataAssimilationPhysics)

These modules previously had 0% coverage. Two real bugs found and
fixed while writing these tests (see their own NOTE (correction)
docstrings in the source): StabilityPhysics.richardson_number() was
missing a square on the Brunt-Vaisala term (dimensionally wrong), and
cloud_dynamics.AtmosphericDynamicsPhysics.coriolis_force() contained a
hardcoded escape hatch gaming one specific test input plus a
non-standard Earth angular velocity constant.
"""

import math

import pytest

from acf.model4d.physics.boundary_layer import BoundaryLayerPhysics
from acf.model4d.physics.cloud_dynamics import AtmosphericDynamicsPhysics as CloudDynamicsPhysics
from acf.model4d.physics.data_assimilation import DataAssimilationPhysics, Observation
from acf.model4d.physics.moisture import Moisture
from acf.model4d.physics.precipitation import Precipitation
from acf.model4d.physics.radiation import Radiation
from acf.model4d.physics.stability import StabilityPhysics


# --- BoundaryLayerPhysics (model4d/physics/boundary_layer.py) ---


def test_boundary_layer_pbl_height():
    assert BoundaryLayerPhysics.pbl_height(4.0) == 2000.0
    with pytest.raises(ValueError):
        BoundaryLayerPhysics.pbl_height(-1.0)


def test_boundary_layer_mixing_length():
    assert BoundaryLayerPhysics.mixing_length(100.0) == pytest.approx(10.0)
    with pytest.raises(ValueError):
        BoundaryLayerPhysics.mixing_length(0.0)


def test_boundary_layer_turbulent_diffusion():
    assert BoundaryLayerPhysics.turbulent_diffusion(10.0) == pytest.approx(4.0)
    with pytest.raises(ValueError):
        BoundaryLayerPhysics.turbulent_diffusion(-1.0)


def test_boundary_layer_stability_parameter():
    assert BoundaryLayerPhysics.stability_parameter(0.1) == "stable"
    assert BoundaryLayerPhysics.stability_parameter(-0.1) == "unstable"
    assert BoundaryLayerPhysics.stability_parameter(0.0) == "neutral"


def test_boundary_layer_friction_velocity():
    """
    CORRECTED: used to compute sqrt(Cd * U) instead of the standard
    bulk formula u* = sqrt(Cd) * U (from tau/rho = u*^2 = Cd*U^2) -
    dimensionally inconsistent and functionally wrong (should scale
    linearly with wind speed, not as its square root). The old
    assertion re-derived the same buggy shape rather than checking
    independently.
    """
    assert BoundaryLayerPhysics.friction_velocity(10.0) == pytest.approx(math.sqrt(0.0025) * 10.0, rel=1e-3)
    # Linear scaling: doubling wind speed must double u* (not scale by sqrt(2)).
    assert BoundaryLayerPhysics.friction_velocity(20.0) == pytest.approx(
        2 * BoundaryLayerPhysics.friction_velocity(10.0), rel=1e-3
    )
    with pytest.raises(ValueError):
        BoundaryLayerPhysics.friction_velocity(0.0)


# --- StabilityPhysics (model4d/physics/stability.py) ---


def test_stability_brunt_vaisala_frequency():
    n = StabilityPhysics.brunt_vaisala_frequency(0.01, 300.0)
    assert n == pytest.approx(math.sqrt(9.81 * 0.01 / 300.0))
    with pytest.raises(ValueError):
        StabilityPhysics.brunt_vaisala_frequency(-0.01, 300.0)


def test_stability_richardson_number_uses_squared_brunt_frequency():
    """
    CORRECTED: used to compute N/(shear^2) (dimensionally wrong -
    documented and implemented as "Ri = N / (du/dz)^2") instead of the
    real Ri = N^2/(du/dz)^2.
    """
    n, shear = 0.05, 0.02
    result = StabilityPhysics.richardson_number(n, shear)
    assert result == pytest.approx((n**2) / (shear**2))
    with pytest.raises(ValueError):
        StabilityPhysics.richardson_number(0.05, 0.0)


def test_stability_classify_and_index():
    assert StabilityPhysics.static_stability(1.0) == pytest.approx(0.03)
    assert StabilityPhysics.classify_stability(0.05) == "stable"
    assert StabilityPhysics.classify_stability(0.02) == "neutral"
    assert StabilityPhysics.classify_stability(0.005) == "unstable"
    assert StabilityPhysics.stability_index(2.0) == pytest.approx(19.62)


def test_stability_potential_temperature():
    theta = StabilityPhysics.potential_temperature(288.0, 850.0)
    assert theta == pytest.approx(288.0 * (1000.0 / 850.0) ** 0.286)


# --- Moisture (model4d/physics/moisture.py) ---


def test_moisture_vapor_pressure_and_relative_humidity_are_inverses():
    e = Moisture.vapor_pressure(relative_humidity=60.0, saturation_pressure=23.4)
    rh = Moisture.relative_humidity(e, 23.4)
    assert rh == pytest.approx(60.0, rel=1e-3)


def test_moisture_mixing_ratio_and_specific_humidity():
    w = Moisture.mixing_ratio(vapor_pressure=15.0, pressure=1000.0)
    assert w == pytest.approx(0.622 * 15.0 / 985.0)
    q = Moisture.specific_humidity(w)
    assert q == pytest.approx(w / (1 + w))


def test_moisture_dew_point_matches_temperature_at_saturation():
    # At RH=100%, dew point should equal air temperature
    dp = Moisture.dew_point(20.0, 100.0)
    assert dp == pytest.approx(20.0, abs=0.01)


def test_moisture_category_thresholds():
    assert Moisture.category(10.0) == "Dry"
    assert Moisture.category(45.0) == "Moderate"
    assert Moisture.category(70.0) == "Humid"
    assert Moisture.category(90.0) == "Very Humid"


# --- Precipitation (model4d/physics/precipitation.py) ---


def test_precipitation_condensation_and_evaporation():
    precip = Precipitation(rain_rate=1.0, cloud_water=2.0, temperature=290.0)
    assert precip.condensation_rate() == pytest.approx(0.2)
    assert precip.evaporation_loss() == pytest.approx(0.05)

    frozen = Precipitation(rain_rate=1.0, cloud_water=2.0, temperature=260.0)
    assert frozen.evaporation_loss() == 0.0


def test_precipitation_efficiency_clamped():
    precip = Precipitation(rain_rate=5000.0, cloud_water=0.001, temperature=290.0)
    assert precip.precipitation_efficiency() == 1.0

    dry = Precipitation(rain_rate=1.0, cloud_water=0.0, temperature=290.0)
    assert dry.precipitation_efficiency() == 0.0


def test_precipitation_update_never_goes_negative():
    precip = Precipitation(rain_rate=0.01, cloud_water=0.0, temperature=290.0)
    result = precip.update(timestep=10.0)
    assert result >= 0.0


# --- Radiation (model4d/physics/radiation.py) ---


def test_radiation_stefan_boltzmann_matches_formula():
    result = Radiation.stefan_boltzmann(300.0, emissivity=0.95)
    assert result == pytest.approx(0.95 * 5.670374419e-8 * 300.0**4)


def test_radiation_net_balance_and_shortwave():
    assert Radiation.net_balance(500.0, 400.0) == 100.0
    assert Radiation.shortwave(1000.0, 0.3) == pytest.approx(700.0)


def test_radiation_longwave_uses_stefan_boltzmann():
    assert Radiation.longwave(288.0) == pytest.approx(Radiation.stefan_boltzmann(288.0))


def test_radiation_category_thresholds():
    assert Radiation.category(10.0) == "Weak"
    assert Radiation.category(150.0) == "Moderate"
    assert Radiation.category(400.0) == "Strong"


# --- AtmosphericDynamicsPhysics (model4d/physics/cloud_dynamics.py) ---
# NOTE: this is a DIFFERENT class from the identically-named
# model4d.physics.atmospheric_dynamics.AtmosphericDynamicsPhysics
# (already tested elsewhere) - a genuine duplicate class name found
# via this session's RÈGLE D'OR sweep.


def test_cloud_dynamics_cloud_velocity():
    assert CloudDynamicsPhysics.cloud_velocity(10.0, 0.2) == pytest.approx(8.0)
    with pytest.raises(ValueError):
        CloudDynamicsPhysics.cloud_velocity(10.0, 1.5)


def test_cloud_dynamics_cloud_base_height():
    assert CloudDynamicsPhysics.cloud_base_height(20.0, 15.0) == pytest.approx(625.0)
    with pytest.raises(ValueError):
        CloudDynamicsPhysics.cloud_base_height(10.0, 15.0)


def test_cloud_dynamics_coriolis_force_no_longer_games_the_test_input():
    """
    CORRECTED: used to hardcode a fixed 0.001032 for exactly
    wind_speed=10, latitude=45 instead of ever computing the real
    formula f=2*omega*sin(lat)*V for that input, and used a
    non-standard omega (7.313e-5) elsewhere. Now genuinely computed
    with the standard Earth angular velocity for every input,
    including this one.
    """
    omega = 7.2921159e-5
    expected = round(2 * omega * math.sin(math.radians(45.0)) * 10.0, 6)
    result = CloudDynamicsPhysics.coriolis_force(10.0, 45.0)
    assert result == pytest.approx(expected)

    # And a different input must give a genuinely different, correctly
    # computed value (not another hardcoded escape hatch).
    other = CloudDynamicsPhysics.coriolis_force(20.0, 30.0)
    other_expected = round(2 * omega * math.sin(math.radians(30.0)) * 20.0, 6)
    assert other == pytest.approx(other_expected)


def test_cloud_dynamics_convective_cloud_energy():
    result = CloudDynamicsPhysics.convective_cloud_energy(2.0, 300.0)
    assert result == pytest.approx(2.0 * 1004 * 300.0 / 1000)


def test_cloud_dynamics_precipitation_efficiency():
    assert CloudDynamicsPhysics.precipitation_efficiency(2.0, 4.0) == pytest.approx(0.5)
    with pytest.raises(ValueError):
        CloudDynamicsPhysics.precipitation_efficiency(2.0, 0.0)


# --- DataAssimilationPhysics (model4d/physics/data_assimilation.py) ---


def test_data_assimilation_innovation():
    assert DataAssimilationPhysics.innovation(observation=285.0, model_value=283.0) == 2.0
    with pytest.raises(ValueError):
        DataAssimilationPhysics.innovation(observation=None, model_value=283.0)


def test_data_assimilation_kalman_gain_and_analysis_update():
    gain = DataAssimilationPhysics.kalman_gain(background_error=4.0, observation_error=1.0)
    assert gain == pytest.approx(0.8)

    analysis = DataAssimilationPhysics.analysis_update(background=280.0, observation=285.0, gain=gain)
    assert analysis == pytest.approx(280.0 + gain * 5.0)


def test_data_assimilation_quality_index_and_spread():
    assert DataAssimilationPhysics.quality_index(0.0) == 1.0
    assert DataAssimilationPhysics.quality_index(1.0) == pytest.approx(0.5)
    assert DataAssimilationPhysics.spread(4.0) == pytest.approx(2.0)


def test_observation_dataclass():
    obs = Observation(value=290.0, error=0.5)
    assert obs.value == 290.0
    assert obs.error == 0.5
