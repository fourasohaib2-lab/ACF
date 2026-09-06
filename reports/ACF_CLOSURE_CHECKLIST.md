# ACF — Checklist de clôture (3 chantiers)

**Date :** 5 septembre 2026
**Commit de référence :** `2babda0` (branche `develop`, à jour avec `origin/develop` au moment de la rédaction)
**Auteur de la vérification :** session d'audit dédiée, méthode Physics Guard (lecture réelle du code, pas d'inférence depuis un nom de fichier ou une docstring)

## Objet de ce document

Répondre à une seule question, sans inventer de chiffre : **combien
d'items concrets, vérifiables, reste-t-il pour clôturer chacun des 3
chantiers du dépôt ACF ?**

Ce document n'est **pas** un audit de plus — c'est un **décompte**. Il
s'appuie sur :
- `reports/ACF_MASTER_AUDIT_v2.md` (9366 lignes, l'audit fabrication/
  duplication post-`model4d`) ;
- `docs/ACF_ARCHITECTURE_TARGET_GAP_MAP.md` (correspondance architecture
  cible ↔ code réel, 38 couches) ;
- `docs/ACF_MASTER_UNIFIED_ARCHITECTURE.md` (architecture cible à 30
  niveaux) ;
- `docs/ACF_MASTER_ROADMAP.md` et `ROADMAP.md` (feuille de route
  v0.2 → v1.0) ;
- une relecture directe du code source (`grep`, lecture de fichiers
  entiers) pour **chaque** item listé ci-dessous — aucun item n'est
  repris tel quel d'un document sans re-vérification dans le code réel
  à la date de ce commit.

