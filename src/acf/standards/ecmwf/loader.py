"""
ECMWF JSON Loader (Compatibility Layer forwarding to acf.importers.ecmwf.importer)
"""

from acf.importers.ecmwf.importer import ECMWFImporter as ECMWFLoader

__all__ = ["ECMWFLoader"]
