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
