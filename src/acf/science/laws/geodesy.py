"""
Atmospheric Complexity Framework (ACF)

Geodesy & Map Projection Laws
==============================

Documents the map-projection formulas the geospatial/ package relies
on (via pyproj/PROJ for the actual numerical transform - these entries
are the scientific reference documentation, mission sections 6-7 and
16-17, not a second hand-rolled implementation).

IMPORTANT (mission section 6): EPSG:9802 and EPSG:9822 are PROJECTION
METHODS, not complete CRSs - the compute_func below implements the
method formula for documentation/verification purposes; a real CRS
additionally needs a datum, ellipsoid, and the specific parameter
values (standard parallels, central meridian, etc.) bound to it.
"""

import math

from acf.science.laws.base_law import AtmosphericLaw


def _lcc_2sp_forward(
    lat_deg: float,
    lon_deg: float,
    lat1_deg: float,
    lat2_deg: float,
    lat0_deg: float,
    lon0_deg: float,
    a: float = 6378137.0,
    e: float = 0.0818191908426,
) -> dict[str, float]:
    """
    Lambert Conformal Conic, 2 Standard Parallels (EPSG:9802).

    Reference: Snyder, J.P. (1987), "Map Projections - A Working
    Manual", USGS Professional Paper 1395, formulas 15-1 to 15-4.
    """

    def m(phi: float) -> float:
        return math.cos(phi) / math.sqrt(1 - e**2 * math.sin(phi) ** 2)

    def t(phi: float) -> float:
        return math.tan(math.pi / 4 - phi / 2) * (
            ((1 + e * math.sin(phi)) / (1 - e * math.sin(phi))) ** (e / 2)
        )

    phi, lam = math.radians(lat_deg), math.radians(lon_deg)
    phi1, phi2 = math.radians(lat1_deg), math.radians(lat2_deg)
    phi0, lam0 = math.radians(lat0_deg), math.radians(lon0_deg)

    m1, m2 = m(phi1), m(phi2)
    t1, t2, t0, t_phi = t(phi1), t(phi2), t(phi0), t(phi)

    n = math.log(m1 / m2) / math.log(t1 / t2)
    f = m1 / (n * t1**n)
    rho = a * f * t_phi**n
    rho0 = a * f * t0**n

    easting = rho * math.sin(n * (lam - lam0))
    northing = rho0 - rho * math.cos(n * (lam - lam0))
    return {"easting_m": easting, "northing_m": northing, "n": n}


def _albers_equal_area_forward(
    lat_deg: float,
    lon_deg: float,
    lat1_deg: float,
    lat2_deg: float,
    lat0_deg: float,
    lon0_deg: float,
    a: float = 6378137.0,
    e: float = 0.0818191908426,
) -> dict[str, float]:
    """
    Albers Equal Area Conic (EPSG:9822).

    Reference: Snyder, J.P. (1987), "Map Projections - A Working
    Manual", USGS Professional Paper 1395, formulas 14-1 to 14-4.
    """

    def m(phi: float) -> float:
        return math.cos(phi) / math.sqrt(1 - e**2 * math.sin(phi) ** 2)

    def q(phi: float) -> float:
        return (1 - e**2) * (
            math.sin(phi) / (1 - e**2 * math.sin(phi) ** 2)
            - (1 / (2 * e)) * math.log((1 - e * math.sin(phi)) / (1 + e * math.sin(phi)))
        )

    phi, lam = math.radians(lat_deg), math.radians(lon_deg)
    phi1, phi2 = math.radians(lat1_deg), math.radians(lat2_deg)
    phi0, lam0 = math.radians(lat0_deg), math.radians(lon0_deg)

    m1, m2 = m(phi1), m(phi2)
    q1, q2, q0, q_phi = q(phi1), q(phi2), q(phi0), q(phi)

    n = (m1**2 - m2**2) / (q2 - q1)
    c = m1**2 + n * q1
    rho = a * math.sqrt(c - n * q_phi) / n
    rho0 = a * math.sqrt(c - n * q0) / n

    easting = rho * math.sin(n * (lam - lam0))
    northing = rho0 - rho * math.cos(n * (lam - lam0))
    return {"easting_m": easting, "northing_m": northing, "n": n}


def _utm_zone_number(longitude_deg: float) -> int:
    """zone = int((longitude + 180) / 6) + 1 (mission section 5)."""
    return int((longitude_deg + 180.0) / 6.0) + 1


