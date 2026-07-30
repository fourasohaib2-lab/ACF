"""
ACF Dataset Registry (Canonical Implementation)

Gestionnaire central des datasets scientifiques.
"""

from datetime import datetime


class DatasetRegistry:
    """
    Catalogue et registre central des datasets ACF.
    """

    def __init__(self):
        self._datasets_dict = {}
        self._datasets_list = []
        self.history = []

    @property
    def datasets(self):
        # Allow both dict and list usage if accessed directly
        return self._datasets_dict

    def register(self, dataset):
        dataset.modified = datetime.now().isoformat()
        dataset_id = getattr(dataset, "id", getattr(dataset, "name", str(id(dataset))))
        self._datasets_dict[dataset_id] = dataset
        if dataset not in self._datasets_list:
            self._datasets_list.append(dataset)
        self.history.append({
            "action": "register",
            "dataset": getattr(dataset, "name", str(dataset_id)),
            "time": datetime.now().isoformat(),
        })
        return dataset_id

    def add(self, dataset):
        return self.register(dataset)

    def remove(self, dataset_id):
        removed = False
        if dataset_id in self._datasets_dict:
            ds = self._datasets_dict.pop(dataset_id)
            if ds in self._datasets_list:
                self._datasets_list.remove(ds)
            removed = True
        else:
            self._datasets_list = [d for d in self._datasets_list if getattr(d, "id", None) != dataset_id]
        return removed

    def get(self, dataset_id):
        return self._datasets_dict.get(dataset_id)

    def all(self):
        if self._datasets_dict:
            return list(self._datasets_dict.values())
        return self._datasets_list

    def count(self):
        return len(self.all())

    def clear(self):
        self._datasets_dict.clear()
        self._datasets_list.clear()

    def search(self, keyword):
        keyword = keyword.lower()
        results = []
        for dataset in self.all():
            text = (getattr(dataset, "name", "") + " " + getattr(dataset, "filetype", "")).lower()
            if keyword in text:
                results.append(dataset)
        return results

    def by_format(self, filetype):
        return [d for d in self.all() if getattr(d, "filetype", None) == filetype]

    def status(self):
        return {
            "datasets": self.count(),
            "history": len(self.history),
            "names": [getattr(d, "name", "") for d in self.all()],
        }

    def summary(self):
        return {
            "datasets": self.count(),
            "formats": list(set(getattr(d, "filetype", "") for d in self.all() if hasattr(d, "filetype"))),
        }
