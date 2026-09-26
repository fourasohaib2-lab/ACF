/**
 * Voxel geometry of the 3-D view (spec SP2B §2): every voxel is a real grid cell of a real pressure level,
 * nothing is interpolated in space. Vertical bounds are the interfaces between neighbouring geopotential
 * heights (same definition as acf.awci.ops.clouds.level_interfaces), floored at the model surface.
 */

export interface Volume {
  values: Float32Array; // level-major (level, lat, lon)
  gh: Float32Array; // geopotential height (m), same layout
  nLev: number; ny: number; nx: number;
  lat0: number; lat1: number; lon0: number; lon1: number; // first/last row and column centres
  levels: number[]; // hPa
}

/** Web-Mercator spherical Earth used by deck.gl: 2 pi R / 360 with R = 6 378 137 m. */
export const METERS_PER_DEGREE = (2 * Math.PI * 6378137) / 360;

export type Rgba = [number, number, number, number];

export function parseVolume(body: ArrayBuffer, headers: Headers): Volume {
  const [nLev, ny, nx] = (headers.get("X-AWCI-Shape") ?? "").split(",").map(Number) as [number, number, number];
  const [lat0, lat1] = (headers.get("X-AWCI-Lats") ?? "").split(",").map(Number) as [number, number];
  const [lon0, lon1] = (headers.get("X-AWCI-Lons") ?? "").split(",").map(Number) as [number, number];
  const n = nLev * ny * nx;
  if (!(n > 0) || body.byteLength !== 2 * n * 4) throw new Error(`volume size ${body.byteLength} B does not match shape ${nLev}x${ny}x${nx}`);
  return { values: new Float32Array(body, 0, n), gh: new Float32Array(body, n * 4, n), nLev, ny, nx, lat0, lat1, lon0, lon1,
    levels: (headers.get("X-AWCI-Levels") ?? "").split(",").filter(Boolean).map(Number) };
}

export function levelInterfaces(gh: Float32Array, nLev: number, nCell: number, terrain: Float32Array) {
  const lower = new Float32Array(nLev * nCell);
  const upper = new Float32Array(nLev * nCell);
  for (let c = 0; c < nCell; c++) {
    const floor = Number.isFinite(terrain[c]!) ? terrain[c]! : 0;
    for (let k = 0; k < nLev; k++) {
      const z = gh[k * nCell + c]!;
      const below = k > 0 ? gh[(k - 1) * nCell + c]! : Number.NaN;
      const above = k < nLev - 1 ? gh[(k + 1) * nCell + c]! : Number.NaN;
      const lo = k > 0 ? 0.5 * (z + below) : z - 0.5 * (above - z);
      const hi = k < nLev - 1 ? 0.5 * (z + above) : z + 0.5 * (z - below);
      lower[k * nCell + c] = Math.max(lo, floor);
      upper[k * nCell + c] = Math.max(hi, floor);
    }
  }
  return { lower, upper };
}

export interface Voxels {
  count: number;
  positions: Float32Array; // lon, lat, base (m) x exaggeration
  thickness: Float32Array; // m (the layer multiplies it by the exaggeration)
  colors: Uint8Array; // rgba
  level: Uint8Array; // level index
  cell: Uint32Array; // row * nx + col
  row: Uint16Array;
}

/**
 * Binary attributes of the voxels that `classify` selects: it returns an index into `palette`, or -1 (not
 * drawn). NaN values and levels entirely under the model surface are never drawn. `exaggeration` multiplies
 * heights (always shown in the UI). Two passes over typed arrays, no allocation per voxel (measured: the
 * per-voxel colour arrays made a full 350 000-cell volume take ~150 ms).
 */
