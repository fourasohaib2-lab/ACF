import numpy as np
import pytest

from acf.awci.ops.isa import ISA_P11_HPA, flight_level, pressure_altitude_m

# ICAO Doc 7488 tabulated pressure altitudes (m)
@pytest.mark.parametrize(
    ("p_hpa", "h_m"),
    [(1013.25, 0.0), (850.0, 1457.3), (500.0, 5574.4), (300.0, 9164.0), (200.0, 11784.0), (100.0, 16179.7)],
)
def test_pressure_altitude_matches_doc7488(p_hpa: float, h_m: float) -> None:
    assert pressure_altitude_m(p_hpa) == pytest.approx(h_m, abs=1.0)


def test_tropopause_pressure_is_22632_pa() -> None:
    assert ISA_P11_HPA == pytest.approx(226.32, abs=0.01)


def test_vectorized_and_continuous_at_tropopause() -> None:
    p = np.array([ISA_P11_HPA + 1e-9, ISA_P11_HPA - 1e-9])
    h = pressure_altitude_m(p)
    assert h[0] == pytest.approx(11000.0, abs=0.01)
    assert h[1] == pytest.approx(11000.0, abs=0.01)


@pytest.mark.parametrize(("p_hpa", "fl"), [(300.0, 301), (250.0, 340), (200.0, 387), (100.0, 531)])
def test_flight_level_labels(p_hpa: float, fl: int) -> None:
    assert flight_level(p_hpa) == fl


def test_rejects_pressure_above_20km() -> None:
    with pytest.raises(ValueError):
        pressure_altitude_m(40.0)
