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
