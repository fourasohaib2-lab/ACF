#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "======================================="
echo " ACF Sprint 08 - Partie 6"
echo " Time Manager"
echo "======================================="

####################################################
# DOSSIER
####################################################

mkdir -p "$PROJECT/src/acf/time"

touch "$PROJECT/src/acf/time/__init__.py"

####################################################
# TIME MANAGER
####################################################

cat > "$PROJECT/src/acf/time/time_manager.py" << 'EOF'
"""
Time Manager
"""

from datetime import datetime


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
EOF

####################################################
# TESTS
####################################################

cat > "$PROJECT/tests/test_time_manager.py" << 'EOF'
from datetime import datetime, timedelta

from acf.time.time_manager import TimeManager


def test_loading():

    manager = TimeManager()

    times = [
        datetime(2026,1,1)+timedelta(hours=i)
        for i in range(5)
    ]

    manager.load(times)

    assert manager.count() == 5


def test_navigation():

    manager = TimeManager()

    times = [
        datetime(2026,1,1)+timedelta(hours=i)
        for i in range(3)
    ]

    manager.load(times)

    assert manager.current() == times[0]

    manager.next()

    assert manager.current() == times[1]

    manager.last()

    assert manager.current() == times[2]

    manager.previous()

    assert manager.current() == times[1]

    manager.first()

    assert manager.current() == times[0]
EOF

echo
echo "Time Manager successfully installed."
