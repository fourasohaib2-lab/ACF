<!-- ACF_OUTDATED_SNAPSHOT_BANNER_2026-09-02 -->
> **📅 Outdated snapshot.** This is a real, dated analysis of the repository
> as it stood when written — not a false completion claim — but the specific
> numbers below (module/file/dependency counts) are now superseded: this
> session alone took the source tree from ~563 to 1353+ production modules,
> removed several of the dependencies listed below as genuinely unused
> (`pandas`, `shapely`, `rasterio`, `h5py`), and resolved some of the
> duplications this file documents. See
> [`../../ROADMAP.md`](../../ROADMAP.md) and
> [`../ACF_PHYSICS_GUARD_AUDIT_CHANGELOG.md`](../ACF_PHYSICS_GUARD_AUDIT_CHANGELOG.md)
> for the current, reproducible state. Re-running this analysis fresh would
> be the correct way to refresh it, not editing the numbers below by hand.
>
> _Banner added 2026-09-02 during a hygiene cleanup pass — original content
> preserved unchanged below._

---

# Composants dupliqués et incohérences

## Résumé

ACF contient plusieurs implémentations de responsabilités identiques ou très proches. Ces duplications sont le principal risque architectural : elles divisent les usages, augmentent les coûts de maintenance et empêchent de définir une API stable.

## Duplications critiques

| Responsabilité | Implémentations | Risque | Direction recommandée |
| --- | --- | --- | --- |
| Fenêtre principale | `gui/main_window.py`, `gui/main_window/main_window.py` | Deux compositions GUI différentes. | Conserver la variante effectivement lancée, migrer l'autre. |
| Moteur cartographique | `maps/engine.py`, `maps/map_engine.py` | Même nom, API différente. | Choisir une seule API `MapEngine`. |
| Canvas carte | `gui/map/map_canvas.py`, `maps/canvas/map_canvas.py` | Backends et intégrations distincts. | Séparer une interface commune du backend Qt/Matplotlib. |
| Couches et renderers | `gui.map`, `maps`, `visualization` | Trois piles de rendu. | Définir un modèle `Layer`/`Renderer` unique. |
| Lecteurs de données | `data`, `data.readers`, `io`, `importers` | Sélection et contrats divergents. | Une interface Reader/Importer canonique. |
| BUFR | `bufr_reader_basic.py`, `bufr_reader.py`, `bufr_reader_v1.py` | Versions concurrentes sans statut. | Garder une implémentation versionnée. |
| NetCDF/GRIB | Lecteurs à la racine de `data` et sous `data.readers` | Doubles chemins d'accès. | Converger vers `data.readers`. |
| Catalogues | `catalog`, `catalogs` | Modèles et hubs distincts. | Choisir un domaine catalogue unique. |
| Paramètres | `core.parameter*`, `parameters.*` | Deux modèles de paramètres et registres. | Faire de `parameters` la source canonique. |
| Plugins | `core.plugin_manager`, `ai.plugins.plugin_manager` | Cycle de vie et API distincts. | Un gestionnaire général avec points d'extension IA. |
| Data manager | `data.manager.DataManager`, `io.manager.DataManager` | Deux abstractions de gestion de lecture. | Unifier autour du workflow de données. |
| Validation dataset | `data.dataset_validator`, `data.engine.dataset_validator` | Règles de validation ambiguës. | Une validation centrale avec règles extensibles. |

## Homonymes de classes significatifs

- `MainWindow` : deux classes.
- `MapEngine` : deux classes.
- `MapCanvas` : deux classes.
- `LayerManager` : trois classes.
- `CartopyRenderer` : trois classes.
- `RasterRenderer` : deux classes.
- `RasterLayer`, `VectorLayer`, `BaseLayer` : deux classes chacun.
- `ReaderFactory` : deux classes.
- `BaseReader` : deux classes.
- `CatalogManager` : deux classes.
- `DatasetRegistry` : deux classes.
- `DatasetValidator` : deux classes.
- `Parameter`, `ParameterRegistry` : deux classes.
- `PluginManager` : deux classes.
- `ProjectionManager` : deux classes.
- `BufrReader` : trois classes.

Les homonymes physiques (`RadiationState`, `CloudMicrophysicsState`, `AtmosphericWaveState`, etc.) méritent aussi une revue : certains sont justifiés par des modèles distincts, mais leur nom identique rend les imports et la documentation ambigus.

## Modules incomplets ou probablement historiques

Les fichiers suivants sont vides ou squelettiques et doivent être soit implémentés, soit retirés du périmètre public :

- `README.md`, `ROADMAP.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `LICENSE` à la racine ;
- plusieurs packages et `__init__.py` ;
- `analysis`, `alerts`, `reports`, `plugins` ;
- plusieurs writers, validateurs, standards, panneaux GUI et implémentations de modèles ;
- tests racine exclus par `testpaths = ["tests"]`.

`docs/ACF_Vision_1.0.md` contient une archive DOCX malgré son extension Markdown. `acf_structure.txt` est un instantané d'arborescence qui ne reflète plus le dépôt.

## Incohérences techniques

- `pyproject.toml` annonce la version `0.1.0`; le changelog annonce `0.2.0-alpha`.
- `ConfigManager` dépend de PyYAML et la journalisation de Loguru, sans déclaration de ces deux dépendances.
- `datetime.utcnow()` est utilisé malgré sa dépréciation.
- Ruff a détecté 76 problèmes : imports inutilisés, redéfinitions, imports tardifs et exception nue.
- `parameters/aliases.py` contient un auto-import qui forme le seul cycle d'import statique détecté.

## Plan de consolidation

1. Désigner une API canonique par responsabilité et geler les alternatives.
2. Ajouter des tests de non-régression avant toute migration.
3. Introduire des adaptateurs temporaires et des avertissements de dépréciation.
4. Migrer progressivement les consommateurs internes.
5. Supprimer les doublons seulement après une version de transition documentée.
6. Mettre à jour les exports, exemples et documentation en même temps.
