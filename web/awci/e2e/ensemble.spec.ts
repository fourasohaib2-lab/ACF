import { expect, test } from "@playwright/test";
import { open } from "./helpers";

test("ENS probability layers are shown at ENS steps and explained elsewhere; the panel gives the members", async ({ page }) => {
  await open(page, "?domain=fixture&step=0&level=850");
  const prob = page.getByRole("radio", { name: "P(AWCI ≥ High)" });
  await prob.check();
  await expect(page).toHaveURL(/layer=p_awci_high/);
  await expect(page.getByRole("figure", { name: /P\(AWCI ≥ High\)/ })).toBeVisible();
  // +3 h (the arrow keys belong to the focused radio group): the ensemble runs every 6 h in this fixture
  await page.getByRole("button", { name: /^\+3 h, valide/ }).click();
  await expect(page).toHaveURL(/step=3/);
  await expect(page.getByText(/Pas de probabilité ENS à \+3 h/)).toBeVisible();
  await page.goto("/?domain=fixture&step=0&level=850&lat=36.5&lon=3");
  const panel = page.getByRole("region", { name: "Ensemble ECMWF" });
  await expect(panel).toContainText("4 membres");
  await expect(panel.getByRole("row", { name: /Convection/ })).toContainText("%");
});

test("a run without ENS says how to get it, and offers no probability layer", async ({ page }) => {
  await open(page, "?domain=fixture_wet&step=3&level=500");
  await expect(page.getByRole("region", { name: "Ensemble ECMWF" })).toContainText("acf-awci-ens");
  await expect(page.getByRole("radio", { name: "P(AWCI ≥ High)" })).toHaveCount(0);
});
