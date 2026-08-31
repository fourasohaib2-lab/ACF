"""
Unit test suite for CommandDispatcher.export_product()'s fabricated-export fix.

REWRITTEN: export_product() used to write the identical one-line text string
("ACF Product Export Format: <FMT>") into `output_path` regardless of which
of the 12 claimed formats (PNG, SVG, PDF, NetCDF4, GRIB2, GeoTIFF, COG, Zarr,
CSV, GeoJSON, MP4, GIF) was requested - a ".png" export got a text file, a
"NetCDF4" export got the same text file - then unconditionally emitted
`product_exported` and returned the path as if a genuine export had
happened. The method has no data parameter at all, so there is no real
simulation state or figure to serialize even in principle. Verified via grep:
zero callers anywhere in the codebase, zero prior test coverage.
"""

import pytest

from acf.gui.esoc.command_dispatcher import CommandDispatcher


def test_export_product_no_longer_writes_a_fake_file(tmp_path):
    dispatcher = CommandDispatcher()
    output_path = str(tmp_path / "forecast.png")

    with pytest.raises(NotImplementedError):
        dispatcher.export_product("PNG", output_path)

    # No file should be created - the old code wrote one regardless of format.
    assert not (tmp_path / "forecast.png").exists()


def test_export_product_raises_for_every_claimed_format(tmp_path):
    """Every one of the 12 formats used to silently claim success identically - all must now honestly raise."""
    dispatcher = CommandDispatcher()
    for fmt in ("PNG", "SVG", "PDF", "NetCDF4", "GRIB2", "GeoTIFF", "COG", "Zarr", "CSV", "GeoJSON", "MP4", "GIF"):
        with pytest.raises(NotImplementedError):
            dispatcher.export_product(fmt, str(tmp_path / f"out.{fmt.lower()}"))


def test_dispatch_export_product_command_also_raises(tmp_path):
    """The dynamic dispatch("export_product", ...) path must propagate the same honest error, not swallow it."""
    dispatcher = CommandDispatcher()
    with pytest.raises(NotImplementedError):
        dispatcher.dispatch("export_product", format="netcdf4", path=str(tmp_path / "out.nc"))
