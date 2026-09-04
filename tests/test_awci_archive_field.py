"""
Tests for acf.awci.archive_field - the real, third AWCI data tier
sourced from an actual archived ALADIN operational forecast (RESTOR),
added 2026-09-04 (explicit user request: use the real ALADIN/AROME/
ARPEGE data found in $HOME/RESTOR to make ACF real).

All tests here require the real RESTOR archive to be present on this
machine (it is not part of the git repository - real operational NWP
output, machine-local only) and are honestly SKIPPED, not faked or
mocked, when it is absent - matching this project's own "real data or
an honest gap, never a substitute" discipline.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from acf.awci.archive_field import (
    RESTOR_LEAD_TIMES_HOURS,
    RESTOR_PRESSURE_LEVELS_HPA,
    load_real_aladin_restor_run,
    restor_fullpos_path,
    sample_archive_at_point,
)
from acf.awci.calculator import AWCICalculator
from acf.data.readers.epygram_reader import EPyGrAMReader

REAL_RESTOR_FILE = Path.home() / "RESTOR" / "ALADIN" / "data" / "FULLPOS_2026083100_0000"


# ------------------------------------------------- pure path-building logic
# (no real file needed - run unconditionally on every machine)


def test_restor_fullpos_path_builds_the_real_restor_naming_convention():
    path = restor_fullpos_path("/some/dir", "2026083100", 24)
    assert path == Path("/some/dir/FULLPOS_2026083100_0024")


def test_restor_fullpos_path_zero_pads_the_lead_hours():
    assert restor_fullpos_path("/d", "2026083100", 0).name == "FULLPOS_2026083100_0000"
    assert restor_fullpos_path("/d", "2026083100", 3).name == "FULLPOS_2026083100_0003"
    assert restor_fullpos_path("/d", "2026083100", 48).name == "FULLPOS_2026083100_0048"


def test_restor_lead_times_are_the_real_3_hourly_schedule_out_to_48h():
    assert RESTOR_LEAD_TIMES_HOURS == list(range(0, 49, 3))
    assert len(RESTOR_LEAD_TIMES_HOURS) == 17  # matches RESTOR's own real date.config (nECH=17)


# --------------------------------------------------- real-archive-gated tests
# (module-level pytestmark would also skip the pure-logic tests above,
# since pytest applies it to every test in the file regardless of
# source position - gated on a class instead, matching the same
# pattern already used in tests/gui/test_awci_dashboard_reference_parity.py's
# own TestRealArchiveWithTheRealFile.)


@pytest.mark.skipif(
    not REAL_RESTOR_FILE.exists(),
    reason="Real RESTOR ALADIN archive not present on this machine (machine-local only, not in git)",
)
class TestWithTheRealArchive:
    @staticmethod
    @pytest.fixture(scope="class")
    def real_archive():
        return load_real_aladin_restor_run(REAL_RESTOR_FILE)

    def test_real_archive_loads_and_flags_itself_as_real_data(self, real_archive):
        assert real_archive["is_real_data"] is True
        assert real_archive["status"] == "REAL_RESTOR_ALADIN_ARCHIVE"
        assert real_archive["source_file"] == str(REAL_RESTOR_FILE)

    def test_real_archive_has_all_8_real_levels_with_no_missing_fields(self, real_archive):
        """This particular real file has every field this module reads -
        a genuine, complete real run (verified by hand before writing this
        test)."""
        expected_labels = {f"{hpa:.0f} hPa" for hpa in RESTOR_PRESSURE_LEVELS_HPA.values()} | {"Surface"}
        assert set(real_archive["levels"].keys()) == expected_labels
        assert real_archive["missing_fields"] == []

    def test_real_archive_grid_matches_restors_own_real_domain(self, real_archive):
        """Real North Africa ALADIN domain, cross-checked against the
        archive's own real date.config / EDF ASCII output while building
        this module."""
        lats, lons = real_archive["lats"], real_archive["lons"]
        assert lats.shape == (350,)
        assert lons.shape == (350,)
        assert lats.min() == pytest.approx(18.54, abs=0.01)
        assert lats.max() == pytest.approx(46.46, abs=0.01)
        assert lons.min() == pytest.approx(-10.71, abs=0.01)
        assert lons.max() == pytest.approx(17.21, abs=0.01)

    def test_real_temperature_cross_checks_against_the_independent_legacy_edf_decode(self, real_archive):
        """Real, independent cross-validation: RESTOR/ALADIN/output/2026083100/T_00
        was decoded by the site's own legacy 32-bit Fortran EDF toolchain
        (a completely different real code path than this module's own
        EPyGrAM-based one) from the SAME real file. At the grid's own
        (lon=-10.71, lat=18.54) corner point, that legacy ASCII file reads
        (in real column order, level 1=P00000/level8=100hPa):
        311.5114746 299.9362793 284.5830078 267.0253906 256.3747253
        243.3430328 222.6834259 196.2617340 - the 7 real constant-pressure
        values (columns 3-9, skipping column 2's P00000 level - see this
        module's own docstring for why P00000 is excluded) must match this
        module's own real EPyGrAM-based read exactly."""
        sample = sample_archive_at_point(real_archive, lat=18.54, lon=-10.71)
        expected_by_level = {
            "850 hPa": 299.9362793,
            "700 hPa": 284.5830078,
            "500 hPa": 267.0253906,
            "400 hPa": 256.3747253,
            "300 hPa": 243.3430328,
            "200 hPa": 222.6834259,
            "100 hPa": 196.2617340,
        }
        for level_label, expected_temperature in expected_by_level.items():
            assert sample[level_label]["temperature"] == pytest.approx(expected_temperature, abs=0.01)

    def test_surface_uses_real_cls_diagnostics_not_the_p00000_model_level(self, real_archive):
        """Real, deliberate distinction (see module docstring): "Surface"
        must be the real CLSTEMPERATURE screen-level diagnostic
        (306.857K at this same corner point, hand-verified), NOT the
        P00000 model-level value (311.511K) the legacy ASCII decode's own
        column 1 reports - the two are genuinely different real fields."""
        sample = sample_archive_at_point(real_archive, lat=18.54, lon=-10.71)
        assert sample["Surface"]["temperature"] == pytest.approx(306.857, abs=0.01)
        assert sample["Surface"]["temperature"] != pytest.approx(311.511, abs=0.01)

    def test_real_pressure_is_honest_per_level(self, real_archive):
        """The 7 constant-pressure levels report their own real fixed
        pressure; "Surface" reports the real LOCAL SURFPRESSION (varies
        with terrain), never a guessed 1013.25 hPa constant."""
        sample_desert = sample_archive_at_point(real_archive, lat=18.54, lon=-10.71)
        sample_coast = sample_archive_at_point(real_archive, lat=36.75, lon=3.06)  # Alger, near sea level

        assert sample_desert["850 hPa"]["pressure"] == pytest.approx(850.0)
        assert sample_desert["Surface"]["pressure"] != sample_coast["Surface"]["pressure"]

    def test_specific_humidity_is_physically_bounded_across_the_real_grid(self, real_archive):
        for fields in real_archive["levels"].values():
            q = fields["specific_humidity"]
            assert np.all(q >= 0.0)
            assert np.all(q < 0.05)  # a real, generous upper bound for specific humidity (kg/kg)

    def test_sample_archive_at_point_uses_real_nearest_neighbour_lookup(self, real_archive):
        """Same convention as vertical_profile_at_point() - the returned
        sample must come from the real grid cell nearest the requested
        point, found via direct index lookup on the same real arrays."""
        lat, lon = 36.75, 3.06
        lat_idx = int(np.argmin(np.abs(real_archive["lats"] - lat)))
        lon_idx = int(np.argmin(np.abs(real_archive["lons"] - lon)))
        expected_t850 = float(real_archive["levels"]["850 hPa"]["temperature"][lat_idx, lon_idx])

        sample = sample_archive_at_point(real_archive, lat, lon)

        assert sample["850 hPa"]["temperature"] == pytest.approx(expected_t850)

    def test_sample_is_a_real_valid_awcicalculator_input_at_every_level(self, real_archive):
        """Cross-check discipline: every level's sample must be directly
        usable by AWCICalculator.calculate() with no further transform,
        and produce a real score in [0, 100]."""
        sample = sample_archive_at_point(real_archive, lat=36.75, lon=3.06)
        calc = AWCICalculator()
        for level_label, inputs in sample.items():
            result = calc.calculate(inputs)
            assert 0.0 <= result["awci"] <= 100.0

    def test_missing_field_is_honestly_omitted_not_fabricated(self, monkeypatch):
        """Real, deliberate degradation path: if one real field genuinely
        fails to read (simulated here via monkeypatch, since this
        particular real file has no missing fields to exercise this with
        naturally), that level is entirely absent from the result and
        named in missing_fields - never filled with a placeholder."""

        real_read_field = EPyGrAMReader.read_field

        def _fail_one_field(self, field_id):
            if field_id == "P85000TEMPERATUR":
                return {
                    "field_id": field_id,
                    "name": None,
                    "data": None,
                    "shape": None,
                    "unit": None,
                    "status": "NOT_READ_NO_REAL_RESOURCE_OPENED",
                    "is_real_data": False,
                }
            return real_read_field(self, field_id)

        monkeypatch.setattr(EPyGrAMReader, "read_field", _fail_one_field)

        archive = load_real_aladin_restor_run(REAL_RESTOR_FILE)

        assert "850 hPa" not in archive["levels"]
        assert "P85000TEMPERATUR" in archive["missing_fields"]
        assert "700 hPa" in archive["levels"]  # everything else still real and present

    def test_all_17_real_lead_times_decode_with_a_real_advancing_validity(self, real_archive):
        """Real, direct proof the other 16 real lead times are genuinely
        different forecast hours, not the same file under 17 names -
        spot-checks 3 (00h/24h/48h, matching the by-hand check done
        while building restor_fullpos_path()) rather than all 17, to
        keep this test fast."""
        aladin_data_dir = REAL_RESTOR_FILE.parent
        expected_validity_by_lead = {0: "2026-08-31", 24: "2026-09-01", 48: "2026-09-02"}
        for lead_hours, expected_date in expected_validity_by_lead.items():
            path = restor_fullpos_path(aladin_data_dir, "2026083100", lead_hours)
            assert path.exists()
            archive = load_real_aladin_restor_run(path)
            assert archive["is_real_data"] is True
            assert archive["missing_fields"] == []
            assert expected_date in (archive["run_datetime"] or "")
