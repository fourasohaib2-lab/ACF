"""Double-moment bulk microphysics parameterization engine."""

import numpy as np


class MicrophysicsEngine:
    """Double-moment microphysics scheme for 6 hydrometeor species:

    Species:
    1. Cloud Water (q_c, N_c)
    2. Cloud Ice (q_i, N_i)
    3. Rain (q_r, N_r)
    4. Snow (q_s, N_s)
    5. Graupel (q_g, N_g)
    6. Hail (q_h, N_h)

    Calculates:
    - Liquid Water Content (LWC, g/m^3)
    - Ice Water Content (IWC, g/m^3)
    - Phase change conversion rates (condensation, deposition, freezing, melting, auto-conversion)
    """

    def __init__(self) -> None:
        self.rho_water = 1000.0  # kg/m^3
        self.rho_ice = 917.0  # kg/m^3
        self.latent_heat_vap = 2.501e6  # J/kg
        self.latent_heat_fusion = 3.34e5  # J/kg

    def initialize_hydrometeors(self, shape: tuple[int, ...]) -> dict[str, np.ndarray]:
        """Initialize mixing ratio tensors (kg/kg) and number concentrations (#/m^3)."""
        return {
            "qc": np.zeros(shape, dtype=np.float64),  # Cloud water
            "qi": np.zeros(shape, dtype=np.float64),  # Cloud ice
            "qr": np.zeros(shape, dtype=np.float64),  # Rain
            "qs": np.zeros(shape, dtype=np.float64),  # Snow
            "qg": np.zeros(shape, dtype=np.float64),  # Graupel
            "qh": np.zeros(shape, dtype=np.float64),  # Hail
            "Nc": np.full(shape, 1e8, dtype=np.float64),  # Cloud droplets concentration
            "Ni": np.full(shape, 1e4, dtype=np.float64),  # Ice crystals concentration
            "Nr": np.zeros(shape, dtype=np.float64),
            "Ns": np.zeros(shape, dtype=np.float64),
            "Ng": np.zeros(shape, dtype=np.float64),
            "Nh": np.zeros(shape, dtype=np.float64),
        }

    def compute_water_content(
        self, state_hydros: dict[str, np.ndarray], air_density: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        """Compute Liquid Water Content (LWC) and Ice Water Content (IWC) in g/m^3.

        Args:
            state_hydros (Dict[str, np.ndarray]): Hydrometeor mixing ratios.
            air_density (np.ndarray): Air density in kg/m^3.

        Returns:
            Tuple[np.ndarray, np.ndarray]: (LWC_g_m3, IWC_g_m3)
        """
        # LWC = rho_air * (qc + qr) * 1000
        lwc = air_density * (state_hydros["qc"] + state_hydros["qr"]) * 1000.0
        # IWC = rho_air * (qi + qs + qg + qh) * 1000
        iwc = air_density * (state_hydros["qi"] + state_hydros["qs"] + state_hydros["qg"] + state_hydros["qh"]) * 1000.0
        return lwc, iwc

    def step(
        self,
        hydros: dict[str, np.ndarray],
        temp: np.ndarray,
        q_vap: np.ndarray,
        air_density: np.ndarray,
        dt: float = 60.0,
    ) -> tuple[dict[str, np.ndarray], np.ndarray]:
        """Advance microphysical phase changes over time step dt.

        Args:
            hydros: Dictionary of hydrometeor fields.
            temp: Air temperature tensor (K).
            q_vap: Water vapor mixing ratio (kg/kg).
            air_density: Density of air (kg/m^3).
            dt: Timestep (s).

        NOTE (found, NOT changed - Physics Guard, flagged by
        `ruff --select ARG`): air_density is accepted but unused below -
        every rate here (auto-conversion, freezing, melting) is
        expressed purely as a fraction of the current mixing ratio per
        second, and mixing ratios (kg/kg, already normalized by air
        mass) are legitimately density-independent quantities in this
        kind of simplified bulk scheme - unlike calculate_lwc_iwc()
        just above, which genuinely needs air_density to convert a
        mixing ratio into a volumetric concentration (g/m^3). Some
        fuller Kessler-family schemes do fold air_density into specific
        terms (e.g. sedimentation, ventilation-dependent evaporation),
        neither of which this simplified step() implements, so there is
        no clear place it would enter here without inventing a term.

        Returns:
            Tuple[Dict[str, np.ndarray], np.ndarray]: (Updated hydrometeors, Updated q_vap)
        """
        qc = hydros["qc"].copy()
        qi = hydros["qi"].copy()
        qr = hydros["qr"].copy()
        qv = q_vap.copy()

        # Simple threshold auto-conversion: Cloud water -> Rain (Kessler scheme proxy)
        #
        # NOTE (correction): the tendency*dt amount transferred between species
        # was applied unclamped to BOTH sides, then only the *source* species
        # was clipped to >= 0 at the end of step(). With a rate*dt product that
        # exceeds the available mass (e.g. the melt_rate=0.05 s^-1 default
        # combined with the default dt=60s gives melt_rate*dt = 3.0, i.e. 3x
        # qi), the source got clamped away but the sink kept the full
        # (unphysical) amount - manufacturing water mass out of nothing. Each
        # transferred amount is now capped at the available source mass
        # *before* being applied to both species, so source and sink always
        # move by exactly the same, physically-bounded quantity (mass
        # conservation, per the Kessler-type conservation rule this module
        # is meant to respect).
        auto_conversion_rate = np.maximum(0.0, qc - 0.0005) * 1e-3
        auto_conversion_amount = np.minimum(auto_conversion_rate * dt, np.maximum(qc, 0.0))
        qc -= auto_conversion_amount
        qr += auto_conversion_amount

        # Freezing of cloud water to cloud ice below 273.15 K
        freezing_mask = temp < 273.15
        freeze_rate = np.where(freezing_mask, 0.01 * qc, 0.0)
        freeze_amount = np.minimum(freeze_rate * dt, np.maximum(qc, 0.0))
        qc -= freeze_amount
        qi += freeze_amount

        # Melting of ice above 273.15 K
        melt_mask = temp >= 273.15
        melt_rate = np.where(melt_mask, 0.05 * qi, 0.0)
        melt_amount = np.minimum(melt_rate * dt, np.maximum(qi, 0.0))
        qi -= melt_amount
        qc += melt_amount

        updated_hydros = hydros.copy()
        updated_hydros["qc"] = np.clip(qc, 0.0, None)
        updated_hydros["qi"] = np.clip(qi, 0.0, None)
        updated_hydros["qr"] = np.clip(qr, 0.0, None)

        return updated_hydros, np.clip(qv, 1e-7, None)
