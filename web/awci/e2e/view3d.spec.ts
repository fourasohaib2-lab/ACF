import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";
import { open } from "./helpers";

test("switching to 3-D states the exaggeration, keeps the URL and comes back to 2-D", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await open(page, "?domain=fixture&step=3&level=700");
  const volume = page.waitForResponse((r) => r.url().includes("/api/v1/awci/volume") && r.url().includes("layer=cloud_fraction"));
  await page.getByRole("button", { name: "Vue 3D" }).click();
  await expect(page).toHaveURL(/view=3d/);
  expect((await volume).status()).toBe(200);
  const panel = page.getByRole("region", { name: "Vue 3D" });
  await expect(panel).toContainText("Relief et altitudes exagérés ×40");
  await panel.getByRole("slider", { name: "Exagération verticale" }).fill("80");
  await expect(page).toHaveURL(/exag=80/);
  await page.reload();
  await expect(page.getByRole("region", { name: "Vue 3D" })).toContainText("×80");
  await page.getByRole("button", { name: "Revenir en 2D" }).click();
  await expect(page).not.toHaveURL(/view=3d/);
  await expect(page.getByRole("figure", { name: /Légende/ })).toBeVisible();
  expect(errors).toEqual([]);
});

test("4-D: the next valid time is preloaded, so stepping shows it without waiting", async ({ page }) => {
  const volumes: string[] = [];
  page.on("request", (r) => { if (r.url().includes("/api/v1/awci/volume")) volumes.push(new URL(r.url()).searchParams.get("step") ?? ""); });
  await open(page, "?domain=fixture&step=0&level=700&view=3d");
  await expect(page.getByRole("region", { name: "Vue 3D" })).toBeVisible();
  await expect.poll(() => volumes.includes("3")).toBe(true); // preloaded before any stepping (spec SP2B §3)
  const before = volumes.length;
  await page.locator("body").press("ArrowRight");
  await expect(page).toHaveURL(/step=3/);
  await page.waitForTimeout(500);
  expect(volumes.slice(before).filter((s) => s === "3")).toEqual([]); // served from the preload
});

test("without WebGL2 the 3-D view says so and the map stays usable", async ({ page }) => {
  await page.addInitScript(() => {
    const original = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function (this: HTMLCanvasElement, type: string, ...rest: unknown[]) {
      if (type === "webgl2" && !this.closest(".map-canvas")) return null; // the probe canvas, not MapLibre's
      return (original as (...a: unknown[]) => unknown).call(this, type, ...rest);
    } as typeof original;
  });
  await open(page, "?domain=fixture&step=3&level=700&view=3d");
  await expect(page.getByText(/Vue 3D indisponible : ce navigateur ne fournit pas WebGL2/)).toBeVisible();
  await expect(page.getByRole("button", { name: "Vue 3D" })).toBeDisabled();
  await expect(page.getByRole("figure", { name: /Légende/ })).toBeVisible();
});

test("the 3-D panel has no serious accessibility violation", async ({ page }) => {
  await open(page, "?domain=fixture&step=3&level=700&view=3d&vol=clouds,icing");
  await expect(page.getByRole("region", { name: "Vue 3D" })).toBeVisible();
  const results = await new AxeBuilder({ page }).include(".view3d-controls").analyze();
  const blocking = results.violations.filter((v) => v.impact === "serious" || v.impact === "critical");
  expect(blocking.map((v) => `${v.id}: ${v.nodes.slice(0, 3).map((n) => n.target.join(" ")).join(" | ")}`)).toEqual([]);
});
