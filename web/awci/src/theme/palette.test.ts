import { AWCI_CLASS_COLORS, CATEGORICAL, SEQ_BLUE, TEXT_ON_AWCI_CLASS, hexToRgb, rampColor } from "./palette";

test("validated palettes are exactly the documented ones", () => {
  expect(AWCI_CLASS_COLORS).toEqual(["#2e7d32", "#66bb6a", "#ffeb3b", "#ff9100", "#e8413c", "#a52cba"]);
  expect(CATEGORICAL).toEqual(["#3987e5", "#d95926", "#199e70"]);
  expect(SEQ_BLUE[0]).toBe("#0d366b");
  expect(SEQ_BLUE[SEQ_BLUE.length - 1]).toBe("#cde2fb");
});
test("rampColor clamps and hits the end stops", () => {
  expect(rampColor(SEQ_BLUE, -1)).toEqual(hexToRgb("#0d366b"));
  expect(rampColor(SEQ_BLUE, 2)).toEqual(hexToRgb("#cde2fb"));
});

const lum = (hex: string) => hexToRgb(hex).map((c) => c / 255).map((c) => (c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4))
  .reduce((acc, c, i) => acc + c * [0.2126, 0.7152, 0.0722][i]!, 0);
const contrast = (a: string, b: string) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x! + 0.05) / (y! + 0.05); };

test("vigilance colours keep 3:1 on the map surface and 4.5:1 for the text written on them (WCAG)", () => {
  for (const c of AWCI_CLASS_COLORS) expect(contrast(c, "#0b1220")).toBeGreaterThanOrEqual(3);
  AWCI_CLASS_COLORS.forEach((c, i) => expect(contrast(c, TEXT_ON_AWCI_CLASS[i]!)).toBeGreaterThanOrEqual(4.5));
});
