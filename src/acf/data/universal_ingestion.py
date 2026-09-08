"""
Atmospheric Complexity Framework (ACF)

Universal Earth Observation Data Ingestion Engine
"""

from pathlib import Path
from typing import Any

from acf.data.dataset import Dataset
from acf.data.detector import FormatDetector
from acf.data.readers.epygram_reader import EPyGrAMReader
from acf.science.encyclopedia.knowledge_graph.graph_engine import KnowledgeGraphEngine
from acf.science.encyclopedia.knowledge_graph.nodes import KnowledgeNode
from acf.science.parameters.engine import ParameterEngine


class UniversalDataIngestionEngine:
    """
    Moteur universel d'ingestion de données d'observation de la Terre et de prévision numérique.
    """

    def __init__(self):
        self.param_engine = ParameterEngine()
        self.graph = KnowledgeGraphEngine()

    def ingest(self, filepath: str | Path, dataset_name: str | None = None) -> Dataset:
        """
        Ingère automatiquement un fichier de n'importe quel format supporté,
        extrait ses métadonnées, associe les paramètres aux registres scientifiques
        et connecte l'ensemble au Graphe de Connaissances ACF.
        """
        path = Path(filepath)
        filetype = FormatDetector.detect(path)

        name = dataset_name or path.stem
        dataset = Dataset(name=name, filepath=path, filetype=filetype, source="UniversalIngestion")

        # Ingestion spécifique via EPyGrAM pour FA / LFA / LFI
        if filetype in ["FA", "LFA", "LFI"]:
            reader = EPyGrAMReader()
            with reader.open(path) as r:
                geom = r.geometry()
                meta = r.metadata()
                fields = r.list_fields()
                proj = r.projection()
                dom = r.domain()
                tval = r.time_validity()
                vlevels = r.vertical_levels()

                dataset.set_metadata("epygram", meta)
                dataset.set_metadata("geometry", geom)
                dataset.set_metadata("fields", fields)
                dataset.set_metadata("projection", proj)
                dataset.set_metadata("domain", dom)
                dataset.set_metadata("time_validity", tval)
                dataset.set_metadata("vertical_levels", vlevels)
                dataset.set_attribute("projection", proj)
                dataset.set_attribute("domain_grid", geom.get("grid_type", "Lambert93"))

        # 1. Extraction automatique des coordonnées & grille
        spatial_meta = self._extract_spatial_metadata(path, filetype)
        time_meta = self._extract_temporal_metadata(path)
        provenance_meta = self._extract_provenance_metadata(path, filetype)

        dataset.set_metadata("spatial", spatial_meta)
        dataset.set_metadata("temporal", time_meta)
        dataset.set_metadata("provenance", provenance_meta)
        # NOTE (correction): the ".get(key, EPSG:4326 / {} / 181 / 360 / 1)"
        # fallbacks here used to mask _extract_spatial_metadata()/
        # _extract_temporal_metadata()'s own fabrication with a second
        # layer of fabricated defaults. Both helpers are now honest
        # (they return None rather than omitting the key), so these
        # plain lookups correctly propagate that "not extracted" state
        # instead of quietly substituting another invented value.
        dataset.set_metadata("crs", spatial_meta.get("crs"))
        dataset.set_metadata("bounding_box", spatial_meta.get("bounding_box"))

        # Dimensions canoniques
        dataset.add_dimension("lat", spatial_meta.get("n_lat"))
        dataset.add_dimension("lon", spatial_meta.get("n_lon"))
        dataset.add_dimension("time", time_meta.get("n_times"))

        # 2. Ingestion des variables & cartographie des paramètres physiques
        variables_dict = self._detect_and_map_variables(path, filetype)
        param_mappings = {}

        for var_name, var_info in variables_dict.items():
            dataset.add_variable(var_name, value=var_info)
            # Alignment with PhysicalParameter Database
            param_obj = self.param_engine.get(var_name)
            if param_obj:
                param_mappings[var_name] = {
                    "canonical_key": param_obj.key,
                    "name": param_obj.name,
                    "unit": param_obj.unit,
                    "cf_standard_name": param_obj.cf_standard_name,
                    "grib2_code": param_obj.grib2_code,
                    "bufr_code": param_obj.bufr_code,
                    "netcdf_name": param_obj.netcdf_name,
                }
            else:
                param_mappings[var_name] = {
                    "canonical_key": var_name,
                    "name": var_info.get("long_name", var_name),
                    "unit": var_info.get("unit", "dimensionless"),
                    "cf_standard_name": var_info.get("cf_standard_name", var_name),
                    "grib2_code": var_info.get("grib2_code", "0,0,0"),
                    "bufr_code": var_info.get("bufr_code", "0 00 000"),
                    "netcdf_name": var_name,
                }

        dataset.set_metadata("parameter_mappings", param_mappings)

        # 3. Contrôle Qualité Automatique (QC)
        self._run_quality_control(dataset)

        # 4. Connexion automatique au Graphe de Connaissances ACF
        self._connect_to_knowledge_graph(dataset)

        return dataset

    def _extract_spatial_metadata(self, path: Path, filetype: str) -> dict[str, Any]:
        """
        NOTE (correction): this used to unconditionally claim a fixed
        global 1deg regular lat-lon grid ("EPSG:4326", 181x360) for
        EVERY ingested file regardless of filetype or content - a
        1.3km AROME domain and a global IFS grid would get byte-
        identical "spatial metadata". No real GRIB2/NetCDF grid reader
        is wired up here (unlike the FA/LFA/LFI path above, which
        genuinely uses EPyGrAMReader, fixed earlier this session). Not
        fabricated.
        """
        return {
            "crs": None,
            "bounding_box": None,
            "n_lat": None,
            "n_lon": None,
            "resolution_deg": None,
            "grid_type": None,
            "status": "NOT_EXTRACTED_NO_GRID_READER_WIRED_FOR_THIS_FORMAT",
        }

    def _extract_temporal_metadata(self, path: Path) -> dict[str, Any]:
        """
        NOTE (correction): this used to unconditionally claim a fixed
        "2026-07-30" reference/valid time and "12h lead time" for
        EVERY ingested file regardless of its actual content. Not
        fabricated.
        """
        return {
            "reference_time": None,
            "valid_time": None,
            "lead_time_hours": None,
            "n_times": None,
            "status": "NOT_EXTRACTED_NO_TIME_READER_WIRED_FOR_THIS_FORMAT",
        }

    def _extract_provenance_metadata(self, path: Path, filetype: str) -> dict[str, Any]:
        """
        NOTE (correction): source_file/format are genuinely derived
        from the real arguments, but institution/model_name/run_cycle
        used to be fixed guesses ("Météo-France / WMO Operational
        Center", "ARPEGE / AROME / ALADIN / IFS", "00Z") claimed
        regardless of the file's actual content - no real header/
        provenance reader is wired up for this format. Not fabricated.
        """
        return {
            "institution": None,
            "model_name": None,
            "run_cycle": None,
            "source_file": path.name,
            "format": filetype,
            "status": "NOT_EXTRACTED_NO_PROVENANCE_READER_WIRED_FOR_THIS_FORMAT",
        }

    def _detect_and_map_variables(self, path: Path, filetype: str) -> dict[str, dict[str, Any]]:
        """
        NOTE (correction): this used to unconditionally claim the same
        fixed 6-variable list (temperature/pressure/humidity/CAPE/
        wind_u/wind_v) was present in EVERY ingested file regardless of
        filetype or actual content - a radar reflectivity file or a
        soil-moisture dataset would get the exact same "detected"
        variable list as an AROME forecast. No real GRIB2/NetCDF/BUFR
        variable-table reader is wired up here (eccodes and netCDF4
        are installed in this environment - see
        release.dependency_validator, fixed earlier this session - but
        no code here actually calls them). Not fabricated.
        """
        return {}

    def _run_quality_control(self, dataset: Dataset):
        dataset.errors = []
        if not dataset.variables:
            dataset.errors.append("No variables ingested")

        if dataset.has_variable("temperature"):
            t_info = dataset.get_variable("temperature")
            if not isinstance(t_info, dict):
                dataset.errors.append("Invalid temperature format")

        dataset.validated = len(dataset.errors) == 0

    def _connect_to_knowledge_graph(self, dataset: Dataset):
        ds_key = f"dataset_{dataset.name.lower()}"
        ds_node = KnowledgeNode(
            key=ds_key,
            name=f"Dataset {dataset.name}",
            domain="Ingestion Données Earth System",
            description=f"Jeu de données canonique ACF au format {dataset.filetype}",
            equation=f"Dataset({dataset.filetype})",
            variables={"Format": dataset.filetype, "Variables": ", ".join(dataset.variable_names)},
            units={},
            references=[dataset.source],
        )
        self.graph.add_node(ds_node)

        for var_name in dataset.variable_names:
            param = self.param_engine.get(var_name)
            if param:
                self.graph.add_edge(
                    ds_key, param.key, relation="contains_parameter", cause="Automatic variable mapping"
                )
