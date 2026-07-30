# Inventaire du projet ACF

## Périmètre analysé

L'inventaire couvre tous les fichiers Python du dépôt hors environnement virtuel et métadonnées Git, les configurations, la documentation disponible, les exemples, scripts et tests. Aucun fichier n'a été modifié lors de l'analyse.

## Chiffres clés

| Indicateur | Valeur |
| --- | ---: |
| Fichiers Python du projet | 918 |
| Modules de production sous `src/acf` | 563 |
| Lignes de production sous `src/acf` | 41 640 |
| Classes de production | 499 |
| Fonctions de module publiques | 41 |
| Méthodes publiques | 2 097 |
| Callables publics par convention | 2 138 |
| Tests Pytest collectés | 1 780 |

## Packaging et configuration

| Fichier | Rôle | Observation |
| --- | --- | --- |
| `pyproject.toml` | Packaging setuptools et Pytest | Python >= 3.12 ; version déclarée `0.1.0`. |
| `requirements.txt` | Dépendances de production | Déclarations sans bornes de version. |
| `requirements-dev.txt` | Outils de développement | Pytest, coverage, Black, Ruff, MyPy. |
| `config/config.yaml` | Configuration par défaut | Version `0.1.0`, GUI, logs et plugins. |
| `Makefile` | Commandes de développement | Test, format, lint, typecheck et clean. |

## Tests et qualité

La collection Pytest est configurée uniquement sur `tests/`. L'exécution observée a donné :

```text
1 777 passed, 3 failed, 6 warnings
```

Les trois échecs portent sur la calibration de confiance de prévisions et concernent des fichiers non suivis présents dans l'état local audité. Les avertissements concernent `datetime.utcnow()` et une incompatibilité binaire signalée par NumPy pendant un test NetCDF.

Ruff relève 76 diagnostics, principalement des imports inutilisés, redéfinitions et quelques défauts de structure. La syntaxe des 918 fichiers Python analysés est valide.

## Exemples, scripts et ressources

- `examples/` contient 14 démonstrateurs : IA, dashboard, animation, API, raster, contour, vent, time manager, standards et alertes.
- `scripts/` contient de nombreux scripts de sprint et de correction ; ils sont des artefacts de développement, non une interface de build structurée.
- `src/acf/resources/standards/` contient les ressources CF et ECMWF.
- `plugins/example_plugin/` est un squelette vide ; il ne démontre pas un contrat de plugin chargeable.

## Documentation

Les documents ODT/DOCX de cadrage présentent la vision d'une plateforme modulaire, scientifique, extensible et orientée plugins. La documentation Markdown opérationnelle à la racine est vide au moment de l'analyse. Les sous-dossiers `docs/architecture`, `docs/developer`, `docs/user`, `docs/adr` et `docs/specifications` étaient précédemment dépourvus de contenu fonctionnel.

## Utilisation réelle et composants incertains

Composants clairement atteints depuis l'entrée GUI : `gui.app`, `gui.main_window`, thèmes, splash, dashboard, workspace, data manager, visualisation et une pile de carte Qt.

Composants clairement atteints depuis l'API Python : registre de paramètres par défaut, `DatasetAnalyzer`, `ForecastAssistant` et `WeatherAlertEngine`.

Composants à usage incertain : `core.Application`/`Bootstrap` depuis le chemin GUI, la plupart de `model4d.physics`, `maps`, `io`, plusieurs readers historiques, `reports`, `analysis`, `alerts` et les plugins généraux. L'absence d'import direct ne prouve pas l'inutilisation, notamment pour les composants chargés dynamiquement ; elle justifie une validation par tests d'intégration et télémétrie de développement.

## État Git observé

L'état de travail contenait déjà une modification d'un module physique et des fichiers non suivis liés à la calibration et à l'explicabilité de prévisions, ainsi que leurs tests. Cette documentation décrit cet instantané sans attribuer ni modifier ces changements.

## Priorités d'architecture

1. Intégrer `Bootstrap` au démarrage GUI et faire de `core` la composition root.
2. Unifier `data`, `io` et `importers` derrière une interface de données canonique.
3. Unifier `catalog` et `catalogs`, puis `core.parameter` et `parameters`.
4. Choisir une seule pile de cartographie et de visualisation.
5. Supprimer ou migrer les doublons `MainWindow`, `MapEngine`, readers, layers et renderers.
6. Définir un modèle de données scientifique commun avec unités, coordonnées, standards et provenance.
7. Mettre en œuvre un vrai contrat de plugins et un cycle de vie chargeable.
8. Déclarer toutes les dépendances, aligner les versions et corriger les fichiers de documentation incohérents.
9. Stabiliser la suite de tests, corriger les échecs, déplacer les tests racine et intégrer les contrôles qualité en CI.
10. Définir une stratégie d'exécution CPU par défaut, avec backends optionnels GPU, Dask et MPI derrière des interfaces communes.
