"""
Animation Engine
"""

from acf.time.time_manager import TimeManager


class AnimationEngine:
    def __init__(self, time_manager=None):

        self.time_manager = time_manager or TimeManager()

        self.running = False

        self.loop = False

    ##################################################

    def play(self):

        self.running = True

    ##################################################

    def pause(self):

        self.running = False

    ##################################################

    def stop(self):

        self.running = False

        self.time_manager.first()

    ##################################################

    def next_frame(self):
        """
        NOTE (correction): self.loop was genuinely settable via
        set_loop() but never actually consulted anywhere in this class
        - TimeManager.next() clamps at the last frame and stays there,
        so enabling loop mode had no effect at all on playback: it
        silently never looped back to the first frame.
        """
        if self.loop and self.time_manager.index >= self.time_manager.count() - 1:
            return self.time_manager.first()

        return self.time_manager.next()

    ##################################################

    def previous_frame(self):

        return self.time_manager.previous()

    ##################################################

    def current_frame(self):

        return self.time_manager.current()

    ##################################################

    def set_loop(self, enabled=True):

        self.loop = bool(enabled)
