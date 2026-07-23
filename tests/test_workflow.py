from pathlib import Path

from acf.data.dataset import Dataset
from acf.data.workflow import Workflow


def test_workflow():

    workflow = Workflow("Demo")

    ds = Dataset(
        name="ERA5",
        filepath=Path("/tmp/test.nc"),
        filetype="NetCDF",
    )

    def validate(dataset):

        dataset.set_metadata(
            "validated",
            True,
        )

        return dataset

    def analyse(dataset):

        dataset.set_metadata(
            "analysis",
            "done",
        )

        return dataset

    workflow.add_step(
        "Validation",
        validate,
    )

    workflow.add_step(
        "Analysis",
        analyse,
    )

    result = workflow.run(ds)

    assert result.metadata["validated"] is True

    assert result.metadata["analysis"] == "done"

    assert len(workflow) == 2
