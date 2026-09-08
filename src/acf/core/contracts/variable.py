"""
VariableContract: the Prompt Maître's section 14 Scientific Variable Contract.
"""

from dataclasses import dataclass

from acf.normalization.variable_names import cf_canonical_unit
from acf.physics_guard.range_check import OPERATIONAL_RANGES


@dataclass
class VariableContract:
    """
    Full scientific metadata for one variable.

    name : str
        ACF's own working name for the variable, e.g. "temperature".
    standard_name : str
        Real CF standard_name, e.g. "air_temperature".
    unit : str
        Real CF canonical unit for standard_name.
    dimensions : tuple[str, ...]
        e.g. ("level", "lat", "lon") or ("lat", "lon").
    valid_range : tuple[float, float] | None
        In `unit`. None if ACF has no documented operational bound for
        this variable yet - see acf.physics_guard.range_check's own
        disclosure on what these bounds are (and are not).
    description, source_variables, derivation, references,
    uncertainty, quality_requirements : free-form documentation fields,
        matching the Prompt Maître's own field names exactly.
    """

    name: str
    standard_name: str
    unit: str
    dimensions: tuple[str, ...]
    valid_range: tuple[float, float] | None = None
    description: str = ""
    source_variables: tuple[str, ...] = ()
    derivation: str = ""
    references: tuple[str, ...] = ()
    uncertainty: str = ""
    quality_requirements: str = ""

    @classmethod
    def from_registry(
        cls, name: str, standard_name: str, dimensions: tuple[str, ...], **overrides: object
    ) -> "VariableContract":
        """
        Build a VariableContract from ACF's own real reference data -
        acf.normalization.variable_names.cf_canonical_unit() for the
        unit, acf.physics_guard.range_check.OPERATIONAL_RANGES for the
        valid_range if one is documented - instead of requiring the
        caller to look both up and risk a transcription mismatch.

        Any keyword in `overrides` replaces the corresponding
        registry-derived or default field (e.g. description=...).

        Raises
        ------
        ValueError
            If `standard_name` has no real CF unit registered (see
            cf_canonical_unit()'s own error) - never falls back to a
            guessed unit.
        """
        unit = cf_canonical_unit(standard_name)
        valid_range = OPERATIONAL_RANGES.get(standard_name)

        fields: dict[str, object] = {
            "name": name,
            "standard_name": standard_name,
            "unit": unit,
            "dimensions": dimensions,
            "valid_range": valid_range,
        }
        fields.update(overrides)
        return cls(**fields)  # type: ignore[arg-type]
