"""
Visibility
==========

Koschmieder's law, extinction from liquid water content, ICAO ILS
operating categories, and a qualitative fog-risk heuristic.

Reference:
    Koschmieder, H. (1924). "Theorie der horizontalen
    Sichtweite". Beitr. Phys. Freien Atmos., 12, 33-53, 171-181.
    ICAO Annex 6 to the Convention on International Civil Aviation —
    Operation of Aircraft (CAT I/II/IIIa/IIIb/IIIc definitions,
    verified against two independent sources converging on the same
    RVR/DH values).
"""

from acf.science.constants import RHO_WATER

# Contrast threshold for the human eye (2%), giving the standard
# Koschmieder constant ln(1/0.02) = 3.912.
KOSCHMIEDER_CONSTANT = 3.912


class Koschmieder:
    """Meteorological optical range (visibility) from the extinction coefficient."""

    @staticmethod
    def visibility(extinction_coefficient_per_m: float) -> float:
        """
        V = 3.912 / sigma_ext   (Koschmieder's law)

        Parameters
        ----------
        extinction_coefficient_per_m : float
            Atmospheric extinction coefficient (m^-1), > 0.

        Returns
        -------
        float
            Meteorological optical range / visibility (m).

        Reference
        ---------
        Koschmieder (1924). Uses the standard 2% contrast threshold.
        """
        if extinction_coefficient_per_m <= 0:
            raise ValueError("extinction_coefficient_per_m must be positive.")
        return KOSCHMIEDER_CONSTANT / extinction_coefficient_per_m

    @staticmethod
    def extinction_coefficient_from_lwc(liquid_water_content_kg_m3: float, effective_radius_m: float) -> float:
        """
        Extinction coefficient from liquid water content and droplet
        effective radius, sigma_ext = 3*LWC / (2*rho_water*r_eff).

        This is the per-unit-volume form of the same physical relation
        used by CloudRadiationEngine.cloud_optical_depth() (which
        integrates it over a path length to get optical depth) — not
        a different formula, just applied locally instead of
        path-integrated.

        Parameters
        ----------
        liquid_water_content_kg_m3 : float
            Liquid water content (kg/m^3), >= 0.
        effective_radius_m : float
            Droplet effective radius (m), > 0 — see
            CloudMicrophysicsEngine.droplet_effective_radius() (Martin
            et al. 1994) for fog droplets specifically.

        Returns
        -------
        float
            Extinction coefficient (m^-1).

        Reference
        ---------
        Stephens (1978); same relation as used in
        science/clouds/radiation.py's cloud_optical_depth().
        """
        if liquid_water_content_kg_m3 < 0:
            raise ValueError("liquid_water_content_kg_m3 must be non-negative.")
        if effective_radius_m <= 0:
            raise ValueError("effective_radius_m must be positive.")
        return 3.0 * liquid_water_content_kg_m3 / (2.0 * RHO_WATER * effective_radius_m)

    @staticmethod
    def visibility_from_lwc(liquid_water_content_kg_m3: float, effective_radius_m: float) -> float:
        """
        Convenience chain: visibility directly from LWC and droplet
        effective radius, composing extinction_coefficient_from_lwc()
        + visibility().
        """
        sigma = Koschmieder.extinction_coefficient_from_lwc(liquid_water_content_kg_m3, effective_radius_m)
        return Koschmieder.visibility(sigma)


class ICAOCategory:
    """ICAO Annex 6 instrument approach operating categories (CAT I/II/III)."""

    @staticmethod
    def classify(decision_height_m: float | None, rvr_m: float | None) -> str:
        """
        Classify an approach's operating category from decision height
        (DH) and runway visual range (RVR), per ICAO Annex 6.

        Parameters
        ----------
        decision_height_m : float or None
            Decision height (m AGL). None means "no DH" (autoland).
        rvr_m : float or None
            Runway visual range (m). None means "no RVR limitation".

        Returns
        -------
        str
            One of "CAT I", "CAT II", "CAT IIIa", "CAT IIIb", "CAT IIIc",
            or "Below CAT III minima" if neither DH nor RVR qualifies
            for any defined category.

        Reference
        ---------
        ICAO Annex 6, Operation of Aircraft:
            CAT I:   DH >= 60m (200ft),        RVR >= 550m (or vis >= 800m)
            CAT II:  30m <= DH < 60m (100-200ft), RVR >= 300m
            CAT IIIa: DH < 30m (100ft) or none,  RVR >= 175m
            CAT IIIb: DH < 15m (50ft) or none,   RVR 50-175m
            CAT IIIc: no DH, no RVR limit
        """
        dh = decision_height_m
        rvr = rvr_m

        if dh is None and rvr is None:
            return "CAT IIIc"
        if (dh is None or dh < 15.0) and rvr is not None and 50.0 <= rvr < 175.0:
            return "CAT IIIb"
        if (dh is None or dh < 30.0) and rvr is not None and rvr >= 175.0:
            return "CAT IIIa"
        if dh is not None and 30.0 <= dh < 60.0 and rvr is not None and rvr >= 300.0:
            return "CAT II"
        if dh is not None and dh >= 60.0 and rvr is not None and rvr >= 550.0:
            return "CAT I"
        return "Below CAT III minima"


class FogRisk:
    """Qualitative fog-formation risk heuristic (NOT a physical law)."""

    @staticmethod
    def radiation_fog_risk(
        wind_speed_m_s: float,
        cloud_cover_fraction: float,
        dewpoint_depression_k: float,
        is_nighttime: bool,
    ) -> str:
        """
        Qualitative radiation-fog risk from classic forecasting rules
        of thumb (clear skies + light wind + small T-Td spread +
        nighttime cooling favor radiation fog). This is a heuristic
        diagnostic aid, not a validated physical formula — unlike
        Koschmieder's law above, there is no single citable equation
        for "fog risk"; thresholds here are standard operational
        forecasting guidance, not derived from a primary reference.

        Parameters
        ----------
        wind_speed_m_s : float
            Surface wind speed (m/s). Light wind (~1-3 m/s) favors
            radiation fog; calm (<0.5 m/s) suppresses the mixing
            needed to spread cooling through a shallow layer; strong
            wind (>5 m/s) mixes the fog away.
        cloud_cover_fraction : float
            Cloud cover in [0, 1]. Low cover favors radiative cooling.
        dewpoint_depression_k : float
            T - Td (K). Small spread favors saturation by cooling.
        is_nighttime : bool
            Radiation fog is a nocturnal/early-morning phenomenon.

        Returns
        -------
        str
            "Low", "Moderate", or "High".
        """
        if not (0.0 <= cloud_cover_fraction <= 1.0):
            raise ValueError("cloud_cover_fraction must be in [0, 1].")

        if not is_nighttime:
            return "Low"

        score = 0
        if 0.5 <= wind_speed_m_s <= 3.0:
            score += 1
        if cloud_cover_fraction < 0.3:
            score += 1
        if dewpoint_depression_k < 2.5:
            score += 1

        if score >= 3:
            return "High"
        if score == 2:
            return "Moderate"
        return "Low"
