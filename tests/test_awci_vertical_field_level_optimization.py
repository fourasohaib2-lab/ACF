"""
Tests for acf.awci.vertical_field.suggest_lowest_complexity_level() -
closing AWCI's "optimisation de niveau de vol" gap (post-model4d
audit, 2026-09-11, §30 of the cross-checked "AWCI - programme complet"
specification). Real solver run throughout, small n_lat/n_lon/n_levels
overrides to keep it fast - same discipline as
test_awci_vertical_field.py.
"""

from __future__ import annotations

from acf.awci.vertical_field import (
    compute_real_complexity_volume,
    suggest_lowest_complexity_level,
    vertical_profile_at_standard_levels,
)


def _real_profile(**overrides):
    volume = compute_real_complexity_volume(model="ALADIN", n_lat=6, n_lon=10, n_levels=6, steps=2, seed=1)
    lat, lon = float(volume["lats"][2]), float(volume["lons"][3])
    targets = overrides.pop("targets", {"Surface": 1000.0, "FL100": 700.0, "FL200": 500.0, "FL300": 300.0})
    return vertical_profile_at_standard_levels(volume, lat, lon, targets)


def test_empty_profile_returns_honest_none_not_a_fabricated_level():
    result = suggest_lowest_complexity_level({})

    assert result["best_level"] is None
    assert result["best_score"] is None
    assert result["ranking"] == []
    assert result["levels_compared"] == 0
    assert result["status"] == "NO_COMPARABLE_LEVELS"


def test_best_level_is_genuinely_the_minimum_real_awci_score():
    profile = _real_profile()
    result = suggest_lowest_complexity_level(profile)

    assert result["status"] == "REAL_LEVEL_COMPARISON"
    assert result["best_level"] in profile
    assert result["best_score"] == profile[result["best_level"]]["result"]["awci"]
    # The real minimum among every level's own real awci score.
    all_scores = [entry["result"]["awci"] for entry in profile.values()]
    assert result["best_score"] == min(all_scores)


def test_ranking_is_real_values_sorted_ascending():
    profile = _real_profile()
    result = suggest_lowest_complexity_level(profile)

    scores = [score for _, score in result["ranking"]]
    assert scores == sorted(scores)
    assert set(label for label, _ in result["ranking"]) == set(profile.keys())
    assert result["levels_compared"] == len(profile)


def test_ranking_labels_and_scores_match_the_real_profile_exactly():
    profile = _real_profile()
    result = suggest_lowest_complexity_level(profile)

    ranking_dict = dict(result["ranking"])
    for label, entry in profile.items():
        assert ranking_dict[label] == entry["result"]["awci"]


def test_score_key_can_target_physical_score_instead_of_awci():
    profile = _real_profile()
    result_awci = suggest_lowest_complexity_level(profile, score_key="awci")
    result_physical = suggest_lowest_complexity_level(profile, score_key="physical_score")

    assert result_physical["status"] == "REAL_LEVEL_COMPARISON"
    for label, score in result_physical["ranking"]:
        assert score == profile[label]["result"]["physical_score"]
    # Not necessarily the same ranking as awci - own real, independent comparison.
    assert result_awci["levels_compared"] == result_physical["levels_compared"]


def test_levels_with_a_real_undefined_score_are_excluded_not_treated_as_zero():
    profile = _real_profile()
    # Real, deliberately undefined renormalization for one level -
    # must be excluded, never silently read as "0 complexity" (which
    # would make it falsely look like the best level).
    some_label = next(iter(profile))
    profile[some_label]["result"] = dict(profile[some_label]["result"])
    profile[some_label]["result"]["awci"] = None

    result = suggest_lowest_complexity_level(profile)

    assert some_label not in dict(result["ranking"])
    assert result["levels_compared"] == len(profile) - 1
    assert result["best_level"] != some_label


def test_all_levels_undefined_returns_honest_none():
    profile = _real_profile()
    for entry in profile.values():
        entry["result"] = dict(entry["result"])
        entry["result"]["awci"] = None

    result = suggest_lowest_complexity_level(profile)

    assert result["best_level"] is None
    assert result["status"] == "NO_COMPARABLE_LEVELS"


def test_single_level_profile_is_trivially_its_own_best():
    profile = _real_profile(targets={"FL200": 500.0})
    result = suggest_lowest_complexity_level(profile)

    assert result["levels_compared"] == 1
    assert result["best_level"] == "FL200"
    assert result["ranking"] == [("FL200", result["best_score"])]
