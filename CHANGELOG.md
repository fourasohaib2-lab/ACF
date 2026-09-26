# Changelog

Toutes les modifications importantes du projet ACF sont documentées ici.

> Note : ce fichier n'a pas été tenu à jour entre juillet et septembre 2026
> alors que le développement continuait (voir `git log --oneline` pour
> l'historique complet et exact sur cette période — il reste la source
> primaire). Il est repris à jour à partir du 6 septembre 2026 et sera
> maintenu à chaque changement notable, comme le demande `AGENTS.md`.

## [Unreleased] - 2026-09-06

### Added
- AWCI Web SP1 : ingestion ECMWF IFS 0,25° Open Data (`acf-awci-ingest`), dangers
  vectorisés + AWCI `operational-v1`, API en lecture seule `/api/v1/awci`
  (`acf-awci-web`). Voir `docs/awci/AWCI_WEB_SP1.md`.
- AWCI Web SP1C (nuages) : fraction nuageuse par niveau (Sundqvist 1989), couvertures
  par étage (σ ECMWF, recouvrement maximum-aléatoire) contrôlées contre le `tcc` IFS,
  couches (base/sommet/octas), plafond OACI, convection (particule de surface, Cu/TCU/Cb),
  genre OMM probable par couche et par étage, espèces diagnosticables, température
  d'émission des sommets (OLR), condensat colonne, neige, pluie verglaçante ; routes
  `/clouds`, `/volume`, `/terrain` ; calibration reproductible de RHc
  (`tools/awci/calibrate_cloud_rhc.py`). Statut HYPOTHESIS. Voir `docs/awci/AWCI_WEB_SP1.md`.
- AWCI Web SP2 (front 2D, `web/awci`) : tableau de bord React/MapLibre servi par `acf-awci-web`
  (même origine) ; champ rééchantillonné en Mercator, hachures « sans donnée », lignes de courant,
  indicateurs de domaine pondérés par l'aire, inspecteur explicable, profils, panneau Nuages,
  observations EUMETView relayées avec heure d'observation, thème clair validé ; nouvelles routes
  `/summary`, `/summary/series`, `/clouds/series`, `/wms`, `/wms/times`, `/wms/layers`. Voir
  `docs/awci/AWCI_WEB_SP2.md`.
- AWCI Web SP5 (ensemble ECMWF) : `acf-awci-ens` traite chaque membre de l'IFS ENS (50 membres, 0,25°) par le
  pipeline déterministe inchangé, en flux, et stocke des comptes exacts ; probabilités de AWCI ≥ High, nuage ≥ 5/8,
  givrage, turbulence ≥ modérée, TCU/Cb réalisé, plafond < 1500 ft, et moyenne ± écart-type de l'AWCI ; routes
  `/ens/*` ; couches de probabilité et panneau « Ensemble ECMWF ». Voir `docs/awci/AWCI_WEB_SP5.md`.
- AWCI Web SP2B (vue volume 3D et lecture 4D) : voxels = mailles IFS réelles entre interfaces de niveaux,
  relief du modèle, nuages par genre, givrage, turbulence et AWCI (deux couches au plus), exagération
  toujours énoncée, échelle en hPa, FL et km, clic sur voxel vers l'inspecteur au niveau du voxel,
  préchargement 4D, message explicite sans WebGL2. deck.gl 9.4 chargé à la demande (203 Ko gz). Voir
  `docs/awci/AWCI_WEB_SP2B.md`.
- Diagnostic convectif recalibré contre les METAR (profil nuageux 1.2.0) : TCU et Cb exigent une convection
  réalisée par l'IFS (précipitation ≥ 0,1 mm/h). Choix fait sur 4 runs, jugé sur 3 runs indépendants :
  biais de 4,36 à 1,14, ETS de 0,11 à 0,16, POD de 0,58 à 0,31. Outil `tools/awci/calibrate_convection.py`.
- AWCI Web SP3 (aérodromes, METAR/TAF, SIGMET, validation) : ingestion AWC (`acf-awci-obs`, domaine
  public) avec pagination au-delà du plafond de 400 éléments ; décodeur METAR (CB/TCU, `///`, CAVOK/NSC/NCD,
  plafond OACI, convection inconnue pour les stations automatiques) contrôlé sur 400 METAR réels ; validation
  du plafond et de la convection (POD, FAR, CSI, biais, ETS par échéance) ; routes `/airports`, `/airport`,
  `/sigmets`, `/verification` ; aérodromes et SIGMET sur la carte à l'heure de validité, panneau Aérodrome,
  page Validation. Premier résultat réel : convection diagnostiquée environ 4 fois trop fréquente (biais 4,15).
  Correctif : ouverture concurrente d'un cube sérialisée (plantage du serveur au démarrage).
  Voir `docs/awci/AWCI_WEB_SP3.md`.
- AWCI Web SP2, revue finale : un EUMETView lent ne retarde plus la prévision (relais : délai 5 s,
  concurrence bornée, mémoire des échecs, heures et tuiles validées contre les capacités, cache borné ;
  navigateur : 3 connexions de tuiles au plus). La carte n'affiche plus le champ d'une autre vue pendant
  un chargement ; liste des couches utilisable au clavier ; run épinglé dès la première interaction ;
  « pas de plafond » distingué de « sans donnée ».
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
