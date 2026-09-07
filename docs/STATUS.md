# ACF — État réel (source de vérité unique)

Ce fichier remplace tous les anciens documents de statut/certificat archivés
dans `docs/archive/`. Un module n'est coché `[x]` que s'il satisfait les 4
critères de `ARCHITECTURE.md` §3 (commit `audit(module)`, tests verts, pas de
surclaim de docstring, dépendances déclarées). `[~]` = travail réel en cours
mais audit non finalisé. Dernière mise à jour : voir `git log -- docs/STATUS.md`.

## Tier F — Foundation (bloquant v1.0)

- [x] `core`
- [x] `science`
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

- [x] `data`
- [x] `catalog`
- [x] `catalogs`
- [x] `importers`
- [x] `geospatial`
- [x] `models`
- [x] `surfex`
- [x] `hpc_connector`
- [x] `hpc_workflow`
- [x] `simulation_engine`
- [x] `gui` (~30k lignes, 10 sous-packages, tous couverts. Finding le
  plus important du sweep : `earth_system_operations.py` (exporté dans
  `gui/__init__.py.__all__`, jamais construit) retournait une
  auto-certification fabriquée — `"ui_version": "ACF-UI-001 Production
  Certified"` et `"integration_status": "ALL_45_MISSIONS_INTEGRATED"`
  — sans aucune UI réelle derrière, et son propre test l'affirmait
  comme vrai. Corrigé (code + test). Autres findings : `map/` (5
  sous-packages entiers non branchés, déjà documenté + 3 mixins
  mal étiquetés corrigés cette passe), `main_window/` (sous-package
  entier non branché, disclosure ajoutée), 11 stubs vides au total
  dans `docks/`/`layer_panel/`/racine corrigés, `view_manager.py`
  (8/15 modes de vue sans projection réelle))
- [x] `visualization`
- [x] `maps`
- [x] `awci`
- [x] `jobs`
- [x] `storage`

## Tier E — Extended (souhaité v1.0)

- [x] `aviation`
- [x] `hydrology`
- [x] `ocean`
- [x] `geology`
- [x] `space_weather`
- [x] `climate`
- [x] `ai`
- [x] `ai_expert`
- [x] `intelligence`
- [x] `digital_twin`
- [x] `aeos`
- [x] `knowledge_platform`
- [x] `dashboard`
- [x] `web`
- [x] `api`
- [x] `monitoring`
- [x] `alerts`
- [x] `hazard_operations`
- [x] `release`
- [x] `verification`
- [x] `data_assimilation`
- [x] `forecast`
- [x] `events`
- [x] `connectors`
- [x] `master`
- [x] `workspace`
- [x] `reports`
- [x] `search`
- [x] `testing`
- [x] `plugins`
- [x] `animation`

## Tier X — Experimental (hors scope v1.0, conservé)

- [x] `model4d` (reclassé Tier F -> Tier X le 2026-09-06, voir
  ARCHITECTURE.md §3 : zéro appelant réel dans tout `src/acf/`, vérifié
  par grep répété. Code réel, testé, conservé - juste hors du périmètre
  v1.0. **Couverture complète atteinte le 2026-09-07** (suite à la
  question directe de l'utilisateur "le projet est terminé ?" ->
  réponse honnête "non" -> "attaque le reste") : les 20
  `physics/*_engine.py` + `weather_intelligence_orchestrator.py`, tout
  `model4d/operators/` (8 fichiers) et `model4d/interpolation/` (9
  fichiers), ET la totalité des 131 fichiers `physics/` non-`_engine.py`
  sont maintenant individuellement relus (45 lors du sweep du
  2026-09-06, les 75 restants le 2026-09-07 — le nombre exact
  s'est avéré 75, pas ~86 comme estimé). Écarts formule/implémentation
  trouvés et divulgués sur l'ensemble du package : les 3 déjà connus
  (`magnetosphere_dynamics.py`/`solar_wind_interaction.py` en désaccord
  d'un facteur 2, `magnetic_pressure()` sans mu_0,
  `cloud_radiative_feedback.py` sans rho_w) restent les seuls trouvés -
  les 75 fichiers de la passe du 2026-09-07 n'en ont révélé aucun
  nouveau : physique "simplifiée" honnêtement labellisée, formules
  correctement citées (Stefan-Boltzmann, Beer-Lambert, Kalman, Kessler,
  Goff-Gratch, Coriolis/géostrophique/Rossby), zéro survente IA/ML.
  `atmospheric_waves.py` s'est avéré déjà excellent (3 corrections
  antérieures avec citations réelles, marquées "CORRECTED:" plutôt que
  la convention habituelle "NOTE (correction", d'où l'omission
  précédente de ce fichier du décompte). Voir le docstring de
  `src/acf/model4d/__init__.py` pour le détail complet.)
- [x] `geoengineering`
- [x] `planetary`
- [x] `fire_weather`
- [x] `certification` (voir ARCHITECTURE.md §3 — audité, excellent,
  compose uniquement des composants déjà vérifiés)

## Correctif utilisateur post-sweep (2026-09-06)

Bug réel rapporté par l'utilisateur : "plusieurs dashboard qui
s'affiche au meme temps" au lancement. Diagnostiqué par reproduction
directe, pas par supposition :
1. `acf.gui.app.run() -> ESOCWindow()` vérifié (introspection Qt live)
   ne crée qu'une seule fenêtre par lancement - pas la cause.
