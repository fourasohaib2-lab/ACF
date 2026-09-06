"""
acf.catalog (singular) - the real, load-bearing parameter/dataset
catalog: ScientificCatalog + CatalogEntry (catalog.py/catalog_entry.py),
DatasetCatalog/DatasetRegistry/DatasetEntry, ParameterMapper (alias
resolution, e.g. "T2"/"TMP"/"2T" -> canonical "t2m"), and default_catalog.
py/default_mapping.py which populate both from the *_parameters.py data
tables (atmospheric/ocean/climate/surface/satellite - real CF standard
names and units, e.g. specific_humidity in "kg kg-1"). CatalogManager
(manager.py) ties ScientificCatalog + DatasetCatalog together.

Verified 2026-09-06 by grep: this is the version actually imported by
real application code (acf.gui.esoc, acf.data.manager, acf.data.
dataset_registry, acf.importers.readers.netcdf_reader) - not the
plural `acf.catalogs` package, which is a much smaller, separate
CF/ECMWF-standards-specific extension layered on top of THIS package's
own CatalogManager (see acf.catalogs's own docstring for that
relationship) - the two are not competing duplicates of the same thing.
"""
