"""
Fronts and Air Masses
=======================

Air mass classification (Bergeron scheme) and frontal type/movement.

NOT implemented here (documented gap, not fabricated): the Thermal
Front Parameter (TFP, Hewson 1998) for automated front location from
gridded analyses — same gap already flagged in science/synoptic.py,
it needs a 2D-field gradient-of-gradient operator that doesn't exist
in ACF yet.

Reference:
    Bergeron, T. (1928). "Über die dreidimensional verknüpfende
    Wetteranalyse". Geofysiske Publikasjoner, 5(6).
    Ahrens, C. D. (2012). "Meteorology Today" (10th ed.) — standard
    textbook air mass source-region table, used here since Bergeron's
    original 1928 paper predates and is less accessible than the
    now-standard textbook presentation of the same 6-type scheme.
"""

import math
from typing import Literal

SurfaceType = Literal["continental", "maritime"]
LatitudeZone = Literal["arctic", "polar", "tropical", "equatorial"]

# The 6 standard Bergeron air mass types: (surface, latitude_zone) -> code.
# Note: there is no standard "continental equatorial" or "maritime arctic"
# type in the classical scheme (oceans don't get cold enough at the
# scale of an air mass source region, and the deep tropics/equator have
# no significant continental interior at very high latitude) — only 6
# of the 8 possible combinations are defined.
_AIR_MASS_TABLE: dict[tuple[SurfaceType, LatitudeZone], str] = {
    ("continental", "arctic"): "cA",
    ("continental", "polar"): "cP",
    ("maritime", "polar"): "mP",
    ("continental", "tropical"): "cT",
    ("maritime", "tropical"): "mT",
    ("maritime", "equatorial"): "mE",
}

_AIR_MASS_DESCRIPTIONS = {
    "cA": "Continental Arctic — très froid, très sec",
    "cP": "Continental Polaire — froid, sec",
    "mP": "Maritime Polaire — frais, humide",
    "cT": "Continental Tropical — chaud, sec",
    "mT": "Maritime Tropical — chaud, humide",
    "mE": "Maritime Équatorial — très chaud, très humide",
}


class AirMass:
    """Bergeron air mass classification by source region."""

    @staticmethod
    def classify_by_source_region(surface_type: SurfaceType, latitude_zone: LatitudeZone) -> str:
        """
        Classify an air mass by its source region characteristics —
        the textbook-correct basis for this scheme (air masses are
        DEFINED by where they form, not solely by an arbitrary later
        temperature/dewpoint reading after modification en route).

        Parameters
        ----------
        surface_type : {"continental", "maritime"}
        latitude_zone : {"arctic", "polar", "tropical", "equatorial"}

        Returns
        -------
        str
            One of "cA", "cP", "mP", "cT", "mT", "mE".

        Raises
        ------
        ValueError
            If the (surface_type, latitude_zone) combination is not
            one of the 6 standard types (e.g. "continental equatorial"
            is not a recognized source region in this scheme).
        """
        key = (surface_type, latitude_zone)
        if key not in _AIR_MASS_TABLE:
            raise ValueError(
                f"'{surface_type} {latitude_zone}' is not one of the 6 standard Bergeron air mass "
                f"source regions: {sorted(_AIR_MASS_TABLE.keys())}"
            )
        return _AIR_MASS_TABLE[key]

    @staticmethod
    def description(air_mass_code: str) -> str:
        """Human-readable description for a code (cA/cP/mP/cT/mT/mE)."""
        if air_mass_code not in _AIR_MASS_DESCRIPTIONS:
            raise ValueError(f"unknown air mass code: {air_mass_code!r}")
        return _AIR_MASS_DESCRIPTIONS[air_mass_code]


class FrontType:
    """Standard synoptic frontal types."""

    COLD = "cold"
    WARM = "warm"
    OCCLUDED_COLD_TYPE = "occluded_cold_type"
    OCCLUDED_WARM_TYPE = "occluded_warm_type"
    STATIONARY = "stationary"

    ALL = (COLD, WARM, OCCLUDED_COLD_TYPE, OCCLUDED_WARM_TYPE, STATIONARY)

    @staticmethod
    def classify_occlusion(
        temperature_behind_cold_front_c: float, temperature_ahead_of_warm_front_c: float
    ) -> str:
        """
        Classify an occluded front as cold-type or warm-type by
        comparing the air behind the overtaking cold front to the air
        ahead of the original warm front.

        Parameters
        ----------
        temperature_behind_cold_front_c : float
            Temperature of the air mass behind the overtaking cold
            front (degC).
        temperature_ahead_of_warm_front_c : float
            Temperature of the air mass ahead of the original warm
            front (degC).

        Returns
        -------
        str
            FrontType.OCCLUDED_COLD_TYPE if the overtaking air is
            colder than the air ahead of the warm front (most common
            case — the occlusion behaves like a cold front at the
            surface), else FrontType.OCCLUDED_WARM_TYPE.
        """
        if temperature_behind_cold_front_c < temperature_ahead_of_warm_front_c:
            return FrontType.OCCLUDED_COLD_TYPE
        return FrontType.OCCLUDED_WARM_TYPE


class FrontMovement:
    """Frontal movement kinematics."""

    @staticmethod
    def speed(wind_speed_m_s: float, wind_direction_deg: float, front_orientation_deg: float) -> float:
        """
        Front-normal speed: the component of the wind (behind the
        front, in the direction the front is moving) perpendicular to
        the front line — the standard estimate for how fast a front
        advances.

            C = wind_speed * cos(wind_direction - front_normal_direction)

        Parameters
        ----------
        wind_speed_m_s : float
            Wind speed (m/s) in the air mass pushing the front, >= 0.
        wind_direction_deg : float
            Wind direction in the standard METEOROLOGICAL convention
            (degrees) — the direction the wind is blowing FROM, e.g.
            270 = "westerly" = a wind blowing FROM the west (i.e. air
            actually moving toward the east). This is converted
            internally to the air's actual motion direction
            (wind_direction_deg + 180) before projecting onto the
            front normal.
        front_orientation_deg : float
            Orientation (azimuth) of the front line itself (degrees).
            The front-normal direction is front_orientation_deg + 90.

        Returns
        -------
        float
            Front movement speed (m/s). Positive means advancing in
            the front-normal direction as defined; sign convention is
            relative to the chosen normal, magnitude is what matters
            operationally.
        """
        if wind_speed_m_s < 0:
            raise ValueError("wind_speed_m_s must be non-negative.")

        motion_direction_deg = wind_direction_deg + 180.0
        front_normal_deg = front_orientation_deg + 90.0
        angle_diff = math.radians(motion_direction_deg - front_normal_deg)
        return wind_speed_m_s * math.cos(angle_diff)
