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

Reste non fait, documenté honnêtement dans le docstring de la classe :
`FORECAST_MODULES` ne contient encore que `confidence`, un scalaire fourni
de l'extérieur — pas encore le vrai spread d'ensemble ou le désaccord
inter-modèles (`ai/ensemble/`, `visualization/ai_forecast_center/
model_consensus_engine.py`, non branchés). Pas de dimension spatiale
(2D/3D/4D) — le moteur reste scalaire/ponctuel.

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
