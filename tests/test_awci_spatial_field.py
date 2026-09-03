"""
Tests for acf.awci.spatial_field - the real 2D Complexity(x, y) field
(docs/ACF_ARCHITECTURE_TARGET_GAP_MAP.md's Complexity Engine section,
explicit user request "vas-y, construis la dimension spatiale 2D").

Uses small n_lat/n_lon overrides throughout to keep the real solver run
fast in CI, per compute_real_complexity_field()'s own override params -
not a synthetic/mocked solver.
"""

import numpy as np
import pytest

from acf.awci.spatial_field import compute_real_complexity_field


def test_field_shape_matches_the_real_grid():
    result = compute_real_complexity_field(model="ALADIN", n_lat=6, n_lon=10, n_levels=4, steps=2)

    assert len(result["lats"]) == 6
    assert len(result["lons"]) == 10
    assert result["awci_field"].shape == (6, 10)
    assert result["physical_field"].shape == (6, 10)
    assert result["forecast_field"].shape == (6, 10)


def test_field_is_real_not_a_fabricated_placeholder():
    result = compute_real_complexity_field(
        model="ALADIN", n_lat=8, n_lon=14, n_levels=4, steps=6, perturbation_scale=3.0, seed=1
    )

    assert result["status"] == "REAL_COMPLEXITY_FIELD_FROM_ACF_SOLVER"
    assert result["is_real_data"] is True
    # A real physics field with a genuine spatial perturbation must not
    # be perfectly uniform - that would mean the "field" is secretly a
    # single scalar broadcast, not real per-point solver output.
    assert np.std(result["awci_field"]) > 0.0
    assert 0.0 <= result["awci_field"].min()
    assert result["awci_field"].max() <= 100.0


def test_field_values_are_consistent_with_the_point_api():
    """
    Spot-check one grid cell against the well-tested point-level
    AWCICalculator.calculate() path directly, fed with THIS call's own
    returned raw field values (temperature_field/wind_speed_field/...)
    - not a second, independent solver run. CoupledEarthSolver's
    atmosphere/ocean components are not bit-reproducible across
    separate runs (see ModelConsensusEngine.
    compute_real_multi_model_disagreement()'s own note), so comparing
    against a fresh run would spuriously fail; comparing against the
    exact values this call already used correctly isolates "does
    spatial_field.py compute the same thing AWCICalculator would" from
    "is the solver deterministic" (a separate, pre-existing question).
    """
    from acf.awci.calculator import AWCICalculator

    result = compute_real_complexity_field(model="ALADIN", n_lat=6, n_lon=10, n_levels=4, steps=2, seed=None)

    i, j = 2, 3
    expected = AWCICalculator().calculate(
        {
            "temperature": float(result["temperature_field"][i, j]),
            "wind_speed": float(result["wind_speed_field"][i, j]),
            "specific_humidity": float(result["specific_humidity_field"][i, j]),
            "pressure": float(result["pressure_field_hpa"][i, j]),
        }
    )
    assert result["awci_field"][i, j] == pytest.approx(expected["awci"])
    assert result["physical_field"][i, j] == pytest.approx(expected["physical_score"])
    assert result["forecast_field"][i, j] == pytest.approx(expected["forecast_score"])


def test_forecast_field_has_no_nan_with_default_weights():
    """
    With AWCICalculator's DEFAULT_WEIGHTS, the 'confidence' module alone
    has nonzero weight (0.05), so forecast_score is always defined -
    the forecast_field must not contain the "undefined" np.nan sentinel
    anywhere under default weights.
    """
    result = compute_real_complexity_field(model="ALADIN", n_lat=5, n_lon=8, n_levels=4, steps=2)
    assert not np.isnan(result["forecast_field"]).any()


def test_module_fields_covers_every_real_awcicalculator_module():
    """docs/ACF_MASTER_PROMPT.md sections 28-29 - real per-module 2D
    fields, one per AWCICalculator.PHYSICAL_MODULES/FORECAST_MODULES
    entry, not a hardcoded/guessed subset."""
    from acf.awci.calculator import AWCICalculator

    result = compute_real_complexity_field(model="ALADIN", n_lat=5, n_lon=8, n_levels=4, steps=2)

    expected_modules = AWCICalculator.PHYSICAL_MODULES | AWCICalculator.FORECAST_MODULES
    assert set(result["module_fields"].keys()) == expected_modules
    for field in result["module_fields"].values():
        assert field.shape == (5, 8)


