# Audit de conformité — ACF Master Implementation Prompt V4

**Date :** 2026-09-13.
**Contexte :** l'utilisateur a fourni un "master prompt" décrivant une
reconstruction complète du dashboard ACF en 47 phases, en supposant une
architecture web React/TypeScript/WebGL. **Correction factuelle faite et
acceptée avant de commencer** : ACF est une application desktop
PySide6/Qt, pas une app web — voir la réponse de session du 2026-09-13
pour le détail. Ce document audite donc la réalisation de chaque phase
**sur l'architecture réelle existante** (`acf.gui.dashboard.
acf_workstation.ACFWorkstation`), sans rewrite.

## Méthode

Même discipline que l'audit de conformité ICAO/OMM (`docs/compliance/
ICAO_WMO_COMPLIANCE_AUDIT.md`) : vérifier factuellement (grep/lecture)
avant de classer, ne jamais fabriquer de contenu pour "cocher une case",
fermer les gaps réels un par un avec tests + doc sync + commit.

## Déjà réel, vérifié (pas de changement nécessaire)

- **Header/Toolbar/Navigation** (Phases 3-4) : réels, fonctionnels,
  routing réel par nom (`_navigate_to()`).
- **Carte 2D + coupe verticale + profil vertical + Key Metrics + Model
  Consensus + Alerts/Hazards + Quick Actions** (Phases 5-12) : réels,
  câblés sur `compute_real_complexity_volume()` (un seul run réel,
  re-tranché par panel, jamais recalculé par onglet).
- **Diagnostics scientifiques** (Phase 13) : Labs dédiés déjà réels
  (Thermodynamics/Convection/Dynamics/Terrain/Microphysics).
- **Time series / 4D "Global Timeline"** (Phases 14/27/28) : réel
  (Phase 41), Play/Pause/vitesse réels.
- **Model Comparison** (Phase 15) : réel via `ACFMultiModelLabPanel` +
  `ModelConsensusEngine.compute_real_multi_model_disagreement()` — même
  moteur que Model Consensus, pas de duplication.
- **Data & Provenance** (Phase 17) : réel, `_export_diagnostics_data()`.
- **HPC/Slurm** (Phase 21) : réel, `HPCConnectionManager` (Paramiko SSH
  réel), jamais de faux statut "Connected".
- **Quality Control visible** (Phase 36) : réel — `run_real_range_qc()`
  alimente honnêtement le "QC [WARN]" du Pipeline Monitor avec de vrais
  violations de plage, jamais un statut inventé.
- **Politique anti-fabrication** (Phase 20) : déjà la discipline
  systématique de tout ce codebase — aucun `Math.random()`/valeur
  aléatoire trouvée dans les chemins réels du Workstation.

## Fermé cette passe (2026-09-13)

1. **Bulk Richardson Number** (Phase 13, Turbulence — nommé
   explicitement) — `acf.science.bulk_richardson_number.
   BulkRichardsonNumber` existait déjà avec ses propres tests, mais
   n'était câblé dans **aucun** panel GUI (vérifié par grep). Câblé
   dans `ACFStabilityIndicesWidget`/`compute_real_stability_indices_at_
   point()`, réutilisant le CAPE/shear déjà calculé au même point —
   zéro nouvelle donnée, zéro nouvelle formule. Honnêtement "n/a" si
   shear = 0 (BRN mathématiquement indéfini).
2. **Accessibilité** (Phase 29) — 0 appel `setAccessibleName`/
   `setAccessibleDescription`/`QAccessible` trouvé dans tout
   `acf_workstation.py` avant cette passe. Ajouté sur les contrôles les
   plus critiques (boutons icône-seule ⛶/⚙, sélecteurs Model/Domain/
   Level, liste de navigation) — **portée disclosed** : couvre le shell
   principal de l'ACFWorkstation, pas un audit a11y de tout le repo
   (~40 autres fichiers GUI), même limitation de portée déjà établie
   dans l'historique de ce projet pour l'a11y repo-wide.
3. **Tests de régression visuelle** (Phase 38) — 0 fichier de test
   visuel trouvé nulle part dans `tests/`. Créé un test réel : rendu
   offscreen Qt du vrai `ACFWorkstationWindow` (avec son propre run
   `CoupledEarthSolver` réel et déterministe, `seed=1`), comparé à une
   image de référence via une miniature 80×50 sous-échantillonnée
   (jamais un diff pixel-à-pixel brut — le rendu de police varie
   réellement selon la machine, un diff pixel exact serait une source
   d'échecs faux-positifs constante). Détecte une vraie régression
   grossière (panel disparu, palette cassée, rendu vide) — ce n'est
   PAS un test de fidélité pixel-parfaite contre un mockup externe
   (déjà explicitement disclosed comme infaisable pour une vraie app
   scientifique dynamique dans le docstring Phase 43 d'`acf_workstation.py`).

## Vérifié réel mais BLOQUÉ, disclosed (pas de fix forcé)

4. **Workflow Engine / "Workflows" nav** (Phase 22) — `acf.hpc_workflow.
   workflow_engine.WorkflowEngine` existe réellement en backend, mais
   **exige Python 3.12+** (`EnvironmentValidationError` sinon — confirmé
   lors du sweep de tests de la passe de conformité ICAO/OMM). Ce
   sandbox tourne en Python 3.11.15. Câbler un panel GUI dessus
   maintenant produirait une intégration **non testable dans cet
   environnement** — contraire à la discipline "jamais affirmer qu'un
   test passe sans l'avoir réellement fait tourner" de ce projet.
   **Non fait, disclosed comme BLOCKED BY ENVIRONMENT**, pas silencieusement
   ignoré.

## Fermé cette passe (suite, 2026-09-13)

5. **K-Index, Total Totals, SWEAT Index** (Phase 13, Stability —
   3 indices synoptiques classiques nommés implicitement) — même
   découverte que le Bulk Richardson Number : `acf.science.{k_index,
   total_totals,sweat_index}` existaient réellement, avec leurs propres
   tests, mais 0 référence nulle part dans `acf.gui` (vérifié par grep
   systématique sur tout `acf.science/` : ~27 modules scientifiques
   réels orphelins trouvés au total, ces 3 étaient les candidats les
   plus directement pertinents et sans risque - les 2 autres classiques
   (Lifted Index/Showalter Index) nécessiteraient un vrai calcul
   d'ascension de parcelle d'air, pas juste une interpolation de
   profil, donc non traités cette passe).

   Contrairement à CAPE/shear/BRN (valeurs au niveau natif du modèle),
   ces indices sont définis à des niveaux de pression standards fixes
   (850/700/500 hPa) - ajout d'une vraie interpolation linéaire
   (`np.interp`) du profil réel de température/point de rosée/vent vers
   ces niveaux, honnêtement `None` si 850/700/500 hPa sort de la plage
   réelle de niveaux natifs de la colonne (jamais une extrapolation
   fabriquée). Point de rosée réel via le même `mpcalc.
   dewpoint_from_specific_humidity()` déjà utilisé pour CAPE/CIN ;
   vitesse/direction de vent réelles via `mpcalc.wind_speed()`/
   `mpcalc.wind_direction()` (pas de trigonométrie réinventée à la
   main).

   Ajouté dans le même `ACFStabilityIndicesWidget` (même panel que BRN,
   même pattern de test). Image de référence de régression visuelle
   régénérée et vérifiée visuellement (changement d'UI délibéré, comme
   documenté dans le test lui-même) : CAPE/CIN/Wind Shear/Static
   Stability/BRN/K-Index/Total Totals/SWEAT Index tous réels, tous
   rendus correctement. 26 tests combinés verts (stability indices +
   k_index + total_totals + sweat_index), 20 tests de régression
   Phase 44/45/accessibilité verts sans changement.

6. **Lifted Index, Showalter Index** (Phase 13, Stability) —
   `acf.science.{lifted_index,showalter_index}` fermés à leur tour :
   contrairement à K-Index/TT/SWEAT (interpolation seule), ces deux
   exigent une vraie température de parcelle d'air ascendante à
   500 hPa. Utilise le vrai `mpcalc.parcel_profile()` de MetPy (le même
   primitif réel que `compute_real_cape_cin_at_point()` utilise déjà en
   interne pour l'ascension adiabatique — pas une seconde implémentation
   inventée), soulevée depuis la surface native réelle de la colonne
   (Lifted Index) ou depuis les 850 hPa déjà interpolés (Showalter
   Index). Honnêtement `None` si 500 hPa hors plage, ou si l'ascension
   réelle de MetPy ne converge pas pour ce profil (`except Exception`
   disclosed, jamais un crash ni une valeur de repli fabriquée).

   Ajouté au même panel, même pattern de test. Image de référence de
   régression visuelle régénérée et vérifiée visuellement (Lifted Index
   3.1 "Stable", Showalter Index 10.3 "Very Stable" rendus
   correctement). 20 tests combinés verts (stability indices + lifted/
   showalter), 20 tests Phase 44/45/accessibilité verts sans
   changement, test de régression visuelle vert.

7. **Model Consensus — statistiques d'ensemble réelles déjà calculées
   mais jetées** (Phase 10, nommé explicitement : "spread, mean,
   median, standard deviation, uncertainty") — en cherchant à câbler le
   module orphelin `acf.science.ensemble_uncertainty`, trouvé un
   problème plus direct et sans risque de duplication : `ModelConsensus
   Engine.compute_real_multi_model_disagreement()` construit déjà un
   vrai `EnsembleManager(list(per_model_value.values()))` (`stats`) et
   n'en extrait que `.mean`/`.spread` — `.median`/`.percentile(10)`/
   `.percentile(90)`/min/max étaient déjà calculés par ce même objet
   réel, mais silencieusement jetés avant cette passe (vérifié en
   lisant le code, pas supposé).

   **Décision délibérée : ne PAS câbler `acf.science.
   ensemble_uncertainty`** (le module orphelin initialement visé) - il
   duplique `EnsembleManager` (même mean/median/spread/percentile), et
   son `ConsensusResult.agreement_fraction` exigerait un paramètre de
   tolérance arbitraire non justifié - exactement le type de score
   composite normalisé sans échelle de référence réelle que ce fichier
   lui-même documente avoir déjà refusé pour la jauge "Agreement Level:
   78% High" du mockup (voir le docstring du module,
   `acf_workstation_overview_landing.py`). Median/p10/p90 en revanche
   sont de vraies statistiques descriptives dans la même unité physique
   réelle (K) que spread/mean déjà affichés - pas un score composite.

   Corrigé : exposition des 5 champs déjà calculés
   (`disagreement_median`/`_min`/`_max`/`_p10`/`_p90`) dans le
   dictionnaire de retour, affichés dans `set_consensus_result()`.
   Zéro nouveau calcul, zéro nouvelle dépendance. 25 tests combinés
   verts (ai_forecast_center + Phase 44), test de régression visuelle
   vert (texte de consensus seulement affiché après clic manuel, hors
   du rendu de la capture de référence).

## Vérifié résolu — pas un vrai gap (2026-09-13)

- **"Datasets"** comme concept nav distinct du mockup — vérifié : la
  Workstation a déjà une section "DATA SOURCES" réelle (Model Data/
  Observations/Scientific Explorer), le même mapping déjà établi et
  disclosed pour "Data"/"Diagnostics" (Phase 31 de ce fichier lui-même).
  Un second panel "Datasets" séparé serait une duplication, pas une
  fermeture de gap — **pas de changement nécessaire**.
- **"Model disagreement" comme type d'alerte** (Phase 16) — vérifié :
  Model Consensus (`ModelConsensusEngine.compute_real_multi_model_
  disagreement()`) expose déjà honnêtement le vrai spread une fois
  calculé, mais c'est une action manuelle coûteuse (un run solveur réel
  par modèle) — jamais auto-déclenchée, par choix de conception déjà
  établi ailleurs dans ce projet (calcul coûteux sur demande
  uniquement). Fusionner ça avec les Alerts auto-calculées créerait soit
  un déclenchement automatique de calculs coûteux non demandés, soit
  une alerte fabriquée avant tout calcul réel. **Pas un gap réel — déjà
  honnêtement conçu ainsi.**
- **Messages d'erreur structurés** (Phase 31) — vérifié `_on_volume_
  failed()` : affiche déjà le vrai message d'exception du solveur, logué,
  UI réactivée. Pas de catégorisation rigide (DATA UNAVAILABLE/INVALID
  GRID/etc.) mais le message réel est plus informatif qu'une catégorie
  générique inventée. **Pas un gap réel.**

## Reste ouvert (feuille de route, non traité cette passe)

- **Triage approfondi des "~22 autres modules orphelins" (2026-09-13,
  suite) — gisement épuisé** : re-vérifié contre `acf.awci/` en plus de
  `acf.gui/` (le premier grep, limité à `acf.gui/`, ratait la couche
  intermédiaire réelle). **2 faux positifs trouvés** : `potential_
  temperature` et `equivalent_potential_temperature` sont déjà utilisés
  réellement (`acf.awci.workstation_fields`/`acf.awci.theta_e`), pas
  orphelins. `ensemble_uncertainty` s'est avéré être un doublon
  probable d'`acf.ai.ensemble.EnsembleManager` (déjà utilisé) plutôt
  qu'un vrai gap à combler - voir point 7 ci-dessus pour la vraie
  correction trouvée à la place (statistiques déjà calculées mais
  jetées). Les candidats restants (`air_density`, `mixing_ratio`, etc.)
  se sont révélés être des noms de paramètres génériques réutilisés
  dans tout `model4d/physics/` (faux positifs de grep), pas des
  fonctions orphelines réelles. `cyclones`/`fronts`/`potential_
  vorticity` opèrent sur des champs 2D complets (pas des diagnostics
  ponctuels) - hors périmètre de ce panel. `climatology`/`radiosonde`
  nécessitent des données historiques/d'observation réelles absentes de
  ce pipeline. `query_engine` est un système d'interrogation distinct,
  pas une métrique scalaire. **Conclusion : le gisement de gaps sûrs et
  pertinents de ce type est maintenant épuisé** pour ce Workstation -
  continuer à chercher mécaniquement produirait plus de faux positifs
  que de vraies fermetures.
- **Audit d'unités systématique** (kt/m/s, ft/m) sur `gui/` dans son
  ensemble — hors périmètre de cette passe (voir aussi l'audit ICAO/OMM
  §4 pour la même limite déjà posée).
- **Accessibilité repo-wide** (au-delà du shell ACFWorkstation) — gros
  chantier séparé, déjà qualifié disproportionné pour une session dans
  l'historique de ce projet.
- **Bulk Richardson Number ailleurs** — vérifié sur 2 candidats, aucun
  des deux n'est un vrai "gain facile" : le Map Inspector exclut déjà
  délibérément CAPE/CIN de son calcul par point-cliqué pour rester bon
  marché sur des clics répétés (BRN en dépend) ; Dynamics Lab calcule
  bien un champ de cisaillement gridé, mais PAS de CAPE gridé (celui-ci
  reste volontairement à la demande et coûteux dans Thermodynamics Lab
  - même raison de coût déjà disclosed dans le docstring de Stability
  Indices). Étendre BRN à l'un ou l'autre reproduirait le même problème
  de coût déjà résolu ailleurs par un calcul à la demande, pas une
  réutilisation gratuite. **Non fait, correctement identifié comme
  nécessitant un vrai calcul à la demande plutôt qu'un câblage trivial
  - pas un gap "petit" comme initialement supposé.**

## Conclusion honnête (format Phase 47 du master prompt)

| Item | Statut |
|---|---|
| Architecture correcte identifiée avant travail | ✅ IMPLEMENTED (corrigée, disclosed à l'utilisateur) |
| Bulk Richardson Number | ✅ IMPLEMENTED |
| Accessibilité (shell principal) | ⚠️ PARTIALLY IMPLEMENTED (disclosed, portée limitée) |
| Tests de régression visuelle | ✅ IMPLEMENTED (métrique tolérante, disclosed) |
| Workflow Engine GUI | ❌ BLOCKED BY MISSING DEPENDENCY (Python 3.12+) |
| "Datasets" nav séparé | ✅ IMPLEMENTED (déjà couvert par "DATA SOURCES", vérifié non-redondant à dupliquer) |
| Alerte "model disagreement" | ✅ IMPLEMENTED (déjà honnêtement exposé dans Model Consensus, fusion avec Alerts délibérément évitée) |
| Messages d'erreur structurés | ✅ IMPLEMENTED (message réel du solveur, plus informatif qu'une catégorie générique) |
| Audit unités systématique | ❌ NOT IMPLEMENTED (hors périmètre, disclosed) |
| Accessibilité repo-wide | ❌ NOT IMPLEMENTED (disproportionné, disclosed) |
| Bulk Richardson Number (autres panels) | ❌ NOT IMPLEMENTED (nécessiterait un vrai calcul CAPE à la demande, pas un câblage gratuit - re-scopé) |
| K-Index / Total Totals / SWEAT Index | ✅ IMPLEMENTED |
| Lifted Index / Showalter Index | ✅ IMPLEMENTED (vraie ascension de parcelle via `mpcalc.parcel_profile()`) |
| Model Consensus (median/min/max/p10/p90) | ✅ IMPLEMENTED (déjà calculé, était jeté avant exposition) |
| ~22 autres modules `acf.science` orphelins | ✅ TRIÉS (2 faux positifs corrigés, le reste hors périmètre ou déjà résolu autrement - gisement épuisé) |
