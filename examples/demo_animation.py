from datetime import datetime, timedelta

from acf.animation.animation_engine import AnimationEngine
from acf.time.time_manager import TimeManager

manager = TimeManager()

manager.load([
    datetime(2026,1,1,0)+timedelta(hours=3*i)
    for i in range(8)
])

engine = AnimationEngine(manager)

print("Current :", engine.current_frame())

engine.play()

print("Running :", engine.running)

engine.next_frame()

print("Next :", engine.current_frame())

engine.stop()

print("After stop :", engine.current_frame())
