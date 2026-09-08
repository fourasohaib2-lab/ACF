"""Multi-layer soil thermodynamics and hydrology solver."""

import numpy as np


class SoilModel:
    """Multi-layer soil model for moisture and thermal dynamics.

    Solves Richards equation for soil moisture transport:
        dtheta/dt = d/dz [ K(theta) * (dpsi/dz + 1) ]
    and heat conduction equation for soil temperature:
        C_s * dT_soil/dt = d/dz [ k_s * dT_soil/dz ]

    Tracks:
    - Soil moisture theta (m^3/m^3)
    - Soil temperature T_soil (K)
    - Freeze/thaw ice fraction
    """

    def __init__(self, n_soil_layers: int = 4) -> None:
        self.n_soil_layers = n_soil_layers
        self.layer_depths = np.array([0.1, 0.4, 1.0, 2.0])  # meters depth

    def initialize_soil_state(self, shape_2d: tuple[int, int]) -> dict[str, np.ndarray]:
        """Initialize soil physical fields across layers."""
        shape_3d = (self.n_soil_layers,) + shape_2d
        state = {
            "soil_moisture": np.full(shape_3d, 0.25, dtype=np.float64),  # m^3/m^3
            "soil_temperature": np.full(shape_3d, 288.15, dtype=np.float64),  # K
            "frozen_fraction": np.zeros(shape_3d, dtype=np.float64),
        }
        return state

    def step(
        self,
        soil_state: dict[str, np.ndarray],
        precip_rate: np.ndarray,
        evapotranspiration: np.ndarray,
        surface_temp: np.ndarray,
        dt: float = 3600.0,
    ) -> dict[str, np.ndarray]:
        """Advance soil moisture and temperature over time step dt.

        Args:
            soil_state: Current soil state dictionary.
            precip_rate: Infiltration rainfall rate (m/s).
            evapotranspiration: Evapotranspiration rate (m/s).
            surface_temp: Air/surface skin temperature (K).
            dt: Timestep (s).

        Returns:
            Dict[str, np.ndarray]: Updated soil state.

        NOTE (found, NOT changed — Physics Guard, found during the
        post-model4d audit, 2026-09-06): despite this class's own
        docstring naming the Richards equation (vertical moisture
        transport between layers) and heat conduction equation (both
        genuinely multi-layer PDEs) as what this model "solves", only
        soil_moisture[0]/soil_temperature[0] (the surface layer) are
        ever updated below - layers 1..n_soil_layers-1 are copied
        unchanged and stay frozen at their initialize_soil_state()
        values through every real call. A genuine Richards-equation
        solve needs an unsaturated hydraulic conductivity K(theta)
        relationship and a real finite-difference discretization across
        layers - not implemented here, and not invented in this pass
        without a citable source (same reasoning as this codebase's
        other undocumented-formula findings). acf.gui.esoc.panel_manager
        .LandSurfacePanel (the real UI for this model) is updated in
        the same commit to disclose this, matching the existing
        acf.gui.esoc.panel_manager.OceanPanel.amoc_label convention for
        a comparable gap.
        """
        moisture = soil_state["soil_moisture"].copy()
        temp = soil_state["soil_temperature"].copy()

        # Surface layer (layer 0) moisture update
        inflow = (precip_rate - evapotranspiration) * dt / self.layer_depths[0]
        moisture[0] = np.clip(moisture[0] + inflow, 0.05, 0.45)  # Porosity bound 0.45

        # Surface layer temperature relaxation towards surface skin temperature
        temp[0] += (surface_temp - temp[0]) * (1.0 - np.exp(-dt / 86400.0))

        # Freeze/thaw state calculation
        frozen_frac = np.where(temp < 273.15, np.clip((273.15 - temp) / 5.0, 0.0, 1.0), 0.0)

        return {
            "soil_moisture": moisture,
            "soil_temperature": temp,
            "frozen_fraction": frozen_frac,
        }
