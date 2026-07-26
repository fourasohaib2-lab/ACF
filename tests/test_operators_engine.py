from acf.model4d.operators.operators_engine import OperatorsEngine


def test_engine_creation():

    engine = OperatorsEngine()

    assert engine is not None



def test_apply_divergence():

    engine = OperatorsEngine()

    value = engine.apply(
        "divergence",
        2,
        3
    )

    assert value == 5



def test_apply_advection():

    engine = OperatorsEngine()

    value = engine.apply(
        "advection",
        velocity=(2,3),
        gradient=(4,5)
    )

    assert value == 23



def test_apply_diffusion():

    engine = OperatorsEngine()

    value = engine.apply(
        "diffusion",
        laplacian=2e-5,
        coefficient=0.5
    )

    assert value == 1e-5



def test_unknown_operator():

    engine = OperatorsEngine()

    try:
        engine.apply("unknown")
        assert False

    except ValueError:
        assert True
