"""
Dataset Validator (Canonical Implementation)
"""


class ValidationReport(dict):
    """
    Subclass of dict that unpacks as (valid, errors) tuple for backwards compatibility.
    """

    def __iter__(self):
        yield self["valid"]
        yield self["errors"]


class DatasetValidator:

    REQUIRED_ATTRIBUTES = (
        "name",
        "variables",
        "dimensions",
        "metadata",
    )

    def validate(self, dataset):
        errors = []
        warnings = []

        if hasattr(dataset, "name") and not dataset.name:
            errors.append("Dataset has no name.")

        for attribute in self.REQUIRED_ATTRIBUTES:
            if not hasattr(dataset, attribute):
                errors.append(f"Missing attribute: {attribute}")

        if hasattr(dataset, "variables") and len(dataset.variables) == 0:
            errors.append("Dataset contains no variables.")

        if hasattr(dataset, "dimensions") and len(dataset.dimensions) == 0:
            warnings.append("Dataset has no dimensions.")

        if hasattr(dataset, "metadata") and isinstance(dataset.metadata, dict):
            coords = dataset.metadata.get("coordinates", [])
            if len(coords) == 0:
                warnings.append("No coordinate variables found.")

        if hasattr(dataset, "filetype") and dataset.filetype not in (
            "NetCDF",
            "GRIB",
            "GeoTIFF",
            "CSV",
            "JSON",
            "GRIB2",
            "BUFR",
        ):
            warnings.append(f"Unknown file type: {dataset.filetype}")

        valid = len(errors) == 0

        return ValidationReport({
            "valid": valid,
            "errors": errors,
            "warnings": warnings,
        })

    def is_valid(self, dataset):
        report = self.validate(dataset)
        return report["valid"]
