from acf.model4d.physics.global_weather_knowledge_graph_engine import (
    GlobalWeatherKnowledgeGraphEngine,
    WeatherKnowledgeNode,
)


def build_event():

    return WeatherKnowledgeNode(
        event_id="STORM_001",
        location="Algeria",
        phenomenon="Mediterranean Convective Storm",
        intensity=80,
        temperature=30,
        pressure=1005,
        humidity=85,
        impact_level=75,
    )



def test_signature():

    engine = GlobalWeatherKnowledgeGraphEngine()

    result = engine.create_weather_signature(
        build_event()
    )

    assert result["event_id"] == "STORM_001"



def test_risk():

    engine = GlobalWeatherKnowledgeGraphEngine()

    assert (
        engine.risk_classification(build_event())
        ==
        "SIGNIFICANT_EVENT"
    )



def test_similarity():

    engine = GlobalWeatherKnowledgeGraphEngine()

    first = build_event()
    second = build_event()

    assert (
        engine.atmospheric_similarity(
            first,
            second,
        )
        ==
        100.0
    )



def test_analogue():

    engine = GlobalWeatherKnowledgeGraphEngine()

    result = engine.find_weather_analogue(
        build_event(),
        [
            build_event()
        ],
    )

    assert result["analogue_event"] == "STORM_001"



def test_update():

    engine = GlobalWeatherKnowledgeGraphEngine()

    result = engine.knowledge_update(
        build_event()
    )

    assert result["risk"] == "SIGNIFICANT_EVENT"

