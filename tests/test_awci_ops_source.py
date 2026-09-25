import json
from datetime import UTC, datetime

import numpy as np
import pytest

from acf.awci.ops.domains import DEFAULT_DOMAINS_PATH, load_domains
from acf.awci.ops.source_ecmwf import (
    PL_LEVELS,
    PL_PARAMS,
    SFC_PARAMS,
    FetchError,
    MissingFieldsError,
    UrllibFetcher,
    find_latest_run,
    parse_index,
    select_entries,
    step_urls,
)


def _index_text(drop: tuple[str, int | None] | None = None) -> str:
    lines, offset = [], 0
    for p in PL_PARAMS:
        for lev in PL_LEVELS:
            if drop != (p, lev):
                lines.append(json.dumps({"param": p, "levtype": "pl", "levelist": str(lev), "_offset": offset, "_length": 10}))
            offset += 10
    for p in SFC_PARAMS:
        if drop != (p, None):
            lines.append(json.dumps({"param": p, "levtype": "sfc", "_offset": offset, "_length": 10}))
        offset += 10
    lines.append(json.dumps({"param": "vo", "levtype": "pl", "levelist": "500", "_offset": offset, "_length": 10}))
    return "\n".join(lines)


def test_default_domain_config() -> None:
    domains = load_domains(DEFAULT_DOMAINS_PATH)
    default = [d for d in domains.values() if d.default]
    assert len(default) == 1 and default[0].name == "north_africa"


@pytest.mark.parametrize("bbox", [(15, 45, 40, -20), (45, 15, -20, 40)])
def test_invalid_domain_bbox_rejected(tmp_path, bbox) -> None:
    south, north, west, east = bbox
    path = tmp_path / "d.json"
    path.write_text(json.dumps({"domains": [{"name": "x", "label": "x", "south": south, "north": north,
                                             "west": west, "east": east, "default": True}]}))
    with pytest.raises(ValueError):
        load_domains(path)


def test_crop_indices() -> None:
    domain = load_domains(DEFAULT_DOMAINS_PATH)["north_africa"]
    lats = np.arange(-90.0, 90.25, 0.25)
    lons = np.arange(-180.0, 180.0, 0.25)
    iy, ix = domain.crop_indices(lats, lons)
    assert lats[iy].min() == 15.0 and lats[iy].max() == 45.0
    assert lons[ix].min() == -20.0 and lons[ix].max() == 40.0


def test_parse_and_select_index() -> None:
    selected = select_entries(parse_index(_index_text()))
    assert len(selected) == len(PL_PARAMS) * len(PL_LEVELS) + len(SFC_PARAMS)
    assert all(e.param != "vo" for e in selected)


def test_missing_field_is_reported() -> None:
    with pytest.raises(MissingFieldsError, match="mucape"):
        select_entries(parse_index(_index_text(drop=("mucape", None))))


def test_step_urls() -> None:
    grib, index = step_urls(datetime(2026, 9, 25, 6, tzinfo=UTC), 3)
    assert grib == "https://data.ecmwf.int/forecasts/20260925/06z/ifs/0p25/oper/20260925060000-3h-oper-fc.grib2"
    assert index.endswith("-3h-oper-fc.index")


class _FakeFetcher:
    def __init__(self, available: set[str]) -> None:
        self.available = available

    def get_text(self, url: str) -> str:
        if url not in self.available:
            raise FetchError(url)
        return ""

    def get_range(self, url: str, offset: int, length: int) -> bytes:
        raise NotImplementedError


def test_latest_run_falls_back_when_last_step_not_published() -> None:
    now = datetime(2026, 9, 25, 14, 0, tzinfo=UTC)
    newest_last = step_urls(datetime(2026, 9, 25, 6, tzinfo=UTC), 72)[1]
    previous_last = step_urls(datetime(2026, 9, 25, 0, tzinfo=UTC), 72)[1]
    fetcher = _FakeFetcher({previous_last})
    assert newest_last not in fetcher.available
    assert find_latest_run(fetcher, now, last_step=72) == datetime(2026, 9, 25, 0, tzinfo=UTC)


def test_urllib_fetcher_retries_then_fails(monkeypatch) -> None:
    calls: list[str] = []
    sleeps: list[float] = []

    def boom(*args, **kwargs):
        calls.append("x")
        raise OSError("down")

    monkeypatch.setattr("acf.awci.ops.source_ecmwf.urllib.request.urlopen", boom)
    fetcher = UrllibFetcher(sleep=sleeps.append)
    with pytest.raises(FetchError):
        fetcher.get_text("https://example.invalid/x")
    assert len(calls) == 5 and sleeps == [2, 4, 8, 16]
