from acf.data.dataset import Dataset
from acf.data.engine.dataset_inspector import DatasetInspector


def test_dataset_inspector():

    dataset = Dataset(name="Demo")

    dataset.add_variable("temperature", [280, 281, 282])
    dataset.add_variable("pressure", [1000, 995])

    dataset.add_dimension("time", 2)
    dataset.add_dimension("latitude", 181)

    dataset.set_metadata("source", "ERA5")

    inspector = DatasetInspector(dataset)

    report = inspector.inspect()

    assert report["name"] == "Demo"
    assert report["variables"] == 2
    assert report["dimensions"] == 2
    assert report["metadata"] == 1
