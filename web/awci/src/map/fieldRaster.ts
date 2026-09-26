import type { Rgba } from "./layers";
import { HATCH } from "../theme/palette";

export interface Grid { values: Float32Array; ny: number; nx: number; lat0: number; lat1: number; lon0: number; lon1: number }
export interface RasterImage {
  data: Uint8ClampedArray; width: number; height: number;
  coordinates: [[number, number], [number, number], [number, number], [number, number]];
}
const RAD = Math.PI / 180;
export const mercY = (lat: number) => Math.log(Math.tan(Math.PI / 4 + (lat * RAD) / 2));
export const invMercY = (y: number) => (2 * Math.atan(Math.exp(y)) - Math.PI / 2) / RAD;

export function gridEdges(g: Grid) {
  if (g.ny < 2 || g.nx < 2) throw new Error("grid needs at least 2x2 cells");
  const dy = (g.lat1 - g.lat0) / (g.ny - 1);
  const dx = (g.lon1 - g.lon0) / (g.nx - 1);
  return { dy, dx, south: g.lat0 - dy / 2, north: g.lat1 + dy / 2, west: g.lon0 - dx / 2, east: g.lon1 + dx / 2 };
}

/** Nearest grid row (latitude-ascending index) of each output row, rows uniform in Mercator y from north to south. */
export function mercatorRowIndex(g: Grid, outRows: number): Int32Array {
  const e = gridEdges(g);
  const yN = mercY(e.north);
  const yS = mercY(e.south);
  const idx = new Int32Array(outRows);
  for (let r = 0; r < outRows; r++) {
    const lat = invMercY(yN + ((r + 0.5) / outRows) * (yS - yN));
    idx[r] = Math.min(g.ny - 1, Math.max(0, Math.round((lat - g.lat0) / e.dy)));
  }
  return idx;
}

/**
 * Nearest-cell raster (no value invented between grid points) in the map's Mercator geometry. NaN is hatched
 * as "no data" unless `nanTransparent`, for layers where NaN is itself an answer (ceiling: no ceiling).
 */
export function renderField(g: Grid, color: (v: number) => Rgba | null, cellPx = 4,
                            { nanTransparent = false }: { nanTransparent?: boolean } = {}): RasterImage {
  const e = gridEdges(g);
  const width = g.nx * cellPx;
  const height = Math.max(1, Math.round(((mercY(e.north) - mercY(e.south)) / (e.dx * RAD)) * cellPx));
  const cells = new Uint8ClampedArray(g.ny * g.nx * 4);
  const nan = new Uint8Array(g.ny * g.nx);
  for (let i = 0; i < g.values.length; i++) {
    const v = g.values[i]!;
    if (Number.isNaN(v)) { nan[i] = 1; continue; }
    const c = color(v);
    if (c) cells.set(c, i * 4);
  }
  const rows = mercatorRowIndex(g, height);
  const data = new Uint8ClampedArray(width * height * 4);
  for (let r = 0; r < height; r++) {
    const base = rows[r]! * g.nx;
    for (let x = 0; x < width; x++) {
      const cell = base + Math.floor(x / cellPx);
      const o = (r * width + x) * 4;
      if (nan[cell]) { if (!nanTransparent && (x + r) % 6 < 2) data.set(HATCH, o); } else data.set(cells.subarray(cell * 4, cell * 4 + 4), o);
    }
  }
  return { data, width, height, coordinates: [[e.west, e.north], [e.east, e.north], [e.east, e.south], [e.west, e.south]] };
}
