import { fieldOpacity, FIELD_OPACITY } from "./CompareControl";

test("the fade only applies while comparing; every other view draws the field at its normal opacity", () => {
  expect(fieldOpacity(true, 0)).toBe(0);
  expect(fieldOpacity(false, 0)).toBe(FIELD_OPACITY);
});