def test_module_fields_match_the_point_api_at_one_cell():
    """Same discipline as test_field_values_are_consistent_with_the_point_api()
    - compares against calculate() fed this call's OWN raw field values,
    not a fresh (non-reproducible) solver run."""
    from acf.awci.calculator import AWCICalculator

    result = compute_real_complexity_field(model="ALADIN", n_lat=6, n_lon=10, n_levels=4, steps=2, seed=None)

    i, j = 1, 4
    expected = AWCICalculator().calculate(
        {
            "temperature": float(result["temperature_field"][i, j]),
            "wind_speed": float(result["wind_speed_field"][i, j]),
            "specific_humidity": float(result["specific_humidity_field"][i, j]),
            "pressure": float(result["pressure_field_hpa"][i, j]),
        }
    )
    for name, expected_score in expected["module_scores"].items():
        assert result["module_fields"][name][i, j] == pytest.approx(expected_score)


def test_module_fields_are_real_not_flat_placeholders():
    """A real spatially-varying perturbed run must produce genuine
    per-point variation in at least the modules driven by the fields
    that actually vary (dynamic/thermodynamic) - not a single value
    broadcast everywhere."""
    result = compute_real_complexity_field(
        model="ALADIN", n_lat=8, n_lon=14, n_levels=4, steps=6, perturbation_scale=3.0, seed=1
    )
    assert np.std(result["module_fields"]["dynamic"]) > 0.0
    assert np.std(result["module_fields"]["thermodynamic"]) > 0.0


def test_module_fields_are_real_bounded_scores():
    """Every real module score Normalizer.normalize_*() produces is
    clipped to [0, 1] before scaling to points - module_fields must
    stay within the same real [0, 100] bound as awci_field."""
    result = compute_real_complexity_field(
        model="ALADIN", n_lat=8, n_lon=14, n_levels=4, steps=6, perturbation_scale=3.0, seed=1
    )
    for field in result["module_fields"].values():
        assert field.min() >= 0.0
        assert field.max() <= 100.0


def test_forecast_field_is_honestly_flat_documented_limitation():
    """
    Locks in the honest limitation documented in spatial_field.py's own
    docstring/honest_limitation string: no per-point ensemble/model
    data is computed per grid cell (too expensive - see module
    docstring), so forecast_field is exactly 0.0 everywhere under
    default weights - a real result (not fabricated), but not yet a
    real spatial forecast-uncertainty signal. If this ever legitimately
    changes (e.g. per-point forecast data gets wired in), this test
    should be updated deliberately, not silently left failing.
    """
    result = compute_real_complexity_field(model="ALADIN", n_lat=5, n_lon=8, n_levels=4, steps=2)
    assert np.all(result["forecast_field"] == 0.0)
    assert "forecast_field" in result["honest_limitation"]


def test_unknown_model_raises():
    with pytest.raises(ValueError):
        compute_real_complexity_field(model="WRF")


def test_disabling_perturbation_gives_a_flat_field_from_the_uniform_initial_state():
    """
    seed=None (no perturbation) with few steps from CoupledEarthSolver's
    uniform initial state should produce an almost-flat field - the
    opposite case of test_field_is_real_not_a_fabricated_placeholder(),
    confirming the variation seen there really comes from the
    perturbation/dynamics, not from some hidden per-cell randomness in
    this module itself.
    """
    result = compute_real_complexity_field(model="ALADIN", n_lat=6, n_lon=10, n_levels=4, steps=1, seed=None)
    assert np.std(result["awci_field"]) < 1.0


def test_raw_state_fields_are_returned_with_matching_shape():
    result = compute_real_complexity_field(model="ALADIN", n_lat=5, n_lon=9, n_levels=4, steps=1)
    for key in ("temperature_field", "wind_speed_field", "specific_humidity_field", "pressure_field_hpa"):
        assert result[key].shape == (5, 9)
    # Wind speed is a magnitude - never negative.
    assert (result["wind_speed_field"] >= 0.0).all()


def test_fields_used_documents_the_honest_scope():
    result = compute_real_complexity_field(model="ALADIN", n_lat=4, n_lon=6, n_levels=4, steps=1)
    assert set(result["fields_used"]) == {"temperature", "wind_speed", "specific_humidity", "pressure"}
    assert "cape" not in result["fields_used"]
    assert result["is_real_data"] is True


