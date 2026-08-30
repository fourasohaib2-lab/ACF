"""
Synoptic Meteorology
=====================

Coriolis parameter, geostrophic and thermal wind, and a facade over
the existing Ertel potential vorticity implementation.

Fixes two registry gaps: 'ertel_potential_vorticity' and
'thermal_wind' in science/laws/dynamics.py had no compute_func
(NotImplementedError on .calculate()) despite being registered,
documented laws — same class of bug found and fixed earlier this
session (monin_obukhov_length, planck_law).

NOT implemented here (documented gap, not fabricated): the Thermal
Front Parameter (TFP, Hewson 1998) used for automated front location.
It requires the gradient of a 2D scalar field's gradient magnitude
(a grid-based second-derivative operation), a different kind of input
(gridded field, not scalar point values) from everything else in
science/ so far — needs a small grid/field-differentiation utility
that doesn't exist yet. Flagged rather than approximated.

Reference:
    Holton, J. R., & Hakim, G. J. (2012). "An Introduction to
    Dynamic Meteorology" (5th ed.). Academic Press.
"""

import math

from acf.science.constants import OMEGA, RD
from acf.science.potential_vorticity import PotentialVorticity

EARTH_RADIUS_M = 6371000.0


class Coriolis:
    """Coriolis parameter f and the beta (meridional gradient) parameter."""

    @staticmethod
    def parameter(latitude_deg: float) -> float:
        """
        f = 2 * Omega * sin(latitude)

        Parameters
        ----------
        latitude_deg : float
            Latitude (degrees, -90 to 90).

        Returns
        -------
        float
            Coriolis parameter f (s^-1). Zero at the equator, changes
            sign across hemispheres.
        """
        if not (-90.0 <= latitude_deg <= 90.0):
            raise ValueError("latitude_deg must be in [-90, 90].")
        return 2.0 * OMEGA * math.sin(math.radians(latitude_deg))

    @staticmethod
    def beta_parameter(latitude_deg: float) -> float:
        """
        beta = df/dy = 2 * Omega * cos(latitude) / R_earth

        The meridional gradient of the Coriolis parameter — governs
        Rossby wave propagation.

        Parameters
        ----------
        latitude_deg : float
            Latitude (degrees, -90 to 90).

        Returns
        -------
        float
            beta (m^-1 s^-1).
        """
        if not (-90.0 <= latitude_deg <= 90.0):
            raise ValueError("latitude_deg must be in [-90, 90].")
        return 2.0 * OMEGA * math.cos(math.radians(latitude_deg)) / EARTH_RADIUS_M


class GeostrophicWind:
    """Geostrophic wind from the horizontal pressure gradient."""

    @staticmethod
    def calculate(dp_dx: float, dp_dy: float, density: float, coriolis_f: float) -> tuple[float, float]:
        """
        f*vg = (1/rho)*dp/dx  ;  f*ug = -(1/rho)*dp/dy

        Parameters
        ----------
        dp_dx, dp_dy : float
            Horizontal pressure gradient components (Pa/m).
        density : float
            Air density (kg/m^3), > 0.
        coriolis_f : float
            Coriolis parameter (s^-1), non-zero (undefined at the
            equator — the geostrophic approximation breaks down there
            anyway).

        Returns
        -------
        tuple of float
            (ug, vg) geostrophic wind components (m/s).

        Reference
        ---------
        Holton & Hakim (2012), Ch. 2. Same formula already registered
        as the 'geostrophic_balance' law — this class gives it a
        proper reusable implementation instead of only an inline
        lambda.
        """
        if density <= 0:
            raise ValueError("density must be positive.")
        if coriolis_f == 0:
            raise ValueError("coriolis_f must not be zero (undefined at the equator).")

        ug = -dp_dy / (coriolis_f * density)
        vg = dp_dx / (coriolis_f * density)
        return ug, vg


class ThermalWind:
    """Thermal wind: vertical shear of the geostrophic wind from horizontal temperature gradients."""

    @staticmethod
    def calculate(dt_dx: float, dt_dy: float, coriolis_f: float, mean_temperature_k: float) -> tuple[float, float]:
        """
        Component form of d(Vg)/d(ln p) = -(Rd/f) * (k x grad(T)):

            d(ug)/d(ln p) =  (Rd/f) * dT/dy
            d(vg)/d(ln p) = -(Rd/f) * dT/dx

        Parameters
        ----------
        dt_dx, dt_dy : float
            Horizontal temperature gradient components (K/m).
        coriolis_f : float
            Coriolis parameter (s^-1), non-zero.
        mean_temperature_k : float
            Mean layer temperature (K) — kept as an explicit parameter
            for callers who want to convert the per-ln(p) shear into a
            per-height shear via the hypsometric relation; not used in
            this formula directly (Rd is temperature-independent) but
            required by convention in most textbook presentations
            of this equation for the accompanying thickness step.

        Returns
        -------
        tuple of float
            (d(ug)/d(ln p), d(vg)/d(ln p)) — thermal wind shear
            components (m/s per unit ln(p), i.e. per Δ(ln p)=1).

        Raises
        ------
        ValueError
            If coriolis_f is zero or mean_temperature_k is non-positive.

        Reference
        ---------
        Holton & Hakim (2012), Ch. 3.
        """
        if coriolis_f == 0:
            raise ValueError("coriolis_f must not be zero.")
        if mean_temperature_k <= 0:
            raise ValueError("mean_temperature_k must be positive.")

        dug_dlnp = (RD / coriolis_f) * dt_dy
        dvg_dlnp = -(RD / coriolis_f) * dt_dx
        return dug_dlnp, dvg_dlnp


class ErtelPotentialVorticity:
    """Facade over PotentialVorticity (isobaric-coordinate Ertel PV)."""

    @staticmethod
    def calculate(relative_vorticity: float, coriolis_f: float, dtheta_dp: float) -> float:
        """
        PV = -g * (zeta + f) * dtheta/dp  (isobaric-coordinate form)

        This is the practical form used operationally (e.g. by ECMWF),
        mathematically equivalent to the general 3D dot-product form
        PV = (1/rho)*(eta . grad(theta)) under the hydrostatic
        approximation. See science/potential_vorticity.py for the
        underlying (already tested) implementation — not duplicated.

        Reference
        ---------
        Hoskins, B. J., McIntyre, M. E., & Robertson, A. W. (1985).
        "On the use and significance of isentropic potential vorticity
        maps". Q. J. R. Meteorol. Soc., 111(470), 877-946.
        """
        return PotentialVorticity.calculate(relative_vorticity, coriolis_f, dtheta_dp)
