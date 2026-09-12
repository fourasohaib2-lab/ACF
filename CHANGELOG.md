# Changelog

Toutes les modifications importantes du projet ACF sont documentées ici.

> Note : ce fichier n'a pas été tenu à jour entre juillet et septembre 2026
> alors que le développement continuait (voir `git log --oneline` pour
> l'historique complet et exact sur cette période — il reste la source
> primaire). Il est repris à jour à partir du 6 septembre 2026 et sera
> maintenu à chaque changement notable, comme le demande `AGENTS.md`.

## [Unreleased] - 2026-09-12

### Added
- Refonte de l'ACF Scientific Workstation (`acf.gui.dashboard.
  acf_workstation`) vers le nouveau mockup de référence, en 4 passes :
  nouvel écran d'accueil (`ACFOverviewLandingPanel`) avec sections
  "Key Metrics" (complexité spatiale/CAPE/RH/cisaillement réels),
  "Model Consensus" (`ModelConsensusEngine` réel, off-thread),
  "Alerts & Hazards" (`ForecastDecisionEngine.assess_severe_weather_
  risk()` réel, seuils NOAA SPC/Doswell et al. 1996) et "Quick Actions"
  (4 boutons câblés à des handlers réels existants) ; nouvelles
  sections nav "REPORTS"/"HPC / JOBS" (horloge, statut moteur, connexion
  HPC réelle off-thread). Le mockup de référence montrait un "Complexity
  Index"/"Agreement Level %" composites - remplacés par ces valeurs
  physiques réelles et disclosed (§21/§67 du master prompt interdisent
  le score composite fabriqué). Voir `docs/STATUS.md` pour le détail
  des 4 phases.
- `theme_tokens.dashboard_stylesheet()` : vraies règles QSS
  `QGroupBox`/`QComboBox`/`QListWidget` (aucune règle avant pour les
  ~20 QGroupBox et 2 QListWidget de la Workstation), nouveau helper
  `_rgba()`.
- Première passe d'audit de conformité technique ICAO/OMM
  (`docs/compliance/ICAO_WMO_COMPLIANCE_AUDIT.md`, sur demande
  explicite) : `acf.standards.grib2_tables`/`ecmwf_parameters`/
  `noaa_parameters` peuplés avec de vraies identités de paramètres
  (WMO Table 4.2, ECMWF GRIB Table 128, NCEP GRIB1 Table 2) pour les 9
  quantités déjà présentes dans `cf_standard_names.py` - ces 3 fichiers
  (+ `wmo_tables.py`, laissé honnêtement vide) n'avaient auparavant
  qu'un docstring auto-généré générique, zéro contenu réel, jamais
  importés nulle part (même famille de bug que le faux
  `"ACF-UI-001 Production Certified"` déjà corrigé dans ce projet).

### Fixed
- Horloge du header ACF Workstation : affichait l'heure locale
  (honnêtement étiquetée "(local)") - passée à une vraie heure UTC
  (`QDateTime.currentDateTimeUtc()`), l'Annexe 3 OACI §4.1 exigeant
  l'UTC exclusivement pour toute information météorologique
  aéronautique.
- Sweep UTC systématique (`datetime.now()` sur tout `src/acf`) : 2 vrais
  bugs de faux étiquetage UTC trouvés et corrigés -
  `BriefingGenerator.generate_briefing()` (générait un "OFFICIAL
  METEOROLOGICAL BRIEFING" étiqueté "UTC" mais calculé en heure locale
  réelle - code réellement câblé, pas mort) et
  `acf.events.event.Event.start_time`/`detect_strong_wind_events()`/
  `detect_fog_favorable_events()` (horodatage d'événement météo en
  heure locale non-disclosed, sérialisé sans offset).
- Grammaire METAR/TAF (`acf.aviation.icao`), items disclosed comme
  manquants dans les docstrings des décodeurs : indicateur de tendance
  RVR U/D/N (METAR) et groupes TX/TN température max/min (TAF) - ce
  dernier tombait auparavant silencieusement dans le filet
  "unrecognized token, skip" du décodeur, aucun champ ne le portait.
- `BUFRAdapter.load()`/`GRIBAdapter.load()` (`acf.data.integration`) :
  retournaient silencieusement un `Dataset` bien formé mais vide, sans
  aucune disclosure, quel que soit le contenu réel du fichier - aucun
  appelant réel actuellement (`AdapterFactory` n'a pas de caller hors
  de ses propres tests), mais un piège silencieux pour un futur
  appelant. `dataset.metadata["is_real_data"]` désormais honnêtement
  `False` avec la raison. Les 6 autres adaptateurs de cette même
  fabrique (NetCDF/CSV/JSON/XML/HDF5/GeoTIFF) ont le même bug non
  corrigé - hors périmètre OACI/OMM de cette session, disclosed pour
  une passe dédiée.

### Changed
- Le dashboard AWCI n'est plus jamais embarqué dans le dock ESOC :
  `PanelManager.AWCIDashboardPanel` (28e onglet, 2e instance redondante
  d'`AWCIDashboard()`) supprimée (`PanelManager.panels` : 44 → 43
  entrées). Le bouton toolbar existant "✈️ AWCI" (ouvre
  `AWCIDashboardWindow` en fenêtre autonome) reste le seul et unique
  chemin réel vers ce dashboard, sans changement de comportement.

## [Unreleased] - 2026-09-11

### Added
- Couches carte AWCI "CAPE"/"Convection" en mode Real Physics :
  `acf.awci.path_sampling.real_layer_grids_at_level()` calcule maintenant
  le vrai CAPE de surface (formule MetPy parcel-ascent déjà utilisée
  ailleurs dans le codebase — `compute_real_cape_cin_at_point()`) à partir
  de la colonne verticale complète déjà présente dans le volume solveur
  (`temperature_volume`/`specific_humidity_volume`/`pressure_volume_hpa`,
  jusque-là seulement tranchés par niveau) — pas une nouvelle formule,
  une réutilisation d'une colonne réelle déjà disponible mais non
  exploitée pour cet usage. "Convection" réutilise ce même CAPE réel
  (`compute_real_max_updraft_velocity`). Honnêtement `NaN` (jamais 0.0
  fabriqué) là où trop peu de niveaux réels subsistent au-dessus du seuil
  de 100 hPa. "Clouds" reste un vrai no-op (aucun champ de précipitation
  nulle part dans ce pipeline, mode démo ou Real Physics). Voir
  `docs/awci/future-improvements.md` §6.
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
