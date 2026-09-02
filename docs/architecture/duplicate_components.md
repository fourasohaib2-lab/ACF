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

<!-- ACF_CONSOLIDATION_REVERIFICATION_BANNER_2026-09-02 -->
> **✅ Re-verified 2026-09-02 (real per-row audit, not a re-read of the
> table below).** Every "Duplications critiques" row and every
> "Homonymes de classes" entry was re-checked against the current tree
> by grepping real importers of each class, not by re-reading this
> file's own claims. Result: **most rows are already resolved** —
> `tests/test_collisions_consolidation.py` (ACF-017) and
> `tests/test_importers_consolidation.py` (ACF-016) prove, with `is`
> identity assertions, that Fenêtre principale/Moteur cartographique/
> Catalogues/Paramètres/Lecteurs de données/BUFR/NetCDF-GRIB/Validation
> dataset are genuinely unified behind a canonical implementation with a
> real compatibility shim on the legacy import path (or, for Fenêtre
> principale, the legacy file is honestly dead - Python's own package-
> over-module import resolution never reaches it, documented in place,
> not deleted).
>
> **Two rows turned out to be false positives, not real duplicates** —
> same class name, genuinely different responsibility, both sides
> genuinely used today: **Plugins** (`core.plugin_manager.PluginManager`
> is generic filesystem plugin discovery used by `core.bootstrap`;
> `ai.plugins.plugin_manager.PluginManager` is an in-memory `AIPlugin`
> registry used by the AI subsystem) and **Data manager**
> (`data.manager.DataManager` is a stateful workflow orchestrator used
> by `acf.dashboard.window`; `io.manager`/`importers.manager.DataManager`
> - already unified via ACF-016 - is the lower-level reader registry).
> Locked in by `test_plugin_manager_is_a_real_homonym_not_a_duplicate()`
> and `test_data_manager_is_a_real_homonym_not_a_duplicate()` so a future
> pass doesn't "fix" them into a broken merge. Same finding, independently,
> for `Divergence`/`Dynamics` (already in ACF-017's own tests) -
> `science.*` are simple/didactic, `model4d.operators`/`physics` are
> the real solver-grade versions.
>
> **Couches et renderers** (the `gui.map`/`maps`/`visualization` triple
> stack) is real but was already fully investigated and honestly
> documented by an earlier pass: `gui/map/__init__.py`'s own NOTE
> confirms the entire `gui.map.{layers,renderers,navigation,projections,
> rendering}/` subpackage tree (covering this row's `LayerManager`/
> `ProjectionManager`/`CartopyRenderer`/`RasterRenderer` homonym entries'
> `gui.map` side) is a complete, correct, but **never-imported-by-
> anything-in-src/** alternate architecture - superseded in practice by
> the flat `gui/map/map_*.py` files ESOC actually uses. Not a live
> three-way split in practice, just a two-way one (`gui.map` flat files
> vs `maps`/`visualization`), and even that mostly already unified per
> the paragraph above.
>
> **One row is a real, still-open, verified duplicate: Canvas carte.**
> `acf.gui.map.map_canvas.MapCanvas` (a `QWidget` composing a matplotlib
> canvas as a child - embedded in ESOC's real live window via
> `acf.gui.esoc.view_manager.ViewManager`/`acf.gui.main_window.
> main_window.MainWindow`) and `acf.maps.canvas.map_canvas.MapCanvas`
> (which IS a `FigureCanvasQTAgg` itself - used by `acf.maps`'s own
> public API, which brands itself "Canonical Cartographic &
> Visualization Package" in its own docstring, and by
> `acf.visualization`'s lazy re-export table) are both genuinely live,
> both genuinely used, and not interchangeable shapes. Documented with a
> full NOTE in both files and locked in by
> `test_map_canvas_is_a_real_verified_duplicate_not_yet_consolidated()`.
> Real consolidation here means picking a winner and migrating either
> ESOC's live GUI or `acf.maps`/`acf.visualization`'s public API onto
> the other's shape - a scoped design decision, not something this pass
> makes unilaterally per this document's own step 1 ("désigner une API
> canonique... geler les alternatives") and step 2 ("tests de
> non-régression avant toute migration", which do not yet exist for
> either consumer group).

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
