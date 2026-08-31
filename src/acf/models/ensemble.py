"""
Ensemble Forecast Manager
"""


class EnsembleForecast:
    def __init__(self, name):

        self.name = name
        self.members = []

    def add_member(self, member):

        self.members.append(member)

    def member(self, index):

        return self.members[index]

    def count(self):

        return len(self.members)

    def mean(self):

        if not self.members:
            return None

        return sum(self.members) / len(self.members)

    def minimum(self):

        if not self.members:
            return None

        return min(self.members)

    def maximum(self):

        if not self.members:
            return None

        return max(self.members)
