/** Route (SP4): waypoints as [lat, lon], URL form "lat,lon;lat,lon", great-circle line for the map. */
export type LatLon = [number, number];
export const MAX_WAYPOINTS = 20;
const RAD = Math.PI / 180;

const round = (x: number) => Math.round(x * 1000) / 1000;

export function parseRoute(raw: string | null): LatLon[] | undefined {
  if (!raw) return undefined;
  const pts: LatLon[] = [];
  for (const part of raw.split(";")) {
    const [a, b, extra] = part.split(",");
    const lat = Number(a);
    const lon = Number(b);
    if (extra !== undefined || a === undefined || b === undefined || a.trim() === "" || b.trim() === ""
        || !Number.isFinite(lat) || !Number.isFinite(lon) || Math.abs(lat) > 90 || Math.abs(lon) > 180) return undefined;
    pts.push([round(lat), round(lon)]);
  }
  return pts.length >= 1 && pts.length <= MAX_WAYPOINTS ? pts : undefined;
}

export const serializeRoute = (pts: LatLon[]) => pts.map(([la, lo]) => `${round(la)},${round(lo)}`).join(";");

const unit = ([lat, lon]: LatLon) => [Math.cos(lat * RAD) * Math.cos(lon * RAD), Math.cos(lat * RAD) * Math.sin(lon * RAD), Math.sin(lat * RAD)];

/** Map line of the route: each leg densified along its great circle (slerp), as the API samples it. */
export function greatCircleLine(pts: LatLon[], perLeg = 64): [number, number][] {
  const out: [number, number][] = [];
  for (let k = 0; k + 1 < pts.length; k++) {
    const a = unit(pts[k]!);
    const b = unit(pts[k + 1]!);
    const dot = Math.min(1, Math.max(-1, a[0]! * b[0]! + a[1]! * b[1]! + a[2]! * b[2]!));
    const omega = Math.acos(dot);
    for (let i = k === 0 ? 0 : 1; i <= perLeg; i++) {
      const f = i / perLeg;
      const s = omega < 1e-12 ? [1 - f, f] : [Math.sin((1 - f) * omega) / Math.sin(omega), Math.sin(f * omega) / Math.sin(omega)];
      const v = [0, 1, 2].map((c) => s[0]! * a[c]! + s[1]! * b[c]!);
      out.push([Math.atan2(v[1]!, v[0]!) / RAD, Math.atan2(v[2]!, Math.hypot(v[0]!, v[1]!)) / RAD]); // [lon, lat]
    }
  }
  return out;
}

/** "DAAG DTTA" → waypoints from the known aerodromes; unknown codes are reported, never guessed. */
export function routeFromIcao(text: string, airports: { icao: string; lat: number; lon: number }[]):
  { points: LatLon[]; unknown: string[] } {
  const codes = text.toUpperCase().split(/[\s,;>-]+/).filter(Boolean);
  const byIcao = new Map(airports.map((a) => [a.icao, a]));
  const points: LatLon[] = [];
  const unknown: string[] = [];
  for (const c of codes) {
    const a = byIcao.get(c);
    if (a) points.push([round(a.lat), round(a.lon)]); else unknown.push(c);
  }
  return { points, unknown };
}

export const NM_PER_KM = 1 / 1.852; // international nautical mile = 1852 m exactly
