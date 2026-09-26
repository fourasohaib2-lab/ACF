import { allowedWith, CLOUD_BINS, classifier, VOLUME_LAYERS } from "./layers3d";

const L = Object.fromEntries(VOLUME_LAYERS.map((d) => [d.id, d]));

test("clouds: only cells at or above the fraction threshold, coloured by genus family, opacity by cover", () => {
  const genus = new Float32Array([6, 9, 8, 6, -1]); // Sc, Cb, Cu, Sc, clear
  const classify = classifier(L.clouds!, { threshold: 0.625, awciBounds: [], aux: genus });
  expect(classify(0.5, 0, 0)).toBe(-1); // below BKN
  const sc = classify(0.7, 0, 0);
  const cb = classify(0.9, 0, 1);
  const cu = classify(1.0, 0, 2);
  expect(Math.floor(sc / CLOUD_BINS)).toBe(0); // stratiform family
  expect(Math.floor(cb / CLOUD_BINS)).toBe(2); // Cb family
  expect(Math.floor(cu / CLOUD_BINS)).toBe(1); // Cu/TCU family
  expect(classify(1.0, 0, 3) % CLOUD_BINS).toBeGreaterThan(sc % CLOUD_BINS); // more cover, more opaque
  expect(classify(0.9, 0, 4)).toBe(-1); // genus "clear": nothing drawn even with a high fraction
  expect(L.clouds!.palette.length).toBe(3 * CLOUD_BINS);
});

test("icing, CAT and AWCI select the hazardous cells only", () => {
  const icing = classifier(L.icing!, { threshold: 0, awciBounds: [], aux: undefined });
  expect([icing(0, 0, 0), icing(1, 0, 0)]).toEqual([-1, 0]);
  const cat = classifier(L.cat!, { threshold: 0, awciBounds: [], aux: undefined });
  expect([cat(1, 0, 0), cat(2, 0, 0), cat(3, 0, 0)]).toEqual([-1, 0, 1]); // moderate and above
  const awci = classifier(L.awci!, { threshold: 0, awciBounds: [20, 35, 50, 65, 85], aux: undefined });
  expect([awci(49, 0, 0), awci(50, 0, 0), awci(70, 0, 0), awci(90, 0, 0)]).toEqual([-1, 0, 1, 2]); // High, Very High, Extreme
});

test("every palette entry and legend row is a real colour with a label", () => {
  for (const d of VOLUME_LAYERS) {
    expect(d.legend.length).toBeGreaterThan(0);
    for (const row of d.legend) expect(row.label.length).toBeGreaterThan(2);
    for (const c of d.palette) expect(c.every((x) => Number.isInteger(x) && x >= 0 && x <= 255)).toBe(true);
  }
});

test("at most two layers, and AWCI never with CAT (it already contains it, and their hues are close)", () => {
  expect(allowedWith(["clouds"], "icing")).toBe(true);
  expect(allowedWith(["clouds", "icing"], "cat")).toBe(false);
  expect(allowedWith(["awci"], "cat")).toBe(false);
  expect(allowedWith(["cat"], "awci")).toBe(false);
  expect(allowedWith([], "awci")).toBe(true);
});
