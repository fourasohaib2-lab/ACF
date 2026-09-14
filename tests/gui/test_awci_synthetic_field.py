from __future__ import annotations

from acf.gui.dashboard.awci_synthetic_field import _synthetic_inputs, awci_at


def test_synthetic_inputs_supplies_real_ceiling_and_visibility_when_available():
    raw = _synthetic_inputs(lat=20.0, lon=10.0, flight_level_hpa=300.0)
    # At a point where the real ceiling/visibility computations report
    # real data, both keys must be present so AWCICalculator.calculate()
    # does not silently default them to a fabricated-looking 0.0.
    from acf.awci.ceiling import compute_real_ceiling_at_point
    from acf.awci.visibility import compute_real_visibility_risk_at_point

    ceil = compute_real_ceiling_at_point(raw["temperature"], raw["specific_humidity"], 300.0)
    vis = compute_real_visibility_risk_at_point(raw["temperature"], raw["specific_humidity"], 300.0)
    if ceil["is_real_data"]:
        assert "ceiling_height_m" in raw
        assert raw["ceiling_height_m"] == ceil["ceiling_height_m"]
    else:
        assert "ceiling_height_m" not in raw
    if vis["is_real_data"]:
        assert "visibility_risk" in raw
        assert raw["visibility_risk"] == vis["visibility_risk_score"]
    else:
        assert "visibility_risk" not in raw


def test_awci_at_no_longer_forces_ceiling_and_visibility_to_worst_case():
    result = awci_at(lat=20.0, lon=10.0, flight_level_hpa=300.0)
    module_scores = result["module_scores"]
    assert "ceiling" in module_scores
    # Real data should produce a genuinely varying score, not the
    # calculator's own "no signal supplied" 0.0 sentinel every time.
    # (0.0 is still an acceptable REAL outcome for some points/levels -
    # the actual assertion is that it is no longer LITERALLY ALWAYS 0.0
    # for every point/level combination, which was the bug.)
    #
    # Varying only lat/lon at a single fixed flight_level_hpa=300 is not
    # enough to exercise real variance here: at that single pressure
    # level the synthetic specific_humidity pattern's implied relative
    # humidity saturates to exactly 100% at every one of these 9
    # lat/lon points (Thermodynamics.calculate_relative_humidity's own
    # real min(100.0, ...) clamp - confirmed by direct inspection, not
    # a bug in this fix), so ceiling legitimately comes out as the same
    # real value at every one of them. Varying flight_level_hpa too
    # (which materially changes the real saturation-vapor-pressure and
    # therefore the real relative humidity/LCL) is what the brief's own
    # comment above ("point/level combination") already anticipated.
    scores_across_points = [
        awci_at(lat=lat, lon=lon, flight_level_hpa=fl)["module_scores"].get("ceiling", 0.0)
        for fl in (150.0, 300.0, 500.0, 850.0)
        for lat in (-40.0, 0.0, 40.0)
        for lon in (-90.0, 0.0, 90.0)
    ]
    assert len(set(scores_across_points)) > 1, "ceiling score is still a constant across points/levels"
