import { AWCI_CLASS_COLORS, CATEGORICAL, SEQ_BLUE, hexToRgb, rampColor } from "./palette";

test("validated palettes are exactly the documented ones", () => {
  expect(AWCI_CLASS_COLORS).toEqual(["#854494", "#b94c90", "#e45d84", "#ff7f6c", "#ffa85d", "#ffd368"]);
  expect(CATEGORICAL).toEqual(["#3987e5", "#d95926", "#199e70"]);
  expect(SEQ_BLUE[0]).toBe("#0d366b");
  expect(SEQ_BLUE[SEQ_BLUE.length - 1]).toBe("#cde2fb");
});
test("rampColor clamps and hits the end stops", () => {
  expect(rampColor(SEQ_BLUE, -1)).toEqual(hexToRgb("#0d366b"));
  expect(rampColor(SEQ_BLUE, 2)).toEqual(hexToRgb("#cde2fb"));
});
