"""
Unit test suite for hpc_connector.data_management's package-level stub
classes (ACF-HPC-107).

REWRITTEN: DataCatalog.list_datasets(), MetadataValidator.validate(),
Checksum.compute(), DataPipeline.run(), FileConverter.convert() and
FileValidator.validate() used to unconditionally claim a trivial
"success" result (True / an empty list / the literal string "sha256"
as if it were a computed hash) regardless of any real input or backend
connected - the same fake-stub pattern found and fixed throughout this
session, here in classes with no real callers or prior test coverage
(verified) but which could mislead a future integration into believing
they already work. See hpc_connector/data_management/__init__.py's
NOTE (correction) docstrings for what each used to fabricate.
"""

from acf.hpc_connector.data_management import (
    Checksum,
    DataCatalog,
    DataPipeline,
    FileConverter,
    FileValidator,
    MetadataValidator,
)


def test_data_catalog_no_longer_fabricates():
    assert DataCatalog().list_datasets() == []


def test_metadata_validator_no_longer_claims_success():
    assert MetadataValidator().validate() is False


def test_checksum_no_longer_returns_the_algorithm_name_as_a_fake_hash():
    """
    CORRECTED: this used to ignore `path` entirely and return the
    literal string "sha256" (the algorithm name, not a hash) for ANY
    path - not even a plausible-looking fake hash.
    """
    assert Checksum().compute("/tmp/some_file.grib2") is None


def test_data_pipeline_no_longer_claims_success():
    assert DataPipeline().run() is False


def test_file_converter_and_validator_no_longer_claim_success():
    assert FileConverter().convert() is False
    assert FileValidator().validate() is False
