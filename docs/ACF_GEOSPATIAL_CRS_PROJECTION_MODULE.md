# ACF — Module Systèmes de Coordonnées et Projections Cartographiques

**Statut :** intégré, additif, non destructif — livré par la mission
"INTÉGRATION DU MODULE « SYSTÈMES DE COORDONNÉES ET PROJECTIONS
CARTOGRAPHIQUES » DANS LE PROJET ACF".

**Package :** `src/acf/geospatial/`
**Lois scientifiques associées :** `src/acf/science/laws/geodesy.py`
(enregistrées dans `ScientificRegistry`, domaine
*"Géodésie & Projections Cartographiques"*).

---

## A. Architecture — fichiers ajoutés / modifiés

Le module est une **couche additive** au-dessus d'ACF existant :
`ACF EXISTANT + CRS / PROJECTION MANAGER`. Rien ailleurs dans ACF
n'importe ce package par défaut — il est donc intrinsèquement
"facilement désactivable" (mission §8) ; un flag explicite
`acf.geospatial.GEOSPATIAL_ENABLED` existe en plus pour les appelants
qui veulent un point de coupure unique.

### Fichiers créés (nouveaux, aucun fichier existant supprimé)

| Fichier | Rôle |
|---|---|
| `src/acf/geospatial/__init__.py` | Point d'entrée du package, flag `GEOSPATIAL_ENABLED`, logging standardisé `[ACF-CRS]` (mission §21) |
| `src/acf/geospatial/crs_manager.py` | Détection CRS (réutilise `ProjectionDetector` existant), validation 10 points (mission §12) |
| `src/acf/geospatial/projections.py` | `PROJECTION_CONFIG`, zones UTM, détection Nord-Algérie, `DECISION_MATRIX`, `recommend_projection()`, catalogue de 23 projections |
| `src/acf/geospatial/reprojection.py` | Transformation réelle via pyproj, toujours sur copie (`reproject_points`, `reproject_dataset_copy`, `round_trip_error`) |
| `src/acf/geospatial/distortion.py` | Diagnostics de distorsion via pyproj/Geod (jamais un modèle de Tissot réimplémenté à la main) |
| `src/acf/geospatial/metadata.py` | `CRSMetadata` (14 champs, mission §13), `describe_crs()`, `build_crs_metadata()` |
| `src/acf/science/laws/geodesy.py` | Formules LCC 2SP / Albers / sélection de zone UTM, documentées et vérifiées numériquement contre pyproj |
| `tests/test_geospatial.py` | 34 tests couvrant les 7 scénarios requis (mission §20) + détection/validation/décision/non-mutation |
| `docs/ACF_GEOSPATIAL_CRS_PROJECTION_MODULE.md` | Ce document |

### Fichiers existants modifiés (additif uniquement)

| Fichier | Modification |
|---|---|
| `src/acf/science/registry.py` | +2 lignes : import de `GEODESY_LAWS` et concaténation dans `_ensure_initialized()`. Aucune loi existante retirée ni modifiée. Vérifié : 54 lois au total (51 + 3). |

