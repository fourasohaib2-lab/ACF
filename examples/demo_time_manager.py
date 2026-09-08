from datetime import datetime, timedelta

from acf.time.time_manager import TimeManager

manager = TimeManager()

times = [datetime(2026, 1, 1, 0) + timedelta(hours=3 * i) for i in range(8)]

manager.load(times)

print("Current :", manager.current())

manager.next()

print("Next :", manager.current())

manager.last()

print("Last :", manager.current())
