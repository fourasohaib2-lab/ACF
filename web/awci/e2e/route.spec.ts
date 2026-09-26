import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";
import { clickMap, open } from "./helpers";

test("a route drawn on the map gives its cross-section and its meteogram, which sets the step", async ({ page }) => {
  await open(page, "?domain=fixture&step=0&level=700");
  await page.getByRole("button", { name: "Route", exact: true }).click();
  const panel = page.getByRole("region", { name: "Route" });
  await expect(panel).toContainText("0/20");
  await clickMap(page, 0.5, 0.3); // clear of the legend (bottom left) and the toolbar (top right)
  await expect(panel).toContainText("1/20");
  await clickMap(page, 0.75, 0.5);
  await expect(panel).toContainText("2/20");
  await expect(page).toHaveURL(/route=/);
  await page.keyboard.press("Escape"); // ends the drawing, keeps the route
  await expect(panel.getByRole("button", { name: "Tracer sur la carte" })).toBeVisible();
  await expect(panel.getByRole("img", { name: /^Coupe verticale de AWCI le long de la route/ })).toBeVisible();
  await expect(panel.getByRole("table", { name: /AWCI maximal le long de la route/ })).toBeVisible();
  await expect(panel.getByRole("columnheader")).toHaveText(["Niveau", "+0 h", "+3 h"]); // the fixture run's steps
  await panel.getByRole("button", { name: /^\+3 h, FL301 : AWCI max/ }).click();
  await expect(page).toHaveURL(/level=300/);
  await expect(page).toHaveURL(/step=3/);
});

test("a route from the URL is kept, cleared, and the panel has no serious accessibility violation", async ({ page }) => {
  await open(page, "?domain=fixture&step=0&level=850&route=35.3,2.2;36.691,3.215");
  const panel = page.getByRole("region", { name: "Route" });
  await expect(panel).toContainText("P1 → DAAG");
  await expect(panel.getByRole("img", { name: /^Coupe verticale/ })).toBeVisible();
  const results = await new AxeBuilder({ page }).include(".route-panel").analyze();
  expect(results.violations.filter((v) => v.impact === "serious" || v.impact === "critical")).toEqual([]);
  await panel.getByRole("button", { name: "Effacer la route" }).click();
  await expect(page).not.toHaveURL(/route=/);
  await expect(page.getByRole("region", { name: "Route" })).toHaveCount(0);
});
