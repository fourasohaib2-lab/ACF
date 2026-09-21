import numpy as np
import pytest
import xarray as xr

from acf.data.readers.netcdf_reader import NetCDFReader


def test_netcdf_reader(tmp_path):

    file = tmp_path / "demo.nc"

    ds = xr.Dataset(
        {
            "temperature": ("time", [20.0, 21.5, 22.3]),
            "pressure": ("time", [1010, 1008, 1006]),
        },
        coords={
            "time": [0, 1, 2],
        },
        attrs={
            "title": "ACF Test Dataset",
        },
    )

    ds.to_netcdf(file)

    reader = NetCDFReader()

    dataset = reader.read(file)

    assert dataset.filetype == "NetCDF"
    assert "temperature" in dataset.variables
    assert "pressure" in dataset.variables
    assert dataset.dimensions["time"] == 3
    assert dataset.metadata["title"] == "ACF Test Dataset"


def test_netcdf_reader_stores_real_variable_values_not_just_names(tmp_path):
    """NOTE (correction, found while testing the ACF/AWCI pipeline
    against real GRIB2 data): NetCDFReader.read() used to call
    dataset.add_variable(name) with only the variable's real NAME,
    never its real decoded array - dataset.get_variable(x) returned
    None for every real variable in every real file this reader ever
    read. This test asserts the actual real values, not just key
    presence (the gap the pre-existing test_netcdf_reader above never
    caught)."""
    file = tmp_path / "demo.nc"

    ds = xr.Dataset(
        {
            "temperature": ("time", [20.0, 21.5, 22.3]),
            "pressure": ("time", [1010.0, 1008.0, 1006.0]),
        },
        coords={"time": [0, 1, 2], "lat": [45.0], "lon": [2.0]},
        attrs={"title": "ACF Test Dataset"},
    )
    ds["temperature"].attrs["units"] = "degC"
    ds["temperature"].attrs["standard_name"] = "air_temperature"
    ds.to_netcdf(file)

    dataset = NetCDFReader().read(file)

    real_temperature = dataset.get_variable("temperature")
    assert real_temperature is not None
    np.testing.assert_array_equal(real_temperature, [20.0, 21.5, 22.3])

    real_pressure = dataset.get_variable("pressure")
    assert real_pressure is not None
    np.testing.assert_array_equal(real_pressure, [1010.0, 1008.0, 1006.0])

    # Real coordinate arrays are also stored, not just data variables.
    np.testing.assert_array_equal(dataset.get_variable("lat"), [45.0])
    np.testing.assert_array_equal(dataset.get_variable("lon"), [2.0])

    # Real per-variable metadata, used by awci.data.model_import to
    # resolve and unit-convert a matched variable.
    assert dataset.metadata["temperature_units"] == "degC"
    assert dataset.metadata["temperature_standard_name"] == "air_temperature"


def test_netcdf_reader_real_dataset_feeds_a_real_awci_computation(tmp_path):
    """End-to-end: a real (synthetic-but-physically-plausible) NetCDF
    file, read through the real NetCDFReader, feeds a real
    awci.data.model_import.compute_awci_from_imported_dataset() call -
    proving the full read -> extract -> AWCICalculator chain actually
    works now that real values survive the read."""
    from awci.data.model_import import compute_awci_from_imported_dataset

    file = tmp_path / "point.nc"
    ds = xr.Dataset(
        {
            "t2m": (("lat", "lon"), [[289.5]]),
            "msl": (("lat", "lon"), [[101300.0]]),
            "q": (("lat", "lon"), [[0.0075]]),
        },
        coords={"lat": [48.85], "lon": [2.35]},
    )
    ds["t2m"].attrs["units"] = "K"
    ds["msl"].attrs["units"] = "Pa"
    ds["q"].attrs["units"] = "kg kg**-1"
    ds.to_netcdf(file)

    dataset = NetCDFReader().read(file)
    output = compute_awci_from_imported_dataset(dataset, lat=48.85, lon=2.35, level_hpa=1000.0)

    assert "temperature" in output["extraction"]["matched_variables"]
    assert output["extraction"]["inputs"]["temperature"] == pytest.approx(289.5)
    assert 0.0 <= output["result"]["awci"] <= 100.0
