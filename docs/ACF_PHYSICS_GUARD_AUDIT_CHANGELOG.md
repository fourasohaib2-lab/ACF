# ACF Physics Guard Audit — Changelog consolidé

**Période :** session(s) de correction menées en parallèle sur deux terminaux Claude Code
(branche `develop`), du commit `9223251` au commit `b27b695`.
**Portée :** 215 commits, ~2794 tests (100% verts à la fin), ruff clean, mypy clean,
`python -m compileall` clean.

## 1. Objectif et méthode

Un audit systématique, fichier par fichier, de l'ensemble du code source `src/acf/` à la
recherche de quatre familles de défauts, avec vérification contre la littérature/les
standards physiques réels avant toute correction (Doswell & Rasmussen 1994, Hunke &
Lipscomb 2008/CICE, Wanninkhof 2014, Magnus-Tetens, Stefan-Boltzmann, WMO/CF, IPCC AR6,
Rational Method, formule de Somigliana, Bolton 1980, Davies-Jones 1990, etc.) :

1. **Données fabriquées** présentées comme des résultats réels/calculés (valeurs fixes,
   statuts "SUCCESS"/"LIVE" inconditionnels, télémétrie inventée).
2. **Formules mal étiquetées** — le docstring revendique une formule/méthode nommée
   (Penman-Monteith, B-spline, Coriolis...) mais le code implémente autre chose ou omet
   un terme requis.
3. **Code réellement cassé** — crashes, méthodes hors du corps de la classe, imports
   circulaires, exceptions avalées silencieusement.
4. **Facteurs de calibration a posteriori** — diviseurs/offsets sans justification
   physique, ajustés uniquement pour faire passer un test donné.

**Convention de correction adoptée :** ne jamais supprimer silencieusement une
fonctionnalité en conflit ; remplacer la fausse donnée par une divulgation honnête
(`None`, statuts `"NOT_X_NO_Y_CONNECTED"`, marqueurs `"is_real_data": False"`), documenter
la correction dans le code via un commentaire `NOTE (correction): ...`, et mettre à jour
les tests verrouillés sur l'ancienne valeur erronée.

## 2. Répartition par thème (vue d'ensemble)

| Thème | Modules concernés (exemples) | Nature dominante |
|---|---|---|
| Encyclopédie scientifique (`science/encyclopedia`) | thermodynamics, microphysics, geodesy, cloud physics | `compute_func` manquants/mal câblés, formules mal étiquetées, doublons |
| HPC / connecteurs (`hpc_connector`, `hpc`, `hpc_workflow`) | cluster detection, SFTP, Slurm, MPI, sécurité, notifications | succès fabriqué sans canal réel, halo-exchange no-op |
| Digital Twin (`digital_twin`) | état Terre global, couplages, feedbacks, limites planétaires | vecteurs d'état fabriqués, résumé d'audit incohérent avec les données |
| Data assimilation / observations | ingestion SYNOP/Argo/satellite, EnKF/4D-Var | scores de qualité et comptes fabriqués |
| Visualisation (`visualization`) | layer_engine, volume_engine, GPU backend, AWCI dashboard | statuts LIVE/rendu GPU fabriqués sans backend connecté |
| ESOC / GUI opérateur | panneaux ESOC, terminal live, dashboard | ~20 panneaux affichaient des données "live" fabriquées |
| Aviation | décodeurs METAR/TAF/SIGMET | décodeurs non fonctionnels ou mal étiquetés (sentinelle 9999) |
| Modèle 4D physique (`model4d/physics`) | CAPE/CIN, radiation, ondes, turbulence, cyclones | ~40+ méthodes avec fudge factors / formules incomplètes |
| Hydrologie / géologie / océan | crue (Rational Method), déclinaison magnétique, JONSWAP | formules dimensionnellement fausses, valeurs fabriquées |
| AEOS / orchestration / intelligence | cluster manager, workflow engine, réponse d'urgence | statuts de cluster/tâche fabriqués |
| Release / monitoring | version, intégrité, licence, télémétrie | fausses certifications "PLATINUM CERTIFIED", version figée |

## 3. Corrections les plus critiques (impact opérationnel)

- **`af72b42`** — `hazard_operations` / `ai/emergency_assistant` : le cluster de faux
  stubs le plus dangereux de la session — données de catastrophe/urgence fabriquées.
- **`213e4fb`** — lecteur EPyGrAM : appel d'API cassé rendant impossible toute lecture
  réelle, masqué par des données de repli aléatoires/fabriquées.
- **`c727cbf`** — `ClusterDetector` fabriquait la détection matériel/logiciel HPC.
- **`bee1119`** / **`2eca930`** / **`f027d29`** — décodeurs METAR/TAF/SIGMET aviation :
  données fabriquées ou sentinelle `9999` mal interprétée comme une vraie distance.
- **`b25cc4d`**, **`006756b`** — `EarthState`/`GlobalEarthStateVector` : revendication de
  synchronisation live et vecteur d'état global entièrement fabriqués.
- **`caeb4bc`** — crue : formule de pointe de débit dimensionnellement impossible.
- **`7f358d5`** — rayonnement OLR : division par un "10.01" injustifié, corrompant
  Stefan-Boltzmann d'un ordre de grandeur (~391 → ~39 W/m²).
- **`cdecd3e`** — CAPE/CIN 100× trop petits, cassant leurs propres fonctions sœurs.
- **`b8bfa5e`** et suite (`query_engine.py`) — multiples "current state" et
  certifications fabriquées propagées dans plusieurs modules consommateurs.

## 4. Validation finale (cette passe)

Exécutée après la fin de l'audit fichier par fichier, sur l'état cumulé des deux
sessions parallèles :

- `pytest tests/` → **2794 passed**, 0 échec.
- `ruff check src/ tests/` → clean.
- `python -m compileall src/acf` → clean.
- `mypy src/acf --ignore-missing-imports` → **2 erreurs trouvées et corrigées**
  (commit `b27b695`) : deux régressions de typage introduites par les propres
  corrections "None au lieu de fausse donnée" de cette session
  (`digital_twin/planetary_limits/planetary_boundaries.py`,
  `geology/geomagnetism.py`) — pas des bugs préexistants, juste des annotations
  de type trop étroites pour leur propre valeur de retour.

## 5. Ce qui reste hors de cette passe

- `model4d/physics/` (~100 fichiers) et `science/` (~170 fichiers) n'ont pas été
  audités à 100% — le rythme de découverte de bugs a nettement diminué sur les
  derniers lots traités (volume_engine, layer_engine, radiation_balance), ce qui a
  motivé la pause de la chasse active fichier par fichier au profit de cette passe
  de validation et de consolidation.
- Le remote git `origin` pointe vers `https://github.com/TON_COMPTE/ACF.git`, qui
  ressemble à un placeholder jamais configuré — à corriger avant tout push/partage.
- Un projet séparé et plus restreint — un outil réutilisable qui automatiserait une
  partie des contrôles faits manuellement ici (recherche de constantes suspectes,
  valeurs fabriquées, docstring vs implémentation) — a été évoqué mais volontairement
  **non lancé**, en attente d'une décision explicite.

## 6. Référence complète des commits

Pour le détail commit-par-commit : `git log --oneline 9223251..b27b695`.