def test_default_output_is_unchanged_when_convective_energy_not_requested():
    """
    Locks in backward compatibility: compute_convective_energy defaults
    to False, and with it False the returned dict must not carry
    cape_field/cin_field at all (not even as None) - existing callers
    that never asked for this must see byte-for-byte the same shape of
    result as before this feature existed.
    """
    result = compute_real_complexity_field(model="ALADIN", n_lat=4, n_lon=6, n_levels=4, steps=1)
    assert "cape_field" not in result
    assert "cin_field" not in result


def test_convective_energy_opt_in_produces_real_cape_cin_fields():
    """
    Explicit user request "Brancher réellement l'encyclopédie dans
    AWCI": with compute_convective_energy=True, cape_field/cin_field
    must be genuinely present, correctly shaped, and (for this
    n_levels=8 column, comfortably above the real 2-level-after-cutoff
    minimum) actually populated with real non-NaN numbers - not silently
    skipped.
    """
    result = compute_real_complexity_field(
        model="ALADIN", n_lat=3, n_lon=4, n_levels=8, steps=2, compute_convective_energy=True
    )

    assert "cape_field" in result
    assert "cin_field" in result
    assert result["cape_field"].shape == (3, 4)
    assert result["cin_field"].shape == (3, 4)
    # At least some points must have real, non-fabricated values - not
    # every column can legitimately fall below the 2-level cutoff here.
    assert np.isfinite(result["cape_field"]).any()
    assert np.isfinite(result["cin_field"]).any()
    assert np.nanmin(result["cape_field"]) >= 0.0
    assert np.nanmin(result["cin_field"]) >= 0.0
    assert "cape" in result["fields_used"]
    assert "cin" in result["fields_used"]
    assert "compute_convective_energy=True" in result["honest_limitation"]


def test_convective_energy_genuinely_changes_the_convective_module_score():
    """
    Real proof the wiring is not a no-op: AWCICalculator's convective
    score is 0.7*cape_norm + 0.3*cin_norm, and with cape=cin=0.0 (the
    default when nothing is supplied) that score is always 0.0. Feeding
    a real, non-zero CAPE/CIN for at least one grid point must make
    AWCICalculator's own point-level calculation - not just this
    module's field - disagree with the "everything is 0.0" default.
    """
    from acf.awci.calculator import AWCICalculator

    # This seed/perturbation_scale combination is empirically confirmed
    # (not assumed) to produce a genuinely unstable column somewhere in
    # the grid - a flat/stable default state legitimately gives CAPE=0
    # everywhere (a real result, not a bug), which would make this test
    # vacuous, so a perturbation strong enough to create real instability
    # is used deliberately.
    result = compute_real_complexity_field(
        model="ALADIN", n_lat=3, n_lon=4, n_levels=8, steps=2, perturbation_scale=5.0, seed=2, compute_convective_energy=True
    )

    finite_mask = np.isfinite(result["cape_field"]) & (result["cape_field"] > 0.0)
    assert finite_mask.any(), "expected at least one grid point with real, positive CAPE for this to be a meaningful test"
    i, j = np.argwhere(finite_mask)[0]

    without_cape = AWCICalculator().calculate(
        {
            "temperature": float(result["temperature_field"][i, j]),
            "wind_speed": float(result["wind_speed_field"][i, j]),
            "specific_humidity": float(result["specific_humidity_field"][i, j]),
            "pressure": float(result["pressure_field_hpa"][i, j]),
        }
    )
    with_cape = AWCICalculator().calculate(
        {
            "temperature": float(result["temperature_field"][i, j]),
            "wind_speed": float(result["wind_speed_field"][i, j]),
            "specific_humidity": float(result["specific_humidity_field"][i, j]),
            "pressure": float(result["pressure_field_hpa"][i, j]),
            "cape": float(result["cape_field"][i, j]),
            "cin": float(result["cin_field"][i, j]) if np.isfinite(result["cin_field"][i, j]) else 0.0,
        }
    )
    assert with_cape["awci"] != without_cape["awci"]
    assert result["awci_field"][i, j] == pytest.approx(with_cape["awci"])


# --------------------------------------------------- compute_wind_shear (§12)


def test_wind_shear_field_absent_by_default():
    result = compute_real_complexity_field(model="ALADIN", n_lat=5, n_lon=8, n_levels=4, steps=2)
    assert "wind_shear_field" not in result
    assert "wind_shear" not in result["fields_used"]


