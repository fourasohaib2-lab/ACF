# Changelog

Toutes les modifications importantes du projet ACF sont documentées ici.

> Note : ce fichier n'a pas été tenu à jour entre juillet et septembre 2026
> alors que le développement continuait (voir `git log --oneline` pour
> l'historique complet et exact sur cette période — il reste la source
> primaire). Il est repris à jour à partir du 6 septembre 2026 et sera
> maintenu à chaque changement notable, comme le demande `AGENTS.md`.

## [Unreleased] - 2026-09-06

### Added
- Table de tiers de maturité/scope (Foundation/Core/Extended/Experimental)
  dans `ARCHITECTURE.md`, couvrant les 62 sous-modules de `src/acf/`.
- `docs/STATUS.md` : suivi unique et vérifiable de l'avancement réel
  (remplace les documents de statut/certificat concurrents).
- `docs/archive/README.md` expliquant l'archivage.

### Changed
- 185 documents historiques de `docs/` (sprints, certificats de release
  v0.4–v1.0, roadmaps concurrentes, rapports d'audit datés) déplacés vers
  `docs/archive/` (`git mv`, historique préservé, rien supprimé).

### Fixed
- **Bug utilisateur** : plusieurs dashboards s'affichaient simultanément
  au lancement de l'application. Deux causes réelles trouvées et
  corrigées : (1) absence de garde mono-instance - ajout de
  `acf.gui.single_instance.SingleInstanceGuard` (réel
  `QLocalServer`/`QLocalSocket`, pas un mock), vérifiée par 3 lancements
  réels successifs et par un test de robustesse au crash (`kill -9` +
  relance) ; (2) 4 scripts orphelins à la racine du dépôt
  (`test_awci_display.py`, `test_dashboard.py`, `test_qt.py`,
  `test_window.py`), chacun construisant sa propre `QApplication` hors du
  périmètre de l'app réelle - supprimés (récupérables via git).
- **Champs AWCI réels jetés silencieusement** : `compute_real_complexity_field()`
  calcule 9 champs réels par module mais `MODULE_COMPLEXITY_LAYERS`
  n'en enregistrait que 6 - les 3 champs `FORECAST_MODULES`
  ("confidence"/"ensemble_spread"/"model_disagreement") étaient
  calculés puis rejetés en silence à chaque usage du bouton "🌪️ AWCI
  Field" (WARNING loggé, invisible en usage normal, jamais une
  exception). Trouvé par un smoke-test réel des 25 commandes de la
  barre d'outils ESOC, pas par lecture de code. Corrigé en enregistrant
  les 3 layers manquants.

# [0.2.0-alpha] - 2026-07-23

## Added

### Project Management System

- Added complete ACF project workspace system.
- Added project creation workflow.
- Added project opening workflow.
- Added project saving system.
- Added project closing system.

### Workspace

- Added `WorkspaceManager`.
- Added `ProjectSerializer`.
- Added persistent `project.acf` files.
- Added project metadata management.

### Recent Projects

- Added `RecentProjectsManager`.
- Added recent projects history.
- Added automatic storage in:
