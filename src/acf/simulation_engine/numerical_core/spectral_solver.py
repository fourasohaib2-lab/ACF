"""Spherical spectral solver for planetary circulation and Rossby wave dynamics."""

import numpy as np
from acf.simulation_engine.numerical_core.earth_grid import EarthGrid, EARTH_RADIUS


class SpectralSolver:
    """Pseudo-spectral solver for large-scale planetary atmospheric circulation.

    Computes spherical harmonics / 2D Fourier transforms to model Rossby waves,
    vorticity transport, and streamfunction-velocity potential inversions.
    """

    def __init__(self, grid: EarthGrid, truncation_degree: int = 42) -> None:
        self.grid = grid
        self.truncation_degree = truncation_degree

    def compute_vorticity(self, u: np.ndarray, v: np.ndarray) -> np.ndarray:
        """Compute relative vorticity zeta = dv/dx - du/dy + spherical metric terms.

        Args:
            u (np.ndarray): Zonal wind (m/s).
            v (np.ndarray): Meridional wind (m/s).

        Returns:
            np.ndarray: Vorticity array (1/s).
        """
        dx = self.grid.get_resolution_km() * 1000.0
        dy = dx

        dv_dx = np.gradient(v, axis=-1) / dx
        du_dy = np.gradient(u, axis=-2) / dy

        zeta = dv_dx - du_dy
        return zeta

    def solve_streamfunction(self, vorticity: np.ndarray) -> np.ndarray:
        """Invert Poisson equation nabla^2 (psi) = vorticity via spectral domain FFT.

        Args:
            vorticity (np.ndarray): Relative vorticity field (1/s).

        Returns:
            np.ndarray: Streamfunction field psi (m^2/s).
        """
        # Transform to spectral domain via 2D FFT
        vort_fft = np.fft.fft2(vorticity)
        ky = np.fft.fftfreq(vorticity.shape[0])[:, np.newaxis]
        kx = np.fft.fftfreq(vorticity.shape[1])[np.newaxis, :]

        k_sq = kx**2 + ky**2
        k_sq[0, 0] = 1.0  # Avoid division by zero at DC component

        # Solve Poisson eq: psi_fft = - vort_fft / (kx^2 + ky^2)
        psi_fft = -vort_fft / (k_sq + 1e-12)
        psi_fft[0, 0] = 0.0

        psi = np.real(np.fft.ifft2(psi_fft))
        return psi

    def rossby_dispersion(
        self, zonal_mean_u: float, wavenumber_k: float, wavenumber_l: float, latitude_deg: float = 45.0
    ) -> float:
        """Calculate Rossby wave phase speed c = U - beta / (k^2 + l^2).

        Args:
            zonal_mean_u (float): Background zonal wind speed (m/s).
            wavenumber_k (float): Zonal wavenumber (1/m).
            wavenumber_l (float): Meridional wavenumber (1/m).
            latitude_deg (float): Latitude in degrees.

        Returns:
            float: Phase speed c (m/s).
        """
        omega_earth = 7.2921159e-5  # rad/s
        lat_rad = np.radians(latitude_deg)
        beta = (2.0 * omega_earth * np.cos(lat_rad)) / EARTH_RADIUS

        k_total_sq = wavenumber_k**2 + wavenumber_l**2
        if k_total_sq <= 0.0:
            return zonal_mean_u

        c = zonal_mean_u - (beta / k_total_sq)
        return float(c)
