from acf.parameters.aliases import ParameterAliases
from acf.parameters.parameter import Parameter
from acf.parameters.registry import ParameterRegistry
from acf.parameters.search import ParameterSearch


def test_aliases():

    aliases = ParameterAliases()

    aliases.add("T2", "t2m")
    aliases.add("temperature_2m", "t2m")

    assert aliases.exists("T2")
    assert aliases.resolve("T2") == "t2m"
    assert aliases.count() == 2


def test_search_alias():

    registry = ParameterRegistry()

    registry.register(
        Parameter(
            code="t2m",
            name="2 metre temperature",
            unit="K",
            standard_name="air_temperature",
            category="Temperature",
        )
    )

    search = ParameterSearch(registry)

    search.aliases.add("T2", "t2m")

    assert search.by_alias("T2").code == "t2m"
