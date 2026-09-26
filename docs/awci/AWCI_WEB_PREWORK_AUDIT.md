# AWCI Web — Audit complet de l'existant (avant travaux)

**Date :** 2026-09-25 · **Branche :** `claude/nouvelle-session-42g700` · **Base :** `7676174`

Audit en lecture seule demandé avant le démarrage d'AWCI Web. Aucun code
de production n'a été modifié. Chaque constat ci-dessous a été établi par
lecture directe du code (méthode : lecture intégrale de chaque module,
docstrings et commentaires retirés pour isoler la logique) et, lorsque
indiqué **[exécuté]**, vérifié en exécutant réellement le code dans un
environnement Python 3.12 propre.

## 0. Périmètre scanné

Il n'existe **pas** de dossier « AWCI web » dans le dépôt. Le périmètre
AWCI réel est :

| Zone | Fichiers | Lignes | Rôle |
|---|---|---|---|
| `src/acf/awci/` | 45 (+ `data/`) | 13 445 | Moteur scientifique (calculateur, normalisation, diagnostics, champs, import modèle, archive ALADIN) |
| `src/acf/web/` | 12 | 1 355 | Backend FastAPI `/api/v1/*` + page HTML HPC |
| `src/acf/gui/dashboard/awci_*.py` | 28 | 10 303 | Dashboard desktop PySide6/matplotlib |
| Autres `awci_*` (`awci_app.py`, `gui/map/{layers,renderers}`, `visualization/widgets`, 5 × `*/awci_*_dashboard.py`, `scripts/awci`) | 11 | ~800 | Point d'entrée, couches carte, stubs |
| `docs/awci/` | 9 | ~1 100 | Audits et spécifications précédents |
| Tests AWCI + web | 110 | 17 463 | 1 177 fonctions de test |

## 1. Architecture actuelle (résumé)

```
                 ┌──────────────── Sources de données ────────────────┐
                 │ Démo synthétique (défaut)   awci_synthetic_field    │
                 │ « Real Physics »            CoupledEarthSolver       │
                 │ Archive ALADIN RESTOR       archive_field (EPyGrAM)  │
                 │ Fichier importé             model_import* (DataMgr)  │
                 │ METAR/TAF/SIGMET live       aviation.icao.live_source│
                 └───────────────────────┬────────────────────────────┘
                                         ▼
      Diagnostics physiques (theta_e, ceiling, visibility, dust, CAT, CAPE…)
                                         ▼
      AWCICalculator (14 modules, 2 interactions, normalisation min-max)
                                         ▼
          ┌──────────────────────────────┴───────────────────────┐
          ▼                                                      ▼
  Dashboard Qt (awci_dashboard.py, 3 442 l.)       FastAPI /api/v1 (complexity,
  état = attributs d'instance                       datasets, events, workstation,
                                                    models, hpc, fno)
```

Points forts réels : discipline « None plutôt que valeur inventée » dans
les diagnostics, registre de statut scientifique (`scientific_status.py`,
`diagnostic_registry.py`), régrillage conservatif correct, lecture réelle
d'une archive ALADIN via EPyGrAM, décodage METAR/TAF/SIGMET réel,
garde-fous de taille de requête côté API.

## 2. Constats critiques (bloquants pour une plateforme web opérationnelle)

### C1 — Le mode « Real Physics » n'est pas reproductible **[exécuté]**
`compute_real_complexity_field(seed=0)` appelé deux fois avec les mêmes
paramètres donne des champs de vent différents et un écart d'AWCI
jusqu'à **1,9 point**. Cause : `seed` ne perturbe que `T`, alors que
`AtmosphereModel.initialize_state()` tire `U`/`V` via `np.random.normal`
**non initialisé** (RNG global). Viole l'exigence de reproductibilité.

### C2 — « Real Physics » n'est pas une donnée réelle au sens opérationnel
L'état initial est une atmosphère standard idéalisée (T = ISA par indice
de niveau, pression de surface uniforme 1013,25 hPa **[exécuté]**, vents
= bruit gaussien, q exponentiel), intégrée 4 à 8 pas de 60–90 s. Les
libellés « AROME / ALADIN / ARPEGE » ne désignent que des configurations
de grille globale (`MODEL_CONFIGS`) — ex. « AROME » = grille 90 × 180
globale (~2°) étiquetée `resolution_km: 1.3`. Le code le déclare dans
`honest_limitation`, mais l'UI affiche « REAL PHYSICS » et l'API
`is_real_data: True`. Pour un utilisateur opérationnel, c'est trompeur.

