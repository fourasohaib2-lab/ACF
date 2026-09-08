"""
Unit test suite for UniversalReader (ACF-100).
"""

from pathlib import Path

import pytest

from acf.data.dataset import Dataset
from acf.data.universal_reader import UniversalReader


def test_universal_reader_open(tmp_path: Path):
    """Test opening datasets using UniversalReader."""
    reader = UniversalReader()

    # Create dummy FA file
    fa_file = tmp_path / "ICMSHAROME+0000.fa"
    fa_file.write_bytes(b"\x00" * 256)

    ds = reader.open(fa_file)
    assert isinstance(ds, Dataset)
    assert ds.get_metadata("reader") == "UniversalReader"
    assert ds.get_metadata("format") == "FA"


def test_universal_reader_file_not_found():
    """Test exception when file is missing."""
    reader = UniversalReader()
    with pytest.raises(FileNotFoundError):
        reader.open("non_existent_file.nc")