**Méthode de comptage — ce que "1 item" veut dire ici** : un fait
vérifiable dans le code (une classe absente, un stub qui retourne un
statut `NOT_*`/`WEIGHTS_ONLY_*`, un clic mort dans une arborescence GUI,
une fonction jamais appelée par son consommateur prévu). Pas une
estimation de charge, pas de jours/semaines — juste un décompte de faits
vérifiés. Un item non listé ici n'est pas nécessairement clos : c'est un
item **non vérifié dans cette passe** (voir la section "Ce que cette
passe ne couvre pas" à la fin).

---

## Chantier 1 — Audit fabrication/duplication post-`model4d`

### Statut : fermé pour son périmètre déclaré, **1 item réel trouvé hors de ce périmètre strict**

**Vérification du périmètre déclaré (21 zones).** Le dernier commit du
dépôt sur `develop` est `2babda0` — "fix(release): 6 fabricated
production-status claims - last zero-coverage zone". La dernière
section de `reports/ACF_MASTER_AUDIT_v2.md` (ligne 9278, "DERNIÈRE
ZONE") confirme et dénombre elle-même les 21 zones couvertes par cette
continuation d'audit (`aeos`, `knowledge_platform`, `parameters`,
`master`, `climate`, `api`, `storage`, `time`, `utils`, `alerts`,
`analysis`, `animation`, `connectors`, `fire_weather`, `workspace`,
`surfex`, `ocean`, `planetary`, `geospatial`, `space_weather`,
`release` = 21), avec un dernier relevé de suite de tests à **4466
passed, 18 skipped, 0 failed**. Aucune zone supplémentaire n'est
annoncée en attente dans le fichier. **Le périmètre des 21 zones
post-`model4d` est donc réellement clos, 21/21 — confirmé, pas
seulement repris de l'énoncé de la tâche.**

**Un item réel reste cependant ouvert, trouvé lors d'une phase
antérieure du même audit (avant la continuation post-`model4d`) et
jamais refermé depuis :**

1. **Doublon `MapCanvas` non consolidé.**
   `src/acf/gui/map/map_canvas.py::MapCanvas` (un `QWidget` composite
   intégré dans la fenêtre ESOC réelle via `ViewManager`/`MainWindow`)
   et `src/acf/maps/canvas/map_canvas.py::MapCanvas` (un
   `FigureCanvasQTAgg` direct, utilisé par l'API publique `acf.maps` et
   par la table de ré-export d'`acf.visualization`) sont **tous les
   deux réellement vivants, tous les deux réellement utilisés
   aujourd'hui**, pas des formes interchangeables — confirmé par
   `docs/architecture/duplicate_components.md` (bannière de
   re-vérification 2026-09-02) et verrouillé par
   `test_map_canvas_is_a_real_verified_duplicate_not_yet_consolidated()`
   dans `tests/test_collisions_consolidation.py`. Vérifié à nouveau
   pour ce document : `git log -- <les deux fichiers>` ne montre aucun
   commit de consolidation depuis leur dernière modification — le
   doublon est toujours présent tel quel dans l'arbre à `2babda0`.
   Consolider signifie choisir un gagnant (`QWidget` composite vs
   `FigureCanvasQTAgg` direct) et migrer l'un des deux groupes
   d'appelants — une décision de conception, explicitement pas prise
   dans aucune passe à ce jour. **[MISSING — 1 item]**

**Vérifié et écarté (faux positifs confirmés, pas des items
restants)** : `docs/architecture/duplicate_components.md` (même
bannière) confirme que la quasi-totalité des autres lignes de son
propre tableau "Duplications critiques" (Fenêtre principale, Moteur
cartographique, Catalogues, Paramètres, Lecteurs de données, BUFR,
NetCDF/GRIB, Validation dataset) sont déjà unifiées derrière une
implémentation canonique avec compatibilité ascendante, verrouillées
par `tests/test_collisions_consolidation.py` (ACF-017) et
`tests/test_importers_consolidation.py` (ACF-016) ; que "Plugins" et
"Data manager" sont des homonymes légitimes (responsabilités
différentes, pas des doublons) ; et que la pile "Couches et renderers"
(`gui.map`/`maps`/`visualization`) n'est pas un vrai triple
dédoublement en pratique (`gui.map.{layers,renderers,...}` n'a aucun
importeur réel dans `src/`).

**Total chantier 1 : 1 item.**

---

## Chantier 2 — Câblage GUI ESOC ("Phase 1 à 52+")

### Statut : en cours, aucun total officiel déclaré nulle part — décompte ci-dessous établi par lecture directe de l'arborescence System Explorer et de son routage réel

**Base de vérification.** `src/acf/gui/esoc/esoc_sidebar.py::ESOCLeftSidebar.categories`
définit l'arborescence réelle du "System Explorer" : **20 catégories,
81 feuilles**. `src/acf/gui/esoc/esoc_layout.py` (`_LEAF_LABEL_TO_PANEL_NAME`
+ `_CATEGORY_LABEL_TO_PANEL_NAME`) est le routage réel, tenu à jour et
documenté avec précision par ses propres auteurs — cette table a été
recomptée manuellement, feuille par feuille, contre l'arbre réel de
`esoc_sidebar.py`, pas reprise telle quelle.

**Clics morts restants (aucun panneau réel derrière la feuille) : 3**

1. **"Earth System / Atmospheric Chemistry"** — aucune classe de
   chimie atmosphérique orchestratrice n'existe dans le dépôt en
   dehors de la réserve déconnectée `acf.model4d` (investiguée et
   délibérément laissée non intégrée, voir `panel_manager.py`
   Phase 48). `_LEAF_LABEL_TO_PANEL_NAME` ne contient aucune entrée
   `"Atmospheric Chemistry"`. **[MISSING]**
2. **"Earth System / Dust"** — aucune formule d'émission de poussière
   minérale vérifiable n'a été trouvée dans le dépôt (même discipline
   de non-fabrication que `fire_weather`) ; `panel_manager.py` ligne
   1983-1985 documente l'investigation et l'abandon délibéré.
   **[MISSING]**
3. **"Settings / API Keys"** — confirmé par grep exhaustif (cité dans
   `panel_manager.py` ligne 2247) : zéro code dans tout le dépôt ne lit
   une clé d'API nulle part ; un formulaire de sauvegarde n'aurait
   aucun consommateur réel. **[MISSING]**

**Panneaux réels avec un gap fonctionnel interne disclosed (le clic
n'est pas mort, mais une partie de ce que le panneau montre n'est pas
réelle) : 4**

4. **"Artificial Intelligence / GNN Surrogates"** — la feuille ouvre le
   vrai `AIForecastPanel`, mais aucun backend GNN réel n'existe nulle
   part dans le dépôt (confirmé par recherche, `esoc_layout.py` lignes
   189-204) ; seul le FNO (`FourierNeuralOperator2D`) est réellement
   entraîné et exécuté. **[PARTIAL]**
5. **"Artificial Intelligence / PINN Models"** — même panneau, même
   constat : aucun backend PINN réel. **[PARTIAL]**
6. **"Output / GRIB2 Datasets"** — `OutputPanel` (`panel_manager.py`
   lignes 1437-1476) a de vrais writers pour NetCDF4, Zarr et GeoTIFF ;
   GRIB2 reste un **gap disclosed**, pas fabriqué : `eccodes`/`cfgrib`
   permettent une vraie lecture GRIB2 (`GRIBReader`) mais aucune
   écriture GRIB2 n'existe dans ce dépôt (template/édition/code
   paramètre non implémentés). **[PARTIAL]**
