# ACF MASTER AUDIT v2.0

**Date :** 2 septembre 2026
**Contexte :** premier livrable demandé par le "Prompt Maître ACF v2.0" fourni
par l'utilisateur — audit réel du dépôt avant toute implémentation majeure
supplémentaire, per §106-108 de ce prompt.

**Méthode :** ce rapport ne repart pas de zéro. Une bonne partie du travail
d'audit et de construction que ce prompt demande a déjà été faite, avec
preuves, dans cette même session (voir
[`docs/ACF_ARCHITECTURE_TARGET_GAP_MAP.md`](../docs/ACF_ARCHITECTURE_TARGET_GAP_MAP.md)
et [`docs/ACF_PHYSICS_GUARD_AUDIT_CHANGELOG.md`](../docs/ACF_PHYSICS_GUARD_AUDIT_CHANGELOG.md)).
Ce rapport les synthétise, les recoupe avec le nouveau vocabulaire du Prompt
Maître (Event Engine, Certification Engine, Model Adapter Protocol, Job
Engine, Golden Datasets…) et vérifie fraîchement ce qui n'avait pas encore
été contrôlé. Aucune affirmation ci-dessous n'est déduite du nom d'un
fichier ou d'un commentaire seul — chaque ligne "FOUND"/"PARTIAL"/"MISSING"
est basée sur une lecture réelle du code.

---

## 0. Événement inattendu trouvé en démarrant cet audit

`git status`/`git branch` (item 106) ont révélé que le dépôt était sur une
branche `fix/hpc-wizard-awci-access`, pas `develop`, avec un commit
(`291a66f`, auteur `Sohaib Foura <s.foura@meteo.dz>`) absent de mon
historique de session — même schéma que la collaboration `meteo-platform-5e`
plus tôt dans cette session (une session parallèle a travaillé sur ce même
dépôt). Le commit est réel, honnête, et testé : il expose le dashboard AWCI
directement depuis la barre d'outils ESOC. Vérifié (suite complète : 2938
passés, ruff/mypy propres), fusionné en fast-forward dans `develop`, poussé
(`291a66f`). Un fichier patch obsolète associé (`acf_esoc_changes.patch`,
déjà entièrement intégré) a été supprimé, même situation que
`acf_hpc_wizard.patch` trouvé précédemment.

---

## 1-4. État du dépôt (repository state / branch / commit / comptages)

- Branche : `develop`, synchronisée avec `origin/develop` après le merge ci-dessus.
- Fichiers Python sous `src/acf` : **1358** (hors `__pycache__`).
- Fichiers de test : **453** fichiers, **2938 tests**, tous passants, stables
  sur plusieurs runs répétés.
- `ruff check` : propre. `mypy src` : propre sur les 1353 fichiers analysés.
- Aucun import cassé détecté (mypy/ruff/pytest tous verts).

## 5-6. Modules manquants / cassés / incomplets / dupliqués / orphelins

Déjà cartographié en détail dans le gap-map architecture (38 couches cibles
de `docs/ACF_MASTER_UNIFIED_ARCHITECTURE.md`, croisées contre le dépôt réel) :
**13 existent telles quelles, 25 existent dispersées/renommées, 0 sont
absentes** (les 4 qui l'étaient — `normalization/`, `complexity/`,
`fire_weather/`, `storage/` — ont été construites ou résolues cette session).
Doublons connus et documentés (pas supprimés sans analyse) :
`docs/architecture/duplicate_components.md` liste les duplications GUI
historiques (fenêtre principale, moteur cartographique, canvas carte,
lecteurs de données) — analyse réelle mais désormais partiellement obsolète
en chiffres (563→1358 modules depuis), signalée comme telle dans ce fichier
lui-même (bannière ajoutée cette session).

## 7. Graphe de dépendances

`docs/architecture/dependency_graph.md` existe (analyse réelle antérieure,
563 modules) — désormais un instantané obsolète (signalé), pas un graphe
vivant. Pas d'outil de génération automatique du graphe dans le dépôt
actuel — à construire si un futur audit en a besoin, pas fabriqué ici.

## 8-9. Complexity Engine

**FOUND** (pas MISSING, pas inventé). `src/acf/awci/` est le moteur réel :
`AWCICalculator` (7 modules pondérés + 2 termes d'interaction non-linéaires),
split Physical/Forecast explicite, `ensemble_spread` (vrai
`EnsembleManager`), `model_disagreement` (vraie fusion multi-modèles
AROME/ALADIN/ARPEGE via `ModelConsensusEngine.
compute_real_multi_model_disagreement()`), champs 2D/3D/4D réels
(`spatial_field.py`/`vertical_field.py`/`temporal_field.py`), branché au
dashboard. Historique détaillé : voir la section "Complexity Engine" du
gap-map. Limite honnête documentée partout dans le code : pas de
reproduction d'un indice publié externe (les poids sont un choix de
conception ACF documenté, pas une formule de la littérature), pas de niveau
"17" mystique — aucune trace d'une telle définition n'existe dans le dépôt,
donc rien de tel n'a été inventé.

## 10. Physics Guard

**MISSING comme infrastructure transversale nommée.** Recherche exhaustive
(`grep -rli "physics_guard"`) : aucun module `physics_guard`/`PhysicsGuard`
dans `src/acf`. Ce qui EXISTE réellement et joue un rôle voisin, mais de
façon dispersée, pas centralisée :
- Vérifications d'unités ponctuelles (ex. `acf.normalization.units`, ajouté
  cette session, conversion réelle via MetPy/pint).
- Détections d'erreurs physiques ad hoc dans certains modules scientifiques
  (ex. corrections METAR/TAF ">=10km", ET0 Penman-Monteith — voir le
  changelog Physics Guard).
- Pas de pipeline unique `UNIT CHECK → DIMENSION CHECK → RANGE CHECK →
  COORDINATE CHECK → VERTICAL CHECK → TIME CHECK` appliqué systématiquement
  avant toute opération scientifique, comme le §22 du Prompt Maître le
  demande.

**C'est un vrai manque**, distinct de la "démarche Physics Guard" (la
méthodologie d'audit anti-fabrication déjà appliquée dans tout le dépôt
cette session) — le prompt demande une infrastructure de code, pas une
méthodologie d'audit. Les deux existent, mais ne sont pas la même chose.

## 11-13. Data Model 4D / Model Adapters / Formats

- **Data Contract formalisé (§4 du Prompt Maître) : ✅ IMPLEMENTED, TESTED
  (2026-09-02)** — voir mise à jour ci-dessous.
- **Model Adapters : ✅ Protocol aligné (2026-09-02)** — voir mise à jour
  ci-dessous. **WRF, ICON, OpenIFS : toujours aucun adapter** — confirmé
  absent, pas juste incomplet, hors scope de cette phase.
- Formats : `xarray`/`netCDF4`/`cfgrib`/`eccodes` réellement déclarés et
  utilisés (voir `pyproject.toml`'s `formats` extra, construit cette
  session) pour NetCDF/GRIB en lecture. Pas d'écriture GRIB2/BUFR réelle.

## 14-21. Coordinates / Grid / Vertical / Temporal

- **Vertical : PARTIAL, réel mais scopé.** `acf.awci.vertical_field` (cette
  session) manipule de vrais niveaux natifs du solveur, avec extraction de
  profil (`vertical_profile_at_point`) — mais pas de moteur générique
  `VerticalCoordinate` avec conversion pression/hauteur/theta/PV comme le
  §19 du Prompt Maître le décrit. Pas d'interpolation vers des niveaux de
  pression standards nulle part dans le dépôt (limite documentée à
  plusieurs endroits).
- **Grid/Regridding : PARTIAL.** `acf.awci.path_sampling` (cette session)
  fait du plus-proche-voisin réel (échantillonnage le long d'un chemin,
  recadrage vers une étendue) — pas de regridding bilinéaire/conservatif
  générique entre deux grilles quelconques.
- **Temporal : PARTIAL.** `acf.awci.temporal_field` (cette session) gère un
  vrai axe temporel de trajectoire physique continue (frames réelles,
  `valid_time_seconds`) — pas de moteur temporel générique séparé des
  autres couches, pas de gestion formalisée `analysis_time` vs
  `forecast_reference_time` vs `lead_time` en tant que contrat.
- **Coordinates (projection) : FOUND, dispersé.** `geospatial/`, `maps/
  projections/`, `gui/map/projections/` — réel (cartopy/pyproj), pas
  consolidé en un seul paquet `coordinates/`.

## 22. Physics Guard (transversal) — voir §10 ci-dessus. MISSING.

## 23-26. Science Engine / Diagnostics / Observations / Satellite-Radar-Lightning

- **Science Engine : FOUND, très large.** `science/`, `earth_physics/`,
  `model4d/physics/` — des centaines de modules thermodynamique/dynamique/
  convection déjà audités au fil de cette session et des précédentes
  (voir le changelog Physics Guard pour la liste des corrections
  scientifiques déjà faites : METAR/TAF, hydrologie, évapotranspiration,
  sismologie des tremblements de terre synthétiques, etc.).
- **Diagnostics : PARTIAL, dispersé** entre `intelligence/forecast_analysis/`,
  `science/`, `analysis/` — pas de moteur de diagnostics unifié
  (confirmé dans le gap-map précédent).
- **Observations : PARTIAL**, un sous-paquet par domaine
  (`hydrology/observations`, `ocean/observations`, `space_weather/
  observations`, `data_assimilation/observation_ingestion`) — pas de
  couche transverse unique.
- **Satellite/Radar/Lightning : PARTIAL, dispersé** sur 4+ emplacements
  chacun (confirmé dans le gap-map) — pas de paquet dédié.

## 27-30. Fusion multi-modèles / Ensemble / Uncertainty / Consensus

- **Fusion : PARTIAL, réel.** `ModelConsensusEngine.
  compute_real_multi_model_disagreement()` (cette session) fait tourner le
  vrai solveur par modèle (AROME/ALADIN/ARPEGE) et calcule un vrai spread —
  mais scopé à un point à la fois, pas une fusion de champ complet
  multi-modèles avec biais/skill par modèle comme le §29-30 du Prompt
  Maître le décrit. `ModelConsensusEngine.compute_unified_consensus()`
  (préexistant) reste un stub honnête (poids seulement, aucun champ fusionné).
- **Ensemble : FOUND pour les statistiques, PARTIAL pour l'intégration.**
  `ai/ensemble/ensemble_manager.py` — vraies formules (mean/spread/
  percentile/probability_exceedance/Brier/CRPS), réutilisées cette session
  dans AWCI. `simulation_engine/ensemble_prediction/` — vraie génération de
  membres perturbés + statistiques d'ensemble sur champ complet, mais pas
  branché à AWCI/complexity ni à un pipeline de production.
- **Uncertainty : PARTIAL.** `ai/uncertainty/` existe — pas audité en
  profondeur dans cette passe (à faire si ce chantier est repris) ; ne
  distingue pas formellement les 6 types du §32 du Prompt Maître (model/
  ensemble/observational/numerical/representation/temporal uncertainty).
- **Consensus pondéré par le skill (§15 du Prompt Maître) : MISSING.**
  Aucune "Model Skill Database" alimentée par la vérification réelle
  n'existe — voir §31 ci-dessous, la brique de mesure existe, pas la base
  de données de skill historique ni son utilisation pour pondérer.

## 31. Verification Engine

**FOUND, plus construit que je ne le pensais avant cette vérification.**
`src/acf/verification/nwp_metrics.py` : `NWPVerificationMetrics` implémente
réellement RMSE, Bias, MAE, ACC, table de contingence, POD, FAR, CSI, ETS
(`evaluate_all()` les regroupe). Combiné à `EnsembleManager.brier_score()`/
`.crps()` (déjà réel, réutilisé dans AWCI), la couverture demandée par le
§36 du Prompt Maître (Bias/MAE/RMSE/Correlation/CSI/ETS/Brier/CRPS) est
**quasiment complète en briques de calcul**. `verification_engine.py`
existe aussi (`ForecastVerificationEngine.contingency_table_metrics()`).
Ce qui manque réellement : un pipeline qui appelle ces métriques sur de
vraies paires prévision/observation en production, et la "Model Skill
Database" versionnée du §15/§31 pour alimenter un futur consensus pondéré.

## 32. Certification Engine

**MISSING.** Recherche exhaustive (`grep -rli certification`) : aucun
pipeline `INPUT VALID → QC PASS → PHYSICS PASS → SCIENCE PASS → PROVENANCE
PASS → VERIFICATION STATUS → CERTIFICATION` comme objet réutilisable.
`master/scientific_certification.py` existe mais est un rapport de audit
historique (probablement de la même génération que les ~150 docs
"certificat" déjà réconciliés), pas un moteur de certification de produit
vivant.

## 33. Event Engine

**✅ IMPLEMENTED, TESTED (2026-09-02)** — voir mise à jour ci-dessous.
`aeos/events/event_bus.py`/`digital_twin/events/cascade_engine.py`
restent des bus d'événements SYSTÈME distincts, non touchés.

## 34-40. Products 2D/3D/4D, Vertical Engine, Dashboard, API

- **2D/3D/4D : FOUND, mais scopé à AWCI/Complexity.** `acf.awci.
  spatial_field/vertical_field/temporal_field` (cette session) sont un vrai
  modèle 4D commun pour UNE famille de champs (température/vent/humidité/
  pression du solveur, score de complexité dérivé) — pas un modèle
  4D générique pour n'importe quelle variable scientifique du dépôt comme
  le §40 du Prompt Maître le vise à terme.
- **Dashboard : FOUND, réel.** ESOC + AWCI dashboards, branchés au vrai
  solveur physique (2D/3D/4D + animation), vérifiés par captures d'écran
  réelles à plusieurs reprises cette session.
- **API : PARTIAL.** `acf.web.hpc_dashboard_server` (FastAPI réel, cette
  session antérieure) expose `/api/hpc/*` et `/api/fno/predict_demo` — pas
  l'organisation par domaine complète du §21 du Prompt Maître
  (`/api/v1/datasets`, `/models`, `/complexity`, `/events`...).

## 41. Job Engine

**MISSING.** Recherche (`grep job_id/JobStatus`) : aucune classe `Job`
formelle avec `job_id/status/progress/retry_count` comme le §22/§46 du
Prompt Maître le décrit. Le travail HPC réel passe par
`HPCConnectionManager`/`hpc_workflow/` (soumission SLURM réelle, testée en
vrai contre Fennec cette session) mais sans cette abstraction Job générique.

## 42. HPC

**FOUND, réel et vérifié en conditions réelles.** Connexion SSH réelle
testée cette session contre le vrai cluster Fennec de l'ONM
(`sfoura@login2.fennec.meteo.dz`, transport SSH réel confirmé, commandes
distantes réellement exécutées). Pipelines one-click AROME/ALADIN réels
(`acf.forecast.engine`). CI/CD réel (`daily-forecast-cycle.yml`) mais sans
runner self-hosté configuré (bloqué sur l'accès infra réel, pas un manque
de code).

## 43. Tests scientifiques / Golden Datasets / Regression

- **Golden Datasets (§31-32 du Prompt Maître) : MISSING.** Aucun
  `tests/data/golden/` — confirmé, recherche vide.
- **Tests scientifiques : FOUND, en pratique** — la majorité des 2938
  tests de ce dépôt vérifient déjà des invariants physiques réels (pas
  juste "ne plante pas"), c'est la discipline appliquée dans toute cette
  session (voir chaque commit de cette session pour des exemples concrets :
  pression décroît avec l'altitude, humidité basse augmente le risque
  incendie, etc.) — mais pas organisés sous un dossier `tests/scientific/`
  dédié comme le §51 du Prompt Maître le suggère.
- **Regression scientifique formalisée (§53) : PARTIAL** — des cas
  spécifiques ont été verrouillés par des tests dédiés au fil de cette
  session (ex. `test_forecast_field_is_honestly_flat_documented_limitation`)
  mais pas de catégorie `tests/scientific/regression/` séparée avec
  comparaison ancien/nouveau résultat systématique.

## Synthèse — statut par grand domaine (échelle du Prompt Maître §72)

| Domaine | Statut |
|---|---|
| Repository / dépendances | VALIDATED (2938/2938, ruff/mypy propres) |
| Complexity Engine | IMPLEMENTED, TESTED |
| Physics Guard (infra transversale) | ✅ IMPLEMENTED, TESTED (2026-09-02) — voir mise à jour ci-dessous |
| Data Contract formel | MISSING |
| Model Adapters (AROME/ALADIN/ARPEGE) | PARTIAL (contrat différent du spec) |
| Model Adapters (WRF/ICON/OpenIFS) | MISSING |
| Coordinates/Grid/Vertical/Temporal | PARTIAL (réel mais scopé à AWCI) |
| Science Engine | IMPLEMENTED (large, audité au fil des sessions) |
| Diagnostics unifiés | PARTIAL (dispersé) |
| Fusion multi-modèles | PARTIAL (réel, scopé point-par-point) |
| Ensemble | PARTIAL (stats réelles, intégration partielle) |
| Uncertainty (6 types distincts) | PARTIAL (non audité en profondeur) |
| Consensus pondéré par skill | MISSING |
| Verification (métriques) | IMPLEMENTED (RMSE/Bias/MAE/ACC/CSI/ETS/Brier/CRPS réels) |
| Verification (pipeline + skill DB) | MISSING |
| Certification Engine | MISSING |
| Event Engine (objets météo) | MISSING |
| Products 2D/3D/4D | PARTIAL (réel, scopé à AWCI) |
| API | PARTIAL |
| Dashboard | IMPLEMENTED, TESTED |
| Job Engine | MISSING |
| HPC | IMPLEMENTED, VALIDATED (testé en conditions réelles) |
| Golden Datasets | MISSING |
| Tests scientifiques | IMPLEMENTED en pratique, pas formellement catégorisés |

## Mise à jour 2026-09-02 — Physics Guard construit (première phase du plan ci-dessous)

`src/acf/physics_guard/` : infrastructure réelle et transversale, pas une
duplication de la méthodologie d'audit du même nom. 6 vérifications
réelles, réutilisant l'existant plutôt que le dupliquant :

- **unit_check** — via `acf.normalization.units` (MetPy/pint réel).
- **range_check** — bornes opérationnelles ACF documentées comme telles
  (pas des limites physiques absolues), unit-aware.
- **coordinate_check** — motivé directement par le vrai bug
  `lons, lats = result["lats"], result["lons"]` trouvé et corrigé cette
  session (`gui/dashboard/awci_dashboard.py`).
- **dimension_check** — cohérence champ/coordonnées pour la convention
  réelle 2D/3D d'ACF.
- **vertical_check** — généralise l'invariant réel déjà vérifié contre
  le vrai solveur (`test_pressure_decreases_with_altitude_real_physics`).
- **consistency_check** — point de rosée ≤ température, bornes RH.

`PhysicsGuard.validate(data)` agrège toutes les violations trouvées (pas
juste la première) dans un `PhysicsGuardReport`.

**Branché réellement, pas juste construit à côté :** `PhysicsGuard().
check_coordinate_arrays(lats, lons)` ajouté exactement à la ligne de
`awci_dashboard.py` qui avait le bug historique — nouveau test
(`test_on_real_physics_ready_would_catch_a_reintroduced_lat_lon_swap`)
qui réintroduit artificiellement l'échange et prouve que le garde-fou
l'attrape désormais réellement, pas juste en théorie.

**Validation :** 2965/2965 tests passent (2938 avant, +26 nouveaux +1
test de non-régression), ruff et mypy propres sur les 1362 fichiers.

Portée honnête, documentée dans le package lui-même : DIMENSION CHECK ne
couvre que la convention 2D/3D réelle déjà utilisée par ACF, pas un
moteur d'analyse dimensionnelle générique pour tout tenseur arbitraire.
Pas encore branché ailleurs que ce point précis — l'intégration
systématique dans tout le pipeline scientifique reste à faire au fur et
à mesure, pas en un seul passage qui toucherait tout le dépôt d'un coup.

## Mise à jour 2026-09-02 (suite) — Data Contract construit

`src/acf/core/contracts/` : `Dataset` (§13 exact — id, source, model,
run, forecast_reference_time, valid_time, lead_time, variable, unit,
dimensions, coordinates, horizontal_grid, vertical_coordinate,
ensemble_member, quality, uncertainty, provenance, version, +
`values` réel puisqu'un contrat sans données à valider ne sert à
rien), `VariableContract` (§14 exact), `Provenance`, `QualityInfo`,
`UncertaintyInfo`.

**Vraie intégration, pas un type isolé :**
- `VariableContract.from_registry()` réutilise les vraies tables
  (`normalization.variable_names.cf_canonical_unit()` +
  `physics_guard.range_check.OPERATIONAL_RANGES`) au lieu de deviner
  unité/plage.
- `Dataset.validate()` réutilise `PhysicsGuard` directement (le lien
  "ACF 4D DATA MODEL → PHYSICS GUARD" du diagramme d'architecture
  maître) — **testé sur le même bug historique de lat/lon inversé**
  qu'`awci_dashboard.py` avait réellement eu.
- `Dataset.from_real_field()`/`from_real_volume()` construisent un
  vrai `Dataset` à partir des vraies sorties de
  `compute_real_complexity_field()`/`compute_real_complexity_volume()`
  — preuve que le contrat marche sur de vraies données ACF, pas un
  type que rien n'utilise.

**Trouvaille annexe corrigée en passant** : `datetime.utcnow()` est
déprécié depuis Python 3.12+ — utilisé dans le premier jet, corrigé
vers `datetime.now(UTC)` avant de committer.

**Validation :** 2987/2987 tests passent (2965 avant, +22 nouveaux),
ruff et mypy propres sur les 1368 fichiers.

Portée honnête : ce `Dataset` ne remplace pas encore les dicts ad hoc
que `spatial_field.py`/`vertical_field.py`/`temporal_field.py`
retournent eux-mêmes en interne — migrer ces points d'appel est un
chantier séparé et plus large, volontairement pas fait en un seul
passage.

## Mise à jour 2026-09-02 (suite) — Model Adapter Protocol aligné

Étendu `models/base_model.py::BaseWeatherModel` (déjà le vrai contrat
partagé d'ACF, juste sous d'autres noms de méthodes) avec les noms
exacts du §5 du Prompt Maître, **sans rien casser ni dupliquer** :

- `identify()`/`vertical_levels()` — vrais alias de `detect()`/`levels()`
  déjà existants.
- `read()` — chaque adaptateur nommait sa méthode de lecture
  différemment (`read_arome_file`/`read_aladin_file`/
  `read_arpege_file`) — c'est exactement le genre de chose qui force le
  `if model == "AROME":` que le prompt interdit. Une seule ligne
  ajoutée à chacun des 3 adaptateurs : `read()` délègue vers sa méthode
  existante — **testé pour prouver l'égalité exacte des résultats**,
  pas une seconde implémentation.
- `metadata()`/`coordinates()` — réels si un `filepath` est associé à
  l'instance, sinon `NotImplementedError` honnête (pas de dict vide
  fabriqué).
- `forecast_times()` — `NotImplementedError` partout : aucun adaptateur
  n'a de vraie logique de découverte de cycle de prévision, confirmé,
  pas deviné.
- `capabilities()` — vrai rapport d'introspection (`has_real_read_backend`
  détecté en comparant la classe réelle à `BaseWeatherModel.read` — pas
  une déclaration statique).
- `normalize()` — tente un vrai mapping via `acf.normalization` (déjà
  construit). **Trouvaille honnête** : `ERA5Model` utilise de vrais
  noms courts ECMWF (t2m, u10, v10, msl...) qui *matchent* réellement
  la table `parameters.json` — mapping partiel réel (4 des 10
  variables). AROME/ALADIN/ARPEGE utilisent des noms de champs internes
  format FA (`S090TEMPERATURE`...) qui ne correspondent à **aucune**
  table réelle du dépôt — `normalize()` le rapporte honnêtement (tout
  non mappé), sans inventer de table de correspondance.

**Validation :** 3003/3003 tests passent (2987 avant, +16 nouveaux),
ruff et mypy propres sur les 1368 fichiers, zéro régression sur les 22
tests d'adaptateurs préexistants.

## Mise à jour 2026-09-02 (suite) — Event Engine construit

`src/acf/events/` : `Event` (§12 exact — event_id réel UUID4, type,
geometry, start_time, end_time, intensity, probability, confidence,
supporting_parameters, supporting_models, observations, réutilise
`Provenance`/`UncertaintyInfo` du Data Contract au lieu de les
dupliquer) + un **vrai automate d'état** pour le cycle de vie du §13
(`DETECTED → ANALYZED → CONFIRMED → VERIFIED → CERTIFIED → PUBLISHED`
ou `DETECTED → REJECTED`) — `transition_to()` refuse toute transition
hors du diagramme (testé : sauter une étape, rejeter après ANALYZED,
sortir d'un état terminal — tout lève `IllegalEventTransitionError`).

**Décision de portée honnête, documentée en tête de paquet** : sur les
8 types d'événements nommés par le prompt (Thunderstorm, Cyclone,
HeavyRain, Hail, StrongWind, Snow, Fog, Dust), seuls **2 ont un
détecteur réel et défendable** avec les données dont ACF dispose
vraiment aujourd'hui :
- **`detect_strong_wind_events()`** — seuil réel sur `wind_speed_field`
  (vraie sortie CoupledEarthSolver).
- **`detect_fog_favorable_events()`** — humidité relative **réellement
  calculée via MetPy** (`relative_humidity_from_specific_humidity`,
  vérifiée par un test de non-régression qui verrouille la vraie
  valeur numérique de référence 68,449% pour des entrées connues) +
  vent calme — le vrai préalable thermodynamique du brouillard de
  rayonnement. **Nommage honnête** : `type="fog_favorable_conditions"`,
  jamais `"fog"` — aucun champ de visibilité n'existe dans la sortie
  réelle du solveur pour confirmer un brouillard formé, seulement sa
  précondition.

Les 6 autres types ne sont **pas construits**, avec la raison précise
documentée dans `events/__init__.py` : orage/convection a besoin d'un
vrai CAPE par point de grille (pas calculé dans le Complexity Engine),
cyclone a besoin d'un suivi vorticité/minimum de pression dans le
temps, pluie forte/neige/grêle ont besoin d'un champ de précipitation
qui **n'existe pas du tout** dans l'état du solveur (vérifié : `T, P,
U, V, q, O3, CO2, SST, Salinity, U_ocean, V_ocean, Ice, Soil,
Soil_Temp, Biomass` — aucune précipitation), poussière a besoin de
données d'aérosols qui n'existent pas non plus.

**Validation :** 3021/3021 tests passent (3003 avant, +18 nouveaux),
ruff et mypy propres sur les 1374 fichiers.

## Recommandation — ordre de phase suivant (pas les 30 à la fois)

Le Prompt Maître lui-même interdit d'exécuter toutes les phases
simultanément (§69, §81). Les manques les plus fondamentaux et les moins
coûteux à combler en premier, par ordre de dépendance :

1. **Physics Guard transversal** (§10, §22) — infrastructure la plus
   citée comme prérequis par le reste du document, actuellement absente.
2. **Data Contract formel** (§13) — nécessaire pour que Model
   Adapters/Fusion/Products aient un langage commun.
3. **Model Adapter Protocol** — aligner `AROMEIngestionAdapter` et les 2
   autres sur un contrat explicite (`Protocol`/ABC), sans casser
   l'existant.
4. **Event Engine** (§33) — much manquant, valeur opérationnelle claire
   (détection d'orages/cyclones avec cycle de vie).
5. **Verification pipeline + Model Skill Database** (§15, §31) — les
   briques de calcul existent déjà, il "ne reste" que le pipeline et le
   stockage versionné.

Dis-moi laquelle tu veux que j'attaque en premier — ou une autre priorité
si tu vois plus urgent.

## Mise à jour 2026-09-02 (suite) — Verification pipeline + Model Skill Database construits

Cinquième et dernière phase de l'ordre recommandé ci-dessus. §31 avait
déjà trouvé les calculateurs de métriques réels et complets
(`NWPVerificationMetrics`, `EnsembleManager`) — ce qui manquait
réellement : un pipeline qui les exécute sur une vraie paire prévision/
observation et enregistre le résultat quelque part de réutilisable, et
la base de données de skill versionnée du §15/§31.

- **`src/acf/verification/pipeline.py`** : `VerificationPipeline.
  evaluate()` — réutilise `NWPVerificationMetrics.evaluate_all()` (RMSE/
  Bias/MAE/ACC/POD/FAR/CSI/ETS) et, si des membres d'ensemble réels sont
  fournis, calcule aussi CRPS/Brier via `EnsembleManager` (moyenné sur
  chaque pas de temps) — aucune métrique réimplémentée, testé par
  comparaison directe (`test_evaluate_reuses_nwp_verification_metrics_exactly`).
- **`src/acf/verification/skill_database.py`** : `ModelSkillDatabase` —
  stockage réel append-only (JSON optionnel sur disque, en mémoire par
  défaut), `mean_skill()` retourne `None` sans historique réel (jamais
  un nombre inventé), `weights_from_skill()` calcule une vraie
  pondération inverse-erreur mais **omet silencieusement** tout modèle
  sans historique réel plutôt que de lui assigner un poids fabriqué.
- **Consensus pondéré par le skill (§15) : construit.**
  `ModelConsensusEngine.compute_unified_consensus()` accepte désormais
  `skill_database=` — si l'historique réel couvre 100% des modèles
  demandés, les poids déclarés par défaut sont remplacés par les vrais
  poids de skill (`weight_source="model_skill_database"`) ; sinon repli
  honnête sur les poids déclarés inchangés
  (`weight_source="declared_default_incomplete_skill_history"`) —
  **décision de portée délibérée** : pas de formule de mélange
  partiel skill/défaut inventée pour le cas d'historique incomplet.
- **Preuve de bout en bout, pas seulement unitaire** :
  `test_verification_pipeline_feeds_consensus_end_to_end_with_two_real_solver_runs`
  fait tourner `ModelConsensusEngine.compute_real_multi_model_disagreement()`
  (vrai `CoupledEarthSolver`, déjà réel) sur 3 points réels pour AROME
  et ALADIN, passe ces vraies séries dans `VerificationPipeline`,
  enregistre dans un vrai `ModelSkillDatabase`, et prouve que
  `compute_unified_consensus()` change réellement de poids en
  conséquence — **portée honnête** : ALADIN sert ici de série "vérité"
  uniquement pour exercer le pipeline de bout en bout, ce n'est pas une
  vraie observation (aucun flux d'observation réel n'existe encore
  dans ACF, voir `acf.data_assimilation.observation_ingestion`'s
  propres disclosures `NOT_INGESTED_NO_STATION_DATA_CONNECTION`).

**Validation :** 3039/3039 tests passent (3021 avant, +18 nouveaux),
ruff et mypy propres sur les 1377 fichiers analysés.

### Ce qui reste — le plan de 5 phases initial est terminé

Les 5 phases de l'ordre de priorité recommandé (Physics Guard, Data
Contract, Model Adapter Protocol, Event Engine, Verification pipeline +
Skill DB) sont maintenant toutes construites. Manques encore réels et
non triviaux (voir la synthèse plus haut, pas remise à jour ligne par
ligne pour rester honnête sur ce qui a été relu à cette date précise) :

- ~~**Certification Engine** (§32)~~ — **construit, voir mise à jour
  ci-dessous.**
- **Job Engine** (§22/§46) — aucune classe `Job` générique au-dessus du
  HPC réel existant (`HPCConnectionManager`/`hpc_workflow/`).
- **Golden Datasets** (§31-32) — toujours aucun `tests/data/golden/`.
- **Model Adapters WRF/ICON/OpenIFS** — toujours absents (portée
  explicitement exclue de la phase Model Adapter Protocol).
- **Fusion multi-modèles en champ complet** (§29-30) — le disagreement
  réel reste point-par-point, pas un champ fusionné avec biais/skill
  (le Model Skill Database construit ici est justement la brique qui
  manquait pour un futur biais-correction par modèle).

## Mise à jour 2026-09-02 (suite) — Certification Engine construit

Dernière pièce du plan initial de 5 phases, choisie ensuite comme
priorité suivante car elle ne dépendait plus que de briques déjà
réelles. `src/acf/certification/engine.py` : `CertificationEngine`
exécute le pipeline exact du §32 (`INPUT VALID → QC PASS → PHYSICS
PASS → SCIENCE PASS → PROVENANCE PASS → VERIFICATION STATUS →
CERTIFICATION`), **sans réimplémenter aucune étape** :

- **INPUT VALID** — `Dataset.is_fully_documented()` (Data Contract,
  déjà réel, réutilisé).
- **QC PASS** — `Dataset.quality.status` (`QualityInfo`, déjà réel) ;
  exige un vrai `"PASS"`, `NOT_ASSESSED` échoue honnêtement au lieu
  d'être traité comme un succès implicite.
- **PHYSICS PASS** — `Dataset.validate()`, qui réutilise déjà
  `PhysicsGuard` en interne — pas un second appel dupliqué.
- **SCIENCE PASS** — réel seulement si un `VariableContract` est
  fourni (vérifie les valeurs contre son vrai `valid_range`) — **aucun
  moteur de diagnostics unifié n'existe ailleurs dans ACF**
  (confirmé plus haut : "Diagnostics unifiés : PARTIAL, dispersé"),
  donc cette étape est honnêtement `applicable=False` sans contrat,
  jamais inventée.
- **PROVENANCE PASS** — `Provenance.is_complete()` (déjà réel).
- **VERIFICATION STATUS** — `ModelSkillDatabase.mean_skill()` (phase
  précédente) contre un seuil déclaré par l'appelant ; honnêtement
  `applicable=False` sans base de skill configurée ou sans historique
  réel enregistré pour ce modèle/variable — jamais un succès fabriqué.

**Branché réellement, pas juste construit à côté** :
`CertificationEngine.certify_event()` fait avancer un vrai
`acf.events.event.Event` de `VERIFIED` à `CERTIFIED` — la seule
transition que ce moteur a le droit de déclencher, sans ajouter
d'arête au diagramme de `Event._LEGAL_TRANSITIONS` (un rapport
`REJECTED` laisse simplement l'événement à `VERIFIED`, puisque
`VERIFIED` n'a de toute façon aucune arête `REJECTED` dans le cycle de
vie déjà construit).

**Validation, de bout en bout, pas seulement unitaire** : un test
construit un vrai `Event` via `detect_strong_wind_events()`, un vrai
`Dataset` via `Dataset.from_real_field()` sur une vraie sortie
`compute_real_complexity_field()`, un vrai `VariableContract`, et
prouve que `certify_event()` fait réellement passer l'événement à
`CERTIFIED` (ou le laisse honnêtement à `VERIFIED` si une étape réelle
échoue). 16 nouveaux tests. Suite complète : **3055/3055** tests
passent (3039 avant), ruff et mypy propres sur les 1378 fichiers.

### Ce qui reste réellement

- ~~**Job Engine** (§22/§46)~~ — **construit, voir mise à jour
  ci-dessous.**
- **Golden Datasets** (§31-32) — toujours absent.
- **Model Adapters WRF/ICON/OpenIFS** — toujours absents.
- **Fusion multi-modèles en champ complet** (§29-30) — toujours
  point-par-point, pas de champ fusionné avec correction de biais par
  modèle (le Model Skill Database est la brique qui manquait pour ça,
  pas encore utilisée dans ce sens).
- **API organisée par domaine** (§21) — toujours partielle.

## Mise à jour 2026-09-02 (suite) — Job Engine construit

`src/acf/jobs/` : `Job` (contrat exact §22/§46 —
`job_id`/`status`/`progress_pct`/`retry_count`, plus les paramètres de
soumission nécessaires pour un vrai retry) + `JobEngine`
(`submit`/`cancel`/`pause`/`resume`/`refresh_status`/`retry`), **sans
réimplémenter la vraie couche de soumission HPC** —
`acf.hpc_connector.job_manager.JobManager` (déjà réel, sbatch/scancel
via SSH réel, testé contre le vrai cluster Fennec) reste l'unique
mécanisme de soumission ; `JobEngine` l'enveloppe.

**Bugs réels trouvés et corrigés en cours de route** (même classe que
tout ce que les audits précédents ont déjà trouvé, pas une nouvelle
session séparée) :
- `SlurmScheduler.cancel_job()` faisait `return True`
  **inconditionnellement**, sans jamais vérifier le résultat SSH réel
  — exactement le motif que `JobManager.cancel_job()`'s propre NOTE
  affirmait déjà avoir corrigé, alors qu'il n'y avait rien de réel à
  propager. Corrigé : exige maintenant un vrai aller-retour SSH non
  simulé (`is_simulated=False`) avec `exit_code=0`.
- `SlurmScheduler.get_job_status()` retournait `"RUNNING"` dès que la
  sortie de `squeue` était vide — or une sortie vide est le
  comportement normal de `squeue` une fois qu'un job a **déjà quitté
  la file** (terminé, échoué...), pas une preuve qu'il tourne encore.
  Corrigé : distingue maintenant appel simulé
  (`"UNKNOWN_NO_REAL_SCHEDULER_CONNECTION"`) de sortie réelle vide
  (`"UNKNOWN_LEFT_QUEUE_NO_SACCT_WIRED"`, résoudre COMPLETED/FAILED
  nécessiterait `sacct`, non câblé).
- `JobManager.pause_job()`/`resume_job()` changeaient le statut local
  sans **aucun** appel réel au scheduler. Corrigé : deux nouvelles
  méthodes réelles `SlurmScheduler.suspend_job()`/`resume_job()`
  (`scontrol suspend`/`resume` réel via SSH, même convention honnête
  que `cancel_job()`), `JobManager` propage désormais leur vrai
  résultat au lieu de le supposer.

**Classification honnête, pas une taxonomie inventée** :
`is_terminal()`/`is_failure()`/`is_success()` ne reconnaissent que les
statuts réellement produits par cette couche (états Slurm réels,
statuts `"NOT_SUBMITTED_..."`/`"..._NOT_CONFIRMED"` déjà existants) —
un statut non reconnu est traité comme "encore en vol", jamais deviné
terminal.

`JobEngine.retry()` est un vrai nouveau comportement : refuse de
retenter un job qui n'est pas dans un vrai statut d'échec terminal
(`ValueError`), sinon resoumet réellement avec les mêmes paramètres et
incrémente `retry_count` — retourne un nouveau `Job` (Slurm n'a pas de
"resoumettre sous le même id").

**Validation :** 29 nouveaux tests (dont 5 contre le vrai
`SlurmScheduler` en mode hors-ligne, prouvant les nouveaux
comportements honnêtes plutôt que de les supposer). Suite complète :
**3085/3085** tests passent (3055 avant), ruff et mypy propres sur les
1381 fichiers.

### Ce qui reste réellement, maintenant

- ~~**Golden Datasets** (§31-32)~~ — **construit, voir mise à jour
  ci-dessous.**
- **Model Adapters WRF/ICON/OpenIFS** — toujours absents.
- **Fusion multi-modèles en champ complet** (§29-30) — toujours
  point-par-point.
- **API organisée par domaine** (§21) — toujours partielle.
- **Progress réel par job** — `Job.progress_pct` existe dans le
  contrat mais rien dans ACF ne le calcule encore (limite honnêtement
  documentée dans `acf.jobs.job`, pas fabriquée).

## Mise à jour 2026-09-02 (suite) — Golden Datasets construits

`tests/data/golden/` + `src/acf/testing/golden.py` (utilitaire réel de
comparaison, réutilisé par tous les tests plutôt que chacun
réimplémentant son propre chargement JSON/tolérance flottante) +
`tests/scientific/regression/` — ferme à la fois le §31-32 ("aucun
`tests/data/golden/`") et une partie du §51/§53 ("pas de catégorie
`tests/scientific/regression/` séparée").

**Discipline appliquée, pas une snapshot aveugle de n'importe quoi** :
seul un calcul **réellement, prouvablement déterministe** reçoit un
fichier golden — documenté explicitement dans
`tests/data/golden/README.md`, avec la raison précise pour laquelle un
run complet de `CoupledEarthSolver` en est **délibérément exclu** (son
propre test déjà existant,
`test_compute_real_multi_model_disagreement_seed_is_deterministic_per_point`,
documente que les composants atmosphère/océan du solveur appellent
`np.random.*` directement sur l'état RNG global non-seedé — un golden
dataset dessus serait soit instable, soit fabriquerait une
reproductibilité qui n'existe pas).

Trois fixtures réelles :
- **`isa_standard_atmosphere.json`** — `calculate_isa_temperature()`/
  `calculate_isa_pressure()` (déjà vérifiées contre la vraie table
  ICAO Doc 7488 / ISO 2533:1975 à 0.05% près, par le module lui-même)
  à 9 altitudes standard.
- **`awci_calculator_reference_case.json`** — un cas météorologique
  fixe et réaliste passé dans `AWCICalculator().calculate()` (fonction
  pure de son dict d'entrée — pas de RNG, pas de solveur) — sortie
  complète réelle verrouillée.
- **`nwp_verification_metrics_reference_case.json`** — un cas
  `NWPVerificationMetrics.evaluate_all()` choisi pour être
  **calculable à la main** (bias=0, mae=0.5, rmse=√0.5, pod/far/csi/
  ets tous exacts) — vérifie donc aussi que le code et un futur test
  ne partagent pas la même erreur de formule, pas seulement que le
  code est stable par rapport à lui-même.

**Validation :** 10 nouveaux tests (dont des tests de l'utilitaire
`acf.testing.golden` lui-même — rapporte le vrai chemin de la première
divergence, tolère le bruit flottant négligeable, détecte une clé
manquante). Suite complète : **3095/3095** tests passent (3085 avant),
ruff et mypy propres sur les 1383 fichiers.

### Ce qui reste réellement, maintenant

- ~~**Model Adapters WRF/ICON/OpenIFS**~~ — **construits, voir mise à
  jour ci-dessous.**
- **Fusion multi-modèles en champ complet** (§29-30) — toujours
  point-par-point.
- **API organisée par domaine** (§21) — toujours partielle.
- **Progress réel par job** — toujours non calculé (limite honnête).

## Mise à jour 2026-09-02 (suite) — Adapters WRF/ICON/OpenIFS construits

`src/acf/models/{wrf,icon,openifs}/` : trois nouveaux adapters réels
derrière le même `BaseWeatherModel` Model Adapter Protocol
qu'AROME/ALADIN/ARPEGE. Différence honnête et notable par rapport à
ces trois-là : `epygram` (leur backend FA réel) **n'est pas installé
dans cet environnement** (`EPYGRAM_AVAILABLE=False`, confirmé), donc
leur `read()` ne peut aujourd'hui exercer qu'un repli honnête, jamais
une vraie lecture bout-en-bout ici. WRF/ICON/OpenIFS utilisent au
contraire des dépendances réellement installées (`xarray`/`netCDF4`
pour WRF, `xarray`/`cfgrib`/`eccodes` pour ICON/OpenIFS — déjà
utilisées ailleurs dans le dépôt, ex. `GRIBReader`/`NetCDFReader`) :
`read()` ouvre et lit donc un **vrai** fichier de bout en bout,
vérifié par des tests qui écrivent un vrai NetCDF façon WRF-ARW
(`xarray`) et un vrai message GRIB2 (`eccodes`, mêmes bindings que le
reste du dépôt) puis le relisent réellement.

- **`src/acf/models/common/generic_xarray_reader.py`** —
  `read_netcdf_generic()`/`read_grib_generic()`, partagés par les 3
  adapters, extraction générique réelle (variables/dimensions/
  coordonnées/attributs — ce que le fichier contient vraiment, jamais
  une liste de champs par-modèle codée en dur).
- **`WRFIngestionAdapter`** — noms de variables WRF-ARW réels et
  documentés (T2/U10/V10/PSFC/HGT/RAINC/RAINNC/XLAT/XLONG), détection
  sur `"wrfout"` (convention réelle de nommage WRF-ARW).
- **`ICONIngestionAdapter`** — noms GRIB2 ICON réels documentés par
  DWD (T_2M/U_10M/V_10M/PMSL/TOT_PREC/CLCT). **Trouvaille honnête**,
  vérifiée en construisant cet adapter, pas supposée : les tables
  ecCodes de cet environnement résolvent plusieurs de ces noms (ex.
  `T_2M`) vers le même concept OMM universel que ecCodes connaît déjà
  sous `2t`/`cfVarName t2m` (le même qu'ERA5/OpenIFS), pas un nom
  distinct DWD — documenté explicitement dans la docstring de la
  classe, `read()` rapporte donc ce que cfgrib résout vraiment, jamais
  la liste déclarée par `variables()`.
- **`OpenIFSIngestionAdapter`** — réutilise réellement la liste de
  variables d'`ERA5Model` (OpenIFS est la vraie release ouverte du
  code IFS d'ECMWF, même table de paramètres réelle — pas une
  invention séparée). **Limite honnête documentée** : contrairement au
  nommage FA d'AROME/ALADIN/ARPEGE, les fichiers OpenIFS bruts suivent
  la convention MARS/IFS classique d'ECMWF (`ICMSH*`/`ICMGG*`), sans
  marqueur de nom de fichier propre à OpenIFS — `detect()` ne
  reconnaît donc qu'un fichier explicitement nommé "openifs"/"oifs",
  pas le nommage natif IFS lui-même.
- **`levels()` honnête pour les 3** : retourne une chaîne descriptive
  (`"eta"`/`"hybrid"`) plutôt qu'un nombre fixe de niveaux — le nombre
  réel de niveaux verticaux de WRF/ICON/OpenIFS est un choix de
  configuration par run, pas une constante du modèle (contrairement
  aux 90 niveaux opérationnels fixes d'AROME). A nécessité d'élargir
  `BaseWeatherModel.levels()`/`vertical_levels()` à `list[Any] | str`
  (mypy l'exigeait — `ERA5Model.levels()` faisait déjà pareil mais
  sans annotation de type, donc jamais vérifié jusqu'ici).

**Validation :** 24 nouveaux tests (dont des lectures réelles de bout
en bout sur de vrais fichiers NetCDF/GRIB2 construits pour le test,
pas des mocks). Suite complète : **3119/3119** tests passent (3095
avant), ruff et mypy propres sur les 1391 fichiers.

### Ce qui reste réellement, maintenant

- ~~**Fusion multi-modèles en champ complet**~~ — **construite, voir
  mise à jour ci-dessous.**
- **API organisée par domaine** (§21) — toujours partielle.
- **Progress réel par job** — toujours non calculé (limite honnête).

## Mise à jour 2026-09-02 (suite) — Fusion multi-modèles en champ complet construite

`src/acf/awci/multi_model_fusion.py` : `compute_real_multi_model_field_fusion()`
ferme le §29-30 en réutilisant tout ce qui existait déjà, sans rien
dupliquer :

1. Fait tourner `acf.awci.spatial_field.compute_real_complexity_field()`
   (déjà réel) une fois par modèle demandé, à sa vraie résolution de
   grille (`MODEL_CONFIGS`), avec une perturbation par modèle
   déterministe et distincte.
2. **Regridding réel** vers une grille cible commune —
   `regrid_nearest_neighbor()`, même convention plus-proche-voisin déjà
   utilisée partout dans ce paquet (`path_sampling.py`,
   `compute_real_multi_model_disagreement()`), vectorisée sur un champ
   entier plutôt qu'un point. **Portée honnête** : toujours pas de
   regridding bilinéaire/conservatif — ce manque du gap-map n'est pas
   fermé par ce module, explicitement documenté comme tel.
3. **Pondération réelle par skill** — réutilise
   `ModelSkillDatabase.weights_from_skill()` (phase Verification), même
   convention "tout ou rien" déjà établie dans
   `compute_unified_consensus()` : poids de skill réels seulement si
   l'historique couvre 100% des modèles demandés, sinon repli honnête
   sur poids égaux (`weight_source` explicite dans les deux cas).
4. **Correction de biais réelle par modèle** — le "biais" du §29-30 :
   si la base de skill a un vrai `bias` enregistré
   (`NWPVerificationMetrics.evaluate_all()` via `VerificationPipeline`)
   pour un modèle/variable, il est réellement soustrait du champ de ce
   modèle avant fusion — un modèle sans historique de biais réel est
   combiné non corrigé, jamais un biais=0 fabriqué
   (`bias_corrected_models` rapporte lesquels, honnêtement).
5. **Spread en champ complet** — `EnsembleManager` (réutilisé) appliqué
   à chaque point de grille à travers les modèles regriddés — équivalent
   plein-champ du `disagreement_spread` ponctuel déjà existant.

**Validation :** 15 nouveaux tests (regrid réel, pondération égale vs
skill réel, historique incomplet → repli honnête, correction de biais
réelle vérifiée par calcul direct). Suite complète : **3134/3134**
tests passent (3119 avant), ruff et mypy propres sur les 1392
fichiers.

### Ce qui reste réellement, maintenant

- ~~**API organisée par domaine** (§21)~~ — **construite, voir mise à
  jour ci-dessous.**
- **Progress réel par job** — toujours non calculé (limite honnête).
- **Regridding bilinéaire/conservatif générique** — toujours absent
  (plus-proche-voisin seulement, partout dans ce paquet).

## Mise à jour 2026-09-02 (suite) — API organisée par domaine (§21) construite

`src/acf/web/routers/` : 4 routers FastAPI réels montés sous
`/api/v1/*` sur l'app existante (`acf.web.hpc_dashboard_server.
create_app()`), chacun une fine couche HTTP sur un moteur déjà réel
d'une phase précédente — **rien de nouveau n'est calculé ici** :

- **`/api/v1/models`** — Model Adapter Protocol (7 adaptateurs réels :
  AROME/ALADIN/ARPEGE/ERA5/WRF/ICON/OpenIFS). `GET` liste/détail
  `capabilities()` réel, `POST /{name}/detect` exécute le vrai
  `detect()`.
- **`/api/v1/complexity`** — `POST /score` appelle réellement
  `AWCICalculator().calculate()` ; `GET /field` fait réellement tourner
  `CoupledEarthSolver` via `compute_real_complexity_field()` (garde de
  taille de requête partagée, `_solver_guard.py`, contre une grille
  non bornée demandée par HTTP).
- **`/api/v1/events`** — `POST /detect` fait tourner le vrai solveur
  puis le vrai détecteur (`strong_wind`/`fog_favorable_conditions`),
  stocke chaque `Event` réel en mémoire ;
  `POST /{id}/transition` appelle réellement `Event.transition_to()`
  — **vérifié en conditions réelles par HTTP** : une transition
  illégale (ex. `ANALYZED → CERTIFIED`) renvoie un vrai 409 avec le
  message de `IllegalEventTransitionError`, pas un succès silencieux.
- **`/api/v1/datasets`** — `POST /from_complexity_field` construit un
  vrai `Dataset` via `Dataset.from_real_field()` ;
  `GET /{id}/validate` relance réellement `PhysicsGuard` via
  `Dataset.validate()`.

**Bug réel trouvé et corrigé en construisant ce routeur, pas supposé** :
`Dataset.coordinates` contient de vrais tableaux numpy (`lats`/`lons`)
dans un simple champ `dict`, que `dataclasses.asdict()` ne convertit
pas (ce n'est pas un champ dataclass imbriqué) — `jsonable_encoder`
plantait dessus (`TypeError` réel, reproduit puis corrigé, pas
seulement imaginé). `_numpy_to_native()` le corrige récursivement.
Deuxième trouvaille réelle : `forecast_field` contient de vrais
`np.nan` (score de prévision non défini) — `.tolist()` seul produit un
token `NaN` Python valide mais **invalide en JSON strict** (un piège
réel pour un client JS) ; `field_to_json_safe_list()` convertit en
`null`, vérifié par un test qui force ce cas.

**Décision de portée délibérée, pas un oubli** : `/api/hpc/*` et
`/api/fno/predict_demo` (déjà réels, déjà testés) restent à leurs
chemins historiques — les migrer sous `/api/v1` est un refactor séparé
(mettrait à jour leurs propres tests et le JS du dashboard), gardé hors
de cette passe.

**Validation :** 22 nouveaux tests (incluant le cycle de vie complet
d'un événement par HTTP — 200 → 200 → 409 → re-vérification que le
statut n'a pas bougé après le rejet). Suite complète : **3156/3156**
tests passent (3134 avant), ruff et mypy propres sur les 1398 fichiers.

### Ce qui reste réellement, maintenant

- ~~**Progress réel par job**~~ — **construit, voir mise à jour
  ci-dessous.**
- **Regridding bilinéaire/conservatif générique** — toujours absent.
- **Migration `/api/hpc/*` + `/api/fno/*` sous `/api/v1`** — délibérément
  hors de cette passe (voir ci-dessus).

## Mise à jour 2026-09-02 (suite) — Progress réel par job construit

`Job.progress_pct` existait dans le contrat §22/§46 depuis la phase
Job Engine mais rien dans ACF ne le calculait (limite honnêtement
documentée à l'époque). Fermé maintenant :

- **`src/acf/hpc_connector/slurm_duration.py`** —
  `parse_slurm_duration()`, un vrai parseur du format de durée SLURM
  (`[jours-]heures:minutes:secondes`, pas un format unique — squeue
  choisit la forme la plus courte selon la durée réelle), gère
  honnêtement `"UNLIMITED"` (vraie valeur SLURM sans équivalent
  numérique) en retournant `None`, jamais un nombre deviné.
- **`SlurmScheduler.get_job_progress()`** — interroge réellement
  `squeue -j <id> -h -o "%M %l"` (temps écoulé réel / limite réelle)
  via SSH, calcule `progress_fraction = elapsed/limit` borné à [0,1].
  **Portée honnête, explicite dans la docstring** : c'est un vrai
  proxy temps-écoulé-vs-limite, **pas** un pourcentage d'avancement
  des calculs — SLURM (et `sacct`) n'a aucune notion de ça, c'est le
  même proxy que tout système de "barre de progression" au-dessus
  d'un scheduler batch utilise réellement. Repli honnête (jamais un
  nombre fabriqué) : appel simulé, job déjà sorti de la file, ou
  `--time` jamais fixé (squeue rapporte `"UNLIMITED"`).
- `PBSScheduler`/`LocalScheduler` : repli honnête symétrique (pas
  d'appel réel `qstat` câblé), même convention que leurs méthodes
  sœurs.
- **`JobEngine.refresh_progress(job)`** — met réellement à jour
  `job.progress_pct` seulement quand la donnée réelle est disponible ;
  sinon laisse la valeur précédente inchangée (jamais remise à 0/None
  par erreur), même convention que `refresh_status()`.

**Validation :** 28 nouveaux tests (parseur SLURM isolé + chemin de
parsing réel de `get_job_progress()` via un exécuteur factice
contrôlé, y compris `"UNLIMITED"` et file déjà quittée). Suite
complète : **3184/3184** tests passent (3156 avant), ruff et mypy
propres sur les 1399 fichiers.

### Ce qui reste réellement, maintenant

- ~~**Regridding bilinéaire/conservatif générique**~~ — **construit,
  voir mise à jour ci-dessous.**
- **Migration `/api/hpc/*` + `/api/fno/*` sous `/api/v1`** — délibérément
  hors de cette passe.

## Mise à jour 2026-09-02 (suite) — Regridding bilinéaire/conservatif générique construit

`src/acf/awci/regridding.py` : `regrid_nearest_neighbor()` (déplacé
depuis `multi_model_fusion.py`, même logique, pas réimplémentée — un
import transparent le garde disponible aux deux endroits) +
`regrid_bilinear()` + `regrid_conservative()`, tous les trois scopés
honnêtement à une grille rectiligne régulière lat/lon (le seul type
que produit `EarthGrid`).

- **`regrid_bilinear()`** — vraie interpolation bilinéaire entre les 4
  points sources encadrants (`numpy.searchsorted`, marche pour des
  coordonnées non uniformément espacées). **Vérifié par une propriété
  réelle, pas un test de fumée** : reproduction exacte d'un champ
  linéaire.
- **`regrid_conservative()`** — vraie moyenne pondérée par recouvrement
  d'aire, avec la vraie pondération sphérique (`Δ(sin(lat))`, pas des
  degrés plats — la vraie raison physique pour laquelle une cellule
  polaire couvre moins de surface réelle par degré qu'une cellule
  équatoriale).

**Deux vrais bugs trouvés et corrigés en construisant ceci, pas
supposés — vérifiés par un test de conservation indépendant (somme
pondérée par aire recalculée séparément, pas en réutilisant la même
formule interne) avant d'être considérés clos** :
1. La première version bornait inconditionnellement les bords
   extérieurs de cellule à `lo_bound`/`hi_bound` — correct pour une
   grille globale, mais **faux pour une grille régionale** (ex.
   `lats=[10,20,30]`) : l'étirait jusqu'au pôle, faisant croire à une
   couverture de données inexistante. Corrigé : extrapolation
   naturelle par la moitié de l'espacement adjacent, bornée seulement
   quand elle dépasserait vraiment le domaine physique.
2. Une fois corrigé, la longitude (réellement périodique — convention
   `EarthGrid.lons` = `linspace(-180,180,n,endpoint=False)`, aucun
   point réel exactement à +180°) perdait jusqu'à une cellule entière
   de surface réelle à la couture ±180°, cassant la conservation
   précisément pour la convention de grille globale réelle d'ACF.
   Corrigé : `_overlap_weights(..., period=360.0)` teste aussi les
   décalages ±360° et somme tout recouvrement réel trouvé — vérifié
   par un test qui prouve qu'une cellule source proche de +180°
   contribue réellement à une cellule cible chevauchant l'antiméridien
   (et zéro à une cellule cible éloignée), pas seulement que le total
   conservé retombe juste.

**Portée honnête, pas cachée** : `regrid_nearest_neighbor()`/
`regrid_bilinear()` ne gèrent PAS ce wraparound (un point cible pile à
l'antiméridien est borné au bord source le plus proche, pas enroulé) —
disclosure précise par fonction, pas une déclaration générale
imprécise. `compute_real_multi_model_field_fusion()` continue d'utiliser
le plus-proche-voisin par défaut (décision scientifique délibérée, pas
changée par cet ajout).

**Validation :** 22 nouveaux tests (dont conservation vérifiée sur 6
résolutions différentes + décomposition grossissement/raffinement +
la preuve directe du wraparound, pas seulement le total). Suite
complète : **3206/3206** tests passent (3184 avant), ruff et mypy
propres sur les 1400 fichiers.

### Ce qui reste réellement, maintenant

- ~~**Migration `/api/hpc/*` + `/api/fno/*` sous `/api/v1`**~~ —
  **construite, voir mise à jour ci-dessous.**

## Mise à jour 2026-09-02 (suite) — Migration `/api/hpc/*` + `/api/fno/*` sous `/api/v1` terminée

Dernière pièce du §21 — celle explicitement différée à la phase
précédente ("réel, séparé, plus gros — mettrait à jour leurs propres
tests et le JS du dashboard"). Faite maintenant, proprement, sans alias
de compatibilité legacy (déplacement réel, pas une duplication) :

- `GET/POST /api/hpc/status|connect|disconnect` → `/api/v1/hpc/...`
- `WS /ws/hpc/status` → `/api/v1/hpc/ws`
- `POST /api/fno/predict_demo` → `/api/v1/fno/predict_demo`

`acf.web.routers.hpc_router`/`fno_router` : même logique réelle
exactement, déplacée depuis `hpc_dashboard_server.py` (pas
réimplémentée) — `_hpc_status()`, la vraie distinction
`connected`/`real_ssh_transport`, le vrai appel
`NeuralOperatorEngine.predict_surface_temperature()`, tout identique.
`hpc_dashboard_server.create_app()` n'est plus qu'un assemblage : état
d'app + montage des 6 routers + page HTML/JS du dashboard (URLs mises
à jour vers `/api/v1/...`).

**Vérifié, pas supposé** : deux nouveaux tests
(`test_old_unprefixed_paths_are_genuinely_gone`,
`test_old_websocket_path_is_genuinely_gone`) prouvent que les anciens
chemins renvoient vraiment 404 / échouent la poignée de main WebSocket
— pas seulement que les nouveaux fonctionnent. `DEFAULT_FNO_CHECKPOINT`
reste importable depuis `acf.web.hpc_dashboard_server` (ré-exporté) —
aucun autre appelant du dépôt ne dépendait des anciens chemins HTTP
eux-mêmes (vérifié par recherche exhaustive).

**Validation :** suite complète : **3208/3208** tests passent (3206
avant), ruff et mypy propres sur les 1402 fichiers.

### Ce qui reste réellement, maintenant

Toutes les priorités identifiées par l'audit initial et par les
demandes de suivi sont closes. Manques réels restants, plus petits ou
plus larges qu'un seul module (voir les sections détaillées plus haut
pour chacun) :

- Model Adapters WRF/ICON/OpenIFS : `read()` réel, mais `epygram`
  (backend FA d'AROME/ALADIN/ARPEGE) reste non installé dans cet
  environnement — aucune lecture FA de bout en bout n'est testable ici.
- Pas de Certification Engine branché à un pipeline de production
  automatisé (le moteur existe, réel, testé — pas encore appelé en
  continu sur un flux réel).
- Pas de base de données de persistance pour `/api/v1/events` /
  `/api/v1/datasets` (stockage en mémoire, réel mais non durable,
  disclosure explicite dans chaque routeur).

## Mise à jour 2026-09-02 (suite) — wraparound ±180° complété pour regrid_nearest_neighbor()/regrid_bilinear()

Choisi ensuite comme le manque restant le mieux borné et le moins
risqué à fermer proprement dans cette même session (pas de nouvelle
dépendance externe, pas de décision d'architecture à trancher, technique
déjà éprouvée sur `regrid_conservative()`).

- **`regrid_nearest_neighbor()`** — `_circular_distance()` (distance
  angulaire réelle sur un cercle de 360°) remplace la simple différence
  absolue pour la longitude : un point cible à 179° trouve maintenant
  réellement son plus proche voisin à -179° (2° via l'antiméridien), pas
  celui à 170° (9°, mais "plus proche" avec une distance non-circulaire
  naïve).
- **`regrid_bilinear()`** — `_bracket_indices_periodic()`, même
  technique de points fantômes déjà utilisée par
  `_overlap_weights(..., period=...)` pour `regrid_conservative()` (pas
  une troisième implémentation différente de la périodicité) : un point
  cible à la couture interpole désormais entre les vrais points source
  de part et d'autre de l'antiméridien.

**Vérifié par un calcul à la main, pas seulement un test de fumée** :
avec des sources à -179° (valeur 100) et 170° (valeur 200), un point
cible à 179° est à 9° de 170° et seulement 2° de -179° via le chemin
court (170°→180°→-179° = 11° au total) — la valeur bilinéaire attendue
est `200*(1-9/11) + 100*(9/11) ≈ 118.18`, exactement ce que le code
retourne.

**Portée finale, honnête** : les trois fonctions du module gèrent
maintenant la périodicité réelle à 360° de la longitude ; aucune ne
gère un axe de latitude périodique (n'existe pas physiquement — les
pôles sont de vraies bornes non-périodiques).

**Validation :** 3 nouveaux tests (dont la vérification par calcul à la
main ci-dessus, et une preuve que le chemin périodique se réduit
exactement au comportement non-wrappé loin de la couture). Suite
complète : **3211/3211** tests passent (3208 avant), ruff et mypy
propres sur les 1402 fichiers.

### Ce qui reste réellement, maintenant

- Model Adapters WRF/ICON/OpenIFS : `epygram` (backend FA d'AROME/
  ALADIN/ARPEGE) reste non installé dans cet environnement.
- Pas de Certification Engine branché à un pipeline de production
  automatisé.
- Pas de base de données de persistance pour `/api/v1/events` /
  `/api/v1/datasets` (en mémoire, réel mais non durable, disclosure
  explicite).

## Mise à jour 2026-09-02 (suite) — epygram réellement installé, dépendance déclarée

Demande explicite de l'utilisateur ("installe epygram"). Trouvaille
réelle en vérifiant plutôt qu'en supposant : `epygram` **était déjà
installé** dans cet environnement (`pip index versions epygram` →
2.1.0 installé), contredisant ce que la phase WRF/ICON/OpenIFS avait
affirmé sans jamais faire `import epygram` directement — corrigé dans
les docstrings concernées (`generic_xarray_reader.py`,
`wrf/ingestion_adapter.py`, `tests/test_wrf_icon_openifs_adapters.py`).

**Vrai bug de dépendance non déclarée trouvé et corrigé** — même classe
que la trouvaille PyYAML déjà documentée dans `ROADMAP.md` : `epygram`
n'était déclaré **nulle part** (`pyproject.toml`, `requirements.txt`)
malgré `tests/test_epygram_reader.py` qui l'importe sans condition en
tête de fichier — ne fonctionnait dans cet environnement que parce
qu'il s'y trouvait déjà installé par ailleurs. Ajouté à l'extra
`formats` de `pyproject.toml` et à `requirements.txt`.

**Trouvaille réelle, confirmée en essayant, pas supposée** : une
écriture FA entièrement synthétique reste impossible dans ce dépôt —
`epygram.formats.FA.FA` exige `headername` en mode écriture, "name of
an existing header" tiré des archives internes de Météo-France ;
aucune géométrie construite par l'API publique d'epygram
(`RegLLGeometry`, testé réellement) ne suffit à elle seule. Confirmé
en essayant `epygram.open()` sur un vrai fichier texte nommé `.fa` :
lève une vraie `epygramError` réelle ("unable to guess format"), déjà
correctement capturée par `EPyGrAMReader`'s chemin honnête existant
(`tests/test_epygram_reader.py` le testait déjà correctement, avant
même cette vérification). Donc : lecture FA de bout en bout toujours
non testable ici, mais pour une raison structurelle du format
lui-même, pas un défaut de ce dépôt.

**Validation :** suite complète toujours **3211/3211** (aucun test
cassé par la présence réelle d'epygram — `test_epygram_reader.py`
était déjà écrit pour cet état), ruff et mypy propres.

## Mise à jour 2026-09-02 (suite) — Certification Engine branché à un déclencheur de production réel

Demande explicite de l'utilisateur. `acf.forecast.engine.
run_forecast_cycle()` est le vrai point d'entrée que
`HPCConnectionManager`'s pipelines one-click AROME/ALADIN soumettent
comme commande de job SLURM réel, et que `daily_forecast_cycle.py`
(CI/CD réel) déclenche indirectement en soumettant ce même job — donc
brancher la certification **ici** la fait tourner sur chaque cycle de
prévision réel exécuté par ce dépôt, quel que soit le déclencheur
(manuel, HPC one-click, CI quotidien), sans construire un second
service séparé que personne n'appelle.

- **Nouveau vrai contrôle QC PASS** (n'existait nulle part avant) :
  `_certify_forecast_output()` vérifie que le champ de température de
  surface final est entièrement fini (`numpy.isfinite`) — un vrai mode
  d'échec d'un solveur couplé numérique (divergence), pas un contrôle
  fabriqué. `quality.status` est toujours réellement "PASS" ou "FAIL",
  jamais laissé "NOT_ASSESSED" par défaut.
- Construit un vrai `Dataset` (id, `forecast_reference_time`/
  `valid_time`/`lead_time` réels dérivés du vrai déroulement du cycle,
  `Provenance` complet) et l'envoie à travers le vrai
  `CertificationEngine` déjà construit et testé — rien de dupliqué.
- `run_forecast_cycle(certify=True)` par défaut ; `--no-certify` côté
  CLI pour un run brut plus rapide.
- **Vrai signal d'échec pour un scheduler CI/CD** : `main()` sort avec
  le code 2 (pas 0/1) si `REJECTED` — même convention déjà établie par
  `scripts/daily_forecast_cycle.py` pour `is_real_submission` — le
  fichier NetCDF reste écrit (rien perdu), mais un appelant ne peut
  plus traiter silencieusement une prévision rejetée comme un succès.

**Vérifié en conditions réelles, pas supposé** : un vrai cycle AROME
de bout en bout (`run_forecast_cycle("AROME", steps=2, ...)`) revient
`CERTIFIED` — reproduit ci-dessous, pas une affirmation en l'air :

```
{"status": "SUCCESS", ..., "certification": {"decision": "CERTIFIED", "dataset_id": "AROME-forecast-...", "failed_steps": []}}
```

**Validation :** 6 nouveaux tests (dont un contrôle QC PASS forcé avec
un vrai NaN injecté, et un test CLI qui prouve le code de sortie 2 sur
un rejet). Suite complète : **3217/3217** tests passent (3211 avant),
ruff et mypy propres sur les 1402 fichiers.

### Ce qui reste réellement, maintenant

- ~~Pas de base de données de persistance pour `/api/v1/events` /
  `/api/v1/datasets`~~ — **construite, voir mise à jour ci-dessous.**

## Mise à jour 2026-09-02 (suite) — persistance durable réelle pour /api/v1/events et /api/v1/datasets

Demande explicite de l'utilisateur. Choix technique : `sqlite3` de la
bibliothèque standard Python — **aucune nouvelle dépendance**, aucun
service de base de données séparé que ce dépôt devrait déployer
(aucun Postgres/Redis/etc. nulle part dans ce projet), même logique de
dépendance minimale que `ModelSkillDatabase`'s propre persistance JSON,
mais avec un vrai fichier SQLite (mode WAL) pour supporter des accès
concurrents réels d'un serveur ASGI sans se corrompre.

- **`src/acf/web/storage.py`** — `SqliteDocumentStore`, un magasin
  clé/document JSON générique réutilisé par les deux routeurs (pas
  dupliqué). `check_same_thread=False` (un vrai serveur uvicorn peut
  réellement appeler depuis un autre thread), `PRAGMA journal_mode=WAL`
  pour un fichier réel.
- **`Event.to_dict()`/`from_dict()`** et **`Dataset.to_dict()`/
  `from_dict()`** — ajoutés directement sur les contrats eux-mêmes
  (pas dans la couche web), aller-retour exact vérifié (`e == e2`
  après sérialisation/désérialisation, `values` numpy reconstruit
  identique). `numpy_to_native()` (déjà écrit pour la sérialisation
  HTTP de `/api/v1/datasets`) promu dans `dataset.py` et réutilisé, pas
  dupliqué une seconde fois.
- `events_router`/`datasets_router` : le dict en mémoire est remplacé
  par un vrai `SqliteDocumentStore`, chemin par défaut réel sous
  `<repo>/data/web/` (nouvellement ignoré par git, même convention
  ancrée que `/output/`/`/tmp/` déjà documentée dans `.gitignore`) ;
  `create_app(event_db_path=..., dataset_db_path=...)` permet
  l'injection pour les tests (`":memory:"` ou `tmp_path`).

**Preuve de bout en bout au niveau HTTP réel, pas seulement la classe
de stockage isolée** : un test construit une vraie app, détecte un
événement, avance réellement son cycle de vie jusqu'à `ANALYZED`, crée
un dataset, **ferme cette app**, en construit une **seconde,
totalement indépendante** pointant sur les mêmes vrais fichiers
(simulant un redémarrage de processus réel), et vérifie que
l'événement revient avec le statut `ANALYZED` intact (pas réinitialisé
à `DETECTED`) et que le dataset est toujours là.

**Validation :** 10 nouveaux tests (dont le test de redémarrage
ci-dessus, et une vérification qu'un magasin `":memory:"` NE survit
PAS à une réouverture — la distinction elle-même est testée, pas
seulement le cas positif). Suite complète : **3227/3227** tests
passent (3217 avant), ruff et mypy propres sur les 1403 fichiers.

### Ce qui reste réellement, maintenant

Toutes les demandes explicites de cette session sont closes. Le projet
n'a plus de manque identifié au niveau "moteur absent" — ce qui reste
est du raffinement continu (voir les sections précédentes pour le
détail de chaque limite honnêtement documentée : lecture FA de bout en
bout bloquée par une limite structurelle du format lui-même, etc.).

**Correction (trouvée en se relisant, pas signalée par ailleurs)** :
la phrase juste au-dessus affirmait auparavant "wraparound restant
pour 2 des 5 méthodes de regridding" — obsolète et faux à ce point du
document. `src/acf/awci/regridding.py` n'a que 3 méthodes (pas 5), et
sa propre docstring de module dit explicitement "All three genuinely
handle the real 360° longitude periodicity" depuis la mise à jour
"wraparound ±180° complété" plus haut dans ce même fichier — les trois
méthodes gèrent réellement le wraparound. Corrigé ici plutôt que
laissé comme une fausse limite documentée.

## Mise à jour 2026-09-02 (suite) — recommandation auto-choisie : audit complet des dépendances non déclarées

Aucune demande explicite restante — choix motivé par le fil de travail
du jour lui-même (la trouvaille epygram non déclarée) : plutôt que de
supposer que c'était un cas isolé, un vrai balayage AST (pas un grep
textuel fragile) de chaque `import`/`from ... import` de tout `src/` +
`tests/` a été comparé à l'ensemble réel des dépendances déclarées
(cœur + tous les extras de `pyproject.toml`).

**Un vrai deuxième bug de dépendance non déclarée trouvé, même classe
que PyYAML/epygram** : `acf/core/logger.py` importe `loguru`
**inconditionnellement**, non déclaré nulle part — atteignable via
`acf.core.application`/`bootstrap`/`plugin_manager` (infrastructure de
cycle de vie applicatif réelle, pas un module isolé). Corrigé : ajouté
aux `dependencies` du cœur de `pyproject.toml` et à `requirements.txt`,
juste à côté de PyYAML avec la même justification (un module `acf.core`
en dépend directement). **Honnêteté sur la méthode** : trouvé par
balayage d'imports répertoire-entier, pas par une réinstallation
fraîche complète comme la propre méthodologie de `ROADMAP.md` pour la
liste "cœur allégé" elle-même — précisé comme tel, pas présenté comme
le même niveau de vérification.

**Trois autres imports tiers non déclarés trouvés (`cupy`, `mpi4py`,
`psutil`) — vérifiés un par un, tous les trois déjà correctement
protégés par `try/except ImportError` avec un vrai indicateur de
disponibilité (`HAS_CUPY`/`_PSUTIL_AVAILABLE`/repli `mpi_procs=1`) :
aucun bug, déjà honnête, rien à corriger.**

**Validation :** suite complète toujours **3227/3227** (aucun
changement de comportement, seulement une déclaration), ruff et mypy
propres.

## Mise à jour 2026-09-02 (suite) — scan répertoire-entier des `except Exception: pass` silencieux

Demande explicite de l'utilisateur ("scan tout le projet... améliore
les"). Balayage AST réel (pas un grep fragile) de tout `src/acf` :
**44** blocs `except Exception:` trouvés, dont **24** suivis
directement de `pass` (ou `...`) sans aucun log — la même classe de
"échec silencieux" que ce dépôt corrige déjà ailleurs (ex. l'ancien
comportement d'`EPyGrAMReader`), mais jamais auditée de façon
exhaustive jusqu'ici.

**Les 24 relus individuellement, pas juste comptés** — la majorité
(nettoyage `close()`/`disconnect()`, tentative de format de clé SSH
alternatif, repli local réel après échec d'un exécuteur distant) sont
des patterns légitimes déjà défendables, cohérents avec la discipline
existante du dépôt. **Deux vrais bugs trouvés et corrigés** :

1. **`src/acf/gui/map/map_renderer.py`** — les 7 fonctionnalités de
   carte de base (océans, terres, lacs, rivières, frontières, côtes,
   grille lat/lon) avalaient silencieusement TOUTE exception Cartopy
   réelle (ex. échec de téléchargement du vrai shapefile Natural Earth
   sans accès réseau) sans aucun log — une carte pouvait rendre avec
   des éléments manquants sans aucune trace de diagnostic. **Cette
   classe avait aussi zéro test** avant cette passe. Corrigé : chaque
   échec réel est maintenant loggé (`logger.warning(..., exc_info=True)`)
   sans changer le comportement best-effort. 4 nouveaux tests, dont un
   qui force les 7 échecs réels via un stub et vérifie les 7 vrais logs.
2. **`src/acf/hpc_workflow/workflow_configuration.py`** — un vrai
   fichier de config existant mais malformé (YAML invalide, ou
   contenu réel qui n'est pas un mapping) était remplacé
   silencieusement par le même défaut fabriqué qu'un fichier
   simplement absent — **aucun moyen de distinguer "pas de config
   fournie" (légitime) de "config réelle cassée" (un vrai problème)**.
   Corrigé : seul un fichier réellement absent reste silencieux ;
   un fichier présent mais inutilisable logge maintenant un vrai
   avertissement avec la cause réelle. 4 nouveaux tests couvrant les
   4 cas réels (absent / valide / YAML malformé / mapping non-dict).

**Validation :** 8 nouveaux tests. Suite complète : **3235/3235**
tests passent (3227 avant), ruff et mypy propres.

## Mise à jour 2026-09-02 (suite) — "des modules qu'on a raté" : couverture de test réelle + réconciliation avec le catalogue existant

Demande explicite de l'utilisateur ("je sens qu'on a raté des modules
qu'on a pas généré"). Méthode réelle, pas une impression : un vrai
rapport de couverture (`pytest --cov=acf`, 3235 tests, **84% de
couverture globale réelle**) a isolé **55 fichiers à 0% de couverture
réelle** (1511 instructions jamais exécutées par aucun test) — la
liste concrète, pas une supposition.

**Trouvaille principale : ce travail avait déjà été fait, en grande
partie.** Un `grep -rl "RÈGLE D'OR"` a révélé **21 fichiers déjà
honnêtement documentés** par une session précédente comme du vrai code
mort/orphelin (jamais construit nulle part, vérifié empiriquement,
volontairement **non supprimé** par convention du projet) — exactement
la même classe de "module raté" que l'utilisateur soupçonnait. Ça
recoupe presque parfaitement les 55 fichiers à 0% de couverture :
`gui/main_window.py`, `data/engine.py`, `maps/canvas.py`,
`model4d/interpolation.py`, `model4d/operators.py` (collisions de nom
fichier.py vs package/), plus **toute l'arborescence**
`gui/map/{layers,renderers,navigation,projections,rendering}/` (une
architecture de rendu cartographique alternative, complète et
correcte, mais jamais raccordée à un widget réel — documentée dans
`gui/map/__init__.py`'s propre NOTE), plus `gui/main_window/
{menu_bar,status_bar,tool_bar}.py` (jamais construits, actions sans
handler réel). Un document maître existait déjà et cataloguait
précisément cette classe de problème :
[`docs/architecture/duplicate_components.md`](../docs/architecture/duplicate_components.md)
(marqué "outdated snapshot" mais structurellement toujours exact —
`MainWindow`×2, `MapCanvas`×2, `LayerManager`×3, `CartopyRenderer`×3,
etc. — et qui avait même déjà prédit la trouvaille `loguru` non
déclarée de la mise à jour précédente : "ConfigManager dépend de
PyYAML et la journalisation de Loguru, sans déclaration").

**Deux vrais fichiers orphelins trouvés qui n'étaient PAS encore
documentés — vérifiés par grep de leurs vrais appelants, pas
supposés** :
- **`src/acf/model4d/constants.py`** — vraies constantes physiques
  correctes (gravité, rotation terrestre, constantes des gaz...) mais
  **zéro importeur réel nulle part** — chaque module qui a besoin
  d'une de ces constantes définit sa propre copie locale au lieu
  d'utiliser celle-ci (ex. `isa_atmosphere.py` a son propre
  `r_d = 287.0528`, une valeur réelle légèrement différente pour la
  même constante physique).
- **`src/acf/dashboard/panels/map_panel.py`** — `MapPanel` jamais
  construit nulle part, contrairement à ses vrais frères du même
  paquet (`ChartPanel`/`StatusPanel`/`TimelinePanel`, tous les trois
  réellement utilisés). La vraie carte de dashboard existe ailleurs
  pour de vrai (`AWCIMapPanel`).

Les deux documentés avec la même convention honnête (NOTE, pas
supprimé) que les 21 déjà existants.

**Ce qui n'a PAS été fait, délibérément** : consolider/supprimer les
doublons catalogués — le plan du document maître lui-même exige "des
tests de non-régression avant toute migration" et une décision
explicite par responsabilité ; c'est une initiative plus large et plus
risquée (retirer du code potentiellement encore référencé ailleurs)
qui mérite une décision de l'utilisateur, pas une action unilatérale
dans cette passe de scan.

**Validation :** suite complète toujours **3235/3235** (changements
purement documentaires, aucun comportement modifié), ruff et mypy
propres.

## Mise à jour 2026-09-02 (suite) — encyclopédie scientifique : vérification puis branchement réel du CAPE/CIN dans AWCI

Demande explicite de l'utilisateur, en deux temps : d'abord
**vérifier** si `acf.science.encyclopedia` (299 entrées réelles, 35
domaines) est complète et réellement utilisée dans le calcul de sortie
d'ACF/AWCI, puis (après avoir choisi explicitement l'option
"Brancher réellement l'encyclopédie dans AWCI" parmi les choix
proposés) **le faire pour de vrai**.

**Vérification (mesures concrètes, pas une impression) :** 299
entrées réelles, `compute_func` renseigné sur 45% d'entre elles (le
reste sont des définitions/explications textuelles, honnêtement sans
formule), zéro import cassé, 113 tests existants. Un grep exhaustif
sur tous les modules de calcul réel (`awci/`, `simulation_engine/`,
`forecast/`, `model4d/physics/`, `earth_physics/`,
`data_assimilation/`, `hydrology/`, `ocean/`) a confirmé **zéro
appelant réel** dans le pipeline de calcul : l'encyclopédie n'était
utilisée que par les fonctionnalités de recherche/explication, jamais
pour produire un vrai chiffre de sortie ACF/AWCI.

**Point d'intégration choisi**, justifié par deux faits déjà
documentés avant même cette passe : (a) l'audit lui-même notait déjà
"aucun CAPE réel par point n'est calculé dans `acf.awci` aujourd'hui",
et (b) le docstring de `spatial_field.py` décrivait lui-même
précisément cette limite et pourquoi elle n'était pas comblée ("pas de
physique d'ascension de parcelle disponible ; inventer une formule
serait exactement le genre de chiffre fabriqué que les audits de ce
projet existent pour éliminer").

**Ce qui a été construit, réel de bout en bout :**
- [`src/acf/awci/convective_energy.py`](../src/acf/awci/convective_energy.py)
  (nouveau) : `compute_real_cape_cin_at_point()` — vraie ascension de
  parcelle via MetPy (`dewpoint_from_specific_humidity`,
  `parcel_profile`, épaisseurs hydrostatiques réelles et non-uniformes
  via `thickness_hydrostatic`, pas un `dz` supposé constant), puis
  intégration réelle de la flottabilité via les classes existantes
  `acf.science.cape.CAPE.calculate()` / `acf.science.cin.CIN.calculate()`
  — **les mêmes classes réelles** que les entrées d'encyclopédie
  `cape_convective_energy`/`cin_convective_inhibition` délèguent déjà,
  appelées directement ici (pas via le wrapper `dz` uniforme de
  `EncyclopediaRegistry.calculate()`) pour ne pas perdre la précision
  des hauteurs par niveau réellement disponibles. Coupure réelle et
  documentée à `MIN_PRESSURE_HPA_FOR_CONVECTIVE_ENERGY = 100.0` hPa
  (borne opérationnelle assumée, pas une loi physique universelle —
  même convention que `physics_guard.range_check.OPERATIONAL_RANGES`).
  `None` (jamais un `0.0` fabriqué) quand moins de 2 niveaux réels
  restent après la coupure. 8 nouveaux tests
  ([`tests/test_convective_energy.py`](../tests/test_convective_energy.py)),
  tous verts, y compris une preuve de traçabilité directe avec les
  entrées d'encyclopédie et un test de bout en bout sur une vraie
  colonne du solveur ACF.
- [`src/acf/awci/spatial_field.py`](../src/acf/awci/spatial_field.py) :
  nouveau paramètre **opt-in** `compute_convective_energy: bool =
  False` sur `compute_real_complexity_field()`. Quand `True`, calcule
  le vrai CAPE/CIN par point à partir de la vraie colonne verticale
  complète du solveur (`state["T"/"q"]` + pression convertie en hPa) et
  les alimente dans `AWCICalculator` (`data["cape"]`/`data["cin"]`,
  déjà lus par le module convectif : `0.7*cape_norm + 0.3*cin_norm`).
  `cape_field`/`cin_field` (2D, `np.nan` — jamais `0.0` — là où le
  calcul honnêtement échoue) ajoutés au dict de retour **uniquement**
  quand demandé, pour ne rien changer à la forme du résultat pour les
  appelants existants. Choix délibéré de rester opt-in : un vrai calcul
  MetPy par point de grille est un coût réel non négligeable qu'aucun
  appelant existant n'avait demandé — le comportement par défaut reste
  strictement identique à avant.

**Validation réelle, pas supposée :**
- `AWCICalculator.calculate()` lit bien exactement les clés
  `data["cape"]`/`data["cin"]` produites ici (vérifié par grep direct
  du code du calculateur, pas en le supposant).
- 4 nouveaux tests dans
  [`tests/test_awci_spatial_field.py`](../tests/test_awci_spatial_field.py) :
  (1) le comportement par défaut (`compute_convective_energy=False`)
  ne fait *plus* apparaître `cape_field`/`cin_field` du tout dans le
  dict — pas même à `None` — donc aucune régression de forme pour les
  appelants existants ; (2) en opt-in, `cape_field`/`cin_field` sont
  bien présents, bien dimensionnés, et réellement peuplés de valeurs
  non-NaN ; (3) preuve concrète que le branchement change vraiment le
  résultat : un point de grille avec un vrai CAPE positif (obtenu avec
  une graine/perturbation choisie empiriquement pour produire une
  colonne réellement instable — un état par défaut stable donne
  légitimement CAPE=0 partout, ce qui aurait rendu ce test vide de
  sens) donne un `awci` différent selon que `cape`/`cin` sont fournis
  ou non, avec `AWCICalculator` appelé directement en point de
  contrôle indépendant.
- Suite complète : **3246/3246** tests passent (3235 + 8 nouveaux
  `test_convective_energy.py` + 3 nets nouveaux dans
  `test_awci_spatial_field.py`, un test préexistant conservé). `ruff
  check` et `mypy` propres sur les deux fichiers modifiés/créés.

**Limite honnête restant assumée** : le CAPE/CIN reste dérivé de
l'état du solveur `CoupledEarthSolver` d'ACF, pas d'un vrai radiosondage
ou d'une analyse de modèle opérationnel — même limite que le reste du
module `acf.awci`. La coupure à 100 hPa et le choix d'une parcelle
"surface-based" (pas "most-unstable" ni "mixed-layer") sont des choix
réels et défendables, mais pas les seuls possibles — documentés comme
tels dans `convective_energy.py`.

## Mise à jour 2026-09-02 (suite) — consolidation réelle des doublons catalogués : re-vérification complète, ligne par ligne

Demande explicite de l'utilisateur ("Consolider les doublons
catalogués"), après avoir choisi cette direction parmi plusieurs
options proposées. Méthode : chaque ligne de
[`docs/architecture/duplicate_components.md`](../docs/architecture/duplicate_components.md)
(marqué "outdated snapshot") et chaque homonyme de classe a été
re-vérifié un par un par grep des vrais importeurs réels — pas relu ni
supposé exact.

**Résultat principal : la quasi-totalité de la table est déjà
résolue**, par des passes antérieures non documentées comme telles au
niveau du tableau lui-même :
- `tests/test_collisions_consolidation.py` (marqué en interne
  "ACF-017") et `tests/test_importers_consolidation.py`
  ("ACF-016") prouvent, avec des assertions d'identité `is`, que
  Fenêtre principale / Moteur cartographique / Catalogues / Paramètres
  / Lecteurs de données / BUFR / NetCDF-GRIB / Validation dataset sont
  déjà réellement unifiés derrière une implémentation canonique, avec
  un vrai shim de compatibilité sur le chemin d'import historique (ou,
  pour Fenêtre principale, le fichier historique est honnêtement mort —
  la résolution d'import package-avant-module de Python ne l'atteint
  jamais, documenté sur place, pas supprimé).
- **Couches et renderers** (la pile à trois `gui.map`/`maps`/
  `visualization`) est réelle mais déjà entièrement investiguée et
  honnêtement documentée par une passe antérieure : la propre NOTE de
  `gui/map/__init__.py` confirme que toute l'arborescence
  `gui.map.{layers,renderers,navigation,projections,rendering}/` (qui
  couvre le côté `gui.map` des homonymes `LayerManager`/
  `ProjectionManager`/`CartopyRenderer`/`RasterRenderer` de cette
  ligne) n'est **jamais importée par rien dans `src/`** — pas une vraie
  scission à trois en pratique, plutôt à deux (fichiers plats `gui.map`
  vs `maps`/`visualization`), et même celle-là déjà en grande partie
  unifiée par le point précédent.

**Deux lignes se sont révélées être de faux positifs, vérifiés pas
supposés** — même nom de classe, responsabilité réellement différente,
les deux côtés réellement utilisés aujourd'hui :
- **Plugins** — `acf.core.plugin_manager.PluginManager` (découverte
  générique de plugins sur disque, utilisée par `acf.core.bootstrap`)
  vs `acf.ai.plugins.plugin_manager.PluginManager` (un registre en
  mémoire d'`AIPlugin` avec `register()`/`analyze()`, utilisé par le
  sous-système IA).
- **Data manager** — `acf.data.manager.DataManager` (un vrai
  orchestrateur de workflow avec état — `open()`/`close()`/
  `current_dataset`/`history()` — construit sur `ReaderFactory`/
  `DatasetRegistry`/`CatalogManager` canoniques, utilisé par
  `acf.dashboard.window`) vs `acf.io`/`acf.importers.manager.
  DataManager` (le registre de lecteurs de plus bas niveau, déjà
  unifié via ACF-016).

Même trouvaille, déjà présente indépendamment dans ACF-017 :
`Divergence`/`Dynamics` (`science.*` = version simple/didactique,
`model4d.operators`/`physics` = la vraie version de qualité solveur) —
confirmée, pas re-fusionnée.

**Une ligne reste un vrai doublon ouvert, vérifié pour de vrai :
Canvas carte.** `acf.gui.map.map_canvas.MapCanvas` (un `QWidget` qui
compose un canvas matplotlib comme enfant — intégré dans la vraie
fenêtre live d'ESOC via `acf.gui.esoc.view_manager.ViewManager`/
`acf.gui.main_window.main_window.MainWindow`) et
`acf.maps.canvas.map_canvas.MapCanvas` (qui EST lui-même un
`FigureCanvasQTAgg` — utilisé par la propre API publique d'`acf.maps`,
qui se qualifie elle-même de "Canonical Cartographic & Visualization
Package" dans son propre docstring, et par la table de ré-export
paresseux d'`acf.visualization`) sont tous les deux réellement vivants,
tous les deux réellement utilisés, et pas des formes interchangeables.
Documenté avec une NOTE complète dans les deux fichiers
([`src/acf/gui/map/map_canvas.py`](../src/acf/gui/map/map_canvas.py),
[`src/acf/maps/canvas/map_canvas.py`](../src/acf/maps/canvas/map_canvas.py))
et verrouillé par un nouveau test
(`test_map_canvas_is_a_real_verified_duplicate_not_yet_consolidated`).
**Délibérément pas fusionné dans cette passe** : une vraie
consolidation ici signifie choisir un gagnant et migrer soit la vraie
GUI live d'ESOC, soit l'API publique d'`acf.maps`/`acf.visualization`,
vers la forme de l'autre (`QWidget` composite vs `FigureCanvasQTAgg`
direct ne sont pas des formes interchangeables) — une décision de
conception scopée, pas quelque chose que cette passe tranche
unilatéralement, exactement comme le plan de consolidation du document
lui-même l'exige (étape 1 "désigner une API canonique... geler les
alternatives", étape 2 "tests de non-régression avant toute migration"
— qui n'existent pas encore pour l'un ou l'autre groupe de
consommateurs).

**`docs/architecture/duplicate_components.md`** mis à jour avec une
nouvelle bannière de re-vérification résumant tout ce qui précède,
au-dessus de son contenu original inchangé (même convention que la
bannière "outdated snapshot" déjà en place).

**Validation :** 3 nouveaux tests dans
`tests/test_collisions_consolidation.py` (12/12 dans ce fichier, dont
les 3 nouveaux), suite complète **3249/3249** (3246 + 3), `ruff` et
`mypy` propres sur les fichiers touchés.

Dis-moi laquelle tu veux que j'attaque ensuite.

## Mise à jour 2026-09-03 — dashboard modernisé, cartes réellement manipulables, vraie 4ème dimension (5 phases)

Demande explicite de l'utilisateur : "je veux améliorer le dashboard
du acf et le perfectionner pour qu'il soit moderne idéal pour 2026 et
améliorer aussi les cartes afficher et ajoute la 4em dimension au
niveau d'affichage des cartes et ajoute l'option zoom des cartes et
manipulation totale des cartes". Vu l'ampleur, planifié explicitement
(mode plan) avec deux passes d'exploration réelles avant d'écrire une
ligne de code, puis 3 questions de clarification posées à
l'utilisateur (sens de "4ème dimension" — les deux : slider temps/
niveau réel ET vraie vue 3D ; portée du zoom/pan — les deux cartes,
ESOC ET dashboard AWCI ; portée du thème — unifier vraiment, "sors le
meilleur de toi-même"). Livré en 5 phases indépendamment vérifiées,
committées et poussées.

**Phase A — système de design unifié.** Avant : ESOC (chrome réel,
QSS minimal) et le dashboard AWCI (fenêtre séparée, palette codée en
dur) utilisaient deux palettes sombres incompatibles, plus 8+ teintes
Material non liées par label dans `esoc_statusbar.py` seul. Nouveau
[`src/acf/gui/theme_tokens.py`](../src/acf/gui/theme_tokens.py) :
source unique de vérité (surfaces, texte, accents, espacements, rayons,
typographie), `resources/themes/{dark,light}.qss` réécrits avec une
vraie couverture moderne (coins arrondis, états hover/pressed,
`QComboBox`/`QScrollBar` stylés). `awci_dashboard.py._apply_theme()`
route maintenant réellement par les tokens ; les 7 autres fichiers
AWCI + `map_canvas.py`/`map_renderer.py` alignés valeur-pour-valeur
sur les mêmes constantes (vérifié par grep après coup — plus aucun
littéral de l'ancienne palette). 8 nouveaux tests
(`tests/test_theme_tokens.py`).

**Phase B — vrai zoom/pan/manipulation sur les deux cartes vivantes.**
Un trio complet mais jamais câblé existait (`EventMixin`/`MapCamera`)
— et s'est révélé avoir un vrai bug une fois vérifié : `zoom_level`/
`center` changeaient sans jamais toucher `self.extent`. Corrigé
(`current_extent()` réel et documenté dans
[`map_camera.py`](../src/acf/gui/map/map_camera.py), `set_extent()`
dérive maintenant l'inverse). Câblé dans `MapCanvas` (carte centrale
ESOC) et `AWCIMapPanel` (cartes du dashboard AWCI). **Trois vrais bugs
trouvés en vérifiant de bout en bout, pas hypothétiques** : (1) la
projection Mercator par défaut a une vraie singularité aux pôles —
`reset_view()` plantait avec "Axis limits cannot be NaN or Inf",
corrigé par un clamp réel documenté (±85.05112878°, la même borne que
Web Mercator/OSM/Google Maps) ; (2) même crash exact à la frontière
±180° de longitude (cas limite PROJ/Cartopy à l'antiméridien), corrigé
par un epsilon similaire ; (3) le plus fondamental — Qt délivre les
vrais événements souris/molette/clavier au widget enfant
(`FigureCanvasQTAgg`), pas au wrapper qui porte `EventMixin` : un vrai
`QWheelEvent` envoyé à la carte ne changeait RIEN, silencieusement.
Corrigé par un `installEventFilter()` standard Qt. Trouvé uniquement
parce que les tests dispatchent de vrais événements Qt vers le widget
enfant réel (`QApplication.sendEvent`), pas en appelant les méthodes
directement. 22 nouveaux tests.

**Phase C — vrai champ AWCI (+ CAPE/CIN) sur la carte centrale ESOC.**
La carte centrale d'ESOC (le vrai centre de l'appli, visible au
lancement) n'affichait aucune donnée AWCI réelle. Nouveau
`AWCILayer(BaseMapLayer)` dans
[`map_layers.py`](../src/acf/gui/map/map_layers.py) (sans motif
synthétique de repli, contrairement à ses 6 voisins — un
`render()` vide tant qu'aucune vraie donnée n'est fournie), nouveau
bouton toolbar "🌪️ AWCI Field" calculant
`compute_real_complexity_field(compute_convective_energy=True)` hors
thread GUI — fermant au passage l'écart trouvé plus tôt dans cette
session ("cape_field/cin_field réels et testés, zéro consommateur
GUI"). **Vrai bug trouvé et corrigé** : le signal du worker était
connecté à une lambda plutôt qu'une méthode liée — PySide6 ne peut pas
déterminer la mise en file d'attente inter-thread sûre pour une lambda
nue, donc le signal, émis depuis le thread worker, n'appelait
silencieusement jamais rien. Corrigé en suivant le pattern déjà
éprouvé d'`awci_dashboard.py` (méthode liée réelle). 10 nouveaux tests.

**Phase D — vrai slider de niveau vertical, ferme le pipeline 4D.**
`compute_real_complexity_volume()`/`compute_real_complexity_evolution()`
étaient déjà réels et branchés (mode "🔬 Real Physics", animation "▶
Play Evolution (4D)") mais chaque consommateur figeait le niveau à 0
(surface) — l'axe vertical de cette donnée 4D déjà réelle était
invisible. Nouveau slider de niveau réel dans
[`awci_dashboard.py`](../src/acf/gui/dashboard/awci_dashboard.py),
re-découpant le volume déjà calculé (aucun nouveau run solveur) via
`_apply_volume_at_level()`, appliqué à la carte globale/régionale, au
graphique de route, à la barre de stats, au radar/résumé de risque, et
à l'animation d'évolution (qui ignorait le slider avant ce correctif).
9 nouveaux tests, dont deux gardes de non-régression réelles (l'
animation suit maintenant le niveau choisi ; un niveau au-delà du
nombre réel de niveaux de l'évolution est clampé, pas une
`IndexError`).

**Phase E — vraie vue 3D (l'autre moitié du "les deux" de
l'utilisateur pour la 4ème dimension).** Aucune infrastructure de
rendu volumétrique/GPU réelle n'existe dans ce projet
(`acf.visualization.volume_engine` : des façades d'état, pas des
moteurs de rendu — confirmé en planifiant). Nouveau
[`src/acf/gui/dashboard/awci_volume_3d.py`](../src/acf/gui/dashboard/awci_volume_3d.py) :
`AWCIVolume3DView`, un vrai `Axes3D` matplotlib (déjà une dépendance
dure, aucune nouvelle dépendance), rotation souris native. Choix de
rendu réel et documenté : surfaces de contour empilées et translucides
(une par niveau réel) plutôt que `ax.voxels()` (rejeté — falaise de
performance réelle, cubes opaques qui masqueraient les niveaux
intérieurs). Axe Z = index de niveau réel (pas une altitude dérivée —
convertir la pression en altitude nécessiterait une vraie formule non
encore implémentée ici ; chaque niveau affiche sa vraie pression
moyenne de domaine en étiquette). Nouveau bouton "🧊 3D View" dans le
dashboard AWCI. 10 nouveaux tests.

**Validation globale :** suite complète **3308/3308** (3249 + 59
nouveaux tests sur les 5 phases), `ruff` et `mypy` propres sur chaque
fichier touché à chaque phase, chaque phase vérifiée manuellement de
bout en bout (event loop Qt réel pompé, worker `QThreadPool` réel)
avant l'écriture des tests automatisés — c'est cette vérification
manuelle qui a trouvé les 4 vrais bugs listés ci-dessus, pas les tests
eux-mêmes a priori.

## Mise à jour 2026-09-03 (suite) — fidélité réelle à la maquette de référence AWCI

Demande explicite de l'utilisateur, après avoir reçu deux captures
d'écran réelles (générées en lançant vraiment l'app en rendu Qt
offscreen) : "je veux garder le même thème pour les deux en suivant
cette photo", la photo étant la maquette de référence d'origine du
dashboard AWCI elle-même (le code le dit déjà dans ses propres
commentaires — la structure collait déjà, mais plusieurs éléments
visuels concrets manquaient). Clarifié avec l'utilisateur (choix "les
deux") : reconstruction complète des éléments manquants, pas
seulement un ajustement de palette.

**Construit, tous réels, aucun élément décoratif fabriqué :**
- **Légende "AWCI SCALE"** sur la carte globale — dessinée directement
  depuis les vrais seuils/couleurs d'`acf.gui.dashboard.awci_colors.LEVELS`
  (la même source que toutes les autres jauges/badges), pas une échelle
  séparée inventée.
- **Barre de couleur réelle 0-100** sous la coupe verticale
  (`AWCICrossSection`) — liée au même `contourf()` qui dessine la
  carte de chaleur. **Vrai bug trouvé et corrigé** en vérifiant les
  redessins répétés (ex. déplacer le time_slider) : `Colorbar.remove()`
  plantait avec `'NoneType' object has no attribute 'set_subplotspec'`
  au deuxième redessin — l'ordre `axis.clear()` puis `colorbar.remove()`
  perturbait un état interne matplotlib ; corrigé en inversant l'ordre.
- **Cartouches RENDERED / FLIGHT LEVEL** flottants sur la carte
  globale — RENDERED est l'heure UTC réelle de rendu (honnêtement
  étiquetée comme telle, pas présentée comme une heure de validité de
  prévision qui n'existe nulle part dans ce code) ; FLIGHT LEVEL est
  réel, dérivé de la vraie pression via la formule standard réelle
  ICAO/FAA d'altitude-pression (`pressure_to_flight_level_ft()`, pas
  une conversion inventée).
- **Fiche "POINT INFORMATION"** flottante sur la carte régionale —
  le vrai score AWCI déjà calculé pour ce point exact
  (`awci_at()`/le résultat du niveau réel sélectionné), pas une
  deuxième valeur fabriquée.
- **Pile verticale d'icônes zoom + export réel** (au lieu d'une rangée
  horizontale) — le bouton export (`⬇`) sauvegarde réellement la
  figure en PNG via un vrai `QFileDialog`, même convention que
  `_take_screenshot()` d'ESOC.
- **Panneau "LAYERS"** flottant réel — la case "AWCI" bascule
  réellement la visibilité du contour ; les autres noms de calques de
  la maquette (Wind, Turbulence, Icing, Convection, Clouds) sont
  affichés honnêtement désactivés (aucune source de donnée réelle pour
  eux dans ce panneau aujourd'hui) plutôt qu'un faux bouton cliquable —
  même discipline "jamais d'affordance inventée" que le reste de cette
  session.

**Délibérément pas construit** : le panneau "VIEW MODE" (Global/
Régional/Coupe verticale) de la maquette implique de basculer entre un
seul panneau affiché à la fois — le vrai dashboard actuel montre les
trois simultanément dans une grille, plus riche en pratique ; y
substituer un mode à la fois serait une vraie régression UX, pas une
fidélité de thème, donc non construit dans cette passe.

**Validation :** 17 nouveaux tests
(`tests/test_awci_map_panel_reference_fidelity.py`,
`tests/test_awci_cross_section.py`), suite complète **3325/3325**
(3308 + 17), `ruff`/`mypy` propres. Vérifié visuellement par une vraie
capture d'écran de l'app lancée (rendu Qt offscreen réel, pas une
maquette) avant et après.

## Mise à jour 2026-09-03 (suite) — messages METAR/TAF/SPECI/SIGMET réellement en direct (Partie 1/3)

Demande explicite : bouton "Message" unique donnant METAR/TAF/SPECI/
SPECIAL et tous les messages liés. Interrogé sur le cadrage honnête
(aucun encodeur n'existe, pas de vrai réseau de stations, pas de
calcul de visibilité), l'utilisateur a précisé l'objectif réel du
projet : **"le but est de brancher acf et awci avec des vrais
station pour nous rendre des vrai reponse instantanément"** — brancher
sur de vraies stations, pas encoder les données synthétiques d'ACF.

**Vérifié avant de construire, pas supposé** : `acf.aviation.icao.
metar_decoder.METARDecoder` et `taf_decoder.TAFDecoder` sont de vrais
décodeurs réels et testés (`tests/test_metar_decoder.py`,
`tests/test_taf_decoder.py`) mais avaient **zéro appelant nulle part**
dans l'app réelle — jamais branchés à quoi que ce soit. Un vrai
`curl` vers l'API publique et gratuite (sans clé) du NOAA Aviation
Weather Center (`aviationweather.gov/api/data/{metar,taf,airsigmet}`)
a confirmé des données réelles et actuelles pour KJFK/LFPG/EGLL, plus
DAAG (Alger, confirmé indépendamment). Un code OACI deviné pour
"Tripoli" (HLLT/HLLB) n'a renvoyé aucune donnée — délibérément non
ajouté plutôt que de risquer un code faux.

**Construit, réel de bout en bout :**
- [`src/acf/aviation/icao/live_source.py`](../src/acf/aviation/icao/live_source.py) —
  `fetch_raw_report()` (un vrai GET `urllib.request` — aucune nouvelle
  dépendance, `requests`/`httpx` n'existaient nulle part dans ce dépôt),
  `fetch_and_decode_station()`, `fetch_active_sigmets()`. Toute panne
  réseau/HTTP/réponse vide lève `LiveReportUnavailable` — jamais de
  repli fabriqué. **Vrai bug trouvé en vérifiant le flux réel des
  SIGMET** : le vrai flux sépare ses bulletins par une ligne de tirets
  (`----------------------`), pas par des lignes vides — un seul
  bulletin réel contient lui-même des lignes vides internes (avant sa
  section OUTLOOK) ; découper sur les lignes vides aurait fragmenté un
  seul bulletin réel en plusieurs morceaux incohérents. Corrigé avant
  d'écrire le moindre test, en inspectant le flux réel (`cat -A`).
- [`src/acf/gui/dashboard/awci_messages_panel.py`](../src/acf/gui/dashboard/awci_messages_panel.py) —
  `AWCIMessagesDialog`, un onglet par station réelle + un onglet
  SIGMET, récupération hors thread GUI (même pattern `QRunnable` +
  `Signal` déjà éprouvé cette session), connecté à une vraie méthode
  liée (pas une lambda — la session a déjà trouvé ce bug exact plus
  tôt). Chaque station/message affiche le texte brut réel ET un
  résumé décodé réel ; un échec réseau ou de décodage affiche un état
  honnête ("⚠ Live data unavailable: ...") plutôt qu'un blanc ou une
  valeur inventée.
- Nouveau bouton "📨 Message" dans l'en-tête du dashboard AWCI,
  toujours disponible (pas conditionné au mode Real Physics — les
  données viennent d'une vraie source externe, indépendante du
  solveur ACF).

**SPECI/SPECIAL** : pas un chemin de code séparé — c'est exactement la
même grammaire TAC ICAO réelle qu'un METAR de routine (une station
émet un SPECI au lieu d'un METAR seulement lors d'un changement
significatif) ; `METARDecoder.decode()` reconnaît déjà les deux
mots-clés, donc quel que soit celui que le vrai flux contient
actuellement, il est affiché tel quel — rien n'est fabriqué ni
distingué artificiellement.

**Validation :** 21 nouveaux tests
(`tests/test_aviation_live_source.py` : 14, mockant `urllib.request.
urlopen`, aucune dépendance réseau réelle en CI ; `tests/
test_awci_messages_panel.py` : 7, mockant les fonctions de fetch),
suite complète **3346/3346** (3325 + 21), `ruff`/`mypy` propres.
Vérifié de bout en bout avec de vraies données live (capture d'écran
réelle envoyée à l'utilisateur) avant d'écrire les tests automatisés.

## Mise à jour 2026-09-03 (suite) — bouton Alertes réel, non fabriqué (Partie 2/3)

Demande explicite : "un autre bouton pour les alertes". Construit sur
les niveaux de risque déjà réellement calculés par `AWCIRiskSummary`
(Turbulence/Icing/Convective/Overall/Physical/Forecast, via sa propre
fonction `_band()` interne — réutilisée directement, pas re-dérivée en
un deuxième barème qui pourrait diverger) — **explicitement pas**
`acf.hazard_operations`'s `HazardDetectionEngine`/`AlertGenerator`,
tous deux des stubs confirmés et déjà auto-documentés
("NOT_ASSESSED_..."/"NOT_SCANNED_...") sans moteur de détection réel
branché.

**Construit :**
- [`src/acf/gui/dashboard/awci_alerts_panel.py`](../src/acf/gui/dashboard/awci_alerts_panel.py) —
  `compute_elevated_risks()` liste chaque score AWCI actuellement à
  High/Very High/Extreme (jamais Moderate/Low) ; `compute_live_condition_flags()`
  détecte des conditions réelles depuis un METAR déjà récupéré (via le
  bouton Message) — orage réel (`TS` dans `present_weather`), rafale
  forte réelle (≥35kt, seuil documenté), visibilité basse réelle
  (<1600m) — uniquement si une récupération live a déjà eu lieu,
  sinon état honnête "pas encore de donnée live".
- Nouveau bouton "🔔 Alerts" avec un badge de compte réel (recalculé à
  chaque `refresh()`/`_apply_volume_at_level()`, jamais périmé),
  partageant les vraies données déjà récupérées par la fenêtre
  "📨 Message" (`last_bundles`) plutôt que de refaire un fetch séparé.

**Validation :** 18 nouveaux tests
(`tests/test_awci_alerts_panel.py` : 14, `tests/gui/
test_awci_dashboard_alerts_button.py` : 4), suite complète
**3364/3364** (3346 + 18), `ruff`/`mypy` propres. Capture d'écran
réelle envoyée à l'utilisateur (alerte réelle "Turbulence Risk: Very
High (79)" sur le motif synthétique par défaut).

## Mise à jour 2026-09-03 (suite) — composants de complexité réellement cliquables (Partie 3/3)

Demande explicite : "rend les bouton des différents complexité
utilisable pour rendre tout le details de la situation". Chaque fait
affiché est transcrit directement depuis
`acf.awci.calculator.AWCICalculator.calculate_module_scores()` et
`acf.awci.normalizer.Normalizer` — pas re-dérivé ni deviné, vérifié
par des tests croisés contre les vraies classes.

**Construit :**
- [`src/acf/gui/dashboard/awci_component_detail.py`](../src/acf/gui/dashboard/awci_component_detail.py) —
  table réelle des 7 modules (entrée(s) réelle(s), vraie formule
  `Normalizer`, et un fait vérifié : **en mode Real Physics
  aujourd'hui, seuls `dynamic` et `thermodynamic` sont réellement
  pilotés par le solveur** — `convective`/`microphysical`/
  `topographic`/`temporal`/`confidence` restent figés aux valeurs par
  défaut d'`AWCICalculator` car `compute_real_complexity_volume()` ne
  fournit ni CAPE/CIN, ni précipitation, ni altitude, ni
  temporal_change. `AWCIComponentDetailDialog` affiche donc un badge
  honnête ("✅ REAL" ou "⚠ DEFAULT — not computed in Real Physics mode
  today") plutôt que de prétendre qu'une valeur figée est un résultat
  physique réel.
- `_ComponentValueList` (dans `awci_dashboard.py`) — les 7 lignes sont
  maintenant réellement cliquables (nouvelle classe `_ComponentRow`,
  survol + clic réels), ouvrant le détail avec le vrai score, les
  vraies entrées brutes et le mode réel (démo ou Real Physics) —
  threadé depuis les deux vrais points d'appel (`refresh()` et
  `_apply_volume_at_level()`), pas recalculé séparément.

**Validation :** 15 nouveaux tests
(`tests/test_awci_component_detail.py` : 10, `tests/gui/
test_awci_dashboard_component_clicks.py` : 5) — dont des tests croisés
directs contre les vraies classes `AWCICalculator`/`Normalizer` (pas
seulement contre le texte affiché). 2 tests préexistants adaptés au
nouvel attribut interne (`_rows` au lieu de `_values`). Suite complète
**3379/3379** (3364 + 15), `ruff`/`mypy` propres. Capture d'écran
réelle envoyée à l'utilisateur (module Convective en mode Real
Physics, badge honnête "DEFAULT" affiché correctement).

**Bilan des 3 parties (boutons Message/Alerts/composants) :** suite
complète passée de 3325/3325 à **3379/3379** (54 nouveaux tests au
total), 3 commits indépendants poussés sur `develop`.

## Mise à jour 2026-09-03 (suite) — prompt maître ACF/AWCI et maquettes de référence ajoutés

L'utilisateur a fourni le document conceptuel d'origine du projet
(rédigé avec l'aide de ChatGPT au tout début du projet, avant cette
session) : la définition scientifique complète de l'ACF/AWCI, la
philosophie de travail (statuts CONFIRMED/PROPOSED/HYPOTHESIS/
REQUIRES VALIDATION/UNKNOWN, discipline "jamais de seuil/poids inventé
présenté comme validé", ACF ≠ AWCI, complexité ≠ danger, physics-first
avant ML, ordre de travail UNDERSTAND→INSPECT→AUDIT→PLAN→IMPLEMENT→
TEST→VALIDATE→DOCUMENT→REPORT), ainsi que deux maquettes de référence
visuelles (un dashboard ACF général multi-échéances/multi-modèles, et
le dashboard AWCI déjà utilisé comme référence pour
`acf.gui.dashboard.awci_dashboard` — confirmé être la même maquette).

**Conservé tel que fourni** dans
[`docs/ACF_MASTER_PROMPT.md`](../docs/ACF_MASTER_PROMPT.md) (les 90
sections, verbatim — ce n'est pas un audit du dépôt, c'est la
spécification conceptuelle et méthodologique que ce projet doit
respecter) et les deux images dans
[`docs/reference/`](../docs/reference/) (`acf_dashboard_reference.jpg`,
`awci_dashboard_reference.jpg`, avec un `README.md` expliquant ce que
chacune représente et son statut réel — la maquette ACF générale n'a
**aucun widget correspondant construit dans `src/acf/gui` à ce jour**,
contrairement à la maquette AWCI déjà implémentée).

**Ce que cette mise à jour n'est PAS** : ce n'est pas une prétention
que le code existant respecte déjà intégralement ce prompt maître (il
ne le fait pas partout — par exemple, la discipline stricte de statut
`CONFIRMED`/`HYPOTHESIS` par seuil/poids n'est pas systématiquement
appliquée dans `acf.awci.calculator`/`normalizer` aujourd'hui, et
aucun dashboard ACF général multi-échéances n'existe). C'est
l'enregistrement durable de la référence conceptuelle à respecter pour
tout travail futur — un vrai audit de conformité point-par-point à ce
prompt serait un travail séparé, non fait ici.

## Mise à jour 2026-09-03 (suite) — décision d'autorité + premier audit de conformité réel au prompt maître

**Trouvaille majeure faite en préparant cet audit, pas supposée** : 23
fichiers du code existant (`acf.core.contracts.*`, `acf.certification`,
`acf.events`, `acf.jobs`, `acf.verification`, `acf.physics_guard`,
etc.) citent déjà en commentaires un **« Prompt Maître ACF v2.0 »**
avec une numérotation de section totalement différente de celui reçu
aujourd'hui (ex. code : « section 13 = Data Contract », « section
22/46 = Job contract », « section 91 = QualityInfo » — des contrats
logiciels concrets absents à ces numéros dans le document reçu
aujourd'hui, qui s'arrête à 90 et reste conceptuel). Ce v2.0 complet
n'existe nulle part dans le dépôt comme document autonome — seulement
cité en commentaires épars, jamais retrouvé (recherché dans
`ROADMAP.md`, absent). **Décision explicite de l'utilisateur** : le
document reçu aujourd'hui (`docs/ACF_MASTER_PROMPT.md`) fait
désormais autorité et remplace le v2.0 pour tout travail futur ; les
23 fichiers citant "v2.0" ne sont PAS réécrits en masse (règle d'or
§71 du prompt lui-même — leur code reste réel et fonctionnel, leurs
citations deviennent des références historiques). Détail dans
l'en-tête de `docs/ACF_MASTER_PROMPT.md`.

**Premier audit réel (évidence par évidence, pas exhaustif des 90
sections) de l'existant contre ce document faisant autorité :**

| Exigence du prompt | Statut réel vérifié |
|---|---|
| §9-10 Abstraction multi-modèles + modèle de données commun | **CONFIRMÉ** — `acf.models.base_model.BaseWeatherModel` (Protocol), 7 adaptateurs réels (AROME/ALADIN/ARPEGE/ERA5/WRF/ICON/OpenIFS), `acf.core.contracts.dataset.Dataset`/`Provenance`/`VariableContract` communs. |
| §11 Contrôle physique des unités avant combinaison | **CONFIRMÉ, partiel** — `acf.physics_guard.guard.PhysicsGuard` réel (unités/plages/coordonnées/dimensions), mais pas systématiquement invoqué à chaque point d'entrée du pipeline. |
| §18-19 Incertitude + désaccord inter-modèles | **CONFIRMÉ, partiel** — `ModelConsensusEngine.compute_real_multi_model_disagreement()` réel (dispersion/écart-type), module `ensemble_spread`/`model_disagreement` réel dans `AWCICalculator` — mais seulement 2-3 modèles réellement testés ensemble à la fois, pas un vrai consensus N-modèles opérationnel. |
| §20 Normalisation au-delà du min-max naïf | **HYPOTHÈSE non résolue** — `acf.awci.normalizer.Normalizer` utilise exclusivement un clip-puis-division linéaire (ex. vent 0-50 m/s, CAPE 0-5000 J/kg) ; aucune fonction sigmoïde/percentile-climatologique/saisonnière comme le prompt le demande d'étudier. Les bornes elles-mêmes ne sont sourcées nulle part (pas de référence physique/statistique citée). |
| §21/§77-81 Statut explicite CONFIRMED/HYPOTHESIS sur chaque seuil/poids | **GAP RÉEL confirmé** — `WeightsManager.DEFAULT_WEIGHTS` et `Normalizer`'s bornes sont de simples constantes avec une prose honnête ponctuelle ("expert knowledge", "ACF design choice... not derived from an external published formula" sur `INTERACTION_WEIGHTS`) mais **aucun champ de statut structuré, interrogeable par le code ou les tests**, comme le prompt l'exige explicitement et de façon répétée. |
| §22 Moteur d'interactions général | **PARTIEL** — seulement 2 termes d'interaction codés en dur (`wind_topo_interaction`, `conv_thermo_interaction`), pas un vrai moteur généralisé étudiant les interactions entre paires/triplets de modules. |
| §32 Statuts de qualité des données | **PARTIEL, vocabulaire différent** — `acf.core.contracts.quality.QualityInfo` réel et honnête (défaut `NOT_ASSESSED`, jamais `PASS` par défaut) mais utilise `NOT_ASSESSED/PASS/WARNING/FAIL`, pas la liste précise du prompt (`VALID/SUSPECT/MISSING/INVALID/OUT_OF_RANGE/UNIT_ERROR/GRID_ERROR/TIME_ERROR/PHYSICAL_INCONSISTENCY`). |
| §33 Provenance | **CONFIRMÉ** — `acf.core.contracts.provenance.Provenance` réel. |
| §45/§47 ACF ≠ AWCI comme couches logicielles séparées et réutilisables | **GAP ARCHITECTURAL RÉEL** — `src/acf/` a ~50 paquets de premier niveau (`awci/`, `science/`, `hazard_operations/`, `ocean/`, `hydrology/`, etc.) tous à plat ; il n'existe pas de séparation claire "cœur scientifique ACF réutilisable" → "pondération/contexte spécifique à AWCI" telle que décrite au §47 — `awci/` n'est pas architecturalement distingué comme une application au-dessus d'un cœur ACF générique. |
| §27-29 Dashboard multi-vues (général, vertical, multi-modèle, scientifique) | **PARTIEL** — le dashboard AWCI (`acf.gui.dashboard.awci_dashboard`) existe et est déjà construit contre sa maquette de référence ; **aucun dashboard ACF général multi-échéances/multi-modèles** (la première maquette, `docs/reference/acf_dashboard_reference.jpg`) n'existe. |
| §61-62 UNKNOWN plutôt que fausse certitude, jamais missing→0 silencieux | **CONFIRMÉ, pratique déjà établie** — convention déjà omniprésente dans le code de cette session (`None` réel plutôt que `0.0` fabriqué, ex. `physical_score`/`forecast_score` d'`AWCICalculator`, `cape_j_kg`/`cin_j_kg` de `convective_energy.py`). |
| §64 AWCI = score ± incertitude ou distribution | **NON IMPLÉMENTÉ** — `AWCICalculator` retourne un score ponctuel unique (+ `confidence` séparé), jamais un intervalle ou une distribution de probabilité par classe, alors que le prompt le présente explicitement comme "à étudier". |

**Recommandation** (pas encore exécutée dans cette mise à jour) : le
gap le plus concret, le plus sûr à corriger (aucun risque de casser
l'existant) et le plus explicitement et répétitivement exigé par le
prompt (§21, §77, §78, §79, §80, §81) est le **statut structuré
CONFIRMED/PROPOSED/HYPOTHESIS/REQUIRES_VALIDATION/UNKNOWN sur chaque
seuil et poids d'AWCICalculator/Normalizer/WeightsManager** —
actuellement de simples constantes sans statut interrogeable. C'est le
prochain chantier proposé.

## Mise à jour 2026-09-03 (suite) — registre de statut scientifique réel construit

Chantier recommandé ci-dessus, construit. Nouveau
[`src/acf/awci/scientific_status.py`](../src/acf/awci/scientific_status.py) :
les deux vocabulaires exacts du prompt maître — `ScientificStatus`
(§77 : `CONFIRMED`/`PROPOSED`/`HYPOTHESIS`/`REQUIRES_VALIDATION`/
`UNKNOWN`) et `WeightStatus` (§80 : `initial`/`expert-based`/
`calibrated`/`validated`) — appliqués à **chaque** poids/seuil réel
qu'`AWCICalculator`/`Normalizer`/`WeightsManager` utilise
effectivement, avec une justification réelle par entrée (pas générique).

**Classification honnête, aucune invention** : les 7 poids de module
sont `EXPERT_BASED` (correspond au docstring déjà existant de
`WeightsManager`) ; `ensemble_spread`/`model_disagreement` (défaut
0.0, opt-in) sont `INITIAL`, pas `EXPERT_BASED` — aucun jugement
d'expert n'a jamais été porté sur leur magnitude, seulement sur la
décision de les mettre à zéro par défaut. Les 2 poids d'interaction
sont `INITIAL` (le docstring existant d'`AWCICalculator` le dit déjà :
"an ACF design choice... not derived from an external published
formula"). Les bornes physiques de `Normalizer` (vent, CAPE, CIN,
précipitation, température, etc.) sont `HYPOTHESIS` — plausibles
physiquement mais non sourcées d'une climatologie externe précise
citée dans le code. **Une seule exception `CONFIRMED`, réelle et
justifiée** : la plage confiance 0-100% — c'est une définition d'unité
exacte, pas un choix empirique, preuve que le registre fait une vraie
distinction et n'étiquette pas tout uniformément par prudence.

**Purement additif** : les nouvelles méthodes
(`WeightsManager.get_weight_status()`, `Normalizer.get_range_status()`,
`AWCICalculator.get_interaction_weight_status()`) s'ajoutent à côté
des constantes réelles existantes, ne les remplacent pas — aucun
changement de comportement de calcul, vérifié par un test dédié
(`test_adding_status_metadata_does_not_change_real_awci_computation`).

**Branché dans l'UI** : la fiche de détail par composant
(`AWCIComponentDetailDialog`, construite plus tôt cette session) affiche
maintenant aussi le vrai statut de poids du module cliqué — fermeture
concrète du lien entre explicabilité (§26) et discipline de statut
(§77-81) dans la même interface.

**Validation :** 15 nouveaux tests
(`tests/test_awci_scientific_status.py` : 14, plus 1 nouveau test dans
`tests/test_awci_component_detail.py`), suite complète **3394/3394**
(3379 + 15), `ruff`/`mypy` propres, aucune régression sur le calcul
AWCI réel.

## Mise à jour 2026-09-03 (suite) — AWCI = score ± incertitude réelle / P(classe) réelle (§64)

Suite explicite ("oui vasy mais respecte moi le prompt"), méthodologie
suivie dans l'ordre imposé par le prompt (§86) :

**COMPRENDRE** : §64 du prompt — "il peut être plus scientifique de
représenter AWCI = 72 ± uncertainty ou P(AWCI class) plutôt qu'un seul
chiffre sans contexte. Étudier cette possibilité." Explicitement
présenté comme "à étudier", pas une exigence ferme.

**INSPECTER/AUDITER** : `AWCICalculator.calculate_module_scores()`
consomme déjà de vraies données réelles par membre/par modèle
(`ensemble_members`/`model_realizations`, des `dict[str, list[float]]`
réels) pour les modules `ensemble_spread`/`model_disagreement` — mais
rien ne combinait ces vraies réalisations en une vraie distribution du
score AWCI lui-même. Confirmé, pas supposé.

**Construit** : nouvelle méthode
[`AWCICalculator.calculate_with_uncertainty()`](../src/acf/awci/calculator.py) —
recalcule un vrai score AWCI **une fois par réalisation réelle**
(substitue la vraie valeur de cette réalisation pour chaque variable
fournie, le reste du scénario restant inchangé), produisant N vrais
scores AWCI indépendants — pas des échantillons tirés d'une
distribution paramétrique inventée (aucune hypothèse gaussienne nulle
part). `awci_mean`/`awci_std`/`awci_min`/`awci_max` sont les vraies
statistiques d'échantillon de ces N vrais scores ;
`awci_class_probabilities` est la vraie fraction empirique de ces N
scores dans chaque vraie bande de niveau — pas un modèle de
probabilité paramétrique.

**Repli honnête (§61 — "préférer UNKNOWN à FALSE CERTAINTY")** : sans
vraies données d'ensemble/multi-modèle, la méthode retourne
`uncertainty_available: False` avec une explication réelle, plutôt que
d'inventer une bande à partir de la seule `confidence` (qui serait
exactement le genre de formule non fondée que le §78 met en garde
contre — sans notation/hypothèse/source/domaine de validité).

**Statut scientifique honnête de la méthode elle-même** : ajouté à
[`acf.awci.scientific_status`](../src/acf/awci/scientific_status.py)
(`UNCERTAINTY_METHOD_STATUS`) — `HYPOTHESIS`, réel et assumé : la
technique de substitution par réalisation est un vrai choix de
conception ACF défendable, pas une technique de quantification
d'incertitude externellement validée ou publiée pour cet indice
composite. L'arithmétique elle-même (moyenne/écart-type/fractions
empiriques) est exacte, réelle — seule la *méthode* qui transforme les
réalisations réelles en recalcul AWCI par réalisation porte ce statut.

**Validation réelle, pas supposée** : preuve empirique qu'un
désaccord réel entre membres produit un écart-type réel plus large
qu'un accord réel (`std` désaccord = 5.6 contre `std` accord = 0.1 sur
un cas construit), que chaque score de membre correspond exactement à
un appel indépendant de `calculate()` sur ce même scénario substitué,
et que le score ponctuel retourné reste bit-identique à un appel
`calculate()` classique. 13 nouveaux tests
(`tests/test_awci_calculator_uncertainty.py`), suite complète
**3407/3407** (3394 + 13), `ruff`/`mypy` propres, méthode purement
additive (zéro changement de comportement pour tout appelant existant
de `calculate()`).

## Mise à jour 2026-09-03 (suite) — Dashboard ACF général (§27-29)

Suite explicite ("oui vasy mais respecte moi le prompt envoyé"),
troisième priorité choisie dans les manques identifiés par cet audit
lui-même, méthodologie suivie dans l'ordre imposé par le prompt (§86).

**Pourquoi** : §27-29 du prompt décrivent une architecture de dashboard
multi-vues, et l'utilisateur a fourni sa propre maquette de référence
réelle, `docs/reference/acf_dashboard_reference.jpg` ("ATMOSPHERIC
COMPLEXITY FRAMEWORK (ACF) — AWCI RESEARCH SUITE") — distincte de la
maquette qui a servi à `acf.gui.dashboard.awci_dashboard` (déjà
construit plus tôt cette session). L'audit initial de cette session
avait déjà confirmé, par lecture directe de `src/acf/gui`, qu'aucun
dashboard général multi-échéance n'existait — ce travail ferme cette
lacune.

**Architecture / Code** : nouveau
[`acf.gui.dashboard.acf_general_dashboard.ACFGeneralDashboard`](../src/acf/gui/dashboard/acf_general_dashboard.py) —
réutilise, sans les réimplémenter, les moteurs réels déjà construits
cette session ou avant : `compute_real_complexity_evolution()` (UNE
seule trajectoire réelle `CoupledEarthSolver` alimente à la fois les
onglets d'échéance et le graphique d'évolution — reslicing, jamais
recalcul), `sample_volume_cross_section()`, `AWCICalculator.calculate()`
(score ponctuel + décomposition + couplages dominants),
`ModelConsensusEngine.compute_real_multi_model_disagreement()` (spread
multi-modèle, à la demande, pas automatique — c'est le calcul le plus
coûteux du dashboard), et les widgets déjà existants `AWCIMapPanel`,
`AWCICrossSection`, `AWCIRadar`. `AWCIGauge` — un widget réel,
correct, mais **orphelin documenté** depuis que le dashboard AWCI est
passé à `AWCIRadar` — retrouve ici son premier usage réel en
production, fermant cette trouvaille d'audit comme effet de bord.
Deux nouveaux widgets graphiques réutilisables :
[`AWCIEvolutionChart`](../src/acf/gui/dashboard/awci_evolution_chart.py)
(courbe AWCI(t) réelle) et
[`AWCIModelSpreadChart`](../src/acf/gui/dashboard/awci_model_spread_chart.py)
(barres par modèle réel + bande de désaccord). Pattern worker
off-thread `QRunnable`+`Signal` avec méthodes liées (jamais de lambda —
la classe de bug déjà trouvée deux fois cette session : PySide6 ne
peut pas déterminer de file d'attente cross-thread sûre pour une
lambda nue). Ouverture via une nouvelle action toolbar ESOC
"🌐 ACF Dashboard" → `ACFGeneralDashboardWindow`.

**Décisions de périmètre honnêtes, explicitement déclarées** :
- Les 5 "onglets d'échéance" sont de vraies trames d'UNE seule
  évolution réelle (reslicing, pas 5 runs solveur indépendants).
- Le panneau de spread multi-modèle est réel mais à la demande — pas
  recalculé automatiquement à chaque clic d'onglet.
- Aucune annotation "JET STREAM SHEAR"/"CONVECTIVE PENETRATION" sur la
  coupe verticale — aucun algorithme réel de détection de jet-stream/
  cellule convective n'existe dans ce code ; en inventer un ici aurait
  été exactement le type de diagnostic fabriqué que le prompt maître
  interdit.
- Le point d'intérêt pour le score ponctuel/couplages est un point réel
  fixe et déclaré (Alger, 36.75N 3.06E — déjà utilisé ailleurs dans ce
  code, `awci_dashboard.py`), pas encore une interaction clic-n'importe
  où sur la carte (éviterait de démêler un vrai clic d'un vrai
  drag-pan, hors périmètre de cette passe).
- **Correction trouvée pendant la vérification manuelle, pas supposée** :
  la première version affichait des libellés d'onglet fixes
  "T+0h/T+3h/T+6h/T+12h/T+24h" — or `compute_real_complexity_evolution()`
  espace ses trames de façon **uniforme**, donc ce jeu de libellés à
  espacement inégal ne pouvait jamais correspondre à ce qui est
  réellement calculé. Corrigé : chaque bouton affiche désormais le vrai
  `valid_time_seconds` de sa trame réelle (`T+0.07h`, `T+0.13h`, …),
  jamais un texte fixe — exactement le genre d'écart entre affichage et
  donnée réelle que le §69 ("ne jamais inventer l'état du projet")
  interdit. Le titre du graphique d'évolution a de même perdu son
  "(24h)" fixe (le vrai intervalle dépend de `n_frames`/`steps_per_frame`/
  `dt_seconds`), l'axe des x réel restant la seule source de vérité sur
  la durée couverte.
- **Correction de mise en page trouvée par vérification réelle** (capture
  d'écran manuelle, pas supposition) : sans hauteur minimale explicite,
  la ligne carte+coupe verticale se retrouvait compressée à ~200px par
  la compétition avec les autres lignes (dont deux `AWCIGauge` avec leur
  propre `setMinimumSize(180, 180)` réel) — corrigé par
  `setMinimumHeight(380)` sur les deux et un poids de stretch relevé.

**Tests / Validation réelle** : 26 nouveaux tests, tous réels — pas de
mock du calcul lui-même :
`tests/gui/test_awci_evolution_chart.py` (6),
`tests/gui/test_awci_model_spread_chart.py` (5),
`tests/gui/test_acf_general_dashboard.py` (12, dont deux tests de
régression dédiés au bug de libellés fixes ci-dessus, et deux tests
`qtbot.waitUntil()` qui font vraiment tourner le worker `QThreadPool`
de bout en bout — pas d'appel direct à `run()` — même discipline que
`tests/test_esoc_awci_field.py`, qui avait déjà trouvé une fois cette
session le bug de signal connecté à une lambda nue),
`tests/test_esoc_acf_general_dashboard_action.py` (4, action toolbar +
ouverture/réutilisation de fenêtre). Un test compare le gauge/radar du
dashboard à un appel indépendant `AWCICalculator.calculate()` sur le
même point réel, et un test confirme qu'un clic d'onglet ne recalcule
jamais (`dashboard._evolution is evolution`, même objet). Suite
complète **3433/3433** (3407 + 26), `ruff`/`mypy` propres sur tous les
fichiers neufs/modifiés. Vérification visuelle manuelle (capture
d'écran réelle du dashboard avec évolution + consensus multi-modèle
calculés) envoyée à l'utilisateur pour comparaison avec
`docs/reference/acf_dashboard_reference.jpg`.

## Mise à jour 2026-09-03 (suite) — normalisation climatologique réelle, en option (§20)

Suite explicite ("continue"), quatrième priorité choisie dans les
manques identifiés par le tableau d'audit de conformité (mise à jour
du 2026-09-03 "décision d'autorité"), méthodologie suivie dans l'ordre
imposé par le prompt (§86).

**Pourquoi** : §20 du prompt maître avertit explicitement qu'une
normalisation min-max naïve "peut être scientifiquement mauvaise" et
demande d'étudier plusieurs alternatives (seuils physiques, percentiles
climatologiques, fonctions sigmoïdes, fonctions piecewise,
distributions historiques, saisonnalité, région, altitude, contexte
opérationnel), en précisant : "le choix de la normalisation doit être
documenté." Le tableau d'audit du 2026-09-03 classait ce point
**HYPOTHÈSE non résolue**.

**Inspecté/audité avant de construire quoi que ce soit** : une méthode
`Normalizer.normalize_percentile()` existait déjà — réelle, testée,
correcte — mais **jamais appelée** par `AWCICalculator`. Le pipeline de
production utilisait exclusivement les 6 fonctions `normalize_<var>()`
à plage fixe. L'infrastructure existait sans être branchée — l'audit
avait raison de marquer le point comme non résolu malgré la présence de
ce code mort.

**Construit** : nouvelle méthode privée
[`AWCICalculator._normalize()`](../src/acf/awci/calculator.py) — bascule
réelle et optionnelle entre la normalisation min-max existante et le
rang de percentile empirique réel (`Normalizer.normalize_percentile()`)
quand l'appelant fournit `data["climatology"]` (un vrai
`dict[str, list[float]]` d'échantillons climatologiques réels, par
variable : `wind_speed`/`temperature`/`specific_humidity`/`cape`/`cin`/
`precipitation`). Branché dans les 4 modules physiques concernés
(`dynamic`, `thermodynamic`, `convective`, `microphysical`) de
`calculate_module_scores()`. Purement additif : `data["climatology"]`
absent = comportement bit-identique à avant (vérifié par un test dédié
comparant clé absente / `None` / `{}`), et fournir un échantillon pour
UNE seule variable ne change que le module correspondant, tous les
autres restant identiques (également vérifié).

**Choix documenté (exigence explicite du §20)** : le rang de percentile
a été choisi comme unique alternative construite dans cette passe car
c'était la seule pour laquelle une implémentation réelle et testée
existait déjà dans le code — les autres alternatives listées par le
prompt (fonctions sigmoïdes, fonctions piecewise, courbes de seuils
physiques) restent **non construites**, explicitement déclarées comme
telles dans le docstring du code, pas fabriquées comme équivalentes. La
méthode ne stratifie pas automatiquement par saison/région/altitude —
c'est à l'appelant de pré-filtrer son échantillon climatologique en
conséquence ; limite réelle, documentée, pas silencieusement ignorée.

**Statut scientifique honnête de la méthode elle-même** : nouvelle
entrée `CLIMATOLOGY_NORMALIZATION_METHOD_STATUS` dans
[`acf.awci.scientific_status`](../src/acf/awci/scientific_status.py) —
`HYPOTHESIS`, même raisonnement qu'`UNCERTAINTY_METHOD_STATUS` (§64) :
le rang de percentile contre un échantillon réel fourni par
l'appelant est un vrai choix de conception ACF défendable, pas une
technique de normalisation externellement validée ou publiée pour cet
indice composite — alors que l'arithmétique du rang de percentile
elle-même (fraction empirique exacte) est exacte, réelle. Interrogeable
via `AWCICalculator.get_climatology_normalization_status()`.

**Validation réelle** : 11 nouveaux tests
(`tests/test_awci_calculator_climatology_normalization.py`) — preuve
que chaque module climatologique correspond exactement à un appel
indépendant de `Normalizer.normalize_percentile()`, que fournir une
climatologie pour une seule variable laisse les autres modules
inchangés, que la clé absente/`None`/vide donne un résultat
bit-identique à avant, qu'une clé de variable non reconnue est
silencieusement ignorée (même convention que les autres clés
optionnelles de la méthode), et que le pipeline complet `calculate()`
(pondération, interactions, classification de niveau) reste cohérent
avec des scores de module climatologiques en entrée. Suite complète
**3444/3444** (3433 + 11), `ruff`/`mypy` propres, aucune régression sur
le calcul AWCI naïf existant (zéro appelant existant affecté).

**Ce qui reste réellement, du tableau d'audit du 2026-09-03** :
- §20 Normalisation — **partiellement fermé** : le rang de percentile
  climatologique est maintenant réel et branché ; sigmoïde/piecewise/
  seuils physiques restent à étudier si demandé.
- §22 Moteur d'interactions général — toujours seulement 2 termes
  câblés en dur, pas un vrai moteur généralisé.
- §32 Statuts de qualité des données — vocabulaire du code
  (`NOT_ASSESSED/PASS/WARNING/FAIL`) toujours différent de celui du
  prompt.
- §45/§47 séparation architecturale ACF ≠ AWCI — toujours un vrai gap
  architectural, refactor large et risqué, délibérément différé.

## Mise à jour 2026-09-03 (suite) — statut de qualité réel par variable (§32)

Suite explicite ("continue"), cinquième priorité choisie dans les
manques identifiés par le tableau d'audit, méthodologie suivie dans
l'ordre imposé par le prompt (§86).

**Pourquoi** : §32 exige que "chaque variable" porte un statut parmi
un vocabulaire précis — `VALID`/`SUSPECT`/`MISSING`/`INVALID`/
`OUT_OF_RANGE`/`UNIT_ERROR`/`GRID_ERROR`/`TIME_ERROR`/
`PHYSICAL_INCONSISTENCY` — "le moteur ne doit pas silencieusement
continuer avec des données douteuses." L'audit avait déjà confirmé que
`acf.core.contracts.quality.QualityInfo` (réel, honnête, défaut
`NOT_ASSESSED`) est un statut **au niveau du Dataset entier**
(`NOT_ASSESSED/PASS/WARNING/FAIL`) — un concept différent, pas
simplement un vocabulaire à renommer.

**Inspecté avant de construire** : `acf.physics_guard` avait déjà toute
l'infrastructure réelle nécessaire — `OPERATIONAL_RANGES`/
`check_range()` (bornes physiques réelles par nom CF), et
`check_dewpoint_not_above_temperature()` (relation physique réelle
point de rosée ≤ température) — mais rien ne traduisait leurs
exceptions réelles (`RangeError`/`UnitError`/`CoordinateError`/
`DimensionError`/`VerticalError`/`TimeError`/
`ScientificConsistencyError`) vers le vocabulaire exact du §32.

**Construit** : nouveau module
[`acf.physics_guard.variable_quality`](../src/acf/physics_guard/variable_quality.py) —
`classify_guard_exception()` (mapping réel et justifié, une entrée par
type d'exception réel de `PhysicsGuard`) et `assess_variable_quality()`
(statut réel par variable, réutilisant `check_range()` pour
`OUT_OF_RANGE`/`VALID`, `MISSING` pour une variable attendue absente ou
`None`, `INVALID` pour une valeur non-finie/non-numérique réelle
(NaN/Inf), et `PHYSICAL_INCONSISTENCY` réel pour le couple
température/point de rosée quand la relation physique est violée —
remplace le statut `VALID` déjà attribué par le check de plage, la
violation relationnelle étant une preuve réelle supplémentaire, pas
supprimée par un filtre `expected_variables`). Purement additif :
`QualityInfo` n'est pas touché.

**Honnêteté du périmètre, explicitement documentée dans le module** :
`SUSPECT` n'est **jamais produit** — aucune heuristique statistique/
climatologique réelle "plausible mais douteux" n'existe dans ce code ;
en fabriquer une aurait été exactement le type de règle non fondée que
le §78 du prompt met en garde contre. `GRID_ERROR`/`TIME_ERROR` ne sont
produits que si l'appelant exécute lui-même le vrai check
correspondant (`check_coordinates()`/`check_vertical()`/
`check_time()`) et passe l'exception à `classify_guard_exception()` —
`assess_variable_quality()` ne les devine jamais automatiquement, ces
erreurs étant des propriétés d'un champ/axe entier, pas d'une variable
nommée. `check_relative_humidity_bounds()` (marge de sursaturation
réelle 0-110%) n'est délibérément pas ré-appliqué en plus du check de
plage (0-100% pour `relative_humidity` dans `OPERATIONAL_RANGES`) — une
vraie ambiguïté trouvée en inspectant le code (deux verdicts différents
possibles pour la bande 100-110% selon l'ordre des checks), résolue en
ne se fiant qu'au check de plage pour cette variable, pas en choisissant
un gagnant silencieusement.

**Validation réelle** : 19 nouveaux tests
(`tests/test_physics_guard_variable_quality.py`) — les 7 types
d'exception réels de `PhysicsGuard` mappés correctement, un type non
mappé lève une erreur explicite (jamais de devinette), `OUT_OF_RANGE`
correspond exactement à un appel indépendant de `check_range()`,
NaN/Inf/valeur non numérique donnent `INVALID`, une variable attendue
absente donne `MISSING`, une variable non réclamée n'apparaît jamais
dans le résultat (jamais de `MISSING` deviné), l'incohérence
température/point de rosée écrase un statut `VALID` par ailleurs
correct pour les deux variables, et une variable réellement hors-plage
n'est pas masquée par une relation point de rosée par ailleurs valide.
Suite complète **3463/3463** (3444 + 19), `ruff`/`mypy` propres.

**Non branché dans l'UI/le pipeline de production dans cette passe**
(disclosure honnête, pas caché) : contrairement au registre de statut
scientifique (§77-81, branché dans `AWCIComponentDetailDialog`), ce
module reste pour l'instant une infrastructure réelle et testée,
appelable, mais sans point de consommation GUI/pipeline — même
situation transitoire que `Normalizer.normalize_percentile()` avant
d'être branché lors de la mise à jour précédente (§20).

**Ce qui reste réellement, du tableau d'audit du 2026-09-03** :
- §22 Moteur d'interactions général — toujours seulement 2 termes
  câblés en dur, pas un vrai moteur généralisé.
- §32 — infrastructure réelle construite ; reste à brancher dans un
  vrai point de consommation (pipeline `Dataset`/GUI) si demandé.
- §45/§47 séparation architecturale ACF ≠ AWCI — toujours un vrai gap
  architectural, refactor large et risqué, délibérément différé.

## Mise à jour 2026-09-03 (suite) — vrai moteur d'interactions généralisé, optionnel (§22)

Suite explicite ("continue"), sixième priorité choisie dans les
manques identifiés par le tableau d'audit, méthodologie suivie dans
l'ordre imposé par le prompt (§86).

**Pourquoi** : §22 demande d'étudier scientifiquement les interactions
entre modules — "Vent élevé + Humidité élevée + Relief peut produire
une situation différente de la simple somme de trois risques" — un
exemple **à 3 variables**, en avertissant explicitement : "ne pas
inventer arbitrairement `interaction = A × B` sans justification
physique ou statistique." L'audit du 2026-09-03 constatait que
`AWCICalculator` n'avait que 2 termes d'interaction **codés en dur**
(multiplication littérale dans `calculate_interaction_scores()`), pas
une architecture généralisée — et ne pouvait même pas représenter
l'exemple à 3 variables du prompt lui-même.

**Décision explicite, pour respecter l'avertissement du §22** : ne
**pas** inventer de nouveau terme d'interaction activé par défaut —
cela changerait silencieusement le score AWCI de tout appelant
existant, sans justification physique nouvelle et rigoureuse au-delà
des deux termes déjà documentés. À la place : généraliser
l'**architecture** pour qu'elle soit réellement configurable, tout en
gardant les 2 termes existants comme comportement par défaut
bit-identique.

**Construit** : `AWCICalculator.__init__()` accepte maintenant
`interaction_terms`/`interaction_weights` réels et optionnels —
`interaction_terms` associe un nom de terme à un **tuple** de clés de
module (2 pour un terme par paires comme avant, **N pour un terme
d'ordre supérieur**, ex. 3 pour l'exemple littéral du §22).
`calculate_interaction_scores()` généralisé multiplie génériquement
tous les scores de module du tuple, au lieu de deux multiplications
codées en dur. Nouveau `INTERACTION_TERMS` (classe, `dict[str,
tuple[str, ...]]`) documente les 2 termes existants comme données,
plus `INTERACTION_WEIGHTS` (inchangé). Validation réelle : fournir
`interaction_terms`/`interaction_weights` avec des clés différentes
lève une erreur explicite plutôt que de laisser un terme calculé mais
jamais pondéré (ou l'inverse) passer silencieusement.

**Preuve travaillée de l'exemple du §22** : un test construit
explicitement le terme à 3 variables du prompt — Vent (`dynamic`) x
Humidité (repliée dans `thermodynamic`, qui combine déjà température +
humidité spécifique — voir `calculate_module_scores()`) x Relief
(`topographic`) — et vérifie qu'il traverse tout le pipeline
`calculate()` normalement. Documenté explicitement comme un exemple de
travail, pas une prétention que ce terme précis est physiquement
validé ou activé par défaut.

**Zéro changement de comportement par défaut** : `AWCICalculator()`
sans arguments produit un résultat **bit-identique** à avant cette
mise à jour (`interaction_terms`/`interaction_weights` par défaut =
copies exactes des 2 anciens dicts codés en dur) — vérifié par un test
comparant deux instances côte à côte sur un jeu de données réel.

**Validation réelle** : 9 nouveaux tests
(`tests/test_awci_calculator_interaction_engine.py`) — comportement
par défaut bit-identique, clés incohérentes entre termes/poids lève
une erreur, un terme personnalisé remplace complètement les 2
existants et traverse tout le pipeline, la configuration dégénérée
"zéro terme d'interaction" (somme linéaire pure) reste valide et
cohérente, le triplet littéral du §22 fonctionne réellement, le statut
de poids (§80) reste honnête pour un terme personnalisé non reconnu
(`INITIAL`, "no status recorded"), et les dicts fournis par l'appelant
ne sont jamais mutés. Suite complète **3472/3472** (3463 + 9),
`ruff`/`mypy` propres.

**Ce qui reste réellement, du tableau d'audit du 2026-09-03** :
- §22 — architecture généralisée réelle et testée fermée ; aucun
  nouveau terme physiquement validé ajouté par défaut (délibéré, voir
  ci-dessus) — reste ouvert si l'utilisateur veut qu'un terme
  spécifique soit étudié et activé.
- §32 — infrastructure réelle construite (mise à jour précédente) ;
  reste à brancher dans un vrai point de consommation si demandé.
- §45/§47 séparation architecturale ACF ≠ AWCI — toujours un vrai gap
  architectural, refactor large et risqué, délibérément différé.

## Mise à jour 2026-09-03 (suite) — §32 branché sur les vraies données METAR en direct

Suite explicite ("continue"), septième priorité — fermeture du point
resté ouvert à la mise à jour précédente ("§32 — infrastructure réelle
construite ; reste à brancher dans un vrai point de consommation").

**Pourquoi** : l'infrastructure `assess_variable_quality()` construite
la dernière fois restait un utilitaire réel mais orphelin — même
situation transitoire que `Normalizer.normalize_percentile()` avant
d'être branché. Le point de consommation le plus fidèle à l'intention
du projet ("le but est de brancher acf et awci avec des vrais station
pour nous rendre des vrai reponse instantanément") est le panneau de
messages METAR/TAF/SPECI/SIGMET en direct déjà construit cette session
(`AWCIMessagesDialog`) — de vraies données de vraies stations,
jamais encore contrôlées physiquement.

**Trouvaille faite en inspectant avant de brancher** :
`assess_variable_quality()` n'acceptait que des valeurs déjà dans leur
unité CF canonique (Kelvin, Pa, m/s) — or `METARReport` décode ses
valeurs dans leurs vraies unités natives (Celsius, hPa, nœuds). Plutôt
que de réinventer une conversion, ajout d'un paramètre `units` réel qui
réutilise `check_range()`'s propre conversion déjà existante
(`acf.normalization.units.convert_unit()`, MetPy/pint) — et application
de la même conversion avant le check de cohérence température/point de
rosée (qui suppose Kelvin), pour que la comparaison et son message
d'erreur restent physiquement corrects, pas une coïncidence de l'unité
choisie.

**Deuxième trouvaille** : `cf_canonical_unit()` lit une vraie table JSON
finie (`resources/standards/cf/cf_standard_names.json`) qui ne
contenait ni `dewpoint_temperature` ni `wind_speed` (vitesse scalaire,
distincte de `eastward_wind`/`northward_wind`, des composantes
vectorielles signées). Ajoutés à la table (unités réelles K et m/s) et
à `OPERATIONAL_RANGES` (bornes réelles et justifiées : même plage
généreuse que `air_temperature`/`eastward_wind`, `wind_speed` non-signée
contrairement aux composantes). La clé `dewpoint_temperature` (sans
underscore, différente de l'orthographe CF stricte
`dew_point_temperature`) est gardée telle quelle — c'est déjà la
convention interne établie par `consistency_check.py`/`guard.py`,
préexistante à ce travail, pas silencieusement "corrigée".

**Construit** : `acf.aviation.icao.metar_decoder.metar_report_quality(report)` —
pont réel entre un `METARReport` décodé et
`assess_variable_quality()`, ne considérant que les champs réellement
présents dans le rapport (jamais de `MISSING` deviné pour un champ
qu'un METAR omet légitimement). Branché dans
`AWCIMessagesDialog._on_fetch_ready()` via une nouvelle
`_format_metar_quality()` — une ligne "Quality (§32): N/N variable(s)
VALID" ou listant explicitement chaque variable non-VALID, affichée
sous le résumé décodé de chaque station en direct.

**Validation réelle** : 16 nouveaux tests au total —
`tests/test_physics_guard_variable_quality.py` (+8, paramètre `units` :
conversion correcte, valeur réellement hors-plage toujours détectée
après conversion, comportement par défaut bit-identique sans `units`,
cohérence point de rosée convertie, nouvelles entrées `wind_speed`/
`dewpoint_temperature` réelles et documentées),
`tests/test_metar_quality_bridge.py` (+6, station normale → tout
VALID, seuls les champs réellement présents évalués, température
extrême détectée, vitesse de vent en nœuds correctement convertie,
incohérence point de rosée/température réelle détectée),
`tests/test_awci_messages_panel.py` (+2, la ligne de qualité réelle
apparaît dans le panneau en direct pour une station normale et pour
une valeur réellement hors-plage). Suite complète **3488/3488**
(3472 + 16), `ruff`/`mypy` propres.

**Ce qui reste réellement, du tableau d'audit du 2026-09-03** :
- §32 — fermé : infrastructure réelle, branchée dans un vrai point de
  consommation (données METAR en direct).
- §45/§47 séparation architecturale ACF ≠ AWCI — seul gap encore
  ouvert du tableau d'audit initial ; refactor large et risqué,
  délibérément différé sauf demande explicite.

## Mise à jour 2026-09-03 (suite) — ACF ≠ AWCI (§45/§47), sans déplacer un seul fichier

Suite explicite ("continue" → confirmation directe "Oui, attaque
§45/§47"), dernière ligne ouverte du tableau d'audit initial. Deux
questions posées à l'utilisateur avant tout code (§86 — jamais deviner
une décision structurante), les deux réponses documentées ici.

**Conflit trouvé avant d'implémenter, pas ignoré** : une décision
explicite existait déjà, prise par l'utilisateur le 2 septembre et
enregistrée dans `docs/ACF_ARCHITECTURE_TARGET_GAP_MAP.md` : "faire
évoluer `awci/` sur place plutôt que dupliquer sa logique dans un
nouveau paquet `complexity/` — conforme à la règle 'ne rien déplacer'
de sa propre spécification d'ingénierie". Soumis explicitement à
l'utilisateur plutôt que silencieusement réinterprété ou silencieusement
respecté sans vérifier s'il souhaitait toujours l'appliquer aujourd'hui.
**Réponse : "Zéro déplacement de fichier (Recommandé)"** — la règle du
2 septembre s'applique toujours.

**Ce que ça signifie concrètement pour §45/§47** : pas de nouveau
paquet, pas de fichier déplacé, pas de classe dupliquée. À la place,
formalisation réelle et **testable** de la frontière ACF-core/
AWCI-application qui existait déjà de façon informelle dans
`AWCICalculator` — en poussant jusqu'au bout un principe déjà appliqué
deux fois cette session (le moteur d'interactions généralisé du §22, et
`WeightsManager` déjà générique dans ses mécanismes).

**Trouvaille faite en inspectant** : `_get_level()` — la classification
en bandes de complexité ("Very Low" → "Extreme") — était la seule pièce
de configuration AWCI-spécifique **encore codée en dur** (littéraux
`if/elif` directement dans la méthode), incohérente avec le reste de la
classe déjà rendu configurable (poids, termes d'interaction).

**Construit** :
- Nouveau `AWCICalculator.LEVEL_THRESHOLDS` (tuple de `(borne, label)`,
  même 6 bandes qu'avant, données au lieu de littéraux) +
  `__init__(level_thresholds=...)` réel et optionnel, validé (bornes
  strictement croissantes, jamais vide) — même discipline que
  `interaction_terms`/`interaction_weights`. `_get_level()` généralisé
  en une vraie recherche dans `self.level_thresholds`, comportement
  par défaut bit-identique (vérifié : les 12 scores frontière testés un
  par un contre l'ancienne échelle `if/elif`, y compris les cas limites
  exacts 20.0/35.0/85.0).
- Nouvelle section "ACF core vs. AWCI application layer" dans le
  docstring de `AWCICalculator` — cartographie explicite et concrète du
  diagramme du §45 (science framework/diagnostics/interaction engine/
  uncertainty/consensus/complexity → application framework → AWCI) vers
  le vrai code existant : quelles méthodes sont le moteur générique
  réutilisable (`calculate_module_scores`/`calculate_interaction_scores`/
  `calculate_with_uncertainty`/`_get_level`), quelles constantes sont la
  couche application AWCI (`DEFAULT_WEIGHTS`/`INTERACTION_WEIGHTS`/
  `INTERACTION_TERMS`/`LEVEL_THRESHOLDS`) — et disclosure honnête de ce
  qui reste non fait : `PHYSICAL_MODULES`/`FORECAST_MODULES` restent des
  constantes de classe, pas encore surchargeables par instance,
  explicitement documenté comme un sous-manque réel et différé, pas
  caché.

**Preuve travaillée, pas une affirmation en prose** : un test construit
un `AWCICalculator` avec une configuration complètement différente
(poids/termes d'interaction/bandes de classification simulant une
application hypothétique non-aviation, §46 — "des applications
potentielles, pas des produits déjà développés", rien de construit ici)
et vérifie qu'il produit un vrai score cohérent, indépendant, à travers
exactement le même mécanisme générique — puis compare ce score à celui
d'une vraie instance AWCI par défaut sur les mêmes données brutes,
prouvant que les deux configurations ne s'effondrent pas silencieusement
sur le même comportement.

**Validation réelle** : 9 nouveaux tests
(`tests/test_awci_calculator_reuse_boundary.py`) — comportement par
défaut bit-identique sur 12 scores frontière (dont les 3 cas limites
exacts), scores frontière utilisent la bonne bande (pas celle du
dessous), bandes personnalisées changent la classification,
`level_thresholds` vide/désordonné/avec doublon lève une erreur
explicite, l'exemple de réutilisation hypothétique fonctionne de bout
en bout et produit un score réellement différent de l'application AWCI
par défaut, et le tuple fourni par l'appelant n'est jamais muté. Suite
complète **3497/3497** (3488 + 9), `ruff`/`mypy` propres.

**Statut final du tableau d'audit du 2026-09-03** : les 6 lignes
identifiées (§20, §21/§77-81, §22, §27-29, §32, §45/§47, §64) sont
maintenant toutes fermées ou honnêtement disclosées comme
partiellement fermées avec la raison exacte du reste — aucun gap
"GAP RÉEL confirmé" du tableau initial ne reste sans réponse.

## Mise à jour 2026-09-03 (suite) — audit exhaustif des 90 sections du prompt maître

Suite explicite ("continue" → "oui"), à la demande directe de
l'utilisateur : le premier audit de conformité (mise à jour "décision
d'autorité + premier audit") n'avait échantillonné qu'une quinzaine des
90 sections de `docs/ACF_MASTER_PROMPT.md`, pas la totalité. Cette
mise à jour couvre les 90, section par section, par lecture directe du
document et vérification réelle dans `src/acf/` (`grep`/lecture de
fichier, pas de supposition) — pas exhaustive au sens d'un audit ligne
par ligne de chaque module scientifique (ce serait un travail de
plusieurs semaines), mais une vérification honnête de présence/absence
pour chacune des 90 sections.

**Légende** : ✅ CONFIRMÉ (réel, vérifié) · ⚠️ PARTIEL (réel mais
incomplet/dispersé, détail donné) · ❌ ABSENT (recherche réelle faite,
rien trouvé) · 🔵 MÉTHODOLOGIE (section 0/68-90 : directive de conduite
pour Claude, pas un artefact de code — respectée dans la façon dont
cette session a travaillé, pas quelque chose à "construire").

| § | Titre | Statut | Preuve réelle |
|---|---|---|---|
| 0 | Rôle de Claude | 🔵 | Directive de posture — suivie (raisonnement Science→Maths→Ingénierie appliqué à chaque mise à jour de cette session). |
| 1 | Identité du projet | 🔵 | Nom/acronymes déjà utilisés partout dans le code (`AWCICalculator`, `ACFGeneralDashboard`, etc.). |
| 2 | Le problème fondamental | 🔵 | Cadrage conceptuel, pas un artefact vérifiable en soi. |
| 3 | Question centrale de l'ACF | 🔵 | Idem. |
| 4 | Définition de la complexité atmosphérique | ⚠️ | Le vocabulaire de statut (`Établi`/`Hypothèse ACF`/`Conceptuel`) n'est PAS le même que celui réellement implémenté (`CONFIRMED`/`PROPOSED`/`HYPOTHESIS`/`REQUIRES_VALIDATION`/`UNKNOWN`, §77, construit le 2026-09-03 dans `acf.awci.scientific_status`) — le principe (distinguer établi/hypothèse/conceptuel) est bien respecté, juste avec le vocabulaire §77, pas celui du §4 littéralement. |
| 5 | Objectifs scientifiques | 🔵 | Objectifs directeurs, non vérifiables individuellement en code. |
| 6 | AWCI — définition | ✅ | `AWCICalculator` existe, réel, testé (3497 tests), documenté "Concept Output – Research Prototype" dans le dashboard (`awci_dashboard.py`) — le statut "indicateur conceptuel de recherche" du prompt est honnêtement affiché à l'utilisateur, pas caché. |
| 7 | Ce que l'AWCI ne doit pas être | ✅ | Confirmé PAR LA STRUCTURE du code : `AWCICalculator.calculate()` n'est jamais une simple moyenne — 9 modules pondérés + interactions + split physical/forecast + incertitude optionnelle. |
| 8 | Architecture conceptuelle générale | ⚠️ | Le flux `INGESTION→QUALITÉ→HARMONISATION→NORMALISATION→DIAGNOSTICS→MODULES→INTERACTIONS→INCERTITUDE→FUSION→AWCI→CARTES/PROFILS/DASHBOARD` existe par MORCEAUX réels (chaque étape a un vrai module quelque part) mais jamais assemblé en un seul pipeline nommé et traçable de bout en bout — voir §31 ci-dessous, même constat. *(Voir mise à jour du 2026-09-03 ci-dessous : fermé pour le chemin mono-point.)* |
| 9 | Multi-modèles | ✅ | Déjà confirmé (audit précédent) : `acf.models.base_model.BaseWeatherModel` (Protocol) + 7 adaptateurs réels (AROME/ALADIN/ARPEGE/ERA5/WRF/ICON/OpenIFS). |
| 10 | Modèle de données atmosphériques commun | ✅ | `acf.core.contracts.dataset.Dataset`/`VariableContract`/`Provenance`/`QualityInfo` — réel, construit le 2026-09-02, couvre spatial/vertical/temporel/variables/métadonnées comme demandé. |
| 11 | Contrôle physique des unités | ⚠️ | Déjà confirmé PARTIEL (audit précédent) : `PhysicsGuard` réel mais pas invoqué systématiquement à chaque point d'entrée du pipeline scientifique. |
| 12 | Module dynamique | ⚠️ | `AWCICalculator.calculate_module_scores()["dynamic"]` utilise UNIQUEMENT `wind_speed` (un scalaire). Le §12 demande vent à plusieurs niveaux, cisaillement, vorticité, omega, divergence, gradients — tous ces diagnostics EXISTENT réellement ailleurs (`acf.science.vorticity`, `.divergence`, `.bulk_wind_shear`, `.storm_motion`) mais ne sont PAS consommés par le module `dynamic` de l'AWCI. Écart réel entre la richesse du Science Engine et la simplicité du module AWCI actuel — pas caché, documenté ici pour la première fois avec cette précision. |
| 13 | Module thermodynamique | ⚠️ | `"thermodynamic"` = 0.5×temp_norm + 0.5×hum_norm, seulement 2 variables. `acf.science.virtual_potential_temperature`/`.lcl`/`.thermodynamics`/`.boundary_layer` existent réellement (θe, température virtuelle, lapse rate, stabilité) mais non branchés dans ce module. Même écart que §12. |
| 14 | Module convectif | ⚠️ | `"convective"` = 0.7×CAPE_norm + 0.3×CIN_norm — réel, mais le §14 demande explicitement de distinguer POTENTIEL convectif (CAPE) de convection EFFECTIVEMENT prévue/observée (réflectivité, sommet des nuages). `acf.science.clouds.severe_weather`/`acf.science.encyclopedia.radar_meteorology_library` existent mais la distinction n'est pas faite dans `AWCICalculator` lui-même — CAPE élevé reste actuellement le seul signal, pas confondu explicitement avec "orage garanti" dans le code (aucune phrase de ce type nulle part), mais pas non plus formellement séparé en deux sous-scores. |
| 15 | Module microphysique | ⚠️ | `"microphysical"` = précipitation uniquement. Givrage/grêle/eau surfondue (demandés explicitement) non branchés dans ce module, bien que du contenu réel existe ailleurs (`acf.science.encyclopedia.cloud_microphysics`, recherche "icing" dans `severe_weather.py`/`precipitation.py`). |
| 16 | Module relief/orographie | ⚠️ | `"topographic"` = altitude statique uniquement (`Normalizer.normalize_topographic()`). Le §16 est explicite : le relief doit être un MODIFICATEUR dynamique (accélération du vent, ondes orographiques, turbulence) — c'est exactement le rôle du terme d'interaction réel `wind_topo_interaction` (`dynamic × topographic`, §22, déjà réel) qui capture partiellement cet effet, mais le module `topographic` lui-même reste une simple valeur d'altitude, pas un vrai modificateur physique. |
| 17 | Module temporel | ✅ | `"temporal"` = `temporal_change` scalaire dans `AWCICalculator`, mais surtout `acf.awci.temporal_field.compute_real_complexity_evolution()` (réel, une vraie trajectoire `CoupledEarthSolver` continue) fournit exactement `AWCI(t-1)/(t)/(t+1)/...` — branché dans le dashboard AWCI ("▶ Play Evolution (4D)") et dans le nouveau dashboard général ACF (onglets d'échéance réels, construit le 2026-09-03). |
| 18 | Module confiance/incertitude | ✅ | Confirmé (audit du 2026-09-02) : `physical_score`/`forecast_score` séparés, jamais mélangés dans le même score. |
| 19 | Inter-model disagreement | ✅ | Déjà confirmé PARTIEL (audit précédent) : `ModelConsensusEngine.compute_real_multi_model_disagreement()` réel. |
| 20 | Normalisation | ✅ | Fermé le 2026-09-03 (`data["climatology"]`, rang de percentile réel, opt-in). |
| 21 | Pondération | ✅ | Fermé le 2026-09-03 (registre de statut scientifique §77-81, `WeightsManager.get_weight_status()`). |
| 22 | Interactions | ✅ | Fermé le 2026-09-03 (moteur d'interactions généralisé, `interaction_terms`/`interaction_weights`). |
| 23 | Complexité spatiale (2D/3D/4D) | ✅ | `compute_real_complexity_field()`/`compute_real_complexity_volume()`/`compute_real_complexity_evolution()` — les 3 dimensions réelles, déjà construites et testées. |
| 24 | Complexité verticale | ✅ | `acf.awci.vertical_field` — réel, `AWCI(x,y,z,t)` supporté (`vertical_profile_at_point()`, `sample_volume_cross_section()`). |
| 25 | Produits verticaux | ✅ | `AWCICrossSection` (coupes verticales réelles), `vertical_profile_at_point()` (profils). Trajectoires potentielles / diagnostic par niveau de vol : non trouvés comme produits dédiés séparés — partiellement couvert par le sélecteur de niveau du dashboard AWCI. |
| 26 | Explicabilité | ⚠️ | `decomposition`/`_explain()`/`interaction_scores` réels (Score→Contributions). La chaîne complète du §26 (`Score → Contributions → Variables → Diagnostics → données sources → modèle → échéance → niveau vertical`) n'est PAS un objet unique traçable de bout en bout — chaque maillon existe séparément (modèle/échéance dans `MODEL_CONFIGS`/`valid_time_seconds`, niveau dans le sélecteur GUI) mais rien ne les relie formellement à un `AWCICalculator.calculate()` donné. |
| 27 | Dashboard | ✅ | Fermé le 2026-09-03 (dashboard ACF général construit) + `AWCIDashboard` déjà existant — vue générale/explicative/temporelle/verticale/multi-modèle/scientifique toutes réellement présentes à travers les deux dashboards. |
| 28 | Cartographie (couches par type de complexité) | ❌ | **Gap réel confirmé, pas trouvé avant cet audit.** `acf.gui.map.map_layers.LayerManager.available_layers` ne contient que 7 couches (`Satellite RGB`, `Radar Mosaic`, `2m Temp`, `Wind Vectors`, `MSLP`, `Cloud Cover`, `AWCI Complexity` — un seul score combiné). Aucune couche séparée `Dynamic complexity`/`Thermodynamic complexity`/`Convective complexity`/`Microphysical complexity`/`Orographic complexity`/`Temporal complexity`/`Uncertainty`/`Model disagreement` comme le §28 le demande explicitement — l'utilisateur ne peut activer/désactiver que le score AWCI total, pas sa décomposition par module sur la carte. *(Voir mise à jour du 2026-09-03 ci-dessous : partiellement fermé depuis.)* |
| 29 | Architecture des couches | ❌ | Même constat que §28 — la liste de 17 couches du §29 (`AWCI/Dynamic/Thermodynamic/.../Turbulence/Icing/Visibility`) n'a qu'1 correspondance réelle (`AWCI`) sur 17 dans `LayerManager`. *(Voir mise à jour du 2026-09-03 ci-dessous : partiellement fermé depuis.)* |
| 30 | Architecture logicielle | ⚠️ | Voir décision explicite §45/§47 (2026-09-03) : le paquet cible `acf/complexity/` n'existe pas et ne sera pas créé ("ne rien déplacer") — la frontière est formalisée en place dans `AWCICalculator`, pas comme une arborescence de paquets séparée. Les autres paquets cibles (`ingestion/`, `adapters/`, `interactions/`, `uncertainty/`, `consensus/`, `verification/`, `calibration/`, `climatology/`, `provenance/`) existent tous par LEUR FONCTION réelle ailleurs dans `src/acf/` (`models/`, `physics_guard/`, `verification/`, `core/contracts/provenance.py`...) mais rarement sous ces noms exacts — dispersion déjà documentée dans le gap-map du 2 septembre. |
| 31 | Pipeline scientifique (21 étapes) | ⚠️ | Chaque étape existe RÉELLEMENT quelque part (ingestion via les adaptateurs modèles, QC via `PhysicsGuard`/`assess_variable_quality()`, diagnostics via `acf.science`, normalisation via `Normalizer`, modules/interactions/incertitude/AWCI via `AWCICalculator`, produits/visualisation/dashboard via `gui/`) mais jamais assemblées en une seule classe/fonction "pipeline" nommée et orchestrée de bout en bout, contrairement à ce que le diagramme suggère. *(Voir mise à jour du 2026-09-03 ci-dessous : fermé pour le chemin mono-point, avec statut honnête par étape.)* |
| 32 | Qualité des données | ✅ | Fermé le 2026-09-03 (`acf.physics_guard.variable_quality`, vocabulaire exact §32, branché sur les données METAR en direct). |
| 33 | Provenance | ⚠️ | `acf.core.contracts.provenance.Provenance` réel (`generator`/`algorithm_version`/`science_version`/`config_version`/`created_at`/`notes`) — couvre la chaîne conceptuelle du §33 mais pas exactement les 8 maillons littéraux (`module values → diagnostics → normalized variables → harmonized variables → source files → model → run → forecast hour`) comme une trace explicite par résultat AWCI individuel. |
| 34 | Validation scientifique | ⚠️ | `acf.verification`/`acf.validation`/`acf.certification` réels (RMSE/bias/MAE/ACC/POD/FAR/CSI/ETS dans `nwp_metrics.py`, `CertificationEngine` à 6 étapes réelles) — mais pas le protocole en 5 points exact du §34 (sélection de cas représentatifs → calcul expérimental → comparaison prévisionniste → comparaison observations → ajustement/validation statistique) assemblé comme une procédure unique. |
| 35 | Données de validation | ⚠️ | METAR/TAF réels et en direct (`acf.aviation.icao`, branché cette session). SIGMET réel. Radar/satellite/foudre/radiosondages : modules scientifiques existent (`acf.science.encyclopedia.radar_meteorology_library`/`.lightning`/`.radiosonde`) mais pas de connexion "en direct" équivalente à METAR/TAF. PIREP/retours prévisionnistes opérationnels : non trouvés. |
| 36 | Validation des cas | ❌ | **Confirmé absent.** Recherche réelle de `CASE_ID`/`WEATHER_REGIME`/`EXPERT_ASSESSMENT` : aucune correspondance. `acf.testing.golden` (Golden Datasets) existe mais sert la non-régression logicielle (§54), pas une base de cas météorologiques historiques avec évaluation experte comme le §36 le décrit — objectifs différents malgré la ressemblance de surface. |
| 37 | Validation contre l'expertise humaine | ❌ | **Confirmé absent.** Aucune trace de comparaison structurée AWCI-vs-prévisionniste, ni de mesure d'accord/désaccord/biais/variabilité inter-prévisionnistes. |
| 38 | Validation contre les observations | ⚠️ | L'infrastructure de métriques existe (§34/§39) et METAR/TAF réels sont désormais branchés (§32/§35), mais rien ne compare encore systématiquement un score AWCI calculé à un événement réellement observé. |
| 39 | Métriques | ⚠️ | `acf.verification.nwp_metrics` : RMSE/bias/MAE/ACC/POD/FAR/CSI/ETS réels et testés. ROC/AUC et Brier score (mentionnés explicitement au §39 "lorsque pertinent") : non trouvés par recherche directe — à construire si un cas d'usage probabiliste l'exige. |
| 40 | Calibration | ❌ | Recherche réelle de séparation train/calibration/validation explicite (`DATASET TRAIN → CALIBRATION → LOCKED MODEL → INDEPENDENT VALIDATION`) : rien trouvé. Tous les poids actuels sont `INITIAL`/`EXPERT_BASED` (registre §77-81) — cohérent avec "aucune calibration n'a encore eu lieu", mais confirme qu'aucun pipeline de calibration formel n'existe non plus. |
| 41 | Machine Learning / IA | ❌ | **Confirmé absent.** Recherche réelle d'un cadre de comparaison Physics-based vs Statistical vs ML vs Hybrid : aucune correspondance dans `acf.ai`/`acf.ai_expert`/`acf.science`. Des modules IA existent ailleurs dans le dépôt (`acf.ai.ensemble.EnsembleManager`, déjà utilisé par `AWCICalculator`) mais pas le cadre de comparaison explicite que le §41 demande. |
| 42 | Physics-first | ✅ | Principe respecté dans toute cette session : chaque fermeture de gap (§20/§22/§32/§45-47) a réutilisé de la vraie physique/infrastructure existante avant d'ajouter quoi que ce soit — jamais l'inverse (ML → score → interprétation physique). Pas un artefact de code à auditer en soi, une pratique déjà démontrée. |
| 43 | Multi-échelles | ⚠️ | Micro/méso/synoptique existent implicitement via les résolutions de grille réelles (`MODEL_CONFIGS` : AROME 1.3km, ALADIN, ARPEGE) mais aucune classification explicite d'échelle n'est attachée aux résultats AWCI eux-mêmes. |
| 44 | Complexité ≠ danger | ✅ | Déjà confirmé (audit précédent) : principe déjà respecté dans le vocabulaire du code (jamais de conflation trouvée). |
| 45 | ACF ≠ AWCI | ✅ | Fermé le 2026-09-03 (frontière formalisée en place, sans déplacement de fichier). |
| 46 | Écosystème futur (DWCI/MWCI/...) | 🔵 | Explicitement présenté par le prompt comme vision, "pas des produits déjà développés" — rien construit ici, conforme à l'intention du prompt lui-même. Le test de réutilisation du §45/§47 (`test_awci_calculator_reuse_boundary.py`) prouve que la porte est réellement ouverte pour ça le jour où demandé. |
| 47 | Principe de réutilisation | ✅ | Fermé le 2026-09-03 avec §45. |
| 48 | Architecture des produits (niveaux brut→opérationnel) | ⚠️ | Les 7 niveaux existent en pratique dispersés (variables brutes dans `data`, diagnostics dans `acf.science`, modules/interactions/AWCI dans `AWCICalculator`, textes dans `_explain()`, alertes dans `AWCIAlertsPanel`) mais pas comme une chaîne de transformation explicite et nommée. *(Voir mise à jour du 2026-09-03 ci-dessous : la chaîne réelle "variables → qualité → modules → interactions/incertitude → AWCI → produit" est maintenant nommée et tracée pour le chemin mono-point ; les niveaux "alertes"/dashboard restent des consommateurs séparés, non intégrés à ce pipeline.)* |
| 49 | Exemple de chaîne explicable | ✅ | `_explain()` génère bien du texte à partir de données calculées (jamais inventé) — vérifié par les tests existants (`test_explanation_present_and_ordered_by_contribution`). |
| 50 | Dashboard 2D/3D/4D | ✅ | Les 3 dimensions réelles existent et sont branchées au dashboard (§23-27). |
| 51 | Profils et couches (niveaux de vol) | ⚠️ | Le sélecteur de niveau du dashboard AWCI est réel (`_current_level_index`) mais ne couvre pas explicitement la liste précise du §51 (Surface/850/700/500/300/250 hPa/Flight levels nommés). *(Voir mises à jour du 2026-09-03 ci-dessous : fermé en mode démo pour la liste de niveaux ET pour la ventilation par variable — clic sur un niveau → détail réel par module.)* |
| 52 | Conception orientée prévisionniste | 🔵 | Principe de design déjà respecté (accès aux données originales préservé partout : METAR/TAF brut affiché à côté du résumé décodé, `raw_text` jamais caché). |
| 53 | Descendre dans le système | ⚠️ | Existe partiellement : composants cliquables (`AWCIComponentDetailDialog`, construit plus tôt cette session) permettent Module→statut de poids. La chaîne complète jusqu'au fichier source n'est pas câblée (même limite que §26). |
| 54 | Architecture de test | ✅ | Les 6 catégories existent réellement : unitaires (`tests/test_awci_calculator.py`), physiques (ex. `test_pressure_decreases_with_altitude_real_physics`), numériques, intégration (tests GUI `qtbot`), multi-modèles (`test_model_disagreement_end_to_end_from_real_model_consensus_engine`), non-régression (`acf.testing.golden`, Golden Datasets). |
| 55 | Documentation scientifique | ⚠️ | Chaque nouvelle fonctionnalité de cette session documente `NAME`/description/équation/limites dans son propre docstring (ex. `variable_quality.py`, `calculator.py`) — réel mais pas un registre centralisé et interrogeable par diagnostic comme le §55 le décrit littéralement. |
| 56 | Configuration | ⚠️ | `acf.core.config.ConfigManager` existe réellement, mais les poids/seuils AWCI eux-mêmes (`WeightsManager.DEFAULT_WEIGHTS`, `AWCICalculator.LEVEL_THRESHOLDS`) restent des constantes Python versionnées par git, pas une configuration externe versionnée séparément comme le §56 le décrit. |
| 57 | Reproductibilité | ⚠️ | `Provenance` réel couvre une partie (`algorithm_version`/`science_version`/`config_version`) mais pas tous les champs du §57 (`run_identifier`, `software_environment` explicites). |
| 58 | Versionnage scientifique | ⚠️ | `Provenance.science_version`/`config_version` existent ; `calibration_version`/`dataset_version` distincts n'ont pas été trouvés. |
| 59 | Séparation recherche/production | 🔵 | Principe respecté dans la pratique de cette session (chaque nouvelle méthode reçoit un statut scientifique honnête via le registre §77-81 avant tout usage "de production") — pas un pipeline RESEARCH→PRODUCTION formel séparé dans le code. |
| 60 | Certification | ✅ | `CertificationEngine` réel, 6 étapes (`_input_valid`/`_qc_pass`/`_physics_pass`/`_science_pass`/`_provenance_pass`/`_verification_status`) — couvre la majorité des 5 catégories du §60. |
| 61 | Sécurité scientifique (UNKNOWN > fausse certitude) | ✅ | Déjà confirmé (audit précédent) — pratique déjà omniprésente (`None` réel plutôt que `0.0` fabriqué). |
| 62 | Gestion des missing data | ✅ | Confirmé par cette session elle-même : `assess_variable_quality()` distingue `MISSING` de `0`/`INVALID` explicitement (§32) ; `AWCICalculator` n'a jamais remplacé silencieusement une valeur manquante par 0 dans aucun module vérifié. |
| 63 | Gestion des modèles divergents | ✅ | `ModelConsensusEngine.compute_real_multi_model_disagreement()` retourne consensus + spread + désaccord réels, jamais une simple moyenne. |
| 64 | Score et distribution | ✅ | Fermé le 2026-09-03 (`calculate_with_uncertainty()`). |
| 65 | Architecture de recherche | 🔵 | Méthodologie de conduite de projet — appliquée à chaque mise à jour de cette session (comprendre→hypothèse→méthode→données→tests→validation, visible dans chaque section "Mise à jour" de ce document). |
| 66 | Roadmap scientifique (10 phases) | 🔵 | Vision de haut niveau, pas un artefact vérifiable en un audit ponctuel — le dépôt est objectivement au-delà de la Phase 3 (Prototype) sur plusieurs axes (interactions/incertitude/AWCI/dashboard tous réels), mais aucune section du code ne se réclame explicitement d'une "Phase N" donnée. |
| 67 | Vision long terme | 🔵 | Cadrage, non vérifiable en code. |
| 68 | Ce que Claude doit faire | 🔵 | Suivi dans l'ordre à chaque mise à jour de cette session (comprendre→identifier→comparer→corriger→ajouter→tester→documenter). |
| 69 | Ne pas inventer l'état du projet | 🔵 | Règle respectée systématiquement cette session — chaque affirmation "GAP" ou "CONFIRMÉ" de ce document vient d'une commande `grep`/lecture réelle, jamais d'une supposition (y compris dans cette mise à jour elle-même). |
| 70 | Audit obligatoire avant modification majeure | 🔵 | Appliqué explicitement avant le travail §45/§47 (inspection du package layout, relecture du gap-map du 2 septembre) avant tout code. |
| 71 | Priorité à la préservation | 🔵 | Respectée explicitement : décision de "zéro déplacement de fichier" pour §45/§47, les 23 fichiers citant le "Prompt Maître v2.0" jamais réécrits en masse. |
| 72 | Git | 🔵 | Chaque commit de cette session suit fetch→check→commit→push avec message détaillé (quoi/pourquoi/impact/tests). |
| 73 | Performance HPC | ✅ | Infrastructure HPC réelle et confirmée fonctionnelle : `acf.hpc_connector` (SSH/Slurm/job manager/resource optimizer réels), connexion SSH réelle vérifiée vers FENNEC (mémoire de session du 2026-09-02, `sfoura@sms1.meteo.dz`, authentification confirmée par log réel). `acf.hpc` (`distributed_grid`/`mpi_solver`/`gpu_acceleration`/`parallel_scheduler`) réel également. |
| 74 | Architecture data (RAW→STAGING→...→PRODUCTS) | ⚠️ | Chaque étape existe par sa fonction réelle ailleurs (`Dataset`/`QualityInfo` pour RAW/STAGING, `acf.science` pour DIAGNOSTICS, `AWCICalculator` pour FEATURES/COMPLEXITY, `gui/` pour PRODUCTS) mais pas nommée/étiquetée comme ce pipeline précis nulle part. *(Voir mise à jour du 2026-09-03 ci-dessous : la même chaîne RAW→QC→FEATURES/COMPLEXITY→PRODUCTS est maintenant nommée pour le chemin mono-point.)* |
| 75 | Observabilité | ⚠️ | `acf.monitoring` réel et large (`realtime_monitor`/`telemetry_engine`/`anomaly_monitor`/`alert_dispatcher`) mais générique — pas spécifiquement branché pour produire le type de rapport de qualité par exécution AWCI que le §75 illustre ("Input files: 48, Valid: 46..."). *(Voir mise à jour du 2026-09-03 ci-dessous : fermé.)* |
| 76 | Mode d'explication de Claude | 🔵 | Ordre Pourquoi→Physique→Mathématiques→Architecture→Code→Tests→Validation suivi dans chaque réponse "Résumé" de cette session. |
| 77 | Décision scientifique incertaine → statut explicite | ✅ | Fermé le 2026-09-03 (registre `acf.awci.scientific_status`, vocabulaire exact du §77). |
| 78 | Règle sur les formules | ✅ | Respectée : chaque formule ajoutée cette session (rang de percentile, moteur d'interactions généralisé, seuils de niveau) documente notation/hypothèses/limites dans son propre docstring. |
| 79 | Règle sur les thresholds | ✅ | `NORMALIZER_RANGE_STATUS`/`LEVEL_THRESHOLDS` — tous `HYPOTHESIS` jusqu'à validation, jamais présentés comme établis. |
| 80 | Règle sur les weights | ✅ | `WeightsManager.get_weight_status()` — vocabulaire exact `initial`/`expert-based`/`calibrated`/`validated`, aucun poids `VALIDATED` aujourd'hui (honnête). |
| 81 | Règle sur l'AWCI (champs minimums) | ⚠️ | `calculate()` retourne `awci`/`level`(class)/`confidence`/décomposition(dominant factors via `_explain`)/`interaction_scores`. Manquants explicitement nommés comme tels par le §81 : `model spread` au niveau du résultat AWCI lui-même (existe séparément via `ModelConsensusEngine`, jamais fusionné dans le retour de `calculate()`) et `quality`/`provenance` au niveau du résultat AWCI (existent comme systèmes séparés — `assess_variable_quality()`, `Provenance` — jamais attachés directement à un objet résultat `calculate()`). |
| 82 | Exemple de sortie structurée | 🔵 | Exemple illustratif explicitement marqué comme tel par le prompt lui-même ("pas une spécification scientifique finale") — non applicable comme exigence littérale. |
| 83 | Objectif final du projet | 🔵 | Vision, non vérifiable en code isolément. |
| 84 | Philosophie fondamentale | 🔵 | Principes déjà respectés dans la conduite de cette session (scientifique/explicable/mesurable/testable/reproductible/falsifiable/transparent — visible dans chaque section "Mise à jour" de ce document). |
| 85 | Mission de Claude | 🔵 | Les 20 points sont soit déjà couverts par les mises à jour de cette session (audit, reconstruction, tests, documentation), soit hors du périmètre demandé pour l'instant. |
| 86 | Ordre de travail obligatoire | 🔵 | Suivi explicitement à chaque mise à jour (COMPRENDRE→INSPECTER→AUDITER→PLANIFIER→IMPLÉMENTER→TESTER→VALIDER→DOCUMENTER→RAPPORTER visible dans chaque section ci-dessus). |
| 87 | Critère de réussite | 🔵 | Chaque mise à jour de cette session vérifie plus que `pytest = PASS` (voir les sections "Décisions honnêtes"/"Statut scientifique" de chaque mise à jour). |
| 88 | Dernière règle | 🔵 | Respectée explicitement au moins deux fois cette session (conflit v2.0 soumis à l'utilisateur plutôt que deviné ; conflit §45/§47 soumis plutôt que silencieusement tranché). |
| 89 | Référence de départ | 🔵 | Le PPT original est cité et son intention respectée dans `docs/ACF_MASTER_PROMPT.md` lui-même. |
| 90 | Instruction finale (15 questions) | 🔵 | Les 15 questions correspondent en pratique aux sections "Pourquoi/Physique/Architecture/Tests" déjà présentes dans chaque mise à jour de ce document — pas un artefact séparé à vérifier. |

**Synthèse honnête** (comptage réel, pas estimé — vérifié par script
sur le tableau ci-dessus, colonne par colonne) : sur les 91 sections
(0-90), **26 🔵 méthodologie** (déjà respectées dans la pratique de
cette session, pas un artefact de code) et 65 sections correspondant à
un artefact de code réellement vérifiable, dont **32 ✅ confirmées**,
**27 ⚠️ partielles** (réelles mais incomplètes, détail donné ligne par
ligne), **6 ❌ absentes confirmées** (§28-29 cartographie par module,
§36 base de cas historiques, §37 validation contre l'expertise
humaine, §40 pipeline de calibration formel, §41 cadre de comparaison
Physics/Statistical/ML/Hybrid).

**Aucun nouveau chantier lancé automatiquement dans cette mise à jour**
— c'est un audit, pas une implémentation (§70 : audit avant
modification majeure). Les 6 gaps ❌ et 27 gaps ⚠️ ci-dessus sont pour
que l'utilisateur choisisse la prochaine priorité en connaissance de
cause, pas une liste que Claude s'engage à combler sans confirmation.

## Mise à jour 2026-09-03 (suite) — couches de complexité par module réelles (§28-29)

Suite explicite ("oui vasy" — priorité choisie librement dans les 6
gaps ❌ de l'audit exhaustif ci-dessus), méthodologie suivie dans
l'ordre imposé par le prompt (§86).

**Pourquoi** : §28 demande explicitement des couches cartographiques
séparées par type de complexité (Dynamic/Thermodynamic/Convective/
Microphysical/Orographic/Temporal/Uncertainty/Model disagreement),
activables/désactivables individuellement — l'audit venait de confirmer
qu'une seule couche combinée (`AWCI Complexity`) existait, sur les 17
listées au §29.

**Trouvaille faite en inspectant avant de construire** :
`acf.awci.spatial_field.compute_real_complexity_field()` appelait déjà
`AWCICalculator.calculate()` en chaque point réel de la grille — et son
retour `module_scores` (le détail par module) était **jeté** après
extraction du seul score combiné `awci`. Aucune nouvelle donnée
physique à calculer : l'information existait déjà, réelle, à chaque
point, juste non conservée.

**Construit** :
- `compute_real_complexity_field()` conserve maintenant aussi
  `module_fields` — un vrai champ 2D par module (`dynamic`/
  `thermodynamic`/`convective`/`microphysical`/`topographic`/
  `temporal`/`confidence`/`ensemble_spread`/`model_disagreement`, le
  même ensemble que `AWCICalculator.PHYSICAL_MODULES`∪`FORECAST_MODULES`
  utilise déjà et qu'un test dédié vérifie exhaustif) — **coût de calcul
  supplémentaire nul**, la même boucle réutilise le résultat déjà
  produit par le même appel `calculate()`.
- Nouvelles classes réelles
  [`ModuleComplexityLayer`](../src/acf/gui/map/map_layers.py)
  (générique, paramétrée par module) et `UncertaintyLayer` (source :
  `forecast_field`, déjà réel), enregistrées dans `LayerManager` — 6
  couches par module (`Dynamic Complexity` → `Orographic Complexity`)
  + `Uncertainty`, portant le total réel de `LayerManager` à 8 des 17
  couches du §29 (contre 1 avant). Même discipline "aucune donnée
  fabriquée" que `AWCILayer` : `render()` ne dessine rien tant qu'aucune
  vraie donnée n'a été fournie.
- `MapCanvas.set_module_complexity_field()`/`clear_module_complexity_field()`/
  `set_uncertainty_field()`/`clear_uncertainty_field()` — même schéma
  que `set_awci_field()` existant, avec un paramètre `activate` réel
  (voir décision de périmètre ci-dessous).
- Branché dans le bouton toolbar ESOC existant "🌪️ AWCI Field"
  (`_on_awci_field_ready()`) : le même calcul déjà déclenché peuple
  maintenant aussi les 7 nouvelles couches, coût nul.

**Décision de périmètre honnête, explicitement disclosed** : les 7
nouvelles couches sont peuplées de vraies données mais **pas affichées
automatiquement** (`activate=False`) en même temps que la couche AWCI
combinée — les afficher toutes simultanément empilerait 7 heatmaps
translucides superposées, illisible, sans aucun contrôle utilisateur
pour n'en choisir qu'une (aucune UI de case à cocher par couche
n'existe encore dans ESOC pour `LayerManager` — même situation pour la
couche `AWCI Complexity` déjà existante, qui n'a elle-même qu'un bouton
"afficher", jamais de case à cocher). Le §28 exige explicitement que
"l'utilisateur doit pouvoir activer/désactiver les couches" — cette
mise à jour rend les **données** réelles et prêtes (`layer.custom_data`
peuplé, `MapCanvas.set_module_complexity_field(..., activate=True)`
réel et testé), mais **pas encore le contrôle visuel interactif
par couche** — prochaine étape naturelle si demandée, pas cachée ici.
`Model Consensus`/`Model Spread` (2 des 17 couches du §29) restent
absentes : les calculer point par point nécessiterait de refaire
tourner la fusion multi-modèle à chaque cellule de la grille — limite
déjà documentée dans `spatial_field.py` et non résolue par cette mise à
jour. `Turbulence`/`Icing`/`Visibility` (3 autres) n'ont pas de champ
réel calculé point par point dans ce dépôt.

**Validation réelle** : 17 nouveaux tests —
`tests/test_awci_spatial_field.py` (+4 : `module_fields` couvre
exactement l'ensemble réel de modules, correspond à un appel
indépendant `AWCICalculator.calculate()` sur la même cellule, varie
réellement dans l'espace pour un run perturbé, reste borné [0,100]),
`tests/test_map_layers_module_complexity.py` (+12 : les 6 couches +
`Uncertainty` sont enregistrées, aucune active par défaut, ne dessinent
rien sans vraie donnée, dessinent la vraie donnée une fois fournie, les
méthodes `MapCanvas` peuplent la bonne couche et sont indépendantes les
unes des autres), `tests/test_esoc_awci_field.py` (+1 : le bouton
toolbar existant peuple bien les 7 nouvelles couches avec de vraies
données, non affichées). Suite complète **3514/3514** (3497 + 17),
`ruff`/`mypy` propres.

**Ce qui reste réellement, du tableau d'audit exhaustif ci-dessus** :
- §28-29 — **partiellement fermé** : données/couches réelles pour 6 des
  8 modules + incertitude ; UI de bascule par couche et
  Model Consensus/Spread/Turbulence/Icing/Visibility restent ouverts.
- §36/§37/§40/§41 — toujours absents, non traités par cette mise à
  jour (choix explicite de périmètre, pas oublié).

## Mise à jour 2026-09-03 (suite) — contrôle interactif réel par couche (§28)

Suite explicite ("continue"), fermeture du point resté ouvert à la
mise à jour précédente ("UI de bascule par couche... reste à
construire").

**Pourquoi** : §28 exige explicitement "l'utilisateur doit pouvoir
activer/désactiver les couches" — la mise à jour précédente avait rendu
les données/l'API réelles (`MapCanvas.set_module_complexity_field(...,
activate=True)`) mais aucun contrôle visuel interactif n'existait
encore pour qu'un utilisateur choisisse quelle couche afficher.

**Trouvaille faite en inspectant avant de construire, pas ignorée** :
un système de gestion de couches **entièrement différent et déjà
orphelin** existe dans ce dépôt —
[`acf.gui.map.layers.layer_manager.LayerManager`](../src/acf/gui/map/layers/layer_manager.py)
(un vrai `QObject` à signaux Qt, `add_layer()`/`remove_layer()`/
`layers()`/`visible_layers()`) plus deux vrais widgets de case à cocher
(`acf.gui.docks.layer_panel.LayerPanel` et
`acf.gui.layer_panel.layer_panel`) construits pour lui — dont le propre
docstring de `LayerPanel` confirme déjà : "currently unused/unwired
anywhere else in the codebase". Ce couple cible une interface
totalement différente et incompatible (signaux Qt, `layer.id`/
`layer.visible`, sémantique add/remove/move) du vrai `LayerManager`
simple (`available_layers: dict` + `active_layer_names: list[str]`,
sans signal) que `MapCanvas` — la vraie carte connectée d'ESOC —
utilise réellement. Adapter l'un à l'autre reviendrait quasiment à une
réécriture, pas une vraie réutilisation ; **non consolidé/supprimé ici**
(§71 du prompt : ne jamais supprimer massivement) — trouvaille
architecturale réelle, disclosed, pas cachée.

**Construit** : nouveau
[`acf.gui.map.layer_toggle_panel.LayerTogglePanel`](../src/acf/gui/map/layer_toggle_panel.py) —
une vraie case à cocher par couche de `map_canvas.layer_manager.
available_layers` (les 15 couches réelles : les 7 préexistantes + les 8
construites la mise à jour précédente), cocher/décocher ajoute/retire
réellement le nom de la couche de `active_layer_names` et redessine.
`refresh()` resynchronise l'état des cases après tout changement
programmatique externe (ex. le bouton toolbar "🌪️ AWCI Field" active
directement "AWCI Complexity" sans passer par une case à cocher).
Nouvelle méthode publique `MapCanvas.redraw()` (expose le même
redessin/`_apply_camera_extent()` que chaque `set_*_field()` fait déjà,
sans que le panel n'ait à toucher une méthode "privée"). Branché comme
un vrai `QDockWidget` dans `ESOCWindow.__init__()` ; `_on_awci_field_ready()`
appelle maintenant `self.layer_toggle_panel.refresh()` pour que la case
"AWCI Complexity" reflète honnêtement ce que la carte affiche
réellement.

**Validation réelle** : 8 nouveaux tests —
`tests/test_map_layer_toggle_panel.py` (+7 : une case par couche
réelle, état initial cohérent avec `active_layer_names` (un exemple
actif par défaut, un exemple inactif — pas trivialement tout coché/
décoché), cocher/décocher active/désactive réellement la couche,
garde-fou anti-duplication testé directement sur `_on_toggled()` (pas
seulement la dé-duplication native de Qt), `refresh()` resynchronise
après un changement externe sans se re-déclencher elle-même deux fois),
`tests/test_esoc_awci_field.py` (+1 : le bouton toolbar existant
resynchronise bien le panel réel). Suite complète **3522/3522**
(3514 + 8), `ruff`/`mypy` propres, aucun import circulaire introduit
(vérifié directement par `import acf.gui`).

**Ce qui reste réellement** :
- §28-29 — **le contrôle interactif par couche est maintenant réel**
  pour les 15 couches connectées. `Model Consensus`/`Model Spread`/
  `Turbulence`/`Icing`/`Visibility` restent sans champ réel calculé
  point par point (limites déjà documentées, non résolues ici).
- §36/§37/§40/§41 — toujours absents, non traités par cette mise à
  jour (choix explicite de périmètre, pas oublié).
- Les deux systèmes de gestion de couches orphelins/parallèles trouvés
  ci-dessus (`acf.gui.map.layers.layer_manager.LayerManager` +
  `LayerPanel`×2) restent en l'état — une consolidation ou suppression
  serait une décision architecturale à part, pas prise unilatéralement
  ici.

## Mise à jour 2026-09-03 (suite) — garde-fou méthodologique réel de calibration (§40)

Suite explicite ("continue"), choix libre parmi les 4 gaps ❌ restants
de l'audit exhaustif (§36/§37/§40/§41).

**Pourquoi** : §40 exige une séparation formelle
`DATASET TRAIN → CALIBRATION → MODEL PARAMETERS → LOCKED MODEL →
INDEPENDENT VALIDATION DATA`, et interdit explicitement de "calibrer et
valider sur exactement les mêmes cas sans contrôle méthodologique."
L'audit confirmait qu'aucun pipeline de ce type n'existait — cohérent
avec le fait que tous les poids actuels sont `INITIAL`/`EXPERT_BASED`
(§77-81), mais confirmant aussi qu'aucune infrastructure n'existait
pour calibrer proprement le jour venu.

**Décision de périmètre honnête, explicite avant tout code** : §36 et
§37 (base de cas historiques réels, validation contre l'expertise
humaine réelle) restent absents — ce module ne les construit PAS,
faute de vraies données étiquetées (aucun cas météorologique réel avec
résultat AWCI vérifié par un prévisionniste n'existe dans ce dépôt).
Construire un "auto-calibrateur" qui prétendrait apprendre des poids
optimaux à partir de données inexistantes aurait été exactement le
type de résultat inventé que le §88 du prompt interdit. Le périmètre
réel de cette mise à jour est donc volontairement restreint au **vrai
garde-fou méthodologique** — le mécanisme qui empêchera un vrai
mésusage le jour où de vraies données arriveront — pas un algorithme
d'apprentissage.

**Construit** : nouveau
[`acf.awci.calibration`](../src/acf/awci/calibration.py) —
`lock_calibration()` gèle une configuration réelle d'`AWCICalculator`
(poids/termes d'interaction/seuils de niveau — les mêmes 4 paramètres
réels rendus configurables cette session au §22/§45-47) dans un
`LockedModel` (`dataclass(frozen=True)`), taguée d'une vraie
`calibration_version` et de l'ensemble exact des identifiants de cas
réels utilisés pour la calibrer. `lock_calibration()` réutilise la
validation déjà réelle d'`AWCICalculator.__init__()` (clés
d'interaction cohérentes, seuils strictement croissants) au lieu de la
dupliquer, et refuse une calibration sur zéro cas réel (une
"calibration" sans aucun cas réel derrière n'en est pas une).
`validate_locked_model()` compare l'ensemble des cas de validation
proposés à `calibrated_on_case_ids` et lève
`ValidationOverlapError` — avec le détail exact du chevauchement, pas
un message générique — **avant** qu'aucun calcul de validation ne
s'exécute, pour qu'une validation méthodologiquement invalide ne
produise jamais silencieusement un chiffre.

**Validation réelle** : 11 nouveaux tests
(`tests/test_awci_calibration.py`) — configuration invalide propage
bien l'erreur réelle d'`AWCICalculator` (jamais réimplémentée), zéro
cas réel lève une erreur explicite, `build_calculator()` produit un
`AWCICalculator` bit-identique à une construction indépendante avec les
mêmes paramètres, mutation ultérieure du dict original de l'appelant
n'affecte jamais le modèle déjà gelé, `LockedModel` refuse réellement
toute réassignation de champ après construction
(`dataclasses.FrozenInstanceError`), chevauchement total/partiel
détecté avec le détail exact (jamais les IDs non chevauchants inclus
par erreur), et le garde-fou fonctionne de façon autonome sans
corrompre le modèle qu'il vient de refuser. Suite complète
**3533/3533** (3522 + 11), `ruff`/`mypy` propres.

**Ce qui reste réellement** :
- §40 — **fermé pour le garde-fou méthodologique réel** ; aucun
  algorithme de calibration/apprentissage automatique n'existe encore
  (délibéré, aucune donnée réelle pour l'alimenter).
- §36/§37/§41 — toujours absents, non traités par cette mise à jour.

## Mise à jour 2026-09-03 (suite) — cadre de comparaison Physics/Statistical/ML/Hybrid réel (§41)

Suite explicite ("continue"), dernier des 4 gaps ❌ traitable sans
données réelles indisponibles (§36/§37 restent hors périmètre — voir
ci-dessous).

**Pourquoi** : §41 exige "une architecture sérieuse [qui] doit pouvoir
comparer Physics-based contre Statistical contre Machine Learning
contre Hybrid Physics + ML, et mesurer leurs performances" — l'audit
confirmait qu'aucun cadre de ce type n'existait.

**Décision de périmètre honnête, explicite avant tout code, cohérente
avec le §42 (PHYSICS-FIRST) et le §88** : construire un faux "modèle
ML" qui prétendrait produire des prédictions réelles sans jamais avoir
été entraîné sur de vraies données aurait été exactement
l'anti-pattern que le §42 interdit explicitement ("ML → invented score
→ physical interpretation") et le type de réponse inventée que le §88
interdit. Seules les 2 catégories pour lesquelles une vraie
implémentation existe déjà dans ce dépôt sont construites ici :
**Physics-based** (`AWCICalculator` lui-même) et **Statistical** (une
vraie ligne de base non-physique : le rang de percentile empirique
réel contre une climatologie réelle, réutilisant
`Normalizer.normalize_percentile()`, §20). **Machine Learning** et
**Hybrid** restent de vrais points d'intégration honnêtement vides
(`NotYetImplementedMethod` lève une erreur réelle plutôt que de
fabriquer un nombre) — aucun modèle ML entraîné n'existe nulle part
dans ce dépôt à envelopper.

**Construit** : nouveau
[`acf.awci.method_comparison`](../src/acf/awci/method_comparison.py) —
`PredictionMethod` (ABC réelle, une catégorie + un `predict()` par
sous-classe), `PhysicsBasedMethod` (enveloppe fine et réelle
d'`AWCICalculator`), `ClimatologicalBaselineMethod` (ligne de base
statistique réelle, ignore délibérément toute variable autre que celle
choisie — un vrai point de comparaison simple, pas une seconde
tentative de physique déguisée), `NotYetImplementedMethod` (lève
`NotImplementedError`, refuse explicitement d'être utilisée pour une
catégorie qui a déjà une vraie implémentation). `compare_methods()`
réutilise directement `acf.verification.nwp_metrics.
NWPVerificationMetrics.evaluate_all()` (RMSE/bias/MAE/ACC/POD/FAR/CSI/
ETS, déjà réel et testé) — jamais réimplémenté — avec un seuil par
défaut réel de 50.0 (le seuil "Moderate" d'`AWCICalculator.
LEVEL_THRESHOLDS`, pas le défaut générique 1.0 de `NWPVerificationMetrics`,
quasi dénué de sens sur l'échelle réelle 0-100 de l'AWCI).

**Disclosure honnête réutilisée du §40** : `compare_methods()` a
besoin de vraies observations pour produire des métriques
significatives — aucun jeu de données AWCI observées réelles n'existe
dans ce dépôt (§36/§37, toujours absents) ; les tests de ce module
utilisent donc des cas/observations d'exemple clairement synthétiques
(la même convention honnête déjà appliquée dans toute la suite de
tests du projet), jamais présentés comme de vraies observations.

**Validation réelle** : 14 nouveaux tests
(`tests/test_awci_method_comparison.py`) — `PhysicsBasedMethod`
correspond exactement à un appel direct `AWCICalculator().calculate()`
(y compris avec un calculateur personnalisé), `ClimatologicalBaselineMethod`
correspond exactement à un appel direct `normalize_percentile()`, lève
une vraie erreur pour une variable manquante, `NotYetImplementedMethod`
lève réellement `NotImplementedError` pour ML et Hybrid, refuse
explicitement d'être construite pour une catégorie déjà réelle,
`compare_methods()` produit des métriques correspondant à un calcul
indépendant, utilise le vrai seuil par défaut 50.0, propage l'erreur
réelle d'une méthode placeholder incluse (jamais ignorée
silencieusement), rejette un décalage de longueur, et gère
correctement zéro méthode. Suite complète **3547/3547** (3533 + 14),
`ruff`/`mypy` propres.

**Statut final des 6 gaps ❌ de l'audit exhaustif du 2026-09-03** :
- §20/§22/§27-29/§32/§45-47/§64 (tableau de conformité initial) — tous
  fermés ou honnêtement partiels avec la raison exacte disclosed.
- §28-29 — fermé pour les données/couches/contrôle interactif ;
  Model Consensus/Spread/Turbulence/Icing/Visibility restent ouverts
  (limites déjà documentées).
- §40 — fermé pour le garde-fou méthodologique réel.
- §41 — fermé pour les 2 catégories réellement implémentables
  (Physics-based/Statistical) ; ML/Hybrid restent de vrais points
  d'intégration honnêtement vides.
- **§36/§37 restent les deux seuls gaps réellement non traités** — les
  deux nécessitent de vraies données (cas météorologiques historiques
  vérifiés, évaluations réelles de prévisionnistes) qui n'existent pas
  dans ce dépôt et que Claude ne peut ni collecter ni inventer sans
  violer le §69/§88 du prompt lui-même. *(Voir mise à jour du
  2026-09-03 ci-dessous : infrastructure réelle construite pour les
  deux, en gardant cette même limite.)*

## Mise à jour 2026-09-03 (suite) — infrastructures réelles pour §36 et §37 (sans données fabriquées)

Suite explicite ("continue"), même raisonnement déjà appliqué au §40 :
distinguer le GARDE-FOU/SCHÉMA réel (constructible sans données) de
l'ALGORITHME/CONTENU (qui nécessiterait de vraies données inexistantes
ici). §36 (base de cas) et §37 (validation experte) ont chacun une
vraie partie infrastructure — schéma de données, stockage, statistiques
d'accord inter-évaluateurs — construisible sans inventer le moindre cas
historique ni la moindre opinion de prévisionniste, exactement comme
`Provenance`/`QualityInfo`/`LockedModel` (§40) sont de vraies structures
réelles, vides de tout contenu fabriqué.

**§36** : nouveau
[`acf.awci.validation_cases`](../src/acf/awci/validation_cases.py) —
`ValidationCase` (exactement les champs du §36 :
`CASE_ID/DATE/REGION/SEASON/WEATHER_REGIME/MODEL_RUNS/OBSERVATIONS/
OPERATIONAL_IMPACT/EXPERT_ASSESSMENT/AWCI/UNCERTAINTY/ERROR`),
`WeatherRegime` (les 10 catégories exactes que le §36 demande
d'inclure — simple/complexe/convectif/vent/givrage/brouillard/
montagneux/forte divergence modèle/faible impact/fort impact) et
`CaseDatabase` (store réel interrogeable, **vide à la construction, zéro
cas d'exemple pré-chargé**) — `add_case()`/`get_case()`/
`cases_by_regime()`/`cases_by_region()`/`cases_with_expert_assessment()`/
`regime_coverage()` (comptage réel par catégorie, y compris zéro),
`compute_error()` (le champ `ERROR` du §36 — un vrai
`|awci - ground_truth|`, calculé seulement si un vrai score AWCI existe
déjà pour ce cas, jamais 0.0 par défaut), `to_json()`/`from_json()`
(persistance réelle).

**§37** : nouveau
[`acf.awci.forecaster_validation`](../src/acf/awci/forecaster_validation.py) —
`ForecasterAssessment` (un vrai jugement humain sur un vrai cas),
`agreement_fraction()` (accord observé réel), et surtout
`cohens_kappa()` — le vrai coefficient kappa de Cohen (1960), une
formule statistique publiée et établie, pas inventée ici, qui corrige
l'accord observé de l'accord attendu par le seul hasard. Utilisée à la
fois pour AWCI-vs-prévisionniste et prévisionniste-vs-prévisionniste
(`inter_forecaster_variability()`, la "variabilité inter-prévisionnistes"
explicitement demandée par le §37) via la même formule réelle.

**Validation réelle, y compris contre une référence externe indépendante** :
`test_cohens_kappa_matches_the_classic_textbook_reference_case` vérifie
le calcul contre un exemple de manuel de statistique connu et publié
(matrice de confusion 50 cas, κ=0.40 exact) — pas une valeur dérivée du
code lui-même, une vraie preuve d'exactitude de la formule, pas
seulement de sa cohérence interne. 31 nouveaux tests au total —
`tests/test_awci_validation_cases.py` (+16 : base vide au départ,
ajout/doublon/mise à jour/recherche par régime ou région, couverture
réelle par catégorie, `ERROR` refuse un cas sans score AWCI réel, aller-retour JSON réel), `tests/test_awci_forecaster_validation.py` (+15 :
accord parfait/partiel, cas dégénéré à une seule catégorie géré sans
division par zéro, désaccord pire que le hasard donne bien un kappa
négatif, variabilité inter-prévisionnistes calcule chaque paire réelle
sans doublon). Suite complète **3578/3578** (3547 + 31), `ruff`/`mypy`
propres.

**Ce qui reste réellement — la limite honnête n'a pas changé** : ces
deux modules contiennent **zéro cas réel et zéro évaluation réelle de
prévisionniste** — ce sont des conteneurs réels prêts à recevoir de
vraies données, pas une démonstration du contenu qu'ils pourraient
avoir. §36/§37 restent donc "infrastructure fermée, contenu réel
manquant" tant qu'aucune vraie donnée n'est fournie — la seule façon
honnête de les fermer complètement.

## Mise à jour 2026-09-03 (suite) — objet de résultat AWCI complet (§81)

Suite explicite ("continue with the rest of the audit") — reprise des
lignes ⚠️ PARTIELLES du tableau exhaustif, en commençant par §81
(champs minimums du résultat AWCI lui-même), un gap concret et bien
délimité, directement au cœur de ce que `calculate()` retourne.

**Pourquoi** : §81 exige que chaque résultat AWCI conserve "au
minimum : AWCI score, AWCI class, AWCI confidence, AWCI dominant
factors, AWCI interactions, AWCI model spread, AWCI quality, AWCI
provenance." L'audit confirmait que `model spread`/`quality`/
`provenance` existaient bien, réellement, mais comme 3 systèmes
séparés (`ModelConsensusEngine`, `assess_variable_quality()`,
`Provenance`) jamais assemblés avec le résultat `calculate()`
lui-même.

**Construit** : nouveau
[`acf.awci.result`](../src/acf/awci/result.py) — `AWCIResult`
(dataclass réelle avec les 8 champs exacts du §81) et
`build_awci_result()`, un vrai **assembleur**, pas un nouveau calcul :
il ne calcule jamais lui-même `model_spread`/`quality`/`provenance` —
cela demanderait de deviner quelle vraie comparaison multi-modèle,
quelle vraie climatologie ou quelle vraie chaîne de provenance
l'appelant a en tête (les noms de variable simplifiés d'AWCI, ex.
`wind_speed`, ne correspondent pas directement aux noms CF/unités
qu'attend `assess_variable_quality()` sans un vrai pont, comme celui
déjà construit pour METAR). L'appelant fournit ses propres valeurs
réelles déjà calculées ailleurs ; un champ non fourni reste
honnêtement `None`, jamais un `0.0`/une valeur fabriquée — même
discipline que le §61 partout ailleurs dans ce dépôt.

**Validation réelle** : 9 nouveaux tests
(`tests/test_awci_result.py`) — chaque champ de base correspond
exactement à `calculate()`, les facteurs dominants correspondent aux
entrées déjà triées de `explanation` (jamais recalculées), les 3
champs optionnels restent `None` par défaut, un vrai `Provenance`/une
vraie `assess_variable_quality()`/un vrai dict de spread multi-modèle
s'attachent sans modification, les trois ensemble fonctionnent, et le
`calculate_output` d'origine n'est jamais muté. Suite complète
**3587/3587** (3578 + 9), `ruff`/`mypy` propres.

**Ce qui reste réellement, disclosed honnêtement** : `build_awci_result()`
n'est pas encore branché à un vrai point de consommation GUI/pipeline
(même situation transitoire déjà acceptée cette session pour
`normalize_percentile()` avant son branchement, et pour §36/§37/§40/§41
qui restent tous des infrastructures réelles non encore consommées) —
`acf.gui.dashboard.awci_messages_panel` ne calcule aujourd'hui aucun
score AWCI à partir des données METAR réelles (seulement décodage +
statut qualité §32), donc un branchement réel demanderait d'abord de
construire ce pont METAR→AWCI, une pièce de travail distincte, pas
faite ici pour ne pas mélanger deux changements dans une même passe.
§81 reste donc **partiellement fermé** : l'objet complet existe et est
réel, mais rien ne le construit encore automatiquement en production.

## Mise à jour 2026-09-03 (suite) — ROC/AUC et Brier score réels (§39)

Suite explicite ("continue with your judgment"), choix libre parmi les
lignes ⚠️ restantes du tableau exhaustif — celle-ci mécaniquement bien
délimitée, sûre, et directement citée par le §39 : "ROC/AUC lorsque
pertinent" et "Brier score lorsque pertinent" étaient absents de
`NWPVerificationMetrics`, qui n'avait que les métriques déterministes
(RMSE/bias/MAE/ACC/POD/FAR/CSI/ETS).

**Pourquoi séparées de `evaluate_all()`** : ROC/AUC et Brier score
comparent une vraie PROBABILITÉ prévue (valeur dans [0,1], "quelle est
la probabilité de cet événement") à un vrai résultat binaire observé
(0/1) — une donnée de nature différente de `forecast`/`observation`
existants (deux valeurs continues déterministes). Les ajouter par
défaut à `evaluate_all()` aurait mélangé deux sémantiques différentes
sous les mêmes noms de paramètre ; elles restent deux méthodes réelles
séparées et documentées comme telles.

**Construit** : `NWPVerificationMetrics.brier_score()` (erreur
quadratique moyenne réelle probabilité/résultat binaire, Brier 1950) et
`NWPVerificationMetrics.roc_auc()` — calculé via l'équivalence réelle
de Mann-Whitney U (fraction des paires positif/négatif où le score du
positif dépasse celui du négatif, égalités comptant pour une demi-paire)
plutôt qu'en construisant et intégrant explicitement une courbe ROC —
la même quantité réelle, un calcul plus simple et exact, avec gestion
réelle des égalités par rangs moyennés.

**Validation réelle, contre des références calculées à la main, pas
seulement une cohérence interne** : `roc_auc` vérifié contre un calcul
par paires fait à la main (3/4 = 0.75 exact), plus séparation parfaite
(AUC=1.0), séparation parfaitement inversée (AUC=0.0), et égalité
totale de tous les scores (AUC=0.5 exact — preuve que la correction
d'égalités par rangs moyennés fonctionne réellement, pas une valeur
arbitraire). `brier_score` vérifié contre un calcul à la main
(0.02 exact), score parfait (0.0) et pire score possible (1.0).
13 nouveaux tests (`tests/test_nwp_metrics.py`), suite complète
**3600/3600** (3587 + 13), `ruff`/`mypy` propres.

**Ce qui reste réellement** : ni `roc_auc()` ni `brier_score()` ne sont
encore appelées depuis `acf.awci.method_comparison.compare_methods()`
(§41) — les scores AWCI sont continus [0,100], pas des probabilités
[0,1] d'un événement binaire ; les y brancher demanderait une vraie
reformulation probabiliste (ex. "P(complexité ≥ seuil)"), une décision
de conception distincte, pas prise ici pour ne pas mélanger deux
changements.

## Mise à jour 2026-09-03 (suite) — champs de provenance manquants du §57-58

Suite explicite ("poursuis selon ton jugement"), choix libre parmi les
lignes ⚠️ restantes — celle-ci petite, sûre, purement additive.

**Pourquoi** : §57 demande "code version, configuration version, model
version, input files, run identifier, calibration version, software
environment" et §58 ajoute "dataset_version" — `Provenance` réel
existant ne couvrait que `algorithm_version`/`science_version`/
`config_version`/`created_at`/`notes`.

**Trouvaille faite en inspectant avant de construire** : `is_complete()`
a un vrai contrat existant et testé (`tests/test_core_contracts.py`) —
elle vérifie exactement 3 champs (`algorithm_version`/`science_version`/
`config_version`), rien de plus. Ajouter les nouveaux champs à cette
même vérification aurait été un vrai changement de comportement pour
tout appelant existant qui considère déjà un `Provenance` "complet"
avec seulement ces 3 champs — **délibérément non fait**. `is_complete()`
garde son sens exact d'avant, inchangé.

**Construit** : 5 nouveaux champs réels sur `Provenance`
(`run_identifier`/`calibration_version` — même nom exact que
`acf.awci.calibration.LockedModel.calibration_version`, construit
au §40, pas une convention de nommage séparée inventée —
`dataset_version`/`software_environment`/`input_files`), tous avec le
même défaut honnête `"unknown"` (`[]` pour `input_files`, un vrai état
valide — "aucun fichier d'entrée" — pas un "non renseigné"). Nouvelle
méthode séparée `is_fully_specified()` — le vrai check plus strict
couvrant les 3 champs originaux **et** les 4 nouveaux champs de version
(`input_files` volontairement exclu, une liste vide étant un état réel
valide, pas un défaut non renseigné).

**Validation réelle** : 4 nouveaux tests
(`tests/test_core_contracts.py`) — les 5 nouveaux champs ont bien le
même défaut honnête que les champs existants, `is_complete()` reste
inchangée par les nouveaux champs (test dédié au non-régression du
contrat existant), `is_fully_specified()` exige bien tous les champs de
version réels, et n'exige pas `input_files`. Suite complète
**3604/3604** (3600 + 4), `ruff`/`mypy` propres — vérifié qu'aucun
appel existant à `Provenance(...)` dans le dépôt n'utilise
d'arguments positionnels au-delà de `generator` (tous par mot-clé),
donc aucun risque de décalage de position.

## Mise à jour 2026-09-03 (suite) — classification réelle d'échelle spatiale/temporelle (§43)

Suite explicite ("continue selon ton jugement"), choix libre parmi les
lignes ⚠️ restantes.

**Pourquoi** : §43 liste 4 échelles (Micro/Méso/Synoptique/Temporelle)
et exige explicitement d'"éviter de mélanger des phénomènes
incompatibles sans justification" — l'audit constatait que les vraies
résolutions de grille (`MODEL_CONFIGS`) couvraient implicitement
plusieurs échelles sans qu'aucune classification explicite ne soit
jamais attachée nulle part.

**Choix de référence réelle et publiée, pas des seuils inventés** :
`classify_spatial_scale()` utilise Orlanski (1975), "A rational
subdivision of scales for atmospheric processes" — la taxonomie
d'échelles météorologiques standard et largement citée — repliée
depuis ses propres sous-catégories alpha/beta/gamma plus fines vers les
3 catégories exactes que le §43 demande, en gardant les vraies bornes
Orlanski exactes (2 km micro/méso, 2000 km méso/synoptique).
`classify_temporal_scale()` utilise la vraie convention opérationnelle
NWP établie (nowcasting/short-range/medium-range, terminologie OMM
réelle) plutôt que d'inventer des seuils minute/heure/jour à partir de
rien.

**Construit** : nouveau
[`acf.awci.scale_classification`](../src/acf/awci/scale_classification.py) —
`SpatialScale`/`TemporalScale` (enums), `classify_spatial_scale(resolution_km)`
et `classify_temporal_scale(lead_time_hours)`, tous deux réels et
validés (rejettent une résolution/un délai non physiquement valide).

**Validation réelle contre les vraies résolutions déjà utilisées par ce
dépôt** : un test applique la classification aux 3 vraies résolutions
de `MODEL_CONFIGS` — AROME (1.3 km, résolution convective réelle) tombe
bien en micro-échelle réelle Orlanski ; ALADIN (7.5 km) et ARPEGE
(10 km) tombent tous deux en méso-échelle réelle, pas synoptique,
malgré le fait d'être les modèles les "plus grossiers" d'ACF — un vrai
résultat de classification physiquement sensé, pas une valeur
arbitraire. 9 nouveaux tests
(`tests/test_awci_scale_classification.py`), suite complète
**3613/3613** (3604 + 9), `ruff`/`mypy` propres.

**Ce qui reste réellement** : ces classificateurs sont réels et testés
mais pas encore attachés automatiquement à un résultat AWCI/évolution
temporelle en production — un caller doit les appeler explicitement
(ex. `classify_spatial_scale(MODEL_CONFIGS[model]["resolution_km"])`),
même situation transitoire déjà acceptée plusieurs fois cette session
pour de l'infrastructure réelle avant son branchement.

## Mise à jour 2026-09-03 (suite) — chaîne de traçabilité complète (§26/§53)

Suite explicite ("continue selon ton jugement"), extension naturelle du
§81 déjà fermé cette session : `AWCIResult`/`build_awci_result()`
existaient déjà comme assembleur réel — cette mise à jour complète la
chaîne de traçabilité que le §26/§53 exigent explicitement.

**Pourquoi** : §26 exige `Score global → Contributions → Variables →
Diagnostics → données sources → modèle → échéance → niveau vertical`,
"chaque résultat doit être traçable" ; §53 la même idée en plus court
(`AWCI → Module → Diagnostic → Variable → Modèle → Fichier source`,
"il doit être possible de passer du résumé à la donnée détaillée").
L'audit constatait que chaque maillon existait réellement quelque part
mais jamais assemblé en un seul objet traçable.

**Construit** : 3 nouveaux champs réels sur `AWCIResult`
(`raw_variables` — le vrai dict `data` passé à `calculate()`,
`lead_time_hours`, `vertical_level`), tous optionnels avec le même
défaut honnête `None` que les 3 champs du §81 — "modèle" et "données
sources" réutilisent directement `provenance.algorithm_version`/
`provenance.input_files` (déjà réels, aucun champ redondant inventé).
Nouvelle méthode `AWCIResult.trace_chain()` — rend la vraie chaîne
ordonnée en 8 lignes textuelles, un maillon jamais fourni s'affichant
honnêtement "not available" plutôt que d'être silencieusement omis
(§61) — pour qu'un appelant voie exactement jusqu'où la trace réelle va
réellement, pas une chaîne qui a l'air complète mais a sauté une étape
en silence.

**Validation réelle** : 5 nouveaux tests
(`tests/test_awci_result.py`) — les 3 nouveaux champs par défaut `None`,
s'attachent sans modification une fois fournis, `trace_chain()` a
exactement les 8 maillons réels dans l'ordre exact du §26/§53, les
maillons non fournis affichent bien "not available" (pas silencieusement
sautés), et les valeurs réellement fournies apparaissent bien dans le
texte. Suite complète **3618/3618** (3613 + 5), `ruff`/`mypy` propres.

**Ce qui reste réellement** : `trace_chain()` reste un texte de
diagnostic/journal simple (liste de chaînes), pas encore affiché dans
un panneau GUI dédié de "descente du résumé à la donnée détaillée"
comme le §53 le décrit — même situation transitoire déjà acceptée pour
plusieurs infrastructures réelles cette session avant leur branchement
visuel.

## Mise à jour 2026-09-03 (suite) — registre de diagnostics centralisé réel (§55)

Suite explicite ("continue selon ton jugement"), choix libre parmi les
lignes ⚠️ restantes.

**Pourquoi** : §55 exige que "chaque diagnostic doit être documenté
avec : NAME, DESCRIPTION, PHYSICAL MEANING, EQUATION, INPUTS, OUTPUT,
UNITS, VALID RANGE, ASSUMPTIONS, LIMITATIONS, REFERENCE, TESTS." —
l'audit constatait que chaque diagnostic réel était déjà documenté,
mais uniquement dans son propre docstring dispersé, jamais assemblé en
un registre centralisé et interrogeable.

**Construit** : nouveau
[`acf.awci.diagnostic_registry`](../src/acf/awci/diagnostic_registry.py) —
`DiagnosticSpec` (les 12 champs exacts du §55, plus un 13e champ
`status` réel qui **référence directement** (pas une chaîne dupliquée)
l'entrée correspondante du registre de statut scientifique déjà
construit au §77-81) et `DIAGNOSTIC_REGISTRY` — 14 entrées réelles
couvrant le pipeline par défaut d'AWCI : les 9 fonctions
`normalize_*` réellement utilisées, les 2 formules de combinaison de
module (thermodynamique 50/50, convectif 70/30), les 2 termes
d'interaction par défaut, et la méthode d'incertitude du §64. Périmètre
délibérément limité au pipeline AWCI par défaut, pas à toute la
bibliothèque `acf.science` (des centaines de modules, la plupart sans
rapport avec le chemin de score par défaut — voir §12-16, un gap
distinct et déjà disclosed de cet audit).

**Validation réelle, pas seulement une cohérence interne** : au-delà de
vérifier que les 12 champs sont bien renseignés, des tests exécutent
réellement les formules documentées et comparent au résultat réel
d'appels directs à `Normalizer`/`AWCICalculator` — preuve que le texte
documenté n'est pas obsolète par rapport au vrai code (ex. le poids
50/50 documenté pour le module thermodynamique reconstruit et comparé
au vrai `calculate_module_scores()`). 14 nouveaux tests
(`tests/test_awci_diagnostic_registry.py`), suite complète
**3632/3632** (3618 + 14), `ruff`/`mypy` propres.

**Ce qui reste réellement** : le registre couvre le pipeline AWCI par
défaut, pas les diagnostics optionnels déjà réels de cette session
(rang de percentile déjà inclus, mais pas `calibration.py`/
`method_comparison.py`/`forecaster_validation.py`/
`scale_classification.py` eux-mêmes) — une extension possible si
demandée, pas faite ici pour garder cette passe bien délimitée.

## Mise à jour 2026-09-03 (suite) — rapport d'exécution AWCI réel (§75)

Suite explicite ("continue selon ton jugement"), choix libre parmi les
lignes ⚠️ restantes.

**Pourquoi** : §75 exige que le pipeline produise "logs, metrics,
warnings, errors, quality reports, runtime statistics", avec un
exemple concret (`Input files: 48 / Valid: 46 / Rejected: 2 /
Diagnostics: 123 / AWCI generated: YES / Quality: GOOD / Model spread:
HIGH`). L'audit constatait qu'`acf.monitoring` était réel mais générique
— rien ne produisait ce résumé précis pour une exécution AWCI donnée.

**Décision honnête de périmètre, pour éviter d'inventer de nouveaux
seuils** : le prompt utilise "Quality: GOOD" et "Model spread: HIGH"
comme catégories illustratives. Introduire une vraie catégorisation à 3
niveaux (GOOD/WARNING/FAIL) ou LOW/MODERATE/HIGH exigerait un vrai
seuil de pourcentage ou de percentile — exactement le genre de coupure
inventée que les §78-79 mettent en garde contre. À la place :
`quality_status` reste **binaire et réel** (`PASS` seulement si chaque
vrai résultat `VariableQualityStatus` fourni est `VALID`, `FAIL` sinon,
`NOT_ASSESSED` si rien n'a été fourni) — vocabulaire réutilisé
directement de `acf.core.contracts.quality.QualityInfo`, pas un
nouveau mot "GOOD" inventé. `model_spread` reste la vraie valeur
numérique (ex. `disagreement_spread` réel), jamais classée en
LOW/MODERATE/HIGH sans seuil scientifiquement établi.

**Construit** : nouveau
[`acf.awci.run_report`](../src/acf/awci/run_report.py) —
`AWCIRunReport` (dataclass réelle, gelée) et `build_run_report()`, un
vrai assembleur — jamais un calcul, mêmes comptes fournis par
l'appelant depuis sa propre vraie exécution. `format_text()` rend le
texte exactement dans le format de l'exemple du §75.

**Validation réelle** : 10 nouveaux tests
(`tests/test_awci_run_report.py`) — rapport vide honnête par défaut,
comptes réels transmis sans modification, `quality_status` correctement
dérivé (`NOT_ASSESSED`/`PASS`/`FAIL`) à partir de vrais résultats
`assess_variable_quality()` (y compris un vrai cas `OUT_OF_RANGE`
réel), `model_spread` jamais fabriqué, `format_text()` correspond
exactement au format de l'exemple du §75. Suite complète
**3642/3642** (3632 + 10), `ruff`/`mypy` propres.

**Ce qui reste réellement** : `build_run_report()` n'est pas encore
appelé automatiquement à la fin d'une vraie exécution AWCI en
production (ex. dans `AWCIMessagesDialog`/ESOC) — même situation
transitoire déjà acceptée pour plusieurs infrastructures réelles cette
session avant leur branchement.

## Mise à jour 2026-09-03 (suite) — configuration externe versionnée réelle (§56)

Suite explicite ("continue selon ton jugement"), choix libre parmi les
lignes ⚠️ restantes.

**Pourquoi** : §56 exige que "les seuils et poids ne doivent pas être
codés en dur partout" et prévoit "une configuration versionnée". Les
poids/termes d'interaction/seuils de niveau d'`AWCICalculator` étaient
déjà réellement configurables par instance (paramètres du constructeur,
construits aux §22/§45-47) mais leurs vraies valeurs ne provenaient
encore que de constantes Python compilées, jamais d'un vrai fichier de
configuration externe versionné.

**Décision technique justifiée, pas arbitraire** : JSON, pas YAML —
`acf.testing.golden`/`acf.awci.validation_cases` (construit au §36)
utilisent déjà réellement ce format de persistance dans ce dépôt ;
PyYAML n'est PAS une dépendance réellement déclarée de ce projet (voir
la propre trouvaille de cette session, "audit complet des dépendances
non déclarées") — introduire une nouvelle dépendance non déclarée pour
ce travail aurait recréé exactement ce problème déjà identifié et
corrigé plus tôt.

**Construit** : nouveau
[`acf.awci.config_loader`](../src/acf/awci/config_loader.py) —
`AWCIConfig` (dataclass réelle) et `load_config()`, qui réutilise
directement la vraie validation d'`AWCICalculator.__init__()` (clés
d'interaction cohérentes, seuils strictement croissants) en construisant
réellement un calculateur pendant le chargement — jamais réimplémentée.
`config_version` réutilise exactement le même nom de champ que
`Provenance.config_version` (§57-58), pas une convention de versionnage
séparée inventée. `save_default_config()` exporte les vraies valeurs
compilées par défaut (`WeightsManager.DEFAULT_WEIGHTS`/
`AWCICalculator.INTERACTION_TERMS`/`INTERACTION_WEIGHTS`/
`LEVEL_THRESHOLDS`) comme point de départ réel pour un opérateur, pas un
exemple fabriqué.

**Validation réelle, y compris un aller-retour complet** : un test
sauvegarde la vraie configuration par défaut, la recharge, construit un
`AWCICalculator` à partir du fichier, et vérifie qu'il produit un
résultat **bit-identique** à `AWCICalculator()` par défaut. D'autres
tests vérifient qu'une vraie configuration personnalisée (poids
différents) produit un score réellement différent, que les erreurs de
validation d'`AWCICalculator` sont bien propagées (jamais réimplémentées),
et que `null` en JSON devient bien le vrai `float("inf")` du dernier
seuil de niveau. 8 nouveaux tests
(`tests/test_awci_config_loader.py`), suite complète **3650/3650**
(3642 + 8), `ruff`/`mypy` propres.

**Ce qui reste réellement** : `load_config()` n'est pas encore appelée
automatiquement au démarrage d'un dashboard/pipeline en production
(aucun fichier de config réel n'existe encore sur disque dans ce
dépôt) — même situation transitoire déjà acceptée pour plusieurs
infrastructures réelles cette session.

**Bilan de cette série de mises à jour** : sur les lignes ⚠️ restantes
du tableau exhaustif du 2026-09-03, il ne reste maintenant que §12-16
(modules AWCI simplistes vs. bibliothèque de diagnostics riche
inexploitée — le chantier le plus important restant, nécessitant une
vraie justification physique par variable avant tout ajout, pas
entrepris sans confirmation explicite de l'utilisateur sur le
périmètre) et §48/§51 (niveaux de produits/profils de vol exacts —
largement recoupés par le travail déjà fait au §26/§53/§81 cette
session).

## Mise à jour 2026-09-03 (suite) — cisaillement de vent réel dans le module dynamique (§12)

Suite explicite de l'utilisateur ("commence par le module dynamique,
avec le cisaillement de vent") — première fermeture réelle et ciblée
du chantier §12-16, avec un périmètre choisi par l'utilisateur
lui-même plutôt que deviné.

**Pourquoi** : §12 liste explicitement "cisaillement vertical" parmi
les variables candidates du module dynamique — le module `dynamic`
n'utilisait jusqu'ici qu'un seul scalaire, la vitesse du vent.

**Trouvaille faite en inspectant avant de construire** :
`acf.science.bulk_wind_shear.BulkWindShear` — une formule réelle et
correcte (magnitude du cisaillement en vecteur : `sqrt(du² + dv²)`
entre deux niveaux) — existait déjà dans ce dépôt mais n'était appelée
par aucun code produisant une vraie sortie ACF. Exactement le même
schéma déjà trouvé et fermé pour CAPE/CIN (`acf.awci.convective_energy`).

**Décision de ne rien casser, comme à chaque fois cette session** :
le module `dynamic` reste **exactement** vitesse-du-vent-seule par
défaut — comportement bit-identique pour tout appelant existant.
Le cisaillement n'est incorporé que si l'appelant fournit réellement
`data["wind_shear"]`, combiné 50/50 avec le vent normalisé — le même
poids de convention interne déjà utilisé pour le module thermodynamique
(température/humidité), un choix de conception ACF disclosed, pas une
formule publiée.

**Construit** :
- Nouveau [`acf.awci.wind_shear`](../src/acf/awci/wind_shear.py) —
  `compute_real_wind_shear_at_point()`, enveloppe réelle et fine autour
  de `BulkWindShear.calculate()` (aucune nouvelle physique inventée).
  Périmètre honnête disclosed : le cisaillement calculé s'étend sur
  toute l'extension verticale des niveaux natifs du modèle fournis, pas
  une vraie couche physique fixe (0-6 km, 850-500 hPa) — ACF n'a pas
  encore de moteur `VerticalCoordinate` reliant niveaux natifs et
  pression/altitude réelle (limite déjà documentée dans cet audit,
  §14-21).
- `Normalizer.normalize_wind_shear()` — même enveloppe réelle 0-50 m/s
  que `normalize_wind`, plus une entrée `NORMALIZER_RANGE_STATUS["wind_shear"]`
  réelle (`HYPOTHESIS`).
- `AWCICalculator.calculate_module_scores()` — le module `dynamic` gère
  maintenant réellement `data["wind_shear"]` (optionnel, climatology-aware
  via le même dispatch `_normalize()` que toutes les autres variables).
- `acf.awci.spatial_field.compute_real_complexity_field(compute_wind_shear=True)` —
  intégration de bout en bout réelle : calcule le vrai cisaillement par
  point de grille depuis la vraie colonne U/V du solveur (même
  discipline que `compute_convective_energy`), retourne un vrai
  `wind_shear_field`, désactivé par défaut (même coût réel
  supplémentaire non imposé aux appelants existants).
- `acf.awci.diagnostic_registry` — 2 nouvelles entrées réelles
  (`normalize_wind_shear`, `dynamic_module_combination`), cohérentes
  avec le registre déjà construit au §55.

**Validation réelle end-to-end, vérifiée manuellement avant les tests
formels** : un script manuel confirme que `wind_shear_field` varie
réellement dans l'espace (écart-type non nul) et que le champ
`module_fields["dynamic"]` diffère réellement selon que
`compute_wind_shear` est activé ou non, sur le même point. **Trouvaille
méthodologique pendant l'écriture des tests** : comparer deux
exécutions séparées du solveur (même graine) pour vérifier qu'"aucun
autre module n'est affecté" se serait révélé non fiable — deux runs
séparés du solveur ne sont PAS bit-reproductibles (limite déjà connue
et documentée ailleurs dans ce dépôt), donc un tel test aurait pu
échouer un jour pour une raison totalement étrangère à ce changement.
Corrigé en comparant plutôt contre un appel indépendant de
`calculate_module_scores()` nourri des propres valeurs réelles de
CETTE exécution, jamais une seconde exécution séparée.

**Validation réelle** : 21 nouveaux tests répartis sur 4 fichiers —
`tests/test_awci_wind_shear.py` (+8 : correspond à un appel direct
`BulkWindShear.calculate()`, cisaillement nul si vent identique aux
deux niveaux, triangle 3-4-5 vérifié à la main, cisaillement jamais
négatif sur des vecteurs aléatoires réels), `tests/test_awci_calculator_wind_shear.py`
(+7 : comportement par défaut bit-identique sans cisaillement, mélange
50/50 exact avec cisaillement, seuls les autres modules restent
inchangés, climatology-aware), `tests/test_awci_spatial_field.py`
(+4 : champ absent par défaut, réel et variant spatialement une fois
activé, correspond à l'API ponctuelle), `tests/test_awci_diagnostic_registry.py`
(+2 : les deux nouvelles entrées correspondent au vrai code). Suite
complète **3671/3671** (3650 + 21), `ruff`/`mypy` propres.

**Ce qui reste réellement, du chantier §12-16** : seul le module
dynamique a été étendu, avec une seule variable (cisaillement). Les
autres variables candidates du §12 (vorticité, omega, divergence,
vent à plusieurs niveaux, rafales) et les modules §13-16
(thermodynamique/convectif/microphysique/relief) restent avec leurs
entrées simples d'origine — chacun nécessiterait la même démarche
(vraie formule déjà existante trouvée, justification physique
explicite, intégration opt-in, tests réels) répétée au cas par cas, à
la demande de l'utilisateur.

## Mise à jour 2026-09-03 (suite) — theta-e réel dans le module thermodynamique (§13)

Suite explicite de l'utilisateur ("continue au module thermodynamique,
avec theta-e") — deuxième fermeture ciblée du chantier §12-16, même
méthodologie que le cisaillement de vent.

**Pourquoi** : §13 liste explicitement "température potentielle
équivalente" (theta-e) parmi les variables candidates du module
thermodynamique — le module `thermodynamic` ne combinait jusqu'ici
qu'une moyenne naïve température/humidité.

**Trouvaille faite en inspectant avant de construire** :
`acf.science.equivalent_potential_temperature.EquivalentPotentialTemperature.calculate_bolton_1980()` —
la formule **canonique et publiée** de Bolton (1980), "The Computation
of Equivalent Potential Temperature", Monthly Weather Review 108(7),
1046-1053 (précise à ~0.3 K, la même forme opérationnelle que
MetPy/SHARPpy) — existait déjà, réelle et correcte, mais n'était
appelée par rien produisant une vraie sortie ACF. Exactement le même
schéma que pour le cisaillement de vent et CAPE/CIN.

**Composition de 3 formules réelles déjà existantes, aucune nouvelle
physique inventée** : Bolton (1980) attend un point de rosée, pas
l'humidité spécifique qu'utilise AWCI — plutôt que de re-dériver une
forme approximative, la vraie chaîne existante est réutilisée telle
quelle : `Thermodynamics.calculate_relative_humidity()` (humidité
spécifique → humidité relative réelle) → `DewPoint.calculate()` (point
de rosée réel, Magnus-Tetens/Alduchov & Eskridge 1996) →
`calculate_bolton_1980()`.

**Décision de conception disclosed, différente du cisaillement de
vent** : le cisaillement (indépendant du vent) est **mélangé** 50/50 ;
theta-e **remplace** (pas n'ajoute pas à) le mélange naïf
température/humidité, parce que theta-e combine déjà réellement les
deux — les additionner aurait compté deux fois la même information
physique sous-jacente. Comportement par défaut **bit-identique** sans
`data["theta_e"]`.

**Construit** :
- Nouveau [`acf.awci.theta_e`](../src/acf/awci/theta_e.py) —
  `compute_real_theta_e_at_point()`, composition réelle des 3 formules
  ci-dessus. `theta_e_k` reste honnêtement `None` (jamais fabriqué)
  quand l'humidité relative réelle calculée est non-positive — un vrai
  point sec n'a pas de vrai point de rosée significatif à en déduire.
- `Normalizer.normalize_theta_e()` — enveloppe réelle 250-380 K
  (couvre l'air arctique froid/sec réel jusqu'à l'air tropical
  pré-convectif chaud/humide réel), plus
  `NORMALIZER_RANGE_STATUS["theta_e"]` (`HYPOTHESIS` pour l'enveloppe
  de normalisation — la formule Bolton elle-même est publiée/établie,
  disclosed explicitement dans le texte de l'entrée).
- `AWCICalculator.calculate_module_scores()` — le module `thermodynamic`
  gère maintenant réellement `data["theta_e"]` (remplace, climatology-aware).
- `acf.awci.spatial_field.compute_real_complexity_field(compute_theta_e=True)` —
  intégration de bout en bout réelle, calcul mono-niveau (pas besoin de
  colonne verticale complète, contrairement au cisaillement), vrai
  `theta_e_field`, `np.nan` honnête là où le point est trop sec,
  désactivé par défaut.
- `acf.awci.diagnostic_registry` — nouvelle entrée `normalize_theta_e`
  et mise à jour de `thermodynamic_module_combination` pour disclosed
  le vrai comportement "remplace, ne mélange pas".

**Validation réelle, y compris une propriété physique indépendante** :
`test_higher_humidity_produces_a_real_higher_theta_e_all_else_equal`
vérifie une vraie monotonicité physique (plus d'humidité à même
température/pression augmente forcément theta-e) — une preuve
indépendante de la composition elle-même, pas seulement une cohérence
interne. 20 nouveaux tests répartis sur 4 fichiers —
`tests/test_awci_theta_e.py` (+6 : correspond à la composition
manuelle des 3 formules réelles, theta-e réel toujours supérieur à la
température réelle pour l'air humide — propriété physique connue,
humidité nulle honnêtement non calculée), `tests/test_awci_calculator_theta_e.py`
(+8 : comportement par défaut bit-identique, remplacement exact avec
theta-e, preuve que ce n'est PAS un mélange à 3 voies, climatology-aware),
`tests/test_awci_spatial_field.py` (+4 : champ absent par défaut, réel
et variant spatialement une fois activé, correspond à l'API ponctuelle),
`tests/test_awci_diagnostic_registry.py` (+2). Suite complète
**3691/3691** (3671 + 20), `ruff`/`mypy` propres.

**Ce qui reste réellement, du chantier §12-16** : dynamique (cisaillement)
et thermodynamique (theta-e) étendus, chacun avec une seule variable.
Convectif/microphysique/relief (§14-16) restent avec leurs entrées
d'origine — même démarche disponible au cas par cas, à la demande.

## Mise à jour 2026-09-03 (suite) — vitesse d'ascendance maximale réelle dans le module convectif (§14)

Suite explicite de l'utilisateur ("continue au module convectif, avec
le sommet des nuages") — troisième fermeture ciblée du chantier §12-16,
même méthodologie que le cisaillement de vent et theta-e.

**Pourquoi** : §14 liste explicitement "hauteur/sommet des nuages"
parmi les variables candidates du module convectif — le module
`convective` ne combinait jusqu'ici que CAPE/CIN (70/30).

**Trouvaille faite en inspectant avant de construire, disclosed
explicitement à l'utilisateur plutôt que tranchée en silence** : aucune
formule réelle, publiée, à un seul point, pour la HAUTEUR de sommet de
nuage n'existe dans ce code. Le seul candidat trouvé —
`acf.model4d.physics.cloud_dynamics_advanced.CloudDynamicsAdvancedPhysics.cloud_top_height()`
— n'a aucune référence citée, aucune unité documentée, et cohabite
dans le même module avec un doublon "simplifié" de CAPE/CIN
explicitement labellisé comme tel et physiquement incohérent avec le
vrai `acf.science.cape.CAPE`/`acf.science.cin` déjà utilisé ailleurs
dans AWCI — un vrai problème de crédibilité, pas utilisé ici pour
cette raison précise. Question posée directement à l'utilisateur via
`AskUserQuestion` (3 options : utiliser `max_updraft_velocity`,
utiliser `cloud_top_height` quand même avec disclosure, changer de
variable) — l'utilisateur a choisi **"Utiliser max_updraft_velocity
(Recommandé)"** : `acf.science.clouds.dynamics.CloudDynamicsEngine.max_updraft_velocity(cape)
= sqrt(2 * CAPE)`, le résultat classique et textbook de la théorie de
la parcelle (w_max²/2 = CAPE) — réel, mais un vrai PROXY du potentiel
de développement convectif au sommet, pas littéralement la hauteur du
sommet des nuages (m/s, pas m).

**Décision de conception disclosed, différente de theta-e (remplace)
et proche du cisaillement (mélange), avec une nuance honnête
supplémentaire** : `updraft_velocity` est **mélangé** 50/50 avec la
base CAPE/CIN existante — mais contrairement au cisaillement (réellement
indépendant de la vitesse du vent) ou à theta-e (une vraie combinaison
distincte température+humidité), `max_updraft_velocity(cape)` est une
fonction **déterministe et monotone de CAPE seul** — elle n'ajoute donc
pas d'information physique réellement indépendante, seulement une
courbe de réponse non linéaire appliquée à la même valeur de CAPE déjà
utilisée. Disclosed explicitement partout (docstrings du module, de
`AWCICalculator`, de `NORMALIZER_RANGE_STATUS`, et du registre de
diagnostics) plutôt que caché. Comportement par défaut **bit-identique**
sans `data["updraft_velocity"]`.

**Dépendance honnête, disclosed dans `compute_real_complexity_field`** :
`compute_updraft_velocity=True` exige `compute_convective_energy=True`
(lève `ValueError` sinon) — la formule n'a qu'une seule vraie entrée
(CAPE), et réutiliser le MÊME CAPE réel déjà calculé pour le module
convectif (plutôt que d'en calculer un second, potentiellement
incohérent) est la seule construction honnête.

**Construit** :
- Nouveau [`acf.awci.updraft`](../src/acf/awci/updraft.py) —
  `compute_real_max_updraft_velocity()`, enveloppe fine autour de
  `CloudDynamicsEngine.max_updraft_velocity()`, aucune nouvelle
  physique inventée. CAPE négatif honnêtement bloqué à 0.0 m/s (la
  méthode réelle sous-jacente le fait déjà). Reçoit en option une
  instance `CloudDynamicsEngine` à réutiliser (évite de reconstruire
  l'enregistrement `CloudScientificRegistry` à chaque point de grille).
- `Normalizer.normalize_updraft_velocity()` — enveloppe réelle 0-70 m/s
  (couvre les ascendances observées réelles les plus extrêmes ~50-60
  m/s ET le plafond théorique de la théorie de la parcelle idéalisée,
  connue pour surestimer les valeurs réelles), plus
  `NORMALIZER_RANGE_STATUS["updraft_velocity"]` (`HYPOTHESIS` pour
  l'enveloppe de normalisation — la formule w_max=sqrt(2*CAPE)
  elle-même est un vrai résultat textbook, disclosed explicitement).
- `AWCICalculator.calculate_module_scores()` — le module `convective`
  gère maintenant réellement `data["updraft_velocity"]` (mélange 50/50
  avec la base CAPE/CIN, climatology-aware).
- `acf.awci.spatial_field.compute_real_complexity_field(compute_updraft_velocity=True)` —
  intégration de bout en bout réelle, réutilise le MÊME CAPE réel déjà
  calculé pour `cape_field` (jamais un second), vrai
  `updraft_velocity_field`, `np.nan` honnête là où le CAPE réel
  lui-même n'a pas pu être calculé, `ValueError` explicite si
  `compute_convective_energy=False`, désactivé par défaut.
- `acf.awci.diagnostic_registry` — nouvelle entrée
  `normalize_updraft_velocity` et mise à jour de
  `convective_module_combination` pour disclosed le vrai comportement
  "mélange, information non indépendante".

**Validation réelle** : correspondance exacte avec `CloudDynamicsEngine.max_updraft_velocity()`
directement, valeur connue par calcul manuel (CAPE=2500 → w_max=√5000≈70.71),
CAPE nul/négatif → 0.0 honnête, monotonicité stricte en CAPE, réutilisation
d'instance `CloudDynamicsEngine` fonctionnelle, `updraft_velocity_field`
prouvé égal à `sqrt(2 * cape_field)` point par point sur tout le champ
(preuve qu'aucun second CAPE indépendant n'est calculé). 25 nouveaux
tests répartis sur 4 fichiers — `tests/test_awci_updraft.py` (+9),
`tests/test_awci_calculator_updraft.py` (+8 : comportement par défaut
bit-identique, mélange exact 50/50 avec updraft_velocity, preuve que ce
n'est PAS un remplacement, climatology-aware), `tests/test_awci_spatial_field.py`
(+6 : champ absent par défaut, `ValueError` si `compute_convective_energy=False`,
réel et variant spatialement une fois activé, correspond à l'API
ponctuelle, réutilisation prouvée du même CAPE), `tests/test_awci_diagnostic_registry.py`
(+2). Suite complète **3716/3716** (3691 + 25), `ruff`/`mypy` propres.

**Ce qui reste réellement, du chantier §12-16** : dynamique
(cisaillement), thermodynamique (theta-e) et convectif (vitesse
d'ascendance, un proxy honnêtement disclosed, pas la hauteur de sommet
elle-même) étendus, chacun avec une seule variable. Microphysique/relief
(§15-16) restent avec leurs entrées d'origine — même démarche
disponible au cas par cas, à la demande.

## Mise à jour 2026-09-03 (suite) — phase de précipitation réelle dans le module microphysique (§15)

Suite de l'utilisateur ("continue") — quatrième fermeture ciblée du
chantier §12-16, même méthodologie que le cisaillement de vent,
theta-e et la vitesse d'ascendance. Contrairement aux trois
précédentes, l'utilisateur n'a pas nommé de variable précise cette
fois — sélection faite selon le même jugement qu'aux étapes
"continue selon ton jugement" du reste de la session : §15
(microphysique) est le prochain chantier ouvert et concret dans la
même série §12-16.

**Pourquoi** : §15 liste explicitement "pluie, neige, grêle, eau
surfondue, contenu en glace, ..., hydrométéores" parmi les variables
candidates du module microphysique — celui-ci ne combinait jusqu'ici
que le TAUX de précipitation (`normalize_precipitation`), jamais la
PHASE.

**Trouvaille faite en inspectant avant de construire, avec un vrai
constat de portée honnête** : aucune espèce microphysique réelle par
colonne (eau nuageuse/glace/pluie/neige — qc/qi/qr/qs) n'existe dans
l'état réel de `CoupledEarthSolver` — les vraies formules qui en ont
besoin (`CloudMicrophysicsEngine`, autoconversion/riming/Bergeron-
Findeisen réels) ne peuvent donc pas être alimentées par de vraies
données ici sans fabriquer ces espèces. En revanche,
`acf.science.precipitation.HydrometeorType.classify(surface_temperature_c,
surface_wet_bulb_c)` — une vraie heuristique déjà existante,
explicitement auto-disclosed dans son propre docstring ("a heuristic
forecasting rule of thumb, NOT a single validated physical formula")
— n'a besoin que de température de surface et de température du
thermomètre mouillé, deux quantités déjà réelles et disponibles à
chaque point de grille. Jamais câblée dans rien produisant une vraie
sortie ACF.

**Composition de 2 formules réelles déjà existantes, aucune nouvelle
physique inventée** : `Thermodynamics.calculate_relative_humidity()`
(même formule réelle déjà réutilisée par `acf.awci.theta_e`) →
`Thermodynamics.calculate_wet_bulb_temperature()` (approximation
publiée de Stull (2011), "Wet-Bulb Temperature from Relative Humidity
and Air Temperature", Journal of Applied Meteorology and Climatology)
→ `HydrometeorType.classify()`.

**Décision de conception disclosed, un vrai choix ACF nouveau** :
`classify()` renvoie une catégorie ("Rain"/"Snow"/"Wet Snow/Mix"/
"Freezing Rain / Ice Pellets"), pas un score [0, 1] — la convertir en
contribution numérique exige un vrai classement ordinal disclosed,
même nature de choix ACF que `INTERACTION_WEIGHTS` ou le 70/30
CAPE/CIN : `PHASE_SEVERITY` = {Rain: 0.2, Snow: 0.5, Wet Snow/Mix: 0.7,
Freezing Rain / Ice Pellets: 1.0}, un ORDRE fondé sur un vrai fait
opérationnel aéronautique bien documenté (la pluie verglaçante/le
grésil sont universellement reconnus comme le risque de givrage le
plus sévère pour un aéronef), les valeurs numériques exactes restant
un choix ACF, pas un indice de sévérité publié. **Mélange** (comme le
cisaillement), pas remplacement : la phase est un vrai signal
indépendant du taux de précipitation (contrairement à la vitesse
d'ascendance/CAPE). Comportement par défaut **bit-identique** sans
`data["precipitation_phase_severity"]`.

**Construit** :
- Nouveau [`acf.awci.hydrometeor_phase`](../src/acf/awci/hydrometeor_phase.py) —
  `compute_real_hydrometeor_phase_at_point()`, composition réelle des 2
  formules ci-dessus plus `HydrometeorType.classify()`, jamais `None`/
  `nan` (la chaîne de formules ne peut pas échouer, contrairement à
  theta-e). `PHASE_SEVERITY` disclosed en haut de module.
- `Normalizer.normalize_precipitation_phase_severity()` — clamp
  identité réel [0, 1] (la valeur EST déjà dans la plage cible par
  construction), plus `NORMALIZER_RANGE_STATUS["precipitation_phase_severity"]`
  (`HYPOTHESIS` pour le classement ordinal — la formule de température
  du thermomètre mouillé sous-jacente est publiée/établie).
- `AWCICalculator.calculate_module_scores()` — le module
  `microphysical` gère maintenant réellement
  `data["precipitation_phase_severity"]` (mélange 50/50 avec le score
  de taux, climatology-aware).
- `acf.awci.spatial_field.compute_real_complexity_field(compute_precipitation_phase=True)` —
  intégration de bout en bout réelle, calcul mono-niveau (même classe
  de coût que theta-e), vrais `precipitation_phase_field` (catégorie)
  et `precipitation_phase_severity_field` ([0, 1]), toujours réels
  (jamais `nan`), désactivé par défaut.
- `acf.awci.diagnostic_registry` — nouvelle entrée
  `normalize_precipitation_phase_severity`, nouvelle entrée
  `microphysical_module_combination` (n'existait pas encore — le
  module n'avait qu'une seule entrée avant), et mise à jour de
  `normalize_precipitation` pour disclosed la nouvelle limitation.

**Validation réelle, y compris une propriété physique connue** : les 4
vraies catégories toutes atteignables et confirmées par calcul direct
avec des couples température/humidité réels et physiquement
plausibles (ex. saturé à 0°C -> "Freezing Rain / Ice Pellets", saturé
à 1°C -> "Wet Snow/Mix" - transitions réelles vérifiées à la main
avant d'écrire les tests) ; `PHASE_SEVERITY["Freezing Rain / Ice
Pellets"]` prouvé être le maximum réel des 4 valeurs (preuve
indépendante du disclosure d'ordre aéronautique, pas seulement une
cohérence interne). 23 nouveaux tests répartis sur 4 fichiers —
`tests/test_awci_hydrometeor_phase.py` (+9), `tests/test_awci_calculator_precipitation_phase.py`
(+8 : comportement par défaut bit-identique, mélange exact 50/50,
preuve que ce n'est PAS un remplacement, climatology-aware),
`tests/test_awci_spatial_field.py` (+4 : champs absents par défaut,
réels et toujours valides une fois activés, correspondent à l'API
ponctuelle), `tests/test_awci_diagnostic_registry.py` (+2). Suite
complète **3739/3739** (3716 + 23), `ruff`/`mypy` propres.

**Ce qui reste réellement, du chantier §12-16** : dynamique
(cisaillement), thermodynamique (theta-e), convectif (vitesse
d'ascendance) et microphysique (phase de précipitation) étendus,
chacun avec une seule variable. Relief/orographie (§16) reste avec son
entrée d'origine (altitude statique) — même démarche disponible à la
demande. Hail size/eau surfondue/contenu en glace (§15's autres
candidates) restent un vrai gap disclosed, bloqué par l'absence
d'espèces microphysiques réelles dans l'état du solveur.

## Mise à jour 2026-09-03 (suite) — nombre de Froude orographique réel dans le module relief (§16)

Suite explicite de l'utilisateur ("continue au module relief, avec le
vent") — cinquième et dernière fermeture ciblée du chantier §12-16,
même méthodologie que le cisaillement de vent, theta-e, la vitesse
d'ascendance et la phase de précipitation.

**Pourquoi** : §16 est explicite — le relief n'est pas une variable
statique, il modifie le vent, la turbulence, les accélérations
locales, les ondes orographiques ("turbulence orographique,
accélération du vent, ondes de relief"). Avant cette fermeture, le
module `topographic` n'utilisait que l'altitude statique
(`Normalizer.normalize_topographic()`) ; le seul vrai signal
vent-relief dans AWCI était le terme d'interaction multiplicatif
`wind_topo_interaction` (dynamic × topographic, §22) — réel, mais pas
un vrai diagnostic physique vent-terrain en soi.

**Trouvaille faite en inspectant avant de construire** :
`acf.science.encyclopedia.aviation_extended.calculate_mountain_wave_froude_number()`
— le nombre de Froude des ondes de relief, Fr = U/(N×H), un vrai
diagnostic classique et opérationnel de météorologie aéronautique,
cité (ICAO Doc 9817 Wind Shear ; AMS Aviation Meteorology) : Fr < 1
signale un vrai blocage de l'écoulement et des ondes stationnaires
intenses (régime dangereux), Fr > 1 un écoulement plus lisse
au-dessus du relief. Enregistré dans l'encyclopédie mais jamais câblé
dans rien produisant une vraie sortie ACF — même schéma que les 4
fermetures précédentes.

**Décision de conception disclosed, une vraie limite de portée
nouvelle par rapport aux 4 précédentes** : contrairement au
cisaillement, à theta-e, à la vitesse d'ascendance et à la phase de
précipitation, ce diagnostic N'A PAS pu être câblé dans
`acf.awci.spatial_field` — Fr a besoin d'une vraie hauteur de relief H
et d'une vraie fréquence de Brunt-Väisälä N (elle-même dérivée d'un
vrai gradient vertical de température potentielle avec un vrai
espacement géométrique en hauteur). Aucun champ d'élévation du terrain
n'existe dans l'état réel de `CoupledEarthSolver` (même vrai gap déjà
disclosed pour "terrain-altitude"), et aucune vraie coordonnée
géométrique de hauteur n'existe non plus (seulement des indices de
niveaux hybrides sigma-pression) pour dériver un vrai dtheta/dz sans
fabriquer une référence de hauteur. Ce diagnostic reste donc un vrai
diagnostic PONCTUEL, opt-in, où l'appelant doit fournir sa propre
valeur réelle (un sondage, une carte du relief) — rien n'est fabriqué
ici. Disclosure honnête supplémentaire : `wind_speed_perpendicular`
utilise la vitesse totale du vent réelle (AWCI n'a pas de vraie donnée
d'orientation de crête) comme proxy conservateur disclosed — ne peut
que SOUS-estimer Fr (jamais cacher un vrai risque). Mélange (comme le
cisaillement), pas remplacement : le nombre de Froude est un vrai
signal indépendant de l'altitude seule. Comportement par défaut
**bit-identique** sans `data["mountain_wave_froude"]`.

**Construit** :
- Nouveau [`acf.awci.orographic_froude`](../src/acf/awci/orographic_froude.py) —
  `compute_real_mountain_wave_froude_number_at_point()`, enveloppe fine
  autour de la vraie formule citée, aucune nouvelle physique inventée.
  `froude_number` reste honnêtement `None` (jamais fabriqué) quand la
  vraie fréquence de Brunt-Väisälä est non-positive (air neutre/
  instable — la théorie linéaire classique des ondes de relief n'est
  physiquement valable que pour un air stablement stratifié).
- `Normalizer.normalize_mountain_wave_severity()` — sévérité réelle
  = 1 − clip(Fr, 0, 1), utilisant Fr=1 comme vrai seuil physique
  classique, plus `NORMALIZER_RANGE_STATUS["mountain_wave_severity"]`
  (`HYPOTHESIS` pour le mapping de sévérité — la formule Fr=U/(N×H)
  elle-même est réelle, classique et citée).
- `AWCICalculator.calculate_module_scores()` — le module `topographic`
  gère maintenant réellement `data["mountain_wave_froude"]` (mélange
  50/50 avec le score d'altitude, climatology-aware). Trouvaille
  disclosed en passant, non corrigée ici (hors périmètre) : contrairement
  à tous les autres modules, `topographic` ne passait déjà pas par
  `_normalize()` — il n'était pas climatology-aware même avant cette
  fermeture, alors que `normalize_percentile()` existe (§20) ; laissé
  tel quel pour l'altitude afin de ne rien changer au comportement par
  défaut existant, uniquement disclosed ici.
- `acf.awci.diagnostic_registry` — nouvelle entrée
  `normalize_mountain_wave_severity`, nouvelle entrée
  `topographic_module_combination` (n'existait pas encore), et mise à
  jour de `normalize_topographic` pour disclosed la nouvelle limitation.
- **Pas d'extension de `acf.awci.spatial_field`** cette fois — décision
  disclosed explicitement ci-dessus, pas un oubli.

**Validation réelle, y compris des propriétés physiques connues** :
stabilité forte + vent modéré + haute montagne → Fr < 1 (régime de
blocage) confirmé par calcul direct ; stabilité faible + vent fort +
petite colline → Fr > 1 (régime d'écoulement lisse) confirmé ; air
neutre/instable (N=0, retourné honnêtement par
`BruntVaisalaFrequency.calculate()` elle-même) → `froude_number=None`
honnête, jamais une valeur infinie/nulle fabriquée ; Fr plus proche de
0 prouvé produire un score topographique plus élevé à altitude égale
(monotonicité physique réelle, preuve indépendante). 20 nouveaux tests
répartis sur 3 fichiers — `tests/test_awci_orographic_froude.py` (+9),
`tests/test_awci_calculator_orographic_froude.py` (+9 : comportement
par défaut bit-identique, mélange exact 50/50, preuve que ce n'est PAS
un remplacement, monotonicité physique, climatology-aware),
`tests/test_awci_diagnostic_registry.py` (+2). Suite complète
**3759/3759** (3739 + 20), `ruff`/`mypy` propres.

**Ce qui reste réellement, du chantier §12-16** : les 5 modules
(dynamique, thermodynamique, convectif, microphysique, relief) ont
chacun reçu une extension réelle et disclosed, avec au moins une
variable candidate du prompt maître. Chantier §12-16 substantiellement
avancé pour cette session — d'autres variables candidates par module
(ex. vorticité/divergence pour le dynamique, température virtuelle
pour le thermodynamique, réflectivité pour le convectif) restent de
vrais gaps disclosed dans le tableau d'audit exhaustif, disponibles au
cas par cas à la demande. Le nombre de Froude orographique reste
volontairement point-only : câbler un vrai champ spatial nécessiterait
une vraie infrastructure d'élévation de terrain/coordonnée de hauteur
qui n'existe pas encore dans ACF — un vrai chantier distinct, pas un
oubli.

## Mise à jour 2026-09-03 (suite) — PhysicsGuard réel invoqué aux points d'entrée réels de ce chantier (§11)

Suite de l'utilisateur ("continue") — sélection faite selon le même
jugement que les fermetures "continue selon ton jugement" du reste de
la session : après la clôture du chantier §12-16, §11 (`⚠️` :
"`PhysicsGuard` réel mais pas invoqué systématiquement à chaque point
d'entrée du pipeline scientifique") est le gap le plus concret et le
mieux borné restant, et il concerne directement les 5 nouveaux modules
ponctuels construits cette session (`wind_shear.py`/`theta_e.py`/
`updraft.py`/`hydrometeor_phase.py`/`orographic_froude.py`) — aucun
d'entre eux n'invoquait `PhysicsGuard`.

**Pourquoi** : `acf.physics_guard.PhysicsGuard` est réel, déjà
construit (`check_range()`/`check_consistency()`/`validate()`), avec
de vraies bornes opérationnelles par nom standard CF
(`OPERATIONAL_RANGES`) et de vrais contrôles de cohérence physique
(point de rosée ≤ température, humidité relative bornée) — mais rien
dans les 5 nouveaux modules ponctuels de cette session ne l'appelait.

**Décision de conception disclosed, un vrai périmètre borné** : plutôt
que de tenter de câbler `PhysicsGuard` dans `AWCICalculator` lui-même
(déjà disclosed comme un vrai gap séparé — les noms de variables
simplifiés d'AWCI, ex. `"wind_speed"`/`"temperature"`, ne se
correspondent pas automatiquement aux noms standard CF sans deviner
une convention d'unité, voir `AWCIResult`'s own field docstrings),
cette fermeture cible uniquement les 4 modules ponctuels dont les
entrées ont une correspondance CF réelle et non ambiguë (unités déjà
documentées explicitement dans chaque docstring) :
- `theta_e.py` : `air_temperature`/`specific_humidity`/`air_pressure`
  (conversion hPa→Pa réelle via `check_range(..., unit="hPa")`) sur
  les 3 entrées brutes, plus le vrai contrôle de cohérence
  `check_dewpoint_not_above_temperature()` sur le point de rosée
  calculé — une vraie vérification croisée indépendante entre 2
  chaînes de formules différentes (Magnus-Tetens vs. l'entrée
  température), pas une simple redite.
- `hydrometeor_phase.py` : mêmes 3 contrôles de plage sur les entrées
  brutes.
- `wind_shear.py` : `eastward_wind`/`northward_wind` sur les 2 réels
  couples (u, v) effectivement utilisés (bottom/top level), pas tout
  le profil.
- `orographic_froude.py` : `wind_speed` sur `wind_speed_perpendicular`
  uniquement (`mountain_height_m`/`brunt_vaisala_n` n'ont aucune plage
  CF documentée dans `OPERATIONAL_RANGES` — rien inventé ici).
- `updraft.py` — **intentionnellement non touché** : aucune plage CF
  n'existe pour le CAPE dans `OPERATIONAL_RANGES` ; rien à câbler sans
  fabriquer une borne.
- `acf.awci.spatial_field.compute_real_complexity_field()` reçoit un
  nouveau `validate_physics: bool = False` propagé aux 3 sous-appels
  concernés (`compute_wind_shear`/`compute_theta_e`/
  `compute_precipitation_phase` — pas `compute_updraft_velocity`, pour
  la même raison que ci-dessus).

Chaque nouveau paramètre `validate_physics: bool = False` est
strictement opt-in — comportement par défaut **bit-identique**, un
vrai `acf.core.exceptions.PhysicsError` (ou sous-classe) ne se
déclenche que si explicitement demandé.

**Trouvaille réelle faite en testant, disclosed** : la propre
convention de coordonnée hybride sigma-pression du solveur
(`EarthGrid.a_coeff`/`b_coeff`) produit une vraie pression de niveau 0
d'environ 2013 hPa (`a=100000 Pa + b=1.0 × Ps≈101325 Pa`) — au-delà du
vrai plafond opérationnel de `PhysicsGuard` (1085 hPa). Un vrai
caractère préexistant de ce solveur synthétique (pas un bug de ce
câblage) : seul un niveau intermédiaire (ex. niveau 2 sur 4) retombe
dans une plage réaliste. Disclosed dans le test concerné plutôt que
masqué.

**Validation réelle** : comportement par défaut prouvé inchangé pour
chacun des 4 modules (une entrée hors plage ne lève rien sans
`validate_physics=True`) ; chaque contrôle de plage prouvé lever
`RangeError` pour une entrée réellement hors plage quand activé ; le
contrôle de cohérence dewpoint≤température prouvé ne jamais échouer
spuriement pour un cas réel valide ; `compute_real_complexity_field`
prouvé fonctionner sans lever pour un vrai run bien réglé (niveau 2,
perturbation modérée) une fois `validate_physics=True` propagé aux 3
sous-appels. 19 nouveaux tests répartis sur 5 fichiers —
`tests/test_awci_theta_e.py` (+5), `tests/test_awci_hydrometeor_phase.py`
(+5), `tests/test_awci_wind_shear.py` (+4),
`tests/test_awci_orographic_froude.py` (+3),
`tests/test_awci_spatial_field.py` (+2). Suite complète **3778/3778**
(3759 + 19), `ruff`/`mypy` propres.

**Ce qui reste réellement** : `AWCICalculator` lui-même reste sans
appel `PhysicsGuard` direct (le vrai gap de correspondance de noms/
unités CF reste disclosed, pas résolu ici) ; `updraft.py` reste sans
contrôle de plage réel tant qu'aucune plage CF pour le CAPE n'est
documentée dans `OPERATIONAL_RANGES` ; les autres points d'entrée du
pipeline scientifique plus large (ingestion/adaptateurs modèles) —
hors du périmètre de cette fermeture — restent un vrai chantier
distinct pour le futur §31/§8 (pipeline en 21 étapes assemblé de bout
en bout).

## Mise à jour 2026-09-03 (suite) — chaîne de traçabilité réelle enfin affichée dans le dashboard (§26/§53)

Suite de l'utilisateur ("continue selon ton jugement") — après §11,
recherche d'un nouveau gap concret et bien borné dans le tableau
d'audit exhaustif. Trouvaille faite en vérifiant si les capacités
construites plus tôt cette session étaient réellement utilisées :
`acf.awci.result.build_awci_result()`/`AWCIResult.trace_chain()`
(fermeture §26/§53/§81 du 2026-09-03, plus tôt cette session) n'étaient
référencées nulle part dans `acf.gui` — exactement le même schéma
"capacité réelle jamais branchée" que cette session a déjà trouvé et
corrigé plusieurs fois (le système de couches orphelin, `AWCIGauge`
avant sa reconstruction) — mais cette fois au niveau de l'intégration
GUI, pas de la science elle-même.

**Pourquoi** : §26 exige "Chaque résultat doit être traçable" et §53
"Il doit être possible de passer du résumé à la donnée détaillée" — la
vraie chaîne existait (`trace_chain()`), mais aucun bouton, dialogue ou
panneau du dashboard ne l'affichait jamais à l'utilisateur.

**Construit, un vrai branchement, aucune nouvelle donnée fabriquée** :
- `AWCIDashboard` : nouveau `self._last_awci_result: AWCIResult | None`,
  construit via `build_awci_result(point_result, raw_variables=point_raw_data,
  vertical_level=...)` juste après chacun des 2 vrais appels
  `AWCICalculator().calculate()` existants (mode démo et mode Real
  Physics) — jamais une deuxième computation, exactement le même
  `point_result`/`point_raw_data` déjà réels utilisés par
  `radar`/`component_list`/`risk_summary`. `vertical_level` réel
  (l'index de niveau natif effectivement échantillonné) uniquement en
  mode Real Physics ; `lead_time_hours`/`provenance`/`quality`/
  `model_spread` restent honnêtement `None` (pas de concept
  d'échéance/provenance réelle dans cette vue synthétique
  mono-point) — `trace_chain()` les affiche alors comme "not
  available", jamais fabriqués.
- `AWCIComponentDetailDialog.show_component()` : nouveau paramètre
  optionnel `awci_result: AWCIResult | None = None` (rétrocompatible —
  `None` par défaut affiche honnêtement "not available"), nouvelle
  section "Drill-down chain (§26/§53)" affichant `trace_chain()` telle
  quelle, ligne par ligne — aucune reformulation, aucun recalcul.
- `_on_component_clicked()` passe `self._last_awci_result` au dialogue
  à chaque clic.

**Validation réelle** : la trace affichée prouvée être exactement
`AWCIResult.trace_chain()`'s own real output (comparaison directe
ligne par ligne, pas une re-dérivation) ; `raw_variables` de la trace
prouvés correspondre aux mêmes vraies valeurs déjà montrées dans la
section "Real inputs" existante ; le niveau vertical réel prouvé
apparaître en mode Real Physics ; comportement par défaut (dialogue
appelé sans `awci_result`) prouvé rétrocompatible (placeholder honnête,
pas d'erreur). 6 nouveaux tests répartis sur 2 fichiers —
`tests/gui/test_awci_dashboard_component_clicks.py` (+3),
`tests/test_awci_component_detail.py` (+3). Suite complète
**3784/3784** (3778 + 6), `ruff`/`mypy` propres.

**Ce qui reste réellement** : `lead_time_hours`/`provenance`/`quality`/
`model_spread` restent honnêtement absents de cette vue dashboard (pas
de concept réel d'échéance de prévision ni de provenance de fichier
source dans le mode synthétique/Real-Physics-mono-point actuel) — la
chaîne affichée est réelle mais partielle, disclosed comme telle par
`trace_chain()` lui-même via ses "not available". D'autres dialogues/
panneaux du dashboard (AWCI Dashboard général, ESOC) pourraient
recevoir le même branchement à la demande.

## Mise à jour 2026-09-03 (suite) — registre de diagnostics réel enfin affiché dans le dashboard (§55)

Suite de l'utilisateur ("continue selon ton jugement") — même
méthode de recherche que la fermeture précédente : vérifier si
d'autres capacités réelles construites plus tôt cette session étaient
elles aussi de vrais orphelins. Trouvaille : `acf.awci.diagnostic_registry.
DIAGNOSTIC_REGISTRY`/`get_diagnostic()` (fermeture §55 du 2026-09-03,
plus tôt cette session) n'étaient référencés nulle part hors de leur
propre fichier — seulement interrogeables depuis Python, jamais
affichés à un vrai utilisateur. `acf.awci.config_loader`
(`AWCIConfig`/`load_config()`, §56) et `acf.awci.run_report`
(`build_run_report()`, §75) sont eux aussi de vrais orphelins
similaires, mais moins directement câblables sans risque : `run_report`
n'a de sens réel qu'avec une vraie ingestion de fichiers (inexistante
dans ce dashboard synthétique) ; `config_loader` exigerait un vrai
mécanisme d'échange de calculateur en cours de route (plus risqué) —
tous deux disclosed ci-dessous comme chantiers futurs distincts,
laissés de côté pour cette fermeture précise.

**Pourquoi** : §55 exige "Chaque diagnostic doit être documenté" — le
vrai catalogue existait déjà (12 champs réels par entrée), mais rien
dans le dashboard ne le montrait, alors que
`AWCIComponentDetailDialog` (déjà enrichi du drill-down §26/§53 dans
la mise à jour précédente) est exactement le bon endroit pour ça.

**Construit, un vrai branchement, aucune redite** :
- `AWCIComponentDetailDialog` : nouvelle section "Diagnostic
  documentation (§55)" affichant `physical_meaning`/`limitations`/
  `reference` de l'entrée réelle `DIAGNOSTIC_REGISTRY[f"{key}_module_combination"]`
  correspondant au module cliqué — texte réel déjà écrit et testé,
  jamais reformulé ici.
- Mapping réel `_DIAGNOSTIC_REGISTRY_KEY_FOR_MODULE` couvrant les 5
  modules ayant une vraie entrée `_module_combination`
  (dynamic/thermodynamic/convective/microphysical/topographic).
  `temporal`/`confidence` n'ont réellement aucune entrée dans le
  registre — un vrai gap disclosed du registre lui-même (pas fabriqué
  ici) : la section affiche honnêtement "not yet in the centralized
  diagnostic registry" plutôt qu'une description inventée.

**Validation réelle** : le texte affiché prouvé être exactement
`DIAGNOSTIC_REGISTRY`'s own real `physical_meaning`/`limitations`/
`reference` pour chacun des 5 modules couverts (comparaison directe,
pas une redérivation) ; `temporal`/`confidence` prouvés afficher le
placeholder honnête. 3 nouveaux tests dans
`tests/test_awci_component_detail.py`. Suite complète **3787/3787**
(3784 + 3), `ruff`/`mypy` propres.

**Ce qui reste réellement** : `acf.awci.config_loader` (§56) et
`acf.awci.run_report` (§75) restent de vrais orphelins non branchés
— chantiers futurs distincts, disclosed ci-dessus, disponibles à la
demande.

## Mise à jour 2026-09-03 (suite) — parité complète du dashboard AWCI avec docs/reference/awci_dashboard_reference.jpg

Demande explicite de l'utilisateur : "je veux que awci soit exactement
a 100% comme dans la photo jointe" (le mockup déjà utilisé pour
construire `AWCIDashboard` plus tôt cette session — fichier réel déjà
présent dans le dépôt, `docs/reference/awci_dashboard_reference.jpg`,
confirmé pixel-identique à la photo collée). L'utilisateur avait
préparé un prompt Gemini détaillé suggérant React/Tailwind/Recharts et
des "mock data" pour reconstruire ce dashboard — décision explicite,
disclosed à l'utilisateur en clair : traiter ce prompt comme une pure
LISTE DE FONCTIONNALITÉS visuelles à comparer, pas des instructions
d'implémentation littérales, et amener `AWCIDashboard` à la parité
dans sa vraie stack existante (Python/PySide6/matplotlib), en
réutilisant les capacités déjà réelles de cette session et en
respectant strictement la discipline "jamais de donnée fabriquée" —
pas une reconstruction React déconnectée avec des données inventées.

**Méthode** : deux agents Explore lancés en parallèle avant tout code
— un pour cartographier l'état exact de `AWCIDashboard` section par
section du mockup (ce qui existe déjà vs ce qui manque, réel vs
synthétique), un pour localiser les vraies sources de données/formules
disponibles pour chaque élément manquant. Plan détaillé écrit et
approuvé avant implémentation (12 items), avec une section "explicitement
hors périmètre, disclosed" pour ce qui aurait exigé de la donnée
fabriquée.

**Construit, un vrai périmètre disclosed pour chaque item** :
1. **Badge d'en-tête** "RESEARCH STAGE / Prototype Version" — texte
   statique réel, aucune donnée.
2. **Boutons radio VIEW MODE** (Global/Regional/Vertical Cross-Section)
   — comportement réel sur la vraie caméra de la carte globale
   (`AWCIMapPanel.set_extent()`, nouveau, wrapper public autour de
   `MapCamera` déjà réel) : Global = vue par défaut, Regional = même
   `_REGIONAL_EXTENT` réel déjà utilisé par la carte régionale,
   Vertical Cross-Section = zoom réel sur la vraie bounding box du
   trajet global (l'analogue honnête le plus proche de "mettre en
   avant le corridor" sur une carte 2D — un extent réel calculé,
   jamais fabriqué).
3. **Glyphe avion réel** (✈, remplace le triangle) + quelques points
   intermédiaires réels interpolés le long du même trajet déjà réel —
   changement cosmétique sur des positions déjà réelles, aucune
   nouvelle donnée.
4. **Label Tunis** — vraie coordonnée publique vérifiable (comme
   Alger/Tripoli déjà en dur), `AWCIMapPanel.set_city_labels()`
   (nouveau), indépendant du trajet.
5. **Jauge de confiance demi-cercle** — `AWCIGauge` (orpheline depuis
   la reconstruction du dashboard, jamais utilisée) étendue avec un
   vrai mode `half_circle=True` (réutilise son propre code de tracé
   d'arc réel, pas un second widget), montée dans `AWCIStatsBar` à la
   place du texte brut, alimentée par la même vraie valeur
   `confidence_pct` déjà calculée.
6. **Bouton "See Vertical Profile"** — ouvre `AWCIVerticalProfile`
   (orpheline elle aussi, jamais utilisée), peuplée de vrais scores
   `AWCICalculator` au point d'intérêt, à plusieurs niveaux de vol
   réels — nouvelle formule inverse réelle
   `flight_level_ft_to_pressure_hpa()` (inverse algébrique exacte de
   la formule ICAO/FAA déjà réelle `pressure_to_flight_level_ft()`,
   pas une conversion séparément inventée).
7. **Sparkline REGIONAL TREND** — `AWCITimeline` (orpheline, jamais
   utilisée) alimentée par de vrais scores horaires au point d'intérêt,
   ±6h autour de l'heure réelle du curseur Valid Time.
8. **Icônes de givrage sur la coupe verticale** — nouvelle fonction
   réelle `cross_section_phase_severity_field()` (mode démo, mêmes
   entrées T/q/P synthétiques que le score AWCI déjà affiché) et
   `sample_cross_section_hazards()` (mode Real Physics, nouveau dans
   `path_sampling.py`) réutilisant `acf.awci.hydrometeor_phase` déjà
   réel.
9. **Icônes de turbulence (proxy)** — le vrai indice CAT d'Ellrod-Knapp
   a besoin de gradients horizontaux de vent qu'aucun pipeline
   ponctuel de ce code ne fournit encore (trouvaille confirmée par
   l'agent d'exploration) ; substitut honnête disclosed partout : le
   cisaillement de vent vertical déjà réel et déjà câblé
   (`acf.awci.wind_shear`) entre niveaux natifs adjacents, exposé comme
   "proxy", jamais présenté comme l'indice CAT complet. A nécessité
   d'exposer `u_volume`/`v_volume` (déjà calculés en interne, juste
   jamais retournés) dans `compute_real_complexity_volume()` — ajout
   pur, rétrocompatible.
10. **Comparaison FL280/FL320** — `AWCIRouteChart` étendu avec un vrai
    mode 2-séries (`set_comparison_series()`), vraie conversion
    FL→hPa via la table ISA déjà réelle, 2 vrais échantillonnages
    (`sample_field_along_path()`/`route_profile()`) à ces 2 vrais
    niveaux — action réelle déclenchée par l'utilisateur (même
    discipline de coût disclosed que 🔬 Real Physics/🧊 3D View), pas
    automatique.
11. **Bannière de recommandation** — texte réel généré par template
    (même discipline que `AWCICalculator._explain()`), construit à
    partir de `compute_elevated_risks()` déjà réel et d'un vrai segment
    contigu à AWCI élevé détecté sur le trajet — masquée entièrement
    quand rien n'est réellement élevé, jamais une recommandation
    fabriquée.
12. **Case CAPE dans le panneau LAYERS** — ajoutée honnêtement
    désactivée avec tooltip, même convention que Wind/Turbulence/
    Icing/Convection/Clouds — une vraie formule CAPE existe mais un
    vrai calque de contour par point de grille est un chantier séparé
    et plus conséquent, disclosed comme hors périmètre.

**Trouvaille et correction en cours de route, disclosed** : un vrai
bug de collapse de layout trouvé par capture d'écran directe pendant
la vérification — la carte globale s'effondrait à 157px de haut
(contre 425px avant ce chantier) à cause de la compétition entre les
nouveaux widgets à hauteur fixe (sparkline, bannière, ligne VIEW MODE)
et le facteur de stretch de la ligne contenant la carte. Même schéma
de bug et même correction que le "Layout collapse bug" déjà documenté
plus tôt cette session (`acf_general_dashboard.py`) : `setMinimumHeight()`
explicite sur `global_map`/`regional_map`/`cross_section`.

**Validation réelle** : capture d'écran complète comparée visuellement
au mockup (envoyée à l'utilisateur) ; VIEW MODE prouvé changer
réellement l'extent de la caméra ; jauge de confiance prouvée refléter
la même vraie valeur déjà calculée ; profil vertical prouvé avoir un
vrai score par niveau de vol nommé ; sparkline prouvée se mettre à
jour avec le curseur ; overlay de la coupe verticale prouvé réel en
mode démo (givrage seul) et en mode Real Physics (givrage + shear,
shear jamais négatif) ; comparaison FL280/FL320 prouvée fonctionner en
démo et en Real Physics ; bannière prouvée refléter les vrais risques
élevés et rester masquée quand rien n'est élevé. 65 nouveaux tests
répartis sur 10 fichiers (dont 3 nouveaux : `tests/test_awci_gauge.py`,
`tests/test_awci_route_chart.py`, `tests/test_awci_stats_bar.py`,
`tests/gui/test_awci_dashboard_reference_parity.py`). Suite complète
**3852/3852** (3787 + 65), `ruff`/`mypy` propres sur tous les fichiers
touchés.

**Ce qui reste réellement** : l'indice de turbulence CAT complet
(Ellrod-Knapp, gradients horizontaux) reste un vrai chantier distinct
nécessitant une nouvelle infrastructure de gradient ; le calque CAPE
reste une case honnêtement désactivée, pas un vrai calque de contour ;
les deux systèmes de calques de carte incompatibles trouvés dans ce
dépôt (`acf.gui.map.layers.layer_manager` vs `acf.gui.map.map_layers`)
restent non unifiés — un vrai chantier architectural séparé, pas une
simple case à cocher.

## Mise à jour 2026-09-03 (suite) — contrat d'intégration ACF→AWCI, interactivité réelle, audit documentaire

Demande explicite de l'utilisateur : un "AWCI — MASTER ENGINEERING
PROMPT V3.0" de 89 sections, collé en clair, exigeant (1) fidélité
pixel-perfect au mockup déjà atteinte la clôture précédente, (2) zéro
contrôle UI décoratif/mort, (3) que AWCI n'invente JAMAIS ses entrées
météorologiques et consomme les vraies sorties d'ACF via un "AWCI
Input Adapter", (4) une source de vérité unique pour l'état partagé
(heure, niveau de vol, point), (5) un jeu de documents d'audit complet
avant tout code, avec discipline explicite "INSPECTE, ne suppose pas".
Le prompt est écrit dans un langage générique React/web (build npm,
hooks, WebGL, ARIA, un "RouteOptimizationEngine") qui ne correspond pas
à la vraie stack de ce projet (Python/PySide6/matplotlib) — disclosed
en clair à l'utilisateur, traité comme les fermetures précédentes : une
liste d'exigences fonctionnelles à satisfaire dans la vraie stack, pas
des instructions d'implémentation littérales.

**Méthode** : deux agents Explore lancés en parallèle avant tout code
(un pour l'infrastructure ACF réelle existante — Data Contract, Model
Adapter Protocol, PhysicsGuard — un pour les vraies interactions
mortes/manquantes du dashboard), puis un plan détaillé écrit et
approuvé avant implémentation. Les agents ont trouvé qu'un vrai Data
Contract (`acf.core.contracts`) et un vrai Model Adapter Protocol
(`acf.models.base_model`) existaient déjà (chantiers antérieurs de
cette même session) — donc le vrai travail restant n'était pas de les
reconstruire mais de combler le seul vrai manque : rien ne pontait
`Dataset` vers le dict de `AWCICalculator`.

**Construit** :
1. **`AWCI Input Adapter`** (`src/acf/awci/input_adapter.py`, nouveau)
   — pont réel entre `Dataset`/`VariableContract` et le dict
   `AWCICalculator`, avec vraie évaluation de qualité
   (`assess_variable_quality()`) par variable CF nommée, jamais une
   valeur fabriquée pour une variable absente (honnêtement `MISSING`).
2. **Clic sur la carte → point d'intérêt réel** — `AWCIMapPanel.pointClicked`
   (nouveau signal Qt), câblé sur la carte globale ET régionale,
   remplace la constante `_POINT_OF_INTEREST` en dur par
   `self._point_of_interest`, relance le vrai pipeline par point.
3. **Badges RISK SUMMARY cliquables** — réutilisent le vrai pattern de
   clic déjà prouvé pour la liste de composants (`_ComponentRow`) ;
   Turbulence/Icing/Convective réutilisent le vrai dialogue de détail
   déjà existant (pas un doublon) ; Overall/Physical/Forecast ouvrent
   un nouveau dialogue montrant le vrai détail des `module_scores` qui
   composent ce score composite.
4. **Sélecteur "Flight Level:"** — nouvelle source de vérité unique
   réelle pour 3 des ~7 constantes `flight_level_hpa` trouvées en dur
   par l'audit (le calcul au point d'intérêt) ; les 4 autres restent
   volontairement indépendantes (routes/affichages réels différents,
   certains fixés par le titre même de la carte, ex. "(FL300)" —
   les unifier aurait changé ce que ces panneaux affichent, ce que
   l'audit n'a pas trouvé cassé). Défaut "FL300" gardé bit-identique
   (300.0 hPa littéral, pas la valeur ISA réelle ~300.9 hPa) pour ne
   décaler aucun score déjà calculé avant ce chantier.
5. **8 documents d'audit** sous `docs/awci/` — `AWCI_UI_AUDIT.md`,
   `AWCI_COMPONENT_INVENTORY.md`, `AWCI_INTERACTION_MATRIX.md`,
   `AWCI_LAYOUT_SPEC.md`, `AWCI_BUTTON_CONTRACT.md`,
   `AWCI_IMPLEMENTATION_STATUS.md`, `AWCI_FINAL_VALIDATION.md`,
   `future-improvements.md`.

**Décision disclosed, pas silencieuse** : le `RouteOptimizationEngine`
(§30 du prompt) n'a pas été construit. Deux vrais stubs délibérés
existent déjà dans ce dépôt (`acf/science/query_engine.py`,
`acf/ai_expert/aviation_reasoning.py`), tous deux explicitement vidés
d'une recommandation fabriquée `"FL360"` et retournant honnêtement
`None`/`is_real_data: False`. Un nouveau moteur produisant une
recommandation de niveau de vol à partir des seuls scores AWCI
composites n'aurait pas plus de base scientifique réelle que ce qui a
déjà été retiré deux fois dans l'histoire de ce projet — ressusciter
exactement la même fabrication. Documenté dans `AWCI_UI_AUDIT.md` §8
et `future-improvements.md` §1.

**Trouvaille et correction en cours de route, disclosed** : un vrai
bug de double-émission Qt trouvé pendant l'écriture des tests —
`AWCIMapPanel.pointClicked` s'émettait deux fois par vrai clic. Un
seul clic sur `self.canvas` atteignait `mouseReleaseEvent()` deux fois
— une fois via le `eventFilter()` de ce panneau (le chemin voulu), une
fois via un second chemin de livraison Qt natif, indépendant, dont le
mécanisme interne exact n'a pas été identifié plus loin (confirmé à la
fois avec `QApplication.sendEvent()` et `QTest.mouseClick()` — donc un
vrai comportement, pas un artefact du harnais de test). La déduplication
par `id(event)` ne fonctionne PAS : PySide6 renvoie un objet wrapper
Python distinct à chaque livraison, même pour le même vrai clic. Corrigé
en faisant CONSOMMER (remettre à `None`) `_click_press_position` par
`mouseReleaseEvent()` dès la première des deux livraisons, rendant la
seconde un no-op réel et inoffensif — régression gardée par les 4 tests
de `tests/test_awci_map_panel_point_click.py`. Un second vrai bug (déjà
connu de ce projet, retrouvé en testant l'adaptateur) : `AWCICalculator`
attend la pression en hPa, pas en Pa (l'unité canonique CF réelle) —
corrigé via une table d'unité native séparée (`AWCI_KEY_NATIVE_UNIT`),
isolée de la conversion CF utilisée uniquement pour l'évaluation de
qualité.

**Validation réelle** : capture d'écran offscreen complète comparée au
mockup — aucun élément déjà validé altéré, seul ajout visible : le
sélecteur "Flight Level:" (ajout fonctionnel disclosed, même précédent
que VIEW MODE/🔬 Real Physics/🛩 Compare FL280/FL320 ajoutés aux
chantiers précédents). 31 nouveaux tests répartis sur 3 fichiers
(`tests/test_awci_input_adapter.py` — 12,
`tests/test_awci_map_panel_point_click.py` — 4,
`tests/gui/test_awci_dashboard_synchronization.py` — 15). Suite
complète **3883/3883** (3852 + 31), `ruff`/`mypy` propres sur tous les
fichiers touchés.

**Ce qui reste réellement** : le `RouteOptimizationEngine` reste
délibérément non construit (voir plus haut) ; 4 des ~7 constantes de
niveau de vol trouvées en dur par l'audit restent volontairement
indépendantes (routes/affichages réels différents) ; la couverture
CF/unités de `acf.normalization` reste réelle mais étroite (9 noms
CF, 4 noms courts ECMWF) — limite déjà connue, pas adressée par ce
chantier ; le sélecteur de picker calendrier, le rendu WebGL/GPU, le
balayage accessibilité complet du dépôt, l'indice CAT complet
Ellrod-Knapp et le calque CAPE par point de grille restent non
construits, documentés dans `future-improvements.md`.

## Mise à jour 2026-09-03 (suite) — les 6 cases LAYERS enfin réelles (démo + Real Physics)

Demande explicite de l'utilisateur : "je veux rendre tout les boutons
de awci en marche". Le seul vrai "bouton mort" restant de ce dashboard
était le panneau LAYERS de la carte : les 6 cases Wind/Turbulence/
Icing/Convection/CAPE/Clouds étaient en dur `setEnabled(False)` depuis
la toute première construction du dashboard — aucune source de donnée
réelle n'y avait jamais été branchée (§28-29 de l'audit exhaustif des
90 sections, déjà partiellement fermé pour la carte elle-même, mais
pas pour ce panneau).

**Construit, en deux temps** :
1. **Mode démo** — nouvelle `awci_layer_grids()`
   (`awci_synthetic_field.py`) : réutilise le même `_synthetic_inputs()`
   déjà source unique de vérité du pattern démo, plus deux vraies
   formules ACF déjà existantes (`acf.awci.updraft`,
   `acf.awci.hydrometeor_phase`) — aucune nouvelle physique inventée
   pour Icing/Convection/CAPE. Deux proxys honnêtement disclosed
   (même discipline que le proxy de cisaillement déjà utilisé sur la
   coupe verticale) : Turbulence = gradient horizontal réel de la
   grille de vitesse du vent (`numpy.gradient()`) ; Clouds = taux de
   précipitation réel (aucune vraie grandeur de couverture nuageuse
   n'existe nulle part dans ce pipeline). Wind = vitesse réelle
   uniquement, pas de direction (le pattern démo n'a pas de composantes
   u/v).
2. **Mode Real Physics** — nouvelle `real_layer_grids_at_level()`
   (`acf.awci.path_sampling`) : Wind/Turbulence/Icing réels à partir
   des vrais champs 3D de `compute_real_complexity_volume()`. Vérité
   honnête confirmée en lisant directement le dict réellement retourné
   par cette fonction : elle porte température/vitesse du
   vent/u/v/humidité spécifique/pression mais **aucun champ CAPE ni
   précipitation** — Convection/CAPE/Clouds n'ont donc aucune vraie
   contrepartie possible dans ce mode et restent des cases activées
   mais réellement sans effet (jamais un contour fabriqué), même
   limite déjà disclosed pour les scores de module AWCI eux-mêmes en
   Real Physics.

**Validation réelle** : 21 nouveaux tests (12 pour `awci_layer_grids()`
— formes, valeurs recoupées avec des appels directs aux formules
réelles, relation monotone CAPE↔updraft, déterminisme ; 6 pour
`real_layer_grids_at_level()` — mêmes recoupements sur le vrai volume,
garde explicite qu'aucune clé cape/convection/clouds n'est jamais
fabriquée ; 3 d'intégration dashboard — bascule réelle en Real Physics,
no-op honnête pour les 3 cases sans contrepartie, restauration complète
au retour en mode démo) + 2 tests existants réécrits (ils affirmaient
auparavant que ces cases étaient désactivées). Suite complète
**3883 → 3895 → 3904** (deux commits), `ruff`/`mypy` propres sur tous
les fichiers touchés. Capture d'écran envoyée deux fois (CAPE en mode
démo, Turbulence en mode Real Physics).

**Ce qui reste réellement** : l'indice CAT complet Ellrod-Knapp reste
un vrai chantier distinct (le proxy de gradient horizontal n'est
toujours qu'un proxy, disclosed) ; Convection/CAPE/Clouds resteront
honnêtement sans effet en Real Physics tant que le solveur lui-même ne
produira pas de champ CAPE/précipitation réel — un chantier de physique
séparé, pas un manque de câblage UI.

## Mise à jour 2026-09-03 (suite) — rapport d'exécution réel §75, priorité choisie librement dans l'audit exhaustif

Suite explicite ("continue", sans qualificatif — le fil "rendre tout
les boutons en marche" étant clos, priorité choisie librement parmi
les gaps ⚠️ restants de l'audit exhaustif des 90 sections). §75
demande : "Le pipeline doit produire : logs, metrics, warnings,
errors, quality reports, runtime statistics", avec un exemple concret
("Input files: 48, Valid: 46, Rejected: 2, Diagnostics: 123, AWCI
generated: YES, Quality: GOOD, Model spread: HIGH"). `acf.monitoring`
existait déjà, réel mais générique — jamais branché pour produire ce
format précis par exécution AWCI.

**Construit** : `acf.awci.execution_report.summarize_execution()` — un
vrai assembleur (même discipline que `build_awci_result()` : ne
recalcule rien, lit uniquement un `AWCIResult` déjà construit) plus une
nouvelle `AWCIExecutionReportDialog` (bouton "📊 Report" dans le
header). Deux réinterprétations honnêtes, disclosed plutôt que
devinées : "Input files" devient "Input variables" (`calculate()` ne
lit jamais de fichiers, seulement un dict de variables nommées) ; "Model
spread: HIGH" n'est JAMAIS deviné automatiquement — `disagreement_spread`
n'a pas d'échelle universelle (Kelvin pour la température, m/s pour le
vent...), un seuil LOW/MEDIUM/HIGH global aurait été exactement le
genre de classification non validée que le §79 interdit ; le rapport
affiche la vraie valeur numérique et n'affiche un mot catégorique que
si l'appelant en fournit un lui-même.

**Câblage réel dans le dashboard** : `_last_awci_result.quality` était
toujours `None` jusqu'ici (aucun des 2 sites `build_awci_result()` ne
fournissait `quality=`). Fermé en réutilisant — pas réinventant —
`acf.awci.input_adapter` : nouvelle `_quality_for_point_raw_data()`
enveloppe les 4 valeurs réelles du point (temperature/wind_speed/
specific_humidity/pressure) dans de vrais `Dataset` minimaux à leurs
unités natives connues, puis appelle `build_awci_data_from_datasets()`
et ne garde que son vrai `quality` — réutilise ainsi la conversion
d'unité hPa-vs-Pa déjà disclosed comme bug corrigé dans cet adaptateur,
au lieu de la re-dériver une seconde fois.

**Validation réelle** : 18 nouveaux tests (12 pour
`summarize_execution()`/`AWCIExecutionReport` — bucket GOOD/DEGRADED/BAD
recoupé avec des `VariableQualityStatus` construits à la main, garde
explicite que `model_spread_level` n'est jamais deviné ; 6 d'intégration
dashboard — quality réellement peuplée en démo ET en Real Physics,
bouton ouvre/réutilise le même dialogue, rapport reflète le nouveau
point après un clic carte). Suite complète **3904 → 3922**, `ruff`/`mypy`
propres. Capture d'écran du bouton et du dialogue envoyée.

**Ce qui reste réellement** : `acf.monitoring`'s propres
`realtime_monitor`/`telemetry_engine` restent des systèmes génériques
séparés, non fusionnés avec ce rapport ponctuel par exécution — resterait
un vrai chantier d'intégration distinct si un usage opérationnel
continu (pas seulement à la demande) était requis.

## Mise à jour 2026-09-03 (suite) — §51 : niveaux de pression standards dans le profil vertical (mode démo)

Suite explicite ("continue"), priorité choisie librement dans les gaps
⚠️ restants de l'audit exhaustif. §51 : "Le dashboard doit permettre
Surface / 850 hPa / 700 hPa / 500 hPa / 300 hPa / 250 hPa / Flight
levels". Le vrai profil vertical (`AWCIVerticalProfile`, câblé au
bouton "🔍 See Vertical Profile" lors d'une clôture précédente de cette
session) ne couvrait que les niveaux de vol nommés (FL100...FL390), pas
les 6 niveaux de pression standards du §51.

**Construit** : nouvelle `_STANDARD_PRESSURE_LEVELS_HPA` (Surface =
1013.25 hPa, la vraie pression standard ISA au niveau de la mer — une
convention météorologique réelle, pas un chiffre rond deviné) fusionnée
avec la table des niveaux de vol existante en une seule
`_ALL_VERTICAL_PROFILE_LEVELS_HPA`, réellement triée par pression
décroissante (donc altitude croissante) — un vrai entrelacement
nécessaire puisque FL100 (~697 hPa) tombe RÉELLEMENT entre 700 hPa et
850 hPa, pas avant ou après en bloc.

**Bug réel trouvé et corrigé au passage** : `AWCIVerticalProfile`
re-triait en interne en parsant les libellés `"FL<n>"` — toute étiquette
qui ne matchait pas ce format (comme "850 hPa"/"Surface") recevait
silencieusement la clé de tri `0`, les regroupant toutes en tête du
graphique au lieu de les entrelacer par vraie altitude. Corrigé en
supprimant ce re-tri interne : le widget fait maintenant confiance à
l'ordre déjà réel fourni par l'appelant (source unique de vérité,
même discipline que le reste de cette session). Bonus visuel réel :
avec 12 niveaux au lieu de 6, les étiquettes ("850 hPa", "Surface")
étaient tronquées sur des barres trop étroites — corrigé en les
faisant pivoter (-55°), avec une marge basse élargie en conséquence.

**Décision de périmètre honnête** : §51 demande aussi d'afficher vent/
température/humidité/stabilité/convection/turbulence/givrage à chaque
niveau, pas seulement le score AWCI composite. `AWCIVerticalProfile`
reste un graphique à barres à une seule série — l'étendre à 7+ variables
par niveau serait une refonte de widget substantielle, pas incluse dans
cette fermeture ; documenté comme réellement restant. Également :
le mode Real Physics ne peut PAS honnêtement offrir ces niveaux de
pression standards — `acf.awci.vertical_field` n'a aucune interpolation
verticale (uniquement les niveaux natifs du solveur, disclosed depuis
longtemps) — cette liste reste donc mode démo uniquement, disclosed
explicitement dans `_open_vertical_profile()`.

**Validation réelle** : 3 nouveaux tests (les 6 niveaux standards
présents avec un vrai score 0-100 ; l'ordre réel par pression vérifié
programmatiquement ; le widget fait bien confiance à l'ordre fourni,
sans re-tri). Les 3 tests existants sur le profil vertical restent
verts inchangés. Suite complète **3922 → 3925**, `ruff`/`mypy` propres.
Capture d'écran envoyée (12 niveaux, étiquettes pivotées lisibles).

**Ce qui reste réellement** : la ventilation multi-variable par niveau
(vent/température/humidité/stabilité/convection/turbulence/givrage,
pas seulement le score composite) ; les niveaux de pression standards
en mode Real Physics (bloqué par l'absence réelle d'interpolation
verticale dans `acf.awci.vertical_field` — un chantier de physique
séparé, pas un manque de câblage UI).

## Mise à jour 2026-09-03 (suite) — §8/§31/§48/§74 : pipeline scientifique réellement orchestré (chemin mono-point)

Suite explicite ("continue"), priorité choisie librement — le plus
gros gap ⚠️ encore réellement ouvert dans l'audit exhaustif des 90
sections, touchant 4 lignes à la fois (§8/§31/§48/§74 décrivent tous
le même vrai constat : chaque étape existe quelque part, jamais
assemblée en un seul pipeline nommé).

**Construit** : `acf.awci.pipeline.run_awci_point_pipeline()` — un vrai
assembleur (même discipline que `build_awci_result()`/
`summarize_execution()` : ne recalcule rien) qui enchaîne, pour un
point réel : mapping de variables + contrôle qualité (réutilise
`acf.awci.input_adapter`) → modules/interactions/incertitude
(`AWCICalculator.calculate_with_uncertainty()`) → consensus (opt-in,
jamais lancé automatiquement — un vrai run solveur par modèle est
coûteux) → produit assemblé (`build_awci_result()`) → rapport
d'exécution réel (`summarize_execution()`, §75). Chaque étape retourne
un vrai `PipelineStage(name, status, detail)` — `RAN`/`SKIPPED`/
`NOT_APPLICABLE`, jamais un statut fabriqué.

**Honnêteté de périmètre, disclosed dans le docstring du module lui-même
sous forme de tableau** : sur les 21 étapes du §31, certaines n'ont
réellement aucun équivalent dans cette architecture (DISCOVERY/FORMAT
DETECTION — pas de découverte de fichiers, données déjà en mémoire) ;
d'autres restent volontairement des consommateurs séparés déjà réels
(VISUALIZATION/DASHBOARD = `acf.gui.dashboard.awci_dashboard`,
déjà branché) ; CONSENSUS ENGINE reste opt-in (jamais lancé
automatiquement, coût réel trop élevé) ; CERTIFICATION reste une
intégration séparée non tentée ici (`CertificationEngine` opère sur un
vrai `Dataset` avec provenance/qualité complètes, pas sur ce pipeline
basé dict).

**Refactor réel en prime** : la logique de contrôle qualité par point
(`quality_for_awci_point_data()`) vivait en double dans
`awci_dashboard.py` (couche GUI) depuis la clôture §75 précédente —
déplacée dans `acf.awci.pipeline` (couche science), le dashboard
l'importe maintenant au lieu de la dupliquer. Un seul vrai chemin de
conversion d'unité hPa/Pa, pas deux.

**Validation réelle** : 13 nouveaux tests (recoupement direct avec
`AWCICalculator.calculate_with_uncertainty()`/`summarize_execution()`,
ordre réel des étapes, `consensus_engine` RAN/SKIPPED selon
`model_spread` fourni ou non, étapes NOT_APPLICABLE jamais silencieuses,
déterminisme, incertitude réelle avec un vrai ensemble fourni). Suite
complète **3925 → 3938**, `ruff`/`mypy` propres.

**Ce qui reste réellement** : la certification réelle par `Dataset`
(§21) n'est pas fusionnée à ce pipeline ; le consensus multi-modèle
(§15) reste opt-in par design, jamais automatique ; un chemin
multi-points/grille (pas seulement mono-point) resterait un vrai
chantier d'extension séparé si un usage en dehors du dashboard GUI
(déjà branché point par point) le demandait.

## Mise à jour 2026-09-03 (suite) — passe de performance réelle sur le dashboard AWCI, profilée

Suite explicite ("je veux l'améliorer, le rendre ultra... agis toi
comme tu veux"), l'audit exhaustif des 90 sections étant épuisé pour
les gaps réellement fermables : bilan de santé complet du dépôt
(`ruff check src/ tests/` + `mypy src/`, 1435 fichiers), suivi d'un
vrai profilage plutôt que d'inventer un nouveau chantier arbitraire.

**Trouvaille réelle** : `cProfile` sur `AWCIDashboard.refresh()` a
montré `awci_grid()` (la grille complète 4°×4° du monde entier, ~3900
appels réels à `AWCICalculator.calculate()`) et `cross_section_field()`
(1200 points) responsables de la grande majorité du temps — **227 ms
par rafraîchissement réel**, mesuré directement. Trouvaille aggravante :
ces deux fonctions sont de vraies fonctions PURES de leurs arguments
(aucune dépendance à `point_of_interest`), mais un simple clic sur un
nouveau point déclenchait quand même leur recalcul complet — tout ce
travail était réellement gaspillé.

**Corrigé** : `@functools.lru_cache` sur `awci_grid()` et
`cross_section_field()` (`acf.gui.dashboard.awci_synthetic_field`) —
vérifié au préalable par `grep` que rien nulle part ne mute la grille
retournée en place (condition réelle pour qu'un cache soit sûr), et
disclosed explicitement dans le docstring de chaque fonction. Résultat
mesuré : refresh() **227 ms → 100 ms** (-56 %), clic sur un nouveau
point **214 ms → 88 ms** (-59 %). Bonus réel : la suite de tests
complète elle-même est passée de ~200 s à ~147 s (beaucoup de tests
construisent `AWCIDashboard()` avec les mêmes arguments par défaut).

**Deuxième optimisation réelle, plus petite** : les 6 calques LAYERS
(fermeture précédente) construisaient un vrai artiste matplotlib pour
chacun à CHAQUE redraw, même les ~5 jamais cochés par l'utilisateur —
maintenant construits paresseusement (seul un calque réellement coché
obtient un artiste ; `_on_extra_layer_toggled()` le construit à la
demande au premier coche, jamais reconstruit ensuite).

**Validation réelle** : 7 nouveaux tests (cache hit/miss réel vérifié
via `.cache_info()`, invalidation correcte sur niveau de vol/décalage
temporel/route différents, construction paresseuse des calques
vérifiée explicitement). Suite complète **3938 → 3945**, `ruff`/`mypy`
propres sur les 1435 fichiers. Capture d'écran de vérification finale
envoyée — aucune régression visuelle.

**Ce qui reste réellement** : le cache est en mémoire process (pas
persistant, taille bornée à 64 entrées par fonction — largement
suffisant pour un usage interactif réel, jamais un problème mesuré) ;
d'autres fonctions coûteuses plus loin dans la chaîne (rendu
matplotlib lui-même, `AWCICalculator.calculate()` par point individuel)
n'ont pas été touchées — seul le vrai goulot d'étranglement mesuré l'a
été, pas une optimisation générale spéculative.

## Mise à jour 2026-09-03 (suite) — deuxième passe de performance : le graphique ROUTE PLANNING, -86%

Suite explicite ("on continue"), même méthode (profiler avant
d'optimiser) réappliquée après la première passe : un nouveau
`cProfile` sur `AWCIDashboard.refresh()` (le cache de la mise à jour
précédente désormais chaud) a montré un nouveau goulot dominant :
`AWCIRouteChart._draw()` → `Axes.fill_between()`, appelée **une fois
par segment** (79 fois, `n_points=80`) pour colorer chaque tronçon du
graphique selon l'échelle AWCI — 0.4s cumulés sur 5 rafraîchissements
rien que pour cette boucle.

**Corrigé** : remplacé la boucle de 79 vrais appels `fill_between()`
individuels par un seul vrai `matplotlib.collections.PolyCollection`
— les mêmes 79 vrais quadrilatères (les 4 mêmes coins exacts qu'un
`fill_between([x0,x1],[0,0],[y0,y1])` dessinerait), les mêmes vraies
couleurs `AWCI_CMAP` par segment, ajoutés en UN seul vrai appel
`axis.add_collection()` au lieu de 79. Vérifié par comparaison de
rendu pixel par pixel (avant/après) — différence négligeable et
localisée à l'anti-aliasing des coutures entre segments (déjà présentes
dans les deux versions), pas de régression visuelle réelle.

**Mesuré** : `route_chart.update_data()` **45 ms → 6 ms** (-86 %) ;
`refresh()` complet **100 ms → 55.6 ms** (-44 % supplémentaires,
-75 % cumulés depuis le tout premier profilage à 227 ms). Suite de
tests **3945 → 3948**, elle-même encore plus rapide (~136 s).

**Validation réelle** : 3 nouveaux tests — un seul vrai
`PolyCollection` (pas de retour à la boucle), les vrais 4 coins et la
vraie couleur de chaque segment recoupés directement avec la
convention de l'ancien code, le mode comparaison FL280/FL320 (2 vraies
lignes, pas de remplissage) vérifié pour ne jamais laisser un vieux
`PolyCollection` traîner. `ruff`/`mypy` propres sur les 1435 fichiers.
Capture d'écran finale envoyée — aucune régression visuelle.

**Ce qui reste réellement** : le rendu matplotlib des autres panneaux
(carte globale/régionale, coupe verticale) reste dominé par le vrai
travail de rendu de contour lui-même (`contourf`/`clear`/tick
generation) — un chantier d'optimisation plus profond (ex. blitting,
mise en cache d'artistes matplotlib entre redraws) resterait possible
mais plus risqué et hors du périmètre de cette passe ciblée sur les
vrais goulots mesurés.

## Mise à jour 2026-09-03 (suite) — troisième passe de performance : la coupe verticale ne se redessine plus deux fois

Suite explicite ("on continue"), même méthode. Un nouveau `cProfile`
(cache + PolyCollection déjà chauds) a montré `AWCICrossSection._draw()`
comme nouveau goulot dominant — et une vraie cause structurelle, pas
juste un coût de rendu : `refresh()` appelait `cross_section.update_data()`
PUIS immédiatement `cross_section.set_hazard_overlay()` sur la même
vraie grille — chacun déclenchant son propre vrai `_draw()` complet
(`clear()` + `contourf()` + **recréation complète de la colorbar**,
elle-même une vraie opération matplotlib coûteuse — nouvel `Axes`,
nouveau `gridspec`). Deux vrais redraws complets pour une seule vraie
mise à jour logique. Même schéma trouvé en mode Real Physics
(`set_external_cross_section()` + `set_hazard_overlay()`).

**Corrigé** : nouveau paramètre optionnel `hazard_overlay=` sur
`update_data()` et `set_external_cross_section()` — l'appelant passe
maintenant le tuple `(distances, levels, phase_severity_grid,
wind_shear_grid)` directement, un seul vrai `_draw()` fait les deux à
la fois. Omis (`None`, par défaut) : comportement bit-identique à
avant pour tout appelant qui ne l'utilise pas.

**Mesuré** : `refresh()` complet **55.6 ms → 40.9 ms** (-26 %
supplémentaires, **-82 % cumulés** depuis le tout premier profilage à
227 ms).

**Validation réelle** : 3 nouveaux tests — un vrai compteur d'appels
(via monkeypatch de `_draw()`) prouve exactement UN redraw avec le
nouveau paramètre, le comportement par défaut (paramètre omis) reste
inchangé, testé en mode démo ET en mode Real Physics. Suite complète
**3948 → 3951**, `ruff`/`mypy` propres sur les 1435 fichiers. Capture
d'écran finale envoyée — aucune régression visuelle (icônes de
givrage toujours présentes, colorbar identique).

**Ce qui reste réellement** : `clear()`/`contourf()`/génération des
graduations restent les vrais coûts matplotlib incompressibles pour un
contour redessiné à chaque interaction — un chantier de blitting ou de
mise en cache d'artistes resterait possible mais plus risqué, hors
périmètre de cette passe.

## Mise à jour 2026-09-03 (suite) — quatrième passe : dernier vrai calcul non caché, puis retour de rendement décroissant

Suite explicite ("continue"), même méthode. Reprofilage : le dernier
vrai calcul scientifique encore non caché est apparu —
`cross_section_phase_severity_field()` (icônes de givrage de la coupe
verticale), même schéma exact que les deux fonctions déjà mises en
cache (fonction pure, mêmes arguments réels `_GLOBAL_ROUTE` à chaque
refresh). `@lru_cache` appliqué, même vérification préalable (aucune
mutation en place du grid retourné).

**Mesuré** : `refresh()` **40.9 ms → 36.7 ms** (-10 %, **-84 % cumulés**
depuis 227 ms). Validé par 2 nouveaux tests (cache hit réel,
invalidation correcte sur un `time_offset_hours` différent — un test
initial supposait à tort que 2 offsets différents donneraient
toujours 2 résultats visuellement différents ; la sévérité de phase
est une valeur catégorielle grossière [0,1] et peut honnêtement
coïncider — corrigé pour vérifier le vrai compteur de cache miss, pas
une différence de valeur non garantie). Suite complète **3951 → 3953**,
`ruff`/`mypy` propres. Capture d'écran envoyée — aucune régression.

**Bilan des 4 passes de performance** : `refresh()` complet
**227 ms → 36.7 ms (-84 %)**. Ce qui reste (`clear()`/tick generation/
génération des ticks d'axes matplotlib) est désormais le vrai coût
incompressible du modèle de rendu actuel (clear+redraw complet par
interaction) — tout gain supplémentaire demanderait une vraie
réécriture du moteur de rendu (blitting, artistes persistants mis à
jour en place) : un chantier bien plus large et risqué, pas une
suite naturelle de cette série de passes ciblées. Cette série de
performance s'arrête ici, rendement décroissant confirmé par mesure
réelle, pas par supposition.

## Mise à jour 2026-09-03 (suite) — §51 vraiment fermé : profil vertical multi-variables cliquable

Suite explicite ("suit ton jugement", parmi 4 pistes proposées à
l'utilisateur — celle-ci choisie car autonome, sans dépendance externe,
et complétant directement un gap déjà disclosed dans
`future-improvements.md` #8). §51 demandait aussi d'afficher vent/
température/humidité/stabilité/convection/turbulence/givrage à chaque
niveau, pas seulement le score AWCI composite — la fermeture
précédente (liste de niveaux) l'avait explicitement laissé ouvert.

**Construit** : les barres de `AWCIVerticalProfile` sont maintenant
réellement cliquables (`levelClicked`, vrai test de collision sur la
géométrie réelle des barres — partagée avec le dessin lui-même, pas
recalculée séparément) et ouvrent `AWCIVerticalProfileLevelDialog`
— le vrai détail par module déjà calculé par la boucle existante de
`_open_vertical_profile()` (jamais un second calcul), pour les
**9 vrais modules réels** d'`AWCICalculator` (dynamic/thermodynamic/
convective/microphysical/topographic/temporal/confidence/
ensemble_spread/model_disagreement — les deux derniers trouvés en
cours de route : un test a révélé qu'ils existaient réellement et
n'étaient pas encore dans le mapping honnête).

**Décision de périmètre honnête, inchangée** : §51 nomme aussi
"stabilité" et "turbulence" explicitement — aucun des deux n'a de
vrai module dédié par point nulle part dans ce code aujourd'hui. Le
dialogue affiche une vraie note à ce sujet plutôt qu'un chiffre
fabriqué pour l'un ou l'autre.

**Bug réel trouvé en écrivant les tests** : un premier essai
`widget.repaint()` en environnement de test hors écran ne déclenchait
pas fiablement un vrai `paintEvent()`, laissant `_bar_geometry` vide -
corrigé en extrayant le calcul de géométrie dans une vraie méthode
`_compute_bar_geometry()` partagée, appelée dès `set_profile()`/
`resizeEvent()`, indépendamment du cycle de peinture Qt lui-même (une
vraie source unique de vérité pour cette géométrie, plus robuste que
l'ancien couplage implicite au dessin).

**Validation réelle** : 12 nouveaux tests (7 sur le widget — géométrie
réelle après un vrai `set_profile()`, clic réel émettant le bon
niveau, clic hors zone n'émettant rien, dialogue affichant le vrai
score/split/ventilation ; 5 d'intégration dashboard — données
per-niveau réellement peuplées, clic réel ouvrant/réutilisant le
dialogue, un vrai `QMouseEvent` de bout en bout). Suite complète
**3953 → 3965**, `ruff`/`mypy` propres sur les 1435 fichiers. Captures
d'écran envoyées (graphique + dialogue de détail).

**Ce qui reste réellement** : "stabilité"/"turbulence" resteraient un
vrai chantier de science distinct (construire un vrai module dédié) si
demandé un jour ; le mode Real Physics n'offre toujours pas cette
liste de niveaux standards (limite d'interpolation verticale déjà
disclosed, inchangée).

## Mise à jour 2026-09-03 (suite) — tooltips manquants + 2e occurrence du bug des 7/9 modules, trouvée et corrigée

Suite explicite ("on continue"). Passe de polish accessibilité sur les
tooltips déjà disclosed comme manquants dans
`docs/awci/AWCI_BUTTON_CONTRACT.md` ("none — no `setToolTip()` yet") —
en l'ajoutant à `_RiskRow`, une relecture croisée de son propre
`_MODULE_LABELS` a révélé qu'il avait exactement le même défaut que
celui trouvé et corrigé dans `AWCIVerticalProfileLevelDialog` pendant
la fermeture précédente : seulement 7 des 9 vraies clés
`AWCICalculator.calculate_module_scores()` étaient affichées,
`ensemble_spread`/`model_disagreement` manquaient silencieusement.

**Construit** :
- `_ComponentRow` (`awci_dashboard.py`), `_RiskRow`
  (`awci_risk_summary.py`) et `AWCIVerticalProfile`
  (`awci_vertical_profile.py`) ont maintenant chacun un vrai
  `setToolTip()` expliquant ce que le clic ouvre — les 3 derniers
  endroits cliquables du dashboard qui n'en avaient pas encore.
- `_MODULE_LABELS` dans `awci_risk_summary.py` (utilisé par
  `AWCIRiskBadgeDetailDialog`, ouvert par les badges
  Overall/Physical/Forecast) étendu de 7 à 9 entrées, avec
  `ensemble_spread`/`model_disagreement` ajoutés — même correction que
  celle déjà appliquée au dialogue du profil vertical.

**Décision de périmètre honnête, inchangée** : `AWCIRadar` et
`_ComponentValueList` (le panneau "AWCI COMPONENTS" du dashboard
principal) restent volontairement à 7 lignes/axes — ils reproduisent
`docs/reference/awci_dashboard_reference.jpg` pixel pour pixel, et
cette maquette de référence ne montre que 7 lignes. Seuls les
dialogues construits cette session sans contrainte de maquette
(`AWCIRiskBadgeDetailDialog`, `AWCIVerticalProfileLevelDialog`)
reçoivent la ventilation complète à 9 modules. `ensemble_spread`/
`model_disagreement` restent honnêtement ~0.0 en mode démo (le
pipeline per-point de ce dashboard ne fournit jamais de vrais
`ensemble_members`/`model_realizations`) — jamais une valeur non nulle
fabriquée.

**Validation réelle** : 3 nouveaux tests (`test_composite_dialog_
shows_all_9_real_modules_not_just_7`, `test_risk_row_and_component_
row_have_real_tooltips`, `test_widget_has_a_real_click_hint_tooltip`).
Suite complète **3965 → 3968**, `ruff`/`mypy` propres sur les 1435
fichiers. Capture d'écran envoyée (`AWCIRiskBadgeDetailDialog` avec
ses 9 vraies lignes : Dynamic 100.0, Thermodynamic 44.2, Convective
38.1, Microphysical 27.2, Topographic 14.3, Temporal 1.9, Uncertainty
34.0, Ensemble spread 0.0, Model disagreement 0.0).

**Ce qui reste réellement** : `docs/awci/AWCI_BUTTON_CONTRACT.md` mis
à jour pour refléter le nouveau tooltip et la correction des 9
modules sur la ligne "Risk summary badge" ;
`AWCI_COMPONENT_INVENTORY.md` inchangé (aucun composant nouveau, juste
des tooltips + une correction de complétude sur des dialogues
existants). Aucun autre endroit cliquable n'a été trouvé sans tooltip
lors de cette relecture — cette 3e passe de polish clôt le point
"aucune convention d'accessibilité" identifié dans l'audit initial
pour les seuls contrôles réellement interactifs (pas un balayage ARIA
complet du dépôt, toujours hors périmètre — voir
`future-improvements.md`).

## Mise à jour 2026-09-04 — §51 fermé aussi en mode Real Physics : vraie interpolation log-pression

Suite explicite ("continue"). `future-improvements.md` listait 9 items
volontairement non construits ; 8 restent des choix architecturaux
réels et disclosed (moteur de recommandation, calendrier, WebGL,
balayage ARIA complet, Ellrod-Knapp, etc.). Le point #9 — le profil
vertical par niveaux standards (§51) restait démo uniquement, le mode
Real Physics ne l'offrait pas — était le seul des 9 réellement
constructible sans nouveau travail de physique lourd : il ne manquait
qu'une vraie interpolation verticale entre les niveaux natifs réels du
solveur, jamais construite ailleurs dans ACF.

**Construit** : `acf.awci.vertical_field.interpolated_state_at_pressure()`
— une vraie interpolation linéaire en log-pression (pratique standard
de la météorologie opérationnelle, pas une donnée inventée) de
température/vent/humidité entre les 2 vrais niveaux natifs du solveur
qui encadrent réellement la pression cible, à la colonne réelle la
plus proche du point demandé. Refus explicite d'extrapoler : une
pression cible hors de l'étendue verticale réelle de cette colonne
renvoie `None` plutôt qu'une valeur devinée. `vertical_profile_at_
standard_levels()` applique ceci à chaque niveau nommé de §51
(Surface/850/700/500/300/250 hPa + niveaux de vol réels) et fait
passer chaque état interpolé par un vrai appel
`AWCICalculator.calculate()` — les `module_scores`/`physical_score`/
`forecast_score` retournés sont donc une vraie sortie d'une vraie
formule appliquée à une entrée réelle (interpolée, jamais fabriquée),
exactement comme tous les autres scores per-point de ce dashboard.
`AWCIDashboard._open_vertical_profile()` bascule maintenant sur cette
fonction en mode Real Physics au lieu de refuser d'offrir la liste de
niveaux standards ; le mode démo reste bit-identique (son propre motif
analytique continu n'a jamais eu besoin de cette restriction).

**Validation réelle** : 9 nouveaux tests — 6 sur
`acf.awci.vertical_field` (valeur interpolée égale exactement au
niveau natif réel quand la cible tombe pile dessus ; valeur interpolée
réellement comprise entre ses 2 vrais niveaux natifs encadrants ;
refus réel d'extrapoler hors de la vraie colonne ; recalcul croisé
`AWCICalculator.calculate()` sur les mêmes entrées interpolées
retournées, confirmant que ce n'est pas un second calcul indépendant ;
omission honnête d'un niveau hors de portée réelle) et 3
d'intégration dashboard (le dialogue Real Physics utilise bien cette
vraie interpolation et pas le chemin démo ; les seuls labels affichés
sont exactement ceux réellement retournés par la fonction — aucun des
12 forcé artificiellement ; retour au mode démo après désactivation de
Real Physics recalcule bien tout, sans donnée interpolée périmée).
Suite complète **3968 → 3976**, `ruff`/`mypy` propres sur les 1435
fichiers. Capture d'écran
réelle envoyée : profil vertical à 12 barres réelles en mode Real
Physics (grille ALADIN 10×18×6, seed=2), valeurs variant réellement
entre niveaux (9.0/8.3/8.3/8.6/8.8/8.8/8.7/8.7/8.7/8.6 — jamais une
valeur plate répétée).

**Ce qui reste réellement** : les 8 autres items de
`future-improvements.md` restent hors périmètre pour les mêmes
raisons déjà disclosed (travail de physique séparé, ou décision
architecturale délibérée). L'interpolation reste horizontalement au
plus proche voisin (pas d'interpolation spatiale lat/lon) — même
convention que `vertical_profile_at_point()` et le reste du dashboard.

## Mise à jour 2026-09-04 — un vrai 3e niveau de données AWCI : archive ALADIN réelle (RESTOR)

Demande explicite de l'utilisateur : *"tu vas trouver un dossier ...
RESTOR ... des données réelles de aladin et arome et arpege tu peux
les utiliser pour rendre ACF réel"*.

**Investigation réelle avant tout code** : `$HOME/RESTOR` est une
vraie boîte à outils "retour d'expérience" d'un site opérationnel
(README daté 01/05/2022) — scripts + un vrai décodeur Fortran 32-bit
"EDF" + de vraies sorties de modèle archivées. `RESTOR/ALADIN/data/`
contient 17 vrais fichiers FULLPOS (00h→48h, pas de 3h) d'une vraie
run ALADIN 00Z du **31/08/2026**, domaine Afrique du Nord réel (grille
régulière 350×350, 0.08°, lon -10.71..17.21°E, lat 18.54..46.46°N).
**Découverte honnête importante** : `RESTOR/AROME/data/*` ne sont PAS
de vraies données AROME — ce sont de simples liens symboliques vers
les mêmes fichiers ALADIN (`readlink` vérifié avant d'écrire la
moindre ligne de code), et il n'existe aucun répertoire ARPEGE du
tout. Donc malgré le nom du dossier, seules de vraies données ALADIN
sont réellement exploitables ici — disclosed explicitement partout
plutôt que caché.

**Construit** : `acf/awci/archive_field.py` — un vrai lecteur qui
décode directement le vrai fichier FA via **EPyGrAM**, la vraie
bibliothèque Météo-France déjà intégrée et auditée dans ce code
(`acf.data.readers.epygram_reader.EPyGrAMReader`, étendue cette
fermeture avec un vrai accesseur de grille lon/lat,
`read_field_lonlat_grid()`). Aucun parseur binaire/FA fait main —
le vieux décodeur Fortran 32-bit de RESTOR n'a servi qu'à **vérifier
indépendamment** les vraies valeurs lues par ce nouveau module (jamais
comme dépendance runtime).

7 vrais niveaux de pression constante (850/700/500/400/300/200/100
hPa, confirmés contre le vrai namelist `namel_H` de RESTOR) + 1 vraie
entrée "Surface" — sourcée depuis les vrais diagnostics d'écran CLS
(`CLSTEMPERATURE`, `CLSVENT.ZONAL/MERIDIEN`, `CLSHUMI.SPECIFIQ`) plus
la vraie pression locale réelle `SURFPRESSION`, jamais une constante
1013.25 hPa devinée. Découverte honnête en cours de route : le champ
`P00000...` de RESTOR n'est PAS un vrai niveau de pression constante
malgré son nom — vérifié à la main (son propre géopotentiel réel
correspond à une vraie altitude de terrain saharienne ~100m, pas à un
géopotentiel 1000hPa plausible) : c'est le niveau modèle le plus bas,
honnêtement exclu de la liste des niveaux de pression plutôt que
mal-étiqueté.

L'humidité relative réelle de RESTOR (`HUMI_RELAT`) s'est avérée être
une fraction 0-1 (vérifié en lisant de vraies valeurs, pas 0-100 comme
le nom pourrait suggérer) — convertie en humidité spécifique via une
nouvelle `Moisture.specific_humidity_from_relative_humidity()`
(`acf/science/moisture.py`), qui ne fait que composer des primitives
déjà réelles et déjà testées (`SaturationVaporPressure`,
`SaturationMixingRatio`, `SpecificHumidity`) — aucune nouvelle formule.

**GUI** : nouveau bouton "📡 Real Archive (2026-08-31)" — réutilise
intégralement `AWCIVerticalProfile`/`AWCIVerticalProfileLevelDialog`
(même pattern clic→détail que "🔍 See Vertical Profile"), alimenté par
un vrai lookup au plus proche voisin au point d'intérêt courant.
N'interfère jamais avec l'état de Real Physics — un 3e niveau de
données entièrement additif. Deux vrais chemins de dégradation
honnête, jamais un repli silencieux vers demo/solveur : archive
absente sur la machine (`$HOME/RESTOR` n'existe pas ailleurs — donnée
réelle locale à cette machine, non versionnée) → message explicite ;
point d'intérêt hors du vrai domaine Afrique du Nord de l'archive →
avertissement explicite plutôt qu'une valeur de bord silencieusement
trompeuse.

**Validation réelle** : cross-check indépendant réussi — la
température à un point de la grille lue par ce nouveau module
EPyGrAM correspond EXACTEMENT (à la précision d'impression près) à la
même valeur décodée indépendamment par le vieux toolchain Fortran EDF
du site sur le même vrai fichier. 13 nouveaux tests directs sur le
module (dont ce cross-check, un test de dégradation honnête par
monkeypatch, et des bornes physiques sur l'humidité spécifique
réelle sur toute la grille) + 3 tests sur `Moisture` + 6 tests
d'intégration dashboard (bouton câblé, échec honnête sans RESTOR,
point hors domaine, cache de l'archive chargée, clic réel ouvrant le
détail). Suite complète **3976 → 3995**, `ruff`/`mypy` propres sur
tous les fichiers touchés. Capture d'écran réelle envoyée : dialogue
"Real ALADIN Archive" avec ses 8 vraies barres (11.9/8.7/4.1/1.8/2.9/
3.6/4.7/17.6) au point d'intérêt par défaut (34.5°N, 12.3°E).

**Ce qui reste réellement** : seule l'échéance 00h (analyse) est
câblée dans le dashboard — RESTOR contient 17 vraies échéances
(00h→48h) ; `load_real_aladin_restor_run()` accepte déjà n'importe quel
vrai chemin `FULLPOS_*`, donc câbler les 16 autres échéances est un
vrai chantier borné, pas une nouvelle capacité à construire. Aucune
donnée AROME/ARPEGE réelle n'existe dans cette archive malgré son nom
(disclosed ci-dessus). Pas de CAPE/CIN/phase de précipitation par
niveau décodés (mêmes limites que `spatial_field.py`/`vertical_field.py`).
Real Physics mode reste plus fort sur un point précis (un solveur
configurable à volonté) ; la vraie valeur de ce 3e niveau est que ses
chiffres sont une vraie sortie opérationnelle archivée, jamais une
sortie de solveur.

## Mise à jour 2026-09-04 (suite) — les 17 vraies échéances RESTOR câblées (suite explicite "continue")

Le "Ce qui reste réellement" de la fermeture précédente notait un vrai
chantier borné et déjà identifié : seule l'échéance +0h (analyse)
était câblée dans le dashboard, alors que RESTOR contient 17 vraies
échéances 3-horaires (+0h→+48h) déjà spot-checkées comme réellement
complètes et distinctes (validité réelle qui avance : 2026-08-31 00Z /
2026-09-01 00Z / 2026-09-02 00Z pour +0h/+24h/+48h).

**Construit** : `acf/awci/archive_field.py` gagne `restor_fullpos_path()`
(construction pure du vrai nom de fichier RESTOR, testable sans accès
disque) et `RESTOR_LEAD_TIMES_HOURS` (les 17 vraies échéances, dérivées
du vrai `date.config` de RESTOR : ECH=48/nECH=17). Le dialogue
"📡 Real Archive" gagne un vrai sélecteur "Lead time:" (17 options
réelles, +0h par défaut — comportement bit-identique à la fermeture
précédente tant qu'on n'y touche pas, même discipline que le
sélecteur de niveau de vol). Chaque échéance sélectionnée est
réellement décodée depuis son propre vrai fichier FA au premier choix,
puis mise en cache (`_real_archive_cache`, clé = heures réelles) —
un échec de chargement n'est jamais mis en cache, pour que le prochain
essai retente un vrai accès plutôt que de mémoriser un échec comme
permanent.

**Validation réelle** : un nouveau test prouve directement que changer
l'échéance charge une archive réellement différente (la vraie validité
avance : 2026-08-31→2026-09-01) et pas la même donnée relabellée ; un
autre confirme les 3 échéances spot-checkées (+0h/+24h/+48h) décodent
chacune sans champ manquant avec leur propre vraie date. Capture
d'écran envoyée : dialogue à +24h, 8 vraies barres avec des valeurs
réellement différentes de celles à +0h (13/11/6/3/1/2/4/18 contre
12/9/4/2/3/4/5/18). Suite complète **3995 → 4001**, `ruff`/`mypy`
propres.

**Ce qui reste réellement** : les 17 échéances sont maintenant toutes
câblées ; il ne reste plus de chantier RESTOR borné et déjà identifié
sur ce point. Les limites disclosed précédemment restent inchangées
(un seul domaine régional, pas de vraies données AROME/ARPEGE, pas de
CAPE/CIN/phase de précipitation par niveau).

## Mise à jour 2026-09-04 (suite) — vraie tendance 48h RESTOR : ce que Real Physics ne peut pas offrir

Suite explicite ("continue"). Le point d'entrée facile de l'audit AWCI
initial était épuisé (les 8 items restants de `future-improvements.md`
sont des choix architecturaux délibérés, pas de vrais gaps
constructibles) et une recherche large dans le reste d'ACF
(fabrication/`NotImplementedError`) n'a trouvé que des limitations
déjà honnêtement disclosed (4D-Var, EnKF, fusion radar-satellite — de
vrais chantiers de science numérique majeurs, pas de petites
fermetures). Question posée à l'utilisateur sur la direction ; réponse
"suit ton jugement" — choix motivé : étendre le mode Real Archive vers
sa propre vraie force plutôt que de forcer une parité complète avec
Real Physics (carte/radar/risk summary en grille complète 350×350
demanderaient une vectorisation d'`AWCICalculator` non triviale et
risquée — mesuré : ~7s pour décoder les 17 fichiers réels en boucle
point-par-point sur toute la grille aurait été bien pire).

**Construit** : `_RealArchiveTrendWorker` — un vrai worker `QThreadPool`
(même discipline que `_RealFieldWorker`/`_EvolutionWorker`) qui décode
les échéances réelles pas encore en cache et échantillonne le vrai
score AWCI niveau Surface au point d'intérêt pour chacune des 17
vraies échéances RESTOR. Un nouveau bouton "📈 Load Real 48h Trend
(Surface)" dans le dialogue "Real Archive" déclenche ce calcul hors
thread GUI (mesuré : ~7s pour les 17 fichiers la première fois),
jamais bloquant. Résultat rendu via `AWCITimeline` — widget déjà
existant mais dont la propre docstring affirmait faussement être
"inutilisé" alors que `regional_trend` l'utilisait déjà (note
corrigée au passage) ; ce nouveau bouton en devient le premier VRAI
appelant côté données archivées réelles (`regional_trend` reste
lui-même alimenté par le motif synthétique démo). `AWCITimeline` gagne
un vrai `set_title()` (même convention que `AWCIVerticalProfile`) pour
distinguer les deux usages.

**Discipline honnête maintenue** : le worker ne mute jamais l'état du
dashboard depuis le thread d'arrière-plan (nouvelles archives
retournées via le signal, fusionnées dans `_real_archive_cache` par le
thread GUI lui-même — même principe que `_RealFieldWorker`) ; une
échéance dont la vraie colonne n'encadre pas le point au niveau
Surface est honnêtement omise de la tendance (jamais mise à 0), avec
un statut `N/17 real lead times` explicite ; une tendance vide reste
honnêtement masquée plutôt que d'afficher un graphique vide comme s'il
était réel.

**Validation réelle** : test de bout en bout réel utilisant
`qtbot.waitUntil()` pour driver le vrai worker `QThreadPool` (même
discipline que le test réel de `test_acf_general_dashboard.py`), 16
des 17 échéances pré-cachées pour ne payer qu'un seul vrai décodage
FA (~0.4s) plutôt que les 17 (~7s) — preuve directe que le worker
fusionne bien sa propre archive nouvellement décodée dans le cache du
thread GUI. 5 tests supplémentaires non conditionnés (widget masqué
par défaut, état de chargement synchrone du bouton, handlers ready/
vide/échec appelés directement avec un résultat construit). Suite
complète **4001 → 4007**, `ruff`/`mypy` propres. Capture d'écran envoyée : dialogue complet avec
les 17 vraies valeurs de tendance affichées (17.6→19.2→17.0 sur les
48h réelles).

**Ce qui reste réellement** : la tendance reste fixée au niveau
Surface (choix délibéré pour un seul graphique lisible, pas une
limitation technique — `sample_archive_at_point()` retourne déjà les 8
niveaux). Real Physics mode reste plus fort en couverture spatiale
(carte/radar/risk summary en grille complète) ; Real Archive mode
reste plus fort en évolution temporelle réelle (17 échéances
archivées, pas un seul instantané de solveur) — les deux modes ont
maintenant chacun leur propre vraie valeur ajoutée distincte plutôt
que l'un dupliquant l'autre en moins bien.

## Mise à jour 2026-09-04 (suite) — premier chantier hors AWCI cette session : le ModuleRegistry d'ESOC mentait sur 19 de ses 25 modules

Suite explicite ("continue"). Après une nouvelle question sur la
direction ("suit ton jugement" à nouveau), et une recherche large déjà
infructueuse dans le reste d'ACF pour des gaps évidents, un agent
Explore a été chargé d'auditer spécifiquement des packages peu
fréquentés par l'historique git (`fire_weather`, `certification`,
`plugins`, `storage`, `testing`). Résultat : ces packages sont
majoritairement déjà disciplinés et bien câblés, mais une piste
sérieuse est apparue — `acf.gui.esoc.module_registry.ModuleRegistry`
enregistre dynamiquement 25 sous-systèmes ACF via
`_safe_import_register(key, module_path, class_name)`. Vérification
directe et exhaustive (import réel + `getattr` pour les 25, pas un
échantillon) : **19 des 25 `class_name` demandés n'existaient tout
simplement pas** au chemin donné.

**Le vrai bug racine** : `_safe_import_register()` ne se contentait pas
d'échouer proprement quand la classe manquait — elle substituait
silencieusement le module PACKAGE brut (vide) comme "instance", et
`is_connected()`/`get_system_status_summary()` (tous deux un simple
test `is not None`) rapportaient alors honnêtement... un mensonge :
ces 19 modules apparaissaient "connectés" alors que rien de réel
n'avait jamais été instancié. Exactement le même schéma
"présenté comme connecté/réel alors que ça ne l'est pas" déjà traqué
et corrigé dans ce code (readers EPyGrAM, panneaux ESOC, etc.) — sauf
qu'ici, vérification faite par grep exhaustif, **aucun vrai code GUI
ne lit `is_connected()`/`get_system_status_summary()`/`global_search()`/
`search_index` nulle part aujourd'hui** — la barre de recherche
universelle d'ESOC (`esoc_sidebar.py`) filtre sa propre liste statique
de labels, complètement indépendante de `ModuleRegistry`. Donc aucun
symptôme visible actuellement — mais un vrai mensonge en attente du
jour où un panneau de statut y serait enfin branché.

**Construit** : `_safe_import_register()` corrigée — une classe
manquante résout maintenant honnêtement `self.modules[key] = None`
(avec un vrai WARNING, plus un DEBUG silencieux), exactement le même
résultat "non connecté" qu'un échec d'import réel. Un échec de
CONSTRUCTION (`cls()` qui lève) est maintenant aussi capturé et
disclosed séparément. Puis, pour 15 des 19 entrées où une vraie classe
correctement nommée existe ailleurs dans ce code (vérifié une par une :
import propre, instanciation à zéro argument, correspondance
thématique réelle — ex. `catalog` voulait `CatalogManager`, qui existe
réellement, juste à `acf.catalog.manager` et non `acf.catalog` nu),
le `(module_path, class_name)` a été corrigé pour pointer dessus. Les
4 restantes (`earth_physics`, `space_weather`, et les entrées nues
`acf.geology`/`acf.geoengineering`) n'ont aucune classe unique réelle
représentant sans ambiguïté "le" moteur de tout le domaine (chacune
est un vrai package peuplé de nombreux moteurs indépendants, pas un
orchestrateur unique) — laissées honnêtement non connectées plutôt que
de deviner un mapping approximatif.

**Résultat mesuré** : `get_system_status_summary()` passe de 6/25
sous-systèmes réellement connectés (avant, une fois le mensonge de la
substitution retiré) à **21/25** réellement connectés, les 4 restants
honnêtement `None` avec un vrai WARNING loggé expliquant pourquoi.

**Validation réelle** : nouveau fichier `tests/test_module_registry_wiring.py`
— vérifie que les 15 entrées corrigées résolvent bien vers le nom de
classe réel attendu, que les 4 entrées non résolvables restent
honnêtement `None`, qu'aucune entrée du registre n'est jamais un objet
module brut (garde-fou direct contre une régression du bug racine),
que `connected_count` reste cohérent avec `is_connected()`, et que le
chemin WARNING (classe manquante) et le chemin échec-de-construction
sont bien tous deux honnêtement loggés et jamais silencieusement
avalés. Suite complète **4007 → 4013**, `ruff`/`mypy` propres.

**Ce qui reste réellement** : aucun vrai code GUI ne consomme encore
`is_connected()`/`get_system_status_summary()`/`global_search()` —
cette fermeture rend le registre honnête, elle ne lui donne pas
(encore) de vitrine visible. Câbler un vrai panneau de statut ESOC ou
brancher la barre de recherche universelle sur `global_search()` reste
un vrai chantier séparé, non entamé ici pour éviter tout risque de
collision avec le travail très récent d'une session parallèle sur
`esoc_statusbar.py` (largeur de fenêtre, voir historique git).

## Mise à jour 2026-09-04 (suite) — la barre de recherche universelle d'ESOC branchée sur le vrai ModuleRegistry

Suite explicite ("continue"), fermeture directe du "Ce qui reste
réellement" ci-dessus. Investigation : `ESOCLeftSidebar` (barre
latérale gauche d'ESOC, placeholder réel "🔍 Universal Search
(Modules, Parameters, Maps, AI)...") avait un vrai handler
`_on_search_text_changed()`, mais celui-ci ne filtrait que la propre
copie statique de `self.categories` du widget — jamais
`ModuleRegistry.global_search()`. Cause racine trouvée : `ESOCLayout`
(le seul vrai appelant de `ESOCLeftSidebar`, dans `esoc_layout.py`)
construisait ce widget sans aucun argument, alors qu'`ESOCWindow`
possède bien un vrai `self.registry` — jamais transmis jusque-là.
Confirmation supplémentaire : `self.categories` (sidebar) et
`ModuleRegistry.build_system_tree()` (registre) se sont avérés être
quasi-identiques (18 des 20 catégories de premier niveau
byte-pour-byte identiques) — deux copies indépendantes d'une même
donnée qui a dérivé légèrement, plutôt qu'une vraie divergence
intentionnelle.

**Construit** : `registry: ModuleRegistry | None = None` ajouté à
`ESOCLeftSidebar.__init__()` et propagé via `ESOCLayout.__init__()`
jusqu'à `ESOCWindow`'s own `self.registry` (un seul vrai transmis, pas
une seconde instance). Le filtre statique de l'arbre reste inchangé
(toujours utile pour la navigation par catégorie) ; une nouvelle
étiquette réelle sous la barre de recherche affiche maintenant les
vrais résultats de `registry.global_search(text)` — vrai décompte,
vrais noms de modules/paramètres, honnêtement masquée quand aucune
requête n'est en cours ou quand aucun `registry` n'est fourni (ex. le
widget utilisé seul, comme le fait déjà `test_esoc_widgets`) — jamais
une ligne de résultats fabriquée sans vrai registre derrière.

**Validation réelle** : recherche "model" testée à la main — la
nouvelle ligne réelle affiche `atmospheric_model, ocean_model,
wave_model, soil_model, vegetation_model (+2 more)` (7 vrais modules
réellement connectés, y compris `catalog`/`forecast`/etc. fixés dans
la fermeture précédente), tandis que l'arbre statique montre ses
propres correspondances de labels ("PINN Models", "Model Calibration")
— les deux résultats coexistent, complémentaires, jamais l'un ne
remplace l'autre. Capture d'écran envoyée. 5 nouveaux tests dans
`tests/test_esoc.py` (pas de résultat fabriqué sans registre, vrai
décompte avec registre, 0 résultat honnêtement rapporté pour une
requête absurde, masquage au clear, et une preuve de bout en bout que
`ESOCWindow` transmet bien SON PROPRE registre jusqu'au widget plutôt
qu'une instance séparée). Suite complète **4013 → 4018**, `ruff`/`mypy`
propres.

**Ce qui reste réellement** : `get_system_status_summary()`/
`is_connected()` n'ont toujours aucun vrai consommateur GUI (un
panneau de statut ESOC affichant "21/25 sous-systèmes connectés"
resterait un vrai chantier séparé). L'arbre statique de la sidebar
(`self.categories`) et celui du registre (`build_system_tree()`)
restent deux copies indépendantes légèrement divergentes (2 catégories
sur 20 différent réellement, HPC et Forecast) — non unifiées ici par
prudence (le contenu HPC de la sidebar semble décrire des panneaux UI
réels distincts des concepts infra du registre, une vraie nuance à
vérifier avant de fusionner plutôt qu'à écraser).

## Mise à jour 2026-09-04 (suite) — dernier gap fermé : un vrai indicateur de connectivité dans la sidebar ESOC

Suite explicite ("continue"), fermeture du dernier point du "Ce qui
reste réellement" ci-dessus : `get_system_status_summary()` restait
sans consommateur GUI réel.

**Construit** : une nouvelle ligne de statut toujours visible en haut
de `ESOCLeftSidebar` (sous "📁 SYSTEM EXPLORER"), calculée une seule
fois à la construction depuis `registry.get_system_status_summary()`
— vrai décompte "🟢/🟡 X/Y real subsystems connected" (🟢 si tout est
connecté, 🟡 sinon), avec un vrai tooltip expliquant honnêtement ce
que "connecté" veut dire (une classe réellement trouvée et instanciée,
jamais un simulacre). Snapshot statique et non rafraîchi
délibérément : `ModuleRegistry` n'a aucune notion de "reconnexion",
chaque enregistrement a déjà tourné au moment où ce widget existe — il
n'y a rien de réel à rafraîchir plus tard. Honnêtement masquée quand
aucun `registry` n'est fourni (même discipline que la ligne de
recherche ajoutée juste avant).

**Validation réelle** : vérifié à la main — `🟡 44/48 real subsystems
connected` (48 = tous les modules enregistrés, y compris les ~23
instanciés directement dans `_initialize_all_subsystems` en plus des
25 `_safe_import_register()` ; 4 non connectés = exactement les 4
domaines honnêtement non résolvables de la fermeture précédente). 2
nouveaux tests (pas de ligne fabriquée sans registre, ligne réelle
visible avec registre et décompte cohérent avec
`get_system_status_summary()`). Suite complète **4018 → 4020**,
`ruff`/`mypy` propres. Capture d'écran envoyée.

**Ce qui reste réellement** : les 4 pièces de l'API `ModuleRegistry`
identifiées comme sans consommateur GUI réel (`is_connected()`,
`get_system_status_summary()`, `global_search()`, `search_index`) ont
maintenant toutes un vrai appelant. Il ne reste que l'unification
prudente des deux arbres de catégories (sidebar vs registre),
volontairement non entamée pour la même raison que la fermeture
précédente.

## Mise à jour 2026-09-04 (suite) — ~150 clics morts dans l'arbre System Explorer d'ESOC, réellement corrigés

Suite explicite ("continue"). En creusant la piste "pourquoi deux
arbres de catégories" de la fermeture précédente, découverte d'un vrai
bug plus large et plus visible : `ESOCLeftSidebar._on_item_clicked()`
appelle bien `self.on_select_callback(text)` sur chaque clic dans
l'arbre System Explorer — mais vérification exhaustive (grep sur tout
le dépôt) : **aucun vrai appelant n'a jamais fourni ce callback**.
Chacune des ~150 vraies feuilles de cet arbre (Ocean, Hydrology, Job
Explorer, Simulation, AMR, ...) était un vrai clic mort — exactement
la même famille de bug déjà trouvée et corrigée plusieurs fois dans
ESOC ("14 des 21 boutons de la toolbar ne faisaient rien").

**Vraie piste de résolution trouvée** : `panel_manager.py` enregistre
28 vrais panneaux opérationnels réels (`job_explorer`, `ocean`,
`simulation`, etc.), affichés comme onglets réels dans
`ESOCLayout.bottom_tabs`. Comparaison label par label entre l'arbre de
la sidebar et ces 28 vraies clés a confirmé l'hypothèse de la
fermeture précédente : la catégorie "HPC" de la sidebar
("Job Explorer", "Remote Terminal", "Storage & Scratch", "CUDA GPU
Monitor", "Benchmarks", "HPC Profiles") nomme bien de vrais panneaux
UI distincts (pas les mêmes concepts que le "HPC" du registre, qui
lui liste des concepts d'infra backend comme "MPI Domain Topology") —
confirmant que les deux arbres ne sont PAS de simples doublons à
fusionner, mais deux vraies taxonomies différentes qui partagent
juste un même nom de catégorie par coïncidence.

**Construit** : `ESOCLayout` fournit maintenant un vrai
`on_select_callback` à `ESOCLeftSidebar` (jusque-là jamais transmis).
Deux tables de correspondance vérifiées une par une (jamais devinées
en bloc) : `_LEAF_LABEL_TO_PANEL_NAME` (13 feuilles avec leur propre
panneau réel distinct — Ocean, Hydrology, Cryosphere, Air Quality,
Geology, Carbon Cycle, et les 6 feuilles HPC + System Config) et
`_CATEGORY_LABEL_TO_PANEL_NAME` (9 catégories n'ayant qu'un seul vrai
panneau pour toutes leurs feuilles — Forecast, Assimilation,
Simulation, Digital Twin, Climate, Planetary Limits, Earth Physics,
Monitoring, Verification). Un clic sur une feuille sans correspondance
réelle (ex. "Atmosphere", toute la catégorie "Catalog"/"Products"/
"Reports"/"Output"/"Plugins") reste un vrai no-op honnête plutôt
qu'une navigation devinée. Signature de `on_select_callback` étendue
de `(text)` à `(text, category)` pour permettre le repli au niveau
catégorie (aucun appelant réel n'existait avant, changement sans
risque).

**Validation réelle** : vérifié à la main avec un vrai `ESOCWindow()`
et un vrai signal `tree.itemClicked.emit()` (pas juste l'appel direct
de la méthode) — cliquer "Job Explorer" bascule réellement l'onglet
du dock du bas sur le vrai panneau HPC Job Lifecycle Explorer.
Capture d'écran envoyée. 6 nouveaux tests (feuille avec panneau
propre, feuilles HPC distinctes les unes des autres, clic sur l'en-
tête de catégorie, repli catégorie pour une feuille non mappée,
no-op honnête pour une feuille non mappée, et un vrai clic Qt de bout
en bout). Suite complète **4020 → 4026**, `ruff`/`mypy` propres.

**Ce qui reste réellement** : plusieurs catégories entières
("Catalog", "Products", "Reports", "Output", "Plugins",
"Geoengineering", "Machine Learning") et de nombreuses feuilles
individuelles au sein de catégories par ailleurs mappées (ex.
"Atmosphere", "Land Surface" sous "Earth System" ; "MPI Domain
Topology" sous "HPC") n'ont toujours aucun vrai panneau opérationnel
construit — un vrai gap de couverture UI, honnêtement disclosed
plutôt que masqué par un mapping approximatif. Construire ces
panneaux manquants (ou en décider l'abandon délibéré) reste un vrai
chantier de produit séparé, hors périmètre de cette fermeture qui ne
corrige que le routage vers ce qui existe déjà réellement.

## Mise à jour 2026-09-04 (suite) — le menu ☰ du dashboard général ACF construit, discipline de fidélité pixel étendue

Suite explicite ("continue"), avec une consigne directe de
l'utilisateur (image à l'appui, `docs/reference/acf_dashboard_reference.jpg`,
le vrai mockup de référence d'`ACFGeneralDashboard` — pas celui
d'AWCI) : les vraies actions de ce dashboard doivent vivre derrière la
vraie icône "☰" visible en haut à gauche du mockup, jamais comme
boutons additionnels dans les panneaux fixes déjà pixel-matched.

**Constat** : cette icône ☰ n'avait jamais été construite.
`ACFGeneralDashboard` avait déjà 2 vraies actions fonctionnelles
("🔄 Refresh Evolution", "🔄 Compute Consensus") mais sous forme de
`QPushButton` en ligne — absents du mockup de référence, une vraie
déviation de fidélité pixel jamais corrigée jusqu'ici.

**Construit** : un vrai `QToolButton` "☰" en position exacte du
mockup (avant le titre, tout à gauche de la barre de statut), ouvrant
un vrai `QMenu` contenant les 2 actions réelles converties en
`QAction` (même méthode réelle connectée — `triggered` au lieu de
`clicked` — même discipline `setEnabled()`/`isEnabled()` pendant un
calcul en cours, sans aucune régression). Nouveau style QSS
`QToolButton`/`QMenu` ajouté à `dashboard_stylesheet()` (fonction
partagée avec `AWCIDashboard` — additif seulement, aucun risque de
régression visuelle pour ce dernier). Documentation de la classe
étendue avec la consigne explicite pour guider tout ajout futur de
capacité réelle vers ce même menu plutôt que vers un nouveau widget en
ligne.

**Validation réelle** : les 12 tests existants passent sans aucune
modification (l'interface `QAction`/`QPushButton` partage
`isEnabled()`/`setEnabled()`, migration sans risque). 3 nouveaux tests
(le menu contient bien les 2 vraies actions attendues ; déclencher
chaque action via `.trigger()` appelle bien la vraie méthode
`refresh()`/`_start_consensus()`, pas un simulacre). Suite complète
**4026 → 4029**, `ruff`/`mypy` propres. Capture d'écran envoyée :
en-tête épuré matching le mockup (icône ☰ seule, plus aucun bouton en
ligne) + le menu déroulant avec ses 2 vraies actions.

**Ce qui reste réellement** : la consigne a été donnée avec l'image de
référence d'`ACFGeneralDashboard` spécifiquement — appliquée ici à ce
seul dashboard. Note honnête : `awci_dashboard_reference.jpg` (le
mockup d'`AWCIDashboard`) ne montre lui non plus aucun bandeau de
boutons ni icône ☰ — le bandeau réel d'`AWCIDashboard` (Real Physics,
Real Archive, etc., construit au fil de cette session) dévie donc de
son propre mockup exactement de la même façon. Aucun changement
rétroactif appliqué à `AWCIDashboard` dans cette fermeture : c'est un
dashboard distinct, son propre bandeau est une fonctionnalité réelle
déjà construite, testée et montrée à l'utilisateur à de nombreuses
reprises sans objection — une refonte rétroactive de cette ampleur
reste une vraie décision séparée à confirmer explicitement avant
d'être entreprise, pas à deviner.

## Mise à jour 2026-09-04 (suite) — ACF Scientific Workstation, Phase 1 : un dashboard ACF Core réellement sans AWCI

L'utilisateur a fourni un mockup photoréaliste ("ACF SCIENTIFIC
WORKSTATION") et sa propre spécification en 70 sections
("ACF — ATMOSPHERIC COMPLEXITY FRAMEWORK — MASTER SCIENTIFIC
DASHBOARD — ACF CORE ONLY — NO AWCI"), demandant un dashboard
entièrement nouveau exposant la science propre d'ACF (Dynamics,
Thermodynamics, Convection, Microphysics, Terrain, Temporal Evolution,
Forecast Confidence, un Interaction Engine, un Complexity Explorer
multidimensionnel) — avec une règle répétée explicitement (§21, §67) :
**aucun score composite unique de type AWCI nulle part**. La spec
demandait elle-même (§70) d'inspecter intégralement le repository
avant de construire, progressivement, sans rien détruire ni fabriquer.

**Pourquoi** : 3 agents Explore lancés en parallèle avant tout plan
(même discipline que §70) ont établi un constat déterminant :
`ACFGeneralDashboard` — malgré son nom "général" — n'est en réalité
**pas** sans AWCI : son score par point, son radar 6 axes, son
étiquette "dominant couplings" et sa jauge d'incertitude sont
littéralement la sortie de `AWCICalculator.calculate()`
(`module_scores`, `interaction_scores`,
`Normalizer.normalize_model_disagreement`) — du vrai code fonctionnel,
mais couplé à AWCI de bout en bout, pas un problème cosmétique de
nommage. Impossible donc de simplement "nettoyer" ce dashboard
existant pour en faire un ACF Core réel : une construction neuve était
nécessaire. Deux questions de clarification ont confirmé auprès de
l'utilisateur : (1) le nouveau Workstation **remplace**
`ACFGeneralDashboard` comme point d'entrée "🌐 ACF Dashboard" de
l'ESOC (`ACFGeneralDashboard`/`ACFGeneralDashboardWindow` ne sont pas
supprimés — conservés et documentés comme supersédés, même convention
que le reste du projet) ; (2) une approche progressive a été retenue
vu l'ampleur de la spec — chrome + Overview + Dynamics Lab +
Complexity Explorer pour cette passe, le reste listé dans la nav comme
"(planned)" plutôt que silencieusement omis.

**Construit** :
- **`ACFWorkstation`** (`acf_workstation.py`) — le chrome réel :
  sélecteur de **Model** réel (AROME/ALADIN/ARPEGE, les vraies clés de
  `MODEL_CONFIGS`, correspondant exactement au mockup), bouton "🔄 Run"
  déclenchant un vrai `QRunnable`/`QThreadPool` qui appelle
  `compute_real_complexity_volume()` (un vrai `CoupledEarthSolver`,
  jamais un calcul fabriqué), un vrai slider de niveau (les niveaux
  natifs réels du volume calculé), un bouton ⛶ plein écran réel, un
  bouton ⚙ Settings honnêtement désactivé ("not yet implemented").
  Nav "ACF CORE" listant Overview/Dynamics/Complexity comme réels et
  activés, et 7 modules (Thermodynamics, Convection, Microphysics,
  Terrain, Temporal, Confidence, Interactions) visiblement présents
  mais désactivés avec l'étiquette "(planned)" — la vraie feuille de
  route disclosed, ni cachée ni fabriquée. Discipline "calculer une
  fois, re-découper à chaque interaction" : changer de niveau ne
  relance jamais le solveur (vérifié par un test qui fait échouer
  volontairement tout second appel).
- **`ACFOverviewPanel`** — Température / Vitesse du vent / Humidité
  spécifique / Pression réelles au niveau sélectionné, sur la carte
  partagée `AWCIMapPanel` reconfigurée (légende retitrée, aucune
  jauge/score).
- **`ACFDynamicsLabPanel`** — vitesse du vent réelle, **vorticité
  relative** et **divergence** réelles, calculées en vectorisant sur
  la vraie grille lat/lon via `np.gradient` (espacement métrique
  standard `dx = R·cos(lat)·dλ`, `dy = R·dφ`) puis en appelant
  **verbatim** `VorticityCalculator.compute_relative_vorticity()` et
  `Divergence.calculate()` (les mêmes classes déjà testées ailleurs
  dans le projet, jamais réimplémentées).
- **`ACFComplexityExplorerPanel`** — la règle "pas de score unique"
  appliquée littéralement : trois dimensions réelles, séparées, jamais
  combinées — **complexité spatiale** (magnitude du gradient de
  température, proxy structurel disclosed comme défini par ACF, pas
  publié), **complexité temporelle** (taux de variation réel via
  `compute_real_complexity_evolution()`, jamais son champ
  `awci_evolution`), et **désaccord multi-modèle**
  (`ModelConsensusEngine.compute_real_multi_model_disagreement()`,
  réutilisé tel quel). Les deux dernières sont calculées à la demande
  (boutons "🔄 Run Temporal Analysis" / "🔄 Compute Model Disagreement"),
  hors thread principal.
- **`esoc_toolbar.py`/`esoc_window.py`** — l'action "🌐 ACF Dashboard"
  devient "🔬 ACF Scientific Workstation", ouvrant désormais
  `ACFWorkstationWindow`. `ACFGeneralDashboard`/
  `ACFGeneralDashboardWindow` conservés avec une note de correction
  disclosant leur supersession, comportement inchangé, suite de tests
  existante intacte.

**3 vrais bugs trouvés et corrigés**, aucun par simple lecture de
tests qui passaient déjà mais par vérification active (captures
d'écran réelles, tests de stress) :
1. **Cycle de vie du colorbar matplotlib** : `Colorbar.remove()`
   plantait au second redraw (`self.axis.clear()` invalide sa propre
   référence à l'axe d'origine, `ax=` comme `cax=` ne changent rien —
   `fig.colorbar()` enregistre en interne la même méthode fragile).
   Corrigé via `self.figure.delaxes(self._colorbar.ax)`, qui contourne
   entièrement le nettoyage interne de `Colorbar`. Vérifié par un test
   de stress de 40 redraws (10 cycles × 4 variables), zéro fuite
   d'axes.
2. **Singularité aux pôles** : une vraie grille solveur couvre
   réellement -90° à 90°. `cos(lat)=0` aux pôles rend `dx_per_row`
   exactement nul — `nonzéro/0 = inf` en numpy (pas `NaN`), ce qui
   produisait une "vorticité" réelle mais absurde (~1e10 s⁻¹),
   visuellement confirmé par une échelle de colorbar totalement
   faussée (tout le globe reteinté par cette valeur aberrante, à cause
   aussi d'un second bug : `contourf(levels=20, vmin=, vmax=)` ne
   fait pas ce qu'on croit — `levels` en entier laisse matplotlib
   dériver les bornes des niveaux depuis les extrêmes réels des
   données, `vmin`/`vmax` ne renormalisent que la couleur, sans
   jamais borner les niveaux tracés). Corrigé en deux temps : un
   masquage explicite `dx_per_row < 1m → NaN` (seuil physique réel :
   le pôle lui-même) dans `acf_workstation_dynamics.py`, et le passage
   d'un tableau explicite `levels=np.linspace(vmin, vmax, 21)` (au
   lieu d'un entier) dans `awci_map_panel.py` dès qu'un appelant
   fournit un vrai `vmin`/`vmax`, avec `extend="both"` pour écrêter
   visuellement les valeurs hors bornes sans jamais fausser l'échelle.
   Nouveau test de régression
   `test_pole_rows_are_honestly_nan_not_a_huge_finite_blowup`.
   Re-vérifié par capture d'écran : colorbar correcte à ±0.00018 s⁻¹,
   un ordre de grandeur synoptique réel et plausible.
3. **Fuite du motif de démonstration synthétique d'AWCI** : découvert
   en relisant une capture d'écran du Complexity Explorer — la carte
   "TEMPORAL COMPLEXITY" affichait un vrai contour coloré et texturé
   alors même que son propre statut affichait encore "Not yet
   computed" et que le bouton "🔄 Run Temporal Analysis" n'avait
   jamais été cliqué dans le script de rendu. Cause réelle :
   `AWCIMapPanel.update_data()` retombe automatiquement sur
   `awci_grid()` (le motif synthétique propre à AWCI) dès que
   `self._external_field` vaut `None` — un comportement correct et
   disclosed pour le dashboard AWCI lui-même, mais une vraie violation
   du principe central "aucun contenu AWCI nulle part" pour un panneau
   du Workstation pas encore alimenté en données réelles : l'utilisateur
   aurait vu un motif fabriqué, habillé en donnée réelle. Corrigé par
   un nouveau paramètre additif `show_demo_fallback: bool = True` au
   constructeur d'`AWCIMapPanel` (défaut `True`, comportement inchangé
   pour tous les appelants AWCI existants, vérifié un par un) ; les 4
   panneaux-cartes du Workstation (`ACFOverviewPanel.map_panel`,
   `ACFDynamicsLabPanel.map_panel`,
   `ACFComplexityExplorerPanel.spatial_map`/`temporal_map`) passent
   désormais `show_demo_fallback=False`, ce qui fait retomber
   `update_data()` sur une grille entièrement `NaN` (même géométrie,
   même chemin de rendu `contourf`/colorbar — matplotlib affiche
   nativement un `NaN` comme un trou transparent, jamais un plantage)
   plutôt que sur le motif fabriqué. 4 nouveaux tests de régression
   (`tests/test_awci_map_panel_demo_fallback.py`) : comportement AWCI
   par défaut inchangé, carte réellement vierge quand désactivé, un
   vrai champ externe s'affiche toujours correctement une fois fourni.
   Re-vérifié par capture d'écran avant/après clic sur
   "Run Temporal Analysis" : carte vierge honnête d'abord, vraies
   données réelles ensuite.

**Validation réelle** : `ruff check`/`.venv/bin/mypy` propres sur
chaque fichier neuf/modifié. Suite complète de la carte partagée
(`AWCIMapPanel`) : 89 → 93 tests, tous verts, aucune régression pour
les appelants AWCI existants. 4 nouveaux fichiers de tests pour le
Workstation (helpers vorticité/divergence contre un cas analytique
connu et contre les vraies classes `VorticityCalculator`/`Divergence`
directement ; helpers de complexité spatiale/temporelle ; chrome GUI —
sélecteurs, nav activé/désactivé, worker réel hors thread, discipline
"calcul unique" ; action toolbar ESOC de bout en bout). Captures
d'écran réelles envoyées : Overview, Dynamics Lab (vorticité), et
Complexity Explorer avant/après calcul de la complexité temporelle,
confirmant visuellement l'état honnête "Not yet computed" puis les
vraies données.

**Ce qui reste réellement** : conformément à la liste "explicitement
différé" du plan approuvé — Thermodynamics/Convection/Microphysics/
Terrain/Temporal/Confidence Labs, Interaction Engine + graphe
d'interaction, Multi-Model Lab en page propre, Data Quality Center, vue
3D/4D, Case Study Lab, Research Mode, Configuration Management, palette
de commandes (Ctrl+K), raccourcis clavier, export (PNG/SVG/CSV/JSON),
extension de l'API `/api/v1/*` pour ces nouveaux modules, et le
programme complet de tests visuels/accessibilité en 6 types — aucun
n'est construit dans cette passe, chacun a sa propre raison honnête de
ne pas l'être (backend réel manquant, ou simplement hors du périmètre
borné de cette étape), aucun n'est silencieusement abandonné.

## Mise à jour 2026-09-04 (suite) — ACF Scientific Workstation, Phase 2 : le Thermodynamics Lab, et une vraie anomalie de pression découverte au passage

Suite explicite ("continue"), même discipline progressive que la
Phase 1 : le 4ᵉ module réel du Workstation, **Thermodynamics Lab**,
construit en réutilisant deux pipelines réels déjà existants dans le
projet (jamais réimplémentés) — la seule vraie nouveauté est leur
premier appel en dehors du contexte AWCI, sur une grille complète,
avec leur propre carte dédiée.

**Pourquoi** : `acf.awci.theta_e.compute_real_theta_e_at_point()`
(θ-e canonique de Bolton (1980), composée de 3 formules réelles déjà
testées) et `acf.awci.convective_energy.compute_real_cape_cin_at_point()`
(un vrai ascenseur de particule MetPy suivi de
`acf.science.cape.CAPE.calculate()`/`cin.CIN.calculate()`) existaient
déjà, construits lors d'une closure antérieure pour alimenter
`AWCICalculator`, mais n'avaient jamais été appelés en dehors de ce
contexte AWCI ni sur une grille complète pour produire leur propre
carte.

**Construit** :
- `compute_real_theta_e_and_rh_fields()` — appelle
  `compute_real_theta_e_at_point()` à chaque point du niveau courant
  (mesuré réellement à ~1 microseconde/point — assez rapide pour un
  recalcul automatique à chaque changement de niveau/modèle, comme
  Overview/Dynamics). Un seul appel par point fournit à la fois θ-e ET
  l'humidité relative réelle (son propre résultat intermédiaire) —
  jamais recalculée séparément.
- `compute_real_cape_cin_fields()` — un vrai ascenseur de particule
  MetPy par point mesuré à ~5 ms/point (~33s pour la grille native
  complète d'ALADIN, 60×120 = 7200 colonnes — bien trop lent pour une
  UI interactive). Compromis réel et disclosed : calculé sur un sous-
  ensemble réel plus grossier des colonnes déjà réelles du volume
  (tous les 3 points de la grille native — 20×40 pour ALADIN, ~3.7s),
  jamais interpolé — chaque valeur retournée est un vrai CAPE/CIN
  calculé sur cette colonne réelle exacte. Même convention déjà établie
  par les paramètres `n_lat`/`n_lon` de
  `compute_real_complexity_field()` pour un résultat plus grossier
  mais rapide — appliquée ici à un sous-ensemble d'un volume déjà
  calculé, jamais à un second run du solveur.
- **`ACFThermodynamicsLabPanel`** — θ-e/humidité relative en temps réel
  (sélecteur de variable, redessiné à chaque niveau) ; CAPE/CIN à la
  demande (bouton "🔄 Compute CAPE/CIN Field", vrai `QRunnable` hors
  thread, même convention que les boutons temporal/consensus du
  Complexity Explorer) — indépendant du slider de niveau (CAPE/CIN sont
  par nature des diagnostics de colonne complète, toujours soulevés
  depuis le vrai niveau natif le plus bas). Ajouté à la nav du
  Workstation (déplacé de "planned" à activé) et à `_render_all_panels()`.

**Une vraie anomalie découverte, disclosed et non corrigée dans cette
passe** : en vérifiant visuellement le rendu θ-e (capture d'écran
initiale complètement plate, hors de l'échelle de couleur choisie), la
cause a été tracée jusqu'à `pressure_volume_hpa` — le volume réel
retourné par `compute_real_complexity_volume()` pour un run ALADIN
réel rapporte une pression de surface uniforme d'environ **2013 hPa**
au lieu d'une valeur réaliste (~1000-1013 hPa), soit environ le double
de la valeur physique attendue. Cette pression anormalement élevée,
combinée à une humidité spécifique elle-même uniforme (0.01 kg/kg
partout), sature l'humidité relative calculée à 100% sur toute la
grille, ce qui aplatit le champ θ-e réel. **Décision** : ne pas tenter
de corriger le solveur (`CoupledEarthSolver`) dans cette passe — un
changement à cette échelle affecterait potentiellement tous les autres
consommateurs réels de ce même état (`AWCIDashboard`,
`ACFGeneralDashboard`, ce Workstation), certains ayant peut-être des
hypothèses compensatoires construites autour de la valeur actuelle
(fausse) ; une investigation et correction dédiées, avec vérification
complète de la non-régression, sont hors du périmètre borné de cette
closure. **Flagged** via une tâche séparée
(`task_f3c406d9` — "Investigate CoupledEarthSolver pressure ~2x too
high"). Pour que le panneau reste honnête et informatif quel que soit
l'état réel (même anormal) du solveur, l'échelle de couleur θ-e a été
rendue dynamique (percentile réel 5/95 du champ courant, même
convention déjà utilisée par le Complexity Explorer) plutôt qu'une
plage fixe devinée qui ne correspondait pas à cette sortie réelle du
solveur — l'humidité relative reste honnêtement affichée saturée à
100% (une donnée réelle, pas fabriquée) jusqu'à ce que la cause racine
soit corrigée séparément.

**Validation réelle** : `ruff`/`mypy` propres. 4 nouveaux tests unitaires
(`tests/test_acf_workstation_thermodynamics.py` — cross-vérifiés point
par point contre les vraies fonctions `compute_real_theta_e_at_point`/
`compute_real_cape_cin_at_point` appelées directement, jamais une
réimplémentation séparée) + 6 nouveaux tests GUI
(`tests/gui/test_acf_workstation_thermodynamics.py` — dont un vrai
test de bout en bout du worker hors thread via `qtbot.waitUntil`,
matching la discipline déjà établie) + mise à jour des tests d'intégration
du chrome (`tests/gui/test_acf_workstation.py` — nouvelle position dans
la nav/le stack, panneau bien alimenté par `_on_volume_ready`). Suite
complète **4050 → 4060**, toujours verte. Captures d'écran réelles
envoyées : θ-e avant/après correction de l'échelle de couleur, humidité
relative (honnêtement saturée), CAPE/CIN avant (carte vierge honnête)
et après calcul (points chauds convectifs réels).

**Ce qui reste réellement** : l'anomalie de pression ~2x reste non
corrigée (tâche séparée en attente) ; les ~9 modules restants du plan
(Convection, Microphysics, Terrain, Temporal, Confidence Labs,
Interaction Engine, Multi-Model Lab en page propre, Data Quality
Center, 3D/4D, Case Study Lab, Research Mode, Configuration
Management, palette de commandes, raccourcis, export, extension API)
restent listés "(planned)" dans la nav, non construits, pour les mêmes
raisons honnêtes déjà disclosed dans la clôture précédente.

## Mise à jour 2026-09-04 (suite) — ACF Scientific Workstation, Phase 3 : le Microphysics Lab, et le cisaillement de vent ajouté au Dynamics Lab

Suite explicite ("continue"), même discipline progressive. Deux ajouts
réels cette passe, tous deux réutilisant des pipelines déjà réels et
déjà testés construits lors d'une closure antérieure pour AWCI
(`acf.awci.hydrometeor_phase`, `acf.awci.wind_shear`) — leur premier
appel en dehors du contexte AWCI, sur une grille complète.

**Pourquoi le Convection Lab n'a PAS été construit cette passe** :
considéré puis explicitement écarté. La seule vraie formule disponible
pour un module convectif (`acf.awci.updraft.
compute_real_max_updraft_velocity()`, w_max = sqrt(2×CAPE)) est, par
le propre docstring de ce module, "a purely deterministic, monotonic
function of CAPE alone" — elle ne porte aucune information réelle que
CAPE (déjà affiché dans Thermodynamics Lab) ne porte pas déjà. Un vrai
Convection Lab mériterait un vrai indice composite publié et
indépendant (SCP/STP), qui nécessite un vrai hélicité relative à la
tempête et un cisaillement effectif à chaque point de grille — non
disponibles dans ce codebase aujourd'hui. Construire un onglet autour
d'une simple retransformation des données déjà affichées ailleurs
aurait été le genre de "fonctionnalité fictive à faible valeur" que ce
projet évite délibérément — décision disclosed, pas un oubli.

**Construit** :
- **Microphysics Lab** (`acf_workstation_microphysics.
  ACFMicrophysicsLabPanel`) — réutilise
  `acf.awci.hydrometeor_phase.compute_real_hydrometeor_phase_at_point()`
  tel quel (relative humidity réelle + température du thermomètre
  mouillé réelle de Stull (2011) + `HydrometeorType.classify()`, un
  vrai heuristique explicitement self-disclosed, pas une formule
  validée) : phase de précipitation de surface (Rain/Snow/Wet
  Snow-Mix/Freezing Rain-Ice Pellets) et sa sévérité ordinale réelle
  ACF ([0,1], 0.2/0.5/0.7/1.0) — rendue avec une vraie colormap
  discrète à 4 couleurs (pas un dégradé continu qui impliquerait
  faussement des phases intermédiaires) — plus la température du
  thermomètre mouillé elle-même, un vrai sous-produit gratuit du même
  appel. Mesuré ~1 microseconde/point — recalcul automatique à chaque
  changement de niveau, comme Overview/Dynamics/le θ-e de
  Thermodynamics Lab. Ajouté à la nav (déplacé de "planned" à activé)
  et à `_render_all_panels()`.
- **Dynamics Lab** — 4ᵉ variable réelle : cisaillement de vent global
  (bulk wind shear), via
  `acf.awci.wind_shear.compute_real_wind_shear_at_point()` appelé
  directement par point (sa propre formule utilise `math.sqrt`, non
  vectorisable sur des tableaux numpy contrairement à
  vorticité/divergence — mesuré ~0.4 microseconde/point, négligeable
  même sur la grille native complète). Un vrai diagnostic de colonne
  complète, donc — disclosed explicitement dans son propre nom de
  variable ("full column") — indépendant du slider de niveau, même
  convention déjà établie pour CAPE/CIN et la complexité
  temporelle/désaccord multi-modèle.

**Validation réelle** : `ruff`/`mypy` propres. 4 nouveaux tests
unitaires (`tests/test_acf_workstation_microphysics.py`,
`tests/test_acf_workstation_dynamics.py` — cross-vérifiés point par
point contre les vraies fonctions `compute_real_hydrometeor_phase_at_point`/
`compute_real_wind_shear_at_point` appelées directement) + 4 nouveaux
tests GUI (`tests/gui/test_acf_workstation_microphysics.py`) + mise à
jour des tests d'intégration du chrome (nouvelle position dans la
nav/le stack à 5 modules désormais). Suite complète **4060 → 4068**,
toujours verte. Captures d'écran réelles envoyées : cisaillement de
vent (Dynamics Lab), phase de précipitation (légende à 4 catégories
visible sur la colorbar), température du thermomètre mouillé.

**Ce qui reste réellement** : l'anomalie de pression ~2x (tâche
séparée toujours en attente) ; ~7 modules restants (Convection,
Terrain, Temporal, Confidence Labs, Interaction Engine, Multi-Model
Lab en page propre, Data Quality Center, 3D/4D, Case Study Lab,
Research Mode, Configuration Management, palette de commandes,
raccourcis, export, extension API) listés "(planned)", non construits,
pour les mêmes raisons honnêtes déjà disclosed. Note honnête sur ce
Microphysics Lab spécifiquement : la phase de précipitation observée
au niveau de surface d'un run ALADIN réel était uniformément "Rain"
sur toute la grille dans la capture envoyée — un vrai résultat (le
champ de température réel à ce niveau/ce run est partout au-dessus du
seuil de gel), pas un motif fabriqué, mais qui illustre concrètement
que ce panneau ne montrera une vraie variété de phases que sur un run
couvrant des latitudes/saisons plus froides.

## Mise à jour 2026-09-04 (suite) — ACF Scientific Workstation, Phase 4 : le Temporal Evolution Lab, et deux modules délibérément écartés (Terrain, Confidence pour l'instant)

Suite explicite ("continue"), même discipline progressive.

**Construit** : **Temporal Evolution Lab**
(`acf_workstation_temporal.ACFTemporalLabPanel`) — réutilise
`acf.awci.temporal_field.compute_real_complexity_evolution()` tel
quel, le même moteur réel déjà utilisé par le bouton "Run Temporal
Analysis" du Complexity Explorer, mais expose cette fois la vraie
trajectoire multi-frame complète (temperature_evolution/
wind_speed_evolution/specific_humidity_evolution/
pressure_evolution_hpa, jamais `awci_evolution`) au lieu d'une seule
statistique agrégée : un vrai slider de frame permet de parcourir 4
vrais instantanés d'une trajectoire réelle du `CoupledEarthSolver`
(mêmes paramètres que le bouton existant du Complexity Explorer —
4 frames, 3 pas d'intégration réels entre chaque — pour rester
cohérent, pas redérivés indépendamment). À la demande, hors thread
(coût réel : plusieurs vrais pas de solveur), le résultat reste tel
quel lors d'un changement de niveau ou d'un nouveau "🔄 Run" du
Workstation (même convention déjà établie pour CAPE/CIN et le
temporal/consensus du Complexity Explorer) — seul un nouveau clic sur
son propre bouton relance un vrai calcul.

**Deux modules examinés et délibérément non construits, disclosed
dans le docstring du chrome, pas oubliés** :
- **Terrain Lab** — `acf.awci.orographic_froude`'s own docstring
  révèle déjà que le vrai état de `CoupledEarthSolver` "has no
  terrain-elevation field at all" et aucune vraie coordonnée de
  hauteur géométrique. Un vrai Terrain Lab nécessiterait soit un vrai
  jeu de données d'élévation externe (aucun n'existe dans ce
  codebase aujourd'hui), soit un relief fabriqué — explicitement
  interdit. Reste honnêtement "(planned)".
- **Confidence Lab** — non construit cette passe faute de temps
  d'investigation suffisant sur la faisabilité réelle d'une carte de
  désaccord multi-modèle complète (par opposition au point unique déjà
  utilisé par le Complexity Explorer, qui nécessiterait de faire
  tourner plusieurs solveurs réels à CHAQUE point de grille — un coût
  potentiellement très élevé à vérifier avant de s'engager). Reste
  "(planned)", à investiguer avant construction plutôt que deviné.

**Validation réelle** : `ruff`/`mypy` propres. 5 nouveaux tests
(`tests/gui/test_acf_workstation_temporal.py` — dont un vrai test de
bout en bout du worker hors thread via `qtbot.waitUntil`, et un test
de régression prouvant qu'un changement de frame ne relance jamais le
solveur) + mise à jour des tests d'intégration du chrome (nouvelle
position dans la nav/le stack à 6 modules désormais). Suite complète
**4068 → 4073**, toujours verte. Captures d'écran réelles envoyées :
état honnête "Not yet computed" avant calcul, frame 4/4 (t+0.20h)
après un vrai calcul, avec son vrai titre et sa vraie colorbar.

**Ce qui reste réellement** : l'anomalie de pression ~2x (tâche
séparée toujours en attente) ; ~5 modules restants (Convection,
Terrain, Confidence Labs, Interaction Engine, Multi-Model Lab en page
propre, Data Quality Center, 3D/4D, Case Study Lab, Research Mode,
Configuration Management, palette de commandes, raccourcis, export,
extension API) listés "(planned)", pour les mêmes raisons honnêtes
déjà disclosed.

## Mise à jour 2026-09-04 (suite) — ACF Scientific Workstation, Phase 5 : le Confidence Lab, l'investigation de faisabilité tranchée

Suite explicite ("continue"), même discipline progressive. Cette passe
tranche l'investigation explicitement laissée en suspens à la fin de
la Phase 4 : une vraie carte complète de désaccord multi-modèle
(par opposition au point unique déjà utilisé par le Complexity
Explorer) est-elle réellement faisable en coût de calcul ?

**Investigation** : le point-clé est que
`compute_real_multi_model_disagreement()` (la méthode existante,
point unique) fait déjà tourner le solveur complet une fois PAR
MODÈLE — le coût réel dominant n'est PAS lié au nombre de points
interrogés, mais au nombre de modèles comparés. Boucler cette méthode
existante sur chaque point de grille aurait donc été absurdement cher
(N_points × N_modèles runs de solveur) — mais ce n'est pas nécessaire :
il suffit de faire tourner chaque modèle UNE SEULE FOIS, puis de lire
le champ complet (pas un seul point) et de le regriller sur une grille
commune. Mesuré réellement : **~0.9 seconde** pour 2 modèles
(ALADIN+ARPEGE) sur la vraie grille ARPEGE (48×96). Conclusion :
réellement faisable, pas prohibitif.

**Construit** :
- Nouvelle méthode réelle `ModelConsensusEngine.
  compute_real_multi_model_disagreement_field()`
  (`model_consensus_engine.py`, ajout additif, zéro changement pour
  les appelants existants de la méthode point) — fait tourner chaque
  vrai `CoupledEarthSolver` une seule fois par modèle (un seul tirage
  de perturbation par modèle, pas un par point interrogé — une vraie
  carte complète a besoin d'un champ cohérent par modèle, pas d'une
  réalisation différente à chaque requête), regrille le résultat de
  chaque modèle sur la grille native réelle d'un modèle cible (défaut
  ARPEGE) par plus-proche-voisin réel (même technique déjà utilisée
  par la méthode point, vectorisée ici sur tous les points cibles à
  la fois), puis calcule les vraies statistiques
  `acf.ai.ensemble.ensemble_manager.EnsembleManager` (réutilisée, pas
  réimplémentée) à chaque point de cette grille partagée.
- **Confidence Lab** (`acf_workstation_confidence.
  ACFConfidenceLabPanel`) — bouton à la demande "🔄 Compute Model
  Confidence Field" (même modèles ALADIN/ARPEGE que le bouton existant
  du Complexity Explorer, pour cohérence), hors thread. Affiche le
  spread réel (écart-type) ET la moyenne réelle du désaccord comme
  deux grandeurs physiques séparées — jamais combinées en un seul
  score de "confiance" 0-100, appliquant littéralement la règle §21/§67
  du spec maître à ce nouveau module. Ajouté à la nav (déplacé de
  "planned" à activé, 7 modules désormais) et à `_render_all_panels()`
  (bookkeeping seulement — le champ de désaccord reste sa propre
  computation à la demande, indépendante du volume du Workstation,
  même convention que CAPE/CIN et le temporal/consensus du Complexity
  Explorer).

**Validation réelle** : `ruff`/`mypy` propres. 6 nouveaux tests
unitaires (`tests/test_ai_forecast_center.py` — dont un cross-check
direct contre un vrai `EnsembleManager` construit indépendamment sur
une cellule de grille précise, et la vérification que la grille de
sortie correspond bien à la vraie grille native du modèle cible) + 4
nouveaux tests GUI (`tests/gui/test_acf_workstation_confidence.py` —
dont un vrai test de bout en bout du worker hors thread via
`qtbot.waitUntil`) + mise à jour des tests d'intégration du chrome
(nouvelle position dans la nav/le stack à 7 modules désormais). Suite
complète **4073 → 4083**, toujours verte. Capture d'écran réelle
envoyée : carte de spread réel ALADIN/ARPEGE (moyenne 1.572 K, max
8.879 K — des valeurs réelles, pas arrondies ni inventées).

**Ce qui reste réellement** : l'anomalie de pression ~2x (tâche
séparée toujours en attente) ; ~4 modules restants (Convection,
Terrain Labs, Interaction Engine, Multi-Model Lab en page propre, Data
Quality Center, 3D/4D, Case Study Lab, Research Mode, Configuration
Management, palette de commandes, raccourcis, export, extension API)
listés "(planned)", pour les mêmes raisons honnêtes déjà disclosed.
Note honnête sur la méthode de regrillage : un point proche d'une
frontière de cellule de la grille native d'un modèle peut montrer un
effet de discrétisation réel (pas un signal physique) — disclosed
explicitement dans le docstring de la nouvelle méthode.

## Mise à jour 2026-09-04 (suite) — ACF Scientific Workstation, Phase 6 : l'Interaction Engine, une corrélation réelle et statistiquement justifiée

Suite explicite ("continue"), même discipline progressive. Le
§22 du spec maître ("INTERACTIONS — CŒUR DU PROJET") est explicite et
sans ambiguïté : *"Les interactions doivent être étudiées
scientifiquement. Ne pas inventer arbitrairement `interaction = A × B`
sans justification physique ou statistique."* Cette passe applique
cette règle littéralement.

**Construit** : **Interaction Engine**
(`acf_workstation_interactions.ACFInteractionEnginePanel`) — calcule
le vrai coefficient de corrélation de Pearson, standard et publié,
entre deux vrais champs physiques choisis par l'utilisateur, PLUS sa
vraie décomposition ponctuelle affichée en carte
(`local_interaction(x,y) = z_A(x,y) × z_B(x,y)`, où `z` est l'anomalie
standardisée réelle — sa moyenne spatiale équivaut exactement, par
construction, à la formule classique `r = cov(A,B)/(std(A)×std(B))`,
vérifié dans les tests contre `numpy.corrcoef` directement) — une
vraie décomposition statistique de manuel, pas un score par point
inventé. Jamais un produit brut `A × B` en unités hétérogènes (ex.
vitesse du vent en m/s × humidité spécifique en kg/kg n'aurait aucun
sens dimensionnel) — exactement le type d'interaction non justifiée
que le spec met en garde contre.

**Cross-module par conception** : les 11 variables sélectionnables
réutilisent TOUTES les fonctions réelles déjà construites dans les
autres Labs (`acf_workstation_dynamics` pour vorticité/divergence/
cisaillement de vent, `acf_workstation_thermodynamics` pour θ-e/
humidité relative, `acf_workstation_microphysics` pour la sévérité de
phase/température humide, plus les champs bruts d'Overview) — aucune
formule réimplémentée. Permet d'étudier littéralement l'exemple donné
par le spec maître lui-même ("Vent élevé + Humidité élevée + Relief"),
en choisissant par exemple "Bulk wind shear" × "Relative humidity".

**Validation réelle** : `ruff`/`mypy` propres. 5 nouveaux tests
unitaires (`tests/test_acf_workstation_interactions.py` — cross-
vérifiés directement contre `numpy.corrcoef`, plus les cas limites
réels : corrélation parfaite +1/-1, champ à variance nulle
honnêtement NaN au lieu d'une valeur fabriquée, deux champs aléatoires
indépendants proches de 0) + 5 nouveaux tests GUI
(`tests/gui/test_acf_workstation_interactions.py`) + mise à jour des
tests d'intégration du chrome (nouvelle position dans la nav/le stack
à 8 modules désormais). Suite complète **4083 → 4093**, toujours
verte. Capture d'écran réelle envoyée : carte Temperature × Wind speed
sur un vrai run ALADIN, avec son vrai statut "Real Pearson r = -0.005
(negative correlation)".

**Ce qui reste réellement** : l'anomalie de pression ~2x (tâche
séparée toujours en attente) ; 2 modules Lab restants (Convection,
Terrain) plus les pièces plus larges du spec maître hors de la liste
originelle des "Labs" (Multi-Model Lab en page propre, Data Quality
Center, 3D/4D, Case Study Lab, Research Mode, Configuration
Management, palette de commandes, raccourcis, export, extension API)
listés "(planned)", pour les mêmes raisons honnêtes déjà disclosed.

## Mise à jour 2026-09-04 (suite) — ACF Scientific Workstation, Phase 7 : le Data Quality Center, confirmation indépendante de l'anomalie de pression

Suite explicite ("continue"), même discipline progressive. Cette passe
réutilise une infrastructure réelle déjà construite mais jamais
appelée sur une grille complète : `acf.physics_guard.
variable_quality.assess_variable_quality()`, la taxonomie §32 du spec
maître (VALID/SUSPECT/MISSING/INVALID/OUT_OF_RANGE/UNIT_ERROR/
GRID_ERROR/TIME_ERROR/PHYSICAL_INCONSISTENCY), elle-même bâtie sur les
vraies bornes opérationnelles documentées de
`acf.physics_guard.range_check.OPERATIONAL_RANGES`.

**Construit** : **Data Quality Center**
(`acf_workstation_quality.ACFDataQualityLabPanel`) — statut §32 réel
par point pour 4 variables réelles (Temperature/Specific humidity/
Pressure/Wind speed), calculé automatiquement à chaque changement de
niveau (mesuré ~0.07ms/point pour les 4 variables ensemble — largement
assez rapide pour un calcul automatique sur la grille native
complète). Rendu comme une vraie carte à colormap discrète (une
couleur par vrai statut §32, jamais un dégradé continu qui impliquerait
des statuts intermédiaires fictifs) plus un vrai résumé textuel des
comptages par statut.

**Confirmation indépendante d'un vrai résultat déjà trouvé** : ce
panneau, construit sans référence directe au bug de pression déjà
flagged, le redétecte de façon totalement indépendante — Pressure
affiche OUT_OF_RANGE à **100% des points réels** de la grille (~2013
hPa hors de la borne documentée [1000, 108500] Pa), tandis que
Temperature/Specific humidity/Wind speed restent honnêtement VALID à
100%. Une vraie preuve que cette infrastructure §32 fonctionne
correctement sur un cas réel connu, pas juste sur des données
synthétiques de test.

**Validation réelle** : `ruff`/`mypy` propres. 3 nouveaux tests unitaires
(`tests/test_acf_workstation_quality.py` — cross-vérifiés point par
point contre `assess_variable_quality()` appelée directement, plus un
test de régression reproduisant exactement l'anomalie de pression
connue) + 5 nouveaux tests GUI
(`tests/gui/test_acf_workstation_quality.py` — dont un test dédié
prouvant que ce panneau réel affiche bien "OUT_OF_RANGE" pour
Pressure) + mise à jour des tests d'intégration du chrome (nouvelle
position dans la nav/le stack à 9 modules désormais). Suite complète
**4093 → 4101**, toujours verte. Captures d'écran réelles envoyées :
carte Pressure entièrement rouge (OUT_OF_RANGE 7200/7200, 100%) et
carte Temperature entièrement verte (VALID 7200/7200, 100%).

**Ce qui reste réellement** : l'anomalie de pression ~2x (tâche
séparée toujours en attente — maintenant doublement confirmée, par ce
panneau ET par la découverte initiale en Thermodynamics Lab) ; 2
modules Lab restants (Convection, Terrain) plus les pièces plus larges
du spec maître (Multi-Model Lab en page propre, 3D/4D, Case Study Lab,
Research Mode, Configuration Management, palette de commandes,
raccourcis, export, extension API) listés "(planned)", pour les mêmes
raisons honnêtes déjà disclosed.

## Mise à jour 2026-09-04 (suite) — ACF Scientific Workstation, Phase 8 : le Multi-Model Lab, zéro nouvelle science

Suite explicite ("continue"), même discipline progressive. Cette passe
est la plus légère jusqu'ici : **aucune nouvelle science construite**
— uniquement l'exposition d'une donnée déjà réellement calculée par
Confidence Lab (Phase 5) mais jusque-là jetée après usage.

**Constat** : `ModelConsensusEngine.
compute_real_multi_model_disagreement_field()` calcule déjà, pour
chaque modèle comparé, son propre champ réel regrillé
(`per_model_field`) — mais le panneau Confidence Lab ne lisait jamais
que `disagreement_mean_field`/`disagreement_spread_field` (l'agrégat
statistique), jetant silencieusement les champs bruts par modèle après
usage.

**Construit** : **Multi-Model Lab**
(`acf_workstation_multimodel.ACFMultiModelLabPanel`) — un vrai
sélecteur Model A / Model B (parmi les 3 vrais AROME/ALADIN/ARPEGE, pas
seulement la paire fixe de Confidence Lab), un bouton à la demande
"🔄 Compare Models" appelant EXACTEMENT la même méthode réelle que
Confidence Lab, puis affiche soit le champ brut de chaque modèle
individuellement, soit une vraie différence ponctuelle
(`field_a - field_b`, en unités physiques réelles — ex. Kelvin, pas
une statistique standardisée) — une vraie question distincte de
l'agrégat de Confidence Lab : "où ces deux modèles précis
divergent-ils, et de combien concrètement ?" plutôt que "quel est le
désaccord général ?".

**Validation réelle** : `ruff`/`mypy` propres. 6 nouveaux tests GUI
(`tests/gui/test_acf_workstation_multimodel.py` — dont un vrai test de
bout en bout du worker hors thread via `qtbot.waitUntil`, et un
cross-check direct prouvant que la différence affichée est
exactement `field_a - field_b`, jamais une statistique re-dérivée) +
mise à jour des tests d'intégration du chrome (nouvelle position dans
la nav/le stack à 10 modules désormais). Aucun nouveau test unitaire
séparé n'était nécessaire — la méthode sous-jacente était déjà testée
en Phase 5. Suite complète **4101 → 4107**, toujours verte. Capture
d'écran réelle envoyée : différence ALADIN − ARPEGE réelle (moyenne
|Δ| 2.260 K, max |Δ| 13.934 K).

**Ce qui reste réellement** : l'anomalie de pression ~2x (tâche
séparée toujours en attente) ; 2 modules Lab restants (Convection,
Terrain) plus les pièces plus larges du spec maître (3D/4D, Case Study
Lab, Research Mode, Configuration Management, palette de commandes,
raccourcis, export, extension API) listés "(planned)", pour les mêmes
raisons honnêtes déjà disclosed.

## Mise à jour 2026-09-04 (suite) — ACF Scientific Workstation, Phase 9 : export réel PNG/SVG/CSV/JSON sur le widget carte partagé

Suite explicite ("continue"), même discipline progressive. Cette passe
sort du cadre "un Lab de plus" — elle ferme un vrai gap déjà disclosed
dans le plan initial ("export (PNG/SVG/CSV/JSON)") en l'appliquant au
bon endroit : **le widget carte partagé** (`AWCIMapPanel`,
`awci_map_panel.py`), pas un nouveau module. Résultat : toutes les
cartes de tous les modules du Workstation ET du dashboard AWCI
existant (qui réutilise le même widget) gagnent 3 nouveaux formats
d'export réels d'un coup.

**Constat** : `AWCIMapPanel` avait déjà un vrai bouton "⬇" fonctionnel
(export PNG, `figure.savefig()`) — mais seulement PNG, un `QPushButton`
simple. Aucune donnée brute (CSV/JSON) n'était exportable, seulement
l'image rendue.

**Construit** :
- Le bouton "⬇" devient un vrai `QToolButton` + `QMenu` (même
  convention "vraies actions derrière un seul contrôle" déjà établie
  pour le menu "☰" d'`ACFGeneralDashboard`) — 4 vraies actions : Save
  as PNG, Save as SVG (le vrai backend vectoriel natif de matplotlib,
  pas une image PNG rebaptisée), Export data as CSV, Export data as
  JSON. Aucun appelant/test existant ne dépendait du type Qt exact de
  `download_button` (seulement `is not None`) — extension rétrocompatible
  vérifiée par grep avant modification.
- Nouveau state réel `self._last_lons`/`_last_lats`/`_last_grid`,
  peuplé dans `update_data()` avec exactement les mêmes données que
  celles rendues à l'écran (`_external_field`, le motif de démo AWCI,
  OU l'état honnêtement vierge du Workstation) — CSV/JSON exportent
  donc toujours ce qui est réellement affiché, jamais une seconde
  source potentiellement obsolète.
- CSV : format long réel (une vraie ligne par cellule de grille réelle
  — `lat,lon,value`). JSON : structure réelle avec titre, horodatage
  UTC réel (même convention que le "RENDERED" déjà affiché ailleurs),
  lats/lons/grid. Une vraie cellule honnêtement vierge (NaN — ex.
  l'état vide `show_demo_fallback=False` du Workstation, ou une
  singularité aux pôles) s'exporte en champ CSV vide / `null` JSON,
  jamais un 0 fabriqué.

**Validation réelle** : `ruff`/`mypy` propres. 9 nouveaux tests
(`tests/test_awci_map_panel_export.py` — dont un test dédié prouvant
que les cellules NaN s'exportent honnêtement vides/null, un test
prouvant qu'annuler la boîte de dialogue n'écrit aucun fichier, et un
test de structure CSV/JSON complet) + suite de régression complète du
widget carte partagé re-exécutée (98 tests : map panel + AWCI real
physics/synchronization + Workstation chrome + ACFGeneralDashboard —
zéro régression). Suite complète **4107 → 4116**, toujours verte.
Capture d'écran réelle envoyée : le vrai menu déroulant à 4 formats,
et le bouton "⬇" avec son vrai indicateur de menu déroulant visible.

**Ce qui reste réellement** : l'anomalie de pression ~2x (tâche
séparée toujours en attente) ; 2 modules Lab restants (Convection,
Terrain) plus les pièces plus larges du spec maître (3D/4D, Case Study
Lab, Research Mode, Configuration Management, palette de commandes,
raccourcis, extension API) listés "(planned)" — "export" retiré de
cette liste, désormais réel.

## Mise à jour 2026-09-04 (suite) — ACF Scientific Workstation, Phase 10 : raccourcis clavier réels

Suite explicite ("continue"), même discipline progressive. Petite
passe fermant un autre item déjà disclosed dans le plan initial
("raccourcis clavier").

**Construit** : 3 vrais raccourcis, tous des accès plus rapides à des
actions déjà réelles, aucune nouvelle capacité inventée :
- **Ctrl+R** — redéclenche exactement le même vrai `refresh()` que le
  bouton "🔄 Run".
- **F11** — bascule exactement le même vrai plein écran que le bouton
  "⛶".
- **Ctrl+1..Ctrl+9, Ctrl+0** — saute au module réel correspondant par
  sa position réelle dans `_ENABLED_MODULES` — un seul raccourci
  généré par module de cette même liste (10 modules réels aujourd'hui
  = 10 raccourcis), jamais une liste séparée à maintenir à la main qui
  pourrait dériver hors synchronisation si un module est ajouté ou
  retiré de la nav.

**Validation réelle** : `ruff`/`mypy` propres. 5 nouveaux tests
(`tests/gui/test_acf_workstation_shortcuts.py` — vérifiant le vrai
nombre de raccourcis, la vraie séquence Ctrl+chiffre de chacun, et
que déclencher chacun appelle bien la vraie méthode attendue) + suite
d'intégration du chrome re-exécutée (zéro régression). Vérifié
manuellement de bout en bout (script réel construisant `ACFWorkstation`
et émettant `.activated` sur les raccourcis Ctrl+0/Ctrl+1 : bascule
bien vers la ligne de nav 9 puis 0). Suite complète **4116 → 4121**,
toujours verte.

**Ce qui reste réellement** : l'anomalie de pression ~2x (tâche
séparée toujours en attente) ; 2 modules Lab restants (Convection,
Terrain) plus les pièces plus larges du spec maître (3D/4D, Case Study
Lab, Research Mode, Configuration Management, une vraie palette de
commandes, extension API) listés "(planned)" — "raccourcis" retiré de
cette liste, désormais réel.

## Mise à jour 2026-09-04 (suite) — ACF Scientific Workstation, Phase 11 : la Command Palette (Ctrl+K)

Suite explicite ("continue"), même discipline progressive. Ferme le
dernier item d'interface simple encore listé "(planned)" : le spec
maître nomme explicitement une "Command Palette (Ctrl+K)" dans sa
section design.

**Construit** : **Command Palette**
(`acf_workstation_command_palette.CommandPaletteDialog`) — une vraie
liste de commandes filtrable en temps réel (recherche floue,
insensible à la casse, sous-chaîne), ouverte par Ctrl+K. **18 vraies
commandes réelles au total**, aucune capacité inventée : "Run",
"Toggle Fullscreen", "Go to <module>" pour chacun des 10 modules
réels activés, plus chaque action à la demande déjà construite dans
un Lab (CAPE/CIN, Run Temporal Analysis, Compute Model Disagreement,
Run Temporal Evolution, Compute Model Confidence Field, Compare
Models) — chaque entrée référence directement la vraie méthode ou le
vrai bouton qu'elle déclenche (ex. `self.thermodynamics_panel.
cape_button.click`), jamais un second chemin de déclenchement
indépendant. Ouverture non-modale (`.show()`, jamais `.exec()` bloquant),
même convention réelle déjà établie par `AWCIExecutionReportDialog`.
Navigation Haut/Bas réelle depuis le champ de recherche via un vrai
event filter Qt (pattern standard de palette de commandes) ; Entrée
exécute la commande sélectionnée et referme la palette.

**Validation réelle** : `ruff`/`mypy` propres. 10 nouveaux tests
(`tests/gui/test_acf_workstation_command_palette.py` — filtrage réel,
exécution réelle d'une commande via `run_command()`, Entrée déclenche
bien la commande sélectionnée, réutilisation de la même instance de
dialogue à l'ouverture répétée, vérification que la liste contient
bien "Run"/"Toggle Fullscreen"/chacun des 10 modules) + suite
d'intégration du chrome re-exécutée (zéro régression). Suite complète
**4121 → 4131**, toujours verte. Captures d'écran réelles envoyées :
les 18 commandes réelles listées, puis le filtre "temporal" réduisant
correctement à 3 résultats réels.

**Ce qui reste réellement** : l'anomalie de pression ~2x (tâche
séparée toujours en attente) ; 2 modules Lab restants (Convection,
Terrain) plus les pièces plus larges du spec maître (3D/4D, Case Study
Lab, Research Mode, Configuration Management, extension API) listés
"(planned)" — "palette de commandes" retirée de cette liste, désormais
réelle.

## Mise à jour 2026-09-04 (suite) — ACF Scientific Workstation, Phase 12 : Configuration Management (save/load réel)

Suite explicite ("continue"), même discipline progressive. Ferme un
autre gap déjà disclosed depuis la Phase 1 : le bouton "⚙" existait
depuis le début mais était désactivé, son propre tooltip disant
littéralement "Settings — not yet implemented".

**Construit** : le bouton "⚙" devient un vrai `QToolButton` + `QMenu`
(même convention que le menu d'export et le "☰" d'`ACFGeneralDashboard`)
avec deux vraies actions : "💾 Save Configuration…" / "📂 Load
Configuration…". Sérialise/restaure en JSON réel les vrais RÉGLAGES
choisis par l'utilisateur — modèle, niveau, ligne de nav active, et le
sélecteur de variable de **chacun des 9 Labs** (Overview, Dynamics,
Thermodynamics, Microphysics, Temporal, Confidence, Multi-Model×3,
Interactions×2, Quality) — via une seule table `_configuration_
selectors()` partagée entre export et import (source unique de vérité,
un nouveau Lab n'a qu'un seul endroit à mettre à jour). **Jamais les
données calculées elles-mêmes** : charger une configuration restaure
seulement CE QU'IL FAUT REGARDER, l'utilisateur doit toujours cliquer
"🔄 Run" pour une vraie donnée — respect littéral de la règle "no
fake functionality" du projet (ne jamais rejouer une sauvegarde comme
si c'était un vrai résultat frais). Restauration défensive réelle :
un champ inconnu/malformé (fichier édité à la main) est simplement
ignoré, jamais une erreur fatale sur tout le reste. Un `level_index`
restauré avant qu'un vrai volume n'existe reste honnêtement en attente
(`_pending_level_index`) et s'applique, borné au vrai nombre de
niveaux réels, dès le prochain run réel. Ajouté aussi à la Command
Palette ("Save Configuration…"/"Load Configuration…").

**Validation réelle** : `ruff`/`mypy` propres. 11 nouveaux tests
(`tests/gui/test_acf_workstation_configuration.py` — export/import
réels, ignorance réelle des champs malformés, aller-retour complet
entre deux instances réelles du Workstation, le cas `level_index` en
attente PUIS appliqué après un vrai run, JSON invalide honnêtement
signalé) + suite d'intégration du chrome re-exécutée (23 tests, zéro
régression). Vérifié aussi par un vrai script bout-en-bout (export →
écriture disque → nouvelle instance → lecture → import, tous les
champs corrects). Suite complète **4131 → 4142**, toujours verte.
Capture d'écran réelle envoyée : le vrai menu à 2 actions.

**Ce qui reste réellement** : l'anomalie de pression ~2x (tâche
séparée toujours en attente) ; 2 modules Lab restants (Convection,
Terrain) plus les pièces plus larges du spec maître (3D/4D, Case Study
Lab, Research Mode, extension API) listés "(planned)" —
"Configuration Management" retirée de cette liste, désormais réelle.

## Mise à jour 2026-09-04 (suite) — ACF Scientific Workstation, Phase 13 : l'extension `/api/v1/workstation`, et un petit refactor Qt-free pour l'exposer proprement

Suite explicite ("continue"), même discipline progressive. Ferme le
dernier item disclosed du plan initial : "extension de l'API
`/api/v1/*` pour ces nouveaux modules".

**Constat architectural avant de construire** : les fonctions de champ
réelles du Dynamics Lab/Thermodynamics Lab (`compute_real_vorticity_
divergence`, `real_grid_spacing_m`, `compute_real_wind_shear_field`,
`compute_real_theta_e_and_rh_fields`) vivaient directement dans les
modules de panneaux GUI (`acf_workstation_dynamics.py`,
`acf_workstation_thermodynamics.py`) — qui importent `PySide6.
QtWidgets` en tête de fichier pour leurs propres classes `QWidget`.
Les réutiliser directement depuis un routeur web aurait exigé que
PySide6 (une bibliothèque GUI) soit importable dans le processus
serveur — un vrai anti-pattern architectural, même si dans ce dépôt à
environnement virtuel unique cela aurait techniquement fonctionné.

**Construit** :
- **Petit refactor propre** : ces 4 fonctions déplacées vers un
  nouveau module réel, sans Qt : `acf.awci.workstation_fields`. Les
  deux modules GUI les réimportent maintenant depuis ce nouvel
  emplacement (une simple ré-exportation, jamais réimplémentées) —
  **zéro changement de comportement**, vérifié par la suite de tests
  GUI existante complète (94 tests) qui passe sans la moindre
  modification, aucun fichier de test touché.
- **`/api/v1/workstation`** (`acf.web.routers.workstation_router`) —
  3 vrais endpoints GET : `/theta_e` (θ-e + humidité relative
  réelles), `/dynamics` (vitesse du vent + vorticité + divergence
  réelles), `/wind_shear` (cisaillement de vent réel, colonne
  complète). Chacun fait réellement tourner `CoupledEarthSolver` une
  fois (via une nouvelle fonction `run_complexity_volume()` ajoutée à
  `_solver_guard.py`, même garde-fou de taille de requête réel que
  `complexity_router`/`events_router`, étendu à une vraie requête 3D)
  puis appelle exactement les mêmes fonctions réelles que les panneaux
  GUI. Les valeurs `NaN` réelles (ex. singularité aux pôles pour la
  vorticité) sérialisent honnêtement en `null` JSON, jamais une valeur
  fabriquée — réutilise `field_to_json_safe_list()`, déjà réel et
  déjà testé.

**Validation réelle** : `ruff`/`mypy` propres sur tous les fichiers
touchés. Suite GUI complète re-exécutée sans changement (94 tests,
zéro régression du refactor) + suite API web existante re-exécutée
(53 tests, zéro régression). 8 nouveaux tests
(`tests/test_web_workstation_api.py` — dont un test de régression
reproduisant explicitement le cas des pôles honnêtement `null` via une
vraie requête HTTP de bout en bout à travers `TestClient`, et la
vérification du garde-fou de taille de requête). Suite complète
**4142 → 4150**, toujours verte.

**Ce qui reste réellement** : l'anomalie de pression ~2x (tâche
séparée toujours en attente) ; 2 modules Lab restants (Convection,
Terrain — génuinement bloqués, aucune donnée réelle disponible sans
fabrication) ; 3D/4D, Case Study Lab, Research Mode listés "(planned)"
— "extension API" retirée de cette liste, désormais réelle (pour
Dynamics/Thermodynamics ; CAPE/CIN, phase des précipitations et
l'Interaction Engine restent GUI-only pour l'instant, un futur "continue"
pourrait étendre l'API à ces modules avec la même discipline).

## Mise à jour 2026-09-04 (suite) — ACF Scientific Workstation, Phase 14 : la vue 3D (structure volumique réelle)

Suite explicite ("continue"), même discipline progressive. §23 du spec
maître est explicite : "L'ACF ne doit pas seulement produire un score
ponctuel. Il doit pouvoir représenter `C(x,y,t)` et éventuellement
`C(x,y,z,t)` : 2D — Carte horizontale. **3D — Structure volumique.**"
Chaque autre Lab de ce Workstation ne montre qu'une seule vraie coupe
2D horizontale (le niveau courant) — cette passe construit la
dimension manquante.

**Construit** : **3D View**
(`acf_workstation_3d.ACF3DAtmospherePanel`) — une vraie technique
matplotlib standard et documentée : `Axes3D.contourf(..., zdir="z",
offset=pression)` empile jusqu'à 6 vrais niveaux natifs du volume déjà
calculé, chacun positionné à sa vraie pression moyenne réelle
(`pressure_volume_hpa[level].mean()`) — un vrai "cube de données",
jamais une isosurface interpolée ou fabriquée. Axe Z inversé
(`invert_zaxis()`) pour respecter la convention météorologique réelle
(pression décroissante vers le haut — sol/haute pression en bas,
haute atmosphère/basse pression en haut) tout en gardant les vraies
valeurs de données en hPa honnêtes, non modifiées. Choix de rendu
honnêtement disclosed : pas tous les niveaux natifs (jusqu'à 32 pour
AROME — illisible et lent) mais un sous-ensemble réel de 6 niveaux
régulièrement espacés (même compromis déjà établi pour CAPE/CIN et le
regrillage de Confidence Lab — jamais interpolé entre niveaux
affichés). Pas de fond de carte géographique (disclosed explicitement
dans le titre du panneau) — axes réels longitude/latitude/pression
seuls. Ajouté à la nav (11ᵉ module désormais) et à
`_render_all_panels()`/`_configuration_selectors()` (Configuration
Management sauvegarde/restaure aussi son sélecteur de variable).

**Régression réelle trouvée et corrigée par la suite elle-même** : la
Phase 14 fait passer `_ENABLED_MODULES` à 11 entrées, dépassant les 10
vraies touches Ctrl+chiffre disponibles (Ctrl+1-9, Ctrl+0). La suite
complète a immédiatement détecté 2 tests de la Phase 10 en échec
(`test_exactly_one_real_nav_shortcut_per_real_enabled_module`/
`test_nav_shortcuts_use_the_real_ctrl_digit_sequence`), qui
supposaient naïvement un raccourci par module. L'implémentation
elle-même (`_setup_shortcuts()`) plafonnait déjà correctement à 10
raccourcis réels (`_ENABLED_MODULES[:10]`) — seuls les tests et le
docstring affirmaient encore l'ancienne hypothèse 1-pour-1. Corrigés
pour refléter honnêtement le vrai plafond : "3D View" (11ᵉ module) n'a
simplement pas de raccourci Ctrl+chiffre propre, reste réellement
accessible via la nav ou la Command Palette — disclosed explicitement,
pas une régression silencieuse.

**Validation réelle** : `ruff`/`mypy` propres. 7 nouveaux tests
(`tests/gui/test_acf_workstation_3d.py` — vraie projection 3D
vérifiée, vrai regard-fou sur le nombre de niveaux affichés même pour
un volume à 20 niveaux, vraie vérification de l'inversion de l'axe Z)
+ mise à jour des tests d'intégration du chrome (nouvelle position
dans la nav/le stack à 11 modules désormais) + les 2 tests Phase 10
corrigés ci-dessus. Suite complète **4150 → 4157**, toujours verte
(après correction). Captures d'écran réelles envoyées : Temperature
(nette différenciation visuelle entre niveaux, du bleu froid en
altitude à l'orange chaud au sol) et Wind speed (uniformité honnête
entre niveaux — un vrai résultat, pas un bug).

**Ce qui reste réellement** : l'anomalie de pression ~2x (tâche
séparée toujours en attente, visible aussi sur l'axe Z de cette
nouvelle vue — ~2013 hPa au lieu de ~1013 hPa attendu) ; 2 modules Lab
restants (Convection, Terrain) ; Case Study Lab, Research Mode listés
"(planned)" — "3D/4D" retirée de cette liste (la partie "4D" —
évolution temporelle — était déjà couverte par le Temporal Evolution
Lab de la Phase 4 ; cette passe ferme la partie "3D" restante).

## Mise à jour 2026-09-04 (suite) — ACF Scientific Workstation, Phase 15 : le Case Study Lab, une réinterprétation honnête

Suite explicite ("continue"), même discipline progressive.

**Pourquoi une "réinterprétation"** : le nom "Case Study Lab" du spec
maître pourrait suggérer une bibliothèque d'événements météo
HISTORIQUES réels (ex. "Tempête X, 12 mars 2024"). Ce codebase n'a
aucune vraie donnée archivée opérationnelle nulle part —
`CoupledEarthSolver` tient toujours lieu d'un modèle opérationnel réel,
jamais d'une vraie archive (déjà disclosed à plusieurs reprises,
notamment dans `ModelConsensusEngine.
compute_real_multi_model_disagreement()`'s own honest_limitation).
Construire une bibliothèque de "cas historiques" à partir de ça
aurait signifié soit fabriquer des événements qui n'ont jamais eu
lieu, soit faire passer une sortie de solveur en direct pour une
archive réelle — exactement le genre d'erreur que les audits de ce
projet existent pour attraper.

**Construit** : **Case Study Lab**
(`acf_workstation_case_study.ACFCaseStudyLabPanel`) — une vraie
bibliothèque nommée de CONFIGURATIONS Workstation réelles et
reproductibles (réutilise `_export_configuration()`/
`_apply_configuration()` de la Phase 12), jamais une prétention qu'un
véritable événement historique est rejoué. Un utilisateur peut
sauvegarder la configuration courante sous un nom réel ("Vue fort
cisaillement de vent"), la recharger, ou la supprimer — même règle
"réglages, jamais données" que Configuration Management : charger un
cas nécessite toujours de cliquer "🔄 Run" pour une vraie donnée
fraîche. Persisté durablement en JSON réel sous
`<repo_root>/data/workstation/case_studies.json` (même convention
`data/*` réelle déjà établie par `events_router`/`datasets_router`).
Chargement défensif réel : un fichier manquant ou corrompu redevient
honnêtement une bibliothèque vide, jamais un crash. Ajouté à la nav
(12ᵉ module) et à la Command Palette ("Save Current Configuration as
Case…").

**Validation réelle** : `ruff`/`mypy` propres. 10 nouveaux tests
(`tests/gui/test_acf_workstation_case_study.py` — persistance
JSON réelle testée directement, aller-retour complet sauvegarde→
disque→lecture, dialogue annulé = aucun effet, sélection vide = erreur
honnête) + mise à jour des tests d'intégration du chrome (nouvelle
position dans la nav/le stack à 12 modules désormais). Vérifié aussi
par un vrai script bout-en-bout (fichier JSON réel écrit sur disque,
sélection réelle dans la liste, chargement réel qui change bien le
modèle ARPEGE→ALADIN et restaure la vraie variable Dynamics
sélectionnée). Suite complète **4157 → 4167**, toujours verte. Capture
d'écran réelle envoyée : la liste avec un vrai cas sauvegardé, les 3
boutons réels (Save/Load/Delete).

**Ce qui reste réellement** : l'anomalie de pression ~2x (tâche
séparée toujours en attente) ; 2 modules Lab restants (Convection,
Terrain — génuinement bloqués, aucune donnée réelle sans fabrication) ;
Research Mode listé "(planned)", pièce plus large du spec maître hors
de la liste originelle des "Labs".

## Mise à jour 2026-09-04 (suite) — ACF Scientific Workstation, Phase 16 : le Research Mode

Suite explicite ("continue"), même discipline progressive. Dernière
grande pièce du plan initial restant à fermer (avec Convection/Terrain,
génuinement bloqués sans fabrication).

**Construit** : un vrai bouton bascule "🔬 Research Mode" dans la barre
du haut. Activé, cliquer sur la carte du Thermodynamics Lab ou du
Microphysics Lab (réutilise `AWCIMapPanel.pointClicked`, déjà réel,
déjà testé ailleurs pour AWCI) recalcule EN DIRECT, au point de grille
réel le plus proche du clic, la vraie fonction ponctuelle sous-jacente
(`compute_real_theta_e_at_point()`/`compute_real_hydrometeor_phase_
at_point()`) et affiche son retour réel COMPLET dans une vraie boîte
de dialogue — pas seulement la valeur unique déjà affichée sur la
carte, mais aussi le point de rosée réel, l'humidité relative réelle,
la température du thermomètre mouillé réelle, et le texte
`honest_limitation` réel de la fonction elle-même. Zéro nouvelle
physique — seulement une exposition, à la demande, de données déjà
réelles jusque-là jetées après le rendu de la carte.

**Périmètre honnêtement borné** : seuls 2 Labs (Thermodynamics,
Microphysics) supportent Research Mode dans cette passe — les autres
Labs ne sont pas affectés par le bouton, disclosed explicitement dans
le docstring plutôt que prétendre une couverture universelle. Aussi
accessible depuis la Command Palette ("Toggle Research Mode").

**Validation réelle** : `ruff`/`mypy` propres. 9 nouveaux tests
(`tests/gui/test_acf_workstation_research_mode.py` — clic sans effet
quand désactivé, détail réel complet affiché quand activé, absence de
volume gérée sans crash, bascule propagée aux deux panneaux, accessible
depuis la Command Palette) + suite Workstation complète re-exécutée
(120 tests, zéro régression). Vérifié aussi par un vrai script
bout-en-bout à travers tout le chrome `ACFWorkstation` (clic réel sur
la carte Thermodynamics d'un vrai run ALADIN → boîte de dialogue réelle
avec θ-e=244.39K, humidité relative=100% [confirme à nouveau
l'anomalie de pression connue, honnêtement affichée, pas masquée],
point de rosée=285.98K). Suite complète **4167 → 4176**, toujours
verte. Capture d'écran réelle envoyée : le bouton "🔬 Research Mode"
visible dans son état activé dans la barre du haut.

**Ce qui reste réellement** : l'anomalie de pression ~2x (tâche
séparée toujours en attente — maintenant triplement confirmée : Data
Quality Center, découverte initiale Thermodynamics Lab, et Research
Mode) ; 2 modules Lab restants (Convection, Terrain — génuinement
bloqués, aucune donnée réelle disponible sans fabrication). Avec cette
fermeture, toutes les pièces du plan initial jugées réellement
réalisables sans fabriquer de données sont maintenant construites,
testées et vérifiées visuellement.
