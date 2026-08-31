from pathlib import Path

import pytest

from acf.data.dataset import Dataset
from acf.data.fusion.data_fusion_engine import DataFusionEngine


def build_dataset(name, variable):

    ds = Dataset(
        name=name,
        filepath=Path(f"/tmp/{name}.nc"),
        filetype="NetCDF",
    )

    ds.add_variable(variable, variable)
    ds.add_dimension("time", 10)
    ds.set_metadata("source", name)

    return ds


def test_merge():

    d1 = build_dataset("gfs", "temperature")
    d2 = build_dataset("era5", "pressure")

    merged = DataFusionEngine().merge(d1, d2)

    assert merged.has_variable("temperature")
    assert merged.has_variable("pressure")


def test_merge_dimensions():

    d1 = build_dataset("gfs", "temperature")
    d2 = build_dataset("era5", "pressure")

    d2.add_dimension("level", 20)

    merged = DataFusionEngine().merge(d1, d2)

    assert merged.has_dimension("time")
    assert merged.has_dimension("level")


def test_empty():

    with pytest.raises(ValueError):
        DataFusionEngine().merge()
