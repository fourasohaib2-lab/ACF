from acf.catalog.catalog import ScientificCatalog
from acf.catalog.surface_parameters import register_surface
from acf.catalog.atmospheric_parameters import register_atmosphere
from acf.catalog.ocean_parameters import register_ocean
from acf.catalog.satellite_parameters import register_satellite
from acf.catalog.climate_parameters import register_climate


def create_catalog():

    catalog = ScientificCatalog()

    register_surface(catalog)
    register_atmosphere(catalog)
    register_ocean(catalog)
    register_satellite(catalog)
    register_climate(catalog)

    return catalog
