"""
Unit test suite for PostProcessingEngine (ACF-NWP-001).
"""

from pathlib import Path

from acf.analysis.postprocessing import PostProcessingEngine
from acf.data.dataset import Dataset


def test_postprocessing_engine_products(tmp_path: Path):
    """Test generating postprocessing maps, time series, profiles, and exports."""
    engine = PostProcessingEngine(output_dir=str(tmp_path))
    ds = Dataset()

    # Maps
    map_file = engine.generate_maps(ds, "temperature")
    assert Path(map_file).exists()

    # Time series
    ts = engine.extract_time_series(ds, 36.7, 3.2, "t2m")
    assert "values" in ts
    assert len(ts["values"]) == 9

    # Vertical profile
    prof = engine.compute_vertical_profile(ds, 36.7, 3.2)
    assert "levels_hpa" in prof

    # NetCDF export
    nc_file = engine.export_netcdf(ds, "output.nc")
    assert Path(nc_file).exists()

    # GeoTIFF export
    gt_file = engine.export_geotiff(ds, "t2m", "output.tif")
    assert Path(gt_file).exists()

    # Verification evaluation
    fcst = [20.0, 22.0, 25.0, 21.0]
    obs = [19.5, 22.5, 24.5, 21.5]
    metrics = engine.evaluate_verification(fcst, obs)
    assert "rmse" in metrics
    assert "bias" in metrics
