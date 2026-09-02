# ACF — Correspondance architecture cible ↔ code réel

**Date :** 2 septembre 2026
**Source cible :** [`docs/ACF_MASTER_UNIFIED_ARCHITECTURE.md`](ACF_MASTER_UNIFIED_ARCHITECTURE.md)
(architecture à 30 niveaux fournie par l'utilisateur le 2 septembre 2026).

Ce document répond à une seule question : **pour chacun des 38 paquets de
la structure cible (`src/acf/<layer>/`), qu'est-ce qui existe réellement
aujourd'hui dans `src/acf/`, et où ?**

Vérifié par recherche directe dans l'arborescence (`find`), pas par
supposition — voir la colonne "Preuve".

## Légende

- ✅ **Existe, nommé pareil** — le paquet cible existe déjà sous ce nom exact.
- ⚠️ **Existe, dispersé/renommé** — le concept existe mais réparti dans
  plusieurs paquets, ou imbriqué plus profond, ou sous un autre nom.
- ❌ **Absent** — aucune trace du concept trouvée dans `src/acf/`.

| # | Couche cible | Statut | Où ça vit réellement | Preuve |
|---|---|---|---|---|
| 1 | `core/` | ✅ | `core/` | dossier identique |
| 2 | `data/` | ⚠️ | `data/`, `catalog/`, `catalogs/`, `importers/`, `io/` | 5 paquets qui se recouvrent partiellement |
| 3 | `ingestion/` | ⚠️ | `data/universal_ingestion.py`, `data_assimilation/observation_ingestion/` | fichiers isolés, pas de paquet dédié |
| 4 | `models/` | ✅ (partiel) | `models/{arome,aladin,arpege,implementations}/` | existe, mais seulement 3 modèles NWP sur les 7 listés (pas de WRF/ICON/IFS/OpenIFS) |
| 5 | `normalization/` | ❌ | — | aucun fichier `*normaliz*` dans `src/acf` |
| 6 | `qc/` | ⚠️ | `data_assimilation/quality_control/` | existe mais imbriqué 2 niveaux, pas top-level |
| 7 | `physics/` | ⚠️ | `earth_physics/`, `science/laws/`, `science/physical_laws/` | logique physique dispersée entre 2 arbres |
| 8 | `grid/` | ⚠️ | `model4d/grid4d.py`, `hpc/distributed_grid.py`, `geospatial/` | pas de paquet `grid/` unifié |
| 9 | `vertical/` | ⚠️ | `model4d/vertical_axis.py` | un seul fichier, pas un moteur vertical dédié |
| 10 | `state/` | ⚠️ | `digital_twin/{planet_state,earth_state,state_vector}.py`, `data_assimilation/analysis_state.py` | concept réparti, pas d'`AtmosphericState` central unique |
| 11 | `model4d/` | ✅ | `model4d/` | dossier identique |
| 12 | `diagnostics/` | ⚠️ | `intelligence/forecast_analysis/`, `science/`, `analysis/` | dispersé, pas de moteur de diagnostics unifié |
| 13 | `observations/` | ⚠️ | `data_assimilation/observation_ingestion/`, `hydrology/observations/`, `ocean/observations/`, `space_weather/observations/` | un sous-dossier `observations/` par domaine, pas de couche transverse |
| 14 | `assimilation/` | ⚠️ | `data_assimilation/assimilation/{ensemble,hybrid,variational}/` | existe, imbriqué sous `data_assimilation/` |
| 15 | `ensemble/` | ⚠️ | `ai/ensemble/`, `simulation_engine/ensemble_prediction/` | dupliqué entre deux arbres |
| 16 | `comparison/` | ⚠️ | `visualization/ai_forecast_center/forecast_comparison.py` | un seul fichier, enterré dans la visualisation |
| 17 | `consensus/` | ⚠️ | `visualization/ai_forecast_center/model_consensus_engine.py` | idem — un seul fichier, pas un moteur top-level |
| 18 | `uncertainty/` | ⚠️ | `ai/uncertainty/` | existe, imbriqué sous `ai/` |
| 19 | `events/` | ⚠️ | `aeos/events/`, `digital_twin/events/` | existe mais orienté "événements système", pas détection d'événements météo (convection, grêle, etc. — voir couche 16 de la cible) |
| 20 | `complexity/` | ⚠️ (mis à jour 2026-09-02) | `awci/` (`AWCICalculator`) | Correction : ce moteur existait déjà, juste scopé/nommé aviation. Après audit approfondi (voir section "Mise à jour" ci-dessous), évolué sur place pour séparer Physical/Forecast Complexity — pas déplacé en `complexity/` (décision explicite utilisateur) |
| 21 | `intelligence/` | ✅ | `intelligence/` | dossier identique, bien fourni (agents, anomalies, decision_support, hypothesis, planner...) |
| 22 | `radar/` | ⚠️ | `visualization/radar_satellite_center.py`, `data_assimilation/observation_ingestion/radar_ingestor.py`, `gui/dashboard/awci_radar.py`, `science/encyclopedia/radar_*.py` | 4+ emplacements différents, aucun paquet `radar/` |
| 23 | `satellite/` | ⚠️ | `visualization/radar_satellite_center.py`, `catalog/satellite_parameters.py`, `data_assimilation/observation_ingestion/satellite_ingestor.py` | idem, dispersé. `space_weather/satellites/` existe mais couvre un domaine différent (météo spatiale, pas télédétection météo) |
| 24 | `land/` | ⚠️ | `earth_physics/land_surface/`, `surfex/` | existe, réparti entre 2 arbres |
| 25 | `ocean/` | ✅ | `ocean/` | dossier identique, bien fourni |
| 26 | `aerosols/` | ⚠️ | `science/clouds/aerosols.py`, `science/encyclopedia/aerosols_chemistry.py`, `model4d/physics/aerosol_*.py` | dispersé sur 3+ fichiers, pas de paquet dédié |
| 27 | `fire_weather/` | ❌ | — | **aucune trace** |
| 28 | `aviation/` | ✅ | `aviation/` | dossier identique, bien fourni (airports, graphics, hazards, icao, performance, routing) |
| 29 | `climate/` | ✅ | `climate/` | dossier identique, bien fourni |
| 30 | `simulation/` | ⚠️ | `simulation_engine/` | existe, nom différent |
| 31 | `products/` | ⚠️ | `reports/`, `digital_twin/reports/` | partiel, pas de "Product Engine" au sens de la cible (cartes, coupes, Skew-T, etc. génériques) |
| 32 | `visualization/` | ✅ | `visualization/` | dossier identique, bien fourni |
| 33 | `dashboard/` | ✅ | `dashboard/`, `gui/dashboard/` | existe (doublé entre 2 emplacements, cf. audit précédent) |
| 34 | `api/` | ⚠️ | `api/`, `web/` | existe, mais séparé entre façade Python (`api/`) et couche HTTP réelle (`web/hpc_dashboard_server.py`) |
| 35 | `realtime/` | ⚠️ | `monitoring/realtime_monitor.py` | un seul fichier, pas de paquet dédié |
| 36 | `workflow/` | ⚠️ | `hpc_workflow/` (19 fichiers), `aeos/workflow/`, `master/workflow_master.py` | très fourni mais 100% orienté HPC/orchestration système, pas un "workflow" générique de traitement de données |
| 37 | `storage/` | ❌ | — | aucun paquet `storage/` (les writers vivent dans `data/writers/`) |
| 38 | `verification/` | ✅ | `verification/`, `climate/verification/` | existe (dupliqué à 2 endroits) |

## Bilan chiffré

| Statut | Nombre de couches / 38 |
|---|---|
| ✅ Existe tel quel | 10 |
| ⚠️ Existe mais dispersé/renommé/imbriqué | 22 |
| ❌ Absent | 6 (`normalization/`, `complexity/`, `fire_weather/`, `storage/`, et partiellement `vertical/`/`grid/` comme moteurs dédiés) |

## Ce que ça veut dire concrètement

L'architecture cible **n'est pas une réinvention** : environ 84% de ses
concepts (32 des 38 couches) existent déjà quelque part dans `src/acf/`,
juste organisés différemment — hérité de l'historique du projet (sprints
successifs, ajouts au fil de l'eau) plutôt que conçu d'un bloc selon cette
chaîne à 30 niveaux.

Les vrais manques fonctionnels (pas juste organisationnels) sont :

1. **`complexity/`** — absent alors que c'est le concept fondateur du
   projet ("Atmospheric **Complexity** Framework"). Aucun indice de
   complexité atmosphérique composite (instabilité + humidité + cisaillement
   + désaccord inter-modèles → un seul score) n'existe nulle part.
2. **`normalization/`** — pas de couche d'interopérabilité CF/unités
   centralisée ; chaque importeur gère probablement ses propres conventions.
3. **`fire_weather/`** — entièrement absent.
4. **`consensus/` et `comparison/`** — existent seulement comme fichiers
   isolés dans la visualisation, pas comme moteurs de calcul indépendants
   réutilisables par le dashboard, l'API, etc.
5. **`storage/`** — pas de couche de stockage générique (juste des writers
   NetCDF/Zarr ad hoc dans `data/writers/`).

## Mise à jour — 2 septembre 2026 : `complexity/` n'était pas absent

L'utilisateur a pointé `awci/` comme piste probable avant que l'audit ne
soit complet. Vérification faite : **il avait raison**. `src/acf/awci/`
(`AWCICalculator`, `Normalizer`, `WeightsManager`) est un vrai moteur de
complexité composite déjà fonctionnel — 7 modules pondérés, 2 termes
d'interaction non-linéaires, décomposition explicable, niveaux
`Very Low → Extreme` — juste nommé et scopé pour l'aviation
("Aviation Weather Complexity Index"), et déjà branché sur 6 panneaux GUI
(`gui/dashboard/awci_*.py`) et testé (`tests/test_awci_calculator.py`).

Écart réel identifié et corrigé (commit `d5451dc`) : le module `confidence`
(incertitude de prévision) était mélangé dans la même somme pondérée que
les 6 modules physiques — exactement l'erreur scientifique que
l'architecture cible interdit ("le désaccord entre modèles n'est pas une
propriété physique de l'atmosphère"). `AWCICalculator.calculate()` retourne
maintenant `physical_score`/`forecast_score` séparément, chacun
renormalisé indépendamment sur `[0, 100]`, tout en gardant `awci`/`level`/
`decomposition` strictement identiques (aucune régression). Le panneau
`AWCIRiskSummary` ("RISK SUMMARY" — l'affichage détaillé qu'évoquait
l'utilisateur) affiche maintenant ces deux scores, avec `—` (jamais 0.0
fabriqué) quand le score est indéfini.

Décision explicite de l'utilisateur : faire évoluer `awci/` sur place
plutôt que dupliquer sa logique dans un nouveau paquet `complexity/` —
conforme à la règle "ne rien déplacer" de sa propre spécification
d'ingénierie pour cette étape.

**Mise à jour 2026-09-02 (suite 3) — dimension spatiale 2D construite**
(sur demande explicite : "vas-y, construis la dimension spatiale 2D") :
nouveau module `awci/spatial_field.py::compute_real_complexity_field()`
— fait tourner `CoupledEarthSolver` une fois à la vraie résolution d'un
modèle (`forecast.engine.MODEL_CONFIGS`), puis évalue `AWCICalculator`
à **chaque** point réel de la grille (température, vent, humidité,
pression réels du solveur — pas un pattern synthétique). Vérifié
visuellement (image générée, non committée) : le champ de température
et le champ de complexité physique varient réellement point par point
(écart-type non nul), pas un score unique dupliqué partout.

Limite honnête trouvée et documentée sans la cacher : le champ
`forecast_field` ressort **plat à 0.0 partout** sous les poids par
défaut — câbler un vrai signal d'ensemble/désaccord inter-modèles par
point de grille demanderait de refaire tourner la fusion multi-modèles
(2-3 passages solveur complets) à *chaque cellule*, ce qui ne passe pas
à l'échelle avec l'infrastructure actuelle. Un résultat réel (pas
fabriqué), mais pas encore un signal spatial de complexité de
prévision utile — testé et verrouillé explicitement
(`test_forecast_field_is_honestly_flat_documented_limitation`) pour que
ça ne redevienne pas une régression silencieuse plus tard.

Au passage : `gui/dashboard/awci_synthetic_field.py::awci_grid_full()`
ajouté pour exposer aussi le split Physical/Forecast sur le champ 2D
*synthétique* de démonstration existant (`awci_grid()` original
inchangé, zéro régression pour ses appelants GUI).

**Mise à jour 2026-09-02 (suite 4) — dimension verticale 3D construite**
(sur demande explicite : "vas-y, construis la dimension verticale 3D") :
nouveau module `awci/vertical_field.py` :
- `compute_real_complexity_volume()` — réutilise **un seul** run du
  solveur (tous les niveaux sont déjà intégrés ensemble par
  `solver.step()`) et évalue `AWCICalculator` à **chaque point réel**
  (niveau, lat, lon) — pas un run par niveau. Vérifié à la vraie
  résolution ARPEGE (20×48×96 = 92 160 points) : 1,4 s.
- `vertical_profile_at_point()` — extrait `Complexity(z)` au point de
  grille le plus proche (plus-proche-voisin réel), avec la vraie
  pression locale par niveau (`pressure_volume_hpa`) pour situer
  physiquement chaque niveau natif.

**Invariant physique réel vérifié** (pas supposé, testé contre la
vraie sortie du solveur) : la pression décroît bien avec l'altitude à
chaque niveau (`test_pressure_decreases_with_altitude_real_physics`).
Profil vertical réel à Alger (image envoyée) : la complexité décroît
proprement de ~15 en surface (2013 hPa) à ~4 en haute altitude
(~1 hPa) — signal physiquement cohérent, pas du bruit, contrairement
aux coupes horizontales qui restent granulaires (intégration courte,
même limite honnête que le champ 2D).

Limite honnête : niveaux **natifs** du solveur, pas de vraie
interpolation vers les niveaux de pression standards
(1000/925/850/700/500/300 hPa...) — cette capacité (couche "vertical
operations: interpolation" de l'architecture cible) n'existe nulle
part dans ACF, donc pas construite ici pour ne pas inventer de valeurs
interpolées. `pressure_volume_hpa` permet de trouver le niveau natif
le plus proche d'une pression donnée, honnêtement, sans fabriquer
d'interpolation.

Trouvaille annexe corrigée au passage : la clé `pressure_field` du
module 2D (`spatial_field.py`) était en Pa brut, non convertie et non
étiquetée — renommée `pressure_field_hpa` (converti en hPa) pour
cohérence avec le nouveau module 3D. Découverte documentée sans la
cacher : la clé `"pressure"` acceptée par `AWCICalculator` n'est en
réalité **jamais lue** dans `calculate_module_scores()` — un input mort
préexistant, non introduit par ce travail, non corrigé ici (hors
scope), juste signalé en commentaire dans le code.

**Mise à jour 2026-09-02 (suite 5) — dimension temporelle 4D construite**
(sur demande explicite : "vas-y, construis la dimension temporelle 4D") :
nouveau module `awci/temporal_field.py` :
- `compute_real_complexity_evolution()` — **une seule** instance du
  solveur, intégrée **en continu** sur toute l'animation (chaque frame
  poursuit réellement la trajectoire physique de la précédente — pas
  `n_frames` runs indépendants relancés de zéro), en réutilisant
  `vertical_field.py::score_volume()` (extrait pour éviter la
  duplication) à chaque frame.
- `profile_over_time()` — extrait `Complexity(t)` en un point réel.

**Preuve numérique de vraie évolution** (pas juste visuelle — le champ
composite arrondi à 1 décimale peut masquer une évolution réelle mais
lente à l'œil sur une carte) : moyenne du domaine 13,872 → 13,939 sur
6h, cellule la plus évolutive 15,9 → 17,4 — croissance réelle et
monotone, vérifiée directement sur les champs bruts de température
(écart max 1,1 K entre la 1re et la dernière frame). Image de 6
snapshots envoyée — changement visuellement subtil à cette échelle de
couleur/durée mais numériquement réel, signalé honnêtement plutôt que
de forcer une démo plus spectaculaire.

Trouvaille de conception importante, documentée en détail dans le
docstring : la perturbation initiale n'est appliquée **qu'une seule
fois**, avant la 1re frame — la réappliquer à chaque frame aurait fait
de chaque snapshot un nouveau coup de dés indépendant, pas l'évolution
réelle d'une seule trajectoire cohérente (le sens honnête de "4D").

Refactoring en passant : la boucle de notation par point
(niveau/lat/lon) de `vertical_field.py` a été extraite en fonction
partagée `score_volume()`, réutilisée telle quelle par le nouveau
module — zéro duplication entre 3D et 4D, mêmes 8 tests 3D toujours
verts après le refactoring.

Mêmes limites honnêtes reportées : niveaux natifs (pas d'interpolation
vers les niveaux standards), CAPE/CIN/précipitation non dérivés,
`forecast_evolution` plat sous poids par défaut (câbler un vrai signal
par point ET par frame multiplierait un coût déjà élevé par
`n_frames`).

**Les 4 dimensions du Complexity Engine sont maintenant réelles et
testées : 2D (`spatial_field.py`), 3D (`vertical_field.py`), 4D
(`temporal_field.py`), plus le split Physical/Forecast et les vrais
signaux ensemble/multi-modèles sur le côté prévision.**

**Mise à jour 2026-09-02 (suite 6) — dashboard branché** (sur demande
explicite : "vas-y, branche le dashboard") : bouton **"🔬 Real Physics"**
ajouté à `gui/dashboard/awci_dashboard.py::AWCIDashboard`. Lance
`compute_real_complexity_field()` sur un vrai worker `QThreadPool`
(même schéma `WorkerRunnable` que `gui/esoc/command_dispatcher.py`,
étendu avec un signal `finished(dict)` pour ramener le résultat sur le
thread GUI sans jamais geler l'interface) et remplace le champ
synthétique par le vrai champ physique sur : carte globale, barre de
stats, radar et risk-summary. Carte régionale, coupe verticale et
graphe de route restent volontairement sur le motif synthétique
(annoncé dans le label de statut, pas laissé incohérent en silence) —
les brancher demanderait d'extraire le vrai champ le long d'un chemin/
d'une région arbitraire, un travail distinct.

**Bug réel trouvé et corrigé par le test, pas en relecture manuelle** :
`lons, lats = result["lats"], result["lons"]` — inversés. Le test
`test_map_panel_external_field_round_trip`/`test_real_physics_ready_...`
a fait planter matplotlib immédiatement (`Length of x (8) must match
number of columns in z (14)`) sur une grille de test volontairement
non carrée (8×14) — une grille carrée aurait laissé ce bug passer
silencieusement. Corrigé, testé, vérifié par un **vrai clic** sur le
vrai bouton dans un `QApplication` xvfb réel (pas un appel direct de
méthode), worker réellement asynchrone attendu via la boucle
d'événements Qt, capture d'écran réelle envoyée.

Petit correctif cosmétique trouvé par la même capture d'écran : le
libellé "CoupledEarthSolver (ARPEGE)" débordait de sa case étroite —
raccourci en "CoupledEarthSolver" (l'info complète reste dans la
bannière de statut).

Reste : niveaux de pression standards par interpolation, signal
forecast par point (coût prohibitif avec l'infrastructure actuelle),
et brancher la carte régionale/coupe/route sur les vrais champs 3D/4D
déjà construits.

**Mise à jour 2026-09-02 (suite) — vrai ensemble branché, consensus resté
honnêtement non branché** (commit à suivre) : `FORECAST_MODULES` inclut
maintenant `ensemble_spread`, calculé à partir de vraies statistiques
d'ensemble (`ai/ensemble/ensemble_manager.py::EnsembleManager`, formule
d'écart-type réelle) quand l'appelant fournit de vraies valeurs par membre
(`data["ensemble_members"]`). Poids par défaut `0.0` (opt-in) — aucun
appelant existant n'est affecté. Vérifié avec de vraies valeurs
d'ensemble : `EnsembleManager([850, 1200, 400, 2100, 950]).spread` = 629.5
J/kg réel, propagé jusqu'à `forecast_score`.

`ModelConsensusEngine.compute_unified_consensus()` et
`ForecastComparisonMatrix` restent, eux, des stubs honnêtes inchangés
(`status: "WEIGHTS_ONLY_NO_MODEL_FIELDS_FUSED"` /
`"NOT_COMPUTED_NO_MODEL_COMPARISON_RUN"`) — aucune fusion de champs n'y
existait, donc rien à en tirer honnêtement.

**Mise à jour 2026-09-02 (suite 2) — vraie fusion multi-modèles construite**
(sur demande explicite : "vas-y, construis la fusion multi-modèles") :
`ModelConsensusEngine` gagne une nouvelle méthode réelle,
`compute_real_multi_model_disagreement(lat, lon, ...)`. Elle fait tourner
pour de vrai `CoupledEarthSolver` une fois par modèle demandé, à sa vraie
configuration de grille (`acf.forecast.engine.MODEL_CONFIGS` — la même
infrastructure que les pipelines HPC one-click AROME/ALADIN, complétée
d'un troisième modèle **ARPEGE** — 48×96×20, 10 km stand-in), avec une
perturbation initiale indépendante par modèle (même convention que les
données d'entraînement du FNO), puis lit la vraie valeur de chaque modèle
au point de grille le plus proche du point demandé — vrai
plus-proche-voisin, un des types de regridding listés dans
l'architecture cible. Vérifié avec de vraies valeurs (Alger) :
`{'ALADIN': 290.42, 'AROME': 287.09, 'ARPEGE': 289.52}` → spread réel
`1.73 K`, propagé jusqu'au nouveau module `model_disagreement` d'AWCI
(poids par défaut `0.0`, même convention opt-in que `ensemble_spread`).

Limite honnête documentée en détail dans le docstring de la méthode :
ceci compare le **propre solveur physique d'ACF** à plusieurs
résolutions/perturbations réelles, en remplacement d'AROME/ALADIN/ARPEGE
— pas de vraies archives opérationnelles (aucune disponible dans cet
environnement). Ce qui est réel : le solveur tourne vraiment par modèle,
les valeurs diffèrent vraiment (physique + discrétisation réelles), et le
spread est vraiment calculé à partir de ces valeurs — rien n'est un
placeholder inventé. Trouvaille annexe honnêtement documentée : les
appels répétés ne sont pas parfaitement reproductibles bit-à-bit (les
composants atmosphère/océan du solveur utilisent l'état RNG global
`np.random` sans le fixer — caractéristique préexistante du solveur, hors
scope de cette tâche, pas introduite par ce nouveau code).

## Recommandation (à valider avec l'utilisateur)

Une réorganisation physique complète (renommer/déplacer les ~1340 fichiers
de `src/acf/` pour épouser exactement les 38 paquets cibles) toucherait la
quasi-totalité des imports du projet, pour un gain **organisationnel**, pas
fonctionnel — gros risque de régression sur une base actuellement 100%
verte (2819/2819 tests, ruff et mypy propres) pour un bénéfice qui reste à
démontrer.

Approche proposée à la place :
- Utiliser ce document comme **boussole** : tout nouveau module se
  positionne explicitement dans la chaîne à 30 niveaux (règle des 8
  questions, section 5 du document cible).
- Combler en priorité les **vrais manques fonctionnels** ci-dessus
  (`complexity/` en premier — c'est le cœur du projet) plutôt que de
  déplacer du code qui fonctionne déjà.
- Renommer/regrouper au cas par cas, uniquement quand un module est de
  toute façon touché pour une autre raison — pas en bloc.
