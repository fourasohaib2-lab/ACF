from acf.parameters.hub import ParameterHub
from acf.parameters.parameter import Parameter


def test_parameter_hub():

    hub = ParameterHub()

    hub.register(
        Parameter(
            code="t2m",
            name="2 metre temperature",
            unit="K",
            standard_name="air_temperature",
            category="Temperature",
        )
    )

    hub.add_alias("T2", "t2m")

    assert hub.exists("t2m")
    assert hub.by_code("t2m").unit == "K"
    assert hub.by_name("2 metre temperature").code == "t2m"
    assert hub.by_alias("T2").code == "t2m"
    assert hub.count() == 1

    # CORRECTED: ParameterHub used to keep a second, separate
    # ParameterAliases store (self.aliases) that add_alias() wrote to
    # but by_alias() never read (only self.search.aliases was
    # consulted) - dead state that could silently diverge from the
    # real one. hub.aliases is now a read-only view of the single
    # source of truth.
    assert hub.aliases.resolve("T2") == "t2m"
    assert hub.aliases is hub.search.aliases
