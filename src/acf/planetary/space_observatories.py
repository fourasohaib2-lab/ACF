"""
Atmospheric Complexity Framework (ACF)

Space Observatories Registry Module (Phase 9)
(ObservatoryRegistry cataloguing JWST, Hubble, Gaia, Euclid, Roman, Rubin, Pan-STARRS, NEOWISE, NEO Surveyor)
"""

from dataclasses import dataclass


@dataclass
class SpaceObservatory:
    """Description d'un observatoire astronomique spatial ou au sol."""

    name: str
    agency: str
    orbit_type: str  # Sun-Earth L2, LEO, Ground-based
    primary_sensors: list[str]
    spectral_coverage: str  # Optical, Infrared, UV, X-Ray
    planetary_applications: list[str]


OBSERVATORY_CATALOG: dict[str, SpaceObservatory] = {
    "jwst": SpaceObservatory(
        name="James Webb Space Telescope (JWST)",
        agency="NASA / ESA / CSA",
        orbit_type="Sun-Earth L2 Halo Orbit",
        primary_sensors=["NIRCam", "NIRSpec", "MIRI"],
        spectral_coverage="Near and Mid-Infrared (0.6 to 28.3 µm)",
        planetary_applications=["Exoplanet Transit Spectroscopy", "Outer Planets Atmospheres", "Comet Volatiles"],
    ),
    "neo_surveyor": SpaceObservatory(
        name="NEO Surveyor Space Telescope",
        agency="NASA PDCO / JPL",
        orbit_type="Sun-Earth L1 Halo Orbit",
        primary_sensors=["Dual-band Infrared Space Telescope"],
        spectral_coverage="Thermal Infrared (4.5 to 10 µm)",
        planetary_applications=["Near-Earth Object Discovery", "Potentially Hazardous Asteroids Characterization"],
    ),
    "rubin": SpaceObservatory(
        name="Vera C. Rubin Observatory (LSST)",
        agency="NSF / DOE",
        orbit_type="Ground-based (Cerro Pachón, Chile)",
        primary_sensors=["3.2 Gigapixel LSST Camera"],
        spectral_coverage="Optical (ugrizy filters)",
        planetary_applications=["Solar System Small-Bodies Survey", "Transient Events", "NEO Discovery"],
    ),
}


class ObservatoryRegistry:
    """Registre des grands observatoires astronomiques et spatiaux."""

    @classmethod
    def get_observatory(cls, key: str) -> SpaceObservatory | None:
        return OBSERVATORY_CATALOG.get(key.lower())

    @classmethod
    def list_observatories(cls) -> list[str]:
        return list(OBSERVATORY_CATALOG.keys())
