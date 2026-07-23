"""
ACF Dataset Registry

Gestion centrale des datasets chargés.
"""

from datetime import datetime



class DatasetRegistry:
    """
    Registre global des datasets ACF.
    """


    def __init__(self):

        self.datasets = {}

        self.history = []



    ##################################################
    # ADD DATASET
    ##################################################

    def add(self, dataset):

        self.datasets[dataset.id] = dataset


        self.history.append(
            {
                "action": "add",
                "dataset": dataset.name,
                "time": datetime.now().isoformat(),
            }
        )


        return dataset.id



    ##################################################
    # REMOVE
    ##################################################

    def remove(self, dataset_id):

        if dataset_id in self.datasets:

            dataset = self.datasets.pop(
                dataset_id
            )


            self.history.append(
                {
                    "action": "remove",
                    "dataset": dataset.name,
                    "time": datetime.now().isoformat(),
                }
            )


            return True


        return False



    ##################################################
    # GET
    ##################################################

    def get(self, dataset_id):

        return self.datasets.get(
            dataset_id
        )



    ##################################################
    # ALL
    ##################################################

    def all(self):

        return list(
            self.datasets.values()
        )



    ##################################################
    # SEARCH
    ##################################################

    def search(self, text):

        text = text.lower()


        return [

            dataset

            for dataset in self.datasets.values()

            if text in dataset.name.lower()

        ]



    ##################################################
    # COUNT
    ##################################################

    def count(self):

        return len(
            self.datasets
        )



    ##################################################
    # CLEAR
    ##################################################

    def clear(self):

        self.datasets.clear()



    ##################################################
    # STATUS
    ##################################################

    def status(self):

        return {

            "datasets": self.count(),

            "history": len(
                self.history
            ),

            "names":
                [
                    d.name
                    for d in self.datasets.values()
                ]

        }

