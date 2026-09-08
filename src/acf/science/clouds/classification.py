"""
Atmospheric Complexity Framework (ACF)

Cloud Classification Engine
"""

from typing import Any


class CloudClassificationEngine:
    """
    Moteur de classification scientifique automatique des genres et espèces de nuages selon la nomenclature OMM (WMO International Cloud Atlas).

    Taxonomie complète (édition 2017, en vigueur — cloudatlas.wmo.int),
    vérifiée directement à la source (WebFetch) plutôt que reconstruite
    de mémoire :
      - 10 genres (GENRE_ABBREVIATIONS)
      - 15 espèces (SPECIES) — l'édition pré-2017 n'en comptait que 14 ;
        "volutus" a été ajoutée en 2017, ACF suit l'édition en vigueur.
      - 9 variétés (VARIETIES)
      - 11 particularités (SUPPLEMENTARY_FEATURES)
      - 4 nuages accessoires (ACCESSORY_CLOUDS) — l'édition pré-2017
        n'en comptait que 3 ; "flumen" a été ajoutée en 2017.

    Les tables de compatibilité genre<->espèce/variété/particularité
    ci-dessous encodent le meilleur effort d'ACF à partir de la
    nomenclature WMO standard ; en cas de doute sur un cas limite,
    l'atlas officiel (cloudatlas.wmo.int) fait foi.

    Reference:
        WMO (2017). International Cloud Atlas, Manual on the
        Observation of Clouds and Other Meteors (WMO-No. 407).
    """

    GENRES = {
        "High": ["Cirrus", "Cirrostratus", "Cirrocumulus"],
        "Middle": ["Altostratus", "Altocumulus"],
        "Low": ["Stratus", "Stratocumulus", "Nimbostratus"],
        "Convective": ["Cumulus", "Cumulus congestus", "Cumulonimbus"],
    }

    # Abréviations OMM standard des 10 genres.
    GENRE_ABBREVIATIONS = {
        "Cirrus": "Ci",
        "Cirrocumulus": "Cc",
        "Cirrostratus": "Cs",
        "Altocumulus": "Ac",
        "Altostratus": "As",
        "Nimbostratus": "Ns",
        "Stratocumulus": "Sc",
        "Stratus": "St",
        "Cumulus": "Cu",
        "Cumulonimbus": "Cb",
    }

    # 15 espèces (édition 2017) -> genres compatibles (abréviations).
    SPECIES = {
        "fibratus": ["Ci", "Cs"],
        "uncinus": ["Ci"],
        "spissatus": ["Ci"],
        "castellanus": ["Cc", "Ac", "Cs", "Sc"],
        "floccus": ["Cc", "Ac", "Cs"],
        "stratiformis": ["Cc", "Ac", "Sc"],
        "nebulosus": ["Cs", "St"],
        "lenticularis": ["Cc", "Ac", "Sc"],
        "volutus": ["Ac", "Sc"],
        "fractus": ["St", "Cu"],
        "humilis": ["Cu"],
        "mediocris": ["Cu"],
        "congestus": ["Cu"],
        "calvus": ["Cb"],
        "capillatus": ["Cb"],
    }

    # 9 variétés -> genres compatibles.
    VARIETIES = {
        "intortus": ["Ci"],
        "vertebratus": ["Ci"],
        "radiatus": ["Ci", "Ac", "As", "Sc", "Cu"],
        "duplicatus": ["Ci", "Cs", "Ac", "Sc", "As"],
        "undulatus": ["Cc", "Ac", "As", "Sc", "St"],
        "lacunosus": ["Cc", "Ac", "Sc"],
        "translucidus": ["Ac", "As", "Sc", "St"],
        "perlucidus": ["Ac", "Sc"],
        "opacus": ["Ac", "As", "Sc", "St"],
    }

    # 11 particularités -> genres compatibles.
    SUPPLEMENTARY_FEATURES = {
        "incus": ["Cb"],
        "mamma": ["Cb", "Ci", "Cc", "Ac", "As", "Sc"],
        "virga": ["Cc", "Ac", "As", "Ns", "Sc", "Cu", "Cb"],
        "praecipitatio": ["As", "Ns", "Sc", "St", "Cu", "Cb"],
        "arcus": ["Cb", "Cu"],
        "tuba": ["Cb", "Cu"],
        "asperitas": ["Ac", "Sc"],
        "fluctus": ["Ci", "Cc", "Ac", "Sc"],
        "cavum": ["Ac", "Cc"],
        "murus": ["Cb"],
        "cauda": ["Cb"],
    }

    # 4 nuages accessoires -> genres compatibles.
    ACCESSORY_CLOUDS = {
        "pileus": ["Cu", "Cb"],
        "velum": ["Cu", "Cb"],
        "pannus": ["As", "Ns", "Cu", "Cb"],
        "flumen": ["Cb"],
    }

    def classify(
        self,
        base_altitude_m: float,
        top_altitude_m: float,
        temperature_c: float,
        relative_humidity: float,
        radar_reflectivity_dbz: float = 0.0,
        cloud_optical_depth: float = 1.0,
        cape_j_kg: float = 0.0,
    ) -> dict[str, Any]:
        """
        Classifie automatiquement le nuage en fonction de ses propriétés physiques, de son altitude, de son optique et du radar.
        """
        thickness = top_altitude_m - base_altitude_m

        # Convective clouds
        if cape_j_kg > 1000 or radar_reflectivity_dbz > 40 or thickness > 6000:
            genre = "Cumulonimbus"
            family = "Convective"
            description = "Nuage convectif de grande extension verticale capable de produire de l'orage et des grêlons."
        elif cape_j_kg > 300 or thickness > 2500:
            genre = "Cumulus congestus"
            family = "Convective"
            description = "Nuage convectif bourgeonnant à fort développement vertical."
        elif thickness > 1000 and base_altitude_m < 2000 and relative_humidity > 0.8:
            if radar_reflectivity_dbz > 20:
                genre = "Nimbostratus"
                family = "Low"
                description = "Couche nuageuse sombre continue produisant de la pluie ou de la neige régulières."
            else:
                genre = "Stratocumulus"
                family = "Low"
                description = "Banc ou couche de galets ou rouleaux nuageux sombres."
        elif base_altitude_m < 2000:
            if thickness < 500:
                genre = "Stratus"
                family = "Low"
                description = "Couche nuageuse grise très basse et uniforme ressemblant à du brouillard élevé."
            else:
                genre = "Cumulus"
                family = "Convective"
                description = "Nuage séparé à contours net se développant sous forme de mamelons."
        elif 2000 <= base_altitude_m < 6000:
            if cloud_optical_depth > 10:
                genre = "Altostratus"
                family = "Middle"
                description = "Nappe nuageuse grisâtre striée couvrant le ciel et noyant le Soleil."
            else:
                genre = "Altocumulus"
                family = "Middle"
                description = "Banc de petits nuages blancs et gris en forme de galets ou de rouleaux."
        else:
            # High clouds (> 6000 m)
            if cloud_optical_depth < 1.0:
                genre = "Cirrus"
                family = "High"
                description = "Nuage élevé sous forme de filaments blancs et délicats constitués de cristaux de glace."
            elif cloud_optical_depth < 3.0:
                genre = "Cirrostratus"
                family = "High"
                description = (
                    "Voile nuageux transparent et blanchâtre produisant des phénomènes d'halo autour du Soleil."
                )
            else:
                genre = "Cirrocumulus"
                family = "High"
                description = "Banc de petits éléments nuageux blancs sans ombre propre."

        return {
            "genre": genre,
            "family": family,
            "base_altitude_m": base_altitude_m,
            "top_altitude_m": top_altitude_m,
            "thickness_m": thickness,
            "temperature_c": temperature_c,
            "optical_depth": cloud_optical_depth,
            "radar_dbz": radar_reflectivity_dbz,
            "description": description,
        }

    def compose(
        self,
        genre: str,
        species: str | None = None,
        varieties: list[str] | None = None,
        supplementary_features: list[str] | None = None,
        accessory_clouds: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Valide et compose un nom de nuage complet OMM :
        Genre [espèce] [variétés] [particularités] [nuages accessoires].

        Ne valide QUE la compatibilité genre<->élément (via les tables
        SPECIES/VARIETIES/SUPPLEMENTARY_FEATURES/ACCESSORY_CLOUDS) — ne
        vérifie pas l'incompatibilité mutuelle entre deux espèces (une
        seule espèce est physiquement possible à la fois, imposée par
        le type même de `species: str | None`) ni les règles fines
        d'exclusion entre variétés (ex : opacus et translucidus sont
        mutuellement exclusifs mais tous deux compatibles avec Ac —
        cette règle n'est pas encore encodée ici).

        Parameters
        ----------
        genre : str
            Nom complet du genre (ex: "Cumulonimbus") ou abréviation
            (ex: "Cb").
        species : str, optional
            Une espèce (au plus une, par définition du genre nuageux).
        varieties : list[str], optional
            Une ou plusieurs variétés.
        supplementary_features : list[str], optional
            Une ou plusieurs particularités.
        accessory_clouds : list[str], optional
            Un ou plusieurs nuages accessoires.

        Returns
        -------
        dict
            {
                "valid": bool,
                "name": str,                # nom composé si valide
                "abbreviation": str,        # ex: "Cb cal mam"
                "errors": list[str],        # incompatibilités détectées
            }
        """
        abbr = self.GENRE_ABBREVIATIONS.get(genre, genre)
        errors: list[str] = []

        def _check(table: dict[str, list[str]], items: list[str], label: str) -> None:
            for item in items:
                key = item.lower()
                if key not in table:
                    errors.append(f"{label} inconnu(e) dans la nomenclature OMM : '{item}'")
                elif abbr not in table[key]:
                    errors.append(f"{label} '{item}' incompatible avec le genre '{genre}' ({abbr})")

        if abbr not in self.GENRE_ABBREVIATIONS.values():
            errors.append(f"genre inconnu dans la nomenclature OMM : '{genre}'")

        if species:
            _check(self.SPECIES, [species], "espèce")
        _check(self.VARIETIES, varieties or [], "variété")
        _check(self.SUPPLEMENTARY_FEATURES, supplementary_features or [], "particularité")
        _check(self.ACCESSORY_CLOUDS, accessory_clouds or [], "nuage accessoire")

        name_parts = [genre]
        if species:
            name_parts.append(species)
        name_parts.extend(varieties or [])
        name_parts.extend(supplementary_features or [])
        if accessory_clouds:
            name_parts.append(f"({' '.join(accessory_clouds)})")

        abbrev_parts = [abbr]
        if species:
            abbrev_parts.append(species[:3])
        abbrev_parts.extend(v[:3] for v in (varieties or []))
        abbrev_parts.extend(f[:3] for f in (supplementary_features or []))

        return {
            "valid": len(errors) == 0,
            "name": " ".join(name_parts),
            "abbreviation": " ".join(abbrev_parts),
            "errors": errors,
        }
