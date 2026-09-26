import { traceStreamline, type WindGrid } from "./streamlines";

const ny = 11, nx = 11;
const wind = (u: number, v: number): WindGrid => ({ u: new Float32Array(ny * nx).fill(u), v: new Float32Array(ny * nx).fill(v),
  ny, nx, lat0: 30, lat1: 40, lon0: 0, lon1: 10 });

test("uniform westerly: constant latitude, spherical metric step", () => {
  const pts = traceStreamline(wind(10, 0), 35, 2, 3600, 5);
  expect(pts.length).toBe(6);
  for (const [, lat] of pts) expect(lat).toBeCloseTo(35, 9);
  const dlon = (10 * 3600) / (6371000 * Math.cos((35 * Math.PI) / 180)) * (180 / Math.PI);
  expect(pts[1]![0] - pts[0]![0]).toBeCloseTo(dlon, 6);
});
test("stops at the domain edge and in calm air", () => {
  expect(traceStreamline(wind(10, 0), 35, 9.9, 3600, 50).length).toBeLessThan(5);
  expect(traceStreamline(wind(0.1, 0), 35, 5, 3600, 50).length).toBe(1);
});
