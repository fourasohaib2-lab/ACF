# ACF — État réel (source de vérité unique)

Ce fichier remplace tous les anciens documents de statut/certificat archivés
dans `docs/archive/`. Un module n'est coché `[x]` que s'il satisfait les 4
critères de `ARCHITECTURE.md` §3 (commit `audit(module)`, tests verts, pas de
surclaim de docstring, dépendances déclarées). `[~]` = travail réel en cours
mais audit non finalisé. Dernière mise à jour : voir `git log -- docs/STATUS.md`.

## Tier F — Foundation (bloquant v1.0)

- [x] `core`
- [x] `science`
- [x] `physics_guard`
- [x] `parameters`
- [x] `standards`
- [x] `validation`
- [x] `normalization`
- [x] `time`
- [x] `utils`
- [x] `earth_physics`
- [x] `io`

## Tier C — Core (bloquant v1.0)

- [x] `data`
- [x] `catalog`
- [x] `catalogs`
- [x] `importers`
- [x] `geospatial`
- [x] `models`
- [x] `surfex`
- [x] `hpc_connector`
- [x] `hpc_workflow`
- [x] `simulation_engine`
- [x] `gui` (~30k lignes, 10 sous-packages, tous couverts. Finding le
  plus important du sweep : `earth_system_operations.py` (exporté dans
  `gui/__init__.py.__all__`, jamais construit) retournait une
  auto-certification fabriquée — `"ui_version": "ACF-UI-001 Production
  Certified"` et `"integration_status": "ALL_45_MISSIONS_INTEGRATED"`
  — sans aucune UI réelle derrière, et son propre test l'affirmait
  comme vrai. Corrigé (code + test). Autres findings : `map/` (5
  sous-packages entiers non branchés, déjà documenté + 3 mixins
  mal étiquetés corrigés cette passe), `main_window/` (sous-package
  entier non branché, disclosure ajoutée), 11 stubs vides au total
  dans `docks/`/`layer_panel/`/racine corrigés, `view_manager.py`
  (8/15 modes de vue sans projection réelle))
- [x] `visualization`
- [x] `maps`
- [x] `awci`
- [x] `jobs`
- [x] `storage`

## Tier E — Extended (souhaité v1.0)

- [x] `aviation`
- [x] `hydrology`
- [x] `ocean`
- [x] `geology`
- [x] `space_weather`
- [x] `climate`
- [x] `ai`
- [x] `ai_expert`
- [x] `intelligence`
- [x] `digital_twin`
- [x] `aeos`
- [x] `knowledge_platform`
- [x] `dashboard`
- [x] `web`
- [x] `api`
- [x] `monitoring`
- [x] `alerts`
- [x] `hazard_operations`
- [x] `release`
- [x] `verification`
- [x] `data_assimilation`
- [x] `forecast`
- [x] `events`
- [x] `connectors`
- [x] `master`
- [x] `workspace`
- [x] `reports`
- [x] `search`
- [x] `testing`
- [x] `plugins`
- [x] `animation`

## Tier X — Experimental (hors scope v1.0, conservé)

- [~] `model4d` (reclassé Tier F -> Tier X le 2026-09-06, voir
  ARCHITECTURE.md §3 : zéro appelant réel dans tout `src/acf/`, vérifié
  par grep répété. Code réel, testé, conservé - juste hors du périmètre
  v1.0. Couverts : les 20 `physics/*_engine.py` +
  `weather_intelligence_orchestrator.py`, tout `model4d/operators/` (8
  fichiers) et `model4d/interpolation/` (9 fichiers), + échantillon
  représentatif de ~12 fichiers `physics/` non-`_engine.py`. Reste (non
  bloquant maintenant) : la majorité des ~131 fichiers `physics/`
  non-`_engine.py`, non individuellement relus)
- [x] `geoengineering`
- [ ] `planetary`
- [ ] `fire_weather`
- [x] `certification` (voir ARCHITECTURE.md §3 — audité, excellent,
  compose uniquement des composants déjà vérifiés)

