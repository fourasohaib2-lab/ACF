"""Real threshold-based event detectors - see acf.events package docstring for the full honest scope (2 of the 8 master-spec event types have real supporting data)."""

from acf.events.detectors.fog_detector import detect_fog_favorable_events
from acf.events.detectors.wind_detector import detect_strong_wind_events

__all__ = ["detect_strong_wind_events", "detect_fog_favorable_events"]
