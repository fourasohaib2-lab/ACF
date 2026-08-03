"""
Time Manager
"""



class TimeManager:

    def __init__(self):

        self.times = []

        self.index = 0

    ##################################################

    def load(self, times):

        self.times = list(times)

        self.index = 0

    ##################################################

    def current(self):

        if not self.times:
            return None

        return self.times[self.index]

    ##################################################

    def next(self):

        if self.index < len(self.times) - 1:

            self.index += 1

        return self.current()

    ##################################################

    def previous(self):

        if self.index > 0:

            self.index -= 1

        return self.current()

    ##################################################

    def first(self):

        self.index = 0

        return self.current()

    ##################################################

    def last(self):

        if self.times:

            self.index = len(self.times) - 1

        return self.current()

    ##################################################

    def count(self):

        return len(self.times)
