"""
Regression test for BriefingGenerator.generate_briefing()'s timestamp -
real bug found during the 2026-09-12 ICAO/WMO compliance audit: the
generated "OFFICIAL METEOROLOGICAL BRIEFING" labelled its timestamp
"UTC" while actually computing it from datetime.now() (this machine's
real local time) - the identical fabricated-UTC-label pattern already
found and fixed once in this same file (see its own module docstring's
"operationally dangerous" correction) and in ACFWorkstation's header
clock. ICAO Annex 3 §4.1 mandates UTC exclusively for aeronautical/
official meteorological information.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from acf.reports.briefings.briefing_generator import BriefingGenerator


def test_generated_timestamp_is_genuine_utc_not_local_time():
    fake_local = datetime(2026, 1, 1, 2, 0, 0)  # 02:00 "local"
    fake_utc = datetime(2026, 1, 1, 14, 0, 0, tzinfo=timezone.utc)  # genuinely 14:00 UTC, same real instant

    class _FakeDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return fake_utc if tz is not None else fake_local

    with patch("acf.reports.briefings.briefing_generator.datetime", _FakeDateTime):
        briefing = BriefingGenerator.generate_briefing()

    assert briefing["timestamp"] == "2026-01-01 14:00 UTC"
    assert "2026-01-01 02:00 UTC" not in briefing["content"]


def test_generated_timestamp_is_close_to_real_utc_now():
    before = datetime.now(timezone.utc)

    briefing = BriefingGenerator.generate_briefing()

    after = datetime.now(timezone.utc)
    stamped = datetime.strptime(briefing["timestamp"], "%Y-%m-%d %H:%M UTC").replace(tzinfo=timezone.utc)
    assert before - timedelta(minutes=1) <= stamped <= after + timedelta(minutes=1)
