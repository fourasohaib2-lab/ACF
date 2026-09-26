"""Ensemble accumulation (SP5): exact counts over members, NaN not counted, real IFS ENS fixture."""

from pathlib import Path

import numpy as np
import pytest

from acf.awci.ops.engine import DEFAULT_OPERATIONAL_PROFILE_PATH, load_profile
from acf.awci.ops.ensemble import (
    CEILING_1500FT_M,
    ENS_LEVEL_PRODUCTS,
    ENS_SURFACE_PRODUCTS,
    EnsembleAccumulator,
    class_lower_bound,
)

ENS = Path(__file__).parent / "data" / "awci_ens"
PROFILE = load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH)


def _member(awci: list[float], cloud: list[float], conv: float, ceiling: float) -> dict[str, np.ndarray]:
    lev = lambda v: np.array(v, dtype=float).reshape(2, 1, 1)  # noqa: E731
    return {"awci": lev(awci), "cloud_fraction": lev(cloud), "icing_potential": lev([0, 1]), "cat_category": lev([2, 0]),
            "convective_class": np.array([[conv]]), "ceiling_m": np.array([[ceiling]])}


def test_high_lower_bound_comes_from_the_profile() -> None:
    assert class_lower_bound(PROFILE, "High") == 50.0  # upper bound of Moderate
    with pytest.raises(ValueError):
        class_lower_bound(PROFILE, "Unknown")


def test_counts_are_exact_and_nan_members_are_not_counted() -> None:
    acc = EnsembleAccumulator((2, 1, 1), (1, 1), awci_high=50.0)
    acc.add(_member([60, 10], [0.7, 0.1], conv=3, ceiling=300.0))   # High at level 0, BKN, TCU+, ceiling < 1500 ft
    acc.add(_member([40, np.nan], [0.625, np.nan], conv=0, ceiling=np.nan))  # level 1 under the relief; no ceiling
    acc.add(_member([55, 70], [0.2, 0.9], conv=2, ceiling=500.0))  # 500 m = 1640 ft: not below 1500 ft
    out = acc.result()
    assert out["members"] == 3
    np.testing.assert_array_equal(out["p_awci_high_count"][:, 0, 0], [2, 1])  # level 1: 10, NaN, 70
    np.testing.assert_array_equal(out["p_awci_high_n"][:, 0, 0], [3, 2])  # the NaN member is not in the denominator
    np.testing.assert_array_equal(out["p_cloud_bkn_count"][:, 0, 0], [2, 1])  # 0.625 = 5/8 counts
    np.testing.assert_array_equal(out["p_icing_count"][:, 0, 0], [0, 3])
    np.testing.assert_array_equal(out["p_cat_moderate_count"][:, 0, 0], [3, 0])
    assert out["p_convection_count"][0, 0] == 2 and out["p_convection_n"][0, 0] == 3
    assert out["p_ceiling_1500ft_count"][0, 0] == 1 and out["p_ceiling_1500ft_n"][0, 0] == 3  # no ceiling = no event
    assert out["awci_mean"][0, 0, 0] == pytest.approx(np.mean([60, 40, 55]))
    assert out["awci_std"][0, 0, 0] == pytest.approx(np.std([60, 40, 55], ddof=1))
    assert out["awci_std"][1, 0, 0] == pytest.approx(np.std([10, 70], ddof=1))


def test_single_member_has_no_spread() -> None:
    acc = EnsembleAccumulator((2, 1, 1), (1, 1), awci_high=50.0)
    acc.add(_member([60, 10], [0.7, 0.1], conv=0, ceiling=np.nan))
    assert np.isnan(acc.result()["awci_std"]).all()


def test_ceiling_threshold_is_1500_ft_exactly() -> None:
    assert CEILING_1500FT_M == pytest.approx(1500 * 0.3048)


def test_real_ens_members_through_the_unchanged_pipeline() -> None:
    from tests.awci_ops_support import ens_member_layers

    members = ens_member_layers(ENS, step=6, members=(1, 2, 3, 4))
    assert len(members) == 4
    acc = EnsembleAccumulator(members[0]["awci"].shape, members[0]["ceiling_m"].shape, awci_high=50.0)
    for layers in members:
        acc.add(layers)
    out = acc.result()
    expected = sum((m["cloud_fraction"] >= 0.625).astype(int) for m in members)
    np.testing.assert_array_equal(out["p_cloud_bkn_count"], expected)
    assert set(ENS_LEVEL_PRODUCTS) | set(ENS_SURFACE_PRODUCTS) <= {k.removesuffix("_count") for k in out if k.endswith("_count")}
    assert (out["p_awci_high_n"] <= 4).all() and out["members"] == 4
    # members differ: the ensemble is not four copies of one forecast
    assert not np.allclose(members[0]["awci"], members[1]["awci"], equal_nan=True)
