"""
ACF - Atmospheric Complexity Framework
Sprint 8.21 - Spectral Physics Module

Spectral representation of atmospheric processes:
- Fourier decomposition
- Wavenumber calculation
- Spectral energy density
- Filtering operations
"""

import math


class SpectralPhysics:
    """
    Spectral physics engine for atmospheric model 4D.
    """

    @staticmethod
    def wavelength_to_wavenumber(wavelength: float) -> float:
        """
        Convert wavelength to wavenumber.

        k = 2π / λ

        Parameters
        ----------
        wavelength : float
            Wavelength in meters.

        Returns
        -------
        float
            Wavenumber.
        """

        if wavelength <= 0:
            raise ValueError("Wavelength must be positive")

        return (2 * math.pi) / wavelength

    @staticmethod
    def wavenumber_to_wavelength(wavenumber: float) -> float:
        """
        Convert wavenumber to wavelength.

        λ = 2π / k
        """

        if wavenumber <= 0:
            raise ValueError("Wavenumber must be positive")

        return (2 * math.pi) / wavenumber

    @staticmethod
    def spectral_energy(amplitude: float) -> float:
        """
        Compute spectral energy.

        E = 1/2 A²
        """

        if amplitude < 0:
            raise ValueError("Amplitude cannot be negative")

        return 0.5 * amplitude**2

    @staticmethod
    def fourier_component(signal: float, frequency: float, phase: float = 0.0) -> float:
        """
        Simple Fourier harmonic component.

        X = A cos(2πft + φ)

        Here signal represents amplitude.
        """

        if frequency < 0:
            raise ValueError("Frequency cannot be negative")

        return signal * math.cos((2 * math.pi * frequency) + phase)

    @staticmethod
    def spectral_filter(spectrum: list[float], cutoff: float) -> list[float]:
        """
        Apply simple spectral cutoff filter.
        """

        if cutoff < 0:
            raise ValueError("Cutoff must be positive")

        return [value if abs(value) <= cutoff else 0.0 for value in spectrum]

    @staticmethod
    def dominant_wavenumber(spectrum: list[float]) -> int:
        """
        Find dominant spectral mode.
        """

        if not spectrum:
            raise ValueError("Spectrum cannot be empty")

        return max(range(len(spectrum)), key=lambda i: abs(spectrum[i]))