### C3 — Le dashboard affiche par défaut des données synthétiques, parfois étiquetées « Real »
- Mode par défaut = démo analytique (`_synthetic_inputs`).
- Le tableau « AIRPORT COMPLEXITY » et le dialogue **« All Airports - Real
  AWCI »** sont calculés sur ce motif synthétique.
- La démo est physiquement incohérente : la température à FL300 vient
  d'une formule de surface (`288 − 0,55·|lat|`, ≈ 270 K au lieu de
  ≈ 230 K ISA), CIN = `80·(1 − storminess)` (maximal par temps calme).

### C4 — Absence de donnée affichée comme risque faible **[exécuté]**
- `POST /api/v1/complexity/score` avec `{}` → **200, AWCI 4,6 « Very
  Low »**. Toute variable manquante reçoit un défaut bénin silencieux
  (vent 0, T 273,15 K, confiance 100 %, …).
- Les cartes « Visibility » / « Ceiling » du dashboard affichent **0 /
  Very Low** quand le module n'est pas alimenté (score 0,0 = « pas de
  signal » dans le calculateur, mais rendu comme risque faible).
- La carte « Model Agreement » affiche **« Very High »** accord quand
  aucun multi-modèle n'est branché (« real default (perfect agreement) »),
  en contradiction avec la convention du calculateur lui-même
  (« 0.0 = no signal, not perfect agreement »).

### C5 — Libellés de danger ne correspondant pas à la grandeur calculée
| Libellé UI | Grandeur réellement affichée |
|---|---|
| « Turbulence Risk » / carte « Turbulence » | module `dynamic` = vitesse du vent normalisée (+ cisaillement si fourni) |
| « Icing Risk » / carte « Icing » / « Microphysical (icing) » | module `microphysical` = taux de précipitation normalisé |
| Couche carte « Icing » | sévérité de phase de précipitation (pluie = 0,2 même à +30 °C) |
| Nav « Model Comparison » | comparaison FL280/FL320 (pas de modèles) |
| Nav « Uncertainty » | rapport d'exécution |

Une forte pluie tropicale chaude s'affiche donc « Icing: High ».

## 3. Constats majeurs

### Science
- **M1 — `normalize_temperature` contredit sa propre documentation.** Le
  registre (`diagnostic_registry.py`) indique « les extrêmes dans les
  deux sens augmentent la complexité », mais la formule est monotone
  croissante : −30 °C → 0, +50 °C → 1. Aucune justification physique
  aviation (le givrage est à froid, la dégradation de performance à
  chaud).
- **M2 — CIN ajoute de la complexité convective** (`0,7·CAPE + 0,3·|CIN|`).
  Une forte inhibition réduit le potentiel convectif ; l'additionner
  positivement n'est pas défendable sans justification (statut
  HYPOTHESIS, non documenté comme tel dans l'effet).
- **M3 — Trois tables de classes incompatibles** pour le même indice :
  `AWCICalculator.LEVEL_THRESHOLDS` (0/20/35/50/65/85),
  `awci_risk_summary._BANDS` (pas de « Very Low », 0–35 = « Low »),
  seuils codés en dur de `awci_vertical_profile` (35/50/65/85). Le même
  score peut porter deux libellés différents à l'écran.
- **M4 — Trois palettes et deux mappings couleur/niveau** : `AWCI_CMAP`
  (dashboard), `turbo` (`AWCILayer`), `RdYlBu_r` (`AWCIRenderer`) ;
  `risk_qcolor()` décale les couleurs d'un cran par rapport à `LEVELS`
  (« Very Low » badge = couleur « Low » carte). `AWCI_LAYOUT_SPEC.md`
  décrit une 3ᵉ palette (vert→rouge) qui n'existe plus.
- **M5 — Trois conversions pression ↔ altitude** : `isa_atmosphere`
  (science), formule troposphérique `145366,45·(1−(p/1013,25)^0,190284)`
  (map panel), table interpolée `_HPA_TO_FT` (cross-section). FL390 est
  hors du domaine de validité troposphérique de la 2ᵉ (écart 0,5 hPa
  **[exécuté]**, croissant au-dessus).
- **M6 — Échantillonnage de route en interpolation lat/lon linéaire**, pas
  sur le grand cercle ; longitude au plus proche sans gestion
  d'antiméridien (`path_sampling`, `vertical_profile_at_point`,
  `sample_archive_at_point`). Faux pour JFK→CDG (route par défaut).
