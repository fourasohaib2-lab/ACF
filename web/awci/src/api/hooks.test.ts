import { freshData } from "./hooks";

test("placeholder data from the previous key is never handed to the map as the current field", () => {
  expect(freshData({ data: 1, isPlaceholderData: true })).toBeUndefined();
  expect(freshData({ data: 1, isPlaceholderData: false })).toBe(1);
});
