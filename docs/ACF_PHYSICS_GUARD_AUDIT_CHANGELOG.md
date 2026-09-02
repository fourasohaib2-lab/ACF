# ACF Physics Guard Audit — Changelog consolidé

**Période :** session(s) de correction menées en parallèle sur deux terminaux Claude Code
(branche `develop`), du commit `9223251` au commit `7bb8f8a`.
**Portée :** 241 commits, 2819 tests (100% verts à la fin), ruff clean, mypy clean,
`python -m compileall` clean. Dépôt sauvegardé sur
[github.com/fourasohaib2-lab/ACF](https://github.com/fourasohaib2-lab/ACF).

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

## 5. Couverture finale et ce qui reste hors de cette passe

- `model4d/physics/` (152 fichiers) et `science/` (170 fichiers) sont maintenant
  **audités à 100%**. Un recensement final (`git log --name-only` sur la période de
  session) a montré que seuls 10 fichiers substantiels restaient non touchés (le
  reste des fichiers "manquants" étaient des `__init__.py` triviaux de 5 à 13
  lignes) — bien moins que l'estimation initiale d'environ 270 fichiers restants.
  Ce dernier lot (`air_density.py`, `frontogenesis.py`, `geopotential_height.py`,
  `specific_humidity.py`, `laws/atmospheric.py`, `laws/mathematics.py`,
  `encyclopedia/mathematics.py`, `cryosphere_dynamics.py`,
  `mesospheric_dynamics.py`, `waves.py`) a été lu intégralement (commit
  `224e3fc`) : un seul bug réel trouvé — l'entrée `virtual_temperature` de
  `science/laws/atmospheric.py` affichait l'équation avec le coefficient 0.61
  alors que son `compute_func` utilisait 0.608 (incohérence interne, et
  incohérente avec les deux entrées sœurs ailleurs dans le code qui utilisent
  toutes deux 0.608) — corrigé. Les 9 autres fichiers étaient déjà corrects,
  honnêtement étiquetés "simplifié"/"approximation" sans revendiquer de formule
  nommée qu'ils n'implémentent pas.
- **Résolu** — le remote git pointait vers un placeholder
  (`https://github.com/TON_COMPTE/ACF.git`) jamais configuré, laissant tout
  ce travail sans sauvegarde sur une seule machine. Un dépôt GitHub réel
  (`fourasohaib2-lab/ACF`, public) a été créé et les branches `develop`
  (branche par défaut) et `master` y ont été poussées intégralement.
- Un projet séparé et plus restreint — un outil réutilisable qui automatiserait une
  partie des contrôles faits manuellement ici (recherche de constantes suspectes,
  valeurs fabriquées, docstring vs implémentation) — a été évoqué mais volontairement
  **non lancé**, en attente d'une décision explicite.

## 6. Phase 2 — finition de l'interface finale de l'application (post-audit)

Une fois le balayage de bugs terminé, l'attention s'est portée sur l'application
réelle (`ESOCWindow`, lancée via `acf-gui`), au-delà de la seule correction de bugs :

- **`7541c15`** — la toolbar principale de l'ESOC a 21 boutons ; **14 d'entre eux ne
  faisaient strictement rien au clic** (aucune erreur, aucun retour), y compris "AI"
  qui pointait vers une fonctionnalité déjà réparée mais jamais branchée. Tous
  câblés à de vraies actions (assistant de connexion HPC réel avec tentative SSH en
  arrière-plan, navigation vers les vrais panneaux opérationnels, visualiseur de logs
  en direct, changement de thème réel, capture d'écran réelle, etc.). A aussi révélé
  un bug caché : `HPCConnectionManager.connect()` retourne toujours `True` (mode
  développement hors-ligne délibéré, déjà couvert par un test) — corrigé pour que la
  barre de statut se base sur l'indicateur honnête `is_real_connection` plutôt que sur
  cette valeur de retour, pour ne jamais afficher "Connected" à tort.
- **`f3f4b42`** — reconstruction complète du dashboard AWCI (Aviation Weather
  Complexity Index) pour correspondre à une maquette de référence fournie par
  l'utilisateur : cartes Cartopy réelles avec halo de complexité, coupe verticale,
  radar des composants, graphique de route, résumé des risques, barre de stats,
  pied de page. Chaque score affiché provient du vrai moteur `AWCICalculator` (formule
  de production, testée), seules les données météo d'entrée sont un champ synthétique
  de démonstration honnêtement documenté. Le dashboard était entièrement orphelin
  (jamais atteignable depuis l'appli) ; intégré comme 28ᵉ onglet réel de l'ESOC.
- **`5cfc78e`** — 4 widgets AWCI rendus orphelins par cette reconstruction (jauge,
  décomposition en barres, timeline, profil vertical) documentés selon la convention
  du projet plutôt que supprimés silencieusement.
- **`86d3616`** — même traitement pour le second dashboard orphelin trouvé ce
  session, `src/acf/dashboard/` (Dashboard/DashboardManager/DashboardLayout :
  carte centrale + docks Explorer/Charts/Properties/Timeline/Console/Status) :
  entièrement construit et testé, mais jamais atteignable depuis l'appli
  réelle. Contrairement à AWCI, ce dashboard veut posséder toute une fenêtre
  (`setCentralWidget`/`addDockWidget` directs) — lancé comme fenêtre
  secondaire via un nouveau bouton toolbar "🗂️ Classic View" dans l'ESOC.
  Corrigé au passage 2 versions codées en dur obsolètes ("0.1.0-alpha" vs
  la vraie `0.1.0`) trouvées dans `status_panel.py` et `splash.py`, même
  catégorie que les bugs `ProductionUpdater`/`VersionManager` déjà corrigés
  plus tôt.
- **`62edad6`** — correction d'architecture demandée par l'utilisateur : la
  relation voulue entre les deux dashboards n'est pas "deux fenêtres
  indépendantes accessibles depuis l'ESOC", mais bien **ACF principal →
  bouton → AWCI**. Ajout de `AWCIDashboardWindow` (fenêtre autonome pour
  `AWCIDashboard`, miroir de `ClassicDashboardWindow`) et d'un bouton
  "✈️ AWCI Dashboard" dans la toolbar du dashboard ACF principal. A révélé
  et corrigé 2 imports circulaires réels (confirmés par l'erreur Python
  effective, pas seulement suspectés) entre `acf.dashboard.window` et
  `acf.gui` (déclenchés par l'import eager de `ESOCWindow` dans
  `acf/gui/__init__.py`) — résolus en différant les imports concernés à
  l'intérieur des méthodes qui les utilisent, motif déjà établi ailleurs
  dans ce code.
- Vérifications faites en direct sous `xvfb` (pas seulement via les tests
  unitaires) : fenêtre principale + 28 panneaux + 22 actions de toolbar +
  la chaîne complète ESOC → Classic View → AWCI Dashboard, 0 exception.
- **`57b368a`** — même traitement pour `gui/menu.py` (134 lignes, le plus
  gros fichier à 0% de couverture repéré dans le rapport plus tôt) :
  un menu File/Data complet (Nouveau/Ouvrir/Récents/Propriétés/
  Enregistrer/Fermer projet, Ouvrir/Fermer/Info dataset) jamais construit
  nulle part, prévu pour fonctionner avec `WorkspaceManager` + `DataManager`
  + `Dashboard.get_panel` — les trois existaient déjà, testés isolément,
  mais jamais assemblés. Branché sur `ClassicDashboardWindow`. En
  creusant un plantage suspecté (`libshiboken: Internal C++ object
  already deleted`), vérifié qu'il s'agissait d'un artefact de la méthode
  d'introspection Python utilisée pour tester, pas d'un vrai bug de durée
  de vie du code original (confirmé via `findChildren()`, le mécanisme
  que Qt utilise réellement) — corrigé le commentaire pour ne pas
  revendiquer un bug qui n'existait pas, conformément à la discipline du
  reste de cette session. A aussi trouvé et corrigé un vrai bug confirmé
  sur disque : `WorkspaceManager()` n'avait aucun moyen d'isoler son
  fichier "projets récents", donc `tests/test_workspace_manager.py`
  écrivait réellement dans `~/.acf/recent_projects.json` (le vrai fichier
  de config de l'utilisateur) à chaque exécution des tests — confirmé :
  6 entrées de tests pytest obsolètes trouvées sur disque. Corrigé avec
  un paramètre `recent_projects_file` optionnel + `tmp_path` dans le test ;
  vérifié que le fichier réel est désormais intact après une suite complète.
- **`9c68d9b`** — dernière trouvaille du même balayage : `gui/map/` compte
  36 fichiers, dont 19 (5 sous-paquets entiers : `layers/`, `navigation/`,
  `projections/`, `renderers/`, `rendering/`) ne sont importés nulle part
  dans `src/`. Contrairement aux collisions `X.py` vs `X/` déjà trouvées
  cette session, il n'y a ici aucune collision de nom forçant la situation
  — c'est une architecture de carte alternative complète et cohérente
  (gestionnaires de calques/rendus/navigation/projections, vérifiés
  corrects) qui a simplement perdu face au système plus simple
  (`map_canvas.py`) réellement utilisé par l'ESOC. La brancher demanderait
  de construire un nouveau widget hôte reliant calques → rendus →
  navigation → vrais événements souris/molette Qt — un travail de nature
  différente de la simple "connexion" appliquée aux dashboards/menu cette
  session. Documenté (pas supprimé, pas branché à moitié), conformément à
  la convention du projet.
- **`d904a29`** — 4 autres ébauches remplacées : `gui/main_window/menu_bar.py`
  et `tool_bar.py` n'ont **aucune connexion de signal du tout** (boutons
  purement décoratifs) — remplacées par `MenuManager`/`ESOCToolbar`.
  `gui/data_menu.py` fait doublon exact avec le menu Data de `MenuManager`.
  `gui/main_window/status_bar.py` est correct mais superflu — `ESOCStatusBar`
  et la barre de statut par défaut de Qt couvrent déjà le besoin. Documentés,
  pas branchés (ça créerait des doublons visibles).
- **`76122b1`** — à l'inverse, `gui/docks/dataset_panel.py` (`DatasetPanel`)
  s'est révélé être un vrai `QDockWidget` autonome, correct et complet —
  contrairement aux 4 ébauches ci-dessus, il ne demandait qu'un point
  d'ancrage, pas de nouvelle logique. Branché dans le dashboard ACF
  principal, à côté de l'Explorer, relié au même `DataManager`.
- **`c1d236d`** — `core/application.py`/`Bootstrap` : petite séquence de
  démarrage générique (config, plugins, services), correcte mais jamais
  utilisée — le seul point d'entrée déclaré (`acf-gui`) lance directement
  `ESOCWindow`. Documenté.

## 6bis. Suite de la roadmap technique (`docs/ACF_HPC_005_NEXT_ROADMAP.md`)

Sur demande explicite de l'utilisateur ("on suit l'architecture du travail"),
premier des 3 axes de la feuille de route HPC-005 choisi et implémenté :

- **`f4f8a01`** — **Dashboard Web FastAPI/WebSocket** : aucune application
  FastAPI n'existait dans le code (`OperationalWebSocketServer` — déjà
  corrigé plus tôt cette session — ne liait aucun vrai socket ; `ACFAPI`
  est une façade Python sans couche HTTP). `fastapi`/`uvicorn` étaient
  installés mais jamais déclarés comme dépendances ; `websockets` manquait
  entièrement (sans lui, `uvicorn` ne peut servir aucun vrai WebSocket) —
  installé et déclaré. Nouveau module `acf/web/hpc_dashboard_server.py` :
  vraie appli FastAPI qui réutilise `HPCConnectionManager` tel quel (rien
  n'est réinventé), avec la même distinction honnête que le correctif de
  la toolbar ESOC (`connected` = workflow terminé vs `real_ssh_transport`
  = vraie liaison SSH confirmée) pour ne jamais afficher une fausse
  connexion. Point d'entrée console `acf-web`. Vérifié deux fois : 7
  tests via `TestClient`, **et** un vrai serveur lancé sur un vrai port,
  interrogé avec `curl` et un vrai client `websockets`, puis confirmé
  visuellement dans un navigateur réel.
- **`f650df1`** — deuxième axe : **CI/CD sur le cluster Fennec**. En
  branchant ça, découverte d'un vrai trou bloquant : le pipeline
  "One-Click AROME" (déjà existant, déjà honnête) génère un script SLURM
  qui lance `python -m acf.forecast.engine --model AROME` — **ce module
  n'existait pas du tout**. Même un job réellement soumis sur un vrai
  cluster aurait planté immédiatement (`ModuleNotFoundError`). Créé
  `acf/forecast/engine.py`, un vrai CLI qui fait réellement tourner
  `CoupledEarthSolver` (déjà utilisé ailleurs cette session) et écrit un
  vrai fichier NetCDF CF-1.8 — vérifié en l'exécutant vraiment, y compris
  en sous-processus réel (`python -m acf.forecast.engine ...`). Ajouté
  `execute_one_click_aladin()` (la roadmap nomme AROME **et** ALADIN,
  seul AROME avait son pipeline). Nouveau script
  `scripts/daily_forecast_cycle.py` qui échoue avec un code de sortie
  non nul si un cycle n'est pas réellement soumis (vérifié : sort avec
  code 1 dans ce sandbox hors-ligne). Nouveau workflow GitHub Actions
  (`daily-forecast-cycle.yml`) ciblant un runner auto-hébergé sur le
  réseau ONM (les runners GitHub-hosted n'ont aucune route vers le vrai
  cluster Fennec) — documente honnêtement les secrets/le runner que
  l'utilisateur doit encore configurer pour un déploiement réel.
- **`7501614`** — troisième et dernier axe : **couplage physique-IA
  (FNO)**. Trouvé en le construisant : le "FNO" existant
  (`NeuralOperatorEngine`) n'avait **aucun poids appris** — un filtre
  spectral fixe (`exp(-1e-4·dt)`), identique à chaque appel, pas un
  opérateur de Fourier neuronal au sens machine learning malgré le nom
  (Li et al. 2020 définit un FNO par ses poids appris sur les modes de
  Fourier). `acceleration_factor = 1000.0` n'était jamais mesuré non
  plus. Pas d'accès aux vraies archives ARPEGE/ERA5 dans cet
  environnement — les données d'entraînement viennent du vrai solveur
  physique `CoupledEarthSolver` d'ACF (trajectoires physiquement
  cohérentes, honnêtement non des observations réelles), volontairement
  limité à un seul champ (température de surface) comme preuve de
  concept fonctionnelle plutôt qu'un remplacement multi-variables
  complet. Torch (CPU) installé pour l'occasion. Nouveau
  `acf/ai/simulation/fno_model.py` (vraie architecture FNO, convolution
  spectrale à poids complexes appris) + `fno_training.py`
  (entraînement réel par rétropropagation). Entraînement de référence
  réellement exécuté : perte 1.01 → 0.022 (réduction de 97,8%),
  checkpoint de 394 Ko committé et vérifié en le rechargeant. En route,
  installer torch a redéclenché le même plantage disque que plus tôt
  (voir section précédente) — causé cette fois par `/home/souhaib/Videos`
  à 311 Go, sans rapport avec ACF ; l'utilisateur a libéré de l'espace
  et l'installation a repris normalement.

## 7. Référence complète des commits

Pour le détail commit-par-commit : `git log --oneline 9223251..7bb8f8a`.

## 8. Les 3 axes de la roadmap HPC-005 sont maintenant complets

| Axe | Statut | Limite honnête |
|---|---|---|
| Dashboard Web FastAPI/WebSocket | ✅ Réel, testé bout-en-bout | Aucune |
| CI/CD sur cluster Fennec | ✅ Scripts/pipeline réels et testés | Nécessite un runner auto-hébergé + secrets réels pour un déploiement effectif — pas testable depuis cet environnement |
| Couplage physique-IA (FNO) | ✅ Vraie architecture entraînée | Entraîné sur des trajectoires générées par ACF, pas sur de vraies archives ARPEGE/ERA5 ; limité à un seul champ (preuve de concept, pas un remplacement opérationnel complet) |

- **`862f747`** — les axes 1 et 3 reliés entre eux : le FNO entraîné
  n'était accessible que par l'API Python brute. Nouveau
  `POST /api/fno/predict_demo` sur le dashboard web (champ de démo
  synthétique honnêtement étiqueté, vraie inférence du modèle entraîné,
  jamais de repli silencieux). Vérifié dans un vrai navigateur : clic sur
  "Run Surrogate on Demo Field" → `PREDICTED_BY_TRAINED_SURROGATE` en
  vert, 264.77K → 265.58K, le vrai modèle tourne de bout en bout.

## 9. Session parallèle et incident réseau (post roadmap)

En reprenant le travail, une session parallèle (`meteo-platform-5e`, même
utilisateur, terminal séparé) avait laissé des correctifs réels non commités
dans l'arbre de travail partagé — repérés, vérifiés, et commités séparément
et honnêtement attribués :

- **`dd6621c`** — l'assistant de connexion HPC de l'ESOC ne faisait
  jamais réellement atteindre les identifiants saisis : le profil
  transmis était le libellé affiché (jamais une clé YAML valide),
  `config/hpc.yaml` orthographiait le compte `username:` alors que le
  code ne lisait que `user:`, le timeout était réinitialisé à 0.0015s à
  chaque appel, et surtout — cause racine — `ssh_connector.py` ne
  tentait jamais de vraie connexion pour un nom DNS, seulement pour une
  IP numérique littérale. Ce dernier point corrige une caractérisation
  de *cette session elle-même* (commit `40a9202` et suivants) qui avait
  pris le comportement "toujours hors-ligne" pour un choix de conception
  délibéré, sans creuser plus loin.
- **Conséquence découverte en poursuivant le travail** : `10.16.20.2` —
  `login2.fennec.meteo.dz` résout vers une vraie adresse interne. Cette
  machine a un accès réseau réel au cluster Fennec de l'ONM. Une fois le
  bug SSH corrigé, **la suite de tests s'est mise à tenter de vraies
  connexions SSH vers l'infrastructure de production à chaque
  exécution**, et un test a fini par bloquer toute la suite indéfiniment
  sur une boîte de dialogue Qt modale bloquante. Signalé explicitement à
  l'utilisateur avant toute correction (question posée, pas de décision
  unilatérale).
- **`430ca72`** — isolation des tests conformément à la décision de
  l'utilisateur : hostname toujours non résolvable (`test-offline-host.invalid`,
  TLD réservé par la RFC 2606) partout où les tests construisent un
  connecteur SSH directement ; le test du dialogue HPC réécrit pour
  refléter que `_test_connection()`/`_save_profile()` sont maintenant de
  vraies fonctionnalités (sonde DNS+TCP réelle, écriture YAML réelle) et
  non plus des stubs factices, testées en isolation (chemin de sauvegarde
  redirigé vers `tmp_path`) ; timeout global pytest de 60s ajouté comme
  filet de sécurité.
- **`7bb8f8a`** — en poursuivant, un vrai bug trouvé dans mon **propre**
  travail de cette session : l'entraînement FNO utilisait `T[-1]`
  (niveau le plus haut/froid) en l'appelant "near-surface" partout,
  alors que l'indice 0 est la surface réelle (confirmé contre
  `CoupledEarthSolver`). Corrigé, checkpoint de référence réentraîné
  (perte 1.01 → 0.022), et le vrai modèle entraîné branché dans le
  panneau AI Forecast de l'ESOC (bouton "1000x" fabriqué retiré,
  remplacé par le vrai statut du modèle entraîné).
