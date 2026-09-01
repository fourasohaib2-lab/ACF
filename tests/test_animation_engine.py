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


def test_loop_mode():
    """
    CORRECTED: set_loop() used to have zero effect on playback -
    next_frame() never consulted self.loop, so it silently stayed
    clamped on the last frame instead of wrapping back to the first.
    """
    manager = TimeManager()
    manager.load([datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(hours=i) for i in range(3)])
    engine = AnimationEngine(manager)

    engine.set_loop(True)
    engine.next_frame()
    engine.next_frame()
    assert manager.index == 2  # last frame

    looped = engine.next_frame()
    assert manager.index == 0
    assert looped == manager.current()
