/** Display helpers for aeronautical observations (METAR decoded by the server, SIGMET) and verification scores. */
import type { AirportsPayload, MetarObs, SigmetProps } from "../api/types";
import { CATEGORICAL, STATUS } from "../theme/palette";
import { fmt } from "./format";

/** FAA flight categories (display only, labelled FAA): mapped on the status scale, text always shown alongside. */
export const CATEGORY_COLORS = { VFR: STATUS.ok, MVFR: STATUS.attention, IFR: STATUS.serious, LIFR: STATUS.critical } as const;

export function ceilingText(o: MetarObs): string {
  switch (o.ceiling_status) {
    case "value": return `${fmt(o.ceiling_ft, 0)} ft`;
    case "none_below_5000": return "aucun sous 5000 ft (CAVOK/NSC)";
    case "none": return "aucun (pas de BKN/OVC)";
    default: return "inconnu (///)";
  }
}

export const convectionText = (c: boolean | null) =>
  c === null ? "inconnue (station automatique)" : c ? "oui (TCU/CB/TS)" : "non";

export const flText = (ft: number | null) =>
  ft === null ? "—" : ft === 0 ? "SFC" : `FL${String(Math.round(ft / 100)).padStart(3, "0")}`;

export const scoreText = (v: number | null) => (v === null ? "—" : fmt(v, 2));

export interface AirportPoint {
  type: "Feature";
  geometry: { type: "Point"; coordinates: [number, number] };
  properties: { icao: string; category: string; convective: boolean; observed: boolean };
}

export function airportFeatures(p: AirportsPayload | undefined): { type: "FeatureCollection"; features: AirportPoint[] } {
  return {
    type: "FeatureCollection",
    features: (p?.airports ?? []).map((a) => ({
      type: "Feature", geometry: { type: "Point", coordinates: [a.lon, a.lat] },
      properties: { icao: a.icao, category: a.observation?.flight_category ?? "none",
        convective: a.observation?.convective === true, observed: !!a.observation },
    })),
  };
}

/** SIGMET hazards (ICAO Annex 3, App. 6): French label, map colour and dash; volcanic ash drawn heavier. */
export const HAZARDS: Record<SigmetProps["hazard"], { label: string; color: string; dash: number[]; width: number }> = {
  TS: { label: "Orages (TS)", color: CATEGORICAL[1], dash: [4, 2], width: 1.5 },
  TURB: { label: "Turbulence (TURB)", color: CATEGORICAL[0], dash: [2, 2], width: 1.5 },
  ICE: { label: "Givrage (ICE)", color: CATEGORICAL[2], dash: [1, 2], width: 1.5 },
  MTW: { label: "Ondes orographiques (MTW)", color: CATEGORICAL[0], dash: [6, 2, 1, 2], width: 1.5 },
  TC: { label: "Cyclone tropical (TC)", color: STATUS.critical, dash: [6, 3], width: 2 },
  VA: { label: "Cendres volcaniques (VA)", color: STATUS.critical, dash: [1, 0], width: 3 },
};
export const sigmetStyle = (h: SigmetProps["hazard"]) => HAZARDS[h];
