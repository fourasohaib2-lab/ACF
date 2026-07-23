"""
Dataset Validator
"""


class DatasetValidator:

    def validate(self, dataset):

        report = {
            "valid": True,
            "errors": [],
            "warnings": []
        }

        # Nom
        if not dataset.name:
            report["errors"].append("Dataset has no name.")

        # Variables
        if len(dataset.variables) == 0:
            report["errors"].append("Dataset contains no variables.")

        # Dimensions
        if len(dataset.dimensions) == 0:
            report["warnings"].append("Dataset has no dimensions.")

        # Coordonnées
        coords = dataset.metadata.get("coordinates", [])

        if len(coords) == 0:
            report["warnings"].append("No coordinate variables found.")

        # Type de fichier
        if dataset.filetype not in (
            "NetCDF",
            "GRIB",
            "GeoTIFF",
            "CSV",
            "JSON",
        ):
            report["warnings"].append(
                f"Unknown file type: {dataset.filetype}"
            )

        if report["errors"]:
            report["valid"] = False

        return report
