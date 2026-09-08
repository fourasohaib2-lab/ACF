"""Severe storm, supercell, and tornado risk simulation engine."""

import numpy as np


class SevereStormSimulator:
    """Supercell, tornado, hail, and severe convective storm simulator.

    Evaluates severe weather indices:
    - Supercell Composite Parameter (SCP)
    - Significant Tornado Parameter (STP)
    - Maximum Expected Hail Size (MESH, mm)
    - Deep layer vertical wind shear (0-6km, m/s)
    - Helicity (SRH, m^2/s^2)
    """

    def __init__(self) -> None:
        pass

    def evaluate_severe_storm_risk(
        self,
        cape: np.ndarray,
        srh_03km: np.ndarray,
        bulk_shear_06km: np.ndarray,
        cin: np.ndarray,
    ) -> dict[str, np.ndarray]:
        """Compute SCP, STP, and Hail Size MESH metrics across grid.

        STP = (CAPE / 1500) * ((2000 - LCL) / 1000) * (SRH / 150) * (BulkShear / 20)

        Args:
            cape (np.ndarray): CAPE array (J/kg).
            srh_03km (np.ndarray): Storm-relative helicity 0-3km (m^2/s^2).
            bulk_shear_06km (np.ndarray): Bulk wind shear 0-6km (m/s).
            cin (np.ndarray): CIN array (J/kg).

        Returns:
            Dict[str, np.ndarray]: Severe storm diagnostic maps.
        """
        # Supercell Composite Parameter SCP = (CAPE/1000) * (SRH/50) * (BulkShear/20)
        scp = (cape / 1000.0) * (srh_03km / 50.0) * (bulk_shear_06km / 20.0)
        scp = np.clip(scp, 0.0, None)

        # Significant Tornado Parameter STP
        stp = (cape / 1500.0) * (srh_03km / 150.0) * (bulk_shear_06km / 20.0)
        stp = np.where(cin < 100.0, np.clip(stp, 0.0, None), 0.0)

        # Maximum Expected Hail Size (MESH, mm) ~ 2.5 * (CAPE^0.5) * (Shear/10)
        hail_mesh_mm = np.where(cape > 1000.0, 2.5 * np.sqrt(cape) * (bulk_shear_06km / 10.0), 0.0)

        return {
            "SCP": scp,
            "STP": stp,
            "hail_mesh_mm": np.clip(hail_mesh_mm, 0.0, 120.0),
            "supercell_risk": scp > 1.0,
            "tornado_risk": stp > 1.0,
        }
