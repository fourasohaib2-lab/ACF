from datetime import datetime, timedelta, timezone

from acf.animation.animation_engine import AnimationEngine
from acf.time.time_manager import TimeManager


def test_play_pause():

    engine = AnimationEngine()

    assert engine.running is False

    engine.play()

    assert engine.running is True

    engine.pause()

    assert engine.running is False


def test_navigation():

    manager = TimeManager()

    manager.load([datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(hours=i) for i in range(4)])

    engine = AnimationEngine(manager)

    assert engine.current_frame() == manager.current()

    engine.next_frame()

    assert engine.current_frame() == manager.current()

    engine.stop()

    assert manager.index == 0