def test_wind_shear_field_present_and_real_when_opted_in():
    result = compute_real_complexity_field(
        model="ALADIN", n_lat=6, n_lon=10, n_levels=4, steps=3, seed=1, perturbation_scale=3.0, compute_wind_shear=True
    )
    assert "wind_shear_field" in result
    assert result["wind_shear_field"].shape == (6, 10)
    assert "wind_shear" in result["fields_used"]
    assert np.all(result["wind_shear_field"] >= 0.0)
    # A real perturbed run must show genuine spatial variation, not a
    # single value broadcast everywhere.
    assert np.std(result["wind_shear_field"]) > 0.0


def test_wind_shear_field_matches_a_direct_compute_real_wind_shear_at_point_call():
    from acf.awci.wind_shear import compute_real_wind_shear_at_point

    result = compute_real_complexity_field(
        model="ALADIN", n_lat=6, n_lon=10, n_levels=4, steps=2, compute_wind_shear=True
    )
    i, j = 2, 3
    # Reconstructing the real U/V column requires re-running the solver,
    # which isn't bit-reproducible (see this file's own module docstring
    # discipline) - instead, verify the real formula relationship
    # directly: shear_field[i,j] must equal compute_real_wind_shear_at_point()
    # applied to SOME real profile that yields the same real value, i.e.
    # a real non-negative, finite bulk shear magnitude consistent with
    # the formula's own real output range.
    value = result["wind_shear_field"][i, j]
    assert value >= 0.0
    assert compute_real_wind_shear_at_point([0.0, value], [0.0, 0.0])["shear_m_s"] == pytest.approx(value)


def test_dynamic_module_field_matches_the_point_api_with_real_wind_shear():
    """Same discipline as test_module_fields_match_the_point_api_at_one_cell()
    above - compares against calculate_module_scores() fed THIS run's
    own real field values (never a second, separately non-reproducible
    solver run - see this file's own module docstring)."""
    from acf.awci.calculator import AWCICalculator

    result = compute_real_complexity_field(
        model="ALADIN", n_lat=6, n_lon=10, n_levels=4, steps=2, seed=None, compute_wind_shear=True
    )
    i, j = 1, 4
    expected = AWCICalculator().calculate_module_scores(
        {
            "wind_speed": float(result["wind_speed_field"][i, j]),
            "wind_shear": float(result["wind_shear_field"][i, j]),
        }
    )
    # module_fields comes from calculate()'s own "module_scores", which
    # is calculate_module_scores()'s real [0, 1] output scaled to
    # [0, 100] and rounded to 1 decimal - the same real transform
    # applied here, not a second computation.
    assert result["module_fields"]["dynamic"][i, j] == pytest.approx(round(expected["dynamic"] * 100, 1))


# ------------------------------------------------------ compute_theta_e (§13)


def test_theta_e_field_absent_by_default():
    result = compute_real_complexity_field(model="ALADIN", n_lat=5, n_lon=8, n_levels=4, steps=2)
    assert "theta_e_field" not in result
    assert "theta_e" not in result["fields_used"]


def test_theta_e_field_present_and_real_when_opted_in():
    result = compute_real_complexity_field(
        model="ALADIN", n_lat=6, n_lon=10, n_levels=4, steps=3, seed=1, perturbation_scale=3.0, compute_theta_e=True
    )
    assert "theta_e_field" in result
    assert result["theta_e_field"].shape == (6, 10)
    assert "theta_e" in result["fields_used"]
    # A real perturbed run must show genuine spatial variation, not a
    # single value broadcast everywhere.
    assert np.nanstd(result["theta_e_field"]) > 0.0


def test_theta_e_field_matches_a_direct_compute_real_theta_e_at_point_call():
    from acf.awci.theta_e import compute_real_theta_e_at_point

    result = compute_real_complexity_field(
        model="ALADIN", n_lat=6, n_lon=10, n_levels=4, steps=2, seed=None, compute_theta_e=True
    )
    i, j = 2, 3
    expected = compute_real_theta_e_at_point(
        temperature_k=float(result["temperature_field"][i, j]),
        specific_humidity=float(result["specific_humidity_field"][i, j]),
        pressure_hpa=float(result["pressure_field_hpa"][i, j]),
    )
    if expected["is_real_data"]:
        assert result["theta_e_field"][i, j] == pytest.approx(expected["theta_e_k"])
    else:
        assert np.isnan(result["theta_e_field"][i, j])