7. **"HPC / MPI Domain Topology"** — vrai découpage de domaine 2D
   (arithmétique réelle), mais `exchange_halo_boundaries()` lève
   délibérément `NotImplementedError` (`panel_manager.py` ligne 2100 et
   2147) : aucune bibliothèque MPI n'est connectée nulle part dans le
   dépôt. **[PARTIAL]**

**Panneau latéral droit (`ESOCRightSidebar`) — 2 items**

8. **6 des 7 onglets Inspector** (Properties, Diagnostics, Metadata,
   Simulation, Logs, Performance) affichent toujours un texte
   d'exemple 100% statique, explicitement étiqueté "Example Layout...
   illustrative, not tied to any real selection" — vérifié en lisant
   `esoc_sidebar.py` lignes 256-360 dans son état actuel : aucun de ces
   6 onglets n'est branché à une sélection, un dataset ou une
   simulation réelle. Honnêtement disclosed (pas fabriqué), mais reste
   un vrai gap fonctionnel. **[PARTIAL — 1 item pour les 6 onglets, même
   cause racine]**
9. **Onglet "AI Analysis & Plots" — bouton "Render Plot"** —
   `_render_plot()` (ligne 412-421) ajoute inconditionnellement
   `"[NOT IMPLEMENTED]: no real plotting backend is connected here"`
   pour chacun des 9 types de graphique proposés dans le menu déroulant
   — confirmé par lecture directe, aucun graphique n'est jamais
   réellement rendu. **[MISSING]**

**`ModuleRegistry` (`src/acf/gui/esoc/module_registry.py`) — 4 items**

Sur les 25 sous-systèmes enregistrés, **21/25 sont réellement
connectés** (vérifié par le fichier lui-même et par
`tests/test_module_registry_wiring.py`) ; les 4 restants pointent vers
une classe qui **n'existe littéralement pas** dans le dépôt — vérifié
directement pour ce document (recherche `class <Nom>` dans tout
`src/acf/`, zéro résultat pour chacune des 4) :

10. **`earth_physics`** → cible `AtmosphericDynamicsEngine` dans
    `acf.earth_physics` — classe introuvable. **[MISSING]**
11. **`space_weather`** → cible `SpaceWeatherPlatform` dans
    `acf.space_weather` — classe introuvable. **[MISSING]**
12. **`geology`** → cible `GeologyPlatform` dans `acf.geology` — classe
    introuvable. **[MISSING]**
13. **`geoengineering`** → cible `GeoengineeringPlatform` dans
    `acf.geoengineering` — classe introuvable. **[MISSING]**

