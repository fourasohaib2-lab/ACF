# API publique ACF

## Convention et inventaire

Le projet n'exprime pas encore une API publique par exports explicites ni par versionnage sémantique. Cette documentation utilise donc une convention pragmatique : toute classe, fonction de module ou méthode dont le nom ne commence pas par `_` est considérée publique par convention.

L'inventaire statique comprend **499 classes**, **41 fonctions de module publiques** et **2 097 méthodes publiques**, soit **2 138 callables publics par convention**. Ce nombre ne doit pas être interprété comme autant d'engagements de compatibilité.

## Interfaces à traiter comme publiques

| Domaine | API | Usage |
| --- | --- | --- |
| Démarrage | `acf.gui.app.run()` | Lance l'application de bureau. |
| API Python | `acf.api.api.ACFAPI` | Paramètres, analyse, prévision et alertes. |
| Noyau | `Application`, `Bootstrap`, `ConfigManager`, `ServiceManager`, `PluginManager` | Initialisation et services. |
| Données | `Dataset`, `DataEngine`, `DataManager`, `ReaderFactory`, `Workflow` | Données et lecture. |
| Paramètres | `Parameter`, `ParameterRegistry`, `ParameterHub`, `ParameterSearch` | Paramètres scientifiques. |
| Standards | `StandardsHub`, `StandardsManager`, `ECMWFManager` | Référentiels et conversions. |
| Workspace | `WorkspaceManager`, `Project`, `ProjectSerializer`, `RecentProjectsManager` | Projets ACF. |
| Cartes | `MapEngine`, `MapCanvas`, `LayerManager`, `ProjectionManager` | Cartographie ; plusieurs variantes existent. |
| IA | `DatasetAnalyzer`, `ForecastAssistant`, `WeatherAlertEngine`, `AIPlugin` | Analyse et décision. |

## Façade Python : `ACFAPI`

`acf.api.api.ACFAPI` est la façade la plus adaptée aux consommateurs externes.

| Méthode | Rôle |
| --- | --- |
| `parameters()` | Retourne les paramètres par défaut. |
| `parameter(parameter_id)` | Recherche un paramètre. |
| `analyze(dataset)` | Analyse un dataset. |
| `forecast_report(dataset)` | Produit un rapport de prévision. |
| `register_alert_rule(variable, threshold, level, message)` | Enregistre une règle d'alerte. |
| `alerts(dataset)` | Évalue les alertes sur un dataset. |

## Noyau et cycle de vie

| Classe | Méthodes publiques principales |
| --- | --- |
| `Application` | `start()` |
| `Bootstrap` | `initialize()` |
| `ConfigManager` | `load()`, `get()` |
| `ServiceManager` | `register()`, `get()`, `exists()`, `list_services()` |
| `PluginManager` | `discover()`, `list_plugins()` |

Ces classes constituent une API d'infrastructure, mais ne sont pas encore la composition root réellement appelée par `main.py`.

## Données et intégration

| API | Méthodes ou capacités publiques |
| --- | --- |
| `Dataset` | Représentation des données, variables et métadonnées. |
| `DataEngine` | `create_dataset()` |
| `DataManager` | Gestion de datasets et lecteurs. |
| `ReaderFactory` (`data`) | `discover()`, `register()`, `readers()`, `get_reader()` |
| `ReaderFactory` (`io`) | `get_reader()` avec registre injecté. |
| `AdapterFactory` | Sélection d'adaptateurs NetCDF, GRIB, BUFR, JSON, XML, HDF5, GeoTIFF et CSV. |
| `IntegrationEngine` | Intégration vers `Dataset`. |
| `DatasetValidator` | Validation de dataset ; deux variantes existent. |

Les méthodes des lecteurs et adaptateurs ne sont pas encore stabilisées autour d'une interface unique. Les consommateurs externes doivent préférer une façade future plutôt que dépendre d'un lecteur concret.

## Paramètres, catalogues et standards

| API | Méthodes publiques principales |
| --- | --- |
| `ParameterRegistry` | `register()`, `get()`, `exists()`, `all()`, `count()` |
| `ParameterHub` | `register()`, `add_alias()`, `by_code()`, `by_name()`, `by_alias()`, `exists()`, `count()` |
| `CatalogManager` (`catalog`) | Gestion de catalogues et de datasets. |
| `CatalogHub` (`catalogs`) | `load_cf()`, `load_ecmwf()`, `find()`, `search()`, `list_catalogs()` |
| `StandardsHub` | `register()`, `get()`, `exists()`, `names()`, `count()`, `load_ecmwf()`, `get_cf()` |

`catalog` et `catalogs`, comme `core.parameter` et `parameters.parameter`, sont des APIs concurrentes. Elles ne doivent pas être présentées comme simultanément canoniques.

## Science et modèle 4D

Les classes de `science` exposent des opérations spécialisées : température, humidité, thermodynamique, vorticité, indices de convection et diagnostics de temps sévère. `ScienceEngine` agrège thermodynamique, dynamique et diagnostics sévères.

`model4d` expose notamment :

- structures : `Grid4D`, `Field4D`, `Domain4D`, `TimeAxis`, `VerticalAxis` ;
- interpolation : `LinearInterpolation`, `BilinearInterpolation`, `CubicInterpolation`, `SplineInterpolation`, `TrilinearInterpolation`, `InterpolationEngine` ;
- opérateurs : `Gradient`, `Divergence`, `Curl`, `Laplacian`, `Advection`, `Diffusion`, `OperatorsEngine` ;
- moteurs physiques : classes des modules sous `model4d.physics`.

Les moteurs physiques doivent être considérés comme expérimentaux ou internes tant que leurs unités, entrées, sorties et niveau de stabilité ne sont pas documentés individuellement.

## IA et prévision

| API | Méthodes publiques |
| --- | --- |
| `DatasetAnalyzer` | `analyze()`, `variables()`, `summary()` |
| `ForecastAssistant` | `generate_report()` |
| `WeatherAlertEngine` | `register_rule()`, `analyze()` |
| `AIPlugin` | `analyze()` |
| `ai.plugins.PluginManager` | `register()`, `available()`, `get()`, `analyze()` |

Les moteurs IA sous `model4d.physics` ne sont pas enregistrés dans cette API. Une future API IA doit inclure le schéma des données, la version du modèle, l'incertitude, les métriques et le backend d'exécution.

## GUI, cartes et visualisation

Les classes GUI sont des APIs d'interface interne, non des contrats de bibliothèque. Les familles suivantes existent :

- `gui.main_window.MainWindow` et `gui.main_window.main_window.MainWindow` ;
- `gui.map.MapCanvas`, ses couches et renderers Qt ;
- `maps.MapEngine`, `maps.canvas.MapCanvas`, layers et renderers ;
- `visualization.VisualizationManager`, layers et renderers.

Avant de créer un nouvel écran, renderer ou layer, identifier le chemin réellement atteint par `acf.gui.app.run()` et utiliser l'API de cette pile. Une future façade cartographique unique devra remplacer ces interfaces concurrentes.

## Politique de stabilisation recommandée

1. Publier les exports explicites de chaque package dans ses `__init__.py`.
2. Versionner les interfaces de bibliothèque.
3. Marquer les APIs historiques comme dépréciées avant suppression.
4. Documenter signatures, unités, exceptions et exemples des APIs scientifiques.
5. Maintenir une seule façade publique pour données, catalogues, cartes et IA.
