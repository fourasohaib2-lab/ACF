import numpy as np

from acf.awci.hydrometeor_phase import PHASE_SEVERITY
from acf.awci.ops.hazards import (
    ECMWF_PTYPE_SEVERITY,
    dust_proxy,
    icing_potential,
    precip_class_codes,
    precip_rate_mm_h,
    ptype_severity,
    relative_humidity_2m_pct,
)
from acf.awci.ops.registry import LAYERS


def test_icing_potential_temperature_and_humidity_window() -> None:
    t = np.array([273.15, 263.15, 253.15, 252.0, 274.0, 263.15, np.nan])
    r = np.array([80.0, 70.0, 90.0, 90.0, 90.0, 69.9, 80.0])
    out = icing_potential(t, r)
    np.testing.assert_array_equal(out[:6], [1.0, 1.0, 1.0, 0.0, 0.0, 0.0])
    assert np.isnan(out[6])


def test_precip_rate_and_wmo_classes() -> None:
    rate = precip_rate_mm_h(np.array([0.0, 1e-4, 2e-3, 5e-3, 2e-2, np.nan]))
    np.testing.assert_allclose(rate[:5], [0.0, 0.36, 7.2, 18.0, 72.0])
    np.testing.assert_array_equal(precip_class_codes(rate), [0, 1, 2, 3, 4, -1])


def test_ptype_severity_reuses_phase_severity_and_rejects_unknown() -> None:
    assert ECMWF_PTYPE_SEVERITY[1] == PHASE_SEVERITY["Rain"]
    assert ECMWF_PTYPE_SEVERITY[5] == PHASE_SEVERITY["Snow"]
    assert ECMWF_PTYPE_SEVERITY[3] == PHASE_SEVERITY["Freezing Rain / Ice Pellets"]
    out = ptype_severity(np.array([0.0, 1.0, 12.0, 42.0, np.nan]))
    np.testing.assert_allclose(out[:3], [0.0, 0.2, 1.0])
    assert np.isnan(out[3]) and np.isnan(out[4])


def test_rh2m_and_dust_proxy() -> None:
    rh = relative_humidity_2m_pct(np.array([300.0, 300.0]), np.array([300.0, 280.0]))
    assert rh[0] == 100.0 and 25.0 < rh[1] < 35.0
    out = dust_proxy(np.array([8.0, 18.0, 18.0, 13.0]), np.array([10.0, 10.0, 80.0, 45.0]))
    np.testing.assert_allclose(out, [0.0, 1.0, 0.0, 0.25])


def test_registry_declares_every_layer_with_status() -> None:
    for name in ("wind_speed", "layer_shear", "vertical_shear", "cat_ti2", "cat_category", "icing_potential",
                 "theta_e", "mucape", "cloud_base_lcl", "precip_rate", "precip_class", "precip_type",
                 "gust_10m", "dust_proxy", "awci"):
        spec = LAYERS[name]
        assert spec.unit and spec.equation and spec.source and spec.status
