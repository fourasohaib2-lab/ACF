"""
WMO Official Code Tables Encyclopedia & Decoder Module (Table 4677 Present Weather, Table 0513 Clouds)
"""

# WMO Code Table 4677 - Present Weather WW
PRESENT_WEATHER_WMO_CODE_TABLE_4677: dict[int, str] = {
    0: "Atmosphere claire sans developpement convectif",
    1: "Nuages se dissipant progressivement",
    2: "Etat du ciel globalement inchange",
    3: "Nuages en formation ou en developpement",
    10: "Brumes seches ou humides (Haze / Mist)",
    17: "Foudre signalee sans tonnerre audible",
    18: "Rafales de vent de grain visibles",
    45: "Brouillard (Fog) continu sans changement",
    51: "Bruine faible continue (Drizzle)",
    61: "Pluie faible continue (Rain, light)",
    63: "Pluie moderee continue (Rain, moderate)",
    65: "Pluie forte continue (Rain, heavy)",
    71: "Neige faible continue (Snow, light)",
    73: "Neige moderee continue (Snow, moderate)",
    75: "Neige forte continue (Snow, heavy)",
    80: "Averse de pluie faible (Rain shower, light)",
    81: "Averse de pluie moderee ou forte (Rain shower, moderate/heavy)",
    89: "Averse de grele faible (Hail shower, light)",
    90: "Averse de grele forte (Hail shower, heavy)",
    95: "Orage faible ou modere avec pluie ou neige (Thunderstorm with rain/snow)",
    99: "Orage violent avec grele (Thunderstorm severe with hail)",
}

# WMO Code Table 0513 - Cloud Genera C
CLOUD_GENERA_WMO_CODE_TABLE_0513: dict[str, str] = {
    "Ci": "Cirrus (Nuage eleve filandreux)",
    "Cc": "Cirrocumulus (Nuage eleve moutonne)",
    "Cs": "Cirrostratus (Voile eleve produisant un halo)",
    "Ac": "Altocumulus (Nuage moyen en galets)",
    "As": "Altostratus (Nappe moyenne grisatre)",
    "Ns": "Nimbostratus (Nappe sombre a pluie/neige continue)",
    "Sc": "Stratocumulus (Banc sombre en galets/rouleaux)",
    "St": "Stratus (Couche bas uniforme)",
    "Cu": "Cumulus (Nuage bourgeonnant a base plate)",
    "Cb": "Cumulonimbus (Nuage d'orage a grand developpement vertical)",
}


def decode_wmo_present_weather(code: int) -> str:
    """Decode un code WMO 4677 de temps present."""
    return PRESENT_WEATHER_WMO_CODE_TABLE_4677.get(code, f"Code WMO 4677 inconnu ({code})")


def decode_metar_visibility(vis_code: str) -> float:
    """
    Decode la visibilite horizontale METAR en metres.
    Exemples: '9999' -> 10000m (>= 10 km, convention METAR standard),
    '0500' -> 500m, '10SM' -> 16093.4m.

    Raises
    ------
    ValueError
        Si le code ne correspond a aucun format METAR reconnu (numerique
        4 chiffres, ou distance en statute miles suffixee 'SM'). Un code
        illisible ne doit jamais etre silencieusement traduit en "10000m"
        (>= 10 km, c.a.d. bonne visibilite) - ce serait une valeur
        inventee et potentiellement dangereuse pour un usage aeronautique,
        pas une decodification honnete (NOTE correction : cette fonction
        renvoyait auparavant 10000.0 pour tout code non parseable,
        confondant "visibilite excellente confirmee" avec "code illisible").
    """
    vis_code = vis_code.strip().upper()
    if vis_code == "9999":
        return 10000.0
    if vis_code.endswith("SM"):
        try:
            miles = float(vis_code[:-2])
        except ValueError as exc:
            raise ValueError(f"Code de visibilite METAR illisible (format 'SM'): {vis_code!r}") from exc
        return miles * 1609.34
    try:
        return float(vis_code)
    except ValueError as exc:
        raise ValueError(f"Code de visibilite METAR non reconnu: {vis_code!r}") from exc
