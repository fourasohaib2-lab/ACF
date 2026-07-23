import pytest

from acf.science.dry_static_energy import DryStaticEnergy


def test_dse():
    dse = DryStaticEnergy.calculate(
        300.0,
        1000.0,
    )

    assert dse > 300000.0


def test_invalid_temperature():
    with pytest.raises(ValueError):
        DryStaticEnergy.calculate(
            0.0,
            1000.0,
        )


def test_invalid_height():
    with pytest.raises(ValueError):
        DryStaticEnergy.calculate(
            300.0,
            -10.0,
        )
