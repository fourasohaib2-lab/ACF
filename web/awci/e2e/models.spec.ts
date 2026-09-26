import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";
import { open } from "./helpers";

test("the model selector shows the GFS run through the same pipeline, and back to IFS", async ({ page }) => {
  await open(page, "?domain=fixture&step=3&level=850");
  const select = page.getByRole("combobox", { name: "Modèle" });
  await expect(select).toHaveValue("ifs");
  await select.selectOption("gfs");
  await expect(page).toHaveURL(/model=gfs/);
  await expect(page.getByRole("button", { name: /^\+6 h, valide/ })).toBeVisible(); // GFS has +6 h, the IFS fixture does not
  await page.getByRole("button", { name: /^\+6 h, valide/ }).click();
  await expect(page).toHaveURL(/step=6/);
  await select.selectOption("ifs");
  await expect(page).not.toHaveURL(/model=gfs/);
});

test("the IFS-GFS difference layer and the agreement panel compare both models at the point", async ({ page }) => {
  await open(page, "?domain=fixture&step=3&level=850&lat=36.5&lon=3");
  await page.getByRole("radio", { name: "Écart d'AWCI (GFS − IFS)" }).check();
  await expect(page).toHaveURL(/layer=awci_diff/);
  await expect(page.getByRole("figure", { name: /Écart d'AWCI/ })).toContainText("orange : GFS plus haut");
  const panel = page.getByRole("region", { name: "Accord des modèles" });
  await expect(panel.getByRole("table", { name: "Valeurs IFS et GFS au point" })).toBeVisible();
  await expect(panel.getByRole("status")).toContainText("classe AWCI");
  const results = await new AxeBuilder({ page }).include("[aria-label='Accord des modèles']").analyze();
  expect(results.violations.filter((v) => v.impact === "serious" || v.impact === "critical")).toEqual([]);
});

test("without a GFS run the comparison says why and offers no difference layer", async ({ page }) => {
  await open(page, "?domain=fixture_wet&step=3&level=500&lat=16&lon=-19");
  await expect(page.getByRole("region", { name: "Accord des modèles" })).toContainText("Pas de run GFS");
  await expect(page.getByRole("radio", { name: "Écart d'AWCI (GFS − IFS)" })).toHaveCount(0);
});
