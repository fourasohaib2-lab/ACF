import { ageLabel, flLabel, fmt, stepLabel, utcLabel } from "./format";

test("fmt uses French separators and an em dash for missing values", () => {
  expect(fmt(1234.5, 1, "J/kg")).toBe(`1${" "}234,5 J/kg`);
  expect(fmt(null)).toBe("—");
  expect(fmt(Number.NaN, 0, "m")).toBe("—");
});
test("labels", () => {
  expect(utcLabel("2026-09-25T12:00:00+00:00")).toBe("25/09 12:00 UTC");
  expect(flLabel(50)).toBe("FL050");
  expect(stepLabel(24)).toBe("+24 h");
  expect(ageLabel("2026-09-25T10:40:00Z", new Date("2026-09-25T12:00:00Z"))).toBe("il y a 1 h 20");
  expect(ageLabel("2026-09-25T11:55:00Z", new Date("2026-09-25T12:00:00Z"))).toBe("il y a 5 min");
});
