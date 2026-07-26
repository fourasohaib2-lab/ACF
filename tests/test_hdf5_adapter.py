from pathlib import Path

from acf.data.integration.hdf5_adapter import HDF5Adapter


def test_hdf5_adapter():

    adapter = HDF5Adapter()

    ds = adapter.load(Path("/tmp/test.h5"))

    assert ds.name == "test"
    assert ds.filetype == "HDF5"


def test_hdf5_support():

    adapter = HDF5Adapter()

    assert adapter.supports(Path("file.h5"))
    assert adapter.supports(Path("file.hdf5"))
    assert not adapter.supports(Path("file.nc"))
