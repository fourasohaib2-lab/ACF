# ACF — État réel (source de vérité unique)

Ce fichier remplace tous les anciens documents de statut/certificat archivés
dans `docs/archive/`. Un module n'est coché `[x]` que s'il satisfait les 4
critères de `ARCHITECTURE.md` §3 (commit `audit(module)`, tests verts, pas de
surclaim de docstring, dépendances déclarées). `[~]` = travail réel en cours
mais audit non finalisé. Dernière mise à jour : voir `git log -- docs/STATUS.md`.

## Tier F — Foundation (bloquant v1.0)

- [ ] `core`
- [ ] `model4d`
- [ ] `science`
- [x] `physics_guard`
- [ ] `parameters`
- [x] `standards`
- [x] `validation`
- [x] `normalization`
- [ ] `time`
- [ ] `utils`
- [ ] `earth_physics`
- [ ] `io`

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

- [x] `geoengineering`
- [ ] `planetary`
- [ ] `fire_weather`
- [ ] `certification`

## Synthèse

- Tier F : 4/12 audités
- Tier C : 5/16 audités
- Tier E : 15/31 audités
- Total bloquant v1.0 (F+C+E) : 24/59
- Tier X : hors critère (voir ARCHITECTURE.md §3)

## Prochaine étape

Continuer le sweep dans l'ordre Tier F -> Tier C -> Tier E, un module à la
fois, en suivant le patron des commits `audit(...)` déjà sur `develop`.
