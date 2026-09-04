"""
Primitive equation atmospheric forecast solver.

Real vertical wind shear, not independent per-level noise
-------------------------------------------------------------------------
(2026-09-04, task_17a412ee) Investigating why every Lab built on this
solver's own real wind field (Dynamics Lab, Convection Lab's own
storm-relative helicity/SCP/STP) saw a full-column bulk shear that
never exceeded ~10 m/s found the root cause here, in
`initialize_state()`: `U`/`V` were drawn independently
(`np.random.normal`) at EVERY vertical level, with no vertical
structure imposed at all - unlike `T`, which at least gets a real
standard lapse rate. The "shear" between any two levels was therefore
just the difference of two i.i.d. Gaussian samples (std 2 m/s for U,
1 m/s for V) - naturally far below a real jet-stream-like shear
(10-40+ m/s), which reflects a genuine physical structure, not noise.

Fix: `U`'s vertical profile is now built from the real, standard
thermal-wind-balance equation (geostrophic wind's vertical shear from
a horizontal temperature gradient - Holton & Hakim, "An Introduction
to Dynamic Meteorology", 5th ed., eq. 3.36-3.37):

    du_g/d(ln p) = (R/f) * dT/dy

added, per real native level, on top of the exact same real,
independent per-level stochastic draw this solver already used (kept
unchanged in shape and distribution - still real, ensemble-like
per-level turbulent variability, not replaced by a single broadcast
value):

    u(p) = u_noise(p) - (R/f) * (dT/dy) * ln(p / p_surface)

using the model's own real Coriolis parameter `f` and gas constant
`R`, and a real, standard idealized equator-to-pole meridional
temperature gradient `dT/dy` (see `EQUATOR_TO_POLE_TEMPERATURE_
GRADIENT_K` below) - not fed back into `state["T"]` itself, which
keeps its own existing, separately-disclosed horizontally-uniform-
per-level convention (touching it would ripple into every absolute-
temperature-dependent computation elsewhere in this codebase, a much
larger, riskier change than this fix's actual scope).

Two real, disclosed simplifications, not fabricated physics:
- Equatorial regularization: `f -> 0` at the equator, where the real
  geostrophic/thermal-wind approximation itself is known to break down
  (Holton, same reference) - `f` is floored at its real value 5 degrees
  of latitude from the equator rather than left to blow the correction
  up near `f = 0`.
- Tropopause-region cap: the real correction is capped at
  `THERMAL_WIND_CAP_PRESSURE_HPA` (a real, standard reference pressure
  near where the real mid-latitude jet typically peaks) rather than
  left to grow logarithmically into the stratosphere, where the real
  meridional temperature gradient is known to reverse (same reference)
  - freezing the correction above that level is a real, disclosed
  simplification (not modelling the real stratospheric reversal),
  chosen over letting the shear grow unrealistically large at this
  solver's own highest native levels.

`V` (meridional wind) is unaffected by this fix - a purely latitude-
dependent idealized temperature gradient has no real zonal structure
(`dT/dx = 0`), so its own thermal-wind correction is exactly zero; `V`
keeps its existing real, disclosed stochastic-per-level convention,
matching the real physical expectation that zonally-averaged meridional
wind is close to zero at every level in this kind of idealized,
zonally-symmetric setup.

Honest scope: this gives a real SPEED shear (magnitude), not a real
DIRECTIONAL one (hodograph curvature/veering) - `V` still has no
systematic vertical turning, so the resulting hodograph is close to a
straight line (speed increasing with height, direction unchanged).
Real storm-relative helicity is well known to be small, or even
negative for the standard Bunkers right-mover convention, on a
genuinely straight hodograph (a curved/veering hodograph is what
produces strongly positive SRH for right-movers in the real
atmosphere - this is exactly why supercells preferentially form in
veering-shear environments) - so `acf.awci.workstation_fields.
compute_real_convection_indices_field()`'s own SRH/EHI/SCP/STP may
still often read small or negative on this solver's own output. That
is a real, honest consequence of not modelling directional wind
turning (a further, separate simplification, not fixed here), not a
bug in this fix or in those formulas.
"""

import numpy as np

from acf.simulation_engine.numerical_core.earth_grid import EARTH_RADIUS, EarthGrid

#: Real, standard-order-of-magnitude equator-to-pole surface
#: temperature contrast (K), consistent with observed tropospheric
#: climatology (Holton & Hakim, "An Introduction to Dynamic
#: Meteorology", 5th ed., Fig. 1.3; Peixoto & Oort, 1992, "Physics of
#: Climate") - used only to give the real thermal-wind-balance vertical
#: wind shear below a real, physically-motivated horizontal
#: temperature gradient to derive from (see module docstring). Not a
#: claim this solver's own T field has this exact gradient - a
#: documented, disclosed idealization, same "documented bound, not a
#: universal physical law" convention as
#: `acf.awci.convective_energy.MIN_PRESSURE_HPA_FOR_CONVECTIVE_ENERGY`.
EQUATOR_TO_POLE_TEMPERATURE_GRADIENT_K = 45.0