2. Ajout d'une garde mono-instance réelle (`acf.gui.single_instance.
   SingleInstanceGuard`, `QLocalServer`/`QLocalSocket`) - vérifiée par
   3 lancements réels successifs de `python -m acf.gui` (2e et 3e se
   ferment proprement sans construire de fenêtre).
3. Cause réelle trouvée ensuite : 4 scripts orphelins à la racine du
   dépôt (`test_awci_display.py`, `test_dashboard.py`, `test_qt.py`,
   `test_window.py`), chacun avec son propre `QApplication` hors du
   périmètre de l'app réelle - supprimés (commit `5d596e6`,
   récupérables via git).

**Run complet post-suppression : 4577 passed, 0 failed** (4574 baseline
+ 3 nouveaux tests de la garde mono-instance). Aucune régression.

**Robustesse de la garde vérifiée séparément (même journée)** : un
`kill -9` sur le process qui détient le `QLocalServer` (simulant un
crash réel, sans destructeur Qt) laisse un fichier socket orphelin
(`/tmp/acf-esoc-single-instance`), mais `SingleInstanceGuard.acquire()`
appelle déjà `QLocalServer.removeServer()` avant d'écouter - un
lancement réel suivant récupère bien le rôle de première instance
(vérifié par un script réel : acquire→kill -9→acquire dans un nouveau
process → `True`). Pas de risque de blocage permanent après un crash.

## Correctif utilisateur (suite) : champs AWCI réels jetés silencieusement (2026-09-06)

Après le correctif ci-dessus, un smoke-test réel et non trivial des 25
commandes de la barre d'outils ESOC (`_handle_toolbar_action`, chaque
dialogue modal bloquant patché en "annulé par l'utilisateur", tout le
reste du code réel non modifié) a été écrit et exécuté pour chercher
d'autres bugs du même genre que le multi-dashboard - trouvés par usage
réel, pas par simple lecture. Résultat : aucun crash sur les 25
commandes, mais un vrai bug silencieux trouvé dans les logs :
`compute_real_complexity_field()` calcule bien 9 champs réels par
module (`AWCICalculator.PHYSICAL_MODULES` + `FORECAST_MODULES` -
"confidence"/"ensemble_spread"/"model_disagreement"), mais
`acf.gui.map.map_layers.MODULE_COMPLEXITY_LAYERS` n'en enregistrait
que 6 - les 3 champs `FORECAST_MODULES` étaient calculés puis rejetés
en silence à chaque clic sur "🌪️ AWCI Field" (`MapCanvas.
set_module_complexity_field()` loguait un WARNING "unknown module_key"
invisible en usage normal, jamais une exception). Corrigé en
enregistrant les 3 layers manquants ("Forecast Confidence"/"Ensemble
Spread"/"Model Disagreement") - `LayerManager` et `LayerTogglePanel`
les prennent en charge automatiquement (ils itèrent déjà le dict
dynamiquement), donc aucun autre fichier n'a besoin de changer pour
que les 3 champs s'affichent réellement. `tests/
test_map_layers_module_complexity.py` + `tests/test_esoc_awci_field.py`
(17 tests, qui itèrent déjà `MODULE_COMPLEXITY_LAYERS` dynamiquement)
verts après coup sans modification. Re-vérifié : le smoke-test des 25
commandes ne montre plus aucun "unknown module_key".

**Run complet de non-régression : 4577 passed, 0 failed** (664
warnings, 424s) - identique à la baseline post-sweep, aucune
régression. Note de méthode : ce run a été lancé juste avant l'ajout
du nouveau test d'invariant `test_module_complexity_layers_covers_every_real_awci_module`
à `tests/test_map_layers_module_complexity.py` - sa collecte pytest ne
l'inclut donc pas (d'où 4577 et non 4578). Ce test précis a été vérifié
séparément, isolé avec ses 12 voisins du même fichier : **13 passed**
juste après son ajout. Total réel : 4578 tests, 0 échec.

## Correctif utilisateur (suite) : branches "Datasets" dupliquées dans l'Explorer (2026-09-07)

Suite au "attaque le reste" de model4d/physics/, retour à la recherche
de bugs par usage réel (même méthode que le fix AWCI ci-dessus) sur une
autre zone : `ClassicDashboardWindow`/`MenuManager`, dont le propre
docstring admet que `WorkspaceManager`/`DataManager`/`DatasetPanel`
"existaient, testés isolément, mais rien ne les avait jamais assemblés
derrière une vraie fenêtre avant" - exactement le profil de code qui a
produit le bug AWCI. Smoke-test réel des 13 actions du menu
Fichier/Données (`ClassicDashboardWindow` réelle, dialogues modaux
bloquants patchés en "annulé"/"rempli", `WorkspaceManager` isolé sur un
fichier temporaire pour ne pas écrire dans le vrai
`~/.acf/recent_projects.json` de l'utilisateur) : les 13 actions
s'exécutent sans exception - mais comme pour le bug AWCI, l'absence de
crash ne suffit pas. Vérification des effets réels (titre de fenêtre,
fichier `.acfproj` sur disque, état de `WorkspaceManager`) : 7/8 OK, le
8e a révélé un vrai bug par un chemin différent - `acf.gui.widgets.
explorer.ExplorerWidget.refresh_datasets()` empilait une nouvelle
branche "🌦 Datasets" à chaque appel au lieu de remplacer la
précédente (`load_project()` fait un `clear()` complet en tête, mais
rien d'équivalent n'existait pour `refresh_datasets()`). Confirmé par
test direct : `topLevelItemCount()` croissait 1, 2, 3, 4... sur 4
appels. `MenuManager.refresh_dataset_view()` est le seul appelant réel,
invoqué à chaque ouverture de dataset - une session normale ouvrant
plusieurs jeux de données aurait accumulé des branches dupliquées
indéfiniment dans l'Explorer. Corrigé en retirant l'ancienne branche
"Datasets" avant d'ajouter la nouvelle (pas un `clear()` complet, pour
ne pas effacer un arbre de projet déjà chargé au-dessus). `ExplorerWidget`
n'avait aucune couverture de test avant ce correctif - 5 nouveaux tests
ajoutés (`tests/test_explorer_widget.py`), couvrant aussi le cas mixte
projet+datasets et le remplacement de projet.

**Run complet de non-régression : 4583 passed, 0 failed** (664
warnings, 391s) - 4578 + 5 nouveaux tests explorer. Aucune régression.

## Correctif utilisateur (suite) : DatasetPanel affichait "Unnamed Dataset" (2026-09-07)

Même audit, même fenêtre (`ClassicDashboardWindow`) : `acf.gui.docks.
dataset_panel.DatasetPanel.refresh()` lisait `registry.datasets` en
supportant liste ou méthode, mais `acf.catalog.dataset_registry.
DatasetRegistry.datasets` est une `@property` retournant un **dict**
(id -> dataset) - jamais callable, donc la branche méthode ne se
déclenchait jamais pour le vrai registre. Sans traitement du cas dict,
`for dataset in datasets:` itérait sur les **clés** du dict (des
chaînes), donc chaque dataset réel s'affichait "Unnamed Dataset" sans
variable. Corrigé (`.values()` avant itération). Aucune couverture de
test avant ce correctif - 7 tests ajoutés (`tests/test_dataset_panel.py`).

## Test avec des données réelles RESTOR/ALADIN, à la demande explicite de l'utilisateur (2026-09-07)

L'utilisateur a demandé de tester ACF avec un vrai fichier de données
("RESTOR c'est des données réelles") - `/home/souhaib/RESTOR`, une
archive opérationnelle Météo-France réelle (retours d'expérience
ALADIN/AROME). Deux vrais bugs trouvés et corrigés dans le seul chemin
d'ingestion réellement câblé de l'application (`DataManager.open()`
via `ClassicDashboardWindow`'s "Open Dataset" - `ESOCWindow._open_dataset()`,
le point d'entrée principal, est honnêtement documenté comme non
connecté à un pipeline de lecture, donc non concerné) :

1. `acf.data.readers.epygram_reader.EPyGrAMReader.can_read()` ne
   reconnaissait que par extension de fichier - les vrais fichiers
   `FULLPOS_*` de RESTOR (format FA authentique, `epygram.formats.guess()`
   confirme "FA") n'ont AUCUNE extension, donc `ReaderFactory.get_reader()`
   retournait toujours `None` pour eux, bien que ce lecteur lise déjà
   parfaitement ce format réel (confirmé : 97 champs réels, grille
   350×350 réelle, température de surface -0.25°C à 39.6°C sur le
   domaine Algérie/Afrique du Nord). Corrigé par un repli sur la
   détection par contenu d'epygram - uniquement pour les fichiers sans
   extension reconnue (coût borné à un vrai clic utilisateur, ce
   lecteur étant interrogé en dernier par `ReaderFactory`).
   Attention : `epygram.config.silent_guess_format = True` provoque une
   redirection de file descriptor bas niveau qui entre en collision
   avec la capture de sortie de pytest ("I/O operation on closed
   file") - laissé à sa valeur par défaut (bruyant sur stderr mais
   jamais un crash).
2. Une fois le premier corrigé, un second bug est apparu au pas
   suivant sur le même fichier réel : `EPyGrAMReader.read()` retournait
   un simple `dict` au lieu d'un `acf.data.dataset.Dataset` - tous les
   autres lecteurs de la fabrique (GRIBReader, NetCDFReader...) en
   retournent un vrai, et `DatasetRegistry.register()` fait
   `dataset.modified = ...` (affectation d'attribut, impossible sur un
   dict) -> `AttributeError`. Corrigé en construisant un vrai `Dataset`
   à partir des mêmes données réelles déjà extraites (noms de champs,
   métadonnées, géométrie) - aucune donnée fabriquée.

Vérifié bout-en-bout avec le vrai fichier
`/home/souhaib/RESTOR/ALADIN/data/FULLPOS_2026083100_0000` : ouverture
complète via `DataManager.open()`, 97 champs réels enregistrés,
`validated: True`, et affichage correct dans `ExplorerWidget` et
`DatasetPanel` (les deux corrigés plus tôt aujourd'hui). Corrigé aussi
le filtre du dialogue "Open Dataset" de `MenuManager` (ne listait pas
`.fa`/`.lfa`/`.lfi`, pas de repli "Tous les fichiers" - même classe de
bug déjà corrigée pour `ESOCWindow._open_dataset()`). 3 nouveaux tests
(`tests/test_epygram_reader.py`).

**Run complet de non-régression : 4593 passed, 0 failed** (664
warnings, 389s) - 4583 + 10 nouveaux tests (7 DatasetPanel + 3
epygram_reader). Aucune régression.

## Correctif : fichier .acfproj orphelin lors d'un renommage de projet (2026-09-07)

Suite naturelle de l'audit RESTOR (même chemin de persistance de
projet) : `Project.project_file` est calculé depuis le nom courant du
projet (`root_path / f"{name}.acfproj"`). Un flux réel et atteignable
(`ProjectPropertiesDialog.update_project()` change `project.name`, puis
`MenuManager.show_project_properties()` appelle `save_project()` juste
après) renomme donc le projet, mais `ProjectSerializer.save()`
écrivait toujours au nouveau chemin sans jamais toucher l'ancien -
confirmé par reproduction directe : renommer "OriginalName" en
"RenamedName" et sauvegarder laissait les DEUX fichiers sur le disque,
l'ancien orphelin et périmé. Corrigé en donnant à `Project` un suivi
réel du dernier chemin sauvegardé/chargé (`_last_saved_path`, exclu du
`repr`/de l'égalité du dataclass) : `ProjectSerializer.save()` supprime
maintenant l'ancien fichier quand le chemin calculé a changé depuis la
dernière sauvegarde/chargement réelle - un vrai renommage, pas une
supposition (les deux chemins sont réels, l'un est le fichier que cet
objet a lui-même écrit en dernier). Vérifié : renommages successifs
(3 de suite), sauvegarde normale sans renommage (ne supprime rien), et
le cas `open_project()` réel puis renommage (pas seulement un projet
créé dans le même process) - les trois fonctionnent correctement.
`ProjectSerializer` n'avait aucune couverture de test avant ce
correctif - 9 tests ajoutés (`tests/test_project_serializer.py`,
couvrant aussi le round-trip save/load de base, déjà correct).

**Run complet de non-régression : 4602 passed, 0 failed** (664
warnings, 388s) - 4593 + 9 nouveaux tests. Aucune régression.

## Validation majeure : le calculateur AWCI fonctionne bout-en-bout sur de vraies données Météo-France (2026-09-07)

En poursuivant l'investigation RESTOR, injection directe de vraies
données ALADIN (Alger, 31/08/2026 00h, point de grille réel le plus
proche) dans le vrai `AWCICalculator().calculate()` : température
27.6°C, pression 1013 hPa, humidité spécifique 20 g/kg, vent 1.8 m/s,
CAPE 1328 J/kg - toutes des valeurs réelles lues du fichier FA, aucune
synthétique. Résultat : score AWCI 20.5 ("Low"), décomposition
physiquement cohérente (module thermodynamique dominant vu la
chaleur/humidité, module convectif reflétant le vrai CAPE). **C'est la
validation la plus significative de cette investigation** : le cœur
scientifique du projet fonctionne réellement sur des données
opérationnelles réelles, pas seulement sur le solveur interne
synthétique (`CoupledEarthSolver`).

En creusant, découverte qu'une session précédente (2026-09-04, même
demande utilisateur RESTOR) avait déjà construit un pipeline complet et
rigoureux pour exactement ça : `acf.awci.archive_field` -
`load_real_aladin_restor_run()` décode un fichier FA RESTOR réel en
profils atmosphériques réels par niveau de pression (7 niveaux +
Surface), avec cross-validation indépendante contre la chaîne Fortran
EDF historique du site (valeurs identiques au point près). Déjà 14
tests, dont la comparaison croisée avec la sortie ASCII legacy.

Amélioration réelle apportée : le docstring du module divulguait
honnêtement "no CAPE/CIN... decoded here". En explorant les 97 champs
réels du fichier, trouvé `SURFCAPE.POS.F00` - un vrai champ CAPE
(convention Météo-France "POS" = CAPE positive uniquement, jamais
négative par définition), valeurs réelles 0-2610 J/kg sur le domaine,
physiquement plausibles. Ajouté à l'entrée "Surface" de
`load_real_aladin_restor_run()` (CAPE est un diagnostic de colonne, pas
par niveau de pression, donc n'appartient pas aux 7 niveaux) et propagé
par `sample_archive_at_point()`. Vérifié que `AWCICalculator` répond
réellement au vrai CAPE (score du module convectif différent avec/sans
CAPE, pas juste présent-mais-ignoré dans le dict). CIN reste
honnêtement non disponible dans cette archive (aucun champ
correspondant trouvé). 4 nouveaux tests
(`tests/test_awci_archive_field.py`, incluant le round-trip complet
CAPE réel → `AWCICalculator`).

**Run complet de non-régression : 4606 passed, 0 failed** (664
warnings, 390s) - 4602 + 4 nouveaux tests. Aucune régression.

## Verrouillage du cycle diurne AWCI 48h en test de régression (2026-09-07)

Vérification manuelle transformée en test permanent : la fonctionnalité
"Real Archive / 48h Trend" du dashboard AWCI (`_RealArchiveTrendWorker`),
exécutée bout-en-bout sur les 17 vraies échéances RESTOR pour Alger (0h
à 48h par pas de 3h), traite tout en ~7s et produit un vrai cycle
diurne physiquement cohérent : température (et donc CAPE et score
AWCI) réellement plus élevés aux deux maxima diurnes réels (+12h, +36h,
~midi local) qu'aux échéances nocturnes environnantes. 1 nouveau test
(`tests/test_awci_archive_field.py`), vérifié contre une vraie relation
physique, pas juste "ne plante pas".

## Nouvelle fonctionnalité : AWCI en application autonome (2026-09-07)

Demande explicite de l'utilisateur : "je veux que tu crée un bouton sur
acf qui affiche awci dans un autre dashboard separer du acf" - précisé
ensuite comme "une vraie application séparée... pas juste une 2e
fenêtre Qt dans le même processus".

Le bouton "✈️ AWCI" existant (ouvre `AWCIDashboardWindow` comme une 2e
fenêtre dans le processus ESOC) ne suffisait pas à cette demande - créé
un vrai second point d'entrée indépendant :

- **`src/acf/awci_app.py`** (nouveau) : lanceur autonome, sa propre
  `QApplication`, sa propre `SingleInstanceGuard` avec un nom de
  serveur distinct de celui d'ESOC (`acf-awci-app-single-instance` vs
  `acf-esoc-single-instance` - jamais confondus), affiche
  `AWCIDashboardWindow` comme fenêtre unique.
- **`acf-awci`** : nouveau point d'entrée terminal (`pyproject.toml`
  `[project.scripts]`), installé et vérifié (`acf-awci --version`,
  `--help`).
- **Bouton "🚀 AWCI (App)"** ajouté dans la barre d'outils ESOC, à côté
  du bouton existant "✈️ AWCI" (conservé, pas remplacé - deux façons
  distinctes d'atteindre AWCI selon le besoin). Appelle
  `subprocess.Popen([sys.executable, "-m", "acf.awci_app"])` -
  fire-and-forget, processus réellement indépendant.
- **Vérifié réellement** (pas seulement testé en isolation) : deux vrais
  processus `acf-awci` lancés successivement en séquence - le premier
  reste actif, le second est détecté par la vraie garde mono-instance
  et se ferme proprement (`exit code 0`), logs propres, aucune erreur.
- 9 nouveaux tests (`tests/test_awci_app.py`,
  `tests/test_esoc_launch_awci_app_action.py`), couvrant le bouton, le
  dispatch, la gestion d'échec de lancement, et confirmant qu'aucune
  fenêtre n'est créée dans le processus ESOC (bien un processus séparé,
  pas juste une 2e fenêtre).

**Run complet de non-régression : 4616 passed, 0 failed** (704
warnings, 422s) - 4607 (après le test de cycle diurne) + 9 nouveaux
tests. Aucune régression.

## Modernisation visuelle du dashboard AWCI (2026-09-07)

Demande explicite : "je veux ... le rendre fonctionnel à 100% et rendre
le dashboard moderne à 2026". Audit honnête d'abord : grep systématique
de `awci_dashboard.py` (1900+ lignes) pour tout marqueur "pas
implémenté"/placeholder - un seul trouvé, et c'est une divulgation
honnête déjà correcte ("Real archive not available on this machine"),
pas un vrai manque. Le dashboard était donc déjà fonctionnellement
complet ; le vrai chantier restant est visuel.

`src/acf/gui/theme_tokens.py` (système de tokens déjà unifié par une
session antérieure, "améliorer le dashboard... moderne idéal pour
2026") étendu avec :
- Palette plus profonde/contrastée (surfaces assombries, radii agrandis
  pour un look carte plus doux).
- `accent_real` : nouveau token distinct pour marquer les vraies
  affordances de données (Real Physics/Real Archive) - pas décoratif,
  sert à guider l'œil vers ce qui est réel plutôt que démo/synthétique.
- `accent_gradient_css()` : vrai gradient QSS calculé (pas une chaîne
  fixe - vérifié que l'angle change effectivement la direction).
- `apply_elevation()` : vraie ombre portée (`QGraphicsDropShadowEffect`)
  - équivalent Qt le plus proche d'un `box-shadow` web.
- Scrollbars modernes stylées (fines, coins arrondis, hover accent) -
  remplacent les scrollbars système par défaut.

Appliqué concrètement dans `awci_dashboard.py` (pas juste ajouté sans
usage) : ombre portée sur les 7 cartes principales (carte globale,
coupe verticale, radar, stats bar, carte régionale, graphique de route,
résumé des risques) - vérifié par introspection réelle
(`isinstance(w.graphicsEffect(), QGraphicsDropShadowEffect)` sur les 7,
tous `True`). Boutons "🔬 Real Physics"/"📡 Real Archive" restylés avec
`accent_real` (bordure/texte teal, fond plein au survol) - vérifiés
visuellement via capture d'écran réelle, se démarquent nettement des
autres boutons de l'en-tête.

**Correctif du débordement d'en-tête (2026-09-07, suite immédiate)** :
le badge "RESEARCH STAGE" tronqué (capture d'écran réelle ci-dessus)
avait d'abord été mal diagnostiqué comme un problème de taille d'écran
(`fit_window_to_screen(self, 1500, 950)` vs un écran de 1366×768).
Re-vérification rigoureuse (`window.screen()` au lieu de
`app.primaryScreen()`, config double-écran sur cette machine) : le vrai
écran utilisé fait 1920×1080, largement suffisant - **ce n'était pas un
problème d'écran**. Cause réelle : `fit_window_to_screen(self, 1500, 950)`
était appelé AVANT la construction de `self.awci_dashboard`, donc la
largeur naturelle réelle de l'en-tête (~1533px, mesurée directement) ne
pouvait pas être connue à ce moment - 33px de trop pour tenir dans les
1500px. Corrigé en construisant le dashboard d'abord, puis en
dimensionnant la fenêtre depuis son vrai `sizeHint()` actuel
(auto-correcteur si l'en-tête change plus tard), toujours borné par
l'écran comme avant. Vérifié par capture d'écran réelle : badge et
valeurs du panneau latéral entièrement visibles. 1 nouveau test
(`tests/test_awci_window_sizing.py`), qui distingue explicitement le
cas "écran assez large" (fenêtre = largeur naturelle) du cas "écran
trop petit" (le clamp existant + `QScrollArea` prennent le relais,
comportement inchangé et toujours correct) - vérifié sur le vrai
écran ET sur l'écran virtuel 800×800 utilisé par la suite de tests.

20 nouveaux tests (`tests/test_theme_tokens.py` +6,
`tests/gui/test_awci_dashboard_reference_parity.py` et autres déjà
verts sans modification - 148 tests de la suite `awci_dashboard`/
`theme_tokens` confirmés verts après ce changement).

## Nouveaux boutons AWCI : Connexion HPC + Import de fichier modèle (2026-09-07)

Demande explicite : "ajoute un bouton pour la connexion à hpc et un
autre bouton pour faire entrer des fichiers de modèle" (sur AWCI, ACF
mis de côté).

- **"🔌 Connect HPC"** : réutilise le vrai connecteur déjà éprouvé côté
  ESOC (`acf.hpc_connector.HPCConnectionManager`, SSH Paramiko réel) -
  pas de réimplémentation. Bascule connexion/déconnexion.
- **"📂 Import Model File"** : réutilise le vrai pipeline d'ingestion
  corrigé plus tôt cette session (`acf.data.manager.DataManager` ->
  `EPyGrAMReader` pour FA/LFA/LFI, GRIB/NetCDF). Portée honnêtement
  limitée : charge et confirme le fichier réel (nom, nombre de
  champs) - ne mappe pas encore automatiquement les noms de champs
  d'un fichier arbitraire vers les clés attendues par
  `AWCICalculator` (c'est ce que `acf.awci.archive_field` fait
  spécifiquement pour RESTOR/ALADIN).

**Bug réel trouvé et corrigé, avec la permission explicite de
l'utilisateur pour tester en conditions réelles contre son vrai
cluster HPC de production** (`login2.fennec.meteo.dz`) : le premier
test réel a montré une vraie connexion SSH réussie (commandes
distantes en lecture seule uniquement - hostname/whoami/nproc/
vérifications de modules, rien de destructif) mais le bouton restait
bloqué sur "🔌 Connecting…" indéfiniment. Diagnostic reproductible :
`_HPCConnectWorker` n'était référencé que par une variable locale dans
`_toggle_hpc_connection()` - une vraie connexion HPC prend ~2-3s
d'E/S réseau réelle (contrairement aux autres workers rapides/CPU de
ce fichier), assez longtemps pour que le ramasse-miettes Python
détruise le worker (et son `signals`, sans parent C++) avant que le
thread d'arrière-plan ait pu émettre `finished` - une vraie race
condition de durée de vie, confirmée en enveloppant le slot réel (il
n'était jamais appelé, même après 20s d'attente post-succès réel).
Corrigé en gardant une référence forte sur `self._hpc_connect_worker`
le temps de l'appel asynchrone. **Re-vérifié en conditions réelles**
(connexion → mise à jour d'état correcte → déconnexion propre → état
réinitialisé) - fonctionne intégralement.

9 nouveaux tests (`tests/gui/test_awci_dashboard_hpc_and_import.py`),
aucun ne fait de vraie connexion réseau (tous mockent
`HPCConnectionManager.connect()`/`disconnect()` au niveau classe) -
dont un test qui verrouille spécifiquement le bug de race condition
GC (délai réel simulé de 0.3s dans le mock + `qtbot.waitUntil()`, la
même condition qui a exposé le bug en premier lieu).

## Sélecteur de route aéroport-à-aéroport + vérification de tous les boutons (2026-09-07)

Demande explicite : "ajoute un bouton pour changer la route entre les
aeroport en intrroduisant tout les aeroport existant fonctionnel et
rendre tout les boutons du dashboard fonctionnel".

- `_REGIONAL_ROUTE` était une constante de module figée (Alger→Tripoli),
  lue directement par 7 endroits réels (graphique de route, échantillonnage
  façon coupe verticale, comparaison FL280/FL320). Convertie en vrai
  attribut d'instance `self._regional_route` que `_on_apply_route()`
  peut changer - la valeur par défaut reste identique, donc aucun
  changement pour un opérateur qui ne touche pas au nouveau sélecteur.
- Nouvelle table `_AIRPORTS` : 28 aéroports réels, vrais codes ICAO,
  vraies coordonnées publiées (précision "référence publique", pas une
  base de données live versionnée - honnêtement disclosé comme tel).
- Deux `QComboBox` (départ/arrivée) + bouton "✈️ Apply Route" sous la
  carte régionale. Vérifié : la carte, le graphique de route et le
  score AWCI se recalculent réellement (testé avec Tokyo→Singapour :
  les distances du graphique changent réellement, pas une valeur
  figée). Une route hors de l'étendue de la carte régionale (ex.
  New York→Paris) recalcule quand même correctement tout le reste -
  seule la ligne sur LA CARTE régionale spécifique ne s'affiche pas
  (limite honnête d'étendue de carte, pas un bug). Départ = arrivée
  rejeté avec un message honnête, pas appliqué silencieusement.
- **Vérification "tous les boutons fonctionnels"** : smoke-test réel
  des 13 `QPushButton` du dashboard (clic réel sur chacun, dialogues
  bloquants mockés) - 13/13 sans exception. Combiné à l'audit
  systématique déjà fait plus tôt (un seul point honnêtement divulgué
  dans tout le fichier, aucun placeholder caché), confirme que le
  dashboard est fonctionnel à 100% au sens où aucun bouton ne mène à
  du code manquant ou fabriqué.

7 nouveaux tests (`tests/gui/test_awci_dashboard_route_selector.py`).

## Correctif de cohérence : point d'intérêt vs route (2026-09-07)

Trouvé par ma propre revue juste après avoir livré le sélecteur de
route, pas signalé par l'utilisateur. `self._point_of_interest` (ce
que le radar, la liste de composants, la tendance régionale, le
résumé des risques, le dialogue Real Archive et le profil vertical
analysent réellement - voir la convention de source unique déjà
documentée dans `_on_map_point_clicked`) restait figé après un
changement de route : choisir Tokyo→Singapour déplaçait bien la carte
et le graphique de route, mais tous les panneaux par point continuaient
d'analyser l'ancien point resté en Méditerranée. Corrigé en recentrant
`self._point_of_interest` sur le point médian réel de la nouvelle
route (moyenne simple des deux coordonnées, honnêtement disclosée
comme une approximation du vrai point médian géodésique, pas prétendue
exacte), en réutilisant le chemin de mise à jour déjà établi par
`_on_map_point_clicked` (re-tranche Real Physics si actif, sinon
`refresh()`) plutôt qu'un second chemin dupliqué. Vérifié : Tokyo→
Singapour recentre exactement sur le point médian calculé.

1 nouveau test (`tests/gui/test_awci_dashboard_route_selector.py`).

## Fenêtre AWCI en plein écran (2026-09-07)

Demande explicite : "gère moi la résolution pour que ça soit en plein
écran". La fenêtre `AWCIDashboardWindow` s'ouvre maintenant maximisée
(`showMaximized()`, contrôles de fenêtre conservés) sur les deux
points d'entrée réels : `acf-awci` (application autonome) et le bouton
"✈️ AWCI" d'ESOC. Précaution : ne maximise qu'au premier lancement -
une réouverture ne doit jamais écraser un redimensionnement manuel de
l'opérateur (`isMinimized()` vérifié avant `showNormal()` côté
standalone ; maximisation conditionnée au premier `show()` côté ESOC).
Vérifié par capture d'écran réelle (1920×1010, en-tête et panneaux
visibles sans débordement). 3 nouveaux tests
(`tests/test_awci_dashboard_fullscreen.py`).

## Boutons du footer AWCI rendus fonctionnels (2026-09-07)

Demande explicite : "la barre d'outils en bas research stage adaptative
to mission multi scale décision support synthétique view sont des
boutons je veux les rendre des boutons fonctionnelles". Les 5 cellules
du footer (`AWCIFooter`) étaient purement décoratives (`QLabel`, aucun
gestionnaire de clic) malgré leur apparence de boutons dans la maquette
de référence. Rendues réellement cliquables (`AWCIFooterCell`, curseur
main, survol visible) et câblées à des fonctionnalités déjà existantes
et testées du dashboard, correspondant honnêtement à leur description
(aucune action inventée) :
- **Synthetic View** → retour au mode démo/synthétique (`_revert_to_demo`)
- **Decision Support** → alertes réelles actives (`_open_alerts`)
- **Multi-Scale** → cycle réel Global → Regional → Coupe Verticale
  (réutilise le mécanisme `view_mode_group` déjà existant)
- **Adaptive to Mission** → profil vertical réel par niveau de vol
  (`_open_vertical_profile`)
- **Research Stage** → rapport d'exécution réel (qualité/diagnostics,
  `_open_execution_report`)

Vérifié : les 5 clics fonctionnent sans crash, le cycle Multi-Scale
change réellement l'étendue de la carte (pas juste l'état du bouton
radio). 9 nouveaux tests (`tests/gui/test_awci_footer_buttons.py`).

## Correctif de stabilité de résolution : plus de défilement forcé (2026-09-07)

Plainte utilisateur explicite : "la resolution du dashboard n'est pas
stable elle se varie lorsque je clique sur les boutons et note que je
veux pas scroller l'eccrans et je sens qu'il est dispatcher".

Cause réelle mesurée, pas supposée : `AWCIDashboard.sizeHint()` était
de **1844×1918px** - presque le double de la hauteur utile d'un vrai
écran 1920×1080 (~994-1008px, mesuré sur la machine réelle de
développement de ce projet, double écran). `QScrollArea.
setWidgetResizable(True)` était censé compresser le widget vers son
`minimumSizeHint()` plus petit, mais un test empirique direct (forcer
un `resize()` manuel vers la taille du viewport) montrait qu'il
revenait systématiquement, en quelques cycles d'événements, exactement
à `sizeHint()` - pas une supposition, un fait mesuré et reproduit.
Tracé à la vraie source : 4 vrais panneaux matplotlib
(`FigureCanvasQTAgg` - carte globale/régionale, coupe verticale,
radar, graphique de route) sans `figsize` explicite, donc matplotlib
utilisait sa valeur par défaut (6.4×4.8 pouces à 100 dpi = 640×480px)
par figure - c'est cette taille par défaut que le layout réaffirmait
sans cesse.

Corrigé à la source réelle, pas en luttant contre le comportement de
`QScrollArea` : `figsize=(6, 1.6)` explicite sur les 4 figures, footer
ramené à une seule ligne (descriptions déplacées en info-bulles),
hauteurs minimales des cartes réduites modestement. **Vérifié
concrètement** : sur un vrai écran 1920×1080 maximisé, la taille du
dashboard correspond maintenant EXACTEMENT à celle du viewport
(1852×1008), les deux barres de défilement ont un maximum de 0 (rien à
défiler). Capture d'écran réelle confirmant que tous les graphiques
restent lisibles à cette taille compacte.

Cette correction répond aussi indirectement à "je sens qu'il est
dispatcher" et à l'instabilité au clic : la majeure partie de l'effet
de "saut"/incohérence perçu venait très probablement du contenu qui
dépassait le viewport et se recalait en défilement à chaque
rafraîchissement déclenché par un clic - éliminé avec le défilement
lui-même.

1 nouveau test (`tests/test_awci_dashboard_fullscreen.py`), qui
vérifie `verticalScrollBar().maximum() == 0` sur un vrai écran assez
grand (se met honnêtement en attente/skip sur l'écran virtuel 800×800
utilisé par la suite de tests, qui ne peut rien prouver sur ce
scénario réel).

## Vérification visuelle réelle en conditions 1920x1080 + correctif de texte tronqué (2026-09-07)

Suite au correctif de stabilité ci-dessous, vérification en conditions
**réelles** (pas seulement via les métriques de test) : rendu du
dashboard hors-écran mais à une vraie taille 1920x1080 (plugin Qt
`vnc`, aucun serveur X ni bibliothèque `libxcb-cursor0` requis), export
d'une vraie capture d'écran PNG et lecture visuelle de l'image, comme
le ferait un utilisateur réel.

Résultat : `vscroll max = 0`, `hscroll max = 29` (conforme au seuil de
40px déjà accepté par le test de non-scroll) - mais l'inspection de
l'image elle-même a révélé que ce résidu de 29px, bien que
négligeable pour la largeur globale de la fenêtre, suffisait à
**tronquer visuellement** le texte de deux colonnes étroites situées
tout à droite : le badge de sévérité du panneau RISK SUMMARY
("Extreme" affiché "Extrem", "Low" affiché "L", "Moderate" affiché
"Moderat") et, dans une moindre mesure, la colonne de valeurs de
`_ComponentValueList` à côté du radar. Le layout Qt, contraint par la
largeur fixe de la fenêtre, préférait comprimer ces deux colonnes à
faible stretch factor plutôt que réduire un widget voisin plus large -
un vrai bug visuel, distinct du bug de scroll déjà corrigé, jamais
signalé explicitement par l'utilisateur mais trouvé en regardant
réellement le rendu (pas seulement les métriques automatisées).

Corrigé sans rouvrir l'instabilité de largeur déjà réglée : la largeur
de figure matplotlib de `AWCIRadar` et `AWCIRouteChart` réduite de
6.0in à 5.4in chacune (~60px libérés chacune, mesurés), et un
`setMinimumWidth()` réel ajouté sur `_ComponentRow.value_label` (36px)
et `_RiskRow.badge` (60px, mesuré via `QFontMetrics` pour couvrir la
chaîne réelle la plus large, "Very High"/"Moderate" ~55px à cette
police) - un simple redéploiement de l'espace déjà disponible dans la
même ligne, pas un changement de largeur totale (vscroll/hscroll
inchangés : toujours 0/29px après correctif). Revérifié par une
nouvelle capture d'écran réelle : les deux colonnes affichent
maintenant leur texte complet et lisible.

## Suite du correctif de stabilité : la largeur bougeait aussi au clic (2026-09-07)

Vérification approfondie du correctif précédent avec une vraie
séquence de clics (Multi-Scale, Real Physics, Decision Support,
changement de texte HPC, Apply Route) - a révélé que le problème
n'était pas entièrement réglé : la LARGEUR du dashboard grandissait
réellement de 1852→2081px après certaines actions, faisant apparaître
un défilement horizontal qui n'existait pas au départ. Cause exacte
trouvée : `play_evolution_button` ("▶ Play Evolution (4D)") était
caché (`setVisible(False)`) puis révélé seulement après un run "🔬 Real
Physics" - élargissant l'en-tête de ~177px à cet instant précis,
dépassant la largeur fixée une fois pour toutes à la construction de
la fenêtre. Corrigé en alignant ce bouton sur le patron déjà utilisé
par son voisin "🧊 3D View" (toujours visible, seul l'état activé/
désactivé change) - Real Physics ne modifie plus du tout la largeur de
l'en-tête. Libellés de deux boutons raccourcis en prime ("📡 Real
Archive (2026-08-31)" → "📡 Real Archive", date déplacée en info-bulle ;
"▶ Play Evolution (4D)" → "▶ 4D Evolution") pour réduire le résiduel de
défilement horizontal (179px → ~20-30px, négligeable).

**Vérifié par la même séquence de clics répétée** : largeur strictement
stable (1883→1883px) à travers Multi-Scale, Real Physics, Apply Route
et retour au mode démo - plus aucune variation liée aux clics.

1 nouveau test (`tests/test_awci_dashboard_fullscreen.py`), qui
verrouille précisément que `header.sizeHint().width()` reste identique
avant/après un vrai run Real Physics.

**Régression suite complète (4652 passed, 2 failed, 1 skipped, 431s)** :
les 2 échecs étaient réels mais attendus - `tests/gui/test_awci_dashboard_evolution.py`
vérifiait encore l'ancien libellé `"▶ Play Evolution (4D)"` du bouton,
raccourci ci-dessus en `"▶ 4D Evolution"`. Corrigé (2 assertions mises à
jour) - fichier revérifié isolément : 9 passed. Aucune autre régression.

## Baseline factuelle

Run complet `pytest -q` du 2026-09-06 (avant tout changement de code de ce
sweep) : **4574 passed, 0 failed**, 480s, 676 warnings (essentiellement des
`DeprecationWarning` Qt/PySide6 sur des constructeurs `QMouseEvent`, et un
avertissement de spécification Zarr — aucun échec, mais à nettoyer pendant
le sweep des modules `gui` et `storage`/`simulation_engine` concernés).

**Vérification finale de non-régression (2026-09-06, fin de sweep)** :
run complet relancé après les 42 commits du sweep Tier F+C+E —
**4574 passed, 0 failed**, identique en nombre à la baseline. Aucune
régression introduite par ce sweep. 2 des occurrences `QMouseEvent`
dépréciées ont été corrigées (`test_awci_map_panel_point_click.py`,
`test_map_canvas_zoom_pan.py`, commit `0f2e3d7`) et re-vérifiées
séparément avec `DeprecationWarning` promu en erreur (12 passed) — ce
run complet-ci a probablement démarré juste avant que cette correction
ne soit sauvegardée sur disque (le nombre total de warnings n'a pas
bougé), donc ne le confirme pas lui-même ; la vérification isolée
après coup fait foi. Le reste des ~674 warnings (Qt/PySide6 divers,
Zarr, Matplotlib/Cartopy internes à ces bibliothèques) reste non
traité — cosmétique, aucun échec, pas prioritaire.

**Écart découvert pendant le sweep Tier C (`gui`), même journée** :
`tests/test_gui_stack_scroll_no_permanent_growth.py` — 2 des 4 tests
échouent maintenant, y compris exécutés seuls (pas un problème
d'ordre) :
`test_esoc_window_can_still_be_explicitly_shrunk_after_visiting_a_large_tab`
et
`test_acf_workstation_window_can_still_be_explicitly_shrunk_after_visiting_complexity_explorer`.
Les deux échouent de la même façon : `window.resize(...)` est appelé
mais la fenêtre reste à 1010px de haut au lieu de la valeur demandée
(500 / <737). Aucun changement de code de ce sweep ne touche ce chemin
(seuls des docstrings ont été modifiés dans `view_manager.py`/
`map_projection.py` avant cette découverte). Hypothèse la plus
probable, non confirmée à l'époque : ces tests dépendent du
gestionnaire de fenêtres X11 réel (`DISPLAY=:0`, pas de serveur X
virtuel) pour honorer un `resize()` de façon synchrone après un seul
`qapp.processEvents()` — cette session a depuis lancé Claude Desktop
(plusieurs fenêtres/processus réels sur le même serveur X), ce qui
peut avoir changé le comportement/timing du WM par rapport au run de
baseline.

**Résolu** : run complet de fin de session (2026-09-06, après les 42
commits du sweep) — **4574 passed, 0 failed**, y compris ces 2 tests,
code de `test_gui_stack_scroll_no_permanent_growth.py` inchangé entre
les deux runs. Confirme l'hypothèse d'un artefact d'environnement
(charge/timing du serveur X partagé), pas une régression de code —
gardé ici comme trace plutôt que supprimé, au cas où ça réapparaisse.

## Synthèse

- Tier F : **11/11 audités — TIER F COMPLET** (model4d reclassé en
  Tier X le 2026-09-06)
- Tier C : **16/16 audités — TIER C COMPLET**
- Tier E : **31/31 audités — TIER E COMPLET**
- Total bloquant v1.0 (F+C+E) : **58/58 — TOUT LE PÉRIMÈTRE v1.0 EST AUDITÉ**
- Tier X : hors critère (voir ARCHITECTURE.md §3)

## Sweep Tier F + Tier C + Tier E : TERMINÉ (2026-09-06)

Les 58 modules bloquants v1.0 (Foundation + Core + Extended) sont tous
individuellement audités, testés et honnêtement documentés. Les deux
derniers items ouverts d'`ARCHITECTURE.md` §3 (`certification/` et
`src/acf/resources/`) sont également résolus.

Ce que "terminé" veut dire concrètement ici — et ne veut pas dire :
un module coché `[x]` a satisfait les 4 critères vérifiables
d'`ARCHITECTURE.md` §3 (commit d'audit, tests verts, pas de surclaim
de docstring connu, dépendances déclarées). Ça ne veut pas dire que le
projet est "fini" au sens produit — ça veut dire que l'écart entre ce
que le code prétend faire et ce qu'il fait réellement est maintenant
documenté partout où on l'a cherché, pas qu'il n'existe plus nulle
part. Prochaines étapes naturelles, non bloquantes :
- `docs/STATUS.md` doit rester tenu à jour à chaque nouveau changement
  de code (pas seulement relu une fois).
- Tier E est "souhaité", pas figé : tout nouveau module y ajouté doit
  suivre la même discipline dès son premier commit, pas être audité
  après coup.

## Mise à jour (2026-09-07) : couverture complète de model4d/physics/

Suite à la question directe de l'utilisateur "le projet est terminé ?"
(réponse honnête : non, un projet de cette taille n'a pas de ligne
d'arrivée en un tour de conversation) et son "attaque le reste" :
les 75 fichiers `model4d/physics/` non-`_engine.py` restés
individuellement non lus après le sweep du 2026-09-06 ont tous été
relus intégralement. Zéro nouvelle fabrication ou écart trouvé — voir
l'entrée `model4d` de la section Tier X ci-dessus et le docstring de
`src/acf/model4d/__init__.py` pour le détail. `model4d/physics/` (151
fichiers : 20 `*_engine.py` + orchestrateur + 130 autres, plus
`operators/`/`interpolation/`) a maintenant une couverture d'audit à
100%, une première pour ce package. Reste Tier X (zéro appelant réel
ailleurs dans `src/acf/`) — la couverture complète change ce qu'on
sait du code, pas si le produit livré l'utilise réellement.
