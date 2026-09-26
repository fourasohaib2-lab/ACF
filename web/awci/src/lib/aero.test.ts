import { airportFeatures, ceilingText, convectionText, flText, HAZARDS, sigmetStyle, scoreText } from "./aero";
import type { AirportsPayload, MetarObs } from "../api/types";

const obs = (o: Partial<MetarObs>): MetarObs => ({ time: "2026-09-25T03:00:00Z", kind: "METAR", raw: "METAR X", auto: false,
  visibility_m: 10000, weather: [], cavok: false, no_sig_cloud: null, layers: [], vertical_visibility_ft: null,
  ceiling_status: "none", ceiling_ft: null, convective: false, flight_category: "VFR", ...o });

test("ceiling text states exactly what the METAR says, including its 5000 ft limit", () => {
  expect(ceilingText(obs({ ceiling_status: "value", ceiling_ft: 400 }))).toBe("400 ft");
  expect(ceilingText(obs({ ceiling_status: "none_below_5000" }))).toBe("aucun sous 5000 ft (CAVOK/NSC)");
  expect(ceilingText(obs({ ceiling_status: "none" }))).toBe("aucun (pas de BKN/OVC)");
  expect(ceilingText(obs({ ceiling_status: "unknown" }))).toBe("inconnu (///)");
});

test("convection text never turns unknown into no", () => {
  expect(convectionText(true)).toBe("oui (TCU/CB/TS)");
  expect(convectionText(false)).toBe("non");
  expect(convectionText(null)).toBe("inconnue (station automatique)");
});

test("flight levels and scores", () => {
  expect(flText(15000)).toBe("FL150");
  expect(flText(0)).toBe("SFC");
  expect(flText(null)).toBe("—");
  expect(scoreText(0.4567)).toBe("0,46");
  expect(scoreText(null)).toBe("—");
});

test("airports become map points carrying category, convection and observed flags", () => {
  const payload = { airports: [
    { icao: "DAAG", name: "Alger", lat: 36.69, lon: 3.21, elev_m: 18, metar: true, taf: true,
      observation: obs({ flight_category: "IFR", convective: true }) },
    { icao: "DAOO", name: "Oran", lat: 35.62, lon: -0.62, elev_m: 90, metar: true, taf: true, observation: null },
  ] } as AirportsPayload;
  const fc = airportFeatures(payload);
  expect(fc.features[0]!.geometry.coordinates).toEqual([3.21, 36.69]);
  expect(fc.features[0]!.properties).toMatchObject({ icao: "DAAG", category: "IFR", convective: true, observed: true });
  expect(fc.features[1]!.properties).toMatchObject({ category: "none", observed: false });
});

test("every SIGMET hazard has a French label and a style; volcanic ash stands out", () => {
  for (const h of ["TS", "TURB", "ICE", "VA", "TC", "MTW"] as const) expect(HAZARDS[h].label.length).toBeGreaterThan(3);
  expect(sigmetStyle("VA").width).toBeGreaterThan(sigmetStyle("TS").width);
});