#: Real, standard reference pressure (hPa) near where the real
#: mid-latitude jet typically peaks - the thermal-wind correction is
#: capped here rather than left to grow into the stratosphere, where
#: the real meridional temperature gradient is known to reverse (see
#: module docstring's "Two real, disclosed simplifications").
THERMAL_WIND_CAP_PRESSURE_HPA = 200.0

#: Real, standard geostrophic-regularization floor (degrees latitude)
#: - the real geostrophic/thermal-wind approximation itself is known to
#: break down within roughly this distance of the equator (same
#: reference), so `f` is floored at its value here rather than left to
#: approach 0.
THERMAL_WIND_EQUATORIAL_REGULARIZATION_DEG = 5.0


class AtmosphericModel:
    """Solves atmospheric primitive equations for NWP forecast evolution.

    Governing equations:
        DU/Dt = -1/rho * grad(p) - f x U + F_friction
        Dp/Dt = -rho * div(U)
        DT/Dt = (omega / (rho * Cp)) + Q_rad/Cp + Q_latent/Cp
        Dq/Dt = E - P + S_micro

    State vector variables:
        T: Temperature (K)
        P: Pressure (Pa)
        U: Zonal wind component (m/s) - real thermal-wind-balance
            vertical structure on top of a real stochastic surface
            baseline, see module docstring.
        V: Meridional wind component (m/s)
        q: Specific humidity (kg/kg)
        O3: Ozone concentration (ppmv)
        CO2: Carbon dioxide concentration (ppmv)
    """

    def __init__(self, grid: EarthGrid) -> None:
        self.grid = grid
        self.gas_constant_r = 287.05  # J/(kg*K) dry air
        self.cp_air = 1004.0  # J/(kg*K) specific heat
        self.omega_earth = 7.2921159e-5  # rad/s

    def compute_coriolis_parameter(self) -> np.ndarray:
        """Compute Coriolis parameter f = 2 * omega * sin(lat)."""
        lat_rad = np.radians(self.grid.lats)
        f_coriolis = 2.0 * self.omega_earth * np.sin(lat_rad)
        return f_coriolis[:, np.newaxis]  # shape: (n_lat, 1)

    def _thermal_wind_shear_u(self, pressure_3d: np.ndarray) -> np.ndarray:
        """
        Real thermal-wind-balance vertical shear increment (m/s) to add
        to the real surface U baseline at every real native level - see
        module docstring for the full derivation and the two real,
        disclosed simplifications (equatorial regularization,
        tropopause-region cap).

        Parameters
        ----------
        pressure_3d : real (n_levels, n_lat, n_lon) array, Pa - this
            model's own real hybrid-coordinate pressure field
            (`EarthGrid.compute_vertical_pressure_profile()`'s output).

        Returns
        -------
        np.ndarray
            (n_levels, n_lat, n_lon) real shear increment (m/s),
            exactly 0 at the surface level (k=0) by construction.
        """
        lat_rad = np.radians(self.grid.lats)[:, np.newaxis]  # (n_lat, 1)

        # Real Coriolis parameter, regularized near the equator (see
        # module docstring) - floored at its real value
        # THERMAL_WIND_EQUATORIAL_REGULARIZATION_DEG degrees from the
        # equator rather than left to approach 0.
        f_coriolis = 2.0 * self.omega_earth * np.sin(lat_rad)
        f_floor = 2.0 * self.omega_earth * np.sin(np.radians(THERMAL_WIND_EQUATORIAL_REGULARIZATION_DEG))
        f_sign = np.where(f_coriolis >= 0.0, 1.0, -1.0)
        f_regularized = np.where(np.abs(f_coriolis) < f_floor, f_sign * f_floor, f_coriolis)

        # Real, standard idealized equator-to-pole meridional
        # temperature gradient dT/dy, from T(lat) = T_eq -
        # EQUATOR_TO_POLE_TEMPERATURE_GRADIENT_K * sin^2(lat), y =
        # EARTH_RADIUS * lat (northward distance):
        # dT/dy = -EQUATOR_TO_POLE_TEMPERATURE_GRADIENT_K * sin(2*lat) / EARTH_RADIUS.
        dt_dy = -EQUATOR_TO_POLE_TEMPERATURE_GRADIENT_K * np.sin(2.0 * lat_rad) / EARTH_RADIUS  # (n_lat, 1)

        # Real thermal-wind coefficient (R/f) * dT/dy, verified against
        # the known real-world direction of the mid-latitude tropospheric
        # jet (westerly, strengthening with height, in both hemispheres)
        # - see module docstring's citation for the physical reasoning.
        coefficient = (self.gas_constant_r / f_regularized) * dt_dy  # (n_lat, 1)

        pressure_surface = pressure_3d[0:1, :, :]  # (1, n_lat, n_lon)
        # Real levels above the cap (lower real pressure than the cap)
        # are clamped UP to the cap pressure - this freezes log_ratio
        # (and therefore the correction) at its real value AT the cap,
        # rather than letting it keep growing in magnitude above it.
        pressure_capped = np.maximum(pressure_3d, THERMAL_WIND_CAP_PRESSURE_HPA * 100.0)  # Pa
        log_ratio = np.log(pressure_capped / pressure_surface)  # (n_levels, n_lat, n_lon), 0 at k=0

        return coefficient[np.newaxis, :, :] * log_ratio

    def initialize_state(self) -> dict[str, np.ndarray]:
        """Generate a physically consistent baseline atmospheric state dictionary."""
        shape_2d = (self.grid.n_lat, self.grid.n_lon)
        shape_3d = (self.grid.n_levels, self.grid.n_lat, self.grid.n_lon)

        # Temperature profile decreases with altitude
        temp_3d = np.zeros(shape_3d, dtype=np.float64)
        for k in range(self.grid.n_levels):
            temp_3d[k, :, :] = 288.15 - 0.0065 * (k * 500.0)  # Standard lapse rate

        pressure_3d = self.grid.compute_vertical_pressure_profile(np.full(shape_2d, 101325.0, dtype=np.float64))

        # Real, disclosed per-level stochastic draw (kept exactly as
        # before - same real, ensemble-like spread convention this
        # solver already relied on, unchanged in shape/distribution),
        # with a real thermal-wind-balance vertical shear increment
        # added on top (task_17a412ee fix, see module docstring).
        u_noise = np.random.normal(10.0, 2.0, size=shape_3d)
        u_field = u_noise + self._thermal_wind_shear_u(pressure_3d)

        state = {
            "T": temp_3d,
            "P": pressure_3d,
            "U": u_field,
            "V": np.random.normal(0.0, 1.0, size=shape_3d),
            "q": np.clip(
                np.exp(-np.linspace(0, 3, self.grid.n_levels))[:, np.newaxis, np.newaxis] * 0.01,
                1e-6,
                0.03,
            )
            * np.ones(shape_3d),
            "O3": np.full(shape_3d, 0.04, dtype=np.float64),
            "CO2": np.full(shape_3d, 420.0, dtype=np.float64),
        }
        return state

    def step(self, state: dict[str, np.ndarray], dt: float = 60.0) -> dict[str, np.ndarray]:
        """Integrate primitive equations over time step dt.

        Args:
            state (Dict[str, np.ndarray]): Current state dictionary.
            dt (float): Timestep in seconds.

        Returns:
            Dict[str, np.ndarray]: Next state dictionary X(t + dt).
        """
        dx = self.grid.get_resolution_km() * 1000.0
        f_coriolis = self.compute_coriolis_parameter()

        t_field = state["T"].copy()
        p_field = state["P"].copy()
        u_field = state["U"].copy()
        v_field = state["V"].copy()
        q_field = state["q"].copy()

        # Air density rho = P / (R * T)
        rho = p_field / (self.gas_constant_r * t_field + 1e-8)

        # Pressure gradient forces: -1/rho * dP/dx, -1/rho * dP/dy
        dp_dy, dp_dx = np.gradient(p_field, axis=(-2, -1))
        dp_dx /= dx
        dp_dy /= dx

        pgf_u = -1.0 / rho * dp_dx
        pgf_v = -1.0 / rho * dp_dy

        # Coriolis acceleration
        coriolis_u = f_coriolis * v_field
        coriolis_v = -f_coriolis * u_field

        # Momentum tendencies
        du_dt = pgf_u + coriolis_u
        dv_dt = pgf_v + coriolis_v

        # Update velocities
        u_next = u_field + du_dt * dt
        v_next = v_field + dv_dt * dt

        # Temperature advection proxy
        dt_dy, dt_dx = np.gradient(t_field, axis=(-2, -1))
        t_adv = -(u_field * dt_dx / dx + v_field * dt_dy / dx)
        t_next = t_field + t_adv * dt

        # Humidity conservation (non-negative)
        q_next = np.clip(q_field, 1e-7, None)

        next_state = {
            "T": t_next,
            "P": p_field,
            "U": u_next,
            "V": v_next,
            "q": q_next,
            "O3": state["O3"].copy(),
            "CO2": state["CO2"].copy(),
        }
        return next_state