- **M7 — Import de fichier : incohérence de pression.** Les alias
  `pressure` incluent `mslp`/`msl`/`prmsl` ; un fichier 3D en niveaux
  pression + MSLP 2D fournit T à 300 hPa avec p ≈ 1013 hPa → RH, θe,
  plafond calculés avec une pression fausse.
- **M8 — Heuristique d'unité RH ambiguë** (`0 < rh ≤ 1,5` ⇒ fraction) :
  une RH de 1 % sans unité déclarée devient 100 %.
- **M9 — Indices convectifs** : SRH et cisaillement « 0–1 km / 0–6 km »
  alimentés avec des valeurs colonne entière (`significant_tornado_parameter_fixed`).
- **M10 — Citation** : `WMO_HEAVY_RAIN_MM_H = 7.6` — 2,5 / 7,6 mm/h sont
  les seuils AMS/NWS ; le guide OMM n°8 utilise 2,5 / 10 / 50 mm/h.
- **M11 — Évolution importée sans coordonnée temps** : axe fabriqué
  « t+1 h par frame » (divulgué dans `notes`, mais affiché comme temps).

### Backend web
- **W1 — Boucle d'événements bloquée.** Tous les endpoints de calcul
  (`/complexity/field`, `/datasets/from_complexity_field`,
  `/events/detect`, `/workstation/*`) sont `async def` mais exécutent de
  lourds calculs synchrones (solveur + boucles Python) : une requête
  gèle tout le serveur, WebSocket HPC compris.
- **W2 — Aucune validation d'entrée** : `/complexity/score` accepte un
  `dict` arbitraire → 500 sur type invalide **[exécuté]** ;
  `/fno/predict_demo` sans borne sur `n_lat`/`n_lon` (0 → 500
  **[exécuté]**, très grand → DoS mémoire).
- **W3 — Aucun endpoint AWCI « produit »** : pas de route pour archive
  ALADIN, METAR/TAF/SIGMET, aéroports, route/cross-section, profil
  vertical, évolution, explicabilité (registre de diagnostics).
- **W4 — Pas de CORS, pas de schéma de réponse (Pydantic), pas de
  versionnement d'erreurs**, page `/` HTML inline dans une chaîne Python.
- **W5 — Dépendances** : le serveur web importe `paramiko` (extra `hpc`)
  sans que l'extra `web` le déclare ; collecte des tests web impossible
  sans lui **[exécuté]**. (`httpx2`, déclaré, est bien celui qu'utilise
  le `TestClient` de Starlette installé — vérifié.)

### Performance
- **P1 — Boucles Python par point partout** : `AWCICalculator.calculate()`
  est scalaire (dicts), appelé par point dans `spatial_field`,
  `vertical_field.score_volume`, `temporal_field`, `cat_turbulence`,
  `path_sampling.real_layer_grids_at_level`, `workstation_fields`,
  `model_import_evolution` (qui re-matche les alias + reconstruit un
  `Dataset` **par cellule et par frame**). Inadapté au web et aux grands
  volumes ; un calculateur vectorisé NumPy est un prérequis.

### Architecture / maintenabilité
- **A1 — `awci_dashboard.py` = 3 442 lignes**, état global en attributs,
  logique métier (choix de source, route, aéroports, recommandation)
  mêlée à l'UI : non réutilisable par un front web.
- **A2 — Duplications** : `_haversine_km` (×4), deux rapports d'exécution
  (`execution_report` GOOD/DEGRADED/BAD vs `run_report` PASS/FAIL),
  formules d'affichage recopiées à la main (`COMPONENT_INFO`) au lieu du
  registre (dérive : la formule « dynamic » affichée omet le mélange
  cisaillement).
- **A3 — Fichiers `awci_*_dashboard.py`** dans `geology`, `master`,
  `planetary`, `ai_expert`, `geoengineering` : métadonnées statiques
  sans lien avec AWCI (nommage trompeur). `AWCIRenderer` contient des
  `print()` de debug.
- **A4 — Identité incohérente** : « Aviation » vs « Atmospheric Weather
  Complexity Index » (`awci_app.py --version`), « AWCI v2.1.0 » codé en
  dur (sidebar) vs paquet `0.1.0`.
- **A5 — Constantes machine** : archive RESTOR codée `~/RESTOR`, run
  `2026083100` fixe ; non disponible hors de la machine d'origine (et
  dans cet environnement).

## 4. Constats mineurs
- Plafond MVFR/VFR à exactement 3 000 ft, visibilité à exactement 5 SM :
  classés VFR (FAA : MVFR inclusif).
