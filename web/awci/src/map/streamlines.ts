/** Streamlines of the real level wind: RK2 (midpoint) on a spherical Earth, bilinear sampling of the grid wind. */
export interface WindGrid { u: Float32Array; v: Float32Array; ny: number; nx: number; lat0: number; lat1: number; lon0: number; lon1: number }
export interface LineFeature { type: "Feature"; properties: { speed: number }; geometry: { type: "LineString"; coordinates: [number, number][] } }
const R = 6371000;
const RAD = Math.PI / 180;

export function sampleWind(g: WindGrid, lat: number, lon: number): [number, number] | null {
  const fy = ((lat - g.lat0) / (g.lat1 - g.lat0)) * (g.ny - 1);
  const fx = ((lon - g.lon0) / (g.lon1 - g.lon0)) * (g.nx - 1);
  if (!(fy >= 0 && fx >= 0 && fy <= g.ny - 1 && fx <= g.nx - 1)) return null;
  const y0 = Math.min(Math.floor(fy), g.ny - 2);
  const x0 = Math.min(Math.floor(fx), g.nx - 2);
  const ty = fy - y0;
  const tx = fx - x0;
  const bil = (a: Float32Array) => {
    const at = (y: number, x: number) => a[y * g.nx + x]!;
    return (1 - ty) * ((1 - tx) * at(y0, x0) + tx * at(y0, x0 + 1)) + ty * ((1 - tx) * at(y0 + 1, x0) + tx * at(y0 + 1, x0 + 1));
  };
  const u = bil(g.u);
  const v = bil(g.v);
  return Number.isFinite(u) && Number.isFinite(v) ? [u, v] : null;
}

function rate(g: WindGrid, lat: number, lon: number): [number, number] | null {
  const w = sampleWind(g, lat, lon);
  return w ? [w[1] / R / RAD, w[0] / (R * Math.cos(lat * RAD)) / RAD] : null; // dlat/dt, dlon/dt in deg/s
}

export function traceStreamline(g: WindGrid, lat: number, lon: number, dtS: number, maxSteps: number,
                                minSpeed = 0.5): [number, number][] {
  const pts: [number, number][] = [[lon, lat]];
  for (let i = 0; i < maxSteps; i++) {
    const w = sampleWind(g, lat, lon);
    if (!w || Math.hypot(w[0], w[1]) < minSpeed) break;
    const k1 = rate(g, lat, lon)!;
    const mid = rate(g, lat + (k1[0] * dtS) / 2, lon + (k1[1] * dtS) / 2);
    if (!mid) break;
    lat += mid[0] * dtS;
    lon += mid[1] * dtS;
    pts.push([lon, lat]);
  }
  return pts;
}

export function streamlineFeatures(g: WindGrid, spacingDeg: number, dtS = 1800, maxSteps = 24) {
  const features: LineFeature[] = [];
  for (let lat = g.lat0 + spacingDeg / 2; lat < g.lat1; lat += spacingDeg) {
    for (let lon = g.lon0 + spacingDeg / 2; lon < g.lon1; lon += spacingDeg) {
      const pts = traceStreamline(g, lat, lon, dtS, maxSteps);
      const w = sampleWind(g, lat, lon);
      if (pts.length >= 3 && w) features.push({ type: "Feature", properties: { speed: Math.hypot(w[0], w[1]) },
        geometry: { type: "LineString", coordinates: pts } });
    }
  }
  return { type: "FeatureCollection" as const, features };
}
