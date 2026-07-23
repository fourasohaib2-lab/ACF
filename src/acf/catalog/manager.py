"""
ACF Catalog Manager

Central access point for all catalogs.
"""


from acf.catalog.default_catalog import create_catalog
from acf.catalog.dataset_catalog import DatasetCatalog



class CatalogManager:
    """
    Gestionnaire global des catalogues ACF.
    """



    def __init__(self):

        # Catalogue scientifique
        self.scientific = create_catalog()


        # Catalogue des datasets
        self.datasets = DatasetCatalog()



    ##################################################

    def add_dataset(self, entry):

        self.datasets.add(
            entry
        )



    ##################################################

    def dataset_count(self):

        return self.datasets.count()



    ##################################################

    def parameters(self):

        return self.scientific.all()



    ##################################################

    def datasets_list(self):

        return self.datasets.all()



    ##################################################

    def status(self):

        return {

            "scientific_parameters":
                len(
                    self.scientific.all()
                ),


            "datasets":
                self.datasets.count(),

        }

