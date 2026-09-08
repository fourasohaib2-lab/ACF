"""
Unit test suite for PreprocessingEngine (ACF-NWP-001).
"""

from pathlib import Path

from acf.data.preprocessing import PreprocessingEngine


def test_preprocessing_validation(tmp_path: Path):
    """Test validating files."""
    engine = PreprocessingEngine()

    # Test non-existent file
    val_missing = engine.validate_file(tmp_path / "non_existent.grib")
    assert val_missing["valid"] is False

    # Test empty file
    empty_file = tmp_path / "empty.nc"
    empty_file.write_text("", encoding="utf-8")
    val_empty = engine.validate_file(empty_file)
    assert val_empty["valid"] is False

    # Test valid file
    valid_file = tmp_path / "sample.fa"
    valid_file.write_bytes(b"\x00" * 128)
    val_valid = engine.validate_file(valid_file)
    assert val_valid["valid"] is True
