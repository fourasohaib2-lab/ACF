import { parseField } from "./client";

test("parseField decodes little-endian float32 and grid headers", () => {
  const values = new Float32Array([1, Number.NaN, 3, 4, 5, 6]);
  const headers = new Headers({ "X-AWCI-Shape": "2,3", "X-AWCI-Lats": "35,35.25", "X-AWCI-Lons": "2,2.5", "X-AWCI-Unit": "m/s" });
  const f = parseField(headers, values.buffer);
  expect([f.ny, f.nx, f.lat0, f.lat1, f.lon0, f.lon1, f.unit]).toEqual([2, 3, 35, 35.25, 2, 2.5, "m/s"]);
  expect(Number.isNaN(f.values[1]!)).toBe(true);
});
test("parseField rejects a size mismatch", () => {
  const headers = new Headers({ "X-AWCI-Shape": "3,3", "X-AWCI-Lats": "0,1", "X-AWCI-Lons": "0,1" });
  expect(() => parseField(headers, new Float32Array(4).buffer)).toThrow();
});