Aucun fichier scientifique déjà validé n'a été modifié. Aucune
architecture existante n'a été réécrite. Le détecteur CRS existant
(`acf.data.engine.projection_detector.ProjectionDetector`) est
**réutilisé**, pas dupliqué. Les couches GUI de projection déjà
présentes (`gui/map/map_projection.py`, `gui/map/projections/
projection_manager.py`) restent un sujet séparé (rendu Cartopy pour
l'affichage) — ce nouveau module comble un manque réel côté couche
scientifique (CRS/EPSG/datum/reprojection sûre), qui n'existait pas
avant.

---

## B. Points d'entrée recommandés

```python
from acf.geospatial import crs_manager, projections, reprojection, distortion, metadata

crs_manager.detect_crs(dataset_or_metadata)          # détection
crs_manager.validate_crs(source, target, bounds)     # 10-point checklist
projections.recommend_projection(bounds, analysis_type, data_crs)
reprojection.reproject_dataset_copy(dataset, target_crs)   # copie, jamais en place
distortion.assess_distortion(crs, bounds)
metadata.build_crs_metadata(source, target)
```

---

## C. Documentation scientifique

### C.1 Distinction CRS / datum / ellipsoïde / méthode de projection / paramètres / unités

Le module distingue explicitement ces six notions, jamais confondues
dans le code ni dans les métadonnées produites (mission §4, §6-7,
§15) :

- **EPSG:4326** est identifié comme **"WGS 84 Geographic CRS"**,
  jamais comme une "projection" — `describe_crs("EPSG:4326")` renvoie
  `is_geographic=True`, `is_projected=False`, `projection_method=None`.
- **EPSG:9802** (Lambert Conformal Conic 2SP) et **EPSG:9822** (Albers
  Equal Area) sont des **méthodes de projection**, jamais des CRS
  complets — documenté explicitement dans `PROJECTION_CONFIG`,
  `PROJECTION_CATALOG`, et dans les `limitations` des lois
  `lambert_conformal_conic_2sp` / `albers_equal_area_conic` du
  registre scientifique. Un CRS complet utilisant l'une de ces
  méthodes doit en plus préciser le datum, l'ellipsoïde et les
  paramètres numériques (parallèles standards, méridien central,
  etc.).
- `CRSMetadata` (14 champs) sépare toujours `datum`, `ellipsoid`,
  `projection_method`, `units` et les paramètres numériques
  (`central_meridian`, `standard_parallel_1/2`, `scale_factor`,
  `false_easting/northing`) — jamais fusionnés dans un seul champ, et
  jamais fabriqués : un champ non rapporté par pyproj pour la CRS
  donnée reste `None` plutôt que `0.0`.

### C.2 Familles de projections (mission §16)

- **Conformes** (préservent les angles localement) : Mercator,
  Transverse Mercator, UTM, LCC 1SP/2SP, Stereographic, Polar
  Stereographic.
- **Équivalentes / équal-area** (préservent les surfaces) : Albers
  Equal Area, Lambert Azimuthal Equal Area, Mollweide, Sinusoidal,
  Eckert IV, Lambert Cylindrical Equal Area, Equal Earth.
- **Équidistantes** (préservent certaines distances) : Azimuthal
  Equidistant, Equidistant Conic, Cassini-Soldner.
- **De compromis** : Robinson, Winkel Tripel.

### C.3 Catalogue des projections (mission §17)

`projections.PROJECTION_CATALOG` documente **23 projections**
(Plate Carrée, Mercator, Web Mercator, Transverse Mercator, UTM,
Lambert Conformal Conic 1SP/2SP, Albers Equal Area, Lambert Azimuthal
Equal Area, Azimuthal Equidistant, Stereographic, Polar Stereographic,
Orthographic, Gnomonic, Robinson, Winkel Tripel, Mollweide,
Sinusoidal, Eckert IV, Bonne, Cassini-Soldner, Equidistant Conic,
Lambert Cylindrical Equal Area, Equal Earth), chacune avec : nom,
famille, géométrie, propriété préservée, paramètres principaux,
comportement de distorsion, usage typique, méthode EPSG, CRS courant,
pertinence pour ACF. Accessible via `projections.get_projection_catalog()`.

### C.4 Matrice de décision (mission §10)

| Usage | Projection recommandée |
|---|---|
| Stockage | EPSG:4326 |
| ERA5 (original) | EPSG:4326 |
| GPM (original) | CRS natif du produit |
| CAPE/CIN | LCC |
| Champs météorologiques | LCC |
| Cartes climatologiques régionales | LCC |
| IDW | UTM |
| Kriging | UTM |
| Distance | UTM |
| Buffer | UTM |
| Superficie | Albers Equal Area |
| Comparaison de superficies | Albers Equal Area |
| Cartographie mondiale | Projection adaptée (Robinson/Winkel Tripel/Equal Earth) |
| Cartographie web | EPSG:3857 (affichage uniquement) |

Implémentée exactement dans `projections.DECISION_MATRIX` et exposée
via `recommend_projection(bounds, analysis_type, data_crs, region)`,
qui retourne une `ProjectionRecommendation(recommended, crs, reason,
analysis_type, warnings)`.

### C.5 Logique spécifique au Nord de l'Algérie (mission §18)

`projections.NORTH_ALGERIA_BOUNDS = {30°N–38°N, -3°E–10°E}`.
`is_north_algeria(bounds)` détecte l'appartenance à cette zone.
`recommend_projection()` ne force **jamais** une seule projection
automatiquement : pour cette région, elle recommande LCC pour la
cartographie météorologique, UTM (avec vérification de compatibilité
de zone — zones 29N–32N, `ALGERIA_UTM_ZONES`) pour les calculs
métriques locaux, et Albers Equal Area pour les superficies.

### C.6 Checklist de validation à 10 points (mission §12)

Implémentée dans `crs_manager.validate_crs(source_crs, target_crs,
bounds)` : (1) CRS source défini, (2) CRS cible défini, (3) datum
identifié, (4) unités identifiées, (5) bbox valide, (6) latitude dans
[-90, 90], (7) longitude dans [-180, 180], (8) transformation
disponible (`pyproj.Transformer.from_crs`), (9) compatibilité de zone
UTM (via `projections.determine_utm_zone()`, séparé), (10) résolution
spatiale — propriété du jeu de données, documentée comme à la charge
de l'appelant plutôt que fabriquée. **Tout échec → `status: "FAILED"`
avec la liste des erreurs — jamais un `PASSED` partiel ou deviné.**

---

## D. Validation — tests exécutés et résultats

### D.1 Suite dédiée : `tests/test_geospatial.py`

```
$ .venv/bin/python -m pytest tests/test_geospatial.py -q
..................................                                       [100%]
34 passed in 0.85s
```

Couvre explicitement les **7 scénarios requis** (mission §20) :

| # | Scénario | Test(s) |
|---|---|---|
| 1 | EPSG:4326 → UTM | `test_reproject_points_wgs84_to_utm`, `test_recommend_projection_distance_over_algeria_gives_utm` |
| 2 | EPSG:4326 → LCC | `test_reproject_points_wgs84_to_lcc`, `test_recommend_projection_meteorological_fields_gives_lcc` |
| 3 | EPSG:4326 → Albers | `test_reproject_points_wgs84_to_albers`, `test_recommend_projection_area_gives_albers` |
| 4 | Réversibilité WGS84 → projeté → WGS84 (tolérance documentée) | `test_round_trip_reversibility` — tolérance : **< 1 mm** (erreur géodésique réelle via `pyproj.Geod`) |
| 5 | Distance en mètres, pas en degrés | `test_distance_in_projected_crs_is_metres_not_degrees` |
| 6 | Calcul de superficie via projection adaptée | `test_area_computation_uses_equal_area_projection_not_web_mercator` |
| 7 | Étendue multi-zones UTM non forcée sur une seule zone | `test_determine_utm_zone_multi_zone_is_not_silently_forced` |

Plus 27 tests additionnels : détection CRS (y compris le
piège pyproj `"latlon"` → IGS20, voir §E), non-invention de CRS
ambigu, distinction géographique/projeté, catalogue de projections,
non-mutation du `Dataset` original lors de la reprojection,
enregistrement des lois géodésiques dans `ScientificRegistry`.

### D.2 Suite complète ACF (non-régression)

```
$ .venv/bin/python -m pytest tests/ -q
2697 passed, 25 warnings in 10.00s
```

Aucun test existant cassé. Les avertissements sont préexistants
(dépréciation Matplotlib/Cartopy, avertissement Zarr) et sans rapport
avec ce module.

### D.3 Qualité de code

```
$ .venv/bin/ruff check src/acf/geospatial/ src/acf/science/laws/geodesy.py \
    src/acf/science/registry.py tests/test_geospatial.py
All checks passed!

$ .venv/bin/mypy src/acf/geospatial/ src/acf/science/laws/geodesy.py
Success: no issues found in 7 source files
```

### D.4 Vérification numérique des formules (Physics Guard)

Les formules LCC 2SP et Albers Equal Area de
`science/laws/geodesy.py` (implémentation Snyder 1987, §14/§15, à
but documentaire et pédagogique — jamais utilisées pour la
reprojection réelle, qui passe toujours par pyproj/PROJ) ont été
comparées numériquement à la transformation pyproj/PROJ réelle, pour
lat=35°, lon=5°, parallèles standards 32°/36°, origine 34°N/3°E,
ellipsoïde WGS84 :

```
LCC    : écart ≈ 1e-9 m
Albers : écart ≈ 1e-9 m
```

---

## E. Rapport — bug découvert et corrigé pendant l'intégration

**Piège CRS ambiguë (mission règle #13) :** `pyproj.CRS.from_user_input
("latlon")` ne renvoie pas d'erreur et ne résout pas non plus vers un
WGS84 générique — il résout silencieusement vers un référentiel
géodésique réel et non lié : **IGS20 (EPSG:10178)**. Le détecteur
existant `ProjectionDetector` renvoie justement `"latlon"` comme
étiquette générique de famille pour `grid_mapping_name=
"latitude_longitude"`. Sans interception, cela aurait produit un CRS
incorrect et invisible dans les résultats.

**Correctif appliqué** dans `crs_manager.detect_crs()` : les
étiquettes génériques de famille (`"lambert"`, `"mercator"`,
`"polar"`) ne sont **jamais** transmises à pyproj (statut
`"PARTIAL"`, aucune description) ; l'étiquette `"latlon"` est
explicitement traduite vers `"EPSG:4326"` (le CRS de stockage
standard pour les sources de données réelles d'ACF, convention CF)
avant d'être transmise à `describe_crs()`. Vérifié par test
(`test_detect_crs_family_label_is_not_silently_resolved_by_pyproj`).

**Bug additionnel corrigé pendant l'écriture des tests :**
`_ANALYSIS_TYPE_ALIASES["web_mapping"]` pointait vers la clé
`"webmercator"`, absente de `DECISION_MATRIX` (qui utilise la clé
`"web_mapping"`), provoquant un `KeyError` sur toute recommandation
de type cartographie web. Corrigé en alignant l'alias sur la clé
réelle de la matrice de décision ; `DECISION_MATRIX["web_mapping"]`
reste `"webmercator"` (la *valeur* recommandée). Couvert par
`test_recommend_projection_web_mapping_warns_against_scientific_use`.

---

## F. Confirmation de compatibilité

- ACF fonctionne toujours intégralement : **2697/2697** tests
  existants passent, sans modification de leur comportement.
- Aucun résultat scientifique déjà validé n'a été modifié — le seul
  changement à un fichier existant est l'ajout additif de 3 lois
  géodésiques au registre (`science/registry.py`), qui n'altère
  aucune des 51 lois précédentes (vérifié : `ScientificRegistry.
  count()` == 54 après intégration, 3 nouvelles clés listées, aucune
  clé retirée).
- Le nouveau module `acf.geospatial` est disponible mais **non
  appelé automatiquement** par aucun pipeline existant — il s'agit
  d'une couche additive prête à l'emploi (`GEOSPATIAL_ENABLED = True`
  comme point de coupure explicite pour les futurs appelants), pas
  d'une réécriture. Son câblage dans les modules d'analyse en aval
  (Spatial Variability, Gradient Analysis, Interpolation, Mapping,
  etc.) n'a pas été effectué à ce stade — conformément à la consigne
  de la mission de ne pas modifier l'architecture existante sans
  nécessité stricte — et reste une extension future à la demande.
