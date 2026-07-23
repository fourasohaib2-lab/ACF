"""
ACF Scientific Data Manager
"""

from acf.data.factory import ReaderFactory
from acf.catalog.dataset_registry import DatasetRegistry
from acf.catalog.manager import CatalogManager



class DataManager:
    """
    Gestionnaire central des données scientifiques ACF.
    """



    def __init__(self):

        self.factory = ReaderFactory()

        self.registry = DatasetRegistry()

        self.catalog = CatalogManager()

        self.current_dataset = None



    ##################################################

    def available_readers(self):

        return [

            reader.__class__.__name__

            for reader in self.factory.readers()

        ]



    ##################################################

    def open(self, filename):


        reader = self.factory.get_reader(
            filename
        )


        if reader is None:

            raise ValueError(
                f"No reader available for '{filename}'."
            )


        dataset = reader.read(
            filename
        )


        self.current_dataset = dataset


        self.registry.register(
            dataset
        )


        return dataset



    ##################################################

    def close(self):

        self.current_dataset = None



    ##################################################

    def datasets(self):

        return self.registry.all()



    ##################################################

    def history(self):

        return self.registry.count()



    ##################################################

    def status(self):

        return {

            "readers":
                self.available_readers(),

            "current_dataset":
                (
                    self.current_dataset.name
                    if self.current_dataset
                    else None
                ),

            "registry":
                self.registry.summary(),

            "catalog":
                self.catalog.status(),

        }
