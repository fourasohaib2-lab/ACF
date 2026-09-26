import { deleteView, loadViews, saveView } from "./savedViews";

beforeEach(() => window.localStorage.clear());

test("saved views round trip and replace by name", () => {
  saveView("Alger FL300", "?domain=north_africa&level=300");
  saveView("Alger FL300", "?domain=north_africa&level=250");
  expect(loadViews()).toEqual([{ name: "Alger FL300", search: "?domain=north_africa&level=250" }]);
  deleteView("Alger FL300");
  expect(loadViews()).toEqual([]);
});

test("an unusable localStorage never breaks the app", () => {
  const spy = vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => { throw new Error("SecurityError"); });
  expect(loadViews()).toEqual([]);
  spy.mockRestore();
  const set = vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => { throw new Error("QuotaExceeded"); });
  expect(() => saveView("x", "?a=1")).not.toThrow();
  set.mockRestore();
});

test("corrupt stored data is ignored", () => {
  window.localStorage.setItem("awci.savedViews", "{not json");
  expect(loadViews()).toEqual([]);
});
