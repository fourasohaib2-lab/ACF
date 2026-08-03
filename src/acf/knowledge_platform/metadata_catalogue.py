"""
Atmospheric Complexity Framework (ACF)

WMO, CF, GRIB2 & NetCDF Metadata Catalogue Module
"""

from typing import Any, Dict, Optional
from acf.knowledge_platform.parameter_database import PARAMETERS_DB


class MetadataCatalogue:
    """
    Catalogue d'indexation et de conversion des métadonnées OMM / CF / GRIB2 / BUFR / NetCDF.
    """

    @classmethod
    def lookup_by_grib2(cls, grib2_code: str) -> Optional[Dict[str, Any]]:
        """Retrouve le paramètre ACF correspondant à un code GRIB2 'discipline,category,number'."""
        for param in PARAMETERS_DB.values():
            if param.grib2_identifier == grib2_code:
                return param.to_dict()
        return None

    @classmethod
    def lookup_by_cf_standard_name(cls, cf_name: str) -> Optional[Dict[str, Any]]:
        """Retrouve le paramètre ACF correspondant à un nom standard CF."""
        for param in PARAMETERS_DB.values():
            if param.cf_convention_name.lower() == cf_name.lower():
                return param.to_dict()
        return None

    @classmethod
    def export_full_catalogue(cls) -> Dict[str, Any]:
        """Exporte la totalité des métadonnées sous forme de dictionnaire structuré."""
        return {
            "total_parameters_catalogued": len(PARAMETERS_DB),
            "parameters": {k: p.to_dict() for k, p in PARAMETERS_DB.items()},
        }
