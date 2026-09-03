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
