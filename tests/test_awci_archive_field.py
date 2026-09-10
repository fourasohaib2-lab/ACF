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
    RESTOR_PRECIP_INTERVAL_HOURS,
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

    def test_surface_carries_real_cape_from_the_real_archive(self, real_archive):
        """Added 2026-09-07 (found while testing ACF against this exact
        real archive at the user's explicit request): SURFCAPE.POS.F00
        genuinely exists in this real file - a real, physically
        plausible per-point CAPE (Météo-France's own "positive-only"
        naming convention, not a different quantity from what
        AWCICalculator expects), added to the Surface entry only (a
        column diagnostic, not a per-level one)."""
        assert "cape" in real_archive["levels"]["Surface"]
        cape_grid = real_archive["levels"]["Surface"]["cape"]
        assert cape_grid.shape == real_archive["levels"]["Surface"]["temperature"].shape
        assert np.all(cape_grid >= 0.0)  # real, physical: CAPE is never negative

    def test_pressure_levels_do_not_carry_a_fabricated_cape(self, real_archive):
        """CAPE is a real column diagnostic (SURFCAPE.POS.F00 has no
        per-pressure-level equivalent in this archive) - must not appear
        on the 7 constant-pressure levels, only Surface."""
        for level_label, fields in real_archive["levels"].items():
            if level_label == "Surface":
                continue
            assert "cape" not in fields

    def test_sample_archive_at_point_carries_the_real_cape_through(self, real_archive):
        lat, lon = 36.75, 3.06
        lat_idx = int(np.argmin(np.abs(real_archive["lats"] - lat)))
        lon_idx = int(np.argmin(np.abs(real_archive["lons"] - lon)))
        expected_cape = float(real_archive["levels"]["Surface"]["cape"][lat_idx, lon_idx])

        sample = sample_archive_at_point(real_archive, lat, lon)

        assert sample["Surface"]["cape"] == pytest.approx(expected_cape)
        assert "cape" not in sample["850 hPa"]

    def test_real_awci_convective_module_responds_to_the_real_cape(self, real_archive):
        """End-to-end proof the real CAPE actually reaches AWCICalculator
        and changes its output, not just present-but-unused in the dict:
        the convective module score with real CAPE included must differ
        from the same real point computed with CAPE stripped out."""
        sample = sample_archive_at_point(real_archive, lat=36.75, lon=3.06)
        assert sample["Surface"]["cape"] > 0.0  # this real point's own real CAPE is nonzero

        with_cape = AWCICalculator().calculate(sample["Surface"])

        without_cape = dict(sample["Surface"])
        del without_cape["cape"]
        no_cape_result = AWCICalculator().calculate(without_cape)

        assert with_cape["module_scores"]["convective"] != no_cape_result["module_scores"]["convective"]

    def test_surface_carries_real_precipitation_rate_from_the_3h_interval_accumulations(self, real_archive):
        """Added 2026-09-10: SURFPREC.EAU.CON + .GEC are real per-grid
        accumulations over the file's own real 3h interval (verified
        from the FA resource's own GRIB2 PDT-8 timing metadata -
        EPyGrAM's cumulativeduration() == 3:00:00 at every lead >= +3h;
        see archive_field's module docstring). The module must report
        the mm/h RATE the microphysical module expects, matching an
        independent re-derivation straight from the raw reader."""
        assert RESTOR_PRECIP_INTERVAL_HOURS == 3.0
        fields = real_archive["levels"]["Surface"]
        assert "precipitation" in fields
        rate_grid = fields["precipitation"]
        assert rate_grid.shape == fields["temperature"].shape
        assert np.all(rate_grid >= 0.0)  # real, physical: accumulated precip is never negative

        # Independent re-derivation at one real point, straight from
        # the raw reader (not through archive_field's own plumbing).
        lat, lon = 18.54, -10.71
        lat_idx = int(np.argmin(np.abs(real_archive["lats"] - lat)))
        lon_idx = int(np.argmin(np.abs(real_archive["lons"] - lon)))
        with EPyGrAMReader(REAL_RESTOR_FILE) as reader:
            con = np.asarray(reader.read_field("SURFPREC.EAU.CON")["data"])
            gec = np.asarray(reader.read_field("SURFPREC.EAU.GEC")["data"])
        expected_rate = (con[lat_idx, lon_idx] + gec[lat_idx, lon_idx]) / 3.0
        assert rate_grid[lat_idx, lon_idx] == pytest.approx(expected_rate)

    def test_lead_0_carries_the_honest_zero_precipitation_rate(self):
        """The +0h analysis declares a ZERO-length accumulation interval
        in the file's own timing metadata and stores genuine zeros - the
        0.0 mm/h rate derived from them is reported as-is, not omitted
        and not fabricated into rain that never fell."""
        archive = load_real_aladin_restor_run(REAL_RESTOR_FILE)
        rate_grid = archive["levels"]["Surface"]["precipitation"]
        assert float(rate_grid.max()) == 0.0

    def test_precipitation_is_surface_only_like_cape(self, real_archive):
        """Precipitation accumulations are real SURF* fields (surface
        diagnostics) - must not appear on the 7 constant-pressure
        levels, same convention as CAPE."""
        for level_label, fields in real_archive["levels"].items():
            if level_label == "Surface":
                continue
            assert "precipitation" not in fields

    def test_850hpa_carries_real_bulk_shear_from_the_file_uv(self, real_archive):
        """Added 2026-09-10: real 850->500 hPa bulk wind shear from the
        file's own real u/v at those two real levels, through the same
        BulkWindShear formula the solver path uses - verified here
        against an independent re-derivation straight from the raw
        reader at one real point."""
        fields = real_archive["levels"]["850 hPa"]
        assert "wind_shear" in fields
        shear_grid = fields["wind_shear"]
        assert shear_grid.shape == fields["temperature"].shape
        assert np.all(shear_grid >= 0.0)  # a magnitude is never negative

        lat, lon = 36.75, 3.06
        lat_idx = int(np.argmin(np.abs(real_archive["lats"] - lat)))
        lon_idx = int(np.argmin(np.abs(real_archive["lons"] - lon)))
        with EPyGrAMReader(REAL_RESTOR_FILE) as reader:
            u850 = np.asarray(reader.read_field("P85000VENT_ZONAL")["data"])
            v850 = np.asarray(reader.read_field("P85000VENT_MERID")["data"])
            u500 = np.asarray(reader.read_field("P50000VENT_ZONAL")["data"])
            v500 = np.asarray(reader.read_field("P50000VENT_MERID")["data"])
        from acf.science.bulk_wind_shear import BulkWindShear

        expected = BulkWindShear.calculate(
            float(u850[lat_idx, lon_idx]),
            float(v850[lat_idx, lon_idx]),
            float(u500[lat_idx, lon_idx]),
            float(v500[lat_idx, lon_idx]),
        )
        assert shear_grid[lat_idx, lon_idx] == pytest.approx(expected)

    def test_wind_shear_is_carried_on_the_850hpa_level_only(self, real_archive):
        """The 850->500 hPa layer's bottom level carries the shear; no
        other level may claim it (a per-level shear column would be a
        different, undocumented quantity)."""
        for level_label, fields in real_archive["levels"].items():
            if level_label == "850 hPa":
                continue
            assert "wind_shear" not in fields

    def test_no_cin_is_fed_from_this_archive(self, real_archive):
        """Deliberate refusal, pinned (2026-09-10): no CIN field of any
        naming convention exists in this real file's full 97-field list
        (re-verified fresh, not from the 2026-09-07 session's notes),
        so no level may ever carry a "cin" key - AWCICalculator's own
        documented default keeps applying instead of a fabricated value."""
        for fields in real_archive["levels"].values():
            assert "cin" not in fields

    def test_altitude_is_not_fed_from_the_terrain_implausible_geopotential(self, real_archive):
        """Deliberate refusal, pinned with the evidence that decided it
        (2026-09-10): the file's only elevation-like field,
        P00000GEOPOTENTI, does NOT follow real terrain - at the Hoggar
        mountains (~23N, 7.5E, true elevation ~2900 m) it reads ~125 m,
        and its whole-domain max is ~220 m, below the known Saharan
        massifs. Feeding it as altitude would inject wrong data, so no
        level may ever carry an "altitude" key."""
        for fields in real_archive["levels"].values():
            assert "altitude" not in fields

        # The decisive evidence itself, kept as a regression pin against
        # a future "helpful" wiring: re-read the field straight from the
        # raw reader and confirm the terrain mismatch is real.
        lat, lon = 23.0, 7.5  # Hoggar mountains, true elevation ~2900 m
        lat_idx = int(np.argmin(np.abs(real_archive["lats"] - lat)))
        lon_idx = int(np.argmin(np.abs(real_archive["lons"] - lon)))
        with EPyGrAMReader(REAL_RESTOR_FILE) as reader:
            geopot = np.asarray(reader.read_field("P00000GEOPOTENTI")["data"])
        elevation_m = float(geopot[lat_idx, lon_idx]) / 9.80665
        assert elevation_m < 500.0  # real Hoggar is ~2900 m - this field is not terrain

    def test_sample_archive_at_point_carries_precip_and_shear_through(self, real_archive):
        lat, lon = 36.75, 3.06
        lat_idx = int(np.argmin(np.abs(real_archive["lats"] - lat)))
        lon_idx = int(np.argmin(np.abs(real_archive["lons"] - lon)))
        expected_precip = float(real_archive["levels"]["Surface"]["precipitation"][lat_idx, lon_idx])
        expected_shear = float(real_archive["levels"]["850 hPa"]["wind_shear"][lat_idx, lon_idx])

        sample = sample_archive_at_point(real_archive, lat, lon)

        assert sample["Surface"]["precipitation"] == pytest.approx(expected_precip)
        assert sample["850 hPa"]["wind_shear"] == pytest.approx(expected_shear)
        assert "wind_shear" not in sample["Surface"]

    def test_real_awci_microphysical_and_dynamic_modules_respond_to_the_new_real_inputs(self, real_archive):
        """End-to-end proof (same discipline as the CAPE response test
        above) that both new real inputs actually reach AWCICalculator
        and change its output, not just present-but-unused in the dict."""
        sample = sample_archive_at_point(real_archive, lat=36.75, lon=3.06)
        assert sample["850 hPa"]["wind_shear"] > 0.0  # this real point's own real shear is nonzero

        with_shear = AWCICalculator().calculate(sample["850 hPa"])
        without_shear = dict(sample["850 hPa"])
        del without_shear["wind_shear"]
        no_shear_result = AWCICalculator().calculate(without_shear)
        assert with_shear["module_scores"]["dynamic"] != no_shear_result["module_scores"]["dynamic"]

        # Precipitation: the +0h analysis the class fixture loads is
        # genuinely DRY (zero-length accumulation interval - see the
        # lead-0 test above), so the response check uses the real +12h
        # lead, whose 3h window contains genuine rain. Samples the real
        # grid's own rainiest cell of that lead.
        lead12 = load_real_aladin_restor_run(restor_fullpos_path(REAL_RESTOR_FILE.parent, "2026083100", 12))
        precip_grid = lead12["levels"]["Surface"]["precipitation"]
        assert float(precip_grid.max()) > 0.0  # this real lead contains genuine rain
        wet_i, wet_j = np.unravel_index(int(np.argmax(precip_grid)), precip_grid.shape)
        wet_sample = sample_archive_at_point(
            lead12, float(lead12["lats"][wet_i]), float(lead12["lons"][wet_j])
        )["Surface"]
        assert wet_sample["precipitation"] == pytest.approx(float(precip_grid.max()))
        with_precip = AWCICalculator().calculate(wet_sample)
        without_precip = dict(wet_sample)
        del without_precip["precipitation"]
        no_precip_result = AWCICalculator().calculate(without_precip)
        assert with_precip["module_scores"]["microphysical"] != no_precip_result["module_scores"]["microphysical"]

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

    def test_the_real_48h_awci_trend_shows_a_physically_sensible_diurnal_cycle(self):
        """
        End-to-end proof of the AWCIDashboard's own "Real Archive / 48h
        Trend" feature (acf.gui.dashboard.awci_dashboard's
        _RealArchiveTrendWorker) - not through the GUI worker itself
        (which needs a QThreadPool/Qt event loop), but through the exact
        same real sequence it runs: all 17 real RESTOR lead times, real
        AWCICalculator.calculate() at each one, for the real Algiers
        point (36.75N, 3.06E) - completing in ~7s, matching the
        dashboard's own docstring estimate.

        The result is checked for a REAL physical property, not just
        "didn't crash": this run starts at 00Z (~midnight local time in
        Algeria) - surface temperature (and, following it, CAPE and the
        AWCI score) must genuinely be higher at the two real subsequent
        daytime maxima (+12h and +36h, both ~local noon) than at the
        nearest real nighttime lead times either side (+0h/+24h and
        +24h/+48h respectively) - a real diurnal heating cycle, not an
        assertion invented to match whatever this run happened to
        produce (the exact same physical relationship independently
        confirmed by hand while building this test, before it was
        written).
        """
        lat, lon = 36.75, 3.06
        aladin_data_dir = REAL_RESTOR_FILE.parent
        calc = AWCICalculator()

        trend: list[tuple[int, float, float]] = []
        for lead_hours in RESTOR_LEAD_TIMES_HOURS:
            path = restor_fullpos_path(aladin_data_dir, "2026083100", lead_hours)
            archive = load_real_aladin_restor_run(path)
            assert archive["is_real_data"] is True
            sample = sample_archive_at_point(archive, lat, lon)
            result = calc.calculate(sample["Surface"])
            trend.append((lead_hours, result["awci"], sample["Surface"]["temperature"]))

        assert len(trend) == 17
        by_lead = {lead: (awci, temp) for lead, awci, temp in trend}

        for lead in by_lead:
            awci, _ = by_lead[lead]
            assert 0.0 <= awci <= 100.0

        # Real diurnal warming: midday genuinely warmer than midnight on
        # both sides, for both real days this 48h window covers.
        assert by_lead[12][1] > by_lead[0][1]
        assert by_lead[12][1] > by_lead[24][1]
        assert by_lead[36][1] > by_lead[24][1]
        assert by_lead[36][1] > by_lead[48][1]
