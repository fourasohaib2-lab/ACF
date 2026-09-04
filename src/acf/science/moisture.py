"""
Moisture
========

Single-import facade over ACF's existing, individually-tested
atmospheric moisture modules — following the same pattern as
science/thermodynamics.py. No formulas are reimplemented here; this
module only aggregates and documents units/ranges for convenience.

Per ACF's single-source-of-truth rule, this is deliberately NOT a
second implementation of es/e/RH/r/q/Td — each already has exactly one
canonical file:
    saturation_vapor_pressure.py  (es, Bolton/Tetens form)
    vapor_pressure.py             (e, from specific humidity + pressure)
    relative_humidity.py          (RH = e/es)
    mixing_ratio.py               (w, from specific humidity)
    saturation_mixing_ratio.py    (ws, from es + pressure)
    specific_humidity.py          (q, from mixing ratio)
    dewpoint.py                   (Td, Magnus-Tetens form)

NOTE: frost point (point de givre, i.e. dewpoint w.r.t. ice rather
than liquid water, relevant below 0 degC) is NOT implemented — no
existing module covers it, and ACF does not fabricate an unverified
formula here. Flagged as a real gap, not silently skipped.
"""

from acf.science.dewpoint import DewPoint
from acf.science.mixing_ratio import MixingRatio
from acf.science.relative_humidity import RelativeHumidity
from acf.science.saturation_mixing_ratio import SaturationMixingRatio
from acf.science.saturation_vapor_pressure import SaturationVaporPressure
from acf.science.specific_humidity import SpecificHumidity
from acf.science.vapor_pressure import VaporPressure


class Moisture:
    """Aggregate facade for atmospheric moisture calculations."""

    @staticmethod
    def saturation_vapor_pressure(temperature: float, is_kelvin: bool = True) -> float:
        """Saturation vapor pressure es (hPa). See SaturationVaporPressure."""
        return SaturationVaporPressure.calculate(temperature, is_kelvin)

    @staticmethod
    def vapor_pressure(specific_humidity: float, pressure_hpa: float) -> float:
        """Actual vapor pressure e (hPa) from specific humidity. See VaporPressure."""
        return VaporPressure.calculate(specific_humidity, pressure_hpa)

    @staticmethod
    def relative_humidity(vapor_pressure_hpa: float, saturation_vapor_pressure_hpa: float) -> float:
        """Relative humidity RH in [0, 1] = e/es. See RelativeHumidity."""
        return RelativeHumidity.calculate(vapor_pressure_hpa, saturation_vapor_pressure_hpa)

    @staticmethod
    def mixing_ratio(specific_humidity: float) -> float:
        """Mixing ratio w (kg/kg) from specific humidity. See MixingRatio."""
        return MixingRatio.calculate(specific_humidity)

    @staticmethod
    def saturation_mixing_ratio(saturation_vapor_pressure_hpa: float, pressure_hpa: float) -> float:
        """Saturation mixing ratio ws (kg/kg). See SaturationMixingRatio."""
        return SaturationMixingRatio.calculate(saturation_vapor_pressure_hpa, pressure_hpa)

    @staticmethod
    def specific_humidity(mixing_ratio: float) -> float:
        """Specific humidity q (kg/kg) from mixing ratio. See SpecificHumidity."""
        return SpecificHumidity.calculate(mixing_ratio)

    @staticmethod
    def dewpoint(temperature_c: float, relative_humidity_percent: float) -> float:
        """Dewpoint Td (degC), Magnus-Tetens form. See DewPoint."""
        return DewPoint.calculate(temperature_c, relative_humidity_percent)

    @staticmethod
    def relative_humidity_from_temperature(
        specific_humidity: float, pressure_hpa: float, temperature_k: float
    ) -> float:
        """
        Convenience chain: RH (0-1) directly from specific humidity,
        pressure and temperature, composing vapor_pressure() +
        saturation_vapor_pressure() + relative_humidity().
        """
        e = Moisture.vapor_pressure(specific_humidity, pressure_hpa)
        es = Moisture.saturation_vapor_pressure(temperature_k, is_kelvin=True)
        return Moisture.relative_humidity(e, es)

    @staticmethod
    def specific_humidity_from_relative_humidity(
        relative_humidity_percent: float, pressure_hpa: float, temperature_k: float
    ) -> float:
        """
        Convenience chain: specific humidity q (kg/kg) from relative
        humidity, pressure and temperature - the real REVERSE of
        relative_humidity_from_temperature() above (added 2026-09-04,
        acf.awci.archive_field's own real need: RESTOR's real archived
        ALADIN output reports HUMI_RELAT (RH, %), not specific
        humidity directly, at its 7 real constant-pressure levels).

        Composes ONLY the already-existing, already-tested primitives
        below (RH -> e via es, then e -> w by REUSING
        SaturationMixingRatio's own w = 0.622*e/(p-e) formula with the
        real actual vapor pressure e rather than es - that formula is
        agnostic to which vapor pressure is passed in - then w -> q)
        - no new formula is implemented here, matching this module's
        own "single source of truth" rule.

        Parameters
        ----------
        relative_humidity_percent : float
            Relative humidity, 0-100 (not 0-1 - matches RESTOR's own
            real HUMI_RELAT field convention).
        pressure_hpa, temperature_k : float
            Real local pressure (hPa) and temperature (K) at the same
            point/level RH was measured/computed at.
        """
        es = Moisture.saturation_vapor_pressure(temperature_k, is_kelvin=True)
        e = (relative_humidity_percent / 100.0) * es
        w = Moisture.saturation_mixing_ratio(e, pressure_hpa)
        return Moisture.specific_humidity(w)
