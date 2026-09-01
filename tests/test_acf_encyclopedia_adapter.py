"""
Unit test suite for tools/acf_encyclopedia_adapter.py (Étape 4, Phase 1).

Covers both CLI modes' core logic directly (run_scan/run_verify) and the CLI
entry point (main()) for exit-code and output-mode behavior.
"""

import importlib.util
import sys
from pathlib import Path

import pytest

_TOOL_PATH = Path(__file__).resolve().parent.parent / "tools" / "acf_encyclopedia_adapter.py"
_spec = importlib.util.spec_from_file_location("acf_encyclopedia_adapter", _TOOL_PATH)
assert _spec is not None and _spec.loader is not None
adapter = importlib.util.module_from_spec(_spec)
sys.modules["acf_encyclopedia_adapter"] = adapter
_spec.loader.exec_module(adapter)


def test_run_scan_reports_no_collision_and_the_5_known_soft_duplicates():
    """
    The 5 soft duplicates found and deliberately kept (renamed, not deleted)
    during this session's EncyclopediaRegistry key-collision fix should all
    be detected by the equation-text heuristic.
    """
    result = adapter.run_scan()
    assert result.collision_error is None
    assert result.total_entries > 290

    pairs = {frozenset((k1, k2)) for k1, k2, _norm in result.soft_duplicates}
    expected_pairs = [
        frozenset(("ideal_gas_law", "ideal_gas_law_thermodynamics")),
        frozenset(("virtual_temperature_encyclopedia", "virtual_temperature_law")),
        frozenset(("density_altitude_aviation", "density_altitude_aviation_basic")),
        frozenset(("kolmogorov_five_thirds_law", "kolmogorov_5_3_spectrum")),
    ]
    for expected in expected_pairs:
        assert expected in pairs


def test_run_scan_detects_a_synthetic_collision(monkeypatch):
    """If EncyclopediaRegistry.register() ever raised again, scan() must surface it, not crash."""
    adapter.EncyclopediaRegistry._ensure_initialized()

    def fake_ensure_initialized():
        raise ValueError("EncyclopediaRegistry key collision: 'fake_key' is already registered")

    monkeypatch.setattr(adapter.EncyclopediaRegistry, "_ensure_initialized", staticmethod(fake_ensure_initialized))
    result = adapter.run_scan()
    assert result.collision_error is not None
    assert "fake_key" in result.collision_error


def test_run_verify_has_no_hard_findings():
    """
    CORRECTED (tool bug, not an encyclopedia bug): the first version of this
    tool blindly passed jittered floats to every parameter, which raised a
    spurious TypeError for semi_lagrangian_advection_scheme's int-annotated
    num_iterations (fed to range()). Fixed by coercing int-annotated
    parameters. NotImplementedError (lfc_height_equation, el_height_equation
    - deliberately unimplemented earlier this session) must NOT count as a
    hard finding either - it's an honest disclosure, not a crash.
    """
    result = adapter.run_verify()
    hard = [f for f in result.findings if f.reason in ("exception", "non_finite")]
    assert hard == [], f"unexpected hard findings: {hard}"


def test_run_verify_classifies_lfc_el_as_honestly_unimplemented_not_exception():
    result = adapter.run_verify()
    by_key = {f.key: f.reason for f in result.findings}
    assert by_key.get("lfc_height_equation") == "honestly_unimplemented"
    assert by_key.get("el_height_equation") == "honestly_unimplemented"


def test_run_verify_covers_all_computable_entries_with_no_skipped_array_input():
    """
    CORRECTED (tool coverage gap, not an encyclopedia bug): the 6
    array/matrix-typed compute_func entries (cape_convective_energy,
    cin_convective_inhibition, cost_function_variational_assimilation,
    finite_difference_schemes, storm_relative_helicity_srh,
    vector_calculus_spherical) used to be entirely skipped (generic
    scalar-jitter probing can't safely fabricate array inputs) - all 6 were
    already manually verified correct earlier this session but had no
    automated regression coverage. Added hand-crafted probe pairs
    (_ARRAY_PROBES) for each; verify() must now probe all 89, not 83.

    89 -> 95: a later Physics Guard pass wired 6 previously-missing
    compute_funcs in physical_laws/thermodynamics_laws.py
    (first_law_thermodynamics_atmos, atmospheric_entropy_law,
    enthalpy_atmospheric_law, internal_energy_atmospheric,
    dry_adiabatic_process_law, dewpoint_temperature_law) - each already
    directly computable from its own documented "equation" field. This
    tool's own jitter-sensitivity probe independently confirmed none of
    the 6 are flagged "insensitive" (see the sibling test below).

    95 -> 105: a further pass wired 10 more (reynolds_number_flow,
    aerodynamic_drag_force, hydrostatic_equilibrium_law,
    thermal_wind_relation, gradient_wind_balance, doppler_radial_velocity,
    tropospheric_ozone_photostationary_state, dry_deposition_velocity,
    hail_growth_model, tornado_vortex_dynamics) - see
    tests/test_encyclopedia_compute_func_gaps_batch2.py. Again none of
    the 10 are flagged "insensitive".

    105 -> 119: a further pass wired 14 more (ekman_spiral,
    snow_albedo_feedback, snow_albedo_aging_metamorphism,
    sea_ice_thermodynamics_cice, clear_air_turbulence_index,
    mountain_waves_rotors, wake_turbulence_decay, subcloud_evaporation,
    bernoulli_principle_flow, gps_radio_occultation_gnss_pwv,
    downdraft_cold_pool, entrainment_detrainment_convection,
    vad_velocity_azimuth_display, rayleigh_scattering_cross_section) -
    see tests/test_encyclopedia_compute_func_gaps_batch3.py. This batch
    also surfaced a genuine tool gap (not an encyclopedia bug): 3 of the
    14 use a validated [0, 1] fraction domain (alpha_fresh,
    relative_humidity) that the generic jitter - which routinely lands
    well outside [0, 1] - correctly triggered ValueError on, which
    run_verify() misclassified as a hard "exception" finding. Fixed by
    adding _UNIT_FRACTION_NAMES, the same class of fix as the existing
    int-coercion for range()-fed parameters.
    """
    result = adapter.run_verify()
    assert result.total_computable == 119
    assert result.checked == 119
    skipped = [f for f in result.findings if f.reason == "skipped_array_input"]
    assert skipped == [], f"unexpected skipped entries: {skipped}"


def test_run_verify_array_probed_entries_are_not_flagged_insensitive():
    """The 6 newly-probed array entries must show genuine sensitivity to input, not a false 'insensitive' flag."""
    result = adapter.run_verify()
    flagged_keys = {f.key for f in result.findings}
    for key in adapter._ARRAY_PROBES:
        assert key not in flagged_keys, f"'{key}' unexpectedly flagged: {[f for f in result.findings if f.key == key]}"


def test_main_scan_mode_exits_zero(capsys):
    exit_code = adapter.main(["scan"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "SCAN:" in captured.out


def test_main_verify_mode_exits_zero(capsys):
    exit_code = adapter.main(["verify"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "VERIFY:" in captured.out


def test_main_report_mode_json_output_is_valid(capsys):
    import json

    exit_code = adapter.main(["report", "--json"])
    assert exit_code == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert "scan" in payload
    assert "verify" in payload
    assert payload["scan"]["collision_error"] is None


def test_main_rejects_unknown_mode():
    with pytest.raises(SystemExit):
        adapter.main(["not_a_real_mode"])
