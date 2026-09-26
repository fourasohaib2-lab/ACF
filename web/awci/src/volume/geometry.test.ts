import { bandVertices, buildVoxels, levelInterfaces, METERS_PER_DEGREE, parseVolume, splitByBand, type Volume } from "./geometry";

// 3 levels (1000, 850, 500 hPa) over a 2 x 2 grid; gh level-major (level, lat, lon)
const gh = new Float32Array([
  100, 100, 100, 100,
  1500, 1500, 1500, 1500,
  5600, 5600, 5600, 5600,
]);

test("level interfaces follow the Python definition: midpoints, half spacing at the ends, never under the terrain", () => {
  const terrain = new Float32Array([0, 0, 0, 900]);
  const { lower, upper } = levelInterfaces(gh, 3, 4, terrain);
  // level 0: lower = 100 - 0.5*(1500-100) = -600 -> floored at terrain 0; upper = (100+1500)/2 = 800
  expect(lower[0]).toBe(0);
  expect(upper[0]).toBe(800);
  expect(lower[4]).toBe(800);
  expect(upper[4]).toBe(3550);
  expect(upper[8]).toBe(5600 + 0.5 * (5600 - 1500));
  // cell 3 terrain 900 m: level 0 lies entirely under the relief (upper 800 -> floored to 900)
  expect(lower[3]).toBe(900);
  expect(upper[3]).toBe(900);
});

const vol: Volume = { values: new Float32Array([0.9, 0.2, Number.NaN, 0.9, 0.7, 0.7, 0.1, 0.7, 0, 0, 0, 0.95]), gh, nLev: 3, ny: 2, nx: 2,
  lat0: 35, lat1: 35.25, lon0: 2, lon1: 2.25, levels: [1000, 850, 500] };

test("voxels are the real grid cells selected by the predicate; NaN and under-relief levels are never drawn", () => {
  const terrain = new Float32Array([0, 0, 0, 900]);
  const v = buildVoxels(vol, terrain, (x) => (x >= 0.625 ? 0 : -1), [[1, 2, 3, 200]], 40);
  // candidates >= 0.625: (0,c0) 0.9, (0,c3) 0.9 under relief -> dropped, (1,c0..c1,c3) 0.7, (2,c3) 0.95
  expect(v.count).toBe(5);
  expect(Array.from(v.level)).toEqual([0, 1, 1, 1, 2]);
  expect(Array.from(v.cell)).toEqual([0, 0, 1, 3, 3]);
  // first voxel: lon/lat of cell 0 (row 0 = lat0), base 0 m exaggerated x40, thickness 800 m (scaled by the layer)
  expect(Array.from(v.positions.slice(0, 3))).toEqual([2, 35, 0]);
  expect(v.thickness[0]).toBe(800);
  // level 1 of cell 0 starts at 800 m -> z = 800 * 40
  expect(v.positions[5]).toBe(800 * 40);
  expect(Array.from(v.colors.slice(0, 4))).toEqual([1, 2, 3, 200]);
});

test("a voxel's footprint is its grid cell: 0.25 deg wide, narrower in metres towards the pole", () => {
  const south = bandVertices(15, 0.25, 0.25);
  const north = bandVertices(45, 0.25, 0.25);
  const width = (v: number[][]) => Math.max(...v.map((p) => p[0]!)) - Math.min(...v.map((p) => p[0]!));
  const height = (v: number[][]) => Math.max(...v.map((p) => p[1]!)) - Math.min(...v.map((p) => p[1]!));
  expect(height(south)).toBeCloseTo(0.25 * METERS_PER_DEGREE, 3);
  expect(width(south)).toBeCloseTo(0.25 * METERS_PER_DEGREE * Math.cos((15 * Math.PI) / 180), 3);
  expect(width(north) / width(south)).toBeCloseTo(Math.cos(Math.PI / 4) / Math.cos(Math.PI / 12), 6);
});

test("the binary /volume answer is split into values and gh with its grid", () => {
  const body = new Float32Array([...vol.values, ...gh]).buffer;
  const headers = new Headers({ "X-AWCI-Shape": "3,2,2", "X-AWCI-Lats": "35,35.25", "X-AWCI-Lons": "2,2.25", "X-AWCI-Levels": "1000,850,500" });
  const parsed = parseVolume(body, headers);
  expect(parsed.nLev).toBe(3);
  expect(parsed.levels).toEqual([1000, 850, 500]);
  expect(Array.from(parsed.gh.slice(4, 5))).toEqual([1500]);
  expect(Number.isNaN(parsed.values[2])).toBe(true);
  expect(() => parseVolume(new ArrayBuffer(8), headers)).toThrow(/size/);
});

test("the classifier also receives the cell index, so a second volume (genus) can colour the first (fraction)", () => {
  const seen: number[] = [];
  buildVoxels(vol, new Float32Array(4), (_x, _k, i) => { seen.push(i); return -1; }, [], 1);
  expect(seen).toEqual([0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11]); // index 2 is NaN
});

test("voxels are grouped by latitude band so each band gets its own cell footprint", () => {
  const big: Volume = { ...vol, ny: 2, nx: 2, lat0: 15, lat1: 17 }; // rows at 15 and 17 N
  const v = buildVoxels(big, new Float32Array(4), (x) => (x >= 0.625 ? 0 : -1), [[1, 2, 3, 4]], 1);
  const bands = splitByBand(v, 2);
  expect(bands.map((b) => b.lat)).toEqual([15, 17]);
  expect(bands.reduce((s, b) => s + b.count, 0)).toBe(v.count);
  const b0 = bands[0]!;
  // band indices map back to the global voxel order, and attributes are copied consistently
  for (let j = 0; j < b0.count; j++) {
    const g = b0.index[j]!;
    expect(b0.positions[j * 3 + 1]).toBe(v.positions[g * 3 + 1]);
    expect(b0.thickness[j]).toBe(v.thickness[g]);
  }
});