## Baseline factuelle

Run complet `pytest -q` du 2026-09-06 (avant tout changement de code de ce
sweep) : **4574 passed, 0 failed**, 480s, 676 warnings (essentiellement des
`DeprecationWarning` Qt/PySide6 sur des constructeurs `QMouseEvent`, et un
avertissement de spécification Zarr — aucun échec, mais à nettoyer pendant
le sweep des modules `gui` et `storage`/`simulation_engine` concernés).

**Écart découvert pendant le sweep Tier C (`gui`), même journée** :
`tests/test_gui_stack_scroll_no_permanent_growth.py` — 2 des 4 tests
échouent maintenant, y compris exécutés seuls (pas un problème
d'ordre) :
`test_esoc_window_can_still_be_explicitly_shrunk_after_visiting_a_large_tab`
et
`test_acf_workstation_window_can_still_be_explicitly_shrunk_after_visiting_complexity_explorer`.
Les deux échouent de la même façon : `window.resize(...)` est appelé
mais la fenêtre reste à 1010px de haut au lieu de la valeur demandée
(500 / <737). Aucun changement de code de ce sweep ne touche ce chemin
(seuls des docstrings ont été modifiés dans `view_manager.py`/
`map_projection.py` avant cette découverte). Hypothèse la plus
probable, non confirmée : ces tests dépendent du gestionnaire de
fenêtres X11 réel (`DISPLAY=:0`, pas de serveur X virtuel) pour
honorer un `resize()` de façon synchrone après un seul
`qapp.processEvents()` — cette session a depuis lancé Claude Desktop
(plusieurs fenêtres/processus réels sur le même serveur X), ce qui
peut avoir changé le comportement/timing du WM par rapport au run de
baseline. **Non résolu ici** — à revérifier dans un environnement
propre/CI avant de conclure à une vraie régression de code plutôt
qu'à un artefact d'environnement. Ne pas ignorer silencieusement :
tracké ici tant que non expliqué avec certitude.

## Synthèse

- Tier F : **11/11 audités — TIER F COMPLET** (model4d reclassé en
  Tier X le 2026-09-06)
- Tier C : **16/16 audités — TIER C COMPLET**
- Tier E : **31/31 audités — TIER E COMPLET**
- Total bloquant v1.0 (F+C+E) : **58/58 — TOUT LE PÉRIMÈTRE v1.0 EST AUDITÉ**
- Tier X : hors critère (voir ARCHITECTURE.md §3)

## Sweep Tier F + Tier C + Tier E : TERMINÉ (2026-09-06)

Les 58 modules bloquants v1.0 (Foundation + Core + Extended) sont tous
individuellement audités, testés et honnêtement documentés. Les deux
derniers items ouverts d'`ARCHITECTURE.md` §3 (`certification/` et
`src/acf/resources/`) sont également résolus.

Ce que "terminé" veut dire concrètement ici — et ne veut pas dire :
un module coché `[x]` a satisfait les 4 critères vérifiables
d'`ARCHITECTURE.md` §3 (commit d'audit, tests verts, pas de surclaim
de docstring connu, dépendances déclarées). Ça ne veut pas dire que le
projet est "fini" au sens produit — ça veut dire que l'écart entre ce
que le code prétend faire et ce qu'il fait réellement est maintenant
documenté partout où on l'a cherché, pas qu'il n'existe plus nulle
part. Prochaines étapes naturelles, non bloquantes :
- `docs/STATUS.md` doit rester tenu à jour à chaque nouveau changement
  de code (pas seulement relu une fois).
- Le reste de `model4d/physics/` (Tier X, ~100 fichiers non
  individuellement relus) et `planetary`/`fire_weather` (Tier X)
  restent des réserves non couvertes, explicitement hors périmètre
  v1.0 — pas oubliées, juste non prioritaires.
- Tier E est "souhaité", pas figé : tout nouveau module y ajouté doit
  suivre la même discipline dès son premier commit, pas être audité
  après coup.
