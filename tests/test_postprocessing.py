"""
Unit test suite for PostProcessingEngine (ACF-NWP-001).
"""

from pathlib import Path

import pytest

from acf.analysis.postprocessing import PostProcessingEngine
from acf.data.dataset import Dataset


def test_postprocessing_engine_products(tmp_path: Path):
    """Test generating postprocessing maps, time series, profiles, and exports."""
    engine = PostProcessingEngine(output_dir=str(tmp_path))
    ds = Dataset()

    # CORRECTED: generate_maps/extract_time_series/compute_vertical_profile/
    # compute_cross_section/export_netcdf/export_geotiff used to silently
    # return fabricated data or write placeholder text into files named
    # like real PNG/NetCDF/GeoTIFF exports (Path(...).exists() would pass
    # while the content was fake and dataset was never touched). Now
    # honestly raise NotImplementedError instead of silently lying.
    with pytest.raises(NotImplementedError):
        engine.generate_maps(ds, "temperature")

    with pytest.raises(NotImplementedError):
        engine.extract_time_series(ds, 36.7, 3.2, "t2m")

    with pytest.raises(NotImplementedError):
        engine.compute_vertical_profile(ds, 36.7, 3.2)

    with pytest.raises(NotImplementedError):
        engine.compute_cross_section(ds, (36.7, 3.2), (40.0, 5.0))

    with pytest.raises(NotImplementedError):
        engine.export_netcdf(ds, "output.nc")

    with pytest.raises(NotImplementedError):
        engine.export_geotiff(ds, "t2m", "output.tif")

    # CORRECTED: mean_calculated/spread_calculated used to unconditionally
    # claim True with no actual mean/spread ever computed.
    stats = engine.compute_ensemble_stats([ds, ds])
    assert stats["members_count"] == 2
    assert stats["mean_calculated"] is False
    assert stats["spread_calculated"] is False

    # export_json_metadata is genuinely derived from the real dataset -
    # unaffected.
    meta_file = engine.export_json_metadata(ds, "meta.json")
    assert Path(meta_file).exists()

    # Verification evaluation - genuine, unaffected.
    fcst = [20.0, 22.0, 25.0, 21.0]
    obs = [19.5, 22.5, 24.5, 21.5]
    metrics = engine.evaluate_verification(fcst, obs)
    assert "rmse" in metrics
    assert "bias" in metrics
