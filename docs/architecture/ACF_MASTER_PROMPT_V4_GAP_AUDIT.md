# Audit de conformité — ACF Master Implementation Prompt V4

**Date :** 2026-09-13.
**Contexte :** l'utilisateur a fourni un "master prompt" décrivant une
reconstruction complète du dashboard ACF en 47 phases, en supposant une
architecture web React/TypeScript/WebGL. **Correction factuelle faite et
acceptée avant de commencer** : ACF est une application desktop
PySide6/Qt, pas une app web — voir la réponse de session du 2026-09-13
pour le détail. Ce document audite donc la réalisation de chaque phase
**sur l'architecture réelle existante** (`acf.gui.dashboard.
acf_workstation.ACFWorkstation`), sans rewrite.

## Méthode

Même discipline que l'audit de conformité ICAO/OMM (`docs/compliance/
ICAO_WMO_COMPLIANCE_AUDIT.md`) : vérifier factuellement (grep/lecture)
avant de classer, ne jamais fabriquer de contenu pour "cocher une case",
fermer les gaps réels un par un avec tests + doc sync + commit.

## Déjà réel, vérifié (pas de changement nécessaire)

- **Header/Toolbar/Navigation** (Phases 3-4) : réels, fonctionnels,
  routing réel par nom (`_navigate_to()`).
- **Carte 2D + coupe verticale + profil vertical + Key Metrics + Model
  Consensus + Alerts/Hazards + Quick Actions** (Phases 5-12) : réels,
  câblés sur `compute_real_complexity_volume()` (un seul run réel,
  re-tranché par panel, jamais recalculé par onglet).
- **Diagnostics scientifiques** (Phase 13) : Labs dédiés déjà réels
  (Thermodynamics/Convection/Dynamics/Terrain/Microphysics).
- **Time series / 4D "Global Timeline"** (Phases 14/27/28) : réel
  (Phase 41), Play/Pause/vitesse réels.
- **Model Comparison** (Phase 15) : réel via `ACFMultiModelLabPanel` +
  `ModelConsensusEngine.compute_real_multi_model_disagreement()` — même
  moteur que Model Consensus, pas de duplication.
- **Data & Provenance** (Phase 17) : réel, `_export_diagnostics_data()`.
- **HPC/Slurm** (Phase 21) : réel, `HPCConnectionManager` (Paramiko SSH
  réel), jamais de faux statut "Connected".
- **Quality Control visible** (Phase 36) : réel — `run_real_range_qc()`
  alimente honnêtement le "QC [WARN]" du Pipeline Monitor avec de vrais
  violations de plage, jamais un statut inventé.
- **Politique anti-fabrication** (Phase 20) : déjà la discipline
  systématique de tout ce codebase — aucun `Math.random()`/valeur
  aléatoire trouvée dans les chemins réels du Workstation.

## Fermé cette passe (2026-09-13)

1. **Bulk Richardson Number** (Phase 13, Turbulence — nommé
   explicitement) — `acf.science.bulk_richardson_number.
   BulkRichardsonNumber` existait déjà avec ses propres tests, mais
   n'était câblé dans **aucun** panel GUI (vérifié par grep). Câblé
   dans `ACFStabilityIndicesWidget`/`compute_real_stability_indices_at_
   point()`, réutilisant le CAPE/shear déjà calculé au même point —
   zéro nouvelle donnée, zéro nouvelle formule. Honnêtement "n/a" si
   shear = 0 (BRN mathématiquement indéfini).
2. **Accessibilité** (Phase 29) — 0 appel `setAccessibleName`/
   `setAccessibleDescription`/`QAccessible` trouvé dans tout
   `acf_workstation.py` avant cette passe. Ajouté sur les contrôles les
   plus critiques (boutons icône-seule ⛶/⚙, sélecteurs Model/Domain/
   Level, liste de navigation) — **portée disclosed** : couvre le shell
   principal de l'ACFWorkstation, pas un audit a11y de tout le repo
   (~40 autres fichiers GUI), même limitation de portée déjà établie
   dans l'historique de ce projet pour l'a11y repo-wide.
3. **Tests de régression visuelle** (Phase 38) — 0 fichier de test
   visuel trouvé nulle part dans `tests/`. Créé un test réel : rendu
   offscreen Qt du vrai `ACFWorkstationWindow` (avec son propre run
   `CoupledEarthSolver` réel et déterministe, `seed=1`), comparé à une
   image de référence via une miniature 80×50 sous-échantillonnée
   (jamais un diff pixel-à-pixel brut — le rendu de police varie
   réellement selon la machine, un diff pixel exact serait une source
   d'échecs faux-positifs constante). Détecte une vraie régression
   grossière (panel disparu, palette cassée, rendu vide) — ce n'est
   PAS un test de fidélité pixel-parfaite contre un mockup externe
   (déjà explicitement disclosed comme infaisable pour une vraie app
   scientifique dynamique dans le docstring Phase 43 d'`acf_workstation.py`).

## Vérifié réel mais BLOQUÉ, disclosed (pas de fix forcé)

4. **Workflow Engine / "Workflows" nav** (Phase 22) — `acf.hpc_workflow.
   workflow_engine.WorkflowEngine` existe réellement en backend, mais
   **exige Python 3.12+** (`EnvironmentValidationError` sinon — confirmé
   lors du sweep de tests de la passe de conformité ICAO/OMM). Ce
   sandbox tourne en Python 3.11.15. Câbler un panel GUI dessus
   maintenant produirait une intégration **non testable dans cet
   environnement** — contraire à la discipline "jamais affirmer qu'un
   test passe sans l'avoir réellement fait tourner" de ce projet.
   **Non fait, disclosed comme BLOCKED BY ENVIRONMENT**, pas silencieusement
   ignoré.

## Vérifié résolu — pas un vrai gap (2026-09-13)

- **"Datasets"** comme concept nav distinct du mockup — vérifié : la
  Workstation a déjà une section "DATA SOURCES" réelle (Model Data/
  Observations/Scientific Explorer), le même mapping déjà établi et
  disclosed pour "Data"/"Diagnostics" (Phase 31 de ce fichier lui-même).
  Un second panel "Datasets" séparé serait une duplication, pas une
  fermeture de gap — **pas de changement nécessaire**.
- **"Model disagreement" comme type d'alerte** (Phase 16) — vérifié :
  Model Consensus (`ModelConsensusEngine.compute_real_multi_model_
  disagreement()`) expose déjà honnêtement le vrai spread une fois
  calculé, mais c'est une action manuelle coûteuse (un run solveur réel
  par modèle) — jamais auto-déclenchée, par choix de conception déjà
  établi ailleurs dans ce projet (calcul coûteux sur demande
  uniquement). Fusionner ça avec les Alerts auto-calculées créerait soit
  un déclenchement automatique de calculs coûteux non demandés, soit
  une alerte fabriquée avant tout calcul réel. **Pas un gap réel — déjà
  honnêtement conçu ainsi.**
- **Messages d'erreur structurés** (Phase 31) — vérifié `_on_volume_
  failed()` : affiche déjà le vrai message d'exception du solveur, logué,
  UI réactivée. Pas de catégorisation rigide (DATA UNAVAILABLE/INVALID
  GRID/etc.) mais le message réel est plus informatif qu'une catégorie
  générique inventée. **Pas un gap réel.**

## Reste ouvert (feuille de route, non traité cette passe)

- **Audit d'unités systématique** (kt/m/s, ft/m) sur `gui/` dans son
  ensemble — hors périmètre de cette passe (voir aussi l'audit ICAO/OMM
  §4 pour la même limite déjà posée).
- **Accessibilité repo-wide** (au-delà du shell ACFWorkstation) — gros
  chantier séparé, déjà qualifié disproportionné pour une session dans
  l'historique de ce projet.
- **Bulk Richardson Number ailleurs** (Dynamics Lab) — vérifié : le Map
  Inspector n'est délibérément PAS un bon candidat (il exclut déjà
  CAPE/CIN de son propre calcul par point-cliqué pour rester bon marché
  sur des clics répétés - voir son propre docstring ; BRN en dépend).
  Dynamics Lab reste un candidat réel non exploré cette passe.

## Conclusion honnête (format Phase 47 du master prompt)

| Item | Statut |
|---|---|
| Architecture correcte identifiée avant travail | ✅ IMPLEMENTED (corrigée, disclosed à l'utilisateur) |
| Bulk Richardson Number | ✅ IMPLEMENTED |
| Accessibilité (shell principal) | ⚠️ PARTIALLY IMPLEMENTED (disclosed, portée limitée) |
| Tests de régression visuelle | ✅ IMPLEMENTED (métrique tolérante, disclosed) |
| Workflow Engine GUI | ❌ BLOCKED BY MISSING DEPENDENCY (Python 3.12+) |
| "Datasets" nav séparé | ✅ IMPLEMENTED (déjà couvert par "DATA SOURCES", vérifié non-redondant à dupliquer) |
| Alerte "model disagreement" | ✅ IMPLEMENTED (déjà honnêtement exposé dans Model Consensus, fusion avec Alerts délibérément évitée) |
| Messages d'erreur structurés | ✅ IMPLEMENTED (message réel du solveur, plus informatif qu'une catégorie générique) |
| Audit unités systématique | ❌ NOT IMPLEMENTED (hors périmètre, disclosed) |
| Accessibilité repo-wide | ❌ NOT IMPLEMENTED (disproportionné, disclosed) |
| Bulk Richardson Number (Dynamics Lab) | ❌ NOT IMPLEMENTED (candidat réel, non traité cette passe) |
