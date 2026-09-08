"""
Atmospheric Complexity Framework (ACF)

NWP Models Encyclopedia Package (ECMWF IFS, Météo-France AROME, WRF, DWD ICON)
"""

from acf.science.encyclopedia.nwp_models import arome, icon, ifs, wrf
from acf.science.encyclopedia.nwp_models.arome import ENTRIES as AROME_ENTRIES
from acf.science.encyclopedia.nwp_models.icon import ENTRIES as ICON_ENTRIES
from acf.science.encyclopedia.nwp_models.ifs import ENTRIES as IFS_ENTRIES
from acf.science.encyclopedia.nwp_models.wrf import ENTRIES as WRF_ENTRIES

__all__ = [
    "AROME_ENTRIES",
    "ICON_ENTRIES",
    "IFS_ENTRIES",
    "WRF_ENTRIES",
    "arome",
    "icon",
    "ifs",
    "wrf",
]
