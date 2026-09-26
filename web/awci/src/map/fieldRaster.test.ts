import { gridEdges, invMercY, mercY, mercatorRowIndex, renderField, type Grid } from "./fieldRaster";

const ny = 121, nx = 3;
const grid: Grid = { values: new Float32Array(ny * nx).fill(1), ny, nx, lat0: 15, lat1: 45, lon0: 0, lon1: 0.5 };

test("rows are resampled uniformly in Mercator y, not in latitude", () => {
  const rows = mercatorRowIndex(grid, 400);
  expect(rows[0]).toBe(ny - 1);
  expect(rows[399]).toBe(0);
  const e = gridEdges(grid);
  const midLat = invMercY((mercY(e.north) + mercY(e.south)) / 2);
  expect(rows[200]).toBe(Math.round((midLat - grid.lat0) / e.dy));
  // Mercator mid-y lies ~1.2 deg north of the arithmetic mid-latitude: a lat-linear image would be off by that much
  expect(midLat).toBeGreaterThan(31);
  expect(midLat).toBeLessThan(31.5);
});
test("NaN cells are hatched, null colours transparent, values coloured", () => {
  const g: Grid = { values: new Float32Array([Number.NaN, 0, 1, 1]), ny: 2, nx: 2, lat0: 0, lat1: 1, lon0: 0, lon1: 1 };
  const img = renderField(g, (v) => (v > 0 ? [255, 0, 0, 255] : null), 6);
  const alpha = (x: number, y: number) => img.data[(y * img.width + x) * 4 + 3];
  const bottom = img.height - 1; // southern row = lat index 0: [NaN, 0]
  const nanAlphas = Array.from({ length: 6 }, (_, x) => alpha(x, bottom));
  expect(nanAlphas.some((a) => a! > 0) && nanAlphas.some((a) => a === 0)).toBe(true);
  expect(alpha(8, bottom)).toBe(0);
  expect(alpha(8, 0)).toBe(255);
  expect(img.coordinates[0]).toEqual([-0.5, 1.5]);
});
test("a layer where NaN is a real answer (no ceiling) leaves it transparent, never hatched", () => {
  const g: Grid = { values: new Float32Array([Number.NaN, Number.NaN, Number.NaN, Number.NaN]), ny: 2, nx: 2, lat0: 0, lat1: 1, lon0: 0, lon1: 1 };
  const img = renderField(g, () => [255, 0, 0, 255], 6, { nanTransparent: true });
  expect(Array.from(img.data).every((v) => v === 0)).toBe(true);
});
