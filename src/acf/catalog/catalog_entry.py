from dataclasses import dataclass


@dataclass(slots=True)
class CatalogEntry:

    parameter_id: str

    standard_name: str

    long_name: str

    units: str

    category: str

    level_type: str

    renderer: str

    colormap: str

    grib_code: str = ""

    cf_name: str = ""

    description: str = ""