Ces 4 domaines sont de vrais paquets peuplés de nombreux moteurs
indépendants (pas d'orchestrateur unique) — c'est documenté comme un
choix délibéré (`module_registry.py` lignes 5-32) plutôt qu'un oubli,
mais reste un gap réel et vérifiable au sens strict de ce décompte.

**Total chantier 2 : 13 items.**

*(Rappel de périmètre : sur 81 feuilles réelles au total dans
l'arborescence System Explorer, 78 ouvrent un panneau réel — la grande
majorité de ce chantier, en volume brut de clics, est donc déjà
fermée ; les 13 items ci-dessus couvrent les 3 clics encore morts plus
10 gaps fonctionnels internes à des panneaux par ailleurs réels.)*

---

## Chantier 3 — Feuille de route globale (v0.2 → v1.0, architecture cible à 30 niveaux)

### Statut : `pyproject.toml` déclare `0.1.0` ; aucun jalon officiel de la chaîne v0.2→v1.0 n'est marqué atteint

**Incohérence de base**

1. **Version déclarée vs feuille de route.** `pyproject.toml` ligne
   contenant `version = "0.1.0"` — vérifié directement. Or
   `docs/ACF_MASTER_ROADMAP.md` présente une chaîne "ACF v0.2 Baseline
   → ... → ACF v1.0" sans jamais indiquer où le code réel se situe
   aujourd'hui sur cette chaîne. `ROADMAP.md` (le fichier tenu à jour,
   distinct du précédent) ne cite non plus aucune version cible
   atteinte — seulement un état "vérifié le 2 septembre 2026" en
   termes de tests, pas de version. **Aucun document du dépôt ne fait
   correspondre `0.1.0` à un jalon précis de la chaîne v0.2→v1.0.**
   **[MISSING — 1 item]**