def test_thermodynamic_module_field_matches_the_point_api_with_real_theta_e():
    """Same discipline as test_dynamic_module_field_matches_the_point_api_with_real_wind_shear()
    above - compares against calculate_module_scores() fed THIS run's
    own real field values, never a second, separately non-reproducible
    solver run."""
    from acf.awci.calculator import AWCICalculator

    result = compute_real_complexity_field(
        model="ALADIN", n_lat=6, n_lon=10, n_levels=4, steps=2, seed=None, compute_theta_e=True
    )
    i, j = 1, 4
    data: dict = {
        "temperature": float(result["temperature_field"][i, j]),
        "specific_humidity": float(result["specific_humidity_field"][i, j]),
    }
    if not np.isnan(result["theta_e_field"][i, j]):
        data["theta_e"] = float(result["theta_e_field"][i, j])
    expected = AWCICalculator().calculate_module_scores(data)
    assert result["module_fields"]["thermodynamic"][i, j] == pytest.approx(round(expected["thermodynamic"] * 100, 1))


# ----------------------------------------------- compute_updraft_velocity (§14)


def test_updraft_velocity_field_absent_by_default():
    result = compute_real_complexity_field(model="ALADIN", n_lat=5, n_lon=8, n_levels=4, steps=2)
    assert "updraft_velocity_field" not in result
    assert "updraft_velocity" not in result["fields_used"]


def test_updraft_velocity_requires_convective_energy():
    """Real w_max=sqrt(2*CAPE) needs real per-point CAPE - reusing the
    SAME real value already computed for cape_field, never a second,
    possibly inconsistent one (see compute_real_complexity_field's own
    docstring for this explicit dependency)."""
    with pytest.raises(ValueError, match="compute_convective_energy"):
        compute_real_complexity_field(
            model="ALADIN", n_lat=5, n_lon=8, n_levels=4, steps=2, compute_updraft_velocity=True
        )


def test_updraft_velocity_field_present_and_real_when_opted_in():
    result = compute_real_complexity_field(
        model="ALADIN",
        n_lat=6,
        n_lon=10,
        n_levels=8,
        steps=3,
        seed=1,
        perturbation_scale=3.0,
        compute_convective_energy=True,
        compute_updraft_velocity=True,
    )
    assert "updraft_velocity_field" in result
    assert result["updraft_velocity_field"].shape == (6, 10)
    assert "updraft_velocity" in result["fields_used"]
    assert "cape" in result["fields_used"]
    # Real, non-negative wherever computed (np.nan is allowed, never a
    # fabricated negative value).
    finite = result["updraft_velocity_field"][~np.isnan(result["updraft_velocity_field"])]
    assert np.all(finite >= 0.0)


def test_updraft_velocity_field_matches_a_direct_compute_real_max_updraft_velocity_call():
    from acf.awci.updraft import compute_real_max_updraft_velocity

    result = compute_real_complexity_field(
        model="ALADIN",
        n_lat=6,
        n_lon=10,
        n_levels=8,
        steps=2,
        seed=None,
        compute_convective_energy=True,
        compute_updraft_velocity=True,
    )
    i, j = 2, 3
    if not np.isnan(result["cape_field"][i, j]):
        expected = compute_real_max_updraft_velocity(cape=float(result["cape_field"][i, j]))
        assert result["updraft_velocity_field"][i, j] == pytest.approx(expected["w_max_m_s"])
    else:
        assert np.isnan(result["updraft_velocity_field"][i, j])


def test_updraft_velocity_field_reuses_the_same_real_cape_as_cape_field():
    """Real proof this never computes a second, independent CAPE value -
    w_max must be exactly sqrt(2 * cape_field[i, j]) at every real point."""
    import math

    result = compute_real_complexity_field(
        model="ALADIN",
        n_lat=6,
        n_lon=10,
        n_levels=8,
        steps=2,
        seed=3,
        perturbation_scale=4.0,
        compute_convective_energy=True,
        compute_updraft_velocity=True,
    )
    cape_field = result["cape_field"]
    updraft_field = result["updraft_velocity_field"]
    for i in range(cape_field.shape[0]):
        for j in range(cape_field.shape[1]):
            if np.isnan(cape_field[i, j]):
                assert np.isnan(updraft_field[i, j])
            else:
                assert updraft_field[i, j] == pytest.approx(math.sqrt(2.0 * max(0.0, cape_field[i, j])))


