"""Tests for acf.hpc_connector.slurm_duration.parse_slurm_duration()."""

import pytest

from acf.hpc_connector.slurm_duration import parse_slurm_duration


@pytest.mark.parametrize(
    "value,expected_seconds",
    [
        ("0:00", 0),
        ("5:23", 5 * 60 + 23),
        ("45", 45),
        ("1:05:23", 1 * 3600 + 5 * 60 + 23),
        ("2-03:05:23", 2 * 86400 + 3 * 3600 + 5 * 60 + 23),
        ("0-00:10:00", 10 * 60),
        ("10:00", 600),
    ],
)
def test_parses_real_slurm_duration_formats(value, expected_seconds):
    assert parse_slurm_duration(value) == expected_seconds


@pytest.mark.parametrize("value", ["UNLIMITED", "unlimited", "NOT_SET", "N/A", "INVALID", ""])
def test_non_numeric_slurm_values_return_none_not_a_guess(value):
    assert parse_slurm_duration(value) is None


@pytest.mark.parametrize("value", ["garbage", "1-2-3", "1:2:3:4", "a:b", "-5:00"])
def test_unparseable_input_returns_none_not_a_guess(value):
    assert parse_slurm_duration(value) is None


def test_whitespace_is_stripped():
    assert parse_slurm_duration("  10:00  ") == 600
