import { expect, type Page } from "@playwright/test";

/** Open a view and wait until the map has drawn its first field. */
export async function open(page: Page, query: string) {
  await page.goto(`/${query}`);
  await expect(page.getByRole("application")).toBeVisible();
  await expect(page.getByRole("button", { name: /AWCI P95 du domaine/ })).toBeVisible();
  await page.waitForTimeout(1500);
}

/** Click at a fraction of the map canvas (0..1 on each axis). */
export async function clickMap(page: Page, fx: number, fy: number) {
  const box = (await page.getByRole("application").boundingBox())!;
  await page.mouse.click(box.x + box.width * fx, box.y + box.height * fy);
}
