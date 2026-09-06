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

- [~] `data`
- [x] `catalog`
- [x] `catalogs`
- [x] `importers`
- [x] `geospatial`
- [x] `models`
- [x] `surfex`
- [x] `hpc_connector`
- [x] `hpc_workflow`
- [x] `simulation_engine`
- [~] `gui` (~30k lignes, 10 sous-packages. Couverts : `esoc/`,
  `dashboard/`, `map/` (42 fichiers — déjà documenté : 5 sous-packages
  entiers `layers/`/`renderers/`/`rendering/`/`navigation/`/
  `projections/` sont une réserve non branchée ; trouvé en plus cette
  passe : 3 mixins réels `RenderingMixin`/`ExportMixin`/`StatusMixin`
  prétendaient être utilisés par `MapCanvas` alors qu'ils ne le sont
  pas — corrigé), `docks/`, `layer_panel/`, plus les stubs vides à la
  racine (`toolbar.py`, `statusbar.py`) et fichiers réels corrigés
  (`theme.py`, `splash.py`, `widgets/property_panel.py`). Reste non
  couvert : `widgets/` (reste), `main_window/`, `dialogs/`, quelques
  fichiers en vrac à la racine)
- [~] `visualization`
- [ ] `maps`
- [~] `awci`
- [x] `jobs`
- [ ] `storage`

## Tier E — Extended (souhaité v1.0)

- [x] `aviation`
- [x] `hydrology`
- [ ] `ocean`
- [x] `geology`
- [ ] `space_weather`
- [ ] `climate`
- [ ] `ai`
- [~] `ai_expert`
- [x] `intelligence`
- [x] `digital_twin`
- [ ] `aeos`
- [ ] `knowledge_platform`
- [x] `dashboard`
- [x] `web`
- [ ] `api`
- [~] `monitoring`
- [ ] `alerts`
- [x] `hazard_operations`
- [ ] `release`
- [x] `verification`
- [x] `data_assimilation`
- [x] `forecast`
- [x] `events`
- [ ] `connectors`
- [ ] `master`
- [ ] `workspace`
- [x] `reports`
- [ ] `search`
- [x] `testing`
- [x] `plugins`
- [ ] `animation`

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
- [ ] `certification`

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
- Tier C : 10/16 audités
- Tier E : 15/31 audités
- Total bloquant v1.0 (F+C+E) : 36/58
- Tier X : hors critère (voir ARCHITECTURE.md §3)

## Prochaine étape

Tier F terminé. Continuer avec Tier C (5/16 audités) : prochains modules
`catalog`/`catalogs` (décision de consolidation à prendre en premier —
voir ARCHITECTURE.md §3), `geospatial`, `surfex`, `simulation_engine`,
`gui`, `maps`, `storage`, puis finir `data`/`visualization`/`awci`
(actuellement `[~]`). Même patron que Tier F : `git log -- <module>`
d'abord pour ne pas refaire un travail déjà honnête, corriger les vrais
surclaims, tests verts, commit `audit(module): ...`.
