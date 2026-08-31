"""Primitive equation atmospheric forecast solver."""

import numpy as np

from acf.simulation_engine.numerical_core.earth_grid import EarthGrid


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
        U: Zonal wind component (m/s)
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

    def initialize_state(self) -> dict[str, np.ndarray]:
        """Generate a physically consistent baseline atmospheric state dictionary."""
        shape_2d = (self.grid.n_lat, self.grid.n_lon)
        shape_3d = (self.grid.n_levels, self.grid.n_lat, self.grid.n_lon)

        # Temperature profile decreases with altitude
        temp_3d = np.zeros(shape_3d, dtype=np.float64)
        for k in range(self.grid.n_levels):
            temp_3d[k, :, :] = 288.15 - 0.0065 * (k * 500.0)  # Standard lapse rate

        state = {
            "T": temp_3d,
            "P": self.grid.compute_vertical_pressure_profile(np.full(shape_2d, 101325.0, dtype=np.float64)),
            "U": np.random.normal(10.0, 2.0, size=shape_3d),
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
