# ACF — État réel (source de vérité unique)

Ce fichier remplace tous les anciens documents de statut/certificat archivés
dans `docs/archive/`. Un module n'est coché `[x]` que s'il satisfait les 4
critères de `ARCHITECTURE.md` §3 (commit `audit(module)`, tests verts, pas de
surclaim de docstring, dépendances déclarées). `[~]` = travail réel en cours
mais audit non finalisé. Dernière mise à jour : voir `git log -- docs/STATUS.md`.

## Tier F — Foundation (bloquant v1.0)

- [x] `core`
- [ ] `science`
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
- [ ] `catalog`
- [ ] `catalogs`
- [x] `importers`
- [ ] `geospatial`
- [x] `models`
- [ ] `surfex`
- [x] `hpc_connector`
- [x] `hpc_workflow`
- [ ] `simulation_engine`
- [ ] `gui`
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

## Synthèse

- Tier F : 10/11 audités (model4d reclassé en Tier X le 2026-09-06)
- Tier C : 5/16 audités
- Tier E : 15/31 audités
- Total bloquant v1.0 (F+C+E) : 30/58
- Tier X : hors critère (voir ARCHITECTURE.md §3)

## Prochaine étape

Continuer le sweep dans l'ordre Tier F -> Tier C -> Tier E, un module à la
fois, en suivant le patron des commits `audit(...)` déjà sur `develop`.
