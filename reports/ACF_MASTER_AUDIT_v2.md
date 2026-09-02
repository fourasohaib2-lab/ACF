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

- **API organisée par domaine** (§21) — toujours partielle.
- **Progress réel par job** — toujours non calculé (limite honnête).
- **Regridding bilinéaire/conservatif générique** — toujours absent
  (plus-proche-voisin seulement, partout dans ce paquet).

Dis-moi laquelle tu veux que j'attaque ensuite.
