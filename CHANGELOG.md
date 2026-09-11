# Changelog

Toutes les modifications importantes du projet ACF sont documentées ici.

> Note : ce fichier n'a pas été tenu à jour entre juillet et septembre 2026
> alors que le développement continuait (voir `git log --oneline` pour
> l'historique complet et exact sur cette période — il reste la source
> primaire). Il est repris à jour à partir du 6 septembre 2026 et sera
> maintenu à chaque changement notable, comme le demande `AGENTS.md`.

## [Unreleased] - 2026-09-11

### Added
- AWCI "turbulence" map layer (Real Physics mode) : indice de turbulence
  en air clair Ellrod-Knapp (1992) complet (`CATIndex.ti1`), remplaçant le
  proxy de gradient de norme du vent utilisé jusque-là — cisaillement
  vertical réel via l'équation hypsométrique (`acf.science.
  hypsometric_equation`) + température virtuelle réelle, déformation
  horizontale réelle à partir des composantes u/v réelles du volume
  solveur. Voir `docs/awci/future-improvements.md` §5. Mode démo inchangé
  (proxy conservé, disclosed — pas de composantes u/v réelles dans le
  pattern synthétique).
- 3 skills de repo (`.claude/skills/`) : `awci-review` (checklist
  scientifique/technique pour tout changement AWCI), `acf-status-sync`
  (cohérence docs/STATUS.md ↔ code après un changement), `acf-dashboard-design`
  (système de tokens UI réel, capacités Qt/QSS, convention charts
  matplotlib ↔ chrome).

### Changed
- Unification de la palette des panneaux matplotlib du dashboard AWCI
  (`awci_radar.py`, `awci_route_chart.py`, `awci_cross_section.py`,
  `awci_volume_3d.py`, complète du reste de `awci_map_panel.py`) sur
  `acf.gui.theme_tokens.TOKENS` — ces 5 fichiers gardaient encore une
  palette hex figée pré-2026-09-07, visuellement incohérente avec le
  chrome Qt déjà modernisé. Couleurs de données volontaires (icônes
  givrage/turbulence, courbe du radar) laissées inchangées, non
  concernées.
- Poursuite de l'unification (2e et 3e passes) : `awci_stats_bar.py`,
  `awci_risk_summary.py`, `awci_toast.py` (couleurs de sévérité
  réutilisent maintenant `TOKENS.success/warning/danger` au lieu de hex
  qui les dupliquaient), `awci_execution_report_dialog.py`,
  `awci_footer.py`. Ajout de 2 nouveaux tokens réels
  `warning_surface`/`warning_surface_border` (`theme_tokens.py`) —
  promotion de la paire ambrée déjà utilisée par la bannière de
  recommandation d'`awci_dashboard.py` (mêmes valeurs, pas de nouvelle
  couleur inventée) en tokens réutilisables, dernier littéral hex du
  fichier. Ajout d'un retour visuel au survol manquant sur
  `acf_workstation_thumbnail_strip.py` (seul élément cliquable du
  dashboard qui n'en avait pas). Portée volontairement limitée à
  AWCI/Scientific Workstation — `acf.gui.esoc` (~123 littéraux restants,
  périmètre distinct et nettement plus large) explicitement exclu de
  cette session sur demande.

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
