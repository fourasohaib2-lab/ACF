from acf.search.scientific_search import ScientificSearch


def test_scientific_search():

    engine = ScientificSearch()

    engine.initialize()

    parameter = engine.find("air_temperature")

    assert parameter is not None

    results = engine.search("temperature")

    assert len(results) > 0