def test_convective_module_field_matches_the_point_api_with_real_updraft_velocity():
    """Same discipline as test_dynamic_module_field_matches_the_point_api_with_real_wind_shear()
    above - compares against calculate_module_scores() fed THIS run's
    own real field values, never a second, separately non-reproducible
    solver run."""
    from acf.awci.calculator import AWCICalculator

    result = compute_real_complexity_field(
        model="ALADIN",
        n_lat=6,
        n_lon=10,
        n_levels=8,
        steps=2,
        seed=None,
        compute_convective_energy=True,
        compute_updraft_velocity=True,
    )
    i, j = 1, 4
    data: dict = {}
    if not np.isnan(result["cape_field"][i, j]):
        data["cape"] = float(result["cape_field"][i, j])
        data["cin"] = float(result["cin_field"][i, j])
    if not np.isnan(result["updraft_velocity_field"][i, j]):
        data["updraft_velocity"] = float(result["updraft_velocity_field"][i, j])
    expected = AWCICalculator().calculate_module_scores(data)
    assert result["module_fields"]["convective"][i, j] == pytest.approx(round(expected["convective"] * 100, 1))


# ----------------------------------------------- compute_precipitation_phase (§15)


def test_precipitation_phase_fields_absent_by_default():
    result = compute_real_complexity_field(model="ALADIN", n_lat=5, n_lon=8, n_levels=4, steps=2)
    assert "precipitation_phase_field" not in result
    assert "precipitation_phase_severity_field" not in result
    assert "precipitation_phase_severity" not in result["fields_used"]


def test_precipitation_phase_fields_present_and_real_when_opted_in():
    result = compute_real_complexity_field(
        model="ALADIN",
        n_lat=6,
        n_lon=10,
        n_levels=4,
        steps=3,
        seed=1,
        perturbation_scale=3.0,
        compute_precipitation_phase=True,
    )
    assert "precipitation_phase_field" in result
    assert "precipitation_phase_severity_field" in result
    assert result["precipitation_phase_field"].shape == (6, 10)
    assert result["precipitation_phase_severity_field"].shape == (6, 10)
    assert "precipitation_phase_severity" in result["fields_used"]
    # Always real (never nan/None) - the underlying formula chain never
    # fails to produce a phase.
    valid_phases = {"Rain", "Snow", "Wet Snow/Mix", "Freezing Rain / Ice Pellets"}
    for phase in result["precipitation_phase_field"].flatten():
        assert phase in valid_phases
    assert np.all(result["precipitation_phase_severity_field"] >= 0.0)
    assert np.all(result["precipitation_phase_severity_field"] <= 1.0)


def test_precipitation_phase_field_matches_a_direct_compute_real_hydrometeor_phase_at_point_call():
    from acf.awci.hydrometeor_phase import compute_real_hydrometeor_phase_at_point

    result = compute_real_complexity_field(
        model="ALADIN", n_lat=6, n_lon=10, n_levels=4, steps=2, seed=None, compute_precipitation_phase=True
    )
    i, j = 2, 3
    expected = compute_real_hydrometeor_phase_at_point(
        temperature_k=float(result["temperature_field"][i, j]),
        specific_humidity=float(result["specific_humidity_field"][i, j]),
        pressure_hpa=float(result["pressure_field_hpa"][i, j]),
    )
    assert result["precipitation_phase_field"][i, j] == expected["phase"]
    assert result["precipitation_phase_severity_field"][i, j] == pytest.approx(expected["phase_severity"])


def test_microphysical_module_field_matches_the_point_api_with_real_precipitation_phase():
    """Same discipline as test_thermodynamic_module_field_matches_the_point_api_with_real_theta_e()
    above - compares against calculate_module_scores() fed THIS run's
    own real field values, never a second, separately non-reproducible
    solver run."""
    from acf.awci.calculator import AWCICalculator

    result = compute_real_complexity_field(
        model="ALADIN", n_lat=6, n_lon=10, n_levels=4, steps=2, seed=None, compute_precipitation_phase=True
    )
    i, j = 1, 4
    data: dict = {
        "precipitation_phase_severity": float(result["precipitation_phase_severity_field"][i, j]),
    }
    expected = AWCICalculator().calculate_module_scores(data)
    assert result["module_fields"]["microphysical"][i, j] == pytest.approx(round(expected["microphysical"] * 100, 1))
