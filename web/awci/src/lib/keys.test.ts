import { ownsKeys } from "./keys";

const el = (html: string, pick: string) => {
  document.body.innerHTML = html;
  return document.querySelector(pick);
};

test("form controls and the map keep their own keys; the page does not", () => {
  for (const type of ["radio", "checkbox", "range", "text"]) expect(ownsKeys(el(`<input type="${type}">`, "input"))).toBe(true);
  expect(ownsKeys(el("<select></select>", "select"))).toBe(true);
  expect(ownsKeys(el('<div role="application"><canvas></canvas></div>', "canvas"))).toBe(true);
  expect(ownsKeys(el('<div role="application"></div>', "div"))).toBe(true);
  expect(ownsKeys(document.body)).toBe(false);
  expect(ownsKeys(el("<button>x</button>", "button"))).toBe(false);
  expect(ownsKeys(null)).toBe(false);
});
