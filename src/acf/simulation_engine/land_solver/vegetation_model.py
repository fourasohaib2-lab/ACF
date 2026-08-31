"""Dynamic vegetation and terrestrial biosphere simulator."""

import numpy as np


class VegetationModel:
    """Dynamic vegetation model tracking biosphere canopy variables:

    - LAI: Leaf Area Index (m^2 leaf / m^2 ground)
    - NDVI: Normalized Difference Vegetation Index ([0, 1])
    - NPP: Net Primary Productivity (g C / m^2 / day)
    - Evapotranspiration (ET) resistance
    """

    def __init__(self) -> None:
        pass

    def compute_vegetation_indices(
        self, temperature_k: np.ndarray, soil_moisture: np.ndarray, solar_radiation: np.ndarray
    ) -> dict[str, np.ndarray]:
        """Compute LAI, NDVI, and NPP from climate forcing drivers.

        Args:
            temperature_k (np.ndarray): Surface air temperature (K).
            soil_moisture (np.ndarray): Topsoil moisture (m^3/m^3).
            solar_radiation (np.ndarray): Downward shortwave radiation (W/m^2).

        Returns:
            Dict[str, np.ndarray]: Vegetation state metrics.
        """
        temp_c = temperature_k - 273.15

        # Temperature growth factor f(T)
        f_temp = np.clip(1.0 - ((temp_c - 25.0) / 20.0) ** 2, 0.0, 1.0)

        # Moisture factor f(W)
        f_moist = np.clip((soil_moisture - 0.05) / 0.3, 0.0, 1.0)

        # Solar factor f(PAR)
        par = solar_radiation * 0.45  # Photosynthetically Active Radiation
        f_par = par / (par + 100.0 + 1e-8)

        # LAI formulation: LAI = LAI_max * f_temp * f_moist * f_par
        lai_max = 6.0
        lai = lai_max * f_temp * f_moist * f_par

        # Empirical NDVI relationship: NDVI ~ 0.8 * (1 - exp(-0.5 * LAI))
        ndvi = 0.8 * (1.0 - np.exp(-0.5 * lai))

        # Gross Primary Productivity (GPP) & NPP (NPP ~ 0.5 * GPP)
        gpp = 12.0 * f_temp * f_moist * f_par * (lai / 3.0)  # g C / m^2 / day
        npp = 0.5 * gpp

        return {
            "LAI": lai,
            "NDVI": ndvi,
            "NPP": npp,
            "canopy_resistance": 100.0 / (lai + 1e-3),  # s/m
        }
