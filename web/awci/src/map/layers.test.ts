import { colorFn, layerDef } from "./layers";
import { AWCI_CLASS_COLORS, CATEGORICAL, hexToRgb } from "../theme/palette";

const BOUNDS = [20, 35, 50, 65, 85];
test("AWCI colours follow the profile class bounds (value >= bound goes up)", () => {
  const c = colorFn(layerDef("awci"), BOUNDS);
  expect(c(19.9)?.slice(0, 3)).toEqual(hexToRgb(AWCI_CLASS_COLORS[0]));
  expect(c(20)?.slice(0, 3)).toEqual(hexToRgb(AWCI_CLASS_COLORS[1]));
  expect(c(99)?.slice(0, 3)).toEqual(hexToRgb(AWCI_CLASS_COLORS[5]));
});
test("genus map folds genera into three validated families", () => {
  const c = colorFn(layerDef("genus_low"), BOUNDS);
  expect(c(9)?.slice(0, 3)).toEqual(hexToRgb(CATEGORICAL[1])); // Cb
  expect(c(8)?.slice(0, 3)).toEqual(hexToRgb(CATEGORICAL[2])); // Cu / TCU
  expect(c(6)?.slice(0, 3)).toEqual(hexToRgb(CATEGORICAL[0])); // stratiform (Sc)
  expect(c(-1)).toBeNull(); // clear: transparent, not a colour
});
test("no-hazard codes are transparent", () => {
  expect(colorFn(layerDef("icing_potential"), BOUNDS)(0)).toBeNull();
  expect(colorFn(layerDef("icing_potential"), BOUNDS)(1)).not.toBeNull();
});
