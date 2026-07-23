"""
Atmospheric Complexity Framework (ACF)

Dataset Core Object
===================

Internal representation of meteorological datasets.
"""


from pathlib import Path
from datetime import datetime
from uuid import uuid4



class Dataset:
    """
    Generic meteorological dataset.
    """


    def __init__(
        self,
        name: str = "",
        filepath: Path | None = None,
        filetype: str = "",
        source: str = "",
    ):


        # Identity

        self.id = str(
            uuid4()
        )


        self.name = name

        self.source = source



        # File information

        self.filepath = filepath

        self.filetype = filetype



        # Data containers

        self.variables = {}

        self.dimensions = {}



        # Metadata

        self.metadata = {}

        self.attributes = self.metadata



        # Quality control

        self.validated = False

        self.errors = []



        # History

        self.created = (
            datetime.now()
            .isoformat()
        )


        self.modified = self.created



    ##################################################
    # Variables
    ##################################################


    def add_variable(
        self,
        name: str,
        value=None
    ):

        self.variables[name] = value

        self.touch()



    def get_variable(
        self,
        name: str
    ):

        return self.variables.get(
            name
        )



    def has_variable(
        self,
        name: str
    ):

        return name in self.variables



    def remove_variable(
        self,
        name: str
    ):

        self.variables.pop(
            name,
            None
        )

        self.touch()



    ##################################################
    # Dimensions
    ##################################################


    def add_dimension(
        self,
        name: str,
        size: int
    ):

        self.dimensions[name] = size

        self.touch()



    def get_dimension(
        self,
        name: str
    ):

        return self.dimensions.get(
            name
        )



    ##################################################
    # Metadata
    ##################################################


    def set_metadata(
        self,
        name: str,
        value
    ):

        self.metadata[name] = value

        self.touch()



    def get_metadata(
        self,
        name: str
    ):

        return self.metadata.get(
            name
        )



    ##################################################
    # Validation
    ##################################################


    def validate(self):

        self.errors = []


        if not self.name:

            self.errors.append(
                "Dataset name missing"
            )


        if not self.variables:

            self.errors.append(
                "No variables found"
            )


        self.validated = (
            len(self.errors) == 0
        )


        return self.validated



    ##################################################
    # Utilities
    ##################################################


    def touch(self):

        self.modified = (
            datetime.now()
            .isoformat()
        )



    @property
    def variable_names(self):

        return list(
            self.variables.keys()
        )



    @property
    def dimension_names(self):

        return list(
            self.dimensions.keys()
        )



    def summary(self):

        return {

            "id": self.id,

            "name": self.name,

            "source": self.source,

            "filetype": self.filetype,

            "variables": self.variable_names,

            "dimensions": self.dimension_names,

            "validated": self.validated,

            "errors": self.errors,

        }



    def __len__(self):

        return len(
            self.variables
        )



    def __repr__(self):

        return (

            f"Dataset("
            f"name='{self.name}', "
            f"type='{self.filetype}', "
            f"variables={len(self.variables)})"

        )
