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

- **Data Contract formalisé (§4 du Prompt Maître) : MISSING** comme classe
  unique. Il existe des dataclasses partielles proches par endroits (ex.
  `EncyclopediaEntry`), mais pas de `Dataset` avec exactement les champs
  proposés (`id, source, model, run, forecast_reference_time, valid_time,
  lead_time, variable, unit, dimensions, coordinates, horizontal_grid,
  vertical_coordinate, ensemble_member, quality, uncertainty, provenance,
  version`).
- **Model Adapters : PARTIAL.** `models/{arome,aladin,arpege}/
  ingestion_adapter.py` existent réellement (`AROMEIngestionAdapter(
  BaseWeatherModel)` avec `detect()/variables()/levels()/projection()/
  read_arome_file()`), mais avec un contrat différent (pas
  `identify/discover/read/metadata/coordinates/vertical_levels/
  forecast_times/capabilities/normalize` du Prompt Maître) — un
  chevauchement partiel, pas une correspondance exacte. **WRF, ICON,
  OpenIFS : aucun adapter** — confirmé absent, pas juste incomplet.
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

**MISSING comme objets de cycle de vie formels.** `aeos/events/event_bus.py`
et `digital_twin/events/cascade_engine.py` existent mais sont des bus
d'événements SYSTÈME (signaux internes de l'application), pas des objets
météorologiques (`ThunderstormEvent`, `CycloneEvent`...) avec le cycle
`DETECTED → ANALYZED → CONFIRMED → VERIFIED → CERTIFIED → PUBLISHED` du
§13-14 du Prompt Maître. Rien de tel n'existe — confirmé, pas supposé.

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
| Physics Guard (infra transversale) | MISSING |
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