- `metar_verification` utilise le QNH comme pression station.
- `archive_field` stocke `validity` sous le nom `run_datetime`.
- `AWCIDecomposition` affiche des points AWCI suffixés « % ».
- Vue 3D : axe vertical = indice de niveau (espacement non physique).
- `terrain_elevation` extrapole (`fill_value=None`) sans bouclage en
  longitude.
- Emojis utilisés comme icônes (accessibilité, cohérence visuelle).
- `set_weight`/`WeightsManager(weights)` partagent la référence du dict
  appelant.

## 5. Ce qui est réellement réutilisable pour AWCI Web
| Brique | État | Réutilisation |
|---|---|---|
| Diagnostics `theta_e`, `ceiling`, `visibility`, `dust`, `wind_shear`, `cat_turbulence`, `convective_energy`, `orographic_froude`, `volcanic_ash`, `microburst` | formules sourcées, `None` honnête | ✅ (à vectoriser) |
| `regridding.py` (NN, bilinéaire, conservatif) | correct | ✅ |
| `archive_field.py` + EPyGrAM | seule source NWP réellement réelle | ✅ si données disponibles côté serveur |
| `aviation.icao` (METAR/TAF/SIGMET live + décodeurs) | réel | ✅ source prioritaire |
| `airport.py` (corridors) | correct | ✅ |
| `scientific_status` / `diagnostic_registry` | source unique d'explicabilité | ✅ à exposer par API |
| `AWCICalculator` | logique OK, défauts silencieux, scalaire | ⚠ à envelopper (validation + vectorisation) |
| `awci_synthetic_field` | incohérent physiquement | ❌ jamais en production web |
| « Real Physics » (`CoupledEarthSolver`) | idéalisé, non reproductible | ❌ comme donnée opérationnelle ; ✅ comme bac à sable étiqueté « simulation » |
| `awci_dashboard.py` | couplé Qt | ❌ (extraire la logique métier) |

## 6. Recommandations avant le démarrage d'AWCI Web
1. **Couche service unique** (`acf.awci.service`) indépendante de Qt,
   consommée à la fois par le desktop et l'API : sélection de source,
   route, aéroports, profil, explicabilité.
2. **Contrat de données explicite** : chaque réponse porte `source_tier`
   (`observation` | `nwp_archive` | `imported` | `simulation` | `demo`),
   `missing_inputs`, `provenance`, et un module non alimenté vaut
   `null`, jamais 0.
3. **Classification unique** (niveaux + palette accessible) servie par
   l'API, consommée par tous les clients.
4. **Calculateur vectorisé** NumPy bit-compatible avec l'actuel (tests de
   parité) avant tout rendu de champ côté web.
5. **Corriger C1** (RNG seedé pour U/V) et **C5** (libellés) avant
   exposition.
6. **Backend** : endpoints lourds en `def` (thread pool) ou file de
   tâches, modèles Pydantic, CORS configuré, bornes sur tous les
   paramètres.
7. **Décisions scientifiques à trancher** (M1, M2) : documenter ou
   corriger la normalisation de température et le rôle du CIN.

## 7. Tests

Suite AWCI + web (110 fichiers) exécutée sous Python 3.12,
`QT_QPA_PLATFORM=offscreen`, extras `gui,geospatial,science,web,
monitoring,dev,hpc,satellite,formats` + `torch` CPU :

- **1 168 passés, 27 ignorés, 0 échec** en fin de compte. Les tests
  ignorés sont conditionnés à l'archive locale `~/RESTOR`, absente de cet
  environnement : la lecture réelle de l'archive ALADIN n'a donc **pas**
  été vérifiée ici.
- 13 échecs initiaux dus uniquement à l'absence de `torch` (extra `ai`) :
  tous passent une fois torch installé. Autrement dit, le lanceur ESOC,
  le champ AWCI ESOC et la page web dépendent de torch à l'import.
- Fragilité observée : lancés en 4 lots parallèles,
  `test_awci_dashboard_hpc_and_import::…without_a_real_ssh_transport…`
  a dépassé son `waitUntil(5000 ms)` et un lot s'est terminé par un
  segfault (code 139). Aucun des deux ne se reproduit en exécution
  isolée : tests sensibles à la charge machine.
- Lancée en un seul processus, la suite complète a dépassé le
  `timeout = 60 s` par test sur
  `test_imported_cross_section_survives_revert_to_demo`, même cause
  probable.
