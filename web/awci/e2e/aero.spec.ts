import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";
import { open } from "./helpers";

test("an aerodrome shows its real METAR at the valid time next to the model, and its TAF", async ({ page }) => {
  await open(page, "?domain=fixture&step=3&level=700");
  await page.getByRole("combobox", { name: /^Aérodrome/ }).selectOption("DAAG");
  await expect(page).toHaveURL(/ap=DAAG/);
  const panel = page.getByRole("region", { name: "Aérodrome" });
  await expect(panel.getByRole("heading", { name: /DAAG — Algiers Intl/ })).toBeVisible();
  await expect(panel.locator(".raw-text").first()).toContainText(/(METAR|SPECI) DAAG 2503/);
  await expect(panel).toContainText("TAF DAAG");
  await expect(panel.getByRole("row", { name: /\+3 h/ })).toHaveAttribute("aria-current", "true");
  await page.locator("body").press("Escape");
  await expect(page).not.toHaveURL(/ap=DAAG/);
});

test("the validation page shows contingency tables and scores for the run", async ({ page }) => {
  await open(page, "?domain=fixture&step=3&level=700");
  await page.getByRole("button", { name: "Validation" }).click();
  const v = page.getByRole("region", { name: "Validation", exact: true });
  await expect(v.getByRole("table", { name: /Convection/ })).toBeVisible();
  await expect(v).toContainText("2 paires");
});

test("SIGMETs at the valid time and a domain without observations are stated, not hidden", async ({ page }) => {
  await open(page, "?domain=fixture&step=3&level=700");
  await expect(page.getByRole("region", { name: "SIGMET" })).toContainText("Aucun SIGMET valide");
  await open(page, "?domain=fixture_wet&step=3&level=500");
  await expect(page.getByText(/Aucune observation ingérée/)).toBeVisible();
});

test("aerodrome panel and validation page have no serious accessibility violation", async ({ page }) => {
  for (const q of ["?domain=fixture&step=3&level=700&ap=DAAG&lat=36.69&lon=3.22", "?domain=fixture&step=3&level=700&panel=validation"]) {
    await open(page, q);
    await page.waitForTimeout(500);
    const results = await new AxeBuilder({ page }).exclude(".maplibregl-canvas").analyze();
    const blocking = results.violations.filter((v) => v.impact === "serious" || v.impact === "critical");
    expect(blocking.map((v) => `${v.id}: ${v.nodes.slice(0, 3).map((n) => n.target.join(" ")).join(" | ")}`)).toEqual([]);
  }
});

test("the validation page scores both models against the real Algiers sounding", async ({ page }) => {
  await open(page, "?domain=fixture&step=3&level=700&panel=validation");
  const s = page.getByRole("region", { name: "Validation contre les radiosondages" });
  await expect(s.getByRole("img", { name: /^Température \(K\) selon la pression.*IFS biais, 12 niveaux.*GFS biais, 12 niveaux/ })).toBeVisible();
  await expect(s.getByRole("table", { name: "Scores sur toute la colonne" }).getByRole("row", { name: /^GFS/ })).toBeVisible();
  await expect(s).toContainText("IFS : 1 sondage, 1 station");
});
