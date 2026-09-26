import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";
import { open } from "./helpers";

for (const theme of ["dark", "light"] as const) {
  test(`no serious or critical accessibility violation (${theme})`, async ({ page }) => {
    await page.addInitScript((t) => localStorage.setItem("awci.theme", t), theme);
    await open(page, "?domain=fixture&step=3&level=700&lat=36.5&lon=3");
    const results = await new AxeBuilder({ page }).exclude(".maplibregl-canvas").analyze();
    const blocking = results.violations.filter((v) => v.impact === "serious" || v.impact === "critical");
    expect(blocking.map((v) => `${v.id}: ${v.nodes.slice(0, 3).map((n) => n.target.join(" ")).join(" | ")}`)).toEqual([]);
  });
}
