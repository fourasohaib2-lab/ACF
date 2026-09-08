import pytest

from acf.model4d.operators.operators_engine import OperatorsEngine


def test_engine_creation():

    engine = OperatorsEngine()

    assert engine is not None


def test_apply_divergence():

    engine = OperatorsEngine()

    value = engine.apply("divergence", 2, 3)

    assert value == 5


def test_apply_advection():

    engine = OperatorsEngine()

    value = engine.apply("advection", velocity=(2, 3), gradient=(4, 5))

    assert value == 23


def test_apply_diffusion():

    engine = OperatorsEngine()

    value = engine.apply("diffusion", laplacian=2e-5, coefficient=0.5)

    assert value == 1e-5


def test_unknown_operator():
    engine = OperatorsEngine()

    with pytest.raises(ValueError):
        engine.apply("unknown")


def test_apply_gradient():
    """
    CORRECTED: engine.gradient()/apply("gradient", ...) used to call a
    nonexistent Gradient.calculate() - always raised AttributeError.
    """
    engine = OperatorsEngine()

    value = engine.apply("gradient", 2.0, 6.0, 2.0)
    assert value == 1.0  # centered difference: (6-2)/(2*2)


def test_apply_curl():
    """
    CORRECTED: engine.curl()/apply("curl", ...) used to call
    Curl.compute() (a generic sum of raw arguments) instead of
    Curl.calculate() (the real curl formula) - summing instead of
    subtracting paired terms is physically meaningless for curl.
    """
    engine = OperatorsEngine()

    value = engine.apply("curl", dw_dy=5.0, dv_dz=2.0, du_dz=1.0, dw_dx=0.0, dv_dx=3.0, du_dy=1.0)
    assert value == (3.0, 1.0, 2.0)  # (dw_dy-dv_dz, du_dz-dw_dx, dv_dx-du_dy)
