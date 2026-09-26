import { availableLayers, newerRun, nextLevel, nextStep, parseView, resolveView, serializeView, withPinnedRun } from "./view";

const meta = { steps: [0, 3, 6, 9], missing_steps: [6], valid_times: ["2026-09-25T12:00:00+00:00",
  "2026-09-25T15:00:00+00:00", "2026-09-25T18:00:00+00:00", "2026-09-25T21:00:00+00:00"],
  levels_hpa: [1000, 850, 500, 300, 200], level_layers: ["awci", "t"], surface_layers: ["mucape"] } as never;

test("URL round trip keeps every field and drops invalid ones", () => {
  const v = parseView("?domain=north_africa&run=2026092512&step=9&level=300&layer=awci&lat=36.7&lon=3.2&ov=mtg_fd:ir105_hrfi");
  expect(parseView(serializeView(v))).toEqual(v);
  expect(parseView("?run=../../etc&step=abc&layer=<x>").run).toBeUndefined();
  expect(parseView("?step=abc").step).toBeUndefined();
});
test("missing steps are skipped both ways", () => {
  expect(nextStep(meta, 3, 1)).toBe(9);
  expect(nextStep(meta, 9, -1)).toBe(3);
  expect(nextStep(meta, 9, 1)).toBe(9);
});
test("levels move up (lower pressure) and down", () => {
  expect(nextLevel(meta, 500, 1)).toBe(300);
  expect(nextLevel(meta, 1000, -1)).toBe(1000);
});
test("resolveView picks the step nearest to now, never a missing one", () => {
  const r = resolveView(parseView(""), [{ name: "d", default: true }] as never,
    [{ run: "2026092512", status: "partial" }] as never, meta, new Date("2026-09-25T18:40:00Z"));
  // 18:40: +6 h (18:00) is missing; among available steps +9 h (21:00, 2 h 20 away) beats +3 h (15:00, 3 h 40)
  expect(r).toMatchObject({ domain: "d", run: "2026092512", step: 9, level: 300, layer: "awci" });
});
test("layers absent from the run are not offered", () => {
  expect(availableLayers(meta).map((d) => d.id)).toEqual(["awci", "mucape"]);
});

test("the first interaction pins the run shown, so a new run never shifts the valid time silently", () => {
  expect(withPinnedRun({ layer: "awci", ov: [] }, "2026092500", { step: 12 })).toEqual({ step: 12, run: "2026092500" });
  expect(withPinnedRun({ layer: "awci", ov: [], run: "2026092418" }, "2026092418", { step: 12 })).toEqual({ step: 12 });
  // "Maintenant" explicitly un-pins
  expect(withPinnedRun({ layer: "awci", ov: [], run: "2026092418" }, "2026092418", { run: undefined, step: undefined }))
    .toEqual({ run: undefined, step: undefined });
  expect(withPinnedRun({ layer: "awci", ov: [] }, undefined, { step: 3 })).toEqual({ step: 3 });
});

test("a newer usable run than the pinned one is announced", () => {
  const runs = [{ run: "2026092506", status: "complete" }, { run: "2026092500", status: "complete" }] as never;
  expect(newerRun(runs, "2026092500")).toBe("2026092506");
  expect(newerRun(runs, "2026092506")).toBeUndefined();
  expect(newerRun(runs, undefined)).toBeUndefined();
  expect(newerRun([{ run: "2026092506", status: "failed" }, { run: "2026092500", status: "complete" }] as never, "2026092500")).toBeUndefined();
});