export function buildVoxels(v: Volume, terrain: Float32Array, classify: (value: number, level: number, index: number) => number,
                            palette: Rgba[], exaggeration: number): Voxels {
  const nCell = v.ny * v.nx;
  const total = v.nLev * nCell;
  const { lower, upper } = levelInterfaces(v.gh, v.nLev, nCell, terrain);
  const dLat = v.ny > 1 ? (v.lat1 - v.lat0) / (v.ny - 1) : 0;
  const dLon = v.nx > 1 ? (v.lon1 - v.lon0) / (v.nx - 1) : 0;
  const picked = new Int32Array(total);
  const klass = new Int16Array(total);
  let n = 0;
  for (let k = 0, i = 0; k < v.nLev; k++) {
    for (let c = 0; c < nCell; c++, i++) {
      const value = v.values[i]!;
      if (value !== value || upper[i]! <= lower[i]!) continue; // value !== value: NaN
      const idx = classify(value, k, i);
      if (idx < 0) continue;
      picked[n] = i;
      klass[n] = idx;
      n++;
    }
  }
  const out: Voxels = { count: n, positions: new Float32Array(n * 3), thickness: new Float32Array(n), colors: new Uint8Array(n * 4),
    level: new Uint8Array(n), cell: new Uint32Array(n), row: new Uint16Array(n) };
  for (let j = 0; j < n; j++) {
    const i = picked[j]!;
    const k = Math.floor(i / nCell);
    const c = i - k * nCell;
    const r = Math.floor(c / v.nx);
    out.positions[j * 3] = v.lon0 + (c - r * v.nx) * dLon;
    out.positions[j * 3 + 1] = v.lat0 + r * dLat;
    out.positions[j * 3 + 2] = lower[i]! * exaggeration;
    out.thickness[j] = upper[i]! - lower[i]!;
    const rgba = palette[klass[j]!]!;
    out.colors[j * 4] = rgba[0];
    out.colors[j * 4 + 1] = rgba[1];
    out.colors[j * 4 + 2] = rgba[2];
    out.colors[j * 4 + 3] = rgba[3];
    out.level[j] = k;
    out.cell[j] = c;
    out.row[j] = r;
  }
  return out;
}

/** Rectangle (metre offsets around the cell centre) of a dLat x dLon cell at `latDeg` (deck.gl spherical metres). */
export function bandVertices(latDeg: number, dLat: number, dLon: number): number[][] {
  const w = (Math.abs(dLon) * METERS_PER_DEGREE * Math.cos((latDeg * Math.PI) / 180)) / 2;
  const h = (Math.abs(dLat) * METERS_PER_DEGREE) / 2;
  return [[-w, -h], [w, -h], [w, h], [-w, h]];
}

export interface Band {
  lat: number; // band centre latitude (deg), used for the cell footprint
  count: number;
  positions: Float32Array; thickness: Float32Array; colors: Uint8Array;
  index: Uint32Array; // global voxel index of each band voxel (picking)
}

/** Voxels grouped by latitude band of `bandDeg` degrees (counting sort, attributes copied once). */
export function splitByBand(v: Voxels, bandDeg: number): Band[] {
  const key = new Int32Array(v.count);
  const counts = new Map<number, number>();
  for (let j = 0; j < v.count; j++) {
    const b = Math.floor(v.positions[j * 3 + 1]! / bandDeg);
    key[j] = b;
    counts.set(b, (counts.get(b) ?? 0) + 1);
  }
  const bands = new Map<number, Band & { fill: number }>();
  for (const [b, n] of [...counts].sort((x, y) => x[0] - y[0])) {
    bands.set(b, { lat: (b + 0.5) * bandDeg, count: n, positions: new Float32Array(n * 3), thickness: new Float32Array(n),
      colors: new Uint8Array(n * 4), index: new Uint32Array(n), fill: 0 });
  }
  for (let j = 0; j < v.count; j++) {
    const band = bands.get(key[j]!)!;
    const f = band.fill++;
    band.positions.set(v.positions.subarray(j * 3, j * 3 + 3), f * 3);
    band.thickness[f] = v.thickness[j]!;
    band.colors.set(v.colors.subarray(j * 4, j * 4 + 4), f * 4);
    band.index[f] = j;
  }
  return [...bands.values()].map(({ fill: _fill, ...band }) => band);
}
