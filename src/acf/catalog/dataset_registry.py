"""
ACF Dataset Registry

Gestionnaire central des datasets scientifiques.
"""


from datetime import datetime



class DatasetRegistry:
    """
    Catalogue des datasets chargés.
    """



    def __init__(self):

        self.datasets = []



    ##################################################

    def register(self, dataset):

        dataset.modified = (
            datetime.now()
            .isoformat()
        )

        self.datasets.append(
            dataset
        )



    ##################################################

    def remove(self, dataset_id):

        self.datasets = [
            d for d in self.datasets
            if d.id != dataset_id
        ]



    ##################################################

    def all(self):

        return self.datasets



    ##################################################

    def count(self):

        return len(
            self.datasets
        )



    ##################################################

    def search(self, keyword):

        keyword = keyword.lower()


        results = []


        for dataset in self.datasets:


            text = (
                dataset.name
                + " "
                + dataset.filetype
            ).lower()



            if keyword in text:

                results.append(
                    dataset
                )


        return results



    ##################################################

    def by_format(self, filetype):

        return [

            d for d in self.datasets

            if d.filetype == filetype

        ]



    ##################################################

    def summary(self):

        return {

            "datasets":
                len(self.datasets),

            "formats":
                list(
                    set(
                        d.filetype
                        for d in self.datasets
                    )
                )

        }
