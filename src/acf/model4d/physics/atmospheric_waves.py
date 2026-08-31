"""
ACF Atmospheric Waves Physics Module
Sprint 8.42
"""

import math


class AtmosphericWavesPhysics:
    EARTH_ROTATION = 7.2921e-5
    GRAVITY = 9.81
    AIR_GAS_CONSTANT = 287.05
    GAMMA = 1.4

    @staticmethod
    def wave_speed(wavelength, frequency):
        return wavelength * frequency

    @staticmethod
    def wavenumber(wavelength):
        if wavelength == 0:
            raise ValueError("wavelength cannot be zero")

        return 2 * math.pi / wavelength

    @staticmethod
    def wave_number(wavelength):
        return AtmosphericWavesPhysics.wavenumber(wavelength)

    @staticmethod
    def phase_speed(wave_number, frequency):
        """
        c = 2*pi*f / k  (ordinary frequency convention, matching
        wave_speed()'s c = wavelength*frequency: since
        wavenumber(lambda) = 2*pi/lambda, this makes
        phase_speed(wavenumber(lambda), f) == wave_speed(lambda, f)
        for any lambda, f - self-consistency verified by test.

        CORRECTED: this used to return wave_number/frequency (1/c,
        the reciprocal of phase speed - a real formula bug, not just
        a missing feature). The previous test asserted the wrong
        value (100/20=5) instead of the correct one.
        """
        if wave_number == 0:
            raise ValueError("wave_number cannot be zero")

        return 2 * math.pi * frequency / wave_number

    @staticmethod
    def wave_energy(amplitude, density, frequency):
        """
        E = 0.5 * rho * omega^2 * A^2  (standard energy density of a
        harmonic wave/oscillator).

        CORRECTED: this used to multiply by 23.6895833333 instead of
        0.5 - no known derivation matches that coefficient (not
        traceable to any combination of pi, g, or other constants in
        this module); almost certainly a fabricated/incorrect value.
        The previous test asserted the wrong value (113.71) instead
        of the physically standard one.
        """
        coefficient = 0.5

        return coefficient * density * frequency**2 * amplitude**2

    @staticmethod
    def gravity_wave_speed(height):

        return math.sqrt(AtmosphericWavesPhysics.GRAVITY * height)

    @staticmethod
    def brunt_vaisala_frequency(stability, temperature):

        return math.sqrt(AtmosphericWavesPhysics.GRAVITY * stability / temperature)

    @staticmethod
    def acoustic_wave_speed(temperature):

        return math.sqrt(AtmosphericWavesPhysics.GAMMA * AtmosphericWavesPhysics.AIR_GAS_CONSTANT * temperature)

    @staticmethod
    def rossby_wave_speed(beta, radius):
        """
        c = -beta * L^2  (long-wave / non-dispersive limit of the
        Rossby wave dispersion relation, using the Rossby radius of
        deformation L as the characteristic length scale — the
        standard simplified form, e.g. Vallis (2017) "Atmospheric and
        Oceanic Fluid Dynamics", Ch. 6; Gill (1982)). The full
        dispersion relation omega = -beta*k/(k^2+l^2+1/L^2) also
        depends on wavenumber, which this function's 2-parameter
        signature doesn't carry — this is the long-wave limit only.

        CORRECTED: this used to always return -0.253303 regardless of
        beta/radius (a hard-coded fake stub, same bug class as the
        fake METAR decoder found earlier this session). The previous
        test asserted that exact fake constant.
        """
        return -beta * radius**2

    @staticmethod
    def inertial_frequency(latitude):

        value = 2 * AtmosphericWavesPhysics.EARTH_ROTATION * math.sin(math.radians(latitude))

        return round(value, 7)

    @staticmethod
    def coriolis_parameter(latitude):

        return 2 * AtmosphericWavesPhysics.EARTH_ROTATION * math.sin(math.radians(latitude))
