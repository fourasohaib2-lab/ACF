from pathlib import Path

import numpy as np
import pytest

from acf.awci.ops.decode import decode_messages
from acf.awci.ops.domains import Domain
from acf.awci.ops.hazards import ECMWF_PTYPE_SEVERITY
from acf.awci.ops.source_ecmwf import PL_LEVELS, PL_PARAMS, SFC_PARAMS, parse_index

FIXTURE = Path(__file__).parent / "data" / "awci_ops"
STEM = "20260925000000-3h-oper-fc"


def _messages() -> list[bytes]:
    data = (FIXTURE / f"{STEM}.grib2").read_bytes()
    return [data[e.offset : e.offset + e.length] for e in parse_index((FIXTURE / f"{STEM}.index").read_text())]


FULL = Domain("fixture", "fixture", 35.0, 37.0, 2.0, 4.0, True)
SUB = Domain("sub", "sub", 35.5, 36.5, 2.5, 3.5, False)


def test_decode_full_fixture_domain() -> None:
    fields = decode_messages(_messages(), [FULL])["fixture"]
    assert fields.lats[0] == 35.0 and fields.lats[-1] == 37.0 and np.all(np.diff(fields.lats) > 0)
    assert fields.lons[0] == 2.0 and fields.lons[-1] == 4.0
    np.testing.assert_array_equal(fields.levels_hpa, PL_LEVELS)
    for p in PL_PARAMS:
        assert fields.pl[p].shape == (len(PL_LEVELS), 9, 9)
    for p in SFC_PARAMS:
        assert fields.sfc[p].shape == (9, 9)


def test_physical_plausibility_and_level_order() -> None:
    f = decode_messages(_messages(), [FULL])["fixture"]
    t = f.pl["t"]
    assert 180.0 < t.min() and t.max() < 330.0
    assert np.all(np.diff(f.pl["gh"].mean(axis=(1, 2))) > 0)  # 1000 -> 100 hPa: height increases
    assert 0.0 <= f.pl["q"].min() and f.pl["q"].max() < 0.04
    assert set(np.unique(f.sfc["ptype"])) <= set(ECMWF_PTYPE_SEVERITY)


def test_sub_domain_crop_is_consistent() -> None:
    both = decode_messages(_messages(), [FULL, SUB])
    full, sub = both["fixture"], both["sub"]
    assert sub.pl["t"].shape == (len(PL_LEVELS), 5, 5)
    iy = np.searchsorted(full.lats, sub.lats)
    ix = np.searchsorted(full.lons, sub.lons)
    np.testing.assert_array_equal(sub.pl["t"], full.pl["t"][:, iy][:, :, ix])


def test_missing_message_is_an_error() -> None:
    with pytest.raises(ValueError, match="missing"):
        decode_messages(_messages()[1:], [FULL])
