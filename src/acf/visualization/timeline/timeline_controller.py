"""
Atmospheric Complexity Framework (ACF)

4D Timeline & Animation Controller Module
"""

from typing import Any


class TimelineController:
    """
    Contrôleur Temporel 4D pour l'animation des prévisions numériques et observations historiques.
    """

    def __init__(self, time_steps: list[str] | None = None):
        self.time_steps = time_steps or [
            "2026-07-30T00:00:00Z",
            "2026-07-30T03:00:00Z",
            "2026-07-30T06:00:00Z",
            "2026-07-30T09:00:00Z",
            "2026-07-30T12:00:00Z",
            "2026-07-30T15:00:00Z",
            "2026-07-30T18:00:00Z",
            "2026-07-30T21:00:00Z",
            "2026-07-31T00:00:00Z",
        ]
        self.current_index = 0
        self.playing = False
        self.loop = True
        self.speed_fps = 2.0
        self.vertical_levels = ["surface", "1000hPa", "925hPa", "850hPa", "700hPa", "500hPa", "300hPa", "200hPa"]
        self.current_level_index = 0
        self.frame_cache: dict[str, Any] = {}

    @property
    def current_time(self) -> str:
        """Retourne le timestamp de la trame active."""
        if not self.time_steps:
            return ""
        return self.time_steps[self.current_index]

    @property
    def current_level(self) -> str:
        """Retourne le niveau vertical actif."""
        return self.vertical_levels[self.current_level_index]

    def play(self):
        """Démarre l'animation."""
        self.playing = True

    def pause(self):
        """Met en pause l'animation."""
        self.playing = False

    def next_frame(self) -> str:
        """Passe à l'échéance suivante."""
        if not self.time_steps:
            return ""
        if self.current_index < len(self.time_steps) - 1:
            self.current_index += 1
        elif self.loop:
            self.current_index = 0
        return self.current_time

    def previous_frame(self) -> str:
        """Passe à l'échéance précédente."""
        if not self.time_steps:
            return ""
        if self.current_index > 0:
            self.current_index -= 1
        elif self.loop:
            self.current_index = len(self.time_steps) - 1
        return self.current_time

    def seek_time(self, timestamp: str) -> bool:
        """Se positionne sur une échéance temporelle spécifique."""
        if timestamp in self.time_steps:
            self.current_index = self.time_steps.index(timestamp)
            return True
        return False

    def set_vertical_level(self, level: str) -> bool:
        """Sélectionne le niveau vertical (ex: 500hPa)."""
        if level in self.vertical_levels:
            self.current_level_index = self.vertical_levels.index(level)
            return True
        return False

    def state(self) -> dict[str, Any]:
        """Retourne l'état complet du timeline 4D."""
        return {
            "playing": self.playing,
            "current_index": self.current_index,
            "current_time": self.current_time,
            "total_frames": len(self.time_steps),
            "current_level": self.current_level,
            "speed_fps": self.speed_fps,
            "loop": self.loop,
        }
