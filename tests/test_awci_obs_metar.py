"""METAR decoder (FM 15, WMO-No. 306 / ICAO Annex 3): normative cases and a real 400-report corpus."""

import json
from pathlib import Path

import pytest

from acf.awci.obs.metar import (
    CEILING_NONE,
    CEILING_NONE_BELOW_5000,
    CEILING_UNKNOWN,
    CEILING_VALUE,
    Layer,
    MetarError,
    ceiling_below,
    parse_metar,
)

CORPUS = json.loads((Path(__file__).parent / "data" / "awc" / "metar_corpus_20260926T08.json").read_text())


def test_basic_groups() -> None:
    r = parse_metar("METAR DAAG 260830Z VRB02KT 9999 FEW020 26/17 Q1021")
    assert (r.station, r.day, r.hour, r.minute) == ("DAAG", 26, 8, 30)
    assert r.visibility_m == 10000 and not r.auto and not r.cavok
    assert r.layers == (Layer("FEW", 2000, None),)
    assert r.ceiling_status == CEILING_NONE and r.ceiling_ft is None
    assert r.convective is False and r.flight_category == "VFR"


def test_ceiling_is_lowest_bkn_or_ovc() -> None:
    # 1200 ft ceiling (MVFR: 1000-3000 ft) and 5000 m = 3.1 SM (MVFR: 3-5 SM)
    r = parse_metar("METAR LBPD 260830Z 32006KT 5000 BR SCT008 BKN012 OVC030 17/09 Q1022")
    assert r.ceiling_status == CEILING_VALUE and r.ceiling_ft == 1200
    assert r.weather == ("BR",) and r.flight_category == "MVFR"


def test_vertical_visibility_is_a_ceiling() -> None:
    r = parse_metar("METAR LEMD 260600Z 00000KT 0150 FG VV001 12/12 Q1025")
    assert r.vertical_visibility_ft == 100 and r.ceiling_ft == 100 and r.flight_category == "LIFR"


@pytest.mark.parametrize("group", ["CAVOK", "9999 NSC", "9999 NCD", "9999 SKC"])
def test_no_significant_cloud_means_no_ceiling_below_5000_ft(group: str) -> None:
    r = parse_metar(f"METAR GMMX 260830Z 28003KT {group} 25/14 Q1017")
    assert r.ceiling_status == CEILING_NONE_BELOW_5000
    assert ceiling_below(r, 1500) is False
    assert ceiling_below(r, 6000) is None  # nothing is said above 5000 ft


def test_unknown_cover_or_base_makes_the_ceiling_unknown() -> None:
    assert parse_metar("METAR LFXX 260830Z AUTO 20005KT 9999 ///015 18/12 Q1020").ceiling_status == CEILING_UNKNOWN
    assert parse_metar("METAR LFXX 260830Z AUTO 20005KT 9999 BKN/// 18/12 Q1020").ceiling_status == CEILING_UNKNOWN
    # a known ceiling above an unknown lower layer is not the ceiling
    r = parse_metar("METAR LFXX 260830Z AUTO 20005KT 9999 ///008 BKN020 18/12 Q1020")
    assert r.ceiling_status == CEILING_UNKNOWN and ceiling_below(r, 500) is None
    # ...but a known ceiling below an unknown layer is
    r = parse_metar("METAR LFXX 260830Z AUTO 20005KT 9999 BKN006 ///020 18/12 Q1020")
    assert r.ceiling_ft == 600 and ceiling_below(r, 1000) is True


def test_convection_from_cloud_type_and_weather() -> None:
    assert parse_metar("METAR DABB 260830Z 21010KT 9999 FEW020 FEW026TCU 26/18 Q1019").convective is True
    assert parse_metar("METAR HECA 261400Z 36010KT 9999 SCT030CB 30/20 Q1010").convective is True
    assert parse_metar("METAR DTTA 261400Z 36010KT 9999 VCTS SCT030 30/20 Q1010").convective is True
    assert parse_metar("METAR DTTA 261400Z 36010KT 3000 +TSRA BKN020 22/20 Q1010").convective is True
    assert parse_metar("METAR DTTA 261400Z 36010KT 9999 -SHRA SCT030 22/20 Q1010").convective is False


def test_automatic_station_without_cloud_type_leaves_convection_unknown() -> None:
    assert parse_metar("METAR LBPD 260830Z AUTO 32006KT 9999 BKN039/// 17/09 Q1022").convective is None
    assert parse_metar("METAR LFKJ 260830Z AUTO 20005KT 9999 NCD 26/19 Q1021").convective is None
    assert parse_metar("METAR LFKJ 260830Z AUTO 20005KT CAVOK 26/19 Q1021").convective is False
    assert parse_metar("METAR LFKJ 260830Z AUTO 20005KT 9999 FEW030 26/19 Q1021").convective is False
    assert parse_metar("METAR LFKJ 260830Z AUTO 20005KT 9999 FEW030CB 26/19 Q1021").convective is True


def test_trend_and_remarks_are_not_decoded_as_the_observation() -> None:
    r = parse_metar("METAR GMTA 260840Z 36003KT 9999 SCT005 23/20 Q1019 TEMPO BKN004 TS RMK CB OVC")
    assert r.ceiling_status == CEILING_NONE and r.convective is False


def test_statute_miles_and_fractions() -> None:
    assert parse_metar("METAR KXXX 260853Z 18005KT 10SM CLR 20/10 A3002").visibility_m == pytest.approx(16093.44)
    assert parse_metar("METAR KXXX 260853Z 18005KT 1 1/2SM BR OVC004 20/19 A3002").visibility_m == pytest.approx(2414.016)
    r = parse_metar("METAR KXXX 260853Z 18005KT M1/4SM FG VV002 20/20 A3002")
    assert r.visibility_m == pytest.approx(402.336) and r.flight_category == "LIFR"


def test_nil_and_garbage() -> None:
    r = parse_metar("METAR DAOO 260830Z NIL")
    assert r.nil and r.ceiling_status == CEILING_UNKNOWN and r.convective is None and r.flight_category is None
    with pytest.raises(MetarError):
        parse_metar("not a metar")
    with pytest.raises(MetarError):
        parse_metar("METAR daag 260830Z")


def test_real_corpus_layers_match_the_awc_decoding() -> None:
    mismatches = []
    for item in CORPUS:
        r = parse_metar(item["rawOb"])
        # AWC lists FEW/SCT/BKN/OVC layers only (unknown "//////" groups and VV/// are left out, all-unknown -> null)
        awc = [(c["cover"], c.get("base")) for c in item["clouds"] or []]
        ours = [(layer.cover, layer.base_ft) for layer in r.layers if layer.cover in ("FEW", "SCT", "BKN", "OVC")]
        if ours != awc:
            mismatches.append((item["rawOb"], awc, ours))
    assert not mismatches, mismatches[:5]


def test_real_corpus_flight_category_agrees_with_the_awc() -> None:
    both = [(parse_metar(i["rawOb"]).flight_category, i["fltCat"]) for i in CORPUS if i["fltCat"]]
    agree = sum(ours == theirs for ours, theirs in both)
    assert agree == len(both) == 397, [(o, t) for o, t in both if o != t][:10]  # measured: full agreement


def test_real_corpus_decodes_completely() -> None:
    reports = [parse_metar(i["rawOb"]) for i in CORPUS]
    assert sum(r.convective is True for r in reports) >= 5
    assert all(r.station == i["icaoId"] for r, i in zip(reports, CORPUS))