GEODESY_LAWS = [
    AtmosphericLaw(
        key="lambert_conformal_conic_2sp",
        name="Lambert Conformal Conic (2SP)",
        domain="Géodésie & Projections Cartographiques",
        equation="rho = a*F*t(phi)^n ; E = E0 + rho*sin[n(lambda-lambda0)] ; "
        "N = N0 + rho0 - rho*cos[n(lambda-lambda0)]",
        variables={
            "phi, lambda": "Latitude/longitude du point (rad)",
            "phi1, phi2": "Parallèles standards",
            "phi0, lambda0": "Origine de latitude / méridien central",
            "n, F, rho, rho0": "Paramètres du cône conforme (Snyder 1987)",
            "e": "Excentricité de l'ellipsoïde",
        },
        units={"E, N": "m", "phi, lambda": "rad"},
        description="Projection conforme conique à deux parallèles standards - préserve les "
        "angles localement. Recommandée par ACF pour la cartographie météorologique régionale "
        "(champs CAPE/CIN, cartes climatologiques) sur des domaines allongés est-ouest aux "
        "moyennes latitudes, notamment le Nord de l'Algérie.",
        references=[
            "Snyder, J.P. (1987) Map Projections - A Working Manual, USGS PP 1395, §15",
            "EPSG Geodetic Parameter Dataset - Coordinate Operation Method 9802 "
            "(method, not a complete CRS - mission section 6)",
        ],
        limitations=[
            "EPSG:9802 identifie la MÉTHODE de projection ; le CRS complet doit en outre "
            "spécifier le datum, l'ellipsoïde et les paramètres numériques (parallèles, "
            "méridien central).",
            "Distorsion croissante loin des deux parallèles standards.",
        ],
        compute_func=_lcc_2sp_forward,
    ),
    AtmosphericLaw(
        key="albers_equal_area_conic",
        name="Albers Equal Area Conic",
        domain="Géodésie & Projections Cartographiques",
        equation="rho = a*sqrt(C - n*q(phi))/n ; E = E0 + rho*sin[n(lambda-lambda0)] ; "
        "N = N0 + rho0 - rho*cos[n(lambda-lambda0)]",
        variables={
            "phi, lambda": "Latitude/longitude du point (rad)",
            "phi1, phi2": "Parallèles standards",
            "q(phi)": "Fonction de latitude authalique (Snyder 1987, eq. 3-12)",
            "n, C, rho, rho0": "Paramètres du cône équivalent (Snyder 1987)",
        },
        units={"E, N": "m", "phi, lambda": "rad"},
        description="Projection équivalente (conserve les superficies) - recommandée par ACF "
        "pour tout calcul ou comparaison de superficies (couverture nuageuse, zones de risque, "
        "bassins versants).",
        references=[
            "Snyder, J.P. (1987) Map Projections - A Working Manual, USGS PP 1395, §14",
            "EPSG Geodetic Parameter Dataset - Coordinate Operation Method 9822 "
            "(method, not a complete CRS - mission section 7)",
        ],
        limitations=[
            "EPSG:9822 identifie la MÉTHODE de projection, pas un CRS complet.",
            "Distorsion angulaire croissante loin des deux parallèles standards.",
        ],
        compute_func=_albers_equal_area_forward,
    ),
    AtmosphericLaw(
        key="utm_zone_selection",
        name="Sélection de zone UTM (Universal Transverse Mercator)",
        domain="Géodésie & Projections Cartographiques",
        equation="zone = int((longitude + 180) / 6) + 1",
        variables={
            "longitude": "Longitude du point (degrés, -180 a 180)",
            "zone": "Numéro de zone UTM (1-60)",
        },
        units={"longitude": "degree", "zone": "dimensionless"},
        description="Chaque zone UTM couvre 6 degrés de longitude, avec un facteur d'échelle "
        "au méridien central k0=0.9996 (WGS84/UTM, Transverse Mercator méthode EPSG:9807). "
        "L'Algérie du Nord est couverte par les zones 29N a 32N (EPSG:32629-32632).",
        references=[
            "Snyder, J.P. (1987) Map Projections - A Working Manual, USGS PP 1395, §8",
            "EPSG Geodetic Parameter Dataset - Coordinate Operation Method 9807 (Transverse Mercator)",
        ],
        limitations=[
            "Ne sélectionne qu'une seule zone : une étendue traversant plusieurs zones doit "
            "utiliser une projection régionale (LCC) plutôt qu'une zone UTM unique arbitraire.",
        ],
        compute_func=_utm_zone_number,
    ),
]
