from acf.parameters.parameter import Parameter
from acf.parameters.registry import ParameterRegistry
from acf.parameters.search import ParameterSearch


def test_search():

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

    assert search.exists("t2m")
    assert search.by_code("t2m").unit == "K"
    assert search.by_name("2 metre temperature").code == "t2m"
    assert "t2m" in search.all_codes()
