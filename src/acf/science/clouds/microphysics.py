"""
Atmospheric Complexity Framework (ACF)

Cloud Microphysics Engine
"""

import math

from acf.science.clouds.base import CloudProcess
from acf.science.clouds.registry import CloudScientificRegistry
from acf.science.constants import RHO_WATER


class CloudMicrophysicsEngine:
    """
    Moteur complet de microphysique des nuages (warm & cold cloud microphysics).
    """

    def __init__(self):
        self._register_microphysics_processes()

    def _register_microphysics_processes(self):
        processes = [
            CloudProcess(
                key="kessler_autoconversion",
                name="Schéma d'Autoconversion de Kessler",
                domain="Microphysique Nuageuse",
                equation="P_auto = k_auto * max(qc - qc_crit, 0)",
                variables={"qc": "Eau liquide nuageuse (kg/kg)", "qc_crit": "Seuil critique (kg/kg)"},
                units={"P_auto": "kg/(kg·s)"},
                description="Conversion des gouttelettes de nuage en gouttes de pluie par collision.",
                references=["Kessler (1969)", "WMO Cloud Physics Guidelines"],
                compute_func=self.kessler_autoconversion,
            ),
            CloudProcess(
                key="berry_autoconversion",
                name="Schéma d'Autoconversion de Berry",
                domain="Microphysique Nuageuse",
                equation="P_berry = (qc^2 * rho) / (60 * (1 + 0.03 * N / qc))",
                variables={"qc": "Eau nuageuse (kg/kg)", "N": "Concentration de gouttelettes (cm⁻³)"},
                units={"P_berry": "kg/(kg·s)"},
                description="Formulation de Berry prenant en compte la concentration numérique des gouttelettes.",
                references=["Berry (1968) J. Atmos. Sci."],
                compute_func=self.berry_autoconversion,
            ),
            CloudProcess(
                key="kohler_theory",
                name="Théorie de Köhler (Activation CCN)",
                domain="Microphysique Nuageuse",
                equation="ln(e/es) = A/r - B/r^3",
                variables={"r": "Rayon de la gouttelette (m)", "A": "Effet de courbure", "B": "Effet de soluté"},
                units={"e/es": "Sursaturation relative"},
                description="Équilibre de la pression de vapeur d'eau autour d'une gouttelette contenant un soluté dissous.",
                references=["Köhler (1936)", "Pruppacher & Klett (1997)"],
                compute_func=self.kohler_equilibrium,
            ),
            CloudProcess(
                key="collision_coalescence",
                name="Collision-Coalescence",
                domain="Microphysique Nuageuse",
                equation="P_coll = k_coll * qc * qr**0.875",
                variables={"qc": "Eau nuageuse", "qr": "Pluie"},
                units={"P_coll": "kg/(kg·s)"},
                description="Grossissement des gouttes de pluie par capture des gouttelettes nuageuses.",
                references=["Kessler (1969)", "Rogers & Yau (1989)"],
                compute_func=self.collision_coalescence,
            ),
            CloudProcess(
                key="rain_evaporation",
                name="Évaporation de la Pluie",
                domain="Microphysique Nuageuse",
                equation="E_rain = C_evap * (1 - RH) * qr**0.52",
                variables={"qr": "Pluie", "RH": "Humidité relative [0, 1]"},
                units={"E_rain": "kg/(kg·s)"},
                description="Sous-sursaturation entraînant la réévaporation des gouttes de pluie sous la base du nuage.",
                references=["ECMWF Microphysics Documentation"],
                compute_func=self.rain_evaporation,
            ),
            CloudProcess(
                key="bergeron_findeisen",
                name="Processus Bergeron-Findeisen",
                domain="Microphysique Nuageuse",
                equation="dm_ice/dt = 4*pi*C*(esi - esw) / (F_k + F_d)",
                variables={"esi": "Saturation / glace", "esw": "Saturation / eau"},
                units={"dm_ice/dt": "kg/s"},
                description="Croissance des cristaux de glace au détriment des gouttes d'eau surfondues dues à la différence de pression de vapeur de saturation.",
                references=["WMO Manual", "Pruppacher & Klett (1997)"],
                compute_func=self.bergeron_findeisen_rate,
            ),
            CloudProcess(
                key="homogeneous_freezing",
                name="Congélation Homogène",
                domain="Microphysique Nuageuse",
                equation="J_hom = V_drop * A_hom * exp(B_hom / (T - T_hom))",
                variables={"T": "Température (< -38°C)"},
                units={"J_hom": "s⁻¹"},
                description="Congélation spontanée des gouttelettes d'eau pure à des températures inférieures à -38°C.",
                references=["Koop et al. (2000) Nature"],
                compute_func=self.homogeneous_freezing_rate,
            ),
            CloudProcess(
                key="riming_graupel",
                name="Givrage et Formation de Grésil (Riming)",
                domain="Microphysique Nuageuse",
                equation="P_rim = E_rim * qc * v_fall_ice",
                variables={"qc": "Eau liquide surfondue", "v_fall": "Vitesse de chute"},
                units={"P_rim": "kg/(kg·s)"},
                description="Capture et congélation immédiate d'eau surfondu sur la surface de cristaux de neige ou de grésil.",
                references=["Rutledge & Hobbs (1983) J. Atmos. Sci."],
                compute_func=self.riming_rate,
            ),
            CloudProcess(
                key="liquid_water_content",
                name="Teneur en Eau Liquide (LWC)",
                domain="Microphysique Nuageuse",
                equation="LWC = qc * rho_air",
                variables={"qc": "Rapport de mélange en eau liquide nuageuse (kg/kg)", "rho_air": "Masse volumique de l'air"},
                units={"LWC": "kg/m³", "qc": "kg/kg", "rho_air": "kg/m³"},
                description="Masse d'eau liquide nuageuse par unité de volume d'air.",
                references=["Rogers & Yau (1989), A Short Course in Cloud Physics"],
                compute_func=self.liquid_water_content,
            ),
            CloudProcess(
                key="ice_water_content",
                name="Teneur en Eau Glace (IWC)",
                domain="Microphysique Nuageuse",
                equation="IWC = qi * rho_air",
                variables={"qi": "Rapport de mélange en glace nuageuse (kg/kg)", "rho_air": "Masse volumique de l'air"},
                units={"IWC": "kg/m³", "qi": "kg/kg", "rho_air": "kg/m³"},
                description="Masse de glace nuageuse par unité de volume d'air.",
                references=["Rogers & Yau (1989), A Short Course in Cloud Physics"],
                compute_func=self.ice_water_content,
            ),
            CloudProcess(
                key="droplet_effective_radius",
                name="Rayon Effectif des Gouttelettes (Martin et al. 1994)",
                domain="Microphysique Nuageuse",
                equation="re = (3 * LWC / (4 * pi * rho_water * k * N))^(1/3)",
                variables={
                    "LWC": "Teneur en eau liquide (kg/m³)",
                    "N": "Concentration numérique de gouttelettes (m⁻³)",
                    "k": "Paramètre de dispersion spectrale (largeur du spectre de tailles), ~0.67-0.85",
                },
                units={"re": "m", "LWC": "kg/m³", "N": "m⁻³"},
                description=(
                    "Relie le rayon effectif au rapport LWC/N via un paramètre de dispersion k qui dépend "
                    "de la largeur relative du spectre de tailles de gouttelettes (k=1 pour un spectre "
                    "monodispersé ; k<1 élargit re par rapport au rayon volumique moyen)."
                ),
                references=[
                    "Martin, G. M., Johnson, D. W., & Spice, A. (1994). J. Atmos. Sci., 51(13), 1823-1842.",
                ],
                limitations=[
                    "La valeur exacte de k selon le régime (maritime/continental) varie selon les sources "
                    "secondaires consultées ; ACF ne fige pas cette correspondance sans vérification "
                    "directe de la publication originale — k est un paramètre explicite de l'appelant, "
                    "pas une valeur codée en dur par régime.",
                ],
                compute_func=self.droplet_effective_radius,
            ),
        ]
        for p in processes:
            CloudScientificRegistry.register(p)

    def kessler_autoconversion(self, qc: float, qc_crit: float = 0.0005, k_auto: float = 0.001) -> float:
        return k_auto * max(qc - qc_crit, 0.0)

    def berry_autoconversion(self, qc: float, N_cm3: float = 100.0, density: float = 1.2) -> float:
        if qc <= 0:
            return 0.0
        return (qc**2 * density) / (60.0 * (1.0 + 0.03 * N_cm3 / max(qc, 1e-6)))

    def kohler_equilibrium(self, radius_m: float, solute_moles: float = 1e-18, temp_k: float = 288.15) -> float:
        # A = 2*sigma / (rho_w * R_v * T)
        A = 1.1e-9 / temp_k
        B = 4.3e-6 * solute_moles
        return 1.0 + A / max(radius_m, 1e-10) - B / max(radius_m**3, 1e-30)

    def collision_coalescence(self, qc: float, qr: float, k_coll: float = 2.2) -> float:
        if qc <= 0 or qr <= 0:
            return 0.0
        return k_coll * qc * (qr**0.875)

    def rain_evaporation(self, qr: float, rh: float, temp_k: float = 288.15) -> float:
        """
        NOTE (found, NOT changed - Physics Guard): temp_k is accepted but
        unused. Simplified Kessler-type evaporation parameterizations
        commonly express the rate purely via the humidity deficit (1-RH)
        and rain mixing ratio qr, folding temperature dependence (which
        physically enters through saturation vapor pressure/ventilation
        coefficient) into rh itself rather than as a separate term - in
        which case this is dimensionally complete as written. Some
        fuller schemes (e.g. Tripoli & Cotton 1980) do carry an explicit
        T-dependent ventilation term instead. I don't have a specific
        citable source pinning down whether *this* coefficient (1.41e-3)
        and exponent (0.52) were derived with or without that term, so
        can't safely add a temperature factor without risking a real
        unit/magnitude error - flagged rather than guessed, same
        situation as NavierStokesVertical's density NOTE in dynamics.py.
        """
        if qr <= 0 or rh >= 1.0:
            return 0.0
        return 1.41e-3 * (1.0 - rh) * (qr**0.52)

    def bergeron_findeisen_rate(self, temp_k: float, qi: float, qc: float) -> float:
        if temp_k >= 273.15 or qc <= 0:
            return 0.0
        # Difference between saturation over water and ice
        es_w = 611.2 * math.exp((17.67 * (temp_k - 273.15)) / (temp_k - 29.65))
        es_i = 611.2 * math.exp((22.51 * (temp_k - 273.15)) / (temp_k - 0.7))
        return 1e-5 * max(es_w - es_i, 0.0) * max(qi, 1e-6)

    def homogeneous_freezing_rate(self, temp_k: float, qc: float) -> float:
        if temp_k > 235.15 or qc <= 0:
            return 0.0
        return qc * 0.1  # Rapid conversion below -38°C

    def riming_rate(self, qc: float, qs: float) -> float:
        if qc <= 0 or qs <= 0:
            return 0.0
        return 0.05 * qc * (qs**0.9)

    def liquid_water_content(self, qc: float, air_density: float = 1.2) -> float:
        """
        Liquid water content: LWC = qc * rho_air (kg/m^3).

        Parameters
        ----------
        qc : float
            Cloud liquid water mixing ratio (kg/kg).
        air_density : float
            Air density (kg/m^3). Defaults to a typical near-surface value.
        """
        if qc < 0:
            raise ValueError("qc must be non-negative.")
        return qc * air_density

    def ice_water_content(self, qi: float, air_density: float = 1.2) -> float:
        """
        Ice water content: IWC = qi * rho_air (kg/m^3).

        Parameters
        ----------
        qi : float
            Cloud ice mixing ratio (kg/kg).
        air_density : float
            Air density (kg/m^3). Defaults to a typical near-surface value.
        """
        if qi < 0:
            raise ValueError("qi must be non-negative.")
        return qi * air_density

    def droplet_effective_radius(
        self,
        liquid_water_content_kg_m3: float,
        droplet_number_concentration_m3: float,
        k: float = 0.8,
    ) -> float:
        """
        Cloud droplet effective radius (Martin et al., 1994 parameterization).

        re = (3 * LWC / (4*pi*rho_water*k*N))^(1/3)

        Parameters
        ----------
        liquid_water_content_kg_m3 : float
            Liquid water content (kg/m^3) — see liquid_water_content().
        droplet_number_concentration_m3 : float
            Cloud droplet number concentration (m^-3).
        k : float
            Spectral dispersion parameter (dimensionless), representing
            the width of the droplet size spectrum relative to a
            monodisperse distribution (k=1). Typical literature values
            fall in roughly the 0.67-0.85 range; ACF does not hard-code
            a maritime/continental split (see the CloudProcess entry's
            limitations note) — pass the value appropriate to the case.

        Returns
        -------
        float
            Effective radius (m).

        Reference
        ---------
        Martin, G. M., Johnson, D. W., & Spice, A. (1994). "The
        Measurement and Parameterization of Effective Radius of
        Droplets in Warm Stratocumulus Clouds". J. Atmos. Sci.,
        51(13), 1823-1842.
        """
        if liquid_water_content_kg_m3 < 0:
            raise ValueError("liquid_water_content must be non-negative.")
        if droplet_number_concentration_m3 <= 0:
            raise ValueError("droplet_number_concentration must be positive.")
        if k <= 0:
            raise ValueError("k must be positive.")

        return (
            3.0
            * liquid_water_content_kg_m3
            / (4.0 * math.pi * RHO_WATER * k * droplet_number_concentration_m3)
        ) ** (1.0 / 3.0)

    def compute_budget(
        self, qv: float, qc: float, qr: float, qi: float, qs: float, qg: float, dt: float = 1.0
    ) -> dict[str, float]:
        """
        Calcule la conservation de la masse d'eau entre les 6 phases: qv, qc, qr, qi, qs, qg.
        """
        # Autoconversion
        p_auto = self.kessler_autoconversion(qc)
        # Collection
        p_coll = self.collision_coalescence(qc, qr)

        dqc = -(p_auto + p_coll) * dt
        dqr = (p_auto + p_coll) * dt

        # Ensure non-negative species
        new_qc = max(qc + dqc, 0.0)
        new_qr = max(qr + dqr, 0.0)

        total_water_before = qv + qc + qr + qi + qs + qg
        total_water_after = qv + new_qc + new_qr + qi + qs + qg

        return {
            "qv": qv,
            "qc": new_qc,
            "qr": new_qr,
            "qi": qi,
            "qs": qs,
            "qg": qg,
            "total_water": total_water_after,
            "mass_conserved": abs(total_water_before - total_water_after) < 1e-12,
        }
