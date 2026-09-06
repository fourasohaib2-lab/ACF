"""
acf.catalogs (plural) - a small CF/ECMWF-standards-specific extension,
NOT a competing duplicate of the real `acf.catalog` (singular) package
(see that package's own docstring for its own, much larger, load-
bearing implementation - verified by grep to be what real application
code actually imports).

This package's own catalog_manager.py is explicitly labeled a
"Compatibility Layer forwarding to acf.catalog.manager" (it just
re-exports acf.catalog.manager.CatalogManager). What IS real and
distinct here: CFCatalog (cf/catalog.py, built from
acf.standards.cf_standard_names) and ECMWFCatalog (ecmwf/catalog.py,
built from acf.standards.ecmwf.manager), unified by CatalogHub
(hub.py) - a thin loader for two specific external standards, used
today by acf.search.scientific_search (its only real caller outside
this package, verified by grep). `managers/` and `loaders/` are empty
subpackages (no content beyond their own `__init__.py`) - disclosed,
not populated or removed (see AGENTS.md on not deleting without an
explicit request).
"""
