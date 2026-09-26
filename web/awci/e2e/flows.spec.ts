import { expect, test } from "@playwright/test";
import { clickMap, open } from "./helpers";

test("the main view shows real data, its provenance and its freshness", async ({ page }) => {
  await open(page, "?domain=fixture&step=3&level=300");
  await expect(page.getByLabel("État des données")).toContainText("complet");
  await expect(page.getByRole("combobox", { name: "Modèle" }).locator("option:checked")).toHaveText("ECMWF IFS 0,25°");
  await expect(page.locator(".maplibregl-ctrl-attrib")).toContainText("ECMWF");
  await expect(page.getByRole("region", { name: "Situation actuelle" })).toContainText("Classe AWCI");
});

test("keyboard moves steps and levels and the URL follows", async ({ page }) => {
  await open(page, "?domain=fixture&step=0&level=300");
  await page.locator("body").press("ArrowRight");
  await expect(page).toHaveURL(/step=3/);
  await page.locator("body").press("ArrowUp");
  await expect(page).toHaveURL(/level=250/);
  await page.locator("body").press("ArrowDown");
  await expect(page).toHaveURL(/level=300/);
});

test("changing layer updates the legend; a point fills the inspector and the clouds panel; reload keeps the view", async ({ page }) => {
  await open(page, "?domain=fixture&step=3&level=700");
  await page.getByRole("radio", { name: /^Givrage potentiel/ }).check();
  await expect(page).toHaveURL(/layer=icing_potential/);
  await expect(page.getByRole("figure", { name: /Givrage potentiel/ })).toBeVisible();
  await page.getByRole("radio", { name: /^Genre, étage bas/ }).check();
  await expect(page.getByRole("figure", { name: /Genre, étage bas/ })).toContainText("Cumulonimbus");
  await clickMap(page, 0.5, 0.5);
  await expect(page).toHaveURL(/lat=/);
  await expect(page.getByRole("region", { name: "Inspecteur de point" })).toContainText("Calculé sur");
  await expect(page.getByRole("region", { name: "Nuages" })).toContainText("MODEL");
  const url = page.url();
  await page.reload();
  await expect(page.getByRole("region", { name: "Inspecteur de point" })).toBeVisible();
  expect(page.url()).toBe(url);
});

test("a partial run never offers its missing step", async ({ page }) => {
  await open(page, "?domain=fixture_wet&step=3&level=500");
  await expect(page.getByText(/Run partiel/)).toBeVisible();
  await expect(page.getByRole("button", { name: /\+6 h, échéance manquante/ })).toBeDisabled();
  await page.locator("body").press("ArrowRight");
  await expect(page).toHaveURL(/step=3/);
});

test("outside the domain is refused; below the relief is named, never zero", async ({ page }) => {
  await open(page, "?domain=fixture&step=3&level=1000");
  await clickMap(page, 0.04, 0.5);
  await expect(page.getByRole("alert").filter({ hasText: "hors du domaine" })).toBeVisible();
  await page.goto("/?domain=fixture&step=3&level=1000&lat=36.5&lon=3");
  await expect(page.getByRole("region", { name: "Inspecteur de point" })).toContainText("Sous le relief");
});

test("observations carry their time and attribution; an unavailable relay is said so", async ({ page }) => {
  await open(page, "?domain=fixture&step=3&ov=mtg_fd:ir105_hrfi,msg_fes:rgb_ash");
  await expect(page.locator(".observed-badge").filter({ hasText: "MTG FCI IR" })).toContainText(/Observé .* UTC · il y a .* · © EUMETSAT/);
  await expect(page.getByText("EUMETView indisponible")).toBeVisible({ timeout: 20_000 });
  await expect(page.getByRole("checkbox", { name: /MSG Ash RGB/ })).not.toBeChecked();
});

test("reduced motion disables transitions", async ({ browser }) => {
  const page = await browser.newPage({ reducedMotion: "reduce" });
  await page.goto("/?domain=fixture&step=3");
  const duration = await page.getByRole("button", { name: /Échéance suivante/ }).evaluate((el) => getComputedStyle(el).transitionDuration);
  expect(duration).toBe("0s");
  await page.close();
});

test("a slow EUMETView never delays the forecast", async ({ page }) => {
  await open(page, "?domain=fixture&step=3&level=300&ov=mtg_fd:rgb_dust");
  // Zoom out until the slow overlay has dozens of tiles in flight, as over a real 30x60 degree domain.
  const box = (await page.getByRole("application").boundingBox())!;
  await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
  for (let i = 0; i < 6; i++) { await page.mouse.wheel(0, 400); await page.waitForTimeout(250); }
  await page.waitForTimeout(500);
  const started = Date.now();
  const field = page.waitForResponse((r) => r.url().includes("/api/v1/awci/field") && r.url().includes("level=250"));
  await page.locator("body").press("ArrowUp");
  await field;
  expect(Date.now() - started).toBeLessThan(2000);
});

test("the layer list is operable from the keyboard (L, arrows, Space)", async ({ page }) => {
  await open(page, "?domain=fixture&step=3&level=700");
  await page.locator("body").press("l");
  await expect(page.getByRole("radio", { name: /^AWCI/ })).toBeFocused();
  await page.keyboard.press("ArrowDown");
  await expect(page).not.toHaveURL(/layer=awci/);
  await expect(page).toHaveURL(/level=700/); // the arrows moved the radio selection, not the level
  const lines = page.getByRole("checkbox", { name: /lignes de courant/i });
  await lines.focus();
  const before = await lines.isChecked();
  await page.keyboard.press(" ");
  expect(await lines.isChecked()).toBe(!before);
});
