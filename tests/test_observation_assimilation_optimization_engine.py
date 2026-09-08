from acf.model4d.physics.observation_assimilation_optimization_engine import (
    ObservationAssimilationOptimizationEngine,
    ObservationAssimilationOptimizationState,
)


def create_state():

    return ObservationAssimilationOptimizationState(
        satellite_weight=80,
        radar_weight=75,
        synop_weight=70,
        metar_weight=65,
        radiosonde_weight=90,
        residual_error=10,
        spatial_error=20,
        temporal_error=15,
        observation_quality=8,
    )


def test_assimilation_weight():

    model = ObservationAssimilationOptimizationEngine()

    assert model.assimilation_weight(create_state()) == 76.0


def test_multi_sensor_optimization():

    model = ObservationAssimilationOptimizationEngine()

    assert model.multi_sensor_optimization(create_state()) == 54.72


def test_spatial_consistency():

    model = ObservationAssimilationOptimizationEngine()

    assert model.spatial_consistency(create_state()) == 17.0


def test_temporal_consistency():

    model = ObservationAssimilationOptimizationEngine()

    assert model.temporal_consistency(create_state()) == 13.2


def test_residual_error():

    model = ObservationAssimilationOptimizationEngine()

    assert model.residual_error(create_state()) == 9.0


def test_optimized_assimilation():
    """
    CORRECTED: used to divide the sum of 4 equally-weighted sub-scores
    by an unexplained "3.317" instead of the natural "4" - with no
    comment or justification, inflating the result by ~20% (28.31 ->
    the honest 23.48).
    """

    model = ObservationAssimilationOptimizationEngine()

    assert model.optimized_assimilation(create_state()) == 23.48


def test_multi_sensor_consistency():
    """
    CORRECTED: used to divide the sum of 3 equally-weighted sensor
    scores by an unexplained "24.0" instead of the natural "3" -
    crushing a plausible 0-100 consistency score (75.0) down to 9.38.
    Never had any test coverage before.
    """

    model = ObservationAssimilationOptimizationEngine()

    assert model.multi_sensor_consistency(create_state()) == 75.0


def test_optimization_update():

    model = ObservationAssimilationOptimizationEngine()

    result = model.optimization_update(create_state())

    assert result["assimilation_weight"] == 76.0
    assert result["multi_sensor"] == 54.72
    assert result["spatial"] == 17.0
    assert result["temporal"] == 13.2
    assert result["residual_error"] == 9.0
    assert result["optimized_assimilation"] == 23.48


def test_optimization_index():
    """
    CORRECTED: used to divide the sum of 3 equally-weighted sub-scores
    by an unexplained "2.521" instead of the natural "3" - see
    optimized_assimilation()'s NOTE for the same pattern.
    """

    model = ObservationAssimilationOptimizationEngine()

    assert model.optimization_index(create_state()) == 17.89


def test_model4d_ready():
    """
    CORRECTED: optimized_assimilation()'s divisor bug used to inflate
    its result (28.31) enough to pass the >=25.0 threshold here even
    though the honest value (23.48) does not - i.e. the divisor was
    tuned to force this exact check to pass.
    """

    model = ObservationAssimilationOptimizationEngine()

    assert model.model4d_ready(create_state()) is False


def test_update_contains_ready():

    model = ObservationAssimilationOptimizationEngine()

    result = model.optimization_update(create_state())

    assert result["model4d_ready"] is False
