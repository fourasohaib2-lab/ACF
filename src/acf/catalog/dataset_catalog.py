"""
ACF Dataset Catalog

Management of loaded scientific datasets.
"""

from acf.catalog.dataset_entry import DatasetEntry


class DatasetCatalog:
    """
    Catalogue des datasets scientifiques ACF.
    """

    def __init__(self):

        self.datasets = {}

    ##################################################

    def add(self, entry: DatasetEntry):

        self.datasets[entry.dataset_id] = entry

    ##################################################

    def get(self, dataset_id):

        return self.datasets.get(dataset_id)

    ##################################################

    def exists(self, dataset_id):

        return dataset_id in self.datasets

    ##################################################

    def remove(self, dataset_id):

        self.datasets.pop(dataset_id, None)

    ##################################################

    def all(self):

        return list(self.datasets.values())

    ##################################################

    def search(self, text):

        text = text.lower()

        return [
            dataset
            for dataset in self.datasets.values()
            if (text in dataset.name.lower() or text in dataset.filetype.lower())
        ]

    ##################################################

    def count(self):

        return len(self.datasets)