**Grid / Regridding (§6 de l'architecture cible)**

2. **Regridding bicubique absent.** `src/acf/awci/regridding.py`
   implémente réellement `regrid_nearest_neighbor()`,
   `regrid_bilinear()` et `regrid_conservative()` (testés, y compris
   par des tests de conservation réels) — confirmé par lecture directe
   et par `reports/ACF_MASTER_AUDIT_v2.md` (ligne 925). Recherche
   `grep -ri bicubic` sur tout `src/acf/` : **zéro résultat**. Le 4ᵉ
   type listé par l'architecture cible n'existe nulle part.
   **[MISSING]**
3. **Regridding scopé aux seules grilles rectilignes régulières
   lat/lon.** Les 3 fonctions ci-dessus sont explicitement documentées
   comme ne fonctionnant que sur `EarthGrid` (le seul type de grille
   qu'ACF produit) — pas de support curvilinéaire ni non structuré, les
   2 autres types listés par l'architecture cible §6. **[MISSING]**
4. **Interpolation verticale vers niveaux de pression standards
   absente.** Confirmé à plusieurs endroits indépendants de l'audit
   (`ACF_ARCHITECTURE_TARGET_GAP_MAP.md` lignes 262-268,
   `reports/ACF_MASTER_AUDIT_v2.md` lignes 116-124) : seuls les niveaux
   natifs du solveur sont exposés (`pressure_volume_hpa` permet de
   trouver le niveau natif le plus proche, mais n'interpole rien).
   Aucune fonction d'interpolation vers 1000/925/850/700/500/300 hPa...
   n'existe dans le dépôt. **[MISSING]**

**Physics Guard transversal (§5 de l'architecture cible)**

5. **Pipeline UNIT→DIMENSION→RANGE→COORDINATE→VERTICAL→TIME non
   appliqué systématiquement.** `src/acf/physics_guard/` existe
   réellement (6 vérifications réelles : unit/range/coordinate/
   dimension/vertical/consistency — voir
   `reports/ACF_MASTER_AUDIT_v2.md` ligne 292). Mais son seul point
   d'agrégation réellement branché à l'ingestion,
   `Dataset.validate()` (`src/acf/core/contracts/dataset.py`, lignes
   154-193), n'exécute que **3 des 6 vérifications disponibles**
   (coordinate, range, time — vérifié en lisant le corps de la
   méthode) ; `unit_check`/`dimension_check`/`vertical_check` existent
   comme fonctions autonomes mais ne sont jamais appelées par ce
   pipeline. Ce pipeline lui-même n'est branché que dans 2 lecteurs
   réels (`grib_reader.py`, `netcdf_reader.py`) plus le moteur de
   certification et un endpoint API — pas systématiquement à chaque
   point d'entrée scientifique du dépôt. **[PARTIAL — 1 item]**

   **Mise à jour 2026-09-06 (audit de continuation, post-clôture) :**
   `Dataset.validate()` exécute désormais **5 des 6** vérifications
   (coordinate, range, dimension, unit, time — dimension et unit
   ajoutés en réutilisant `acf.physics_guard.dimension_check.
   check_field_shape()` et `acf.physics_guard.unit_check.check_unit()`
   déjà existants et déjà testés, aucune nouvelle logique de
   vérification inventée). Au passage, un vrai bug trouvé et corrigé :
   `range_check.check_range()` laissait échapper une
   `pint.errors.DimensionalityError` brute (non déclarée par son
   propre docstring) au lieu d'une `RangeError` catchable quand `unit`
   était dimensionnellement incompatible avec l'unité canonique de la
   variable — ce qui aurait fait planter `Dataset.validate()` au lieu
   de rapporter une violation, pour n'importe quel Dataset réel dont le
   champ `unit` serait erroné. `vertical_check` reste délibérément non
   branché : `coordinates["levels"]` est un simple index de niveau dans
   l'usage réel de ce contrat (`Dataset.from_real_volume()`), pas un
   profil de pression réel - brancher `check_pressure_decreases_with_
   altitude()` dessus validerait silencieusement la mauvaise grandeur
   physique. Validé par `pytest tests/test_core_contracts.py
   tests/test_certification_engine.py tests/test_physics_guard.py
   tests/test_physics_guard_variable_quality.py` (99/99), `ruff check`
   propre. Item désormais **[PARTIAL, réduit]** : le pipeline
   `Dataset.validate()` couvre 5/6 vérifications au lieu de 3/6 ; il
   reste non branché à chaque point d'entrée scientifique du dépôt
   (ce second volet de l'item, hors scope de cette passe, reste ouvert).

   **Correction 2026-09-06 (même passe) — l'affirmation "branché dans
   `grib_reader.py`/`netcdf_reader.py`" ci-dessus est fausse, vérifiée
   directement plutôt que reprise telle quelle :** aucun des 3
   `grib_reader.py` réels du dépôt (`acf.data.grib_reader`,
   `acf.data.readers.grib_reader`, `acf.importers.readers.grib_reader`)
   ni des 3 `netcdf_reader.py` équivalents n'importe `physics_guard` ou
   `core.contracts` (`grep` exhaustif, zéro résultat).
   `acf.importers.readers.grib_reader.GRIBReader.read()` appelle bien
   un `dataset.validate()`, mais sur `acf.data.dataset.Dataset` - une
   classe homonyme et sans rapport, dont `validate()` ne vérifie que la
   présence d'un nom et d'au moins une variable, sans aucun lien avec
   Physics Guard. Les 2 points d'intégration réels de
   `acf.core.contracts.dataset.Dataset.validate()` (le seul `Dataset`
   dont `validate()` appelle réellement Physics Guard) sont
   `certification/engine.py` et `web/routers/datasets_router.py`
   (confirmés) ; les 2 autres appelants réels sont `forecast/engine.py`
   et `awci/{input_adapter,pipeline}.py` - **pas** les lecteurs
   GRIB/NetCDF. Compte réel des points d'intégration donc : **4
   consommateurs réels, 0 lecteur de fichier** - pas "2 lecteurs +
   certification + API" comme l'énoncé original le disait.

**Multi-modèle / Consensus / Incertitude (§12-15 de l'architecture cible)**

6. **`ModelConsensusEngine.compute_unified_consensus()` reste un stub
   honnête.** Vérifié directement : `src/acf/visualization/
   ai_forecast_center/model_consensus_engine.py` ligne 96 retourne
   `"status": "WEIGHTS_ONLY_NO_MODEL_FIELDS_FUSED"` — aucune fusion
   réelle de champs de plusieurs modèles. À distinguer de
   `compute_real_multi_model_disagreement()`, une méthode différente,
   réelle mais scopée à un seul point de grille (Alger, 3 modèles),
   ajoutée séparément. **[PARTIAL]**

   **Correction 2026-09-06 (demande explicite de l'utilisateur : "la
   fusion multi-modèle") — cet item décrivait mal le vrai gap.** Une
   fusion de champ complet réelle, pondérée (poids déclarés ou skill
   database réel), avec correction de biais réelle et spread réel,
   **existait déjà** depuis le 2026-09-02
   (`acf.awci.multi_model_fusion.compute_real_multi_model_field_fusion()`,
   voir `reports/ACF_MASTER_AUDIT_v2.md`) - cet énoncé ne l'avait pas
   trouvée. Vérifié par grep exhaustif à l'époque : zéro appelant réel
   nulle part dans le dépôt - le vrai gap était l'INACCESSIBILITÉ de
   cette capacité déjà réelle depuis `ModelConsensusEngine`, pas son
   absence. Corrigé : ajout de
   `ModelConsensusEngine.compute_real_weighted_field_fusion()`, un pur
   wrapper vers la fonction déjà réelle (aucune logique dupliquée).
   `compute_unified_consensus()` elle-même reste inchangée à raison -
   son statut honnête couvre un périmètre différent (12 modèles
   NWP/IA majoritairement non implémentés dans ACF), pas les 3 modèles
   réels que la fusion couvre. Validé par 2 nouveaux tests dans
   `tests/test_ai_forecast_center.py` (33/33 passent), `ruff check`
   propre. Item réel restant, non traité cette passe : l'extension GUI
   du panneau "Multi-Model Lab" pour afficher ce champ fusionné
   pondéré (actuellement il n'affiche que les champs bruts et leur
   différence) - un chantier PySide6 distinct, non tenté faute
   d'environnement GUI complet ici (`libEGL.so.1` absent).
7. **`ForecastComparisonMatrix` reste un stub honnête.** Vérifié
   directement : `src/acf/visualization/ai_forecast_center/
   forecast_comparison.py` ligne 26 retourne
   `"status": "NOT_COMPUTED_NO_MODEL_COMPARISON_RUN"` — aucune
   comparaison de modèles n'est jamais calculée. **[MISSING]**

**Digital Twin (§21 de l'architecture cible)**

8. **`DigitalTwinScenarioEngine.run_scenario()` reste un stub honnête
   pour les 5 scénarios déclarés** (SSP1-1.9, SSP2-4.5, SSP3-7.0,
   SSP5-8.5, +2°C). Vérifié directement :
   `src/acf/digital_twin/scenario_engine.py` retourne
   inconditionnellement `"projections": None`,
   `"status": "NOT_SIMULATED_NO_CLIMATE_MODEL_CONNECTED"` — aucun
   modèle climatique CMIP6 n'est connecté. Les feuilles System
   Explorer "2030"/"2050"/"2100"/"2300" de la catégorie "Digital Twin"
   ouvrent bien un panneau réel (`digital_twin`), mais ce panneau
   n'a, pour la partie scénarios, aucun calcul réel derrière lui.
   **[MISSING]**

**HPC / Temps réel (§26-27 de l'architecture cible)**

9. **Solveurs accélérés GPU non branchés au solveur de production.**
   `src/acf/hpc/gpu_acceleration.py::GPUPhysicsAccelerator` et
   `src/acf/hpc/simulation/gpu_solver.py::GPUSolver` sont réels et
   honnêtes (détection `cupy` réelle, repli CPU disclosed si absent —
   pas de fabrication). Mais vérifié par recherche exhaustive : **aucun
   appelant réel** de ces deux classes n'existe dans
   `acf.digital_twin`/`acf.simulation_engine`/`CoupledEarthSolver` — le
   solveur physique que tout le reste du dépôt utilise (AWCI, ESOC,
   dashboards) tourne intégralement sur CPU/NumPy aujourd'hui.
   **[PARTIAL — l'utilitaire existe, il n'est simplement jamais appelé]**
10. **Orchestration HPC multi-cluster / failover absente.** Recherche
    `grep -ri "failover\|multi.cluster"` sur tout `src/acf/` : **zéro
    résultat**. `hpc_connector` (vérifié) gère une connexion HPC à la
    fois, pas de bascule automatique entre clusters. **[MISSING]**
11. **Ingestion temps réel (streaming) satellite/radar absente.**
    Vérifié directement : `src/acf/data/streaming.py::StreamingEngine
    .get_stream_status()` retourne
    `"status": "NOT_STREAMING_NO_CONNECTION_ESTABLISHED"`,
    `"is_real_data": False` ; `src/acf/monitoring/
    realtime_monitor.py::GlobalRealtimeMonitor.start_monitoring_loop()`
    fait bien basculer un drapeau `is_active`, mais ne démarre aucune
    boucle réelle (pas de thread/tâche asyncio), et
    `sync_status = "NOT_SYNCHRONIZED_NO_DATA_SOURCE_CONNECTED"` reste
    inchangé. Les ingesteurs `satellite_ingestor.py`/`radar_ingestor.py`
    existent mais n'ont, eux non plus, aucune connexion de flux réelle
    branchée. **[MISSING]**

**Modèles NWP (§0-1 de l'architecture cible)**

12. **AROME/ALADIN/ARPEGE : lecture bout-en-bout réelle impossible
    dans cet environnement.** Les 3 adaptateurs existent
    (`src/acf/models/{arome,aladin,arpege}/`), mais leur backend FA
    réel dépend d'`epygram`, **non installé dans cet environnement**
    (`EPYGRAM_AVAILABLE=False`, confirmé par
    `reports/ACF_MASTER_AUDIT_v2.md` ligne 711-720) — leur `read()` ne
    peut exercer qu'un repli honnête ici. À l'inverse, WRF/ICON/
    OpenIFS/IFS (les 4 adaptateurs ajoutés ensuite) utilisent des
    dépendances réellement installées (`xarray`/`netCDF4`/`cfgrib`) et
    lisent un vrai fichier de bout en bout — vérifié : les 7 modèles
    cibles de l'architecture (ARPEGE/AROME/ALADIN/WRF/ICON/IFS/
    OpenIFS) ont bien chacun un module dans `src/acf/models/` ou
    `src/acf/models/implementations/` aujourd'hui (ce point précis du
    gap-map original est donc résolu), mais 3 des 7 restent
    non-exerçables de bout en bout **dans cet environnement précis**
    faute de dépendance installée. **[PARTIAL — dépendance
    d'environnement, pas un manque de code]**

**Total chantier 3 : 12 items.**

---

## Synthèse chiffrée

| Chantier | Items vérifiés restants |
| --- | --- |
| 1. Audit fabrication/duplication post-`model4d` | **1** |
| 2. Câblage GUI ESOC | **13** |
| 3. Feuille de route globale (architecture cible v1.0) | **12** |
| **Total global** | **26** |

Aucun de ces 26 items n'est une estimation — chacun cite un fichier et
une ligne (ou une commande `grep` reproductible) vérifiés à la date de
ce document sur le commit `2babda0` de `develop`.

---

## Ce que cette passe ne couvre pas (limites honnêtes de ce document)

Cette liste de 26 items est un **plancher vérifié**, pas un plafond.
Compte tenu de l'échelle du dépôt (~1400 fichiers `src/acf`, ~9366
lignes rien que pour l'audit v2, ~223 documents sous `docs/`), cette
passe n'a **pas** :

- Ré-audité intégralement les 38 couches de
  `ACF_ARCHITECTURE_TARGET_GAP_MAP.md` ligne par ligne comme l'a fait
  l'audit initial du 2 septembre — seuls les points explicitement
  signalés MISSING/PARTIAL par ce document et par les mises à jour de
  `ACF_MASTER_AUDIT_v2.md` ont été re-vérifiés dans le code réel.
- Relu les ~223 fichiers `docs/*.md` un par un (les ~150 documents
  "certificat"/"rapport de sprint" déjà signalés comme aspirationnels
  par `ROADMAP.md` n'ont pas été rouverts individuellement).
- Ré-exécuté la suite de tests : `pytest` n'est pas installé dans cet
  environnement d'exécution (`ModuleNotFoundError` confirmé) — le
  dernier relevé cité (4466 passed / 18 skipped / 0 failed) est celui
  du dernier commit de `reports/ACF_MASTER_AUDIT_v2.md`, pas une
  ré-exécution de cette session.
- Vérifié en profondeur les domaines `aviation/`, `climate/`
  (au-delà des 3 docstrings déjà corrigés listés dans l'audit),
  `hydrology/`, `cryosphere/` — ces zones sont mentionnées comme
  "bien fournies" par le gap-map mais n'ont pas fait l'objet d'une
  nouvelle lecture ligne par ligne dans cette passe.

Tout gap réel dans ces zones non couvertes reste donc possible et
n'est **pas** implicitement déclaré "clos" par son absence de cette
liste — il est simplement **non vérifié dans cette passe**.

---

*Aucune modification de code n'a été effectuée pour produire ce
document — tâche d'audit et de comptage uniquement, conformément à la
consigne.*
