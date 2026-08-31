"""
Atmospheric Complexity Framework (ACF)

Data Engine & Dataset Statistics Test Suite

`from acf.data.engine import DataEngine` resolves to the
`acf.data.engine` PACKAGE (data/engine/__init__.py aliases
DataEngine = DatasetEngine from dataset_engine.py) - Python's import
resolution always finds that package before the sibling
data/engine.py module of the same name, which is therefore genuinely
unreachable dead code (flagged with its own NOTE, not tested here).
DatasetStatistics previously had 0% coverage - no test file imported
it at all.
"""

import math

from acf.data.engine import DataEngine
from acf.data.engine.dataset_statistics import DatasetStatistics


def test_data_engine_create_dataset():
    engine = DataEngine()
    ds = engine.create_dataset(name="ERA5_sample", filetype="netcdf")
    assert ds.name == "ERA5_sample"
    assert ds.filetype == "netcdf"
    assert ds.id  # a real uuid was assigned


def test_dataset_statistics_basic_compute():
    engine = DataEngine()
    ds = engine.create_dataset(name="obs")
    ds.add_variable("temperature_c", [10.0, 20.0, 30.0])
    ds.add_variable("station_ids", ["A", "B", "C"])  # non-numeric -> skipped

    stats = DatasetStatistics(ds).compute()

    assert "temperature_c" in stats
    assert stats["temperature_c"]["count"] == 3
    assert stats["temperature_c"]["minimum"] == 10.0
    assert stats["temperature_c"]["maximum"] == 30.0
    assert stats["temperature_c"]["mean"] == 20.0
    assert "station_ids" not in stats


def test_dataset_statistics_skips_nan_values():
    engine = DataEngine()
    ds = engine.create_dataset(name="obs")
    ds.add_variable("humidity_pct", [50.0, math.nan, 70.0])

    stats = DatasetStatistics(ds).compute()

    assert stats["humidity_pct"]["count"] == 2
    assert stats["humidity_pct"]["mean"] == 60.0


def test_dataset_statistics_empty_dataset():
    engine = DataEngine()
    ds = engine.create_dataset(name="empty")
    assert DatasetStatistics(ds).compute() == {}
