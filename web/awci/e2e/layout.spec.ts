import { expect, test } from "@playwright/test";
import { open } from "./helpers";

for (const width of [900, 1440, 1920, 2560]) {
  test(`layout at ${width} px: every zone present, no horizontal scroll`, async ({ page }) => {
    await page.setViewportSize({ width, height: 1100 });
    await open(page, "?domain=fixture&step=3&level=700&lat=36.5&lon=3");
    for (const name of ["Indicateurs du domaine", "Carte", "Situation actuelle", "Inspecteur de point", "Évolution temporelle"]) {
      await expect(page.getByRole("region", { name })).toBeVisible();
    }
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    expect(overflow).toBeLessThanOrEqual(0);
    await expect(page).toHaveScreenshot(`layout-${width}.png`, {
      fullPage: true, mask: [page.locator(".clock"), page.locator(".data-status"), page.locator(".runs-list")],
    });
  });
}
