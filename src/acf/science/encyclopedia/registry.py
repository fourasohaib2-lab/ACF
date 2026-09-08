"""
Atmospheric Complexity Framework (ACF)

Encyclopedia Scientific Registry
"""

import importlib
import logging
from typing import Any

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.laws.base_law import AtmosphericLaw
from acf.science.registry import ScientificRegistry

logger = logging.getLogger("acf.science.encyclopedia")


class EncyclopediaRegistry:
    """
    Registre universel centralisé de l'Encyclopédie Scientifique Atmosphérique ACF.
    """

    _entries: dict[str, EncyclopediaEntry] = {}
    _initialized: bool = False
    _failed_modules: list[str] = []

    @classmethod
    def _ensure_initialized(cls):
        if cls._initialized:
            return
        cls._initialized = True
        modules = [
            "acf.science.encyclopedia.atmosphere",
            "acf.science.encyclopedia.thermodynamics",
            "acf.science.encyclopedia.clouds",
            "acf.science.encyclopedia.convection",
            "acf.science.encyclopedia.precipitation",
            "acf.science.encyclopedia.boundary_layer",
            "acf.science.encyclopedia.dynamics",
            "acf.science.encyclopedia.radiation",
            "acf.science.encyclopedia.aerosols_chemistry",
            "acf.science.encyclopedia.ocean",
            "acf.science.encyclopedia.cryosphere",
            "acf.science.encyclopedia.nwp",
            "acf.science.encyclopedia.assimilation",
            "acf.science.encyclopedia.satellite",
            "acf.science.encyclopedia.radar",
            "acf.science.encyclopedia.aviation",
            "acf.science.encyclopedia.mathematics",
            "acf.science.encyclopedia.turbulence",
            "acf.science.encyclopedia.cloud_microphysics.cloud_classification",
            "acf.science.encyclopedia.cloud_microphysics.nwp_microphysics",
            "acf.science.encyclopedia.cloud_physics.cloud_physics",
            "acf.science.encyclopedia.cloud_physics.wmo_cloud_taxonomy",
            "acf.science.encyclopedia.convection_extended",
            "acf.science.encyclopedia.lightning",
            "acf.science.encyclopedia.severe_weather",
            "acf.science.encyclopedia.severe_weather_library",
            "acf.science.encyclopedia.turbulence_extended",
            "acf.science.encyclopedia.ocean_atmosphere",
            "acf.science.encyclopedia.chemistry",
            "acf.science.encyclopedia.chemistry_extended",
            "acf.science.encyclopedia.satellite_extended",
            "acf.science.encyclopedia.satellites_registry",
            "acf.science.encyclopedia.remote_sensing_extended",
            "acf.science.encyclopedia.radar_extended",
            "acf.science.encyclopedia.radar_meteorology_library",
            "acf.science.encyclopedia.nwp_models.ifs",
            "acf.science.encyclopedia.nwp_models.arome",
            "acf.science.encyclopedia.nwp_models.wrf",
            "acf.science.encyclopedia.nwp_models.icon",
            "acf.science.encyclopedia.knowledge_sources.sources_indexer",
            "acf.science.physics_ai.models",
            "acf.science.encyclopedia.assimilation_extended",
            "acf.science.encyclopedia.data_assimilation_advanced",
            "acf.science.encyclopedia.mathematics_nwp",
            "acf.science.encyclopedia.mathematics_advanced",
            "acf.science.encyclopedia.numerical_methods_extended",
            "acf.science.encyclopedia.physical_laws.thermodynamics_laws",
            "acf.science.encyclopedia.aerodynamics.flight_mechanics",
            "acf.science.encyclopedia.aerodynamics.isa_atmosphere",
            "acf.science.encyclopedia.aviation_extended",
            "acf.science.encyclopedia.nwp_database.nwp_models_registry",
            "acf.science.encyclopedia.hydrology.surface_hydrology",
            "acf.science.encyclopedia.parameterizations.operational_schemes",
            "acf.science.encyclopedia.cryosphere_extended",
            "acf.science.encyclopedia.earth_system_coupling",
            "acf.science.observations.surface_obs",
            "acf.science.observations.aviation_obs",
            "acf.science.observations.upper_air_obs",
            "acf.science.observations.wmo_code_tables",
        ]
        # NOTE (correction): this loop used to swallow every import error
        # silently (`except Exception: pass`). Each module registers its
        # entries as a side effect of import, so a future broken import in
        # any single one of these ~60 modules (typo, syntax error, a
        # dependency removed elsewhere) would silently shrink the
        # encyclopedia with zero error and zero log line - exactly the kind
        # of silent, invisible incompleteness this project's own history
        # (see the register() key-collision fix above) has repeatedly found
        # and fixed elsewhere. count() >= 60 in the test suite would not
        # reliably catch this: the encyclopedia holds ~300 entries, so
        # losing one module's handful of entries would not cross that
        # floor. Failures are now logged loudly (module still skipped
        # rather than aborting the whole registry, since one broken module
        # should not prevent the other ~59 from registering) instead of
        # vanishing silently.
        failed_modules: list[str] = []
        for mod in modules:
            try:
                importlib.import_module(mod)
            except Exception:
                failed_modules.append(mod)
                logger.warning(
                    "EncyclopediaRegistry: failed to import '%s' - its entries were NOT "
                    "registered (encyclopedia is silently incomplete for this module).",
                    mod,
                    exc_info=True,
                )
        if failed_modules:
            cls._failed_modules = list(failed_modules)

    @classmethod
    def register(cls, entry: EncyclopediaEntry):
        """
        Enregistre une entrée encyclopédique et la synchronise avec ScientificRegistry.

        NOTE (correction): this used to silently overwrite `cls._entries[key]`
        with no collision check at all. Five real, previously-undetected key
        collisions across the encyclopedia (ideal_gas_law, boussinesq_approximation,
        supercell_thunderstorm, density_altitude_aviation, thompson_microphysics_scheme)
        meant whichever module happened to import last - a side effect of
        unrelated test collection order, not a deliberate contract - silently
        won, while the other entry became completely inaccessible (in one
        case, thompson_microphysics_scheme, silently discarding a working
        compute_func in favor of a descriptive-only one). This was
        demonstrated to cause real, non-deterministic test failures
        (`pytest -k ideal_gas` failed while a full unfiltered run passed by
        accidental import ordering). Now raises immediately and loudly at
        import time instead of silently overwriting, so any future
        accidental collision is caught the moment it's introduced rather
        than lurking until an unlucky import order surfaces it.
        """
        if entry.key in cls._entries and cls._entries[entry.key] is not entry:
            existing = cls._entries[entry.key]
            raise ValueError(
                f"EncyclopediaRegistry key collision: '{entry.key}' is already registered "
                f"(existing entry: {existing.name!r} in domain {existing.domain!r}; "
                f"new entry: {entry.name!r} in domain {entry.domain!r}). "
                "Give the new entry a distinct key instead of silently overwriting the existing one."
            )
        cls._entries[entry.key] = entry
        law = AtmosphericLaw(
            key=entry.key,
            name=entry.name,
            domain=entry.domain,
            equation=entry.equation,
            variables=entry.variables,
            units=entry.units,
            description=entry.description,
            references=entry.references,
            limitations=entry.limitations,
            compute_func=entry.compute_func,
        )
        ScientificRegistry.register(law)

    @classmethod
    def get(cls, key_or_name: str) -> EncyclopediaEntry | None:
        """
        Récupère une entrée par sa clé ou son nom.
        """
        cls._ensure_initialized()
        if key_or_name in cls._entries:
            return cls._entries[key_or_name]
        q = key_or_name.lower()
        for entry in cls._entries.values():
            if entry.name.lower() == q or entry.key.lower() == q:
                return entry
        return None

    @classmethod
    def search(cls, query: str) -> list[EncyclopediaEntry]:
        """
        Recherche dans l'encyclopédie par mot-clé.
        """
        cls._ensure_initialized()
        q = query.lower()
        results = []
        for entry in cls._entries.values():
            text = f"{entry.name} {entry.domain} {entry.subdomain} {entry.description} {entry.equation}".lower()
            if q in text:
                results.append(entry)
        return results

    @classmethod
    def list_domain(cls, domain: str) -> list[EncyclopediaEntry]:
        """
        Liste toutes les entrées d'un domaine donné.
        """
        cls._ensure_initialized()
        dom_lower = domain.lower()
        return [e for e in cls._entries.values() if dom_lower in e.domain.lower()]

    @classmethod
    def list_entries(cls) -> list[EncyclopediaEntry]:
        """
        Liste toutes les entrées enregistrées dans l'encyclopédie.
        """
        cls._ensure_initialized()
        return list(cls._entries.values())

    @classmethod
    def get_all_entries(cls) -> list[EncyclopediaEntry]:
        """
        Alias pour list_entries().
        """
        return cls.list_entries()

    @classmethod
    def domains(cls) -> list[str]:
        """
        Liste la totalité des domaines scientifiques répertoriés.
        """
        cls._ensure_initialized()
        return sorted({e.domain for e in cls._entries.values()})

    @classmethod
    def calculate(cls, key_or_name: str, **kwargs) -> Any:
        """
        Calcule la valeur numérique associée à une entrée encyclopédique.
        """
        entry = cls.get(key_or_name)
        if entry is None:
            raise KeyError(f"Entrée encyclopédique inconnue: '{key_or_name}'")
        return entry.calculate(**kwargs)

    @classmethod
    def count(cls) -> int:
        """
        Retourne le nombre total d'entrées répertoriées.
        """
        cls._ensure_initialized()
        return len(cls._entries)

    @classmethod
    def failed_modules(cls) -> list[str]:
        """
        Retourne la liste des modules d'encyclopédie dont l'import a échoué
        lors de l'initialisation (voir la note dans _ensure_initialized()).
        Une liste non vide signifie que l'encyclopédie est incomplète.
        """
        cls._ensure_initialized()
        return list(cls._failed_modules)
