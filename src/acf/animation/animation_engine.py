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
